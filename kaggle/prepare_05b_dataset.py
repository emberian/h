"""Build the public Kaggle bundle for the pinned Falcon-H1 0.5B checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil


MODEL = "tiiuae/Falcon-H1-0.5B-Base"
REVISION = "59fb76e8c5d3fc7441b062be638e1ba0afd5c687"
MODEL_BYTES = 1_042_886_408
MODEL_SHA256 = "865a1e864b3fe6495ec37256e1fdec8cd1d254b607eab29141e7263791172ce6"
TOKENIZER_SHA256 = "605c664925653e3fbf2f35ea063847db441ba5b7a6af04378880409c3ab311fc"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def stage(source: Path, destination: Path) -> None:
    if destination.exists():
        if source.stat().st_size == destination.stat().st_size and sha256_file(
            source
        ) == sha256_file(destination):
            return
        raise FileExistsError(f"Refusing to replace a different file: {destination}")
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    model = args.model.expanduser().resolve()
    fixtures = args.fixtures.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    weight = model / "model.safetensors"
    tokenizer = model / "tokenizer.json"
    if weight.stat().st_size != MODEL_BYTES or sha256_file(weight) != MODEL_SHA256:
        raise ValueError("The 0.5B checkpoint does not match the pinned revision")
    if sha256_file(tokenizer) != TOKENIZER_SHA256:
        raise ValueError("The 0.5B tokenizer does not match the pinned revision")

    sources = {
        name: model / name
        for name in (
            "README.md",
            "config.json",
            "generation_config.json",
            "model.safetensors",
            "special_tokens_map.json",
            "tokenizer.json",
            "tokenizer_config.json",
        )
    }
    sources.update(
        {
            "h1jax-parity-tokens.npy": fixtures / "tokens.npy",
            "h1jax-torch-reference.npz": fixtures / "reference-logits.npz",
            "FALCON_LICENSE.html": Path(
                "kaggle/base_model_dataset_public/FALCON_LICENSE.html"
            ).resolve(),
            "FALCON_ACCEPTABLE_USE_POLICY.html": Path(
                "kaggle/base_model_dataset_public/FALCON_ACCEPTABLE_USE_POLICY.html"
            ).resolve(),
        }
    )
    for name, source in sources.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        stage(source, output / name)

    metadata = {
        "title": "Falcon-H1 0.5B Base for H Ghost",
        "id": "emberian64/hghost-falcon-h1-0-5b-base-public",
        "subtitle": "Pinned unmodified TII checkpoint with JAX parity fixtures",
        "description": (
            "Public, unmodified tiiuae/Falcon-H1-0.5B-Base checkpoint pinned at "
            f"revision {REVISION}, plus deterministic JAX parity fixtures. Use and "
            "redistribution are governed by the included Falcon-LLM License and "
            "Acceptable Use Policy."
        ),
        "licenses": [{"name": "other"}],
    }
    write_json(output / "dataset-metadata.json", metadata)
    manifest = {
        "schema_version": 1,
        "model": MODEL,
        "revision": REVISION,
        "parameter_count": 521_411_104,
        "files": {
            name: {
                "bytes": (output / name).stat().st_size,
                "sha256": sha256_file(output / name),
            }
            for name in sources
        },
        "float32_parity": {
            "shape": [1, 15, 32784],
            "max_absolute_error": 0.0000667572021484375,
            "mean_absolute_error": 0.00000756471172280726,
            "atol": 0.002,
            "rtol": 0.002,
        },
        "tokenizer_compatible_with_tiny": True,
    }
    write_json(output / "preflight-manifest.json", manifest)
    (output / "REDISTRIBUTION_NOTICE.md").write_text(
        "# Falcon-H1 0.5B Base redistribution notice\n\n"
        f"This dataset republishes the unmodified public checkpoint and tokenizer from `{MODEL}`, "
        f"pinned at Hugging Face revision `{REVISION}`.\n\n"
        "The model is licensed by the Technology Innovation Institute under the Falcon-LLM "
        "License. Use and redistribution are subject to that license and its Acceptable Use "
        "Policy. Exact copies of those terms are included in this dataset; current upstream "
        "terms control. The `h1jax-*` files are deterministic numerical parity fixtures.\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
