#!/usr/bin/env python3
"""Validate paper codings (codebook v1) and measure agreement between two codings of one paper.

  python3 tools/check_coding.py validate CODING.json [...]
  python3 tools/check_coding.py agree A.json B.json        two coders, same paper
  python3 tools/check_coding.py agree-dir DIR_A DIR_B      every key present in both folders

Validation implements the parts of JSON Schema the schema uses (type, enum, required,
additionalProperties, items) and adds the codebook's rules: every step has a page, quotes are at
most 25 words, steps are numbered 1..n. Agreement reports entry node, outcome, Jaccard overlap of
the node and mode sets, and sequence similarity (1 minus the normalized edit distance) of the
final-paper node and mode sequences, consecutive repeats merged.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'agents' / 'coder' / 'coding.schema.json').read_text())
TYPES = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool}


NEW_IN = {'disagreements': '1.3.0', 'alternatives_considered': '1.3.0', 'v_checks': '1.5.0'}


def _older(v, than):
    try:
        return tuple(map(int, v.split('.'))) < tuple(map(int, than.split('.')))
    except Exception:  # noqa: BLE001
        return False


def check(node, schema, path, errs, version=None):
    t = schema.get('type')
    if t and not isinstance(node, TYPES[t]):
        errs.append(f'{path}: expected {t}'); return
    if 'enum' in schema and node not in schema['enum']:
        errs.append(f'{path}: {node!r} not in {schema["enum"]}')
    if t == 'object':
        for k in schema.get('required', []):
            if k not in node and not (path == '$' and k in NEW_IN and _older(version or '', NEW_IN[k])):
                errs.append(f'{path}: missing {k}')
        if schema.get('additionalProperties') is False:
            for k in node:
                if k not in schema['properties']:
                    errs.append(f'{path}: unexpected {k}')
        for k, sub in schema.get('properties', {}).items():
            if k in node:
                check(node[k], sub, f'{path}.{k}', errs)
    if t == 'array':
        for i, item in enumerate(node):
            check(item, schema['items'], f'{path}[{i}]', errs)


def validate(c: dict) -> list[str]:
    errs: list[str] = []
    check(c, SCHEMA, '$', errs, c.get('codebook_version'))
    for s in c.get('sequences', []):
        for i, st in enumerate(s.get('steps', []), 1):
            if st.get('n') != i:
                errs.append(f'{s.get("kind")} step {i}: numbered {st.get("n")}')
            if not str(st.get('page', '')).strip():
                errs.append(f'{s.get("kind")} step {i}: no page')
            if len(str(st.get('quote', '')).split()) > 25:
                errs.append(f'{s.get("kind")} step {i}: quote over 25 words')
    if not any(s.get('kind') == 'final_paper' for s in c.get('sequences', [])):
        errs.append('no final_paper sequence')
    if 'v_checks' in c:  # codebook 1.5.0, section 3a (NASEM 2019)
        here = [v for v in c['v_checks'] if v.get('performed_here') is True]
        has_v = any(st.get('node') == 'V' for s in c.get('sequences', []) if s.get('kind') == 'final_paper' for st in s.get('steps', []))
        if has_v and not here:
            errs.append('V steps in the final paper but no check performed here in v_checks (codebook 3a)')
        for i, v in enumerate(c['v_checks'], 1):
            if len(str(v.get('quote', '')).split()) > 25:
                errs.append(f'v_checks {i}: quote over 25 words')
            if not str(v.get('page', '')).strip():
                errs.append(f'v_checks {i}: no page')
    return errs


def v_status(c: dict) -> dict:
    """NASEM V for a paper (codebook 1.5.0, section 3a): full, partial or none, and whether it triangulates."""
    here = [v['kind'] for v in c.get('v_checks', []) if v.get('performed_here') is True]
    mark = 'full' if any(k != 'reproduction' for k in here) else ('partial' if here else 'none')
    tri = len({k for k in here if k in ('replication', 'method', 'generalization')}) >= 2
    return {'v': mark, 'triangulation': tri, 'kinds': sorted(set(here))}


def runs(xs):
    out = []
    for x in xs:
        if not out or out[-1] != x:
            out.append(x)
    return out


def edit(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (x != y))
    return d[len(b)]


def seq(c, field):
    s = next(s for s in c['sequences'] if s['kind'] == 'final_paper')
    return runs([st[field] for st in s['steps']])


def jacc(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


def agree(a: dict, b: dict) -> dict:
    na, nb, ma, mb = seq(a, 'node'), seq(b, 'node'), seq(a, 'mode'), seq(b, 'mode')
    sim = lambda x, y: 1 - edit(x, y) / max(len(x), len(y), 1)
    return {'entry_node': a['entry']['node'] == b['entry']['node'], 'entry_state': a['entry']['state'] == b['entry']['state'],
            'outcome': a['end']['outcome'] == b['end']['outcome'], 'decisive_mode': a['decisive_move']['mode'] == b['decisive_move']['mode'],
            'node_set_jaccard': round(jacc(na, nb), 2), 'mode_set_jaccard': round(jacc(ma, mb), 2),
            'node_seq_similarity': round(sim(na, nb), 2), 'mode_seq_similarity': round(sim(ma, mb), 2),
            'steps': (len(na), len(nb))}


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__); return 2
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'validate':
        bad = 0
        for p in args:
            errs = validate(json.loads(Path(p).read_text()))
            print(f'{p}: {"ok" if not errs else str(len(errs)) + " problems"}')
            for e in errs[:20]:
                print('   ', e)
            bad += bool(errs)
        return 1 if bad else 0
    if cmd == 'agree':
        print(json.dumps(agree(*(json.loads(Path(p).read_text()) for p in args[:2])), indent=1)); return 0
    if cmd == 'agree-dir':
        A, B = Path(args[0]), Path(args[1]); rows = []
        for pa in sorted(A.glob('*.json')):
            pb = B / pa.name
            if pb.exists():
                r = agree(json.loads(pa.read_text()), json.loads(pb.read_text())); rows.append(r)
                print(pa.stem, json.dumps(r))
        if rows:
            mean = lambda k: round(sum(r[k] for r in rows) / len(rows), 2)
            print('mean', {k: mean(k) for k in ['entry_node', 'outcome', 'decisive_mode', 'node_set_jaccard', 'mode_set_jaccard', 'node_seq_similarity', 'mode_seq_similarity']})
        return 0
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main())
