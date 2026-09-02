#!/usr/bin/env bash
# Mac-side driver for hbox_training/rollout_eval.py: sync checkpoints and inputs to
# hbox, run the evaluator there inside tmux session `hghost-rollouts` (survives a
# dropped ssh), wait, and rsync the results back under research/results/hbox-rollouts/.
#
#   hbox_training/run_rollout_eval.sh [all|sync|launch|wait|fetch|status] [options]
#
#   --run NAME            run id (default: a timestamp); pass it again to wait/fetch
#   --checkpoint N=PATH   evaluate PATH as N; PATH is `base`, a path under
#                         artifacts/checkpoints/tpu, or an absolute checkpoint directory
#                         on the Mac; repeatable. Default: base, trunk-e1, leaf-e1,
#                         trunk-e4, leaf-e4
#   --all                 the defaults plus every other trunk save
#   --room                also run the room-format pass (research/eval/room_prompts.json)
#   --batch N | --kernel auto|reference|triton | --samples N | --skip-generation
#   --force               redo checkpoints that already have a summary on hbox
#   --no-sync             `all` without the rsync step
#   --force-launch        ignore the load / GPU-busy / tmux preflight
#   --no-scan             fetch without running the haunting scan on the Mac
#
# One new checkpoint, loss slices plus the room pass, results and tables back on the Mac:
#   hbox_training/run_rollout_eval.sh all --run room-<name> --room --skip-generation \
#       --checkpoint <name>=/abs/path/to/checkpoint
#
# Never touches optimizer state (excluded from the sync) and never runs a build on
# hbox. Checkpoints land under /othersys/h1-ghost/checkpoints/tpu/, runs under
# /othersys/h1-ghost/rollouts/<run>/, scripts under ~/h1-ghost/scripts-rollout/.
set -euo pipefail

HBOX=${HBOX:-hbox}
SESSION=hghost-rollouts
# A private tmux server: hbox's default server predates the user's render/video group
# membership, so its children cannot open /dev/kfd (no GPU). Attach with `tmux -L hghost a`.
TMUX="tmux -L hghost"
ROOT=$(cd "$(dirname "$0")/.." && pwd)
PYTHON="$ROOT/.venv/bin/python"
LOCAL_CKPT="$ROOT/artifacts/checkpoints/tpu"
LOCAL_BASE="$ROOT/kaggle/base_model_dataset_public"
LOCAL_INPUTS="$ROOT/research/results/hbox-rollouts/inputs"
LOCAL_RESULTS="$ROOT/research/results/hbox-rollouts"
REMOTE_CKPT=/othersys/h1-ghost/checkpoints/tpu
REMOTE_RUNS=/othersys/h1-ghost/rollouts
REMOTE_INPUTS=$REMOTE_RUNS/inputs
REMOTE_BIN=/home/hbox/h1-ghost/scripts-rollout
TRUNK=h-ghost-h1jax-cpt-91m/trunk-wsd-lr1e-4-seed0

DEFAULT_CHECKPOINTS=(
  "base=base"
  "trunk-e1=$TRUNK/tokens-000374603776"
  "leaf-e1=h-ghost-h1jax-leaf-e1-decay10/leaf-e1-decay10/tokens-000412044297"
  "trunk-e4=$TRUNK/tokens-001497620848"
  "leaf-e4=h-ghost-h1jax-leaf-e4-decay10/leaf-e4-decay10/tokens-001535061369"
)

command=all
RUN=""
CHECKPOINTS=()
EVAL_ARGS=()
ALL=0
ROOM=0
SYNC=1
FORCE_LAUNCH=0
SCAN=1
while [ $# -gt 0 ]; do
  case "$1" in
    all|sync|launch|wait|fetch|status) command=$1 ;;
    --run) RUN=$2; shift ;;
    --checkpoint) CHECKPOINTS+=("$2"); shift ;;
    --all) ALL=1 ;;
    --room) ROOM=1 ;;
    --batch|--kernel|--samples) EVAL_ARGS+=("$1" "$2"); shift ;;
    --force|--skip-generation|--skip-losses) EVAL_ARGS+=("$1") ;;
    --no-sync) SYNC=0 ;;
    --force-launch) FORCE_LAUNCH=1 ;;
    --no-scan) SCAN=0 ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done
[ -n "$RUN" ] || RUN=$(date +%Y%m%d-%H%M)
REMOTE_RUN=$REMOTE_RUNS/$RUN
LOCAL_RUN=$LOCAL_RESULTS/$RUN

if [ ${#CHECKPOINTS[@]} -eq 0 ]; then
  CHECKPOINTS=("${DEFAULT_CHECKPOINTS[@]}")
  if [ "$ALL" = 1 ]; then
    for dir in "$LOCAL_CKPT/$TRUNK"/tokens-*; do
      tokens=$(basename "$dir" | sed 's/^tokens-0*//')
      case "$(basename "$dir")" in
        tokens-000374603776|tokens-001497620848) ;;
        *) CHECKPOINTS+=("trunk-t$tokens=$TRUNK/$(basename "$dir")") ;;
      esac
    done
  fi
fi

remote() { ssh -o BatchMode=yes "$HBOX" "$@"; }

# NAME=PATH -> the checkpoint directory on the Mac / on hbox.
local_dir() {
  local path=${1#*=}
  if [ "$path" = base ]; then echo "$LOCAL_BASE"
  elif [[ "$path" = /* ]]; then echo "$path"
  else echo "$LOCAL_CKPT/$path"; fi
}
remote_dir() {
  local name=${1%%=*} path=${1#*=}
  if [[ "$path" = /* ]]; then echo "$REMOTE_CKPT/extra/$name"; else echo "$REMOTE_CKPT/$path"; fi
}

do_sync() {
  echo "== inputs"
  if [ ! -f "$LOCAL_INPUTS/slices.json" ]; then
    "$PYTHON" "$ROOT/hbox_training/rollout_summary.py" slices --output "$LOCAL_INPUTS"
  fi
  remote "mkdir -p $REMOTE_CKPT $REMOTE_INPUTS $REMOTE_BIN"
  rsync -a "$LOCAL_INPUTS/slices.json" "$ROOT/research/eval/prompts.json" \
    "$ROOT/research/eval/retention.txt" "$HBOX:$REMOTE_INPUTS/"
  for extra in "$LOCAL_INPUTS/masks.npz" "$ROOT/research/eval/room_prompts.json"; do
    [ -f "$extra" ] && rsync -a "$extra" "$HBOX:$REMOTE_INPUTS/"
  done
  rsync -a "$ROOT/hbox_training/rollout_eval.py" "$ROOT/hbox_training/rocm_triton_ssd.py" \
    "$HBOX:$REMOTE_BIN/"
  echo "== checkpoints (weights, config and tokenizer only; optimizer state excluded)"
  for spec in "${CHECKPOINTS[@]}"; do
    local src dst
    src=$(local_dir "$spec"); dst=$(remote_dir "$spec")
    [ -f "$src/config.json" ] || { echo "no config.json in $src" >&2; exit 1; }
    echo "   ${spec%%=*}: $src -> $HBOX:$dst"
    remote "mkdir -p $dst"
    rsync -a --info=stats1 --include 'config.json' --include 'generation_config.json' \
      --include 'model.safetensors' --include 'special_tokens_map.json' \
      --include 'tokenizer.json' --include 'tokenizer_config.json' \
      --include 'trainer_state.json' --exclude '*' "$src/" "$HBOX:$dst/" | grep -E "^(sent|total)"
  done
}

preflight() {
  echo "== hbox preflight"
  remote 'uptime; free -g | sed -n 2p; echo "gpu busy: $(cat /sys/class/drm/card*/device/gpu_busy_percent 2>/dev/null | head -1)%"'
  if remote "$TMUX has-session -t $SESSION 2>/dev/null"; then
    echo "tmux session $SESSION already exists on hbox (status: $0 status --run <run>)" >&2
    [ "$FORCE_LAUNCH" = 1 ] || exit 1
  fi
  local busy available
  busy=$(remote 'cat /sys/class/drm/card*/device/gpu_busy_percent 2>/dev/null | head -1')
  available=$(remote "awk '/MemAvailable/ {print int(\$2 / 1048576)}' /proc/meminfo")
  if [ "${busy:-0}" -gt 20 ] || [ "${available:-0}" -lt 4 ]; then
    echo "hbox is busy (gpu ${busy}%, ${available} GiB available); pass --force-launch to run anyway" >&2
    [ "$FORCE_LAUNCH" = 1 ] || exit 1
  fi
}

do_launch() {
  preflight
  local args=()
  for spec in "${CHECKPOINTS[@]}"; do
    args+=("--checkpoint" "${spec%%=*}=$(remote_dir "$spec")")
  done
  args+=("--output" "$REMOTE_RUN" "--slices" "$REMOTE_INPUTS/slices.json"
    "--prompts" "$REMOTE_INPUTS/prompts.json" "--retention" "$REMOTE_INPUTS/retention.txt")
  if [ -f "$LOCAL_INPUTS/masks.npz" ]; then
    args+=("--masks" "$REMOTE_INPUTS/masks.npz")
  fi
  if [ "$ROOM" = 1 ]; then
    args+=("--room-prompts" "$REMOTE_INPUTS/room_prompts.json")
  fi
  if [ ${#EVAL_ARGS[@]} -gt 0 ]; then args+=("${EVAL_ARGS[@]}"); fi
  remote "mkdir -p $REMOTE_RUN && cat > $REMOTE_RUN/run.sh" <<EOF
#!/usr/bin/env bash
set -o pipefail
source /home/hbox/h1-ghost/env.sh
cd $REMOTE_BIN
python rollout_eval.py ${args[*]} 2>&1 | tee -a $REMOTE_RUN/log.txt
echo \${PIPESTATUS[0]} > $REMOTE_RUN/exit.txt
EOF
  remote "rm -f $REMOTE_RUN/exit.txt && $TMUX new-session -d -s $SESSION \"bash $REMOTE_RUN/run.sh\""
  echo "== launched run $RUN in tmux -L hghost session $SESSION on $HBOX"
  echo "   follow: ssh $HBOX tail -f $REMOTE_RUN/log.txt"
  echo "   then:   $0 fetch --run $RUN"
}

do_wait() {
  echo "== waiting for $REMOTE_RUN/exit.txt"
  local last=""
  while ! remote "test -f $REMOTE_RUN/exit.txt"; do
    local line
    line=$(remote "tail -n 1 $REMOTE_RUN/log.txt 2>/dev/null" || true)
    if [ "$line" != "$last" ]; then echo "   $line"; last=$line; fi
    sleep 30
  done
  local status
  status=$(remote "cat $REMOTE_RUN/exit.txt")
  echo "== hbox run $RUN exited with $status"
  return "$status"
}

do_fetch() {
  mkdir -p "$LOCAL_RUN"
  rsync -a "$HBOX:$REMOTE_RUN/" "$LOCAL_RUN/"
  echo "== results in $LOCAL_RUN"
  if [ "$SCAN" = 1 ]; then
    "$PYTHON" "$ROOT/hbox_training/rollout_summary.py" report "$LOCAL_RUN"
  else
    "$PYTHON" "$ROOT/hbox_training/rollout_summary.py" report "$LOCAL_RUN" --no-scan
  fi
  if ls "$LOCAL_RUN"/room-*.jsonl >/dev/null 2>&1; then
    "$PYTHON" "$ROOT/hbox_training/rollout_summary.py" room "$LOCAL_RUN" >/dev/null
    echo "== room table: $LOCAL_RUN/room-table.md"
  fi
}

case "$command" in
  sync) do_sync ;;
  launch) [ "$SYNC" = 1 ] && do_sync; do_launch ;;
  wait) do_wait ;;
  fetch) do_fetch ;;
  status) remote "$TMUX has-session -t $SESSION 2>/dev/null && echo 'session running' || echo 'no session'; tail -n 5 $REMOTE_RUN/log.txt 2>/dev/null; cat $REMOTE_RUN/exit.txt 2>/dev/null" ;;
  all)
    [ "$SYNC" = 1 ] && do_sync
    do_launch
    status=0
    do_wait || status=$?
    do_fetch
    exit "$status"
    ;;
esac
