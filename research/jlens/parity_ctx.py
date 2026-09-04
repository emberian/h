"""Save the JAX Jacobian (d x d, same-position, last token) for one context, for cross-implementation parity."""
import os, sys, json, time
import numpy as np, jax
sys.path.insert(0, os.path.dirname(__file__))
from jlens import Lensing, get_tokenizer, room_prompts, encode, pad_ids, model_dir

model, layer, T = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
lens = Lensing(model)
tok = get_tokenizer()
ids = encode(tok, room_prompts()[0]["prompt"])[:T]
batch = pad_ids(ids, T)
h = lens.hidden(batch, layer)
t0 = time.time()
G = np.asarray(lens.jacobian(h, layer, T - 1, 256))
J = G[:, T - 1, :]
out = model_dir(model)
np.save(out / f"parity-L{layer}-J.npy", J.astype(np.float32))
np.save(out / f"parity-L{layer}-hl.npy", np.asarray(h)[0].astype(np.float32))
hf = np.asarray(lens.residual_from(h, layer))[0, T - 1]
np.save(out / f"parity-L{layer}-hfinal.npy", hf.astype(np.float32))
json.dump({"model": model, "layer": layer, "T": T, "ids": ids, "seconds": time.time() - t0, "frob": float(np.linalg.norm(J))}, open(out / f"parity-L{layer}.json", "w"))
print("saved", out, "frob", np.linalg.norm(J), "seconds", time.time() - t0)
