from __future__ import annotations

import argparse
import gzip
import html.parser
import json
import os
import posixpath
import re
import subprocess
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from .census import DEFAULT_MODEL, TokenCounter, pdf_pages, sidecar_for
from .common import Document, content_hash, normalize_text, parse_roots, stable_rank, walk_files


SCHEMA_VERSION = 1
PLAIN_TEXT_SUFFIXES = {".txt", ".md", ".text"}
CONTAINER_SUFFIXES = {".epub", ".docx"}
MIN_TEXT_CHARS = 1_000
MIN_CHARS_PER_PAGE = 40


@dataclass(frozen=True)
class ExtractionJob:
    document: Document
    kind: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract PDF and standalone text into resumable, provenance-preserving records."
    )
    parser.add_argument("--root", action="append", required=True, metavar="NAME=PATH")
    parser.add_argument("--output", type=Path, default=Path("artifacts/extracted"))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--tokenizer", default=DEFAULT_MODEL)
    parser.add_argument("--limit", type=int, help="deterministic development subset")
    parser.add_argument("--seed", type=int, default=104)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--only-new",
        action="store_true",
        help="schedule only documents without an existing record",
    )
    parser.add_argument(
        "--no-standalone-text", action="store_true", help="extract PDFs only"
    )
    return parser


def is_derived_sidecar(path: Path) -> bool:
    name = path.name.casefold()
    return name.endswith("_djvu.txt") or name.endswith("_hocr_searchtext.txt.gz")


def is_redundant_text_pdf(path: Path) -> bool:
    if path.suffix.casefold() != ".pdf" or not path.stem.casefold().endswith("_text"):
        return False
    return path.with_name(f"{path.stem[:-5]}.pdf").is_file()


def discover(args: argparse.Namespace) -> list[ExtractionJob]:
    jobs: list[ExtractionJob] = []
    for root in parse_roots(args.root):
        for item in walk_files(root):
            suffix = item.path.suffix.casefold()
            if suffix == ".pdf" and not is_redundant_text_pdf(item.path):
                jobs.append(ExtractionJob(item, "pdf"))
            elif (
                not args.no_standalone_text
                and suffix in PLAIN_TEXT_SUFFIXES
                and not item.path.name.startswith(".")
                and not is_derived_sidecar(item.path)
            ):
                jobs.append(ExtractionJob(item, "plain_text"))
            elif suffix in CONTAINER_SUFFIXES:
                jobs.append(ExtractionJob(item, suffix[1:]))
    jobs.sort(key=lambda job: (job.document.source, job.document.relative_path))
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError("--limit must be positive")
        jobs = sorted(
            jobs,
            key=lambda job: stable_rank(
                args.seed, f"{job.document.source}/{job.document.relative_path}"
            ),
        )[: args.limit]
    return jobs


def output_path(output: Path, job: ExtractionJob) -> Path:
    return output / "records" / job.document.source / f"{job.document.document_id}.json.gz"


def read_pdf_text(path: Path, timeout: int) -> tuple[str, str]:
    sidecar, extraction = sidecar_for(path)
    if sidecar is not None:
        opener = gzip.open if sidecar.suffix.casefold() == ".gz" else open
        with opener(sidecar, "rb") as stream:
            return stream.read().decode("utf-8", "replace"), extraction
    with tempfile.TemporaryDirectory(prefix="hghost-extract-") as temp_dir:
        text_path = Path(temp_dir) / "document.txt"
        try:
            result = subprocess.run(
                ["pdftotext", "-q", "-enc", "UTF-8", str(path), str(text_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"pdftotext timeout after {timeout}s") from exc
        if result.returncode != 0 and not text_path.exists():
            detail = result.stderr.decode("utf-8", "replace").strip()[-500:]
            raise RuntimeError(f"pdftotext exit {result.returncode}: {detail}")
        return text_path.read_text(encoding="utf-8", errors="replace"), extraction


class _HTMLTextExtractor(html.parser.HTMLParser):
    block_tags = {
        "address",
        "article",
        "aside",
        "blockquote",
        "br",
        "div",
        "figcaption",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "main",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "svg"}:
            self.ignored_depth += 1
        elif tag in self.block_tags and not self.ignored_depth:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "svg"} and self.ignored_depth:
            self.ignored_depth -= 1
        elif tag in self.block_tags and not self.ignored_depth:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.ignored_depth:
            self.parts.append(data)

    def text(self) -> str:
        return "".join(self.parts)


def html_to_text(value: bytes) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(value.decode("utf-8", "replace"))
    return parser.text()


def read_epub_text(path: Path) -> str:
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(path) as archive:
        container = ET.fromstring(archive.read("META-INF/container.xml"))
        rootfile = next(
            element
            for element in container.iter()
            if element.tag.rsplit("}", 1)[-1] == "rootfile"
        ).attrib["full-path"]
        package = ET.fromstring(archive.read(rootfile))
        manifest: dict[str, str] = {}
        for element in package.iter():
            if element.tag.rsplit("}", 1)[-1] == "item":
                manifest[element.attrib["id"]] = element.attrib["href"]
        base = posixpath.dirname(rootfile)
        chapters: list[str] = []
        for element in package.iter():
            if element.tag.rsplit("}", 1)[-1] != "itemref":
                continue
            href = manifest.get(element.attrib.get("idref", ""))
            if href:
                chapters.append(html_to_text(archive.read(posixpath.normpath(posixpath.join(base, href)))))
        return "\n\n\f\n\n".join(chapters)


def read_docx_text(path: Path) -> str:
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
    paragraphs: list[str] = []
    for paragraph in document.iter():
        if paragraph.tag.rsplit("}", 1)[-1] != "p":
            continue
        parts = [
            node.text or ""
            for node in paragraph.iter()
            if node.tag.rsplit("}", 1)[-1] in {"t", "tab", "br"}
        ]
        paragraphs.append("".join(parts))
    return "\n\n".join(paragraphs)


def atomic_json_gzip(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                compressed.write(
                    (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
                        "utf-8"
                    )
                )
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def extract_one(
    job: ExtractionJob,
    destination: Path,
    counter: TokenCounter,
    timeout: int,
    overwrite: bool,
) -> dict:
    document = job.document
    target = output_path(destination, job)
    if target.is_file() and target.stat().st_size > 20 and not overwrite:
        return {
            "document_id": document.document_id,
            "source": document.source,
            "relative_path": document.relative_path,
            "status": "skipped_existing",
            "record_path": str(target.relative_to(destination)),
        }
    pages = pdf_pages(document.path, timeout) if job.kind == "pdf" else None
    extraction = job.kind
    error = ""
    raw_text = ""
    try:
        if job.kind == "pdf":
            raw_text, extraction = read_pdf_text(document.path, timeout)
        elif job.kind == "plain_text":
            raw_text = document.path.read_text(encoding="utf-8", errors="replace")
        elif job.kind == "epub":
            raw_text = read_epub_text(document.path)
        elif job.kind == "docx":
            raw_text = read_docx_text(document.path)
        else:
            raise RuntimeError(f"unsupported extraction kind {job.kind!r}")
    except Exception as exc:
        error = str(exc)
    text = normalize_text(raw_text) if raw_text else ""
    chars = len(text)
    words = len(re.findall(r"\S+", text))
    alpha_ratio = sum(char.isalpha() for char in text) / max(chars, 1)
    replacement_ratio = text.count("\ufffd") / max(chars, 1)
    threshold = max(MIN_TEXT_CHARS, (pages or 1) * MIN_CHARS_PER_PAGE)
    ready = not error and chars >= threshold and alpha_ratio >= 0.25
    if error:
        status = "error"
    elif ready:
        status = "ready"
    elif job.kind == "pdf":
        status = "needs_ocr"
    else:
        status = "rejected_low_text"
    tokens = counter.count(text) if ready else 0
    record = {
        "schema_version": SCHEMA_VERSION,
        "document_id": document.document_id,
        "source": document.source,
        "relative_path": document.relative_path,
        "original_bytes": document.size,
        "kind": job.kind,
        "pages": pages,
        "extraction": extraction,
        "status": status,
        "error": error,
        "chars": chars,
        "words": words,
        "tokens": tokens,
        "token_count_kind": counter.kind,
        "alpha_ratio": alpha_ratio,
        "replacement_ratio": replacement_ratio,
        "content_sha256": content_hash(text) if ready else None,
        "text": text if ready else "",
    }
    atomic_json_gzip(target, record)
    return {key: value for key, value in record.items() if key != "text"} | {
        "record_path": str(target.relative_to(destination))
    }


def run(args: argparse.Namespace) -> dict[str, int]:
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    counter = TokenCounter(args.tokenizer or None)
    jobs = discover(args)
    if getattr(args, "only_new", False) and not args.overwrite:
        jobs = [job for job in jobs if not output_path(output, job).is_file()]
    statuses: dict[str, int] = {}
    manifest = output / "last_run.jsonl"
    with manifest.open("w", encoding="utf-8") as manifest_stream:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(
                    extract_one, job, output, counter, args.timeout, args.overwrite
                ): job
                for job in jobs
            }
            for completed, future in enumerate(as_completed(futures), start=1):
                job = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    result = {
                        "document_id": job.document.document_id,
                        "source": job.document.source,
                        "relative_path": job.document.relative_path,
                        "status": "worker_error",
                        "error": str(exc),
                    }
                status = str(result["status"])
                statuses[status] = statuses.get(status, 0) + 1
                manifest_stream.write(json.dumps(result, ensure_ascii=False) + "\n")
                manifest_stream.flush()
                print(
                    f"[{completed:>5}/{len(jobs)}] {status:<18} "
                    f"{result['source']}/{result['relative_path']}",
                    flush=True,
                )
    summary = {
        "jobs": len(jobs),
        "token_count_kind": counter.kind,
        "statuses": dict(sorted(statuses.items())),
    }
    (output / "last_run_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return statuses


def main() -> None:
    run(build_parser().parse_args())


if __name__ == "__main__":
    main()
