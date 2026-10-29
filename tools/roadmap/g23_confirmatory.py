"""Round 2 as a confirmatory test of the round-1 associations: freeze the plan before round-2 codings exist, then test.

Decided by the PI on October 27, 2026: round 1 is exploratory; round 2 tests its associations; both rounds are also
reported pooled for description, with round as a stratum.

freeze  Reads the round-1 results and writes the plan, which is public and committed before any round-2 coding exists
        (the script refuses to freeze if private/analysis/codings/api/r2/ holds a coding file).
        Hypotheses
          H01-H15  the g17 feature-outcome associations with q < 0.1 in round 1 (Spearman rho). Predicted: same sign.
          H16-H43  the g20 field and venue associations with q < 0.1 in round 1 (workflow feature against OpenAlex
                   subfield or journal family). Predicted direction:
                     binary       the round-1 leading group (largest |rate minus rest| among named groups) has a
                                  rate difference of the same sign in round 2;
                     count        group medians in round 2 rank the shared named groups in the same order as round 1
                                  (Spearman correlation of group medians > 0);
                     categorical  no direction; association only.
        Rule     one family of 43 tests; Benjamini-Hochberg q over the 43 round-2 p values. A hypothesis is confirmed
                 when q < 0.1 and the predicted direction holds; reversed when q < 0.1 and the direction is opposite;
                 otherwise not confirmed. Effect sizes are reported with 95% bootstrap intervals for every hypothesis.
        Data     round-2 papers with a valid coding (tools/check_coding.py validate(), tag r2, codebook 1.5.0) and
                 metrics in derived/r2/metrics.json; no other exclusion. Groups are the round-1 named groups; a
                 round-2 paper in any other subfield or family goes to 'pooled small groups'. Same features (g17
                 features()), same outcomes and citer rule (g17), same statistics code (g17 test(); g20 assoc() and
                 numeric_by_group()), 2000 bootstrap resamples and 5000 permutations; g17 tests draw from
                 np.random.default_rng(2027), g20 tests from g20's per-test generator named 'conf|<id>'.
        Secondary (reported, not part of the rule): each H01-H15 estimate within subfield and within journal family
                 (g20 stratified()); the pooled descriptive analysis of both rounds with round as a stratum.
test    Runs the plan on round 2 and writes the verdict per hypothesis.

Inputs   derived/outcomes/outcomes.json (g17, round 1), derived/topics/topics_journals.json (g20, round 1),
         derived/r2/metrics.json, private/analysis/codings/api/r2/*.json (test only)
Outputs  preregistration/round2-confirmatory.{json,md} (public, freeze);
         derived/confirmatory/{results.json, CONFIRMATORY.md} (test)
Run:     python tools/roadmap/g23_confirmatory.py freeze      (once, before round-2 codings exist; then commit and push)
         python tools/roadmap/g23_confirmatory.py test        (after round 2 is collected)
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from common import ROOT, PRIVATE, DERIVED, TODAY, read_json, write_json, log
from check_coding import validate
import g17_outcomes as g17
import g20_topics_journals as g20

PLAN = ROOT / 'preregistration' / 'round2-confirmatory.json'
R2 = PRIVATE / 'analysis' / 'codings' / 'api' / 'r2'
OUT = DERIVED / 'confirmatory'
Q, SEED = 0.1, 2027
INPUTS = ['tools/roadmap/g17_outcomes.py', 'tools/roadmap/g20_topics_journals.py', 'tools/roadmap/g23_confirmatory.py',
          'tools/check_coding.py', 'agents/coder/CODEBOOK.md']


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def r2_codings() -> list[Path]:
    return sorted(R2.glob('g22_*.json')) if R2.is_dir() else []


def named(groups: dict) -> list[str]:
    return [g for g in groups if g != g20.POOLED]


def freeze() -> None:
    if r2_codings():
        sys.exit(f'refusing to freeze: {len(r2_codings())} round-2 coding files already exist in {R2}')
    o = read_json(DERIVED / 'outcomes' / 'outcomes.json')
    t = read_json(DERIVED / 'topics' / 'topics_journals.json')
    hyp = []
    for r in sorted([r for r in o['rows'] if r['q'] < Q], key=lambda r: r['q']):
        hyp.append({'source': 'g17', 'feature': f"{r['type']}:{r['feature']}", 'outcome': r['outcome'],
                    'round1': {k: r[k] for k in ('rho', 'ci', 'p', 'q', 'n')}, 'predicted_sign': int(np.sign(r['rho']))})
    groupings = {v: named(t['workflows']['groupings'][v]['groups']) for v in ('subfield', 'family')}
    for r in sorted([r for r in t['workflows']['rows'] if r['q'] < Q], key=lambda r: (r['grouping'], r['kind'], r['feature'])):
        h = {'source': 'g20', 'grouping': r['grouping'], 'feature': r['feature'], 'kind': r['kind'],
             'round1': {k: r.get(k) for k in ('cramers_v_bc', 'v_bc_ci', 'epsilon2', 'epsilon2_ci', 'p', 'q', 'n') if k in r}}
        if r['kind'] == 'binary':
            g = {k: v for k, v in r['groups'].items() if k != g20.POOLED and v.get('diff_vs_rest') is not None}
            lead = max(g, key=lambda k: abs(g[k]['diff_vs_rest']))
            h['predicted'] = {'leading_group': lead, 'sign_of_rate_minus_rest': int(np.sign(g[lead]['diff_vs_rest'])),
                              'round1_rate_minus_rest': g[lead]['diff_vs_rest']}
        elif r['kind'] == 'count':
            h['predicted'] = {'round1_group_medians': {k: v['median'] for k, v in r['groups'].items() if k != g20.POOLED},
                              'rule': 'Spearman correlation of round-1 and round-2 group medians over shared named groups > 0'}
        hyp.append(h)
    for i, h in enumerate(hyp, 1):
        h['id'] = f'H{i:02d}'
    plan = {'frozen': TODAY, 'decided_by': 'Marine Denolle (PI), October 27, 2026',
            'design': 'round 1 exploratory; round 2 confirmatory for the associations below; both rounds also pooled for '
                      'description with round as a stratum',
            'family_size': len(hyp), 'q_threshold': Q, 'seed': SEED, 'groupings': groupings,
            'round2_codings_at_freeze': 0, 'rule': __doc__.split('test    ')[0].split('freeze  ')[1].strip(),
            'inputs_sha256': {p: sha(ROOT / p) for p in INPUTS}
                             | {'derived/outcomes/outcomes.json': sha(DERIVED / 'outcomes' / 'outcomes.json'),
                                'derived/topics/topics_journals.json': sha(DERIVED / 'topics' / 'topics_journals.json')},
            'hypotheses': hyp}
    PLAN.parent.mkdir(parents=True, exist_ok=True)
    PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + '\n')
    md = ['# Round 2: confirmatory test of the round-1 associations', '',
          f'Frozen {TODAY}, before any round-2 coding existed; decided by the PI on October 27, 2026. '
          f'Machine-readable plan: `round2-confirmatory.json`; code: `tools/roadmap/g23_confirmatory.py` (`test`).', '',
          '- Round 1 (233 coded papers) is exploratory. Round 2 tests the associations below as one family of '
          f'{len(hyp)} tests, Benjamini-Hochberg q < {Q}, with the predicted direction.',
          '- Both rounds are also reported pooled for description, with round as a stratum. That analysis is not part of this test.',
          '- Data, groups, features, statistics and seed are fixed in the json `rule` field.', '',
          '| id | source | association | round 1 | predicted |', '|:--|:--|:--|:--|:--|']
    for h in hyp:
        if h['source'] == 'g17':
            md.append(f"| {h['id']} | g17 | {h['feature']} vs {h['outcome']} | rho {h['round1']['rho']}, q {h['round1']['q']} | "
                      f"{'positive' if h['predicted_sign'] > 0 else 'negative'} |")
        else:
            eff = h['round1'].get('cramers_v_bc', h['round1'].get('epsilon2'))
            pred = (f"{h['predicted']['leading_group']} {'above' if h['predicted']['sign_of_rate_minus_rest'] > 0 else 'below'} the rest"
                    if h['kind'] == 'binary' else 'same order of group medians' if h['kind'] == 'count' else 'association only')
            md.append(f"| {h['id']} | g20 | {h['feature']} by {h['grouping']} ({h['kind']}) | effect {eff}, q {h['round1']['q']} | {pred} |")
    PLAN.with_suffix('.md').write_text('\n'.join(md) + '\n')
    log('g23_confirmatory.py freeze', 'round-2 confirmatory plan frozen', len(hyp), f'{len(hyp)} hypotheses')
    print(f'{PLAN.relative_to(ROOT)}: {len(hyp)} hypotheses frozen; commit and push it before round-2 codings arrive')


def test() -> None:
    plan = json.loads(PLAN.read_text())
    met = {'g22_' + m['id']: m for m in read_json(DERIVED / 'r2' / 'metrics.json')}
    codes = {}
    for p in r2_codings():
        c = json.loads(p.read_text())
        if not validate(c) and c['key'] in met:
            codes[c['key']] = c
    keys = sorted(codes)
    if not keys:
        sys.exit('no valid round-2 codings')
    F = {k: g17.features(codes[k]) for k in keys}
    g17.rng = np.random.default_rng(SEED)
    A = {k: {'subfield': met[k].get('subfield') or 'unknown', 'family': g20.family(met[k])} for k in keys}
    rows = []
    for h in plan['hypotheses']:
        r = {'id': h['id']}
        if h['source'] == 'g17':
            kind, name = h['feature'].split(':', 1)
            o = h['outcome']
            ks = [k for k in keys if met[k].get(o) is not None and (o != 'breadth_citers' or (met[k].get('n_citers_noself') or 0) >= 10)]
            res = g17.test([float(F[k].get(f'{kind}:{name}', False)) for k in ks], [met[k][o] for k in ks])
            r.update(res or {'rho': None, 'p': 1.0, 'n': len(ks)})
            r['direction_ok'] = res is not None and np.sign(res['rho']) == h['predicted_sign']
            for var in ('subfield', 'family'):
                if res:
                    r[f'within_{var}'] = g20.stratified([float(F[k].get(f'{kind}:{name}', False)) for k in ks], [met[k][o] for k in ks],
                                                        [A[k][var] for k in ks], f'conf|{h["id"]}|{var}')
        else:
            var, groups = h['grouping'], set(plan['groupings'][h['grouping']])
            g = [A[k][var] if A[k][var] in groups else g20.POOLED for k in keys]
            nm = h['feature']
            if h['kind'] == 'binary':
                res = g20.assoc(g, [bool(F[k].get(f'bin:{nm}', False)) for k in keys], f'conf|{h["id"]}')
                lead = res['groups'].get(h['predicted']['leading_group'], {})
                d = lead.get('diff_vs_rest')
                r['direction_ok'] = d is not None and np.sign(d) == h['predicted']['sign_of_rate_minus_rest']
                r['leading_group_round2'] = lead
            elif h['kind'] == 'count':
                res = g20.numeric_by_group(g, [float(F[k].get(f'num:{nm}', 0)) for k in keys], f'conf|{h["id"]}')
                m1 = h['predicted']['round1_group_medians']
                shared = [x for x in m1 if x in res['groups']]
                rc = g17.spearman([m1[x] for x in shared], [res['groups'][x]['median'] for x in shared]) if len(shared) >= 3 else float('nan')
                r['direction_ok'] = bool(rc > 0) if not np.isnan(rc) else False
                r['median_order_rho'] = None if np.isnan(rc) else round(rc, 3)
            else:
                whole = nm.split(' ')[0]
                lv = [next((n.split(' ', 1)[1] for n in F[k] if n.startswith(f'bin:{whole} ')), 'none') for k in keys]
                lv, _ = g20.pool_small(lv)
                res = g20.assoc(g, lv, f'conf|{h["id"]}')
                r['direction_ok'] = True
            r.update({k: v for k, v in res.items() if k != 'groups'})
        rows.append(r)
    for r in rows:   # post-freeze fix (serialization only): numpy booleans are not JSON serializable
        r['direction_ok'] = bool(r['direction_ok'])
    for r, q in zip(rows, g17.bh([r['p'] for r in rows])):
        r['q'] = round(float(q), 4)
        r['verdict'] = ('confirmed' if r['q'] < plan['q_threshold'] and r['direction_ok'] else
                        'reversed' if r['q'] < plan['q_threshold'] else 'not confirmed')
    res = {'plan_sha256': sha(PLAN), 'papers': len(keys), 'family_size': len(rows),
           'verdicts': {v: sum(r['verdict'] == v for r in rows) for v in ('confirmed', 'reversed', 'not confirmed')}, 'rows': rows}
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / 'results.json', res, ['preregistration/round2-confirmatory.json', 'derived/r2/metrics.json', 'private/analysis/codings/api/r2'])
    md = ['# Round 2 confirmatory test', '', f"{len(keys)} round-2 papers; {res['verdicts']}", '',
          '| id | verdict | q | effect |', '|:--|:--|--:|:--|']
    md += [f"| {r['id']} | {r['verdict']} | {r['q']} | {r.get('rho', r.get('cramers_v_bc', r.get('epsilon2')))} |" for r in rows]
    (OUT / 'CONFIRMATORY.md').write_text('\n'.join(md) + '\n')
    log('g23_confirmatory.py test', 'round-2 confirmatory test', len(keys), str(res['verdicts']))
    print(res['verdicts'])


if __name__ == '__main__':
    {'freeze': freeze, 'test': test}[sys.argv[1] if len(sys.argv) > 1 else 'freeze']()
