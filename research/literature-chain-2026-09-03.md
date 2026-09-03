# Literature sweep → method chains for h (2026-09-03)

Method: 29 Kagi queries across seven themes, ~75 abstracts read on arxiv.org (plus TII's Falcon-H1 finetuning doc).
Excluded as already covered: `research/grpo-mentalization-evidence.md` (RL vs SFT for introspection/ToM, RLVR limits,
reasoning collapse ≤3B: 2504.01698, 2501.17161, 2507.10616, 2504.13837) and `qwen/RECIPE.md` (Unsloth CPT recipe).
Our measured situation is in `research/results/night-2026-09-02.md` (breakage audit, WiSE-FT table, span-weighting arms).
Costs below use the ledger: one 0.5B epoch of the 417M-token room mix = 66–73 TPU min at 131K tok/s; TPU quota is
21.06/20 h until Friday 00:00; 30 T4 h/week; the Mac (103 GB, MLX) and the 12 GB AMD box are free.

## 1. Continued pretraining without forgetting

| work | finding | numbers |
|---|---|---|
| 2403.08763 Ibrahim+ *Simple and Scalable CPT* | LR re-warm + re-decay + replay matches retraining from scratch; re-warming itself causes forgetting; higher peak LR = more adaptation and more forgetting; "infinite" (constant-then-anneal) schedules avoid re-warm forgetting | 405M and 10B; 5% replay for weak shift (Pile→SlimPajama), 25% for strong (→German) |
| 2508.01908 *Revisiting Replay and Gradient Alignment* | replay and gradient alignment both stabilise CPT; meta-experience replay at negligible overhead | Llama family, 100B tokens/language; 25% replay is a better use of compute than a bigger model; 50% is not |
| 2502.06042 *Scaling Laws for Forgetting with Pretraining Data Injection* | small target sets overfit and drift; injecting pretraining data fixes both | as little as **1%** pretraining data in the mix prevents forgetting of the pretraining set |
| 2603.04964 *Replaying pre-training data improves fine-tuning* | replay improves the *target* domain too, most when target data is rare in pretraining | 150M models, 4M target tokens: 1.87× target-data efficiency (FT), 2.06× (mid-training); 8B: +4.5% web-nav, +2% Basque QA |
| 2406.14833 *Mitigating the Stability Gap* | CPT dips then recovers; multiple epochs on a right-sized high-quality subset beat one pass over everything; mix in pretraining-like data | OpenLlama-3B medical 36.2→40.7% at 40% budget, no general-task forgetting |
| 2605.26097 *Forgetting: Capacity, Optimization, Self-Generated Replay* | the model's own samples are effective replay (near-zero forgetting); low LR alone reduces forgetting but needs many more steps; replay removes the trade-off; forgetting persists when capacity is saturated | — |
| 2605.20005 FINCH; 2502.02797 *Upweighting Easy Samples* | per-step forgetting ∝ LR·√loss → lower LR on high-loss batches; or weight samples by the *base* model's loss (low-loss up) | FINCH −93% forgetting at matched task perf (Qwen3-4B); Gemma-2-2B: 0.8% GSM8K drop, +5.4% pretraining acc preserved |
| 2305.16264 *Scaling Data-Constrained LMs*; 2202.00470 OCR noise; 2606.02991 TypewriterLM | ≤4 epochs of repeated data ≈ unique data, then value decays; LMs diverge from noiseless targets as OCR quality drops (small corpora: simpler models win); a 7.24B model on 54B tokens of pre-1913 text needed extensive cleaning | 4 epochs |

## 2. Merging / interpolation

| work | finding | numbers |
|---|---|---|
| 2109.01903 WiSE-FT | weight-space ensemble of base and fine-tune improves robustness at no cost | +4–6 pp under shift, +1.6 pp in-distribution (CLIP) |
| 2504.10478 *Weight Ensembling Improves Reasoning* | SFT raises pass@1 but collapses pass@k; interpolating the last checkpoint with an early one (ratio 0.5) "almost completely recovers pass@k while improving pass@1", and the blend RL-tunes better with less data; complementary to temperature | ratio 0.5 |
| 2412.19512 pre/post-tuning merging; 2410.17146 LiNeS | merging base with fine-tune restores lost (safety) behaviour without data; LiNeS scales updates linearly with depth so shallow layers stay near base — less forgetting, better merges | — |
| 2410.03617 *What Matters for Merging at Scale* | stronger base and larger models merge better; merging improves held-out generalisation; methods converge at scale | 1B–64B, up to 8 experts |
| 2511.21437 *In-the-Wild Merging* | with heterogeneous/conflicting experts only plain Task Arithmetic reliably beats the base; TIES/DARE/subspace methods usually do not | 4 bases × 12 checkpoints × 16 benchmarks |
| 2405.09673 *LoRA Learns Less and Forgets Less*; 2406.16768 WARP | LoRA underfits the target (CPT 20B tokens) but preserves out-of-domain skills and generation diversity; full FT updates have 10–100× the rank; WARP = EMA anchor in the KL, SLERP of policies, then LERP toward init to recover pretraining features, iterated | — |

## 3. Reward-free voice shaping

| work | finding | numbers |
|---|---|---|
| 2306.13649 GKD | distil on the student's *own* samples with teacher feedback; use JSD/reverse-KL when the student cannot match the teacher | — |
| 2412.14964 prompt distillation; 2402.13669 SDFT | a model conditioned on a document teaches its unconditioned self (no larger teacher); self-distilled data matches the model's own distribution and so avoids forgetting | beats SFT, can beat RAG for knowledge injection |
| 2604.01193 SSD | sample with a chosen temperature/truncation, SFT on the samples, no verifier or teacher; sharpens where precision matters, keeps diversity elsewhere | Qwen3-30B LiveCodeBench 42.4→55.3% pass@1; holds at 4B/8B |
| 2601.18734 OPSD; 2608.06296 U-OPSD; 2607.05184 | same model as privileged-context teacher and bare-context student, per-token divergence over student rollouts; U-OPSD builds the privileged context from a majority vote (no labels); caveat: privileged self-distillation hurts *thinking* models on long traces | U-OPSD +8.5/+10.7% (Qwen3 4B/8B non-thinking); up to −17% avg@16 for thinking models |
| 2507.14805 subliminal learning | traits transfer through unrelated data **only when teacher and student share a base model** | — |
| 2507.21509 persona vectors; 2603.13249 style modulation heads | finetuning-induced persona shifts are linear directions; preventative steering during training; flag data that will shift persona; three attention heads carry style — steer them, not the residual stream, to avoid incoherence | — |
| 2504.02193 *More is Less*; 2410.06961 SynPO | DPO with chosen from a stronger model and rejected from self is linearly separable → shortcut learning; self-generated pairs for both sides are safer; iterated self-generated preferences still improve | SynPO: +22.1% win-rate (AlpacaEval 2), +3.2–5.0 Open LLM avg after 4 rounds |
| 2401.01335 SPIN; 2509.07414 Language Self-Play; 2603.12273 | self-play discriminating own vs. target-distribution text (needs demonstrations); data-free RL self-play works on a 3B instruct model; hindsight self-distillation from follow-up messages improves without regressions | — |

## 4. RL for small models

| work | finding | numbers |
|---|---|---|
| 2503.16219; 2503.18892 SimpleRL-Zoo; 2506.13404 | GRPO on 1.5B is cheap and fast but unstable with length; zero-RL works on Qwen2.5 0.5B–32B with format-reward and difficulty control; response length ≠ cognition; 0.5B needs SFT/KD+RL hybrids | 7k samples, $42: AMC23 63→80% |
| 2511.04902 *You Need Reasoning to Learn Reasoning* | label-free RL falls **below baseline** on weak/small bases (0.5B–7B); curriculum + masking no-majority rollouts rescues it | — |
| 2505.22617 entropy mechanism; 2509.07430 DPH-RL | performance is bought with entropy (R = −a·e^H + b); reverse-KL accelerates collapse, forward-KL/JS to the init acts as rehearsal and keeps pass@k | — |
| 2509.15194 EVOL-RL; 2605.29190 novelty bonus | majority anchor + novelty reward (distance from sibling rollouts / perplexity under frozen reference) prevents collapse label-free | Qwen3-4B-Base AIME25 pass@1 4.6→16.4, pass@16 18.5→37.9; +7pp pass@32 |
| 2604.06268 RAGEN-2 | "template collapse" is invisible to entropy; monitor mutual information across inputs; filter prompts by reward variance (SNR) | — |
| 2506.00103 Writing-Zero; 2507.00769 LitBench; 2508.18642 RLMR; 2605.08061 | pairwise generative RM with explicit writing principles + in-group bootstrapped reference (BRPO) resists hacking where scalar RMs fail; a trained BT/GenRM beats zero-shot judges; mixed subjective+constraint rewards with dynamic weights; rubric rewards from a frozen judge with grounding the policy cannot see transfer out of domain | LitBench: trained RM 78% vs best zero-shot 73% |
| 2512.02807 SR-GRPO | stable rank of hidden states as an intrinsic reward, no supervision | 84% RewardBench; Qwen2.5-1.5B +10% STEM, +19% math |
| 2507.05386 | RFT preserves prior tasks and general benchmarks where SFT forgets; not due to KL or CoT but selective updates | Qwen2.5-VL-7B |

## 5. Multi-party dialogue

| work | finding | numbers |
|---|---|---|
| 2603.11409 *Speak or Stay Silent* | 8 LLMs fail speak/silent zero-shot; SFT with reasoning traces fixes it; "not emergent, must be trained" | 120K labelled convs; +23 pp balanced acc |
| 2605.05626 When2Speak | SFT on SPEAK/SILENT labels gives big F1 gains but over-conservative models; RL with asymmetric reward fixes recall | 215K examples, 2–6 speakers; SFT +60% macro-F1; missed-intervention 0.50 → 0.19–0.22, recall 0.48 → 0.78–0.81 |
| 2606.13544 ModeratorLM; 2401.04883 MUCA; 2506.05309 *Time to Talk* | role-conditioned turn-taking; What/When/Who decomposition with a user simulator; separate generator and scheduler modules reach human-level timing in Mafia games | precision +40%, recall +70% |
| 2604.07798 LightMem; 2511.17208 | SLM-driven STM/MTM/LTM memory keyed by user id for multi-user; event-level propositions (EDUs) as a strong non-compressive memory baseline | — |

## 6. Data quality for CPT

| work | finding | numbers |
|---|---|---|
| 2402.09739 QuRating | pairwise LLM judgments → scalar rater; sample with quality as logits (keep diversity); educational value is the best criterion; also a curriculum | 1.3B: ≈ uniform sampling with 50% more steps |
| 2409.05816; 2503.00808 PreSelect | pick documents whose loss correlates with downstream benchmarks (no training needed); fastText scorer | 30B selected ≈ 300B vanilla at 1B/3B (10×) |
| 2512.12770 Curió-Edu | edu/STEM-filtered 10% of the CPT corpus beats the full corpus | LLaMA-2 7B, 10B vs 100B tokens, 20% compute |
| 2403.16952 Data Mixing Laws; 2507.09404 | fit loss-vs-mixture on small runs, extrapolate; predicts the critical replay proportion that avoids forgetting in continual training | 1B/100B ≈ 48% more steps on default mix |
| 2504.12491 | held-out perplexity is a misleading selector between same-size checkpoints | 50 1B variants; proxies cut error >50% |
| 2502.01205 OCR post-correction | open LLMs cut English CER, "no free lunches" for harder languages/segments | — |

## 7. Hybrid Mamba / Gated DeltaNet specifics

| work | finding | numbers |
|---|---|---|
| 2604.22127 *Where Should LoRA Go?* | on Falcon-H1-0.5B (parallel) and Qwen3.5-0.8B (sequential GDN): attention-only LoRA beats full-model adaptation with 5–10× fewer params; adapting the recurrent path is **destructive in sequential hybrids, constructive in parallel ones**; sequential hybrids show catastrophic forgetting, parallel show positive transfer | −14.8 pp GSM8K (Qwen3.5 recurrent) vs +8.6 pp (Falcon-H1 SSM) |
| 2604.01168 S0 tuning | tune one initial-state matrix per recurrent layer, weights frozen, zero inference overhead | Qwen3.5-4B +23.6 pp HumanEval; Falcon-H1-7B 71.8 vs LoRA 71.4; ~48 MB |
| tiiuae/Falcon-H1 `docs/finetuning.md` | exclude `conv1d` and `out_proj` from LoRA (the Mamba kernel bypasses LoRA forward; merges break, issue #13); never quantise `out_proj` in QLoRA | — |
| 2411.03855 MambaPEFT; 2405.09673 | PEFT works better on Mamba than transformers; per-module placement beats all-module; LoRA is LR/target-sensitive | — |
| 2507.22448 Falcon-H1; 2608.30320 Qwen3.8-Next | parallel attention+SSM; 1.5B-deep rivals 7–10B; Qwen3.8-Next swaps its full-attention layers for sparse attention *at CPT time* and notes loss and downstream do not always move together | — |

## Synthesis (a): what the literature says about our failure

**CPT.** Our −5.4 (0.5B, one epoch) and −5.7 (91M, four epochs) points are the textbook re-warm-and-no-replay result
(2403.08763): re-warming the LR to a fresh peak buys adaptation and forgetting together, and only replay breaks the
trade (2605.26097). The dose is small — 1% prevents pretraining-set forgetting (2502.06042), 5–25% matches retraining
(2403.08763), 25% is worth more than a bigger model (2508.01908) — and it helps the target too when the target is rare
in pretraining (2603.04964), which OCR'd books and room transcripts are. Our epochs are within the ≤4 rule (2305.16264),
and the stability-gap paper's "multiple epochs over a right-sized high-quality subset" (2406.14833) is exactly the
corpus-v2 admission manifest. OCR noise is a known perplexity tax (2202.00470); nobody reports CPT recipes specific to it.

**Merging.** The α=0.7–0.9 result is WiSE-FT behaving as published (2109.01903): the fine-tune overshoots, the blend
recovers held-out loss and restores generation diversity (2504.10478 — pass@k, the same axis as our echo/quotation
problem), and blends RL-tune better afterwards. Two refinements are free: depth-scaled updates (LiNeS, 2410.17146) so the
shallow layers stay near base, and WARP's habit of LERP-ing toward the init after every RL round (2406.16768). Do not
expect TIES/DARE to beat plain interpolation (2511.21437).

**Voice without instructions.** The literature's reward-free route is on-policy self-distillation: the same model,
conditioned on privileged context, teaches its bare-context self on its own rollouts (2412.14964, 2601.18734,
2608.06296), which also protects general skills because the data is the model's own distribution (2402.13669). Traits
transfer best when teacher and student share a base (2507.14805) — an argument for the Falcon-H1 line teaching itself,
or the 1.5B teaching the 0.5B, over a Qwen teacher. Style lives in a few heads/directions (2603.13249, 2507.21509), so
"steer the resident" is a two-hour experiment on the 91M before any training.

**RL.** For 0.5B–1.5B the warnings are consistent: label-free or outcome-only RL degrades weak bases (2511.04902,
2504.01698), collapse is bought with entropy (2505.22617) and hides from entropy metrics (2604.06268), and reverse-KL
makes it worse (2509.07430). The remedies are equally consistent: a majority/judge anchor plus a novelty term
(2509.15194, 2605.29190), forward-KL/JS to the init, SNR prompt filtering, and pairwise generative judging with an in-group
reference for non-verifiable tasks (2506.00103). RFT itself forgets less than SFT (2507.05386, 2507.10616).

**Multi-party.** Speak/silent is "not emergent, must be trained" (2603.11409); SFT on labels produces over-silent
models and RL with asymmetric reward fixes recall (2605.05626: missed interventions 0.50→0.19). Our reply-when-named
harness plus `room-decisions.jsonl` is the same setup; the scheduler can be a separate small head (2506.05309).

**Data.** Quality-filtered subsets beat the full corpus at a fraction of compute (2512.12770, 2402.09739), sampling
by quality-as-logits keeps diversity, mixing laws predict the anti-forgetting replay ratio from small runs (2403.16952),
and held-out perplexity is a poor checkpoint selector (2504.12491) — our retention proxy failed for the same reason.

**Hybrid.** Falcon-H1 is a *parallel* hybrid, where adapting the SSM path helps (+8.6 pp, 2604.22127) and attention-only
LoRA is the efficient default; the Qwen3.5/3.8 line is *sequential*, where touching the GDN path costs −14.8 pp and
forgets catastrophically. S0 tuning (2604.01168) is a 48 MB, zero-overhead "voice adapter" for hybrids we have not tried.

## Synthesis (b): three chains

**Chain A — retention-first CPT (this week; TPU refresh Friday).**
1. Audit e2-v5 (12.5% FineWeb-Edu replay, done) with the six-benchmark audit, not loss (2504.12491).
2. Second arm: 25% replay drawn from a pretraining-like mix (2403.08763, 2508.01908), peak LR halved with the same
   WSD, on the corpus-v2 admission manifest sampled with quality-as-logits (2402.09739, 2406.14833). Optional third arm:
   base-loss sample weights (2502.02797) — we already compute base losses per document.
3. WiSE-FT sweep α∈{0.7,0.8,0.9} against base for each arm, plus a LiNeS depth-scaled variant (2410.17146); pick by audit.
Expected: recover 2–4 of the 5.4 lost points at ≤0.01 nats of room loss (e2-v5 already costs 0.005 nats on both library
and room; its payoff has to show in the audit). Cost: 2 arms × 70 TPU min + blends/audit ≈ 3 GPU h. Risk: replay dilutes the voice; the trade is measurable.

**Chain B — on-policy self-distillation of the voice (reward-free; T4 + Mac + one short TPU run).**
1. Start from Chain A's best blend. Teacher = the *same* checkpoint with privileged context (the room so far + a
   retrieved library passage + h's real next line from the bank, or a 27B-adapter continuation when it exists); student =
   bare room context (2601.18734, 2412.14964). Sample 20–40k student rollouts on the bank (0.5B on a T4: ~2 h).
2. Filter: 91M library-likeness judge, and an echo gate (n-gram overlap with the visitor's line; copy-penalty
   rationale from 1911.03860). Train on teacher token distributions where available, else SFT on survivors (SSD,
   2604.01193) with JSD (2306.13649). One short epoch on TPU (~30 min) or LoRA on the Mac.
3. Re-blend toward the pre-distillation weights (2504.10478); two rounds; SynPO-style iteration if it holds (2410.06961).
Expected: echo 0.35 → <0.2, lift up, audit flat (self-distillation preserves, 2402.13669). Cost: ~6 T4 h + 1 TPU h per
round. Risk: reinforcing the model's own tics; monitor distinct-n and cross-input MI (2604.06268).

**Chain C — GRPO with a reward bundle that cannot be shortcut (after A/B; 1.5B preferred).**
1. Policy = Chain B output, LoRA on attention only (2604.22127), or S0 state tuning as a cheaper first try (2604.01168).
2. Rewards: pairwise generative judge with written principles and an in-group bootstrapped reference (Writing-Zero
   BRPO, 2506.00103) run by the 27B/Qwen-instruct on the Mac; gates for echo, quotation, floor labels; speak/silent with
   asymmetric reward (2605.05626); novelty = perplexity under the frozen init within the group (2605.29190, 2509.15194);
   later a Bradley–Terry RM on human "keep" pairs once ≥1k (2507.00769).
3. Optimiser: GRPO with forward-KL/JS to init (2509.07430), Clip-Cov entropy control (2505.22617), SNR prompt filtering
   (2604.06268); WARP-style LERP toward init after each round (2406.16768).
Expected: participation and voice under a judge, without the ≤3B collapse. Cost: 0.5B LoRA GRPO on a T4 ≈ 10–15 h per
500 steps at G=8; 1.5B needs the JAX kernel gate (unknown, ~3× 0.5B per token). Risk: judge hacking (length,
over-explanation, 2506.00103) and template collapse; the bundle and the MI monitor are the defence.

## Synthesis (c): three things not to do

1. **Full-parameter multi-epoch CPT at a re-warmed peak LR with no replay, selected by held-out loss.** The 91M's four
   epochs and the 0.5B's first two are this; 2403.08763 and 2605.26097 predict the forgetting we measured, and 2504.12491
   says the loss proxy we selected by cannot see it. Replay ≥1–5% and the six-number audit are the minimum from here.
2. **LoRA on the Gated DeltaNet projections of the Qwen3.8-27B adapter** (as `qwen/RECIPE.md` prescribes). In sequential
   GDN hybrids that is −14.8 pp and catastrophic forgetting (2604.22127); target attention (and MLP) only. On Falcon-H1
   the SSM path is fine to adapt, but exclude `conv1d`/`out_proj` (TII).
3. **Synthetic-preference DPO with "chosen" from the 27B and "rejected" from the resident, or label-free GRPO on the
   0.5B.** The former learns a linearly separable shortcut (2504.02193); the latter falls below baseline on weak bases
   (2511.04902, 2504.01698). Use same-model on-policy distillation (Chain B) and a bundled, anchored reward (Chain C).
