---
addendum: review-disclosures
version: 1.0.0
date: 2026-10-28
applies_to: paper-coding codebook 1.5.0, requests with an open review record only
schema: agents/coder/review_addendum.schema.json (fields added to agents/coder/coding.schema.json)
kinds: tools/roadmap/g27_author_responses.py (scheme fixed before its labelling, 2026-10-28)
---

# Review addendum: disclosures in author responses (v1.0.0)

This addendum applies only when an open review record is attached. Code the paper under the codebook as before, with the `final_paper` and `review` sequences. Then add two top-level fields to the same JSON object: `review_addendum_version` ("1.0.0") and `disclosures`.

A paper does not report its work in the order it was done, and it leaves out what was tried and dropped. In an open review the authors answer referees in their own voice, and those answers sometimes say what the paper does not. `disclosures` records each such statement and whether the published paper carries it.

## R1. What a disclosure is
- One disclosure = one author statement of one kind. A paragraph may hold several disclosures, of the same or different kinds.
- Read every author paragraph of the open review record (`AC` comments: `[AC1 ¶3]`, `[AC1 p.2]`, `[AC1-S p.1]`) and every page of the author-responses document when one is attached (`[AR1 p.2]`: responses filed with each revision, pages not already in the open discussion).
- Only the authors' own words count. A sentence in which the authors quote the referee, or quote their revised manuscript, is not a disclosure; the statement around it may be.
- Referee, community and editor comments (`RC`, `CC`, `EC`) are never the source of a disclosure; they are coded in the `review` sequence.
- Code every disclosure, in the order of the record. An author text with none gives an empty list.

## R2. Kinds

| kind | What the authors state |
|:--|:--|
| `tried_dropped` | A method, dataset, parameter, model setting or analysis that the authors say they tried, tested or ran and did not report, or reported only as "results not shown" or "similar results" (includes sensitivity tests run before or during review whose outcome is given only in the response). |
| `order_of_work` | What was done first or later: the sequence of the work, an earlier design, what existed before the study started, what was done after submission, what is planned in follow-up work. |
| `constraint` | A limit on the work: data access or availability, time, funding or project scope, instrument or sensor limits, computing cost, field logistics, permissions, staff. |
| `unstated_reason` | The reason for a methodological or data choice, given in the response because a referee asked about a choice the discussion manuscript states without its reason. |
| `added_for_review` | A new analysis, computation, experiment, dataset or quantitative test carried out for the review. Text edits, added references, figure styling and rewording are not counted. |
| `claim_narrowed` | The authors weaken, qualify or remove a claim or interpretation (scope, generality, causal language, certainty). |
| `writing_process` | How the paper itself was composed, as distinct from the research: a figure, section or framing drafted and cut, debated among the authors, shaped by length or format. |

## R3. Unit, quote and content
- `unit`: the locator printed at the start of the paragraph or page, without brackets: `AC1 ¶3`, `AC2 p.1`, `AC2-S p.1`, `AR1 p.2`.
- `quote`: at most 25 words, copied exactly from that unit, in the authors' own words (R1). A reader must find it by searching the unit.
- `content`: at most 25 words, what exactly was disclosed (the method tried, the order, the limit, the reason, the added analysis, the narrowed wording).

## R4. Final-paper status
Search the published paper (the first document, and its publisher XML text when attached: main text, figure captions, appendices) for the specific content of the disclosure.

| `final_paper_status` | Meaning |
|:--|:--|
| `present` | The final paper states the specific content: the method tried, the order, the limit, the reason, the added analysis, the narrowed wording. |
| `partly` | The final paper touches the topic but not the specific content (it names the alternative method but not that it was tried; it mentions a limit only in general terms). |
| `absent` | The specific content is not found in the final paper. |

- With `present` or `partly`, give `final_loc` (a locator of the XML text as printed: `§3 ¶2`, `Figure 3`, or `TITLE` for the title; a page when only the PDF is attached) and `final_quote` (at most 25 words, copied exactly from the published paper).
- With `absent`, `final_loc` and `final_quote` are empty strings.
- For a claim or an analysis the authors say they removed, `present` means the final paper no longer carries it: set `removed` to true and leave `final_quote` empty. Otherwise `removed` is false.
- For `writing_process`, `present` means the paper itself says something about the composition step (it rarely does).
- The paper's supplement and data-availability statements are not searched.

## R5. Workflow node and loop
- `node`: the graph v0.4.2 letter of the step the disclosure is about, with the same letters and rules as codebook section 3 (N E O I Q H S D F C V X K P R). A sensitivity test that was run is V; a dropped alternative model is the node where the fork sits; a constraint on data acquisition is O or F. Use `none` when the disclosure maps to no step of the inquiry (most `writing_process`, and limits on project scope that bind no step).
- `loop`: true when the statement shows the work went back to an earlier step: an attempt failed, mismatched or was replaced and the step was redone or revised (codebook move `return_after_failure`), before submission or during review. A check that agreed with the result, a reason, or a limit is not a loop. An analysis added for review is a loop only when it revised an earlier step's result or method.

## R6. Fields
Each item of `disclosures` has: `unit`, `kind`, `quote`, `content`, `final_paper_status`, `final_loc`, `final_quote`, `removed`, `node`, `loop`. The validator checks the word limits, and for each item that the unit is an author unit, that the quote is in it (or in another paragraph or page of the same author document) and is not referee text, and that the final quote is in the published paper. An item that fails a quote check is dropped from the analysis; the rest of the coding stands.

## Change log
| Version | Date | Change |
|:--|:--|:--|
| 1.0.0 | 2026-10-28 | First version: the seven kinds and the final-paper check of `tools/roadmap/g27_author_responses.py`, made a defined task folded into the review coding call (one call codes inquiry, review sequence and disclosures); workflow node and loop flag added |
