#!/usr/bin/env python3
"""Build a paper corpus (manifest) from OpenAlex for coding at scale.

  python3 tools/corpus.py --name ns2005 --sources S137773608,S3880285 --years 2005-2015 \
      --field 19 --n 1000 --strata citation-decile --seed 2026
  python3 tools/corpus.py --name geo-journals --issn 0094-8276,2169-9356 --years 2010-2020 --n 500

Writes private/corpus/<name>.jsonl, one paper per line:
  key, doi, title, year, venue, source_id, cited_by_count, cnp (field-normalized percentile), fwci,
  subfield, referenced_works_count, is_oa, oa_url, stratum
and private/corpus/<name>.meta.json with the query, the pool size, and the random seed.

Pool rules: type article; primary field = --field (OpenAlex field id; 19 = Earth and Planetary
Sciences); at least --min-refs references; not retracted; titles that look like corrections,
replies, comments, news, or editorials dropped. Strata:
  citation-decile  deciles of cited_by_count within each source x year (draws spread over deciles)
  year             equal draws per year
  none             simple random sample
OpenAlex is queried anonymously by default. Set OPENALEX_API_KEY to use a key; nothing else
identifying is sent.
"""
from __future__ import annotations
import argparse, json, os, random, re, sys, time, urllib.error, urllib.parse, urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import keys  # noqa: E402
keys.load()
OUT = ROOT / 'private' / 'corpus'
API = 'https://api.openalex.org/works'
UA = {'User-Agent': 'metascience-seminar-corpus/1.0'}
SELECT = ('id,doi,title,publication_year,primary_location,cited_by_count,citation_normalized_percentile,'
          'fwci,primary_topic,referenced_works_count,open_access,is_retracted,authorships,type')
DROP = re.compile(r'^(correction|erratum|retraction|reply|response|comment|news|editorial|author correction|publisher correction)\b', re.I)


def get(url: str) -> dict:
    key = os.environ.get('OPENALEX_API_KEY')
    if key:
        url += ('&' if '?' in url else '?') + 'api_key=' + urllib.parse.quote(key)
    for a in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and a < 5:
                time.sleep(int(e.headers.get('Retry-After') or 0) or 2 ** a * 5); continue
            if e.code >= 500 and a < 5:
                time.sleep(2 ** a * 3); continue
            raise
        except Exception:  # noqa: BLE001
            time.sleep(2 ** a * 2)
    raise SystemExit(f'failed: {url}')


def pool(filters: list[str], cap: int) -> list[dict]:
    out, page = [], 1
    base = f'{API}?filter={",".join(filters)}&select={SELECT}&per-page=200'
    while len(out) < cap:
        r = get(f'{base}&page={page}').get('results', [])
        out += r
        if len(r) < 200:
            break
        page += 1; time.sleep(0.2)
    return out


def key_for(w: dict, used: set) -> str:
    au = (w.get('authorships') or [{}])[0].get('author', {}).get('display_name') or 'anon'
    last = re.sub(r'[^a-z]', '', au.split()[-1].lower()) or 'anon'
    base = f'{last}{w.get("publication_year")}'
    k, i = base, 0
    while k in used:
        i += 1; k = base + 'abcdefghijklmnopqrstuvwxyz'[i - 1] if i <= 26 else f'{base}_{i}'
    used.add(k)
    return k


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--name', required=True)
    ap.add_argument('--sources', help='comma-separated OpenAlex source ids (e.g. S137773608 = Nature)')
    ap.add_argument('--issn', help='comma-separated ISSNs, alternative to --sources')
    ap.add_argument('--years', required=True, help='YYYY-YYYY')
    ap.add_argument('--field', default='19')
    ap.add_argument('--min-refs', type=int, default=15)
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--strata', choices=['citation-decile', 'year', 'none'], default='citation-decile')
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--cap', type=int, default=20000, help='maximum pool size read per source and year')
    args = ap.parse_args()
    y0, y1 = map(int, args.years.split('-'))
    srcs = [('primary_location.source.id', s) for s in args.sources.split(',')] if args.sources else \
           [('primary_location.source.issn', s) for s in (args.issn or '').split(',') if s]
    if not srcs:
        print('give --sources or --issn'); return 2
    cells: dict[tuple, list] = defaultdict(list)
    for fld, s in srcs:
        for y in range(y0, y1 + 1):
            f = [f'{fld}:{s}', f'publication_year:{y}', 'type:article', f'primary_topic.field.id:{args.field}',
                 f'referenced_works_count:>{args.min_refs - 1}', 'is_retracted:false']
            for w in pool(f, args.cap):
                if not w.get('doi') or DROP.match(w.get('title') or ''):
                    continue
                cells[(s, y)].append(w)
            print(f'{s} {y}: {len(cells[(s, y)])}', file=sys.stderr)
    rng = random.Random(args.seed)
    rows = []
    for (s, y), ws in cells.items():
        ws.sort(key=lambda w: w['cited_by_count'])
        for i, w in enumerate(ws):
            w['_stratum'] = f'decile {min(9, int(10 * i / len(ws))) + 1}' if args.strata == 'citation-decile' else (str(y) if args.strata == 'year' else 'all')
        rows += ws
    groups: dict[str, list] = defaultdict(list)
    for w in rows:
        groups[w['_stratum']].append(w)
    per = max(1, args.n // max(1, len(groups)))
    pick = []
    for g in sorted(groups):
        ws = sorted(groups[g], key=lambda w: w['id'])
        pick += rng.sample(ws, min(per, len(ws)))
    OUT.mkdir(parents=True, exist_ok=True)
    used: set = set()
    with open(OUT / f'{args.name}.jsonl', 'w') as fh:
        for w in sorted(pick, key=lambda w: (w['publication_year'], w['id'])):
            loc = (w.get('primary_location') or {}).get('source') or {}
            pt = w.get('primary_topic') or {}
            fh.write(json.dumps({'key': key_for(w, used), 'doi': w['doi'].replace('https://doi.org/', ''), 'title': w.get('title'),
                                 'year': w.get('publication_year'), 'venue': loc.get('display_name'), 'source_id': (loc.get('id') or '').rsplit('/', 1)[-1],
                                 'cited_by_count': w.get('cited_by_count'), 'cnp': (w.get('citation_normalized_percentile') or {}).get('value'),
                                 'fwci': w.get('fwci'), 'subfield': (pt.get('subfield') or {}).get('display_name'),
                                 'referenced_works_count': w.get('referenced_works_count'), 'is_oa': (w.get('open_access') or {}).get('is_oa'),
                                 'oa_url': (w.get('open_access') or {}).get('oa_url'), 'stratum': w['_stratum']}, ensure_ascii=False) + '\n')
    meta = {'name': args.name, 'args': vars(args), 'pool': len(rows), 'drawn': len(pick), 'strata': {g: len(v) for g, v in groups.items()},
            'retrieved': time.strftime('%Y-%m-%d'), 'source': 'OpenAlex works API'}
    (OUT / f'{args.name}.meta.json').write_text(json.dumps(meta, indent=1))
    print(f'{len(pick)} drawn from a pool of {len(rows)}; manifest {OUT / (args.name + ".jsonl")}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
