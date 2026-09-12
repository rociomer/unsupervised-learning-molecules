# Example data

These files are **not** committed to this repository. They are built from their
original sources by

```bash
python scripts/download_data.py
```

which downloads each upstream distribution once into `data/_upstream/`, then
applies a derivation recorded in that script to produce the working copy here.
You can read the derivation, so you can check it, and that is what makes the
provenance below worth something. A mirror of a derived file would give you
nothing but someone's word that the derivation was done right once.

Add `--force` to rebuild a file that already exists.

| file | what it is | source | DOI |
|---|---|---|---|
| `zinc-250k-sample.csv` | first 10,000 records of ZINC-250k, with logP, QED and SA score | [chemical_vae](https://github.com/aspuru-guzik-group/chemical_vae) | [10.1021/acscentsci.7b00572](https://doi.org/10.1021/acscentsci.7b00572) |
| `protac-tpddb-sample.csv` | 1,000 PROTACs, 500 CRBN and 500 VHL, with targets and ligases | [TPDdb](https://tpddb.idrblab.net/download) | [10.1093/nar/gkaf996](https://doi.org/10.1093/nar/gkaf996) |
| `qm7.xyz` | 7,165 structures with atomization energies | [quantum-machine.org](http://quantum-machine.org/datasets/) | [10.1103/PhysRevLett.108.058301](https://doi.org/10.1103/PhysRevLett.108.058301) |
| `md17_aspirin_10000.npz` | 10,000 evenly spaced frames of the aspirin trajectory | [sgdml.org](http://www.sgdml.org/#datasets) | [10.1126/sciadv.1603015](https://doi.org/10.1126/sciadv.1603015) |

## Three things about these files that are not obvious

**QM7 positions are in bohr, not angstrom.** `qm7.mat` distributes `R` in atomic
units and the conversion to XYZ copied the numbers as they were, so methane's
C-H distance reads 2.06 and not 1.09. The Coulomb-matrix work is unaffected,
because it uses off-diagonal entries and a uniform rescaling of every distance
multiplies those by one constant. Anything that depends on an absolute length
scale is not: notebook 08's shape descriptor and any SOAP or ACSF cutoff in
notebook 06 multiply by 0.529177210903 to reach angstrom first, and so should
you.

**The `smiles=` field inside `qm7.xyz` is not a useful SMILES.** It was written
from coordinates without bond perception, so every structure appears as a
disconnected atom list and methane is `[C].[H].[H].[H].[H]`. QM7 as distributed
here carries no usable chemical identifiers. Run bond perception on the
coordinates if you need them, and use the ZINC or PROTAC files when you want
SMILES.

**The PROTAC sample is where deduplication has something to find.** ZINC-250k
arrives pre-cleaned: across the first ten thousand records there is not one salt,
not one multi-fragment entry and not one repeated SMILES, so it cannot show you
what deduplication is for. The PROTAC sample can. It holds twenty groups of
molecules that differ only in stereochemistry, mostly enantiomer pairs at the
glutarimide center of the E3 ligand, which collapse into duplicates the moment
you standardize stereochemistry away. Notebook 04 uses both files for that
reason. Its `ligase` and `target_symbol` columns are
labels no unsupervised method in these notebooks is given, so you can use them to
interpret a clustering from outside it.

## Provenance

The upstream URL, the DOI and the exact transformation applied to each file are
recorded in `scripts/download_data.py`. Keep them with any derived data you save.
Section 4 of the accompanying article argues that provenance costs minutes at
curation time and cannot be reconstructed afterwards.

The MD17 subset is 10,000 frames spaced evenly across the full 211,762-frame
trajectory, `numpy.linspace(0, n - 1, 10000).round().astype(int)`. No random
seed, the same frames on every machine, and the sample spans the full torsional
range by construction. Even spacing is not statistical independence, though:
notebook 08 measures the autocorrelation of the shipped frames and finds the
energy effectively decorrelated but the ring-carboxyl dihedral strongly
correlated from one frame to the next, so the syn/anti population split it
reports is approximate rather than a count of independent draws.
