# Checkpoint evaluation pack

Generated 2026-09-02T01:34:29+00:00. Losses: h1jax on CPU, parameters loaded as float32, compute dtype `float32`, sequence length 512. Furniture: exact training matches of >= 8 tokens whose 8-token windows occur in >= 5 distinct training documents (haunting index). Unseen: positions outside any exact match of >= 8 tokens. Deltas are against the first checkpoint.

## Slices

| slice | sequences | predicted tokens | furniture | matched | documents |
|---|---|---|---|---|---|
| first-32 | 32 | 16,384 | 15.36% | 20.00% | 2 |
| first-512 | 512 | 262,144 | 10.59% | 20.53% | 6 |
| clean-512 | 512 | 262,144 | 6.40% | 12.95% | 11 |

Retention proxy: `research/eval/retention.txt` (52,449 bytes, 14,643 tokens, 28 sequences of 512); training-match coverage at >=8: 0.90%, >=16: 0.12%, >=32: 0.00%.

## Loss (plain, all positions)

| checkpoint | first-32 | first-512 | clean-512 |
|---|---|---|---|
| base | 3.7456 | 3.7875 | 3.2048 |
| hbox-10m | 3.6159 (-0.1297) | 3.8212 (+0.0338) | 3.4025 (+0.1977) |

## Loss (furniture-subtracted)

| checkpoint | first-32 | first-512 | clean-512 |
|---|---|---|---|
| base | 4.0076 | 3.9170 | 3.3192 |
| hbox-10m | 4.1617 (+0.1541) | 4.0032 (+0.0862) | 3.5315 (+0.2123) |

## Loss (unseen positions only)

| checkpoint | first-32 | first-512 | clean-512 |
|---|---|---|---|
| base | 4.1103 | 4.0018 | 3.3992 |
| hbox-10m | 4.2678 (+0.1574) | 4.1084 (+0.1066) | 3.6187 (+0.2194) |

## Loss on furniture positions only

| checkpoint | first-32 | first-512 | clean-512 |
|---|---|---|---|
| base | 2.3012 | 2.6936 | 1.5306 |
| hbox-10m | 0.6075 | 2.2848 | 1.5145 |

## Next-token accuracy (all positions)

| checkpoint | first-32 | first-512 | clean-512 |
|---|---|---|---|
| base | 35.00% | 31.49% | 39.77% |
| hbox-10m | 36.81% | 30.83% | 36.60% |

## Next-token accuracy (furniture-subtracted)

| checkpoint | first-32 | first-512 | clean-512 |
|---|---|---|---|
| base | 30.47% | 30.46% | 38.20% |
| hbox-10m | 27.88% | 28.90% | 34.91% |

## Retention proxy (out-of-corpus English)

| checkpoint | loss | perplexity | accuracy |
|---|---|---|---|
| base | 3.5814 | 35.92 | 33.91% |
| hbox-10m | 3.9097 (+0.3283) | 49.89 | 29.74% |

## Generation memorization (token-weighted over all prompts)

| checkpoint | coverage>=8 | coverage>=16 | coverage>=32 | furniture | quotation>=8 | quotation>=16 | quotation>=32 | longest | gens quoting>=32 |
|---|---|---|---|---|---|---|---|---|---|
| base | 3.06% | 0.00% | 0.00% | 1.18% | 1.88% | 0.00% | 0.00% | 10 | 0/12 |
| hbox-10m | 5.10% | 0.00% | 0.00% | 0.65% | 4.44% | 0.00% | 0.00% | 11 | 0/12 |

Coverage: fraction of generated tokens inside an exact training match of at least the threshold. Furniture: fraction inside windows shared by >= 5 documents. Quotation: covered but not furniture. Generations are stored blind under `generations/<id>.jsonl`; `generations/KEY.json` maps ids to checkpoints.

## Checkpoints

| name | blind id | path | loss seconds | generation seconds |
|---|---|---|---|---|
| base | a602ca843c7a | `/Users/ember/dev/h/kaggle/base_model_dataset_public` | 3368 | 33 |
| hbox-10m | e087a46e70e8 | `/Users/ember/dev/h/artifacts/checkpoints/hbox-full-cpt-v1-10m` | 3381 | 80 |
