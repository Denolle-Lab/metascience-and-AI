# MetaScience, Scientific Inquiry, and Agents

Working Quarto book, v0.4. Thirteen one-hour meetings for the Denolle Lab, taken one at a
time in the order below rather than on fixed dates.

**Published at <https://denolle-lab.github.io/metascience-and-AI/>**

Scientific advance is the primary outcome: warranted gains in knowledge, understanding, and
research capability. We study plural geoscientific inquiry through philosophy, history, and the
science of scientific process and impact, then design agents around human-defined modes and
evaluate them against past work. Novelty, correctness/warrant, and impact inform the assessment;
interdisciplinary integration is a candidate contributor to advance.

One anchor and one companion per meeting keep participation light. The convenor authorized the
v0.4 revision; the mode definitions and evaluation instruments remain drafts for discussion.

## Contents

| Path | What it is |
|:--|:--|
| `index.qmd` | Rationale, schedule, standing questions |
| `glossary.qmd` | Working definitions of the modes of inquiry and of the terms the quarter measures; meeting 1 revises it |
| `unit.qmd` | The unit of inquiry: deduction, induction, abduction; the hypothetico-deductive schema and its verbs; the thinkers who fixed them; one graph on which Platt's loop and Cleland's objections are placed |
| `agents/skills/unit-of-inquiry/SKILL.md` | The unit graph as an agent skill: state, one rule per node with its source, three compositions of units, required outputs, planted-flaw tests; every meeting's page ends by saying what its papers change here |
| `metrics.qmd` | Registry of what the measurement literature found useful for novelty, impact, breadth, and advance, with data, findings, stated limitations, and the basis each entry rests on; how the club tests the metrics against its own judgments; the embedding-era revisit |
| `tools/indicators.py` | Computes citations, field percentile, the CD_5 disruption index, and the sleeping-beauty coefficient for the assigned papers from OpenAlex, into `private/indicators.json` |
| `sessions/` | One chapter per meeting, thirteen of them |
| `rubrics.qmd` | Inquiry, novelty, advance, and evaluation worksheets |
| `prior-art.qmd` | Registry of existing science agents and benchmarks, and what their scores do not establish |
| `corpus-study.qmd` | Design for coding the mode of inquiry of published papers and relating it to impact, novelty, interdisciplinarity, and depth |
| `agent-design.qmd` | Versioned modes, procedures, claim records, implementation status, and fair agent comparisons |
| `bibliography.qmd` | Every reading by meeting with links and access notes, the group's suggestions, and the full reference list; the reading lists are generated from `curriculum.json` |
| `modes/` | Authoritative human-editable mode specifications, exported for agent use |
| `historical-evaluation.qmd` | Decision reconstruction, reproduction/reassessment, and extension/transfer cases |
| `templates/claim-record.json` | Empty claim-record template; no experimental result |
| `agents/mode-instructions.json` | Generated mode instructions with source hashes; not an agent runtime |
| `tools/export_modes.py` | Regenerates and checks the instruction export |
| `review/` | Dated audits, convergence plans, and source-check evidence |
| `notes.qmd` | The group's meeting record — add yours |
| `contributing.qmd` | How to contribute, and what must never be published here |
| `references.bib` | Bibliographic records; current counts are reported by the validator |
| `curriculum.json` | Editorial metadata for sessions and references. Kept in step with the `.qmd` files by hand; `validate.py` checks that the citation keys agree |
| `READING-AUDIT.md` | Why the reading selections are what they are |
| `PLAN-AUDIT.md` | September 2026 audit of the plan against the seminar's aims, and the reasoning behind the expanded optional extensions |
| `tools/validate.py` | Source, schedule, link, and citation checks, including that the generated reading lists are current |
| `tools/build_bibliography.py` | Regenerates the reading lists in `bibliography.qmd` from `references.bib` and `curriculum.json` |
| `tools/select_dois.py` | Selects exact-size citation-balanced DOI cohorts by keywords, disciplines, journals and dates; freezes the cohort and appends citation snapshots. See `tools/select_dois_README.txt` |
| `tools/nature_dataset.py` | Coordinates one fixed topic/date protocol across equal-size journal samples, preflights every citation band, freezes a complete combined cohort, and runs XML downloads/citation follow-up. See `tools/nature_dataset_README.txt` |
| `tools/download_nature.py` | Retrieves validated full-text JATS XML by DOI through Springer Nature OA or licensed Full Text APIs. See `tools/nature_workflow_README.txt` for six Nature journal presets, availability checks and citation follow-up |
| `tools/download_wiley.py` | Downloads Wiley article PDFs from a TXT/CSV DOI list using a TDM token, with rate limits, resumable downloads, and a results log in `private/pdfs/wiley/` |
| `tools/fetch_open_copies.py` | Fetches legal open-access copies of the references into the gitignored `private/pdfs/` and writes `private/reading-copies.md` |
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
.venv/bin/python tools/export_modes.py
.venv/bin/python tools/build_bibliography.py
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
no unpublished data, nothing a collaborator has not agreed to share, and nothing from `private/` except the roadmap data release, which `tools/roadmap/g22_release.py` builds into `data/roadmap-release/` (codings with quotes, derived tables, figure provenance; no paper texts, abstracts or review texts; per-paper records of the papers in human coding held back until that coding is done).

`private/` is where the parallel agent analysis lives. It is gitignored, and `validate.py` fails if
that ignore rule is removed or if private material is registered as a chapter.

## Reading access and rights

Every assigned paper has an external DOI, publisher, repository, or proceedings link, and some full
texts require institutional access. No journal PDFs are redistributed here. Free access is not
permission to republish; check the license and preserve attribution before adding any third-party
asset.

For a citation-balanced study corpus, use `tools/select_dois.py`. Its default draws
an equal number from each of ten OpenAlex citation-percentile bands, normalized by
year, work type and primary subfield. `--n` must be a multiple of ten. It supports
keyword, journal/source, discipline, publication-date and citation filters, stores
selection probabilities, and appends citation observations for the frozen cohort.
See [the selection instructions](tools/select_dois_README.txt) for name lookups,
examples, citation follow-up and the weighting needed for population estimates.

For the complete Nature dataset workflow, start with
[`templates/nature-dataset.example.json`](templates/nature-dataset.example.json)
and `tools/nature_dataset.py`. The script applies one topic query, fixed publication
start/end dates and equal N per journal, balances normalized citation bands within
each journal, checks all journals before sampling, and freezes the combined cohort
only when every journal succeeds. Downloads share one request budget and citation
refresh uses the same fixed manifest. See the
[study instructions](tools/nature_dataset_README.txt).

For Nature journals, `select_dois.py` includes verified presets for Nature Geoscience,
Nature Communications, Communications Earth & Environment, Nature Reviews Earth &
Environment, Nature Water and Nature Sustainability. `--availability-only` checks
all citation-band counts before drawing a sample; `--work-type review` includes review
articles explicitly. `tools/download_nature.py` retrieves JATS XML with a separately
activated Springer Nature Open Access or licensed Full Text API credential. See the
[Nature workflow](tools/nature_workflow_README.txt) for the chosen design of equal N per journal with citation balance within
each journal, access setup, a one-DOI pilot and preserving the fixed cohort during follow-up.

For a Wiley DOI list (one DOI per line, or a CSV with a `doi` column), use the dedicated
TDM downloader. It uses Python 3.10+ with no additional packages and prompts privately
for your Wiley token, or reads `WILEY_TDM_TOKEN` / `TDM_API_TOKEN` from the environment:

``` sh
python3 tools/download_wiley.py private/dois.txt --dry-run
python3 tools/download_wiley.py private/dois.txt --limit 1
python3 tools/download_wiley.py private/dois.txt
```

Downloads and `results.csv` default to the ignored `private/pdfs/wiley/` folder.
Rerun to skip existing PDFs. Run from a public IP Wiley recognizes for institutional
access; browser sign-in alone does not give Python that access. The standard TDM
service supplies PDFs; ask `tdm@wiley.com` about XML/HTML delivery for a DOI corpus.
See [Wiley's TDM instructions](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining).

## Running the Python tools

The selection, download, coding, and analysis scripts in `tools/` run in one conda environment. Results, PDFs, and credentials stay under the ignored `private/` folder and `~/.config/metascience/`; nothing from them enters Git except the roadmap data release in `data/roadmap-release/`, which `tools/roadmap/g22_release.py` builds under the rules in `tools/roadmap/README.md`.

### Set up the environment (any machine)

``` sh
git clone git@github.com:Denolle-Lab/metascience-and-AI.git
cd metascience-and-AI
mamba env create -f environment.yml        # or: conda env create -f environment.yml
conda activate metascience
```

`environment.yml` installs Python 3.12, PyYAML, Matplotlib, poppler (for `pdftotext`), and the `anthropic` SDK. Without conda: `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`, then install poppler (`brew install poppler` on macOS, `sudo apt install poppler-utils` on Debian or Ubuntu).

Check that everything works before a real run (no network needed):

``` sh
python -m unittest discover -s tools -p "test_*.py"                      # selection and download tools (70 tests)
PYTHONPATH=tools python -m unittest discover -s tools/ai_readiness/tests  # AI-readiness module (61 tests)
python tools/validate.py                                                 # the book's sources and links
```

### Credentials

Keep every key in `~/.config/metascience/keys.env`, one `NAME=value` per line, readable only by you (`chmod 600`). The names the scripts read:

| Variable | Used by |
|:--|:--|
| `OPENALEX_API_KEY` | `select_dois.py`, `nature_dataset.py`, `corpus.py` |
| `WILEY_TDM_TOKEN` | `download_wiley.py`, `fetch_pdfs.py` (Wiley, including AGU journals) |
| `ELSEVIER_API_KEY`, `ELSEVIER_INSTTOKEN` | `fetch_pdfs.py` |
| `SPRINGER_OA_API_KEY` or `SPRINGER_TDM_API_KEY` | `download_nature.py` |
| `ANTHROPIC_API_KEY` | `code_papers.py` (or run `ant auth login` once instead) |
| `UNPAYWALL_EMAIL`, `S2_API_KEY` | `fetch_pdfs.py`, optional |

`fetch_pdfs.py`, `code_papers.py`, and `corpus.py` read the file themselves. For the other scripts, load it into the shell first:

``` sh
set -a; . ~/.config/metascience/keys.env; set +a
```

### Run on a remote machine

Use a machine on the UW network, such as a lab workstation or a departmental server. Publisher text-and-data-mining APIs (Wiley, Elsevier, Springer Nature) grant subscription access by the machine's UW IP address; a commercial cloud machine will not get that access, and copying subscription PDFs to it raises the licence questions in `agents/coder/RUNBOOK.md`. The coding itself (`code_papers.py`) runs on Anthropic's servers, so the remote machine only fetches, uploads, waits, and collects.

1. **Connect.** Off campus, start the UW VPN (Husky OnNet) first. Create a key once on your laptop and copy it to the machine:

   ``` sh
   ssh-keygen -t ed25519                      # once, on your laptop; accept the default path
   ssh-copy-id you@machine.example.washington.edu
   ```

   Then add an entry to `~/.ssh/config` on your laptop so `ssh lab` is enough:

   ```
   Host lab
       HostName machine.example.washington.edu
       User you
       ForwardAgent yes
   ```

   `ForwardAgent yes` lets the remote machine use your laptop's key for GitHub, so no key needs to be stored there.

2. **Install conda on the machine** if it has none (no administrator rights needed):

   ``` sh
   ssh lab
   curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
   bash Miniforge3-Linux-x86_64.sh -b -p ~/miniforge3 && ~/miniforge3/bin/conda init && exec $SHELL
   ```

3. **Get the code and the environment**, as in "Set up the environment" above (`git clone`, `mamba env create`, `conda activate metascience`, run the tests).

4. **Copy the private material and the credentials from your laptop.** The private repository is not pushed anywhere, so copy it directly:

   ``` sh
   rsync -av --exclude pdfs/ private/ lab:metascience-and-AI/private/     # run in the repo on your laptop
   ssh lab 'mkdir -p ~/.config/metascience && chmod 700 ~/.config/metascience'
   scp ~/.config/metascience/keys.env lab:.config/metascience/keys.env
   ssh lab 'chmod 600 ~/.config/metascience/keys.env'
   ```

5. **Run long jobs inside `tmux`**, so they survive a closed laptop or a dropped VPN:

   ``` sh
   ssh lab
   tmux new -s fetch                          # a named session
   conda activate metascience && cd metascience-and-AI
   set -a; . ~/.config/metascience/keys.env; set +a
   python tools/select_dois.py select --name earth-pilot --n 200 --field 19 --from 2015-01-01 --to 2020-12-31 --seed 2026
   python tools/fetch_pdfs.py add-manifest private/corpus/earth-pilot.jsonl && python tools/fetch_pdfs.py run
   # Ctrl-b then d detaches; the job keeps running. Later: ssh lab, then tmux attach -t fetch
   ```

   The coding steps follow `agents/coder/RUNBOOK.md` (pilot of 20 papers first, then `code_papers.py submit`, `collect --wait`, `cost`).

6. **Bring results back to your laptop.** Codings, manifests, and summaries are small; PDFs can stay on the machine.

   ``` sh
   rsync -av --exclude pdfs/ lab:metascience-and-AI/private/ private/     # run in the repo on your laptop
   ```

On a shared cluster (for example UW Hyak), run downloads from a node that has internet access and is allowed to run long jobs; login nodes are usually not, and compute nodes may have no outbound network. Check the cluster's documentation before starting a multi-hour fetch.

Course content is CC BY 4.0 and `tools/` is MIT; see [LICENSE](LICENSE). Rights in the cited papers
remain with their holders.

## Validation status

See [VALIDATION.md](VALIDATION.md).

## Documentation

- Book structure: <https://quarto.org/docs/books/book-structure.html>
- Book output: <https://quarto.org/docs/books/book-output.html>
- GitHub Pages: <https://quarto.org/docs/publishing/github-pages.html>
- Citations: <https://quarto.org/docs/authoring/citations.html>
