#!/bin/sh
# Evaluate a finished 0.5B arm end to end: harvest, hbox slices + room pass + judge (after_run.sh), then serve
# the cooled checkpoint on :8125 and measure echo rate / context lift on the room evaluation bank.
# usage: research/roommix/after_arm.sh <downloaded-kernel-dir> <run-name> <served-name>
set -eu
cd /Users/ember/dev/h
DL="$1"; RUN_NAME="$2"; NAME="$3"; KERNEL=$(basename "$DL")
sh research/roommix/after_run.sh "$DL" "$RUN_NAME"
RUN=artifacts/checkpoints/tpu/$KERNEL/$RUN_NAME
FINAL=$(ls -d $RUN/tokens-* | sort | tail -1)
ln -sfn "$(cd "$FINAL" && pwd)" artifacts/serving/$NAME
tmux kill-session -t hghost-serve05b 2>/dev/null || true
tmux new-session -d -s hghost-serve05b -c "$PWD/artifacts/serving" "$HOME/.cache/h1-distributed/venv/bin/python -m mlx_lm.server --model $NAME --host 127.0.0.1 --port 8125 >> /tmp/hghost-serve-8125.log 2>&1"
for i in $(seq 1 120); do lsof -nP -iTCP:8125 -sTCP:LISTEN >/dev/null 2>&1 && break; sleep 1; done
mkdir -p research/results/$NAME
.venv/bin/python research/roommix/read_room.py "$NAME" 8125 research/results/$NAME/mac-room-replies.jsonl 5 | tail -3
.venv/bin/hghost-roombank sample --model "$NAME" --port 8125 --samples 4 2>&1 | tail -2
.venv/bin/hghost-roombank lift --model "$NAME" --evaluator 91m 2>&1 | tail -4
.venv/bin/hghost-roombank lift --model "$NAME" --evaluator 05b --batch 4 2>&1 | tail -4
