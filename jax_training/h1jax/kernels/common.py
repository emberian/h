"""Shared pieces of the Kaggle TPU kernels.

The run-spec settings tables and their parsing, the JSON event line with its watchdog heartbeat, the
process watchdog, and the input helpers that `cpt.py` and `gate.py` both carried as copies. This module
imports nothing from jax at import time (jax is imported inside `hbm_stats`) so `kaggle/spec_kernel.py`
can load it by file path with a plain python3 and validate a spec without a JAX environment.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------------- settings
#
# Each table maps a spec key to (kind, default). The default is the env-style string the old kernel
# carried in its `os.environ.get("HGHOST_..._KEY", default)` call; None means the kernel computes it
# (`output` from `run_name`, `resume_globs` from `output`, `require_tpu` from `local`, the env fallbacks
# for the rehearsal keys). The kind says how a string is parsed, exactly as the env kernels parsed it,
# and how an already-typed JSON value is coerced.

CPT_SETTINGS: dict[str, tuple[str, str | None]] = {
    "run_name": ("str", "trunk-wsd-lr1e-4-seed0"),
    "output": ("str", None),  # /kaggle/working/<run_name>
    "ssd": ("str", "v1"),  # h1jax SSD implementation (H1JAX_SSD, read by h1jax.model at import)
    "remat_policy": ("str", ""),  # H1JAX_REMAT_POLICY, likewise
    "per_chip": ("int", "64"),
    "seq": ("int", "512"),
    "remat": ("flag", "1"),
    "total_tokens": ("int", "1497620848"),
    "lr": ("float", "1e-4"),
    "warmup_tokens": ("int", "10000000"),
    "min_lr_ratio": ("float", "0.1"),
    "weight_decay": ("float", "0.1"),
    "max_grad_norm": ("float", "1.0"),
    "save_tokens": ("ints", "10000000,30000000,100000000,200000000,374405212,748810424,1123215636"),
    "eval_every_tokens": ("int", "25000000"),
    "eval_sequences": ("int", "512"),
    "fixed_eval_sequences": ("int", "32"),
    "log_steps": ("int", "10"),
    "max_minutes": ("float", "400"),
    "watchdog_minutes": ("float", "30"),
    "budget_margin_minutes": ("float", "6"),
    "seed": ("int", "0"),
    "schedule": ("str", "wsd"),  # cosine | wsd
    "decay_tokens": ("int", "0"),  # wsd: decay over the last N tokens
    "branch_from": ("str", ""),  # trunk checkpoint dir (or trainer_state.json glob) to branch from
    "resume_globs": ("strs", None),  # /kaggle/input/**/trainer_state.json,<output>/**/trainer_state.json
    "mir_weight": ("float", "0"),  # 0 = plain NTP
    "mir_max_ratio": ("float", "0.5"),
    "mir_mask_id": ("int", "0"),  # <|pad|>, never in the corpus
    "simreg_weight": ("float", "0"),  # 0 = off
    "extra_validation": ("str", ""),  # second validation stream inside the corpus dataset
    "simreg_temperature": ("float", "0.1"),
    "role_weights": ("floats", ""),  # per-class loss weights; empty = plain next-token loss
    "weights_file": ("str", "train-weights.bin"),
    "extra_weights_file": ("str", "room-validation-weights.bin"),
    "param_sharding": ("str", "replicated"),  # replicated | fsdp
    "rollout_steps": ("int", "64"),  # 0 disables in-run rollouts
    "rollout_length": ("int", "96"),
    "rollout_temperature": ("float", "0.8"),
    # Rehearsal and environment keys (the old HGHOST_LOCAL / HGHOST_BASE_DIR / HGHOST_CORPUS_DIR /
    # HGHOST_REQUIRE_TPU / HGHOST_LAYER_SCAN variables, which remain honoured as fallbacks).
    "local": ("flag", None),
    "base_dir": ("str", None),
    "corpus_dir": ("str", None),
    "require_tpu": ("flag", None),  # default "0" when local else "1"
    "layer_scan": ("flag", None),  # default "1"
}

GATE_SETTINGS: dict[str, tuple[str, str | None]] = {
    "output": ("str", "/kaggle/working/h1jax-profile-gate-15b-deep"),
    "shapes": ("str", "4x512r,8x512r"),  # <per_chip>x<seq_len>[r], comma separated
    "warmup": ("int", "3"),
    "steps": ("int", "20"),
    "sync_steps": ("int", "5"),
    "profile_steps": ("int", "3"),
    "bench_iters": ("int", "10"),
    "sanity_steps": ("int", "30"),
    "watchdog_minutes": ("float", "20"),
    "max_minutes": ("float", "45"),  # hard limit enforced by the watchdog
    "sanity_lr": ("float", "3e-5"),
    "eval_sequences": ("int", "32"),
    "peak_flops_per_chip": ("float", "197e12"),
    "hbm_bytes_per_chip": ("float", str(16 * 1024**3)),
    "param_sharding": ("str", "fsdp"),  # replicated | fsdp
    "hbox_base_loss": ("float", None),  # hbox Transformers loss on the fixed 32-sequence slice, if one exists
    "hbox_base_accuracy": ("float", None),
    "local": ("flag", None),
    "base_dir": ("str", None),
    "corpus_dir": ("str", None),
    "require_tpu": ("flag", None),
    "layer_scan": ("flag", None),
}

SETTINGS = {"cpt": CPT_SETTINGS, "gate": GATE_SETTINGS}


def coerce(kind: str, value: Any) -> Any:
    """Parse an env-style string exactly as the env kernels did, or coerce an already-typed value."""
    if kind == "int":
        return int(value)
    if kind == "float":
        return float(value)
    if kind == "str":
        return str(value)
    if kind == "flag":
        return value if isinstance(value, bool) else str(value) == "1"
    if kind == "ints":
        if isinstance(value, str):
            return [int(v) for v in value.split(",") if v]
        return [int(v) for v in value]
    if kind == "floats":
        if isinstance(value, str):
            return [float(x) for x in value.split(",") if x.strip()]
        return [float(v) for v in value]
    if kind == "strs":
        if isinstance(value, str):
            return value.split(",")
        return [str(v) for v in value]
    raise ValueError(f"unknown setting kind {kind!r}")


def resolve(spec: Mapping[str, Any], kind: str) -> dict[str, Any]:
    """Every setting of a `kind` kernel from `spec`, defaults applied; unknown keys are an error."""
    table = SETTINGS[kind]
    unknown = sorted(key for key in spec if key not in table and key != "kind")
    if unknown:
        raise ValueError(f"unknown {kind} spec keys {unknown}; known keys: {sorted(table)}")
    if spec.get("kind", kind) != kind:
        raise ValueError(f"spec kind {spec.get('kind')!r} is not {kind!r}")
    settings: dict[str, Any] = {}
    for key, (value_kind, default) in table.items():
        if key in spec and spec[key] is not None:
            settings[key] = coerce(value_kind, spec[key])
        elif default is None:
            settings[key] = None
        else:
            settings[key] = coerce(value_kind, default)
    return settings


def env_flag(settings: Mapping[str, Any], key: str, variable: str, default: str) -> bool:
    """A flag setting, falling back to its old HGHOST_* environment variable, then to `default`."""
    if settings[key] is not None:
        return bool(settings[key])
    return os.environ.get(variable, default) == "1"


# ----------------------------------------------------------------------------- events and watchdog

_HEARTBEAT: Path | None = None


def emit(event: str, **values: Any) -> None:
    """One JSON event line on stdout; touches the watchdog heartbeat once the watchdog is running."""
    if _HEARTBEAT is not None:
        try:
            _HEARTBEAT.write_text(str(time.time()))
        except OSError:
            pass
    print(json.dumps({"event": event, **values}, default=str), flush=True)


# A job that stalls (hung collective, post-OOM limbo) must kill itself, never wait to be cancelled. A
# separate PROCESS (immune to the GIL and to a main thread stuck in native code) watches a heartbeat file
# that every emitted event touches; a stale heartbeat or the hard time limit -> SIGKILL to this process.
_WATCHDOG_CODE = r"""
import os, sys, time, signal
pid, path, stall, hard = int(sys.argv[1]), sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
started = time.time()
while True:
    time.sleep(15)
    try:
        os.kill(pid, 0)
    except OSError:
        sys.exit(0)  # parent gone
    try:
        last = float(open(path).read())
    except Exception:
        last = started
    now = time.time()
    reason = None
    if now - last > stall * 60:
        reason = f"no progress event for {(now - last) / 60:.1f} min"
    elif now - started > hard * 60:
        reason = f"hard time limit {hard:.0f} min"
    if reason:
        print('{"event": "watchdog", "reason": "%s"}' % reason, flush=True)
        os.kill(pid, signal.SIGKILL)
        sys.exit(0)
"""


def start_watchdog(stall_minutes: float, hard_minutes: float) -> subprocess.Popen:
    global _HEARTBEAT
    _HEARTBEAT = Path(tempfile.gettempdir()) / f"hghost-heartbeat-{os.getpid()}"
    _HEARTBEAT.write_text(str(time.time()))
    return subprocess.Popen(
        [sys.executable, "-c", _WATCHDOG_CODE, str(os.getpid()), str(_HEARTBEAT), str(stall_minutes), str(hard_minutes)]
    )


# ----------------------------------------------------------------------------- probes and inputs


def hbm_stats() -> dict:
    """Per-device HBM bytes in use / limit / peak from the runtime (empty on backends without stats)."""
    import jax

    out = {}
    try:
        for d in jax.devices():
            st = d.memory_stats() or {}
            out[str(d.id)] = {
                "in_use": st.get("bytes_in_use"),
                "limit": st.get("bytes_limit"),
                "peak": st.get("peak_bytes_in_use"),
            }
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)[:200]
    return out


def memory_probe(tag: str) -> None:
    info: dict[str, Any] = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith(("MemTotal", "MemAvailable")):
                key, value = line.split(":")
                info[key] = int(value.split()[0]) * 1024
    except OSError:
        pass
    for path in (
        "/sys/fs/cgroup/memory.max",
        "/sys/fs/cgroup/memory/memory.limit_in_bytes",
    ):
        try:
            info["cgroup_limit"] = Path(path).read_text().strip()
            break
        except OSError:
            pass
    for path in (
        "/sys/fs/cgroup/memory.current",
        "/sys/fs/cgroup/memory/memory.usage_in_bytes",
    ):
        try:
            info["cgroup_current"] = Path(path).read_text().strip()
            break
        except OSError:
            pass
    try:
        info["rss_bytes"] = int(
            Path("/proc/self/statm").read_text().split()[1]
        ) * os.sysconf("SC_PAGE_SIZE")
    except (OSError, ValueError):
        pass
    emit("memory", tag=tag, hbm=hbm_stats(), **info)


def exactly_one(pattern: str) -> Path:
    matches = [Path(p) for p in glob.glob(pattern, recursive=True) if Path(p).is_file()]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {pattern!r}, found: {matches}")
    return matches[0]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def input_roots(local: bool, settings: Mapping[str, Any]) -> tuple[Path, Path]:
    """The base-model and corpus directories: from the spec / HGHOST_*_DIR when local, else found under
    /kaggle/input by their manifest files."""
    if local:
        base_root = Path(settings["base_dir"] or os.environ["HGHOST_BASE_DIR"]).resolve()
        corpus_root = Path(settings["corpus_dir"] or os.environ["HGHOST_CORPUS_DIR"]).resolve()
    else:
        base_root = exactly_one("/kaggle/input/**/preflight-manifest.json").parent
        corpus_root = exactly_one("/kaggle/input/**/validation-report.json").parent
    return base_root, corpus_root
