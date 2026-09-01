# Falcon-H1 distributed-training feasibility and setup

## Outcome

Do **not** run one synchronous model across `nextop.local`, `hbox`, and
`persvati`. There is no stock process group spanning native Apple MLX tensors
and PyTorch ROCm tensors, PyTorch cannot all-reduce an MPS tensor with Gloo,
and the measured home-network synchronization cost overwhelms useful GPU work.

The useful topology is:

1. Gate the Kaggle TPU v5e-8 with the bounded real-token XLA probe in this
   directory. If Falcon-H1's fallback Mamba graph compiles and warmed throughput
   beats the Mac, use all eight TPU devices as the homogeneous primary trainer.
2. Until that gate passes, use the M2 Max as the primary full-weight trainer via
   native MLX.
3. Use `hbox`, `persvati`, and Kaggle T4 for independent controls, data work,
   evaluation shards, and checkpoint selection. Those are parallel experiments,
   **not ranks jointly optimizing one model**.

No long training job and no external Kaggle job was started. Dataset-preparation
files were not modified.

## What is installed and verified

All local paths are isolated from the active dataset workspace.

| Host | Hardware | Environment | Result |
|---|---|---|---|
| `nextop.local` (`192.168.50.130`) | M2 Max, 38 GPU cores, 96 GB, Metal 4 | `/Users/ember/.cache/h1-distributed/venv`; MLX 0.32.2; mlx-lm 0.32.0 from commit `44b42cc137763309b0662284ce12d7a95b8c5d99`; PyTorch 2.9.1 | Native MLX loaded all 91,131,072 BF16 parameters, unfroze all of them, and completed loss/backward/AdamW updates. PyTorch MPS also trains but is unusably slow. |
| `hbox` (`192.168.50.39`) | RX 6750 XT, 12 GB, physical `gfx1031` | `/home/hbox/h1-ghost`; PyTorch `2.9.1+rocm6.3`, HIP `6.3.42134-a9a80e791`, Transformers 4.57.1 | Full-weight BF16 training verified. Requires unofficial `HSA_OVERRIDE_GFX_VERSION=10.3.0`; the first GPU operation fails without it. |
| `persvati` (`192.168.50.120`) | Ryzen AI 9 HX PRO 370, Radeon 890M APU, physical `gfx1150`, 83 GB RAM | `/home/ember/h1-distributed`; PyTorch `2.9.1+rocm6.3`, HIP `6.3.42134-a9a80e791`, Transformers 4.57.1 | Full-weight BF16 training verified only with unofficial `HSA_OVERRIDE_GFX_VERSION=11.0.0`. Current Ubuntu 25.10/system ROCm 6.2.4/wheel combination is outside AMD's supported matrix. |

Every host uses model revision
`7994372e93b62822ae25f8bfb19f653649cea3a3`. The Mac model is at
`/Users/ember/.cache/h1-distributed/models/Falcon-H1-Tiny-90M-Base`, hbox at
`/home/hbox/h1-ghost/models/Falcon-H1-Tiny-90M-Base`, and persvati at
`/home/ember/h1-distributed/models/Falcon-H1-Tiny-90M-Base`.

Current storage is healthy enough for the bounded setups: the Mac environment
and cache use 2.1 GB with about 196 GiB free; hbox's existing environment/cache
uses 23 GB with 54 GiB free on NVMe and 1.5 TiB free on `/tank`; persvati's
environment/cache uses 23 GB with 280 GiB free. Keep hbox corpora and durable
shards under `/tank/joshibot/h1-corpora`, but keep the environment, model, and
active checkpoints on its NVMe.

## Measured training performance

All numbers below are full forward + causal-LM loss + backward + AdamW with
every model parameter trainable. The ROCm paths use Transformers' unfused
fallback Mamba implementation; they do not have the CUDA-only fused
`mamba-ssm`/`causal-conv1d` fast path.

| Host/backend | Shape | Warm rate | Peak memory |
|---|---:|---:|---:|
| Mac / compiled MLX BF16 | b1 s512 | 6,458–6,659 tok/s | 1,246 MiB |
| Mac / compiled MLX BF16 | b1 s1024 | 12,702–15,040 tok/s | 1,676 MiB |
| hbox / PyTorch ROCm BF16 | b1 s512 | 481.0 tok/s | 2.96/3.49 GiB allocated/reserved |
| hbox / PyTorch ROCm BF16 | b1 s1024 | 443.9 tok/s | 5.51/6.58 GiB allocated/reserved |
| persvati / PyTorch ROCm BF16 | b1 s256 | 136.52 tok/s | 1,890/2,006 MiB allocated/reserved |
| Mac / PyTorch MPS BF16 | b1 s16 | about 0.416 tok/s | 837/1,662 MiB allocated/driver |

MLX compilation matters. At s512, the four observed steps took 0.9638, 0.5964,
0.07689, and 0.07928 seconds. At s1024 they took 1.7215, 0.4151, 0.08062,
and 0.06808 seconds. A fresh tiny s8 graph, run while the OCR MLX service was
active, took 10.534 seconds to compile/execute its first step and 0.157 seconds
for its second.

The tiny MLX verification produced global gradient L2 norms 2,046.99 and
1,148.64; 2,916,251 then 4,775,603 BF16 parameter elements changed; the maximum
per-element delta was `6.103515625e-05`; and repeated-batch loss changed from
32.4594 to 15.6947. All 91,131,072 parameters were in the trainable tree. The
large tied embedding contains roughly 66 million elements, so a tiny batch does
not address most embedding rows. BF16 update quantization also means “all
trainable” does not imply every element changes on every optimizer step.

The common rough training-compute heuristic `6 * parameters * tokens` maps the
median warmed s1024 rate to about 7.5 TFLOP/s. That is only a heuristic: Falcon-H1
is a hybrid attention/Mamba model and the benchmark includes framework-specific
compiled behavior. Treat measured tokens/s—not that FLOP conversion—as the
capacity figure. For 267 million tokens, the two warmed MLX context regimes imply
about 5.4–11.3 ideal compute hours for one pass. Real token loading, evaluation,
checkpointing, thermal behavior, and padding will increase that time; do a
real-data gate before scheduling the full run.

## Network and collective results

Direct bounded TCP measurements over the current Wi-Fi:

| Direction | MiB/s |
|---|---:|
| Mac → hbox / hbox → Mac | 20.44 / 16.02 |
| Mac → persvati / persvati → Mac | 14.09 / 6.48 |
| hbox → persvati / persvati → hbox | 12.714 / 7.067 |

A full BF16 gradient contains 91,131,072 elements, or 173.819 MiB. A real
two-rank PyTorch/RCCL all-reduce of exactly that payload between hbox and
persvati succeeded, but took 29.02–29.12 seconds (about 5.97 MiB/s). At s256,
ideal overlap bounds a global 512-token DDP step at no better than about 17.6
tok/s; no overlap gives about 16.5 tok/s. Bucketed Wi-Fi collectives add latency.
This is roughly 26–28 times slower than hbox alone.

To reproduce the two-rank collective, use two terminals after copying
`collective_probe.py` as already installed:

```bash
# hbox, rank 0
source /home/hbox/h1-ghost/env.sh
export NCCL_SOCKET_IFNAME=wlo1
export MASTER_ADDR=192.168.50.39 MASTER_PORT=29611 WORLD_SIZE=2 RANK=0
python /home/hbox/h1-distributed/scripts/collective_probe.py
```

```bash
# persvati, rank 1
source /home/ember/h1-distributed/env.sh
export MASTER_ADDR=192.168.50.39 MASTER_PORT=29611 WORLD_SIZE=2 RANK=1
python /home/ember/h1-distributed/scripts/collective_probe.py
```

## Why the proposed joint modes do not help

**Synchronous data parallelism.** MLX's distributed ring reduces MLX arrays;
PyTorch RCCL reduces ROCm tensors. They are not one process group. Stock PyTorch
Gloo raised `NotImplementedError: c10d::allreduce_ not currently implemented for
MPS` in the included two-rank probe. CPU-staging Mac gradients would add copies
and send 173.8 MiB per step over Wi-Fi. Even the homogeneous Linux pair is far
slower than solo training by direct measurement.

**Tensor/FSDP parallelism.** The model fits comfortably on each machine, so
sharding is not needed for memory. Tensor parallelism adds collectives inside
layers, making the slow link more—not less—important. There is also no native
cross-framework autograd between MLX and PyTorch.

**Pipeline parallelism.** A hidden-state boundary can be small (for example,
b1 × s1024 × hidden512 × BF16 is about 1 MiB), so a custom hbox/persvati-only
pipeline is technically more plausible than DDP. It still excludes the Mac,
requires manually splitting a hybrid model with tied embeddings/output head,
and is throughput-limited by the slow APU and pipeline bubbles. The Mac's
measured native path is tens of times faster, so that engineering has no useful
payback. It was not implemented.

**Local SGD / FedAvg.** With one local plain-SGD step from identical weights,
averaging post-step weights can equal an averaged-gradient step. That equivalence
does not hold for independent AdamW states, and multiple local steps are a
different optimization algorithm. Weight-only averaging while leaving moments
local is particularly unsafe. Cross-framework averaging also requires a tested
inverse conversion because mlx-lm transposes Falcon-H1 convolution weights and
folds model multipliers during sanitization. A BF16 weight exchange alone is
173.8 MiB; parameters plus optimizer moments cost several times that. Periodic
averaging can be a research experiment, but it is not a speed-preserving
substitute for centralized pretraining here.

## Kaggle: TPU v5e-8 gate, T4 fallback, P100 caveat

The user's TPU v5e-8 entitlement is 20 hours/week. Its quoted ~1.5 PFLOP/s is a
system theoretical BF16 figure, not an expected Falcon-H1 rate. Falcon-H1 uses
Mamba operations. Transformers falls back to a generic PyTorch implementation
when CUDA-specific kernels are unavailable; XLA must lower and compile that
graph successfully before the TPU can be considered primary.

Prepare a bounded real-token file locally or in the notebook:

```bash
python prepare_probe_tokens.py \
  --jsonl /kaggle/input/H1_DATASET/probe.jsonl \
  --output /kaggle/working/falcon_probe_tokens.npy \
  --max-records 256 --max-tokens 32768
```

In a Kaggle TPU notebook, keep the preinstalled matching `torch`/`torch_xla`
pair and install only the model dependency:

```bash
python -m pip install 'transformers==4.57.1' numpy
PJRT_DEVICE=TPU PT_XLA_DEBUG=1 python kaggle_tpu_probe.py \
  --tokens-npy /kaggle/working/falcon_probe_tokens.npy \
  --devices 1 --batch-size 1 --seq-len 256 --steps 3
```

The script requires real token IDs, checks that all parameters are trainable,
checks finite nonzero gradients, synchronizes execution for honest compile and
warmed timing, and prints the XLA metrics report. Stop on an unsupported-op,
compile explosion, OOM, repeated recompilation, or a warmed rate below the Mac.
Only after the single-device gate passes, spend a second bounded run on all
eight local TPU devices:

```bash
PJRT_DEVICE=TPU PT_XLA_DEBUG=1 python kaggle_tpu_probe.py \
  --tokens-npy /kaggle/working/falcon_probe_tokens.npy \
  --devices 8 --batch-size 1 --seq-len 512 --steps 3
```

This eight-device TPU job is genuine synchronous training inside a homogeneous,
high-bandwidth slice. Do not add the home machines as WAN ranks. If PyTorch/XLA
cannot lower the Falcon-H1 graph, the next route is a JAX/Flax Falcon-H1 port plus
a carefully validated checkpoint converter; that is a new implementation, not a
small launcher change.

For GPU quota, prefer T4 for independent FP16 control runs and evaluation. T4
does not offer the BF16 path used by the base model, so validate FP16 stability.
P100 also requires FP16/FP32 and, as of the current official Kaggle CLI docs, the
default Kaggle PyTorch CUDA 12.8 image omits Pascal `sm_60`; it fails on the first
CUDA operation unless a Pascal-compatible PyTorch build is installed. Installing
that older stack consumes time and creates another compatibility island, so T4
is the lower-friction fallback.

## Practical parallel schedule

| Worker | Job | Same jointly trained model? |
|---|---|---|
| TPU v5e-8, if gate passes | Primary full-weight run across the eight TPU devices | Yes, within the TPU slice only |
| M2 Max | Primary MLX run, or seed/LR control if TPU wins | No relative to TPU |
| hbox | Short Transformers controls; checkpoint-load and loss checks; validation shard | No |
| persvati CPU/APU | Dataset validation/tokenization; validation shard; short smoke controls | No |
| Kaggle T4 | Independent FP16 LR/seed run or evaluation shard | No |

Validation sharding is exact when every worker emits additive
`negative_log_likelihood_sum`, `predicted_token_count`, and optionally
`correct_token_count`. Combine those JSON files with `aggregate_eval.py`; never
average per-shard perplexities directly.

MLX checkpoints are not automatically Hugging Face checkpoints. The native
Falcon-H1 loader sanitizes layouts and muP multipliers. Keep selection/evaluation
in MLX until an MLX→Transformers converter has been round-trip tested on logits,
loss, and generation. This is a gating item before delegating MLX checkpoint
evaluation to hbox or Kaggle.

## Reusable files

- `mlx_full_benchmark.py`: full-model MLX loss/backward/AdamW benchmark with
  gradient norm and parameter-delta checks.
- `pytorch_full_benchmark.py`: full-model ROCm benchmark used on Linux.
- `collective_probe.py`: exact two-rank BF16 GPU all-reduce benchmark.
- `mps_gloo_probe.py`: minimal reproducer for unsupported MPS Gloo all-reduce.
- `kaggle_tpu_probe.py`: bounded real-token PyTorch/XLA gate for one or eight TPU
  devices.
- `prepare_probe_tokens.py`: deterministic small real-text token-file builder.
- `aggregate_eval.py`: exact aggregation of additive validation metrics.
- `env_*.sh`: environment references for the three home machines.
- `measurements.json` and `topology.json`: machine-readable results and roles.

## Primary references

- [PyTorch distributed backends and capability table](https://docs.pytorch.org/docs/2.9/distributed.html)
- [PyTorch MPS backend notes](https://docs.pytorch.org/docs/2.9/notes/mps.html)
- [MLX distributed communication](https://ml-explore.github.io/mlx/build/html/usage/distributed.html)
- [MLX-LM Falcon-H1 implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/falcon_h1.py)
- [PyTorch/XLA 2.8 documentation](https://docs.pytorch.org/xla/release/r2.8/index.html)
- [Correct XLA compile versus execution timing](https://docs.pytorch.org/xla/master/learn/trace-vs-execution-time.html)
- [AMD Ryzen Linux support matrix](https://rocm.docs.amd.com/projects/radeon-ryzen/en/docs-7.0.2/docs/compatibility/compatibilityryz/native_linux/native_linux_compatibility.html)
- [Official Kaggle accelerator metadata and current P100 warning](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels_metadata.md)
