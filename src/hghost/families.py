"""Group corpus-v1 documents into work/edition families and audit split leakage.

The curated dataset is document-disjoint between train and validation, but two
scans, editions, parts, or excerpts of one work can sit on opposite sides of
that split.  This module builds a per-document ``family_id`` from two signals:

* **path/title**: normalised filename stems (extensions, volume/issue/part
  numbers, scan suffixes, archive boilerplate and dates stripped) grouped
  within and across directories;
* **content**: a Broder ``MOD_m`` sketch of word 5-shingles (every shingle whose
  64-bit hash has its top ``SAMPLE_BITS`` bits clear is kept), which supports
  both resemblance (Jaccard) and *containment* estimates.  Candidate pairs
  come from an inverted index over the sampled shingles, i.e. LSH with one row
  per band, at thresholds far looser than the 0.92 the dataset build used.

Evidence is combined into a confidence level per pair; ``medium`` and ``high``
edges are unioned into families, ``low`` edges are recorded as weak links.
Periodical issues that only share a series (masthead, ads) are tracked as a
``series_id`` and reported separately, because two issues of one magazine are
different works even though they leak style.

Nothing under ``artifacts/dataset`` or ``artifacts/tokenized`` is modified.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import time
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from hghost.build_dataset import _DisjointSet, canonical_words

SHINGLE_WORDS = 5
SAMPLE_BITS = 3  # keep shingles whose top 3 hash bits are zero: 1/8 of them
MAX_POSTING = 64  # a sampled shingle in more documents than this is boilerplate
MIN_SHARED_SAMPLES = 8  # pairs sharing fewer sampled shingles are not scored
MIN_SAMPLES = 16  # documents with fewer sampled shingles have no content evidence
CONTENT_THRESHOLDS = {"high": 0.70, "medium": 0.35, "low": 0.15}
CONFIDENCE_RANK = {"none": 0, "low": 1, "medium": 2, "high": 3}
REVIEW_CONTENT_THRESHOLD = 0.6  # families whose best overlap is below this are reviewed
STRATUM_MIN_SHARE = 0.01  # smaller (source, top-directory) strata pool into "other"
LEVELS = ("high", "medium", "low")

_MIX_MULTIPLIER = np.uint64(0x9E3779B97F4A7C15)
_MIX_A = np.uint64(0xBF58476D1CE4E5B9)
_MIX_B = np.uint64(0x94D049BB133111EB)

PERIODICAL_RE = re.compile(
    r"journal|newsletter|magazine|proceedings|bulletin|review|quarterly|monthly|weekly"
    r"|gazette|zine|news|chronicle|digest|studies|annals|forum|voice|times|reader"
    r"|almanac|circular|leaves|papers|report|triad|semeia|october|parabola|omega|io$",
    re.IGNORECASE,
)
ISSUE_CODE_RE = re.compile(r"^(v\d+n\d+|v\d+|n\d+|no\d+|nr\d+|vol\d+|\d+n\d+)$")
ISSUE_PHRASE_RE = re.compile(
    r"\b(?:vol|volume|no|nr|num|number|issue|heft|band|tome)\.?\s*[#]?\s*(\d+|[ivxlc]+)\b"
)
YEAR_RE = re.compile(r"^(1[5-9]|20)\d\d$")
ORDINAL_RE = re.compile(r"^\d+(st|nd|rd|th)$")
HEX_RE = re.compile(r"^[0-9a-f]{16,}$")
ROMAN_RE = re.compile(r"^[ivxlc]+$")
MONTHS = {
    "jan", "january", "feb", "february", "mar", "march", "apr", "april", "may", "jun",
    "june", "jul", "july", "aug", "august", "sep", "sept", "september", "oct", "october",
    "nov", "november", "dec", "december", "spring", "summer", "fall", "autumn", "winter",
}  # fmt: skip
NOISE_TOKENS = {
    "text", "ocr", "ia", "kz", "final", "redacted", "ebook", "scan", "scanned", "copy",
    "edition", "ed", "edn", "vol", "volume", "v", "no", "nr", "num", "number", "issue",
    "part", "pt", "pdf", "epub", "txt", "docx", "anna", "annas", "archive", "z", "zlib",
    "library", "lib", "sk", "1lib", "supp", "supplement", "rev", "revised", "reprint",
    "booklet", "complete", "full", "excerpt", "the", "a", "an", "of", "and", "in", "on",
    "de", "la", "le", "der", "die", "das", "el", "los", "las", "les", "und", "et", "zu",
    "for", "to", "with", "by", "s",
}  # fmt: skip


# --------------------------------------------------------------------------- #
# Path / title signals
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class PathSignals:
    directory: str
    basename: str
    top: str
    author: str | None
    stem: str
    numbers: tuple[str, ...]  # part/volume/issue-like numbers (not years)
    years: tuple[str, ...]
    periodical_hint: bool

    @property
    def title_words(self) -> list[str]:
        return [word for word in self.stem.split() if len(word) >= 3 and word.isalpha()]

    @property
    def distinctive(self) -> bool:
        """True when the stem is specific enough to match across directories."""
        return len(self.title_words) >= 2 and len(self.stem) >= 10


def _split_extension(filename: str) -> str:
    lowered = filename.casefold()
    for suffix in (".json.gz", ".jsonl.gz", ".tar.gz"):
        if lowered.endswith(suffix):
            return filename[: -len(suffix)]
    if "." in filename:
        stem, ext = filename.rsplit(".", 1)
        if ext.isalnum() and len(ext) <= 5:
            return stem
    return filename


def path_signals(relative_path: str) -> PathSignals:
    parts = relative_path.split("/")
    filename = parts[-1]
    dirs = parts[:-1]
    directory = "/".join(dirs)
    basename = dirs[-1] if dirs else "(root)"
    top = dirs[0] if dirs else "(root)"
    author = dirs[1] if top == "people" and len(dirs) > 1 else None
    title = _split_extension(filename)
    if (
        " -- " in title
    ):  # "Title -- Author -- Year -- Publisher -- ISBN -- md5 -- Anna's Archive"
        title = title.split(" -- ")[0]
    title = re.sub(r"\([^)]*\)|\[[^\]]*\]|\{[^}]*\}", " ", title)
    title = unicodedata.normalize("NFKC", title).casefold()
    title = title.replace("'", "").replace("\u2019", "")
    issue_codes = ["".join(match.split()) for match in ISSUE_PHRASE_RE.findall(title)]
    title = ISSUE_PHRASE_RE.sub(" ", title)
    tokens = re.findall(r"[^\W_]+", title)
    kept: list[str] = []
    numbers: list[str] = list(issue_codes)
    years: list[str] = []
    for token in tokens:
        if YEAR_RE.match(token):
            years.append(token)
            continue
        if (
            token.isdigit()
            or ISSUE_CODE_RE.match(token)
            or ORDINAL_RE.match(token)
            or ROMAN_RE.match(token)
        ):
            numbers.append(token)
            continue
        if token in NOISE_TOKENS or token in MONTHS or HEX_RE.match(token):
            continue
        kept.append(token)
    stem = " ".join(kept)
    periodical_hint = (
        top == "magazines"
        or bool(issue_codes)
        or bool(dirs and PERIODICAL_RE.search(dirs[-1]))
        or bool(PERIODICAL_RE.search(stem))
        or any(ISSUE_CODE_RE.match(number) for number in numbers)
    )
    return PathSignals(
        directory,
        basename,
        top,
        author,
        stem,
        tuple(numbers),
        tuple(years),
        periodical_hint,
    )


# --------------------------------------------------------------------------- #
# Content sketches
# --------------------------------------------------------------------------- #


class _WordHashes(dict):
    """Memoised deterministic 64-bit word hashes."""

    def __missing__(self, word: str) -> int:
        value = int.from_bytes(
            hashlib.blake2b(word.encode("utf-8"), digest_size=8).digest(), "big"
        )
        self[word] = value
        return value


def shingle_hashes(word_hashes: np.ndarray, size: int = SHINGLE_WORDS) -> np.ndarray:
    """Vectorised 64-bit hashes of every ``size``-word window."""
    count = len(word_hashes) - size + 1
    if count <= 0:
        return np.zeros(0, dtype=np.uint64)
    acc = np.zeros(count, dtype=np.uint64)
    for offset in range(size):
        acc = acc * _MIX_MULTIPLIER
        acc ^= word_hashes[offset : offset + count]
    acc ^= acc >> np.uint64(30)
    acc *= _MIX_A
    acc ^= acc >> np.uint64(27)
    acc *= _MIX_B
    acc ^= acc >> np.uint64(31)
    return acc


def sampled_shingles(
    text: str, cache: _WordHashes | None = None
) -> tuple[np.ndarray, int]:
    """Return (sorted unique sampled shingle hashes, total shingle positions)."""
    cache = _WordHashes() if cache is None else cache
    words = canonical_words(text)
    if len(words) < SHINGLE_WORDS:
        return np.zeros(0, dtype=np.uint64), 0
    hashes = np.fromiter(
        (cache[word] for word in words), dtype=np.uint64, count=len(words)
    )
    shingles = shingle_hashes(hashes)
    keep = (shingles >> np.uint64(64 - SAMPLE_BITS)) == 0
    return np.unique(shingles[keep]), len(shingles)


# --------------------------------------------------------------------------- #
# Dataset loading
# --------------------------------------------------------------------------- #


@dataclass
class Doc:
    index: int
    id: str
    source: str
    path: str
    tokens: int
    split: str
    content_sha256: str
    words: int
    signals: PathSignals
    samples: int = 0
    shingles: int = 0
    extraction: str = ""
    pages: int = 0


def iter_dataset(dataset: Path) -> Iterator[tuple[str, dict]]:
    manifest = json.loads((dataset / "manifest.json").read_text(encoding="utf-8"))
    for split, info in manifest["splits"].items():
        for shard in info["shards"]:
            with gzip.open(dataset / shard["path"], "rt", encoding="utf-8") as stream:
                for line in stream:
                    yield split, json.loads(line)


def load_record_metadata(records: Path | None) -> dict[str, dict]:
    """Extraction method and page counts, for the review queue.  Optional."""
    if records is None or not records.is_dir():
        return {}
    metadata: dict[str, dict] = {}
    for path in sorted(records.rglob("*.json.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            record = json.load(stream)
        metadata[record["document_id"]] = {
            "extraction": record.get("extraction") or "",
            "pages": int(record.get("pages") or 0),
        }
    return metadata


def load_documents(
    dataset: Path, sketch_cache: Path | None, records: Path | None
) -> tuple[list[Doc], list[np.ndarray]]:
    docs: list[Doc] = []
    sketches: list[np.ndarray] = []
    cached: dict[str, tuple[np.ndarray, int]] = {}
    if sketch_cache is not None and sketch_cache.is_file():
        with np.load(sketch_cache) as archive:
            ids = archive["ids"]
            offsets = archive["offsets"]
            hashes = archive["hashes"]
            shingle_counts = archive["shingles"]
            for position, document_id in enumerate(ids):
                cached[str(document_id)] = (
                    hashes[offsets[position] : offsets[position + 1]],
                    int(shingle_counts[position]),
                )
    cache = _WordHashes()
    for split, payload in iter_dataset(dataset):
        text = payload["text"]
        if payload["id"] in cached:
            sketch, shingles = cached[payload["id"]]
        else:
            sketch, shingles = sampled_shingles(text, cache)
        docs.append(
            Doc(
                index=len(docs),
                id=payload["id"],
                source=payload["source"],
                path=payload["path"],
                tokens=int(payload["tokens"]),
                split=split,
                content_sha256=payload["content_sha256"],
                words=len(canonical_words(text)) if payload["id"] not in cached else -1,
                signals=path_signals(payload["path"]),
                samples=len(sketch),
                shingles=shingles,
            )
        )
        sketches.append(sketch)
    if sketch_cache is not None and not sketch_cache.is_file():
        sketch_cache.parent.mkdir(parents=True, exist_ok=True)
        offsets = np.zeros(len(sketches) + 1, dtype=np.int64)
        offsets[1:] = np.cumsum([len(sketch) for sketch in sketches])
        np.savez(
            sketch_cache,
            ids=np.array([doc.id for doc in docs]),
            offsets=offsets,
            hashes=np.concatenate(sketches)
            if sketches
            else np.zeros(0, dtype=np.uint64),
            shingles=np.array([doc.shingles for doc in docs], dtype=np.int64),
        )
    for doc in docs:
        if doc.words < 0:
            doc.words = doc.shingles + SHINGLE_WORDS - 1 if doc.shingles else 0
    metadata = load_record_metadata(records)
    for doc in docs:
        extra = metadata.get(doc.id)
        if extra:
            doc.extraction = extra["extraction"]
            doc.pages = extra["pages"]
    return docs, sketches


# --------------------------------------------------------------------------- #
# Pair scoring
# --------------------------------------------------------------------------- #


@dataclass
class PairEvidence:
    left: int
    right: int
    shared: int = 0
    jaccard: float = 0.0
    containment: float = 0.0  # fraction of the smaller sketch inside the larger
    contained_doc: int | None = None  # the document that is (mostly) inside the other
    content_relation: str = "none"
    content_confidence: str = "none"
    path_relation: str = "none"
    path_confidence: str = "none"
    confidence: str = "none"

    @property
    def relation(self) -> str:
        if self.content_relation != "none" and self.path_relation != "none":
            return f"{self.path_relation}+{self.content_relation}"
        if self.content_relation != "none":
            return self.content_relation
        return self.path_relation


def candidate_pairs(
    sketches: list[np.ndarray], max_posting: int = MAX_POSTING
) -> tuple[np.ndarray, np.ndarray, np.ndarray, Counter[int]]:
    """Count sampled shingles shared by every document pair (inverted index).

    Returns (left, right, shared) arrays and a histogram of posting sizes.
    """
    lengths = np.array([len(sketch) for sketch in sketches], dtype=np.int64)
    total = int(lengths.sum())
    if total == 0:
        empty = np.zeros(0, dtype=np.int64)
        return empty, empty, empty, Counter()
    hashes = np.concatenate(sketches)
    owners = np.repeat(np.arange(len(sketches), dtype=np.int64), lengths)
    order = np.argsort(hashes, kind="stable")
    hashes = hashes[order]
    owners = owners[order]
    change = np.flatnonzero(hashes[1:] != hashes[:-1]) + 1
    starts = np.concatenate([[0], change])
    ends = np.concatenate([change, [len(hashes)]])
    run_lengths = ends - starts
    histogram = Counter(
        {int(k): int(v) for k, v in zip(*np.unique(run_lengths, return_counts=True))}
    )
    keys: list[np.ndarray] = []
    count = len(sketches)
    for size in range(2, max_posting + 1):
        run_starts = starts[run_lengths == size]
        if not len(run_starts):
            continue
        members = owners[run_starts[:, None] + np.arange(size)[None, :]]
        upper, lower = np.triu_indices(size, 1)
        left = members[:, upper].ravel()
        right = members[:, lower].ravel()
        keys.append(np.minimum(left, right) * count + np.maximum(left, right))
    if not keys:
        empty = np.zeros(0, dtype=np.int64)
        return empty, empty, empty, histogram
    unique_keys, shared = np.unique(np.concatenate(keys), return_counts=True)
    return unique_keys // count, unique_keys % count, shared.astype(np.int64), histogram


def content_level(jaccard: float, containment: float) -> str:
    score = max(jaccard, containment)
    for level in LEVELS:
        if score >= CONTENT_THRESHOLDS[level]:
            return level
    return "none"


def content_relation(jaccard: float, containment: float, level: str) -> str:
    if level == "none":
        return "none"
    if level == "high":
        return (
            "near_duplicate" if jaccard >= CONTENT_THRESHOLDS["high"] else "contained"
        )
    if level == "medium":
        return "overlapping"
    return "weak_overlap"


def score_pairs(
    docs: list[Doc], sketches: list[np.ndarray], min_shared: int = MIN_SHARED_SAMPLES
) -> tuple[dict[tuple[int, int], PairEvidence], Counter[int]]:
    left, right, shared, histogram = candidate_pairs(sketches)
    sizes = np.array([len(sketch) for sketch in sketches], dtype=np.float64)
    keep = shared >= min_shared
    left, right, shared = left[keep], right[keep], shared[keep]
    if len(left):
        sizes_left = sizes[left]
        sizes_right = sizes[right]
        jaccard = shared / (sizes_left + sizes_right - shared)
        smaller = np.minimum(sizes_left, sizes_right)
        containment = shared / smaller
    else:
        jaccard = containment = np.zeros(0)
    pairs: dict[tuple[int, int], PairEvidence] = {}
    for position in range(len(left)):
        a = int(left[position])
        b = int(right[position])
        if docs[a].samples < MIN_SAMPLES or docs[b].samples < MIN_SAMPLES:
            continue
        j = float(jaccard[position])
        c = float(containment[position])
        level = content_level(j, c)
        evidence = PairEvidence(
            a,
            b,
            shared=int(shared[position]),
            jaccard=round(j, 4),
            containment=round(c, 4),
            contained_doc=a if docs[a].samples <= docs[b].samples else b,
            content_relation=content_relation(j, c, level),
            content_confidence=level,
        )
        pairs[(a, b)] = evidence
    return pairs, histogram


# --------------------------------------------------------------------------- #
# Path grouping and evidence combination
# --------------------------------------------------------------------------- #


def path_groups(
    docs: list[Doc],
) -> tuple[dict[tuple[int, int], tuple[str, str]], dict[int, str]]:
    """Path relations per pair and a series id per document.

    Same directory, same non-empty stem:

    * periodical context -> ``series`` (tracked as ``series_id``; every
      ``magazines/<title>/`` folder is one series whatever its issues are
      called, and a same-named folder elsewhere joins it);
    * any part/volume-like number, or no numbers at all but a real title word
      (scan variants such as ``.ia`` / ``.ocr``) -> ``parts_or_editions`` (medium);
    * members differing only by years (``author-1974`` / ``author-1980``) ->
      ``year_siblings`` (low: same author, probably different papers);
    * identifier-only stems (``d4331c_<md5>``) -> unrelated.

    Different directories, same distinctive stem and same numbers ->
    ``same_title`` (low).  Numbered issues of a periodical living in two
    directories are joined as a series, not as a family.
    """
    relations: dict[tuple[int, int], tuple[str, str]] = {}
    series: dict[int, str] = {}
    by_directory: dict[tuple[str, str, str], list[Doc]] = defaultdict(list)
    by_stem: dict[str, list[Doc]] = defaultdict(list)
    for doc in docs:
        by_directory[(doc.source, doc.signals.directory, doc.signals.stem)].append(doc)
        if doc.signals.distinctive:
            by_stem[doc.signals.stem].append(doc)

    def relate(a: Doc, b: Doc, relation: str, confidence: str) -> None:
        key = (min(a.index, b.index), max(a.index, b.index))
        if key not in relations:
            relations[key] = (relation, confidence)

    for (source, _directory, stem), members in by_directory.items():
        if len(members) < 2:
            continue
        if any(member.signals.periodical_hint for member in members):
            series_id = f"series:{source}:{members[0].signals.basename}:{stem or '#'}"
            for member in members:
                series[member.index] = series_id
            continue
        if not stem:
            continue  # purely numeric filenames outside a periodical: unrelated
        has_parts = any(member.signals.numbers for member in members)
        has_years = any(member.signals.years for member in members)
        if has_parts or (not has_years and members[0].signals.title_words):
            relation, confidence = "parts_or_editions", "medium"
        elif has_years and members[0].signals.title_words:
            relation, confidence = "year_siblings", "low"
        else:
            continue
        for i, a in enumerate(members):
            for b in members[i + 1 :]:
                relate(a, b, relation, confidence)
    # The curator files periodicals as magazines/<title>/<issue>; issue names
    # inside one folder are often fused codes (thviii01, tt075, Para10) that no
    # stem rule can align, so the folder itself is the series.
    by_folder: dict[tuple[str, str], list[Doc]] = defaultdict(list)
    for doc in docs:
        parts = doc.signals.directory.split("/")
        if doc.signals.top == "magazines" and len(parts) >= 2:
            by_folder[(doc.source, parts[1])].append(doc)
    magazine_folders = {key for key, members in by_folder.items() if len(members) >= 2}
    for (source, folder), members in by_folder.items():
        if (source, folder) in magazine_folders:
            for member in members:
                series[member.index] = f"series:{source}:{folder}"
    # One periodical split over two folders with the same basename is one series.
    by_basename: dict[tuple[str, str, str], list[Doc]] = defaultdict(list)
    for doc in docs:
        if doc.signals.periodical_hint and doc.signals.stem:
            key = (doc.source, doc.signals.basename, doc.signals.stem)
            by_basename[key].append(doc)
    for (source, basename, stem), members in by_basename.items():
        if len(members) >= 2:
            series_id = (
                f"series:{source}:{basename}"
                if (source, basename) in magazine_folders
                else f"series:{source}:{basename}:{stem}"
            )
            for member in members:
                series.setdefault(member.index, series_id)
    for stem, members in by_stem.items():
        for i, a in enumerate(members):
            for b in members[i + 1 :]:
                if (a.source, a.signals.directory) == (b.source, b.signals.directory):
                    continue  # handled above
                if a.signals.periodical_hint or b.signals.periodical_hint:
                    if (a.signals.numbers, a.signals.years) != (
                        b.signals.numbers,
                        b.signals.years,
                    ):
                        continue  # different issues of one periodical
                elif a.signals.numbers != b.signals.numbers:
                    continue  # different volumes of one title
                relate(a, b, "same_title", "low")
    return relations, series


def combine_confidence(
    content: str,
    path_relation: str,
    path_confidence: str,
    same_series: bool,
    distinctive: bool = True,
) -> str:
    """Combine one pair's content and path evidence into a single confidence.

    A title match plus measurable overlap is the strongest evidence we have
    short of a near-duplicate; a surname-only stem needs more overlap.
    """
    content_rank = CONFIDENCE_RANK[content]
    if path_relation == "parts_or_editions":
        if content_rank >= CONFIDENCE_RANK["medium"]:
            return "high"
        if content_rank == CONFIDENCE_RANK["low"]:
            return "high" if distinctive else "medium"
        return path_confidence
    if path_relation in ("same_title", "year_siblings"):
        if content_rank >= CONFIDENCE_RANK["medium"]:
            return "high"
        if content_rank == CONFIDENCE_RANK["low"]:
            return "medium"
        return path_confidence
    if same_series:
        # Issues of one periodical: only strong content overlap makes a family.
        if content_rank >= CONFIDENCE_RANK["high"]:
            return "high"
        if content_rank == CONFIDENCE_RANK["medium"]:
            return "medium"
        return "low" if content_rank else "none"
    return content


def combine_evidence(
    docs: list[Doc],
    pairs: dict[tuple[int, int], PairEvidence],
    relations: dict[tuple[int, int], tuple[str, str]],
    series: dict[int, str],
) -> dict[tuple[int, int], PairEvidence]:
    combined: dict[tuple[int, int], PairEvidence] = {}
    for key in set(pairs) | set(relations):
        evidence = pairs.get(key) or PairEvidence(*key)
        path_relation, path_confidence = relations.get(key, ("none", "none"))
        same_series = series.get(key[0]) is not None and series.get(
            key[0]
        ) == series.get(key[1])
        if same_series and path_relation == "none":
            path_relation = "series"
        evidence.path_relation = path_relation
        evidence.path_confidence = path_confidence
        evidence.confidence = combine_confidence(
            evidence.content_confidence,
            path_relation,
            path_confidence,
            same_series,
            docs[key[0]].signals.distinctive and docs[key[1]].signals.distinctive,
        )
        if evidence.confidence != "none" or same_series:
            combined[key] = evidence
    return combined


# --------------------------------------------------------------------------- #
# Families
# --------------------------------------------------------------------------- #


@dataclass
class Family:
    id: str
    members: list[int]
    tokens: int
    confidence: str
    methods: list[str]
    edges: list[PairEvidence] = field(default_factory=list)


def family_id_for(document_ids: list[str]) -> str:
    digest = hashlib.sha256("\n".join(sorted(document_ids)).encode("utf-8")).hexdigest()
    return f"fam-{digest[:12]}"


def build_families(
    docs: list[Doc], evidence: dict[tuple[int, int], PairEvidence]
) -> tuple[list[Family], dict[int, Family]]:
    groups = _DisjointSet(len(docs))
    for (a, b), pair in evidence.items():
        if CONFIDENCE_RANK[pair.confidence] >= CONFIDENCE_RANK["medium"]:
            groups.union(a, b)
    members_by_root: dict[int, list[int]] = defaultdict(list)
    for doc in docs:
        members_by_root[groups.find(doc.index)].append(doc.index)
    edges_by_root: dict[int, list[PairEvidence]] = defaultdict(list)
    for (a, b), pair in evidence.items():
        if groups.find(a) == groups.find(b):
            edges_by_root[groups.find(a)].append(pair)
    families: list[Family] = []
    by_doc: dict[int, Family] = {}
    for root, members in members_by_root.items():
        edges = [
            edge
            for edge in edges_by_root[root]
            if CONFIDENCE_RANK[edge.confidence] >= CONFIDENCE_RANK["medium"]
        ]
        methods = sorted(
            {
                "content" if edge.content_relation != "none" else "path"
                for edge in edges
                if edge.confidence != "none"
            }
        )
        if len(members) == 1:
            confidence = "none"
            methods = ["singleton"]
        else:
            confidence = min(
                (edge.confidence for edge in edges),
                key=lambda level: CONFIDENCE_RANK[level],
            )
        family = Family(
            id=family_id_for([docs[index].id for index in members]),
            members=sorted(members),
            tokens=sum(docs[index].tokens for index in members),
            confidence=confidence,
            methods=methods,
            edges=sorted(
                edges, key=lambda edge: (-CONFIDENCE_RANK[edge.confidence], edge.left)
            ),
        )
        families.append(family)
        for index in members:
            by_doc[index] = family
    families.sort(key=lambda family: (-family.tokens, family.id))
    return families, by_doc


def document_confidence(doc: Doc, family: Family) -> tuple[str, str]:
    """(method, confidence) of the strongest edge attaching ``doc`` to its family."""
    if len(family.members) == 1:
        return "singleton", "none"
    best: PairEvidence | None = None
    for edge in family.edges:
        if doc.index not in (edge.left, edge.right):
            continue
        if (
            best is None
            or CONFIDENCE_RANK[edge.confidence] > CONFIDENCE_RANK[best.confidence]
        ):
            best = edge
    if best is None:
        return "transitive", family.confidence
    method = (
        "content+path"
        if best.content_relation != "none"
        and best.path_relation
        not in (
            "none",
            "series",
        )
        else ("content" if best.content_relation != "none" else "path")
    )
    return method, best.confidence


# --------------------------------------------------------------------------- #
# Reports
# --------------------------------------------------------------------------- #


def _doc_ref(doc: Doc) -> dict:
    return {
        "id": doc.id,
        "source": doc.source,
        "path": doc.path,
        "tokens": doc.tokens,
        "split": doc.split,
    }


def _edge_json(
    docs: list[Doc], edge: PairEvidence, viewpoint: int | None = None
) -> dict:
    other = edge.right if viewpoint == edge.left else edge.left
    payload = {
        "relation": edge.relation,
        "confidence": edge.confidence,
        "content_confidence": edge.content_confidence,
        "path_relation": edge.path_relation,
        "shared_samples": edge.shared,
        "jaccard": edge.jaccard,
        "containment": edge.containment,
    }
    if viewpoint is None:
        payload["left"] = _doc_ref(docs[edge.left])
        payload["right"] = _doc_ref(docs[edge.right])
    else:
        payload["other"] = _doc_ref(docs[other])
        if edge.contained_doc is not None:
            payload["contained"] = (
                "self" if edge.contained_doc == viewpoint else "other"
            )
    return payload


def leakage_report(
    docs: list[Doc],
    families: dict[int, Family],
    evidence: dict[tuple[int, int], PairEvidence],
    series: dict[int, str],
    all_pairs: dict[tuple[int, int], PairEvidence] | None = None,
) -> dict:
    by_doc_edges: dict[int, list[PairEvidence]] = defaultdict(list)
    for (a, b), pair in evidence.items():
        by_doc_edges[a].append(pair)
        by_doc_edges[b].append(pair)
    best_neighbor: dict[int, PairEvidence] = {}
    for (a, b), pair in (all_pairs or {}).items():
        for me, other in ((a, b), (b, a)):
            if docs[me].split == "validation" and docs[other].split == "train":
                current = best_neighbor.get(me)
                if current is None or max(pair.jaccard, pair.containment) > max(
                    current.jaccard, current.containment
                ):
                    best_neighbor[me] = pair
    series_members: dict[str, list[int]] = defaultdict(list)
    for index, series_id in series.items():
        series_members[series_id].append(index)
    validation = [doc for doc in docs if doc.split == "validation"]
    total_tokens = sum(doc.tokens for doc in validation)
    entries = []
    level_counts: Counter[str] = Counter()
    level_tokens: Counter[str] = Counter()
    for doc in validation:
        family = families[doc.index]
        train_family = [
            index for index in family.members if docs[index].split == "train"
        ]
        train_edges = [
            edge
            for edge in by_doc_edges[doc.index]
            if docs[edge.left if edge.right == doc.index else edge.right].split
            == "train"
            and edge.confidence != "none"
        ]
        train_edges.sort(
            key=lambda edge: (
                -CONFIDENCE_RANK[edge.confidence],
                -max(edge.jaccard, edge.containment),
            )
        )
        best = train_edges[0].confidence if train_edges else "none"
        series_id = series.get(doc.index)
        series_train = [
            index
            for index in series_members.get(series_id, [])
            if docs[index].split == "train" and index != doc.index
        ]
        if best == "none":
            level = "series_only" if series_train else "clean"
        else:
            level = best
        level_counts[level] += 1
        level_tokens[level] += doc.tokens
        entries.append(
            {
                **_doc_ref(doc),
                "family_id": family.id,
                "family_size": len(family.members),
                "family_tokens": family.tokens,
                "leakage_level": level,
                "train_family_members": [
                    _doc_ref(docs[index]) for index in train_family
                ],
                "train_edges": [
                    _edge_json(docs, edge, doc.index) for edge in train_edges[:12]
                ],
                "train_edge_count": len(train_edges),
                "series_id": series_id,
                "series_train_siblings": len(series_train),
                "best_train_neighbor": (
                    _edge_json(docs, best_neighbor[doc.index], doc.index)
                    if doc.index in best_neighbor
                    else None
                ),
            }
        )
    summary = {
        "validation_documents": len(validation),
        "validation_tokens": total_tokens,
        "by_level": {
            level: {
                "documents": level_counts[level],
                "tokens": level_tokens[level],
                "token_fraction": round(level_tokens[level] / total_tokens, 4)
                if total_tokens
                else 0,
            }
            for level in ("high", "medium", "low", "series_only", "clean")
        },
    }
    cumulative = 0
    cumulative_docs = 0
    for level in ("high", "medium", "low", "series_only"):
        cumulative += level_tokens[level]
        cumulative_docs += level_counts[level]
        summary["by_level"][level]["cumulative_documents"] = cumulative_docs
        summary["by_level"][level]["cumulative_token_fraction"] = (
            round(cumulative / total_tokens, 4) if total_tokens else 0
        )
    return {"summary": summary, "documents": entries}


def largest_families(
    docs: list[Doc], families: list[Family], limit: int = 40
) -> list[dict]:
    rows = []
    for family in families[:limit]:
        rows.append(
            {
                "family_id": family.id,
                "tokens": family.tokens,
                "size": len(family.members),
                "confidence": family.confidence,
                "methods": family.methods,
                "splits": dict(Counter(docs[index].split for index in family.members)),
                "members": [_doc_ref(docs[index]) for index in family.members],
                "edges": [_edge_json(docs, edge) for edge in family.edges[:8]],
            }
        )
    return rows


def review_queue(
    docs: list[Doc],
    families: list[Family],
    evidence: dict[tuple[int, int], PairEvidence],
    series: dict[int, str],
    min_tokens: int = 100_000,
) -> list[dict]:
    """Ambiguous, high-token families and validation-touching weak links."""
    queue: list[dict] = []
    for family in families:
        if len(family.members) < 2 or family.tokens < min_tokens:
            continue
        strongest = max(CONFIDENCE_RANK[edge.confidence] for edge in family.edges)
        path_only = all(edge.content_relation == "none" for edge in family.edges)
        weak_content = all(
            max(edge.jaccard, edge.containment) < REVIEW_CONTENT_THRESHOLD
            for edge in family.edges
        )
        reasons = []
        if path_only:
            reasons.append("path_only_family")
        elif weak_content:
            reasons.append("borderline_content_overlap")
        if strongest < CONFIDENCE_RANK["high"]:
            reasons.append("no_high_confidence_edge")
        if len(family.members) >= 6:
            reasons.append("large_family_check_for_overmerge")
        if not reasons:
            continue
        queue.append(
            {
                "kind": "family",
                "family_id": family.id,
                "tokens": family.tokens,
                "size": len(family.members),
                "confidence": family.confidence,
                "reasons": reasons,
                "question": "Are these the same work (edition/scan/part/excerpt) or merely related titles?",
                "members": [
                    {
                        **_doc_ref(docs[index]),
                        "extraction": docs[index].extraction,
                        "pages": docs[index].pages,
                    }
                    for index in family.members
                ],
                "edges": [_edge_json(docs, edge) for edge in family.edges[:10]],
            }
        )
    for (a, b), pair in evidence.items():
        if pair.confidence != "low":
            continue
        if {docs[a].split, docs[b].split} != {"train", "validation"}:
            continue
        if docs[a].tokens + docs[b].tokens < min_tokens // 4:
            continue
        queue.append(
            {
                "kind": "validation_weak_link",
                "tokens": docs[a].tokens + docs[b].tokens,
                "confidence": pair.confidence,
                "reasons": ["weak_link_across_split"],
                "question": "Is this overlap shared boilerplate (masthead, ads, front matter) or the same work?",
                "members": [_doc_ref(docs[a]), _doc_ref(docs[b])],
                "edges": [_edge_json(docs, pair)],
            }
        )
    queue.sort(key=lambda item: -item["tokens"])
    return queue


# --------------------------------------------------------------------------- #
# Proposed split
# --------------------------------------------------------------------------- #


def _split_hash(content_sha256: str, salt: str) -> int:
    return int(
        hashlib.blake2b(
            f"{salt}\0{content_sha256}".encode(), digest_size=8
        ).hexdigest(),
        16,
    )


def propose_split(
    docs: list[Doc],
    families: dict[int, Family],
    evidence: dict[tuple[int, int], PairEvidence],
    series: dict[int, str],
    review_ids: set[str],
    target_tokens: int,
    min_tokens: int,
    max_tokens: int,
) -> dict:
    """Pick family-, series- and weak-link-free documents for validation and test."""
    linked: set[int] = set()
    for (a, b), pair in evidence.items():
        if pair.confidence != "none":
            linked.update((a, b))
    series_sizes = Counter(series.values())
    eligible: list[Doc] = []
    ineligible: Counter[str] = Counter()
    for doc in docs:
        family = families[doc.index]
        if len(family.members) > 1:
            ineligible["in_multi_document_family"] += 1
        elif doc.index in linked:
            ineligible["weak_link_or_series_overlap"] += 1
        elif series.get(doc.index) and series_sizes[series[doc.index]] > 1:
            ineligible["periodical_series_sibling"] += 1
        elif doc.id in review_ids:
            ineligible["in_review_queue"] += 1
        elif doc.samples < MIN_SAMPLES:
            ineligible["too_short_for_content_evidence"] += 1
        elif not min_tokens <= doc.tokens <= max_tokens:
            ineligible["outside_token_range"] += 1
        else:
            eligible.append(doc)
    corpus_tokens = sum(doc.tokens for doc in docs)
    top_tokens: Counter[tuple[str, str]] = Counter()
    for doc in docs:
        top_tokens[(doc.source, doc.signals.top)] += doc.tokens

    def stratum_of(doc: Doc) -> tuple[str, str]:
        key = (doc.source, doc.signals.top)
        if top_tokens[key] >= STRATUM_MIN_SHARE * corpus_tokens:
            return key
        return (doc.source, "other")

    stratum_tokens: Counter[tuple[str, str]] = Counter()
    for doc in docs:
        stratum_tokens[stratum_of(doc)] += doc.tokens
    targets = {
        stratum: target_tokens * tokens / corpus_tokens
        for stratum, tokens in stratum_tokens.items()
    }
    slack = max(max_tokens // 4, 1)
    chosen: dict[str, list[Doc]] = {"validation": [], "test": []}
    filled: dict[str, Counter[tuple[str, str]]] = {
        "validation": Counter(),
        "test": Counter(),
    }
    # Clean documents that are already held out stay in validation, so the
    # proposed set remains comparable with checkpoints evaluated on corpus-v1.
    taken: set[int] = set()
    for doc in eligible:
        if doc.split == "validation":
            chosen["validation"].append(doc)
            filled["validation"][stratum_of(doc)] += doc.tokens
            taken.add(doc.index)
    ordered = sorted(
        (doc for doc in eligible if doc.index not in taken),
        key=lambda doc: _split_hash(doc.content_sha256, "families-v1"),
    )
    for doc in ordered:
        stratum = stratum_of(doc)
        for name in ("validation", "test"):
            if filled[name][stratum] + doc.tokens <= targets[stratum] + slack:
                chosen[name].append(doc)
                filled[name][stratum] += doc.tokens
                taken.add(doc.index)
                break
    # Second pass: top up to the total budget from whatever is left.
    for name in ("validation", "test"):
        remaining = target_tokens - sum(doc.tokens for doc in chosen[name])
        for doc in ordered:
            if remaining <= 0:
                break
            if doc.index in taken or doc.tokens > remaining + slack:
                continue
            chosen[name].append(doc)
            taken.add(doc.index)
            remaining -= doc.tokens

    def summarize(selected: list[Doc]) -> dict:
        by_stratum: dict[str, dict] = {}
        for doc in selected:
            key = "/".join(stratum_of(doc))
            entry = by_stratum.setdefault(key, {"documents": 0, "tokens": 0})
            entry["documents"] += 1
            entry["tokens"] += doc.tokens
        return {
            "documents": len(selected),
            "tokens": sum(doc.tokens for doc in selected),
            "by_source": dict(Counter(doc.source for doc in selected)),
            "kept_from_current_validation": sum(
                doc.split == "validation" for doc in selected
            ),
            "by_stratum": dict(
                sorted(by_stratum.items(), key=lambda kv: -kv[1]["tokens"])
            ),
        }

    return {
        "target_tokens": target_tokens,
        "document_token_range": [min_tokens, max_tokens],
        "eligible_documents": len(eligible),
        "eligible_tokens": sum(doc.tokens for doc in eligible),
        "ineligible_reasons": dict(ineligible),
        "strata": {
            "/".join(stratum): {
                "corpus_tokens": tokens,
                "target_tokens": round(targets[stratum]),
            }
            for stratum, tokens in sorted(stratum_tokens.items(), key=lambda kv: -kv[1])
        },
        "validation": chosen["validation"],
        "test": chosen["test"],
        "validation_summary": summarize(chosen["validation"]),
        "test_summary": summarize(chosen["test"]),
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inventory work/edition families in the curated dataset and audit split leakage."
    )
    parser.add_argument("--dataset", type=Path, default=Path("artifacts/dataset"))
    parser.add_argument(
        "--records", type=Path, default=Path("artifacts/extracted/records")
    )
    parser.add_argument("--output", type=Path, default=Path("artifacts/families"))
    parser.add_argument(
        "--sketch-cache",
        type=Path,
        default=None,
        help="npz of sampled shingles; defaults to <output>/sketches.npz",
    )
    parser.add_argument("--target-tokens", type=int, default=2_500_000)
    parser.add_argument("--min-doc-tokens", type=int, default=2_000)
    parser.add_argument("--max-doc-tokens", type=int, default=150_000)
    parser.add_argument("--largest", type=int, default=40)
    return parser


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def run(args: argparse.Namespace) -> dict:
    started = time.time()
    dataset = args.dataset.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    sketch_cache = args.sketch_cache or output / "sketches.npz"
    records = args.records.expanduser().resolve() if args.records else None

    docs, sketches = load_documents(dataset, sketch_cache, records)
    loaded = time.time()
    pairs, histogram = score_pairs(docs, sketches)
    relations, series = path_groups(docs)
    evidence = combine_evidence(docs, pairs, relations, series)
    families, by_doc = build_families(docs, evidence)
    report = leakage_report(docs, by_doc, evidence, series, pairs)
    largest = largest_families(docs, families, args.largest)
    queue = review_queue(docs, families, evidence, series)
    review_ids = {member["id"] for item in queue for member in item["members"]}
    proposal = propose_split(
        docs,
        by_doc,
        evidence,
        series,
        review_ids,
        args.target_tokens,
        args.min_doc_tokens,
        args.max_doc_tokens,
    )

    rows = []
    for doc in docs:
        family = by_doc[doc.index]
        method, confidence = document_confidence(doc, family)
        weak = [
            pair
            for (a, b), pair in evidence.items()
            if doc.index in (a, b) and pair.confidence == "low"
        ]
        rows.append(
            {
                "id": doc.id,
                "source": doc.source,
                "path": doc.path,
                "tokens": doc.tokens,
                "split": doc.split,
                "family_id": family.id,
                "family_size": len(family.members),
                "family_tokens": family.tokens,
                "method": method,
                "confidence": confidence,
                "title_stem": doc.signals.stem,
                "series_id": series.get(doc.index),
                "weak_links": len(weak),
                "sampled_shingles": doc.samples,
            }
        )
    _write_jsonl(output / "families.jsonl", rows)
    _write_jsonl(
        output / "pairs.jsonl",
        [_edge_json(docs, pair) for _, pair in sorted(evidence.items())],
    )
    (output / "leakage-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    _write_jsonl(output / "largest-families.jsonl", largest)
    _write_jsonl(output / "review-queue.jsonl", queue)
    for name in ("validation", "test"):
        _write_jsonl(
            output / f"proposed-{name}.jsonl",
            [
                {
                    **_doc_ref(doc),
                    "content_sha256": doc.content_sha256,
                    "family_id": by_doc[doc.index].id,
                    "stratum": f"{doc.source}/{doc.signals.top}",
                    "current_split": doc.split,
                }
                for doc in proposal[name]
            ],
        )
    multi = [family for family in families if len(family.members) > 1]
    summary = {
        "documents": len(docs),
        "tokens": sum(doc.tokens for doc in docs),
        "families": len(families),
        "multi_document_families": len(multi),
        "documents_in_multi_document_families": sum(
            len(family.members) for family in multi
        ),
        "tokens_in_multi_document_families": sum(family.tokens for family in multi),
        "families_by_confidence": dict(Counter(family.confidence for family in multi)),
        "families_by_method": dict(
            Counter("+".join(family.methods) for family in multi)
        ),
        "pairs_by_confidence": dict(
            Counter(pair.confidence for pair in evidence.values())
        ),
        "pairs_by_relation": dict(Counter(pair.relation for pair in evidence.values())),
        "path_stem_groups": {
            "parts_or_editions_pairs": sum(
                r == "parts_or_editions" for r, _ in relations.values()
            ),
            "same_title_pairs": sum(r == "same_title" for r, _ in relations.values()),
            "series": len(set(series.values())),
            "documents_in_series": len(series),
        },
        "posting_size_histogram": {
            str(k): v for k, v in sorted(histogram.items())[:12]
        },
        "settings": {
            "shingle_words": SHINGLE_WORDS,
            "sample_fraction": 1 / 2**SAMPLE_BITS,
            "max_posting": MAX_POSTING,
            "min_shared_samples": MIN_SHARED_SAMPLES,
            "min_samples": MIN_SAMPLES,
            "content_thresholds": CONTENT_THRESHOLDS,
        },
        "leakage": report["summary"],
        "proposed_split": {
            key: value
            for key, value in proposal.items()
            if key not in ("validation", "test")
        },
        "runtime_seconds": {
            "load_and_sketch": round(loaded - started, 1),
            "analysis": round(time.time() - loaded, 1),
            "total": round(time.time() - started, 1),
        },
    }
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    summary = run(build_parser().parse_args())
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
