#!/usr/bin/env python3
"""Rebuild every paper figure, in order, from the current derived data and codings.

Each fig*.py writes private/data/roadmap/figures/paper/<name>.pdf, .png and .json (provenance, numbers drawn, draft
caption) through paperstyle.save(). Run the analysis scripts first (g13, g14, g16, g17, g19, g20, g21) so the figures and the
reported numbers come from the same state; then commit the public repo before this run, so the commits recorded in
every .json are clean.

The public book embeds aggregate figures from assets/roadmap/ (results only, no paper-level identifiers). After the
figures are written, the PNGs already present there are refreshed from the private copy, but only for figures whose
script ran in this call and exited 0, and never when METASCIENCE_PRIVATE is set (a run on a copy of the data release
or another tree must not replace the book's figures). To publish a new figure, copy it there once by hand after
checking it shows no titles, DOIs or quotes. A figure whose provenance JSON lists data_issues (an input older than
another, for instance) is reported as 'ok (stale input)' with the issues.

Run: python tools/roadmap/figures/make_all.py [fig03 fig07 ...]
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIVATE = Path(os.environ['METASCIENCE_PRIVATE']).resolve() if os.environ.get('METASCIENCE_PRIVATE') else ROOT / 'private'   # as in common.py
PAPER = PRIVATE / 'data' / 'roadmap' / 'figures' / 'paper'
PUBLIC = ROOT / 'assets' / 'roadmap'


def data_issues(name: str) -> list:
    try:
        return json.loads((PAPER / f'{name}.json').read_text()).get('numbers', {}).get('data_issues') or []
    except (OSError, ValueError, AttributeError):
        return []


def main() -> int:
    want = sys.argv[1:]
    scripts = sorted(p for p in HERE.glob('fig[0-9][0-9]_*.py') if not want or any(p.name.startswith(w) for w in want))
    failed, written = [], set()
    for p in scripts:
        r = subprocess.run([sys.executable, str(p)], cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            print(f'FAIL {p.name}')
            failed.append(p.name)
            print(r.stderr[-2000:])
            continue
        written.add(p.stem)
        issues = data_issues(p.stem)
        print(f"{'ok (stale input)' if issues else 'ok  '} {p.name}")
        for x in issues:
            print(f'     data issue: {x}')
    print(f'{len(scripts) - len(failed)} of {len(scripts)} figures written')
    if os.environ.get('METASCIENCE_PRIVATE'):
        print('public copies not refreshed: METASCIENCE_PRIVATE is set')
        return 1 if failed else 0
    for pub in sorted(PUBLIC.glob('fig*.png')):
        if pub.stem in written and (PAPER / pub.name).is_file():
            shutil.copy2(PAPER / pub.name, pub)
            print(f'public copy refreshed: assets/roadmap/{pub.name}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
