#!/usr/bin/env python3
"""Relate workflow topology to outcomes: which coded routes go with impact, breadth, and conclusions.

  python3 tools/analyze_topology.py --papers private/analysis/codings/summary/papers.csv \
      --manifest private/corpus/<name>.jsonl [--breadth private/analysis/success-set/breadth/<run>_results.json] \
      [--out private/analysis/codings/summary/topology]

Inputs: papers.csv from tools/aggregate_codings.py; the corpus manifest (impact = OpenAlex
field-normalized citation percentile `cnp`); optionally breadth v1 results (far share of citers,
first five years, self-citations excluded) from the breadth script.
For each topology feature (entry from a capability; uses N, E, H, D, V, X, P; contradiction outcome;
any stated disagreement; any reported alternative; steps; distinct modes; returns to a mode) it reports
the Spearman correlation with each outcome and the difference in prevalence (or mean) between the top
and bottom thirds of the outcome, each with a 95% bootstrap interval (2,000 resamples, seed 2026).
These are associations in a selected sample: no causal reading, no correction for multiple
comparisons beyond reporting all of them. Standard library only.
"""
from __future__ import annotations
import argparse, csv, json, random, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEATURES = [('entry_capability', lambda r: r['entry_state'] == 'capability'), ('uses_N', lambda r: r['has_N'] == 'True'),
            ('uses_E', lambda r: r['has_E'] == 'True'), ('uses_H', lambda r: r['has_H'] == 'True'), ('uses_D', lambda r: r['has_D'] == 'True'),
            ('uses_V', lambda r: r['has_V'] == 'True'), ('uses_X', lambda r: r['has_X'] == 'True'), ('uses_P', lambda r: r['has_P'] == 'True'),
            ('outcome_contradicted', lambda r: r['outcome'] == 'contradicted'), ('any_disagreement', lambda r: int(r.get('n_disagreements') or 0) > 0),
            ('alternative_effect_reported', lambda r: int(r.get('n_alternatives_effect_reported') or 0) > 0),
            ('steps', lambda r: int(r['steps'])), ('distinct_modes', lambda r: int(r['distinct_modes'])), ('mode_returns', lambda r: int(r['mode_returns']))]


def ranks(x):
    order = sorted(range(len(x)), key=lambda i: x[i]); r = [0.0] * len(x); i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    if len(set(x)) < 2 or len(set(y)) < 2:
        return None
    rx, ry = ranks(x), ranks(y); mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else None


def tertile_diff(x, y):
    order = sorted(range(len(y)), key=lambda i: y[i]); t = max(1, len(y) // 3)
    lo, hi = [x[i] for i in order[:t]], [x[i] for i in order[-t:]]
    return statistics.mean(hi) - statistics.mean(lo)


def boot(fn, x, y, n=2000, seed=2026):
    rng = random.Random(seed); idx = range(len(x)); vals = []
    for _ in range(n):
        s = [rng.choice(idx) for _ in idx]; v = fn([x[i] for i in s], [y[i] for i in s])
        if v is not None:
            vals.append(v)
    if len(vals) < n * 0.5:
        return None
    vals.sort(); return [round(vals[int(0.025 * len(vals))], 3), round(vals[int(0.975 * len(vals)) - 1], 3)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--papers', required=True); ap.add_argument('--manifest', required=True); ap.add_argument('--breadth')
    ap.add_argument('--out', type=Path, default=ROOT / 'private' / 'analysis' / 'codings' / 'summary' / 'topology')
    a = ap.parse_args()
    meta = {json.loads(l)['key']: json.loads(l) for l in Path(a.manifest).read_text().splitlines() if l.strip()}
    breadth = json.loads(Path(a.breadth).read_text()) if a.breadth else {}
    rows = [r for r in csv.DictReader(open(a.papers)) if r['key'] in meta]
    outcomes = {'impact (cnp)': lambda r: meta[r['key']].get('cnp')}
    if breadth:
        outcomes['breadth v1 (far share)'] = lambda r: (((breadth.get(r['key']) or {}).get('v1') or {}).get('far') or {}).get('p')
    res = []
    for oname, of in outcomes.items():
        sub = [r for r in rows if of(r) is not None]
        y = [float(of(r)) for r in sub]
        for fname, ff in FEATURES:
            x = [float(ff(r)) for r in sub]
            if len(sub) < 6:
                continue
            res.append({'outcome': oname, 'feature': fname, 'n': len(sub), 'prevalence_or_mean': round(statistics.mean(x), 3),
                        'spearman': None if spearman(x, y) is None else round(spearman(x, y), 3), 'spearman_ci95': boot(spearman, x, y),
                        'top_minus_bottom_third': round(tertile_diff(x, y), 3), 'diff_ci95': boot(tertile_diff, x, y)})
    a.out.mkdir(parents=True, exist_ok=True)
    with open(a.out / 'topology_outcomes.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(res[0]) if res else ['outcome']); w.writeheader(); w.writerows(res)
    L = ['# Workflow topology and outcomes', '', f'{len(rows)} coded papers joined to {Path(a.manifest).name}. Associations, not effects; '
         f'{len(res)} comparisons reported, none corrected.', '', '| Outcome | Feature | n | Prevalence or mean | Spearman [95% CI] | Top minus bottom third [95% CI] |', '|:--|:--|:--|:--|:--|:--|']
    for r in res:
        L.append(f"| {r['outcome']} | {r['feature']} | {r['n']} | {r['prevalence_or_mean']} | {r['spearman']} {r['spearman_ci95']} | {r['top_minus_bottom_third']} {r['diff_ci95']} |")
    (a.out / 'topology_outcomes.md').write_text('\n'.join(L) + '\n')
    print(f'{len(res)} comparisons on {len(rows)} papers; {a.out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
