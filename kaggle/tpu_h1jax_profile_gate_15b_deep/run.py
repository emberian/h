"""h1jax TPU profile gate: measure real Falcon-H1-1.5B-Deep training throughput on v5e-8.

Copy of kaggle/tpu_h1jax_profile_gate_05b/run.py for tiiuae/Falcon-H1-1.5B-Deep-Base (66 layers,
hidden 1280, vocab 65,536, untied head) on the 65,536-vocabulary room corpus. The question this copy
answers is memory: 1.55B parameters with an FP32 master copy and AdamW state is ~18.6 GB replicated
per chip before activations, against 16 GiB of HBM, so the shape sweep starts at 4x512 with remat.

This is a measurement kernel, not a training run. For each requested shape it compiles the
full FP32-master / BF16-compute AdamW step under explicit SPMD sharding (parameters and
optimizer state replicated, batch sharded across the eight chips), records XLA's memory
and cost analysis BEFORE executing, then times warm steps with asynchronous dispatch. It
also micro-benchmarks the step's components (attention, Mamba mixer, SSD scan, MLP,
embedding/head/loss, and a plain matmul roofline) so the time budget is decomposed without
needing xprof, writes a short profiler trace for offline analysis, checks the base
checkpoint's validation loss against the hbox Transformers measurement, and finishes with a
few real-learning-rate steps to confirm the loss moves.

Everything is configurable through HGHOST_* environment variables so the identical script
can be exercised on CPU with eight simulated devices before spending TPU minutes.
"""

from __future__ import annotations

import glob
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any

LOCAL = os.environ.get("HGHOST_LOCAL") == "1"
if not LOCAL:
    os.environ.setdefault("JAX_COMPILATION_CACHE_DIR", "/kaggle/working/jax-cache")
OUTPUT = Path(os.environ.get("HGHOST_OUTPUT", "/kaggle/working/h1jax-profile-gate-15b-deep"))
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
from h1jax.checkpoint import load_hf_params
from h1jax.config import FalconH1Config
from h1jax.data import TokenStream, ValidationStream
from h1jax.model import (
    _layer_params,
    attention,
    causal_lm_loss,
    count_parameters,
    mamba,
    mlp,
    ssd_forward,
)
from jax.sharding import Mesh, NamedSharding
from jax.sharding import PartitionSpec as P

# ----------------------------------------------------------------------------- settings

SHAPES = os.environ.get("HGHOST_GATE_SHAPES", "4x512r,8x512r")
WARMUP_STEPS = int(os.environ.get("HGHOST_GATE_WARMUP", "3"))
TIMED_STEPS = int(os.environ.get("HGHOST_GATE_STEPS", "20"))
SYNC_STEPS = int(os.environ.get("HGHOST_GATE_SYNC_STEPS", "5"))
PROFILE_STEPS = int(os.environ.get("HGHOST_PROFILE_STEPS", "3"))
BENCH_ITERS = int(os.environ.get("HGHOST_BENCH_ITERS", "10"))
SANITY_STEPS = int(os.environ.get("HGHOST_SANITY_STEPS", "30"))
WATCHDOG_MINUTES = float(os.environ.get("HGHOST_WATCHDOG_MINUTES", "20"))
HARD_MAX_MINUTES = float(os.environ.get("HGHOST_GATE_MAX_MINUTES", "45"))


# ---- watchdog: a job that stalls (hung collective, post-OOM limbo) must kill itself, never wait to be cancelled.
import threading

_LAST_EVENT = [time.time()]
_ORIGINAL_EMIT = emit


def emit(event: str, **values: Any) -> None:
    _LAST_EVENT[0] = time.time()
    _ORIGINAL_EMIT(event, **values)


def _watchdog(stall_minutes: float, hard_minutes: float) -> None:
    started = time.time()
    while True:
        time.sleep(30)
        now = time.time()
        if now - _LAST_EVENT[0] > stall_minutes * 60:
            _ORIGINAL_EMIT("watchdog", reason="no progress event", minutes=round((now - _LAST_EVENT[0]) / 60, 1))
            sys.stdout.flush(); os._exit(3)
        if now - started > hard_minutes * 60:
            _ORIGINAL_EMIT("watchdog", reason="hard time limit", minutes=round((now - started) / 60, 1))
            sys.stdout.flush(); os._exit(4)


threading.Thread(target=_watchdog, args=(WATCHDOG_MINUTES, HARD_MAX_MINUTES), daemon=True).start()
SANITY_LR = float(os.environ.get("HGHOST_SANITY_LR", "3e-5"))
EVAL_SEQUENCES = int(os.environ.get("HGHOST_EVAL_SEQUENCES", "32"))
EVAL_SEQUENCE_LENGTH = 512
REQUIRE_TPU = os.environ.get("HGHOST_REQUIRE_TPU", "0" if LOCAL else "1") == "1"
LAYER_SCAN = os.environ.get("HGHOST_LAYER_SCAN", "1") == "1"
PEAK_FLOPS_PER_CHIP = float(os.environ.get("HGHOST_PEAK_FLOPS_PER_CHIP", "197e12"))
HBM_BYTES_PER_CHIP = float(
    os.environ.get("HGHOST_HBM_BYTES_PER_CHIP", str(16 * 1024**3))
)
# The hbox Transformers number (research/results/hbox-cpt-10m.md) was measured for the 91M model on the
# 32,768-vocabulary stream; the 1.5B-deep stream is a different tokenization, so no hbox comparison exists.
HBOX_BASE_EVAL: dict[str, float] | None = None


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
    "optax": getattr(optax, "__version__", "unknown"),
    "backend": jax.default_backend(),
    "device_count": jax.device_count(),
    "devices": [str(d) for d in jax.devices()],
    "device_kind": jax.devices()[0].device_kind,
    "python": sys.version.split()[0],
}
emit("hardware", **hardware, layer_scan=LAYER_SCAN)
memory_probe("start")
if REQUIRE_TPU and (hardware["backend"] != "tpu" or hardware["device_count"] != 8):
    raise RuntimeError("This gate requires the complete TPU v5e-8 slice")
DEVICE_COUNT = hardware["device_count"]
PEAK_FLOPS = (
    PEAK_FLOPS_PER_CHIP * DEVICE_COUNT if hardware["backend"] == "tpu" else None
)

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
model_path = base_root / "model.safetensors"
train_path = corpus_root / "train.bin"
validation_path = corpus_root / "validation.bin"
hashes = {
    "model": sha256(model_path),
    "train": sha256(train_path),
    "validation": sha256(validation_path),
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
host_params = {
    k: np.asarray(v) for k, v in load_hf_params(base_root, dtype=jnp.float32).items()
}
parameter_count = count_parameters(host_params)
if parameter_count != base_manifest["parameter_count"]:
    raise RuntimeError(
        f"parameter count {parameter_count} != manifest {base_manifest['parameter_count']}"
    )
memory_probe("model_loaded")
emit(
    "model_loaded",
    parameters=parameter_count,
    layers=cfg.num_hidden_layers,
    hidden=cfg.hidden_size,
)

# ----------------------------------------------------------------------------- analytic FLOPs


def analytic_flops_per_token(
    cfg: FalconH1Config, seq_len: int, params: int
) -> dict[str, float]:
    dense = 6.0 * params
    attn_per_layer_fwd = (
        2.0 * seq_len * cfg.head_dim * cfg.num_attention_heads * 2
    )  # QK^T and AV
    attention_total = attn_per_layer_fwd * 3.0 * cfg.num_hidden_layers
    chunk = min(cfg.mamba_chunk_size, seq_len)
    ssd_per_head_fwd = (
        2.0 * chunk * cfg.mamba_d_state  # C B^T inside the chunk
        + 2.0 * chunk * cfg.mamba_d_head  # masked-decay matrix times X
        + 2.0 * cfg.mamba_d_state * cfg.mamba_d_head  # chunk state B^T X
        + 2.0 * cfg.mamba_d_state * cfg.mamba_d_head  # C times carried state
    )
    ssd_total = ssd_per_head_fwd * cfg.mamba_n_heads * 3.0 * cfg.num_hidden_layers
    return {
        "dense_6n": dense,
        "attention": attention_total,
        "ssd": ssd_total,
        "total": dense + attention_total + ssd_total,
    }


# ----------------------------------------------------------------------------- sharding

mesh = Mesh(np.array(jax.devices()), axis_names=("data",))
REPLICATED = NamedSharding(mesh, P())
SHARDED = NamedSharding(mesh, P("data"))


def put_replicated(tree):
    return jax.device_put(tree, REPLICATED)


# "replicated": every chip holds FP32 masters + AdamW state; "fsdp": each parameter and its optimizer
# moments are sharded along the largest axis divisible by the chip count (XLA gathers weights as used).
PARAM_SHARDING = os.environ.get("HGHOST_PARAM_SHARDING", "fsdp")


def sharding_for(array) -> NamedSharding:
    shape = getattr(array, "shape", ())
    n = mesh.devices.size
    if PARAM_SHARDING != "fsdp" or not shape:
        return REPLICATED
    axis = max(range(len(shape)), key=lambda i: (shape[i] % n == 0, shape[i]))
    if shape[axis] % n != 0:
        return REPLICATED
    spec = [None] * len(shape)
    spec[axis] = "data"
    return NamedSharding(mesh, P(*spec))


def tree_shardings(tree):
    return jax.tree_util.tree_map(sharding_for, tree) if PARAM_SHARDING == "fsdp" else REPLICATED


def put_params(tree):
    if PARAM_SHARDING == "fsdp":
        return jax.tree_util.tree_map(lambda a, sh: jax.device_put(a, sh), tree, tree_shardings(tree))
    return jax.device_put(tree, REPLICATED)


def _stacked_sharding(array) -> NamedSharding:
    """Sharding for a layer-stacked array [L, ...]: the same rule as sharding_for, never the layer axis."""
    shape = getattr(array, "shape", ())
    n = mesh.devices.size
    if PARAM_SHARDING != "fsdp" or len(shape) < 2:
        return REPLICATED
    axis = max(range(1, len(shape)), key=lambda i: (shape[i] % n == 0, shape[i]))
    if shape[axis] % n != 0:
        return REPLICATED
    spec = [None] * len(shape)
    spec[axis] = "data"
    return NamedSharding(mesh, P(*spec))


def _layer_hooks():
    if PARAM_SHARDING != "fsdp":
        return None
    outside = lambda tree: jax.tree_util.tree_map(
        lambda a: jax.lax.with_sharding_constraint(a, _stacked_sharding(a)), tree
    )
    inside = lambda tree: jax.tree_util.tree_map(
        lambda a: jax.lax.with_sharding_constraint(a, REPLICATED), tree
    )
    return (outside, inside)


LAYER_HOOKS = _layer_hooks()


def put_sharded(array):
    return jax.device_put(array, SHARDED)


decay_mask = {key: value.ndim >= 2 for key, value in host_params.items()}


def make_optimizer(learning_rate: float):
    return optax.chain(
        optax.clip_by_global_norm(1.0),
        optax.adamw(
            learning_rate=learning_rate,
            b1=0.9,
            b2=0.95,
            eps=1e-8,
            weight_decay=0.1,
            mask=decay_mask,
        ),
    )


def make_train_step(optimizer, remat: bool, param_shardings, opt_shardings):
    def loss_fn(params, tokens):
        return causal_lm_loss(
            params,
            tokens,
            cfg,
            compute_dtype=jnp.bfloat16,
            gradient_checkpointing=remat,
            layer_scan=LAYER_SCAN,
            layer_hooks=LAYER_HOOKS,
        )

    def step(params, opt_state, tokens):
        (_, metrics), grads = jax.value_and_grad(loss_fn, has_aux=True)(params, tokens)
        updates, opt_state = optimizer.update(grads, opt_state, params)
        params = optax.apply_updates(params, updates)
        metrics = dict(metrics)
        metrics["gradient_norm"] = optax.global_norm(grads)
        return params, opt_state, metrics

    return jax.jit(
        step,
        in_shardings=(param_shardings, opt_shardings, SHARDED),
        out_shardings=(param_shardings, opt_shardings, REPLICATED),
        donate_argnums=(0, 1),
    )


def eval_loss_fn(params, tokens):
    _, metrics = causal_lm_loss(
        params,
        tokens,
        cfg,
        compute_dtype=jnp.bfloat16,
        gradient_checkpointing=False,
        layer_scan=LAYER_SCAN,
        layer_hooks=LAYER_HOOKS,
    )
    return metrics


eval_step = jax.jit(
    eval_loss_fn, in_shardings=(tree_shardings(host_params), SHARDED), out_shardings=REPLICATED
)

# ----------------------------------------------------------------------------- data

train_stream = TokenStream(train_path, 512, seed=0)
validation_stream = ValidationStream(validation_path, EVAL_SEQUENCE_LENGTH)


def host_batch(
    stream: TokenStream, offset: int, global_batch: int, seq_len: int
) -> np.ndarray:
    if stream.sequence_length != seq_len:
        stream = TokenStream(stream.path, seq_len, seed=stream.seed)
    rows = stream.batch(
        offset, device_count=1, accumulation_steps=1, per_device_batch=global_batch
    )
    return rows.reshape(global_batch, seq_len + 1)


def is_oom(exc: BaseException) -> bool:
    text = f"{type(exc).__name__}: {exc}"
    return any(
        marker in text
        for marker in ("RESOURCE_EXHAUSTED", "Out of memory", "OOM", "exhausted")
    )


def analysis_dict(compiled) -> dict[str, Any]:
    out: dict[str, Any] = {}
    try:
        mem = compiled.memory_analysis()
        if mem is not None:
            out["memory"] = {
                name: int(getattr(mem, name))
                for name in (
                    "argument_size_in_bytes",
                    "output_size_in_bytes",
                    "temp_size_in_bytes",
                    "generated_code_size_in_bytes",
                    "alias_size_in_bytes",
                )
                if hasattr(mem, name)
            }
    except Exception as exc:  # noqa: BLE001
        out["memory_error"] = repr(exc)
    try:
        cost = compiled.cost_analysis()
        if isinstance(cost, list):
            cost = cost[0] if cost else {}
        if cost:
            out["cost"] = {
                k: float(v)
                for k, v in cost.items()
                if k in ("flops", "bytes accessed", "transcendentals")
            }
    except Exception as exc:  # noqa: BLE001
        out["cost_error"] = repr(exc)
    return out


def timed_loop(fn, params, opt_state, batches, sync_each: bool):
    times = []
    metrics_out = []
    for tokens in batches:
        started = time.perf_counter()
        params, opt_state, metrics = fn(params, opt_state, tokens)
        if sync_each:
            jax.block_until_ready(params)
            times.append(time.perf_counter() - started)
        metrics_out.append(metrics)
    if not sync_each:
        jax.block_until_ready(params)
    return params, opt_state, metrics_out, times


# ----------------------------------------------------------------------------- base eval parity

report: dict[str, Any] = {
    "schema_version": 1,
    **hardware,
    "parameters": parameter_count,
    "hashes": hashes,
    "peak_flops_per_second": PEAK_FLOPS,
    "shapes": [],
    "components": {},
}

params = put_params(host_params)
eval_rows = host_batch(validation_stream, 0, EVAL_SEQUENCES, EVAL_SEQUENCE_LENGTH)
eval_started = time.perf_counter()
eval_metrics = jax.device_get(eval_step(params, put_sharded(eval_rows)))
eval_seconds = time.perf_counter() - eval_started
base_eval = {k: float(v) for k, v in eval_metrics.items()}
report["base_eval"] = {
    **base_eval,
    "sequences": EVAL_SEQUENCES,
    "predicted_tokens": EVAL_SEQUENCES * EVAL_SEQUENCE_LENGTH,
    "hbox_transformers_bf16": HBOX_BASE_EVAL if EVAL_SEQUENCES == 32 else None,
    "loss_delta_vs_hbox": base_eval["loss"] - HBOX_BASE_EVAL["loss"]
    if EVAL_SEQUENCES == 32 and HBOX_BASE_EVAL is not None
    else None,
    "seconds_including_compile": eval_seconds,
}
emit("base_eval", **report["base_eval"])
memory_probe("after_base_eval")

# ----------------------------------------------------------------------------- shape sweep

shape_specs = []
for token in SHAPES.split(","):
    token = token.strip()
    if not token:
        continue
    remat = token.endswith("r")
    per_chip, seq_len = token.rstrip("r").split("x")
    shape_specs.append(
        {
            "name": token,
            "per_chip": int(per_chip),
            "seq_len": int(seq_len),
            "remat": remat,
        }
    )

throughput_optimizer = make_optimizer(1e-6)
best_shape: dict[str, Any] | None = None
data_offset = 0
for spec in shape_specs:
    per_chip, seq_len, remat = spec["per_chip"], spec["seq_len"], spec["remat"]
    global_batch = per_chip * DEVICE_COUNT
    tokens_per_step = global_batch * seq_len
    flops = analytic_flops_per_token(cfg, seq_len, parameter_count)
    result: dict[str, Any] = {
        **spec,
        "global_batch": global_batch,
        "tokens_per_step": tokens_per_step,
        "analytic_flops_per_token": flops,
        "analytic_flops_per_step": flops["total"] * tokens_per_step,
    }
    emit(
        "shape_start",
        **{k: v for k, v in result.items() if k != "analytic_flops_per_token"},
    )
    params = put_params(host_params)
    host_opt = throughput_optimizer.init(host_params)
    opt_state = put_params(host_opt)
    train_step = make_train_step(
        throughput_optimizer, remat, tree_shardings(host_params), tree_shardings(host_opt)
    )
    try:
        first = put_sharded(
            host_batch(train_stream, data_offset, global_batch, seq_len)
        )
        memory_probe(f"before_compile_{spec['name']}")
        compile_started = time.perf_counter()
        lowered = train_step.lower(params, opt_state, first)
        compiled = lowered.compile()
        memory_probe(f"after_compile_{spec['name']}")
        result["compile_seconds"] = time.perf_counter() - compile_started
        result.update(analysis_dict(compiled))
        if "memory" in result:
            mem = result["memory"]
            per_chip_bytes = mem.get("temp_size_in_bytes", 0) + mem.get(
                "argument_size_in_bytes", 0
            )
            result["predicted_peak_bytes_per_chip"] = per_chip_bytes
            result["predicted_peak_fraction_of_hbm"] = (
                per_chip_bytes / HBM_BYTES_PER_CHIP
            )
        emit(
            "shape_compiled",
            name=spec["name"],
            compile_seconds=result["compile_seconds"],
            memory=result.get("memory"),
            cost=result.get("cost"),
        )

        def batches(count: int, batch_size: int = global_batch, length: int = seq_len):
            global data_offset
            for _ in range(count):
                rows = host_batch(train_stream, data_offset, batch_size, length)
                data_offset += batch_size
                yield put_sharded(rows)

        # Warm-up (includes any residual compilation of the executable path).
        params, opt_state, _, _ = timed_loop(
            compiled, params, opt_state, batches(WARMUP_STEPS), sync_each=True
        )
        # Per-step synchronized timing: exposes step-time spread.
        params, opt_state, sync_metrics, sync_times = timed_loop(
            compiled, params, opt_state, batches(SYNC_STEPS), sync_each=True
        )
        # Asynchronous pipeline timing: the honest production number.
        pipeline_started = time.perf_counter()
        params, opt_state, async_metrics, _ = timed_loop(
            compiled, params, opt_state, batches(TIMED_STEPS), sync_each=False
        )
        pipeline_seconds = time.perf_counter() - pipeline_started
        losses = [
            float(jax.device_get(m["loss"])) for m in sync_metrics + async_metrics
        ]
        step_seconds = pipeline_seconds / TIMED_STEPS
        result.update(
            {
                "sync_step_seconds": sync_times,
                "sync_step_seconds_median": statistics.median(sync_times),
                "async_step_seconds": step_seconds,
                "tokens_per_second": tokens_per_step / step_seconds,
                "losses": losses,
                "finite": all(math.isfinite(v) for v in losses),
                "pass_hours_374m": 374_405_212
                / (tokens_per_step / step_seconds)
                / 3600.0,
            }
        )
        if PEAK_FLOPS:
            result["mfu"] = (
                result["analytic_flops_per_step"] / step_seconds / PEAK_FLOPS
            )
            result["achieved_tflops"] = (
                result["analytic_flops_per_step"] / step_seconds / 1e12
            )
        if PROFILE_STEPS > 0:
            trace_dir = OUTPUT / "profile" / spec["name"]
            try:
                jax.profiler.start_trace(str(trace_dir))
                params, opt_state, _, _ = timed_loop(
                    compiled, params, opt_state, batches(PROFILE_STEPS), sync_each=False
                )
                jax.profiler.stop_trace()
                result["trace_dir"] = str(trace_dir)
            except Exception as exc:  # noqa: BLE001
                result["trace_error"] = repr(exc)
        result["ok"] = result["finite"]
        emit(
            "shape_done",
            **{
                k: v
                for k, v in result.items()
                if k not in ("analytic_flops_per_token", "sync_step_seconds", "losses")
            },
        )
        if result["ok"] and (
            best_shape is None
            or result["tokens_per_second"] > best_shape["tokens_per_second"]
        ):
            best_shape = result
    except Exception as exc:  # noqa: BLE001
        result["ok"] = False
        result["error"] = f"{type(exc).__name__}: {str(exc)[:2000]}"
        result["oom"] = is_oom(exc)
        emit(
            "shape_failed",
            name=spec["name"],
            oom=result["oom"],
            error=result["error"][:400],
        )
        if not result["oom"]:
            traceback.print_exc()
    finally:
        params = None
        opt_state = None
    report["shapes"].append(result)

# ----------------------------------------------------------------------------- component benches

if best_shape is not None:
    b_per_chip, seq_len = best_shape["per_chip"], best_shape["seq_len"]
    global_batch = b_per_chip * DEVICE_COUNT
    layer0 = {k: put_replicated(v) for k, v in _layer_params(host_params, 0).items()}
    rng = np.random.default_rng(0)
    hidden_np = rng.standard_normal(
        (global_batch, seq_len, cfg.hidden_size), dtype=np.float32
    ).astype(jnp.bfloat16)
    hidden = put_sharded(jnp.asarray(hidden_np))
    tokens = put_sharded(host_batch(train_stream, data_offset, global_batch, seq_len))

    def bench(name: str, fn, *args):
        entry: dict[str, Any] = {}
        try:
            jitted = jax.jit(fn)
            started = time.perf_counter()
            jax.block_until_ready(jitted(*args))
            entry["first_call_seconds"] = time.perf_counter() - started
            for _ in range(2):
                jax.block_until_ready(jitted(*args))
            started = time.perf_counter()
            for _ in range(BENCH_ITERS):
                out = jitted(*args)
            jax.block_until_ready(out)
            entry["seconds"] = (time.perf_counter() - started) / BENCH_ITERS
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {str(exc)[:500]}"
        report["components"][name] = entry
        emit("component", name=name, **entry)
        return entry

    def grad_sum(fn):
        def wrapped(p, x):
            def scalar(p_, x_):
                return jnp.sum(fn(p_, x_).astype(jnp.float32))

            g = jax.grad(scalar)(p, x)
            return jax.tree_util.tree_map(lambda v: v[..., :1].sum(), g)

        return wrapped

    attention_bench = bench(
        "attention_layer_fwd_bwd",
        grad_sum(lambda p, x: attention(p, x, cfg)),
        layer0,
        hidden,
    )
    mamba_bench = bench(
        "mamba_mixer_fwd_bwd", grad_sum(lambda p, x: mamba(p, x, cfg)), layer0, hidden
    )
    mlp_bench = bench(
        "mlp_fwd_bwd", grad_sum(lambda p, x: mlp(p, x, cfg)), layer0, hidden
    )

    ssd_hidden = put_sharded(
        jnp.asarray(
            rng.standard_normal(
                (global_batch, seq_len, cfg.mamba_n_heads, cfg.mamba_d_head),
                dtype=np.float32,
            )
        )
    )
    ssd_dt = put_sharded(
        jnp.asarray(
            rng.standard_normal(
                (global_batch, seq_len, cfg.mamba_n_heads), dtype=np.float32
            )
        )
    )
    ssd_b = put_sharded(
        jnp.asarray(
            rng.standard_normal(
                (global_batch, seq_len, cfg.mamba_n_heads, cfg.mamba_d_state),
                dtype=np.float32,
            )
        )
    )
    ssd_c = put_sharded(
        jnp.asarray(
            rng.standard_normal(
                (global_batch, seq_len, cfg.mamba_n_heads, cfg.mamba_d_state),
                dtype=np.float32,
            )
        )
    )
    ssd_a = put_replicated(
        -jnp.exp(jnp.asarray(host_params["model.layers.0.mamba.A_log"]))
    )
    ssd_d = put_replicated(jnp.asarray(host_params["model.layers.0.mamba.D"]))
    ssd_dtb = put_replicated(jnp.asarray(host_params["model.layers.0.mamba.dt_bias"]))

    def ssd_scalar(x, dt, b, c):
        return jnp.sum(
            ssd_forward(
                x,
                dt,
                ssd_a,
                b,
                c,
                cfg.mamba_chunk_size,
                ssd_d,
                ssd_dtb,
                cfg.time_step_limit,
            ).astype(jnp.float32)
        )

    def ssd_fwd_bwd(x, dt, b, c):
        g = jax.grad(ssd_scalar, argnums=(0, 1, 2, 3))(x, dt, b, c)
        return sum(jnp.sum(v[..., :1]) for v in g)

    bench("ssd_scan_fwd_bwd", ssd_fwd_bwd, ssd_hidden, ssd_dt, ssd_b, ssd_c)

    embed = put_replicated(jnp.asarray(host_params["model.embed_tokens.weight"]))

    def head_loss(e, toks):
        h = e[toks[:, :-1]].astype(jnp.bfloat16)
        logits = jnp.matmul(h, e.astype(jnp.bfloat16).T).astype(jnp.float32)
        labels = toks[:, 1:]
        lse = jax.nn.logsumexp(logits, axis=-1)
        sel = jnp.take_along_axis(logits, labels[..., None], axis=-1)[..., 0]
        return jnp.mean(lse - sel)

    def head_fwd_bwd(e, toks):
        return jnp.sum(jax.grad(head_loss)(e, toks)[:1, :1])

    bench("embed_head_loss_fwd_bwd", head_fwd_bwd, embed, tokens)

    w_in = put_replicated(
        jnp.asarray(host_params["model.layers.0.mamba.in_proj.weight"]).astype(
            jnp.bfloat16
        )
    )
    flat = put_sharded(
        jnp.asarray(hidden_np.reshape(global_batch * seq_len, cfg.hidden_size))
    )

    def matmul_only(x, w):
        return jnp.matmul(x, w.T)

    matmul_entry = bench("matmul_bf16_in_proj", matmul_only, flat, w_in)
    if "seconds" in matmul_entry:
        matmul_flops = 2.0 * global_batch * seq_len * w_in.shape[0] * w_in.shape[1]
        matmul_entry["tflops"] = matmul_flops / matmul_entry["seconds"] / 1e12
        if PEAK_FLOPS:
            matmul_entry["fraction_of_peak"] = (
                matmul_entry["tflops"] * 1e12 / PEAK_FLOPS
            )
        emit("component", name="matmul_bf16_in_proj", **matmul_entry)

    layer_seconds = sum(
        report["components"][k].get("seconds", 0.0)
        for k in ("attention_layer_fwd_bwd", "mamba_mixer_fwd_bwd", "mlp_fwd_bwd")
    )
    report["components"]["_decomposition"] = {
        "best_shape": best_shape["name"],
        "step_seconds": best_shape["async_step_seconds"],
        "layers_times_component_sum_seconds": layer_seconds * cfg.num_hidden_layers,
        "head_seconds": report["components"]
        .get("embed_head_loss_fwd_bwd", {})
        .get("seconds"),
        "note": "component benches include their own all-reduce of parameter gradients; sums are indicative, not exact",
    }
    emit("decomposition", **report["components"]["_decomposition"])

# ----------------------------------------------------------------------------- loss sanity

if best_shape is not None and SANITY_STEPS > 0:
    per_chip, seq_len, remat = (
        best_shape["per_chip"],
        best_shape["seq_len"],
        best_shape["remat"],
    )
    global_batch = per_chip * DEVICE_COUNT
    sanity_optimizer = make_optimizer(SANITY_LR)
    host_opt = sanity_optimizer.init(host_params)
    sanity_step = make_train_step(
        sanity_optimizer, remat, tree_shardings(host_params), tree_shardings(host_opt)
    )
    params = put_params(host_params)
    opt_state = put_params(host_opt)
    losses = []
    grad_norms = []
    started = time.perf_counter()
    for _ in range(SANITY_STEPS):
        rows = host_batch(train_stream, data_offset, global_batch, seq_len)
        data_offset += global_batch
        params, opt_state, metrics = sanity_step(params, opt_state, put_sharded(rows))
        losses.append(metrics["loss"])
        grad_norms.append(metrics["gradient_norm"])
    jax.block_until_ready(params)
    sanity_seconds = time.perf_counter() - started
    losses = [float(v) for v in jax.device_get(losses)]
    grad_norms = [float(v) for v in jax.device_get(grad_norms)]
    post_eval = {
        k: float(v)
        for k, v in jax.device_get(eval_step(params, put_sharded(eval_rows))).items()
    }
    report["sanity"] = {
        "shape": best_shape["name"],
        "learning_rate": SANITY_LR,
        "steps": SANITY_STEPS,
        "tokens": SANITY_STEPS * global_batch * seq_len,
        "seconds": sanity_seconds,
        "losses_first_5": losses[:5],
        "losses_last_5": losses[-5:],
        "loss_mean_first_10": statistics.mean(losses[:10]),
        "loss_mean_last_10": statistics.mean(losses[-10:]),
        "gradient_norm_max": max(grad_norms),
        "finite": all(math.isfinite(v) for v in losses + grad_norms),
        "eval_after": post_eval,
        "eval_loss_delta": post_eval["loss"] - base_eval["loss"],
    }
    emit("sanity", **report["sanity"])

# ----------------------------------------------------------------------------- report

report["best_shape"] = best_shape["name"] if best_shape else None
report["ok"] = best_shape is not None and (report.get("sanity", {}).get("finite", True))
report_path = OUTPUT / "h1jax-profile-gate-report.json"
report_path.write_text(json.dumps(report, indent=2, default=str) + "\n")
emit(
    "complete",
    report=str(report_path),
    ok=report["ok"],
    best_shape=report["best_shape"],
    best_tokens_per_second=best_shape["tokens_per_second"] if best_shape else None,
    best_mfu=best_shape.get("mfu") if best_shape else None,
)
if not report["ok"]:
    raise RuntimeError("h1jax profile gate produced no successful shape")
print("TPU_H1JAX_PROFILE_GATE_OK", flush=True)
