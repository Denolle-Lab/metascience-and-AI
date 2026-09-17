#!/usr/bin/env python3
"""Compute citation-based indicators for the seminar's assigned papers from OpenAlex.

For each paper that has a DOI, the script records what OpenAlex knows (citations,
the field-and-year citation percentile, counts by year, topic) and computes two
indicators the seminar reads about: the CD_5 disruption index of Funk and
Owen-Smith (2017) as used by Wu, Wang, and Evans (2019), and the Ke and colleagues
(2015) sleeping-beauty coefficient. Both are computed from OpenAlex's citation
graph, which is not the Web of Science data the original papers used; the
numbers are for the group's own comparison, not for publication.

CD_5: among works citing the focal paper within five years of its publication
plus works citing only its references in that window, CD = (n_i - n_j) / n_total,
where n_i cite the focal paper but none of its references, n_j cite both, and
n_k cite only the references. CD_5 near +1: the citers ignore the paper's
references (disruptive). Near -1: the citers also cite its references
(developing). n_k requires querying each of the focal paper's references for
citers, which is expensive; by default only n_i and n_j are computed and the
"CD_5 (no n_k)" column says so. Pass --with-nk to compute the full index.

Sleeping beauty B (Ke et al. 2015): sum over years t of the gap between the
straight line from (0, c_0) to (t_m, c_max) and the actual citations c_t,
divided by max(1, c_t), for t from 0 to t_m, the year of maximum citations.
Large B: a long dormancy followed by a burst.

Usage: .venv/bin/python tools/indicators.py [--keys platt1964 cleland2001 ...]
       [--assigned] [--with-nk] [--out private/indicators.json]
"""
from __future__ import annotations
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT = 'metascience-seminar-indicators/1.0 (mailto:mdenolle@uw.edu)'
API = 'https://api.openalex.org'


def get(url: str) -> dict:
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': AGENT}), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return {}
            time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    return {}


def paged(url: str, select: str, per_page: int = 200, cap: int = 5000) -> list[dict]:
    out, cursor = [], '*'
    while cursor and len(out) < cap:
        page = get(f'{url}&select={select}&per-page={per_page}&cursor={cursor}&mailto=mdenolle@uw.edu')
        out.extend(page.get('results', []))
        cursor = (page.get('meta') or {}).get('next_cursor')
        time.sleep(0.25)
    return out


def work(doi: str) -> dict:
    return get(f'{API}/works/doi:{urllib.parse.quote(doi, safe="")}?mailto=mdenolle@uw.edu'
               '&select=id,title,publication_year,cited_by_count,counts_by_year,cited_by_percentile_year,'
               'referenced_works,primary_topic,open_access')


def cd_index(w: dict, with_nk: bool) -> dict:
    wid = w['id'].rsplit('/', 1)[-1]
    year = w['publication_year']
    refs = set(w.get('referenced_works') or [])
    window = f'from_publication_date:{year}-01-01,to_publication_date:{year + 5}-12-31'
    citers = paged(f'{API}/works?filter=cites:{wid},{window}', 'id,referenced_works')
    n_i = n_j = 0
    for c in citers:
        if refs & set(c.get('referenced_works') or []):
            n_j += 1
        else:
            n_i += 1
    result = {'n_i': n_i, 'n_j': n_j, 'citers_in_window': len(citers), 'references': len(refs)}
    if with_nk and refs:
        citer_ids = {c['id'] for c in citers}
        n_k_ids: set[str] = set()
        for ref in sorted(refs):
            rid = ref.rsplit('/', 1)[-1]
            for c in paged(f'{API}/works?filter=cites:{rid},{window}', 'id', cap=2000):
                if c['id'] not in citer_ids:
                    n_k_ids.add(c['id'])
        n_k = len(n_k_ids)
        total = n_i + n_j + n_k
        result.update({'n_k': n_k, 'CD_5': (n_i - n_j) / total if total else None})
    else:
        total = n_i + n_j
        result.update({'n_k': None, 'CD_5_no_nk': (n_i - n_j) / total if total else None})
    return result


def sleeping_beauty(w: dict) -> dict:
    counts = {c['year']: c['cited_by_count'] for c in (w.get('counts_by_year') or [])}
    if not counts:
        return {'B': None, 'note': 'OpenAlex counts_by_year covers only recent years'}
    y0 = w['publication_year']
    years = sorted(counts)
    series = [(y, counts[y]) for y in years]
    ymax, cmax = max(series, key=lambda p: p[1])
    tm = ymax - y0
    c0 = counts.get(y0, 0)
    b = 0.0
    for y, c in series:
        t = y - y0
        if t > tm or tm == 0:
            continue
        line = c0 + (cmax - c0) * t / tm
        b += (line - c) / max(1, c)
    return {'B': round(b, 2), 'awakening_year': ymax, 'peak_citations_per_year': cmax,
            'note': 'computed on OpenAlex counts_by_year, which starts in 2012; papers older than that lose their dormancy period'}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--keys', nargs='*')
    ap.add_argument('--assigned', action='store_true', help='all anchor, companion, and discussant papers')
    ap.add_argument('--with-nk', action='store_true')
    ap.add_argument('--out', default=str(ROOT / 'private' / 'indicators.json'))
    args = ap.parse_args()
    data = json.loads((ROOT / 'curriculum.json').read_text())
    refs = data['references']
    keys = list(args.keys or [])
    if args.assigned:
        for s in data['sessions']:
            keys += list(s['pair']) + list(s.get('discussant', []))
    if not keys:
        ap.error('give --keys or --assigned')
    out = {}
    for key in dict.fromkeys(keys):
        doi = refs.get(key, {}).get('doi')
        if not doi:
            out[key] = {'note': 'no DOI'}
            print(f'{key:16} no DOI', file=sys.stderr)
            continue
        w = work(doi)
        if not w:
            out[key] = {'note': 'not in OpenAlex'}
            continue
        pct = w.get('cited_by_percentile_year') or {}
        rec = {'title': w.get('title'), 'year': w.get('publication_year'), 'citations': w.get('cited_by_count'),
               'percentile_min': pct.get('min'), 'percentile_max': pct.get('max'),
               'topic': (w.get('primary_topic') or {}).get('display_name'),
               'cd': cd_index(w, args.with_nk), 'sleeping_beauty': sleeping_beauty(w),
               'source': 'OpenAlex', 'retrieved': time.strftime('%Y-%m-%d')}
        out[key] = rec
        cd = rec['cd'].get('CD_5', rec['cd'].get('CD_5_no_nk'))
        print(f"{key:16} {rec['year']}  cites={rec['citations']:>6}  pct={pct.get('min')}-{pct.get('max')}  "
              f"CD5={'n/a' if cd is None else f'{cd:+.2f}'} (n_i={rec['cd']['n_i']}, n_j={rec['cd']['n_j']})  B={rec['sleeping_beauty'].get('B')}")
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(f'wrote {args.out}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
