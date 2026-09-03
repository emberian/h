#!/usr/bin/env python3
"""h explorer: a local causal workbench for the small models in the library.

    python3 explorer/serve.py --port 8130      # then open http://127.0.0.1:8130

Stdlib only. Serves one static page and a handful of JSON endpoints:

    GET  /api/servers                 model servers (probed live), serving links, checkpoint dirs
    POST /api/generate                {server, model, prompt, n, temperature, top_p, max_tokens, stop}
                                      -> NDJSON stream, one {"type":"sample"} line per completion
    POST /api/haunt                   {items:[{id,text}], ...} -> exact-match provenance per item (cached by text)
    GET  /api/observatory[?date=...]  room-proxy observatory records for a day, with derived summary
    GET  /api/weaves[?name=...]       list saved weaves / load one
    POST /api/weaves                  {name, weave} -> validate and save explorer/weaves/<name>.json

Token ids in completions are decoded here with a pure-Python byte-level BPE decoder read from tokenizer.json,
so every sampled node carries exact token/logprob alignment. Re-tokenising text (only needed to shade
observatory candidates, which store logprobs without token ids) uses the `tokenizers` package from the
project venv through a tiny worker process; without it those candidates fall back to a bar strip.
"""
from __future__ import annotations

import argparse
import codecs
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STATIC = HERE / "static"
WEAVES = HERE / "weaves"
HAUNT_CACHE = HERE / "cache" / "haunt"

CFG = {
    "tokenizer": ROOT / "kaggle/base_model_dataset_public/tokenizer.json",
    "haunt_bin": ROOT / ".venv/bin/hghost-haunt",
    "haunt_index": ROOT / "artifacts/haunting-index",
    "observatory": ROOT / "research/results/room-observatory",
    "serving": ROOT / "artifacts/serving",
    "checkpoints": ROOT / "artifacts/checkpoints/tpu",
    "venv_python": ROOT / ".venv/bin/python",
    "jax_python": ROOT / ".venv-jax/bin/python",
    "labels": ROOT / "research/results/room-labels",
    "roombank_results": ROOT / "research/results/roombank",
    "roombank_bank": ROOT / "research/eval/roombank/bank.jsonl",
    "roomstate": "http://127.0.0.1:8140",
    "scorers": [ROOT / "kaggle/base_model_dataset_public", ROOT / "artifacts/kaggle/base_model_05b"],
    "judge_leaf": ROOT / "artifacts/checkpoints/tpu/h-ghost-h1jax-leaf-s1-e4/leaf-s1-e4-decay10/tokens-001535061369",
    "judge_base": ROOT / "kaggle/base_model_dataset_public",
    "serve_port": 8125,
    "serve_session": "hghost-serve05b",
    "mlx_python": Path.home() / ".cache/h1-distributed/venv/bin/python",
}
SERVER_URLS: list[str] = ["http://127.0.0.1:8124", "http://127.0.0.1:8125", "http://127.0.0.1:8127", "http://127.0.0.1:8128"]
SERVER_NAMES: dict[str, str] = {}  # url -> model name override (--server name@url)

WEAVE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ----------------------------------------------------------------------------------------------- tokens

def bytes_to_unicode() -> dict[int, str]:
    """GPT-2's reversible byte -> printable-unicode map used by ByteLevel BPE vocabularies."""
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))


class Decoder:
    """Token ids -> per-token text, from a HF tokenizer.json with a ByteLevel decoder. Multi-byte characters
    that straddle tokens are attributed to the token that completes them."""

    def __init__(self, path: Path):
        spec = json.loads(path.read_text(encoding="utf-8"))
        u2b = {v: k for k, v in bytes_to_unicode().items()}
        self.pieces = {i: bytes(u2b[c] for c in tok) for tok, i in spec["model"]["vocab"].items()}
        self.added = {a["id"]: a["content"] for a in spec.get("added_tokens", [])}

    def decode(self, ids: list[int]) -> list[str]:
        dec = codecs.getincrementaldecoder("utf-8")(errors="replace")
        out: list[str] = []
        for i in ids:
            if i in self.added:
                out.append(dec.decode(b"", final=True) + self.added[i])
                dec.reset()
            else:
                out.append(dec.decode(self.pieces.get(i, b""), final=False))
        tail = dec.decode(b"", final=True)
        if tail and out:
            out[-1] += tail
        return out


class Encoder:
    """Text -> token ids through a worker running the project venv's `tokenizers` (lazy, optional)."""

    def __init__(self, python: Path, tokenizer: Path):
        self.python, self.tokenizer = python, tokenizer
        self.proc: subprocess.Popen | None = None
        self.lock = threading.Lock()
        self.failed = False
        self.cache: dict[str, list[int]] = {}

    def _start(self) -> bool:
        if self.proc and self.proc.poll() is None:
            return True
        if self.failed or not self.python.exists():
            self.failed = True
            return False
        try:
            self.proc = subprocess.Popen(
                [str(self.python), str(HERE / "tokenize_worker.py"), str(self.tokenizer)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            )
            self.proc.stdin.write("[]\n")
            self.proc.stdin.flush()
            ready = self.proc.stdout.readline()
            if ready.strip() != "[]":
                raise RuntimeError("worker did not answer")
            return True
        except Exception as e:  # noqa: BLE001
            print(f"tokenize worker unavailable ({e}); observatory candidates will use logprob strips", flush=True)
            self.failed = True
            return False

    def encode(self, texts: list[str]) -> list[list[int]] | None:
        with self.lock:
            if not self._start():
                return None
            missing = [t for t in dict.fromkeys(texts) if t not in self.cache]
            if missing:
                try:
                    self.proc.stdin.write(json.dumps(missing) + "\n")
                    self.proc.stdin.flush()
                    ids = json.loads(self.proc.stdout.readline())
                except Exception as e:  # noqa: BLE001
                    print(f"tokenize worker died ({e})", flush=True)
                    self.proc = None
                    return None
                self.cache.update(zip(missing, ids))
            return [self.cache[t] for t in texts]


DEC: Decoder | None = None
ENC: Encoder | None = None


def git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(ROOT), capture_output=True, text=True,
                              timeout=5, check=False).stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


def file_sha(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    except Exception:  # noqa: BLE001
        return None


VERSION: dict = {}


def version_info() -> dict:
    if not VERSION:
        VERSION.update({"explorer": git_rev(), "tokenizer_sha": file_sha(CFG["tokenizer"]),
                        "proxy_sha": file_sha(ROOT / "chapterx/room_proxy.py"), "python": sys.version.split()[0]})
    return VERSION


# ----------------------------------------------------------------------------------------------- scoring

class Scorer:
    """Fixed-text scoring (per-token logprob + rank under a context) through score_worker.py in the JAX venv."""

    def __init__(self, python: Path, tokenizer: Path):
        self.python, self.tokenizer = python, tokenizer
        self.proc: subprocess.Popen | None = None
        self.lock = threading.Lock()
        self.failed: str | None = None
        self.cache: dict[str, dict] = {}

    def _start(self) -> bool:
        if self.proc and self.proc.poll() is None:
            return True
        if not self.python.exists():
            self.failed = f"no JAX venv at {self.python}"
            return False
        env = dict(os.environ, PYTHONPATH=str(ROOT / "jax_training"), JAX_PLATFORM_NAME="cpu")
        try:
            self.proc = subprocess.Popen(
                [str(self.python), str(HERE / "score_worker.py"), str(self.tokenizer)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=env,
                cwd=str(ROOT))
            self.proc.stdin.write(json.dumps({"ping": 1}) + "\n")
            self.proc.stdin.flush()
            ready = json.loads(self.proc.stdout.readline() or "{}")
            if "pong" not in ready:
                raise RuntimeError("worker did not answer")
            self.failed = None
            return True
        except Exception as e:  # noqa: BLE001
            self.failed = f"score worker unavailable: {e}"
            return False

    @staticmethod
    def key(checkpoint: str, context: str, text: str) -> str:
        return hashlib.sha256(f"{checkpoint}\x00{context}\x00{text}".encode()).hexdigest()[:24]

    def score(self, checkpoint: str, items: list[dict], ranks: bool = True) -> dict:
        ck = str(Path(checkpoint).resolve())
        out, todo = {}, []
        for it in items:
            k = self.key(ck, it.get("context", ""), it.get("text", ""))
            if k in self.cache:
                out[it["id"]] = dict(self.cache[k], id=it["id"], cached=True)
            else:
                todo.append(it)
        seconds = loaded = 0.0
        if todo:
            with self.lock:
                if not self._start():
                    raise RuntimeError(self.failed or "score worker unavailable")
                try:
                    self.proc.stdin.write(json.dumps({"checkpoint": ck, "items": todo, "ranks": ranks}) + "\n")
                    self.proc.stdin.flush()
                    resp = json.loads(self.proc.stdout.readline() or "{}")
                except Exception as e:  # noqa: BLE001
                    self.proc = None
                    raise RuntimeError(f"score worker died: {e}")
            if "error" in resp:
                raise RuntimeError(resp["error"])
            seconds, loaded = resp.get("seconds", 0), resp.get("loaded", 0)
            by_id = {r["id"]: r for r in resp.get("results", [])}
            for it in todo:
                r = by_id.get(it["id"])
                if r is None:
                    continue
                self.cache[self.key(ck, it.get("context", ""), it.get("text", ""))] = r
                out[it["id"]] = dict(r, cached=False)
        return {"checkpoint": ck, "results": out, "seconds": seconds, "loaded": loaded}


SCORER: Scorer | None = None


def scorer_checkpoints() -> list[dict]:
    """Checkpoint dirs the scorer can load: the two bases plus every TPU checkpoint."""
    out = []
    for p in CFG["scorers"]:
        if (Path(p) / "config.json").exists():
            out.append({"path": str(p), "name": Path(p).name, "kind": "base"})
    for d in checkpoint_dirs():
        parts = Path(d).parts
        out.append({"path": d, "name": f"{parts[-2]}/{parts[-1]}", "kind": "checkpoint"})
    return out


# ----------------------------------------------------------------------------------------------- labels

LABELS = ["KEEP", "echo", "self-copy", "false speak", "missed intervention", "wrong addressee", "missed callback",
          "generic assistant", "frame leak", "OCR corruption", "dead strangeness", "overquotation",
          "proxy false positive", "other"]
LABEL_LOCK = threading.Lock()


def append_label(record: dict) -> dict:
    """Append one failure/keep label to research/results/room-labels/YYYY-MM-DD.jsonl (schema in README)."""
    if record.get("label") not in LABELS:
        raise ValueError(f"label must be one of {LABELS}")
    if not isinstance(record.get("candidate"), str):
        raise ValueError("candidate text required")
    rec = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "who": str(record.get("who") or "ember"),
        "label": record["label"],
        "correction": record.get("correction") or None,
        "note": record.get("note") or None,
        "source": record.get("source") or {},
        "context": record.get("context") or "",
        "candidate": record["candidate"],
        "checkpoint": record.get("checkpoint"),
        "model": record.get("model"),
        "server": record.get("server"),
        "sampler": record.get("sampler"),
        "proxy_sha": record.get("proxy_sha"),
        "explorer": version_info()["explorer"],
    }
    CFG["labels"].mkdir(parents=True, exist_ok=True)
    path = CFG["labels"] / (time.strftime("%Y-%m-%d") + ".jsonl")
    with LABEL_LOCK, path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return {"ok": True, "path": str(path), "record": rec}


def label_summary(limit: int = 200) -> dict:
    d = CFG["labels"]
    counts: Counter = Counter()
    recent = []
    if d.is_dir():
        for p in sorted(d.glob("*.jsonl")):
            for line in p.open(encoding="utf-8"):
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                counts[r.get("label")] += 1
                recent.append(r)
    return {"labels": LABELS, "counts": dict(counts), "total": sum(counts.values()), "recent": recent[-limit:],
            "dir": str(d)}


# ----------------------------------------------------------------------------------------------- roombank pairs

def roombank_pairs() -> dict:
    """Blind pairwise sheets from `hghost-roombank pairs`: items rebuilt from the key file's state ids and each
    model's replies.jsonl, with the model identities removed. The key is never sent."""
    res = CFG["roombank_results"]
    sheets = []
    if (res / "pairs").is_dir():
        for key_path in sorted((res / "pairs").glob("*-key.json")):
            sheets.append({"stem": key_path.name[: -len("-key.json")], "modified": key_path.stat().st_mtime})
    return {"sheets": sheets, "dir": str(res / "pairs")}


def roombank_sheet(stem: str) -> dict:
    if not re.match(r"^[A-Za-z0-9._-]{1,120}$", stem):
        raise ValueError("bad sheet name")
    res = CFG["roombank_results"]
    key = json.loads((res / "pairs" / f"{stem}-key.json").read_text(encoding="utf-8"))
    replies = {}
    for model in (key["a"], key["b"]):
        path = res / model / "replies.jsonl"
        if path.exists():
            for line in path.open(encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    replies[(model, r.get("state_id"), r.get("mode"), r.get("sample"))] = r.get("text", "")
    states = {}
    if CFG["roombank_bank"].exists():
        for line in CFG["roombank_bank"].open(encoding="utf-8"):
            if line.strip():
                st = json.loads(line)
                states[st.get("id")] = st
    mode, sa, sb = key.get("mode", "sample"), key.get("sample_a", 0), key.get("sample_b", 0)
    items = []
    for it in key["items"]:
        sid = it["state_id"]
        left_model, right_model = it["left"], it["right"]
        st = states.get(sid, {})
        left_text = (replies.get((left_model, sid, mode, sa if left_model == key["a"] else sb)) or "").strip()
        right_text = (replies.get((right_model, sid, mode, sa if right_model == key["a"] else sb)) or "").strip()
        items.append({"n": it.get("n"), "state_id": sid, "kind": st.get("kind"), "frame": st.get("frame"),
                      "turns": st.get("turns"), "left": left_text, "right": right_text})
    items.sort(key=lambda x: x.get("n") or 0)
    return {"stem": stem, "a_b_hidden": True, "mode": mode, "items": items,
            "questions": ["Which would you keep in the room?", "Which makes you want to answer?",
                          "Which sounds specifically like h?"]}


# ----------------------------------------------------------------------------------------------- room-state server (hbox forward)

def roomstate(method: str, path: str, body: dict | None = None, timeout: float = 300.0) -> dict:
    url = CFG["roomstate"] + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def roomstate_status() -> dict:
    try:
        h = roomstate("GET", "/health", timeout=4)
        return {"up": True, "url": CFG["roomstate"], "health": h}
    except Exception as e:  # noqa: BLE001
        return {"up": False, "url": CFG["roomstate"], "error": str(e),
                "hint": "hbox_training/run_room_state_server.sh forward  (or launch) to bring the tunnel up"}


# ----------------------------------------------------------------------------------------------- serving a checkpoint on :8125

SERVE_LOCK = threading.Lock()
SERVE_STATE: dict = {"switching": False, "target": None, "error": None, "since": None}


def serve_checkpoint(path: str, name: str | None = None) -> dict:
    """Point artifacts/serving/<name> at the checkpoint and restart mlx_lm.server on CFG['serve_port'] (the
    second server, never :8124). Blocks until the port answers or 180 s pass."""
    ck = Path(path).resolve()
    if not (ck / "config.json").exists() or not str(ck).startswith(str(ROOT)):
        raise ValueError("checkpoint must be a config-bearing directory under the project")
    if not name:
        name = "x-" + hashlib.sha256(str(ck).encode()).hexdigest()[:10]
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,60}$", name):
        raise ValueError("bad serving name")
    port, session = CFG["serve_port"], CFG["serve_session"]
    with SERVE_LOCK:
        SERVE_STATE.update({"switching": True, "target": str(ck), "error": None, "since": time.time()})
        try:
            CFG["serving"].mkdir(parents=True, exist_ok=True)
            link = CFG["serving"] / name
            if link.is_symlink() or link.exists():
                link.unlink()
            link.symlink_to(ck)
            subprocess.run(["tmux", "kill-session", "-t", session], capture_output=True, check=False)
            cmd = (f"{CFG['mlx_python']} -m mlx_lm.server --model {name} --host 127.0.0.1 --port {port} "
                   f">> /tmp/hghost-serve-{port}.log 2>&1")
            subprocess.run(["tmux", "new-session", "-d", "-s", session, "-c", str(CFG["serving"]), cmd], check=True,
                           capture_output=True)
            deadline = time.time() + 180
            while time.time() < deadline:
                try:
                    http_json(f"http://127.0.0.1:{port}/v1/models", timeout=3)
                    break
                except Exception:  # noqa: BLE001
                    time.sleep(1.5)
            else:
                raise RuntimeError(f"server on :{port} did not come up in 180 s (see /tmp/hghost-serve-{port}.log)")
            return {"ok": True, "name": name, "path": str(ck), "url": f"http://127.0.0.1:{port}",
                    "seconds": round(time.time() - SERVE_STATE["since"], 1)}
        except Exception as e:
            SERVE_STATE["error"] = str(e)
            raise
        finally:
            SERVE_STATE["switching"] = False


# ----------------------------------------------------------------------------------------------- servers

def http_json(url: str, body: dict | None = None, timeout: float = 600.0) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def serving_links() -> dict[str, str]:
    """name -> resolved checkpoint path for every symlink in artifacts/serving."""
    out = {}
    if CFG["serving"].is_dir():
        for p in sorted(CFG["serving"].iterdir()):
            if p.is_symlink():
                out[p.name] = str(p.resolve())
    return out


def checkpoint_dirs() -> list[str]:
    base = CFG["checkpoints"]
    if not base.is_dir():
        return []
    return sorted(str(p) for p in base.glob("*/*/tokens-*") if p.is_dir())


def probe_servers() -> list[dict]:
    links = serving_links()
    by_path = {}
    for name, path in links.items():
        by_path.setdefault(path, name)
    out = []
    for url in SERVER_URLS:
        info = {"url": url, "up": False, "model": SERVER_NAMES.get(url), "path": None}
        try:
            data = http_json(url + "/v1/models", timeout=3)
            for m in data.get("data", []):
                mid = m.get("id", "")
                if mid.startswith("/"):
                    info["path"] = mid
                    if not info["model"]:
                        info["model"] = by_path.get(str(Path(mid).resolve()))
            info["up"] = True
        except Exception as e:  # noqa: BLE001
            info["error"] = str(e)
        out.append(info)
    return out


# ----------------------------------------------------------------------------------------------- haunt

HAUNT_LOCK = threading.Lock()


def text_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]


def haunt(items: list[dict], thresholds: str | None = None) -> dict:
    """Exact-match provenance for each {id, text}; results cached under cache/haunt/<sha>.json."""
    HAUNT_CACHE.mkdir(parents=True, exist_ok=True)
    results, todo, summary = {}, {}, None
    for it in items:
        key = text_key(it["text"])
        cached = HAUNT_CACHE / f"{key}.json"
        if cached.exists():
            results[it["id"]] = json.loads(cached.read_text(encoding="utf-8"))
        else:
            todo[key] = it["text"]
    started = time.time()
    if todo:
        with HAUNT_LOCK, tempfile.TemporaryDirectory(prefix="h-explorer-haunt-") as tmp:
            gens = Path(tmp) / "gens.jsonl"
            outp = Path(tmp) / "out.jsonl"
            gens.write_text("".join(json.dumps({"id": k, "text": t}) + "\n" for k, t in todo.items()), encoding="utf-8")
            cmd = [str(CFG["haunt_bin"]), "scan", "--index", str(CFG["haunt_index"]), "--generations", str(gens),
                   "--tokenizer", str(CFG["tokenizer"]), "--output", str(outp), "--decode"]
            if thresholds:
                cmd += ["--thresholds", thresholds]
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=600, check=False)
            if proc.returncode != 0:
                raise RuntimeError(f"haunt scan failed: {proc.stderr.strip()[-2000:]}")
            for line in proc.stdout.splitlines():
                if line.startswith("{"):
                    obj = json.loads(line)
                    if obj.get("type") == "summary":
                        summary = obj
            by_key = {}
            if outp.exists():
                for line in outp.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        rec = json.loads(line)
                        rec["text_key"] = rec["id"]
                        by_key[rec["id"]] = rec
            for it in items:
                key = text_key(it["text"])
                if key in by_key:
                    (HAUNT_CACHE / f"{key}.json").write_text(json.dumps(by_key[key]), encoding="utf-8")
                    results[it["id"]] = by_key[key]
    return {"results": results, "summary": summary, "scanned": len(todo), "cached": len(items) - len(todo),
            "seconds": round(time.time() - started, 3)}


# ----------------------------------------------------------------------------------------------- observatory

TURN = re.compile(r"^(.{1,40}?): (.*)$", re.DOTALL)


def prompt_blocks(raw: str, cleaned: str) -> list[dict]:
    """Blank-line blocks of the raw prompt, flagged `dropped` when the proxy's cleaned prompt lacks them."""
    split = lambda s: [b.strip() for b in s.rstrip().split("\n\n") if b.strip()]
    have = Counter(split(cleaned))
    out = []
    for b in split(raw):
        m = TURN.match(b)
        turn = m is not None and "\n" not in m.group(1) and ". " not in m.group(1)
        dropped = have[b] <= 0
        if not dropped:
            have[b] -= 1
        out.append({"text": b, "dropped": dropped, "kind": "turn" if turn else ("tail" if b == "h:" else "frame"),
                    "name": m.group(1) if turn else None})
    return out


def align_candidate_tokens(records: list[dict]) -> None:
    """Attach `tokens` (strings aligned with `logprobs`) to every candidate we can re-tokenise exactly."""
    if ENC is None or DEC is None:
        return
    wanted = []
    for r in records:
        for c in r.get("candidates", []):
            t = c.get("text") or ""
            wanted += [" " + t, t]
    if not wanted:
        return
    encoded = ENC.encode(wanted)
    if encoded is None:
        return
    enc = dict(zip(wanted, encoded))
    for r in records:
        stop = ((r.get("sampler") or {}).get("stop") or ["\n\n"])[0]
        for c in r.get("candidates", []):
            n = len(c.get("logprobs") or [])
            c["tokens_text"] = None
            t = c.get("text") or ""
            for variant in (" " + t, t):
                ids = enc.get(variant)
                if ids is None or n == 0:
                    continue
                if len(ids) == n:
                    c["tokens_text"] = DEC.decode(ids)
                    break
                if len(ids) == n - 1:
                    c["tokens_text"] = DEC.decode(ids) + [stop]
                    break


def observatory_dates() -> list[dict]:
    d = CFG["observatory"]
    out = []
    if d.is_dir():
        for p in sorted(d.glob("*.jsonl"), reverse=True):
            out.append({"date": p.stem, "bytes": p.stat().st_size,
                        "records": sum(1 for line in p.open(encoding="utf-8") if line.strip())})
    return out


def observatory_day(date: str) -> dict:
    path = CFG["observatory"] / f"{date}.jsonl"
    records = []
    if path.exists():
        for i, line in enumerate(path.open(encoding="utf-8")):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            r["index"] = i
            r["blocks"] = prompt_blocks(r.get("prompt_raw") or "", r.get("prompt_cleaned") or "")
            records.append(r)
    align_candidate_tokens(records)
    n = len(records)
    mean = lambda xs: (sum(xs) / len(xs)) if xs else None
    chosen_lp = []
    for r in records:
        for c in r.get("candidates", []):
            if c.get("text") == r.get("chosen") and c.get("mean_logprob") is not None:
                chosen_lp.append(c["mean_logprob"])
                break
    summary = {
        "date": date, "records": n,
        "accepted": sum(1 for r in records if r.get("chosen_accepted")),
        "acceptance_rate": mean([1.0 if r.get("chosen_accepted") else 0.0 for r in records]),
        "mean_candidates": mean([len(r.get("candidates", [])) for r in records]),
        "mean_seconds": mean([r["seconds"] for r in records if isinstance(r.get("seconds"), (int, float))]),
        "mean_chosen_logprob": mean(chosen_lp),
        "dropped_echo_turns": sum(int(r.get("dropped_echo_turns") or 0) for r in records),
        "models": sorted({r.get("model") for r in records if r.get("model")}),
    }
    return {"date": date, "summary": summary, "records": records}


# ----------------------------------------------------------------------------------------------- weaves

def validate_weave(w: dict) -> str | None:
    """Mirror universal-weave's DependentWeave::validate: tree links consistent, one active tip, bookmarks
    consistent, roots exactly the parentless nodes, no cycles, everything reachable. Returns an error or None."""
    if not isinstance(w, dict):
        return "weave must be an object"
    for k in ("nodes", "roots", "active", "bookmarked", "metadata"):
        if k not in w:
            return f"missing field {k}"
    nodes, roots, bookmarked = w["nodes"], w["roots"], w["bookmarked"]
    if not isinstance(nodes, dict) or not isinstance(roots, list) or not isinstance(bookmarked, list):
        return "nodes must be an object; roots and bookmarked must be lists"
    if len(nodes) > 20000:
        return "too many nodes"
    active_nodes = []
    for nid, node in nodes.items():
        if not isinstance(node, dict) or node.get("id") != nid:
            return f"node {nid}: id mismatch"
        frm, to = node.get("from"), node.get("to")
        if not isinstance(to, list) or len(set(to)) != len(to):
            return f"node {nid}: to must be a list without duplicates"
        if frm is not None:
            if frm == nid or frm not in nodes:
                return f"node {nid}: bad parent {frm}"
            if nid not in nodes[frm].get("to", []):
                return f"node {nid}: parent does not list it as a child"
        for child in to:
            if child not in nodes or nodes[child].get("from") != nid:
                return f"node {nid}: child {child} does not point back"
        if not isinstance(node.get("contents"), dict) or not isinstance(node["contents"].get("text"), str):
            return f"node {nid}: contents.text must be a string"
        if node.get("active"):
            active_nodes.append(nid)
        if bool(node.get("bookmarked")) != (nid in bookmarked):
            return f"node {nid}: bookmark flag disagrees with weave.bookmarked"
    if set(roots) != {nid for nid, n in nodes.items() if n.get("from") is None} or len(set(roots)) != len(roots):
        return "roots must be exactly the parentless nodes"
    if len(set(bookmarked)) != len(bookmarked) or any(b not in nodes for b in bookmarked):
        return "bookmarked must be a set of node ids"
    if (w["active"] is None and active_nodes) or (w["active"] is not None and active_nodes != [w["active"]]):
        return "exactly the node named by weave.active may carry active=true"
    seen, stack = set(), list(roots)
    while stack:
        nid = stack.pop()
        if nid in seen:
            return "cycle or shared child detected"
        seen.add(nid)
        stack.extend(nodes[nid]["to"])
    if len(seen) != len(nodes):
        return "unreachable nodes"
    return None


def list_weaves() -> list[dict]:
    out = []
    if WEAVES.is_dir():
        for p in sorted(WEAVES.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            info = {"name": p.stem, "modified": p.stat().st_mtime, "bytes": p.stat().st_size}
            try:
                w = json.loads(p.read_text(encoding="utf-8"))
                info["nodes"] = len(w.get("nodes", {}))
                info["roots"] = len(w.get("roots", []))
                meta = w.get("metadata") or {}
                info["modified_iso"] = meta.get("modified")
            except Exception as e:  # noqa: BLE001
                info["error"] = str(e)
            out.append(info)
    return out


def delete_weave(name: str) -> dict:
    if not WEAVE_NAME.match(name):
        raise ValueError("bad weave name")
    p = WEAVES / f"{name}.json"
    if not p.exists():
        raise ValueError("no such weave")
    p.unlink()
    return {"ok": True, "name": name}


def save_weave(name: str, weave: dict) -> dict:
    if not WEAVE_NAME.match(name):
        raise ValueError("weave name must match [A-Za-z0-9][A-Za-z0-9._-]{0,63}")
    err = validate_weave(weave)
    if err:
        raise ValueError(err)
    WEAVES.mkdir(parents=True, exist_ok=True)
    meta = weave.setdefault("metadata", {})
    meta["name"] = name
    meta["modified"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    path = WEAVES / f"{name}.json"
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(weave, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)
    return {"name": name, "nodes": len(weave["nodes"]), "path": str(path)}


# ----------------------------------------------------------------------------------------------- http

MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png"}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    verbose = False

    def log_message(self, fmt, *args):
        if self.verbose:
            super().log_message(fmt, *args)

    # -- helpers
    def _send(self, status: int, body: bytes, ctype: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, status: int = 200) -> None:
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _error(self, status: int, message: str) -> None:
        self._json({"error": message}, status)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length > 50_000_000:
            raise ValueError("request too large")
        raw = self.rfile.read(length) if length else b"{}"
        obj = json.loads(raw or b"{}")
        if not isinstance(obj, dict):
            raise ValueError("body must be a JSON object")
        return obj

    def _stream_begin(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Transfer-Encoding", "chunked")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _stream_line(self, obj) -> None:
        data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
        self.wfile.write(b"%x\r\n%s\r\n" % (len(data), data))
        self.wfile.flush()

    def _stream_end(self) -> None:
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()

    # -- routes
    def do_GET(self):
        url = urllib.parse.urlsplit(self.path)
        q = urllib.parse.parse_qs(url.query)
        path = url.path
        t0 = time.time()
        try:
            if path == "/":
                return self._static("index.html")
            if path == "/favicon.ico":
                return self._send(204, b"", "image/x-icon")
            if path.startswith("/static/"):
                return self._static(path[len("/static/"):])
            if path == "/api/servers":
                return self._json({"servers": probe_servers(), "serving": serving_links(),
                                   "checkpoints": checkpoint_dirs(), "root": str(ROOT), "version": version_info(),
                                   "serve": dict(SERVE_STATE, port=CFG["serve_port"])})
            if path == "/api/version":
                return self._json(version_info())
            if path == "/api/scorers":
                return self._json({"checkpoints": scorer_checkpoints(), "judge": {"leaf": str(CFG["judge_leaf"]),
                                   "base": str(CFG["judge_base"])}, "worker": (SCORER.failed if SCORER else "no scorer")})
            if path == "/api/labels":
                return self._json(label_summary())
            if path == "/api/roombank":
                stem = (q.get("sheet") or [None])[0]
                if stem is None:
                    return self._json(roombank_pairs())
                try:
                    return self._json(roombank_sheet(stem))
                except (ValueError, FileNotFoundError) as e:
                    return self._error(404, str(e))
            if path == "/api/roomstate/status":
                return self._json(roomstate_status())
            if path.startswith("/api/roomstate/"):
                sub = path[len("/api/roomstate"):]
                try:
                    return self._json(roomstate("GET", sub, timeout=60))
                except urllib.error.HTTPError as e:
                    return self._send(e.code, e.read())
                except Exception as e:  # noqa: BLE001
                    return self._error(502, f"room-state server: {e}")
            if path == "/api/observatory":
                date = (q.get("date") or [None])[0]
                if date is None:
                    return self._json({"dates": observatory_dates(), "dir": str(CFG["observatory"])})
                if not DATE.match(date):
                    return self._error(400, "date must be YYYY-MM-DD")
                return self._json(observatory_day(date))
            if path == "/api/weaves":
                name = (q.get("name") or [None])[0]
                if name is None:
                    return self._json({"weaves": list_weaves(), "dir": str(WEAVES)})
                if not WEAVE_NAME.match(name):
                    return self._error(400, "bad weave name")
                p = WEAVES / f"{name}.json"
                if not p.exists():
                    return self._error(404, "no such weave")
                return self._send(200, p.read_bytes())
            return self._error(404, "not found")
        except Exception as e:  # noqa: BLE001
            return self._error(500, f"{type(e).__name__}: {e}")
        finally:
            if path.startswith("/api/"):
                print(f"GET {self.path} {int((time.time() - t0) * 1000)}ms", flush=True)

    def do_POST(self):
        path = urllib.parse.urlsplit(self.path).path
        t0 = time.time()
        try:
            body = self._read_json()
            if path == "/api/generate":
                return self._generate(body)
            if path == "/api/haunt":
                items = body.get("items")
                if not isinstance(items, list) or not items or len(items) > 500:
                    return self._error(400, "items must be a non-empty list of {id, text} (max 500)")
                clean = []
                for it in items:
                    if not isinstance(it, dict) or not isinstance(it.get("text"), str) or "id" not in it:
                        return self._error(400, "each item needs id and text")
                    if it["text"].strip():
                        clean.append({"id": str(it["id"]), "text": it["text"]})
                if not clean:
                    return self._json({"results": {}, "summary": None, "scanned": 0, "cached": 0, "seconds": 0})
                thresholds = body.get("thresholds")
                if thresholds is not None and not re.match(r"^\d+(,\d+)*$", str(thresholds)):
                    return self._error(400, "thresholds must look like 8,16,32")
                return self._json(haunt(clean, thresholds))
            if path == "/api/weaves":
                name, weave = body.get("name"), body.get("weave")
                if not isinstance(name, str) or not isinstance(weave, dict):
                    return self._error(400, "need name and weave")
                try:
                    return self._json(save_weave(name, weave))
                except ValueError as e:
                    return self._error(400, str(e))
            if path == "/api/weaves/delete":
                try:
                    return self._json(delete_weave(str(body.get("name") or "")))
                except ValueError as e:
                    return self._error(400, str(e))
            if path == "/api/labels":
                try:
                    return self._json(append_label(body))
                except ValueError as e:
                    return self._error(400, str(e))
            if path == "/api/score":
                return self._score(body)
            if path == "/api/serve":
                try:
                    return self._json(serve_checkpoint(str(body.get("checkpoint") or ""), body.get("name")))
                except ValueError as e:
                    return self._error(400, str(e))
                except Exception as e:  # noqa: BLE001
                    return self._error(500, str(e))
            if path.startswith("/api/roomstate/"):
                sub = path[len("/api/roomstate"):]
                try:
                    return self._json(roomstate("POST", sub, body, timeout=600))
                except urllib.error.HTTPError as e:
                    return self._send(e.code, e.read())
                except Exception as e:  # noqa: BLE001
                    return self._error(502, f"room-state server: {e}")
            return self._error(404, "not found")
        except json.JSONDecodeError as e:
            return self._error(400, f"bad JSON: {e}")
        except Exception as e:  # noqa: BLE001
            return self._error(500, f"{type(e).__name__}: {e}")
        finally:
            print(f"POST {path} {int((time.time() - t0) * 1000)}ms", flush=True)

    def do_DELETE(self):
        path = urllib.parse.urlsplit(self.path).path
        if path.startswith("/api/roomstate/"):
            try:
                return self._json(roomstate("DELETE", path[len("/api/roomstate"):], timeout=60))
            except urllib.error.HTTPError as e:
                return self._send(e.code, e.read())
            except Exception as e:  # noqa: BLE001
                return self._error(502, f"room-state server: {e}")
        return self._error(404, "not found")

    def _score(self, body: dict) -> None:
        """Stream per-item scores: {type:'start'}, one {type:'result'} per item (worker calls are per item so the
        first result lands early), then {type:'done'}."""
        if SCORER is None:
            return self._error(503, "scorer not configured")
        checkpoint = body.get("checkpoint")
        items = body.get("items")
        if not isinstance(checkpoint, str) or not isinstance(items, list) or not items or len(items) > 200:
            return self._error(400, "need checkpoint and 1..200 items of {id, context, text}")
        for it in items:
            if not isinstance(it, dict) or "id" not in it or not isinstance(it.get("text"), str):
                return self._error(400, "each item needs id and text (context optional)")
            it["context"] = it.get("context") or ""
        ranks = bool(body.get("ranks", True))
        self._stream_begin()
        self._stream_line({"type": "start", "checkpoint": checkpoint, "n": len(items)})
        for it in items:
            try:
                res = SCORER.score(checkpoint, [it], ranks)
                r = res["results"].get(it["id"])
                self._stream_line({"type": "result", "id": it["id"], "result": r, "seconds": res["seconds"],
                                   "loaded": res["loaded"], "checkpoint": res["checkpoint"]})
            except Exception as e:  # noqa: BLE001
                self._stream_line({"type": "error", "id": it["id"], "message": str(e)})
                break
        self._stream_line({"type": "done"})
        self._stream_end()

    def _static(self, rel: str) -> None:
        target = (STATIC / rel).resolve()
        if not str(target).startswith(str(STATIC.resolve()) + os.sep) and target != STATIC.resolve():
            return self._error(403, "forbidden")
        if not target.is_file():
            return self._error(404, "not found")
        self._send(200, target.read_bytes(), MIME.get(target.suffix, "application/octet-stream"))

    def _generate(self, body: dict) -> None:
        server = body.get("server")
        model = body.get("model")
        prompt = body.get("prompt")
        if server not in SERVER_URLS:
            return self._error(400, f"server must be one of {SERVER_URLS}")
        if not isinstance(model, str) or not model:
            return self._error(400, "model name required (see /api/servers)")
        if not isinstance(prompt, str):
            return self._error(400, "prompt must be a string")
        try:
            n = max(1, min(64, int(body.get("n", 1))))
            max_tokens = max(1, min(2048, int(body.get("max_tokens", 40))))
            temperature = max(0.0, float(body.get("temperature", 0.7)))
            top_p = min(1.0, max(0.0, float(body.get("top_p", 0.9))))
        except (TypeError, ValueError):
            return self._error(400, "n, max_tokens, temperature, top_p must be numbers")
        stop = body.get("stop", ["\n\n"])
        if stop is not None and (not isinstance(stop, list) or not all(isinstance(s, str) for s in stop)):
            return self._error(400, "stop must be a list of strings or null")
        stop = [s for s in (stop or []) if s]
        upstream = {"model": model, "prompt": prompt, "max_tokens": max_tokens, "temperature": temperature,
                    "top_p": top_p, "logprobs": True}
        if stop:
            upstream["stop"] = stop
        rp = body.get("repetition_penalty")
        if isinstance(rp, (int, float)) and rp and rp != 1.0:
            upstream["repetition_penalty"] = float(rp)
        sampler = {"temperature": temperature, "top_p": top_p, "max_tokens": max_tokens, "stop": stop,
                   "repetition_penalty": upstream.get("repetition_penalty")}
        srv = next((x for x in probe_servers() if x["url"] == server), {})
        repro = {"server": server, "model": model, "checkpoint": srv.get("path"), "backend": "mlx_lm.server",
                 "tokenizer_sha": version_info()["tokenizer_sha"], "explorer": version_info()["explorer"],
                 "stop": stop, "logprobs": True, "seed": None}
        self._stream_begin()
        self._stream_line({"type": "start", "n": n, "server": server, "model": model, "sampler": sampler, "repro": repro})
        for i in range(n):
            t0 = time.time()
            try:
                resp = http_json(server + "/v1/completions", upstream)
                choice = resp["choices"][0]
                content = ((choice.get("logprobs") or {}).get("content") or [])
                ids = [int(t["id"]) for t in content]
                lps = [t.get("logprob") for t in content]
                texts = DEC.decode(ids) if DEC else [""] * len(ids)
                tokens = [{"id": tid, "text": tx, "logprob": lp} for tid, tx, lp in zip(ids, texts, lps)]
                text = "".join(texts) if DEC else choice.get("text", "")
                valid = [lp for lp in lps if isinstance(lp, (int, float))]
                self._stream_line({
                    "type": "sample", "index": i, "text": text, "text_stripped": choice.get("text", ""),
                    "tokens": tokens, "finish_reason": choice.get("finish_reason"),
                    "mean_logprob": (sum(valid) / len(valid)) if valid else None,
                    "seconds": round(time.time() - t0, 3), "server": server, "model": model, "sampler": sampler,
                    "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "usage": resp.get("usage"), "repro": repro,
                })
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", "replace")[:500]
                self._stream_line({"type": "error", "index": i, "message": f"upstream {e.code}: {detail}"})
                break
            except Exception as e:  # noqa: BLE001
                self._stream_line({"type": "error", "index": i, "message": f"{type(e).__name__}: {e}"})
                break
        self._stream_line({"type": "done"})
        self._stream_end()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--port", type=int, default=8130)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--server", action="append", default=[],
                    help="model server as URL or name@URL (repeatable; default :8124 and :8125, names from artifacts/serving)")
    ap.add_argument("--tokenizer", type=Path, default=CFG["tokenizer"])
    ap.add_argument("--haunt-index", type=Path, default=CFG["haunt_index"])
    ap.add_argument("--observatory", type=Path, default=CFG["observatory"])
    ap.add_argument("--roomstate", default=CFG["roomstate"], help="room-state server (hbox forward) base URL")
    ap.add_argument("--verbose", action="store_true", help="log every HTTP request")
    args = ap.parse_args()

    global DEC, ENC, SCORER
    CFG["tokenizer"], CFG["haunt_index"], CFG["observatory"] = args.tokenizer, args.haunt_index, args.observatory
    CFG["roomstate"] = args.roomstate.rstrip("/")
    SCORER = Scorer(CFG["jax_python"], CFG["tokenizer"])
    if args.server:
        SERVER_URLS.clear()
        for s in args.server:
            name, _, url = s.rpartition("@")
            SERVER_URLS.append(url)
            if name:
                SERVER_NAMES[url] = name
    if CFG["tokenizer"].exists():
        DEC = Decoder(CFG["tokenizer"])
        ENC = Encoder(CFG["venv_python"], CFG["tokenizer"])
    else:
        print(f"tokenizer not found at {CFG['tokenizer']}; tokens will be ids only", flush=True)
    Handler.verbose = args.verbose
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    httpd.daemon_threads = True
    print(f"h explorer on http://{args.host}:{args.port}  (servers: {', '.join(SERVER_URLS)})", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
