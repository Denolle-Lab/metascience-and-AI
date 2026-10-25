#!/usr/bin/env python3
"""Gold set, step 5: the final stratified gold set, frozen, plus a manifest for the PDF fetcher.

Input : derived/gold/metrics.json (g04)
Output: derived/gold/gold_set.json      the frozen set with every metric and its stratum
        derived/gold/gold_manifest.jsonl  key, doi, stratum: input to `fetch_pdfs.py add-manifest`
        derived/gold/gold_set.md        readable table for the convenor
Rule  : per ring, N/2 papers spread over the 27 cells of impact tercile x novelty tercile x reference-breadth tercile
        (terciles computed within the ring's preselection). Cells are visited round robin in a seeded random order;
        inside a cell the paper whose subfield is least represented so far is taken (ties broken at random), so the
        set spans subfields as well as the three measured dimensions. Advance is not stratified (no metric); it is rated later.
Run   : python tools/roadmap/g05_select.py [--n 100] [--seed 2026]
"""
from __future__ import annotations
import argparse
import json
import random
from collections import Counter, defaultdict
from common import DERIVED, decision, log, read_json, write_json


def terciles(vals: list[float]) -> tuple[float, float]:
    v = sorted(x for x in vals if x is not None)
    return v[len(v) // 3], v[2 * len(v) // 3]


def tier(x, cuts) -> int | None:
    if x is None:
        return None
    return 1 if x < cuts[0] else (2 if x < cuts[1] else 3)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=100)
    ap.add_argument('--seed', type=int, default=2026)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    rows = read_json(DERIVED / 'gold' / 'metrics.json')
    gold, cutlog = [], {}
    for ring in ('core', 'broad'):
        R = sorted([r for r in rows if r['ring'] == ring], key=lambda r: r['id'])
        cuts = {m: terciles([r[m] for r in R]) for m in ('cnp', 'novelty_pair', 'breadth_refs')}
        cutlog[ring] = cuts
        cells = defaultdict(list)
        for r in R:
            t = (tier(r['cnp'], cuts['cnp']), tier(r['novelty_pair'], cuts['novelty_pair']), tier(r['breadth_refs'], cuts['breadth_refs']))
            if None in t:
                continue
            cells[t].append({**r, 'impact_tier': t[0], 'novelty_tier': t[1], 'breadth_tier': t[2]})
        order = sorted(cells)
        rng.shuffle(order)
        for c in order:
            rng.shuffle(cells[c])
        picked, sf = [], Counter()
        while len(picked) < a.n // 2 and any(cells.values()):
            for c in order:
                if cells[c] and len(picked) < a.n // 2:
                    best = min(cells[c], key=lambda r: sf[r['subfield']])
                    cells[c].remove(best)
                    picked.append(best)
                    sf[best['subfield']] += 1
        gold += picked
    for r in gold:
        r['key'] = 'g22_' + r['id']
        r['stratum'] = f"{r['ring']} I{r['impact_tier']} N{r['novelty_tier']} B{r['breadth_tier']}"
    write_json(DERIVED / 'gold' / 'gold_set.json', gold, ['derived/gold/metrics.json'], {'n': a.n, 'seed': a.seed, 'tercile_cuts': cutlog})
    with open(DERIVED / 'gold' / 'gold_manifest.jsonl', 'w') as f:
        for r in gold:
            f.write(json.dumps({'key': r['key'], 'doi': r['doi'], 'stratum': f"gold2022 {r['ring']}", 'openalex': r['id']}) + '\n')
    lines = ['# Gold set 2022 (frozen)', '', f"{len(gold)} papers; seed {a.seed}; rule in `tools/roadmap/g05_select.py`. "
             'I, N, B = impact, novelty proxy, reference breadth terciles within the ring (1 low, 3 high). Route: how the full text is fetched.', '',
             '| Key | Ring | I | N | B | Citations | Percentile | Citer breadth (n) | Subfield | Journal | Route | Title |', '|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|']
    for r in sorted(gold, key=lambda r: (r['ring'], -r['impact_tier'], -r['novelty_tier'], -r['breadth_tier'])):
        cb = f"{r['breadth_citers']:.2f} ({r['n_citers_noself']})" if r['breadth_citers'] is not None else f"n/a ({r['n_citers_noself']})"
        lines.append(f"| {r['key']} | {r['ring']} | {r['impact_tier']} | {r['novelty_tier']} | {r['breadth_tier']} | {r['cited_by_count']} | "
                     f"{r['cnp']:.3f} | {cb} | {r['subfield']} | {r['journal']} | {r['route']} | [{(r['title'] or '').replace('|', '/')}](https://doi.org/{r['doi']}) |")
    (DERIVED / 'gold' / 'gold_set.md').write_text('\n'.join(lines) + '\n')
    cov = Counter((r['ring'], r['impact_tier'], r['novelty_tier'], r['breadth_tier']) for r in gold)
    log('g05_select.py', 'frozen gold set', len(gold), f'{len(cov)} of 54 ring x cells covered; seed {a.seed}')
    decision(f'Gold set frozen: {len(gold)} papers, {a.n // 2} per ring, spread over impact x novelty-proxy x reference-breadth terciles '
             f'with subfield balancing; seed {a.seed}. Advance is not stratified because no metadata measure exists; it will be rated blind.')
    print(len(gold), 'gold papers;', len(cov), 'cells covered;', Counter(r['route'] for r in gold), Counter(r['subfield'] for r in gold).most_common(12))


if __name__ == '__main__':
    main()
