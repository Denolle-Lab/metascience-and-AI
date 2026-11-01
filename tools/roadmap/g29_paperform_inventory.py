"""Inventory for the paper-form study (agents/paperform/CODEBOOK.md v0.1.0, private/analysis/paperform-plan.md).

Direction from the PI (October 28, 2026): papers are not written the way the science is done, they follow recipes,
and the translation from a finished workflow to a paper should be studied. Before anything is coded, this script
counts what the form study can draw on, so that the plan's sample sizes rest on counts, not on guesses. It reads and
counts; it codes nothing and calls no model.

Steps
  journals   OpenAlex article counts (type:article) per wave year 2005, 2010, 2015, 2020, 2025, all and open access,
             for a candidate panel of Earth-science journals (JOURNALS below, by ISSN). Through common.openalex (key from
             keys.env, every response cached verbatim under raw/openalex/). OpenAlex files JGR Solid Earth before 2013
             under one "Journal of Geophysical Research" source, so its 2005 and 2010 counts read 0 here; that is an
             indexing artefact, not an absence of papers.
  corpus     For every paper of the two coded rounds (derived/calc1/manifest.jsonl, derived/r2calc/manifest.jsonl) whose
             full text is on disk in pdfs/gold/: publisher and journal (derived/gold/preselect.json,
             derived/r2/preselect.json), text route (XML, PDF), and the front-matter elements the text carries.
               XML  JATS <abstract abstract-type=...>: key points, plain language summary, highlights, short summary,
                    graphical; Elsevier <ce:abstract class=...>: author-highlights, graphical; data or code availability
                    statement found by tools/jats_text.py _availability(). The stored <key>.xml.txt keeps only the first
                    abstract (jats_text convert), so these elements are absent from the text the coders have read so far.
               PDF  pdftotext of the first 3 pages: a line starting "Key Points", "Plain Language Summary",
                    "Highlights", "Graphical abstract"; whole text: "Data Availability", "Open Research",
                    "Code availability", "Code and data availability". A string match, so a PDF count is an upper
                    bound for highlights (the word can open a section of another kind) and a lower bound where
                    pdftotext loses the heading.
  review     For the 61 Copernicus papers with an open discussion (derived/review/open_review_index.json): files on
             disk per kind (discussion preprint, manuscript versions, tracked-changes ATC, author responses AR, referee
             RC, editor ED, author comment AC, supplements), referee-, editor- or commenter-triggered review steps per
             paper in the E3 review codings that pass tools/check_coding.py validate() (private/analysis/codings/api/
             calc1-review/, read only; 58 of 61 at E3), and workflow
             disclosures per paper from g27 (derived/translation/author_responses.json, read only).

Outputs  private/data/roadmap/derived/paperform/{inventory.json, INVENTORY.md}; one MANIFEST.md line.
Run:     python tools/roadmap/g29_paperform_inventory.py [--skip-openalex]
"""
from __future__ import annotations

import argparse
import json
import re
import statistics as st
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

from common import PRIVATE, DATA, DERIVED, TODAY, openalex, write_json, log, rel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jats_text  # noqa: E402
import check_coding  # noqa: E402

GOLD = DATA / 'pdfs' / 'gold'
REVIEW = DATA / 'review'
OUT = DERIVED / 'paperform'
CODINGS_REVIEW = PRIVATE / 'analysis' / 'codings' / 'api' / 'calc1-review'
WAVES = (2005, 2010, 2015, 2020, 2025)
JOURNALS = {
    'Geophysical Research Letters': '0094-8276', 'JGR Solid Earth': '2169-9313', 'JGR Atmospheres': '2169-897X',
    'Atmospheric Chemistry and Physics': '1680-7316', 'Hydrology and Earth System Sciences': '1027-5606',
    'Natural Hazards and Earth System Sciences': '1561-8633', 'The Cryosphere': '1994-0416', 'Solid Earth': '1869-9510',
    'Biogeosciences': '1726-4170', 'Climate of the Past': '1814-9324', 'Earth and Planetary Science Letters': '0012-821X',
    'Geophysical Journal International': '0956-540X', 'Bulletin of the Seismological Society of America': '0037-1106',
    'Earth, Planets and Space': '1880-5981'}
XML_KINDS = {'key points': 'key_points', 'keypoints': 'key_points', 'plainlanguage': 'plain_language_summary',
             'plain language summary': 'plain_language_summary', 'plain-language-summary': 'plain_language_summary',
             'articlehighlights': 'highlights', 'article highlights': 'highlights', 'author-highlights': 'highlights',
             'highlights': 'highlights', 'shortsummary': 'short_summary', 'graphical': 'graphical_abstract'}
PDF_FRONT = {'key_points': r'^\s*Key Points\b', 'plain_language_summary': r'^\s*Plain Language Summary\b',
             'highlights': r'^\s*(?:Research )?Highlights\s*$', 'graphical_abstract': r'^\s*Graphical abstract\b'}
PDF_AVAIL = r'^\s*(?:\d+(?:\.\d+)*\.?\s*)?(?:Data Availability|Open Research|Code availability|Code and data availability)'
ELEMENTS = ('key_points', 'plain_language_summary', 'highlights', 'short_summary', 'graphical_abstract', 'availability')


def local(tag: str) -> str:
    return tag.rsplit('}', 1)[-1]


def journals() -> dict:
    out = {}
    for name, issn in JOURNALS.items():
        s = openalex(f'sources/issn:{issn}')
        sid = (s.get('id') or '').rsplit('/', 1)[-1]
        rows = {}
        for oa in (False, True):
            f = f'primary_location.source.id:{sid},type:article,publication_year:2005-2025' + (',is_oa:true' if oa else '')
            g = {int(x['key']): x['count'] for x in openalex('works', {'filter': f, 'group_by': 'publication_year'}).get('group_by', [])}
            rows['oa' if oa else 'all'] = {y: g.get(y, 0) for y in WAVES}
        out[name] = {'issn': issn, 'openalex_source': sid, 'display_name': s.get('display_name'),
                     'publisher': s.get('host_organization_name'), **rows}
    return out


def meta() -> dict:
    m = {}
    for f, rnd in (('gold/preselect.json', 'round1'), ('r2/preselect.json', 'round2')):
        for p in json.loads((DERIVED / f).read_text())['data']:
            m['g22_' + p['id']] = {'journal': p.get('journal'), 'publisher': p.get('publisher'), 'round': rnd}
    return m


def xml_front(path: Path) -> dict:
    root = ET.parse(path).getroot()
    found = Counter()
    for e in root.iter():
        if local(e.tag) != 'abstract':     # JATS <abstract abstract-type=...> and Elsevier <ce:abstract class=...>
            continue
        k = XML_KINDS.get((e.get('abstract-type') or e.get('class') or '').strip().lower())
        if k:
            found[k] += 1
    found['availability'] = len(jats_text._availability(root, set()))
    return {k: found.get(k, 0) > 0 for k in ELEMENTS}


def pdf_front(path: Path) -> dict:
    def text(last: int | None) -> str:
        cmd = ['pdftotext', '-q'] + (['-l', str(last)] if last else []) + [str(path), '-']
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout
        except subprocess.TimeoutExpired:
            return ''
    head, whole = text(3), text(None)
    r = {k: bool(re.search(p, head, re.M | re.I if k == 'graphical_abstract' else re.M)) for k, p in PDF_FRONT.items()}
    r['short_summary'] = False
    r['availability'] = bool(re.search(PDF_AVAIL, whole, re.M | re.I))
    return {k: r[k] for k in ELEMENTS}


def corpus() -> dict:
    m = meta()
    keys = []
    for f in ('calc1/manifest.jsonl', 'r2calc/manifest.jsonl'):
        keys += [json.loads(line)['key'] for line in (DERIVED / f).read_text().splitlines() if line.strip()]
    rows = []
    for k in dict.fromkeys(keys):
        xml, pdf = GOLD / f'{k}.xml', GOLD / f'{k}.pdf'
        if not xml.is_file() and not pdf.is_file():
            continue
        row = {'key': k, **m.get(k, {}), 'xml': xml.is_file(), 'pdf': pdf.is_file()}
        fx = xml_front(xml) if xml.is_file() else None
        fp = pdf_front(pdf) if pdf.is_file() else None
        row['front'] = {e: bool((fx or {}).get(e) or (fp or {}).get(e)) for e in ELEMENTS}
        row['front_route'] = 'xml+pdf' if fx and fp else ('xml' if fx else 'pdf')
        rows.append(row)
    by_pub = defaultdict(lambda: Counter())
    for r in rows:
        c = by_pub[r.get('publisher') or 'unknown']
        c['papers'] += 1
        c['xml'] += r['xml']
        c['pdf'] += r['pdf']
        for e in ELEMENTS:
            c[e] += r['front'][e]
    return {'papers': len(rows), 'by_round': dict(Counter(r.get('round', 'unknown') for r in rows)),
            'by_publisher': {p: dict(c) for p, c in sorted(by_pub.items(), key=lambda x: -x[1]['papers'])},
            'rows': rows}


def kind_of(name: str) -> str:
    for k, p in (('supplement', r'supplement'), ('manuscript_version', r'manuscript-version\d+'), ('AR', r'-AR\d+'),
                 ('ATC', r'-ATC\d+'), ('RC', r'-RC\d+'), ('ED', r'-ED\d+'), ('CC', r'-CC\d+'), ('AC', r'-AC\d+')):
        if re.search(p, name):
            return k
    return 'discussion_text' if name == 'discussion.txt' else 'preprint_or_other'


def review() -> dict:
    idx = json.loads((DERIVED / 'review' / 'open_review_index.json').read_text())['data']
    keys = [r['key'] for r in idx if not r.get('no_open_discussion')]
    files = Counter()
    papers_with = Counter()
    for k in keys:
        kinds = Counter(kind_of(p.name) for p in (REVIEW / k).iterdir()) if (REVIEW / k).is_dir() else Counter()
        files.update(kinds)
        papers_with.update({x: 1 for x in kinds})
    triggered, invalid = {}, []
    for f in sorted(CODINGS_REVIEW.glob('*.json')):
        d = json.loads(f.read_text())
        if check_coding.validate(d):
            invalid.append(f.stem)
            continue
        seq = next((s for s in d.get('sequences', []) if s.get('kind') == 'review'), None)
        steps = (seq or {}).get('steps', [])
        triggered[d.get('key', f.stem)] = {
            'triggered': sum(1 for s in steps if s.get('trigger') in ('referee', 'editor', 'commenter')),
            'review_forced': sum(1 for s in steps if s.get('move') == 'review_forced'),
            'declined': sum(1 for s in steps if s.get('move') == 'declined')}
    t = [v['triggered'] for v in triggered.values()]
    ar_path = DERIVED / 'translation' / 'author_responses.json'
    ar = json.loads(ar_path.read_text())['data']['summary'] if ar_path.is_file() else None
    return {'papers_open_discussion': len(keys), 'files_by_kind': dict(files), 'papers_with_kind': dict(papers_with),
            'review_codings_valid': len(triggered), 'review_codings_invalid': invalid,
            'triggered_steps': {'total': sum(t), 'median': st.median(t) if t else None, 'min': min(t, default=None),
                                'max': max(t, default=None)} if t else None,
            'per_paper': triggered, 'author_responses_summary': ar}


def report(d: dict) -> str:
    L = [f'# Paper-form inventory ({TODAY})', '',
         f'Script `tools/roadmap/g29_paperform_inventory.py`; data `{rel(OUT / "inventory.json")}`. Counts only; nothing coded.', '']
    if d.get('journals'):
        L += ['## Candidate journal panel: articles per wave year (OpenAlex, all / open access)', '',
              '| Journal | ' + ' | '.join(map(str, WAVES)) + ' |', '|:--|' + '--:|' * len(WAVES)]
        for n, j in d['journals'].items():
            L.append(f'| {n} | ' + ' | '.join(f"{j['all'][y]} / {j['oa'][y]}" for y in WAVES) + ' |')
        L += ['', 'JGR Solid Earth before 2013 is indexed under the single JGR source, hence 0.', '']
    c = d['corpus']
    L += [f'## Coded rounds with full text on disk: {c["papers"]} papers ({c["by_round"]})', '',
          '| Publisher | Papers | XML | PDF | ' + ' | '.join(ELEMENTS) + ' |', '|:--|' + '--:|' * (3 + len(ELEMENTS))]
    for p, x in c['by_publisher'].items():
        L.append(f'| {p} | {x["papers"]} | {x.get("xml", 0)} | {x.get("pdf", 0)} | ' + ' | '.join(str(x.get(e, 0)) for e in ELEMENTS) + ' |')
    r = d['review']
    L += ['', f'## Copernicus open review: {r["papers_open_discussion"]} papers', '',
          f'Files by kind: {r["files_by_kind"]}', '', f'Papers with each kind: {r["papers_with_kind"]}', '',
          f'Valid E3 review codings: {r["review_codings_valid"]}; referee-, editor- or commenter-triggered steps: {r["triggered_steps"]}', '']
    return '\n'.join(L) + '\n'


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--skip-openalex', action='store_true', help='leave out the journal panel counts')
    a = ap.parse_args()
    d = {'journals': None if a.skip_openalex else journals(), 'corpus': corpus(), 'review': review()}
    inputs = ['derived/calc1/manifest.jsonl', 'derived/r2calc/manifest.jsonl', 'derived/gold/preselect.json',
              'derived/r2/preselect.json', 'pdfs/gold/<key>.xml|.pdf', 'derived/review/open_review_index.json',
              'review/<key>/', 'private/analysis/codings/api/calc1-review/*.json (read only)',
              'derived/translation/author_responses.json'] + ([] if a.skip_openalex else ['OpenAlex sources and works group_by'])
    write_json(OUT / 'inventory.json', d, inputs, {'waves': WAVES, 'journals': JOURNALS})
    (OUT / 'INVENTORY.md').write_text(report(d))
    log('g29_paperform_inventory.py', 'paper-form inventory: journal panel counts, front matter on disk, open-review files',
        d['corpus']['papers'], f"{d['review']['papers_open_discussion']} open-review papers")
    print(report(d))


if __name__ == '__main__':
    main()
