#!/usr/bin/env python3
"""Human research workflows against agent loops, on graph v0.4.2 nodes.

  python3 tools/compare_loops.py validate FILE.json ...                  check agent-loop codings
  python3 tools/compare_loops.py import-csv AGENT_LOOPS.csv OUT_DIR      legacy CSV to one JSON per system
  python3 tools/compare_loops.py agree DIR_A DIR_B                        two coders on the same systems
  python3 tools/compare_loops.py compare --human 'GLOB' [--human 'GLOB' ...] [--human-review 'GLOB'] \
      --agents DIR [--review-returns FILE.json] --out DIR [--figures]

Human codings are paper codings under agents/coder/CODEBOOK.md (schema agents/coder/coding.schema.json):
the node sequence of each `final_paper` sequence, consecutive repeats merged, gives the nodes a paper
uses and its transitions; `review` sequences add transitions only. Agent codings are under
agents/loop-coder/CODEBOOK.md: `full` nodes are the nodes a loop runs, `loops[].steps` its transitions.
--review-returns is an optional JSON object {node: count} of returns recorded in process documents
(for the AI@UW figure: the return-node table of private/analysis/success-set/loops/REPORT.md).

compare writes OUT/compare.json, and with --figures OUT/loops_matrix.png and OUT/loops_nodes.png.
It warns when the human codings mix codebook versions, because granularity differs between versions.
Medians are upper medians (statistics.median_high), as in the October 24, 2026 talk script.
Standard library only, except matplotlib for --figures.
"""
from __future__ import annotations
import argparse, csv, glob, json, statistics, sys
from collections import Counter
from pathlib import Path

NODES = list('NEOIQHSDFCVXKPR')
WORD = {'N': 'new capability', 'E': 'explore', 'O': 'observe', 'I': 'infer', 'Q': 'question', 'H': 'hypothesize', 'S': 'simulate',
        'D': 'design', 'F': 'find conditions', 'C': 'compare', 'V': 'vary, replicate', 'X': 'exclude', 'K': 'keep', 'P': 'protect', 'R': 'refine'}
FAMILIES = ['science', 'coding', 'deep research', 'multi-agent', 'workflow pattern', 'general']
SCHEMA = Path(__file__).resolve().parents[1] / 'agents' / 'loop-coder' / 'loop.schema.json'


def runs(xs):
    out = []
    for x in xs:
        if not out or out[-1] != x:
            out.append(x)
    return out


# ---------- validation (the schema's rules, checked by hand so no jsonschema dependency) ----------

def validate(c: dict) -> list[str]:
    s = json.loads(SCHEMA.read_text())
    err = [f'missing field {k}' for k in s['required'] if k not in c]
    err += [f'unknown field {k}' for k in c if k not in s['properties']]
    if c.get('family') not in FAMILIES:
        err.append(f"family {c.get('family')!r} not one of {FAMILIES}")
    if c.get('no_conclusion_exit') not in ('yes', 'flag_only', 'no'):
        err.append('no_conclusion_exit must be yes, flag_only or no')
    for i, src in enumerate(c.get('sources', []), 1):
        if src.get('read') not in ('full_text', 'abstract', 'web_raw', 'web_extracted', 'metadata'):
            err.append(f'source {i}: bad read status {src.get("read")!r}')
    nodes = c.get('nodes', {})
    for n in NODES:
        m = nodes.get(n)
        if not isinstance(m, dict):
            err.append(f'node {n} missing'); continue
        if m.get('mark') not in ('full', 'partial', 'none'):
            err.append(f'node {n}: mark must be full, partial or none')
        if m.get('mark') in ('full', 'partial') and not (m.get('quote') and m.get('where')):
            err.append(f'node {n}: a {m.get("mark")} mark needs a quote and a where')
        if m.get('mark') == 'partial' and not m.get('note'):
            err.append(f'node {n}: a partial mark needs a note naming the surrogate')
        if len((m.get('quote') or '').split()) > 25:
            err.append(f'node {n}: quote longer than 25 words')
    for lp in c.get('loops', []):
        bad = [x for x in lp.get('steps', []) if x not in NODES]
        if bad or len(lp.get('steps', [])) < 2:
            err.append(f"loop {lp.get('name')!r}: steps must be two or more node letters (bad: {bad})")
        if not lp.get('evidence'):
            err.append(f"loop {lp.get('name')!r}: evidence is empty")
    return err


def cmd_validate(a):
    bad = 0
    for p in a.files:
        e = validate(json.loads(Path(p).read_text()))
        print(f'{p}: ' + ('ok' if not e else '; '.join(e)))
        bad += bool(e)
    sys.exit(1 if bad else 0)


# ---------- legacy CSV ----------

def cmd_import_csv(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for r in csv.DictReader(open(a.csv)):
        full, partial = set(r['full'].split()), set(r['partial'].split()) - set(r['full'].split())
        key = ''.join(ch if ch.isalnum() else '_' for ch in r['system'].lower()).strip('_')
        mark = lambda n: 'full' if n in full else 'partial' if n in partial else 'none'
        c = {'key': key, 'system': r['system'], 'family': r['family'], 'codebook_version': 'legacy-csv-2026-10-24',
             'coder': 'main session, claude-opus-5-5, typed by hand on 2026-10-24 (no per-node evidence)',
             'sources': [{'citation': r['source'], 'id': '', 'read': 'metadata'}],
             'nodes': {n: {'mark': mark(n), 'quote': '', 'where': '', 'note': 'legacy: see 09-agent-loops.md section 4 or 07-loops.md table 2.1'} for n in NODES},
             'loops': [{'name': 'main', 'steps': r['loop'].split(), 'evidence': '', 'where': ''}],
             'supplied': [], 'human_steps': [], 'return_trigger': '', 'stop_rule': '', 'no_conclusion_exit': 'no',
             'measured_behaviour': '', 'limits': 'Imported from the legacy CSV; marks and loop have no evidence fields and do not validate.'}
        (out / f'{key}.json').write_text(json.dumps(c, indent=1, ensure_ascii=False))
        print(out / f'{key}.json')


# ---------- loading ----------

def load_human(patterns, review_patterns=()):
    papers, edges, versions = {}, Counter(), Counter()
    for pat in patterns:
        for p in sorted(glob.glob(pat)):
            c = json.loads(Path(p).read_text())
            versions[c.get('codebook_version', '?') + (' (converted v0)' if 'v0' in c.get('coder', '') else '')] += 1
            for s in c['sequences']:
                seq = runs([x['node'] for x in s['steps']])
                if s['kind'] == 'final_paper':
                    papers[Path(p).stem] = seq
                edges.update(zip(seq, seq[1:]))
    for pat in review_patterns:  # review sequences only, e.g. a second coding of a paper already counted
        for p in sorted(glob.glob(pat)):
            for s in json.loads(Path(p).read_text())['sequences']:
                if s['kind'] == 'review':
                    seq = runs([x['node'] for x in s['steps']])
                    edges.update(zip(seq, seq[1:]))
    return papers, edges, versions


def load_agents(d):
    ags = []
    for p in sorted(Path(d).glob('*.json')):
        c = json.loads(p.read_text())
        full = {n for n in NODES if c['nodes'][n]['mark'] == 'full'}
        partial = {n for n in NODES if c['nodes'][n]['mark'] == 'partial'}
        e = set()
        for lp in c['loops']:
            e |= {(x, y) for x, y in zip(lp['steps'], lp['steps'][1:]) if x != y}
        ags.append({'system': c['system'], 'family': c['family'], 'full': full, 'partial': partial, 'edges': e,
                    'evidence': all(c['nodes'][n]['quote'] for n in full | partial)})
    return ags


# ---------- compare ----------

def compare(papers, hedges, versions, ags):
    n_p = len(papers)
    used = set().union(*map(set, papers.values()))
    human_edges = set(hedges)
    agent_edges = set().union(*(a['edges'] for a in ags))
    per_agent = {a['system']: {'nodes_full': sorted(a['full'], key=NODES.index), 'n_nodes': len(a['full']),
                               'edges_seen_in_human_record': f"{len(a['edges'] & human_edges)}/{len(a['edges'])}",
                               'subset_nodes': a['full'] <= used, 'subset_edges': a['edges'] <= human_edges,
                               'has_evidence': a['evidence']} for a in ags}
    return {'human_papers': n_p, 'agent_systems': len(ags), 'human_codebook_versions': dict(versions),
            'human_nodes_used': sorted(used, key=NODES.index),
            'median_nodes_per_human_paper': statistics.median_high(len(set(s)) for s in papers.values()),
            'median_nodes_per_agent_full': statistics.median_high(len(a['full']) for a in ags),
            'agents_node_subset_of_human': sum(v['subset_nodes'] for v in per_agent.values()),
            'agents_edge_subset_of_human': sum(v['subset_edges'] for v in per_agent.values()),
            'agents_with_evidence': sum(v['has_evidence'] for v in per_agent.values()),
            'distinct_edges': {'human': len(human_edges), 'agent': len(agent_edges), 'shared': len(human_edges & agent_edges),
                               'agent_only': sorted('>'.join(e) for e in agent_edges - human_edges),
                               'human_only': len(human_edges - agent_edges)},
            'share_of_agents_running_node': {n: round(sum(n in a['full'] for a in ags) / len(ags), 2) for n in NODES},
            'share_of_agents_partial_node': {n: round(sum(n in a['partial'] for a in ags) / len(ags), 2) for n in NODES},
            'share_of_human_papers_using_node': {n: round(sum(n in s for s in papers.values()) / n_p, 2) for n in NODES},
            'per_agent': per_agent}


def figures(stats, ags, review, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    use, run = stats['share_of_human_papers_using_node'], stats['share_of_agents_running_node']
    ags = sorted(ags, key=lambda a: (FAMILIES.index(a['family']), -len(a['full'])))
    rows = [(f"Human papers ({stats['human_papers']}): share using node", 'use')]
    if review:
        rows.append(('Human review loops: returns', 'review'))
    rows += [(a['system'], a) for a in ags]
    fig, ax = plt.subplots(figsize=(14, 0.42 * len(rows) + 2.5), dpi=150)
    for i, (name, a) in enumerate(rows):
        y = len(rows) - i
        for j, n in enumerate(NODES):
            if a == 'use':
                v = use[n]; ax.scatter(j, y, s=60 + 520 * v, color='#b5562b', alpha=0.25 + 0.75 * v, edgecolor='none')
            elif a == 'review':
                v = review.get(n, 0) / max(review.values()); ax.scatter(j, y, s=20 + 560 * v, color='#b5562b', alpha=0.2 + 0.8 * v, edgecolor='none')
            elif n in a['full']:
                ax.scatter(j, y, s=200, color='#0f4c5c')
            elif n in a['partial']:
                ax.scatter(j, y, s=200, facecolor='none', edgecolor='#0f4c5c', lw=1.5)
            else:
                ax.scatter(j, y, s=10, color='#c9cfd1')
        ax.text(-0.8, y, name, ha='right', va='center', fontsize=9.5)
    for j, n in enumerate(NODES):
        ax.text(j, len(rows) + 1.2, n, ha='center', fontsize=13, fontweight='bold')
    ax.set_xlim(-9.5, len(NODES)); ax.set_ylim(0.3, len(rows) + 2); ax.axis('off')
    fig.savefig(out / 'loops_matrix.png', bbox_inches='tight')
    fig, ax = plt.subplots(figsize=(13, 5.6), dpi=150)
    x = range(len(NODES)); w = 0.4
    ax.bar([i - w / 2 for i in x], [use[n] for n in NODES], w, color='#b5562b', label=f"human papers using the step (n = {stats['human_papers']})")
    ax.bar([i + w / 2 for i in x], [run[n] for n in NODES], w, color='#0f4c5c', label=f"agent loops running the step (n = {stats['agent_systems']})")
    ax.set_xticks(list(x)); ax.set_xticklabels([f'{n}  {WORD[n]}' for n in NODES], rotation=35, ha='right')
    ax.set_ylim(0, 1.05); ax.set_ylabel('share'); ax.legend(frameon=False, loc='upper left')
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    fig.savefig(out / 'loops_nodes.png', bbox_inches='tight')


def cmd_compare(a):
    papers, hedges, versions = load_human(a.human, a.human_review or ())
    ags = load_agents(a.agents)
    if not papers or not ags:
        sys.exit('no human codings or no agent codings found')
    if len(versions) > 1:
        print(f'WARNING: human codings mix codebook versions {dict(versions)}; step granularity differs between them', file=sys.stderr)
    stats = compare(papers, hedges, versions, ags)
    review = json.loads(Path(a.review_returns).read_text()) if a.review_returns else None
    stats['review_returns'] = review
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / 'compare.json').write_text(json.dumps(stats, indent=1))
    if a.figures:
        figures(stats, ags, review, out)
    print(json.dumps({k: v for k, v in stats.items() if k != 'per_agent'}, indent=1))


# ---------- agreement between two coders of the same systems ----------

def kappa(pairs):
    n = len(pairs); po = sum(x == y for x, y in pairs) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0


def cmd_agree(a):
    A = {p.stem: json.loads(p.read_text()) for p in Path(a.dir_a).glob('*.json')}
    B = {p.stem: json.loads(p.read_text()) for p in Path(a.dir_b).glob('*.json')}
    keys = sorted(set(A) & set(B))
    if not keys:
        sys.exit('no system coded in both folders')
    pairs, rows = [], []
    for k in keys:
        pk = [(A[k]['nodes'][n]['mark'], B[k]['nodes'][n]['mark']) for n in NODES]
        pairs += pk
        fa = {n for n in NODES if A[k]['nodes'][n]['mark'] == 'full'}; fb = {n for n in NODES if B[k]['nodes'][n]['mark'] == 'full'}
        rows.append((k, sum(x == y for x, y in pk), round(len(fa & fb) / max(1, len(fa | fb)), 2)))
    po, k = kappa(pairs)
    print('system\tmarks agreeing of 15\tJaccard of full nodes')
    for r in rows:
        print(*r, sep='\t')
    print(f'\n{len(keys)} systems, {len(pairs)} marks: observed agreement {po:.2f}, Cohen kappa {k:.2f}')
    per_node = {n: kappa([(A[s]['nodes'][n]['mark'], B[s]['nodes'][n]['mark']) for s in keys])[0] for n in NODES}
    print('agreement by node: ' + ', '.join(f'{n} {v:.2f}' for n, v in per_node.items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('validate'); p.add_argument('files', nargs='+'); p.set_defaults(f=cmd_validate)
    p = sp.add_parser('import-csv'); p.add_argument('csv'); p.add_argument('out'); p.set_defaults(f=cmd_import_csv)
    p = sp.add_parser('agree'); p.add_argument('dir_a'); p.add_argument('dir_b'); p.set_defaults(f=cmd_agree)
    p = sp.add_parser('compare'); p.add_argument('--human', action='append', required=True); p.add_argument('--agents', required=True)
    p.add_argument('--human-review', action='append', help='GLOB of codings whose review sequences add transitions only')
    p.add_argument('--review-returns'); p.add_argument('--out', required=True); p.add_argument('--figures', action='store_true'); p.set_defaults(f=cmd_compare)
    a = ap.parse_args(); a.f(a)


if __name__ == '__main__':
    main()
