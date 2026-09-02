#!/usr/bin/env bash
set -o pipefail
source /home/hbox/h1-ghost/env.sh
cd /home/hbox/h1-ghost/scripts-rollout
python rollout_eval.py --checkpoint room05b-final=/othersys/h1-ghost/checkpoints/tpu/extra/room05b-final --checkpoint base05b=/othersys/h1-ghost/checkpoints/tpu/extra/base05b --output /othersys/h1-ghost/rollouts/room05b --slices /othersys/h1-ghost/rollouts/inputs/slices.json --prompts /othersys/h1-ghost/rollouts/inputs/prompts.json --retention /othersys/h1-ghost/rollouts/inputs/retention.txt --masks /othersys/h1-ghost/rollouts/inputs/masks.npz --room-prompts /othersys/h1-ghost/rollouts/inputs/room_prompts.json --skip-generation 2>&1 | tee -a /othersys/h1-ghost/rollouts/room05b/log.txt
echo ${PIPESTATUS[0]} > /othersys/h1-ghost/rollouts/room05b/exit.txt
