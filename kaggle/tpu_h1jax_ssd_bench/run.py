"""Benchmark SSD implementations inside the real h1jax training step on TPU v5e-8.

For each variant (reference ``v1``; ``v2`` rewrite; ``v2`` with bfloat16 matmul inputs) this compiles the
full FP32-master / BF16-compute AdamW step at the production shape (64 × 512 per chip, rematerialized,
layer scan), times warm steps with asynchronous dispatch, checks that the variants agree on the loss of
the same batch, and micro-benchmarks the bare SSD forward+backward. No checkpoint is written.
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

LOCAL = os.environ.get("HGHOST_LOCAL") == "1"
if not LOCAL:
    os.environ.setdefault("JAX_COMPILATION_CACHE_DIR", "/kaggle/working/jax-cache")
OUTPUT = Path(os.environ.get("HGHOST_OUTPUT", "/kaggle/working/h1jax-ssd-bench"))
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
from h1jax import model as h1model
from h1jax.checkpoint import load_hf_params
from h1jax.config import FalconH1Config
from h1jax.data import TokenStream
from h1jax.model import causal_lm_loss, count_parameters, ssd_forward, ssd_forward_v2
from jax.sharding import Mesh, NamedSharding
from jax.sharding import PartitionSpec as P

VARIANTS = os.environ.get("HGHOST_SSD_VARIANTS", "v1,v2,v2bf16,v2_dotsave").split(",")
PER_CHIP = int(os.environ.get("HGHOST_BENCH_PER_CHIP", "64"))
SEQ_LEN = int(os.environ.get("HGHOST_BENCH_SEQ", "512"))
REMAT = os.environ.get("HGHOST_BENCH_REMAT", "1") == "1"
WARMUP_STEPS = int(os.environ.get("HGHOST_BENCH_WARMUP", "3"))
TIMED_STEPS = int(os.environ.get("HGHOST_BENCH_STEPS", "15"))
COMPONENT_ITERS = int(os.environ.get("HGHOST_BENCH_COMPONENT_ITERS", "10"))
REQUIRE_TPU = os.environ.get("HGHOST_REQUIRE_TPU", "0" if LOCAL else "1") == "1"
PEAK_FLOPS_PER_CHIP = 197e12

hardware = {
    "jax": jax.__version__,
    "backend": jax.default_backend(),
    "device_count": jax.device_count(),
    "device_kind": jax.devices()[0].device_kind,
}
emit("hardware", **hardware)
if REQUIRE_TPU and (hardware["backend"] != "tpu" or hardware["device_count"] != 8):
    raise RuntimeError("This benchmark requires the complete TPU v5e-8 slice")
DEVICE_COUNT = hardware["device_count"]
GLOBAL_BATCH = PER_CHIP * DEVICE_COUNT
TOKENS_PER_STEP = GLOBAL_BATCH * SEQ_LEN

if LOCAL:
    base_root = Path(os.environ["HGHOST_BASE_DIR"]).resolve()
    corpus_root = Path(os.environ["HGHOST_CORPUS_DIR"]).resolve()
else:
    base_root = exactly_one("/kaggle/input/**/preflight-manifest.json").parent
    corpus_root = exactly_one("/kaggle/input/**/validation-report.json").parent
cfg = FalconH1Config.from_json(base_root / "config.json")
host_params = {
    k: np.asarray(v) for k, v in load_hf_params(base_root, dtype=jnp.float32).items()
}
parameter_count = count_parameters(host_params)
flops_per_token = (
    6.0 * parameter_count
    + (
        2.0
        * SEQ_LEN
        * cfg.head_dim
        * cfg.num_attention_heads
        * 2
        * 3
        * cfg.num_hidden_layers
    )
    + (
        (
            2.0
            * min(cfg.mamba_chunk_size, SEQ_LEN)
            * (cfg.mamba_d_state + cfg.mamba_d_head)
            + 4.0 * cfg.mamba_d_state * cfg.mamba_d_head
        )
        * cfg.mamba_n_heads
        * 3.0
        * cfg.num_hidden_layers
    )
)

mesh = Mesh(np.array(jax.devices()), axis_names=("data",))
REPLICATED = NamedSharding(mesh, P())
SHARDED = NamedSharding(mesh, P("data"))
stream = TokenStream(corpus_root / "train.bin", SEQ_LEN, seed=0)


def batch(offset: int) -> jax.Array:
    rows = stream.batch(
        offset, device_count=1, accumulation_steps=1, per_device_batch=GLOBAL_BATCH
    )
    return jax.device_put(rows.reshape(GLOBAL_BATCH, SEQ_LEN + 1), SHARDED)


decay_mask = {key: value.ndim >= 2 for key, value in host_params.items()}
optimizer = optax.chain(
    optax.clip_by_global_norm(1.0),
    optax.adamw(
        learning_rate=1e-6, b1=0.9, b2=0.95, eps=1e-8, weight_decay=0.1, mask=decay_mask
    ),
)


def make_step():
    def loss_fn(p, tokens):
        return causal_lm_loss(
            p,
            tokens,
            cfg,
            compute_dtype=jnp.bfloat16,
            gradient_checkpointing=REMAT,
            layer_scan=True,
        )

    def step(p, s, tokens):
        (_, metrics), grads = jax.value_and_grad(loss_fn, has_aux=True)(p, tokens)
        updates, s = optimizer.update(grads, s, p)
        return optax.apply_updates(p, updates), s, metrics

    return jax.jit(
        step,
        in_shardings=(REPLICATED, REPLICATED, SHARDED),
        out_shardings=(REPLICATED, REPLICATED, REPLICATED),
        donate_argnums=(0, 1),
    )


def configure(variant: str) -> None:
    h1model.REMAT_POLICY = ""
    if variant == "v2_dotsave":
        h1model.SSD_IMPLEMENTATION, h1model.SSD_MATMUL_DTYPE = "v2", None
        h1model.REMAT_POLICY = "dots_no_batch"
        return
    if variant == "v1":
        h1model.SSD_IMPLEMENTATION, h1model.SSD_MATMUL_DTYPE = "v1", None
    elif variant == "v2":
        h1model.SSD_IMPLEMENTATION, h1model.SSD_MATMUL_DTYPE = "v2", None
    elif variant == "v2bf16":
        h1model.SSD_IMPLEMENTATION, h1model.SSD_MATMUL_DTYPE = (
            "v2",
            jnp.dtype(jnp.bfloat16),
        )
    else:
        raise ValueError(variant)


report: dict[str, Any] = {
    **hardware,
    "per_chip": PER_CHIP,
    "seq_len": SEQ_LEN,
    "remat": REMAT,
    "variants": {},
}
reference_loss = None
first_batch = batch(0)

for variant in VARIANTS:
    configure(variant)
    entry: dict[str, Any] = {}
    try:
        params = jax.device_put(host_params, REPLICATED)
        opt_state = jax.device_put(optimizer.init(host_params), REPLICATED)
        step = make_step()
        started = time.perf_counter()
        compiled = step.lower(params, opt_state, first_batch).compile()
        entry["compile_seconds"] = time.perf_counter() - started
        mem = compiled.memory_analysis()
        if mem is not None:
            entry["temp_bytes"] = int(mem.temp_size_in_bytes)
        # Loss agreement on the identical first batch, before any update.
        params, opt_state, metrics = compiled(params, opt_state, first_batch)
        entry["first_loss"] = float(jax.device_get(metrics["loss"]))
        if reference_loss is None:
            reference_loss = entry["first_loss"]
        entry["loss_delta_vs_first_variant"] = entry["first_loss"] - reference_loss
        offset = GLOBAL_BATCH
        for _ in range(WARMUP_STEPS):
            params, opt_state, metrics = compiled(params, opt_state, batch(offset))
            offset += GLOBAL_BATCH
        jax.block_until_ready(params)
        sync_times = []
        for _ in range(3):
            t0 = time.perf_counter()
            params, opt_state, metrics = compiled(params, opt_state, batch(offset))
            offset += GLOBAL_BATCH
            jax.block_until_ready(params)
            sync_times.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        for _ in range(TIMED_STEPS):
            params, opt_state, metrics = compiled(params, opt_state, batch(offset))
            offset += GLOBAL_BATCH
        jax.block_until_ready(params)
        step_seconds = (time.perf_counter() - t0) / TIMED_STEPS
        entry.update(
            {
                "sync_step_seconds": sync_times,
                "async_step_seconds": step_seconds,
                "tokens_per_second": TOKENS_PER_STEP / step_seconds,
                "mfu": flops_per_token
                * TOKENS_PER_STEP
                / step_seconds
                / (PEAK_FLOPS_PER_CHIP * DEVICE_COUNT),
                "last_loss": float(jax.device_get(metrics["loss"])),
            }
        )
        del params, opt_state
        emit("variant_step", variant=variant, **entry)
    except Exception as exc:  # noqa: BLE001
        entry["error"] = f"{type(exc).__name__}: {str(exc)[:600]}"
        emit("variant_failed", variant=variant, error=entry["error"][:300])
    report["variants"][variant] = entry

# Bare SSD forward+backward at the per-layer shape, sharded over chips like the real step.
rng = np.random.default_rng(0)
shape_x = (GLOBAL_BATCH, SEQ_LEN, cfg.mamba_n_heads, cfg.mamba_d_head)
x = jax.device_put(jnp.asarray(rng.standard_normal(shape_x, dtype=np.float32)), SHARDED)
dt = jax.device_put(
    jnp.asarray(rng.standard_normal(shape_x[:3], dtype=np.float32)), SHARDED
)
b_groups = jax.device_put(
    jnp.asarray(
        rng.standard_normal(
            (GLOBAL_BATCH, SEQ_LEN, cfg.mamba_n_groups, cfg.mamba_d_state),
            dtype=np.float32,
        )
    ),
    SHARDED,
)
c_groups = jax.device_put(
    jnp.asarray(
        rng.standard_normal(
            (GLOBAL_BATCH, SEQ_LEN, cfg.mamba_n_groups, cfg.mamba_d_state),
            dtype=np.float32,
        )
    ),
    SHARDED,
)
a = jax.device_put(
    -jnp.exp(jnp.asarray(host_params["model.layers.0.mamba.A_log"])), REPLICATED
)
d = jax.device_put(jnp.asarray(host_params["model.layers.0.mamba.D"]), REPLICATED)
dt_bias = jax.device_put(
    jnp.asarray(host_params["model.layers.0.mamba.dt_bias"]), REPLICATED
)
repeats = cfg.mamba_n_heads // cfg.mamba_n_groups


def bench(name: str, fn, *args) -> None:
    entry: dict[str, Any] = {}
    try:
        jitted = jax.jit(fn)
        t0 = time.perf_counter()
        jax.block_until_ready(jitted(*args))
        entry["first_call_seconds"] = time.perf_counter() - t0
        for _ in range(2):
            jax.block_until_ready(jitted(*args))
        t0 = time.perf_counter()
        for _ in range(COMPONENT_ITERS):
            out = jitted(*args)
        jax.block_until_ready(out)
        entry["seconds"] = (time.perf_counter() - t0) / COMPONENT_ITERS
    except Exception as exc:  # noqa: BLE001
        entry["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
    report["variants"].setdefault("components", {})[name] = entry
    emit("component", name=name, **entry)


def v1_fwd_bwd(x_, dt_, b_, c_):
    b_heads = jnp.repeat(b_, repeats, axis=2)
    c_heads = jnp.repeat(c_, repeats, axis=2)

    def scalar(x2, dt2, b2, c2):
        return jnp.sum(
            ssd_forward(
                x2,
                dt2,
                a,
                b2,
                c2,
                cfg.mamba_chunk_size,
                d,
                dt_bias,
                cfg.time_step_limit,
            ).astype(jnp.float32)
        )

    grads = jax.grad(scalar, argnums=(0, 1, 2, 3))(x_, dt_, b_heads, c_heads)
    return sum(jnp.sum(g[..., :1]) for g in grads)


def v2_fwd_bwd(x_, dt_, b_, c_, matmul_dtype=None):
    def scalar(x2, dt2, b2, c2):
        return jnp.sum(
            ssd_forward_v2(
                x2,
                dt2,
                a,
                b2,
                c2,
                cfg.mamba_chunk_size,
                d,
                dt_bias,
                cfg.time_step_limit,
                matmul_dtype=matmul_dtype,
            ).astype(jnp.float32)
        )

    grads = jax.grad(scalar, argnums=(0, 1, 2, 3))(x_, dt_, b_, c_)
    return sum(jnp.sum(g[..., :1]) for g in grads)


bench("ssd_v1_fwd_bwd", v1_fwd_bwd, x, dt, b_groups, c_groups)
bench("ssd_v2_fwd_bwd", v2_fwd_bwd, x, dt, b_groups, c_groups)
bench(
    "ssd_v2bf16_fwd_bwd",
    lambda *args: v2_fwd_bwd(*args, matmul_dtype=jnp.bfloat16),
    x,
    dt,
    b_groups,
    c_groups,
)

(OUTPUT / "ssd-bench-report.json").write_text(
    json.dumps(report, indent=2, default=str) + "\n"
)
emit(
    "complete",
    **{
        k: v.get("tokens_per_second")
        for k, v in report["variants"].items()
        if isinstance(v, dict) and "tokens_per_second" in v
    },
)
print("TPU_H1JAX_SSD_BENCH_OK", flush=True)
