#!/usr/bin/env python3
"""Compare H1's mixed FP16/BF16 compute policy with the BF16 Triton baseline."""

from __future__ import annotations

import argparse
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from compare_checkpoints import parameter_group
from rocm_triton_ssd import enable_rocm_triton_ssd
from torch.nn import functional
from transformers import AutoModelForCausalLM


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--model", type=Path, required=True)
    result.add_argument("--corpus", type=Path, required=True)
    result.add_argument("--mamba-root", type=Path, required=True)
    result.add_argument("--sequence-length", type=int, default=512)
    result.add_argument("--eval-batches", type=int, default=4)
    result.add_argument("--sample-stride", type=int, default=8)
    result.add_argument("--output", type=Path)
    result.add_argument("--max-loss-delta", type=float, default=0.02)
    result.add_argument("--max-logit-relative-mean", type=float, default=0.03)
    result.add_argument("--min-top1-agreement", type=float, default=0.98)
    result.add_argument("--min-gradient-cosine", type=float, default=0.995)
    result.add_argument("--min-group-gradient-cosine", type=float, default=0.98)
    return result


def tensor_error(reference: torch.Tensor, candidate: torch.Tensor) -> dict[str, float]:
    difference = candidate - reference
    reference_norm = torch.linalg.vector_norm(reference.double())
    candidate_norm = torch.linalg.vector_norm(candidate.double())
    dot = torch.dot(reference.double().reshape(-1), candidate.double().reshape(-1))
    denominator = reference.abs().mean().clamp_min(1e-12)
    return {
        "mean_abs": float(difference.abs().mean()),
        "max_abs": float(difference.abs().max()),
        "relative_mean": float(difference.abs().mean() / denominator),
        "cosine": float(dot / (reference_norm * candidate_norm).clamp_min(1e-30)),
        "reference_norm": float(reference_norm),
        "candidate_norm": float(candidate_norm),
    }


def gradient_error_accumulators():
    return defaultdict(
        lambda: {
            "elements": 0,
            "reference_abs_sum": 0.0,
            "difference_abs_sum": 0.0,
            "difference_max_abs": 0.0,
            "reference_square_sum": 0.0,
            "candidate_square_sum": 0.0,
            "dot": 0.0,
        }
    )


def add_gradient_error(
    values: dict, reference: torch.Tensor, candidate: torch.Tensor
) -> None:
    reference = reference.reshape(-1)
    candidate = candidate.reshape(-1)
    difference = candidate - reference
    values["elements"] += reference.numel()
    values["reference_abs_sum"] += float(reference.abs().sum())
    values["difference_abs_sum"] += float(difference.abs().sum())
    values["difference_max_abs"] = max(
        values["difference_max_abs"], float(difference.abs().max())
    )
    values["reference_square_sum"] += float(torch.dot(reference, reference))
    values["candidate_square_sum"] += float(torch.dot(candidate, candidate))
    values["dot"] += float(torch.dot(reference, candidate))


def finish_gradient_error(values: dict) -> dict[str, float | int]:
    reference_norm = math.sqrt(values["reference_square_sum"])
    candidate_norm = math.sqrt(values["candidate_square_sum"])
    mean_abs = values["difference_abs_sum"] / values["elements"]
    reference_mean_abs = values["reference_abs_sum"] / values["elements"]
    return {
        "elements": values["elements"],
        "mean_abs": mean_abs,
        "max_abs": values["difference_max_abs"],
        "relative_mean": mean_abs / max(reference_mean_abs, 1e-30),
        "cosine": values["dot"] / max(reference_norm * candidate_norm, 1e-30),
        "reference_norm": reference_norm,
        "candidate_norm": candidate_norm,
    }


def main() -> None:
    args = parser().parse_args()
    if args.sequence_length < 2 or args.eval_batches < 1 or args.sample_stride < 1:
        raise ValueError("Invalid sequence length, batch count, or sample stride")
    if not torch.cuda.is_available() or torch.version.hip is None:
        raise RuntimeError("This validator requires a PyTorch ROCm device")

    model_path = args.model.expanduser().resolve()
    corpus = args.corpus.expanduser().resolve()
    manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    validation = np.memmap(
        corpus / manifest["splits"]["validation"]["path"], dtype="<u2", mode="r"
    )
    required = args.eval_batches * args.sequence_length + 1
    if len(validation) < required:
        raise RuntimeError(
            f"Validation stream has {len(validation)} tokens; need {required}"
        )

    enable_rocm_triton_ssd(args.mamba_root)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, dtype=torch.float32, local_files_only=True
    ).to("cuda")
    model.train()

    policies = (
        ("bfloat16", torch.bfloat16, None),
        ("float16_bfloat16_scan", torch.float16, torch.bfloat16),
    )
    baseline_gradients: dict[str, torch.Tensor] = {}
    baseline_logits = baseline_top1 = None
    runs: dict[str, dict] = {}

    for label, compute_dtype, scan_dtype in policies:
        kernel = enable_rocm_triton_ssd(args.mamba_root, scan_dtype=scan_dtype)
        model.zero_grad(set_to_none=True)
        losses: list[float] = []
        accuracies: list[float] = []
        sampled_logits: list[torch.Tensor] = []
        top1: list[torch.Tensor] = []
        activation_sums = [0.0] * len(model.model.layers)
        activation_maxima = [0.0] * len(model.model.layers)
        activation_counts = [0] * len(model.model.layers)

        def activation_hook(
            index: int,
            sums: list[float] = activation_sums,
            maxima: list[float] = activation_maxima,
            counts: list[int] = activation_counts,
        ):
            def collect(_module, _inputs, output):
                value = output[0] if isinstance(output, tuple) else output
                detached = value.detach().float()
                sums[index] += float((detached * detached).sum())
                maxima[index] = max(maxima[index], float(detached.abs().max()))
                counts[index] += detached.numel()

            return collect

        hooks = [
            layer.mamba.register_forward_hook(activation_hook(index))
            for index, layer in enumerate(model.model.layers)
        ]
        torch.cuda.synchronize()
        started = time.perf_counter()
        finite = True
        for index in range(args.eval_batches):
            start = index * args.sequence_length
            array = np.asarray(
                validation[start : start + args.sequence_length + 1], dtype=np.int64
            )
            tokens = torch.from_numpy(array.copy()).unsqueeze(0).to("cuda")
            labels = tokens[:, 1:]
            with torch.autocast("cuda", dtype=compute_dtype):
                logits = model(input_ids=tokens[:, :-1], use_cache=False).logits
                loss = functional.cross_entropy(
                    logits.float().reshape(-1, logits.shape[-1]), labels.reshape(-1)
                )
            finite = (
                finite
                and bool(torch.isfinite(logits).all())
                and bool(torch.isfinite(loss))
            )
            (loss / args.eval_batches).backward()
            losses.append(float(loss.detach()))
            accuracies.append(
                float((logits.detach().argmax(-1) == labels).float().mean())
            )
            sampled_logits.append(
                logits.detach()[0, :: args.sample_stride].float().cpu()
            )
            top1.append(logits.detach().argmax(-1).cpu())
        torch.cuda.synchronize()
        seconds = time.perf_counter() - started
        for hook in hooks:
            hook.remove()

        finite = finite and all(
            bool(torch.isfinite(parameter.grad).all())
            for parameter in model.parameters()
            if parameter.grad is not None
        )
        combined_logits = torch.cat(sampled_logits)
        combined_top1 = torch.cat(top1, dim=1)
        run = {
            "kernel": kernel,
            "compute_dtype": str(compute_dtype),
            "finite": finite,
            "seconds_with_diagnostic_hooks": seconds,
            "losses": losses,
            "mean_loss": sum(losses) / len(losses),
            "mean_accuracy": sum(accuracies) / len(accuracies),
            "mamba_activation_rms": [
                math.sqrt(total / count)
                for total, count in zip(activation_sums, activation_counts, strict=True)
            ],
            "mamba_activation_max_abs": activation_maxima,
        }
        if label == "bfloat16":
            baseline_gradients = {
                name: parameter.grad.detach().float().cpu().clone()
                for name, parameter in model.named_parameters()
                if parameter.grad is not None
            }
            baseline_logits = combined_logits
            baseline_top1 = combined_top1
        else:
            assert baseline_logits is not None and baseline_top1 is not None
            run["sampled_logit_error"] = tensor_error(baseline_logits, combined_logits)
            run["top1_agreement"] = float(
                (baseline_top1 == combined_top1).float().mean()
            )
            accumulators = gradient_error_accumulators()
            for name, parameter in model.named_parameters():
                if name not in baseline_gradients or parameter.grad is None:
                    continue
                candidate = parameter.grad.detach().float().cpu()
                add_gradient_error(
                    accumulators["all"], baseline_gradients[name], candidate
                )
                add_gradient_error(
                    accumulators[parameter_group(name)],
                    baseline_gradients[name],
                    candidate,
                )
            run["gradient_error"] = finish_gradient_error(accumulators.pop("all"))
            run["gradient_group_errors"] = {
                group: finish_gradient_error(values)
                for group, values in sorted(accumulators.items())
            }
        runs[label] = run

    baseline = runs["bfloat16"]
    mixed = runs["float16_bfloat16_scan"]
    loss_delta = mixed["mean_loss"] - baseline["mean_loss"]
    group_cosines = [
        value["cosine"] for value in mixed["gradient_group_errors"].values()
    ]
    checks = {
        "finite": baseline["finite"] and mixed["finite"],
        "loss_delta": abs(loss_delta) <= args.max_loss_delta,
        "sampled_logits": (
            mixed["sampled_logit_error"]["relative_mean"]
            <= args.max_logit_relative_mean
        ),
        "top1": mixed["top1_agreement"] >= args.min_top1_agreement,
        "gradient": mixed["gradient_error"]["cosine"] >= args.min_gradient_cosine,
        "gradient_groups": min(group_cosines) >= args.min_group_gradient_cosine,
    }
    result = {
        "schema_version": 1,
        "torch": torch.__version__,
        "hip": torch.version.hip,
        "device": torch.cuda.get_device_name(0),
        "model": str(model_path),
        "corpus": str(corpus),
        "sequence_length": args.sequence_length,
        "eval_batches": args.eval_batches,
        "thresholds": {
            "max_loss_delta": args.max_loss_delta,
            "max_logit_relative_mean": args.max_logit_relative_mean,
            "min_top1_agreement": args.min_top1_agreement,
            "min_gradient_cosine": args.min_gradient_cosine,
            "min_group_gradient_cosine": args.min_group_gradient_cosine,
        },
        "loss_delta": loss_delta,
        "checks": checks,
        "ok": all(checks.values()),
        "runs": runs,
    }
    if args.output is not None:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        temporary.replace(output)
    print(json.dumps(result, indent=2))
    if not result["ok"]:
        raise RuntimeError("Mixed compute policy failed one or more numerical gates")


if __name__ == "__main__":
    main()
