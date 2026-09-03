#!/bin/sh
# The room's services, declared once. usage: chapterx/services.sh start|status|check|restart <name>|watch
#   start    start every service that is not running
#   status   one line per service
#   check    liveness (a real completion through each model server and the proxy; HTTP on the explorer); exit 1 if any fails
#   watch    loop: check every 5 minutes, restart what died, append alarms to /tmp/hghost-services.log
# Services: name | tmux session | port | start command (run from the repo root). Model names are the serving symlinks.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
MLX="$HOME/.cache/h1-distributed/venv/bin/python"
RESIDENT_CK="$(readlink artifacts/serving/h-05b-room-e2v4 2>/dev/null || echo artifacts/checkpoints/tpu/h-ghost-h1jax-room05b-e2-v4/room05b-e2-v4-decay10/tokens-000794693880)"
services() {
  cat <<TABLE
resident|hghost-serve|8124|$MLX -m mlx_lm.server --model h-05b-replay --host 127.0.0.1 --port 8124
preview|hghost-serve05b|8125|$MLX -m mlx_lm.server --model h-05b-blend090 --host 127.0.0.1 --port 8125
base15b|hghost-serve15b|8127|$MLX -m mlx_lm.server --model h1-15b-deep-base --host 127.0.0.1 --port 8127
qwen27b|hghost-serve27b|8128|$MLX -m mlx_lm.server --model qwen38-27b-4bit --host 127.0.0.1 --port 8128
proxy|hghost-proxy|8126|/usr/bin/python3 $ROOT/chapterx/room_proxy.py --port 8126 --upstream http://127.0.0.1:8124 --candidates 4
explorer|hexplorer|8130|python3 $ROOT/explorer/serve.py --port 8130
bot|hghost-chapterx|-|sh $ROOT/chapterx/run-h-bot.sh
TABLE
}
listening() { lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1; }
start_one() { # name session port cmd
  case "$1" in
    bot) tmux kill-session -t "$2" 2>/dev/null; sh chapterx/run-h-bot.sh >/dev/null 2>&1 ;;
    *) tmux kill-session -t "$2" 2>/dev/null; tmux new-session -d -s "$2" -c "$ROOT/artifacts/serving" "$4 >> /tmp/hghost-$1.log 2>&1" ;;
  esac
}
complete_ok() { # port model
  curl -s -m 240 "http://127.0.0.1:$1/v1/completions" -H 'Content-Type: application/json' \
    -d "{\"model\":\"$2\",\"prompt\":\"A room in the library, late.\\n\\nember: hi h\\n\\nh:\",\"max_tokens\":4,\"temperature\":0.7,\"stop\":[\"\\n\\n\"]}" \
    | grep -q '"text"'
}
check_one() { # name port
  case "$1" in
    resident) complete_ok 8124 h-05b-replay ;;
    preview) complete_ok 8125 h-05b-blend090 ;;
    base15b) complete_ok 8127 h1-15b-deep-base ;;
    qwen27b) complete_ok 8128 qwen38-27b-4bit ;;
    proxy) complete_ok 8126 h-05b-replay ;;
    explorer) curl -s -m 20 http://127.0.0.1:8130/api/version | grep -q explorer ;;
    bot) tmux has-session -t hghost-chapterx 2>/dev/null && pgrep -f "chapterx/(dist|src)|chapterx.*node|node.*chapterx" >/dev/null 2>&1 && ! tail -20 ~/dev/chapterx/logs/h-bot.log 2>/dev/null | grep -q "ECONNREFUSED\|Disconnected" ;;
  esac
}
cmd="${1:-status}"
case "$cmd" in
  status) services | while IFS='|' read -r name sess port run; do
      if [ "$port" = "-" ]; then st=$(tmux has-session -t "$sess" 2>/dev/null && echo up || echo DOWN); else st=$(listening "$port" && echo up || echo DOWN); fi
      printf "%-9s %-16s %-5s %s\n" "$name" "$sess" "$port" "$st"; done ;;
  start) services | while IFS='|' read -r name sess port run; do
      if [ "$port" = "-" ]; then tmux has-session -t "$sess" 2>/dev/null && continue; else listening "$port" && continue; fi
      echo "starting $name"; start_one "$name" "$sess" "$port" "$run"; done ;;
  restart) services | while IFS='|' read -r name sess port run; do [ "$name" = "$2" ] && { echo "restarting $name"; start_one "$name" "$sess" "$port" "$run"; }; done ;;
  check) fail=0; services | while IFS='|' read -r name sess port run; do
      if check_one "$name" "$port"; then echo "ok    $name"; else echo "FAIL  $name"; echo fail > /tmp/hghost-check-fail; fi; done
      [ -f /tmp/hghost-check-fail ] && { rm -f /tmp/hghost-check-fail; exit 1; }; exit 0 ;;
  watch) while true; do
      services | while IFS='|' read -r name sess port run; do
        if ! check_one "$name" "$port"; then echo "$(date '+%F %T') ALARM $name failed liveness; restarting" >> /tmp/hghost-services.log; start_one "$name" "$sess" "$port" "$run"; fi
      done; sleep 300; done ;;
  *) echo "usage: $0 start|status|check|restart <name>|watch"; exit 2 ;;
esac
