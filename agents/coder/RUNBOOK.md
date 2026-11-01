# Coding papers at scale: runbook

For coding 1,000 or more papers under the codebook (`CODEBOOK.md`, v1.2.0), with the scripts in `tools/`. Everything written goes under `private/` (a separate, unpushed repository); nothing here publishes data. For the roadmap codings, publication is a separate step: `tools/roadmap/g22_release.py` copies codings with quotes, derived tables and figure provenance into `data/roadmap-release/`, without paper texts, abstracts or review texts, and holds back per-paper records of the papers in human coding until that coding is done.

## 0. Before the first run

| Need | How |
|:--|:--|
| Python packages | `pip install anthropic` (the other scripts use the standard library; `pypdf` is not needed) |
| Claude credentials | `ant auth login`, or `export ANTHROPIC_API_KEY=...` |
| `pdftotext` | already at `/usr/local/bin/pdftotext`; used to check that each PDF is the paper |
| Optional, for full texts | `UNPAYWALL_EMAIL` (Unpaywall needs an email; none is sent without it), `WILEY_TDM_TOKEN` (Wiley text-and-data-mining token, covers AGU journals), `ELSEVIER_API_KEY` and optionally `ELSEVIER_INSTTOKEN` (from UW Libraries), `OPENALEX_API_KEY` |

**Licence check.** Open-access papers under CC BY can be sent to a model API. For subscription PDFs, check the University of Washington's licence with each publisher before sending them to a commercial model service; many text-and-data-mining licences restrict use with generative AI or third-party processing. `fetch_pdfs.py` records the route each file came by, so subscription files can be filtered out.

## 1. Build a corpus

```bash
# Nature and Science Earth-science research articles, 2005-2015, 1,000 drawn across citation deciles
python3 tools/corpus.py --name ns2005 --sources S137773608,S3880285 --years 2005-2015 --n 1000 --strata citation-decile
# Geoscience flagship journals by ISSN (GRL, JGR Solid Earth, EPSL, GJI, BSSA, WRR), 2010-2020
python3 tools/corpus.py --name geo2010 --issn 0094-8276,2169-9313,0012-821X,0956-540X,0037-1106,0043-1397 --years 2010-2020 --n 1000
```

Each run writes `private/corpus/<name>.jsonl` (one paper per line, with its stratum and citation metrics) and `<name>.meta.json` (the query, pool size, and seed). The Nature and Science pool for 2005 to 2015 holds about 1,700 qualifying papers, so a draw of 1,000 is most of it.

## 2. Get the full texts

```bash
python3 tools/fetch_pdfs.py add-manifest private/corpus/ns2005.jsonl
python3 tools/fetch_pdfs.py run            # about 5 requests per paper, 1 s between requests to one host
```

Papers it cannot fetch go into `private/download-list.md`, grouped by stratum, with APA citations and UW Libraries proxy links. PDFs saved anywhere under `~/Dropbox/ARTICLES/METASCIENCE/` are found on the next run by the DOI printed inside them. On the first run (66 papers) the open routes alone found 9; the Wiley and Elsevier tokens should raise that substantially for geoscience journals.

## 3. Pilot (do this before any large batch)

```bash
python3 tools/code_papers.py submit --limit 20 --tag pilot --dry-run   # count and rough cost
python3 tools/code_papers.py submit --limit 20 --tag pilot
python3 tools/code_papers.py collect --tag pilot --wait
python3 tools/code_papers.py cost --tag pilot                          # measured, from recorded usage
python3 tools/code_papers.py submit --keys <the same 20> --tag pilot-b # second independent run
python3 tools/check_coding.py agree-dir private/analysis/codings/api/pilot private/analysis/codings/api/pilot-b
python3 tools/check_coding.py agree-dir private/analysis/codings/agent private/analysis/codings/api/pilot
```

Include in the pilot the papers already coded by the Claude Code agent (`private/analysis/codings/agent/`) so the API coder can be compared with it.

**Go on to the full run only if:** every coding validates; test-retest agreement (pilot against pilot-b) reaches a node-set Jaccard of at least 0.7 and agreement on entry state and outcome in at least 80% of papers; and the measured cost per paper fits the budget. These thresholds are the seminar's, provisional.

## 4. Full run

```bash
python3 tools/code_papers.py submit --manifest private/corpus/ns2005.jsonl --tag ns2005-v1.1 --batch-size 200
python3 tools/code_papers.py collect --tag ns2005-v1.1 --wait     # batches finish within 24 hours, usually within 1
python3 tools/code_papers.py retry --tag ns2005-v1.1              # errored, expired, invalid, truncated
python3 tools/code_papers.py cleanup-files                        # delete uploaded PDFs afterwards
```

The tag names the corpus and codebook version; a codebook change gets a new tag, never an overwrite. State is in `private/analysis/codings/api/state.json`; every command can be rerun after an interruption.

## 5. Aggregate

```bash
python3 tools/aggregate_codings.py private/analysis/codings/api/ns2005-v1.1 --manifest private/corpus/ns2005.jsonl
```

Writes `papers.csv`, `transitions.csv`, `nodes.csv`, `tree.csv`, and `summary.md` to `private/analysis/codings/summary/`. The first comparison the seminar needs: do papers in the top citation deciles walk the tree differently from the bottom deciles (entry state, returns to a mode, use of H and D, outcome)?

## 6. Quality control throughout

- **Test-retest**: recode a random 5% under a second tag and report agreement with `check_coding.py agree-dir`.
- **Human check**: one human coding of at least four papers per corpus, with Cohen's kappa on entry state and outcome, before any count is cited.
- **Drift**: rerun the eight success papers under every new codebook version and compare.

## Cost and time (measured on the format test, October 25, 2026)

| Item | Assumption | Per paper | 1,000 papers |
|:--|:--|:--|:--|
| Input | about 2,300 tokens per PDF page (text plus page image), 10 to 20 pages, codebook cached | 23,000 to 46,000 tokens | |
| Output | about 10,000 tokens, thinking included | | |
| Price, estimated beforehand | Claude Opus 5.5, $4 input and $20 output per million tokens, batches at half price | about $0.15 to $0.20 | about $150 to $200 |
| Price, measured | 24 batch requests on six papers, effort high (`code_papers.py cost --tag fmt-P1` etc.): PDF alone $0.26 to $0.27; PDF plus the located XML text $0.34 to $0.39 | $0.27 to $0.39 | about $270 to $390 |

Long Methods sections or supplements can double the input. Batches finish within 24 hours. Fetching runs about one paper every 5 to 10 seconds.

## Change log

| Date | Change |
|:--|:--|
| 2026-10-25 | Measured cost from the format test replaces the estimate; the batch coder now puts the schema in the prompt (constrained decoding refused the schema as too large) |
| 2026-10-21 | First runbook: corpus builder, manifest queueing, Files API batches with state and retries, aggregation, pilot gates |
