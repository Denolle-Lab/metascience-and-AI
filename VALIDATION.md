# Validation performed

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
