"""Aggregate research/jlens/out/<model>/*.json into markdown tables (stdout)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "out"
MODELS = ["90m-base", "91m-leaf", "05b-base", "05b-e2v4"]


def load(path):
    return json.loads(path.read_text()) if path.exists() else None


def pairwise_cos(A: np.ndarray, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    idx = rng.choice(A.shape[0], size=min(n, A.shape[0]), replace=False)
    X = A[idx].astype(np.float64)
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    C = X @ X.T
    off = C[~np.eye(len(idx), dtype=bool)]
    return float(off.mean()), float(np.median(off)), float(np.percentile(off, 5)), float(np.percentile(off, 95))


MODEL_DIRS = {
    "90m-base": "kaggle/base_model_dataset_public",
    "91m-leaf": "artifacts/checkpoints/tpu/h-ghost-h1jax-leaf-s1-e4/leaf-s1-e4-decay10/tokens-001535061369",
    "05b-base": "artifacts/kaggle/base_model_05b",
    "05b-e2v4": "artifacts/checkpoints/tpu/h-ghost-h1jax-room05b-e2-v4/room05b-e2-v4-decay10/tokens-000794693880",
}
_UC = {}


def unembed_paircos(m):
    if m not in _UC:
        from safetensors import safe_open

        root = OUT.parents[2] / MODEL_DIRS[m]
        cfg = json.loads((root / "config.json").read_text())
        key = "model.embed_tokens.weight" if cfg.get("tie_word_embeddings", True) else "lm_head.weight"
        import jax.numpy as jnp

        with safe_open(str(root / "model.safetensors"), framework="flax") as h:  # bf16-safe
            W = np.asarray(jnp.asarray(h.get_tensor(key), dtype=jnp.float32))
        _UC[m] = pairwise_cos(W)[0]
    return _UC[m]


def fmt_tokens(items, n=20):
    return " ".join(f"`{t}`" for _, t, _ in items[:n])


def section_check():
    print("## Sanity checks\n")
    print("| model | layer | (a) max abs logit diff (reconstruction) | (b) FD rel. err on h_final (3 trials) | cos | FD rel. err on logits | Jacobian time (T=96) |")
    print("|---|---|---|---|---|---|---|")
    for m in MODELS:
        c = load(OUT / m / "check.json")
        if not c:
            continue
        for l, r in c["reconstruction"].items():
            fd = c["finite_difference"].get(l)
            if fd:
                rel = "/".join(f"{t['rel_err_hfinal']:.1e}" for t in fd["trials"])
                cos = min(t["cos_hfinal"] for t in fd["trials"])
                rl = "/".join(f"{t['rel_err_logits']:.1e}" for t in fd["trials"])
                sec = f"{fd['seconds']:.0f}s"
            else:
                rel = cos = rl = sec = "-"
            print(f"| {m} | {l} | {r['max_abs']:.1e} | {rel} | {cos if cos == '-' else f'{cos:.6f}'} | {rl} | {sec} |")
    print()


def section_lens():
    print("## Lens statistics (same-position Jacobian)\n")
    print("| model | layer | N jac | minutes | erank(J) entropy / PR / 90%-energy | erank(M) entropy / PR / 90%-energy | \\|J_mean\\|_F / mean \\|J_i\\|_F | lens-norm p10/p50/p90 | cos(lens row, unembed row) | pairwise cos lens rows (mean, p5, p95) | pairwise cos unembed rows (mean) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    tops = []
    for m in MODELS:
        paths = [p for p in (OUT / m).glob("lens-L*.json")] if (OUT / m).exists() else []
        for p in sorted(paths, key=lambda q: int(q.stem.split("L")[-1])):
            if "future" in p.name:
                continue
            j = load(p)
            l = j["layer"]
            s = j["same_position"]
            eJ, eM = s["erank_J"], s["erank_M"]
            pct = s["norm_percentiles_1_10_50_90_99_100"]
            M = np.load(OUT / m / f"lens-L{l}.npy")
            pc = pairwise_cos(M)
            V = M.shape[0]
            uc = f"{unembed_paircos(m):.3f}"
            print(f"| {m} | {l} | {j['n_jacobians']} | {j['seconds_total']/60:.0f} | {eJ['entropy_rank']:.0f} / {eJ['participation_ratio']:.0f} / {eJ['rank_90pct_energy']} | {eM['entropy_rank']:.0f} / {eM['participation_ratio']:.0f} / {eM['rank_90pct_energy']} | {j['frob_mean_jacobian']:.1f} / {j['mean_frob_single']:.1f} | {pct[1]:.2f}/{pct[2]:.2f}/{pct[3]:.2f} | {s['cos_M_vs_unembed_rows_mean']:.3f} | {pc[0]:.3f}, {pc[2]:.3f}, {pc[3]:.3f} | {uc} |")
            tops.append((m, l, s, j))
    print()
    print("### Top lens tokens\n")
    for m, l, s, j in tops:
        print(f"**{m} L{l}** top-20 by lens-vector norm: {fmt_tokens(s['top_by_norm'])}  ")
        print(f"top-20 by norm ratio lens/unembed (tokens the Jacobian amplifies): {fmt_tokens(s['top_by_norm_ratio_vs_unembed'])}  ")
        fut = j.get("future_variant")
        if fut:
            print(f"future-variant top-20 by norm: {fmt_tokens(fut['top_by_norm'])}  ")
        prof = j["lag_profile_frob"][:8]
        print(f"\\|J_(s->t)\\|_F by lag t-s = 0..7: " + ", ".join(f"{x:.1f}" for x in prof) + "\n")
    print()


def section_readout():
    print("## Readout on the room prompts (workspace loading = cosine with lens vectors)\n")
    for m in MODELS:
        r = load(OUT / m / "readout.json")
        if not r:
            continue
        layers = sorted({e["layer"] for e in r})
        for l in layers:
            entries = [e for e in r if e["layer"] == l]
            maxload = np.mean([e["positions"]["final"]["max_loading"] for e in entries])
            overlap = np.mean([10 - len(e["positions"]["final"]["loaded_not_predicted"]) for e in entries])
            print(f"### {m} L{l}  (mean max loading at final position {maxload:.3f}; mean |top10 loading ∩ top10 prediction| = {overlap:.1f}/10)\n")
            print("| prompt | pos | loading top-10 (cos) | paper readout softmax(W_U norm(J h)) top-10 | centered loading top-10 (diagnostic) | model top-10 next tokens (p) | loaded, not predicted |")
            print("|---|---|---|---|---|---|---|")
            for e in entries:
                for pos in ("final", "h-label"):
                    q = e["positions"][pos]
                    ld = " ".join(f"`{t}`:{v:.2f}" for t, v in q["loading_top10"])
                    jl = " ".join(f"`{t}`" for t, _ in q["jlens_logit_top10"])
                    lc = " ".join(f"`{t}`:{v:.2f}" for t, v in q.get("centered_loading_top10", [])[:6])
                    pr = " ".join(f"`{t}`:{np.exp(v):.2f}" for t, v in q["prediction_top10"])
                    un = " ".join(f"`{t}`" for t in q["loaded_not_predicted"])
                    print(f"| {e['prompt']} {e['kind']} | {pos} `{q['token']}` | {ld} | {jl} | {lc} | {pr} | {un} |")
            print()


def section_inject():
    print("## Injection (flexible use): capital recall after adding a country direction at the filler's last token\n")
    print("Lift = mean log p(capital tokens) after injection minus before; 'others' = the same lift averaged over the 11 other capitals; 'specific' = correct - others; top1 = fraction of fillers where the correct capital has the highest per-token log-prob among the 12 capitals.\n")
    for m in MODELS:
        for p in sorted((OUT / m).glob("inject*.json")) if (OUT / m).exists() else []:
            r = load(p)
            for l, res in sorted(r["layers"].items(), key=lambda kv: int(kv[0])):
                s = res["summary"]
                print(f"### {m} L{l} ({p.name}; {r['n_fillers']} fillers x {len(r['countries'])} countries; alpha in units of ||h_l||={res['h_norm_mean_at_inject']:.1f}); baseline top1 {s['baseline_top1_among_capitals']:.2f}; natural-prompt ceiling lift {s['natural_minus_baseline']:+.2f}\n")
                print("| direction | alpha | lift correct | lift others | specific | top1 among capitals |")
                print("|---|---|---|---|---|---|")
                for dirn in ("lens", "unembed", "random"):
                    for a in r["alphas"]:
                        q = s[f"{dirn}_a{a:g}"]
                        print(f"| {dirn} | {a:g} | {q['mean_lift_correct']:+.2f} | {q['mean_lift_others']:+.2f} | {q['specific_lift']:+.2f} | {q['top1_among_capitals']:.2f} |")
                print()
                print("Per country (base logp / natural logp / baseline top1; specific lift at alpha=4 for lens, unembed, random):\n")
                print("| country | base | natural | top1 | lens | unembed | random |")
                print("|---|---|---|---|---|---|---|")
                for c, q in res["countries"].items():
                    a = "4"
                    print(f"| {c} | {q['baseline_logp']:.2f} | {q['natural_logp']:.2f} | {q['baseline_top1_among_capitals']:.2f} | {q[f'lens_a{a}']['lift_correct'] - q[f'lens_a{a}']['lift_others']:+.2f} | {q[f'unembed_a{a}']['lift_correct'] - q[f'unembed_a{a}']['lift_others']:+.2f} | {q[f'random_a{a}']['lift_correct'] - q[f'random_a{a}']['lift_others']:+.2f} |")
                print()


def section_sparse():
    print("## Sparse decomposition (nonnegative OMP, k atoms): fraction of ||h_l||^2 explained\n")
    print("| model | layer | k | lens: room / library | unembed: room / library | random dict: room / library |")
    print("|---|---|---|---|---|---|")
    atoms = []
    for m in MODELS:
        for p in sorted((OUT / m).glob("sparse*.json")) if (OUT / m).exists() else []:
            r = load(p)
            for l, res in sorted(r["layers"].items(), key=lambda kv: int(kv[0])):
                f = res["fractions"]
                print(f"| {m} | {l} | {r['k']} | {f['lens']['room_mean']:.3f} / {f['lens']['stored_mean']:.3f} ± {f['lens']['stored_std']:.3f} | {f['unembed']['room_mean']:.3f} / {f['unembed']['stored_mean']:.3f} | {f['random']['room_mean']:.3f} / {f['random']['stored_mean']:.3f} |")
                atoms.append((m, l, res["room"]))
    print()
    for m, l, room in atoms:
        print(f"**{m} L{l}** lens atoms at the final `:` of each room prompt (coefficient):  ")
        for e in room:
            print(f"- {e['prompt']} {e['kind']} ({e['explained']:.3f}): " + " ".join(f"`{t}`:{c:.1f}" for t, c in e["atoms"]))
        print()


if __name__ == "__main__":
    which = sys.argv[1:] or ["check", "lens", "readout", "inject", "sparse"]
    for w in which:
        globals()[f"section_{w}"]()
