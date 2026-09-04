#!/bin/zsh
# Pull hbox lens outputs for a model into research/jlens/out/<model>/ and fill in the lens statistics.
# Usage: research/jlens/pull_hbox.sh <model> [layers...]
cd /Users/ember/dev/h
m=$1; shift
rsync -a --include='lens-L*' --include='jac-L*' --include='hlast-L*' --include='parity-torch-*' --exclude='*' hbox:/home/hbox/h1-ghost/jlens/out/$m/ research/jlens/out/$m/
rsync -a hbox:/home/hbox/h1-ghost/jlens/out/lens-$m-L*.log research/jlens/out/ 2>/dev/null
PYTHONPATH=jax_training JAX_PLATFORM_NAME=cpu H1JAX_SSD=v2 .venv-jax/bin/python -u research/jlens/jlens.py stats --model $m --layers "$@" 2>&1 | grep -v WARNING
