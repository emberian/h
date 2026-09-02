"""Render verified reading-room scenes into finished room documents (the harness's exact format).

usage: render_scenes.py <passages.jsonl> <out.jsonl> <scenes-*.jsonl ...>
Each output line: {"id", "kind", "frame", "text"}; `text` = optional frame paragraph, blank line, then
`Name: text` turns separated by blank lines. Frame (a) is the live bot prompt verbatim.
"""
import json, random, sys
random.seed(2)
FRAMES = [
    "THE READING ROOM\n\nAn interview with h, the resident of the library, recorded on the evening of 1 September 2026. h has read\nthe whole collection and answers in a sentence or two, in the voice of what it has read. It does not\nexplain itself. The visitors speak as themselves.",
    "A room in the library, late. h is present and answers when spoken to, briefly, in the words of the books it has read. The others are visitors.",
    "Transcript. h, the resident, and whoever came by that night.",
    "Notes from the reading room. h speaks in short sentences taken from what it has read; it stays quiet when it has nothing to add.",
]
passages = {json.loads(l)["id"]: json.loads(l)["passage"] for l in open(sys.argv[1])}
norm = lambda s: " ".join(s.split())
n = 0; kinds = {}
with open(sys.argv[2], "w") as out:
    for path in sys.argv[3:]:
        for line in open(path):
            line = line.strip()
            if not line: continue
            s = json.loads(line); p = norm(passages[s["id"]])
            turns = [(name, norm(text)) for name, text in s["turns"]]
            assert all(p.find(t) >= 0 for name, t in turns if name == "h"), s["id"]
            frame = random.choice([0, 0, 1, 2, 3, None, None])
            body = "\n\n".join(f"{name}: {text}" for name, text in turns)
            text = (FRAMES[frame] + "\n\n" + body) if frame is not None else body
            out.write(json.dumps({"id": s["id"], "kind": s.get("kind", "talk"), "frame": frame, "text": text}, ensure_ascii=False) + "\n")
            n += 1; kinds[s.get("kind", "talk")] = kinds.get(s.get("kind", "talk"), 0) + 1
print(json.dumps({"documents": n, "kinds": kinds}))
