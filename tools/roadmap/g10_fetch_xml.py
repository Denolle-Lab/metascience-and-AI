#!/usr/bin/env python3
"""Gold set, step 10: publisher full-text XML for the gold papers, beside the PDFs, plus a located plain-text version.

Input : derived/gold/gold_set.json (g05); keys from keys.env (SPRINGER_OA_API_KEY, SPRINGER_TDM_API_KEY, ELSEVIER_API_KEY,
        ELSEVIER_INSTTOKEN)
Output: private/data/roadmap/pdfs/gold/<key>.xml        the publisher XML as delivered
        private/data/roadmap/pdfs/gold/<key>.xml.txt    tools/jats_text.py output: every paragraph with a §-locator
        derived/gold/xml_status.json                    per paper: route used, every attempt, accepted or not
Routes, in order (each attempt is recorded):
  copernicus   https://<journal>.copernicus.org/articles/<vol>/<page>/<year>/<name>.xml (all open access)
  springer     Springer Nature Open Access API (JATS); the TDM API when SPRINGER_TDM_API_KEY is set
  elsevier     Elsevier Article Retrieval API with Accept: text/xml (subscription entitlement by UW network or insttoken)
  europepmc    Europe PMC fullTextXML for papers with a PMCID
A file is accepted only if it parses, carries the article body (at least 15 paragraphs, so abstract-only responses are
rejected), and contains the paper's DOI or most of its title words.
Run   : python tools/roadmap/g10_fetch_xml.py [--keys g22_W... ...]
"""
from __future__ import annotations
import argparse
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from common import DERIVED, ROOT, log, openalex, read_json, sid, write_json

sys.path.insert(0, str(ROOT / 'tools'))
import jats_text  # noqa: E402

OUT = ROOT / 'private' / 'data' / 'roadmap' / 'pdfs' / 'gold'
UA = 'metascience-roadmap/1.0'


def fetch(url: str, headers: dict | None = None) -> tuple[bytes | None, str]:
    req = urllib.request.Request(url, headers={'User-Agent': UA, **(headers or {})})
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read(), 'ok'
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and a < 2:
                time.sleep(3 * (a + 1)); continue
            return None, f'HTTP {e.code}'
        except Exception as e:  # noqa: BLE001
            if a == 2:
                return None, type(e).__name__
            time.sleep(2)
    return None, 'failed'


def accept(data: bytes, doi: str, title: str, dest: Path) -> tuple[bool, str]:
    tmp = dest.with_suffix('.xml.part')
    tmp.write_bytes(data)
    try:
        root = jats_text.parse(tmp)
    except Exception as e:  # noqa: BLE001
        tmp.unlink(); return False, f'does not parse ({type(e).__name__})'
    if not jats_text.full_text_ok(root):
        tmp.unlink(); return False, 'no article body (abstract or metadata only)'
    txt = data.decode('utf-8', 'replace').lower()
    words = [w for w in re.findall(r'[a-z]{4,}', (title or '').lower())]
    hit = sum(1 for w in words if w in txt) / max(len(words), 1)
    if doi.lower() not in txt and hit < 0.6:
        tmp.unlink(); return False, 'DOI and title not found in the XML'
    tmp.rename(dest)
    (dest.parent / (dest.name + '.txt')).write_text(jats_text.convert(root))
    return True, 'accepted'


def springer_article(data: bytes) -> bytes | None:
    """The OA and TDM APIs wrap JATS <article> elements in a <response><records> envelope."""
    s = data.decode('utf-8', 'replace')
    m = re.search(r'<article[\s>].*?</article>', s, re.S)
    return m.group(0).encode() if m else None


def routes(g: dict, dest: Path) -> tuple[str | None, list[str]]:
    doi, title, tried = g['doi'], g['title'], []
    m = re.match(r'10\.5194/([a-z]+)-(\d+)-(\d+)-(\d{4})$', doi, re.I)
    if m:
        ab, vol, pg, yr = m.groups(); ab = ab.lower()
        data, why = fetch(f'https://{ab}.copernicus.org/articles/{vol}/{pg}/{yr}/{ab}-{vol}-{pg}-{yr}.xml')
        ok, why = accept(data, doi, title, dest) if data else (False, why)
        tried.append(f'copernicus: {why}')
        if ok:
            return 'copernicus', tried
    if doi.startswith(('10.1038/', '10.1007/', '10.1186/', '10.1140/')):
        for svc, var, base in (('oa', 'SPRINGER_OA_API_KEY', 'https://api.springernature.com/openaccess/jats'),
                               ('tdm', 'SPRINGER_TDM_API_KEY', 'https://api.springernature.com/xmldata/jats')):
            key = os.environ.get(var)
            if not key:
                tried.append(f'springer {svc}: skipped ({var} not set)'); continue
            data, why = fetch(f'{base}?q=doi:{urllib.parse.quote(doi)}&api_key={urllib.parse.quote(key)}')
            art = springer_article(data) if data else None
            ok, why = accept(art, doi, title, dest) if art else (False, why if not data else 'no article in the response')
            tried.append(f'springer {svc}: {why}')
            if ok:
                return f'springer {svc}', tried
    if doi.startswith(('10.1016/',)):
        key = os.environ.get('ELSEVIER_API_KEY')
        if key:
            h = {'X-ELS-APIKey': key, 'Accept': 'text/xml'}
            if os.environ.get('ELSEVIER_INSTTOKEN'):
                h['X-ELS-Insttoken'] = os.environ['ELSEVIER_INSTTOKEN']
            data, why = fetch('https://api.elsevier.com/content/article/doi/' + urllib.parse.quote(doi), h)
            ok, why = accept(data, doi, title, dest) if data else (False, why)
            tried.append(f'elsevier: {why}')
            if ok:
                return 'elsevier', tried
        else:
            tried.append('elsevier: skipped (ELSEVIER_API_KEY not set)')
    w = openalex(f"works/{g['id']}", {'select': 'id,ids'})
    pmcid = ((w or {}).get('ids') or {}).get('pmcid')
    if pmcid:
        data, why = fetch(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{sid(pmcid)}/fullTextXML')
        ok, why = accept(data, doi, title, dest) if data else (False, why)
        tried.append(f'europepmc: {why}')
        if ok:
            return 'europepmc', tried
    return None, tried


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--keys', nargs='*')
    a = ap.parse_args()
    gold = read_json(DERIVED / 'gold' / 'gold_set.json')
    if a.keys:
        gold = [g for g in gold if g['key'] in a.keys]
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for g in gold:
        dest = OUT / f"{g['key']}.xml"
        if dest.is_file():
            rows.append({'key': g['key'], 'doi': g['doi'], 'xml': True, 'route': 'already present', 'tried': []}); continue
        route, tried = routes(g, dest)
        rows.append({'key': g['key'], 'doi': g['doi'], 'xml': route is not None, 'route': route, 'tried': tried})
        print(f"{g['key']}: {route or 'none'}  {tried}", flush=True)
    write_json(DERIVED / 'gold' / 'xml_status.json', rows, ['derived/gold/gold_set.json'])
    c = Counter(r['route'] for r in rows if r['xml'])
    log('g10_fetch_xml.py', 'publisher full-text XML for the gold set', len(rows), f"{sum(r['xml'] for r in rows)} with XML: {dict(c)}")
    print(sum(r['xml'] for r in rows), 'of', len(rows), 'with XML;', dict(c))


if __name__ == '__main__':
    main()
