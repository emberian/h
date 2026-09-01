"""One-shot sequential 10M/20M corpus-native TPU pretraining job. Do not push early."""

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
os.environ.setdefault("JAX_DEFAULT_MATMUL_PRECISION", "highest")

VOCAB_SIZE = 8192
EOS_TOKEN_ID = 2
TOTAL_TOKENS = 300_000_000
SEQUENCE_LENGTH = 512
PER_DEVICE_BATCH = 16
ACCUMULATION_STEPS = 1
LEARNING_RATE = 3.0e-4
SAVE_TOKENS = (10_000_000, 30_000_000, 100_000_000, TOTAL_TOKENS)
EXPECTED_PARAMETERS = {"born-10m": 9_856_488, "born-20m": 19_511_990}
TOKENIZER_FILES = (
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "tokenizer-manifest.json",
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


def validate_corpus_bundle(root: Path) -> tuple[dict, dict, dict]:
    upload = load_json(root / "upload-manifest.json")
    if upload.get("schema_version") != 1 or upload.get("sealed") is not True:
        raise RuntimeError("Corpus upload manifest is not a sealed schema-v1 bundle")
    verify_files(root, upload["files"])
    for name in TOKENIZER_FILES:
        if name not in upload["files"]:
            raise RuntimeError(f"Sealed bundle omits tokenizer artifact {name}")

    corpus = load_json(root / "manifest.json")
    validation = load_json(root / "validation-report.json")
    tokenizer_manifest = load_json(root / "tokenizer-manifest.json")
    if validation.get("ok") is not True:
        raise RuntimeError("Corpus validator did not report success")
    if int(corpus.get("vocab_size", -1)) != VOCAB_SIZE:
        raise RuntimeError("Corpus vocabulary does not match the fresh-model configuration")
    if int(corpus.get("eos_token_id", -1)) != EOS_TOKEN_ID:
        raise RuntimeError("Corpus EOS ID does not match the fresh-model configuration")
    if corpus.get("dtype") != "little-endian uint16":
        raise RuntimeError(f"Unexpected corpus dtype: {corpus.get('dtype')}")
    dataset_hash = corpus.get("source_manifest_sha256")
    if validation.get("dataset_manifest_sha256") != dataset_hash:
        raise RuntimeError("Corpus and validator refer to different curated manifests")
    if tokenizer_manifest.get("dataset_manifest_sha256") != dataset_hash:
        raise RuntimeError("Tokenizer and token stream refer to different curated manifests")
    if int(tokenizer_manifest.get("vocab_size", -1)) != VOCAB_SIZE:
        raise RuntimeError("Tokenizer manifest has the wrong vocabulary size")
    expected_special_ids = {"pad_token": 0, "bos_token": 1, "eos_token": 2}
    if tokenizer_manifest.get("special_token_ids") != expected_special_ids:
        raise RuntimeError("Tokenizer special-token IDs do not match the model contract")

    tokenizer_json = load_json(root / "tokenizer.json")
    vocabulary = tokenizer_json.get("model", {}).get("vocab", {})
    if len(vocabulary) != VOCAB_SIZE:
        raise RuntimeError("tokenizer.json has the wrong vocabulary size")
    for token, expected_id in (
        ("<|pad|>", 0),
        ("<|begin_of_text|>", 1),
        ("<|end_of_text|>", 2),
    ):
        if int(vocabulary.get(token, -1)) != expected_id:
            raise RuntimeError(f"tokenizer.json assigns the wrong ID to {token}")

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
        if int(report["maximum_token_id"]) >= VOCAB_SIZE:
            raise RuntimeError(f"Out-of-vocabulary token reported in {split}")
        if int(report.get("eos_tokens", -1)) != int(report["documents"]):
            raise RuntimeError(f"EOS/document mismatch reported in {split}")

    train_tokens = int(corpus["splits"]["train"]["tokens_including_eos"])
    usable_train_tokens = max(0, (train_tokens - 1) // SEQUENCE_LENGTH) * SEQUENCE_LENGTH
    if usable_train_tokens < TOTAL_TOKENS:
        raise RuntimeError(
            f"Training stream has only {usable_train_tokens} usable tokens; need {TOTAL_TOKENS}"
        )
    validation_tokens = int(corpus["splits"]["validation"]["tokens_including_eos"])
    minimum_validation = 8 * 8 * PER_DEVICE_BATCH * SEQUENCE_LENGTH + 1
    if validation_tokens < minimum_validation:
        raise RuntimeError(
            f"Validation stream has only {validation_tokens} tokens; need {minimum_validation}"
        )
    return corpus, validation, tokenizer_manifest


def train_one(name: str, cfg, corpus_root: Path, corpus: dict, build_parser, run) -> dict:
    config_path = Path(f"/kaggle/working/{name}-config.json")
    cfg.to_json(config_path)
    output = Path(f"/kaggle/working/{name}")
    if output.exists():
        raise RuntimeError(f"Refusing pre-existing output directory: {output}")
    arguments = build_parser().parse_args(
        [
            "--config",
            str(config_path),
            "--random-init",
            "--tokenizer-dir",
            str(corpus_root),
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
    print(json.dumps({"event": "model_start", "name": name}), flush=True)
    run(arguments)
    completion = load_json(output / "training-complete.json")
    if completion.get("completed") is not True or int(completion.get("tokens", -1)) != TOTAL_TOKENS:
        raise RuntimeError(f"{name} trainer returned without a completion marker")
    missing = [
        threshold
        for threshold in SAVE_TOKENS
        if not (output / f"tokens-{threshold:012d}" / "model.safetensors").is_file()
    ]
    if missing:
        raise RuntimeError(f"{name} is missing requested checkpoints: {missing}")
    result = {
        "name": name,
        "parameters": EXPECTED_PARAMETERS[name],
        "completion": completion,
        "checkpoint_thresholds": list(SAVE_TOKENS),
    }
    print(json.dumps({"event": "model_complete", **result}), flush=True)
    return result


def main() -> None:
    wheel = exactly_one("/kaggle/input/**/*.whl", startswith="hghost_jax-")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-deps", "--quiet", str(wheel)],
        check=True,
    )

    import flax
    import jax
    import optax

    from h1jax.config import born_10m_config, born_20m_config
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

    upload_manifest_path = exactly_one("/kaggle/input/**/upload-manifest.json")
    corpus_root = upload_manifest_path.parent
    corpus, validation, tokenizer_manifest = validate_corpus_bundle(corpus_root)
    configs = {
        "born-10m": born_10m_config(VOCAB_SIZE),
        "born-20m": born_20m_config(VOCAB_SIZE),
    }
    actual_parameters = {
        name: parameter_count_for_config(cfg) for name, cfg in configs.items()
    }
    if actual_parameters != EXPECTED_PARAMETERS:
        raise RuntimeError(
            f"Fresh-model parameter counts changed: {actual_parameters} != {EXPECTED_PARAMETERS}"
        )
    tokens_per_step = 8 * PER_DEVICE_BATCH * ACCUMULATION_STEPS * SEQUENCE_LENGTH
    preflight = {
        "schema_version": 1,
        "hardware": hardware,
        "corpus_manifest": corpus,
        "corpus_validation": validation,
        "tokenizer_manifest": tokenizer_manifest,
        "dataset_files": load_json(upload_manifest_path)["files"],
        "models": actual_parameters,
        "tokens_per_step": tokens_per_step,
        "steps_per_model": math.ceil(TOTAL_TOKENS / tokens_per_step),
        "total_exposure_tokens": 2 * TOTAL_TOKENS,
        "free_bytes_before_training": shutil.disk_usage("/kaggle/working").free,
    }
    if int(preflight["free_bytes_before_training"]) < 10_000_000_000:
        raise RuntimeError("Kaggle working volume has less than 10 GB free")
    Path("/kaggle/working/fresh-preflight-report.json").write_text(
        json.dumps(preflight, indent=2) + "\n", encoding="utf-8"
    )

    results = [
        train_one(name, cfg, corpus_root, corpus, build_parser, run)
        for name, cfg in configs.items()
    ]
    Path("/kaggle/working/fresh-training-complete.json").write_text(
        json.dumps({"completed": True, "models": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    print("H_GHOST_TPU_FRESH_TRAINING_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
