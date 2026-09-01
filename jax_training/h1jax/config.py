from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any


@dataclasses.dataclass(frozen=True)
class FalconH1Config:
    """The training-relevant subset of a Hugging Face Falcon-H1 config."""

    vocab_size: int = 32768
    hidden_size: int = 512
    num_hidden_layers: int = 24
    num_attention_heads: int = 8
    num_key_value_heads: int = 2
    head_dim: int = 64
    intermediate_size: int = 768
    hidden_act: str = "silu"
    rms_norm_eps: float = 1e-5
    rope_theta: float = 100_000_000_000.0
    max_position_embeddings: int = 262144
    attention_bias: bool = False
    attention_dropout: float = 0.0
    mlp_bias: bool = False
    projectors_bias: bool = False
    mamba_proj_bias: bool = False
    mamba_conv_bias: bool = True
    mamba_d_ssm: int = 768
    mamba_d_state: int = 64
    mamba_d_head: int = 32
    mamba_n_heads: int = 24
    mamba_n_groups: int = 1
    mamba_d_conv: int = 4
    mamba_chunk_size: int = 128
    mamba_rms_norm: bool = False
    mamba_norm_before_gate: bool = False
    tie_word_embeddings: bool = True
    pad_token_id: int = 0
    bos_token_id: int = 1
    eos_token_id: int = 11
    initializer_range: float = 0.02
    embedding_multiplier: float = 1.0
    lm_head_multiplier: float = 1.0
    key_multiplier: float = 1.0
    attention_in_multiplier: float = 1.0
    attention_out_multiplier: float = 1.0
    ssm_in_multiplier: float = 1.0
    ssm_out_multiplier: float = 1.0
    mlp_multipliers: tuple[float, float] = (1.0, 1.0)
    ssm_multipliers: tuple[float, float, float, float, float] = (
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    )
    time_step_min: float = 0.001
    time_step_max: float = 0.1
    time_step_floor: float = 0.0001
    time_step_limit: tuple[float, float] = (0.0, float("inf"))

    def __post_init__(self) -> None:
        if self.hidden_act != "silu":
            raise ValueError("Only Falcon-H1's silu activation is implemented")
        if self.num_attention_heads * self.head_dim != self.hidden_size:
            raise ValueError("num_attention_heads * head_dim must equal hidden_size")
        if self.num_attention_heads % self.num_key_value_heads:
            raise ValueError("num_attention_heads must be divisible by num_key_value_heads")
        if self.mamba_n_heads * self.mamba_d_head != self.mamba_d_ssm:
            raise ValueError("mamba_n_heads * mamba_d_head must equal mamba_d_ssm")
        if len(self.mlp_multipliers) != 2 or len(self.ssm_multipliers) != 5:
            raise ValueError("Falcon-H1 expects 2 MLP and 5 SSM multipliers")

    @property
    def mamba_group_state_size(self) -> int:
        return self.mamba_n_groups * self.mamba_d_state

    @property
    def mamba_conv_dim(self) -> int:
        return self.mamba_d_ssm + 2 * self.mamba_group_state_size

    @property
    def mamba_projection_size(self) -> int:
        return self.mamba_d_ssm + self.mamba_conv_dim + self.mamba_n_heads

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "FalconH1Config":
        fields = {field.name for field in dataclasses.fields(cls)}
        selected = {key: value for key, value in values.items() if key in fields}
        for key in ("mlp_multipliers", "ssm_multipliers", "time_step_limit"):
            if key in selected and selected[key] is not None:
                selected[key] = tuple(selected[key])
        return cls(**selected)

    @classmethod
    def from_json(cls, path: str | Path) -> "FalconH1Config":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def to_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")


def born_10m_config(vocab_size: int = 8192) -> FalconH1Config:
    """9.86M parameter corpus-native model (with tied embeddings)."""

    return FalconH1Config(
        vocab_size=vocab_size,
        hidden_size=256,
        num_hidden_layers=10,
        num_attention_heads=4,
        num_key_value_heads=1,
        head_dim=64,
        intermediate_size=384,
        mamba_d_ssm=384,
        mamba_d_state=32,
        mamba_d_head=32,
        mamba_n_heads=12,
        mamba_d_conv=4,
        mamba_chunk_size=128,
        rope_theta=100_000.0,
        eos_token_id=2,
        bos_token_id=1,
    )


def born_20m_config(vocab_size: int = 8192) -> FalconH1Config:
    """19.51M parameter corpus-native model (with tied embeddings)."""

    return FalconH1Config(
        vocab_size=vocab_size,
        hidden_size=320,
        num_hidden_layers=14,
        num_attention_heads=5,
        num_key_value_heads=1,
        head_dim=64,
        intermediate_size=480,
        mamba_d_ssm=480,
        mamba_d_state=48,
        mamba_d_head=32,
        mamba_n_heads=15,
        mamba_d_conv=4,
        mamba_chunk_size=128,
        rope_theta=100_000.0,
        eos_token_id=2,
        bos_token_id=1,
    )
