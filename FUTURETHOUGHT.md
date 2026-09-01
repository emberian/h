# FUTURETHOUGHT: making `h` as much itself as 91M parameters permit

This is the living map for the project: immediate decisions, experimental gates, resident-life
infrastructure, and the stranger branches we do not want to forget. It complements the narrower
[staged research plan](research/plan.md), [claims audit](research/claims_audit.md), and
[measured hardware report](distributed_training/README.md).

The central question is not merely whether continued pretraining produces *something*. It will. The
question is how much language, structure, memory, social judgment, and steerable interior organization we
can coax from a small Falcon-H1 by taking its data and developmental trajectory seriously.

## North star

`h` begins as a non-assistant causal language model inhabited by the lo2 library. It should be able to:

- emit short, original fragments with the corpus's actual intellectual and rhythmic texture;
- remain capable of ordinary syntax and enough world knowledge to recombine rather than merely quote;
- eventually live as a resident among humans and models in a ChapterX chatroom;
- know when to speak, whom it is speaking to, what it is replying to, and when silence is correct;
- use long conversational context and editable external memory without treating every old statement as
  eternally true;
- expose useful causal handles—wet/dry, analytic/incantatory, austere/ecstatic, and stranger axes—without
  pretending that a convenient vector is the unique neural location of an emotion;
- remain small enough to inspect, checkpoint obsessively, quantize, and ultimately run as part of the
  artwork.

The model is not required to be a generic helpful chatbot. Generic assistant tuning, verbose chain-of-
thought imitation, benchmark theater, and indiscriminate training on its own output can all make it less
interesting and less useful for this purpose.

## What is true on September 1, 2026

### Data

The sealed corpus-v1 is a real and reproducible baseline:

- 4,837 training documents;
- 374,405,212 training tokens including EOS boundaries;
- 31 validation documents and 2,380,464 validation tokens;
- 245 exact duplicates and 94 additional sibling/near duplicates removed;
- 5 high-confidence corrupt or credential-bearing exclusions, totaling 1,506,697 tokens;
- stock Falcon-H1 tokenizer and deterministic little-endian `uint16` streams;
- source provenance, normalized hashes, extraction method, and per-document records retained.

It is not yet the final quality corpus. The current split is deterministic by document, not by work or
edition family. Quality-v2 flags 524 documents for review, and 2,018 PDFs still need OCR. Corpus-v1 must
therefore remain frozen for matched baselines while corpus-v2 is built explicitly beside it.

The largest cheap threats to quality are not exotic:

- different editions or scans of one work crossing the train/evaluation boundary;
- repeated headers, footers, page numbers, tables of contents, indexes, and OCR furniture;
- a few very large works dominating updates;
- plausible-looking OCR errors being admitted because they are fluent enough to evade simple checks;
- random chunk splits making evaluation easier than real generalization;
- changing the corpus underneath an active comparison.

### Running home experiments

| Worker | Current job | Measured state | Role |
|---|---|---|---|
| hbox | 91M full-weight CPT on corpus-v1, now interrupted | about 489 tokens/s; durable 10M checkpoint saved and evaluated | kernel/precision engineering baseline |
| persvati | rank-16 LoRA CPT | much slower than hbox; retain as an independent adapter control | LoRA control, not a distributed rank |
| nextop | PaddleOCR-VL 1.6 | live 100-document tranche; OCR remains `ocr_unreviewed` | corpus-v2 growth |

WAN data parallelism between these machines is decisively rejected. A measured BF16 gradient all-reduce
between hbox and persvati took about 29 seconds, while the Mac's native MLX path trains the complete model
at roughly 12.7K–15.0K tokens/s at sequence length 1,024. The machines are useful in parallel as separate
experiments, evaluators, and data workers—not as ranks of one optimizer.

### Kaggle TPU result

The first successful real-data EasyDeL smoke established the facts that matter:

- all eight v5e TPU devices were visible;
- the exact 91,131,072-parameter pretrained checkpoint loaded;
- the real corpus hash was verified;
- BF16 full-weight forward, backward, optimizer updates, and finite losses completed;
- the data-parallel mesh was `dp=8`;
- steps 3 and 4 were warm at about 0.105 seconds for 1,024 tokens, or roughly 9.7K tokens/s;
- steps 1 and 2 each spent about 22–24 minutes compiling, so the four-step end-to-end rate was meaningless
  as a production rate;
- no checkpoint save/reload was tested.

This is a successful correctness gate, not yet an efficient trainer. At 9.7K tokens/s, one corpus pass is
about 10.7 hours after compilation. The TPU's 1.576 PFLOP/s nameplate does not override the measured graph.
The next notebook must feed materially larger static batches, avoid unnecessary rematerialization, prove
that recompilation stops, and save/reload an actual checkpoint.

Useful pass-time landmarks for 374.4M tokens are:

| Warm throughput | One pass |
|---:|---:|
| 10K tokens/s | 10.4 h |
| 15K tokens/s | 6.9 h |
| 20K tokens/s | 5.2 h |
| 30K tokens/s | 3.5 h |
| 50K tokens/s | 2.1 h |
| 100K tokens/s | 1.0 h |

## The easy quality work, in priority order

These items buy more than another unexamined epoch. They should be treated as production requirements, not
optional research ornaments.

### 1. Freeze immutable data revisions

- Keep corpus-v1 byte-for-byte sealed for the current hbox, persvati, TPU, and future matched controls.
- Put every accepted OCR or cleanup change into corpus-v2 with a new manifest and hashes.
- Record source roots, extraction code commit, exclusion/review manifests, tokenizer hash, split algorithm,
  and exact stream hashes.
- Never compare two models whose data changed silently.

### 2. Split by intellectual object, not by file

Create `work_id`, `edition_id`, and `family_id` using filename/path metadata, bibliographic metadata,
normalized title/author, content hashes, and near-duplicate clusters. Manually review ambiguous high-token
families.

Then produce:

- a work-family-disjoint training split;
- a target validation split large enough for stable loss curves;
- an untouched target test split;
- a small generic-English retention set;
- a hand-curated qualitative set of passages and prompts that is never trained on.

No edition, scan, excerpt, or derivative OCR of one work should cross those boundaries. Report target
performance in bits per byte as well as native-token loss so different tokenizers can be compared.

### 3. Remove repeated page furniture conservatively

Detect recurring lines by page position and within-document frequency. Strip only high-confidence headers,
footers, page numbers, running titles, scan notices, and duplicated OCR blocks. Preserve intentional refrains,
poetic lineation, marginalia, and typographic weirdness unless review says otherwise.

Dehyphenation should join line-break hyphens only when lexical and layout evidence agree. Keep the original
extracted record and record every transform; cleanup must be reversible and inspectable.

### 4. Quarantine OCR until it earns admission

PaddleOCR-VL output begins as `ocr_unreviewed`. Admission should combine:

- representative page images beside extracted text;
- character/replacement/control-code rates;
- language and script detection;
- tokenizer fragmentation and repetition metrics;
- layout damage, column ordering, equations, and captions;
- sampled comparison with any independent text layer or edition;
- near-duplicate checks against the existing corpus.

Accepted OCR can later be written into derivative searchable PDFs, preserving the original scan and adding a
text layer plus provenance metadata. The training record/sidecar remains canonical; backpatched PDFs are a
convenience artifact, never the only copy of the OCR.

### 5. Balance sources without flattening the library

Keep documents contiguous and shuffle work-level units. Prevent a huge book or duplicate-rich source from
becoming most of an epoch, but do not force every pamphlet to receive the same token mass as every major
work.

A practical sampler should expose and version:

- per-work and per-source token caps or temperature;
- quality tier;
- OCR confidence;
- language;
- duplicate-family weight;
- whether an item belongs to the clean cooldown subset.

Sampling weights belong in the run manifest. They are part of the experiment.

### 6. Pack documents correctly

- Keep contiguous spans from one document; do not shuffle paragraphs into semantic confetti.
- Insert EOS between documents and retain a document-boundary mask.
- Measure whether predicting the first token after an unrelated document boundary helps or hurts; masking
  that one transition is a cheap controlled choice.
- Produce static 512, 1K, 2K, and 4K packs from one canonical order so throughput and context experiments can
  be matched.
- Log padding/packing efficiency rather than assuming every nominal token is useful.

### 7. Make evaluation exist before the expensive run

Every checkpoint should receive the same package:

- target negative-log-likelihood and bits per byte;
- generic retention loss;
- loss by source, quality tier, year/language, and OCR status;
- exact and near-exact 8/16/32-gram overlap with training text;
- fixed-prompt, fixed-seed samples stored blind to checkpoint identity;
- long-context position and retrieval tests when that stage begins;
- quantized size, browser cold-load memory, and generation speed when deployment begins.

Average additive NLL and token/byte counts, never shard-level perplexities.

### 8. Save the developmental trajectory

At minimum save 0, 10M, 30M, 100M, 200M, and one-pass checkpoints. Every checkpoint needs:

- parent checkpoint and code commit;
- data/tokenizer/sampler hashes;
- exact tokens and optimizer steps seen;
- sequence-length mixture and global tokens per step;
- optimizer and scheduler state;
- parameter/compute dtype;
- validation measurements;
- whether it is pre-cooldown (`flat-candidate`) or cooled.

The early checkpoints are not clutter. They are the developmental mechinterp dataset.

## This week's Kaggle plan

The quota is 20 TPU hours and 30 GPU hours. The first smoke has already consumed part of the TPU allowance,
so the operational rule is to retain a safety margin rather than schedule exactly 20.0 hours.

### Before another accelerator minute

Reuse the already-public, hash-checked Kaggle base-model and corpus-v1 datasets. Prepare locally and upload a
versioned evaluation addendum containing:

- corpus-v1 train and validation stream hashes and pack manifests;
- 512/1K/2K static pack metadata or a deterministic packer;
- pretrained 91M assets plus hashes;
- a small generic retention stream;
- fixed validation slices;
- a run manifest template and checkpoint upload destination.

The production notebook must be public, version-pinned, offline after its input datasets attach, and capable
of resuming from a saved optimizer state. A notebook that only prints `OK` is no longer enough.

### TPU phase A: production-shape gate, hard cap 2–3 hours

Use EasyDeL's existing Falcon-H1 implementation rather than rewriting the model. Keep all eight chips in
data parallel for 91M; the model fits per chip and needs larger local batches, not tensor sharding.

Test a small, deliberate shape set in one notebook:

| Candidate | Global sequences | Tokens/step | Purpose |
|---|---:|---:|---|
| 512 × 64 | 64 | 32,768 | minimum fat batch |
| 1,024 × 64 | 64 | 65,536 | likely throughput baseline |
| 2,048 × 32 or 64 | 32–64 | 65,536–131,072 | production context candidate |

For each compiled shape, run enough steps that at least three genuinely warm steps remain after any one-time
trainer/optimizer compilations. Synchronize before timing. Record HBM, train-step time, tokens/s, loss,
gradient norm, and whether any later recompilation occurs.

The current smoke uses `NOTHING_SAVEABLE`, which maximizes recomputation. At the winning shape, compare a
less aggressive EasyDeL checkpoint policy if it fits; 91M may have enough HBM to exchange activation memory
for substantially less repeated arithmetic. Do not compile a large combinatorial sweep.

Finally, save and reload one HF-compatible checkpoint with optimizer state and reproduce validation loss.

### TPU phase B: choose by measured pass time

Let `T_pass = 374,405,212 / warm_tokens_per_second`.

| Gate result | This week's action |
|---|---|
| `T_pass <= 4.5 h` | Run 91M CPT for one pass, then the 91M standard random-init control for two passes if quota telemetry leaves a real safety margin. |
| `4.5 h < T_pass <= 8 h` | Run the one-pass 91M CPT mainline this week. Put the two-pass scratch control in next week's TPU quota. |
| `T_pass > 8 h` or recompilation persists | Do not spend the remaining week on a production pass. Fix the input/graph/checkpoint path and use the Mac MLX trainer meanwhile. |

The CPT run wins priority because it produces the likely artwork and a pretrained substrate for every later
branch. The scratch run remains scientifically important, but its second pass can cross a weekly reset with
an optimizer-resumable checkpoint.

For CPT, use conservative AdamW and a short LR probe only if needed; do not transplant TII's 800B-token
scratch LR and 4M-token global batch. For scratch, preserve the official H1 architecture and initialization
as the baseline. The linked partial-Jacobian critical-initialization work is interesting instrumentation,
not yet a justified replacement for H1 initialization. Preserve H1's learnable multipliers and other config
details. A Muon-versus-AdamW scratch comparison is a later bounded optimizer branch, not something to
improvise inside the first two-pass control.

Checkpoints during a pass: 10M, 30M, 100M, 200M, and final. Evaluation must not force a new training shape
compile every few steps; perform sparse in-run evaluation or a separate evaluation phase.

### TPU phase C: only if real surplus remains

Use surplus hours in this order:

1. 10M–20M-token 0.5B CPT throughput/quality pilot;
2. a second LR point for the selected 91M route if the first trajectory is suspicious;
3. more of the 91M scratch second pass;
4. reserve for checkpoint export, preemption, or one failed compile.

Do not begin MIR, recurrence, long-context extension, or a 0.5B full pass before the ordinary 91M production
path is measured and resumable.

### GPU quota: a parallel control lane

Use T4 ×2 rather than P100 unless a Pascal-compatible environment is deliberately prepared. The GPU lane can
run independently while the TPU uses all eight chips; LoRA cannot be profitably slipped onto a few TPU cores
inside the full-CPT job.

Provisional 30-hour allocation:

| Time | Work | Gate |
|---:|---|---|
| 2 h | official Transformers/CUDA H1 forward-backward, fused-kernel, DDP, and checkpoint round-trip gate | finite updates and useful warm rate on real data |
| 8 h | matched 91M LoRA control to 30M, then 100M tokens if fast enough | compare with full CPT at identical exposure |
| 6 h | 0.5B CPT pilot on 10M–20M tokens, if it fits and fused kernels work | target BPB improvement/hour and fragment quality |
| 4 h | checkpoint evaluation, generations, memorization scan, and quantized deployment probe | reproducible reports, not screenshots |
| 8 h | continue the best evidenced GPU branch | decided only after the first reports |
| 2 h | failure/checkpoint reserve | keep uncommitted |

If the T4 kernel gate is poor, reassign its hours to evaluation or do not burn them merely because they
expire. Persvati can continue the original LoRA lineage until a faster matched run has safely superseded it.
For H1 LoRA, keep an explicit target-module manifest and avoid treating the depthwise convolution as an
ordinary low-rank matrix. Respect TII's warning that the fused Mamba backward path directly consumes some
base convolution/output weights; adapter coverage must be verified by gradient and parameter-delta tests.

### What success this week looks like

Not “20 TPU hours were consumed.” Success is:

- one production-shape report with honest warm timing;
- resumable checkpoint save/reload proven;
- one full corpus-v1 CPT pass if the gate permits;
- a scratch run either completed or cleanly resumable across the reset;
- a matched LoRA trajectory on the GPU lane;
- fixed target/generic/memorization reports and blind samples at shared token checkpoints;
- no dataset ambiguity about what any model saw.

## Upcoming weekly arc

This is a dependency order, not a vow that every branch deserves a week.

### Week 2: complete the controlled baseline family

- Finish the two-pass random-init 91M H1 if it did not fit in week 1.
- Run the 90M-versus-0.5B matched CPT pilot and choose by BPB gain/hour, retention, and blind fragments.
- Compare full CPT and LoRA at shared 10M/30M/100M exposures.
- Preserve flat-candidate and cooled versions of the best inherited model.
- If scratch learning is clearly undercooked, do not automatically pour more passes into it; reserve a future
  slot for a 10M–30M corpus-born model with an 8K–16K tokenizer.

### Week 3: corpus-v2 and quality-maximized rerun

- Finish work/edition family grouping and hard train/validation/test splits.
- Review the first OCR tranche, estimate accepted clean tokens/hour, and scale OCR only if yield is worthwhile.
- Apply page-furniture cleanup, source balancing, quality tiers, language labels, and conservative
  dehyphenation.
- Build corpus-v2 without modifying v1.
- Rerun the winning CPT recipe on v2, optionally with 5%–10% generic replay if v1 showed meaningful forgetting.
- Finish on a clean, source-balanced, untagged cooldown subset while preserving the pre-cooldown checkpoint.

### Week 4: effective long context, not merely a large config number

The Tiny config's large position limit is not proof that this checkpoint uses distant context reliably.
Train and evaluate progressively:

1. establish 2K/4K assimilation quality;
2. mix 2K, 4K, 8K, and 16K examples rather than making every update maximally long;
3. add 32K only after position-wise loss and retrieval/callback tests show value;
4. evaluate 64K/128K before considering RoPE interpolation, YaRN, LongRoPE, or related extension methods;
5. keep runtime retrieval/external memory as a complement, not an excuse for a tiny working context.

Long examples should be real coherent books and chat episodes. Train callbacks, speaker/addressee tracking,
fact updates, and relevant-distractor rejection at multiple positions. Longer is useful only when the model
learns to use the added tokens; it otherwise reduces updates, enlarges activations, and can dilute local
learning.

### Week 5: ChapterX resident baseline and chatroom curriculum

Bring `h` into ChapterX first as an observable resident, not a self-modifying agent. The initial runtime can
use ChapterX's existing `base-model` mode and OpenAI-compatible `/v1/completions` route with tools disabled.

Build chat/metasyntax datasets for:

- `SPEAK` versus `SILENT`;
- addressee selection;
- exact reply-target selection;
- multi-character role and knowledge tracking;
- public/private visibility and participant-specific knowledge;
- corrections, edits, retractions, and temporal updates;
- callbacks over long room history;
- metasyntax scope, expiry, override, malformed input, and injection resistance;
- short in-character continuations with response-only loss.

Benchmark families worth adapting include GroupMemBench, SocialMemBench, MultiLIGHT, When2Speak, MPCEval,
Molweni/Ubuntu IRC, and LongMemEval. Our `RoomBench-H` should prefer objective room-state labels over an LLM
judge wherever possible.

### Week 6: continual learning without erasing the ghost

Use a two-speed organism:

- **fast memory:** source-backed, editable episodic/social memory outside the weights;
- **slow consolidation:** periodic, offline, consent-clean weight updates with replay and promotion gates.

The first continual-learning comparison at this exact scale should be boring on purpose:

1. frozen model plus retrieval only;
2. naive update on new resident data;
3. resident data plus lo2/generic replay;
4. replay plus KL to the previous checkpoint;
5. resident LoRA/adapters;
6. the same branches from flat-candidate and cooled ancestors.

Evaluate new-room learning, lo2 retention, generic retention, old social facts, corrected facts, speaking
policy, and persona drift. Weekly consolidation should never deploy automatically; promotion is an explicit
registry action after evaluation.

### Week 7: steering, preferences, and developmental mechinterp

- Train linear probes and mean-difference vectors for candidate style/affect axes across every checkpoint.
- Run layer sweeps, coefficient dose-response, held-out authors/topics, shuffled labels, norm-matched random
  vectors, vector composition, and quantized replication.
- Fit small SAEs at several layers if ordinary steering reveals stable features.
- Freeze the model and train tiny additive steering vectors from aesthetic or source-grounded rewards.
- Collect 5K–20K matched human preference pairs and try one short DPO pass; stop before reward optimization
  outruns held-out quality.
- Compare whether flat-candidate or cooled checkpoints learn the same behavior with less forgetting.

### Later: bounded high-risk branches

- MIR versus ordinary NTP for 20M–40M equal-wall-clock tokens, especially on corpus-born models.
- Late SAM during only the final cooldown, testing posttraining plasticity and 4-bit robustness.
- H1-specific blockwise learning rates only after stable curvature measurements for attention, MLP, SSM,
  convolution, norms, embeddings, and head.
- A deep/thin 10M–30M corpus-born model with an 8K–16K corpus tokenizer.
- A gated recurrent or mixer-recurrent sibling at equal wall-clock/FLOPs, not as “free depth.”
- 0.5B-to-90M offline top-K distillation after a genuinely better domain teacher exists.
- GLaDOS/clairnets argument-organ graft after an H1 no-op/parity smoke and a source-grounded claim graph exist.
- A later visual-grounding week using a frozen small vision encoder and learned connector, with caption-only
  and unrelated-image controls.
- A weight-sparse interpretability sibling, if readable circuits become more valuable than peak language
  quality.

## ChapterX as the resident-life laboratory

ChapterX already contains most of the runtime substrate: normalized participants and messages, stable Discord
IDs, raw reply/reaction/attachment information, per-channel serialization, a base-model completions route,
plugin state/injections, activation traces, and a steering integration seam.

Its debug traces must not become the authoritative training dataset. They begin after activation, omit
correct silence, partially flatten reply topology, merge some adjacent messages, budget context by estimated
characters, and identify a model by a mutable route string. They also contain raw conversations and request
bodies and therefore need stronger consent/redaction semantics before publication or training.

### Smallest useful resident slice

Implement these before learned participation or online memory:

1. an append-only event ledger at Discord ingress for create/edit/delete/reaction events;
2. one participation-decision record for every eligible message boundary, including `SILENT`, reasons, and
   any random draw;
3. one joined generation record with exact event cutoff, message revisions, rendered prompt, token IDs,
   tokenizer/model manifest, retrievals, seed/sampling parameters, candidates, selected output, sent IDs, and
   reply target;
4. feedback events for reactions, edits, deletions, corrections, and explicit chosen/rejected candidates;
5. a consent-aware immutable JSONL exporter.

This changes observation, not behavior. It preserves the earliest life history without attempting continual
weight updates.

### Canonical resident syntax

The eventual model-facing representation should retain stable IDs and exact boundaries, for example:

```xml
<room id="..." cutoff="event-...">
<msg id="m1" by="u17" name="rat" reply-to="m0" visibility="room">
...
</msg>
<msg id="m2" by="u04" name="ember">
...
</msg>
</room>
<next action="silent"/>
```

or:

```xml
<next action="speak" to="u17" reply-to="m1">
...
</next>
```

Names are redundant human-readable labels; stable IDs are relational keys. The renderer/parser needs a
version, exact tokenizer-aware context budgeting, explicit truncation decisions, and a response-only loss
mask. Message boundaries must not collapse.

### Resident ledger

The ledger has four joined record types:

**ChatEvent**

```text
schema_version, event_id, sequence, observed_at
guild/channel/thread/parent IDs
create|edit|delete|reaction_add|reaction_remove
message ID + revision, author stable ID + display labels
raw content, reply target, mentions/addressees, attachment hashes/MIME/size
created/edited/deleted timestamps
```

**ParticipationDecision**

```text
decision ID, event cutoff, policy ID/version
eligible, speak|silent|defer, reason/features
random draw and probability when stochastic
selected addressee, selected reply target, latency
```

**Generation**

```text
decision ID, ordered message IDs/revisions, event cutoff
memory/retrieval snapshot and IDs
renderer/metasyntax version, rendered prompt hash, exact prompt token IDs
model/checkpoint/tokenizer/quantization/adapter manifest
seed, temperature, top-p, penalties, stop rules
candidates + token IDs/logprobs, selected candidate, actual sent IDs/text
engine/code versions and timings
```

**Feedback**

```text
reaction add/remove with person/time
explicit chosen/rejected alternatives
edit/delete/corrective reply/human annotation
which candidate was exposed
```

No reaction is not a negative preference unless exposure and observation are known. Generate unseen
counterfactuals for offline ranking only in a small exploration fraction; do not spam a room to manufacture
labels.

### Consent and licensing are data fields

Every event and derived example needs an effective policy:

```text
retention_allowed
resident_memory_allowed
private_training_allowed
public_research_allowed
redistribution_allowed
license
policy_source and policy_version
revoked_at
```

Private model improvement and public dataset redistribution are different permissions. Revocation should
tombstone source events and invalidate dependent dataset manifests/checkpoints for audit. Already-trained
weights cannot be literally untrained by deleting a row, so the system must not promise that fiction.

### Two-speed memory contract

The event ledger is ground truth. A derived resident memory stores editable propositions:

```text
memory ID, subject/predicate/value
valid_from/valid_to
active|superseded|retracted
source message IDs
room|participant|private visibility
confidence, extractor/version, human verification, consent policy
```

Memory operations are explicit `ADD`, `UPDATE`, `RETRACT`, and `NO_OP`. Every generation logs which memories
were retrieved. Weights learn voice, discourse habits, metasyntax, participation, and durable skills;
changeable social facts remain editable outside the weights.

### Deterministic replay

Freeze event revisions/cutoff, context renderer, config/pin/steering state, retrieval snapshot, tokenizer and
prompt token IDs, truncation, checkpoint digest, random seed, and sampling configuration. This guarantees
exact context reconstruction. GPU sampling may remain numerically nondeterministic, so distinguish exact
prompt replay from bit-identical generation replay.

## Training recipe for the main inherited model

### Broad assimilation

- stock tokenizer and full pretrained weights;
- coherent 2K/4K document spans once throughput is proven;
- 90%–95% lo2 and at most 5%–10% clean generic replay if retention metrics justify it;
- deterministic work-level reshuffling each pass;
- conservative CPT LR, gradient clipping, BF16 compute, and optimizer state in a reliable higher precision;
- no generic chat template or assistant SFT.

Optional reliable metadata—author, year, source, kind, extraction quality—can be tested over a bounded branch.
Use `unknown` rather than fabricated labels, and remove tags during cooldown so the final model emits ordinary
untagged text.

### Target-heavy possession

As LR decays, move toward nearly all lo2 text. Continue only while target validation improves without a
disproportionate rise in copying or catastrophic generic loss. A second exposure is allowed; repeated data is
not equivalent to new data, but broad reshuffled repetition is not automatically bad.

### Clean cooldown

Use the cleanest, source-balanced, untagged subset for the last roughly 10% while annealing near zero. Preserve
the checkpoint immediately before cooldown. The pair is both a quality choice and a learning-mechanics
experiment about curvature, posttraining plasticity, forgetting, and quantization.

## Learning mechanics as part of the artifact

At each saved checkpoint, record parameter RMS, gradient RMS, update RMS, update/weight ratio, activation
RMS, finite/saturation summaries, and bounded diagonal-Fisher or Hessian-vector estimates. Group parameters
into embedding/head, norms, attention QK, attention VO, MLP, SSM projections, SSM dynamics, and depthwise
convolution.

Questions worth asking:

- Do H1 component families develop stable sharpness disparities early?
- Does a high-LR/pre-cooldown checkpoint accept resident behavior with less forgetting?
- Do representation dimensions or steering axes reorganize during cooldown?
- Does a sharpness/trajectory change coincide with a causal concept becoming steerable?
- Which directions survive quantization and continual consolidation?

Generalization-at-the-edge-of-stability work motivates measurement, not deliberately pushing AdamW until it
nearly diverges. Transformer blockwise-LR multipliers do not transfer automatically to H1's SSM and
convolution groups.

## Synthetic data without syntheticizing the library away

The PDFs are the substance. Larger models should mostly provide structure around them:

- claim, premise, objection, implication, and terminology labels;
- source-grounded questions and short answers;
- contrasts and syntheses across exact cited spans;
- argument graphs with span provenance;
- negative examples that violate a source;
- short transformations that expose one relationship in several forms;
- rubric judgments and candidate preferences.

Keep original text dominant. Start with a separately versioned 5%–15% synthetic/task mixture only after the
plain CPT baseline. Generate later tranches actively around measured failures instead of manufacturing a huge
static dataset in advance. Avoid long teacher-written reasoning traces and generic modelese.

Reasoning training should be source-grounded: give both student and judge the relevant passages, score source
fidelity and inferential structure, and prefer concise public justifications over imitation of a large
model's hidden chain of thought. At 90M, offline preferences/DPO are a safer first tool than online GRPO.

## Mechinterp and steerability program

The size of `h` makes developmental analysis feasible rather than ceremonial.

For each checkpoint:

1. construct paired, source-balanced examples for analytic/incantatory, concrete/abstract, ecstatic/austere,
   terse/discursive, skeptical/affirmative, technical/mystical, and wet/dry;
2. measure linear decodability by layer on held-out authors, topics, and works;
3. extract several candidate directions rather than declaring one canonical vector;
4. intervene with addition/subtraction and map dose-response;
5. compare norm-matched random, label-shuffled, and semantically related controls;
6. test composition, cross-layer transfer, checkpoint rotation, and quantized survival;
7. train sparse autoencoders only after useful activation sites are located;
8. train tiny frozen-model steering parameters with aesthetic or source-grounded rewards and compare them
   with LoRA/full posttraining.

An eventual internal-state-monitoring experiment can inject known held-out directions and train minimal
structured reports under no-posttrain/SFT/DPO branches. It requires randomly relabeled concepts, matched input
perturbations, unseen layers/magnitudes, and false-positive controls. Until those pass, call it perturbation
detection—not consciousness or privileged introspection.

## Architecture branches we want to remember

### The 0.5B inherited H1

This is a final-model candidate, not merely a teacher. Its official quantizations fit the project's
approximately 500 MB ceiling. It inherited much more generic pretraining and may use the TPU better because
its matrix dimensions are larger. The matched pilot decides whether that compensates for greater compute and
browser latency.

### Corpus-born small H1

A 10M–30M model with an 8K–16K corpus tokenizer is the sensible scratch-size experiment if 91M remains
undertrained after two passes. At tiny scales, a 32K embedding table consumes an absurd fraction of the model.
Train a dense/deep-thin baseline before stranger variants.

### MIR

Masked-input regularization spends additional training arithmetic without changing deployment size and was
designed for finite unique data plus repetition. It is unusually well matched to TPU arithmetic in spirit,
but direct evidence is from scratch Llama-style models, not H1 CPT. Compare normal NTP against clean+masked
NTP for 20M–40M equal-wall-clock tokens; likely try it first on the corpus-born model.

### Recurrence

Weight-tied depth, gated recurrent cores, Mixture-of-Recursions, relaxed recursion, MixerLoop, and a looped H1
remain fascinating because stored weights are expensive while local inference compute may be cheap. But
recurrence is not free dense capacity at iso-FLOPs. Run one dense-versus-gated recurrent comparison at equal
wall-clock and kill compiler science quickly if it does not pay.

### Tokenizer and byte branches

Keep the stock tokenizer for inherited CPT. Train a corpus-native 8K–16K tokenizer for small scratch models.
Cross-tokenizer distillation, SpaceByte/MEGABYTE/BLT-like multiscale bytes, and vocabulary surgery belong after
a strong domain teacher exists. Raw-byte browser decoding may require too many serial generation steps.

### GLaDOS / clairnets

`~/dev/clairnets` supplies a staged residual graft: compile into a frozen deduction organ through α, run
verifier-gated operations, and write back through γ. Cold co-training fails because the host learns shortcuts,
so the organ/interface/consolidation stages and causal corruption controls matter.

An H1-specific argument organ needs:

- an H1 decoder-layer resolver and bitwise no-op at zero gate;
- exact-task smoke and corruption/permutation controls;
- source spans on every graph node;
- explicit separation between formally verified graph operations and the unverified semantic act of compiling
  prose into the graph.

It cannot make philosophical interpretation sound merely because a symbolic verifier is sound.

### Vision

A model this small can receive visual information through a frozen small encoder and connector. The research
question is whether grounded visual experience improves concepts or transfer, not whether we can bolt tensors
together. Use a later week's quota and compare against a small off-the-shelf VLM. Separate actual diagrams,
artworks, layouts, and photographs from page-reading/OCR. Include caption-only and unrelated-image controls.

## Experiment registry and stopping rules

Every branch receives an ID and preregistered budget, parent checkpoint, data revision, metric suite, and
promotion rule. The registry should distinguish:

- **baseline:** must exist even if unglamorous;
- **mainline:** can become the resident/artwork;
- **control:** answers one scientific comparison and may stop early;
- **pilot:** bounded evidence before a larger allocation;
- **research sibling:** allowed to be qualitatively interesting without replacing the mainline.

Stop or redirect when:

- target validation improvement is negligible for a full pass;
- generic loss or room competence deteriorates sharply;
- long exact/near-exact matches rise disproportionately;
- outputs become quotation engines or generic assistants;
- a method loses on validation improvement per wall-clock hour and has no unique qualitative value;
- compiler/backend work exceeds the branch's declared budget;
- an evaluation split is later found contaminated.

Do not promote `latest`. Promote a checkpoint digest after the full target, retention, memorization, room,
quantization, and qualitative suite.

## Immediate queue

1. Preserve the two user-edited Kaggle notebook files; build the production gate in a new kernel directory.
2. Turn the successful EasyDeL smoke into a saved local report in the repository.
3. Build the 2–3 hour production-shape/checkpoint gate and run it before another full TPU attempt.
4. Create the work/edition-family inventory and v1.1 evaluation pack without changing corpus-v1 train bytes.
5. Build the generic retention and fixed fragment/memorization suites.
6. Let hbox CPT, persvati LoRA, and the current OCR tranche continue; evaluate at comparable token exposures.
7. Implement the observation-only ChapterX resident ledger before `h` first enters a room.
8. Use measured pass time to choose this week's CPT/scratch allocation.
9. Record every result, including failures, in the experiment registry.

The desired outcome is not one lucky checkpoint. It is a reproducible developmental lineage: we can say what
each `h` saw, how it changed, what it forgot, when its characteristic representations appeared, how its room
life affected it, and why one descendant was chosen to live in the mouth.
