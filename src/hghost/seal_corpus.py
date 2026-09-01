from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile


SEALED_FILES = ("train.bin", "validation.bin", "manifest.json", "validation-report.json")
TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stage a validated token corpus as a hash-sealed Kaggle dataset bundle."
    )
    parser.add_argument("--tokenized", type=Path, default=Path("artifacts/tokenized"))
    parser.add_argument("--output", type=Path, default=Path("kaggle/corpus_dataset"))
    parser.add_argument(
        "--tokenizer-dir",
        type=Path,
        help="optionally include and verify a corpus-native tokenizer",
    )
    return parser


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _atomic_json(path: Path, value: dict) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _stage_file(source: Path, destination: Path) -> None:
    if destination.exists():
        if destination.stat().st_size == source.stat().st_size and sha256_file(destination) == sha256_file(
            source
        ):
            return
        raise FileExistsError(f"Refusing to replace a different staged file: {destination}")
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    try:
        try:
            os.link(source, temporary)
        except OSError:
            shutil.copy2(source, temporary)
        os.replace(temporary, destination)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def run(args: argparse.Namespace) -> dict:
    tokenized = args.tokenized.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    validation_path = tokenized / "validation-report.json"
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if validation.get("ok") is not True:
        raise ValueError("Refusing to seal a corpus without a successful validation report")

    manifest = json.loads((tokenized / "manifest.json").read_text(encoding="utf-8"))
    if validation.get("dataset_manifest_sha256") != manifest.get("source_manifest_sha256"):
        raise ValueError("Token manifest and validation report refer to different curated datasets")
    for split in ("train", "validation"):
        specification = manifest["splits"][split]
        report = validation["splits"][split]
        if specification["path"] != f"{split}.bin":
            raise ValueError(f"Unexpected {split} filename: {specification['path']}")
        if specification["sha256"] != report["sha256"]:
            raise ValueError(f"Token manifest and validation report disagree for {split}")

    sources = {
        "train.bin": tokenized / "train.bin",
        "validation.bin": tokenized / "validation.bin",
        "manifest.json": tokenized / "manifest.json",
        "validation-report.json": validation_path,
    }
    tokenizer_manifest = None
    tokenizer_dir_arg = getattr(args, "tokenizer_dir", None)
    if tokenizer_dir_arg is not None:
        tokenizer_dir = tokenizer_dir_arg.expanduser().resolve()
        tokenizer_manifest_path = tokenizer_dir / "manifest.json"
        tokenizer_manifest = json.loads(tokenizer_manifest_path.read_text(encoding="utf-8"))
        if tokenizer_manifest.get("dataset_manifest_sha256") != validation.get(
            "dataset_manifest_sha256"
        ):
            raise ValueError("Tokenizer and token stream refer to different curated datasets")
        if int(tokenizer_manifest.get("vocab_size", -1)) != int(manifest["vocab_size"]):
            raise ValueError("Tokenizer and token stream vocabulary sizes differ")
        special_ids = tokenizer_manifest.get("special_token_ids", {})
        if int(special_ids.get("eos_token", -1)) != int(manifest["eos_token_id"]):
            raise ValueError("Tokenizer and token stream EOS IDs differ")
        for name in TOKENIZER_FILES:
            source = tokenizer_dir / name
            expected = tokenizer_manifest["artifacts"][name]
            if source.stat().st_size != int(expected["bytes"]):
                raise ValueError(f"Tokenizer artifact size mismatch: {source}")
            if sha256_file(source) != expected["sha256"]:
                raise ValueError(f"Tokenizer artifact hash mismatch: {source}")
            sources[name] = source
        sources["tokenizer-manifest.json"] = tokenizer_manifest_path

    sealed_names = tuple(sources)
    for name in sealed_names:
        source = sources[name]
        if not source.is_file():
            raise FileNotFoundError(source)
        _stage_file(source, output / name)

    files = {
        name: {
            "bytes": (output / name).stat().st_size,
            "sha256": sha256_file(output / name),
        }
        for name in sealed_names
    }
    sealed = {
        "schema_version": 1,
        "sealed": True,
        "files": files,
        "dataset_manifest_sha256": validation["dataset_manifest_sha256"],
        "selected_documents": validation["selected_documents"],
        "train_tokens_including_eos": validation["splits"]["train"][
            "tokens_including_eos"
        ],
        "validation_tokens_including_eos": validation["splits"]["validation"][
            "tokens_including_eos"
        ],
    }
    if tokenizer_manifest is not None:
        sealed["tokenizer_manifest_sha256"] = files["tokenizer-manifest.json"]["sha256"]
    _atomic_json(output / "upload-manifest.json", sealed)
    return sealed


def main() -> None:
    print(json.dumps(run(build_parser().parse_args()), indent=2))


if __name__ == "__main__":
    main()
