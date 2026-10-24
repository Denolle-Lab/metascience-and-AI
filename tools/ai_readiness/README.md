# Offline AI-readiness study extension

This module connects the existing DOI/OpenAlex selection, Nature JATS retrieval,
local PDF queue and semantic inquiry coding to a separate, evidence-first
AI-readiness study. It does not duplicate retrieval, import API clients, load
credentials, submit model jobs or publish anything. All examples write under
`private/`, which remains excluded from this public repository. No article full
text, personal research data, private study results or credentials belong in Git.

Run from the repository root with Python 3.10+ and `PYTHONPATH=tools`. The analysis
module needs only the standard library. Plotting additionally needs Matplotlib in
your existing Python environment; no dependency is installed automatically.

## Start with an existing frozen cohort

Use the existing `tools/select_dois.py`, `tools/nature_dataset.py`, or
`tools/corpus.py` files and their manifests; this module makes no new requests.
The original tools' separate credentials, cost and license rules still apply.

```sh
export PYTHONPATH=tools
python3 -m ai_readiness import \
  --input private/corpus/earth-pilot.jsonl --out private/readiness/earth-2026-10-23 \
  --cohort earth-pilot --ontology earth_measurement_families
python3 -m ai_readiness screen \
  --input private/readiness/earth-2026-10-23/works.jsonl \
  --out private/readiness/earth-2026-10-23/screen.jsonl
```

The import accepts raw OpenAlex JSON/JSONL, `select_dois` manifests, Nature's
`manifest.jsonl`, and legacy `corpus.py` JSONL. It normalizes DOI aliases and rejects
duplicate keys/DOIs/IDs rather than silently replacing a sampled item. An ID-less
legacy record uses a `doi:` identity, never a fabricated OpenAlex work ID. Missing
abstracts remain missing; a title-only screen is not a negative actual-use label.
All original fields and input hashes are retained in the private run.

## Preserve a documented sampling design

For an existing `select_dois` random or citation-balanced cohort:

```sh
python3 -m ai_readiness bind-selection \
  --run private/readiness/earth-2026-10-23 \
  --metadata private/corpus/earth-pilot.meta.json \
  --out private/readiness/earth-2026-10-23/design.json
python3 -m ai_readiness attach-design \
  --input private/readiness/earth-2026-10-23/screen.jsonl \
  --design private/readiness/earth-2026-10-23/design.json \
  --out private/readiness/earth-2026-10-23/sampled_screen.jsonl
```

For Nature, pass the original study's `study.json` instead. Its manifest and
protocol hashes and child `cohorts/*.meta.json` counts are checked. Direct selector
metadata must be the original `.meta.json` sibling of the imported `.jsonl`;
counts, original IDs, bin memberships, probabilities and inverse weights must
agree. Legacy selector metadata does not contain a historic manifest hash: the
new import records its current hash and safeguards routine file mismatches, but
cannot retroactively prove an original cryptographic draw. Keep original receipts.

Ranked/most-cited samples and legacy `corpus.py` output are **descriptive only**.
The legacy corpus may have capped pools and lacks per-paper inclusion
probabilities; its pool/drawn counts do not establish a probability design. If
using a separately verified complete population frame, the `sample` command can
reuse the pilot's `manifest.json` (complete flag, exact identity digest and works
file SHA), sample every source/year/AI-screen stratum including negatives, and
save a bound draw. Never present a selected cohort as a complete frame or resample
only AI-positive papers. A weighted frame can itself be narrowly query-restricted;
weights do not make it representative of all Earth science or all CS.

## Review and record evidence

```sh
python3 -m ai_readiness template \
  --input private/readiness/earth-2026-10-23/sampled_screen.jsonl \
  --out private/readiness/earth-2026-10-23/annotations_blank.jsonl
```

Without a probability design, use `screen.jsonl` directly and report descriptively.
Annotators save a new `annotations_adjudicated.jsonl`, retaining paper IDs and
assignments. The CLI refuses existing output paths to protect previous reviews.
`annotation.schema.json` is the full portable contract; runtime validation enforces
the evidence, consistency and inferential gates used by reports.

A completed review requires a named reviewer, full-text access and evidence. Use
`pending`, `inaccessible` or `adjudication` when appropriate. Record short excerpts,
URLs and methods/results sections or pages for each positive actual-use label.
Metadata/API-coder output cannot mark an article human-reviewed automatically.

The labels distinguish:

- Actual AI use, actual deep-learning use, foundation-model use and foundation-model
  **pretraining**. Fine-tuning, inference, frozen features and evaluation of an
  existing model are not automatically pretraining. This codebook's neural
  foundation models require DL=yes and AI=yes.
- Supervised, self-supervised, semi-supervised, pseudo-label/self-training and
  reinforcement learning. Multiple regimes may coexist; explicit evidence supports
  each regime. Do not infer a regime from the model name.
- Scientific measurement families versus platforms or file representations. Two
  image files from the same measurement family are not automatically multimodal.
  CS runs instead use named text/image/audio/tabular/graph/proprioceptive information
  channels; this is a distinct ontology requiring a sensitivity analysis to compare.
- Data access, machine readability, physical/inter-experiment compatibility,
  training scale, independent evaluation and community reuse as separate dimensions.
  They do not form an invented universal maturity score.
- Small-model comparisons with the actual task, models, metric, tuning/data/compute
  conditions and evidence. No universal parameter-count cutoff or causal adequacy
  conclusion is inferred.
- Explicit author explanations for access, labels, interoperability, computing,
  skills, transfer/evaluation or small-model adequacy versus assessor hypotheses.
  Non-use and publication counts alone do not reveal why authors did not use AI.

## Reuse semantic coding and local full-text manifests

```sh
python3 -m ai_readiness bridge \
  --run private/readiness/earth-2026-10-23 --repo . \
  --queue private/download-queue.json \
  --codings private/analysis/codings/api/pilot \
  --assets private/corpus/nature-pilot/xml/download_log.csv \
  --out private/readiness/earth-2026-10-23/evidence_queue.jsonl \
  --semantic-manifest private/readiness/earth-2026-10-23/semantic_manifest.jsonl
```

`--assets` is optional and accepts the downloader's existing CSV or DOI/status/path
JSONL. Check your actual log filename. Queue/coding joins require exact normalized
DOI and original key. Mismatches are quarantined in the bridge receipt. Local file
existence/hashes are recorded without copying full text. Final-paper semantic steps
supply page/quote/action candidates only; review sequences are excluded, while
cited, inherited or declined moves remain flagged. Node O, a simulation mode, or a
data import never becomes actual modality/AI use. The original codebook's strict
schema is unchanged; this is a sidecar.

The optional semantic manifest is compatible with the existing `code_papers.py
--manifest` key filter for queue entries that already have a verified local PDF.
The bridge **does not run** that tool. Any later model upload/batch requires a
separate deliberate invocation under its existing permission, license and cost
rules. JATS/PDF availability likewise does not certify evidence or redistribution
rights.

## Report and plot reviewed results

```sh
python3 -m ai_readiness report \
  --input private/readiness/earth-2026-10-23/annotations_adjudicated.jsonl \
  --design private/readiness/earth-2026-10-23/design.json \
  --out private/readiness/earth-2026-10-23/report.json
python3 -m ai_readiness.plot_report private/readiness/earth-2026-10-23/report.json \
  --outprefix private/readiness/earth-2026-10-23/figures/readiness \
  --label 'Earth cohort: frozen journal frame' --conditionals
```

Omit `--design` for descriptive reviewed-subset counts only. Reports contain pooled
and annual metrics with their own known-label denominators, plus full-text coverage
and separate descriptive training-regime/author-explanation summaries. Conditional
FM-given-AI and FM-given-DL rates keep their distinct denominators.

For valid bound stratified random samples, reports use inverse inclusion weights
and Taylor ratio variance with finite-population correction. Annual estimates are
**domains of the original sample**: all original strata and draws remain in the
calculation, including draws outside the year. The code never invents year-specific
population counts from observed sample years. Missing sampled reviews, changed
IDs/years/weights, uncertain relevant labels or singleton non-census variance
strata suppress affected population estimates. Boundary estimates do not receive
zero-width confidence intervals. Normal intervals are exploratory for sparse
outcomes; exact/sensitivity work is still needed. No trend test or causal claim is
automatically generated. Frame omissions, changing source coverage, publication lag,
full-text nonresponse and annotation error are outside those sampling intervals.

Plots write SVG and PNG points with denominator labels. They do not connect missing
years or manufacture trends, draw intervals for descriptive subsets, or create a
figure when no reviewed data exist. A template-only report is not a result figure.

## Add a separate CS cohort

Copy and resolve `cohort_protocol.example.json` before acquisition. It deliberately
contains no guessed source IDs and no claim that an unfinished CS frame exists.
Use the existing selector for your verified CS journal/proceedings frame; import it
as a **separate run** with `--ontology cs_information_channels`, then use the same
review/report steps. Freeze common years, inclusion rules, article types and
annotation definitions, and audit full-text coverage. Proceedings/preprint duplicates
and OpenAlex series identities require particular care. Different field ontologies
must not be equated just because both yield a percentage called multimodality.

```sh
python3 -m ai_readiness compare \
  --earth private/readiness/earth-2026-10-23/report.json \
  --cs private/readiness/cs-2026-10-23/report.json \
  --protocol private/readiness/matched_protocol.json \
  --out private/readiness/comparison-2026-10-23.json
```

This keeps reports side by side. Its comparison-ready flag requires recorded
confirmation/evidence for matched years, article eligibility, annotation codebook,
full-text coverage and frozen source frames. It never pools fields or computes a
significance test. Separate, nonrepresentative pilots cannot establish a cross-field
adoption claim.

## Offline checks

```sh
PYTHONPATH=tools python3 -m unittest discover -s tools/ai_readiness/tests -v
```

Tests use synthetic fixtures, not fabricated study results. They cover DOI/key
joins, no automatic actual-use conversion, original assignment binding, annual
domain weights, unknown/inaccessible labels, training evidence, legacy design
rejection and plot safeguards. The existing acquisition tests remain separate and
are not replaced. No credentials, network requests or model jobs are needed.

## Optional endpoint changes

To quantify a first/last-year contrast, resolve `endpoint_protocol.example.json`
from the frozen frame and review-coverage audit, then add
`--endpoint-protocol private/readiness/endpoint_protocol.json` to `report`. Without
that protocol, endpoint changes are suppressed. Missing years, incomplete reviews,
changed frames, unresolved eligibility/codebook rules or unmatched full-text
coverage cannot support the contrast. The output reports percentage-point change
and last/first ratio only when both baselines are usable; a zero baseline yields
no finite ratio. It uses verified bound-design population estimates when both are
available; otherwise any permitted result is explicitly a descriptive accessible-
subset contrast. No difference CI, trend test, significance or causal claim is
computed from endpoint estimates or from overlapping/unpaired confidence intervals.
