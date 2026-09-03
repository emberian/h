| checkpoint | tokens | dtype | lambada_openai (acc) | hellaswag (acc_norm) | arc_easy (acc_norm) | arc_challenge (acc_norm) | piqa (acc_norm) | winogrande (acc) | mean | lambada ppl | minutes |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base-0.5b | - | float16 | 0.496 ± 0.022 | 0.522 ± 0.022 | 0.652 ± 0.021 | 0.410 ± 0.022 | 0.716 ± 0.020 | 0.584 ± 0.022 | 0.563 | 13.27 | 32 |
| hghost-05b-blend090 | 794.7M | float16 | 0.448 ± 0.022 | 0.506 ± 0.022 | 0.576 ± 0.022 | 0.318 ± 0.021 | 0.704 ± 0.020 | 0.550 ± 0.022 | 0.517 | 15.60 | 32 |
| room05b-e2-v5-replay-decay10 | 854.7M | float16 | 0.424 ± 0.022 | 0.516 ± 0.022 | 0.588 ± 0.022 | 0.324 ± 0.021 | 0.714 ± 0.020 | 0.586 ± 0.022 | 0.525 | 16.98 | 32 |

Deltas against the same-family base (z = Δ / √(se²+se²); limit 500 docs/task):

| checkpoint | vs | lambada_openai | hellaswag | arc_easy | arc_challenge | piqa | winogrande | mean Δ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| hghost-05b-blend090 | base-0.5b | -0.048 (z -1.5) | -0.016 (z -0.5) | -0.076 (z -2.5) | -0.092 (z -3.0) | -0.012 (z -0.4) | -0.034 (z -1.1) | -0.046 |
| room05b-e2-v5-replay-decay10 | base-0.5b | -0.072 (z -2.3) | -0.006 (z -0.2) | -0.064 (z -2.1) | -0.086 (z -2.8) | -0.002 (z -0.1) | +0.002 (z +0.1) | -0.038 |
