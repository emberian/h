# The 91M recipe: pre, mid, post, with evidence and arms

> **Status 2026-09-02 01:20.** The trunk arms below (seeds, WD, LR, MIR, SimReg, 8 epochs) are parked: ember
> decided no further 91M training runs; the resident line moved to Falcon-H1-0.5B on the room-mixed stream.
> MIR measured: 3.279 vs 3.280 plain at equal tokens, twice the compute. The 91M stays the site's ghost and
> the instrument (judge, population, interpretability). See `research/results/night-2026-09-02.md`.

Written 2026-09-01, 23:50. This is the confident version, assembled from TII's own Tiny-H1 recipe
(`research/sources/tiny_h1_blog/`), tonight's measurements, and the literature pass. Each stage lists what
we know, what we do, and the arm that tests it. Kernels for every arm are generated from
`kaggle/tpu_h1jax_cpt/run.py` with `kaggle/make_leaf_kernel.py`; one epoch is ~17 minutes at SSD v2.

## What TII did to make this exact model (and what transfers)

| Their choice | Number | Transfers to our CPT? |
|---|---|---|
| Optimizer | Muon (WD applied, update RMS matched to AdamW), same optimal LR as AdamW | Later arm; AdamW is fine for CPT |
| µP + 35 forward multipliers, learnable row/column multipliers (LRM) | LRM: up to +20% relative on MMLU/BBH/GSM8K | Multipliers are baked into the released config; LRM not needed for CPT |
| LR / WD / batch | 2.56e-3 under µP, WD 0.1, 4M-token batches, batch ramp-up | LR does not transfer (µP scaling); WD 0.1 and batch ramp do |
| Schedule | WSD: 100M warmup, stable, ×64 exponential decay over the last 100B of 800B | Our trunk-and-leaves is the same shape at 1/500 scale |
| Repetition | "memorization window" ≈ 5B tokens for a 100M model; HQ sources repeated 100+ times | Our 374M-token corpus fits the window ~13×; 4–8 epochs is safe by their measure |
| Specialized data | SFT-*pretraining* beats curriculum SFT (IFEval 50.1 vs 40.8; 66.1 vs 53.5 after DPO); best mix 25% SFT, 75% base ("pretraining data is essential") | Room/persona data goes into the mix at ≤25%, not into a separate SFT |
| Reasoning traces | chain-of-thought sources made the 90M loop; filtered out | No CoT, ever |
| Tool calling | pretrain-SFT ≈ curriculum SFT; BFCL v3 41.2% at 85% tool data in the SFT mix | Reachable if we ever want ChapterX tools; same 25% rule applies |
| DPO | large IFEval gains, degradation after >1 epoch | One epoch of aesthetic DPO, no more |
| Depth/width | 27-layer × 512 chosen over 50 × 384 for throughput | n/a |
| Future work they name | model merging of small models; multi-epoch and forgetting-window study | Our seed soups and epoch curves are exactly these |

## Pre-training (the trunk)

Known tonight: 4 epochs at LR 1e-4 constant took validation 3.787 → 3.163, still falling; a 10%-of-an-epoch
cooldown is worth about an epoch (3.280 → 3.234 at epoch 1, 3.163 → 3.136 at epoch 4). Train/validation gap
grows 0.15 → 0.27 over four repeats.

Do: WSD trunk, 8 epochs (inside TII's window), leaves cooled from epochs 1, 2, 4, 8; weight decay 0.1 vs
0.3 (data-constrained scaling says heavier); LR 1e-4 vs 3e-4; MIR at 0.4 vs a batch-matched control;
three seeds of the winner, then a soup. Every checkpoint carries in-run rollouts (greedy and sampled
continuations of the fixed prompts) so the memorization scan runs the moment a log lands.

Arms queued or generated: `trunk-seed1/2`, `leaf-s1-e1/e4`, `trunk-mir` + `trunk-plain32`, `trunk-wd03`,
`trunk-lr3e4`. Next: `trunk-8ep` (seed 0 continued to 8 epochs) with leaves at 6 and 8.

## Mid-training (representation geometry, sparsity, the room)

This is the stage ember asked about: optimize the representation, not just the loss.

1. **Separation: SimReg-style token contrastive regularization.** SimReg (arXiv 2605.08809) adds a loss that
   pulls together hidden states of tokens sharing the same next-token label within a sequence and pushes
   apart different-label tokens; reported >30% faster convergence and >1% average zero-shot gain in
   pretraining (dense and MoE). Cheap here: a 512×512 Gram per sequence on the final hidden state. Arm:
   `HGHOST_CPT_SIMREG_WEIGHT` in the kernel (supervised-contrastive form, temperature 0.1), one epoch
   branched from the epoch-4 checkpoint, against the plain leaf. Measure: evaluation pack, plus
   representation dispersion (mean pairwise cosine of hidden states on validation) and the crosscoder diff.
2. **Geometry we can watch.** "Linguistic Collapse" (arXiv 2405.17767) finds neural-collapse-like geometry
   in LMs correlating with generalization; "Structure Before Collapse" (arXiv 2606.26749) shows semantic
   clustering is transient before collapse; "Flatness is Necessary, Neural Collapse is Not" (arXiv
   2509.17738) shows flatness is the thing that predicts generalization and collapse merely co-occurs. So
   the instrument is flatness (sharpness per parameter family, already planned) and dispersion, not
   collapse itself; the lever with evidence is sharpness-aware training in the cooldown (Sharpness-Aware
   Pretraining, arXiv 2605.02105, 20M–150M models, up to 80% less forgetting). Arm: `leaf-sam` (SAM only
   during the decay) vs the plain leaf, judged on retention and on post-training plasticity.
3. **Sparsity.** TopK Language Models (arXiv 2506.21468) put a TopK activation at chosen layers so hidden
   states are SAE-like by construction, with steering by neuron intervention and feature stability across
   checkpoints; trained from scratch in the paper, retrofit untested. Arm (tomorrow, risky): insert TopK on
   the residual at 2–3 layers with a large k (e.g. 128 of 512) during a one-epoch continuation and see
   whether loss recovers; if it does, the site's knob gets a neuron address instead of a direction.
   "Beyond the Hard Budget" (arXiv 2606.27321) has softer sparsity regularizers if the hard TopK is too
   violent for a retrofit. The weight-sparse sibling (OpenAI 2025) stays a later interpretability branch.
4. **The room as a genre.** Corpus-native interviews, Gutenberg dialogue, When2Speak/MultiLIGHT rooms with
   `h` as a participant, ≤25% of the mix per TII, in the exact `name: text` format the harness renders
   (`research/resident-treatments.md`; builder running). Arm: `trunk-room` branched from epoch 4, one epoch
   at 15% room mix, cooled; judged on the evaluation pack, room-validation loss, and speak/silent accuracy.
5. **Context.** Length mixture (2K/4K/8K on real books) in the last epoch only, after the above.

## Post-training (persona, social cognition, tools; still not an assistant)

- **Persona by experience, not instruction:** Character-LLM (arXiv 2310.10158) scenes generated from
  corpus passages with `h` present, with protective scenes; kept inside the mix at ≤25% (TII), one epoch.
- **Social cognition, honestly:** "Small LLMs Do Not Learn a Generalizable Theory of Mind" (arXiv 2507.15788):
  training small models on HiToM/ExploreToM/FANToM improves in-distribution only and RL hacks statistics.
  So we do not chase ToM benchmarks; we train and measure *room* competence (who is speaking to whom, what
  was said, when to stay silent, what changed) with graph-derived exact labels (RoomBench-H-lite).
- **Tools:** TII got BFCL 41% at 90M with 85% tool data; if `h` ever needs ChapterX tools (memory
  lookups, the haunting index as a citation tool), the same in-mix approach applies, no CoT.
- **Preferences:** one epoch of DPO on aesthetic pairs from room reactions; stop.
- **Steering:** trained additive vectors with reward (RL-steering paper in the bibliography) as the knob;
  dose–response and controls before any claim.

## Order of operations from here

1. Tonight's queue (replicates, MIR pair, WD, LR) → morning evaluation table with furniture-free and clean
   slices, memorization, retention.
2. SimReg arm and 8-epoch continuation (kernel flags exist or are trivial).
3. Room-mix arm when the builder lands (needs one Kaggle dataset upload).
4. SAM-cooldown leaf; TopK retrofit probe.
5. Persona scenes and the participation head; then the site and the room get the winner.
