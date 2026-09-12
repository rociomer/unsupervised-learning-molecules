#!/usr/bin/env python3
"""Regenerate every figure the article uses, by running the notebooks that draw them.

    python scripts/make_manuscript_figures.py                 # write to notebooks/figures
    python scripts/make_manuscript_figures.py --outdir /tmp/f # write somewhere else
    python scripts/make_manuscript_figures.py --list          # show the mapping and exit

Each figure is drawn in the notebook for the section that discusses it, and
nowhere else. That is the whole point: a figure produced by a script the reader
never opens is a figure the reader cannot check. This script executes those
notebooks and confirms that every expected file appeared and is newer than the
run started, so a notebook that quietly skipped its figure fails the build
instead of leaving a stale file in place.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# figure stem -> (article figure number, notebook that draws it)
FIGURES = {
    "caffeineCM": (2, "06-representations-and-baselines.ipynb"),
    "scaling_pca": (3, "06-representations-and-baselines.ipynb"),
    "embedding_illusion": (4, "07-dimensionality-reduction.ipynb"),
    "embedding_quality": (5, "07-dimensionality-reduction.ipynb"),
    "silhouette_selection_bias": (6, "08-clustering.ipynb"),
    "cluster1_angle": (7, "08-clustering.ipynb"),
    "clustering_illusion_molecules": (8, "08-clustering.ipynb"),
    "method_comparison": (9, "09-statistical-comparison.ipynb"),
    "property_confound": (10, "10-generative-models.ipynb"),
}
# Figure 1 is the workflow overview, drawn by hand and kept beside the manuscript.


def run_notebook(name: str, outdir: Path) -> bool:
    path = REPO / "notebooks" / name
    print(f"  running {name}")
    env = dict(os.environ, FIGDIR=str(outdir))
    result = subprocess.run(
        [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook",
         "--execute", "--stdout", str(path)],
        capture_output=True, text=True, env=env,
    )
    if result.returncode != 0:
        tail = result.stderr.strip().splitlines()[-15:]
        print(f"    FAILED\n      " + "\n      ".join(tail), file=sys.stderr)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--outdir", type=Path,
                        default=REPO / "notebooks" / "figures",
                        help="where the figures are written (default: notebooks/figures)")
    parser.add_argument("--list", action="store_true", help="show the mapping and exit")
    args = parser.parse_args()

    if args.list:
        for stem, (number, notebook) in sorted(FIGURES.items(), key=lambda kv: kv[1][0]):
            print(f"  Figure {number:>2}  {stem:<32s} {notebook}")
        return 0

    args.outdir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    notebooks = sorted({nb for _, nb in FIGURES.values()})
    print(f"Writing figures to {args.outdir}")
    ok = all([run_notebook(nb, args.outdir) for nb in notebooks])

    missing, stale = [], []
    for stem, (number, notebook) in FIGURES.items():
        for suffix in ("png", "pdf"):
            path = args.outdir / f"{stem}.{suffix}"
            if not path.exists() or path.stat().st_size == 0:
                missing.append(f"Figure {number} ({stem}.{suffix}, from {notebook})")
            elif path.stat().st_mtime < started:
                stale.append(f"Figure {number} ({stem}.{suffix}, from {notebook})")

    if missing:
        print("\nNever written:\n  " + "\n  ".join(missing), file=sys.stderr)
    if stale:
        print("\nLeft over from an earlier run, so the notebook skipped it:\n  "
              + "\n  ".join(stale), file=sys.stderr)
    if ok and not missing and not stale:
        print(f"\nAll {len(FIGURES)} figures regenerated.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
