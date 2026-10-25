# Roadmap scripts

Scripts for the research roadmap in `private/analysis/roadmap-plurality-loops.md`. The scripts are versioned here; everything they download or derive goes to `private/data/roadmap/` (the sealed private repository). Only results of the analysis are made public, never the downloaded data.

## Traceability rules

1. **Every number traces to a dated query.** All OpenAlex calls go through `common.openalex()`, which stores the verbatim response under `private/data/roadmap/raw/openalex/` with its URL (key removed) and retrieval time. A rerun reads the cache, so results do not drift when OpenAlex updates.
2. **Every run is logged.** `private/data/roadmap/MANIFEST.md` gets one row per script run: date, script, git commit, what was fetched or derived, record count, API calls and cache hits.
3. **Every choice is logged.** Selection rules, thresholds and exclusions are appended to `private/data/roadmap/DECISIONS.md` by the script that applies them, with the commit.
4. **Every derived table names its inputs.** JSON outputs carry a `_provenance` block: script, commit, date, input files, parameters (seeds, cut-offs).
5. **Every coded claim cites the paper.** Codings follow `agents/coder/CODEBOOK.md`: each step quotes the paper (25 words or fewer) with its page, so a result in the analysis traces back to the passage that supports it.
6. **Commit before you run.** The commit recorded in the logs is only meaningful if the scripts are committed; uncommitted runs are marked `+uncommitted`.

## Gold set (Phase 0)

About 100 research articles from 2022 near the convenor's research, spanning impact, novelty, breadth, and subfield, coded by two humans and by the model to measure coding reliability.

| Step | Script | Output in `private/data/roadmap/derived/gold/` |
|:--|:--|:--|
| 1 | `g01_author_profile.py` | `author_profile.json`: the convenor's OpenAlex topics, from her articles (ORCID) |
| 2 | `g02_pool.py` | `pool.json`: 2022 articles in her topics (core ring) and neighbouring Earth-science subfields (broad ring), in venues with a full-text route |
| 3 | `g03_preselect.py` | `preselect.json`: 600 papers, ring × impact quintile × subfield |
| 4 | `g04_metrics.py` | `metrics.json`: novelty proxy (topic-pair rarity), reference breadth, citer breadth (breadth v1) |
| 5 | `g05_select.py` (first pass, before screening; superseded by step 8) | first `gold_set.json` |
| 6 | `g06_abstracts.py` | `screen_input.json`, `screen_batches/`: abstracts of the 600 for screening |
| 7 | workflow `workflows/gold-eligibility-screen.js`, then `g07_eligibility.py` | `eligibility.json`: two independent model screeners per abstract, a third on disagreements |
| 8 | `g05_select.py` (rerun; reads `eligibility.json`) | `gold_set.json`, `gold_set.md`, `gold_manifest.jsonl`: the frozen set, eligible papers only |
| 9 | `tools/fetch_pdfs.py` | PDFs in `private/data/roadmap/pdfs/gold/` (gitignored) |
| 10 | `g08_fetch_status.py` | `fetch_status.json`: fetched or not, route, licence, and whether the paper may go to model coding now |
| 11 | `g10_fetch_xml.py` (`--reconvert` after a converter change) | `<key>.xml` and located text `<key>.xml.txt` beside the PDFs; `xml_status.json` |
| 12 | `g09_human_coding_app.py` | frozen `human_assignment.json` (40 papers, two coders each, 20 per coder); `private/data/roadmap/app/packets/<ID>/` (one per coder: app locked to that coder, PDFs, located texts, `my_codings/`, README) and `app/gold-coordinator.html` |
| 13 | `g11_human_agreement.py` | collects `my_codings/` into `derived/gold/human/<ID>/`; `human_agreement.json`: per-pair agreement and Krippendorff's alpha per field, against the 0.67 and 0.8 gates |

Tests: `python tools/roadmap/test_g11_alpha.py` (alpha reproduces the reliability run's 0.63); `node tools/roadmap/app/e2e_test.js` (two coders code a shared paper in headless Chrome; files validate; import of a co-coder's file is refused; the coordinator pairs them).

Format test (codebook 1.4.0): `f00_format_test_prep.py`, the workflow `workflows/format-test-coding.js`, batch-API arms via `tools/code_papers.py submit --tag fmt-P1 --no-xml` (and fmt-PX1 without `--no-xml`), then `f01_format_test.py`.

```bash
conda activate metascience
python tools/roadmap/g01_author_profile.py
python tools/roadmap/g02_pool.py
python tools/roadmap/g03_preselect.py --n 600 --seed 2026
python tools/roadmap/g04_metrics.py
python tools/roadmap/g06_abstracts.py
# run the workflow tools/roadmap/workflows/gold-eligibility-screen.js with args {"n_batches": 60}; save its result as JSON
python tools/roadmap/g07_eligibility.py RESULT.json --run-id wf_...
python tools/roadmap/g05_select.py --n 100 --seed 2026
python tools/fetch_pdfs.py add-manifest private/data/roadmap/derived/gold/gold_manifest.jsonl
python tools/fetch_pdfs.py run --out private/data/roadmap/pdfs/gold
python tools/roadmap/g08_fetch_status.py
python tools/roadmap/g10_fetch_xml.py
python tools/roadmap/g09_human_coding_app.py          # first time: --reassign; afterwards the assignment is frozen
python tools/roadmap/g11_human_agreement.py           # after coders return their my_codings folders
```

Keys are read from `~/.config/metascience/keys.env` (see the main README). The fetcher records the route used for each paper; papers it cannot get are listed with links in `private/download-list.md`.
