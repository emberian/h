# Qwen3.8-27B library adapter: the recipe as reported, not assumed (2026-09-03)

Sources read: Unsloth's Qwen3.8 fine-tuning guide (unsloth.ai/docs/models/qwen3.8/train), Unsloth's continued-pretraining doc
(unsloth.ai/docs/basics/continued-pretraining), the Hugging Face forum thread on fine-tuning Qwen3.5-4B-Base on raw novel text
without a chat format (discuss.huggingface.co/t/.../179431), the r/LocalLLaMA "Findings from LoRA finetuning for Qwen3" thread
(rank 8 best in that study), the Qwen3-8B thinking-loss thread (empty `<think>` blocks in the template), the official
Qwen/Qwen3.8-27B model card, and the mlx-community/Qwen3.8-27B-4bit card (converted with mlx-vlm 0.6.8).

Model: causal LM with a vision encoder; 64 layers, 16 x (3 x (Gated DeltaNet -> FFN) -> 1 x (Gated Attention -> FFN));
thinking on by default in the chat template; 262K context. The base checkpoint is gated (application pending); the instruct
weights are used for plumbing only.

Quantization: use community quantizations, never our own. mlx-community/Qwen3.8-27B-4bit (mlx-vlm), or
unsloth/Qwen3.8-27B-unsloth-bnb-4bit on CUDA.

Recipe (raw-text continued pretraining through an adapter):
- Objective: plain causal LM on raw library text, no chat template ever rendered, EOS between documents.
- LoRA r=16, alpha=16, dropout 0, all linear projections in the language blocks (attention q/k/v/o, Gated DeltaNet projections,
  MLP gate/up/down); vision layers frozen. On CUDA with memory, add lm_head and embed_tokens with an embedding LR 2-10x smaller
  (Unsloth: 5e-6 against 5e-5).
- LR 5e-5 (Unsloth's continued-pretraining setting; 2e-4 is their instruction-SFT setting), warmup ~3% (>= 10 steps), decay to 10%.
- Sequence 2048, batch 1 x grad-accum 4, gradient checkpointing.
- Community results: rank 8 beat 16/32 in one Qwen3 8B study; rank 32 -> 64 did not help raw-text CPT on Qwen3.5-4B; data quantity
  and duration matter more than rank.
- Evaluation before any sweep (forum advice): book-level held-out documents, identical raw-prefix generations base vs adapter,
  explicit document-boundary choice; only then rank/LR/epoch ablations.
- Pitfall: Qwen3's chat template renders non-thinking turns with an empty `<think>` block; SFT through the template can lose
  thinking mode. Raw-text training avoids the template entirely; at inference use raw prompts for the room.

Resources: no local CUDA GPU with 24+ GB (hbox is a 12 GB Radeon). Local path: MLX on the 103 GB Mac if mlx_lm/mlx_vlm supports
this architecture's LoRA; otherwise a rented 24-40 GB GPU with Unsloth (a few dollars per hour).
