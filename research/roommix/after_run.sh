#!/bin/sh
# After a 0.5B room run lands: harvest, hbox loss slices + room pass (final checkpoint vs the 0.5B base),
# judge on the hbox room replies. usage: research/roommix/after_run.sh <downloaded-kernel-dir> <run-name>
#   e.g. after_run.sh scratchpad/tpu-queue/h-ghost-h1jax-room05b-e2 room05b-e2-decay10
set -eu
DL="$1"; RUN_NAME="$2"; KERNEL=$(basename "$DL")
.venv/bin/python kaggle/harvest_kernel.py "$DL" --delete-scratch
RUN=artifacts/checkpoints/tpu/$KERNEL/$RUN_NAME
FINAL=$(ls -d $RUN/tokens-* | sort | tail -1)
echo "final=$FINAL"
python3 - "$RUN/events.jsonl" <<'PY'
import json,sys
ev=[json.loads(l) for l in open(sys.argv[1])]
vals=[e for e in ev if e["event"]=="validation"]
print("| tokens | library loss | fixed-32 | room loss |"); print("|---:|---:|---:|---:|")
for v in vals: print(f"| {v['tokens']:,} | {v['loss']:.4f} | {v['fixed_loss']:.4f} | {v.get('extra_loss', float('nan')):.4f} |")
PY
TAG=$(echo "$RUN_NAME" | sed 's/-decay10$//')
hbox_training/run_rollout_eval.sh all --run "$TAG" --room --skip-generation \
  --checkpoint "$TAG-final=$(cd "$FINAL" && pwd)" \
  --checkpoint base05b="$(cd artifacts/kaggle/base_model_05b && pwd)"
PYTHONPATH=jax_training .venv-jax/bin/python research/eval/judge.py --base kaggle/base_model_dataset_public \
  --model artifacts/checkpoints/tpu/h-ghost-h1jax-leaf-s1-e4/leaf-s1-e4-decay10/tokens-001535061369 \
  --texts "research/results/hbox-rollouts/$TAG/room-$TAG-final.jsonl" --field text --max-tokens 96 \
  --output "research/results/hbox-rollouts/$TAG/judge-$TAG-final.jsonl" | tail -2
