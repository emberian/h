from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


MIB = 1024 * 1024
GIB = 1024 * MIB


@dataclass(frozen=True)
class RootSpec:
    name: str
    path: Path


@dataclass(frozen=True)
class Document:
    source: str
    root: Path
    path: Path
    size: int

    @property
    def relative_path(self) -> str:
        return str(self.path.relative_to(self.root))

    @property
    def document_id(self) -> str:
        value = f"{self.source}\0{self.relative_path}".encode("utf-8", "surrogatepass")
        return hashlib.sha256(value).hexdigest()[:24]


def parse_roots(values: Iterable[str]) -> list[RootSpec]:
    roots: list[RootSpec] = []
    names: set[str] = set()
    for raw in values:
        if "=" not in raw:
            raise ValueError(f"root must be NAME=PATH, got {raw!r}")
        name, path_text = raw.split("=", 1)
        name = name.strip()
        path = Path(path_text).expanduser().resolve()
        if not name or name in names:
            raise ValueError(f"root name must be nonempty and unique: {name!r}")
        if not path.is_dir():
            raise ValueError(f"root is not a directory: {path}")
        names.add(name)
        roots.append(RootSpec(name=name, path=path))
    return roots


def walk_files(root: RootSpec) -> Iterator[Document]:
    for directory, dirnames, filenames in os.walk(root.path):
        dirnames.sort()
        filenames.sort()
        base = Path(directory)
        for filename in filenames:
            path = base / filename
            try:
                stat = path.stat()
            except OSError:
                continue
            if path.is_file():
                yield Document(root.name, root.path, path, stat.st_size)


def size_stratum(size: int) -> str:
    if size < MIB:
        return "00_lt_1MiB"
    if size < 10 * MIB:
        return "01_1_to_10MiB"
    if size < 100 * MIB:
        return "02_10_to_100MiB"
    if size < GIB:
        return "03_100MiB_to_1GiB"
    return "04_ge_1GiB"


def stable_rank(seed: int, value: str) -> bytes:
    return hashlib.blake2b(
        f"{seed}\0{value}".encode("utf-8", "surrogatepass"), digest_size=16
    ).digest()


_SPACE_BEFORE_NEWLINE = re.compile(r"[ \t]+\n")
_MANY_BLANKS = re.compile(r"\n{4,}")
_WORD_HYPHEN_BREAK = re.compile(r"(?<=[A-Za-z])-[ \t]*\n(?=[a-z])")
_SOFT_HYPHEN = re.compile("\u00ad")


def normalize_text(text: str, *, dehyphenate: bool = True) -> str:
    """Conservative PDF cleanup that preserves paragraph and page structure."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    text = _SOFT_HYPHEN.sub("", text)
    text = unicodedata.normalize("NFC", text)
    if dehyphenate:
        text = _WORD_HYPHEN_BREAK.sub("", text)
    text = _SPACE_BEFORE_NEWLINE.sub("\n", text)
    text = _MANY_BLANKS.sub("\n\n\n", text)
    return text.strip()


def content_hash(text: str) -> str:
    canonical = unicodedata.normalize("NFKC", text).casefold()
    canonical = re.sub(r"\s+", " ", canonical).strip()
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def human_bytes(value: int | float) -> str:
    number = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(number) < 1024 or unit == "TiB":
            return f"{number:.2f} {unit}"
        number /= 1024
    raise AssertionError("unreachable")


def human_int(value: int | float) -> str:
    return f"{round(value):,}"

