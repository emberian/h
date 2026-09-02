#!/bin/sh
# Serve a Falcon-H1 HF checkpoint directory as an OpenAI-compatible /v1/completions endpoint via mlx-lm,
# inside a tmux session so it outlives the shell that launched it.
set -eu
MODEL="${1:?usage: serve-h.sh <hf checkpoint dir> [port]}"
PORT="${2:-8124}"
VENV="${HGHOST_MLX_VENV:-$HOME/.cache/h1-distributed/venv}"
LOG="${HGHOST_SERVE_LOG:-/tmp/hghost-serve-$PORT.log}"
tmux kill-session -t hghost-serve 2>/dev/null || true
tmux new-session -d -s hghost-serve \
  "$VENV/bin/python -m mlx_lm.server --model '$MODEL' --host 127.0.0.1 --port $PORT >> '$LOG' 2>&1"
for _ in $(seq 1 60); do
  if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "serving $MODEL on http://127.0.0.1:$PORT/v1 (tmux hghost-serve, log $LOG)"
    echo "request model field must be exactly: $MODEL"
    exit 0
  fi
  sleep 1
done
echo "server did not start; see $LOG" >&2
exit 1
