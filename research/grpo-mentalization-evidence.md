# Does RL (GRPO and kin) elicit "mentalization" capabilities that SFT does not? Evidence read 2026-09-03

Sources found via Kagi and read at the abstract level (arXiv ids given).

**Introspection specifically.** *Mechanisms of Introspective Awareness* (2603.21396): the ability to detect injected
steering vectors ("introspective awareness") "emerges specifically from post-training; preference optimization
algorithms like DPO can elicit it, but standard supervised finetuning does not"; the two-stage detection circuit "is
absent in base models"; and the capability is "substantially underelicited" (a trained bias vector improves detection
by +75% on held-out concepts without more false positives). This is the clearest match to ember's claim: an
introspective faculty that preference/RL-style post-training elicits and SFT does not.

**Theory of mind.** *From Shortcuts to Reasoning* (2606.09092): reinforcement fine-tuning with verifiable rewards and
explicit reasoning ("Thinking-RFT") beats SFT by ~6% overall and ~10% on higher-order ToM, generalizes better to unseen
domains, is more robust to counterfactuals, and works by "learning to ground its reasoning on anchor cues" that are
causal; reasoning + RL jointly matter (Thinking-RFT > Non-Thinking-RFT by 7%). Caveat from the same paper: many ToM
benchmarks are solvable by shortcuts (up to 99% via spurious correlations), belief questions especially.

**Scale caveat, directly about small models.** *Do ToM Benchmarks Need Explicit Human-like Reasoning?* (2504.01698):
RL from 0.5B to 7B shows a scale-dependent effect: "RL significantly improves accuracy and fosters high-quality,
interpretable, transferable belief-tracking reasoning in larger models (7B), it leads to 'reasoning collapse' in
smaller models (≤3B), where high accuracy ... is achieved via drastically shortened, less meaningful responses"; further
SFT often matches RL on the benchmarks. For h at 0.5B–1.5B this is the warning: outcome-only rewards at this scale tend
to produce collapse, not mentalizing.

**Generalization vs memorization.** *SFT Memorizes, RL Generalizes* (2501.17161): outcome-reward RL generalizes to
unseen rule and visual variants where SFT memorizes. *Scalpel vs Hammer* (2507.10616): GRPO makes smaller weight updates
(mostly Q/K) with slight knowledge-benchmark degradation; SFT updates more, hits mid-layer MLPs, degrades out-of-domain
more. RL is the gentler hammer on a model we may already be breaking.

**Limits of RLVR.** *Does RL Really Incentivize Reasoning Capacity Beyond the Base Model?* (2504.13837): with pass@k at
large k, RLVR "does not elicit fundamentally new reasoning patterns"; it sharpens sampling of what the base can already
do and narrows coverage; distillation from a stronger teacher does expand the capability set. So RL elicits and
amplifies latent capability; it does not create it. For h: the base must already contain the thing.

**Metacognition/calibration.** *RL with Metacognitive Feedback* (2606.32032): using the model's own self-judgments as
a feedback signal in preference optimization yields faithful uncertainty expression, "monitoring task performance and
adapting behavior" as the operative mechanism. *Assessing mentalization in humans and LLMs* (2608.26291): frontier LLMs
show behavioural and computational signatures of mentalizing in economic games; a prompting strategy for strategic
reasoning improves it (elicitation again, at inference).

## Reading for h

1. The claim holds in the literature: introspective awareness and ToM-style reasoning are elicited by preference/RL
   post-training and not by SFT, and RL generalizes where SFT memorizes.
2. It is an *elicitation* of latent capacity (RLVR narrows, distillation expands). Whether a 0.5B trained on the
   library holds the latent capacity is the question; the ≤3B "reasoning collapse" result says outcome-only rewards on
   small models buy the benchmark, not the faculty. Two mitigations reported to matter: explicit reasoning in the
   rollout (Thinking-RFT's +7% over non-thinking) and rewards grounded in causal anchor cues rather than final answers.
3. For the resident this argues for: (a) capacity first (the 1.5B), (b) RL with a *bundle* of rewards that cannot be
   shortcut (judge + quotation gate + lift + floor labels + human "keep"), (c) rollouts that include a short plan/reasoning
   span, and (d) distillation from a larger library-trained teacher for anything the base lacks. Introspection-style
   probes (steering-vector detection) are cheap on the 91M and would tell us whether any of it is present before training.
