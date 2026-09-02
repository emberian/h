"""Kaggle GPU kernel: evaluate every Falcon-H1 checkpoint found in the attached kernel outputs.

Runs the same evaluator hbox uses (`rollout_eval.py`, shipped in the code dataset): loss slices
(first-512 / clean-512 / retention / room), corpus-prompt generations and the room-prompt pass,
per checkpoint, on the Kaggle GPU. Writes <output>/<name>/{summary.json,generations.jsonl,
room.jsonl,losses/*.npz} plus a combined `table.md` and `table.json`.

Attach: the code dataset (evaluator + inputs), the base-model dataset (tokenizer), the corpus
dataset (validation.bin), the room dataset (room-validation.bin) and, as kernel sources, the TPU
runs whose `tokens-*/` checkpoints should be evaluated.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

LOCAL = os.environ.get("HGHOST_LOCAL") == "1"
OUTPUT = Path(os.environ.get("HGHOST_EVAL_OUTPUT", "/kaggle/working/gpu-room-eval"))
TRANSFORMERS = os.environ.get("HGHOST_EVAL_TRANSFORMERS", "transformers==4.57.6")
SAMPLES = int(os.environ.get("HGHOST_EVAL_SAMPLES", "4"))
ROOM_SAMPLES = int(os.environ.get("HGHOST_EVAL_ROOM_SAMPLES", "8"))
MAX_NEW = int(os.environ.get("HGHOST_EVAL_MAX_NEW", "128"))
ROOM_MAX_NEW = int(os.environ.get("HGHOST_EVAL_ROOM_MAX_NEW", "64"))
BATCH = int(os.environ.get("HGHOST_EVAL_BATCH", "8"))
ROOM_SEQUENCES = int(os.environ.get("HGHOST_EVAL_ROOM_SEQUENCES", "512"))
INCLUDE_BASE = os.environ.get("HGHOST_EVAL_INCLUDE_BASE", "1") == "1"
CHECKPOINT_GLOB = os.environ.get("HGHOST_EVAL_CHECKPOINTS", "/kaggle/input/**/tokens-*/config.json")
MAX_CHECKPOINTS = int(os.environ.get("HGHOST_EVAL_MAX_CHECKPOINTS", "12"))
OUTPUT.mkdir(parents=True, exist_ok=True)


def emit(event: str, **values) -> None:
    print(json.dumps({"event": event, **values}, default=str), flush=True)


def exactly_one(pattern: str) -> Path:
    matches = sorted(Path(p) for p in glob.glob(pattern, recursive=True) if Path(p).is_file())
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {pattern!r}, found: {matches}")
    return matches[0]


if not LOCAL:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", TRANSFORMERS, "accelerate"],
        check=True,
    )
    inputs = "/kaggle/input"
    evaluator = exactly_one(f"{inputs}/**/rollout_eval.py")
    base_root = exactly_one(f"{inputs}/**/preflight-manifest.json").parent
    validation = exactly_one(f"{inputs}/**/hghost-curated-tokens-v1/**/validation.bin")
    room_validation = sorted(glob.glob(f"{inputs}/**/room-validation.bin", recursive=True))
    slices = exactly_one(f"{inputs}/**/slices.json")
    masks = exactly_one(f"{inputs}/**/masks.npz")
    prompts = exactly_one(f"{inputs}/**/prompts.json")
    retention = exactly_one(f"{inputs}/**/retention.txt")
    room_prompts = exactly_one(f"{inputs}/**/room_prompts.json")
else:
    root = Path(os.environ["HGHOST_ROOT"])
    evaluator = root / "hbox_training/rollout_eval.py"
    base_root = Path(os.environ["HGHOST_BASE_DIR"])
    validation = root / "artifacts/tokenized/validation.bin"
    room_validation = [str(root / "artifacts/roommix/room-validation.bin")]
    slices = Path(os.environ.get("HGHOST_SLICES", root / "research/results/hbox-rollouts/inputs/slices.json"))
    masks = root / "research/results/hbox-rollouts/inputs/masks.npz"
    prompts = root / "research/eval/prompts.json"
    retention = root / "research/eval/retention.txt"
    room_prompts = root / "research/eval/room_prompts.json"

import torch

emit(
    "hardware",
    cuda=torch.cuda.is_available(),
    device=torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
    torch=torch.__version__,
)

# ------------------------------------------------------------------ checkpoints: weights + base tokenizer
TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json")
staged = OUTPUT / "checkpoints"
staged.mkdir(exist_ok=True)
found = sorted(Path(p).parent for p in glob.glob(CHECKPOINT_GLOB, recursive=True))
if LOCAL and os.environ.get("HGHOST_EVAL_LOCAL_CHECKPOINTS"):
    found = [Path(p) for p in os.environ["HGHOST_EVAL_LOCAL_CHECKPOINTS"].split(",")]
found = found[-MAX_CHECKPOINTS:]
targets: list[tuple[str, Path]] = []
if INCLUDE_BASE:
    targets.append(("base", base_root))
for ckpt in found:
    run_name = ckpt.parent.name
    name = f"{run_name}-{ckpt.name.replace('tokens-', 't')}"
    dest = staged / name
    dest.mkdir(exist_ok=True)
    for item in ckpt.iterdir():
        if item.name == "optimizer.msgpack":
            continue
        target = dest / item.name
        if not target.exists():
            try:
                os.symlink(item, target)
            except OSError:
                shutil.copy2(item, target)
    for name_ in TOKENIZER_FILES:
        src = base_root / name_
        if src.exists() and not (dest / name_).exists():
            shutil.copy2(src, dest / name_)
    targets.append((name, dest))
emit("checkpoints", names=[n for n, _ in targets], sources=[str(p) for p in found])

# ------------------------------------------------------------------ evaluate
results = {}
for name, path in targets:
    started = time.time()
    cmd = [
        sys.executable, str(evaluator),
        "--checkpoint", f"{name}={path}",
        "--output", str(OUTPUT),
        "--slices", str(slices), "--validation", str(validation), "--masks", str(masks),
        "--prompts", str(prompts), "--retention", str(retention),
        "--room-prompts", str(room_prompts),
        "--kernel", "reference", "--reference-tolerance", "100", "--batch", str(BATCH),
        "--samples", str(SAMPLES), "--max-new-tokens", str(MAX_NEW),
        "--room-samples", str(ROOM_SAMPLES), "--room-max-new-tokens", str(ROOM_MAX_NEW),
    ]
    if room_validation:
        cmd += ["--room-validation", room_validation[0], "--room-validation-sequences", str(ROOM_SEQUENCES)]
    if os.environ.get("HGHOST_EVAL_EXTRA_ARGS"):
        cmd += os.environ["HGHOST_EVAL_EXTRA_ARGS"].split()
    emit("evaluate_start", name=name, path=str(path))
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    (OUTPUT / f"{name}.log").write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
    summary_path = OUTPUT / name / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else None
    results[name] = {"returncode": proc.returncode, "seconds": round(time.time() - started, 1), "summary": summary}
    emit("evaluate_done", name=name, returncode=proc.returncode, seconds=results[name]["seconds"],
         slices={k: round(v["mean_loss"], 4) for k, v in (summary or {}).get("slices", {}).items()
                 if isinstance(v, dict) and "mean_loss" in v})
    if proc.returncode != 0:
        print(proc.stderr[-3000:], flush=True)

# ------------------------------------------------------------------ table
def cell(summary, key):
    try:
        return f"{summary['slices'][key]['mean_loss']:.4f}"
    except (KeyError, TypeError):
        return "-"

keys = ["first-32", "first-512", "clean-512", "retention", "room"]
lines = ["| checkpoint | " + " | ".join(keys) + " | greedy room reply (prompt 0) |", "|---|" + "---:|" * len(keys) + "---|"]
for name, r in results.items():
    reply = "-"
    room_file = OUTPUT / f"room-{name}.jsonl"
    if room_file.exists():
        for line in room_file.read_text().splitlines():
            d = json.loads(line)
            if d.get("mode", d.get("kind")) in ("greedy",) and d.get("prompt_index", d.get("index", 0)) == 0:
                reply = str(d.get("completion", d.get("text", "")))[:100].replace("|", "/")
                break
    lines.append(f"| {name} | " + " | ".join(cell(r["summary"], k) for k in keys) + f" | {reply} |")
(OUTPUT / "table.md").write_text("\n".join(lines) + "\n")
(OUTPUT / "table.json").write_text(json.dumps(results, indent=1, default=str))
print("\n".join(lines), flush=True)
emit("complete", checkpoints=len(results), failed=[n for n, r in results.items() if r["returncode"] != 0])
print("GPU_ROOM_EVAL_OK", flush=True)
