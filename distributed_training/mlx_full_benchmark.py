#!/usr/bin/env python3
"""Bounded full-weight Falcon-H1 training benchmark for Apple MLX."""

from __future__ import annotations

import argparse
import json
import time
from functools import partial
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx_lm import load
from mlx.utils import tree_flatten


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(
            "/Users/ember/.cache/h1-distributed/models/Falcon-H1-Tiny-90M-Base"
        ),
    )
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--seq-len", type=int, default=256)
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.batch_size < 1 or args.seq_len < 2 or args.steps < 1:
        raise ValueError("batch size and steps must be positive; sequence length must be at least 2")

    model, _ = load(str(args.model))
    model.unfreeze()
    model.train()
    parameters = tree_flatten(model.parameters())
    trainable = tree_flatten(model.trainable_parameters())
    total_parameters = sum(value.size for _, value in parameters)
    trainable_parameters = sum(value.size for _, value in trainable)
    if total_parameters != trainable_parameters:
        raise RuntimeError(
            f"not all parameters are trainable: {trainable_parameters}/{total_parameters}"
        )

    optimizer = optim.AdamW(learning_rate=args.learning_rate)

    def loss_fn(current_model: nn.Module, tokens: mx.array) -> mx.array:
        logits = current_model(tokens[:, :-1]).astype(mx.float32)
        targets = tokens[:, 1:]
        return nn.losses.cross_entropy(logits, targets).mean()

    loss_and_grad = nn.value_and_grad(model, loss_fn)
    compile_state = [model.state, optimizer.state]

    @partial(mx.compile, inputs=compile_state, outputs=compile_state)
    def step(tokens: mx.array) -> tuple[mx.array, mx.array]:
        loss, gradients = loss_and_grad(model, tokens)
        gradient_squares = [
            mx.sum(gradient.astype(mx.float32) ** 2)
            for _, gradient in tree_flatten(gradients)
        ]
        gradient_norm = mx.sqrt(sum(gradient_squares))
        optimizer.update(model, gradients)
        return loss, gradient_norm

    mx.random.seed(20260901)
    tokens = mx.random.randint(
        0,
        model.args.vocab_size,
        shape=(args.batch_size, args.seq_len + 1),
    )
    mx.eval(tokens, model.parameters())
    mx.reset_peak_memory()

    results: list[dict[str, float]] = []
    for index in range(args.steps):
        before = {
            name: value + mx.zeros_like(value)
            for name, value in tree_flatten(model.parameters())
        }
        mx.eval(before)
        started = time.perf_counter()
        loss, gradient_norm = step(tokens)
        mx.eval(loss, gradient_norm, model.parameters(), optimizer.state)
        mx.synchronize()
        seconds = time.perf_counter() - started
        after = dict(tree_flatten(model.parameters()))
        changed_elements = 0
        changed_tensors = 0
        total_elements = 0
        max_parameter_delta = 0.0
        for name, old_value in before.items():
            new_value = after[name]
            tensor_changed_elements = int(mx.sum(old_value != new_value).item())
            changed_elements += tensor_changed_elements
            changed_tensors += int(tensor_changed_elements > 0)
            total_elements += old_value.size
            max_parameter_delta = max(
                max_parameter_delta,
                float(mx.max(mx.abs(old_value - new_value)).item()),
            )
        results.append(
            {
                "step": index + 1,
                "loss": float(loss.item()),
                "gradient_l2_norm": float(gradient_norm.item()),
                "changed_parameter_elements": changed_elements,
                "changed_parameter_fraction": changed_elements / total_elements,
                "changed_parameter_tensors": changed_tensors,
                "total_parameter_tensors": len(before),
                "max_parameter_delta": max_parameter_delta,
                "seconds": seconds,
                "tokens_per_second": args.batch_size * args.seq_len / seconds,
            }
        )

    report = {
        "status": "ok",
        "framework": "mlx",
        "device": mx.device_info(),
        "batch_size": args.batch_size,
        "sequence_length": args.seq_len,
        "steps": args.steps,
        "total_parameters": total_parameters,
        "trainable_parameters": trainable_parameters,
        "parameter_dtypes": sorted({str(value.dtype) for _, value in parameters}),
        "active_memory_mib": mx.get_active_memory() / 2**20,
        "cache_memory_mib": mx.get_cache_memory() / 2**20,
        "peak_memory_mib": mx.get_peak_memory() / 2**20,
        "steps_detail": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
