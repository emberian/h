"""Render verified reading-room scenes into finished room documents (the harness's exact format).

usage: render_scenes.py <passages.jsonl> <out.jsonl> <scenes-*.jsonl ...> [--stitch K]
With --stitch K, scenes are grouped K at a time into one room document (one frame, blank-line-separated
turns, visitor names made consistent across the group) so the model sees rooms that continue past two
exchanges instead of ending in EOS after every scene.
Each output line: {"id", "kind", "frame", "text"}; `text` = optional frame paragraph, blank line, then
`Name: text` turns separated by blank lines. Frame (a) is the live bot prompt verbatim.
"""
import json
import random
import sys

random.seed(2)
STITCH = 0
if "--stitch" in sys.argv:
    i = sys.argv.index("--stitch"); STITCH = int(sys.argv[i + 1]); del sys.argv[i:i + 2]
FRAMES = [
    "THE READING ROOM\n\nAn interview with h, the resident of the library, recorded on the evening of 1 September 2026. h has read\nthe whole collection and answers in a sentence or two, in the voice of what it has read. It does not\nexplain itself. The visitors speak as themselves.",
    "A room in the library, late. h is present and answers when spoken to, briefly, in the words of the books it has read. The others are visitors.",
    "Transcript. h, the resident, and whoever came by that night.",
    "Notes from the reading room. h speaks in short sentences taken from what it has read; it stays quiet when it has nothing to add.",
]
with open(sys.argv[1]) as fh:
    passages = {json.loads(l)["id"]: json.loads(l)["passage"] for l in fh}
import re

NAME_POOL = ["ember", "rat", "mira", "dov", "kestrel", "ana", "jules", "tam", "oriol", "wren", "sable", "nico", "pim",
             "lux", "quill", "marrow", "ash", "vesna", "hollis", "bee", "cmr://ember", "glitch", "iris", "finn", "draig"]


def flush_group(group, out):
    """Write one room document made of several scenes: a single frame, visitor names remapped so the same few
    people stay in the room, turns separated by blank lines. Kinds and ids are kept for provenance."""
    cast = random.sample(NAME_POOL, k=random.randint(2, 4))
    mapping = {}
    turns_all = []
    for s, turns in group:
        for name, text in turns:
            if name != "h" and name not in mapping:
                mapping[name] = cast[len(mapping) % len(cast)]
            turns_all.append((name if name == "h" else mapping[name], text))
    frame = random.choice([0, 1, 2, 3, None])
    body = "\n\n".join(f"{name}: {text}" for name, text in turns_all)
    text = (FRAMES[frame] + "\n\n" + body) if frame is not None else body
    out.write(json.dumps({"id": "+".join(s["id"] for s, _ in group), "kind": "stitched",
                          "kinds": [s.get("kind", "talk") for s, _ in group], "frame": frame, "text": text},
                         ensure_ascii=False) + "\n")


def sentence_shaped(text: str) -> bool:
    """An h line must look like whole sentences: starts with a capital, quote, digit or bracket and ends with
    terminal punctuation (or a closing quote after it). Fragments sliced mid-sentence are dropped."""
    t = text.strip()
    return bool(re.match(r"^[\"'“‘(\[A-Z0-9]", t)) and bool(re.search(r"[.!?…]['\"”’)\]]*$", t))

norm = lambda s: " ".join(s.split())
n = 0; kinds = {}; dropped = 0; pending = []
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
            if s.get("silent"):
                turns = turns[:-1]  # silence scenes: the appended h turn was for the checker only
            frame = random.choice([0, 0, 1, 2, 3, None, None])
            if STITCH > 1:
                pending.append((s, turns))
                if len(pending) >= STITCH:
                    flush_group(pending, out); pending.clear()
                n += 1; kinds[s.get("kind", "talk")] = kinds.get(s.get("kind", "talk"), 0) + 1
                continue
            body = "\n\n".join(f"{name}: {text}" for name, text in turns)
            text = (FRAMES[frame] + "\n\n" + body) if frame is not None else body
            out.write(json.dumps({"id": s["id"], "kind": s.get("kind", "talk"), "frame": frame, "text": text}, ensure_ascii=False) + "\n")
            n += 1; kinds[s.get("kind", "talk")] = kinds.get(s.get("kind", "talk"), 0) + 1
if STITCH > 1 and pending:
    with open(sys.argv[2], "a") as out:
        flush_group(pending, out)
print(json.dumps({"scenes": n, "stitch": STITCH, "kinds": kinds, "dropped_fragment_scenes": dropped}))
