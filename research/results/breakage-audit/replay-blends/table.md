| checkpoint | tokens | dtype | lambada_openai (acc) | hellaswag (acc_norm) | arc_easy (acc_norm) | arc_challenge (acc_norm) | piqa (acc_norm) | winogrande (acc) | mean | lambada ppl | minutes |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base-0.5b | - | float16 | 0.496 ± 0.022 | 0.522 ± 0.022 | 0.652 ± 0.021 | 0.410 ± 0.022 | 0.716 ± 0.020 | 0.584 ± 0.022 | 0.563 | 13.27 | 31 |
| replay-blend0.80 | 854.7M | float16 | 0.476 ± 0.022 | 0.512 ± 0.022 | 0.632 ± 0.022 | 0.350 ± 0.021 | 0.712 ± 0.020 | 0.592 ± 0.022 | 0.546 | 13.47 | 30 |
| replay-blend0.90 | 854.7M | float16 | 0.444 ± 0.022 | 0.514 ± 0.022 | 0.602 ± 0.022 | 0.340 ± 0.021 | 0.710 ± 0.020 | 0.588 ± 0.022 | 0.533 | 14.89 | 30 |

Deltas against the same-family base (z = Δ / √(se²+se²); limit 500 docs/task):

| checkpoint | vs | lambada_openai | hellaswag | arc_easy | arc_challenge | piqa | winogrande | mean Δ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| replay-blend0.80 | base-0.5b | -0.020 (z -0.6) | -0.010 (z -0.3) | -0.020 (z -0.7) | -0.060 (z -2.0) | -0.004 (z -0.1) | +0.008 (z +0.3) | -0.018 |
| replay-blend0.90 | base-0.5b | -0.052 (z -1.6) | -0.008 (z -0.3) | -0.050 (z -1.6) | -0.070 (z -2.3) | -0.006 (z -0.2) | +0.004 (z +0.1) | -0.030 |
