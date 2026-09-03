# h1jax TPU profile gate, Falcon-H1-1.5B-Deep-Base

A copy of `kaggle/tpu_h1jax_profile_gate_05b` pointed at `tiiuae/Falcon-H1-1.5B-Deep-Base` (66 decoder
layers, hidden 1280, vocabulary 65,536, untied embeddings, 1,554,872,208 parameters) and at the room
corpus re-tokenized with its tokenizer (`emberian64/hghost-curated-tokens-v1-3-room-15b`, private). It
does not train anything durable. For each shape in `HGHOST_GATE_SHAPES` (default `4x512r,8x512r,16x512r`;
`r` = per-layer rematerialization) it:

1. compiles the full FP32-master / BF16-compute AdamW step under explicit SPMD sharding
   (parameters and optimizer state replicated, batch sharded over the eight chips, donated buffers);
2. records XLA's memory and cost analysis before executing, so an OOM is predicted, not discovered;
3. times warm steps both synchronously (spread) and with asynchronous dispatch (the production number);
4. writes a short `jax.profiler` trace for offline analysis.

It then micro-benchmarks the step's components at the best shape, evaluates the base checkpoint on the
first 32 x 512 tokens of the 65,536-vocabulary `validation.bin` (there is no hbox Transformers number for
this stream, so `loss_delta_vs_hbox` is null), and runs a few real-learning-rate steps to confirm the loss
moves.

What this copy measures is memory. Replicated per chip: 1.55B FP32 parameters (6.2 GB) plus two AdamW
moments (12.4 GB) is ~18.6 GB before gradients and activations, against 16 GiB of HBM per v5e chip. XLA's
memory analysis runs before the first step, so an infeasible shape is reported as `shape_failed` with
`oom: true` rather than crashing the host; if every shape fails, the report says so and the kernel exits
non-zero. The layer scan (`HGHOST_LAYER_SCAN=1`, default) keeps trace and compile cost independent of the
66-layer depth.

Inputs are verified against `preflight-manifest.json` (model sha256 and parameter count) and
`validation-report.json` (train and validation stream sha256) exactly as in the 0.5B gate.

Local rehearsal on CPU (no TPU minutes). Eight simulated devices would replicate ~25 GB of parameter,
gradient and optimizer buffers per device, so rehearse on one:

```sh
HGHOST_LOCAL=1 JAX_PLATFORM_NAME=cpu XLA_FLAGS=--xla_force_host_platform_device_count=1 \
HGHOST_BASE_DIR=artifacts/kaggle/base_model_15b_deep \
HGHOST_CORPUS_DIR=artifacts/roommix-15b/corpus-v1.3-room-15b \
HGHOST_OUTPUT=/tmp/h1jax-gate-15b HGHOST_GATE_SHAPES=1x64r HGHOST_GATE_STEPS=1 \
HGHOST_GATE_WARMUP=1 HGHOST_GATE_SYNC_STEPS=1 HGHOST_PROFILE_STEPS=0 HGHOST_BENCH_ITERS=1 \
HGHOST_SANITY_STEPS=1 HGHOST_EVAL_SEQUENCES=2 \
PYTHONPATH=jax_training .venv-jax/bin/python kaggle/tpu_h1jax_hbm_probe_15b_deep/run.py
```

Launch (private kernel; the room corpus is private because its stream detokenizes to text):

```sh
uvx --from kaggle kaggle kernels push -p kaggle/tpu_h1jax_hbm_probe_15b_deep
uvx --from kaggle kaggle kernels status emberian64/h-ghost-h1jax-hbm-probe-15b-deep
uvx --from kaggle kaggle kernels output emberian64/h-ghost-h1jax-hbm-probe-15b-deep -p /tmp/h1jax-hbm-probe-15b-out --force
```

Success marker: `TPU_H1JAX_PROFILE_GATE_OK`. The report is `h1jax-profile-gate-report.json`.
Record every launch in `kaggle/TPU_LEDGER.md`.
