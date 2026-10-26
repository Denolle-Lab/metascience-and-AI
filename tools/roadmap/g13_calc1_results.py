"""First calculation: test-retest agreement on the gold papers and corpus descriptives (roadmap Phase 0).

Inputs
  private/analysis/codings/api/calc1/*.json     first model coding (codebook 1.5.0), eligible papers with full text
  private/analysis/codings/api/gold-r2/*.json   second, independent model coding of the gold papers
  private/data/roadmap/derived/calc1/manifest.jsonl   the 525 eligible papers
  private/data/roadmap/derived/gold/metrics.json      impact, novelty, breadth proxies for the 600 preselected

Outputs
  private/data/roadmap/derived/calc1/results.json   all numbers below, with provenance
  private/data/roadmap/derived/calc1/RESULTS.md     the same, as tables

Run:  python tools/roadmap/g13_calc1_results.py
"""
import json, statistics as st
from collections import Counter
from pathlib import Path
from common import ROOT, DERIVED, write_json, log, read_json
from check_coding import validate, v_status, seq, agree
from g11_human_agreement import alpha_nominal

API = ROOT / 'private' / 'analysis' / 'codings' / 'api'
NODES = list('NEOIQHSDFCVXKPR')


def load(tag):
    out = {}
    for f in sorted((API / tag).glob('*.json')):
        try:
            c = json.loads(f.read_text())
        except Exception:
            continue
        if not validate(c):
            out[c['key']] = c
    return out


def returns(xs):
    seen, n = set(), 0
    for x in xs:
        n += x in seen
        seen.add(x)
    return n


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 3) if xs else None


def share(c: Counter, n):
    return {k: [v, round(v / n, 2)] for k, v in c.most_common()}


def main():
    r1, r2 = load('calc1'), load('gold-r2')
    man = [json.loads(l) for l in (DERIVED / 'calc1' / 'manifest.jsonl').read_text().splitlines()]
    gold = {m['key'] for m in man if m['in_gold']}
    met = {('g22_' + m['id']): m for m in read_json(DERIVED / 'gold' / 'metrics.json')}

    # ---- test-retest on gold papers coded twice ----
    pair = sorted(k for k in r2 if k in r1)
    rows = [agree(r1[k], r2[k]) for k in pair]
    tr = {'papers': len(pair)}
    for f in ['entry_state', 'entry_node', 'outcome', 'decisive_mode']:
        tr[f + '_agree'] = round(sum(r[f] for r in rows) / len(rows), 2)
    for f in ['node_set_jaccard', 'mode_set_jaccard', 'node_seq_similarity', 'mode_seq_similarity']:
        tr[f + '_mean'] = round(st.mean(r[f] for r in rows), 2)
    tr['alpha'] = {
        'entry_state': alpha_nominal([[r1[k]['entry']['state'], r2[k]['entry']['state']] for k in pair]),
        'outcome': alpha_nominal([[r1[k]['end']['outcome'], r2[k]['end']['outcome']] for k in pair]),
        'claim_status': alpha_nominal([[r1[k]['end']['claim_status'], r2[k]['end']['claim_status']] for k in pair]),
        'decisive_mode': alpha_nominal([[r1[k]['decisive_move']['mode'], r2[k]['decisive_move']['mode']] for k in pair]),
        'composition': alpha_nominal([[r1[k]['composition'], r2[k]['composition']] for k in pair]),
        'v_status': alpha_nominal([[v_status(r1[k])['v'], v_status(r2[k])['v']] for k in pair]),
        'node_presence': alpha_nominal([[n in seq(r1[k], 'node'), n in seq(r2[k], 'node')] for k in pair for n in NODES]),
    }
    tr['gate'] = {'node_set_jaccard>=0.7': tr['node_set_jaccard_mean'] >= 0.7,
                  'entry_and_outcome>=0.8': tr['entry_state_agree'] >= 0.8 and tr['outcome_agree'] >= 0.8}

    # ---- corpus descriptives over first codings ----
    C = list(r1.values()); n = len(C)
    nodes = {c['key']: seq(c, 'node') for c in C}; modes = {c['key']: seq(c, 'mode') for c in C}
    V = [v_status(c) for c in C]
    textbook = list('QHSDFOC')
    def contains_order(xs, pat):
        it = iter(xs); return all(p in it for p in pat)
    corpus = {
        'papers_coded': n, 'eligible': len(man), 'coverage': round(n / len(man), 2),
        'entry_state': share(Counter(c['entry']['state'] for c in C), n),
        'entry_node': share(Counter(c['entry']['node'] for c in C), n),
        'outcome': share(Counter(c['end']['outcome'] for c in C), n),
        'claim_status': share(Counter(c['end']['claim_status'] for c in C), n),
        'composition': share(Counter(c['composition'] for c in C), n),
        'decisive_mode': share(Counter(c['decisive_move']['mode'] for c in C), n),
        'mode_used_share': {m: round(sum(m in modes[k] for k in modes) / n, 2) for m in sorted({x for v in modes.values() for x in v})},
        'node_used_share': {x: round(sum(x in nodes[k] for k in nodes) / n, 2) for x in NODES},
        'steps_median': med([len(v) for v in nodes.values()]),
        'mode_returns_median': med([returns(v) for v in modes.values()]),
        'papers_with_return_after_failure': round(sum(any(s.get('move') == 'return_after_failure' for s in next(q for q in c['sequences'] if q['kind'] == 'final_paper')['steps']) for c in C) / n, 2),
        'textbook_route_in_order': round(sum(contains_order(nodes[k], textbook) for k in nodes) / n, 2),
        'papers_with_D_design': round(sum('D' in nodes[k] for k in nodes) / n, 2),
        'v': share(Counter(v['v'] for v in V), n),
        'triangulation': round(sum(v['triangulation'] for v in V) / n, 2),
        'v_kinds_performed': share(Counter(k for v in V for k in v['kinds']), n),
        'gates_claim_yes': round(sum(c['gates']['claim'] == 'yes' for c in C) / n, 2),
        'gates_action_yes': round(sum(c['gates']['action'] == 'yes' for c in C) / n, 2),
    }

    # ---- who got coded: access bias against the eligible pool ----
    def summ(keys):
        ms = [met[k] for k in keys if k in met]
        return {'n': len(ms), 'impact_cnp_median': med([m['cnp'] for m in ms]), 'novelty_median': med([m['novelty_pair'] for m in ms]),
                'breadth_refs_median': med([m['breadth_refs'] for m in ms]), 'open_access_share': round(sum(bool(m['is_oa']) for m in ms) / max(len(ms), 1), 2)}
    elig = [m['key'] for m in man]
    access = {'coded': summ([k for k in elig if k in r1]), 'not_coded': summ([k for k in elig if k not in r1])}

    # ---- does the walk differ with impact? (descriptive, coded papers only) ----
    by_q = {}
    for c in C:
        q = (met.get(c['key']) or {}).get('impact_quintile')
        if q:
            by_q.setdefault(q, []).append(c)
    impact = {q: {'n': len(cs), 'capability_entry': round(sum(c['entry']['state'] == 'capability' for c in cs) / len(cs), 2),
                  'v_full': round(sum(v_status(c)['v'] == 'full' for c in cs) / len(cs), 2),
                  'steps_median': med([len(nodes[c['key']]) for c in cs]),
                  'modes_median': med([len(set(modes[c['key']])) for c in cs])} for q, cs in sorted(by_q.items())}

    res = {'test_retest': tr, 'corpus': corpus, 'access': access, 'by_impact_quintile': impact}
    out = DERIVED / 'calc1' / 'results.json'
    write_json(out, res, ['private/analysis/codings/api/calc1', 'private/analysis/codings/api/gold-r2',
                          'derived/calc1/manifest.jsonl', 'derived/gold/metrics.json'], {'codebook': '1.5.0'})
    md = ['# First calculation: results', '', f'Codings: {n} of {len(man)} eligible papers (first coding); {len(pair)} gold papers coded twice. Codebook 1.5.0, model coder.', '',
          '## Test-retest (two independent model codings)', '', '| Measure | Value |', '|:--|:--|']
    md += [f'| {k} | {v} |' for k, v in tr.items() if k not in ('alpha', 'gate')]
    md += [f'| alpha {k} | {v} |' for k, v in tr['alpha'].items()] + [f'| gate {k} | {v} |' for k, v in tr['gate'].items()]
    md += ['', '## Corpus', '', '```', json.dumps(corpus, indent=1), '```', '', '## Access bias', '', '```', json.dumps(access, indent=1), '```',
           '', '## By impact quintile', '', '```', json.dumps(impact, indent=1), '```']
    (DERIVED / 'calc1' / 'RESULTS.md').write_text('\n'.join(md) + '\n')
    log('g13_calc1_results.py', 'first-calculation agreement and descriptives', n, f'{len(pair)} test-retest pairs')
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
