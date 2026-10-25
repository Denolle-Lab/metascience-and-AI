#!/usr/bin/env python3
"""Turn publisher full-text XML (JATS, or Elsevier's full-text format) into plain text with locators.

Every paragraph is prefixed with a locator a coder can cite instead of a page (codebook v1.4.0):
  [§0 ¶2]          abstract, second paragraph
  [§3.2 ¶4]        section 3.2, fourth paragraph (section numbers from the article's labels, else by position)
  [Fig. 3]         figure caption        [Table 2]   table caption        [§A1 ¶1]  appendix
Section headings are written as their own lines ('§3.2 Title'). Formulas are kept as TeX when the XML carries it,
otherwise as the MathML text. Elements are matched by local name, so namespaces and both formats work.

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


def convert(root: ET.Element) -> str:
    lines = []
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

    def do_sec(sec, num):
        lab = child(sec, {'label'})
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
        top = [c for c in body if local(c.tag) in SEC]
        loose = [c for c in body if local(c.tag) in PARA]
        for k, p in enumerate(loose, 1):
            t = text_of(p)
            if t:
                lines.append(f'[§body ¶{k}] {t}')
        for i, s in enumerate(top, 1):
            do_sec(s, str(i))
    for app in [e for e in root.iter() if local(e.tag) in ('app', 'appendix')]:
        lab = child(app, {'label'})
        do_sec(app, 'A' + (text_of(lab).replace('Appendix', '').strip() if lab is not None else '1'))
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
