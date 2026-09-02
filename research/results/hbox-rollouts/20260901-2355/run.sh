#!/usr/bin/env bash
set -o pipefail
source /home/hbox/h1-ghost/env.sh
cd /home/hbox/h1-ghost/scripts-rollout
python rollout_eval.py --checkpoint base=/othersys/h1-ghost/checkpoints/tpu/base --checkpoint trunk-e1=/othersys/h1-ghost/checkpoints/tpu/h-ghost-h1jax-cpt-91m/trunk-wsd-lr1e-4-seed0/tokens-000374603776 --checkpoint leaf-e1=/othersys/h1-ghost/checkpoints/tpu/h-ghost-h1jax-leaf-e1-decay10/leaf-e1-decay10/tokens-000412044297 --checkpoint trunk-e4=/othersys/h1-ghost/checkpoints/tpu/h-ghost-h1jax-cpt-91m/trunk-wsd-lr1e-4-seed0/tokens-001497620848 --checkpoint leaf-e4=/othersys/h1-ghost/checkpoints/tpu/h-ghost-h1jax-leaf-e4-decay10/leaf-e4-decay10/tokens-001535061369 --output /othersys/h1-ghost/rollouts/20260901-2355 --slices /othersys/h1-ghost/rollouts/inputs/slices.json --prompts /othersys/h1-ghost/rollouts/inputs/prompts.json --retention /othersys/h1-ghost/rollouts/inputs/retention.txt --masks /othersys/h1-ghost/rollouts/inputs/masks.npz 2>&1 | tee -a /othersys/h1-ghost/rollouts/20260901-2355/log.txt
echo ${PIPESTATUS[0]} > /othersys/h1-ghost/rollouts/20260901-2355/exit.txt
