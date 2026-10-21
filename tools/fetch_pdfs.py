#!/usr/bin/env python3
"""Fetch full texts for a list of DOIs by legal routes, and keep the list of what is still missing.

Routes, tried in order for each DOI (each attempt is recorded):
  1. library   a PDF already in a local folder (indexed by the DOI printed in its first pages)
  2. openalex  every open-access location OpenAlex lists (anonymous; no email sent)
  3. s2        Semantic Scholar's openAccessPdf link (anonymous, or S2_API_KEY for a dedicated rate limit)
  4. unpaywall only if UNPAYWALL_EMAIL is set (Unpaywall requires an email; none is sent otherwise)
  5. europepmc the PMC rendering when OpenAlex gives a PMCID
  6. tdm       publisher text-and-data-mining APIs, only with institutional credentials in the
               environment and only for content the institution subscribes to:
                 Wiley (incl. AGU journals)  WILEY_TDM_TOKEN
                 Elsevier                    ELSEVIER_API_KEY, optional ELSEVIER_INSTTOKEN
               Any other Crossref "text-mining" link is tried without credentials.
A file counts only if it starts with %PDF, is larger than 20 KB, and (when pdftotext is
available) its first two pages contain the DOI or at least 60% of the title's words. Files that
fail the check are kept as <key>.check.pdf and the DOI stays in the queue.

State lives in private/download-queue.json; private/download-list.md is rewritten on every run
with APA citations, DOI links, and a UW Libraries proxy link for everything still missing.

Usage:
  python3 tools/fetch_pdfs.py add KEY [KEY ...]        queue references from references.bib by key
  python3 tools/fetch_pdfs.py add-doi FILE             queue DOIs from a file (one 'doi' or 'key doi' per line)
  python3 tools/fetch_pdfs.py add-manifest FILE.jsonl  queue a corpus manifest from tools/corpus.py (group = corpus name and stratum)
  python3 tools/fetch_pdfs.py run [--out DIR] [--library DIR ...] [--dry-run]
  python3 tools/fetch_pdfs.py list                     rewrite private/download-list.md only
Nothing fetched here is redistributed; PDFs go to a gitignored folder.
"""
from __future__ import annotations
import argparse, json, os, re, shutil, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import apa  # noqa: E402

QUEUE = ROOT / 'private' / 'download-queue.json'
LIST = ROOT / 'private' / 'download-list.md'
INDEX = ROOT / 'private' / 'library-index.json'
DEFAULT_OUT = ROOT / 'private' / 'pdfs'
DEFAULT_LIBRARY = [Path.home() / 'Dropbox' / 'ARTICLES' / 'METASCIENCE', ROOT / 'private' / 'pdfs']
UA = 'metascience-seminar-fetch/1.0 (research group reading list)'
PROXY = 'https://offcampus.lib.washington.edu/login?url=https://doi.org/'
TIMEOUT = 60
_last: dict[str, float] = {}
META: dict[str, dict] = {}
BLOCKED: dict[str, list] = {}  # open copies that refused scripted download (HTTP 403)


def polite(url: str) -> None:
    host = urllib.parse.urlparse(url).netloc
    wait = 1.0 - (time.time() - _last.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _last[host] = time.time()


def get(url: str, headers: dict | None = None, raw: bool = False):
    polite(url)
    req = urllib.request.Request(url, headers={'User-Agent': UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = r.read()
            return (data, r.headers.get('Content-Type', '')) if raw else json.loads(data)
    except urllib.error.HTTPError as e:
        return (None, f'HTTP {e.code}') if raw else None
    except Exception as e:  # noqa: BLE001
        return (None, type(e).__name__) if raw else None


def pdf_text(path: Path) -> str:
    if not shutil.which('pdftotext'):
        return ''
    try:
        return subprocess.run(['pdftotext', '-l', '2', '-q', str(path), '-'], capture_output=True, text=True, timeout=60).stdout
    except Exception:  # noqa: BLE001
        return ''


def norm(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()


def matches(path: Path, doi: str, title: str) -> str:
    text = pdf_text(path)
    if not text:
        return 'unchecked (no pdftotext)'
    if doi.lower() in text.lower().replace('\n', ''):
        return 'doi found'
    words = [w for w in norm(title).split() if len(w) > 3]
    if words:
        t = norm(text)
        hit = sum(1 for w in words if w in t) / len(words)
        if hit >= 0.6:
            return f'title {hit:.0%}'
        return f'MISMATCH (title {hit:.0%})'
    return 'unchecked (no title)'


def save(data: bytes, dest: Path, doi: str, title: str) -> tuple[bool, str]:
    if not data or not data.startswith(b'%PDF') or len(data) < 20_000:
        return False, 'not a PDF or too small'
    dest.write_bytes(data)
    check = matches(dest, doi, title)
    if check.startswith('MISMATCH'):
        bad = dest.with_suffix('.check.pdf')
        dest.replace(bad)
        return False, f'{check}; kept as {bad.name}'
    return True, check


def index_library(dirs: list[Path]) -> dict:
    idx = json.loads(INDEX.read_text()) if INDEX.exists() else {}
    for d in dirs:
        if not d.is_dir():
            continue
        for p in d.rglob('*.pdf'):
            key = str(p)
            st = p.stat()
            if key in idx and idx[key].get('mtime') == st.st_mtime:
                continue
            dois = sorted(set(m.rstrip('.,;)').lower() for m in re.findall(r'10\.\d{4,9}/[^\s"<>]+', pdf_text(p))))
            idx[key] = {'mtime': st.st_mtime, 'dois': dois}
    INDEX.write_text(json.dumps(idx, indent=1))
    return idx


def load_queue() -> dict:
    return json.loads(QUEUE.read_text()) if QUEUE.exists() else {}


def store_queue(q: dict) -> None:
    QUEUE.write_text(json.dumps(q, indent=1, ensure_ascii=False))


def refs() -> dict:
    return json.loads((ROOT / 'curriculum.json').read_text())['references']


def routes_for(doi: str, title: str, key: str, out: Path) -> tuple[str | None, list[str]]:
    tried = []
    dest = out / f'{key}.pdf'
    w = get('https://api.openalex.org/works/https://doi.org/' + urllib.parse.quote(doi, safe=''))
    title = title or (w or {}).get('title') or ''
    META[key] = {'title': (w or {}).get('title'), 'year': (w or {}).get('publication_year'),
                 'venue': (((w or {}).get('primary_location') or {}).get('source') or {}).get('display_name')}
    locs = (w or {}).get('locations') or []
    for loc in locs:
        url = loc.get('pdf_url')
        if not url:
            continue
        data, info = get(url, {'Accept': 'application/pdf,*/*'}, raw=True)
        ok, why = save(data, dest, doi, title) if data else (False, info)
        tried.append(f'openalex {urllib.parse.urlparse(url).netloc}: {why}')
        if 'HTTP 403' in str(why):
            BLOCKED.setdefault(key, []).append(url)
        if ok:
            return f'openalex ({urllib.parse.urlparse(url).netloc})', tried
    s2h = {'x-api-key': os.environ['S2_API_KEY']} if os.environ.get('S2_API_KEY') else {}
    for a in range(3):
        s2 = get('https://api.semanticscholar.org/graph/v1/paper/DOI:' + urllib.parse.quote(doi, safe='/') + '?fields=openAccessPdf', s2h)
        if s2 is not None:
            break
        time.sleep(3 * (a + 1))
    url = ((s2 or {}).get('openAccessPdf') or {}).get('url')
    if url and not url.startswith('https://doi.org/'):
        data, info = get(url, {'Accept': 'application/pdf,*/*'}, raw=True)
        ok, why = save(data, dest, doi, title) if data else (False, info)
        tried.append(f's2 {urllib.parse.urlparse(url).netloc}: {why}')
        if 'HTTP 403' in str(why):
            BLOCKED.setdefault(key, []).append(url)
        if ok:
            return f's2 ({urllib.parse.urlparse(url).netloc})', tried
    else:
        tried.append('s2: no direct PDF link' if s2 is not None else 's2: no response')
    email = os.environ.get('UNPAYWALL_EMAIL')
    if email:
        u = get(f'https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={urllib.parse.quote(email)}')
        for loc in (u or {}).get('oa_locations') or []:
            url = loc.get('url_for_pdf')
            if not url:
                continue
            data, info = get(url, {'Accept': 'application/pdf,*/*'}, raw=True)
            ok, why = save(data, dest, doi, title) if data else (False, info)
            tried.append(f'unpaywall {urllib.parse.urlparse(url).netloc}: {why}')
            if ok:
                return 'unpaywall', tried
    else:
        tried.append('unpaywall: skipped (UNPAYWALL_EMAIL not set)')
    pmcid = ((w or {}).get('ids') or {}).get('pmcid')
    if pmcid:
        pid = pmcid.rsplit('/', 1)[-1]
        data, info = get(f'https://europepmc.org/articles/{pid}?pdf=render', raw=True)
        ok, why = save(data, dest, doi, title) if data else (False, info)
        tried.append(f'europepmc: {why}')
        if ok:
            return 'europepmc', tried
    cr = get('https://api.crossref.org/works/' + urllib.parse.quote(doi))
    links = [l for l in ((cr or {}).get('message') or {}).get('link', []) if l.get('intended-application') == 'text-mining']
    wiley, els, insttok = os.environ.get('WILEY_TDM_TOKEN'), os.environ.get('ELSEVIER_API_KEY'), os.environ.get('ELSEVIER_INSTTOKEN')
    publisher = (((cr or {}).get('message') or {}).get('publisher') or '').lower()
    if 'wiley' in publisher:
        if wiley:
            url = 'https://api.wiley.com/onlinelibrary/tdm/v1/articles/' + urllib.parse.quote(doi, safe='')
            data, info = get(url, {'Wiley-TDM-Client-Token': wiley}, raw=True)
            ok, why = save(data, dest, doi, title) if data else (False, info)
            tried.append(f'tdm wiley: {why}')
            if ok:
                return 'tdm (Wiley)', tried
        else:
            tried.append('tdm wiley: skipped (WILEY_TDM_TOKEN not set)')
    if 'elsevier' in publisher:
        if els:
            h = {'X-ELS-APIKey': els, 'Accept': 'application/pdf'}
            if insttok:
                h['X-ELS-Insttoken'] = insttok
            data, info = get('https://api.elsevier.com/content/article/doi/' + urllib.parse.quote(doi), h, raw=True)
            ok, why = save(data, dest, doi, title) if data else (False, info)
            tried.append(f'tdm elsevier: {why}')
            if ok:
                return 'tdm (Elsevier)', tried
        else:
            tried.append('tdm elsevier: skipped (ELSEVIER_API_KEY not set)')
    for l in links:
        if 'wiley' in l['URL'] or 'elsevier' in l['URL']:
            continue
        data, info = get(l['URL'], {'Accept': 'application/pdf'}, raw=True)
        ok, why = save(data, dest, doi, title) if data else (False, info)
        tried.append(f'crossref tdm link {urllib.parse.urlparse(l["URL"]).netloc}: {why}')
        if ok:
            return 'crossref tdm link', tried
    return None, tried


def write_list(q: dict) -> None:
    R = refs()
    miss = {k: v for k, v in q.items() if v.get('status') != 'have'}
    have = {k: v for k, v in q.items() if v.get('status') == 'have'}
    L = ['# Papers to download by hand', '',
         f'Generated by `tools/fetch_pdfs.py` on {time.strftime("%Y-%m-%d")}. {len(miss)} still missing, {len(have)} in hand.',
         'Save each as `<key>.pdf` in `~/Dropbox/ARTICLES/METASCIENCE/` (any name works: the next run finds it by the DOI printed in the PDF).', '']
    blocked = {k: v for k, v in miss.items() if v.get('open_blocked')}
    if blocked:
        L += ['## Open copies that refuse scripted download (save from a browser)', '',
              'These are legally open; the host blocks scripts. Opening the link in a browser and saving the PDF is enough.', '']
        for k, v in sorted(blocked.items()):
            L.append(f'- **{k}**: ' + ' · '.join(f'[{urllib.parse.urlparse(u).netloc}]({u})' for u in v['open_blocked']))
        L.append('')
    groups: dict[str, list[str]] = {}
    for k, v in sorted(miss.items(), key=lambda kv: (kv[1].get('group', ''), kv[0])):
        groups.setdefault(v.get('group', 'other'), []).append(k)
    for g, ks in groups.items():
        L += [f'## {g}', '']
        for k in ks:
            v = q[k]
            m = v.get('meta') or {}
            cite = apa.reference(R[k]) if k in R else (f'{m.get("title")}. *{m.get("venue")}* ({m.get("year")}). https://doi.org/{v["doi"]}' if m.get('title') else f'https://doi.org/{v["doi"]}')
            last = '; '.join(v.get('tried', [])[-3:])
            L.append(f'- **{k}**: {cite} [UW Libraries]({PROXY}{v["doi"]}){f". Tried: {last}" if last else ""}')
        L.append('')
    if have:
        L += ['## In hand', '']
        L += [f'- {k}: {v.get("file")} ({v.get("route")})' for k, v in sorted(have.items())]
    LIST.write_text('\n'.join(L) + '\n')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('add'); a.add_argument('keys', nargs='+'); a.add_argument('--group', default='other')
    b = sub.add_parser('add-doi'); b.add_argument('file'); b.add_argument('--group', default='other')
    mf = sub.add_parser('add-manifest'); mf.add_argument('file')
    r = sub.add_parser('run'); r.add_argument('--out', type=Path, default=DEFAULT_OUT)
    r.add_argument('--library', type=Path, action='append'); r.add_argument('--dry-run', action='store_true')
    sub.add_parser('list')
    args = ap.parse_args()
    q = load_queue(); R = refs()
    if args.cmd == 'add':
        for k in args.keys:
            if k not in R or not R[k].get('doi'):
                print(f'skip {k}: not in references.bib or no DOI'); continue
            q.setdefault(k, {'doi': R[k]['doi'], 'status': 'missing', 'group': args.group, 'tried': []})
    elif args.cmd == 'add-doi':
        for line in Path(args.file).read_text().split('\n'):
            parts = line.split()
            if not parts or line.startswith('#'):
                continue
            key, doi = (parts[0], parts[1]) if len(parts) > 1 else (re.sub(r'\W+', '_', parts[0]), parts[0])
            q.setdefault(key, {'doi': doi, 'status': 'missing', 'group': args.group, 'tried': []})
    elif args.cmd == 'add-manifest':
        name = Path(args.file).name.split('.')[0]
        for line in Path(args.file).read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            q.setdefault(r['key'], {'doi': r['doi'], 'status': 'missing', 'group': f'Corpus {name}: {r.get("stratum", "all")}', 'tried': [],
                                    'meta': {'title': r.get('title'), 'year': r.get('year'), 'venue': r.get('venue')}})
    elif args.cmd == 'run':
        args.out.mkdir(parents=True, exist_ok=True)
        idx = index_library(args.library or DEFAULT_LIBRARY)
        by_doi = {d: f for f, v in idx.items() for d in v['dois']}
        for k, v in q.items():
            if v.get('status') == 'have' and v.get('file') and Path(v['file']).exists():
                continue
            doi = v['doi'].lower()
            if doi in by_doi:
                v.update(status='have', route='library', file=by_doi[doi]); print(f'{k}: in library'); continue
            if args.dry_run:
                print(f'{k}: would try routes'); continue
            title = R.get(k, {}).get('title', '')
            route, tried = routes_for(v['doi'], title, k, args.out)
            v['tried'] = tried; v['updated'] = time.strftime('%Y-%m-%d')
            v['open_blocked'] = sorted(set(BLOCKED.get(k, [])))
            if k not in R and META.get(k, {}).get('title'):
                v['meta'] = META[k]
            if route:
                v.update(status='have', route=route, file=str(args.out / f'{k}.pdf'))
            print(f'{k}: {route or "missing"}')
            store_queue(q)
    store_queue(q); write_list(q)
    n = sum(1 for v in q.values() if v.get('status') != 'have')
    print(f'{len(q)} queued, {n} missing; list at {LIST.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
