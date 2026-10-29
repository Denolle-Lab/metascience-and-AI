"""Phase 3b: do outcomes depend on the iterations papers erase? Analysis plan for the layered workflow reconstruction,
frozen before any advance coding of a non-pilot Copernicus paper exists, then tested.

Direction from the PI (October 28, 2026): papers give the paper's account of the work, not its chronology, and they
leave out loops; part of what they leave out is recoverable from referee comments, author responses and the submitted
manuscript. g31_reconstruct.py builds the layered walk descriptively. This script fixes, before outcome data exist, how
the layers are joined to the blind advance outcome (agents/advance/RUBRIC.md, tools/roadmap/g24_advance.py) and to
citation impact (g04 metrics). The human-readable plan is preregistration/reconstruction.md; the machine-readable plan
is preregistration/reconstruction.json, written by `draft` (status draft) and by `freeze` (status frozen).

draft     Writes the plan json with status 'draft' (no freeze, no refusal check): hypotheses, definitions, the expected n
          from the data on disk and the power table below. Safe to rerun.
freeze    Refuses (1) when the plan json is already frozen; (2) when any advance coding exists for a Copernicus paper
          (DOI 10.5194) outside the advance pilot keys: a g22_* file in private/analysis/codings/api/*-advance/ or its
          _invalid/, or in derived/advance/rescued/, or a key of a '*-advance' batch in state.json (read only); (3)
          when an advance coding's key has no DOI in any metrics file, manifest or open-review index (cannot rule it
          out); (4) when a FROZEN or RECORDED file has uncommitted changes or is untracked (git status --porcelain), so
          the code the plan names has a public commit; (5) when METASCIENCE_PRIVATE is set and the plan path is the
          default (a plan frozen on another tree would be written into the public one); (6) when
          check_coding.DISCLOSURE_CHECKS is not DISCLOSURE_CHECKS. Then builds the whole plan (power included) in
          memory, and only then rewrites the Status line of the plan md and writes the plan json with status 'frozen',
          the sha256 of every FROZEN and RECORDED file and of the plan md, the code commit (HEAD), the freeze time, the
          private tree read (common.PRIVATE_ROOT), the cop22 order, the sha256 of every round-1 and round-2 inquiry
          coding of a candidate paper, and the counts at freeze. One MANIFEST row. The PI then commits the plan json,
          md and figure in one commit and pushes it before any non-pilot Copernicus advance coding is submitted.
features  Computes the per-paper features and the layer completeness of every set (no outcome read) and writes
          derived/reconstruction/features.json. Descriptive; any time.
audit-sample  Draws the absent-status audit sample (below) from the complete papers' kept disclosures and writes
          derived/reconstruction/absent_audit_sample.json and absent_audit_form.csv. No outcome read.
power     Prints the power table (synthetic data only; no data read). One MANIFEST row.
test      Runs the frozen plan: recomputes the features, reads the advance codings of each set's advance tag (valid
          under tools/check_advance.py, through g24 advance_codings(), no rescue) and the metrics, and writes
          derived/reconstruction/{results.json, RECONSTRUCTION_TEST.md}. Refuses when preregistration/advance-plan.json
          does not exist, and unless all of: the plan is the one of the last commit touching
          preregistration/reconstruction.json (git log -n1), byte for byte, with status frozen; that commit is on a
          remote branch (pushed); the plan's code commit is its ancestor; every FROZEN file equals its version in that
          commit (else --accept-deviation, which records the list); every advance attempt (state.json batch 'submitted'
          or 'spent' time) of a non-pilot paper entering C5 is later than the freeze commit time, minute resolution, the
          commit time read in the machine's local zone. --plan is refused unless METASCIENCE_PRIVATE is set (a
          synthetic tree): the git checks are then replaced by the plan's own freeze time and recorded as 'synthetic'.

Sets (overridable at freeze with --set NAME=INQUIRY_TAG,REVIEW_TAG,ADVANCE_TAG[,ROOT[,ADVANCE_ROOT]]; ADVANCE_TAG 'plan'
= the full_run_tag of preregistration/advance-plan.json; ROOT, the codings root of the inquiry and review tags, and
ADVANCE_ROOT, that of the advance tag: 'api' (Claude, private/analysis/codings/api; the default) or 'open' (an
open-weight rerun, private/analysis/codings/open, tools/code_papers_open.py and g33_handoff.py requests). An 'open'
root replaces the state.json checks by its run.json (model, review input hashes) and has no re-draw record)
  round1   calc1, calc1-review-v2, plan; index derived/review/open_review_index.json; metrics derived/gold/metrics.json.
           Drawn: round-1 preselection, equal cnp quintiles of 600 papers (g02, g03).
  round2   r2, r2-review-v2, plan; index derived/review/open_review_index_r2.json; metrics derived/r2/metrics.json.
           Drawn: round-2 preselection, open access only, at most 4 papers per journal (g18).
  cop22    cop22, cop22-review-v2, cop22-advance; index derived/review/open_review_index_cop22.json; metrics
           derived/cop22/metrics.json. Drawn: g32, equal quota per journal spread over impact quintiles. Copernicus keys
           of derived/cop22/draw_manifest.jsonl only (the Nature-family papers of that draw are outside this plan by
           design: their peer review files carry no AC or AR author units, which the review addendum codes). Entry order:
           COP22_ORDER = the Copernicus rows of derived/cop22/preselect.json in g32's draw_order (journals interleaved in
           proportion, so any prefix is an approximately equal-weight sub-draw), fixed in the plan at freeze; the test
           takes the longest prefix of that order in which every paper has an attempt under each of the set's inquiry,
           review and advance tags (state.json batch or 'spent' record, or a file in the tag folder or its _invalid;
           run.json for root 'open'), so a budget-limited subset is a prefix, never a choice.
  A key in two sets counts in the first.

Complete (all layers; a paper with any layer missing is not in the test population)
  C0 open discussion    the set index row has 'comments' and the DOI is 10.5194
  C1 reported           a valid blind inquiry coding (tools/check_coding.py validate(), codebook 1.5.0) under the inquiry
                        tag. round1, round2 (coded before this plan): the coding file is the one hashed at freeze. cop22:
                        answered by MODEL and valid within REDRAW_CAP content re-draws (state.json 'spent')
  C2 review-induced     a valid review coding under the review tag: validate(review=True, texts, checks DISCLOSURE_CHECKS),
                        review_addendum_version 1.0.0, a review sequence with at least one step triggered by a referee,
                        editor or commenter; answered by MODEL (state.json 'spent'), within REDRAW_CAP content re-draws,
                        from a request that recorded disclosure_checks DISCLOSURE_CHECKS (batch record, or the 'spent'
                        attempt of a synchronous run). Root 'open': the run.json status ok and its model recorded
  C3 disclosed          C2, and the sha256 of the discussion text and of the author-responses document that the request
                        recorded (state.json batch review_inputs[key], or the attempt's review_inputs; run.json for root
                        'open') equal the hashes of the texts on disk now (tools/code_papers.review_inputs, read only)
  C4 revised            g26 finds the discussion preprint and the published text, and at least LOCATED_MIN of the reported
                        steps are located in the published text (g31 status other than 'unlocated')
  C5 outcome            (test only) a valid advance coding under the advance tag whose verdict is not unassessable U4
  Excluded              PILOT_SEEN and every key of derived/advance/pilot_keys.json (advance codings seen in the pilots)

Disclosure quote checks: rule DISCLOSURE_CHECKS = 'item' (check_coding.kept_disclosures): a disclosure whose unit is not
an author unit, whose quote is in no author unit of the cited document, whose quote is referee text, or whose final quote
is not in the published paper is dropped and counted (disclosures_dropped); the coding stays valid. On the 58 E3 codings,
705 of 746 review-step quotes sit in the cited unit and 746 of 746 in the same document (October 28, 2026).

Features (per paper; from the kept disclosures of the set's review coding and g31_reconstruct.paper() on the set's
inquiry and review codings, with the real coding paths hashed and no E4 labels, so every input is a defined prompt,
schema and validator task)
  outside_only_loops   distinct loop events visible only outside the paper: kept disclosures of kind tried_dropped or
                       added_for_review with final_paper_status 'absent', or with removed true (the paper no longer
                       carries it); events() below
  events()             two items are one event when they share a document (g31 DISCLOSURE MATCH document rule: AC1, AR2)
                       and g31.qcov() >= g31.DMATCH, or when g31.qcov() >= SAME_EVENT_OTHER_DOC in different documents
                       (the same reply posted twice, or an AR page repeating an AC paragraph; g30 MATCH_OTHER_UNIT)
  tried_dropped        events() over kept tried_dropped disclosures (any final status)
  review_loops         g31 measure review_loops (review steps by referee, editor or commenter, move not declined)
  review_V_loops       review_loops whose node is V
  claim_narrowed       events() over kept claim_narrowed disclosures
  revision_share       g31 paper_steps_absent_in_preprint / paper_steps_located
  paper_returns, paper_revisits, paper_steps   g31 measures of the reported walk
  disclosures, disclosures_dropped             kept and dropped disclosures
  Decomposition features: oo_tried_dropped, oo_added_for_review (outside_only_loops of one kind only). Sensitivity
  features: outside_only_loops_flagged (items with loop true only); review_added_V_in_paper (added_for_review, node V,
  final present or partly); oo_e4_g27 (round 1 only: g31's default outside_only_loops with calc1-review, E4 labels and g27
  disclosures, as in derived/reconstruct/merged_walks.json); response_words (words of the AC paragraphs of
  discussion.txt plus the AR document)

Outcomes (advance coding, RUBRIC.md v1.1.0; g24 derived() and check_advance.basis_gain())
  achieved   verdict achieved 1, else 0 (unassessable U1-U3, U5 stay as 0; U4 excluded), as g24 'achieved'
  achieved_assessable   achieved on assessable papers only (S7)
  score      advance_score 1-5, papers with verdict achieved or not_demonstrated
  W3         criterion W3 of the verdict-basis gain (G1 when not_demonstrated) met or not_applicable 1, not_met 0;
             assessable papers
  W_count    number of W1-W4 of that gain met (W3 not_applicable counts as met), 0-4; assessable papers
  overreach  overreach.exceeds_warrant no 0, partly 1, yes 2; assessable papers
  cnp, fwci  the set's metrics.json (secondary family)

Test rule  For each hypothesis: partial Spearman within strata. Ranks of feature, outcome and covariates; feature and
           outcome ranks residualized on stratum indicators and covariate ranks (OLS); rho = correlation of the two
           residuals. Two-sided p: Freedman-Lane permutation, the outcome residual permuted within stratum and
           residualized again (NPERM); 95% interval: bootstrap of papers within stratum (NBOOT); generator g20.gen
           ('recon|<id>'). Strata: journal (DOI 10.5194/<abbr>-) x set, because the three sets were drawn by different
           designs; inside each set, journals with fewer than MIN_STRATUM papers in the hypothesis's population are
           pooled into one stratum of that set. Covariates: paper_steps, paper_returns, paper_revisits, less the feature
           itself. Testable when the outcome varies and at least MIN_N papers lie above the feature's minimum and at
           least MIN_N below its maximum; else p = 1, kept in the family.
           Benjamini-Hochberg over the primary family (H1-H8) and separately over the secondary family (S01-S14, sets in
           SECONDARY_EXCLUDE left out); supported when
           q < Q and the sign is the predicted one, reversed when q < Q and the sign is opposite, else not supported.
Reported beside the rule, not part of it: Mantel-Haenszel odds ratio of any outside-only loop against achieved within
strata (bootstrap interval); the H1 minus H8 contrast (paired bootstrap, one-sided test below); sensitivities S1-S7 and
decompositions D1-D2 (no verdicts); the g24 validation gate, the disclosure gate (g30) and the absent-audit gate.

Inputs   the sets' index, inquiry, review and advance folders; private/analysis/codings/api/state.json (read only);
         derived/review/visibility_labels.json and derived/translation/labels/ (S6); review/<key>/, pdfs/;
         derived/{gold,r2,cop22}/metrics.json; derived/cop22/preselect.json; derived/advance/pilot_keys.json;
         preregistration/advance-plan.json (test); derived/translation/disclosure_agreement_r2_oo.json (g30) and
         derived/reconstruction/absent_audit.json (human audit) for the gates
Outputs  preregistration/reconstruction.json (draft, freeze; public); derived/reconstruction/features.json (features);
         derived/reconstruction/absent_audit_sample.json, absent_audit_form.csv (audit-sample);
         derived/reconstruction/results.json, RECONSTRUCTION_TEST.md (test); one MANIFEST row per run
Run:     python tools/roadmap/g34_reconstruction.py draft
         python tools/roadmap/g34_reconstruction.py freeze      (PI, after committing every FROZEN and RECORDED file,
                                                                 before any non-pilot Copernicus advance coding; then
                                                                 commit the plan json, md and png together and push)
         python tools/roadmap/g34_reconstruction.py features
         python tools/roadmap/g34_reconstruction.py audit-sample (after the review-v2 codings exist)
         python tools/roadmap/g34_reconstruction.py test        (after the review-v2 and advance codings exist)
         --plan PATH puts the plan elsewhere (dry runs; test only with METASCIENCE_PRIVATE); METASCIENCE_PRIVATE points
         every read and write at another tree.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from common import ROOT, PRIVATE, PRIVATE_ROOT, DATA, DERIVED, TODAY, commit, log, read_json, rel, write_json
import check_coding
from check_coding import validate, kept_disclosures
import rounds
import g17_outcomes as g17
import g20_topics_journals as g20
import g31_reconstruct as g31

CODINGS = PRIVATE / 'analysis' / 'codings'
API = CODINGS / 'api'
STATE = API / 'state.json'
PLAN = ROOT / 'preregistration' / 'reconstruction.json'
PLAN_REL = 'preregistration/reconstruction.json'
ADV_PLAN = ROOT / 'preregistration' / 'advance-plan.json'
OUT = DERIVED / 'reconstruction'
PILOT_SEEN = g31.PILOT_SEEN                   # g22_W4205292752, g22_W4223595027: Copernicus papers coded in the pilots
PILOT_KEYS = DERIVED / 'advance' / 'pilot_keys.json'
MODEL = 'claude-opus-5-5'                     # the coder every Claude layer must come from (state.json 'spent' model)
Q, SEED, NPERM, NBOOT, MIN_N, MIN_STRATUM = 0.1, 2034, 5000, 2000, 10, 5
LOCATED_MIN = 0.8
SAME_EVENT_OTHER_DOC = 0.8
DISCLOSURE_CHECKS = 'item'                    # check_coding.DISCLOSURE_CHECKS must agree (freeze refuses otherwise)
REDRAW_CAP = 1                                # content re-draws allowed per paper and tag coded under this plan
CONTRAST_ALPHA = 0.05                         # one-sided bootstrap test of H1 minus H8 > 0
AUDIT_N, AUDIT_MIN_CONFIRMED = 50, 0.8        # absent-status audit: items drawn, share confirmed absent to pass
OO_KINDS = ('tried_dropped', 'added_for_review')
SETS = [
    {'name': 'round1', 'inquiry_tag': 'calc1', 'review_tag': 'calc1-review-v2', 'advance_tag': 'plan', 'root': 'api',
     'index': 'derived/review/open_review_index.json', 'metrics': 'gold', 'inquiry_fixed_at_freeze': True,
     'design': 'round-1 preselection: equal cnp quintiles of 600 papers (g02, g03)'},
    {'name': 'round2', 'inquiry_tag': 'r2', 'review_tag': 'r2-review-v2', 'advance_tag': 'plan', 'root': 'api',
     'index': 'derived/review/open_review_index_r2.json', 'metrics': 'r2', 'inquiry_fixed_at_freeze': True,
     'design': 'round-2 preselection: open access only, at most 4 papers per journal (g18)'},
    {'name': 'cop22', 'inquiry_tag': 'cop22', 'review_tag': 'cop22-review-v2', 'advance_tag': 'cop22-advance', 'root': 'api',
     'index': 'derived/review/open_review_index_cop22.json', 'metrics': 'cop22', 'inquiry_fixed_at_freeze': False,
     'design': 'g32 draw: equal quota per journal, spread over impact quintiles'},
]
COP22_MANIFEST = DERIVED / 'cop22' / 'draw_manifest.jsonl'
COP22_PRESELECT = DERIVED / 'cop22' / 'preselect.json'
COVARIATES = ['paper_steps', 'paper_returns', 'paper_revisits']
POPULATION = ('2022 Copernicus papers with an open discussion (referee and author comments on the discussion page and a '
              'discussion preprint), drawn in round 1 by equal cnp quintiles of the corpus preselection, in round 2 from '
              'the open-access preselection (at most 4 per journal) and in cop22 by an equal quota per journal spread over '
              'impact quintiles; the advance pilot papers excluded')
HYPOTHESES = [
    {'id': 'H1', 'primary': True, 'feature': 'outside_only_loops', 'outcome': 'achieved', 'sign': 1,
     'theory': 'selection under test: a claim that survived alternatives tried and dropped, and tests run only for review, '
               'is more often warranted as reported; rival (requests follow weak papers) predicts a negative sign'},
    {'id': 'H2', 'primary': True, 'feature': 'outside_only_loops', 'outcome': 'score', 'sign': 1,
     'theory': 'as H1, on the size of the warranted gain'},
    {'id': 'H3', 'feature': 'tried_dropped', 'outcome': 'achieved', 'sign': 1,
     'theory': 'alternatives tried before the reported route (any final status): the reported route is the survivor'},
    {'id': 'H4', 'feature': 'review_V_loops', 'outcome': 'W3', 'sign': 1,
     'theory': 'referees ask for checks of the principal threat; the checks added enter the paper the blind coder reads'},
    {'id': 'H5', 'feature': 'review_loops', 'outcome': 'W_count', 'sign': 1,
     'theory': 'work reopened at review adds warrant to the published text (uncertainty, checks, consistency)'},
    {'id': 'H6', 'feature': 'claim_narrowed', 'outcome': 'overreach', 'sign': -1,
     'theory': 'a claim narrowed at review fits its warrant in the published text; rival (narrowing is asked of '
               'overreaching papers and stays partial) predicts a positive sign'},
    {'id': 'H7', 'feature': 'revision_share', 'outcome': 'achieved', 'sign': 1,
     'theory': 'steps written after submission are mostly answers to review and add warrant the coder can see'},
    {'id': 'H8', 'feature': 'paper_returns', 'outcome': 'achieved', 'sign': 1,
     'theory': 'loops the paper reports are selected for the argument; the claim that H8 is weaker than H1 is tested '
               'separately (one-sided bootstrap of H1 minus H8, CONTRAST_ALPHA)'},
]
REPLICATION_NOTE = ('replication of a known round-1 null: paper_returns ("returns after failure") against cnp and fwci on '
                    'the 374 round-1 papers, rho 0.042 and 0.045, q 0.717 and 0.707 (g17, derived/outcomes/outcomes.json, '
                    'October 27, 2026)')
SECONDARY = [{'id': f'S{i:02d}', 'feature': f, 'outcome': o, 'sign': s, **({'note': REPLICATION_NOTE} if f == 'paper_returns' else {})}
             for i, (f, o, s) in enumerate([(f, o, s) for f, s in (('outside_only_loops', 1), ('tried_dropped', 1),
                                                                   ('review_loops', 1), ('review_V_loops', 1),
                                                                   ('claim_narrowed', -1), ('revision_share', 1),
                                                                   ('paper_returns', 1)) for o in ('cnp', 'fwci')], 1)]
# Sets left out of the secondary family: round-1 review-layer features were correlated with real round-1 cnp and fwci in
# the g34 dry run of October 28, 2026 (synthetic advance outcomes; features from E3 codings and g27 labels), before the
# freeze. Declared at once, whatever the values; the primary family is unaffected (its outcomes were synthetic).
SECONDARY_EXCLUDE = {'round1': 'round-1 features against real cnp and fwci were computed in the dry run of October 28, 2026'}
SENSITIVITY = {
    'S1_plain': 'within-stratum Spearman without covariates',
    'S2_more_covariates': 'covariates plus log paper words (blinded text meta), log response words, log author count and '
                          'log reference count (set metrics n_authors, n_refs) and disclosures_dropped',
    'S3_strata_journal': 'strata journal only (pooled across sets) instead of journal x set',
    'S4_flagged': 'H1, H2 with outside_only_loops_flagged (items with loop true only)',
    'S5_visible_V': 'H4 with review_added_V_in_paper (added_for_review, node V, final present or partly)',
    'S6_e4': 'H1, H2 on round 1 with oo_e4_g27 (g31 default inputs: E4 visibility labels and g27 disclosures, agent labels; '
             'includes the g31 E4 no_change rule added after a look at the data)',
    'S7_assessable': 'H1, H3, H7, H8 with achieved_assessable (unassessable U1-U3, U5 left out instead of counted as 0)',
}
DECOMPOSITION = {
    'D1_tried_dropped': 'H1, H2 with oo_tried_dropped: tried and dropped, absent from the paper (selection among routes)',
    'D2_added_for_review': 'H1, H2 with oo_added_for_review: analyses added for review and kept out of the paper; they '
                           'cannot add warrant the blind coder sees, so an association here is selection or confounding '
                           '(for example how conscientious the team is), not added warrant',
}
FROZEN = ['tools/roadmap/g34_reconstruction.py', 'tools/roadmap/g31_reconstruct.py', 'tools/roadmap/g26_translation.py',
          'tools/check_coding.py', 'agents/coder/REVIEW_ADDENDUM.md', 'agents/coder/review_addendum.schema.json',
          'agents/coder/CODEBOOK.md', 'agents/coder/coding.schema.json']
RECORDED = ['tools/code_papers.py', 'tools/code_papers_open.py', 'tools/check_advance.py',
            'agents/advance/RUBRIC.md', 'agents/advance/advance.schema.json', 'tools/roadmap/g24_advance.py',
            'tools/roadmap/g17_outcomes.py', 'tools/roadmap/g20_topics_journals.py', 'tools/roadmap/g27_author_responses.py',
            'tools/roadmap/g30_disclosure_agreement.py', 'tools/roadmap/g33_handoff.py', 'tools/roadmap/rounds.py',
            'tools/roadmap/common.py']
# Expected-n rates, each with its measured source (used by draft and freeze; the test does not use them)
RATES = {'review_valid': (58, 61, 'E3: valid calc1-review codings of the 61 round-1 open-review papers; under the item '
                                  'rule a failed quote check drops the item, not the coding'),
         'revised_layer': (61, 61, 'g31: discussion preprint and published text for 61 of 61, 1,447 of 1,449 steps located'),
         'advance_valid': (39, 40, 'advance pilot 2 (rubric 1.1.0, tags pilot2-a-advance and pilot2-b-advance): valid '
                                   'without rescue, read as load_advance reads them (g24 advance_codings, rescue off), '
                                   'October 28'),
         'inquiry_valid': (102, 104, 'valid calc1 and r2 codings of the 104 round-1 and round-2 Copernicus papers'),
         'eligible': (104, 106, 'g32: Copernicus papers of rounds 1 and 2 passing the eligibility screen'),
         'open_discussion': (61, 64, 'round 1: open discussion on the Copernicus page (used for round 2 only while '
                                     'open_review_index_r2.json is missing)')}
ITEM_RETENTION = (746, 746, 'E3 review-step quotes found in the cited document (705 of 746 in the cited unit), '
                            'October 28; proxy for disclosure quotes')


def sha(p: Path) -> str | None:
    p = Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def bare(doi: str | None) -> str:
    return re.sub(r'^https?://(dx\.)?doi\.org/', '', (doi or '').strip().lower())


def is_cop(doi: str | None) -> bool:
    return bare(doi).startswith('10.5194/')


def plan_path(args) -> Path:
    return Path(args.plan).resolve() if getattr(args, 'plan', None) else PLAN


def pilot_keys() -> set:
    return set(PILOT_SEEN) | (set(read_json(PILOT_KEYS)['keys']) if PILOT_KEYS.is_file() else set())


def git(*a) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', str(ROOT), *a], capture_output=True)


_STATE = None


def state() -> dict:
    """state.json of the Claude runs, read once (read only)."""
    global _STATE
    if _STATE is None:
        _STATE = json.loads(STATE.read_text()) if STATE.is_file() else {'batches': [], 'done': {}, 'spent': {}}
        _STATE.setdefault('spent', {})
    return _STATE


def folder(S: dict, kind: str) -> Path:
    root = S.get('advance_root', 'api') if kind == 'advance' else S.get('root', 'api')
    return CODINGS / root / S[f'{kind}_tag']


_CP = None


def cp():
    """tools/code_papers.py with REVIEW_DIR on the review records (texts and hashes only; no API call)."""
    global _CP
    if _CP is None:
        import functools
        import code_papers
        code_papers.REVIEW_DIR = str(DATA / 'review')
        # one author-responses build per paper and run (it runs pdftotext when the cache is missing or stale)
        code_papers.author_responses_for = functools.lru_cache(maxsize=None)(code_papers.author_responses_for)
        _CP = code_papers
    return _CP


# ------------------------------------------------------------------------------------------------ keys and layers
def doi_map() -> dict:
    out = {}
    for s in ('gold', 'r2', 'cop22'):
        f = DERIVED / s / 'metrics.json'
        for m in (read_json(f) if f.is_file() else []):
            out['g22_' + m['id']] = bare(m.get('doi'))
    for f in [COP22_MANIFEST] + [DERIVED / d / 'manifest.jsonl' for d in ('calc1', 'r2calc', 'cop22calc')]:
        for l in (f.read_text().splitlines() if f.is_file() else []):
            if l.strip():
                r = json.loads(l)
                out.setdefault(r['key'], bare(r.get('doi')))
    for f in sorted((DERIVED / 'review').glob('open_review_index*.json')):
        for r in read_json(f):
            out.setdefault(r['key'], bare(r.get('doi')))
    return out


def advance_records() -> list[tuple[str, str]]:
    """(key, where) for every advance coding on disk or advance batch request in state.json (read only)."""
    out = []
    for d in sorted(API.glob('*-advance')) + sorted((DERIVED / 'advance' / 'rescued').glob('*')):
        for f in sorted(d.glob('g22_*')) + sorted((d / '_invalid').glob('g22_*')):
            out.append((f.stem, rel(f)))
    if STATE.is_file():
        for b in json.loads(STATE.read_text()).get('batches', []):
            if str(b.get('tag', '')).endswith('-advance'):
                out += [(k, f"state.json batch {b.get('id')} ({b['tag']})") for k in b.get('keys', [])]
    return out


def violations() -> tuple[list, list]:
    dois, pk = doi_map(), pilot_keys()
    bad, unknown = [], []
    for k, where in advance_records():
        if k in pk:
            continue
        if k not in dois:
            unknown.append(f'{k} ({where})')
        elif is_cop(dois[k]):
            bad.append(f'{k} ({where})')
    return sorted(set(bad)), sorted(set(unknown))


def cop22_order() -> list[str]:
    """The Copernicus keys of the cop22 draw in g32's draw_order (derived/cop22/preselect.json), manifest keys only."""
    man = {json.loads(l)['key'] for l in COP22_MANIFEST.read_text().splitlines() if l.strip()} if COP22_MANIFEST.is_file() else set()
    rows = read_json(COP22_PRESELECT) if COP22_PRESELECT.is_file() else []
    return [f"g22_{r['id']}" for r in sorted(rows, key=lambda r: r['draw_order'])
            if is_cop(r.get('doi')) and f"g22_{r['id']}" in man]


def open_run(S: dict, kind: str) -> dict:
    f = folder(S, kind) / 'run.json'
    return json.loads(f.read_text()) if f.is_file() else {'papers': {}}


def root_of(S: dict, kind: str) -> str:
    return S.get('advance_root', 'api') if kind == 'advance' else S.get('root', 'api')


def attempted(S: dict, kind: str, key: str) -> bool:
    """An attempt of the paper under the set's tag: a file in the folder or its _invalid, a state.json batch or 'spent'
    record (root api), a run.json record (root open)."""
    d = folder(S, kind)
    if (d / f'{key}.json').is_file() or any((d / '_invalid').glob(f'{key}.*')):
        return True
    if root_of(S, kind) == 'open':
        return key in open_run(S, kind).get('papers', {})
    tag, st = S[f'{kind}_tag'], state()
    return f'{tag}:{key}' in st['spent'] or any(b['tag'] == tag and key in b['keys'] for b in st['batches'])


def provenance(S: dict, kind: str, key: str) -> dict:
    """How the paper's coding under the set's tag was produced: answering model, content re-draws before it, the
    quote-check rule and review inputs its request recorded."""
    tag = S[f'{kind}_tag']
    if S.get('root', 'api') == 'open':
        run = open_run(S, kind)
        p = run.get('papers', {}).get(key, {})
        return {'model': run.get('model'), 'redraws': None, 'disclosure_checks': DISCLOSURE_CHECKS if p else None,
                'review_inputs': {'discussion': p.get('review_sha256'), 'responses': p.get('responses_sha256')} if p else None,
                'root': 'open'}
    st = state()
    spent = st['spent'].get(f'{tag}:{key}', [])
    content = lambda x: x['outcome'].startswith('invalid_json') or 'validation problems' in x['outcome']
    ok = next((i for i, x in enumerate(spent) if x['outcome'].startswith('ok')), None)
    att = spent[ok] if ok is not None else None
    done = st['done'].get(f'{tag}:{key}') or {}
    b = next((b for b in st['batches'] if b['id'] == (att or {}).get('batch', done.get('batch'))), None) if (att or done) else None
    src = b if b is not None else (att or {})
    return {'model': (att or {}).get('model'), 'redraws': sum(content(x) for x in spent[:ok]) if ok is not None else None,
            'attempts': len(spent), 'batch': (b or {}).get('id'), 'disclosure_checks': src.get('disclosure_checks'),
            'review_inputs': (src.get('review_inputs') or {}).get(key) if b is not None else src.get('review_inputs'),
            'root': 'api'}


def valid_inquiry(S: dict) -> dict:
    out = {}
    d = folder(S, 'inquiry')
    for f in sorted(d.glob('g22_*.json')) if d.is_dir() else []:
        try:
            c = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            continue
        if not validate(c):
            out[c['key']] = c
    return out


def valid_review(S: dict, keys) -> dict:
    """{key: (coding, kept disclosures, dropped count)} for review codings valid under the review addendum, the quote
    checks run against the texts (DISCLOSURE_CHECKS)."""
    out = {}
    d = folder(S, 'review')
    for k in keys:
        f = d / f'{k}.json'
        if not f.is_file():
            continue
        try:
            c = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            continue
        if c.get('review_addendum_version') != '1.0.0':
            continue
        texts = cp().review_texts(k, store=False)
        if validate(c, review=True, texts=texts, checks=DISCLOSURE_CHECKS):
            continue
        kept, dropped = kept_disclosures(c, texts) if DISCLOSURE_CHECKS == 'item' else (c.get('disclosures') or [], 0)
        out[k] = (c, kept, dropped)
    return out


def response_words(key: str) -> int:
    d = DATA / 'review' / key / 'discussion.txt'
    ac = sum(len(m.group(2).split()) for l in (d.read_text().splitlines() if d.is_file() else [])
             if (m := re.match(r'\[(AC\d+(?:-S)? (?:¶|p\.)\d+)\] (.*)', l)))
    ar = cp().author_responses_for(key, store=False)
    return ac + (len(ar.split()) if ar else 0)


def events(items: list[dict]) -> int:
    """Distinct events among disclosure items (union-find over the same-event rule)."""
    par = list(range(len(items)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    doc = lambda d: d['unit'].split(' ')[0].split('-')[0]
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            v = g31.qcov(items[i].get('quote'), items[j].get('quote'))
            if v >= (g31.DMATCH if doc(items[i]) == doc(items[j]) else SAME_EVENT_OTHER_DOC):
                par[find(i)] = find(j)
    return len({find(i) for i in range(len(items))})


def as_items(kept: list[dict]) -> list[dict]:
    """Kept disclosures in g31's item form (final = final_paper_status, node None for 'none')."""
    return [{**d, 'final': d.get('final_paper_status'), 'final_quote': d.get('final_quote') or None,
             'node': None if d.get('node') in (None, '', 'none') else d['node']} for d in kept]


def outside_only(d: dict) -> bool:
    return d.get('kind') in OO_KINDS and (d.get('final') == 'absent' or d.get('removed') is True)


def features_of(rec: dict, items: list[dict], dropped: int) -> dict:
    m = rec['measures']
    loops = [s for s in rec['walk'] if s['layer'] == 'review_induced' and s['loop']]
    oo = [d for d in items if outside_only(d)]
    kind = lambda k: [d for d in items if d.get('kind') == k]
    return {'outside_only_loops': events(oo), 'outside_only_loops_flagged': events([d for d in oo if d.get('loop') is True]),
            'oo_tried_dropped': events([d for d in oo if d['kind'] == 'tried_dropped']),
            'oo_added_for_review': events([d for d in oo if d['kind'] == 'added_for_review']),
            'any_outside_only': int(bool(oo)), 'tried_dropped': events(kind('tried_dropped')), 'review_loops': m['review_loops'],
            'review_V_loops': sum(s['node'] == 'V' for s in loops),
            'claim_narrowed': events(kind('claim_narrowed')),
            'revision_share': round(m['paper_steps_absent_in_preprint'] / m['paper_steps_located'], 4) if m['paper_steps_located'] else None,
            'paper_returns': m['paper_returns'], 'paper_revisits': m['paper_revisits'], 'paper_steps': m['paper_steps'],
            'review_added_V_in_paper': sum(d.get('kind') == 'added_for_review' and d.get('node') == 'V' and d.get('final') in ('present', 'partly') for d in items),
            'disclosures': len(items), 'disclosures_dropped': dropped}


def prefix_len(S: dict, order: list[str], kinds: tuple) -> dict:
    """Longest prefix of order in which every paper has an attempt under each tag kind; per kind and the minimum."""
    per = {k: next((i for i, x in enumerate(order) if not attempted(S, k, x)), len(order)) for k in kinds}
    return {'per_tag': {S[f'{k}_tag']: v for k, v in per.items()}, 'prefix': min(per.values()) if per else len(order)}


def collect(sets: list[dict], order: list[str] | None, e4: bool = True, prefix_kinds=('inquiry', 'review'),
            inquiry_sha: dict | None = None) -> dict:
    """{key: record} for every candidate paper of every set: layers C0-C4, features when C1 and C2 hold.
    inquiry_sha: {key: sha256} of the round-1 and round-2 inquiry codings at freeze (test); C1 of a set with
    inquiry_fixed_at_freeze then requires the same file."""
    vis = {}
    if e4 and g31.VIS.is_file():
        raw = json.loads(g31.VIS.read_text())
        vis = {p['key']: {s['i']: s for s in p['steps']} for p in raw.get('data', raw)}
    out, notes = {}, {}
    pk = pilot_keys()
    for S in sets:
        idxf = DATA / S['index']
        if not idxf.is_file():
            notes[S['name']] = f'no index {rel(idxf)}'
            continue
        idx = {r['key']: r for r in read_json(idxf)}
        cand = [k for k in idx if is_cop(idx[k].get('doi'))]
        if S['name'] == 'cop22' and order is not None:
            pre = prefix_len(S, order, prefix_kinds)
            cand = [k for k in order[:pre['prefix']] if k in idx]
            notes['cop22_prefix'] = pre
            notes['cop22_prefix_without_index_row'] = sorted(k for k in order[:pre['prefix']] if k not in idx)
        cand = [k for k in cand if k not in out]
        inq, rev = valid_inquiry(S), valid_review(S, cand)
        capped_inquiry = not S.get('inquiry_fixed_at_freeze')
        old = rounds.valid('calc1-review') if S['name'] == 'round1' and e4 else {}
        for k in cand:
            r = idx[k]
            pr_i, pr_r = provenance(S, 'inquiry', k), provenance(S, 'review', k)
            c1 = k in inq and inq[k].get('codebook_version') == '1.5.0'
            why1 = []
            if c1 and S.get('inquiry_fixed_at_freeze') and S.get('root', 'api') == 'api' and inquiry_sha is not None and inquiry_sha.get(k) != sha(folder(S, 'inquiry') / f'{k}.json'):
                why1.append('inquiry coding not the one hashed at freeze')
            if c1 and capped_inquiry and S.get('root', 'api') == 'api':
                if pr_i['model'] != MODEL:
                    why1.append(f"inquiry answered by {pr_i['model']}")
                if (pr_i['redraws'] or 0) > REDRAW_CAP:
                    why1.append(f"inquiry re-drawn {pr_i['redraws']} times")
            c2 = k in rev and any(s.get('trigger') in g31.REVIEWERS for x in rev[k][0]['sequences']
                                  if x['kind'] == 'review' for s in x['steps'])
            why2 = []
            if c2 and S.get('root', 'api') == 'api':
                if pr_r['model'] != MODEL:
                    why2.append(f"review answered by {pr_r['model']}")
                if (pr_r['redraws'] or 0) > REDRAW_CAP:
                    why2.append(f"review re-drawn {pr_r['redraws']} times")
                if pr_r['disclosure_checks'] != DISCLOSURE_CHECKS:
                    why2.append(f"review request recorded disclosure_checks {pr_r['disclosure_checks']}")
            rec = {'key': k, 'set': S['name'], 'journal': g31.journal(bare(r['doi'])), 'doi': bare(r['doi']),
                   'excluded_pilot': k in pk,
                   'layers': {'C0_open_discussion': 'comments' in r, 'C1_reported': c1 and not why1, 'C2_review': c2 and not why2},
                   'provenance': {'inquiry': pr_i, 'review': pr_r}, 'not_complete_because': why1 + why2}
            now = cp().review_inputs(k, store=False) if rec['layers']['C2_review'] else None
            rec['layers']['C3_disclosed'] = bool(rec['layers']['C2_review'] and pr_r['review_inputs'] and now == pr_r['review_inputs'])
            if rec['layers']['C2_review'] and not rec['layers']['C3_disclosed']:
                rec['not_complete_because'].append('review inputs recorded at the request differ from the texts on disk')
            if rec['layers']['C0_open_discussion'] and rec['layers']['C1_reported'] and rec['layers']['C2_review']:
                c, kept, dropped = rev[k]
                paths = {'inquiry': folder(S, 'inquiry') / f'{k}.json', 'review': folder(S, 'review') / f'{k}.json'}
                w = g31.paper(r, inq[k], c, {}, S['review_tag'], paths=paths, droot=CODINGS / S.get('root', 'api'))
                rec['features'] = features_of(w, as_items(kept), dropped)
                rec['features']['response_words'] = response_words(k)
                m = w['measures']
                rec['layers']['C4_revised'] = bool(w['layers']['revised_after_submission'] and m['paper_steps']
                                                   and m['paper_steps_located'] / m['paper_steps'] >= LOCATED_MIN)
                rec['inputs_sha256'] = {**w['inputs_sha256'], 'review_inputs': now}
                if k in old:
                    rec['features']['oo_e4_g27'] = g31.paper(r, inq[k], old[k], vis, None)['measures'].get('outside_only_loops')
            else:
                rec['layers']['C4_revised'] = False
            rec['complete_C0_C4'] = all(rec['layers'].values()) and not rec['excluded_pilot']
            out[k] = rec
    return {'papers': out, 'notes': notes}


def inquiry_hashes(sets: list[dict]) -> dict:
    """sha256 of every inquiry coding of a Copernicus candidate of the sets coded before this plan (frozen in the plan)."""
    out = {}
    for S in sets:
        if not S.get('inquiry_fixed_at_freeze'):
            continue
        idxf = DATA / S['index']
        keys = [r['key'] for r in read_json(idxf) if is_cop(r.get('doi'))] if idxf.is_file() else []
        if S['name'] == 'round2':
            keys += [x['key'] for x in rounds.manifest('r2calc') if is_cop(x.get('doi'))]
        for k in sorted(set(keys)):
            h = sha(folder(S, 'inquiry') / f'{k}.json')
            if h:
                out.setdefault(k, h)
    return out


# ------------------------------------------------------------------------------------------------ statistics
def strata_of(labels: list[str]) -> list[str]:
    """Strata from 'set|journal' labels (or plain journals): a label with fewer than MIN_STRATUM papers is pooled into
    one stratum of its set ('set|pooled'; g20.POOLED for plain journals)."""
    c = Counter(labels)
    pool = lambda x: f"{x.split('|')[0]}|{g20.POOLED}" if '|' in x else g20.POOLED
    return [x if c[x] >= MIN_STRATUM else pool(x) for x in labels]


def _resid(v: np.ndarray, Z: np.ndarray) -> np.ndarray:
    return v - Z @ np.linalg.lstsq(Z, v, rcond=None)[0]


def _design(s: np.ndarray, covs: list) -> np.ndarray:
    D = (s[:, None] == np.unique(s)[None, :]).astype(float)
    return np.column_stack([D] + [g17.rank(c) for c in covs]) if covs else D


def partial_within(f, o, covs, strata, name, nperm=NPERM, nboot=NBOOT, rng=None, keep_boot=False) -> dict | None:
    """Partial Spearman within strata: estimate, Freedman-Lane permutation p (two-sided), bootstrap interval."""
    rng = rng or g20.gen(name)
    f, o = np.asarray(f, float), np.asarray(o, float)
    covs = [np.asarray(c, float) for c in covs]
    _, s = np.unique(strata, return_inverse=True)
    Z = _design(s, covs)
    ef, eo = _resid(g17.rank(f), Z), _resid(g17.rank(o), Z)
    d = np.sqrt((ef @ ef) * (eo @ eo))
    if d <= 1e-12:
        return None
    rho = float(ef @ eo / d)
    M = np.eye(len(f)) - Z @ np.linalg.pinv(Z)
    idx = np.tile(np.arange(len(f)), (nperm, 1))
    for g in np.unique(s):
        gi = np.flatnonzero(s == g)
        idx[:, gi] = rng.permuted(np.tile(gi, (nperm, 1)), axis=1)
    E = eo[idx] @ M
    st = np.abs(E @ ef) / (np.linalg.norm(E, axis=1) * np.sqrt(ef @ ef) + 1e-300)
    p = (1 + (st >= abs(rho) - 1e-12).sum()) / (nperm + 1)
    groups = [np.flatnonzero(s == g) for g in np.unique(s)]
    bs = []
    for _ in range(nboot):
        i = np.concatenate([gi[rng.integers(0, len(gi), len(gi))] for gi in groups])
        Zb = _design(s[i], [c[i] for c in covs])
        a, b = _resid(g17.rank(f[i]), Zb), _resid(g17.rank(o[i]), Zb)
        db = np.sqrt((a @ a) * (b @ b))
        if db > 1e-12:
            bs.append(a @ b / db)
    return {'rho_partial': round(rho, 3), 'ci': g20.ci(bs), 'p': round(float(p), 4), 'n': int(len(f)),
            'strata': len(groups), 'covariates': len(covs)}


def mantel_haenszel(x, y, strata, name, nboot=NBOOT) -> dict:
    x, y = np.asarray(x, int), np.asarray(y, int)
    _, s = np.unique(strata, return_inverse=True)

    def mh(i):
        num = den = 0.0
        for g in np.unique(s[i]):
            j = i[s[i] == g]
            a, b = ((x[j] == 1) & (y[j] == 1)).sum(), ((x[j] == 1) & (y[j] == 0)).sum()
            c, d = ((x[j] == 0) & (y[j] == 1)).sum(), ((x[j] == 0) & (y[j] == 0)).sum()
            num, den = num + a * d / len(j), den + b * c / len(j)
        return num / den if den > 0 else np.nan
    rng = g20.gen(name)
    groups = [np.flatnonzero(s == g) for g in np.unique(s)]
    bs = [mh(np.concatenate([gi[rng.integers(0, len(gi), len(gi))] for gi in groups])) for _ in range(nboot)]
    est = mh(np.arange(len(x)))
    return {'or_mh': None if np.isnan(est) else round(float(est), 3), 'ci': g20.ci([b for b in bs if np.isfinite(b)]),
            'n': int(len(x)), 'exposed': int(x.sum())}


def testable(f, o) -> bool:
    """The outcome varies, and at least MIN_N papers lie above the feature's minimum and MIN_N below its maximum."""
    f = np.asarray(f, float)
    return len(set(o)) > 1 and len(f) > 0 and (f > f.min()).sum() >= MIN_N and (f < f.max()).sum() >= MIN_N


# ------------------------------------------------------------------------------------------------ expected n and power
def expected_n() -> dict:
    r = {k: v[0] / v[1] for k, v in RATES.items()}
    pk, out = pilot_keys(), {}
    i1 = DATA / SETS[0]['index']
    r1 = [x for x in read_json(i1) if 'comments' in x and x['key'] not in pk] if i1.is_file() else []
    out['round1'] = {'candidates': len(r1), 'rule': 'open discussion x review valid x revised layer x advance valid',
                     'expected': round(len(r1) * r['review_valid'] * r['revised_layer'] * r['advance_valid'], 1)}
    m2 = [x for x in rounds.manifest('r2calc') if is_cop(x.get('doi')) and x['key'] not in pk]
    v2 = rounds.valid('r2')
    i2 = DATA / SETS[1]['index']
    rows2 = {x['key']: x for x in read_json(i2)} if i2.is_file() else {}
    n2 = [x['key'] for x in m2 if x['key'] in v2]
    if rows2:   # the round-2 index on disk: open discussion counted on the papers with a valid inquiry coding
        od_n = sum('comments' in rows2.get(k, {}) for k in n2)
        od, od_src = od_n / max(1, len(n2)), f'open_review_index_r2.json: {od_n} of {len(n2)} with a valid r2 coding'
    else:
        od, od_src = r['open_discussion'], 'borrowed from round 1 (no round-2 index on disk)'
    out['round2'] = {'candidates': len(m2), 'valid_inquiry': len(n2), 'open_discussion_rate': round(od, 3),
                     'open_discussion_source': od_src,
                     'rule': 'valid inquiry x open discussion x review valid x revised layer x advance valid',
                     'expected': round(len(n2) * od * r['review_valid'] * r['revised_layer'] * r['advance_valid'], 1)}
    n3 = len(cop22_order())
    per = r['eligible'] * r['inquiry_valid'] * r['review_valid'] * r['revised_layer'] * r['advance_valid']
    out['cop22'] = {'candidates': n3, 'rule': 'eligible x inquiry valid x open discussion (1.0: drawn on Crossref has-review) '
                    'x review valid x revised layer x advance valid', 'per_paper': round(per, 3),
                    'expected_full': round(n3 * per, 1), 'expected_prefix_80': round(80 * per, 1)}
    base = out['round1']['expected'] + out['round2']['expected']
    out['scenarios'] = {'rounds_1_2': round(base), 'rounds_1_2_cop22_prefix_80': round(base + 80 * per),
                        'rounds_1_2_cop22_full': round(base + n3 * per)}
    out['rates'] = {k: {'value': round(v[0] / v[1], 3), 'k': v[0], 'n': v[1], 'source': v[2]} for k, v in RATES.items()}
    out['item_retention'] = {'value': round(ITEM_RETENTION[0] / ITEM_RETENTION[1], 3), 'k': ITEM_RETENTION[0],
                             'n': ITEM_RETENTION[1], 'source': ITEM_RETENTION[2],
                             'note': 'under the item rule a failed quote check drops the disclosure, not the paper, so it '
                                     'does not enter the expected n; dropped items are a covariate in S2'}
    return out


def journal_mix() -> dict:
    """Expected papers per journal (Copernicus abbreviation) for the power simulation, from the sets on disk."""
    pk = pilot_keys()
    i1 = DATA / SETS[0]['index']
    j1 = Counter(g31.journal(bare(x['doi'])) for x in (read_json(i1) if i1.is_file() else []) if 'comments' in x and x['key'] not in pk)
    j2 = Counter(g31.journal(bare(x['doi'])) for x in rounds.manifest('r2calc') if is_cop(x.get('doi')) and x['key'] not in pk)
    d = doi_map()
    j3 = Counter(g31.journal(d.get(k, '')) for k in cop22_order())
    return {'round1': dict(j1), 'round2': dict(j2), 'cop22': dict(j3)}


OO_DIST = {0: 36, 1: 15, 2: 8, 3: 1, 4: 1}   # g27 labels, round 1 (61 papers): tried_dropped or added_for_review, final absent
P_ACHIEVED = 24 / 38                          # advance pilot 1 (rubric 1.0.1), all verdicts counted
SCORE_DIST = {1: 6, 2: 16, 3: 8}              # advance pilot 1 scores among scored codings (30 of 38)
SCENARIO_SETS = {'rounds_1_2': ('round1', 'round2'), 'rounds_1_2_cop22_prefix_80': ('round1', 'round2', 'cop22'),
                 'rounds_1_2_cop22_full': ('round1', 'round2', 'cop22')}


def _sizes(mix: dict, n: int, sets=None) -> list[tuple[str, int]]:
    """n papers spread over 'set|journal' cells in proportion to the sets' journal mix (largest remainder)."""
    cells = sorted((f'{s}|{j}', c) for s, v in mix.items() if sets is None or s in sets for j, c in v.items())
    w = np.array([c for _, c in cells], float)
    k = np.floor(w / w.sum() * n).astype(int)
    for i in np.argsort(-(w / w.sum() * n - k))[:n - k.sum()]:
        k[i] += 1
    return [(lab, int(x)) for (lab, _), x in zip(cells, k) if x > 0]


def _draw(rng, sizes, kind, eff):
    sizes = [x[1] if isinstance(x, tuple) else x for x in sizes]
    n = sum(sizes)
    s = np.repeat(np.arange(len(sizes)), sizes)
    lv, pr = np.array(list(OO_DIST)), np.array(list(OO_DIST.values()), float) / sum(OO_DIST.values())
    cut = np.cumsum(pr)[:-1]
    steps = np.round(rng.normal(24, 5, n)).clip(8)
    covs = [steps, rng.poisson(0.6, n), np.round(0.55 * steps + rng.normal(0, 2, n)).clip(0)]
    from statistics import NormalDist
    ppf = NormalDist().inv_cdf
    u = lambda z: (z.argsort().argsort() + 0.5) / len(z)   # empirical normal scores to uniform
    if kind == 'latent':
        z = rng.standard_normal(n)
        f = lv[np.searchsorted(cut, u(z))]
        y = eff * z + np.sqrt(1 - eff ** 2) * rng.standard_normal(n)
        o = (y > ppf(1 - P_ACHIEVED)).astype(float)
    elif kind == 'latent_score':
        z = rng.standard_normal(n)
        f = lv[np.searchsorted(cut, u(z))]
        y = eff * z + np.sqrt(1 - eff ** 2) * rng.standard_normal(n)
        sp = np.cumsum(np.array(list(SCORE_DIST.values()), float) / sum(SCORE_DIST.values()))[:-1]
        o = 1.0 + np.searchsorted([ppf(x) for x in sp], y)
    else:   # odds ratio on any outside-only loop
        f = lv[np.searchsorted(cut, rng.random(n))]
        x = (f > 0).astype(float)
        px = x.mean()
        b = np.log(eff)
        a = np.log(P_ACHIEVED / (1 - P_ACHIEVED)) - b * px          # approximately the pilot achieved rate overall
        o = (rng.random(n) < 1 / (1 + np.exp(-(a + b * x)))).astype(float)
    return f.astype(float), o, covs, s


def calibrate(kind: str, target: float, rng) -> float:
    """Latent correlation giving a population Spearman of `target` between the observed feature and outcome."""
    grid = np.linspace(0.05, 0.6, 23)
    vals = [g17.spearman(*_draw(rng, [60000], kind, r)[:2]) for r in grid]
    return float(np.interp(target, vals, grid))


def power(nsim: int = 400, nperm: int = 1000) -> dict:
    rng = np.random.default_rng(SEED)
    mix, en = journal_mix(), expected_n()
    family = len(HYPOTHESES)
    scen = [('rho 0.2, H1 (achieved)', 'latent', calibrate('latent', 0.2, rng), 1.0),
            ('rho 0.2, H2 (score)', 'latent_score', calibrate('latent_score', 0.2, rng), sum(SCORE_DIST.values()) / 38),
            ('odds ratio 1.5, H1', 'or', 1.5, 1.0), ('odds ratio 2.0, H1', 'or', 2.0, 1.0), ('odds ratio 3.0, H1', 'or', 3.0, 1.0)]
    out = {'nsim': nsim, 'nperm': nperm, 'family_size': family, 'alpha': [Q, round(Q / family, 4)],
           'note': ('power of the planned test (partial Spearman within journal x set strata, journals under MIN_STRATUM '
                    'pooled within their set, Freedman-Lane permutation) on synthetic data: feature distribution of g27 '
                    'round 1 (tried_dropped or added_for_review, final absent), achieved rate and score distribution of '
                    'advance pilot 1, covariates independent of the feature, journal mix of the sets in each scenario '
                    '(rounds 1 and 2 only for rounds_1_2). alpha 0.1 is the BH threshold when most of the family is '
                    'non-null; alpha 0.1/8 when H1 is the only non-null hypothesis (BH rank 1).'), 'rows': []}
    for label, kind, eff, frac in scen:
        for nk, n in en['scenarios'].items():
            m = int(round(n * frac))
            sizes = _sizes(mix, m, SCENARIO_SETS[nk])
            labs = [lab for lab, c in sizes for _ in range(c)]
            ps = []
            for _ in range(nsim):
                f, o, covs, s = _draw(rng, sizes, kind, eff)
                r = partial_within(f, o, covs, strata_of(labs), '', nperm=nperm, nboot=0, rng=rng)
                ps.append(r['p'] if r and np.sign(r['rho_partial']) > 0 else 1.0)
            ps = np.array(ps)
            out['rows'].append({'scenario': label, 'sample': nk, 'n': m, 'effect_parameter': round(eff, 3),
                                'strata': len(set(strata_of(labs))),
                                f'power_alpha_{Q}': round(float((ps < Q).mean()), 3),
                                f'power_alpha_{round(Q / family, 4)}': round(float((ps < Q / family).mean()), 3)})
    return out


def power_figure(pw: dict, path: Path) -> None:
    """Power of the planned test against the expected n, one panel per alpha (PNG with source footer)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    ink, bg = '#153742', '#f5f4f2'
    series = [('rho 0.2, H1 (achieved)', '#0089a8', 'o'), ('rho 0.2, H2 (score)', '#a3527f', 's'),
              ('odds ratio 2.0, H1', '#b87a0f', '^')]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True, facecolor=bg)
    for ax, a in zip(axes, pw['alpha']):
        ax.set_facecolor(bg)
        for lab, col, mk in series:
            rr = sorted([r for r in pw['rows'] if r['scenario'] == lab], key=lambda r: r['n'])
            x, y = [r['n'] for r in rr], [r[f'power_alpha_{a}'] for r in rr]
            ax.plot(x, y, color=col, lw=2, marker=mk, ms=7, label=lab)
            ax.annotate(f'{y[-1]:.2f}', (x[-1], y[-1]), xytext=(6, 0), textcoords='offset points', va='center', fontsize=8, color=ink)
        ax.axhline(0.8, color='#8a9aa0', lw=1, ls='--')
        ax.set_title(f'alpha {a}' + (' (BH, most hypotheses non-null)' if a == pw['alpha'][0] else ' (BH, H1 the only non-null)'),
                     fontsize=9, color=ink)
        ax.set_xlabel('papers in the test (expected n: rounds 1-2; + cop22 prefix of 80; + all cop22)', fontsize=8, color=ink)
        ax.spines[['top', 'right']].set_visible(False)
        ax.tick_params(colors=ink, labelsize=8)
        ax.set_ylim(0, 1)
    axes[0].set_ylabel(f"power: share of {pw['nsim']} simulated studies\nwith p < alpha and the predicted sign", fontsize=8, color=ink)
    axes[0].legend(frameon=False, fontsize=8, loc='upper left')
    fig.text(0.01, 0.01, f"Source: tools/roadmap/g34_reconstruction.py power ({commit()}, {TODAY}); synthetic data: g27 round-1 feature "
             f"distribution, advance pilot 1 outcome rates,\njournal x set strata from the sets of each scenario; {pw['nperm']} "
             "permutations per study. H2 n is the scored share (30 of 38 in pilot 1).", fontsize=6.5, color='#555')
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(path, dpi=160, facecolor=bg)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ plan
def plan_body(sets: list[dict], with_power: bool) -> dict:
    p = {'title': 'Reconstruction analysis: do outcomes depend on the iterations papers erase?',
         'direction': 'Marine Denolle (PI), October 28, 2026: papers are the paper\'s account, not its chronology, and omit '
                      'loops; reconstruct each workflow in layers (reported, review-induced, disclosed, revised) and ask '
                      'what maximizes outcome',
         'drafted': 'Claude Code workflow agent, October 28, 2026; the PI freezes',
         'population': POPULATION,
         'nature_family_exclusion': ('The Nature Communications and Communications Earth & Environment papers of the cop22 '
                                     'draw are outside this plan by design: their peer review files carry no AC or AR author '
                                     'units, and the review addendum codes disclosures by those units. (They would also '
                                     'fail C4: no discussion preprint.)'),
         'sets': sets, 'pilot_keys_excluded': sorted(pilot_keys()), 'complete': {
             'C0_open_discussion': 'set index row with comments; DOI 10.5194',
             'C1_reported': 'valid blind inquiry coding, codebook 1.5.0 (check_coding.validate); rounds 1 and 2: the file '
                            f'hashed at freeze; cop22: answered by {MODEL}, at most {REDRAW_CAP} content re-draw',
             'C2_review': f'valid review coding under REVIEW_ADDENDUM.md 1.0.0 (validate review=True with texts, checks '
                          f'{DISCLOSURE_CHECKS}), >= 1 review step by a referee, editor or commenter; answered by {MODEL}, at '
                          f'most {REDRAW_CAP} content re-draw, request recorded disclosure_checks {DISCLOSURE_CHECKS}',
             'C3_disclosed': 'C2, and the discussion and author-responses sha256 recorded with the request equal the texts on disk',
             'C4_revised': f'discussion preprint and published text found by g26; >= {LOCATED_MIN} of reported steps located',
             'C5_outcome': 'valid advance coding (check_advance via g24 advance_codings, rescue off) under the set advance '
                           'tag, every attempt submitted after the freeze commit; verdict not U4'},
         'disclosure_checks': DISCLOSURE_CHECKS, 'redraw_cap': REDRAW_CAP, 'model': MODEL,
         'features': 'Features (' + __doc__.split('Features (')[1].split('Outcomes (')[0].strip(),
         'outcomes': 'Outcomes (' + __doc__.split('Outcomes (')[1].split('Test rule  ')[0].strip(),
         'covariates': COVARIATES, 'hypotheses': HYPOTHESES, 'secondary_family': SECONDARY,
         'secondary_exclude_sets': SECONDARY_EXCLUDE, 'sensitivity': SENSITIVITY, 'decomposition': DECOMPOSITION,
         'rule': __doc__.split('Test rule  ')[1].split('Reported beside')[0].strip(),
         'q_threshold': Q, 'seed': SEED, 'nperm': NPERM, 'nboot': NBOOT, 'min_feature_papers': MIN_N,
         'min_stratum': MIN_STRATUM, 'strata': 'journal x set, journals under min_stratum pooled within their set',
         'located_min': LOCATED_MIN, 'same_event_other_doc': SAME_EVENT_OTHER_DOC,
         'g31_constants': {'loc': g31.LOC, 'changed': g31.CHANGED, 'min_tok': g31.MIN_TOK, 'land_dist': g31.LAND_DIST, 'dmatch': g31.DMATCH},
         'support': ('H1 and H2 are the primary pair; the answer uses them alone. For the population above, and for reported '
                     'warrant as the blind coder judges it: "yes, positive" when H1 or H2 is supported and neither is '
                     'reversed; "yes, negative" (the rival: requests follow weak papers) when H1 or H2 is reversed and '
                     'neither is supported; "inconsistent" when one is supported and the other reversed; "no association '
                     'detected" otherwise, qualified "rho of 0.2 or more excluded" when the upper bound of the 95% interval '
                     'of both H1 and H2 is below 0.2. S6 (round 1, agent labels) is reported beside the answer as sign '
                     'concordance with H1 and H2, not as a condition.'),
         'contrast': (f'H1 minus H8 (partial rho of outside_only_loops minus that of paper_returns against achieved, same '
                      f'papers and strata): "H1 stronger than H8" when the one-sided paired-bootstrap p (share of '
                      f'{NBOOT // 4} resamples with a difference <= 0) is below {CONTRAST_ALPHA}; reported beside the family, '
                      'not part of the answer.'),
         'shared_method': ('The review coding (disclosures, final_paper_status) and the advance coding are made by the same '
                           'model family (claude-opus-5-5) from text of the same paper. The advance coder reads only the blinded '
                           'published text (tools/blind_text.py) and sees no review record; the review coder reads the review '
                           'record and the published paper. A shared response to how much the paper reports is possible in both '
                           'directions: a terse paper makes more disclosures absent and gives less reported warrant (bias toward '
                           'a negative H1), a long paper with long responses gives more disclosures and more reported warrant '
                           '(bias toward a positive H1). S2 adds log paper words, log response words, log author and reference '
                           'counts and disclosures_dropped. The method is not shared equally across features: H7, H8 and the '
                           'covariates come from the same published text that the advance outcome is read from, by the same '
                           'model family, while the H1 feature comes from the review record; H8 therefore carries more shared-'
                           'method variance than H1, which biases the H1 minus H8 contrast toward H8. The OLMo rerun of both '
                           'tasks on the same papers (tools/code_papers_open.py) is the planned cross-model check.'),
         'gates': {'advance': 'g24 gate() on the advance codings of the full-run tag (the 40 human-rated gold papers are in '
                              'it); until it passes, outcomes are reported as the model judgment of reported warrant',
                   'disclosure': ('g30 on round 2 (tag r2-review-v2) against g27 labels of round 2, restricted to the kinds '
                                  'tried_dropped and added_for_review (g30 --kinds, output '
                                  'derived/translation/disclosure_agreement_r2_oo.json): final-status alpha (nominal) >= 0.667 '
                                  'on matched items and detection precision >= 0.6. Round 2 because the instrument was '
                                  'developed on round 1. g27 is one agent labeller of the same model family, not a reference '
                                  'standard'),
                   'absent_audit': (f'human audit of {AUDIT_N} disclosures of kind tried_dropped or added_for_review with '
                                    'final_paper_status absent, drawn at random from the kept disclosures of the complete '
                                    'papers (C0-C4), stratified by set in proportion to their absent items (audit-sample, '
                                    f'seed {SEED}); raters search the published XML text for the content; the gate passes '
                                    f'when at least {AUDIT_MIN_CONFIRMED:.0%} are confirmed absent. Until both disclosure '
                                    'gates pass, outside-only features are reported as unvalidated model coding'),
                   'node_loop': 'node and loop of disclosures have no check; S4 uses loop and is reported only'},
         'expected_n': expected_n(), 'journal_mix': journal_mix()}
    if with_power:
        p['power'] = power()
    return p


def parse_sets(specs: list[str] | None) -> list[dict]:
    sets = [dict(s) for s in SETS]
    for spec in specs or []:
        name, tags = spec.split('=', 1)
        parts = tags.split(',')
        s = next(x for x in sets if x['name'] == name)
        s.update({'inquiry_tag': parts[0], 'review_tag': parts[1], 'advance_tag': parts[2]})
        if len(parts) > 3:
            if parts[3] not in ('api', 'open'):
                sys.exit(f'--set {spec}: root must be api or open')
            s['root'] = parts[3]
        if len(parts) > 4:
            if parts[4] not in ('api', 'open'):
                sys.exit(f'--set {spec}: advance root must be api or open')
            s['advance_root'] = parts[4]
    return sets


def draft(args) -> None:
    pp = plan_path(args)
    if pp.is_file() and json.loads(pp.read_text()).get('status') == 'frozen':
        sys.exit(f'{pp} is frozen; draft does not overwrite it')
    plan = {'status': 'draft', 'frozen': None, **plan_body(parse_sets(args.set), not args.no_power),
            'md_sha256': sha(pp.with_suffix('.md'))}
    pp.parent.mkdir(parents=True, exist_ok=True)
    pp.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + '\n')
    if 'power' in plan:
        power_figure(plan['power'], pp.with_name(pp.stem + '_power.png'))
    log('g34_reconstruction.py draft', 'reconstruction plan draft', len(HYPOTHESES), f"expected n {plan['expected_n']['scenarios']}")
    print(f"{rel(pp)}: draft written; expected n {plan['expected_n']['scenarios']}")


def freeze(args) -> None:
    pp = plan_path(args)
    if pp.is_file() and json.loads(pp.read_text()).get('status') == 'frozen':
        sys.exit(f'refusing to freeze: {pp} is already frozen')
    if os.environ.get('METASCIENCE_PRIVATE') and pp == PLAN:
        sys.exit('refusing to freeze: METASCIENCE_PRIVATE is set and the plan path is the public default; a plan frozen on '
                 'another tree would be written into the public one (pass --plan for a dry run)')
    if check_coding.DISCLOSURE_CHECKS != DISCLOSURE_CHECKS:
        sys.exit(f'refusing to freeze: check_coding.DISCLOSURE_CHECKS is {check_coding.DISCLOSURE_CHECKS!r}, the plan says {DISCLOSURE_CHECKS!r}')
    synthetic = pp != PLAN
    if not synthetic:
        dirty = git('status', '--porcelain', '--untracked-files=all', '--', *FROZEN, *RECORDED).stdout.decode().strip()
        if dirty:
            sys.exit('refusing to freeze: FROZEN or RECORDED files are uncommitted or untracked; commit them first:\n' + dirty)
    bad, unknown = violations()
    if bad:
        sys.exit(f'refusing to freeze: {len(bad)} advance coding(s) of non-pilot Copernicus papers exist: ' + '; '.join(bad[:10]))
    if unknown:
        sys.exit(f'refusing to freeze: {len(unknown)} advance record(s) with no known DOI: ' + '; '.join(unknown[:10]))
    md = pp.with_suffix('.md')
    if not md.is_file():
        sys.exit(f'refusing to freeze: no plan text at {md}')
    sets = parse_sets(args.set)
    if any(s['advance_tag'] == 'plan' for s in sets) and ADV_PLAN.is_file():
        tag = json.loads(ADV_PLAN.read_text()).get('full_run_tag')
        for s in sets:
            s['advance_tag_resolved_at_freeze'] = tag if s['advance_tag'] == 'plan' else s['advance_tag']
    # the whole plan first (power included); the md and the json are written only once it is built
    body = plan_body(sets, not args.no_power)
    head = git('rev-parse', 'HEAD').stdout.decode().strip()
    md_text = re.sub(r'^Status: .*$', f'Status: frozen {TODAY} with `tools/roadmap/g34_reconstruction.py freeze` '
                     f'(code commit {head[:7]}); machine-readable plan `{pp.name}`.', md.read_text(), count=1, flags=re.M)
    plan = {'status': 'frozen', 'frozen': TODAY, 'frozen_at': dt.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'code_commit': head, 'private_root': PRIVATE_ROOT, 'synthetic': synthetic, **body,
            'cop22_order': cop22_order(), 'cop22_manifest_sha256': sha(COP22_MANIFEST),
            'cop22_preselect_sha256': sha(COP22_PRESELECT), 'inquiry_sha256_at_freeze': inquiry_hashes(sets),
            'advance_records_at_freeze': len(advance_records()), 'non_pilot_copernicus_advance_codings_at_freeze': 0,
            'inputs_sha256': {f: sha(ROOT / f) for f in FROZEN + RECORDED}, 'frozen_files': FROZEN, 'recorded_files': RECORDED,
            'advance_plan_sha256_at_freeze': sha(ADV_PLAN),
            'md_sha256': hashlib.sha256(md_text.encode()).hexdigest()}
    md.write_text(md_text)
    pp.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + '\n')
    if 'power' in plan:
        power_figure(plan['power'], pp.with_name(pp.stem + '_power.png'))
    log('g34_reconstruction.py freeze', 'reconstruction plan frozen', len(HYPOTHESES),
        f"plan sha256 {sha(pp)[:12]}; code commit {head[:7]}; expected n {plan['expected_n']['scenarios']}")
    print(f'{rel(pp)}: frozen, sha256 {sha(pp)}; commit {md.name}, {pp.name} and {pp.stem}_power.png together and push '
          'before any Copernicus advance coding')


def features(args) -> None:
    pp = plan_path(args)
    plan = json.loads(pp.read_text()) if pp.is_file() else {}
    sets = plan.get('sets') or parse_sets(args.set)
    res = collect(sets, plan.get('cop22_order') or cop22_order(), inquiry_sha=plan.get('inquiry_sha256_at_freeze'))
    P = res['papers']
    summary = {'by_set': {s['name']: {'candidates': sum(r['set'] == s['name'] for r in P.values()),
                                      **{l: sum(r['set'] == s['name'] and r['layers'][l] for r in P.values())
                                         for l in ('C0_open_discussion', 'C1_reported', 'C2_review', 'C3_disclosed', 'C4_revised')},
                                      'complete_C0_C4': sum(r['set'] == s['name'] and r['complete_C0_C4'] for r in P.values()),
                                      'disclosures_kept': sum(r.get('features', {}).get('disclosures', 0) for r in P.values() if r['set'] == s['name']),
                                      'disclosures_dropped': sum(r.get('features', {}).get('disclosures_dropped', 0) for r in P.values() if r['set'] == s['name'])}
                          for s in sets}, 'not_complete_because': dict(Counter(w for r in P.values() for w in r['not_complete_because'])),
               'notes': res['notes']}
    write_json(OUT / 'features.json', {'summary': summary, 'papers': P}, [rel(pp)] + [rel(folder(s, t))
               for s in sets for t in ('inquiry', 'review')] + [rel(STATE) + ' (read only)'], {'sets': sets})
    log('g34_reconstruction.py features', 'reconstruction features and layer completeness (no outcome read)', len(P),
        json.dumps({k: v['complete_C0_C4'] for k, v in summary['by_set'].items()}))
    print(json.dumps(summary, indent=1))


def audit_sample(args) -> None:
    """The absent-status audit sample: AUDIT_N kept disclosures of the two outside-only kinds with status absent, from
    the complete papers, stratified by set in proportion (largest remainder), random within a set (default_rng(SEED))."""
    pp = plan_path(args)
    plan = json.loads(pp.read_text()) if pp.is_file() else {}
    sets = plan.get('sets') or parse_sets(args.set)
    P = collect(sets, plan.get('cop22_order') or cop22_order(), e4=False, inquiry_sha=plan.get('inquiry_sha256_at_freeze'))['papers']
    pool = {}
    for k, r in sorted(P.items()):
        if not r['complete_C0_C4']:
            continue
        S = next(s for s in sets if s['name'] == r['set'])
        c, kept, _ = valid_review(S, [k])[k]
        for i, d in enumerate(as_items(kept), 1):
            if d['kind'] in OO_KINDS and d['final'] == 'absent':
                pool.setdefault(r['set'], []).append({'id': f'{k}#{i}', 'key': k, 'set': r['set'], 'doi': r['doi'], 'unit': d['unit'],
                                                      'kind': d['kind'], 'quote': d.get('quote'), 'content': d.get('content')})
    tot = sum(len(v) for v in pool.values())
    if not tot:
        sys.exit('no absent disclosures of the two kinds among complete papers yet')
    n = min(AUDIT_N, tot)
    w = {s: len(v) / tot * n for s, v in pool.items()}
    alloc = {s: int(x) for s, x in w.items()}
    for s in sorted(w, key=lambda s: -(w[s] - alloc[s]))[:n - sum(alloc.values())]:
        alloc[s] += 1
    rng = np.random.default_rng(SEED)
    rows = []
    for s in sorted(pool):
        idx = rng.permutation(len(pool[s]))[:alloc[s]]
        rows += [pool[s][i] for i in sorted(idx)]
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / 'absent_audit_sample.json', {'n': len(rows), 'pool': {s: len(v) for s, v in pool.items()}, 'allocation': alloc,
                                                  'items': rows}, [rel(pp)], {'seed': SEED, 'audit_n': AUDIT_N})
    with (OUT / 'absent_audit_form.csv').open('w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['id', 'set', 'doi', 'unit', 'kind', 'quote', 'content', 'confirmed_absent (yes/no)', 'where found (locator)', 'rater'])
        for r in rows:
            wr.writerow([r['id'], r['set'], r['doi'], r['unit'], r['kind'], r['quote'], r['content'], '', '', ''])
    log('g34_reconstruction.py audit-sample', 'absent-status audit sample (no outcome read)', len(rows), json.dumps(alloc))
    print(f'{len(rows)} items ({alloc}) to {rel(OUT / "absent_audit_form.csv")}; results go to {rel(OUT / "absent_audit.json")} '
          '({"items": [{"id": ..., "confirmed_absent": true|false}, ...]})')


# ------------------------------------------------------------------------------------------------ test
def load_advance(tag: str, root: str = 'api') -> dict:
    """Valid advance codings of a tag (g24 advance_codings, rescue off); root 'open': the same revalidation of the files
    of private/analysis/codings/open/<tag>/."""
    import g24_advance as g24
    if root == 'api':
        return g24.advance_codings(tag)[0]
    out = {}
    for f in sorted((CODINGS / 'open' / tag).glob('g22_*.json')):
        try:
            n, errs, _ = g24._revalidate(json.loads(f.read_text()))
        except Exception:  # noqa: BLE001
            continue
        if not errs:
            out[n['key']] = n
    return out


def outcomes(c: dict) -> dict:
    import g24_advance as g24
    import check_advance as ca
    d = g24.derived(c)
    g = ca.basis_gain(c)
    cr = g['criteria']
    ok = lambda x: cr[x] == 'met' or (x == 'W3' and cr[x] == 'not_applicable')
    a = d['assessable']
    return {'verdict': d['verdict'], 'screen_fail': d['screen_fail'], 'achieved': float(d['achieved']),
            'achieved_assessable': float(d['achieved']) if a else None,
            'score': None if d['score'] is None else float(d['score']),
            'W3': float(ok('W3')) if a else None, 'W_count': float(sum(ok(x) for x in ('W1', 'W2', 'W3', 'W4'))) if a else None,
            'overreach': float({'no': 0, 'partly': 1, 'yes': 2}[c['overreach']['exceeds_warrant']]) if a else None}


def run_family(hyps, keys, F, O, J, setn, tagp, covs_extra=None, strata_mode='journal_set', feature_sub=None,
               outcome_sub=None) -> list[dict]:
    rows = []
    for h in hyps:
        fn = (feature_sub or {}).get(h['id'], h['feature'])
        on = (outcome_sub or {}).get(h['id'], h['outcome'])
        ks = [k for k in keys if O[k].get(on) is not None and F[k].get(fn) is not None]
        f, o = [F[k][fn] for k in ks], [O[k][on] for k in ks]
        cv = [[F[k][c] for k in ks] for c in COVARIATES if c != fn] if covs_extra != 'none' else []
        if covs_extra == 'more':
            cv += [np.log1p([F[k]['paper_words'] for k in ks]), np.log1p([F[k]['response_words'] for k in ks]),
                   np.log1p([F[k].get('n_authors') or 0 for k in ks]), np.log1p([F[k].get('n_refs') or 0 for k in ks]),
                   [F[k]['disclosures_dropped'] for k in ks]]
        st = strata_of([f'{setn[k]}|{J[k]}' if strata_mode == 'journal_set' else J[k] for k in ks])
        ok = testable(f, o)
        r = partial_within(f, o, cv, st, f'recon|{tagp}|{h["id"]}') if ok else None
        row = {'id': h['id'], 'feature': fn, 'outcome': on, 'predicted_sign': h['sign'], 'n': len(ks),
               'feature_nonzero': int(sum(x > 0 for x in f)), 'testable': bool(ok and r), **({'note': h['note']} if h.get('note') else {})}
        row.update(r or {'rho_partial': None, 'p': 1.0})
        row['direction_ok'] = bool(r and np.sign(r['rho_partial']) == h['sign'])
        rows.append(row)
    for r, q in zip(rows, g17.bh([r['p'] for r in rows])):
        r['q'] = round(float(q), 4)
        r['verdict'] = ('supported' if r['q'] < Q and r['direction_ok'] else 'reversed' if r['q'] < Q else 'not supported')
    return rows


def answer(prim: list[dict], s6: list[dict]) -> dict:
    """The answer to the PI question from H1 and H2 alone; S6 sign concordance beside it."""
    h = {r['id']: r for r in prim if r['id'] in ('H1', 'H2')}
    v = [h[i]['verdict'] for i in ('H1', 'H2')]
    sup, rev = 'supported' in v, 'reversed' in v
    a = ('inconsistent' if sup and rev else 'yes, positive' if sup else 'yes, negative' if rev else 'no association detected')
    if a == 'no association detected' and all(h[i].get('ci') and h[i]['ci'][1] < 0.2 for i in ('H1', 'H2')):
        a += '; rho of 0.2 or more excluded'
    s6r = {r['id']: r for r in s6}
    conc = {i: (None if s6r.get(i, {}).get('rho_partial') is None or h[i].get('rho_partial') is None
                else bool(np.sign(s6r[i]['rho_partial']) == np.sign(h[i]['rho_partial']))) for i in ('H1', 'H2')}
    return {'answer': a, 'population': POPULATION, 'H1': v[0], 'H2': v[1], 'S6_sign_concordance': conc}


def local_minute(iso: str) -> dt.datetime:
    """A commit time (git %cI) in the machine's local zone, naive, to the minute (state.json times are local minutes)."""
    return dt.datetime.fromisoformat(iso).astimezone().replace(tzinfo=None, second=0, microsecond=0)


def freeze_commit(pp: Path, plan: dict, accept: bool) -> tuple[dict, list[str]]:
    """The git checks of `test` (see the docstring); returns (record, FROZEN files changed since the freeze commit)."""
    r = git('log', '-n1', '--format=%H %cI', '--', PLAN_REL).stdout.decode().split()
    if len(r) != 2:
        sys.exit(f'refusing to test: {PLAN_REL} has no commit')
    h, when = r
    at = lambda f: git('show', f'{h}:{f}')
    committed = at(PLAN_REL)
    if committed.returncode or committed.stdout != pp.read_bytes():
        sys.exit(f'refusing to test: {PLAN_REL} differs from its version in commit {h[:7]} (the last commit touching it)')
    if json.loads(committed.stdout).get('status') != 'frozen':
        sys.exit(f'refusing to test: the plan in commit {h[:7]} is not frozen')
    if not git('branch', '-r', '--contains', h).stdout.decode().strip():
        sys.exit(f'refusing to test: the freeze commit {h[:7]} is on no remote branch (push it first)')
    if git('merge-base', '--is-ancestor', plan['code_commit'], h).returncode:
        sys.exit(f"refusing to test: the plan's code commit {plan['code_commit'][:7]} is not an ancestor of {h[:7]}")
    changed = [f for f in plan['frozen_files'] if (x := at(f)).returncode or x.stdout != (ROOT / f).read_bytes()]
    if changed and not accept:
        sys.exit(f'refusing to test: changed since the freeze commit {h[:7]}: {changed} (rerun with --accept-deviation to record them)')
    rec_changed = [f for f in plan.get('recorded_files', []) if (x := at(f)).returncode or x.stdout != (ROOT / f).read_bytes()]
    return {'mode': 'git', 'freeze_commit': h, 'freeze_commit_time': when, 'cutoff_local': local_minute(when).strftime('%Y-%m-%d %H:%M'),
            'recorded_changed_since_freeze': rec_changed}, changed


def advance_after_freeze(tags: dict, keys: list[str], cutoff: str) -> list[str]:
    """Advance attempts (batch submission or synchronous attempt time) at or before the cutoff minute, per key used."""
    st, bad = state(), []
    for k, tag in keys:
        times = [b['submitted'] for b in st['batches'] if b['tag'] == tag and k in b['keys']]
        times += [x['at'] for x in st['spent'].get(f'{tag}:{k}', []) if x.get('batch') is None]
        if not times:
            bad.append(f'{tag}:{k} (no attempt recorded in state.json)')
        elif min(times) <= cutoff:
            bad.append(f'{tag}:{k} ({min(times)})')
    return bad


def test(args) -> None:
    pp = plan_path(args)
    if getattr(args, 'plan', None) and not os.environ.get('METASCIENCE_PRIVATE'):
        sys.exit('refusing to test: --plan is for synthetic trees only (set METASCIENCE_PRIVATE)')
    if not pp.is_file() or json.loads(pp.read_text()).get('status') != 'frozen':
        sys.exit(f'refusing to test: no frozen plan at {pp}')
    plan = json.loads(pp.read_text())
    if not ADV_PLAN.is_file():
        sys.exit(f'refusing to test: {rel(ADV_PLAN)} does not exist (freeze the advance instrument first)')
    if pp == PLAN:
        fz, changed = freeze_commit(pp, plan, args.accept_deviation)
    else:
        changed = [f for f in plan['frozen_files'] if sha(ROOT / f) != plan['inputs_sha256'][f]]
        if changed and not args.accept_deviation:
            sys.exit(f'refusing to test: changed since the freeze: {changed} (rerun with --accept-deviation to record them)')
        fz = {'mode': 'synthetic (METASCIENCE_PRIVATE and --plan; no git checks)', 'cutoff_local': plan['frozen_at']}
    adv_tag = json.loads(ADV_PLAN.read_text()).get('full_run_tag')
    sets = plan['sets']
    res = collect(sets, plan['cop22_order'], prefix_kinds=('inquiry', 'review', 'advance'),
                  inquiry_sha=plan.get('inquiry_sha256_at_freeze'))
    P = res['papers']
    O, F, J, setn = {}, {}, {}, {}
    tags = {s['name']: (adv_tag if s['advance_tag'] == 'plan' else s['advance_tag']) for s in sets}
    aroot = {tags[s['name']]: s.get('advance_root', 'api') for s in sets}
    adv = {t: load_advance(t, aroot.get(t, 'api')) for t in set(tags.values()) | {adv_tag}}
    met = {}
    for s in sets:
        f = DERIVED / s['metrics'] / 'metrics.json'
        met.update({'g22_' + m['id']: m for m in (read_json(f) if f.is_file() else [])})
    import g24_advance as g24
    used = [(k, tags[r['set']]) for k, r in P.items() if r['complete_C0_C4'] and k in adv[tags[r['set']]]]
    early = advance_after_freeze(tags, [(k, t) for k, t in used if aroot.get(t, 'api') == 'api'], fz['cutoff_local'])
    if early:
        sys.exit(f'refusing to test: {len(early)} advance attempt(s) of papers in the test are not later than the freeze '
                 f"({fz['cutoff_local']}): " + '; '.join(early[:10]))
    u4 = []
    for k, r in P.items():
        c = adv[tags[r['set']]].get(k)
        r['layers']['C5_outcome'] = c is not None
        if not r['complete_C0_C4'] or c is None:
            continue
        o = outcomes(c)
        if o['screen_fail']:
            u4.append(k)
            continue
        o.update({x: met.get(k, {}).get(x) for x in ('cnp', 'fwci')})
        O[k], F[k], J[k], setn[k] = o, dict(r['features']), r['journal'], r['set']
        F[k].update({'paper_words': g24.read_meta(k, c).get('words', 0), 'n_authors': met.get(k, {}).get('n_authors'),
                     'n_refs': met.get(k, {}).get('n_refs')})
    keys = sorted(O)
    if not keys:
        sys.exit('no complete papers with a valid advance coding')
    prim = run_family(HYPOTHESES, keys, F, O, J, setn, 'primary')
    excl = plan.get('secondary_exclude_sets', {})
    sec = run_family(SECONDARY, [k for k in keys if setn[k] not in excl], F, O, J, setn, 'secondary')
    H = {h['id']: h for h in HYPOTHESES}
    sens = {'S1_plain': run_family(HYPOTHESES, keys, F, O, J, setn, 's1', covs_extra='none'),
            'S2_more_covariates': run_family(HYPOTHESES, keys, F, O, J, setn, 's2', covs_extra='more'),
            'S3_strata_journal': run_family(HYPOTHESES, keys, F, O, J, setn, 's3', strata_mode='journal'),
            'S4_flagged': run_family(HYPOTHESES[:2], keys, F, O, J, setn, 's4', feature_sub={'H1': 'outside_only_loops_flagged', 'H2': 'outside_only_loops_flagged'}),
            'S5_visible_V': run_family([H['H4']], keys, F, O, J, setn, 's5', feature_sub={'H4': 'review_added_V_in_paper'}),
            'S6_e4': run_family(HYPOTHESES[:2], [k for k in keys if setn[k] == 'round1' and F[k].get('oo_e4_g27') is not None],
                                F, O, J, setn, 's6', feature_sub={'H1': 'oo_e4_g27', 'H2': 'oo_e4_g27'}),
            'S7_assessable': run_family([H[i] for i in ('H1', 'H3', 'H7', 'H8')], keys, F, O, J, setn, 's7',
                                        outcome_sub={i: 'achieved_assessable' for i in ('H1', 'H3', 'H7', 'H8')})}
    deco = {'D1_tried_dropped': run_family(HYPOTHESES[:2], keys, F, O, J, setn, 'd1', feature_sub={'H1': 'oo_tried_dropped', 'H2': 'oo_tried_dropped'}),
            'D2_added_for_review': run_family(HYPOTHESES[:2], keys, F, O, J, setn, 'd2', feature_sub={'H1': 'oo_added_for_review', 'H2': 'oo_added_for_review'})}
    for v in list(sens.values()) + list(deco.values()):   # reported, not tested: no verdicts
        for r in v:
            r.pop('verdict', None)
    ach = [k for k in keys if O[k]['achieved'] is not None]
    st = np.array(strata_of([f'{setn[k]}|{J[k]}' for k in ach]))
    mh = mantel_haenszel([F[k]['any_outside_only'] for k in ach], [O[k]['achieved'] for k in ach], st, 'recon|mh')
    rng = g20.gen('recon|contrast')
    groups = [np.flatnonzero(st == g) for g in np.unique(st)]

    def prho(ii, fn):
        cv = [[F[ach[i]][c] for i in ii] for c in COVARIATES if c != fn]
        r = partial_within([F[ach[i]][fn] for i in ii], [O[ach[i]]['achieved'] for i in ii], cv, st[ii], '', nperm=1, nboot=0, rng=rng)
        return r['rho_partial'] if r else np.nan
    diffs = []
    for _ in range(NBOOT // 4):
        ii = np.concatenate([gi[rng.integers(0, len(gi), len(gi))] for gi in groups])
        diffs.append(prho(ii, 'outside_only_loops') - prho(ii, 'paper_returns'))
    fin = [d for d in diffs if np.isfinite(d)]
    p1 = (1 + sum(d <= 0 for d in fin)) / (len(fin) + 1) if fin else 1.0
    contrast = {'H1_minus_H8': round(float(prho(np.arange(len(ach)), 'outside_only_loops') - prho(np.arange(len(ach)), 'paper_returns')), 3),
                'ci': g20.ci(diffs), 'resamples': NBOOT // 4, 'p_one_sided': round(float(p1), 4),
                'verdict': 'H1 stronger than H8' if p1 < CONTRAST_ALPHA else 'not shown'}
    da = DERIVED / 'translation' / 'disclosure_agreement_r2_oo.json'
    dgate = {'status': f'no g30 run on file ({rel(da)})'}
    if da.is_file():
        a = read_json(da)
        fa = (a.get('final_status') or {}).get('alpha_nominal')
        pr = (a.get('detection') or {}).get('precision')
        dgate = {'final_status_alpha': fa, 'precision': pr,
                 'passed': bool(fa is not None and pr is not None and fa >= 0.667 and pr >= 0.6)}
    au = OUT / 'absent_audit.json'
    agate = {'status': f'no human audit on file ({rel(au)})'}
    if au.is_file():
        items = (json.loads(au.read_text()).get('data') or json.loads(au.read_text())).get('items', [])
        rated = [x for x in items if isinstance(x.get('confirmed_absent'), bool)]
        share = sum(x['confirmed_absent'] for x in rated) / len(rated) if rated else None
        agate = {'rated': len(rated), 'confirmed_absent_share': None if share is None else round(share, 3),
                 'passed': bool(share is not None and len(rated) >= AUDIT_N * 0.9 and share >= AUDIT_MIN_CONFIRMED)}
    out = {'plan_sha256': sha(pp), 'freeze': fz, 'deviations': changed, 'advance_tags': tags, 'papers': len(keys), 'U4_excluded': len(u4),
           'by_set': dict(Counter(setn[k] for k in keys)), 'by_journal': dict(Counter(J[k] for k in keys)),
           'candidates': len(P), 'complete_C0_C4': sum(r['complete_C0_C4'] for r in P.values()),
           'primary': prim, 'answer': answer(prim, sens['S6_e4']), 'secondary': sec, 'sensitivity': sens, 'decomposition': deco,
           'mantel_haenszel_any_outside_only_vs_achieved': mh, 'contrast_H1_H8': contrast,
           'gates': {'advance': g24.gate(adv[adv_tag]), 'disclosure': dgate, 'absent_audit': agate},
           'verdicts': dict(Counter(r['verdict'] for r in prim)), 'notes': res['notes']}
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / 'results.json', out, [rel(pp), rel(ADV_PLAN), rel(STATE) + ' (read only)'] + [f'private/analysis/codings/api/{t}' for t in set(tags.values())]
               + [rel(folder(s, t)) for s in sets for t in ('inquiry', 'review')])
    md = ['# Reconstruction test (g34)', '',
          f"Plan `{pp.name}` (sha256 `{out['plan_sha256'][:12]}`), frozen {plan['frozen']} ({fz['mode']}). {len(keys)} complete papers "
          f"({out['by_set']}); U4 excluded {len(u4)}. Answer: **{out['answer']['answer']}** (population: {POPULATION}). "
          f"S6 sign concordance {out['answer']['S6_sign_concordance']}. Advance gate: {out['gates']['advance'].get('status')}. "
          f"Disclosure gate: {dgate.get('passed', dgate.get('status'))}. Absent audit: {agate.get('passed', agate.get('status'))}."
          + (f' Deviations: {changed}.' if changed else ''), '',
          '| id | feature | outcome | n | rho partial | 95% CI | p | q | verdict |', '|:--|:--|:--|--:|--:|:--|--:|--:|:--|']
    md += [f"| {r['id']} | {r['feature']} | {r['outcome']} | {r['n']} | {r['rho_partial']} | {r.get('ci')} | {r['p']} | {r['q']} | {r['verdict']} |"
           for r in prim + sec]
    md += ['', f"Mantel-Haenszel OR, any outside-only loop vs achieved: {mh}.", f"H1 minus H8: {contrast}."]
    (OUT / 'RECONSTRUCTION_TEST.md').write_text('\n'.join(md) + '\n')
    log('g34_reconstruction.py test', 'reconstruction plan run', len(keys), f"{out['answer']['answer']}; {out['verdicts']}")
    print(out['answer'], out['verdicts'], out['by_set'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['draft', 'freeze', 'features', 'audit-sample', 'power', 'test'])
    ap.add_argument('--plan', default=None)
    ap.add_argument('--set', action='append', default=None, help='NAME=INQUIRY_TAG,REVIEW_TAG,ADVANCE_TAG[,ROOT]')
    ap.add_argument('--no-power', action='store_true')
    ap.add_argument('--accept-deviation', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'power':
        pw = power()
        print(json.dumps(pw, indent=1))
        log('g34_reconstruction.py power', 'power of the planned test (synthetic data only)', len(pw['rows']),
            json.dumps({f"{r['scenario']}|{r['sample']}": r[f'power_alpha_{Q}'] for r in pw['rows'] if r['scenario'].startswith('rho 0.2, H1')}))
    else:
        {'draft': draft, 'freeze': freeze, 'features': features, 'audit-sample': audit_sample, 'test': test}[a.cmd](a)
