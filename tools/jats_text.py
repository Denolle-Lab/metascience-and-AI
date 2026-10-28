#!/usr/bin/env python3
"""Turn publisher full-text XML (JATS, or Elsevier's full-text format) into plain text with locators.

The first lines give the DOI and the title. Every paragraph is prefixed with a locator a coder can cite instead of a page (codebook v1.4.0):
  [§0 ¶2]          abstract, second paragraph
  [§3.2 ¶4]        section 3.2, fourth paragraph (section numbers from the article's labels, else by position)
  [Fig. 3]         figure caption        [Table 2]   table caption        [§A1 ¶1]  appendix
Section headings are written as their own lines ('§3.2 Title'). Formulas are kept as TeX when the XML carries it,
otherwise as the MathML text. Elements are matched by local name, so namespaces and both formats work.

convert(root) with no options is the text stored as <key>.xml.txt and sent to the inquiry and readiness coders; it
must stay byte-identical. Two options, used only by tools/blind_text.py (BLIND_VERSION 1.2.0, October 28, 2026):
  descend_sections  Elsevier full text puts its sections inside ja:body/ce:sections; without this option the body
                    loop sees only 'sections' and drops the whole body (101 of the 581 blinded texts at v1.1.1)
  table_rows        print every table row after its caption as '[Table n] cell | cell | ...' (JATS tr/td/th and
                    CALS row/entry), so table contents reach the coder as they do on the pdftotext route
  availability      print the data and code availability statements kept outside the body (JATS back sec
                    sec-type="data-availability", Copernicus notes notes-type="dataavailability" / "codeavailability" /
                    "codedataavailability", Elsevier ce:data-availability, or a back section titled '... availability'
                    or 'Open Research') as sections §D1, §D2, ..., after the appendices; the pdftotext route prints them
                    as part of the page text (BLIND_VERSION 1.2.1: 210 of the 318 XML-route texts had lost one)

Usage: python3 tools/jats_text.py FILE.xml [OUT.txt]      (prints to stdout without OUT)
"""
from __future__ import annotations
import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SEC = {'sec', 'section'}
PARA = {'p', 'para', 'simple-para'}
TITLE = {'title', 'section-title'}
FIG = {'fig', 'figure'}
TAB = {'table-wrap', 'table'}
SKIP_INLINE = {'xref-group'}


def local(tag) -> str:
    return tag.rsplit('}', 1)[-1] if isinstance(tag, str) else ''


def parse(path: Path) -> ET.Element:
    raw = path.read_bytes().decode('utf-8', 'replace')
    raw = re.sub(r'<!DOCTYPE[^>\[]*(\[[^\]]*\])?>', '', raw, count=1)
    # named HTML entities that the DTD would have defined; XML's own five are left alone
    raw = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)([A-Za-z][A-Za-z0-9]*);',
                 lambda m: html.unescape(m.group(0)) if html.unescape(m.group(0)) != m.group(0) else ' ', raw)
    return ET.fromstring(raw)


def text_of(el: ET.Element) -> str:
    out = []

    def walk(e):
        n = local(e.tag)
        if n in ('inline-formula', 'disp-formula', 'formula'):
            tex = next((x for x in e.iter() if local(x.tag) == 'tex-math'), None)
            out.append(' ' + (tex.text or '').strip() + ' ' if tex is not None and tex.text else ' ' + ' '.join(t.strip() for t in e.itertext() if t.strip()) + ' ')
            if e.tail:
                out.append(e.tail)
            return
        if n in FIG | TAB | SEC:  # nested floats and sections are emitted separately
            if e.tail:
                out.append(e.tail)
            return
        if e.text:
            out.append(e.text)
        for c in e:
            walk(c)
        if e.tail:
            out.append(e.tail)
    if el.text:
        out.append(el.text)
    for c in el:
        walk(c)
    return re.sub(r'\s+', ' ', ''.join(out)).strip()


def child(el: ET.Element, names: set) -> ET.Element | None:
    return next((c for c in el if local(c.tag) in names), None)


def _rows(tab: ET.Element) -> list[str]:
    """Table rows as 'cell | cell' strings (JATS tr/td/th, CALS/Elsevier row/entry); empty rows dropped."""
    out = []
    for r in (e for e in tab.iter() if local(e.tag) in ('tr', 'row')):
        cells = [text_of(c) for c in r if local(c.tag) in ('td', 'th', 'entry')]
        if any(cells):
            out.append(' | '.join(cells))
    return out


AV_TYPES = {'data-availability', 'dataavailability', 'codeavailability', 'codedataavailability', 'data-and-code-availability'}
AV_TITLE = re.compile(r'^\s*(?:\d+(?:\.\d+)*\.?\s*)?(?:(?:(?:code|data|software)(?:\s*(?:,|and|&|/)\s*)?)+\s*availability'
                      r'(?:\s+statement)?|availability of (?:data|code|software)\b.*|open research|data access(?:ibility)?'
                      r'(?:\s+statement)?|data statement)\s*[.:]?\s*$', re.I)


def _availability(root: ET.Element, inside: set) -> list[ET.Element]:
    """Availability statements outside the already-emitted subtrees (`inside`: ids), outermost only, in document order."""
    found = []
    for e in root.iter():
        n = local(e.tag)
        if id(e) in inside or n not in SEC | {'notes', 'data-availability'}:
            continue
        ttl = child(e, TITLE)
        if (n == 'data-availability' or (e.get('sec-type') or e.get('notes-type') or '').lower() in AV_TYPES
                or (ttl is not None and AV_TITLE.match(text_of(ttl)))):
            found.append(e)
    nested = {id(x) for e in found for x in e.iter() if x is not e}
    return [e for e in found if id(e) not in nested]


def convert(root: ET.Element, descend_sections: bool = False, table_rows: bool = False, availability: bool = False) -> str:
    lines = []
    doi = next(((e.text or '').strip() for e in root.iter() if (local(e.tag) == 'article-id' and e.get('pub-id-type') == 'doi')
                or local(e.tag) == 'doi'), '')
    if doi:
        lines.append('DOI: ' + doi.replace('https://doi.org/', ''))
    title = next((e for e in root.iter() if local(e.tag) in ('article-title', 'title') and e is not None), None)
    if title is not None:
        lines.append('TITLE: ' + text_of(title))
    for ab in [e for e in root.iter() if local(e.tag) == 'abstract'][:1]:
        lines.append('§0 Abstract')
        paras = [e for e in ab.iter() if local(e.tag) in PARA]
        for k, p in enumerate(paras or [ab], 1):
            t = text_of(p)
            if t:
                lines.append(f'[§0 ¶{k}] {t}')
    body = next((e for e in root.iter() if local(e.tag) in ('body', 'sections')), None)
    figs = []

    def do_sec(sec, num, use_label=True):
        lab = child(sec, {'label'}) if use_label else None
        ttl = child(sec, TITLE)
        n = (text_of(lab).rstrip('.') if lab is not None and text_of(lab) else num)
        lines.append(f'§{n} ' + (text_of(ttl) if ttl is not None else ''))
        k, sub = 0, 0
        for c in sec:
            nm = local(c.tag)
            if nm in PARA:
                t = text_of(c)
                if t:
                    k += 1
                    lines.append(f'[§{n} ¶{k}] {t}')
                figs.extend(e for e in c.iter() if local(e.tag) in FIG | TAB)
            elif nm in SEC:
                sub += 1
                do_sec(c, f'{n}.{sub}')
            elif nm in FIG | TAB:
                figs.append(c)
            elif nm in ('list', 'disp-quote', 'boxed-text'):
                for p in [e for e in c.iter() if local(e.tag) in PARA]:
                    t = text_of(p)
                    if t:
                        k += 1
                        lines.append(f'[§{n} ¶{k}] {t}')
    if body is not None:
        kids = list(body)
        if descend_sections:   # Elsevier: ja:body > ce:sections > ce:section
            kids = [x for c in kids for x in (list(c) if local(c.tag) == 'sections' else [c])]
        top = [c for c in kids if local(c.tag) in SEC]
        loose = [c for c in kids if local(c.tag) in PARA]
        for k, p in enumerate(loose, 1):
            t = text_of(p)
            if t:
                lines.append(f'[§body ¶{k}] {t}')
        for i, s in enumerate(top, 1):
            do_sec(s, str(i))
    apps = [e for e in root.iter() if local(e.tag) in ('app', 'appendix')]
    for app in apps:
        lab = child(app, {'label'})
        do_sec(app, 'A' + (text_of(lab).replace('Appendix', '').strip() if lab is not None else '1'))
    if availability:
        inside = {id(x) for top_el in ([body] if body is not None else []) + apps for x in top_el.iter()}
        for i, s in enumerate(_availability(root, inside), 1):
            do_sec(s, f'D{i}', use_label=False)
    seen = set()
    for f in figs + [e for e in root.iter() if local(e.tag) in FIG | TAB]:
        if id(f) in seen:
            continue
        seen.add(id(f))
        lab = child(f, {'label'})
        cap = child(f, {'caption'})
        if cap is None:
            continue
        name = text_of(lab) if lab is not None else ('Figure' if local(f.tag) in FIG else 'Table')
        lines.append(f'[{name.rstrip(".")}] {text_of(cap)}')
        if table_rows and local(f.tag) in TAB:
            for e in f.iter():
                seen.add(id(e))      # a JATS table-wrap holds a caption-less table: print its rows once
            lines.extend(f'[{name.rstrip(".")}] {r}' for r in _rows(f))
    return '\n'.join(lines) + '\n'


def full_text_ok(root: ET.Element, min_paras: int = 15) -> bool:
    """True when the XML carries the body of the article, not only metadata and an abstract."""
    body = next((e for e in root.iter() if local(e.tag) in ('body', 'sections')), None)
    return body is not None and sum(1 for e in body.iter() if local(e.tag) in PARA) >= min_paras


def main() -> None:
    root = parse(Path(sys.argv[1]))
    out = convert(root)
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(out)
    else:
        sys.stdout.write(out)


if __name__ == '__main__':
    main()
