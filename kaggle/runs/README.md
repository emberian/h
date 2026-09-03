# Kaggle TPU runs: one kernel, many specs

A run used to be a copy of `kaggle/tpu_h1jax_cpt/run.py` (1,100 lines) with its `HGHOST_CPT_*` defaults
rewritten by `kaggle/make_leaf_kernel.py`; thirty such directories accumulated. Since `hghost_jax` 0.2.0
the kernels live in the wheel and a run is a spec:

- `h1jax.kernels.cpt.main(spec)` is the continued-pretraining kernel (the former `tpu_h1jax_cpt/run.py`);
- `h1jax.kernels.gate.main(spec)` is the profile gate (the former `tpu_h1jax_profile_gate_15b_deep/run.py`);
- `jax_training/h1jax/kernels/common.py` holds `CPT_SETTINGS` and `GATE_SETTINGS`: every key with its
  default, which are the old `HGHOST_CPT_<KEY>` / `HGHOST_GATE_<KEY>` (and `HGHOST_<KEY>`) names without
  the prefix, lower-cased, with the same default strings.

Kaggle pushes exactly one code file per script kernel, so each run directory here holds:

| file | what it is |
|---|---|
| `spec.json` | the run: `{"kind": "cpt", ...settings that differ from the defaults}` |
| `run.py` | ~40 lines: finds and pip-installs the wheel from the attached code dataset, sets the two h1jax import-time variables (`H1JAX_SSD`, `H1JAX_REMAT_POLICY`) from the spec, holds the same spec as a JSON literal, calls `main(SPEC)` |
| `kernel-metadata.json` | slug, title, datasets, kernel sources (a branch or resume attaches the previous run's output here) |

`run.py` is generated; edit the spec and regenerate rather than editing it.

## Declaring and generating a run

```sh
python3 kaggle/spec_kernel.py --name room05b-e2-v4-lr5e5 --kind cpt \
  --set RUN_NAME=room05b-e2-v4-lr5e5-decay10 --set SSD=v2 --set PER_CHIP=16 --set LR=5e-5 \
  --set 'BRANCH_FROM=/kaggle/input/**/room05b-e1-decay10/tokens-000375783424/trainer_state.json' \
  --set TOTAL_TOKENS=794693880 --set DECAY_TOKENS=41891045 --set SAVE_TOKENS=752802835 \
  --set MAX_MINUTES=120 --set EXTRA_VALIDATION=room-validation.bin \
  --kernel-source emberian64/h-ghost-h1jax-room05b-e1 \
  --dataset-source emberian64/hghost-jax-code-public \
  --dataset-source emberian64/hghost-falcon-h1-0-5b-base-public \
  --dataset-source emberian64/hghost-curated-tokens-v1-4-room
```

writes `kaggle/runs/room05b-e2-v4-lr5e5/` with

```json
{
  "kind": "cpt",
  "run_name": "room05b-e2-v4-lr5e5-decay10",
  "ssd": "v2",
  "per_chip": 16,
  "lr": 5e-05,
  "branch_from": "/kaggle/input/**/room05b-e1-decay10/tokens-000375783424/trainer_state.json",
  "total_tokens": 794693880,
  "decay_tokens": 41891045,
  "save_tokens": [752802835],
  "max_minutes": 120.0,
  "extra_validation": "room-validation.bin"
}
```

The flags are those of `make_leaf_kernel.py` (`--name`, `--set KEY=VALUE`, `--kernel-source`,
`--dataset-source`, `--title` which Kaggle ignores) plus `--kind cpt|gate`, `--private` (the template
`tpu_h1jax_cpt` is the public 91M kernel; the 0.5B arms are private) and `--runs-dir` (for scratch
rehearsals). `--set` values are parsed exactly as the env kernels parsed them (`SAVE_TOKENS=` is the empty
list, `ROLE_WEIGHTS=1,0.25,4,4` a float list, `REMAT=1` a flag) and stored typed. An unknown key, a
malformed value, or a `dataset_sources` list without the code dataset fails at generation, before any TPU
minute is spent. A spec records only what differs from the defaults; the kernel writes the fully resolved
settings (and the spec itself) into the run's `run-manifest.json`.

Gate runs: `--kind gate`, keys `shapes`, `warmup`, `steps`, `sync_steps`, `profile_steps`, `bench_iters`,
`sanity_steps`, `watchdog_minutes`, `max_minutes`, `sanity_lr`, `eval_sequences`, `peak_flops_per_chip`,
`hbm_bytes_per_chip`, `param_sharding`, `output`, and `hbox_base_loss` / `hbox_base_accuracy` (the
hbox Transformers number the per-copy `HBOX_BASE_EVAL` constant used to carry; unset = no comparison).

## Rehearsing on CPU before pushing

Generate a scratch spec with tiny shapes into a scratch directory and run its `run.py` under the local
environment; the same `run.py` runs unchanged on Kaggle (the wheel install and cache directory are skipped
when `HGHOST_LOCAL=1`, and `h1jax` is imported from `PYTHONPATH`):

```sh
python3 kaggle/spec_kernel.py --name rehearsal --runs-dir /tmp/specs \
  --set PER_CHIP=1 --set SEQ=64 --set TOTAL_TOKENS=4096 --set WARMUP_TOKENS=1024 --set SAVE_TOKENS=2048 \
  --set EVAL_EVERY_TOKENS=2048 --set EVAL_SEQUENCES=16 --set FIXED_EVAL_SEQUENCES=8 --set LOG_STEPS=1 \
  --set ROLLOUT_STEPS=0 --set RUN_NAME=local-smoke --set OUTPUT=/tmp/h1jax-cpt-a
HGHOST_LOCAL=1 JAX_PLATFORM_NAME=cpu XLA_FLAGS=--xla_force_host_platform_device_count=8 \
HGHOST_BASE_DIR=kaggle/base_model_dataset_public HGHOST_CORPUS_DIR=artifacts/tokenized \
PYTHONPATH=jax_training .venv-jax/bin/python /tmp/specs/rehearsal/run.py
```

`HGHOST_LOCAL`, `HGHOST_BASE_DIR`, `HGHOST_CORPUS_DIR`, `HGHOST_REQUIRE_TPU` and `HGHOST_LAYER_SCAN` are
still honoured (they were never `HGHOST_CPT_*` settings); they also exist as spec keys `local`,
`base_dir`, `corpus_dir`, `require_tpu`, `layer_scan`. Nothing else is read from the environment: the spec
is the only source of settings, on Kaggle and locally.

## Pushing

The code dataset attached to the kernel must carry a wheel with the kernels (`hghost_jax-0.2.0` or later),
and exactly one `hghost_jax-*.whl` (`run.py` refuses otherwise, as the old kernels did). Until the
0.2.0 wheel is published, a pushed spec kernel fails at `from h1jax.kernels.cpt import main` a minute in.
To publish:

1. `cd jax_training && uv build --wheel` (the version is `jax_training/pyproject.toml`);
2. copy `artifacts/kaggle/code_dataset_v019/` to `artifacts/kaggle/code_dataset_v020/`, delete the 0.1.9
   wheel there, add `jax_training/dist/hghost_jax-0.2.0-py3-none-any.whl`;
3. `uvx --from kaggle kaggle datasets version -p artifacts/kaggle/code_dataset_v020 -m "hghost_jax 0.2.0: kernels in the wheel"`;
4. wait for the new version to show as live before pushing any kernel (the ledger has a run that attached
   the previous version because it was pushed seconds after the upload).

Then, as before: `uvx --from kaggle kaggle kernels push -p kaggle/runs/<name>` for one run, or
`kaggle/tpu_queue.sh <out-root> <wait-slug> kaggle/runs/<a> kaggle/runs/<b> ...` for a sequence (it reads
the slug from `kernel-metadata.json`, so spec directories queue exactly like the old ones).

## Recording

One row in `kaggle/TPU_LEDGER.md` per launch, as now, with the kernel column naming the spec:
`h-ghost-h1jax-<name>` (`kaggle/runs/<name>/spec.json`). The spec is the complete record of what was
asked; the output's `run-manifest.json` (`spec` plus every resolved setting) and the `wheel` event in the
log (the wheel path, hence its version) record what ran. `code_sha256` in `trainer_state.json` and
`hashes.code` in `inputs_verified` are now the sha256 of `h1jax/kernels/cpt.py` inside the installed wheel
rather than of the pushed script, since the pushed script no longer contains the kernel.

## The old directories as specs

Every `kaggle/tpu_h1jax_*` directory stays in place (their outputs on Kaggle are branch sources and the
ledger names them). Read as specs:

| directory | spec |
|---|---|
| `tpu_h1jax_cpt` | `--kind cpt` with no `--set` (`run_name` trunk-wsd-lr1e-4-seed0, 64x512, 4 epochs, wsd, no decay) |
| `tpu_h1jax_trunk_seed1`, `_seed2` | `RUN_NAME=trunk-wsd-lr1e-4-seed<n> SEED=<n> SSD=v2 MAX_MINUTES=240` |
| `tpu_h1jax_trunk_lr3e4` | `RUN_NAME=trunk-wsd-lr3e-4-seed0 SSD=v2 LR=3e-4 TOTAL_TOKENS=374405212 SAVE_TOKENS=100000000,200000000 MAX_MINUTES=60` |
| `tpu_h1jax_trunk_wd03` | `RUN_NAME=trunk-wsd-lr1e-4-wd0.3-seed0 SSD=v2 WEIGHT_DECAY=0.3 TOTAL_TOKENS=374405212 SAVE_TOKENS=100000000,200000000 MAX_MINUTES=60` |
| `tpu_h1jax_trunk_plain32` | `RUN_NAME=trunk-wsd-lr1e-4-seed0-b32 SSD=v2 PER_CHIP=32 TOTAL_TOKENS=374405212 SAVE_TOKENS=10000000,30000000,100000000,200000000 MAX_MINUTES=90` |
| `tpu_h1jax_trunk_mir` | as plain32 with `MIR_WEIGHT=0.4`, `RUN_NAME=trunk-mir0.4-lr1e-4-seed0-b32`, `MAX_MINUTES=120` |
| `tpu_h1jax_leaf_e1_decay10`, `_e4_decay10` | `RUN_NAME=leaf-e<n>-decay10 BRANCH_FROM=/kaggle/input/**/trunk-wsd-lr1e-4-seed0/tokens-<aligned>/trainer_state.json TOTAL_TOKENS=<trunk+10%> DECAY_TOKENS=37440521 SAVE_TOKENS= EVAL_EVERY_TOKENS=5000000 MAX_MINUTES=60`, `--kernel-source emberian64/h-ghost-h1jax-cpt-91m` |
| `tpu_h1jax_leaf_s1_e1`, `_s1_e4` | the seed-1 leaves: as above with `SEED=1 SSD=v2`, branch from `trunk-wsd-lr1e-4-seed1`, kernel source `h-ghost-h1jax-trunk-seed1` |
| `tpu_h1jax_room_e5` | `RUN_NAME=room-e5-decay10 SSD=v2 BRANCH_FROM=.../trunk-wsd-lr1e-4-seed0/tokens-001497620848/... TOTAL_TOKENS=1912620848 DECAY_TOKENS=41500000 SAVE_TOKENS=1871120848 MAX_MINUTES=80 EXTRA_VALIDATION=room-validation.bin` |
| `tpu_h1jax_room05b_e1` | `RUN_NAME=room05b-e1-decay10 SSD=v2 PER_CHIP=16 LR=1e-4 TOTAL_TOKENS=417533162 DECAY_TOKENS=41753316 SAVE_TOKENS=375779846 MAX_MINUTES=300 EXTRA_VALIDATION=room-validation.bin` on the 0.5B base and room datasets |
| `tpu_h1jax_room05b_e2`, `_e2_v3`, `_e2_v4`, `_e2_v4_lr5e5`, `_e2_v5_replay`, `_e3` | second/third epochs branched from the e1 (or e2-v3) pre-cooldown checkpoint; the lr5e5 spec is the example above, the others differ in `RUN_NAME`, `LR`, `TOTAL_TOKENS`, `DECAY_TOKENS`, `SAVE_TOKENS`, `MAX_MINUTES` and the corpus dataset (their `GENERATED.md` lists the exact values) |
| `tpu_h1jax_room05b_w_hup`, `_w_roomdown`, `_w_honly` | the e2-v3 spec plus `ROLE_WEIGHTS=1,1,8,8` / `1,0.25,4,4` / `1,0,4,4` |
| `tpu_h1jax_profile_gate` (91M) | `--kind gate --set SHAPES=16x512,32x512,64x512r,8x1024 --set SANITY_STEPS=40 --set PARAM_SHARDING=replicated --set OUTPUT=/kaggle/working/h1jax-profile-gate --set HBOX_BASE_LOSS=3.745613 --set HBOX_BASE_ACCURACY=0.349426` |
| `tpu_h1jax_profile_gate_05b` | `--kind gate --set SHAPES=8x512r,16x512r,32x512r --set PARAM_SHARDING=replicated --set OUTPUT=/kaggle/working/h1jax-profile-gate-05b` (+ the hbox pair above, which that copy carried) |
| `tpu_h1jax_profile_gate_15b_deep` | `--kind gate` with no `--set` (the gate defaults are this kernel's) |
| `tpu_h1jax_hbm_probe_15b_deep` | `--kind gate --set SHAPES=1x128r,4x512r --set WATCHDOG_MINUTES=15 --set MAX_MINUTES=25` |
| `tpu_h1jax_ssd_bench` | not a spec kernel: a separate SSD-variant benchmark script |
| `tpu_smoke*`, `tpu_train`, `tpu_fresh_*`, `tpu_both_91m`, `tpu_91m_production_gate`, `gpu_*` | not spec kernels: the pre-h1jax smoke, fresh-91M, and GPU evaluation scripts |

The `GENERATED.md` in each generated directory lists its `--set` values verbatim; they are valid `--set`
arguments to `spec_kernel.py` as they stand.

## What differs from the env kernels

The kernel bodies were moved, not rewritten: checked statement by statement against the old modules, and
by CPU rehearsals (plain, role-weighted, FSDP) whose per-step losses match the env kernels. The differences:

- `hashes.code` / `code_sha256` hash `h1jax/kernels/cpt.py` in the installed wheel, not the pushed script.
- `run-manifest.json` (and the gate's report JSON) gain a `spec` field; the `start` event does not carry it.
- The `wheel` event is printed by `run.py` rather than by the kernel; same name and field.
- `H1JAX_SSD` / `H1JAX_REMAT_POLICY` are set by `run.py` before importing `h1jax` (its model module
  reads them at import); the kernel checks that the imported model agrees with the spec and raises
  `RuntimeError` otherwise, instead of silently training with the wrong SSD implementation.
- An unknown spec key raises at `main()`; a misspelt `HGHOST_CPT_*` variable used to be ignored.
- Error messages name spec keys (`branch_from`, `schedule`, `param_sharding`) instead of the env variables.
- The gate's per-copy `HBOX_BASE_EVAL` constant is the `hbox_base_loss` / `hbox_base_accuracy` spec pair.
