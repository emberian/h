#!/bin/sh
# Generate the room-run kernel: continue the seed-0 epoch-4 trunk for one epoch of the room-mixed stream
# (corpus-v1.2-room), then cool over its last 10%. Checkpoints at the pre-cooldown point and the end.
#
# usage: research/roommix/make_room_kernel.sh <stream-train-tokens> [dataset-id] [name]
set -eu
STREAM="$1"
DATASET="${2:-emberian64/hghost-curated-tokens-v1-2-room}"
NAME="${3:-room-e5}"
BRANCH_TOKENS=1497620848
DECAY=$((STREAM / 10))
TOTAL=$((BRANCH_TOKENS + STREAM))
PRE=$((TOTAL - DECAY))
python3 kaggle/make_leaf_kernel.py \
  --name "$NAME" \
  --set RUN_NAME="$NAME-decay10" \
  --set SSD=v2 \
  --set BRANCH_FROM='/kaggle/input/**/trunk-wsd-lr1e-4-seed0/tokens-001497620848/trainer_state.json' \
  --set TOTAL_TOKENS="$TOTAL" --set DECAY_TOKENS="$DECAY" --set SAVE_TOKENS="$PRE" \
  --set MAX_MINUTES=80 --set EXTRA_VALIDATION=room-validation.bin \
  --kernel-source emberian64/h-ghost-h1jax-cpt-91m \
  --dataset-source emberian64/hghost-jax-code-public \
  --dataset-source emberian64/hghost-falcon-h1-90m-base-public \
  --dataset-source "$DATASET"
DIR="kaggle/tpu_h1jax_$(echo "$NAME" | tr '-' '_')"
# The room stream is private on Kaggle (detokenizable text), so the kernel must be private too.
python3 - "$DIR/kernel-metadata.json" <<'PY'
import json, sys
p = sys.argv[1]; m = json.load(open(p)); m["is_private"] = True
json.dump(m, open(p, "w"), indent=2); print("private kernel:", m["id"], m["dataset_sources"], m["kernel_sources"])
PY
echo "stream=$STREAM total=$TOTAL decay=$DECAY pre-cooldown save=$PRE -> $DIR"
