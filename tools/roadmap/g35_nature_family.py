"""Phase 3c: the Nature-family papers (Nature Communications, NC; Communications Earth & Environment, CEE; Nature) of
rounds 1 and 2 and of the 2022 draw (cop22). Analysis plan, drafted here, frozen by the PI, then run. Modelled on
g34_reconstruction.py, whose functions it calls for every shared step.

Why a separate plan. The PI requires every draw to include all journals equally and put the NC and CEE peer review
files in the review arm (private/data/roadmap/DECISIONS.md, October 28, 2026). The frozen reconstruction plan
(preregistration/reconstruction.json, g34) covers Copernicus papers only: its review addendum codes disclosures by
Copernicus author units (AC, AR). preregistration/ERRATA.md promises the cop22 NC and CEE papers their own plan,
frozen before any of their advance codings exists, with an advance tag apart from the full run. This is that plan,
extended to the Nature Portfolio papers of rounds 1 and 2 that publish a peer review file. Human-readable plan:
preregistration/nature-family.md; machine-readable plan: preregistration/nature-family.json (draft, then frozen).

Sample (sample())  eligible papers (the set's manifest) with a 10.1038 DOI whose review folder holds a peer review file
         that tools/roadmap/g27_nature_units.py reads (is_nature); the advance pilot papers (g34.pilot_keys) excluded.
  nature_r1  derived/calc1/manifest.jsonl (round 1); files from g37_nature_review_files.py; arm post-hoc
  nature_r2  derived/r2calc/manifest.jsonl (round 2); files from g37; arm post-hoc
  nature22   derived/cop22calc/manifest.jsonl (cop22); files from g32 `prf`; arm prospective; entered in g32's
             draw_order (derived/cop22/preselect.json), fixed at freeze (nat_order); the test takes the longest prefix of
             that order in which every paper has an attempt under the inquiry, review and advance tags (g34.prefix_len),
             so a budget-limited subset is a prefix, never a choice.
Arms     prospective: no advance coding or advance request of any of its papers exists at freeze (freeze refuses
         otherwise) and every advance attempt used by the test is later than the freeze commit (test refuses
         otherwise). Post-hoc: the round-1 and round-2 papers were coded under the advance full run (tag full-advance,
         preregistration/advance-plan.json) before this plan; their verdicts exist on disk. The plan is fixed before any
         of their review codings (the feature layer) exists: freeze refuses when a review coding, batch request or
         attempt under REVIEW_TAG (or any request carrying the Nature-family addendum) exists for a post-hoc paper, or
         an advance record under a tag other than full-advance; it records the sha256 of each post-hoc paper's
         full-advance coding, and the test uses that file only (a changed or re-coded file is a deviation). The
         post-hoc arm is reported apart from the prospective arm and enters the pooled sensitivity only as a labelled
         variant.
Tags     inquiry calc1 / r2 (coded before this plan, hashed at freeze) / cop22; review REVIEW_TAG for every set
         (tools/code_papers.py --review-dir private/data/roadmap/review: the peer review file as units, review addendum
         1.0.0 plus REVIEW_ADDENDUM_NATURE.md 1.0.0, validator tools/check_coding_nature.py); advance full-advance
         (post-hoc) / nature22-advance (prospective; agents/advance/RUBRIC.md as frozen in advance-plan.json).
Layers   1 reported, 2 review-induced, 3 disclosed. Layer 4 (revised after submission) needs a discussion preprint;
         these papers have none, so revision_share and H7 do not apply.
Complete (all of; a paper missing a layer is counted by layer and reported)
  N0 review file       g27_nature_units parses the peer review file cleanly: at least one referee unit and one author
                       unit with own text
  N1 reported          a valid blind inquiry coding (check_coding.validate, codebook 1.5.0) under the set's inquiry tag;
                       post-hoc sets: the file hashed at freeze; nature22: answered by MODEL, at most REDRAW_CAP content
                       re-draws (state.json 'spent', read through g34.provenance)
  N2 review-induced    a valid review coding under REVIEW_TAG: check_coding_nature.validate_nature(texts, checks
                       DISCLOSURE_CHECKS), review_addendum_version 1.0.0, review_source nature_review_file,
                       nature_addendum_version 1.0.0, at least one review step triggered by a referee or the editor
                       (g31.REVIEWERS); answered by MODEL, at most REDRAW_CAP content re-draws, from a request that
                       recorded disclosure_checks DISCLOSURE_CHECKS
  N3 disclosed         N2, and the sha256 of the peer-review-file document recorded with the request equals the one
                       code_papers.review_inputs builds now
  N5 outcome           (test only) a valid advance coding under the set's advance tag (g34.load_advance, rescue off),
                       verdict not U4; prospective: every advance attempt later than the freeze commit; post-hoc: the
                       file hashed at freeze
Features (per paper; g34.features_of on g31_reconstruct.paper() with REVIEW_TAG as the disclosure source and the kept
disclosures of check_coding_nature.kept_disclosures; the definitions of the reconstruction plan): outside_only_loops,
tried_dropped, review_loops, review_V_loops, claim_narrowed, paper_returns, paper_revisits, paper_steps, disclosures,
disclosures_dropped, and g34's decomposition and sensitivity features. revision_share is None (no layer 4). The author
document of the same-event rule is every A unit of the paper (unit locator up to the first '-'). g31's disclosure match
to review steps reads Copernicus document names only, so on these papers no disclosure matches a review step; no
feature used here depends on that match. response_words: words of the A units.
Outcomes  as the reconstruction plan (g34.outcomes: achieved, score, W3, W_count, overreach; cnp, fwci from the set's
metrics.json).

Analysis
  D  Descriptive, no confirmatory claim, no p-value, no verdict, for the prospective arm, the post-hoc arm and both:
     per feature n, mean, median, quartiles, papers with at least one (g31.dist); verdict distribution; for each
     hypothesis of the reconstruction family but H7, the partial Spearman within journal strata with its 95% bootstrap
     interval (NBOOT, g20.gen 'nature|<arm>|<id>'), reported as an estimate only; feature distributions by journal.
     H8 (paper_returns) is left out of the post-hoc and both-arms estimates (NOT_BLIND_POSTHOC).
  P  Pooled sensitivity of the reconstruction hypotheses: the complete Copernicus papers of the frozen g34 test (its own
     sets, tags, checks and cut-off, read through g34; not run when g34's checks refuse) with the complete Nature-family
     papers; H1-H6 and H8 (H7 needs layer 4); g34's test rule (partial Spearman, Freedman-Lane permutation within
     strata, bootstrap, BH q < Q over this family). P1 strata journal (a journal is its own stratum, journals under
     MIN_STRATUM pooled), prospective arm only; P1b as P1 with the post-hoc arm added (labelled post-hoc); P2 strata
     journal x set, both arms. P1b and P2 leave out H8 (NOT_BLIND_POSTHOC): its feature, paper_returns, comes from the
     inquiry coding, which exists for the post-hoc papers and entered the advance test (H9) before this plan. Reported beside the frozen reconstruction answer; it does not change that answer. The
     H1-H2 answer rule of g34 is applied to P1 and labelled 'pooled sensitivity'.
  Power  power() runs the planned test on synthetic data (g34's generator) at the expected n of each sample; the n of
     either arm alone cannot support a confirmatory test.

draft     writes the plan json with status 'draft' (no refusal checks) and the power figure; safe to rerun.
freeze    refuses (1) when the plan json is already frozen; (2) when METASCIENCE_PRIVATE is set and the plan path is the
          default; (3) when check_coding.DISCLOSURE_CHECKS is not DISCLOSURE_CHECKS; (4) when a FROZEN or RECORDED file
          is uncommitted or untracked (git status --porcelain --untracked-files=all); (5) when an advance record exists
          for a prospective paper: a file in private/analysis/codings/{api,open}/*advance*/ or its _invalid/, or in
          derived/advance/rescued/, a key of an '*-advance' batch in state.json, or a '<tag>-advance:<key>' attempt in
          state.json 'spent' (read only); (6) when a post-hoc paper has such a record under a tag other than its set's
          advance tag, or any review record (review_records()); (7) when the plan md is missing or the sample is empty.
          It builds the whole plan (power included) before it rewrites the md Status line and writes the json with the
          code commit (HEAD), the freeze time, the private tree read (common.PRIVATE_ROOT), the sample and nat_order,
          the parse result of each paper, the sha256 of each post-hoc inquiry and advance coding, of every FROZEN and
          RECORDED file, the manifests, the preselection, the indexes and each review file PDF.
features  computes the layers and features (no outcome read) to derived/nature_family/features.json.
power     prints the power table (synthetic data only).
test      refuses unless the plan is frozen; on the default path, unless the plan equals its version in the last commit
          touching preregistration/nature-family.json, that commit is on a remote branch, the plan's code commit is its
          ancestor, and every FROZEN file equals its version there (else --accept-deviation, recorded). It refuses when
          any advance attempt of a prospective paper (state.json batch 'submitted' or synchronous 'spent' time, minute
          resolution, local time) is not later than the freeze commit time, and when a post-hoc paper's advance coding
          differs from the file hashed at freeze (else --accept-deviation, recorded). Then writes
          derived/nature_family/{results.json, NATURE_FAMILY_TEST.md}. --plan is refused unless METASCIENCE_PRIVATE is
          set (synthetic tree; the freeze time stands in for the commit time).
Run:      python tools/roadmap/g35_nature_family.py draft | freeze | features | power | test [--plan PATH] [--no-power]
"""
from __future__ import annotations
import argparse
import datetime as dt
import functools
import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from common import ROOT, PRIVATE_ROOT, DATA, DERIVED, TODAY, commit, log, read_json, rel, write_json
import check_coding
import g31_reconstruct as g31
import g34_reconstruction as g34
import g27_nature_units as g27n

sys.path.insert(0, str(ROOT / 'tools'))
import check_coding_nature as ccn  # noqa: E402

PLAN = ROOT / 'preregistration' / 'nature-family.json'
PLAN_REL = 'preregistration/nature-family.json'
OUT = DERIVED / 'nature_family'
MODEL, DISCLOSURE_CHECKS, REDRAW_CAP = g34.MODEL, g34.DISCLOSURE_CHECKS, g34.REDRAW_CAP
Q, SEED, NPERM, NBOOT, MIN_STRATUM = g34.Q, 2035, g34.NPERM, g34.NBOOT, g34.MIN_STRATUM
REVIEW_TAG = 'nature-review'
SETS = [
    {'name': 'nature_r1', 'arm': 'posthoc', 'inquiry_tag': 'calc1', 'review_tag': REVIEW_TAG, 'advance_tag': 'full-advance',
     'root': 'api', 'manifest': 'derived/calc1/manifest.jsonl', 'index': 'derived/review/open_review_index_nature12.json',
     'metrics': 'gold', 'inquiry_fixed_at_freeze': True,
     'design': 'round-1 preselection (equal cnp quintiles of 600 papers), Nature Portfolio rows with a peer review file'},
    {'name': 'nature_r2', 'arm': 'posthoc', 'inquiry_tag': 'r2', 'review_tag': REVIEW_TAG, 'advance_tag': 'full-advance',
     'root': 'api', 'manifest': 'derived/r2calc/manifest.jsonl', 'index': 'derived/review/open_review_index_nature12.json',
     'metrics': 'r2', 'inquiry_fixed_at_freeze': True,
     'design': 'round-2 preselection (open access, at most 4 per journal), Nature Portfolio rows with a peer review file'},
    {'name': 'nature22', 'arm': 'prospective', 'inquiry_tag': 'cop22', 'review_tag': REVIEW_TAG, 'advance_tag': 'nature22-advance',
     'root': 'api', 'manifest': 'derived/cop22calc/manifest.jsonl', 'index': 'derived/review/open_review_index_nature22.json',
     'metrics': 'cop22', 'inquiry_fixed_at_freeze': False,
     'design': 'g32 cop22 draw, NC and CEE rows: equal quota per journal spread over impact quintiles'},
]
JOURNAL = {'s41467': 'NC', 's43247': 'CEE', 's41586': 'Nature', 's41561': 'NGEO', 's41558': 'NCC', 's41612': 'npjCAS',
           's41559': 'NEE', 's41598': 'SciRep'}
HYPOTHESES = [h for h in g34.HYPOTHESES if h['id'] != 'H7']   # H7 needs layer 4 (a discussion preprint)
# Hypotheses whose feature is not blind for the post-hoc arm: paper_returns comes from the inquiry coding (g31.paper reads
# c1's final_paper sequence), which exists for the post-hoc papers and entered advance-plan.json H9 in aggregate.
NOT_BLIND_POSTHOC = {'H8'}
HYPOTHESES_WITH_POSTHOC = [h for h in HYPOTHESES if h['id'] not in NOT_BLIND_POSTHOC]
FEATURES = ['outside_only_loops', 'tried_dropped', 'review_loops', 'review_V_loops', 'claim_narrowed', 'paper_returns',
            'paper_revisits', 'paper_steps', 'disclosures', 'disclosures_dropped', 'response_words']
OWN = ['tools/roadmap/g35_nature_family.py', 'tools/roadmap/g27_nature_units.py', 'tools/roadmap/g37_nature_review_files.py',
       'tools/check_coding_nature.py', 'agents/coder/REVIEW_ADDENDUM_NATURE.md', 'agents/coder/review_addendum_nature.schema.json']
FROZEN = OWN + [f for f in g34.FROZEN if f not in OWN]
RECORDED = list(g34.RECORDED) + ['tools/roadmap/g32_copernicus_draw.py']
RATES = {k: g34.RATES[k] for k in ('review_valid', 'advance_valid', 'inquiry_valid')}
POSTHOC_STATEMENT = (
    'The round-1 and round-2 papers of this plan (sets nature_r1, nature_r2) already have advance codings under the '
    'full run (tag full-advance), made before this plan was drafted; their verdicts are on disk and entered the advance '
    'test of preregistration/advance-plan.json in aggregate. Their review codings, from which the review-derived features '
    '(outside_only_loops, tried_dropped, review_loops, review_V_loops, claim_narrowed, disclosures, disclosures_dropped) '
    'are computed, do not exist at freeze (freeze refuses otherwise). paper_returns, paper_revisits and paper_steps come '
    'from the inquiry codings (calc1, r2), which exist for these papers, and the advance test related them to outcomes in '
    'aggregate (advance-plan.json H9, any return after failure against score). The plan is therefore blind to the '
    'association of the review-derived features with outcome for these papers, not to their outcomes and not to H8 '
    '(paper_returns) or the three covariates. They form a post-hoc arm: reported apart from the prospective arm '
    '(nature22) and added to the pooled sensitivity only as the labelled variants P1b and P2, which leave out H8, as do the '
    'post-hoc and both-arms estimates; the covariates stay in every model and are labelled not blind. The drafting agent '
    'listed which advance files exist for these keys and did not read any verdict.')


def sha(p: Path) -> str | None:
    return g34.sha(p)


def journal(doi: str | None) -> str:
    m = re.match(r'10\.1038/(s\d+)-', g34.bare(doi))
    return JOURNAL.get(m.group(1), m.group(1)) if m else g31.journal(g34.bare(doi))


def plan_path(args) -> Path:
    return Path(args.plan).resolve() if getattr(args, 'plan', None) else PLAN


@functools.lru_cache(maxsize=None)
def units(key: str) -> tuple:
    return tuple(g27n.nature_units(key))


@functools.lru_cache(maxsize=None)
def parse(key: str) -> dict:
    return g27n.parse_result(key, list(units(key))) if g27n.is_nature(key) else {'clean': False, 'problem': 'no peer review file'}


def set_of(name: str) -> dict:
    return next(S for S in SETS if S['name'] == name)


# ------------------------------------------------------------------------------------------------ sample and guard
def manifest_rows(S: dict) -> list[dict]:
    f = DATA / S['manifest']
    return [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.is_file() else []


def sample() -> dict:
    """{'sets': {name: [keys]}, 'excluded': {key: reason}, 'doi': {key: doi}}: eligible Nature Portfolio rows with a peer
    review file, pilot papers excluded; nature22 in g32's draw_order."""
    pk = g34.pilot_keys()
    pre = {f"g22_{r['id']}": r['draw_order'] for r in read_json(g34.COP22_PRESELECT)} if g34.COP22_PRESELECT.is_file() else {}
    out, excl, dois = {}, {}, {}
    for S in SETS:
        keys = []
        for r in manifest_rows(S):
            k, doi = r['key'], g34.bare(r.get('doi'))
            if not doi.startswith('10.1038/'):
                continue
            dois[k] = doi
            if not g27n.is_nature(k):
                excl[k] = f"{S['name']}: no peer review file in review/{k}/ ({journal(doi)})"
            elif k in pk:
                excl[k] = f"{S['name']}: advance pilot paper (its advance codings were read in the pilots)"
            else:
                keys.append(k)
        if S['name'] == 'nature22':
            keys.sort(key=lambda k: pre.get(k, 10 ** 9))
        out[S['name']] = keys
    return {'sets': out, 'excluded': excl, 'doi': dois}


def arm_keys(smp: dict, arm: str) -> list[str]:
    return [k for S in SETS if S['arm'] == arm for k in smp['sets'][S['name']]]


def advance_records(keys: set) -> list[dict]:
    """Every advance record of a key: files (api and open roots, _invalid, rescued), state.json advance batches and 'spent'
    attempts under an '-advance' tag (read only). {'key', 'tag', 'where'}; no coding content is read."""
    out = []
    dirs = sorted((g34.CODINGS / 'api').glob('*-advance')) + sorted((g34.CODINGS / 'open').glob('*advance*'))
    dirs += sorted((DERIVED / 'advance' / 'rescued').glob('*'))
    for d in dirs:
        for f in sorted(d.glob('g22_*')) + sorted((d / '_invalid').glob('g22_*')):
            k = f.name.split('.')[0]
            if k in keys:
                out.append({'key': k, 'tag': d.name, 'where': rel(f)})
        rj = d / 'run.json'
        if rj.is_file():
            out += [{'key': k, 'tag': d.name, 'where': rel(rj)} for k in json.loads(rj.read_text()).get('papers', {}) if k in keys]
    st = g34.state()
    for b in st.get('batches', []):
        if str(b.get('tag', '')).endswith('-advance'):
            out += [{'key': k, 'tag': b['tag'], 'where': f"state.json batch {b.get('id')}"} for k in b.get('keys', []) if k in keys]
    for tk in st.get('spent', {}):
        tag, _, k = tk.rpartition(':')
        if tag.endswith('-advance') and k in keys:
            out.append({'key': k, 'tag': tag, 'where': f'state.json spent {tk}'})
    uniq = {(r['key'], r['tag'], r['where']): r for r in out}
    return [uniq[x] for x in sorted(uniq)]


def review_records(keys: set) -> list[str]:
    """Every Nature-family review record of a key: files under REVIEW_TAG (api, open, _invalid), state.json batches under
    REVIEW_TAG or naming the key in nature_keys, 'spent' attempts under REVIEW_TAG or carrying nature_addendum."""
    out = []
    for root in ('api', 'open'):
        d = g34.CODINGS / root / REVIEW_TAG
        for f in sorted(d.glob('g22_*')) + sorted((d / '_invalid').glob('g22_*')):
            if f.name.split('.')[0] in keys:
                out.append(f"{f.name.split('.')[0]} ({rel(f)})")
    st = g34.state()
    for b in st.get('batches', []):
        out += [f"{k} (state.json batch {b.get('id')}, {b['tag']})" for k in b.get('keys', [])
                if k in keys and (b['tag'] == REVIEW_TAG or k in (b.get('nature_keys') or []))]
    for tk, att in st.get('spent', {}).items():
        tag, _, k = tk.rpartition(':')
        if k in keys and (tag == REVIEW_TAG or any(x.get('nature_addendum') for x in att)):
            out.append(f'{k} (state.json spent {tk})')
    return sorted(set(out))


def advance_attempts(keys: set, tags: set | None = None) -> list[tuple[str, str, str]]:
    """(key, tag, time) of every advance attempt of a key in state.json (batch submission or synchronous attempt)."""
    st, out = g34.state(), []
    for b in st['batches']:
        if str(b.get('tag', '')).endswith('-advance') and (tags is None or b['tag'] in tags):
            out += [(k, b['tag'], b['submitted']) for k in b.get('keys', []) if k in keys]
    for tk, att in st['spent'].items():
        tag, _, k = tk.rpartition(':')
        if tag.endswith('-advance') and k in keys and (tags is None or tag in tags):
            out += [(k, tag, x['at']) for x in att if x.get('batch') is None]
    return out


def posthoc_advance(smp: dict) -> dict:
    """{key: {'tag', 'file', 'sha256', 'invalid', 'attempts'}} for the post-hoc papers: which advance coding exists, by
    file hash only (no verdict read)."""
    out = {}
    for S in SETS:
        if S['arm'] != 'posthoc':
            continue
        for k in smp['sets'][S['name']]:
            f = g34.CODINGS / 'api' / S['advance_tag'] / f'{k}.json'
            out[k] = {'tag': S['advance_tag'], 'file': rel(f) if f.is_file() else None, 'sha256': sha(f),
                      'invalid': sorted(rel(x) for x in (f.parent / '_invalid').glob(f'{k}.*')),
                      'attempts': sorted(t for kk, _, t in advance_attempts({k}, {S['advance_tag']}))}
    return out


def inquiry_hashes(smp: dict) -> dict:
    """sha256 of the inquiry coding of every post-hoc paper (coded before this plan; fixed at freeze)."""
    return {k: sha(g34.folder(S, 'inquiry') / f'{k}.json') for S in SETS if S.get('inquiry_fixed_at_freeze')
            for k in smp['sets'][S['name']]}


# ------------------------------------------------------------------------------------------------ layers and features
def index_rows(S: dict) -> dict:
    f = DATA / S['index']
    return {r['key']: r for r in read_json(f)} if f.is_file() else {}


def valid_inquiry(S: dict, keys) -> dict:
    out, d = {}, g34.folder(S, 'inquiry')
    for k in keys:
        f = d / f'{k}.json'
        try:
            c = json.loads(f.read_text()) if f.is_file() else None
        except Exception:  # noqa: BLE001
            c = None
        if c is not None and not check_coding.validate(c):
            out[k] = c
    return out


def valid_review(S: dict, keys) -> dict:
    """{key: (coding, kept disclosures, dropped)} for review codings valid under the Nature-family variant."""
    out, d = {}, g34.folder(S, 'review')
    for k in keys:
        f = d / f'{k}.json'
        if not f.is_file():
            continue
        try:
            c = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            continue
        if c.get('review_addendum_version') != '1.0.0' or not ccn.is_nature_coding(c):
            continue
        texts = g34.cp().review_texts(k, store=False)
        if ccn.validate_nature(c, texts=texts, checks=DISCLOSURE_CHECKS):
            continue
        kept, dropped = ccn.kept_disclosures(c, texts)
        out[k] = (c, kept, dropped)
    return out


def a_words(key: str) -> int:
    doc = g34.cp().review_text_for(key, store=False) or ''
    return sum(len(t.split()) for u, t in ccn.units(doc).items() if u.startswith('A-'))


def collect(smp: dict, nat_order: list[str], prefix_kinds=('inquiry', 'review'), inquiry_sha: dict | None = None) -> dict:
    """{'papers': {key: record}, 'prefix': ...}: layers N0-N3 of every candidate, features when N0-N3 hold."""
    P, notes = {}, {}
    for S in SETS:
        if S['name'] == 'nature22':
            pre = g34.prefix_len(S, nat_order, prefix_kinds)
            cand = nat_order[:pre['prefix']]
            notes['nature22_prefix'] = pre
        else:
            cand = list(smp['sets'][S['name']])
        idx = index_rows(S)
        inq, rev = valid_inquiry(S, cand), valid_review(S, cand)
        for k in cand:
            r = idx.get(k) or {'key': k, 'doi': smp['doi'].get(k)}
            pr = parse(k)
            pr_i, pr_r = g34.provenance(S, 'inquiry', k), g34.provenance(S, 'review', k)
            why = []
            n1 = k in inq and inq[k].get('codebook_version') == '1.5.0'
            if n1 and S.get('inquiry_fixed_at_freeze') and inquiry_sha is not None and inquiry_sha.get(k) != sha(g34.folder(S, 'inquiry') / f'{k}.json'):
                why.append('inquiry coding not the one hashed at freeze')
            if n1 and not S.get('inquiry_fixed_at_freeze'):
                if pr_i['model'] != MODEL:
                    why.append(f"inquiry answered by {pr_i['model']}")
                if (pr_i['redraws'] or 0) > REDRAW_CAP:
                    why.append(f"inquiry re-drawn {pr_i['redraws']} times")
            n2 = k in rev and any(s.get('trigger') in g31.REVIEWERS for x in rev[k][0]['sequences']
                                  if x['kind'] == 'review' for s in x['steps'])
            if n2:
                if pr_r['model'] != MODEL:
                    why.append(f"review answered by {pr_r['model']}")
                if (pr_r['redraws'] or 0) > REDRAW_CAP:
                    why.append(f"review re-drawn {pr_r['redraws']} times")
                if pr_r['disclosure_checks'] != DISCLOSURE_CHECKS:
                    why.append(f"review request recorded disclosure_checks {pr_r['disclosure_checks']}")
            lay = {'N0_review_file': bool(pr['clean']), 'N1_reported': n1 and not any(w.startswith('inquiry') for w in why),
                   'N2_review': n2 and not any(w.startswith('review') for w in why)}
            now = g34.cp().review_inputs(k, store=False) if lay['N2_review'] else None
            lay['N3_disclosed'] = bool(lay['N2_review'] and pr_r['review_inputs'] and now == pr_r['review_inputs'])
            if lay['N2_review'] and not lay['N3_disclosed']:
                why.append('review inputs recorded at the request differ from the texts on disk')
            rec = {'key': k, 'set': S['name'], 'arm': S['arm'], 'journal': journal(r.get('doi')), 'doi': g34.bare(r.get('doi')),
                   'layers': lay, 'parse': {x: pr.get(x) for x in ('clean', 'rounds', 'R_units', 'E_units', 'A_units', 'A_units_with_own_text')},
                   'provenance': {'inquiry': pr_i, 'review': pr_r}, 'not_complete_because': why}
            if all(lay.values()):
                c, kept, dropped = rev[k]
                paths = {'inquiry': g34.folder(S, 'inquiry') / f'{k}.json', 'review': g34.folder(S, 'review') / f'{k}.json'}
                w = g31.paper(r, inq[k], c, {}, S['review_tag'], paths=paths, droot=g34.CODINGS / S['root'])
                f = g34.features_of(w, g34.as_items(kept), dropped)
                f['revision_share'] = None   # no layer 4: no discussion preprint
                f['response_words'] = a_words(k)
                rec['features'] = f
                rec['inputs_sha256'] = {**w['inputs_sha256'], 'review_inputs': now}
            rec['complete_N0_N3'] = all(lay.values())
            P[k] = rec
    return {'papers': P, 'notes': notes}


# ------------------------------------------------------------------------------------------------ expected n and power
def expected_n(smp: dict) -> dict:
    """Expected complete papers with an outcome per set. Post-hoc sets: parse and inquiry on disk, the advance file's
    presence (no verdict read), review valid at the E3 rate. nature22: parse on disk, then the measured rates."""
    r = {k: v[0] / v[1] for k, v in RATES.items()}
    out = {}
    for S in SETS:
        keys = smp['sets'][S['name']]
        clean = [k for k in keys if parse(k)['clean']]
        row = {'candidates': len(keys), 'parse_clean': len(clean),
               'by_journal': dict(Counter(journal(smp['doi'].get(k)) for k in keys))}
        if S['arm'] == 'posthoc':
            inq = valid_inquiry(S, clean)
            inq = [k for k in clean if k in inq and inq[k].get('codebook_version') == '1.5.0']
            adv = [k for k in inq if (g34.CODINGS / 'api' / S['advance_tag'] / f'{k}.json').is_file()]
            row.update(valid_inquiry_on_disk=len(inq), advance_file_on_disk=len(adv),
                       rule='parse clean x valid inquiry (on disk) x advance coding file (on disk; verdict not read) x review valid',
                       expected=round(len(adv) * r['review_valid'], 1))
        else:
            row.update(rule='parse clean x inquiry valid x review valid x advance valid',
                       expected=round(len(clean) * r['inquiry_valid'] * r['review_valid'] * r['advance_valid'], 1))
        out[S['name']] = row
    out['prospective'] = out['nature22']['expected']
    out['posthoc'] = round(sum(out[S['name']]['expected'] for S in SETS if S['arm'] == 'posthoc'), 1)
    out['both_arms'] = round(out['prospective'] + out['posthoc'], 1)
    out['rates'] = {k: {'value': round(v[0] / v[1], 3), 'k': v[0], 'n': v[1], 'source': v[2]} for k, v in RATES.items()}
    out['review_valid_note'] = 'borrowed from the Copernicus E3 review run (58 of 61); no Nature-family review coding exists yet'
    return out


def journal_mix(smp: dict, arms=('prospective', 'posthoc')) -> dict:
    return dict(Counter(journal(smp['doi'].get(k)) for a in arms for k in arm_keys(smp, a)))


def power(smp: dict, nsim: int = 300, nperm: int = 500) -> dict:
    """Power of g34's test rule (partial Spearman within journal strata, journals under MIN_STRATUM pooled, Freedman-Lane
    permutation; g34's synthetic generator) at the expected n of: the prospective arm, both arms, the Copernicus papers of
    the reconstruction plan (full-cop22 scenario), and the pooled sensitivity (Copernicus plus both arms)."""
    rng = np.random.default_rng(SEED)
    en = expected_n(smp)
    n_pro, n_both = int(round(en['prospective'])), int(round(en['both_arms']))
    base = g34.expected_n()['scenarios']['rounds_1_2_cop22_full']
    cmix = g34.journal_mix()
    samples = [('nature, prospective arm', g34._sizes({'nature': journal_mix(smp, ('prospective',))}, n_pro), nsim),
               ('nature, both arms', g34._sizes({'nature': journal_mix(smp)}, n_both), nsim),
               ('copernicus, reconstruction plan', g34._sizes(cmix, base), max(100, nsim // 3)),
               ('pooled: copernicus and both nature arms', g34._sizes({**cmix, 'nature': journal_mix(smp)}, base + n_both), max(100, nsim // 3))]
    rows = []
    for target in (0.2, 0.3):
        eff = g34.calibrate('latent', target, rng)
        for label, sizes, ns in samples:
            labs = [lab.split('|')[1] for lab, c in sizes for _ in range(c)]
            st = g34.strata_of(labs)
            ps = []
            for _ in range(ns):
                f, o, covs, s = g34._draw(rng, sizes, 'latent', eff)
                r = g34.partial_within(f, o, covs, st, '', nperm=nperm, nboot=0, rng=rng)
                ps.append(r['p'] if r and np.sign(r['rho_partial']) > 0 else 1.0)
            ps = np.array(ps)
            rows.append({'scenario': f'rho {target}, H1 (achieved)', 'sample': label, 'n': int(sum(c for _, c in sizes)),
                         'effect_parameter': round(eff, 3), 'strata': len(set(st)), 'sims': len(ps),
                         f'power_alpha_{Q}': round(float((ps < Q).mean()), 3),
                         f'power_alpha_{round(Q / len(HYPOTHESES), 4)}': round(float((ps < Q / len(HYPOTHESES)).mean()), 3)})
    return {'nsim': nsim, 'nperm': nperm, 'family_size': len(HYPOTHESES), 'alpha': [Q, round(Q / len(HYPOTHESES), 4)],
            'expected_n': {'prospective': n_pro, 'both_arms': n_both, 'copernicus': base}, 'rows': rows,
            'note': ('synthetic data, the generator of g34 power(): g27 round-1 H1 feature distribution, advance pilot 1 '
                     'achieved rate; strata = journal (journals under MIN_STRATUM pooled); rho is the population Spearman '
                     'of feature and outcome the latent effect is calibrated to; covariates independent of the feature')}


def power_figure(pw: dict, path: Path) -> None:
    """Power of the planned test at the expected n of each sample, one panel per alpha, bars for rho 0.2 and 0.3 (PNG
    with source footer)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    ink, bg = '#153742', '#f5f4f2'
    cols = {'rho 0.2, H1 (achieved)': '#0089a8', 'rho 0.3, H1 (achieved)': '#a3527f'}
    samples = list(dict.fromkeys(r['sample'] for r in pw['rows']))
    nof = {r['sample']: r['n'] for r in pw['rows']}
    simsof = {r['sample']: r['sims'] for r in pw['rows']}
    x = np.arange(len(samples))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), sharey=True, facecolor=bg)
    for ax, a in zip(axes, pw['alpha']):
        ax.set_facecolor(bg)
        for i, (lab, col) in enumerate(cols.items()):
            v = [next(r[f'power_alpha_{a}'] for r in pw['rows'] if r['scenario'] == lab and r['sample'] == s) for s in samples]
            bars = ax.bar(x + (i - 0.5) * 0.38, v, 0.36, color=col, label=lab.replace(', H1 (achieved)', ''))
            for bb, y in zip(bars, v):
                ax.annotate(f'{y:.2f}', (bb.get_x() + bb.get_width() / 2, y), xytext=(0, 2), textcoords='offset points',
                            ha='center', fontsize=7, color=ink)
        ax.axhline(0.8, color='#8a9aa0', lw=1, ls='--')
        ax.set_xticks(x)
        short = {'nature, prospective arm': 'Nature family\nprospective arm', 'nature, both arms': 'Nature family\nboth arms',
                 'copernicus, reconstruction plan': 'Copernicus\n(g34 plan)', 'pooled: copernicus and both nature arms': 'pooled\nCopernicus + Nature'}
        ax.set_xticklabels([f"{short.get(s, s)}\nn = {nof[s]}" for s in samples], fontsize=7, color=ink)
        ax.set_title(f'alpha {a}' + (' (BH, most hypotheses non-null)' if a == pw['alpha'][0] else ' (BH, H1 the only non-null)'),
                     fontsize=9, color=ink)
        ax.spines[['top', 'right']].set_visible(False)
        ax.tick_params(colors=ink, labelsize=7)
        ax.set_ylim(0, 1.08)
    axes[0].set_ylabel('power of H1 (achieved): share of simulated\nstudies with p < alpha and the predicted sign', fontsize=8, color=ink)
    axes[0].legend(frameon=False, fontsize=8, loc='upper left', title='population Spearman', title_fontsize=8)
    fig.text(0.01, 0.01, f"Source: tools/roadmap/g35_nature_family.py power ({commit()}, {TODAY}); synthetic data from the g34 generator (g27 "
             "round-1 feature distribution, advance pilot 1 achieved rate),\njournal strata, journals under 5 papers pooled; "
             f"{pw['nperm']} permutations per study; studies per bar: "
             + ', '.join(f'{simsof[s]} ({s.split(",")[0].split(":")[0]})' for s in samples)
             + '. n = expected complete papers with an outcome (plan expected_n).', fontsize=6.3, color='#555')
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(path, dpi=160, facecolor=bg)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ plan
def plan_body(smp: dict, with_power: bool) -> dict:
    doc = __doc__
    p = {'title': 'Nature-family papers of rounds 1 and 2 and the 2022 draw: layered reconstruction, descriptive and pooled',
         'direction': ('Marine Denolle (PI), October 28, 2026: every draw includes all journals equally; NC and CEE peer '
                       'review files in the review arm; every eligible round-1 and round-2 paper coded completely. '
                       'ERRATA.md: the cop22 NC and CEE papers get their own plan, frozen before any of their advance codings '
                       'exists, with an advance tag apart from the full run'),
         'drafted': 'Claude Code workflow agent (claude-opus-5-5), October 28, 2026; the PI freezes',
         'sample': {'rule': ('eligible rows (set manifest) with a 10.1038 DOI and a peer review file that g27_nature_units '
                             f'{g27n.VERSION} reads; advance pilot papers excluded'),
                    'sets': smp['sets'], 'excluded': smp['excluded'],
                    'by_journal': {S['name']: dict(Counter(journal(smp['doi'].get(k)) for k in smp['sets'][S['name']])) for S in SETS},
                    'order_nature22': 'g32 draw_order (derived/cop22/preselect.json)'},
         'arms': {'prospective': [S['name'] for S in SETS if S['arm'] == 'prospective'],
                  'posthoc': [S['name'] for S in SETS if S['arm'] == 'posthoc'], 'posthoc_statement': POSTHOC_STATEMENT},
         'sets': SETS, 'review_tag': REVIEW_TAG, 'model': MODEL, 'disclosure_checks': DISCLOSURE_CHECKS, 'redraw_cap': REDRAW_CAP,
         'reader': {'module': 'tools/roadmap/g27_nature_units.py', 'version': g27n.VERSION},
         'addendum': {'file': 'agents/coder/REVIEW_ADDENDUM_NATURE.md', 'review_source': 'nature_review_file',
                      'nature_addendum_version': '1.0.0', 'review_addendum_version': '1.0.0'},
         'complete': {k.strip(): re.sub(r'\s+', ' ', v).strip() for k, v in
                      re.findall(r'\n  (N\d [a-z\- ]+?)\s{2,}(.+?)(?=\n  N\d |\nFeatures)', doc, re.S)},
         'layers': {'1_reported': 'inquiry coding', '2_review_induced': 'review sequence of the review coding',
                    '3_disclosed': 'disclosures in A units (REVIEW_ADDENDUM_NATURE.md 1.0.0)',
                    '4_revised': 'not available: no discussion preprint; revision_share and H7 dropped'},
         'features': re.sub(r'\s+', ' ', 'Features (' + doc.split('Features (')[1].split('Outcomes  ')[0]).strip(),
         'outcomes': 'as preregistration/reconstruction.json (g34.outcomes); cnp and fwci from the set metrics.json',
         'analysis': {'descriptive': re.sub(r'\s+', ' ', doc.split('  D  ')[1].split('  P  ')[0]).strip(),
                      'pooled_sensitivity': re.sub(r'\s+', ' ', doc.split('  P  ')[1].split('  Power  ')[0]).strip(),
                      'confirmatory': 'none: these papers alone support no confirmatory claim'},
         'hypotheses_pooled': HYPOTHESES,
         'not_blind_posthoc': {'hypotheses': sorted(NOT_BLIND_POSTHOC), 'covariates': g34.COVARIATES,
                               'rule': ('left out of P1b, P2 and the post-hoc and both-arms estimates; the covariates '
                                        'stay in every model, labelled not blind for the post-hoc arm')},
         'covariates': g34.COVARIATES, 'q_threshold': Q, 'seed': SEED, 'nperm': NPERM,
         'nboot': NBOOT, 'min_stratum': MIN_STRATUM, 'expected_n': expected_n(smp),
         'reconstruction_plan_sha256': sha(g34.PLAN), 'g31_constants': {'dmatch': g31.DMATCH, 'loc': g31.LOC}}
    if with_power:
        p['power'] = power(smp)
    return p


def draft(args) -> None:
    pp = plan_path(args)
    if pp.is_file() and json.loads(pp.read_text()).get('status') == 'frozen':
        sys.exit(f'{pp} is frozen; draft does not overwrite it')
    smp = sample()
    plan = {'status': 'draft', 'frozen': None, **plan_body(smp, not args.no_power), 'nat_order': smp['sets']['nature22'],
            'md_sha256': sha(pp.with_suffix('.md'))}
    pp.parent.mkdir(parents=True, exist_ok=True)
    pp.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + '\n')
    if 'power' in plan:
        power_figure(plan['power'], pp.with_name(pp.stem + '_power.png'))
    en = plan['expected_n']
    log('g35_nature_family.py draft', 'Nature-family plan draft', sum(len(v) for v in smp['sets'].values()),
        f"expected n prospective {en['prospective']}, post-hoc {en['posthoc']}")
    print(f"{rel(pp)}: draft written; sample {({k: len(v) for k, v in smp['sets'].items()})}; expected complete with an "
          f"outcome: prospective {en['prospective']}, post-hoc {en['posthoc']}")


def freeze(args) -> None:
    pp = plan_path(args)
    if pp.is_file() and json.loads(pp.read_text()).get('status') == 'frozen':
        sys.exit(f'refusing to freeze: {pp} is already frozen')
    if os.environ.get('METASCIENCE_PRIVATE') and pp == PLAN:
        sys.exit('refusing to freeze: METASCIENCE_PRIVATE is set and the plan path is the public default')
    if check_coding.DISCLOSURE_CHECKS != DISCLOSURE_CHECKS:
        sys.exit(f'refusing to freeze: check_coding.DISCLOSURE_CHECKS is {check_coding.DISCLOSURE_CHECKS!r}, the plan says {DISCLOSURE_CHECKS!r}')
    synthetic = pp != PLAN
    if not synthetic:
        dirty = g34.git('status', '--porcelain', '--untracked-files=all', '--', *FROZEN, *RECORDED).stdout.decode().strip()
        if dirty:
            sys.exit('refusing to freeze: FROZEN or RECORDED files are uncommitted or untracked; commit them first:\n' + dirty)
    smp = sample()
    pro, post = set(arm_keys(smp, 'prospective')), set(arm_keys(smp, 'posthoc'))
    if not pro and not post:
        sys.exit('refusing to freeze: the sample is empty')
    tag_of = {k: S['advance_tag'] for S in SETS for k in smp['sets'][S['name']]}
    recs = advance_records(pro | post)
    bad = [r for r in recs if r['key'] in pro] + [r for r in recs if r['key'] in post and r['tag'] != tag_of[r['key']]]
    if bad:
        sys.exit(f'refusing to freeze: {len(bad)} advance record(s) of sample papers outside the post-hoc full-run tag: '
                 + '; '.join(f"{r['key']} ({r['tag']}: {r['where']})" for r in bad[:10]))
    rv = review_records(post)
    if rv:
        sys.exit(f'refusing to freeze: {len(rv)} Nature-family review record(s) of post-hoc papers exist (their features would '
                 'be known before the freeze): ' + '; '.join(rv[:10]))
    md = pp.with_suffix('.md')
    if not md.is_file():
        sys.exit(f'refusing to freeze: no plan text at {md}')
    body = plan_body(smp, not args.no_power)
    head = g34.git('rev-parse', 'HEAD').stdout.decode().strip()
    md_text = re.sub(r'^Status: .*$', f'Status: frozen {TODAY} with `tools/roadmap/g35_nature_family.py freeze` (code commit '
                     f'{head[:7]}); machine-readable plan `{pp.name}`.', md.read_text(), count=1, flags=re.M)
    keys = sorted(pro | post)
    plan = {'status': 'frozen', 'frozen': TODAY, 'frozen_at': dt.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'code_commit': head, 'private_root': PRIVATE_ROOT, 'synthetic': synthetic, **body, 'nat_order': smp['sets']['nature22'],
            'parse_at_freeze': {k: {x: parse(k)[x] for x in ('clean', 'rounds', 'R_units', 'E_units', 'A_units', 'A_units_with_own_text')}
                                for k in keys},
            'review_files_sha256': {k: g27n.source_hashes(k) for k in keys},
            'inquiry_sha256_at_freeze': inquiry_hashes(smp), 'posthoc_advance_at_freeze': posthoc_advance(smp),
            'prospective_advance_records_at_freeze': 0, 'posthoc_review_records_at_freeze': 0,
            'manifests_sha256': {S['manifest']: sha(DATA / S['manifest']) for S in SETS},
            'indexes_sha256': {S['index']: sha(DATA / S['index']) for S in SETS}, 'preselect_sha256': sha(g34.COP22_PRESELECT),
            'inputs_sha256': {f: sha(ROOT / f) for f in FROZEN + RECORDED}, 'frozen_files': FROZEN, 'recorded_files': RECORDED,
            'md_sha256': hashlib.sha256(md_text.encode()).hexdigest()}
    md.write_text(md_text)
    pp.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + '\n')
    if 'power' in plan:
        power_figure(plan['power'], pp.with_name(pp.stem + '_power.png'))
    log('g35_nature_family.py freeze', 'Nature-family plan frozen', len(keys), f'plan sha256 {sha(pp)[:12]}; code commit {head[:7]}')
    print(f'{rel(pp)}: frozen, sha256 {sha(pp)}; commit {md.name}, {pp.name} and {pp.stem}_power.png together and push before any '
          f'review coding under {REVIEW_TAG} of a post-hoc paper and any advance coding under nature22-advance')


def features(args) -> None:
    pp = plan_path(args)
    plan = json.loads(pp.read_text()) if pp.is_file() else {}
    smp = sample()
    res = collect(smp, plan.get('nat_order') or smp['sets']['nature22'], inquiry_sha=plan.get('inquiry_sha256_at_freeze'))
    P = res['papers']
    by = lambda pred: {l: sum(r['layers'][l] for r in P.values() if pred(r)) for l in ('N0_review_file', 'N1_reported', 'N2_review', 'N3_disclosed')}
    summary = {'candidates': {S['name']: sum(r['set'] == S['name'] for r in P.values()) for S in SETS}, 'notes': res['notes'],
               'layers': {S['name']: by(lambda r, n=S['name']: r['set'] == n) for S in SETS},
               'complete_N0_N3': {S['name']: sum(r['complete_N0_N3'] for r in P.values() if r['set'] == S['name']) for S in SETS},
               'not_complete_because': dict(Counter(w for r in P.values() for w in r['not_complete_because'])),
               'features': {f: g31.dist([r['features'][f] for r in P.values() if 'features' in r]) for f in FEATURES}}
    write_json(OUT / 'features.json', {'summary': summary, 'papers': P}, [rel(pp)] + [rel(g34.folder(S, t)) for S in SETS for t in ('inquiry', 'review')]
               + [rel(g34.STATE) + ' (read only)'], {'sets': SETS})
    log('g35_nature_family.py features', 'Nature-family layers and features (no outcome read)', len(P), json.dumps(summary['complete_N0_N3']))
    print(json.dumps(summary, indent=1))


# ------------------------------------------------------------------------------------------------ test
def freeze_commit(pp: Path, plan: dict, accept: bool) -> tuple[dict, list[str]]:
    r = g34.git('log', '-n1', '--format=%H %cI', '--', PLAN_REL).stdout.decode().split()
    if len(r) != 2:
        sys.exit(f'refusing to test: {PLAN_REL} has no commit')
    h, when = r
    at = lambda f: g34.git('show', f'{h}:{f}')
    committed = at(PLAN_REL)
    if committed.returncode or committed.stdout != pp.read_bytes():
        sys.exit(f'refusing to test: {PLAN_REL} differs from its version in commit {h[:7]}')
    if json.loads(committed.stdout).get('status') != 'frozen':
        sys.exit(f'refusing to test: the plan in commit {h[:7]} is not frozen')
    if not g34.git('branch', '-r', '--contains', h).stdout.decode().strip():
        sys.exit(f'refusing to test: the freeze commit {h[:7]} is on no remote branch (push it first)')
    if g34.git('merge-base', '--is-ancestor', plan['code_commit'], h).returncode:
        sys.exit(f"refusing to test: the plan's code commit {plan['code_commit'][:7]} is not an ancestor of {h[:7]}")
    changed = [f for f in plan['frozen_files'] if (x := at(f)).returncode or x.stdout != (ROOT / f).read_bytes()]
    if changed and not accept:
        sys.exit(f'refusing to test: changed since the freeze commit {h[:7]}: {changed} (--accept-deviation records them)')
    return {'mode': 'git', 'freeze_commit': h, 'freeze_commit_time': when,
            'cutoff_local': g34.local_minute(when).strftime('%Y-%m-%d %H:%M')}, changed


def estimates(keys, F, O, J, name) -> list[dict]:
    """Partial Spearman within journal strata, point estimate and bootstrap interval only (no p, no verdict). The post-hoc
    and both-arms estimates leave out NOT_BLIND_POSTHOC."""
    rows = []
    for h in (HYPOTHESES if name == 'prospective' else HYPOTHESES_WITH_POSTHOC):
        ks = [k for k in keys if O[k].get(h['outcome']) is not None and F[k].get(h['feature']) is not None]
        f, o = [F[k][h['feature']] for k in ks], [O[k][h['outcome']] for k in ks]
        cv = [[F[k][c] for k in ks] for c in g34.COVARIATES if c != h['feature']]
        r = None
        if len(ks) >= 4 and len(set(o)) > 1 and len(set(f)) > 1:
            r = g34.partial_within(f, o, cv, g34.strata_of([J[k] for k in ks]), f'nature|{name}|{h["id"]}', nperm=1)
        rows.append({'id': h['id'], 'feature': h['feature'], 'outcome': h['outcome'], 'n': len(ks),
                     'feature_nonzero': int(sum(x > 0 for x in f)), 'rho_partial': r and r['rho_partial'], 'ci': r and r['ci'],
                     'note': 'descriptive estimate; no test'})
    return rows


def describe(keys, F, O, J, name) -> dict:
    return {'papers': len(keys), 'by_journal': dict(Counter(J[k] for k in keys)),
            'features': {f: g31.dist([F[k][f] for k in keys]) for f in FEATURES},
            'features_by_journal': {j: {f: g31.dist([F[k][f] for k in keys if J[k] == j]) for f in FEATURES} for j in sorted({J[k] for k in keys})},
            'verdicts': dict(Counter(O[k]['verdict'] for k in keys)),
            'achieved': g31.dist([O[k]['achieved'] for k in keys]), 'score': g31.dist([O[k]['score'] for k in keys]),
            'estimates_within_journal': estimates(keys, F, O, J, name)}


def pooled(nat: dict, accept: bool) -> dict:
    """The pooled sensitivity: g34's complete Copernicus papers (its own checks) with the complete Nature-family papers.
    nat: {key: (outcomes, features, journal, set, arm)}."""
    if not g34.PLAN.is_file() or json.loads(g34.PLAN.read_text()).get('status') != 'frozen':
        return {'status': 'not run: the reconstruction plan is not frozen'}
    p34 = json.loads(g34.PLAN.read_text())
    try:
        fz34, _ = g34.freeze_commit(g34.PLAN, p34, accept)
    except SystemExit as e:
        return {'status': f'not run: the reconstruction plan checks refused ({e})'}
    adv_tag = json.loads(g34.ADV_PLAN.read_text()).get('full_run_tag') if g34.ADV_PLAN.is_file() else None
    res = g34.collect(p34['sets'], p34['cop22_order'], prefix_kinds=('inquiry', 'review', 'advance'),
                      inquiry_sha=p34.get('inquiry_sha256_at_freeze'))
    tags = {s['name']: (adv_tag if s['advance_tag'] == 'plan' else s['advance_tag']) for s in p34['sets']}
    adv = {t: g34.load_advance(t) for t in set(tags.values()) if t}
    used = [(k, tags[r['set']]) for k, r in res['papers'].items() if r['complete_C0_C4'] and k in adv.get(tags[r['set']], {})]
    early = g34.advance_after_freeze(tags, used, fz34['cutoff_local'])
    if early:
        return {'status': f'not run: {len(early)} Copernicus advance attempts not later than the reconstruction freeze'}
    F, O, J, setn, arm = {}, {}, {}, {}, {}
    for k, t in used:
        o = g34.outcomes(adv[t][k])
        if o['screen_fail']:
            continue
        r = res['papers'][k]
        O[k], F[k], J[k], setn[k], arm[k] = o, dict(r['features']), r['journal'], r['set'], 'copernicus'
    for k, (o, f, j, s, a) in nat.items():
        O[k], F[k], J[k], setn[k], arm[k] = o, f, j, s, a
    without_post = sorted(k for k in O if arm[k] != 'posthoc')
    every = sorted(O)
    p1 = g34.run_family(HYPOTHESES, without_post, F, O, J, setn, 'nature-pooled-P1', strata_mode='journal')
    p1b = g34.run_family(HYPOTHESES_WITH_POSTHOC, every, F, O, J, setn, 'nature-pooled-P1b', strata_mode='journal')
    p2 = g34.run_family(HYPOTHESES_WITH_POSTHOC, every, F, O, J, setn, 'nature-pooled-P2')
    return {'status': 'run', 'papers_P1': len(without_post), 'papers_P1b_P2': len(every), 'by_arm': dict(Counter(arm.values())),
            'P1_strata_journal_prospective': p1, 'P1b_strata_journal_with_posthoc': p1b, 'P2_strata_journal_x_set': p2,
            'answer_P1': {**g34.answer(p1, []), 'label': 'pooled sensitivity; does not change the reconstruction answer'},
            'reconstruction_freeze': fz34}


def test(args) -> None:
    pp = plan_path(args)
    if getattr(args, 'plan', None) and not os.environ.get('METASCIENCE_PRIVATE'):
        sys.exit('refusing to test: --plan is for synthetic trees only (set METASCIENCE_PRIVATE)')
    if not pp.is_file() or json.loads(pp.read_text()).get('status') != 'frozen':
        sys.exit(f'refusing to test: no frozen plan at {pp}')
    plan = json.loads(pp.read_text())
    if pp == PLAN:
        fz, changed = freeze_commit(pp, plan, args.accept_deviation)
    else:
        changed = [f for f in plan['frozen_files'] if sha(ROOT / f) != plan['inputs_sha256'][f]]
        if changed and not args.accept_deviation:
            sys.exit(f'refusing to test: changed since the freeze: {changed} (--accept-deviation records them)')
        fz = {'mode': 'synthetic (METASCIENCE_PRIVATE and --plan; no git checks)', 'cutoff_local': plan['frozen_at']}
    smp = {'sets': plan['sample']['sets'], 'doi': sample()['doi']}
    pro = set(arm_keys(smp, 'prospective'))
    early = sorted({f'{k} under {t} at {when}' for k, t, when in advance_attempts(pro) if when <= fz['cutoff_local']})
    if early:
        sys.exit(f'refusing to test: {len(early)} advance attempt(s) of prospective papers are not later than the freeze '
                 f"({fz['cutoff_local']}): " + '; '.join(early[:10]))
    ph = plan['posthoc_advance_at_freeze']
    moved = sorted(k for k, v in ph.items() if sha(g34.CODINGS / 'api' / v['tag'] / f'{k}.json') != v['sha256'])
    if moved and not args.accept_deviation:
        sys.exit(f'refusing to test: the advance coding of {len(moved)} post-hoc paper(s) differs from the file hashed at '
                 f'freeze: {moved} (--accept-deviation records them and leaves them out)')
    res = collect(smp, plan['nat_order'], prefix_kinds=('inquiry', 'review', 'advance'), inquiry_sha=plan.get('inquiry_sha256_at_freeze'))
    P = res['papers']
    adv = {t: g34.load_advance(t) for t in {S['advance_tag'] for S in SETS}}
    met = {}
    for S in SETS:
        f = DERIVED / S['metrics'] / 'metrics.json'
        met.update({'g22_' + m['id']: m for m in (read_json(f) if f.is_file() else [])})
    O, F, J, setn, arm, u4 = {}, {}, {}, {}, {}, []
    for k, r in P.items():
        S = set_of(r['set'])
        c = None if k in moved else adv[S['advance_tag']].get(k)
        r['layers']['N5_outcome'] = c is not None
        if not r['complete_N0_N3'] or c is None:
            continue
        o = g34.outcomes(c)
        if o['screen_fail']:
            u4.append(k)
            continue
        o.update({x: met.get(k, {}).get(x) for x in ('cnp', 'fwci')})
        O[k], F[k], J[k], setn[k], arm[k] = o, r['features'], r['journal'], r['set'], r['arm']
    keys = sorted(O)
    kp = [k for k in keys if arm[k] == 'prospective']
    kh = [k for k in keys if arm[k] == 'posthoc']
    desc = {'prospective': describe(kp, F, O, J, 'prospective'), 'posthoc': describe(kh, F, O, J, 'posthoc'),
            'both_arms': describe(keys, F, O, J, 'both')}
    pool = pooled({k: (O[k], F[k], J[k], setn[k], arm[k]) for k in keys}, args.accept_deviation)
    out = {'plan_sha256': sha(pp), 'freeze': fz, 'deviations': changed, 'posthoc_advance_changed': moved, 'papers': len(keys),
           'by_arm': {'prospective': len(kp), 'posthoc': len(kh)}, 'U4_excluded': len(u4), 'candidates': len(P),
           'complete_N0_N3': sum(r['complete_N0_N3'] for r in P.values()), 'descriptive': desc, 'pooled_sensitivity': pool,
           'posthoc_statement': POSTHOC_STATEMENT, 'notes': res['notes'],
           'not_complete_because': dict(Counter(w for r in P.values() for w in r['not_complete_because']))}
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / 'results.json', out, [rel(pp), rel(g34.STATE) + ' (read only)'] + [rel(g34.folder(S, 'advance')) for S in SETS])
    md = ['# Nature-family papers (g35)', '',
          f"Plan `{pp.name}` (sha256 `{out['plan_sha256'][:12]}`), frozen {plan['frozen']} ({fz['mode']}). Complete papers with an "
          f"outcome: prospective {len(kp)}, post-hoc {len(kh)} ({POSTHOC_STATEMENT}); U4 excluded {len(u4)}. Descriptive only; "
          f"pooled sensitivity: {pool.get('status')}." + (f' Deviations: {changed}.' if changed else '')
          + (f' Post-hoc advance files changed since freeze, left out: {moved}.' if moved else ''), '']
    for a in ('prospective', 'posthoc', 'both_arms'):
        md += [f'## {a}', '', '| id | feature | outcome | n | rho partial (within journal) | 95% CI |', '|:--|:--|:--|--:|--:|:--|']
        md += [f"| {r['id']} | {r['feature']} | {r['outcome']} | {r['n']} | {r['rho_partial']} | {r['ci']} |" for r in desc[a]['estimates_within_journal']]
        md.append('')
    if pool.get('status') == 'run':
        md += [f"Pooled sensitivity P1 (journal strata, prospective arm with Copernicus, {pool['papers_P1']} papers): "
               f"{pool['answer_P1']['answer']}."]
        md += [f"- {r['id']}: rho {r['rho_partial']}, q {r['q']}, {r['verdict']}" for r in pool['P1_strata_journal_prospective']]
    (OUT / 'NATURE_FAMILY_TEST.md').write_text('\n'.join(md) + '\n')
    log('g35_nature_family.py test', 'Nature-family plan run (descriptive and pooled sensitivity)', len(keys), str(pool.get('status')))
    print('\n'.join(md))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['draft', 'freeze', 'features', 'power', 'test'])
    ap.add_argument('--plan', default=None)
    ap.add_argument('--no-power', action='store_true')
    ap.add_argument('--accept-deviation', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'power':
        pw = power(sample())
        print(json.dumps(pw, indent=1))
        log('g35_nature_family.py power', 'power at the expected n (synthetic data only)', len(pw['rows']),
            json.dumps({r['sample'] + '|' + r['scenario']: r[f'power_alpha_{Q}'] for r in pw['rows']}))
    else:
        {'draft': draft, 'freeze': freeze, 'features': features, 'test': test}[a.cmd](a)
