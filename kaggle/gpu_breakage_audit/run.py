"""Kaggle GPU kernel: breakage audit of the Falcon-H1 checkpoints (did continued pretraining on the
library damage general competence?).

Runs lm-evaluation-harness (lambada_openai, hellaswag, arc_easy, arc_challenge, piqa, winogrande) over
the two pinned bases (0.5B, 90M) and the FINAL checkpoint of each attached TPU run (the largest
`tokens-*/` per run dir; pre-cooldown checkpoints are skipped). Writes, under
<output>/ (default /kaggle/working/breakage-audit):
  results/<name>.json      the harness results for one checkpoint (+ our provenance fields)
  lm-eval/<name>/          the harness output tree as written
  logs/<name>.log          stdout/stderr of the harness run
  table.md / table.json    rows = checkpoints, columns = tasks (acc_norm where the task reports it,
                           else acc, with stderr), plus deltas against the same-family base
  plan.json                the throughput probe and the limit decision

Budget: the harness limit starts at LIMIT (1000 docs/task); each family's base is loaded once to probe
throughput, and if the projected total exceeds BUDGET_S the limit drops to FALLBACK_LIMIT (500) for
every checkpoint (one limit for all rows, so they stay comparable). A soft deadline stops launching new
checkpoints so the table is written before Kaggle's hard limit.

Attach: the two base datasets (preflight-manifest.json is verified) and, as kernel sources, the TPU runs.
"""

from __future__ import annotations

import glob
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

STARTED = time.time()
LOCAL = os.environ.get("HGHOST_LOCAL") == "1"
OUTPUT = Path(os.environ.get("HGHOST_AUDIT_OUTPUT", "/kaggle/working/breakage-audit"))
TRANSFORMERS = os.environ.get("HGHOST_AUDIT_TRANSFORMERS", "transformers==4.57.6")
LM_EVAL = os.environ.get("HGHOST_AUDIT_LM_EVAL", "lm-eval==0.4.13")
TASKS = os.environ.get("HGHOST_AUDIT_TASKS", "lambada_openai,hellaswag,arc_easy,arc_challenge,piqa,winogrande")
LIMIT = int(os.environ.get("HGHOST_AUDIT_LIMIT", "1000"))
FALLBACK_LIMIT = int(os.environ.get("HGHOST_AUDIT_FALLBACK_LIMIT", "500"))
BUDGET_S = float(os.environ.get("HGHOST_AUDIT_BUDGET_S", str(2.5 * 3600)))
DEADLINE_S = float(os.environ.get("HGHOST_AUDIT_DEADLINE_S", str(4 * 3600)))
DTYPE = os.environ.get("HGHOST_AUDIT_DTYPE", "float16")
BATCH = os.environ.get("HGHOST_AUDIT_BATCH", "8")
MAX_BATCH = int(os.environ.get("HGHOST_AUDIT_MAX_BATCH", "8"))
MAX_LENGTH = int(os.environ.get("HGHOST_AUDIT_MAX_LENGTH", "2048"))
# Padded harness tokens per doc index summed over the six tasks (lambada 1 request, hellaswag/arc 4,
# piqa/winogrande 2), a rough figure used only to size the limit; the probe measures the model.
TOKENS_PER_DOC = float(os.environ.get("HGHOST_AUDIT_TOKENS_PER_DOC", "1400"))
SAFETY = float(os.environ.get("HGHOST_AUDIT_SAFETY", "2.0"))
LOAD_OVERHEAD_S = 120.0
SKIP_SHA = os.environ.get("HGHOST_AUDIT_SKIP_SHA") == "1"
CHECKPOINT_GLOB = os.environ.get("HGHOST_AUDIT_CHECKPOINT_GLOB", "/kaggle/input/**/no-such-run/tokens-*/config.json")
MANIFEST_GLOB = os.environ.get("HGHOST_AUDIT_MANIFEST_GLOB", "/kaggle/input/**/hghost-falcon-h1-0-5b-base-public/preflight-manifest.json")
# Run dir -> the final checkpoint we expect there (the ledger's cooled checkpoints). Anything else
# attached is a mistake we would rather learn about before spending GPU hours.
EXPECTED_FINALS = {
    "room05b-e1-decay10": "tokens-000417533162",
    "room05b-e2-v3-decay10": "tokens-000793917970",
    "room05b-e2-v4-decay10": "tokens-000794693880",
    "leaf-s1-e4-decay10": "tokens-001535061369",
}
TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json")
PROBE_TEXT = (
    "The library was quiet at that hour. Rain moved across the high windows, and the reading lamps "
    "threw small circles onto the long oak tables. She turned the page carefully, because the paper "
    "was old and the binding had begun to give, and read the sentence again: the river, it said, "
    "does not remember the bridge. Outside, a bus hissed to a stop and pulled away. Nobody looked up."
)

OUTPUT.mkdir(parents=True, exist_ok=True)
for sub in ("checkpoints", "results", "lm-eval", "logs"):
    (OUTPUT / sub).mkdir(exist_ok=True)


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


# ------------------------------------------------------------------ environment
if not LOCAL:
    # Pin torch to the image's build: the image torch is what supports the T4 (sm_75); letting pip
    # replace it with a PyPI wheel is how a kernel ends up with a CUDA build the card cannot run.
    torch_pin = f"torch=={installed('torch')}"
    cmd = [sys.executable, "-m", "pip", "install", "--quiet", LM_EVAL, TRANSFORMERS, "accelerate", torch_pin]
    emit("pip_install", command=cmd)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    (OUTPUT / "logs" / "pip.log").write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
    if proc.returncode != 0:
        print(proc.stderr[-4000:], flush=True)
        raise SystemExit("pip install failed")
    emit("pip_done", torch=installed("torch"), transformers=installed("transformers"), lm_eval=installed("lm_eval"))

import torch

if torch.cuda.is_available():
    DEVICE = "cuda"
elif getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"
emit(
    "hardware",
    device=DEVICE,
    name=torch.cuda.get_device_name(0) if DEVICE == "cuda" else DEVICE,
    torch=torch.__version__,
    transformers=installed("transformers"),
    lm_eval=installed("lm_eval"),
)


# ------------------------------------------------------------------ bases: verified against their manifests
def family_key(config_path: Path) -> str:
    cfg = json.loads(config_path.read_text())
    return f"h{cfg['hidden_size']}-l{cfg['num_hidden_layers']}"


bases: dict[str, dict] = {}  # family -> {"name", "path", "model"}
if LOCAL:
    manifests = [Path(p).resolve() / "preflight-manifest.json" for p in os.environ["HGHOST_AUDIT_BASES"].split(",")]
else:
    manifests = sorted(Path(p) for p in glob.glob(MANIFEST_GLOB, recursive=True))
if not manifests:
    raise SystemExit(f"no base manifests matched {MANIFEST_GLOB}")
for manifest_path in manifests:
    root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text())
    expected = manifest["files"]["model.safetensors"]["sha256"]
    weights = root / "model.safetensors"
    if not SKIP_SHA:
        digest = sha256(weights)
        if digest != expected:
            raise SystemExit(f"{weights}: sha256 {digest} != manifest {expected}")
    model_id = manifest["model"]
    name = "base-" + model_id.split("/")[-1].lower().replace("falcon-h1-", "").replace("-base", "")
    family = family_key(root / "config.json")
    if family in bases:
        raise SystemExit(f"two bases share family {family}: {bases[family]['path']} and {root}")
    bases[family] = {"name": name, "path": root, "model": model_id, "revision": manifest.get("revision")}
    emit("base", name=name, family=family, path=str(root), model=model_id, sha256_verified=not SKIP_SHA)


# ------------------------------------------------------------------ checkpoints: the final tokens-* of each run
def tokens_of(path: Path) -> int:
    return int(path.name.replace("tokens-", ""))


if LOCAL and os.environ.get("HGHOST_AUDIT_CHECKPOINTS"):
    found = [Path(p).resolve() for p in os.environ["HGHOST_AUDIT_CHECKPOINTS"].split(",")]
else:
    found = [Path(p).resolve().parent for p in glob.glob(CHECKPOINT_GLOB, recursive=True)]
runs: dict[Path, list[Path]] = {}
for ckpt in found:
    runs.setdefault(ckpt.parent, []).append(ckpt)
finals: list[Path] = []
for run_dir, ckpts in sorted(runs.items()):
    ckpts = sorted(ckpts, key=tokens_of)
    final = ckpts[-1]
    expected_final = EXPECTED_FINALS.get(run_dir.name)
    if not LOCAL and expected_final is not None and final.name != expected_final:
        raise SystemExit(f"{run_dir}: final checkpoint {final.name} != expected {expected_final}")
    finals.append(final)
    emit("run", run=run_dir.name, final=final.name, skipped=[c.name for c in ckpts[:-1]])
if not LOCAL:
    missing = sorted(set(EXPECTED_FINALS) - {p.parent.name for p in finals})
    if missing:
        print(f"warning: expected runs not attached (bases only): {missing}", file=sys.stderr)


def repaired_config(source: Path) -> dict:
    """The repairs kaggle/harvest_kernel.py applies to configs from older h1jax wheels."""
    cfg = json.loads(source.read_text())
    if isinstance(cfg.get("mamba_expand"), float):
        cfg["mamba_expand"] = max(1, -(-int(cfg["mamba_d_ssm"]) // int(cfg["hidden_size"])))
    limit = cfg.get("time_step_limit")
    if isinstance(limit, list) and any(isinstance(x, float) and math.isinf(x) for x in limit):
        cfg.pop("time_step_limit")
    return cfg


targets: list[dict] = []  # {"name", "path", "family", "base": bool, "tokens", "source"}
for family, base in bases.items():
    targets.append({"name": base["name"], "path": base["path"], "family": family, "base": True, "tokens": None,
                    "source": str(base["path"])})
staged_root = OUTPUT / "checkpoints"
for ckpt in finals:
    name = ckpt.parent.name
    dest = staged_root / name
    dest.mkdir(exist_ok=True)
    for item in ckpt.iterdir():
        if item.name in ("optimizer.msgpack", "config.json"):
            continue
        target = dest / item.name
        if not target.exists():
            try:
                os.symlink(item.resolve(), target)
            except OSError:
                shutil.copy2(item, target)
    (dest / "config.json").write_text(json.dumps(repaired_config(ckpt / "config.json"), indent=2) + "\n")
    family = family_key(dest / "config.json")
    if family not in bases:
        raise SystemExit(f"{ckpt}: family {family} has no attached base (have {sorted(bases)})")
    for fname in TOKENIZER_FILES:
        if not (dest / fname).exists():
            shutil.copy2(bases[family]["path"] / fname, dest / fname)
    targets.append({"name": name, "path": dest, "family": family, "base": False, "tokens": tokens_of(ckpt),
                    "source": str(ckpt)})
# Largest family first, base before its checkpoints, so the expensive rows land earliest.
targets.sort(key=lambda t: (-int(t["family"].split("-")[0][1:]), not t["base"], t["name"]))
emit("targets", names=[t["name"] for t in targets], sources=[t["source"] for t in targets])


# ------------------------------------------------------------------ probe each family: dtype sanity + throughput
def probe(path: Path, dtype_name: str) -> dict:
    from transformers import AutoTokenizer, FalconH1ForCausalLM

    dtype = getattr(torch, dtype_name)
    model = FalconH1ForCausalLM.from_pretrained(path, dtype=dtype, local_files_only=True).to(DEVICE).eval()
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
    ids = torch.tensor([tokenizer.encode(PROBE_TEXT, add_special_tokens=False)], device=DEVICE)
    with torch.no_grad():
        logits = model(ids).logits.float()
        loss = torch.nn.functional.cross_entropy(logits[0, :-1], ids[0, 1:]).item()
        finite = bool(torch.isfinite(logits).all())
        bench = torch.randint(0, int(model.config.vocab_size), (16, 256), device=DEVICE)
        model(bench)
        if DEVICE == "cuda":
            torch.cuda.synchronize()
        started = time.time()
        rounds = 3
        for _ in range(rounds):
            model(bench)
        if DEVICE == "cuda":
            torch.cuda.synchronize()
        seconds = time.time() - started
    tokens_per_second = rounds * bench.numel() / seconds
    del model
    if DEVICE == "cuda":
        torch.cuda.empty_cache()
    return {"dtype": dtype_name, "loss": round(loss, 4), "finite": finite, "tokens_per_second": round(tokens_per_second, 1),
            "probe_tokens": int(ids.shape[1])}


family_dtype: dict[str, str] = {}
family_speed: dict[str, float] = {}
for family, base in bases.items():
    result = probe(base["path"], DTYPE)
    if not result["finite"] or result["loss"] > 12:
        emit("probe_fallback", family=family, **result)
        result = probe(base["path"], "float32")
    family_dtype[family] = result["dtype"]
    family_speed[family] = result["tokens_per_second"]
    emit("probe", family=family, name=base["name"], **result)


def projected_seconds(limit: int) -> float:
    return sum(LOAD_OVERHEAD_S + SAFETY * limit * TOKENS_PER_DOC / family_speed[t["family"]] for t in targets)


limit = LIMIT
remaining = BUDGET_S - (time.time() - STARTED)
estimate = projected_seconds(limit)
if estimate > remaining and FALLBACK_LIMIT < LIMIT:
    limit = FALLBACK_LIMIT
    estimate = projected_seconds(limit)
plan = {
    "limit": limit, "requested_limit": LIMIT, "fallback_limit": FALLBACK_LIMIT, "budget_seconds": BUDGET_S,
    "projected_seconds": round(estimate), "projected_seconds_at_requested": round(projected_seconds(LIMIT)),
    "over_budget": estimate > remaining, "tokens_per_doc": TOKENS_PER_DOC, "safety": SAFETY,
    "family_tokens_per_second": family_speed, "family_dtype": family_dtype, "device": DEVICE, "tasks": TASKS.split(","),
}
(OUTPUT / "plan.json").write_text(json.dumps(plan, indent=1) + "\n")
emit("plan", **plan)


# ------------------------------------------------------------------ evaluate
def newest_results(directory: Path) -> Path | None:
    files = sorted(Path(p) for p in glob.glob(f"{directory}/**/results_*.json", recursive=True))
    return files[-1] if files else None


def evaluate(target: dict) -> dict:
    name, path = target["name"], target["path"]
    out_dir = OUTPUT / "lm-eval" / name
    dtype = family_dtype[target["family"]]
    cmd = [
        sys.executable, "-m", "lm_eval", "--model", "hf",
        "--model_args", f"pretrained={path},dtype={dtype},max_length={MAX_LENGTH}",
        "--tasks", TASKS, "--limit", str(limit), "--batch_size", BATCH, "--max_batch_size", str(MAX_BATCH),
        "--device", DEVICE, "--output_path", str(out_dir),
    ]
    if os.environ.get("HGHOST_AUDIT_EXTRA_ARGS"):
        cmd += os.environ["HGHOST_AUDIT_EXTRA_ARGS"].split()
    emit("evaluate_start", name=name, path=str(path), dtype=dtype, limit=limit)
    started = time.time()
    env = {**os.environ, "TOKENIZERS_PARALLELISM": "false", "HF_HUB_DISABLE_TELEMETRY": "1"}
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    seconds = round(time.time() - started, 1)
    (OUTPUT / "logs" / f"{name}.log").write_text(" ".join(cmd) + "\n\n" + proc.stdout + "\n--- stderr ---\n" + proc.stderr)
    results_file = newest_results(out_dir)
    record = {"name": name, "source": target["source"], "family": target["family"], "base": target["base"],
              "tokens": target["tokens"], "dtype": dtype, "limit": limit, "seconds": seconds,
              "returncode": proc.returncode, "results": None}
    if results_file is not None:
        harness = json.loads(results_file.read_text())
        record["results"] = harness.get("results")
        record["harness_file"] = str(results_file)
        harness["hghost"] = {k: v for k, v in record.items() if k != "results"}
        (OUTPUT / "results" / f"{name}.json").write_text(json.dumps(harness, indent=1, default=str) + "\n")
    emit("evaluate_done", name=name, returncode=proc.returncode, seconds=seconds,
         summary={task: round(v.get("acc_norm,none", v.get("acc,none", float("nan"))), 4)
                  for task, v in (record["results"] or {}).items()})
    if proc.returncode != 0 or record["results"] is None:
        print(proc.stderr[-3000:], flush=True)
    return record


# ------------------------------------------------------------------ table
def metric(results: dict | None, task: str) -> tuple[str, float, float] | None:
    if not results or task not in results:
        return None
    row = results[task]
    for key in ("acc_norm", "acc"):
        if f"{key},none" in row:
            return key, float(row[f"{key},none"]), float(row.get(f"{key}_stderr,none", float("nan")))
    return None


def fmt(value: float, err: float) -> str:
    return f"{value:.3f} ± {err:.3f}" if math.isfinite(err) else f"{value:.3f}"


def write_table(records: list[dict]) -> str:
    tasks = TASKS.split(",")
    metric_names = {}
    for task in tasks:
        for r in records:
            m = metric(r["results"], task)
            if m:
                metric_names[task] = m[0]
                break
    head = ["checkpoint", "tokens", "dtype"] + [f"{t} ({metric_names.get(t, '?')})" for t in tasks] + ["mean", "lambada ppl", "minutes"]
    lines = ["| " + " | ".join(head) + " |", "|---|---:|---|" + "---:|" * (len(tasks) + 3)]
    means: dict[str, float] = {}
    for r in records:
        cells = []
        values = []
        for task in tasks:
            m = metric(r["results"], task)
            if m:
                cells.append(fmt(m[1], m[2]))
                values.append(m[1])
            else:
                cells.append("-" if r["returncode"] == 0 else "ERR")
        mean = sum(values) / len(values) if len(values) == len(tasks) else float("nan")
        means[r["name"]] = mean
        ppl = (r["results"] or {}).get("lambada_openai", {}).get("perplexity,none")
        tokens = f"{r['tokens'] / 1e6:.1f}M" if r["tokens"] else "-"
        tail = [f"{mean:.3f}" if math.isfinite(mean) else "-", f"{ppl:.2f}" if ppl is not None else "-", f"{r['seconds'] / 60:.0f}"]
        lines.append("| " + " | ".join([r["name"], tokens, r["dtype"]] + cells + tail) + " |")
    # Deltas against the same-family base, with z = delta / sqrt(se_a^2 + se_b^2).
    base_by_family = {r["family"]: r for r in records if r["base"]}
    delta_lines = ["", f"Deltas against the same-family base (z = Δ / √(se²+se²); limit {limit} docs/task):", "",
                   "| checkpoint | vs | " + " | ".join(tasks) + " | mean Δ |", "|---|---|" + "---:|" * (len(tasks) + 1)]
    for r in records:
        if r["base"] or r["family"] not in base_by_family:
            continue
        base = base_by_family[r["family"]]
        cells = []
        for task in tasks:
            a, b = metric(r["results"], task), metric(base["results"], task)
            if a and b:
                delta = a[1] - b[1]
                se = math.sqrt(a[2] ** 2 + b[2] ** 2) if math.isfinite(a[2]) and math.isfinite(b[2]) else float("nan")
                z = delta / se if se and math.isfinite(se) else float("nan")
                cells.append(f"{delta:+.3f} (z {z:+.1f})" if math.isfinite(z) else f"{delta:+.3f}")
            else:
                cells.append("-")
        mean_delta = means[r["name"]] - means[base["name"]]
        delta_lines.append(f"| {r['name']} | {base['name']} | " + " | ".join(cells)
                           + (f" | {mean_delta:+.3f} |" if math.isfinite(mean_delta) else " | - |"))
    text = "\n".join(lines + delta_lines) + "\n"
    (OUTPUT / "table.md").write_text(text)
    (OUTPUT / "table.json").write_text(json.dumps({"plan": plan, "records": records}, indent=1, default=str) + "\n")
    return text


records: list[dict] = []
skipped: list[str] = []
for target in targets:
    if time.time() - STARTED > DEADLINE_S:
        skipped.append(target["name"])
        emit("skipped_deadline", name=target["name"])
        continue
    records.append(evaluate(target))
    print(write_table(records), flush=True)

failed = [r["name"] for r in records if r["returncode"] != 0 or r["results"] is None]
emit("complete", checkpoints=len(records), failed=failed, skipped=skipped, limit=limit,
     minutes=round((time.time() - STARTED) / 60, 1))
print("BREAKAGE_AUDIT_OK" if not failed and not skipped else "BREAKAGE_AUDIT_PARTIAL", flush=True)
