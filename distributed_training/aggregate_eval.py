#!/usr/bin/env python3
"""Exactly aggregate additive validation metrics from independent workers."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("partials", nargs="+", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    negative_log_likelihood = 0.0
    predicted_tokens = 0
    correct_tokens = 0
    for path in args.partials:
        with path.open() as source:
            partial = json.load(source)
        negative_log_likelihood += float(partial["negative_log_likelihood_sum"])
        predicted_tokens += int(partial["predicted_token_count"])
        correct_tokens += int(partial.get("correct_token_count", 0))
    if predicted_tokens < 1:
        raise ValueError("aggregate predicted token count is zero")
    mean_nll = negative_log_likelihood / predicted_tokens
    report = {
        "negative_log_likelihood_sum": negative_log_likelihood,
        "predicted_token_count": predicted_tokens,
        "mean_negative_log_likelihood": mean_nll,
        "perplexity": math.exp(mean_nll),
        "correct_token_count": correct_tokens,
        "token_accuracy": correct_tokens / predicted_tokens,
        "partials": [str(path) for path in args.partials],
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
