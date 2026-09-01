#!/usr/bin/env bash
# Source for the isolated persvati PyTorch/ROCm probe environment.
export H1_DISTRIBUTED_HOME=/home/ember/h1-distributed
export VIRTUAL_ENV="$H1_DISTRIBUTED_HOME/venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
export HF_HOME="$H1_DISTRIBUTED_HOME/cache/huggingface"
export HF_HUB_CACHE="$HF_HOME/hub"
export UV_CACHE_DIR="$H1_DISTRIBUTED_HOME/cache/uv"
export H1_MODEL_DIR="$H1_DISTRIBUTED_HOME/models/Falcon-H1-Tiny-90M-Base"
# Unofficial compatibility override: the physical GPU is gfx1150.
export HSA_OVERRIDE_GFX_VERSION=11.0.0
export NCCL_SOCKET_IFNAME=wlp194s0
