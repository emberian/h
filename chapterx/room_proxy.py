"""Reply filter between ChapterX and mlx_lm.server: OpenAI-compatible /v1/completions on PORT, forwarding to
UPSTREAM. For each request it samples up to N candidates and returns the first that is not (a) empty or one
word, (b) an echo of the last visitor line, (c) a copy of an earlier h line in the prompt, (d) a sentence of the
frame. If all candidates fail, the least-bad one (highest word overlap distance) is returned.
usage: room_proxy.py [--port 8126] [--upstream http://127.0.0.1:8124] [--candidates 4]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WORD = re.compile(r"[a-z0-9']+")


def words(text: str) -> set[str]:
    return set(WORD.findall(text.lower()))


def overlap(a: str, b: str) -> float:
    """Fraction of the shorter text's words found in the other (1.0 = one contains the other)."""
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return 0.0
    small, big = (wa, wb) if len(wa) <= len(wb) else (wb, wa)
    return len(small & big) / len(small)


TURN = re.compile(r"^(.{1,40}?): (.*)$", re.DOTALL)


def split_turn(block: str) -> tuple[str, str] | None:
    m = TURN.match(block)
    if not m or "\n" in m.group(1) or ". " in m.group(1):
        return None
    return m.group(1), m.group(2)


def prompt_parts(prompt: str) -> tuple[list[str], str, list[str], str]:
    """Split a rendered room prompt into frame sentences, the last visitor line, earlier h lines, and a cleaned
    prompt in which h turns that echoed the visitor line before them are removed (context hygiene)."""
    blocks = [b.strip() for b in prompt.rstrip().split("\n\n") if b.strip()]
    tail = ""
    if blocks and blocks[-1] == "h:":
        blocks = blocks[:-1]
        tail = "\n\nh:"
    frame_sentences: list[str] = []
    kept: list[str] = []
    last_visitor = ""
    h_lines: list[str] = []
    for b in blocks:
        turn = split_turn(b)
        if turn is None:
            frame_sentences += [x.strip() for x in re.split(r"(?<=[.!?])\s+", b) if len(x.strip()) > 20]
            kept.append(b)
            continue
        name, text = turn
        if name == "h":
            if last_visitor and overlap(text, last_visitor) >= 0.6:
                continue  # an echo: drop it from the context
            h_lines.append(text)
        else:
            last_visitor = text
        kept.append(b)
    cleaned = "\n\n".join(kept) + tail
    return frame_sentences, last_visitor, h_lines, cleaned


def judge(candidate: str, frame_sentences: list[str], last_visitor: str, h_lines: list[str]) -> tuple[bool, float]:
    text = candidate.strip()
    if len(words(text)) < 2:
        return False, 0.0
    worst = 0.0
    if last_visitor:
        worst = max(worst, overlap(text, last_visitor))
    for line in h_lines[-6:]:
        worst = max(worst, overlap(text, line))
    for s in frame_sentences:
        worst = max(worst, overlap(text, s))
    return worst < 0.6, worst


OBSERVATORY = Path(os.environ.get("HGHOST_OBSERVATORY", "research/results/room-observatory"))
PROXY_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]


def record(entry: dict) -> None:
    """Append one opportunity-to-speak record (prompt, candidates, logprobs, decision) to today's JSONL."""
    OBSERVATORY.mkdir(parents=True, exist_ok=True)
    path = OBSERVATORY / (time.strftime("%Y-%m-%d") + ".jsonl")
    with path.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class Handler(BaseHTTPRequestHandler):
    upstream = "http://127.0.0.1:8124"
    candidates = 4

    def log_message(self, fmt, *args):  # quieter
        pass

    def _forward(self, body: dict) -> dict:
        req = urllib.request.Request(
            self.upstream + "/v1/completions",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as r:
            raw = r.read()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"upstream returned non-JSON ({raw[:80]!r})") from exc

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length) or b"{}")
        if self.path.rstrip("/") != "/v1/completions" or not isinstance(body.get("prompt"), str):
            payload = self._forward(body)
            return self._send(payload)
        streaming = bool(body.get("stream"))
        body = dict(body, stream=False)  # candidates are sampled whole; the reply is streamed back as one chunk
        raw_prompt = body["prompt"]
        frame_sentences, last_visitor, h_lines, cleaned = prompt_parts(raw_prompt)
        dropped = raw_prompt.count("\n\nh: ") - cleaned.count("\n\nh: ")
        body = dict(body, prompt=cleaned)
        best, best_score, payload = None, -1.0, None
        tried = []
        started = time.time()
        upstream_body = dict(body, logprobs=True)
        for _ in range(self.candidates):
            payload = self._forward(upstream_body)
            choice = payload["choices"][0]
            text = choice["text"]
            ok, worst = judge(text, frame_sentences, last_visitor, h_lines)
            lp = [t.get("logprob") for t in ((choice.get("logprobs") or {}).get("content") or [])]
            tried.append({"text": text, "overlap": round(worst, 3), "accepted": ok, "logprobs": lp,
                          "tokens": len(lp), "mean_logprob": (sum(lp) / len(lp)) if lp else None})
            if ok:
                best = text
                break
            if (1.0 - worst) > best_score:
                best, best_score = text, 1.0 - worst
        chosen = best if best is not None else payload["choices"][0]["text"]
        payload["choices"][0]["text"] = chosen
        payload["choices"][0].pop("logprobs", None)
        payload["room_proxy"] = {"tried": [(t["overlap"], t["text"].strip()[:60]) for t in tried],
                                 "accepted": bool(tried and tried[-1]["accepted"])}
        record({
            "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "model": body.get("model"), "proxy_sha": PROXY_SHA,
            "sampler": {k: body.get(k) for k in ("temperature", "top_p", "max_tokens", "stop", "repetition_penalty")},
            "prompt_raw": raw_prompt, "prompt_cleaned": cleaned,
            "dropped_echo_turns": dropped, "last_visitor": last_visitor, "candidates": tried, "chosen": chosen,
            "chosen_accepted": bool(best is not None and tried and tried[-1]["accepted"]),
            "seconds": round(time.time() - started, 2),
        })
        print(json.dumps({"visitor": last_visitor[:60], "dropped_echoes": dropped, "stream": streaming,
                          "tried": [(t["overlap"], t["text"].strip()[:60]) for t in tried]}), flush=True)
        if streaming:
            self._send_stream(payload, chosen)
        else:
            self._send(payload)

    def do_GET(self):
        req = urllib.request.Request(self.upstream + self.path)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_stream(self, payload: dict, text: str):
        """OpenAI-style SSE: one chunk carrying the whole chosen reply, then [DONE]."""
        chunk = {"id": payload.get("id", "room-proxy"), "object": "text_completion", "created": payload.get("created", 0),
                 "model": payload.get("model", ""), "choices": [{"text": text, "index": 0, "logprobs": None, "finish_reason": "stop"}]}
        data = (f"data: {json.dumps(chunk)}\n\n" + "data: [DONE]\n\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send(self, payload: dict):
        data = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8126)
    ap.add_argument("--upstream", default="http://127.0.0.1:8124")
    ap.add_argument("--candidates", type=int, default=4)
    args = ap.parse_args()
    Handler.upstream = args.upstream
    Handler.candidates = args.candidates
    print(f"room proxy on :{args.port} -> {args.upstream}, {args.candidates} candidates", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
