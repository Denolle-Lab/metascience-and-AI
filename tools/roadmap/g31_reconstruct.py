"""Phase 3a: the layered (merged) walk of each Copernicus paper's workflow, and its loops per layer. Descriptive only.

Direction from the PI (October 28, 2026): papers give the paper's account of the work, not its chronology, and they
leave out loops. Part of what they leave out is recoverable from the open review record: referee comments, author
responses, and the submitted manuscript next to the published one. This script stacks four layers on the final-paper
inquiry walk and counts loops in each. It makes no model call and joins no outcome: no advance coding is read, and
cnp, fwci, novelty and breadth are not joined (any association with outcome waits for a plan frozen before outcome
data are examined, the g23 pattern).

Paper set  The round-1 Copernicus papers with an open discussion: derived/review/open_review_index.json rows with
           'comments' (61). The review layer exists for the 58 whose E3 review coding (tag calc1-review) passes
           tools/check_coding.py validate(); the other three get the other layers only. The two advance pilot papers
           (PILOT_SEEN) are flagged excluded_from_confirmatory wherever they occur.

Layers (provenance tags on the steps of the merged walk; a step may carry several)
  reported                  every step of the final_paper sequence of the paper's inquiry coding (tag calc1, valid
                            codings; codebook agents/coder/CODEBOOK.md 1.5.0). This is the base walk, in the paper's
                            order. Fields are copied, not re-coded.
  review_induced            (a) every review-sequence step of the calc1-review coding whose trigger is referee,
                            editor or commenter (as g16 and g29 read them) becomes a step of the post-submission block,
                            with its node, mode, move and the E4 visibility label of that step (g16 visibility labels,
                            derived/review/visibility_labels.json, matched by step index i). (b) A reported step is also
                            tagged review_induced when the E4 published-text quote of a review change lands on it
                            (LANDING below); the review step then records lands_on = that step's n.
  revised_after_submission  a reported step whose quote is located in the published text (coverage >= LOC) and is
                            absent from the discussion preprint (coverage < CHANGED). Coverage and the text versions are
                            g26's (g26_translation.py: versions(), parse_xml/parse_pdf, label(), all_rows(), tokens()):
                            share of the quote's tokens matched by difflib blocks of >= 2 tokens within the best
                            window of three consecutive sentences. submitted_status per step: same (>= LOC), changed
                            (CHANGED to LOC), absent (< CHANGED), unlocated (not located in the published text, or
                            fewer than MIN_TOK tokens: such steps get no revision verdict).
  disclosed                 author-response disclosures. Source now: g27 labels (derived/translation/labels/<key>.json,
                            one Claude Code agent, source flag 'g27_agent_labels'). Later: the disclosures block of a
                            review-task coding (--disclosures-tag <tag>: private/analysis/codings/api/<tag>/<key>.json,
                            field 'disclosures' of the review addendum v1.0.0, agents/coder/review_addendum.schema.json:
                            g27's item fields with final_paper_status for final, plus node; source flag 'coding:<tag>'). tried_dropped items become steps (kind 'tried_dropped'); order_of_work
                            items become reordering annotations. Node: the item's own 'node' when the source gives one;
                            else the node of the review step it matches (DISCLOSURE MATCH), node_source
                            'review_step_match'; else none. A matched review step is tagged disclosed as well; a
                            reported step that the item's final_quote lands on (LANDING) is tagged disclosed.

Matching rules (fixed in code; constants below)
  LANDING            two quotes locate in the published text (coverage >= LOC each) at sentence-window centres at most
                     LAND_DIST sentences apart.
  DISCLOSURE MATCH   the disclosure's unit document (AC1, AR2: the unit locator up to the first space or '-S') is among
                     the documents cited in the review step's page field, and the larger of the two directed
                     coverages between the disclosure quote and the review step quote is >= DMATCH. Best match wins.
                     The E3 review coder saw the open discussion (AC, RC, CC, EC), not the AR files, so AR disclosures
                     cannot match.

Orders
  paper_order          the reported steps in the paper's order, with each placed tried_dropped step inserted just
                       before the reported step its final_quote lands on.
  reconstructed_order  pre-submission block: reported steps whose submitted_status is not absent, in paper order, with
                       placed tried_dropped items as above; then the post-submission block: review-induced steps in the
                       review coding's order (each tried_dropped item matched to a review step follows it), then
                       reported steps absent from the preprint that no review change lands on (revised after
                       submission, cause unattributed); unplaced tried_dropped items last. order_of_work annotations
                       are listed, not placed: g27 gives them as text, without a position in the walk.

Loop measures per paper (the units are steps or items; every count is per paper)
  paper_returns             reported steps with move return_after_failure (the paper says an earlier attempt failed,
                            mismatched or was revised and the work went back to it).
  paper_revisits            reported steps whose node occurs at an earlier reported step (g17 'revisits').
  paper_returns_added_after_submission   paper_returns whose submitted_status is absent: the loop entered the paper's
                            account only in revision.
  review_loops              review-induced steps with move other than declined: work reopened after submission because
                            a referee, editor or commenter asked. Read from the review coding alone (a defined prompt,
                            schema and validator, so rerunnable with an open-weight model).
  review_loops_to_paper_node  review_loops whose node occurs in the reported walk (a return to a stage the paper shows).
  review_loops_non_K        review_loops on any node but K (keep the claim): sensitivity that drops claim rewording.
  review_loops_absent       review_loops whose E4 label is absent or no_change (the reopening leaves nothing in the
                            published paper: E4 found no trace, or found that the paper did not change; the second
                            happens when the work asked for was done and dropped, e.g. a test whose result is given only
                            in the response).
  review_loops_hidden       review_loops whose E4 label is not as_revision (not readable as a revision).
  disclosed_tried_dropped   tried_dropped disclosures.
  tried_dropped_only_in_responses   tried_dropped disclosures with final 'absent' (the final paper does not state the
                            attempt); '_or_partly' adds final 'partly'.
  total_loops               paper_returns + review_loops + disclosed_tried_dropped, minus double counts: a
                            tried_dropped item matched to a review loop is counted once (as the review loop); one whose
                            final_quote lands on a reported return_after_failure step is counted once (as the return).
  outside_only_loops        loops visible only outside the paper: review loops with E4 label absent or no_change, plus
                            unmatched tried_dropped items with final absent; a review loop with matched tried_dropped
                            items counts only when every layer that judged it says so (E4 absent or no_change, and
                            every matched g27 final check absent).
  outside_only_share        outside_only_loops / total_loops (papers with total_loops > 0).
  hidden_loops, hidden_share  the broad version: review loops not labelled as_revision (or with a matched item whose
                            final check is not 'present') plus unmatched tried_dropped items with final not 'present',
                            over total_loops. A loop shown as if planned is hidden as a loop though its content
                            is in the paper.
  The review-dependent measures (review_*, total, outside, hidden) are reported only for papers with a valid review
  coding; disclosed and revised measures for every paper with the input.

Checks reported  location rates of reported-step quotes; landing and match rates; for review changes with an E4
           published quote, the share of those quotes absent from or changed in the preprint (a change made after
           submission should not be in the preprint: a consistency check of E3 and E4 against g26); paper_returns
           counted from the final_paper sequence of the calc1-review coding (same text, coder also saw the review) against
           calc1.

Summary    per measure: n papers, sum, mean, median, quartiles, range, papers with >= 1; outside_only_share and
           hidden_share as the mean of per-paper shares with a 95% percentile bootstrap over papers (NBOOT resamples,
           np.random.default_rng(SEED)) and as the pooled ratio of sums; the same by journal (DOI 10.5194/<abbr>-).

Inputs   derived/review/open_review_index.json; private/analysis/codings/api/calc1/<key>.json and calc1-review/<key>.json
         (read only); derived/review/visibility_labels.json (E4); derived/translation/labels/<key>.json (E13);
         review/<key>/<preprint stem>.pdf and pdfs/gold/<key>.xml.txt or .pdf (E12). sha256 of every file read per paper
         is stored with the paper's record.
Outputs  derived/reconstruct/merged_walks.json, RECONSTRUCT.md, fig_reconstruct.png; one MANIFEST.md line per run.
Run:     python tools/roadmap/g31_reconstruct.py [--disclosures-tag TAG] [KEY ...]   (keys: a dry subset, nothing written)
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from common import DERIVED, PRIVATE, TODAY, commit, log, read_json, rel, write_json
import rounds
import g26_translation as g26

API = PRIVATE / 'analysis' / 'codings' / 'api'
INDEX = DERIVED / 'review' / 'open_review_index.json'
VIS = DERIVED / 'review' / 'visibility_labels.json'
G27 = DERIVED / 'translation' / 'labels'
OUT = DERIVED / 'reconstruct'
PILOT_SEEN = {'g22_W4205292752', 'g22_W4223595027'}   # advance pilot papers whose advance codings have been read
REVIEWERS = {'referee', 'editor', 'commenter'}
NOT_IN_PAPER = ('absent', 'no_change')                # E4 labels under which a reopening leaves no trace in the paper
LOC, CHANGED = g26.GAP_SAME, g26.GAP_CHANGED          # 0.9 and 0.5, as g26 locates the gap statement
MIN_TOK = 4                                            # a quote with fewer tokens gets no location
LAND_DIST = 1
DMATCH = 0.5
NBOOT, SEED = 5000, 2026
JOURNALS = {'tc': 'The Cryosphere', 'nhess': 'Nat. Hazards Earth Syst. Sci.', 'hess': 'Hydrol. Earth Syst. Sci.',
            'acp': 'Atmos. Chem. Phys.', 'amt': 'Atmos. Meas. Tech.', 'bg': 'Biogeosciences', 'cp': 'Clim. Past',
            'esd': 'Earth Syst. Dynam.', 'essd': 'Earth Syst. Sci. Data', 'gmd': 'Geosci. Model Dev.', 'os': 'Ocean Sci.',
            'se': 'Solid Earth', 'wcd': 'Weather Clim. Dynam.', 'gchron': 'Geochronology', 'esurf': 'Earth Surf. Dynam.',
            'ejm': 'Eur. J. Mineral.', 'angeo': 'Ann. Geophys.', 'npg': 'Nonlin. Processes Geophys.',
            'gi': 'Geosci. Instrum. Method. Data Syst.', 'soil': 'SOIL', 'wes': 'Wind Energ. Sci.', 'adgeo': 'Adv. Geosci.',
            'tc-': 'The Cryosphere', 'hgss': 'Hist. Geo Space Sci.', 'gc': 'Geosci. Commun.', 'asr': 'Adv. Sci. Res.'}


def sha(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def journal(doi: str) -> str:
    m = re.match(r'10\.5194/([a-z]+)-', (doi or '').lower())
    return m.group(1) if m else 'other'


def place(quote: str, rows: list[dict]) -> tuple[float, int | None]:
    """g26.locate, returning the centre index of the best window instead of its section."""
    q = g26.tokens(quote or '')
    if len(q) < MIN_TOK or not rows:
        return 0.0, None
    qc = {t for t in q if t not in g26.STOP and len(t) > 2}
    cnt = Counter()
    for j, r in enumerate(rows):
        n = len(qc & r['content'])
        if n:
            cnt[j] = n
    best, bj = 0.0, None
    for j, _ in cnt.most_common(10):
        win = sum((rows[k]['tok'] for k in range(max(0, j - 1), min(len(rows), j + 2))), [])
        c = g26.coverage(q, win)
        if c > best:
            best, bj = c, j
    return round(best, 4), bj


def status(quote: str, pub: list[dict], sub: list[dict] | None) -> dict:
    cp, jp = place(quote, pub)
    if jp is None or cp < LOC:
        return {'submitted_status': 'unlocated', 'cov_published': cp, 'pub_row': None}
    if sub is None:
        return {'submitted_status': 'no_preprint', 'cov_published': cp, 'pub_row': jp}
    cs, _ = place(quote, sub)
    st = 'same' if cs >= LOC else ('changed' if cs >= CHANGED else 'absent')
    return {'submitted_status': st, 'cov_published': cp, 'cov_submitted': cs, 'pub_row': jp}


def docs(page: str) -> set[str]:
    return set(re.findall(r'\b((?:AC|AR|RC|CC|EC)\d+)', page or ''))


def qcov(a: str, b: str) -> float:
    ta, tb = g26.tokens(a or ''), g26.tokens(b or '')
    if len(ta) < MIN_TOK or len(tb) < MIN_TOK:
        return 0.0
    return round(max(g26.coverage(ta, tb), g26.coverage(tb, ta)), 4)


def texts(r: dict):
    """(published rows, submitted rows or None, version records) with g26's parsing."""
    sub_v, pub_v = g26.versions(r)
    pub = sub = None
    if pub_v['kind']:
        pf = g26.from_private(pub_v['file'])
        pub = g26.all_rows(g26.label(g26.parse_xml(pf) if pf.suffix == '.txt' else g26.parse_pdf(pf)))
    if sub_v['kind'] == 'discussion preprint':
        sub = g26.all_rows(g26.label(g26.parse_pdf(g26.from_private(sub_v['file']))))
    return pub or [], sub, sub_v, pub_v


def disclosures(key: str, tag: str | None, root: Path | None = None) -> tuple[list[dict], str | None, Path]:
    """(items, source flag, file). root: the codings folder holding <tag>/ (default private/analysis/codings/api; an
    open-weight run's codings are under private/analysis/codings/open)."""
    if tag:   # review addendum v1.0.0 (agents/coder/review_addendum.schema.json): final_paper_status, node 'none', '' for null
        f = (root or API) / tag / f'{key}.json'
        items = json.loads(f.read_text()).get('disclosures', []) if f.is_file() else []
        items = [{**d, 'final': d.get('final_paper_status', d.get('final')), 'final_quote': d.get('final_quote') or None,
                  'node': None if d.get('node') in (None, '', 'none') else d['node']} for d in items]
        return items, f'coding:{tag}', f
    f = G27 / f'{key}.json'
    return (json.loads(f.read_text())['disclosures'] if f.is_file() else []), 'g27_agent_labels', f


def paper(r: dict, c1: dict, rv: dict | None, vis: dict, dtag: str | None, paths: dict | None = None,
          droot: Path | None = None) -> dict:
    """The layered walk of one paper. paths: {name: coding file} hashed into inputs_sha256 (default: the calc1 and
    calc1-review files, as this script reads them); droot: the codings folder of the disclosure tag (disclosures())."""
    key = r['key']
    pub, sub, sub_v, pub_v = texts(r)
    files = dict(paths) if paths else {'calc1': API / 'calc1' / f'{key}.json', 'calc1_review': API / 'calc1-review' / f'{key}.json'}
    if sub_v.get('file'):
        files['submitted'] = g26.from_private(sub_v['file'])
    if pub_v.get('file'):
        files['published'] = g26.from_private(pub_v['file'])
    items, dsrc, dfile = disclosures(key, dtag, droot)
    files['disclosures'] = dfile
    rec = {'key': key, 'doi': r['doi'], 'journal': journal(r['doi']), 'excluded_from_confirmatory': key in PILOT_SEEN,
           'submitted': sub_v, 'published': pub_v, 'disclosure_source': dsrc,
           'layers': {'reported': True, 'review_induced': rv is not None, 'revised_after_submission': sub is not None,
                      'disclosed': dfile.is_file()},
           'inputs_sha256': {k: sha(p) for k, p in files.items() if p.is_file()}}

    # reported (base walk)
    steps = []
    seen = set()
    for s in next(x for x in c1['sequences'] if x['kind'] == 'final_paper')['steps']:
        st = status(s.get('quote'), pub, sub)
        steps.append({'id': f"P{s['n']}", 'layer': 'reported', 'n': s['n'], 'node': s['node'], 'mode': s['mode'],
                      'action': s['action'], 'page': s['page'], 'quote': s.get('quote'), 'move': s.get('move'),
                      'trigger': s.get('trigger'), 'revisit': s['node'] in seen, 'provenance': ['reported'], **st})
        seen.add(s['node'])
        if st['submitted_status'] == 'absent':
            steps[-1]['provenance'].append('revised_after_submission')
    paper_nodes = {s['node'] for s in steps}

    def lands(quote):
        cp, jp = place(quote, pub)
        if jp is None or cp < LOC:
            return None
        hits = [(abs(s['pub_row'] - jp), s) for s in steps if s['pub_row'] is not None and abs(s['pub_row'] - jp) <= LAND_DIST]
        return min(hits, key=lambda h: (h[0], h[1]['n']))[1] if hits else None

    # review-induced
    rsteps, e4_checks = [], []
    if rv is not None:
        rev = next((x for x in rv['sequences'] if x['kind'] == 'review'), {'steps': []})
        lab = vis.get(key, {})
        for i, s in enumerate(rev['steps'], 1):
            if s.get('trigger') not in REVIEWERS:
                continue
            L = lab.get(i, {})
            st = {'id': f'R{i}', 'layer': 'review_induced', 'i': i, 'node': s['node'], 'mode': s['mode'],
                  'action': s['action'], 'page': s['page'], 'quote': s.get('quote'), 'move': s.get('move'),
                  'trigger': s.get('trigger'), 'e4_label': L.get('label'), 'e4_quote': L.get('quote'),
                  'loop': s.get('move') != 'declined', 'to_paper_node': s['node'] in paper_nodes,
                  'provenance': ['review_induced'], 'lands_on': None}
            if L.get('label') in ('as_planned', 'as_revision') and L.get('quote'):
                hit = lands(L['quote'])
                if hit is not None:
                    st['lands_on'] = hit['n']
                    if 'review_induced' not in hit['provenance']:
                        hit['provenance'].append('review_induced')
                if st['loop']:
                    e4_checks.append(status(L['quote'], pub, sub)['submitted_status'])
            rsteps.append(st)

    # disclosed
    dsteps, reorder = [], []
    for k, d in enumerate(items, 1):
        if d.get('kind') not in ('tried_dropped', 'order_of_work'):
            continue
        best = None
        for s in rsteps:
            if d['unit'].split(' ')[0].split('-')[0] in docs(s['page']):
                v = qcov(d.get('quote'), s.get('quote'))
                if v >= DMATCH and (best is None or v > best[0]):
                    best = (v, s)
        node, nsrc = (d['node'], 'given') if d.get('node') else ((best[1]['node'], 'review_step_match') if best else (None, None))
        hit = lands(d.get('final_quote')) if d.get('final_quote') else None
        item = {'id': f'D{k}', 'layer': 'disclosed', 'kind': d['kind'], 'unit': d['unit'], 'quote': d.get('quote'),
                'content': d.get('content'), 'final': d.get('final'), 'final_loc': d.get('final_loc'),
                'node': node, 'node_source': nsrc, 'matched_review_step': best[1]['id'] if best else None,
                'match_cov': best[0] if best else None, 'lands_on': hit['n'] if hit else None,
                'provenance': ['disclosed'], 'source': dsrc}
        if best and 'disclosed' not in best[1]['provenance']:
            best[1]['provenance'].append('disclosed')
        if hit is not None and 'disclosed' not in hit['provenance']:
            hit['provenance'].append('disclosed')
        (dsteps if d['kind'] == 'tried_dropped' else reorder).append(item)

    # orders
    before = defaultdict(list)
    after_r = defaultdict(list)
    unplaced = []
    for d in dsteps:
        if d['matched_review_step']:
            after_r[d['matched_review_step']].append(d['id'])
        elif d['lands_on'] is not None:
            before[d['lands_on']].append(d['id'])
        else:
            unplaced.append(d['id'])
    paper_order = [x for s in steps for x in before[s['n']] + [s['id']]]
    landed = {s['lands_on'] for s in rsteps if s['lands_on'] is not None}
    pre = [x for s in steps if s['submitted_status'] != 'absent' for x in before[s['n']] + [s['id']]]
    post = [x for s in rsteps for x in [s['id']] + after_r[s['id']]]
    late = [x for s in steps if s['submitted_status'] == 'absent' and s['n'] not in landed for x in before[s['n']] + [s['id']]]
    rec['paper_order'] = paper_order + [d['id'] for d in dsteps if d['matched_review_step'] or d['lands_on'] is None]
    rec['reconstructed_order'] = {'pre_submission': pre, 'post_submission': post, 'revised_unattributed': late,
                                  'unplaced_disclosed': unplaced}
    rec['walk'] = steps + rsteps + dsteps
    rec['reorder_annotations'] = reorder

    # loop measures
    m = {'paper_steps': len(steps),
         'paper_returns': sum(s['move'] == 'return_after_failure' for s in steps),
         'paper_revisits': sum(s['revisit'] for s in steps),
         'paper_returns_added_after_submission': sum(s['move'] == 'return_after_failure' and s['submitted_status'] == 'absent' for s in steps),
         'paper_steps_located': sum(s['submitted_status'] not in ('unlocated',) for s in steps),
         'paper_steps_absent_in_preprint': sum(s['submitted_status'] == 'absent' for s in steps),
         'paper_steps_changed_in_preprint': sum(s['submitted_status'] == 'changed' for s in steps),
         'disclosed_tried_dropped': len(dsteps),
         'tried_dropped_only_in_responses': sum(d['final'] == 'absent' for d in dsteps),
         'tried_dropped_only_in_responses_or_partly': sum(d['final'] in ('absent', 'partly') for d in dsteps),
         'order_of_work': len(reorder)}
    if rv is not None:
        loops = [s for s in rsteps if s['loop']]
        byid = {s['id']: s for s in rsteps}
        returns = {s['n'] for s in steps if s['move'] == 'return_after_failure'}
        dup = out_d = hid_d = 0
        finals = defaultdict(list)   # review loop id -> g27 final checks of the tried_dropped items matched to it
        for d in dsteps:
            rs = byid.get(d['matched_review_step'])
            if rs is not None and rs['loop']:
                dup += 1
                finals[rs['id']].append(d['final'])
            elif d['lands_on'] in returns:
                dup += 1
            else:
                out_d += d['final'] == 'absent'
                hid_d += d['final'] != 'present'
        for s in loops:   # every layer that judged the loop: E4, and g27 for matched items
            s['outside_only'] = s['e4_label'] in NOT_IN_PAPER and all(f == 'absent' for f in finals[s['id']])
            s['hidden'] = s['e4_label'] != 'as_revision' or any(f != 'present' for f in finals[s['id']])
        m.update({'review_steps': len(rsteps), 'review_declined': sum(not s['loop'] for s in rsteps),
                  'review_loops': len(loops), 'review_loops_to_paper_node': sum(s['to_paper_node'] for s in loops),
                  'review_loops_non_K': sum(s['node'] != 'K' for s in loops),
                  'review_loops_return_after_failure': sum(s['move'] == 'return_after_failure' for s in loops),
                  'review_loops_absent': sum(s['e4_label'] in NOT_IN_PAPER for s in loops),
                  'review_loops_hidden': sum(s['e4_label'] != 'as_revision' for s in loops),
                  'review_loops_outside_only': sum(s['outside_only'] for s in loops),
                  'review_loops_hidden_any_layer': sum(s['hidden'] for s in loops),
                  'review_loops_landed': sum(s['lands_on'] is not None for s in loops),
                  'tried_dropped_matched_to_review': sum(d['matched_review_step'] is not None for d in dsteps),
                  'double_counted': dup})
        m['total_loops'] = m['paper_returns'] + m['review_loops'] + m['disclosed_tried_dropped'] - dup
        m['outside_only_loops'] = m['review_loops_outside_only'] + out_d
        m['hidden_loops'] = m['review_loops_hidden_any_layer'] + hid_d
        m['outside_only_share'] = round(m['outside_only_loops'] / m['total_loops'], 4) if m['total_loops'] else None
        m['hidden_share'] = round(m['hidden_loops'] / m['total_loops'], 4) if m['total_loops'] else None
        m['e4_quote_in_preprint'] = dict(Counter(e4_checks))
        fp = next(x for x in rv['sequences'] if x['kind'] == 'final_paper')['steps']
        m['paper_returns_in_review_coding'] = sum(s.get('move') == 'return_after_failure' for s in fp)
    rec['measures'] = m
    return rec


def dist(v) -> dict:
    v = np.asarray([x for x in v if x is not None], dtype=float)
    if not len(v):
        return {'n': 0}
    return {'n': int(len(v)), 'sum': float(v.sum()), 'mean': round(float(v.mean()), 2), 'median': float(np.median(v)),
            'q25': float(np.percentile(v, 25)), 'q75': float(np.percentile(v, 75)), 'min': float(v.min()),
            'max': float(v.max()), 'papers_ge1': int((v >= 1).sum())}


def share(recs, num, den, rng) -> dict:
    rr = [r['measures'] for r in recs if r['measures'].get(den)]
    if not rr:
        return {'n': 0}
    per = np.array([x[num] / x[den] for x in rr])
    idx = rng.integers(0, len(per), (NBOOT, len(per)))
    b = per[idx].mean(1)
    return {'n': len(per), 'mean': round(float(per.mean()), 4),
            'ci': [round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)],
            'pooled': round(sum(x[num] for x in rr) / sum(x[den] for x in rr), 4),
            'num': int(sum(x[num] for x in rr)), 'den': int(sum(x[den] for x in rr)),
            'papers_with_any': int(sum(x[num] > 0 for x in rr))}


MEASURES = ['paper_steps', 'paper_returns', 'paper_revisits', 'paper_returns_added_after_submission', 'review_loops',
            'review_loops_to_paper_node', 'review_loops_non_K', 'review_loops_absent', 'review_loops_hidden', 'review_loops_outside_only',
            'review_declined', 'disclosed_tried_dropped', 'tried_dropped_only_in_responses',
            'tried_dropped_only_in_responses_or_partly', 'order_of_work', 'total_loops', 'outside_only_loops', 'hidden_loops']


def summarize(recs) -> dict:
    rng = np.random.default_rng(SEED)
    rv = [r for r in recs if r['layers']['review_induced']]
    S = {'papers': len(recs), 'papers_review_layer': len(rv),
         'papers_preprint': sum(r['layers']['revised_after_submission'] for r in recs),
         'papers_disclosed': sum(r['layers']['disclosed'] for r in recs),
         'excluded_from_confirmatory_present': sorted(r['key'] for r in recs if r['excluded_from_confirmatory']),
         'measures': {k: dist([r['measures'].get(k) for r in recs]) for k in MEASURES},
         'outside_only_share': share(rv, 'outside_only_loops', 'total_loops', rng),
         'hidden_share': share(rv, 'hidden_loops', 'total_loops', rng)}
    steps = [s for r in recs for s in r['walk'] if s['layer'] == 'reported']
    S['reported_submitted_status'] = dict(Counter(s['submitted_status'] for s in steps))
    S['reported_provenance'] = dict(Counter('+'.join(s['provenance']) for s in steps))
    loops = [s for r in rv for s in r['walk'] if s['layer'] == 'review_induced' and s['loop']]
    S['review_loops_by_e4'] = dict(Counter(str(s['e4_label']) for s in loops))
    S['review_loops_by_node'] = dict(Counter(s['node'] for s in loops).most_common())
    S['review_loops_landed'] = [sum(s['lands_on'] is not None for s in loops),
                                sum(s['e4_label'] in ('as_planned', 'as_revision') and bool(s['e4_quote']) for s in loops)]
    e4 = Counter()
    for r in rv:
        e4.update(r['measures']['e4_quote_in_preprint'])
    S['e4_quote_in_preprint'] = dict(e4)
    td = [s for r in recs for s in r['walk'] if s['layer'] == 'disclosed']
    S['tried_dropped'] = {'n': len(td), 'final': dict(Counter(d['final'] for d in td)),
                          'matched_to_review_step': sum(d['matched_review_step'] is not None for d in td),
                          'with_node': sum(d['node'] is not None for d in td),
                          'landed_on_reported_step': sum(d['lands_on'] is not None for d in td),
                          'units': dict(Counter(re.match(r'[A-Z]+', d['unit']).group(0) for d in td))}
    S['order_of_work_units'] = dict(Counter(re.match(r'[A-Z]+', a['unit']).group(0) for r in recs for a in r['reorder_annotations']))
    S['returns_calc1_vs_review_coding'] = {'calc1': int(sum(r['measures']['paper_returns'] for r in rv)),
                                           'calc1_review_final_paper': int(sum(r['measures']['paper_returns_in_review_coding'] for r in rv)),
                                           'papers_equal': int(sum(r['measures']['paper_returns'] == r['measures']['paper_returns_in_review_coding'] for r in rv)),
                                           'n': len(rv)}
    byj = defaultdict(list)
    for r in recs:
        byj[r['journal']].append(r)
    S['by_journal'] = {}
    for j, rr in sorted(byj.items(), key=lambda x: -len(x[1])):
        rj = [r for r in rr if r['layers']['review_induced']]
        S['by_journal'][j] = {'papers': len(rr), 'papers_review_layer': len(rj),
                              **{k: dist([r['measures'].get(k) for r in (rj if k in ('review_loops', 'total_loops', 'outside_only_loops') else rr)])
                                 for k in ('paper_returns', 'review_loops', 'disclosed_tried_dropped', 'total_loops', 'outside_only_loops')},
                              'outside_only_share': share(rj, 'outside_only_loops', 'total_loops', rng),
                              'hidden_share': share(rj, 'hidden_loops', 'total_loops', rng)}
    return S


def figure(recs, S, path: Path, prov) -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    ink, teal, gold = '#153742', '#0f4c5c', '#d9a441'
    rv = [r for r in recs if r['layers']['review_induced']]
    rv.sort(key=lambda r: (r['measures']['total_loops'], r['measures']['review_loops']))
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={'width_ratios': [2.2, 1]})
    x = np.arange(len(rv))
    parts = [('paper_returns', 'in the paper (return after failure)', teal),
             ('review_loops', 'added by review', '#7fa7b0'),
             ('td_unique', 'tried and dropped, disclosed in responses', gold)]
    bottom = np.zeros(len(rv))
    for k, lab_, col in parts:
        v = np.array([(r['measures']['disclosed_tried_dropped'] - r['measures']['double_counted']) if k == 'td_unique'
                      else r['measures'][k] for r in rv], float)
        a.bar(x, v, bottom=bottom, color=col, width=0.8, label=lab_, edgecolor='white', linewidth=0.6)
        bottom += v
    oo = np.array([r['measures']['outside_only_loops'] for r in rv], float)
    a.scatter(x, oo, marker='_', s=60, color=ink, zorder=3, label='of which visible only outside the paper')
    a.set_xticks([])
    a.set_xlabel(f'papers ({len(rv)} with a valid review coding), sorted by total loops', fontsize=9, color=ink)
    a.set_ylabel('loops per paper (count)', fontsize=9, color=ink)
    a.legend(frameon=False, fontsize=8, loc='upper left')
    a.spines[['top', 'right']].set_visible(False)
    bj = [(j, v) for j, v in S['by_journal'].items() if v['outside_only_share'].get('n')]
    for i, (j, v) in enumerate(bj):
        o, h = v['outside_only_share'], v['hidden_share']
        b.barh(i, h['pooled'], color='#c9d9dd', height=0.7)
        b.barh(i, o['pooled'], color=teal, height=0.7)
        b.text(h['pooled'] + 0.02, i, f"{o['num']} / {h['num']} of {o['den']}, {o['n']} paper{'s' if o['n'] > 1 else ''}", va='center', fontsize=7, color=ink)
    b.set_yticks(range(len(bj)))
    b.set_yticklabels([j for j, _ in bj], fontsize=8)
    b.invert_yaxis()
    b.set_xlim(0, 1.45)
    b.set_xticks([0, 0.25, 0.5, 0.75, 1])
    b.set_xlabel('share of loops (pooled): dark = only outside the paper,\nlight = not shown as a loop in the paper', fontsize=8, color=ink)
    b.spines[['top', 'right']].set_visible(False)
    fig.text(0.01, 0.01, f"Source: g31_reconstruct.py ({prov['commit']}, {prov['date']}); round-1 Copernicus papers with open review; "
             "paper = calc1 coding, review = calc1-review coding (E3) with E4 visibility labels,\n"
             "disclosures = g27 single-agent labels (E13), preprint alignment = g26 (E12). Descriptive; no outcome joined.",
             fontsize=7, color='#555')
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def fmt(d, keys=('n', 'sum', 'mean', 'median', 'q25', 'q75', 'min', 'max', 'papers_ge1')):
    return ' | '.join(str(int(d[k]) if isinstance(d.get(k), float) and d[k].is_integer() else d.get(k, '')) for k in keys)


def report(recs, S, prov) -> str:
    def sh(x):
        return f"{x['mean']:.2f} [{x['ci'][0]:.2f}, {x['ci'][1]:.2f}] (pooled {x['num']} of {x['den']} = {x['pooled']:.2f}, {x['n']} papers)" if x.get('n') else 'n/a'
    md = [f"# Layered workflow reconstruction (g31), round-1 Copernicus papers", '',
          f"Generated {prov['date']} by `tools/roadmap/g31_reconstruct.py` at commit {prov['commit']}. Descriptive only: no advance "
          "coding read, no outcome joined. Definitions are in the script docstring; the short form is below.", '',
          '![loops per paper by layer](fig_reconstruct.png)', '',
          '## Papers and layers', '',
          f"- Papers: {S['papers']} with an open discussion; review layer (valid calc1-review coding) {S['papers_review_layer']}; "
          f"discussion preprint on disk {S['papers_preprint']}; disclosure labels {S['papers_disclosed']}.",
          f"- Advance pilot papers in this set (excluded from any confirmatory test): {', '.join(S['excluded_from_confirmatory_present']) or 'none'}.", '',
          '## Loop measures per paper', '',
          '| measure | papers | sum | mean | median | q25 | q75 | min | max | papers with >= 1 |', '|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|']
    for k in MEASURES:
        md.append(f"| {k} | {fmt(S['measures'][k])} |")
    md += ['', f"- Share of loops visible only outside the paper, mean of per-paper shares [95% bootstrap]: {sh(S['outside_only_share'])}.",
           f"- Share of loops not shown as a loop in the paper (broad): {sh(S['hidden_share'])}.", '',
           '## By journal', '',
           '| journal | papers | review layer | paper returns (sum) | review loops (sum) | tried and dropped (sum) | total loops (sum) | outside only (sum) | outside-only share, pooled | hidden share, pooled |',
           '|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|']
    for j, v in S['by_journal'].items():
        o, h = v['outside_only_share'], v['hidden_share']
        md.append(f"| {JOURNALS.get(j, j)} ({j}) | {v['papers']} | {v['papers_review_layer']} | {int(v['paper_returns'].get('sum', 0))} | "
                  f"{int(v['review_loops'].get('sum', 0))} | {int(v['disclosed_tried_dropped'].get('sum', 0))} | {int(v['total_loops'].get('sum', 0))} | "
                  f"{int(v['outside_only_loops'].get('sum', 0))} | {o.get('pooled', 'n/a')} | {h.get('pooled', 'n/a')} |")
    td = S['tried_dropped']
    md += ['', '## Checks', '',
           f"- Reported steps by preprint status: {S['reported_submitted_status']}.",
           f"- Reported steps by provenance: {S['reported_provenance']}.",
           f"- Review loops by E4 label: {S['review_loops_by_e4']}; by node: {S['review_loops_by_node']}.",
           f"- Review loops whose E4 published quote lands on a reported step: {S['review_loops_landed'][0]} of {S['review_loops_landed'][1]} with such a quote.",
           f"- E4 published quotes of review loops, status in the preprint: {S['e4_quote_in_preprint']} (a post-submission change should be absent or changed).",
           f"- Tried and dropped: {td['n']} items, final check {td['final']}; matched to a review step {td['matched_to_review_step']}; "
           f"with a node {td['with_node']}; final quote lands on a reported step {td['landed_on_reported_step']}; by document {td['units']}.",
           f"- Order-of-work annotations by document: {S['order_of_work_units']}.",
           f"- paper_returns from calc1 against the final_paper sequence of the calc1-review coding: {S['returns_calc1_vs_review_coding']}.", '',
           '## Definitions (short form)', '',
           '- paper_returns: reported steps with move return_after_failure. paper_revisits: reported steps whose node occurs earlier in the walk.',
           '- review_loops: review-sequence steps triggered by a referee, editor or commenter whose move is not declined.',
           '- disclosed_tried_dropped: g27 tried_dropped disclosures; only_in_responses: final check absent.',
           '- total_loops: paper_returns + review_loops + tried_dropped, with a tried_dropped item matched to a review loop or landing on a reported return counted once.',
           '- outside_only_loops: review loops with E4 label absent or no_change, plus tried_dropped items whose final check is absent (a review loop with matched items: every layer absent).',
           '- hidden_loops: review loops not labelled as_revision, plus tried_dropped items not stated in the final paper.', '',
           '## Caveats', '',
           '- Disclosures come from one Claude Code agent (g27, E13) and visibility labels from Claude Code agents (E4): neither is yet a defined prompt, schema and validator, so outside_only and hidden shares cannot be rerun with OLMo as they stand. review_loops and paper_returns come from the defined coding task.',
           '- The review layer covers the open discussion (AC, RC, CC, EC) that E3 read; second-round author responses (AR files) feed the disclosed layer only, so review loops of later rounds are missing.',
           '- A loop in the review layer is a reopening of submitted work, not necessarily a return after failure; most are requested additions or clarifications.',
           '- Matching thresholds (LOC 0.9, CHANGED 0.5 from g26; DMATCH 0.5; LAND_DIST 1) were set before the first run and not changed; landing can attach a review change to a neighbouring reported step. One rule changed after a spot check of the first run: E4 no_change on a review loop counts as not in the paper (a test asked for, run, and given only in the response); under the first rule (E4 absent only) the outside-only count was 38 of 594.',
           '- Every review loop is hidden by construction: E4 marked none of them as_revision, so the broad hidden share mostly restates E4.',
           '- Some E4 published quotes of review changes are already in the preprint (see Checks): E4 or E3 then points at text that predates the review.',
           '- Quotes from figure captions are not in the parsed XML text (g26 parse_xml keeps paragraphs), so those steps are unlocated.',
           '- Copernicus journals only, all 2022; journals with few papers give unstable shares.']
    return '\n'.join(md) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--disclosures-tag', default=None)
    ap.add_argument('keys', nargs='*')
    a = ap.parse_args()
    idx = [r for r in read_json(INDEX) if 'comments' in r]
    c1, rv = rounds.valid('calc1'), rounds.valid('calc1-review')
    raw = json.loads(VIS.read_text())
    vis = {p['key']: {s['i']: s for s in p['steps']} for p in raw.get('data', raw)}
    recs = []
    for r in idx:
        if a.keys and r['key'] not in a.keys:
            continue
        if r['key'] not in c1:
            print(r['key'], 'no valid calc1 coding; skipped')
            continue
        rec = paper(r, c1[r['key']], rv.get(r['key']), vis, a.disclosures_tag)
        recs.append(rec)
        m = rec['measures']
        print(rec['key'], rec['journal'], 'returns', m['paper_returns'], 'review', m.get('review_loops'),
              'td', m['disclosed_tried_dropped'], 'outside', m.get('outside_only_loops'), 'total', m.get('total_loops'))
    S = summarize(recs)
    if a.keys:
        print(json.dumps({k: S[k] for k in ('outside_only_share', 'hidden_share')}, indent=1))
        return
    params = {'loc': LOC, 'changed': CHANGED, 'min_tok': MIN_TOK, 'land_dist': LAND_DIST, 'dmatch': DMATCH,
              'reviewers': sorted(REVIEWERS), 'bootstrap': NBOOT, 'seed': SEED, 'disclosures': a.disclosures_tag or 'g27_agent_labels',
              'pilot_seen': sorted(PILOT_SEEN)}
    inputs = [rel(INDEX), 'private/analysis/codings/api/calc1/<key>.json', 'private/analysis/codings/api/calc1-review/<key>.json',
              rel(VIS), (f'private/analysis/codings/api/{a.disclosures_tag}/<key>.json' if a.disclosures_tag else rel(G27) + '/<key>.json'),
              'private/data/roadmap/review/<key>/<stem>.pdf', 'private/data/roadmap/pdfs/gold/<key>.xml.txt or .pdf',
              f'g26_translation.py sha256 {sha(Path(g26.__file__))}']
    write_json(OUT / 'merged_walks.json', {'summary': S, 'papers': recs}, inputs, params)
    prov = json.loads((OUT / 'merged_walks.json').read_text())['_provenance']
    figure(recs, S, OUT / 'fig_reconstruct.png', prov)
    (OUT / 'RECONSTRUCT.md').write_text(report(recs, S, prov))
    o = S['outside_only_share']
    log('g31_reconstruct.py', 'layered workflow walks (reported, review-induced, revised, disclosed) and loops per layer',
        len(recs), f"review layer {S['papers_review_layer']}; outside-only share of loops {o.get('mean')} {o.get('ci')}, "
        f"pooled {o.get('num')}/{o.get('den')}; descriptive, no outcome joined")


if __name__ == '__main__':
    main()
