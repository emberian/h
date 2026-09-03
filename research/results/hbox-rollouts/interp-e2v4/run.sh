#!/usr/bin/env bash
set -o pipefail
source /home/hbox/h1-ghost/env.sh
cd /home/hbox/h1-ghost/scripts-rollout
python rollout_eval.py --checkpoint interp025=/othersys/h1-ghost/checkpoints/tpu/extra/interp025 --checkpoint interp050=/othersys/h1-ghost/checkpoints/tpu/extra/interp050 --checkpoint interp075=/othersys/h1-ghost/checkpoints/tpu/extra/interp075 --output /othersys/h1-ghost/rollouts/interp-e2v4 --slices /othersys/h1-ghost/rollouts/inputs/slices.json --prompts /othersys/h1-ghost/rollouts/inputs/prompts.json --retention /othersys/h1-ghost/rollouts/inputs/retention.txt --masks /othersys/h1-ghost/rollouts/inputs/masks.npz --room-validation /othersys/h1-ghost/rollouts/inputs/room-validation.bin --room-validation-sequences 512 --skip-generation 2>&1 | tee -a /othersys/h1-ghost/rollouts/interp-e2v4/log.txt
echo ${PIPESTATUS[0]} > /othersys/h1-ghost/rollouts/interp-e2v4/exit.txt
