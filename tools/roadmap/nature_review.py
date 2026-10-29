"""Units of a Nature Portfolio peer review file (Nature Communications, Communications Earth & Environment): a second,
independent reader, kept for comparison only.

Status (October 28, 2026). Not used by any request, validator or plan. The reader the pipeline uses is
tools/roadmap/g27_nature_units.py (tools/code_papers.py, tools/check_coding_nature.py, g35_nature_family.py). This
module was written in parallel by a second agent; `compare` measures how far the two readers agree, so a change to
either can be checked against the other. Its outputs carry an _alt suffix so they never overwrite g27_nature_units'.
On the 18 cop22 NC and CEE files (g27_nature_units 1.0.0) the two gave every paper the same set of role-round blocks
and the same role and round to 99.3% of the 8-word shingles both read; this reader splits paragraphs more finely
(about 1.5 times the units). g27_nature_units was kept because the request, validator, cache and plan were built on
it and its units are coarser (fewer locators for the coder to cite, each with more context); it took over this
reader's 'Response:' marker inside a referee block in 1.1.0.

Why. The review addendum (agents/coder/REVIEW_ADDENDUM.md 1.0.0) codes disclosures by Copernicus author units (AC
paragraphs of the open discussion, AR pages of the author-response PDFs; tools/roadmap/g27_author_responses.py). A
Nature Portfolio paper has no open discussion; its peer review file (the '..._MOESM<n>_ESM.pdf' that g32 saved under
review/<key>/) holds, round by round, the editor's decision letter (Communications Earth & Environment only), the
referee reports and the authors' rebuttal letter, which quotes the referees point by point. This module splits that
file into located paragraphs in the same spirit as g27's AC units. It does not change g27 or any Copernicus input.

Units (locators, printed in square brackets at the start of each paragraph of the rendered document)
  Rn-roundk ¶m   paragraph m of referee n's report in round k (R0: a report whose referee number the file does not give)
  E-roundk ¶m    paragraph m of the editor's text in round k (decision letter, 'Editor (Remarks to the Author)')
  A-roundk ¶m    paragraph m of the authors' response to the round-k reports (it also carries the referee text the
                 authors quote; such a paragraph is marked quoted = True in the unit records: >= QUOTED of its 8-word
                 shingles occur in the R and E text of the file, g27's rule)
Round k counts the reports: round 1 answers the first submission, round 2 the first revision, and so on. The
authors' response to round k is filed with revision k, so A-roundk follows Rn-roundk in the file.

Parsing (pdftotext without -layout, page by page; PARSER_VERSION)
  furniture  the licence block of page 1 (through the creativecommons.org line), the redaction notice, lone page
             numbers and lines of fewer than MIN_PARA_WORDS words that are not headings
  paragraph  a blank line; a line that ends a sentence and is shorter than SHORT of the page's 90th-percentile line
             length; a heading; a response marker ('Response:', 'Reply', 'Answer', 'Author's response', ...); a
             point marker ('Reviewer's Comment', 'Comment 3', 'R1-1:', '1.', 'L101:') starts a new paragraph
  headings   explicit round headers of Communications Earth & Environment files ('Decision letter and referee
             reports: first round', 'Author Responses: first round') fix the round and the section. Without them
             (Nature Communications files) a state machine reads the referee headings ('Reviewer #1 (Remarks to the
             Author):', 'REVIEWER COMMENTS', 'REVIEWERS' COMMENTS'), editor headings, response-letter headings
             ('Response to Reviewer #1', 'DETAILED RESPONSES TO THE REVIEWERS', 'Dear Editor') and response markers.
             A referee heading or a 'REVIEWER COMMENTS' header inside a response letter is read ahead (ahead(): the
             majority label of the next AHEAD paragraphs of at least MIN_WORDS words; a referee not yet seen in a block
             of reports: the first such paragraph only): a paragraph that repeats earlier referee text (>= QUOTED of
             its shingles; inside a block of reports, referee text of the current round only, since a referee may
             quote their own earlier report) is quoted, one that repeats the authors' earlier response or is repeated later in the file
             (a report is quoted in the next response letter) or reads in a referee's voice is a report, one in the
             authors' voice (voice()) is the authors'. Quoted or authors: the letter goes on; report: a new round of
             reports starts. A report paragraph that repeats referee text of the current round or reads in the authors' voice, is
             not repeated later in the file and does not quote the authors' earlier response, ends the reports (the
             response letter has begun without a heading). In editor text only a marker or heading ends it.
Clean parse: at least one referee unit and one author unit that is not quoted referee text.
Known limits: referee text the authors paste from a report the file does not carry (an annotated PDF, an attachment)
is not recognised as quoted and stays in an A unit; a short line inside a sentence can split a paragraph. The review
addendum for these files (agents/coder/REVIEW_ADDENDUM_NATURE.md) tells the coder that only the authors' own words
count, and the validator (tools/check_coding_nature.py) drops a disclosure whose quote is referee text of the file.

Outputs  derived/review/nature_units_alt/<key>.txt (the rendered document; header: source file names, their sha256 and
         the parser version), derived/review/nature_units_alt.json (extract: per-paper unit counts, rounds, voice
         diagnostics); derived/review/nature_reader_agreement.json (compare: per paper, the role and round each reader
         gives the 8-word shingles both read, and the words per role and round of each)
Run:     python tools/roadmap/nature_review.py extract [--keys k1,k2]
         python tools/roadmap/nature_review.py compare [--keys k1,k2]   (default: every Nature folder)
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from g27_author_responses import norm, shingles, QUOTED, MIN_WORDS  # noqa: E402  (g27's matching, unchanged)

PARSER_VERSION = 'nature-units 1.0.0'
SHORT = 0.75
MIN_PARA_WORDS = 3
AHEAD = 3
UNIT_RE = re.compile(r'^\[((?:R\d+|E|A)-round\d+ ¶\d+)\] (.*)$')
ORD = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6, 'seventh': 7, 'eighth': 8}

DECISION_RE = re.compile(r'^Decision letter and referee reports?:?\s*(\w+) round\b', re.I)
AUTHORS_RE = re.compile(r'^Authors?[’\']?s?[’\']? Responses?:?\s*(\w+) round\b', re.I)
REPORTS_RE = re.compile(r'^(?:REVIEWERS?[’\']?S?[’\']?|Reviewers?[’\']?s?[’\']?|REFEREES?[’\']?|Referees?[’\']?)\s+'
                        r'(?:COMMENTS|Comments|comments|REPORTS?|Reports?)\s*:?\s*(?:</?B>)?\s*:?\s*$')
REVIEWER_RE = re.compile(r'^[-–—_=*\s]*(?:REVIEWER|Reviewer|Referee|REFEREE)\s*#?\s*(\d+)\s*(.*)$')
REVIEWER_REST = re.compile(r'^(?:[:,.;]|\(|[-–—_=]|$|(?:COMMENTS|comments|Comments|attachment|Attachment|Remarks|Report|report)\b)')
REMARKS_RE = re.compile(r'^\(?Remarks to the Author\)?:?\s*$', re.I)
EDITOR_RE = re.compile(r'^(?:Editor\s*(?:\(Remarks to the Author\))?|Editorial Board Member comments|Editor[’\']?s? comments?|'
                       r'EDITOR[’\']?S? COMMENTS?)\s*:?\s*$', re.I)
RESPONSE_DOC_RE = re.compile(r'^[-–—_=*\s]*(?:point[- ]by[- ]point (?:response|reply)|detailed responses?|responses? to (?:the )?'
                             r'(?:reviewers?|referees?|editors?|comments|the reviewer)|repl(?:y|ies)(?: back)? to (?:the )?'
                             r'(?:reviewers?|referees?|comments)|rebuttal|authors?[’\']?s? (?:responses?|replies|reply) to|'
                             r'.*with our responses)', re.I)
DEAR_AUTHOR_RE = re.compile(r'^Dear (?:Editors?|Dr\.? [\w\-]+ and (?:the )?reviewers|Editor and Reviewers|Reviewers?)\b', re.I)
RESPONSE_MARK_RE = re.compile(r'^(?:Response|Responses|Reply|Answer|Our response|Authors?[’\']?s? (?:response|reply)|AR\s*\d*)'
                              r'\s*(?:to the (?:comment|editor)[^:]*)?[:.\-–]?(?:\s|$)')
POINT_RE = re.compile(r'^(?:Reviewer[’\']?s? [Cc]omments?:?$|Comments?\s*\d|Point\s*\d|Q\d|R\d+[-.]\d+\s*[:.]|\(?\d{1,2}[).]\s+\S|'
                      r'[A-Z]?\d{1,2}\.\d+\s|L\d+|Lines? \d+|[•▪●◦]\s|Original:|Revised\b)')
FURNITURE_RE = re.compile(r'^(?:\d{1,3}|Page \d+( of \d+)?|\d{1,2}-\d{1,2}-\d{2,4})$')


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def source_files(folder: Path) -> list[Path]:
    """The peer review PDF(s) of a review folder: Springer supplementary files '<journal>_<year>_<n>_MOESM<k>_ESM.pdf'."""
    return sorted(folder.glob('*_MOESM*_ESM.pdf'))


def is_nature_folder(folder: Path) -> bool:
    """A Nature Portfolio peer review file and no Copernicus open discussion."""
    return not (folder / 'discussion.txt').is_file() and bool(source_files(folder))


def voice(text: str) -> tuple[int, int, int]:
    """(authors' voice, referee voice, first-person plural) cue counts of a paragraph."""
    t = text.lower()
    we = len(re.findall(r'\b(?:we|our|ours|us)\b', t))
    a = we + 3 * len(re.findall(
        r'\b(?:the|this|each|both|all) (?:reviewers?|referees?)\b|\breviewer[’\']?s\b|\bthank (?:you|the)\b|\bin the revised (?:manuscript|version|text)\b', t))
    r = 3 * len(re.findall(r'\b(?:the|these) authors\b|\bauthors[’\']', t)) + len(re.findall(r'\b(?:i|my|me)\b', t))
    return a, r, we


def authors_voice(text: str) -> bool:
    a, r, we = voice(text)
    return we >= 2 and a >= 3 and a > 2 * r


def referee_voice(text: str) -> bool:
    a, r, we = voice(text)
    return r >= 3 and r > a


def heading(line: str) -> tuple[str, object] | None:
    """(kind, info) of a structural line, or None."""
    s = line.strip()
    if not s:
        return None
    if (m := DECISION_RE.match(s)):
        return 'decision', ORD.get(m.group(1).lower())
    if (m := AUTHORS_RE.match(s)):
        return 'authors', ORD.get(m.group(1).lower())
    if len(s.split()) <= 15 and RESPONSE_DOC_RE.match(s):
        n = re.search(r'(?:reviewer|referee)\s*#?\s*(\d+)', s, re.I)
        return 'response_doc', int(n.group(1)) if n else None
    if REPORTS_RE.match(s):
        return 'reports', None
    if (m := REVIEWER_RE.match(s)) and REVIEWER_REST.match(m.group(2).strip()) and len(m.group(2).split()) <= 12:
        return 'reviewer', int(m.group(1))
    if REMARKS_RE.match(s):
        return 'remarks', None
    if EDITOR_RE.match(s):
        return 'editor', None
    return None


def pages_of(pdf: Path) -> list[list[str]]:
    out = subprocess.run(['pdftotext', str(pdf), '-'], capture_output=True, text=True).stdout
    return [pg.split('\n') for pg in out.split('\f')]


def items_of(pdfs: list[Path]) -> tuple[list[dict], dict]:
    """Headings and paragraphs in file order: {'t': 'head', 'kind', 'info', 'line'} or {'t': 'para', 'text', 'page'}."""
    items, stats = [], Counter()
    for fi, pdf in enumerate(pdfs, 1):
        pages = pages_of(pdf)
        lic = next((i for i, l in enumerate(pages[0]) if 'creativecommons.org/licenses' in l), None) if pages else None
        buf, bpage = [], None

        def flush():
            nonlocal buf, bpage
            txt = re.sub(r'\s+', ' ', ' '.join(buf)).strip()
            if txt:
                if len(txt.split()) < MIN_PARA_WORDS and not RESPONSE_MARK_RE.match(txt):
                    stats['short_dropped'] += 1
                else:
                    items.append({'t': 'para', 'text': txt, 'page': bpage, 'file': fi})
            buf, bpage = [], None
        for pn, lines in enumerate(pages, 1):
            if pn == 1 and lic is not None:
                lines = lines[lic + 1:]
            lens = sorted(len(l) for l in lines if l.strip())
            p90 = lens[int(0.9 * (len(lens) - 1))] if lens else 80
            nonblank = [i for i, l in enumerate(lines) if l.strip()]
            first, lastl = (nonblank[0], nonblank[-1]) if nonblank else (0, -1)
            for i, raw in enumerate(lines):
                line = raw.strip()
                if not line:
                    if first < i < lastl:   # blank lines before the first or after the last text line of a page
                        flush()             # do not end a paragraph that runs over the page break
                    continue
                if FURNITURE_RE.match(line) or line.startswith('Web links to the author') or line == 'to maintain confidentiality.':
                    stats['furniture_lines'] += 1
                    continue
                h = heading(line)
                if h:
                    flush()
                    items.append({'t': 'head', 'kind': h[0], 'info': h[1], 'line': line, 'page': pn, 'file': fi})
                    continue
                if buf and (RESPONSE_MARK_RE.match(line) or POINT_RE.match(line) or DEAR_AUTHOR_RE.match(line)
                            or re.match(r'^Dear\b', line)):
                    flush()
                if not buf:
                    bpage = pn
                buf.append(line)
                if re.search(r'[.?!:;)"”’]$', line) and len(line) < SHORT * p90:
                    flush()
        flush()
    return items, dict(stats)


def parse(pdfs: list[Path]) -> tuple[list[dict], dict]:
    """Units {'unit', 'role' (referee|editor|author), 'reviewer', 'round', 'page', 'text', 'quoted'} and statistics."""
    items, stats = items_of(pdfs)
    explicit = any(it['t'] == 'head' and it['kind'] in ('decision', 'authors') for it in items)
    units, ref_sh, auth_sh, cur_sh = [], set(), set(), set()   # cur_sh: referee and editor text of the current round
    counters = Counter()
    state = {'mode': 'start', 'round': 0, 'reviewer': None, 'seen': set(), 'answering': None}
    switches = Counter()

    def add(role, text, page):
        k = max(1, state['round'])
        if role == 'referee':
            n = state['reviewer'] if state['reviewer'] is not None else 0
            fam = f'R{n}-round{k}'
        elif role == 'editor':
            fam = f'E-round{k}'
        else:
            fam = f'A-round{k}'
        counters[fam] += 1
        u = {'unit': f'{fam} ¶{counters[fam]}', 'role': role, 'round': k, 'page': page, 'text': text,
             'reviewer': state['reviewer'] if role == 'referee' else state['answering'] if role == 'author' else None}
        units.append(u)
        sh = shingles(norm(text).split())
        (ref_sh if role in ('referee', 'editor') else auth_sh).update(sh)
        if role in ('referee', 'editor'):
            cur_sh.update(sh)

    def dup(text, against=None) -> bool:
        sh = shingles(norm(text).split())
        pool = ref_sh if against is None else against
        return bool(sh) and len(sh & pool) / len(sh) >= QUOTED

    def quotes_authors(text) -> bool:
        """A referee quoting the authors' earlier response (a later-round report), not the authors writing."""
        return dup(text, auth_sh) and not dup(text)

    # forward repetition: the share of a paragraph's shingles that occur again later in the file (a referee report is
    # quoted in the next response letter; the authors' own words are rarely repeated)
    last = {}
    for j, it in enumerate(items):
        if it['t'] == 'para':
            for x in shingles(norm(it['text']).split()):
                last[x] = j

    def fwd(j) -> float:
        sh = shingles(norm(items[j]['text']).split())
        return sum(last[x] > j for x in sh) / len(sh) if sh else 0.0

    def ahead(i, n=AHEAD) -> str:
        """'quoted', 'authors', 'report' or 'unknown': the majority label (a tie goes to the earliest) of the next n
        paragraphs of >= MIN_WORDS words after item i, up to the next heading (a referee heading before the first such
        paragraph, or a referee's attachment heading, does not stop it). Each is quoted when it repeats earlier referee
        text, authors when it reads in the authors' voice and is not repeated later, report when it is repeated later or
        reads in a referee's voice. A response marker or salutation right after the heading gives authors."""
        seen = []
        for j in range(i + 1, len(items)):
            it = items[j]
            if it['t'] == 'head':
                if it['kind'] == 'remarks' or (it['kind'] == 'reviewer' and ('ttachment' in it['line'] or not seen)):
                    continue
                if it['kind'] in ('response_doc', 'authors'):
                    seen.append('authors')
                break
            if RESPONSE_MARK_RE.match(it['text']) or DEAR_AUTHOR_RE.match(it['text']):
                seen.append('authors')
                break
            if len(it['text'].split()) >= MIN_WORDS:
                t = it['text']
                q = dup(t, cur_sh) if state['mode'] == 'referee' else dup(t)
                seen.append('quoted' if q else 'report' if quotes_authors(t) or fwd(j) >= QUOTED or referee_voice(t)
                            else 'authors' if authors_voice(t) else 'unknown')
                if len(seen) >= n:
                    break
        if 'authors' in seen[-1:] and len(seen) == 1:
            return 'authors'
        votes = [v for v in seen if v != 'unknown']
        if not votes:
            return 'unknown'
        top = Counter(votes).most_common()
        best = [v for v, c in top if c == top[0][1]]
        return next(v for v in votes if v in best)   # majority; a tie goes to the earliest

    def new_round():
        cur_sh.clear()
        state['round'] += 1
        state['seen'] = set()
        state['reviewer'] = None

    for i, it in enumerate(items):
        if explicit:
            if it['t'] == 'head':
                if it['kind'] == 'decision':
                    state.update(mode='editor', reviewer=None, seen=set())
                    state['round'] = it['info'] or state['round'] + 1
                elif it['kind'] == 'authors':
                    state.update(mode='author', answering=None)
                    state['round'] = it['info'] or max(1, state['round'])
                elif state['mode'] in ('editor', 'referee'):
                    if it['kind'] == 'reports':
                        state.update(mode='referee', reviewer=None)
                    elif it['kind'] == 'reviewer':
                        state.update(mode='referee', reviewer=it['info'])
                    elif it['kind'] == 'editor':
                        state.update(mode='editor')
                elif state['mode'] == 'author' and it['kind'] in ('reviewer', 'response_doc') and it['info']:
                    state['answering'] = it['info']
                continue
            if state['mode'] == 'start':
                stats['before_first_section'] = stats.get('before_first_section', 0) + 1
                continue
            role = {'editor': 'editor', 'referee': 'referee', 'author': 'author'}[state['mode']]
            add(role, it['text'], it['page'])
            continue
        # inferred (no explicit round headers)
        if it['t'] == 'head':
            kind, info = it['kind'], it['info']
            if kind == 'response_doc':
                if state['mode'] != 'author':
                    switches['to_author:heading'] += 1
                state['mode'] = 'author'
                state['round'] = max(1, state['round'])
                if info:
                    state['answering'] = info
            elif kind == 'reports':
                a = ahead(i)
                if state['mode'] == 'start':
                    new_round()
                    state['mode'] = 'referee'
                elif state['mode'] == 'author':
                    if a in ('report', 'unknown'):
                        new_round()
                        state['mode'] = 'referee'
                        switches['new_round:reports_header'] += 1
                elif a in ('quoted', 'authors'):
                    state['mode'] = 'author'
                    switches['to_author:reports_header_' + a] += 1
                else:
                    if state['seen']:
                        new_round()
                    state['mode'] = 'referee'
            elif kind == 'reviewer' and 'ttachment' in it['line'] and state['mode'] == 'referee' and info == state['reviewer']:
                pass   # 'Reviewer #1 Attachment on the following page': the same report goes on
            elif kind == 'reviewer':
                # a referee not yet seen in this block of reports: only the first paragraph decides
                a = ahead(i, 1 if state['mode'] == 'referee' and info not in state['seen'] else AHEAD)
                if state['mode'] == 'start':
                    new_round()
                    state.update(mode='referee', reviewer=info)
                    state['seen'].add(info)
                elif state['mode'] in ('referee', 'editor'):
                    if a in ('quoted', 'authors') or (info in state['seen'] and a != 'report'):
                        state.update(mode='author', answering=info)
                        switches['to_author:reviewer_heading_' + a] += 1
                    else:
                        if info in state['seen']:
                            new_round()
                            switches['new_round:repeated_reviewer'] += 1
                        state.update(mode='referee', reviewer=info)
                        state['seen'].add(info)
                else:   # author
                    if a == 'report':
                        new_round()
                        state.update(mode='referee', reviewer=info)
                        state['seen'].add(info)
                        switches['new_round:reviewer_heading'] += 1
                    else:
                        state['answering'] = info
            elif kind == 'editor':
                if state['mode'] in ('author', 'start'):
                    new_round()
                state['mode'] = 'editor'
            continue
        text = it['text']
        if state['mode'] == 'start':
            if DEAR_AUTHOR_RE.match(text) or RESPONSE_MARK_RE.match(text):
                state.update(mode='author', round=1)
            else:
                stats['before_first_section'] = stats.get('before_first_section', 0) + 1
                continue
        if state['mode'] in ('referee', 'editor'):
            if RESPONSE_MARK_RE.match(text) or DEAR_AUTHOR_RE.match(text):
                state['mode'] = 'author'
                switches['to_author:marker'] += 1
            elif (state['mode'] == 'referee' and len(text.split()) >= MIN_WORDS and fwd(i) < QUOTED and not quotes_authors(text)
                  and (dup(text, cur_sh) or authors_voice(text))):
                state.update(mode='author', answering=state['reviewer'])
                switches['to_author:' + ('quoted' if dup(text, cur_sh) else 'voice')] += 1
        add({'referee': 'referee', 'editor': 'editor', 'author': 'author'}[state['mode']], text, it['page'])

    # quoted referee text inside the authors' letters, against all referee and editor text of the file
    ref_all = shingles(norm(' '.join(u['text'] for u in units if u['role'] != 'author')).split())
    for u in units:
        sh = shingles(norm(u['text']).split())
        u['quoted'] = u['role'] == 'author' and bool(sh) and len(sh & ref_all) / len(sh) >= QUOTED
    a_own = [u for u in units if u['role'] == 'author' and not u['quoted']]
    stats.update({'explicit_headers': explicit, 'rounds': max((u['round'] for u in units), default=0),
                  'units': len(units), 'referee_units': sum(u['role'] == 'referee' for u in units),
                  'editor_units': sum(u['role'] == 'editor' for u in units),
                  'author_units': sum(u['role'] == 'author' for u in units), 'author_units_own': len(a_own),
                  'author_units_quoted': sum(u['quoted'] for u in units),
                  'referee_units_in_authors_voice': sum(u['role'] == 'referee' and authors_voice(u['text']) for u in units),
                  'author_own_units_in_referee_voice': sum(referee_voice(u['text']) for u in a_own),
                  'words_referee': sum(len(u['text'].split()) for u in units if u['role'] == 'referee'),
                  'words_author_own': sum(len(u['text'].split()) for u in a_own),
                  'switches': dict(switches), 'clean': bool(any(u['role'] == 'referee' for u in units) and a_own)})
    return units, stats


def render(units: list[dict], head: list[str]) -> str:
    out, last = list(head), None
    for u in units:
        sec = (u['round'], u['role'], u['reviewer'] if u['role'] != 'editor' else None)
        if sec != last:
            if u['role'] == 'referee':
                out.append(f"## Round {u['round']}: report of referee {u['reviewer'] or '(number not given)'}")
            elif u['role'] == 'editor':
                out.append(f"## Round {u['round']}: editor")
            else:
                out.append(f"## Round {u['round']}: authors' response" + (f" (to referee {u['reviewer']})" if u['reviewer'] else ''))
            last = sec
        out.append(f"[{u['unit']}] {u['text']}")
    return '\n'.join(out) + '\n'


def document(folder: Path, doi: str | None = None) -> tuple[str, list[dict], dict]:
    """(rendered document, units, stats) of a review folder's peer review file(s)."""
    pdfs = source_files(folder)
    units, stats = parse(pdfs)
    head = [f'# Peer review file{"s" if len(pdfs) > 1 else ""} of {doi or folder.name}, split by round into referee (R), '
            "editor (E) and authors' response (A) paragraphs",
            '# Locators: [Rn-roundk ¶m] referee n, report of round k; [E-roundk ¶m] editor, round k; [A-roundk ¶m] '
            "the authors' response to the round-k reports (it quotes the referees)."]
    return render(units, head), units, stats


def source_header(folder: Path) -> str:
    return '# sources: ' + ' '.join(f'{p.name}={sha16(p)}' for p in source_files(folder)) + f' parser={PARSER_VERSION}'


def units_of_text(doc: str | None) -> dict[str, str]:
    """Locator -> text of every unit line of a rendered document."""
    out = {}
    for line in (doc or '').splitlines():
        m = UNIT_RE.match(line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def extract(keys: list[str] | None = None) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import DATA, DERIVED, log, write_json, rel
    review = DATA / 'review'
    keys = keys or sorted(p.name for p in review.iterdir() if p.is_dir() and is_nature_folder(p))
    out, per = DERIVED / 'review' / 'nature_units_alt', {}
    out.mkdir(parents=True, exist_ok=True)
    for k in keys:
        doc, units, st = document(review / k)
        (out / f'{k}.txt').write_text(f'# Peer review file of {k}, units by tools/roadmap/nature_review.py\n{source_header(review / k)}\n{doc}')
        per[k] = st
        print(k, 'clean' if st['clean'] else 'NOT CLEAN', {x: st[x] for x in ('explicit_headers', 'rounds', 'referee_units', 'editor_units',
              'author_units_own', 'author_units_quoted', 'referee_units_in_authors_voice', 'author_own_units_in_referee_voice')})
    clean = sorted(k for k, v in per.items() if v['clean'])
    write_json(DERIVED / 'review' / 'nature_units_alt.json', {'papers': per, 'clean': clean,
               'not_clean': sorted(set(per) - set(clean))}, [rel(review) + '/<key>/*_MOESM*_ESM.pdf'],
               {'parser': PARSER_VERSION, 'quoted': QUOTED, 'short': SHORT, 'min_words': MIN_WORDS})
    log('nature_review.py extract', 'Nature Portfolio peer review files split into R/E/A units', len(per),
        f'{len(clean)} of {len(per)} clean (>= 1 referee unit and >= 1 own author unit)')
    print(f'{len(clean)} of {len(per)} clean')


ROLE = {'referee': 'R', 'editor': 'E', 'author': 'A'}


def compare(keys: list[str] | None = None) -> None:
    """Agreement of this reader with tools/roadmap/g27_nature_units.py: for every 8-word shingle both readers read, the
    (role, round) each gives it (first occurrence); and words per role and round of each reader."""
    from common import DATA, DERIVED, log, write_json, rel
    import g27_nature_units as g27n
    review = DATA / 'review'
    keys = keys or sorted(p.name for p in review.iterdir() if p.is_dir() and is_nature_folder(p) and g27n.is_nature(p.name))
    rows, tot = [], Counter()
    for k in keys:
        ua = g27n.nature_units(k)
        ub, _ = parse(source_files(review / k))
        la, lb, wa, wb = {}, {}, Counter(), Counter()
        for u in ua:
            wa[f"{u['source']}{u['round']}"] += len(u['text'].split())
            for s in shingles(norm(u['text']).split()):
                la.setdefault(s, (u['source'], u['round']))
        for u in ub:
            wb[f"{ROLE[u['role']]}{u['round']}"] += len(u['text'].split())
            for s in shingles(norm(u['text']).split()):
                lb.setdefault(s, (ROLE[u['role']], u['round']))
        both = set(la) & set(lb)
        same = sum(la[s] == lb[s] for s in both)
        rows.append({'key': k, 'shingles_g27n': len(la), 'shingles_alt': len(lb), 'shared': len(both), 'same_role_round': same,
                     'agreement': round(same / len(both), 3) if both else None, 'same_blocks': sorted(wa) == sorted(wb),
                     'units_g27n': len(ua), 'units_alt': len(ub), 'words_g27n': dict(wa), 'words_alt': dict(wb)})
        tot['shared'] += len(both)
        tot['same'] += same
        print(k, 'agreement', rows[-1]['agreement'], 'same blocks', rows[-1]['same_blocks'], 'units', len(ua), len(ub))
    pooled = round(tot['same'] / tot['shared'], 3) if tot['shared'] else None
    write_json(DERIVED / 'review' / 'nature_reader_agreement.json', {'pooled_agreement': pooled, 'papers': rows},
               [rel(review) + '/<key>/*.pdf'], {'g27_nature_units': g27n.VERSION, 'alt': PARSER_VERSION})
    log('nature_review.py compare', 'agreement of the two Nature peer-review-file readers (role and round per shingle)',
        len(rows), f'pooled {pooled}; g27_nature_units {g27n.VERSION} vs {PARSER_VERSION}; '
        f"{sum(r['same_blocks'] for r in rows)} of {len(rows)} with the same role-round blocks")
    print('pooled agreement', pooled)


if __name__ == '__main__':
    ks = sys.argv[sys.argv.index('--keys') + 1].split(',') if '--keys' in sys.argv else None
    if len(sys.argv) > 1 and sys.argv[1] == 'extract':
        extract(ks)
    elif len(sys.argv) > 1 and sys.argv[1] == 'compare':
        compare(ks)
    else:
        print(__doc__)
