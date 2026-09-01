# Falcon-H1 ROCm Triton SSD experiment

Date: 2026-09-01

## Outcome

The RX 6750 XT can train Falcon-H1 through the upstream Mamba-2 Triton SSD scan even though the complete
`mamba-ssm`/`causal-conv1d` compiled fast path is unavailable. The project patch retains PyTorch's grouped
depthwise Conv1d and replaces the extremely slow reference SSD calculation with
`mamba_chunk_scan_combined` from the pinned `mamba-ssm` 2.3.2.post1 source distribution.

The old corpus-v1 run used BF16 parameters, BF16 AdamW moments, and the Transformers reference Mamba path.
The replacement smoke used FP32 parameters and AdamW moments with BF16 autocast compute.

## Environment

| Component | Value |
|---|---|
| GPU | AMD RX 6750 XT, exposed as `gfx1030` through `HSA_OVERRIDE_GFX_VERSION=10.3.0` |
| PyTorch | 2.9.1+rocm6.3 |
| HIP runtime | 6.3.42134 |
| Triton | 3.5.1 from the PyTorch ROCm wheel |
| Mamba source | 2.3.2.post1 sdist |
| Mamba sdist SHA-256 | `104cc47e9101e5401a675fa2b784f2952b9b037f3b1dd83b5ac544394e95d028` |
| Convolution | PyTorch grouped `Conv1d` |
| SSD | upstream `mamba_chunk_scan_combined` Python/Triton implementation |

The PyTorch wheel contained the ROCm Triton compiler but the host lacked Python headers; `python3.12-dev`
was the only system package added. The upstream sdist was unpacked under
`/othersys/h1-ghost/kernel-test` rather than installed into the production environment. `einops==0.8.1` is
the only Python dependency added to the hbox Falcon environment.

## Kernel and layer parity

The standalone H1-shaped SSD forward/backward took 395.25 seconds to compile and autotune on first use. It
then ran in 2.8 ms warm. A formal layer-0 validation compared sequence-256 BF16 outputs, input gradients, and
all parameter gradients with Transformers' reference implementation:

| Measurement | Result |
|---|---:|
| reference mixer forward/backward | 904.8 ms |
| first cached-process Triton call | 13.94 s |
| warm Triton mixer forward/backward | 6.92 ms |
| output relative mean absolute error | 0.2657% |
| input-gradient relative mean absolute error | 0.2354% |
| maximum parameter-gradient relative mean absolute error | 0.3735% |
| gradient keys identical | yes |
| declared tolerance | 1.0% |
| result | pass |

The durable machine report is `/othersys/h1-ghost/kernel-test/h1-layer-parity.json`. The committed validator
can reproduce it.

## Full-model real-token smokes

Every row is the complete 91,131,072-parameter model, forward, loss, backward, clipping, and AdamW update.
The first step includes process-local compilation; throughput below is from later warm steps.

| Parameters/moments | Batch × sequence | Warm tokens/s | Peak allocated/reserved | Projected 374.4M-token pass |
|---|---:|---:|---:|---:|
| BF16, reference SSD | 1 × 512, accumulation 4 | ~489 | 2.96/3.49 GiB in earlier probe | ~212.7 h |
| FP32, Triton SSD | 1 × 256 | 1,604 | not recorded | ~64.9 h |
| FP32, Triton SSD | **1 × 512** | **2,259–2,365** | **2.20/2.35 GiB** | **~44–46 h** |
| FP32, Triton SSD | 4 × 512 | 2,060–2,065 | not recorded | ~50.4 h |
| FP32, Triton SSD | 1 × 1,024 | 1,855–1,856 | not recorded | ~56.0 h |

The best tested shape is batch 1 × sequence 512. Larger parallel batch and longer sequence both reduced
throughput. Gradient accumulation can set the desired optimizer batch without changing this microbatch.

The corrected path is about 4.7–4.8× faster at the matched sequence-512 shape while also improving optimizer
precision. It still does not approach the M2 Max MLX rate or justify making hbox the primary corpus-pass
trainer. It does make hbox useful for independent CPT/optimizer/regularization controls that would otherwise
take more than a week.

## Production decision

- Do not resume the old BF16-state checkpoint as the clean baseline; it has already quantization-frozen
  parameter families.
- Start any scientifically clean hbox branch from the base or another deliberately selected checkpoint with
  FP32 master state.
- Retain the Triton cache, pinned source hash, parity report, and exact patch version.
- Before a long branch, perform checkpoint save/reload parity and a longer loss/finite-value smoke.
- Treat the Transformers “fast path unavailable” warning as expected: the project deliberately uses the
  stepwise ROCm Triton SSD path, not the unavailable fused causal-convolution extension.

## Reusable implementation

- [`hbox_training/rocm_triton_ssd.py`](../../hbox_training/rocm_triton_ssd.py)
- [`hbox_training/validate_rocm_triton.py`](../../hbox_training/validate_rocm_triton.py)
- [`hbox_training/train_hbox.py`](../../hbox_training/train_hbox.py)
