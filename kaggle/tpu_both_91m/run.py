"""One allocation: full-model smoke, 91M CPT 1x, then fresh 91M 2x."""

from __future__ import annotations

import gc
import glob
import json
from pathlib import Path
import runpy
import time


PHASES = (
    ("full_91m_smoke", "tpu_smoke_gate.py"),
    ("falcon_h1_91m_cpt_1x", "tpu_cpt_91m.py"),
    ("falcon_h1_91m_random_init_2x", "tpu_fresh_91m.py"),
)


def exactly_one(name: str) -> Path:
    matches = [
        Path(path)
        for path in glob.glob(f"/kaggle/input/**/{name}", recursive=True)
        if Path(path).is_file()
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {name}, found {matches}")
    return matches[0]


def release_jax() -> None:
    gc.collect()
    try:
        import jax

        jax.clear_caches()
    except ImportError:
        pass
    gc.collect()


def main() -> None:
    started = time.time()
    completed: list[dict] = []
    for phase, filename in PHASES:
        phase_started = time.time()
        source = exactly_one(filename)
        print(
            json.dumps(
                {"event": "phase_start", "phase": phase, "source": str(source)}
            ),
            flush=True,
        )
        runpy.run_path(str(source), run_name="__main__")
        phase_report = {
            "phase": phase,
            "elapsed_seconds": time.time() - phase_started,
        }
        completed.append(phase_report)
        print(json.dumps({"event": "phase_complete", **phase_report}), flush=True)
        release_jax()

    report = {
        "completed": True,
        "phases": completed,
        "elapsed_seconds": time.time() - started,
    }
    Path("/kaggle/working/h-ghost-91m-experiments-complete.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print("H_GHOST_ALL_91M_EXPERIMENTS_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
