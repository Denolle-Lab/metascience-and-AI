"""Units of a Nature-family peer review file (Nature Communications, NC; Communications Earth & Environment, CEE;
Nature), in the spirit of g27's AC and AR units: every referee paragraph and every paragraph of the authors' response
letters, with a stable locator, so the review request can carry the file and the validator can check disclosure quotes.

Why a separate module. g27_author_responses.py reads Copernicus author comments (AC) and author-response PDFs (AR), and
its sha256 is recorded in the frozen reconstruction plan (preregistration/reconstruction.json, RECORDED). This module
imports g27's text helpers (norm, shingles, sentences, classify, MIN_WORDS, DUP) and changes nothing in g27, so every
Copernicus unit, reading file and request stays byte-identical.

The file. A peer review file (review/<key>/<file>.pdf: g32 `prf` for the cop22 NC and CEE papers, g37 `fetch` for the
Nature Portfolio papers of rounds 1 and 2) is the journal's compilation of each review round: the referee reports (and
in CEE the editor's decision letter), then the authors' response letter to that round, appended as the authors
uploaded it; the last round's reports usually have no response. Text: pdftotext -layout per page (as g32 and g27 AR),
page 1 (licence) dropped. Two-column pages (1.2.0): some letters set each referee comment beside its reply in a
two-column table, and -layout then merges the two cells of a row into one line, often with a single space between
them ("3. Since the piezo sensors will be recording In fact, the piezometer is measuring ..."). A page is two-column
when its word boxes (pdftotext -bbox) show a gutter: an x between 30% and 75% of the page width at which at least
GUTTER_HITS lines have a word starting (with at least three words before it on the line), and those lines make at
least GUTTER_SCORE of the lines that either start a word there or have a word straddling it. Such a page is rebuilt
from its word boxes: each line split at the gutter, the left cells (the quoted comment) and the right cells (the
reply) of a table row emitted as separate paragraphs, left first; a line with a word straddling the gutter (a heading,
a full-width sentence) is kept whole. parse_result reports the pages rebuilt and two_column_share: the share of the
non-blank author-block lines that still carry the two-column signature after the rebuild (a gap of 5 or more spaces at
the page's shared column with at least three words on each side); N0 fails above TWO_COL_MAX.

Segmentation into blocks (role, round; round k = the k-th set of referee reports in file order)
  CEE   explicit markers: "Decision letter and referee reports: <ordinal> round" opens a referee block (the decision
        letter is editor text), "Author Responses: <ordinal> round" opens an author block. Round = the ordinal.
  Nature  explicit markers (1.1.0): "Reviewer Reports on the Initial Version" / "on the First Revision" ... opens a
        referee block of round 1 / 2 ..., "Author Rebuttals to Initial Comments" / "to First Revision" ... an author
        block of round 1 / 2 ... (NAT_REF, NAT_AUT).
  NC    no author marker. Page by page: a page whose first three lines hold a round header (REVIEWER COMMENTS,
        REVIEWERS' COMMENTS, Reviewers' comments) opens a referee block of the next round, unless at least SWITCH of
        its 8-word shingles are already in earlier referee text (the authors pasting the header into their letter).
        In a referee block, a page opens the author block of the same round when one of its first six lines starts
        with a strong response cue (CUE_STRONG: "Response to", "Reply", "Point-by-point", "Rebuttal", ...) or with a
        salutation (CUE_DEAR: "Dear Editor", "Dear Dr"; 1.1.0: only when the page speaks in the authors' voice, since
        a referee's report may open "Dear Editor, hereby I send you my review"), or one of its first two lines starts with an author's "We thank / We appreciate / We are pleased"
        (CUE_WE; 1.1.0 also "The authors thank") or holds "point by point" ("point-to-point", 1.1.0) or "response(s) to the reviewers" (CUE_ANY), or when at least SWITCH of its
        8-word shingles are earlier referee text and the rest of the page speaks in the authors' voice (voice(): we,
        our, us outnumber I, my and 'the authors'), the letter quoting the reports; a referee attachment repeating the
        report typed in the form overlaps too but speaks as a referee. Pages with fewer than MIN_SHINGLES shingles are
        decided by cues only. A canonical report header ("Reviewer #n (Remarks to the Author)") at the
        top of a page with low overlap opens a new referee round after an author block, or after a referee block in
        which reviewer n has already reported, unless n is the reviewer whose report is running (1.1.0: a header
        repeated at the top of each page of an attachment continues the report).
        Inside a referee page, a paragraph that starts with CUE_STRONG after at least one report opens the author block
        (letters that begin mid-page), and so does one that starts with CUE_DEAR or a response marker (RESP_MARK:
        "Response:", "Reply:", "Our response:"; 1.1.0) when the rest of the page speaks in the authors' voice and is not, for
        SWITCH or more of its 8-word shingles, text of an earlier author block (a later report quoting the authors).
Paragraphs  blank lines; a reviewer header line (also "Response to Reviewer #2", "Reply to the reviewer 1"); in author
        blocks an indentation change of >= 4 columns after a line ending a sentence (responses set off by indentation
        from the quoted comment). Page numbers alone on a line are dropped. A paragraph under MIN_WORDS words is merged
        into the next one of the same speaker (a header joins its text), the last one into the previous.
Units and locators
  R<n>-round<k> ¶m   referee #n, round k, paragraph m (referee text before any reviewer header of a NC block, and
                 the CEE decision letter, are editor text)
  E-round<k> ¶m  editor, round k ("Editor (Remarks to the Author)" in NC; the decision letter in CEE)
  A-round<k> ¶m  the authors' response letter to round k, paragraph m; 'answers' = the reviewer the letter's last
                 header named (or None). An A paragraph whose 8-word shingles are >= DUP inside earlier A paragraphs
                 is dropped (a later letter repeating an earlier answer), as g27 drops repeated AC replies.
  Every unit keeps its page ('PRF1 p.5'). The author document, for the quote checks, is every A unit of the paper.
Reading classes (analysis only; the request carries the units as they are): g27.classify over the A units, referee
  shingles from the R and E units, paper shingles from the published XML text when present. own_words = words of
  sentences classed own.
Parse result per paper: clean when it has at least one R unit and at least one A unit with own_words >= MIN_WORDS, and
two_column_share is at most TWO_COL_MAX (1.2.0).

Versions  1.0.0 (October 28, 2026): NC and CEE. 1.1.0 (October 28, 2026, before any Nature-family coding): Nature's
          explicit round markers; RESP_MARK inside a referee page; a salutation (CUE_DEAR) opens the
          authors' letter only in the authors' voice; a canonical header repeated by the running report continues it. Checked against a second, independent reader
          (tools/roadmap/nature_review.py, comparison only): on the 18 cop22 NC and CEE files the two assign the same
          role and round to 99.3% of the 8-word shingles both read under 1.0.0 (one paper at 92.9%: the round-1
          letter that starts "Response:" under the editor's remarks, which 1.1.0 reads as the authors').
          1.2.0 (October 28, 2026, before any Nature-family coding): two-column pages rebuilt from word boxes;
          two_column_share in the parse result, and the clean-parse test fails above TWO_COL_MAX.

Run:     python tools/roadmap/g27_nature_units.py extract [KEY ...]     units and parse result of every Nature folder
         (review/<key>/peer_review.txt present, no discussion.txt) to derived/review/nature_units.json; with keys,
         prints only (nothing written).
"""
from __future__ import annotations
import hashlib
import html
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from common import DATA, TODAY, log, rel, write_json
import g27_author_responses as g27

VERSION = '1.2.0'
REVIEW = DATA / 'review'
GOLD = DATA / 'pdfs' / 'gold'
OUT = DATA / 'derived' / 'review' / 'nature_units.json'
MIN_WORDS, DUP, SWITCH, INDENT = g27.MIN_WORDS, g27.DUP, 0.3, 4
ORD = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6}
CEE_REF = re.compile(r'^Decision letter and referee reports:\s*(\w+)\s+round', re.I)
CEE_AUT = re.compile(r'^Author Responses?:\s*(\w+)\s+round', re.I)
NAT_REF = re.compile(r'^Reviewer Reports on the (Initial Version|\w+ Revision)\s*:?\s*$', re.I)
NAT_AUT = re.compile(r'^Author Rebuttals? to (Initial Comments|\w+ Revision)\s*:?\s*$', re.I)
NAT_ORD = {'initial version': 1, 'initial comments': 1, 'first revision': 2, 'second revision': 3, 'third revision': 4,
           'fourth revision': 5, 'fifth revision': 6}
RESP_MARK = re.compile(r"^(?:response|reply|answer|our response|authors?['’]?s? (?:response|reply))\s*[:\-–]", re.I)
ROUND = re.compile(r"^(?:REVIEWERS?['’]?\s+COMMENTS|Reviewers?['’]?\s+[Cc]omments|Reviewer Comments)\s*(?::|</B>)?\s*$")
REV_CANON = re.compile(r'^Reviewer\s*#?\s*(\d+)\s*:?\s*\(?Remarks to the Author\)?', re.I)
REV_HDR = re.compile(r'^(?:Reviewer|REVIEWER|Referee|REFEREE)\s*#?\s*(\d+)\b')
EDITOR_HDR = re.compile(r'^Editor\s*\(Remarks', re.I)
RESP_HDR = re.compile(r'^(?:Response|Responses|Reply|Replies|Answer)s?\b[^.]{0,40}?\b(?:reviewer|referee)\s*#?\s*(\d+)', re.I)
CUE_STRONG = re.compile(r"^(?:responses? to (?:the )?(?:reviewers?|referees?|editor|comments)|repl(?:y|ies)\b|point[- ]by[- ]point|"
                        r"rebuttal|authors?['’]?s? (?:response|reply)|our (?:point|response))", re.I)
CUE_DEAR = re.compile(r'^dear (?:editors?|dr|prof|professor)\b', re.I)
CUE_WE = re.compile(r'^(?:the authors (?:thank|are grateful|appreciate)|we (?:would like to |sincerely |really |are (?:pleased|grateful|very grateful)|thank|appreciate|have (?:revised|addressed)))', re.I)
CUE_ANY = re.compile(r'point[- ](?:by|to)[- ]point|responses? to (?:the )?reviewers|replies to the reviewers', re.I)
MIN_SHINGLES = 40   # a page with fewer 8-word shingles is too short for the overlap rule (cues only)
GUTTER_HITS, GUTTER_SCORE, GUTTER_SPAN, TWO_COL_MAX = 6, 0.65, (0.30, 0.75), 0.15   # two-column pages (1.2.0)
WORD = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>')
TWO_COL_GAP = re.compile(r' {5,}(?=\S)')
FURN = re.compile(r'^(?:\d{1,3}|Page \d+( of \d+)?|\[link redacted\])$', re.I)
NOTICE = re.compile(r'Web links to the author.s journal account have been redacted|to maintain confidentiality\.?$', re.I)


def is_nature(key: str, review: Path = REVIEW) -> bool:
    """A Nature-family review folder: a peer review file (g32 `prf`, g37 `fetch`) and no Copernicus discussion."""
    d = Path(review) / key
    return (d / 'peer_review.txt').is_file() and not (d / 'discussion.txt').is_file() and any(d.glob('*.pdf'))


def prf_files(key: str, review: Path = REVIEW) -> list[Path]:
    return sorted((Path(review) / key).glob('*.pdf'))


def _pages(f: Path) -> list[str]:
    """Page texts of a PDF: pdftotext -layout, except two-column pages, rebuilt from word boxes (_rebuild)."""
    pages = subprocess.run(['pdftotext', '-layout', str(f), '-'], capture_output=True, text=True).stdout.split('\f')
    for i, (width, words) in enumerate(_boxes(f)):
        if i < len(pages) and (x := _gutter(_rows(words), width)) is not None:
            pages[i] = _rebuild(_rows(words), x)
    return pages


def two_column_pages(f: Path) -> list[int]:
    """Pages (1-based) of a PDF that _pages rebuilds as two-column."""
    return [i for i, (width, words) in enumerate(_boxes(f), 1) if _gutter(_rows(words), width) is not None]


def _boxes(f: Path) -> list[tuple[float, list[tuple]]]:
    """Word boxes per page (pdftotext -bbox): (page width, [(xMin, yMin, xMax, yMax, word), ...])."""
    out = subprocess.run(['pdftotext', '-bbox', str(f), '-'], capture_output=True, text=True).stdout
    res = []
    for chunk in out.split('<page ')[1:]:
        m = re.match(r'width="([\d.]+)"', chunk)
        res.append((float(m.group(1)) if m else 612.0,
                    [(float(a), float(b), float(c), float(d), html.unescape(t)) for a, b, c, d, t in WORD.findall(chunk)]))
    return res


def _rows(words: list[tuple]) -> list[tuple[float, list[tuple]]]:
    """Words grouped into lines by top edge (within 2.5 pt), each line sorted left to right: [(y, [(x0, x1, w)])]."""
    rows: list = []
    for x0, y0, x1, _, t in sorted(words, key=lambda w: (w[1], w[0])):
        if rows and abs(rows[-1][0] - y0) < 2.5:
            rows[-1][1].append((x0, x1, t))
        else:
            rows.append((y0, [(x0, x1, t)]))
    return [(y, sorted(ws)) for y, ws in rows]


def _starts_at(ws: list[tuple], x: float) -> int | None:
    """Index of the word of a line that starts at x (within 1.5 pt) after a gap, with at least three words before it."""
    return next((i for i, w in enumerate(ws) if i >= 3 and abs(w[0] - x) <= 1.5 and w[0] - ws[i - 1][1] > 1.0), None)


def _gutter(rows: list, width: float) -> float | None:
    """x of the column gutter of a two-column page, or None (rule in the module docstring)."""
    cand = Counter(round(ws[i][0]) for _, ws in rows for i in range(3, len(ws))
                   if ws[i][0] - ws[i - 1][1] > 1.0 and GUTTER_SPAN[0] * width < ws[i][0] < GUTTER_SPAN[1] * width)
    best = None
    for x, _ in cand.most_common(8):
        hit = sum(_starts_at(ws, x) is not None for _, ws in rows)
        strad = sum(_starts_at(ws, x) is None and any(w[0] < x - 1.5 and w[1] > x + 1.5 for w in ws) for _, ws in rows)
        score = hit / (hit + strad) if hit + strad else 0.0
        if hit >= GUTTER_HITS and score >= GUTTER_SCORE and (best is None or score > best[0]):
            best = (score, x)
    return best and best[1]


def _rebuild(rows: list, x: float) -> str:
    """Text of a two-column page: per table row, the left cell's lines, a blank line, the right cell's lines, a blank
    line. A row starts where both columns start a line and each column's previous line ended a sentence (or the column
    was empty); a line with a word straddling x is kept whole between rows. Within a column, a vertical gap of more than
    1.6 line pitches is a paragraph break."""
    pitch = sorted(b[0] - a[0] for a, b in zip(rows, rows[1:]) if b[0] > a[0]) or [12.0]
    gap = 1.6 * pitch[len(pitch) // 2]
    out: list[str] = []
    cols: dict = {'L': [], 'R': []}

    def flush():
        for side in ('L', 'R'):
            prev = None
            for y, t in cols[side]:
                if prev is not None and y - prev > gap:
                    out.append('')
                out.append(t)
                prev = y
            if cols[side]:
                out.append('')
            cols[side] = []

    for y, ws in rows:
        if any(w[0] < x - 1.5 and w[1] > x + 1.5 for w in ws):
            flush()
            out.append(' '.join(w[2] for w in ws))
            continue
        left = ' '.join(w[2] for w in ws if w[0] < x - 1.5)
        right = ' '.join(w[2] for w in ws if w[0] >= x - 1.5)
        if left and right and cols['L'] and cols['R'] and _ends_sentence(cols['L'][-1][1]) and _ends_sentence(cols['R'][-1][1]):
            flush()
        if left:
            cols['L'].append((y, left))
        if right:
            cols['R'].append((y, right))
    flush()
    return '\n'.join(out)


def _two_column_lines(lines: list[str]) -> int:
    """Lines of one page that carry the -layout two-column signature: a gap of 5 or more spaces with at least three
    words on each side, at the page's most shared column (within 3)."""
    starts = []
    for l in lines:
        cs = [m.end() for m in TWO_COL_GAP.finditer(l)
              if len(l[:m.start()].split()) >= 3 and len(l[m.end():].split()) >= 3]
        starts.append(cs)
    allc = Counter(c for cs in starts for c in cs)
    if not allc:
        return 0
    best = max(allc, key=lambda c: sum(v for k, v in allc.items() if abs(k - c) <= 3))
    return sum(any(abs(c - best) <= 3 for c in cs) for cs in starts)


def voice(text: str, ref_sh: set) -> int:
    """Author voice of the sentences of a page that are not earlier referee text: first person plural (we, our, us)
    minus first person singular (I, my) and 'the authors'. Positive on response letters, negative on reports."""
    own = ' '.join(x for x in g27.sentences(text) if (sh := g27.shingles(g27.norm(x).split())) and len(sh & ref_sh) / len(sh) < 0.5)
    return (len(re.findall(r'\b(?:we|our|us)\b', own, re.I)) - len(re.findall(r'\b(?:I|my)\b', own))
            - len(re.findall(r'\bthe authors\b', own, re.I)))


def _ends_sentence(s: str) -> bool:
    return bool(re.search(r'[.:?!”"\)]\s*$', s))


def blocks(key: str, review: Path = REVIEW) -> list[dict]:
    """Referee and author blocks in file order: {'role': 'ref'|'aut', 'round': k, 'lines': [(page, line), ...]}."""
    pages = []
    for i, f in enumerate(prf_files(key, review), 1):
        for n, pg in enumerate(_pages(f), 1):
            if n == 1 and 'Creative Commons' in pg:
                continue
            pages.append((f'PRF{i} p.{n}', pg.splitlines()))
    explicit = any(CEE_REF.match(l.strip()) or NAT_REF.match(l.strip()) for _, ls in pages for l in ls)
    out: list[dict] = []
    cur = None

    def new(role, rnd):
        nonlocal cur
        cur = {'role': role, 'round': rnd, 'lines': [], 'seen': set()}
        out.append(cur)

    if explicit:   # CEE and Nature: the file names each block and its round
        for pg, ls in pages:
            for l in ls:
                s = l.strip()
                last = max((b['round'] for b in out), default=0)
                if (m := CEE_REF.match(s) or CEE_AUT.match(s)):
                    ref = bool(CEE_REF.match(s))
                    new('ref' if ref else 'aut', ORD.get(m.group(1).lower(), last + (1 if ref else 0)))
                    continue
                if (m := NAT_REF.match(s) or NAT_AUT.match(s)):
                    ref = bool(NAT_REF.match(s))
                    new('ref' if ref else 'aut', NAT_ORD.get(m.group(1).lower(), last + (1 if ref else 0)))
                    continue
                if cur is not None:
                    cur['lines'].append((pg, l))
        return out
    ref_sh: set = set()
    aut_sh: set = set()
    rnd = 0
    for pg, ls in pages:
        nb = [l.strip() for l in ls if l.strip() and not FURN.match(l.strip())]
        if not nb:
            continue
        sh = g27.shingles(g27.norm(' '.join(nb)).split())
        ov = len(sh & ref_sh) / len(sh) if len(sh) >= MIN_SHINGLES else 0.0
        head = nb[:6]
        canon = REV_CANON.match(head[0])
        if any(ROUND.match(h) for h in head[:3]) and ov < SWITCH:
            rnd += 1
            new('ref', rnd)
        elif cur is None:
            rnd = 1
            new('ref', rnd)
        elif cur['role'] == 'ref' and (any(CUE_STRONG.match(h) for h in head) or any(CUE_WE.match(h) or CUE_ANY.search(h) for h in head[:2])
                                       or ((ov >= SWITCH or any(CUE_DEAR.match(h) for h in head)) and voice(' '.join(nb), ref_sh) > 0)):
            new('aut', rnd)
        elif canon and ov < SWITCH and (cur['role'] == 'aut' or (int(canon.group(1)) in cur['seen']
                                                                 and int(canon.group(1)) != cur.get('last'))):
            rnd += 1
            new('ref', rnd)
        prev_blank = True
        for i, l in enumerate(ls):
            s = l.strip()
            if cur['role'] == 'ref':
                if (m := REV_HDR.match(s)) and len(s) < 80:
                    cur['seen'].add(int(m.group(1)))
                    cur['last'] = int(m.group(1))
                elif prev_blank and cur['seen'] and cur['lines'] and (
                        CUE_STRONG.match(s) or ((RESP_MARK.match(s) or CUE_DEAR.match(s)) and _authors_rest(ls[i:], ref_sh, aut_sh))):
                    new('aut', rnd)
            cur['lines'].append((pg, l))
            prev_blank = not s
        if cur['role'] == 'ref':
            ref_sh |= sh
        else:
            aut_sh |= sh
    return out


def _authors_rest(lines: list[str], ref_sh: set, aut_sh: set) -> bool:
    """The rest of a page from a response marker on is the authors' letter: authors' voice (voice()), and under SWITCH
    of its 8-word shingles in earlier author blocks (else a later report quoting the authors' earlier letter)."""
    t = ' '.join(x.strip() for x in lines if x.strip())
    sh = g27.shingles(g27.norm(t).split())
    if sh and len(sh & aut_sh) / len(sh) >= SWITCH:
        return False
    return voice(t, ref_sh) > 0


def paragraphs(b: dict) -> list[dict]:
    """Paragraphs of a block with their speaker: {'who': 'R<n>'|'E'|'A', 'answers': n|None, 'page', 'text'}."""
    paras, cur, prev = [], [], None
    who = 'E' if b['role'] == 'ref' else 'A'
    answers = None

    def flush():
        nonlocal cur
        if cur:
            paras.append({'who': who, 'answers': answers if b['role'] == 'aut' else None, 'page': cur[0][0],
                          'text': re.sub(r'\s+', ' ', ' '.join(s for _, s in cur)).strip()})
        cur = []

    for pg, l in b['lines']:
        s = l.strip()
        if not s:
            flush()
            prev = None
            continue
        if FURN.match(s) or NOTICE.search(s):
            continue
        ind = len(l) - len(l.lstrip())
        hdr = REV_HDR.match(s) if len(s) < 80 else None
        resp = RESP_HDR.match(s) if len(s) < 100 else None
        if b['role'] == 'ref' and (hdr or EDITOR_HDR.match(s)):
            flush()
            who = f'R{int(hdr.group(1))}' if hdr else 'E'
        elif b['role'] == 'aut' and (hdr or resp):
            flush()
            answers = int((hdr or resp).group(1))
        elif b['role'] == 'aut' and prev is not None and abs(ind - prev[0]) >= INDENT and _ends_sentence(prev[1]):
            flush()
        cur.append((pg, s))
        prev = (ind, s)
    flush()
    # merge short paragraphs into the next of the same speaker (headers join their text), the last into the previous
    out, short = [], None

    def settle():   # a short paragraph with no next paragraph of its speaker joins the previous one, else is dropped
        if short is not None and out and out[-1]['who'] == short['who']:
            out[-1]['text'] += ' ' + short['text']

    for p in paras:
        if short is not None:
            if short['who'] == p['who']:
                p = {**p, 'page': short['page'], 'text': short['text'] + ' ' + p['text']}
            else:
                settle()
            short = None
        if len(p['text'].split()) < MIN_WORDS:
            short = p
        else:
            out.append(p)
    settle()
    return out


def nature_units(key: str, review: Path = REVIEW) -> list[dict]:
    """Every unit of the paper's peer review file, in file order, with its locator."""
    units, count, seen = [], Counter(), set()
    for b in blocks(key, review):
        k = b['round']
        for p in paragraphs(b):
            if p['who'] == 'A':
                sh = g27.shingles(g27.norm(p['text']).split())
                if sh and len(sh & seen) / len(sh) >= DUP:
                    continue
                seen |= sh
            tag = f"{p['who']}-round{k}"
            count[tag] += 1
            units.append({'key': key, 'unit': f'{tag} ¶{count[tag]}', 'source': p['who'][0], 'round': k,
                          'reviewer': int(p['who'][1:]) if p['who'].startswith('R') else None,
                          'answers': p['answers'], 'page': p['page'], 'text': p['text']})
    return units


def document(key: str, units: list[dict], review: Path = REVIEW) -> str:
    """The text a review request carries: a two-line legend and one [locator] line per unit."""
    files = ', '.join(f.name for f in prf_files(key, review))
    return (f'# Peer review file of {key} ({files}), split into units by role and round (g27_nature_units {VERSION})\n'
            '# [R<n>-round<k> ¶m] referee #n in review round k; [E-round<k> ¶m] editor in round k; [A-round<k> ¶m] the '
            'authors\' response letter to round k\n' + ''.join(f'[{u["unit"]}] {u["text"]}\n' for u in units))


def source_hashes(key: str, review: Path = REVIEW) -> str:
    return ' '.join(f'{p.name}={hashlib.sha256(p.read_bytes()).hexdigest()[:16]}' for p in prf_files(key, review))


def layout_stats(key: str, review: Path = REVIEW) -> dict:
    """Two-column pages rebuilt (per PDF) and two_column_share: author-block lines that still carry the two-column
    signature after the rebuild, over the non-blank author-block lines."""
    rebuilt = {f.name: two_column_pages(f) for f in prf_files(key, review)}
    by_page: dict = {}
    for b in blocks(key, review):
        if b['role'] == 'aut':
            for pg, l in b['lines']:
                if l.strip():
                    by_page.setdefault(pg, []).append(l)
    n = sum(len(v) for v in by_page.values())
    hit = sum(_two_column_lines(v) for v in by_page.values())
    return {'two_column_pages_rebuilt': {k: v for k, v in rebuilt.items() if v}, 'author_lines': n,
            'two_column_lines_left': hit, 'two_column_share': round(hit / n, 4) if n else 0.0}


def parse_result(key: str, units: list[dict], review: Path = REVIEW) -> dict:
    """Own-text classes of the A units (g27.classify), the two-column check (layout_stats) and the clean-parse test."""
    ref = g27.shingles(g27.norm(' '.join(u['text'] for u in units if u['source'] in ('R', 'E'))).split())
    x = GOLD / f'{key}.xml.txt'
    paper = g27.shingles(g27.norm(x.read_text()).split()) if x.is_file() else set()
    au = [dict(u) for u in units if u['source'] == 'A']
    g27.classify(au, ref, paper)
    own = [sum(len(s['s'].split()) for s in u['sents'] if s['class'] == 'own') for u in au]
    words = lambda src: sum(len(u['text'].split()) for u in units if u['source'] == src)
    r = {'key': key, 'rounds': max((u['round'] for u in units), default=0),
         'rounds_with_response': len({u['round'] for u in units if u['source'] == 'A'}),
         'R_units': sum(u['source'] == 'R' for u in units), 'E_units': sum(u['source'] == 'E' for u in units),
         'A_units': len(au), 'A_units_with_own_text': sum(o >= MIN_WORDS for o in own),
         'reviewers': sorted({u['reviewer'] for u in units if u['reviewer']}),
         'words': {'R': words('R'), 'E': words('E'), 'A': words('A'), 'A_own': sum(own)},
         'A_quoted_referee_words': sum(len(s['s'].split()) for u in au for s in u['sents'] if s['class'] == 'quoted_referee')}
    r.update(layout_stats(key, review))
    r['clean'] = r['R_units'] >= 1 and r['A_units_with_own_text'] >= 1 and r['two_column_share'] <= TWO_COL_MAX
    r['problem'] = (None if r['clean'] else 'no referee unit' if not r['R_units'] else 'no author unit with own text'
                    if r['A_units_with_own_text'] < 1 else f"two-column share {r['two_column_share']} above {TWO_COL_MAX}")
    return r


def extract(keys: list[str]) -> None:
    write = not keys
    keys = keys or sorted(p.name for p in REVIEW.iterdir() if is_nature(p.name))
    rows, allu = [], {}
    for k in keys:
        u = nature_units(k)
        allu[k] = u
        rows.append(parse_result(k, u))
    for r in rows:
        print(f"{r['key']} rounds {r['rounds']} (with response {r['rounds_with_response']}) R {r['R_units']} E {r['E_units']} "
              f"A {r['A_units']} (own {r['A_units_with_own_text']}) words R {r['words']['R']} A {r['words']['A']} "
              f"own {r['words']['A_own']} 2col {r['two_column_share']} rebuilt {r['two_column_pages_rebuilt'] or '-'} "
              f"{'clean' if r['clean'] else 'FAIL: ' + r['problem']}")
    n = sum(r['clean'] for r in rows)
    print(f'{n} of {len(rows)} parse cleanly')
    if write:
        write_json(OUT, {'version': VERSION, 'papers': rows, 'clean': n, 'units': allu},
                   [rel(REVIEW) + '/<key>/*.pdf'], {'min_words': MIN_WORDS, 'dup': DUP, 'switch': SWITCH, 'indent': INDENT,
                                                     'gutter_hits': GUTTER_HITS, 'gutter_score': GUTTER_SCORE,
                                                     'gutter_span': list(GUTTER_SPAN), 'two_col_max': TWO_COL_MAX})
        log('g27_nature_units.py extract', 'Nature-family peer review files split into R, E and A units', len(rows),
            f'{n} of {len(rows)} parse cleanly (>= 1 R unit and >= 1 A unit with own text); {sum(len(v) for v in allu.values())} units')


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] != 'extract':
        print(__doc__)
        sys.exit(2)
    extract(sys.argv[2:])
