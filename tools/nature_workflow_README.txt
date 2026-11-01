NATURE JOURNALS: CITATION-BALANCED SELECTION AND FULL-TEXT XML
===========================================================

Python 3.10+, no extra packages. Run commands from:
  /Users/marinedenolle/GitHub/metascience-and-AI

PREFERRED COMPLETE STUDY WORKFLOW

Use tools/nature_dataset.py with templates/nature-dataset.example.json
for one common topic query, fixed dates and equal N per journal. It checks
all journals before sampling and freezes the combined study only after
all journal quotas succeed. See tools/nature_dataset_README.txt for the
plan, availability, select, download and refresh commands. The individual
commands below remain available for inspecting or running one journal.

SIX VERIFIED JOURNAL PRESETS

Preset                               Journal                              Electronic ISSN
nature-geoscience                    Nature Geoscience                    1752-0908
nature-communications                Nature Communications                2041-1723
communications-earth-environment      Communications Earth & Environment   2662-4435
nature-reviews-earth-environment      Nature Reviews Earth & Environment   2662-138X
nature-water                         Nature Water                         2731-6084
nature-sustainability                Nature Sustainability                2398-9629

The group --journal-set nature-earth-environment includes all six.
Communications Earth & Environment and Nature Reviews Earth & Environment
are separate journals; both are included. Names/ISSNs are recorded in the
query metadata. No journal-source ID lookup is needed for these presets.

Nature Water began in 2023; Nature Reviews Earth & Environment and
Communications Earth & Environment began in 2020. A window starting in
2023 covers all six journals, but recent papers have shorter citation
follow-up. The dates below are EXAMPLES, not a selected study protocol.

CHOSEN STUDY DESIGN

Use the SAME N PER JOURNAL, balanced across normalized citation bands
WITHIN EACH JOURNAL. Keep six separate frozen cohorts with the same dates,
query and article-type policy. For example N=100 per journal means 600
papers total and 10 per citation band in each journal, if feasible.
The pooled group preset is available for other designs but is not the
chosen study design.

STEP 1: CHECK WHETHER YOUR CITATION-BALANCED SAMPLE IS POSSIBLE

Start with one journal, for example Nature Geoscience, N=100:

  python3 tools/select_dois.py select \
    --name nature-geoscience-2023-2025 --n 100 \
    --journal-set nature-geoscience \
    --work-type article --work-type review \
    --from 2023-01-01 --to 2025-12-31 --seed 2026 \
    --availability-only

This uses your OpenAlex API key (OPENALEX_API_KEY or a hidden terminal
prompt), counts the base pool and each citation band, and draws nothing.
It creates no cohort files. Adding --dry-run prints the plan without
using a key or making requests, so it cannot establish availability.

Each sample has N/10 papers from each normalized citation percentile
band [0,.1), [.1,.2), ... [.9,1]. N must be divisible by ten. OpenAlex's
percentile adjusts for year, type and primary subfield. A low global
percentile band might be empty in a selective journal. The tool reports
this and does not borrow papers from another band, change the bins, or
silently substitute journals. Broaden the dates/eligibility or revise
the sampling design explicitly if a band is empty; reducing N alone
cannot fill an empty band. Missing percentiles are counted and excluded.

--work-type review is important for Nature Reviews Earth & Environment.
The default is article only; specifying both retains eligible articles
and reviews. Preserve type for analysis because these are different kinds
of contribution, even when the citation measure accounts for work type.

To check all six separately with the same N, repeat the command for each
individual preset. This gives each journal its own quotas and report.
A combined preset pools the journals; Nature Communications may dominate
that pool. Pooled citation balance does not ensure equal journal counts.

For one command covering the chosen six-journal availability check:

  for journal in nature-geoscience nature-communications communications-earth-environment nature-reviews-earth-environment nature-water nature-sustainability
  do
    python3 tools/select_dois.py select \
      --name "${journal}-2023-2025" --n 100 --journal-set "$journal" \
      --work-type article --work-type review \
      --from 2023-01-01 --to 2025-12-31 --seed 2026 --availability-only
  done

Each report is labelled with its cohort name. All six must have sufficient
papers in every band before this example can yield the full 600-paper study.
Remove --availability-only from this loop only after accepting the counts
and final eligibility criteria. Each journal then gets its own manifest,
DOI list, metadata and citation history. N=100 and these dates are examples.

Optional restrictions, appended to the same command:
  --query '("machine learning" OR "deep learning") AND (seismic OR earthquake)'
  --field 19
  --subfield SUBFIELD_ID_FROM_LOOKUP

Different restrictions are ANDed; repeated journal/field/subfield options
are ORed at the same level. The keyword search defaults to title/abstract.
Do not impose field 19 automatically on all environmental journals: many
relevant papers can have other primary fields. For discipline IDs use:

  python3 tools/select_dois.py lookup --kind fields --query "Environmental Science"

Manual --issn and --journal-set can be combined. They cannot be combined
with --source: choose one journal identification method per command.

STEP 2: FREEZE THE SAMPLE WHEN AVAILABILITY AND ELIGIBILITY ARE ACCEPTABLE

Repeat the command without --availability-only:

  python3 tools/select_dois.py select \
    --name nature-geoscience-2023-2025 --n 100 \
    --journal-set nature-geoscience \
    --work-type article --work-type review \
    --from 2023-01-01 --to 2025-12-31 --seed 2026

For equal numbers per journal, run the same N for each individual preset.
For a single pooled sample, use --journal-set nature-earth-environment
and treat N as the TOTAL across all six. These are different designs.

Outputs, all ignored by Git:
  private/corpus/NAME.jsonl              fixed sample and baseline metrics
  private/corpus/NAME.dois.txt           DOI list for downloading
  private/corpus/NAME.meta.json          eligibility, quotas, counts, weights, seed
  private/corpus/NAME.citations.jsonl    initial and later citation observations

The tool refuses to overwrite an existing cohort. Each row includes its
citation band and sampling probability. Weighted population estimates
apply to eligible indexed works with known percentiles, not excluded
missing-percentile works. Unweighted summaries describe this intentionally
balanced sample. For journal comparisons, retain journal/year/type/subfield
and use comparable citation follow-up windows.

STEP 3: PROVISION THE MATCHING SPRINGER NATURE API ACCESS

OpenAlex's key is for discovery/metrics; Springer Nature's key is separate.
Create/sign in to the Springer Nature Developer Portal and enable the API
you need under API Management / API Keys:
  https://dev.springernature.com/

OA route: a key with Open Access API access. Python reads SPRINGER_OA_API_KEY
(or SPRINGER_API_KEY) or prompts privately in a terminal.

Licensed route: Full Text API/TDM access and entitlement to the selected
content, under the applicable UW agreement. Use the KEY/METRIC credential
provisioned in the portal. Python reads SPRINGER_TDM_API_KEY, either as the
complete KEY/METRIC or with SPRINGER_TDM_METRIC supplied separately; it can
also prompt privately for the complete credential. A metadata-only key or
normal browser subscription is not proof of Full Text API entitlement.

Nature Communications and Communications Earth & Environment are currently
open-access journals, but API coverage still needs article-level checking;
older Nature Communications content predates its full-OA transition.
For the other titles, OA articles can be attempted through the OA route;
non-OA content requires matching licensed access. The script never scrapes
nature.com article pages or bypasses access controls.

STEP 4: TEST A SINGLE DOI AND DOWNLOAD XML

Validate your DOI list without keys or network:

  python3 tools/download_nature.py \
    private/corpus/nature-geoscience-2023-2025.dois.txt --dry-run

Try the first DOI via the OA API:

  python3 tools/download_nature.py \
    private/corpus/nature-geoscience-2023-2025.dois.txt --service oa --limit 1

Then try the full list:

  python3 tools/download_nature.py \
    private/corpus/nature-geoscience-2023-2025.dois.txt --service oa

With licensed Full Text API access, use:

  python3 tools/download_nature.py \
    private/corpus/nature-geoscience-2023-2025.dois.txt --service tdm --limit 1

Remove --limit 1 for the remaining batch. Using the same output folder
skips XML already retrieved via either route. DOI lists can also be CSV
with a DOI column (--doi-column chooses another name).

DEFAULT OUTPUT

  private/xml/nature/<encoded-doi>--<hash>.xml
  private/xml/nature/results.csv

Saved XML contains the matching JATS article, including its front/body/back
and permissions when present, rather than the surrounding API envelope.
The script rejects metadata-only records, an incorrect DOI, invalid XML,
and a missing/empty body. It uses temporary files and validates existing
XML before skipping it. XML serialization can change namespace prefixes;
this is not a byte-for-byte preservation of the API response.

JATS XML is structured full text, not HTML. The official API does not
provide a corresponding documented HTML switch. Article images and
supplementary files referenced by XML are not automatically downloaded.
The article license/institutional agreement governs use and retention.
Full text and logs stay under private/, outside published book content.

ACCESS FAILURES AND QUOTAS

Unavailable coverage/entitlement is logged explicitly; it is not evidence
that a DOI is invalid. Keep inaccessible selected papers in the fixed
cohort and treat full-text availability separately. Replacing them with
only accessible papers would change the sampling design.

Requests are sequential, at least 1.1 seconds apart by default. Retries
honor Retry-After and count toward --max-requests (default 450 per RUN).
After unresolved 401, 403 or 429, or a depleted local budget, the run stops.
This per-run guard is not account-wide daily tracking. Other runs/tools
share your provider allowance; check the portal before rerunning.

Published free OA limits are currently 500/day and 100/minute; higher and
licensed plans differ. Thus 600 requested files can exceed a free daily
allowance even when spread across separate script runs. Errors/retries
may also consume allowance. The script does not buy/upgrade an API plan.

STEP 5: TRACK CITATIONS WITHOUT CHANGING THE SAMPLE

  python3 tools/select_dois.py refresh \
    private/corpus/nature-geoscience-2023-2025.jsonl

Repeat for each journal cohort on your chosen measurement dates. Refresh
appends citation snapshots and explicit failures without reselecting papers.
The selection-time percentile band stays fixed even if later counts or
classification change. No automatic schedule is created.

CHECKS AND LIMITS OF VALIDATION

The downloader, presets, exact quotas, shortage behavior, logs that omit
credentials, request budgets, resuming and citation snapshots have offline tests.
No live cohort or full-text retrieval was performed during implementation.
A real one-DOI test is needed with your activated API service and its
entitlements before planning a large batch.

OFFICIAL SOURCES (checked 22 October 2026)

Journal information, including electronic ISSNs:
https://www.nature.com/ngeo/journal-information
https://www.nature.com/ncomms/journal-information
https://www.nature.com/commsenv/journal-information
https://www.nature.com/natrevearthenviron/journal-information
https://www.nature.com/natwater/journal-information
https://www.nature.com/natsustain/journal-information

OA API / licensed Full Text API / DOI queries:
https://dev.springernature.com/docs/api-endpoints/open-access/
https://dev.springernature.com/docs/api-endpoints/fulltext-api/
https://dev.springernature.com/docs/supported-query-params/

Current host migration (old spdi host retired 7 August 2026):
https://dev.springernature.com/docs/full-text-api-migration-guide/

Quotas, User-Agent guidance and terms:
https://dev.springernature.com/subscription/
https://support.springernature.com/en/support/solutions/articles/6000251800-text-and-data-mining-tdm
https://dev.springernature.com/terms-conditions/

OpenAlex journal filters and metric interpretation:
https://help.openalex.org/api/filtering/
https://help.openalex.org/data/works/citations/
https://help.openalex.org/data/works/attributes/
