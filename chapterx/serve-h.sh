#!/bin/sh
# Serve a Falcon-H1 HF checkpoint directory as an OpenAI-compatible /v1/completions endpoint via mlx-lm,
# under a model NAME that ChapterX can route to, inside tmux so it outlives the shell that launched it.
#
# mlx_lm.server resolves the request's "model" field as a path relative to its working directory (or a Hub
# repo), so the checkpoint is exposed through a symlink artifacts/serving/<name> and the server runs there.
set -eu
MODEL="${1:?usage: serve-h.sh <hf checkpoint dir> [name] [port]}"
NAME="${2:-h-corpus-v1-cpt}"
PORT="${3:-8124}"
VENV="${HGHOST_MLX_VENV:-$HOME/.cache/h1-distributed/venv}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVING="$ROOT/artifacts/serving"
LOG="${HGHOST_SERVE_LOG:-/tmp/hghost-serve-$PORT.log}"
mkdir -p "$SERVING"
ln -sfn "$(cd "$MODEL" && pwd)" "$SERVING/$NAME"
tmux kill-session -t hghost-serve 2>/dev/null || true
tmux new-session -d -s hghost-serve -c "$SERVING" \
  "$VENV/bin/python -m mlx_lm.server --model '$NAME' --host 127.0.0.1 --port $PORT >> '$LOG' 2>&1"
for _ in $(seq 1 90); do
  if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "serving $NAME -> $(readlink "$SERVING/$NAME") on http://127.0.0.1:$PORT/v1 (tmux hghost-serve, log $LOG)"
    echo "request model field: $NAME"
    exit 0
  fi
  sleep 1
done
echo "server did not start; see $LOG" >&2
exit 1
