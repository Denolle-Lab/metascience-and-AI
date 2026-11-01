"""Hand-download list for the eligible round-1 and round-2 papers that still have no full text.

Decided by the PI on October 28, 2026 (DECISIONS.md): every eligible round-1 and round-2 paper is coded completely.
On October 29 the PI found no Springer Nature TDM key is available to her personal or academic account, so Springer and
Pleiades papers (DOI prefixes 10.1007, 10.1134, 10.3103) are downloaded by hand too. All are saved through UW Libraries
into ~/Dropbox/ARTICLES/METASCIENCE, which tools/fetch_pdfs.py indexes by the DOI printed in the PDF. The other
publishers (SSA, Oxford GJI, AAAS, ...) come first, as before, so a place in the list stays put; the Springer and
Pleiades papers follow. Papers the PI excluded (queue status 'skipped', Russian Geology and Geophysics) are left out.

Inputs   derived/calc1/manifest.jsonl, derived/r2calc/manifest.jsonl, private/download-queue.json, derived/{gold,r2}/metrics.json
Output   private/data/roadmap/manual_downloads.md (checklist by publisher, with DOI and UW Libraries proxy links)
Run:     python tools/roadmap/g36_manual_list.py
"""
import json
from collections import defaultdict

from common import DERIVED, PRIVATE, log, read_json

SPRINGER = {'10.1007': 'Springer', '10.1134': 'Pleiades Publishing (Springer)', '10.3103': 'Allerton Press (Springer)'}
PROXY = 'https://offcampus.lib.washington.edu/login?url=https://doi.org/'


def main() -> None:
    q = json.loads((PRIVATE / 'download-queue.json').read_text())
    meta = {}
    for s in ('gold', 'r2'):
        for r in read_json(DERIVED / s / 'metrics.json'):
            meta['g22_' + r['id'].split('/')[-1]] = r
    groups, springer = defaultdict(list), defaultdict(list)
    for rnd, m in (('round 1', 'calc1'), ('round 2', 'r2calc')):
        for line in (DERIVED / m / 'manifest.jsonl').read_text().splitlines():
            r = json.loads(line)
            st = (q.get(r['key']) or {}).get('status')
            if st in ('have', 'skipped'):
                continue
            x = meta.get(r['key'], {})
            row = (rnd, r['key'], r['doi'], x.get('title') or '', x.get('journal') or '')
            prefix = r['doi'].split('/')[0]
            if prefix in SPRINGER:
                springer[SPRINGER[prefix]].append(row)
            else:
                groups[x.get('publisher') or r['doi'].split('/')[0]].append(row)
    n = sum(len(v) for v in groups.values())
    n_s = sum(len(v) for v in springer.values())
    md = ['# Papers to download by hand (rounds 1 and 2)', '',
          f'{n + n_s} papers ({n} from SSA, AAAS, Elsevier, Wiley and Oxford, then {n_s} from Springer and its partner presses). Save each PDF into ~/Dropbox/ARTICLES/METASCIENCE (any file name; the fetcher matches the DOI in the PDF), '
          'then run `python tools/fetch_pdfs.py run --library-only --out private/data/roadmap/pdfs/gold` (matches the folder only; no publisher is contacted) and `python tools/roadmap/g36_manual_list.py` to drop what you have from this list.', '']
    for pub in sorted(groups, key=lambda p: -len(groups[p])):
        md += [f'## {pub} ({len(groups[pub])})', '']
        md += [f'- [ ] {t} ({j}, {rnd}): [{d}]({PROXY}{d})' for rnd, k, d, t, j in sorted(groups[pub], key=lambda r: r[4])]
        md.append('')
    for pub in sorted(springer, key=lambda p: -len(springer[p])):
        md += [f'## {pub} ({len(springer[pub])})', '']
        md += [f'- [ ] {t} ({j}, {rnd}): [{d}]({PROXY}{d})' for rnd, k, d, t, j in sorted(springer[pub], key=lambda r: (r[4], r[3]))]
        md.append('')
    out = PRIVATE / 'data' / 'roadmap' / 'manual_downloads.md'
    out.write_text('\n'.join(md) + '\n')
    log('g36_manual_list.py', 'hand-download list for rounds 1-2', n + n_s, f'{n} other publishers, {n_s} Springer and partners, all by hand')
    print(f'{out}: {n + n_s} by hand ({n} other publishers, {n_s} Springer and partners)')


if __name__ == '__main__':
    main()
