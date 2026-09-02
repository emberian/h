# h1jax CPT 91M (Kaggle TPU v5e-8)

Resumable full-weight continued pretraining of `Falcon-H1-Tiny-90M-Base` on sealed corpus-v1 using the
exact `h1jax` port: FP32 master parameters and AdamW moments, BF16 compute, explicit SPMD sharding
(parameters replicated, batch sharded across the eight chips), asynchronous dispatch, developmental
checkpoints with optimizer state, and a wall-clock budget guard.

Shape and schedule come from environment variables (defaults in `run.py`): `HGHOST_CPT_PER_CHIP`,
`HGHOST_CPT_SEQ`, `HGHOST_CPT_REMAT`, `HGHOST_CPT_TOTAL_TOKENS`, `HGHOST_CPT_LR`, `HGHOST_CPT_WARMUP_TOKENS`,
`HGHOST_CPT_SAVE_TOKENS`, `HGHOST_CPT_EVAL_EVERY_TOKENS`, `HGHOST_CPT_MAX_MINUTES`, `HGHOST_CPT_SEED`,
`HGHOST_CPT_RUN_NAME`, `HGHOST_CPT_SCHEDULE` (`cosine` or `wsd`), `HGHOST_CPT_DECAY_TOKENS` (wsd: decay over the
last N tokens; 0 = a trunk that never decays), `HGHOST_CPT_BRANCH_FROM` (a trunk checkpoint directory: start a
NEW run that continues the trunk's data order and optimizer moments but has its own name, total, and decay;
this is the "one stable trunk, many cooled leaves" pattern from `FABLETHOUGHT.md`). Multi-epoch training is
simply `HGHOST_CPT_TOTAL_TOKENS` larger than the corpus; the token stream reshuffles each epoch with a new
deterministic permutation. `HGHOST_CPT_MIR_WEIGHT` > 0 adds masked-input regularization (a second forward on
inputs corrupted at a per-sequence ratio drawn from [0, `HGHOST_CPT_MIR_MAX_RATIO`], targets unchanged, mask id
`HGHOST_CPT_MIR_MASK_ID` = `<|pad|>`), roughly doubling step arithmetic; the logged `loss` stays the clean NTP loss so
arms remain comparable, and `total_loss`/`mir_loss` are logged beside it. Kaggle script kernels cannot take
environment variables from the CLI, so set
them at the top of `run.py` (or via `os.environ` edits) before pushing; the pushed source is hashed into
every checkpoint's `trainer_state.json` as `code_sha256`.

Outputs under `/kaggle/working/<run name>/`:

- `run-manifest.json`: config, hashes, schedule, resume source;
- `tokens-<n>/`: HF-loadable `model.safetensors` (FP32) + `config.json` + tokenizer files +
  `optimizer.msgpack` + `trainer_state.json`, at each save threshold, at the end, on a budget stop
  (`label: budget`), or on a non-finite metric (`label: nonfinite`);
- `training-complete.json` or `training-paused.json`.

Resume across sessions: attach the previous run's kernel output as a `kernel_sources` entry; the script
selects the highest-token `trainer_state.json` with the same `run_name` and matching settings.

Local rehearsal (CPU, eight simulated devices, tiny budget), including a save/resume round trip:

```sh
export HGHOST_LOCAL=1 JAX_PLATFORM_NAME=cpu XLA_FLAGS=--xla_force_host_platform_device_count=8
export HGHOST_BASE_DIR=kaggle/base_model_dataset_public HGHOST_CORPUS_DIR=artifacts/tokenized
export HGHOST_CPT_PER_CHIP=1 HGHOST_CPT_SEQ=64 HGHOST_CPT_TOTAL_TOKENS=4096 HGHOST_CPT_WARMUP_TOKENS=1024
export HGHOST_CPT_SAVE_TOKENS=2048 HGHOST_CPT_EVAL_EVERY_TOKENS=2048 HGHOST_CPT_EVAL_SEQUENCES=16
export HGHOST_CPT_FIXED_EVAL_SEQUENCES=8 HGHOST_CPT_LOG_STEPS=1 HGHOST_CPT_RUN_NAME=local-smoke
HGHOST_CPT_OUTPUT=/tmp/h1jax-cpt-a HGHOST_CPT_MAX_MINUTES=1 .venv-jax/bin/python kaggle/tpu_h1jax_cpt/run.py
HGHOST_CPT_OUTPUT=/tmp/h1jax-cpt-b HGHOST_CPT_RESUME_GLOBS=/tmp/h1jax-cpt-a/**/trainer_state.json \
  .venv-jax/bin/python kaggle/tpu_h1jax_cpt/run.py
```

Success markers: `TPU_H1JAX_CPT_OK` (finished) or `TPU_H1JAX_CPT_PAUSED` (budget stop with a resumable
checkpoint). Record every launch in `kaggle/TPU_LEDGER.md`.
