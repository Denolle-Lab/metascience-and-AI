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

Runs (added October 27, 2026, after the round-2 confirmatory test; the functions features, test, spearman, rank and bh
that g23_confirmatory.py imports are unchanged from the frozen version, public commit b4369fe)
  round 1 (top-level keys, as before)   all valid round-1 (calc1) codings now: the 233 of the first analysis plus the
          top-up papers (tools/roadmap/rounds.py). Same features, filter, statistics and seed (default_rng(2026)) as the
          run the plan was frozen from, so the rows are the exploratory analysis at the current n.
  round1_hypotheses   the 15 frozen g17 hypotheses (H01-H15, preregistration/round2-confirmatory.json): rho at the
          first analysis (233, from the plan), at the current round-1 n (these rows), on the top-up papers alone (g17
          test(), generator default_rng(2028)), in round 2 (read from derived/confirmatory/results.json, not recomputed),
          and pooled within round (below).
  pooled_round_stratified   both rounds (round 2: tag r2, metrics derived/r2/metrics.json), round as a stratum. Ranks are
          computed within each round, centred within round, and combined (g20 within_rho): rho_within is the Pearson
          correlation of within-round ranks pooled over rounds, so a level difference between rounds adds nothing.
          Interval: 2000 bootstrap resamples within round, ranks recomputed in each resample. p: two-sided, 5000
          permutations of the outcome within round. Generator per test: g20 gen('g17 pooled|<feature>|<outcome>').
          Per-round rho (plain Spearman) beside it. Same binary filter (10 to n - 10 papers, over both rounds), same
          citer rule. BH q over the pooled tests only. Descriptive: the pooled run is not a confirmatory test (that
          is g23 on round 2 alone).

Outputs  private/data/roadmap/derived/outcomes/{outcomes.json, OUTCOMES.md}
Run:     python tools/roadmap/g17_outcomes.py
"""
import json
from collections import Counter
from pathlib import Path
import numpy as np
from common import ROOT, PRIVATE, DERIVED, write_json, log, read_json
from check_coding import validate, v_status
import rounds

API = PRIVATE / 'analysis' / 'codings' / 'api' / 'calc1'
OUT = DERIVED / 'outcomes'
PLAN = ROOT / 'preregistration' / 'round2-confirmatory.json'
CONF = DERIVED / 'confirmatory' / 'results.json'
NBOOT, NPERM = 2000, 5000
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


# ---------- added October 27, 2026: pooled run with round as a stratum, and the 15 frozen hypotheses ----------
def outcome_keys(keys, met, o):
    """Papers with outcome o, under the citer rule for breadth_citers (as in main)."""
    return [k for k in keys if met[k].get(o) is not None and (o != 'breadth_citers' or (met[k].get('n_citers_noself') or 0) >= 10)]


def within_round_test(f, o, s, name):
    """Spearman within round, combined: ranks inside each round, centred within round (g20.within_rho); stratified
    bootstrap interval (ranks recomputed per resample) and two-sided permutation p with outcomes shuffled within round."""
    import g20_topics_journals as g20
    rng_ = g20.gen(name)
    f, o = np.asarray(f, float), np.asarray(o, float)
    labels, s = np.unique(np.asarray(s), return_inverse=True)
    groups = [np.flatnonzero(s == j) for j in range(len(labels))]

    def ranked(x, gs):
        r = np.empty(len(x))
        for gi in gs:
            r[gi] = g20.rank(x[gi])
        return r
    rho, a, b, d = g20.within_rho(ranked(f, groups), ranked(o, groups), s)
    if np.isnan(rho):
        return None
    perm = np.empty(NPERM)
    idx = np.arange(len(s))
    for t in range(NPERM):
        for gi in groups:
            idx[gi] = gi[rng_.permutation(len(gi))]
        perm[t] = abs((a * b[idx]).sum() / d)
    p = (1 + (perm >= abs(rho) - 1e-12).sum()) / (NPERM + 1)
    bs = []
    for _ in range(NBOOT):
        pick = [gi[rng_.integers(0, len(gi), len(gi))] for gi in groups]
        i = np.concatenate(pick)
        ss = np.concatenate([np.full(len(x), j) for j, x in enumerate(pick)])
        gs = [np.flatnonzero(ss == j) for j in range(len(pick))]
        v = g20.within_rho(ranked(f[i], gs), ranked(o[i], gs), ss)[0]
        if not np.isnan(v):
            bs.append(v)
    by = {}
    for lab, gi in zip(labels, groups):
        v = spearman(f[gi], o[gi])
        by[str(lab)] = {'rho': None if np.isnan(v) else round(v, 3), 'n': len(gi)}
    return {'rho_within': round(rho, 3), 'ci': [round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)],
            'p': round(float(p), 4), 'n': len(f), 'by_round': by}


def pooled_run(codes1, met1):
    """Both rounds, round as a stratum (see the module docstring)."""
    met2 = rounds.metrics('r2')
    codes2 = {k: c for k, c in rounds.valid('r2').items() if k in met2}
    P = {('round1', k): (codes1[k], met1[k]) for k in codes1} | {('round2', k): (codes2[k], met2[k]) for k in codes2}
    keys = sorted(P)
    F = {x: features(P[x][0]) for x in keys}
    M = {x: P[x][1] for x in keys}
    names = sorted({n for f in F.values() for n in f})
    rows = []
    for name in names:
        vals = [float(F[x].get(name, False)) for x in keys]
        if name.startswith('bin:') and not (10 <= sum(vals) <= len(vals) - 10):
            continue
        for o in OUTCOMES:
            ks = outcome_keys(keys, M, o)
            r = within_round_test([float(F[x].get(name, False)) for x in ks], [M[x][o] for x in ks], [x[0] for x in ks],
                                  f'g17 pooled|{name}|{o}')
            if r:
                r.update({'feature': name[4:], 'type': name[:3], 'outcome': o,
                          'prevalence': round(sum(F[x].get(name, False) for x in ks) / len(ks), 2) if name.startswith('bin:') else None})
                rows.append(r)
    for r, qq in zip(rows, bh([r['p'] for r in rows])):
        r['q'] = round(float(qq), 3)
    sig = sorted([r for r in rows if r['q'] < 0.1], key=lambda r: r['q'])
    return {'papers': {'round1': len(codes1), 'round2': len(codes2), 'total': len(keys)}, 'tests': len(rows), 'q_below_0.1': len(sig),
            'outcome_median_by_round': {o: {rd: round(float(np.median([M[x][o] for x in outcome_keys(keys, M, o) if x[0] == rd])), 3)
                                            for rd in ('round1', 'round2') if any(x[0] == rd for x in outcome_keys(keys, M, o))} for o in OUTCOMES},
            'rows': rows,
            'note': 'rho_within: Spearman with ranks inside each round, centred within round and pooled (g20.within_rho); 95% '
                    'interval from 2000 bootstrap resamples within round; p from 5000 permutations of the outcome within round; '
                    'BH q over these pooled tests; descriptive, not confirmatory'}


def round1_hypotheses(rows, codes, met, F, top, pooled):
    """H01-H15 of the frozen plan at 233 (plan), at the current round-1 n, on the top-up alone, in round 2, and pooled."""
    global rng
    if not PLAN.is_file():
        return None
    plan = json.loads(PLAN.read_text())
    conf = {r['id']: r for r in read_json(CONF)['rows']} if CONF.is_file() else {}
    now = {(f"{r['type']}:{r['feature']}", r['outcome']): r for r in rows}
    pool = {(f"{r['type']}:{r['feature']}", r['outcome']): r for r in pooled['rows']}
    saved, rng = rng, np.random.default_rng(2028)
    out = []
    for h in [h for h in plan['hypotheses'] if h['source'] == 'g17']:
        key, o, sgn = (h['feature'], h['outcome']), h['outcome'], h['predicted_sign']
        n1 = now.get(key)
        ks = outcome_keys(sorted(top), met, o)
        tt = test([float(F[k].get(h['feature'], False)) for k in ks], [met[k][o] for k in ks]) if ks else None
        c = conf.get(h['id'], {})
        pr = pool.get(key)
        same = lambda v: None if v is None else bool(np.sign(v) == sgn)
        out.append({'id': h['id'], 'feature': h['feature'], 'outcome': o, 'predicted_sign': sgn,
                    'round1_first_analysis': h['round1'],
                    'round1_now': {k: n1[k] for k in ('rho', 'ci', 'p', 'q', 'n')} | {'same_sign': same(n1['rho'])} if n1 else None,
                    'round1_top_up': (tt | {'same_sign': same(tt['rho'])}) if tt else None,
                    'round2': {k: c.get(k) for k in ('rho', 'ci', 'p', 'q', 'n', 'verdict')} if c else None,
                    'pooled_within_round': {k: pr[k] for k in ('rho_within', 'ci', 'p', 'q', 'n', 'by_round')} | {'same_sign': same(pr['rho_within'])} if pr else None})
    rng = saved
    return {'rows': out,
            'round1_now_q_below_0.1': sum(bool(r['round1_now'] and r['round1_now']['q'] < 0.1) for r in out),
            'round1_now_same_sign': sum(bool(r['round1_now'] and r['round1_now']['same_sign']) for r in out),
            'top_up_same_sign': sum(bool(r['round1_top_up'] and r['round1_top_up']['same_sign']) for r in out),
            'top_up_p_below_0.05_same_sign': sum(bool(r['round1_top_up'] and r['round1_top_up']['same_sign'] and r['round1_top_up']['p'] < 0.05) for r in out),
            'pooled_q_below_0.1_same_sign': sum(bool(r['pooled_within_round'] and r['pooled_within_round']['same_sign'] and r['pooled_within_round']['q'] < 0.1) for r in out),
            'round2_verdicts': dict(Counter(r['round2']['verdict'] for r in out if r['round2'])),
            'note': 'round1_first_analysis from the frozen plan (233 papers); round1_now = the round-1 rows above (first analysis plus '
                    'top-up, so not independent of the 233); round1_top_up = top-up papers only, g17 test() with default_rng(2028), '
                    'not part of any BH family; round2 read from derived/confirmatory/results.json (g23 test, not rerun)'}


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
    first, top = rounds.round1_split(keys)
    pooled = pooled_run(codes, met)
    hyp = round1_hypotheses(rows, codes, met, F, top, pooled)
    res = {'papers': len(keys), 'tests': len(rows), 'q_below_0.1': len(sig), 'outcome_summary': desc, 'outcome_intercorrelation': inter,
           'advance': 'not measured: human blind ratings pending', 'rows': rows,
           'note': 'Spearman rho, 95% bootstrap CI over papers, permutation p, Benjamini-Hochberg q over all tests; exploratory',
           'round1_papers': {'first_analysis': len(first), 'top_up': len(top), 'rule': 'tools/roadmap/rounds.py round1_split'},
           'round1_hypotheses': hyp, 'pooled_round_stratified': pooled}
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / 'outcomes.json', res, ['private/analysis/codings/api/calc1', 'private/analysis/codings/api/r2', 'derived/gold/metrics.json',
                                            'derived/r2/metrics.json', 'private/analysis/codings/api/state.json',
                                            'preregistration/round2-confirmatory.json', 'derived/confirmatory/results.json'])

    md = ['# Workflow features against outcome metrics', '',
          f"Round 1: {len(keys)} papers coded under codebook 1.5.0 ({len(first)} in the first analysis, {len(top)} top-up). "
          f"{len(rows)} feature-outcome tests; {len(sig)} with Benjamini-Hochberg q < 0.1. Exploratory: one model coder, "
          'open-access-leaning sample, citations at about four years. Advance is not measured yet. '
          'The confirmatory test of the 15 associations found at 233 papers is round 2 (g23_confirmatory.py); '
          'the pooled run below is descriptive.', '', '## Outcomes, round 1', '', '| Outcome | Papers | Median |', '|:--|--:|--:|']
    md += [f"| {OUTCOMES[o]} | {d['n']} | {d['median']} |" for o, d in desc.items()]
    md += ['', 'Rank correlations among outcomes: ' + '; '.join(f'{k} {v}' for k, v in inter.items()), '']
    md += ['## Associations with q < 0.1, round 1', '', '| Feature | Outcome | rho [95% CI] | n | q | Share of papers |', '|:--|:--|:--|--:|--:|--:|']
    md += [f"| {r['feature']} | {OUTCOMES[r['outcome']]} | {r['rho']} [{r['ci'][0]}, {r['ci'][1]}] | {r['n']} | {r['q']} | {r['prevalence'] if r['prevalence'] is not None else 'numeric'} |" for r in sig]
    md += ['', '## Strongest association per outcome (any q), round 1', '', '| Outcome | Feature | rho [95% CI] | q |', '|:--|:--|:--|--:|']
    for o in OUTCOMES:
        rr = sorted([r for r in rows if r['outcome'] == o], key=lambda r: -abs(r['rho']))[:5]
        md += [f"| {OUTCOMES[o]} | {r['feature']} | {r['rho']} [{r['ci'][0]}, {r['ci'][1]}] | {r['q']} |" for r in rr]
    if hyp:
        f3 = lambda d, k='rho': f"{d[k]} [{d['ci'][0]}, {d['ci'][1]}]" if d else 'n/a'
        md += ['', '## The 15 frozen round-1 associations at each stage', '',
               f"rho [95% bootstrap CI]. First analysis: {hyp['rows'][0]['round1_first_analysis']['n']} papers (the plan). "
               f"Round 1 now: {len(keys)} papers ({len(first)} + {len(top)} top-up; not independent of the first analysis). "
               f"Top-up alone: {len(top)} papers, new to the analysis. Round 2: the confirmatory test (g23, read, not rerun). "
               'Pooled: within-round ranks, round as a stratum, BH q over the pooled family.', '',
               '| id | Feature | Outcome | First analysis | Round 1 now (q) | Top-up alone (p) | Round 2 (verdict) | Pooled within round (q) |',
               '|:--|:--|:--|:--|:--|:--|:--|:--|']
        for r in hyp['rows']:
            md.append(f"| {r['id']} | {r['feature'][4:]} | {r['outcome']} | {f3(r['round1_first_analysis'])} | "
                      f"{f3(r['round1_now'])} ({r['round1_now']['q'] if r['round1_now'] else ''}) | "
                      f"{f3(r['round1_top_up'])} ({r['round1_top_up']['p'] if r['round1_top_up'] else ''}) | "
                      f"{f3(r['round2'])} ({r['round2']['verdict'] if r['round2'] else ''}) | "
                      f"{f3(r['pooled_within_round'], 'rho_within')} ({r['pooled_within_round']['q'] if r['pooled_within_round'] else ''}) |")
        md += ['', f"Round 1 now: {hyp['round1_now_q_below_0.1']} of 15 at q < 0.1, {hyp['round1_now_same_sign']} with the round-1 sign. "
               f"Top-up alone: {hyp['top_up_same_sign']} with the same sign, {hyp['top_up_p_below_0.05_same_sign']} also at p < 0.05. "
               f"Pooled: {hyp['pooled_q_below_0.1_same_sign']} at q < 0.1 with the same sign. Round 2: {hyp['round2_verdicts']}."]
    pr = pooled
    psig = sorted([r for r in pr['rows'] if r['q'] < 0.1], key=lambda r: r['q'])
    md += ['', '## Pooled, round as a stratum (descriptive)', '',
           f"{pr['papers']['total']} papers (round 1 {pr['papers']['round1']}, round 2 {pr['papers']['round2']}); {pr['tests']} tests; "
           f"{pr['q_below_0.1']} with BH q < 0.1. rho_within = Spearman on ranks computed inside each round, centred within round "
           'and pooled; interval from 2000 bootstrap resamples within round; p from 5000 permutations of the outcome within round.', '',
           '| Outcome | Round 1 median | Round 2 median |', '|:--|--:|--:|']
    md += [f"| {OUTCOMES[o]} | {v.get('round1')} | {v.get('round2')} |" for o, v in pr['outcome_median_by_round'].items()]
    md += ['', '| Feature | Outcome | rho_within [95% CI] | rho round 1 | rho round 2 | n | q |', '|:--|:--|:--|--:|--:|--:|--:|']
    md += [f"| {r['feature']} | {OUTCOMES[r['outcome']]} | {r['rho_within']} [{r['ci'][0]}, {r['ci'][1]}] | "
           f"{r['by_round'].get('round1', {}).get('rho')} | {r['by_round'].get('round2', {}).get('rho')} | {r['n']} | {r['q']} |" for r in psig]
    (OUT / 'OUTCOMES.md').write_text('\n'.join(md) + '\n')
    log('g17_outcomes.py', 'workflow features against outcome metrics, round 1 and pooled by round', len(keys) + pooled['papers']['round2'],
        f"round 1 {len(keys)}: {len(rows)} tests, {len(sig)} q<0.1; pooled {pooled['papers']['total']}: {pooled['tests']} tests, {pooled['q_below_0.1']} q<0.1")
    print('\n'.join(md))


if __name__ == '__main__':
    main()
