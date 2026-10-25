#!/usr/bin/env python3
"""Gold set, step 11: collect the human codings and compute agreement between coders (the analysis of record).

Input : coders' my_codings folders (default: private/data/roadmap/app/packets/<ID>/my_codings/, or --from DIR with one
        subfolder per coder ID); derived/gold/human_assignment.json
Output: derived/gold/human/<ID>/<key>.<ID>.{coding,ratings}.json   collected copies (draft files are ignored)
        derived/gold/human_agreement.json                         per pair and summary
Measures:
  per pair       tools/check_coding.py agree(): entry node and state, outcome, decisive mode (match or not), node and mode
                 set Jaccard, node and mode sequence similarity
  per field      Krippendorff's alpha, nominal, over all papers with two codings: entry state, entry node, outcome, claim
                 status, composition, decisive node and mode, each gate; node presence (one unit per paper and node, as in
                 the reliability run); ratings: novelty and advance scores (ordinal alpha), eligibility, impact forecast
  gate           the roadmap's thresholds: alpha >= 0.67 for categorical fields, >= 0.8 for outcome fields
Every file is validated against its schema before use; invalid files are listed and skipped.
Run   : python tools/roadmap/g11_human_agreement.py [--from DIR]
"""
from __future__ import annotations
import argparse
import itertools
import json
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from common import DATA, DERIVED, ROOT, decision, log, read_json, write_json

sys.path.insert(0, str(ROOT / 'tools'))
from check_coding import agree  # noqa: E402
import jsonschema  # noqa: E402

NODES = list('NEOIQHSDFCVXKPR')


def alpha_nominal(units: list[list]) -> float | None:
    """Krippendorff's alpha for nominal data; units = list of value lists (one value per coder, None = missing)."""
    coinc = Counter()
    n_tot = 0
    for vals in units:
        v = [x for x in vals if x is not None]
        m = len(v)
        if m < 2:
            continue
        for a, b in itertools.permutations(range(m), 2):
            coinc[(v[a], v[b])] += 1 / (m - 1)
        n_tot += m
    if n_tot == 0:
        return None
    marg = Counter()
    for (a, _), w in coinc.items():
        marg[a] += w
    do = sum(w for (a, b), w in coinc.items() if a != b)
    de = sum(marg[a] * marg[b] for a in marg for b in marg if a != b) / (n_tot - 1)
    return None if de == 0 else round(1 - do / de, 3)


def alpha_ordinal(units: list[list]) -> float | None:
    """Krippendorff's alpha with the ordinal metric, for scores 1..5."""
    coinc = Counter()
    n_tot = 0
    for vals in units:
        v = [x for x in vals if x is not None]
        m = len(v)
        if m < 2:
            continue
        for a, b in itertools.permutations(range(m), 2):
            coinc[(v[a], v[b])] += 1 / (m - 1)
        n_tot += m
    if n_tot == 0:
        return None
    marg = Counter()
    for (a, _), w in coinc.items():
        marg[a] += w
    cats = sorted(marg)

    def d2(c, k):
        lo, hi = min(c, k), max(c, k)
        s = sum(marg[g] for g in cats if lo <= g <= hi) - (marg[c] + marg[k]) / 2
        return s * s
    do = sum(w * d2(a, b) for (a, b), w in coinc.items())
    de = sum(marg[a] * marg[b] * d2(a, b) for a in cats for b in cats) / (n_tot - 1)
    return None if de == 0 else round(1 - do / de, 3)


def collect(src: Path | None) -> dict:
    out = DERIVED / 'gold' / 'human'
    roots = {}
    if src:
        roots = {d.name: d for d in src.iterdir() if d.is_dir()}
    else:
        for d in (DATA / 'app' / 'packets').glob('*'):
            if (d / 'my_codings').is_dir():
                roots[d.name] = d / 'my_codings'
    n = 0
    for cid, d in roots.items():
        for f in d.glob('*.json'):
            if '.draft.' in f.name:
                continue
            (out / cid).mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out / cid / f.name)
            n += 1
    return {'copied': n, 'coders': sorted(roots)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--from', dest='src')
    a = ap.parse_args()
    col = collect(Path(a.src) if a.src else None)
    cs = json.loads((ROOT / 'agents/coder/coding.schema.json').read_text())
    rs = json.loads((ROOT / 'agents/coder/ratings.schema.json').read_text())
    cod, rat, bad = defaultdict(dict), defaultdict(dict), []
    for f in sorted((DERIVED / 'gold' / 'human').glob('*/*.json')):
        cid = f.parent.name
        try:
            obj = json.loads(f.read_text())
            if f.name.endswith('.coding.json'):
                jsonschema.validate(obj, cs); cod[obj['key']][cid] = obj
            elif f.name.endswith('.ratings.json'):
                jsonschema.validate(obj, rs); rat[obj['key']][cid] = obj
        except Exception as e:  # noqa: BLE001
            bad.append({'file': str(f.relative_to(ROOT)), 'error': str(e).splitlines()[0][:200]})
    pairs = []
    for k, by in cod.items():
        for x, y in itertools.combinations(sorted(by), 2):
            pairs.append({'key': k, 'coders': [x, y], **agree(by[x], by[y])})
    def field(get, src):
        return [[get(v) for v in by.values()] for by in src.values() if len(by) >= 2]
    fp = lambda c: next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps']
    alphas = {
        'entry_state': alpha_nominal(field(lambda c: c['entry']['state'], cod)),
        'entry_node': alpha_nominal(field(lambda c: c['entry']['node'], cod)),
        'outcome': alpha_nominal(field(lambda c: c['end']['outcome'], cod)),
        'claim_status': alpha_nominal(field(lambda c: c['end']['claim_status'], cod)),
        'composition': alpha_nominal(field(lambda c: c['composition'], cod)),
        'decisive_node': alpha_nominal(field(lambda c: c['decisive_move']['node'], cod)),
        'decisive_mode': alpha_nominal(field(lambda c: c['decisive_move']['mode'], cod)),
        'gate_action': alpha_nominal(field(lambda c: c['gates']['action'], cod)),
        'gate_claim': alpha_nominal(field(lambda c: c['gates']['claim'], cod)),
        'gate_registration': alpha_nominal(field(lambda c: c['gates']['registration'], cod)),
        'node_presence': alpha_nominal([u for by in cod.values() if len(by) >= 2
                                        for u in ([[n in {s['node'] for s in fp(c)} for c in by.values()] for n in NODES])]),
        'novelty_score': alpha_ordinal(field(lambda r: r['novelty']['score'], rat)),
        'advance_score': alpha_ordinal(field(lambda r: r['advance']['score'], rat)),
        'eligible_in_my_view': alpha_nominal(field(lambda r: r['eligible_in_my_view'], rat)),
        'impact_forecast': alpha_nominal(field(lambda r: r['impact_forecast'], rat)),
    }
    gate = {k: (None if v is None else v >= (0.8 if k in ('outcome', 'claim_status') else 0.67)) for k, v in alphas.items()}
    mean = lambda f: round(sum(float(p[f]) for p in pairs) / len(pairs), 3) if pairs else None
    summary = {'papers_with_two_codings': sum(1 for by in cod.values() if len(by) >= 2), 'pairs': len(pairs),
               **{f: mean(f) for f in ('node_set_jaccard', 'mode_set_jaccard', 'node_seq_similarity', 'mode_seq_similarity',
                                       'entry_node', 'entry_state', 'outcome', 'decisive_mode')},
               'alpha': alphas, 'meets_gate': gate,
               'minutes_per_paper': round(sum(r['minutes_spent'] for by in rat.values() for r in by.values()) / max(1, sum(len(by) for by in rat.values())), 1)}
    write_json(DERIVED / 'gold' / 'human_agreement.json', {'collected': col, 'invalid_files': bad, 'summary': summary, 'pairs': pairs},
               ['derived/gold/human/', 'agents/coder/coding.schema.json', 'agents/coder/ratings.schema.json'])
    log('g11_human_agreement.py', 'human gold-set agreement', len(pairs),
        f"{summary['papers_with_two_codings']} papers with two codings; {len(bad)} invalid files; node alpha {alphas['node_presence']}")
    if pairs:
        decision(f"Human agreement computed on {summary['papers_with_two_codings']} papers (g11): node-presence alpha {alphas['node_presence']}, "
                 f"outcome alpha {alphas['outcome']}; gates per field in human_agreement.json.")
    print(json.dumps(summary, indent=1))
    if bad:
        print('invalid files:', json.dumps(bad, indent=1))


if __name__ == '__main__':
    main()
