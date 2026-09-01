#!/usr/bin/env python3
"""Compare a Falcon-H1 checkpoint with its base on a sealed corpus validation stream."""

from __future__ import annotations

import argparse
import gc
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from safetensors import safe_open
from torch.nn import functional
from transformers import AutoModelForCausalLM, AutoTokenizer

DEFAULT_PROMPTS = (
    "The relation between thought and language",
    "In the beginning was neither being nor nothing, but",
    "Consciousness is not an object because",
    "The geometry of",
    "h",
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--base", type=Path, required=True)
    result.add_argument("--checkpoint", type=Path, required=True)
    result.add_argument("--corpus", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--sequence-length", type=int, default=512)
    result.add_argument("--eval-batches", type=int, default=32)
    result.add_argument("--max-new-tokens", type=int, default=128)
    result.add_argument("--seed", type=int, default=20260901)
    return result


def parameter_group(name: str) -> str:
    if "embed_tokens" in name or "lm_head" in name:
        return "embedding_head"
    if "layernorm" in name or ".norm." in name:
        return "norms"
    if ".mamba.conv1d." in name:
        return "mamba_conv"
    if ".mamba.in_proj." in name:
        return "mamba_in_proj"
    if ".mamba.out_proj." in name:
        return "mamba_out_proj"
    if any(part in name for part in (".mamba.A_log", ".mamba.D", ".mamba.dt_bias")):
        return "mamba_dynamics"
    if ".self_attn.q_proj." in name or ".self_attn.k_proj." in name:
        return "attention_qk"
    if ".self_attn.v_proj." in name or ".self_attn.o_proj." in name:
        return "attention_vo"
    if ".feed_forward." in name:
        return "mlp"
    return "other"


def parameter_deltas(
    base: Path, checkpoint: Path
) -> dict[str, dict[str, float | int | None]]:
    accumulators: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {
            "elements": 0,
            "changed": 0,
            "base_square_sum": 0.0,
            "delta_square_sum": 0.0,
            "max_abs_delta": 0.0,
        }
    )
    with (
        safe_open(base / "model.safetensors", framework="pt", device="cpu") as original,
        safe_open(
            checkpoint / "model.safetensors", framework="pt", device="cpu"
        ) as trained,
    ):
        if set(original.keys()) != set(trained.keys()):
            raise RuntimeError("Base and checkpoint tensor names differ")
        for name in original:
            before = original.get_tensor(name).float()
            after = trained.get_tensor(name).float()
            delta = after - before
            values = accumulators[parameter_group(name)]
            values["elements"] += before.numel()
            values["changed"] += int((delta != 0).sum())
            values["base_square_sum"] += float((before * before).sum())
            values["delta_square_sum"] += float((delta * delta).sum())
            values["max_abs_delta"] = max(
                float(values["max_abs_delta"]), float(delta.abs().max())
            )

    result: dict[str, dict[str, float | int | None]] = {}
    for group, values in sorted(accumulators.items()):
        elements = int(values["elements"])
        base_rms = math.sqrt(float(values["base_square_sum"]) / elements)
        delta_rms = math.sqrt(float(values["delta_square_sum"]) / elements)
        result[group] = {
            "elements": elements,
            "changed_fraction": int(values["changed"]) / elements,
            "base_rms": base_rms,
            "delta_rms": delta_rms,
            "relative_delta_rms": delta_rms / base_rms if base_rms else None,
            "max_abs_delta": float(values["max_abs_delta"]),
        }
    return result


def optimizer_tensor_dtypes(checkpoint: Path) -> dict[str, int] | None:
    path = checkpoint / "optimizer.pt"
    if not path.is_file():
        return None
    state = torch.load(path, map_location="cpu", weights_only=True)
    counts: dict[str, int] = defaultdict(int)
    for parameter_state in state["state"].values():
        for name, value in parameter_state.items():
            if torch.is_tensor(value):
                counts[f"{name}:{value.dtype}"] += value.numel()
    return dict(sorted(counts.items()))


def evaluate_and_generate(
    model_path: Path,
    tokenizer,
    validation: np.memmap,
    prompts: list[str],
    *,
    sequence_length: int,
    eval_batches: int,
    max_new_tokens: int,
    seed: int,
) -> dict:
    model = AutoModelForCausalLM.from_pretrained(
        model_path, dtype=torch.bfloat16, local_files_only=True
    ).to("cuda")
    model.eval()
    negative_log_likelihood = 0.0
    correct = 0
    predicted_tokens = 0
    started = time.monotonic()
    with torch.inference_mode():
        for index in range(eval_batches):
            start = index * sequence_length
            tokens = np.asarray(
                validation[start : start + sequence_length + 1], dtype=np.int64
            )
            inputs = torch.from_numpy(tokens[:-1].copy()).unsqueeze(0).to("cuda")
            labels = torch.from_numpy(tokens[1:].copy()).unsqueeze(0).to("cuda")
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(input_ids=inputs, use_cache=False).logits
            negative_log_likelihood += float(
                functional.cross_entropy(
                    logits.float().reshape(-1, logits.shape[-1]),
                    labels.reshape(-1),
                    reduction="sum",
                )
            )
            correct += int((logits.argmax(-1) == labels).sum())
            predicted_tokens += labels.numel()
    torch.cuda.synchronize()
    loss = negative_log_likelihood / predicted_tokens
    metrics = {
        "negative_log_likelihood_sum": negative_log_likelihood,
        "predicted_tokens": predicted_tokens,
        "loss": loss,
        "perplexity": math.exp(loss),
        "accuracy": correct / predicted_tokens,
        "seconds": time.monotonic() - started,
    }

    generations = []
    for index, prompt in enumerate(prompts):
        encoded = tokenizer(prompt, return_tensors="pt")
        inputs = {
            key: value.to("cuda")
            for key, value in encoded.items()
            if key in ("input_ids", "attention_mask")
        }
        torch.manual_seed(seed + index)
        torch.cuda.manual_seed_all(seed + index)
        with torch.inference_mode():
            output = model.generate(
                **inputs,
                do_sample=True,
                temperature=0.8,
                top_p=0.95,
                repetition_penalty=1.08,
                max_new_tokens=max_new_tokens,
                use_cache=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        generations.append(
            {
                "prompt": prompt,
                "completion": tokenizer.decode(
                    output[0, inputs["input_ids"].shape[1] :], skip_special_tokens=True
                ),
            }
        )

    del model
    gc.collect()
    torch.cuda.empty_cache()
    return {"metrics": metrics, "generations": generations}


def main() -> None:
    args = parser().parse_args()
    if args.sequence_length < 2 or args.eval_batches < 1 or args.max_new_tokens < 1:
        raise ValueError(
            "Sequence length, eval batches, and generation length must be positive"
        )
    if not torch.cuda.is_available():
        raise RuntimeError("This comparison expects a CUDA or ROCm PyTorch device")

    base = args.base.expanduser().resolve()
    checkpoint = args.checkpoint.expanduser().resolve()
    corpus = args.corpus.expanduser().resolve()
    manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    validation_path = corpus / manifest["splits"]["validation"]["path"]
    validation = np.memmap(validation_path, dtype="<u2", mode="r")
    required = args.eval_batches * args.sequence_length + 1
    if len(validation) < required:
        raise RuntimeError(
            f"Validation stream has {len(validation)} tokens; need {required}"
        )

    tokenizer = AutoTokenizer.from_pretrained(base, local_files_only=True)
    prompts = list(DEFAULT_PROMPTS)
    prompts.append(
        tokenizer.decode(
            np.asarray(validation[:96], dtype=np.int64), skip_special_tokens=True
        )
    )
    result = {
        "schema_version": 1,
        "torch": torch.__version__,
        "hip": torch.version.hip,
        "device": torch.cuda.get_device_name(0),
        "base": str(base),
        "checkpoint": str(checkpoint),
        "validation": str(validation_path),
        "sequence_length": args.sequence_length,
        "eval_batches": args.eval_batches,
        "sampling": {
            "seed": args.seed,
            "temperature": 0.8,
            "top_p": 0.95,
            "repetition_penalty": 1.08,
            "max_new_tokens": args.max_new_tokens,
        },
        "optimizer_tensor_dtypes": optimizer_tensor_dtypes(checkpoint),
        "parameter_deltas": parameter_deltas(base, checkpoint),
        "models": {},
    }
    for label, path in (("base", base), ("checkpoint", checkpoint)):
        result["models"][label] = evaluate_and_generate(
            path,
            tokenizer,
            validation,
            prompts,
            sequence_length=args.sequence_length,
            eval_batches=args.eval_batches,
            max_new_tokens=args.max_new_tokens,
            seed=args.seed,
        )

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(output)
    print(json.dumps({"event": "comparison_complete", "output": str(output)}))


if __name__ == "__main__":
    main()
