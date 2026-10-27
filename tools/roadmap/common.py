"""Shared plumbing for the roadmap scripts: keys, OpenAlex access, raw-response cache, provenance log.

Every API call made through `openalex()` is cached verbatim under private/data/roadmap/raw/openalex/
(file name = sha1 of the URL without the key) and logged once per script run in
private/data/roadmap/MANIFEST.md with the date, script, git commit, query and record count.
Derived tables carry a `_provenance` block (script, commit, date, inputs) written by `write_json()`.
Nothing here sends the user's email; OpenAlex is called with the key from keys.env.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import keys  # noqa: E402
keys.load()

# The private tree (data, codings, reports). A colleague working from the public data release points it there:
# METASCIENCE_PRIVATE=data/roadmap-release python tools/roadmap/g13_calc1_results.py (relative paths resolve from the cwd).
PRIVATE = Path(os.environ['METASCIENCE_PRIVATE']).resolve() if os.environ.get('METASCIENCE_PRIVATE') else ROOT / 'private'
DATA = PRIVATE / 'data' / 'roadmap'
RAW = DATA / 'raw'
DERIVED = DATA / 'derived'
# Which paper set and corpus a run works on (round 1: gold / calc1). Round 2: ROADMAP_SET=r2 ROADMAP_CALC=r2calc.
SET = DERIVED / os.environ.get('ROADMAP_SET', 'gold')
CALC = DERIVED / os.environ.get('ROADMAP_CALC', 'calc1')
MANIFEST = DATA / 'MANIFEST.md'
# Which tree a run read: the private tree, or a copy of the public data release (it holds RELEASE.json). Recorded in
# every provenance block and MANIFEST row, so a rerun's output is never mistaken for the record.
_REL = PRIVATE / 'RELEASE.json'
PRIVATE_ROOT = 'private' if not os.environ.get('METASCIENCE_PRIVATE') else (
    ('release (embargo on)' if json.loads(_REL.read_text()).get('embargo', {}).get('active') else 'release (embargo lifted)')
    if _REL.is_file() else 'METASCIENCE_PRIVATE (not a release)')
DECISIONS = DATA / 'DECISIONS.md'
API = 'https://api.openalex.org'
UA = {'User-Agent': 'metascience-roadmap/1.0'}
TODAY = dt.date.today().isoformat()
_calls = {'api': 0, 'cache': 0}


def commit() -> str:
    try:
        sha = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain', 'tools/roadmap'], capture_output=True, text=True).stdout.strip()
        return sha + ('+uncommitted' if dirty else '')
    except Exception:  # noqa: BLE001
        return 'unknown'


def rel(p) -> str:
    """A path as provenance writes it: 'private/...' under the private tree (wherever METASCIENCE_PRIVATE points),
    repository-relative under the repository, else as given. Never a local home path for files of either tree."""
    p = Path(p)
    for base, pre in ((PRIVATE, 'private/'), (ROOT, '')):
        try:
            return pre + p.resolve().relative_to(base.resolve()).as_posix()
        except ValueError:
            continue
    return str(p)


def private_path(f: str | Path) -> Path:
    """Resolve a path stored in the fetch queue ('private/data/roadmap/pdfs/...', relative to the repository) against
    the private tree in use; absolute paths are kept as they are, other relative paths resolve from the repository."""
    f = Path(f)
    if f.is_absolute():
        return f
    if f.parts and f.parts[0] == 'private':
        return PRIVATE.joinpath(*f.parts[1:])
    return ROOT / f


def openalex(path: str, params: dict | None = None, refresh: bool = False) -> dict:
    """GET {API}/{path}?{params}; cached by URL. Returns {} on 404."""
    q = dict(params or {})
    url = f'{API}/{path.lstrip("/")}' + ('?' + urllib.parse.urlencode(q, safe=':,|') if q else '')
    cache = RAW / 'openalex' / (hashlib.sha1(url.encode()).hexdigest() + '.json')
    if cache.is_file() and not refresh:
        _calls['cache'] += 1
        return json.loads(cache.read_text())['response']
    key = os.environ.get('OPENALEX_API_KEY')
    full = url + (('&' if '?' in url else '?') + 'api_key=' + urllib.parse.quote(key) if key else '')
    for a in range(7):
        try:
            with urllib.request.urlopen(urllib.request.Request(full, headers=UA), timeout=120) as r:
                resp = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                resp = {}
                break
            if e.code in (429, 500, 502, 503, 504) and a < 6:
                time.sleep(int(e.headers.get('Retry-After') or 0) or 2 ** a * 3)
                continue
            raise
        except Exception:  # noqa: BLE001
            if a == 6:
                raise
            time.sleep(2 ** a * 2)
    _calls['api'] += 1
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({'url': url, 'retrieved': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'response': resp}))
    return resp


def paged(path: str, params: dict, cap: int = 10000) -> list[dict]:
    """All results of a list endpoint, by page number, so every page is cached under a stable URL.
    OpenAlex serves at most 10,000 results by page number; a larger single-year query is split by month."""
    import calendar
    import re
    flt = params.get('filter', '')
    m = re.search(r'publication_year:(\d{4})(?=,|$)', flt)
    if m and cap > 10000:
        n = openalex(path, {**params, 'per-page': 1, 'select': 'id'}).get('meta', {}).get('count', 0)
        if n > 10000:
            y, out = int(m.group(1)), []
            for mo in range(1, 13):
                last = calendar.monthrange(y, mo)[1]
                f2 = flt.replace(m.group(0), f'from_publication_date:{y}-{mo:02d}-01,to_publication_date:{y}-{mo:02d}-{last}')
                out += paged(path, {**params, 'filter': f2}, cap=10000)
            return out[:cap]
    out, page = [], 1
    while len(out) < cap:
        r = openalex(path, {**params, 'per-page': 200, 'page': page})
        res = r.get('results', [])
        out += res
        if len(res) < 200:
            break
        page += 1
    return out[:cap]


def log(script: str, what: str, n: int, note: str = '') -> None:
    """Append one line per script run to MANIFEST.md."""
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    if not MANIFEST.is_file():
        MANIFEST.write_text('# Download and derivation log\n\n| Date | Script | Commit | What | Records | API calls / cache hits | Note |\n|:--|:--|:--|:--|:--|:--|:--|\n')
    with MANIFEST.open('a') as f:
        tree = '' if PRIVATE_ROOT == 'private' else f' [tree: {PRIVATE_ROOT}]'
        f.write(f"| {TODAY} | `{script}` | {commit()} | {what} | {n} | {_calls['api']} / {_calls['cache']} | {note}{tree} |\n")


def decision(text: str) -> None:
    """Append a dated decision to DECISIONS.md (selection rules, thresholds, exclusions)."""
    DECISIONS.parent.mkdir(parents=True, exist_ok=True)
    if not DECISIONS.is_file():
        DECISIONS.write_text('# Decisions log\n\nEach entry: date, script, commit, the decision and its reason. Newest last.\n\n')
    with DECISIONS.open('a') as f:
        f.write(f'- {TODAY} `{Path(sys.argv[0]).name}` ({commit()}): {text}\n')


def write_json(path: Path, data, inputs: list[str], params: dict | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    prov = {'script': Path(sys.argv[0]).name, 'commit': commit(), 'date': TODAY, 'private_root': PRIVATE_ROOT,
            'inputs': inputs, 'params': params or {}}
    path.write_text(json.dumps({'_provenance': prov, 'data': data}, indent=1, ensure_ascii=False))


def read_json(path: Path):
    return json.loads(Path(path).read_text())['data']


def sid(x: str | None) -> str | None:
    return x.rsplit('/', 1)[-1] if x else None
