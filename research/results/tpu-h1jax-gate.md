# h1jax on Kaggle TPU v5e-8: profile gate

Date: 2026-09-01 (evening). Kernel `emberian64/h-ghost-h1jax-tpu-profile-gate`, source
`kaggle/tpu_h1jax_profile_gate/run.py`, wheel `hghost_jax-0.1.4`. Raw report and logs in
[`tpu-h1jax-gate/`](tpu-h1jax-gate/). Ledger: `kaggle/TPU_LEDGER.md`.

## Outcome

The exact `h1jax` Falcon-H1-Tiny port trains on the full v5e-8 slice at **219,722 tokens/s** (median of 20
asynchronously dispatched warm steps; five synchronized steps all 1.204-1.205 s), i.e. **9.5% MFU, 149
TFLOP/s**, at global batch 512 × 512 tokens (64 sequences per chip) with per-layer rematerialization.
One 374.4M-token corpus pass is **28 minutes** of warm compute. The EasyDeL smoke earlier the same day
measured 9.7K tokens/s on the same hardware.

| Shape (per chip × seq) | Remat | Result |
|---|---|---|
| 16 × 512 | no | OOM at compile: program needs 24.42 GB of 15.75 GB HBM |
| 32 × 512 | no | OOM at compile: 48.67 GB |
| 8 × 1024 | no | OOM at compile: 28.89 GB |
| **64 × 512** | **yes** | **compile 186.5 s; temp 8.43 GB; 219,722 tok/s; finite losses** |

Without rematerialization the saved activations are about 3 MB per token (many intermediates are FP32:
SSD internals, RMSNorm, gates, and the FP32 logits), so remat is mandatory at this model's footprint;
with it, 64 × 512 uses 55% of HBM and larger per-chip batches are possible.

## Parity

Base checkpoint on the first 32 × 512 validation sequences: loss **3.7458**, accuracy 34.99%, against hbox's
Transformers BF16 measurement of 3.7456 / 34.94% (`hbox-cpt-10m.md`). Gate v1 (unrolled layers) measured
3.7456 exactly; the scan-over-layers forward differs by 2e-4, within BF16 accumulation noise (the FP32
unit test agrees to 1e-5).

## Where the time goes (64 × 512 per chip, forward + backward, per layer)

| Component | ms | Share of a 1.19 s step (× 24 layers) |
|---|---:|---:|
| Mamba mixer, total | 28.4 | 57% |
| of which SSD chunked scan | 26.6 | 54% |
| attention (GQA, masked, seq 512) | 5.4 | 11% |
| MLP | 1.1 | 2% |
| embedding + LM head + loss (once) | 24.4 | 2% |
| plain BF16 matmul roofline (in_proj shape) | 0.43 | 1,050 TFLOP/s = 66% of peak |

The matrix units are fine. The chunked SSD (per-head 32 × 64 einsums, FP32 segment sums) is the entire
optimization target; a Pallas kernel for it, or reshaping the per-head products into MXU-friendly blocks,
is the next 2-4× if we ever need it. Everything else is already near its floor.

## Loss sanity

40 steps at LR 3e-5 (10.5M tokens, 47 s of compute) took the fixed 32-sequence validation loss from
3.7458 to **3.4113** (accuracy 34.99% → 39.42%), with max gradient norm 68 before clipping and every loss
finite. hbox's 10M-token BF16-state checkpoint reached 3.6160 on the same slice. This slice is
furniture-heavy (see `haunting-index.md`), so treat the absolute drop as an upper bound on learning.

## Gate v1 (unrolled layers)

Reached the same base-eval parity, then the host killed the process while compiling the Python-unrolled
24-layer training step (eval compile alone took 73 s vs 10 s with the scan). The 0.5B smoke earlier that day
died the same way at 36 unrolled layers. Host RAM was not the constraint (405 GB, cgroup 354 GB). The fix
is `layer_scan=True` in `h1jax` 0.1.4.

## What this changes

- One pass costs ~0.5 TPU-hour including compile and checkpoints; the 20-hour weekly quota is ~35 passes.
- Multi-epoch trunks, cooled leaves, replicates, MIR/replay/weight-decay arms, and a 0.5B pilot are all
  affordable this week (`FABLETHOUGHT.md` section 5; `OVERNIGHT-2026-09-01.md`).
- The Mac MLX path (12.7-15K tok/s) is a fallback again, not the mainline.

## Profiler trace, 64 × 512 per chip (3 steps, TPU:0, XLA Ops thread)

Aggregated from the `jax.profiler` trace the gate wrote (`trace.json.gz`; the `while` wrapper of the layer
scan overlaps its children and is excluded). Per step of 1.19 s:

| Category | Share | Note |
|---|---:|---|
| convolution fusion (MXU matmuls, incl. SSD einsums) | 38% | 3,969 fusions / 3 steps |
| data formatting (copy, reshape, transpose) | 20% | chunking reshapes and the 24× head-repeat of B/C |
| loop fusion (elementwise) | 12% | gates, decays, norms |
| reduce-window | 6.5% | the `segment_sum` cumulative sums |
| output fusion | 6% | |
| copy-done / slice / async | ~3% | |
| all-reduce (gradients, 8 chips) | 0.25% | data parallelism is free at this size |

Reading: the matrix units are busy for well under half the step, and about a quarter of the step is
memory traffic that exists only because of how the chunked SSD is written (materialized `jnp.repeat` of the
group state across 24 heads, chunk reshapes, cumsum-based segment sums). A rewrite of `ssd_forward` that
broadcasts B/C inside the einsums instead of repeating them, computes segment sums with a triangular
matmul, and keeps chunk tensors in the layout the MXU wants is the cheapest next 15-25%; a Pallas kernel is
the step after that. Neither is needed for tonight's runs.

## SSD implementations on the full training step (bench kernel, 22:04)

Same shape as the trunk (64 × 512 per chip, remat, layer scan), 15 asynchronously dispatched warm steps
after 3 warm-ups; the first-batch loss is identical across variants to four decimals.

| Variant | tok/s | MFU | step | bare SSD fwd+bwd, one layer |
|---|---:|---:|---:|---:|
| v1 (reference chunked form) | 219,716 | 9.5% | 1.193 s | 24.4 ms |
| **v2** (group-shaped B/C, cumsum decay, two matmuls, chunk scan) | **359,360** | **15.5%** | 0.729 s | 7.2 ms |
| v2 + bf16 matmul inputs | 369,196 | 15.9% | 0.710 s | 6.4 ms |
| v2 + selective remat (keep batch-free dot outputs) | 338,226 | 14.6% | 0.775 s; temp 21.9 GB | |

One corpus pass is now ~17 minutes. v2 (fp32 matmul inputs) is the default for every run after the
seed-0 trunk (`HGHOST_CPT_SSD=v2`); the bf16 variant's 3% is not worth a precision question. A fused
kernel remains the route past this.
