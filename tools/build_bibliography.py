#!/usr/bin/env python3
"""Generate the reading lists in bibliography.qmd from curriculum.json.

references.bib and curriculum.json are the sources of truth for what the book cites.
This script writes the by-meeting reading lists and the list of works cited outside
the meetings between the GENERATED markers in bibliography.qmd, so that page cannot
drift from those files. Run it after changing either source. tools/validate.py runs
it with --check and fails if the page is out of date.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'bibliography.qmd'
BEGIN = '<!-- BEGIN GENERATED: {name} -->'
END = '<!-- END GENERATED: {name} -->'


def entry(key: str, refs: dict) -> str:
    v = refs[key]
    line = f"**@{key}.** [{v['title']}]({v['url']}). {v['journal']}. {v['access']}"
    if v.get('note'):
        line += f"\n\n{v['note']}"
    return line


def by_meeting(data: dict) -> str:
    refs = data['references']
    out: list[str] = []
    for s in data['sessions']:
        out.append(f"### Meeting {s['n']}: {s['title']}\n")
        out.append(f"*[Session page](sessions/{s['n']:02}-{s['slug']}.qmd).*\n")
        for role, key in zip(('Anchor', 'Companion'), s['pair']):
            out.append(f'**{role}.**\n')
            out.append(entry(key, refs) + '\n')
        if s.get('corrections'):
            out.append('**Required correction with the companion.**\n')
            out.extend(entry(k, refs) + '\n' for k in s['corrections'])
        if s.get('discussant'):
            out.append('**Discussant-led.** Read in depth by one rotating discussant; everyone else reads the abstract.\n')
            out.extend(entry(k, refs) + '\n' for k in s['discussant'])
        if s.get('optional'):
            out.append('**Optional extensions.** The session page says in a sentence or two why each is there.\n')
            out.extend(entry(k, refs) + '\n' for k in s['optional'])
    return '\n'.join(out)


def outside_meetings(data: dict) -> str:
    used: set[str] = set()
    for s in data['sessions']:
        used.update(s['pair'])
        used.update(s.get('discussant', []))
        used.update(s.get('corrections', []))
        used.update(s.get('optional', []))
    keys = [k for k in data['references'] if k not in used]
    return '\n'.join(entry(k, data['references']) + '\n' for k in keys)


def splice(text: str, name: str, body: str) -> str:
    begin, end = BEGIN.format(name=name), END.format(name=name)
    if begin not in text or end not in text:
        raise SystemExit(f'bibliography.qmd is missing the {name} markers')
    i = text.index(begin) + len(begin)
    j = text.index(end)
    return text[:i] + '\n' + body.strip('\n') + '\n\n' + text[j:]


def render(data: dict, text: str) -> str:
    text = splice(text, 'by-meeting', by_meeting(data))
    return splice(text, 'outside-meetings', outside_meetings(data))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail if the page is out of date instead of rewriting it')
    args = parser.parse_args()
    data = json.loads((ROOT / 'curriculum.json').read_text())
    text = PAGE.read_text()
    new = render(data, text)
    if args.check:
        if new != text:
            print('FAIL: bibliography.qmd is out of date; run tools/build_bibliography.py', file=sys.stderr)
            return 1
        print('PASS: bibliography.qmd reading lists match references.bib and curriculum.json')
        return 0
    PAGE.write_text(new)
    print('bibliography.qmd updated')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
