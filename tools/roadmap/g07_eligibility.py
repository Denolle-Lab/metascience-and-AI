#!/usr/bin/env python3
"""Gold set, step 7: store the eligibility screen's decisions as a derived table.

Input : the JSON returned by the workflow tools/roadmap/workflows/gold-eligibility-screen.js (run id given on the command line),
        saved by the operator to a file; derived/gold/screen_input.json for the record list
Output: derived/gold/eligibility.json  one row per paper: eligible, category, both screeners' calls, the adjudication
Run   : python tools/roadmap/g07_eligibility.py RESULT.json --run-id wf_...
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from common import DERIVED, decision, log, read_json, write_json


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('result')
    ap.add_argument('--run-id', required=True)
    a = ap.parse_args()
    res = json.load(open(a.result))
    dec = {d['key']: d for d in res['decisions']}
    recs = read_json(DERIVED / 'gold' / 'screen_input.json')
    rows = []
    for r in recs:
        d = dec.get(r['key'])
        rows.append({'key': r['key'], 'eligible': d.get('eligible') if d else None, 'category': d.get('category') if d else None,
                     'adjudicated': d.get('adjudicated') if d else None, 'screenA': d.get('screenA') if d else None,
                     'screenB': d.get('screenB') if d else None, 'adjudication': d.get('adjudication') if d else None})
    both = [x for x in rows if x['screenA'] and x['screenB']]
    agree = sum(1 for x in both if x['screenA']['eligible'] == x['screenB']['eligible'])
    write_json(DERIVED / 'gold' / 'eligibility.json', rows, ['derived/gold/screen_input.json', f'workflow {a.run_id}'],
               {'workflow': 'tools/roadmap/workflows/gold-eligibility-screen.js', 'run_id': a.run_id})
    c = Counter(x['category'] for x in rows)
    log('g07_eligibility.py', f'eligibility screen (workflow {a.run_id})', len(rows),
        f"{sum(1 for x in rows if x['eligible'])} eligible; screener agreement {agree}/{len(both)}; "
        f"{sum(1 for x in rows if x['adjudicated'])} adjudicated; {sum(1 for x in rows if x['eligible'] is None)} undecided")
    decision(f'Eligibility screen (workflow {a.run_id}): two independent model screeners per abstract, a third on every disagreement '
             f'or low-confidence call; criteria in tools/roadmap/workflows/gold-eligibility-screen.js. Only eligible papers enter the gold set. '
             f'Categories: {dict(c)}.')
    print(dict(c), f'agreement {agree}/{len(both)}')


if __name__ == '__main__':
    main()
