from __future__ import annotations

import argparse
import json
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

from .checkpoint import load_hf_params
from .config import FalconH1Config
from .model import falcon_h1_forward


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare JAX logits with a saved PyTorch reference")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--tokens", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--atol", type=float, default=2e-4)
    parser.add_argument("--rtol", type=float, default=2e-4)
    args = parser.parse_args()
    cfg = FalconH1Config.from_json(args.checkpoint / "config.json")
    params = load_hf_params(args.checkpoint, dtype=jnp.float32)
    tokens = np.load(args.tokens).astype(np.int32)
    reference = np.load(args.reference)["logits"].astype(np.float32)
    forward = jax.jit(
        lambda p, t: falcon_h1_forward(
            p, t, cfg, compute_dtype=jnp.float32, gradient_checkpointing=False
        )
    )
    actual = np.asarray(forward(params, tokens), dtype=np.float32)
    difference = np.abs(actual - reference)
    report = {
        "shape": list(actual.shape),
        "max_absolute_error": float(difference.max()),
        "mean_absolute_error": float(difference.mean()),
        "allclose": bool(np.allclose(actual, reference, atol=args.atol, rtol=args.rtol)),
    }
    print(json.dumps(report, indent=2))
    if not report["allclose"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
