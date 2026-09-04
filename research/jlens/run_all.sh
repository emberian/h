#!/bin/zsh
# Sequential lens chain (concurrent runs starved each other and filled swap).
# 91M pair: 72 validation windows (64-128 tokens) + 12 full room prompts, layers 12/8/16, cotangent chunk 128.
# 0.5B pair: 28 windows of 64 tokens + 8 room prompts truncated to their last 96 tokens, layer 18, chunk 128.
cd /Users/ember/dev/h
export PYTHONPATH=jax_training JAX_PLATFORM_NAME=cpu H1JAX_SSD=v2
for m in 90m-base 91m-leaf; do
  .venv-jax/bin/python -u research/jlens/jlens.py lens --model $m --layers 12 8 16 --n 72 --chunk 128 \
    > research/jlens/out/lens-$m.log 2>&1
done
echo done > research/jlens/out/lens-91m.done
for m in 05b-base 05b-e2v4; do
  .venv-jax/bin/python -u research/jlens/jlens.py lens --model $m --layers 18 --n 28 --chunk 128 \
    --min-len 64 --max-len 64 --room-idx 0 1 3 4 6 8 9 11 --room-last 96 > research/jlens/out/lens-$m.log 2>&1
done
echo done > research/jlens/out/lens-05b.done
