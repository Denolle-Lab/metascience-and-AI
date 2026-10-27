#!/usr/bin/env python3
"""Round 2, step 1: a diversified preselection of 2022 papers, drawn from the same pool as round 1.

Input : derived/gold/pool.json (g02), derived/gold/preselect.json (round 1, excluded)
Output: derived/r2/preselect.json   same record format as round 1, so g04, g06, g07, g10 and g12 run unchanged
        with ROADMAP_SET=r2 ROADMAP_CALC=r2calc
Rule  : drop papers with a convenor co-author and every round-1 preselected paper; keep open-access papers only
        (fetchable without subscriptions, licence-clean for any model, inputs shareable with colleagues re-running
        the protocol on another model); at most --cap papers per journal; per ring, N/2 papers with equal numbers per
        impact quintile (OpenAlex citation_normalized_percentile); within a quintile, round robin over publishers,
        then over journals inside a publisher, so no venue dominates.
        random.Random(seed); candidates sorted by OpenAlex id before shuffling, so the draw is reproducible.
Run   : python tools/roadmap/g18_round2_draw.py [--n 300] [--cap 4] [--seed 2027]
"""
from __future__ import annotations
import argparse
import random
from collections import Counter, defaultdict
from common import DERIVED, decision, log, read_json, write_json


def quintile(x):
    return 0 if x is None else min(4, int(x * 5))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=300)
    ap.add_argument('--cap', type=int, default=4)
    ap.add_argument('--seed', type=int, default=2027)
    a = ap.parse_args()
    r1 = {p['id'] for p in read_json(DERIVED / 'gold' / 'preselect.json')}
    pool = [p for p in read_json(DERIVED / 'gold' / 'pool.json')
            if not p['convenor_coauthor'] and p['id'] not in r1 and p.get('is_oa') and p.get('doi')]
    rng = random.Random(a.seed)
    per_journal = Counter()
    out = []
    for ring in ('core', 'broad'):
        want = a.n // 2 // 5
        for q in range(5):
            cand = sorted([p for p in pool if p['ring'] == ring and quintile(p.get('cnp')) == q], key=lambda p: p['id'])
            rng.shuffle(cand)
            by_pub = defaultdict(lambda: defaultdict(list))
            for p in cand:
                by_pub[p.get('publisher') or '?'][p.get('journal') or '?'].append(p)
            pubs = sorted(by_pub); rng.shuffle(pubs)
            got = []
            while len(got) < want and any(any(js.values()) for js in by_pub.values()):
                for pub in pubs:
                    js = by_pub[pub]
                    names = [j for j in sorted(js) if js[j] and per_journal[j] < a.cap]
                    if not names:
                        continue
                    j = names[rng.randrange(len(names))]
                    p = js[j].pop()
                    per_journal[j] += 1
                    got.append(p)
                    if len(got) >= want:
                        break
                else:
                    if not any(js[j] and per_journal[j] < a.cap for js in by_pub.values() for j in js):
                        break
            out += got
    write_json(DERIVED / 'r2' / 'preselect.json', out, ['derived/gold/pool.json', 'derived/gold/preselect.json (excluded)'])
    pubs = Counter(p.get('publisher') for p in out); js = Counter(p.get('journal') for p in out)
    log('g18_round2_draw.py', 'round 2 preselection (open access, journal cap)', len(out),
        f'{len(js)} journals, {len(pubs)} publishers, cap {a.cap}, seed {a.seed}')
    decision(f'Round 2 preselection: {len(out)} open-access 2022 papers not in round 1, at most {a.cap} per journal, equal per '
             f'impact quintile and ring, round robin over publishers (seed {a.seed}). Open access only so that every paper can '
             f'be fetched and the same inputs can be handed to colleagues re-running the protocol with an open-weight model.')
    print(len(out), 'papers;', len(js), 'journals;', len(pubs), 'publishers')
    print('publishers', pubs.most_common(15))
    print('per quintile', Counter((p['ring'], quintile(p.get('cnp'))) for p in out))


if __name__ == '__main__':
    main()
