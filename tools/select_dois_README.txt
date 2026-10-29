CITATION-BALANCED DOI SELECTION AND FOLLOW-UP
=============================================

Use tools/select_dois.py for discovery and citation snapshots, then use
publisher-specific services for article full text. It needs Python 3.10+
and no extra packages. All outputs default to the ignored private/corpus/.

The chosen default is a citation-balanced sample: equal numbers from ten
OpenAlex citation-normalized percentile bands, adjusted for publication
year, work type, and primary subfield. N must be a multiple of 10.
For example, N=200 selects 20 from each band. This is a balanced study
sample, not an unweighted representation of the publication population.

1. PREPARE ACCESS

Run these commands from the repository root:

  cd /Users/marinedenolle/GitHub/metascience-and-AI

Obtain an OpenAlex API key from your OpenAlex account's settings. It is
separate from the Wiley TDM token. Selection and refresh read
OPENALEX_API_KEY or prompt privately when you run interactively. Lookups
can use limited anonymous access. Free-account usage allowances apply;
this script does not upgrade an account or buy anything.

2. RESOLVE JOURNAL AND DISCIPLINE NAMES

  python3 tools/select_dois.py lookup --kind sources --query "Geophysical Research Letters"
  python3 tools/select_dois.py lookup --kind fields --query "Earth and Planetary Sciences"
  python3 tools/select_dois.py lookup --kind subfields --query "Geophysics"

Check journal title and ISSN in the output before selecting an ID.
Journal IDs begin S; field/subfield IDs are numbers. Earth and Planetary
Sciences is field 19. A primary field is assigned to each individual
paper, not simply inherited from its journal. Multidisciplinary journals
such as Nature contain papers in many primary fields.

3. REVIEW AND SELECT N PAPERS

Example: 200 research articles on machine/deep learning and seismology,
published 2018-2022, with primary field Earth and Planetary Sciences:

  python3 tools/select_dois.py select --name ai-seismology-balanced --n 200 \
    --query '("machine learning" OR "deep learning") AND (seismic OR earthquake)' \
    --field 19 --from 2018-01-01 --to 2022-12-31 --seed 2026 --dry-run

Remove --dry-run to perform the selection. That switch only prints the
query plan and makes no network requests; it does not count availability.

To restrict this example to particular journals, add --source followed
by an S ID from lookup. Repeat --source for each journal, e.g.:

  --source S123456 --source S789012

Those two S IDs are placeholders: use the real IDs returned by lookup.
Repeat --field or --subfield to allow multiple disciplines at that level.
Within one kind of filter, alternatives are ORed. Different kinds of
filter are ANDed: keywords AND journal selection AND discipline AND date.
Dates are inclusive. Omit --source to allow all journals. The default
work type is article and retracted works are excluded.

Keywords search titles and abstracts by default, with uppercase AND,
OR, NOT and double quotes for phrases. --search-scope all broadens search
to available full text and OpenAlex's keyword tags. Missing abstracts
and index coverage can affect retrieval. Use a pilot selection and read
titles/abstracts to check relevance before freezing a large cohort.

BALANCING RULES

- The ten percentile bands are [0,0.1), [0.1,0.2), ... [0.9,1].
- Each receives N/10 papers chosen using a recorded random seed.
- The normalized metric already controls for year/type/subfield. Equal
  deciles do not additionally guarantee equal counts per journal or year.
- Uncited papers remain eligible where their normalized metric places
  them. Zero percentiles are valid; missing percentiles are excluded and
  their number reported. Missing metrics are never converted to zero.
- Ties and a narrow topical/journal population can leave bands empty or
  too small. The selector reports shortages and stops without saving an
  incomplete or silently rebalanced cohort. Broaden filters or reduce N;
  an empty band cannot be repaired merely by reducing N.
- Metadata records eligible and selected counts in each band and the
  sampling fractions. This permits later inverse-probability weighting for eligible works with
  known normalized percentiles; it does not represent missing-percentile works.
- A fixed seed reproduces a query against the same index state, but
  OpenAlex changes. The saved cohort is the authoritative fixed sample.

Citation restrictions are available but can conflict with full-decile
balance. --min-citations 50 / --max-citations 500 use inclusive raw-count
bounds. --top-10-percent asks for the normalized top 10%; combine it with
--method random rather than balanced, since the other nine deciles would
be empty. --method most-cited selects the most-cited N, and is deliberately
not balanced. For the chosen study, retain --method balanced (the default).

4. KEEP THE FROZEN COHORT AND BASELINE

For the example, outputs are:

  private/corpus/ai-seismology-balanced.jsonl
      Fixed per-paper records: DOI, OpenAlex ID, title, date, journal,
      primary discipline, selection band, citations, normalized percentile,
      FWCI, annual citation counts and the UTC retrieval time.
  private/corpus/ai-seismology-balanced.dois.txt
      One DOI per line, for a publisher downloader.
  private/corpus/ai-seismology-balanced.meta.json
      Public query parameters, seed, selected/eligible counts, balancing
      rules, missing-percentile exclusions, and per-band sampling fractions.
  private/corpus/ai-seismology-balanced.citations.jsonl
      Initial citation observations, then appended dated updates.

Existing cohorts are not overwritten. Use a new name for a new selection.
Keep the original manifest and metadata unchanged for analysis provenance.

If the selected journals are Wiley titles, download their articles with:

  python3 tools/download_wiley.py private/corpus/ai-seismology-balanced.dois.txt --limit 1
  python3 tools/download_wiley.py private/corpus/ai-seismology-balanced.dois.txt

The Wiley script prompts for the separate Wiley token; PDFs and its log
stay in private/pdfs/wiley/. For mixed publishers, download each subset
through that publisher's appropriate service. OpenAlex discovery and
citation metrics do not grant full-text access.

5. UPDATE CITATIONS FOR THE SAME PAPERS

  python3 tools/select_dois.py refresh private/corpus/ai-seismology-balanced.jsonl

Repeat when you want another measurement (for example monthly). Refresh
appends snapshots and records failures explicitly; it does not reselect
papers, change the baseline, or move them into different selection bands.
No automatic schedule is created by these instructions.

INTERPRETING IMPACT

Keep raw cited_by_count, the normalized percentile, FWCI, and the date of
measurement. FWCI=1 is the expected citation impact for the reference
set; 2 means twice expected. Its window is the publication year plus the
three following years. Do not equate normalized percentile with a raw
citation count or assume it uses exactly the same time window as FWCI.

For longitudinal analysis, compare snapshots for each fixed OpenAlex ID.
A difference in total citations is a change in indexed citations: backfill,
merges and corrections can also change counts. Preserve failed/missing
observations as missing rather than zero. counts_by_year covers a moving
10-year history and can omit zero years; it is not an archived snapshot
of what the database knew on a historical date.

A citation-balanced design overrepresents citation bands that are sparse
in the eligible pool. Use the saved sampling fractions for population
estimates or report results conditional on the bands. In particular,
unweighted mean citations and top-10% shares from this selected cohort
are not estimates of those quantities for all eligible publications.
For AI/control comparisons, also match or adjust publication year and
subfield and use comparable follow-up windows. Citation measures capture
one dimension of impact, not correctness or scientific advance.

This companion does not change the existing corpus.py or indicators.py.
Their older sampling and reporting behavior differs; use select_dois.py
for the exact-N, keyword-filtered, balanced and longitudinal workflow here.

JOURNAL PRESETS, REVIEW ARTICLES AND AVAILABILITY CHECKS

--journal-set nature-earth-environment includes six verified Nature
journals; individual presets and repeatable --issn are also available.
Use --source OR the ISSN/preset method in one command. Preset journals are
pooled, so pooled citation balance does not guarantee equal journal counts.
Run an individual preset separately at the same N for equal journal quotas.

--work-type article is the default; add --work-type review to include
reviews, especially Nature Reviews Earth & Environment. Both types can
be requested together and the type is retained in the frozen records.

--availability-only counts candidates and each citation band, draws no
sample and writes no cohort files. It requires an OpenAlex API key.
Combining it with --dry-run only displays the unsampled query plan and
makes no requests, so that combination cannot establish feasibility.
See tools/nature_workflow_README.txt for complete Nature examples and
Springer Nature JATS XML access.

OFFICIAL REFERENCES (checked 22 October 2026)

Search and Boolean queries:
https://help.openalex.org/api/searching/
Filters and numeric bounds:
https://help.openalex.org/api/filtering/
Fields and classification:
https://help.openalex.org/data/fields/
Citation metrics:
https://help.openalex.org/data/works/citations/
Metric attributes and annual histories:
https://help.openalex.org/data/works/attributes/
API key/access:
https://help.openalex.org/api/authentication/
Sampling and paging recipes:
https://help.openalex.org/how-to/api-recipes/
https://help.openalex.org/api/paging/
