"""Reply filter between ChapterX and mlx_lm.server: OpenAI-compatible /v1/completions on PORT, forwarding to
UPSTREAM. For each request it samples up to N candidates and returns the first that is not (a) empty or one
word, (b) an echo of the last visitor line, (c) a copy of an earlier h line in the prompt, (d) a sentence of the
frame. If all candidates fail, the least-bad one (highest word overlap distance) is returned.
usage: room_proxy.py [--port 8126] [--upstream http://127.0.0.1:8124] [--candidates 4]
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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
            return json.loads(r.read())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length) or b"{}")
        if self.path.rstrip("/") != "/v1/completions" or not isinstance(body.get("prompt"), str):
            payload = self._forward(body)
            return self._send(payload)
        frame_sentences, last_visitor, h_lines, cleaned = prompt_parts(body["prompt"])
        dropped = body["prompt"].count("\n\nh: ") - cleaned.count("\n\nh: ")
        body = dict(body, prompt=cleaned)
        best, best_score, payload = None, -1.0, None
        tried = []
        for _ in range(self.candidates):
            payload = self._forward(body)
            text = payload["choices"][0]["text"]
            ok, worst = judge(text, frame_sentences, last_visitor, h_lines)
            tried.append((round(worst, 2), text.strip()[:60]))
            if ok:
                best = text
                break
            if (1.0 - worst) > best_score:
                best, best_score = text, 1.0 - worst
        payload["choices"][0]["text"] = best if best is not None else payload["choices"][0]["text"]
        payload["room_proxy"] = {"tried": tried, "accepted": bool(best is not None and tried[-1][0] < 0.6)}
        print(json.dumps({"visitor": last_visitor[:60], "dropped_echoes": dropped, "tried": tried}), flush=True)
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
