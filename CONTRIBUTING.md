# Contributing

This is a living document. The article records what it does not yet cover
(Section 13), and those gaps are the most valuable places to contribute:
conditional generative modeling, coarse-graining, anomaly detection and
applicability domain, active learning coupled to unsupervised exploration, and
agentic analysis.

## Ways to contribute, in rough order of usefulness

1. **Tell us a recommendation is wrong.** Open an issue with the evidence. A
   best-practices guide should be able to be corrected/updated giving improvement in practices over time.
2. **Contribute a worked example** that demonstrates a failure mode we describe
   but do not illustrate.
3. **Contribute a missing section**, ideally with an accompanying notebook.
4. **Report a reference that is wrong, outdated, or superseded.** Several
   entries in the manuscript bibliography carry a `% TO VERIFY` comment;
   confirming or correcting one of those is a real help.
5. **Fix a bug in the code.**

## Ground rules for new recommendations

Because this is a best-practices document rather than a review, a new
recommendation needs more than a citation:

- It must be **actionable**: a reader should be able to tell whether they have
  followed it.
- It must be **supported**, ideally by published evidence. Where the community
  disagrees, say so and represent the positions fairly rather than picking one.
- Where practical, it should come with a **worked example** in a notebook, so a
  reader can see the advice applied to real data.

## Opening a pull request

If you have never opened a pull request before, this is the whole process. A pull
request, or PR, is a proposed set of changes that we can read, discuss, and refine
before it becomes part of the repository. Nothing you do on your own copy touches
the main repository until a PR is reviewed and merged, so you cannot break anything
by trying.

### If you only want to flag something

You do not need a pull request to raise a problem. Open an issue on the repository's
**Issues** tab describing what you found, with a pointer to the file, figure, or line.
For co-authors reviewing the repository, an issue, or a comment on an open PR, is
often the fastest way to record a concern without editing files yourself.

### The quick route, for a one-line text or reference fix

For a small correction, such as a wrong reference, a typo, or a broken link, you do
not need to install anything. On the file's page on GitHub, click the pencil icon
("Edit this file"), make the change, and at the bottom choose "Create a new branch
for this commit and start a pull request." GitHub walks you through the rest, and
this is the right route for most review comments that already come with a concrete
fix.

### The full route, for code, notebooks, or a new section

1. **Get a copy you can push to.** Co-authors and collaborators with write access can
   clone the main repository directly and skip to step 2. Everyone else clicks
   **Fork** at the top right of the GitHub page to create a copy under their own
   account, then clones that fork:
   ```bash
   # collaborators:
   git clone https://github.com/rociomer/unsupervised-learning-molecules.git
   # everyone else, after forking:
   git clone https://github.com/YOUR-USERNAME/unsupervised-learning-molecules.git
   cd unsupervised-learning-molecules
   ```
2. **Set up the environment** (the same two commands as under "Practical steps"):
   ```bash
   conda env create -f environment.yml && conda activate ulms
   python scripts/download_data.py
   ```
3. **Make a branch** with a short, descriptive name, so your change stays isolated
   from `main`:
   ```bash
   git checkout -b fix-tanimoto-caption
   ```
4. **Make your change.** If you touched a notebook, run it top to bottom and then
   clear its outputs, for the reasons under "Practical steps" below.
5. **Commit and push** to your branch:
   ```bash
   git add -A
   git commit -m "Fix the Tanimoto size-bias caption in notebook 08"
   git push -u origin fix-tanimoto-caption
   ```
6. **Open the PR.** After the push, GitHub prints a link you can click, or go to the
   repository on GitHub and press "Compare & pull request." Point it at the `main`
   branch of `rociomer/unsupervised-learning-molecules`, and in the description say
   what you changed and why; if you changed a figure the article uses, give its
   figure number.

With the GitHub CLI installed, steps 5 and 6 shorten to `git push -u origin <branch>`
followed by `gh pr create`.

## Practical steps

```bash
conda env create -f environment.yml && conda activate ulms
python scripts/download_data.py
```

- Code that a reader should learn from goes **in the notebook**, not in a module
  they have to open separately. The notebooks are longer for it, which is the
  trade we want.
- Clear notebook outputs before committing (Kernel, then Restart Kernel and
  Clear Outputs of All Cells). CI fails if outputs are committed.
- Run the notebook you changed, top to bottom, before pushing. CI runs all of
  them, so a notebook that only works from the middle will be caught anyway.
- If you change a figure the article uses, say which figure number in the pull
  request, and regenerate it with `python scripts/make_manuscript_figures.py`.

## Authorship

Contributors whose input changes the article will be acknowledged. Substantial
contributions may warrant authorship on a future version, in line with LiveCoMS
policy on authorship of living documents.
