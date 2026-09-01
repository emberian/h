# CODEXOUT: restart and handoff map

Snapshot: **2026-09-01, about 18:00 EDT**. Live counters will move after this was written.

This is the shortest path back into the project without reconstructing a day of context. The more expansive
research map remains in [`FUTURETHOUGHT.md`](FUTURETHOUGHT.md); this file is authoritative for what is live,
what was actually measured, what is uncommitted, and what should happen next.

## Read this first

The project is not at “choose an architecture” anymore. It has:

- a public CC0 repository at `git@github.com:emberian/h.git` / <https://github.com/emberian/h>;
- a sealed, deduplicated 374.4M-training-token corpus-v1 already on Kaggle and the home machines;
- a real 10M-token Falcon-H1 CPT checkpoint showing a substantial held-out shift;
- a functioning but extremely inefficient first EasyDeL TPU smoke;
- a reviewed, unlaunched production-shape TPU gate intended to resolve that inefficiency;
- a live OCR tranche on nextop and a live LoRA control on persvati;
- a parity-tested ROCm Triton Mamba scan and upstream `causal-conv1d` wheel on hbox;
- a detailed near/later program covering data quality, long context, resident chat life, learning mechanics,
  mechanistic interpretability, steering, continual learning, MIR, recurrence, distillation, and GLaDOS.

The immediate job is **not** to invent another branch. Finish the TPU production gate, use its measured warm
rate to select the week's main run, preserve the two live background jobs, and build the evaluation/data-v2
infrastructure that makes later comparisons meaningful.

Do not accidentally do any of the following:

- Do not resume the old hbox BF16-state CPT as the clean production baseline. It quantization-froze whole
  parameter families, including all norm values and nearly all Mamba dynamics.
- Do not promote hbox's mixed FP16/BF16 experiment merely because it stayed finite. It failed the multi-batch
  gradient-group parity gate.
- Do not infer TPU efficiency from the 9.7K tok/s smoke. That graph had one tiny sequence per chip, maximum
  rematerialization, and vanilla attention.
- Do not launch the full TPU pass until the new gate has saved and cold-reloaded optimizer state and passed
  its warm-throughput/stability assertions.
- Do not admit PaddleOCR results into training automatically. Every result is deliberately
  `ocr_unreviewed`.
- Do not mutate corpus-v1. All OCR, split, cleanup, balancing, or metadata improvements belong in corpus-v2
  (or an explicitly named v1.1 evaluation addendum).
- Do not use WAN DDP between these machines. It was measured and decisively loses.
- Do not replace the high-quality source prose with a large volume of synthetic model prose. Synthetic data
  is best used later as a small, source-grounded structural/task/preference supplement.

## Machine and job state

### nextop / this Mac: OCR is live

Two processes are intentionally running:

```text
PID 16240  mlx_vlm.server, PaddlePaddle/PaddleOCR-VL-1.6, port 8111
PID 98929  hghost-paddle-ocr, 100-document bounded tranche
tmux       hghost-ocr
```

At the snapshot the log had completed **53/100** entries, all quarantined as `ocr_unreviewed`. There were 94
raw result files; the current item was `rat_palace/people/ingo_swann/Swann_B105_F5_P1.pdf`. The apparent
difference between completed count and raw-file count is normal because some documents/regions create more
than one artifact and the pipeline is resumable.

Useful commands:

```sh
tmux attach -t hghost-ocr
tail -f artifacts/paddle-ocr/logs/resume-20260901.log
ps -p 16240,98929 -o pid,etime,%cpu,%mem,rss,stat,command
find artifacts/paddle-ocr/raw -type f | wc -l
```

Invocation, for reconstruction only—do not start a duplicate while the current job is alive:

```sh
.venv-paddle/bin/python -m mlx_vlm.server \
  --host 127.0.0.1 --port 8111 \
  --model PaddlePaddle/PaddleOCR-VL-1.6 \
  --max-num-seqs 4 --max-tokens 8192

.venv-paddle/bin/hghost-paddle-ocr \
  --root cathedral=/Users/ember/PARAHEPTARCH/interface.cathedral.bucket \
  --root rat_palace=/Users/ember/archive/rat-palace \
  --records artifacts/extracted/records \
  --raw-output artifacts/paddle-ocr/raw \
  --server-url http://127.0.0.1:8111/ \
  --region-concurrency 4 --min-pages 4 --max-pages 40 --limit 100
```

The server warns that `mlx-vlm-server` ignores `min_pixels`/`max_pixels`; these warnings have not stopped
processing. When the tranche finishes, generate a review sheet with `hghost-review-ocr`; visually inspect a
stratified sample and quantify clean tokens/hour before scaling beyond the next bounded tranche.

### persvati: LoRA is live, but slow

SSH alias `persvati` works. Active process at snapshot:

```text
PID 1656947
python /home/ember/h1-distributed/scripts/train_lora.py ...
```

The log is `/home/ember/h1-distributed/logs/lora-v1.log`. It had reached about **2,232,320 tokens** after
8h15m. Current throughput was mostly **72–80 tok/s**, materially below its earlier 130–137 tok/s smoke. The
machine exposes an **AMD Radeon 890M** through ROCm, so `nvidia-smi` failing is expected, not evidence that
the trainer is necessarily off-device. No durable training checkpoint exists yet because the first save is
at 10M tokens. At the current rate that save is still roughly another 29 hours away.

Exact run:

```text
rank=16, alpha=32, seq=512, batch=1, accumulation=4
2,048 tokens/optimizer step, warmup=3M, peak LR=3e-4
save at 10M, 30M, 100M, 300M, and 374,405,120
3,597,312 trainable adapter parameters
```

Target modules are `gate_proj`, `up_proj`, `down_proj`, `in_proj`, `q_proj`, `k_proj`, `v_proj`, `o_proj`.
PEFT rejected the depthwise convolution and Mamba `out_proj`; that limitation is documented. The run is a
scientific LoRA control, not the mainline. Check it with:

```sh
ssh persvati 'tail -40 /home/ember/h1-distributed/logs/lora-v1.log'
ssh persvati 'ps -p 1656947 -o pid,etime,%cpu,%mem,rss,stat,cmd'
```

Do not casually kill it before 10M: it has no intermediate checkpoint. Once it reaches 10M, evaluate it
against the full-CPT 10M lineage at matched exposure, then decide whether its very low throughput justifies
continuation.

### hbox: no trainer is running

SSH alias `hbox` works. Storage at snapshot:

```text
/          51 GiB free
/othersys  162 GiB free (SSD)
/tank      924 GiB free
```

The earlier run stopped after reaching about 11.1M tokens. Its durable checkpoint is:

```text
/othersys/h1-ghost/checkpoints/full-cpt-v1/tokens-000010000000
actual exposure: 10,000,384 tokens, step 4,883
model SHA-256: 752d368a897c5cc537ec3655f158dc3372a311e373433158cdfd9d9784ee9ec0
```

The process that watched for the checkpoint failed its PID validation, so the old trainer ran approximately
another 1.1M tokens before being interrupted; those unsaved updates are gone. The 10M checkpoint is intact
and is a useful developmental specimen. It is not the clean production ancestor.

Important hbox assets:

```text
/othersys/h1-ghost/data/corpus-v1
/othersys/h1-ghost/models/Falcon-H1-Tiny-90M-Base
/othersys/h1-ghost/models/Falcon-H1-0.5B-Base
/othersys/h1-ghost/kernel-test
/othersys/h1-ghost/checkpoints/full-cpt-v1/tokens-000010000000
```

The official ROCm build container `rocm/dev-ubuntu-24.04:6.3.3-complete` is present and occupies about
29.8 GB. It is useful for reproducible `gfx1030` extension builds; do not delete it merely as anonymous
cache. The user's old `mina-blocks` data remains available through snapshots by deliberate choice.

### Kaggle: no new gate is running

The previous EasyDeL real-data smoke is **COMPLETE**. The two older custom/0.5B experiments show **ERROR**.
The new production gate has not yet been pushed, so Kaggle returning “kernel slug not found” for it is
expected.

Kaggle CLI authentication works through the user's token file. Never print token contents. The UI is still
authoritative for remaining weekly TPU/GPU hours; the CLI does not expose a reliable quota counter.

## Repository state

Working directory: `/Users/ember/dev/h`

At the start of this handoff:

```text
branch: main
HEAD/origin/main: 22ece44 Diagnose and accelerate hbox CPT
remote: git@github.com:emberian/h.git
```

The following implementation was still uncommitted before this handoff file was added:

```text
M  hbox_training/compare_checkpoints.py
M  hbox_training/make_smoke_bundle.py
M  hbox_training/rocm_triton_ssd.py
M  hbox_training/train_hbox.py
M  hbox_training/validate_rocm_triton.py
?? hbox_training/benchmark_causal_conv1d.py
?? hbox_training/validate_compute_policy.py
?? kaggle/tpu_91m_production_gate/
?? CODEXOUT.md
```

The `compare_checkpoints.py` and `make_smoke_bundle.py` diffs are principally formatting/executable-mode
cleanup. The other hbox diffs are real kernel/precision work. The production-gate directory is entirely
new. Before this handoff, all of the following passed:

```text
ruff check: pass
ruff format --check: pass
py_compile: pass
pytest: 24 passed
git diff --check: pass
```

Re-run them, inspect the final diff, then commit and push. Do not discard the dirty tree; it is ours, not an
unknown user's work.

```sh
uvx ruff check hbox_training kaggle/tpu_91m_production_gate/run.py
uvx ruff format --check hbox_training kaggle/tpu_91m_production_gate/run.py
python3 -m py_compile hbox_training/*.py kaggle/tpu_91m_production_gate/run.py
.venv/bin/python -m pytest -q
git diff --check
git status --short
```

## Corpus-v1: exact facts

Corpus-v1 is sealed and already public on Kaggle as `emberian64/hghost-curated-tokens-v1`.

```text
source records:                         7,410
ready source documents before dedup:    5,212
training documents:                     4,837
validation documents:                      31
exact duplicates removed:                 245
all exact/near/sibling duplicates:         339
explicit high-confidence exclusions:         5 (1,506,697 tokens)
training tokens including EOS:      374,405,212
validation tokens including EOS:      2,380,464
```

Hashes:

```text
base model.safetensors:
ee1d547c2d78df42a52afd55b23459301ca21126851b82e0900f1e313dbcf5ef

train.bin:
fdaa8b8514b006942e410f7044d5e9da8be852089f7380e5d05eff5b3573f124

validation.bin:
07bce22a3de6101d4d946d1592a500c30a3790afffdecb8da6bd99777b985928

source manifest:
6a059742543cde4822f95605e8f0f42e1e89bbad829a95e27234d59a2fc8b7ae
```

Token format is little-endian `uint16`, stock `tiiuae/Falcon-H1-Tiny-90M-Base` tokenizer, vocab 32,768,
EOS 11, and contiguous source text with EOS after every document. The local canonical files are under
`artifacts/tokenized`; the Kaggle upload staging copy is `kaggle/corpus_dataset`.

Corpus-v1's known limitation is serious: the validation split is document-disjoint but not yet reliably
**work/edition-family-disjoint**. It also contains visible page furniture and occasional control/form-feed
artifacts. Preserve it for matched experiments; fix these in corpus-v2 and in a separate stronger evaluation
pack.

Quality-v2 found 524 documents worth review among 405.3M ready pre-dedup tokens. The largest cheap data gains
are work/edition grouping, repeated page-furniture removal, conservative dehyphenation, OCR review, language
and tokenizer-fragmentation checks, and source balancing—not another optimizer novelty.

Current extraction status in the frozen build manifest includes **2,018 `needs_ocr` PDFs**. A neighboring
quality summary reported 2,019 because one record changed status between those pipeline snapshots; always
name the manifest/version rather than treating either number as eternal.

## What the 10M CPT already proved

Read [`research/results/hbox-cpt-10m.md`](research/results/hbox-cpt-10m.md).

On the same fixed 16,384-token validation slice:

| Model | Loss | Perplexity | Accuracy |
|---|---:|---:|---:|
| untouched Falcon-H1-Tiny base | 3.745613 | 42.3349 | 34.9426% |
| hbox CPT at 10M | 3.615983 | 37.1879 | 36.7615% |

Only 2.67% of a corpus pass improved loss 3.46%, perplexity 12.16%, and accuracy 1.82 points. Generations
became plainly more library-like. They also began reproducing page numbers, citations, form feeds, and
recursive repetition. That is the empirical reason to continue CPT **and** the empirical reason corpus
cleanup/memorization evaluation are production requirements.

The old run used BF16 parameters and BF16 Adam moments. At 10M:

- norms were bit-identical;
- only 7.76% of embedding/head values changed;
- only 9.58% of Mamba convolution values changed;
- only 0.75% of recurrent-dynamics values changed.

Use BF16 arithmetic with FP32 master parameters and FP32 moments henceforth.

## hbox ROCm engineering: accepted and rejected paths

### Accepted: upstream Mamba-2 Triton SSD scan

[`hbox_training/rocm_triton_ssd.py`](hbox_training/rocm_triton_ssd.py) patches Falcon-H1 to use the upstream
Mamba-2 Triton SSD scan while retaining grouped PyTorch Conv1d. It is explicit and opt-in.

Pinned source on hbox:

```text
mamba-ssm 2.3.2.post1 sdist
SHA-256 104cc47e9101e5401a675fa2b784f2952b9b037f3b1dd83b5ac544394e95d028
root /othersys/h1-ghost/kernel-test/mamba-source/mamba_ssm-2.3.2.post1
```

Layer parity versus Transformers reference at seq256 passed:

```text
output relative mean error       0.2657%
input-gradient relative error    0.2354%
worst parameter-gradient error   0.3735%
warm mixer forward+backward      6.92 ms
```

Full-model real-token FP32-master/BF16-compute smokes:

| Microbatch | Warm throughput |
|---|---:|
| 1 × 512 | 2,259–2,365 tok/s |
| 4 × 512 | 2,060–2,065 tok/s |
| 1 × 1,024 | 1,855–1,856 tok/s |

Batch 1 × seq512 was best. One corpus pass is still about 44–46 compute hours, so hbox is useful for bounded
controls, not the likely main pass.

### Rejected: broad FP16 plus a BF16 recurrent island

The mixed policy appeared fast (roughly 3.5–3.8K tok/s) and finite, but the proper four-batch full-model gate
failed. Durable report:

```text
/othersys/h1-ghost/kernel-test/full-model-mixed-policy-s128-b4.json
```

Important failures:

```text
full-gradient relative mean error  10.25%
norm-gradient cosine                0.975227 (gate required >= 0.98)
Mamba conv relative mean error      12.55%
attention V/O relative error        10.64%
```

Leave BF16 compute as the safe default. “Finite” is not a sufficient precision criterion.

### Promising but not integrated: upstream causal-conv1d

An official upstream `causal-conv1d` 1.6.2.post1 ROCm wheel was built in the matching ROCm 6.3.3 container,
targeted to `gfx1030`, but **not installed into the production venv**.

```text
source tar:
/othersys/h1-ghost/kernel-test/causal-conv-source/causal-conv1d-v1.6.2.post1.tar.gz
SHA-256 4589196e0afd58a015f32dd7333183e1bb582c928d0a333496b6ec86f462012d

wheel:
/othersys/h1-ghost/kernel-test/causal-conv-source/causal-conv1d-1.6.2.post1/dist/
causal_conv1d-1.6.2.post1-cp312-cp312-linux_x86_64.whl
SHA-256 8a6fc3f37a90d46eff0ee4a4a292f64c8568bf94771e722d33a19eccf61db9ee

extracted test staging:
/othersys/h1-ghost/kernel-test/causal-conv-wheel-test
```

Actual H1 convolution shape, batch1/channels896/seq512/kernel4, BF16 forward+backward:

```text
output relative mean error     0.1485%, cosine 0.99999586
input-gradient relative error  0.1545%, cosine 0.99999637
weight-gradient relative error 0.1705%, cosine 0.99999670
grouped Conv1d time            0.816 ms
causal-conv1d time             0.2165 ms
speedup                        3.769×
```

Report: `/othersys/h1-ghost/kernel-test/causal-conv-b1s512.json`.

Next hbox task: integrate **only** this causal convolution into the already-validated training path, without
accidentally selecting Transformers' fully fused split-conv Mamba training function. Then run full-mixer and
full-model parity, checkpoint round-trip, and a longer loss smoke. The current patch deliberately forces the
non-fused path to use our Triton scan; simply installing both fast-path packages may change which whole
forward implementation Transformers selects.

Fused AdamW is another plausible ~10% gain, exposed behind `--fused-adamw`, but it also requires a real
checkpoint/resume and parameter-delta test before a long run.

## TPU: what happened and what is ready

### Successful first real-data smoke

Public kernel: <https://www.kaggle.com/code/emberian64/h-ghost-easydel-real-cpt-smoke>

The completed EasyDeL 0.3.0 smoke proved:

- eight TPU v5e devices visible and `dp=8`;
- exact 91,131,072-parameter pretrained H1 loaded;
- real corpus and model hashes checked;
- four finite BF16 full-weight optimizer updates completed;
- steps 3–4 were warm at about 0.104–0.106 seconds for 1,024 global tokens: about **9.7K tok/s**.

It spent about 24 minutes on each of the first two compile-heavy steps. It did not save a checkpoint. Its
configuration was intentionally tiny for correctness: seq128, global batch8, or only one sequence / 128
tokens per chip.

Static review found why its warm utilization was still awful:

1. only 128 tokens per chip;
2. `EasyDeLGradientCheckPointers.NOTHING_SAVEABLE` means maximum recomputation, not “none”;
3. the notebook selected vanilla attention;
4. it used BF16 parameters/optimizer state;
5. it never tested serialization.

The measured H1 step was about 6 useful TFLOP/s over a 1.576-PFLOP/s slice—roughly 0.4% nameplate. The user's
judgment that 9.7K tok/s is bad for this hardware is correct.

### Reviewed production gate (not launched)

Directory: [`kaggle/tpu_91m_production_gate`](kaggle/tpu_91m_production_gate)

Intended public slug:

```text
emberian64/h-ghost-91m-production-gate
```

Configuration:

```text
Falcon-H1-Tiny-90M-Base, exact public checkpoint
sequence length                 512
global sequences               128
sequences per chip              16
tokens per chip              8,192
global tokens per step      65,536
optimizer steps                  6 (393,216 real train tokens)
warm rows                         4
compute                         BF16
parameters/momenta              FP32
mesh                            pure dp=8 replication
attention                       AUTO -> EasyDeL blocksparse/Splash on TPU v4+
gradient checkpointing          NONE (no rematerialization)
final checkpoint                yes, including optimizer state
validation                      fixed real batch before/after cold reload
```

Hard gates:

```text
median warm throughput >= 50,000 tok/s
warm max/min execution time <= 1.5
all train losses finite
restored step == 6
pre/post reload validation loss delta <= 1e-6
all floating graph leaves FP32
all floating optimizer leaves FP32
```

The script hashes itself, the base checkpoint, both corpus streams, and the saved checkpoint tree. It records
per-step metrics and dtype trees. The EasyDeL 0.3.0 wheel source was independently inspected:

- all 29 passed `TrainingArguments` keywords exist;
- `NONE` is indeed no rematerialization;
- `AUTO` on TPU v4+ chooses the blocksparse/Splash implementation in BF16;
- `do_last_save=True` and `save_optimizer_state=True` feed EasyDeL's final state save;
- `EasyDeLState.load_state(..., tx_template=arguments.get_tx_template())` is the supported optimizer restore
  path;
- trainer step execution is explicitly synchronized before metrics timing.

Local lint, compile, and repository tests passed. The remaining uncertainty is exactly what the gate is for:
whether 16 × 512 tokens/chip with no rematerialization fits 16 GiB HBM, compiles once, and actually feeds the
matrix hardware. An OOM is a useful failure; do not silently shrink it and call the gate passed.

Launch only after committing/pushing the exact source:

```sh
uvx --from kaggle kaggle kernels push -p kaggle/tpu_91m_production_gate
uvx --from kaggle kaggle kernels status emberian64/h-ghost-91m-production-gate
```

After completion:

```sh
mkdir -p /tmp/hghost-tpu-production-gate
uvx --from kaggle kaggle kernels output \
  emberian64/h-ghost-91m-production-gate \
  -p /tmp/hghost-tpu-production-gate --force
```

Inspect `tpu-91m-production-gate-report.json`, the complete log, and checkpoint contents. Do not rely only
on Kaggle's green status. The gate checkpoint uses LR 1e-6 and exists to prove serialization; the actual CPT
run should start from the base unless its optimizer/schedule is intentionally made continuous with the gate.

If the gate passes, compute:

```text
T_pass_hours = 374,405,212 / warm_tokens_per_second / 3600
```

Then create the actual resumable one-pass CPT kernel using the same proven shape/runtime. Save at 10M, 30M,
100M, 200M, and final. Do not launch the two-pass random-init control before the CPT mainline is durable
unless remaining quota is clearly sufficient.

If the gate OOMs, keep all other settings fixed and first try a smaller global sequence batch (64) while
retaining seq512 and no rematerialization. If it is slow rather than OOM, inspect HLO/profile and the Mamba
lowering before spending the rest of the week. Do not return to the old tiny shape.

Production should eventually vendor the resolved EasyDeL wheel set into a public Kaggle dataset and run
offline. The gate still has internet enabled and installs pinned `easydel==0.3.0`; its transitive environment
and JAX version are recorded, but this is not ideal for a multi-hour production pass.

### Existing public Kaggle inputs

```text
emberian64/hghost-falcon-h1-90m-base-public
emberian64/hghost-curated-tokens-v1
emberian64/hghost-jax-code-public
emberian64/hghost-falcon-h1-0-5b-base-public
```

The 90M public base includes the Falcon license, acceptable-use policy, redistribution notice, tokenizer,
config, exact model, and preflight parity assets.

## Compute topology decision

The machines should run independent branches, not one distributed optimizer.

- Kaggle TPU v5e-8: likely 91M full CPT and scratch mainline if the production gate succeeds.
- nextop M2 Max: OCR now; native MLX is the trusted fallback trainer and measured at 12.7–15.0K tok/s at
  seq1024, 6.46–6.66K at seq512.
- hbox RX 6750 XT: bounded full-CPT/kernel/precision/regularization controls after causal-conv integration.
- persvati Radeon 890M: current LoRA control; reevaluate at 10M because it is exceptionally slow.
- Kaggle T4 ×2: future CUDA fused-kernel LoRA/0.5B pilot/evaluation lane. Prefer it over P100 unless a
  Pascal-compatible PyTorch environment is deliberately built.

Measured hbox↔persvati BF16 gradient all-reduce of 173.819 MiB took about 29.1 seconds. MLX cannot join a
PyTorch process group, and MPS Gloo tensor all-reduce is unsupported. WAN tensor/FSDP/pipeline parallelism
is not worth revisiting without radically different networking.

Full evidence and scripts: [`distributed_training/README.md`](distributed_training/README.md).

## What to do in the next working session

In order:

1. Confirm OCR and persvati remain alive; note their new progress. Do not restart duplicates.
2. Re-run local lint/tests and inspect the dirty diff.
3. Commit and push this handoff plus the ROCm validation work and TPU production gate.
4. Push the TPU production gate and monitor through checkpoint cold-reload, not merely first compilation.
5. Download and commit the machine-readable gate report/log summary.
6. If it passes, calculate measured pass time and generate a separate public, resumable one-pass CPT kernel.
7. Build the stronger v1.1 evaluation addendum in parallel; do not wait for OCR to finish.
8. At persvati's 10M checkpoint, run matched full-CPT-vs-LoRA evaluation and decide whether to stop it.
9. Integrate causal-conv1d on hbox with full-model parity before starting any clean hbox branch.

The first data/evaluation deliverables should be:

- `work_id`, `edition_id`, and `family_id` inventory with manual review queue;
- work-family-disjoint target validation and untouched test sets;
- small generic-English retention set;
- fixed prompt/seed generation suite;
- exact and near-exact 8/16/32-gram memorization scanner;
- source/quality/language/OCR-stratified NLL and bits-per-byte aggregation;
- static 512/1K/2K/4K pack metadata from one canonical order;
- high-confidence page furniture report/removal transform with reversible provenance.

## This week's quota decision tree

Quota is nominally 20 TPU hours and 30 GPU hours per week, but use the Kaggle UI to inspect the actual
remainder after the earlier failed/complete kernels.

TPU priority:

1. production gate;
2. one full 91M continued-pretraining pass if projected pass time fits with checkpoint margin;
3. two-pass random-init 91M control, resumable across weekly resets if needed;
4. only with real surplus: 0.5B CPT pilot, LR point, MIR pilot, or scratch continuation.

The one-pass CPT is the likely artwork and ancestor for posttraining/mechinterp, so it wins over scratch when
quota forces a choice. The 91M random-init 2× run remains scientifically interesting but is expected to be
undertrained; it is a control, not the default deployment candidate.

GPU priority:

1. matched LoRA control to a shared exposure;
2. CUDA/H1 fused-kernel gate on T4 ×2;
3. short 0.5B CPT throughput/quality pilot;
4. evaluation, quantization, and browser profiling;
5. continue only the branch with evidence.

LoRA cannot be usefully computed “in parallel” on spare TPU cores while data-parallel CPT uses the full
v5e-8 slice. Run it on an independent GPU machine as already planned.

## Context length and eventual chat life

The current gate uses seq512 to optimize the first domain-assimilation pass. That is not a declaration that
the resident will only remember 512 tokens. Longer is valuable but makes training more expensive and does
not automatically teach multi-party tracking.

Staged context plan:

1. domain CPT at a throughput-efficient context (start 512; benchmark 1K/2K only after the gate);
2. later context extension on a relatively small long-sequence token budget, using the architecture's native
   positional/frequency controls and a length mixture rather than making every base-CPT token long;
3. explicit chat metasyntax training with stable participant/message IDs, replies, edits, reactions, and
   `SPEAK/SILENT` decisions;
4. long-context evaluations for needle retrieval, distant callbacks, multi-speaker state, temporal updates,
   reply/addressee selection, and knowing when not to speak.

The destination harness is `/Users/ember/dev/chapterx`.

## ChapterX resident design handoff

The design subagent inspected ChapterX but made no edits. Its key conclusion: ChapterX already supports a
causal base model behind an OpenAI-compatible `/v1/completions` endpoint and has serialized channel loops,
reply IDs, reactions, attachments, plugins, and steering hooks. Its debug tracing is **not** an adequate
training ledger because it begins only after activation and therefore loses correct silences.

The smallest useful ChapterX implementation is an observation-only, append-only resident ledger:

1. `ChatEvent` for every create/edit/delete/reaction event before activation gating;
2. `ParticipationDecision` for every eligible boundary, including `speak`, `silent`, `defer`, reason,
   stochastic draw, addressee, and reply target;
3. `Generation` joining exact message revisions/cutoff, retrieval snapshot, renderer/metasyntax version,
   tokenizer and prompt token IDs, checkpoint digest, sampling config/seed, candidates, selected text, sent
   Discord IDs, and timings;
4. `Feedback` for reaction add/remove, edits/deletes, direct corrections, and explicit chosen/rejected pairs;
5. consent fields that distinguish retention, resident memory, private training, public research, and
   redistribution;
6. consent-aware immutable offline exporters.

Preserve exact message boundaries; ChapterX currently merges consecutive bot messages in places. Use stable
IDs as relational keys and names only as redundant labels. Make context budgets tokenizer-aware, not
character-estimated. Store social facts in a source-backed, retractable two-speed memory rather than baking
every changing event into weekly weights.

Later stages:

- mention-only resident with tools disabled;
- canonical `<next action="silent"/>` / `<next action="speak" to=... reply-to=...>` syntax;
- learned participation and reply/addressee policy;
- retrieved social/episodic memory with logged provenance;
- consent-clean datasets split by episode/time/relationship to prevent leakage;
- weekly consolidation branches mixed with lo2 replay, promoted only through evaluation;
- steering/readout instrumentation using ChapterX's existing seams.

The detailed code seams and line references were returned by the completed `chapterx_resident_design`
subagent in the preceding Codex session; if that mailbox is unavailable after restart, re-inspect
`src/agent/loop.ts`, `src/discord/connector.ts`, `src/context`, `src/trace`, `src/tools/plugins`, and
`src/steering` in ChapterX before editing.

## Near-term research once the baseline exists

These are ordered by dependency and expected value, not novelty.

### 1. Developmental checkpoints and honest evaluation

Save base, 10M, 30M, 100M, 200M, one pass, and repeated-pass checkpoints. Use identical target, generic,
memorization, long-context, and blind generation suites. Preserve a pre-cooldown “flat candidate” as well as
the cooled checkpoint; learning-rate decay may change posttraining plasticity even at similar loss.

### 2. Full CPT versus LoRA

Compare at the same base, data order, and 10M/30M/100M exposures. The scientific question is whether LoRA
teaches “perform the library” while full CPT changes the underlying distribution. Do not spend a ceremonial
full epoch on LoRA if it is plainly behind at shared exposure.

### 3. Learning mechanics pilot

Instrument a bounded run for sharpness/Hessian-vector estimates by parameter family: embeddings, norms,
Q/K, V/O, MLP, SSM projections, convolution, and recurrent dynamics. Test blockwise learning rates only
after measuring the H1-specific disparity. Preserve flat-vs-cooled checkpoints and apply the same small
posttraining/steering task to both.

### 4. MIR before exotic architecture

Masked-Input Regularization is unusually well matched to 100M–400M unique-token, repeated-data training and
adds training compute without inference parameters. Run a 20M–40M-token ordinary-NTP versus MIR A/B before
committing. Published evidence is from scratch training, so CPT benefit is a hypothesis.

### 5. Small, source-grounded posttraining

Keep original corpus prose dominant. Use larger models as annotators, relation extractors, critics, and
reward judges—not as the voice of the new corpus. Candidate additions:

- short cross-document contrast/implication/objection/synthesis tasks;
- active synthetic generation targeted to the current student's high-loss concepts;
- 5–20K human-ranked aesthetic pairs followed by one conservative DPO epoch;
- public, source-grounded argument tasks where a large judge sees the actual passages;
- no long generic chain-of-thought traces at 90M unless evidence reverses H1-Tiny's observed repetition
  problem.

### 6. Steering and mechinterp

Track author/topic/style axes across checkpoints. Candidate human/model-labelled axes include wet↔dry,
analytic↔incantatory, austere↔ecstatic, concrete↔abstract, technical↔mystical, and terse↔discursive. Require
layer sweeps, dose-response curves, held-out authors/topics, norm-matched random controls, composition tests,
and post-quantization checks. Do not call a convenient, non-identifiable steering direction “the unique
emotion neuron.”

Train small residual steering vectors with preference/RL signals as an interpretable alternative to another
full fine-tune. A particularly clean tiny-model study is base vs SFT vs DPO ability to detect controlled
activation injection, using random relabeling and input-perturbation controls to distinguish introspection
from semantic/anomaly cues. Call it internal-state monitoring until the stronger interpretation earns its
name.

### 7. 0.5B challenger and distillation

Falcon-H1-0.5B is itself deployable under the user's roughly 500 MB ceiling (official Q4 is around 315 MB),
and inherits about 2.5T tokens. Run only a matched short CPT pilot first. If it is a substantially stronger
domain model but too slow for the site, cache top-K logits offline and distill into 90M or a smaller
corpus-native student. Do not train a random large teacher merely to distill it.

## Later branches, after baseline/data/evaluation

### Corpus-born models

- 91M random-init H1, two repeated passes, as the requested matched architecture control.
- A more plausible 10M–30M corpus-born model with an 8K–16K tokenizer; a 32K embedding table consumes an
  absurd fraction of that budget.
- Deep/thin dense baseline before claiming recurrence wins.

### Recurrence and compute-for-parameters

One bounded 30M–70M unique-parameter experiment can test fixed shared depth, gated recurrent depth, or a
MixerLoop-style repeated mixer. Recurrence trades more training/inference compute for fewer stored weights;
it is not free effective parameters and often loses under strict iso-FLOP comparison. Kill the branch if it
is over ~10% behind the dense baseline per wall-clock/FLOP without a unique qualitative advantage.

### Tokenizer and bytes

Keep the native tokenizer for inherited H1 CPT. Use a corpus-native 8K–16K tokenizer for small scratch
models. Cross-tokenizer KD, byte-prefix marginalization, SpaceByte/MEGABYTE/BLT-like work, and a browser byte
model are generation-two experiments after a useful domain teacher exists.

### GLaDOS / clairnets

Source checkout exists at `/Users/ember/dev/clairnets`. The current GLaDOS design uses a host residual state,
an alpha compiler into a frozen deduction organ, verifier-gated operations, and gamma writeback. Cold
co-training is known to shortcut; the proposed order is organ pretrain → freeze → interface learning →
RLVR/consolidation, with corruption/permutation causal controls. It is a separate argument-organ experiment,
not justification to claim sound natural-language reasoning. The PDF corpus could support source-span claim,
premise, objection, and argument graphs.

### Vision

Vision may help lexical grounding and concept acquisition, but bolting it onto the first 91M text model is
not this week's task. Revisit with a later week's Kaggle quota: frozen small vision encoder, compact projector,
interleaved high-quality page/image-text examples, and a controlled text-only comparison. Do not let visual
token volume erase the language budget.

### Continual resident learning

Do not update weights online per message. First log clean events, retrievals, decisions, outcomes, and
consent. Then perform offline weekly consolidation with lo2 replay, resident replay, held-out temporal room
episodes, rollbackable checkpoint promotion, and explicit forgetting/memorization checks. Fast changing facts
belong in editable memory; weights learn habits, voice, participation, and metasyntax.

## Research bundle already downloaded

Primary papers and SHA-256 manifests are under [`research/papers`](research/papers) and
[`research/sources`](research/sources). Important local PDFs include:

- Falcon-H1 technical report;
- masked-input regularization / data-constrained scaling;
- sharpness disparity, sharpness-aware pretraining, edge of stability, LR/catastrophic overtraining;
- recurrence equivalence, Gated Recurrent Transformers, MixerLoop;
- persona vectors, RL-trained steering vectors, introspective awareness and its reality check;
- offline top-K distillation;
- instruction pretraining, EntiGraph synthetic CPT, rationale-consistent judging;
- compute-optimal tokenization;
- weight-sparse Transformers;
- SmolVLM and visual-grounding papers.

The claims audit distinguishes published evidence from our extrapolations. Read
[`research/claims_audit.md`](research/claims_audit.md) before turning a recent result into a production
recipe.

## File map

```text
README.md                         current pipeline/user entry point
FUTURETHOUGHT.md                  long research and weekly roadmap (some live-rate rows now stale)
CODEXOUT.md                       this restart document; live state overrides stale roadmap rows

artifacts/dataset                 deduplicated JSONL corpus-v1
artifacts/tokenized               canonical sealed uint16 corpus-v1
artifacts/paddle-ocr              live OCR outputs/logs, quarantined
artifacts/quality-v2              latest structural quality report

kaggle/tpu_91m_production_gate    reviewed but unlaunched production gate
kaggle/tpu_smoke_notebook         completed EasyDeL correctness smoke source
kaggle/tpu_fresh_91m              existing custom-JAX scratch 91M kernel
kaggle/tpu_smoke_05b              existing 0.5B smoke (last run errored)
kaggle/base_model_dataset_public  public 90M checkpoint staging
kaggle/corpus_dataset             public corpus staging

hbox_training                     deterministic ROCm trainer, validators, kernel patches
persvati_lora                     LoRA trainer and smoke evidence
jax_training                      custom JAX/Flax H1 implementation and parity tests
distributed_training              measured topology and hardware probes
research/results                  10M CPT and ROCm Triton empirical reports
research/papers                   downloaded literature bundle
```

## Open questions that should be answered with gates

1. Does the 512×128/no-remat/Splash EasyDeL graph fit and exceed 50K tok/s?
2. If yes, what is honest one-pass wall time including compile, sparse eval, and checkpoint saves?
3. Does 91M full CPT continue its strong early validation improvement through 30M/100M/one pass without
   becoming a quotation/page-furniture engine?
4. At matched exposure, is LoRA qualitatively a performance layer or does it approach full CPT?
5. How much generic-language retention is lost, and does 5–10% replay help enough to justify its tokens?
6. Can causal-conv1d improve complete hbox training measurably after the scan is already accelerated?
7. Which work/edition families contaminate corpus-v1 validation, and how different is the clean split?
8. How many of the 2,018 OCR candidates yield high-quality unique text per GPU-hour?
9. Does MIR help finite-data scratch training, and does it help or harm inherited H1 CPT?
10. Are flat pre-cooldown checkpoints more posttrainable/steerable than similarly good cooled checkpoints?
11. When do corpus style/topic directions become linearly decodable and causally steerable across the
    developmental checkpoint trajectory?
12. How much long-context capability can be added later without paying long-context cost on every CPT token?

## Definition of a successful handoff

The next person should be able to say, without guessing:

- which jobs are live and how to inspect them;
- which checkpoint is durable and why it is not the production baseline;
- which precision/kernel paths passed or failed causal parity;
- what exact Kaggle gate is ready and how it can fail safely;
- what bytes and hashes define corpus-v1;
- what must be improved in data/evaluation before quality claims;
- why CPT is first, LoRA/scratch are controls, and recurrence/vision/GLaDOS are later;
- how `h` eventually enters ChapterX without losing its earliest life history;
- where every primary result, script, and paper lives.

The spirit of the project is real engineering in service of a strange artifact: preserve provenance, test
the alluring shortcuts, save the developmental lineage, and give the tiny model every fair chance to become
more than a texture sampler without pretending in advance that it has.
