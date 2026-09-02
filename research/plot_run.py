"""Plot the loss curve of an h1jax CPT kernel from its Kaggle log (JSON-lines events).

usage: .venv/bin/python research/plot_run.py <kernel log or extracted .txt> <output png> [--title T]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def read_events(path: Path) -> list[dict]:
    raw = path.read_text()
    lines: list[str] = []
    try:
        entries = json.loads(raw)
        for entry in entries:
            lines.extend(str(entry.get("data", "")).splitlines())
    except (json.JSONDecodeError, AttributeError):
        lines = raw.splitlines()
    events = []
    for line in lines:
        line = line.strip()
        if line.startswith("{"):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", default="")
    parser.add_argument("--epoch-tokens", type=int, default=374_405_212)
    args = parser.parse_args()

    events = read_events(args.log)
    train = [e for e in events if e.get("event") == "train"]
    val = [e for e in events if e.get("event") == "validation"]
    if not train:
        raise SystemExit("no train events found")
    tokens = np.array([e["tokens"] for e in train]) / 1e6
    loss = np.array([e["loss"] for e in train])
    lr = np.array([e.get("learning_rate", np.nan) for e in train])
    tps = np.array([e.get("tokens_per_second", np.nan) for e in train])
    window = max(1, len(loss) // 100)
    smooth = np.convolve(loss, np.ones(window) / window, mode="valid")

    fig, axes = plt.subplots(
        3, 1, figsize=(11, 10), sharex=True, gridspec_kw={"height_ratios": [3, 1, 1]}
    )
    ax = axes[0]
    ax.plot(tokens, loss, color="#bbbbbb", linewidth=0.5, label="train loss (per step)")
    ax.plot(
        tokens[window - 1 :],
        smooth,
        color="#1f4e79",
        linewidth=1.5,
        label=f"train loss (mean of {window})",
    )
    if val:
        vt = np.array([e["tokens"] for e in val]) / 1e6
        ax.plot(
            vt,
            [e["loss"] for e in val],
            "o-",
            color="#c0392b",
            markersize=4,
            label=f"validation ({val[0].get('sequences', '?')} seq)",
        )
        if "fixed_loss" in val[0]:
            ax.plot(
                vt,
                [e["fixed_loss"] for e in val],
                "s--",
                color="#e67e22",
                markersize=3,
                label="fixed 32-seq slice",
            )
    epochs = int(tokens.max() * 1e6 // args.epoch_tokens) + 1
    for k in range(1, epochs + 1):
        x = k * args.epoch_tokens / 1e6
        if x <= tokens.max():
            ax.axvline(x, color="#999999", linestyle=":", linewidth=0.8)
            ax.text(
                x,
                ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else loss.max(),
                f" epoch {k}",
                fontsize=8,
                color="#666666",
                va="top",
            )
    ax.set_ylabel("loss (nats/token)")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title(args.title or str(args.log.name))
    ax.grid(alpha=0.3)
    axes[1].plot(tokens, lr, color="#2e8b57")
    axes[1].set_ylabel("learning rate")
    axes[1].grid(alpha=0.3)
    axes[2].plot(tokens, tps / 1e3, color="#555555", linewidth=0.8)
    axes[2].set_ylabel("K tok/s")
    axes[2].set_xlabel("training tokens (millions)")
    axes[2].grid(alpha=0.3)
    fig.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=130)
    summary = {
        "steps": len(train),
        "first_loss": float(loss[0]),
        "last_smoothed_loss": float(smooth[-1]),
        "min_smoothed_loss": float(smooth.min()),
        "validation": [
            {k: e[k] for k in ("tokens", "loss", "fixed_loss", "accuracy") if k in e}
            for e in val
        ],
        "median_tokens_per_second": float(np.nanmedian(tps)),
    }
    (args.output.with_suffix(".json")).write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "validation"}))
    for e in summary["validation"]:
        print(e)


if __name__ == "__main__":
    main()
