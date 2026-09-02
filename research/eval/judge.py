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

import sys

import jax.numpy as jnp
import numpy as np
from h1jax.checkpoint import load_hf_params
from h1jax.config import FalconH1Config
from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from hghost.evalpack_jax import per_token_losses  # the one h1jax forward shared with evalpack and roombank

BOS_PREFIX = "\n"  # score each text as a fresh document after a newline


def nll_per_text(params, cfg, ids: list[list[int]], length: int, batch_size: int = 8) -> list[float]:
    """Mean next-token NLL per text; inputs padded to one fixed length so the model compiles once."""
    rows = np.zeros((len(ids), length + 1), dtype=np.int32)
    valid = np.zeros((len(ids), length), dtype=np.float32)
    for i, seq in enumerate(ids):
        seq = seq[: length + 1]
        rows[i, : len(seq)] = seq
        valid[i, : len(seq) - 1] = 1.0
    if not len(ids):
        return []
    losses, _ = per_token_losses(params, cfg, rows, batch_size=batch_size)
    return [float(np.sum(losses[i] * valid[i]) / np.sum(valid[i])) for i in range(len(ids))]


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
