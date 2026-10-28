#!/usr/bin/env python3
"""Validate paper codings (codebook v1) and measure agreement between two codings of one paper.

  python3 tools/check_coding.py validate CODING.json [...]
  python3 tools/check_coding.py agree A.json B.json        two coders, same paper
  python3 tools/check_coding.py agree-dir DIR_A DIR_B      every key present in both folders

Validation implements the parts of JSON Schema the schema uses (type, enum, required,
additionalProperties, items) and adds the codebook's rules: every step has a page, quotes are at
most 25 words, steps are numbered 1..n. Agreement reports entry node, outcome, Jaccard overlap of
the node and mode sets, and sequence similarity (1 minus the normalized edit distance) of the
final-paper node and mode sequences, consecutive repeats merged.

Review codings under the review addendum (agents/coder/REVIEW_ADDENDUM.md, schema review_addendum.schema.json) add
`review_addendum_version` and `disclosures`. The two fields are optional for any coding and required when validate() is
called with review=True (tools/code_papers.py does so for requests with an open review record) or when the coding
declares review_addendum_version; review codings made before the addendum (E3, tag calc1-review) stay valid without
them. With texts (the open discussion, the author-responses document, the published paper's located text), each
disclosure's quotes are checked with the matching of tools/roadmap/g27_author_responses.py (normalised substring, or
the same ignoring spaces): the unit exists and is an author unit (AC or AR), the quote is in it and is not referee
text (>= 50% of its 8-word shingles in the RC, CC and EC paragraphs), the final quote is in the published paper.
Whether the final quote sits at final_loc is recorded by disclosure_checks() but is not a validation error.
Two rules for the quote checks (validate(checks=...)): 'strict' makes every failed check a validation error of the
coding; 'item' (DISCLOSURE_CHECKS, the rule of tools/code_papers.py and tools/roadmap/g34_reconstruction.py) leaves the
coding valid and drops the failing disclosures: kept_disclosures() returns the items that pass item_ok() (an author
unit; the quote in the cited unit or in another author unit of the same document, AC1 or AR2; not referee text; the
final quote, when checked, in the published paper) and the number dropped. On the 58 E3 review codings, 705 of 746
review-step quotes sit in the cited unit and 746 of 746 in the same document (October 28, 2026).
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'agents' / 'coder' / 'coding.schema.json').read_text())
ADDENDUM = json.loads((ROOT / 'agents' / 'coder' / 'review_addendum.schema.json').read_text())
# coding.schema.json is sent verbatim in every inquiry request, so the addendum's fields live in their own file and are
# merged here: optional in SCHEMA_ANY, required in SCHEMA_REVIEW
SCHEMA_ANY = {**SCHEMA, 'properties': {**SCHEMA['properties'], **ADDENDUM['properties']}}
SCHEMA_REVIEW = {**SCHEMA_ANY, 'required': SCHEMA['required'] + ADDENDUM['required']}
UNIT = r'\[((?:AC|AR|RC|CC|EC)\d+(?:-S)? (?:¶|p\.)\d+)\] (.*)'
TYPES = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool}
DISCLOSURE_CHECKS = 'item'   # 'strict' (a failed quote check invalidates the coding) or 'item' (the item is dropped)
ITEM_CHECKS = ('author_unit', 'quote_in_document', 'quote_not_referee', 'final_quote_in_paper')


NEW_IN = {'disagreements': '1.3.0', 'alternatives_considered': '1.3.0', 'v_checks': '1.5.0'}


def _older(v, than):
    try:
        return tuple(map(int, v.split('.'))) < tuple(map(int, than.split('.')))
    except Exception:  # noqa: BLE001
        return False


def check(node, schema, path, errs, version=None):
    t = schema.get('type')
    if t and not isinstance(node, TYPES[t]):
        errs.append(f'{path}: expected {t}'); return
    if 'enum' in schema and node not in schema['enum']:
        errs.append(f'{path}: {node!r} not in {schema["enum"]}')
    if t == 'object':
        for k in schema.get('required', []):
            if k not in node and not (path == '$' and k in NEW_IN and _older(version or '', NEW_IN[k])):
                errs.append(f'{path}: missing {k}')
        if schema.get('additionalProperties') is False:
            for k in node:
                if k not in schema['properties']:
                    errs.append(f'{path}: unexpected {k}')
        for k, sub in schema.get('properties', {}).items():
            if k in node:
                check(node[k], sub, f'{path}.{k}', errs)
    if t == 'array':
        for i, item in enumerate(node):
            check(item, schema['items'], f'{path}[{i}]', errs)


def validate(c: dict, review: bool = False, texts: dict | None = None, checks: str = 'strict') -> list[str]:
    """Errors of a coding. With texts and checks 'strict', every failed disclosure quote check is an error; with checks
    'item' the quote checks are left to kept_disclosures() (a failing disclosure is dropped, the coding stays valid)."""
    errs: list[str] = []
    check(c, SCHEMA_REVIEW if review or 'review_addendum_version' in c else SCHEMA_ANY, '$', errs, c.get('codebook_version'))
    for s in c.get('sequences', []):
        for i, st in enumerate(s.get('steps', []), 1):
            if st.get('n') != i:
                errs.append(f'{s.get("kind")} step {i}: numbered {st.get("n")}')
            if not str(st.get('page', '')).strip():
                errs.append(f'{s.get("kind")} step {i}: no page')
            if len(str(st.get('quote', '')).split()) > 25:
                errs.append(f'{s.get("kind")} step {i}: quote over 25 words')
    if not any(s.get('kind') == 'final_paper' for s in c.get('sequences', [])):
        errs.append('no final_paper sequence')
    if 'v_checks' in c:  # codebook 1.5.0, section 3a (NASEM 2019)
        here = [v for v in c['v_checks'] if v.get('performed_here') is True]
        has_v = any(st.get('node') == 'V' for s in c.get('sequences', []) if s.get('kind') == 'final_paper' for st in s.get('steps', []))
        if has_v and not here:
            errs.append('V steps in the final paper but no check performed here in v_checks (codebook 3a)')
        for i, v in enumerate(c['v_checks'], 1):
            if len(str(v.get('quote', '')).split()) > 25:
                errs.append(f'v_checks {i}: quote over 25 words')
            if not str(v.get('page', '')).strip():
                errs.append(f'v_checks {i}: no page')
    if isinstance(c.get('disclosures'), list):   # review addendum 1.0.0
        for i, d in enumerate(c['disclosures'], 1):
            if not isinstance(d, dict):
                continue
            for f in ('quote', 'content', 'final_quote'):
                if len(str(d.get(f, '')).split()) > 25:
                    errs.append(f'disclosures {i}: {f} over 25 words')
            st, fq = d.get('final_paper_status'), str(d.get('final_quote', '')).strip()
            if st in ('present', 'partly') and not d.get('removed') and not fq:
                errs.append(f'disclosures {i}: {st} without final_quote')
            if st == 'absent' and (fq or str(d.get('final_loc', '')).strip()):
                errs.append(f'disclosures {i}: absent with a final_quote or final_loc')
        if texts and checks == 'strict':
            for i, ch in enumerate(disclosure_checks(c, texts), 1):
                errs += [f'disclosures {i} ({ch["unit"]}): {k} failed' for k in ('unit_found', 'author_unit', 'quote_in_unit',
                         'quote_not_referee', 'final_quote_in_paper') if ch.get(k) is False]
    return errs


def review_units(*docs: str | None) -> dict[str, str]:
    """Locator -> text for every [ID ¶n] / [ID p.n] line of the open discussion and the author-responses document."""
    out: dict[str, str] = {}
    for doc in docs:
        for line in (doc or '').splitlines():
            m = re.match(UNIT, line)
            if m:
                out[m.group(1)] = (out.get(m.group(1), '') + ' ' + m.group(2)).strip()
    return out


def paper_paragraphs(text: str | None) -> dict[str, str]:
    """Locator -> text of the published paper's located XML text (tools/jats_text.py): [§3.2 ¶4], [Figure 3], [Table 2],
    and TITLE (the TITLE: line), as g27 reads it."""
    out: dict[str, str] = {}
    for line in (text or '').splitlines():
        m = re.match(r'\[([^\]]+)\] (.*)', line)
        if m:
            out[m.group(1)] = m.group(2)
        elif line.startswith('TITLE: '):
            out['TITLE'] = line[7:]
    return out


def disclosure_checks(c: dict, texts: dict) -> list[dict]:
    """Per-disclosure quote checks (g27's matching). texts: 'review' (discussion.txt), 'responses' (author-responses
    document or None), 'paper' (located text of the published paper, or None: final quotes are then not checked)."""
    sys.path.insert(0, str(ROOT / 'tools' / 'roadmap'))
    from g27_author_responses import contains, clean, norm, shingles, QUOTED
    units = review_units(texts.get('review'), texts.get('responses'))
    ref = shingles(norm(' '.join(t for u, t in units.items() if u[:2] in ('RC', 'CC', 'EC'))).split())
    paper, paras = texts.get('paper'), paper_paragraphs(texts.get('paper'))
    out = []
    for d in c.get('disclosures') or []:
        if not isinstance(d, dict):
            continue
        u, q = str(d.get('unit', '')).strip(), str(d.get('quote', ''))
        t = units.get(u)
        sh = shingles(norm(q).split())
        doc = u.split(' ')[0].split('-')[0]
        ch = {'unit': u, 'unit_found': t is not None, 'author_unit': u[:2] in ('AC', 'AR'),
              'quote_in_unit': t is not None and (contains(t, q) or contains(clean(t), q)),
              'quote_not_referee': not sh or len(sh & ref) / len(sh) < QUOTED}
        # the same document: another paragraph or page of the same author comment or AR file (AC1 ¶3 cited, AC1 ¶4 holds it)
        ch['quote_in_document'] = ch['quote_in_unit'] or (u[:2] in ('AC', 'AR') and bool(q.strip()) and any(
            contains(v, q) or contains(clean(v), q) for x, v in units.items() if x.split(' ')[0].split('-')[0] == doc))
        fq = str(d.get('final_quote', '')).strip()
        if fq and paper:
            ch['final_quote_in_paper'] = contains(paper, fq)
            ch['final_quote_at_loc'] = contains(paras.get(str(d.get('final_loc', '')).strip(), ''), fq)
        out.append(ch)
    return out


def item_ok(ch: dict) -> bool:
    """A disclosure kept under the 'item' rule: every check of ITEM_CHECKS passed (final_quote_in_paper only when checked)."""
    return all(ch.get(k) is not False for k in ITEM_CHECKS) and ch.get('author_unit') and ch.get('quote_in_document')


def kept_disclosures(c: dict, texts: dict) -> tuple[list[dict], int]:
    """(disclosures that pass item_ok(), number dropped) of a review coding, in the coding's order."""
    items = [d for d in c.get('disclosures') or [] if isinstance(d, dict)]
    chk = disclosure_checks(c, texts)
    kept = [d for d, ch in zip(items, chk) if item_ok(ch)]
    return kept, len(items) - len(kept)


def v_status(c: dict) -> dict:
    """NASEM V for a paper (codebook 1.5.0, section 3a): full, partial or none, and whether it triangulates."""
    here = [v['kind'] for v in c.get('v_checks', []) if v.get('performed_here') is True]
    mark = 'full' if any(k != 'reproduction' for k in here) else ('partial' if here else 'none')
    tri = len({k for k in here if k in ('replication', 'method', 'generalization')}) >= 2
    return {'v': mark, 'triangulation': tri, 'kinds': sorted(set(here))}


def runs(xs):
    out = []
    for x in xs:
        if not out or out[-1] != x:
            out.append(x)
    return out


def edit(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (x != y))
    return d[len(b)]


def seq(c, field):
    s = next(s for s in c['sequences'] if s['kind'] == 'final_paper')
    return runs([st[field] for st in s['steps']])


def jacc(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


def agree(a: dict, b: dict) -> dict:
    na, nb, ma, mb = seq(a, 'node'), seq(b, 'node'), seq(a, 'mode'), seq(b, 'mode')
    sim = lambda x, y: 1 - edit(x, y) / max(len(x), len(y), 1)
    return {'entry_node': a['entry']['node'] == b['entry']['node'], 'entry_state': a['entry']['state'] == b['entry']['state'],
            'outcome': a['end']['outcome'] == b['end']['outcome'], 'decisive_mode': a['decisive_move']['mode'] == b['decisive_move']['mode'],
            'node_set_jaccard': round(jacc(na, nb), 2), 'mode_set_jaccard': round(jacc(ma, mb), 2),
            'node_seq_similarity': round(sim(na, nb), 2), 'mode_seq_similarity': round(sim(ma, mb), 2),
            'steps': (len(na), len(nb))}


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__); return 2
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'validate':
        bad = 0
        for p in args:
            errs = validate(json.loads(Path(p).read_text()))
            print(f'{p}: {"ok" if not errs else str(len(errs)) + " problems"}')
            for e in errs[:20]:
                print('   ', e)
            bad += bool(errs)
        return 1 if bad else 0
    if cmd == 'agree':
        print(json.dumps(agree(*(json.loads(Path(p).read_text()) for p in args[:2])), indent=1)); return 0
    if cmd == 'agree-dir':
        A, B = Path(args[0]), Path(args[1]); rows = []
        for pa in sorted(A.glob('*.json')):
            pb = B / pa.name
            if pb.exists():
                r = agree(json.loads(pa.read_text()), json.loads(pb.read_text())); rows.append(r)
                print(pa.stem, json.dumps(r))
        if rows:
            mean = lambda k: round(sum(r[k] for r in rows) / len(rows), 2)
            print('mean', {k: mean(k) for k in ['entry_node', 'outcome', 'decisive_mode', 'node_set_jaccard', 'mode_set_jaccard', 'node_seq_similarity', 'mode_seq_similarity']})
        return 0
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main())
