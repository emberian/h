from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


def _load_preflight_module():
    path = Path(__file__).parents[1] / "kaggle" / "tpu_train" / "run.py"
    specification = importlib.util.spec_from_file_location("hghost_tpu_run", path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _file_spec(path: Path) -> dict:
    return {
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def test_tpu_preflight_accepts_only_a_sealed_validated_bundle(tmp_path: Path) -> None:
    preflight = _load_preflight_module()
    preflight.TOTAL_TOKENS = 36
    preflight.SEQUENCE_LENGTH = 4
    for name, size in (("train.bin", 40), ("validation.bin", 1200)):
        (tmp_path / name).write_bytes(b"\x00\x00" * size)
    source_hash = "a" * 64
    corpus = {
        "dtype": "little-endian uint16",
        "vocab_size": 128,
        "eos_token_id": 11,
        "source_manifest_sha256": source_hash,
        "splits": {
            "train": {
                "path": "train.bin",
                "tokens_including_eos": 40,
                **_file_spec(tmp_path / "train.bin"),
            },
            "validation": {
                "path": "validation.bin",
                "tokens_including_eos": 1200,
                **_file_spec(tmp_path / "validation.bin"),
            },
        },
    }
    validation = {
        "ok": True,
        "vocab_size": 128,
        "eos_token_id": 11,
        "dataset_manifest_sha256": source_hash,
        "splits": {
            split: {
                "sha256": corpus["splits"][split]["sha256"],
                "tokens_including_eos": corpus["splits"][split]["tokens_including_eos"],
                "maximum_token_id": 0,
            }
            for split in ("train", "validation")
        },
    }
    (tmp_path / "manifest.json").write_text(json.dumps(corpus), encoding="utf-8")
    (tmp_path / "validation-report.json").write_text(
        json.dumps(validation), encoding="utf-8"
    )
    sealed_files = {
        name: _file_spec(tmp_path / name)
        for name in ("train.bin", "validation.bin", "manifest.json", "validation-report.json")
    }
    (tmp_path / "upload-manifest.json").write_text(
        json.dumps({"schema_version": 1, "sealed": True, "files": sealed_files}),
        encoding="utf-8",
    )

    actual, actual_validation = preflight.validate_corpus_bundle(
        tmp_path, vocab_size=128, eos_token_id=11
    )
    assert actual == corpus
    assert actual_validation == validation

    with (tmp_path / "train.bin").open("ab") as stream:
        stream.write(b"tampered")
    with pytest.raises(RuntimeError, match="Size mismatch"):
        preflight.validate_corpus_bundle(tmp_path, vocab_size=128, eos_token_id=11)
