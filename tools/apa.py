#!/usr/bin/env python3
"""Render curriculum.json reference records as APA-style references.

Titles keep the capitalisation the journal published them under. APA asks for
sentence case, but the corpus spans Cascadia, the Holocene, GLUE and Leonardo da
Vinci, and lowercasing those automatically does more damage than the deviation.
Everything else follows APA 7: inverted names with initials, ampersand before the
final author, italic journal and volume, issue in parentheses, and the URL last.
"""
from __future__ import annotations
import re
from urllib.parse import quote

BOOK = re.compile(r'\b(Press|Publishers|Publishing)\b')
CONFERENCE = re.compile(r'\b(Conference|Proceedings|Association for Computational Linguistics|Symposium|Workshop)\b')


def initials(given: str) -> str:
    """'John R.' -> 'J. R.'   'Wei-Hung' -> 'W.-H.'"""
    out = []
    for token in given.replace('.', ' ').split():
        pieces = [p for p in token.split('-') if p]
        out.append('-'.join(p[0].upper() + '.' for p in pieces))
    return ' '.join(out)


def one_author(name: str) -> str:
    if ',' not in name:
        return name.strip()
    family, _, given = name.partition(',')
    given = given.strip()
    return f'{family.strip()}, {initials(given)}' if given else family.strip()


def authors(field: str) -> str:
    """BibTeX 'A and B and others' -> APA author string."""
    parts = [p.strip() for p in field.split(' and ') if p.strip()]
    truncated = bool(parts) and parts[-1].lower() in {'others', 'et al.', 'et al'}
    if truncated:
        parts = parts[:-1]
    names = [one_author(p) for p in parts]
    if not names:
        return ''
    if len(names) == 1:
        return names[0]
    # APA 7: list up to 20; for 21 or more, first 19, an ellipsis, then the last.
    if len(names) > 20 or (truncated and len(names) >= 20):
        return ', '.join(names[:19]) + ', . . . ' + names[-1]
    return ', '.join(names[:-1]) + ', & ' + names[-1]


def pages(value: str) -> str:
    return value.replace('--', '–').replace('-', '–') if value else ''


def doi_url(record: dict) -> str:
    """APA wants the DOI when one exists, and the stored link otherwise."""
    url = record.get('url', '')
    if url.startswith('https://doi.org/'):
        return url  # already the DOI, and already percent-encoded where needed
    doi = (record.get('doi') or '').strip()
    if doi:
        return 'https://doi.org/' + quote(doi, safe='/.-_;()')
    return url


def link(url: str) -> str:
    # Angle brackets round the destination so parentheses inside a DOI are safe.
    return f'[{url}](<{url}>)'


def reference(record: dict) -> str:
    """One APA reference, ending in a linked URL."""
    who = authors(record['author'])
    year = record.get('year', 'n.d.')
    title = record['title'].rstrip('.')
    journal = record.get('journal', '').strip().rstrip(':')
    volume, issue, page = record.get('volume', ''), record.get('issue', ''), pages(record.get('pages', ''))
    url = doi_url(record)

    if volume:
        where = f'*{journal}, {volume}*'
        if issue:
            where += f'({issue})'
        if page:
            where += f', {page}'
        body = f'{title}. {where}.'
    elif journal.lower().startswith('arxiv'):
        ident = journal.split()[-1] if journal.split() else 'arXiv'
        body = f'{title}. *arXiv*, {ident}.'
    elif BOOK.search(journal):
        body = f'*{title}*. {journal}.'
    elif CONFERENCE.search(journal):
        body = f'{title}. In *{journal}*.'
    else:
        body = f'{title}. *{journal}*.'

    return ' '.join(part for part in [f'{who} ({year}).', body, link(url)] if part)


if __name__ == '__main__':
    import json
    import sys
    from pathlib import Path
    refs = json.loads((Path(__file__).resolve().parents[1] / 'curriculum.json').read_text())['references']
    keys = sys.argv[1:] or list(refs)
    for key in keys:
        print(f'{key}:\n  {reference(refs[key])}\n')
