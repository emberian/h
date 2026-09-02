"""JAX worker for ``hghost-beliefgeo probe``: residual streams, SSM states, linear probes.

This module runs inside the h1jax virtualenv (``.venv-jax``), which has JAX and h1jax but
not the rest of ``hghost``'s dependencies; it imports only numpy and the numpy-only
``hghost.beliefgeo`` (for the process and probe mathematics). Input is the ``.npz``
written by the driver: ``rows`` int32 ``[N, T]``, ``targets`` float32 ``[N, T, K]``,
``valid`` bool ``[N, T]`` and ``test`` bool ``[N]``. Output is ``probe-results.json`` and
``probe-predictions.npz`` in the output directory.

Residual streams are collected after the embedding (``embed``), after every decoder
layer (``layerNN``) and after the final RMS norm (``final_norm``) by running
``h1jax.model.decoder_layer`` in a Python loop. The Mamba-2 SSM state is not exposed by
``h1jax.model.ssd_forward`` (its chunked scan only forms chunk-boundary states), so the
per-token state is recomputed here with the sequential recurrence

    h_t = exp(dt_t * A) h_{t-1} + dt_t * B_t x_t^T,    y_t = h_t C_t + D x_t

from the same projections ``mamba()`` builds, and checked against ``ssd_forward`` on the
first batch of every probed layer (``parity`` in the results).
"""

from __future__ import annotations

import argparse
import platform
import sys
import time
from pathlib import Path

import numpy as np

from hghost.beliefgeo import probe_features, write_json


def parse_layers(specification: str, count: int) -> list[int]:
    if specification == "all":
        return list(range(count))
    if specification == "none":
        return []
    layers = sorted({int(item) for item in specification.split(",") if item.strip()})
    if any(index < 0 or index >= count for index in layers):
        raise ValueError(f"layer indices must lie in [0, {count})")
    return layers


def model_functions(cfg, stride: int):
    """JIT-compiled per-layer functions: residual step, final norm, SSM states, parity."""

    import jax
    import jax.numpy as jnp
    from h1jax.model import (
        _depthwise_causal_conv,
        _linear,
        _mup_vector,
        _rms_norm,
        decoder_layer,
        ssd_forward,
    )

    def ssm_inputs(layer, hidden):
        x = _rms_norm(hidden, layer["input_layernorm.weight"], cfg.rms_norm_eps)
        projected = _linear(
            x * jnp.asarray(cfg.ssm_in_multiplier, x.dtype),
            layer["mamba.in_proj.weight"],
            layer.get("mamba.in_proj.bias"),
        )
        projected = projected * _mup_vector(cfg, projected.dtype)
        _, conv_input, dt = jnp.split(
            projected, (cfg.mamba_d_ssm, cfg.mamba_d_ssm + cfg.mamba_conv_dim), axis=-1
        )
        convolved = _depthwise_causal_conv(
            conv_input,
            layer["mamba.conv1d.weight"],
            layer.get("mamba.conv1d.bias"),
            cfg.mamba_d_conv,
        )
        inner, b_matrix, c_matrix = jnp.split(
            convolved,
            (cfg.mamba_d_ssm, cfg.mamba_d_ssm + cfg.mamba_group_state_size),
            axis=-1,
        )
        batch, seq_len, _ = inner.shape
        inner = inner.reshape(batch, seq_len, cfg.mamba_n_heads, cfg.mamba_d_head)
        b_matrix = b_matrix.reshape(
            batch, seq_len, cfg.mamba_n_groups, cfg.mamba_d_state
        )
        c_matrix = c_matrix.reshape(
            batch, seq_len, cfg.mamba_n_groups, cfg.mamba_d_state
        )
        repeats = cfg.mamba_n_heads // cfg.mamba_n_groups
        b_matrix = jnp.repeat(b_matrix, repeats, axis=2)
        c_matrix = jnp.repeat(c_matrix, repeats, axis=2)
        a = -jnp.exp(layer["mamba.A_log"].astype(jnp.float32))
        return (
            inner.astype(jnp.float32),
            dt,
            a,
            b_matrix.astype(jnp.float32),
            c_matrix.astype(jnp.float32),
        )

    def discretize(dt, layer):
        dt = jax.nn.softplus(dt + layer["mamba.dt_bias"].astype(dt.dtype))
        return jnp.clip(dt, cfg.time_step_limit[0], cfg.time_step_limit[1]).astype(
            jnp.float32
        )

    def recurrence(layer, hidden):
        """Time-major inputs for the scan: x[T,B,H,P], dt[T,B,H], b/c[T,B,H,N]."""

        x, dt_raw, a, b_matrix, c_matrix = ssm_inputs(layer, hidden)
        dt = discretize(dt_raw, layer)
        d = layer["mamba.D"].astype(jnp.float32)

        def step(state, inputs):
            x_t, dt_t, b_t, c_t = inputs
            decay = jnp.exp(dt_t * a)
            state = (
                state * decay[..., None, None]
                + (dt_t[..., None] * x_t)[..., None] * b_t[..., None, :]
            )
            y_t = jnp.einsum("bhpn,bhn->bhp", state, c_t) + d[None, :, None] * x_t
            return state, y_t

        batch = x.shape[0]
        initial = jnp.zeros(
            (batch, cfg.mamba_n_heads, cfg.mamba_d_head, cfg.mamba_d_state), jnp.float32
        )
        inputs = (
            x.transpose(1, 0, 2, 3),
            dt.transpose(1, 0, 2),
            b_matrix.transpose(1, 0, 2, 3),
            c_matrix.transpose(1, 0, 2, 3),
        )
        return step, initial, inputs, (x, dt_raw, a, b_matrix, c_matrix, d)

    def ssm_states(layer, hidden):
        """States at positions stride-1, 2*stride-1, ...: [B, T // stride, H, P, N]."""

        step, initial, inputs, _ = recurrence(layer, hidden)
        seq_len = inputs[0].shape[0]
        chunks = seq_len // stride
        chunked = tuple(
            value.reshape(chunks, stride, *value.shape[1:]) for value in inputs
        )

        def chunk_step(state, chunk_inputs):
            def inner(index, carry):
                carry, _ = step(carry, tuple(value[index] for value in chunk_inputs))
                return carry

            state = jax.lax.fori_loop(0, stride, inner, state)
            return state, state

        _, states = jax.lax.scan(chunk_step, initial, chunked)
        return states.transpose(1, 0, 2, 3, 4)

    def parity(layer, hidden):
        step, initial, inputs, (x, dt_raw, a, b_matrix, c_matrix, _) = recurrence(
            layer, hidden
        )
        _, outputs = jax.lax.scan(step, initial, inputs)
        outputs = outputs.transpose(1, 0, 2, 3)
        reference = ssd_forward(
            x,
            dt_raw,
            a,
            b_matrix,
            c_matrix,
            cfg.mamba_chunk_size,
            layer["mamba.D"],
            layer["mamba.dt_bias"],
            cfg.time_step_limit,
        )
        return jnp.max(jnp.abs(outputs - reference)), jnp.max(jnp.abs(reference))

    return {
        "layer": jax.jit(lambda layer, hidden: decoder_layer(layer, hidden, cfg)),
        "final_norm": jax.jit(
            lambda hidden, weight: _rms_norm(hidden, weight, cfg.rms_norm_eps)
        ),
        "ssm_states": jax.jit(ssm_states),
        "parity": jax.jit(parity),
    }


def collect(
    params,
    cfg,
    rows: np.ndarray,
    *,
    batch_size: int,
    ssm_layers: list[int],
    stride: int,
    progress,
) -> dict:
    """Residual streams for every layer and subsampled SSM states for the chosen layers."""

    import jax.numpy as jnp
    from h1jax.model import _layer_params

    count, seq_len = rows.shape
    if seq_len % stride:
        raise ValueError("the row length must be a multiple of the SSM stride")
    functions = model_functions(cfg, stride)
    layer_params = [
        _layer_params(params, index) for index in range(cfg.num_hidden_layers)
    ]
    names = [
        "embed",
        *[f"layer{index:02d}" for index in range(cfg.num_hidden_layers)],
        "final_norm",
    ]
    residual = np.empty((len(names), count, seq_len, cfg.hidden_size), dtype=np.float32)
    state_width = cfg.mamba_n_heads * cfg.mamba_d_head * cfg.mamba_d_state
    states = {
        index: np.empty((count, seq_len // stride, state_width), dtype=np.float32)
        for index in ssm_layers
    }
    parity = {}
    embedding = params["model.embed_tokens.weight"]
    multiplier = jnp.asarray(cfg.embedding_multiplier, jnp.float32)
    for start in range(0, count, batch_size):
        batch = rows[start : start + batch_size]
        actual = batch.shape[0]
        if actual < batch_size:
            batch = np.concatenate(
                [batch, np.repeat(batch[:1], batch_size - actual, axis=0)], axis=0
            )
        hidden = embedding[jnp.asarray(batch)].astype(jnp.float32) * multiplier
        residual[0, start : start + actual] = np.asarray(hidden)[:actual]
        for index, layer in enumerate(layer_params):
            if index in states:
                if start == 0:
                    difference, magnitude = functions["parity"](layer, hidden)
                    parity[f"layer{index:02d}"] = {
                        "max_abs_difference": float(difference),
                        "max_abs_reference": float(magnitude),
                    }
                chunk_states = functions["ssm_states"](layer, hidden)
                states[index][start : start + actual] = np.asarray(
                    chunk_states
                ).reshape(batch_size, -1, state_width)[:actual]
            hidden = functions["layer"](layer, hidden)
            residual[index + 1, start : start + actual] = np.asarray(hidden)[:actual]
        final = functions["final_norm"](hidden, params["model.final_layernorm.weight"])
        residual[-1, start : start + actual] = np.asarray(final)[:actual]
        progress(start + actual, count)
    return {"names": names, "residual": residual, "states": states, "parity": parity}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument(
        "--input", type=Path, required=True, help="probe-input.npz from the driver"
    )
    parser.add_argument("--output", type=Path, required=True, help="output directory")
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--ssm-stride", type=int, default=16)
    parser.add_argument("--ssm-layers", default="all")
    parser.add_argument("--ridges", default="1e-4,1e-3,1e-2,1e-1,1,10")
    parser.add_argument("--seed", type=int, default=0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    import jax
    import jax.numpy as jnp
    from h1jax.checkpoint import load_hf_params
    from h1jax.config import FalconH1Config

    started = time.perf_counter()
    cfg = FalconH1Config.from_json(args.checkpoint / "config.json")
    params = load_hf_params(args.checkpoint, dtype=jnp.float32)
    with np.load(args.input) as archive:
        rows = archive["rows"].astype(np.int32)
        targets = archive["targets"].astype(np.float32)
        valid = archive["valid"].astype(bool)
        test = archive["test"].astype(bool)
    ssm_layers = parse_layers(args.ssm_layers, cfg.num_hidden_layers)
    ridges = tuple(float(item) for item in args.ridges.split(","))
    load_seconds = time.perf_counter() - started

    def progress(done: int, total: int) -> None:
        print(
            f"[beliefgeo-jax] {done}/{total} rows, {time.perf_counter() - started:.0f}s",
            file=sys.stderr,
            flush=True,
        )

    collected = collect(
        params,
        cfg,
        rows,
        batch_size=args.batch,
        ssm_layers=ssm_layers,
        stride=args.ssm_stride,
        progress=progress,
    )
    forward_seconds = time.perf_counter() - started - load_seconds

    count, seq_len = rows.shape
    groups = np.repeat(np.arange(count), seq_len)
    keep = valid.reshape(-1)
    flat_targets = targets.reshape(-1, targets.shape[-1])[keep]
    flat_groups = groups[keep]
    flat_test = test[flat_groups]
    predictions = {"truth": flat_targets[flat_test]}
    residual_results = []
    for index, name in enumerate(collected["names"]):
        features = collected["residual"][index].reshape(-1, cfg.hidden_size)[keep]
        outcome = probe_features(
            features,
            flat_targets,
            flat_groups,
            flat_test,
            ridges=ridges,
            shuffle_seed=args.seed,
        )
        predictions[f"residual/{name}"] = outcome["real"].pop("predictions")
        outcome["shuffled"].pop("predictions")
        residual_results.append({"name": name, **outcome})
        print(
            f"[beliefgeo-jax] {name}: R2={outcome['real']['r2']:.3f} shuffled={outcome['shuffled']['r2']:.3f}",
            file=sys.stderr,
            flush=True,
        )
    del collected["residual"]

    positions = np.arange(args.ssm_stride - 1, seq_len, args.ssm_stride)
    ssm_groups = np.repeat(np.arange(count), positions.shape[0])
    ssm_targets = targets[:, positions].reshape(-1, targets.shape[-1])
    ssm_test = test[ssm_groups]
    predictions["ssm_truth"] = ssm_targets[ssm_test]
    ssm_results = []
    for index in ssm_layers:
        name = f"layer{index:02d}"
        array = collected["states"].pop(index)
        features = array.reshape(-1, array.shape[-1])
        outcome = probe_features(
            features,
            ssm_targets,
            ssm_groups,
            ssm_test,
            ridges=ridges,
            shuffle_seed=args.seed,
        )
        predictions[f"ssm/{name}"] = outcome["real"].pop("predictions")
        outcome["shuffled"].pop("predictions")
        ssm_results.append({"name": name, "positions": positions.tolist(), **outcome})
        print(
            f"[beliefgeo-jax] ssm {name}: R2={outcome['real']['r2']:.3f} shuffled={outcome['shuffled']['r2']:.3f}",
            file=sys.stderr,
            flush=True,
        )
        del features

    args.output.mkdir(parents=True, exist_ok=True)
    np.savez(args.output / "probe-predictions.npz", **predictions)
    results = {
        "checkpoint": str(args.checkpoint.resolve()),
        "checkpoint_name": args.checkpoint.resolve().name,
        "config": {
            "hidden_size": cfg.hidden_size,
            "num_hidden_layers": cfg.num_hidden_layers,
            "mamba_n_heads": cfg.mamba_n_heads,
            "mamba_d_head": cfg.mamba_d_head,
            "mamba_d_state": cfg.mamba_d_state,
        },
        "sequences": int(count),
        "test_sequences": int(test.sum()),
        "length": int(seq_len),
        "batch": args.batch,
        "compute_dtype": "float32",
        "ridges": list(ridges),
        "ridge_rule": "relative to trace(Gram)/rank; chosen on 20% of training sequences",
        "shuffle_seed": args.seed,
        "ssm_stride": args.ssm_stride,
        "ssm_state_width": int(
            cfg.mamba_n_heads * cfg.mamba_d_head * cfg.mamba_d_state
        ),
        "residual": residual_results,
        "ssm": ssm_results,
        "parity": collected["parity"],
        "jax_version": jax.__version__,
        "devices": [str(device) for device in jax.devices()],
        "python": platform.python_version(),
        "load_seconds": round(load_seconds, 3),
        "forward_seconds": round(forward_seconds, 3),
        "total_seconds": round(time.perf_counter() - started, 3),
    }
    write_json(args.output / "probe-results.json", results)


if __name__ == "__main__":
    main()
