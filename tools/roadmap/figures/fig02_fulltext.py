"""Figure 2: full-text access by publisher for the eligible papers of each round (round 1, and round 2 when present).

What it shows
  For each publisher, one horizontal 100% stacked bar over the round's eligible papers: PDF and publisher XML, PDF only,
  XML only (drawn and put in the legend only when a round has any), no full text. Beside it, a narrow panel with the
  open-access share (OpenAlex is_oa) of the same papers. One row of panels per round, an "All publishers" row on top.
  Both rounds use one publisher order: round-1 eligible count, then publishers that only round 2 shows, then Other.

Publisher labels
  metrics.json `publisher` is the OpenAlex host organization assigned in g02_pool.py, not the DOI registrant. GJI, BSSA
  and SRL carry their journal name because they enter the pool by source id; the figure adds their publisher in
  parentheses. Two relabelling rules, each counted under 'checks' in the provenance numbers:
    AGU         a journal name on the AGU list below (Wiley publishes these for AGU; OpenAlex hosts only some under
                AGU). In rounds 1 and 2 this selects exactly the papers with DOI prefix 10.1029 ('checks' counts any
                difference as agu_list_vs_prefix_10.1029_mismatch).
    Copernicus  DOI prefix 10.5194 (European Journal of Mineralogy, which OpenAlex hosts under Elsevier).
  Within each round, a publisher with fewer than 5 eligible papers is folded into "Other".

Full-text status (read as the files stand at run time; rerun after any re-fetch by tools/fetch_pdfs.py)
  PDF  private/download-queue.json status 'have' and the file it names (or pdfs/gold/<key>.pdf) exists on disk
  XML  the round's xml_status.json says xml true and pdfs/gold/<key>.xml exists on disk; the xml_status 'route' of
       each XML paper, its format read from the file's root element (JATS <article> or Elsevier
       <full-text-retrieval-response>; xml_status says 'already present' for files kept from an earlier run), and the
       Elsevier 'HTTP 403' refusals of papers still without XML are recorded in the provenance numbers; the XML sentence
       of the caption is built from these counts
  Disagreements between the status files and the disk are counted in the provenance numbers under 'checks'.

Inputs
  private/data/roadmap/derived/calc1/manifest.jsonl, calc1/xml_status.json, gold/metrics.json   round 1 (525 eligible)
  private/data/roadmap/derived/r2calc/manifest.jsonl, r2calc/xml_status.json, r2/metrics.json   round 2 (if present)
  private/download-queue.json; private/data/roadmap/pdfs/gold/
Outputs  private/data/roadmap/figures/paper/fig02_fulltext.{pdf,png,json}
Run:     python tools/roadmap/figures/fig02_fulltext.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402

from matplotlib.gridspec import GridSpec  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

D = ps.DERIVED
QUEUE = ps.ROOT / 'private' / 'download-queue.json'
PDFS = ps.DATA / 'pdfs' / 'gold'
MIN_N = 5
ROUNDS = [  # (label, manifest folder, metrics folder)
    ('Round 1', 'calc1', 'gold'),
    ('Round 2', 'r2calc', 'r2'),
]
# AGU journals (published by Wiley on AGU's behalf), compared after removing case and non-letters
AGU = ["Geophysical Research Letters", "Journal of Geophysical Research Atmospheres", "Journal of Geophysical Research Biogeosciences",
       "Journal of Geophysical Research Earth Surface", "Journal of Geophysical Research Oceans",
       "Journal of Geophysical Research Planets", "Journal of Geophysical Research Solid Earth",
       "Journal of Geophysical Research Space Physics", "Journal of Geophysical Research Machine Learning and Computation",
       "Water Resources Research", "Tectonics", "Geochemistry Geophysics Geosystems", "Global Biogeochemical Cycles",
       "Paleoceanography and Paleoclimatology", "Paleoceanography", "Journal of Advances in Modeling Earth Systems",
       "Reviews of Geophysics", "Radio Science", "Space Weather", "Earth's Future", "Earth and Space Science", "GeoHealth",
       "AGU Advances", "Community Science", "Perspectives of Earth and Space Scientists"]
NORM = lambda s: re.sub(r'[^a-z]', '', (s or '').lower())  # noqa: E731
AGU_KEYS = {NORM(j) for j in AGU}
COPERNICUS_PREFIX = '10.5194'
PLEIADES_PREFIXES = ('10.1134', '10.3103')  # Pleiades Publishing, Russian journals in translation (Springer Nature host)
PREFIX_NAMES = {'10.2113': 'GeoScienceWorld', '10.1002': 'Wiley', '10.1007': 'Springer', '10.1186': 'BioMed Central'}
CATS = [('both', 'PDF and XML', ps.BLUE), ('pdf', 'PDF only', ps.ORANGE), ('xml', 'XML only', ps.AQUA),
        ('none', 'No full text', ps.NEUTRAL)]
SHORT = {'Geophysical Journal International': 'GJI (Oxford)', 'Bulletin of the Seismological Society of America': 'BSSA (SSA)',
         'Seismological Research Letters': 'SRL (SSA)', 'AGU': 'AGU (Wiley)', 'Wiley': 'Wiley, not AGU',
         'Springer': 'Springer (incl. Pleiades)'}
FT_HEADER = 'Any full text'


def read_queue(tries: int = 5) -> dict:
    """The queue may be rewritten by a running fetch; retry a partial read."""
    for a in range(tries):
        try:
            return json.loads(QUEUE.read_text())
        except json.JSONDecodeError:
            if a == tries - 1:
                raise
            time.sleep(0.5)
    return {}


def resolve(f: str | None) -> Path | None:
    if not f:
        return None
    p = Path(f)
    return p if p.is_absolute() else ps.ROOT / p


def doi_prefix(doi: str | None) -> str:
    d = (doi or '').lower().replace('https://doi.org/', '').strip()
    return d.split('/')[0] if '/' in d else ''


def xml_format(path: Path) -> tuple[str, bool]:
    """Format of a full-text XML file from its root element, and whether it holds an article body."""
    t = path.read_text(errors='ignore')
    head = t[:3000]
    fmt = ('elsevier' if '<full-text-retrieval-response' in head else 'jats' if re.search(r'<article[\s>]', head)
           else 'other')
    body = '<body' in t or '<ce:sections' in t
    return fmt, body


def load_round(mfold: str, metfold: str, queue: dict):
    man = [json.loads(line) for line in (D / mfold / 'manifest.jsonl').read_text().splitlines() if line.strip()]
    met = {r['id']: r for r in ps.read_json(D / metfold / 'metrics.json')}
    xs = {r['key']: r for r in ps.read_json(D / mfold / 'xml_status.json')}
    checks = Counter()
    rows = []
    for r in man:
        k = r['key']
        m = met.get(r['openalex'])
        if m is None:
            checks['no_metrics_row'] += 1
            continue
        q = queue.get(k)
        if q is None:
            checks['not_in_queue'] += 1
        qhave = bool(q) and q.get('status') == 'have'
        qf = resolve(q.get('file')) if q else None
        on_disk = (qf is not None and qf.is_file()) or (PDFS / f'{k}.pdf').is_file()
        pdf = qhave and on_disk
        if qhave and not on_disk:
            checks['queue_have_no_pdf_file'] += 1
        if not qhave and (PDFS / f'{k}.pdf').is_file():
            checks['pdf_file_but_queue_missing'] += 1
        if qhave and qf is not None and PDFS not in qf.parents:
            checks['pdf_outside_pdfs_gold'] += 1
        xrec = xs.get(k)
        if xrec is None:
            checks['not_in_xml_status'] += 1
        xflag = bool(xrec and xrec.get('xml'))
        xdisk = (PDFS / f'{k}.xml').is_file()
        xml = xflag and xdisk
        if xflag and not xdisk:
            checks['xml_status_true_no_file'] += 1
        if xdisk and not xflag:
            checks['xml_file_but_status_false'] += 1
        prefix = doi_prefix(m.get('doi') or r.get('doi'))
        pub = m.get('publisher') or 'Unknown'
        agu = NORM(m.get('journal')) in AGU_KEYS
        if agu != (prefix == '10.1029'):
            checks['agu_list_vs_prefix_10.1029_mismatch'] += 1
        if agu and pub != 'AGU':
            checks[f'relabelled_AGU_from_{pub}'] += 1
            pub = 'AGU'
        elif prefix == COPERNICUS_PREFIX and pub != 'Copernicus':
            checks[f'relabelled_Copernicus_from_{pub}'] += 1
            pub = 'Copernicus'
        elif pub == 'Springer Nature':   # OpenAlex splits Springer journals between two labels; Nature Portfolio stays apart
            checks['merged_Springer_Nature_into_Springer'] += 1
            pub = 'Springer'
        cat = 'both' if pdf and xml else 'pdf' if pdf else 'xml' if xml else 'none'
        xfmt = None
        if xml:
            xfmt, xbody = xml_format(PDFS / f'{k}.xml')
            if not xbody:
                checks['xml_without_body'] += 1
        tried = (xrec or {}).get('tried') or []
        rows.append({'key': k, 'publisher': pub, 'cat': cat, 'oa': bool(m.get('is_oa')), 'prefix': prefix,
                     'xml_route': (xrec or {}).get('route') if xml else None, 'xml_format': xfmt,
                     'elsevier_403': not xml and any(str(t).startswith('elsevier: HTTP 403') for t in tried)})
    return rows, checks


def tabulate(rows):
    n = Counter(r['publisher'] for r in rows)
    keep = {p for p, c in n.items() if c >= MIN_N}
    folded = sorted(p for p in n if p not in keep)
    groups = {}
    for r in rows:
        g = r['publisher'] if r['publisher'] in keep else 'Other'
        groups.setdefault(g, []).append(r)
    groups['All publishers'] = rows
    tab = {}
    for g, rs in groups.items():
        c = Counter(r['cat'] for r in rs)
        tab[g] = {'n': len(rs), **{k: c.get(k, 0) for k, _, _ in CATS}, 'oa': sum(r['oa'] for r in rs)}
    return groups, tab, folded, dict(n)


def common_order(drawn: list) -> list:
    """One publisher order for every round: round-1 eligible count, then rows that only later rounds show, Other last."""
    order = []
    for rd in drawn:
        new = [g for g in rd['tab'] if g not in ('All publishers', 'Other') and g not in order]
        order += sorted(new, key=lambda g: (-rd['tab'][g]['n'], g))
    return ['All publishers'] + order + ['Other']


def main() -> None:
    queue = read_queue()
    queue_mtime = datetime.fromtimestamp(QUEUE.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
    inputs = [QUEUE]
    drawn = []
    for label, mf, metf in ROUNDS:
        need = [D / mf / 'manifest.jsonl', D / metf / 'metrics.json', D / mf / 'xml_status.json']
        if all(p.is_file() for p in need):
            rows, checks = load_round(mf, metf, queue)
            groups, tab, folded, raw = tabulate(rows)
            drawn.append({'label': label, 'rows': rows, 'groups': groups, 'tab': tab, 'folded': folded, 'raw': raw,
                          'checks': dict(checks)})
            inputs += need
    inputs.append(PDFS)
    order_all = common_order(drawn)
    for rd in drawn:
        rd['order'] = [g for g in order_all if g in rd['tab']]
    xml_only_total = sum(rd['tab']['All publishers']['xml'] for rd in drawn)
    cats_shown = [c for c in CATS if c[0] != 'xml' or xml_only_total > 0]

    nrows = [len(r['order']) for r in drawn]
    bar_h = 0.155  # inches per publisher row
    height = 0.3 + sum(n * bar_h + 0.5 for n in nrows)
    fig, _ = ps.figure(ps.DOUBLE, height)
    fig.clf()
    gs = GridSpec(len(drawn), 2, figure=fig, width_ratios=[5.0, 1.25], height_ratios=[n + 1.6 for n in nrows],
                  wspace=0.32, hspace=0.42)
    letters = iter('abcdefgh')
    numbers = {'rounds_drawn': [r['label'] for r in drawn], 'min_eligible_for_own_row': MIN_N,
               'categories': {k: lab for k, lab, _ in CATS}, 'categories_in_legend': [lab for _, lab, _ in cats_shown],
               'publisher_order': order_all, 'download_queue_mtime': queue_mtime}
    for i, rd in enumerate(drawn):
        order, tab = rd['order'], rd['tab']
        ax = fig.add_subplot(gs[i, 0])
        axo = fig.add_subplot(gs[i, 1], sharey=ax)
        y = {g: j + (0 if j == 0 else 0.6) for j, g in enumerate(order)}  # gap below the "All" row
        xml_only_labelled = False
        all_oa = all(tab[g]['oa'] == tab[g]['n'] for g in order)
        for g in order:
            t = tab[g]
            left = 0.0
            for k, _, col in CATS:
                w = t[k] / t['n'] if t['n'] else 0
                if w > 0:
                    ax.barh(y[g], w, left=left, height=0.72, color=col, edgecolor='white', linewidth=0.6)
                    if k == 'xml' and not xml_only_labelled:  # AQUA needs a direct label; fires only if XML only exists
                        # label in the gap under the "All publishers" row, clear of the legend
                        ax.annotate(f'XML only ({t[k]})', xy=(left + w / 2, y[g] + 0.36), xytext=(left + w / 2 + 0.03, y[g] + 0.8),
                                    fontsize=ps.SMALL, color=ps.INK2, ha='left', va='center',
                                    arrowprops=dict(arrowstyle='-', color=ps.INK2, lw=0.5, shrinkA=0, shrinkB=0))
                        xml_only_labelled = True
                left += w
            anyft = (t['both'] + t['pdf'] + t['xml'])
            ax.text(1.01, y[g], f"{anyft}/{t['n']}", va='center', ha='left', fontsize=ps.SMALL, color=ps.INK2,
                    transform=ax.get_yaxis_transform())
            share = t['oa'] / t['n'] if t['n'] else 0
            axo.plot([0, share], [y[g], y[g]], color=ps.GRID, lw=0.8, solid_capstyle='butt', zorder=1)
            axo.plot(share, y[g], 'o', ms=3.2, color=ps.INK, mec='white', mew=0.4, zorder=2, clip_on=False)
        labels = [f"{SHORT.get(g, g)}  ({tab[g]['n']})" for g in order]
        ax.set_yticks([y[g] for g in order], labels)
        ax.get_yticklabels()[0].set_fontweight('bold')
        ax.set_ylim(max(y.values()) + 0.6, -0.6)
        ax.tick_params(axis='y', length=0)
        ax.spines['left'].set_visible(False)
        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ['0', '0.25', '0.5', '0.75', '1'])
        ps.grid(ax, 'x')
        ax.set_xlabel(f"Share of eligible papers ({rd['label'].lower()}, n = {tab['All publishers']['n']})")
        ax.text(1.01, -0.75, FT_HEADER, ha='left', va='bottom', fontsize=ps.SMALL, color=ps.INK2,
                transform=ax.get_yaxis_transform())
        ps.panel(ax, next(letters), x=-0.30, y=1.0)
        if i == 0:
            handles = [Patch(facecolor=c, edgecolor='white', linewidth=0.6, label=lab) for _, lab, c in cats_shown]
            ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(0, 1.03), ncol=len(handles), handlelength=1.2,
                      columnspacing=1.4, borderaxespad=0)
        axo.set_xlim(0, 1.06)
        axo.set_xticks([0, 0.5, 1.0], ['0', '0.5', '1'])
        axo.tick_params(axis='y', left=False, labelleft=False)
        axo.spines['left'].set_visible(False)
        ps.grid(axo, 'x')
        axo.set_xlabel('Open-access share')
        ps.panel(axo, next(letters), x=-0.02, y=1.0)
        numbers.setdefault('all_open_access_by_design', {})[rd['label']] = all_oa
        rows = rd['rows']
        els = [r for r in rows if r['publisher'] == 'Elsevier']
        sn = [r for r in rows if r['publisher'] == 'Springer']
        numbers[rd['label']] = {
            'eligible': tab['All publishers']['n'],
            'by_publisher': {g: tab[g] for g in order},
            'folded_into_other': {p: rd['raw'][p] for p in rd['folded']},
            'raw_publisher_counts_after_relabelling': rd['raw'],
            'xml_route_of_xml_papers': dict(Counter(r['xml_route'] for r in rows if r['xml_route'])),
            'xml_format_by_publisher': {f: dict(Counter(r['publisher'] for r in rows if r['xml_format'] == f))
                                        for f in sorted({r['xml_format'] for r in rows if r['xml_format']})},
            'elsevier_n': len(els), 'elsevier_xml': sum(r['cat'] in ('both', 'xml') for r in els),
            'elsevier_http_403_without_xml': sum(r['elsevier_403'] for r in els),
            'elsevier_doi_prefixes': dict(Counter(r['prefix'] for r in els)),
            'springer_nature_n': len(sn),
            'springer_nature_pleiades': sum(r['prefix'] in PLEIADES_PREFIXES for r in sn),
            'checks': rd['checks'],
        }

    def nm(lbl):
        return numbers[lbl]

    letters_bar = ', '.join(chr(97 + 2 * i) for i in range(len(drawn)))
    letters_oa = ', '.join(chr(98 + 2 * i) for i in range(len(drawn)))
    parts = []
    for rd in drawn:
        t = rd['tab']['All publishers']
        parts.append(f"{rd['label']}, n = {t['n']}: {t['both']} PDF and XML, {t['pdf']} PDF only, {t['xml']} XML only, "
                     f"{t['none']} none; {t['oa']} open access")
    # XML sources, from the root element of each XML file drawn (xml_status 'route' says 'already present' on reruns)
    fmt_pub = {}
    for rd in drawn:
        for f, by in nm(rd['label'])['xml_format_by_publisher'].items():
            for pub, c in by.items():
                fmt_pub.setdefault(f, Counter())[pub] += c
    jats = [SHORT.get(p, p).split(' (')[0] for p, _ in sorted(fmt_pub.get('jats', {}).items(), key=lambda x: (-x[1], x[0]))]
    xml_txt = ('XML is publisher full-text XML with the article body: JATS (Journal Article Tag Suite, the standard XML for articles) for ' + ', '.join(jats[:-1])
               + (' and ' if len(jats) > 1 else '') + jats[-1] + ' papers') if jats else 'XML is publisher full-text XML'
    if fmt_pub.get('other'):
        xml_txt += f", other XML for {sum(fmt_pub['other'].values())} papers"
    els_xml = [(rd['label'], nm(rd['label'])['elsevier_xml'], nm(rd['label'])['elsevier_n']) for rd in drawn]
    if any(x for _, x, _ in els_xml):
        xml_txt += ', and Elsevier article XML from the Elsevier full-text API (' + ', '.join(
            f'{x} of {n} Elsevier papers in {lab.lower()}' for lab, x, n in els_xml) + ')'
    els_403 = [(rd['label'], nm(rd['label'])['elsevier_http_403_without_xml'], nm(rd['label'])['elsevier_n']) for rd in drawn]
    els_403 = [e for e in els_403 if e[1]]
    if els_403:
        xml_txt += ('; Elsevier full-text XML requests were refused (HTTP 403) for '
                    + ', '.join(f'{k} of {n} Elsevier papers in {lab.lower()}' for lab, k, n in els_403))
    xml_txt += '.'
    pleiades = ', '.join(f"{nm(rd['label'])['springer_nature_pleiades']} of {nm(rd['label'])['springer_nature_n']} papers in "
                         f"{rd['label'].lower()}" for rd in drawn)
    els_other = []
    for rd in drawn:
        pre = {p: c for p, c in nm(rd['label'])['elsevier_doi_prefixes'].items() if p != '10.1016'}
        if pre:
            els_other.append(' and '.join(f"{c} {PREFIX_NAMES.get(p, 'other')} ({p})" for p, c in sorted(pre.items(), key=lambda x: (-x[1], x[0])))
                             + f" DOI{'s' if sum(pre.values()) > 1 else ''} in {rd['label'].lower()}")
    other = '; '.join(f"{rd['label'].lower()}: " + ', '.join(f"{SHORT.get(p, p).split(' (')[0]} {c}"
                                                            for p, c in sorted(nm(rd['label'])['folded_into_other'].items(),
                                                                               key=lambda x: (-x[1], x[0])))
                      for rd in drawn if rd['folded'])
    agu_mismatch = sum(rd['checks'].get('agu_list_vs_prefix_10.1029_mismatch', 0) for rd in drawn)
    xml_only_txt = (f'XML only (0 papers in {"either round" if len(drawn) > 1 else "this round"}, so not drawn)'
                    if xml_only_total == 0 else 'XML only')
    caption = (
        'Full-text access by publisher for the eligible 2022 papers of '
        + (' and '.join(r['label'].lower() for r in drawn)) + '. '
        f'({letters_bar}) Each bar splits a publisher\'s eligible papers into PDF and XML, PDF only, {xml_only_txt}, and '
        f'no full text. {xml_txt} The number after the publisher name is its '
        f'eligible count; the fraction at the right ("{FT_HEADER.lower()}") counts papers with a PDF or XML. '
        f'({letters_oa}) Share of the same papers that OpenAlex lists as open access. '
        'Publisher is the OpenAlex host organization, not the DOI registrant, with two exceptions: papers whose journal '
        'is on the AGU journal list are shown as AGU (Wiley)'
        + (', which in these rounds are exactly the papers with DOI prefix 10.1029' if agu_mismatch == 0 else '')
        + ', and papers with DOI prefix 10.5194 (European Journal of Mineralogy, hosted by OpenAlex under Elsevier) are '
        'shown as Copernicus. GJI, SRL and BSSA are shown by journal; their publishers are given in parentheses. '
        f'Springer joins the two OpenAlex labels Springer and Springer Nature (Nature Portfolio is shown apart) and includes Pleiades translations of Russian journals (DOI prefixes 10.1134 and 10.3103; '
        f'{pleiades})'
        + (f"; the Elsevier host includes {', and '.join(els_other)}" if els_other else '') + '. '
        f'Publishers with fewer than {MIN_N} eligible papers in a round are pooled as Other ({other}). Rows keep the '
        'round-1 order in both rounds. PDF status from the download queue and XML status from the round\'s '
        f'xml_status.json, each confirmed on disk (queue as of {queue_mtime}). Counts are a census of each eligible set, '
        'so no sampling interval is drawn. ' + '. '.join(parts) + '.'
        + (' Round 2 was drawn from open-access papers only, with at most 4 papers per journal and a round robin over '
           'publishers (g18_round2_draw.py, seed 2027), so its publisher mix and its open-access share (1 for every '
           'publisher) are set by the design; its per-publisher shares are not a second sample of the round-1 population.'
           if numbers.get('all_open_access_by_design', {}).get('Round 2') else ''))
    r1 = numbers[drawn[0]['label']]['by_publisher']['All publishers']
    numbers['all_round1_any_fulltext_share'] = round((r1['both'] + r1['pdf'] + r1['xml']) / r1['n'], 3)
    ps.save(fig, 'fig02_fulltext', inputs=inputs, numbers=numbers, caption=caption)


if __name__ == '__main__':
    main()
