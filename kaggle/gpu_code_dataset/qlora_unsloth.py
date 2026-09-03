#!/usr/bin/env python3
"""QLoRA library adapter for a Qwen3.5-family hybrid (Gated DeltaNet + attention) model on one GPU.

The recipe is qwen/RECIPE.md and qwen/lora.yaml as corrected on 2026-09-03: plain causal LM on raw
library text (no chat template; EOS only where a document really ends), LoRA r=16, alpha=16, dropout 0
on the attention projections (self_attn q/k/v/o) and the MLP projections (gate/up/down) ONLY, never on
the Gated DeltaNet projections (linear_attn in_proj_*/out_proj: arXiv 2604.22127), LR 5e-5 with a short
warmup and a linear decay to 10% of peak, sequence 2048, batch 1 x accumulation 4, gradient
checkpointing, 4-bit NF4 base weights (bitsandbytes), book-level held-out validation chunks.

Data: <data dir>/train.jsonl and valid.jsonl with {"text": ...} chunks (qwen/scripts/build_data.py cut
them to 2048 tokens; a chunk shorter than the window is a real document end). Each chunk is tokenized
without special tokens, EOS is appended, and the sequence is truncated to --seq tokens: mid-book chunks
lose the EOS again (no fake boundary), document tails keep it (mlx-lm's semantics, so the Mac and the
GPU runs see the same targets).

Backends: `--backend peft` is transformers + peft + bitsandbytes (the path proven on the Kaggle T4);
`--backend unsloth` loads through Unsloth's FastLanguageModel (faster kernels on Ampere+; unverified on
our side) and then runs the same training loop. Both write a PEFT adapter (adapter_config.json +
adapter_model.safetensors) under <output>/adapter/.

Merging: the adapter is NOT merged by default. Serving loads base + adapter (transformers/peft, or
mlx-lm after `mlx_lm.convert`/adapter conversion). `--merge` additionally reloads the base in 16-bit,
merges the adapter (peft merge_and_unload) and writes <output>/merged/ as HF safetensors; that needs the
16-bit base in memory (the 27B: 55 GB) and is what to do if a standalone checkpoint is wanted for
`mlx_lm.convert -q`. The validation loss of the merged model is reported next to the adapter's so the
quantization mismatch (adapter trained against NF4 weights, merged into bf16) is a number, not a guess.

Events: JSON lines on stdout and in <output>/events.jsonl ({"event": "train"|"validation"|"adapter"|...}).

    # H100 (recipe defaults; one epoch of qwen/data):
    python gpu/qlora_unsloth.py --model Qwen/Qwen3.8-27B --data-dir qwen/data --output /data/runs/qwen38-27b-lib-r16
    # T4 test: --tiny (Qwen/Qwen3.5-2B-Base, 30 steps, fp32 compute because the GDN layers NaN in fp16)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import threading
import time
from pathlib import Path

RECIPE = {
    "rank": 16,
    "alpha": 16.0,
    "dropout": 0.0,
    "lr": 5e-5,
    "warmup_frac": 0.03,
    "warmup_min_steps": 10,
    "final_lr_frac": 0.10,
    "weight_decay": 0.01,
    "grad_clip": 1.0,
    "seq": 2048,
    "batch": 1,
    "accum": 4,
    "epochs": 1.0,
    "max_steps": 0,
    "eval_every": 0,  # 0 = ten evaluations per run
    "valid_chunks": 0,  # 0 = all
    "log_every": 10,
    "max_minutes": 0.0,
    "stall_minutes": 20.0,
}
TINY = {
    **RECIPE,
    "max_steps": 30,
    "eval_every": 10,
    "valid_chunks": 16,
    "log_every": 5,
    "max_minutes": 30.0,
    "stall_minutes": 15.0,
}
TARGET_PATTERN = re.compile(r"\.self_attn\.(q|k|v|o)_proj$|\.mlp\.(gate|up|down)_proj$")
EXCLUDE_PATTERN = re.compile(r"visual|vision|linear_attn|mtp")

STARTED = time.time()
_EVENT_LOG: Path | None = None


def emit(event: str, **values) -> None:
    record = {"event": event, "elapsed_minutes": round((time.time() - STARTED) / 60, 3), **values}
    line = json.dumps(record, default=str)
    print(line, flush=True)
    if _EVENT_LOG is not None:
        with _EVENT_LOG.open("a") as handle:
            handle.write(line + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True, help="Hub id or local directory of the base model")
    parser.add_argument("--data-dir", type=Path, required=True, help="directory with train.jsonl and valid.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=("peft", "unsloth"), default="peft")
    parser.add_argument("--tiny", action="store_true", help="30-step test settings (see TINY)")
    parser.add_argument("--rank", type=int)
    parser.add_argument("--alpha", type=float)
    parser.add_argument("--dropout", type=float)
    parser.add_argument("--lr", type=float)
    parser.add_argument("--warmup-frac", type=float)
    parser.add_argument("--warmup-min-steps", type=int)
    parser.add_argument("--final-lr-frac", type=float)
    parser.add_argument("--weight-decay", type=float)
    parser.add_argument("--grad-clip", type=float)
    parser.add_argument("--seq", type=int)
    parser.add_argument("--batch", type=int)
    parser.add_argument("--accum", type=int)
    parser.add_argument("--epochs", type=float)
    parser.add_argument("--max-steps", type=int, help="stop after this many optimizer steps (0 = epochs)")
    parser.add_argument("--eval-every", type=int, help="optimizer steps between validations (0 = ten per run)")
    parser.add_argument("--valid-chunks", type=int, help="validation chunks to use (0 = all)")
    parser.add_argument("--log-every", type=int)
    parser.add_argument("--max-minutes", type=float, help="wall-clock budget: save the adapter and exit")
    parser.add_argument("--stall-minutes", type=float, help="exit 3 if no optimizer step completes within this bound")
    parser.add_argument("--loss-chunk", type=int, default=512, help="positions per lm_head + cross-entropy chunk (memory)")
    parser.add_argument("--compute-dtype", choices=("auto", "bf16", "fp16", "fp32"), default="auto",
                        help="auto = bf16 where supported, else fp32 (Qwen3.5 GDN layers produce NaN gradients in fp16)")
    parser.add_argument("--no-4bit", action="store_true", help="load the base in 16-bit instead of NF4 (LoRA, not QLoRA)")
    parser.add_argument("--train-embeddings", action="store_true",
                        help="also train lm_head and embed_tokens in full at --embedding-lr (Unsloth CPT variant; off = recipe)")
    parser.add_argument("--embedding-lr", type=float, default=5e-6)
    parser.add_argument("--merge", action="store_true", help="after training, merge into the 16-bit base and write <output>/merged/")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()
    preset = TINY if args.tiny else RECIPE
    for key, value in preset.items():
        if getattr(args, key) is None:
            setattr(args, key, value)
    return args


# ------------------------------------------------------------------------------------------- data
def load_chunks(path: Path, tokenizer, seq: int, limit: int = 0) -> list[list[int]]:
    """Token id lists (EOS appended, truncated to seq) for the {"text": ...} rows of a JSONL file."""

    rows = [json.loads(line)["text"] for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if limit:
        rows = rows[:limit]
    eos = tokenizer.eos_token_id
    if eos is None:
        raise SystemExit("tokenizer has no EOS token")
    out = []
    kept_eos = 0
    for begin in range(0, len(rows), 256):
        encoded = tokenizer(rows[begin : begin + 256], add_special_tokens=False)["input_ids"]
        for ids in encoded:
            ids = ids + [eos]
            if len(ids) <= seq:
                kept_eos += 1
            out.append(ids[:seq])
    emit("data", path=str(path), chunks=len(out), tokens=sum(len(x) for x in out), chunks_ending_with_eos=kept_eos,
         mean_tokens=round(sum(len(x) for x in out) / max(1, len(out)), 1))
    return out


def collate(chunks: list[list[int]], device, pad_id: int):
    import torch

    width = max(len(c) for c in chunks)
    input_ids = torch.full((len(chunks), width), pad_id, dtype=torch.long)
    labels = torch.full((len(chunks), width), -100, dtype=torch.long)
    attention = torch.zeros((len(chunks), width), dtype=torch.long)
    for row, ids in enumerate(chunks):
        input_ids[row, : len(ids)] = torch.tensor(ids)
        labels[row, : len(ids)] = torch.tensor(ids)
        attention[row, : len(ids)] = 1
    return input_ids.to(device), labels.to(device), attention.to(device)


def _chunk_loss(lm_head, hidden, labels):
    import torch

    logits = lm_head(hidden).float()
    return torch.nn.functional.cross_entropy(logits.reshape(-1, logits.shape[-1]), labels.reshape(-1), ignore_index=-100,
                                             reduction="sum")


def lm_loss(model, input_ids, attention_mask, labels, chunk: int, checkpoint: bool):
    """Summed next-token cross-entropy and the token count, with the lm_head + softmax evaluated per `chunk`
    positions (recomputed in the backward when `checkpoint`), so the [seq, vocab] fp32 logits of a 248k-vocab
    model never exist all at once (that is 2 GB per copy at 2048 tokens; the T4 test OOMed on it)."""

    import torch

    base = model.get_base_model() if hasattr(model, "get_base_model") else model
    hidden = base.model(input_ids=input_ids, attention_mask=attention_mask, use_cache=False).last_hidden_state
    shift_hidden, shift_labels = hidden[:, :-1], labels[:, 1:]
    count = int((shift_labels != -100).sum())
    total = torch.zeros((), dtype=torch.float32, device=hidden.device)
    for start in range(0, shift_hidden.shape[1], chunk):
        h, y = shift_hidden[:, start : start + chunk], shift_labels[:, start : start + chunk]
        if checkpoint:
            total = total + torch.utils.checkpoint.checkpoint(_chunk_loss, base.lm_head, h, y, use_reentrant=False)
        else:
            total = total + _chunk_loss(base.lm_head, h, y)
    return total, count


# ------------------------------------------------------------------------------------------ model
def lora_targets(model) -> list[str]:
    import torch

    names = []
    for name, module in model.named_modules():
        if TARGET_PATTERN.search(name) and not EXCLUDE_PATTERN.search(name) and (
            isinstance(module, torch.nn.Linear) or type(module).__name__.startswith("Linear")
        ):
            names.append(name)
    if not names:
        raise SystemExit("no attention/MLP projections found to adapt")
    return names


def load_peft(args, compute_dtype, device):
    import torch
    import transformers
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    kwargs = {"dtype": compute_dtype if compute_dtype != torch.float32 else torch.float32}
    if not args.no_4bit:
        from transformers import BitsAndBytesConfig

        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=compute_dtype,
        )
        kwargs["device_map"] = {"": 0} if device == "cuda" else None
    model = AutoModelForCausalLM.from_pretrained(args.model, **kwargs)
    if args.no_4bit:
        model.to(device)
    model.config.use_cache = False
    if not args.no_4bit:
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
                                                gradient_checkpointing_kwargs={"use_reentrant": False})
    else:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
    targets = lora_targets(model)
    config = LoraConfig(
        r=args.rank, lora_alpha=args.alpha, lora_dropout=args.dropout, bias="none", task_type="CAUSAL_LM",
        target_modules=targets, modules_to_save=["lm_head", "embed_tokens"] if args.train_embeddings else None,
    )
    model = get_peft_model(model, config)
    return model, tokenizer, targets, {"transformers": transformers.__version__, "class": type(model.base_model.model).__name__}


def load_unsloth(args, compute_dtype, device):
    import torch
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model, max_seq_length=args.seq, load_in_4bit=not args.no_4bit,
        dtype=None if compute_dtype == torch.float32 else compute_dtype,
    )
    targets = lora_targets(model)
    model = FastLanguageModel.get_peft_model(
        model, r=args.rank, lora_alpha=args.alpha, lora_dropout=args.dropout, bias="none", target_modules=targets,
        modules_to_save=["lm_head", "embed_tokens"] if args.train_embeddings else None,
        use_gradient_checkpointing="unsloth", random_state=args.seed,
    )
    FastLanguageModel.for_training(model)
    import unsloth

    return model, tokenizer, targets, {"unsloth": getattr(unsloth, "__version__", "?"), "class": type(model).__name__}


def main() -> None:
    global _EVENT_LOG
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    _EVENT_LOG = args.output / "events.jsonl"

    import torch

    device = args.device or ("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    bf16_ok = device == "cuda" and torch.cuda.is_bf16_supported(including_emulation=False)
    if args.compute_dtype == "auto":
        compute_dtype = torch.bfloat16 if bf16_ok else torch.float32
    else:
        compute_dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[args.compute_dtype]
    if compute_dtype == torch.bfloat16 and device == "cuda" and not bf16_ok:
        raise SystemExit("this GPU has no bf16 support: use --compute-dtype fp32 (fp16 NaNs on Qwen3.5 GDN layers)")
    torch.manual_seed(args.seed)
    emit("hardware", device=device, name=torch.cuda.get_device_name(0) if device == "cuda" else device, torch=torch.__version__,
         compute_dtype=str(compute_dtype).replace("torch.", ""), four_bit=not args.no_4bit, backend=args.backend,
         memory_gb=round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1) if device == "cuda" else None)

    loader = load_unsloth if args.backend == "unsloth" else load_peft
    started_load = time.time()
    model, tokenizer, targets, versions = loader(args, compute_dtype, device)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    kinds = {}
    for name in targets:
        kinds[name.rsplit(".", 1)[-1]] = kinds.get(name.rsplit(".", 1)[-1], 0) + 1
    emit("model", model=args.model, load_seconds=round(time.time() - started_load, 1), trainable_parameters=trainable,
         parameters=total, trainable_fraction=trainable / max(1, total), lora_targets=len(targets), lora_target_kinds=kinds,
         lora_target_examples=targets[:3], excluded_pattern=EXCLUDE_PATTERN.pattern, rank=args.rank, alpha=args.alpha, **versions)
    with (args.output / "lora-targets.json").open("w") as handle:
        json.dump({"targets": targets, "rank": args.rank, "alpha": args.alpha, "dropout": args.dropout}, handle, indent=1)

    train_chunks = load_chunks(args.data_dir / "train.jsonl", tokenizer, args.seq)
    valid_chunks = load_chunks(args.data_dir / "valid.jsonl", tokenizer, args.seq, args.valid_chunks)
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    per_step = args.batch * args.accum
    steps_per_epoch = math.ceil(len(train_chunks) / per_step)
    total_steps = args.max_steps or max(1, math.ceil(steps_per_epoch * args.epochs))
    warmup = max(args.warmup_min_steps, int(total_steps * args.warmup_frac))
    warmup = min(warmup, max(1, total_steps // 2))
    eval_every = args.eval_every or max(1, total_steps // 10)
    config = {k: getattr(args, k) for k in vars(args)}
    config.update(total_steps=total_steps, steps_per_epoch=steps_per_epoch, warmup_steps=warmup, eval_every=eval_every,
                  train_chunks=len(train_chunks), valid_chunks=len(valid_chunks), device=device,
                  compute_dtype=str(compute_dtype).replace("torch.", ""))
    emit("config", **config)
    (args.output / "config.json").write_text(json.dumps(config, indent=2, default=str) + "\n")

    def lr_at(step: int) -> float:
        if step < warmup:
            return args.lr * (step + 1) / warmup
        progress = (step - warmup) / max(1, total_steps - warmup)
        return args.lr * (1.0 - (1.0 - args.final_lr_frac) * min(1.0, progress))

    lora_params = [p for n, p in model.named_parameters() if p.requires_grad and "lora_" in n]
    other_params = [p for n, p in model.named_parameters() if p.requires_grad and "lora_" not in n]
    groups = [{"params": lora_params, "lr": args.lr, "weight_decay": args.weight_decay}]
    if other_params:
        groups.append({"params": other_params, "lr": args.embedding_lr, "weight_decay": 0.0})
    optimizer = torch.optim.AdamW(groups, betas=(0.9, 0.999), eps=1e-8)
    use_scaler = compute_dtype == torch.float16
    scaler = torch.amp.GradScaler(device, enabled=use_scaler)
    autocast = lambda: torch.autocast(device_type=device, dtype=compute_dtype, enabled=(compute_dtype != torch.float32))  # noqa: E731

    @torch.no_grad()
    def evaluate(model_) -> dict:
        model_.eval()
        total_loss, total_tokens = 0.0, 0
        for begin in range(0, len(valid_chunks), args.batch):
            input_ids, labels, attention = collate(valid_chunks[begin : begin + args.batch], device, pad_id)
            with autocast():
                loss, count = lm_loss(model_, input_ids, attention, labels, args.loss_chunk, checkpoint=False)
            total_loss += loss.item()
            total_tokens += count
        model_.train()
        return {"loss": total_loss / max(1, total_tokens), "eval_tokens": total_tokens, "chunks": len(valid_chunks)}

    def save_adapter(label: str, step: int) -> Path:
        path = args.output / "adapter"
        model.save_pretrained(str(path), safe_serialization=True)
        tokenizer.save_pretrained(str(path))
        (path / "trainer_state.json").write_text(json.dumps({"step": step, "label": label, "total_steps": total_steps,
                                                             "elapsed_minutes": round((time.time() - STARTED) / 60, 2),
                                                             "config": config}, indent=2, default=str) + "\n")
        emit("adapter", path=str(path), step=step, label=label)
        return path

    heartbeat = {"time": time.time()}
    state = {"step": 0}

    def stall_guard() -> None:
        while True:
            time.sleep(30)
            if time.time() - heartbeat["time"] > args.stall_minutes * 60:
                emit("watchdog", reason=f"no optimizer step for {args.stall_minutes} minutes", step=state["step"])
                sys.stdout.flush()
                os._exit(3)

    if args.stall_minutes and args.stall_minutes > 0:
        threading.Thread(target=stall_guard, daemon=True).start()

    order = []
    rng = __import__("numpy").random.default_rng(args.seed)
    while len(order) < total_steps * per_step:
        order.extend(int(i) for i in rng.permutation(len(train_chunks)))
    emit("validation", step=0, tokens=0, **evaluate(model))
    model.train()
    tokens_done = 0
    interval = {"loss": 0.0, "steps": 0, "tokens": 0, "started": time.time()}
    stopped_for_budget = False
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    for step in range(total_steps):
        lr = lr_at(step)
        optimizer.param_groups[0]["lr"] = lr
        step_loss, step_tokens = 0.0, 0
        for micro in range(args.accum):
            begin = (step * args.accum + micro) * args.batch
            chunks = [train_chunks[i] for i in order[begin : begin + args.batch]]
            input_ids, labels, attention = collate(chunks, device, pad_id)
            with autocast():
                loss_sum, count = lm_loss(model, input_ids, attention, labels, args.loss_chunk, checkpoint=True)
            loss = loss_sum / max(1, count)
            scaler.scale(loss / args.accum).backward()
            step_loss += loss.item() / args.accum
            step_tokens += count
        scaler.unscale_(optimizer)
        grad_norm = torch.nn.utils.clip_grad_norm_([p for g in groups for p in g["params"]], args.grad_clip).item()
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)
        state["step"] = step + 1
        heartbeat["time"] = time.time()
        tokens_done += step_tokens
        if not math.isfinite(step_loss):
            emit("nonfinite", step=step + 1, loss=step_loss, grad_norm=grad_norm)
            if not use_scaler:
                raise SystemExit(f"non-finite loss at step {step + 1}")
        interval["loss"] += step_loss
        interval["steps"] += 1
        interval["tokens"] += step_tokens
        if (step + 1) % args.log_every == 0 or step + 1 == total_steps:
            now = time.time()
            emit("train", step=step + 1, tokens=tokens_done, loss=interval["loss"] / interval["steps"], learning_rate=lr,
                 gradient_norm=grad_norm, tokens_per_second=interval["tokens"] / max(now - interval["started"], 1e-9),
                 peak_memory_gb=round(torch.cuda.max_memory_allocated() / 2**30, 2) if device == "cuda" else None)
            interval = {"loss": 0.0, "steps": 0, "tokens": 0, "started": now}
        if (step + 1) % eval_every == 0 and step + 1 < total_steps:
            emit("validation", step=step + 1, tokens=tokens_done, **evaluate(model))
        if args.max_minutes and (time.time() - STARTED) / 60 >= args.max_minutes - 1.0 and step + 1 < total_steps:
            save_adapter("budget", step + 1)
            stopped_for_budget = True
            emit("budget_stop", step=step + 1, tokens=tokens_done)
            break

    final = evaluate(model)
    emit("validation", step=state["step"], tokens=tokens_done, final=not stopped_for_budget, **final)
    adapter_path = save_adapter("final" if not stopped_for_budget else "budget", state["step"])
    summary = {"completed": not stopped_for_budget, "steps": state["step"], "tokens": tokens_done, "final_validation": final,
               "adapter": str(adapter_path), "elapsed_minutes": round((time.time() - STARTED) / 60, 2), "merged": None}

    if args.merge:
        from peft import PeftModel
        from transformers import AutoModelForCausalLM

        del optimizer
        model.cpu()
        del model
        if device == "cuda":
            torch.cuda.empty_cache()
        merge_dtype = torch.bfloat16 if bf16_ok else (torch.float16 if device == "cuda" else torch.float32)
        base = AutoModelForCausalLM.from_pretrained(args.model, dtype=merge_dtype).to(device)
        merged = PeftModel.from_pretrained(base, str(adapter_path)).merge_and_unload()
        merged_path = args.output / "merged"
        merged.save_pretrained(str(merged_path), safe_serialization=True)
        tokenizer.save_pretrained(str(merged_path))
        merged_loss = evaluate(merged)
        emit("merged", path=str(merged_path), dtype=str(merge_dtype).replace("torch.", ""), **{f"merged_{k}": v for k, v in merged_loss.items()},
             adapter_loss=final["loss"], delta=merged_loss["loss"] - final["loss"])
        summary["merged"] = {"path": str(merged_path), "dtype": str(merge_dtype).replace("torch.", ""), "validation": merged_loss}

    (args.output / ("training-complete.json" if not stopped_for_budget else "training-paused.json")).write_text(
        json.dumps(summary, indent=2, default=str) + "\n")
    emit("complete", **{k: v for k, v in summary.items() if k != "final_validation"}, final_loss=final["loss"])


if __name__ == "__main__":
    main()
