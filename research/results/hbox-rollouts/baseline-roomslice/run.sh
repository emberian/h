#!/usr/bin/env bash
set -o pipefail
source /home/hbox/h1-ghost/env.sh
cd /home/hbox/h1-ghost/scripts-rollout
python rollout_eval.py --checkpoint room05b-e2-v3-final=/othersys/h1-ghost/checkpoints/tpu/extra/room05b-e2-v3-final --checkpoint room05b-e2-final=/othersys/h1-ghost/checkpoints/tpu/extra/room05b-e2-final --output /othersys/h1-ghost/rollouts/baseline-roomslice --slices /othersys/h1-ghost/rollouts/inputs/slices.json --prompts /othersys/h1-ghost/rollouts/inputs/prompts.json --retention /othersys/h1-ghost/rollouts/inputs/retention.txt --masks /othersys/h1-ghost/rollouts/inputs/masks.npz --room-validation /othersys/h1-ghost/rollouts/inputs/room-validation.bin --room-validation-sequences 512 --skip-generation 2>&1 | tee -a /othersys/h1-ghost/rollouts/baseline-roomslice/log.txt
echo ${PIPESTATUS[0]} > /othersys/h1-ghost/rollouts/baseline-roomslice/exit.txt
