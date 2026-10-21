#!/usr/bin/env python3
"""Aggregate paper codings (codebook v1) into corpus tables.

  python3 tools/aggregate_codings.py DIR [DIR ...] [--manifest FILE.jsonl ...] [--out OUTDIR]

Reads every <key>.json in the folders (later folders override earlier ones for the same key),
joins each paper to its stratum and citation metrics from the manifests (tools/corpus.py) when
given, and writes to OUTDIR (default private/analysis/codings/summary/):
  papers.csv        one row per paper: stratum, entry, outcome, claim status, composition, gates,
                    steps, distinct modes, returns to an earlier mode and node, nodes used, citations
  transitions.csv   mode-to-mode hand-offs (consecutive repeats merged), counted by stratum
  nodes.csv         node-to-node transitions, counted by stratum
  tree.csv          how often each controller question is answered, and the mode it called
  summary.md        the same, as tables for reading, with counts by stratum
Invalid codings are skipped and listed.
"""
from __future__ import annotations
import argparse, collections, csv, json, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from check_coding import validate  # noqa: E402


def runs(xs):
    out = []
    for x in xs:
        if not out or out[-1] != x:
            out.append(x)
    return out


def returns(xs):
    r = runs(xs)
    return sum(1 for i, x in enumerate(r) if x in r[:i])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('dirs', nargs='+')
    ap.add_argument('--manifest', action='append', default=[])
    ap.add_argument('--out', type=Path, default=ROOT / 'private' / 'analysis' / 'codings' / 'summary')
    args = ap.parse_args()
    meta = {}
    for m in args.manifest:
        for line in Path(m).read_text().splitlines():
            if line.strip():
                r = json.loads(line); meta[r['key']] = r
    codings, bad = {}, []
    for d in args.dirs:
        for p in sorted(Path(d).glob('*.json')):
            c = json.loads(p.read_text())
            if validate(c):
                bad.append(p.name); continue
            codings[p.stem] = c
    args.out.mkdir(parents=True, exist_ok=True)
    rows, trans, ntrans, tree = [], collections.Counter(), collections.Counter(), collections.Counter()
    for k, c in sorted(codings.items()):
        fp = next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps']
        modes, nodes = [s['mode'] for s in fp], [s['node'] for s in fp]
        st = meta.get(k, {}).get('stratum', 'unassigned')
        rows.append({'key': k, 'stratum': st, 'entry_state': c['entry']['state'], 'entry_node': c['entry']['node'],
                     'outcome': c['end']['outcome'], 'claim_status': c['end']['claim_status'], 'composition': c['composition'],
                     'gate_action': c['gates']['action'], 'gate_claim': c['gates']['claim'], 'gate_registration': c['gates']['registration'],
                     'steps': len(fp), 'distinct_modes': len(set(modes)), 'mode_returns': returns(modes), 'node_returns': returns(nodes),
                     'nodes_used': ''.join(sorted(set(nodes))), 'has_H': 'H' in nodes, 'has_D': 'D' in nodes, 'has_V': 'V' in nodes,
                     'review_steps': sum(len(s['steps']) for s in c['sequences'] if s['kind'] == 'review'),
                     'cited_by_count': meta.get(k, {}).get('cited_by_count'), 'cnp': meta.get(k, {}).get('cnp'),
                     'decisive_mode': c['decisive_move']['mode'], 'codebook': c['codebook_version'], 'coder': c['coder']})
        for a, b in zip(runs(modes), runs(modes)[1:]):
            trans[(st, a, b)] += 1
        for a, b in zip(runs(nodes), runs(nodes)[1:]):
            ntrans[(st, a, b)] += 1
        for t in c['tree']:
            tree[(st, t['question'], t['mode_called'])] += 1
    def dump(name, header, data):
        with open(args.out / name, 'w', newline='') as fh:
            w = csv.writer(fh); w.writerow(header); w.writerows(data)
    if rows:
        with open(args.out / 'papers.csv', 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    dump('transitions.csv', ['stratum', 'from_mode', 'to_mode', 'count'], [(*k, v) for k, v in sorted(trans.items())])
    dump('nodes.csv', ['stratum', 'from_node', 'to_node', 'count'], [(*k, v) for k, v in sorted(ntrans.items())])
    dump('tree.csv', ['stratum', 'question', 'mode_called', 'count'], [(*k, v) for k, v in sorted(tree.items())])
    by = collections.defaultdict(list)
    for r in rows:
        by[r['stratum']].append(r)
    L = [f'# Coding summary', '', f'{len(rows)} papers from {", ".join(args.dirs)}; {len(bad)} invalid skipped{": " + ", ".join(bad) if bad else ""}.', '',
         '| Stratum | Papers | Median steps | Mean returns to a mode | With H (rivals) | With D (designed test) | Entry: capability | Outcome kept / excluded / contradicted / none |',
         '|:--|:--|:--|:--|:--|:--|:--|:--|']
    for s, rs in sorted(by.items()):
        n = len(rs); oc = collections.Counter(r['outcome'] for r in rs)
        L.append(f'| {s} | {n} | {statistics.median(r["steps"] for r in rs)} | {statistics.mean(r["mode_returns"] for r in rs):.1f} | '
                 f'{sum(r["has_H"] for r in rs)} | {sum(r["has_D"] for r in rs)} | {sum(r["entry_state"] == "capability" for r in rs)} | '
                 f'{oc["kept"]} / {oc["excluded"]} / {oc["contradicted"]} / {oc["no_conclusion"]} |')
    L += ['', '## Most frequent mode hand-offs', '', '| Stratum | From | To | Count |', '|:--|:--|:--|:--|']
    L += [f'| {s} | {a} | {b} | {v} |' for (s, a, b), v in trans.most_common(30)]
    (args.out / 'summary.md').write_text('\n'.join(L) + '\n')
    print(f'{len(rows)} papers aggregated; {len(bad)} invalid; outputs in {args.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
