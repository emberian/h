from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
import tempfile
from array import array
from pathlib import Path
from typing import Iterable, Iterator

from .census import DEFAULT_MODEL


BUFFER_TOKENS = 1_000_000


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Tokenize curated JSONL shards into deterministic little-endian uint16 streams."
    )
    parser.add_argument("--dataset", type=Path, default=Path("artifacts/dataset"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/tokenized"))
    parser.add_argument("--tokenizer", default=DEFAULT_MODEL)
    parser.add_argument("--eos-token-id", type=int, default=11)
    return parser


def iter_records(paths: Iterable[Path]) -> Iterator[dict]:
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    yield json.loads(line)


def _write_little_endian(stream, values: list[int]) -> None:
    packed = array("H", values)
    if sys.byteorder != "little":
        packed.byteswap()
    packed.tofile(stream)


def write_split(paths: list[Path], output: Path, tokenizer, eos_token_id: int) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    tokens = documents = mismatched_counts = 0
    digest = hashlib.sha256()
    buffer: list[int] = []
    try:
        with os.fdopen(descriptor, "wb") as stream:
            for record in iter_records(paths):
                ids = tokenizer.encode(record["text"], add_special_tokens=False).ids
                if len(ids) != int(record["tokens"]):
                    mismatched_counts += 1
                ids.append(eos_token_id)
                if any(token < 0 or token > 65_535 for token in ids):
                    raise ValueError("token ID does not fit uint16")
                buffer.extend(ids)
                tokens += len(ids)
                documents += 1
                if len(buffer) >= BUFFER_TOKENS:
                    packed = array("H", buffer)
                    if sys.byteorder != "little":
                        packed.byteswap()
                    payload = packed.tobytes()
                    stream.write(payload)
                    digest.update(payload)
                    buffer.clear()
            if buffer:
                packed = array("H", buffer)
                if sys.byteorder != "little":
                    packed.byteswap()
                payload = packed.tobytes()
                stream.write(payload)
                digest.update(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
    return {
        "path": output.name,
        "documents": documents,
        "tokens_including_eos": tokens,
        "bytes": output.stat().st_size,
        "sha256": digest.hexdigest(),
        "source_token_count_mismatches": mismatched_counts,
        "complete_sequences": {
            str(length): max(0, (tokens - 1) // length) for length in (256, 512, 1024)
        },
    }


def run(args: argparse.Namespace) -> dict:
    dataset = args.dataset.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not 0 <= args.eos_token_id <= 65_535:
        raise ValueError("--eos-token-id must fit uint16")
    manifest_path = dataset / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    try:
        from tokenizers import Tokenizer
    except ImportError as exc:
        raise RuntimeError("tokenizers is not installed") from exc
    tokenizer_path = Path(args.tokenizer).expanduser()
    tokenizer = (
        Tokenizer.from_file(str(tokenizer_path))
        if tokenizer_path.is_file()
        else Tokenizer.from_pretrained(args.tokenizer)
    )
    vocab_size = tokenizer.get_vocab_size(with_added_tokens=True)
    if vocab_size > 65_536:
        raise ValueError(f"tokenizer vocabulary {vocab_size} does not fit uint16")
    if args.eos_token_id >= vocab_size:
        raise ValueError("--eos-token-id is outside the tokenizer vocabulary")

    output.mkdir(parents=True, exist_ok=True)
    split_results: dict[str, dict] = {}
    for split in ("train", "validation"):
        paths = [dataset / item["path"] for item in manifest["splits"][split]["shards"]]
        split_results[split] = write_split(
            paths, output / f"{split}.bin", tokenizer, args.eos_token_id
        )
    result = {
        "schema_version": 1,
        "format": "contiguous token IDs; EOS after every document; causal labels are next-token shift",
        "dtype": "little-endian uint16",
        "tokenizer": args.tokenizer,
        "vocab_size": vocab_size,
        "eos_token_id": args.eos_token_id,
        "source_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "splits": split_results,
    }
    (output / "manifest.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    print(json.dumps(run(build_parser().parse_args()), indent=2))


if __name__ == "__main__":
    main()
