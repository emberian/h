| checkpoint | tokens | dtype | lambada_openai (acc) | hellaswag (acc_norm) | arc_easy (acc_norm) | arc_challenge (acc_norm) | piqa (acc_norm) | winogrande (acc) | mean | lambada ppl | minutes |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base-0.5b | - | float16 | ERR | ERR | ERR | ERR | ERR | ERR | - | - | 2 |
| room05b-e1-decay10 | 417.5M | float16 | 0.424 ± 0.022 | 0.506 ± 0.022 | 0.566 ± 0.022 | 0.314 ± 0.021 | 0.702 ± 0.020 | 0.558 ± 0.022 | 0.512 | 17.37 | 31 |
| room05b-e2-v3-decay10 | 793.9M | float16 | 0.412 ± 0.022 | 0.498 ± 0.022 | 0.546 ± 0.022 | 0.310 ± 0.021 | 0.692 ± 0.021 | 0.540 ± 0.022 | 0.500 | 18.52 | 31 |
| room05b-e2-v4-decay10 | 794.7M | float16 | 0.428 ± 0.022 | 0.502 ± 0.022 | 0.548 ± 0.022 | 0.306 ± 0.021 | 0.692 ± 0.021 | 0.548 ± 0.022 | 0.504 | 18.14 | 31 |
| base-tiny-90m | - | float16 | 0.358 ± 0.021 | 0.448 ± 0.022 | 0.484 ± 0.022 | 0.274 ± 0.020 | 0.670 ± 0.021 | 0.530 ± 0.022 | 0.461 | 39.32 | 11 |
| leaf-s1-e4-decay10 | 1535.1M | float16 | 0.300 ± 0.021 | 0.406 ± 0.022 | 0.414 ± 0.022 | 0.210 ± 0.018 | 0.580 ± 0.022 | 0.514 ± 0.022 | 0.404 | 59.08 | 11 |

Deltas against the same-family base (z = Δ / √(se²+se²); limit 500 docs/task):

| checkpoint | vs | lambada_openai | hellaswag | arc_easy | arc_challenge | piqa | winogrande | mean Δ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| room05b-e1-decay10 | base-0.5b | - | - | - | - | - | - | - |
| room05b-e2-v3-decay10 | base-0.5b | - | - | - | - | - | - | - |
| room05b-e2-v4-decay10 | base-0.5b | - | - | - | - | - | - | - |
| leaf-s1-e4-decay10 | base-tiny-90m | -0.058 (z -2.0) | -0.042 (z -1.3) | -0.070 (z -2.2) | -0.064 (z -2.4) | -0.090 (z -2.9) | -0.016 (z -0.5) | -0.057 |
