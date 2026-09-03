"""Kaggle GPU (T4) kernel: small-scale proof of gpu/cpt_torch.py before the rented H100 day.

Runs cpt_torch.py --tiny on the Falcon-H1-Tiny-90M base over 2M tokens of corpus-v1.5-replay (the
32,768-vocab stream) with T4-sized settings (4 x 2 x 2048 tokens per step, fp16 autocast with fp32
masters; Turing has no bf16), then checks the run the way the H100 day will be checked:

  * every train loss finite, validation losses (library and room) finite and reported;
  * an HF safetensors checkpoint under tokens-*/ that reloads with FalconH1ForCausalLM and reproduces
    the trained model's validation loss (cpt_torch.py --reload-check, plus an independent reload here
    through the same evaluator interface the room-eval kernel uses);
  * throughput (tokens/s) and peak memory, for the H100 projection.

Writes <output>/{summary.json, cpt.log} next to the run directory; prints T4_CPT_TEST_OK at the end.
Attach: the code dataset (cpt_torch.py), the 90M base dataset (preflight-manifest.json verified) and
the corpus-v1.5-replay dataset (validation-report.json sha256 verified).
"""

from __future__ import annotations

import glob
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

STARTED = time.time()
LOCAL = os.environ.get("HGHOST_LOCAL") == "1"
OUTPUT = Path(os.environ.get("HGHOST_T4_OUTPUT", "/kaggle/working/t4-cpt-test"))
TRANSFORMERS = os.environ.get("HGHOST_T4_TRANSFORMERS", "transformers==4.57.6")
MAX_MINUTES = float(os.environ.get("HGHOST_T4_MAX_MINUTES", "26"))
TOKENS = int(os.environ.get("HGHOST_T4_TOKENS", "2000000"))
EXTRA_ARGS = os.environ.get("HGHOST_T4_EXTRA_ARGS", "")
OUTPUT.mkdir(parents=True, exist_ok=True)


def emit(event: str, **values) -> None:
    print(json.dumps({"event": event, "elapsed": round(time.time() - STARTED, 1), **values}, default=str), flush=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def installed(package: str) -> str:
    from importlib.metadata import version

    return version(package)


def exactly_one(pattern: str) -> Path:
    matches = sorted(Path(p) for p in glob.glob(pattern, recursive=True) if Path(p).is_file())
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {pattern!r}, found: {matches}")
    return matches[0]


# ------------------------------------------------------------------ environment and inputs
if not LOCAL:
    torch_pin = f"torch=={installed('torch')}"  # the image's torch is the one that runs on the T4
    cmd = [sys.executable, "-m", "pip", "install", "--quiet", TRANSFORMERS, "accelerate", torch_pin]
    emit("pip_install", command=cmd)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    (OUTPUT / "pip.log").write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
    if proc.returncode != 0:
        print(proc.stderr[-4000:], flush=True)
        raise SystemExit("pip install failed")
    script = exactly_one("/kaggle/input/**/cpt_torch.py")
    base = exactly_one("/kaggle/input/**/hghost-falcon-h1-90m-base-public/**/preflight-manifest.json").parent
    corpus = exactly_one("/kaggle/input/**/hghost-curated-tokens-v1-5-replay/**/validation-report.json").parent
else:
    root = Path(os.environ["HGHOST_ROOT"])
    script = root / "gpu/cpt_torch.py"
    base = root / "kaggle/base_model_dataset_public"
    corpus = root / "artifacts/roommix/corpus-v1.5-replay"

import torch

emit("hardware", cuda=torch.cuda.is_available(), device=torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
     torch=torch.__version__, transformers=installed("transformers"), script=str(script), script_sha256=sha256(script))

manifest = json.loads((base / "preflight-manifest.json").read_text())
weights = base / "model.safetensors"
if not LOCAL and sha256(weights) != manifest["files"]["model.safetensors"]["sha256"]:
    raise SystemExit(f"{weights}: sha256 does not match the preflight manifest")
report = json.loads((corpus / "validation-report.json").read_text())
for split, name in (("train", "train.bin"), ("validation", "validation.bin")):
    digest = sha256(corpus / name)
    if digest != report["splits"][split]["sha256"]:
        raise SystemExit(f"{corpus / name}: sha256 {digest} != validation report")
emit("inputs", base=str(base), model=manifest["model"], corpus=str(corpus), train_tokens=report["splits"]["train"]["tokens_including_eos"],
     validation_tokens=report["splits"]["validation"]["tokens_including_eos"], sha_verified=True)

# ------------------------------------------------------------------ the run
run_dir = OUTPUT / "run"
cmd = [
    sys.executable, str(script), "--tiny", "--model", str(base), "--stream", str(corpus / "train.bin"),
    "--validation", str(corpus / "validation.bin"), "--room-validation", str(corpus / "room-validation.bin"),
    "--output", str(run_dir), "--run-name", "t4-cpt-test", "--tokens", str(TOKENS), "--max-minutes", str(MAX_MINUTES),
    "--reload-check",
]
if EXTRA_ARGS:
    cmd += EXTRA_ARGS.split()
emit("run_start", command=cmd)
with (OUTPUT / "cpt.log").open("w") as log:
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                            env={**os.environ, "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"})
    for line in proc.stdout:
        log.write(line)
        if line.startswith("{"):
            print(line, end="", flush=True)
    returncode = proc.wait()
emit("run_done", returncode=returncode, minutes=round((time.time() - STARTED) / 60, 1))

# ------------------------------------------------------------------ checks
events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text().splitlines() if line.startswith("{")]
by_kind: dict[str, list[dict]] = {}
for event in events:
    by_kind.setdefault(event["event"], []).append(event)
problems: list[str] = []
if returncode != 0:
    problems.append(f"cpt_torch.py exited {returncode}")
train = by_kind.get("train", [])
if not train:
    problems.append("no train events")
if any(not math.isfinite(e["loss"]) for e in train):
    problems.append("non-finite train loss")
if by_kind.get("nonfinite"):
    problems.append(f"{len(by_kind['nonfinite'])} non-finite steps")
validations = by_kind.get("validation", [])
if len(validations) < 2:
    problems.append("fewer than two validation events")
for v in validations:
    for key in ("loss", "room_loss"):
        if key not in v or not math.isfinite(v[key]):
            problems.append(f"validation at {v.get('tokens')} tokens: {key} missing or non-finite")
checkpoints = sorted(p for p in run_dir.glob("tokens-*") if (p / "config.json").exists() and (p / "model.safetensors").exists())
if not checkpoints:
    problems.append("no HF checkpoint written")
reload = by_kind.get("reload_check", [])
if not reload or not reload[-1].get("ok"):
    problems.append("reload check missing or failed")

# Independent reload through the interface the room-eval kernel and hbox evaluator use.
independent = None
if checkpoints:
    from transformers import AutoTokenizer, FalconH1ForCausalLM

    sys.path.insert(0, str(script.parent))
    from cpt_torch import WindowStream

    device = "cuda" if torch.cuda.is_available() else "cpu"
    final = checkpoints[-1]
    model = FalconH1ForCausalLM.from_pretrained(final, dtype=torch.float32, local_files_only=True).to(device).eval()
    tokenizer = AutoTokenizer.from_pretrained(final, local_files_only=True)
    cfg = json.loads((run_dir / "config.json").read_text())
    rows = WindowStream(corpus / "validation.bin", cfg["seq"], 0).head(cfg["validation_windows"])
    total = 0.0
    with torch.no_grad():
        for begin in range(0, rows.shape[0], cfg["batch"]):
            batch = torch.from_numpy(rows[begin : begin + cfg["batch"]]).to(device)
            logits = model(input_ids=batch[:, :-1], use_cache=False).logits.float()
            loss = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.shape[-1]), batch[:, 1:].reshape(-1))
            total += loss.item() * batch.shape[0]
    independent = {"checkpoint": str(final), "loss_fp32": total / rows.shape[0], "tokenizer_vocab": len(tokenizer),
                   "config_dtype": json.loads((final / "config.json").read_text()).get("dtype"),
                   "safetensors_bytes": (final / "model.safetensors").stat().st_size}
    last_loss = validations[-1]["loss"] if validations else float("nan")
    independent["delta_vs_trained"] = independent["loss_fp32"] - last_loss
    if abs(independent["delta_vs_trained"]) > 0.05:
        problems.append(f"independent reload loss {independent['loss_fp32']:.4f} vs trained {last_loss:.4f}")
    del model
    emit("independent_reload", **independent)

speeds = [e["tokens_per_second"] for e in train[1:]] or [e["tokens_per_second"] for e in train]
summary = {
    "ok": not problems,
    "problems": problems,
    "returncode": returncode,
    "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
    "fast_path": (by_kind.get("hardware") or [{}])[0].get("fast_path"),
    "steps": train[-1]["step"] if train else 0,
    "tokens": train[-1]["tokens"] if train else 0,
    "completed": bool(by_kind.get("complete")) and (by_kind["complete"][-1].get("completed") is True),
    "budget_stop": bool(by_kind.get("budget_stop")),
    "train_loss_first": train[0]["loss"] if train else None,
    "train_loss_last": train[-1]["loss"] if train else None,
    "validation": [{k: v.get(k) for k in ("step", "tokens", "loss", "room_loss", "final")} for v in validations],
    "tokens_per_second_median": statistics.median(speeds) if speeds else None,
    "tokens_per_second_max": max(speeds) if speeds else None,
    "peak_memory_gb": max((e.get("peak_memory_gb") or 0) for e in train) if train else None,
    "checkpoints": [p.name for p in checkpoints],
    "reload_check": reload[-1] if reload else None,
    "independent_reload": independent,
    "minutes": round((time.time() - STARTED) / 60, 1),
    "versions": {"torch": torch.__version__, "transformers": installed("transformers")},
}
(OUTPUT / "summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
emit("summary", **{k: v for k, v in summary.items() if k not in ("validation", "reload_check", "independent_reload")})
for v in summary["validation"]:
    print(f"  validation at {v['tokens']:>9} tokens: library {v['loss']:.4f}  room {v['room_loss']:.4f}", flush=True)
print("T4_CPT_TEST_OK" if not problems else "T4_CPT_TEST_FAILED: " + "; ".join(problems), flush=True)
if problems:
    raise SystemExit(1)
