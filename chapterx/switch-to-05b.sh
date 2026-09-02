#!/bin/sh
# Put the cooled 0.5B room checkpoint into the private Discord server: serve it on :8124 under the name the
# bot config routes to, install the 0.5B bot config (bare frame, stop at the blank line), restart the bot.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CK="${1:-$ROOT/artifacts/checkpoints/tpu/h-ghost-h1jax-room05b-e1/room05b-e1-decay10/tokens-000417533162}"
tmux kill-session -t hghost-serve05b 2>/dev/null || true   # the :8125 preview server
sh "$ROOT/chapterx/serve-h.sh" "$CK" h-05b-room-e1 8124
cp "$HOME/dev/chapterx/config/bots/h.yaml" "$HOME/dev/chapterx/config/bots/h.yaml.pre-05b"
cp "$ROOT/chapterx/h.bot.05b.yaml" "$HOME/dev/chapterx/config/bots/h.yaml"
tmux kill-session -t hghost-chapterx 2>/dev/null || true
sh "$ROOT/chapterx/run-h-bot.sh"
sleep 12; tail -5 "$HOME/dev/chapterx/logs/h-bot.log" | grep -o "Discord client ready\|ERROR.*" | tail -1
echo "h is now the 0.5B room checkpoint ($CK); previous bot config saved as h.yaml.pre-05b"
