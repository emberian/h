#!/usr/bin/env python3
"""Parity and speed gate for the upstream causal-conv1d ROCm extension."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch
import torch.nn.functional as F
from causal_conv1d import causal_conv1d_fn


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--batch-size", type=int, default=1)
    result.add_argument("--channels", type=int, default=896)
    result.add_argument("--sequence-length", type=int, default=512)
    result.add_argument("--kernel-size", type=int, default=4)
    result.add_argument("--warmup", type=int, default=10)
    result.add_argument("--iterations", type=int, default=50)
    result.add_argument("--seed", type=int, default=1729)
    result.add_argument("--output", type=Path)
    return result


def error(reference: torch.Tensor, candidate: torch.Tensor) -> dict[str, float]:
    ref = reference.detach().float()
    got = candidate.detach().float()
    delta = got - ref
    reference_norm = torch.linalg.vector_norm(ref.double()).item()
    candidate_norm = torch.linalg.vector_norm(got.double()).item()
    dot = torch.dot(ref.double().reshape(-1), got.double().reshape(-1)).item()
    return {
        "mean_abs": delta.abs().mean().item(),
        "max_abs": delta.abs().max().item(),
        "relative_mean": delta.abs().mean().item()
        / max(ref.abs().mean().item(), 1e-12),
        "cosine": dot / max(reference_norm * candidate_norm, 1e-30),
    }


def grouped_reference(
    x: torch.Tensor,
    weight: torch.Tensor,
    bias: torch.Tensor,
) -> torch.Tensor:
    sequence_length = x.shape[-1]
    convolved = F.conv1d(
        x,
        weight.unsqueeze(1),
        bias,
        padding=weight.shape[-1] - 1,
        groups=x.shape[1],
    )[..., :sequence_length]
    return F.silu(convolved)


def run_backward(
    implementation,
    x: torch.Tensor,
    weight: torch.Tensor,
    bias: torch.Tensor,
    upstream: torch.Tensor,
) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
    local_x = x.detach().clone().requires_grad_(True)
    local_weight = weight.detach().clone().requires_grad_(True)
    local_bias = bias.detach().clone().requires_grad_(True)
    output = implementation(local_x, local_weight, local_bias)
    torch.autograd.backward(output, upstream)
    return output.detach(), (
        local_x.grad.detach(),
        local_weight.grad.detach(),
        local_bias.grad.detach(),
    )


def benchmark(
    implementation,
    x: torch.Tensor,
    weight: torch.Tensor,
    bias: torch.Tensor,
    upstream: torch.Tensor,
    warmup: int,
    iterations: int,
) -> float:
    for _ in range(warmup):
        _, gradients = run_backward(implementation, x, weight, bias, upstream)
        del gradients
    torch.cuda.synchronize()
    started = time.perf_counter()
    for _ in range(iterations):
        _, gradients = run_backward(implementation, x, weight, bias, upstream)
        del gradients
    torch.cuda.synchronize()
    return (time.perf_counter() - started) / iterations


def main() -> None:
    args = parser().parse_args()
    if (
        min(
            args.batch_size,
            args.channels,
            args.sequence_length,
            args.kernel_size,
            args.warmup,
            args.iterations,
        )
        < 1
    ):
        raise ValueError("All shape and iteration arguments must be positive")
    if not torch.cuda.is_available():
        raise RuntimeError("This benchmark requires the hbox ROCm device")

    device = torch.device("cuda")
    generator = torch.Generator(device=device).manual_seed(args.seed)
    shape = (args.batch_size, args.channels, args.sequence_length)
    x = (
        torch.randn(shape, device=device, dtype=torch.bfloat16, generator=generator)
        * 0.1
    )
    weight = (
        torch.randn(
            (args.channels, args.kernel_size),
            device=device,
            dtype=torch.bfloat16,
            generator=generator,
        )
        * 0.1
    )
    bias = (
        torch.randn(
            (args.channels,), device=device, dtype=torch.bfloat16, generator=generator
        )
        * 0.1
    )
    upstream = (
        torch.randn(shape, device=device, dtype=torch.bfloat16, generator=generator)
        * 0.1
    )

    def causal(x_value, weight_value, bias_value):
        return causal_conv1d_fn(x_value, weight_value, bias_value, activation="silu")

    reference_output, reference_gradients = run_backward(
        grouped_reference, x, weight, bias, upstream
    )
    causal_output, causal_gradients = run_backward(causal, x, weight, bias, upstream)
    output_error = error(reference_output, causal_output)
    gradient_errors = {
        name: error(reference, candidate)
        for name, reference, candidate in zip(
            ("input", "weight", "bias"),
            reference_gradients,
            causal_gradients,
            strict=True,
        )
    }

    grouped_seconds = benchmark(
        grouped_reference,
        x,
        weight,
        bias,
        upstream,
        args.warmup,
        args.iterations,
    )
    causal_seconds = benchmark(
        causal,
        x,
        weight,
        bias,
        upstream,
        args.warmup,
        args.iterations,
    )
    checks = {
        "finite": all(
            torch.isfinite(value).all().item()
            for value in (
                reference_output,
                causal_output,
                *reference_gradients,
                *causal_gradients,
            )
        ),
        "output": output_error["relative_mean"] <= 0.01
        and output_error["cosine"] >= 0.999,
        "gradients": all(
            values["relative_mean"] <= 0.02 and values["cosine"] >= 0.995
            for values in gradient_errors.values()
        ),
        "faster": causal_seconds < grouped_seconds,
    }
    report = {
        "schema_version": 1,
        "torch": torch.__version__,
        "hip": torch.version.hip,
        "device": torch.cuda.get_device_name(),
        "dtype": "bfloat16",
        "shape": {
            "batch": args.batch_size,
            "channels": args.channels,
            "sequence_length": args.sequence_length,
            "kernel_size": args.kernel_size,
        },
        "output_error": output_error,
        "gradient_errors": gradient_errors,
        "grouped_conv1d_seconds": grouped_seconds,
        "causal_conv1d_seconds": causal_seconds,
        "speedup": grouped_seconds / causal_seconds,
        "checks": checks,
        "ok": all(checks.values()),
    }
    rendered = json.dumps(report, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered, flush=True)
    if not report["ok"]:
        raise RuntimeError("causal-conv1d failed parity or performance gate")


if __name__ == "__main__":
    main()
