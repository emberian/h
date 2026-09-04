#!/bin/bash
# hbox: J-lens Jacobians for all four models with the same contexts as the Mac (72 windows + 12 room prompts).
# Usage: KERNEL=triton MODE=replicate CHUNK=64 ./run_hbox.sh   (defaults: reference kernel, batched vjp, auto chunk)
cd /home/hbox/h1-ghost/jlens && source /home/hbox/h1-ghost/env.sh
KERNEL=${KERNEL:-reference}; MODE=${MODE:-batched}; CHUNK=${CHUNK:-0}
CTX=contexts-n72-s0.json
LEAF=/othersys/h1-ghost/checkpoints/tpu/h-ghost-h1jax-leaf-s1-e4/leaf-s1-e4-decay10/tokens-001535061369
run() {  # name checkpoint layers...
  local name=$1 ckpt=$2; shift 2
  for l in "$@"; do
    python -u jlens_torch.py lens --checkpoint "$ckpt" --contexts $CTX --layer $l --out out/$name --model-name $name \
      --kernel $KERNEL --mode $MODE --chunk $CHUNK > out/lens-$name-L$l.log 2>&1
  done
}
run 91m-leaf  $LEAF 16
run 05b-base  /othersys/h1-ghost/checkpoints/tpu/extra/base05b 18
run 05b-e2v4  /othersys/h1-ghost/checkpoints/tpu/extra/room05b-e2-v4-final 18
run 91m-leaf  $LEAF 12 8
run 90m-base  /othersys/h1-ghost/checkpoints/tpu/base 12 8 16
echo done > out/all.done
