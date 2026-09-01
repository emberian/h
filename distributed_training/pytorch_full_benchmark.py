#!/usr/bin/env python3
"""Bounded full-weight Falcon-H1 benchmark for PyTorch ROCm."""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM


DTYPES = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--dtype", choices=DTYPES, default="bf16")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--seq-len", type=int, default=256)
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--expected-arch")
    return parser.parse_args()


def sync() -> None:
    torch.cuda.synchronize()


def main() -> None:
    args = parse_args()
    if args.batch_size < 1 or args.seq_len < 2 or args.steps < 1:
        raise ValueError("batch size and steps must be positive; sequence length must be at least 2")
    if not torch.cuda.is_available():
        raise RuntimeError("ROCm GPU is unavailable")
    properties = torch.cuda.get_device_properties(0)
    if args.expected_arch and properties.gcnArchName != args.expected_arch:
        raise RuntimeError(f"expected {args.expected_arch}, got {properties.gcnArchName}")

    dtype = DTYPES[args.dtype]
    torch.manual_seed(20260901)
    torch.cuda.manual_seed_all(20260901)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        dtype=dtype,
        local_files_only=True,
    ).to("cuda")
    model.config.use_cache = False
    model.train()
    for parameter in model.parameters():
        parameter.requires_grad_(True)
    total_parameters = sum(parameter.numel() for parameter in model.parameters())
    trainable_parameters = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    if total_parameters != trainable_parameters:
        raise RuntimeError(f"not all parameters are trainable: {trainable_parameters}/{total_parameters}")

    input_ids = torch.randint(
        0,
        model.config.vocab_size,
        (args.batch_size, args.seq_len),
        dtype=torch.long,
        device="cuda",
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, foreach=False)
    results: list[dict[str, float]] = []

    for index in range(args.steps):
        optimizer.zero_grad(set_to_none=True)
        sync()
        started = time.perf_counter()
        output = model(
            input_ids=input_ids,
            labels=input_ids,
            use_cache=False,
            logits_to_keep=0,
        )
        output.loss.backward()
        optimizer.step()
        sync()
        seconds = time.perf_counter() - started

        gradients = [
            parameter.grad for parameter in model.parameters() if parameter.grad is not None
        ]
        if not gradients or not all(
            bool(torch.isfinite(gradient).all()) for gradient in gradients
        ):
            raise RuntimeError("missing or non-finite gradients")
        grad_norm = math.sqrt(
            sum(float(gradient.float().norm()) ** 2 for gradient in gradients)
        )
        results.append(
            {
                "step": index + 1,
                "loss": float(output.loss.detach()),
                "grad_norm": grad_norm,
                "seconds": seconds,
                "tokens_per_second": args.batch_size * args.seq_len / seconds,
            }
        )

    report = {
        "status": "ok",
        "framework": "pytorch-rocm",
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "hip": torch.version.hip,
        "gpu_name": torch.cuda.get_device_name(0),
        "gpu_arch": properties.gcnArchName,
        "hsa_override": os.environ.get("HSA_OVERRIDE_GFX_VERSION"),
        "dtype": args.dtype,
        "batch_size": args.batch_size,
        "sequence_length": args.seq_len,
        "steps": args.steps,
        "total_parameters": total_parameters,
        "trainable_parameters": trainable_parameters,
        "peak_allocated_mib": torch.cuda.max_memory_allocated() / 2**20,
        "peak_reserved_mib": torch.cuda.max_memory_reserved() / 2**20,
        "steps_detail": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
