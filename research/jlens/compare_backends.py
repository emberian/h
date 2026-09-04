"""Compare Mac/JAX lenses (out/<model>/mac/) with hbox/PyTorch lenses (out/<model>/hbox/) on the same contexts."""
import json, sys
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parent / "out"
rows = []
for m in sys.argv[1:] or ["90m-base", "91m-leaf"]:
    for p in sorted((OUT / m / "hbox").glob("jac-L*.npy")):
        if "future" in p.name:
            continue
        l = p.stem.split("L")[-1]
        q = OUT / m / "mac" / p.name
        if not q.exists():
            continue
        A, B = np.load(q).astype(np.float64), np.load(p).astype(np.float64)
        rel = np.linalg.norm(A - B) / np.linalg.norm(A)
        MA, MB = np.load(OUT / m / "mac" / f"lens-L{l}.npy"), np.load(OUT / m / "hbox" / f"lens-L{l}.npy")
        relM = np.linalg.norm(MA - MB) / np.linalg.norm(MA)
        ja, jb = json.loads((OUT / m / "mac" / f"lens-L{l}.json").read_text()), json.loads((OUT / m / "hbox" / f"lens-L{l}.json").read_text())
        ta = ja["seconds_total"] / ja["n_jacobians"]; tb = jb["seconds_total"] / jb["n_jacobians"]
        rows.append((m, int(l), rel, relM, ta, tb))
print("| model | layer | rel diff of mean J (Mac vs hbox) | rel diff of lens M | s/Jacobian Mac (JAX CPU, shared) | s/Jacobian hbox (torch ROCm) |")
print("|---|---|---|---|---|---|")
for m, l, rel, relM, ta, tb in sorted(rows):
    print(f"| {m} | {l} | {rel:.1e} | {relM:.1e} | {ta:.0f} | {tb:.1f} |")
