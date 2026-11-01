#!/usr/bin/env python3
"""Validate advance codings (agents/advance/RUBRIC.md v1.1.0, schema agents/advance/advance.schema.json; codings made
under v1.0.1 are checked against agents/advance/archive/advance.schema.1.0.1.json).

  python tools/check_advance.py CODING.json [...]        errors and warnings per file; exit 1 if any file has errors
  python tools/check_advance.py --normalize CODING.json  also print what normalize() would change (the file is not written)

A saved coding is the model's JSON plus objects added by tools/code_papers.py after validation: `human_blocks` (the
ratings.schema.json field names, assemble_human(); RUBRIC.md section 12), `run` (model that answered, opaque key,
blinded-text sha256 and version, attempt) and `_normalized` (what normalize() changed). They are stripped before the
schema check; human_blocks must equal assemble_human() of the coding.

v1.1.0 (October 28, 2026; diagnosis of advance pilot 1): hard failures are only (1) the schema core, after
normalization (types, required fields, enums, gain ids G1..Gn in order); (2) fabricated quotes, two or more quotes not
found in the blinded text; (3) a verdict that contradicts its score, its unassessable condition or the criteria. All
other rules are warnings. Pilot 1 lost 20 of 40 codings to rules that are now warnings or normalizations.

normalize()  applied by code_papers.write_advance before validation, each change recorded in `_normalized`
  extra       a property the schema does not define: dropped when empty, else moved to `notes` (pilot 1: 8 codings
              failed on an empty precedent_search.*_note)
  enum        a near-miss enum value (case, spaces or hyphens) set to the enum value
  basis       verdict_basis set to a gain meeting every criterion when it names one that does not (achieved; the model's choice among such gains is kept), G1 (not_demonstrated) or none
              (unassessable); the verdict itself is never changed
Checks
  schema     JSON Schema draft 2020-12 (jsonschema); maxItems, minItems (except candidate_gains) and the id patterns
             are budgets: warnings
  version    rubric_version is a known version; validate() (the collection path) needs the current RUBRIC.md version
  quotes     every quote (in `quotes` and in each gain's `checks`) found in the blinded text the coder read (the cache,
             or private/data/roadmap/blind/archive/<version>/ when run.blind_sha256 names an earlier text). Matching
             ignores case, whitespace, punctuation, quote and dash styles; '...' splits a quote into parts that must
             appear in order; a quote that still fails is accepted when 90% of its word 4-grams occur in the text. One
             unmatched quote is a warning; two or more are an error. Length counts only tokens with a letter or digit
             (in 'm s - 1' the dash does not count): warning above 30.
  locators   the nearest preceding marker ([p. N], [§n ¶k], [Fig. n], [Table n], [Ref n]) agrees with the cited locator;
             mismatches are warnings
  rhetoric   at least one evidence and one verdict quote outside the abstract, key points, summary, title and
             conclusions, one of them stating a result (warnings)
  coverage   quotes support headline_claim, starting_state, gain (any quote with a gain_id counts), evidence, verdict;
             novelty when a closest precedent is named; overreach when the claim exceeds the warrant (warnings);
             quote budget (x-quote-budget in the schema) and word budgets (x-max-words) are warnings
  gains      headline components first, at most MAX_GAINS per rubric version; out_of_taxonomy if and only if none_fits;
             rival_test not_applicable if and only if not understanding; any criterion may be not_applicable when the
             verdict is unassessable, else only W3 and only for a capability gain; W3 met needs a check that addresses
             the principal threat; magnitude_form is authoritative and a 'Not quantifiable ...:' prefix that disagrees
             with it is a warning (all warnings)
  verdict    errors: achieved needs no unassessable condition, a gain meeting every criterion and score 2 to 5;
             not_demonstrated needs no condition, no gain meeting every criterion and score 1; unassessable needs a
             condition U1-U5 and score null. Warnings: eligible_in_my_view no without U4; basis on a gain stated only in
             a figure or supplement
  novelty    limits names a work (author and year) whose surname and year are absent from the reference list while
             uncited_precedent_known is false (warning; pilot 1's three cases were all in the paper's references)
"""
from __future__ import annotations
import json
import re
from collections import Counter
import sys
import unicodedata
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import blind_text  # noqa: E402

SCHEMA_PATH = ROOT / 'agents' / 'advance' / 'advance.schema.json'
RUBRIC_PATH = ROOT / 'agents' / 'advance' / 'RUBRIC.md'
SCHEMAS = {'1.1.0': SCHEMA_PATH, '1.0.1': ROOT / 'agents' / 'advance' / 'archive' / 'advance.schema.1.0.1.json'}
MAX_GAINS = {'1.0.1': 5, '1.1.0': 2}
MAX_QUOTE_WORDS = 30          # counted words (tokens with a letter or digit); the rubric asks for at most 25
REQUIRED_SUPPORT = ('headline_claim', 'starting_state', 'gain', 'evidence', 'verdict')
DERIVED = ('human_blocks', 'run', '_normalized')
CRIT = ('M1', 'M2', 'W1', 'W2', 'W3', 'W4')
NQ_CLASSES = {'qualitative discrimination between rivals': 'not_quantifiable_qualitative_discrimination',
              'first observation with no prior value': 'not_quantifiable_first_observation',
              'feasibility demonstration': 'not_quantifiable_feasibility',
              'descriptive or taxonomic': 'not_quantifiable_descriptive'}
MARK = re.compile(r'\[(p\. ?\d+|§[^\s\]]+ ¶\d+|Fig\. [^\]]+|Table [^\]]+|Ref \d+)\]')
CONC = re.compile(r'^(?:[\dA-Z]{1,2}(?:\.\d+)*\.?\s*)?(conclusions?|concluding remarks|summary(?: and (?:conclusions?|outlook|discussion))?|'
                  r'conclusions? and (?:outlook|perspectives?|implications|future work)|outlook|key points|plain language summary)\b', re.I)
NEXT_HEAD = re.compile(r'^\s*(?:\d{1,2}(?:\.\d+)*\.?\s+[A-Z]|acknowledg|references\b|appendix|data availability|open research|'
                       r'code availability|supplementary|author contributions|competing|declaration)', re.I)
RESULT = re.compile(r'\d|\b(?:increas|decreas|higher|lower|larger|smaller|reduc|improv|exceed|outperform|consistent|agree|match|differ|'
                    r'reject|fail|correlat|significant|shift|earlier|later|faster|slower|deeper|shallower|warmer|colder|wetter|drier|'
                    r'lead|lag|misfit|bias|within|resolv|detect|confirm|reproduc|recover)\w*', re.I)
WORK = re.compile(r'\b[A-Z][\wÀ-ɏ\'-]+(?:\s+et al\.?,?|\s+(?:and|&)\s+[A-Z][\w\'-]+,?|,)\s*\(?(?:19|20)\d\d[a-z]?\b'
                  r'|\b[A-Z][\wÀ-ɏ\'-]+(?:\s+et al\.?)?\s+\((?:19|20)\d\d[a-z]?\)')
MAG_NUM = re.compile(r'\d[\d.,]*\s*(?:%|‰|°|[A-Za-zµ])')
NQ_PREFIX = re.compile(r'^\s*not\s+quantifiable\b[^:]{0,60}:\s*(.*)', re.I | re.S)
_VALIDATORS: dict = {}


def rubric_version() -> str:
    for line in RUBRIC_PATH.read_text().splitlines():
        if line.startswith('version:'):
            return line.split(':', 1)[1].strip()
    return 'unknown'


def schema_for(version: str | None) -> dict | None:
    p = SCHEMAS.get(version or '')
    return json.loads(p.read_text()) if p and p.is_file() else None


def _validator(version: str | None = None):
    version = version or rubric_version()
    if version not in _VALIDATORS:
        sch = schema_for(version)
        _VALIDATORS[version] = jsonschema.Draft202012Validator(sch) if sch else None
    return _VALIDATORS[version]


def _sub(sch: dict | None, path: list) -> dict | None:
    """The subschema at a data path (object keys and array indices); used to accept, as a warning, an enum value that an
    older coding lacks but the current schema allows (dependency kind 'concept', added in v1.1.0)."""
    for k in path:
        if not isinstance(sch, dict):
            return None
        sch = sch.get('items') if isinstance(k, int) else (sch.get('properties') or {}).get(k)
    return sch


def words(s: str) -> int:
    """Counted words: whitespace tokens with a letter or digit ('m s - 1' counts 3, 'M ( 2 , 3 )' counts 3)."""
    return sum(bool(re.search(r'[0-9A-Za-zÀ-ɏͰ-Ͽ]', t)) for t in s.split())


# --------------------------------------------------------------------------------------------- text and positions
_KEEP = re.compile(r'[0-9a-zÀ-ɏͰ-Ͽ]')


def norm_map(s: str) -> tuple[str, list[int]]:
    """Normalized text (NFKC per character, lower case, letters and digits only) and, for each kept character, its
    index in s. Hyphens, spaces and line breaks drop out, so line-break hyphenation needs no special case."""
    out, idx = [], []
    for i, c in enumerate(s):
        for x in unicodedata.normalize('NFKC', c).lower():
            if _KEEP.match(x):
                out.append(x); idx.append(i)
    return ''.join(out), idx


def _norm(s: str) -> str:
    return norm_map(s)[0]


class Text:
    """The blinded text with normalized form, marker positions and restating ('rhetoric') spans."""

    def __init__(self, raw: str):
        self.raw = raw
        self.norm, self.idx = norm_map(raw)
        self.marks = [(m.start(), _parse_loc(m.group(1))) for m in MARK.finditer(raw)]
        self.xml = raw.startswith('Locators: [§')
        self.rhet = self._rhetoric()

    def _rhetoric(self) -> list[tuple[int, int]]:
        spans, pos, lines = [], 0, []
        for ln in self.raw.splitlines(keepends=True):
            lines.append((pos, ln)); pos += len(ln)
        for p, ln in lines:
            if ln.startswith('TITLE:'):
                spans.append((p, p + len(ln)))
        if self.xml:
            conc, cur = set(), None
            for p, ln in lines:
                m = re.match(r'^§(\S+) ?(.*)$', ln)
                if m:
                    if CONC.match(m.group(2).strip()):
                        conc.add(m.group(1))
                    continue
                m = re.match(r'^\[§(\S+) ¶\d+\]', ln)
                if m:
                    sec = m.group(1)
                    if sec == '0' or any(sec == c or sec.startswith(c + '.') for c in conc):
                        spans.append((p, p + len(ln)))
            return spans
        # PDF route: front matter up to the Introduction heading (within the first 40% of the text)
        intro = next((p for p, ln in lines if p < 0.4 * len(self.raw) and
                      re.sub(r'[\s.]', '', ln).lower() in ('introduction', '1introduction', 'iintroduction')), None)
        if intro is not None:
            spans.append((0, intro))
        else:
            a = next((p for p, ln in lines if re.match(r'^\s*abstract\b', ln, re.I)), None)
            if a is not None:
                spans.append((a, a + 1500))
        start = None
        for p, ln in lines:
            t = ln.strip()
            if start is None:
                if t and len(t) < 60 and CONC.match(re.sub(r'(?<=\b\w) (?=\w\b)', '', t)):
                    start = p
            elif t and len(t) < 80 and NEXT_HEAD.match(t):
                spans.append((start, p)); start = None
        if start is not None:
            ref = self.raw.find('\nReferences\n', start)
            spans.append((start, ref if ref > 0 else len(self.raw)))
        return spans

    def in_rhet(self, pos: int) -> bool:
        return any(a <= pos < b for a, b in self.rhet)

    def marker_before(self, pos: int):
        best = None
        for p, loc in self.marks:
            if p > pos:
                break
            best = loc
        return best

    def find(self, q: str) -> tuple[bool, list[tuple[int, int]]]:
        """(found, [(raw start, raw end) of each exact occurrence]); found by 4-gram fallback gives no positions."""
        parts = [_norm(p) for p in re.split(r'\.\.\.|…|\[\.\.\.\]', q)]
        parts = [p for p in parts if p]
        if not parts:
            return False, []
        occ, i = [], self.norm.find(parts[0])
        while i >= 0:
            pos, ok = i + len(parts[0]), True
            for p in parts[1:]:
                j = self.norm.find(p, pos)
                if j < 0:
                    ok = False; break
                pos = j + len(p)
            if ok:
                occ.append((self.idx[i], self.idx[pos - 1]))
            i = self.norm.find(parts[0], i + 1)
        if occ:
            return True, occ
        w = [_norm(x) for x in q.split() if _norm(x)]
        grams = [''.join(w[k:k + 4]) for k in range(max(0, len(w) - 3))]
        return bool(grams) and sum(g in self.norm for g in grams) >= 0.9 * len(grams), []


def _parse_loc(s: str) -> list[tuple]:
    out = []
    for m in re.finditer(r'§\s*([\w.]+)\s*¶\s*(\d+)', s):
        out.append(('sec', m.group(1).rstrip('.'), int(m.group(2))))
    if not out:
        for m in re.finditer(r'§\s*([\w.]+)', s):
            out.append(('sec', m.group(1).rstrip('.'), None))
    for m in re.finditer(r'\bpp?\.?\s*(\d+)', s):
        out.append(('p', int(m.group(1))))
    for m in re.finditer(r'\bFig(?:ure)?s?\.?\s*(\w+)', s):
        out.append(('fig', m.group(1).lower()))
    for m in re.finditer(r'\bTables?\s*(\w+)', s):
        out.append(('tab', m.group(1).lower()))
    for m in re.finditer(r'\bRefs?\.?\s*(\d+)', s):
        out.append(('ref', int(m.group(1))))
    return out


def _loc_agrees(cited: list[tuple], marker: list[tuple] | None) -> bool:
    if not marker:
        return False
    for c in cited:
        for m in marker:
            if c[0] != m[0]:
                continue
            if c[0] == 'sec':
                if c[1] == m[1] and (c[2] is None or m[2] is None or c[2] == m[2]):
                    return True
            elif c[1:] == m[1:]:
                return True
    return False


def locate(T: Text, quote: str, locator: str) -> dict:
    """{'found', 'positions', 'locator': 'ok' | 'mismatch' | 'unparsed' | 'unknown', 'rhetoric': bool | None}"""
    found, occ = T.find(quote)
    r = {'found': found, 'positions': occ, 'locator': 'unknown', 'rhetoric': None}
    if not occ:
        return r
    cited = _parse_loc(locator)
    if not cited or all(T.marker_before(o[0]) is None for o in occ):   # no locator, or text before the first marker (title)
        r['locator'] = 'unparsed'
    else:
        good = [o for o in occ if _loc_agrees(cited, T.marker_before(o[0])) or _loc_agrees(cited, T.marker_before(o[1]))]
        r['locator'] = 'ok' if good else 'mismatch'
        occ = good or occ
    r['rhetoric'] = all(T.in_rhet(o[0]) for o in occ)
    return r


# --------------------------------------------------------------------------------------------- human-compatible blocks
def basis_gain(d: dict) -> dict:
    g = {x['id']: x for x in d['candidate_gains']}
    return g.get(d['verdict_basis']) or d['candidate_gains'][0]


def assemble_human(d: dict) -> dict:
    """The ratings.schema.json v1.0.0 blocks for comparison with human raters (RUBRIC.md section 12). advance.score is
    null for unassessable codings: compare it as missing."""
    g, s, c, p = basis_gain(d), d['starting_state_as_stated'], d['starting_state_coder_2021'], d['precedent_search']
    return {'eligible_in_my_view': d['eligible_in_my_view'], 'familiarity': d['familiarity'],
            'novelty': {'atomic_claim': p['atomic_claim'], 'claim_kind': p['claim_kind'], 'closest_precedent': p['closest_precedent'],
                        'new_component': p['new_component'], 'judgment': p['judgment_with_coder_knowledge'],
                        'score': d['novelty_score'], 'confidence': d['novelty_confidence']},
            'advance': {'starting_state': f"{s['text']} Coder's account (frame about 2021; {c['agreement']} with the stated gap): {c['text']}",
                        'gain': g['gain'], 'magnitude': g['magnitude'], 'evidence': g['evidence'], 'roles': d['roles'],
                        'score': d['advance_score'], 'confidence': d['advance_confidence']},
            'impact_forecast': d['impact_forecast']}


def model_part(d: dict) -> dict:
    return {k: v for k, v in d.items() if k not in DERIVED}


# --------------------------------------------------------------------------------------------- normalization
def _empty(v) -> bool:
    return v is None or v == '' or v == [] or v == {} or (isinstance(v, str) and not v.strip())


def _walk(node, sch: dict, path: str, out: list, notes: list):
    """Normalize node in place against sch: extra properties and near-miss enum values."""
    if not isinstance(sch, dict):
        return node
    if 'enum' in sch and isinstance(node, str) and node not in sch['enum']:
        cand = re.sub(r'[\s-]+', '_', node.strip().lower())
        if cand in sch['enum']:
            out.append({'rule': 'enum', 'path': path.lstrip('/'), 'from': node, 'to': cand})
            return cand
    if isinstance(node, dict) and 'properties' in sch:
        if sch.get('additionalProperties') is False:
            for k in [k for k in node if k not in sch['properties']]:
                v = node.pop(k)
                if _empty(v):
                    out.append({'rule': 'extra', 'path': f'{path}/{k}'.lstrip('/'), 'action': 'dropped (empty)'})
                else:
                    notes.append((f'{path}/{k}'.lstrip('/'), v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)))
                    out.append({'rule': 'extra', 'path': f'{path}/{k}'.lstrip('/'), 'action': 'moved to notes'})
        for k, sub in sch['properties'].items():
            if k in node:
                node[k] = _walk(node[k], sub, f'{path}/{k}', out, notes)
    elif isinstance(node, list) and isinstance(sch.get('items'), dict):
        for i, x in enumerate(node):
            node[i] = _walk(x, sch['items'], f'{path}/{i}', out, notes)
    return node


def full_gains(d: dict) -> list[str]:
    return [g['id'] for g in d.get('candidate_gains') or [] if isinstance(g, dict) and isinstance(g.get('criteria'), dict) and
            all(g['criteria'].get(k) == 'met' or (k == 'W3' and g['criteria'].get(k) == 'not_applicable') for k in CRIT)]


def normalize(d: dict) -> tuple[dict, list[dict]]:
    """(normalized copy, list of changes) by the rules in the module docstring. Model content is never rewritten
    beyond them; the verdict, the criteria and the score are never changed."""
    d = json.loads(json.dumps(model_part(d)))
    out, notes = [], []
    sch = schema_for(d.get('rubric_version')) or schema_for(rubric_version())
    _walk(d, sch, '', out, notes)
    if notes:
        if isinstance(sch['properties'].get('notes', {}).get('items'), dict):      # v1.1.0: list of {field, note}
            d.setdefault('notes', [])
            if isinstance(d['notes'], list):
                d['notes'] += [{'field': p, 'note': v} for p, v in notes]
        else:                                                                   # v1.0.1: one string
            d['notes'] = ((d.get('notes') or '') + ' ' + ' '.join(f'[{p}] {v}' for p, v in notes)).strip()
    v, ids = d.get('verdict'), [g.get('id') for g in d.get('candidate_gains') or [] if isinstance(g, dict)]
    full = full_gains(d)
    want = {'achieved': d.get('verdict_basis') if d.get('verdict_basis') in full else (full or [None])[0],
            'not_demonstrated': 'G1', 'unassessable': 'none'}.get(v)
    if want and d.get('verdict_basis') != want and (want == 'none' or want in ids):
        out.append({'rule': 'basis', 'path': 'verdict_basis', 'from': d.get('verdict_basis'), 'to': want})
        d['verdict_basis'] = want
    return d, out


# --------------------------------------------------------------------------------------------- the checks
def _refs_part(raw: str) -> str:
    i = max(raw.rfind('\n§R References'), raw.rfind('\nReferences\n'))
    return raw[i:] if i >= 0 else ''


def _budget_warnings(d: dict, sch: dict) -> list[str]:
    over = []

    def walk(node, s, path):
        if not isinstance(s, dict):
            return
        if isinstance(node, str) and s.get('x-max-words') and words(node) > s['x-max-words']:
            over.append(f'{path} {words(node)}/{s["x-max-words"]}')
        if isinstance(node, dict):
            for k, sub in (s.get('properties') or {}).items():
                if k in node:
                    walk(node[k], sub, f'{path}/{k}'.lstrip('/'))
        elif isinstance(node, list) and isinstance(s.get('items'), dict):
            for i, x in enumerate(node):
                walk(x, s['items'], f'{path}/{i}')
    walk(d, sch, '')
    w = [f'{len(over)} fields over their word budget: ' + '; '.join(over[:6])] if over else []
    qb = (sch['properties'].get('quotes') or {}).get('x-quote-budget')
    if qb:
        c = Counter(q.get('supports') for q in d.get('quotes', []))
        mx = (sch['properties']['quotes'].get('maxItems'))
        extra = {k: n for k, n in c.items() if n > qb.get(k, 1)}
        if (mx and len(d.get('quotes', [])) > mx) or extra:
            w.append(f'quote budget exceeded: {len(d.get("quotes", []))} quotes' + (f' (max {mx})' if mx else '') +
                     (f'; per field {extra}' if extra else ''))
    return w


def check(d: dict, text: str | None = None, key: str | None = None, info: dict | None = None,
          expect_version: str | None = None) -> tuple[list[str], list[str]]:
    """(errors, warnings) for one coding, after normalize() has been applied by the caller. text = the blinded text the
    coder read; looked up by run.blind_sha256 (cache, then archive) when None. expect_version: the rubric version a new
    coding must carry (the collection path); otherwise any known version is checked against its own schema."""
    errs, warns = [], []
    m = model_part(d)
    ver = m.get('rubric_version')
    V = _validator(ver)
    if V is None:
        return [f'rubric_version {ver!r} is not a known version ({", ".join(SCHEMAS)})'], warns
    if expect_version and ver != expect_version:
        errs.append(f'rubric_version {ver} is not RUBRIC.md {expect_version}')
    for e in sorted(V.iter_errors(m), key=lambda e: list(e.path)):
        where = "/".join(map(str, e.path)) or "(root)"
        budget = (e.validator in ('maxItems', 'minItems') and where != 'candidate_gains') or \
                 (e.validator == 'pattern' and isinstance(e.instance, str) and re.fullmatch(r'(G\d+|none)?', e.instance)) or \
                 (e.validator == 'enum' and e.instance in (_sub(json.loads(SCHEMA_PATH.read_text()), list(e.path)) or {}).get('enum', []))
        (warns if budget else errs).append(f'schema {where}: {e.message[:200]}' + (' (warning only)' if budget else ''))
    if errs:
        return errs, warns
    sch = schema_for(ver)
    if key and d['key'] != key:
        errs.append(f'key {d["key"]!r} is not the requested {key!r}')
    if 'human_blocks' in d and d['human_blocks'] != assemble_human(d):
        errs.append('human_blocks differ from assemble_human() of the coding')
    gains = d['candidate_gains']
    ids = [g['id'] for g in gains]
    if ids != [f'G{i}' for i in range(1, len(gains) + 1)]:
        errs.append(f'candidate gain ids {ids} are not G1..G{len(gains)} in order')
    warns += _budget_warnings(m, sch)
    # ---- quotes and locators
    if text is None:
        text, _ = blind_text.cached_as_read(d['key'], (d.get('run') or {}).get('blind_sha256'))
        if text is None and (d.get('run') or {}).get('blind_sha256'):
            warns.append('no cached or archived blinded text matches run.blind_sha256: quotes checked against the current text')
            text = blind_text.cached(d['key'])
    T = Text(text) if text else None
    allq = [(f'quotes {i} ({q["supports"]})', q['quote'], q['locator'], q) for i, q in enumerate(d['quotes'])]
    for g in gains:
        allq += [(f'{g["id"]} check {j}', c['quote'], c['locator'], None) for j, c in enumerate(g['checks'])]
    unmatched, mism, located, long_q = [], [], {}, 0
    for label, quote, loc, q in allq:
        if words(quote) > MAX_QUOTE_WORDS:
            long_q += 1
            warns.append(f'{label}: {words(quote)} counted words (over {MAX_QUOTE_WORDS})')
        if not loc.strip():
            warns.append(f'{label}: no locator')
        if not quote.strip():
            warns.append(f'{label}: empty quote')
            continue
        if T is None:
            continue
        r = locate(T, quote, loc)
        if q is not None:
            located[id(q)] = r
        if not r['found']:
            unmatched.append(f'{label} ({loc}): not found in the blinded text: {quote[:80]!r}')
        elif r['locator'] == 'mismatch':
            mism.append(f'{label}: cited {loc!r} but the quote follows another marker')
    if T is None:
        warns.append('blinded text not found: quotes, locators and restating parts not checked')
    else:
        if len(unmatched) >= 2:
            errs.append(f'{len(unmatched)} quotes not found in the blinded text (fabricated or altered)')
            errs.extend(unmatched[:5])
        else:
            warns.extend(unmatched)
        if mism:
            warns.append(f'{len(mism)} locator mismatches'); warns.extend(mism[:5])
    # ---- coverage
    have = {q['supports'] for q in d['quotes']} | ({'gain'} if any(q['gain_id'] for q in d['quotes']) else set())
    need = list(REQUIRED_SUPPORT)
    if not d['precedent_search']['closest_precedent'].strip().lower().startswith('none'):
        need.append('novelty')
    if d['overreach']['exceeds_warrant'] != 'no':
        need.append('overreach')
    for s in need:
        if s not in have:
            warns.append(f'no quote supports {s}')
    for q in d['quotes']:
        if q['gain_id'] and q['gain_id'] not in ids:
            warns.append(f'quote gain_id {q["gain_id"]} names no candidate gain')
    # ---- restating parts and result statements
    rh = {'evidence': [0, 0], 'verdict': [0, 0]}
    result_outside = False
    if T is not None:
        for q in d['quotes']:
            if q['supports'] not in rh:
                continue
            r = located.get(id(q))
            if not r or r['rhetoric'] is None:
                continue
            if r['rhetoric']:
                rh[q['supports']][1] += 1
            else:
                rh[q['supports']][0] += 1
                result_outside |= bool(RESULT.search(q['quote']))
        for s, (out, inside) in rh.items():
            if out == 0:
                warns.append(f'no {s} quote located outside the abstract, key points, summary, title and conclusions'
                             + (f' ({inside} inside them)' if inside else ''))
        if (rh['evidence'][0] or rh['verdict'][0]) and not result_outside:
            warns.append('no evidence or verdict quote outside the restating parts states a result (number, direction or check outcome)')
    # ---- candidate gains
    v, cond, score, basis = d['verdict'], d['unassessable_condition'], d['advance_score'], d['verdict_basis']
    origins = [g['origin'] for g in gains]
    nh = sum(o == 'headline_component' for o in origins)
    if nh < 1 or origins[:nh] != ['headline_component'] * nh or len(gains) > MAX_GAINS.get(ver, 5) or len(gains) - nh > 2:
        warns.append(f'candidate gains: headline components first, at most {MAX_GAINS.get(ver, 5)} gains: {origins}')
    for g in gains:
        gid, c = g['id'], g['criteria']
        if v != 'unassessable':
            for k, val in c.items():
                if val == 'not_applicable' and k != 'W3':
                    warns.append(f'{gid} {k} not_applicable on an assessable coding (counts as not met)')
            if c['W3'] == 'not_applicable' and g['gain_type'] != 'capability':
                warns.append(f'{gid} W3 not_applicable is for a data set release (capability) only')
        if c['W3'] == 'met' and not any(x['addresses_principal_threat'] for x in g['checks']):
            warns.append(f'{gid} W3 met but no listed check addresses the principal threat')
        if not g['principal_threat'].strip():
            warns.append(f'{gid}: no principal_threat named')
        if (g['origin'] == 'out_of_taxonomy') != (g['gain_type'] == 'none_fits'):
            warns.append(f'{gid}: origin out_of_taxonomy if and only if gain_type none_fits')
        if g['origin'] == 'out_of_taxonomy' and not g['meaningfulness_argument'].strip():
            warns.append(f'{gid}: out_of_taxonomy gain needs a meaningfulness_argument')
        if (g['rival_test'] == 'not_applicable') != (g['gain_type'] != 'understanding'):
            warns.append(f'{gid}: rival_test is not_applicable if and only if the gain is not understanding')
        if g['gain_type'] == 'understanding' and g['rival_test'] == 'none' and c['M2'] == 'met':
            warns.append(f'{gid}: understanding with rival_test none meets M2')
        if g['origin'] == 'headline_component' and c['M1'] == 'met' and d['gap_claim_supported'] == 'no':
            warns.append(f'{gid}: M1 met on a headline component although gap_claim_supported is no')
        mag, form = g['magnitude'].strip(), g['magnitude_form']
        nq = NQ_PREFIX.match(mag)
        if nq:
            cls = next((v_ for k_, v_ in NQ_CLASSES.items() if nq.group(1).lower().startswith(k_)), None)
            if not form.startswith('not_quantifiable'):
                warns.append(f'{gid}: magnitude text says not quantifiable but magnitude_form (authoritative) is {form}')
            elif cls and cls != form:
                warns.append(f'{gid}: magnitude reason class differs from magnitude_form {form} (authoritative)')
        elif not form.startswith('not_quantifiable') and not MAG_NUM.search(mag):
            warns.append(f'{gid}: magnitude has no number with units and no "not quantifiable:" reason')
    if d['gap_claim_supported'] == 'yes' and not d['starting_state_as_stated']['prior_results']:
        warns.append('gap_claim_supported yes needs at least one specific prior result')
    # ---- verdict (errors: verdict against score, condition and criteria)
    if basis != 'none' and basis not in ids:
        errs.append(f'verdict_basis {basis} names no candidate gain')
    full = full_gains(d)
    if v == 'achieved':
        if cond != 'none':
            errs.append(f'verdict achieved with unassessable_condition {cond}')
        if not full:
            errs.append('verdict achieved but no candidate gain meets every criterion')
        elif basis not in full:
            warns.append(f'verdict_basis {basis} is not a gain meeting every criterion ({", ".join(full)})')
        if score is None or not 2 <= score <= 5:
            errs.append(f'verdict achieved needs advance_score 2 to 5, not {score}')
        if basis in ids and basis_gain(d)['evidence_access'] == 'figure_or_supplement_only':
            warns.append(f'verdict achieved on {basis}, whose result is stated only in a figure or supplement (U2)')
        if not any(q['supports'] == 'evidence' and q['gain_id'] == basis for q in d['quotes']):
            warns.append(f'no evidence quote carries gain_id {basis}')
    elif v == 'not_demonstrated':
        if cond != 'none':
            errs.append(f'verdict not_demonstrated with unassessable_condition {cond}: use unassessable')
        if full:
            errs.append(f'verdict not_demonstrated but {", ".join(full)} meets every criterion')
        if score != 1:
            errs.append(f'verdict not_demonstrated needs advance_score 1, not {score}')
    else:
        if cond == 'none':
            errs.append('verdict unassessable needs an unassessable_condition U1-U5')
        if score is not None:
            errs.append(f'verdict unassessable needs advance_score null, not {score}')
        if cond == 'U2' and any(g['evidence_access'] != 'figure_or_supplement_only' for g in gains if g['origin'] == 'headline_component'):
            warns.append('U2 while a headline component has its result stated in the text or a caption')
    if v != 'unassessable' and basis == 'none':
        errs.append(f'verdict_basis none with verdict {v}')
    if d['eligible_in_my_view'] == 'no' and not (v == 'unassessable' and cond == 'U4'):
        warns.append('eligible_in_my_view no without verdict unassessable U4')
    if cond == 'U4' and d['eligible_in_my_view'] == 'yes':
        warns.append('U4 while eligible_in_my_view is yes')
    if 'advance_score_reasons' in d and score is not None and not d['advance_score_reasons'].strip():
        warns.append('advance_score_reasons is empty')
    if d.get('blind_leak_cues') and not d.get('blind_leak_note', '').strip():
        warns.append('blind_leak_cues named without a blind_leak_note')
    # ---- roles, novelty, frame flags
    cp = d['corrected_prior_claim']
    if 'corrective' in d['roles']:
        if not (cp['text'].strip() and cp['locator'].strip()):
            warns.append('role corrective without corrected_prior_claim text and locator')
        elif not re.search(r'Ref|§|p\.|\d{4}', cp['locator']):
            warns.append('corrected_prior_claim locator is not a reference locator')
    p = d['precedent_search']
    if not p['uncited_precedent_known']:
        refs = _norm(_refs_part(text or ''))
        for mw in WORK.finditer(p['limits']):
            sur, yr = mw.group(0).split()[0].strip(',('), re.search(r'(?:19|20)\d\d', mw.group(0)).group(0)
            ns = _norm(sur)
            if not refs or not any(yr in refs[i:i + 400] for i in [x.start() for x in re.finditer(re.escape(ns), refs)]):
                warns.append(f'precedent_search.limits names {mw.group(0)!r}, not found in the reference list, but uncited_precedent_known is false')
                break
    bg = basis_gain(d)
    if (p['judgment_with_coder_knowledge'] == 'exact_precedent' and bg['criteria']['M1'] == 'met'
            and bg['replication_or_correction'] == 'none' and 'corrective' not in d['roles']):
        warns.append('exact_precedent but M1 met on the basis gain, which is neither a replication nor a correction')
    if bg['magnitude_form'] == 'quantified_change' and not any(re.search(r'\d', q['quote']) for q in d['quotes'] if q['supports'] == 'evidence'):
        warns.append('magnitude is a quantified change but no evidence quote contains a number')
    if not d['post_2022_knowledge_flag'].strip():
        warns.append('post_2022_knowledge_flag is empty (write "none" or the later work)')
    if info is not None:
        info.update({'quotes': len(allq), 'unmatched': len(unmatched), 'locator_mismatch': len(mism), 'quotes_over_30_words': long_q,
                     'evidence_quotes_outside': rh['evidence'][0], 'evidence_quotes_restating': rh['evidence'][1],
                     'verdict_quotes_outside': rh['verdict'][0], 'verdict_quotes_restating': rh['verdict'][1],
                     'warnings': len(warns), 'normalized': len(d.get('_normalized') or [])})
    return errs, warns


def validate(d: dict, text: str | None = None, key: str | None = None) -> list[str]:
    """Errors only, the interface tools/code_papers.py uses: a new coding must carry the current rubric version. Call
    normalize() first."""
    return check(d, text, key, expect_version=rubric_version())[0]


def main() -> int:
    bad, args = 0, sys.argv[1:]
    show = '--normalize' in args
    for f in [a for a in args if a != '--normalize']:
        try:
            d = json.loads(Path(f).read_text())
        except Exception as e:  # noqa: BLE001
            print(f'{f}: unreadable ({e})'); bad += 1; continue
        if isinstance(d.get('coding'), dict) and 'errors' in d:     # an _invalid record: {'errors', 'run', 'coding'}
            d = {**d['coding'], 'run': d.get('run') or {}}
        n, changes = normalize(d)
        n.update({k: d[k] for k in DERIVED if k in d})
        errs, warns = check(n)
        if show:
            for c in changes:
                print('  normalize ' + json.dumps(c, ensure_ascii=False))
        print(f'{f}: ' + ('ok' if not errs else f'{len(errs)} errors') + (f', {len(warns)} warnings' if warns else ''))
        for x in errs:
            print('  error   ' + x)
        for x in warns:
            print('  warning ' + x)
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
