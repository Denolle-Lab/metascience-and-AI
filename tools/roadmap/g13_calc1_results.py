"""First calculation: test-retest agreement on the gold papers and corpus descriptives (roadmap Phase 0), per round.

Inputs
  private/analysis/codings/api/calc1/*.json     round 1: first model coding (codebook 1.5.0), eligible papers with full text
  private/analysis/codings/api/r2/*.json        round 2: model coding, same codebook and coder
  private/analysis/codings/api/gold-r2/*.json   second, independent model coding of the round-1 gold papers
  private/analysis/codings/api/state.json       batch of each coding (round-1 first analysis against top-up; rounds.py)
  private/data/roadmap/derived/calc1/manifest.jsonl    the 525 eligible round-1 papers
  private/data/roadmap/derived/r2calc/manifest.jsonl   the 222 eligible round-2 papers
  private/data/roadmap/derived/gold/metrics.json       impact, novelty, breadth proxies for the 600 round-1 preselected
  private/data/roadmap/derived/r2/metrics.json         the same for the 277 round-2 drawn papers

Blocks of results.json
  test_retest, corpus, access, by_impact_quintile   round 1 (calc1), keys as before so figures and g19 read them unchanged.
                  test-retest is round 1 only (the gold papers are round-1 papers).
  round1_split    corpus descriptives for the 233 first-analysis papers and the top-up papers separately (rounds.py), so
                  the round-1 numbers reported at 233 can be compared with the same numbers at the current n.
  round2          corpus, access and by_impact_quintile for round 2 (tag r2). Round-2 papers have no stored quintile, so
                  it is computed from cnp with the g03/g18 rule (rounds.quintile).
  pooled          corpus over both rounds (raw shares over all valid codings), the same per round side by side, and
                  round_comparison: is each categorical descriptive associated with round? Levels with fewer than 10
                  papers are merged into 'other' first; chi-square permutation test and bias-corrected Cramer's V with a
                  bootstrap interval (g20_topics_journals.assoc: 5000 permutations, 2000 resamples, per-test generator).
                  Step counts: Kruskal-Wallis permutation test with epsilon^2 (g20 numeric_by_group). The rounds were
                  drawn differently (round 2 open access only, journal cap), so a round difference mixes sampling and
                  coding drift; it is descriptive.

Definitions (corpus block): shares are [count, share of valid codings]; mode_used_share = share of papers whose
final-paper sequence uses that mode of inquiry at least once; steps and returns on the run-collapsed sequence
(check_coding.seq); textbook_route_in_order = QHSDFOC as an ordered subsequence.

Outputs
  private/data/roadmap/derived/calc1/results.json   all numbers below, with provenance
  private/data/roadmap/derived/calc1/RESULTS.md     the same, as tables

Run:  python tools/roadmap/g13_calc1_results.py
"""
import json, statistics as st
from collections import Counter
from pathlib import Path
from common import ROOT, PRIVATE, DERIVED, write_json, log, read_json
from check_coding import validate, v_status, seq, agree
from g11_human_agreement import alpha_nominal
import rounds

API = PRIVATE / 'analysis' / 'codings' / 'api'
NODES = list('NEOIQHSDFCVXKPR')
MIN_LEVEL = 10


def load(tag):
    return rounds.valid(tag)


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


def contains_order(xs, pat):
    it = iter(xs)
    return all(p in it for p in pat)


def descriptives(C, n_eligible):
    """Corpus block for a list of codings (keys as the round-1 block always had)."""
    n = len(C)
    nodes = {c['key']: seq(c, 'node') for c in C}; modes = {c['key']: seq(c, 'mode') for c in C}
    V = [v_status(c) for c in C]
    textbook = list('QHSDFOC')
    return {
        'papers_coded': n, 'eligible': n_eligible, 'coverage': round(n / n_eligible, 2) if n_eligible else None,
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


def access_bias(elig, coded, met):
    def summ(keys):
        ms = [met[k] for k in keys if k in met]
        return {'n': len(ms), 'impact_cnp_median': med([m['cnp'] for m in ms]), 'novelty_median': med([m['novelty_pair'] for m in ms]),
                'breadth_refs_median': med([m['breadth_refs'] for m in ms]), 'open_access_share': round(sum(bool(m['is_oa']) for m in ms) / max(len(ms), 1), 2)}
    return {'coded': summ([k for k in elig if k in coded]), 'not_coded': summ([k for k in elig if k not in coded])}


def by_quintile(C, met, quint):
    by_q = {}
    for c in C:
        q = quint(met.get(c['key']) or {})
        if q:
            by_q.setdefault(q, []).append(c)
    return {q: {'n': len(cs), 'capability_entry': round(sum(c['entry']['state'] == 'capability' for c in cs) / len(cs), 2),
                'v_full': round(sum(v_status(c)['v'] == 'full' for c in cs) / len(cs), 2),
                'steps_median': med([len(seq(c, 'node')) for c in cs]),
                'modes_median': med([len(set(seq(c, 'mode'))) for c in cs])} for q, cs in sorted(by_q.items())}


def round_comparison(tagged):
    """tagged: [(round name, coding)]. Categorical descriptives against round, and step counts against round."""
    import g20_topics_journals as g20
    rnd = [r for r, _ in tagged]
    fields = {'entry_state': lambda c: c['entry']['state'], 'entry_node': lambda c: c['entry']['node'],
              'outcome': lambda c: c['end']['outcome'], 'claim_status': lambda c: c['end']['claim_status'],
              'composition': lambda c: c['composition'], 'decisive_mode': lambda c: c['decisive_move']['mode']}
    out = {}
    for name, f in fields.items():
        y = [f(c) for _, c in tagged]
        cnt = Counter(y)
        y = [v if cnt[v] >= MIN_LEVEL else 'other' for v in y]
        r = g20.assoc(rnd, y, f'g13 round|{name}')
        out[name] = {k: r[k] for k in ('n', 'chi2', 'cramers_v_bc', 'v_bc_ci', 'p')}
        out[name]['levels_merged_into_other'] = sorted(v for v, m in cnt.items() if m < MIN_LEVEL)
    r = g20.numeric_by_group(rnd, [len(seq(c, 'node')) for _, c in tagged], 'g13 round|steps')
    out['steps'] = {k: r[k] for k in ('n', 'H', 'epsilon2', 'epsilon2_ci', 'p')} | {'median_by_round': {g: v['median'] for g, v in r['groups'].items()}}
    q = g20.bh([v['p'] for v in out.values()])
    for v, qq in zip(out.values(), q):
        v['q'] = round(float(qq), 3)
    return out


def main():
    r1, r2 = load('calc1'), load('gold-r2')
    rr2 = load('r2')
    man = rounds.manifest('calc1')
    man2 = rounds.manifest('r2calc')
    met = rounds.metrics('gold')
    met2 = rounds.metrics('r2')

    # ---- test-retest on gold papers coded twice (round 1 only) ----
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

    # ---- corpus descriptives, round 1 (keys unchanged) ----
    C = list(r1.values()); n = len(C)
    corpus = descriptives(C, len(man))
    elig = [m['key'] for m in man]
    access = access_bias(elig, r1, met)
    impact = by_quintile(C, met, lambda m: m.get('impact_quintile'))

    # ---- round 1 split: first analysis (233) against top-up ----
    first, top = rounds.round1_split(r1)
    split = {'rule': 'top-up = valid calc1 codings whose state.json record names a calc1 batch submitted on or after '
                     f'{rounds.TOPUP_FROM}; first analysis = the other valid calc1 codings',
             'first_analysis': descriptives([r1[k] for k in sorted(first)], len(man)),
             'top_up': descriptives([r1[k] for k in sorted(top)], len(man))}

    # ---- round 2 ----
    C2 = list(rr2.values())
    round2 = {}
    if C2:
        round2 = {'corpus': descriptives(C2, len(man2)),
                  'access': access_bias([m['key'] for m in man2], rr2, met2),
                  'by_impact_quintile': by_quintile(C2, met2, lambda m: rounds.quintile(m.get('cnp'))),
                  'quintile_rule': 'rounds.quintile: min(4, int(cnp * 5)) + 1, the g03/g18 rule (round-2 metrics store no quintile)'}

    # ---- pooled, round as a stratum ----
    pooled = {}
    if C2:
        tagged = [('round1', c) for c in C] + [('round2', c) for c in C2]
        pooled = {'corpus': descriptives([c for _, c in tagged], len(man) + len(man2)),
                  'papers_by_round': {'round1': n, 'round2': len(C2)},
                  'round_comparison': round_comparison(tagged),
                  'note': 'pooled shares are raw shares over all valid codings of both rounds; the rounds differ in sampling '
                          '(round 2 open access only, at most 4 papers per journal), so round_comparison mixes sampling and coding drift'}

    res = {'test_retest': tr, 'corpus': corpus, 'access': access, 'by_impact_quintile': impact,
           'round1_split': split, 'round2': round2, 'pooled': pooled}
    out = DERIVED / 'calc1' / 'results.json'
    write_json(out, res, ['private/analysis/codings/api/calc1', 'private/analysis/codings/api/r2', 'private/analysis/codings/api/gold-r2',
                          'private/analysis/codings/api/state.json', 'derived/calc1/manifest.jsonl', 'derived/r2calc/manifest.jsonl',
                          'derived/gold/metrics.json', 'derived/r2/metrics.json'], {'codebook': '1.5.0', 'min_level': MIN_LEVEL})

    def side(field, blocks):
        """Rows [level, share per block] for a categorical field."""
        lv = []
        for b in blocks.values():
            for k in b.get(field, {}):
                if k not in lv:
                    lv.append(k)
        L = ['| ' + field + ' | ' + ' | '.join(blocks) + ' |', '|:--|' + '--:|' * len(blocks)]
        for k in lv:
            L.append(f'| {k} | ' + ' | '.join(f"{b[field][k][1]}" if k in b.get(field, {}) else '0' for b in blocks.values()) + ' |')
        return L

    md = ['# First calculation: results', '',
          f'Codings: round 1 {n} of {len(man)} eligible papers (first coding; {len(first)} in the first analysis, {len(top)} top-up); '
          f'round 2 {len(C2)} of {len(man2)} eligible; {len(pair)} round-1 gold papers coded twice. Codebook 1.5.0, model coder. '
          'Valid = passes tools/check_coding.py validate().', '',
          '## Test-retest (two independent model codings, round 1 gold papers)', '', '| Measure | Value |', '|:--|:--|']
    md += [f'| {k} | {v} |' for k, v in tr.items() if k not in ('alpha', 'gate')]
    md += [f'| alpha {k} | {v} |' for k, v in tr['alpha'].items()] + [f'| gate {k} | {v} |' for k, v in tr['gate'].items()]
    blocks = {f'round 1 first analysis ({len(first)})': split['first_analysis'], f'round 1 all ({n})': corpus}
    if C2:
        blocks[f'round 2 ({len(C2)})'] = round2['corpus']
        blocks[f'pooled ({n + len(C2)})'] = pooled['corpus']
    md += ['', '## Corpus descriptives by round (shares of valid codings)', '']
    for f in ['entry_state', 'entry_node', 'outcome', 'claim_status', 'composition', 'decisive_mode']:
        md += side(f, blocks) + ['']
    allm = sorted({m for b in blocks.values() for m in b['mode_used_share']})
    md += ['| mode of inquiry used (share of papers) | ' + ' | '.join(blocks) + ' |', '|:--|' + '--:|' * len(blocks)]
    md += [f'| {m} | ' + ' | '.join(str(b['mode_used_share'].get(m, 0)) for b in blocks.values()) + ' |' for m in allm]
    md += ['', '| Count | ' + ' | '.join(blocks) + ' |', '|:--|' + '--:|' * len(blocks)]
    md += [f'| {k} | ' + ' | '.join(str(b[k]) for b in blocks.values()) + ' |'
           for k in ['steps_median', 'mode_returns_median', 'papers_with_return_after_failure', 'textbook_route_in_order',
                     'papers_with_D_design', 'triangulation', 'gates_claim_yes', 'gates_action_yes']]
    if C2:
        md += ['', '## Round 1 against round 2 (descriptive)', '',
               '| Variable | n | Cramer V (bias-corrected) or epsilon^2 [95% CI] | permutation p | BH q |', '|:--|--:|:--|--:|--:|']
        for k, v in pooled['round_comparison'].items():
            eff = f"V {v['cramers_v_bc']} {v['v_bc_ci']}" if 'cramers_v_bc' in v else f"eps2 {v['epsilon2']} {v['epsilon2_ci']}"
            md.append(f"| {k} | {v['n']} | {eff} | {v['p']} | {v['q']} |")
    md += ['', '## Round 1 corpus (json)', '', '```', json.dumps(corpus, indent=1), '```', '', '## Access bias, round 1', '', '```', json.dumps(access, indent=1), '```',
           '', '## By impact quintile, round 1', '', '```', json.dumps(impact, indent=1), '```']
    if C2:
        md += ['', '## Access bias, round 2', '', '```', json.dumps(round2['access'], indent=1), '```',
               '', '## By impact quintile, round 2', '', '```', json.dumps(round2['by_impact_quintile'], indent=1), '```']
    (DERIVED / 'calc1' / 'RESULTS.md').write_text('\n'.join(md) + '\n')
    log('g13_calc1_results.py', 'first-calculation agreement and descriptives, per round and pooled', n + len(C2),
        f'round 1 {n}, round 2 {len(C2)}; {len(pair)} test-retest pairs')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
