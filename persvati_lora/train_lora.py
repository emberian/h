#!/usr/bin/env python3
"""Deterministic Falcon-H1 all-linear LoRA continued pretraining on persvati."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
import time

import numpy as np
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
import torch
import torch.nn.functional as functional
from transformers import AutoConfig, AutoModelForCausalLM


TOKENIZER_FILES = (
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "generation_config.json",
)
TARGET_MODULES = (
    "gate_proj",
    "up_proj",
    "down_proj",
    "in_proj",
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--model-dir", type=Path, required=True)
    result.add_argument("--corpus-dir", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--resume", type=Path)
    result.add_argument("--rank", type=int, default=16)
    result.add_argument("--alpha", type=int, default=32)
    result.add_argument("--sequence-length", type=int, default=512)
    result.add_argument("--batch-size", type=int, default=1)
    result.add_argument("--accumulation-steps", type=int, default=4)
    result.add_argument("--total-tokens", type=int, default=374_405_120)
    result.add_argument("--warmup-tokens", type=int, default=3_000_000)
    result.add_argument("--learning-rate", type=float, default=3e-4)
    result.add_argument("--min-learning-rate-ratio", type=float, default=0.1)
    result.add_argument("--weight-decay", type=float, default=0.0)
    result.add_argument("--max-gradient-norm", type=float, default=1.0)
    result.add_argument("--seed", type=int, default=17)
    result.add_argument(
        "--save-tokens",
        default="10000000,30000000,100000000,300000000,374405120",
    )
    result.add_argument("--eval-every-tokens", type=int, default=10_000_000)
    result.add_argument("--eval-batches", type=int, default=8)
    result.add_argument("--log-steps", type=int, default=10)
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def verify_corpus(root: Path, *, vocab_size: int, eos_token_id: int) -> dict:
    upload = json.loads((root / "upload-manifest.json").read_text(encoding="utf-8"))
    if upload.get("schema_version") != 1 or upload.get("sealed") is not True:
        raise RuntimeError("Corpus is not a sealed schema-v1 bundle")
    for name, expected in upload["files"].items():
        path = (root / name).resolve()
        if path.parent != root.resolve() or not path.is_file():
            raise RuntimeError(f"Invalid sealed corpus path: {name!r}")
        if path.stat().st_size != int(expected["bytes"]) or sha256(path) != expected["sha256"]:
            raise RuntimeError(f"Sealed corpus hash/size mismatch: {name}")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    validation = json.loads((root / "validation-report.json").read_text(encoding="utf-8"))
    if validation.get("ok") is not True:
        raise RuntimeError("Corpus validation report is not successful")
    for key, expected in (("vocab_size", vocab_size), ("eos_token_id", eos_token_id)):
        if int(manifest.get(key, -1)) != expected or int(validation.get(key, -1)) != expected:
            raise RuntimeError(f"Corpus {key} does not match model config")
    if manifest.get("dtype") != "little-endian uint16":
        raise RuntimeError(f"Unsupported corpus dtype: {manifest.get('dtype')}")
    if validation["dataset_manifest_sha256"] != manifest["source_manifest_sha256"]:
        raise RuntimeError("Corpus manifest and validation report disagree")
    for split in ("train", "validation"):
        expected = manifest["splits"][split]
        checked = validation["splits"][split]
        if checked["sha256"] != expected["sha256"]:
            raise RuntimeError(f"Corpus validation hash mismatch for {split}")
        if int(checked["maximum_token_id"]) >= vocab_size:
            raise RuntimeError(f"Out-of-vocabulary token in {split}")
    return manifest


class TokenStream:
    def __init__(self, path: Path, sequence_length: int, seed: int, *, validation: bool = False):
        self.tokens = np.memmap(path, dtype="<u2", mode="r")
        self.sequence_length = sequence_length
        self.sequence_count = (len(self.tokens) - 1) // sequence_length
        if self.sequence_count < 1:
            raise ValueError(f"Token stream is too short: {path}")
        if validation:
            self.shift, self.stride = 0, 1
        else:
            rng = np.random.default_rng(seed)
            self.shift = int(rng.integers(0, self.sequence_count))
            stride = int(rng.integers(1, self.sequence_count + 1))
            while math.gcd(stride, self.sequence_count) != 1:
                stride = stride % self.sequence_count + 1
            self.stride = stride

    def batch(self, example_offset: int, count: int) -> torch.Tensor:
        order = np.arange(example_offset, example_offset + count, dtype=np.int64)
        sequence_ids = (self.shift + order * self.stride) % self.sequence_count
        values = np.empty((count, self.sequence_length + 1), dtype=np.int64)
        for row, sequence_id in enumerate(sequence_ids):
            start = int(sequence_id) * self.sequence_length
            values[row] = self.tokens[start : start + self.sequence_length + 1]
        return torch.from_numpy(values)


def learning_rate(step: int, total_steps: int, warmup_steps: int, peak: float, floor: float) -> float:
    if step < warmup_steps:
        return peak * step / max(1, warmup_steps)
    progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
    multiplier = floor + 0.5 * (1.0 - floor) * (1.0 + math.cos(math.pi * progress))
    return peak * multiplier


def save_checkpoint(root: Path, model, optimizer, model_dir: Path, state: dict) -> None:
    root.parent.mkdir(parents=True, exist_ok=True)
    if root.exists():
        raise FileExistsError(f"Refusing to overwrite checkpoint: {root}")
    staging = Path(tempfile.mkdtemp(prefix=f".{root.name}.", dir=root.parent))
    try:
        model.save_pretrained(staging, safe_serialization=True, save_embedding_layers=False)
        for name in TOKENIZER_FILES:
            source = model_dir / name
            if source.is_file():
                shutil.copy2(source, staging / name)
        torch.save(optimizer.state_dict(), staging / "optimizer.pt")
        atomic_json(staging / "trainer_state.json", state)
        os.replace(staging, root)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def validate_args(args: argparse.Namespace) -> None:
    for name in (
        "rank",
        "alpha",
        "sequence_length",
        "batch_size",
        "accumulation_steps",
        "total_tokens",
        "warmup_tokens",
        "eval_every_tokens",
        "eval_batches",
        "log_steps",
    ):
        if int(getattr(args, name)) < 1:
            raise ValueError(f"--{name.replace('_', '-')} must be positive")
    if args.learning_rate <= 0 or args.weight_decay < 0 or args.max_gradient_norm <= 0:
        raise ValueError("Invalid optimizer hyperparameters")
    if not 0 <= args.min_learning_rate_ratio <= 1:
        raise ValueError("--min-learning-rate-ratio must be between zero and one")


def main() -> None:
    args = parser().parse_args()
    validate_args(args)
    if not torch.cuda.is_available():
        raise RuntimeError("ROCm GPU is unavailable")
    if torch.cuda.get_device_properties(0).gcnArchName != "gfx1100":
        raise RuntimeError("HSA_OVERRIDE_GFX_VERSION=11.0.0 is required on persvati")
    model_dir = args.model_dir.expanduser().resolve()
    corpus_dir = args.corpus_dir.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    config = AutoConfig.from_pretrained(model_dir, local_files_only=True)
    config.use_cache = False
    manifest = verify_corpus(
        corpus_dir, vocab_size=int(config.vocab_size), eos_token_id=int(config.eos_token_id)
    )
    train_path = corpus_dir / manifest["splits"]["train"]["path"]
    validation_path = corpus_dir / manifest["splits"]["validation"]["path"]
    tokens_per_step = args.batch_size * args.accumulation_steps * args.sequence_length
    total_steps = math.ceil(args.total_tokens / tokens_per_step)
    warmup_steps = max(1, math.ceil(args.warmup_tokens / tokens_per_step))
    run_settings = {
        "rank": args.rank,
        "alpha": args.alpha,
        "target_modules": list(TARGET_MODULES),
        "adapter_dtype": "bfloat16",
        "sequence_length": args.sequence_length,
        "batch_size": args.batch_size,
        "accumulation_steps": args.accumulation_steps,
        "tokens_per_step": tokens_per_step,
        "total_tokens": args.total_tokens,
        "warmup_tokens": args.warmup_tokens,
        "learning_rate": args.learning_rate,
        "min_learning_rate_ratio": args.min_learning_rate_ratio,
        "weight_decay": args.weight_decay,
        "max_gradient_norm": args.max_gradient_norm,
        "seed": args.seed,
    }

    base = AutoModelForCausalLM.from_pretrained(
        model_dir, dtype=torch.bfloat16, local_files_only=True
    )
    base.config.use_cache = False
    if args.resume is not None:
        load_from = args.resume.expanduser().resolve()
        model = PeftModel.from_pretrained(
            base,
            load_from,
            is_trainable=True,
            autocast_adapter_dtype=False,
        )
        state = json.loads((load_from / "trainer_state.json").read_text(encoding="utf-8"))
        mismatches = {
            key: (state.get(key), expected)
            for key, expected in run_settings.items()
            if state.get(key) != expected
        }
        if mismatches:
            raise RuntimeError(f"Resume settings do not match: {mismatches}")
        start_step = int(state["step"])
    else:
        lora = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=args.rank,
            lora_alpha=args.alpha,
            lora_dropout=0.0,
            bias="none",
            target_modules=list(TARGET_MODULES),
        )
        model = get_peft_model(base, lora, autocast_adapter_dtype=False)
        start_step = 0
    model = model.to("cuda")
    model.train()
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    trainable_count = sum(parameter.numel() for parameter in trainable)
    total_count = sum(parameter.numel() for parameter in model.parameters())
    if not 0 < trainable_count < total_count // 10:
        raise RuntimeError(f"Unexpected LoRA trainable count: {trainable_count}/{total_count}")
    if {parameter.dtype for parameter in trainable} != {torch.bfloat16}:
        raise RuntimeError("LoRA adapter parameters are not uniformly BF16")
    optimizer = torch.optim.AdamW(
        trainable,
        lr=args.learning_rate,
        betas=(0.9, 0.95),
        eps=1e-8,
        weight_decay=args.weight_decay,
        foreach=False,
    )
    if args.resume is not None:
        optimizer.load_state_dict(
            torch.load(load_from / "optimizer.pt", map_location="cuda", weights_only=True)
        )
    if start_step < 0 or start_step > total_steps:
        raise RuntimeError(f"Resume step {start_step} is outside this run")

    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    training = TokenStream(train_path, args.sequence_length, args.seed)
    validation = TokenStream(validation_path, args.sequence_length, 0, validation=True)
    start_tokens = min(start_step * tokens_per_step, args.total_tokens)
    save_thresholds = sorted(
        {
            *(int(value) for value in args.save_tokens.split(",") if value.strip()),
            args.total_tokens,
        }
    )
    save_thresholds = [value for value in save_thresholds if start_tokens < value <= args.total_tokens]
    next_eval = (start_tokens // args.eval_every_tokens + 1) * args.eval_every_tokens
    atomic_json(
        output / "run-manifest.json",
        {
            "schema_version": 1,
            **run_settings,
            "start_step": start_step,
            "start_tokens": start_tokens,
            "base_parameters": total_count,
            "trainable_parameters": trainable_count,
            "model_safetensors_sha256": sha256(model_dir / "model.safetensors"),
            "corpus_upload_manifest_sha256": sha256(corpus_dir / "upload-manifest.json"),
            "torch": torch.__version__,
            "device": torch.cuda.get_device_name(0),
        },
    )

    started = interval_started = time.monotonic()
    interval_tokens = 0
    print(
        json.dumps(
            {
                "event": "start",
                "base_parameters": total_count,
                "trainable_parameters": trainable_count,
                "tokens_per_step": tokens_per_step,
                "total_steps": total_steps,
                "start_step": start_step,
            }
        ),
        flush=True,
    )
    optimizer.zero_grad(set_to_none=True)
    for step in range(start_step, total_steps):
        loss_total = accuracy_total = 0.0
        for micro in range(args.accumulation_steps):
            offset = step * args.batch_size * args.accumulation_steps + micro * args.batch_size
            tokens = training.batch(offset, args.batch_size).to("cuda")
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                logits = model(input_ids=tokens[:, :-1], use_cache=False).logits
                labels = tokens[:, 1:]
                loss = functional.cross_entropy(
                    logits.float().reshape(-1, logits.shape[-1]), labels.reshape(-1)
                )
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError(f"Non-finite loss at step {step + 1}")
            (loss / args.accumulation_steps).backward()
            loss_total += float(loss.detach())
            accuracy_total += float((logits.detach().argmax(-1) == labels).float().mean())

        lr = learning_rate(
            step,
            total_steps,
            min(warmup_steps, total_steps),
            args.learning_rate,
            args.min_learning_rate_ratio,
        )
        for group in optimizer.param_groups:
            group["lr"] = lr
        gradient_norm = torch.nn.utils.clip_grad_norm_(
            trainable, args.max_gradient_norm, error_if_nonfinite=True
        )
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        torch.cuda.synchronize()
        exposed_tokens = min((step + 1) * tokens_per_step, args.total_tokens)
        interval_tokens += tokens_per_step
        if (step + 1) % args.log_steps == 0 or step == start_step:
            now = time.monotonic()
            print(
                json.dumps(
                    {
                        "event": "train",
                        "step": step + 1,
                        "tokens": exposed_tokens,
                        "loss": loss_total / args.accumulation_steps,
                        "accuracy": accuracy_total / args.accumulation_steps,
                        "gradient_norm": float(gradient_norm),
                        "learning_rate": lr,
                        "tokens_per_second": interval_tokens / (now - interval_started),
                    }
                ),
                flush=True,
            )
            interval_started, interval_tokens = now, 0

        if exposed_tokens >= next_eval:
            model.eval()
            eval_loss = eval_accuracy = 0.0
            with torch.no_grad():
                for index in range(args.eval_batches):
                    tokens = validation.batch(index * args.batch_size, args.batch_size).to("cuda")
                    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                        logits = model(input_ids=tokens[:, :-1], use_cache=False).logits
                        labels = tokens[:, 1:]
                        loss = functional.cross_entropy(
                            logits.float().reshape(-1, logits.shape[-1]), labels.reshape(-1)
                        )
                    eval_loss += float(loss)
                    eval_accuracy += float((logits.argmax(-1) == labels).float().mean())
            if not math.isfinite(eval_loss):
                raise FloatingPointError(f"Non-finite validation at step {step + 1}")
            print(
                json.dumps(
                    {
                        "event": "validation",
                        "step": step + 1,
                        "tokens": exposed_tokens,
                        "loss": eval_loss / args.eval_batches,
                        "accuracy": eval_accuracy / args.eval_batches,
                    }
                ),
                flush=True,
            )
            model.train()
            next_eval += args.eval_every_tokens

        while save_thresholds and exposed_tokens >= save_thresholds[0]:
            threshold = save_thresholds.pop(0)
            checkpoint = output / f"tokens-{threshold:012d}"
            save_checkpoint(
                checkpoint,
                model,
                optimizer,
                model_dir,
                {
                    **run_settings,
                    "step": step + 1,
                    "tokens": exposed_tokens,
                    "requested_token_threshold": threshold,
                    "elapsed_seconds": time.monotonic() - started,
                    "base_parameters": total_count,
                    "trainable_parameters": trainable_count,
                },
            )
            print(json.dumps({"event": "checkpoint", "path": str(checkpoint)}), flush=True)

    atomic_json(
        output / "training-complete.json",
        {
            "completed": True,
            "steps": total_steps,
            "tokens": args.total_tokens,
            "elapsed_seconds": time.monotonic() - started,
        },
    )


if __name__ == "__main__":
    main()
