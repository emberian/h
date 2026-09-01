from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit eager float32 Falcon-H1 reference logits")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--tokens", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    model = AutoModelForCausalLM.from_pretrained(
        args.checkpoint,
        dtype=torch.float32,
        attn_implementation="eager",
        local_files_only=True,
    ).eval()
    tokens = torch.from_numpy(np.load(args.tokens).astype(np.int64))
    with torch.inference_mode():
        logits = model(tokens, use_cache=False, logits_to_keep=0).logits.float().cpu().numpy()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez(args.output, logits=logits)


if __name__ == "__main__":
    main()
