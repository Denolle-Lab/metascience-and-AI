# Roadmap data release

Data, model codings, figures and reports of the roadmap study in this repository (how Earth-science papers move
through the inquiry graph v0.4.2, coded by a language model under codebook 1.5.0). Built on 2026-10-27 by
`tools/roadmap/g22_release.py` from the private working tree (public commit 3b4b2d5, private commit abf4cf7+uncommitted).
268 files, 24.6 MB. `RELEASE.json` lists every file with its sha256 and size.

The folder mirrors the layout of the private tree (`private/` in the scripts' docstrings and provenance blocks is this
folder), so every path written as `private/...` in a report or provenance block is found here without the `private/`
prefix.

## What is here

| Path | Content |
|:--|:--|
| `data/roadmap/derived/` | every derived table: the 2022 pool and preselection (OpenAlex metadata, no abstracts), eligibility screen decisions, gold set, metrics, round-1 and round-2 manifests, first-calculation results (g13), outcomes (g17), topics and journals (g20), entry-state evaluation (g21), open-review index and visibility labels (g16), report numbers (g19), format test (f01) |
| `data/roadmap/figures/paper/` | paper figures fig01-fig13 as PNG, each with its provenance JSON (inputs with sha256, numbers drawn, draft caption) |
| `data/roadmap/{EXPERIMENTS,DECISIONS,MANIFEST}.md` | experiment log, every selection rule and exclusion, one row per script run |
| `analysis/codings/api/<tag>/` | the model codings, one JSON per paper: `calc1` round 1, `gold-r2` second coding of the gold papers (test-retest), `calc1-review` papers with open review, `fmt-*` format test |
| `analysis/codings/api/state.json` | batch log of the coding runs: batches, per-paper cost and tokens, Files API ids |
| `download-queue.json`, `data/roadmap/download-queue.before-refetch-2026-10-27.json` | full-text fetch state of the roadmap papers (DOI, status, route, file name, title, year, venue), now and on October 27, 2026; the scripts read them to know which papers had full text |
| `text/`, `analysis/` | the reports: `text/report-roadmap.md`, `text/report-section-entry-state.md`, `text/report-review-visibility.md`, `analysis/entry-state-evaluation.md`, `analysis/roadmap-plurality-loops.md`, `analysis/roadmap-inquirygraph.md` |

## What is not here, and why

| Withheld | Why |
|:--|:--|
| Paper full texts (PDF, publisher XML, extracted text) | publishers' terms: we quote papers, we do not republish them |
| Abstracts (eligibility screen input) | same reason |
| Open-review discussion texts and the excerpts given to the visibility coder | same reason |
| The raw OpenAlex cache | size; every query can be refetched from OpenAlex |
| The human-coder app and its packets, who codes what | part of the blind human coding |
| Per-paper records of the 90 papers under embargo (below) | blinding |
| Figure PDFs | the repository does not carry PDFs; PNG and provenance JSON are here |

Quotes. A field that quotes a paper (`quote`, `entry.evidence`) is cut to 25 words, the codebook limit, with " [...]"
appended; 64 quotes were longer. The marker keeps such a coding invalid under `tools/check_coding.py`, as it was,
so reruns use the same papers. Separate strings of one coding that continue each other in the paper (a V-check quote
that picks up where a step quote stops) are cut where together they would pass 25 words; 419 strings were
shortened this way, with " [...] " where words were removed. Every string in the release was then compared with every
paper text, open-review file and abstract we hold: no verbatim passage, single or chained, is longer than 25 words,
except bibliographic titles and citation strings. Taken together, the quotes and coded fields of this release reproduce
a median of 3.9% of the words of a coded paper's text and at most 22.8% (180 paper texts with any 12-word
match; an upper bound, since paraphrased fields that share 12 words with the paper count too).

## Embargo

40 papers will be coded by four people (derived/gold/human_assignment.json, not released) and 60 papers
were drawn for the entry-state audit, which may also go to them (10 papers are in both: 90 in all). Until
their coding is done, no per-paper record of these papers is released: their coding files, their rows in the derived
tables (the pool and preselection files included: `pool.json` holds 14,133 of 14,223 rows), the audit rows and blind
re-codings, and the sentences in the reports that name or describe them. In `state.json` their cost, token and
validation entries are kept under pseudonyms (`withheld-001`, ...) so that total spend reproduces.

Aggregates computed over many papers (results.json, outcomes.json, entry_state.json, topics_journals.json and the
figures) are released as computed on the full set; they include these papers. One consequence: a table cell of such an
aggregate minus the released per-paper records of the same cell gives the embargoed papers' distribution in that cell.
For the model's entry state, where 78% of round-1 papers are `problem`, a few small cells (a subfield or publisher
family with 4 or 5 embargoed papers) contain only `problem` papers, so the model's label of those papers can be inferred.
The embargo hides the model's per-paper coding from the human coders; it does not hide aggregates. The embargo lifts
when the four coders have finished; the release is then rebuilt with `python tools/roadmap/g22_release.py
--lift-embargo` and the withheld records appear.

## Rerunning the analyses

Copy the folder first: reruns overwrite outputs and append to MANIFEST.md, and the released outputs are the full-set
record, which a rerun from this folder cannot reproduce while the embargo holds. From the repository root, with the
conda environment of the repository:

```sh
cp -r data/roadmap-release /tmp/roadmap-rerun
METASCIENCE_PRIVATE=/tmp/roadmap-rerun python tools/roadmap/g13_calc1_results.py
METASCIENCE_PRIVATE=/tmp/roadmap-rerun python tools/roadmap/g17_outcomes.py
```

`METASCIENCE_PRIVATE` points the scripts at a private tree (default `private/`); a relative path is read from the
current directory. While the embargo holds, reruns use the papers released here, so their numbers differ from the
reports, which used all coded papers. g22 ran g13 and g17 on a copy of this release when it built it; a correct rerun
gives:

| Number | Released (all coded papers) | Rerun from this release |
|:--|:--|:--|
| g13 papers coded (round 1, valid) | 233 | 144 |
| g13 eligible papers | 525 | 435 |
| g13 coverage | 0.44 | 0.33 |
| g13 test-retest pairs | 50 | 7 |
| g13 entry state problem (papers, share) | [181, 0.78] | [121, 0.84] |
| g17 papers | 233 | 144 |
| g17 tests | 245 | 234 |
| g17 tests with q < 0.1 | 15 | 2 |

Scripts that fetch or read full texts (f00, f01, g08, g10, g15, the coding runs) need the withheld files and do not run
from the release.

Checked on October 27, 2026 against a copy of the release (embargo on):

| Runs | Does not run, and what it needs |
|:--|:--|
| g13_calc1_results, g17_outcomes, g21_entry_state (without its blind-audit section, withheld); fig01, fig02 (fig02 counts PDFs on disk, of which the release has none), fig04, fig07, fig08, fig09, fig10; fig11 and fig12, which draw the released full-set topics_journals.json against the released codings and report that as a data issue (`make_all.py` prints "ok (stale input)") | g19_report_numbers: stops at the open-model text route, which needs the PDFs and XML texts; later steps also read the reliability study (`analysis/reliability/`) and `analysis/success-set/loops/REPORT.md`, which are not part of the release |
| | g20_topics_journals: OpenAlex topic names come from the raw cache, which is not released; with network access it refetches them from OpenAlex |
| | fig03: the format-test papers are all under embargo; fig13: the blind audit is under embargo |
| | g14_papers_vs_agents, fig05, fig06: the agent codings of the reliability study (`analysis/reliability/`, not released) |

`tools/roadmap/figures/make_all.py` refreshes the book's `assets/roadmap/` figures only when it runs on the private tree;
with `METASCIENCE_PRIVATE` set it leaves them alone.

## Licence and citation

Data and text in this folder: CC BY 4.0 (see `LICENSE`, section 1). Code in `tools/`: MIT. Rights in the papers quoted
remain with their holders; a quotation here does not license reuse of the source.

Cite as: Denolle, M. (2026). *Roadmap data release: model codings of Earth-science papers on the inquiry graph*
(release of 2026-10-27, commit 3b4b2d5). Denolle Lab, University of Washington.
https://github.com/Denolle-Lab/metascience-and-AI/tree/main/data/roadmap-release
