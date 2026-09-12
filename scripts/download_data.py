#!/usr/bin/env python3
"""Fetch the example data sets and build the files the notebooks read.

    python scripts/download_data.py            # build anything missing
    python scripts/download_data.py --force    # rebuild everything

Each file is derived from its original source rather than copied from a mirror.
The script downloads the upstream distribution once into ``data/_upstream/``,
then applies the derivation recorded below to produce the working copy in
``data/``. You can read the derivation, which means you can check it, and it is
the reason the provenance recorded here is worth something.

Section 4 of the article argues that provenance costs minutes at curation time
and cannot be reconstructed afterwards. The upstream URL, the DOI and the exact
transformation applied to each file are recorded here for that reason.
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

UPSTREAM = {
    "qm7.mat": {
        "url": "http://quantum-machine.org/data/qm7.mat",
        "doi": "10.1103/PhysRevLett.108.058301",  # Rupp et al. 2012
    },
    "250k_rndm_zinc_drugs_clean_3.csv": {
        # The Kaggle mirror needs an API token, so it cannot be fetched by a
        # script. This is the same file, publicly readable.
        "url": ("https://raw.githubusercontent.com/aspuru-guzik-group/chemical_vae/"
                "master/models/zinc/250k_rndm_zinc_drugs_clean_3.csv"),
        "doi": "10.1021/acscentsci.7b00572",  # Gomez-Bombarelli et al. 2018
    },
    "PROTAC_main_table.txt": {
        "url": "https://tpddb.idrblab.net/sites/files/tpd_download/PROTAC_main_table.txt",
        "doi": "10.1093/nar/gkaf996",  # Qin et al. 2026, TPDdb
    },
    "md17_aspirin.npz": {
        "url": "http://www.quantum-machine.org/gdml/data/npz/md17_aspirin.npz",
        "doi": "10.1126/sciadv.1603015",  # Chmiela et al. 2017
        "large": True,
    },
}

MD17_N_FRAMES = 10_000
PROTAC_LIGASES = ("CRBN", "VHL")
PROTAC_PER_LIGASE = 500
TPDDB_HEADER = ("TPD ID", "TPD NAME", "PubChem synonyms", "SMILES", "Fomula",
                "Target Symbol", "Target ID", "Ligase", "Source")


def derive_qm7_xyz(upstream: Path) -> bytes:
    """``upstream/qm7.mat`` as extended XYZ bytes, one frame per row of ``R``.

    Assumes the .mat file carries ``R``, ``Z`` and ``T`` and contains only H,
    C, N, O and S; any other element raises a KeyError. Coordinates are copied
    across unchanged, so the output is in BOHR and not angstrom.

    The ``smiles=`` field is written from coordinates without bond perception,
    which makes it a disconnected atom list for every structure and therefore
    unusable. It is kept because the published figures were computed from this
    exact file.
    """
    import numpy as np
    import scipy.io

    mat = scipy.io.loadmat(upstream / "qm7.mat")
    positions, species, energies = mat["R"], mat["Z"], mat["T"].ravel()
    symbols = {1: "H", 6: "C", 7: "N", 8: "O", 16: "S"}

    out = io.StringIO()
    for i in range(positions.shape[0]):
        numbers = species[i]
        n_atoms = int((numbers > 0).sum())
        atoms = [symbols[int(round(z))] for z in numbers[:n_atoms]]
        pseudo_smiles = ".".join(f"[{a}]" for a in atoms)
        out.write(f"{n_atoms}\n")
        # str(), not an f-string: formatting a numpy scalar with an empty format
        # spec widens it to float64 and writes -417.9599914550781 for -417.96.
        out.write("Properties=species:S:1:pos:R:3 "
                  "atomization_energy=" + str(np.float32(energies[i])) + " "
                  f'smiles={pseudo_smiles} pbc="F F F"\n')
        for atom, xyz in zip(atoms, positions[i][:n_atoms]):
            out.write(f"{atom:<2s}" + "".join(f"{float(v):17.8f}" for v in xyz) + "\n")
    return out.getvalue().encode()


ZINC_N_RECORDS = 10_000


def derive_zinc_sample(upstream: Path) -> bytes:
    """The first ``ZINC_N_RECORDS`` rows of ZINC-250k, as CSV bytes.

    Reads ``upstream/250k_rndm_zinc_drugs_clean_3.csv`` and raises ValueError
    if its columns are no longer ``smiles, logP, qed, SAS``. The SMILES is
    stripped of surrounding whitespace and nothing else is touched: the
    numeric columns are copied as text and never parsed, because round-tripping
    2.0840945720726807 through a float is not guaranteed to give back the same
    characters.

    Ten thousand rather than a thousand because the standardization work in
    notebook 04 needs molecules that standardization actually changes: about a
    third of ZINC records carry a formal charge, so ten thousand gives roughly
    3,200 for the uncharging step to act on where a thousand gave about 300.
    Notebooks whose pairwise work is quadratic take the first thousand rows
    instead.
    """
    with (upstream / "250k_rndm_zinc_drugs_clean_3.csv").open(newline="") as handle:
        rows = list(csv.reader(handle))
    header, records = rows[0], rows[1:]
    if header != ["smiles", "logP", "qed", "SAS"]:
        raise ValueError(f"unexpected upstream columns: {header}")

    out = io.StringIO()
    out.write(",".join(header) + "\n")
    for record in records[:ZINC_N_RECORDS]:
        # The upstream CSV keeps a trailing newline inside the quoted SMILES.
        out.write(",".join([record[0].strip()] + record[1:]) + "\n")
    return out.getvalue().encode()


def derive_protac_sample(upstream: Path) -> bytes:
    """``PROTAC_PER_LIGASE`` CRBN and VHL PROTACs from TPDdb, as CSV bytes.

    Reads ``upstream/PROTAC_main_table.txt``. A row is kept if it has the
    expected number of columns, a non-empty SMILES, one of ``PROTAC_LIGASES``,
    and a SMILES string not already seen; the first ``PROTAC_PER_LIGASE`` of
    each ligase in file order are written out. Raises ValueError if the
    upstream header has changed, or if either ligase yields too few rows.

    Nothing else is cleaned, so that duplicate structures written two ways,
    salt forms and missing fields all survive into the curation work of
    notebook 04.
    """
    with (upstream / "PROTAC_main_table.txt").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t"))

    header = tuple(rows[0])
    if header != TPDDB_HEADER:
        raise ValueError("TPDdb's PROTAC table no longer has the columns this "
                         f"derivation expects.\n  expected {TPDDB_HEADER}\n  got {header}")
    index = {name: i for i, name in enumerate(header)}

    kept = {ligase: [] for ligase in PROTAC_LIGASES}
    seen = set()
    for row in rows[1:]:
        if len(row) != len(header):
            continue
        smiles = row[index["SMILES"]].strip()
        ligase = row[index["Ligase"]].strip()
        if not smiles or ligase not in kept or smiles in seen:
            continue
        if len(kept[ligase]) >= PROTAC_PER_LIGASE:
            continue
        seen.add(smiles)
        kept[ligase].append([row[index[c]].strip() for c in
                             ("TPD ID", "SMILES", "Fomula", "Target Symbol",
                              "Target ID", "Ligase", "Source")])

    short = {lig: len(v) for lig, v in kept.items() if len(v) < PROTAC_PER_LIGASE}
    if short:
        raise ValueError(f"wanted {PROTAC_PER_LIGASE} PROTACs per ligase, got {short}. "
                         "Check the Ligase column before lowering PROTAC_PER_LIGASE.")

    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["tpd_id", "smiles", "formula", "target_symbol",
                     "target_id", "ligase", "source"])
    for ligase in PROTAC_LIGASES:
        writer.writerows(kept[ligase])
    return out.getvalue().encode()


def derive_md17_subset(upstream: Path) -> bytes:
    """``MD17_N_FRAMES`` evenly spaced aspirin frames, as a compressed .npz.

    Reads ``upstream/md17_aspirin.npz``. ``E``, ``F`` and ``R`` are subset by
    ``numpy.linspace(0, n - 1, MD17_N_FRAMES).round().astype(int)`` and every
    other array is copied through unchanged. Raises ValueError if that spacing
    does not yield distinct indices, which means the trajectory is shorter than
    the derivation expects.

    Even spacing rather than a random draw, so that there is no seed and no
    dependence on numpy's RNG and the frames are the same on every machine.
    It also gives the decorrelated frames covering the full torsional range
    that the aspirin example needs, by construction.
    """
    import numpy as np

    with np.load(upstream / "md17_aspirin.npz", allow_pickle=True) as data:
        n_frames = data["E"].shape[0]
        keep = np.unique(np.linspace(0, n_frames - 1, MD17_N_FRAMES).round().astype(np.int64))
        if keep.size != MD17_N_FRAMES:
            raise ValueError(f"even spacing over {n_frames} frames gave {keep.size} "
                             "unique indices; the trajectory is shorter than expected")
        arrays = {"E": data["E"][keep], "name": data["name"], "F": data["F"][keep],
                  "theory": data["theory"], "R": data["R"][keep], "z": data["z"],
                  "type": data["type"], "md5": data["md5"]}

    buffer = io.BytesIO()
    np.savez_compressed(buffer, **arrays)
    return buffer.getvalue()


FILES = {
    "zinc-250k-sample.csv": {
        "what": "first 10,000 records of ZINC-250k with logP, QED and SA score",
        "derive": derive_zinc_sample,
        "needs": ["250k_rndm_zinc_drugs_clean_3.csv"],
    },
    "protac-tpddb-sample.csv": {
        "what": "1,000 PROTACs from TPDdb, 500 CRBN and 500 VHL, uncurated",
        "derive": derive_protac_sample,
        "needs": ["PROTAC_main_table.txt"],
    },
    "qm7.xyz": {
        "what": "7,165 QM7 structures with atomization energies, extended XYZ",
        "derive": derive_qm7_xyz,
        "needs": ["qm7.mat"],
    },
    "md17_aspirin_10000.npz": {
        "what": "10,000 evenly spaced frames of the MD17 aspirin trajectory",
        "derive": derive_md17_subset,
        "needs": ["md17_aspirin.npz"],
    },
}


def download(name: str, target: Path) -> bool:
    spec = UPSTREAM[name]
    print(f"    fetching {name}")
    print(f"      from {spec['url']}")
    if spec.get("large"):
        print("      This one is about 200 MB and there is no progress bar. Give it a\n"
              "      few minutes and do not interrupt it. It is cached afterwards.")
    tmp = target.with_suffix(target.suffix + ".part")
    try:
        urllib.request.urlretrieve(spec["url"], tmp)
    except (urllib.error.URLError, OSError) as exc:
        tmp.unlink(missing_ok=True)
        reason = (f"HTTP {exc.code} {exc.reason}"
                  if isinstance(exc, urllib.error.HTTPError) else str(exc))
        print(f"    FAILED: {reason}\n"
              f"    Open {spec['url']} in a browser. If it downloads, save it as\n"
              f"      {target}\n"
              "    and run this script again; it will pick the file up and carry on.",
              file=sys.stderr)
        return False
    tmp.replace(target)
    return True


def build(name: str, spec: dict, data_dir: Path, upstream_dir: Path, force: bool) -> bool:
    target = data_dir / name
    if target.exists() and not force:
        print(f"  {name}: already here")
        return True

    print(f"  {name}: building {spec['what']}")
    upstream_dir.mkdir(parents=True, exist_ok=True)
    for needed in spec["needs"]:
        cached = upstream_dir / needed
        if cached.exists() and not force:
            print(f"    {needed}: cached")
        elif not download(needed, cached):
            return False

    try:
        content = spec["derive"](upstream_dir)
    except Exception as exc:  # noqa: BLE001 - the message matters more than the type
        print(f"    FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return False

    target.write_bytes(content)
    print(f"    wrote {target.name} ({target.stat().st_size / 1e6:.1f} MB)")
    return True


# Expected size and record count of each derived file. An upstream re-release of
# ZINC or TPDdb, or a changed derivation, must not silently alter the counts the
# notebooks quote (for example the 10,000 records notebook 04 reports), so the
# build verifies against these and fails loudly on any drift. The record count is
# the robust signal; the byte count is exact for the pinned environment.
EXPECTED = {
    "zinc-250k-sample.csv": {"bytes": 876969, "records": 10000},
    "protac-tpddb-sample.csv": {"bytes": 176898, "records": 1000},
    "qm7.xyz": {"bytes": 6997155, "records": 7165},
    "md17_aspirin_10000.npz": {"bytes": 9762532, "records": 10000},
}


def record_count(path: Path) -> int:
    """Records in a derived file: CSV data rows, XYZ structures, or npz frames."""
    if path.suffix == ".csv":
        with path.open() as handle:
            return sum(1 for _ in handle) - 1               # minus the header row
    if path.suffix == ".xyz":
        # Extended XYZ starts each structure with a lone atom-count line.
        with path.open() as handle:
            return sum(1 for line in handle
                       if len(line.split()) == 1 and line.strip().isdigit())
    if path.suffix == ".npz":
        import numpy as np
        with np.load(path) as archive:
            return int(archive["R"].shape[0])
    raise ValueError(f"no record-count rule for {path.name}")


def verify(data_dir: Path) -> bool:
    """Fail loudly if any derived file's size or record count has drifted."""
    ok = True
    for name, expected in EXPECTED.items():
        path = data_dir / name
        size, records = path.stat().st_size, record_count(path)
        changed = size != expected["bytes"] or records != expected["records"]
        print(f"  {name:32s} {size:9d} bytes, {records:6d} records  "
              f"[{'CHANGED' if changed else 'ok'}]")
        if changed:
            ok = False
            print(f"    expected {expected['bytes']} bytes and {expected['records']} records; an "
                  "upstream re-release or a changed derivation would explain this, and the "
                  "notebooks' counts can no longer be trusted until it is understood.",
                  file=sys.stderr)
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="rebuild files that already exist")
    parser.add_argument("--data-dir", type=Path, default=REPO / "data",
                        help="where the files go (default: <repo>/data)")
    args = parser.parse_args()
    args.data_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building example data in {args.data_dir}\n")
    results = [build(name, spec, args.data_dir, args.data_dir / "_upstream", args.force)
               for name, spec in FILES.items()]
    if not all(results):
        print("\nSomething did not build; see the messages above.", file=sys.stderr)
        return 1

    print("\nVerifying each derived file against its recorded size and record count:")
    if not verify(args.data_dir):
        print("\nA derived file no longer matches its recorded counts; see above.", file=sys.stderr)
        return 1
    print("\nAll four data files are ready and match their recorded counts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
