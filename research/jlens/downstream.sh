#!/bin/zsh
# readout + sparse + inject for one model/layer on the Mac (inject only for the 91M models unless INJECT=1).
cd /Users/ember/dev/h
export PYTHONPATH=jax_training JAX_PLATFORM_NAME=cpu H1JAX_SSD=v2
m=$1; l=$2
.venv-jax/bin/python -u research/jlens/jlens.py readout --model $m --layers $l > research/jlens/out/readout-$m-L$l.log 2>&1
.venv-jax/bin/python -u research/jlens/jlens.py sparse --model $m --layers $l --n-stored 72 > research/jlens/out/sparse-$m-L$l.log 2>&1
if [[ $m == 9* || ${INJECT:-0} == 1 ]]; then
  while pgrep -f "jlens.py inject" > /dev/null; do sleep 20; done
  .venv-jax/bin/python -u research/jlens/jlens.py inject --model $m --layers $l > research/jlens/out/inject-$m-L$l.log 2>&1
fi
echo done > research/jlens/out/downstream-$m-L$l.done
