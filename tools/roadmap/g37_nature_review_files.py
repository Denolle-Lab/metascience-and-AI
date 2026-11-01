"""Peer review files of the Nature Portfolio papers of rounds 1 and 2 (the cop22 NC and CEE papers have theirs from
g32 `prf`), so the Nature-family review coding (tools/roadmap/g27_nature_units.py, agents/coder/REVIEW_ADDENDUM_NATURE.md)
covers every eligible round-1 and round-2 paper that has one (PI, October 28, 2026: every eligible round-1 and round-2
paper is coded completely, all layers that exist for it).

Papers   every row of derived/calc1/manifest.jsonl (round 1, eligible) and derived/r2calc/manifest.jsonl (round 2,
         eligible) whose DOI starts 10.1038/ (Nature Portfolio: Nature Communications s41467, Communications Earth &
         Environment s43247, Nature s41586, Nature Geoscience s41561, Nature Climate Change s41558, npj Climate and
         Atmospheric Science s41612, Nature Ecology & Evolution s41559, Scientific Reports s41598, ...).
Fetch    as g32 `prf`: the article page https://www.nature.com/articles/<suffix> read once through g28.page (evidence
         only, g28.nature_evidence: links labelled 'peer review file', the 'Peer review information' sentence); each
         linked PDF saved as review/<key>/<file>.pdf (open download, no key, 2 s pause, each request in
         raw/inventory/fetch_log.jsonl), the located text review/<key>/peer_review.txt ("[PRF1 p.3] ..."). Nothing is
         fetched for a paper whose article page links no peer review file.
Output   derived/review/open_review_index_nature12.json: per paper key, doi, round, journal (DOI prefix), page status,
         peer_review_information, files (url, file, bytes, sha256, pages), words, has_author_response (g32 phrase rule),
         and the g27_nature_units parse result (rounds, R/E/A units, clean) when a file was saved.
Run      python tools/roadmap/g37_nature_review_files.py fetch [--keys k1,k2]
"""
from __future__ import annotations
import argparse
import hashlib
import re
import subprocess
import urllib.parse
from collections import Counter

from common import DATA, DERIVED, TODAY, log, rel, write_json
import rounds
import g28_review_inventory as g28
import g27_nature_units as g27n

INDEX = DERIVED / 'review' / 'open_review_index_nature12.json'
ROUNDS = (('round1', 'calc1'), ('round2', 'r2calc'))
AUTHOR_RESPONSE = re.compile(r'(?i)response to (?:the )?reviewers?|point[- ]by[- ]point|we thank the reviewers?|'
                             r"authors?['’]? (?:response|reply)|rebuttal|our response")   # g32 prf rule
PREFIX = {'s41467': 'NC', 's43247': 'CEE', 's41586': 'Nature', 's41561': 'NGEO', 's41558': 'NCC', 's41612': 'npjCAS',
          's41559': 'NEE', 's41598': 'SciRep'}


def papers(keys: set | None = None) -> list[dict]:
    out = []
    for name, folder in ROUNDS:
        for r in rounds.manifest(folder):
            doi = (r.get('doi') or '').lower()
            if doi.startswith('10.1038/') and (not keys or r['key'] in keys):
                m = re.match(r'10\.1038/(s\d+)-', doi)
                out.append({'key': r['key'], 'doi': doi, 'round': name,
                            'journal': PREFIX.get(m.group(1), m.group(1)) if m else 'other'})
    return out


def fetch_one(p: dict) -> dict:
    key, doi = p['key'], p['doi']
    d = DATA / 'review' / key
    ev = g28.page('https://www.nature.com/articles/' + doi.split('/', 1)[1], keep=False, extract=g28.nature_evidence)
    e = ev.get('evidence') or {}
    rec = {**p, 'page_status': ev.get('status'), 'peer_review_information': e.get('peer_review_information'),
           'prf_sentence': e.get('prf_sentence'), 'prf_links': e.get('prf_links') or [], 'files': []}
    lines = [f'# Peer review file of {doi}', '# Locator: [PRF<n> p.k] = page k of peer review file n.', '']
    for i, link in enumerate(rec['prf_links'], 1):
        url = link['href']
        f = d / urllib.parse.unquote(url.rsplit('/', 1)[1])
        if not f.is_file():
            status, final, body = g28._request(url)
            g28._logfetch({'url': url, 'final_url': final, 'date': TODAY, 'status': status, 'bytes': len(body),
                           'sha256': hashlib.sha256(body).hexdigest(), 'file': rel(f) if body[:4] == b'%PDF' else None})
            if status != 200 or body[:4] != b'%PDF':
                rec['files'].append({'url': url, 'status': status, 'error': 'not a PDF' if status == 200 else f'HTTP {status}'})
                continue
            d.mkdir(parents=True, exist_ok=True)
            f.write_bytes(body)
        pages = subprocess.run(['pdftotext', '-layout', str(f), '-'], capture_output=True, text=True).stdout.split('\f')
        lines += [f'[PRF{i} p.{n}] ' + re.sub(r'\s+', ' ', pg).strip() for n, pg in enumerate(pages, 1) if pg.strip()]
        rec['files'].append({'url': url, 'file': rel(f), 'bytes': f.stat().st_size,
                             'sha256': hashlib.sha256(f.read_bytes()).hexdigest(), 'pages': sum(1 for pg in pages if pg.strip())})
    if any('file' in x for x in rec['files']):
        txt = '\n'.join(lines)
        (d / 'peer_review.txt').write_text(txt + '\n')
        rec.update(words=len(txt.split()), has_author_response=bool(AUTHOR_RESPONSE.search(txt)))
        pr = g27n.parse_result(key, g27n.nature_units(key))
        rec['parse'] = {x: pr[x] for x in ('clean', 'problem', 'rounds', 'rounds_with_response', 'R_units', 'E_units',
                                          'A_units', 'A_units_with_own_text')}
    rec['has_review_file'] = any('file' in x for x in rec['files'])
    return rec


def fetch(keys: set | None) -> None:
    rows = []
    for p in papers(keys):
        r = fetch_one(p)
        rows.append(r)
        print(r['key'], r['round'], r['journal'], 'page', r['page_status'], 'links', len(r['prf_links']), 'files',
              sum('file' in x for x in r['files']), 'parse', (r.get('parse') or {}).get('clean'), flush=True)
    if keys:   # a partial run prints only
        return
    write_json(INDEX, rows, [rel(DERIVED / 'calc1' / 'manifest.jsonl'), rel(DERIVED / 'r2calc' / 'manifest.jsonl'),
                             'nature.com article pages (evidence only) and peer review files (static-content.springer.com)'],
               {'pause_s': 2.0, 'reader': f'g27_nature_units {g27n.VERSION}'})
    got = [r for r in rows if r['has_review_file']]
    by = Counter(f"{r['round']}|{r['journal']}|{'file' if r['has_review_file'] else 'none'}" for r in rows)
    log('g37_nature_review_files.py fetch', 'peer review files of the round-1 and round-2 Nature Portfolio papers', len(rows),
        f"{len(got)} of {len(rows)} with a peer review file; {sum((r.get('parse') or {}).get('clean', False) for r in got)} parse "
        f"cleanly; {dict(sorted(by.items()))}; web {dict(g28._n)}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['fetch'])
    ap.add_argument('--keys', default=None)
    a = ap.parse_args()
    fetch(set(a.keys.split(',')) if a.keys else None)
