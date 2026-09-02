"""h1jax resumable Falcon-H1-Tiny continued pretraining on Kaggle TPU v5e-8.

Full-weight causal-LM training of the exact 91,131,072-parameter checkpoint on the sealed
corpus-v1 token stream with FP32 master parameters and AdamW moments, BF16 compute, explicit
SPMD sharding (parameters and optimizer state replicated, batch sharded over the eight chips),
asynchronous dispatch, developmental checkpoints with optimizer state, a fixed validation
slice, and a wall-clock budget guard that saves a resumable checkpoint and exits cleanly.

Resume: attach a previous run's output as a kernel source; the script picks the highest-token
`trainer_state.json` whose settings match and continues from it.

The data traversal is h1jax's deterministic affine permutation with seed HGHOST_CPT_SEED, the
same order hbox consumed, so matched-exposure comparisons remain valid up to batch alignment.
"""

from __future__ import annotations

import glob
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

LOCAL = os.environ.get("HGHOST_LOCAL") == "1"
if not LOCAL:
    os.environ.setdefault("JAX_COMPILATION_CACHE_DIR", "/kaggle/working/jax-cache")

RUN_NAME = os.environ.get("HGHOST_CPT_RUN_NAME", "leaf-e1-decay10")
OUTPUT = Path(os.environ.get("HGHOST_CPT_OUTPUT", f"/kaggle/working/{RUN_NAME}"))
OUTPUT.mkdir(parents=True, exist_ok=True)


def emit(event: str, **values: Any) -> None:
    print(json.dumps({"event": event, **values}, default=str), flush=True)


def exactly_one(pattern: str) -> Path:
    matches = [Path(p) for p in glob.glob(pattern, recursive=True) if Path(p).is_file()]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {pattern!r}, found: {matches}")
    return matches[0]


if not LOCAL:
    wheel = exactly_one("/kaggle/input/**/hghost_jax-*.whl")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-deps", "--quiet", str(wheel)],
        check=True,
    )
    emit("wheel", path=str(wheel))

import jax
import jax.numpy as jnp
import numpy as np
import optax
from flax import serialization
from h1jax.checkpoint import load_hf_params
from h1jax.config import FalconH1Config
from h1jax.data import TokenStream, ValidationStream
from h1jax.model import causal_lm_loss, count_parameters, falcon_h1_forward
from h1jax.train import (
    _atomic_write_json,
    _resume_compatibility,
    _save_training_checkpoint,
)
from jax.sharding import Mesh, NamedSharding
from jax.sharding import PartitionSpec as P

# ----------------------------------------------------------------------------- settings

PER_CHIP = int(os.environ.get("HGHOST_CPT_PER_CHIP", "64"))
SEQ_LEN = int(os.environ.get("HGHOST_CPT_SEQ", "512"))
REMAT = os.environ.get("HGHOST_CPT_REMAT", "1") == "1"
TOTAL_TOKENS = int(os.environ.get("HGHOST_CPT_TOTAL_TOKENS", "411845733"))
LEARNING_RATE = float(os.environ.get("HGHOST_CPT_LR", "1e-4"))
WARMUP_TOKENS = int(os.environ.get("HGHOST_CPT_WARMUP_TOKENS", "10000000"))
MIN_LR_RATIO = float(os.environ.get("HGHOST_CPT_MIN_LR_RATIO", "0.1"))
WEIGHT_DECAY = float(os.environ.get("HGHOST_CPT_WEIGHT_DECAY", "0.1"))
MAX_GRAD_NORM = float(os.environ.get("HGHOST_CPT_MAX_GRAD_NORM", "1.0"))
SAVE_TOKENS = [
    int(v)
    for v in os.environ.get(
        "HGHOST_CPT_SAVE_TOKENS",
        "",
    ).split(",")
    if v
]
EVAL_EVERY_TOKENS = int(os.environ.get("HGHOST_CPT_EVAL_EVERY_TOKENS", "5000000"))
EVAL_SEQUENCES = int(os.environ.get("HGHOST_CPT_EVAL_SEQUENCES", "512"))
FIXED_EVAL_SEQUENCES = int(os.environ.get("HGHOST_CPT_FIXED_EVAL_SEQUENCES", "32"))
LOG_STEPS = int(os.environ.get("HGHOST_CPT_LOG_STEPS", "10"))
MAX_MINUTES = float(os.environ.get("HGHOST_CPT_MAX_MINUTES", "60"))
BUDGET_MARGIN_MINUTES = float(os.environ.get("HGHOST_CPT_BUDGET_MARGIN_MINUTES", "6"))
SEED = int(os.environ.get("HGHOST_CPT_SEED", "0"))
SCHEDULE = os.environ.get("HGHOST_CPT_SCHEDULE", "wsd")  # cosine | wsd
DECAY_TOKENS = int(
    os.environ.get("HGHOST_CPT_DECAY_TOKENS", "37440521")
)  # wsd: decay over the last N tokens
BRANCH_FROM = os.environ.get(
    "HGHOST_CPT_BRANCH_FROM", "/kaggle/input/**/trunk-wsd-lr1e-4-seed0/tokens-000374405212/trainer_state.json"
)  # trunk checkpoint dir to branch from
REQUIRE_TPU = os.environ.get("HGHOST_REQUIRE_TPU", "0" if LOCAL else "1") == "1"
LAYER_SCAN = os.environ.get("HGHOST_LAYER_SCAN", "1") == "1"
RESUME_GLOBS = os.environ.get(
    "HGHOST_CPT_RESUME_GLOBS",
    f"/kaggle/input/**/trainer_state.json,{OUTPUT}/**/trainer_state.json",
).split(",")
MIR_WEIGHT = float(os.environ.get("HGHOST_CPT_MIR_WEIGHT", "0"))  # 0 = plain NTP
MIR_MAX_RATIO = float(os.environ.get("HGHOST_CPT_MIR_MAX_RATIO", "0.5"))
MIR_MASK_ID = int(
    os.environ.get("HGHOST_CPT_MIR_MASK_ID", "0")
)  # <|pad|>, never in the corpus
HBOX_BASE_EVAL = {"loss": 3.745613, "accuracy": 0.349426}

started_wall = time.monotonic()


def memory_probe(tag: str) -> None:
    info: dict[str, Any] = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith(("MemTotal", "MemAvailable")):
                key, value = line.split(":")
                info[key] = int(value.split()[0]) * 1024
    except OSError:
        pass
    for path in (
        "/sys/fs/cgroup/memory.max",
        "/sys/fs/cgroup/memory/memory.limit_in_bytes",
    ):
        try:
            info["cgroup_limit"] = Path(path).read_text().strip()
            break
        except OSError:
            pass
    for path in (
        "/sys/fs/cgroup/memory.current",
        "/sys/fs/cgroup/memory/memory.usage_in_bytes",
    ):
        try:
            info["cgroup_current"] = Path(path).read_text().strip()
            break
        except OSError:
            pass
    try:
        info["rss_bytes"] = int(
            Path("/proc/self/statm").read_text().split()[1]
        ) * os.sysconf("SC_PAGE_SIZE")
    except (OSError, ValueError):
        pass
    emit("memory", tag=tag, **info)


# ----------------------------------------------------------------------------- hardware

hardware = {
    "jax": jax.__version__,
    "backend": jax.default_backend(),
    "device_count": jax.device_count(),
    "devices": [str(d) for d in jax.devices()],
    "device_kind": jax.devices()[0].device_kind,
}
emit("hardware", **hardware, layer_scan=LAYER_SCAN)
memory_probe("start")
if REQUIRE_TPU and (hardware["backend"] != "tpu" or hardware["device_count"] != 8):
    raise RuntimeError("This run requires the complete TPU v5e-8 slice")
DEVICE_COUNT = hardware["device_count"]
GLOBAL_BATCH = PER_CHIP * DEVICE_COUNT
TOKENS_PER_STEP = GLOBAL_BATCH * SEQ_LEN
TOTAL_STEPS = math.ceil(TOTAL_TOKENS / TOKENS_PER_STEP)
WARMUP_STEPS = max(1, math.ceil(WARMUP_TOKENS / TOKENS_PER_STEP))

# ----------------------------------------------------------------------------- inputs


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if LOCAL:
    base_root = Path(os.environ["HGHOST_BASE_DIR"]).resolve()
    corpus_root = Path(os.environ["HGHOST_CORPUS_DIR"]).resolve()
else:
    base_root = exactly_one("/kaggle/input/**/preflight-manifest.json").parent
    corpus_root = exactly_one("/kaggle/input/**/validation-report.json").parent
base_manifest = json.loads((base_root / "preflight-manifest.json").read_text())
corpus_report = json.loads((corpus_root / "validation-report.json").read_text())
train_path = corpus_root / "train.bin"
validation_path = corpus_root / "validation.bin"
hashes = {
    "model": sha256(base_root / "model.safetensors"),
    "train": sha256(train_path),
    "validation": sha256(validation_path),
    "code": sha256(Path(__file__)),
}
expected = {
    "model": base_manifest["files"]["model.safetensors"]["sha256"],
    "train": corpus_report["splits"]["train"]["sha256"],
    "validation": corpus_report["splits"]["validation"]["sha256"],
}
for key, value in expected.items():
    if hashes[key] != value:
        raise RuntimeError(f"{key} checksum mismatch: {hashes[key]} != {value}")
emit(
    "inputs_verified", base_root=str(base_root), corpus_root=str(corpus_root), **hashes
)

cfg = FalconH1Config.from_json(base_root / "config.json")

# ----------------------------------------------------------------------------- settings record

resume_settings = {
    "sequence_length": SEQ_LEN,
    "per_device_batch": PER_CHIP,
    "accumulation_steps": 1,
    "tokens_per_step": TOKENS_PER_STEP,
    "run_batch_aligned_tokens": TOTAL_STEPS * TOKENS_PER_STEP,
    "batch_alignment_overhead_tokens": TOTAL_STEPS * TOKENS_PER_STEP - TOTAL_TOKENS,
    "seed": SEED,
    "total_tokens": TOTAL_TOKENS,
    "warmup_tokens": WARMUP_TOKENS,
    "learning_rate": LEARNING_RATE,
    "min_learning_rate_ratio": MIN_LR_RATIO,
    "weight_decay": WEIGHT_DECAY,
    "max_gradient_norm": MAX_GRAD_NORM,
    "gradient_checkpointing": REMAT,
    "schedule": SCHEDULE,
    "decay_tokens": DECAY_TOKENS,
    "mir_weight": MIR_WEIGHT,
    "mir_max_ratio": MIR_MAX_RATIO,
}

# ----------------------------------------------------------------------------- resume discovery


def find_resume() -> tuple[Path | None, dict | None]:
    best: tuple[int, Path, dict] | None = None
    for pattern in RESUME_GLOBS:
        for match in glob.glob(pattern.strip(), recursive=True):
            path = Path(match)
            try:
                state = json.loads(path.read_text())
            except (OSError, ValueError) as exc:
                emit(
                    "resume_candidate_unreadable",
                    path=str(path),
                    reason=repr(exc)[:200],
                )
                continue
            if state.get("run_name") != RUN_NAME:
                continue
            try:
                _resume_compatibility(state, resume_settings)
            except ValueError as exc:
                emit("resume_candidate_rejected", path=str(path), reason=str(exc)[:300])
                continue
            tokens = int(state.get("tokens", 0))
            if best is None or tokens > best[0]:
                best = (tokens, path.parent, state)
    if best is None:
        return None, None
    return best[1], best[2]


if BRANCH_FROM:
    # Branch: continue data order and optimizer moments from a trunk checkpoint, but as a NEW run with
    # its own name, schedule, and total; no compatibility check against the trunk's settings.
    branch_matches = sorted(
        Path(m).parent
        for m in glob.glob(BRANCH_FROM, recursive=True)
        if m.endswith("trainer_state.json")
    )
    if branch_matches:
        if len(branch_matches) != 1:
            raise RuntimeError(
                f"HGHOST_CPT_BRANCH_FROM matched several checkpoints: {branch_matches}"
            )
        resume_dir = branch_matches[0]
    else:
        resume_dir = Path(BRANCH_FROM).resolve()
    resume_state = json.loads((resume_dir / "trainer_state.json").read_text())
    if int(resume_state["tokens_per_step"]) != TOKENS_PER_STEP:
        raise RuntimeError(
            f"branch requires the trunk's tokens_per_step ({resume_state['tokens_per_step']}), got {TOKENS_PER_STEP}"
        )
    if int(resume_state.get("seed", SEED)) != SEED:
        raise RuntimeError("branch requires the trunk's data seed")
    emit(
        "branch",
        path=str(resume_dir),
        step=resume_state["step"],
        tokens=resume_state["tokens"],
        trunk_run=resume_state.get("run_name"),
    )
else:
    resume_dir, resume_state = find_resume()

# ----------------------------------------------------------------------------- model and optimizer

mesh = Mesh(np.array(jax.devices()), axis_names=("data",))
REPLICATED = NamedSharding(mesh, P())
SHARDED = NamedSharding(mesh, P("data"))

if resume_dir is not None:
    host_params = load_hf_params(resume_dir, dtype=jnp.float32)
    start_step = int(resume_state["step"])
    emit("resume", path=str(resume_dir), step=start_step, tokens=resume_state["tokens"])
else:
    host_params = load_hf_params(base_root, dtype=jnp.float32)
    start_step = 0
host_params = {k: np.asarray(v) for k, v in host_params.items()}
parameter_count = count_parameters(host_params)
if parameter_count != base_manifest["parameter_count"]:
    raise RuntimeError(f"parameter count {parameter_count} != manifest")

if SCHEDULE == "cosine":
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=LEARNING_RATE,
        warmup_steps=min(WARMUP_STEPS, TOTAL_STEPS),
        decay_steps=max(TOTAL_STEPS, WARMUP_STEPS + 1),
        end_value=LEARNING_RATE * MIN_LR_RATIO,
    )
elif SCHEDULE == "wsd":
    # Warmup, stable at peak, then decay over the last DECAY_TOKENS of the run. With DECAY_TOKENS=0 this is
    # a pure trunk (never decays); a leaf branches from a trunk checkpoint with DECAY_TOKENS > 0.
    DECAY_STEPS = min(math.ceil(DECAY_TOKENS / TOKENS_PER_STEP), TOTAL_STEPS)
    decay_start = TOTAL_STEPS - DECAY_STEPS
    warmup = optax.linear_schedule(
        0.0, LEARNING_RATE, max(1, min(WARMUP_STEPS, decay_start))
    )
    stable = optax.constant_schedule(LEARNING_RATE)
    decay = optax.cosine_decay_schedule(
        LEARNING_RATE, max(1, DECAY_STEPS), alpha=MIN_LR_RATIO
    )
    schedule = optax.join_schedules(
        [warmup, stable, decay],
        boundaries=[min(WARMUP_STEPS, decay_start), decay_start],
    )
else:
    raise ValueError(f"unknown HGHOST_CPT_SCHEDULE {SCHEDULE!r}")
decay_mask = {key: value.ndim >= 2 for key, value in host_params.items()}
optimizer = optax.chain(
    optax.clip_by_global_norm(MAX_GRAD_NORM),
    optax.adamw(
        learning_rate=schedule,
        b1=0.9,
        b2=0.95,
        eps=1e-8,
        weight_decay=WEIGHT_DECAY,
        mask=decay_mask,
    ),
)
host_opt_state = optimizer.init(host_params)
if resume_dir is not None:
    host_opt_state = serialization.from_bytes(
        host_opt_state, (resume_dir / "optimizer.msgpack").read_bytes()
    )

params = jax.device_put(host_params, REPLICATED)
opt_state = jax.device_put(host_opt_state, REPLICATED)
del host_params, host_opt_state


def loss_fn(p, tokens):
    return causal_lm_loss(
        p,
        tokens,
        cfg,
        compute_dtype=jnp.bfloat16,
        gradient_checkpointing=REMAT,
        layer_scan=LAYER_SCAN,
    )


def masked_input_loss(p, tokens, key):
    """Masked-input regularization: predict the clean next tokens from corrupted inputs.

    Following the data-constrained pretraining recipe, each sequence draws a mask ratio uniformly
    from [0, MIR_MAX_RATIO] and that fraction of its input positions is replaced by MIR_MASK_ID; the
    targets are unchanged. Returned as an auxiliary loss weighted by MIR_WEIGHT.
    """

    inputs = tokens[:, :-1]
    labels = tokens[:, 1:]
    ratio_key, mask_key = jax.random.split(key)
    ratios = jax.random.uniform(
        ratio_key, (inputs.shape[0], 1), minval=0.0, maxval=MIR_MAX_RATIO
    )
    mask = jax.random.uniform(mask_key, inputs.shape) < ratios
    corrupted = jnp.where(mask, jnp.asarray(MIR_MASK_ID, inputs.dtype), inputs)
    logits = falcon_h1_forward(
        p,
        corrupted,
        cfg,
        compute_dtype=jnp.bfloat16,
        gradient_checkpointing=REMAT,
        layer_scan=LAYER_SCAN,
    ).astype(jnp.float32)
    log_normalizer = jax.nn.logsumexp(logits, axis=-1)
    selected = jnp.take_along_axis(logits, labels[..., None], axis=-1)[..., 0]
    return jnp.mean(log_normalizer - selected), jnp.mean(mask.astype(jnp.float32))


MIR_KEY = jax.random.PRNGKey(SEED + 1_000_003)


def _train_step(p, s, tokens, step):
    def total_loss(p_):
        loss, metrics = loss_fn(p_, tokens)
        metrics = dict(metrics)
        if MIR_WEIGHT > 0:
            mir_loss, masked_fraction = masked_input_loss(
                p_, tokens, jax.random.fold_in(MIR_KEY, step)
            )
            metrics["mir_loss"] = mir_loss
            metrics["mir_masked_fraction"] = masked_fraction
            loss = loss + MIR_WEIGHT * mir_loss
        metrics["total_loss"] = loss
        return loss, metrics

    (_, metrics), grads = jax.value_and_grad(total_loss, has_aux=True)(p)
    updates, s = optimizer.update(grads, s, p)
    p = optax.apply_updates(p, updates)
    metrics["gradient_norm"] = optax.global_norm(grads)
    return p, s, metrics


train_step = jax.jit(
    _train_step,
    in_shardings=(REPLICATED, REPLICATED, SHARDED, REPLICATED),
    out_shardings=(REPLICATED, REPLICATED, REPLICATED),
    donate_argnums=(0, 1),
)


def _eval_step(p, tokens):
    _, metrics = causal_lm_loss(
        p,
        tokens,
        cfg,
        compute_dtype=jnp.bfloat16,
        gradient_checkpointing=False,
        layer_scan=LAYER_SCAN,
    )
    return metrics


eval_step = jax.jit(
    _eval_step, in_shardings=(REPLICATED, SHARDED), out_shardings=REPLICATED
)

# ----------------------------------------------------------------------------- data

train_stream = TokenStream(train_path, SEQ_LEN, seed=SEED)
validation_stream = ValidationStream(validation_path, SEQ_LEN)
EVAL_SEQUENCES = min(EVAL_SEQUENCES, validation_stream.sequence_count)


def train_batch(step: int) -> jax.Array:
    rows = train_stream.batch(
        step * GLOBAL_BATCH,
        device_count=1,
        accumulation_steps=1,
        per_device_batch=GLOBAL_BATCH,
    ).reshape(GLOBAL_BATCH, SEQ_LEN + 1)
    return jax.device_put(rows, SHARDED)


def evaluate(p) -> dict[str, float]:
    """Mean loss over the first EVAL_SEQUENCES validation sequences, plus the fixed 32-sequence slice."""
    chunks = max(1, EVAL_SEQUENCES // GLOBAL_BATCH)
    totals = {"loss": 0.0, "accuracy": 0.0}
    for index in range(chunks):
        rows = validation_stream.batch(
            index * GLOBAL_BATCH,
            device_count=1,
            accumulation_steps=1,
            per_device_batch=GLOBAL_BATCH,
        ).reshape(GLOBAL_BATCH, SEQ_LEN + 1)
        metrics = jax.device_get(eval_step(p, jax.device_put(rows, SHARDED)))
        for key in totals:
            totals[key] += float(metrics[key])
    result = {key: value / chunks for key, value in totals.items()}
    result["sequences"] = chunks * GLOBAL_BATCH
    fixed_rows = validation_stream.batch(
        0, device_count=1, accumulation_steps=1, per_device_batch=FIXED_EVAL_SEQUENCES
    ).reshape(FIXED_EVAL_SEQUENCES, SEQ_LEN + 1)
    fixed = jax.device_get(eval_step(p, jax.device_put(fixed_rows, SHARDED)))
    result["fixed_loss"] = float(fixed["loss"])
    result["fixed_accuracy"] = float(fixed["accuracy"])
    result["fixed_sequences"] = FIXED_EVAL_SEQUENCES
    return result


# ----------------------------------------------------------------------------- manifest

save_thresholds = sorted(
    {t for t in SAVE_TOKENS if 0 < t < TOTAL_TOKENS} | {TOTAL_TOKENS}
)
start_tokens = min(start_step * TOKENS_PER_STEP, TOTAL_TOKENS)
save_thresholds = [t for t in save_thresholds if t > start_tokens]
next_eval = (start_tokens // EVAL_EVERY_TOKENS + 1) * EVAL_EVERY_TOKENS
run_manifest = {
    "schema_version": 1,
    "run_name": RUN_NAME,
    "config": cfg.to_dict(),
    "parameters": parameter_count,
    **hardware,
    **resume_settings,
    "global_batch": GLOBAL_BATCH,
    "total_steps": TOTAL_STEPS,
    "warmup_steps": WARMUP_STEPS,
    "hashes": hashes,
    "pretrained_checkpoint": base_manifest["model"],
    "resumed_from": str(resume_dir) if resume_dir else None,
    "branched": bool(BRANCH_FROM),
    "epochs_of_corpus": TOTAL_TOKENS / max(1, train_stream.sequence_count * SEQ_LEN),
    "start_step": start_step,
    "start_tokens": start_tokens,
    "save_thresholds": save_thresholds,
    "eval_every_tokens": EVAL_EVERY_TOKENS,
    "eval_sequences": EVAL_SEQUENCES,
    "max_minutes": MAX_MINUTES,
}
_atomic_write_json(OUTPUT / "run-manifest.json", run_manifest)
emit(
    "start", **{k: v for k, v in run_manifest.items() if k not in ("config", "devices")}
)


def save(step: int, exposed: int, label: str, extra: dict | None = None) -> Path:
    checkpoint = OUTPUT / f"tokens-{exposed:012d}"
    if checkpoint.exists():
        checkpoint = OUTPUT / f"tokens-{exposed:012d}-{label}"
    _save_training_checkpoint(
        checkpoint,
        params,
        opt_state,
        cfg,
        {
            **resume_settings,
            "run_name": RUN_NAME,
            "step": step,
            "tokens": exposed,
            "batch_aligned_tokens": step * TOKENS_PER_STEP,
            "label": label,
            "parameters": parameter_count,
            "elapsed_seconds": time.monotonic() - started_wall,
            "code_sha256": hashes["code"],
            "branched_from": str(resume_dir) if BRANCH_FROM else None,
            **(extra or {}),
        },
        tokenizer_dir=base_root,
    )
    emit("checkpoint", path=str(checkpoint), step=step, tokens=exposed, label=label)
    return checkpoint


# ----------------------------------------------------------------------------- baseline eval

if start_step == 0:
    base_eval = evaluate(params)
    emit(
        "validation",
        step=0,
        tokens=0,
        **base_eval,
        fixed_loss_delta_vs_hbox=base_eval["fixed_loss"] - HBOX_BASE_EVAL["loss"],
    )

# ----------------------------------------------------------------------------- train loop

memory_probe("before_train_loop")
interval_started = time.monotonic()
interval_tokens = 0
pending_metrics = None
stopped_for_budget = False
step = start_step
for step in range(start_step, TOTAL_STEPS):
    params, opt_state, pending_metrics = train_step(
        params, opt_state, train_batch(step), jnp.asarray(step, jnp.int32)
    )
    exposed = min((step + 1) * TOKENS_PER_STEP, TOTAL_TOKENS)
    interval_tokens += TOKENS_PER_STEP
    completed = step + 1

    if completed % LOG_STEPS == 0 or step == start_step:
        host = jax.device_get(pending_metrics)
        if step == start_step:
            memory_probe("after_first_step")
        now = time.monotonic()
        values = {
            k: float(host[k])
            for k in (
                "loss",
                "accuracy",
                "gradient_norm",
                "total_loss",
                "mir_loss",
                "mir_masked_fraction",
            )
            if k in host
        }
        if not all(math.isfinite(v) for v in values.values()):
            save(completed, exposed, "nonfinite")
            raise FloatingPointError(
                f"Non-finite training metrics at step {completed}: {values}"
            )
        emit(
            "train",
            step=completed,
            tokens=exposed,
            **values,
            learning_rate=float(schedule(step)),
            tokens_per_second=interval_tokens / max(now - interval_started, 1e-9),
            elapsed_minutes=(now - started_wall) / 60.0,
        )
        interval_started, interval_tokens = now, 0

    if exposed >= next_eval and exposed < TOTAL_TOKENS:
        jax.block_until_ready(params)
        metrics = evaluate(params)
        emit("validation", step=completed, tokens=exposed, **metrics)
        next_eval += EVAL_EVERY_TOKENS

    while save_thresholds and exposed >= save_thresholds[0]:
        threshold = save_thresholds.pop(0)
        jax.block_until_ready(params)
        save(completed, exposed, "scheduled", {"requested_token_threshold": threshold})

    elapsed_minutes = (time.monotonic() - started_wall) / 60.0
    if (
        elapsed_minutes >= MAX_MINUTES - BUDGET_MARGIN_MINUTES
        and exposed < TOTAL_TOKENS
    ):
        jax.block_until_ready(params)
        save(completed, exposed, "budget")
        stopped_for_budget = True
        emit(
            "budget_stop",
            step=completed,
            tokens=exposed,
            elapsed_minutes=elapsed_minutes,
        )
        break

jax.block_until_ready(params)
final_step = step + 1 if TOTAL_STEPS > start_step else start_step
final_tokens = min(final_step * TOKENS_PER_STEP, TOTAL_TOKENS)
if not stopped_for_budget:
    final_eval = evaluate(params)
    emit("validation", step=final_step, tokens=final_tokens, **final_eval, final=True)
_atomic_write_json(
    OUTPUT
    / ("training-complete.json" if not stopped_for_budget else "training-paused.json"),
    {
        "completed": not stopped_for_budget,
        "run_name": RUN_NAME,
        "steps": final_step,
        "tokens": final_tokens,
        "tokens_per_step": TOKENS_PER_STEP,
        "elapsed_seconds": time.monotonic() - started_wall,
    },
)
print("TPU_H1JAX_CPT_PAUSED" if stopped_for_budget else "TPU_H1JAX_CPT_OK", flush=True)
