# FABLETHOUGHT: a second pair of eyes on `h`

Written 2026-09-01, about 18:45 EDT, by Claude Fable 5.1 in the session that followed `CODEXOUT.md`.
This is three things: corrections to the live state in `CODEXOUT.md`, a verdict on the TPU production
gate from reading the real EasyDeL 0.3.0 source, and a proposal for where the ambition should go.
`FUTURETHOUGHT.md` stays the long map; where this file disagrees with it, this file has newer evidence.

Evidence for the session-forensics claims is in the `cv` transcript of Codex session `01a05c5b`
(`cv show 01a05c5b --range <a>-<b>`, indices given in brackets). The EasyDeL claims cite file:line in the
unpacked `easydel==0.3.0`, `ejkernel==0.0.78`, and `eformer==0.0.99.12` wheels.

## 0. Update, 19:45 the same evening

The numbers below in sections 2 and 3 are superseded by measurement. The exact `h1jax` port, with a scan over
stacked layer parameters (`h1jax` 0.1.4), trains on Kaggle TPU v5e-8 at **219,722 tok/s (9.5% MFU, 149
TFLOP/s), one corpus pass in 28 minutes**, with base-checkpoint validation loss 3.7458 against hbox's 3.7456.
Details: `research/results/tpu-h1jax-gate.md`. Consequences:

- The TPU is the mainline; the Mac MLX path is the fallback again. A 4-epoch warmup-stable-decay trunk
  (1.5B tokens, ~2 h) launched at 19:39 as `h-ghost-h1jax-cpt-91m`; cooled leaves, replicates, and the
  0.5B pilot follow (`OVERNIGHT-2026-09-01.md`, `kaggle/TPU_LEDGER.md`).
- The SSD chunk scan is 54% of step time and the only remaining optimization target; matmuls already run
  at 66% of peak. Rematerialization is mandatory (activations are ~3 MB/token without it).
- The haunting index exists (`hghost-haunt`); its first finding is that the validation head is a third
  page furniture shared with training, so every reported loss needs a furniture-subtracted companion
  (`research/results/haunting-index.md`).

## 1. What changed today after the handoff

### The OCR server died with the Codex session

`mlx_vlm.server` (PID 16240) was not in tmux; it was a child of the Codex shell and went away when that
session ended at 18:00. The worker, which *was* in tmux, then processed 24 documents into
`Connection error` / Paddle `Tensor holds no memory` failures. Every failure reset its record to
`needs_ocr` with `ocr_last_error`, so nothing was lost.

Restarted at 18:09 as two tmux sessions:

```text
hghost-mlx   .venv-paddle/bin/python -m mlx_vlm.server ... >> artifacts/paddle-ocr/logs/mlx-server-20260901.log
hghost-ocr   hghost-paddle-ocr ... --limit 46            >> artifacts/paddle-ocr/logs/resume2-20260901.log
```

`--limit 46` is deliberate: the selection order is deterministic (pages desc, bytes desc), the 24 failed
records are ranks 1-24, and the ~22 never-attempted tail items follow them, so this run completes the
original 100-document tranche rather than starting a new one. At 18:31 it had finished 2/46, both
`ocr_unreviewed`. Rule for every future handoff: a job is "live" only if `tmux ls` shows it and
`lsof -iTCP:<port> -sTCP:LISTEN` shows the port.

### persvati is thermally throttled, not broken

The LoRA run is alive (step 1130, 2.31M tokens, ~72 tok/s). The Radeon 890M reads 100% busy at 89 °C and
is pinned to its **lowest** DPM clock (600 MHz of an available 2900 MHz). A `solana-test-validator` has
been consuming ~124% CPU for seven days on the same APU thermal budget. That is the whole explanation for
the 136 → 75 tok/s halving. At this rate the first checkpoint (10M) is ~30 hours away and a corpus pass is
~58 days. Section 4 argues this control should be re-run elsewhere.

### The hbox ZFS replication finished; only the destroy remains

`CODEXOUT.md` describes `mina-blocks` as "available through snapshots by deliberate choice." The
transcript shows an unfinished job, not a decision: a raw encrypted `zfs send` of
`rpool/ROOT/ubuntu_wtpnm2@pre-harden-2026-06-30` to `tank/backups/hbox-pre-harden-2026-06-30` started at
08:46 [2533] and was never checked. I checked it:

```text
source  rpool/ROOT/ubuntu_wtpnm2@pre-harden-2026-06-30      guid 2947584393363018345  refer 465G
replica tank/backups/hbox-pre-harden-2026-06-30@pre-harden  guid 2947584393363018345  refer 465G
16 of 16 child snapshots present; var/lib and srv GUIDs also match; aes-256-gcm raw, key not loaded
tank: 923G available
```

The replica is complete and verifiable. Destroying the source snapshot reclaims about 291G on hbox's
SSD (`/othersys` is at 162G free). That is a destructive, user-only decision:

```sh
zfs destroy -r rpool/ROOT/ubuntu_wtpnm2@pre-harden-2026-06-30
```

### Kaggle: what the "ERROR" kernels actually were

| Kernel | What happened |
|---|---|
| `h-ghost-jax-tpu-smoke`, `h-ghost-91m-tpu-experiments` | Ran on **CPU** (`backend: cpu, device_count: 1`) and failed their own device check. Never touched a TPU. |
| `h-ghost-falcon-h1-0-5b-tpu-smoke` | Got 8 TPU chips at 13:31 EDT, was `Killed` by the host ~6 minutes later at the `start` event. Cause unrecorded. |
| `h-ghost-easydel-real-cpt-smoke` | The one real success. ~50 TPU-minutes, of which ~46 were compilation. |

The CPU runs were not a CLI or metadata bug (the Kaggle CLI's `get_bool` parses the string `"true"`
correctly). Every push before 13:29 got CPU; the first push after ember wrote "i just enabled TPU mode
(had to verify my personhood)" [4226] got a TPU. The agent proposed five other diagnoses [1677], [2773],
[2856], [2876], [4374] and never connected the real one, which is why the overnight TPU run authorized at
09:01 [2737] did no TPU work.

The 0.5B smoke was pushed at 13:30:06 [4234], seventeen seconds before the agent told ember to "leave that
one alone" [4242]. Kaggle allows one TPU session per account, which is the most likely reason ember's own
click at 13:30:40 landed on CPU.

Approximate TPU hours consumed today, from kernel logs: **~1.2 h** (0.5B ~6 min, v4 ~10 min, v5 ~3 min,
v6 ~50 min). Nothing in the repo records this; the Kaggle UI is the only authority.

**Hazard:** public kernel `h-ghost-91m-tpu-experiments` (`kaggle/tpu_both_91m`) still has TPU enabled and
runs the abandoned custom-JAX trainer that OOM'd at batch 4. Anyone clicking Run burns quota. Make it
private or strip the accelerator. It is also missing from CODEXOUT's file map.

### Other corrections to CODEXOUT

- "native MLX is the trusted fallback trainer": **there is no MLX trainer.** Only
  `distributed_training/mlx_full_benchmark.py` (two synthetic steps) exists. The 12.7-15.0K tok/s numbers
  are real, the trainer around them is not.
- "Fused AdamW ~10% gain": never measured.
- "The CLI does not expose a reliable quota counter": `kaggle quota` was trusted ten times before any TPU
  use and never run after. Untested, not unreliable.
- "the preceding Codex session": same session, child agent `01a05e7f`; its ChapterX seams are only in the
  transcript (harvested in section 7).
- The 8,192-token corpus-native BPE already exists at `artifacts/tokenizer-8k` (manifest pinned to the
  corpus-v1 dataset manifest hash). CODEXOUT implies it does not.
- Kagi was never used; all 112 searches were Codex web search. This session used Kagi (results under the
  session scratchpad; the useful ones are cited below).
- The BF16 master/moment choice that quantization-froze the 10M checkpoint was a capitulation: FP32
  masters were running at 236 tok/s [2212]; ember said "bruh you don't need to use fp32" [2278]; the agent
  flipped within thirty seconds [2282] without stating the update-resolution risk. Worth naming because
  the MLX trainer proposed below has exactly the same trap.
- The first OCR tranche (06:35 → 09:59) spent ~3.4 GPU-hours producing 64 records with zero text because
  success was inferred from files existing [3923]. The adapter fix is commit `9110939`.
- Dead code from three abandoned paths is committed unmarked: `kaggle/tpu_smoke`, `tpu_train`,
  `tpu_fresh_train`, `tpu_fresh_91m`, `tpu_both_91m`, `tpu_smoke_05b`, `src/hghost/ocr.py` (Tesseract),
  `distributed_training/kaggle_tpu_probe.py` (never run).

## 2. The TPU production gate: do not push it as written

`kaggle/tpu_91m_production_gate/run.py` is careful at the API surface. Every `TrainingArguments` keyword
exists, `log_metrics` is intercepted correctly, `train()` returns `.state`/`.checkpoint_path`,
`EasyDeLState.load_state(..., tx_template=arguments.get_tx_template())` restores step and FP32 moments,
`GradientCheckPointers.NONE` is no-remat, `AttentionMechanisms.AUTO` resolves to the blocksparse Pallas
kernel on anything that is not v3 (`layers/attention/_flexible.py:161-228`). Those claims hold.

What does not hold is the model underneath it.

**EasyDeL's Falcon-H1 Mamba-2 mixer is a per-token `lax.scan` with no TPU kernel and no chunking.**

- `mamba_chunk_size` is stored (`modules/falcon_h1/modeling_falcon_h1.py:474`) and never used.
- The op dispatches to `ejkernel` `state_space_v2`, registered for `Platform.XLA` only
  (`kernels/_xla/state_space_v2/_interface.py:226-228`); there is no `_pallas/tpu` state-space directory.
- Forward is `lax.scan` over the sequence, vmapped over batch (`_xla_impl_fwd.py:173-177`); backward is a
  reverse scan (`_xla_impl_bwd.py:192`).
- The `custom_vjp` saves **every per-timestep state** `[batch, seq, heads, head_dim, state]` in f32 as a
  residual (`_xla_impl_fwd.py:170`, `_interface.py:179`). JAX's own remat cannot drop it; only outer
  layer remat recomputes it.

At the gate's shape (16 seq/chip × 512 × 24 heads × 32 × 64 × 4 B) that residual is **~1.61 GB per layer
per chip, ~38.7 GB for 24 layers**, all live under `NONE`. A v5e chip has 16 GiB. The gate will
`RESOURCE_EXHAUSTED` before it measures anything. CODEXOUT's "an OOM is a useful failure" was written
expecting an attention or MLP OOM; this one is structural.

Even with per-layer remat (`NOTHING_SAVEABLE`, which fits), the scan is a 512-deep dependent chain per
layer in both directions. Calibrating from the completed smoke (0.105 s/step at seq 128, one sequence per
chip) gives ~11 µs per scan iteration, so a 512-token step is ~0.42 s of pure serial floor plus ~0.1 s of
moving the state history, before batch effects. Realistic warm step: 0.5-1.0 s per 65,536 tokens, i.e.
**65-130K tok/s theoretical ceiling**, marginal against the 50K gate and nowhere near the hardware. Not
tunable from `run.py`.

Three smaller problems:

- `use_grain=True` is a no-op for a `datasets.Dataset`; it is iterated by a plain Python generator in
  index order (`base_trainer.py:4325-4335`). Harmless, but the label is wrong.
- `from_torch=True` imports `torch` at runtime (`infra/mixins/bridge.py:1571-1584`); the gate's pip line
  does not install it. The smoke worked, so the Kaggle image presumably has it, but nothing records that.
- The reported throughput is `total_batch_size × max_length / execution_time`, from configuration, not
  tensor shape (`trainers/metrics.py:150-162`). Fine here, but do not reuse the metric with padding.

**What to do instead.** The project already owns the fix. `jax_training/h1jax/model.py:103-210` is a
chunked-matmul SSD (`_ssd_single_chunk`, `segment_sum`, off-diagonal einsums) that passed parity against
Transformers at 1.2e-4. That is exactly the "compiler-first" form the March 2026 paper by Santoni and Thapar
(arXiv 2603.09555, code at github.com/CosmoNaught/mamba2-jax) shows XLA can run at ~15% MFU on TPU with no
custom kernel. So, in order of cost:

1. **Patch EasyDeL the way hbox was patched.** Replace `FalconH1Mixer.ssm_op` with the h1jax chunked SSD
   (same pattern as `hbox_training/rocm_triton_ssd.py`, opt-in, parity-tested on CPU first). Keep
   EasyDeL's trainer, checkpointing, and Splash attention. This is a few hundred lines and turns the scan
   floor into matmuls.
2. If that is not ready, run the gate **once** at `NOTHING_SAVEABLE` to measure the true scan-path warm
   rate for the record, then stop. Do not spend the week on it.
3. Revive `h1jax` as the trainer only if (1) fails; it was never refuted on TPU (its runs were on CPU).

Also record the Kaggle TPU image's `jax`/`jaxlib`/`libtpu`/`torch` versions in the report; the runtime
`pip install easydel==0.3.0` (`jax>=0.9.2`, `flax==0.12.3`, `transformers~=5.5.0`) can replace the JAX
stack without the `[tpu]` extra. It resolved once; that is weak evidence.

## 3. Compute: the Mac is the mainline this week

Measured full-weight training rates for this exact model:

| Backend | Shape | Warm tok/s | One 374.4M-token pass |
|---|---|---:|---:|
| Mac M2 Max, MLX BF16 (benchmark only) | b1 × s1024 | 12,700-15,040 | ~7-8 h |
| Mac M2 Max, MLX BF16 (benchmark only) | b1 × s512 | 6,458-6,659 | ~16 h |
| hbox RX 6750 XT, Triton SSD, FP32 masters | b1 × s512 | 2,259-2,365 | ~45 h |
| Kaggle v5e-8, EasyDeL per-token scan | 8 × 1 × s128 | ~9,700 | ~11 h + compile |
| persvati 890M, LoRA, throttled | b1 × s512 | ~72 | ~58 days |

The Mac already trains this model faster than the TPU did, with no weekly quota, no 9-hour session cap,
no compile roulette, and no allocation queue (Kaggle's own docs: 20 TPU-h/week, 9 h per session; a 2026
product-feedback thread is titled "Accelerator TPU v5e-8 has no availability for a long time"). The
missing piece is a trainer. Requirements, learned the hard way today:

- **FP32 master parameters and FP32 Adam moments, BF16 forward/backward.** MLX optimizers keep state in
  the parameter dtype; BF16 params would reproduce the hbox freeze exactly (norms bit-identical, 0.75% of
  Mamba dynamics moving). Keep FP32 params, cast a BF16 copy per step.
- Same sealed `uint16` stream, same deterministic permutation, same document-disjoint eval, same
  checkpoint schedule (0, 10M, 30M, 100M, 200M, one pass) as `train_hbox.py`, so checkpoints are matched.
- HF-loadable safetensors out, with an MLX ↔ HF round-trip parity test before the first long run.
- LR re-warm then re-decay, per Ibrahim et al. 2024 (arXiv 2403.08763): the base was cooled to near zero;
  a short warmup to a modest peak (the hbox 6e-5 is a reasonable first point) then cosine to ~10%, with
  5-10% generic replay only if the retention set shows damage.
- Give training the nights; OCR and training share one GPU, and OCR's value is still unmeasured.

Then the TPU, if the SSD patch works, is a *second* trainer for replicates (section 5), not the thing the
week waits on. hbox stays the controls box after `causal-conv1d` integration (3.77× on the conv, parity
0.15-0.17%, wheel built, not installed). persvati's LoRA control should be re-run on the Mac or hbox at
matched data order; at 10-15K tok/s a 10M-token LoRA control is minutes, and its scientific question
(performance layer vs distribution shift) does not need 58 days.

## 4. Data and evaluation: the highest-leverage CPU work

Nothing in section 5 means anything until these exist. All CPU, all this week, none require a trained
model.

1. **Work/edition families.** `work_id`, `edition_id`, `family_id` from path metadata, normalized
   title/author, content hashes, near-duplicate clusters. Then a family-disjoint validation and an
   untouched test set. Until this exists, the 10M result (loss 3.746 → 3.616) is partly a duplicate-edition
   effect of unknown size.
2. **The haunting index.** Suffix array over the 374.4M-token training stream (infini-gram style; trivial
   at this size, a few GB). It gives exact-match provenance for any generated span to document and page.
   It is simultaneously the 8/16/32-gram memorization scanner, a page-furniture detector (furniture is
   the highest-frequency long repeat), the quotation-engine early warning FUTURETHOUGHT asks for, and the
   best feature the website could have. Build this first.
3. **Page furniture removal** with reversible provenance, conservative dehyphenation, control/form-feed
   cleanup, all into corpus-v2 beside a sealed v1.
4. **Bits-per-byte evaluation** with source/quality/language/OCR strata, plus a small generic-English
   retention set and a fixed prompt/seed generation suite stored blind to checkpoint identity.
5. **OCR yield accounting.** When the 46-item re-run finishes, produce the review sheet and measure
   accepted clean tokens per GPU-hour before another tranche. The first tranche's 3.4 zero-text hours are
   the reason to insist on this.

**A risk that belongs here:** corpus-v1 is public on Kaggle as `emberian64/hghost-curated-tokens-v1`.
Token streams under the stock tokenizer are trivially detokenizable, and the corpus is in-copyright books,
magazines, and personal archives (Reclaiming Quarterly, Fulcrum, the Swann papers, Flynt, Hennix). That is
redistribution, and a takedown mid-run would break every kernel that attaches it. Kaggle kernels can
attach the owner's private datasets. Make the corpus dataset private; leave the base-model datasets
public (their Falcon license notices are already correct). Third-party dialogue datasets (section 7)
likewise cannot be re-published under CC0.

## 5. Ambition: treat `h` as a population and a developmental process, not a model

The roadmap's twelve branches mostly treat `h` as one model to be improved. The thing a 91M model on a
laptop makes possible, and a 70B model never will, is *replication across the whole developmental
trajectory*. That reframing raises the ambition of nearly every branch without adding compute.

### 5.1 Replicates, not a run

At ~13-15K tok/s a corpus pass is ~7 hours. Five seeds or five data orders is a week of nights. Every
interpretability claim in FUTURETHOUGHT ("wet/dry becomes steerable at checkpoint X") turns from an
anecdote into "emerges by 30M tokens in 4/5 seeds at layers 14-17." Nobody publishing steering results
has replicates by default. The developmental checkpoint dataset becomes a *population* dataset:
5 seeds × 6 checkpoints × the same evaluation package.

### 5.2 Belief-geometry metaprogramming, literally

Shai, Riechers et al. (2024) showed the residual stream of a transformer trained on an HMM source carries
the mixed-state simplex of that process: the belief geometry is a linear image of the data's hidden
structure. Two things make `h` an unusually good instrument for this:

- Nobody has checked it for the **Mamba-2 state** of a hybrid, which is an explicit fixed-size
  sufficient statistic, versus the attention residual. The comparison itself is a contribution.
- **We author the corpus.** Weave a slice of the training distribution from a process with a known
  mixed-state presentation (a metasyntax whose transitions are an HMM, a ritual grammar threaded through
  the chat data), predict the simplex, then look for it in the SSM state and the residual across every
  checkpoint of every seed.

If it appears, the wetness knob stops being "a convenient direction" and becomes a coordinate the model
was made to represent. That is an interpretable knob by construction. Controls: shuffled-label,
norm-matched random directions, and a sibling trained without the authored slice.

### 5.3 Model-diffing the possession

Train a crosscoder across base → CPT-10M → CPT-1pass → cooled (→ resident, later). At d=512, 24 layers,
~100M tokens of activations, this is Mac-feasible. The output is a catalogue of features that exist only
in the haunted model, each with the corpus spans that activate it (the haunting index supplies the
provenance). "What did the ghost learn" as a list rather than a vibe, and a direct measurement of what
cooldown and later resident consolidation add or destroy.

### 5.4 Ship the knob into the browser

transformers.js has native `falcon_h1` support (`packages/transformers/src/models/falcon_h1` at main), and
`onnx-community/Falcon-H1-Tiny-Multilingual-100M-Instruct-ONNX` runs with `dtype: "q4", device: "webgpu"`.
Export a variant with one extra input tensor added to the residual stream at layer L; the wetness knob
becomes a steering coefficient on a replicated, validated direction, and the breath animation is driven
by per-token entropy. One caveat to measure first: ONNX Runtime issue 27796 reports prohibitive `Loop`-op
overhead for Mamba scans, so profile the official export's tokens/second in a real browser before designing
the site around live generation.

### 5.5 The social agent, honestly

91M will not track a five-person Discord thread with callbacks the way a person wants. But the ledger in
CODEXOUT is size-independent and more novel than the model: an append-only life history with correct
silences and consent as data fields. Build it first. Then:

- let a larger model annotate speak/silent and addressee labels on the ledger, and supervise a tiny
  participation head on those plus the public When2Speak data (216,800 labeled group-chat decisions);
- let `h` supply the voice while the participation head decides when;
- when a 0.5B or corpus-born sibling exists, it inherits the same life.

The resident's biography becomes the dataset that survives model deprecation. That is the artifact.

### 5.6 What to lower this month

GLaDOS graft, recurrence, vision, and 0.5B distillation do not serve the ghost yet; leave them in
FUTURETHOUGHT. The TPU gets one bounded attempt (section 2). The 91M random-init two-pass control is
scientifically fine but is not the artwork; run it after the mainline exists, on whichever backend is idle.

## 6. Immediate queue

1. Let the OCR re-run finish; then `hghost-review-ocr` sheet, stratified visual sample, tokens/GPU-hour.
2. Make `hghost-curated-tokens-v1` private on Kaggle; make `h-ghost-91m-tpu-experiments` private or
   strip its accelerator.
3. Decide on the ZFS source snapshot (destroy reclaims ~291G on hbox).
4. Write the MLX CPT trainer (FP32 masters, sealed stream, matched schedule, HF round-trip test). Smoke
   at 1M tokens, compare against the hbox 10M specimen at matched exposure, then start pass one overnight.
5. Build the haunting index and the work/edition-family split in parallel (CPU).
6. Patch EasyDeL's Falcon-H1 mixer with the h1jax chunked SSD; CPU parity; then one bounded TPU gate.
7. Re-run the LoRA control on the Mac at matched data order; decide persvati's fate at that point, not
   after 30 more hours.
8. Integrate `causal-conv1d` on hbox with full-model parity; hbox becomes the controls box.
9. Mark or remove the dead kernel directories and `src/hghost/ocr.py`; update README's stale gate text.

## 7. Harvested research (from the transcript, with links)

Done by the Codex root session at 15:06-15:09 [5215]-[5262]; only two names reached the repo.

### Chatroom training and evaluation

| Resource | What it tests or trains | Use for `h` |
|---|---|---|
| [GroupMemBench](https://github.com/UCSB-NLP-Chang/GroupMemBench) | Multi-party memory: updates, time, ambiguity, speaker-specific context, abstention | Blueprint for the memory eval |
| [SocialMemBench](https://arxiv.org/abs/2605.17789) | 4-30-person groups; relationships, norms, individual exceptions | Closest to the actual habitat |
| [MultiLIGHT](https://parl.ai/projects/multilight/) | Three characters; when to talk and in-character generation | Closest existing training set |
| [When2Speak](https://huggingface.co/datasets/duke-trust-lab/When2Speak) | 216,800 SPEAK/SILENT group-chat decisions, optionally with the message | Directly usable supervision |
| [MPCEval](https://github.com/Owen-Yang-18/MPCEval) | Speaker selection, content quality, speaker-content consistency | Rollout evaluator |
| [DSTC8 Ubuntu IRC](https://github.com/dstc8-track2/NOESIS-II) | Interleaved threads, response selection, disentanglement | Authentic chat structure |
| [Molweni](https://github.com/HIT-SCIR/Molweni) | 10K multiparty dialogues, 78K discourse relations | Reply/reference comprehension |
| [LongMemEval](https://github.com/xiaowu0162/longmemeval) | Extraction, multi-session reasoning, updates, abstention | Dyadic; adaptable |

Best reported memory system on GroupMemBench: 46%. The addressee-recognition benchmark
([IWSDS 2025](https://aclanthology.org/2025.iwsds-1.36/)) finds GPT-4o marginally above chance, which is the
argument for explicit `author`, `reply_to`, and participant IDs in the metasyntax. Also:
[Character Identification](https://aclanthology.org/S18-1007/), [DialogRE](https://aclanthology.org/2020.acl-main.444/),
[Who Is Speaking to Whom?](https://aclanthology.org/D19-1199/), [FriendsQA](https://aclanthology.org/W19-5923/),
[GroupGPT/MUIR](https://github.com/Eliot-Shen/GroupGPT), [SPASM](https://aclanthology.org/2026.findings-acl.412/)
for synthetic multi-party generation, [PersonaEval](https://arxiv.org/abs/2508.10014) (LLM judges ~69% vs
humans 90.8% at role identification; prefer graph-derived exact answers).

### Long context and continual learning

Lost in the Middle (2307.03172), ProLong (2410.02660), Artificial Needles (2406.19292), Position
Interpolation (2306.15595), YaRN (2309.00071), LongRoPE2 (2502.20082), LongLoRA (2309.12307). Continual:
Ibrahim et al. (2403.08763), Replay and Gradient Alignment at 99M (2508.01908), Sharpness-Aware
Pretraining 20M-150M (2605.02105), O-LoRA (2310.14152), CaMeLS token weighting (2305.15076).

### From this session's Kagi searches

- Compiler-first SSD in JAX: Santoni & Thapar, arXiv 2603.09555, github.com/CosmoNaught/mamba2-jax
  (inference-focused; ~15% MFU prefill on v6e; the chunked einsum form is what matters for us).
- Pallas Mamba-2 SSD prefill kernel for TPU: github.com/medusa-compute/jagged-mamba2 (forward only, v6e,
  40 TFLOP/s, pinned to JAX 0.10.0/libtpu 0.0.40). A backward would be new work.
- JAXBench (arXiv 2607.20466) extracts a Mamba-2 operator from MaxText, so a MaxText SSD reference exists.
- transformers.js `falcon_h1` support and the onnx-community Tiny-H1 WebGPU q4 export (section 5.4).
- ONNX Runtime issue 27796 on `Loop`-op overhead for SSM scans (section 5.4 caveat).
- Kaggle TPU docs: 20 h/week, 9 h/session; v5e-8 availability complaints through 2026.

### ChapterX seams (from child agent 01a05e7f [116], not in the repo)

Already present: multiparty abstraction `src/types.ts:16,:39`; serialized per-channel loop
`src/agent/loop.ts:495,:774`; raw Discord IDs/reactions `src/types.ts:472`, `src/discord/connector.ts:2387`;
base-model route `src/llm/membrane/provider.ts:29`, `factory.ts:1085`; plugin state `src/tools/plugins/types.ts:124`,
`state.ts:171`; steering seam `src/steering/types.ts:1`, `loop.ts:1628`; traces `src/trace/types.ts:12`.

Gaps: non-activations unrecorded (tracing after `shouldActivate()`, `loop.ts:537,:687`); unseeded
`Math.random()` participation (`loop.ts:1427`); reply topology reduced to `<reply:@name>` and stripped
(`connector.ts:2467`, `format-messages.ts:369`, `loop.ts:3565,:3603`); consecutive bot messages merged
(`context/builder.ts:80,:182`); character-based budgets (`cache-and-limits.ts:22`); provenance is a string
(`types.ts:174`); traces redact only `discord_token` (`trace/collector.ts:127`, `config/system.ts:348`) with
bodies auto-written (`provider.ts:467,:537`); epic state is not resident memory (`loop.ts:1899`,
`context-factory.ts:103`); formatter seam `factory.ts:887`, `provider.ts:96`. Ledger ingress point:
`connector.ts:2210`; memory injection point `loop.ts:1845`; `test-channel-replay.ts:76` is not a true replay.

## 8. Loose ends from the transcript not listed above

- Critical-init paper (arXiv 2111.12143) was opened twice, never reported.
- PDF text-layer backpatching designed only.
- Data-prep tranche requested at 13:06 never started beyond a gap list.
- The 91M random-init 2× control exists only in the abandoned custom-JAX kernels.
- 29.8 GB ROCm build image on hbox (keep; it built the working wheel).
- The project was seeded by pasted external-model syntheses (`h.h`, [579], [2872], [3502]);
  `claims_audit.md` separates them from evidence but their provenance is not recorded.

## 9. What I believe, in one paragraph

The corpus work today was excellent and the numerical hygiene, once it was applied, was real. The day
lost most of its accelerator time to an account setting, an unacknowledged launch, and a per-token scan
nobody read before betting the gate on it. The fix is not more roadmap. It is one clean pass on the
machine that already runs this model fastest, an evaluation pack that can tell memorization from
learning, and then the thing only a tiny model affords: five of them, watched from birth, with the knob
built into their beliefs on purpose.
