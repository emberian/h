from __future__ import annotations

from collections.abc import Mapping
from functools import partial

import jax
import jax.numpy as jnp
import numpy as np

from .config import FalconH1Config

Array = jax.Array
Params = Mapping[str, Array]

# SSD implementation switch (read once at import): "v1" is the reference chunked form that
# passed parity against Transformers; "v2" is the TPU-friendlier rewrite (ssd_forward_v2),
# which must agree with v1 to float32 tolerance (see tests). H1JAX_SSD_MATMUL_DTYPE may lower
# v2's two large matmul inputs (e.g. "bfloat16"); unset keeps float32.
import os as _os

SSD_IMPLEMENTATION = _os.environ.get("H1JAX_SSD", "v1")
SSD_MATMUL_DTYPE = (
    jnp.dtype(_os.environ["H1JAX_SSD_MATMUL_DTYPE"])
    if _os.environ.get("H1JAX_SSD_MATMUL_DTYPE")
    else None
)
# Rematerialization policy for the per-layer checkpoint in the layer scan: "" (recompute
# everything, minimum memory), "dots_no_batch" (keep the outputs of batch-free matmuls, i.e. the
# projections), or "dots" (keep every dot output; large).
REMAT_POLICY = _os.environ.get("H1JAX_REMAT_POLICY", "")


def _remat_policy():
    if REMAT_POLICY == "dots_no_batch":
        return jax.checkpoint_policies.dots_with_no_batch_dims_saveable
    if REMAT_POLICY == "dots":
        return jax.checkpoint_policies.dots_saveable
    if REMAT_POLICY:
        raise ValueError(f"unknown H1JAX_REMAT_POLICY {REMAT_POLICY!r}")
    return None


def _linear(x: Array, weight: Array, bias: Array | None = None) -> Array:
    """PyTorch-layout linear: weight is (out_features, in_features)."""

    dtype = x.dtype
    output = jnp.matmul(x, weight.astype(dtype).T)
    if bias is not None:
        output = output + bias.astype(dtype)
    return output


def _rms_norm(x: Array, weight: Array, eps: float) -> Array:
    dtype = x.dtype
    normalized = x.astype(jnp.float32) * jax.lax.rsqrt(
        jnp.mean(jnp.square(x.astype(jnp.float32)), axis=-1, keepdims=True) + eps
    )
    return (normalized.astype(dtype) * weight.astype(dtype)).astype(dtype)


def _rotate_half(x: Array) -> Array:
    half = x.shape[-1] // 2
    return jnp.concatenate((-x[..., half:], x[..., :half]), axis=-1)


def _apply_rope(q: Array, k: Array, cfg: FalconH1Config) -> tuple[Array, Array]:
    seq_len = q.shape[2]
    inv_freq = 1.0 / (
        cfg.rope_theta
        ** (jnp.arange(0, cfg.head_dim, 2, dtype=jnp.float32) / cfg.head_dim)
    )
    freqs = jnp.einsum("l,d->ld", jnp.arange(seq_len, dtype=jnp.float32), inv_freq)
    emb = jnp.concatenate((freqs, freqs), axis=-1)
    cos = jnp.cos(emb).astype(q.dtype)[None, None, :, :]
    sin = jnp.sin(emb).astype(q.dtype)[None, None, :, :]
    return q * cos + _rotate_half(q) * sin, k * cos + _rotate_half(k) * sin


def attention(layer: Params, x: Array, cfg: FalconH1Config) -> Array:
    batch, seq_len, _ = x.shape
    q = _linear(x, layer["self_attn.q_proj.weight"])
    k = _linear(x, layer["self_attn.k_proj.weight"]) * jnp.asarray(
        cfg.key_multiplier, x.dtype
    )
    v = _linear(x, layer["self_attn.v_proj.weight"])
    q = q.reshape(batch, seq_len, cfg.num_attention_heads, cfg.head_dim).transpose(
        0, 2, 1, 3
    )
    k = k.reshape(batch, seq_len, cfg.num_key_value_heads, cfg.head_dim).transpose(
        0, 2, 1, 3
    )
    v = v.reshape(batch, seq_len, cfg.num_key_value_heads, cfg.head_dim).transpose(
        0, 2, 1, 3
    )
    q, k = _apply_rope(q, k, cfg)
    repeats = cfg.num_attention_heads // cfg.num_key_value_heads
    if repeats != 1:
        k = jnp.repeat(k, repeats, axis=1)
        v = jnp.repeat(v, repeats, axis=1)
    scores = jnp.matmul(q, jnp.swapaxes(k, -1, -2)) * (cfg.head_dim**-0.5)
    causal = jnp.tril(jnp.ones((seq_len, seq_len), dtype=jnp.bool_))
    scores = jnp.where(causal[None, None, :, :], scores, -jnp.inf)
    probabilities = jax.nn.softmax(scores.astype(jnp.float32), axis=-1).astype(q.dtype)
    output = jnp.matmul(probabilities, v)
    output = output.transpose(0, 2, 1, 3).reshape(batch, seq_len, cfg.attention_width)
    return _linear(output, layer["self_attn.o_proj.weight"])


def _pad_sequence(x: Array, amount: int) -> Array:
    if amount == 0:
        return x
    widths = [(0, 0)] * x.ndim
    widths[1] = (0, amount)
    return jnp.pad(x, widths)


def segment_sum(x: Array) -> Array:
    """Stable lower-triangular segment sums, matching Transformers' fallback."""

    size = x.shape[-1]
    expanded = jnp.broadcast_to(x[..., None], x.shape + (size,))
    strict_lower = jnp.tril(jnp.ones((size, size), dtype=jnp.bool_), k=-1)
    cumulative = jnp.cumsum(jnp.where(strict_lower, expanded, 0.0), axis=-2)
    lower = jnp.tril(jnp.ones((size, size), dtype=jnp.bool_))
    return jnp.where(lower, cumulative, -jnp.inf)


def _ssd_single_chunk(
    x: Array,
    dt: Array,
    a: Array,
    b_matrix: Array,
    c_matrix: Array,
    d: Array,
    precision: jax.lax.Precision,
) -> Array:
    x_discrete = x * dt[..., None]
    a_discrete = a.astype(jnp.float32) * dt
    a_time_major = a_discrete.transpose(0, 2, 1)
    decay = jnp.exp(segment_sum(a_time_major))
    output = jnp.einsum(
        "blhn,bshn,bhls,bshp->blhp",
        c_matrix,
        b_matrix,
        decay,
        x_discrete,
        precision=precision,
    )
    return output + d[None, None, :, None] * x


def ssd_forward(
    x: Array,
    dt: Array,
    a: Array,
    b_matrix: Array,
    c_matrix: Array,
    chunk_size: int,
    d: Array,
    dt_bias: Array,
    dt_limit: tuple[float, float],
    *,
    precision: jax.lax.Precision = jax.lax.Precision.DEFAULT,
) -> Array:
    """Chunked Mamba-2 SSD in the exact Falcon-H1 fallback parameterization."""

    batch, seq_len, num_heads, _ = x.shape
    dt_dtype = dt.dtype
    dt = jax.nn.softplus(dt + dt_bias.astype(dt_dtype)).astype(dt_dtype)
    dt = jnp.clip(dt, dt_limit[0], dt_limit[1]).astype(jnp.float32)
    x = x.astype(jnp.float32)
    b_matrix = b_matrix.astype(jnp.float32)
    c_matrix = c_matrix.astype(jnp.float32)
    d = d.astype(jnp.float32)
    if seq_len <= chunk_size:
        return _ssd_single_chunk(x, dt, a, b_matrix, c_matrix, d, precision)

    pad_size = (chunk_size - seq_len % chunk_size) % chunk_size
    x_padded = _pad_sequence(x, pad_size)
    dt_padded = _pad_sequence(dt, pad_size)
    b_padded = _pad_sequence(b_matrix, pad_size)
    c_padded = _pad_sequence(c_matrix, pad_size)
    d_residual = d[None, None, :, None] * x_padded
    x_discrete = x_padded * dt_padded[..., None]
    a_discrete = a.astype(jnp.float32) * dt_padded

    def chunk(tensor: Array) -> Array:
        return tensor.reshape(
            tensor.shape[0],
            tensor.shape[1] // chunk_size,
            chunk_size,
            *tensor.shape[2:],
        )

    x_blocks = chunk(x_discrete)
    a_blocks = chunk(a_discrete)
    b_blocks = chunk(b_padded)
    c_blocks = chunk(c_padded)
    a_blocks = a_blocks.transpose(0, 3, 1, 2)
    a_cumsum = jnp.cumsum(a_blocks, axis=-1)

    within_decay = jnp.exp(segment_sum(a_blocks))
    y_diagonal = jnp.einsum(
        "bclhn,bcshn,bhcls,bcshp->bclhp",
        c_blocks,
        b_blocks,
        within_decay,
        x_blocks,
        precision=precision,
    )

    state_decay = jnp.exp(a_cumsum[..., -1:] - a_cumsum)
    states = jnp.einsum(
        "bclhn,bhcl,bclhp->bchpn",
        b_blocks,
        state_decay,
        x_blocks,
        precision=precision,
    )
    states = jnp.concatenate((jnp.zeros_like(states[:, :1]), states), axis=1)
    a_ends = jnp.pad(a_cumsum[..., -1], ((0, 0), (0, 0), (1, 0)))
    chunk_decay = jnp.exp(segment_sum(a_ends))
    boundary_states = jnp.einsum(
        "bhzc,bchpn->bzhpn",
        chunk_decay,
        states,
        precision=precision,
    )[:, :-1]

    y_off_diagonal = jnp.einsum(
        "bclhn,bchpn,bhcl->bclhp",
        c_blocks,
        boundary_states,
        jnp.exp(a_cumsum),
        precision=precision,
    )
    output = y_diagonal + y_off_diagonal
    output = output.reshape(batch, -1, num_heads, x.shape[-1]) + d_residual
    return output[:, :seq_len]


def ssd_forward_v2(
    x: Array,
    dt: Array,
    a: Array,
    b_matrix: Array,
    c_matrix: Array,
    chunk_size: int,
    d: Array,
    dt_bias: Array,
    dt_limit: tuple[float, float],
    *,
    precision: jax.lax.Precision = jax.lax.Precision.DEFAULT,
    matmul_dtype: jnp.dtype | None = None,
) -> Array:
    """Chunked Mamba-2 SSD, same math as ``ssd_forward`` in a TPU-friendlier form.

    Differences from the reference form: ``b_matrix``/``c_matrix`` may be group-shaped
    ``[batch, seq, groups, state]`` (no materialized repeat across heads); the intra-chunk
    decay is ``exp(cumsum_i - cumsum_j)`` from a single cumulative sum instead of a 4-D
    segment sum; the intra-chunk product is two explicit batched matmuls (C B^T once per
    group, then the decayed [q, q] matrix against X per head); the carried state runs as a
    scan over chunks. ``matmul_dtype`` optionally lowers the two big matmul inputs.
    """

    batch, seq_len, num_heads, head_dim = x.shape
    dt_dtype = dt.dtype
    dt = jax.nn.softplus(dt + dt_bias.astype(dt_dtype)).astype(dt_dtype)
    dt = jnp.clip(dt, dt_limit[0], dt_limit[1]).astype(jnp.float32)
    x = x.astype(jnp.float32)
    b_matrix = b_matrix.astype(jnp.float32)
    c_matrix = c_matrix.astype(jnp.float32)
    d = d.astype(jnp.float32)
    groups = b_matrix.shape[2]
    if num_heads % groups != 0:
        raise ValueError(f"{num_heads} heads are not divisible into {groups} groups")
    repeats = num_heads // groups
    state = b_matrix.shape[-1]

    pad_size = (chunk_size - seq_len % chunk_size) % chunk_size
    x_padded = _pad_sequence(x, pad_size)
    dt_padded = _pad_sequence(dt, pad_size)
    b_padded = _pad_sequence(b_matrix, pad_size)
    c_padded = _pad_sequence(c_matrix, pad_size)
    padded_len = seq_len + pad_size
    chunks = padded_len // chunk_size

    d_residual = d[None, None, :, None] * x_padded
    x_discrete = (x_padded * dt_padded[..., None]).reshape(
        batch, chunks, chunk_size, groups, repeats, head_dim
    )
    a_discrete = (a.astype(jnp.float32) * dt_padded).reshape(
        batch, chunks, chunk_size, groups, repeats
    )
    b_blocks = b_padded.reshape(batch, chunks, chunk_size, groups, state)
    c_blocks = c_padded.reshape(batch, chunks, chunk_size, groups, state)

    # Cumulative log-decay within each chunk, laid out [batch, chunk, group, head, q].
    cumsum = jnp.cumsum(a_discrete.transpose(0, 1, 3, 4, 2), axis=-1)
    causal = jnp.tril(jnp.ones((chunk_size, chunk_size), dtype=jnp.bool_))
    # Mask before the exponential: the upper triangle would overflow to inf and poison the
    # backward pass with 0 * inf; exp(-inf) is 0 with a zero gradient.
    within_decay = jnp.exp(
        jnp.where(causal, cumsum[..., :, None] - cumsum[..., None, :], -jnp.inf)
    )  # [b, c, g, r, i, j]

    cb = jnp.einsum(
        "bcign,bcjgn->bcgij", c_blocks, b_blocks, precision=precision
    )  # [b, c, g, i, j]
    mixed = within_decay * cb[:, :, :, None]  # [b, c, g, r, i, j]
    x_heads = x_discrete.transpose(0, 1, 3, 4, 2, 5)  # [b, c, g, r, j, p]
    if matmul_dtype is not None:
        mixed = mixed.astype(matmul_dtype)
        x_heads = x_heads.astype(matmul_dtype)
    y_diagonal = jnp.einsum(
        "bcgrij,bcgrjp->bcgrip", mixed, x_heads, precision=precision
    ).astype(jnp.float32)  # [b, c, g, r, i, p]

    # Chunk states: sum_j B_j exp(cs_end - cs_j) X_j  -> [b, c, g, r, n, p].
    decay_to_end = jnp.exp(cumsum[..., -1:] - cumsum)  # [b, c, g, r, j]
    weighted_x = x_heads * decay_to_end[..., None]  # [b, c, g, r, j, p]
    states = jnp.einsum(
        "bcjgn,bcgrjp->bcgrnp",
        b_blocks,
        weighted_x.astype(jnp.float32),
        precision=precision,
    )
    chunk_end_decay = jnp.exp(cumsum[..., -1])  # [b, c, g, r]

    def carry_step(carry, inputs):
        end_decay, chunk_state = inputs
        boundary = carry
        carry = boundary * end_decay[..., None, None] + chunk_state
        return carry, boundary

    _, boundary_states = jax.lax.scan(
        carry_step,
        jnp.zeros((batch, groups, repeats, state, head_dim), jnp.float32),
        (chunk_end_decay.transpose(1, 0, 2, 3), states.transpose(1, 0, 2, 3, 4, 5)),
    )
    boundary_states = boundary_states.transpose(1, 0, 2, 3, 4, 5)  # [b, c, g, r, n, p]

    y_off_diagonal = jnp.einsum(
        "bcign,bcgrnp,bcgri->bcgrip",
        c_blocks,
        boundary_states,
        jnp.exp(cumsum),
        precision=precision,
    )
    output = (y_diagonal + y_off_diagonal).transpose(
        0, 1, 4, 2, 3, 5
    )  # [b, c, i, g, r, p]
    output = output.reshape(batch, padded_len, num_heads, head_dim) + d_residual
    return output[:, :seq_len]


def _depthwise_causal_conv(
    x: Array, weight: Array, bias: Array | None, kernel_size: int
) -> Array:
    """PyTorch Conv1d cross-correlation with causal left padding."""

    seq_len = x.shape[1]
    padded = jnp.pad(x, ((0, 0), (kernel_size - 1, 0), (0, 0)))
    kernel = weight[:, 0, :].astype(x.dtype).T
    output = sum(
        padded[:, offset : offset + seq_len, :] * kernel[offset][None, None, :]
        for offset in range(kernel_size)
    )
    if bias is not None:
        output = output + bias.astype(x.dtype)
    return jax.nn.silu(output)


def _mup_vector(cfg: FalconH1Config, dtype: jnp.dtype) -> Array:
    sizes = (
        cfg.mamba_d_ssm,
        cfg.mamba_d_ssm,
        cfg.mamba_group_state_size,
        cfg.mamba_group_state_size,
        cfg.mamba_n_heads,
    )
    return jnp.concatenate(
        [
            jnp.full((size,), multiplier, dtype=dtype)
            for size, multiplier in zip(sizes, cfg.ssm_multipliers)
        ]
    )


def mamba(
    layer: Params,
    x: Array,
    cfg: FalconH1Config,
    *,
    ssd_precision: jax.lax.Precision = jax.lax.Precision.DEFAULT,
) -> Array:
    projected = _linear(
        x * jnp.asarray(cfg.ssm_in_multiplier, x.dtype),
        layer["mamba.in_proj.weight"],
        layer.get("mamba.in_proj.bias"),
    )
    projected = projected * _mup_vector(cfg, projected.dtype)
    gate, conv_input, dt = jnp.split(
        projected,
        (cfg.mamba_d_ssm, cfg.mamba_d_ssm + cfg.mamba_conv_dim),
        axis=-1,
    )
    convolved = _depthwise_causal_conv(
        conv_input,
        layer["mamba.conv1d.weight"],
        layer.get("mamba.conv1d.bias"),
        cfg.mamba_d_conv,
    )
    hidden, b_matrix, c_matrix = jnp.split(
        convolved,
        (
            cfg.mamba_d_ssm,
            cfg.mamba_d_ssm + cfg.mamba_group_state_size,
        ),
        axis=-1,
    )
    batch, seq_len, _ = hidden.shape
    hidden = hidden.reshape(batch, seq_len, cfg.mamba_n_heads, cfg.mamba_d_head)
    b_matrix = b_matrix.reshape(batch, seq_len, cfg.mamba_n_groups, cfg.mamba_d_state)
    c_matrix = c_matrix.reshape(batch, seq_len, cfg.mamba_n_groups, cfg.mamba_d_state)
    a = -jnp.exp(layer["mamba.A_log"].astype(jnp.float32))
    if SSD_IMPLEMENTATION == "v2":
        scanned = ssd_forward_v2(
            hidden,
            dt,
            a,
            b_matrix,
            c_matrix,
            cfg.mamba_chunk_size,
            layer["mamba.D"],
            layer["mamba.dt_bias"],
            cfg.time_step_limit,
            precision=ssd_precision,
            matmul_dtype=SSD_MATMUL_DTYPE,
        ).reshape(batch, seq_len, cfg.mamba_d_ssm)
    else:
        head_repeats = cfg.mamba_n_heads // cfg.mamba_n_groups
        b_matrix = jnp.repeat(b_matrix, head_repeats, axis=2)
        c_matrix = jnp.repeat(c_matrix, head_repeats, axis=2)
        scanned = ssd_forward(
            hidden,
            dt,
            a,
            b_matrix,
            c_matrix,
            cfg.mamba_chunk_size,
            layer["mamba.D"],
            layer["mamba.dt_bias"],
            cfg.time_step_limit,
            precision=ssd_precision,
        ).reshape(batch, seq_len, cfg.mamba_d_ssm)
    if cfg.mamba_rms_norm:
        if not cfg.mamba_norm_before_gate:
            scanned = scanned * jax.nn.silu(gate.astype(jnp.float32))
        scanned = _rms_norm(scanned, layer["mamba.norm.weight"], cfg.rms_norm_eps)
        if cfg.mamba_norm_before_gate:
            scanned = scanned * jax.nn.silu(gate.astype(jnp.float32))
    else:
        scanned = scanned * jax.nn.silu(gate)
    return _linear(
        scanned.astype(x.dtype),
        layer["mamba.out_proj.weight"],
        layer.get("mamba.out_proj.bias"),
    )


def mlp(layer: Params, x: Array, cfg: FalconH1Config) -> Array:
    gate = _linear(
        x,
        layer["feed_forward.gate_proj.weight"],
        layer.get("feed_forward.gate_proj.bias"),
    )
    up = _linear(
        x, layer["feed_forward.up_proj.weight"], layer.get("feed_forward.up_proj.bias")
    )
    hidden = up * jax.nn.silu(gate * jnp.asarray(cfg.mlp_multipliers[0], x.dtype))
    return _linear(
        hidden,
        layer["feed_forward.down_proj.weight"],
        layer.get("feed_forward.down_proj.bias"),
    ) * jnp.asarray(cfg.mlp_multipliers[1], x.dtype)


def decoder_layer(
    layer: Params,
    hidden: Array,
    cfg: FalconH1Config,
    *,
    ssd_precision: jax.lax.Precision = jax.lax.Precision.DEFAULT,
) -> Array:
    residual = hidden
    normalized = _rms_norm(hidden, layer["input_layernorm.weight"], cfg.rms_norm_eps)
    mamba_output = mamba(
        layer, normalized, cfg, ssd_precision=ssd_precision
    ) * jnp.asarray(cfg.ssm_out_multiplier, hidden.dtype)
    attention_output = attention(
        layer,
        normalized * jnp.asarray(cfg.attention_in_multiplier, hidden.dtype),
        cfg,
    ) * jnp.asarray(cfg.attention_out_multiplier, hidden.dtype)
    hidden = residual + mamba_output + attention_output
    return hidden + mlp(
        layer,
        _rms_norm(hidden, layer["pre_ff_layernorm.weight"], cfg.rms_norm_eps),
        cfg,
    )


def _layer_params(params: Params, index: int) -> dict[str, Array]:
    prefix = f"model.layers.{index}."
    return {
        key[len(prefix) :]: value
        for key, value in params.items()
        if key.startswith(prefix)
    }


def stacked_layer_params(params: Params, cfg: FalconH1Config) -> dict[str, Array]:
    """Stack every per-layer tensor along a new leading layer axis for `lax.scan`."""

    prefix = "model.layers.0."
    names = sorted(key[len(prefix) :] for key in params if key.startswith(prefix))
    return {
        name: jnp.stack(
            [
                params[f"model.layers.{index}.{name}"]
                for index in range(cfg.num_hidden_layers)
            ]
        )
        for name in names
    }


def falcon_h1_forward(
    params: Params,
    input_ids: Array,
    cfg: FalconH1Config,
    *,
    compute_dtype: jnp.dtype = jnp.bfloat16,
    gradient_checkpointing: bool = False,
    ssd_precision: jax.lax.Precision = jax.lax.Precision.DEFAULT,
    layer_scan: bool = False,
    return_hidden: bool = False,
) -> Array | tuple[Array, Array]:
    """Full forward pass to logits (and, with `return_hidden`, the final normalized hidden state).

    `layer_scan=True` runs the decoder stack as one `lax.scan` over stacked layer parameters
    instead of unrolling 24 copies of the layer graph. The arithmetic is identical; the traced
    program and XLA compile cost stop growing with depth, which matters on TPU where the
    unrolled 24-layer training step exhausted the host during compilation.
    """

    hidden = params["model.embed_tokens.weight"][input_ids].astype(compute_dtype)
    hidden = hidden * jnp.asarray(cfg.embedding_multiplier, compute_dtype)
    apply_layer = partial(decoder_layer, cfg=cfg, ssd_precision=ssd_precision)
    if layer_scan:

        def body(carry: Array, layer: dict[str, Array]) -> tuple[Array, None]:
            return apply_layer(layer, carry), None

        if gradient_checkpointing:
            policy = _remat_policy()
            body = (
                jax.checkpoint(body, policy=policy) if policy else jax.checkpoint(body)
            )
        hidden, _ = jax.lax.scan(body, hidden, stacked_layer_params(params, cfg))
    else:
        if gradient_checkpointing:
            apply_layer = jax.checkpoint(apply_layer)
        for index in range(cfg.num_hidden_layers):
            hidden = apply_layer(_layer_params(params, index), hidden)
    hidden = _rms_norm(hidden, params["model.final_layernorm.weight"], cfg.rms_norm_eps)
    lm_head = (
        params["model.embed_tokens.weight"]
        if cfg.tie_word_embeddings
        else params["lm_head.weight"]
    )
    logits = _linear(hidden, lm_head) * jnp.asarray(
        cfg.lm_head_multiplier, hidden.dtype
    )
    if return_hidden:
        return logits, hidden
    return logits


def causal_lm_loss(
    params: Params,
    tokens: Array,
    cfg: FalconH1Config,
    *,
    compute_dtype: jnp.dtype = jnp.bfloat16,
    gradient_checkpointing: bool = True,
    layer_scan: bool = False,
) -> tuple[Array, dict[str, Array]]:
    logits = falcon_h1_forward(
        params,
        tokens[:, :-1],
        cfg,
        compute_dtype=compute_dtype,
        gradient_checkpointing=gradient_checkpointing,
        layer_scan=layer_scan,
    ).astype(jnp.float32)
    labels = tokens[:, 1:]
    log_normalizer = jax.nn.logsumexp(logits, axis=-1)
    selected = jnp.take_along_axis(logits, labels[..., None], axis=-1)[..., 0]
    losses = log_normalizer - selected
    loss = jnp.mean(losses)
    accuracy = jnp.mean(jnp.argmax(logits, axis=-1) == labels)
    return loss, {"loss": loss, "accuracy": accuracy}


def count_parameters(params: Params) -> int:
    return sum(int(value.size) for value in jax.tree_util.tree_leaves(params))


def parameter_count_for_config(cfg: FalconH1Config) -> int:
    """Count parameters from shapes without allocating a model."""

    total = cfg.vocab_size * cfg.hidden_size + cfg.hidden_size
    if not cfg.tie_word_embeddings:
        total += cfg.vocab_size * cfg.hidden_size
    layer = 2 * cfg.hidden_size
    layer += cfg.hidden_size * cfg.attention_width
    layer += 2 * cfg.hidden_size * cfg.num_key_value_heads * cfg.head_dim
    layer += cfg.hidden_size * cfg.attention_width
    if cfg.attention_bias:
        layer += (
            2 * cfg.num_attention_heads * cfg.head_dim
            + 2 * cfg.num_key_value_heads * cfg.head_dim
        )
    layer += 3 * cfg.hidden_size * cfg.intermediate_size
    if cfg.mlp_bias:
        layer += 2 * cfg.intermediate_size + cfg.hidden_size
    layer += cfg.mamba_projection_size * cfg.hidden_size
    layer += cfg.hidden_size * cfg.mamba_d_ssm
    if cfg.mamba_proj_bias:
        layer += cfg.mamba_projection_size
    if cfg.projectors_bias:
        layer += cfg.hidden_size
    layer += cfg.mamba_conv_dim * cfg.mamba_d_conv
    if cfg.mamba_conv_bias:
        layer += cfg.mamba_conv_dim
    layer += 3 * cfg.mamba_n_heads
    if cfg.mamba_rms_norm:
        layer += cfg.mamba_d_ssm
    return total + cfg.num_hidden_layers * layer


def _normal(rng: np.random.Generator, shape: tuple[int, ...], std: float) -> Array:
    return jnp.asarray(rng.normal(0.0, std, shape).astype(np.float32))


def init_params(cfg: FalconH1Config, seed: int = 0) -> dict[str, Array]:
    """Initialize in Hugging Face tensor layout, including Falcon-H1 SSM constants."""

    rng = np.random.default_rng(seed)
    params: dict[str, Array] = {}
    embedding = rng.normal(
        0.0, cfg.initializer_range, (cfg.vocab_size, cfg.hidden_size)
    ).astype(np.float32)
    if 0 <= cfg.pad_token_id < cfg.vocab_size:
        embedding[cfg.pad_token_id] = 0
    params["model.embed_tokens.weight"] = jnp.asarray(embedding)
    for index in range(cfg.num_hidden_layers):
        prefix = f"model.layers.{index}."
        params[prefix + "input_layernorm.weight"] = jnp.ones(
            (cfg.hidden_size,), jnp.float32
        )
        params[prefix + "pre_ff_layernorm.weight"] = jnp.ones(
            (cfg.hidden_size,), jnp.float32
        )
        for name, output, input_size in (
            ("self_attn.q_proj.weight", cfg.attention_width, cfg.hidden_size),
            (
                "self_attn.k_proj.weight",
                cfg.num_key_value_heads * cfg.head_dim,
                cfg.hidden_size,
            ),
            (
                "self_attn.v_proj.weight",
                cfg.num_key_value_heads * cfg.head_dim,
                cfg.hidden_size,
            ),
            ("self_attn.o_proj.weight", cfg.hidden_size, cfg.attention_width),
            ("feed_forward.gate_proj.weight", cfg.intermediate_size, cfg.hidden_size),
            ("feed_forward.up_proj.weight", cfg.intermediate_size, cfg.hidden_size),
            ("feed_forward.down_proj.weight", cfg.hidden_size, cfg.intermediate_size),
            ("mamba.in_proj.weight", cfg.mamba_projection_size, cfg.hidden_size),
            ("mamba.out_proj.weight", cfg.hidden_size, cfg.mamba_d_ssm),
        ):
            params[prefix + name] = _normal(
                rng, (output, input_size), cfg.initializer_range
            )
        if cfg.attention_bias:
            for name, size in (
                ("self_attn.q_proj.bias", cfg.attention_width),
                ("self_attn.k_proj.bias", cfg.num_key_value_heads * cfg.head_dim),
                ("self_attn.v_proj.bias", cfg.num_key_value_heads * cfg.head_dim),
                ("self_attn.o_proj.bias", cfg.hidden_size),
            ):
                params[prefix + name] = jnp.zeros((size,), jnp.float32)
        if cfg.mlp_bias:
            for name, size in (
                ("feed_forward.gate_proj.bias", cfg.intermediate_size),
                ("feed_forward.up_proj.bias", cfg.intermediate_size),
                ("feed_forward.down_proj.bias", cfg.hidden_size),
            ):
                params[prefix + name] = jnp.zeros((size,), jnp.float32)
        if cfg.mamba_proj_bias:
            params[prefix + "mamba.in_proj.bias"] = jnp.zeros(
                (cfg.mamba_projection_size,), jnp.float32
            )
        if cfg.projectors_bias:
            params[prefix + "mamba.out_proj.bias"] = jnp.zeros(
                (cfg.hidden_size,), jnp.float32
            )
        params[prefix + "mamba.conv1d.weight"] = _normal(
            rng, (cfg.mamba_conv_dim, 1, cfg.mamba_d_conv), cfg.initializer_range
        )
        if cfg.mamba_conv_bias:
            params[prefix + "mamba.conv1d.bias"] = jnp.zeros(
                (cfg.mamba_conv_dim,), jnp.float32
            )
        params[prefix + "mamba.A_log"] = jnp.log(
            jnp.arange(1, cfg.mamba_n_heads + 1, dtype=jnp.float32)
        )
        params[prefix + "mamba.D"] = jnp.ones((cfg.mamba_n_heads,), jnp.float32)
        params[prefix + "mamba.dt_bias"] = jnp.ones((cfg.mamba_n_heads,), jnp.float32)
        if cfg.mamba_rms_norm:
            params[prefix + "mamba.norm.weight"] = jnp.ones(
                (cfg.mamba_d_ssm,), jnp.float32
            )
    params["model.final_layernorm.weight"] = jnp.ones((cfg.hidden_size,), jnp.float32)
    if not cfg.tie_word_embeddings:
        params["lm_head.weight"] = _normal(
            rng, (cfg.vocab_size, cfg.hidden_size), cfg.initializer_range
        )
    return params
