"""Build the public Kaggle bundle for the pinned Falcon-H1 1.5B-Deep checkpoint.

Same layout as `prepare_05b_dataset.py` (which built `artifacts/kaggle/base_model_05b`): the
unmodified Hub files at one pinned revision, the Falcon license and acceptable-use policy, the h1jax
parity fixtures, `preflight-manifest.json` (the TPU kernels verify `model.safetensors` by sha256 and
the parameter count from it) and a redistribution notice. The parity numbers are read from the JSON
that `h1jax.parity` printed, rather than retyped.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil


MODEL = "tiiuae/Falcon-H1-1.5B-Deep-Base"
REVISION = "e975d35c1283500d7cd844c0cd9e2c58e30a8db8"
MODEL_BYTES = 3_109_870_496
MODEL_SHA256 = "d93c5faefd36b79860f82dec1a981f746fe71e79d29ebba1cc4643b1fd6cf4a8"
TOKENIZER_SHA256 = "eb7825ecac026cc37e37c03d7e8d06d1f85c7ab8bdefabe81fc1b40f0ed7929a"
PARAMETER_COUNT = 1_554_872_208
KAGGLE_ID = "emberian64/hghost-falcon-h1-1-5b-deep-base-public"


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
    parser.add_argument(
        "--parity",
        type=Path,
        required=True,
        help="JSON printed by `python -m h1jax.parity` for these fixtures",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    model = args.model.expanduser().resolve()
    fixtures = args.fixtures.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    weight = model / "model.safetensors"
    tokenizer = model / "tokenizer.json"
    if weight.stat().st_size != MODEL_BYTES or sha256_file(weight) != MODEL_SHA256:
        raise ValueError("The 1.5B-Deep checkpoint does not match the pinned revision")
    if sha256_file(tokenizer) != TOKENIZER_SHA256:
        raise ValueError("The 1.5B-Deep tokenizer does not match the pinned revision")
    config = json.loads((model / "config.json").read_text(encoding="utf-8"))
    if config["num_hidden_layers"] != 66 or config["vocab_size"] != 65_536:
        raise ValueError("config.json is not the 1.5B-Deep configuration")

    parity = json.loads(args.parity.read_text(encoding="utf-8"))
    if not parity.get("allclose"):
        raise ValueError("The parity report does not say allclose")
    if parity["shape"][-1] != config["vocab_size"]:
        raise ValueError("The parity report is for a different vocabulary")

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
        "title": "Falcon-H1 1-5B Deep Base for H Ghost",
        "id": KAGGLE_ID,
        "subtitle": "Pinned unmodified TII checkpoint with JAX parity fixtures",
        "description": (
            "Public, unmodified tiiuae/Falcon-H1-1.5B-Deep-Base checkpoint pinned at "
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
        "parameter_count": PARAMETER_COUNT,
        "files": {
            name: {
                "bytes": (output / name).stat().st_size,
                "sha256": sha256_file(output / name),
            }
            for name in sources
        },
        "float32_parity": {
            "shape": parity["shape"],
            "max_absolute_error": parity["max_absolute_error"],
            "mean_absolute_error": parity["mean_absolute_error"],
            "atol": parity["atol"],
            "rtol": parity["rtol"],
        },
        "tokenizer_compatible_with_tiny": False,
        "tokenizer_note": (
            "65,536-token vocabulary; not the 32,768-token Falcon-H1-Tiny/0.5B tokenizer, so the "
            "v1 token streams cannot be reused. EOS id 11 and pad id 0 are the same."
        ),
    }
    write_json(output / "preflight-manifest.json", manifest)
    (output / "REDISTRIBUTION_NOTICE.md").write_text(
        "# Falcon-H1 1.5B-Deep Base redistribution notice\n\n"
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
