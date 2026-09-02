"""Render verified reading-room scenes into finished room documents (the harness's exact format).

usage: render_scenes.py <passages.jsonl> <out.jsonl> <scenes-*.jsonl ...>
Each output line: {"id", "kind", "frame", "text"}; `text` = optional frame paragraph, blank line, then
`Name: text` turns separated by blank lines. Frame (a) is the live bot prompt verbatim.
"""
import json
import random
import sys

random.seed(2)
FRAMES = [
    "THE READING ROOM\n\nAn interview with h, the resident of the library, recorded on the evening of 1 September 2026. h has read\nthe whole collection and answers in a sentence or two, in the voice of what it has read. It does not\nexplain itself. The visitors speak as themselves.",
    "A room in the library, late. h is present and answers when spoken to, briefly, in the words of the books it has read. The others are visitors.",
    "Transcript. h, the resident, and whoever came by that night.",
    "Notes from the reading room. h speaks in short sentences taken from what it has read; it stays quiet when it has nothing to add.",
]
with open(sys.argv[1]) as fh:
    passages = {json.loads(l)["id"]: json.loads(l)["passage"] for l in fh}
import re


def sentence_shaped(text: str) -> bool:
    """An h line must look like whole sentences: starts with a capital, quote, digit or bracket and ends with
    terminal punctuation (or a closing quote after it). Fragments sliced mid-sentence are dropped."""
    t = text.strip()
    return bool(re.match(r"^[\"'“‘(\[A-Z0-9]", t)) and bool(re.search(r"[.!?…]['\"”’)\]]*$", t))

norm = lambda s: " ".join(s.split())
n = 0; kinds = {}; dropped = 0
with open(sys.argv[2], "w") as out:
    for path in sys.argv[3:]:
        with open(path) as fh:
            lines = fh.read().splitlines()
        for line in lines:
            line = line.strip()
            if not line: continue
            s = json.loads(line); p = norm(passages[s["id"]])
            turns = [(name, norm(text)) for name, text in s["turns"]]
            # drop trailing pairs whose h line is a fragment; skip the scene if nothing sentence-shaped is left
            while turns and turns[-1][0] == "h" and not sentence_shaped(turns[-1][1]):
                turns = turns[:-2]
            bad = [t for name, t in turns if name == "h" and not sentence_shaped(t)]
            if not turns or bad:
                dropped += 1
                continue
            assert all(p.find(t) >= 0 for name, t in turns if name == "h"), s["id"]
            frame = random.choice([0, 0, 1, 2, 3, None, None])
            body = "\n\n".join(f"{name}: {text}" for name, text in turns)
            text = (FRAMES[frame] + "\n\n" + body) if frame is not None else body
            out.write(json.dumps({"id": s["id"], "kind": s.get("kind", "talk"), "frame": frame, "text": text}, ensure_ascii=False) + "\n")
            n += 1; kinds[s.get("kind", "talk")] = kinds.get(s.get("kind", "talk"), 0) + 1
print(json.dumps({"documents": n, "kinds": kinds, "dropped_fragment_scenes": dropped}))
