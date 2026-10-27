> Summarized in section 8 of the roadmap report, `private/text/report-roadmap.md` (October 27, 2026). This file keeps the full methods and references.

# What peer review changes, and what the paper says about it: an open-review visibility experiment on 58 Earth-science papers

Draft v0.2, October 27, 2026. Denolle Lab metascience project, roadmap Phase 2b (the experiment on work done during peer review).
Status: model-coded and model-labelled; no human check yet.

## Abstract

Published papers are the main record from which both people and AI agents learn how research is done. If the work done in response to peer review is written into the paper as if it had been planned, that record understates how much of research is iteration. We tested this on Earth-science papers whose review is public. Of the 233 papers coded in round 1 of the roadmap corpus (2022 articles; 525 eligible), 64 are in journals published by Copernicus, nearly all of the European Geosciences Union (EGU). For the 61 that have an open discussion (referee, author, community and editor comments posted beside a citable discussion preprint), Claude Opus 5.5 read the discussion and the published paper and coded the review process as a sequence of steps on the graph of inquiry, the seminar's map of 15 kinds of research move (paper codebook 1.5.0). Fifty-eight codings passed the format check. Two separate runs of a Claude labeler then classified each of the 746 coded review steps by how it appears in the published paper, with a third run settling disagreements. Of the 580 steps that changed the work, 560 (96.6%) are in the published paper and 20 (3.4%; 95% interval over papers 1.7% to 5.6%) are not. None of the 580 is marked in the paper as a revision or as prompted by review. With 0 of 58 papers marking any change, the share of papers in journals like these that would mark one is below about 5% (one-sided 95% upper bound). A script search of the published PDFs agrees: every mention of reviewers is a thank-you or the journal's review statement. The labelers agreed on 720 of 746 steps (96.5%, Cohen's kappa 0.91), and all 560 quotes offered as evidence exist verbatim in the published text. The changes most often missing are checks of the result (node V: sensitivity tests, comparisons with independent data or methods, controls, reruns): 13 of 102, against 7 of 478 for all other nodes, a difference that holds with papers as the unit (q = 0.003 over 14 nodes, exploratory). The direction agrees with the October 21 loop pilot on nine papers (4 of 126 loops readable as loops in the paper). Because the review record of these journals is itself public, the finding is that the paper, not the scientific record, presents review-driven work as planned.

## 1. Question

Two problems motivate the roadmap. Experts reach different results from the same data, and much of the inquiry behind a paper is never reported. This experiment addresses the second in its most observable form: work done during peer review. The question is narrow. When referees ask for changes and authors make them, does the published paper show that the work changed in review, or does it read as if the work had been planned that way?

The answer matters for the agent-design part of the project. An agent loop (the cycle of steps an automated research system repeats) trained or evaluated on published papers sees a research process without the review loop. If the review loop is where much of the checking happens (sensitivity tests, comparisons, narrowed claims), papers alone will teach agents a cleaner workflow than the one people use.

## 2. Corpus

- **Preselection (script g03).** 600 papers from 2022, drawn from an OpenAlex pool of 14,223 articles: half from the core ring (the 8 OpenAlex topics of the study's principal investigator, Marine Denolle: seismology, seismic waves and imaging, earthquakes and tectonics, seismic sensors, cryosphere, high-pressure geophysics) and half from the broad ring (8 Earth-science subfields), with equal numbers per impact quintile and subfields taken in turn. An abstract screen by two model calls that did not see each other's answer, with a third on disagreements, left 525 eligible. Scripts g01 to g08 in `tools/roadmap/`; decisions in `private/data/roadmap/DECISIONS.md`.
- **Gold set (script g05).** A frozen sample of 100 of the 525 eligible papers, 50 per ring, spread over terciles of impact, novelty and breadth. It is the set for the human coding (40 papers, two coders each, not started) and for the run-to-run test. The review experiment does not use it.
- **First calculation.** Full text was obtained for 235 of the 525 eligible papers before the first coding batch, and each was coded once; 233 codings pass the format check (paper codebook 1.5.0). Coverage is biased toward open access (83% of coded papers, 46% of uncoded). A re-fetch on October 27 brought round-1 full text to 379 papers; the 146 papers with full text and no valid coding were sent for coding the same day.
- **Open-review subset.** 64 of the coded papers are in Copernicus journals. For 61 an open discussion exists (the other three, in European Journal of Mineralogy and Scientific Drilling, journals Copernicus publishes for other societies, have none). For each, `tools/roadmap/g15_open_review.py` retrieved the discussion page with every comment, the comment supplements, and the review files (author responses, tracked-changes manuscripts, manuscript versions): 134 referee comments, 147 author comments, 6 community comments and 4 editor comments in total. All 61 have the publisher XML of the final article, which gives a located text (section and paragraph) for checking quotes.
- **Coded and labelled.** 58 of the 61 codings passed the format check after one retry; three failed again, two on quotes longer than 25 words and one on a schema error, and were dropped. Journals: The Cryosphere 33, Natural Hazards and Earth System Sciences 4, Geoscientific Model Development 4, Hydrology and Earth System Sciences 4, Biogeosciences 4, Atmospheric Chemistry and Physics 3, Earth Surface Dynamics 2, Earth System Science Data 2, Geoscientific Instrumentation 1, Solid Earth 1.

## 3. Methods

### 3.1 Coding the review process

Each paper was coded with `tools/code_papers.py`: Claude Opus 5.5 (`claude-opus-5-5`) through Anthropic's asynchronous batch mode, effort high, maximum 32,000 output tokens (papers that ran out were retried at 64,000), no temperature or thinking parameter set. The request carried the paper PDF, the located publisher text, and the open-review record (`--review-dir`). The review record given to the coder is `discussion.txt`: the comments of the discussion (referee, author, community, editor) with the supplements attached to comments. The tracked-changes manuscripts, author-response PDFs and manuscript versions were downloaded for all 58 papers but not sent, and neither was the article supplement. Under codebook 1.5.0 (the written instructions the model follows) the coder writes two sequences: the final paper's walk on the graph of inquiry, and a review sequence whose steps are the changes and refusals recorded in the discussion. Each step has a graph node, a mode, a one-sentence action, a location in the review record, a quote of at most 25 words, a move (`review_forced`, `declined`, `return_after_failure`, `new`) and a trigger (`referee`, `editor`, `commenter`, `author`). Codings were checked against the JSON schema and codebook rules by `tools/check_coding.py`; the check concerns format, not accuracy. Cost for the 58 valid codings: $26.76 at batch prices ($0.46 per paper). The first pass left 14 requests to resubmit.

Because the coder read the final paper as well as the discussion, it may have phrased review steps from the final text. That can only raise the share labelled "as if planned" and lower "not in the paper".

### 3.2 Labelling visibility

For each paper, `tools/roadmap/g16_visibility.py prep` wrote an input packet with the numbered review steps and the paths to the published text and the review record. The workflow `tools/roadmap/workflows/visibility.js` gave each packet to two model labelers, separate runs of a Claude model inside Claude Code (the model id was not recorded; workflow agents take the model of the session that runs them), each without seeing the other's labels. Each labeler assigned every step one of four labels:

| Label | Rule |
|:--|:--|
| as_revision | The change is in the published paper and the paper ties it to review (for example "as suggested by a reviewer", "added in revision", an acknowledgement naming this change). A generic thank-you to referees does not count. |
| as_planned | The change is in the published paper with no sign it came from review. |
| absent | The review step describes a change to the work, and the published paper does not contain it. |
| no_change | The step records no change: a declined request, a reply that only argues, a promise that is not a change to the manuscript. |

Every as_revision or as_planned label had to carry a quote copied from the published text with its section-and-paragraph locator. Where the labelers differed, a third run re-read the step and the published text and decided. `g16_visibility.py analyze` then matched each quote against the normalized published text and computed the shares. A labelling pilot of 10 papers was run and checked before the remaining 48.

The published text the labelers searched is the converter's output from the publisher XML. It keeps body text and captions; only 12 of the 58 texts include an acknowledgements section, and none includes the article supplement. An acknowledgement that names a change would have been invisible to the labelers, and a change moved to the supplement would be labelled absent. Section 4.5 checks the first gap by script; the second remains open.

### 3.3 Intervals

Because no change was marked as a revision, the bootstrap over papers is degenerate for the marked share only (every resample gives zero). For that share we report the rule-of-three bound: with zero events in n independent units, the one-sided 95% upper bound on the event rate is about 3/n (Hanley, 1983). Papers, not changes, are taken as the independent units, because marking practice is a property of the authors and the journal. The absent share has an ordinary bootstrap interval over papers (5000 resamples).

## 4. Results

### 4.1 Visibility of review changes

Counts are drawn in `figures/paper/fig07_review` panel a.

- Review steps coded: 746. No change (declined or argued): 166. Changes to the work: 580.
- In the paper, as if planned: 560 (96.6%). Not in the paper: 20 (3.4%; 95% interval over papers 1.7% to 5.6%). Marked as a revision: 0.
- Papers marking any review change: 0 of 58 (95% upper bound about 5%).
- Review steps per paper: median 13, range 5 to 23. Changes per paper (steps that are not "no change"): median 10, range 4 to 18.
- Labeler agreement before adjudication: 720 of 746 steps (96.5%), Cohen's kappa 0.91 over the four labels; 26 steps adjudicated.
- Quote existence: 560 of 560 quotes are found verbatim in the published text. This shows the quotes exist, not that each shows its change. 44 of them exceed the 25-word limit the labelers were given.
- Trigger: 729 steps follow referee comments, 15 community comments, 2 the authors' own initiative; none was coded as an editor's request. All 20 absences follow referee requests.

### 4.2 Which changes go missing

Per-node counts are drawn in fig07 panel b. Checks of the result (node V: sensitivity tests, comparisons with independent data or methods, controls, reruns) are both the most common kind of change asked for in review (102 of 580) and the kind most often promised in a reply but not found in the paper (13 of 102, 13%; all other nodes together 7 of 478, 1.5%). The 13 absences fall in 10 papers. Treating papers as the unit (absent labels shuffled among the changes within each paper, 5000 permutations; bootstrap over papers), V's absent share exceeds that of the other nodes by 11.3 percentage points (95% interval 4.1 to 19.6), q = 0.003 after Benjamini-Hochberg adjustment (Benjamini & Hochberg, 1995) over the 14 nodes with at least 5 changes. No other node differs. The test is exploratory: V was singled out after the per-node shares were seen.

### 4.3 Refusals that still changed the paper

The coder marked 220 steps as `declined`. Of these, 60 (27%) were labelled as_planned: the authors declined the request in their reply yet the published text contains a change that answers it, usually a caveat or a sentence of justification. Conversely, 6 steps coded as review-forced were labelled no_change on inspection.

### 4.4 Comparison with the October 21 loop pilot

The October 21 loop pilot coded loops from Nature peer-review files, EGU discussions and one preprint revision for nine papers: of 126 loops, 4 were readable as loops in the paper, 70 were in the paper as if planned and 52 were absent (`private/analysis/success-set/loops/REPORT.md`; recorded in `report_numbers.json` as `review.loop_pilot`). It is a different pilot from the 10-paper labelling pilot of section 3.2. The direction agrees. The absent share differs (41% against 3.4%). The likely reason is construction: the pilot counted analyses discussed in review files that never entered any version of the manuscript, while the EGU review sequences were coded from the discussion comments with the final paper in view, which favours finding a change in the paper (section 3.1). An earlier draft attributed the difference to coding from the tracked-changes manuscripts; the coder was not given them.

### 4.5 Script check of the published text

Independently of the labelers, `g19_report_numbers.py` searched the published text of the 58 papers in two forms: the XML text the labelers read, and text extracted from the published PDF. In the PDFs, 55 papers have an acknowledgements section and 53 mention reviewers or referees; every mention sits in a thank-you or in the Copernicus review statement, and none of the 58 uses a phrase that ties content to review ("as suggested by the reviewer", "in the revised manuscript", "in response to the referee", "during the review"). The XML texts contain no such mention at all, because most back matter is missing from them. The zero therefore holds on the full text, for the phrases searched. This is a check on the zero, not a recall test of the labelers: they have not been shown papers known to mark revisions.

## 5. Discussion

In these 58 papers, the published text records review changes without marking any of them as such. Roughly one change in thirty that authors described in their replies did not reach the paper, and none of the rest was identified as coming from review. The paper presents the outcome of an iterative, negotiated process as a planned design.

This is a convention, not misconduct. Copernicus journals publish the full discussion on a citable discussion preprint that the final paper links to (Pöschl, 2012), so a reader can recover the history. The point for the project is where the history lives. A model trained on papers, or an agent loop designed from the methods sections of papers, sees no review loop at all. The kind of work most affected is checking: sensitivity tests, comparisons with independent data or methods, controls and reruns (node V). In the comparison of 233 papers with 31 published agent systems (`tools/roadmap/g14_papers_vs_agents.py`), V is among the steps the coded agent loops rarely run: 10% of systems against 97% of papers. Q (question) shows the same gap (10% against 98%), and I (5%), H (6%) and P (0%) are run still less often by the systems. Refinement of claims (node R) goes the other way, since loops run it more often than papers (68% against 56%). So the published record understates one of the steps, checking, that the coded agent loops rarely run. The 31 systems were hand-picked for a comparison talk and were coded from their descriptions under a separate loop codebook, so this is a comparison of descriptions, not of executed runs.

## 6. Limitations

1. **No human check.** The coding, the labelling and the adjudication were done by Claude models. Labeler agreement (96.5%, kappa 0.91) is agreement between runs of one model family: it shows stability, not correctness, and errors the runs share do not show. The human gold-set coding (Han, Kidiwela, Hemmett, Denolle) has not covered the review sequences.
2. **Coder saw the final paper.** The review sequence was coded with the published text in view, which can only inflate "as if planned".
3. **Labelers searched an incomplete text.** The XML text lacks most acknowledgements and every supplement. Section 4.5 covers acknowledgements for the phrases searched; supplements are unchecked, so some of the 20 absences may sit there.
4. **No recall test.** The labelers' ability to find a marked revision is assumed, not measured.
5. **What counts as a change depends on the coder.** The review sequence is the coder's reading of the discussion. Steps merged or split differently would change the denominators, though not the zero.
6. **Sample.** 58 papers, 33 from The Cryosphere, all from 2022, all from journals with open discussion. Journals with closed review may differ in both directions: authors may mark revisions more where review is not public, or less.
7. **Selection upstream.** The papers come from the 233 coded round-1 papers (525 eligible), which lean toward open access, and every Copernicus paper is open access.
8. **Contamination.** The papers and their discussions predate the model's knowledge cutoff (June 2026), so the model may recall them.
9. **A strict definition of "marked."** We did not count generic acknowledgements of referees. Under a looser rule most papers would count as marking review in general (53 of 58 mention reviewers in a thank-you or review statement), though still not marking which change it caused.
10. **Three papers dropped** for format failures (two quotes over 25 words, one schema error), not at random with respect to length.

## 7. Next steps

- Code the review sequences of a subset by hand (target 10 papers, two people) and score the model labels against them.
- Ablation: code the review sequences from the review record alone, without the published text, then label them.
- Have a model from another family label a subset (the open-weight path in `tools/code_papers_open.py`).
- Recall probe: label papers known to mark revisions, or texts with inserted marked-revision sentences, and report the hit rate. Entailment check: ask a second model or a person whether a random 50 of the 560 quotes show the change their label claims.
- Check the 20 absent changes against the article supplements (Copernicus posts them beside the paper).
- Extend to journals that publish review files after closed review (Nature Communications, Nature Geoscience) to test whether open discussion changes the result.
- Code the 146 round-1 papers sent for coding on October 27 (144 fetched after the first batch, 2 resubmitted after failing the format check). A separate 146 eligible papers still have no PDF, mostly Seismological Society of America journals, Geophysical Journal International and Springer translation journals.
- Feed the review sequences into the corrected human-workflow model (roadmap Phase 3) as the observed rate at which checking work disappears from papers.

## 8. Reproducibility

| Item | Location | Commit |
|:--|:--|:--|
| Paper codebook 1.5.0, schema | `agents/coder/` | public 01b7f78 |
| Batch coder | `tools/code_papers.py` | public 8c3337d |
| Open-review fetch | `tools/roadmap/g15_open_review.py` | public 8c3337d |
| Visibility prep and analysis | `tools/roadmap/g16_visibility.py` | public 4ff3f93 |
| Labelling workflow | `tools/roadmap/workflows/visibility.js` | public 4ff3f93 |
| String check, triggers, node test, loop pilot | `tools/roadmap/g19_report_numbers.py` | additions of October 27, uncommitted |
| Review codings (58 valid) | `private/analysis/codings/api/calc1-review/` | private dacfd0e |
| Labels | `private/data/roadmap/derived/review/visibility_labels.json` | private dacfd0e |
| Results | `private/data/roadmap/derived/review/visibility_results.json` | private dacfd0e |
| Download and run log | `private/data/roadmap/MANIFEST.md` | private |

Rerun: `python tools/roadmap/g16_visibility.py prep`, run the workflow over the packet keys, then `python tools/roadmap/g16_visibility.py analyze` and `python tools/roadmap/g19_report_numbers.py`. The coding step costs money; rerunning analysis alone does not.

## References

Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B (Methodological), 57*(1), 289–300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x

Hanley, J. A. (1983). If nothing goes wrong, is everything all right? Interpreting zero numerators. *JAMA, 249*(13), 1743. https://doi.org/10.1001/jama.1983.03330370053031 (Crossref lists one author; the article is by Hanley and Lippman-Hand.)

Pöschl, U. (2012). Multi-stage open peer review: Scientific evaluation integrating the strengths of traditional peer review with the virtues of transparency and self-regulation. *Frontiers in Computational Neuroscience, 6*, 33. https://doi.org/10.3389/fncom.2012.00033
