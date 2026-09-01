from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import tempfile
import time
from functools import partial
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import optax
from flax import serialization

from .checkpoint import load_hf_params, save_hf_params, write_hf_config
from .config import FalconH1Config
from .data import TokenStream, ValidationStream
from .model import causal_lm_loss, count_parameters, init_params


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train Falcon-H1 with JAX on one host's TPU devices")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--train-bin", type=Path, required=True)
    parser.add_argument("--validation-bin", type=Path)
    parser.add_argument("--checkpoint", type=Path, help="HF safetensors directory for continued pretraining")
    parser.add_argument("--random-init", action="store_true")
    parser.add_argument("--resume", type=Path)
    parser.add_argument(
        "--tokenizer-dir",
        type=Path,
        help="copy HF tokenizer assets into every saved checkpoint",
    )
    parser.add_argument("--output", type=Path, default=Path("/kaggle/working/h1-output"))
    parser.add_argument("--sequence-length", type=int, default=512)
    parser.add_argument("--per-device-batch", type=int, default=1)
    parser.add_argument("--accumulation-steps", type=int, default=1)
    parser.add_argument("--total-tokens", type=int, default=10_000_000)
    parser.add_argument("--warmup-tokens", type=int, default=1_000_000)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--min-learning-rate-ratio", type=float, default=0.1)
    parser.add_argument("--weight-decay", type=float, default=0.1)
    parser.add_argument("--max-gradient-norm", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--dtype", choices=("bfloat16", "float32"), default="bfloat16")
    parser.add_argument(
        "--gradient-checkpointing",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="rematerialize every decoder layer to reduce activation memory",
    )
    parser.add_argument("--save-tokens", default="10000000,30000000,100000000,300000000")
    parser.add_argument(
        "--save-final-checkpoint",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="always include a checkpoint at total-tokens",
    )
    parser.add_argument("--eval-every-tokens", type=int, default=10_000_000)
    parser.add_argument("--eval-batches", type=int, default=8)
    parser.add_argument("--log-steps", type=int, default=10)
    return parser


def _parse_thresholds(raw: str, maximum: int) -> list[int]:
    values = sorted({int(value) for value in raw.split(",") if value.strip()})
    return [value for value in values if 0 < value <= maximum]


def _first_local_shard(tree):
    return jax.tree_util.tree_map(
        lambda value: value.addressable_shards[0].data.squeeze(0), tree
    )


_TOKENIZER_FILES = (
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "generation_config.json",
)


def _atomic_write_json(path: Path, value: dict) -> None:
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


def _validate_args(args: argparse.Namespace) -> None:
    sources = sum((args.checkpoint is not None, bool(args.random_init), args.resume is not None))
    if sources != 1:
        raise ValueError("Choose exactly one of --checkpoint, --random-init, or --resume")
    for name in (
        "sequence_length",
        "per_device_batch",
        "accumulation_steps",
        "total_tokens",
        "warmup_tokens",
        "eval_every_tokens",
        "eval_batches",
        "log_steps",
    ):
        if int(getattr(args, name)) < 1:
            raise ValueError(f"--{name.replace('_', '-')} must be positive")
    if not 0.0 <= args.min_learning_rate_ratio <= 1.0:
        raise ValueError("--min-learning-rate-ratio must be between zero and one")
    if args.learning_rate <= 0 or args.weight_decay < 0 or args.max_gradient_norm <= 0:
        raise ValueError("Learning rate and gradient norm must be positive; weight decay cannot be negative")
    for name in ("config", "train_bin"):
        path = Path(getattr(args, name)).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
    if args.validation_bin is not None and not args.validation_bin.expanduser().resolve().is_file():
        raise FileNotFoundError(args.validation_bin)
    if args.tokenizer_dir is not None:
        tokenizer_dir = args.tokenizer_dir.expanduser().resolve()
        if not (tokenizer_dir / "tokenizer.json").is_file():
            raise FileNotFoundError(tokenizer_dir / "tokenizer.json")


def _resume_compatibility(state: dict, expected: dict) -> None:
    mismatches = {
        key: (state.get(key), value)
        for key, value in expected.items()
        if state.get(key) != value
    }
    if mismatches:
        raise ValueError(f"Resume settings do not match checkpoint: {mismatches}")


def _save_training_checkpoint(
    root: Path,
    params,
    optimizer_state,
    cfg: FalconH1Config,
    metadata: dict,
    tokenizer_dir: Path | None = None,
) -> None:
    root.parent.mkdir(parents=True, exist_ok=True)
    if root.exists():
        raise FileExistsError(f"Refusing to overwrite checkpoint: {root}")
    staging = Path(tempfile.mkdtemp(prefix=f".{root.name}.", dir=root.parent))
    host_params = jax.device_get(params)
    host_optimizer = jax.device_get(optimizer_state)
    try:
        save_hf_params(host_params, staging, dtype=jnp.float32)
        write_hf_config(cfg, staging, dtype="float32")
        optimizer_path = staging / "optimizer.msgpack"
        with optimizer_path.open("wb") as stream:
            stream.write(serialization.to_bytes(host_optimizer))
            stream.flush()
            os.fsync(stream.fileno())
        _atomic_write_json(staging / "trainer_state.json", metadata)
        if tokenizer_dir is not None:
            for name in _TOKENIZER_FILES:
                source = tokenizer_dir / name
                if source.is_file():
                    shutil.copy2(source, staging / name)
        os.replace(staging, root)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def run(args: argparse.Namespace) -> None:
    _validate_args(args)
    cfg = FalconH1Config.from_json(args.config)
    devices = jax.local_devices()
    device_count = len(devices)
    if device_count < 1:
        raise RuntimeError("JAX reported no local devices")
    compute_dtype = jnp.bfloat16 if args.dtype == "bfloat16" else jnp.float32
    tokens_per_step = (
        device_count * args.accumulation_steps * args.per_device_batch * args.sequence_length
    )
    total_steps = math.ceil(args.total_tokens / tokens_per_step)
    warmup_steps = max(1, math.ceil(args.warmup_tokens / tokens_per_step))
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=args.learning_rate,
        warmup_steps=min(warmup_steps, total_steps),
        decay_steps=max(total_steps, warmup_steps + 1),
        end_value=args.learning_rate * args.min_learning_rate_ratio,
    )

    resume_settings = {
        "sequence_length": args.sequence_length,
        "per_device_batch": args.per_device_batch,
        "accumulation_steps": args.accumulation_steps,
        "tokens_per_step": tokens_per_step,
        "run_batch_aligned_tokens": total_steps * tokens_per_step,
        "batch_alignment_overhead_tokens": total_steps * tokens_per_step
        - args.total_tokens,
        "seed": args.seed,
        "total_tokens": args.total_tokens,
        "warmup_tokens": args.warmup_tokens,
        "learning_rate": args.learning_rate,
        "min_learning_rate_ratio": args.min_learning_rate_ratio,
        "weight_decay": args.weight_decay,
        "max_gradient_norm": args.max_gradient_norm,
        "gradient_checkpointing": args.gradient_checkpointing,
    }
    if args.resume is not None:
        params = load_hf_params(args.resume, dtype=jnp.float32)
        state = json.loads((args.resume / "trainer_state.json").read_text(encoding="utf-8"))
        _resume_compatibility(state, resume_settings)
        start_step = int(state["step"])
    elif args.checkpoint is not None:
        params = load_hf_params(args.checkpoint, dtype=jnp.float32)
        start_step = 0
    else:
        params = init_params(cfg, args.seed)
        start_step = 0
    parameter_count = count_parameters(params)
    if start_step < 0 or start_step > total_steps:
        raise ValueError(f"Resume step {start_step} is outside this {total_steps}-step run")

    decay_mask = {key: value.ndim >= 2 for key, value in params.items()}
    optimizer = optax.chain(
        optax.clip_by_global_norm(args.max_gradient_norm),
        optax.adamw(
            learning_rate=schedule,
            b1=0.9,
            b2=0.95,
            eps=1e-8,
            weight_decay=args.weight_decay,
            mask=decay_mask,
        ),
    )
    optimizer_state = optimizer.init(params)
    if args.resume is not None:
        optimizer_state = serialization.from_bytes(
            optimizer_state, (args.resume / "optimizer.msgpack").read_bytes()
        )

    def micro_loss(current_params, micro_batch):
        return causal_lm_loss(
            current_params,
            micro_batch,
            cfg,
            compute_dtype=compute_dtype,
            gradient_checkpointing=args.gradient_checkpointing,
        )

    @partial(
        jax.pmap,
        axis_name="data",
        in_axes=(None, None, 0),
        out_axes=(None, None, 0),
        donate_argnums=(0, 1),
    )
    def train_step(current_params, current_optimizer, batch):
        zero_grads = jax.tree_util.tree_map(jnp.zeros_like, current_params)
        zero_metrics = {"loss": jnp.array(0.0), "accuracy": jnp.array(0.0)}

        def accumulate(index, carry):
            gradient_sum, metric_sum = carry
            (_, metrics), gradients = jax.value_and_grad(micro_loss, has_aux=True)(
                current_params, batch[index]
            )
            gradient_sum = jax.tree_util.tree_map(jnp.add, gradient_sum, gradients)
            metric_sum = jax.tree_util.tree_map(jnp.add, metric_sum, metrics)
            return gradient_sum, metric_sum

        gradients, metrics = jax.lax.fori_loop(
            0, batch.shape[0], accumulate, (zero_grads, zero_metrics)
        )
        divisor = jnp.asarray(batch.shape[0], jnp.float32)
        gradients = jax.tree_util.tree_map(lambda value: value / divisor, gradients)
        metrics = jax.tree_util.tree_map(lambda value: value / divisor, metrics)
        gradients = jax.lax.pmean(gradients, "data")
        metrics = jax.lax.pmean(metrics, "data")
        updates, new_optimizer = optimizer.update(gradients, current_optimizer, current_params)
        new_params = optax.apply_updates(current_params, updates)
        metrics["gradient_norm"] = optax.tree.norm(gradients)
        return new_params, new_optimizer, metrics

    @partial(jax.pmap, axis_name="data", in_axes=(None, 0), out_axes=0)
    def eval_step(current_params, batch):
        _, metrics = causal_lm_loss(
            current_params,
            batch,
            cfg,
            compute_dtype=compute_dtype,
            gradient_checkpointing=False,
        )
        return jax.lax.pmean(metrics, "data")

    train_data = TokenStream(args.train_bin, args.sequence_length, args.seed)
    validation = (
        ValidationStream(args.validation_bin, args.sequence_length)
        if args.validation_bin is not None
        else None
    )
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    start_tokens = min(start_step * tokens_per_step, args.total_tokens)
    save_threshold_set = set(_parse_thresholds(args.save_tokens, args.total_tokens))
    if args.save_final_checkpoint:
        save_threshold_set.add(args.total_tokens)
    save_thresholds = sorted(save_threshold_set)
    save_thresholds = [threshold for threshold in save_thresholds if threshold > start_tokens]
    next_eval = (
        (start_tokens // args.eval_every_tokens + 1) * args.eval_every_tokens
        if validation is not None
        else math.inf
    )
    examples_per_step = device_count * args.accumulation_steps * args.per_device_batch
    run_manifest = {
        "schema_version": 1,
        "config": cfg.to_dict(),
        "parameters": parameter_count,
        "devices": [str(device) for device in devices],
        **resume_settings,
        "dtype": args.dtype,
        "train_bin": str(args.train_bin.expanduser().resolve()),
        "validation_bin": (
            str(args.validation_bin.expanduser().resolve())
            if args.validation_bin is not None
            else None
        ),
        "start_step": start_step,
        "start_tokens": start_tokens,
        "save_thresholds": save_thresholds,
        "save_final_checkpoint": args.save_final_checkpoint,
        "eval_every_tokens": args.eval_every_tokens,
        "eval_batches": args.eval_batches,
    }
    _atomic_write_json(output / "run-manifest.json", run_manifest)
    started = time.monotonic()
    interval_started = started
    interval_tokens = 0
    print(
        json.dumps(
            {
                "event": "start",
                "devices": [str(device) for device in devices],
                "parameters": parameter_count,
                "tokens_per_step": tokens_per_step,
                "total_steps": total_steps,
                "start_step": start_step,
            }
        ),
        flush=True,
    )

    for step in range(start_step, total_steps):
        batch = train_data.batch(
            step * examples_per_step,
            device_count=device_count,
            accumulation_steps=args.accumulation_steps,
            per_device_batch=args.per_device_batch,
        )
        params, optimizer_state, metrics = train_step(params, optimizer_state, batch)
        jax.block_until_ready(metrics)
        exposed_tokens = min((step + 1) * tokens_per_step, args.total_tokens)
        interval_tokens += tokens_per_step
        if (step + 1) % args.log_steps == 0 or step == start_step:
            now = time.monotonic()
            host_metrics = jax.device_get(_first_local_shard(metrics))
            if not all(
                math.isfinite(float(host_metrics[key]))
                for key in ("loss", "accuracy", "gradient_norm")
            ):
                raise FloatingPointError(f"Non-finite training metrics at step {step + 1}")
            print(
                json.dumps(
                    {
                        "event": "train",
                        "step": step + 1,
                        "tokens": exposed_tokens,
                        "loss": float(host_metrics["loss"]),
                        "accuracy": float(host_metrics["accuracy"]),
                        "gradient_norm": float(host_metrics["gradient_norm"]),
                        "learning_rate": float(schedule(step)),
                        "tokens_per_second": interval_tokens / (now - interval_started),
                    }
                ),
                flush=True,
            )
            interval_started, interval_tokens = now, 0

        if validation is not None and exposed_tokens >= next_eval:
            totals = {"loss": 0.0, "accuracy": 0.0}
            for eval_index in range(args.eval_batches):
                eval_batch = validation.batch(
                    eval_index * device_count * args.per_device_batch,
                    device_count=device_count,
                    accumulation_steps=1,
                    per_device_batch=args.per_device_batch,
                )[:, 0]
                eval_metrics = jax.device_get(_first_local_shard(eval_step(params, eval_batch)))
                for key in totals:
                    value = float(eval_metrics[key])
                    if not math.isfinite(value):
                        raise FloatingPointError(
                            f"Non-finite validation metric {key} at step {step + 1}"
                        )
                    totals[key] += value
            print(
                json.dumps(
                    {
                        "event": "validation",
                        "step": step + 1,
                        "tokens": exposed_tokens,
                        **{key: value / args.eval_batches for key, value in totals.items()},
                    }
                ),
                flush=True,
            )
            next_eval += args.eval_every_tokens

        while save_thresholds and exposed_tokens >= save_thresholds[0]:
            threshold = save_thresholds.pop(0)
            checkpoint = output / f"tokens-{threshold:012d}"
            _save_training_checkpoint(
                checkpoint,
                params,
                optimizer_state,
                cfg,
                {
                    **resume_settings,
                    "step": step + 1,
                    "tokens": exposed_tokens,
                    "batch_aligned_tokens": (step + 1) * tokens_per_step,
                    "requested_token_threshold": threshold,
                    "tokens_per_step": tokens_per_step,
                    "parameters": parameter_count,
                    "elapsed_seconds": time.monotonic() - started,
                },
                tokenizer_dir=(
                    args.tokenizer_dir.expanduser().resolve()
                    if args.tokenizer_dir is not None
                    else None
                ),
            )
            print(json.dumps({"event": "checkpoint", "path": str(checkpoint)}), flush=True)

    _atomic_write_json(
        output / "training-complete.json",
        {
            "completed": True,
            "steps": total_steps,
            "tokens": args.total_tokens,
            "tokens_per_step": tokens_per_step,
            "batch_aligned_tokens": total_steps * tokens_per_step,
            "batch_alignment_overhead_tokens": total_steps * tokens_per_step
            - args.total_tokens,
            "elapsed_seconds": time.monotonic() - started,
        },
    )


def main() -> None:
    run(build_parser().parse_args())


if __name__ == "__main__":
    main()
