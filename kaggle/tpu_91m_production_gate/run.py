from __future__ import annotations

import gc
import glob
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# EasyDeL reads these while importing, so they must precede JAX/EasyDeL imports.
os.environ.setdefault("EASYDEL_AUTO", "1")
os.environ.setdefault("ENABLE_DISTRIBUTED_INIT", "0")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("JAX_COMPILATION_CACHE_DIR", "/kaggle/working/jax-cache")
os.environ.setdefault("PIP_DISABLE_PIP_VERSION_CHECK", "1")

subprocess.run(
    [sys.executable, "-m", "pip", "install", "--quiet", "easydel==0.3.0", "pillow"],
    check=True,
)

import easydel as ed
import jax
import jax.numpy as jnp
import numpy as np
from datasets import Dataset

SEQUENCE_LENGTH = 512
GLOBAL_BATCH = 128
TRAIN_STEPS = 6
WARM_STEPS = 4
EVAL_BATCH = 8
MINIMUM_WARM_TOKENS_PER_SECOND = 50_000.0
MAXIMUM_WARM_TIME_RATIO = 1.50
MAXIMUM_RELOAD_LOSS_DELTA = 1e-6


def emit(event: str, **values: Any) -> None:
    print(json.dumps({"event": event, **values}, default=str), flush=True)


def exactly_one(pattern: str) -> Path:
    matches = [Path(value) for value in glob.glob(pattern, recursive=True)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one match for {pattern!r}, found {matches}")
    return matches[0]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checkpoint_digest(root: Path) -> tuple[str, int, int]:
    digest = hashlib.sha256()
    total_bytes = 0
    files = 0
    for path in sorted(value for value in root.rglob("*") if value.is_file()):
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        digest.update(relative.encode())
        digest.update(str(size).encode())
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                digest.update(block)
        total_bytes += size
        files += 1
    return digest.hexdigest(), files, total_bytes


def tree_dtype_stats(tree: Any) -> dict[str, Any]:
    counts: dict[str, int] = {}
    elements: dict[str, int] = {}
    byte_counts: dict[str, int] = {}
    arrays = 0
    for leaf in jax.tree_util.tree_leaves(tree):
        value = getattr(leaf, "value", leaf)
        if not hasattr(value, "dtype") or not hasattr(value, "size"):
            continue
        dtype = str(value.dtype)
        size = int(value.size)
        itemsize = int(value.dtype.itemsize)
        counts[dtype] = counts.get(dtype, 0) + 1
        elements[dtype] = elements.get(dtype, 0) + size
        byte_counts[dtype] = byte_counts.get(dtype, 0) + size * itemsize
        arrays += 1
    return {
        "arrays": arrays,
        "counts": counts,
        "elements": elements,
        "bytes": byte_counts,
        "total_bytes": sum(byte_counts.values()),
    }


def serializable_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in metrics.items():
        if value is None or isinstance(value, str | bool | int | float):
            output[key] = value
            continue
        try:
            array = np.asarray(value)
            output[key] = array.item() if array.size == 1 else array.tolist()
        except (TypeError, ValueError):
            output[key] = str(value)
    return output


class RecordingTrainer(ed.Trainer):
    def __init__(self, *args: Any, **kwargs: Any):
        self.recorded_metrics: list[dict[str, Any]] = []
        super().__init__(*args, **kwargs)

    def log_metrics(
        self,
        metrics: dict[str, Any],
        pbar: Any,
        step: int,
        mode: str = "train",
        **kwargs: Any,
    ) -> Any:
        self.recorded_metrics.append(
            {
                "mode": mode,
                "step": int(step),
                "metrics": serializable_metrics(metrics),
            }
        )
        return super().log_metrics(metrics, pbar, step, mode, **kwargs)


def train_metric_rows(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for record in history:
        metrics = record["metrics"]
        if record["mode"] == "train" and "train/train_step" in metrics:
            rows.append(metrics)
    return rows


def last_eval_loss(history: list[dict[str, Any]]) -> float:
    losses = []
    for record in history:
        if record["mode"] != "eval":
            continue
        value = record["metrics"].get("eval/loss")
        if value is not None:
            losses.append(float(value))
    if not losses:
        raise RuntimeError("Evaluation completed without an eval/loss metric")
    return losses[-1]


hardware = {
    "jax": jax.__version__,
    "easydel": getattr(ed, "__version__", "0.3.0"),
    "backend": jax.default_backend(),
    "device_count": jax.device_count(),
    "devices": [str(device) for device in jax.devices()],
}
code_sha256 = sha256(Path(__file__))
emit("hardware", **hardware)
if hardware["backend"] != "tpu" or hardware["device_count"] != 8:
    raise RuntimeError("This gate requires the complete TPU v5e-8 slice")

base_manifest_path = exactly_one("/kaggle/input/**/preflight-manifest.json")
corpus_report_path = exactly_one("/kaggle/input/**/validation-report.json")
base_root = base_manifest_path.parent
corpus_root = corpus_report_path.parent
base_manifest = json.loads(base_manifest_path.read_text())
corpus_report = json.loads(corpus_report_path.read_text())
model_path = base_root / "model.safetensors"
train_path = corpus_root / "train.bin"
validation_path = corpus_root / "validation.bin"

expected_model_sha = base_manifest["files"]["model.safetensors"]["sha256"]
expected_train_sha = corpus_report["splits"]["train"]["sha256"]
expected_validation_sha = corpus_report["splits"]["validation"]["sha256"]
actual_model_sha = sha256(model_path)
actual_train_sha = sha256(train_path)
actual_validation_sha = sha256(validation_path)
if actual_model_sha != expected_model_sha:
    raise RuntimeError(f"Model checksum mismatch: {actual_model_sha}")
if actual_train_sha != expected_train_sha:
    raise RuntimeError(f"Training stream checksum mismatch: {actual_train_sha}")
if actual_validation_sha != expected_validation_sha:
    raise RuntimeError(f"Validation stream checksum mismatch: {actual_validation_sha}")

train_stream = np.memmap(train_path, mode="r", dtype="<u2")
validation_stream = np.memmap(validation_path, mode="r", dtype="<u2")
train_rows = GLOBAL_BATCH * TRAIN_STEPS
train_tokens = train_rows * SEQUENCE_LENGTH
eval_tokens = EVAL_BATCH * SEQUENCE_LENGTH
if train_stream.size < train_tokens or validation_stream.size < eval_tokens:
    raise RuntimeError("The sealed token streams are shorter than the production gate")

train_sequences = np.asarray(train_stream[:train_tokens], dtype=np.int32).reshape(
    train_rows, SEQUENCE_LENGTH
)
eval_sequences = np.asarray(validation_stream[:eval_tokens], dtype=np.int32).reshape(
    EVAL_BATCH, SEQUENCE_LENGTH
)
train_dataset = Dataset.from_dict(
    {
        "input_ids": [row.tolist() for row in train_sequences],
        "attention_mask": [[1] * SEQUENCE_LENGTH for _ in range(train_rows)],
    }
)
eval_dataset = Dataset.from_dict(
    {
        "input_ids": [row.tolist() for row in eval_sequences],
        "attention_mask": [[1] * SEQUENCE_LENGTH for _ in range(EVAL_BATCH)],
    }
)
emit(
    "real_dataset",
    sequence_length=SEQUENCE_LENGTH,
    global_batch=GLOBAL_BATCH,
    per_device_batch=GLOBAL_BATCH // jax.device_count(),
    tokens_per_step=GLOBAL_BATCH * SEQUENCE_LENGTH,
    train_steps=TRAIN_STEPS,
    first_train_tokens=train_sequences[0, :16].tolist(),
    first_eval_tokens=eval_sequences[0, :16].tolist(),
    train_sha256=actual_train_sha,
    validation_sha256=actual_validation_sha,
)

load_started = time.time()
model = ed.AutoEasyDeLModelForCausalLM.from_pretrained(
    str(base_root),
    from_torch=True,
    auto_shard_model=True,
    dtype=jnp.bfloat16,
    param_dtype=jnp.float32,
    precision=jax.lax.Precision.DEFAULT,
    sharding_axis_dims=(8, 1, 1, 1, 1),
    config_kwargs=ed.EasyDeLBaseConfigDict(
        freq_max_position_embeddings=SEQUENCE_LENGTH,
        mask_max_position_embeddings=SEQUENCE_LENGTH,
        attn_mechanism=ed.AttentionMechanisms.AUTO,
        attn_dtype=jnp.bfloat16,
        gradient_checkpointing=ed.EasyDeLGradientCheckPointers.NONE,
    ),
    verbose=True,
)
emit(
    "model_loaded",
    seconds=time.time() - load_started,
    parameters=base_manifest["parameter_count"],
    model_sha256=actual_model_sha,
    mesh=str(model.mesh),
    compute_dtype=str(model.dtype),
    parameter_dtype=str(model.param_dtype),
    attention="auto (EasyDeL selects blocksparse/Splash on TPU v4+)",
    gradient_checkpointing="none",
)

output_root = Path("/kaggle/working/easydel-91m-production-gate")
arguments = ed.TrainingArguments(
    save_directory=str(output_root),
    num_train_epochs=1,
    max_training_steps=TRAIN_STEPS,
    total_batch_size=GLOBAL_BATCH,
    eval_batch_size=EVAL_BATCH,
    gradient_accumulation_steps=1,
    learning_rate=1e-6,
    weight_decay=0.01,
    clip_grad=1.0,
    tx_mu_dtype=jnp.float32,
    max_length=SEQUENCE_LENGTH,
    log_steps=1,
    report_steps=1,
    log_grad_norms=False,
    performance_mode=True,
    shuffle_train_dataset=False,
    use_grain=True,
    dataloader_num_workers=0,
    use_wandb=False,
    use_esurge_generation=False,
    progress_bar_type="json",
    low_mem_usage=True,
    track_memory=False,
    do_eval=True,
    resume_if_possible=False,
    save_tpu_preemption_checkpoints=False,
    save_optimizer_state=True,
    do_last_save=True,
    verbose=True,
)

trainer = RecordingTrainer(
    arguments=arguments,
    model=model,
    dataset_train=train_dataset,
    dataset_eval=eval_dataset,
)
train_started = time.time()
result = trainer.train()
train_seconds = time.time() - train_started
completed_steps = int(np.asarray(jax.device_get(result.state.step)))
if completed_steps != TRAIN_STEPS:
    raise RuntimeError(f"Expected {TRAIN_STEPS} optimizer steps, got {completed_steps}")

metric_history = list(trainer.recorded_metrics)
step_rows = train_metric_rows(metric_history)
if len(step_rows) != TRAIN_STEPS:
    raise RuntimeError(
        f"Expected {TRAIN_STEPS} train metric rows, got {len(step_rows)}"
    )
warm_rows = step_rows[-WARM_STEPS:]
warm_times = [float(row["train-mlperf/execution_time"]) for row in warm_rows]
warm_throughputs = [float(row["train-mlperf/throughput"]) for row in warm_rows]
warm_tokens_per_second = statistics.median(warm_throughputs)
warm_time_ratio = max(warm_times) / min(warm_times)
train_losses = [float(row["train/loss"]) for row in step_rows]
if not all(math.isfinite(value) for value in train_losses):
    raise RuntimeError(f"Non-finite training loss: {train_losses}")

pre_reload_eval_loss = last_eval_loss(metric_history)
pre_reload_graph_dtypes = tree_dtype_stats(result.state.graphstate)
pre_reload_optimizer_dtypes = tree_dtype_stats(result.state.opt_state)
checkpoint_path = Path(result.checkpoint_path)
if not checkpoint_path.exists():
    raise RuntimeError(f"EasyDeL reported a missing checkpoint: {checkpoint_path}")
checkpoint_sha, checkpoint_files, checkpoint_bytes = checkpoint_digest(checkpoint_path)
emit(
    "trained_and_saved",
    checkpoint_path=str(checkpoint_path),
    checkpoint_sha256=checkpoint_sha,
    checkpoint_files=checkpoint_files,
    checkpoint_bytes=checkpoint_bytes,
    train_seconds_including_compile_eval_and_save=train_seconds,
    warm_times=warm_times,
    warm_throughputs=warm_throughputs,
    warm_tokens_per_second=warm_tokens_per_second,
    train_losses=train_losses,
    eval_loss=pre_reload_eval_loss,
    graph_dtypes=pre_reload_graph_dtypes,
    optimizer_dtypes=pre_reload_optimizer_dtypes,
)

# Force the restore to stand on its own rather than retaining the live state by accident.
del result
del trainer
del model
gc.collect()

reload_started = time.time()
reloaded_state = ed.EasyDeLState.load_state(
    load_directory=checkpoint_path,
    dtype=jnp.bfloat16,
    param_dtype=jnp.float32,
    precision=jax.lax.Precision.DEFAULT,
    sharding_axis_dims=(8, 1, 1, 1, 1),
    auto_shard_model=True,
    tx_template=arguments.get_tx_template(),
    verbose=True,
)
reload_seconds = time.time() - reload_started
reloaded_step = int(np.asarray(jax.device_get(reloaded_state.step)))
reloaded_graph_dtypes = tree_dtype_stats(reloaded_state.graphstate)
reloaded_optimizer_dtypes = tree_dtype_stats(reloaded_state.opt_state)

reload_trainer = RecordingTrainer(
    arguments=arguments,
    model_state=reloaded_state,
    dataset_train=train_dataset,
    dataset_eval=eval_dataset,
)
list(reload_trainer.eval(reloaded_state))
post_reload_eval_loss = last_eval_loss(reload_trainer.recorded_metrics)
reload_loss_delta = abs(post_reload_eval_loss - pre_reload_eval_loss)

graph_float_dtypes = {
    dtype
    for dtype in reloaded_graph_dtypes["counts"]
    if dtype in {"float16", "bfloat16", "float32", "float64"}
}
optimizer_float_dtypes = {
    dtype
    for dtype in reloaded_optimizer_dtypes["counts"]
    if dtype in {"float16", "bfloat16", "float32", "float64"}
}
checks = {
    "warm_throughput": warm_tokens_per_second >= MINIMUM_WARM_TOKENS_PER_SECOND,
    "warm_step_stability": warm_time_ratio <= MAXIMUM_WARM_TIME_RATIO,
    "finite_losses": all(math.isfinite(value) for value in train_losses),
    "checkpoint_reloaded": reloaded_step == TRAIN_STEPS,
    "validation_reproduced": reload_loss_delta <= MAXIMUM_RELOAD_LOSS_DELTA,
    "fp32_parameters": graph_float_dtypes == {"float32"},
    "fp32_optimizer_state": optimizer_float_dtypes == {"float32"},
}
ok = all(checks.values())
visited_tokens = completed_steps * GLOBAL_BATCH * SEQUENCE_LENGTH
report = {
    "ok": ok,
    "checks": checks,
    **hardware,
    "parameters": base_manifest["parameter_count"],
    "pretrained_checkpoint": base_manifest["model"],
    "model_sha256": actual_model_sha,
    "train_sha256": actual_train_sha,
    "validation_sha256": actual_validation_sha,
    "code_sha256": code_sha256,
    "real_corpus": True,
    "sequence_length": SEQUENCE_LENGTH,
    "global_batch": GLOBAL_BATCH,
    "per_device_batch": GLOBAL_BATCH // jax.device_count(),
    "tokens_per_step": GLOBAL_BATCH * SEQUENCE_LENGTH,
    "steps": completed_steps,
    "visited_tokens": visited_tokens,
    "train_seconds_including_compile_eval_and_save": train_seconds,
    "end_to_end_tokens_per_second": visited_tokens / train_seconds,
    "warm_step_times": warm_times,
    "warm_step_throughputs": warm_throughputs,
    "warm_tokens_per_second_median": warm_tokens_per_second,
    "warm_time_ratio": warm_time_ratio,
    "minimum_warm_tokens_per_second": MINIMUM_WARM_TOKENS_PER_SECOND,
    "train_losses": train_losses,
    "pre_reload_eval_loss": pre_reload_eval_loss,
    "post_reload_eval_loss": post_reload_eval_loss,
    "reload_loss_delta": reload_loss_delta,
    "compute_dtype": "bfloat16",
    "parameter_dtype": "float32",
    "optimizer_momentum_dtype": "float32",
    "gradient_checkpointing": "none",
    "attention": "auto (blocksparse/Splash on TPU v5e)",
    "checkpoint_path": str(checkpoint_path),
    "checkpoint_sha256": checkpoint_sha,
    "checkpoint_files": checkpoint_files,
    "checkpoint_bytes": checkpoint_bytes,
    "reload_seconds": reload_seconds,
    "reloaded_step": reloaded_step,
    "pre_reload_graph_dtypes": pre_reload_graph_dtypes,
    "pre_reload_optimizer_dtypes": pre_reload_optimizer_dtypes,
    "reloaded_graph_dtypes": reloaded_graph_dtypes,
    "reloaded_optimizer_dtypes": reloaded_optimizer_dtypes,
}
report_path = Path("/kaggle/working/tpu-91m-production-gate-report.json")
report_path.write_text(json.dumps(report, indent=2) + "\n")
emit("complete", **report)

if not ok:
    failed = [name for name, passed in checks.items() if not passed]
    raise RuntimeError(f"TPU production gate failed: {failed}")

print("TPU_V5E8_91M_PRODUCTION_GATE_OK", flush=True)
