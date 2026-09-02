# Kaggle TPU ledger

Kaggle's UI is the only authority for the remaining weekly quota (20 TPU-hours, 9 h per session).
This file records what we launched and what each run cost, estimated from kernel logs, so the
number is never unknown again. Times are America/New_York.

| Date | Kernel | Version | TPU minutes (est.) | Outcome |
|---|---|---:|---:|---|
| 2026-09-01 | h-ghost-falcon-h1-0-5b-tpu-smoke | v1 | 6 | Killed by host at `start`; in hindsight the same failure as the h1jax gate v1: compiling a Python-unrolled deep stack (36 layers) exhausts the host |
| 2026-09-01 | h-ghost-easydel-real-cpt-smoke | v4 | 10 | killed during compilation |
| 2026-09-01 | h-ghost-easydel-real-cpt-smoke | v5 | 3 | `ENABLE_DISTRIBUTED_INIT` failure |
| 2026-09-01 | h-ghost-easydel-real-cpt-smoke | v6 | 50 | complete; 9.7K tok/s at 8 × 1 × 128, ~46 min compiling |
| 2026-09-01 | (CPU-only runs: jax-tpu-smoke, 91m-tpu-experiments) | — | 0 | never allocated a TPU (account not yet TPU-enabled) |

Running total before this session's work: **~69 minutes**.

Authorized budget for the 2026-09-01 overnight session (ember): initially 90 minutes, then at 19:05 EDT
"authorized to just use all 20 hours if you think you have a handle on what you're doing." Working rule:
spend in bounded, reported increments; never launch a run whose worst case exceeds the remaining week.

| Date | Kernel | Version | TPU minutes (est.) | Outcome |
|---|---|---|---:|---|

| 2026-09-01 19:03 | h-ghost-h1jax-tpu-profile-gate | v1 | 11 | TPU acquired; base eval parity 3.7456 = hbox; host `Killed` compiling the unrolled 24-layer train step |
| 2026-09-01 19:25 | h-ghost-h1jax-tpu-profile-gate | v2 | 18 | **PASS**: 64x512 remat 219,722 tok/s, 9.5% MFU, 28 min/pass; no-remat shapes OOM (24-49 GB HBM); base eval 3.7458; 10.5M-token sanity loss 3.75→3.41 |

| 2026-09-01 21:42 | h-ghost-h1jax-leaf-e1-decay10 | v1 | 3 | ERROR: branch glob named the checkpoint by requested tokens, not batch-aligned tokens (fixed) |
| 2026-09-01 19:39 | h-ghost-h1jax-cpt-91m | v1 | 122 | **COMPLETE** 21:41: 4-epoch WSD trunk, 8 checkpoints (analysis pending) |
| 2026-09-01 21:46 | h-ghost-h1jax-leaf-e1-decay10 | v2 | 9 | COMPLETE: cooled epoch-1 checkpoint, val 3.280 → 3.234 |
| 2026-09-01 21:55 | h-ghost-h1jax-leaf-e4-decay10 | v1 | 9 | COMPLETE: cooled epoch-4 checkpoint, val 3.163 → 3.136 |

| 2026-09-01 22:04 | h-ghost-h1jax-ssd-bench | v1 | 15 | **v1 219,716 / v2 359,360 / v2-bf16 369,196 / v2+dotsave 338,226 tok/s**; SSD fwd+bwd 24.4 → 7.2 ms; losses identical |
