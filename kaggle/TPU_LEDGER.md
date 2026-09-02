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
| 2026-09-01 22:20 | h-ghost-h1jax-trunk-seed-1 | v1 | 76 | COMPLETE 23:36: seed-1 replicate trunk, 4 epochs, SSD v2 |
| 2026-09-01 23:36 | h-ghost-h1jax-leaf-s1-e1 | v1 | 9 | COMPLETE: seed-1 cooled epoch-1 leaf, val 3.285 → 3.235 (seed 0: 3.234) |
| 2026-09-01 23:50 | h-ghost-h1jax-leaf-s1-e4 | v1 | 9 | COMPLETE: seed-1 cooled epoch-4 leaf, val 3.164 → 3.134 (seed 0: 3.136) |
| 2026-09-02 00:38 | h-ghost-gpu-room-eval (GPU) | v1 | 5 | ERROR: P100 unsupported by image torch + cuda_sync recursion |
| 2026-09-02 00:48 | h-ghost-gpu-room-eval (GPU) | v2 | ~210 | LOST: ran ~3.5 h over the 91M checkpoints, then v3 was pushed while it ran and its output is not retrievable | evaluator over 91M trunk + leaves + 0.5B base; GPU quota |
| 2026-09-01 23:59 | h-ghost-h1jax-trunk-mir | v1 | 39 | COMPLETE: MIR 0.4 at 32x512, one epoch, val 3.279 (plain 64x512 trunk at the same 374M tokens: 3.280); 194K tok/s. No gain at 2x compute. |
| 2026-09-02 00:39 | h-ghost-h1jax-profile-gate-0-5b | v1 | 37 | **PASS** 0.5B: 16x512 remat 100,191 tok/s, 22.0% MFU, one 417M-token pass ~70 min; 8x512 93.5K, 32x512 93.4K (94% HBM); compile ~7 min/shape; base eval on the fixed slice 3.490 (91M base 3.746); sanity 30 steps finite |
| 2026-09-02 01:19 | h-ghost-h1jax-room05b-e1 | v1 | 68 | **COMPLETE** 02:25: 0.5B one epoch on corpus-v1.2-room v2, 131K tok/s; library val 3.423 -> 2.893, room val 3.240 -> 2.609, fixed-32 3.490 -> 3.021; checkpoints at 375.8M (pre-cooldown) and 417.5M (cooled) |
| 2026-09-02 03:20 | h-ghost-h1jax-room05b-e2 | v1 | 66 | **COMPLETE** 04:12: second epoch of the room mix from the e1 pre-cooldown checkpoint, cooled; library 2.893 -> 2.858, room 2.609 -> 2.582, fixed-32 3.021 -> 3.016; 131K tok/s |
| 2026-09-02 02:27 | h-ghost-gpu-room-eval (GPU) | v3 | ~60 | COMPLETE: 0.5B base + e1 pre-cooldown + e1 cooled on a T4; agrees with hbox and the TPU to 4 decimals |
| 2026-09-02 04:12 | h-ghost-h1jax-room05b-e2-v3 | v1 | 66 | **COMPLETE** 05:38: second epoch on corpus-v1.3-room (scenes A x6 + B x8) from the e1 pre-cooldown; library 2.852 (e2 2.858), room 2.581 (2.582), fixed-32 3.011 (3.016); 131K tok/s |
| 2026-09-02 04:44 | h-ghost-gpu-room-eval (GPU) | v4 | ~95 | COMPLETE: e2 pre-cooldown + cooled on a T4; agrees with hbox/TPU (2.858 / 2.628 / 3.142, room 2.582) |
| 2026-09-02 05:55 | h-ghost-h1jax-room05b-e3 | v1 | 66 | **COMPLETE** 07:20: third epoch on v1.3 from the e2-v3 pre-cooldown; library 2.848 (e2-v3 2.852), room 2.576 (2.581), fixed-32 3.019 (3.011); train loss 2.35 vs 2.48: the train/val gap opens (0.37 -> 0.50). Diminishing returns; stop at two epochs. |
| 2026-09-02 04:46 | h-ghost-gpu-room-eval-91m (GPU) | v1 | ~195 | COMPLETE 08:0x: 91M base + trunk (8) + leaves (2) on a T4; the room-loss column: base 3.578, trunk 3.68, leaf-e4 3.664 (library epochs made the 91M worse at room text) |
| 2026-09-02 07:08 | h-ghost-gpu-room-eval (GPU) | v5 | ~55 | COMPLETE: e2-v3 pre-cooldown + cooled on a T4 |
| 2026-09-02 14:43 | h-ghost-h1jax-room05b-w-hup / w-roomdown / w-honly | v1 | (queued, est 3x66) | response-span weighting arms at matched compute to e2-v3: h x8; visitors x0.25 + h x4; visitors x0 + h x4 |
| 2026-09-02 15:01 | h-ghost-h1jax-room05b-w-hup | v1 | 7 | ERROR: attached dataset v2 (pushed seconds after the v3 upload, before the version was live): train-weights.bin missing; re-pushed |
