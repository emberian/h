"""One-shot full-size 91M random-init TPU pretraining. Do not push early."""

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


os.environ.setdefault("JAX_COMPILATION_CACHE_DIR", "/kaggle/working/jax-cache")

EXPECTED_PARAMETERS = 91_131_072
ONE_PASS_TOKENS = 374_405_120
TRAIN_PASSES = 2
TOTAL_TOKENS = ONE_PASS_TOKENS * TRAIN_PASSES
SEQUENCE_LENGTH = 512
PER_DEVICE_BATCH = 4
ACCUMULATION_STEPS = 1
LEARNING_RATE = 1.6e-4
SAVE_TOKENS = (
    10_000_000,
    30_000_000,
    100_000_000,
    300_000_000,
    ONE_PASS_TOKENS,
    600_000_000,
    TOTAL_TOKENS,
)


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
        if path.stat().st_size != int(expected["bytes"]):
            raise RuntimeError(f"Size mismatch for {path}")
        if sha256(path) != expected["sha256"]:
            raise RuntimeError(f"SHA-256 mismatch for {path}")


def validate_corpus_bundle(
    root: Path, *, vocab_size: int, eos_token_id: int
) -> tuple[dict, dict]:
    upload = load_json(root / "upload-manifest.json")
    if upload.get("schema_version") != 1 or upload.get("sealed") is not True:
        raise RuntimeError("Corpus upload manifest is not a sealed schema-v1 bundle")
    verify_files(root, upload["files"])
    corpus = load_json(root / "manifest.json")
    validation = load_json(root / "validation-report.json")
    if validation.get("ok") is not True:
        raise RuntimeError("Corpus validator did not report success")
    for key, expected in (("vocab_size", vocab_size), ("eos_token_id", eos_token_id)):
        if int(corpus.get(key, -1)) != expected or int(validation.get(key, -1)) != expected:
            raise RuntimeError(f"Corpus {key} does not match the 91M configuration")
    if corpus.get("dtype") != "little-endian uint16":
        raise RuntimeError(f"Unexpected corpus dtype: {corpus.get('dtype')}")
    if validation.get("dataset_manifest_sha256") != corpus.get("source_manifest_sha256"):
        raise RuntimeError("Corpus and validator refer to different curated manifests")
    for split in ("train", "validation"):
        specification = corpus["splits"][split]
        report = validation["splits"][split]
        path = root / specification["path"]
        if path.name not in upload["files"]:
            raise RuntimeError(f"Token split is absent from sealed manifest: {path.name}")
        if report["sha256"] != specification["sha256"]:
            raise RuntimeError(f"Validator hash mismatch for {split}")
        if int(report["tokens_including_eos"]) != int(
            specification["tokens_including_eos"]
        ):
            raise RuntimeError(f"Validator token-count mismatch for {split}")
        if int(report["maximum_token_id"]) >= vocab_size:
            raise RuntimeError(f"Out-of-vocabulary token reported in {split}")
        if int(report.get("eos_tokens", -1)) != int(report["documents"]):
            raise RuntimeError(f"EOS/document mismatch reported in {split}")
    train_tokens = int(corpus["splits"]["train"]["tokens_including_eos"])
    usable_train_tokens = max(0, (train_tokens - 1) // SEQUENCE_LENGTH) * SEQUENCE_LENGTH
    if usable_train_tokens != ONE_PASS_TOKENS:
        raise RuntimeError(
            f"Pinned one-pass token count changed: {usable_train_tokens} != {ONE_PASS_TOKENS}"
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
    import optax

    from h1jax.config import FalconH1Config
    from h1jax.model import parameter_count_for_config
    from h1jax.train import build_parser, run

    hardware = {
        "python": sys.version,
        "jax": jax.__version__,
        "flax": flax.__version__,
        "optax": optax.__version__,
        "backend": jax.default_backend(),
        "device_count": jax.device_count(),
        "devices": [str(device) for device in jax.devices()],
    }
    print(json.dumps({"event": "hardware_preflight", **hardware}), flush=True)
    if jax.default_backend() != "tpu" or jax.device_count() != 8:
        raise RuntimeError("Production gate requires exactly one TPU v5e-8 slice")

    base_preflight_path = exactly_one("/kaggle/input/**/preflight-manifest.json")
    base_root = base_preflight_path.parent
    base_preflight = load_json(base_preflight_path)
    verify_files(base_root, base_preflight["files"])
    cfg = FalconH1Config.from_json(base_root / "config.json")
    parameter_count = parameter_count_for_config(cfg)
    if parameter_count != EXPECTED_PARAMETERS:
        raise RuntimeError(
            f"91M configuration changed: {parameter_count} != {EXPECTED_PARAMETERS}"
        )

    upload_manifest_path = exactly_one("/kaggle/input/**/upload-manifest.json")
    corpus_root = upload_manifest_path.parent
    corpus, validation = validate_corpus_bundle(
        corpus_root, vocab_size=cfg.vocab_size, eos_token_id=cfg.eos_token_id
    )
    free_bytes = shutil.disk_usage("/kaggle/working").free
    if free_bytes < 10_000_000_000:
        raise RuntimeError(f"Insufficient checkpoint space: only {free_bytes} bytes free")

    tokens_per_step = 8 * PER_DEVICE_BATCH * ACCUMULATION_STEPS * SEQUENCE_LENGTH
    preflight = {
        "schema_version": 1,
        "hardware": hardware,
        "base_preflight": base_preflight,
        "corpus_manifest": corpus,
        "corpus_validation": validation,
        "parameters": parameter_count,
        "parallelism": "8-way synchronous data parallel (jax.pmap + lax.pmean)",
        "per_device_batch": PER_DEVICE_BATCH,
        "training_passes": TRAIN_PASSES,
        "one_pass_tokens": ONE_PASS_TOKENS,
        "tokens_per_step": tokens_per_step,
        "steps": math.ceil(TOTAL_TOKENS / tokens_per_step),
        "batch_aligned_tokens": math.ceil(TOTAL_TOKENS / tokens_per_step)
        * tokens_per_step,
        "batch_alignment_overhead_tokens": math.ceil(TOTAL_TOKENS / tokens_per_step)
        * tokens_per_step
        - TOTAL_TOKENS,
        "free_bytes_before_training": free_bytes,
    }
    Path("/kaggle/working/fresh-91m-preflight-report.json").write_text(
        json.dumps(preflight, indent=2) + "\n", encoding="utf-8"
    )

    output = Path("/kaggle/working/h1-fresh-91m")
    if output.exists():
        raise RuntimeError(f"Refusing pre-existing output directory: {output}")
    arguments = build_parser().parse_args(
        [
            "--config",
            str(base_root / "config.json"),
            "--random-init",
            "--tokenizer-dir",
            str(base_root),
            "--train-bin",
            str(corpus_root / corpus["splits"]["train"]["path"]),
            "--validation-bin",
            str(corpus_root / corpus["splits"]["validation"]["path"]),
            "--output",
            str(output),
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
            str(LEARNING_RATE),
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
    completion = load_json(output / "training-complete.json")
    if completion.get("completed") is not True or int(completion.get("tokens", -1)) != TOTAL_TOKENS:
        raise RuntimeError("91M trainer returned without a complete final marker")
    if int(completion.get("batch_alignment_overhead_tokens", -1)) != 4_096:
        raise RuntimeError(f"Unexpected fresh-pretrain batch alignment: {completion}")
    missing = [
        threshold
        for threshold in SAVE_TOKENS
        if not (output / f"tokens-{threshold:012d}" / "model.safetensors").is_file()
    ]
    if missing:
        raise RuntimeError(f"91M run is missing requested checkpoints: {missing}")
    Path("/kaggle/working/fresh-91m-training-complete.json").write_text(
        json.dumps(
            {
                "completed": True,
                "parameters": parameter_count,
                "training": completion,
                "checkpoint_thresholds": list(SAVE_TOKENS),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("H_GHOST_TPU_FRESH_91M_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
