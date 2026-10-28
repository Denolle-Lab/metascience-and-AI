"""Phase 2c: agreement between the model's disclosure coding and g27's labels (E13), once review codings exist.

Question. The author-response layer is now a defined task: the review coding call of tools/code_papers.py with
--review-dir codes `disclosures` under agents/coder/REVIEW_ADDENDUM.md v1.0.0 (schema review_addendum.schema.json,
validator tools/check_coding.py). How well do those codings agree with the exploratory labels of g27 (one Claude Code
agent, E13), on which statements are disclosures, of which kind, and whether the final paper carries them?

Status. Stub, written October 28 before any review coding with disclosures exists. No paid API call. g27 is a single
agent labeller, not a gold standard: precision and recall below are agreement with g27, not accuracy. The two
advance pilot papers (g22_W4205292752, g22_W4223595027) are not in the 61 review papers; any later join with the
advance outcome must still exclude them from a confirmatory test (EXCLUDE).

Inputs   model codings: private/analysis/codings/api/<tag>/<key>.json (read only), or --codings DIR; only codings that
         carry review_addendum_version are used, each re-validated with check_coding.validate(review=True, texts,
         checks=DISCLOSURE_CHECKS); under the 'item' rule the disclosures failing a quote check are dropped
         (check_coding.kept_disclosures) before matching, as g34 drops them
         g27 labels: derived/translation/labels/<key>.json; g27 units: derived/translation/author_units.jsonl
         texts for the quote checks: tools/code_papers.review_texts (discussion.txt, the author-responses document
         derived/review/author_responses/<key>.txt, the publisher XML text)
Matching (one-to-one, per paper, greedy by score)
         score  overlap coefficient of the two quotes' normalised word 3-grams (g27 norm()): |A & B| / min(|A|, |B|);
                quotes under 3 words use word sets
         pair   same unit and score >= MATCH_SAME_UNIT, or different units and score >= MATCH_OTHER_UNIT (the same reply
                posted twice under two AC numbers, or an AR page repeating an AC paragraph)
Measures
         detection     matched pairs, model-only and g27-only items; precision = matched / model items, recall =
                       matched / g27 items, F1; overall and per g27 kind (recall) and model kind (precision)
         kind          on matched pairs: share equal and Krippendorff's alpha, nominal (g11_human_agreement.alpha_nominal)
         final status  on matched pairs: share equal, alpha nominal, and alpha ordinal with absent 1 < partly 2 < present 3
                       (g11 alpha_ordinal)
         unit-kind presence  matching-free: one unit per (paper, g27 author unit, kind), value true when the coder gives
                       that unit at least one disclosure of that kind; alpha nominal, as node presence in g11
         quote checks  share of model disclosures passing each check of check_coding.disclosure_checks
         model only    node and loop distributions (g27 has no counterpart)
Kinds    --kinds K1,K2 keeps only items of those kinds on both sides (the g34 disclosure gate: tried_dropped and
         added_for_review, on round 2, where the instrument was not developed; round 2 needs g27 labels first)
Outputs  derived/translation/<out>.json and <OUT>.md (default disclosure_agreement, DISCLOSURE_AGREEMENT); MANIFEST row
Run      python tools/roadmap/g30_disclosure_agreement.py --tag <review tag>      (e.g. a tag of a calc1-review rerun)
         python tools/roadmap/g30_disclosure_agreement.py --tag r2-review-v2 --kinds tried_dropped,added_for_review \
             --out disclosure_agreement_r2_oo                                    (the g34 gate)
         python tools/roadmap/g30_disclosure_agreement.py selftest              (g27 against a perturbed copy of
         itself in memory; checks the pipeline, writes nothing but the MANIFEST row)
"""
from __future__ import annotations
import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from common import DERIVED, PRIVATE, ROOT, TODAY, commit, log, rel, write_json
from g11_human_agreement import alpha_nominal, alpha_ordinal
from g27_author_responses import KINDS, FINAL, LABELS, UNITS, norm

sys.path.insert(0, str(ROOT / 'tools'))
from check_coding import validate, disclosure_checks, kept_disclosures, item_ok, DISCLOSURE_CHECKS  # noqa: E402

OUT = DERIVED / 'translation'
CODINGS = PRIVATE / 'analysis' / 'codings' / 'api'
EXCLUDE = {'g22_W4205292752', 'g22_W4223595027'}   # advance pilot papers: seen advance codings, never in a confirmatory test
MATCH_SAME_UNIT, MATCH_OTHER_UNIT, NGRAM = 0.5, 0.8, 3
ORD = {'absent': 1, 'partly': 2, 'present': 3}
CHECKS = ['unit_found', 'author_unit', 'quote_in_unit', 'quote_in_document', 'quote_not_referee', 'final_quote_in_paper',
          'final_quote_at_loc']
KINDS_KEPT = None   # set from --kinds: only these kinds on both sides


def grams(q: str) -> set:
    w = norm(q).split()
    return {' '.join(w[i:i + NGRAM]) for i in range(len(w) - NGRAM + 1)} if len(w) >= NGRAM else set(w)


def score(a: str, b: str) -> float:
    A, B = grams(a), grams(b)
    return len(A & B) / min(len(A), len(B)) if A and B else 0.0


def g27_items(key: str) -> list[dict]:
    lab = json.loads((LABELS / f'{key}.json').read_text())
    return [{'unit': d['unit'], 'kind': d['kind'], 'quote': d['quote'], 'final_paper_status': d['final']} for d in lab['disclosures']
            if KINDS_KEPT is None or d['kind'] in KINDS_KEPT]


def match(model: list[dict], ref: list[dict]) -> list[tuple[int, int, float]]:
    cand = []
    for i, m in enumerate(model):
        for j, r in enumerate(ref):
            s = score(m['quote'], r['quote'])
            if s >= (MATCH_SAME_UNIT if m['unit'] == r['unit'] else MATCH_OTHER_UNIT):
                cand.append((s + (m['unit'] == r['unit']), i, j, s))
    used_i, used_j, pairs = set(), set(), []
    for _, i, j, s in sorted(cand, reverse=True):
        if i not in used_i and j not in used_j:
            used_i.add(i); used_j.add(j); pairs.append((i, j, round(s, 3)))
    return pairs


def prf(m: int, a: int, b: int) -> dict:
    p, r = (m / a if a else None), (m / b if b else None)
    return {'matched': m, 'model': a, 'g27': b, 'precision': None if p is None else round(p, 3),
            'recall': None if r is None else round(r, 3), 'f1': round(2 * p * r / (p + r), 3) if p and r else None}


def analyse(model_by_key: dict[str, list[dict]], checks_by_key: dict[str, list[dict]]) -> dict:
    units = defaultdict(set)
    for line in UNITS.read_text().splitlines():
        u = json.loads(line)
        units[u['key']].add(u['unit'])
    pairs_all, kind_units, final_units, presence = [], [], [], []
    det_kind = {k: Counter() for k in KINDS}
    n_model = n_ref = 0
    for key, model in sorted(model_by_key.items()):
        ref = g27_items(key)
        pairs = match(model, ref)
        n_model += len(model); n_ref += len(ref)
        for i, j, s in pairs:
            m, r = model[i], ref[j]
            pairs_all.append({'key': key, 'model_unit': m['unit'], 'g27_unit': r['unit'], 'score': s, 'model_kind': m['kind'],
                              'g27_kind': r['kind'], 'model_final': m['final_paper_status'], 'g27_final': r['final_paper_status']})
            kind_units.append([m['kind'], r['kind']])
            final_units.append([m['final_paper_status'], r['final_paper_status']])
        mi, rj = {i for i, _, _ in pairs}, {j for _, j, _ in pairs}
        for j, r in enumerate(ref):
            det_kind[r['kind']]['g27'] += 1; det_kind[r['kind']]['recalled'] += j in rj
        for i, m in enumerate(model):
            if m['kind'] in det_kind:
                det_kind[m['kind']]['model'] += 1; det_kind[m['kind']]['confirmed'] += i in mi
        for u in sorted(units[key]):
            for k in KINDS:
                presence.append([any(m['unit'] == u and m['kind'] == k for m in model), any(r['unit'] == u and r['kind'] == k for r in ref)])
    allchk = [c for cs in checks_by_key.values() for c in cs]
    flat = [m for ms in model_by_key.values() for m in ms]
    eq = lambda us: round(sum(a == b for a, b in us) / len(us), 3) if us else None
    return {
        'papers': len(model_by_key), 'excluded_present': sorted(EXCLUDE & set(model_by_key)),
        'detection': prf(len(pairs_all), n_model, n_ref),
        'detection_by_kind': {k: {'g27': c['g27'], 'recall': round(c['recalled'] / c['g27'], 3) if c['g27'] else None,
                                  'model': c['model'], 'precision': round(c['confirmed'] / c['model'], 3) if c['model'] else None}
                              for k, c in det_kind.items()},
        'kind': {'pairs': len(kind_units), 'equal': eq(kind_units), 'alpha_nominal': alpha_nominal(kind_units),
                 'confusion': dict(Counter(f'{a}|{b}' for a, b in kind_units))},
        'final_status': {'pairs': len(final_units), 'equal': eq(final_units), 'alpha_nominal': alpha_nominal(final_units),
                         'alpha_ordinal': alpha_ordinal([[ORD[a], ORD[b]] for a, b in final_units]),
                         'confusion': dict(Counter(f'{a}|{b}' for a, b in final_units))},
        'unit_kind_presence': {'units': len(presence), 'alpha_nominal': alpha_nominal(presence)},
        'quote_checks': {c: (round(sum(x.get(c) is True for x in allchk) / n, 3) if (n := sum(c in x for x in allchk)) else None) for c in CHECKS},
        'model_only': {'node': dict(Counter(m.get('node') for m in flat)), 'loop': dict(Counter(str(m.get('loop')) for m in flat)),
                       'units_outside_g27_reading': sum(1 for k, ms in model_by_key.items() for m in ms if m['unit'] not in units[k])},
        'pairs': pairs_all,
    }


def load_model(src: Path) -> tuple[dict, dict, list]:
    import code_papers as cp
    cp.REVIEW_DIR = str(PRIVATE / 'data' / 'roadmap' / 'review')
    have = {f.stem for f in LABELS.glob('*.json')}
    model, checks, invalid = {}, {}, []
    for f in sorted(src.glob('*.json')):
        c = json.loads(f.read_text())
        if 'review_addendum_version' not in c or c.get('key', f.stem) not in have:
            continue
        texts = cp.review_texts(c['key'])
        errs = validate(c, review=True, texts=texts, checks=DISCLOSURE_CHECKS)
        if errs:
            invalid.append({'key': c['key'], 'errors': errs[:5]}); continue
        chk = disclosure_checks(c, texts)
        items = kept_disclosures(c, texts)[0] if DISCLOSURE_CHECKS == 'item' else c['disclosures']
        model[c['key']] = [d for d in items if KINDS_KEPT is None or d.get('kind') in KINDS_KEPT]
        checks[c['key']] = [ch for d, ch in zip([d for d in c['disclosures'] if isinstance(d, dict)], chk)
                            if KINDS_KEPT is None or d.get('kind') in KINDS_KEPT]
    return model, checks, invalid


def report(res: dict, src: str, invalid: list) -> list[str]:
    d, k, f = res['detection'], res['kind'], res['final_status']
    md = [f'# Disclosures: model coding against g27 labels ({TODAY})', '',
          f'Source: tools/roadmap/g30_disclosure_agreement.py ({commit()}); model codings {src}; g27 labels (E13, one Claude Code agent, '
          'exploratory). Agreement with g27, not accuracy.', '',
          f'Papers {res["papers"]}; invalid or skipped codings {len(invalid)}.',
          f'Detection: {d["matched"]} matched of {d["model"]} model and {d["g27"]} g27 items; precision {d["precision"]}, recall {d["recall"]}, F1 {d["f1"]}.',
          f'Kind on matched pairs: equal {k["equal"]}, Krippendorff alpha (nominal) {k["alpha_nominal"]}.',
          f'Final-paper status on matched pairs: equal {f["equal"]}, alpha nominal {f["alpha_nominal"]}, alpha ordinal {f["alpha_ordinal"]}.',
          f'Unit-kind presence (no matching): alpha {res["unit_kind_presence"]["alpha_nominal"]} over {res["unit_kind_presence"]["units"]} units.',
          f'Quote checks passed (share of model items): {res["quote_checks"]}.']
    return md


def run(args) -> None:
    src = Path(args.codings) if args.codings else CODINGS / args.tag
    model, checks, invalid = load_model(src)
    if not model:
        print(f'no valid codings with disclosures (review addendum) under {src}; {len(invalid)} invalid')
        log('g30_disclosure_agreement.py', 'model review codings with disclosures', 0, f'{rel(src)}: none yet; {len(invalid)} invalid')
        return
    res = analyse(model, checks)
    res['invalid'] = invalid
    res['kinds_kept'] = sorted(KINDS_KEPT) if KINDS_KEPT else 'all'
    res['disclosure_checks'] = DISCLOSURE_CHECKS
    res['items_dropped_by_quote_checks'] = sum(not item_ok(ch) for cs in checks.values() for ch in cs) if DISCLOSURE_CHECKS == 'item' else 0
    write_json(OUT / f'{args.out}.json', res, inputs=[rel(src) + '/*.json', rel(LABELS) + '/*.json', rel(UNITS)],
               params={'match_same_unit': MATCH_SAME_UNIT, 'match_other_unit': MATCH_OTHER_UNIT, 'ngram': NGRAM, 'kinds': KINDS,
                       'final': FINAL, 'kinds_kept': sorted(KINDS_KEPT) if KINDS_KEPT else None, 'disclosure_checks': DISCLOSURE_CHECKS})
    md = report(res, rel(src), invalid)
    (OUT / f'{args.out.upper()}.md').write_text('\n'.join(md) + '\n')
    d = res['detection']
    log('g30_disclosure_agreement.py', 'disclosures matched to g27 labels', d['matched'],
        f'{res["papers"]} papers from {rel(src)}; P {d["precision"]} R {d["recall"]}; kind alpha {res["kind"]["alpha_nominal"]}; '
        f'final alpha {res["final_status"]["alpha_nominal"]}')
    print('\n'.join(md))


def selftest(args) -> None:
    """g27 against a perturbed copy of itself: 20% of items dropped, 10% relabelled in kind, 10% in final status. Checks
    matching and the alpha plumbing; nothing is written except the MANIFEST row."""
    rnd = random.Random(30)
    model = {}
    for f in sorted(LABELS.glob('*.json')):
        items = []
        for r in g27_items(f.stem):
            if rnd.random() < 0.2:
                continue
            m = dict(r)
            if rnd.random() < 0.1:
                m['kind'] = rnd.choice([k for k in KINDS if k != r['kind']])
            if rnd.random() < 0.1:
                m['final_paper_status'] = rnd.choice([x for x in FINAL if x != r['final_paper_status']])
            m['node'], m['loop'] = 'none', False
            items.append(m)
        model[f.stem] = items
    res = analyse(model, {})
    d = res['detection']
    assert d['precision'] == 1.0 and abs(d['recall'] - 0.8) < 0.05, d
    assert 0.8 <= res['kind']['equal'] <= 0.95 and 0.8 <= res['final_status']['equal'] <= 0.95, (res['kind'], res['final_status'])
    print('selftest ok:', json.dumps({x: res[x] for x in ('detection', 'unit_kind_presence')}),
          'kind', res['kind']['equal'], res['kind']['alpha_nominal'], 'final', res['final_status']['equal'], res['final_status']['alpha_nominal'])
    log('g30_disclosure_agreement.py selftest', 'g27 labels against a perturbed copy (in memory)', d['matched'],
        f'P {d["precision"]} R {d["recall"]}; kind alpha {res["kind"]["alpha_nominal"]}; final alpha {res["final_status"]["alpha_nominal"]}; nothing written')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', nargs='?', default='run', choices=['run', 'selftest'])
    ap.add_argument('--tag', help='review coding tag under private/analysis/codings/api/')
    ap.add_argument('--codings', help='folder of review codings (instead of --tag)')
    ap.add_argument('--kinds', help='comma-separated kinds kept on both sides (default all)')
    ap.add_argument('--out', default='disclosure_agreement', help='output stem under derived/translation/')
    a = ap.parse_args()
    if a.kinds:
        KINDS_KEPT = set(a.kinds.split(','))
        if KINDS_KEPT - set(KINDS):
            ap.error(f'unknown kinds {sorted(KINDS_KEPT - set(KINDS))}')
    if a.cmd == 'selftest':
        selftest(a)
    elif not (a.tag or a.codings):
        ap.error('give --tag or --codings')
    else:
        run(a)
