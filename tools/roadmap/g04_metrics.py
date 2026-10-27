#!/usr/bin/env python3
"""Gold set, step 4: novelty and breadth proxies for the preselected papers.

Input : derived/gold/preselect.json (g03); topic verdicts from the breadth v1 audit
        (private/analysis/success-set/breadth/topic_audit.csv)
Output: derived/gold/metrics.json
Measures (all from OpenAlex, retrieval date in the provenance block):
  impact            citation_normalized_percentile (field and year normalized) and FWCI, carried from the pool
  novelty_pair      rarity of the paper's two leading topics appearing together in 2017-2021:
                    novelty_pair = -log10(1 + number of 2017-2021 works tagged with both topics). Higher = rarer.
                    A proxy for an unusual combination (in the spirit of Uzzi et al. 2013), not a measure of novelty.
  breadth_refs      share of the paper's references whose primary topic is outside geoscience
                    (breadth v1 topic map: fields 19 and 23 = geo, audit overrides; 'near' counted separately)
  breadth_citers    breadth v1 M2: share of citing works 2022-2026 outside geoscience, self-citations removed;
                    reported only when there are >= 10 citers (n given)
  advance           not computable from metadata; left for blinded human rating
Run   : python tools/roadmap/g04_metrics.py
"""
from __future__ import annotations
import csv
import math
from common import SET, CALC, DERIVED, ROOT, decision, log, openalex, paged, read_json, sid, write_json

AUDIT = ROOT / 'private' / 'analysis' / 'success-set' / 'breadth' / 'topic_audit.csv'
GEO_FIELDS = {'19', '23'}
WSEL = 'id,publication_year,primary_topic,authorships'


def load_audit() -> dict:
    v = {'geoscience': 'geo', 'adjacent': 'near', 'outside': 'far'}
    return {r['topic_id']: v[r['verdict'].strip()] for r in csv.DictReader(open(AUDIT)) if r.get('verdict', '').strip() in v}


def klass(w: dict, ov: dict) -> str | None:
    pt = w.get('primary_topic') or {}
    t = sid(pt.get('id'))
    if not t:
        return None
    if t in ov:
        return ov[t]
    return 'geo' if sid((pt.get('field') or {}).get('id')) in GEO_FIELDS else 'far'


def shares(works: list[dict], ov: dict) -> dict:
    cl = [klass(w, ov) for w in works]
    cl = [c for c in cl if c]
    n = len(cl)
    return {'n': n, 'far': cl.count('far') / n if n else None, 'near': cl.count('near') / n if n else None}


def refs_of(wid: str) -> list[str]:
    w = openalex(f'works/{wid}', {'select': 'id,referenced_works,authorships'})
    return [sid(r) for r in w.get('referenced_works', [])], {sid((a.get('author') or {}).get('id')) for a in w.get('authorships', [])}


def batch(ids: list[str]) -> list[dict]:
    out = []
    for i in range(0, len(ids), 50):
        out += openalex('works', {'filter': 'openalex_id:' + '|'.join(ids[i:i + 50]), 'select': WSEL, 'per-page': 50}).get('results', [])
    return out


def main() -> None:
    ov = load_audit()
    pre = read_json(SET / 'preselect.json')
    out = []
    for k, p in enumerate(pre):
        refs, authors = refs_of(p['id'])
        rb = shares(batch(refs), ov)
        t = p['topic_ids'][:2]
        n_pair = None
        if len(t) == 2:
            n_pair = openalex('works', {'filter': f'topics.id:{t[0]},topics.id:{t[1]},from_publication_date:2017-01-01,'
                                                  'to_publication_date:2021-12-31', 'per-page': 1, 'select': 'id'}).get('meta', {}).get('count')
        cites = [w for w in paged('works', {'filter': f"cites:{p['id']},from_publication_date:2022-01-01", 'select': WSEL}, cap=2000)
                 if not ({sid((a.get('author') or {}).get('id')) for a in w.get('authorships', [])} & authors)]
        cb = shares(cites, ov)
        out.append({**p, 'novelty_pair_count': n_pair,
                    'novelty_pair': None if n_pair is None else -math.log10(1 + n_pair),
                    'breadth_refs': rb['far'], 'breadth_refs_near': rb['near'], 'n_refs_classified': rb['n'],
                    'breadth_citers': cb['far'] if cb['n'] >= 10 else None, 'n_citers_noself': cb['n'], 'advance': None})
        if k % 50 == 0:
            print(k, p['id'], rb, n_pair, cb['n'], flush=True)
    write_json(SET / 'metrics.json', out, ['derived/gold/preselect.json', str(AUDIT.relative_to(ROOT))])
    log('g04_metrics.py', 'novelty (topic-pair rarity) and breadth (references, citers) for preselected papers', len(out))
    decision('Breadth used for stratification = share of references outside geoscience (defined for every paper, not tied to '
             'citation count); citer breadth v1 (>= 10 citers, self-citations removed, 2022-2026) recorded as an outcome. '
             'Novelty proxy = rarity of the two leading OpenAlex topics co-occurring in 2017-2021. Advance is not computed; it is '
             'left for blinded human rating.')


if __name__ == '__main__':
    main()
