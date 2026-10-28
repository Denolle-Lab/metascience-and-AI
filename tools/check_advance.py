#!/usr/bin/env python3
"""Validate advance codings (agents/advance/RUBRIC.md v1.0.1, schema agents/advance/advance.schema.json).

  python tools/check_advance.py CODING.json [...]        errors and warnings per file; exit 1 if any file has errors

A saved coding is the model's JSON plus two objects added by tools/code_papers.py after validation: `human_blocks`
(the ratings.schema.json field names, assembled by assemble_human(); RUBRIC.md section 12) and `run` (model that
answered, opaque key sent, blinded-text sha256, attempt). Both are stripped before the schema check; human_blocks must
equal assemble_human() of the coding.

Checks
  schema     JSON Schema draft 2020-12 (jsonschema)
  version    rubric_version equals the version line of RUBRIC.md
  quotes     every quote (in `quotes` and in each gain's `checks`) at most 25 words and found in the blinded text the
             coder read (private/data/roadmap/blind/<key>.txt, tools/blind_text.py). Matching ignores case, whitespace,
             punctuation, quote and dash styles; '...' splits a quote into parts that must appear in order. A quote that
             still fails is accepted when 90% of its word 4-grams occur in the text (its position is then unknown). One
             unmatched quote is a warning; two or more are an error.
  locators   for each located quote, the nearest preceding marker ([p. N], [§n ¶k], [Fig. n], [Table n], [Ref n]) at
             any occurrence must agree with the cited locator (same page, same section and paragraph, same figure, table
             or reference; the marker where the quote ends also counts). One mismatch is a warning; two or more are an
             error. A locator with no recognizable marker is not counted.
  rhetoric   the abstract, key points, summary, title and conclusions are 'restating' parts (XML: §0 and sections headed
             Conclusion(s), Summary, Concluding remarks, Outlook; PDF: everything before the Introduction heading, and
             Conclusions or Summary sections). At least one evidence quote and one verdict quote must lie outside them,
             and at least one of those outside quotes must state a result (a digit, a direction of change or a check
             outcome word); each evidence or verdict quote inside them is a warning.
  coverage   quotes support headline_claim, starting_state, gain, evidence and verdict; novelty when a closest
             precedent is named; overreach when the claim exceeds the warrant
  gains      ids G1..Gn in order; 1 to 3 headline components first, at most 2 others; out_of_taxonomy if and only if
             gain_type none_fits, and then a meaningfulness argument; rival_test not_applicable if and only if the gain
             is not understanding; understanding with rival_test none cannot meet M2; only W3 may be not_applicable, and
             only for a capability gain; W3 met needs a check that addresses the principal threat; a principal threat is
             named; M1 met on a headline component needs gap_claim_supported yes or unclear; gap_claim_supported yes
             needs a specific prior result; magnitude 'not quantifiable:' agrees with magnitude_form and names a reason
             class (warning when a magnitude has neither a number with units nor that form)
  verdict    achieved: no unassessable condition, verdict_basis is the first gain in list order with every criterion
             met (W3 may be not_applicable), whose evidence is not figure_or_supplement_only, score 2 to 5;
             not_demonstrated: no unassessable condition, every gain has a criterion not met, basis G1, score 1;
             unassessable: a condition U1-U5, basis none, score null; eligible_in_my_view no needs U4
  roles      corrective names the corrected prior claim and its locator
  novelty    uncited_precedent_known is true when precedent_search.limits names a specific work (author and year);
             warning when judgment_with_coder_knowledge is exact_precedent while the basis gain meets M1 and is
             neither a replication nor a correction, nor corrective
"""
from __future__ import annotations
import json
import re
import sys
import unicodedata
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import blind_text  # noqa: E402

SCHEMA_PATH = ROOT / 'agents' / 'advance' / 'advance.schema.json'
RUBRIC_PATH = ROOT / 'agents' / 'advance' / 'RUBRIC.md'
REQUIRED_SUPPORT = ('headline_claim', 'starting_state', 'gain', 'evidence', 'verdict')
DERIVED = ('human_blocks', 'run')
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
_VALIDATOR = None


def rubric_version() -> str:
    for line in RUBRIC_PATH.read_text().splitlines():
        if line.startswith('version:'):
            return line.split(':', 1)[1].strip()
    return 'unknown'


def _validator():
    global _VALIDATOR
    if _VALIDATOR is None:
        _VALIDATOR = jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))
    return _VALIDATOR


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


# --------------------------------------------------------------------------------------------- the checks
def check(d: dict, text: str | None = None, key: str | None = None, info: dict | None = None) -> tuple[list[str], list[str]]:
    """(errors, warnings) for one coding. text = the blinded text; read from the cache by key when None. info, when
    given, receives counts (quotes, unmatched, locator mismatches, restating quotes) for the pilot report."""
    errs, warns = [], []
    m = model_part(d)
    for e in sorted(_validator().iter_errors(m), key=lambda e: list(e.path)):
        errs.append(f'schema {"/".join(map(str, e.path)) or "(root)"}: {e.message[:200]}')
    if errs:
        return errs, warns
    if key and d['key'] != key:
        errs.append(f'key {d["key"]!r} is not the requested {key!r}')
    if d['rubric_version'] != rubric_version():
        errs.append(f'rubric_version {d["rubric_version"]} is not RUBRIC.md {rubric_version()}')
    if 'human_blocks' in d and d['human_blocks'] != assemble_human(d):
        errs.append('human_blocks differ from assemble_human() of the coding')
    gains = d['candidate_gains']
    ids = [g['id'] for g in gains]
    # ---- quotes and locators
    if text is None:
        text = blind_text.cached(d['key'])
    if text and 'run' in d and d['run'].get('blind_sha256') and d['run']['blind_sha256'] != blind_text.sha(text):
        warns.append('the cached blinded text differs from the one the coder read (blind_sha256): quote checks may be off')
    T = Text(text) if text else None
    allq = [(f'quotes {i} ({q["supports"]})', q['quote'], q['locator'], q) for i, q in enumerate(d['quotes'])]
    for g in gains:
        allq += [(f'{g["id"]} check {j}', c['quote'], c['locator'], None) for j, c in enumerate(g['checks'])]
    unmatched, mism, located = [], [], {}
    for label, quote, loc, q in allq:
        if len(quote.split()) > 25:
            errs.append(f'{label}: over 25 words')
        if not loc.strip():
            errs.append(f'{label}: no locator')
        if not quote.strip():
            errs.append(f'{label}: empty quote')
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
        (warns.extend if len(unmatched) == 1 else errs.extend)(([f'{len(unmatched)} quotes not found in the blinded text'] if len(unmatched) > 1 else []) + unmatched[:5])
        (warns.extend if len(mism) == 1 else errs.extend)(([f'{len(mism)} locator mismatches'] if len(mism) > 1 else []) + mism[:5])
    # ---- coverage
    have = {q['supports'] for q in d['quotes']}
    need = list(REQUIRED_SUPPORT)
    if not d['precedent_search']['closest_precedent'].strip().lower().startswith('none'):
        need.append('novelty')
    if d['overreach']['exceeds_warrant'] != 'no':
        need.append('overreach')
    for s in need:
        if s not in have:
            errs.append(f'no quote supports {s}')
    for q in d['quotes']:
        if q['gain_id'] and q['gain_id'] not in ids:
            errs.append(f'quote gain_id {q["gain_id"]} names no candidate gain')
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
                warns.append(f'{q["supports"]} quote from a restating part (abstract, key points, summary, title or conclusions): {q["quote"][:60]!r}')
            else:
                rh[q['supports']][0] += 1
                result_outside |= bool(RESULT.search(q['quote']))
        for s, (out, _) in rh.items():
            if out == 0:
                errs.append(f'no {s} quote located outside the abstract, key points, summary, title and conclusions')
        if (rh['evidence'][0] or rh['verdict'][0]) and not result_outside:
            errs.append('no evidence or verdict quote outside the restating parts states a result (number, direction or check outcome)')
    # ---- candidate gains
    if ids != [f'G{i}' for i in range(1, len(gains) + 1)]:
        errs.append(f'candidate gain ids {ids} are not G1..G{len(gains)} in order')
    origins = [g['origin'] for g in gains]
    nh = sum(o == 'headline_component' for o in origins)
    if not (1 <= nh <= 3) or origins[:nh] != ['headline_component'] * nh or len(gains) - nh > 2:
        errs.append(f'candidate gains must list 1 to 3 headline components first, then at most 2 others: {origins}')
    for g in gains:
        gid, c = g['id'], g['criteria']
        for k, val in c.items():
            if val == 'not_applicable' and k != 'W3':
                errs.append(f'{gid} {k}: only W3 may be not_applicable')
        if c['W3'] == 'not_applicable' and g['gain_type'] != 'capability':
            errs.append(f'{gid} W3 not_applicable is for a data set release (capability) only')
        if c['W3'] == 'met' and not any(x['addresses_principal_threat'] for x in g['checks']):
            errs.append(f'{gid} W3 met but no check addresses the principal threat')
        if not g['principal_threat'].strip():
            errs.append(f'{gid}: no principal_threat named')
        if (g['origin'] == 'out_of_taxonomy') != (g['gain_type'] == 'none_fits'):
            errs.append(f'{gid}: origin out_of_taxonomy if and only if gain_type none_fits')
        if g['origin'] == 'out_of_taxonomy' and not g['meaningfulness_argument'].strip():
            errs.append(f'{gid}: out_of_taxonomy gain needs a meaningfulness_argument')
        if (g['rival_test'] == 'not_applicable') != (g['gain_type'] != 'understanding'):
            errs.append(f'{gid}: rival_test is not_applicable if and only if the gain is not understanding')
        if g['gain_type'] == 'understanding' and g['rival_test'] == 'none' and c['M2'] == 'met':
            errs.append(f'{gid}: understanding with rival_test none cannot meet M2')
        if g['origin'] == 'headline_component' and c['M1'] == 'met' and d['gap_claim_supported'] == 'no':
            errs.append(f'{gid}: M1 met on a headline component although gap_claim_supported is no')
        mag = g['magnitude'].strip()
        nq = re.match(r'not quantifiable:\s*(.*)', mag, re.I | re.S)
        if nq:
            cls = next((v for k, v in NQ_CLASSES.items() if nq.group(1).lower().startswith(k)), None)
            if not cls:
                warns.append(f'{gid}: "not quantifiable:" without one of the reason classes')
            if not g['magnitude_form'].startswith('not_quantifiable'):
                errs.append(f'{gid}: magnitude says not quantifiable but magnitude_form is {g["magnitude_form"]}')
            elif cls and cls != g['magnitude_form']:
                errs.append(f'{gid}: magnitude reason class does not match magnitude_form {g["magnitude_form"]}')
        else:
            if g['magnitude_form'].startswith('not_quantifiable'):
                errs.append(f'{gid}: magnitude_form {g["magnitude_form"]} but the magnitude does not start with "not quantifiable:"')
            if not MAG_NUM.search(mag):
                warns.append(f'{gid}: magnitude has no number with units and no "not quantifiable:" reason')
    if d['gap_claim_supported'] == 'yes' and not d['starting_state_as_stated']['prior_results']:
        errs.append('gap_claim_supported yes needs at least one specific prior result')
    # ---- verdict
    v, cond, score, basis = d['verdict'], d['unassessable_condition'], d['advance_score'], d['verdict_basis']
    if basis != 'none' and basis not in ids:
        errs.append(f'verdict_basis {basis} names no candidate gain')
    full = [g['id'] for g in gains if all(g['criteria'][k] == 'met' or (k == 'W3' and g['criteria'][k] == 'not_applicable') for k in CRIT)]
    if v == 'achieved':
        if cond != 'none':
            errs.append(f'verdict achieved with unassessable_condition {cond}')
        if not full:
            errs.append('verdict achieved but no candidate gain meets every criterion')
        elif basis != full[0]:
            errs.append(f'verdict_basis {basis} is not the first gain meeting every criterion ({full[0]})')
        if score is None or not 2 <= score <= 5:
            errs.append(f'verdict achieved needs advance_score 2 to 5, not {score}')
        if basis in ids and basis_gain(d)['evidence_access'] == 'figure_or_supplement_only':
            errs.append(f'verdict achieved on {basis}, whose result is stated only in a figure or supplement (U2)')
        if not any(q['supports'] == 'evidence' and q['gain_id'] == basis for q in d['quotes']):
            warns.append(f'no evidence quote carries gain_id {basis}')
    elif v == 'not_demonstrated':
        if cond != 'none':
            errs.append(f'verdict not_demonstrated with unassessable_condition {cond}: use unassessable')
        if full:
            errs.append(f'verdict not_demonstrated but {", ".join(full)} meets every criterion')
        if basis != 'G1':
            errs.append(f'verdict not_demonstrated needs verdict_basis G1, not {basis}')
        if score != 1:
            errs.append(f'verdict not_demonstrated needs advance_score 1, not {score}')
    else:
        if cond == 'none':
            errs.append('verdict unassessable needs an unassessable_condition U1-U5')
        if basis != 'none':
            errs.append(f'verdict unassessable needs verdict_basis none, not {basis}')
        if score is not None:
            errs.append(f'verdict unassessable needs advance_score null, not {score}')
        if cond == 'U2' and any(g['evidence_access'] != 'figure_or_supplement_only' for g in gains if g['origin'] == 'headline_component'):
            warns.append('U2 while a headline component has its result stated in the text or a caption')
    if v != 'unassessable' and basis == 'none':
        errs.append(f'verdict_basis none with verdict {v}')
    if d['eligible_in_my_view'] == 'no' and not (v == 'unassessable' and cond == 'U4'):
        errs.append('eligible_in_my_view no needs verdict unassessable with condition U4')
    if cond == 'U4' and d['eligible_in_my_view'] == 'yes':
        warns.append('U4 while eligible_in_my_view is yes')
    # ---- roles, novelty, frame flags
    cp = d['corrected_prior_claim']
    if 'corrective' in d['roles']:
        if not (cp['text'].strip() and cp['locator'].strip()):
            errs.append('role corrective needs corrected_prior_claim with text and locator')
        elif not re.search(r'Ref|§|p\.|\d{4}', cp['locator']):
            warns.append('corrected_prior_claim locator is not a reference locator')
    p = d['precedent_search']
    if WORK.search(p['limits']) and not p['uncited_precedent_known']:
        errs.append('precedent_search.limits names a specific work but uncited_precedent_known is false')
    bg = basis_gain(d)
    if (p['judgment_with_coder_knowledge'] == 'exact_precedent' and bg['criteria']['M1'] == 'met'
            and bg['replication_or_correction'] == 'none' and 'corrective' not in d['roles']):
        warns.append('exact_precedent but M1 met on the basis gain, which is neither a replication nor a correction')
    if bg['magnitude_form'] == 'quantified_change' and not any(re.search(r'\d', q['quote']) for q in d['quotes'] if q['supports'] == 'evidence'):
        warns.append('magnitude is a quantified change but no evidence quote contains a number')
    if not d['post_2022_knowledge_flag'].strip():
        errs.append('post_2022_knowledge_flag is empty (write "none" or the later work)')
    if info is not None:
        info.update({'quotes': len(allq), 'unmatched': len(unmatched), 'locator_mismatch': len(mism),
                     'evidence_quotes_outside': rh['evidence'][0], 'evidence_quotes_restating': rh['evidence'][1],
                     'verdict_quotes_outside': rh['verdict'][0], 'verdict_quotes_restating': rh['verdict'][1]})
    return errs, warns


def validate(d: dict, text: str | None = None, key: str | None = None) -> list[str]:
    """Errors only, the interface tools/code_papers.py uses for every task's validator."""
    return check(d, text, key)[0]


def main() -> int:
    bad = 0
    for f in sys.argv[1:]:
        try:
            d = json.loads(Path(f).read_text())
        except Exception as e:  # noqa: BLE001
            print(f'{f}: unreadable ({e})'); bad += 1; continue
        errs, warns = check(d)
        print(f'{f}: ' + ('ok' if not errs else f'{len(errs)} errors') + (f', {len(warns)} warnings' if warns else ''))
        for x in errs:
            print('  error   ' + x)
        for x in warns:
            print('  warning ' + x)
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
