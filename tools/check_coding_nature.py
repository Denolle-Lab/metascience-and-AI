#!/usr/bin/env python3
"""Validate review codings whose record is a Nature-family peer review file (agents/coder/REVIEW_ADDENDUM_NATURE.md
1.0.0, schema review_addendum_nature.schema.json), on top of tools/check_coding.py.

Why a separate file. tools/check_coding.py is a FROZEN file of the reconstruction plan (preregistration/
reconstruction.json); its test refuses to run when it changes. This module imports it and changes nothing in it, so
every Copernicus coding validates exactly as before.

validate_nature(c, texts=None, checks='strict')
  1. the two Nature fields (review_source 'nature_review_file', nature_addendum_version '1.0.0') are present and in
     their enums; they are removed from a copy of the coding;
  2. the copy is validated by check_coding.validate(copy, review=True): codebook schema, the review addendum 1.0.0
     fields (review_addendum_version required), step rules, disclosure word limits and final-status consistency;
  3. with texts and checks 'strict', every failed disclosure quote check (disclosure_checks below) is an error; with
     checks 'item' (check_coding.DISCLOSURE_CHECKS) the quote checks are left to kept_disclosures().
disclosure_checks(c, texts)   texts: 'review' (the unit document of g27_nature_units: [R<n>-round<k> ¶m], [E-round<k> ¶m],
  [A-round<k> ¶m] lines), 'paper' (located text of the published paper). The checks of check_coding.disclosure_checks
  with Nature units: unit_found; author_unit (an A unit); quote_in_unit; quote_in_document (in any A unit of the
  paper); quote_not_referee (< 50% of its 8-word shingles in the R and E units of the cited A unit's round or
  earlier, so an author sentence that a later referee quotes back stays the authors'; a quote cited to a unit that is
  not an A unit is compared with every R and E unit); final_quote_in_paper and
  final_quote_at_loc (recorded, not an error) when the paper text is given. Matching is g27's (normalised substring,
  or the same ignoring spaces).
kept_disclosures(c, texts)    (items passing check_coding.item_ok, number dropped), as check_coding's.
is_nature_coding(c)           the coding declares review_source 'nature_review_file'.

  python3 tools/check_coding_nature.py validate CODING.json [...]     (structure only; no texts)
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_coding  # noqa: E402

NATURE = json.loads((ROOT / 'agents' / 'coder' / 'review_addendum_nature.schema.json').read_text())
FIELDS = tuple(NATURE['required'])
UNIT = r'\[((?:R\d+|E|A)-round\d+ ¶\d+)\] (.*)'


def is_nature_coding(c: dict) -> bool:
    return isinstance(c, dict) and c.get('review_source') == 'nature_review_file'


def validate_nature(c: dict, texts: dict | None = None, checks: str = 'strict') -> list[str]:
    errs: list[str] = []
    for k in FIELDS:
        if k not in c:
            errs.append(f'$: missing {k}')
        elif c[k] not in NATURE['properties'][k]['enum']:
            errs.append(f'$.{k}: {c[k]!r} not in {NATURE["properties"][k]["enum"]}')
    base = {k: v for k, v in c.items() if k not in FIELDS}
    errs += check_coding.validate(base, review=True)
    if texts and checks == 'strict' and isinstance(c.get('disclosures'), list):
        for i, ch in enumerate(disclosure_checks(c, texts), 1):
            errs += [f'disclosures {i} ({ch["unit"]}): {k} failed' for k in ('unit_found', 'author_unit', 'quote_in_unit',
                     'quote_not_referee', 'final_quote_in_paper') if ch.get(k) is False]
    return errs


def units(doc: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (doc or '').splitlines():
        m = re.match(UNIT, line)
        if m:
            out[m.group(1)] = (out.get(m.group(1), '') + ' ' + m.group(2)).strip()
    return out


def disclosure_checks(c: dict, texts: dict) -> list[dict]:
    sys.path.insert(0, str(ROOT / 'tools' / 'roadmap'))
    from g27_author_responses import contains, clean, norm, shingles, QUOTED
    us = units(texts.get('review'))
    rnd = lambda u: int(m.group(1)) if (m := re.search(r'-round(\d+) ', u + ' ')) else None   # noqa: E731
    refs: dict = {}

    def ref_upto(k):   # shingles of the R and E units of round <= k (k None: every round)
        if k not in refs:
            refs[k] = shingles(norm(' '.join(t for x, t in us.items() if not x.startswith('A-')
                                             and (k is None or (rnd(x) or 0) <= k))).split())
        return refs[k]
    paper, paras = texts.get('paper'), check_coding.paper_paragraphs(texts.get('paper'))
    out = []
    for d in c.get('disclosures') or []:
        if not isinstance(d, dict):
            continue
        u, q = str(d.get('unit', '')).strip(), str(d.get('quote', ''))
        t = us.get(u)
        sh = shingles(norm(q).split())
        ch = {'unit': u, 'unit_found': t is not None, 'author_unit': u.startswith('A-'),
              'quote_in_unit': t is not None and (contains(t, q) or contains(clean(t), q)),
              'quote_not_referee': not sh or len(sh & ref_upto(rnd(u) if u.startswith('A-') else None)) / len(sh) < QUOTED}
        ch['quote_in_document'] = ch['quote_in_unit'] or (u.startswith('A-') and bool(q.strip()) and any(
            contains(v, q) or contains(clean(v), q) for x, v in us.items() if x.startswith('A-')))
        fq = str(d.get('final_quote', '')).strip()
        if fq and paper:
            ch['final_quote_in_paper'] = contains(paper, fq)
            ch['final_quote_at_loc'] = contains(paras.get(str(d.get('final_loc', '')).strip(), ''), fq)
        out.append(ch)
    return out


def kept_disclosures(c: dict, texts: dict) -> tuple[list[dict], int]:
    items = [d for d in c.get('disclosures') or [] if isinstance(d, dict)]
    kept = [d for d, ch in zip(items, disclosure_checks(c, texts)) if check_coding.item_ok(ch)]
    return kept, len(items) - len(kept)


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] != 'validate':
        print(__doc__)
        return 2
    bad = 0
    for p in sys.argv[2:]:
        errs = validate_nature(json.loads(Path(p).read_text()))
        print(f'{p}: {"ok" if not errs else str(len(errs)) + " problems"}')
        for e in errs[:20]:
            print('   ', e)
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
