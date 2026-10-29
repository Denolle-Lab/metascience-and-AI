"""Researchers' papers against agent loops on graph v0.4.2, with bootstrap intervals and the V rule run both ways.

Human side: the first-calculation model codings (codebook 1.5.0), final_paper sequences.
Agent side: the 31 agent systems coded blind by two model coders under loop codebook 0.1.2
(private/analysis/reliability/codings/agents/{opus-b,sonnet-c}); a node counts when marked "full";
shares are averaged over the two coders. That study's own files are read, never changed.

Outputs: private/data/roadmap/derived/calc1/papers_vs_agents.json and PAPERS_VS_AGENTS.md
Run:     python tools/roadmap/g14_papers_vs_agents.py
"""
import json, random
from collections import Counter
from pathlib import Path
from common import ROOT, PRIVATE, DERIVED, write_json, log
from check_coding import validate, seq

API = PRIVATE / 'analysis' / 'codings' / 'api' / 'calc1'
AG = PRIVATE / 'analysis' / 'reliability' / 'codings' / 'agents'
NODES = list('NEOIQHSDFCVXKPR')
NAMES = dict(N='new capability', E='explore', O='observe', I='infer a latent quantity', Q='question', H='hypothesize rivals',
             S='simulate or derive', D='design the test', F='find or set conditions', C='compare', V='vary and replicate',
             X='exclude a rival', K='keep the claim', P='protect', R='refine')
TRI = {'replication', 'method', 'generalization'}
B = 2000
rng = random.Random(2026)


def ci(vals, stat=lambda xs: sum(xs) / len(xs)):
    """Point estimate and 95% percentile bootstrap interval over units."""
    n = len(vals)
    bs = sorted(stat([vals[rng.randrange(n)] for _ in range(n)]) for _ in range(B))
    return [round(stat(vals), 2), round(bs[int(.025 * B)], 2), round(bs[int(.975 * B) - 1], 2)]


def edges(xs):
    return {(a, b) for a, b in zip(xs, xs[1:]) if a != b}


def v_rule(kinds, controls_full):
    full_kinds = {k for k in kinds if k != 'reproduction' and (controls_full or k != 'control')}
    return 'full' if full_kinds else ('partial' if kinds else 'none')


def main():
    papers = []
    for f in sorted(API.glob('*.json')):
        c = json.loads(f.read_text())
        if validate(c):
            continue
        ns = seq(c, 'node')
        kinds = {v['kind'] for v in c.get('v_checks', []) if v.get('performed_here') is True}
        papers.append({'nodes': ns, 'set': set(ns), 'edges': edges(ns), 'kinds': kinds})
    coders = {}
    for d in sorted(p for p in AG.iterdir() if p.is_dir()):
        sysm = {}
        for f in sorted(d.glob('*.json')):
            a = json.loads(f.read_text())
            full = {n for n in NODES if a['nodes'][n]['mark'] == 'full'}
            e = set()
            for lp in a.get('loops', []):
                e |= edges(lp['steps'])
            kinds = {v['kind'] for v in a.get('v_checks', []) if v.get('in_loop')}
            sysm[a['key']] = {'set': full, 'edges': e, 'kinds': kinds, 'version': a.get('codebook_version')}
        coders[d.name] = sysm
    keys = sorted(set.intersection(*(set(v) for v in coders.values())))
    versions = sorted({coders[c][k]['version'] for c in coders for k in keys})

    # node use
    node = {}
    for n in NODES:
        hum = ci([int(n in p['set']) for p in papers])
        ag = [sum(int(n in coders[c][k]['set']) for c in coders) / len(coders) for k in keys]
        node[n] = {'name': NAMES[n], 'papers': hum, 'agents': ci(ag)}
    # edges: which researcher transitions do agent loops ever run, and vice versa
    hum_edges = Counter(e for p in papers for e in p['edges'])
    ag_edges = {c: set().union(*(coders[c][k]['edges'] for k in keys)) for c in coders}
    common_h = {e for e, m in hum_edges.items() if m / len(papers) >= .10}
    edge = {'researcher_edges_in_10pct_of_papers': len(common_h),
            'of_those_run_by_any_agent': {c: len(common_h & ag_edges[c]) for c in coders},
            'agent_edges_never_in_papers': {c: sorted(''.join(e) for e in ag_edges[c] - set(hum_edges)) for c in coders},
            'top_researcher_edges_no_agent_runs': [[''.join(e), round(m / len(papers), 2)] for e, m in hum_edges.most_common()
                                                   if all(e not in ag_edges[c] for c in coders)][:10]}
    # V both ways
    vk = {}
    for label, cf in [('controls_count_full', True), ('controls_count_partial', False)]:
        hv = [v_rule(p['kinds'], cf) for p in papers]
        av = {c: [v_rule(coders[c][k]['kinds'], cf) for k in keys] for c in coders}
        vk[label] = {'papers_full': ci([int(x == 'full') for x in hv]), 'papers_partial': ci([int(x == 'partial') for x in hv]),
                     'agents_full': ci([sum(av[c][i] == 'full' for c in coders) / len(coders) for i in range(len(keys))])}
    vk['triangulation'] = {'papers': ci([int(len(p['kinds'] & TRI) >= 2) for p in papers]),
                           'agents': ci([sum(len(coders[c][k]['kinds'] & TRI) >= 2 for c in coders) / len(coders) for k in keys])}
    sizes = {'papers': ci([len(p['set']) for p in papers], stat=lambda xs: sorted(xs)[len(xs) // 2]),
             'agents': ci([sum(len(coders[c][k]['set']) for c in coders) / len(coders) for k in keys], stat=lambda xs: sorted(xs)[len(xs) // 2])}
    res = {'n_papers': len(papers), 'n_agents': len(keys), 'agent_coders': list(coders), 'loop_codebook_versions': versions,
           'distinct_nodes_median': sizes, 'node_use': node, 'edges': edge, 'v': vk,
           'note': 'Each cell is [estimate, 2.5%, 97.5%] from 2000 bootstrap resamples of papers or of agent systems. Agent shares average the two blind coders.'}
    write_json(DERIVED / 'calc1' / 'papers_vs_agents.json', res,
               ['private/analysis/codings/api/calc1', 'private/analysis/reliability/codings/agents/opus-b', 'private/analysis/reliability/codings/agents/sonnet-c'],
               {'bootstrap': B, 'seed': 2026, 'agent_node_mark': 'full'})
    md = [f'# Papers against agent loops ({len(papers)} papers, {len(keys)} agent systems)', '', res['note'], '',
          '| Node | Papers | Agents |', '|:--|:--|:--|']
    md += [f'| {n} {v["name"]} | {v["papers"]} | {v["agents"]} |' for n, v in node.items()]
    md += ['', '| V | Papers full | Agents full |', '|:--|:--|:--|']
    md += [f'| {k} | {v["papers_full"]} | {v["agents_full"]} |' for k, v in vk.items() if k != 'triangulation']
    md += [f'| triangulation | {vk["triangulation"]["papers"]} | {vk["triangulation"]["agents"]} |', '',
           f'Distinct nodes per unit, median: papers {sizes["papers"]}, agents {sizes["agents"]}.', '',
           f'Researcher transitions in at least 10% of papers: {edge["researcher_edges_in_10pct_of_papers"]}; run by any agent: {edge["of_those_run_by_any_agent"]}.', '',
           'Most common researcher transitions no agent loop runs: ' + ', '.join(f'{e} ({s})' for e, s in edge['top_researcher_edges_no_agent_runs'])]
    (DERIVED / 'calc1' / 'PAPERS_VS_AGENTS.md').write_text('\n'.join(md) + '\n')
    log('g14_papers_vs_agents.py', 'papers vs agent loops with bootstrap intervals', len(papers), f'{len(keys)} agents, loop codebook {versions}')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
