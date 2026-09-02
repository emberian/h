"""Sample clean prose passages from the corpus-v1 training shards for reading-room scenes.

Each passage is 60-160 words, sentence-aligned, from a train document; furniture-heavy and OCR-column
text is rejected by cheap heuristics (alphabetic ratio, line length, form feeds, digit density).
Output: JSONL with id, source, path, doc_id, passage.
"""
import gzip, json, random, re, sys
from pathlib import Path

random.seed(20260901)
root = Path("artifacts/dataset")
out = Path(sys.argv[1]); n_target = int(sys.argv[2])
shards = sorted(root.glob("train-*.jsonl.gz"))
docs = []
for sh in shards:
    with gzip.open(sh, "rt") as f:
        for line in f:
            d = json.loads(line)
            if d.get("tokens", 0) < 3000:
                continue
            docs.append((d["id"], d.get("source"), d.get("path"), d["text"]))
print("docs", len(docs), file=sys.stderr)
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")
BAD = re.compile(r"\f|\|{2,}|www\.|http|©|JSTOR|Downloaded from|All rights reserved|ISBN|Library of Congress", re.I)

def clean_paragraphs(text):
    for para in re.split(r"\n\s*\n", text):
        p = " ".join(para.split())
        if len(p) < 300 or len(p) > 2500 or BAD.search(p):
            continue
        letters = sum(c.isalpha() for c in p); digits = sum(c.isdigit() for c in p)
        if letters / len(p) < 0.78 or digits / len(p) > 0.03:
            continue
        words = p.split()
        if sum(len(w) == 1 for w in words) / len(words) > 0.08:  # OCR columns / broken words
            continue
        if max(len(w) for w in words) > 28:
            continue
        yield p

per_doc = {}
random.shuffle(docs)
rows = []
for doc_id, source, path, text in docs:
    paras = list(clean_paragraphs(text))
    if not paras:
        continue
    random.shuffle(paras)
    for p in paras[:3]:
        sents = SENT.split(p)
        # take a sentence-aligned window of 60-160 words
        acc = []; words = 0
        for s in sents:
            acc.append(s); words += len(s.split())
            if words >= 60:
                break
        if words < 60 or words > 160:
            continue
        rows.append({"id": f"p{len(rows):05d}", "doc_id": doc_id, "source": source, "path": path, "passage": " ".join(acc)})
    if len(rows) >= n_target:
        break
random.shuffle(rows)
with out.open("w") as f:
    for r in rows[:n_target]:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("passages", min(len(rows), n_target), "from", len({r["doc_id"] for r in rows[:n_target]}), "docs", file=sys.stderr)
