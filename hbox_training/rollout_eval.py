#!/usr/bin/env python3
"""Rollout-and-loss evaluator for Falcon-H1 checkpoints on hbox (PyTorch ROCm).

Runs on hbox inside the ``/home/hbox/h1-ghost`` environment (``source env.sh`` first).
For every ``--checkpoint NAME=DIR`` it writes under ``<output>/<NAME>/``:

* ``losses/first-512.npz`` and ``losses/clean-512.npz``: per-token losses (float32,
  natural log) and next-token correctness ``[n, L]`` over the validation slices defined
  in ``slices.json`` (exported on the Mac by ``rollout_summary.py slices`` from the
  evaluation pack's own selection), plus ``losses/retention.npz`` on the out-of-corpus
  text tokenized with the checkpoint's tokenizer;
* ``generations.jsonl``: per prompt, ``--samples`` sampled completions with fixed seeds
  and one greedy completion (prompt, seed, token ids, decoded text, tokens/second);
* ``<output>/room-<NAME>.jsonl`` when ``--room-prompts`` is given: the room-format pass
  (the live ChapterX frame plus visitor turns ending in ``h:``), one greedy and
  ``--room-samples`` sampled one-line replies per prompt, cut at the prompt's stop string;
* ``summary.json``: mean loss per slice (``first-32`` is derived from the first 32 rows
  of ``first-512``), furniture-free means when ``--masks`` is given, the kernel check
  against the reference recipe, environment and timings.

Losses follow ``compare_checkpoints.py``, the recipe behind the 3.745613 reference:
model loaded in BF16, ``torch.autocast`` BF16 forward, logits upcast to float32. The
kernel check re-runs the first 32 sequences at batch 1 through Transformers' reference
Mamba path for every checkpoint; the full passes use the upstream Triton SSD scan
(``rocm_triton_ssd.py``) when it loads, otherwise the reference path. Generation always
uses the reference path, which is also the recipe behind the earlier hbox samples.

This file imports nothing from ``hghost``; ``rollout_summary.py`` on the Mac imports its
pure-numpy helpers, so PyTorch and Transformers are only imported inside functions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import socket
import statistics
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np


def device_name() -> str:
    """CUDA/ROCm when visible, otherwise CPU (rehearsals only; see HGHOST_ALLOW_CPU)."""
    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


def cuda_sync() -> None:
    import torch

    if torch.cuda.is_available():
        cuda_sync()

STREAM_DTYPE = "<u2"
DEFAULT_MAMBA_ROOT = Path(
    "/othersys/h1-ghost/kernel-test/mamba-source/mamba_ssm-2.3.2.post1"
)
DEFAULT_VALIDATION = Path("/othersys/h1-ghost/data/corpus-v1/validation.bin")
REFERENCE_LOSS = 3.745613  # base model, first 32 x 512, hbox Transformers BF16
LOG_PREFIX = "[rollout-eval]"


def log(message: str) -> None:
    print(
        f"{LOG_PREFIX} {time.strftime('%H:%M:%S')} {message}",
        file=sys.stderr,
        flush=True,
    )


# --------------------------------------------------------------------------- inputs


def parse_checkpoint(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"expected NAME=DIR, got {value!r}")
    name, raw = value.split("=", 1)
    name = name.strip()
    path = Path(raw).expanduser().resolve()
    if not name or "/" in name:
        raise argparse.ArgumentTypeError(f"bad checkpoint name in {value!r}")
    if not (path / "config.json").is_file():
        raise argparse.ArgumentTypeError(f"{path} has no config.json")
    return name, path


def parse_reference(value: str) -> tuple[str, float]:
    name, _, raw = value.partition("=")
    return name.strip(), float(raw) if raw else REFERENCE_LOSS


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 22), b""):
            hasher.update(block)
    return hasher.hexdigest()


def load_slices(path: Path) -> dict:
    spec = json.loads(path.read_text(encoding="utf-8"))
    for name, item in spec["slices"].items():
        item["sequence_ids"] = np.asarray(item["sequence_ids"], dtype=np.int64)
        if item["sequence_ids"].ndim != 1 or not item["sequence_ids"].size:
            raise ValueError(f"slice {name} has no sequence ids")
    return spec


def sequence_rows(
    tokens: np.ndarray, sequence_ids: np.ndarray, length: int
) -> np.ndarray:
    """Rows ``[n, length + 1]``: sequence ``s`` is ``tokens[s * length : s * length + length + 1]``.

    Identical to the evaluation pack (and h1jax's ``ValidationStream``), so the same
    sequence ids name the same tokens on every machine.
    """
    rows = np.empty((len(sequence_ids), length + 1), dtype=np.int64)
    for row, sequence in enumerate(sequence_ids):
        start = int(sequence) * length
        window = tokens[start : start + length + 1]
        if window.shape[0] != length + 1:
            raise ValueError(f"sequence {sequence} runs past the end of the stream")
        rows[row] = window
    return rows


def open_stream(path: Path, expected: dict) -> np.ndarray:
    digest = sha256_file(path)
    if digest != expected["sha256"]:
        raise RuntimeError(f"{path}: sha256 {digest} != expected {expected['sha256']}")
    tokens = np.memmap(path, dtype=STREAM_DTYPE, mode="r")
    if int(tokens.shape[0]) != int(expected["tokens"]):
        raise RuntimeError(f"{path}: {tokens.shape[0]} tokens != {expected['tokens']}")
    return tokens


def load_masks(path: Path | None) -> dict[str, dict[str, np.ndarray]]:
    """``{slice: {"furniture": [n, L] bool, "matched": [n, L] bool}}`` from ``masks.npz``."""
    masks: dict[str, dict[str, np.ndarray]] = {}
    if path is None:
        return masks
    stored = np.load(path)
    for key in stored.files:
        name, _, kind = key.rpartition(".")
        if kind in ("furniture", "matched") and name:
            masks.setdefault(name, {})[kind] = np.asarray(stored[key], dtype=bool)
    return masks


def load_prompts(path: Path) -> tuple[int, list[dict]]:
    values = json.loads(path.read_text(encoding="utf-8"))
    return int(values["base_seed"]), list(values["prompts"])


# --------------------------------------------------------------------------- metrics


def masked_mean(values: np.ndarray, keep: np.ndarray) -> float | None:
    selected = values[keep]
    return float(selected.mean()) if selected.size else None


def summarize_losses(
    losses: np.ndarray,
    correct: np.ndarray,
    furniture: np.ndarray | None = None,
    matched: np.ndarray | None = None,
) -> dict:
    """Plain, furniture-free and unseen-only means, shaped like the evaluation pack's."""
    losses = np.asarray(losses, dtype=np.float64)
    correct = np.asarray(correct, dtype=bool)
    total = int(losses.size)
    plain = float(losses.mean()) if total else None
    summary = {
        "sequences": int(losses.shape[0]) if losses.ndim == 2 else 1,
        "tokens": total,
        "loss": plain,
        "perplexity": math.exp(plain) if plain is not None else None,
        "accuracy": float(correct.mean()) if total else None,
    }
    if furniture is not None:
        if furniture.shape != losses.shape:
            raise ValueError(
                f"furniture mask {furniture.shape} != losses {losses.shape}"
            )
        keep = ~np.asarray(furniture, dtype=bool)
        summary["furniture_fraction"] = float(1 - keep.mean()) if total else None
        summary["furniture_free_loss"] = masked_mean(losses, keep)
        summary["furniture_free_accuracy"] = masked_mean(correct, keep)
        summary["furniture_loss"] = masked_mean(losses, ~keep)
    if matched is not None:
        if matched.shape != losses.shape:
            raise ValueError(f"matched mask {matched.shape} != losses {losses.shape}")
        keep = ~np.asarray(matched, dtype=bool)
        summary["matched_fraction"] = float(1 - keep.mean()) if total else None
        summary["unseen_loss"] = masked_mean(losses, keep)
        summary["unseen_accuracy"] = masked_mean(correct, keep)
    return summary


def slice_summaries(
    spec: dict,
    stored: dict[str, dict[str, np.ndarray]],
    masks: dict[str, dict[str, np.ndarray]],
) -> dict[str, dict]:
    """Summaries for every stored slice plus the derived ones (``first-32``)."""
    summaries: dict[str, dict] = {}
    for name, arrays in stored.items():
        mask = masks.get(name, {})
        summaries[name] = summarize_losses(
            arrays["losses"],
            arrays["correct"],
            mask.get("furniture"),
            mask.get("matched"),
        )
    for name, derived in spec.get("derived", {}).items():
        parent, rows = derived["slice"], int(derived["rows"])
        if parent not in stored:
            continue
        arrays = stored[parent]
        mask = masks.get(parent, {})
        summaries[name] = summarize_losses(
            arrays["losses"][:rows],
            arrays["correct"][:rows],
            None if "furniture" not in mask else mask["furniture"][:rows],
            None if "matched" not in mask else mask["matched"][:rows],
        )
    return summaries


# --------------------------------------------------------------------------- kernels


class Kernels:
    """Switch Falcon-H1's Mamba mixer between the reference path and the Triton scan.

    The reference ``forward`` is captured before the patch so it stays byte-identical to
    the recipe that produced the reference loss; ``enable_rocm_triton_ssd`` then installs
    the Triton forward, which is swapped in only inside ``use("triton")``.
    """

    def __init__(self, requested: str, mamba_root: Path) -> None:
        import transformers.models.falcon_h1.modeling_falcon_h1 as falcon_h1

        self.mixer = falcon_h1.FalconH1Mixer
        self.reference_forward = self.mixer.forward
        self.triton_forward = None
        self.report: dict = {"requested": requested, "triton": None}
        if requested in ("auto", "triton"):
            try:
                from rocm_triton_ssd import enable_rocm_triton_ssd

                self.report["triton"] = enable_rocm_triton_ssd(mamba_root)
                self.triton_forward = self.mixer.forward
            except Exception as error:
                if requested == "triton":
                    raise
                self.report["triton_error"] = f"{type(error).__name__}: {error}"
                log(f"Triton SSD path unavailable, using the reference path: {error}")
            finally:
                self.mixer.forward = self.reference_forward
        self.report["losses"] = "triton" if self.triton_forward else "reference"
        self.report["generation"] = "reference"

    @property
    def loss_kernel(self) -> str:
        return "triton" if self.triton_forward else "reference"

    @contextmanager
    def use(self, name: str):
        if name == "triton" and self.triton_forward is None:
            raise RuntimeError("the Triton SSD path is not loaded")
        self.mixer.forward = (
            self.triton_forward if name == "triton" else self.reference_forward
        )
        try:
            yield
        finally:
            self.mixer.forward = self.reference_forward


# --------------------------------------------------------------------------- model


def environment() -> dict:
    import torch
    import transformers

    try:
        import triton

        triton_version = triton.__version__
    except ImportError:
        triton_version = None
    busy = None
    for candidate in sorted(
        Path("/sys/class/drm").glob("card*/device/gpu_busy_percent")
    ):
        try:
            busy = int(candidate.read_text().strip())
            break
        except (OSError, ValueError):
            continue
    available = None
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                available = int(line.split()[1]) * 1024
    except OSError:
        pass
    return {
        "host": socket.gethostname(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "hip": torch.version.hip,
        "transformers": transformers.__version__,
        "triton": triton_version,
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "hsa_override_gfx_version": os.environ.get("HSA_OVERRIDE_GFX_VERSION"),
        "load_average": os.getloadavg(),
        "memory_available_bytes": available,
        "gpu_busy_percent": busy,
    }


def load_model(path: Path):
    import torch
    from transformers import AutoTokenizer, FalconH1ForCausalLM

    started = time.perf_counter()
    model = FalconH1ForCausalLM.from_pretrained(
        path, dtype=torch.bfloat16, local_files_only=True
    ).to(device_name())
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
    return model, tokenizer, time.perf_counter() - started


def per_token_losses(
    model, rows: np.ndarray, *, batch_size: int, progress=None
) -> tuple[np.ndarray, np.ndarray, float]:
    """Per-token loss and correctness for rows ``[n, L + 1]`` in BF16 autocast.

    Same arithmetic as ``compare_checkpoints.py``: BF16 forward, float32 logits,
    cross-entropy against the next token; here kept per position instead of summed.
    """
    import torch
    from torch.nn import functional

    count, width = rows.shape[0], rows.shape[1] - 1
    losses = np.empty((count, width), dtype=np.float32)
    correct = np.empty((count, width), dtype=bool)
    cuda_sync()
    started = time.perf_counter()
    with torch.inference_mode():
        for start in range(0, count, batch_size):
            batch = torch.from_numpy(rows[start : start + batch_size]).to(device_name())
            inputs, labels = batch[:, :-1], batch[:, 1:]
            with torch.autocast(device_name(), dtype=torch.bfloat16):
                logits = model(input_ids=inputs, use_cache=False).logits
            logits = logits.float()
            loss = functional.cross_entropy(
                logits.reshape(-1, logits.shape[-1]),
                labels.reshape(-1),
                reduction="none",
            ).view(labels.shape)
            losses[start : start + batch.shape[0]] = loss.cpu().numpy()
            correct[start : start + batch.shape[0]] = (
                (logits.argmax(-1) == labels).cpu().numpy()
            )
            if progress is not None:
                progress(start + batch.shape[0], count)
    cuda_sync()
    return losses, correct, time.perf_counter() - started


def generate_one(
    model,
    tokenizer,
    prompt_ids: list[int],
    *,
    seed: int | None,
    settings: dict,
    stop: str | None = None,
) -> dict:
    """One completion; with ``stop`` generation halts at that string and ``text`` is cut there."""
    import torch

    input_ids = torch.tensor([prompt_ids], dtype=torch.long, device=device_name())
    attention_mask = torch.ones_like(input_ids)
    options = {
        "max_new_tokens": settings["max_new_tokens"],
        "repetition_penalty": settings["repetition_penalty"],
        "use_cache": True,
        "pad_token_id": tokenizer.eos_token_id,
    }
    if stop:
        options.update(stop_strings=[stop], tokenizer=tokenizer)
    if seed is None:
        options["do_sample"] = False
    else:
        options.update(
            do_sample=True, temperature=settings["temperature"], top_p=settings["top_p"]
        )
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    cuda_sync()
    started = time.perf_counter()
    with torch.inference_mode():
        output = model.generate(
            input_ids=input_ids, attention_mask=attention_mask, **options
        )
    cuda_sync()
    seconds = time.perf_counter() - started
    tokens = [int(token) for token in output[0, len(prompt_ids) :].tolist()]
    finish_reason = "length"
    if tokens and tokens[-1] == tokenizer.eos_token_id:
        tokens = tokens[:-1]
        finish_reason = "stop"
    elif len(tokens) < settings["max_new_tokens"]:
        finish_reason = "stop"
    completion = tokenizer.decode(tokens, skip_special_tokens=True)
    result = {
        "tokens": tokens,
        "completion": completion,
        "finish_reason": finish_reason,
        "seconds": round(seconds, 4),
        "tokens_per_second": round(len(tokens) / seconds, 2) if seconds else None,
    }
    if stop:
        cut = completion.find(stop)
        result["text"] = completion if cut < 0 else completion[:cut]
        result["stopped"] = cut >= 0
    return result


def run_generations(
    model, tokenizer, prompts: list[dict], base_seed: int, settings: dict, output: Path
) -> dict:
    """One JSON line per (prompt, sample) then the greedy line; ids ``<prompt>/s<k>``.

    Sample ``k`` of prompt ``i`` uses seed ``base_seed + i + 100 * k`` so sample 0 keeps
    the evaluation pack's per-prompt seeds. ``tokens`` and ``id`` are what
    ``hghost-haunt scan`` reads.
    """
    started = time.perf_counter()
    generated = 0
    rates: list[float] = []
    with output.open("w", encoding="utf-8") as sink:
        for index, prompt in enumerate(prompts):
            prompt_ids = tokenizer.encode(prompt["text"], add_special_tokens=False)
            runs = [
                (f"s{k}", base_seed + index + 100 * k)
                for k in range(settings["samples"])
            ]
            runs.append(("greedy", None))
            for label, seed in runs:
                result = generate_one(
                    model, tokenizer, prompt_ids, seed=seed, settings=settings
                )
                record = {
                    "id": f"{prompt['id']}/{label}",
                    "prompt_id": prompt["id"],
                    "kind": prompt.get("kind", ""),
                    "sample": label,
                    "mode": "greedy" if seed is None else "sample",
                    "seed": seed,
                    "prompt": prompt["text"],
                    "prompt_tokens": [int(token) for token in prompt_ids],
                    **result,
                }
                sink.write(json.dumps(record, ensure_ascii=False) + "\n")
                sink.flush()
                generated += len(result["tokens"])
                if result["tokens_per_second"]:
                    rates.append(result["tokens_per_second"])
            log(
                f"generated {index + 1}/{len(prompts)} {prompt['id']}"
                f" ({len(runs)} completions, last {result['tokens_per_second']} tok/s)"
            )
    seconds = time.perf_counter() - started
    return {
        "prompts": len(prompts),
        "samples_per_prompt": settings["samples"],
        "greedy_per_prompt": 1,
        "completions": len(prompts) * (settings["samples"] + 1),
        "generated_tokens": generated,
        "seconds": round(seconds, 3),
        "tokens_per_second": round(generated / seconds, 2) if seconds else None,
        "per_call_tokens_per_second_median": (
            round(statistics.median(rates), 2) if rates else None
        ),
        "base_seed": base_seed,
        **{
            k: settings[k]
            for k in ("max_new_tokens", "temperature", "top_p", "repetition_penalty")
        },
    }


def load_room_prompts(path: Path) -> list[dict]:
    """Room prompts: a list (or ``{"prompts": [...]}``) of ``kind`` / ``prompt`` / ``stop``."""
    values = json.loads(path.read_text(encoding="utf-8"))
    items = values["prompts"] if isinstance(values, dict) else values
    return [
        {
            "index": index,
            "kind": item.get("kind", ""),
            "prompt": item["prompt"],
            "stop": item.get("stop", "\n"),
        }
        for index, item in enumerate(items)
    ]


def run_room(
    model, tokenizer, prompts: list[dict], settings: dict, output: Path
) -> dict:
    """Room-format pass: one greedy and ``samples`` sampled replies per prompt.

    Each prompt is the live ChapterX frame with visitor turns, ending in ``h:``; the
    harness keeps the reply up to the first newline, so ``text`` is cut at the prompt's
    stop string while ``raw_text`` keeps the whole decode. Sample ``k`` of prompt ``i``
    uses seed ``seed + i + 100 * k``.
    """
    started = time.perf_counter()
    generated = 0
    with output.open("w", encoding="utf-8") as sink:
        for prompt in prompts:
            prompt_ids = tokenizer.encode(prompt["prompt"], add_special_tokens=False)
            runs = [("greedy", None)] + [
                (f"s{k}", settings["seed"] + prompt["index"] + 100 * k)
                for k in range(settings["samples"])
            ]
            for label, seed in runs:
                result = generate_one(
                    model,
                    tokenizer,
                    prompt_ids,
                    seed=seed,
                    settings=settings,
                    stop=prompt["stop"],
                )
                record = {
                    "kind": prompt["kind"],
                    "prompt_index": prompt["index"],
                    "mode": "greedy" if seed is None else "sample",
                    "sample": label,
                    "seed": seed,
                    "text": result["text"],
                    "raw_text": result["completion"],
                    "stopped": result["stopped"],
                    "finish_reason": result["finish_reason"],
                    "prompt_tokens": len(prompt_ids),
                    "new_tokens": len(result["tokens"]),
                    "tokens_per_second": result["tokens_per_second"],
                }
                sink.write(json.dumps(record, ensure_ascii=False) + "\n")
                sink.flush()
                generated += len(result["tokens"])
            log(
                f"room {prompt['index'] + 1}/{len(prompts)} {prompt['kind']}:"
                f" greedy {records_first_text(output, prompt['index'])!r}"
            )
    seconds = time.perf_counter() - started
    return {
        "prompts": len(prompts),
        "samples_per_prompt": settings["samples"],
        "greedy_per_prompt": 1,
        "completions": len(prompts) * (settings["samples"] + 1),
        "generated_tokens": generated,
        "seconds": round(seconds, 3),
        "tokens_per_second": round(generated / seconds, 2) if seconds else None,
        **{
            k: settings[k]
            for k in (
                "seed",
                "max_new_tokens",
                "temperature",
                "top_p",
                "repetition_penalty",
            )
        },
    }


def records_first_text(output: Path, index: int, limit: int = 70) -> str:
    """The greedy reply for prompt ``index`` from the jsonl written so far (for logs)."""
    with output.open(encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            if record["prompt_index"] == index and record["mode"] == "greedy":
                return record["text"][:limit]
    return ""


# --------------------------------------------------------------------------- driver


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--checkpoint",
        type=parse_checkpoint,
        action="append",
        required=True,
        metavar="NAME=DIR",
        help="checkpoint directory to evaluate (repeatable)",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--slices", type=Path, required=True, help="slices.json from the Mac"
    )
    parser.add_argument("--validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--prompts", type=Path, required=True)
    parser.add_argument("--retention", type=Path, required=True)
    parser.add_argument(
        "--room-validation",
        type=Path,
        default=None,
        help="optional uint16 token stream of held-out room documents; mean loss over its first N sequences",
    )
    parser.add_argument("--room-validation-sequences", type=int, default=512)
    parser.add_argument(
        "--masks",
        type=Path,
        help="optional masks.npz: <slice>.furniture / <slice>.matched",
    )
    parser.add_argument("--batch", type=int, default=8, help="rows per forward")
    parser.add_argument(
        "--kernel", choices=("auto", "reference", "triton"), default="auto"
    )
    parser.add_argument("--mamba-root", type=Path, default=DEFAULT_MAMBA_ROOT)
    parser.add_argument(
        "--reference",
        type=parse_reference,
        default=("base", REFERENCE_LOSS),
        metavar="NAME[=LOSS]",
        help="checkpoint whose reference-path first-32 loss must reproduce LOSS",
    )
    parser.add_argument("--reference-tolerance", type=float, default=0.005)
    parser.add_argument("--samples", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--repetition-penalty", type=float, default=1.08)
    parser.add_argument(
        "--room-prompts",
        type=Path,
        help="room-format prompts (kind/prompt/stop); writes <output>/room-<NAME>.jsonl",
    )
    parser.add_argument("--room-samples", type=int, default=4)
    parser.add_argument("--room-max-new-tokens", type=int, default=64)
    parser.add_argument("--room-temperature", type=float, default=0.7)
    parser.add_argument("--room-top-p", type=float, default=0.9)
    parser.add_argument("--room-repetition-penalty", type=float, default=1.0)
    parser.add_argument("--room-seed", type=int, default=20260902)
    parser.add_argument("--skip-losses", action="store_true")
    parser.add_argument("--skip-generation", action="store_true")
    parser.add_argument(
        "--force", action="store_true", help="redo checkpoints with a summary"
    )
    return parser


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def evaluate_checkpoint(
    args: argparse.Namespace,
    name: str,
    path: Path,
    *,
    spec: dict,
    stream: np.ndarray,
    masks: dict,
    kernels: Kernels,
    prompts: tuple[int, list[dict]],
) -> dict:
    import torch

    out = args.output / name
    out.mkdir(parents=True, exist_ok=True)
    length = int(spec["sequence_length"])
    started = time.perf_counter()
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    model, tokenizer, load_seconds = load_model(path)
    summary: dict = {
        "name": name,
        "checkpoint": str(path),
        "model_safetensors_sha256": sha256_file(path / "model.safetensors"),
        "config_dtype": json.loads((path / "config.json").read_text()).get("dtype"),
        "sequence_length": length,
        "batch": args.batch,
        "kernel": {**kernels.report},
        "timings": {"load_seconds": round(load_seconds, 3), "losses": {}},
        "slices": {},
    }
    log(f"{name}: loaded in {load_seconds:.1f}s from {path}")

    if not args.skip_losses:
        # Kernel check: the exact reference recipe (reference path, batch 1, first 32).
        check_rows = sequence_rows(stream, np.arange(32, dtype=np.int64), length)
        with kernels.use("reference"):
            check_losses, _, check_seconds = per_token_losses(
                model, check_rows, batch_size=1
            )
        reference_first32 = float(check_losses.mean())
        summary["kernel_check"] = {
            "slice": "first-32",
            "reference_path_batch1_loss": reference_first32,
            "reference_path_seconds": round(check_seconds, 3),
        }
        log(
            f"{name}: first-32 on the reference path at batch 1: {reference_first32:.6f}"
        )
        if name == args.reference[0]:
            delta = reference_first32 - args.reference[1]
            summary["kernel_check"]["expected_loss"] = args.reference[1]
            summary["kernel_check"]["expected_delta"] = delta
            summary["kernel_check"]["ok"] = abs(delta) <= args.reference_tolerance
            if not summary["kernel_check"]["ok"]:
                raise RuntimeError(
                    f"{name}: first-32 reference loss {reference_first32:.6f} is"
                    f" {delta:+.6f} from {args.reference[1]} (tolerance"
                    f" {args.reference_tolerance}); not trusting this setup"
                )
            log(f"{name}: reproduces {args.reference[1]} within {delta:+.6f}")

        stored: dict[str, dict[str, np.ndarray]] = {}
        losses_dir = out / "losses"
        losses_dir.mkdir(exist_ok=True)
        jobs = [
            (
                slice_name,
                sequence_rows(stream, item["sequence_ids"], length),
                item["sequence_ids"],
            )
            for slice_name, item in spec["slices"].items()
        ]
        text = args.retention.read_text(encoding="utf-8")
        retention_tokens = np.asarray(
            tokenizer.encode(text, add_special_tokens=False), dtype=np.int64
        )
        retention_count = (int(retention_tokens.shape[0]) - 1) // length
        if retention_count < 1:
            raise ValueError("retention text is shorter than one sequence")
        retention_ids = np.arange(retention_count, dtype=np.int64)
        jobs.append(
            (
                "retention",
                sequence_rows(retention_tokens, retention_ids, length),
                retention_ids,
            )
        )
        summary["retention"] = {
            "path": str(args.retention),
            "bytes": len(text.encode("utf-8")),
            "tokens": int(retention_tokens.shape[0]),
            "sequences": retention_count,
        }
        if args.room_validation is not None:
            room_tokens = np.fromfile(args.room_validation, dtype=np.uint16).astype(np.int64)
            room_count = min(
                args.room_validation_sequences, (int(room_tokens.shape[0]) - 1) // length
            )
            if room_count < 1:
                raise ValueError("room validation stream is shorter than one sequence")
            room_ids = np.arange(room_count, dtype=np.int64)
            jobs.append(("room", sequence_rows(room_tokens, room_ids, length), room_ids))
            summary["room_validation"] = {
                "path": str(args.room_validation),
                "tokens": int(room_tokens.shape[0]),
                "sequences": room_count,
            }
        with kernels.use(kernels.loss_kernel):
            for slice_name, rows, ids in jobs:
                losses, correct, seconds = per_token_losses(
                    model,
                    rows,
                    batch_size=args.batch,
                    progress=lambda done, total, s=slice_name: (
                        log(f"{name}: {s} {done}/{total} rows")
                        if done % 128 == 0
                        else None
                    ),
                )
                np.savez(
                    losses_dir / f"{slice_name}.npz",
                    losses=losses,
                    correct=correct,
                    sequence_ids=ids,
                )
                stored[slice_name] = {"losses": losses, "correct": correct}
                summary["timings"]["losses"][slice_name] = {
                    "seconds": round(seconds, 3),
                    "tokens_per_second": round(losses.size / seconds, 1),
                }
                log(
                    f"{name}: {slice_name} loss {losses.mean():.4f}"
                    f" ({losses.size / seconds:,.0f} tok/s, {kernels.loss_kernel})"
                )
        summary["slices"] = slice_summaries(spec, stored, masks)
        summary["kernel_check"]["run_first32_loss"] = summary["slices"]["first-32"][
            "loss"
        ]
        summary["kernel_check"]["run_kernel"] = kernels.loss_kernel
        summary["kernel_check"]["run_batch"] = args.batch
        summary["kernel_check"]["run_minus_reference_path"] = (
            summary["slices"]["first-32"]["loss"] - reference_first32
        )
        summary["masks"] = sorted(masks) if masks else []

    if not args.skip_generation:
        base_seed, prompt_list = prompts
        settings = {
            "samples": args.samples,
            "max_new_tokens": args.max_new_tokens,
            "temperature": args.temperature,
            "top_p": args.top_p,
            "repetition_penalty": args.repetition_penalty,
        }
        with kernels.use("reference"):
            summary["generation"] = run_generations(
                model,
                tokenizer,
                prompt_list,
                base_seed,
                settings,
                out / "generations.jsonl",
            )
        summary["timings"]["generation_seconds"] = summary["generation"]["seconds"]
        log(
            f"{name}: {summary['generation']['completions']} completions,"
            f" {summary['generation']['tokens_per_second']} tok/s overall,"
            f" median call {summary['generation']['per_call_tokens_per_second_median']} tok/s"
        )

    if args.room_prompts is not None:
        settings = {
            "samples": args.room_samples,
            "max_new_tokens": args.room_max_new_tokens,
            "temperature": args.room_temperature,
            "top_p": args.room_top_p,
            "repetition_penalty": args.room_repetition_penalty,
            "seed": args.room_seed,
        }
        with kernels.use("reference"):
            summary["room"] = run_room(
                model,
                tokenizer,
                load_room_prompts(args.room_prompts),
                settings,
                args.output / f"room-{name}.jsonl",
            )
        summary["timings"]["room_seconds"] = summary["room"]["seconds"]
        log(
            f"{name}: room pass {summary['room']['completions']} replies,"
            f" {summary['room']['tokens_per_second']} tok/s"
        )

    summary["gpu"] = {
        "max_memory_allocated_bytes": int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else 0,
        "max_memory_reserved_bytes": int(torch.cuda.max_memory_reserved()) if torch.cuda.is_available() else 0,
    }
    summary["timings"]["total_seconds"] = round(time.perf_counter() - started, 3)
    write_json(out / "summary.json", summary)
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return summary


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    import torch

    if not torch.cuda.is_available() and os.environ.get("HGHOST_ALLOW_CPU") != "1":
        raise RuntimeError(
            "no ROCm/CUDA device visible; source env.sh (HSA_OVERRIDE_GFX_VERSION)"
            " or set HGHOST_ALLOW_CPU=1 for a rehearsal"
        )
    names = [name for name, _ in args.checkpoint]
    if len(set(names)) != len(names):
        raise SystemExit("checkpoint names must be unique")
    # The reference checkpoint goes first: nothing else is trusted until it reproduces.
    order = sorted(args.checkpoint, key=lambda item: item[0] != args.reference[0])
    args.output.mkdir(parents=True, exist_ok=True)
    spec = load_slices(args.slices)
    stream = open_stream(args.validation, spec["validation"])
    masks = load_masks(args.masks)
    prompts = load_prompts(args.prompts)
    kernels = Kernels(args.kernel, args.mamba_root)
    run: dict = {
        "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "environment": environment(),
        "kernel": kernels.report,
        "slices": {
            name: {"sequences": int(item["sequence_ids"].size)}
            for name, item in spec["slices"].items()
        },
        "validation": {"path": str(args.validation), **spec["validation"]},
        "settings": {
            key: (str(value) if isinstance(value, Path) else value)
            for key, value in vars(args).items()
            if key != "checkpoint"
        },
        "checkpoints": {
            name: {"path": str(path), "status": "pending"} for name, path in order
        },
        "complete": False,
    }
    run["settings"]["reference"] = list(args.reference)
    write_json(args.output / "run.json", run)
    log(
        f"{run['environment']['host']}: load {run['environment']['load_average']},"
        f" gpu busy {run['environment']['gpu_busy_percent']}%, losses on"
        f" {kernels.loss_kernel}, generation on reference"
    )
    started = time.perf_counter()
    for name, path in order:
        summary_path = args.output / name / "summary.json"
        if summary_path.is_file() and not args.force:
            log(f"{name}: summary exists, skipping (use --force to redo)")
            run["checkpoints"][name]["status"] = "reused"
            write_json(args.output / "run.json", run)
            continue
        try:
            summary = evaluate_checkpoint(
                args,
                name,
                path,
                spec=spec,
                stream=stream,
                masks=masks,
                kernels=kernels,
                prompts=prompts,
            )
        except Exception as error:
            run["checkpoints"][name]["status"] = (
                f"failed: {type(error).__name__}: {error}"
            )
            write_json(args.output / "run.json", run)
            raise
        run["checkpoints"][name].update(
            status="done",
            seconds=summary["timings"]["total_seconds"],
            losses={k: v.get("loss") for k, v in summary.get("slices", {}).items()},
        )
        write_json(args.output / "run.json", run)
    run["complete"] = True
    run["seconds"] = round(time.perf_counter() - started, 1)
    write_json(args.output / "run.json", run)
    log(f"done in {run['seconds']}s: {args.output}")
    print(
        json.dumps({name: item["status"] for name, item in run["checkpoints"].items()})
    )


if __name__ == "__main__":
    main()
