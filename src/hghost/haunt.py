"""Haunting index: exact-match provenance over the sealed training token stream.

The index is a token-aligned suffix array over ``train.bin``.  Every uint16
token is written as two big-endian bytes, so byte order equals token order;
libdivsufsort sorts the byte string and only the even (token-aligned) byte
offsets are kept.  One structure answers three questions:

* provenance: which corpus document does a generated span quote, and where?
* memorization: what fraction of a generation is covered by exact 8/16/32-gram
  matches against the training stream?
* page furniture: which token n-grams recur across many distinct documents
  (running heads, scan notices, footers, dot leaders)?
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import platform
import resource
import sys
import time
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

import numpy as np

from .census import DEFAULT_MODEL

INDEX_FORMAT_VERSION = 1
SUFFIX_ARRAY_FILE = "suffix-array.npy"
DOCUMENTS_FILE = "documents.jsonl"
MANIFEST_FILE = "index-manifest.json"
DEFAULT_EOS_TOKEN_ID = 11
DEFAULT_TOKENIZER_FILE = Path("kaggle/base_model_dataset_public/tokenizer.json")
DEFAULT_THRESHOLDS = (8, 16, 32)
FILTER_CHUNK = 1 << 26
LCP_CHUNK = 1 << 24
FURNITURE_BATCH_ROWS = 1 << 25
MAX_OCCURRENCE_ROWS = 1 << 17
TOKEN_DTYPE = np.dtype("<u2")


# --------------------------------------------------------------------------- documents


@dataclass(frozen=True)
class DocumentEntry:
    id: str
    source: str
    path: str
    token_offset: int
    tokens: int

    @property
    def end(self) -> int:
        """Exclusive end of the document in the stream, EOS included."""
        return self.token_offset + self.tokens + 1

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "path": self.path,
            "token_offset": self.token_offset,
            "tokens": self.tokens,
        }


def read_document_table(dataset: Path, split: str = "train") -> list[DocumentEntry]:
    """Reconstruct document offsets from the dataset shards in manifest order."""
    manifest = json.loads((dataset / "manifest.json").read_text(encoding="utf-8"))
    entries: list[DocumentEntry] = []
    offset = 0
    for shard in manifest["splits"][split]["shards"]:
        with gzip.open(dataset / shard["path"], "rt", encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                record = json.loads(line)
                count = int(record["tokens"])
                entries.append(
                    DocumentEntry(
                        str(record["id"]), str(record["source"]), str(record["path"]), offset, count
                    )
                )
                offset += count + 1
    return entries


def read_documents_file(path: Path) -> list[DocumentEntry]:
    entries: list[DocumentEntry] = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                item = json.loads(line)
                entries.append(
                    DocumentEntry(
                        item["id"],
                        item["source"],
                        item["path"],
                        int(item["token_offset"]),
                        int(item["tokens"]),
                    )
                )
    return entries


def verify_document_layout(
    tokens: np.ndarray, entries: Sequence[DocumentEntry], eos_token_id: int
) -> dict:
    """Compare EOS positions in the stream with the manifest-reconstructed document ends."""
    eos_positions = np.flatnonzero(tokens == eos_token_id)
    expected_ends = np.array([entry.end - 1 for entry in entries], dtype=np.int64)
    expected_total = entries[-1].end if entries else 0
    problems: list[str] = []
    if int(tokens.shape[0]) != expected_total:
        problems.append(
            f"stream has {tokens.shape[0]} tokens but the manifest reconstructs {expected_total}"
        )
    if eos_positions.size != expected_ends.size:
        problems.append(
            f"stream has {eos_positions.size} EOS tokens but the manifest lists {len(entries)}"
            " documents"
        )
    else:
        diverging = np.flatnonzero(eos_positions != expected_ends)
        if diverging.size:
            first = int(diverging[0])
            problems.append(
                f"{diverging.size} EOS positions differ from reconstructed document ends;"
                f" first at document {first}: stream {eos_positions[first]},"
                f" manifest {expected_ends[first]}"
            )
    return {
        "eos_count": int(eos_positions.size),
        "documents": len(entries),
        "stream_tokens": int(tokens.shape[0]),
        "expected_tokens": int(expected_total),
        "problems": problems,
    }


# --------------------------------------------------------------------------- streams


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 24), b""):
            digest.update(block)
    return digest.hexdigest()


def load_token_stream(path: Path, in_memory: bool = False) -> np.ndarray:
    if in_memory:
        return np.fromfile(path, dtype=TOKEN_DTYPE)
    return np.memmap(path, dtype=TOKEN_DTYPE, mode="r")


def peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def load_query_tokens(spec: str, offset: int = 0, count: int | None = None) -> np.ndarray:
    """Read a query token sequence from .bin (uint16 LE), .npy, .json, or a JSON list literal."""
    text = spec.strip()
    if text.startswith("["):
        values = np.asarray(json.loads(text), dtype=np.int64)
    else:
        path = Path(spec).expanduser()
        if path.suffix == ".npy":
            values = np.load(path).astype(np.int64)
        elif path.suffix == ".json":
            values = np.asarray(json.loads(path.read_text(encoding="utf-8")), dtype=np.int64)
        else:
            values = np.fromfile(path, dtype=TOKEN_DTYPE).astype(np.int64)
    stop = None if count is None else offset + count
    return as_token_array(values[offset:stop])


def as_token_array(values: Iterable[int] | np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=np.int64).reshape(-1)
    if array.size and (array.min() < 0 or array.max() > 65_535):
        raise ValueError("token IDs must fit uint16")
    return array.astype(np.uint16)


def load_tokenizer(spec: str | None):
    """Load a `tokenizers` Tokenizer from a file path or hub id; None when unavailable."""
    try:
        from tokenizers import Tokenizer
    except ImportError:
        return None
    candidates = [spec] if spec else [str(DEFAULT_TOKENIZER_FILE), DEFAULT_MODEL]
    for candidate in candidates:
        path = Path(candidate).expanduser()
        try:
            if path.is_file():
                return Tokenizer.from_file(str(path))
            if not spec and candidate == str(DEFAULT_TOKENIZER_FILE):
                continue
            return Tokenizer.from_pretrained(candidate)
        except Exception as exc:  # noqa: BLE001 - tokenizer loading failures are non-fatal
            print(f"warning: could not load tokenizer {candidate!r}: {exc}", file=sys.stderr)
    return None


def decode_tokens(tokenizer, tokens: np.ndarray) -> str | None:
    if tokenizer is None:
        return None
    return tokenizer.decode([int(token) for token in tokens], skip_special_tokens=False)


# --------------------------------------------------------------------------- build


def build_suffix_array(tokens: np.ndarray, output: Path) -> dict:
    """Sort all token-aligned suffixes of ``tokens`` and store them as a memmapped .npy."""
    from pydivsufsort import divsufsort

    count = int(tokens.shape[0])
    dtype = np.int32 if 2 * count < np.iinfo(np.int32).max else np.int64
    started = time.perf_counter()
    big_endian = np.ascontiguousarray(tokens, dtype=">u2")
    byte_suffixes = divsufsort(big_endian.view(np.uint8))
    del big_endian
    sort_seconds = time.perf_counter() - started
    suffix_array = np.lib.format.open_memmap(output, mode="w+", dtype=dtype, shape=(count,))
    written = 0
    for start in range(0, byte_suffixes.shape[0], FILTER_CHUNK):
        chunk = byte_suffixes[start : start + FILTER_CHUNK]
        aligned = chunk[(chunk & 1) == 0] >> 1
        suffix_array[written : written + aligned.shape[0]] = aligned
        written += int(aligned.shape[0])
    del byte_suffixes
    if written != count:
        raise RuntimeError(f"kept {written} token-aligned suffixes, expected {count}")
    suffix_array.flush()
    del suffix_array
    return {
        "dtype": np.dtype(dtype).name,
        "sort_seconds": round(sort_seconds, 3),
        "seconds": round(time.perf_counter() - started, 3),
    }


def suffix_order_violations(
    tokens: np.ndarray, suffix_array: np.ndarray, ranks: Iterable[int], depth: int
) -> int:
    """Count adjacent suffix-array rows that are out of order within ``depth`` tokens."""
    count = int(tokens.shape[0])
    violations = 0
    for rank in ranks:
        left = int(suffix_array[rank])
        right = int(suffix_array[rank + 1])
        left_length = min(depth, count - left)
        right_length = min(depth, count - right)
        shared = min(left_length, right_length)
        left_tokens = tokens[left : left + shared]
        right_tokens = tokens[right : right + shared]
        mismatches = np.flatnonzero(left_tokens != right_tokens)
        if mismatches.size:
            if left_tokens[mismatches[0]] > right_tokens[mismatches[0]]:
                violations += 1
        elif right_length < depth and left_length > right_length:
            violations += 1
    return violations


def build_index(
    tokens_path: Path,
    dataset: Path,
    output: Path,
    *,
    split: str = "train",
    eos_token_id: int = DEFAULT_EOS_TOKEN_ID,
    check_samples: int = 20_000,
) -> dict:
    started_at = datetime.now(UTC)
    started = time.perf_counter()
    tokens_path = tokens_path.expanduser().resolve()
    dataset = dataset.expanduser().resolve()
    output = output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    tokens = load_token_stream(tokens_path)
    entries = read_document_table(dataset, split)
    layout = verify_document_layout(tokens, entries, eos_token_id)
    if layout["problems"]:
        raise ValueError(
            "document offset reconstruction disagrees with the stream: "
            + "; ".join(layout["problems"])
        )
    stream_sha256 = sha256_file(tokens_path)
    suffix_stats = build_suffix_array(tokens, output / SUFFIX_ARRAY_FILE)

    suffix_array = np.load(output / SUFFIX_ARRAY_FILE, mmap_mode="r")
    count = int(tokens.shape[0])
    sample_count = min(check_samples, max(count - 1, 0))
    ranks = np.random.default_rng(0).choice(count - 1, size=sample_count, replace=False)
    violations = suffix_order_violations(tokens, suffix_array, sorted(int(r) for r in ranks), 64)
    if violations:
        raise RuntimeError(f"suffix array failed the order check: {violations} violations")

    with (output / DOCUMENTS_FILE).open("w", encoding="utf-8") as stream:
        for entry in entries:
            stream.write(json.dumps(entry.as_dict(), ensure_ascii=False) + "\n")

    manifest = {
        "schema_version": INDEX_FORMAT_VERSION,
        "kind": "haunting-index",
        "tokens_path": str(tokens_path),
        "tokens_bytes": tokens_path.stat().st_size,
        "tokens_sha256": stream_sha256,
        "token_dtype": "little-endian uint16",
        "token_count": count,
        "eos_token_id": eos_token_id,
        "eos_count": layout["eos_count"],
        "documents": len(entries),
        "split": split,
        "dataset_manifest_sha256": sha256_file(dataset / "manifest.json"),
        "suffix_array": {
            "path": SUFFIX_ARRAY_FILE,
            "dtype": suffix_stats["dtype"],
            "entries": count,
            "encoding": "uint16 tokens as big-endian byte pairs; even byte offsets kept",
            "order_check": {"samples": sample_count, "depth": 64, "violations": violations},
        },
        "library": {
            "name": "pydivsufsort",
            "version": metadata.version("pydivsufsort"),
            "numpy": np.__version__,
        },
        "build": {
            "started": started_at.isoformat(timespec="seconds"),
            "seconds": round(time.perf_counter() - started, 3),
            "sort_seconds": suffix_stats["sort_seconds"],
            "suffix_array_seconds": suffix_stats["seconds"],
            "peak_rss_bytes": peak_rss_bytes(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
    }
    (output / MANIFEST_FILE).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


# --------------------------------------------------------------------------- queries


@dataclass(frozen=True)
class Span:
    query_offset: int
    length: int
    corpus_offset: int

    @property
    def end(self) -> int:
        return self.query_offset + self.length


class HauntingIndex:
    def __init__(
        self,
        tokens: np.ndarray,
        suffix_array: np.ndarray,
        documents: Sequence[DocumentEntry],
        eos_token_id: int = DEFAULT_EOS_TOKEN_ID,
        manifest: dict | None = None,
    ):
        self.tokens = tokens
        self.suffix_array = suffix_array
        self.documents = list(documents)
        self.eos_token_id = eos_token_id
        self.manifest = manifest or {}
        self.count = int(tokens.shape[0])
        self.offsets = np.array([entry.token_offset for entry in self.documents], dtype=np.int64)
        if suffix_array.shape[0] != self.count:
            raise ValueError("suffix array and token stream have different lengths")

    @classmethod
    def load(
        cls,
        directory: Path,
        tokens_path: Path | None = None,
        *,
        in_memory: bool = False,
        verify: bool = False,
    ) -> HauntingIndex:
        directory = directory.expanduser().resolve()
        manifest = json.loads((directory / MANIFEST_FILE).read_text(encoding="utf-8"))
        path = (tokens_path or Path(manifest["tokens_path"])).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"token stream {path} is missing; pass --stream")
        if path.stat().st_size != manifest["tokens_bytes"]:
            raise ValueError(f"token stream {path} has a different size than the indexed stream")
        if verify and sha256_file(path) != manifest["tokens_sha256"]:
            raise ValueError(f"token stream {path} does not match the indexed sha256")
        tokens = load_token_stream(path, in_memory)
        suffix_array = np.load(directory / manifest["suffix_array"]["path"], mmap_mode="r")
        documents = read_documents_file(directory / DOCUMENTS_FILE)
        return cls(tokens, suffix_array, documents, int(manifest["eos_token_id"]), manifest)

    # -- primitive comparisons ------------------------------------------------

    def compare(self, pattern: np.ndarray, offset: int) -> tuple[int, int]:
        """Return (lcp, order); order is -1, 0, 1 for pattern <, prefix-of, > the suffix."""
        limit = min(int(pattern.shape[0]), self.count - offset)
        segment = self.tokens[offset : offset + limit]
        head = pattern[:limit]
        mismatches = np.flatnonzero(segment != head)
        if mismatches.size:
            index = int(mismatches[0])
            return index, -1 if head[index] < segment[index] else 1
        if limit == pattern.shape[0]:
            return limit, 0
        return limit, 1

    def _bound(self, pattern: np.ndarray, upper: bool) -> tuple[int, int, int]:
        low, high = 0, self.count
        best_length, best_offset = 0, -1
        while low < high:
            middle = (low + high) // 2
            offset = int(self.suffix_array[middle])
            lcp, order = self.compare(pattern, offset)
            if lcp > best_length:
                best_length, best_offset = lcp, offset
            if order > 0 or (upper and order == 0):
                low = middle + 1
            else:
                high = middle
        return low, best_length, best_offset

    def occurrence_range(self, pattern: np.ndarray) -> tuple[int, int]:
        """Suffix-array rank range [low, high) of every corpus occurrence of ``pattern``."""
        if pattern.shape[0] == 0:
            return 0, self.count
        low = self._bound(pattern, upper=False)[0]
        high = self._bound(pattern, upper=True)[0]
        return low, high

    def longest_match(self, pattern: np.ndarray) -> tuple[int, int]:
        """Length of the longest corpus-occurring prefix of ``pattern`` and one corpus offset."""
        if pattern.shape[0] == 0:
            return 0, -1
        rank, best_length, best_offset = self._bound(pattern, upper=False)
        for candidate in (rank - 1, rank):
            if 0 <= candidate < self.count:
                offset = int(self.suffix_array[candidate])
                lcp, _ = self.compare(pattern, offset)
                if lcp > best_length:
                    best_length, best_offset = lcp, offset
        return best_length, best_offset

    def match_lengths(self, query: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Longest corpus match starting at every query position, with one corpus offset each."""
        query = np.ascontiguousarray(query, dtype=np.uint16)
        size = int(query.shape[0])
        lengths = np.zeros(size, dtype=np.int64)
        offsets = np.full(size, -1, dtype=np.int64)
        for index in range(size):
            remaining = size - index
            if index and lengths[index - 1] - 1 == remaining:
                lengths[index] = remaining
                offsets[index] = offsets[index - 1] + 1
                continue
            lengths[index], offsets[index] = self.longest_match(query[index:])
        return lengths, offsets

    # -- documents ------------------------------------------------------------

    def document_index(self, offset: int) -> int:
        return int(np.searchsorted(self.offsets, offset, side="right") - 1)

    def document_at(self, offset: int) -> DocumentEntry:
        return self.documents[self.document_index(offset)]

    def documents_for_ranks(self, low: int, high: int, limit: int = MAX_OCCURRENCE_ROWS):
        rows = np.asarray(self.suffix_array[low : min(high, low + limit)], dtype=np.int64)
        indexes = np.unique(np.searchsorted(self.offsets, rows, side="right") - 1)
        return indexes, high - low > limit

    def describe_span(
        self, query: np.ndarray, span: Span, tokenizer=None, max_documents: int = 5
    ) -> dict:
        document = self.document_at(span.corpus_offset)
        pattern = np.ascontiguousarray(query[span.query_offset : span.end], dtype=np.uint16)
        low, high = self.occurrence_range(pattern)
        indexes, truncated = self.documents_for_ranks(low, high)
        record = {
            "type": "span",
            "query_offset": span.query_offset,
            "length": span.length,
            "corpus_offset": span.corpus_offset,
            "document": {"id": document.id, "source": document.source, "path": document.path},
            "document_offset": span.corpus_offset - document.token_offset,
            "crosses_document_boundary": span.corpus_offset + span.length > document.end,
            "occurrences": high - low,
            "distinct_documents": int(indexes.size),
            "distinct_documents_truncated": truncated,
            "documents": [self.documents[int(i)].id for i in indexes[:max_documents]],
        }
        text = decode_tokens(tokenizer, pattern)
        if text is not None:
            record["text"] = text
        return record


def maximal_spans(lengths: np.ndarray, offsets: np.ndarray, min_tokens: int) -> list[Span]:
    """Matched spans not contained in another matched span, of at least ``min_tokens``."""
    spans: list[Span] = []
    for index in range(int(lengths.shape[0])):
        length = int(lengths[index])
        if length < min_tokens:
            continue
        if index and length < lengths[index - 1]:
            continue
        spans.append(Span(index, length, int(offsets[index])))
    return spans


def coverage_fractions(lengths: np.ndarray, thresholds: Sequence[int]) -> dict[int, float]:
    """Fraction of query positions inside some exact match of at least each threshold."""
    size = int(lengths.shape[0])
    result: dict[int, float] = {}
    for threshold in thresholds:
        if size == 0:
            result[threshold] = 0.0
            continue
        marks = np.zeros(size + 1, dtype=np.int64)
        starts = np.flatnonzero(lengths >= threshold)
        np.add.at(marks, starts, 1)
        np.add.at(marks, starts + lengths[starts], -1)
        result[threshold] = float((np.cumsum(marks[:size]) > 0).mean())
    return result


def scan_generation(
    index: HauntingIndex,
    query: np.ndarray,
    thresholds: Sequence[int],
    *,
    max_spans: int = 3,
    tokenizer=None,
) -> dict:
    lengths, offsets = index.match_lengths(query)
    min_threshold = min(thresholds)
    spans = maximal_spans(lengths, offsets, min_threshold)
    per_document: dict[int, int] = {}
    for span in spans:
        document = index.document_index(span.corpus_offset)
        per_document[document] = per_document.get(document, 0) + span.length
    top_documents = sorted(per_document.items(), key=lambda item: (-item[1], item[0]))[:5]
    longest = sorted(spans, key=lambda span: (-span.length, span.query_offset))[:max_spans]
    return {
        "tokens": int(query.shape[0]),
        "longest_match": int(lengths.max()) if lengths.size else 0,
        "coverage": {
            str(threshold): value
            for threshold, value in coverage_fractions(lengths, thresholds).items()
        },
        "span_count": len(spans),
        "top_documents": [
            {**index.documents[document].as_dict(), "quoted_tokens": total}
            for document, total in top_documents
        ],
        "longest_spans": [
            index.describe_span(query, span, tokenizer, max_documents=3) for span in longest
        ],
    }


# --------------------------------------------------------------------------- furniture


def capped_lcp(index: HauntingIndex, max_tokens: int, chunk: int = LCP_CHUNK) -> np.ndarray:
    """lcp[r] = min(max_tokens, lcp(suffix at rank r-1, suffix at rank r)); lcp[0] = 0."""
    count = index.count
    tokens = index.tokens
    suffix_array = index.suffix_array
    result = np.zeros(count, dtype=np.uint8)
    for start in range(1, count, chunk):
        stop = min(count, start + chunk)
        left = np.asarray(suffix_array[start - 1 : stop - 1], dtype=np.int64)
        right = np.asarray(suffix_array[start:stop], dtype=np.int64)
        depth = np.zeros(stop - start, dtype=np.uint8)
        active = np.arange(stop - start)
        for shift in range(max_tokens):
            left_positions = left[active] + shift
            right_positions = right[active] + shift
            inside = (left_positions < count) & (right_positions < count)
            equal = np.zeros(active.shape[0], dtype=bool)
            equal[inside] = tokens[left_positions[inside]] == tokens[right_positions[inside]]
            active = active[equal]
            if active.size == 0:
                break
            depth[active] = shift + 1
        result[start:stop] = depth
    return result


def _repeat_groups(
    index: HauntingIndex,
    lcp: np.ndarray,
    level: int,
    min_documents: int,
    max_tokens: int,
    batch_rows: int,
) -> Iterator[dict]:
    """Yield left-maximal repeated ``level``-grams shared by >= min_documents documents."""
    hits = np.concatenate([lcp >= level, [False]])
    run_starts = np.flatnonzero(hits[1:] & ~hits[:-1]) + 1
    run_stops = np.flatnonzero(hits[:-1] & ~hits[1:]) + 1
    first_rows = run_starts - 1
    sizes = run_stops - run_starts + 1
    keep = sizes >= min_documents
    first_rows, sizes = first_rows[keep], sizes[keep]
    document_count = len(index.documents)
    boundaries = np.cumsum(sizes)
    batch_start = 0
    while batch_start < first_rows.shape[0]:
        base = boundaries[batch_start - 1] if batch_start else 0
        batch_stop = int(np.searchsorted(boundaries, base + batch_rows, side="right"))
        batch_stop = max(batch_stop, batch_start + 1)
        starts = first_rows[batch_start:batch_stop]
        counts = sizes[batch_start:batch_stop]
        group_starts = np.concatenate([[0], np.cumsum(counts)[:-1]])
        total = int(counts.sum())
        group_ids = np.repeat(np.arange(counts.shape[0]), counts)
        rows = np.repeat(starts - group_starts, counts) + np.arange(total)
        positions = np.asarray(index.suffix_array[rows], dtype=np.int64)
        documents = np.searchsorted(index.offsets, positions, side="right") - 1
        unique_keys = np.unique(group_ids * document_count + documents)
        distinct = np.bincount(unique_keys // document_count, minlength=counts.shape[0])
        previous = np.where(
            positions > 0,
            np.asarray(index.tokens[np.maximum(positions - 1, 0)], dtype=np.int64),
            -1,
        )
        left_maximal = np.minimum.reduceat(previous, group_starts) != np.maximum.reduceat(
            previous, group_starts
        )
        extensions = lcp[rows].astype(np.int64)
        extensions[group_starts] = max_tokens
        common = np.minimum.reduceat(extensions, group_starts)
        for group in np.flatnonzero((distinct >= min_documents) & left_maximal):
            yield {
                "level": level,
                "first_row": int(starts[group]),
                "occurrences": int(counts[group]),
                "documents": int(distinct[group]),
                "length": int(common[group]),
            }
        batch_start = batch_stop


def find_furniture(
    index: HauntingIndex,
    *,
    min_tokens: int = 8,
    min_documents: int = 5,
    max_tokens: int = 64,
    top: int = 500,
    lcp: np.ndarray | None = None,
    batch_rows: int = FURNITURE_BATCH_ROWS,
    tokenizer=None,
    examples: int = 3,
) -> list[dict]:
    """Token n-grams (>= min_tokens) shared by >= min_documents documents, by document count."""
    if lcp is None:
        lcp = capped_lcp(index, max_tokens)
    levels: list[int] = []
    level = min_tokens
    while level <= max_tokens:
        levels.append(level)
        level *= 2
    found: dict[tuple[int, int], dict] = {}
    for level in levels:
        for group in _repeat_groups(index, lcp, level, min_documents, max_tokens, batch_rows):
            found.setdefault((group["first_row"], group["occurrences"]), group)
    ranked = sorted(
        found.values(),
        key=lambda item: (
            -item["documents"],
            -item["length"],
            -item["occurrences"],
            item["first_row"],
        ),
    )[:top]
    results = []
    for rank, group in enumerate(ranked, start=1):
        first_row = group["first_row"]
        offset = int(index.suffix_array[first_row])
        pattern = np.asarray(index.tokens[offset : offset + group["length"]], dtype=np.uint16)
        indexes, _ = index.documents_for_ranks(first_row, first_row + group["occurrences"])
        record = {
            "type": "furniture",
            "rank": rank,
            "documents": group["documents"],
            "occurrences": group["occurrences"],
            "length": group["length"],
            "length_truncated": group["length"] >= max_tokens,
            "level": group["level"],
            "corpus_offset": offset,
            "tokens": pattern.tolist(),
            "examples": [
                {"id": index.documents[int(i)].id, "source": index.documents[int(i)].source}
                for i in indexes[:examples]
            ],
        }
        text = decode_tokens(tokenizer, pattern)
        if text is not None:
            record["text"] = text
        results.append(record)
    return results


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Exact-match provenance index (suffix array) over the training token stream."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build", help="build the suffix array and document table")
    build.add_argument("--tokens", type=Path, default=Path("artifacts/tokenized/train.bin"))
    build.add_argument("--dataset", type=Path, default=Path("artifacts/dataset"))
    build.add_argument("--output", type=Path, default=Path("artifacts/haunting-index"))
    build.add_argument("--split", default="train")
    build.add_argument("--eos-token-id", type=int, default=DEFAULT_EOS_TOKEN_ID)
    build.add_argument("--check-samples", type=int, default=20_000)

    def add_index_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument("--index", type=Path, default=Path("artifacts/haunting-index"))
        command.add_argument("--stream", type=Path, help="override the indexed token stream path")
        command.add_argument("--in-memory", action="store_true", help="load the stream into RAM")
        command.add_argument("--verify", action="store_true", help="re-hash the stream first")
        command.add_argument("--tokenizer", help="tokenizer.json path or hub id for text/decoding")

    query = commands.add_parser("query", help="map a token sequence back to corpus documents")
    add_index_arguments(query)
    query.add_argument("--tokens", help=".bin (uint16 LE), .npy, .json, or a JSON list literal")
    query.add_argument("--text", help="tokenize this text as the query")
    query.add_argument("--offset", type=int, default=0, help="skip this many query tokens")
    query.add_argument("--count", type=int, help="use at most this many query tokens")
    query.add_argument("--min-tokens", type=int, default=16)
    query.add_argument("--max-documents", type=int, default=5)
    query.add_argument("--decode", action="store_true", help="include decoded span text")

    scan = commands.add_parser("scan", help="batch memorization report over generations")
    add_index_arguments(scan)
    scan.add_argument("--generations", type=Path, required=True, help="JSONL of tokens/text")
    scan.add_argument("--output", type=Path, help="write per-generation JSONL here")
    scan.add_argument("--thresholds", default=",".join(map(str, DEFAULT_THRESHOLDS)))
    scan.add_argument("--max-spans", type=int, default=3)
    scan.add_argument("--decode", action="store_true", help="include decoded span text")

    furniture = commands.add_parser("furniture", help="find n-grams shared across documents")
    add_index_arguments(furniture)
    furniture.add_argument("--min-tokens", type=int, default=8)
    furniture.add_argument("--min-documents", type=int, default=5)
    furniture.add_argument("--max-tokens", type=int, default=64)
    furniture.add_argument("--top", type=int, default=500)
    furniture.add_argument("--output", type=Path, help="write furniture JSONL here")
    furniture.add_argument("--lcp-cache", type=Path, help="reuse/save the capped LCP array (.npy)")
    return parser


def _open_index(args: argparse.Namespace, in_memory: bool | None = None) -> HauntingIndex:
    return HauntingIndex.load(
        args.index,
        args.stream,
        in_memory=args.in_memory if in_memory is None else in_memory,
        verify=args.verify,
    )


def _emit(record: dict, stream) -> None:
    stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    stream.flush()


def run_query(args: argparse.Namespace) -> dict:
    if (args.tokens is None) == (args.text is None):
        raise ValueError("pass exactly one of --tokens or --text")
    tokenizer = load_tokenizer(args.tokenizer) if (args.text or args.decode) else None
    if args.text is not None:
        if tokenizer is None:
            raise RuntimeError("--text needs a tokenizer; pass --tokenizer")
        query = as_token_array(tokenizer.encode(args.text, add_special_tokens=False).ids)
        stop = None if args.count is None else args.offset + args.count
        query = query[args.offset : stop]
    else:
        query = load_query_tokens(args.tokens, args.offset, args.count)
    index = _open_index(args)
    started = time.perf_counter()
    lengths, offsets = index.match_lengths(query)
    spans = maximal_spans(lengths, offsets, args.min_tokens)
    for span in spans:
        _emit(index.describe_span(query, span, tokenizer, args.max_documents), sys.stdout)
    summary = {
        "type": "summary",
        "tokens": int(query.shape[0]),
        "min_tokens": args.min_tokens,
        "spans": len(spans),
        "longest_match": int(lengths.max()) if lengths.size else 0,
        "coverage": {
            str(threshold): value
            for threshold, value in coverage_fractions(lengths, DEFAULT_THRESHOLDS).items()
        },
        "seconds": round(time.perf_counter() - started, 3),
    }
    _emit(summary, sys.stdout)
    return summary


def iter_generations(path: Path, tokenizer) -> Iterator[tuple[str, np.ndarray]]:
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream):
            if not line.strip():
                continue
            record = json.loads(line)
            identifier = str(record.get("id", number))
            if "tokens" in record:
                yield identifier, as_token_array(record["tokens"])
            elif "text" in record:
                if tokenizer is None:
                    raise RuntimeError("generation has text but no tokenizer is available")
                ids = tokenizer.encode(record["text"], add_special_tokens=False).ids
                yield identifier, as_token_array(ids)
            else:
                raise ValueError(f"generation {identifier} has neither tokens nor text")


def run_scan(args: argparse.Namespace) -> dict:
    thresholds = tuple(sorted({int(value) for value in args.thresholds.split(",")}))
    tokenizer = load_tokenizer(args.tokenizer)
    index = _open_index(args)
    started = time.perf_counter()
    sink = args.output.open("w", encoding="utf-8") if args.output else sys.stdout
    total_tokens = 0
    generations = 0
    weighted = {threshold: 0.0 for threshold in thresholds}
    quoting = {threshold: 0 for threshold in thresholds}
    longest_overall = 0
    per_document: dict[str, int] = {}
    try:
        for identifier, query in iter_generations(args.generations, tokenizer):
            report = scan_generation(
                index,
                query,
                thresholds,
                max_spans=args.max_spans,
                tokenizer=tokenizer if args.decode else None,
            )
            report = {"type": "generation", "index": generations, "id": identifier, **report}
            _emit(report, sink)
            generations += 1
            total_tokens += report["tokens"]
            longest_overall = max(longest_overall, report["longest_match"])
            for threshold in thresholds:
                weighted[threshold] += report["coverage"][str(threshold)] * report["tokens"]
                quoting[threshold] += report["longest_match"] >= threshold
            for document in report["top_documents"]:
                per_document[document["id"]] = (
                    per_document.get(document["id"], 0) + document["quoted_tokens"]
                )
    finally:
        if args.output:
            sink.close()
    documents_by_id = {entry.id: entry for entry in index.documents}
    summary = {
        "type": "summary",
        "generations": generations,
        "tokens": total_tokens,
        "thresholds": list(thresholds),
        "token_weighted_coverage": {
            str(threshold): (weighted[threshold] / total_tokens if total_tokens else 0.0)
            for threshold in thresholds
        },
        "generations_with_match_at_least": {
            str(threshold): quoting[threshold] for threshold in thresholds
        },
        "longest_match": longest_overall,
        "top_documents": [
            {**documents_by_id[identifier].as_dict(), "quoted_tokens": total}
            for identifier, total in sorted(per_document.items(), key=lambda item: -item[1])[:10]
        ],
        "seconds": round(time.perf_counter() - started, 3),
    }
    _emit(summary, sys.stdout)
    return summary


def run_furniture(args: argparse.Namespace) -> dict:
    tokenizer = load_tokenizer(args.tokenizer)
    index = _open_index(args, in_memory=True)
    started = time.perf_counter()
    lcp = None
    if args.lcp_cache and args.lcp_cache.is_file():
        lcp = np.load(args.lcp_cache, mmap_mode="r")
        if lcp.shape[0] != index.count:
            raise ValueError("--lcp-cache does not match the index length")
    if lcp is None:
        lcp = capped_lcp(index, args.max_tokens)
        if args.lcp_cache:
            np.save(args.lcp_cache, lcp)
    lcp_seconds = time.perf_counter() - started
    results = find_furniture(
        index,
        min_tokens=args.min_tokens,
        min_documents=args.min_documents,
        max_tokens=args.max_tokens,
        top=args.top,
        lcp=lcp,
        tokenizer=tokenizer,
    )
    sink = args.output.open("w", encoding="utf-8") if args.output else sys.stdout
    try:
        for record in results:
            _emit(record, sink)
    finally:
        if args.output:
            sink.close()
    summary = {
        "type": "summary",
        "min_tokens": args.min_tokens,
        "min_documents": args.min_documents,
        "max_tokens": args.max_tokens,
        "reported": len(results),
        "lcp_seconds": round(lcp_seconds, 3),
        "seconds": round(time.perf_counter() - started, 3),
        "peak_rss_bytes": peak_rss_bytes(),
    }
    _emit(summary, sys.stdout)
    return summary


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "build":
        manifest = build_index(
            args.tokens,
            args.dataset,
            args.output,
            split=args.split,
            eos_token_id=args.eos_token_id,
            check_samples=args.check_samples,
        )
        print(json.dumps(manifest, indent=2))
    elif args.command == "query":
        run_query(args)
    elif args.command == "scan":
        run_scan(args)
    elif args.command == "furniture":
        run_furniture(args)


if __name__ == "__main__":
    main()
