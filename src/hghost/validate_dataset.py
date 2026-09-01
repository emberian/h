from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np


STAT_CHUNK_TOKENS = 8 * 1024 * 1024


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify curated JSONL shards and uint16 token streams byte-for-byte."
    )
    parser.add_argument("--dataset", type=Path, default=Path("artifacts/dataset"))
    parser.add_argument("--tokenized", type=Path, default=Path("artifacts/tokenized"))
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/tokenized/validation-report.json")
    )
    return parser


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _binary_stats(values: np.memmap, eos_token_id: int) -> tuple[int, int, int]:
    minimum = maximum = -1
    eos_count = 0
    for offset in range(0, len(values), STAT_CHUNK_TOKENS):
        chunk = values[offset : offset + STAT_CHUNK_TOKENS]
        if not len(chunk):
            continue
        chunk_minimum = int(chunk.min())
        chunk_maximum = int(chunk.max())
        minimum = chunk_minimum if minimum < 0 else min(minimum, chunk_minimum)
        maximum = max(maximum, chunk_maximum)
        eos_count += int(np.count_nonzero(chunk == eos_token_id))
    return minimum, maximum, eos_count


def run(args: argparse.Namespace) -> dict:
    dataset = args.dataset.expanduser().resolve()
    tokenized = args.tokenized.expanduser().resolve()
    output = args.output.expanduser().resolve()
    dataset_manifest_path = dataset / "manifest.json"
    token_manifest_path = tokenized / "manifest.json"
    dataset_manifest = _load_json(dataset_manifest_path)
    token_manifest = _load_json(token_manifest_path)
    expected_source_hash = token_manifest["source_manifest_sha256"]
    actual_source_hash = sha256_file(dataset_manifest_path)
    if actual_source_hash != expected_source_hash:
        raise ValueError("Token stream was not built from this dataset manifest")
    if token_manifest.get("dtype") != "little-endian uint16":
        raise ValueError(f"Unsupported token dtype: {token_manifest.get('dtype')}")

    selected_ids: set[str] = set()
    content_hashes: dict[str, set[str]] = {"train": set(), "validation": set()}
    split_reports: dict[str, dict] = {}
    for split in ("train", "validation"):
        expected_split = dataset_manifest["splits"][split]
        document_count = token_count = 0
        for shard in expected_split["shards"]:
            path = dataset / shard["path"]
            if path.stat().st_size != int(shard["compressed_bytes"]):
                raise ValueError(f"Compressed size mismatch: {path}")
            if sha256_file(path) != shard["sha256"]:
                raise ValueError(f"Shard hash mismatch: {path}")
            shard_documents = shard_tokens = 0
            with gzip.open(path, "rt", encoding="utf-8") as stream:
                for line in stream:
                    record = json.loads(line)
                    document_id = str(record["id"])
                    content_hash = str(record["content_sha256"])
                    if document_id in selected_ids:
                        raise ValueError(f"Document appears more than once: {document_id}")
                    if content_hash in content_hashes[split]:
                        raise ValueError(f"Content hash appears more than once in {split}: {content_hash}")
                    selected_ids.add(document_id)
                    content_hashes[split].add(content_hash)
                    shard_documents += 1
                    shard_tokens += int(record["tokens"])
            if shard_documents != int(shard["documents"]) or shard_tokens != int(shard["tokens"]):
                raise ValueError(f"Shard record totals mismatch: {path}")
            document_count += shard_documents
            token_count += shard_tokens
        if document_count != int(expected_split["documents"]):
            raise ValueError(f"Document total mismatch for {split}")
        if token_count != int(expected_split["tokens"]):
            raise ValueError(f"Token total mismatch for {split}")

        binary_spec = token_manifest["splits"][split]
        binary = tokenized / binary_spec["path"]
        binary_tokens = int(binary_spec["tokens_including_eos"])
        if int(binary_spec["documents"]) != document_count:
            raise ValueError(f"Token manifest document total mismatch for {split}")
        if binary_tokens < document_count:
            raise ValueError(f"Token manifest has fewer tokens than documents for {split}")
        if binary.stat().st_size != int(binary_spec["bytes"]):
            raise ValueError(f"Binary size mismatch: {binary}")
        if binary.stat().st_size != binary_tokens * 2:
            raise ValueError(f"Binary token count mismatch: {binary}")
        if sha256_file(binary) != binary_spec["sha256"]:
            raise ValueError(f"Binary hash mismatch: {binary}")
        values = np.memmap(binary, mode="r", dtype="<u2")
        minimum_token, maximum_token, eos_count = _binary_stats(
            values, int(token_manifest["eos_token_id"])
        )
        if maximum_token >= int(token_manifest["vocab_size"]):
            raise ValueError(f"Out-of-vocabulary token {maximum_token} in {binary}")
        if eos_count != document_count:
            raise ValueError(
                f"EOS count mismatch for {split}: expected {document_count}, found {eos_count}"
            )
        tokenized_source_tokens = binary_tokens - document_count
        source_count_mismatches = int(binary_spec.get("source_token_count_mismatches", 0))
        if source_count_mismatches == 0 and tokenized_source_tokens != token_count:
            raise ValueError(
                f"Tokenized/source count mismatch for {split} despite zero document mismatches"
            )
        split_reports[split] = {
            "documents": document_count,
            "source_tokens": token_count,
            "dataset_source_tokens": token_count,
            "tokenized_source_tokens": tokenized_source_tokens,
            "source_token_count_mismatches": source_count_mismatches,
            "eos_tokens": eos_count,
            "tokens_including_eos": binary_tokens,
            "bytes": binary.stat().st_size,
            "sha256": binary_spec["sha256"],
            "minimum_token_id": minimum_token,
            "maximum_token_id": maximum_token,
        }

    overlap = content_hashes["train"] & content_hashes["validation"]
    if overlap:
        raise ValueError(f"Train/validation content-hash overlap: {len(overlap)}")

    excluded_ids: set[str] = set()
    exclusions_path = dataset / "exclusions_applied.jsonl"
    with exclusions_path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                excluded_ids.add(str(json.loads(line)["document_id"]))
    duplicate_ids: set[str] = set()
    duplicates_path = dataset / "duplicates.jsonl"
    with duplicates_path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                duplicate_ids.add(str(json.loads(line)["duplicate_id"]))
    leaked_exclusions = selected_ids & excluded_ids
    leaked_duplicates = selected_ids & duplicate_ids
    if leaked_exclusions or leaked_duplicates:
        raise ValueError(
            f"Curated stream leaked exclusions={len(leaked_exclusions)}, duplicates={len(leaked_duplicates)}"
        )

    report = {
        "schema_version": 1,
        "ok": True,
        "dataset_manifest_sha256": actual_source_hash,
        "tokenizer": token_manifest["tokenizer"],
        "vocab_size": int(token_manifest["vocab_size"]),
        "eos_token_id": int(token_manifest["eos_token_id"]),
        "selected_documents": len(selected_ids),
        "excluded_documents": len(excluded_ids),
        "duplicate_documents": len(duplicate_ids),
        "cross_split_content_hash_overlap": 0,
        "splits": split_reports,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    print(json.dumps(run(build_parser().parse_args()), indent=2))


if __name__ == "__main__":
    main()
