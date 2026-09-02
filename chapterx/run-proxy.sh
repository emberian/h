#!/bin/sh
# Reply filter between ChapterX (:8126) and mlx_lm.server (:8124), in tmux. See chapterx/room_proxy.py.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
tmux kill-session -t hghost-proxy 2>/dev/null || true
tmux new-session -d -s hghost-proxy "/usr/bin/python3 $ROOT/chapterx/room_proxy.py --port 8126 --upstream http://127.0.0.1:8124 --candidates 4 >> /tmp/hghost-proxy-8126.log 2>&1"
sleep 1; lsof -nP -iTCP:8126 -sTCP:LISTEN >/dev/null && echo "room proxy on :8126 (tmux hghost-proxy, log /tmp/hghost-proxy-8126.log)"
