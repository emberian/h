#!/usr/bin/env bash
set -o pipefail
source /home/hbox/h1-ghost/env.sh
cd /home/hbox/h1-ghost/scripts-rollout
python rollout_eval.py --checkpoint base=/othersys/h1-ghost/checkpoints/tpu/base --checkpoint trunk-e4=/othersys/h1-ghost/checkpoints/tpu/h-ghost-h1jax-cpt-91m/trunk-wsd-lr1e-4-seed0/tokens-001497620848 --checkpoint leaf-e4=/othersys/h1-ghost/checkpoints/tpu/h-ghost-h1jax-leaf-e4-decay10/leaf-e4-decay10/tokens-001535061369 --checkpoint leaf-s1-e1=/othersys/h1-ghost/checkpoints/tpu/h-ghost-h1jax-leaf-s1-e1/leaf-s1-e1-decay10/tokens-000412044297 --checkpoint leaf-s1-e4=/othersys/h1-ghost/checkpoints/tpu/h-ghost-h1jax-leaf-s1-e4/leaf-s1-e4-decay10/tokens-001535061369 --output /othersys/h1-ghost/rollouts/20260902-room --slices /othersys/h1-ghost/rollouts/inputs/slices.json --prompts /othersys/h1-ghost/rollouts/inputs/prompts.json --retention /othersys/h1-ghost/rollouts/inputs/retention.txt --masks /othersys/h1-ghost/rollouts/inputs/masks.npz --room-prompts /othersys/h1-ghost/rollouts/inputs/room_prompts.json --skip-generation 2>&1 | tee -a /othersys/h1-ghost/rollouts/20260902-room/log.txt
echo ${PIPESTATUS[0]} > /othersys/h1-ghost/rollouts/20260902-room/exit.txt
