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
| 5 | `g05_select.py` | `gold_set.json`, `gold_set.md`, `gold_manifest.jsonl`: the frozen set |
| 6 | `tools/fetch_pdfs.py` | PDFs in `private/data/roadmap/pdfs/gold/` (gitignored) |

```bash
conda activate metascience
python tools/roadmap/g01_author_profile.py
python tools/roadmap/g02_pool.py
python tools/roadmap/g03_preselect.py --n 600 --seed 2026
python tools/roadmap/g04_metrics.py
python tools/roadmap/g05_select.py --n 100 --seed 2026
python tools/fetch_pdfs.py add-manifest private/data/roadmap/derived/gold/gold_manifest.jsonl
python tools/fetch_pdfs.py run --out private/data/roadmap/pdfs/gold
```

Keys are read from `~/.config/metascience/keys.env` (see the main README). The fetcher records the route used for each paper; papers it cannot get are listed with links in `private/download-list.md`.
