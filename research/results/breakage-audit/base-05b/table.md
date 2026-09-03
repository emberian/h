| checkpoint | tokens | dtype | lambada_openai (acc) | hellaswag (acc_norm) | arc_easy (acc_norm) | arc_challenge (acc_norm) | piqa (acc_norm) | winogrande (acc) | mean | lambada ppl | minutes |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base-0.5b | - | float16 | 0.485 ± 0.016 | 0.523 ± 0.016 | 0.657 ± 0.015 | 0.413 ± 0.016 | 0.720 ± 0.014 | 0.596 ± 0.016 | 0.566 | 12.73 | 61 |

Deltas against the same-family base (z = Δ / √(se²+se²); limit 1000 docs/task):

| checkpoint | vs | lambada_openai | hellaswag | arc_easy | arc_challenge | piqa | winogrande | mean Δ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
