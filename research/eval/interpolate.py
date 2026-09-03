"""WiSE-FT style weight interpolation: theta = (1-alpha) * base + alpha * tuned, written as an HF checkpoint dir
(config/tokenizer copied from the tuned checkpoint). usage: interpolate.py <base dir> <tuned dir> <out root> <alpha ...>"""
import shutil, sys
from pathlib import Path
import jax.numpy as jnp
from safetensors.flax import load_file, save_file

base, tuned, out_root = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
alphas = [float(a) for a in sys.argv[4:]]
b = load_file(str(base / "model.safetensors")); t = load_file(str(tuned / "model.safetensors"))
assert set(b) == set(t), "tensor names differ"
for alpha in alphas:
    out = out_root / f"alpha{alpha:.2f}"; out.mkdir(parents=True, exist_ok=True)
    mixed = {}
    for k in t:
        tb, tt = b[k].astype(jnp.float32), t[k].astype(jnp.float32)
        mixed[k] = ((1 - alpha) * tb + alpha * tt).astype(t[k].dtype)
    save_file(mixed, str(out / "model.safetensors"), metadata={"format": "pt"})
    for name in ("config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"):
        if (tuned / name).exists(): shutil.copy(tuned / name, out / name)
    print("wrote", out, "alpha", alpha, "dtype", next(iter(mixed.values())).dtype)
