# Validation performed

## v0.4 implementation, September 10, 2026

Scientific advance now organizes the book, eleven versioned mode specifications, the thirteen
anchor/companion meetings, the claim/episode records, and the historical evaluation design.
Meeting 11 uses the integration pair; the documented citation and scope corrections are applied.
The convenor authorized implementation of the converged plan; no group discussion or empirical
agent benefit is asserted.

Checks completed on the revised sources:

- `.venv/bin/python tools/validate.py`: 34 chapters, 13 ordered meetings, 27 assigned readings
  (26 anchor/companion readings plus the Karaca erratum), 154 reference records; citations,
  source links, session metadata, eleven mode specifications and their generated export agree.
- `.venv/bin/python tools/export_modes.py --check`: the export matches the authoritative source
  versions and hashes. Isolated temporary fixtures also checked round-trip export and rejection
  of stale source, a missing evidence section, and a mismatched mode ID.
- `quarto render`: successful full build of all 34 chapters. A separate HTML-parser pass found
  no broken local file or fragment links among those rendered chapters, including the exported
  instructions and claim template.
- `.venv/bin/python tools/check_links.py`: checked 173 distinct external URLs across 35 sources.
  DOI registrations passed. Six publisher requests returned 403 and remain access checks for a
  reader: AGU/Wiley (Lindsey), SAGE (Flake), MIT Press (Nersessian), Annual Reviews (Moore), and
  ScienceDirect (Wang and Petersen). These are recorded separately from missing-link failures;
  they do not certify accessible full text. The checker's final wording now preserves that distinction.
- Visual inspection in isolated headless Chrome: desktop glossary, meeting 11, and bibliography;
  actual emulated 390-pixel viewport for estimation and the claim-record table. Both mobile
  pages reported document width equal to viewport width; headings and table contents wrapped.
  Initial command-line screenshots used an inaccurate narrow viewport; only the subsequent
  device-emulation captures support the mobile check.
- `git diff --check`: no whitespace errors.

Evidence and limits:

- `review/audit-evidence/v0.4-reading-checks.json` records new-source identity checks, targeted
  interpretation checks, and their limits. Nersessian's official OA status and excerpt identity
  are verified; automated full-subsection retrieval was blocked. Read the selected section
  before constructing a detailed historical evaluation packet from it.
- The new case chapter provides three reading-based specifications, not executable historical
  data packets. The JSON mode export and blank claim template are implemented artifacts;
  they are not a scientific-agent runtime or experimental outcomes.
- No private case material was published, no private agent implementation was modified, and
  no historical replay, policy comparison, corpus study, or prospective evaluation was run.
- This entry records local validation, not deployment of v0.4.

Earlier entries below retain their dates and describe prior versions.


## September 9, 2026: bullet-level public pages, status labels, and the geoscience-method readings

The public pages were moved to bullet level at the convenor's request, with the prose and analysis
kept in the private repository under `text/`. Every page now carries a status label (drafted,
discussed, adopted) and the front page a table of where things stand. Sixteen readings on
geoscientific method and practice were added; the design notes were rewritten around one worked
project; meeting 13 now specifies changes to the group's own agent family and evaluation vault.

- `tools/validate.py` passes: 22 chapter files, 13 meetings in order, 31 assigned papers, 139
  bibliography records; generated reading lists current; Pandoc citations without warnings.
- `tools/check_links.py`: every DOI registered, including the percent-encoded Frodeman and Baker
  DOIs; the same publisher pages block scripted requests as before.
- `quarto render` produced all 22 pages; the status badges render on every page.

## September 9, 2026: design notes and reading copies

Added `agent-design.qmd` to the working materials and ten references for it (Virtual Lab, FunSearch,
ChemCrow, STORM, DiscoveryWorld, the Sozou review, Darden, Langley and colleagues, Thagard, Klahr
and Simon), all verified against Crossref. Corrected the A-Lab figure from "forty-one new compounds"
to the published 36 of 57 targets, after reading the paper. Added `tools/fetch_open_copies.py`,
which writes the manifest `private/reading-copies.md` and fetches open copies into the gitignored
`private/pdfs/`.

- `tools/validate.py` passes: 22 chapter files, 13 meetings in order, 31 assigned papers, 123
  bibliography records; generated reading lists current; Pandoc citations without warnings.
- `quarto render` produced all 22 pages.

## September 8, 2026: meeting dates removed

The seminar now proceeds one meeting at a time in numbered order, with no dates or times anywhere
in the book. Session headers read "Meeting N of 13", the index lists the meetings without a date
column, the meeting-notes page carries a "Held: date to be recorded" line per meeting, the
corpus-study timeline is keyed to meetings, and `curriculum.json` no longer has a `date` field.
`tools/validate.py` checks that the thirteen meetings are numbered in order and no longer checks
a calendar. (This change was committed to the public repository as `869e6c5`, whose message
mentions "analysis headers" by mistake; the commit itself contains the book changes.)

- `tools/validate.py` passes: 21 chapter files, 13 meetings in order, 31 assigned papers, 113
  bibliography records; generated reading lists current; Pandoc citations without warnings.
- `quarto render` produced all 21 pages.

## September 8, 2026: consolidated bibliography

`reading-library.qmd`, `references.qmd`, and `suggested-readings.qmd` were merged into one page,
`bibliography.qmd`, whose reading lists are generated from `curriculum.json` by
`tools/build_bibliography.py`. `tools/validate.py` now runs that script with `--check` and fails if
the lists are stale.

- `tools/validate.py` passes: 21 chapter files, 13 consecutive Tuesdays, 31 assigned papers, 113
  bibliography records; generated reading lists current; Pandoc citations without warnings.
- `quarto render` produced all 21 pages. Every citation in every chapter resolves to
  `bibliography.html#ref-<key>`, the reference list renders once, on that page, with 113 entries,
  and the per-chapter reference blocks Quarto emits are hidden, so nothing is listed twice.
- No `references.html`, `reading-library.html`, or `suggested-readings.html` is produced; links
  to the old pages inside the book were repointed, and `check_links.py` reports nothing new.

## September 6, 2026, third pass: glossary and corpus study

Same environment. After the glossary was added as the book's first page, the corpus-study design was
added to the working materials, and fifteen measurement papers were entered in the bibliography.

- `tools/validate.py` passes: 23 chapter files, 13 consecutive Tuesdays, 31 assigned papers, 113
  bibliography records (the last two are the ambient-noise papers added when the instruments and
  methods rows were split); all citation keys and local links resolve; Pandoc processes every
  citation without warnings.
- `tools/check_links.py`: 137 distinct URLs across 24 source files; every DOI registered on Crossref.
  Four publisher 403s are bot mitigation. The two GitHub links to the audit files return 404 and 429
  until the commit is pushed.
- `quarto render` produced all 23 pages, including `glossary.html` and `corpus-study.html`.

## September 6, 2026, after the plan audit and the second pass

Run on macOS with Quarto 1.9.38, Pandoc 3.9.0.2, and Python 3.14 in the local virtual environment,
after fifty-seven optional extensions were added and five audit recommendations were adopted: the
inquiry-mode ledger, discussant-led papers in meetings 1, 6, and 9, the swap of meetings 11 and 12,
and Cleland 2001 as Paper B of meeting 1 (see `PLAN-AUDIT.md`).

**Source checks — `tools/validate.py`, passing.**

- 21 chapter files, 13 consecutive Tuesdays, 31 assigned papers (26 paired, 5 discussant-led), 96
  bibliography records.
- BibTeX keys and `curriculum.json` metadata describe the same set.
- New check: every key in a meeting's `optional` list exists and is cited on that meeting's page.
- Pandoc parses the Markdown and processes all citations without warnings.

**External links — `tools/check_links.py`.** 122 distinct URLs across 22 source files.

- All 96 DOIs are registered, verified individually against the Crossref API. This includes the
  Geology DOI for Cleland 2001, which contains angle brackets and is percent-encoded in the sources;
  the checker now decodes a DOI before querying the registry.
- Five publisher URLs answer an automated request with 403 (Wiley, SAGE, Annual Reviews, two
  ScienceDirect). Bot mitigation, as before; the DOIs resolve.
- One GitHub link is unresolved only because the commit has not been pushed: the link to
  `PLAN-AUDIT.md` returns 404 until the file is on `main`. Re-run after pushing.

**Quarto build.** `quarto render` completed and produced all 21 pages in `_book/`, including the
renamed session files `11-polymathy` and `12-scientific-advance`, the discussant-led sections on
meetings 1, 6, and 9, the ledger on the rubrics and notes pages, the new optional-extension
sections on every session page, and the lineage section in the prior-art chapter. Stale HTML from
the pre-swap file names was removed from the local build directory.


## v0.3, September 5, 2026

Run on macOS with Quarto 1.9.38, Pandoc 3.9.0.2, and Python 3.14 in a local virtual environment.

**Source checks — `tools/validate.py`, passing.**

- 21 chapter files referenced by `_quarto.yml` exist.
- 13 sessions fall on consecutive Tuesdays, September 8 – December 1, 2026.
- Every session has exactly two required papers; meeting 13 additionally declares two
  discussant-led papers, and all four are cited on its page.
- 28 assigned papers and 39 bibliographic keys; the BibTeX keys and the `curriculum.json`
  reference metadata describe the same set.
- Local QMD source links and citation keys resolve.
- No path under `private/` is registered as a chapter, and the `.gitignore` rule excluding it
  is present.
- Pandoc parses the Markdown and processes the BibTeX citations without warnings.

**Quarto build — executed for the first time in this repository.** `quarto render` completed,
producing all 21 pages in `_book/` with no errors. The sidebar shows the four parts and every new
chapter. This closes the gap recorded in the v0.2 note below.

**External links — `tools/check_links.py`.**

- All 39 DOIs are registered, verified individually against the Crossref API rather than by
  fetching the publisher page. This includes the three records previously flagged as unverified:
  `machado2026`, the 2026 correction to `shibayama2021`, and the ACL Anthology record for
  `novbench2026`.
- Every prior-art entry was checked against the arXiv API before being listed; titles, authors,
  and identifiers match.
- Five direct publisher URLs (Wiley, SAGE, Annual Reviews, two ScienceDirect) answer an automated
  request with 403. These are bot mitigation, not broken links; the corresponding DOIs resolve.

## Not verified by these tests

Browser layout, sidebar and search behavior, mobile table overflow, and accessibility have not been
reviewed by a person. The deployed site has not been checked, because publication had not yet
happened when these checks were run.

The GitHub link to `READING-AUDIT.md` in `index.qmd` and `suggested-readings.qmd` returns 404 until
the repository is public at `Denolle-Lab/metascience-and-AI`. Re-run `tools/check_links.py` after
the transfer; it should then report no failures.

URLs identify publication records or full-text sources. They do not guarantee open access, an
institutional entitlement, or permanent availability. No third-party journal PDF, font file,
credential, or unpublished research dataset is bundled.

## v0.2, earlier source-package check

The preparation environment did not contain the Quarto CLI, so the full Quarto build, rendered
sidebar and search behavior, browser layout, and accessibility remained untested at v0.2. A separate
single-page Pandoc reading preview was produced and its internal fragment links resolved; that
preview was not the Quarto website output. The staging script's help, missing-build guard, copy
behavior, and overwrite refusal were tested in temporary directories.
