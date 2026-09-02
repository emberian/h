#!/usr/bin/env python3
"""Scoring worker for the explorer: per-token logprobs and ranks of a fixed text under a context, with h1jax on
CPU (float32), the same forward the evaluation pack uses. Runs under .venv-jax with PYTHONPATH=jax_training.

Protocol (one JSON object per line on stdin, one per line on stdout):
  {"checkpoint": "<dir>", "items": [{"id": ..., "context": "...", "text": "..."}], "ranks": true}
  -> {"checkpoint": ..., "results": [{"id", "n", "nll_sum", "nll_mean", "tokens": [{"id","text","logprob","rank"}]}],
      "seconds": ..., "loaded": <seconds to load, or 0>}
  {"ping": 1} -> {"pong": 1}
Only the tokens of `text` are scored (the context is the conditioning prefix); tokenisation is of context+text with
character offsets, so BPE merges across the boundary are attributed to the text. Sequences are padded to the next
bucket length so the model compiles once per bucket. Up to two checkpoints stay loaded (LRU).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("JAX_PLATFORM_NAME", "cpu")
os.environ.setdefault("H1JAX_SSD", "v2")

import jax  # noqa: E402
import jax.numpy as jnp  # noqa: E402
import numpy as np  # noqa: E402
from tokenizers import Tokenizer  # noqa: E402

from h1jax.checkpoint import load_hf_params  # noqa: E402
from h1jax.config import FalconH1Config  # noqa: E402
from h1jax.model import falcon_h1_forward  # noqa: E402

BUCKETS = (64, 128, 256, 512, 1024)
MAX_LOADED = 2


class Model:
    def __init__(self, path: Path, tokenizer: Tokenizer):
        self.path = path
        self.cfg = FalconH1Config.from_json(path / "config.json")
        self.params = load_hf_params(path, dtype=jnp.float32)
        self.tok = tokenizer
        cfg = self.cfg
        self.forward = jax.jit(
            lambda p, t: falcon_h1_forward(p, t, cfg, compute_dtype=jnp.float32, layer_scan=True)
        )
        self.used = time.time()

    def score(self, context: str, text: str, ranks: bool) -> dict:
        enc_ctx = self.tok.encode(context, add_special_tokens=False)
        enc_all = self.tok.encode(context + text, add_special_tokens=False)
        ids = enc_all.ids
        offsets = enc_all.offsets
        boundary = len(context)
        # text tokens: those whose span ends beyond the context boundary
        first = next((i for i, (a, b) in enumerate(offsets) if b > boundary), len(ids))
        if first == 0 and ids[: len(enc_ctx.ids)] == enc_ctx.ids:
            first = len(enc_ctx.ids)
        seq = ids[: max(1, min(len(ids), 1025))]
        n_total = len(seq)
        length = next((b for b in BUCKETS if b >= n_total), BUCKETS[-1])
        padded = np.zeros((1, length + 1), dtype=np.int32)
        padded[0, :n_total] = seq
        tokens = jnp.asarray(padded)
        logits = self.forward(self.params, tokens[:, :-1]).astype(jnp.float32)  # (1, length, V)
        logz = jax.nn.logsumexp(logits, axis=-1)
        labels = tokens[:, 1:]
        sel = jnp.take_along_axis(logits, labels[..., None], axis=-1)[..., 0]
        lp = np.asarray(sel - logz)[0]  # logprob of token t+1 given prefix..t
        rk = None
        if ranks:
            rk = np.asarray(jnp.sum(logits > sel[..., None], axis=-1))[0]
        out = []
        # token at position j (j>=1) is predicted at logits index j-1
        for j in range(max(1, first), n_total):
            piece = self.tok.decode([seq[j]])
            out.append({"id": int(seq[j]), "text": piece, "logprob": float(lp[j - 1]),
                        "rank": int(rk[j - 1]) if rk is not None else None})
        nll = [-t["logprob"] for t in out]
        return {"n": len(out), "nll_sum": float(sum(nll)), "nll_mean": (float(sum(nll)) / len(nll)) if nll else None,
                "context_tokens": int(first), "tokens": out, "bucket": length}


def main() -> None:
    tokenizer_path = sys.argv[1]
    tok = Tokenizer.from_file(tokenizer_path)
    models: dict[str, Model] = {}
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"bad json: {e}"}), flush=True)
            continue
        if "ping" in req:
            print(json.dumps({"pong": 1, "loaded": list(models)}), flush=True)
            continue
        started = time.time()
        ck = str(Path(req["checkpoint"]).resolve())
        loaded = 0.0
        try:
            if ck not in models:
                if len(models) >= MAX_LOADED:
                    oldest = min(models, key=lambda k: models[k].used)
                    del models[oldest]
                t0 = time.time()
                models[ck] = Model(Path(ck), tok)
                loaded = time.time() - t0
            m = models[ck]
            m.used = time.time()
            results = []
            for it in req.get("items", []):
                r = m.score(it.get("context", ""), it.get("text", ""), bool(req.get("ranks", True)))
                r["id"] = it.get("id")
                results.append(r)
            print(json.dumps({"checkpoint": ck, "results": results, "seconds": round(time.time() - started, 3),
                              "loaded": round(loaded, 2)}), flush=True)
        except Exception as e:  # noqa: BLE001
            print(json.dumps({"error": f"{type(e).__name__}: {e}", "checkpoint": ck}), flush=True)


if __name__ == "__main__":
    main()
