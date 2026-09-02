"""Library-likeness judge: per-text loss under a library-trained checkpoint minus loss under base.

usage: judge.py --base DIR --model DIR [--model DIR ...] (--texts FILE.jsonl | --room FILE.jsonl) [--field completion]
Reads texts (one JSON object per line; `--field` names the text field, default `completion`) and prints,
per text, the mean next-token NLL under each model and the delta versus base; negative delta = more
library-like. Runs h1jax on CPU in float32 (the same code path as the evaluation pack).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("JAX_PLATFORM_NAME", "cpu")
os.environ.setdefault("H1JAX_SSD", "v2")

import jax
import jax.numpy as jnp
import numpy as np
from h1jax.checkpoint import load_hf_params
from h1jax.config import FalconH1Config
from h1jax.model import falcon_h1_forward
from tokenizers import Tokenizer

BOS_PREFIX = "\n"  # score each text as a fresh document after a newline


def nll_per_text(params, cfg, ids: list[list[int]], length: int) -> list[float]:
    """Mean next-token NLL per text; inputs padded to one fixed length so the model compiles once."""
    forward = jax.jit(
        lambda p, t: falcon_h1_forward(p, t, cfg, compute_dtype=jnp.float32, layer_scan=True)
    )
    out = []
    for seq in ids:
        seq = seq[: length + 1]
        padded = np.zeros((1, length + 1), dtype=np.int32)
        padded[0, : len(seq)] = seq
        valid = np.zeros((1, length), dtype=np.float32)
        valid[0, : len(seq) - 1] = 1.0
        tokens = jnp.asarray(padded)
        logits = forward(params, tokens[:, :-1]).astype(jnp.float32)
        labels = tokens[:, 1:]
        logz = jax.nn.logsumexp(logits, axis=-1)
        sel = jnp.take_along_axis(logits, labels[..., None], axis=-1)[..., 0]
        nll = (logz - sel) * jnp.asarray(valid)
        out.append(float(jnp.sum(nll) / jnp.sum(jnp.asarray(valid))))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--model", type=Path, action="append", required=True)
    ap.add_argument("--texts", type=Path, required=True)
    ap.add_argument("--field", default="completion")
    ap.add_argument("--tokenizer", type=Path, default=Path("kaggle/base_model_dataset_public/tokenizer.json"))
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    tok = Tokenizer.from_file(str(args.tokenizer))
    rows = [json.loads(l) for l in args.texts.read_text().splitlines() if l.strip()]
    texts = [str(r.get(args.field, "")) for r in rows]
    ids = [tok.encode(BOS_PREFIX + t).ids[: args.max_tokens] for t in texts]
    keep = [i for i, s in enumerate(ids) if len(s) >= 3]
    results = {}
    for name, path in [("base", args.base)] + [(p.name, p) for p in args.model]:
        cfg = FalconH1Config.from_json(path / "config.json")
        params = load_hf_params(path, dtype=jnp.float32)
        results[name] = nll_per_text(params, cfg, [ids[i] for i in keep], args.max_tokens)
        del params
    names = [n for n in results if n != "base"]
    print("| # | " + " | ".join(["base"] + [f"{n} (Δ)" for n in names]) + " | text |")
    print("|---:|" + "---:|" * (1 + len(names)) + "---|")
    out_rows = []
    for j, i in enumerate(keep):
        b = results["base"][j]
        cells = [f"{b:.3f}"] + [f"{results[n][j]:.3f} ({results[n][j]-b:+.3f})" for n in names]
        print(f"| {i} | " + " | ".join(cells) + " | " + texts[i][:90].replace("|", "/").replace("\n", " ") + " |")
        out_rows.append({"index": i, "text": texts[i], "base": b, **{n: results[n][j] for n in names}})
    means = {n: float(np.mean(results[n])) for n in results}
    print("means:", {n: round(v, 4) for n, v in means.items()},
          "deltas:", {n: round(means[n] - means["base"], 4) for n in names})
    if args.output:
        args.output.write_text("".join(json.dumps(r) + "\n" for r in out_rows))


if __name__ == "__main__":
    main()
