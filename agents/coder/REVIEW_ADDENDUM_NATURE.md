---
addendum: review-disclosures-nature
version: 1.0.0
date: 2026-10-28
applies_to: review addendum 1.0.0 (agents/coder/REVIEW_ADDENDUM.md), requests whose review record is a Nature Portfolio peer review file only
source: nature_review_file
schema: agents/coder/review_addendum_nature.schema.json (fields added to agents/coder/coding.schema.json and review_addendum.schema.json)
units: tools/roadmap/g27_nature_units.py 1.2.0
---

# Review addendum, Nature-family variant (v1.0.0)

This variant applies only when the attached review record is a peer review file of a Nature Portfolio journal (Nature Communications, Communications Earth & Environment, Nature), split into units. The review addendum 1.0.0 above still applies: the kinds (R2), the quote and content limits (R3), the final-paper check (R4), node and loop (R5) and the fields (R6). This section changes the units, adjusts two kinds and adds two fields.

## N1. The record and its units
- A peer review file has no open discussion and no discussion preprint. It holds, round by round, the referee reports (in Communications Earth & Environment also the editor's decision letter, in Nature Communications sometimes the editor's remarks) and then the authors' response letter to that round. The last round's reports often have no response.
- Every paragraph carries a locator:
  - `R<n>-round<k> ¶m`: referee #n in review round k, paragraph m;
  - `E-round<k> ¶m`: the editor in round k;
  - `A-round<k> ¶m`: the authors' response letter to round k, paragraph m.
- Round k counts the sets of reports: round 1 answers the first submission, round 2 the first revision. The authors' response to round k comes after the round-k reports.
- There are no `AC`, `AR`, `RC`, `CC` or `EC` locators in this record. Do not use them.

## N2. Where disclosures come from
- Read every `A` paragraph. A disclosure's `unit` is the `A-round<k> ¶m` locator printed at the start of the paragraph that holds the quote, without brackets.
- A response letter often repeats the referee's comment before answering it, often without quotation marks and in the same paragraph. The repeated comment is referee text: it is never a disclosure, and a quote taken from it fails the referee-text check. The statement around it may be one. A paragraph under an `A` locator that is plainly a referee's comment (pasted from a report or an annotated manuscript) is not a disclosure source either.
- `R` and `E` paragraphs are never the source of a disclosure. They are coded in the `review` sequence: cite the `R` or `E` locator in the step's page field, with trigger `referee` for `R` and `editor` for `E`.

## N3. Kinds (changes to R2)
- `unstated_reason`: the submitted manuscript is not attached. The referee's question about a choice is the evidence that the reason was missing.
- `added_for_review`: an analysis the authors say they carried out for the review, in any round.
- The other kinds are unchanged.

## N4. Final paper
- As in R4: the published paper (the first document, and its publisher XML text).

## N5. Fields and validation
- Add two top-level fields to the coding: `review_source` = "nature_review_file" and `nature_addendum_version` = "1.0.0". `review_addendum_version` stays "1.0.0".
- The validator (tools/check_coding_nature.py) checks the disclosures as in R6, with these units: the unit must be an `A` unit; the quote must be in it or in another `A` paragraph of the file; it must not be referee or editor text (half or more of its 8-word shingles in the `R` and `E` paragraphs of the same round or an earlier one, so a sentence of yours that a later referee quotes back stays yours); the final quote must be in the published paper. An item that fails a quote check is dropped from the analysis; the rest of the coding stands.

## Change log
| Version | Date | Change |
|:--|:--|:--|
| 1.0.0 | 2026-10-28 | First version: Nature Portfolio peer review files (NC, CEE, Nature) as R, E and A units (g27_nature_units.py 1.1.0), two kinds adjusted for a record without a submitted manuscript, two added fields; appended to the system prompt as a second block only for papers whose review folder holds such a file. Revised the same day, before any coding: units from g27_nature_units.py 1.2.0 (two-column comment and reply tables split), and the referee-text check limited to rounds up to the cited A unit's. No coding was made under an earlier text |
