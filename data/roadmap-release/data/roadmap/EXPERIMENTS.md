# Experiment registry

One entry per experiment of the roadmap. Each names its question, inputs, model, codebook, the script and commit
that produced it, the exact command, outputs, cost, and where the results are reported. Use it to rerun an
experiment, to rerun it with another model (see `agents/coder/HANDOFF.md` in the public repo), or to hand it off.

Conventions
- Public repo (`metascience-and-AI`, branch `framework-v0.5`, PR #2): code, codebooks, schemas, workflows, result pages.
- Private repo (`private/`, local only, never pushed): papers, codings, labels, derived tables, prose reports.
- Paths below are relative to the public repo root; `private/` is the private repo.
- Every script appends a line to `private/data/roadmap/MANIFEST.md` (date, script, commit, n) and selection rules
  go to `private/data/roadmap/DECISIONS.md`.
- Model for all Claude codings: `claude-opus-5-5`, Message Batches API, effort high, max output 32,000 tokens
  (retries 64,000). Cost figures are measured batch prices recorded per paper in
  `private/analysis/codings/api/state.json`.
- Round 1 (the 600-paper plan) runs with the default `ROADMAP_SET=gold ROADMAP_CALC=calc1`; round 2 with
  `ROADMAP_SET=r2 ROADMAP_CALC=r2calc`.

## Corpus construction (round 1)

| Step | Script | Output | n |
|:--|:--|:--|--:|
| Author profile from the convenor's publications | `tools/roadmap/g01_author_profile.py` | `derived/gold/author_profile.json` | |
| Candidate pool, 2022, OpenAlex | `g02_pool.py` | `derived/gold/pool.json` | 14,223 |
| Stratified preselection | `g03_preselect.py --n 600 --seed 2026` | `derived/gold/preselect.json` | 600 |
| Impact, novelty, breadth metrics | `g04_metrics.py` | `derived/gold/metrics.json` | 600 |
| Gold-set draw | `g05_select.py` (commit 6016ce0) | `derived/gold/gold_set.json` | 100 |
| Abstracts | `g06_abstracts.py` | `derived/gold/screen_input.json` | 600 |
| Double-blind eligibility screen | workflow `tools/roadmap/workflows/gold-eligibility-screen.js`, then `g07_eligibility.py` | `derived/gold/eligibility.json` | 525 eligible |
| Corpus manifest | `g12_calc1_manifest.py` | `derived/calc1/manifest.jsonl` | 525 |
| Full text | `tools/fetch_pdfs.py`, `g10_fetch_xml.py` | `private/data/roadmap/pdfs/`, `private/download-queue.json` | 235 PDF, 116 XML at the first calculation (October 25); later counts in E7 and `derived/report_numbers.json` |

## E0. Format test: does the input format change the coding?

- Question: PDF only, PDF plus XML text, XML text only: same coding?
- Inputs: 6 open-licence gold papers; codebook 1.4.0. Tags `fmt-P1`, `fmt-P2`, `fmt-PX1`, `fmt-PX2` (two replicates per arm).
- Scripts: `tools/roadmap/f00_format_test_prep.py`, `f01_format_test.py` (commit 1c9c11f); workflow `tools/roadmap/workflows/format-test-coding.js` for the text arms.
- Cost: $6.64.
- Result: format changes the coding no more than a repeat run does; quotes verifiable 100% from XML, 83% from PDF text.
- Outputs: `private/data/roadmap/derived/format_test/`.

## E1. First calculation: code the eligible papers once

- Question: what do Earth-science papers' workflows look like on the graph of inquiry?
- Inputs: `derived/calc1/manifest.jsonl`, papers with full text (235); codebook 1.5.0 (commit 01b7f78).
- Command: `python tools/code_papers.py submit --manifest private/data/roadmap/derived/calc1/manifest.jsonl --tag calc1 --max-usd 250`, then `collect --tag calc1`, `retry --tag calc1`.
- Script: `tools/code_papers.py` (commit 8c3337d).
- Outputs: `private/analysis/codings/api/calc1/` (233 valid of 235).
- Cost: $74.47 ($0.32 per paper).
- Analysis: `tools/roadmap/g13_calc1_results.py` (commit 49fb25e) → `derived/calc1/results.json`, `RESULTS.md`.

## E2. Test-retest of the model coder

- Question: does the model give the same coding twice?
- Inputs: 50 gold papers with full text, coded a second time independently; tag `gold-r2`; codebook 1.5.0.
- Command: as E1 with `--manifest` the gold papers and `--tag gold-r2`.
- Cost: $15.72.
- Result: node-set overlap 0.86, entry state 92%, outcome 100%, alpha decisive mode 0.83 (`derived/calc1/results.json`).

## E3. Open-review coding

- Question: what changes during peer review?
- Inputs: the 64 Copernicus papers among E1; open discussion fetched for 61 by `tools/roadmap/g15_open_review.py` (commit 8c3337d) into `private/data/roadmap/review/<key>/`.
- Command: `python tools/code_papers.py submit --manifest <calc1 manifest> --keys <61 keys> --tag calc1-review --review-dir private/data/roadmap/review --max-usd 250`; `collect`; `retry`.
- Outputs: `private/analysis/codings/api/calc1-review/` (58 valid).
- Cost: $26.76. The 61-paper batch took 15.6 hours (October 26).

## E4. Review visibility labelling

- Question: does the published paper show the review changes?
- Inputs: review sequences of E3; packets by `g16_visibility.py prep` (commit 4ff3f93) in `derived/review/visibility_input/`.
- Procedure: workflow `tools/roadmap/workflows/visibility.js`, two independent labelers per paper and one adjudicator, run as a 10-paper pilot (run wf_72fb1d3d-6c8), then 37 papers (wf_a78365bc-5a9), then 11 (wf_ef3c5579-dac). Labelers are Claude agents in Claude Code, not the batch API (no API cost).
- Analysis: `python tools/roadmap/g16_visibility.py analyze` → `derived/review/visibility_results.json`.
- Result: 0 of 580 changes marked as a revision; 560 as if planned; 20 absent; agreement 97%; 560 of 560 quotes found.
- Reports: public `review-visibility.qmd`; prose `private/text/report-review-visibility.md`.

## E5. Papers against agent loops

- Inputs: E1 codings; 31 agent loops coded under loop codebook 0.1.2 by the reliability study (`private/analysis/reliability/`).
- Script: `tools/roadmap/g14_papers_vs_agents.py` (commit 8c3337d) → `derived/calc1/papers_vs_agents.json`.

## E6. Workflow features against outcomes

- Inputs: E1 codings (233); `derived/gold/metrics.json`.
- Script: `python tools/roadmap/g17_outcomes.py` (commit 1e821d0) → `derived/outcomes/outcomes.json`, `OUTCOMES.md`.
- Result: 15 of 245 tests with q < 0.1; report `workflow-outcomes.qmd`.

## E7. Round 2: diversified open-access corpus (in progress, October 27)

- Question: do E1, E4 and E6 hold on a corpus spread over more journals and publishers?
- Draw: `python tools/roadmap/g18_round2_draw.py --n 300 --cap 4 --seed 2027` → `derived/r2/preselect.json`: 277 papers, 157 journals, 12 publishers, open access only, at most 4 per journal.
- Then, with `ROADMAP_SET=r2 ROADMAP_CALC=r2calc`: `g06_abstracts.py`, `g04_metrics.py`, eligibility screen (workflow `gold-eligibility-screen.js` with `args.dir = derived/r2/screen_batches`, run wf_9f4b0839-d9f), `g07_eligibility.py`, `g12_calc1_manifest.py` → `derived/r2calc/manifest.jsonl`; fetch; code with tag `r2`.
- Screen: 222 of 277 eligible; screeners agreed on 275 of 277. Excluded: off-topic 42, review 8, comment or reply 4, other 1.
- Fetch (October 27): PDF 153, XML 105 (Copernicus 40, Springer OA 65), text of either kind 154; 68 open-access papers not fetched (Elsevier 23, Wiley 16, AGU 11, Springer 8, BSSA 4, Science Advances 4, SRL 1, GJI 1).
- Coding: `python tools/code_papers.py submit --manifest private/data/roadmap/derived/r2calc/manifest.jsonl --tag r2 --max-usd 250` (October 27), 154 papers; spend before submission $123.59; dry-run estimate $107, about $52 at the measured $0.34 per paper. Then `collect --tag r2`, `retry --tag r2`.

- Re-fetch (October 27, on the UW network): `python tools/fetch_pdfs.py run --out private/data/roadmap/pdfs/gold --group "Corpus manifest: r2calc" --group "Corpus manifest: calc1" --group "Corpus gold_manifest"` (commit 3ec8a49 adds `--group`), twice; the second pass after fixing the Wiley route for AGU DOIs (Crossref names AGU as publisher, so 10.1029 papers had never been sent to the Wiley API). Then `g10_fetch_xml.py` for both manifests. 192 new PDFs (Wiley 106, Elsevier 85, Springer 1) and 103 Elsevier XML. Text now: round 2 202 of 222, round 1 381 of 525. Logs `refetch_2026-10-27.log`, `refetch_agu_2026-10-27.log`; queue before the retry kept as `download-queue.before-refetch-2026-10-27.json`. Earlier 403s came from runs off the UW network.
- Skipped by decision: Russian Geology and Geophysics, 5 papers (DECISIONS.md).
- Top-up coding: 48 newly fetched round-2 papers, batch msgbatch_01HTgc7EkMN55Gd8gzUtQPjm, same command as above (commit 3ec8a49). From this batch on, the shared prefix (instructions, codebook, schema; 10,884 tokens) is cached for 1 hour and pre-warmed by one max_tokens 0 request before submission; the pre-warm read the cache (10,884 tokens read, 0 written).

## Audit of reported numbers and paper figures (October 27)

- Audit: four independent agents traced every number in review-visibility.qmd, workflow-outcomes.qmd, this registry, RESULTS.md, PAPERS_VS_AGENTS.md, the review-visibility report and the OLMo brief to its data and script, and recomputed it (workflow run wf_ee55d013-cab). Corrected: 245 feature-outcome tests (425 was a digit swap); 233 valid round-1 codings (g13 and g14 had been run before the last retry, on 232); agents run R more often than papers, so only V fits "run least by agents"; the 3 dropped review codings were 2 overlong quotes and 1 schema error; the eligible open-access share is 62.5% (46% is the share among uncoded papers); main coding cost $0.32 per paper (E1), not $0.34.
- Reruns at a clean commit: g13, g14, g17 (3ec8a49), g16 and g19 (a77b516). `g19_report_numbers.py` writes `derived/report_numbers.json` (154 ids) for every number no other script writes.
- Figures: `python tools/roadmap/figures/make_all.py` (scripts in `tools/roadmap/figures/`, commit 2798f89) writes `private/data/roadmap/figures/paper/fig01..fig10` as PDF, PNG and a provenance JSON. Each figure was checked by an independent agent that recomputed the plotted numbers from the raw files.
- Incident: during figure development a test render wrote through a symlink into `private/analysis/codings/api/calc1/` (160 files). The files were restored and match private commit cdadda2 byte for byte; the symlinks were removed.

## E1b. Round-1 top-up (in progress, October 27)

- Inputs: the 146 eligible round-1 papers whose full text arrived in the October 27 re-fetch on the UW network (mostly AGU through the Wiley API, and Elsevier), codebook 1.5.0.
- Command: `python tools/code_papers.py submit --manifest private/data/roadmap/derived/calc1/manifest.jsonl --tag calc1 --max-usd 250` → batch msgbatch_01EsvmQCFDiY2ido76NMGZK3, 146 papers. First batch submitted with the prompt-cache warm-up (10,884 tokens written before submission, 1-hour cache).
- Expected cost: about $47 at $0.32 per paper. Collect with `collect --tag calc1`, then rerun g13, g14, g17, g19, g20, g21 and `make_all.py`.

## E8. Topics and journals

- Question: which fields and venues are in the corpus at each stage, does coding coverage depend on them, do workflows differ by field and venue, and do the E6 associations survive within subfield and within journal family?
- Script: `python tools/roadmap/g20_topics_journals.py` (public commit 79a7bb6) → `derived/topics/topics_journals.json`, `TOPICS.md`. Figures fig11, fig12. Built and checked by workflow wf_1f7c1b81-e0e (author, independent recompute, two figure verifiers, four readers).
- Result (round 1, 233 codings): coverage depends on journal family (Cramér's V 0.73) more than subfield (0.26), through download timing; 28 of 104 field and venue tests with q < 0.1; all 15 E6 associations survive within subfield; within journal family the steps-citation link roughly halves; the breadth links hold everywhere. None of the 245 E6 tests passes Benjamini-Yekutieli.
- Reports: public `topics-journals.qmd`; private `text/report-roadmap.md` section 6 and 7.

## E9. Entry-state evaluation

- Question: does the coded entry state record what started the work, or the introduction's gap statement?
- Script: `python tools/roadmap/g21_entry_state.py` (and `... audit`), public commit 79a7bb6 → `derived/entry/entry_state.json`, `ENTRY.md`, `audit_sample.json` (60 papers, rng 2026), `audit_packets/` (blind packets: key, DOI, title, text paths only).
- Blind audit: workflow wf_d964d4c7-5a1, two blind Claude agents per paper in Claude Code (no API cost) coding entry state, node, gap flag and operational start; outputs saved verbatim in `derived/entry/blind_audit.json`.
- Result: `problem` (78% of round 1) confirmed by both blind coders in 20 of 36; reweighted share about 44% [31, 57]; other states 20 of 24 confirmed; alpha 0.77 batch vs batch, 0.81 blind vs blind, 0.60 to 0.67 blind vs batch. No paper reframes its question after a failure. Figure fig13.
- Proposal (not adopted): codebook 1.6.0 adds `entry.start {kind, evidence, page}`; `analysis/entry-state-evaluation.md`.

## Report

- `text/report-roadmap.md` (draft v0.2, October 27): scientific report of E0 to E9 for geoscientists and NLP researchers, every outcome metric and agreement statistic defined in place. Reviewed by workflow wf_1e353a97-c37 (geoscientist, NLP researcher, numbers auditor, voice editor; 97 findings, high and medium applied). Regenerate after round 2 and the top-up return.

## Rerunning with another model

- `tools/code_papers_open.py export` writes the exact system prompt, per-paper user text, a `requests.jsonl` and an `inputs.json` with sha256 of every input text, for any manifest. `run` sends the same requests to an OpenAI-compatible endpoint (OLMo on vLLM) and validates with the same checker. Tested end to end against a mock endpoint on October 27; not yet run on a real open model.
- Compare with Claude: `python tools/check_coding.py agree <claude coding> <open-model coding>` per paper, or the E2 procedure in `g13_calc1_results.py` with the open-model folder in place of `gold-r2`.
- Text input: XML where available (116 of 235 round-1 papers), else pdftotext with [p. N] markers (`--pdf-text`). Papers over 200,000 characters are skipped and listed (3 in round 1).
