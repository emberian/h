"""Corpus-v2 admission: OCR *fidelity* (does the text match the page) apart from *library value*.

Nothing here writes under ``artifacts/dataset``, ``artifacts/extracted`` or any other sealed
tree; outputs go to ``artifacts/corpus-v2/``. The spec is ``research/corpus-v2-admission.md``.

Commands (``hghost-admission``):

* ``pdfinfo``      cache Producer/Creator/page geometry per source PDF (text-layer origin prior)
* ``score``        per-document fidelity/value scores and signals -> ``scores.jsonl`` + summary
* ``gold sample``  stratified ~300-page gold set with unit-test style checks + review sheet
* ``gold check``   run the checks against the current extraction (raw and reading view)
* ``manifest``     proposed v2 manifest: main / specialist / quarantine / drop + family-clean splits
* ``reading-view`` print one document's reading view and its transform log
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
import random
import re
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from .privacy import credential_dump_indicator_count, credential_indicator_count

SCHEMA_VERSION = 1
FORM_FEED = "\f"
DEFAULT_DICTIONARY = Path("/usr/share/dict/words")
DEFAULT_ROOTS = {
    "cathedral": Path("~/PARAHEPTARCH/interface.cathedral.bucket").expanduser(),
    "rat_palace": Path("~/archive/rat-palace").expanduser(),
}

_ALPHA_WORD = re.compile(r"[^\W\d_]+")
_TOKEN = re.compile(r"\S+")
_SPACES = re.compile(r"\s+")
_DIGITS = re.compile(r"\d+")
_INNER_CAPS = re.compile(r"[a-z][A-Z]")
_INNER_CAPS_WORD = re.compile(r"(?<![^\W\d_])(?=[^\W\d_]{4})[^\W\d_]*?[a-z][A-Z][^\W\d_]*")
_GUTTER = re.compile(r"(?<![^\W\d_])[^\W\d_]{2,}+[ \t]{3,}+[^\W\d_]{2,}")
_MIXED_CORE = re.compile(r"(?:[^\W\d_]++|\d++|[^\w\s]++){3,}")
_STRIP_PUNCT = ".,;:!?()[]{}\"'«»“”‘’-—–"
_JOINERS = str.maketrans("", "", "-'’.·/")
_DOT_LEADER = re.compile(r"(?:\.[ \t]*){5,}")
_DOT_LEADER_RUN = re.compile(r"[ \t]*(?:\.[ \t]+){4,}\.?[ \t]*")
_DASH_RULE = re.compile(r"^[\s\-_=~.*]{8,}$")
_NUMERIC_TOKEN = re.compile(r"^[\d.,;:/%$€£()\-+]+$")
_PAGE_NUMBER = re.compile(r"^\s*(?:[\-–—]?\s*)?(?:\d{1,4}|[ivxlcdm]{1,7}|[IVXLCDM]{1,7})(?:\s*[\-–—])?\s*$")
_SPACED_LETTERS = re.compile(r"(?<![^\W\d_])(?:[^\W\d_] ){3,}[^\W\d_](?![^\W\d_])")
_YEAR = re.compile(r"(?<!\d)(1[5-9]\d\d|20[0-2]\d)(?!\d)")
_TABLE_FIELD = re.compile(r"(?<!\S)[\d][\d.,]*%?(?!\S)")

# Furniture families seen in the haunting index (research/results/haunting-index.md). A line
# matching any of these is page furniture, whatever document it sits in.
FURNITURE_PATTERNS: dict[str, re.Pattern[str]] = {
    "jstor_download": re.compile(r"This content downloaded from", re.IGNORECASE),
    "jstor_ip_timestamp": re.compile(r"^\s*\d{1,3}(?:\.\d{1,3}){3} on \w{3}, \d\d \w{3} \d{4} \d\d:\d\d:\d\d UTC", re.IGNORECASE),
    "jstor_terms": re.compile(r"All use subject to https?://about\.jstor\.org/terms", re.IGNORECASE),
    "jstor_stable": re.compile(r"Stable URL:\s*https?://www\.jstor\.org/stable/", re.IGNORECASE),
    "jstor_service": re.compile(r"JSTOR is a not-for-profit service that helps scholars", re.IGNORECASE),
    "jstor_use": re.compile(r"Your use of the JSTOR archive indicates your acceptance", re.IGNORECASE),
    "jstor_contact": re.compile(r"For more information about JSTOR, please contact", re.IGNORECASE),
    "jstor_open": re.compile(r"openly available as part of an Open JSTOR Collection", re.IGNORECASE),
    "jstor_licenses": re.compile(r"^\s*Licenses?:\s*Creative Commons", re.IGNORECASE),
    "reveal_digital": re.compile(r"Reveal Digital (?:is collaborating with JSTOR|, \d\d-\d\d-\d{4})", re.IGNORECASE),
    "reveal_source": re.compile(r"^\s*Source:\s*Reveal Digital", re.IGNORECASE),
    "ia_digitized": re.compile(r"Digitized by the Internet Archive", re.IGNORECASE),
    "ia_funding": re.compile(r"^\s*(?:in \d{4} )?with funding from\s*$", re.IGNORECASE),
    "ia_kahle": re.compile(r"Kahle/Austin Foundation", re.IGNORECASE),
    "ia_details": re.compile(r"^\s*https?://archive\.org/details/\S+\s*$", re.IGNORECASE),
    "google_digitized": re.compile(r"Digitized by\s+Google", re.IGNORECASE),
    "google_notice": re.compile(r"This is a digital copy of a book that was preserved for generations", re.IGNORECASE),
    "saturnian_mirror": re.compile(r"mirrored file at https?://SaturnianCosmology\.Org", re.IGNORECASE),
    "saturnian_access": re.compile(r"For complete access to all the files of this collection", re.IGNORECASE),
    "saturnian_search": re.compile(r"see https?://SaturnianCosmology\.org/search\.php", re.IGNORECASE),
    "benjamins_reproduce": re.compile(r"No part of this book may be reproduced in any form, by print, photoprint", re.IGNORECASE),
    "kronia_visit": re.compile(r"PLEASE VISIT THE KRONIA COMMUNICATIONS WEBSITE", re.IGNORECASE),
    "kronia_links": re.compile(r"^\s*https?://www\.(?:flash\.net/~cjransom|knowledge\.co\.uk/sis|grazian-archive\.com|bearfabrique\.org)\S*\s*$", re.IGNORECASE),
    "kronia_other": re.compile(r"Other suggested Web site URL's for more information about", re.IGNORECASE),
    "equals_rule": re.compile(r"^\s*={12,}\s*$"),
}
# Cheap prefilter: a line can only match a furniture pattern if it contains one of these.
_FURNITURE_HINT = re.compile(
    r"jstor|content downloaded from|all use subject to|stable url|reveal digital|archive\.org|"
    r"^\s*\d{1,3}(?:\.\d{1,3}){3} on |"
    r"digitized by|with funding from|kahle|saturniancosmology|no part of this book|kronia|"
    r"other suggested web|for complete access|preserved for generations|licenses?:|^\s*source:|"
    r"^\s*={12,}\s*$|flash\.net|knowledge\.co\.uk|grazian-archive|bearfabrique",
    re.IGNORECASE,
)

STOPWORDS: dict[str, tuple[str, ...]] = {
    "en": ("the", "and", "of", "to", "in", "that", "is", "was", "for", "with", "as", "it", "his", "on", "be", "at", "by", "this", "which", "from", "or", "have", "not", "are", "but"),
    "de": ("der", "die", "und", "das", "ist", "nicht", "ein", "eine", "mit", "sich", "auf", "den", "von", "dem", "des", "zu", "ich", "wird", "auch", "als", "sie", "dass", "daß", "oder", "wie"),
    "fr": ("le", "la", "les", "des", "une", "est", "dans", "que", "qui", "pas", "pour", "sur", "avec", "sont", "cette", "mais", "nous", "vous", "ont", "aux", "ses", "leur", "était", "être", "plus"),
    "es": ("el", "los", "las", "una", "por", "con", "para", "como", "del", "más", "pero", "sus", "este", "esta", "entre", "también", "muy", "hay", "ser", "son", "fue", "había", "sobre", "todo", "cuando"),
    "it": ("il", "della", "che", "per", "con", "sono", "una", "del", "alla", "nel", "anche", "come", "più", "questo", "essere", "dei", "delle", "gli", "hanno", "nella", "ma", "non", "sua", "quella", "questa"),
    "la": ("et", "in", "est", "non", "ad", "cum", "quod", "sed", "ut", "qui", "quae", "sunt", "esse", "enim", "autem", "atque", "etiam", "per", "ex", "hoc", "nec", "quam", "vel", "sicut", "omnia"),
    "pl": ("nie", "się", "jest", "jak", "ale", "tak", "jego", "przez", "tego", "tym", "może", "tylko", "oraz", "były", "jednak", "także", "który", "która", "które", "bardzo", "ich", "dla", "czy", "już", "nad"),
    "hu": ("és", "hogy", "nem", "egy", "az", "is", "van", "volt", "mint", "meg", "csak", "már", "ez", "vagy", "még", "ki", "azt", "mert", "minden", "ezt", "lehet", "el", "ha", "aki", "után"),
    "nl": ("het", "een", "van", "dat", "niet", "zijn", "met", "voor", "ook", "maar", "aan", "door", "naar", "hij", "wordt", "worden", "deze", "nog", "over", "bij", "meer", "dan", "zij", "geen", "veel"),
    "pt": ("não", "uma", "com", "para", "por", "mais", "como", "mas", "seu", "sua", "foi", "são", "isso", "está", "também", "muito", "quando", "ele", "ela", "nos", "dos", "das", "pelo", "pela", "ser"),
}
_STOPWORD_INDEX: dict[str, set[str]] = {}
for _lang, _words in STOPWORDS.items():
    for _word in _words:
        _STOPWORD_INDEX.setdefault(_word, set()).add(_lang)

# Falcon-H1 tokens per whitespace word expected for clean text in each language; the excess
# over this is the fragmentation signal (tokenizer_fragmentation in quality.py, made language-aware).
# Corpus medians per guessed language (corpus-v1, 2026-09-02): older prose with rare vocabulary
# and page-broken lines tokenizes well above web English's ~1.35.
EXPECTED_TOKENS_PER_WORD: dict[str, float] = {
    "en": 1.7, "de": 2.9, "fr": 2.4, "es": 2.5, "it": 2.7, "la": 3.0, "pl": 4.0, "hu": 3.9,
    "nl": 2.5, "pt": 2.6, "ru": 3.5, "el": 4.0, "ja": 3.0, "zh": 3.0, "ar": 4.0, "he": 4.0, "unknown": 3.0,
}
NON_LATIN_TOKENS_PER_WORD = 3.0  # added per unit of non-Latin letter share (Arabic, Hebrew, CJK...)

# Character-level noise is implausible in a born-digital text layer (its failures are layout and
# font-encoding); the character terms are down-weighted there, the layout terms are not.
ORIGIN_NOISE_WEIGHT: dict[str, float] = {
    "born_digital": 0.5, "ocr_layer": 1.0, "ia_ocr_sidecar": 1.0, "paddleocr_vl": 1.0, "unknown": 1.0,
}
CHARACTER_SIGNALS = {"hapax_ratio", "unknown_ratio", "inner_caps_ratio", "mixed_token_ratio", "replacement_ratio", "dictionary_miss"}

# Curatorial tiers (a proposal; see the spec). Matched in order, first hit wins.
DEFAULT_TIERS: list[dict] = [
    {"pattern": r"thegame23/", "tier": "C", "why": "pastebin dumps"},
    {"pattern": r"gov\.uscourts", "tier": "C", "why": "court docket"},
    {"pattern": r"(?i)foia|_redacted", "tier": "C", "why": "FOIA release"},
    {"pattern": r"people/steen/Epstein files", "tier": "C", "why": "document dump"},
    {"pattern": r"^rat_palace/(milshit|technology|tech)/", "tier": "B", "why": "manuals and military documents"},
    {"pattern": r"^cathedral/", "tier": "B", "why": "collection mirror"},
    {"pattern": r"^rat_palace/", "tier": "A", "why": "the library"},
]
TIER_PRIOR = {"A": 0.85, "B": 0.62, "C": 0.25}

# Piecewise-linear ramps mapping a raw signal to a badness in [0, 1]: 0 at or below ``lo``, 1 at
# or above ``hi``. ``weight`` is the severity in the noisy-OR. Calibrated on corpus-v1 (spec §3).
FIDELITY_RAMPS: dict[str, tuple[float, float, float]] = {
    # signal: (lo, hi, weight); lo sits near the corpus p90-p95, hi near p99 (spec §10)
    "hapax_ratio": (0.08, 0.30, 0.9),
    "unknown_ratio": (0.15, 0.50, 0.6),
    "inner_caps_ratio": (0.01, 0.06, 0.8),
    "mixed_token_ratio": (0.03, 0.12, 0.7),
    "single_char_line_ratio": (0.08, 0.30, 0.5),
    "spaced_letter_ratio": (0.01, 0.08, 0.6),
    "replacement_ratio": (0.0005, 0.02, 0.7),
    "non_alpha_excess": (0.34, 0.55, 0.6),
    "fragmentation_excess": (0.5, 1.5, 0.5),
    "dictionary_miss": (0.30, 0.60, 0.5),
}
LAYOUT_RAMPS: dict[str, tuple[float, float, float]] = {
    "gutter_line_ratio": (0.03, 0.25, 0.8),
    "single_char_line_max_run": (4, 20, 0.5),
    "running_head_page_ratio": (0.3, 0.9, 0.3),
    "furniture_hits_per_10k": (2, 20, 0.4),
    "dot_leader_lines_per_10k": (5, 40, 0.3),
}
VALUE_ADJUSTMENTS = {
    "rare_valid_ratio": (0.04, 0.16, +0.12),
    "numeric_ratio": (0.15, 0.40, -0.25),
    "repeated_line_ratio": (0.10, 0.40, -0.30),
    "low_vocabulary": (0.0, 1.0, -0.25),
    "credential_dump": (0.0, 1.0, -0.60),
}
FIDELITY_THRESHOLD = 0.60
VALUE_THRESHOLD = 0.50


# --------------------------------------------------------------------------- helpers


def ramp(value: float, lo: float, hi: float) -> float:
    if hi <= lo:
        raise ValueError("ramp needs lo < hi")
    if value <= lo:
        return 0.0
    if value >= hi:
        return 1.0
    return (value - lo) / (hi - lo)


def noisy_or(badness: Iterable[tuple[float, float]]) -> float:
    """1 - prod(1 - w*b): any single strong signal is enough to flag a document."""
    survival = 1.0
    for value, weight in badness:
        survival *= 1.0 - max(0.0, min(1.0, value)) * weight
    return 1.0 - survival


def normalize_line(line: str) -> str:
    line = unicodedata.normalize("NFKC", line).casefold()
    line = _DIGITS.sub("#", line)
    return _SPACES.sub(" ", line).strip()


def normalize_phrase(text: str) -> str:
    return _SPACES.sub(" ", unicodedata.normalize("NFKC", text).casefold()).strip()


def guess_year(path: str) -> int | None:
    """Most plausible publication year in a path: prefer the filename, then the last directory."""
    parts = path.replace("\\", "/").split("/")
    for component in (parts[-1], *reversed(parts[:-1])):
        years = [int(match) for match in _YEAR.findall(component)]
        if years:
            return years[-1]
    return None


def typography_guess(year: int | None, born_digital: bool) -> str:
    if born_digital:
        return "digital"
    if year is None:
        return "unknown"
    if year < 1900:
        return "letterpress"
    if year < 1975:
        return "letterpress-typewriter"
    if year < 1995:
        return "phototypeset"
    return "digital-era-scan"


BORN_DIGITAL = re.compile(
    r"LaTeX|pdfTeX|XeTeX|LuaTeX|InDesign|QuarkXPress|Microsoft|Word|LibreOffice|OpenOffice|"
    r"Pages|Quartz PDFContext|Prince|wkhtmltopdf|Chrom|Skia|cairo|Firefox|iText|PDFsharp|"
    r"ReportLab|FrameMaker|PageMaker|Ghostscript|dvips|Acrobat Distiller|PScript|Illustrator|"
    r"Scribus|groff|troff|Calibre|pandoc",
    re.IGNORECASE,
)
OCR_LAYER = re.compile(
    r"ABBYY|FineReader|Tesseract|OCRmyPDF|hOCR|Paper Capture|ClearScan|Acrobat Capture|"
    r"LuraDocument|LuraTech|Omnipage|Readiris|Kofax|CVISION|PDF Compressor|Internet Archive|"
    r"Adobe Acrobat .*Paper|ScanSnap|Scan|Nuance|ExactScan|Xerox|Canon|Fujitsu|Epson|"
    r"HP Digital|Ricoh|Kyocera|Brother|Konica",
    re.IGNORECASE,
)


def text_layer_origin(producer: str | None, creator: str | None) -> str:
    """'born_digital' | 'ocr_layer' | 'unknown' from PDF metadata (an origin prior, not a measurement)."""
    blob = " ".join(item for item in (producer, creator) if item)
    if not blob:
        return "unknown"
    if OCR_LAYER.search(blob):
        return "ocr_layer"
    if BORN_DIGITAL.search(blob):
        return "born_digital"
    return "unknown"


def tier_for(source: str, path: str, tiers: list[dict] | None = None) -> tuple[str, str]:
    key = f"{source}/{path}"
    for rule in tiers or DEFAULT_TIERS:
        if re.search(rule["pattern"], key):
            return rule["tier"], rule["why"]
    return "B", "unlisted source"


# --------------------------------------------------------------------------- dictionary


class Dictionary:
    """A headword list with crude English suffix stripping, so 'houses'/'walked'/'walking' count."""

    def __init__(self, words: Iterable[str]):
        self.words = {word.strip().casefold() for word in words if word.strip()}
        self._memo: dict[str, bool] = {}

    @classmethod
    def load(cls, path: Path | None) -> Dictionary | None:
        if path is None or not path.is_file():
            return None
        with path.open(encoding="utf-8", errors="replace") as stream:
            return cls(stream)

    def __contains__(self, word: str) -> bool:
        word = word.casefold()
        if word in self.words:
            return True
        cached = self._memo.get(word)
        if cached is not None:
            return cached
        found = False
        for suffix in ("s", "es", "ed", "d", "ing", "ly", "er", "est", "'s", "ies"):
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                stem = word[: -len(suffix)]
                if stem in self.words or (suffix == "ies" and stem + "y" in self.words):
                    found = True
                    break
                if suffix == "ing" and stem + "e" in self.words:
                    found = True
                    break
                if stem.endswith("i") and stem[:-1] + "y" in self.words:  # happily, cities, tidier
                    found = True
                    break
        if len(self._memo) > 500_000:
            self._memo.clear()
        self._memo[word] = found
        return found


def alpha_words(text: str) -> list[str]:
    return _ALPHA_WORD.findall(text)


def document_word_set(text: str, min_length: int = 3) -> set[str]:
    return {word.casefold() for word in alpha_words(text) if len(word) >= min_length}


# --------------------------------------------------------------------------- signals


def single_char_line_stats(lines: list[str]) -> tuple[int, int, int]:
    """(single-character lines, longest run of them, non-blank lines)."""
    count = 0
    longest = 0
    run = 0
    nonblank = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        nonblank += 1
        if len(stripped) == 1:
            count += 1
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return count, longest, nonblank


def spaced_letter_count(text: str) -> int:
    """Letters written 'e d i t i o n' style: runs of four or more single letters separated by spaces."""
    total = 0
    for match in _SPACED_LETTERS.finditer(text):
        total += (len(match.group(0)) + 1) // 2
    return total


def inner_caps_count(words: Iterable[str]) -> int:
    return sum(1 for word in words if len(word) >= 4 and not word.isupper() and _INNER_CAPS.search(word))


def inner_caps_count_text(text: str) -> int:
    """Same count as ``inner_caps_count`` over the words of ``text``, in one regex pass."""
    return len(_INNER_CAPS_WORD.findall(text))


def mixed_token_count(tokens: Iterable[str]) -> int:
    """Tokens like '!li!li\ufffd.N' or 'Coo6wenue1': letters interleaved with digits/symbols (>= 2 switches)."""
    total = 0
    for token in tokens:
        if token.isalpha():
            continue
        core = token.strip(_STRIP_PUNCT)
        if len(core) < 3 or core.isalpha() or core.isdigit() or _NUMERIC_TOKEN.match(core):
            continue
        if core.translate(_JOINERS).isalpha():
            continue  # well-known, don't, e.g.: joined words, not noise
        if _MIXED_CORE.fullmatch(core):
            total += 1
    return total


def gutter_line_count(lines: Iterable[str]) -> int:
    return sum(1 for line in lines if _GUTTER.search(line))


def gutter_line_count_text(text: str) -> int:
    return sum(1 for line in text.split("\n") if "   " in line and _GUTTER.search(line))


def language_guess(words: Iterable[str], sample: int = 30000) -> tuple[str, float, dict[str, float]]:
    """Stopword-vote language guess over the first ``sample`` words; Cyrillic and Greek by script."""
    hits: Counter[str] = Counter()
    total = 0
    cyrillic = greek = kana = han = arabic = hebrew = letters = 0
    for word in (words[:sample] if isinstance(words, list) else words):
        total += 1
        lowered = word.casefold()
        for lang in _STOPWORD_INDEX.get(lowered, ()):
            hits[lang] += 1
        for char in lowered[:3]:
            letters += 1
            code = ord(char)
            if 0x0400 <= code <= 0x04FF:
                cyrillic += 1
            elif 0x0370 <= code <= 0x03FF:
                greek += 1
            elif 0x3040 <= code <= 0x30FF:
                kana += 1
            elif 0x4E00 <= code <= 0x9FFF:
                han += 1
            elif 0x0600 <= code <= 0x06FF:
                arabic += 1
            elif 0x0590 <= code <= 0x05FF:
                hebrew += 1
    if letters:
        for lang, count in (("ru", cyrillic), ("el", greek), ("ja", kana + han if kana else 0), ("zh", han), ("ar", arabic), ("he", hebrew)):
            if count / letters > 0.5:
                return lang, count / letters, {}
    if not total:
        return "unknown", 0.0, {}
    scores = {lang: count / total for lang, count in hits.items()}
    if not scores:
        return "unknown", 0.0, scores
    lang, score = max(scores.items(), key=lambda item: item[1])
    if score < 0.02:
        return "unknown", score, scores
    return lang, score, scores


_LATIN_LETTER = re.compile(r"[A-Za-z\u00C0-\u024F\u1E00-\u1EFF]")


def non_latin_ratio(words: list[str], sample: int = 30000) -> float:
    """Share of alphabetic characters outside Latin script (first ``sample`` words)."""
    letters = 0
    latin = 0
    for word in words[:sample]:
        letters += len(word)
        latin += len(_LATIN_LETTER.findall(word))
    return round(1.0 - latin / letters, 4) if letters else 0.0


def running_heads(page_texts: list[str], min_pages: int = 3) -> tuple[list[str], int]:
    """Lines that open or close at least ``min_pages`` pages (digits collapsed): running heads/feet.

    Returns (normalized lines, number of pages carrying at least one)."""
    if len(page_texts) < max(min_pages, 2):
        return [], 0
    seen: Counter[str] = Counter()
    per_page: list[set[str]] = []
    for page in page_texts:
        lines = [line for line in page.splitlines() if line.strip()]
        edge = set()
        for line in lines[:EDGE_LINES] + lines[-EDGE_LINES:]:
            normalized = normalize_line(line)
            if len(normalized) >= 4 and not _PAGE_NUMBER.match(normalized):
                edge.add(normalized)
        per_page.append(edge)
        seen.update(edge)
    heads = sorted(line for line, count in seen.items() if count >= min_pages)
    head_set = set(heads)
    pages_with = sum(1 for edge in per_page if edge & head_set)
    return heads, pages_with


def furniture_line_kinds(line: str) -> list[str]:
    if not _FURNITURE_HINT.search(line):
        return []
    return [name for name, pattern in FURNITURE_PATTERNS.items() if pattern.search(line)]


class FurnitureCatalogue:
    """Exact-line furniture from the haunting index (research/results/haunting-index/furniture-*.jsonl)."""

    def __init__(self, lines: dict[str, int]):
        self.lines = lines

    @classmethod
    def load(cls, paths: Iterable[Path], min_documents: int = 8) -> FurnitureCatalogue:
        lines: dict[str, int] = {}
        for path in paths:
            if not path.is_file():
                continue
            with path.open(encoding="utf-8") as stream:
                for raw in stream:
                    record = json.loads(raw)
                    documents = int(record.get("documents") or 0)
                    if documents < min_documents:
                        continue
                    for line in str(record.get("text") or "").split("\n"):
                        normalized = normalize_line(line)
                        if len(normalized) < 20 or len(alpha_words(normalized)) < 3:
                            continue
                        if _DOT_LEADER.search(normalized):
                            continue
                        lines[normalized] = max(lines.get(normalized, 0), documents)
        return cls(lines)

    def __contains__(self, line: str) -> bool:
        return normalize_line(line) in self.lines

    def __len__(self) -> int:
        return len(self.lines)


def table_row_count(lines: Iterable[str], min_fields: int = 3) -> int:
    return sum(1 for line in lines if len(_TABLE_FIELD.findall(line)) >= min_fields)


def longest_valid_run(
    text: str, is_valid, min_words: int = 6, max_words: int = 14, single_line: bool = False
) -> str | None:
    """The longest run of consecutive 'valid' words on a page, as it appears in the text."""
    best: tuple[int, int, int] | None = None  # (length, start, end)
    run_start = None
    run_length = 0
    last_end = 0
    for match in _ALPHA_WORD.finditer(text):
        word = match.group(0)
        gap = text[last_end : match.start()]
        # A run breaks at a blank line or a form feed (or any line break when single_line).
        broken = "\n\n" in gap or FORM_FEED in gap or (single_line and "\n" in gap)
        if is_valid(word) and not broken and run_start is not None:
            run_length += 1
        elif is_valid(word):
            run_start = match.start()
            run_length = 1
        else:
            run_start = None
            run_length = 0
        last_end = match.end()
        if run_start is not None and run_length >= min_words and (best is None or run_length > best[0]):
            best = (run_length, run_start, match.end())
    if best is None:
        return None
    phrase = text[best[1] : best[2]]
    words = phrase.split()
    if len(words) > max_words:
        phrase = " ".join(words[:max_words])
    return _SPACES.sub(" ", phrase).strip()


def phrase_present(haystack: str, phrase: str) -> bool:
    return normalize_phrase(phrase) in normalize_phrase(haystack)


def phrase_precedes(haystack: str, first: str, second: str) -> bool | None:
    normalized = normalize_phrase(haystack)
    left = normalized.find(normalize_phrase(first))
    right = normalized.find(normalize_phrase(second))
    if left < 0 or right < 0:
        return None
    return left < right


@dataclass
class Signals:
    values: dict = field(default_factory=dict)


def text_signals(
    text: str,
    *,
    tokens: int | None = None,
    df: dict[str, int] | None = None,
    dictionary: Dictionary | None = None,
    catalogue: FurnitureCatalogue | None = None,
) -> dict:
    """Every per-document signal from the text alone (plus the record's Falcon token count)."""
    lines = text.split("\n")
    page_texts = text.split(FORM_FEED)
    tokens_ws = _TOKEN.findall(text)
    words = alpha_words(text)
    words_ge4 = [word for word in words if len(word) >= 4]
    chars = max(len(text), 1)
    word_count = max(len(tokens_ws), 1)
    alpha_count = max(len(words), 1)
    alpha_chars = sum(map(len, words))

    # One pass over the lines: blank/single-character bookkeeping, furniture, dot leaders,
    # and the digit-collapsed normal form shared by the catalogue lookup and repeated-line ratio.
    single = single_run = longest_run = nonblank = 0
    furniture_kinds: Counter[str] = Counter()
    catalogue_hits = dot_leader_lines = 0
    normalized_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        nonblank += 1
        if len(stripped) == 1:
            single += 1
            single_run += 1
            longest_run = max(longest_run, single_run)
        else:
            single_run = 0
        kinds = furniture_line_kinds(stripped)
        for kind in kinds:
            furniture_kinds[kind] += 1
        if len(stripped) >= 20:
            normalized = normalize_line(stripped)
            normalized_lines.append(normalized)
            if catalogue is not None and normalized in catalogue.lines:
                catalogue_hits += 1
        if _DOT_LEADER.search(stripped):
            dot_leader_lines += 1
    nonblank = max(nonblank, 1)

    lang, lang_score, _ = language_guess(words)
    non_latin = non_latin_ratio(words)
    expected_tpw = EXPECTED_TOKENS_PER_WORD.get(lang, EXPECTED_TOKENS_PER_WORD["unknown"])
    expected_tpw += NON_LATIN_TOKENS_PER_WORD * non_latin
    tokens_per_word = (tokens / word_count) if tokens else None

    # Vocabulary against the corpus document-frequency table and the dictionary.
    hapax = unknown = valid = rare_valid = dict_hits = dict_checked = 0
    if df is not None or dictionary is not None:
        for word in words_ge4:
            lowered = word.casefold()
            frequency = df.get(lowered, 1) if df is not None else None
            in_dictionary = dictionary is not None and lowered.isascii() and lowered in dictionary
            if dictionary is not None and lowered.isascii():
                dict_checked += 1
                dict_hits += in_dictionary
            if frequency is not None:
                if frequency <= 1 and not in_dictionary:
                    hapax += 1
                if frequency <= 2 and not in_dictionary:
                    unknown += 1
                if frequency >= 3 or in_dictionary:
                    valid += 1
                    if frequency <= 30:
                        rare_valid += 1
    ge4 = max(len(words_ge4), 1)

    heads, head_pages = running_heads(page_texts)
    furniture_hits = sum(furniture_kinds.values()) + catalogue_hits
    numeric = sum(1 for token in tokens_ws if not token.isalpha() and _NUMERIC_TOKEN.match(token))
    ttr_window = [word.casefold() for word in words[:20000]]
    ttr = len(set(ttr_window)) / max(len(ttr_window), 1)

    repeated_chars = 0
    if normalized_lines:
        counts = Counter(normalized_lines)
        repeated_chars = sum((count - 1) * len(line) for line, count in counts.items())
    repeated_line_ratio = repeated_chars / max(sum(len(line) for line in normalized_lines), 1)

    values = {
        "chars": len(text),
        "pages_in_text": len(page_texts),
        "words": len(tokens_ws),
        "alpha_words": len(words),
        "alpha_ratio": alpha_chars / chars,
        "replacement_ratio": text.count("\ufffd") / chars,
        "single_char_line_ratio": single / nonblank,
        "single_char_line_max_run": longest_run,
        "spaced_letter_ratio": spaced_letter_count(text) / alpha_count,
        "inner_caps_ratio": inner_caps_count_text(text) / ge4,
        "mixed_token_ratio": mixed_token_count(tokens_ws) / word_count,
        "gutter_line_ratio": gutter_line_count_text(text) / nonblank,
        "dot_leader_lines_per_10k": 10_000 * dot_leader_lines / nonblank,
        "numeric_ratio": numeric / word_count,
        "type_token_ratio_20k": ttr,
        "repeated_line_ratio": repeated_line_ratio,
        "running_head_lines": heads[:8],
        "running_head_count": len(heads),
        "running_head_page_ratio": head_pages / max(len(page_texts), 1),
        "furniture_hits": furniture_hits,
        "furniture_hits_per_10k": 10_000 * furniture_hits / nonblank,
        "furniture_kinds": dict(furniture_kinds.most_common(6)),
        "catalogue_line_hits": catalogue_hits,
        "language": lang,
        "language_score": round(lang_score, 4),
        "non_latin_ratio": non_latin,
        "tokens_per_word": tokens_per_word,
        "expected_tokens_per_word": expected_tpw,
        "fragmentation_excess": (tokens_per_word - expected_tpw) if tokens_per_word else 0.0,
        "hapax_ratio": hapax / ge4 if df is not None else None,
        "unknown_ratio": unknown / ge4 if df is not None else None,
        "rare_valid_ratio": (rare_valid / max(valid, 1)) if df is not None else None,
        "dictionary_ratio": (dict_hits / dict_checked) if dict_checked else None,
        "credential_indicators": credential_indicator_count(text),
        "credential_dump_indicators": credential_dump_indicator_count(text),
    }
    values["non_alpha_excess"] = 1.0 - values["alpha_ratio"]
    values["dictionary_miss"] = (
        1.0 - values["dictionary_ratio"]
        if values["dictionary_ratio"] is not None and lang == "en" and dict_checked >= 50
        else 0.0
    )
    return values


def fidelity_score(signals: dict, origin: str = "unknown") -> tuple[float, dict[str, float]]:
    """1 - noisy-OR of ramped character-level noise signals. Returns (fidelity, per-signal badness)."""
    badness: dict[str, float] = {}
    terms = []
    origin_weight = ORIGIN_NOISE_WEIGHT.get(origin, 1.0)
    # The vocabulary terms are Latin-script instruments: an Arabic or Hebrew edition is not noise.
    script_weight = 1.0 - min(1.0, float(signals.get("non_latin_ratio") or 0.0))
    for name, (lo, hi, weight) in FIDELITY_RAMPS.items():
        value = signals.get(name)
        if value is None:
            continue
        badness[name] = ramp(float(value), lo, hi)
        if name in CHARACTER_SIGNALS:
            weight *= origin_weight * script_weight
        terms.append((badness[name], weight))
    return 1.0 - noisy_or(terms), badness


def layout_score(signals: dict) -> tuple[float, dict[str, float]]:
    badness: dict[str, float] = {}
    terms = []
    for name, (lo, hi, weight) in LAYOUT_RAMPS.items():
        value = signals.get(name)
        if value is None:
            continue
        badness[name] = ramp(float(value), lo, hi)
        terms.append((badness[name], weight))
    return 1.0 - noisy_or(terms), badness


def value_score(signals: dict, tier: str, tokens: int, judge_delta: float | None = None) -> tuple[float, dict]:
    value = TIER_PRIOR.get(tier, TIER_PRIOR["B"])
    parts: dict[str, float] = {"tier_prior": value}
    lo, hi, weight = VALUE_ADJUSTMENTS["rare_valid_ratio"]
    if signals.get("rare_valid_ratio") is not None:
        parts["rare_vocabulary"] = weight * ramp(signals["rare_valid_ratio"], lo, hi)
    lo, hi, weight = VALUE_ADJUSTMENTS["numeric_ratio"]
    parts["numeric"] = weight * ramp(signals.get("numeric_ratio") or 0.0, lo, hi)
    lo, hi, weight = VALUE_ADJUSTMENTS["repeated_line_ratio"]
    parts["repetition"] = weight * ramp(signals.get("repeated_line_ratio") or 0.0, lo, hi)
    ttr = signals.get("type_token_ratio_20k")
    if ttr is not None and signals.get("alpha_words", 0) >= 2000:
        parts["low_vocabulary"] = VALUE_ADJUSTMENTS["low_vocabulary"][2] * ramp(0.12 - ttr, 0.0, 0.06)
    if signals.get("credential_dump_indicators", 0) >= 1:
        parts["credential_dump"] = VALUE_ADJUSTMENTS["credential_dump"][2]
    if tokens < 500:
        parts["tiny"] = -0.10
    if judge_delta is not None:
        # Library-likeness judge (NLL under a library checkpoint minus base): negative = library-like.
        parts["judge"] = 0.20 * ramp(-judge_delta, 0.0, 0.3) - 0.20 * ramp(judge_delta, 0.0, 0.3)
    total = max(0.0, min(1.0, sum(parts.values())))
    return total, parts


def cell_for(fidelity: float, value: float) -> str:
    high_f = fidelity >= FIDELITY_THRESHOLD
    high_v = value >= VALUE_THRESHOLD
    if high_f and high_v:
        return "main"
    if high_f:
        return "specialist"
    if high_v:
        return "quarantine"
    return "drop"


# --------------------------------------------------------------------------- reading view


@dataclass
class Transform:
    line: int
    kind: str
    original: str
    replacement: str | None  # None = line removed

    def as_dict(self) -> dict:
        return {"line": self.line, "kind": self.kind, "original": self.original, "replacement": self.replacement}


EDGE_LINES = 3  # running heads/feet and page numbers live in the first/last few non-blank lines


def edge_line_indices(lines: list[str], depth: int = EDGE_LINES) -> set[int]:
    """Indices of the first/last ``depth`` non-blank lines of every page (pages split on form feeds)."""
    edges: set[int] = set()
    page_start = 0
    for index in range(len(lines) + 1):
        at_end = index == len(lines)
        if at_end or FORM_FEED in lines[index]:
            nonblank = [i for i in range(page_start, index) if lines[i].strip() and FORM_FEED not in lines[i]]
            edges.update(nonblank[:depth] + nonblank[-depth:])
            if not at_end and lines[index].strip(FORM_FEED).strip():
                edges.add(index)  # text after the form feed on the same line opens the next page
            page_start = index
    return edges


def reading_view(
    text: str,
    *,
    heads: Iterable[str] = (),
    catalogue: FurnitureCatalogue | None = None,
    single_run: int = 4,
) -> tuple[str, list[Transform]]:
    """Strip page furniture from a document, keeping form feeds and a reversible transform log.

    Removes: catalogue/pattern furniture lines, running heads and feet (given), bare page-number
    lines at page edges, dash rules, runs of >= ``single_run`` single-character lines. Collapses
    dot leaders to a single ellipsis. ``restore`` inverts it exactly."""
    lines = text.split("\n")
    head_set = set(heads)
    transforms: list[Transform] = []
    keep: list[str | None] = list(lines)

    edge_indices = edge_line_indices(lines)

    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        body = stripped.strip(FORM_FEED).strip()
        kinds = furniture_line_kinds(body)
        kind = None
        if kinds:
            kind = "furniture:" + kinds[0]
        elif catalogue is not None and body in catalogue:
            kind = "furniture:catalogue"
        elif head_set and normalize_line(body) in head_set and index in edge_indices:
            kind = "running_head"
        elif index in edge_indices and _PAGE_NUMBER.match(body):
            kind = "page_number"
        elif _DASH_RULE.match(body) and len(body) >= 8:
            kind = "rule"
        if kind is not None:
            replacement = FORM_FEED if FORM_FEED in line else None
            transforms.append(Transform(index, kind, line, replacement))
            keep[index] = replacement
            continue
        if _DOT_LEADER_RUN.search(line):
            replaced = _DOT_LEADER_RUN.sub(" … ", line)
            transforms.append(Transform(index, "dot_leader", line, replaced))
            keep[index] = replaced

    # Runs of single-character lines (spine/caption debris), measured on the surviving lines.
    run: list[int] = []

    def flush() -> None:
        if len(run) >= single_run:
            for i in run:
                transforms.append(Transform(i, "single_char_run", lines[i], None))
                keep[i] = None
        run.clear()

    for index, line in enumerate(lines):
        if keep[index] is None:
            continue  # already removed: it neither joins nor breaks a run
        if keep[index] != line:
            flush()
            continue
        body = line.strip().strip(FORM_FEED).strip()
        if not body:
            continue  # blank lines do not break a run
        if len(body) == 1 and FORM_FEED not in line:
            run.append(index)
        else:
            flush()
    flush()

    transforms.sort(key=lambda item: item.line)
    kept = [line for line in keep if line is not None]
    view = "\n".join(kept)
    view = re.sub(r"\n{4,}", "\n\n\n", view)
    return view, transforms


def restore(view_lines: list[str], transforms: list[Transform]) -> list[str]:
    """Inverse of ``reading_view`` on the un-collapsed kept lines (used by the tests)."""
    result = list(view_lines)
    for transform in sorted(transforms, key=lambda item: item.line):
        if transform.replacement is None:
            result.insert(transform.line, transform.original)
        else:
            result[transform.line] = transform.original
    return result


# --------------------------------------------------------------------------- corpus io


def iter_dataset(dataset: Path) -> Iterator[dict]:
    manifest = json.loads((dataset / "manifest.json").read_text())
    for split, info in manifest["splits"].items():
        for shard in info["shards"]:
            with gzip.open(dataset / shard["path"], "rt", encoding="utf-8") as stream:
                for line in stream:
                    record = json.loads(line)
                    record["split"] = split
                    yield record


def read_record(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def iter_unreviewed(records: Path) -> Iterator[dict]:
    for path in sorted(records.glob("*/*.json.gz")):
        record = read_record(path)
        if record.get("status") == "ocr_unreviewed" and record.get("text"):
            yield {
                "id": record["document_id"],
                "source": record["source"],
                "path": record["relative_path"],
                "content_sha256": record.get("content_sha256"),
                "tokens": int(record.get("tokens") or 0),
                "text": record["text"],
                "split": None,
            }


def record_metadata(records: Path, ids: Iterable[str]) -> dict[str, dict]:
    wanted = set(ids)
    found: dict[str, dict] = {}
    for path in records.glob("*/*.json.gz"):
        document_id = path.name.split(".")[0]
        if document_id not in wanted:
            continue
        record = read_record(path)
        found[document_id] = {
            key: record.get(key)
            for key in ("kind", "extraction", "pages", "status", "chars", "words", "ocr_raw", "ocr_model")
        }
    return found


def _shard_word_sets(shard: Path) -> Counter:
    counter: Counter[str] = Counter()
    with gzip.open(shard, "rt", encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            counter.update(document_word_set(record["text"]))
    return counter


def build_document_frequency(dataset: Path, extra_texts: Iterable[str], workers: int) -> Counter:
    manifest = json.loads((dataset / "manifest.json").read_text())
    shards = [dataset / shard["path"] for info in manifest["splits"].values() for shard in info["shards"]]
    df: Counter[str] = Counter()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for partial in pool.map(_shard_word_sets, shards):
            df.update(partial)
    for text in extra_texts:
        df.update(document_word_set(text))
    return df


def save_df(df: Counter, path: Path, min_df: int = 2) -> int:
    kept = {word: count for word, count in df.items() if count >= min_df}
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as stream:
        json.dump(kept, stream, ensure_ascii=False)
    return len(kept)


def load_df(path: Path) -> dict[str, int]:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def families_index(families_dir: Path) -> tuple[dict[str, dict], dict[str, dict], dict[str, str]]:
    """(family info by id, best non-series sibling by id, proposed split by id)."""
    info = {row["id"]: row for row in load_jsonl(families_dir / "families.jsonl")}
    siblings: dict[str, dict] = {}
    pairs_path = families_dir / "pairs.jsonl"
    if pairs_path.is_file():
        with pairs_path.open(encoding="utf-8") as stream:
            for line in stream:
                pair = json.loads(line)
                if pair.get("relation") == "series":
                    continue
                agreement = max(float(pair.get("jaccard") or 0), float(pair.get("containment") or 0))
                for side, other in (("left", "right"), ("right", "left")):
                    document_id = pair[side]["id"]
                    current = siblings.get(document_id)
                    if current is None or agreement > current["agreement"]:
                        siblings[document_id] = {
                            "sibling_id": pair[other]["id"],
                            "sibling_path": pair[other]["path"],
                            "relation": pair.get("relation"),
                            "confidence": pair.get("confidence"),
                            "agreement": agreement,
                            "jaccard": pair.get("jaccard"),
                            "containment": pair.get("containment"),
                        }
    splits: dict[str, str] = {}
    for name in ("validation", "test"):
        for row in load_jsonl(families_dir / f"proposed-{name}.jsonl"):
            splits[row["id"]] = name
    return info, siblings, splits


# --------------------------------------------------------------------------- pdfinfo


def run_pdfinfo(path: Path, timeout: int = 60) -> dict:
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)], capture_output=True, text=True, timeout=timeout, check=False
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"error": str(exc)}
    info: dict[str, str] = {}
    for line in result.stdout.splitlines():
        key, _, value = line.partition(":")
        if key and value:
            info[key.strip()] = value.strip()
    out = {
        "producer": info.get("Producer"),
        "creator": info.get("Creator"),
        "pages": int(info["Pages"]) if info.get("Pages", "").isdigit() else None,
        "page_size": info.get("Page size"),
        "tagged": info.get("Tagged"),
    }
    if result.returncode != 0 and not info:
        out["error"] = result.stderr.strip()[-300:]
    return out


def _pdfinfo_job(item: tuple[str, str]) -> dict:
    document_id, path = item
    row = run_pdfinfo(Path(path))
    row["id"] = document_id
    row["text_layer_origin"] = text_layer_origin(row.get("producer"), row.get("creator"))
    return row


def run_pdfinfo_command(args: argparse.Namespace) -> dict:
    roots = parse_roots(args.root)
    output = args.output / "pdfinfo.jsonl"
    done = {row["id"] for row in load_jsonl(output)}
    jobs: list[tuple[str, str]] = []
    for record in iter_universe(args.dataset, args.records, include_text=False):
        if record["id"] in done or not record["path"].lower().endswith(".pdf"):
            continue
        source_path = roots[record["source"]] / record["path"]
        if source_path.is_file():
            jobs.append((record["id"], str(source_path)))
    rows = list(load_jsonl(output))
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows.extend(pool.map(_pdfinfo_job, jobs, chunksize=16))
    write_jsonl(output, rows)
    origins = Counter(row.get("text_layer_origin") for row in rows)
    summary = {"pdfs": len(rows), "new": len(jobs), "origins": dict(origins)}
    print(json.dumps(summary))
    return summary


def parse_roots(values: list[str] | None) -> dict[str, Path]:
    roots = dict(DEFAULT_ROOTS)
    for value in values or []:
        name, _, path = value.partition("=")
        roots[name] = Path(path).expanduser().resolve()
    return roots


def iter_universe(dataset: Path, records: Path | None, include_text: bool = True) -> Iterator[dict]:
    for record in iter_dataset(dataset):
        record["in_dataset"] = True
        if not include_text:
            record.pop("text", None)
        yield record
    if records is not None and records.is_dir():
        for record in iter_unreviewed(records):
            record["in_dataset"] = False
            if not include_text:
                record.pop("text", None)
            yield record


# --------------------------------------------------------------------------- score


_WORKER: dict = {}


def _score_init(df_path: str | None, dictionary_path: str | None, catalogue_paths: list[str]) -> None:
    _WORKER["df"] = load_df(Path(df_path)) if df_path else None
    _WORKER["dictionary"] = Dictionary.load(Path(dictionary_path)) if dictionary_path else None
    _WORKER["catalogue"] = FurnitureCatalogue.load([Path(p) for p in catalogue_paths])


def _score_shard(job: tuple[str, str | None]) -> list[dict]:
    """Score every record of one shard (or the unreviewed records dir when shard is None)."""
    kind, path = job
    out = []
    if kind == "shard":
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            records = (json.loads(line) for line in stream)
            for record in records:
                signals = text_signals(
                    record["text"],
                    tokens=record["tokens"],
                    df=_WORKER["df"],
                    dictionary=_WORKER["dictionary"],
                    catalogue=_WORKER["catalogue"],
                )
                out.append({"id": record["id"], "signals": signals})
    else:
        for record in iter_unreviewed(Path(path)):
            signals = text_signals(
                record["text"],
                tokens=record["tokens"],
                df=_WORKER["df"],
                dictionary=_WORKER["dictionary"],
                catalogue=_WORKER["catalogue"],
            )
            out.append({"id": record["id"], "signals": signals})
    return out


SIGNAL_COLUMNS = (
    "chars", "pages_in_text", "words", "alpha_words", "alpha_ratio", "replacement_ratio",
    "single_char_line_ratio", "single_char_line_max_run", "spaced_letter_ratio", "inner_caps_ratio",
    "mixed_token_ratio", "gutter_line_ratio", "dot_leader_lines_per_10k", "numeric_ratio",
    "type_token_ratio_20k", "repeated_line_ratio", "running_head_lines", "running_head_count",
    "running_head_page_ratio", "furniture_hits", "furniture_hits_per_10k", "furniture_kinds",
    "catalogue_line_hits", "language", "language_score", "tokens_per_word", "expected_tokens_per_word",
    "fragmentation_excess", "hapax_ratio", "unknown_ratio", "rare_valid_ratio", "dictionary_ratio",
    "credential_indicators", "credential_dump_indicators", "non_alpha_excess", "dictionary_miss",
    "non_latin_ratio",
)


def run_score(args: argparse.Namespace) -> dict:
    output: Path = args.output
    output.mkdir(parents=True, exist_ok=True)
    df_path = output / "vocab-df.json.gz"
    catalogue_paths = [str(p) for p in args.furniture]

    if getattr(args, "rescore", False):
        # Recompute scores from the signal columns already on disk (ramp calibration loop).
        signals_by_id = {
            row["id"]: {key: row.get(key) for key in SIGNAL_COLUMNS}
            for row in load_jsonl(output / "scores.jsonl")
        }
        return finish_score(args, signals_by_id)

    if not df_path.is_file() or args.rebuild_df:
        extra = [record["text"] for record in iter_unreviewed(args.records)] if args.records else []
        df = build_document_frequency(args.dataset, extra, args.workers)
        kept = save_df(df, df_path)
        print(f"document-frequency table: {len(df):,} words, {kept:,} with df>=2 -> {df_path}", file=sys.stderr)
        del df

    manifest = json.loads((args.dataset / "manifest.json").read_text())
    jobs: list[tuple[str, str | None]] = [
        ("shard", str(args.dataset / shard["path"]))
        for info in manifest["splits"].values()
        for shard in info["shards"]
    ]
    if args.records and args.records.is_dir():
        jobs.append(("unreviewed", str(args.records)))
    signals_by_id: dict[str, dict] = {}
    with ProcessPoolExecutor(
        max_workers=args.workers,
        initializer=_score_init,
        initargs=(str(df_path), str(args.dictionary) if args.dictionary else None, catalogue_paths),
    ) as pool:
        for rows in pool.map(_score_shard, jobs):
            for row in rows:
                signals_by_id[row["id"]] = row["signals"]
    return finish_score(args, signals_by_id)


def finish_score(args: argparse.Namespace, signals_by_id: dict[str, dict]) -> dict:
    output: Path = args.output
    metadata_ids = list(signals_by_id)
    metadata = record_metadata(args.records, metadata_ids) if args.records else {}
    pdfinfo = {row["id"]: row for row in load_jsonl(output / "pdfinfo.jsonl")}
    family_info, siblings, proposed_splits = families_index(args.families)
    quality_flags = {
        row["document_id"]: row.get("flags", "") for row in load_jsonl(args.quality / "flagged.jsonl")
    } if args.quality else {}
    judge = {row["id"]: float(row["delta"]) for row in load_jsonl(args.judge)} if args.judge else {}
    tiers = json.loads(args.tiers.read_text()) if args.tiers else None

    rows: list[dict] = []
    for record in iter_universe(args.dataset, args.records, include_text=False):
        signals = signals_by_id.get(record["id"])
        if signals is None:
            continue
        meta = metadata.get(record["id"], {})
        info = pdfinfo.get(record["id"], {})
        origin = info.get("text_layer_origin") or "unknown"
        if meta.get("extraction") == "paddleocr_vl_1_6_mlx":
            origin = "paddleocr_vl"
        elif meta.get("extraction") in ("ia_djvu_txt", "ia_hocr_searchtext"):
            origin = "ia_ocr_sidecar"
        elif meta.get("kind") in ("plain_text", "epub", "docx"):
            origin = "born_digital"
        tier, tier_why = tier_for(record["source"], record["path"], tiers)
        year = guess_year(record["path"])
        sibling = siblings.get(record["id"])
        if sibling and sibling["agreement"] >= 0.7 and signals.get("hapax_ratio") is not None:
            # A near-duplicate copy lifts every word to df = 2; count only true hapaxes then.
            signals["unknown_ratio"] = signals["hapax_ratio"]
        fidelity, fidelity_badness = fidelity_score(signals, origin)
        layout, layout_badness = layout_score(signals)
        value, value_parts = value_score(signals, tier, record["tokens"], judge.get(record["id"]))
        fam = family_info.get(record["id"], {})
        p_corrupt = 1.0 - fidelity
        row = {
            "id": record["id"],
            "source": record["source"],
            "path": record["path"],
            "tokens": record["tokens"],
            "split": record.get("split"),
            "proposed_split": proposed_splits.get(record["id"]),
            "in_dataset": record["in_dataset"],
            "extraction": meta.get("extraction"),
            "kind": meta.get("kind"),
            "pages": meta.get("pages"),
            "text_layer_origin": origin,
            "pdf_producer": info.get("producer"),
            "pdf_creator": info.get("creator"),
            "year_guess": year,
            "typography_guess": typography_guess(year, origin == "born_digital"),
            "tier": tier,
            "tier_why": tier_why,
            "family_id": fam.get("family_id"),
            "family_size": fam.get("family_size"),
            "series_id": fam.get("series_id"),
            "weak_links": fam.get("weak_links"),
            "sibling_id": sibling["sibling_id"] if sibling else None,
            "sibling_relation": sibling["relation"] if sibling else None,
            "sibling_agreement": round(sibling["agreement"], 4) if sibling else None,
            "quality_flags": quality_flags.get(record["id"], ""),
            "judge_delta": judge.get(record["id"]),
            "fidelity": round(fidelity, 4),
            "layout": round(layout, 4),
            "value": round(value, 4),
            "p_corrupt": round(p_corrupt, 4),
            "cell": cell_for(fidelity, value),
            "reocr_priority": round(p_corrupt * record["tokens"] * value, 1),
            "fidelity_badness": {k: round(v, 3) for k, v in fidelity_badness.items() if v > 0},
            "layout_badness": {k: round(v, 3) for k, v in layout_badness.items() if v > 0},
            "value_parts": {k: round(v, 3) for k, v in value_parts.items()},
        }
        for key, val in signals.items():
            row[key] = round(val, 5) if isinstance(val, float) else val
        rows.append(row)

    rows.sort(key=lambda row: (row["source"], row["path"]))
    write_jsonl(output / "scores.jsonl", rows)
    summary = summarize_scores(rows)
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    (output / "summary.md").write_text(render_summary(summary, rows))
    priority = sorted(
        (row for row in rows if reocr_candidate(row)),
        key=lambda row: -row["reocr_priority"],
    )
    write_jsonl(
        output / "reocr-priority.jsonl",
        (
            {
                key: row[key]
                for key in (
                    "id", "source", "path", "tokens", "p_corrupt", "value", "reocr_priority",
                    "text_layer_origin", "pages", "language", "fidelity_badness",
                )
            }
            for row in priority
        ),
    )
    print(json.dumps({"documents": len(rows), "cells": summary["cells"]}, ensure_ascii=False))
    return summary


def reocr_candidate(row: dict) -> bool:
    """Quarantine documents in corpus-v1 whose text is Latin-script (the instruments' domain)."""
    return row["cell"] == "quarantine" and bool(row["in_dataset"]) and (row.get("non_latin_ratio") or 0.0) < 0.3


def summarize_scores(rows: list[dict]) -> dict:
    cells: dict[str, dict] = {}
    for row in rows:
        bucket = cells.setdefault(row["cell"], {"documents": 0, "tokens": 0, "in_dataset_documents": 0, "in_dataset_tokens": 0})
        bucket["documents"] += 1
        bucket["tokens"] += row["tokens"]
        if row["in_dataset"]:
            bucket["in_dataset_documents"] += 1
            bucket["in_dataset_tokens"] += row["tokens"]
    by_origin: dict[str, dict] = {}
    for row in rows:
        bucket = by_origin.setdefault(row["text_layer_origin"], {"documents": 0, "tokens": 0, "fidelity_sum": 0.0})
        bucket["documents"] += 1
        bucket["tokens"] += row["tokens"]
        bucket["fidelity_sum"] += row["fidelity"]
    for bucket in by_origin.values():
        bucket["mean_fidelity"] = round(bucket.pop("fidelity_sum") / max(bucket["documents"], 1), 3)
    languages = Counter(row["language"] for row in rows)
    offenders = sorted(rows, key=lambda row: -(row["p_corrupt"] * row["tokens"]))[:25]
    priority = sorted((row for row in rows if reocr_candidate(row)), key=lambda row: -row["reocr_priority"])[:25]
    tiers: dict[str, dict] = {}
    for row in rows:
        bucket = tiers.setdefault(row["tier"], {"documents": 0, "tokens": 0})
        bucket["documents"] += 1
        bucket["tokens"] += row["tokens"]
    return {
        "schema_version": SCHEMA_VERSION,
        "documents": len(rows),
        "tokens": sum(row["tokens"] for row in rows),
        "thresholds": {"fidelity": FIDELITY_THRESHOLD, "value": VALUE_THRESHOLD},
        "cells": cells,
        "by_text_layer_origin": by_origin,
        "by_tier": tiers,
        "languages": dict(languages.most_common()),
        "top_offenders": [
            {k: row[k] for k in ("id", "source", "path", "tokens", "fidelity", "value", "cell", "fidelity_badness")}
            for row in offenders
        ],
        "reocr_priority": [
            {k: row[k] for k in ("id", "source", "path", "tokens", "p_corrupt", "value", "reocr_priority", "text_layer_origin")}
            for row in priority
        ],
    }


def render_summary(summary: dict, rows: list[dict]) -> str:
    lines = ["# corpus-v2 admission scores", ""]
    lines.append(f"Documents: {summary['documents']:,}; tokens: {summary['tokens']:,}. "
                 f"Thresholds: fidelity >= {FIDELITY_THRESHOLD}, value >= {VALUE_THRESHOLD}.")
    lines += ["", "## 2x2 (documents / tokens; in-dataset counts in parentheses)", "",
              "| cell | fidelity | value | documents | tokens |", "|---|---|---|---:|---:|"]
    labels = {"main": ("high", "high"), "specialist": ("high", "low"), "quarantine": ("low", "high"), "drop": ("low", "low")}
    for cell in ("main", "specialist", "quarantine", "drop"):
        bucket = summary["cells"].get(cell, {"documents": 0, "tokens": 0, "in_dataset_documents": 0, "in_dataset_tokens": 0})
        lines.append(
            f"| {cell} | {labels[cell][0]} | {labels[cell][1]} | {bucket['documents']:,} ({bucket['in_dataset_documents']:,}) "
            f"| {bucket['tokens']:,} ({bucket['in_dataset_tokens']:,}) |"
        )
    lines += ["", "## By text-layer origin", "", "| origin | documents | tokens | mean fidelity |", "|---|---:|---:|---:|"]
    for origin, bucket in sorted(summary["by_text_layer_origin"].items(), key=lambda item: -item[1]["tokens"]):
        lines.append(f"| {origin} | {bucket['documents']:,} | {bucket['tokens']:,} | {bucket['mean_fidelity']} |")
    lines += ["", "## By tier", "", "| tier | documents | tokens |", "|---|---:|---:|"]
    for tier, bucket in sorted(summary["by_tier"].items()):
        lines.append(f"| {tier} | {bucket['documents']:,} | {bucket['tokens']:,} |")
    lines += ["", "## Languages (stopword guess)", "", ", ".join(f"{k} {v:,}" for k, v in summary["languages"].items())]
    lines += ["", "## Top offenders (p_corrupt x tokens)", "", "| tokens | fidelity | value | cell | path | badness |", "|---:|---:|---:|---|---|---|"]
    for row in summary["top_offenders"]:
        badness = ", ".join(f"{k}={v}" for k, v in sorted(row["fidelity_badness"].items(), key=lambda kv: -kv[1])[:3])
        lines.append(f"| {row['tokens']:,} | {row['fidelity']} | {row['value']} | {row['cell']} | {row['source']}/{row['path']} | {badness} |")
    lines += ["", "## Re-OCR priority (p_corrupt x tokens x value, quarantine cell)", "", "| priority | tokens | p_corrupt | value | origin | path |", "|---:|---:|---:|---:|---|---|"]
    for row in summary["reocr_priority"]:
        lines.append(f"| {row['reocr_priority']:,.0f} | {row['tokens']:,} | {row['p_corrupt']} | {row['value']} | {row['text_layer_origin']} | {row['source']}/{row['path']} |")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- page geometry


_BBOX_BLOCK = re.compile(r"<block xMin=\"([\d.]+)\" yMin=\"([\d.]+)\" xMax=\"([\d.]+)\" yMax=\"([\d.]+)\">(.*?)</block>", re.DOTALL)
_BBOX_LINE = re.compile(r"<line xMin=\"([\d.]+)\" yMin=\"([\d.]+)\" xMax=\"([\d.]+)\" yMax=\"([\d.]+)\">(.*?)</line>", re.DOTALL)
_BBOX_WORD = re.compile(r"<word [^>]*>(.*?)</word>", re.DOTALL)
_BBOX_PAGE = re.compile(r"<page width=\"([\d.]+)\" height=\"([\d.]+)\">")


@dataclass
class Block:
    x0: float
    y0: float
    x1: float
    y1: float
    lines: list[str]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


def parse_bbox_layout(xml: str) -> tuple[float, float, list[Block]]:
    page = _BBOX_PAGE.search(xml)
    width = float(page.group(1)) if page else 0.0
    height = float(page.group(2)) if page else 0.0
    blocks: list[Block] = []
    for match in _BBOX_BLOCK.finditer(xml):
        lines = []
        for line_match in _BBOX_LINE.finditer(match.group(5)):
            words = [html.unescape(word) for word in _BBOX_WORD.findall(line_match.group(5))]
            if words:
                lines.append(" ".join(words))
        if lines:
            blocks.append(Block(*(float(match.group(i)) for i in range(1, 5)), lines))
    return width, height, blocks


def pdf_page_blocks(pdf: Path, page_index: int, timeout: int = 120) -> tuple[float, float, list[Block]]:
    result = subprocess.run(
        ["pdftotext", "-bbox-layout", "-f", str(page_index + 1), "-l", str(page_index + 1), str(pdf), "-"],
        capture_output=True, text=True, timeout=timeout, check=False,
    )
    return parse_bbox_layout(result.stdout)


def paddle_page_blocks(page: dict) -> tuple[float, float, list[Block]]:
    width = float(page.get("width") or 0)
    height = float(page.get("height") or 0)
    blocks = []
    for block in page.get("blocks", []):
        bbox = block.get("bbox") or []
        content = (block.get("content") or "").strip()
        if len(bbox) != 4 or not content:
            continue
        blocks.append(Block(*(float(v) for v in bbox), content.split("\n")))
    return width, height, blocks


def column_layout(width: float, blocks: list[Block], min_lines: int = 2) -> list[list[Block]]:
    """Group narrow text blocks into columns by x-overlap; wide blocks (> 0.6 page) are not columns."""
    if width <= 0:
        return []
    narrow = [b for b in blocks if len(b.lines) >= min_lines and (b.x1 - b.x0) <= 0.6 * width]
    narrow.sort(key=lambda b: b.x0)
    columns: list[list[Block]] = []
    for block in narrow:
        for column in columns:
            left = max(block.x0, min(b.x0 for b in column))
            right = min(block.x1, max(b.x1 for b in column))
            if right - left > 0.5 * (block.x1 - block.x0):
                column.append(block)
                break
        else:
            columns.append([block])
    columns = [sorted(column, key=lambda b: b.y0) for column in columns if sum(len(b.lines) for b in column) >= 4]
    columns.sort(key=lambda column: min(b.x0 for b in column))
    return columns


def column_order_phrases(columns: list[list[Block]], min_words: int = 4) -> tuple[str, str] | None:
    """(last phrase of the left column, first phrase of the next column) for an order check."""
    if len(columns) < 2:
        return None
    left, right = columns[0], columns[1]

    def phrase(lines: list[str], from_end: bool) -> str | None:
        for line in (reversed(lines) if from_end else lines):
            tokens = line.split()
            window = tokens[-6:] if from_end else tokens[:6]
            alphabetic = sum(1 for w in window if _ALPHA_WORD.fullmatch(w.strip(".,;:!?()\"'")))
            if alphabetic >= min_words:
                return " ".join(window)  # contiguous, punctuation kept, so it can be found verbatim
        return None

    first = phrase(left[-1].lines, from_end=True) or phrase([l for b in left for l in b.lines], from_end=True)
    second = phrase(right[0].lines, from_end=False) or phrase([l for b in right for l in b.lines], from_end=False)
    if first and second and normalize_phrase(first) != normalize_phrase(second):
        return first, second
    return None


def render_page(pdf: Path, page_index: int, target: Path, scale: int = 1000, quality: int = 55, timeout: int = 180) -> Path | None:
    target.parent.mkdir(parents=True, exist_ok=True)
    prefix = target.with_suffix("")
    try:
        subprocess.run(
            ["pdftoppm", "-f", str(page_index + 1), "-l", str(page_index + 1), "-gray", "-scale-to", str(scale),
             "-jpeg", "-jpegopt", f"quality={quality}", "-singlefile", str(pdf), str(prefix)],
            capture_output=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return None
    candidate = prefix.with_suffix(".jpg")
    return candidate if candidate.is_file() and candidate.stat().st_size > 0 else None


# --------------------------------------------------------------------------- gold set


def noise_band(fidelity: float) -> str:
    if fidelity >= 0.85:
        return "clean"
    if fidelity >= FIDELITY_THRESHOLD:
        return "mid"
    return "noisy"


def era_band(year: int | None) -> str:
    if year is None:
        return "unknown"
    if year < 1950:
        return "pre-1950"
    if year < 1990:
        return "1950-1989"
    return "1990+"


def page_checks(
    page_text: str,
    *,
    blocks: list[Block],
    width: float,
    heads: Iterable[str],
    is_valid,
    catalogue: FurnitureCatalogue | None,
    paddle_page: dict | None = None,
) -> list[dict]:
    """Unit-test style checks for one page. Each has kind, args, and a one-line human question."""
    checks: list[dict] = []
    lines = page_text.split("\n")

    # The must-contain phrase is prose: build it on the page's reading view (furniture gone) and
    # require it to sit inside the raw page too, falling back to a single physical line.
    view_text, _ = reading_view(page_text, heads=heads, catalogue=catalogue)
    phrase = longest_valid_run(view_text, is_valid)
    if phrase is not None and not phrase_present(page_text, phrase):
        phrase = longest_valid_run(view_text, is_valid, single_line=True)
    checks.append({
        "kind": "must_contain",
        "phrase": phrase,
        "question": "Is this phrase printed on the page image, in this order, with these words?",
        "auto_note": None if phrase else "no run of 6 valid words found on the page",
    })

    furniture_lines = []
    head_set = set(heads)
    edges = edge_line_indices(lines)
    for index, line in enumerate(lines):
        body = line.strip()
        if not body:
            continue
        kinds = furniture_line_kinds(body)
        if kinds:
            furniture_lines.append({"line": body[:160], "kind": kinds[0]})
        elif catalogue is not None and body in catalogue:
            furniture_lines.append({"line": body[:160], "kind": "catalogue"})
        elif index in edges and normalize_line(body) in head_set:
            furniture_lines.append({"line": body[:160], "kind": "running_head"})
    for item in furniture_lines[:3]:
        checks.append({
            "kind": "must_not_contain",
            "phrase": item["line"],
            "furniture_kind": item["kind"],
            "question": "Is this line page furniture (stamp, running head, notice) rather than the work's text?",
        })

    columns = column_layout(width, blocks)
    order = column_order_phrases(columns)
    if order:
        checks.append({
            "kind": "column_order",
            "first": order[0],
            "second": order[1],
            "columns": len(columns),
            "question": "On the image, does the first phrase end the left column and the second begin the next column?",
        })

    _, longest_run, _ = single_char_line_stats(lines)
    if longest_run >= 4:
        checks.append({
            "kind": "no_single_letter_run",
            "run": longest_run,
            "question": "Is there really a vertical column of single letters on the page (spine, caption), or is this OCR debris?",
        })

    suspicious = Counter(
        word for word in alpha_words(page_text) if len(word) >= 4 and not is_valid(word)
    )
    total_ge4 = max(sum(1 for word in alpha_words(page_text) if len(word) >= 4), 1)
    checks.append({
        "kind": "no_invented_text",
        "suspicious_ratio": round(sum(suspicious.values()) / total_ge4, 4),
        "suspicious": [word for word, _ in suspicious.most_common(12)],
        "question": "Are the listed words on the page as written? (Anything not on the page is invented or misread.)",
    })

    if paddle_page is not None:
        tables = [b for b in paddle_page.get("blocks", []) if b.get("label") == "table"]
        if tables:
            rows = sum(str(b.get("content", "")).count("<tr") for b in tables)
            checks.append({"kind": "table_rows", "rows": rows, "tables": len(tables),
                           "question": f"Does the page have {len(tables)} table(s) with {rows} rows in total?"})
    else:
        rows = table_row_count(lines)
        if rows >= 3:
            checks.append({"kind": "table_rows", "rows": rows,
                           "question": f"Does the page have a table with {rows} numeric rows?"})

    if blocks and paddle_page is None:
        layer_text = "\n".join(b.text for b in blocks)
        checks.append({
            "kind": "page_alignment",
            "phrase": phrase,
            "question": "Same page as the image? (The extraction's page split and the PDF page agree.)",
            "layer_chars": len(layer_text),
        })
        checks[-1]["_layer_text"] = layer_text
    return checks


def evaluate_check(check: dict, raw_text: str, view_text: str) -> dict:
    """Run one check against the raw page and the reading view. Returns {raw: bool|None, view: bool|None}."""
    kind = check["kind"]
    raw = view = None
    if kind == "must_contain":
        if check.get("phrase"):
            raw = phrase_present(raw_text, check["phrase"])
            view = phrase_present(view_text, check["phrase"])
        else:
            raw = view = False
    elif kind == "must_not_contain":
        raw = not phrase_present(raw_text, check["phrase"])
        view = not phrase_present(view_text, check["phrase"])
    elif kind == "column_order":
        raw = phrase_precedes(raw_text, check["first"], check["second"])
        view = phrase_precedes(view_text, check["first"], check["second"])
    elif kind == "no_single_letter_run":
        raw = single_char_line_stats(raw_text.split("\n"))[1] < 4
        view = single_char_line_stats(view_text.split("\n"))[1] < 4
    elif kind == "no_invented_text":
        raw = view = check.get("suspicious_ratio", 0.0) < 0.05
    elif kind == "table_rows":
        expected = check.get("rows", 0)
        raw = table_row_count(raw_text.split("\n")) == expected if "tables" not in check else True
        view = table_row_count(view_text.split("\n")) == expected if "tables" not in check else True
    elif kind == "page_alignment":
        layer = check.get("_layer_text") or check.get("layer_text") or ""
        if check.get("phrase") and layer:
            # Any 6-word window of the prose phrase suffices: dehyphenation or a ligature
            # differs between the record and the layout dump, page identity does not.
            words = check["phrase"].split()
            windows = [" ".join(words[i : i + 6]) for i in range(max(1, len(words) - 5))]
            raw = view = any(phrase_present(layer, window) for window in windows)
        else:
            raw = view = None
    return {"raw": raw, "view": view}


def stratified_pick(candidates: list[dict], size: int, keys: tuple[str, ...], seed: int) -> list[dict]:
    """Round-robin over strata so every (source, era, columns, noise) cell is represented."""
    rng = random.Random(seed)
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for candidate in candidates:
        buckets[tuple(candidate["strata"][key] for key in keys)].append(candidate)
    for bucket in buckets.values():
        rng.shuffle(bucket)
    order = sorted(buckets, key=lambda key: (-len(buckets[key]), key))
    chosen: list[dict] = []
    seen_docs: set[str] = set()
    while len(chosen) < size and any(buckets.values()):
        progressed = False
        for key in order:
            bucket = buckets[key]
            while bucket:
                candidate = bucket.pop()
                if candidate["id"] in seen_docs:
                    continue
                chosen.append(candidate)
                seen_docs.add(candidate["id"])
                progressed = True
                break
            if len(chosen) >= size:
                break
        if not progressed:
            break
    return chosen


def run_gold_sample(args: argparse.Namespace) -> dict:
    rng = random.Random(args.seed)
    roots = parse_roots(args.root)
    output: Path = args.output / "gold"
    output.mkdir(parents=True, exist_ok=True)
    scores = {row["id"]: row for row in load_jsonl(args.output / "scores.jsonl")}
    if not scores:
        raise SystemExit("run `hghost-admission score` first: scores.jsonl is missing")
    df = load_df(args.output / "vocab-df.json.gz")
    dictionary = Dictionary.load(args.dictionary)
    catalogue = FurnitureCatalogue.load(args.furniture)

    def is_valid(word: str) -> bool:
        lowered = word.casefold()
        return df.get(lowered, 1) >= 3 or (dictionary is not None and lowered.isascii() and lowered in dictionary)

    # Pass 1: candidate pages. Oversample, measure columns cheaply, then balance.
    per_band = {"clean": 0, "mid": 0, "noisy": 0}
    candidates: list[dict] = []
    texts: dict[str, str] = {}
    want_per_band = args.size * args.oversample // 3
    for record in iter_universe(args.dataset, args.records):
        score = scores.get(record["id"])
        if score is None or not record["path"].lower().endswith(".pdf"):
            continue
        band = noise_band(score["fidelity"])
        if per_band[band] >= want_per_band * 3:
            continue
        pages = record["text"].split(FORM_FEED)
        recorded = score.get("pages") or len(pages)
        if len(pages) < 2 or abs(len(pages) - recorded) > 1:
            continue
        pdf = roots[record["source"]] / record["path"]
        if not pdf.is_file():
            continue
        # skip the cover and the last page; weight interior pages equally
        interior = [i for i in range(1, len(pages) - 1) if len(pages[i].strip()) >= 200] or [
            i for i in range(len(pages)) if len(pages[i].strip()) >= 200
        ]
        if not interior:
            continue
        keep_probability = min(1.0, (want_per_band * 3) / max(1, args.expected_documents_per_band))
        if rng.random() > keep_probability:
            continue
        page_index = rng.choice(interior)
        per_band[band] += 1
        candidates.append({
            "id": record["id"], "source": record["source"], "path": record["path"], "page_index": page_index,
            "page_count": len(pages), "pdf": str(pdf), "fidelity": score["fidelity"], "value": score["value"],
            "cell": score["cell"], "in_dataset": record["in_dataset"], "extraction": score.get("extraction"),
            "text_layer_origin": score.get("text_layer_origin"), "ocr_raw": None,
            "strata": {
                "source": record["source"], "era": era_band(score.get("year_guess")),
                "typography": score.get("typography_guess"), "noise": band, "columns": "?",
            },
        })
        texts[record["id"]] = record["text"]
    print(f"candidate pages: {len(candidates)} {per_band}", file=sys.stderr)

    raw_records = {}
    if args.records:
        for row in candidates:
            if row["extraction"] == "paddleocr_vl_1_6_mlx":
                raw_path = args.records.parent.parent / "paddle-ocr" / "raw" / row["source"] / f"{row['id']}.json.gz"
                if raw_path.is_file():
                    raw_records[row["id"]] = read_record(raw_path)
                    row["ocr_raw"] = str(raw_path)

    # Pass 2: measure columns on the sampled page (cheap), then stratified pick.
    measured: list[dict] = []
    for row in candidates:
        try:
            if row["id"] in raw_records:
                page = raw_records[row["id"]]["pages"][row["page_index"]]
                width, _height, blocks = paddle_page_blocks(page)
            else:
                width, _height, blocks = pdf_page_blocks(Path(row["pdf"]), row["page_index"])
        except (subprocess.TimeoutExpired, IndexError):
            continue
        columns = column_layout(width, blocks)
        row["strata"]["columns"] = "multi" if len(columns) >= 2 else ("single" if blocks else "none")
        row["_blocks"] = blocks
        row["_width"] = width
        measured.append(row)
    chosen = stratified_pick(measured, args.size, ("noise", "source", "columns", "era"), args.seed)
    print(f"chosen pages: {len(chosen)}", file=sys.stderr)

    # Pass 3: checks and page images.
    pages_dir = output / "pages"
    gold_rows: list[dict] = []
    for number, row in enumerate(sorted(chosen, key=lambda r: (r["strata"]["noise"], r["source"], r["path"]))):
        text = texts[row["id"]]
        page_texts = text.split(FORM_FEED)
        page_text = page_texts[row["page_index"]]
        heads, _ = running_heads(page_texts)
        paddle_page = raw_records[row["id"]]["pages"][row["page_index"]] if row["id"] in raw_records else None
        checks = page_checks(
            page_text, blocks=row["_blocks"], width=row["_width"], heads=heads, is_valid=is_valid,
            catalogue=catalogue, paddle_page=paddle_page,
        )
        image = render_page(Path(row["pdf"]), row["page_index"], pages_dir / f"{row['id']}-p{row['page_index']}.jpg", scale=args.scale)
        for check in checks:
            layer = check.pop("_layer_text", None)
            if layer is not None:
                check["layer_text"] = layer[:4000]
        gold_rows.append({
            "gold_id": f"g{number:03d}",
            "id": row["id"], "source": row["source"], "path": row["path"], "page_index": row["page_index"],
            "page_count": row["page_count"], "image": f"pages/{image.name}" if image else None,
            "strata": row["strata"], "fidelity": row["fidelity"], "value": row["value"], "cell": row["cell"],
            "extraction": row["extraction"], "text_layer_origin": row["text_layer_origin"],
            "in_dataset": row["in_dataset"], "running_heads": heads[:6],
            "page_text": page_text, "checks": checks, "verdict": None, "notes": "",
        })
    write_jsonl(output / "gold.jsonl", gold_rows)
    strata = Counter(tuple(sorted(row["strata"].items())) for row in gold_rows)
    summary = {
        "pages": len(gold_rows), "documents": len({row["id"] for row in gold_rows}),
        "images": sum(1 for row in gold_rows if row["image"]),
        "checks": Counter(check["kind"] for row in gold_rows for check in row["checks"]),
        "by_noise": Counter(row["strata"]["noise"] for row in gold_rows),
        "by_source": Counter(row["strata"]["source"] for row in gold_rows),
        "by_columns": Counter(row["strata"]["columns"] for row in gold_rows),
        "by_era": Counter(row["strata"]["era"] for row in gold_rows),
        "by_typography": Counter(row["strata"]["typography"] for row in gold_rows),
        "distinct_strata": len(strata),
    }
    (output / "sample-summary.json").write_text(json.dumps(summary, indent=2, default=dict))
    print(json.dumps(summary, default=dict))
    return summary


def run_gold_check(args: argparse.Namespace) -> dict:
    output: Path = args.output / "gold"
    rows = load_jsonl(output / "gold.jsonl")
    catalogue = FurnitureCatalogue.load(args.furniture)
    results = []
    tallies: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        raw = row["page_text"]
        view, transforms = reading_view(raw, heads=row.get("running_heads", ()), catalogue=catalogue)
        row_results = []
        for check in row["checks"]:
            outcome = evaluate_check(check, raw, view)
            row_results.append({"kind": check["kind"], **outcome})
            for which in ("raw", "view"):
                if outcome[which] is None:
                    tallies[check["kind"]][f"{which}_na"] += 1
                else:
                    tallies[check["kind"]][f"{which}_pass" if outcome[which] else f"{which}_fail"] += 1
        results.append({
            "gold_id": row["gold_id"], "id": row["id"], "page_index": row["page_index"],
            "strata": row["strata"], "checks": row_results, "transforms": len(transforms),
            "view_chars": len(view), "raw_chars": len(raw),
            "all_raw_pass": all(c["raw"] for c in row_results if c["raw"] is not None),
            "all_view_pass": all(c["view"] for c in row_results if c["view"] is not None),
        })
    write_jsonl(output / "check-results.jsonl", results)

    def rate(counter: Counter, which: str) -> float | None:
        passed = counter[f"{which}_pass"]
        failed = counter[f"{which}_fail"]
        return round(passed / (passed + failed), 4) if passed + failed else None

    per_kind = {
        kind: {
            "applicable": counter["raw_pass"] + counter["raw_fail"],
            "raw_pass_rate": rate(counter, "raw"),
            "view_pass_rate": rate(counter, "view"),
        }
        for kind, counter in sorted(tallies.items())
    }
    total_raw = sum(c["raw_pass"] for c in tallies.values()), sum(c["raw_pass"] + c["raw_fail"] for c in tallies.values())
    total_view = sum(c["view_pass"] for c in tallies.values()), sum(c["view_pass"] + c["view_fail"] for c in tallies.values())
    by_noise: dict[str, Counter] = defaultdict(Counter)
    for result in results:
        band = result["strata"]["noise"]
        by_noise[band]["pages"] += 1
        by_noise[band]["raw_all_pass"] += result["all_raw_pass"]
        by_noise[band]["view_all_pass"] += result["all_view_pass"]
    summary = {
        "pages": len(rows),
        "checks": total_raw[1],
        "raw_pass_rate": round(total_raw[0] / max(total_raw[1], 1), 4),
        "view_pass_rate": round(total_view[0] / max(total_view[1], 1), 4),
        "pages_all_pass_raw": sum(r["all_raw_pass"] for r in results),
        "pages_all_pass_view": sum(r["all_view_pass"] for r in results),
        "per_kind": per_kind,
        "by_noise": {band: dict(counter) for band, counter in sorted(by_noise.items())},
    }
    (output / "check-summary.json").write_text(json.dumps(summary, indent=2))
    write_review_sheet(rows, results, output / "review.html")
    print(json.dumps(summary))
    return summary


def write_review_sheet(rows: list[dict], results: list[dict], target: Path) -> None:
    by_id = {r["gold_id"]: r for r in results}
    parts = [
        "<!doctype html><meta charset=utf-8><title>corpus-v2 gold set review</title>",
        "<style>body{font:14px/1.4 system-ui,sans-serif;margin:0;padding:1rem;background:#f6f5f2;color:#1b1b1b}"
        ".page{display:grid;grid-template-columns:minmax(320px,46%) 1fr;gap:1rem;background:#fff;border:1px solid #ddd;"
        "border-radius:8px;padding:1rem;margin-bottom:1.5rem}.page img{width:100%;height:auto;border:1px solid #ccc}"
        "pre{white-space:pre-wrap;font:12px/1.35 ui-monospace,Menlo,monospace;max-height:70vh;overflow:auto;background:#fafafa;padding:.5rem;border:1px solid #eee}"
        ".meta{color:#555;font-size:12px}.check{margin:.35rem 0;padding:.4rem .6rem;border-left:4px solid #bbb;background:#fbfbfb}"
        ".check.pass{border-color:#4a9}.check.fail{border-color:#d55}.check .q{color:#333}.check code{background:#eee;padding:0 .2rem}"
        ".verdict label{margin-right:.8rem}.tally{position:sticky;top:0;background:#fff;padding:.5rem 1rem;border:1px solid #ddd;border-radius:8px;margin-bottom:1rem;z-index:2}"
        "textarea{width:100%;height:8rem;font:12px ui-monospace,monospace}.tag{display:inline-block;background:#eef;padding:0 .4rem;border-radius:4px;margin-right:.3rem;font-size:12px}</style>",
        f"<div class=tally><b>corpus-v2 gold set</b> — {len(rows)} pages. For each check: <b>confirm</b> if the page image agrees with the check, <b>deny</b> if it does not, <b>skip</b> if unclear. "
        "Verdicts persist in this browser; <button onclick=exportVerdicts()>export verdicts</button> writes JSONL below. "
        "<span id=progress></span><br><textarea id=out placeholder='verdicts.jsonl appears here'></textarea></div>",
    ]
    for row in rows:
        result = by_id.get(row["gold_id"], {"checks": []})
        outcomes = {i: c for i, c in enumerate(result["checks"])}
        tags = "".join(f"<span class=tag>{html.escape(f'{k}={v}')}</span>" for k, v in row["strata"].items())
        parts.append(f"<div class=page id={row['gold_id']}><div>")
        parts.append(f"<div class=meta><b>{row['gold_id']}</b> {html.escape(row['source'])}/{html.escape(row['path'])} · page {row['page_index'] + 1}/{row['page_count']} · "
                     f"fidelity {row['fidelity']} · value {row['value']} · {row['cell']} · {html.escape(str(row['extraction']))} · {html.escape(str(row['text_layer_origin']))}<br>{tags}</div>")
        if row.get("image"):
            parts.append(f"<a href='{row['image']}' target=_blank><img loading=lazy src='{row['image']}' alt='page image'></a>")
        else:
            parts.append("<p><i>no page image rendered</i></p>")
        parts.append("</div><div>")
        for index, check in enumerate(row["checks"]):
            outcome = outcomes.get(index, {})
            raw = outcome.get("raw")
            state = "pass" if raw else ("fail" if raw is False else "")
            detail = {k: v for k, v in check.items() if k not in ("kind", "question", "layer_text", "auto_note")}
            detail_html = " ".join(f"<code>{html.escape(str(k))}={html.escape(json.dumps(v, ensure_ascii=False)[:300])}</code>" for k, v in detail.items())
            auto = f" · raw {'pass' if raw else 'FAIL' if raw is False else 'n/a'} / view {'pass' if outcome.get('view') else 'FAIL' if outcome.get('view') is False else 'n/a'}"
            note = f"<br><i>{html.escape(check['auto_note'])}</i>" if check.get("auto_note") else ""
            key = f"{row['gold_id']}:{index}"
            parts.append(
                f"<div class='check {state}'><b>{check['kind']}</b>{auto}<br><span class=q>{html.escape(check['question'])}</span>{note}<br>{detail_html}"
                f"<div class=verdict>"
                + "".join(f"<label><input type=radio name='{key}' value={v} onchange=save()> {v}</label>" for v in ("confirm", "deny", "skip"))
                + "</div></div>"
            )
        parts.append(f"<div class=verdict>notes: <input type=text name='{row['gold_id']}:notes' style='width:80%' oninput=save()></div>")
        parts.append(f"<pre>{html.escape(row['page_text'][:6000])}</pre></div></div>")
    parts.append(
        "<script>const KEY='corpus-v2-gold-verdicts';function load(){try{const s=JSON.parse(localStorage.getItem(KEY)||'{}');"
        "for(const [k,v] of Object.entries(s)){const els=document.getElementsByName(k);for(const el of els){if(el.type==='radio'){el.checked=(el.value===v)}else{el.value=v}}}}catch(e){}progress()}"
        "function save(){try{const s={};for(const el of document.querySelectorAll('input[type=radio]:checked'))s[el.name]=el.value;"
        "for(const el of document.querySelectorAll('input[type=text]'))if(el.value)s[el.name]=el.value;localStorage.setItem(KEY,JSON.stringify(s))}catch(e){}progress()}"
        "function progress(){const n=document.querySelectorAll('input[type=radio]:checked').length;const t=document.querySelectorAll('.check').length;document.getElementById('progress').textContent=n+' / '+t+' checks answered'}"
        "function exportVerdicts(){const s=JSON.parse(localStorage.getItem(KEY)||'{}');const rows={};for(const [k,v] of Object.entries(s)){const [g,i]=k.split(':');rows[g]=rows[g]||{gold_id:g,verdicts:{},notes:''};"
        "if(i==='notes')rows[g].notes=v;else rows[g].verdicts[i]=v}document.getElementById('out').value=Object.values(rows).map(r=>JSON.stringify(r)).join('\\n')}load();</script>"
    )
    target.write_text("\n".join(parts), encoding="utf-8")


# --------------------------------------------------------------------------- manifest


def run_manifest(args: argparse.Namespace) -> dict:
    rows = load_jsonl(args.output / "scores.jsonl")
    if not rows:
        raise SystemExit("run `hghost-admission score` first")
    _, _, proposed = families_index(args.families)
    exclusions = {row["document_id"] for row in load_jsonl(args.quality / "recommended_exclusions.jsonl")} if args.quality else set()
    documents = []
    streams: dict[str, dict] = {name: {"documents": 0, "tokens": 0} for name in ("main", "specialist", "quarantine", "drop", "validation", "test")}
    for row in rows:
        reasons = []
        split = proposed.get(row["id"])
        stream = row["cell"]
        if row["id"] in exclusions:
            stream = "drop"
            reasons.append("quality_v2_recommended_exclusion")
        if (row.get("credential_dump_indicators") or 0) >= 1:
            stream = "drop"
            reasons.append("credential_dump")
        if stream == "quarantine" and (row.get("non_latin_ratio") or 0) >= 0.3:
            # The fidelity instruments are Latin-script; a faithful Arabic/Hebrew edition is a
            # specialist-stream question (script, tokenizer), not a re-OCR target.
            stream = "specialist"
            reasons.append(f"non-Latin script ({row['non_latin_ratio']:.0%} of letters): specialist, not re-OCR")
        if stream == "quarantine":
            reasons.append(f"fidelity {row['fidelity']} < {FIDELITY_THRESHOLD}; value {row['value']} keeps it: re-OCR")
        elif stream == "drop" and not reasons:
            reasons.append(f"fidelity {row['fidelity']} and value {row['value']} both low")
        elif stream == "specialist" and row["cell"] == "specialist":
            reasons.append(f"faithful (fidelity {row['fidelity']}) but value {row['value']} < {VALUE_THRESHOLD} (tier {row['tier']}: {row['tier_why']})")
        elif stream == "main":
            reasons.append(f"fidelity {row['fidelity']}, value {row['value']}")
        badness = row.get("fidelity_badness") or {}
        if badness:
            top = sorted(badness.items(), key=lambda kv: -kv[1])[:3]
            reasons.append("noise: " + ", ".join(f"{k}={v}" for k, v in top))
        if row.get("layout_badness"):
            reasons.append("layout: " + ", ".join(f"{k}={v}" for k, v in sorted(row["layout_badness"].items(), key=lambda kv: -kv[1])[:2]))
        if not row["in_dataset"]:
            reasons.append("paddleocr_vl candidate, not in corpus-v1")
        if split:
            reasons.append(f"family-clean {split} (artifacts/families)")
            target = split
        else:
            target = stream
        streams[target]["documents"] += 1
        streams[target]["tokens"] += row["tokens"]
        documents.append({
            "id": row["id"], "source": row["source"], "path": row["path"], "tokens": row["tokens"],
            "split": split or ("train" if stream in ("main", "specialist") else None),
            "stream": stream, "cell": row["cell"], "fidelity": row["fidelity"], "value": row["value"],
            "p_corrupt": row["p_corrupt"], "reocr_priority": row["reocr_priority"], "tier": row["tier"],
            "in_dataset": row["in_dataset"], "text_layer_origin": row["text_layer_origin"],
            "running_heads": row.get("running_head_lines", [])[:4], "reasons": reasons,
        })
    scores_sha = hashlib.sha256((args.output / "scores.jsonl").read_bytes()).hexdigest()
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "status": "proposed",
        "built_from": {
            "dataset_manifest": str(args.dataset / "manifest.json"),
            "scores_sha256": scores_sha,
            "families": str(args.families),
            "thresholds": {"fidelity": FIDELITY_THRESHOLD, "value": VALUE_THRESHOLD},
            "tiers": DEFAULT_TIERS if not args.tiers else json.loads(args.tiers.read_text()),
        },
        "representation": {
            "train_view": "reading view (furniture stripped; see research/corpus-v2-admission.md §5)",
            "diplomatic_view": "raw extraction kept beside it for the ghost-noise stream and provenance",
        },
        "streams": streams,
        "splits": {
            "validation": [d["id"] for d in documents if d["split"] == "validation"],
            "test": [d["id"] for d in documents if d["split"] == "test"],
        },
        "documents": documents,
    }
    target = args.output / "proposed-manifest.json"
    target.write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    print(json.dumps(streams))
    return streams


# --------------------------------------------------------------------------- reading-view command


def run_reading_view(args: argparse.Namespace) -> None:
    catalogue = FurnitureCatalogue.load(args.furniture)
    for record in iter_universe(args.dataset, args.records):
        if record["id"] != args.id:
            continue
        heads, _ = running_heads(record["text"].split(FORM_FEED))
        view, transforms = reading_view(record["text"], heads=heads, catalogue=catalogue)
        if args.log:
            for transform in transforms:
                print(json.dumps(transform.as_dict(), ensure_ascii=False))
        else:
            print(view[: args.limit] if args.limit else view)
        print(f"# {len(transforms)} transforms, {len(record['text'])} -> {len(view)} chars, heads={heads[:5]}", file=sys.stderr)
        return
    raise SystemExit(f"document {args.id} not found")


# --------------------------------------------------------------------------- cli


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    def common(command: argparse.ArgumentParser) -> None:
        command.add_argument("--dataset", type=Path, default=Path("artifacts/dataset"))
        command.add_argument("--records", type=Path, default=Path("artifacts/extracted/records"))
        command.add_argument("--output", type=Path, default=Path("artifacts/corpus-v2"))
        command.add_argument("--families", type=Path, default=Path("artifacts/families"))
        command.add_argument("--quality", type=Path, default=Path("artifacts/quality-v2"))
        command.add_argument("--dictionary", type=Path, default=DEFAULT_DICTIONARY)
        command.add_argument(
            "--furniture", type=Path, action="append",
            default=[Path("research/results/haunting-index/furniture-16.jsonl"), Path("research/results/haunting-index/furniture-32.jsonl")],
        )
        command.add_argument("--root", action="append", help="NAME=PATH source root (defaults: cathedral, rat_palace)")
        command.add_argument("--workers", type=int, default=6)

    info = commands.add_parser("pdfinfo", help="cache pdfinfo Producer/Creator per source PDF")
    common(info)

    score = commands.add_parser("score", help="per-document fidelity/value scores")
    common(score)
    score.add_argument("--rebuild-df", action="store_true")
    score.add_argument("--rescore", action="store_true", help="recompute scores from scores.jsonl signal columns (no text pass)")
    score.add_argument("--judge", type=Path, help="optional JSONL of {id, delta} library-likeness judge deltas")
    score.add_argument("--tiers", type=Path, help="optional JSON list of {pattern, tier, why} overriding DEFAULT_TIERS")

    gold = commands.add_parser("gold", help="gold set")
    gold_commands = gold.add_subparsers(dest="gold_command", required=True)
    sample = gold_commands.add_parser("sample")
    common(sample)
    sample.add_argument("--size", type=int, default=300)
    sample.add_argument("--oversample", type=int, default=3)
    sample.add_argument("--expected-documents-per-band", type=int, default=1200)
    sample.add_argument("--seed", type=int, default=2026)
    sample.add_argument("--scale", type=int, default=1000, help="pdftoppm -scale-to for page images")
    check = gold_commands.add_parser("check")
    common(check)

    manifest = commands.add_parser("manifest", help="proposed v2 manifest")
    common(manifest)
    manifest.add_argument("--tiers", type=Path)

    view = commands.add_parser("reading-view", help="print one document's reading view")
    common(view)
    view.add_argument("--id", required=True)
    view.add_argument("--log", action="store_true", help="print the transform log instead of the view")
    view.add_argument("--limit", type=int, default=0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "pdfinfo":
        run_pdfinfo_command(args)
    elif args.command == "score":
        run_score(args)
    elif args.command == "gold":
        if args.gold_command == "sample":
            run_gold_sample(args)
        else:
            run_gold_check(args)
    elif args.command == "manifest":
        run_manifest(args)
    elif args.command == "reading-view":
        run_reading_view(args)


if __name__ == "__main__":
    main()
