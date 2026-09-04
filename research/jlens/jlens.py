"""Jacobian lens (J-lens) for the small Falcon-H1 models, in JAX on CPU.

Method (after "A global workspace in language models", Anthropic 2026, Methods):

    J_l = E_{context, position t} [ d h_final[t] / d h_l[t] ]          (d x d)
    M   = c_head * W_U diag(g_final) J_l                                (V x d)

where h_l is the residual stream entering decoder layer l, h_final is the residual
leaving the last decoder layer (before the final RMS norm), g_final the final-norm gain,
W_U the unembedding and c_head the lm_head multiplier. Rows of M are the J-lens vectors.
The paper's expectation also runs over readout positions t' >= t; we get that variant
for free from the same reverse-mode passes (readout fixed at the last position, averaged
over source positions) and save it as "-future".

Subcommands: check, lens, readout, inject, sparse (see README.md).
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import sys
import time
from functools import partial
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

from h1jax.checkpoint import load_hf_params
from h1jax.config import FalconH1Config
from h1jax.model import (
    _layer_params,
    _linear,
    _rms_norm,
    decoder_layer,
    falcon_h1_forward,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "out"

MODELS = {
    "90m-base": "kaggle/base_model_dataset_public",
    "91m-leaf": (
        "artifacts/checkpoints/tpu/h-ghost-h1jax-leaf-s1-e4/leaf-s1-e4-decay10/"
        "tokens-001535061369"
    ),
    "05b-base": "artifacts/kaggle/base_model_05b",
    "05b-e2v4": (
        "artifacts/checkpoints/tpu/h-ghost-h1jax-room05b-e2-v4/room05b-e2-v4-decay10/"
        "tokens-000794693880"
    ),
}
TOKENIZER = ROOT / "kaggle/base_model_dataset_public/tokenizer.json"
VALIDATION = ROOT / "artifacts/dataset/validation-00000.jsonl.gz"
ROOM_PROMPTS = ROOT / "research/eval/room_prompts.json"

F32 = jnp.float32


# --------------------------------------------------------------------------- model glue


def load_model(name: str):
    root = ROOT / MODELS[name]
    cfg = FalconH1Config.from_json(root / "config.json")
    params = load_hf_params(root, dtype=F32)
    return params, cfg


def embed(params, cfg, ids):
    hidden = params["model.embed_tokens.weight"][ids].astype(F32)
    return hidden * jnp.asarray(cfg.embedding_multiplier, F32)


def hidden_at_layer(params, cfg, ids, l: int):
    """Residual stream entering decoder layer ``l`` (layers 0..l-1 applied)."""
    hidden = embed(params, cfg, ids)
    for index in range(l):
        hidden = decoder_layer(_layer_params(params, index), hidden, cfg)
    return hidden


def residual_from(params, cfg, hidden, l: int):
    """Run decoder layers l..L-1; return the final residual before the final norm."""
    for index in range(l, cfg.num_hidden_layers):
        hidden = decoder_layer(_layer_params(params, index), hidden, cfg)
    return hidden


def lm_head(params, cfg):
    return (
        params["model.embed_tokens.weight"]
        if cfg.tie_word_embeddings
        else params["lm_head.weight"]
    )


def unembed(params, cfg, hidden):
    """Final RMS norm + unembedding + lm_head multiplier, exactly as falcon_h1_forward."""
    hidden = _rms_norm(hidden, params["model.final_layernorm.weight"], cfg.rms_norm_eps)
    return _linear(hidden, lm_head(params, cfg)) * jnp.asarray(cfg.lm_head_multiplier, F32)


def forward_from(params, cfg, hidden, l: int):
    return unembed(params, cfg, residual_from(params, cfg, hidden, l))


def full_logits(params, cfg, ids):
    return falcon_h1_forward(params, ids, cfg, compute_dtype=F32, gradient_checkpointing=False)


def lens_readout_matrix(params, cfg):
    """c_head * W_U diag(g_final): the fixed linear part of the unembedding (V x d)."""
    gain = params["model.final_layernorm.weight"].astype(F32)
    return lm_head(params, cfg).astype(F32) * gain[None, :] * cfg.lm_head_multiplier


def jacobian_to_last(params, cfg, hidden_l, l: int, t, basis):
    """Reverse-mode rows of d h_final[0, t, :] / d h_l for the cotangents in ``basis``.

    Returns G with G[k, s, j] = sum_i basis[k, i] * d h_final[t, i] / d h_l[s, j].
    With basis = I this is the Jacobian J_{s->t} for every source position s <= t
    (positions > t get exactly zero by causality).
    """

    def f(h):
        return jax.lax.dynamic_index_in_dim(
            residual_from(params, cfg, h, l)[0], t, axis=0, keepdims=False
        )

    _, vjp = jax.vjp(f, hidden_l)
    return jax.vmap(lambda c: vjp(c)[0][0])(basis)


class Lensing:
    """Jitted pieces for one model."""

    def __init__(self, name: str):
        self.name = name
        self.params, self.cfg = load_model(name)
        self.d = self.cfg.hidden_size
        self.L = self.cfg.num_hidden_layers
        # Parameters are always passed as jit arguments (never closed over): closing over
        # them bakes the whole checkpoint into every compiled program as constants.
        cfg = self.cfg
        self._hidden = {}
        self._jac = {}
        self._fwd_from = {}
        self._res_from = {}
        self._logits = jax.jit(lambda p, ids: full_logits(p, cfg, ids))
        self._unembed = jax.jit(lambda p, h: unembed(p, cfg, h))
        self.readout_matrix = np.asarray(lens_readout_matrix(self.params, self.cfg))
        self.unembedding = np.asarray(lm_head(self.params, self.cfg), dtype=np.float32)

    def hidden(self, ids: np.ndarray, l: int):
        if l not in self._hidden:
            self._hidden[l] = jax.jit(lambda p, ids: hidden_at_layer(p, self.cfg, ids, l))
        return self._hidden[l](self.params, jnp.asarray(ids))

    def forward_from(self, hidden, l: int):
        if l not in self._fwd_from:
            self._fwd_from[l] = jax.jit(lambda p, h: forward_from(p, self.cfg, h, l))
        return self._fwd_from[l](self.params, hidden)

    def residual_from(self, hidden, l: int):
        if l not in self._res_from:
            self._res_from[l] = jax.jit(lambda p, h: residual_from(p, self.cfg, h, l))
        return self._res_from[l](self.params, hidden)

    def logits(self, ids: np.ndarray):
        return self._logits(self.params, jnp.asarray(ids))

    def unembed(self, hidden):
        return self._unembed(self.params, hidden)

    def jacobian(self, hidden_l, l: int, t: int, chunk: int):
        """All J_{s->t} (d x T x d array G[k, s, j]) for the single sequence hidden_l (1,T,d)."""
        if l not in self._jac:
            self._jac[l] = jax.jit(
                lambda p, h, t, basis: jacobian_to_last(p, self.cfg, h, l, t, basis)
            )
        eye = jnp.eye(self.d, dtype=F32)
        parts = []
        for start in range(0, self.d, chunk):
            parts.append(
                self._jac[l](self.params, hidden_l, jnp.int32(t), eye[start : start + chunk])
            )
        return jnp.concatenate(parts, axis=0)


# --------------------------------------------------------------------------- data


def get_tokenizer():
    from tokenizers import Tokenizer

    return Tokenizer.from_file(str(TOKENIZER))


def encode(tok, text: str) -> list[int]:
    return tok.encode(text, add_special_tokens=False).ids


def token_str(tok, i: int) -> str:
    s = tok.id_to_token(int(i))
    if s is None:
        return f"<id{i}>"
    return s.replace("Ġ", "␣").replace("Ċ", "⏎")


def room_prompts() -> list[dict]:
    return json.loads(ROOM_PROMPTS.read_text())


def sample_windows(tok, n: int, seed: int, min_len=64, max_len=128) -> list[dict]:
    """~n windows of min_len..max_len tokens from the library validation shard."""
    docs = []
    with gzip.open(VALIDATION, "rt") as f:
        for line in f:
            d = json.loads(line)
            docs.append((d["id"], d["text"]))
    rng = np.random.default_rng(seed)
    windows = []
    while len(windows) < n:
        doc_id, text = docs[rng.integers(len(docs))]
        if len(text) < 3000:
            continue
        start = int(rng.integers(0, len(text) - 3000))
        chunk = text[start : start + 3000]
        ids = encode(tok, chunk)
        length = int(rng.integers(min_len, max_len + 1))
        if len(ids) < length + 8:
            continue
        off = int(rng.integers(4, len(ids) - length))  # drop the possibly-cut first word
        window = ids[off : off + length]
        windows.append(
            {
                "source": "validation",
                "doc": doc_id,
                "char_start": start,
                "ids": window,
                "preview": tok.decode(window[:16]),
            }
        )
    return windows


def contexts_for(
    tok,
    n_windows: int,
    seed: int,
    include_room: bool = True,
    room_idx: list[int] | None = None,
    room_last: int = 0,
    min_len: int = 64,
    max_len: int = 128,
) -> list[dict]:
    """Validation windows plus room prompts (optionally a subset, truncated to their last tokens)."""
    ctx = sample_windows(tok, n_windows, seed, min_len, max_len)
    if include_room:
        for i, p in enumerate(room_prompts()):
            if room_idx is not None and i not in room_idx:
                continue
            ids = encode(tok, p["prompt"])
            if room_last:
                ids = ids[-room_last:]
            ctx.append(
                {
                    "source": "room",
                    "doc": f"room-{i}-{p['kind']}",
                    "ids": ids,
                    "truncated_to_last": room_last or None,
                    "preview": p["prompt"][-60:],
                }
            )
    return ctx


def bucket(n: int, step: int = 32) -> int:
    return int(math.ceil(n / step) * step)


def pad_ids(ids: list[int], length: int, pad: int = 0) -> np.ndarray:
    out = np.full((1, length), pad, dtype=np.int32)
    out[0, : len(ids)] = ids
    return out


# --------------------------------------------------------------------------- math helpers


def effective_rank(s: np.ndarray) -> dict:
    s = np.asarray(s, dtype=np.float64)
    p = s / s.sum()
    p = p[p > 0]
    entropy_rank = float(np.exp(-(p * np.log(p)).sum()))
    participation = float(s.sum() ** 2 / (s**2).sum())  # (sum s)^2 / sum s^2
    energy = np.cumsum(s**2) / (s**2).sum()
    return {
        "entropy_rank": entropy_rank,
        "participation_ratio": participation,
        "rank_90pct_energy": int(np.searchsorted(energy, 0.90) + 1),
        "rank_99pct_energy": int(np.searchsorted(energy, 0.99) + 1),
        "top_singular": [float(x) for x in s[:5]],
        "min_singular": float(s[-1]),
    }


def default_layers(L: int) -> list[int]:
    return [L // 2, L // 3, (2 * L) // 3]


def merge_json(path: Path, update: dict, key: str = "layers") -> None:
    """Write ``update`` to ``path``, merging its per-layer entries into an existing file."""
    if path.exists():
        prev = json.loads(path.read_text())
        merged = {**prev, **{k: v for k, v in update.items() if k != key}}
        merged[key] = {**prev.get(key, {}), **{str(k): v for k, v in update[key].items()}}
    else:
        merged = {**update, key: {str(k): v for k, v in update[key].items()}}
    path.write_text(json.dumps(merged, indent=1))


def model_dir(name: str) -> Path:
    d = OUT / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_lens(name: str, l: int, variant: str = "") -> np.ndarray:
    return np.load(model_dir(name) / f"lens-L{l}{variant}.npy")


def cosine_loading(M: np.ndarray, h: np.ndarray) -> np.ndarray:
    """Workspace loading: cosine similarity of h (d,) with each lens vector (row of M)."""
    norms = np.linalg.norm(M, axis=1) + 1e-12
    return (M @ h) / (norms * (np.linalg.norm(h) + 1e-12))


def nn_pursuit(D_unit: np.ndarray, x: np.ndarray, k: int) -> tuple[list[int], np.ndarray, float]:
    """Nonnegative orthogonal matching pursuit with unit-norm dictionary rows D_unit (n x d).

    Returns (selected indices, coefficients, fraction of ||x||^2 explained).
    """
    from scipy.optimize import nnls

    r = x.copy()
    selected: list[int] = []
    coef = np.zeros(0)
    for _ in range(k):
        scores = D_unit @ r
        if selected:
            scores[selected] = -np.inf
        i = int(np.argmax(scores))
        if scores[i] <= 0:
            break
        selected.append(i)
        A = D_unit[selected].T  # d x |S|
        coef, _ = nnls(A, x)
        r = x - A @ coef
    explained = 1.0 - float(r @ r) / float(x @ x)
    return selected, coef, explained


# --------------------------------------------------------------------------- check


def cmd_check(args):
    tok = get_tokenizer()
    lens = Lensing(args.model)
    cfg = lens.cfg
    layers = args.layers or default_layers(lens.L)
    prompt = room_prompts()[0]["prompt"]
    ids = np.asarray([encode(tok, prompt)], dtype=np.int32)
    T = ids.shape[1]
    print(f"[{args.model}] d={lens.d} L={lens.L} vocab_rows={lens.unembedding.shape[0]} T={T}")

    t0 = time.time()
    ref = np.asarray(lens.logits(ids))
    print(f"full forward: {time.time() - t0:.1f}s, logits {ref.shape}")
    report = {"model": args.model, "T": T, "reconstruction": {}, "finite_difference": {}}
    for l in layers:
        h = lens.hidden(ids, l)
        out = np.asarray(lens.forward_from(h, l))
        err = float(np.abs(out - ref).max())
        rel = float(np.abs(out - ref).max() / np.abs(ref).max())
        print(f"(a) reconstruction l={l}: max|diff|={err:.3e} (rel {rel:.2e}) -> {'ok' if err < 1e-4 else 'FAIL'}")
        report["reconstruction"][l] = {"max_abs": err, "rel": rel}

    # (b) finite differences against the Jacobian at the last position on a short window.
    rng = np.random.default_rng(0)
    short = ids[:, : min(T, 96)]
    Ts = short.shape[1]
    t = Ts - 1
    for l in layers:
        h = lens.hidden(short, l)
        t0 = time.time()
        G = np.asarray(lens.jacobian(h, l, t, args.chunk))  # (d, Ts, d)
        dt = time.time() - t0
        J = G[:, t, :]  # rows: output dims, cols: input dims
        h_np = np.asarray(h)
        hn = float(np.linalg.norm(h_np[0, t]))
        res = []
        for _ in range(3):
            u = rng.normal(size=lens.d).astype(np.float32)
            u /= np.linalg.norm(u)
            eps = 1e-3 * hn
            hp, hm = h_np.copy(), h_np.copy()
            hp[0, t] += eps * u
            hm[0, t] -= eps * u
            def final(hh):
                return np.asarray(lens.residual_from(jnp.asarray(hh), l))[0, t]
            fd = (final(hp) - final(hm)) / (2 * eps)
            pred = J @ u
            rel_err = float(np.linalg.norm(fd - pred) / np.linalg.norm(fd))
            cos = float(fd @ pred / (np.linalg.norm(fd) * np.linalg.norm(pred)))
            # logits through the real norm+unembed chain
            lp = np.asarray(lens.forward_from(jnp.asarray(hp), l))[0, t]
            lm = np.asarray(lens.forward_from(jnp.asarray(hm), l))[0, t]
            fd_logit = (lp - lm) / (2 * eps)
            hf = final(h_np)
            _, pred_logit = jax.jvp(
                lambda x: unembed(lens.params, cfg, x), (jnp.asarray(hf),), (jnp.asarray(pred),)
            )
            pred_logit = np.asarray(pred_logit)
            rel_logit = float(np.linalg.norm(fd_logit - pred_logit) / np.linalg.norm(fd_logit))
            res.append({"rel_err_hfinal": rel_err, "cos_hfinal": cos, "rel_err_logits": rel_logit})
        zero_future = float(np.abs(G[:, t + 1 :, :]).max()) if t + 1 < Ts else 0.0
        print(
            f"(b) finite-difference l={l}: jacobian {dt:.1f}s; "
            + "; ".join(f"rel {r['rel_err_hfinal']:.2e} cos {r['cos_hfinal']:.6f} logit-rel {r['rel_err_logits']:.2e}" for r in res)
            + f"; |J|_F={np.linalg.norm(J):.3f}; ||h_l||={hn:.2f}"
        )
        report["finite_difference"][l] = {"seconds": dt, "trials": res, "frob": float(np.linalg.norm(J)), "h_norm": hn, "max_grad_after_t": zero_future}
    (model_dir(args.model) / "check.json").write_text(json.dumps(report, indent=2))


# --------------------------------------------------------------------------- lens


def cmd_lens(args):
    tok = get_tokenizer()
    lens = Lensing(args.model)
    d, L = lens.d, lens.L
    layers = args.layers or default_layers(L)
    ctx = contexts_for(
        tok, args.n, args.seed, include_room=not args.no_room, room_idx=args.room_idx, room_last=args.room_last,
        min_len=args.min_len, max_len=args.max_len,
    )
    if args.max_ctx:
        ctx = ctx[: args.max_ctx]
    out = model_dir(args.model)
    print(f"[{args.model}] d={d} L={L} layers={layers} contexts={len(ctx)} chunk={args.chunk}")
    rng = np.random.default_rng(args.seed + 1)

    for l in layers:
        t_start = time.time()
        sum_same = np.zeros((d, d), np.float64)
        sum_future = np.zeros((d, d), np.float64)
        lag_norm = np.zeros(64, np.float64)
        lag_count = np.zeros(64, np.float64)
        h_last = []
        n_jac = 0
        per_ctx = []
        for ci, c in enumerate(ctx):
            ids = c["ids"]
            positions = [len(ids) - 1]
            if args.extra_positions and len(ids) > 24:
                positions += sorted(int(p) for p in rng.integers(16, len(ids) - 1, size=args.extra_positions))
            for t in positions:
                Tb = bucket(t + 1)
                batch = pad_ids(ids[: t + 1], Tb)
                h = lens.hidden(batch, l)
                t0 = time.time()
                G = np.asarray(lens.jacobian(h, l, t, args.chunk))  # (d, Tb, d)
                dt = time.time() - t0
                J_same = G[:, t, :]
                J_future = G[:, : t + 1, :].mean(axis=1)
                sum_same += J_same
                sum_future += J_future
                n_jac += 1
                norms = np.linalg.norm(G[:, : t + 1, :].reshape(d, t + 1, d), axis=(0, 2))  # per source position
                lags = t - np.arange(t + 1)
                m = lags < 64
                lag_norm[lags[m]] += norms[m]
                lag_count[lags[m]] += 1
                if t == len(ids) - 1:
                    h_last.append(np.asarray(h)[0, t])
                per_ctx.append({"ctx": ci, "t": t, "frob": float(np.linalg.norm(J_same)), "h_norm": float(np.linalg.norm(np.asarray(h)[0, t])), "seconds": dt})
                if ci % 10 == 0 or ci == len(ctx) - 1:
                    el = time.time() - t_start
                    print(f"  l={l} ctx {ci+1}/{len(ctx)} t={t} T={Tb} jac {dt:.1f}s |J|_F={per_ctx[-1]['frob']:.3f} elapsed {el/60:.1f}m", flush=True)
        J_mean = (sum_same / n_jac).astype(np.float32)
        J_future = (sum_future / n_jac).astype(np.float32)
        M = (lens.readout_matrix @ J_mean).astype(np.float32)
        M_future = (lens.readout_matrix @ J_future).astype(np.float32)
        np.save(out / f"lens-L{l}.npy", M)
        np.save(out / f"lens-L{l}-future.npy", M_future)
        np.save(out / f"jac-L{l}.npy", J_mean)
        np.save(out / f"jac-L{l}-future.npy", J_future)
        np.save(out / f"hlast-L{l}.npy", np.stack(h_last).astype(np.float32))
        stats = lens_stats(M, J_mean, lens, tok)
        stats_future = lens_stats(M_future, J_future, lens, tok)
        meta = {
            "model": args.model,
            "layer": l,
            "num_layers": L,
            "d": d,
            "n_jacobians": n_jac,
            "contexts": [{k: v for k, v in c.items() if k != "ids"} | {"n_tokens": len(c["ids"])} for c in ctx],
            "per_context": per_ctx,
            "seconds_total": time.time() - t_start,
            "mean_frob_single": float(np.mean([p["frob"] for p in per_ctx])),
            "frob_mean_jacobian": float(np.linalg.norm(J_mean)),
            "lag_profile_frob": (lag_norm / np.maximum(lag_count, 1)).tolist(),
            "same_position": stats,
            "future_variant": stats_future,
            "formula": "M = lm_head_multiplier * W_U diag(g_final) mean_{ctx,t}[d h_final[t] / d h_l[t]]",
        }
        (out / f"lens-L{l}.json").write_text(json.dumps(meta, indent=1))
        print(f"== {args.model} layer {l}: {n_jac} jacobians in {meta['seconds_total']/60:.1f} min")
        print_lens_stats(stats, "same-position")
        print_lens_stats(stats_future, "future-variant")
        prof = meta["lag_profile_frob"][:12]
        print("  |J_{s->t}|_F by lag t-s:", " ".join(f"{x:.3f}" for x in prof))


def lens_stats(M, J, lens, tok, top=20):
    sM = np.linalg.svd(M.astype(np.float64), compute_uv=False)
    sJ = np.linalg.svd(J.astype(np.float64), compute_uv=False)
    norms = np.linalg.norm(M, axis=1)
    unorm = np.linalg.norm(lens.readout_matrix, axis=1)
    V = min(M.shape[0], tok.get_vocab_size())
    ratio = norms[:V] / (unorm[:V] + 1e-12)
    order = np.argsort(-norms[:V])[:top]
    order_ratio = np.argsort(-ratio)[:top]
    logit_lens_top = np.argsort(-unorm[:V])[:top]
    pct = np.percentile(norms[:V], [1, 10, 50, 90, 99, 100])
    return {
        "erank_M": effective_rank(sM),
        "erank_J": effective_rank(sJ),
        "norm_percentiles_1_10_50_90_99_100": [float(x) for x in pct],
        "mean_norm": float(norms[:V].mean()),
        "mean_unembed_norm": float(unorm[:V].mean()),
        "top_by_norm": [(int(i), token_str(tok, i), float(norms[i])) for i in order],
        "top_by_norm_ratio_vs_unembed": [(int(i), token_str(tok, i), float(ratio[i])) for i in order_ratio],
        "top_unembed_norm": [(int(i), token_str(tok, i), float(unorm[i])) for i in logit_lens_top],
        "cos_M_vs_unembed_rows_mean": float(
            np.mean(np.einsum("ij,ij->i", M[:V], lens.readout_matrix[:V]) / (norms[:V] * unorm[:V] + 1e-12))
        ),
    }


def print_lens_stats(s, label):
    eJ, eM = s["erank_J"], s["erank_M"]
    print(f"  [{label}] erank(J): entropy {eJ['entropy_rank']:.1f} PR {eJ['participation_ratio']:.1f} 90%-energy {eJ['rank_90pct_energy']} top-sv {eJ['top_singular'][0]:.3f}")
    print(f"  [{label}] erank(M): entropy {eM['entropy_rank']:.1f} PR {eM['participation_ratio']:.1f} 90%-energy {eM['rank_90pct_energy']}")
    print(f"  [{label}] lens-norm pct 1/10/50/90/99/100: " + " ".join(f"{x:.3g}" for x in s["norm_percentiles_1_10_50_90_99_100"]))
    print(f"  [{label}] top-20 by norm: " + " ".join(f"{t}" for _, t, _ in s["top_by_norm"]))
    print(f"  [{label}] top-20 by norm/unembed-norm: " + " ".join(f"{t}" for _, t, _ in s["top_by_norm_ratio_vs_unembed"]))
    print(f"  [{label}] mean cos(lens row, unembed row) = {s['cos_M_vs_unembed_rows_mean']:.3f}")


def cmd_stats(args):
    """Fill lens statistics into lens-L<l>.json for lenses computed elsewhere (hbox/PyTorch)."""
    tok = get_tokenizer()
    lens = Lensing(args.model)
    for l in args.layers or default_layers(lens.L):
        out = model_dir(args.model)
        M, J = load_lens(args.model, l), np.load(out / f"jac-L{l}.npy")
        Mf, Jf = load_lens(args.model, l, "-future"), np.load(out / f"jac-L{l}-future.npy")
        path = out / f"lens-L{l}.json"
        meta = json.loads(path.read_text()) if path.exists() else {"model": args.model, "layer": l}
        meta["same_position"] = lens_stats(M, J, lens, tok)
        meta["future_variant"] = lens_stats(Mf, Jf, lens, tok)
        path.write_text(json.dumps(meta, indent=1))
        print(f"== {args.model} layer {l}: {meta.get('n_jacobians', '?')} jacobians ({meta.get('backend', 'jax')})")
        print_lens_stats(meta["same_position"], "same-position")
        print_lens_stats(meta["future_variant"], "future-variant")


# --------------------------------------------------------------------------- readout


def topk_tokens(scores: np.ndarray, tok, k=10, V=None):
    V = V or tok.get_vocab_size()
    idx = np.argsort(-scores[:V])[:k]
    return [(token_str(tok, i), float(scores[i])) for i in idx]


def cmd_readout(args):
    tok = get_tokenizer()
    lens = Lensing(args.model)
    layers = args.layers or default_layers(lens.L)
    V = tok.get_vocab_size()
    prompts = room_prompts()
    if args.prompt:
        prompts = [{"kind": "cli", "prompt": args.prompt}]
    if args.only is not None:
        prompts = [prompts[i] for i in args.only]
    results = []
    for l in layers:
        M = load_lens(args.model, l, args.variant)
        for pi, p in enumerate(prompts):
            ids = encode(tok, p["prompt"])
            batch = np.asarray([ids], dtype=np.int32)
            h = np.asarray(lens.hidden(batch, l))[0]
            logits = np.asarray(lens.logits(batch))[0]
            logit_lens = np.asarray(lens.unembed(jnp.asarray(h[None])))[0]
            J = np.load(model_dir(args.model) / f"jac-L{l}{args.variant}.npy")
            jlens_logit = np.asarray(lens.unembed(jnp.asarray((h @ J.T)[None])))[0]
            T = len(ids)
            positions = {"final": T - 1, "h-label": T - 2, "last-user-token": T - 4}
            entry = {"layer": l, "prompt": pi, "kind": p["kind"], "tail": p["prompt"][-50:], "positions": {}}
            print(f"\n=== {args.model} L{l} prompt {pi} [{p['kind']}] ...{p['prompt'][-40:]!r}")
            M_centered = M - M.mean(axis=0, keepdims=True)  # diagnostic: remove the shared lens direction
            for label, t in positions.items():
                load = cosine_loading(M, h[t])
                load_c = cosine_loading(M_centered, h[t])
                pred = jax.nn.log_softmax(logits[t])
                pred = np.asarray(pred)
                top_load = topk_tokens(load, tok, 10, V)
                top_load_c = topk_tokens(load_c, tok, 10, V)
                top_pred = topk_tokens(pred, tok, 10, V)
                top_ll = topk_tokens(logit_lens[t], tok, 10, V)
                top_jl = topk_tokens(jlens_logit[t], tok, 10, V)
                pred_set = {s for s, _ in top_pred}
                unsaid = [s for s, _ in top_load if s not in pred_set]
                entry["positions"][label] = {
                    "t": t,
                    "token": token_str(tok, ids[t]),
                    "loading_top10": top_load,
                    "centered_loading_top10": top_load_c,
                    "jlens_logit_top10": top_jl,
                    "logit_lens_top10": top_ll,
                    "prediction_top10": top_pred,
                    "loaded_not_predicted": unsaid,
                    "max_loading": float(load[:V].max()),
                }
                print(f"  @{label} (t={t}, tok {token_str(tok, ids[t])!r})")
                print("    loading (cos) : " + " ".join(f"{s}:{v:.2f}" for s, v in top_load))
                print("    centered load : " + " ".join(f"{s}:{v:.2f}" for s, v in top_load_c))
                print("    J-lens logits : " + " ".join(f"{s}" for s, _ in top_jl))
                print("    logit lens    : " + " ".join(f"{s}" for s, _ in top_ll))
                print("    prediction    : " + " ".join(f"{s}:{math.exp(v):.2f}" for s, v in top_pred))
                print("    loaded-not-predicted: " + " ".join(unsaid))
            results.append(entry)
    suffix = "" if not args.prompt else "-cli"
    path = model_dir(args.model) / f"readout{args.variant}{suffix}.json"
    if path.exists():
        done = {e["layer"] for e in results}
        results = [e for e in json.loads(path.read_text()) if e["layer"] not in done] + results
    path.write_text(json.dumps(results, indent=1))


# --------------------------------------------------------------------------- inject

FILLERS = [
    "The kettle whistled while the cat slept on the windowsill",
    "She folded the letter twice and slid it under the door",
    "Rain had been falling since dawn and the gutters overflowed",
    "The old clock in the hallway lost four minutes every day",
    "He sharpened the pencil until the point snapped again",
    "A single lamp burned in the window of the bakery",
    "The children counted the steps down to the cellar",
    "Nobody remembered who had planted the apple tree",
    "The ferry left the dock ten minutes behind schedule",
    "My grandmother kept her buttons in a biscuit tin",
    "The choir rehearsed the same verse until midnight",
    "A stray dog followed the postman along the canal",
    "The bridge was closed for repairs all summer",
    "Someone had left a bicycle chained to the fence",
    "The soup needed more salt and a little pepper",
    "Frost covered the fields by the end of the week",
    "The librarian stamped the book and smiled",
    "Two swans drifted past the reeds without a sound",
    "The train conductor checked his watch and nodded",
    "Paint peeled from the shutters of the empty house",
    "We waited under the awning for the storm to pass",
    "The market stalls were packed away before noon",
    "A moth circled the bulb above the kitchen table",
    "The mechanic wiped his hands on a greasy rag",
    "The river had risen almost to the lower path",
    "She tuned the violin while the audience settled",
    "The last bus climbs the hill just after eleven",
    "Dust gathered on the piano nobody played anymore",
    "The fisherman mended his nets on the quay",
    "Snow muffled every footstep in the narrow lane",
    "The gardener pruned the roses before the first frost",
    "A kite tangled itself in the telephone wires",
    "The waiter brought two coffees and the bill",
    "The lighthouse keeper logged the wind at dusk",
    "Our neighbour practices the trumpet on Sundays",
    "The ink had faded on the back of the photograph",
    "The tailor measured the sleeve a second time",
    "Bees hummed in the lavender beside the path",
    "The projector flickered and the film began",
    "A cold draught crept in under the workshop door",
]

COUNTRIES = [
    ("France", "Paris"),
    ("Italy", "Rome"),
    ("Germany", "Berlin"),
    ("England", "London"),
    ("Japan", "Tokyo"),
    ("Egypt", "Cairo"),
    ("Spain", "Madrid"),
    ("Russia", "Moscow"),
    ("China", "Beijing"),
    ("Canada", "Ottawa"),
    ("Brazil", "Brasilia"),
    ("Greece", "Athens"),
]


def cmd_inject(args):
    tok = get_tokenizer()
    lens = Lensing(args.model)
    layers = args.layers or default_layers(lens.L)
    rng = np.random.default_rng(args.seed)
    alphas = args.alphas
    fillers = FILLERS[: args.n_fillers]
    countries = COUNTRIES[: args.n_countries]
    W_U = lens.unembedding
    template = args.template  # "{filler}. The capital city is"
    results = {"model": args.model, "template": template, "alphas": alphas, "n_fillers": len(fillers), "countries": [c for c, _ in countries], "layers": {}}

    # Tokenize prompts; injection position = last filler token (or the following period).
    prompts = []
    for f in fillers:
        pre = encode(tok, f)
        full = encode(tok, template.format(filler=f))
        assert full[: len(pre)] == pre, (f, tok.decode(full[: len(pre)]), f)
        prompts.append({"prompt_ids": full, "inject_pos": len(pre) - 1, "period_pos": len(pre)})
    cap_ids = {c: encode(tok, " " + cap) for c, cap in countries}
    country_ids = {}
    for c, _ in countries:
        e = encode(tok, " " + c)
        assert len(e) == 1, (c, e)
        country_ids[c] = e[0]
    nC, nF = len(countries), len(fillers)

    def pack(seqs):
        Tb = bucket(max(len(s) for s in seqs))
        ids = np.zeros((len(seqs), Tb), np.int32)
        for i, s in enumerate(seqs):
            ids[i, : len(s)] = s
        return ids

    def span_logprob(logits, ids, spans):
        logp = np.asarray(jax.nn.log_softmax(jnp.asarray(logits), axis=-1))
        return np.asarray([sum(logp[i, j - 1, ids[i, j]] for j in range(a, b)) for i, (a, b) in enumerate(spans)])

    # One batch holding every (capital, filler) teacher-forced continuation: row = ci * nF + fi.
    seqs, spans = [], []
    for c, _ in countries:
        for p in prompts:
            seqs.append(p["prompt_ids"] + cap_ids[c])
            spans.append((len(p["prompt_ids"]), len(p["prompt_ids"]) + len(cap_ids[c])))
    ids_all = pack(seqs)
    inj_pos = np.asarray([p[args.inject_at] for p in prompts] * nC)
    rows = np.arange(nC * nF)
    cap_len = np.asarray([len(cap_ids[c]) for c, _ in countries])

    for l in layers:
        M = load_lens(args.model, l, args.variant)
        h_all = lens.hidden(ids_all, l)  # (nC*nF, Tb, d), injection-independent
        h_norms = np.asarray(jnp.linalg.norm(h_all[rows, inj_pos], axis=-1))  # per row
        base = span_logprob(np.asarray(lens.forward_from(h_all, l)), ids_all, spans).reshape(nC, nF)
        nat = np.zeros((nC, nF))
        for k, (c, _) in enumerate(countries):
            s2, sp2 = [], []
            for f in fillers:
                ids = encode(tok, args.natural_template.format(filler=f, country=c))
                s2.append(ids + cap_ids[c])
                sp2.append((len(ids), len(ids) + len(cap_ids[c])))
            ids2 = pack(s2)
            nat[k] = span_logprob(np.asarray(lens.forward_from(lens.hidden(ids2, l), l)), ids2, sp2)
        base_top1 = (np.argmax(base / cap_len[:, None], axis=0) == np.arange(nC)[:, None]).mean(axis=1)

        res_l = {"countries": {}, "summary": {}, "h_norm_mean_at_inject": float(h_norms.mean())}
        agg = {dirn: {a: {"correct": [], "others": [], "top1": []} for a in alphas} for dirn in ("lens", "unembed", "random")}
        for k, (c, cap) in enumerate(countries):
            cid = country_ids[c]
            dirs = {
                "lens": M[cid] / np.linalg.norm(M[cid]),
                "unembed": W_U[cid] / np.linalg.norm(W_U[cid]),
                "random": (lambda v: v / np.linalg.norm(v))(rng.normal(size=lens.d)),
            }
            per_c = {"baseline_logp": float(base[k].mean()), "natural_logp": float(nat[k].mean()), "baseline_top1_among_capitals": float(base_top1[k])}
            for dirn, u in dirs.items():
                for a in alphas:
                    vecs = (a * h_norms)[:, None] * u[None, :].astype(np.float32)
                    h_inj = h_all.at[rows, inj_pos].add(jnp.asarray(vecs))
                    lp = span_logprob(np.asarray(lens.forward_from(h_inj, l)), ids_all, spans).reshape(nC, nF)
                    lift = lp - base  # (capital, filler)
                    lift_correct = lift[k].mean()
                    lift_others = np.delete(lift, k, axis=0).mean()
                    top1 = (np.argmax(lp / cap_len[:, None], axis=0) == k).mean()
                    agg[dirn][a]["correct"].append(float(lift_correct))
                    agg[dirn][a]["others"].append(float(lift_others))
                    agg[dirn][a]["top1"].append(float(top1))
                    per_c[f"{dirn}_a{a:g}"] = {"lift_correct": float(lift_correct), "lift_others": float(lift_others), "top1_among_capitals": float(top1), "logp_correct": float(lp[k].mean())}
            res_l["countries"][c] = per_c
            print(f"  L{l} {c:8s} base {per_c['baseline_logp']:.2f} natural {per_c['natural_logp']:.2f} top1 {per_c['baseline_top1_among_capitals']:.2f} | " + " | ".join(f"{dn} " + " ".join(f"a{a:g}:{per_c[f'{dn}_a{a:g}']['lift_correct']:+.2f}/{per_c[f'{dn}_a{a:g}']['lift_others']:+.2f}" for a in alphas) for dn in dirs), flush=True)
        for dirn in agg:
            for a in alphas:
                s = agg[dirn][a]
                res_l["summary"][f"{dirn}_a{a:g}"] = {
                    "mean_lift_correct": float(np.mean(s["correct"])),
                    "mean_lift_others": float(np.mean(s["others"])),
                    "specific_lift": float(np.mean(s["correct"]) - np.mean(s["others"])),
                    "top1_among_capitals": float(np.mean(s["top1"])),
                }
        res_l["summary"]["baseline_top1_among_capitals"] = float(base_top1.mean())
        res_l["summary"]["natural_minus_baseline"] = float((nat - base).mean())
        results["layers"][l] = res_l
        print(f"== {args.model} L{l} inject summary (mean over {nC} countries x {nF} fillers); natural-prompt ceiling lift {res_l['summary']['natural_minus_baseline']:+.2f}; baseline top1 {base_top1.mean():.2f}")
        for dirn in ("lens", "unembed", "random"):
            print("   " + dirn.ljust(8) + " ".join(f"a{a:g}: correct {res_l['summary'][f'{dirn}_a{a:g}']['mean_lift_correct']:+.2f} others {res_l['summary'][f'{dirn}_a{a:g}']['mean_lift_others']:+.2f} specific {res_l['summary'][f'{dirn}_a{a:g}']['specific_lift']:+.2f} top1 {res_l['summary'][f'{dirn}_a{a:g}']['top1_among_capitals']:.2f} |" for a in alphas))
    merge_json(model_dir(args.model) / f"inject{args.variant}-{args.inject_at}.json", results)


# --------------------------------------------------------------------------- sparse


def cmd_sparse(args):
    tok = get_tokenizer()
    lens = Lensing(args.model)
    layers = args.layers or default_layers(lens.L)
    V = tok.get_vocab_size()
    rng = np.random.default_rng(args.seed)
    prompts = room_prompts()
    results = {"model": args.model, "k": args.k, "layers": {}}
    for l in layers:
        M = load_lens(args.model, l, args.variant)[:V]
        dicts = {
            "lens": M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12),
            "unembed": lens.unembedding[:V] / (np.linalg.norm(lens.unembedding[:V], axis=1, keepdims=True) + 1e-12),
            "random": (lambda R: R / np.linalg.norm(R, axis=1, keepdims=True))(rng.normal(size=(V, lens.d)).astype(np.float32)),
        }
        # residuals: room prompt final positions (fresh forward) + stored final positions of lens contexts
        room_h = []
        for p in prompts:
            ids = np.asarray([encode(tok, p["prompt"])], np.int32)
            room_h.append(np.asarray(lens.hidden(ids, l))[0, -1])
        room_h = np.stack(room_h)
        stored = np.load(model_dir(args.model) / f"hlast-L{l}.npy")
        stored = stored[: args.n_stored]
        res_l = {"room": [], "fractions": {}}
        for name, D in dicts.items():
            fr_room, fr_stored = [], []
            for i, x in enumerate(room_h):
                sel, coef, expl = nn_pursuit(D, x.astype(np.float64), args.k)
                fr_room.append(expl)
                if name == "lens":
                    res_l["room"].append({"prompt": i, "kind": prompts[i]["kind"], "explained": expl, "atoms": [(token_str(tok, j), float(c)) for j, c in zip(sel, coef)]})
                    print(f"  L{l} room {i:2d} [{prompts[i]['kind']:8s}] J-space fraction {expl:.3f}: " + " ".join(f"{token_str(tok, j)}:{c:.1f}" for j, c in zip(sel, coef)))
            for x in stored:
                _, _, expl = nn_pursuit(D, x.astype(np.float64), args.k)
                fr_stored.append(expl)
            res_l["fractions"][name] = {"room_mean": float(np.mean(fr_room)), "room_all": [float(v) for v in fr_room], "stored_mean": float(np.mean(fr_stored)), "stored_std": float(np.std(fr_stored)), "n_stored": len(fr_stored)}
            print(f"== {args.model} L{l} k={args.k} dict={name:8s} fraction explained: room {np.mean(fr_room):.3f}  library contexts {np.mean(fr_stored):.3f} +- {np.std(fr_stored):.3f} (n={len(fr_stored)})")
        results["layers"][l] = res_l
    merge_json(model_dir(args.model) / f"sparse{args.variant}-k{args.k}.json", results)


# --------------------------------------------------------------------------- cli


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--model", required=True, choices=sorted(MODELS))
        p.add_argument("--layers", type=int, nargs="*", help="residual-stream layers (default L/2, L/3, 2L/3)")
        p.add_argument("--variant", default="", choices=["", "-future"], help="lens variant to read")
        p.add_argument("--seed", type=int, default=0)

    p = sub.add_parser("check"); common(p)
    p.add_argument("--chunk", type=int, default=256)
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("lens"); common(p)
    p.add_argument("--n", type=int, default=200, help="validation windows")
    p.add_argument("--no-room", action="store_true")
    p.add_argument("--room-idx", type=int, nargs="*", default=None, help="subset of room prompts to include")
    p.add_argument("--room-last", type=int, default=0, help="truncate room prompts to their last K tokens")
    p.add_argument("--min-len", type=int, default=64)
    p.add_argument("--max-len", type=int, default=128)
    p.add_argument("--max-ctx", type=int, default=0)
    p.add_argument("--extra-positions", type=int, default=0, help="extra random earlier positions per context")
    p.add_argument("--chunk", type=int, default=256, help="cotangent rows per vjp batch")
    p.set_defaults(fn=cmd_lens)

    p = sub.add_parser("stats"); common(p)
    p.set_defaults(fn=cmd_stats)

    p = sub.add_parser("readout"); common(p)
    p.add_argument("--prompt", default=None)
    p.add_argument("--only", type=int, nargs="*", default=None)
    p.set_defaults(fn=cmd_readout)

    p = sub.add_parser("inject"); common(p)
    p.add_argument("--alphas", type=float, nargs="*", default=[2.0, 4.0, 8.0])
    p.add_argument("--n-fillers", type=int, default=40)
    p.add_argument("--n-countries", type=int, default=len(COUNTRIES))
    p.add_argument("--template", default="{filler}. The capital city is")
    p.add_argument("--natural-template", default="{filler}. The capital city of {country} is")
    p.add_argument("--inject-at", default="inject_pos", choices=["inject_pos", "period_pos"], help="last filler token (default) or the following period")
    p.set_defaults(fn=cmd_inject)

    p = sub.add_parser("sparse"); common(p)
    p.add_argument("--k", type=int, default=8)
    p.add_argument("--n-stored", type=int, default=100)
    p.set_defaults(fn=cmd_sparse)

    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
