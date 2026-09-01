#!/usr/bin/env python3
"""Create a small, real-text token stream for accelerator smoke benchmarks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--text-field", default="text")
    parser.add_argument(
        "--tokenizer",
        default="tiiuae/Falcon-H1-Tiny-90M-Base",
    )
    parser.add_argument(
        "--revision",
        default="7994372e93b62822ae25f8bfb19f653649cea3a3",
    )
    parser.add_argument("--max-records", type=int, default=256)
    parser.add_argument("--max-tokens", type=int, default=32_768)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    tokenizer = AutoTokenizer.from_pretrained(
        args.tokenizer,
        revision=args.revision,
    )
    eos = tokenizer.eos_token_id
    token_ids: list[int] = []
    records = 0
    with args.jsonl.open() as source:
        for line_number, line in enumerate(source, start=1):
            if records >= args.max_records or len(token_ids) >= args.max_tokens:
                break
            record = json.loads(line)
            text = record.get(args.text_field)
            if not isinstance(text, str):
                raise TypeError(
                    f"{args.jsonl}:{line_number}: {args.text_field!r} is not text"
                )
            ids = tokenizer.encode(text, add_special_tokens=False)
            token_ids.extend(ids)
            if eos is not None:
                token_ids.append(eos)
            records += 1

    token_ids = token_ids[: args.max_tokens]
    if len(token_ids) < 2:
        raise ValueError("fewer than two tokens were produced")
    if max(token_ids) > np.iinfo(np.uint32).max:
        raise ValueError("token id does not fit uint32")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.save(args.output, np.asarray(token_ids, dtype=np.uint32), allow_pickle=False)
    report = {
        "status": "ok",
        "source": str(args.jsonl),
        "output": str(args.output),
        "records": records,
        "tokens": len(token_ids),
        "tokenizer": args.tokenizer,
        "revision": args.revision,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
