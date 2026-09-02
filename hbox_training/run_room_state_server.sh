#!/usr/bin/env bash
# Mac-side driver for hbox_training/room_state_server.py: sync the server to hbox, launch it
# inside the private tmux server (`tmux -L hghost`, session `hghost-room`), open an ssh port
# forward, and run the smoke walk from the Mac through it.
#
#   hbox_training/run_room_state_server.sh [all|sync|launch|forward|wait|smoke|selftest|status|logs|stop] [options]
#
#   --checkpoint DIR      checkpoint directory ON HBOX (default: the room05b-e2-v3-final 0.5B)
#   --port N              port on hbox (default 8140); --local-port N on the Mac (default: same)
#   --read-mode chunk|step, --state-dtype float32|bfloat16, --room ID, --seed N, --n N
#   --force-launch        ignore the GPU-busy preflight
#   --keep                `all` without stopping the server and the forward afterwards
#
# `all` = sync + launch + forward + wait + smoke. The smoke report lands under
# research/results/room-state-server/. The server keeps rooms in memory; persisted snapshots
# go to /othersys/h1-ghost/rooms/<room>/ on hbox. Never touches rollout_eval's session.
set -euo pipefail

HBOX=${HBOX:-hbox}
SESSION=hghost-room
TMUX="tmux -L hghost"
ROOT=$(cd "$(dirname "$0")/.." && pwd)
PYTHON="$ROOT/.venv/bin/python"
LOCAL_RESULTS="$ROOT/research/results/room-state-server"
REMOTE_BIN=/home/hbox/h1-ghost/scripts-room
REMOTE_STATE=/othersys/h1-ghost/rooms
REMOTE_LOG=$REMOTE_STATE/server.log
DEFAULT_CHECKPOINT=/othersys/h1-ghost/checkpoints/tpu/extra/room05b-e2-v3-final

command=all
CHECKPOINT=$DEFAULT_CHECKPOINT
PORT=8140
LOCAL_PORT=""
SERVER_ARGS=()
SMOKE_ARGS=()
FORCE_LAUNCH=0
KEEP=0
while [ $# -gt 0 ]; do
  case "$1" in
    all|sync|launch|forward|wait|smoke|selftest|status|logs|stop) command=$1 ;;
    --checkpoint) CHECKPOINT=$2; shift ;;
    --port) PORT=$2; shift ;;
    --local-port) LOCAL_PORT=$2; shift ;;
    --read-mode|--state-dtype) SERVER_ARGS+=("$1" "$2"); shift ;;
    --room|--seed|--n) SMOKE_ARGS+=("$1" "$2"); shift ;;
    --force-launch) FORCE_LAUNCH=1 ;;
    --keep) KEEP=1 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done
[ -n "$LOCAL_PORT" ] || LOCAL_PORT=$PORT
URL="http://127.0.0.1:$LOCAL_PORT"
STAMP=$(date +%Y%m%d-%H%M%S)

remote() { ssh -o BatchMode=yes "$HBOX" "$@"; }

do_sync() {
  echo "== sync room_state_server.py -> $HBOX:$REMOTE_BIN/"
  remote "mkdir -p $REMOTE_BIN $REMOTE_STATE"
  rsync -a "$ROOT/hbox_training/room_state_server.py" "$HBOX:$REMOTE_BIN/"
  remote "test -f $CHECKPOINT/config.json" || { echo "no config.json in $HBOX:$CHECKPOINT" >&2; exit 1; }
}

preflight() {
  echo "== hbox preflight"
  remote 'uptime; free -g | sed -n 2p; echo "gpu busy: $(cat /sys/class/drm/card*/device/gpu_busy_percent 2>/dev/null | head -1)%"'
  if remote "$TMUX has-session -t $SESSION 2>/dev/null"; then
    echo "tmux session $SESSION already exists on hbox ($0 status / stop)" >&2
    exit 1
  fi
  local busy
  busy=$(remote 'cat /sys/class/drm/card*/device/gpu_busy_percent 2>/dev/null | head -1')
  if [ "${busy:-0}" -gt 50 ]; then
    echo "hbox GPU is busy (${busy}%); pass --force-launch to run anyway" >&2
    [ "$FORCE_LAUNCH" = 1 ] || exit 1
  fi
}

do_launch() {
  preflight
  local args="serve --checkpoint $CHECKPOINT --port $PORT --snapshot-dir $REMOTE_STATE ${SERVER_ARGS[*]:-}"
  remote "cat > $REMOTE_STATE/run.sh" <<EOF
#!/usr/bin/env bash
source /home/hbox/h1-ghost/env.sh
cd $REMOTE_BIN
echo "== \$(date) launching: python room_state_server.py $args" >> $REMOTE_LOG
python room_state_server.py $args 2>&1 | grep --line-buffered -v amdgpu.ids | tee -a $REMOTE_LOG
EOF
  remote "$TMUX new-session -d -s $SESSION \"bash $REMOTE_STATE/run.sh\""
  echo "== launched tmux -L hghost session $SESSION on $HBOX (port $PORT); log: $REMOTE_LOG"
}

forward_pid() { pgrep -f "ssh -f -N -o ExitOnForwardFailure=yes -L $LOCAL_PORT:127.0.0.1:$PORT $HBOX" || true; }

do_forward() {
  if [ -n "$(forward_pid)" ]; then echo "== forward $LOCAL_PORT -> $HBOX:$PORT already up"; return; fi
  ssh -f -N -o ExitOnForwardFailure=yes -L "$LOCAL_PORT:127.0.0.1:$PORT" "$HBOX"
  echo "== forward $LOCAL_PORT -> $HBOX:$PORT (pid $(forward_pid))"
}

do_wait() {
  echo "== waiting for $URL/health"
  local i
  for i in $(seq 1 120); do
    if curl -sf "$URL/health" >/dev/null 2>&1; then curl -s "$URL/health"; echo; return 0; fi
    if ! remote "$TMUX has-session -t $SESSION 2>/dev/null"; then
      echo "server session died; last log lines:" >&2; remote "tail -n 20 $REMOTE_LOG" >&2; return 1
    fi
    sleep 3
  done
  echo "server did not come up" >&2; return 1
}

do_smoke() {
  mkdir -p "$LOCAL_RESULTS"
  "$PYTHON" "$ROOT/hbox_training/room_state_server.py" smoke --url "$URL" \
    --out "$LOCAL_RESULTS/smoke-$STAMP.json" "${SMOKE_ARGS[@]:-}" | tee "$LOCAL_RESULTS/smoke-$STAMP.txt"
}

do_selftest() {
  # In-process walk on hbox (no HTTP, plain ssh session which can see /dev/kfd), for debugging.
  remote "source /home/hbox/h1-ghost/env.sh && cd $REMOTE_BIN && python room_state_server.py selftest \
    --checkpoint $CHECKPOINT --snapshot-dir $REMOTE_STATE ${SERVER_ARGS[*]:-} ${SMOKE_ARGS[*]:-} \
    --out $REMOTE_STATE/selftest-$STAMP.json 2>&1 | grep --line-buffered -v amdgpu.ids"
}

do_stop() {
  local pid
  pid=$(forward_pid)
  if [ -n "$pid" ]; then kill $pid && echo "== forward stopped"; fi
  if remote "$TMUX has-session -t $SESSION 2>/dev/null"; then
    remote "$TMUX kill-session -t $SESSION" && echo "== tmux session $SESSION stopped"
  fi
}

case "$command" in
  sync) do_sync ;;
  launch) do_sync; do_launch ;;
  forward) do_forward ;;
  wait) do_forward; do_wait ;;
  smoke) do_forward; do_smoke ;;
  selftest) do_sync; do_selftest ;;
  status)
    remote "$TMUX has-session -t $SESSION 2>/dev/null && echo 'session running' || echo 'no session'; tail -n 5 $REMOTE_LOG 2>/dev/null"
    [ -n "$(forward_pid)" ] && echo "forward up (pid $(forward_pid))" || echo "no forward"
    curl -s "$URL/health" 2>/dev/null && echo || true ;;
  logs) remote "tail -n ${LINES:-40} $REMOTE_LOG" ;;
  stop) do_stop ;;
  all)
    do_sync; do_launch; do_forward; do_wait; do_smoke
    if [ "$KEEP" = 1 ]; then
      echo "== server left running: $URL (stop with $0 stop)"
    else
      do_stop
    fi ;;
esac
