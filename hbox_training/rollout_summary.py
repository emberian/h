#!/usr/bin/env python3
"""Mac side of the hbox rollout evaluator: slice export and the results table.

Two subcommands, both run from the repository root with the main environment::

    .venv/bin/python hbox_training/rollout_summary.py slices
    .venv/bin/python hbox_training/rollout_summary.py report research/results/hbox-rollouts/<run>

``slices`` writes ``slices.json`` (the validation sequence ids the evaluation pack uses
for ``first-512`` and ``clean-512``, computed with the pack's own functions) and, when
the evaluation pack's haunting-mask cache is present, ``masks.npz`` with the furniture
and matched masks for those rows. Both travel to hbox with the checkpoints.

``report`` reads the directories ``rollout_eval.py`` produced, runs ``hghost-haunt scan``
over each ``generations.jsonl`` (cached as ``haunt-scan.jsonl`` / ``haunt-summary.json``)
and prints one table: checkpoint x slice losses (plain and furniture-free), loss and
generation throughput, and memorization coverage.

``room`` turns the ``room-<checkpoint>.jsonl`` files of a run into ``room-table.md``:
prompts as rows, checkpoints as columns, the greedy reply per cell, then the same with
one sampled reply.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

from rollout_eval import (
    load_masks,
    load_room_prompts,
    slice_summaries,
)

DEFAULT_INPUTS = Path("research/results/hbox-rollouts/inputs")
DEFAULT_EVALPACK = Path("research/results/evalpack-baseline")
DEFAULT_TOKENIZER = Path("kaggle/base_model_dataset_public/tokenizer.json")
DEFAULT_ROOM_PROMPTS = Path("research/eval/room_prompts.json")
LOSS_SLICES = ("first-32", "first-512", "clean-512", "retention")


def log(message: str) -> None:
    print(f"[rollout-summary] {message}", file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- slices


def export_slices(args: argparse.Namespace) -> None:
    from hghost.evalpack import (
        clean_sequence_ids,
        digest,
        evenly_spaced,
        load_leakage_levels,
    )
    from hghost.haunt import TOKEN_DTYPE, read_document_table, verify_document_layout

    length = args.sequence_length
    report = json.loads(args.validation_report.read_text(encoding="utf-8"))
    validation = report["splits"]["validation"]
    tokens = np.memmap(args.validation, dtype=TOKEN_DTYPE, mode="r")
    if int(tokens.shape[0]) != int(validation["tokens_including_eos"]):
        raise RuntimeError("validation.bin does not match validation-report.json")
    entries = read_document_table(args.dataset, "validation")
    layout = verify_document_layout(tokens, entries, int(report["eos_token_id"]))
    if layout["problems"]:
        raise RuntimeError("validation layout: " + "; ".join(layout["problems"]))
    offsets = np.array([entry.token_offset for entry in entries])

    def documents(ids: np.ndarray) -> int:
        return len(np.unique(np.searchsorted(offsets, ids * length, side="right") - 1))

    slices: dict[str, dict] = {}
    first = np.arange(args.sequences, dtype=np.int64)
    slices[f"first-{args.sequences}"] = {
        "sequence_ids": first.tolist(),
        "documents": documents(first),
    }
    levels = load_leakage_levels(args.families)
    clean_ids, _ = clean_sequence_ids(entries, levels, length, int(tokens.shape[0]))
    chosen = evenly_spaced(clean_ids, args.clean_sequences)
    slices[f"clean-{len(chosen)}"] = {
        "sequence_ids": chosen.tolist(),
        "documents": documents(chosen),
        "clean_sequences_available": len(clean_ids),
    }
    spec = {
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "sequence_length": length,
        "validation": {
            "sha256": validation["sha256"],
            "tokens": int(validation["tokens_including_eos"]),
            "eos_token_id": int(report["eos_token_id"]),
            "dataset_manifest_sha256": report["dataset_manifest_sha256"],
        },
        "families": str(args.families),
        "slices": slices,
        "derived": {
            f"first-{count}": {"slice": f"first-{args.sequences}", "rows": count}
            for count in args.derived
            if count < args.sequences
        },
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "slices.json").write_text(
        json.dumps(spec, indent=1) + "\n", encoding="utf-8"
    )
    log(
        "slices: "
        + ", ".join(
            f"{name} {len(item['sequence_ids'])} rows" for name, item in slices.items()
        )
        + f" -> {args.output / 'slices.json'}"
    )

    # Furniture masks: reuse the evaluation pack's cache when its key matches exactly.
    pack_report = args.evalpack / "report.json"
    if not pack_report.is_file():
        log(f"no evaluation-pack report at {pack_report}; masks.npz not written")
        return
    settings = json.loads(pack_report.read_text(encoding="utf-8"))["settings"]
    union = np.unique(
        np.concatenate(
            [
                np.arange(max(settings["sequences"])),
                *[np.asarray(s["sequence_ids"]) for s in slices.values()],
            ]
        )
    )
    key = digest(
        union,
        length,
        settings["min_tokens"],
        settings["min_documents"],
        settings["index_tokens_sha256"],
        args.validation.stat().st_size,
    )
    cache = args.evalpack / "cache" / f"masks-{key}.npz"
    if not cache.is_file():
        log(f"no mask cache {cache}; masks.npz not written")
        return
    stored = np.load(cache)
    row_of = {int(sequence): row for row, sequence in enumerate(union)}
    exported: dict[str, np.ndarray] = {}
    for name, item in slices.items():
        rows = np.array([row_of[int(s)] for s in item["sequence_ids"]], dtype=np.int64)
        exported[f"{name}.furniture"] = stored["furniture"][rows]
        exported[f"{name}.matched"] = stored["matched"][rows]
        item["furniture_fraction"] = float(exported[f"{name}.furniture"].mean())
        item["matched_fraction"] = float(exported[f"{name}.matched"].mean())
    np.savez(args.output / "masks.npz", **exported)
    spec["masks"] = {
        "source": str(cache),
        "min_tokens": settings["min_tokens"],
        "min_documents": settings["min_documents"],
        "index_tokens_sha256": settings["index_tokens_sha256"],
    }
    (args.output / "slices.json").write_text(
        json.dumps(spec, indent=1) + "\n", encoding="utf-8"
    )
    log(
        "masks: "
        + ", ".join(
            f"{name} furniture {100 * item['furniture_fraction']:.2f}%"
            for name, item in slices.items()
        )
        + f" -> {args.output / 'masks.npz'}"
    )


# --------------------------------------------------------------------------- report


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def haunt_scan(directory: Path, args: argparse.Namespace) -> dict | None:
    generations = directory / "generations.jsonl"
    cached = directory / "haunt-summary.json"
    if not generations.is_file():
        return None
    if cached.is_file() and not args.rescan:
        return read_json(cached)
    command = [
        str(args.haunt),
        "scan",
        "--index",
        str(args.index),
        "--generations",
        str(generations),
        "--output",
        str(directory / "haunt-scan.jsonl"),
        "--tokenizer",
        str(args.tokenizer),
        "--decode",
    ]
    log("run " + " ".join(command))
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    summary = json.loads(completed.stdout.strip().splitlines()[-1])
    cached.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary


def recompute_with_masks(directory: Path, spec: dict, masks: dict) -> dict:
    stored = {}
    for name in spec["slices"]:
        path = directory / "losses" / f"{name}.npz"
        if path.is_file():
            arrays = np.load(path)
            stored[name] = {"losses": arrays["losses"], "correct": arrays["correct"]}
    return slice_summaries(spec, stored, masks)


def fmt(value, digits: int = 4) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def pct(value) -> str:
    return "-" if value is None else f"{100 * value:.1f}%"


def render_table(header: list[str], rows: list[list[str]]) -> str:
    widths = [max(len(str(cell)) for cell in column) for column in zip(header, *rows)]
    lines = [
        "  ".join(
            str(cell).ljust(width) for cell, width in zip(header, widths)
        ).rstrip(),
        "  ".join("-" * width for width in widths),
    ]
    for row in rows:
        lines.append(
            "  ".join(
                str(cell).rjust(width) if index else str(cell).ljust(width)
                for index, (cell, width) in enumerate(zip(row, widths))
            ).rstrip()
        )
    return "\n".join(lines)


def collect(args: argparse.Namespace) -> list[dict]:
    spec = read_json(args.slices) if args.slices and args.slices.is_file() else None
    masks = load_masks(args.masks) if args.masks else {}
    if masks and spec is None:
        raise SystemExit("--masks needs --slices to know the slice layout")
    rows: list[dict] = []
    for run in args.runs:
        run_json = run / "run.json"
        order = (
            list(read_json(run_json)["checkpoints"])
            if run_json.is_file()
            else sorted(p.name for p in run.iterdir() if (p / "summary.json").is_file())
        )
        for name in order:
            directory = run / name
            summary_path = directory / "summary.json"
            if not summary_path.is_file():
                rows.append({"name": name, "run": run.name, "status": "missing"})
                continue
            summary = read_json(summary_path)
            slices = summary.get("slices", {})
            if masks:
                slices = recompute_with_masks(directory, spec, masks)
            rows.append(
                {
                    "name": name,
                    "run": run.name,
                    "directory": directory,
                    "summary": summary,
                    "slices": slices,
                    "haunt": haunt_scan(directory, args) if args.scan else None,
                }
            )
    return rows


def report(args: argparse.Namespace) -> None:
    rows = collect(args)
    baseline = next((row for row in rows if "slices" in row), None)
    header = [
        "checkpoint",
        *LOSS_SLICES,
        "ff first-32",
        "ff first-512",
        "ff clean-512",
        "loss tok/s",
        "gen tok/s",
        "cov>=8",
        "cov>=16",
        "cov>=32",
        "longest",
    ]
    table = []
    for row in rows:
        if "slices" not in row:
            table.append([row["name"], row["status"], *[""] * (len(header) - 2)])
            continue
        slices, summary = row["slices"], row["summary"]
        cells = [row["name"]]
        for name in LOSS_SLICES:
            value = slices.get(name, {}).get("loss")
            cell = fmt(value)
            reference = (
                baseline["slices"].get(name, {}).get("loss") if baseline else None
            )
            if row is not baseline and value is not None and reference is not None:
                cell += f" ({value - reference:+.3f})"
            cells.append(cell)
        for name in ("first-32", "first-512", "clean-512"):
            cells.append(fmt(slices.get(name, {}).get("furniture_free_loss")))
        timings = summary.get("timings", {}).get("losses", {})
        loss_rate = timings.get("first-512", {}).get("tokens_per_second")
        cells.append(f"{loss_rate:,.0f}" if loss_rate else "-")
        generation = summary.get("generation", {})
        cells.append(fmt(generation.get("tokens_per_second"), 1))
        haunt = row.get("haunt") or {}
        coverage = haunt.get("token_weighted_coverage", {})
        cells.extend(pct(coverage.get(t)) for t in ("8", "16", "32"))
        cells.append(str(haunt.get("longest_match", "-")))
        table.append(cells)
    print(render_table(header, table))
    kernels = {
        row["summary"]["kernel"].get("losses") for row in rows if "summary" in row
    }
    checks = [
        f"{row['name']} {row['summary']['kernel_check'].get('reference_path_batch1_loss'):.6f}"
        + (
            f" (expected {row['summary']['kernel_check']['expected_loss']},"
            f" {row['summary']['kernel_check']['expected_delta']:+.6f})"
            if "expected_loss" in row["summary"]["kernel_check"]
            else ""
        )
        for row in rows
        if "summary" in row and "kernel_check" in row["summary"]
    ]
    print()
    print(
        f"loss kernel: {', '.join(sorted(k for k in kernels if k))}; generation: reference path"
    )
    print("first-32 on the reference path at batch 1: " + "; ".join(checks))
    if any(
        "summary" in row and "furniture_free_loss" in row["slices"].get("first-512", {})
        for row in rows
    ):
        print(
            "ff = furniture-free (positions inside page furniture found by the haunting index dropped)"
        )
    if args.samples:
        wanted = set(args.prompt_ids.split(",")) if args.prompt_ids else None
        for row in rows:
            if "directory" not in row:
                continue
            print(f"\n== {row['name']}")
            shown: dict[str, int] = {}
            with (row["directory"] / "generations.jsonl").open(
                encoding="utf-8"
            ) as stream:
                for line in stream:
                    record = json.loads(line)
                    if wanted and record["prompt_id"] not in wanted:
                        continue
                    if shown.get(record["prompt_id"], 0) >= args.samples:
                        continue
                    shown[record["prompt_id"]] = shown.get(record["prompt_id"], 0) + 1
                    text = record["completion"].replace("\n", "\\n")
                    if len(text) > args.width:
                        text = text[: args.width - 3] + "..."
                    print(
                        f"[{record['id']} seed={record['seed']}] {record['prompt']!r} -> {text}"
                    )


# --------------------------------------------------------------------------- room


def visitor_line(prompt: str, limit: int = 44) -> str:
    """The last visitor turn of a room prompt (the line before the trailing ``h:``)."""
    lines = [line.strip() for line in prompt.splitlines() if line.strip()]
    if lines and lines[-1] == "h:":
        lines.pop()
    text = lines[-1] if lines else ""
    return text if len(text) <= limit else text[: limit - 3] + "..."


def cell_text(text: str, width: int) -> str:
    text = text.strip().replace("\n", "\\n").replace("|", "\\|")
    if not text:
        return "(empty)"
    return text if len(text) <= width else text[: width - 3] + "..."


def markdown_table(header: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join(["---"] * len(header)) + "|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def room_table(args: argparse.Namespace) -> None:
    run = args.run
    prompts = load_room_prompts(args.prompts)
    files = {
        path.name[len("room-") : -len(".jsonl")]: path
        for path in sorted(run.glob("room-*.jsonl"))
    }
    if not files:
        raise SystemExit(f"no room-*.jsonl under {run}")
    run_json = run / "run.json"
    order = list(read_json(run_json)["checkpoints"]) if run_json.is_file() else []
    names = [n for n in order if n in files] + [n for n in files if n not in order]
    records = {
        name: [
            json.loads(line)
            for line in files[name].open(encoding="utf-8")
            if line.strip()
        ]
        for name in names
    }

    def reply(name: str, index: int, sample: str) -> str:
        for record in records[name]:
            if record["prompt_index"] == index and record.get("sample") == sample:
                return cell_text(record["text"], args.width)
        return "-"

    header = ["#", "prompt", *names]
    tables = []
    for title, sample in (("Greedy", "greedy"), ("One sample (s0)", "s0")):
        rows = [
            [
                str(prompt["index"]),
                f"{prompt['kind']}: {visitor_line(prompt['prompt'])}",
                *[reply(name, prompt["index"], sample) for name in names],
            ]
            for prompt in prompts
        ]
        tables += ["", f"## {title}", "", markdown_table(header, rows)]
    settings = None
    for name in names:
        summary_path = run / name / "summary.json"
        if summary_path.is_file():
            settings = read_json(summary_path).get("room")
            if settings:
                break
    caption = (
        f"Run `{run.name}`, prompts `{args.prompts}` ({len(prompts)} room prompts, reply cut"
        " at the first newline as the harness does)."
    )
    if settings:
        caption += (
            f" Sampled at temperature {settings['temperature']}, top-p {settings['top_p']},"
            f" repetition penalty {settings['repetition_penalty']}, up to"
            f" {settings['max_new_tokens']} new tokens, seed {settings['seed']} + prompt"
            f" + 100 x sample; {settings['samples_per_prompt']} samples per prompt in the"
            " jsonl files."
        )
    text = "\n".join(["# Room-format completions", "", caption, *tables, ""])
    (run / "room-table.md").write_text(text, encoding="utf-8")
    print(text)
    log(f"wrote {run / 'room-table.md'}")


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    slices = commands.add_parser(
        "slices", help="export slices.json (and masks.npz) for hbox"
    )
    slices.add_argument("--output", type=Path, default=DEFAULT_INPUTS)
    slices.add_argument(
        "--validation", type=Path, default=Path("artifacts/tokenized/validation.bin")
    )
    slices.add_argument(
        "--validation-report",
        type=Path,
        default=Path("artifacts/tokenized/validation-report.json"),
    )
    slices.add_argument("--dataset", type=Path, default=Path("artifacts/dataset"))
    slices.add_argument(
        "--families", type=Path, default=Path("artifacts/families/leakage-report.json")
    )
    slices.add_argument(
        "--evalpack", type=Path, default=DEFAULT_EVALPACK, help="for the mask cache"
    )
    slices.add_argument("--sequence-length", type=int, default=512)
    slices.add_argument("--sequences", type=int, default=512, help="first-N slice")
    slices.add_argument("--clean-sequences", type=int, default=512)
    slices.add_argument(
        "--derived", type=int, nargs="*", default=[32], help="first-N prefixes"
    )
    slices.set_defaults(function=export_slices)

    report_parser = commands.add_parser(
        "report", help="table over returned run directories"
    )
    report_parser.add_argument(
        "runs", type=Path, nargs="+", help="research/results/hbox-rollouts/<run>"
    )
    report_parser.add_argument(
        "--no-scan", dest="scan", action="store_false", help="skip hghost-haunt scan"
    )
    report_parser.add_argument(
        "--rescan", action="store_true", help="ignore cached scans"
    )
    report_parser.add_argument(
        "--haunt", type=Path, default=ROOT / ".venv" / "bin" / "hghost-haunt"
    )
    report_parser.add_argument(
        "--index", type=Path, default=Path("artifacts/haunting-index")
    )
    report_parser.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    report_parser.add_argument(
        "--slices", type=Path, default=DEFAULT_INPUTS / "slices.json"
    )
    report_parser.add_argument(
        "--masks", type=Path, help="recompute furniture-free means from the npz files"
    )
    report_parser.add_argument(
        "--samples", type=int, default=0, help="print N completions per prompt"
    )
    report_parser.add_argument(
        "--prompt-ids", default="", help="comma-separated prompt ids to print"
    )
    report_parser.add_argument("--width", type=int, default=400)
    report_parser.set_defaults(function=report)

    room = commands.add_parser(
        "room", help="room-table.md from a run's room-*.jsonl files"
    )
    room.add_argument("run", type=Path, help="research/results/hbox-rollouts/<run>")
    room.add_argument("--prompts", type=Path, default=DEFAULT_ROOM_PROMPTS)
    room.add_argument("--width", type=int, default=120, help="cell truncation")
    room.set_defaults(function=room_table)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.function(args)


if __name__ == "__main__":
    main()
