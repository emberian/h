#!/usr/bin/env python3
"""Single-GPU continued pretraining of a Falcon-H1 checkpoint (Hugging Face transformers) on our
uint16 token streams.

Recipe defaults (research/literature-chain-2026-09-03.md chain A; research/results/night-2026-09-02.md):
one epoch over the stream, AdamW (0.9, 0.95) with weight decay 0.1 on matrices, peak LR 5e-5 (half the
0.5B's 1e-4) re-warmed over the first 2% of tokens, warmup-stable-decay with a linear cooldown over the
last 10% of tokens to 10% of peak, sequence 2048, global batch 64 x 2048 tokens via accumulation, FP32
master weights with BF16 autocast, gradient checkpointing, checkpoints at every 25% and at the end in HF
safetensors (loadable by our MLX serving, JAX evaluators, hbox_training/rollout_eval.py and the Kaggle
GPU kernels: `tokens-<n>/` directories like the TPU kernel), validation loss on validation.bin and
room-validation.bin every 5%, and a JSON event log (`{"event": ..., "tokens": ..., "loss": ...}` lines
on stdout and in <output>/events.jsonl).

Data: the stream is contiguous token ids with EOS after each document; the dataset yields
non-overlapping windows of seq+1 tokens (window i = stream[i*seq : i*seq+seq+1]) in a deterministic
permutation per epoch (numpy default_rng(seed + epoch)). Documents are not masked from one another.

Watchdogs: --max-minutes saves a resumable checkpoint and exits 0 when the wall clock runs out;
--stall-minutes kills the process (exit 3) if no optimizer step completes within the bound.

Fast path: transformers' FalconH1 uses the `mamba-ssm` Triton SSD kernels and `causal-conv1d` when both
import on CUDA (`is_fast_path_available` in modeling_falcon_h1), otherwise a pure-PyTorch chunked scan
(`torch_forward`, several times slower). The "hardware" event reports which one is active.

    # H100, the 1.5B on corpus-v1.5-replay-15b (one epoch):
    python gpu/cpt_torch.py --model /data/models/falcon-h1-1.5b-deep-base \
        --stream /data/corpus-v1.5-replay-15b/train.bin \
        --validation /data/corpus-v1.5-replay-15b/validation.bin \
        --room-validation /data/corpus-v1.5-replay-15b/room-validation.bin \
        --output /data/runs/h15b-replay-e1 --max-minutes 600

    # T4 test (Kaggle): --tiny applies the small-scale settings (2M tokens, 4 x 2 x 2048, fp16 autocast).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import threading
import time
from pathlib import Path

import numpy as np

STREAM_DTYPE = "<u2"
TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "generation_config.json")
RESUME_FILES = ("master.pt", "optimizer.pt", "scaler.pt")

# The recipe, and the T4-sized override used by --tiny. A flag given on the command line wins over both.
RECIPE = {
    "tokens": None,  # one epoch
    "lr": 5e-5,
    "warmup_frac": 0.02,
    "warmup_min_steps": 20,  # Adam's first full-LR steps are sign steps; never start a run with fewer warmup steps
    "decay_frac": 0.10,
    "final_lr_frac": 0.10,
    "weight_decay": 0.1,
    "beta1": 0.9,
    "beta2": 0.95,
    "grad_clip": 1.0,
    "seq": 2048,
    "batch": 8,
    "accum": 8,
    "dtype": "bf16",
    "checkpoint_every_frac": 0.25,
    "validate_every_frac": 0.05,
    "validation_windows": 256,
    "log_every": 10,
    "max_minutes": 0.0,
    "stall_minutes": 20.0,
}
TINY = {
    **RECIPE,
    "tokens": 2_000_000,
    "lr": 6e-5,  # the 90M's hbox PyTorch run (research/results/hbox-cpt-10m.md) used 6e-5 with a 3M-token warmup
    "warmup_frac": 0.30,
    "batch": 2,  # 4 x 2048 OOMs a 16 GB T4 in the pure-PyTorch scan's backward (a 6 GiB block); 2 x 4 keeps 16k tokens/step
    "accum": 4,
    "dtype": "fp16",
    "checkpoint_every_frac": 0.25,
    "validate_every_frac": 0.25,
    "validation_windows": 16,
    "log_every": 5,
    "max_minutes": 30.0,
    "stall_minutes": 15.0,
}

STARTED = time.time()
_EVENT_LOG: Path | None = None


def emit(event: str, **values) -> None:
    record = {"event": event, "elapsed_minutes": round((time.time() - STARTED) / 60, 3), **values}
    line = json.dumps(record, default=str)
    print(line, flush=True)
    if _EVENT_LOG is not None:
        with _EVENT_LOG.open("a") as handle:
            handle.write(line + "\n")


# ------------------------------------------------------------------------------------------- data
class WindowStream:
    """Non-overlapping (seq+1)-token windows over a uint16 stream, in a seeded permutation per epoch."""

    def __init__(self, path: Path, seq: int, seed: int):
        self.path = path
        self.seq = seq
        self.seed = seed
        self.tokens = np.memmap(path, dtype=STREAM_DTYPE, mode="r")
        self.windows = (self.tokens.shape[0] - 1) // seq
        if self.windows < 1:
            raise SystemExit(f"{path}: {self.tokens.shape[0]} tokens is fewer than one window of {seq + 1}")
        self._epoch = -1
        self._order = None

    def order(self, epoch: int) -> np.ndarray:
        if epoch != self._epoch:
            self._order = np.random.default_rng(self.seed + epoch).permutation(self.windows)
            self._epoch = epoch
        return self._order

    def window(self, index: int) -> np.ndarray:
        start = index * self.seq
        return np.asarray(self.tokens[start : start + self.seq + 1], dtype=np.int64)

    def batch(self, position: int, batch: int) -> np.ndarray:
        """Windows number position .. position+batch-1 of the global (epoch-concatenated) order."""

        rows = []
        for k in range(position, position + batch):
            epoch, offset = divmod(k, self.windows)
            rows.append(self.window(int(self.order(epoch)[offset])))
        return np.stack(rows)

    def head(self, count: int) -> np.ndarray:
        """The first `count` windows in stream order (the fixed validation slice)."""

        count = min(count, self.windows)
        return np.stack([self.window(i) for i in range(count)])


# ---------------------------------------------------------------------------------------- schedule
def lr_at(tokens: int, total: int, peak: float, warmup_frac: float, decay_frac: float, final_frac: float, warmup_min: int = 0) -> float:
    """Linear warmup over max(warmup_frac * total, warmup_min) tokens, constant, then a linear decay over the
    last decay_frac * total tokens from peak to final_frac * peak."""

    warmup = max(1, int(total * warmup_frac), warmup_min)
    decay = max(1, int(total * decay_frac))
    if tokens < warmup:
        return peak * (tokens + 1) / warmup
    decay_start = total - decay
    if tokens < decay_start:
        return peak
    progress = min(1.0, (tokens - decay_start) / decay)
    return peak * (1.0 - (1.0 - final_frac) * progress)


# ------------------------------------------------------------------------------------------- main
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", type=Path, required=True, help="HF Falcon-H1 checkpoint directory")
    parser.add_argument("--stream", type=Path, required=True, help="uint16 training stream (train.bin)")
    parser.add_argument("--validation", type=Path, required=True, help="uint16 validation stream (validation.bin)")
    parser.add_argument("--room-validation", type=Path, default=None, help="uint16 room holdout (room-validation.bin)")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-name", default=None, help="recorded in events and trainer_state (default: output dir name)")
    parser.add_argument("--tiny", action="store_true", help="T4-sized defaults: 2M tokens, 4 x 2 x 2048, fp16 autocast")
    parser.add_argument("--tokens", type=int, help="token budget (default: one epoch of the stream)")
    parser.add_argument("--lr", type=float)
    parser.add_argument("--warmup-frac", type=float)
    parser.add_argument("--warmup-min-steps", type=int, help="warmup is at least this many optimizer steps")
    parser.add_argument("--decay-frac", type=float)
    parser.add_argument("--final-lr-frac", type=float)
    parser.add_argument("--weight-decay", type=float)
    parser.add_argument("--beta1", type=float)
    parser.add_argument("--beta2", type=float)
    parser.add_argument("--grad-clip", type=float)
    parser.add_argument("--seq", type=int)
    parser.add_argument("--batch", type=int, help="sequences per forward")
    parser.add_argument("--accum", type=int, help="forwards per optimizer step (global batch = batch x accum)")
    parser.add_argument("--dtype", choices=("bf16", "fp16", "fp32"), help="autocast compute dtype; masters are fp32")
    parser.add_argument("--save-dtype", choices=("bf16", "fp16", "fp32"), default="bf16", help="dtype of the HF checkpoints")
    parser.add_argument("--checkpoint-every-frac", type=float)
    parser.add_argument("--validate-every-frac", type=float)
    parser.add_argument("--validation-windows", type=int, help="windows of seq tokens per validation stream")
    parser.add_argument("--log-every", type=int, help="optimizer steps between train events")
    parser.add_argument("--max-minutes", type=float, help="wall-clock budget: save a resumable checkpoint and exit (0 = none)")
    parser.add_argument("--stall-minutes", type=float, help="exit 3 if no optimizer step completes within this bound")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--attn", default="sdpa", help="attn_implementation (sdpa, eager, flash_attention_2)")
    parser.add_argument("--no-gradient-checkpointing", action="store_true")
    parser.add_argument("--keep-resume-states", action="store_true", help="keep master/optimizer files in every checkpoint")
    parser.add_argument("--resume", type=Path, default=None, help="a tokens-*/ directory with master.pt and optimizer.pt")
    parser.add_argument("--reload-check", action="store_true", help="after training, reload the final checkpoint and re-validate")
    parser.add_argument("--device", default=None)
    args = parser.parse_args()
    preset = TINY if args.tiny else RECIPE
    for key, value in preset.items():
        if getattr(args, key) is None:
            setattr(args, key, value)
    if args.run_name is None:
        args.run_name = args.output.name
    return args


def main() -> None:
    global _EVENT_LOG
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    _EVENT_LOG = args.output / "events.jsonl"

    import torch
    import transformers
    from transformers import AutoTokenizer, FalconH1ForCausalLM
    from transformers.models.falcon_h1 import modeling_falcon_h1

    device = args.device or ("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    compute_dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[args.dtype]
    save_dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[args.save_dtype]
    if device == "cuda" and compute_dtype == torch.bfloat16 and not torch.cuda.is_bf16_supported(including_emulation=False):
        raise SystemExit("this GPU has no bf16 support (Turing/T4): pass --dtype fp16 or fp32")
    torch.manual_seed(args.seed)
    emit(
        "hardware",
        device=device,
        name=torch.cuda.get_device_name(0) if device == "cuda" else device,
        torch=torch.__version__,
        transformers=transformers.__version__,
        fast_path=bool(modeling_falcon_h1.is_fast_path_available),
        fast_path_note="mamba-ssm + causal-conv1d kernels" if modeling_falcon_h1.is_fast_path_available else
        "pure-PyTorch chunked scan (install mamba-ssm and causal-conv1d for the CUDA fast path)",
        memory_gb=round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1) if device == "cuda" else None,
    )

    # ---------------------------------------------------------------------------------------- data
    train = WindowStream(args.stream, args.seq, args.seed)
    validation = WindowStream(args.validation, args.seq, args.seed)
    room = WindowStream(args.room_validation, args.seq, args.seed) if args.room_validation else None
    tokens_per_step = args.batch * args.accum * args.seq
    epoch_tokens = train.windows * args.seq
    total_tokens = args.tokens or epoch_tokens
    total_steps = max(1, math.ceil(total_tokens / tokens_per_step))
    total_tokens = total_steps * tokens_per_step  # batch-aligned, like the TPU kernel
    config = {
        key: getattr(args, key)
        for key in (
            "run_name", "tokens", "lr", "warmup_frac", "warmup_min_steps", "decay_frac", "final_lr_frac", "weight_decay", "beta1", "beta2",
            "grad_clip", "seq", "batch", "accum", "dtype", "save_dtype", "checkpoint_every_frac", "validate_every_frac",
            "validation_windows", "seed", "attn", "max_minutes", "stall_minutes",
        )
    }
    warmup_tokens = max(1, int(total_tokens * args.warmup_frac), args.warmup_min_steps * tokens_per_step)

    def schedule(tokens_: int) -> float:
        return lr_at(tokens_, total_tokens, args.lr, args.warmup_frac, args.decay_frac, args.final_lr_frac, warmup_tokens)

    config.update(
        model=str(args.model), stream=str(args.stream), validation=str(args.validation),
        room_validation=str(args.room_validation) if args.room_validation else None, output=str(args.output),
        stream_tokens=int(train.tokens.shape[0]), stream_windows=train.windows, epoch_tokens=epoch_tokens,
        total_tokens=total_tokens, total_steps=total_steps, tokens_per_step=tokens_per_step,
        warmup_tokens=warmup_tokens, warmup_steps=math.ceil(warmup_tokens / tokens_per_step),
        decay_tokens=int(total_tokens * args.decay_frac),
        epochs=total_tokens / epoch_tokens, gradient_checkpointing=not args.no_gradient_checkpointing,
    )
    emit("config", **config)
    (args.output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    stream_max = int(np.asarray(train.tokens[: min(train.tokens.shape[0], 50_000_000)]).max())

    # --------------------------------------------------------------------------------------- model
    model = FalconH1ForCausalLM.from_pretrained(args.model, dtype=torch.float32, attn_implementation=args.attn, local_files_only=True)
    if stream_max >= model.config.vocab_size:
        raise SystemExit(f"stream has token id {stream_max} >= model vocab {model.config.vocab_size}: wrong tokenizer family")
    model.config.use_cache = False
    if not args.no_gradient_checkpointing:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.to(device)
    model.train()
    parameters = [p for p in model.parameters() if p.requires_grad]
    decay = [p for p in parameters if p.ndim >= 2]
    no_decay = [p for p in parameters if p.ndim < 2]
    optimizer = torch.optim.AdamW(
        [{"params": decay, "weight_decay": args.weight_decay}, {"params": no_decay, "weight_decay": 0.0}],
        lr=args.lr, betas=(args.beta1, args.beta2), eps=1e-8, fused=(device == "cuda"),
    )
    scaler = torch.amp.GradScaler(device, enabled=(compute_dtype == torch.float16))
    emit("model", parameters=sum(p.numel() for p in parameters), decay_tensors=len(decay), no_decay_tensors=len(no_decay),
         vocab_size=model.config.vocab_size, layers=model.config.num_hidden_layers, hidden=model.config.hidden_size)

    step = 0
    tokens_done = 0
    if args.resume:
        state = json.loads((args.resume / "trainer_state.json").read_text())
        model.load_state_dict(torch.load(args.resume / "master.pt", map_location=device))
        optimizer.load_state_dict(torch.load(args.resume / "optimizer.pt", map_location=device))
        if (args.resume / "scaler.pt").exists():
            scaler.load_state_dict(torch.load(args.resume / "scaler.pt"))
        step, tokens_done = int(state["step"]), int(state["tokens"])
        if state["tokens_per_step"] != tokens_per_step or state["seed"] != args.seed:
            raise SystemExit("resume checkpoint was written with a different batch shape or seed")
        emit("resume", path=str(args.resume), step=step, tokens=tokens_done)

    # ---------------------------------------------------------------------------------- evaluation
    def loss_of(windows: np.ndarray) -> torch.Tensor:
        batch = torch.from_numpy(windows).to(device, non_blocking=True)
        inputs, targets = batch[:, :-1], batch[:, 1:]
        with torch.autocast(device_type=device, dtype=compute_dtype, enabled=(compute_dtype != torch.float32)):
            logits = model(input_ids=inputs, use_cache=False).logits
        return torch.nn.functional.cross_entropy(logits.float().reshape(-1, logits.shape[-1]), targets.reshape(-1))

    @torch.no_grad()
    def evaluate(model_) -> dict:
        model_.eval()
        result = {}
        for key, stream in (("loss", validation), ("room_loss", room)):
            if stream is None:
                continue
            rows = stream.head(args.validation_windows)
            total = 0.0
            for begin in range(0, rows.shape[0], args.batch):
                chunk = rows[begin : begin + args.batch]
                total += loss_of(chunk).item() * chunk.shape[0]
            result[key] = total / rows.shape[0]
            result[key.replace("loss", "windows")] = int(rows.shape[0])
        model_.train()
        return result

    # ------------------------------------------------------------------------------- checkpointing
    def save(step_: int, tokens_: int, label: str, resumable: bool) -> Path:
        path = args.output / f"tokens-{tokens_:012d}"
        temporary = args.output / f".tokens-{tokens_:012d}.tmp"
        if temporary.exists():
            shutil.rmtree(temporary)
        temporary.mkdir()
        model.save_pretrained(temporary, safe_serialization=True, max_shard_size="20GB",
                              state_dict={k: v.to(save_dtype) for k, v in model.state_dict().items()})
        saved_config = json.loads((temporary / "config.json").read_text())
        saved_config["dtype"] = {"bf16": "bfloat16", "fp16": "float16", "fp32": "float32"}[args.save_dtype]
        saved_config["torch_dtype"] = saved_config["dtype"]
        saved_config["use_cache"] = True
        (temporary / "config.json").write_text(json.dumps(saved_config, indent=2) + "\n")
        for name in TOKENIZER_FILES:
            if (args.model / name).exists():
                shutil.copy2(args.model / name, temporary / name)
        if resumable:
            torch.save(model.state_dict(), temporary / "master.pt")
            torch.save(optimizer.state_dict(), temporary / "optimizer.pt")
            if scaler.is_enabled():
                torch.save(scaler.state_dict(), temporary / "scaler.pt")
        (temporary / "trainer_state.json").write_text(json.dumps({
            "run_name": args.run_name, "step": step_, "tokens": tokens_, "label": label, "tokens_per_step": tokens_per_step,
            "total_tokens": total_tokens, "seed": args.seed, "learning_rate": schedule(tokens_),
            "resumable": resumable, "elapsed_minutes": round((time.time() - STARTED) / 60, 2), "config": config,
        }, indent=2) + "\n")
        if path.exists():
            shutil.rmtree(path)
        os.replace(temporary, path)
        if resumable and not args.keep_resume_states:
            for other in sorted(args.output.glob("tokens-*")):
                if other != path:
                    for name in RESUME_FILES:
                        (other / name).unlink(missing_ok=True)
        emit("checkpoint", path=str(path), step=step_, tokens=tokens_, label=label, resumable=resumable)
        return path

    # ------------------------------------------------------------------------------------ watchdog
    heartbeat = {"time": time.time()}

    def stall_guard() -> None:
        while True:
            time.sleep(30)
            if time.time() - heartbeat["time"] > args.stall_minutes * 60:
                emit("watchdog", reason=f"no optimizer step for {args.stall_minutes} minutes", step=step, tokens=tokens_done)
                sys.stdout.flush()
                os._exit(3)

    if args.stall_minutes and args.stall_minutes > 0:
        threading.Thread(target=stall_guard, daemon=True).start()

    # ---------------------------------------------------------------------------------------- loop
    validate_every = max(tokens_per_step, int(total_tokens * args.validate_every_frac)) if args.validate_every_frac > 0 else None
    checkpoint_every = max(tokens_per_step, int(total_tokens * args.checkpoint_every_frac)) if args.checkpoint_every_frac > 0 else None
    next_validation = (tokens_done // validate_every + 1) * validate_every if validate_every else None
    next_checkpoint = (tokens_done // checkpoint_every + 1) * checkpoint_every if checkpoint_every else None
    if step == 0 and validate_every:
        emit("validation", step=0, tokens=0, **evaluate(model))
    interval_loss, interval_steps, interval_tokens, interval_started = 0.0, 0, 0, time.time()
    stopped_for_budget = False
    last_checkpoint: Path | None = None
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    while step < total_steps:
        lr = schedule(tokens_done)
        for group in optimizer.param_groups:
            group["lr"] = lr
        position = step * args.batch * args.accum
        step_loss = 0.0
        for micro in range(args.accum):
            windows = train.batch(position + micro * args.batch, args.batch)
            loss = loss_of(windows)
            scaler.scale(loss / args.accum).backward()
            step_loss += loss.item() / args.accum
        scaler.unscale_(optimizer)
        grad_norm = torch.nn.utils.clip_grad_norm_(parameters, args.grad_clip).item()
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)
        step += 1
        tokens_done += tokens_per_step
        heartbeat["time"] = time.time()
        if not math.isfinite(step_loss):
            emit("nonfinite", step=step, tokens=tokens_done, loss=step_loss, grad_norm=grad_norm, scale=scaler.get_scale())
            if compute_dtype != torch.float16:
                save(step, tokens_done, "nonfinite", resumable=True)
                raise SystemExit(f"non-finite loss at step {step}")
        interval_loss += step_loss
        interval_steps += 1
        interval_tokens += tokens_per_step
        if step % args.log_every == 0 or step == total_steps:
            now = time.time()
            emit(
                "train", step=step, tokens=tokens_done, loss=interval_loss / interval_steps, learning_rate=lr,
                gradient_norm=grad_norm, tokens_per_second=interval_tokens / max(now - interval_started, 1e-9),
                epoch=tokens_done / epoch_tokens,
                peak_memory_gb=round(torch.cuda.max_memory_allocated() / 2**30, 2) if device == "cuda" else None,
                scale=scaler.get_scale() if scaler.is_enabled() else None,
            )
            interval_loss, interval_steps, interval_tokens, interval_started = 0.0, 0, 0, now
        if next_validation and tokens_done >= next_validation and step < total_steps:
            emit("validation", step=step, tokens=tokens_done, **evaluate(model))
            next_validation += validate_every
        if next_checkpoint and tokens_done >= next_checkpoint and step < total_steps:
            last_checkpoint = save(step, tokens_done, "scheduled", resumable=True)
            next_checkpoint += checkpoint_every
        if args.max_minutes and (time.time() - STARTED) / 60 >= args.max_minutes - 1.0 and step < total_steps:
            last_checkpoint = save(step, tokens_done, "budget", resumable=True)
            stopped_for_budget = True
            emit("budget_stop", step=step, tokens=tokens_done)
            break

    final = evaluate(model)
    emit("validation", step=step, tokens=tokens_done, final=not stopped_for_budget, **final)
    if not stopped_for_budget:
        last_checkpoint = save(step, tokens_done, "final", resumable=args.keep_resume_states)
    (args.output / ("training-complete.json" if not stopped_for_budget else "training-paused.json")).write_text(json.dumps({
        "completed": not stopped_for_budget, "run_name": args.run_name, "steps": step, "tokens": tokens_done,
        "tokens_per_step": tokens_per_step, "elapsed_minutes": round((time.time() - STARTED) / 60, 2),
        "final_validation": final, "checkpoint": str(last_checkpoint) if last_checkpoint else None,
    }, indent=2) + "\n")

    if args.reload_check and last_checkpoint is not None:
        del optimizer
        model.cpu()
        del model
        if device == "cuda":
            torch.cuda.empty_cache()
        model = FalconH1ForCausalLM.from_pretrained(last_checkpoint, dtype=torch.float32, local_files_only=True).to(device)
        tokenizer = AutoTokenizer.from_pretrained(last_checkpoint, local_files_only=True)
        reloaded = evaluate(model)
        delta = abs(reloaded["loss"] - final["loss"])
        emit("reload_check", path=str(last_checkpoint), tokenizer_vocab=len(tokenizer), **{f"reloaded_{k}": v for k, v in reloaded.items()},
             delta=delta, ok=delta < 0.05)
        if not delta < 0.05:
            raise SystemExit(f"reloaded checkpoint disagrees with the trained model: {reloaded} vs {final}")
    emit("complete", completed=not stopped_for_budget, steps=step, tokens=tokens_done)


if __name__ == "__main__":
    main()
