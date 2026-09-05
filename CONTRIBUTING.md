# Contributing

Full guidance, rendered: <https://denolle-lab.github.io/metascience-and-AI/contributing.html>

This book is the Denolle Lab's shared workspace for the Fall 2026 metascience seminar. Notes,
readings, corrections, and recorded disagreements are all welcome.

## Never publish these

The repository is **public**. Before you commit, check that your change contains none of:

- **Journal PDFs or article full texts.** This book distributes links and metadata only. Put reading
  copies in `private/pdfs/`, which git ignores.
- **Unpublished data or results**, yours or a collaborator's, including figures from work in review.
- **Anything a collaborator, student, or reviewer has not agreed to make public.** The case exercises
  ask people how their own projects really went. That material belongs in the private group notes.
- **Anything from `private/`.** It holds the parallel analysis, is excluded by `.gitignore`, and
  `tools/validate.py` fails if that ignore rule is missing. Do not defeat either guard.

Ask before committing rather than after. A commit that reaches public history is not fully undone by
a later deletion.

## The usual changes

| You want to | Edit |
|:--|:--|
| Record what was said at a meeting | `notes.qmd` — signed, dated, under your meeting |
| Suggest a reading | `references.bib` **and** `curriculum.json` **and** `suggested-readings.qmd` |
| Add an agent system or benchmark | a table row in `prior-art.qmd`, with a DOI or arXiv ID |
| Change what is assigned | `curriculum.json` **and** the session `.qmd` **and** `READING-AUDIT.md` — open an issue first |

The "Edit this page" link in the right margin of any page opens it on GitHub and turns your edit into
a pull request, with no local clone needed.

## Check before pushing

``` bash
python3 -m venv .venv
.venv/bin/pip install PyYAML
.venv/bin/python tools/validate.py
quarto render
```

A virtual environment rather than a plain `pip install`, because recent macOS and Linux Pythons
refuse to install into the system interpreter. `.venv/` is gitignored.

`validate.py` checks chapters, local links, citation keys, the thirteen-Tuesday schedule, and that
`references.bib` and `curriculum.json` describe the same set of works, then runs a Pandoc citation
pass that fails on any warning. The same checks run on every pull request.

Changed a reference or added a prior-art row? Also run `.venv/bin/python tools/check_links.py`, which
verifies every DOI against Crossref and fetches every other URL.

## Style

Match the surrounding pages: state what a source does and does not establish, label reconstruction as
inference, keep claims proportionate to what was shown, and prefer "no precedent located within this
search" to "never done before".
