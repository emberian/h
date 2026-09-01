#!/usr/bin/env python3
"""Demonstrate whether stock PyTorch Gloo can reduce an MPS tensor."""

from __future__ import annotations

import os
from datetime import timedelta

import torch
import torch.distributed as dist


def main() -> None:
    rank = int(os.environ["RANK"])
    dist.init_process_group("gloo", timeout=timedelta(seconds=30))
    value = torch.tensor([float(rank)], device="mps")
    dist.all_reduce(value)
    torch.mps.synchronize()
    print(f"rank={rank} value={float(value.item())}", flush=True)
    dist.destroy_process_group()


if __name__ == "__main__":
    main()
