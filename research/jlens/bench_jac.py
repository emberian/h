"""Time one d x d Jacobian (single vmapped vjp over the identity basis) for a model/layer."""
import os, sys, time
import numpy as np, jax
sys.path.insert(0, os.path.dirname(__file__))
from jlens import Lensing, get_tokenizer, room_prompts, encode, pad_ids

model, layer, T, chunk = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
print("XLA_FLAGS=", os.environ.get("XLA_FLAGS"), "devices", jax.devices(), flush=True)
lens = Lensing(model)
tok = get_tokenizer()
ids = encode(tok, room_prompts()[0]["prompt"])[:T]
batch = pad_ids(ids, T)
h = lens.hidden(batch, layer)
for i in range(3):
    t0 = time.time()
    G = lens.jacobian(h, layer, T - 1, chunk)
    G.block_until_ready()
    print(f"run {i}: {time.time() - t0:.1f}s (T={T}, d={lens.d}, chunk={chunk}, layers {layer}..{lens.L-1})", flush=True)
