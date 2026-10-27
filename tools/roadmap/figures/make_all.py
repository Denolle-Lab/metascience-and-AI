#!/usr/bin/env python3
"""Rebuild every paper figure, in order, from the current derived data and codings.

Each fig*.py writes private/data/roadmap/figures/paper/<name>.pdf, .png and .json (provenance, numbers drawn, draft
caption) through paperstyle.save(). Run the analysis scripts first (g13, g14, g16, g17, g19, g20, g21) so the figures and the
reported numbers come from the same state; then commit the public repo before this run, so the commits recorded in
every .json are clean.

The public book embeds aggregate figures from assets/roadmap/ (results only, no paper-level identifiers). After the
figures are written, every PNG already present there is refreshed from the private copy; to publish a new figure,
copy it there once by hand after checking it shows no titles, DOIs or quotes.

Run: python tools/roadmap/figures/make_all.py [fig03 fig07 ...]
"""
from __future__ import annotations
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAPER = ROOT / 'private' / 'data' / 'roadmap' / 'figures' / 'paper'
PUBLIC = ROOT / 'assets' / 'roadmap'


def main() -> int:
    want = sys.argv[1:]
    scripts = sorted(p for p in HERE.glob('fig[0-9][0-9]_*.py') if not want or any(p.name.startswith(w) for w in want))
    failed = []
    for p in scripts:
        r = subprocess.run([sys.executable, str(p)], cwd=ROOT, capture_output=True, text=True)
        print(f"{'ok  ' if r.returncode == 0 else 'FAIL'} {p.name}")
        if r.returncode:
            failed.append(p.name)
            print(r.stderr[-2000:])
    print(f'{len(scripts) - len(failed)} of {len(scripts)} figures written')
    for pub in sorted(PUBLIC.glob('fig*.png')):
        shutil.copy2(PAPER / pub.name, pub)
        print(f'public copy refreshed: assets/roadmap/{pub.name}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
