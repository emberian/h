"""Export the lens contexts (token ids) so another implementation (hbox/PyTorch) uses the same ones."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from jlens import contexts_for, get_tokenizer, OUT

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=100)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--min-len", type=int, default=64)
ap.add_argument("--max-len", type=int, default=128)
ap.add_argument("--room-last", type=int, default=0)
ap.add_argument("--out", default=None)
a = ap.parse_args()
ctx = contexts_for(get_tokenizer(), a.n, a.seed, True, None, a.room_last, a.min_len, a.max_len)
out = a.out or (OUT / f"contexts-n{a.n}-s{a.seed}.json")
json.dump({"args": vars(a), "contexts": ctx}, open(out, "w"))
print(out, len(ctx), "contexts; lengths", min(len(c["ids"]) for c in ctx), "-", max(len(c["ids"]) for c in ctx))
