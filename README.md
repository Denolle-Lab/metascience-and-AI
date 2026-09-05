# MetaScience, Scientific Inquiry, and Agents

Working Quarto book, v0.3. Thirteen one-hour Tuesday meetings for the Denolle Lab,
September 8 – December 1, 2026, 1–2 PM America/Los_Angeles.

**Published at <https://denolle-lab.github.io/metascience-and-AI/>**

An exploratory quarter: the group reads its way through how experimental, observational,
historical, and theoretical research actually proceeds, then asks what follows for the design and
evaluation of agents for science. One proposal is tested rather than assumed — that agents let a
researcher work competently across more fields, making individual polymathy practical again.

## Contents

| Path | What it is |
|:--|:--|
| `index.qmd` | Rationale, schedule, standing questions |
| `sessions/` | One chapter per meeting, thirteen of them |
| `rubrics.qmd` | Inquiry, novelty, advance, and evaluation worksheets |
| `prior-art.qmd` | Registry of existing science agents and benchmarks, and what their scores do not establish |
| `reading-library.qmd` | Publisher, DOI, and proceedings links for every assigned paper |
| `notes.qmd` | The group's meeting record — add yours |
| `suggested-readings.qmd` | Readings the group adds during the quarter |
| `contributing.qmd` | How to contribute, and what must never be published here |
| `references.bib` | 39 records: 26 paired papers, 2 discussant papers, 11 optional extensions |
| `curriculum.json` | Editorial metadata for sessions and references. Kept in step with the `.qmd` files by hand; `validate.py` checks that the citation keys agree |
| `READING-AUDIT.md` | Why the reading selections are what they are |
| `tools/validate.py` | Source, schedule, link, and citation checks |
| `tools/check_links.py` | Verifies every DOI against Crossref and fetches every other URL |
| `tools/stage_site.py` | Fallback: copies a rendered book into a subdirectory of a local Jekyll checkout. Not the current publishing path |

## Build locally

Install the Quarto CLI from <https://quarto.org/docs/get-started/>. The book has no executable code
cells and needs no Jupyter kernel, R, or Julia.

``` sh
quarto preview      # live reload while editing
quarto render       # writes _book/
```

The source checks need Python 3 and PyYAML. On a system with an externally managed Python — recent
macOS and most Linux distributions — use a virtual environment rather than `pip install` into the
system interpreter:

``` sh
python3 -m venv .venv
.venv/bin/pip install PyYAML
.venv/bin/python tools/validate.py
.venv/bin/python tools/check_links.py
```

`.venv/` is gitignored. `validate.py` checks that every chapter exists, that local links and
citation keys resolve, that the thirteen meetings fall on consecutive Tuesdays, that `references.bib`
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

Course content is CC BY 4.0 and `tools/` is MIT — see [LICENSE](LICENSE). Rights in the cited papers
remain with their holders.

## Validation status

See [VALIDATION.md](VALIDATION.md).

## Documentation

- Book structure: <https://quarto.org/docs/books/book-structure.html>
- Book output: <https://quarto.org/docs/books/book-output.html>
- GitHub Pages: <https://quarto.org/docs/publishing/github-pages.html>
- Citations: <https://quarto.org/docs/authoring/citations.html>
