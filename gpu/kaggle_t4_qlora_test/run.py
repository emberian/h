"""Kaggle GPU (T4) kernel: small-scale proof of gpu/qlora_unsloth.py before the rented H100 day.

Runs the QLoRA library-adapter recipe (qwen/RECIPE.md: r=16, alpha 16, attention + MLP projections only,
LR 5e-5, raw text, seq 2048, batch 1 x accumulation 4) for 30 optimizer steps on a small Qwen3.5-family
base with the same Gated DeltaNet + attention hybrid as Qwen3.8-27B, NF4 4-bit base weights through
bitsandbytes, on qwen/data (3,000 train chunks, held-out validation chunks). The T4 has no bf16 and
Qwen3.5's GDN layers produce NaN gradients in fp16, so the compute dtype is fp32 here (the H100 runs
bf16). Then:

  * every train loss finite; validation loss before and after, on the same held-out chunks;
  * the PEFT adapter under adapter/ reloads onto a fresh 4-bit base and reproduces the final validation
    loss (independent of the script's own evaluator);
  * the adapter merged into the 16-bit base (--merge) is written and its validation loss reported, so
    the merge-or-not decision has a number;
  * throughput (tokens/s) and peak memory, for the H100 projection.

Writes <output>/{summary.json, qlora.log}; prints T4_QLORA_TEST_OK at the end.
Attach: the code dataset (qlora_unsloth.py) and the Qwen library-chunks dataset (train/valid.jsonl).
"""

from __future__ import annotations

import glob
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

STARTED = time.time()
LOCAL = os.environ.get("HGHOST_LOCAL") == "1"
OUTPUT = Path(os.environ.get("HGHOST_T4_OUTPUT", "/kaggle/working/t4-qlora-test"))
MODEL = os.environ.get("HGHOST_T4_MODEL", "Qwen/Qwen3.5-2B-Base")
BACKEND = os.environ.get("HGHOST_T4_BACKEND", "peft")
PACKAGES = os.environ.get("HGHOST_T4_PACKAGES", "transformers==5.16.1 peft==0.20.0 bitsandbytes accelerate").split()
STEPS = int(os.environ.get("HGHOST_T4_STEPS", "30"))
MAX_MINUTES = float(os.environ.get("HGHOST_T4_MAX_MINUTES", "23"))  # the T4's fp32 fallback path does ~195 tokens/s: 30 steps in ~21 min
VALID_CHUNKS = int(os.environ.get("HGHOST_T4_VALID_CHUNKS", "8"))
EVAL_EVERY = int(os.environ.get("HGHOST_T4_EVAL_EVERY", "15"))
COMPUTE_DTYPE = os.environ.get("HGHOST_T4_COMPUTE_DTYPE", "fp32")
MERGE = os.environ.get("HGHOST_T4_MERGE", "1") == "1"
EXTRA_ARGS = os.environ.get("HGHOST_T4_EXTRA_ARGS", "")
OUTPUT.mkdir(parents=True, exist_ok=True)


def emit(event: str, **values) -> None:
    print(json.dumps({"event": event, "elapsed": round(time.time() - STARTED, 1), **values}, default=str), flush=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def installed(package: str) -> str:
    from importlib.metadata import version

    return version(package)


def exactly_one(pattern: str) -> Path:
    matches = sorted(Path(p) for p in glob.glob(pattern, recursive=True) if Path(p).is_file())
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {pattern!r}, found: {matches}")
    return matches[0]


# ------------------------------------------------------------------ environment and inputs
if not LOCAL:
    torch_pin = f"torch=={installed('torch')}"  # keep the image's torch: it is the build that runs on the T4
    cmd = [sys.executable, "-m", "pip", "install", "--quiet", *PACKAGES, torch_pin]
    if BACKEND == "unsloth":
        cmd.append("unsloth")
    emit("pip_install", command=cmd)
    # The image ships torchao 0.10; peft 0.20's LoRA dispatcher imports it for plain nn.Linear targets (the merge
    # path) and refuses anything below 0.16. Absent is fine: the dispatcher then skips torchao.
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", "torchao"], capture_output=True, text=True, check=False)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    (OUTPUT / "pip.log").write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
    if proc.returncode != 0:
        print(proc.stderr[-4000:], flush=True)
        raise SystemExit("pip install failed")
    script = exactly_one("/kaggle/input/**/qlora_unsloth.py")
    data_dir = exactly_one("/kaggle/input/**/hghost-qwen-library-chunks/**/valid.jsonl").parent
else:
    root = Path(os.environ["HGHOST_ROOT"])
    script = root / "gpu/qlora_unsloth.py"
    data_dir = root / "qwen/data"

import torch

versions = {"torch": torch.__version__, "transformers": installed("transformers"), "peft": installed("peft"),
            "bitsandbytes": installed("bitsandbytes") if not LOCAL else None}
emit("hardware", cuda=torch.cuda.is_available(), device=torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
     script=str(script), script_sha256=sha256(script), data_dir=str(data_dir), **versions)
for name in ("train.jsonl", "valid.jsonl"):
    rows = sum(1 for line in (data_dir / name).open(encoding="utf-8") if line.strip())
    emit("data_file", name=name, rows=rows, bytes=(data_dir / name).stat().st_size)

# ------------------------------------------------------------------ the run
run_dir = OUTPUT / "run"
cmd = [
    sys.executable, str(script), "--tiny", "--model", MODEL, "--data-dir", str(data_dir), "--output", str(run_dir),
    "--backend", BACKEND, "--max-steps", str(STEPS), "--valid-chunks", str(VALID_CHUNKS), "--max-minutes", str(MAX_MINUTES),
    "--eval-every", str(EVAL_EVERY), "--compute-dtype", COMPUTE_DTYPE,
]
if MERGE:
    cmd.append("--merge")
if EXTRA_ARGS:
    cmd += EXTRA_ARGS.split()
emit("run_start", command=cmd)
with (OUTPUT / "qlora.log").open("w") as log:
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                            env={**os.environ, "HF_HUB_DISABLE_TELEMETRY": "1", "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"})
    for line in proc.stdout:
        log.write(line)
        if line.startswith("{"):
            print(line, end="", flush=True)
    returncode = proc.wait()
emit("run_done", returncode=returncode, minutes=round((time.time() - STARTED) / 60, 1))

# ------------------------------------------------------------------ checks
events_path = run_dir / "events.jsonl"
events = [json.loads(line) for line in events_path.read_text().splitlines() if line.startswith("{")] if events_path.exists() else []
by_kind: dict[str, list[dict]] = {}
for event in events:
    by_kind.setdefault(event["event"], []).append(event)
problems: list[str] = []
if returncode != 0:
    problems.append(f"qlora_unsloth.py exited {returncode}")
train = by_kind.get("train", [])
if not train:
    problems.append("no train events")
if any(not math.isfinite(e["loss"]) for e in train):
    problems.append("non-finite train loss")
if by_kind.get("nonfinite"):
    problems.append(f"{len(by_kind['nonfinite'])} non-finite steps")
validations = by_kind.get("validation", [])
if len(validations) < 2 or any(not math.isfinite(v["loss"]) for v in validations):
    problems.append("validation missing or non-finite")
adapter = run_dir / "adapter"
adapter_files = sorted(p.name for p in adapter.iterdir()) if adapter.exists() else []
if "adapter_model.safetensors" not in adapter_files or "adapter_config.json" not in adapter_files:
    problems.append(f"adapter not saved: {adapter_files}")
model_event = (by_kind.get("model") or [{}])[0]
kinds = model_event.get("lora_target_kinds") or {}
if set(kinds) - {"q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"}:
    problems.append(f"unexpected LoRA targets: {kinds}")
if adapter.exists():
    adapter_config = json.loads((adapter / "adapter_config.json").read_text())
    bad = [t for t in adapter_config.get("target_modules", []) if "linear_attn" in t or "visual" in t]
    if bad:
        problems.append(f"adapter targets Gated DeltaNet or vision modules: {bad[:3]}")

# Independent reload: fresh 4-bit base + the saved adapter, evaluated on the same held-out chunks.
independent = None
if adapter.exists() and not LOCAL:
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    sys.path.insert(0, str(script.parent))
    from qlora_unsloth import collate, lm_loss, load_chunks

    cfg = json.loads((run_dir / "config.json").read_text())
    compute = {"float32": torch.float32, "bfloat16": torch.bfloat16, "float16": torch.float16}[cfg["compute_dtype"]]
    tokenizer = AutoTokenizer.from_pretrained(str(adapter))
    base = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=compute, device_map={"": 0},
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                                               bnb_4bit_compute_dtype=compute),
    )
    model = PeftModel.from_pretrained(base, str(adapter)).eval()
    chunks = load_chunks(data_dir / "valid.jsonl", tokenizer, cfg["seq"], cfg["valid_chunks"])
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    total_loss, total_tokens = 0.0, 0
    with torch.no_grad():
        for chunk in chunks:
            input_ids, labels, attention = collate([chunk], "cuda", pad_id)
            with torch.autocast(device_type="cuda", dtype=compute, enabled=(compute != torch.float32)):
                loss, count = lm_loss(model, input_ids, attention, labels, cfg["loss_chunk"], checkpoint=False)
            total_loss += loss.item()
            total_tokens += count
    final_loss = validations[-1]["loss"] if validations else float("nan")
    independent = {"loss": total_loss / max(1, total_tokens), "tokens": total_tokens, "delta_vs_trained": total_loss / max(1, total_tokens) - final_loss,
                   "adapter_bytes": (adapter / "adapter_model.safetensors").stat().st_size}
    if abs(independent["delta_vs_trained"]) > 0.02:
        problems.append(f"independent adapter reload loss {independent['loss']:.4f} vs trained {final_loss:.4f}")
    emit("independent_reload", **independent)
    del model, base
    torch.cuda.empty_cache()

speeds = [e["tokens_per_second"] for e in train[1:]] or [e["tokens_per_second"] for e in train]
merged = (by_kind.get("merged") or [None])[-1]
summary = {
    "ok": not problems,
    "problems": problems,
    "returncode": returncode,
    "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
    "model": MODEL,
    "backend": BACKEND,
    "compute_dtype": (by_kind.get("hardware") or [{}])[0].get("compute_dtype"),
    "trainable_parameters": model_event.get("trainable_parameters"),
    "parameters": model_event.get("parameters"),
    "lora_targets": model_event.get("lora_targets"),
    "lora_target_kinds": kinds,
    "steps": train[-1]["step"] if train else 0,
    "tokens": train[-1]["tokens"] if train else 0,
    "completed": bool(by_kind.get("complete")) and by_kind["complete"][-1].get("completed") is True,
    "train_loss_first": train[0]["loss"] if train else None,
    "train_loss_last": train[-1]["loss"] if train else None,
    "validation": [{k: v.get(k) for k in ("step", "tokens", "loss", "final")} for v in validations],
    "tokens_per_second_median": statistics.median(speeds) if speeds else None,
    "tokens_per_second_max": max(speeds) if speeds else None,
    "peak_memory_gb": max((e.get("peak_memory_gb") or 0) for e in train) if train else None,
    "load_seconds": model_event.get("load_seconds"),
    "adapter_files": adapter_files,
    "independent_reload": independent,
    "merged": {k: merged.get(k) for k in ("path", "dtype", "merged_loss", "adapter_loss", "delta")} if merged else None,
    "minutes": round((time.time() - STARTED) / 60, 1),
    "versions": versions,
}
(OUTPUT / "summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
emit("summary", **{k: v for k, v in summary.items() if k not in ("validation", "independent_reload", "adapter_files")})
for v in summary["validation"]:
    print(f"  validation at step {v['step']:>3}: loss {v['loss']:.4f}", flush=True)
print("T4_QLORA_TEST_OK" if not problems else "T4_QLORA_TEST_FAILED: " + "; ".join(problems), flush=True)
if problems:
    raise SystemExit(1)
