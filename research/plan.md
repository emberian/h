# H-Ghost staged research plan

## Decision in one paragraph

The hbox full-CPT run was deliberately interrupted after its first durable 10M-token checkpoint. That
checkpoint already improves the fixed validation slice and changes generation strongly, but it exposed an
unfused Mamba fallback and BF16 parameter/moment update quantization. Do not resume that exact recipe. Keep
the 90M-versus-0.5B bakeoff as the next scale decision after the production backend uses FP32 master state
with BF16 compute. Treat MIR, blockwise learning rates, late SAM, recurrence, synthetic data, steering,
introspection, and GLaDOS as gated branches after a clean H1 baseline exists.

## What is already running

| Machine | Job | Scientific role | Action |
|---|---|---|---|
| hbox | H1-Tiny-90M full CPT stopped at 10M | Precision/kernel diagnostic | Preserve the checkpoint; do not resume the BF16-state fallback recipe. |
| persvati | H1-Tiny-90M LoRA, matched corpus stream | Adapter control | Let it run; stop only if clearly dominated after matched evaluation. |
| nextop | PaddleOCR-VL extraction | Corpus-v2 growth | Continue asynchronously; admit OCR text only through quality and dedupe gates. |
| Kaggle | EasyDeL 91M real-data TPU smoke completed | Fast mainline/challenger path | Benchmark production shapes, rematerialization, and checkpoint resume before a full pass. |

## Stage 0 — freeze the scientific substrate

The sealed corpus-v1 remains the common input for every matched comparison. OCR output becomes corpus-v2;
it must not silently change the data underneath an active experiment.

Before comparing checkpoints, finish these CPU-side artifacts:

1. A work/edition-family split with no near-duplicate leakage.
2. Held-out target text scored in bits per byte, because the H1 tokenizers differ.
3. A small generic-English retention set.
4. A fixed prompt-and-seed fragment suite.
5. Exact and near-exact 8/16/32-gram overlap checks against training text.
6. A checkpoint manifest containing data revision, tokenizer revision, tokens seen, optimizer state,
   learning-rate phase, and code commit.

## Stage 1 — inherited H1 bakeoff

### Candidates

| Candidate | Inherited training | Current official config | Deployment evidence |
|---|---:|---|---|
| Falcon-H1-Tiny-90M-Base | 800B tokens in TII's Tiny recipe | 24 layers, width 512, tied 32,768 vocabulary | Existing official Tiny quantizations are far below the 500 MB ceiling. |
| Falcon-H1-0.5B-Base | 2.5T tokens | 36 layers, width 1024, untied 32,784 vocabulary, 16K context | Official 0.5B Instruct GGUF is 315 MB Q4_K_M, 371 MB Q5_K_M, and 430 MB Q6_K. |

The GGUF sizes demonstrate the architecture's deployment envelope; a lo2 CPT checkpoint still needs its
own conversion and quantization validation.

### TPU preflight

Do not replace the known-good 91M fallback until all of the following pass without accelerator time or in a
very short TPU gate:

1. Load the pinned 0.5B config and checkpoint into the JAX implementation.
2. Match parameter names, shapes, parameter count, and reference logits on a tiny CPU/GPU parity case.
3. Compile a rematerialized full backward step at sequence length 512.
4. Confirm per-core memory headroom with FP32 parameters/Adam moments and BF16 compute.
5. Run two finite-loss steps and save/reload an HF-compatible checkpoint.

The JAX model is configuration-driven, but the 0.5B checkpoint is not yet a proven path. Its untied LM head,
larger SSM, 36 layers, and memory footprint make this a real gate rather than a config-file rename.

### Matched pilot

Run both scales on the same first 10M–20M corpus tokens, data order, validation slices, and precision. Probe
three conservative CPT learning rates per scale only if a single default is unstable or obviously inert.

Record after compilation:

- target bits-per-byte change per hour;
- generic-retention change per hour;
- tokens/s and useful model FLOP/s;
- peak memory and compile time;
- gradient/update norms and finite-value checks;
- fixed-prompt samples.

Choose 0.5B when its qualitative gain is compelling and its target-loss improvement per hour is reasonably
close to Tiny's. Otherwise, put the quota into Tiny. The suggested 70% threshold is a project heuristic, not
a claim from the literature.

A dense `6ND` estimate puts one 374.4M-token pass at about 205 PFLOP for 91M and 1.17 EFLOP for 0.52B.
The larger model may use the TPU better, so wall-clock measurement—not nameplate FLOPs—decides the branch.

Do not co-run LoRA on four of the eight TPU cores. Data-parallel full-model training on all eight cores is
the cleaner utilization regime, while Persvati supplies the concurrent LoRA control.

## Stage 2 — clean CPT trajectory

For the selected scale:

1. Broad assimilation on the deduplicated corpus, with a small generic replay fraction only if the matched
   pilot shows retention damage.
2. Target-heavy phase after the learning rate has materially decayed.
3. A clean, untagged cooldown on the best extracted and source-balanced material.

Save developmental checkpoints at least at 0, 10M, 30M, 100M, 200M, and one corpus pass; continue to later
passes only while validation, novelty, and memorization evidence justify them. Reshuffle the whole work-level
corpus each epoch. Do not hammer a small prestige subset throughout training.

Preserve both:

- the last checkpoint before the final learning-rate cooldown (`flat-candidate`); and
- the final cooled checkpoint (`cooled`).

Later posttrain the two with an identical tiny behavior dataset. This nearly free branch tests whether the
less-cooled checkpoint is a more plastic and quantization-robust substrate, without rerunning CPT.

## Stage 3 — learning-mechanics instrumentation

Instrumentation is welcome on the main run; unvalidated optimizer changes are not.

At saved checkpoints, record per parameter group:

- parameter RMS, gradient RMS, update RMS, and update/weight ratio;
- activation RMS and saturation/finite-value summaries;
- diagonal-Fisher or Hessian-vector sharpness estimates on a fixed micro-validation sample;
- groups for embedding/head, norms, attention QK, attention VO, MLP, SSM projections, SSM dynamics,
  and depthwise convolution.

The Sharpness Disparity paper's fixed Transformer multipliers—embedding 10×, QK 8×, FFN 6×, VO 4× relative
to norm—must not be copied into H1 CPT. H1 adds SSM and convolutional groups, and the paper studies
from-scratch GPT/LLaMA training. Use the first measurements to decide whether an H1-specific A/B is warranted.

`Generalization at the Edge of Stability` motivates trajectory analysis; it is not an instruction to push
AdamW CPT to the edge of numerical failure.

## Stage 4 — bounded sample-efficiency A/Bs

Run these only from a shared checkpoint and for 20M–40M matched tokens or equal wall-clock time.

### MIR

Compare ordinary next-token prediction with clean-plus-masked next-token prediction. The paper's selected
setting samples a mask ratio uniformly from 0 to 0.5 and uses auxiliary weight 0.4.

Important limitation: MIR was demonstrated in from-scratch Llama-style models with 100M–400M unique tokens,
16–64 selected epochs, and unusually strong tuned weight decay. It has not been established for CPT of a
trillion-token-pretrained H1. Because the clean and masked branches roughly double training arithmetic, the
decision metric is validation gain per wall-clock hour, not gain per optimizer step.

### Late SAM

If downstream plasticity or 4-bit robustness matters, compare ordinary cooldown with SAM only during the last
roughly 10% of a matched branch. The cited work reports that late SAM recovers much of full-SAM's robustness
benefit while adding roughly the annealing fraction in total compute. It is still an OLMo result, not an H1
CPT result.

### Blockwise learning rates

Only run this branch if the measured H1 groupwise curvature ordering is stable across checkpoints. Derive
conservative H1-specific multipliers; include an ordinary-AdamW control with identical schedule and tokens.

Kill any method that does not improve target bits per byte per hour, generic retention, or later behavior
learning in a preregistered comparison.

## Stage 5 — post-CPT behavior without making a chatbot

Use the original PDFs as substance. Use larger models mainly as annotators, critics, relation extractors, and
reward-model assistants—not as bulk ghostwriters.

Start with short corpus-grounded transformations and controls:

- contrast two source spans;
- identify a premise, objection, implication, or terminological distinction;
- paraphrase without stylistic normalization;
- produce a short fragment under explicit page-state controls;
- provide source spans and machine-checkable provenance for every synthetic item.

Keep synthetic material a small, separately versioned mixture. A first 5%–15% pilot is enough to learn
whether it helps. Long chain-of-thought imitation is a poor default at 90M and conflicts with TII's own Tiny
tool-calling observations.

Once good generations exist, collect human aesthetic preferences over matched candidate pairs. Run one short
DPO pass and stop on held-out preference quality, corpus loss, and generic retention. TII's Tiny-H1 source
reports rapid degradation after the first DPO epoch even while DPO reward continues to rise.

## Stage 6 — developmental mechinterp and steering

Apply the same analysis suite to every developmental checkpoint:

1. Build paired examples for candidate axes such as analytic/incantatory, concrete/abstract,
   ecstatic/austere, terse/discursive, and wet/dry.
2. Measure linear decodability across layers, authors, topics, and held-out works.
3. Extract mean-difference/persona-style residual directions.
4. Establish causal dose-response with activation addition and subtraction.
5. Include norm-matched random directions, shuffled labels, held-out concepts, layer sweeps, and quantized-model
   replication.
6. Track whether directions emerge, rotate, compose, or disappear across CPT and cooldown.

Call these style/affect directions until causal and identifiability controls justify stronger language.
Multiple non-identical vectors can produce similar behavior; no single vector should be described as the
unique neural location of an emotion.

After ordinary steering works, train tiny frozen-model steering vectors with a preference or verifiable
reward. Compare them with LoRA/full posttraining on quality, parameter count, compositionality, and causal
legibility.

## Stage 7 — strict internal-state monitoring experiment

This is a later replication, not evidence of consciousness.

Branch the same CPT model into no-posttraining, SFT, and DPO conditions. Inject held-out concept directions
and ask for a minimal structured report. Include the strongest skeptical controls from the Reality Check:

- matched input perturbations versus internal activation perturbations;
- random and semantic directions;
- randomly relabeled concepts;
- unseen injection strengths and layers;
- a classifier that sees only the input;
- false-positive rates fixed before comparing true-positive rates.

The positive 2026 paper studies much larger models and finds the behavior after contrastive preference
training. Whether 90M has enough capacity is genuinely open.

## Stage 8 — one recurrence branch

Recurrence is a storage-efficiency experiment, not the primary TPU-compute optimization.

If a slot remains, compare a dense 30M–70M corpus-born model with one simple gated prelude/core/coda model at
equal wall-clock time and training FLOPs. Mixer-only recurrence is a second option only after the dense and
gated baselines work. Kill the branch if it spends more than two hours in compiler/backend work or trails
dense validation improvement per hour by more than about 10%, unless its fragment behavior is uniquely useful.

The positive Gated Recurrent Transformer result is extremely fresh and used roughly 9.8B training tokens on
a GPT-2-style stack. The recurrence-equivalence study is the stronger warning: parameter reuse generally
does not produce free dense-model capacity at equal training compute.

## Stage 9 — GLaDOS as a separate integration study

The local `clairnets` repo already supplies a canonical, staged α → verifier-gated organ → γ system, causal
controls, and grafts across seven host families including one Mamba-2 hybrid. It has not demonstrated a
Falcon-H1 graft or semantic soundness over arbitrary PDF arguments.

Proceed only after the H1 base is stable:

1. Add an H1 decoder-layer resolver and prove bitwise no-op at zero gate.
2. Run the existing exact-task smoke and causal-control table.
3. Test whether α can compile structure from actual source language without privileged graph metadata.
4. Only then design a source-grounded argument organ whose nodes retain exact PDF-span provenance.

The verifier can certify graph operations and formal deductions relative to a compiled structure. It cannot
certify that α extracted the right philosophical claim from prose. That structure-compilation boundary must
remain explicit.

## Later-week branch — visual grounding

Vision is feasible at this scale, but it belongs to a later Kaggle week. SmolVLM-256M is the decisive
existence proof: its published design combines a small language model with a 93M-parameter SigLIP encoder,
runs in under 1 GB inference memory, and has ONNX/WebGPU and MLX paths. A 90M H1 plus a similarly sized
frozen vision encoder and a small connector would remain comfortably inside the project's weight envelope.

The first comparison should include the off-the-shelf SmolVLM-256M Base as a baseline. Do not spend a week
recreating a weaker connector before learning what that model already provides.

For an H1-specific pilot:

1. Freeze a small pretrained vision encoder and the domain H1 checkpoint.
2. Compress each image to a fixed, small visual-token budget (initially 64–256) through a learned
   resampler/projector.
3. Train only the connector first; optionally unfreeze the top H1 blocks after alignment stabilizes.
4. Use paired images and short, source-grounded text. Separate PDF text/OCR pages from actual diagrams,
   artworks, layouts, and photographs—the former tests reading, not visual concept grounding.
5. Compare three token- and wall-clock-matched arms: text only, image plus text, and unrelated-image control.
6. Evaluate both multimodal tasks and text-only held-out concept/relationship transfer. If only captioning or
   OCR improves, the hypothesis that vision improved general concept acquisition has not passed.

The evidence for language-side benefit is mixed. Some visual-grounding work improves text-only language and
commonsense tasks; other controlled lexical-grounding work finds no significant advantage over text-only
pretraining. So this is a good experiment, not a settled principle.

Begin with a tiny connector-only pilot and kill it if held-out text-only concept transfer is indistinguishable
from the caption-only arm. If it passes, a later week can test joint adaptation and whether visual directions
share or reshape the style/affect manifolds found in the text model.

## Generation two

Only after a strong domain teacher exists:

- distill 0.5B to 90M or a smaller corpus-native model;
- investigate a smaller tokenizer or cross-tokenizer distillation;
- consider intrinsic weight sparsity or a recurrent student;
- quantize and profile in the actual browser.

Offline top-K distillation removes online teacher cost but moves it to storage. The cited implementation uses
top-100 targets. At a minimal 4-byte index plus 2-byte value per entry, 374.4M tokens would require about
224.6 GB before shard metadata, retained-mass values, checksums, or filesystem overhead. Smaller K,
quantized values, selective corpora, and empirical KD-quality curves are prerequisites here.

## Priority queue

1. Finish corpus-v1 evaluation artifacts while the existing jobs run.
2. Prove 0.5B JAX checkpoint parity and memory feasibility.
3. Run the matched 90M/0.5B TPU pilot and commit the remaining allocation to the winner.
4. Preserve flat-candidate and cooled checkpoints and build the developmental analysis dataset.
5. Quantize, browser-profile, and blind-rate the clean CPT result.
6. Run one aesthetic DPO branch and the first causal style-vector study.
7. Choose exactly one of MIR/late-SAM/blockwise-LR for a bounded A/B based on the observed failure mode.
8. Defer recurrence, internal-state monitoring, visual grounding, GLaDOS, and distillation until the mainline
   result exists.
