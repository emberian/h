#!/usr/bin/env python3
"""Create a tiny deterministic sealed corpus for hbox trainer verification."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def spec(path: Path) -> dict:
    return {
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(20260901)
    for split in ("train", "validation"):
        rng.integers(0, 32_768, size=4_097, dtype=np.uint16).tofile(output / f"{split}.bin")
    source_hash = "0" * 64
    manifest = {
        "schema_version": 1,
        "dtype": "little-endian uint16",
        "vocab_size": 32_768,
        "eos_token_id": 11,
        "source_manifest_sha256": source_hash,
        "splits": {
            split: {
                "path": f"{split}.bin",
                "tokens_including_eos": 4_097,
                **spec(output / f"{split}.bin"),
            }
            for split in ("train", "validation")
        },
    }
    validation = {
        "ok": True,
        "vocab_size": 32_768,
        "eos_token_id": 11,
        "dataset_manifest_sha256": source_hash,
        "splits": {
            split: {
                "tokens_including_eos": 4_097,
                "maximum_token_id": 32_767,
                "sha256": manifest["splits"][split]["sha256"],
            }
            for split in ("train", "validation")
        },
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "validation-report.json").write_text(json.dumps(validation, indent=2) + "\n")
    files = {
        name: spec(output / name)
        for name in ("train.bin", "validation.bin", "manifest.json", "validation-report.json")
    }
    (output / "upload-manifest.json").write_text(
        json.dumps({"schema_version": 1, "sealed": True, "files": files}, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
