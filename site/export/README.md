# site/export — Falcon-H1 checkpoints → ONNX for the in-browser ghost

`export_onnx.py` turns a Hugging Face Falcon-H1 checkpoint directory (`config.json`,
`model.safetensors` in fp32 or bf16, tokenizer files) into the directory layout that
transformers.js 4.2.0 loads for a `falcon_h1` text-generation model, and proves the result
against PyTorch with onnxruntime before it is used.

```
site/models/<name>/
  config.json                 + "transformers.js_config": {"use_external_data_format": true}
  generation_config.json  tokenizer.json  tokenizer_config.json  special_tokens_map.json
  onnx/model.onnx      + model.onnx_data       fp32   (dtype: "fp32")
  onnx/model_q4.onnx   + model_q4.onnx_data    4-bit, the Hub recipe (dtype: "q4") — unusable for this checkpoint, see Results
  onnx/model_quantized.onnx + _data            8-bit (dtype: "q8", what the site uses)
  export_report.json                           parity, timings, sizes, library versions
```

## Export a checkpoint

```sh
# one-time: an isolated venv (do not reuse the training venvs)
uv venv --python 3.12 .venv-onnx
uv pip install --python .venv-onnx/bin/python -r site/export/requirements.txt

# export + verify (CPU only; a few minutes)
.venv-onnx/bin/python site/export/export_onnx.py <hf checkpoint dir> site/models/<name>
```

Options: `--no-q4` / `--no-q8` (skip a quantized file), `--q8-embedding q8|q4|fp16|fp32`,
`--q8-block-size 32`, `--q8-accuracy-level 4` (int8 activations: much faster on CPU/WASM, see
Results), `--q4-block-size`, `--q4-symmetric`, `--q4-accuracy-level`, `--no-q4-embedding`,
`--no-slim`, `--no-verify`, `--prompt`, `--new-tokens`, `--opset` (18), `--threads`.

Then point the site at it in `site/config.js`: `model.id = "<name>"`, `model.localPath =
"./models/"`, `model.dtype = "q8"` (see the site README, "Loading the project's own
checkpoint"). `site/models/` is gitignored; deploy the directory next to the site.

## What the exporter does

1. Loads `FalconH1ForCausalLM` in fp32 on CPU (transformers 4.57.6 — the version the
   checkpoint's `config.json` was written by; bf16 weights are upcast).
2. Rebuilds the forward pass in `FalconH1Onnx`, a small `nn.Module` whose interface is the
   flat ONNX one transformers.js feeds (`packages/transformers/src/configs.js#getCacheNames`,
   `models/modeling_utils.js#addPastKeyValues/decoder_forward` in the pinned clone):

   | input | shape | | output | shape |
   |---|---|---|---|---|
   | `input_ids` | `[B, L]` int64 | | `logits` | `[B, keep, vocab]` |
   | `attention_mask` | `[B, T]` int64, T = past + L | | `present.{i}.key/value` | `[B, kv_heads, T, head_dim]` |
   | `num_logits_to_keep` | `[]` int64, 0 = all | | `present_conv.{i}` | `[B, conv_dim, d_conv]` |
   | `past_key_values.{i}.key/value` | `[B, kv_heads, past, head_dim]` | | `present_ssm.{i}` | `[B, n_heads, d_head, d_state]` |
   | `past_conv.{i}` | `[B, conv_dim, d_conv]` | | | |
   | `past_ssm.{i}` | `[B, n_heads, d_head, d_state]` | | | |

   This is exactly the interface of `onnx-community/Falcon-H1-Tiny-Multilingual-100M-Instruct-ONNX`
   (graphs downloaded to `reference/` for comparison; that export is a hand-built graph with
   `GroupQueryAttention`/`If` contrib ops, not something a stock exporter produces, and neither
   `optimum` 2.x nor `optimum-onnx` 0.1.0 has a `falcon_h1` config).
   transformers.js zero-fills every `past_*` input from the session's input metadata (symbolic
   dims resolve to 0, so the first call has `past = 0`), reads the sequence length from
   `present.{i}.key`, renames `present*` → `past*`, and passes `num_logits_to_keep = 1` while
   generating. It does not create `position_ids`; positions come from the mask inside the graph.
3. One graph covers prefill, decode and continued prefill: the Mamba-2 scan is the SSD closed
   form over the whole incoming chunk with `past_ssm` as the initial state (segment sums computed
   the way `modeling_falcon_h1.py` does, so the numbers match its chunked scan to fp32 rounding),
   and the depthwise causal conv reads its window from `past_conv` (four shifted multiplies,
   no `Conv`). Attention is plain `MatMul`/`Softmax` with an additive mask built from
   `attention_mask` (left padding safe); RoPE is computed in-graph from mask-cumsum positions.
   Every MuP multiplier (`attention_in/out`, `key`, `ssm_in/out`, `mlp_multipliers`, the
   `mup_vector` on `in_proj`) is folded into the weights; `embedding_multiplier` and
   `lm_head_multiplier` stay as scalar `Mul`s because the two share one tensor.
   Only standard ONNX ops are emitted (`Softplus` is spelled with `Relu`/`Exp`/`Log`), so both
   the WebGPU and WASM backends of onnxruntime-web run it.
4. `torch.onnx.export` (TorchScript tracer, `dynamo=False`, opset 17, cyclic GC paused — with
   it enabled the tracer spends its time in `gc_collect_main`), then `onnxslim`.
5. q4: `onnxruntime.quantization.matmul_nbits_quantizer.MatMulNBitsQuantizer(bits=4,
   block_size=32, is_symmetric=False, accuracy_level=None, op_types_to_quantize=("MatMul",
   "Gather"))` — the same recipe as the Hub q4 (every `MatMul` → `MatMulNBits` with zero
   points, the embedding `Gather` → `GatherBlockQuantized`). This is what the transformers.js
   `scripts/quantize.py` (last shipped in 3.8.1, copied to `scripts-3.8.1/`) calls, minus the
   embedding step that the 3.x script lacks and the Hub files have. The quantizer forces the
   graph to opset 21 (int4 tensor types), which is why the export uses opset 18 and not 17:
   at 17 `ReduceMean` carries `axes` as an attribute and the bumped graph does not load.
   q8: the same quantizer with `bits=8` on the MatMuls, plus an 8-bit `GatherBlockQuantized`
   for the embedding built by hand (`quantize_embedding_8bit`; the Python quantizer only
   emits the 4-bit form, the kernels in the bundled onnxruntime-web accept both).
6. fp32: the tied `lm_head` weight is written once (a `Transpose` of the embedding) instead of
   twice. All files are saved with a single external `_data` file (written by the script
   itself: `onnx.save_model(save_as_external_data=True)` wrote this graph's tensors twice, and
   ORT needs the tiny `Slice` constants inline), which the `use_external_data_format` flag in
   `config.json` tells transformers.js to fetch.
7. Verification against PyTorch with onnxruntime (CPU EP): full-prompt logits at every
   position, the same prompt prefilled in two chunks (exercises the incoming-state path), the
   cache from both, a left-padded batch of two, greedy generation token-for-token through the
   with-past loop versus `generate(do_sample=False)`, and the q4 model's logits and greedy
   text. Numbers land in `export_report.json`.

## Results for the base checkpoint

Checkpoint: `kaggle/base_model_dataset_public` = `tiiuae/Falcon-H1-Tiny-90M-Base` (91,131,072
parameters, bf16 safetensors upcast to fp32). Exported 2026-09-01 on an Apple-silicon Mac that was
running an OCR job and ~200 other processes (load average 130-230, 0 % idle), so every timing
below is pessimistic; the same run took 12.9 s / 21.9 s / 6.9 s for export / slim / q4 in a
quieter moment.

```
.venv-onnx/bin/python site/export/export_onnx.py kaggle/base_model_dataset_public site/models/h1-tiny-90m-base
# torch.onnx.export 59.8 s (9664 nodes) → onnxslim 137 s (4184 nodes) → q4 23 s → q8 11 s → verify ≈ 1.5 min; 310 s total
```

| file | bytes | what |
|---|---|---|
| `onnx/model.onnx` + `model.onnx_data` | 1,215,426 + 364,517,376 | fp32, opset 18, 36 op types, all standard |
| `onnx/model_q4.onnx` + `_data` | 1,294,600 + 69,573,120 | 4-bit MatMulNBits (217) + 4-bit GatherBlockQuantized, block 32, zero points, opset 21 |
| `onnx/model_quantized.onnx` + `_data` | 1,300,397 + 125,144,064 | 8-bit MatMulNBits (217) + 8-bit GatherBlockQuantized, block 32, zero points |

Parity against PyTorch (transformers 4.57.6, fp32, CPU — bit-identical to the project's stored
`kaggle/base_model_dataset_public/h1jax-torch-reference*.npz` logits, max abs 0.0), on a 39-token
prompt, logits at every position:

| file | max abs logit error | mean abs | mean KL (nats) | argmax agreement | greedy 20 tokens vs PyTorch |
|---|---|---|---|---|---|
| fp32 | 1.26e-4 | 1.17e-5 | 0 | 1.000 | identical |
| q4 | 23.5 | 1.66 | 0.61 | 0.667 | diverges after 3 |
| q8 | 0.98 | 0.084 | 0.0014 | 1.000 | diverges after 5 (both texts coherent) |

fp32 also matches when the prompt is prefilled in two chunks of 19 + 20 (max abs 9.5e-5; the
caches from the split and the one-shot prefill agree to 1.6e-4) and in a left-padded batch of two
(padded row max abs 1.2e-4). Greedy text, fp32/PyTorch: `' is often used to indicate the end of a
sentence.\n\nThe word "hope" is'`; q8: `' is often used to indicate a pause or pause in
speech.\n\n---\n\n### Intermediate Questions\n\n'`; q4: `' is often used in the context of the
word (@) to refer to a person or thing that'`.

CPU speed (onnxruntime 1.29, CPU EP, that loaded machine): fp32 prefill 355 ms, decode 70 ms per
token; q4 603 / 137; q8 1514 / 1094. The plain 8-bit MatMulNBits CPU kernel is unvectorized;
`--q8-accuracy-level 4` (int8 activations) brings it to 148 ms per token at KL 0.0064, but it also
steers the WebGPU EP onto its DP4A / subgroup-matrix kernels, which were not tested here, so it is
off by default. On WebGPU the default MatMulNBits shader is used either way.

**Why the site uses q8 and not the Hub's q4 recipe.** Round-to-nearest 4-bit wrecks this checkpoint,
and not because of one layer: on 48 tokens, 4-bit on *only* `in_proj` costs 0.048 nats, only the
attention projections 0.082, only `out_proj` 0.141, only `gate/up` 0.110, only `down` 0.112, only
`lm_head` 0.049, only the embedding 0.017 — all together 0.46-0.61. Block 128 and symmetric
quantization do not help; an fp32 graph loaded with the *same* dequantized weights reproduces the
MatMulNBits numbers exactly, so the kernel is fine and the loss is intrinsic (mean relative weight
error 9.6 %). 8-bit everywhere is 0.002 nats. The Hub's `Falcon-H1-Tiny-Multilingual-100M-Instruct`
q4 was made with this same recipe, which would explain the site's previously recorded fragments.

**Why the embedding is an 8-bit GatherBlockQuantized and not fp16.** An fp16 table with a `Cast`
after the `Gather` (139 MB) loaded on WebGPU but every generation failed with `Program Gather
requires f16 but the device does not support it` — the headless SwiftShader adapter has no
`shader-f16`, and neither do some real ones. The 8-bit op needs nothing optional and is smaller.

## Browser check

```sh
cd site && python3 -m http.server 8765 &          # any static server; 8000 was taken here
NODE_PATH=/opt/homebrew/lib/node_modules/playwriter/node_modules \
  node export/check_site.mjs http://localhost:8765/ 900
```

`check_site.mjs` drives headless Chromium (playwright-core 1.58, Chromium 1223 from the
playwright cache, `--enable-unsafe-webgpu`) with the page as-is, taps the ghost worker's
messages, and exits 0 only when the model reported ready and murmured with no console errors,
page errors, or failed requests.

Result, 2026-09-01, `config.js` as now committed (`localPath: "./models/"`, `id:
"h1-tiny-90m-base"`, `dtype: "q8"`): device **webgpu**; fetched `config.json`, `tokenizer.json`,
`tokenizer_config.json`, `generation_config.json`, `onnx/model_quantized.onnx`,
`onnx/model_quantized.onnx_data` from the local server; **0 console errors, 0 page errors, 0 failed
requests**; the ghost murmured `" winter 04, 2015\nGermany and Sweden are the first two"`. The run
hit its 900 s cap before a second fragment — SwiftShader WebGPU on a box at load average 200 makes a
token every few seconds — and exited 0. With the model files absent the same harness reports the
404s and exits 1, so a pass means the local files were really used.

## Files

- `export_onnx.py` — the exporter + verifier (this document's subject).
- `check_site.mjs` — headless browser check.
- `requirements.txt` — exact versions.
- `transformers.js/` (gitignored) — shallow clone of huggingface/transformers.js, commit
  `bf27627c` (2026-08-29), read for what the JS runtime expects; tag `3.8.1` fetched for the
  old Python scripts (`scripts-3.8.1/`, gitignored).
- `reference/` (gitignored) — `config.json` and the weightless `onnx/model.onnx`,
  `onnx/model_q4.onnx` graphs of the Hub export, for interface comparison.
