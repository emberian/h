# h1jax TPU profile gate

A measurement kernel for the exact `h1jax` Falcon-H1-Tiny port on Kaggle TPU v5e-8. It does not
train anything durable. For each shape in `HGHOST_GATE_SHAPES` (default `16x512,32x512,64x512r,8x1024`;
`r` = per-layer rematerialization) it:

1. compiles the full FP32-master / BF16-compute AdamW step under explicit SPMD sharding
   (parameters and optimizer state replicated, batch sharded over the eight chips, donated buffers);
2. records XLA's memory and cost analysis before executing, so an OOM is predicted, not discovered;
3. times warm steps both synchronously (spread) and with asynchronous dispatch (the production number);
4. writes a short `jax.profiler` trace for offline analysis.

It then micro-benchmarks the step's components at the best shape (attention, Mamba mixer, SSD scan,
MLP, embedding/head/loss, and a plain BF16 matmul roofline), checks the base checkpoint's validation
loss on the same 32 × 512 slice hbox measured (`research/results/hbox-cpt-10m.md`), and runs a few
real-learning-rate steps to confirm the loss moves.

MFU is computed from analytic FLOPs (6N plus attention and SSD terms) against 197 TFLOP/s per chip.

`HGHOST_LAYER_SCAN=1` (default) runs the 24 decoder layers as one `lax.scan` over stacked parameters
(`h1jax` 0.1.4, `layer_scan=True`), which keeps trace and compile cost independent of depth. Version 1 of this
kernel (2026-09-01 19:03, unrolled layers) reproduced the hbox base validation loss to four decimals
(3.7456) and was then `Killed` by the Kaggle host while compiling the unrolled 24-layer training step; the
`memory` events in the log now record host and cgroup limits around every compile.

Local rehearsal on CPU with eight simulated devices (no TPU minutes):

```sh
HGHOST_LOCAL=1 JAX_PLATFORM_NAME=cpu XLA_FLAGS=--xla_force_host_platform_device_count=8 \
HGHOST_BASE_DIR=kaggle/base_model_dataset_public HGHOST_CORPUS_DIR=artifacts/tokenized \
HGHOST_OUTPUT=/tmp/h1jax-gate HGHOST_GATE_SHAPES=2x64,2x64r HGHOST_GATE_STEPS=2 \
HGHOST_GATE_WARMUP=1 HGHOST_GATE_SYNC_STEPS=1 HGHOST_PROFILE_STEPS=1 HGHOST_BENCH_ITERS=2 \
HGHOST_SANITY_STEPS=3 HGHOST_EVAL_SEQUENCES=8 .venv-jax/bin/python kaggle/tpu_h1jax_profile_gate/run.py
```

Launch:

```sh
uvx --from kaggle kaggle kernels push -p kaggle/tpu_h1jax_profile_gate
uvx --from kaggle kaggle kernels status emberian64/h-ghost-h1jax-tpu-profile-gate
uvx --from kaggle kaggle kernels output emberian64/h-ghost-h1jax-tpu-profile-gate -p /tmp/h1jax-gate-out --force
```

Success marker: `TPU_H1JAX_PROFILE_GATE_OK`. The report is `h1jax-profile-gate-report.json`.
Record every launch in `kaggle/TPU_LEDGER.md`.
