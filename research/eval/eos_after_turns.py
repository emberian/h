"""Does the model believe a room ends after two exchanges? For each transcript, the next-token distribution after
the second h turn: P(EOS), P(blank line), and P(any name-like continuation). usage: eos_after_turns.py <ckpt> [<ckpt> ...]"""
import json, sys, numpy as np, jax, jax.numpy as jnp
from tokenizers import Tokenizer
from h1jax.checkpoint import load_hf_params
from h1jax.config import FalconH1Config
from h1jax.model import falcon_h1_forward

FRAME = "A room in the library, late. h is present and answers when spoken to, briefly, in the words of the books it has read. The others are visitors."
TRANSCRIPTS = [
    [("ember", "hi h"), ("h", "The lake was covered with blank space."), ("ember", "what lake?"), ("h", "The one that is not on any map.")],
    [("rat", "h, what are you reading tonight"), ("h", "A treatise on the migration of souls."), ("rat", "any good?"), ("h", "It is neither good nor bad; it is exact.")],
    [("mira", "does anyone know what time it is"), ("h", "It is late enough that the books have stopped talking."), ("mira", "lol ok h"), ("h", "You laugh, but the shelves are listening.")],
    [("dov", "h can you explain quantum computing simply"), ("h", "One might for example see streams of coloured liquid rising from the crystals."), ("dov", "that's not simple"), ("h", "Simplicity is the last thing a crystal learns.")],
]
tok = Tokenizer.from_file("kaggle/base_model_dataset_public/tokenizer.json")
EOS = 11
nl_ids = tok.encode("\n\n", add_special_tokens=False).ids
for ckpt in sys.argv[1:]:
    cfg = FalconH1Config.from_json(f"{ckpt}/config.json")
    params = load_hf_params(ckpt, cfg)
    p_eos, p_nl = [], []
    for t in TRANSCRIPTS:
        text = FRAME + "\n\n" + "\n\n".join(f"{n}: {x}" for n, x in t)
        ids = tok.encode(text, add_special_tokens=False).ids
        logits = falcon_h1_forward(params, jnp.asarray([ids], jnp.int32), cfg, compute_dtype=jnp.float32, gradient_checkpointing=False, layer_scan=True)
        probs = np.asarray(jax.nn.softmax(logits[0, -1].astype(jnp.float32)))
        p_eos.append(float(probs[EOS])); p_nl.append(float(probs[nl_ids[0]]))
    print(json.dumps({"checkpoint": ckpt.split("/")[-3], "P(EOS)": [round(x, 3) for x in p_eos], "P(blank line)": [round(x, 3) for x in p_nl], "mean P(EOS)": round(float(np.mean(p_eos)), 3)}))
