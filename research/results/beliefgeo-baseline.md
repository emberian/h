# Belief-geometry instrument: Mess3 slice, corpus v1.1, and the base-checkpoint probe

Date: 2026-09-01. Instrument: `src/hghost/beliefgeo.py` (`hghost-beliefgeo`) with the JAX worker
`src/hghost/beliefgeo_jax.py`; tests in `tests/test_beliefgeo.py`. Plan: `FABLETHOUGHT.md` section 5.2.
Reference: Shai, Riechers, Teixeira, Oldenziel, Shai, "Transformers represent belief state geometry in their
residual stream", arXiv 2405.15943.

This is the **control baseline**: the unmodified `tiiuae/Falcon-H1-Tiny-90M-Base` checkpoint
(`kaggle/base_model_dataset_public`), which has never seen Mess3, probed on held-out Mess3 token
sequences. The training arm (checkpoints trained on corpus v1.1) runs on the TPU later and is probed
with the same command against the same held-out sequences.

## Headline

- The base model's residual stream already **linearly encodes the Mess3 belief state**, including the
  fractal geometry: at x=0.15, α=0.6 the best residual layer (layer03) reaches test R² = 0.999
  (MSE 3.1e-5), the layer00 Mamba SSM state reaches R² = 0.9996, and the shuffled-target control is
  −0.001. The predicted points on the 2-simplex reproduce the Sierpinski-like structure of the true
  beliefs (`beliefgeo-baseline/x0.15-a0.6-probe-simplex-best.png`).
- A pure-recency linear baseline explains most of it: a one-hot of the last 16 symbols gives
  R² = 0.987 (MSE 6.0e-4). The residual and the SSM state beat that baseline by a factor of ~20 in
  MSE, which is the part that a recency lookup does not explain. Mess3's Bayesian update is close to a
  linear function of exponentially-weighted symbol counts at a few time scales, and that is what a
  multi-rate SSM (and the early residual stream that reads it) provides for any token stream.
- Consequence for the training arm: **R² on Mess3 is not a discriminating statistic for this model
  family**. The measurements that can still move are (i) the MSE at the fine scale of the fractal,
  (ii) the depth profile (where the belief is best decoded, currently layers 0-3 and then a slow
  decay), (iii) the SSM-state vs residual comparison per layer, and (iv) sibling controls (a checkpoint
  trained without the slice, random-init). A process whose belief is *not* near-linear in recency
  features (RRXOR-like, or a longer-memory metasyntax) is the better instrument for "made to represent".

## The process

Mess3 (Marzen & Crutchfield 2017; Shai et al. 2024) has three hidden states and three symbols. With
`y = 1 − 2x` and `b = (1 − α)/2`, `T[a][i][j] = P(emit a, next state j | state i)`:

```
T[A] = [[αy, bx, bx], [αx, by, bx], [αx, bx, by]]
T[B] = [[by, αx, bx], [bx, αy, bx], [bx, αx, by]]
T[C] = [[by, bx, αx], [bx, by, αx], [bx, bx, αy]]
```

i.e. the state stays with probability `y` and moves to each other state with probability `x`; the
symbol is the *destination* state's label with probability `α`, else each other symbol with
probability `b`. The stationary distribution is uniform. Beliefs are computed exactly with the forward
algorithm, `η' = η T[x] / (η T[x] 1)`, from the stationary prior (`belief_states`), and the test
`test_belief_update_matches_brute_force_forward_algorithm` checks it against explicit matrix products.

Two parameter settings were generated and probed (16,000 pool + 256 held-out sequences × 512 symbols,
seed 0, each):

| setting | notes |
|---|---|
| x=0.15, α=0.6 | the classic Mess3 fractal simplex (Fig. 1 of the paper); default of the authors' library; **used for corpus v1.1** |
| x=0.05, α=0.85 | what the paper's printed `T[A]` entries (0.765, 0.00375, 0.0425, 0.0675) decode to (`test_mess3_matches_the_paper_matrices`); very sticky, beliefs pile up at the vertices |

`hghost-beliefgeo generate` defaults are x=0.05, α=0.85 and `--x/--alpha` select the other.

## Emission tokens

`hghost-beliefgeo tokens` enumerates non-special Falcon-H1 tokens that decode to exactly one
printable Unicode *symbol* character and re-encode to the same single id alone and as a run, then
counts every token id in `artifacts/tokenized/train.bin` (374,405,212 tokens). Fourteen tokens pass;
the chosen four are all ≤ 302 occurrences in the corpus (< 1 ppm):

| glyph | id | name | corpus count |
|---|---|---|---|
| `⁻` | 17675 | SUPERSCRIPT MINUS | 0 |
| `│` | 32670 | BOX DRAWINGS LIGHT VERTICAL | 10 |
| `←` | 25112 | LEFTWARDS ARROW | 105 |
| `∇` | 30357 | NABLA | 119 |
| `∂` | 23431 | PARTIAL DIFFERENTIAL | 302 |
| `×` | 19201 | MULTIPLICATION SIGN | 1002 |
| `∞` | 28567 | INFINITY | 1606 |
| `→` | 29058 | RIGHTWARDS ARROW | 2567 |
| `™` | 29579 | TRADE MARK SIGN | 3730 |
| `−` | 26459 | MINUS SIGN | 4157 |
| `€` | 23487 | EURO SIGN | 11140 |
| `©` | 22309 | COPYRIGHT SIGN | 12709 |
| `°` | 9266 | DEGREE SIGN | 36563 |
| `®` | 19989 | REGISTERED SIGN | 43415 |

Chosen: prefix `│` (32670, count 10); emissions `∇` (30357, count 119) = symbol A, `∂` (23431, count
302) = symbol B, `←` (25112, count 105) = symbol C. Symbols rather than the zero-count CJK/Hangul
single-character tokens so that the regime marker carries no natural-language morphology into the
ghost; `⁻` (count 0) was passed over as visually a hyphen. A rendered 257-token document re-tokenizes
to exactly its ids (`round_trip` in `mess3-tokens.json`).

Document format: `[│] + one emission token per symbol + [EOS]` (514 tokens for 512 symbols). The
prefix is a single regime marker after the document boundary: it gives the model a position at which
the belief is the stationary prior before the first symbol, it survives the trainer's 512-token window
cuts (a 514-token document straddles two or three windows), and it lets the probe run
`[prefix, symbols…]` without depending on EOS as a first token.

## Corpus v1.1 (`artifacts/beliefgeo/corpus-v1.1-mess3/`, Kaggle layout, not uploaded)

Built from the x=0.15, α=0.6 pool with `--fraction 0.02 --seed 0`. Each synthetic document is
assigned a slot `Uniform{0..4837}` (insert before v1 document `slot`; 4837 = append) and documents
sharing a slot are written in index order; every v1 document keeps its bytes and order.

| quantity | value |
|---|---|
| v1 train tokens | 374,405,212 (sha256 `fdaa8b85…3124`, 4,837 documents) |
| synthetic documents used | 14866 of the 16,000 pool × 514 tokens = 7,641,124 tokens |
| synthetic fraction of v1.1 | 2.0001% |
| v1.1 train tokens | 382,046,336 (764,092,672 bytes, 19,703 documents) |
| v1.1 `train.bin` sha256 | `3729532c00e085eae2517db066d5146d45e2f92208e919987b8b1ef665661ca3` |
| `validation.bin` | byte-identical to v1, sha256 `07bce22a3de6101d4d946d1592a500c30a3790afffdecb8da6bd99777b985928` |
| `mess3-validation.bin` | 256 held-out documents, 131,584 tokens, sha256 `561231b5004ae35700263dabda0cfc70829093d8dda0a8f3bca923bbd4e5e237` |
| insertion groups | 4609 (max 10 documents in one slot) |
| 512-token trainer windows touching synthetic tokens | 19,531 of 746,184 (2.62%) |
| verification | 374,405,212 v1 tokens byte-identical outside insertions; every insertion re-read |

`validation-report.json` keeps the v1 schema (the TPU kernels glob for it and verify
`splits.train.sha256` and `splits.validation.sha256`) with the train split updated and a `derived_from`
block; `manifest.json` records the process, the token mapping, every insertion offset (v1 and v1.1) and
hashes; `dataset-metadata.json` is `emberian64/hghost-curated-tokens-v1-1-mess3`, title "H Ghost
corpus v1.1 + Mess3 slice". The dataset-level license is left as v1's "unknown" because Kaggle's
license field is dataset-wide and the bulk is the v1 corpus; the description and README state that the
synthetic slice and belief files are CC0. The stream reads correctly through `h1jax.data.TokenStream`.

A superseded build from the x=0.05, α=0.85 pool had sha256 `2f2044c0251cb47efeff0fa752991fa0d1887e355918592d74e634d9c953e84f`
(same size and insertion plan); it is not kept.

## Probe method

- Rows: 64 held-out sequences × 512 tokens (`│` + the first 511 symbols), FP32, CPU JAX, batch 8.
  Target at position t ≥ 1 is the exact belief after symbol t−1; the prefix position is excluded.
  Split by sequence: 51 train (10 of them used to choose the ridge), 13 test (26,061 / 6,643 rows).
- Features: residual stream after the embedding (`embed`), after each of the 24 decoder layers, and
  after the final RMS norm (512-d); the Mamba-2 SSM state (24 heads × 32 × 64 = 49,152-d) at every
  16th position (2,048 rows, 1,632 / 416), fit in the dual form.
- Probe: affine ridge regression to the 3-simplex; ridge relative to the mean Gram eigenvalue chosen
  from {1e-4 … 10} on held-out training sequences, refit on all training rows, scored on test rows
  (pooled R² over the three components, MSE).
- Controls and baselines: the same procedure on globally permuted targets (`shuffled`), and linear
  probes from the one-hot of the last k symbols, k ∈ {1, 4, 16} (`recency`). `embed` equals the k=1
  baseline exactly, as it must (three distinct tokens span the same 3-d space).
- SSM state: `h1jax.model.ssd_forward` only forms chunk-boundary states, so `beliefgeo_jax`
  recomputes the per-token recurrence `h_t = exp(dt_t A) h_(t−1) + dt_t B_t x_tᵀ` from the same
  projections `mamba()` builds and checks `y_t = h_t C_t + D x_t` against `ssd_forward` on the first
  batch of every layer. Worst layer at x=0.15: layer05: max |Δy| = 4.6e-05 against max |y| = 52.4 (8.7e-07 relative); at x=0.05: layer03: max |Δy| = 1.6e-05 against max |y| = 13.2 (1.2e-06 relative).

## Results: x=0.15, α=0.6 (the fractal; the corpus-v1.1 setting)

Plots: `beliefgeo-baseline/x0.15-a0.6-probe-simplex-best.png` (true beliefs, k=16 baseline, best
layer), `beliefgeo-baseline/x0.15-a0.6-probe-simplex.png` (every layer), `beliefgeo-baseline/x0.15-a0.6-probe-r2.png`.

| features | R² | shuffled R² | MSE | SSM state R² | SSM shuffled R² |
|---|---|---|---|---|---|
| recency k=1 (one-hot) | 0.774 | -0.001 | 0.0103 | – | – |
| recency k=4 (one-hot) | 0.985 | -0.001 | 0.0007 | – | – |
| recency k=16 (one-hot) | 0.987 | -0.001 | 0.0006 | – | – |
| residual embed | 0.774 | -0.001 | 0.0103 | – | – |
| residual layer00 | 0.999 | -0.001 | 0.0000 | 1.000 | -0.016 |
| residual layer01 | 0.999 | -0.001 | 0.0000 | 0.999 | -0.024 |
| residual layer02 | 0.999 | -0.001 | 0.0000 | 0.998 | -0.015 |
| residual layer03 | 0.999 | -0.001 | 0.0000 | 0.998 | -0.022 |
| residual layer04 | 0.999 | -0.001 | 0.0000 | 0.994 | -0.018 |
| residual layer05 | 0.999 | -0.001 | 0.0001 | 0.996 | -0.019 |
| residual layer06 | 0.998 | -0.001 | 0.0001 | 0.993 | -0.015 |
| residual layer07 | 0.998 | -0.001 | 0.0001 | 0.980 | -0.012 |
| residual layer08 | 0.997 | -0.001 | 0.0001 | 0.962 | -0.017 |
| residual layer09 | 0.998 | -0.001 | 0.0001 | 0.978 | -0.022 |
| residual layer10 | 0.997 | -0.001 | 0.0001 | 0.897 | -0.011 |
| residual layer11 | 0.997 | -0.001 | 0.0002 | 0.987 | -0.012 |
| residual layer12 | 0.996 | -0.001 | 0.0002 | 0.979 | -0.011 |
| residual layer13 | 0.996 | -0.001 | 0.0002 | 0.983 | -0.011 |
| residual layer14 | 0.996 | -0.001 | 0.0002 | 0.984 | -0.011 |
| residual layer15 | 0.995 | -0.001 | 0.0002 | 0.995 | -0.013 |
| residual layer16 | 0.994 | -0.001 | 0.0003 | 0.988 | -0.009 |
| residual layer17 | 0.994 | -0.001 | 0.0003 | 0.994 | -0.013 |
| residual layer18 | 0.993 | -0.001 | 0.0003 | 0.995 | -0.010 |
| residual layer19 | 0.993 | -0.001 | 0.0003 | 0.994 | -0.014 |
| residual layer20 | 0.992 | -0.001 | 0.0004 | 0.992 | -0.014 |
| residual layer21 | 0.992 | -0.001 | 0.0004 | 0.994 | -0.013 |
| residual layer22 | 0.992 | -0.001 | 0.0004 | 0.993 | -0.013 |
| residual layer23 | 0.991 | -0.001 | 0.0004 | 0.988 | -0.019 |
| residual final_norm | 0.990 | -0.001 | 0.0005 | – | – |

## Results: x=0.05, α=0.85 (the paper's printed matrices)

Plots: `beliefgeo-baseline/x0.05-a0.85-probe-simplex-best.png`, `…-probe-simplex.png`, `…-probe-r2.png`.

| features | R² | shuffled R² | MSE | SSM state R² | SSM shuffled R² |
|---|---|---|---|---|---|
| recency k=1 (one-hot) | 0.803 | -0.000 | 0.0324 | – | – |
| recency k=4 (one-hot) | 0.965 | -0.000 | 0.0058 | – | – |
| recency k=16 (one-hot) | 0.967 | -0.000 | 0.0055 | – | – |
| residual embed | 0.803 | -0.000 | 0.0324 | – | – |
| residual layer00 | 0.995 | -0.000 | 0.0009 | 0.996 | -0.004 |
| residual layer01 | 0.996 | -0.000 | 0.0007 | 0.997 | 0.001 |
| residual layer02 | 0.996 | -0.000 | 0.0007 | 0.995 | -0.004 |
| residual layer03 | 0.995 | -0.000 | 0.0007 | 0.994 | -0.010 |
| residual layer04 | 0.994 | -0.000 | 0.0010 | 0.991 | -0.006 |
| residual layer05 | 0.993 | -0.001 | 0.0012 | 0.990 | -0.006 |
| residual layer06 | 0.991 | -0.001 | 0.0014 | 0.985 | -0.002 |
| residual layer07 | 0.989 | -0.001 | 0.0018 | 0.966 | -0.008 |
| residual layer08 | 0.987 | -0.001 | 0.0021 | 0.949 | -0.003 |
| residual layer09 | 0.988 | -0.001 | 0.0021 | 0.960 | -0.012 |
| residual layer10 | 0.986 | -0.001 | 0.0022 | 0.912 | -0.005 |
| residual layer11 | 0.986 | -0.001 | 0.0023 | 0.969 | -0.000 |
| residual layer12 | 0.986 | -0.001 | 0.0023 | 0.976 | -0.005 |
| residual layer13 | 0.985 | -0.001 | 0.0025 | 0.969 | -0.003 |
| residual layer14 | 0.985 | -0.001 | 0.0024 | 0.973 | 0.001 |
| residual layer15 | 0.984 | -0.001 | 0.0026 | 0.982 | -0.004 |
| residual layer16 | 0.983 | -0.001 | 0.0027 | 0.974 | -0.002 |
| residual layer17 | 0.982 | -0.001 | 0.0030 | 0.980 | -0.004 |
| residual layer18 | 0.980 | -0.001 | 0.0032 | 0.986 | -0.008 |
| residual layer19 | 0.978 | -0.001 | 0.0036 | 0.980 | -0.002 |
| residual layer20 | 0.977 | -0.001 | 0.0037 | 0.977 | -0.009 |
| residual layer21 | 0.977 | -0.001 | 0.0038 | 0.978 | -0.004 |
| residual layer22 | 0.977 | -0.001 | 0.0038 | 0.977 | -0.002 |
| residual layer23 | 0.977 | -0.001 | 0.0038 | 0.970 | -0.005 |
| residual final_norm | 0.975 | -0.001 | 0.0041 | – | – |

## Reading the numbers

- Both settings: the residual stream is decodable to R² ≥ 0.99 from layer00 on, peaks in layers 1-3,
  and declines slowly through the stack (0.975 / 0.990 at `final_norm`); the SSM state tracks the
  residual within ~0.01 except for a dip at layer10 (0.91 / 0.90) and layers 07-09. Shuffled controls
  are within ±0.02 of zero everywhere (the SSM dual fits are slightly negative because 1,632 rows in
  49,152 dimensions overfit noise).
- The recency baselines are the honest yardstick: k=4 already gives 0.965 / 0.985, k=16 gives
  0.967 / 0.987. The residual's gain over k=16 is in MSE (x=0.05: 5.5e-3 → 7e-4; x=0.15: 6.0e-4 →
  3.1e-5). In the simplex plots the k=16 prediction lands on a discrete lattice (a linear map of lag
  one-hots is a sumset, which is itself Sierpinski-shaped), while the residual prediction is continuous
  and, at x=0.15, reproduces the true fractal; at x=0.05 the residual prediction is a diffuse cloud
  around each vertex and the fine structure is blurred, even though R² is 0.996.
- Nothing here says the base model *represents* Mess3; it says that the belief state of this process
  is close to a linear readout of multi-timescale recency features, which an SSM computes for any
  stream. The training arm should therefore report MSE (not only R²), the depth profile, and the same
  probe on a sibling trained without the slice; and the next instrument should be a process whose
  mixed-state presentation is not recoverable from recency alone.

## Runtime (M2 Max, CPU, machine load average ≈ 140 from other sessions)

| step | wall time |
|---|---|
| `generate` (16,256 × 512, exact beliefs) | 9.5-9.7 s |
| `tokens` (bincount over 374M tokens + candidate scan) | 5.2 s |
| `build` (weave 764 MB, verify, hash, copy) | 10-12 s |
| `probe` worker per setting (64 × 512 rows, 26 residual + 24 SSM fits) | load 6 s, forward 270 s, worker total 477 s (x=0.15); 468 s (x=0.05) |
| `probe` driver (baselines + plots) | ~40 s |
| `tests/test_beliefgeo.py` (12 tests) | 1.6 s |

## Exact commands

```
.venv/bin/python -m hghost.beliefgeo generate --process mess3 --x 0.15 --alpha 0.6 --sequences 16000 --holdout 256 --length 512 --seed 0 --output artifacts/beliefgeo/mess3-x0.15-a0.6
.venv/bin/python -m hghost.beliefgeo generate --process mess3 --x 0.05 --alpha 0.85 --sequences 16000 --holdout 256 --length 512 --seed 0 --output artifacts/beliefgeo/mess3-x0.05-a0.85
.venv/bin/python -m hghost.beliefgeo tokens --tokenizer kaggle/base_model_dataset_public --train-bin artifacts/tokenized/train.bin --output artifacts/beliefgeo/tokens
.venv/bin/python -m hghost.beliefgeo build --generated artifacts/beliefgeo/mess3-x0.15-a0.6 --tokens artifacts/beliefgeo/tokens/mess3-tokens.json --train-bin artifacts/tokenized/train.bin --fraction 0.02 --seed 0 --output artifacts/beliefgeo/corpus-v1.1-mess3
.venv/bin/python -m hghost.beliefgeo probe --checkpoint kaggle/base_model_dataset_public --generated artifacts/beliefgeo/mess3-x0.15-a0.6 --tokens artifacts/beliefgeo/tokens/mess3-tokens.json --output artifacts/beliefgeo/probe-base-x0.15-a0.6 --sequences 64 --length 512 --batch 8 --ssm-layers all --ssm-stride 16 --force
.venv/bin/python -m hghost.beliefgeo probe --checkpoint kaggle/base_model_dataset_public --generated artifacts/beliefgeo/mess3-x0.05-a0.85 --tokens artifacts/beliefgeo/tokens/mess3-tokens.json --output artifacts/beliefgeo/probe-base-x0.05-a0.85 --sequences 64 --length 512 --batch 8 --ssm-layers all --ssm-stride 16 --force
.venv/bin/python -m pytest tests/test_beliefgeo.py -q
uvx ruff check src/hghost/beliefgeo.py src/hghost/beliefgeo_jax.py tests/test_beliefgeo.py && uvx ruff format src/hghost/beliefgeo.py src/hghost/beliefgeo_jax.py tests/test_beliefgeo.py
```

`hghost-beliefgeo` is the installed entry point for the same subcommands. The probe driver runs the
worker as `.venv-jax/bin/python -m hghost.beliefgeo_jax` with `PYTHONPATH=src` (override with
`--jax-python`); re-running `probe` without `--force` reuses the worker outputs and only recomputes the
baselines, plots and table. For a trained checkpoint, point `--checkpoint` at its Hugging Face
directory and keep `--generated`, `--tokens`, `--sequences` and `--seed` identical so the test rows match.

## Files

- Code: `src/hghost/beliefgeo.py`, `src/hghost/beliefgeo_jax.py`, `tests/test_beliefgeo.py`; `pyproject.toml`
  gains `hghost-beliefgeo` and `matplotlib` (`uv add matplotlib`).
- Data (gitignored under `artifacts/beliefgeo/`): `mess3-x0.15-a0.6/`, `mess3-x0.05-a0.85/` (symbols,
  states, beliefs, holdouts, manifests), `tokens/mess3-tokens.json` (+ `train-token-counts.npy`),
  `corpus-v1.1-mess3/`, `probe-base-x0.15-a0.6/`, `probe-base-x0.05-a0.85/` (`probe-results.json`,
  `probe-predictions.npz`, `probe-table.md`, the three PNGs).
- This directory: `beliefgeo-baseline/*.png` and `*-probe-table.md` copied from the probe outputs.
