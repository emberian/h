"""One-shot TPU production run. Do not push until every local gate passes."""

from __future__ import annotations

import glob
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


os.environ.setdefault("JAX_COMPILATION_CACHE_DIR", "/kaggle/working/jax-cache")

TOTAL_TOKENS = 374_405_120
SEQUENCE_LENGTH = 512
PER_DEVICE_BATCH = 4
ACCUMULATION_STEPS = 1
SAVE_TOKENS = (10_000_000, 30_000_000, 100_000_000, 300_000_000, TOTAL_TOKENS)


def exactly_one(pattern: str, *, startswith: str | None = None) -> Path:
    matches = [Path(path) for path in glob.glob(pattern, recursive=True) if Path(path).is_file()]
    if startswith is not None:
        matches = [path for path in matches if path.name.startswith(startswith)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one file for {pattern!r}, found {matches}")
    return matches[0]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_files(root: Path, descriptions: dict) -> None:
    resolved_root = root.resolve()
    for name, expected in descriptions.items():
        path = (root / name).resolve()
        if path.parent != resolved_root:
            raise RuntimeError(f"Manifest path must be a direct child of {root}: {name!r}")
        if not path.is_file():
            raise RuntimeError(f"Missing required input: {path}")
        actual_size = path.stat().st_size
        if actual_size != int(expected["bytes"]):
            raise RuntimeError(f"Size mismatch for {path}: {actual_size} != {expected['bytes']}")
        actual_hash = sha256(path)
        if actual_hash != expected["sha256"]:
            raise RuntimeError(f"SHA-256 mismatch for {path}: {actual_hash}")


def validate_corpus_bundle(root: Path, *, vocab_size: int, eos_token_id: int) -> tuple[dict, dict]:
    upload = load_json(root / "upload-manifest.json")
    if upload.get("schema_version") != 1 or upload.get("sealed") is not True:
        raise RuntimeError("Corpus upload manifest is not a sealed schema-v1 bundle")
    verify_files(root, upload["files"])

    corpus = load_json(root / "manifest.json")
    validation = load_json(root / "validation-report.json")
    if validation.get("ok") is not True:
        raise RuntimeError("Corpus validator did not report success")
    expected_identity = {"vocab_size": vocab_size, "eos_token_id": eos_token_id}
    for key, expected in expected_identity.items():
        if int(corpus.get(key, -1)) != expected or int(validation.get(key, -1)) != expected:
            raise RuntimeError(f"Corpus {key} does not match the base checkpoint")
    if corpus.get("dtype") != "little-endian uint16":
        raise RuntimeError(f"Unexpected corpus dtype: {corpus.get('dtype')}")
    if validation.get("dataset_manifest_sha256") != corpus.get("source_manifest_sha256"):
        raise RuntimeError("Corpus and validator refer to different curated manifests")

    for split in ("train", "validation"):
        specification = corpus["splits"][split]
        report = validation["splits"][split]
        path = root / specification["path"]
        if path.name not in upload["files"]:
            raise RuntimeError(f"Token split is absent from the sealed upload manifest: {path.name}")
        if report["sha256"] != specification["sha256"]:
            raise RuntimeError(f"Validator hash mismatch for {split}")
        if int(report["tokens_including_eos"]) != int(specification["tokens_including_eos"]):
            raise RuntimeError(f"Validator token-count mismatch for {split}")
        if int(report["maximum_token_id"]) >= vocab_size:
            raise RuntimeError(f"Out-of-vocabulary token reported in {split}")

    train_tokens = int(corpus["splits"]["train"]["tokens_including_eos"])
    usable_train_tokens = max(0, (train_tokens - 1) // SEQUENCE_LENGTH) * SEQUENCE_LENGTH
    if usable_train_tokens != TOTAL_TOKENS:
        raise RuntimeError(
            f"Pinned one-pass token count changed: {usable_train_tokens} != {TOTAL_TOKENS}"
        )
    validation_tokens = int(corpus["splits"]["validation"]["tokens_including_eos"])
    minimum_validation = 8 * 8 * PER_DEVICE_BATCH * SEQUENCE_LENGTH + 1
    if validation_tokens < minimum_validation:
        raise RuntimeError(
            f"Validation stream has only {validation_tokens} tokens; need {minimum_validation}"
        )
    return corpus, validation


def main() -> None:
    wheel = exactly_one("/kaggle/input/**/*.whl", startswith="hghost_jax-")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-deps", "--quiet", str(wheel)],
        check=True,
    )

    import flax
    import jax
    import jax.numpy as jnp
    import numpy as np
    import optax
    import safetensors

    from h1jax.checkpoint import load_hf_params
    from h1jax.config import FalconH1Config
    from h1jax.model import count_parameters, falcon_h1_forward
    from h1jax.train import build_parser, run

    hardware = {
        "python": sys.version,
        "jax": jax.__version__,
        "flax": flax.__version__,
        "optax": optax.__version__,
        "safetensors": safetensors.__version__,
        "backend": jax.default_backend(),
        "device_count": jax.device_count(),
        "devices": [str(device) for device in jax.devices()],
    }
    print(json.dumps({"event": "hardware_preflight", **hardware}), flush=True)
    if jax.default_backend() != "tpu" or jax.device_count() != 8:
        raise RuntimeError("Production gate requires exactly one TPU v5e-8 slice")

    preflight_path = exactly_one("/kaggle/input/**/preflight-manifest.json")
    base_root = preflight_path.parent
    preflight = load_json(preflight_path)
    verify_files(base_root, preflight["files"])
    cfg = FalconH1Config.from_json(base_root / "config.json")

    upload_manifest_path = exactly_one("/kaggle/input/**/upload-manifest.json")
    corpus_root = upload_manifest_path.parent
    corpus, corpus_validation = validate_corpus_bundle(
        corpus_root, vocab_size=cfg.vocab_size, eos_token_id=cfg.eos_token_id
    )
    train_path = corpus_root / corpus["splits"]["train"]["path"]
    validation_path = corpus_root / corpus["splits"]["validation"]["path"]

    free_bytes = shutil.disk_usage("/kaggle/working").free
    if free_bytes < 10_000_000_000:
        raise RuntimeError(f"Insufficient checkpoint space: only {free_bytes} bytes free")

    params = load_hf_params(base_root, dtype=jnp.float32)
    if count_parameters(params) != int(preflight["parameter_count"]):
        raise RuntimeError("Checkpoint parameter count does not match the pinned manifest")
    tokens = np.load(base_root / "h1jax-parity-tokens-129.npy", allow_pickle=False).astype(np.int32)
    with np.load(base_root / "h1jax-torch-reference-129.npz", allow_pickle=False) as archive:
        reference = archive["logits"].astype(np.float32)
    parity_forward = jax.jit(
        lambda p, t: falcon_h1_forward(
            p,
            t,
            cfg,
            compute_dtype=jnp.float32,
            gradient_checkpointing=False,
            ssd_precision=jax.lax.Precision.HIGHEST,
        )
    )
    started = time.monotonic()
    actual = np.asarray(parity_forward(params, tokens), dtype=np.float32)
    difference = np.abs(actual - reference)
    # Strict 2e-4 parity was established locally on CPU. TPU matrix units have
    # different floating-point decomposition, so this hardware gate is wider
    # while still being tight enough to catch layout or algebra errors.
    backend_atol = max(float(preflight["float32_parity"]["atol"]), 2e-3)
    backend_rtol = max(float(preflight["float32_parity"]["rtol"]), 2e-3)
    parity = {
        "shape": list(actual.shape),
        "max_absolute_error": float(difference.max()),
        "mean_absolute_error": float(difference.mean()),
        "compile_and_run_seconds": time.monotonic() - started,
        "atol": backend_atol,
        "rtol": backend_rtol,
        "allclose": bool(np.allclose(actual, reference, atol=backend_atol, rtol=backend_rtol)),
    }
    print(json.dumps({"event": "checkpoint_parity", **parity}), flush=True)
    if not parity["allclose"]:
        raise RuntimeError("JAX/Transformers checkpoint parity failed on TPU")
    del actual, difference, params, parity_forward, reference
    jax.clear_caches()

    report = {
        "hardware": hardware,
        "checkpoint_preflight": preflight,
        "corpus_manifest": corpus,
        "corpus_validation": corpus_validation,
        "parity": parity,
        "training_passes": 1,
        "one_pass_tokens": TOTAL_TOKENS,
        "tokens_per_step": 8
        * PER_DEVICE_BATCH
        * ACCUMULATION_STEPS
        * SEQUENCE_LENGTH,
        "steps": math.ceil(
            TOTAL_TOKENS
            / (8 * PER_DEVICE_BATCH * ACCUMULATION_STEPS * SEQUENCE_LENGTH)
        ),
        "batch_alignment_overhead_tokens": math.ceil(
            TOTAL_TOKENS
            / (8 * PER_DEVICE_BATCH * ACCUMULATION_STEPS * SEQUENCE_LENGTH)
        )
        * (8 * PER_DEVICE_BATCH * ACCUMULATION_STEPS * SEQUENCE_LENGTH)
        - TOTAL_TOKENS,
        "free_bytes_before_training": free_bytes,
    }
    Path("/kaggle/working/preflight-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )

    arguments = build_parser().parse_args(
        [
            "--config",
            str(base_root / "config.json"),
            "--checkpoint",
            str(base_root),
            "--tokenizer-dir",
            str(base_root),
            "--train-bin",
            str(train_path),
            "--validation-bin",
            str(validation_path),
            "--output",
            "/kaggle/working/h1-cpt",
            "--sequence-length",
            str(SEQUENCE_LENGTH),
            "--per-device-batch",
            str(PER_DEVICE_BATCH),
            "--accumulation-steps",
            str(ACCUMULATION_STEPS),
            "--total-tokens",
            str(TOTAL_TOKENS),
            "--warmup-tokens",
            "3000000",
            "--learning-rate",
            "0.0001",
            "--weight-decay",
            "0.1",
            "--max-gradient-norm",
            "1.0",
            "--dtype",
            "bfloat16",
            "--no-gradient-checkpointing",
            "--save-tokens",
            ",".join(str(value) for value in SAVE_TOKENS),
            "--eval-every-tokens",
            "10000000",
            "--eval-batches",
            "8",
            "--log-steps",
            "10",
        ]
    )
    run(arguments)
    completion = load_json(Path("/kaggle/working/h1-cpt/training-complete.json"))
    final_checkpoint = Path(
        f"/kaggle/working/h1-cpt/tokens-{TOTAL_TOKENS:012d}/model.safetensors"
    )
    if completion.get("completed") is not True or not final_checkpoint.is_file():
        raise RuntimeError("Trainer returned without a complete final checkpoint")
    if int(completion.get("batch_alignment_overhead_tokens", -1)) != 2_048:
        raise RuntimeError(f"Unexpected CPT batch alignment: {completion}")
    print("H_GHOST_TPU_TRAINING_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
