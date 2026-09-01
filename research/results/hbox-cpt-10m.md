# H1-Tiny hbox CPT at 10M tokens

Date: 2026-09-01

The hbox full-weight run was interrupted after its first durable checkpoint. The process had reached about
11.1M exposed tokens; this report evaluates the checkpoint saved at exactly 10,000,384 batch-aligned tokens.

## Reproducibility

| Artifact | SHA-256 |
|---|---|
| Base `model.safetensors` | `ee1d547c2d78df42a52afd55b23459301ca21126851b82e0900f1e313dbcf5ef` |
| 10M `model.safetensors` | `752d368a897c5cc537ec3655f158dc3372a311e373433158cdfd9d9784ee9ec0` |
| corpus-v1 `validation.bin` | `07bce22a3de6101d4d946d1592a500c30a3790afffdecb8da6bd99777b985928` |

The comparison used the first 32 contiguous 512-token validation examples: 16,384 predicted tokens. Both
models ran through Transformers 4.57.1 in BF16 on hbox's ROCm 6.3 PyTorch build. Sampling used identical
per-prompt seeds, temperature 0.8, top-p 0.95, repetition penalty 1.08, and 128 generated tokens.

## Held-out change

| Model | Loss | Perplexity | Accuracy |
|---|---:|---:|---:|
| untouched base | 3.745613 | 42.3349 | 34.9426% |
| CPT at 10M | 3.615983 | 37.1879 | 36.7615% |

After only 2.67% of one corpus pass, held-out loss improved by 0.129629 (3.46%), perplexity fell by 12.16%,
and next-token accuracy rose by 1.82 percentage points. This is a small fixed validation slice and is not a
replacement for the work-family-disjoint evaluation set, but the behavioral shift is not subtle.

## Generation change

The untouched base strongly defaults to generic explanatory/assistant prose. For `The relation between
thought and language`, it produced a conclusion about “linguistic theories,” “cognitive psychology,” and
“language teaching.”

The 10M checkpoint instead began:

> is the same. That is the same in terms of how a thought which can explain a linguistic process of its own
> is in fact just as a thought which...

For `In the beginning was neither being nor nothing, but`, the base produced loose conversational prose
about the world, beauty, comfort, and pain. The checkpoint produced a recursive distinction among the self,
things, actuality, being, and non-being.

The result is already more library-like, but not simply better. It repeats clauses and readily reproduces
page furniture. `Consciousness is not an object because` collapsed into a citation followed by page numbers;
the validation-prefix prompt repeated contributor names and emitted a form-feed marker. This is direct
evidence that header/footer/page-number cleanup and a repetition/memorization suite are quality work, not
cosmetics.

## BF16 update-resolution failure

Although every parameter participated in autograd, the model parameters and both AdamW moments were stored in
BF16. The checkpoint's optimizer contains 91,131,072 BF16 first moments and 91,131,072 BF16 second moments.

| Parameter family | Elements | Fraction changed | Delta RMS / base RMS |
|---|---:|---:|---:|
| embedding/head | 16,777,216 | 7.76% | 2.23% |
| norms | 25,088 | **0.00%** | **0.00%** |
| attention Q/K | 7,864,320 | 41.48% | 4.03% |
| attention V/O | 7,864,320 | 63.20% | 3.40% |
| MLP | 28,311,552 | 41.03% | 2.50% |
| Mamba input projection | 20,742,144 | 76.22% | 9.47% |
| Mamba output projection | 9,437,184 | 82.48% | 15.16% |
| Mamba convolution | 107,520 | 9.58% | 0.061% |
| Mamba dynamics (`A_log`, `D`, `dt_bias`) | 1,728 | 0.75% | 0.0058% |

This means the run was full-weight in the requires-gradient sense but not in update resolution. Norms were
bit-identical after 10M tokens, and most embedding, convolution, and recurrent-dynamics values could not
cross a BF16 quantization boundary. Future CPT should use BF16 compute with FP32 master parameters and AdamW
moments. This is particularly important for the scale-sensitive recurrent dynamics.

## Why hbox was slow

The environment had neither `mamba_ssm` nor `causal_conv1d`. Transformers printed the definitive warning:

```text
The fast path is not available because one of
(selective_state_update, causal_conv1d_fn, causal_conv1d_update) is None.
Falling back to the naive implementation.
```

That fallback materializes the chunked SSD calculation through ordinary PyTorch operations. Full training
held about 489 tokens/s at batch 1, sequence 512, and four gradient-accumulation microbatches. The correct
fix is an independently validated Mamba-2 SSD kernel path, not merely a larger batch around the naive graph.

The reusable comparison command is implemented in
[`hbox_training/compare_checkpoints.py`](../../hbox_training/compare_checkpoints.py).
