#!/usr/bin/env python3
"""Gold set, step 6: titles, venues and abstracts of the preselected papers, as input to the eligibility screen.

Input : derived/gold/preselect.json (g03)
Output: derived/gold/screen_input.json  [{key, id, doi, title, journal, topic, subfield, abstract}]
        Abstracts are rebuilt from OpenAlex's abstract_inverted_index (word -> positions).
Run   : python tools/roadmap/g06_abstracts.py
"""
from __future__ import annotations
from common import SET, CALC, DERIVED, log, openalex, read_json, write_json


def rebuild(inv: dict | None) -> str:
    if not inv:
        return ''
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return ' '.join(w for _, w in pos)


def main() -> None:
    pre = read_json(SET / 'preselect.json')
    out = []
    for i in range(0, len(pre), 50):
        chunk = pre[i:i + 50]
        res = openalex('works', {'filter': 'openalex_id:' + '|'.join(p['id'] for p in chunk),
                                 'select': 'id,abstract_inverted_index,type,type_crossref', 'per-page': 50}).get('results', [])
        ab = {r['id'].rsplit('/', 1)[-1]: r for r in res}
        for p in chunk:
            r = ab.get(p['id'], {})
            out.append({'key': 'g22_' + p['id'], 'id': p['id'], 'doi': p['doi'], 'title': p['title'], 'journal': p['journal'],
                        'topic': p['topic'], 'subfield': p['subfield'], 'type_crossref': r.get('type_crossref'),
                        'abstract': rebuild(r.get('abstract_inverted_index'))})
    write_json(SET / 'screen_input.json', out, ['derived/gold/preselect.json', 'OpenAlex abstract_inverted_index'])
    log('g06_abstracts.py', 'abstracts for the eligibility screen', len(out), f"{sum(1 for o in out if not o['abstract'])} without abstract")
    print(len(out), 'records;', sum(1 for o in out if not o['abstract']), 'without abstract')


if __name__ == '__main__':
    main()
