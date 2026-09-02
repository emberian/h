# Overnight log, 2026-09-01 → 09-02 (Claude Fable 5.1)

Running log of the autonomous session ember authorized ("make h the best it can be until 8am"; TPU budget
raised from 1.5 h to the full weekly 20 h at 19:05, spent in bounded, reported increments). Newest at the
bottom. `FABLETHOUGHT.md` has the review and proposals; `kaggle/TPU_LEDGER.md` has every TPU launch.

## 18:05–19:00

- OCR server had died with the Codex session; relaunched server and worker in tmux (`hghost-mlx`,
  `hghost-ocr`), `--limit 46` completes the original 100-document tranche. 10/46 done by 19:25, no errors.
- `FABLETHOUGHT.md` written (review, EasyDeL verdict, ambition proposals, harvested research).
- persvati LoRA diagnosed as thermal throttling (600 MHz at 89 °C, co-tenant solana validator).
- hbox ZFS replica verified complete (GUIDs match, 16/16 snapshots); source snapshot destroy left to ember.

## 19:00–19:25

- Built `kaggle/tpu_h1jax_profile_gate` (measurement kernel on the exact `h1jax` port: SPMD sharding,
  per-shape memory/cost analysis, async timing, component benches, base-eval parity, loss sanity) and
  `kaggle/tpu_h1jax_cpt` (resumable CPT with developmental checkpoints and a wall-clock budget guard).
  Both rehearsed on CPU with eight simulated devices; the CPT budget-stop → resume path reproduces the
  original run's losses step for step.
- Gate v1 on TPU (19:03, ~11 TPU-min): TPU v5e-8 acquired immediately; **JAX base validation loss 3.7456 on
  the same 32 × 512 slice hbox measured, identical to Transformers to four decimals**; then the host
  `Killed` the process while compiling the Python-unrolled 24-layer train step. The 0.5B smoke earlier
  today died the same way (36 unrolled layers). Root cause: compile cost of unrolled depth.
- Fix: `h1jax` 0.1.4 adds `layer_scan=True` (one `lax.scan` over stacked layer parameters); parity test
  against the unrolled forward/backward passes at 1e-5 (with and without remat). Wheel uploaded as a new
  version of `emberian64/hghost-jax-code-public`. Host/cgroup memory probes added to both kernels.
- `mlx_lm.server` verified as an OpenAI-compatible `/v1/completions` server for Falcon-H1 HF checkpoints;
  ChapterX resident config drafted under `chapterx/` (vendor snippet, bot yaml, `serve-h.sh`).
- Subagents running: haunting index (suffix array over corpus-v1), work/edition-family split analysis,
  and the h.fg-goose.online site scaffold under `site/`.

## 19:25–19:30

- Gate v2 (layer scan, memory probes) pushed at 19:25; running.
- CPT kernel gained `HGHOST_CPT_SCHEDULE=wsd` (warmup, stable, cosine decay over the last `DECAY_TOKENS`) and
  `HGHOST_CPT_BRANCH_FROM` (start a new run from any trunk checkpoint, continuing data order and optimizer
  moments with its own decay). Multi-epoch is just a larger total. Rehearsing trunk → leaf on CPU.
- Browser deployment sizes from the official Tiny-H1 ONNX export (100M multilingual instruct): q4 154 MB,
  q4f16 113 MB, fp16 250 MB, fp32 499 MB. Larger than a pure 4-bit weight count because embeddings/head
  stay unquantized; still inside the site budget.

## 19:40 — haunting index built (`hghost-haunt`, `research/results/haunting-index.md`)

- Token-aligned suffix array over all 374.4M training tokens (`artifacts/haunting-index/`, 1.5 GB int32),
  built in ~5.6 min wall (~2 min of CPU), peak 7.6 GB. Document offsets reconstructed from the dataset
  manifest match the EOS scan exactly (0 mismatches).
- Positive control: 2,000 tokens copied from train match as one 2,000-token span with the right document.
- **Validation head (MagazineStudies.2.pdf): 34% of positions covered by >=8-token spans present in
  train, 20% by >=32-token spans, all of it furniture** (JSTOR "This content downloaded from ..." stamps,
  the 197-token JSTOR license paragraph, "All use subject to ..."). The 10M checkpoint's loss drop is
  measured on text like this; every eval must subtract furniture from now on.
- Furniture detector output: 681 documents share " . . . ." leaders; 284 carry the Library of Congress
  CIP line; 270 the archive.org banner; 147-161 the Kahle/Austin funding line; 110 documents *begin* with
  a 46-token "mirrored file at SaturnianCosmology.Org" head; Kronia/Velikovskian footers, THOTH mastheads,
  ADF addresses, JSTOR/Reveal Digital notices. Lists in `research/results/haunting-index/`.

## 19:40 — gate v2 PASSED; trunk launched

- `h1jax` on v5e-8: **219,722 tok/s, 9.5% MFU, 28 min per corpus pass** at 64 × 512 per chip with remat
  (no-remat shapes need 24-49 GB HBM; activations ~3 MB/token). SSD scan is 54% of step time; matmuls hit
  66% of peak. Base eval 3.7458 (hbox 3.7456). 10.5M-token sanity at LR 3e-5: fixed-slice loss 3.75 → 3.41.
  Full write-up: `research/results/tpu-h1jax-gate.md`.
- 19:39 launched `h-ghost-h1jax-cpt-91m` v1: WSD trunk, LR 1e-4 (warmup 10M tokens, then constant), weight
  decay 0.1, 64 × 512 remat, **4 epochs = 1.498B tokens (~2 h)**, checkpoints with optimizer state at 10M,
  30M, 100M, 200M, and every epoch; eval every 25M tokens on 512 validation sequences plus the fixed
  32-sequence slice. Budget guard at 400 min. A non-finite loss saves a checkpoint and ends the run.
- Next on the TPU after the trunk: cooled leaves from the epoch-1 and epoch-4 checkpoints (decay over ~10% of
  an epoch each), then a second seed, then the 0.5B pilot.
- persvati's LoRA control is now scientifically redundant (a matched LoRA on the TPU is minutes); it is left
  running because it has no checkpoint yet and stopping it is ember's call.

## 19:41–19:47 (times below were first written as guesses; corrected against `date`)

- `kaggle/make_leaf_kernel.py` generates derived kernels from the single CPT source (defaults rewritten,
  trunk output attached as a kernel source). Generated and lint-checked, not pushed: `tpu_h1jax_leaf_e1_decay10`
  (cool from the epoch-1 checkpoint over 37.4M tokens), `tpu_h1jax_leaf_e4_decay10`, `tpu_h1jax_trunk_seed1`.
- Evaluation-pack subagent started: plain and furniture-subtracted validation losses, blind fixed-seed
  generations via mlx-lm, memorization scan via the haunting index, generic-English retention proxy; baseline
  on the base model and the hbox 10M checkpoint (fetched read-only from hbox).

## 19:48 — plan for the TPU after the trunk (one session at a time on Kaggle)

1. `leaf-e1-decay10`: cool the epoch-1 checkpoint over 37.4M tokens (~8 min incl. boot/compile).
2. `leaf-e4-decay10`: same from the epoch-4 checkpoint.
3. MIR arm: 1-epoch trunk with `MIR_WEIGHT=0.4` at 32 × 512 per chip (two forwards per step; ~1 h).
4. `trunk-wsd-lr1e-4-seed1`: the first replicate (4 epochs, ~2 h) if the seed-0 curve looks healthy.
5. 0.5B pilot: tokenizer compatibility checked below; needs its own memory shape.
Evaluate everything with `hghost-evalpack` (subagent building it) plus the haunting scan.
- 0.5B tokenizer check: identical to the Tiny tokenizer (all 32,768 entries, merges, pre-tokenizer);
  its config merely pads the embedding to 32,784. Corpus-v1 streams are valid input for the 0.5B.
  Generated `kaggle/tpu_h1jax_pilot_05b` (8 × 512 per chip, remat, 30M tokens, LR 5e-5, cosine).

## 19:50 — family split done (`hghost-families`, `research/results/family-split.md`)

- 4,868 documents → 4,273 families; 244 multi-document families hold 17.3% of tokens; 122 periodical
  series cover 45.6% of documents.
- Current validation: 7.6% of tokens have a same-work twin in train at low-or-better confidence (one
  article is 83% contained in a train magazine issue; a Bertiaux part has its siblings in train), 26.7% are
  periodical issues with hundreds of sibling issues in train, 65.7% (12 documents) are clean. The 10M loss
  drop is therefore mostly real, and the honest held-out slice for tonight's checkpoints is those 12
  documents (evaluation pack asked to report it).
- Proposed for corpus-v2: family-, series-, and weak-link-free validation (118 docs, 2.96M tokens) and
  test (72 docs, 2.54M tokens), stratified over 17 source/directory strata; the magazines stratum cannot
  be filled without holding out whole periodical titles, which is a curation decision. 44-entry review
  queue for the largest ambiguous families (Whole Earth Catalog editions 4.7M tokens, Vollmann epub+pdf
  3.2M, "Investigations into Magic" vols 3.0M, 36 Langman Lanza page-saves 3.0M, ...).

## 19:52 — MIR arm rehearsed; derived kernels regenerated

- `HGHOST_CPT_MIR_WEIGHT` works on CPU: masked auxiliary loss ~6 at the expected mean 24% corruption,
  total = clean + 0.4 × masked, clean `loss` remains the comparable metric. Layer-scan vs unrolled BF16 runs
  diverge by ~1e-4 per step in loss (accumulation order), as expected.
- All derived kernels regenerated from the final source: `leaf_e1_decay10`, `leaf_e4_decay10`,
  `trunk_seed1`, `pilot_05b`, `trunk_mir` (1 epoch, MIR 0.4, 32 × 512 per chip because two forwards need
  the HBM), and `trunk_plain32` (the batch-matched control for the MIR arm). None pushed yet.

## 19:54 — site scaffold done (`site/`, `site/README.md`)

- Static site, no bundler: hand-authored midsagittal vocal-tract SVG with a glottis inset, phase-continuous
  breath clock, Web Audio /h/ synth morphing dry → humid → gargle with the oversized Wetness knob (spring,
  condensation, localStorage), two-layer skyline that tilts and sinks per breath, breath counter, and the
  ghost: transformers.js 4.2.0 in a module worker (WebGPU, WASM fallback) generating breath-length
  fragments seeded by wetness band, breath count, and minutes on page. Per-token entropy comes from a custom
  LogitsProcessor (the library never returns scores) and drives the h's glow and breath period.
- Verified headless (Chromium via playwright-core): zero console errors with the ghost on and off; the q4
  model (~154 MB) loaded over WebGPU and murmured. Unverified: real-GPU speed, Safari, audibility.
- Run: `cd site && python3 -m http.server 8000`. Model id/dtype/localPath in `site/config.js`.
- Still loads the stock `onnx-community` Tiny-H1 instruct export; exporting our own checkpoints to ONNX is
  the next deployment step (subagent started).

## 19:58

- Profiler trace of the gate aggregated by op (`research/results/tpu-h1jax-gate.md`): matmuls 38% of the
  step, data-formatting copies/reshapes 20%, elementwise 12%, cumsum reduce-windows 6.5%. The chunked SSD's
  materialized head-repeat of B/C and cumsum segment sums are the cheapest next 15-25%; deferred, not
  needed tonight.
- Belief-geometry subagent started: Mess3 hidden-process generator with exact Bayesian beliefs, three rare
  single-id emission tokens, a corpus-v1.1 stream with the synthetic slice inserted at ~2% (v1 bytes intact
  outside insertions; Kaggle-uploadable), and a layer-wise linear probe from residual stream to the belief
  simplex, run first on the base checkpoint as the control baseline.
- Load on the Mac right now: OCR (GPU), evaluation pack (CPU + mlx generation), ONNX export (CPU),
  belief-geometry build (CPU).

## 20:30 — account rotation

- The session hit its API limit and ember rotated accounts; the harness restarted. The belief-geometry agent
  had not started, the evaluation-pack and ONNX-export agents were mid-work; all three were resumed by
  message. tmux jobs (OCR server, OCR worker, the site's local http server) and the Kaggle trunk were
  unaffected. Trunk status at 20:30: RUNNING (50 min).
- OCR viewer added (`hghost-ocr-view`, output `artifacts/ocr-viewer/index.html`): page render with layout
  boxes overlaid, recognized text beside it, hover to pair.

## 20:40–20:58 — published, and the SSD rewrite

- Pushed four commits (h1jax + TPU kernels; haunting index + families; review/log/ChapterX/OCR viewer;
  site + Pages workflow). GitHub Pages enabled with workflow builds, custom domain `h.fg-goose.online`
  (ember set the DNS CNAME), HTTPS enforced. **The site is live at https://h.fg-goose.online/** loading
  the public Tiny-H1 ONNX from the Hub; our own checkpoints follow once the export lands.
- `ssd_forward_v2` in `h1jax` 0.1.5: group-shaped B/C (no 24× head repeat), single cumsum with masked
  difference for the intra-chunk decay (masking before `exp`, which is where a NaN in the dt gradient
  came from and was fixed), explicit two-matmul intra-chunk product, chunk-state scan. Parity with the
  reference: forward 2e-6 relative, all gradients ≤ 1.3e-4, test added. Selected by `H1JAX_SSD=v2`;
  default stays `v1`, so the trunk's leaves keep the trunk's math.
- `kaggle/tpu_h1jax_ssd_bench`: times the full training step for v1 / v2 / v2-bf16 and the bare SSD
  forward+backward; runs after the trunk and leaves (one TPU session per account).

## 21:00 — belief-geometry instrument done (`hghost-beliefgeo`, `research/results/beliefgeo-baseline.md`)

- Mess3 generator with exact Bayesian beliefs; emission glyphs `∇ ∂ ←` (corpus counts 119/302/105) with
  prefix `│`; corpus-v1.1 stream with 14,866 synthetic documents = 2.0001% of 382.0M tokens, v1 bytes
  verified identical outside insertions, Kaggle layout ready (not uploaded); residual-stream and per-token
  Mamba-state probes (state recurrence parity-checked against `ssd_forward` at 1.2e-6).
- **Negative result that saves a TPU arm:** with the paper's x=0.15, α=0.6, a linear probe from the last
  16 one-hot symbols explains R² 0.987 of the belief; the base model's residual reaches 0.999 at layer 3
  and the SSM state 0.9996 at layer 0, shuffled controls ≈ 0. Mess3 belief is near-linear in recency, so it
  cannot distinguish an authored representation from ordinary recency features. Use a process whose belief
  is not recency-linear (RRXOR-like or longer memory) for the "made to represent" experiment; report MSE and
  depth profiles rather than R² when the arm runs.

## 21:08 — TPU queue armed

- `kaggle/tpu_queue.sh` runs in tmux `hghost-tpu-queue`: waits for the trunk, then pushes and waits for
  `leaf-e1-decay10`, `leaf-e4-decay10`, and the SSD bench in order, downloading each finished output to the
  session scratchpad; stops at the first failure. Log: scratchpad `tpu-queue/queue.log`.
- `h1jax` 0.1.6 adds `H1JAX_REMAT_POLICY` (selective rematerialization: keep batch-free matmul outputs);
  the bench compares v1, v2, v2-bf16, and v2 + selective remat on the full training step.
