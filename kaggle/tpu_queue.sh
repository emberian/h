#!/bin/sh
# Sequential Kaggle TPU queue: wait for a running kernel, then push the next ones one at a time
# (Kaggle allows one TPU session per account), downloading each finished output.
#
# usage: kaggle/tpu_queue.sh <out-root> <wait-slug> <dir1> [<dir2> ...]
#   out-root  directory for downloads and the queue log
#   wait-slug kernel slug currently running (e.g. emberian64/h-ghost-h1jax-cpt-91m), or "-" for none
#   dirN      kernel directories to push in order (each has kernel-metadata.json with its slug)
#
# Stops at the first ERROR/CANCEL so a broken run does not consume the queue. Intended to run inside
# tmux; progress lines are prefixed with the time so a log monitor can follow them.
set -u
OUT="$1"; shift
WAIT="$1"; shift
KAGGLE="uvx --from kaggle kaggle"
mkdir -p "$OUT"
log() { printf '%s %s\n' "$(date +%H:%M:%S)" "$*"; }

status_of() { timeout 90 $KAGGLE kernels status "$1" 2>&1 | tail -1; }

wait_for() {
  slug="$1"
  while true; do
    s=$(status_of "$slug")
    case "$s" in
      *COMPLETE*) log "DONE $slug"; return 0 ;;
      *ERROR*|*CANCEL*) log "FAILED $slug: $s"; return 1 ;;
      *) sleep 90 ;;
    esac
  done
}

download() {
  slug="$1"; name=$(basename "$slug"); dest="$OUT/$name"
  mkdir -p "$dest"
  log "DOWNLOAD $slug -> $dest"
  timeout 3600 $KAGGLE kernels output "$slug" -p "$dest" --force >"$dest/download.log" 2>&1 \
    && log "DOWNLOADED $slug" || log "DOWNLOAD-FAILED $slug (see $dest/download.log)"
}

if [ "$WAIT" != "-" ]; then
  log "WAITING $WAIT"
  wait_for "$WAIT" || { log "QUEUE STOPPED"; exit 1; }
  ( download "$WAIT" ) &
fi

for dir in "$@"; do
  slug=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['id'])" "$dir/kernel-metadata.json")
  log "PUSH $dir ($slug)"
  timeout 300 $KAGGLE kernels push -p "$dir" 2>&1 | tail -1
  sleep 60
  wait_for "$slug" || { log "QUEUE STOPPED"; wait; exit 1; }
  ( download "$slug" ) &
done
wait
log "QUEUE COMPLETE"
