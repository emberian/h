#!/usr/bin/env python3
"""Harvest a downloaded Kaggle TPU kernel output into the durable checkpoint tree.

usage: harvest_kernel.py <download-dir> [--delete-scratch]
  <download-dir>  e.g. scratchpad/tpu-queue/h-ghost-h1jax-leaf-s1-e1 (from kaggle/tpu_queue.sh)

Copies <run>/tokens-*/ checkpoints and the run metadata to artifacts/checkpoints/tpu/<kernel>/<run>/, repairs
HF configs written by older h1jax wheels (float `mamba_expand`, `Infinity` in `time_step_limit`), converts the
Kaggle JSON log into a plain JSONL event log next to them, prints the validation trajectory, the run minutes,
and a ready-made TPU_LEDGER row. With --delete-scratch, removes the download directory afterwards.
"""
import json, shutil, sys
from pathlib import Path

src = Path(sys.argv[1]).resolve(); delete = "--delete-scratch" in sys.argv
kernel = src.name
root = Path("artifacts/checkpoints/tpu") / kernel
runs = [p for p in src.iterdir() if p.is_dir() and p.name not in ("jax-cache",)]
events = []
for log in src.glob("*.log"):
    if log.name == "download.log": continue
    raw = log.read_text()
    try:
        entries = json.loads(raw)
    except json.JSONDecodeError:
        entries = []
        for line in raw.splitlines():
            if line.startswith("{"):
                try: entries.append({"stream_name": "stdout", "time": 0, "data": line})
                except Exception: pass
    for e in entries:
        d = e.get("data", "")
        if e.get("stream_name") == "stdout" and d.startswith("{"):
            try: events.append(json.loads(d))
            except json.JSONDecodeError: pass
    last_time = max((e.get("time", 0) for e in entries), default=0)
vals = [e for e in events if e.get("event") == "validation"]
for run in runs:
    dest = root / run.name; dest.mkdir(parents=True, exist_ok=True)
    for item in run.iterdir():
        target = dest / item.name
        if item.is_dir():
            if not target.exists(): shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
        cfg = target / "config.json"
        if item.is_dir() and cfg.exists():
            c = json.loads(cfg.read_text())
            changed = False
            if isinstance(c.get("mamba_expand"), float):
                # Older wheels wrote d_ssm / hidden (1.5); loaders want the integer the base config uses (2).
                c["mamba_expand"] = max(1, -(-int(c["mamba_d_ssm"]) // int(c["hidden_size"]))); changed = True
            if isinstance(c.get("time_step_limit"), list) and any(x in (float("inf"),) for x in c["time_step_limit"]):
                c.pop("time_step_limit"); changed = True
            if changed: cfg.write_text(json.dumps(c, indent=2) + "\n")
    (dest / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    print(f"harvested {run.name} -> {dest} ({len(events)} events)")
traj = [(v.get("tokens"), round(v.get("loss", float('nan')), 4)) for v in vals]
print("validation:", traj[0] if traj else None, "...", traj[-1] if traj else None)
minutes = round(last_time / 60) if events else None
finals = [v for v in vals if v.get("final")]
final_loss = round(finals[-1]["loss"], 3) if finals else None
print(f"minutes~{minutes} final_val={final_loss}")
print(f"| {kernel} | est {minutes} min | COMPLETE: final val {final_loss} |")
if delete:
    shutil.rmtree(src); print("deleted", src)
