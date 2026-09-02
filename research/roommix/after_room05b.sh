#!/bin/sh
# After the 0.5B room run lands: harvest, evaluate on hbox (room pass + loss slices), judge, and push the
# Kaggle GPU evaluation. Run from /Users/ember/dev/h.
#
# usage: research/roommix/after_room05b.sh <downloaded-kernel-dir>   (e.g. scratchpad/tpu-queue/h-ghost-h1jax-room05b-e1)
set -eu
DL="$1"
.venv/bin/python kaggle/harvest_kernel.py "$DL" --delete-scratch
RUN=artifacts/checkpoints/tpu/h-ghost-h1jax-room05b-e1/room05b-e1-decay10
FINAL=$(ls -d $RUN/tokens-* | sort | tail -1)
PRE=$(ls -d $RUN/tokens-* | sort | head -1)
echo "final=$FINAL pre=$PRE"
python3 - "$RUN/events.jsonl" <<'PY'
import json,sys
ev=[json.loads(l) for l in open(sys.argv[1])]
vals=[e for e in ev if e["event"]=="validation"]
print("| tokens | library loss | fixed-32 | room loss |"); print("|---:|---:|---:|---:|")
for v in vals: print(f"| {v['tokens']:,} | {v['loss']:.4f} | {v['fixed_loss']:.4f} | {v.get('extra_loss', float('nan')):.4f} |")
PY
# hbox: room pass + loss slices for the final (cooled) checkpoint, against the 91M leaf and the 0.5B base
hbox_training/run_rollout_eval.sh all --run room05b --room --skip-generation \
  --checkpoint room05b-final="$(cd "$FINAL" && pwd)" \
  --checkpoint base05b="$(cd artifacts/kaggle/base_model_05b && pwd)"
# judge: library-likeness of the room replies
PYTHONPATH=jax_training .venv-jax/bin/python research/eval/judge.py --base kaggle/base_model_dataset_public \
  --model artifacts/checkpoints/tpu/h-ghost-h1jax-leaf-s1-e4/leaf-s1-e4-decay10/tokens-001535061369 \
  --texts research/results/hbox-rollouts/room05b/room-room05b-final.jsonl --field text --max-tokens 96 \
  --output research/results/hbox-rollouts/room05b/judge-room05b-final.jsonl | tail -3
