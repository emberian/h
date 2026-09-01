"""Two-step full-backward gate for the official Falcon-H1 0.5B checkpoint."""

from __future__ import annotations

import glob
import json
import os
from pathlib import Path
import subprocess
import sys


os.environ.setdefault("JAX_COMPILATION_CACHE_DIR", "/kaggle/working/jax-cache")


def exactly_one(pattern: str) -> Path:
    matches = [Path(path) for path in glob.glob(pattern, recursive=True)]
    matches = [path for path in matches if path.is_file()]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {pattern!r}, found: {matches}")
    return matches[0]


wheel = exactly_one("/kaggle/input/**/hghost_jax-*.whl")
subprocess.run(
    [sys.executable, "-m", "pip", "install", "--no-deps", "--quiet", str(wheel)],
    check=True,
)

import jax

from h1jax.config import FalconH1Config
from h1jax.model import parameter_count_for_config
from h1jax.train import build_parser, run


hardware = {
    "jax": jax.__version__,
    "backend": jax.default_backend(),
    "device_count": jax.device_count(),
    "devices": [str(device) for device in jax.devices()],
}
print(json.dumps({"event": "hardware", **hardware}), flush=True)
if hardware["backend"] != "tpu" or hardware["device_count"] != 8:
    raise RuntimeError("This gate requires the complete TPU v5e-8 slice")

checkpoint_file = exactly_one("/kaggle/input/**/model.safetensors")
checkpoint = checkpoint_file.parent
config_path = checkpoint / "config.json"
train_bin = exactly_one("/kaggle/input/**/train.bin")
cfg = FalconH1Config.from_json(config_path)
parameters = parameter_count_for_config(cfg)
if parameters != 521_411_104:
    raise RuntimeError(f"Unexpected 0.5B parameter count: {parameters}")
if cfg.hidden_size != 1024 or cfg.attention_width != 512:
    raise RuntimeError(
        f"Unexpected residual/attention widths: {cfg.hidden_size}/{cfg.attention_width}"
    )

sequence_length = 512
per_device_batch = 1
steps = 2
tokens_per_step = jax.device_count() * per_device_batch * sequence_length
total_tokens = tokens_per_step * steps
output = Path("/kaggle/working/h1-05b-smoke-output")
arguments = build_parser().parse_args(
    [
        "--config",
        str(config_path),
        "--checkpoint",
        str(checkpoint),
        "--train-bin",
        str(train_bin),
        "--output",
        str(output),
        "--sequence-length",
        str(sequence_length),
        "--per-device-batch",
        str(per_device_batch),
        "--accumulation-steps",
        "1",
        "--total-tokens",
        str(total_tokens),
        "--warmup-tokens",
        str(tokens_per_step),
        "--learning-rate",
        "0.00003",
        "--dtype",
        "bfloat16",
        "--gradient-checkpointing",
        "--save-tokens",
        "",
        "--no-save-final-checkpoint",
        "--log-steps",
        "1",
    ]
)
run(arguments)
completion = json.loads(
    (output / "training-complete.json").read_text(encoding="utf-8")
)
if completion.get("completed") is not True or int(completion.get("steps", -1)) != steps:
    raise RuntimeError(f"0.5B smoke did not complete exactly {steps} updates: {completion}")
report = {
    "ok": True,
    **hardware,
    "parameters": parameters,
    "hidden_size": cfg.hidden_size,
    "attention_width": cfg.attention_width,
    "sequence_length": sequence_length,
    "per_device_batch": per_device_batch,
    "gradient_checkpointing": True,
    "steps": steps,
    "tokens": total_tokens,
    "completion": completion,
}
Path("/kaggle/working/tpu-05b-smoke-report.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8"
)
print("TPU_V5E8_FALCON_H1_05B_SMOKE_OK", flush=True)
