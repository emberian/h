from __future__ import annotations

import glob
from pathlib import Path
import runpy


matches = [
    Path(path)
    for path in glob.glob("/kaggle/input/**/tpu_smoke_05b.py", recursive=True)
    if Path(path).is_file()
]
if len(matches) != 1:
    raise RuntimeError(f"Expected exactly one 0.5B smoke entrypoint, found: {matches}")
runpy.run_path(str(matches[0]), run_name="__main__")
