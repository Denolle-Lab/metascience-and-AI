"""Workflow features against outcome metrics (roadmap Phase 0/1 descriptive analysis).

Inputs
  private/analysis/codings/api/calc1/*.json      model coding of each eligible paper with full text (codebook 1.5.0)
  private/data/roadmap/derived/gold/metrics.json impact, novelty, breadth proxies for the 600 preselected papers

Features (per paper, from the final_paper sequence of the coding)
  numeric   steps, distinct nodes, distinct modes, revisits, returns after failure, imports, import fields,
            novelty claims, kinds of V check performed here
  binary    entry state, each node used, each mode used, decisive mode, composition, gates,
            V full, triangulation, outcome contradicted, any return after failure

Outcomes
  impact    cnp (OpenAlex citation normalized percentile), fwci
  novelty   novelty_pair (-log10 of 1 + prior works sharing the paper's leading topic pair)
  breadth   breadth_refs (share of references outside geoscience); breadth_citers (share of citers outside
            geoscience, only where at least 10 non-self citers)
  advance   not measured (human ratings pending)

Statistics: Spearman rank correlation (binary features as 0/1), 95% bootstrap interval (2000 resamples over
papers), two-sided permutation p (5000), Benjamini-Hochberg q over all feature-outcome tests. Descriptive and
exploratory: no causal reading, many tests, coded by one model.

Outputs  private/data/roadmap/derived/outcomes/{outcomes.json, OUTCOMES.md}
Run:     python tools/roadmap/g17_outcomes.py
"""
import json
from collections import Counter
from pathlib import Path
import numpy as np
from common import ROOT, DERIVED, write_json, log, read_json
from check_coding import validate, v_status

API = ROOT / 'private' / 'analysis' / 'codings' / 'api' / 'calc1'
OUT = DERIVED / 'outcomes'
NODES = {'N': 'new capability', 'E': 'explore', 'O': 'observe', 'I': 'infer', 'Q': 'question', 'H': 'hypothesize',
         'S': 'simulate or derive', 'D': 'design', 'F': 'find or set conditions', 'C': 'compare', 'V': 'vary and replicate',
         'X': 'exclude', 'K': 'keep', 'P': 'protect', 'R': 'refine'}
OUTCOMES = {'cnp': 'impact: citation percentile', 'fwci': 'impact: field-weighted citations',
            'novelty_pair': 'novelty: rare topic pair', 'breadth_refs': 'breadth: references outside geoscience',
            'breadth_citers': 'breadth: citers outside geoscience (>=10 citers)'}
rng = np.random.default_rng(2026)


def rank(x):
    x = np.asarray(x, float)
    order = x.argsort(kind='mergesort')
    r = np.empty(len(x)); r[order] = np.arange(len(x))
    for v in np.unique(x):            # average ranks for ties
        m = x == v
        if m.sum() > 1:
            r[m] = r[m].mean()
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    if ra.std() == 0 or rb.std() == 0:
        return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])


def test(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    rho = spearman(a, b)
    if np.isnan(rho):
        return None
    n = len(a)
    bs = []
    for _ in range(2000):
        i = rng.integers(0, n, n)
        v = spearman(a[i], b[i])
        if not np.isnan(v):
            bs.append(v)
    ra, rb = rank(a), rank(b)
    ra, rb = (ra - ra.mean()) / ra.std(), (rb - rb.mean()) / rb.std()
    obs = abs((ra * rb).mean())
    perm = np.array([abs((ra * rng.permutation(rb)).mean()) for _ in range(5000)])
    p = (1 + (perm >= obs - 1e-12).sum()) / 5001
    return {'rho': round(rho, 3), 'ci': [round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)],
            'p': round(float(p), 4), 'n': n}


def bh(ps):
    ps = np.asarray(ps); m = len(ps); o = ps.argsort()
    q = np.empty(m); prev = 1.0
    for k, i in enumerate(o[::-1]):
        prev = min(prev, ps[i] * m / (m - k)); q[i] = prev
    return q


def features(c):
    steps = next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps']
    nodes, modes = [s['node'] for s in steps], [s['mode'] for s in steps]
    seen, rev = set(), 0
    for x in nodes:
        rev += x in seen; seen.add(x)
    v = v_status(c)
    f = {'num:steps': len(steps), 'num:distinct nodes': len(set(nodes)), 'num:distinct modes': len(set(modes)),
         'num:revisits': rev, 'num:returns after failure': sum(s.get('move') == 'return_after_failure' for s in steps),
         'num:imports': len(c.get('imports', [])), 'num:import fields': len({i.get('field') for i in c.get('imports', [])}),
         'num:novelty claims': len(c.get('novelty_claims', [])), 'num:V check kinds': len(v['kinds']),
         'bin:any return after failure': any(s.get('move') == 'return_after_failure' for s in steps),
         'bin:V full': v['v'] == 'full', 'bin:triangulation': v['triangulation'],
         'bin:claim gate yes': c['gates'].get('claim') == 'yes', 'bin:action gate yes or partly': c['gates'].get('action') in ('yes', 'partly'),
         'bin:outcome contradicted': c['end'].get('outcome') == 'contradicted'}
    for n, name in NODES.items():
        f[f'bin:node {n} {name}'] = n in nodes
    for m in sorted(set(modes)):
        f[f'bin:mode {m}'] = True
    f[f"bin:entry {c['entry']['state']}"] = True
    f[f"bin:decisive {c['decisive_move']['mode']}"] = True
    f[f"bin:composition {c['composition']}"] = True
    return f


def main():
    met = {('g22_' + m['id']): m for m in read_json(DERIVED / 'gold' / 'metrics.json')}
    codes = {}
    for p in sorted(API.glob('*.json')):
        try:
            c = json.loads(p.read_text())
        except Exception:
            continue
        if not validate(c) and c['key'] in met:
            codes[c['key']] = c
    keys = sorted(codes)
    F = {k: features(codes[k]) for k in keys}
    names = sorted({n for f in F.values() for n in f})
    # binary features absent from a paper are False; keep features present in at least 10 and at most n-10 papers
    tests, rows = [], []
    for name in names:
        vals = [float(F[k].get(name, False)) for k in keys]
        if name.startswith('bin:') and not (10 <= sum(vals) <= len(vals) - 10):
            continue
        for o in OUTCOMES:
            ks = [k for k in keys if met[k].get(o) is not None and (o != 'breadth_citers' or (met[k].get('n_citers_noself') or 0) >= 10)]
            r = test([float(F[k].get(name, False)) for k in ks], [met[k][o] for k in ks])
            if r:
                r.update({'feature': name[4:], 'type': name[:3], 'outcome': o,
                          'prevalence': round(sum(F[k].get(name, False) for k in ks) / len(ks), 2) if name.startswith('bin:') else None})
                rows.append(r)
    q = bh([r['p'] for r in rows])
    for r, qq in zip(rows, q):
        r['q'] = round(float(qq), 3)
    # outcome distributions and their mutual correlations
    desc = {o: {'n': sum(met[k].get(o) is not None for k in keys),
                'median': round(float(np.median([met[k][o] for k in keys if met[k].get(o) is not None])), 3)} for o in OUTCOMES}
    inter = {f'{a}~{b}': test(*zip(*[(met[k][a], met[k][b]) for k in keys if met[k].get(a) is not None and met[k].get(b) is not None]))['rho']
             for i, a in enumerate(OUTCOMES) for b in list(OUTCOMES)[i + 1:]}
    sig = sorted([r for r in rows if r['q'] < 0.1], key=lambda r: r['q'])
    res = {'papers': len(keys), 'tests': len(rows), 'q_below_0.1': len(sig), 'outcome_summary': desc, 'outcome_intercorrelation': inter,
           'advance': 'not measured: human blind ratings pending', 'rows': rows,
           'note': 'Spearman rho, 95% bootstrap CI over papers, permutation p, Benjamini-Hochberg q over all tests; exploratory'}
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / 'outcomes.json', res, ['private/analysis/codings/api/calc1', 'derived/gold/metrics.json'])

    md = ['# Workflow features against outcome metrics', '',
          f"{len(keys)} papers coded under codebook 1.5.0 (first calculation). {len(rows)} feature-outcome tests; "
          f"{len(sig)} with Benjamini-Hochberg q < 0.1. Exploratory: one model coder, open-access-leaning sample, citations at about four years. "
          'Advance is not measured yet.', '', '## Outcomes', '', '| Outcome | Papers | Median |', '|:--|--:|--:|']
    md += [f"| {OUTCOMES[o]} | {d['n']} | {d['median']} |" for o, d in desc.items()]
    md += ['', 'Rank correlations among outcomes: ' + '; '.join(f'{k} {v}' for k, v in inter.items()), '']
    md += ['## Associations with q < 0.1', '', '| Feature | Outcome | rho [95% CI] | n | q | Share of papers |', '|:--|:--|:--|--:|--:|--:|']
    md += [f"| {r['feature']} | {OUTCOMES[r['outcome']]} | {r['rho']} [{r['ci'][0]}, {r['ci'][1]}] | {r['n']} | {r['q']} | {r['prevalence'] if r['prevalence'] is not None else 'numeric'} |" for r in sig]
    md += ['', '## Strongest association per outcome (any q)', '', '| Outcome | Feature | rho [95% CI] | q |', '|:--|:--|:--|--:|']
    for o in OUTCOMES:
        rr = sorted([r for r in rows if r['outcome'] == o], key=lambda r: -abs(r['rho']))[:5]
        md += [f"| {OUTCOMES[o]} | {r['feature']} | {r['rho']} [{r['ci'][0]}, {r['ci'][1]}] | {r['q']} |" for r in rr]
    (OUT / 'OUTCOMES.md').write_text('\n'.join(md) + '\n')
    log('g17_outcomes.py', 'workflow features against outcome metrics', len(keys), f'{len(rows)} tests, {len(sig)} q<0.1')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
