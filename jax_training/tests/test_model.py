from __future__ import annotations

import json
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import pytest
from h1jax.config import FalconH1Config, born_10m_config, born_20m_config
from h1jax.model import (
    causal_lm_loss,
    count_parameters,
    falcon_h1_forward,
    init_params,
    parameter_count_for_config,
    ssd_forward,
)
from h1jax.train import _resume_compatibility, build_parser, run


def tiny_config() -> FalconH1Config:
    return FalconH1Config(
        vocab_size=128,
        hidden_size=64,
        num_hidden_layers=2,
        num_attention_heads=4,
        num_key_value_heads=2,
        head_dim=16,
        intermediate_size=96,
        mamba_d_ssm=96,
        mamba_d_state=8,
        mamba_d_head=16,
        mamba_n_heads=6,
        mamba_n_groups=1,
        mamba_d_conv=4,
        mamba_chunk_size=4,
        rope_theta=10000.0,
    )


def test_preset_parameter_counts() -> None:
    assert parameter_count_for_config(born_10m_config()) == 9_856_488
    assert parameter_count_for_config(born_20m_config()) == 19_511_990
    assert parameter_count_for_config(FalconH1Config()) == 91_131_072


def test_official_half_billion_config_parameter_count() -> None:
    root = Path(__file__).resolve().parents[2]
    cfg = FalconH1Config.from_json(
        root / "research/sources/model_configs/falcon_h1_0.5b_base_config.json"
    )
    assert cfg.attention_width == 512
    assert cfg.hidden_size == 1024
    assert not cfg.tie_word_embeddings
    assert parameter_count_for_config(cfg) == 521_411_104


def test_forward_loss_and_gradient() -> None:
    cfg = tiny_config()
    params = init_params(cfg, seed=3)
    tokens = jnp.arange(18, dtype=jnp.int32).reshape(2, 9) % cfg.vocab_size
    logits = falcon_h1_forward(params, tokens[:, :-1], cfg, compute_dtype=jnp.float32)
    assert logits.shape == (2, 8, cfg.vocab_size)
    assert bool(jnp.all(jnp.isfinite(logits)))
    (loss, _), grads = jax.value_and_grad(causal_lm_loss, has_aux=True)(
        params, tokens, cfg, compute_dtype=jnp.float32, gradient_checkpointing=True
    )
    assert bool(jnp.isfinite(loss))
    assert (
        float(
            jax.tree_util.tree_reduce(
                lambda total, x: total + jnp.sum(x * x), grads, 0.0
            )
        )
        > 0
    )
    assert count_parameters(params) > 0


def test_attention_width_can_be_narrower_than_hidden_size() -> None:
    cfg = FalconH1Config(
        vocab_size=128,
        hidden_size=64,
        num_hidden_layers=1,
        num_attention_heads=2,
        num_key_value_heads=1,
        head_dim=16,
        intermediate_size=96,
        mamba_d_ssm=96,
        mamba_d_state=8,
        mamba_d_head=16,
        mamba_n_heads=6,
        mamba_n_groups=1,
        mamba_d_conv=4,
        mamba_chunk_size=4,
        rope_theta=10000.0,
    )
    params = init_params(cfg, seed=4)
    tokens = jnp.arange(8, dtype=jnp.int32).reshape(1, 8)
    logits = falcon_h1_forward(params, tokens, cfg, compute_dtype=jnp.float32)
    assert cfg.attention_width == 32
    assert params["model.layers.0.self_attn.o_proj.weight"].shape == (64, 32)
    assert logits.shape == (1, 8, cfg.vocab_size)


def test_chunked_ssd_matches_recurrence() -> None:
    rng = np.random.default_rng(9)
    batch, length, heads, head_dim, state = 2, 9, 3, 4, 5
    x = jnp.asarray(rng.normal(size=(batch, length, heads, head_dim)), jnp.float32)
    dt = jnp.asarray(rng.normal(size=(batch, length, heads)), jnp.float32)
    a = -jnp.arange(1, heads + 1, dtype=jnp.float32)
    b = jnp.asarray(rng.normal(size=(batch, length, heads, state)), jnp.float32)
    c = jnp.asarray(rng.normal(size=(batch, length, heads, state)), jnp.float32)
    d = jnp.asarray(rng.normal(size=(heads,)), jnp.float32)
    dt_bias = jnp.asarray(rng.normal(size=(heads,)), jnp.float32)
    actual = ssd_forward(x, dt, a, b, c, 4, d, dt_bias, (0.0, float("inf")))

    discrete_dt = jax.nn.softplus(dt + dt_bias)
    recurrent_state = jnp.zeros((batch, heads, head_dim, state), jnp.float32)
    expected = []
    for index in range(length):
        decay = jnp.exp(discrete_dt[:, index] * a)[..., None, None]
        update = (
            x[:, index, :, :, None]
            * discrete_dt[:, index, :, None, None]
            * b[:, index, :, None, :]
        )
        recurrent_state = recurrent_state * decay + update
        output = jnp.einsum("bhpn,bhn->bhp", recurrent_state, c[:, index])
        expected.append(output + d[None, :, None] * x[:, index])
    expected = jnp.stack(expected, axis=1)
    np.testing.assert_allclose(actual, expected, atol=2e-5, rtol=2e-5)


def _training_args(tmp_path, cfg_path, train_path, output, *extra):
    return build_parser().parse_args(
        [
            "--config",
            str(cfg_path),
            "--train-bin",
            str(train_path),
            "--output",
            str(output),
            "--sequence-length",
            "8",
            "--per-device-batch",
            "1",
            "--accumulation-steps",
            "1",
            "--total-tokens",
            "32",
            "--warmup-tokens",
            "8",
            "--learning-rate",
            "0.001",
            "--dtype",
            "float32",
            "--save-tokens",
            "16,32",
            "--eval-every-tokens",
            "8",
            "--eval-batches",
            "1",
            "--log-steps",
            "1",
            *extra,
        ]
    )


def test_training_checkpoint_and_resume_are_complete(tmp_path, capsys) -> None:
    cfg = tiny_config()
    cfg_path = tmp_path / "config.json"
    cfg.to_json(cfg_path)
    train_path = tmp_path / "train.bin"
    (np.arange(256, dtype=np.uint16) % cfg.vocab_size).tofile(train_path)
    tokenizer = tmp_path / "tokenizer"
    tokenizer.mkdir()
    (tokenizer / "tokenizer.json").write_text("{}\n", encoding="utf-8")

    first_output = tmp_path / "first"
    run(
        _training_args(
            tmp_path,
            cfg_path,
            train_path,
            first_output,
            "--random-init",
            "--validation-bin",
            str(train_path),
            "--tokenizer-dir",
            str(tokenizer),
        )
    )
    assert (first_output / "training-complete.json").is_file()
    checkpoint_16 = first_output / "tokens-000000000016"
    checkpoint_32 = first_output / "tokens-000000000032"
    for checkpoint in (checkpoint_16, checkpoint_32):
        assert (checkpoint / "model.safetensors").is_file()
        assert (checkpoint / "optimizer.msgpack").is_file()
        assert (checkpoint / "trainer_state.json").is_file()
        assert (checkpoint / "tokenizer.json").is_file()

    capsys.readouterr()
    resumed_output = tmp_path / "resumed"
    run(
        _training_args(
            tmp_path,
            cfg_path,
            train_path,
            resumed_output,
            "--resume",
            str(checkpoint_16),
            "--validation-bin",
            str(train_path),
        )
    )
    events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    validation_tokens = [
        event["tokens"] for event in events if event["event"] == "validation"
    ]
    assert validation_tokens == [24, 32]
    assert not (resumed_output / "tokens-000000000016").exists()
    assert (resumed_output / "tokens-000000000032" / "model.safetensors").is_file()


def test_resume_settings_must_match() -> None:
    with pytest.raises(ValueError, match="Resume settings"):
        _resume_compatibility({"sequence_length": 8}, {"sequence_length": 16})


@pytest.mark.parametrize("remat", [False, True])
def test_layer_scan_matches_unrolled(remat: bool) -> None:
    cfg = tiny_config()
    params = init_params(cfg, seed=3)
    tokens = jnp.asarray(
        np.random.default_rng(5).integers(0, cfg.vocab_size, (2, 9)), dtype=jnp.int32
    )
    unrolled_logits = falcon_h1_forward(
        params, tokens, cfg, compute_dtype=jnp.float32, gradient_checkpointing=remat
    )
    scanned_logits = falcon_h1_forward(
        params,
        tokens,
        cfg,
        compute_dtype=jnp.float32,
        gradient_checkpointing=remat,
        layer_scan=True,
    )
    np.testing.assert_allclose(
        np.asarray(scanned_logits), np.asarray(unrolled_logits), rtol=1e-5, atol=1e-5
    )

    def loss(p, scan):
        return causal_lm_loss(
            p,
            tokens,
            cfg,
            compute_dtype=jnp.float32,
            gradient_checkpointing=remat,
            layer_scan=scan,
        )[0]

    unrolled_loss, unrolled_grads = jax.value_and_grad(loss)(params, False)
    scanned_loss, scanned_grads = jax.value_and_grad(loss)(params, True)
    assert abs(float(unrolled_loss) - float(scanned_loss)) < 1e-5
    for key in params:
        np.testing.assert_allclose(
            np.asarray(scanned_grads[key]),
            np.asarray(unrolled_grads[key]),
            rtol=1e-4,
            atol=1e-5,
            err_msg=key,
        )


def test_ssd_forward_v2_matches_reference() -> None:
    from h1jax.model import ssd_forward, ssd_forward_v2

    rng = np.random.default_rng(0)
    batch, seq_len, heads, head_dim, state, groups, chunk = 2, 300, 6, 8, 16, 2, 128
    x = jnp.asarray(
        rng.standard_normal((batch, seq_len, heads, head_dim), dtype=np.float32)
    )
    dt = jnp.asarray(rng.standard_normal((batch, seq_len, heads), dtype=np.float32))
    a = -jnp.exp(jnp.asarray(rng.standard_normal(heads, dtype=np.float32)))
    b_groups = jnp.asarray(
        rng.standard_normal((batch, seq_len, groups, state), dtype=np.float32)
    )
    c_groups = jnp.asarray(
        rng.standard_normal((batch, seq_len, groups, state), dtype=np.float32)
    )
    d = jnp.asarray(rng.standard_normal(heads, dtype=np.float32))
    dt_bias = jnp.asarray(rng.standard_normal(heads, dtype=np.float32))
    limit = (0.0, float("inf"))
    repeats = heads // groups
    b_heads = jnp.repeat(b_groups, repeats, axis=2)
    c_heads = jnp.repeat(c_groups, repeats, axis=2)

    def reference(x_, dt_, b_, c_):
        return jnp.sum(
            jnp.sin(ssd_forward(x_, dt_, a, b_, c_, chunk, d, dt_bias, limit))
        )

    def rewrite(x_, dt_, b_, c_):
        return jnp.sum(
            jnp.sin(ssd_forward_v2(x_, dt_, a, b_, c_, chunk, d, dt_bias, limit))
        )

    y1 = ssd_forward(x, dt, a, b_heads, c_heads, chunk, d, dt_bias, limit)
    y2 = ssd_forward_v2(x, dt, a, b_groups, c_groups, chunk, d, dt_bias, limit)
    scale = float(jnp.max(jnp.abs(y1)))
    assert float(jnp.max(jnp.abs(y1 - y2))) / scale < 1e-4

    g1 = jax.grad(reference, argnums=(0, 1, 2, 3))(x, dt, b_heads, c_heads)
    g2 = jax.grad(rewrite, argnums=(0, 1, 2, 3))(x, dt, b_groups, c_groups)
    g1_b = g1[2].reshape(batch, seq_len, groups, repeats, state).sum(3)
    g1_c = g1[3].reshape(batch, seq_len, groups, repeats, state).sum(3)
    for expected, actual in (
        (g1[0], g2[0]),
        (g1[1], g2[1]),
        (g1_b, g2[2]),
        (g1_c, g2[3]),
    ):
        assert bool(jnp.all(jnp.isfinite(actual)))
        assert (
            float(jnp.max(jnp.abs(expected - actual)))
            / float(jnp.max(jnp.abs(expected)))
            < 1e-3
        )
