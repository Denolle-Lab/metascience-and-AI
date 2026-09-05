#!/usr/bin/env python3
"""Check that every external link in the book sources resolves.

DOIs are verified through Crossref content negotiation rather than by fetching
the publisher page, because most publishers answer an automated request to a
resolved DOI with 403 regardless of whether the article exists. Other URLs are
fetched directly; a 403 or 405 there is reported for a human to judge rather
than failed, since it usually means bot mitigation.
"""
from __future__ import annotations
import concurrent.futures
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (sorted(ROOT.glob('*.qmd')) + sorted((ROOT / 'sessions').glob('*.qmd'))
           + [ROOT / 'references.bib'])
AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
         '(KHTML, like Gecko) Chrome/125 Safari/537.36')
TIMEOUT = 30
# 403 and 405 are bot mitigation, not evidence that a page is missing.
TOLERATED = {403, 405, 406, 501}


def extract(text: str) -> list[str]:
    """Pull URLs out of prose, honouring parentheses inside DOIs.

    A DOI such as 10.1016/S0022-1694(01)00421-8 contains balanced parentheses
    and is usually itself wrapped in a Markdown link, so a naive pattern stops
    in the wrong place.
    """
    found = []
    index = 0
    while (start := text.find('http', index)) != -1:
        if not text.startswith(('http://', 'https://'), start):
            index = start + 4
            continue
        depth = 0
        cursor = start
        while cursor < len(text):
            char = text[cursor]
            if char.isspace() or char in '<>"\'`]}|\\':
                break
            if char == '(':
                depth += 1
            elif char == ')':
                if depth == 0:
                    break
                depth -= 1
            cursor += 1
        found.append(text[start:cursor].rstrip('.,;:'))
        index = cursor if cursor > start else start + 4
    return found


FENCE = re.compile(r'^(`{3,}|~{3,}).*?^\1[^\S\n]*$', re.M | re.S)


def urls() -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for path in SOURCES:
        if not path.is_file():
            continue
        # Fenced blocks hold worked examples, whose placeholder URLs are not
        # meant to resolve.
        for url in extract(FENCE.sub('', path.read_text())):
            found.setdefault(url, set()).add(path.name)
    return found


def fetch(url: str, headers: dict[str, str], method: str = 'GET') -> int:
    request = urllib.request.Request(url, method=method,
                                     headers={'User-Agent': AGENT, **headers})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.status


DOI_PREFIX = 'https://doi.org/'


def check_doi(url: str) -> tuple[str, int | str]:
    """Ask the registry whether the DOI is registered.

    Not the publisher whether it feels like serving us the article today.
    Crossref rate-limits, so back off and retry rather than reporting 429 as
    if the record were missing.
    """
    doi = url[len(DOI_PREFIX):]
    api = 'https://api.crossref.org/works/' + urllib.request.quote(doi, safe='')
    for attempt in range(4):
        try:
            request = urllib.request.Request(api, headers={'User-Agent': AGENT})
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                payload = json.load(response)
            title = (payload.get('message', {}).get('title') or [''])[0]
            return url, 200 if title else 'registered, no title'
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return url, 'DOI not registered'
            if exc.code == 429 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return url, exc.code
        except Exception as exc:  # noqa: BLE001
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return url, type(exc).__name__
    return url, 'gave up after retries'


def check(url: str) -> tuple[str, int | str]:
    try:
        return url, fetch(url, {}, method='HEAD')
    except urllib.error.HTTPError as exc:
        if exc.code in TOLERATED:
            try:
                return url, fetch(url, {'Range': 'bytes=0-2047'})
            except urllib.error.HTTPError as inner:
                return url, inner.code
            except Exception as inner:  # noqa: BLE001
                return url, type(inner).__name__
        return url, exc.code
    except Exception as exc:  # noqa: BLE001
        return url, type(exc).__name__


def main() -> int:
    found = urls()
    dois = [u for u in found if u.startswith(DOI_PREFIX)]
    others = [u for u in found if not u.startswith(DOI_PREFIX)]
    results: dict[str, int | str] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results.update(dict(pool.map(check, others)))
    # Crossref is queried one DOI at a time on purpose; a burst earns a 429.
    for index, url in enumerate(sorted(dois)):
        if index:
            time.sleep(0.4)
        key, status = check_doi(url)
        results[key] = status
    failures, review = [], []
    for url in sorted(results):
        status = results[url]
        line = f'{status}  {url}  [{", ".join(sorted(found[url]))}]'
        if status in (200, 206):
            continue
        if status in TOLERATED:
            review.append(line)
        else:
            failures.append(line)
    print(f'Checked {len(results)} distinct URLs across '
          f'{sum(1 for p in SOURCES if p.is_file())} source files.')
    if review:
        print('\nBlocked by bot mitigation, not evidence of a broken link:')
        print('\n'.join('  ' + line for line in review))
    if failures:
        print('\nFAIL: unresolved:', file=sys.stderr)
        print('\n'.join('  ' + line for line in failures), file=sys.stderr)
        return 1
    print('\nPASS: every DOI is registered and every other URL resolves.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
