#!/bin/sh
# Start the h resident in ChapterX (local dev layout with BOT_NAME=h) inside tmux.
# Needs: ~/dev/chapterx/config/bots/h.yaml (installed), config/shared.yaml with the openaicompletion-h vendor
# (installed), the h checkpoint served on 127.0.0.1:8124 (chapterx/serve-h.sh), and the Discord bot token at
# ~/dev/chapterx/config/bots/h_discord_token (create the bot at https://discord.com/developers, enable the
# Message Content intent, invite it with Send Messages + Read Message History; the Discord username can be
# anything, BOT_NAME selects the config).
set -eu
CX="${CHAPTERX_DIR:-$HOME/dev/chapterx}"
TOKEN="$CX/config/bots/h_discord_token"
[ -s "$TOKEN" ] || { echo "missing Discord token file: $TOKEN" >&2; exit 1; }
lsof -nP -iTCP:8124 -sTCP:LISTEN >/dev/null 2>&1 || { echo "nothing serving on 127.0.0.1:8124; run chapterx/serve-h.sh first" >&2; exit 1; }
tmux kill-session -t hghost-chapterx 2>/dev/null || true
mkdir -p "$CX/logs"
tmux new-session -d -s hghost-chapterx -c "$CX" \
  "BOT_NAME=h CACHE_PATH=./cache_h LOG_LEVEL=info npm run dev >> logs/h-bot.log 2>&1"
echo "h resident starting in tmux hghost-chapterx; log: $CX/logs/h-bot.log"
