#!/usr/bin/env bash
# Source for the measured Apple MLX/PyTorch-MPS probe environment.
export H1_DISTRIBUTED_HOME=/Users/ember/.cache/h1-distributed
export VIRTUAL_ENV="$H1_DISTRIBUTED_HOME/venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
export HF_HOME="$H1_DISTRIBUTED_HOME/cache/huggingface"
export HF_HUB_CACHE="$HF_HOME/hub"
export H1_MODEL_DIR="$H1_DISTRIBUTED_HOME/models/Falcon-H1-Tiny-90M-Base"
