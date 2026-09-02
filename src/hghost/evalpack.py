"""Checkpoint evaluation pack: comparable reports for a list of Falcon-H1 checkpoints.

For every checkpoint (a Hugging Face directory with ``model.safetensors``, ``config.json``
and tokenizer files) the pack produces

* validation losses on fixed slices of ``validation.bin`` (the first N sequences, and a
  subsample of the sequences inside family-clean validation documents), each reported
  plain, furniture-subtracted (positions inside page furniture found by the haunting
  index are dropped) and unseen-only (positions inside any exact training match dropped);
* a generic-English retention proxy: loss on a fixed out-of-corpus text;
* fixed-prompt, fixed-seed generations sampled with mlx-lm, stored blind under a hash of
  the checkpoint path with a separate key file;
* a memorization scan of those generations against the training stream, separating
  furniture (n-grams shared by many documents) from quotation (long spans from one or two
  documents).

Losses run through h1jax on CPU in a subprocess inside ``.venv-jax``; generation runs in
the mlx-lm virtualenv. Everything else runs in the main ``hghost`` environment.

Typical use (from the repository root)::

    .venv/bin/hghost-evalpack --output research/results/evalpack-<date> --parallel 4 \\
        --checkpoint base=kaggle/base_model_dataset_public \\
        --checkpoint tpu-10m=/path/to/tokens-000010000000 ...

Per-checkpoint losses and generations are cached under the output directory (a killed
JAX worker resumes from its last slab), so re-running with more ``--checkpoint``
arguments only evaluates the new ones and rebuilds the report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import multiprocessing
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from .haunt import (
    DEFAULT_TOKENIZER_FILE,
    TOKEN_DTYPE,
    HauntingIndex,
    Span,
    as_token_array,
    coverage_fractions,
    maximal_spans,
    read_document_table,
    verify_document_layout,
)

DEFAULT_JAX_PYTHON = Path(".venv-jax/bin/python")
DEFAULT_MLX_PYTHON = Path("~/.cache/h1-distributed/venv/bin/python")
DEFAULT_FAMILIES = Path("artifacts/families/leakage-report.json")
DEFAULT_THRESHOLDS = (8, 16, 32)
MASK_PAD = 64
MASK_CHUNK = 4096
DEFAULT_WORKERS = max(1, min(6, os.cpu_count() or 1))
LOG_PREFIX = "[evalpack]"


def log(message: str) -> None:
    stamp = time.strftime("%H:%M:%S")
    print(f"{LOG_PREFIX} {stamp} {message}", file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- inputs


@dataclass(frozen=True)
class Checkpoint:
    name: str
    path: Path

    @property
    def blind_id(self) -> str:
        return hashlib.sha256(str(self.path).encode("utf-8")).hexdigest()[:12]


def parse_checkpoint(value: str) -> Checkpoint:
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"expected NAME=DIR, got {value!r}")
    name, raw = value.split("=", 1)
    name = name.strip()
    path = Path(raw).expanduser().resolve()
    if not name:
        raise argparse.ArgumentTypeError(f"empty checkpoint name in {value!r}")
    if not (path / "config.json").is_file():
        raise argparse.ArgumentTypeError(f"{path} has no config.json")
    return Checkpoint(name, path)


def parse_int_list(value: str) -> tuple[int, ...]:
    values = tuple(sorted({int(item) for item in value.split(",") if item.strip()}))
    if not values or min(values) < 1:
        raise argparse.ArgumentTypeError(f"expected positive integers, got {value!r}")
    return values


def sequence_rows(
    tokens: np.ndarray, sequence_ids: np.ndarray, length: int
) -> np.ndarray:
    """Rows ``[n, length + 1]`` for the given sequence ids of a contiguous stream.

    Sequence ``s`` is ``tokens[s * length : s * length + length + 1]`` in file order,
    which is exactly what h1jax's ``ValidationStream`` yields for offset ``s``.
    """
    rows = np.empty((len(sequence_ids), length + 1), dtype=np.int32)
    for row, sequence in enumerate(sequence_ids):
        start = int(sequence) * length
        rows[row] = tokens[start : start + length + 1]
    return rows


def clean_sequence_ids(
    entries,
    levels: dict[str, str],
    length: int,
    stream_tokens: int,
) -> tuple[np.ndarray, dict[str, int]]:
    """Sequence ids whose whole ``length + 1`` window lies inside a clean document."""
    sequence_count = (stream_tokens - 1) // length
    starts = np.arange(sequence_count, dtype=np.int64) * length
    offsets = np.array([entry.token_offset for entry in entries], dtype=np.int64)
    ends = np.array([entry.end for entry in entries], dtype=np.int64)
    document = np.searchsorted(offsets, starts, side="right") - 1
    inside = starts + length + 1 <= ends[document]
    clean = np.array([levels.get(entry.id) == "clean" for entry in entries], dtype=bool)
    keep = inside & clean[document]
    per_document = {
        entries[index].id: int(count)
        for index, count in zip(*np.unique(document[keep], return_counts=True))
    }
    return np.flatnonzero(keep).astype(np.int64), per_document


def evenly_spaced(values: np.ndarray, count: int) -> np.ndarray:
    """A deterministic subsample of ``values`` spread over the whole array."""
    if count <= 0 or len(values) <= count:
        return np.asarray(values)
    picks = np.round(np.linspace(0, len(values) - 1, count)).astype(np.int64)
    return np.asarray(values)[np.unique(picks)]


def load_leakage_levels(path: Path) -> dict[str, str]:
    report = json.loads(path.read_text(encoding="utf-8"))
    return {str(item["id"]): str(item["leakage_level"]) for item in report["documents"]}


def load_tokenizer_file(path: Path):
    from tokenizers import Tokenizer

    return Tokenizer.from_file(str(path))


def checkpoint_tokenizer_file(checkpoint: Checkpoint, fallback: Path) -> Path:
    candidate = checkpoint.path / "tokenizer.json"
    return candidate if candidate.is_file() else fallback


# --------------------------------------------------------------------------- haunting


def coverage_mask(lengths: np.ndarray, threshold: int) -> np.ndarray:
    """Positions inside some exact match of at least ``threshold`` tokens."""
    size = int(lengths.shape[0])
    marks = np.zeros(size + 1, dtype=np.int64)
    starts = np.flatnonzero(lengths >= threshold)
    np.add.at(marks, starts, 1)
    np.add.at(marks, starts + lengths[starts], -1)
    return np.cumsum(marks[:size]) > 0


def distinct_documents(index: HauntingIndex, pattern: np.ndarray, minimum: int) -> int:
    """Distinct training documents containing ``pattern`` (exact when >= minimum)."""
    low, high = index.occurrence_range(np.ascontiguousarray(pattern, dtype=np.uint16))
    if high - low < minimum:
        return high - low
    indexes, _ = index.documents_for_ranks(low, high)
    return int(indexes.size)


@dataclass
class HauntMasks:
    lengths: np.ndarray
    matched: np.ndarray
    furniture: np.ndarray
    spans: list[Span] = field(default_factory=list)


def haunt_masks(
    index: HauntingIndex,
    query: np.ndarray,
    *,
    min_tokens: int,
    min_documents: int,
) -> HauntMasks:
    """Per-position exact-match and furniture masks of ``query`` against training.

    ``matched[p]`` is true when some exact training match of at least ``min_tokens``
    covers position ``p``. ``furniture[p]`` is true when such a match window of exactly
    ``min_tokens`` (or a whole maximal span) covering ``p`` occurs in at least
    ``min_documents`` distinct training documents; a long span quoted from one or two
    documents whose pieces are common boilerplate therefore still counts as furniture.
    """
    query = np.ascontiguousarray(query, dtype=np.uint16)
    lengths, offsets = index.match_lengths(query)
    matched = coverage_mask(lengths, min_tokens)
    furniture = np.zeros(query.shape[0], dtype=bool)
    spans = maximal_spans(lengths, offsets, min_tokens)
    for span in spans:
        pattern = query[span.query_offset : span.end]
        if distinct_documents(index, pattern, min_documents) >= min_documents:
            furniture[span.query_offset : span.end] = True
            continue
        for start in range(span.query_offset, span.end - min_tokens + 1):
            window = slice(start, start + min_tokens)
            if furniture[window].all():
                continue
            if distinct_documents(index, query[window], min_documents) >= min_documents:
                furniture[window] = True
    return HauntMasks(lengths, matched, furniture, spans)


def stream_masks(
    index: HauntingIndex,
    tokens: np.ndarray,
    start: int,
    end: int,
    *,
    min_tokens: int,
    min_documents: int,
    pad: int = MASK_PAD,
) -> HauntMasks:
    """Masks for stream positions ``[start, end)`` with context so matches are exact.

    Padding by at least ``min_tokens`` on both sides makes coverage independent of the
    cut: any match that crosses the cut also has a sub-match of at least ``min_tokens``
    that begins inside the padded window.
    """
    pad = max(pad, min_tokens)
    left = max(0, start - pad)
    right = min(int(tokens.shape[0]), end + pad)
    masks = haunt_masks(
        index,
        np.asarray(tokens[left:right]),
        min_tokens=min_tokens,
        min_documents=min_documents,
    )
    window = slice(start - left, end - left)
    return HauntMasks(
        masks.lengths[window],
        masks.matched[window],
        masks.furniture[window],
        masks.spans,
    )


def contiguous_runs(sequence_ids: np.ndarray) -> list[tuple[int, int]]:
    """Group sorted sequence ids into (first, last + 1) runs of consecutive ids."""
    runs: list[tuple[int, int]] = []
    for sequence in sorted(int(value) for value in sequence_ids):
        if runs and runs[-1][1] == sequence:
            runs[-1] = (runs[-1][0], sequence + 1)
        else:
            runs.append((sequence, sequence + 1))
    return runs


def mask_chunks(
    sequence_ids: np.ndarray, length: int, chunk: int = MASK_CHUNK
) -> list[tuple[int, int]]:
    """Stream label ranges ``[start, end)`` covering the rows, in pieces of <= chunk."""
    pieces: list[tuple[int, int]] = []
    for first, stop in contiguous_runs(sequence_ids):
        start, end = first * length + 1, stop * length + 1
        for piece in range(start, end, chunk):
            pieces.append((piece, min(end, piece + chunk)))
    return pieces


_MASK_WORKER: dict = {}


def _init_mask_worker(
    index_dir: Path, tokens_path: Path, min_tokens: int, min_documents: int
) -> None:
    _MASK_WORKER["index"] = HauntingIndex.load(index_dir)
    _MASK_WORKER["tokens"] = np.memmap(tokens_path, dtype=TOKEN_DTYPE, mode="r")
    _MASK_WORKER["min_tokens"] = min_tokens
    _MASK_WORKER["min_documents"] = min_documents


def _mask_chunk(piece: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    masks = stream_masks(
        _MASK_WORKER["index"],
        _MASK_WORKER["tokens"],
        piece[0],
        piece[1],
        min_tokens=_MASK_WORKER["min_tokens"],
        min_documents=_MASK_WORKER["min_documents"],
    )
    return masks.matched, masks.furniture


def label_masks(
    index: HauntingIndex,
    tokens: np.ndarray,
    sequence_ids: np.ndarray,
    length: int,
    *,
    min_tokens: int,
    min_documents: int,
    progress=None,
    mapper=None,
) -> tuple[np.ndarray, np.ndarray]:
    """``matched`` and ``furniture`` masks ``[n, length]`` over the label positions.

    Row ``r`` predicts stream tokens ``s * length + 1 .. s * length + length`` for
    sequence ``s = sequence_ids[r]``; a label position is masked when the label token
    itself lies inside a matched (or furniture) window. ``mapper`` maps a chunk
    function over ``mask_chunks`` (``map`` by default, or a pool's ``map``).
    """
    sequence_ids = np.asarray(sequence_ids, dtype=np.int64)
    matched = np.zeros((len(sequence_ids), length), dtype=bool)
    furniture = np.zeros((len(sequence_ids), length), dtype=bool)
    pieces = mask_chunks(sequence_ids, length)

    def compute(piece: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
        masks = stream_masks(
            index,
            tokens,
            piece[0],
            piece[1],
            min_tokens=min_tokens,
            min_documents=min_documents,
        )
        return masks.matched, masks.furniture

    results = map(compute, pieces) if mapper is None else mapper(pieces)
    for number, ((start, end), (piece_matched, piece_furniture)) in enumerate(
        zip(pieces, results)
    ):
        positions = np.arange(start, end, dtype=np.int64) - 1
        rows = np.searchsorted(sequence_ids, positions // length)
        columns = positions % length
        matched[rows, columns] = piece_matched
        furniture[rows, columns] = piece_furniture
        if progress is not None:
            progress(number + 1, len(pieces))
    return matched, furniture


# --------------------------------------------------------------------------- metrics


def masked_mean(values: np.ndarray, keep: np.ndarray) -> float | None:
    selected = values[keep]
    return float(selected.mean()) if selected.size else None


def summarize_losses(
    losses: np.ndarray,
    correct: np.ndarray,
    matched: np.ndarray | None = None,
    furniture: np.ndarray | None = None,
) -> dict:
    """Plain, furniture-free and unseen-only means over per-token losses."""
    losses = np.asarray(losses, dtype=np.float64)
    correct = np.asarray(correct, dtype=bool)
    total = int(losses.size)
    plain = float(losses.mean()) if total else None
    summary = {
        "sequences": int(losses.shape[0]) if losses.ndim == 2 else 1,
        "tokens": total,
        "loss": plain,
        "perplexity": math.exp(plain) if plain is not None else None,
        "accuracy": float(correct.mean()) if total else None,
    }
    if furniture is not None:
        keep = ~np.asarray(furniture, dtype=bool)
        summary["furniture_fraction"] = float(1 - keep.mean()) if total else None
        summary["furniture_free_loss"] = masked_mean(losses, keep)
        summary["furniture_free_accuracy"] = masked_mean(correct, keep)
        summary["furniture_loss"] = masked_mean(losses, ~keep)
    if matched is not None:
        keep = ~np.asarray(matched, dtype=bool)
        summary["matched_fraction"] = float(1 - keep.mean()) if total else None
        summary["unseen_loss"] = masked_mean(losses, keep)
        summary["unseen_accuracy"] = masked_mean(correct, keep)
    return summary


def scan_generation_text(
    index: HauntingIndex,
    tokens: np.ndarray,
    *,
    thresholds: tuple[int, ...],
    min_documents: int,
    tokenizer=None,
) -> dict:
    """Memorization scan of one generation, separating furniture from quotation."""
    tokens = as_token_array(tokens)
    min_tokens = min(thresholds)
    masks = haunt_masks(
        index, tokens, min_tokens=min_tokens, min_documents=min_documents
    )
    size = int(tokens.shape[0])
    coverage = coverage_fractions(masks.lengths, thresholds)
    quotation = {}
    for threshold in thresholds:
        covered = coverage_mask(masks.lengths, threshold) & ~masks.furniture
        quotation[str(threshold)] = float(covered.mean()) if size else 0.0
    longest: dict | None = None
    if masks.spans:
        span = max(masks.spans, key=lambda item: (item.length, -item.query_offset))
        described = index.describe_span(tokens, span, tokenizer, max_documents=3)
        described["furniture"] = bool(
            masks.furniture[span.query_offset : span.end].all()
        )
        longest = described
    return {
        "tokens": size,
        "longest_match": int(masks.lengths.max()) if size else 0,
        "coverage": {str(threshold): value for threshold, value in coverage.items()},
        "furniture_fraction": float(masks.furniture.mean()) if size else 0.0,
        "quotation": quotation,
        "span_count": len(masks.spans),
        "longest_span": longest,
    }


def summarize_memorization(records: list[dict], thresholds: tuple[int, ...]) -> dict:
    total = sum(record["tokens"] for record in records)

    def weighted(key: str, threshold: str) -> float:
        if not total:
            return 0.0
        return (
            sum(record[key][threshold] * record["tokens"] for record in records) / total
        )

    return {
        "generations": len(records),
        "tokens": total,
        "coverage": {str(t): weighted("coverage", str(t)) for t in thresholds},
        "quotation": {str(t): weighted("quotation", str(t)) for t in thresholds},
        "furniture_fraction": (
            sum(record["furniture_fraction"] * record["tokens"] for record in records)
            / total
            if total
            else 0.0
        ),
        "longest_match": max(
            (record["longest_match"] for record in records), default=0
        ),
        "generations_with_match_at_least": {
            str(t): sum(record["longest_match"] >= t for record in records)
            for t in thresholds
        },
        "generations_with_quotation_at_least": {
            str(t): sum(record["quotation"][str(t)] > 0 for record in records)
            for t in thresholds
        },
    }


# --------------------------------------------------------------------------- workers


def package_root() -> Path:
    return Path(__file__).resolve().parent.parent


def run_worker(python: Path, module: str, arguments: list[str], env: dict) -> None:
    command = [str(python), "-m", module, *arguments]
    log("run " + " ".join(command))
    merged = dict(os.environ)
    merged.update(env)
    merged["PYTHONPATH"] = str(package_root()) + (
        os.pathsep + merged["PYTHONPATH"] if merged.get("PYTHONPATH") else ""
    )
    subprocess.run(command, check=True, env=merged)


def loss_output(
    args: argparse.Namespace, checkpoint: Checkpoint, rows_key: str
) -> Path:
    return args.output / "losses" / f"{checkpoint.blind_id}-{rows_key}.npz"


def run_losses(
    args: argparse.Namespace, checkpoint: Checkpoint, rows_path: Path, output: Path
) -> dict:
    if output.is_file() and not args.force:
        log(f"{checkpoint.name}: reusing {output}")
    else:
        run_worker(
            args.jax_python,
            "hghost.evalpack_jax",
            [
                "--checkpoint",
                str(checkpoint.path),
                "--rows",
                str(rows_path),
                "--output",
                str(output),
                "--batch",
                str(args.batch),
                "--dtype",
                args.dtype,
            ],
            {"JAX_PLATFORM_NAME": "cpu"},
        )
    return json.loads(output.with_suffix(".json").read_text(encoding="utf-8"))


def run_generation(
    args: argparse.Namespace, checkpoint: Checkpoint, output: Path
) -> dict:
    if output.is_file() and not args.force:
        log(f"{checkpoint.name}: reusing {output}")
    else:
        run_worker(
            args.mlx_python,
            "hghost.evalpack_mlx",
            [
                "--checkpoint",
                str(checkpoint.path),
                "--prompts",
                str(args.prompts),
                "--output",
                str(output),
                "--max-tokens",
                str(args.max_new_tokens),
                "--temperature",
                str(args.temperature),
                "--top-p",
                str(args.top_p),
                "--repetition-penalty",
                str(args.repetition_penalty),
            ],
            {},
        )
    return json.loads(output.with_suffix(".meta.json").read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


# --------------------------------------------------------------------------- report


def fmt(value, digits: int = 4) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def pct(value) -> str:
    return "-" if value is None else f"{100 * value:.2f}%"


def markdown_table(header: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join(["---"] * len(header)) + "|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def metric_table(
    report: dict, key: str, formatter=fmt, *, delta: bool = False
) -> str | None:
    slices = list(report["slices"])
    checkpoints = report["checkpoints"]
    if not checkpoints or not slices:
        return None
    header = ["checkpoint", *slices]
    rows = []
    baseline = checkpoints[0]
    for checkpoint in checkpoints:
        row = [checkpoint["name"]]
        for name in slices:
            value = checkpoint["losses"].get(name, {}).get(key)
            cell = formatter(value)
            reference = baseline["losses"].get(name, {}).get(key)
            if delta and checkpoint is not baseline and None not in (value, reference):
                cell += f" ({value - reference:+.4f})"
            row.append(cell)
        rows.append(row)
    return markdown_table(header, rows)


def render_report(report: dict) -> str:
    settings = report["settings"]
    parts = [
        "# Checkpoint evaluation pack",
        "",
        (
            f"Generated {report['generated']}. Losses: h1jax on CPU, parameters loaded"
            f" as float32, compute dtype `{settings['dtype']}`, sequence length"
            f" {settings['sequence_length']}. Furniture: exact training matches of"
            f" >= {settings['min_tokens']} tokens whose {settings['min_tokens']}-token"
            f" windows occur in >= {settings['min_documents']} distinct training"
            " documents (haunting index). Unseen: positions outside any exact match"
            f" of >= {settings['min_tokens']} tokens. Deltas are against the first"
            " checkpoint."
        ),
        "",
        "## Slices",
        "",
        markdown_table(
            [
                "slice",
                "sequences",
                "predicted tokens",
                "furniture",
                "matched",
                "documents",
            ],
            [
                [
                    name,
                    str(info["sequences"]),
                    f"{info['tokens']:,}",
                    pct(info.get("furniture_fraction")),
                    pct(info.get("matched_fraction")),
                    str(info.get("documents", "-")),
                ]
                for name, info in report["slices"].items()
            ],
        ),
    ]
    retention = report.get("retention")
    if retention:
        parts += [
            "",
            f"Retention proxy: `{retention['path']}` ({retention['bytes']:,} bytes,"
            f" {retention['tokens']:,} tokens, {retention['sequences']} sequences of"
            f" {settings['sequence_length']}); training-match coverage at"
            + " "
            + ", ".join(f">={t}: {pct(v)}" for t, v in retention["coverage"].items())
            + ".",
        ]
    tables = [
        ("Loss (plain, all positions)", "loss", fmt, True),
        ("Loss (furniture-subtracted)", "furniture_free_loss", fmt, True),
        ("Loss (unseen positions only)", "unseen_loss", fmt, True),
        ("Loss on furniture positions only", "furniture_loss", fmt, False),
        ("Next-token accuracy (all positions)", "accuracy", pct, False),
        (
            "Next-token accuracy (furniture-subtracted)",
            "furniture_free_accuracy",
            pct,
            False,
        ),
    ]
    for title, key, formatter, delta in tables:
        table = metric_table(report, key, formatter, delta=delta)
        if table:
            parts += ["", f"## {title}", "", table]
    if retention and any("retention" in c for c in report["checkpoints"]):
        rows = []
        first = None
        for checkpoint in report["checkpoints"]:
            value = checkpoint.get("retention", {}).get("loss")
            if first is None:
                first = value
            cell = fmt(value)
            if (
                value is not None
                and first is not None
                and checkpoint is not report["checkpoints"][0]
            ):
                cell += f" ({value - first:+.4f})"
            rows.append(
                [
                    checkpoint["name"],
                    cell,
                    fmt(checkpoint.get("retention", {}).get("perplexity"), 2),
                    pct(checkpoint.get("retention", {}).get("accuracy")),
                ]
            )
        parts += [
            "",
            "## Retention proxy (out-of-corpus English)",
            "",
            markdown_table(["checkpoint", "loss", "perplexity", "accuracy"], rows),
        ]
    if any("memorization" in c for c in report["checkpoints"]):
        thresholds = [str(t) for t in settings["thresholds"]]
        header = [
            "checkpoint",
            *[f"coverage>={t}" for t in thresholds],
            "furniture",
            *[f"quotation>={t}" for t in thresholds],
            "longest",
            f"gens quoting>={thresholds[-1]}",
        ]
        rows = []
        for checkpoint in report["checkpoints"]:
            memo = checkpoint.get("memorization")
            if not memo:
                rows.append([checkpoint["name"], *["-"] * (len(header) - 1)])
                continue
            rows.append(
                [
                    checkpoint["name"],
                    *[pct(memo["coverage"][t]) for t in thresholds],
                    pct(memo["furniture_fraction"]),
                    *[pct(memo["quotation"][t]) for t in thresholds],
                    str(memo["longest_match"]),
                    (
                        f"{memo['generations_with_quotation_at_least'][thresholds[-1]]}"
                        f"/{memo['generations']}"
                    ),
                ]
            )
        parts += [
            "",
            "## Generation memorization (token-weighted over all prompts)",
            "",
            markdown_table(header, rows),
            "",
            (
                "Coverage: fraction of generated tokens inside an exact training match"
                " of at least the threshold. Furniture: fraction inside windows shared"
                f" by >= {settings['min_documents']} documents. Quotation: covered but"
                " not furniture. Generations are stored blind under"
                " `generations/<id>.jsonl`; `generations/KEY.json` maps ids to"
                " checkpoints."
            ),
        ]
        rows = []
        for checkpoint in report["checkpoints"]:
            for record in checkpoint.get("memorization_records", []):
                span = record.get("longest_span")
                if not span or span["length"] < settings["thresholds"][-1]:
                    continue
                text = span.get("text", "")
                text = text.replace("\n", "\\n").replace("|", "\\|")
                if len(text) > 80:
                    text = text[:77] + "..."
                rows.append(
                    [
                        checkpoint["name"],
                        record["prompt_id"],
                        str(span["length"]),
                        str(span["distinct_documents"]),
                        "furniture" if span["furniture"] else "quotation",
                        span["document"]["path"][-50:],
                        f"`{text}`",
                    ]
                )
        if rows:
            parts += [
                "",
                f"## Longest matches of >= {settings['thresholds'][-1]} tokens",
                "",
                markdown_table(
                    ["checkpoint", "prompt", "len", "docs", "kind", "document", "text"],
                    rows,
                ),
            ]
    parts += [
        "",
        "## Checkpoints",
        "",
        markdown_table(
            ["name", "blind id", "path", "loss seconds", "generation seconds"],
            [
                [
                    c["name"],
                    c["blind_id"],
                    f"`{c['path']}`",
                    fmt(c.get("loss_meta", {}).get("seconds"), 0),
                    fmt(c.get("generation_meta", {}).get("seconds"), 0),
                ]
                for c in report["checkpoints"]
            ],
        ),
        "",
    ]
    return "\n".join(parts)


# --------------------------------------------------------------------------- driver


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--checkpoint",
        type=parse_checkpoint,
        action="append",
        required=True,
        metavar="NAME=DIR",
        help="checkpoint to evaluate (repeatable; the first one is the delta baseline)",
    )
    parser.add_argument(
        "--validation", type=Path, default=Path("artifacts/tokenized/validation.bin")
    )
    parser.add_argument("--dataset", type=Path, default=Path("artifacts/dataset"))
    parser.add_argument("--index", type=Path, default=Path("artifacts/haunting-index"))
    parser.add_argument(
        "--prompts", type=Path, default=Path("research/eval/prompts.json")
    )
    parser.add_argument(
        "--retention", type=Path, default=Path("research/eval/retention.txt")
    )
    parser.add_argument(
        "--families",
        type=Path,
        default=DEFAULT_FAMILIES,
        help="leakage report with per-document leakage_level (for the clean slice)",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--sequences",
        type=parse_int_list,
        default=(32, 512),
        help="comma-separated prefix sizes of validation sequences to report",
    )
    parser.add_argument("--sequence-length", type=int, default=512)
    parser.add_argument(
        "--clean-sequences",
        type=int,
        default=512,
        help="evenly spaced sequences from family-clean validation documents (0: off)",
    )
    parser.add_argument("--min-tokens", type=int, default=8)
    parser.add_argument("--min-documents", type=int, default=5)
    parser.add_argument("--thresholds", type=parse_int_list, default=DEFAULT_THRESHOLDS)
    parser.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER_FILE)
    parser.add_argument("--jax-python", type=Path, default=DEFAULT_JAX_PYTHON)
    parser.add_argument("--mlx-python", type=Path, default=DEFAULT_MLX_PYTHON)
    parser.add_argument("--batch", type=int, default=8, help="JAX rows per forward")
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="JAX loss workers to run concurrently (each uses under two cores)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help="processes for the haunting-index masks over the validation slices",
    )
    parser.add_argument("--dtype", choices=("float32", "bfloat16"), default="float32")
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--repetition-penalty", type=float, default=1.08)
    parser.add_argument("--skip-losses", action="store_true")
    parser.add_argument("--skip-generation", action="store_true")
    parser.add_argument("--skip-memorization", action="store_true")
    parser.add_argument(
        "--force", action="store_true", help="recompute cached losses and generations"
    )
    return parser


def digest(*parts: object) -> str:
    hasher = hashlib.sha256()
    for part in parts:
        if isinstance(part, np.ndarray):
            hasher.update(np.ascontiguousarray(part).tobytes())
        else:
            hasher.update(json.dumps(part, sort_keys=True, default=str).encode("utf-8"))
        hasher.update(b"\0")
    return hasher.hexdigest()[:16]


@dataclass
class Prepared:
    """Everything shared by all checkpoints: rows, masks, slice definitions."""

    rows_path: Path
    rows_key: str
    slices: dict[str, np.ndarray]  # slice name -> row indices into rows
    slice_info: dict[str, dict]
    matched: np.ndarray  # [validation rows, L]
    furniture: np.ndarray
    validation_rows: int
    retention_rows: slice | None
    retention_info: dict | None


def prepare(args: argparse.Namespace, index: HauntingIndex, tokenizer) -> Prepared:
    length = args.sequence_length
    tokens = np.memmap(args.validation, dtype=TOKEN_DTYPE, mode="r")
    if int(tokens.shape[0]) < (max(args.sequences) * length + 1):
        raise ValueError("validation stream is shorter than the requested slices")
    prefix = np.arange(max(args.sequences), dtype=np.int64)
    slice_ids: dict[str, np.ndarray] = {
        f"first-{count}": np.arange(count, dtype=np.int64) for count in args.sequences
    }
    slice_docs: dict[str, dict] = {}
    entries = None
    if (args.dataset / "manifest.json").is_file():
        entries = read_document_table(args.dataset, "validation")
        layout = verify_document_layout(tokens, entries, index.eos_token_id)
        if layout["problems"]:
            raise ValueError(
                "validation document layout mismatch: " + "; ".join(layout["problems"])
            )
        offsets = np.array([entry.token_offset for entry in entries])
        for name, ids in slice_ids.items():
            documents = np.searchsorted(offsets, ids * length, side="right") - 1
            slice_docs[name] = {"documents": len(np.unique(documents))}
    if args.clean_sequences > 0 and args.families.is_file() and entries is not None:
        levels = load_leakage_levels(args.families)
        clean_ids, _ = clean_sequence_ids(entries, levels, length, int(tokens.shape[0]))
        chosen = evenly_spaced(clean_ids, args.clean_sequences)
        name = f"clean-{len(chosen)}"
        slice_ids[name] = chosen
        documents = np.searchsorted(offsets, chosen * length, side="right") - 1
        counts = {
            entries[int(doc)].path: int(count)
            for doc, count in zip(*np.unique(documents, return_counts=True))
        }
        slice_docs[name] = {
            "documents": len(counts),
            "clean_sequences_available": len(clean_ids),
            "sequences_per_document": counts,
        }
        log(
            f"clean slice: {len(chosen)} of {len(clean_ids)} sequences inside"
            f" {len(counts)} clean documents"
        )
    elif args.clean_sequences > 0:
        log(f"no families report at {args.families} or dataset; clean slice skipped")

    sequence_ids = np.unique(np.concatenate([prefix, *slice_ids.values()]))
    row_of = {int(sequence): row for row, sequence in enumerate(sequence_ids)}
    validation_rows = sequence_rows(tokens, sequence_ids, length)

    retention_rows = None
    retention_info = None
    rows = validation_rows
    if args.retention.is_file():
        text = args.retention.read_text(encoding="utf-8")
        retention_tokens = as_token_array(
            tokenizer.encode(text, add_special_tokens=False).ids
        )
        count = (int(retention_tokens.shape[0]) - 1) // length
        if count < 1:
            raise ValueError("retention text is shorter than one sequence")
        extra = sequence_rows(retention_tokens, np.arange(count), length)
        rows = np.concatenate([validation_rows, extra], axis=0)
        retention_rows = slice(len(validation_rows), len(rows))
        lengths, _ = index.match_lengths(retention_tokens)
        retention_info = {
            "path": str(args.retention),
            "bytes": len(text.encode("utf-8")),
            "tokens": int(retention_tokens.shape[0]),
            "sequences": count,
            "coverage": {
                str(t): v
                for t, v in coverage_fractions(lengths, args.thresholds).items()
            },
            "longest_match": int(lengths.max()),
        }
        log(
            f"retention text: {retention_info['tokens']} tokens, longest training"
            f" match {retention_info['longest_match']}"
        )

    rows_key = digest(rows, args.dtype, length)
    cache = args.output / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    rows_path = cache / f"rows-{rows_key}.npy"
    if not rows_path.is_file():
        np.save(rows_path, rows)

    mask_key = digest(
        sequence_ids,
        length,
        args.min_tokens,
        args.min_documents,
        index.manifest.get("tokens_sha256"),
        args.validation.stat().st_size,
    )
    mask_path = cache / f"masks-{mask_key}.npz"
    if mask_path.is_file():
        stored = np.load(mask_path)
        matched, furniture = stored["matched"], stored["furniture"]
        log(f"reusing haunting masks {mask_path}")
    else:
        started = time.perf_counter()
        pieces = len(mask_chunks(sequence_ids, length))
        workers = max(1, min(args.workers, pieces))
        log(f"haunting masks: {pieces} chunks on {workers} worker(s)")
        with ProcessPoolExecutor(
            max_workers=workers,
            mp_context=multiprocessing.get_context("spawn"),
            initializer=_init_mask_worker,
            initargs=(args.index, args.validation, args.min_tokens, args.min_documents),
        ) as pool:
            matched, furniture = label_masks(
                index,
                tokens,
                sequence_ids,
                length,
                min_tokens=args.min_tokens,
                min_documents=args.min_documents,
                progress=lambda done, total: (
                    log(f"haunting masks: chunk {done}/{total}")
                    if done % 16 == 0 or done == total
                    else None
                ),
                mapper=lambda pieces: pool.map(_mask_chunk, pieces),
            )
        np.savez(mask_path, matched=matched, furniture=furniture)
        log(
            f"haunting masks over {len(sequence_ids)} rows: {time.perf_counter() - started:.0f}s"
        )

    slices: dict[str, np.ndarray] = {}
    slice_info: dict[str, dict] = {}
    for name, ids in slice_ids.items():
        indices = np.array([row_of[int(sequence)] for sequence in ids], dtype=np.int64)
        slices[name] = indices
        slice_info[name] = {
            "sequences": len(indices),
            "tokens": int(len(indices) * length),
            "sequence_ids": [int(value) for value in ids],
            "furniture_fraction": float(furniture[indices].mean()),
            "matched_fraction": float(matched[indices].mean()),
            **slice_docs.get(name, {}),
        }
    return Prepared(
        rows_path,
        rows_key,
        slices,
        slice_info,
        matched,
        furniture,
        len(validation_rows),
        retention_rows,
        retention_info,
    )


def evaluate_checkpoint(
    args: argparse.Namespace,
    checkpoint: Checkpoint,
    prepared: Prepared,
    index: HauntingIndex,
    prompts_sha256: str,
) -> dict:
    result: dict = {
        "name": checkpoint.name,
        "path": str(checkpoint.path),
        "blind_id": checkpoint.blind_id,
        "losses": {},
    }
    if not args.skip_losses:
        output = loss_output(args, checkpoint, prepared.rows_key)
        result["loss_meta"] = run_losses(args, checkpoint, prepared.rows_path, output)
        stored = np.load(output)
        losses, correct = stored["losses"], stored["correct"]
        for name, indices in prepared.slices.items():
            result["losses"][name] = summarize_losses(
                losses[indices],
                correct[indices],
                prepared.matched[indices],
                prepared.furniture[indices],
            )
        if prepared.retention_rows is not None:
            result["retention"] = summarize_losses(
                losses[prepared.retention_rows], correct[prepared.retention_rows]
            )
        summary = result["losses"]
        log(
            f"{checkpoint.name}: "
            + ", ".join(
                f"{name} {fmt(values['loss'])}/{fmt(values['furniture_free_loss'])}"
                for name, values in summary.items()
            )
            + (
                f", retention {fmt(result['retention']['loss'])}"
                if "retention" in result
                else ""
            )
        )
    if not args.skip_generation:
        output = args.output / "generations" / f"{checkpoint.blind_id}.jsonl"
        result["generation_meta"] = run_generation(args, checkpoint, output)
        result["generation_meta"]["prompts_sha256"] = prompts_sha256
        if not args.skip_memorization:
            tokenizer = load_tokenizer_file(
                checkpoint_tokenizer_file(checkpoint, args.tokenizer)
            )
            records = []
            for generation in read_jsonl(output):
                encoded = tokenizer.encode(
                    generation["completion"], add_special_tokens=False
                )
                scan = scan_generation_text(
                    index,
                    encoded.ids,
                    thresholds=args.thresholds,
                    min_documents=args.min_documents,
                    tokenizer=tokenizer,
                )
                records.append(
                    {
                        "checkpoint": checkpoint.name,
                        "blind_id": checkpoint.blind_id,
                        "prompt_id": generation["prompt_id"],
                        "kind": generation["kind"],
                        "sampled_tokens": len(generation["tokens"]),
                        **scan,
                    }
                )
            result["memorization_records"] = records
            result["memorization"] = summarize_memorization(records, args.thresholds)
            memo = result["memorization"]
            log(
                f"{checkpoint.name}: memorization coverage "
                + " ".join(f">={t}: {pct(v)}" for t, v in memo["coverage"].items())
                + f", furniture {pct(memo['furniture_fraction'])},"
                f" longest {memo['longest_match']}"
            )
    return result


def write_outputs(
    args: argparse.Namespace, report: dict, checkpoints: list[Checkpoint]
) -> None:
    output = args.output
    (output / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output / "report.md").write_text(render_report(report), encoding="utf-8")
    with (output / "memorization.jsonl").open("w", encoding="utf-8") as sink:
        for checkpoint in report["checkpoints"]:
            for record in checkpoint.get("memorization_records", []):
                sink.write(json.dumps(record, ensure_ascii=False) + "\n")
            if "memorization" in checkpoint:
                summary = {
                    "type": "summary",
                    "checkpoint": checkpoint["name"],
                    "blind_id": checkpoint["blind_id"],
                    **checkpoint["memorization"],
                }
                sink.write(json.dumps(summary, ensure_ascii=False) + "\n")
    if not args.skip_generation:
        key_path = output / "generations" / "KEY.json"
        key = (
            json.loads(key_path.read_text(encoding="utf-8"))
            if key_path.is_file()
            else {}
        )
        for checkpoint in checkpoints:
            key[checkpoint.blind_id] = {
                "name": checkpoint.name,
                "checkpoint": str(checkpoint.path),
                "updated": report["generated"],
            }
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    run(build_parser().parse_args(argv))


def run(args: argparse.Namespace) -> dict:
    args.jax_python = args.jax_python.expanduser()
    args.mlx_python = args.mlx_python.expanduser()
    names = [checkpoint.name for checkpoint in args.checkpoint]
    if len(set(names)) != len(names):
        raise SystemExit("checkpoint names must be unique")
    started = time.perf_counter()
    args.output.mkdir(parents=True, exist_ok=True)
    index = HauntingIndex.load(args.index)
    tokenizer = load_tokenizer_file(args.tokenizer)
    prepared = prepare(args, index, tokenizer)
    prompts_sha256 = (
        hashlib.sha256(args.prompts.read_bytes()).hexdigest()
        if args.prompts.is_file()
        else ""
    )
    report = {
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "settings": {
            "validation": str(args.validation),
            "index": str(args.index),
            "index_tokens_sha256": index.manifest.get("tokens_sha256"),
            "prompts": str(args.prompts),
            "prompts_sha256": prompts_sha256,
            "families": str(args.families) if args.families.is_file() else None,
            "sequence_length": args.sequence_length,
            "sequences": list(args.sequences),
            "clean_sequences": args.clean_sequences,
            "min_tokens": args.min_tokens,
            "min_documents": args.min_documents,
            "thresholds": list(args.thresholds),
            "dtype": args.dtype,
            "batch": args.batch,
            "parallel": args.parallel,
            "max_new_tokens": args.max_new_tokens,
            "temperature": args.temperature,
            "top_p": args.top_p,
            "repetition_penalty": args.repetition_penalty,
            "tokenizer": str(args.tokenizer),
        },
        "slices": prepared.slice_info,
        "retention": prepared.retention_info,
        "checkpoints": [],
    }
    if not args.skip_losses and args.parallel > 1:
        log(f"losses: up to {args.parallel} JAX workers in parallel")
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            list(
                pool.map(
                    lambda checkpoint: run_losses(
                        args,
                        checkpoint,
                        prepared.rows_path,
                        loss_output(args, checkpoint, prepared.rows_key),
                    ),
                    args.checkpoint,
                )
            )
    for checkpoint in args.checkpoint:
        report["checkpoints"].append(
            evaluate_checkpoint(args, checkpoint, prepared, index, prompts_sha256)
        )
        write_outputs(args, report, args.checkpoint)
    report["seconds"] = round(time.perf_counter() - started, 1)
    write_outputs(args, report, args.checkpoint)
    log(f"done in {report['seconds']}s: {args.output / 'report.md'}")
    return report


if __name__ == "__main__":
    main()
