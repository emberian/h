from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import jax
import jax.numpy as jnp
from safetensors import safe_open
from safetensors.flax import save_file

from .config import FalconH1Config


def _checkpoint_files(root: Path) -> list[Path]:
    single = root / "model.safetensors"
    if single.exists():
        return [single]
    index = root / "model.safetensors.index.json"
    if index.exists():
        values = json.loads(index.read_text(encoding="utf-8"))
        return [root / name for name in sorted(set(values["weight_map"].values()))]
    files = sorted(root.glob("*.safetensors"))
    if not files:
        raise FileNotFoundError(f"No safetensors checkpoint found in {root}")
    return files


def load_hf_params(
    checkpoint: str | Path,
    *,
    dtype: jnp.dtype = jnp.float32,
) -> dict[str, jax.Array]:
    """Load Hugging Face tensors without importing PyTorch or changing layout."""

    root = Path(checkpoint).expanduser().resolve()
    params: dict[str, jax.Array] = {}
    for path in _checkpoint_files(root):
        with safe_open(path, framework="flax") as handle:
            for key in handle.keys():
                if key in params:
                    raise ValueError(f"Duplicate checkpoint tensor: {key}")
                params[key] = jnp.asarray(handle.get_tensor(key), dtype=dtype)
    return params


def save_hf_params(
    params: dict[str, Any],
    output: str | Path,
    *,
    dtype: jnp.dtype | None = None,
    metadata: dict[str, str] | None = None,
) -> Path:
    """Atomically save a single-file Hugging Face-compatible safetensors file."""

    root = Path(output).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = root / "model.safetensors"
    temporary = root / ".model.safetensors.tmp"
    host = jax.device_get(params)
    if dtype is not None:
        host = jax.tree_util.tree_map(lambda value: jnp.asarray(value, dtype=dtype), host)
    save_file(host, str(temporary), metadata=metadata or {"format": "pt"})
    os.replace(temporary, path)
    return path


def write_hf_config(cfg: FalconH1Config, output: str | Path, *, dtype: str = "float32") -> Path:
    root = Path(output).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    values = cfg.to_dict()
    values.update(
        {
            "architectures": ["FalconH1ForCausalLM"],
            "model_type": "falcon_h1",
            "dtype": dtype,
            "expansion_factor": cfg.mamba_d_ssm / cfg.hidden_size,
            "mamba_expand": cfg.mamba_d_ssm / cfg.hidden_size,
            "use_cache": True,
        }
    )
    path = root / "config.json"
    path.write_text(json.dumps(values, indent=2) + "\n", encoding="utf-8")
    return path

