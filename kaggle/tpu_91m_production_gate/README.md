> **Superseded 2026-09-01 evening.** Do not push this kernel. Source verification of EasyDeL 0.3.0 showed its
> Falcon-H1 Mamba-2 path is a per-token `lax.scan` with no TPU kernel whose custom VJP pins ~38.7 GB per chip of
> state history at this shape (v5e has 16 GiB). See `FABLETHOUGHT.md` section 2. The replacement is
> `kaggle/tpu_h1jax_profile_gate` (measurement) and `kaggle/tpu_h1jax_cpt` (training) on the exact `h1jax` port.

# 91M TPU production-shape gate

This is the boundary between the successful EasyDeL correctness smoke and a real
continued-pretraining run. It deliberately compiles one static production candidate:

- Falcon-H1-Tiny-90M-Base, replicated over all eight v5e chips;
- 512-token sequences, 128 global sequences, 65,536 real corpus tokens per step;
- BF16 arithmetic with FP32 parameters and FP32 Adam state;
- EasyDeL's TPU-native automatic attention backend;
- no activation rematerialization;
- six optimizer steps, leaving four warm measurements after the two compile-heavy steps seen
  in the first smoke;
- one fixed real validation batch before and after checkpoint reload.

The machine-readable report rejects the run if warm throughput is below 50,000 tokens/s,
state dtypes are wrong, warm steps appear to recompile, the checkpoint cannot restore its
optimizer step, or validation changes across serialization.

The kernel currently enables internet only to install the pinned `easydel==0.3.0` release.
The production pass should move the resolved wheel set into a public input dataset and run
offline after this shape gate passes.
