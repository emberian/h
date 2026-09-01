from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .build_dataset import read_record as load_record
from .census import DEFAULT_MODEL, TokenCounter
from .common import content_hash, normalize_text, parse_roots
from .extract import MIN_CHARS_PER_PAGE, MIN_TEXT_CHARS, atomic_json_gzip


IGNORED_BLOCK_LABELS = {
    "aside_text",
    "footer",
    "footer_image",
    "header",
    "header_image",
    "number",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run resumable PaddleOCR-VL 1.6 over records marked needs_ocr."
    )
    parser.add_argument("--root", action="append", required=True, metavar="NAME=PATH")
    parser.add_argument("--records", type=Path, default=Path("artifacts/extracted/records"))
    parser.add_argument("--raw-output", type=Path, default=Path("artifacts/paddle-ocr/raw"))
    parser.add_argument("--server-url", default="http://127.0.0.1:8111/")
    parser.add_argument("--model", default="PaddlePaddle/PaddleOCR-VL-1.6")
    parser.add_argument("--tokenizer", default=DEFAULT_MODEL)
    parser.add_argument("--region-concurrency", type=int, default=8)
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--min-pages",
        type=int,
        default=4,
        help="skip tiny documents by default; use 1 to include single-page material",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=80,
        help="bound time-to-first-result for very large scans",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--ocr-image-blocks",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="OCR regions the layout model labels as images; important for noisy scans",
    )
    return parser


def discover(
    records: Path,
    limit: int | None,
    overwrite: bool,
    min_pages: int = 4,
    max_pages: int = 80,
) -> list[tuple[Path, dict]]:
    jobs: list[tuple[Path, dict]] = []
    for path in sorted(records.rglob("*.json.gz")):
        record = load_record(path)
        if record.get("status") == "needs_ocr" or (
            overwrite and str(record.get("extraction", "")).startswith("paddleocr_vl")
        ):
            pages = int(record.get("pages") or 0)
            if min_pages <= pages <= max_pages:
                jobs.append((path, record))
    jobs.sort(
        key=lambda item: (
            -int(item[1].get("pages") or 0),
            -int(item[1].get("original_bytes") or 0),
            item[1]["source"],
            item[1]["relative_path"],
        )
    )
    return jobs[:limit] if limit is not None else jobs


def _plain(value: Any) -> Any:
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _value(container: Any, key: str, default: Any = None) -> Any:
    if isinstance(container, dict):
        return container.get(key, default)
    try:
        return container[key]
    except (KeyError, TypeError, IndexError):
        return getattr(container, key, default)


def page_from_result(result: Any, fallback_index: int) -> dict:
    blocks: list[dict] = []
    for block in result.get("parsing_res_list", []):
        blocks.append(
            {
                "label": str(_value(block, "block_label") or ""),
                "content": str(_value(block, "block_content") or ""),
                "bbox": _plain(_value(block, "block_bbox")),
                "order": _value(block, "block_order"),
                "group_id": _value(block, "group_id"),
            }
        )
    return {
        "page_index": result.get("page_index")
        if result.get("page_index") is not None
        else fallback_index,
        "page_count": result.get("page_count"),
        "width": result.get("width"),
        "height": result.get("height"),
        "blocks": blocks,
    }


def text_from_pages(pages: Iterable[dict]) -> str:
    page_texts: list[str] = []
    for page in sorted(pages, key=lambda item: int(item.get("page_index") or 0)):
        ordered = sorted(
            enumerate(page.get("blocks", [])),
            key=lambda pair: (
                pair[1].get("order") is None,
                pair[1].get("order") if pair[1].get("order") is not None else pair[0],
            ),
        )
        page_area = max(int(page.get("width") or 0) * int(page.get("height") or 0), 1)
        parts: list[str] = []
        for _, block in ordered:
            content = block.get("content", "").strip()
            label = block.get("label")
            if not content or label in IGNORED_BLOCK_LABELS:
                continue
            if label == "image":
                bbox = block.get("bbox") or [0, 0, 0, 0]
                if len(bbox) != 4:
                    continue
                area = max(0, bbox[2] - bbox[0]) * max(0, bbox[3] - bbox[1])
                # OCR whole-page/large scan regions, not photographs embedded
                # in an otherwise readable page.
                if area / page_area < 0.25:
                    continue
            parts.append(content)
        page_texts.append("\n\n".join(parts))
    return normalize_text("\n\n\f\n\n".join(page_texts))


def raw_path(raw_output: Path, record: dict) -> Path:
    return raw_output / record["source"] / f"{record['document_id']}.json.gz"


def write_error(record_path: Path, record: dict, error: str) -> None:
    record["status"] = "needs_ocr"
    record["ocr_last_error"] = error
    record["ocr_attempt"] = "paddleocr_vl_1_6_mlx"
    atomic_json_gzip(record_path, record)


def process_one(
    pipeline: Any,
    record_path: Path,
    record: dict,
    roots: dict[str, Path],
    raw_output: Path,
    counter: TokenCounter,
    model: str,
    ocr_image_blocks: bool,
) -> dict:
    source = record["source"]
    if source not in roots:
        raise RuntimeError(f"no --root supplied for source {source!r}")
    input_pdf = roots[source] / record["relative_path"]
    if not input_pdf.is_file() or input_pdf.stat().st_size == 0:
        error = f"missing or empty source PDF: {input_pdf}"
        write_error(record_path, record, error)
        return {"status": "ocr_error", "error": error}

    result_pages = [
        page_from_result(result, index)
        for index, result in enumerate(pipeline.predict(str(input_pdf)))
    ]
    if not result_pages:
        error = "PaddleOCR-VL returned no pages"
        write_error(record_path, record, error)
        return {"status": "ocr_error", "error": error}
    raw = {
        "schema_version": 1,
        "document_id": record["document_id"],
        "source": source,
        "relative_path": record["relative_path"],
        "engine": "PaddleOCR-VL",
        "engine_version": "1.6",
        "model": model,
        "backend": "mlx-vlm-server",
        "pages": result_pages,
    }
    raw_target = raw_path(raw_output, record)
    atomic_json_gzip(raw_target, raw)

    text = text_from_pages(result_pages)
    chars = len(text)
    words = len(text.split())
    alpha_ratio = sum(char.isalpha() for char in text) / max(chars, 1)
    replacement_ratio = text.count("\ufffd") / max(chars, 1)
    page_count = len(result_pages)
    threshold = max(MIN_TEXT_CHARS, page_count * MIN_CHARS_PER_PAGE)
    usable_volume = chars >= threshold and alpha_ratio >= 0.25
    record.update(
        {
            "status": "ocr_unreviewed" if usable_volume else "ocr_low_text",
            "error": "" if usable_volume else "Paddle OCR output failed text-volume gate",
            "extraction": "paddleocr_vl_1_6_mlx",
            "pages": page_count,
            "chars": chars,
            "words": words,
            "tokens": counter.count(text) if usable_volume else 0,
            "token_count_kind": counter.kind,
            "alpha_ratio": alpha_ratio,
            "replacement_ratio": replacement_ratio,
            "content_sha256": content_hash(text) if usable_volume else None,
            "text": text if usable_volume else "",
            "ocr_raw": str(raw_target),
            "ocr_model": model,
            "ocr_backend": "mlx-vlm-server",
            "ocr_image_blocks": ocr_image_blocks,
        }
    )
    record.pop("ocr_last_error", None)
    atomic_json_gzip(record_path, record)
    return {
        "status": record["status"],
        "pages": page_count,
        "chars": chars,
        "tokens": record["tokens"],
        "error": record["error"],
    }


def run(args: argparse.Namespace) -> dict:
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be positive")
    if args.region_concurrency < 1:
        raise ValueError("--region-concurrency must be positive")
    if args.min_pages < 1 or args.max_pages < args.min_pages:
        raise ValueError("page bounds must satisfy 1 <= --min-pages <= --max-pages")
    try:
        from paddleocr import PaddleOCRVL
    except ImportError as exc:
        raise RuntimeError("PaddleOCR is not installed in this environment") from exc

    roots = {spec.name: spec.path for spec in parse_roots(args.root)}
    records = args.records.expanduser().resolve()
    raw_output = args.raw_output.expanduser().resolve()
    counter = TokenCounter(args.tokenizer or None)
    jobs = discover(
        records,
        args.limit,
        args.overwrite,
        min_pages=args.min_pages,
        max_pages=args.max_pages,
    )
    pipeline = PaddleOCRVL(
        pipeline_version="v1.6",
        vl_rec_backend="mlx-vlm-server",
        vl_rec_server_url=args.server_url,
        vl_rec_api_model_name=args.model,
        vl_rec_max_concurrency=args.region_concurrency,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_ocr_for_image_block=args.ocr_image_blocks,
    )
    statuses: Counter[str] = Counter()
    total_tokens = 0
    for completed, (path, record) in enumerate(jobs, start=1):
        try:
            result = process_one(
                pipeline,
                path,
                record,
                roots,
                raw_output,
                counter,
                args.model,
                args.ocr_image_blocks,
            )
        except Exception as exc:
            write_error(path, record, str(exc))
            result = {"status": "ocr_error", "error": str(exc)}
        statuses[result["status"]] += 1
        total_tokens += int(result.get("tokens") or 0)
        print(
            f"[{completed:>5}/{len(jobs)}] {result['status']:<15} "
            f"{record['source']}/{record['relative_path']} {result.get('error', '')}",
            flush=True,
        )
    return {"jobs": len(jobs), "statuses": dict(statuses), "tokens": total_tokens}


def main() -> None:
    print(json.dumps(run(build_parser().parse_args()), indent=2))


if __name__ == "__main__":
    main()
