# Checkpoint evaluation pack: baseline (base vs hbox 10M)

Date: 2026-09-01 (run 20:33-21:33 local). Full outputs in `research/results/evalpack-baseline/`
(`report.md`, `report.json`, `memorization.jsonl`, blind `generations/<id>.jsonl` + `generations/KEY.json`).

## Command

```sh
.venv/bin/hghost-evalpack --output research/results/evalpack-baseline --parallel 2 \
    --checkpoint base=kaggle/base_model_dataset_public \
    --checkpoint hbox-10m=artifacts/checkpoints/hbox-full-cpt-v1-10m
# defaults: --sequences 32,512 --clean-sequences 512 --sequence-length 512
#           --min-tokens 8 --min-documents 5 --thresholds 8,16,32 --dtype float32
# morning: add one --checkpoint NAME=DIR per TPU checkpoint and --parallel 4;
#          cached losses/generations are reused, only new checkpoints are evaluated.
```

`hghost-evalpack` (`src/hghost/evalpack.py`) runs in the main venv and calls two workers:
`hghost.evalpack_jax` inside `.venv-jax` (`JAX_PLATFORM_NAME=cpu`, parameters loaded as
float32, compute dtype float32, h1jax `falcon_h1_forward` with `layer_scan=True`) for per-token
losses, and `hghost.evalpack_mlx` inside `~/.cache/h1-distributed/venv` (mlx-lm 0.32.0, Apple GPU)
for sampling. Tests: `.venv/bin/python -m pytest tests/test_evalpack.py` (10 pass, 1 JAX test
skipped) and `PYTHONPATH=src JAX_PLATFORM_NAME=cpu .venv-jax/bin/python -m pytest
tests/test_evalpack.py -p no:cacheprovider` (8 pass, 3 index tests skipped: no pydivsufsort there).

## What is measured

| Slice | Sequences | Predicted tokens | Furniture | Any match | Documents |
|---|---:|---:|---:|---:|---:|
| first-32 (the project's reference slice) | 32 | 16,384 | 15.36% | 20.00% | 2 |
| first-512 | 512 | 262,144 | 10.59% | 20.53% | 6 |
| clean-512 | 512 | 262,144 | 6.40% | 12.95% | 11 |

- Slices are contiguous 512-token windows of `artifacts/tokenized/validation.bin` in file order
  (identical to h1jax `ValidationStream`); the label at each position is the next token.
- **clean-512**: 512 evenly spaced sequences among the 3,041 sequences that lie entirely inside
  the 12 validation documents the family analysis marks `clean`
  (`artifacts/families/leakage-report.json`, `leakage_level == "clean"`; no work-family or
  series sibling in train). 11 of the 12 documents are represented; the subsample skips
  `richard_sylvan/1974.Another 'Fatal' Objection...` (only 5 eligible sequences).
- **Furniture**: a label position is excluded when it lies inside an exact training match of
  >= 8 tokens whose 8-token windows occur in >= 5 distinct training documents (haunting index,
  `artifacts/haunting-index`). This is stricter than whole-span `distinct_documents`: the
  197-token JSTOR licence paragraph is quoted whole by only 2-3 documents, but every 8-token
  window of it is in 60+, so it counts as furniture. **Unseen** additionally drops every
  position inside any exact >= 8-token training match (quotation as well as furniture).
- **Retention proxy**: chapters II-V of *The Adventures of Tom Sawyer* (Gutenberg text found
  offline in a Go module's testdata; `research/eval/retention.txt`, 52,449 bytes, 14,643 tokens,
  28 sequences). It is not in the corpus: 0.90% of its tokens sit inside some >= 8-token
  training match, 0.12% inside >= 16, none >= 32, longest match 17 tokens.
- **Generations**: 12 prompts (`research/eval/prompts.json`: the three hbox prompts plus
  "The geometry of", five library-flavoured openings, one furniture bait, two neutral), seed
  20260901 + prompt index, temperature 0.8, top-p 0.95, repetition penalty 1.08, 128 new tokens,
  every checkpoint cast to float32 before loading. Files are named by a hash of the checkpoint
  path; `KEY.json` is the only mapping.
- **Memorization**: each completion is re-tokenized with the checkpoint's `tokenizer.json`
  and scanned against the training stream; coverage at 8/16/32, furniture (windows in >= 5
  documents) versus quotation (covered but not furniture), longest span.

## Losses (natural log, per predicted token)

| Checkpoint | first-32 plain | first-32 furniture-free | first-512 plain | first-512 furniture-free | clean-512 plain | clean-512 furniture-free | retention |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | **3.7456** | 4.0076 | 3.7875 | 3.9170 | 3.2048 | 3.3192 | 3.5814 |
| hbox-10m | 3.6159 (-0.1297) | 4.1617 (+0.1541) | 3.8212 (+0.0338) | 4.0032 (+0.0862) | 3.4025 (+0.1977) | 3.5315 (+0.2123) | 3.9097 (+0.3283) |

Unseen-only losses (no exact >= 8-token match at all): base 4.1103 / 4.0018 / 3.3992,
hbox-10m 4.2678 / 4.1084 / 3.6187 on first-32 / first-512 / clean-512.
Loss on furniture positions only: base 2.3012 / 2.6936 / 1.5306, hbox-10m **0.6075** / 2.2848 / 1.5145.

Next-token accuracy (all positions, furniture-free): base 35.00% / 30.47%, 31.49% / 30.46%,
39.77% / 38.20%; hbox-10m 36.81% / 27.88%, 30.83% / 28.90%, 36.60% / 34.91%. Retention
perplexity 35.92 -> 49.89, accuracy 33.91% -> 29.74%.

The base model's first-32 loss reproduces the reference (3.745613 hbox Transformers BF16,
3.7458 h1jax TPU BF16): 3.745556 here in FP32 on CPU, accuracy 34.998% vs 34.943%. The hbox 10M
checkpoint gives 3.61586 vs the 3.615983 reported in BF16.

## Generation memorization

| Checkpoint | tokens | coverage >= 8 | >= 16 | >= 32 | furniture | quotation >= 8 | longest span |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 1,436 | 3.06% | 0.00% | 0.00% | 1.18% | 1.88% | 10 (` is equal to the sum of the squares of the`, 3 docs) |
| hbox-10m | 1,530 | 5.10% | 0.00% | 0.00% | 0.65% | 4.44% | 11 (`. In the early 1940s,`, 2 docs) |

Neither model reproduces any 16-token run of training text in 12 x 128 sampled tokens; the
>= 8 matches are ordinary English phrases. The furniture-bait prompt (`Library of Congress
Cataloging-in-Publication Data`) did not trigger a CIP block from either model.

## Reading

1. **The hbox 10M "improvement" is page furniture.** Its -0.130 on first-32 comes entirely from
   the 15% of positions that are furniture (JSTOR / Reveal Digital download notices and the
   licence paragraph of the `MagazineStudies.2` scan, whose sibling issues are in train): loss
   there fell from 2.30 to 0.61. On the other 85% of positions the checkpoint is **worse** by
   +0.154, and it is worse on every other measure: first-512 (+0.034 plain, +0.086
   furniture-free), the family-clean slice (+0.198 plain, +0.212 furniture-free, accuracy
   39.8% -> 36.6%), and out-of-corpus English (+0.328, perplexity 36 -> 50). This is consistent
   with the BF16 update-resolution failure described in `hbox-cpt-10m.md`; after 10M tokens
   that run had learned boilerplate and lost general competence. The first-32 slice should not
   be quoted as a headline number again; furniture-free clean-512 is the one to watch.
2. The clean documents are easier for the base model (3.20 vs 3.79 on the periodical-heavy
   prefix), so cross-slice numbers are not comparable; only same-slice deltas are.
3. Generations from the 10M checkpoint are library-like but degraded (fragmented lines,
   "the / beginning / is not / of / being or nothing" for the being-nothing prompt), matching
   the loss picture; the base writes assistant-style lists and quiz questions.

## Surprises and caveats

- h1jax's `write_hf_config` writes `mamba_expand` as the float 1.5; both mlx-lm's `ModelArgs`
  and the Transformers 5 config that `AutoTokenizer` consults reject it. The MLX worker stages
  a symlinked copy with `mamba_expand: 2` (the SSM is sized from `mamba_d_ssm` anyway), so
  tonight's TPU checkpoints load; verified on a base model re-saved through h1jax. Anyone
  loading those checkpoints with Transformers directly will hit the same error.
- mlx-lm folds the Falcon-H1 multipliers into the weights at load time in the stored dtype, so a
  BF16 file and its exact FP32 upcast sampled differently (max weight diff 2.4e-4, logits 0.09).
  The worker now converts every checkpoint's weights to float32 before loading; a BF16 file and
  its FP32 copy then produce identical tokens for all 12 prompts, and two runs of the same
  checkpoint are bit-identical.
- JAX on this CPU is far slower than the "about a minute" estimate: ~1.3 s per 512-token
  sequence when the box is idle (~28 GFLOP/s; XLA uses under two cores, 7.7 s of a 13 s
  8-sequence batch is the Mamba block) and ~3.6 s tonight with the box at load average 220.
  Multiple CPU devices via `pmap` did not help (1.28 -> 1.08 s/seq at 8 devices); separate
  worker processes do (three at once: 2.25x aggregate), hence `--parallel`. The two-checkpoint
  loss phase took 56 min; expect 8 TPU checkpoints at `--parallel 4` to take about an hour and
  a half if the box is as busy as tonight, half that if idle. Workers save every 64 rows and
  resume, and the haunting masks (3 min, 6 processes) are cached under `cache/`.
- One retention text of 14.6k tokens is a proxy only; the numbers are for deltas, not
  benchmarks.

## Could not be done / not done

- Nothing under `artifacts/tokenized`, `artifacts/dataset`, `artifacts/extracted`,
  `artifacts/haunting-index` or `jax_training/h1jax` was modified. Nothing was committed.
- The hbox checkpoint was fetched without `optimizer.pt` (349 MB); it has its own tokenizer
  files (`model.safetensors` sha256 `752d368a...`, matching `hbox-cpt-10m.md`).
- The first evaluation run was killed by the session interruption after ~10 min; the second
  completed. The `.venv` lost `pytest` to another agent's resync mid-session and was reinstalled.
