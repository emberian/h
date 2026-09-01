# Falcon-H1 in JAX

This is a functional JAX implementation of the complete Falcon-H1 hybrid
decoder plus a single-host, eight-device data-parallel trainer for Kaggle TPU
v5e-8. Parameter keys and tensor layouts remain identical to Hugging Face
safetensors. The trainer keeps FP32 master weights, uses BF16 compute, averages
gradients across TPU devices, supports microbatch accumulation/rematerialization,
and saves resumable optimizer state with HF-loadable weights.

The implementation is not a loose H1-like model. It includes GQA causal
attention, non-interleaved RoPE, the causal depthwise convolution, chunked
Mamba-2 SSD, all Falcon-H1 muP multipliers, parallel attention/SSM residuals,
SwiGLU MLPs, tied or untied embeddings/heads, and the scaled language-model
head. Attention projection width may differ from residual width, as it does in
the official 0.5B checkpoint.

## Verification performed

- Chunked SSD agrees with a token-by-token recurrent SSM at `2e-5` tolerance.
- Tiny forward, causal loss, backward gradient, AdamW updates, atomic
  safetensors checkpoints, tokenizer packaging, and optimizer resume run end to
  end, including an eight-device simulated CPU run.
- The published 91,131,072-parameter `Falcon-H1-Tiny-90M-Base` checkpoint agrees
  with eager Transformers float32 over a 129-token input that crosses the
  Mamba chunk boundary (4,227,072 logits): maximum absolute error
  `1.2016296e-4`, mean absolute error `5.0071e-6`.
- The full 91M BF16/rematerialized backward graph traces successfully at the
  production `[1, 513]` microbatch shape, producing gradients for all 386
  checkpoint tensors.
- The published 521,411,104-parameter `Falcon-H1-0.5B-Base` checkpoint agrees
  with eager Transformers float32 over a 15-token input (491,760 logits):
  maximum absolute error `6.67572e-5`, mean absolute error `7.56471e-6`. See
  `falcon_h1_0_5b_preflight.json` for the pinned revision and file hashes.

Run the local tests:

```bash
uv venv --python 3.12 .venv-jax
uv pip install --python .venv-jax/bin/python -e 'jax_training[test]'
JAX_PLATFORM_NAME=cpu .venv-jax/bin/pytest -q jax_training/tests
```

Create a PyTorch reference and repeat full-checkpoint parity:

```bash
/path/to/transformers/python jax_training/torch_reference.py \
  --checkpoint /path/to/Falcon-H1-Tiny-90M-Base \
  --tokens /tmp/parity-tokens.npy --output /tmp/reference.npz

JAX_PLATFORM_NAME=cpu .venv-jax/bin/h1jax-parity \
  --checkpoint /path/to/Falcon-H1-Tiny-90M-Base \
  --tokens /tmp/parity-tokens.npy --reference /tmp/reference.npz
```

## Train

Continued pretraining keeps the stock tokenizer and starts from the HF
checkpoint:

```bash
h1jax-train \
  --config /kaggle/input/hghost-base/config.json \
  --checkpoint /kaggle/input/hghost-base \
  --train-bin /kaggle/input/hghost-corpus/train.bin \
  --validation-bin /kaggle/input/hghost-corpus/validation.bin \
  --output /kaggle/working/h1-cpt \
  --sequence-length 512 --per-device-batch 1 --accumulation-steps 2 \
  --total-tokens 300000000 --warmup-tokens 3000000 --learning-rate 1e-4 \
  --save-tokens 10000000,30000000,100000000,300000000
```

For a born model, point `--config` at a corpus-tokenizer-specific config and
replace `--checkpoint ...` with `--random-init`. `born_10m_config()` is 9,856,488
parameters at an 8,192-token vocabulary; `born_20m_config()` is 20,167,350 at a
10,240-token vocabulary.

The token files are raw little-endian uint16 streams. Every training example is
`sequence_length + 1` tokens, and the loader traverses all aligned sequences in
a deterministic permutation before repeating.

## Kaggle CLI loop

The checked-in `kaggle/` folders are private-dataset/kernel bundles. The local
access token is used only by the CLI and is never copied into either bundle.

```bash
uvx --from kaggle kaggle datasets create -p kaggle/code_dataset
uvx --from kaggle kaggle kernels push -p kaggle/tpu_smoke
uvx --from kaggle kaggle kernels status emberian64/h-ghost-jax-tpu-smoke
uvx --from kaggle kaggle kernels output emberian64/h-ghost-jax-tpu-smoke \
  -p artifacts/kaggle-smoke-output
```
