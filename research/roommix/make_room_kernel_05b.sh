#!/bin/sh
# Generate the 0.5B room run: Falcon-H1-0.5B-Base, one epoch of the room-mixed stream (corpus-v1.2-room)
# straight from the base checkpoint, WSD with the last 10% cooled, uncooled checkpoints at quarter points,
# room loss reported beside library loss.
#
# usage: [SAVES=t1,t2] research/roommix/make_room_kernel_05b.sh <stream-train-tokens> <per-chip-batch> [lr] [dataset-id] [name]
# Default saves: the pre-cooldown checkpoint only (plus the final one); a 0.5B checkpoint with optimizer state is
# ~6.3 GB and Kaggle caps kernel output at 20 GB.
set -eu
STREAM="$1"; PER_CHIP="$2"; LR="${3:-5e-5}"
DATASET="${4:-emberian64/hghost-curated-tokens-v1-2-room}"
NAME="${5:-room05b-e1}"
DECAY=$((STREAM / 10)); PRE=$((STREAM - DECAY))
Q1=$((STREAM / 4)); Q2=$((STREAM / 2)); Q3=$((3 * STREAM / 4))
python3 kaggle/make_leaf_kernel.py \
  --name "$NAME" \
  --set RUN_NAME="$NAME-decay10" \
  --set SSD=v2 --set PER_CHIP="$PER_CHIP" --set LR="$LR" \
  --set BRANCH_FROM= \
  --set TOTAL_TOKENS="$STREAM" --set DECAY_TOKENS="$DECAY" \
  --set SAVE_TOKENS="${SAVES:-$PRE}" \
  --set MAX_MINUTES=300 --set EXTRA_VALIDATION=room-validation.bin \
  --dataset-source emberian64/hghost-jax-code-public \
  --dataset-source emberian64/hghost-falcon-h1-0-5b-base-public \
  --dataset-source "$DATASET"
DIR="kaggle/tpu_h1jax_$(echo "$NAME" | tr '-' '_')"
python3 - "$DIR/kernel-metadata.json" <<'PY'
import json, sys
p = sys.argv[1]; m = json.load(open(p)); m["is_private"] = True; m["kernel_sources"] = []
json.dump(m, open(p, "w"), indent=2); print("private kernel:", m["id"], m["dataset_sources"])
PY
echo "stream=$STREAM per_chip=$PER_CHIP lr=$LR decay=$DECAY saves=$Q1,$Q2,$Q3,$PRE -> $DIR"
