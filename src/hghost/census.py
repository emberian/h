from __future__ import annotations

import argparse
import codecs
import csv
import gzip
import json
import math
import random
import re
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import BinaryIO, Iterable

from .common import (
    Document,
    RootSpec,
    human_bytes,
    human_int,
    parse_roots,
    size_stratum,
    stable_rank,
    walk_files,
)


DEFAULT_MODEL = "tiiuae/Falcon-H1-Tiny-90M-Base"
TEXT_LAYER_MIN_CHARS = 1_000
TEXT_LAYER_MIN_CHARS_PER_PAGE = 40


@dataclass
class SampleResult:
    document_id: str
    source: str
    relative_path: str
    pdf_bytes: int
    stratum: str
    pages: int | None
    extraction: str
    extracted_bytes: int
    chars: int
    words: int
    tokens: int
    token_count_kind: str
    alpha_ratio: float
    replacement_ratio: float
    text_bearing: bool
    error: str


class TokenCounter:
    def __init__(self, model_or_file: str | None):
        self.kind = "chars_div_4_proxy"
        self.tokenizer = None
        if not model_or_file:
            return
        try:
            from tokenizers import Tokenizer

            path = Path(model_or_file).expanduser()
            self.tokenizer = (
                Tokenizer.from_file(str(path))
                if path.is_file()
                else Tokenizer.from_pretrained(model_or_file)
            )
            self.kind = f"tokenizers:{model_or_file}"
        except Exception as exc:  # pragma: no cover - depends on network/cache
            raise RuntimeError(f"could not load tokenizer {model_or_file!r}: {exc}") from exc

    def count(self, text: str) -> int:
        if self.tokenizer is None:
            return round(len(text) / 4)
        return len(self.tokenizer.encode(text, add_special_tokens=False).ids)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inventory PDF corpora and estimate Falcon-H1 tokens by stratified sampling."
    )
    parser.add_argument(
        "--root",
        action="append",
        required=True,
        metavar="NAME=PATH",
        help="corpus root; repeat for multiple sources",
    )
    parser.add_argument("--output", type=Path, default=Path("artifacts/census"))
    parser.add_argument(
        "--samples-per-stratum",
        type=int,
        default=20,
        help="sample count for every source × PDF-size stratum",
    )
    parser.add_argument("--seed", type=int, default=104)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument(
        "--tokenizer",
        default=DEFAULT_MODEL,
        help="Hub model id or tokenizer.json; pass an empty string for chars/4 proxy",
    )
    return parser


def inventory(roots: Iterable[RootSpec]) -> tuple[list[Document], list[Document]]:
    files: list[Document] = []
    pdfs: list[Document] = []
    for root in roots:
        for document in walk_files(root):
            files.append(document)
            if document.path.suffix.casefold() == ".pdf":
                pdfs.append(document)
    return files, pdfs


def select_sample(pdfs: list[Document], count: int, seed: int) -> list[Document]:
    groups: dict[tuple[str, str], list[Document]] = defaultdict(list)
    for pdf in pdfs:
        groups[(pdf.source, size_stratum(pdf.size))].append(pdf)
    selected: list[Document] = []
    for key in sorted(groups):
        ranked = sorted(
            groups[key], key=lambda doc: stable_rank(seed, f"{doc.source}/{doc.relative_path}")
        )
        selected.extend(ranked[:count])
    return selected


def sidecar_for(pdf: Path) -> tuple[Path | None, str]:
    candidates = (
        (pdf.with_name(f"{pdf.stem}_djvu.txt"), "ia_djvu_txt"),
        (pdf.with_name(f"{pdf.stem}_hocr_searchtext.txt.gz"), "ia_hocr_searchtext"),
    )
    for path, kind in candidates:
        if path.is_file():
            return path, kind
    return None, "pdftotext"


_PAGES_RE = re.compile(r"^Pages:\s*(\d+)\s*$", re.MULTILINE)


def pdf_pages(path: Path, timeout: int) -> int | None:
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
            text=True,
            errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = _PAGES_RE.search(result.stdout)
    return int(match.group(1)) if match else None


def inspect_stream(stream: BinaryIO, counter: TokenCounter) -> tuple[int, int, int, int, float, float]:
    decoder = codecs.getincrementaldecoder("utf-8")("replace")
    extracted_bytes = chars = words = tokens = alpha = replacements = 0
    carry = ""
    while chunk := stream.read(1024 * 1024):
        extracted_bytes += len(chunk)
        text = decoder.decode(chunk)
        if not text:
            continue
        chars += len(text)
        alpha += sum(char.isalpha() for char in text)
        replacements += text.count("\ufffd")
        token_text = carry + text
        split = max(token_text.rfind("\n"), token_text.rfind(" "))
        if split < 0 or len(token_text) - split > 256:
            split = len(token_text)
        ready, carry = token_text[:split], token_text[split:]
        words += len(re.findall(r"\S+", ready))
        tokens += counter.count(ready)
    tail = decoder.decode(b"", final=True)
    if tail:
        chars += len(tail)
        alpha += sum(char.isalpha() for char in tail)
        replacements += tail.count("\ufffd")
        carry += tail
    if carry:
        words += len(re.findall(r"\S+", carry))
        tokens += counter.count(carry)
    denominator = max(chars, 1)
    return extracted_bytes, chars, words, tokens, alpha / denominator, replacements / denominator


def inspect_pdf(document: Document, counter: TokenCounter, timeout: int) -> SampleResult:
    pages = pdf_pages(document.path, timeout)
    sidecar, extraction = sidecar_for(document.path)
    error = ""
    try:
        if sidecar is not None:
            opener = gzip.open if sidecar.suffix.casefold() == ".gz" else open
            with opener(sidecar, "rb") as stream:
                metrics = inspect_stream(stream, counter)
        else:
            with tempfile.TemporaryDirectory(prefix="hghost-census-") as temp_dir:
                output = Path(temp_dir) / "text.txt"
                try:
                    result = subprocess.run(
                        ["pdftotext", "-q", "-enc", "UTF-8", "-nopgbrk", str(document.path), str(output)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE,
                        timeout=timeout,
                        check=False,
                    )
                except subprocess.TimeoutExpired:
                    raise RuntimeError(f"pdftotext timeout after {timeout}s")
                if result.returncode != 0 and not output.exists():
                    detail = result.stderr.decode("utf-8", "replace").strip()[-500:]
                    raise RuntimeError(f"pdftotext exit {result.returncode}: {detail}")
                with output.open("rb") as stream:
                    metrics = inspect_stream(stream, counter)
    except Exception as exc:
        metrics = (0, 0, 0, 0, 0.0, 0.0)
        error = str(exc)
    extracted_bytes, chars, words, tokens, alpha_ratio, replacement_ratio = metrics
    page_threshold = (pages or 1) * TEXT_LAYER_MIN_CHARS_PER_PAGE
    text_bearing = chars >= max(TEXT_LAYER_MIN_CHARS, page_threshold) and alpha_ratio >= 0.25
    return SampleResult(
        document_id=document.document_id,
        source=document.source,
        relative_path=document.relative_path,
        pdf_bytes=document.size,
        stratum=size_stratum(document.size),
        pages=pages,
        extraction=extraction,
        extracted_bytes=extracted_bytes,
        chars=chars,
        words=words,
        tokens=tokens,
        token_count_kind=counter.kind,
        alpha_ratio=alpha_ratio,
        replacement_ratio=replacement_ratio,
        text_bearing=text_bearing,
        error=error,
    )


def ratio_bootstrap(
    results: list[SampleResult], population_bytes: int, seed: int, rounds: int = 2_000
) -> tuple[float, float, float]:
    usable = [row for row in results if not row.error]
    if not usable:
        return 0.0, 0.0, 0.0
    estimate = sum(row.tokens for row in usable) / sum(row.pdf_bytes for row in usable) * population_bytes
    if len(usable) == 1:
        return estimate, estimate, estimate
    rng = random.Random(seed)
    draws: list[float] = []
    for _ in range(rounds):
        sample = [rng.choice(usable) for _ in usable]
        draws.append(sum(row.tokens for row in sample) / sum(row.pdf_bytes for row in sample) * population_bytes)
    draws.sort()
    return estimate, draws[math.floor(0.025 * (rounds - 1))], draws[math.floor(0.975 * (rounds - 1))]


def summarize(files: list[Document], pdfs: list[Document], results: list[SampleResult], seed: int) -> dict:
    by_extension: Counter[str] = Counter()
    bytes_by_extension: Counter[str] = Counter()
    roots: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0, "pdfs": 0, "pdf_bytes": 0})
    for item in files:
        suffix = item.path.suffix.casefold() or "[none]"
        by_extension[suffix] += 1
        bytes_by_extension[suffix] += item.size
        roots[item.source]["files"] += 1
        roots[item.source]["bytes"] += item.size
        if suffix == ".pdf":
            roots[item.source]["pdfs"] += 1
            roots[item.source]["pdf_bytes"] += item.size

    population: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"pdfs": 0, "bytes": 0})
    for pdf in pdfs:
        key = (pdf.source, size_stratum(pdf.size))
        population[key]["pdfs"] += 1
        population[key]["bytes"] += pdf.size
    samples: dict[tuple[str, str], list[SampleResult]] = defaultdict(list)
    for result in results:
        samples[(result.source, result.stratum)].append(result)

    strata: list[dict] = []
    total_estimate = total_low = total_high = 0.0
    estimated_text_bearing_pdfs = 0.0
    estimated_needs_ocr_pdfs = 0.0
    for index, key in enumerate(sorted(population)):
        pop = population[key]
        rows = samples.get(key, [])
        estimate, low, high = ratio_bootstrap(rows, pop["bytes"], seed + index)
        usable = [row for row in rows if not row.error]
        text_count = sum(row.text_bearing for row in usable)
        text_fraction = text_count / len(usable) if usable else 0.0
        estimated_text_here = pop["pdfs"] * text_fraction
        estimated_ocr_here = pop["pdfs"] - estimated_text_here
        strata.append(
            {
                "source": key[0],
                "stratum": key[1],
                "population_pdfs": pop["pdfs"],
                "population_pdf_bytes": pop["bytes"],
                "sampled": len(rows),
                "usable": len(usable),
                "text_bearing": text_count,
                "estimated_text_bearing_pdfs": round(estimated_text_here),
                "estimated_needs_ocr_pdfs": round(estimated_ocr_here),
                "estimated_tokens": round(estimate),
                "estimated_tokens_low_95": round(low),
                "estimated_tokens_high_95": round(high),
            }
        )
        total_estimate += estimate
        total_low += low
        total_high += high
        estimated_text_bearing_pdfs += estimated_text_here
        estimated_needs_ocr_pdfs += estimated_ocr_here
    return {
        "roots": dict(sorted(roots.items())),
        "extensions": [
            {"extension": suffix, "files": count, "bytes": bytes_by_extension[suffix]}
            for suffix, count in by_extension.most_common()
        ],
        "pdf_total": {"files": len(pdfs), "bytes": sum(pdf.size for pdf in pdfs)},
        "sample_total": {
            "selected": len(results),
            "usable": sum(not row.error for row in results),
            "text_bearing": sum(row.text_bearing for row in results if not row.error),
            "used_ia_sidecar": sum(row.extraction.startswith("ia_") for row in results),
            "estimated_text_bearing_pdfs": round(estimated_text_bearing_pdfs),
            "estimated_needs_ocr_pdfs": round(estimated_needs_ocr_pdfs),
        },
        "token_estimate": {
            "estimate": round(total_estimate),
            "low_95_sum_of_strata": round(total_low),
            "high_95_sum_of_strata": round(total_high),
            "note": "PDF-only ratio estimate; interval is the sum of per-stratum bootstrap bounds.",
        },
        "strata": strata,
    }


def write_csv(path: Path, rows: Iterable[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def render_report(summary: dict, counter_kind: str) -> str:
    estimate = summary["token_estimate"]
    sample = summary["sample_total"]
    lines = [
        "# h ghost corpus census",
        "",
        "## Headline",
        "",
        f"- PDF inventory: **{human_int(summary['pdf_total']['files'])} files / {human_bytes(summary['pdf_total']['bytes'])}**",
        f"- Estimated PDF text: **{human_int(estimate['estimate'])} Falcon-H1 tokens**",
        f"- Indicative stratified range: **{human_int(estimate['low_95_sum_of_strata'])}–{human_int(estimate['high_95_sum_of_strata'])} tokens**",
        f"- Samples: **{sample['usable']}/{sample['selected']} usable**, **{sample['text_bearing']} text-bearing**, **{sample['used_ia_sidecar']} using IA OCR sidecars**",
        f"- Population projection: **~{human_int(sample['estimated_text_bearing_pdfs'])} text-bearing PDFs / ~{human_int(sample['estimated_needs_ocr_pdfs'])} OCR candidates**",
        f"- Token counter: `{counter_kind}`",
        "",
        "The estimate covers PDFs only. EPUB, HTML, and standalone text should be inventoried separately during final extraction. Image-only PDFs contribute approximately zero until OCR is run.",
        "",
        "## Roots",
        "",
        "| Source | Files | Total bytes | PDFs | PDF bytes |",
        "|---|---:|---:|---:|---:|",
    ]
    for source, values in summary["roots"].items():
        lines.append(
            f"| {source} | {human_int(values['files'])} | {human_bytes(values['bytes'])} | {human_int(values['pdfs'])} | {human_bytes(values['pdf_bytes'])} |"
        )
    lines.extend(
        [
            "",
            "## Sampling strata",
            "",
            "| Source | PDF size | Population | Sample | Text-bearing | Projected OCR | Estimated H1 tokens |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in summary["strata"]:
        lines.append(
            f"| {row['source']} | {row['stratum']} | {human_int(row['population_pdfs'])} | {row['usable']}/{row['sampled']} | {row['text_bearing']} | ~{human_int(row['estimated_needs_ocr_pdfs'])} | {human_int(row['estimated_tokens'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Treat the interval as a planning estimate, not a guarantee: PDF size is weakly related to text volume, OCR quality varies, and each source/size cell has a modest sample. Increase `--samples-per-stratum` before committing to a from-scratch token budget.",
            "",
        ]
    )
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict:
    if shutil.which("pdfinfo") is None or shutil.which("pdftotext") is None:
        raise RuntimeError("Poppler's pdfinfo and pdftotext must be installed")
    if args.samples_per_stratum < 1 or args.workers < 1:
        raise ValueError("sample and worker counts must be positive")
    roots = parse_roots(args.root)
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    files, pdfs = inventory(roots)

    write_csv(
        output / "inventory.csv",
        (
            {
                "document_id": item.document_id,
                "source": item.source,
                "relative_path": item.relative_path,
                "bytes": item.size,
                "extension": item.path.suffix.casefold() or "[none]",
            }
            for item in files
        ),
        ["document_id", "source", "relative_path", "bytes", "extension"],
    )

    counter = TokenCounter(args.tokenizer or None)
    chosen = select_sample(pdfs, args.samples_per_stratum, args.seed)
    results: list[SampleResult] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(inspect_pdf, doc, counter, args.timeout): doc for doc in chosen}
        for completed, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            results.append(result)
            print(
                f"[{completed:>3}/{len(chosen)}] {result.source} {result.stratum} "
                f"tokens={result.tokens:,} text={result.text_bearing} {result.relative_path}",
                flush=True,
            )
    results.sort(key=lambda row: (row.source, row.stratum, row.relative_path))
    fields = list(asdict(results[0]).keys()) if results else list(SampleResult.__annotations__)
    write_csv(output / "pdf_sample.csv", (asdict(row) for row in results), fields)
    summary = summarize(files, pdfs, results, args.seed)
    summary["settings"] = {
        "roots": [{"name": root.name, "path": str(root.path)} for root in roots],
        "samples_per_stratum": args.samples_per_stratum,
        "seed": args.seed,
        "workers": args.workers,
        "tokenizer": args.tokenizer or None,
        "token_count_kind": counter.kind,
    }
    with (output / "summary.json").open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    (output / "report.md").write_text(render_report(summary, counter.kind), encoding="utf-8")
    print(f"wrote {output / 'report.md'}")
    return summary


def main() -> None:
    run(build_parser().parse_args())


if __name__ == "__main__":
    main()
