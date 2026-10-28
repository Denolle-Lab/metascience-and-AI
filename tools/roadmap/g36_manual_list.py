"""Hand-download list for the eligible round-1 and round-2 papers that still have no full text.

Decided by the PI on October 28, 2026 (DECISIONS.md): every eligible round-1 and round-2 paper is coded completely.
Springer and Pleiades papers (DOI prefixes 10.1007, 10.1134, 10.3103) wait for a Springer Nature TDM key and are
listed apart; everything else (SSA, Oxford GJI, AAAS, GeoScienceWorld, ...) is downloaded by hand through UW Libraries
into ~/Dropbox/ARTICLES/METASCIENCE, which tools/fetch_pdfs.py indexes by the DOI printed in the PDF. Papers the PI
excluded (queue status 'skipped', Russian Geology and Geophysics) are left out.

Inputs   derived/calc1/manifest.jsonl, derived/r2calc/manifest.jsonl, private/download-queue.json, derived/{gold,r2}/metrics.json
Output   private/data/roadmap/manual_downloads.md (checklist by publisher, with DOI and UW Libraries proxy links)
Run:     python tools/roadmap/g36_manual_list.py
"""
import json
from collections import defaultdict

from common import DERIVED, PRIVATE, log, read_json

KEY_ROUTE = ('10.1007', '10.1134', '10.3103')
PROXY = 'https://offcampus.lib.washington.edu/login?url=https://doi.org/'


def main() -> None:
    q = json.loads((PRIVATE / 'download-queue.json').read_text())
    meta = {}
    for s in ('gold', 'r2'):
        for r in read_json(DERIVED / s / 'metrics.json'):
            meta['g22_' + r['id'].split('/')[-1]] = r
    groups, keyed = defaultdict(list), []
    for rnd, m in (('round 1', 'calc1'), ('round 2', 'r2calc')):
        for line in (DERIVED / m / 'manifest.jsonl').read_text().splitlines():
            r = json.loads(line)
            st = (q.get(r['key']) or {}).get('status')
            if st in ('have', 'skipped'):
                continue
            x = meta.get(r['key'], {})
            row = (rnd, r['key'], r['doi'], x.get('title') or '', x.get('journal') or '')
            if r['doi'].startswith(KEY_ROUTE):
                keyed.append(row)
            else:
                groups[x.get('publisher') or r['doi'].split('/')[0]].append(row)
    n = sum(len(v) for v in groups.values())
    md = ['# Papers to download by hand (rounds 1 and 2)', '',
          f'{n} papers. Save each PDF into ~/Dropbox/ARTICLES/METASCIENCE (any file name; the fetcher matches the DOI in the PDF), '
          'then run `python tools/fetch_pdfs.py run --out private/data/roadmap/pdfs/gold`.', '']
    for pub in sorted(groups, key=lambda p: -len(groups[p])):
        md += [f'## {pub} ({len(groups[pub])})', '']
        md += [f'- [ ] {t} ({j}, {rnd}): [{d}]({PROXY}{d})' for rnd, k, d, t, j in sorted(groups[pub], key=lambda r: r[4])]
        md.append('')
    md += [f'## Waiting for the Springer Nature TDM key ({len(keyed)})', '',
           'Fetched automatically once SPRINGER_TDM_API_KEY is set in ~/.config/metascience/keys.env.', '']
    md += [f'- {t} ({j}, {rnd}): {d}' for rnd, k, d, t, j in sorted(keyed, key=lambda r: r[4])]
    out = PRIVATE / 'data' / 'roadmap' / 'manual_downloads.md'
    out.write_text('\n'.join(md) + '\n')
    log('g36_manual_list.py', 'hand-download list for rounds 1-2', n + len(keyed), f'{n} by hand, {len(keyed)} via Springer key')
    print(f'{out}: {n} by hand, {len(keyed)} via the Springer key')


if __name__ == '__main__':
    main()
