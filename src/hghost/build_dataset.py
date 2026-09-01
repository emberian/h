from __future__ import annotations

import argparse
import gzip
import heapq
import hashlib
import json
import math
import os
import re
import tempfile
import unicodedata
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Iterator, Sequence


DEFAULT_NEAR_DUPLICATE_THRESHOLD = 0.92
DEFAULT_NEAR_DUPLICATE_SKETCH_SIZE = 192
DEFAULT_NEAR_DUPLICATE_MIN_WORDS = 500
SHINGLE_WORDS = 5
MAX_SHINGLES_PER_DOCUMENT = 200_000
_WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Exact-dedupe extracted records and build document-level train/validation shards."
    )
    parser.add_argument("--records", type=Path, default=Path("artifacts/extracted/records"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/dataset"))
    parser.add_argument("--validation-fraction", type=float, default=0.005)
    parser.add_argument(
        "--tokens-per-shard", type=int, default=20_000_000, help="close shard after this many tokens"
    )
    parser.add_argument(
        "--near-duplicate-threshold",
        type=float,
        default=DEFAULT_NEAR_DUPLICATE_THRESHOLD,
        help="bottom-k word-shingle resemblance required to merge documents",
    )
    parser.add_argument(
        "--near-duplicate-sketch-size",
        type=int,
        default=DEFAULT_NEAR_DUPLICATE_SKETCH_SIZE,
    )
    parser.add_argument(
        "--near-duplicate-min-words",
        type=int,
        default=DEFAULT_NEAR_DUPLICATE_MIN_WORDS,
        help="do not fuzzy-dedupe documents shorter than this",
    )
    parser.add_argument("--no-near-dedupe", action="store_true")
    parser.add_argument(
        "--exclude-file",
        type=Path,
        help="JSONL audit exclusions (document_id + reasons), or one document id per line",
    )
    return parser


def read_record(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def record_paths(root: Path) -> list[Path]:
    return sorted(root.rglob("*.json.gz"))


def load_exclusions(path: Path | None) -> dict[str, list[str]]:
    if path is None:
        return {}
    exclusions: dict[str, list[str]] = {}
    with path.expanduser().resolve().open(encoding="utf-8") as stream:
        for raw in stream:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("{"):
                item = json.loads(line)
                document_id = str(item["document_id"])
                reasons = [str(reason) for reason in item.get("reasons") or ["listed"]]
            else:
                document_id = line
                reasons = ["listed"]
            exclusions[document_id] = reasons
    return exclusions


def split_for(content_hash: str, validation_fraction: float) -> str:
    value = int(hashlib.blake2b(content_hash.encode(), digest_size=8).hexdigest(), 16)
    return "validation" if value / 2**64 < validation_fraction else "train"


def canonical_words(text: str) -> list[str]:
    canonical = unicodedata.normalize("NFKC", text).casefold()
    return _WORD_RE.findall(canonical)


def bottom_k_word_shingles(text: str, size: int) -> tuple[int, ...]:
    """Return a deterministic KMV sketch of five-word shingles.

    The sketch is compact enough to build over the full corpus.  Unlike a
    prefix or page sample, it represents the whole document and tolerates
    small OCR/export differences.
    """
    words = canonical_words(text)
    if len(words) < SHINGLE_WORDS:
        return ()
    positions = len(words) - SHINGLE_WORDS + 1
    stride = max(1, math.ceil(positions / MAX_SHINGLES_PER_DOCUMENT))
    heap: list[int] = []
    retained: set[int] = set()
    for index in range(0, positions, stride):
        value = int.from_bytes(
            hashlib.blake2b(
                "\0".join(words[index : index + SHINGLE_WORDS]).encode("utf-8"),
                digest_size=8,
            ).digest(),
            "big",
        )
        if value in retained:
            continue
        if len(heap) < size:
            heapq.heappush(heap, -value)
            retained.add(value)
        elif value < -heap[0]:
            removed = -heapq.heapreplace(heap, -value)
            retained.remove(removed)
            retained.add(value)
    return tuple(sorted(retained))


def bottom_k_resemblance(left: Sequence[int], right: Sequence[int], size: int) -> float:
    """Estimate shingle Jaccard similarity from two bottom-k/KMV sketches."""
    left_set = set(left)
    right_set = set(right)
    union_bottom = sorted(left_set | right_set)[:size]
    if not union_bottom:
        return 0.0
    shared = sum(value in left_set and value in right_set for value in union_bottom)
    return shared / len(union_bottom)


class _DisjointSet:
    def __init__(self, size: int):
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def near_duplicate_clusters(
    records: list[dict], threshold: float, sketch_size: int, min_words: int
) -> tuple[list[list[int]], dict[tuple[int, int], float]]:
    """Find conservative near-duplicate clusters without an all-pairs scan."""
    sketches: list[tuple[int, ...]] = []
    eligible: list[bool] = []
    postings: dict[int, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        word_count = int(record.get("words") or len(canonical_words(record["text"])))
        is_eligible = word_count >= min_words
        sketch = bottom_k_word_shingles(record["text"], sketch_size) if is_eligible else ()
        sketches.append(sketch)
        eligible.append(bool(sketch))
        for value in sketch:
            postings[value].append(index)

    shared_counts: Counter[tuple[int, int]] = Counter()
    for indexes in postings.values():
        # A random 64-bit bottom-k value occurring in scores of documents is
        # generic boilerplate and is not useful candidate evidence.
        if 1 < len(indexes) <= 64:
            for pair in combinations(indexes, 2):
                shared_counts[pair] += 1

    minimum_shared = max(4, round(sketch_size * max(0.05, threshold - 0.20)))
    similarities: dict[tuple[int, int], float] = {}
    groups = _DisjointSet(len(records))
    for (left, right), shared in shared_counts.items():
        if shared < minimum_shared or not eligible[left] or not eligible[right]:
            continue
        score = bottom_k_resemblance(sketches[left], sketches[right], sketch_size)
        if score >= threshold:
            similarities[(left, right)] = score
            groups.union(left, right)

    clustered: dict[int, list[int]] = defaultdict(list)
    for index in range(len(records)):
        clustered[groups.find(index)].append(index)
    return [members for members in clustered.values() if len(members) > 1], similarities


def preferred_record(records: list[dict], members: list[int]) -> int:
    """Prefer the most complete copy, with deterministic provenance tie-breaks."""
    return min(
        members,
        key=lambda index: (
            -int(records[index].get("chars") or 0),
            records[index]["source"],
            records[index]["relative_path"],
        ),
    )


class ShardWriter:
    def __init__(self, output: Path, split: str, tokens_per_shard: int):
        self.output = output
        self.split = split
        self.tokens_per_shard = tokens_per_shard
        self.index = 0
        self.tokens = 0
        self.documents = 0
        self.raw = None
        self.compressed = None
        self.path: Path | None = None
        self.shards: list[dict] = []

    def _open(self) -> None:
        self.path = self.output / f"{self.split}-{self.index:05d}.jsonl.gz"
        self.raw = self.path.open("wb")
        self.compressed = gzip.GzipFile(filename="", mode="wb", fileobj=self.raw, mtime=0)

    def _close(self) -> None:
        if self.compressed is None or self.raw is None or self.path is None:
            return
        self.compressed.close()
        self.raw.close()
        digest = hashlib.sha256()
        with self.path.open("rb") as stream:
            while block := stream.read(8 * 1024 * 1024):
                digest.update(block)
        self.shards.append(
            {
                "path": self.path.name,
                "documents": self.documents,
                "tokens": self.tokens,
                "compressed_bytes": self.path.stat().st_size,
                "sha256": digest.hexdigest(),
            }
        )
        self.index += 1
        self.tokens = 0
        self.documents = 0
        self.raw = self.compressed = self.path = None

    def write(self, record: dict) -> None:
        if self.compressed is None:
            self._open()
        payload = {
            "id": record["document_id"],
            "source": record["source"],
            "path": record["relative_path"],
            "content_sha256": record["content_sha256"],
            "tokens": record["tokens"],
            "text": record["text"],
        }
        assert self.compressed is not None
        self.compressed.write(
            (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
                "utf-8"
            )
        )
        self.tokens += int(record["tokens"])
        self.documents += 1
        if self.tokens >= self.tokens_per_shard:
            self._close()

    def close(self) -> None:
        self._close()


def run(args: argparse.Namespace) -> dict:
    if not 0 < args.validation_fraction < 1:
        raise ValueError("--validation-fraction must be between 0 and 1")
    if args.tokens_per_shard < 1:
        raise ValueError("--tokens-per-shard must be positive")
    near_threshold = float(
        getattr(args, "near_duplicate_threshold", DEFAULT_NEAR_DUPLICATE_THRESHOLD)
    )
    sketch_size = int(
        getattr(args, "near_duplicate_sketch_size", DEFAULT_NEAR_DUPLICATE_SKETCH_SIZE)
    )
    min_words = int(
        getattr(args, "near_duplicate_min_words", DEFAULT_NEAR_DUPLICATE_MIN_WORDS)
    )
    no_near_dedupe = bool(getattr(args, "no_near_dedupe", False))
    exclude_file = getattr(args, "exclude_file", None)
    exclusions = load_exclusions(exclude_file)
    if not 0 < near_threshold <= 1:
        raise ValueError("--near-duplicate-threshold must be in (0, 1]")
    if sketch_size < 16:
        raise ValueError("--near-duplicate-sketch-size must be at least 16")
    if min_words < SHINGLE_WORDS:
        raise ValueError(f"--near-duplicate-min-words must be at least {SHINGLE_WORDS}")
    records_root = args.records.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths = record_paths(records_root)
    loaded = [read_record(path) for path in paths]
    ready_by_location = {
        (record["source"], record["relative_path"]): record
        for record in loaded
        if record["status"] == "ready" and record["document_id"] not in exclusions
    }
    seen: dict[str, dict] = {}
    duplicates: list[dict] = []
    duplicate_reasons: Counter[str] = Counter()
    applied_exclusions: list[dict] = []
    statuses: Counter[str] = Counter()
    selected: list[dict] = []
    for record in loaded:
        statuses[record["status"]] += 1
        if record["status"] != "ready":
            continue
        if record["document_id"] in exclusions:
            applied_exclusions.append(
                {
                    "document_id": record["document_id"],
                    "source": record["source"],
                    "relative_path": record["relative_path"],
                    "reasons": exclusions[record["document_id"]],
                    "tokens": int(record.get("tokens") or 0),
                }
            )
            continue
        relative = Path(record["relative_path"])
        if relative.suffix.casefold() == ".pdf" and relative.stem.casefold().endswith("_text"):
            base_relative = str(relative.with_name(f"{relative.stem[:-5]}.pdf"))
            base = ready_by_location.get((record["source"], base_relative))
            if base is not None:
                duplicates.append(
                    {
                        "reason": "derived_text_pdf_sibling",
                        "duplicate_id": record["document_id"],
                        "duplicate_source": record["source"],
                        "duplicate_path": record["relative_path"],
                        "kept_id": base["document_id"],
                        "kept_source": base["source"],
                        "kept_path": base["relative_path"],
                        "content_sha256": record["content_sha256"],
                    }
                )
                duplicate_reasons["derived_text_pdf_sibling"] += 1
                continue
        digest = record["content_sha256"]
        if digest in seen:
            duplicates.append(
                {
                    "reason": "exact_normalized_content",
                    "duplicate_id": record["document_id"],
                    "duplicate_source": record["source"],
                    "duplicate_path": record["relative_path"],
                    "kept_id": seen[digest]["document_id"],
                    "kept_source": seen[digest]["source"],
                    "kept_path": seen[digest]["relative_path"],
                    "content_sha256": digest,
                }
            )
            duplicate_reasons["exact_normalized_content"] += 1
            continue
        seen[digest] = record
        selected.append(record)

    if not no_near_dedupe:
        clusters, similarities = near_duplicate_clusters(
            selected, near_threshold, sketch_size, min_words
        )
        removed_indexes: set[int] = set()
        for members in clusters:
            kept_index = preferred_record(selected, members)
            for duplicate_index in members:
                if duplicate_index == kept_index:
                    continue
                pair = (min(kept_index, duplicate_index), max(kept_index, duplicate_index))
                duplicate = selected[duplicate_index]
                kept = selected[kept_index]
                duplicates.append(
                    {
                        "reason": "near_normalized_content",
                        "similarity": similarities.get(pair),
                        "duplicate_id": duplicate["document_id"],
                        "duplicate_source": duplicate["source"],
                        "duplicate_path": duplicate["relative_path"],
                        "kept_id": kept["document_id"],
                        "kept_source": kept["source"],
                        "kept_path": kept["relative_path"],
                        "content_sha256": duplicate["content_sha256"],
                    }
                )
                duplicate_reasons["near_normalized_content"] += 1
                removed_indexes.add(duplicate_index)
        selected = [record for index, record in enumerate(selected) if index not in removed_indexes]

    selected.sort(key=lambda record: (record["content_sha256"], record["document_id"]))
    writers = {
        split: ShardWriter(output, split, args.tokens_per_shard)
        for split in ("train", "validation")
    }
    split_counts: dict[str, Counter[str]] = {
        "train": Counter(),
        "validation": Counter(),
    }
    for record in selected:
        split = split_for(record["content_sha256"], args.validation_fraction)
        writers[split].write(record)
        split_counts[split]["documents"] += 1
        split_counts[split]["tokens"] += int(record["tokens"])
    for writer in writers.values():
        writer.close()

    with (output / "duplicates.jsonl").open("w", encoding="utf-8") as stream:
        for duplicate in duplicates:
            stream.write(json.dumps(duplicate, ensure_ascii=False) + "\n")
    with (output / "exclusions_applied.jsonl").open("w", encoding="utf-8") as stream:
        for exclusion in applied_exclusions:
            stream.write(json.dumps(exclusion, ensure_ascii=False) + "\n")
    manifest = {
        "schema_version": 1,
        "source_record_count": len(paths),
        "source_statuses": dict(sorted(statuses.items())),
        "exact_duplicates_removed": duplicate_reasons["exact_normalized_content"],
        "duplicates_removed": len(duplicates),
        "duplicates_by_reason": dict(sorted(duplicate_reasons.items())),
        "curation_exclusions": {
            "listed": len(exclusions),
            "applied_documents": len(applied_exclusions),
            "applied_tokens": sum(item["tokens"] for item in applied_exclusions),
        },
        "near_duplicate_settings": {
            "enabled": not no_near_dedupe,
            "threshold": near_threshold,
            "sketch_size": sketch_size,
            "minimum_words": min_words,
            "shingle_words": SHINGLE_WORDS,
        },
        "validation_fraction": args.validation_fraction,
        "tokens_per_shard": args.tokens_per_shard,
        "splits": {
            split: {
                "documents": split_counts[split]["documents"],
                "tokens": split_counts[split]["tokens"],
                "shards": writers[split].shards,
            }
            for split in ("train", "validation")
        },
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    manifest = run(build_parser().parse_args())
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
