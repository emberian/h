# Qwen3.8-27B library adapter: plumbing status (2026-09-03)

Recipe and sources: see RECIPE.md. Model: mlx-community/Qwen3.8-27B-4bit (community quantization, mlx-vlm 0.6.8),
15 GB at artifacts/models/qwen3.8-27b-mlx-4bit. Data: qwen/data/{train,valid}.jsonl, 3,000 + 100 chunks of ~2,048
tokens of raw library text (no chat template). LoRA config: qwen/lora.yaml (r=16, scale 1.0, all language-block
projections: self_attn q/k/v/o, linear_attn in_proj_qkv/z/a/b + out_proj, mlp gate/up/down).

What works on the Mac (103 GB unified memory, mlx-lm 0.32.0):
- `mlx_lm generate --model artifacts/models/qwen3.8-27b-mlx-4bit --prompt ... --max-tokens 60`: 8.3 tokens/s generation,
  17 tokens/s prompt, 15.5 GB peak. Note: mlx_lm.generate applies the chat template by default (the model narrates
  "The user provided a short phrase..."); for room-style raw prompts pass --ignore-chat-template.
- The model loads for LoRA (model_type qwen3_5 / qwen3_5_text); trainable parameters 0.43% with adapters on all 64 layers.

What does not work on the Mac, and why:
- Adapters on all 64 layers: `[metal::malloc] Resource limit (499000) exceeded` (Metal live-buffer cap).
- Adapters on 32 or 16 layers, seq 2048 or 1024, with or without the OCR server on the GPU: the first training step is
  killed with `Command buffer execution failed: Impacting Interactivity`. This is ml-explore/mlx issue #3267: the
  macOS Metal watchdog kills GPU work that blocks WindowServer compositing while the display is active; reported 100%
  reproducible with the display on and 100% avoidable with the display asleep (`pmset displaysleepnow`, keep the
  machine awake with `caffeinate -s`). On M5 Max machines the same condition escalated to a watchdog kernel panic and
  hard reboot even with `AGX_RELAX_CDM_CTXSTORE_TIMEOUT=1`.
- A separate open issue, ml-explore/mlx-lm #1206, reports Qwen3.5-family LoRA crashing at the first backward pass with a
  Metal OOM on some chips (M5 Max, M3 Pro) but not others; it may or may not apply here once the watchdog is out of the way.

Decision: do not train the 27B on this Mac while it hosts the resident's servers; a display-off overnight run is possible
but carries the documented reboot risk. The reported training path is Unsloth on a CUDA GPU with >= 24-40 GB
(unsloth/Qwen3.8-27B-unsloth-bnb-4bit, r=16, alpha 16, LR 5e-5 for raw text, seq 2048), a few dollars per hour rented.
Serving the 27B locally for reading (8 tokens/s) is fine.
