"""Per-token role classes for a woven room corpus, aligned to train.bin (and to the room holdout).

Classes (uint8): 0 = library (v1) token, 1 = room token outside h turns, 2 = h utterance token (the text
after "h: " plus the blank-line separator that ends the turn), 3 = the "h:" label tokens (the floor
decision). The training kernel maps classes to loss weights (HGHOST_CPT_ROLE_WEIGHTS).

usage: make_weights.py <corpus dir> <room dir> [tokenizer.json]
writes <corpus dir>/train-weights.bin and <corpus dir>/room-validation-weights.bin, plus a summary JSON.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import numpy as np
from tokenizers import Tokenizer

H_TURN = re.compile(r"(?:^|\n\n)(h:)( ?)(.*?)(?=\n\n|\Z)", re.DOTALL)


def classes_for_document(tok: Tokenizer, ids: np.ndarray, eos_id: int) -> np.ndarray:
    """Class per token of one room document (ids exclude nothing: the trailing EOS is class 1)."""
    out = np.ones(ids.shape[0], dtype=np.uint8)
    body = ids[:-1] if ids.shape[0] and ids[-1] == eos_id else ids
    text = tok.decode(body.tolist())
    enc = tok.encode(text, add_special_tokens=False)
    same = len(enc.ids) == body.shape[0] and np.array_equal(np.asarray(enc.ids, dtype=np.int64), body.astype(np.int64))
    if not same:
        # fall back to prefix decoding to recover offsets exactly for this document
        offsets = []
        prev = ""
        for k in range(1, body.shape[0] + 1):
            cur = tok.decode(body[:k].tolist())
            offsets.append((len(prev), len(cur)))
            prev = cur
        text = prev
    else:
        offsets = enc.offsets
    starts = np.asarray([o[0] for o in offsets]); ends = np.asarray([o[1] for o in offsets])
    for m in H_TURN.finditer(text):
        label_a, label_b = m.start(1), m.end(1)
        utt_a = m.start(3) if m.group(3) else m.end(2)
        utt_b = min(len(text), m.end(3) + 2)  # include the "\n\n" that closes the turn
        lab = (starts < label_b) & (ends > label_a)
        utt = (starts < utt_b) & (ends > utt_a)
        out[: body.shape[0]][utt] = 2
        out[: body.shape[0]][lab] = 3
    return out, same


def main() -> None:
    corpus = Path(sys.argv[1]); rooms = Path(sys.argv[2])
    tok = Tokenizer.from_file(sys.argv[3] if len(sys.argv) > 3 else "kaggle/base_model_dataset_public/tokenizer.json")
    manifest = json.loads((corpus / "manifest.json").read_text())
    eos = int(manifest["eos_token_id"])
    room_stream = np.fromfile(rooms / "room-documents.bin", dtype="<u2")
    records = [json.loads(l) for l in (rooms / "room-documents.jsonl").open()]
    started = time.time(); fallbacks = 0
    doc_classes: list[np.ndarray] = []
    for i, r in enumerate(records):
        ids = room_stream[r["offset"]: r["offset"] + r["tokens"]]
        c, same = classes_for_document(tok, ids, eos)
        fallbacks += 0 if same else 1
        doc_classes.append(c)
        if i % 20000 == 0:
            print(f"  {i}/{len(records)} documents, {time.time()-started:.0f}s, fallbacks {fallbacks}", flush=True)
    total = int(manifest["splits"]["train"]["tokens_including_eos"])
    weights = np.zeros(total, dtype=np.uint8)
    placed = 0
    for ins in manifest["insertions"]:
        off = int(ins["v11_offset"])
        for d in ins["documents"]:
            c = doc_classes[d]
            weights[off: off + c.shape[0]] = c
            off += c.shape[0]; placed += c.shape[0]
        assert off - int(ins["v11_offset"]) == int(ins["tokens"]), ins["slot"]
    train_bin = corpus / "train.bin"
    assert train_bin.stat().st_size // 2 == total, (train_bin.stat().st_size // 2, total)
    weights.tofile(corpus / "train-weights.bin")
    # holdout: room-validation.bin is the concatenation of the holdout documents in room-validation.jsonl order
    hold = np.fromfile(corpus / "room-validation.bin", dtype="<u2")
    hrecords = [json.loads(l) for l in (rooms / "room-validation.jsonl").open()]
    hw = np.zeros(hold.shape[0], dtype=np.uint8)
    for r in hrecords:
        ids = hold[r["offset"]: r["offset"] + r["tokens"]]
        c, _ = classes_for_document(tok, ids, eos)
        hw[r["offset"]: r["offset"] + c.shape[0]] = c
    hw.tofile(corpus / "room-validation-weights.bin")
    counts = {int(k): int(v) for k, v in zip(*np.unique(weights, return_counts=True))}
    hcounts = {int(k): int(v) for k, v in zip(*np.unique(hw, return_counts=True))}
    summary = {"train_tokens": total, "room_tokens_placed": placed, "class_counts": counts, "holdout_class_counts": hcounts,
               "fallback_documents": fallbacks, "classes": {"0": "library", "1": "room other", "2": "h utterance", "3": "h label"}}
    (corpus / "weights-summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
