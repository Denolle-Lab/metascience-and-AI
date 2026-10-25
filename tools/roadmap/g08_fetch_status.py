#!/usr/bin/env python3
"""Gold set, step 8: full-text status and licence for every gold paper.

Input : derived/gold/gold_set.json (g05); private/download-queue.json (state written by tools/fetch_pdfs.py);
        PDFs in private/data/roadmap/pdfs/gold/
Output: derived/gold/fetch_status.json  per paper: fetched?, file, route tried, OpenAlex licence of the best open copy,
        and `model_coding` = 'open_licence' (CC licence: may be sent to a model service now) or 'hold_licence'
        (subscription or no licence: held until UW Libraries confirms the TDM terms allow it) or 'missing'
        `version` = 'doi_printed' (the PDF's first pages print the paper's DOI), 'other_version' (they print another DOI
        of the same publisher, e.g. a discussion preprint), or 'unverified' (no DOI found; matched on title only)
        --requeue-mismatch moves 'other_version' PDFs aside (<key>.other-version.pdf) and marks them missing in the queue
Run   : python tools/roadmap/g08_fetch_status.py [--requeue-mismatch]
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from common import DERIVED, ROOT, decision, log, openalex, read_json, write_json

PDFS = ROOT / 'private' / 'data' / 'roadmap' / 'pdfs' / 'gold'
QUEUE = ROOT / 'private' / 'download-queue.json'


sys.path.insert(0, str(ROOT / 'tools'))
import fetch_pdfs  # noqa: E402


def version_of(pdf, doi) -> str:
    m = fetch_pdfs.matches(pdf, doi, '')
    return 'doi_printed' if m == 'doi found' else ('other_version' if 'other version' in m else 'unverified')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--requeue-mismatch', action='store_true')
    a = ap.parse_args()
    gold = read_json(DERIVED / 'gold' / 'gold_set.json')
    q = json.loads(QUEUE.read_text()) if QUEUE.is_file() else {}
    moved = []
    if a.requeue_mismatch:
        for g in gold:
            f = PDFS / f"{g['key']}.pdf"
            if f.is_file() and version_of(f, g['doi']) == 'other_version':
                f.replace(f.with_suffix('.other-version.pdf'))
                if g['key'] in q:
                    q[g['key']].update(status='missing', route=None, file=None)
                moved.append(g['key'])
        QUEUE.write_text(json.dumps(q, indent=1, ensure_ascii=False))
        if moved:
            decision(f'{len(moved)} gold PDFs were another version of the paper (discussion preprints), moved aside and re-queued: '
                     f'{", ".join(moved)}. The fetcher now rejects a PDF that prints another DOI of the same publisher and tries the '
                     'Copernicus final article first.')
    lic = {}
    for i in range(0, len(gold), 50):
        res = openalex('works', {'filter': 'openalex_id:' + '|'.join(g['id'] for g in gold[i:i + 50]),
                                 'select': 'id,open_access,best_oa_location,primary_location', 'per-page': 50}).get('results', [])
        for r in res:
            b = r.get('best_oa_location') or {}
            lic[r['id'].rsplit('/', 1)[-1]] = {'oa_status': (r.get('open_access') or {}).get('oa_status'),
                                                'license': b.get('license') or (r.get('primary_location') or {}).get('license')}
    rows = []
    for g in gold:
        f = PDFS / f"{g['key']}.pdf"
        st = q.get(g['key'], {})
        L = lic.get(g['id'], {})
        cc = (L.get('license') or '').startswith('cc')
        rows.append({'key': g['key'], 'doi': g['doi'], 'journal': g['journal'], 'route_class': g['route'],
                     'fetched': f.is_file(), 'file': str(f.relative_to(ROOT)) if f.is_file() else None,
                     'queue_status': st.get('status'), 'route': st.get('route'), 'tried': st.get('tried'),
                     'oa_status': L.get('oa_status'), 'license': L.get('license'),
                     'version': version_of(f, g['doi']) if f.is_file() else None,
                     'model_coding': ('open_licence' if cc else 'hold_licence') if f.is_file() else 'missing'})
    write_json(DERIVED / 'gold' / 'fetch_status.json', rows, ['derived/gold/gold_set.json', 'private/download-queue.json', 'OpenAlex best_oa_location'])
    c = Counter(r['model_coding'] for r in rows)
    log('g08_fetch_status.py', 'gold-set full-text and licence status', len(rows), ', '.join(f'{k} {v}' for k, v in c.items()))
    decision('Model coding of full text: papers whose best open copy carries a Creative Commons licence are coded now; subscription '
             'papers fetched through publisher TDM routes are held until UW Libraries confirms the terms allow sending text to a '
             'model service (roadmap Phase 0, licence question).')
    print(dict(c), Counter(r['version'] for r in rows if r['fetched']), 'moved aside:', moved)


if __name__ == '__main__':
    main()
