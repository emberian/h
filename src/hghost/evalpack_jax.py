"""JAX worker for ``hghost-evalpack``: per-token causal losses of a Falcon-H1 checkpoint.

This module is executed inside the h1jax virtualenv (``.venv-jax``), which has JAX and
h1jax but not the rest of ``hghost``; it therefore imports nothing else from the package.
Input is a ``.npy`` int32 array of token rows ``[N, L + 1]``; output is a ``.npz`` with the
per-token loss ``[N, L]`` (float32, natural log) and next-token correctness ``[N, L]`` in
the same row order, plus a JSON sidecar describing the run.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from collections.abc import Callable
from pathlib import Path

import numpy as np


def loss_function(cfg, compute_dtype) -> Callable:
    """JIT-compiled ``(params, rows) -> (losses, correct)`` for rows ``[B, L + 1]``."""
    import jax
    import jax.numpy as jnp
    from h1jax.model import falcon_h1_forward

    @jax.jit
    def per_token(params, rows):
        logits = falcon_h1_forward(
            params,
            rows[:, :-1],
            cfg,
            compute_dtype=compute_dtype,
            gradient_checkpointing=False,
            layer_scan=True,
        ).astype(jnp.float32)
        labels = rows[:, 1:]
        log_normalizer = jax.nn.logsumexp(logits, axis=-1)
        selected = jnp.take_along_axis(logits, labels[..., None], axis=-1)[..., 0]
        return log_normalizer - selected, jnp.argmax(logits, axis=-1) == labels

    return per_token


def per_token_losses(
    params,
    cfg,
    rows: np.ndarray,
    *,
    batch_size: int = 8,
    compute_dtype=None,
    progress: Callable[[int, int], None] | None = None,
    function: Callable | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Per-token losses and correctness for every row, batched with a fixed shape.

    The last partial batch is padded with copies of its first row so that only one XLA
    program is compiled; the padding rows are dropped from the result. Pass a prebuilt
    ``function`` from :func:`loss_function` to reuse one compilation across calls.
    """
    import jax.numpy as jnp

    compute_dtype = jnp.float32 if compute_dtype is None else compute_dtype
    rows = np.ascontiguousarray(rows, dtype=np.int32)
    if rows.ndim != 2 or rows.shape[1] < 2:
        raise ValueError("rows must have shape [N, L + 1] with L >= 1")
    count = rows.shape[0]
    if function is None:
        function = loss_function(cfg, compute_dtype)
    losses = np.empty((count, rows.shape[1] - 1), dtype=np.float32)
    correct = np.empty((count, rows.shape[1] - 1), dtype=bool)
    for start in range(0, count, batch_size):
        batch = rows[start : start + batch_size]
        actual = batch.shape[0]
        if actual < batch_size:
            batch = np.concatenate(
                [batch, np.repeat(batch[:1], batch_size - actual, axis=0)], axis=0
            )
        batch_losses, batch_correct = function(params, jnp.asarray(batch))
        losses[start : start + actual] = np.asarray(batch_losses)[:actual]
        correct[start : start + actual] = np.asarray(batch_correct)[:actual]
        if progress is not None:
            progress(start + actual, count)
    return losses, correct


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument(
        "--rows", type=Path, required=True, help=".npy int32 [N, L + 1]"
    )
    parser.add_argument("--output", type=Path, required=True, help=".npz destination")
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--dtype", choices=("float32", "bfloat16"), default="float32")
    parser.add_argument(
        "--slab",
        type=int,
        default=64,
        help="rows between partial saves; a killed run resumes from the last slab",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    import jax
    import jax.numpy as jnp
    from h1jax.checkpoint import load_hf_params
    from h1jax.config import FalconH1Config

    started = time.perf_counter()
    cfg = FalconH1Config.from_json(args.checkpoint / "config.json")
    params = load_hf_params(args.checkpoint, dtype=jnp.float32)
    rows = np.load(args.rows)
    load_seconds = time.perf_counter() - started

    def progress(done: int, total: int) -> None:
        elapsed = time.perf_counter() - started
        print(
            f"[evalpack-jax] {done}/{total} rows, {elapsed:.0f}s",
            file=sys.stderr,
            flush=True,
        )

    compute_dtype = jnp.float32 if args.dtype == "float32" else jnp.bfloat16
    args.output.parent.mkdir(parents=True, exist_ok=True)
    partial = args.output.with_suffix(".partial.npz")
    count, width = rows.shape[0], rows.shape[1] - 1
    losses = np.zeros((count, width), dtype=np.float32)
    correct = np.zeros((count, width), dtype=bool)
    done = 0
    if partial.is_file():
        stored = np.load(partial)
        if stored["losses"].shape == losses.shape and stored["dtype"] == args.dtype:
            done = int(stored["done"])
            losses[:done] = stored["losses"][:done]
            correct[:done] = stored["correct"][:done]
            print(f"[evalpack-jax] resuming after {done} rows", file=sys.stderr)
    function = loss_function(cfg, compute_dtype)
    slab = max(args.batch, args.slab)
    while done < count:
        stop = min(count, done + slab)
        losses[done:stop], correct[done:stop] = per_token_losses(
            params,
            cfg,
            rows[done:stop],
            batch_size=args.batch,
            compute_dtype=compute_dtype,
            function=function,
        )
        done = stop
        np.savez(partial, losses=losses, correct=correct, done=done, dtype=args.dtype)
        progress(done, count)
    np.savez(args.output, losses=losses, correct=correct)
    partial.unlink(missing_ok=True)
    meta = {
        "checkpoint": str(args.checkpoint.resolve()),
        "rows": int(rows.shape[0]),
        "sequence_length": int(rows.shape[1] - 1),
        "batch": args.batch,
        "compute_dtype": args.dtype,
        "parameter_dtype": "float32",
        "jax_version": jax.__version__,
        "devices": [str(device) for device in jax.devices()],
        "python": platform.python_version(),
        "load_seconds": round(load_seconds, 3),
        "seconds": round(time.perf_counter() - started, 3),
    }
    args.output.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
