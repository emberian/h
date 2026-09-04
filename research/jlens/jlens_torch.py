"""J-lens Jacobians in PyTorch (for hbox's GPU), output-compatible with research/jlens/jlens.py.

Same quantity as the JAX implementation: at the last token t of each context,
J = d h_final[t] / d h_l[t] (d x d), averaged over contexts; M = lm_head_multiplier *
W_U diag(g_final) J. Layers are the model's own FalconH1DecoderLayer modules, called with
exactly the kwargs FalconH1Model.forward builds (causal mask, rotary embeddings,
cache_position); the Mamba mixer runs Transformers' reference torch path.

    python jlens_torch.py parity --checkpoint DIR --parity parity-L18.json --ref parity-L18-J.npy --layer 18
    python jlens_torch.py lens --checkpoint DIR --contexts contexts.json --layer 18 --out OUT/<model>
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch


MAMBA_ROOT = "/othersys/h1-ghost/kernel-test/mamba-source/mamba_ssm-2.3.2.post1"


def log(msg: str) -> None:
    print(f"[jlens-torch {time.strftime('%H:%M:%S')}] {msg}", flush=True)


class TorchLens:
    def __init__(self, checkpoint: str, device: str = "cuda", dtype=torch.float32, ssd_chunk: int = 32, kernel: str = "reference"):
        if kernel == "triton":
            # hbox_training/rocm_triton_ssd.py: Mamba-2's Triton SSD scan (autograd backward included)
            # in place of Transformers' reference path, which materializes 6-D intermediates.
            import sys as _sys
            _sys.path.insert(0, str(Path(__file__).resolve().parent))
            from rocm_triton_ssd import enable_rocm_triton_ssd

            self.kernel_report = enable_rocm_triton_ssd(Path(MAMBA_ROOT))
        else:
            self.kernel_report = {"enabled": False, "kernel": "reference"}
        from transformers import FalconH1ForCausalLM

        self.model = FalconH1ForCausalLM.from_pretrained(checkpoint, torch_dtype=dtype).to(device).eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        # The reference SSD path materializes (B, chunks, chunk, chunk, heads, head_dim) tensors;
        # a smaller chunk computes the same function with much smaller intermediates.
        for layer in self.model.model.layers:
            layer.mamba.chunk_size = ssd_chunk
        self.device = device
        self.dtype = dtype
        self.inner = self.model.model
        self.cfg = self.model.config
        self.d = self.cfg.hidden_size
        self.L = self.cfg.num_hidden_layers
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False

    def _kwargs(self, T: int, batch: int = 1):
        """The per-layer kwargs FalconH1Model.forward passes (no cache, no padding mask)."""
        cache_position = torch.arange(T, device=self.device)
        position_ids = cache_position.unsqueeze(0)
        dummy = torch.zeros(batch, T, self.d, device=self.device, dtype=self.dtype)
        causal_mask = self.inner._update_causal_mask(None, dummy, cache_position, None, False)
        mamba_mask = self.inner._update_mamba_mask(None, cache_position)
        position_embeddings = self.inner.rotary_emb(dummy, position_ids)
        return dict(
            attention_mask=causal_mask,
            mamba_attention_mask=mamba_mask,
            position_ids=position_ids,
            past_key_values=None,
            output_attentions=False,
            use_cache=False,
            cache_position=cache_position,
            position_embeddings=position_embeddings,
        )

    def _layer(self, i: int, h: torch.Tensor, kw: dict) -> torch.Tensor:
        out = self.inner.layers[i](h, **kw)
        return out[0] if isinstance(out, tuple) else out

    @torch.no_grad()
    def hidden_at_layer(self, ids: torch.Tensor, l: int) -> torch.Tensor:
        h = self.inner.embed_tokens(ids) * self.inner.embedding_multiplier
        kw = self._kwargs(ids.shape[1], ids.shape[0])
        for i in range(l):
            h = self._layer(i, h, kw)
        return h

    def residual_from(self, h: torch.Tensor, l: int) -> torch.Tensor:
        kw = self._kwargs(h.shape[1], h.shape[0])
        for i in range(l, self.L):
            h = self._layer(i, h, kw)
        return h

    @torch.no_grad()
    def logits_from(self, h: torch.Tensor, l: int) -> torch.Tensor:
        hf = self.inner.final_layernorm(self.residual_from(h, l))
        return self.model.lm_head(hf) * self.inner.lm_head_multiplier

    def readout_matrix(self) -> np.ndarray:
        W = self.model.lm_head.weight.detach().float()
        g = self.inner.final_layernorm.weight.detach().float()
        return (W * g[None, :] * self.inner.lm_head_multiplier).cpu().numpy()

    def jacobian(self, h_l: torch.Tensor, l: int, t: int, chunk: int, mode: str = "replicate") -> torch.Tensor:
        """G[k, s, :] = d h_final[t, k] / d h_l[s, :] for the single sequence h_l (1, T, d)."""
        T = h_l.shape[1]
        eye = torch.eye(self.d, device=self.device, dtype=self.dtype)
        rows = []
        start = 0
        while start < self.d:
            basis = eye[start : start + chunk]
            B = basis.shape[0]
            try:
                rows.append(self._rows(h_l, l, t, basis, mode))
            except torch.OutOfMemoryError:
                torch.cuda.empty_cache()
                if chunk <= 4:
                    raise
                chunk //= 2
                log(f"OOM at {B} rows; retrying with chunk={chunk}")
                continue
            start += B
        return torch.cat(rows, 0)  # (d, T, d)

    def _rows(self, h_l, l, t, basis, mode):
        T = h_l.shape[1]
        B = basis.shape[0]
        if True:
            if mode == "replicate":
                h = h_l.detach().expand(B, T, self.d).clone().requires_grad_(True)
                out = self.residual_from(h, l)[:, t, :]  # (B, d)
                (g,) = torch.autograd.grad(out, h, grad_outputs=basis)
            else:  # batched vjp via vmap over the backward
                h = h_l.detach().clone().requires_grad_(True)
                out = self.residual_from(h, l)[0, t, :]  # (d,)
                (g,) = torch.autograd.grad(out, h, grad_outputs=basis, is_grads_batched=True)
                g = g[:, 0]
            return g.detach()


def auto_chunk(T: int, tokens: int = 2048) -> int:
    return max(8, min(128, (tokens // T) // 8 * 8))


def cmd_parity(args):
    lens = TorchLens(args.checkpoint, ssd_chunk=args.ssd_chunk, kernel=args.kernel)
    meta = json.loads(Path(args.parity).read_text())
    ids = torch.tensor([meta["ids"]], device=lens.device)
    T = ids.shape[1]
    l = args.layer
    ref_J = np.load(args.ref)
    h = lens.hidden_at_layer(ids, l)
    ref_hl = np.load(str(args.ref).replace("-J.npy", "-hl.npy"))
    ref_hf = np.load(str(args.ref).replace("-J.npy", "-hfinal.npy"))
    hl = h[0].float().cpu().numpy()
    with torch.no_grad():
        hf = lens.residual_from(h, l)[0, T - 1].float().cpu().numpy()
    log(f"h_l rel err {np.linalg.norm(hl - ref_hl) / np.linalg.norm(ref_hl):.2e}; h_final[t] rel err {np.linalg.norm(hf - ref_hf) / np.linalg.norm(ref_hf):.2e}")
    for mode in args.modes:
        torch.cuda.synchronize(); t0 = time.time()
        try:
            G = lens.jacobian(h, l, T - 1, args.chunk or auto_chunk(T), mode)
        except Exception as e:  # noqa: BLE001
            log(f"mode {mode} failed: {type(e).__name__}: {str(e)[:200]}")
            continue
        torch.cuda.synchronize(); dt = time.time() - t0
        J = G[:, T - 1, :].float().cpu().numpy()
        rel = np.linalg.norm(J - ref_J) / np.linalg.norm(ref_J)
        cos = float((J * ref_J).sum() / (np.linalg.norm(J) * np.linalg.norm(ref_J)))
        log(f"mode {mode}: {dt:.1f}s (T={T}, chunk={args.chunk or auto_chunk(T)}); |J|_F torch {np.linalg.norm(J):.3f} jax {np.linalg.norm(ref_J):.3f}; rel Frobenius err {rel:.2e}; cos {cos:.6f}; max|diff| {np.abs(J - ref_J).max():.2e}; peak mem {torch.cuda.max_memory_allocated()/1e9:.1f} GB")
        json.dump({"mode": mode, "kernel": args.kernel, "chunk": args.chunk or auto_chunk(T), "seconds": dt, "rel_frob_err": float(rel), "cos": cos, "T": T, "layer": l, "frob_torch": float(np.linalg.norm(J)), "frob_jax": float(np.linalg.norm(ref_J)), "hl_rel_err": float(np.linalg.norm(hl - ref_hl) / np.linalg.norm(ref_hl)), "hfinal_rel_err": float(np.linalg.norm(hf - ref_hf) / np.linalg.norm(ref_hf)), "peak_mem_gb": torch.cuda.max_memory_allocated() / 1e9}, open(Path(args.out) / f"parity-torch-L{l}-{args.kernel}-{mode}.json", "w"), indent=1)


def cmd_lens(args):
    lens = TorchLens(args.checkpoint, ssd_chunk=args.ssd_chunk, kernel=args.kernel)
    d, L, l = lens.d, lens.L, args.layer
    ctx = json.loads(Path(args.contexts).read_text())["contexts"]
    if args.max_ctx:
        ctx = ctx[: args.max_ctx]
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    log(f"d={d} L={L} layer={l} contexts={len(ctx)} mode={args.mode}")
    t_start = time.time()
    sum_same = np.zeros((d, d), np.float64)
    sum_future = np.zeros((d, d), np.float64)
    lag_norm = np.zeros(64); lag_count = np.zeros(64)
    h_last, per_ctx = [], []
    for ci, c in enumerate(ctx):
        ids = torch.tensor([c["ids"]], device=lens.device)
        T = ids.shape[1]; t = T - 1
        h = lens.hidden_at_layer(ids, l)
        torch.cuda.synchronize(); t0 = time.time()
        G = lens.jacobian(h, l, t, args.chunk or auto_chunk(T), args.mode)
        torch.cuda.synchronize(); dt = time.time() - t0
        Gn = G.float().cpu().numpy()
        J_same = Gn[:, t, :]
        sum_same += J_same
        sum_future += Gn.mean(axis=1)
        norms = np.linalg.norm(Gn, axis=(0, 2))
        lags = t - np.arange(T); m = lags < 64
        lag_norm[lags[m]] += norms[m]; lag_count[lags[m]] += 1
        h_last.append(h[0, t].float().cpu().numpy())
        per_ctx.append({"ctx": ci, "t": t, "frob": float(np.linalg.norm(J_same)), "h_norm": float(np.linalg.norm(h_last[-1])), "seconds": dt})
        if ci % 10 == 0 or ci == len(ctx) - 1:
            log(f"ctx {ci+1}/{len(ctx)} T={T} jac {dt:.1f}s |J|_F={per_ctx[-1]['frob']:.3f} elapsed {(time.time()-t_start)/60:.1f}m peak mem {torch.cuda.max_memory_allocated()/1e9:.1f} GB")
        del G, Gn
    n = len(ctx)
    J_mean = (sum_same / n).astype(np.float32)
    J_future = (sum_future / n).astype(np.float32)
    R = lens.readout_matrix()
    np.save(out / f"lens-L{l}.npy", (R @ J_mean).astype(np.float32))
    np.save(out / f"lens-L{l}-future.npy", (R @ J_future).astype(np.float32))
    np.save(out / f"jac-L{l}.npy", J_mean)
    np.save(out / f"jac-L{l}-future.npy", J_future)
    np.save(out / f"hlast-L{l}.npy", np.stack(h_last).astype(np.float32))
    meta = {
        "model": args.model_name, "layer": l, "num_layers": L, "d": d, "n_jacobians": n,
        "backend": f"torch {torch.__version__} on {torch.cuda.get_device_name(0)} (hbox), fp32, kernel={args.kernel} (ssd chunk {args.ssd_chunk}), mode={args.mode}, rows/pass {args.chunk or auto_chunk(128)}",
        "kernel_report": lens.kernel_report,
        "contexts": [{k: v for k, v in c.items() if k != "ids"} | {"n_tokens": len(c["ids"])} for c in ctx],
        "per_context": per_ctx, "seconds_total": time.time() - t_start,
        "mean_frob_single": float(np.mean([p["frob"] for p in per_ctx])),
        "frob_mean_jacobian": float(np.linalg.norm(J_mean)),
        "lag_profile_frob": (lag_norm / np.maximum(lag_count, 1)).tolist(),
        "formula": "M = lm_head_multiplier * W_U diag(g_final) mean_{ctx,t}[d h_final[t] / d h_l[t]]",
    }
    (out / f"lens-L{l}.json").write_text(json.dumps(meta, indent=1))
    log(f"done: {n} jacobians in {meta['seconds_total']/60:.1f} min; mean per-jacobian {np.mean([p['seconds'] for p in per_ctx]):.1f}s")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("parity")
    p.add_argument("--checkpoint", required=True); p.add_argument("--parity", required=True); p.add_argument("--ref", required=True)
    p.add_argument("--layer", type=int, required=True); p.add_argument("--chunk", type=int, default=0)
    p.add_argument("--modes", nargs="*", default=["replicate", "batched"]); p.add_argument("--out", default=".")
    p.add_argument("--ssd-chunk", type=int, default=32); p.add_argument("--kernel", default="reference", choices=["reference", "triton"])
    p.set_defaults(fn=cmd_parity)
    p = sub.add_parser("lens")
    p.add_argument("--checkpoint", required=True); p.add_argument("--contexts", required=True)
    p.add_argument("--layer", type=int, required=True); p.add_argument("--chunk", type=int, default=0)
    p.add_argument("--mode", default="replicate", choices=["replicate", "batched"])
    p.add_argument("--max-ctx", type=int, default=0); p.add_argument("--out", required=True); p.add_argument("--model-name", default="")
    p.add_argument("--ssd-chunk", type=int, default=32); p.add_argument("--kernel", default="reference", choices=["reference", "triton"])
    p.set_defaults(fn=cmd_lens)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
