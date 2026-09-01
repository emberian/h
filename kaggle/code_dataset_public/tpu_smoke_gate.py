from __future__ import annotations

import glob
import json
import os
from pathlib import Path
import subprocess
import sys


os.environ.setdefault("JAX_COMPILATION_CACHE_DIR", "/kaggle/working/jax-cache")
wheel = [
    path
    for path in glob.glob("/kaggle/input/**/*.whl", recursive=True)
    if Path(path).name.startswith("hghost_jax-")
]
if len(wheel) != 1:
    raise RuntimeError(f"Expected one hghost-jax wheel, found: {wheel}")
subprocess.run(
    [sys.executable, "-m", "pip", "install", "--no-deps", "--quiet", wheel[0]],
    check=True,
)

import jax
import numpy as np

from h1jax.config import FalconH1Config
from h1jax.model import parameter_count_for_config
from h1jax.train import build_parser, run


print(
    {
        "jax": jax.__version__,
        "backend": jax.default_backend(),
        "device_count": jax.device_count(),
        "devices": [str(device) for device in jax.devices()],
    },
    flush=True,
)
if jax.default_backend() != "tpu" or jax.device_count() != 8:
    raise RuntimeError("This gate requires the complete TPU v5e-8 slice")

working = Path("/kaggle/working/smoke-input")
working.mkdir(parents=True, exist_ok=True)
cfg = FalconH1Config()
parameter_count = parameter_count_for_config(cfg)
if parameter_count != 91_131_072:
    raise RuntimeError(f"Unexpected full-model parameter count: {parameter_count}")
cfg.to_json(working / "config.json")
sequence_length = 512
per_device_batch = 4
steps = 2
total_tokens = jax.device_count() * per_device_batch * sequence_length * steps
rng = np.random.default_rng(20260901)
rng.integers(0, cfg.vocab_size, size=total_tokens * 4, dtype=np.uint16).tofile(
    working / "train.bin"
)

arguments = build_parser().parse_args(
    [
        "--config",
        str(working / "config.json"),
        "--train-bin",
        str(working / "train.bin"),
        "--random-init",
        "--output",
        "/kaggle/working/h1jax-smoke-output",
        "--sequence-length",
        str(sequence_length),
        "--per-device-batch",
        str(per_device_batch),
        "--accumulation-steps",
        "1",
        "--total-tokens",
        str(total_tokens),
        "--warmup-tokens",
        str(jax.device_count() * sequence_length),
        "--learning-rate",
        "0.001",
        "--dtype",
        "bfloat16",
        "--save-tokens",
        "",
        "--no-save-final-checkpoint",
        "--log-steps",
        "1",
    ]
)
run(arguments)
completion = json.loads(
    Path("/kaggle/working/h1jax-smoke-output/training-complete.json").read_text(
        encoding="utf-8"
    )
)
if completion.get("completed") is not True or int(completion.get("steps", -1)) != steps:
    raise RuntimeError(f"Smoke trainer did not complete exactly {steps} updates: {completion}")
report = {
    "ok": True,
    "backend": jax.default_backend(),
    "device_count": jax.device_count(),
    "parameters": parameter_count,
    "sequence_length": sequence_length,
    "per_device_batch": per_device_batch,
    "steps": steps,
    "tokens": total_tokens,
    "completion": completion,
}
Path("/kaggle/working/tpu-smoke-report.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8"
)
print("TPU_V5E8_SMOKE_OK", flush=True)
