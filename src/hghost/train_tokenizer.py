from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Iterator


SPECIAL_TOKENS = (
    ("pad_token", "<|pad|>", 0),
    ("bos_token", "<|begin_of_text|>", 1),
    ("eos_token", "<|end_of_text|>", 2),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train a corpus-native byte-level BPE on only the curated train split."
    )
    parser.add_argument("--dataset", type=Path, default=Path("artifacts/dataset"))
    parser.add_argument(
        "--base-tokenizer",
        type=Path,
        default=Path("kaggle/base_model_dataset/tokenizer.json"),
        help="Tokenizer JSON whose pre-tokenizer and decoder should be retained.",
    )
    parser.add_argument("--output", type=Path, default=Path("artifacts/tokenizer-8k"))
    parser.add_argument("--vocab-size", type=int, default=8192)
    parser.add_argument("--min-frequency", type=int, default=2)
    parser.add_argument("--show-progress", action=argparse.BooleanOptionalAction, default=True)
    return parser


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _train_shards(dataset: Path, manifest: dict) -> list[Path]:
    paths: list[Path] = []
    for specification in manifest["splits"]["train"]["shards"]:
        path = dataset / specification["path"]
        if path.stat().st_size != int(specification["compressed_bytes"]):
            raise ValueError(f"Compressed size mismatch: {path}")
        if sha256_file(path) != specification["sha256"]:
            raise ValueError(f"Shard hash mismatch: {path}")
        paths.append(path)
    return paths


def iter_texts(paths: list[Path]) -> Iterator[str]:
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    yield str(json.loads(line)["text"])


def _tokenizer_config() -> dict:
    added_tokens_decoder = {
        str(token_id): {
            "content": token,
            "lstrip": False,
            "normalized": False,
            "rstrip": False,
            "single_word": False,
            "special": True,
        }
        for _, token, token_id in SPECIAL_TOKENS
    }
    return {
        "add_bos_token": False,
        "add_eos_token": False,
        "added_tokens_decoder": added_tokens_decoder,
        "bos_token": SPECIAL_TOKENS[1][1],
        "clean_up_tokenization_spaces": False,
        "eos_token": SPECIAL_TOKENS[2][1],
        "model_max_length": 262144,
        "pad_token": SPECIAL_TOKENS[0][1],
        "tokenizer_class": "PreTrainedTokenizerFast",
    }


def run(args: argparse.Namespace) -> dict:
    try:
        from tokenizers import AddedToken, Tokenizer
        from tokenizers.models import BPE
        from tokenizers.pre_tokenizers import ByteLevel
        from tokenizers.trainers import BpeTrainer
    except ImportError as exc:
        raise RuntimeError("tokenizers is not installed") from exc

    dataset = args.dataset.expanduser().resolve()
    base_tokenizer_path = args.base_tokenizer.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if args.vocab_size < 259 or args.vocab_size > 65_536:
        raise ValueError("--vocab-size must be between 259 and 65,536")
    if args.min_frequency < 1:
        raise ValueError("--min-frequency must be positive")
    if output.exists():
        raise FileExistsError(f"Refusing to replace existing tokenizer directory: {output}")

    dataset_manifest_path = dataset / "manifest.json"
    dataset_manifest = json.loads(dataset_manifest_path.read_text(encoding="utf-8"))
    paths = _train_shards(dataset, dataset_manifest)
    expected_documents = int(dataset_manifest["splits"]["train"]["documents"])

    base = Tokenizer.from_file(str(base_tokenizer_path))
    if base.pre_tokenizer is None or base.decoder is None:
        raise ValueError("Base tokenizer must provide both a pre-tokenizer and decoder")
    tokenizer = Tokenizer(BPE(unk_token=None, byte_fallback=False))
    tokenizer.normalizer = base.normalizer
    tokenizer.pre_tokenizer = base.pre_tokenizer
    tokenizer.decoder = base.decoder
    trainer = BpeTrainer(
        vocab_size=args.vocab_size,
        min_frequency=args.min_frequency,
        show_progress=args.show_progress,
        special_tokens=[
            AddedToken(token, normalized=False, special=True)
            for _, token, _ in SPECIAL_TOKENS
        ],
        initial_alphabet=ByteLevel.alphabet(),
        max_token_length=128,
    )
    tokenizer.train_from_iterator(iter_texts(paths), trainer=trainer, length=expected_documents)

    actual_vocab_size = tokenizer.get_vocab_size(with_added_tokens=True)
    if actual_vocab_size != args.vocab_size:
        raise ValueError(
            f"Trainer produced {actual_vocab_size} tokens instead of requested {args.vocab_size}"
        )
    for _, token, expected_id in SPECIAL_TOKENS:
        actual_id = tokenizer.token_to_id(token)
        if actual_id != expected_id:
            raise ValueError(f"Special token {token!r} has ID {actual_id}, expected {expected_id}")

    samples: list[str] = []
    for text in iter_texts(paths):
        samples.append(text[:4096])
        if len(samples) == 8:
            break
    for sample in samples:
        encoded = tokenizer.encode(sample, add_special_tokens=False)
        decoded = tokenizer.decode(encoded.ids, skip_special_tokens=False)
        if decoded != sample:
            raise ValueError("Tokenizer failed a UTF-8 round-trip check")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
    try:
        tokenizer_path = temporary / "tokenizer.json"
        tokenizer.save(str(tokenizer_path), pretty=True)
        _write_json(temporary / "tokenizer_config.json", _tokenizer_config())
        _write_json(
            temporary / "special_tokens_map.json",
            {name: token for name, token, _ in SPECIAL_TOKENS},
        )
        artifacts = {
            name: {
                "bytes": (temporary / name).stat().st_size,
                "sha256": sha256_file(temporary / name),
            }
            for name in ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json")
        }
        result = {
            "schema_version": 1,
            "algorithm": "byte-level BPE",
            "vocab_size": actual_vocab_size,
            "min_frequency": args.min_frequency,
            "training_split": "train",
            "training_documents": expected_documents,
            "training_source_tokens_falcon": int(
                dataset_manifest["splits"]["train"]["tokens"]
            ),
            "dataset_manifest_sha256": sha256_file(dataset_manifest_path),
            "base_tokenizer_sha256": sha256_file(base_tokenizer_path),
            "special_token_ids": {
                name: token_id for name, _, token_id in SPECIAL_TOKENS
            },
            "artifacts": artifacts,
        }
        _write_json(temporary / "manifest.json", result)
        os.replace(temporary, output)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return result


def main() -> None:
    print(json.dumps(run(build_parser().parse_args()), indent=2))


if __name__ == "__main__":
    main()
