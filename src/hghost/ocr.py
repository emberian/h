from __future__ import annotations

import argparse
import fnmatch
import gzip
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .census import DEFAULT_MODEL, TokenCounter
from .common import content_hash, normalize_text, parse_roots
from .extract import MIN_CHARS_PER_PAGE, MIN_TEXT_CHARS, atomic_json_gzip


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OCR records marked needs_ocr using text-only OCRmyPDF sidecars."
    )
    parser.add_argument("--root", action="append", required=True, metavar="NAME=PATH")
    parser.add_argument("--records", type=Path, default=Path("artifacts/extracted/records"))
    parser.add_argument("--sidecars", type=Path, default=Path("artifacts/ocr-sidecars"))
    parser.add_argument("--workers", type=int, default=2, help="PDFs processed concurrently")
    parser.add_argument(
        "--jobs-per-document", type=int, default=4, help="OCRmyPDF page workers per PDF"
    )
    parser.add_argument("--timeout", type=int, default=14_400)
    parser.add_argument("--language", action="append", default=[], help="Tesseract language; repeat to combine")
    parser.add_argument(
        "--language-map",
        type=Path,
        help="ordered JSON rules: [{\"pattern\": \"source/path/**\", \"languages\": [\"eng\"]}]",
    )
    parser.add_argument("--tokenizer", default=DEFAULT_MODEL)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-deskew", action="store_true")
    parser.add_argument("--no-rotate", action="store_true")
    parser.add_argument("--oversample", type=int, default=300)
    parser.add_argument(
        "--trust-output",
        action="store_true",
        help="mark volume-valid OCR as ready without a separate quality review",
    )
    return parser


def load_record(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def atomic_gzip_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                compressed.write(text.encode("utf-8"))
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def discover(records: Path, limit: int | None) -> list[tuple[Path, dict]]:
    jobs: list[tuple[Path, dict]] = []
    for path in sorted(records.rglob("*.json.gz")):
        record = load_record(path)
        if record.get("status") == "needs_ocr":
            jobs.append((path, record))
    return jobs[:limit] if limit is not None else jobs


def ocr_command(
    args: argparse.Namespace, input_pdf: Path, sidecar: Path, languages: list[str]
) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "ocrmypdf",
        "--output-type",
        "none",
        "--sidecar",
        str(sidecar),
        "--mode",
        "force",
        "--jobs",
        str(args.jobs_per_document),
        "--language",
        "+".join(languages),
        "--oversample",
        str(args.oversample),
        "--tesseract-timeout",
        "300",
        "--quiet",
    ]
    if not args.no_deskew:
        command.append("--deskew")
    if not args.no_rotate:
        command.append("--rotate-pages")
    command.extend([str(input_pdf), "-"])
    return command


def load_language_rules(path: Path | None) -> list[dict]:
    if path is None:
        return []
    value = json.loads(path.expanduser().read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("language map must be a JSON list")
    rules: list[dict] = []
    for rule in value:
        if not isinstance(rule, dict) or not isinstance(rule.get("pattern"), str):
            raise ValueError(f"invalid language rule: {rule!r}")
        languages = rule.get("languages")
        if not isinstance(languages, list) or not languages or not all(
            isinstance(language, str) and language for language in languages
        ):
            raise ValueError(f"invalid languages in rule: {rule!r}")
        rules.append({"pattern": rule["pattern"], "languages": languages})
    return rules


def languages_for(record: dict, rules: list[dict], fallback: list[str]) -> list[str]:
    location = f"{record['source']}/{record['relative_path']}"
    for rule in rules:
        if fnmatch.fnmatchcase(location.casefold(), rule["pattern"].casefold()):
            return list(rule["languages"])
    return fallback


def process_one(
    args: argparse.Namespace,
    record_path: Path,
    record: dict,
    roots: dict[str, Path],
    sidecars: Path,
    counter: TokenCounter,
    language_rules: list[dict],
) -> dict:
    source = record["source"]
    if source not in roots:
        raise RuntimeError(f"no --root supplied for source {source!r}")
    input_pdf = roots[source] / record["relative_path"]
    languages = languages_for(record, language_rules, args.language or ["eng"])
    sidecar = sidecars / source / f"{record['document_id']}.txt.gz"
    text = ""
    if sidecar.is_file() and not args.overwrite:
        with gzip.open(sidecar, "rt", encoding="utf-8", errors="replace") as stream:
            text = stream.read()
        extraction = "ocrmypdf_tesseract_cached"
    else:
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="hghost-ocr-") as temp_dir:
            raw_sidecar = Path(temp_dir) / "ocr.txt"
            try:
                result = subprocess.run(
                    ocr_command(args, input_pdf, raw_sidecar, languages),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    timeout=args.timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                return {"status": "ocr_error", "error": f"timeout after {args.timeout}s"}
            if result.returncode != 0 or not raw_sidecar.is_file():
                detail = result.stderr.decode("utf-8", "replace").strip()[-1_000:]
                return {
                    "status": "ocr_error",
                    "error": f"ocrmypdf exit {result.returncode}: {detail}",
                }
            text = raw_sidecar.read_text(encoding="utf-8", errors="replace")
        atomic_gzip_text(sidecar, text)
        extraction = "ocrmypdf_tesseract"

    text = normalize_text(text)
    chars = len(text)
    alpha_ratio = sum(char.isalpha() for char in text) / max(chars, 1)
    replacement_ratio = text.count("\ufffd") / max(chars, 1)
    threshold = max(MIN_TEXT_CHARS, (record.get("pages") or 1) * MIN_CHARS_PER_PAGE)
    ready = chars >= threshold and alpha_ratio >= 0.25
    record.update(
        {
            "status": (
                "ready" if ready and args.trust_output else "ocr_unreviewed" if ready else "ocr_low_text"
            ),
            "error": "" if ready else "OCR output did not pass text-volume/quality threshold",
            "extraction": extraction,
            "chars": chars,
            "words": len(text.split()),
            "tokens": counter.count(text) if ready else 0,
            "token_count_kind": counter.kind,
            "alpha_ratio": alpha_ratio,
            "replacement_ratio": replacement_ratio,
            "content_sha256": content_hash(text) if ready else None,
            "text": text if ready else "",
            "ocr_sidecar": str(sidecar),
            "ocr_languages": languages,
        }
    )
    atomic_json_gzip(record_path, record)
    return {
        "status": record["status"],
        "chars": chars,
        "tokens": record["tokens"],
        "sidecar": str(sidecar),
        "error": record["error"],
    }


def run(args: argparse.Namespace) -> dict:
    try:
        import ocrmypdf  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("ocrmypdf is not installed; run `uv sync --extra ocr`") from exc
    if args.workers < 1 or args.jobs_per_document < 1:
        raise ValueError("worker counts must be positive")
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be positive")
    roots = {spec.name: spec.path for spec in parse_roots(args.root)}
    records = args.records.expanduser().resolve()
    sidecars = args.sidecars.expanduser().resolve()
    counter = TokenCounter(args.tokenizer or None)
    language_rules = load_language_rules(args.language_map)
    jobs = discover(records, args.limit)
    statuses: Counter[str] = Counter()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                process_one, args, path, record, roots, sidecars, counter, language_rules
            ): (
                path,
                record,
            )
            for path, record in jobs
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            _, record = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {"status": "worker_error", "error": str(exc)}
            statuses[result["status"]] += 1
            print(
                f"[{completed:>5}/{len(jobs)}] {result['status']:<14} "
                f"{record['source']}/{record['relative_path']} {result.get('error', '')}",
                flush=True,
            )
    summary = {
        "jobs": len(jobs),
        "languages": args.language or ["eng"],
        "language_map": str(args.language_map) if args.language_map else None,
        "statuses": dict(sorted(statuses.items())),
    }
    sidecars.mkdir(parents=True, exist_ok=True)
    (sidecars / "last_run_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    print(json.dumps(run(build_parser().parse_args()), indent=2))


if __name__ == "__main__":
    main()
