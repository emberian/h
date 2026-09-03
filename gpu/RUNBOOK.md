# The rented H100 day

Two runs, one box, one day: continued pretraining of Falcon-H1-1.5B-Deep-Base on the replay-woven room
corpus (`gpu/cpt_torch.py`), and the Qwen3.8-27B library adapter (`gpu/qlora_unsloth.py`). Both scripts
were run at small scale on Kaggle's free T4 first (`gpu/kaggle_t4_cpt_test/`, `gpu/kaggle_t4_qlora_test/`;
numbers in section 7), so the rented hours go to training. Nothing here touches the TPU.

Prices below use $2.39/h (the median H100 SXM 80 GB hourly rate on the marketplaces at the time of
writing); adjust the arithmetic, not the plan, if the instance costs something else.

## 0. What exists already (on this Mac)

| thing | where | size |
|---|---|---|
| 1.5B base (HF, bf16, revision e975d35c) | `artifacts/models/falcon-h1-1.5b-deep-base` and Kaggle `emberian64/hghost-falcon-h1-1-5b-deep-base-public` | 3.1 GB |
| the CPT corpus (65,536 vocab, 12.6% replay) | `artifacts/roommix-15b/corpus-v1.5-replay-15b` (built by `research/roommix/make_replay_15b.py`; section 8) and Kaggle `emberian64/hghost-curated-tokens-v1-5-replay-15b` (private) | train.bin 944 MB, validation.bin 4.7 MB, room-validation.bin 2.0 MB |
| Qwen adapter data | `qwen/data/{train,valid}.jsonl` and Kaggle `emberian64/hghost-qwen-library-chunks` (private) | 27 MB |
| the scripts | `gpu/cpt_torch.py`, `gpu/qlora_unsloth.py` and Kaggle `emberian64/hghost-gpu-code` | 50 KB |
| Qwen3.8-27B (instruct; the base is gated, application pending) | Hub `Qwen/Qwen3.8-27B` | 55.6 GB |

Corpus sha256 (`manifest.json`): train.bin `dd78e8b89eabdc11ddbfbc227219ea222e980cdb41a0e3cf3c8bd7275b1db39d`, 471,890,484
tokens, 200,852 documents; validation.bin `ac57f58e0101264aa9870505065cd63deb4373018a704026d216fef024a2b24d` (2,361,018
tokens, byte-identical to corpus-v1.3-room-15b); room-validation.bin `5fed0d61386c9d5d440f5224e463ff3577c201804fcea7987d750aa82fe345a9`.
Base model.safetensors sha256 `d93c5faefd36b79860f82dec1a981f746fe71e79d29ebba1cc4643b1fd6cf4a8`.

## 1. Instance

- **One H100 SXM 80 GB** (not PCIe: the SXM part has 3.35 TB/s HBM3 and the higher clocks; the CPT run is
  memory-bound in the Mamba scan). 80 GB is needed: fp32 master weights + AdamW for 1.5B = 25 GB before
  activations; the 27B in NF4 is 15 GB plus activations at 2048 tokens.
- **A persistent volume of 200 GB** mounted at `/data` (base 3 GB + corpus 1 GB + Qwen 56 GB + four bf16
  checkpoints 12.4 GB + one resumable state 19 GB + adapter + room for a merged 55 GB model if wanted).
  Persistent, so a preempted or restarted instance resumes instead of restarting.
- **Fast network** (>= 1 Gbit/s to the Hub): the Qwen download is the largest transfer of the day.
- CUDA 12.x image with Python 3.11+ (any recent PyTorch image; the pinned wheels below replace its torch
  only if it is older than 2.6). `nvidia-smi` must show the H100 and `nvcc` must exist for the
  `mamba-ssm` build.
- Sanity: `nvidia-smi --query-gpu=name,memory.total,clocks.max.sm --format=csv` and
  `df -h /data`. Start the session clock now.

## 2. Install (15 minutes, most of it the mamba-ssm build)

Two virtual environments, because the Falcon path is pinned to transformers 4.57.6 (the version the
Kaggle T4 test and every evaluator in this repo run) and the Qwen path needs transformers 5.x.

```bash
sudo apt-get install -y tmux git build-essential ninja-build   # if missing
pip install uv
mkdir -p /data/venvs /data/runs /data/models /data/corpus

# --- venv A: Falcon-H1 continued pretraining --------------------------------------------
uv venv /data/venvs/cpt --python 3.11
. /data/venvs/cpt/bin/activate
uv pip install "torch==2.8.*" --index-url https://download.pytorch.org/whl/cu128   # or the image's torch if >= 2.6
uv pip install "transformers==4.57.6" accelerate safetensors numpy
# the fast path (documented in cpt_torch.py): Triton SSD kernels + the causal conv
uv pip install ninja packaging
MAX_JOBS=16 uv pip install --no-build-isolation causal-conv1d      # ~3 min
MAX_JOBS=16 uv pip install --no-build-isolation mamba-ssm          # ~10 min; prebuilt wheels exist for
                                                                   # some torch/CUDA pairs and skip the build
python - <<'EOF'
from transformers.models.falcon_h1 import modeling_falcon_h1 as m
print("fast path:", m.is_fast_path_available)   # must print True before the CPT run
EOF
deactivate

# --- venv B: Qwen QLoRA -----------------------------------------------------------------
uv venv /data/venvs/qlora --python 3.11
. /data/venvs/qlora/bin/activate
uv pip install "torch==2.8.*" --index-url https://download.pytorch.org/whl/cu128
uv pip install "transformers==5.16.1" "peft==0.20.0" bitsandbytes accelerate safetensors numpy
uv pip install flash-linear-attention causal-conv1d   # the Gated DeltaNet fast path (fla); optional, falls back to torch
pip list 2>/dev/null | grep -i torchao && uv pip install "torchao>=0.16"   # peft 0.20 refuses torchao < 0.16 on the merge path; absent is fine
# optional, unverified on our side: uv pip install unsloth   (then --backend unsloth)
deactivate
```

If `mamba-ssm` will not build (a CUDA/torch mismatch is the usual cause), do not spend more than 20
minutes on it: run the 5-minute gate in section 4 and read its `tokens_per_second`; the pure-PyTorch scan
costs several times the wall clock (section 7), so at that point the choice is "fix the build" or "run
half an epoch tonight and the rest tomorrow" (`--resume`). The kernels change speed, not results. The
fallback also eats memory: on the T4 test the 90M at 4 x 2048 asked for a single 6 GiB block in the
scan's backward (OOM on 16 GB; 2 x 2048 fits), so on the fallback path use `--batch 1 --accum 64` or
`--batch 2 --accum 32` for the 1.5B and let the gate's `peak_memory_gb` decide.

## 3. Pull the models and the corpus (10 minutes)

```bash
# base model, pinned revision, from the Hub (fastest); verify the sha256 against the ledger above
. /data/venvs/cpt/bin/activate
hf download tiiuae/Falcon-H1-1.5B-Deep-Base --revision e975d35c1283500d7cd844c0cd9e2c58e30a8db8 \
    --local-dir /data/models/falcon-h1-1.5b-deep-base
sha256sum /data/models/falcon-h1-1.5b-deep-base/model.safetensors   # d93c5fae...

# the corpus: the private Kaggle dataset emberian64/hghost-curated-tokens-v1-5-replay-15b (uploaded from the Mac
# on 2026-09-03; train.bin 943,780,968 bytes listed) ...
pip install kaggle; mkdir -p ~/.kaggle && vi ~/.kaggle/kaggle.json     # {"username": "emberian64", "key": "..."}
kaggle datasets download -d emberian64/hghost-curated-tokens-v1-5-replay-15b -p /data/corpus --unzip
# ... or a tarball from the Mac (the same files; 1.0 GB over rsync):
#   (Mac) tar cf - -C artifacts/roommix-15b corpus-v1.5-replay-15b | ssh h100 "tar xf - -C /data/corpus"
sha256sum /data/corpus/corpus-v1.5-replay-15b/train.bin   # dd78e8b8...

# Qwen and its data
. /data/venvs/qlora/bin/activate
hf download Qwen/Qwen3.8-27B --local-dir /data/models/qwen3.8-27b          # 55.6 GB
kaggle datasets download -d emberian64/hghost-qwen-library-chunks -p /data/qwen-data --unzip
#   or: (Mac) rsync -a qwen/data/ h100:/data/qwen-data/
```

The Kaggle route needs the token on the box; the rsync route needs the Mac awake. Either way verify the
sha256 lines: a truncated `train.bin` trains silently on garbage.

## 4. Run 1: the 1.5B continued pretraining (the day's main cost)

Recipe (defaults of `cpt_torch.py`): one epoch (471.9M tokens), AdamW (0.9, 0.95), weight decay 0.1 on
matrices, peak LR 5e-5 re-warmed over 2% of tokens (9.4M tokens, 72 steps), constant, linear cooldown over
the last 10% to 5e-6, sequence 2048, global batch 8 x 8 x 2048 = 131,072 tokens/step (3,600 steps),
fp32 masters with bf16 autocast, gradient checkpointing, checkpoints at 25/50/75/100% as HF safetensors
(bf16) under `tokens-<n>/`, validation (256 x 2048 tokens each of validation.bin and room-validation.bin)
every 5%, JSON events on stdout and in `events.jsonl`.

**Gate first (5 minutes, ~$0.20).** Same model, same corpus, a few hundred steps, hard stop:

```bash
. /data/venvs/cpt/bin/activate
cd /data/runs
python /data/h/gpu/cpt_torch.py --model /data/models/falcon-h1-1.5b-deep-base \
    --stream /data/corpus/corpus-v1.5-replay-15b/train.bin \
    --validation /data/corpus/corpus-v1.5-replay-15b/validation.bin \
    --room-validation /data/corpus/corpus-v1.5-replay-15b/room-validation.bin \
    --output /data/runs/h15b-gate --tokens 26214400 --validate-every-frac 0.5 --checkpoint-every-frac 0 \
    --validation-windows 64 --max-minutes 5 --reload-check
```

Read three lines of its output: `"event": "hardware"` must say `"fast_path": true`; the `train` events'
`tokens_per_second` (steady state, after step 20) is the day's throughput; `peak_memory_gb` must be under
70. Projected hours for the epoch = 471.9e6 / tokens_per_second / 3600. If the projection exceeds the
session, lower `--validation-windows` (validation is 20 x 2 x 256 windows = 21M forward tokens over the
run) or split the epoch with `--max-minutes` and `--resume` (the resumable state is written in every
scheduled checkpoint; `tokens-*/master.pt` + `optimizer.pt`).

**The run** (inside tmux; it survives a dropped ssh):

```bash
tmux new -s cpt
. /data/venvs/cpt/bin/activate
python /data/h/gpu/cpt_torch.py --model /data/models/falcon-h1-1.5b-deep-base \
    --stream /data/corpus/corpus-v1.5-replay-15b/train.bin \
    --validation /data/corpus/corpus-v1.5-replay-15b/validation.bin \
    --room-validation /data/corpus/corpus-v1.5-replay-15b/room-validation.bin \
    --output /data/runs/h15b-replay-e1 --run-name h15b-replay-e1 \
    --max-minutes 660 2>&1 | tee /data/runs/h15b-replay-e1.log
# follow from another pane:  grep -h '"event": "validation"' /data/runs/h15b-replay-e1/events.jsonl | tail
```

`--max-minutes 660` is the watchdog: at 11 hours it writes a resumable checkpoint and exits 0 rather than
being killed mid-write. A stall (no optimizer step for 20 minutes) exits 3. To resume:
`... --resume /data/runs/h15b-replay-e1/tokens-<n>` (same flags). The final checkpoint is
`tokens-000471859200/` (3,600 steps x 131,072 tokens, batch-aligned like the TPU kernel); the earlier
ones keep only weights unless `--keep-resume-states`.

What good looks like (from the 0.5B line, TPU, 512-token sequences): library val 3.42 -> 2.89 and room
val 3.24 -> 2.61 in one epoch; the 1.5B base sits at 3.28 on the fixed library slice. The 2048-token
validation here reads lower than the 512-token TPU numbers by construction; compare 1.5B checkpoints with
each other and with the base's step-0 `validation` event, and leave cross-family comparisons to the
evaluators in section 6.

## 5. Run 2: the Qwen3.8-27B library adapter (an hour or two)

Recipe (defaults of `qlora_unsloth.py`, from `qwen/RECIPE.md` and `qwen/lora.yaml`): raw text, no chat
template, EOS only where a document ends; LoRA r=16, alpha 16, dropout 0 on `self_attn.{q,k,v,o}_proj` and
`mlp.{gate,up,down}_proj` only (the script enumerates the module names and refuses anything under
`linear_attn`, i.e. the Gated DeltaNet projections, and the vision tower); NF4 base weights; LR 5e-5,
warmup 3% (>= 10 steps), linear decay to 5e-6; sequence 2048; batch 1 x accumulation 4; one epoch of
`train.jsonl` (750 steps); validation on the 100 held-out chunks every 75 steps.

```bash
tmux new -s qlora
. /data/venvs/qlora/bin/activate
python /data/h/gpu/qlora_unsloth.py --model /data/models/qwen3.8-27b --data-dir /data/qwen-data \
    --output /data/runs/qwen38-27b-lib-r16 --max-minutes 240 2>&1 | tee /data/runs/qwen38-27b-lib-r16.log
```

Memory note: the script never materializes the full `[2048, 248,320]` fp32 logits; the lm_head and the
cross-entropy run per `--loss-chunk` (512) positions under activation checkpointing, because the first T4
attempt OOMed on exactly those 2 GB copies (section 7). On the H100 the 27B's peak is dominated by the NF4
weights (~15 GB) and the recomputed layer activations; expect 25-35 GB. `--compute-dtype auto` picks bf16
only where the hardware has it (`is_bf16_supported(including_emulation=False)`; the T4 answers True to the
default call and then emulates bf16 at fp32 speed).

`--backend unsloth` swaps the loader for Unsloth's (their kernels are 1.5-2x faster on Ampere+); it was
NOT exercised on the T4 (Unsloth forces fp32 for Qwen3.5 on fp16-only GPUs, and its API is the moving
part), so use it only after a 20-step trial with `--max-steps 20` reproduces the peft loss curve.

**Merge or not.** The adapter is the product: `adapter/adapter_model.safetensors` (+ config, tokenizer,
`trainer_state.json`). Serving loads base + adapter (transformers/peft on CUDA, or mlx-lm with the adapter
converted; the Mac already serves the community 4-bit MLX base). Do not merge into the NF4 weights (there
is no such thing; merging means a 16-bit base). Merge only if a standalone checkpoint is wanted for
`mlx_lm.convert -q`: `--merge` reloads the base in bf16 (55 GB, fits the H100 next to nothing else),
writes `merged/` (55 GB, ~5 minutes) and reports the merged model's validation loss next to the adapter's;
the difference is the NF4-vs-16-bit mismatch: on the T4 test the merged fp16 2B scored 0.040 nats *better*
than the adapter over NF4 (section 7), so merging into the 16-bit base loses nothing and recovers the
quantization loss; the cost is only the 55 GB of disk and the 16-bit serving footprint. If you merge, push `merged/` to the Hub as a private repo from the box rather
than copying 55 GB to the Mac.

## 6. What to copy back, and where it plugs in

From the box (rsync to the Mac; the Mac has ~90 GB free, so nothing over 20 GB):

```bash
# checkpoints without the resume states (12.4 GB), event logs, configs
rsync -a --exclude 'master.pt' --exclude 'optimizer.pt' --exclude 'scaler.pt' \
    h100:/data/runs/h15b-replay-e1/ artifacts/checkpoints/gpu/h15b-replay-e1/
rsync -a h100:/data/runs/h15b-replay-e1.log artifacts/checkpoints/gpu/h15b-replay-e1/
# the adapter (a few hundred MB) and its events
rsync -a --exclude merged h100:/data/runs/qwen38-27b-lib-r16/ qwen/adapters/qwen38-27b-lib-r16/
# and, from the box, the checkpoints as a Kaggle dataset for the GPU evaluators (and the Hub as backup):
kaggle datasets create -p /data/runs/h15b-replay-e1 --dir-mode skip   # after writing a dataset-metadata.json
hf upload emberian/h-15b-replay-e1 /data/runs/h15b-replay-e1/tokens-000471859200 --private
```

Then the same three reads every resident candidate gets:

1. **hbox slices** (`hbox_training/run_rollout_eval.sh`): the checkpoint directories are HF-native
   (config.json + model.safetensors + tokenizer files), so
   `hbox_training/run_rollout_eval.sh all --run h15b-e1 --room --skip-generation --checkpoint h15b-e1=/abs/path/tokens-000471859200`
   works as for the TPU checkpoints, with one preparation: the slices and validation stream the script
   syncs are the 32,768-vocab ones (`research/results/hbox-rollouts/inputs/slices.json`,
   `artifacts/roommix/room-validation.bin`). For the 1.5B family build the 65,536-vocab inputs once with
   `hbox_training/rollout_summary.py slices --validation artifacts/tokenized-15b/validation.bin
   --validation-report artifacts/tokenized-15b/validation-report.json --output research/results/hbox-rollouts/inputs-15b`
   and point the script's `LOCAL_INPUTS` and room-validation at `inputs-15b` / `artifacts/roommix-15b/room-validation.bin`
   (a two-line edit, or a `--inputs` flag). The evaluator itself loads any Falcon-H1 checkpoint in bf16.
2. **The audit** (`kaggle/gpu_breakage_audit`): attach the checkpoint dataset and the 1.5B base dataset
   (`emberian64/hghost-falcon-h1-1-5b-deep-base-public`, which carries `preflight-manifest.json`); widen
   `MANIFEST_GLOB` to `/kaggle/input/**/preflight-manifest.json` so the h1280-l66 family finds its base.
   The base row is the number to beat: the 0.5B lost 5.4 points of mean accuracy in one epoch without
   replay; e2-v5 (12.5% replay, 0.5B) is the same-recipe control. Also run `research/eval/interpolate.py`
   at alpha 0.8/0.9 against the base; the blend is a free knob.
3. **The room read**: no conversion needed; mlx-lm loads HF safetensors directly, which is how every
   0.5B checkpoint is served (`artifacts/serving/<name>` is a symlink to the HF directory). Serve the
   checkpoint on the preview port (`chapterx/serve-h.sh artifacts/checkpoints/gpu/h15b-replay-e1/tokens-000471859200
   h-15b-replay-e1 8125`), sample the bank (`hghost-roombank sample --model h-15b-replay-e1 --port 8125`),
   and read `mac-room-replies.jsonl` before anything reaches Discord (`chapterx/switch-to-05b.sh <dir>`
   takes any checkpoint directory; the 1.5B base already serves this way on :8127, so memory is known to fit).

The adapter: `qwen/scripts/sample.py` with the adapter for identical raw-prefix generations base vs
adapter on `valid.jsonl` documents (the RECIPE's evaluation-before-sweeps rule), then the same room read
through a raw-prompt server.

## 7. Time and cost

### T4 measurements (Kaggle, 2026-09-03; raw summaries and event logs under `gpu/kaggle_t4_*_test/results/`)

**CPT (`h-ghost-t4-cpt-test` v3):** Falcon-H1-Tiny-90M (91.1M parameters) on corpus-v1.5-replay, `--tiny`:
2 x 4 x 2048 = 16,384 tokens/step, fp16 autocast with fp32 masters, gradient checkpointing, pure-PyTorch
Mamba scan (no `mamba-ssm` on Kaggle), image torch 2.10.0+cu128, transformers 4.57.6.

| what | value |
|---|---|
| throughput | **337 tokens/s** (median over 5-step intervals; 339 max), i.e. 48 s per 16k-token step |
| peak memory | 7.96 GB at 2 x 2048 (4 x 2048 OOMed: a 6 GiB block in the scan's backward) |
| steps done | 30 of 122 (491,520 of 2M tokens) before the 26-minute watchdog saved and exited cleanly |
| train loss | 3.25 (step 5) -> 3.04 (step 30); gradient norm 12.6-17.1 at 16k tokens/step |
| validation (16 x 2048 tokens) | library 3.8152 -> 3.8449, room 3.1098 -> 3.1606 (step 0 -> step 30; still inside the 37-step warmup at LR 4.7e-5: the early-Adam perturbation, not learning yet; the hbox reference run needed 3M warmup tokens before held-out loss fell) |
| checkpoint | `tokens-000000491520/` (bf16 safetensors, 215.9 MB) reloads with FalconH1ForCausalLM: fp32 re-evaluation 3.8419 vs 3.8449 trained under fp16 autocast (delta 0.003) |
| kernel wall clock | 28.7 min including pip, sha256 of the 958 MB stream, and the reload check |

The gradient-norm scale is a property of batch size on this model: 46.9 at 1k tokens/step, 20.5 at 4k, 13-17
at 16k (the local MPS/CPU probes and the T4), i.e. noise falling as 1/sqrt(B); at 131k tokens/step on the
1.5B expect a few units, so `--grad-clip 1.0` (the TPU kernel's value) will be active on most steps. Adam
is scale-invariant, so that only modulates step-to-step; watch the gate's `gradient_norm` and, if it is
steady, leave the clip alone.

**QLoRA (`h-ghost-t4-qlora-test` v3 and v4; v4 is the complete run):** Qwen/Qwen3.5-2B-Base (1.21B text parameters; 4-bit NF4 base,
LoRA r=16 on 96 projections = 10.9M trainable), fp32 compute (the T4 has no bf16; fp16 NaNs the GDN
layers), seq 2048, batch 1 x accumulation 4, pure-PyTorch Gated DeltaNet (no `fla`), transformers 5.16.1,
peft 0.20.0, bitsandbytes 0.50.2.

| what | value |
|---|---|
| throughput | **186-195 tokens/s** median (v4 186, v3 195; the same T4 model varies by a few percent between sessions), i.e. 42-44 s per 8,190-token step |
| peak memory | 4.58 GB with the chunked cross-entropy (12.6 GB and OOM without it, on the 248k-vocab logits) |
| steps done | v4: 28 of 30 (228,355 tokens) before the 23-minute watchdog saved the adapter; v3: 22 of 30 |
| train loss | 3.01 -> 3.10 (noisy at 8k tokens/step: 2.83-3.15); gradient norm 0.19-0.27 |
| validation (8 held-out chunks, 16,376 tokens) | 2.9219 -> 2.9158 (step 15) -> 2.9114 (step 28) |
| adapter | 43.7 MB; reloaded onto a fresh NF4 base in the kernel: loss 2.9114, delta 0.0 vs the trained model |
| merge | v4: merged into the fp16 base (peft `merge_and_unload`, 4.5 GB written): validation **2.8718 vs 2.9114** for adapter-on-NF4, i.e. the 16-bit base is 0.040 nats better than its NF4 quantization on this 2B and the adapter transfers into it without loss. (v3's merge died on the image's `torchao 0.10`; peft 0.20 refuses <0.16, so the kernel now uninstalls it.) |
| model load | 57 s (4.5 GB download + NF4 quantization on the fly) |

### Projection method

The FLOP count is the primary estimate; the T4 numbers anchor the fallback path.

- CPT, 1.5B: 6 x 1.555e9 = 9.3 GFLOP per token for forward + backward, x 4/3 for checkpointing recompute
  = 12.4 GFLOP/token. H100 SXM dense bf16 peak 989 TFLOP/s. Hybrid Mamba-2 + attention models through
  transformers with the Triton SSD kernels land at 20-35% MFU on one GPU (the chunked scan is
  memory-bound; our 0.5B reached 22% MFU on a TPU v5e-8 with a hand-written JAX port). At 25% MFU: 20K
  tokens/s -> 471.9M tokens in 6.6 h; at 20%: 16K tokens/s, 8.2 h; at 35%: 28K tokens/s, 4.7 h. Plus ~25
  minutes of validation and checkpoints. **Budget 8 h (~$19); plausible range 5-9 h.**
- CPT fallback (no mamba-ssm): the T4 anchor is 337 tokens/s for the 90M in fp16. Scaling by parameters
  (1.555B / 0.091B = 17x) gives ~20 tokens/s on a T4 and, at the 10-12x H100/T4 factor, **200-240
  tokens/s on the H100 fallback path: 550-650 hours for the epoch.** That is the case for the kernels in one
  number. (The fallback is dominated by the scan's Python-level chunk loop and its materialized
  intermediates, so the per-parameter scaling is pessimistic for the wider 1.5B, but not by 100x.) Do not
  start the epoch on the fallback; fix the build, then read the gate.
- QLoRA, 27B: frozen base, so ~4 x 27e9 = 108 GFLOP/token for forward + backward, x 1.5 for recompute
  = 162 GFLOP/token, and NF4 dequantization roughly halves bitsandbytes' effective rate: 1-2K tokens/s.
  One epoch of train.jsonl is 6.1M tokens: **1-2 h (~$3-5)**, plus 15 minutes for the download and the
  10 validations (100 x 2048 tokens each). Unsloth would roughly halve it. T4 anchor: 195 tokens/s for
  the 2B in fp32 on the pure-PyTorch GDN; scaled by parameters (27/1.2 = 22x) that is ~9 tokens/s on a
  T4, ~100 tokens/s on the H100 for the same (fallback, fp32) code path, i.e. 17 h per epoch. The
  bf16 + `fla` kernels are what make the 1-2 h figure: check the `hardware` event (`compute_dtype`
  bfloat16) and that `flash_linear_attention` imports before starting the epoch; run `--max-steps 20`
  first and read `tokens_per_second`.
- Setup and transfers: 30-45 minutes. Copying back: 15 minutes.

**The day: ~10-11 h of instance time, $24-27 at $2.39/h; rent 12 h.** The CPT run dominates; the gate's
`tokens_per_second` turns the range into a number before the money is spent.

Assumed H100/T4 speedup for the anchors: 15x at the peak (989 vs 65 TFLOP/s dense fp16/bf16), ~10x on
memory bandwidth (3.35 TB/s vs 320 GB/s); the Mamba scan sits between, so 10-12x is the honest factor for
the same code path, before the kernel-vs-fallback factor.

## 8. The corpus build (done on the Mac, 2026-09-03)

`research/roommix/make_replay_15b.py` took the 57,241 fineweb-edu documents of corpus-v1.5-replay
(60,000,128 tokens under the 90M tokenizer), recovered their text by decoding with the 90M tokenizer
(re-encoding reproduced every id: 0 mismatches), encoded them with the 1.5B tokenizer (59,639,479 tokens,
ratio 0.994, max id 65,528) and wove them into corpus-v1.3-room-15b (412,251,005 tokens, 143,611
documents) with the same rule as the 90M weave: replay document k goes before base document
floor(k x (143,611 + 1) / 57,241), streaming order. Result: 471,890,484 tokens, 12.638% replay (the
target was 12.5%; the 0.6% tokenization ratio is the difference), 200,852 documents, max id 65,530,
sha256 above. Verified: `verify_weave` (every base token identical outside the insertions), the sidecar
in lockstep (class 0 for replay), the copied validation files byte-identical, and independently by
deleting the insertion spans from the woven stream and re-hashing (it reproduces the v1.3-15b sha256).
`manifest.json` records the rule, every insertion (`v13_offset`, `v15_offset`), and the retokenization.

## 9. Before you rent

- [x] The corpus is on Kaggle (`emberian64/hghost-curated-tokens-v1-5-replay-15b`, private; `kaggle datasets files`
      lists train.bin at 943,780,968 bytes). Re-upload with `kaggle datasets version -p artifacts/roommix-15b/corpus-v1.5-replay-15b --dir-mode skip`
      only if the corpus is rebuilt.
- [ ] Kaggle token on hand for the box, or the Mac awake for rsync.
- [ ] Hub token on the box if you want the private-repo backups.
- [ ] Re-read section 7's T4 numbers; if the T4 run was cut by the watchdog, the fallback anchor is a lower bound.
