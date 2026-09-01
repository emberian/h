#!/usr/bin/env python3
"""Bounded, real-token, full-weight Falcon-H1 PyTorch/XLA training gate.

Run this as a script in a Kaggle TPU v5e-8 notebook. Start with one device.
Only try all eight devices after one-device compilation and optimizer steps pass.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokens-npy", type=Path, required=True)
    parser.add_argument(
        "--model",
        default="tiiuae/Falcon-H1-Tiny-90M-Base",
    )
    parser.add_argument(
        "--revision",
        default="7994372e93b62822ae25f8bfb19f653649cea3a3",
    )
    parser.add_argument("--devices", type=int, choices=(1, 8), default=1)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--seq-len", type=int, default=256)
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    return parser.parse_args()


def _worker(index: int, args: argparse.Namespace) -> None:
    # Importing or touching an XLA device before torch_xla.launch is unsafe.
    import torch_xla
    import torch_xla.core.xla_model as xm
    import torch_xla.debug.metrics as met
    import torch_xla.runtime as xr

    device = torch_xla.device()
    rank = xr.global_ordinal()
    world_size = xr.world_size()
    tokens = np.load(args.tokens_npy, mmap_mode="r", allow_pickle=False)
    if tokens.ndim != 1 or not np.issubdtype(tokens.dtype, np.integer):
        raise TypeError("--tokens-npy must be a one-dimensional integer NumPy array")
    tokens_per_batch = args.batch_size * (args.seq_len + 1)
    if tokens.size < world_size * tokens_per_batch:
        raise ValueError("token stream is too short for one distinct batch per rank")

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        revision=args.revision,
        dtype=torch.bfloat16,
    )
    model.config.use_cache = False
    model.train()
    for parameter in model.parameters():
        parameter.requires_grad_(True)
    model.to(device)
    total_parameters = sum(parameter.numel() for parameter in model.parameters())
    trainable_parameters = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    if total_parameters != trainable_parameters:
        raise RuntimeError(
            f"not all parameters are trainable: {trainable_parameters}/{total_parameters}"
        )
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        foreach=False,
    )

    # Fixed shapes are intentional: recompilation would make a short TPU test misleading.
    rank_offset = rank * tokens_per_batch
    rank_tokens = np.asarray(
        tokens[rank_offset : rank_offset + tokens_per_batch],
        dtype=np.int64,
    ).reshape(args.batch_size, args.seq_len + 1)
    input_ids = torch.from_numpy(rank_tokens).to(device)

    step_reports: list[dict[str, float | int]] = []
    for step_index in range(args.steps):
        optimizer.zero_grad(set_to_none=True)
        torch_xla.sync(wait=True)
        started = time.perf_counter()
        output = model(
            input_ids=input_ids,
            labels=input_ids,
            use_cache=False,
        )
        output.loss.backward()
        gradients = [
            parameter.grad
            for parameter in model.parameters()
            if parameter.grad is not None
        ]
        if not gradients:
            raise RuntimeError("no gradients were produced")
        gradient_norm = torch.sqrt(
            sum(torch.sum(gradient.float() ** 2) for gradient in gradients)
        )
        xm.optimizer_step(optimizer, barrier=True)
        torch_xla.sync(wait=True)
        seconds = time.perf_counter() - started
        # Each rank reports; use the slowest rank for honest global throughput.
        max_seconds = xm.mesh_reduce(
            f"step-{step_index}-seconds",
            seconds,
            max,
        )
        step_reports.append(
            {
                "step": step_index + 1,
                "loss": float(output.loss.detach().cpu()),
                "gradient_l2_norm": float(gradient_norm.detach().cpu()),
                "max_rank_seconds": max_seconds,
                "global_tokens_per_second": (
                    world_size * args.batch_size * args.seq_len / max_seconds
                ),
            }
        )

    finite = all(
        math.isfinite(float(report["loss"]))
        and math.isfinite(float(report["gradient_l2_norm"]))
        and float(report["gradient_l2_norm"]) > 0
        for report in step_reports
    )
    if not finite:
        raise RuntimeError("loss or gradient check failed")
    if rank == 0:
        report = {
            "status": "ok",
            "warning": (
                "Falcon-H1 used the Transformers fallback Mamba path; verify XLA "
                "metrics and warmed throughput before treating TPU as primary"
            ),
            "torch": torch.__version__,
            "torch_xla": torch_xla.__version__,
            "pjrt_device": os.environ.get("PJRT_DEVICE"),
            "world_size": world_size,
            "dtype": "bfloat16",
            "model": args.model,
            "revision": args.revision,
            "total_parameters": total_parameters,
            "trainable_parameters": trainable_parameters,
            "batch_size_per_rank": args.batch_size,
            "sequence_length": args.seq_len,
            "real_token_file": str(args.tokens_npy),
            "steps_detail": step_reports,
        }
        print(json.dumps(report, indent=2, sort_keys=True), flush=True)
        print(met.short_metrics_report(), flush=True)


def main() -> None:
    args = parse_args()
    if args.steps < 2:
        raise ValueError("use at least two steps so compile and warmed timing are visible")
    os.environ.setdefault("PJRT_DEVICE", "TPU")
    os.environ.setdefault("XLA_USE_BF16", "1")
    import torch_xla

    torch_xla.launch(_worker, args=(args,), nprocs=args.devices)


if __name__ == "__main__":
    main()
