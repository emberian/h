"""Verify reading-room scenes against their passages.

usage: check_scenes.py <passages.jsonl> <scenes.jsonl>  -> prints counts; exit 1 if any scene is invalid.
A scene is valid when: its id exists; h turns default to mode "cite" (verbatim from the passage); a scene-level
"mode" or per-turn "modes" {"<turn index>": "cite|compose|bridge"} lets compose/bridge lines be original (they must
NOT be verbatim passage text of 8+ words); turns alternate visitor/h and end with an h turn; every h line is a
verbatim substring of the passage (after whitespace normalization), 3-70 words; every visitor line is
1-40 words, contains no newline, and is not a bare label; visitor names are plain handles.
"""
import json, re, sys
passages = {json.loads(l)["id"]: json.loads(l)["passage"] for l in open(sys.argv[1])}
norm = lambda s: " ".join(s.split())
NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_./:@-]{0,30}$")
ok = bad = 0; reasons = {}
def fail(r):
    global bad; bad += 1; reasons[r] = reasons.get(r, 0) + 1
for line in open(sys.argv[2]):
    line = line.strip()
    if not line: continue
    try: s = json.loads(line)
    except Exception: fail("json"); continue
    p = passages.get(s.get("id"))
    if p is None: fail("unknown id"); continue
    turns = s.get("turns") or []
    if len(turns) < 2 or turns[-1][0] != "h" or turns[0][0] == "h": fail("shape"); continue
    good = True
    for i, (name, text) in enumerate(turns):
        if name == "h":
            t = norm(text); w = len(t.split())
            mode = (s.get("modes") or {}).get(str(i), s.get("mode", "cite"))
            if mode == "cite" and norm(p).find(t) < 0: good = False; fail("h not verbatim"); break
            if mode in ("compose", "bridge") and norm(p).find(t) >= 0 and w >= 8: good = False; fail("compose line is verbatim"); break
            if w < 3 or w > 70: good = False; fail("h length"); break
        else:
            if not NAME.match(name) or name.lower() == "h": good = False; fail("visitor name"); break
            w = len(text.split())
            if "\n" in text or w < 1 or w > 40: good = False; fail("visitor length"); break
        if i > 0 and (turns[i-1][0] == "h") == (name == "h"): good = False; fail("alternation"); break
    if good: ok += 1
print(json.dumps({"ok": ok, "bad": bad, "reasons": reasons}))
sys.exit(1 if bad else 0)
