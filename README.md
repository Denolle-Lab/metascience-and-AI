# MetaScience, Scientific Inquiry, and Agents

Working Quarto book, v0.3. Thirteen one-hour meetings for the Denolle Lab, taken one at a
time in the order below rather than on fixed dates.

**Published at <https://denolle-lab.github.io/metascience-and-AI/>**

An exploratory quarter: the group reads its way through how experimental, observational,
historical, and theoretical research actually proceeds, then asks what follows for the design and
evaluation of agents for science. Meeting 11 takes up one such proposal: that agents let a researcher work competently across more fields, making individual polymathy practical again. The seminar puts it as a question and says what would count against it.

## Contents

| Path | What it is |
|:--|:--|
| `index.qmd` | Rationale, schedule, standing questions |
| `glossary.qmd` | Working definitions of the modes of inquiry and of the terms the quarter measures; meeting 1 revises it |
| `sessions/` | One chapter per meeting, thirteen of them |
| `rubrics.qmd` | Inquiry, novelty, advance, and evaluation worksheets |
| `prior-art.qmd` | Registry of existing science agents and benchmarks, and what their scores do not establish |
| `corpus-study.qmd` | Design for coding the mode of inquiry of published papers and relating it to impact, novelty, interdisciplinarity, and depth |
| `bibliography.qmd` | Every reading by meeting with links and access notes, the group's suggestions, and the full reference list; the reading lists are generated from `curriculum.json` |
| `notes.qmd` | The group's meeting record — add yours |
| `contributing.qmd` | How to contribute, and what must never be published here |
| `references.bib` | 113 records: 26 paired papers, 5 discussant papers, 65 optional extensions, 17 papers cited by the glossary and the corpus study |
| `curriculum.json` | Editorial metadata for sessions and references. Kept in step with the `.qmd` files by hand; `validate.py` checks that the citation keys agree |
| `READING-AUDIT.md` | Why the reading selections are what they are |
| `PLAN-AUDIT.md` | September 2026 audit of the plan against the seminar's aims, and the reasoning behind the expanded optional extensions |
| `tools/validate.py` | Source, schedule, link, and citation checks, including that the generated reading lists are current |
| `tools/build_bibliography.py` | Regenerates the reading lists in `bibliography.qmd` from `references.bib` and `curriculum.json` |
| `tools/check_links.py` | Verifies every DOI against Crossref and fetches every other URL |
| `tools/stage_site.py` | Fallback: copies a rendered book into a subdirectory of a local Jekyll checkout. Not the current publishing path |

## Build locally

Install the Quarto CLI from <https://quarto.org/docs/get-started/>. The book has no executable code
cells and needs no Jupyter kernel, R, or Julia.

``` sh
quarto preview      # live reload while editing
quarto render       # writes _book/
```

The source checks need Python 3 and PyYAML. On a system with an externally managed Python, which covers recent macOS and most Linux distributions, use a virtual environment rather than `pip install` into the system interpreter:

``` sh
python3 -m venv .venv
.venv/bin/pip install PyYAML
.venv/bin/python tools/validate.py
.venv/bin/python tools/check_links.py
```

`.venv/` is gitignored. `validate.py` checks that every chapter exists, that local links and
citation keys resolve, that the thirteen meetings are numbered in order, that `references.bib`
and `curriculum.json` describe the same set of works, and that no private material is registered as a
chapter; it then runs a Pandoc citation pass that fails on any warning. `check_links.py` is slower and
hits the network, so run it when you have changed references rather than on every edit.

## Publishing

Pushing to `main` triggers `.github/workflows/publish.yml`, which validates the sources, renders, and
publishes to the `gh-pages` branch. Pull requests run validation and a render without publishing.
There is nothing to run by hand.

`tools/stage_site.py` remains for the alternative of copying a rendered build into the group's Jekyll
site at `denolle-lab.github.io`. That is not how this book is published and the script is kept only as
a fallback.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: this repository is public, so no journal PDFs,
no unpublished data, nothing a collaborator has not agreed to share, and nothing from `private/`.

`private/` is where the parallel agent analysis lives. It is gitignored, and `validate.py` fails if
that ignore rule is removed or if private material is registered as a chapter.

## Reading access and rights

Every assigned paper has an external DOI, publisher, repository, or proceedings link, and some full
texts require institutional access. No journal PDFs are redistributed here. Free access is not
permission to republish; check the license and preserve attribution before adding any third-party
asset.

Course content is CC BY 4.0 and `tools/` is MIT; see [LICENSE](LICENSE). Rights in the cited papers
remain with their holders.

## Validation status

See [VALIDATION.md](VALIDATION.md).

## Documentation

- Book structure: <https://quarto.org/docs/books/book-structure.html>
- Book output: <https://quarto.org/docs/books/book-output.html>
- GitHub Pages: <https://quarto.org/docs/publishing/github-pages.html>
- Citations: <https://quarto.org/docs/authoring/citations.html>
