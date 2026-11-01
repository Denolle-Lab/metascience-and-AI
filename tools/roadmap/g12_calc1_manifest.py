#!/usr/bin/env python3
"""First calculation, step 1: the corpus manifest, the eligible papers of the 600-paper 2022 preselection.

Input : derived/gold/preselect.json (g03), derived/gold/eligibility.json (g07), derived/gold/gold_set.json (g05)
Output: derived/calc1/manifest.jsonl   one line per eligible paper: key, doi, stratum ('calc1 core' / 'calc1 broad'),
                                       openalex id, in_gold (bool); the input to fetch_pdfs.py add-manifest and to
                                       code_papers.py --manifest
Run   : python tools/roadmap/g12_calc1_manifest.py
"""
from __future__ import annotations
import json
from common import SET, CALC, DERIVED, decision, log, read_json


def main() -> None:
    pre = read_json(SET / 'preselect.json')
    ok = {d['key'] for d in read_json(SET / 'eligibility.json') if d.get('eligible') is True}
    gold = {g['key'] for g in read_json(SET / 'gold_set.json')} if (SET / 'gold_set.json').is_file() else set()
    out = CALC / 'manifest.jsonl'
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in sorted(pre, key=lambda p: p['id']):
        k = 'g22_' + p['id']
        if k in ok:
            rows.append({'key': k, 'doi': p['doi'], 'stratum': f"{CALC.name} {p['ring']}", 'openalex': p['id'], 'in_gold': k in gold})
    out.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    log('g12_calc1_manifest.py', 'first-calculation corpus manifest (eligible papers of the 600 preselected)', len(rows),
        f"{sum(r['in_gold'] for r in rows)} also in the gold set")
    decision(f'First calculation corpus = the {len(rows)} eligible papers of the 600-paper 2022 preselection (eligibility screen '
             'wf_658989aa-088); the 100 gold papers are a subset and are coded a second time independently.')
    print(len(rows), 'papers;', sum(r['in_gold'] for r in rows), 'in gold')


if __name__ == '__main__':
    main()
