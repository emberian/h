"""Build corpus-v1.5-replay-15b: the corpus-v1.3-room-15b train stream with the SAME general-English
replay documents as corpus-v1.5-replay woven in, re-tokenized for the Falcon-H1-1.5B-Deep tokenizer.

corpus-v1.5-replay (32,768-vocab) was built by `make_replay.py`: 57,241 fineweb-edu documents inserted
at evenly spaced document boundaries of the room stream. This script takes that replay stream
(`replay-documents.bin`, 90M-tokenized), recovers the text by decoding it with the 90M tokenizer
(verified exact: re-encoding reproduces every id), encodes it with the 1.5B tokenizer (65,536 vocab,
EOS 11), and weaves the documents into the 65,536-vocab room stream with the same slot rule
(`slot_k = floor(k * (base_documents + 1) / replay_documents)`). The base bytes are untouched outside
the insertions; the uint8 class sidecar is woven in lockstep with class 0 for every replay token;
validation.bin, room-validation.bin and the other held-out files are copied byte-identical.

usage: make_replay_15b.py <replay dir> <15b corpus dir> <out dir> [--kaggle-id ID]
  replay dir     output of `make_replay.py fetch` (replay-documents.bin/.jsonl, replay-manifest.json)
  15b corpus dir artifacts/roommix-15b/corpus-v1.3-room-15b
  out dir        artifacts/roommix-15b/corpus-v1.5-replay-15b
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hghost.beliefgeo import (  # noqa: E402
    derive_validation_report,
    document_bounds,
    verify_weave,
    weave_stream,
)
from make_replay import (  # noqa: E402
    EOS_ID,
    SOURCE,
    even_slots,
    log,
    sha256_file,
    verify_sidecar,
    weave_sidecar,
    write_json,
)

SOURCE_TOKENIZER = ROOT / "kaggle/base_model_dataset_public/tokenizer.json"
TARGET_TOKENIZER = ROOT / "artifacts/models/falcon-h1-1.5b-deep-base/tokenizer.json"
SOURCE_VOCAB = 32768
TARGET_VOCAB = 65536
KAGGLE_TITLE = "H Ghost corpus v1-5 replay for H1 1-5B Deep"


def retokenize(replay_dir: Path) -> tuple[list[np.ndarray], list[dict], dict]:
    """The replay documents as 1.5B-tokenizer arrays (EOS-terminated), their provenance rows, and stats."""

    from tokenizers import Tokenizer

    manifest = json.loads((replay_dir / "replay-manifest.json").read_text())
    if manifest["vocab_size"] != SOURCE_VOCAB or manifest["eos_token_id"] != EOS_ID:
        raise SystemExit("replay dir is not a 32,768-vocab / EOS-11 replay stream")
    bin_path = replay_dir / "replay-documents.bin"
    if sha256_file(bin_path) != manifest["files"]["replay-documents.bin"]["sha256"]:
        raise SystemExit("replay-documents.bin does not match replay-manifest.json")
    stream = np.fromfile(bin_path, dtype="<u2")
    if stream.shape[0] != manifest["tokens"]:
        raise SystemExit("replay token count differs from replay-manifest.json")
    starts, ends = document_bounds(stream, EOS_ID)
    if starts.shape[0] != manifest["documents"]:
        raise SystemExit("replay document count differs from replay-manifest.json")
    rows = [json.loads(line) for line in (replay_dir / "replay-documents.jsonl").read_text().splitlines()]
    if len(rows) != starts.shape[0]:
        raise SystemExit("replay-documents.jsonl row count differs from the stream")

    source = Tokenizer.from_file(str(SOURCE_TOKENIZER))
    target = Tokenizer.from_file(str(TARGET_TOKENIZER))
    if source.get_vocab_size(True) != SOURCE_VOCAB or target.get_vocab_size(True) != TARGET_VOCAB:
        raise SystemExit("tokenizer vocabulary sizes are not 32,768 / 65,536")
    documents: list[np.ndarray] = []
    provenance: list[dict] = []
    mismatches = 0
    offset = 0
    total_source = 0
    minimum, maximum = TARGET_VOCAB, -1
    started = time.perf_counter()
    batch = 1024
    for begin in range(0, starts.shape[0], batch):
        ids = [stream[a : b - 1].tolist() for a, b in zip(starts[begin : begin + batch], ends[begin : begin + batch])]
        texts = [source.decode(doc, skip_special_tokens=False) for doc in ids]
        back = source.encode_batch(texts, add_special_tokens=False)
        fresh = target.encode_batch(texts, add_special_tokens=False)
        for index, (doc, again, encoding) in enumerate(zip(ids, back, fresh)):
            if again.ids != doc:
                mismatches += 1
            arr = np.asarray(encoding.ids + [EOS_ID], dtype="<u2")
            if arr.max() >= TARGET_VOCAB:
                raise SystemExit(f"token id {int(arr.max())} out of range in replay document {begin + index}")
            documents.append(arr)
            row = rows[begin + index]
            provenance.append(
                {
                    "index": begin + index,
                    "offset": offset,
                    "tokens": int(arr.shape[0]),
                    "tokens_32k": int(len(doc) + 1),
                    "id": row["id"],
                    "url": row["url"],
                    "dump": row["dump"],
                    "source_token_count": row["source_token_count"],
                    "score": row["score"],
                }
            )
            offset += int(arr.shape[0])
            total_source += len(doc) + 1
            minimum = min(minimum, int(arr.min()))
            maximum = max(maximum, int(arr.max()))
        if (begin // batch) % 8 == 0:
            log(f"retokenized {min(begin + batch, starts.shape[0])}/{starts.shape[0]} documents")
    if mismatches:
        raise SystemExit(f"{mismatches} replay documents did not round-trip through the 90M tokenizer")
    stats = {
        "source_tokenizer": "tiiuae/Falcon-H1-Tiny-90M-Base",
        "source_tokenizer_file": str(SOURCE_TOKENIZER.relative_to(ROOT)),
        "source_tokenizer_sha256": sha256_file(SOURCE_TOKENIZER),
        "source_tokens": int(total_source),
        "roundtrip": "decode(90M) then encode(90M) reproduced every document id-for-id",
        "roundtrip_mismatches": 0,
        "target_tokenizer": "tiiuae/Falcon-H1-1.5B-Deep-Base",
        "target_tokenizer_file": str(TARGET_TOKENIZER.relative_to(ROOT)),
        "target_tokenizer_sha256": sha256_file(TARGET_TOKENIZER),
        "tokens": int(offset),
        "tokens_ratio": offset / total_source,
        "documents": len(documents),
        "minimum_token_id": minimum,
        "maximum_token_id": maximum,
        "seconds": round(time.perf_counter() - started, 3),
    }
    log(f"retokenized {len(documents)} documents: {total_source} -> {offset} tokens (ratio {offset / total_source:.4f}), max id {maximum}")
    return documents, provenance, stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("replay_dir")
    parser.add_argument("base_dir")
    parser.add_argument("output")
    parser.add_argument("--kaggle-id", default="emberian64/hghost-curated-tokens-v1-5-replay-15b")
    args = parser.parse_args()
    started = time.perf_counter()
    replay_dir, base_dir, output = Path(args.replay_dir), Path(args.base_dir), Path(args.output)

    base_manifest = json.loads((base_dir / "manifest.json").read_text())
    base_report = json.loads((base_dir / "validation-report.json").read_text())
    if base_manifest["vocab_size"] != TARGET_VOCAB or base_manifest["eos_token_id"] != EOS_ID:
        raise SystemExit("base corpus is not a 65,536-vocab / EOS-11 stream")
    base_sha = sha256_file(base_dir / "train.bin")
    if base_sha != base_manifest["splits"]["train"]["sha256"] or base_sha != base_report["splits"]["train"]["sha256"]:
        raise SystemExit("base train.bin does not match its manifest / validation report")
    stream = np.memmap(base_dir / "train.bin", dtype="<u2", mode="r")
    if stream.shape[0] != base_report["splits"]["train"]["tokens_including_eos"]:
        raise SystemExit("base train.bin does not match the token count in its report")
    base_weights = np.memmap(base_dir / "train-weights.bin", dtype=np.uint8, mode="r")
    if base_weights.shape[0] != stream.shape[0]:
        raise SystemExit("base train-weights.bin length differs from train.bin")
    base_weights_sha = sha256_file(base_dir / "train-weights.bin")
    base_documents = int(np.count_nonzero(stream == EOS_ID))
    log(f"base stream {stream.shape[0]} tokens, {base_documents} documents, sha256 {base_sha}")

    documents, provenance, retok = retokenize(replay_dir)
    replay_tokens = sum(int(d.shape[0]) for d in documents)
    slots = even_slots(base_documents, len(documents))

    output.mkdir(parents=True, exist_ok=True)
    log(f"weaving {len(documents)} replay documents ({replay_tokens} tokens) into {base_dir}")
    plan = weave_stream(stream, documents, slots, output / "train.bin", EOS_ID)
    verification = verify_weave(stream, documents, plan, output / "train.bin")
    log(f"verified {verification['v1_tokens_identical']} base tokens identical outside insertions")
    if plan["tokens"] != stream.shape[0] + replay_tokens:
        raise SystemExit("woven token count is not base + replay")
    woven = np.memmap(output / "train.bin", dtype="<u2", mode="r")
    woven_max = int(woven.max())
    if woven_max >= TARGET_VOCAB:
        raise SystemExit(f"woven stream has token id {woven_max} >= {TARGET_VOCAB}")
    del woven

    weave_sidecar(base_weights, plan, output / "train-weights.bin", fill=0)
    sidecar_verification = verify_sidecar(base_weights, plan, output / "train-weights.bin", fill=0)
    log(f"sidecar verified: {sidecar_verification['class_counts']}")

    copied = (
        "validation.bin",
        "room-validation.bin",
        "room-validation-weights.bin",
        "room-validation.jsonl",
        "room-decisions.jsonl",
    )
    for name in copied:
        shutil.copyfile(base_dir / name, output / name)
    with (output / "replay-documents.jsonl").open("w", encoding="utf-8") as handle:
        for row in provenance:
            handle.write(json.dumps(row) + "\n")

    insertions = [
        {
            "slot": group["slot"],
            "v13_offset": group["v1_offset"],
            "v15_offset": group["v11_offset"],
            "documents": group["documents"],
            "tokens": group["tokens"],
        }
        for group in plan["insertions"]
    ]
    replay_manifest = json.loads((replay_dir / "replay-manifest.json").read_text())
    replay_slice = {
        "source": SOURCE,
        "documents": len(documents),
        "tokens": replay_tokens,
        "fraction_actual": replay_tokens / plan["tokens"],
        "fraction_target": 0.125,
        "same_documents_as": "artifacts/roommix/corpus-v1.5-replay (57,241 fineweb-edu documents, streaming order)",
        "filters": replay_manifest["filters"],
        "documents_seen": replay_manifest["documents_seen"],
        "documents_skipped_short": replay_manifest["documents_skipped_short"],
        "documents_skipped_long": replay_manifest["documents_skipped_long"],
        "minimum_token_id": retok["minimum_token_id"],
        "maximum_token_id": retok["maximum_token_id"],
        "retokenization": retok,
        "replay_documents_32k_sha256": replay_manifest["files"]["replay-documents.bin"]["sha256"],
        "replay_manifest_sha256": sha256_file(replay_dir / "replay-manifest.json"),
        "class": 0,
        "insertion_rule": "slot_k = floor(k * (v13_documents + 1) / replay_documents) for replay document k "
        "(evenly spaced, streaming order); a document is written before v1.3-15b document slot "
        "(slot == v13_documents appends); documents sharing a slot are written in index order",
    }
    report = derive_validation_report(base_report, plan, replay_slice)
    report["derived_from"] = {
        "corpus": "hghost curated tokens v1.3 room for H1 1.5B Deep",
        "train_sha256": base_sha,
        "room_mix": base_report["derived_from"]["room_mix"],
        "replay": {k: v for k, v in replay_slice.items()},
    }
    write_json(output / "validation-report.json", report)

    names = ("train.bin", "train-weights.bin", *copied, "replay-documents.jsonl", "validation-report.json")
    files = {name: {"sha256": sha256_file(output / name), "bytes": (output / name).stat().st_size} for name in names}
    if files["train.bin"]["sha256"] != plan["sha256"]:
        raise SystemExit("train.bin hash changed between writing and hashing")
    for name in copied:
        if files[name]["sha256"] != sha256_file(base_dir / name):
            raise SystemExit(f"copied {name} differs from v1.3-15b")
    if files["validation.bin"]["sha256"] != base_report["splits"]["validation"]["sha256"]:
        raise SystemExit("validation.bin does not match the sha256 in the base report")

    manifest = {
        key: base_manifest[key]
        for key in ("schema_version", "format", "dtype", "tokenizer", "vocab_size", "eos_token_id", "room_format", "resident")
    }
    manifest["corpus"] = "hghost curated tokens v1.5 for H1 1.5B Deep: v1.3-15b room stream + general-English replay"
    manifest["v1"] = base_manifest["v1"]
    manifest["v13_15b"] = {
        "train_bin": str(base_dir / "train.bin"),
        "train_sha256": base_sha,
        "train_tokens": int(stream.shape[0]),
        "train_documents": base_documents,
        "train_weights_sha256": base_weights_sha,
        "manifest_sha256": sha256_file(base_dir / "manifest.json"),
        "validation_report_sha256": sha256_file(base_dir / "validation-report.json"),
        "room_mix": base_manifest["room_mix"],
        "room_insertions_note": "room documents woven into v1 (offsets v1_offset in the v1-15b stream, "
        "v11_offset in the v1.3-15b stream); the v1.5-15b offsets are under replay.insertions",
        "room_insertions": base_manifest["insertions"],
        "verification": base_manifest["verification"],
    }
    manifest["room_mix"] = base_manifest["room_mix"]
    manifest["replay"] = {**replay_slice, "insertions": insertions}
    manifest["holdout"] = base_manifest["holdout"]
    manifest["licenses"] = {**base_manifest["licenses"], "replay": SOURCE["license"]}
    manifest["weights"] = {
        "train": "train-weights.bin",
        "holdout": "room-validation-weights.bin",
        "classes": {"0": "library", "1": "room other", "2": "h utterance", "3": "h label"},
        "class_counts": sidecar_verification["class_counts"],
        "replay_class": 0,
    }
    manifest["splits"] = {
        "train": {"path": "train.bin", "tokens_including_eos": plan["tokens"], **files["train.bin"]},
        "validation": {
            "path": "validation.bin",
            "tokens_including_eos": base_report["splits"]["validation"]["tokens_including_eos"],
            **files["validation.bin"],
        },
    }
    manifest["files"] = files
    manifest["verification"] = {
        "stream": {
            "v13_tokens_identical": verification["v1_tokens_identical"],
            "replay_tokens": verification["synthetic_tokens"],
            "maximum_token_id": woven_max,
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
            "title": KAGGLE_TITLE,
            "id": args.kaggle_id,
            "subtitle": f"65536-vocab uint16 streams, {percent:.1f}% fineweb-edu replay, {room_percent:.1f}% rooms",
            "description": (
                "The hghost curated token corpus v1.3 for Falcon-H1-1.5B-Deep (65,536-token vocabulary, EOS id 11 "
                "after every document; v1 library stream + room mix with scenes v3) with the same general-English "
                "replay documents as corpus v1.5 woven in at evenly spaced document boundaries so that "
                f"{percent:.2f}% of the training tokens are whole documents from HuggingFaceFW/fineweb-edu "
                "(sample-10BT, streaming order, 200-8000 tokens each under the 90M tokenizer; ODC-By 1.0), "
                "re-tokenized for the 1.5B tokenizer. validation.bin, room-validation.bin and "
                "room-validation-weights.bin are byte-identical to v1.3-15b; train-weights.bin is the v1.3-15b "
                "class sidecar woven in lockstep with class 0 (library) for every replay token. Token streams "
                "only, no source text or paths; mixed or unknown source-document licensing. manifest.json records "
                "per-source counts, licenses, every insertion offset, and hashes; replay-documents.jsonl records "
                "the id and url of every replay document."
            ),
            "licenses": [{"name": "unknown"}],
        },
    )
    (output / "README.md").write_text(
        "# H Ghost corpus v1.5 for H1 1.5B Deep: v1.3-15b rooms + general-English replay\n\n"
        "- `train.bin`: the v1.3-15b train stream (v1 re-tokenized for Falcon-H1-1.5B-Deep + room mix) with "
        f"fineweb-edu documents inserted at evenly spaced document boundaries so that {percent:.2f}% of tokens "
        "are replay (uint16 little-endian, EOS 11 after every document, ids < 65,536). v1.3-15b bytes are "
        "identical outside the insertions.\n"
        "- `train-weights.bin`: uint8 class per token of `train.bin` (0 library, 1 room other, 2 h utterance, "
        "3 h label); replay tokens are class 0.\n"
        "- `validation.bin`, `room-validation.bin`, `room-validation-weights.bin`, `room-validation.jsonl`, "
        "`room-decisions.jsonl`: byte-identical to v1.3-15b.\n"
        "- `replay-documents.jsonl`: per replay document its index, offset in the (1.5B-tokenized) replay "
        "stream, token count under both tokenizers, fineweb-edu id, url, dump and score. The documents are "
        "exactly those of corpus-v1.5-replay (32,768 vocab), recovered by decoding and re-encoded.\n"
        "- `manifest.json`: `v1`, `v13_15b`, `room_mix`, `holdout`, `licenses`, `replay` (source, counts, "
        "fraction, retokenization, every insertion with `v13_offset` and `v15_offset`) and `verification`.\n\n"
        f"Replay source: {SOURCE['dataset']} ({SOURCE['config']}), {SOURCE['order']}; "
        f"{replay_slice['documents']} documents, {replay_slice['tokens']} tokens.\n\n"
        "Room format: lines of `<display name>: <text>` separated by one blank line; the resident is `h`; "
        "silence is the absence of a line.\n",
        encoding="utf-8",
    )
    log(
        f"train.bin: {plan['tokens']} tokens, {len(documents)} replay documents ({percent:.3f}%), "
        f"max id {woven_max}, sha256 {plan['sha256']}"
    )


if __name__ == "__main__":
    main()
