"""Kaggle TPU kernels shipped in the wheel.

A pushed Kaggle script is a ~30-line `run.py` (see `kaggle/spec_kernel.py`) that installs this wheel from
the attached code dataset, sets the two h1jax import-time environment variables, and calls one of:

- `h1jax.kernels.cpt.main(spec)`: resumable continued pretraining (the former `kaggle/tpu_h1jax_cpt/run.py`);
- `h1jax.kernels.gate.main(spec)`: the TPU profile gate (the former `kaggle/tpu_h1jax_profile_gate_*/run.py`).

`spec` is a plain dict whose keys are the old `HGHOST_CPT_*` / `HGHOST_GATE_*` setting names without the
prefix, lower-cased (`total_tokens`, `role_weights`, `param_sharding`, ...); `common.CPT_SETTINGS` and
`common.GATE_SETTINGS` list every key with its default. Values may be typed or the env-style strings.
"""
