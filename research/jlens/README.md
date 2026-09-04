# J-lens (Jacobian lens) for the small Falcon-H1 models

Implementation of the Jacobian lens from *A global workspace in language models*
(Anthropic, 2026; Methods, "The Jacobian Lens", "The J-Space", "Technical details of
J-lens use cases"), for the h1jax Falcon-H1 checkpoints, on CPU, with the first
experiments on the 90M/91M pair and the 0.5B pair. Nothing here is committed; all
outputs live under `research/jlens/out/<model>/`.

## What was implemented

`research/jlens/jlens.py` (CLI with subcommands `check`, `lens`, `readout`, `inject`,
`sparse`; `research/jlens/report.py` renders the JSON outputs into the tables below).

Model glue reuses `h1jax.model.decoder_layer`, `_layer_params`, `_rms_norm`, `_linear`
exactly as `falcon_h1_forward` composes them (no layer is re-implemented):

- `hidden_at_layer(params, cfg, ids, l)` = `embed * embedding_multiplier` followed by
  decoder layers `0..l-1`: the residual stream **entering** layer `l`, written `h_l`.
- `residual_from(params, cfg, h_l, l)` = decoder layers `l..L-1`: the final residual
  `h_final` before the final RMS norm.
- `forward_from(params, cfg, h_l, l)` = `lm_head_multiplier * W_U rmsnorm_g(h_final)`, the
  logits.

The lens at layer `l`:

```
J_l  = mean over (context, position t) of  d h_final[t] / d h_l[t]         (d x d)
M_l  = lm_head_multiplier * W_U diag(g_final) J_l                          (V x d)
```

Row `v` of `M_l` is the J-lens vector of token `v`; the paper writes `W_U J_l` and
folds the final norm's gain `g_final` and the head multiplier into `W_U`, which we do
explicitly (the data-dependent 1/rms factor of the norm is a positive scalar and does not
change directions, cosines or rankings). `W_U` is the tied embedding for the 90M/91M and
the separate `lm_head.weight` for the 0.5B.

The Jacobian is computed in reverse mode: for a context truncated at position `t`,
`jax.vjp` of `h_l -> h_final[t]`, vmapped over the `d` standard-basis cotangents (in
chunks of 256-512 rows). One such set of passes yields `d h_final[t] / d h_l[s]` for
**every** source position `s <= t` at once (positions `s > t` are exactly zero by
causality; contexts are right-padded to length buckets of 32 to bound recompilation, which
is harmless for the same reason). From it we save two lenses:

- `lens-L<l>.npy`: the **same-position** lens (`s = t`, `t` = last token of the context),
  the quantity asked for here;
- `lens-L<l>-future.npy`: the paper's variant with readout at a fixed later position,
  `mean_{s<=t} d h_final[t] / d h_l[s]`, for free from the same passes. It is dominated by
  the `s = t` term; the Frobenius norm of `d h_final[t] / d h_l[s]` falls by ~5x at lag 1
  and ~15-30x by lag 2 (see the lag profiles below).

Also saved per layer: `jac-L<l>.npy` (`J_l`, d x d), `hlast-L<l>.npy` (the `h_l` at the
final position of every context, for `sparse`), `lens-L<l>.json` (contexts, timings,
statistics).

**Contexts.** `N` windows of 64-128 tokens sampled (seed 0) from the library validation
shard `artifacts/dataset/validation-00000.jsonl.gz` (31 long documents; a 3000-character
slice is tokenized and a random window taken from it), plus the 12 room prompts of
`research/eval/room_prompts.json` (177-210 tokens, ending in `\n\nh:`). Jacobians are
taken at the last token of each context.

**readout.** Workspace loading of token `v` at position `t` = `cos(h_l[t], M_l[v])`
(paper, "workspace loading"). For each room prompt we print, at the final `:` and at the
`h` speaker label, the top-10 loaded tokens, the paper's logit-form readout
`softmax(W_U norm(J_l h_l))`, the plain logit lens, and the model's actual top-10
next-token distribution; loaded-but-not-predicted tokens are listed.

**inject.** 40 filler sentences that mention no place, in the template
`"<filler>. The capital city is"`. At layer `l`, at the filler's last token, add
`alpha * ||h_l[t]|| * u` with `u` the unit lens vector of the country token (` France`,
...), or the unit **unembedding** row of the same token, or a random unit vector (one per
country); `alpha in {2, 4, 8}`. Measured: the teacher-forced log-probability of the full
capital string (` Paris`, ` Tokyo` = 2 tokens, ...) at the end of the prompt, minus the
same quantity on the unmodified prompt ("lift"); the same lift averaged over the 11
other capitals ("others", a generic "say a capital" effect); their difference
("specific"); and the fraction of fillers where the correct capital has the highest
per-token log-prob among the 12 capitals ("top1"). Reference rows: the baseline top1 with
no injection, and the "natural" ceiling `"<filler>. The capital city of <country> is"`.
Countries: France, Italy, Germany, England, Japan, Egypt, Spain, Russia, China, Canada,
Brazil, Greece (all single tokens with a leading space).

**sparse.** Nonnegative orthogonal matching pursuit (`scipy.optimize.nnls` on the active
set) over the unit-normalized lens vectors, `k = 8` atoms, applied to `h_l` at the final
`:` of each room prompt and at the final token of the first 100 lens contexts. Reported:
fraction of `||h_l||^2` explained (= squared norm of the J-space component / squared
norm), and the selected atoms. Controls: the same pursuit over the unembedding rows
(logit-lens frame) and over a random Gaussian dictionary of the same size (V x d).

Run with:

```
cd /Users/ember/dev/h && PYTHONPATH=jax_training JAX_PLATFORM_NAME=cpu H1JAX_SSD=v2 \
  .venv-jax/bin/python research/jlens/jlens.py {check,lens,readout,inject,sparse} --model <m> [--layers ...]
```

(`H1JAX_SSD=v2` selects the TPU-style SSD rewrite, ~20% faster on CPU for the batched
backward pass; numbers are identical to v1 at float32 precision.)

## Compute and timings

Sanity checks (`check`): (a) `forward_from(hidden_at_layer(ids, l), l)` reproduces
`falcon_h1_forward` logits **exactly** (max abs diff 0.0 at l = 8, 12, 16 for the 90M and
l = 18 for the 0.5B; the same ops in the same order); (b) central finite differences of
`h_final[t]` along random unit directions (eps = 1e-3 ||h_l||) agree with the Jacobian to
relative error 3e-4 to 2e-3 (cosine 0.999998-1.000000), and the induced logit change
(through the real final norm + unembedding) to 1e-3 to 5e-3 (float32 arithmetic).

Where the Jacobians were computed:

- **Mac, JAX CPU (12 cores, shared with the model-serving processes)**: a 91M Jacobian
  (512 cotangent rows, layers l..23, T = 128) takes 20-27 s uncontended (l = 12), 16 s at
  l = 16 and ~30 s at l = 8; under four concurrent JAX processes the same Jacobian took
  53-78 s. Batching all 512 rows in one vmapped vjp versus 128-row chunks made no
  difference beyond load noise (73-78 s vs 53-54 s, chunked being *faster* under
  contention), `--xla_cpu_multi_thread_eigen=true` is already the default, and XLA has no
  intra-op thread flag (`--intra_op_parallelism_threads` is rejected). A 0.5B Jacobian
  (1024 rows, layers 18..35) takes 250-320 s on the Mac. Two 91M runs started concurrently
  with a 0.5B run filled the 23 GB swap (a 512-row vjp through the batched SSD backward
  holds ~13-18 GB); the runs were restarted sequentially with 128-row chunks.
- **hbox, PyTorch 2.9.1+rocm6.3 on the Radeon (12.9 GB VRAM)**, `jlens_torch.py`:
  the model's own `FalconH1DecoderLayer` modules called with the kwargs
  `FalconH1Model.forward` builds; Transformers' reference Mamba path (the fast kernels are
  not installed there) with each mixer's SSD `chunk_size` set to 32 so the reference
  path's 6-D intermediates fit; `torch.autograd.grad(..., is_grads_batched=True)` (a
  vmapped vjp) over 16-24 cotangent rows per pass. **Parity** on one context (room prompt 0
  truncated to 96 tokens, 0.5B base, l = 18) against the JAX Jacobian: h_l and h_final
  agree to 7e-7 relative, the d x d Jacobian to **2.3e-6 relative Frobenius error**
  (cosine 1.000004, max abs diff 3e-6). Timings: **91M 7.5 s** per Jacobian at T ~ 80
  (l = 16), 16-18 s for the 184-210-token room prompts, 84 Jacobians in 14.3 min;
  **0.5B 60 s at T = 64, 110 s at T = 97**, ~250 s for the room prompts. The Triton SSD
  scan (`hbox_training/rocm_triton_ssd.py`) also passes parity (2.6e-6) but its backward
  only fits 4 rows per pass (315 s per 0.5B Jacobian) and cannot be vmapped, so it was not
  used.

Contexts actually used: 72 validation windows + the 12 room prompts (84 Jacobians per
layer, seed 0) for every model and layer; the 0.5B models at l = 18 only. With
per-context Jacobians of Frobenius norm ~120 (91M, l = 12) and an across-context spread
of ~100 around a mean of norm ~57-86, the mean Jacobian has ~15-20% relative noise at
N = 84; the ranking-level results below did not change between a 6-context pilot and the
full run except for the (flat) top-by-norm list.

TABLES_PLACEHOLDER

## Reading

**Against the pre-registered expectation.** The lenses exist and are well-behaved as
linear objects (full-rank, effective rank 100-400 of 512, finite-difference-exact), but
nothing in these four models behaves like a reportable, modulable workspace, and the
library-continued-pretrained models do not differ from their bases in that respect.
Concretely: (i) the same-position lens vectors are dominated by a shared component (mean
pairwise cosine 0.41-0.55 at l = 8-12, versus 0.32 between unembedding rows), so the
top-loaded tokens at the room prompts' final `:` are the same ten sentence-openers on
every prompt (`The/There/This/It/If/That` for the base; `Yes/Because/There/Does/Answer/
Assume/However` for the leaf) with cosines of only 0.13-0.25, and the tokens "on its
mind but not said" are other openers, never content (the one prompt-specific readout is
the python-function prompt at l = 16: `Write/Take/Let/Please/Give/Start`). (ii) The
injection test finds no usable transport of country identity to the capital readout:
at l = 8 and 12 the lens direction and the unembedding row of the country token behave
alike (a "specific" lift of +0.3 to +1.2 nats that comes from *suppressing the other
capitals* rather than raising the correct one, whose log-probability mostly falls), and
top-1-among-capitals stays at the 0.08 baseline for every direction and alpha, against
+3.8 nats (base) / +1.9 (leaf) for the natural prompt. At l = 8 both directions produce a
generic "capital-ish" boost for *all* capitals (+0.7 to +1.0): they carry "a country was
mentioned", not which one. The single exception is the leaf at l = 16, where the lens
direction does beat the unembedding row (specific +2.3 to +2.6 vs +0.7 to +1.1; top-1
0.12-0.18 vs 0.02-0.13; random -0.1 to -0.2) - but the correct capital's own
log-probability rises only +0.8 at alpha = 2 and falls at alpha >= 4, so even there the
effect is "not the others" more than "this one". (iii) The J-space component (k = 8 nonnegative atoms) explains 2.5-8% of the
residual norm at l = 8-12 and 7-11% at l = 16 - in the paper's "small" range - but a
random dictionary of the same size explains 20%, and the unembedding frame 6-8%: the
lens frame is not a privileged sparse subframe here, it is a nearly one-directional
cone. The leaf differs from the base only in *which* openers it loads (answer-shaped
ones, consistent with its reading-room training) and in a slightly larger l = 16 J-space
fraction (10.6% vs 7.6% on the room prompts); its lens Jacobians are also more diffuse
(higher effective rank, lower norm). This is the "little or none" outcome the
expectation predicted for base and library-CPT models; it does not test the other half
(that preference post-training assembles the structure), because no DPO/RL checkpoint
was in scope.

**Against the paper's five properties.** *Verbal report* and *directed modulation* need
a model that follows instructions ("what are you thinking about", "hold X in mind while
copying") and could not be tested on these base/CPT models at all; the closest proxy,
the readout at the `h:` turn boundary, shows a sentence-opener state rather than
concepts, and the paper's own hedge applies with force here: the lens only sees
single-token concepts, and a 32k-vocabulary tiny model spends its lens norm on
sub-word fragments (`ournal`, `coming`, `rit`) and punctuation. *Internal reasoning* was
not tested (two-hop prompts with swaps would be the next experiment; the 90M base does not
reliably do two-hop recall, which makes the test ill-posed at this size). *Flexible
generalization* is what `inject` tests and it fails in the specific sense above: the lens
direction is not a better argument to the "capital of" function than the raw
unembedding direction, and neither makes the function produce the right value.
*Selectivity* is the one property partially consistent with the data: the J-space is a
small fraction of the activation (2-11%) and the model's next-token behaviour is
dominated by what lies outside it - but since a random frame of the same size captures
more, "small" here reflects the frame's geometry, not a privileged subset. What we could
not do at all: J-space ablation over a corpus (property 5 proper), swaps in lens
coordinates, and any post-trained comparison; those are the experiments a DPO/RL
checkpoint would unlock.
