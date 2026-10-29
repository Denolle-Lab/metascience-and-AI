NATURE DATASET: ONE FIXED PROTOCOL, SIX BALANCED JOURNAL SAMPLES
==============================================================

The scripts use Python 3.10+ and the standard library. From the repository:

  cd /Users/marinedenolle/GitHub/metascience-and-AI

QUICK START

1. Edit templates/nature-dataset.example.json or copy it to your own config.
   Set the study name, journals, papers PER JOURNAL, topic query and fixed
   inclusive publication dates. The shipped 2023-2025 and N=100 values are
   examples; an empty query includes all topics within the chosen journals.

2. Inspect the resolved protocol. This sends no requests and needs no keys:

   python3 tools/nature_dataset.py plan --config templates/nature-dataset.example.json

   Add --show-api-queries to inspect the complete per-journal API requests.

3. Count eligibility in EVERY journal and citation band before sampling:

   python3 tools/nature_dataset.py availability --config templates/nature-dataset.example.json

4. When the counts and criteria are acceptable, freeze the complete study:

   python3 tools/nature_dataset.py select --config templates/nature-dataset.example.json

5. Test one full-text retrieval, then download the cohort:

   python3 tools/nature_dataset.py download --study private/datasets/nature-earth-environment-example --service oa --limit 1
   python3 tools/nature_dataset.py download --study private/datasets/nature-earth-environment-example --service oa

   With separately activated, licensed Full Text API/TDM access:

   python3 tools/nature_dataset.py download --study private/datasets/nature-earth-environment-example --service tdm --limit 1

6. Update citations for the SAME selected papers later:

   python3 tools/nature_dataset.py refresh --study private/datasets/nature-earth-environment-example

PARAMETERS

The example configuration contains:

  name: a short study identifier; use a new name for a new frozen study
  journals: individual preset names, listed below
  n_per_journal: the SAME N for each journal; positive and divisible by 10
  publication_start: YYYY-MM-DD, inclusive
  publication_end: YYYY-MM-DD, inclusive
  query: Boolean keywords over titles and abstracts; empty means all topics
  fields: optional OpenAlex primary field IDs, e.g. ["19"]
  subfields: optional OpenAlex primary subfield IDs
  work_types: ["article"], ["review"], or both
  seed: fixed integer seed, recorded in the frozen protocol

Keywords can use uppercase AND, OR, NOT and double-quoted phrases:

  ("climate change" OR "global warming") AND (water OR ecosystem)

Command-line overrides let you reuse a config while saving the actual
resolved values in the resulting study protocol:

   python3 tools/nature_dataset.py plan \
     --config templates/nature-dataset.example.json \
     --query '("climate change" OR "global warming") AND (water OR ecosystem)' \
     --from 2023-01-01 --to 2025-12-31 --n-per-journal 100

Use the same overrides for availability and select. The topic parameter is
text search, not a guarantee of topical relevance. Inspect pilot titles and
abstracts and freeze the chosen eligibility expression before your study.

Individual journal presets:

  nature-geoscience                 Nature Geoscience
  nature-communications             Nature Communications
  communications-earth-environment Communications Earth & Environment
  nature-reviews-earth-environment  Nature Reviews Earth & Environment
  nature-water                      Nature Water
  nature-sustainability             Nature Sustainability

--journal PRESET can be repeated to override the config's journal list.
These presets use publisher-verified electronic ISSNs. The study script
requires individual journals, not a pooled journal group.

Nature Water started in 2023. Date windows before that will not give it
papers; a common window from 2023 covers all six journals. Recent windows
provide shorter citation follow-up. Reviews need work_types to include
"review", particularly for Nature Reviews Earth & Environment. Keep article
and review type in your later analysis; they differ scientifically even
when the citation metric controls for type.

Find discipline IDs with the existing helper:

   python3 tools/select_dois.py lookup --kind fields --query "Environmental Science"
   python3 tools/select_dois.py lookup --kind subfields --query "Geophysics"

Do not automatically force field 19 on all environmental topics; a paper
can have another relevant primary field. Different eligibility dimensions
are ANDed; alternatives inside the same field/journal level are ORed.

BALANCING AND FAILURE RULES

Each journal contributes N papers. Within each journal, N/10 are drawn
from each OpenAlex year/type/subfield-normalized citation percentile band:
[0,.1), [.1,.2), ... [.9,1]. For N=100 and six journals, this means 600
papers total and 10 per journal x citation-band cell.

These are fixed global normalized percentile bands, not ranks recomputed
within each journal. A selective journal or narrow topic may lack papers
in a low band. The availability step reports the exact shortfalls and
missing percentile counts. Empty bands cannot be filled by reducing N.
The scripts do not silently switch bin definitions, borrow papers from a
different band, replace journals, or select only accessible articles.

Selection first checks ALL journals. If ANY journal is short, no sample is
drawn. If an API failure occurs during sampling, the partial study is not
published as a completed study. Journal files and combined artifacts are
assembled in a temporary directory, validated together, then renamed into
the final study folder only after the full sample succeeds.

Missing normalized metrics remain missing and are excluded explicitly.
Zero is a valid percentile. Every selected work retains its citation band
and sampling probability. Sampling weights describe eligible indexed works
with known percentiles; they do not recover excluded missing-metric works.
An unweighted citation-balanced sample does not estimate the full eligible
population's citation distribution.

PUBLICATION WINDOW VERSUS CITATION MEASUREMENT TIME

The fixed start/end dates filter PUBLICATION dates. Citation counts and
normalized metrics are observed when the API is queried, not as they were
at publication_end. The saved baseline includes the observation time;
refresh appends later observations. Current counts cannot reconstruct a
historical database snapshot. OpenAlex classifications/metrics can change,
so retain the saved metadata rather than rerunning a query to recreate it.

OUTPUTS

Default study location:

  private/datasets/<study-name>/

Contains:
  study.json                    frozen resolved protocol, hash and provenance
  manifest.jsonl                combined fixed cohort, with journal and strata
  dois.txt                      combined DOI list
  manifest.citations.jsonl      authoritative combined citation history
  cohorts/                      each journal's original cohort and query metadata
  xml/                          full-text JATS XML and download results.csv

The parent private/ folder is ignored by Git. The study refuses to overwrite
an existing completed study. A new selection needs a new study name. The
original protocol and cohort hashes are checked before downloads or citation
refresh. Download and refresh use --study, not a newly edited configuration;
changing the example config cannot silently change an existing sample.

The combined citation history is authoritative for follow-up. Per-journal
files under cohorts/ retain their selection-time records and baseline
snapshots. Refresh never changes selected membership or the baseline cohort.
A failed refresh is recorded explicitly rather than converted to zero.
Join follow-up citation observations to manifest.jsonl on the stable key
field to recover the original journal and selection-time citation band;
follow-up rows do not repeat all of that baseline context.

API ACCESS AND DOWNLOADS

OpenAlex discovery/metrics: OPENALEX_API_KEY, or the helper's hidden terminal
prompt. It is separate from Springer Nature credentials.

Open Access XML: SPRINGER_OA_API_KEY (or SPRINGER_API_KEY), with Open Access
API access activated. Licensed XML: SPRINGER_TDM_API_KEY as KEY/METRIC, or
SPRINGER_TDM_API_KEY plus SPRINGER_TDM_METRIC separately. A hidden terminal
prompt is supported. Never place any credential in the study config.

The downloader uses the documented JATS XML routes:
  https://api.springernature.com/openaccess/jats
  https://api.springernature.com/xmldata/jats

Licensed access depends on the Full Text API agreement and content
entitlements. Browser sign-in/subscription alone does not establish API
access. Missing coverage is logged; preserve those papers in the cohort
and handle availability separately from scientific eligibility.

Downloads use ONE combined DOI list and ONE request budget across all six
journals. The default --max-requests 450 includes retries for that run.
This is not account-wide daily quota tracking; other runs/tools share the
provider allowance. The current published free OA allowance is 500/day.
A 600-paper study can exceed that allowance. Check your activated plan,
use the portal's limits, and resume when quota permits. Existing validated
XML is skipped; inaccessible articles are not silently replaced.

Use --limit 1 for a pilot. Other download controls include --max-requests,
--interval, and --retries. The wrapper delegates XML validation, safe logs,
retry/backoff, atomic saves and explicit access failures to download_nature.py.
JATS XML contains structured article text; linked figures/supplements are
not automatically fetched. See nature_workflow_README.txt for access details.

No keys, accounts, paid plan upgrades, live corpus, or article downloads
are created by installing these scripts. Offline tests use mocked APIs.

OFFICIAL REFERENCES

Full Text API:
https://dev.springernature.com/docs/api-endpoints/fulltext-api/
Open Access API:
https://dev.springernature.com/docs/api-endpoints/open-access/
Query parameters:
https://dev.springernature.com/docs/supported-query-params/
API quotas:
https://dev.springernature.com/subscription/
OpenAlex searching and metrics:
https://help.openalex.org/api/searching/
https://help.openalex.org/data/works/citations/
