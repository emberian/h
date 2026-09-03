"""Build corpus-v1.5-replay: the corpus-v1.4-room train stream with general-English replay woven in.

The continued-pretraining "replay" recipe against forgetting: about 15% of the mixed stream is
general web/educational English (HuggingFaceFW/fineweb-edu, sample-10BT) inserted as whole
documents (EOS-terminated) at evenly spaced document boundaries of the v1.4 stream. The v1.4
bytes are untouched outside the insertions; the uint8 class sidecar is woven in lockstep with
class 0 (library) for every replay token.

usage: make_replay.py fetch <replay dir> [--target-tokens N] [--min-tokens 200] [--max-tokens 8000]
                             [--resume-from <prior replay dir>]
       make_replay.py weave <v1.4 corpus dir> <replay dir> <out dir> [--version 1.5]
                             [--kaggle-id ID] [--kaggle-title TITLE]

`fetch` streams fineweb-edu and writes replay-documents.bin (uint16 LE, EOS 11 after every
document), replay-documents.jsonl (provenance per document) and replay-manifest.json. With
`--resume-from`, the rows a prior fetch consumed are re-streamed and checked document by document
against its files (same order, ids, token counts and bytes, so the prior stream is a verified
prefix of the new one), then the fetch continues from the next row to the larger target.
`weave` writes the corpus directory (train.bin, train-weights.bin, copied validation files,
manifest.json, validation-report.json, README.md, dataset-metadata.json) and verifies it;
`--version` names the corpus (1.5: 12.5% replay; 1.6: 25%).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hghost.beliefgeo import (  # noqa: E402
    derive_validation_report,
    document_bounds,
    verify_weave,
    weave_stream,
)

TOKENIZER = ROOT / "kaggle/base_model_dataset_public/tokenizer.json"
EOS_ID = 11
VOCAB_SIZE = 32768
SOURCE = {
    "dataset": "HuggingFaceFW/fineweb-edu",
    "config": "sample-10BT",
    "split": "train",
    "order": "the first documents in streaming order that pass the length filter",
    "license": "ODC-By 1.0 (dataset), subject to the Common Crawl terms of use (source text)",
}
BATCH_ROWS = 512


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 24), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------------------- fetch


def load_prior(replay_dir: Path, args: argparse.Namespace) -> dict:
    """A prior fetch's files, checked against its manifest and against this fetch's filters."""

    manifest = json.loads((replay_dir / "replay-manifest.json").read_text())
    if manifest["filters"]["min_tokens"] != args.min_tokens or manifest["filters"]["max_tokens"] != args.max_tokens:
        raise SystemExit(f"prior fetch used filters {manifest['filters']}, this one {args.min_tokens}-{args.max_tokens}")
    if manifest["tokenizer_file"] != str(TOKENIZER.relative_to(ROOT)) or manifest["eos_token_id"] != EOS_ID:
        raise SystemExit("prior fetch used a different tokenizer or EOS id")
    if manifest["target_tokens"] >= args.target_tokens:
        raise SystemExit("the prior fetch's target is not below this fetch's target; nothing to resume")
    bin_path = replay_dir / "replay-documents.bin"
    bin_sha = sha256_file(bin_path)
    if bin_sha != manifest["files"]["replay-documents.bin"]["sha256"]:
        raise SystemExit("prior replay-documents.bin does not match its manifest")
    tokens = np.memmap(bin_path, dtype="<u2", mode="r")
    if tokens.shape[0] != manifest["tokens"]:
        raise SystemExit("prior replay-documents.bin length differs from its manifest")
    with (replay_dir / "replay-documents.jsonl").open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle]
    if len(rows) != manifest["documents"]:
        raise SystemExit("prior replay-documents.jsonl row count differs from its manifest")
    return {
        "replay_dir": str(replay_dir),
        "manifest": manifest,
        "manifest_sha256": sha256_file(replay_dir / "replay-manifest.json"),
        "documents_sha256": bin_sha,
        "tokens": tokens,
        "rows": rows,
    }


class ReplayWriter:
    """Tokenizes stream rows, applies the length filter, appends kept documents to the replay files.

    While ``prior`` is set and fewer documents have been kept than the prior fetch kept, every kept
    document is also compared with the prior fetch's record and bytes at the same index.
    """

    def __init__(self, tok, bin_handle, jsonl_handle, args: argparse.Namespace, prior: dict | None):
        self.tok = tok
        self.bin_handle = bin_handle
        self.jsonl_handle = jsonl_handle
        self.min_tokens = args.min_tokens
        self.max_tokens = args.max_tokens
        self.prior = prior
        self.digest = hashlib.sha256()
        self.total = 0
        self.kept = 0
        self.seen = 0
        self.short = 0
        self.long_ = 0
        self.bad_id = 0
        self.minimum = VOCAB_SIZE
        self.maximum = -1

    def check_prior(self, record: dict, arr: np.ndarray) -> None:
        prior = self.prior
        expected = prior["rows"][record["index"]]
        for key in ("index", "offset", "tokens", "id", "url", "dump", "source_token_count", "score"):
            if record[key] != expected[key]:
                raise SystemExit(
                    f"replay document {record['index']} differs from the prior fetch: "
                    f"{key} {record[key]!r} vs {expected[key]!r}"
                )
        block = prior["tokens"][record["offset"] : record["offset"] + record["tokens"]]
        if not np.array_equal(block, arr):
            raise SystemExit(f"replay document {record['index']} bytes differ from the prior fetch")

    def check_prior_complete(self) -> None:
        manifest = self.prior["manifest"]
        actual = {
            "documents": self.kept,
            "tokens": self.total,
            "documents_seen": self.seen,
            "documents_skipped_short": self.short,
            "documents_skipped_long": self.long_,
            "documents_skipped_bad_id": self.bad_id,
            "minimum_token_id": self.minimum,
            "maximum_token_id": self.maximum,
        }
        for key, value in actual.items():
            if manifest[key] != value:
                raise SystemExit(f"prior fetch {key} {manifest[key]} not reproduced ({value})")
        if self.digest.copy().hexdigest() != self.prior["documents_sha256"]:
            raise SystemExit("re-streamed prefix hash differs from the prior replay-documents.bin")
        log(f"prior fetch reproduced: {self.kept} documents, {self.total} tokens, sha256 {self.prior['documents_sha256']}")

    def flush(self, rows: list[dict], target: int) -> bool:
        """Process a batch; stop (leaving the rest of the batch unexamined) once ``target`` is met."""

        encodings = self.tok.encode_batch([row["text"] for row in rows], add_special_tokens=False)
        for row, encoding in zip(rows, encodings):
            ids = encoding.ids
            n = len(ids)
            if n < self.min_tokens:
                self.short += 1
                continue
            if n > self.max_tokens:
                self.long_ += 1
                continue
            arr = np.asarray(ids + [EOS_ID], dtype="<u2")
            if arr.max() >= VOCAB_SIZE or arr.min() < 0:
                self.bad_id += 1
                continue
            record = {
                "index": self.kept,
                "offset": self.total,
                "tokens": int(arr.shape[0]),
                "id": row["id"],
                "url": row["url"],
                "dump": row["dump"],
                "source_token_count": row["token_count"],
                "score": row["score"],
            }
            if self.prior is not None and self.kept < self.prior["manifest"]["documents"]:
                self.check_prior(record, arr)
            block = arr.tobytes()
            self.bin_handle.write(block)
            self.digest.update(block)
            self.jsonl_handle.write(json.dumps(record) + "\n")
            self.minimum = min(self.minimum, int(arr.min()))
            self.maximum = max(self.maximum, int(arr.max()))
            self.total += int(arr.shape[0])
            self.kept += 1
            if self.total >= target:
                return True
        return False


def run_fetch(args: argparse.Namespace) -> None:
    from datasets import load_dataset
    from tokenizers import Tokenizer

    out = Path(args.replay_dir)
    out.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(str(TOKENIZER))
    if tok.get_vocab_size(True) != VOCAB_SIZE:
        raise SystemExit(f"tokenizer vocab is {tok.get_vocab_size(True)}, expected {VOCAB_SIZE}")
    prior = load_prior(Path(args.resume_from), args) if args.resume_from else None
    # Phase targets: a resumed fetch first reproduces the prior fetch exactly (its target, hence its
    # early stop inside a batch), then continues from the next batch to the new target.
    targets = ([prior["manifest"]["target_tokens"]] if prior else []) + [args.target_tokens]
    dataset = load_dataset(
        SOURCE["dataset"], name=SOURCE["config"], split=SOURCE["split"], streaming=True
    )
    started = time.perf_counter()
    bin_path = out / "replay-documents.bin"
    jsonl_path = out / "replay-documents.jsonl"
    batch: list[dict] = []

    with bin_path.open("wb") as bin_handle, jsonl_path.open("w", encoding="utf-8") as jsonl_handle:
        writer = ReplayWriter(tok, bin_handle, jsonl_handle, args, prior)
        phase = 0
        done = False
        for row in dataset:
            writer.seen += 1
            batch.append(row)
            if len(batch) >= BATCH_ROWS:
                done = writer.flush(batch, targets[phase])
                batch = []
                if writer.kept and writer.kept % 8192 < BATCH_ROWS:
                    log(
                        f"seen {writer.seen} kept {writer.kept} tokens {writer.total} "
                        f"({writer.total / args.target_tokens:.1%})"
                    )
                if done:
                    if phase + 1 < len(targets):
                        writer.check_prior_complete()
                        phase += 1
                        done = writer.total >= targets[phase]
                    if done:
                        break
        if batch and not done:
            writer.flush(batch, targets[phase])
    unexamined = writer.seen - writer.kept - writer.short - writer.long_ - writer.bad_id
    manifest = {
        "schema_version": 1,
        "source": SOURCE,
        "tokenizer": "tiiuae/Falcon-H1-Tiny-90M-Base",
        "tokenizer_file": str(TOKENIZER.relative_to(ROOT)),
        "vocab_size": VOCAB_SIZE,
        "eos_token_id": EOS_ID,
        "format": "contiguous token IDs; EOS after every document",
        "dtype": "little-endian uint16",
        "filters": {
            "min_tokens": args.min_tokens,
            "max_tokens": args.max_tokens,
            "note": "token counts by this tokenizer, excluding EOS",
        },
        "target_tokens": args.target_tokens,
        "documents_seen": writer.seen,
        "documents_skipped_short": writer.short,
        "documents_skipped_long": writer.long_,
        "documents_skipped_bad_id": writer.bad_id,
        "documents_unexamined": unexamined,
        "documents_unexamined_note": f"rows of a {BATCH_ROWS}-row batch after the row that met a target; "
        "consumed from the stream (counted in documents_seen) but neither kept nor filtered",
        "documents": writer.kept,
        "tokens": writer.total,
        "minimum_token_id": writer.minimum,
        "maximum_token_id": writer.maximum,
        "files": {
            "replay-documents.bin": {"sha256": writer.digest.hexdigest(), "bytes": writer.total * 2},
            "replay-documents.jsonl": {
                "sha256": sha256_file(jsonl_path),
                "bytes": jsonl_path.stat().st_size,
            },
        },
        "seconds": round(time.perf_counter() - started, 3),
    }
    if prior is not None:
        manifest["resumed_from"] = {
            "replay_dir": prior["replay_dir"],
            "replay_manifest_sha256": prior["manifest_sha256"],
            "replay_documents_sha256": prior["documents_sha256"],
            "target_tokens": prior["manifest"]["target_tokens"],
            "documents": prior["manifest"]["documents"],
            "tokens": prior["manifest"]["tokens"],
            "documents_seen": prior["manifest"]["documents_seen"],
            "verification": "the prior fetch's rows were re-streamed, re-tokenized and compared document by "
            "document (index, offset, token count, id, url, dump, score, bytes) with its files, and its "
            "counters and replay-documents.bin hash were reproduced before the fetch continued; the prior "
            "stream is the first documents_seen rows and the first tokens bytes of this one",
        }
    if sha256_file(bin_path) != manifest["files"]["replay-documents.bin"]["sha256"]:
        raise SystemExit("replay-documents.bin hash changed between writing and hashing")
    write_json(out / "replay-manifest.json", manifest)
    log(
        f"replay: {writer.kept} documents, {writer.total} tokens (seen {writer.seen}, short {writer.short}, "
        f"long {writer.long_}, bad id {writer.bad_id}, unexamined {unexamined}), "
        f"sha256 {manifest['files']['replay-documents.bin']['sha256']}"
    )


# ----------------------------------------------------------------------------------------- weave


def even_slots(document_count: int, replay_count: int) -> np.ndarray:
    """Evenly spaced slots over 0..document_count (slot k = before base document k; k == n appends)."""

    return np.floor(np.arange(replay_count) * (document_count + 1) / replay_count).astype(np.int64)


def weave_sidecar(base: np.ndarray, plan: dict, output: Path, fill: int = 0) -> None:
    """Write ``base`` (uint8 per token) with ``fill`` inserted for every insertion in ``plan``."""

    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    cursor = 0
    with temporary.open("wb") as handle:
        for group in plan["insertions"]:
            if group["v1_offset"] > cursor:
                handle.write(np.ascontiguousarray(base[cursor : group["v1_offset"]]).tobytes())
                cursor = group["v1_offset"]
            handle.write(np.full(group["tokens"], fill, dtype=np.uint8).tobytes())
        handle.write(np.ascontiguousarray(base[cursor:]).tobytes())
    os.replace(temporary, output)


def verify_sidecar(base: np.ndarray, plan: dict, output: Path, fill: int = 0) -> dict:
    woven = np.memmap(output, dtype=np.uint8, mode="r")
    if woven.shape[0] != plan["tokens"]:
        raise ValueError(f"sidecar has {woven.shape[0]} entries, expected {plan['tokens']}")
    cursor_base = 0
    cursor_woven = 0
    compared = 0
    inserted = 0
    for group in plan["insertions"] + [
        {"v1_offset": base.shape[0], "v11_offset": plan["tokens"], "tokens": 0}
    ]:
        length = group["v1_offset"] - cursor_base
        if length:
            if not np.array_equal(
                woven[cursor_woven : cursor_woven + length],
                base[cursor_base : cursor_base + length],
            ):
                raise ValueError(f"sidecar differs at base offset {cursor_base}")
            compared += length
        start = group["v11_offset"]
        if group["tokens"] and np.any(woven[start : start + group["tokens"]] != fill):
            raise ValueError(f"sidecar insertion at {start} is not class {fill}")
        inserted += group["tokens"]
        cursor_base = group["v1_offset"]
        cursor_woven = start + group["tokens"]
    if compared != base.shape[0] or compared + inserted != plan["tokens"]:
        raise ValueError("coverage mismatch while verifying the sidecar")
    counts = np.bincount(woven, minlength=4)
    return {
        "base_entries_identical": int(compared),
        "replay_entries": int(inserted),
        "replay_class": fill,
        "class_counts": {str(k): int(v) for k, v in enumerate(counts) if v},
        "ok": True,
    }


def run_weave(args: argparse.Namespace) -> dict:
    started = time.perf_counter()
    version = args.version  # "1.5", "1.6": the corpus label
    tag = "v" + version.replace(".", "")  # v15, v16: the offset key of this stream in the manifest
    kaggle_title = args.kaggle_title or f"H Ghost corpus v{version.replace('.', '-')} replay"
    base_dir = Path(args.base_dir)
    replay_dir = Path(args.replay_dir)
    output = Path(args.output)
    base_manifest = json.loads((base_dir / "manifest.json").read_text())
    base_report = json.loads((base_dir / "validation-report.json").read_text())
    replay_manifest = json.loads((replay_dir / "replay-manifest.json").read_text())
    eos_id = int(base_manifest["eos_token_id"])
    if eos_id != EOS_ID or replay_manifest["eos_token_id"] != eos_id:
        raise SystemExit("EOS id mismatch")

    # Base stream: check it is the stream its manifest and report describe.
    base_sha = sha256_file(base_dir / "train.bin")
    if base_sha != base_manifest["splits"]["train"]["sha256"]:
        raise SystemExit("base train.bin does not match its manifest")
    if base_sha != base_report["splits"]["train"]["sha256"]:
        raise SystemExit("base train.bin does not match its validation report")
    stream = np.memmap(base_dir / "train.bin", dtype="<u2", mode="r")
    if stream.shape[0] != base_report["splits"]["train"]["tokens_including_eos"]:
        raise SystemExit("base train.bin does not match the token count in its report")
    base_weights = np.memmap(base_dir / "train-weights.bin", dtype=np.uint8, mode="r")
    if base_weights.shape[0] != stream.shape[0]:
        raise SystemExit("base train-weights.bin length differs from train.bin")
    base_weights_sha = sha256_file(base_dir / "train-weights.bin")
    log(f"base stream {stream.shape[0]} tokens, sha256 {base_sha}")

    # Replay documents.
    replay_sha = sha256_file(replay_dir / "replay-documents.bin")
    if replay_sha != replay_manifest["files"]["replay-documents.bin"]["sha256"]:
        raise SystemExit("replay-documents.bin does not match replay-manifest.json")
    replay = np.fromfile(replay_dir / "replay-documents.bin", dtype="<u2")
    if replay.shape[0] != replay_manifest["tokens"]:
        raise SystemExit("replay token count differs from replay-manifest.json")
    starts, ends = document_bounds(replay, eos_id)
    if starts.shape[0] != replay_manifest["documents"]:
        raise SystemExit("replay document count differs from replay-manifest.json")
    documents = [replay[a:b] for a, b in zip(starts, ends)]
    base_documents = int(np.count_nonzero(stream == eos_id))
    slots = even_slots(base_documents, len(documents))

    output.mkdir(parents=True, exist_ok=True)
    log(f"weaving {len(documents)} replay documents ({replay.shape[0]} tokens) into {base_dir}")
    plan = weave_stream(stream, documents, slots, output / "train.bin", eos_id)
    verification = verify_weave(stream, documents, plan, output / "train.bin")
    log(f"verified {verification['v1_tokens_identical']} base tokens identical outside insertions")
    if plan["tokens"] != stream.shape[0] + replay.shape[0]:
        raise SystemExit("woven token count is not base + replay")

    weave_sidecar(base_weights, plan, output / "train-weights.bin", fill=0)
    sidecar_verification = verify_sidecar(base_weights, plan, output / "train-weights.bin", fill=0)
    log(f"sidecar verified: {sidecar_verification['class_counts']}")

    for name in (
        "validation.bin",
        "room-validation.bin",
        "room-validation-weights.bin",
        "room-validation.jsonl",
        "room-decisions.jsonl",
    ):
        shutil.copyfile(base_dir / name, output / name)
    shutil.copyfile(replay_dir / "replay-documents.jsonl", output / "replay-documents.jsonl")

    insertions = [
        {
            "slot": group["slot"],
            "v14_offset": group["v1_offset"],
            f"{tag}_offset": group["v11_offset"],
            "documents": group["documents"],
            "tokens": group["tokens"],
        }
        for group in plan["insertions"]
    ]
    replay_slice = {
        "source": replay_manifest["source"],
        "documents": int(len(documents)),
        "tokens": int(replay.shape[0]),
        "fraction_actual": float(replay.shape[0] / plan["tokens"]),
        "filters": replay_manifest["filters"],
        "documents_seen": replay_manifest["documents_seen"],
        "documents_skipped_short": replay_manifest["documents_skipped_short"],
        "documents_skipped_long": replay_manifest["documents_skipped_long"],
        "minimum_token_id": int(replay.min()),
        "maximum_token_id": int(replay.max()),
        "replay_documents_sha256": replay_sha,
        "replay_manifest_sha256": sha256_file(replay_dir / "replay-manifest.json"),
        **({"resumed_from": replay_manifest["resumed_from"]} if "resumed_from" in replay_manifest else {}),
        "class": 0,
        "insertion_rule": "slot_k = floor(k * (v14_documents + 1) / replay_documents) for replay document "
        "k (evenly spaced, streaming order); a document is written before v1.4 document slot",
    }
    report = derive_validation_report(base_report, plan, replay_slice)
    report["derived_from"] = {
        "corpus": "hghost curated tokens v1.4 room",
        "train_sha256": base_sha,
        "room_mix": base_report["derived_from"]["room_mix"],
        "replay": {k: v for k, v in replay_slice.items()},
    }
    write_json(output / "validation-report.json", report)

    names = (
        "train.bin",
        "train-weights.bin",
        "validation.bin",
        "room-validation.bin",
        "room-validation-weights.bin",
        "room-validation.jsonl",
        "room-decisions.jsonl",
        "replay-documents.jsonl",
        "validation-report.json",
    )
    files = {
        name: {"sha256": sha256_file(output / name), "bytes": (output / name).stat().st_size}
        for name in names
    }
    if files["train.bin"]["sha256"] != plan["sha256"]:
        raise SystemExit("train.bin hash changed between writing and hashing")
    for name in ("validation.bin", "room-validation.bin", "room-validation-weights.bin"):
        if files[name]["sha256"] != sha256_file(base_dir / name):
            raise SystemExit(f"copied {name} differs from v1.4")
    if files["validation.bin"]["sha256"] != base_report["splits"]["validation"]["sha256"]:
        raise SystemExit("validation.bin does not match the sha256 in the base report")

    manifest = {
        key: base_manifest[key]
        for key in (
            "schema_version",
            "format",
            "dtype",
            "tokenizer",
            "vocab_size",
            "eos_token_id",
            "room_format",
            "resident",
        )
    }
    manifest["corpus"] = f"hghost curated tokens v{version}: v1.4 room stream + general-English replay"
    manifest["v1"] = base_manifest["v1"]
    manifest["v14"] = {
        "train_bin": str(base_dir / "train.bin"),
        "train_sha256": base_sha,
        "train_tokens": int(stream.shape[0]),
        "train_documents": base_documents,
        "train_weights_sha256": base_weights_sha,
        "manifest_sha256": sha256_file(base_dir / "manifest.json"),
        "validation_report_sha256": sha256_file(base_dir / "validation-report.json"),
        "room_mix": base_manifest["room_mix"],
        "room_insertions_note": "room documents woven into v1 (offsets v1_offset in the v1 stream, "
        f"v11_offset in the v1.4 stream); the v{version} offsets are under replay.insertions",
        "room_insertions": base_manifest["insertions"],
        "verification": base_manifest["verification"],
    }
    manifest["room_mix"] = base_manifest["room_mix"]
    manifest["replay"] = {**replay_slice, "insertions": insertions}
    manifest["holdout"] = base_manifest["holdout"]
    manifest["licenses"] = {**base_manifest["licenses"], "replay": replay_manifest["source"]["license"]}
    manifest["weights"] = {
        "train": "train-weights.bin",
        "holdout": "room-validation-weights.bin",
        "classes": {"0": "library", "1": "room other", "2": "h utterance", "3": "h label"},
        "class_counts": sidecar_verification["class_counts"],
        "replay_class": 0,
    }
    manifest["splits"] = {
        "train": {
            "path": "train.bin",
            "tokens_including_eos": plan["tokens"],
            **files["train.bin"],
        },
        "validation": {
            "path": "validation.bin",
            "tokens_including_eos": base_report["splits"]["validation"]["tokens_including_eos"],
            **files["validation.bin"],
        },
    }
    manifest["files"] = files
    manifest["verification"] = {
        "stream": {
            "v14_tokens_identical": verification["v1_tokens_identical"],
            "replay_tokens": verification["synthetic_tokens"],
            "ok": verification["ok"],
        },
        "sidecar": sidecar_verification,
    }
    manifest["seconds"] = round(time.perf_counter() - started, 3)
    write_json(output / "manifest.json", manifest)

    percent = replay_slice["fraction_actual"] * 100
    room_percent = base_manifest["room_mix"]["fraction_actual"] * 100 * stream.shape[0] / plan["tokens"]
    write_json(
        output / "dataset-metadata.json",
        {
            "title": kaggle_title,
            "id": args.kaggle_id,
            "subtitle": (
                f"v1-4 room stream with {replay_slice['tokens'] // 1_000_000}M tokens of "
                "fineweb-edu replay woven in"
            ),
            "description": (
                "The hghost curated token corpus v1.4 (train.bin: v1 stream + stitched room mix) "
                f"with general English replay woven in at document boundaries so that {percent:.2f}% "
                "of the training tokens are whole documents from HuggingFaceFW/fineweb-edu "
                "(sample-10BT, streaming order, 200-8000 tokens each; ODC-By 1.0) - the standard "
                f"continued-pretraining replay recipe against forgetting. Rooms are {room_percent:.2f}% "
                "of the mixed stream. validation.bin, room-validation.bin and "
                "room-validation-weights.bin are byte-identical to v1.4; train-weights.bin is the v1.4 "
                "class sidecar woven in lockstep with class 0 (library) for every replay token. The "
                "corpus portion carries the same caveats as v1: token streams only, no source text or "
                "paths, and mixed or unknown source-document licensing. manifest.json records "
                "per-source counts, licenses, every insertion offset, and hashes; "
                "replay-documents.jsonl records the id and url of every replay document."
            ),
            "licenses": [{"name": "unknown"}],
        },
    )
    (output / "README.md").write_text(
        f"# H Ghost corpus v{version}: v1.4 rooms + general-English replay\n\n"
        "- `train.bin`: the v1.4 train stream (v1 + stitched room mix) with fineweb-edu documents "
        f"inserted at evenly spaced document boundaries so that {percent:.2f}% of tokens are replay "
        "(uint16 little-endian, EOS after every document). v1.4 bytes are identical outside the "
        "insertions.\n"
        "- `train-weights.bin`: uint8 class per token of `train.bin` (0 library, 1 room other, "
        "2 h utterance, 3 h label); the v1.4 sidecar woven in lockstep, replay tokens are class 0.\n"
        "- `validation.bin`: byte-identical to v1 (and v1.4).\n"
        "- `validation-report.json`: v1 schema; `splits.train.sha256` and "
        "`splits.validation.sha256` are what the TPU kernels verify; `derived_from.replay` "
        "describes the replay slice and `derived_from.room_mix` the room slice.\n"
        "- `room-validation.bin` / `room-validation-weights.bin` / `room-validation.jsonl`: "
        "byte-identical to v1.4 (held-out room documents, never in train.bin).\n"
        "- `room-decisions.jsonl`: as v1.4.\n"
        "- `replay-documents.jsonl`: per replay document its index, offset in the replay stream, "
        "token count, fineweb-edu id, url, dump and score.\n"
        "- `manifest.json`: v1.4 sections (`v1`, `v14`, `room_mix`, `holdout`, `licenses`) plus "
        f"`replay` (source, counts, fraction, every insertion with `v14_offset` and `{tag}_offset`) "
        "and `verification`.\n\n"
        f"Replay source: {SOURCE['dataset']} ({SOURCE['config']}), {SOURCE['order']}; "
        f"{replay_slice['documents']} documents, {replay_slice['tokens']} tokens.\n\n"
        "Room format: lines of `<display name>: <text>` separated by one blank line; the "
        "resident is `h`; silence is the absence of a line.\n",
        encoding="utf-8",
    )
    log(
        f"train.bin: {plan['tokens']} tokens, {len(documents)} replay documents "
        f"({percent:.3f}%), sha256 {plan['sha256']}"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch")
    fetch.add_argument("replay_dir")
    fetch.add_argument("--target-tokens", type=int, default=60_000_000)
    fetch.add_argument("--min-tokens", type=int, default=200)
    fetch.add_argument("--max-tokens", type=int, default=8000)
    fetch.add_argument(
        "--resume-from",
        default=None,
        metavar="DIR",
        help="a prior fetch (replay-documents.bin/.jsonl, replay-manifest.json) to verify and continue",
    )
    fetch.set_defaults(func=run_fetch)
    weave = sub.add_parser("weave")
    weave.add_argument("base_dir")
    weave.add_argument("replay_dir")
    weave.add_argument("output")
    weave.add_argument("--version", default="1.5", help="corpus version label (1.5, 1.6)")
    weave.add_argument("--kaggle-id", default="emberian64/hghost-curated-tokens-v1-5-replay")
    weave.add_argument("--kaggle-title", default=None, help='default "H Ghost corpus v<1-x> replay"')
    weave.set_defaults(func=run_weave)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
