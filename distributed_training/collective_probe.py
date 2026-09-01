#!/usr/bin/env python3
"""Measure a bounded two-rank GPU all-reduce with the model's gradient size."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import timedelta

import torch
import torch.distributed as dist


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--elements", type=int, default=91_131_072)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rank = int(os.environ["RANK"])
    world_size = int(os.environ["WORLD_SIZE"])
    if world_size != 2:
        raise ValueError("this bounded probe is intentionally limited to two ranks")
    torch.cuda.set_device(0)
    dist.init_process_group(
        backend="nccl",
        timeout=timedelta(seconds=args.timeout_seconds),
        device_id=torch.device("cuda", 0),
    )
    payload = torch.full(
        (args.elements,),
        float(rank),
        dtype=torch.bfloat16,
        device="cuda",
    )

    dist.all_reduce(payload)
    torch.cuda.synchronize()
    results: list[float] = []
    for _ in range(args.iterations):
        payload.fill_(float(rank))
        torch.cuda.synchronize()
        started = time.perf_counter()
        dist.all_reduce(payload)
        torch.cuda.synchronize()
        results.append(time.perf_counter() - started)
        if float(payload[0]) != 1.0:
            raise RuntimeError(f"bad all-reduce result on rank {rank}: {float(payload[0])}")

    report = {
        "rank": rank,
        "world_size": world_size,
        "backend": dist.get_backend(),
        "torch": torch.__version__,
        "hip": torch.version.hip,
        "gpu": torch.cuda.get_device_name(0),
        "arch": torch.cuda.get_device_properties(0).gcnArchName,
        "elements": args.elements,
        "payload_mib": args.elements * payload.element_size() / 2**20,
        "seconds": results,
        "payload_mib_per_second": [
            args.elements * payload.element_size() / 2**20 / seconds
            for seconds in results
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    dist.destroy_process_group()


if __name__ == "__main__":
    main()
