from __future__ import annotations

import argparse
import csv
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

from .build_dataset import read_record, record_paths
from .privacy import credential_dump_indicator_count, credential_indicator_count


_TOKEN_RE = re.compile(r"\S+")
_SPACE_RE = re.compile(r"\s+")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit extracted records for suspicious text without changing them."
    )
    parser.add_argument("--records", type=Path, default=Path("artifacts/extracted/records"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/quality"))
    return parser


def repeated_line_ratio(text: str) -> float:
    lines: list[str] = []
    for raw in text.splitlines():
        line = _SPACE_RE.sub(" ", unicodedata.normalize("NFKC", raw).casefold()).strip()
        if len(line) >= 20:
            lines.append(line)
    if not lines:
        return 0.0
    counts = Counter(lines)
    repeated_chars = sum((count - 1) * len(line) for line, count in counts.items())
    return repeated_chars / sum(len(line) for line in lines)


def text_quality_metrics(text: str, record: dict) -> dict[str, float]:
    tokens = _TOKEN_RE.findall(text)
    token_count = max(len(tokens), 1)
    lexical = [token for token in tokens if any(char.isalpha() for char in token)]
    normalized_words = [
        "".join(char for char in token.casefold() if char.isalpha()) for token in lexical
    ]
    normalized_words = [word for word in normalized_words if word]
    # Newlines, tabs, carriage returns, and form feeds are intentional text
    # structure. In particular, extraction uses form feed as a page boundary.
    controls = sum(
        unicodedata.category(char) in {"Cc", "Cs"} and char not in "\n\t\r\f"
        for char in text
    )
    denominator = max(len(text), 1)
    return {
        "lexical_token_ratio": len(lexical) / token_count,
        "unique_word_ratio": len(set(normalized_words)) / max(len(normalized_words), 1),
        "long_token_ratio": sum(len(token) >= 40 for token in tokens) / token_count,
        "single_char_token_ratio": sum(len(token.strip(".,;:!?()[]{}\"'")) <= 1 for token in tokens)
        / token_count,
        "control_ratio": controls / denominator,
        "repeated_line_ratio": repeated_line_ratio(text),
        "falcon_tokens_per_word": float(record.get("tokens") or 0) / token_count,
        "credential_indicator_count": float(credential_indicator_count(text)),
        "credential_dump_indicator_count": float(credential_dump_indicator_count(text)),
    }


def quality_flags(record: dict, metrics: dict[str, float]) -> list[str]:
    flags: list[str] = []
    if float(record.get("replacement_ratio") or 0) > 0.0005:
        flags.append("replacement_characters")
    if float(record.get("alpha_ratio") or 0) < 0.35:
        flags.append("low_alphabetic_content")
    if metrics["control_ratio"] > 0.0001:
        flags.append("control_characters")
    if metrics["lexical_token_ratio"] < 0.50:
        flags.append("low_lexical_content")
    if metrics["repeated_line_ratio"] > 0.35:
        flags.append("repetitive_lines")
    if metrics["falcon_tokens_per_word"] > 3.5:
        flags.append("tokenizer_fragmentation")
    if metrics["long_token_ratio"] > 0.02:
        flags.append("many_long_tokens")
    if metrics["single_char_token_ratio"] > 0.35:
        flags.append("many_single_character_tokens")
    if int(record.get("words") or 0) >= 1_000 and metrics["unique_word_ratio"] < 0.03:
        flags.append("very_low_vocabulary")
    if metrics["credential_indicator_count"] > 0:
        flags.append("credential_material")
    return flags


def recommended_exclusion_reasons(
    record: dict, flags: list[str], metrics: dict[str, float] | None = None
) -> list[str]:
    reasons: list[str] = []
    flag_set = set(flags)
    # A single credential-like string in an otherwise useful document is only
    # a review flag.  Automatically exclude actual credential tables/dumps.
    if metrics is not None and metrics.get("credential_dump_indicator_count", 0) > 0:
        reasons.append("credential_dump")
    if {
        "replacement_characters",
        "low_alphabetic_content",
        "many_single_character_tokens",
    }.issubset(flag_set):
        reasons.append("severely_corrupt_text_layer")
    return reasons


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[math.floor(fraction * (len(ordered) - 1))]


def run(args: argparse.Namespace) -> dict:
    records_root = args.records.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    statuses: Counter[str] = Counter()
    flags: Counter[str] = Counter()
    tokens_by_flag: Counter[str] = Counter()
    values: dict[str, list[float]] = {}
    ready_tokens = 0
    recommended_exclusions: list[dict] = []

    for path in record_paths(records_root):
        record = read_record(path)
        statuses[str(record.get("status"))] += 1
        if record.get("status") != "ready":
            continue
        ready_tokens += int(record.get("tokens") or 0)
        metrics = text_quality_metrics(record.get("text") or "", record)
        record_flags = quality_flags(record, metrics)
        exclusion_reasons = recommended_exclusion_reasons(record, record_flags, metrics)
        for name, value in metrics.items():
            values.setdefault(name, []).append(value)
        for flag in record_flags:
            flags[flag] += 1
            tokens_by_flag[flag] += int(record.get("tokens") or 0)
        rows.append(
            {
                "document_id": record["document_id"],
                "source": record["source"],
                "relative_path": record["relative_path"],
                "extraction": record.get("extraction"),
                "tokens": int(record.get("tokens") or 0),
                "chars": int(record.get("chars") or 0),
                "alpha_ratio": float(record.get("alpha_ratio") or 0),
                "replacement_ratio": float(record.get("replacement_ratio") or 0),
                **metrics,
                "flag_count": len(record_flags),
                "flags": ";".join(record_flags),
                "recommended_exclusion_reasons": ";".join(exclusion_reasons),
            }
        )
        if exclusion_reasons:
            recommended_exclusions.append(
                {
                    "document_id": record["document_id"],
                    "source": record["source"],
                    "relative_path": record["relative_path"],
                    "reasons": exclusion_reasons,
                    "tokens": int(record.get("tokens") or 0),
                }
            )

    rows.sort(key=lambda row: (-row["flag_count"], -row["tokens"], row["document_id"]))
    fields = list(rows[0]) if rows else ["document_id", "source", "relative_path", "flags"]
    with (output / "records.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with (output / "flagged.jsonl").open("w", encoding="utf-8") as stream:
        for row in rows:
            if row["flag_count"]:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (output / "recommended_exclusions.jsonl").open("w", encoding="utf-8") as stream:
        for exclusion in recommended_exclusions:
            stream.write(json.dumps(exclusion, ensure_ascii=False) + "\n")

    summary = {
        "source_statuses": dict(sorted(statuses.items())),
        "ready_documents": len(rows),
        "ready_tokens": ready_tokens,
        "flagged_documents": sum(bool(row["flag_count"]) for row in rows),
        "recommended_exclusions": {
            "documents": len(recommended_exclusions),
            "tokens": sum(item["tokens"] for item in recommended_exclusions),
        },
        "flags": {
            flag: {"documents": flags[flag], "tokens": tokens_by_flag[flag]}
            for flag in sorted(flags)
        },
        "metric_quantiles": {
            name: {
                "p01": quantile(metric_values, 0.01),
                "p50": quantile(metric_values, 0.50),
                "p95": quantile(metric_values, 0.95),
                "p99": quantile(metric_values, 0.99),
            }
            for name, metric_values in sorted(values.items())
        },
    }
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report = [
        "# h ghost text-quality audit",
        "",
        f"- Ready records audited: **{len(rows):,}**",
        f"- Ready Falcon-H1 tokens: **{ready_tokens:,}**",
        f"- Records with one or more conservative review flags: **{summary['flagged_documents']:,}**",
        f"- High-confidence recommended exclusions: **{len(recommended_exclusions):,}**",
        "",
        "Flags identify review candidates; this command never mutates or rejects source records.",
        "",
        "| Flag | Documents | Tokens represented |",
        "|---|---:|---:|",
    ]
    for flag in sorted(flags):
        report.append(f"| {flag} | {flags[flag]:,} | {tokens_by_flag[flag]:,} |")
    report.append("")
    (output / "report.md").write_text("\n".join(report), encoding="utf-8")
    return summary


def main() -> None:
    print(json.dumps(run(build_parser().parse_args()), indent=2))


if __name__ == "__main__":
    main()
