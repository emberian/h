from __future__ import annotations

import argparse
import csv
import gzip
import json
from pathlib import Path

from .extract import atomic_json_gzip


DECISIONS = {"accept", "reject", "retry"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create an OCR review sheet or apply explicit accept/reject/retry decisions."
    )
    parser.add_argument("--records", type=Path, default=Path("artifacts/extracted/records"))
    parser.add_argument("--sheet", type=Path, default=Path("artifacts/ocr-review.csv"))
    parser.add_argument("--apply", type=Path, help="review CSV containing document_id and decision")
    return parser


def load(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def records_by_id(root: Path) -> dict[str, tuple[Path, dict]]:
    result = {}
    for path in sorted(root.rglob("*.json.gz")):
        record = load(path)
        result[record["document_id"]] = (path, record)
    return result


def make_sheet(records: dict[str, tuple[Path, dict]], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "document_id",
        "decision",
        "source",
        "relative_path",
        "languages",
        "pages",
        "tokens",
        "chars_per_page",
        "alpha_ratio",
        "sample",
        "notes",
    ]
    count = 0
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for _, record in records.values():
            if record.get("status") != "ocr_unreviewed":
                continue
            pages = record.get("pages") or 1
            sample = " ".join(record.get("text", "").split())[:1_000]
            writer.writerow(
                {
                    "document_id": record["document_id"],
                    "decision": "",
                    "source": record["source"],
                    "relative_path": record["relative_path"],
                    "languages": "+".join(record.get("ocr_languages", [])),
                    "pages": record.get("pages") or "",
                    "tokens": record.get("tokens", 0),
                    "chars_per_page": round(record.get("chars", 0) / pages, 1),
                    "alpha_ratio": round(record.get("alpha_ratio", 0), 4),
                    "sample": sample,
                    "notes": "",
                }
            )
            count += 1
    return count


def apply_sheet(records: dict[str, tuple[Path, dict]], sheet: Path) -> dict[str, int]:
    counts = {decision: 0 for decision in DECISIONS}
    with sheet.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            decision = row.get("decision", "").strip().casefold()
            if not decision:
                continue
            if decision not in DECISIONS:
                raise ValueError(f"invalid decision {decision!r} for {row.get('document_id')}")
            document_id = row.get("document_id", "").strip()
            if document_id not in records:
                raise ValueError(f"unknown document_id {document_id!r}")
            path, record = records[document_id]
            if record.get("status") != "ocr_unreviewed":
                raise ValueError(
                    f"document {document_id} has status {record.get('status')!r}, expected 'ocr_unreviewed'"
                )
            record["status"] = {
                "accept": "ready",
                "reject": "ocr_rejected",
                "retry": "needs_ocr",
            }[decision]
            record["ocr_review"] = {
                "decision": decision,
                "notes": row.get("notes", ""),
            }
            atomic_json_gzip(path, record)
            counts[decision] += 1
    return counts


def main() -> None:
    args = build_parser().parse_args()
    records = records_by_id(args.records.expanduser().resolve())
    if args.apply:
        print(json.dumps(apply_sheet(records, args.apply.expanduser().resolve()), indent=2))
    else:
        count = make_sheet(records, args.sheet.expanduser().resolve())
        print(f"wrote {count} rows to {args.sheet.expanduser().resolve()}")


if __name__ == "__main__":
    main()

