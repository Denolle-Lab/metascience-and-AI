#!/usr/bin/env python3
"""Gold set, step 3: stratified preselection from the pool, so metrics are computed on hundreds, not 18,000.

Input : derived/gold/pool.json (g02)
Output: derived/gold/preselect.json
Rule  : drop papers with a convenor co-author; per ring, draw N/2 papers with equal numbers per impact quintile
        (OpenAlex citation_normalized_percentile), and within a quintile spread across subfields by round robin.
        random.seed(SEED); candidates sorted by OpenAlex id before shuffling, so the draw is reproducible.
Run   : python tools/roadmap/g03_preselect.py [--n 600] [--seed 2026]
"""
from __future__ import annotations
import argparse
import random
from collections import defaultdict
from common import DERIVED, decision, log, read_json, write_json


def quintile(x: float | None) -> int:
    return 0 if x is None else min(4, int(x * 5))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=600)
    ap.add_argument('--seed', type=int, default=2026)
    a = ap.parse_args()
    pool = [p for p in read_json(DERIVED / 'gold' / 'pool.json') if not p['convenor_coauthor']]
    rng = random.Random(a.seed)
    out = []
    for ring in ('core', 'broad'):
        per_q = a.n // 2 // 5
        for q in range(5):
            cell = sorted([p for p in pool if p['ring'] == ring and quintile(p['cnp']) == q], key=lambda p: p['id'])
            by_sf = defaultdict(list)
            for p in cell:
                by_sf[p['subfield'] or 'none'].append(p)
            for v in by_sf.values():
                rng.shuffle(v)
            sfs = sorted(by_sf)
            rng.shuffle(sfs)
            picked = []
            while len(picked) < per_q and any(by_sf.values()):
                for s in sfs:
                    if by_sf[s] and len(picked) < per_q:
                        picked.append({**by_sf[s].pop(), 'impact_quintile': q + 1})
            out += picked
    write_json(DERIVED / 'gold' / 'preselect.json', out, ['derived/gold/pool.json'], {'n': a.n, 'seed': a.seed})
    log('g03_preselect.py', 'stratified preselection (ring x impact quintile x subfield)', len(out), f'seed {a.seed}')
    decision(f'Preselection: {len(out)} papers, half per ring, equal per impact quintile (OpenAlex citation_normalized_percentile '
             f'as of {__import__("common").TODAY}), subfields interleaved within a quintile; seed {a.seed}. Papers with a convenor '
             'co-author are excluded so that raters and coders stay independent of the convenor.')
    print(len(out), 'preselected')


if __name__ == '__main__':
    main()
