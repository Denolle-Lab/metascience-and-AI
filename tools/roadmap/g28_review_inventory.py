"""Inventory of open peer review in the geosciences: counts only, no full-text downloads.

Direction from the PI (October 28, 2026): papers are not written the way the science is done, they follow recipes,
and the translation from a finished research workflow to the paper is worth studying; keep going with open review in
the geosciences. Before sampling at scale we need to know which venues publish what part of the review record, for
which years, and how many papers that is. This script counts; it reads no paper text.

Parts (each writes derived/review/inventory_parts/<part>.json; `report` joins them)
copernicus  Copernicus (EGU and other) journals, listed from OpenAlex (publishers P4310313756 and P4310313776, plus
            journals that moved to Copernicus and are filed under another host: WCD, GChron, GC, MR, EJM, FR, EGQSJ,
            SP, Polarforschung).
            Counts per year
              openalex_articles     OpenAlex works, primary_location.source.id = the journal, type:article
              crossref_final        Crossref works with the journal ISSN and the Copernicus prefix 10.5194 (the
                                    years the journal was published by Copernicus)
              with_discussion       ... of which Crossref asserts relation has-preprint (the discussion preprint)
              with_review_dois      ... of which Crossref asserts has-review (comments registered as DOIs, from 2016)
            Review DOIs per year (Crossref, 2016 on): for every final paper with has-review, the subject-asserted
              review DOIs counted by type (RC referee, AC author, CC/SC community, EC editor), by year pages of
              1000 records (offset paging, so every page has a stable cached URL).
            Era check: for each journal and era year (2005, 2012, 2018, 2023) with Copernicus papers, 3 final articles
              drawn from OpenAlex (sample=6, seed=28; the first 3 with a 10.5194 DOI). For each: the Crossref record
              (licence, landing page) and the article's <stem>-discussion.html page, parsed for comment counts by type,
              inline or PDF comments, author responses after the discussion (AR), tracked-changes manuscripts (ATC),
              manuscript versions, second-round referee reports (RR) and editor decisions (ED); a HEAD request
              (no body) for the article XML <stem>.xml, keeping its declared size (old XML of a few kB is metadata,
              abstract and references; the size is reported, the file is not opened).
nature      Nature Communications (S64187185), Communications Earth & Environment (S4210221880), Nature Geoscience
            (S48977010). Earth-science papers = OpenAlex primary_topic.field 19 (Earth and Planetary Sciences).
            50 per journal for the first two (10 per year, sample seed 28; NC 2017, 2019, 2021, 2023, 2025; CEE 2021
            to 2025), 20 for Nature Geoscience (10 in 2025, 10 in 2026, all fields). The article page is checked
            for a peer review file (supplementary link labelled "peer review file", or "A peer review file is
            available"). Article pages carry the paper text, so only the evidence is kept (status, final URL,
            sha256 and byte count of the page, the matched link and sentence), not the page.
diamond     Community diamond open-access journals on OJS: Seismica, Volcanica, Tektonika, Sedimentologika,
            Geomorphica. Census of every OpenAlex type:article work: the landing page (abstract page, no paper
            text) is saved and its galleys read; a galley whose label names review reports, peer review or
            referees counts as published reviews. A site that refuses 3 requests in a row is not asked again
            (Tektonika answered HTTP 403/406 on October 28, 2026; 65 requests were made before this rule).
others      AGU Advances, Royal Society Open Science, PeerJ, JOSS (Journal of Open Source Software), Peer Community
            Journal: OpenAlex counts per year (all and field 19). JOSS, Peer Community Journal and PeerJ: 10 field-19
            pages each (sample seed 28) checked for the public review link (joss-reviews issue; Peer Community In
            recommendation DOI 10.24072/pci.<community>.<n>; PeerJ /reviews/ page), evidence only. PeerJ answered
            HTTP 403. AGU Advances and Royal Society Open Science: one landing page request each to record
            whether the publisher site answers a script (it did not on October 28, 2026: HTTP 403); their review
            policies are then reported as unverified.
report      Joins the parts into derived/review/inventory.json and derived/review/INVENTORY.md.

Caching and provenance
  OpenAlex through common.openalex() (raw/openalex/). Crossref JSON under raw/inventory/crossref/<sha1>.json.gz.
  Pages under raw/inventory/pages/<sha1>.html (Copernicus discussion pages and OJS abstract pages) or
  raw/inventory/evidence/<sha1>.json (article pages that carry the paper text). HEAD results under
  raw/inventory/head/<sha1>.json. Every network request is logged in raw/inventory/fetch_log.jsonl (URL, date, status,
  bytes, sha256, file). Pauses before each request: 1.5 s Copernicus, 1 s Crossref, 2 s any other site.
  The User-Agent names the seminar and the university; no email is sent.

Inputs   OpenAlex, Crossref REST API, Copernicus discussion pages, nature.com article pages, OJS article pages
Outputs  derived/review/inventory_parts/{copernicus,nature,diamond,others}.json
         derived/review/inventory.json, derived/review/INVENTORY.md
Run:     python tools/roadmap/g28_review_inventory.py copernicus|nature|diamond|others|report|all
         (parts touch different hosts and can run at the same time; rerunning reads the cache)
"""
from __future__ import annotations
import collections
import datetime as dt
import gzip
import hashlib
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from common import RAW, DERIVED, TODAY, openalex, paged, write_json, read_json, log, rel, sid

UA = {'User-Agent': 'Mozilla/5.0 (metascience seminar, University of Washington)'}
INV = RAW / 'inventory'
FETCH_LOG = INV / 'fetch_log.jsonl'
PARTS = DERIVED / 'review' / 'inventory_parts'
OUT = DERIVED / 'review'
CROSSREF = 'https://api.crossref.org'
ERAS = (2005, 2012, 2018, 2023)
YEARS = range(1997, 2027)
SEED = 28
PAUSE = {'copernicus.org': 1.5, 'api.crossref.org': 1.0}
_last: dict[str, float] = {}
_n = collections.Counter()
_hdr: dict = {}

# Copernicus journals: abbreviation -> (OpenAlex source id, geoscience?). Non-geoscience Copernicus titles
# (animal breeding, primate biology, mechanical sciences, sensors, ISPRS series, abstracts) are left out.
COPERNICUS = {
    'ACP': ('S162708223', True), 'AMT': ('S70769875', True), 'ANGEO': ('S63956823', True), 'AR': ('S4387290661', True),
    'ASCMO': ('S4210199883', True), 'ADGEO': ('S13330807', True), 'ASR': ('S170509739', True), 'BG': ('S13442111', True),
    'CP': ('S202457705', True), 'DWES': ('S37755942', True), 'EJM': ('S114012392', True), 'ESD': ('S163739988', True),
    'ESSD': ('S106909380', True), 'ESurf': ('S4210169354', True), 'EGQSJ': ('S4210224252', True),
    'FR': ('S137571962', True), 'GChron': ('S4210176307', True), 'GC': ('S4210203713', True),
    'GH': ('S4210184459', True), 'GI': ('S4210221359', True), 'GMD': ('S60406085', True), 'HESS': ('S93121129', True),
    'HGSS': ('S64277006', True), 'JM': ('S90051289', True), 'MR': ('S4210199904', False), 'NHESS': ('S70708404', True),
    'NPG': ('S190716948', True), 'OS': ('S152701455', True), 'PIAHS': ('S4210170531', True), 'POLF': ('S4210203660', True),
    'SD': ('S174624501', True), 'SE': ('S203396075', True), 'SOIL': ('S4210190384', True), 'SP': ('S4387292935', True),
    'TC': ('S169796457', True), 'WCD': ('S4210178013', True), 'WES': ('S4210189655', False),
}
NATURE = {'NC': ('S64187185', 'Nature Communications', (2017, 2019, 2021, 2023, 2025), 10, True),
          'CEE': ('S4210221880', 'Communications Earth & Environment', (2021, 2022, 2023, 2024, 2025), 10, True),
          'NGEO': ('S48977010', 'Nature Geoscience', (2025, 2026), 10, False)}
DIAMOND = {'Seismica': 'S4387284412', 'Volcanica': 'S4210167754', 'Tektonika': 'S4387287549',
           'Sedimentologika': 'S4387287832', 'Geomorphica': 'S4404675134'}
OTHERS = {'AGU Advances': 'S4210240585', 'Royal Society Open Science': 'S2737558550', 'PeerJ': 'S1983995261',
          'JOSS': 'S4210214273', 'Peer Community Journal': 'S4387278563'}
FIELD_EARTH = 'fields/19'
REVIEW_LINK = {'JOSS': r'joss-reviews/issues/\d+', 'Peer Community Journal': r'10\.24072/pci\.[a-z]+\.\d+',
               'PeerJ': r'/articles/\d+/reviews/?'}


# ---------------------------------------------------------------------------------------------- network and cache
def _key(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()


def _pause(url: str) -> None:
    host = urllib.parse.urlparse(url).netloc
    p = next((v for k, v in PAUSE.items() if host.endswith(k)), 2.0)
    wait = _last.get(host, 0) + p - time.time()
    if wait > 0:
        time.sleep(wait)
    _last[host] = time.time()


def _logfetch(rec: dict) -> None:
    INV.mkdir(parents=True, exist_ok=True)
    with FETCH_LOG.open('a') as f:
        f.write(json.dumps(rec) + '\n')


def _request(url: str, method: str = 'GET') -> tuple[int, str, bytes]:
    _pause(url)
    _n['net'] += 1
    req = urllib.request.Request(url, headers={**UA, 'Accept': 'text/html,application/json'}, method=method)
    for a in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                if method == 'HEAD':
                    _hdr['length'] = int(r.headers.get('Content-Length') or 0)
                    _hdr['type'] = r.headers.get('Content-Type')
                return r.status, r.geturl(), (r.read() if method == 'GET' else b'')
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and a < 3:
                time.sleep(int(e.headers.get('Retry-After') or 0) or 5 * 2 ** a)
                continue
            return e.code, url, b''
        except Exception as e:  # noqa: BLE001
            if a == 3:
                return -1, f'{type(e).__name__}: {e}', b''
            time.sleep(5 * 2 ** a)
    return -1, url, b''


def crossref(path: str, params: dict | None = None) -> dict:
    """Crossref REST GET, cached gzip under raw/inventory/crossref/. Returns {} on failure."""
    url = f'{CROSSREF}/{path.lstrip("/")}' + ('?' + urllib.parse.urlencode(params, safe=':,*') if params else '')
    f = INV / 'crossref' / (_key(url) + '.json.gz')
    if f.is_file():
        _n['cache'] += 1
        return json.loads(gzip.decompress(f.read_bytes()))['response']
    status, final, body = _request(url)
    resp = json.loads(body).get('message', {}) if status == 200 else {}
    f.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps({'url': url, 'retrieved': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
                       'status': status, 'response': resp}).encode()
    f.write_bytes(gzip.compress(blob))
    _logfetch({'url': url, 'date': TODAY, 'status': status, 'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest(),
               'file': rel(f)})
    return resp


def page(url: str, keep: bool, extract=None) -> dict:
    """GET a web page once. keep=True saves the page verbatim (review records, abstract pages); keep=False saves only
    the evidence returned by extract(page_text) with the page's hash (article pages that carry the paper text)."""
    k = _key(url)
    raw_f, ev_f = INV / 'pages' / (k + '.html'), INV / 'evidence' / (k + '.json')
    meta_f = INV / 'pages' / (k + '.meta.json')
    if keep and meta_f.is_file():
        _n['cache'] += 1
        meta = json.loads(meta_f.read_text())
        text = raw_f.read_text(errors='replace') if raw_f.is_file() else ''
        return {**meta, 'text': text, **({'evidence': extract(text)} if extract and text else {})}
    if not keep and ev_f.is_file():
        _n['cache'] += 1
        return json.loads(ev_f.read_text())
    status, final, body = _request(url)
    text = body.decode('utf-8', 'replace')
    meta = {'url': url, 'final_url': final, 'status': status, 'retrieved': TODAY, 'bytes': len(body),
            'sha256': hashlib.sha256(body).hexdigest()}
    if keep:
        raw_f.parent.mkdir(parents=True, exist_ok=True)
        if body:
            raw_f.write_text(text)
        meta_f.write_text(json.dumps(meta))
        _logfetch({**meta, 'file': rel(raw_f) if body else None})
        return {**meta, 'text': text, **({'evidence': extract(text)} if extract and text else {})}
    ev = {**meta, 'evidence': extract(text) if (extract and text) else None}
    ev_f.parent.mkdir(parents=True, exist_ok=True)
    ev_f.write_text(json.dumps(ev))
    _logfetch({**meta, 'file': rel(ev_f), 'kept': 'evidence only'})
    return ev


def head(url: str) -> dict:
    """HEAD request (no body): status, Content-Length and Content-Type. An old Copernicus XML of a few kB carries
    metadata only (no body text), so the length separates full-text XML from metadata XML without downloading it."""
    f = INV / 'head' / (_key(url) + '.json')
    if f.is_file():
        rec = json.loads(f.read_text())
        if 'length' in rec:
            _n['cache'] += 1
            return rec
    _hdr.clear()
    status, final, _ = _request(url, 'HEAD')
    rec = {'url': url, 'final_url': final, 'status': status, 'retrieved': TODAY,
           'length': _hdr.get('length'), 'type': _hdr.get('type')}
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(rec))
    _logfetch({'url': url, 'date': TODAY, 'status': status, 'method': 'HEAD', 'bytes_declared': rec['length'], 'file': rel(f)})
    return rec


# ---------------------------------------------------------------------------------------------------- OpenAlex
def by_year(filt: str) -> dict[int, int]:
    r = openalex('works', {'filter': filt, 'group_by': 'publication_year'})
    return {int(g['key']): g['count'] for g in r.get('group_by', []) if str(g['key']).isdigit()}


def sample(filt: str, n: int) -> list[dict]:
    r = openalex('works', {'filter': filt, 'sample': n, 'seed': SEED, 'per-page': n,
                           'select': 'id,doi,publication_year,primary_topic,primary_location'})
    return r.get('results', [])


# ---------------------------------------------------------------------------------------------------- Copernicus
COMMENT = re.compile(r'<strong>(RC|AC|SC|CC|EC)\d*</strong>\s*(?:[A-Z]{0,2}\d+\s*)?:(?!\s*(?:Author|Referee|Short|Community|Editor) comment)')


def parse_discussion(p: str) -> dict:
    kinds = collections.Counter(m.group(1) for m in COMMENT.finditer(p))
    if 'SC' in kinds:
        kinds['CC'] += kinds.pop('SC')
    files = set(re.findall(r'href="(https://[^"]+\.pdf)"', p))
    return {
        'comments': dict(kinds),
        'inline_comments': 'comment-body-' in p,
        'AR': len({f for f in files if re.search(r'-AR\d*\.pdf$', f)}),
        'ATC': len({f for f in files if re.search(r'-ATC\d*\.pdf$', f)}),
        'manuscript_versions': len({f for f in files if re.search(r'manuscript-version\d+\.pdf$', f)}),
        'RR': len(re.findall(r'<strong>RR\d*</strong>\s*by', p)),
        'ED': len(re.findall(r'<strong>ED:</strong>', p)),
        'completion_section': "<strong>AR</strong>: Author's response" in p,
        'comment_supplements': len({f for f in files if re.search(r'-(?:RC|AC|CC|SC|EC)\d*-supplement\.pdf$', f)}),
    }


def crossref_issn(src: dict) -> str | None:
    best, n = None, -1
    for issn in src.get('issn') or []:
        m = crossref('works', {'filter': f'issn:{issn},prefix:10.5194', 'rows': 0})
        if m.get('total-results', 0) > n:
            best, n = issn, m.get('total-results', 0)
    return best if n > 0 else None


def facet_years(filt: str) -> dict[int, int]:
    m = crossref('works', {'filter': filt, 'facet': 'published:*', 'rows': 0})
    return {int(k): v for k, v in m.get('facets', {}).get('published', {}).get('values', {}).items()}


def review_dois(issn: str, year: int) -> dict:
    out = {'papers': 0, 'RC': 0, 'AC': 0, 'CC': 0, 'EC': 0, 'other': 0}
    offset = 0
    while True:
        m = crossref('works', {'filter': f'issn:{issn},prefix:10.5194,relation.type:has-review,'
                                         f'from-pub-date:{year}-01-01,until-pub-date:{year}-12-31',
                               'select': 'DOI,relation', 'rows': 1000, 'offset': offset})
        items = m.get('items', [])
        for it in items:
            out['papers'] += 1
            ids = {x['id'] for x in it.get('relation', {}).get('has-review', []) if x.get('asserted-by') == 'subject'}
            for d in ids:
                t = re.search(r'-(RC|AC|CC|SC|EC)\d+$', d, flags=re.I)
                k = t.group(1).upper() if t else 'other'
                out['CC' if k == 'SC' else k] += 1
        offset += 1000
        if len(items) < 1000 or offset >= m.get('total-results', 0):
            return out


def era_check(abbr: str, source: str, year: int) -> list[dict]:
    rows = []
    for w in sample(f'primary_location.source.id:{source},publication_year:{year},type:article', 6):
        doi = (w.get('doi') or '').replace('https://doi.org/', '')
        if not doi.lower().startswith('10.5194/'):
            continue
        cr = crossref('works/' + urllib.parse.quote(doi, safe='/'))
        rec = {'doi': doi, 'year': year}
        if not cr:
            rec['error'] = 'no Crossref record'
            rows.append(rec)
            continue
        rel_ = cr.get('relation', {})
        rec['crossref_preprint'] = [x['id'] for x in rel_.get('has-preprint', []) if x.get('asserted-by') == 'subject'][:1]
        rec['crossref_review_dois'] = len({x['id'] for x in rel_.get('has-review', []) if x.get('asserted-by') == 'subject'})
        rec['licence'] = sorted({l['URL'] for l in cr.get('license', []) if l.get('content-version') in ('vor', 'unspecified')})
        land = cr.get('resource', {}).get('primary', {}).get('URL', '').rstrip('/') + '/'
        stem = doi.split('/', 1)[1]
        d = page(land + stem + '-discussion.html', keep=True)
        rec['discussion_status'] = d['status']
        if d['status'] == 200 and ('Interactive discussion' in d['text'] or COMMENT.search(d['text'])):
            rec.update(parse_discussion(d['text']))
            rec['has_discussion_page'] = True
        else:
            rec['has_discussion_page'] = False
        h = head(land + stem + '.xml')
        rec['xml_status'], rec['xml_bytes'] = h['status'], h.get('length')
        rows.append(rec)
        if len(rows) == 3:
            break
    return rows


def run_copernicus() -> dict:
    out = {}
    for abbr, (source, geo) in COPERNICUS.items():
        src = openalex('sources/' + source)
        issn = crossref_issn(src)
        j = {'name': src.get('display_name'), 'openalex_source': source, 'geoscience': geo, 'issn_crossref': issn,
             'openalex_articles': by_year(f'primary_location.source.id:{source},type:article')}
        if issn:
            base = f'issn:{issn},prefix:10.5194'
            j['crossref_final'] = facet_years(base)
            j['with_discussion'] = facet_years(base + ',relation.type:has-preprint')
            j['with_review_dois'] = facet_years(base + ',relation.type:has-review')
            j['review_dois'] = {y: review_dois(issn, y) for y in sorted(j['with_review_dois']) if y >= 2016}
            j['era_check'] = {y: era_check(abbr, source, y) for y in ERAS if j['crossref_final'].get(y)}
        disc = [y for y, n in sorted(j.get('crossref_final', {}).items())
                if n >= 5 and j['with_discussion'].get(y, 0) / n >= 0.5]
        j['discussion_years'] = [disc[0], disc[-1]] if disc else None
        out[abbr] = j
        print(abbr, issn, j['discussion_years'], sum(j.get('crossref_final', {}).values()), 'papers;',
              {y: len(v) for y, v in j.get('era_check', {}).items()}, dict(_n), flush=True)
    return out


# ---------------------------------------------------------------------------------------------------- Nature
def nature_evidence(p: str) -> dict:
    labels = re.findall(r'data-track-label="([^"]*peer review file[^"]*)"[^>]*href="([^"]+)"', p, flags=re.I)
    sent = re.search(r'<h3[^>]*>Peer review information</h3>\s*<p>(.*?)</p>', p, flags=re.S)
    s = html.unescape(re.sub(r'<[^>]+>', '', sent.group(1))).strip() if sent else None
    return {'prf_links': [{'label': a, 'href': b} for a, b in labels],
            'prf_sentence': bool(re.search(r'(?i)peer review file is available', p)),
            'peer_review_information': s,
            'reviewer_named': bool(s and re.search(r'thanks\s+(?!the anonymous)[A-Z]', s)),
            'has_peer_review_file': bool(labels) or bool(re.search(r'(?i)peer review file is available', p))}


def run_nature() -> dict:
    out = {}
    for abbr, (source, name, years, n, earth) in NATURE.items():
        base = f'primary_location.source.id:{source},type:article'
        j = {'name': name, 'openalex_source': source, 'articles': by_year(base),
             'earth_articles': by_year(base + f',primary_topic.field.id:{FIELD_EARTH}'), 'sample': []}
        for y in years:
            for w in sample(base + f',publication_year:{y}' + (f',primary_topic.field.id:{FIELD_EARTH}' if earth else ''), n):
                doi = (w.get('doi') or '').replace('https://doi.org/', '')
                if not doi.startswith('10.1038/'):
                    j['sample'].append({'doi': None, 'openalex': w['id'], 'year': y, 'status': None, 'skipped': 'no DOI in OpenAlex'})
                    continue
                ev = page('https://www.nature.com/articles/' + doi.split('/', 1)[1], keep=False, extract=nature_evidence)
                e = ev.get('evidence') or {}
                j['sample'].append({'doi': doi, 'year': y, 'status': ev['status'],
                                    'topic': (w.get('primary_topic') or {}).get('display_name'),
                                    'licence': (w.get('primary_location') or {}).get('license'),
                                    'has_peer_review_file': e.get('has_peer_review_file'),
                                    'reviewer_named': e.get('reviewer_named')})
        out[abbr] = j
        print(abbr, len(j['sample']), sum(bool(s.get('has_peer_review_file')) for s in j['sample']), dict(_n), flush=True)
    return out


# ---------------------------------------------------------------------------------------------------- OJS diamond
REVIEW_LABEL = re.compile(r'(?i)review report|peer[- ]?review|referee|reviewer|review history|decision letter')


def ojs_evidence(p: str) -> dict:
    g = re.findall(r'<a[^>]*class="(?:obj_galley_link|galley-link)[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', p, flags=re.S)
    g += [(h, t) for t, h in re.findall(r'<a[^>]*href="([^"]+)"[^>]*class="(?:obj_galley_link|galley-link)[^"]*"[^>]*>(.*?)</a>', p, flags=re.S)]
    labels = [' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', t)).split()) for _, t in g]
    return {'galleys': labels, 'review_galleys': [l for l in labels if REVIEW_LABEL.search(l)]}


def run_diamond() -> dict:
    out = {}
    for name, source in DIAMOND.items():
        works = paged('works', {'filter': f'primary_location.source.id:{source},type:article',
                                'select': 'id,doi,publication_year,primary_location'})
        rows = []
        for w in sorted(works, key=lambda w: w['id']):
            url = w.get('doi') or (w.get('primary_location') or {}).get('landing_page_url')
            if not url:
                continue
            pg = page(url, keep=True, extract=ojs_evidence)
            e = pg.get('evidence') or {}
            rows.append({'doi': (w.get('doi') or '').replace('https://doi.org/', ''), 'year': w.get('publication_year'),
                         'status': pg['status'], 'licence': (w.get('primary_location') or {}).get('license'),
                         'galleys': e.get('galleys'), 'review_galleys': e.get('review_galleys')})
            if len(rows) >= 3 and all(r['status'] != 200 for r in rows[-3:]):
                break  # the site refuses scripts (Tektonika, October 28 2026: HTTP 403/406); stop after 3 refusals in a row
        out[name] = {'openalex_source': source, 'articles': by_year(f'primary_location.source.id:{source},type:article'),
                     'checked': rows}
        print(name, len(rows), sum(bool(r['review_galleys']) for r in rows), dict(_n), flush=True)
    return out


# ---------------------------------------------------------------------------------------------------- others
def run_others() -> dict:
    out = {}
    probes = {'AGU Advances': 'https://doi.org/10.1029/2023av001134', 'Royal Society Open Science': 'https://doi.org/10.1098/rsos.230859'}
    for name, source in OTHERS.items():
        base = f'primary_location.source.id:{source},type:article'
        j = {'openalex_source': source, 'articles': by_year(base),
             'earth_articles': by_year(base + f',primary_topic.field.id:{FIELD_EARTH}')}
        if name in probes:
            ev = page(probes[name], keep=False, extract=lambda p: {'peer_review_mentions': len(re.findall(r'(?i)peer review', p))})
            j['site_probe'] = {'url': probes[name], 'status': ev['status'], 'final_url': ev['final_url']}
        if name in REVIEW_LINK:
            pat = REVIEW_LINK[name]
            j['sample'] = []
            for w in sample(base + f',primary_topic.field.id:{FIELD_EARTH}', 10):
                ev = page(w['doi'], keep=False, extract=lambda p, pat=pat: {'review_links': sorted(set(re.findall(pat, p)))[:5]})
                links = (ev.get('evidence') or {}).get('review_links') or []
                j['sample'].append({'doi': w['doi'].replace('https://doi.org/', ''), 'year': w.get('publication_year'),
                                    'status': ev['status'], 'review_links': links,
                                    'licence': (w.get('primary_location') or {}).get('license')})
        out[name] = j
        print(name, sum(j['earth_articles'].values()), dict(_n), flush=True)
    return out


# ---------------------------------------------------------------------------------------------------- report
def share(a, b):
    return round(a / b, 3) if b else None


def report() -> None:
    parts = {p: read_json(PARTS / f'{p}.json') for p in ('copernicus', 'nature', 'diamond', 'others') if (PARTS / f'{p}.json').is_file()}
    md = ['# Open peer review in the geosciences: inventory (counts only)', '',
          f'Built by `tools/roadmap/g28_review_inventory.py report` on {TODAY} from the parts in derived/review/inventory_parts/. '
          'No paper text was downloaded. Sources of every number are named in the column heads; see the script docstring.', '']
    summary = {}
    if 'copernicus' in parts:
        cop = parts['copernicus']
        md += ['## 1. Copernicus journals', '',
               'final = Crossref works with the journal ISSN and prefix 10.5194; disc = of which Crossref asserts a discussion '
               'preprint (has-preprint); rev = of which comments are registered as DOIs (has-review, 2016 on). '
               'OpenAlex = OpenAlex type:article works of the source, all years. Discussion years = first and last year '
               'with at least 5 papers and at least half with a discussion preprint.', '',
               '| Journal | Geo | Discussion years | Final 2005-2025 | With discussion | OpenAlex articles | Final 2025 | RC DOIs 2016-2025 | AC DOIs 2016-2025 |',
               '|:--|:--|:--|--:|--:|--:|--:|--:|--:|']
        for abbr, j in cop.items():
            f = {int(k): v for k, v in j.get('crossref_final', {}).items()}
            dsc = {int(k): v for k, v in j.get('with_discussion', {}).items()}
            rd = {int(k): v for k, v in j.get('review_dois', {}).items()}
            oa = {int(k): v for k, v in j.get('openalex_articles', {}).items()}
            r25 = range(2005, 2026)
            md.append(f"| {abbr} | {'y' if j['geoscience'] else 'n'} | {j['discussion_years'] or 'none'} | "
                      f"{sum(f.get(y, 0) for y in r25)} | {sum(dsc.get(y, 0) for y in r25)} | {sum(oa.values())} | {f.get(2025, 0)} | "
                      f"{sum(v['RC'] for y, v in rd.items() if y <= 2025)} | {sum(v['AC'] for y, v in rd.items() if y <= 2025)} |")
        md += ['', '### Era check (3 final papers per journal and era year, discussion page parsed)', '',
               '| Era | Papers checked | With discussion page | Inline comments | Author comments (AC) posted | AR posted | Tracked changes (ATC) | Manuscript versions | Second-round reports (RR) | Editor decisions (ED) | XML found | XML size, median kB (min-max) | Licences |',
               '|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:--|']
        era = {}
        for y in ERAS:
            rows = [r for j in cop.values() if j['geoscience'] for r in j.get('era_check', {}).get(str(y), j.get('era_check', {}).get(y, []))]
            d = [r for r in rows if r.get('has_discussion_page')]
            e = {'checked': len(rows), 'discussion_page': len(d), 'inline': sum(r['inline_comments'] for r in d),
                 'AC': sum(r['comments'].get('AC', 0) > 0 for r in d), 'AR': sum(r['AR'] > 0 for r in d),
                 'ATC': sum(r['ATC'] > 0 for r in d), 'versions': sum(r['manuscript_versions'] > 0 for r in d),
                 'RR': sum(r['RR'] > 0 for r in d), 'ED': sum(r['ED'] > 0 for r in d),
                 'xml': sum(r.get('xml_status') == 200 for r in rows),
                 'xml_kb': sorted(round((r.get('xml_bytes') or 0) / 1000) for r in rows if r.get('xml_status') == 200),
                 'licences': dict(collections.Counter(l.split('licenses/')[-1].strip('/') for r in rows for l in r.get('licence', [])))}
            era[y] = e
            md.append(f"| {y} | {e['checked']} | {e['discussion_page']} | {e['inline']} | {e['AC']} | {e['AR']} | {e['ATC']} | {e['versions']} | {e['RR']} | {e['ED']} | {e['xml']} | {e['xml_kb'][len(e['xml_kb']) // 2] if e['xml_kb'] else ''} ({e['xml_kb'][0] if e['xml_kb'] else ''}-{e['xml_kb'][-1] if e['xml_kb'] else ''}) | {'; '.join(f'{k} ({v})' for k, v in sorted(e['licences'].items()))} |")
        md += ['', 'Per-journal era rows (AR / ATC / manuscript versions present among the papers with a discussion page):', '',
               '| Journal | ' + ' | '.join(str(y) for y in ERAS) + ' |', '|:--|' + '--|' * len(ERAS)]
        for abbr, j in cop.items():
            cells = []
            for y in ERAS:
                rows = j.get('era_check', {}).get(str(y), [])
                d = [r for r in rows if r.get('has_discussion_page')]
                cells.append(f"{len(d)}/{len(rows)} disc; AR {sum(r['AR'] > 0 for r in d)}, ATC {sum(r['ATC'] > 0 for r in d)}, MV {sum(r['manuscript_versions'] > 0 for r in d)}" if rows else '-')
            md.append(f'| {abbr} | ' + ' | '.join(cells) + ' |')
        yearly = collections.defaultdict(lambda: collections.Counter())
        for j in cop.values():
            if not j['geoscience']:
                continue
            for k in ('crossref_final', 'with_discussion', 'with_review_dois'):
                for y, v in j.get(k, {}).items():
                    yearly[int(y)][k] += v
            for y, v in j.get('review_dois', {}).items():
                for t in ('RC', 'AC', 'CC', 'EC'):
                    yearly[int(y)][t] += v[t]
        md += ['', '### Copernicus geoscience journals per year (all journals with Geo = y)', '',
               '| Year | Final papers | With discussion | With review DOIs | RC DOIs | AC DOIs | CC DOIs | EC DOIs |', '|:--|--:|--:|--:|--:|--:|--:|--:|']
        for y in range(2005, 2026):
            c = yearly[y]
            md.append(f"| {y} | {c['crossref_final']} | {c['with_discussion']} | {c['with_review_dois']} | {c['RC']} | {c['AC']} | {c['CC']} | {c['EC']} |")
        summary['copernicus'] = {'era': era, 'yearly': {y: dict(yearly[y]) for y in range(2005, 2026)}}
    if 'nature' in parts:
        md += ['', '## 2. Nature Portfolio journals: peer review file on the article page', '',
               'Earth = OpenAlex primary_topic field 19 (Earth and Planetary Sciences). Sample drawn with OpenAlex sample, seed 28.', '',
               '| Journal | Year | Earth articles (OpenAlex) | Checked | With peer review file |', '|:--|:--|--:|--:|--:|']
        nat = {}
        for abbr, j in parts['nature'].items():
            by = collections.defaultdict(list)
            for s in j['sample']:
                by[s['year']].append(s)
            ea = {int(k): v for k, v in j['earth_articles'].items()}
            for y, ss in sorted(by.items()):
                ok = [s for s in ss if s['status'] == 200]
                md.append(f"| {j['name']} | {y} | {ea.get(y, 0)} | {len(ok)} | {sum(bool(s['has_peer_review_file']) for s in ok)} |")
            ok = [s for s in j['sample'] if s['status'] == 200]
            nat[abbr] = {'checked': len(ok), 'with_prf': sum(bool(s['has_peer_review_file']) for s in ok),
                         'earth_articles_2016_2025': sum(v for y, v in ea.items() if 2016 <= y <= 2025)}
        summary['nature'] = nat
    if 'diamond' in parts:
        md += ['', '## 3. Community diamond open-access journals (census of OpenAlex articles)', '',
               '| Journal | Years | Articles (OpenAlex) | Pages read | With review galley | Galley labels seen |', '|:--|:--|--:|--:|--:|:--|']
        dia = {}
        for name, j in parts['diamond'].items():
            rows = j['checked']
            ok = [r for r in rows if r['status'] == 200]
            yrs = sorted(int(k) for k in j['articles'])
            labels = collections.Counter(l for r in ok for l in (r['galleys'] or []))
            dia[name] = {'articles': sum(j['articles'].values()), 'read': len(ok), 'with_reviews': sum(bool(r['review_galleys']) for r in ok),
                         'status_if_unread': sorted({r['status'] for r in rows if r['status'] != 200})}
            md.append(f"| {name} | {yrs[0] if yrs else ''}-{yrs[-1] if yrs else ''} | {dia[name]['articles']} | {len(ok)} | {dia[name]['with_reviews']} | "
                      + '; '.join(f'{k} ({v})' for k, v in labels.most_common(6)) + (f" (HTTP {dia[name]['status_if_unread']})" if not ok else '') + ' |')
        md += ['', 'Per year, articles read / with a review galley:', '', '| Journal | ' + ' | '.join(str(y) for y in range(2018, 2027)) + ' |',
               '|:--|' + '--:|' * 9]
        for name, j in parts['diamond'].items():
            ok = [r for r in j['checked'] if r['status'] == 200]
            md.append(f'| {name} | ' + ' | '.join(f"{sum(r['year'] == y for r in ok)} / {sum(r['year'] == y and bool(r['review_galleys']) for r in ok)}"
                                                   for y in range(2018, 2027)) + ' |')
        summary['diamond'] = dia
    if 'others' in parts:
        md += ['', '## 4. Other venues (OpenAlex counts; review availability as checked)', '',
               '| Venue | Articles 2016-2025 | Earth articles 2016-2025 | Check |', '|:--|--:|--:|:--|']
        oth = {}
        for name, j in parts['others'].items():
            a = sum(v for y, v in j['articles'].items() if 2016 <= int(y) <= 2025)
            e = sum(v for y, v in j['earth_articles'].items() if 2016 <= int(y) <= 2025)
            chk = ''
            if 'site_probe' in j:
                chk = f"publisher site answered HTTP {j['site_probe']['status']} to the script; review availability not verified"
            if 'sample' in j:
                ok = [s for s in j['sample'] if s['status'] == 200]
                chk = (f"{sum(bool(s['review_links']) for s in ok)} of {len(ok)} Earth-field pages link a public review" if ok else
                       f"{len(j['sample'])} Earth-field pages requested, publisher site answered HTTP "
                       f"{sorted({s['status'] for s in j['sample']})}; review availability not verified")
            oth[name] = {'articles_2016_2025': a, 'earth_2016_2025': e, 'check': chk}
            md.append(f'| {name} | {a} | {e} | {chk} |')
        summary['others'] = oth
    write_json(OUT / 'inventory.json', {'summary': summary, 'parts': parts},
               [rel(PARTS / f'{p}.json') for p in parts], {'eras': ERAS, 'seed': SEED})
    (OUT / 'INVENTORY.md').write_text('\n'.join(md) + '\n')
    print('wrote', rel(OUT / 'inventory.json'), rel(OUT / 'INVENTORY.md'))


def main() -> None:
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    runs = {'copernicus': run_copernicus, 'nature': run_nature, 'diamond': run_diamond, 'others': run_others}
    for part in (runs if what == 'all' else [what] if what in runs else []):
        data = runs[part]()
        write_json(PARTS / f'{part}.json', data, ['OpenAlex', 'Crossref REST API', 'publisher pages (see raw/inventory/fetch_log.jsonl)'],
                   {'eras': ERAS, 'seed': SEED, 'pauses_s': {**PAUSE, 'other': 2.0}})
        log(f'g28_review_inventory.py {part}', f'open review inventory: {part}', len(data),
            f"{_n['net']} web requests, {_n['cache']} web cache hits")
    if what in ('report', 'all'):
        report()
    elif what not in runs:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
