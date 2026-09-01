# Falcon-H1 0.5B TPU gate

This public Kaggle script loads the pinned official 521,411,104-parameter base
checkpoint and the sealed corpus-v1 token stream. It requires a TPU v5e-8,
replicates the complete model across all eight devices, and performs exactly two
BF16/rematerialized full-model optimizer updates at sequence length 512.

The kernel refuses to run on CPU/GPU or with an unexpected device count,
checkpoint, or shape. It saves no large checkpoint. Success is the marker:

```text
TPU_V5E8_FALCON_H1_05B_SMOKE_OK
```
