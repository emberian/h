"""MLX worker for ``hghost-evalpack``: fixed-prompt, fixed-seed sampling from a checkpoint.

Executed inside the mlx-lm virtualenv (``~/.cache/h1-distributed/venv``), which has
``mlx_lm`` with native Falcon-H1 support but none of ``hghost``; it imports nothing else
from the package. Reads the prompt list, samples ``max_tokens`` new tokens per prompt with
``mx.random.seed(base_seed + index)``, and writes one JSON record per prompt. The records
carry no checkpoint identity so the file can be rated blind.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--prompts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--repetition-penalty", type=float, default=1.08)
    parser.add_argument("--seed", type=int, help="override the prompt file's base seed")
    parser.add_argument(
        "--dtype",
        choices=("float32", "bfloat16", "float16"),
        default="float32",
        help="cast every checkpoint to this dtype so BF16 and FP32 files sample alike",
    )
    return parser


def config_repairs(config: dict) -> dict:
    """Config values written by h1jax that strict Falcon-H1 config classes reject.

    ``h1jax.checkpoint.write_hf_config`` stores ``mamba_expand`` as the float ratio
    ``mamba_d_ssm / hidden_size`` (1.5 for H1-Tiny). mlx-lm's ``ModelArgs`` and the
    Transformers config consulted by ``AutoTokenizer`` both declare it ``int``; the SSM
    is sized from ``mamba_d_ssm`` anyway, so only the type needs fixing.
    """
    repairs: dict = {}
    expand = config.get("mamba_expand")
    if isinstance(expand, float):
        repairs["mamba_expand"] = max(1, round(expand))
    return repairs


def weight_dtypes(checkpoint: Path) -> set[str]:
    import mlx.core as mx

    return {
        str(value.dtype).removeprefix("mlx.core.")
        for path in checkpoint.glob("*.safetensors")
        for value in mx.load(str(path)).values()
    }


@contextmanager
def loadable_checkpoint(checkpoint: Path, dtype: str) -> Iterator[tuple[Path, dict]]:
    """Yield a directory mlx-lm can load with weights already in ``dtype``.

    That is the checkpoint itself when nothing needs changing, otherwise a staged copy:
    ``config.json`` with the repairs from :func:`config_repairs`, weights converted to
    ``dtype`` (mlx-lm folds Falcon-H1's multipliers into the weights at load time in the
    stored dtype, so a BF16 file and its exact FP32 upcast would otherwise sample
    differently), and everything else symlinked.
    """
    import mlx.core as mx

    config = json.loads((checkpoint / "config.json").read_text(encoding="utf-8"))
    repairs = config_repairs(config)
    convert = weight_dtypes(checkpoint) != {dtype}
    if not repairs and not convert:
        yield checkpoint, repairs
        return
    with tempfile.TemporaryDirectory(prefix="evalpack-mlx-") as temporary:
        staged = Path(temporary) / checkpoint.name
        staged.mkdir()
        for entry in checkpoint.iterdir():
            if entry.name == "config.json" or entry.name.startswith("optimizer"):
                continue
            if convert and entry.suffix == ".safetensors":
                weights = mx.load(str(entry))
                mx.save_safetensors(
                    str(staged / entry.name),
                    {
                        name: value.astype(getattr(mx, dtype))
                        for name, value in weights.items()
                    },
                    metadata={"format": "pt"},
                )
            else:
                os.symlink(entry, staged / entry.name)
        (staged / "config.json").write_text(
            json.dumps({**config, **repairs}, indent=2) + "\n", encoding="utf-8"
        )
        yield staged, {**repairs, **({"weights": dtype} if convert else {})}


def load_prompts(path: Path) -> tuple[int, list[dict]]:
    values = json.loads(path.read_text(encoding="utf-8"))
    return int(values["base_seed"]), list(values["prompts"])


def main() -> None:
    args = build_parser().parse_args()
    import mlx.core as mx
    import mlx_lm
    from mlx_lm import load
    from mlx_lm.sample_utils import make_logits_processors, make_sampler

    stream_generate = sys.modules["mlx_lm.generate"].stream_generate
    base_seed, prompts = load_prompts(args.prompts)
    if args.seed is not None:
        base_seed = args.seed
    started = time.perf_counter()
    with loadable_checkpoint(args.checkpoint.resolve(), args.dtype) as (
        loadable,
        repairs,
    ):
        model, tokenizer = load(str(loadable))
    sampler = make_sampler(temp=args.temperature, top_p=args.top_p)
    processors = make_logits_processors(repetition_penalty=args.repetition_penalty)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as sink:
        for index, prompt in enumerate(prompts):
            seed = base_seed + index
            mx.random.seed(seed)
            prompt_tokens = tokenizer.encode(prompt["text"])
            tokens: list[int] = []
            pieces: list[str] = []
            finish_reason = "length"
            for response in stream_generate(
                model,
                tokenizer,
                prompt_tokens,
                max_tokens=args.max_tokens,
                sampler=sampler,
                logits_processors=processors,
            ):
                tokens.append(int(response.token))
                pieces.append(response.text)
                if response.finish_reason:
                    finish_reason = response.finish_reason
            record = {
                "prompt_id": prompt["id"],
                "kind": prompt.get("kind", ""),
                "prompt": prompt["text"],
                "seed": seed,
                "prompt_tokens": [int(token) for token in prompt_tokens],
                "tokens": tokens,
                "completion": "".join(pieces),
                "finish_reason": finish_reason,
            }
            sink.write(json.dumps(record, ensure_ascii=False) + "\n")
            sink.flush()
            print(
                f"[evalpack-mlx] {index + 1}/{len(prompts)} {prompt['id']}: {len(tokens)} tokens",
                file=sys.stderr,
                flush=True,
            )
    meta = {
        "checkpoint": str(args.checkpoint.resolve()),
        "prompts": len(prompts),
        "base_seed": base_seed,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "repetition_penalty": args.repetition_penalty,
        "config_repairs": repairs,
        "dtype": args.dtype,
        "mlx_lm_version": mlx_lm.__version__,
        "mlx_version": mx.__version__,
        "python": platform.python_version(),
        "seconds": round(time.perf_counter() - started, 3),
    }
    args.output.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
