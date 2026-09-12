# Unsupervised Learning for Molecular Systems

Companion code for the LiveCoMS Best Practices Guide ***Best Practices for Unsupervised Learning in Molecular Systems* (Article v1.0)**.

This is the first release of the code. Both it and the article were revised substantially in response to review before that release, so the notebooks here differ considerably from the ones circulated with the original submission.

This repository is not a collection of demonstrations. It is a set of tools for doing unsupervised analysis of molecular data defensibly, together with notebooks that show each recommendation applied to real data, including examples where it changes the answer.

The guiding idea, from Section 1 of the article, is that unsupervised learning carries no automatic error signal of the kind supervised learning provides, so the practitioner has to supply one deliberately. Null models, stability analysis, honest baselines and statistical tests are how that is done here.

---

## Start here

Three steps, in this order. Set aside an afternoon, most of it spent waiting for notebooks to run.

1. **Set up the environment** (below). If you have conda, `environment.yml`
   pins every version and resolves the dependencies for you.
2. **Get the data**: `python scripts/download_data.py`. It pulls about 250 MB
   from the original sources and rebuilds the example files, so give it a few
   minutes the first time. After that it's cached.
3. **Run the notebooks in order**, 04 through 10. Each builds on the last, and
   each opens by telling you what it needs, how long it takes, and what it is
   about to make go wrong.

Every metric a notebook prints is defined where it first appears, together with
how to tell whether the number you got is good, bad, or meaningless. That second
part is the one that is hard to look up anywhere else.

You don't need to read anything else in this repository to follow along. The two
scripts exist to fetch the data and to regenerate the article's figures, and both
are short enough to read if you are curious.

---

## Install

```bash
git clone https://github.com/rociomer/unsupervised-learning-molecules.git
cd unsupervised-learning-molecules

conda env create -f environment.yml && conda activate ulms
# or, with pip:  pip install -r requirements.txt

python scripts/download_data.py
```

There is no package to install. Everything a notebook needs is written in the
notebook itself, so you can read the code that produces each result instead of
tracing it into a library. That makes the notebooks longer and it is the point.

`environment.yml` pins exact minor versions and is the reproducible route.
`requirements.txt` is there if you would rather use pip. Either way you get
RDKit, ASE, scikit-learn and PyTorch, which between them cover every notebook.

`python scripts/download_data.py` fetches the four example data sets from their
original sources and builds the files the notebooks read. It pulls about 250 MB
the first time, mostly the MD17 trajectory, and caches it afterwards.

---

## The notebooks

Numbered to match the sections of the article, so you can go from a recommendation to a working implementation without searching. Each is executed end-to-end in continuous integration on every commit (see [What CI means here](#what-ci-means-here) below).

| notebook | article section | what it makes go wrong |
|---|---|---|
| [`04-data-curation-and-standardization`](notebooks/04-data-curation-and-standardization.ipynb) | §4 | duplicates that only become visible after stereochemistry is standardized away |
| [`05-splitting-and-leakage`](notebooks/05-splitting-and-leakage.ipynb) | §5 | a random split of an analogue-rich library that strands near-duplicates, and a scaffold split that barely helps; a scaler fitted before splitting |
| [`06-representations-and-baselines`](notebooks/06-representations-and-baselines.ipynb) | §6 | two descriptor sets that disagree about which molecules are neighbors |
| [`07-dimensionality-reduction`](notebooks/07-dimensionality-reduction.ipynb) | §7 | t-SNE producing a silhouette of 0.39 from **pure noise** |
| [`08-clustering`](notebooks/08-clustering.ipynb) | §8 | an "optimal" *k* found in data with no clusters |
| [`09-statistical-comparison`](notebooks/09-statistical-comparison.ipynb) | §9 | a naive comparison declaring a winner among identical methods |
| [`10-generative-models`](notebooks/10-generative-models.ipynb) | §10 | a latent space "organized by chemistry" that is organized by size |

Notebooks are committed **with outputs stripped**, which keeps diffs clean and reviewable. Run them yourself, or download the executed versions from the artifacts of the latest continuous-integration run (see below).

---

## What CI means here

**CI** is short for continuous integration. It is a
configuration file ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) listing checks
that GitHub runs for you. Every time anyone pushes a commit or opens a pull request, it
rents a fresh empty Linux machine, installs this project from scratch, and runs them. It
does the same once a week on a schedule.

There are three checks here:

| check | what it verifies |
|---|---|
| notebooks committed clean | no notebook was committed with its outputs stored in it |
| data builds | `scripts/download_data.py` still fetches and builds all four data sets |
| notebooks run | every notebook executes end to end, top to bottom |

The third one is the real check and the other two exist to make it possible. A notebook
that no longer runs is a broken claim, and running it is the only way to find out.

Why this matters for a scientific repository in particular: the machine is empty, so
*"it works on my laptop"* becomes checkable, and a package you installed two years ago and
forgot cannot silently prop the code up. The weekly run catches **dependency rot**, where
code that was correct when published stops working because a library changed underneath
it. Nobody has to touch the code for that to happen, and without a scheduled check nobody
notices until a reader complains.

A green tick next to the latest commit means all three passed on a clean machine. A red
cross means something is broken and you should not trust the current state of `main`.

GitHub's
[Understanding GitHub Actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions)
is a good short introduction. It is free for public repositories, and `ci.yml` here is
about seventy lines you are welcome to copy into your own project.

---

## Before you commit a notebook

Clear its outputs first. Notebooks are committed without them, so diffs show the code you changed and not a wall of re-encoded images. In Jupyter that is Kernel, then Restart Kernel and Clear Outputs of All Cells. CI checks this and fails if a notebook arrives with outputs stored in it.

---

## Contributing

This is a living document, and so is its code. The scope section of the article lists what is deliberately not yet covered (conditional generative modeling, coarse-graining, anomaly detection, active learning, agentic analysis) and contributions in those areas are especially welcome. See `CONTRIBUTING.md`.

If you find that one of our recommendations is wrong, please open an issue. That is the most useful contribution there is.

## Citation

See `CITATION.cff`, or use GitHub's *Cite this repository* button.

## License

MIT for the code (see `LICENSE`). The article itself is licensed separately by LiveCoMS.
