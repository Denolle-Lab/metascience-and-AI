"""Build the public book page roadmap-report.qmd from the report of record, private/text/report-roadmap.md.

The report is public since October 27, 2026 (quotes of single papers are allowed; paper texts are not redistributed).
This script copies it into the book: the first heading becomes the page title, a status line goes under it, the
"Private; not for circulation" sentence is dropped, figure links are pointed at assets/roadmap/ and every figure PNG
the report uses is copied there from private/data/roadmap/figures/paper/. Paths written as code (`private/...`) are
left as they are: they name files in the data release, data/roadmap-release/, which mirrors the private layout.

Inputs   private/text/report-roadmap.md, private/data/roadmap/figures/paper/fig*.png
Outputs  roadmap-report.qmd, assets/roadmap/fig*.png
Run:     python tools/roadmap/build_report_page.py   (after make_all.py; then add roadmap-report.qmd to _quarto.yml once)
"""
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = Path(os.environ['METASCIENCE_PRIVATE']).resolve() if os.environ.get('METASCIENCE_PRIVATE') else ROOT / 'private'   # as in common.py
SRC = PRIVATE / 'text' / 'report-roadmap.md'
PAPER = PRIVATE / 'data' / 'roadmap' / 'figures' / 'paper'
ASSETS = ROOT / 'assets' / 'roadmap'
OUT = ROOT / 'roadmap-report.qmd'


def main() -> None:
    text = SRC.read_text()
    title, body = text.split('\n', 1)
    title = title.lstrip('# ').strip()
    version = re.search(r'Draft (v[\d.]+), ([A-Z][a-z]+ \d+, \d{4})', body)
    status = f'[{version.group(1)} · {version.group(2)} · model-coded, no human check yet]' if version else '[draft]'
    body = re.sub(r' ?Private; not for circulation outside the lab\.( The public book carries aggregate results only\.)?', '', body)
    figs = sorted(set(re.findall(r'\]\(\.\./data/roadmap/figures/paper/(fig\d\d_[a-z_]+\.png)\)', body)))
    body = re.sub(r'\]\(\.\./data/roadmap/figures/paper/(fig\d\d_[a-z_]+\.png)\)', r'](assets/roadmap/\1)', body)
    ASSETS.mkdir(parents=True, exist_ok=True)
    for f in figs:
        shutil.copy2(PAPER / f, ASSETS / f)
    page = (f'# {title} {{.unnumbered}}\n\n[Drafted]{{.status .drafted}} {status}{{.status-line}}\n\n'
            f'- Data release (codings with quotes, derived tables, figure provenance; no paper texts): '
            f'[`data/roadmap-release/`](https://github.com/Denolle-Lab/metascience-and-AI/tree/framework-v0.5/data/roadmap-release).\n'
            f'- Short result pages: [topics and journals](topics-journals.qmd), [workflows and outcomes](workflow-outcomes.qmd), '
            f'[peer review](review-visibility.qmd).\n' + body)
    # blinding: the page must not identify a paper still in human coding (same embargo as g22_release.py)
    sys.path.insert(0, str(ROOT / 'tools' / 'roadmap'))
    from g22_release import Embargo
    hits = Embargo(PRIVATE, lifted='--lift-embargo' in sys.argv).hits(page)
    if hits:
        sys.exit('roadmap-report.qmd NOT written, embargoed papers named: ' + '; '.join(hits))
    OUT.write_text(page)
    print(f'{OUT.name}: {len(body.split())} words, {len(figs)} figures copied to assets/roadmap/')


if __name__ == '__main__':
    main()
