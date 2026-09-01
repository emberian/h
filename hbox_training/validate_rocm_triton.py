#!/usr/bin/env python3
"""Validate the experimental ROCm Triton SSD path against Falcon-H1's reference mixer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import torch
from transformers import AutoModelForCausalLM

from rocm_triton_ssd import enable_rocm_triton_ssd


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--model", type=Path, required=True)
    result.add_argument("--mamba-root", type=Path, required=True)
    result.add_argument("--sequence-length", type=int, default=256)
    result.add_argument("--layer", type=int, default=0)
    result.add_argument("--seed", type=int, default=44)
    result.add_argument("--output", type=Path)
    result.add_argument("--relative-tolerance", type=float, default=0.01)
    return result


def error(reference: torch.Tensor, candidate: torch.Tensor) -> dict[str, float]:
    difference = (reference - candidate).abs()
    denominator = reference.abs().mean().clamp_min(1e-9)
    return {
        "max_abs": float(difference.max()),
        "mean_abs": float(difference.mean()),
        "relative_mean": float(difference.mean() / denominator),
    }


def main() -> None:
    args = parser().parse_args()
    if args.sequence_length < 2 or args.relative_tolerance <= 0:
        raise ValueError("Invalid sequence length or tolerance")
    kernel = enable_rocm_triton_ssd(args.mamba_root)
    model = AutoModelForCausalLM.from_pretrained(
        args.model.expanduser().resolve(), dtype=torch.bfloat16, local_files_only=True
    ).to("cuda")
    mixer = model.model.layers[args.layer].mamba
    mixer.train()
    torch.manual_seed(args.seed)
    inputs = torch.randn(
        1,
        args.sequence_length,
        model.config.hidden_size,
        dtype=torch.bfloat16,
        device="cuda",
    )

    def collect(*, reference: bool):
        mixer.zero_grad(set_to_none=True)
        hidden = inputs.detach().clone().requires_grad_(True)
        torch.cuda.synchronize()
        started = time.perf_counter()
        output = mixer.torch_forward(hidden) if reference else mixer(hidden)
        loss = output.float().square().mean()
        loss.backward()
        torch.cuda.synchronize()
        gradients = {
            name: parameter.grad.detach().float().cpu()
            for name, parameter in mixer.named_parameters()
            if parameter.grad is not None
        }
        return {
            "output": output.detach().float().cpu(),
            "input_gradient": hidden.grad.detach().float().cpu(),
            "parameter_gradients": gradients,
            "loss": float(loss.detach()),
            "seconds": time.perf_counter() - started,
        }

    reference = collect(reference=True)
    first_triton = collect(reference=False)
    warm_triton = collect(reference=False)
    if set(reference["parameter_gradients"]) != set(warm_triton["parameter_gradients"]):
        raise RuntimeError("Reference and Triton paths produced different parameter-gradient keys")

    result = {
        "schema_version": 1,
        "kernel": kernel,
        "layer": args.layer,
        "sequence_length": args.sequence_length,
        "relative_tolerance": args.relative_tolerance,
        "reference_loss": reference["loss"],
        "triton_loss": warm_triton["loss"],
        "reference_seconds": reference["seconds"],
        "first_triton_seconds": first_triton["seconds"],
        "warm_triton_seconds": warm_triton["seconds"],
        "output_error": error(reference["output"], warm_triton["output"]),
        "input_gradient_error": error(
            reference["input_gradient"], warm_triton["input_gradient"]
        ),
        "parameter_gradient_errors": {
            name: error(reference["parameter_gradients"][name], candidate)
            for name, candidate in warm_triton["parameter_gradients"].items()
        },
    }
    relative_errors = [
        result["output_error"]["relative_mean"],
        result["input_gradient_error"]["relative_mean"],
        *(
            value["relative_mean"]
            for value in result["parameter_gradient_errors"].values()
        ),
    ]
    result["maximum_relative_mean_error"] = max(relative_errors)
    result["ok"] = result["maximum_relative_mean_error"] <= args.relative_tolerance
    if args.output is not None:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        temporary.replace(output)
    print(json.dumps(result, indent=2))
    if not result["ok"]:
        raise RuntimeError("ROCm Triton SSD parity exceeded the declared tolerance")


if __name__ == "__main__":
    main()
