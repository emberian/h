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
| 2026-09-02 15:01 | h-ghost-h1jax-room05b-w-hup | v1 | 7 | ERROR: attached dataset v2 (pushed seconds after the v3 upload, before the version was live): train-weights.bin missing; re-pushed |
| 2026-09-02 15:08 | h-ghost-h1jax-room05b-w-hup | v2 | 66 | COMPLETE 16:27: h x8; cooled library 2.864, room 2.599, h-span 2.579 (e2-v3 h-span 2.762 on the same slice); hbox 2.864/2.631/3.156 |
| 2026-09-02 16:27 | h-ghost-h1jax-room05b-w-roomdown | v1 | 66 | COMPLETE 17:38: visitors x0.25 + h x4; cooled library 2.854, room 2.635, h-span 2.614, other 2.638 |
| 2026-09-02 17:38 | h-ghost-h1jax-room05b-w-honly | v1 | 66 | COMPLETE 18:50: visitors x0 + h x4; cooled library 2.855, room 2.881 (other 2.884), h-span 2.860: zero visitor weight hurts h too |
| 2026-09-02 18:53 | h-ghost-h1jax-profile-gate-15b-deep | v1 | 130 | CANCELLED 21:01: base eval 3.279 (fixed slice); 4x512r compiled in 755 s then OOM (XLA gathers full weights under automatic sharding), stalled on the next shape until cancelled |
|  | h-ghost-h1jax-room05b-e2-v4 | v1 | 66 | COMPLETE 22:11: second epoch on corpus-v1.4-room (stitched A+B+C); library 2.852 (e2-v3 2.852), fixed-32 3.010 (3.011), room 2.581 (2.581): no loss change from stitching + set C |
| 2026-09-03 09:05 | h-ghost-h1jax-profile-gate-15b-deep | v2 | 105 | CANCELLED 11:21: same OOM at 4x512r program load with per-layer hooks; thread watchdog failed to fire; HBM not instrumented |
| 2026-09-03 11:21 | h-ghost-h1jax-room05b-e2-v5-replay | v1 | 73 | COMPLETE 12:54 (ran past quota; TPU now 21.06/20 h): second epoch on v1.5 (12.5% FineWeb-Edu replay); cooled library 2.857 (e2-v4 2.852), fixed-32 3.016 (3.010), room 2.586 (2.581), h-span 2.569 (2.559). Audit pending. |
| 2026-09-05 00:05 | h-ghost-h1jax-room05b-e2-v6-replay25-lr5e5 (`kaggle/runs/room05b-e2-v6-replay25-lr5e5/spec.json`) | v1 | 85 | (queued Sat 00:05) 25% replay at LR 5e-5, spec kernel: corpus-v1.6-replay25 (v1.4 + 139.6M FineWeb-Edu tokens = 558,548,561; e1 pre-cooldown branch, TOTAL 934,331,985, decay 55,854,856), behind `tpu_h1jax_hbm_probe_15b_deep` in the `hghost-tpu-midnight` queue |
| 2026-09-03 14:43 | h-ghost-t4-cpt-test (GPU) | v1 | 2 | ERROR: landed on a P100 (`--accelerator nvidiaTeslaT4` is silently ignored; the enum is `NvidiaTeslaT4`); image torch 2.10+cu128 has no sm_60 kernels |
| 2026-09-03 14:46 | h-ghost-t4-qlora-test (GPU) | v1 | 2 | ERROR: same P100 misfire |
| 2026-09-03 14:48 | h-ghost-t4-cpt-test (GPU) | v2 | 3 | ERROR on a T4: 90M at 4 x 2048 OOMs (6 GiB block in the pure-PyTorch Mamba scan's backward); step-0 validation ran (library 3.815 / room 3.110 at 16 x 2048) |
| 2026-09-03 14:58 | h-ghost-t4-qlora-test (GPU) | v2 | 15 | ERROR on a T4 after 10 steps: Qwen3.5-2B-Base NF4 QLoRA, val 3.019 -> 3.016, 143 tok/s at emulated bf16, then OOM at 12.6 GB on the 248k-vocab fp32 logits; fixed with a chunked cross-entropy |
| 2026-09-03 15:14 | h-ghost-t4-cpt-test (GPU) | v3 | 29 | **COMPLETE** (T4_CPT_TEST_OK): 90M `--tiny` at 2 x 4 x 2048 fp16, 30 steps / 491k tokens before the 26-min watchdog, 337 tok/s on the pure-PyTorch scan, peak 8.0 GB; bf16 checkpoint reloads (delta 0.003); library val 3.815 -> 3.845, room 3.110 -> 3.161 (mid-warmup) |
| 2026-09-03 15:26 | h-ghost-t4-qlora-test (GPU) | v3 | 19 | ERROR only at `--merge` (image torchao 0.10 vs peft 0.20): 22 steps of Qwen3.5-2B-Base NF4 QLoRA fp32, 195 tok/s, peak 4.6 GB with chunked CE, val 2.922 -> 2.913, adapter 43.7 MB reloads (delta 0.0) |
| 2026-09-03 15:52 | h-ghost-t4-qlora-test (GPU) | v4 | 25 | **COMPLETE** (T4_QLORA_TEST_OK): torchao removed; 28 steps / 228k tokens before the 23-min watchdog, 186 tok/s fp32, peak 4.6 GB; val 2.922 -> 2.911; adapter reloads (delta 0.0); merged into the fp16 base: 2.872 (0.040 nats better than adapter-on-NF4) |
