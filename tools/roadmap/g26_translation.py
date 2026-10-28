"""Section-level change from submission to publication for the Copernicus (EGU) papers with an open review record.

Direction from the PI (October 28, 2026): papers are not written the way the science is done (framing is often written
last), and they follow recipes. The open review record of the Copernicus journals keeps the submitted manuscript (the
discussion preprint) next to the published paper, so one step of the translation, submission to publication, can be
measured section by section.

fetch    For each paper of derived/review/open_review_index.json with an open discussion (61 papers), make sure the
         discussion preprint is on disk. g15 stored the review files but not the preprint itself. The preprint is the
         PDF that the article's Copernicus discussion page links as preprints/[YYYY/]<stem>/<stem>.pdf, where <stem> is
         the preprint DOI suffix (10.5194/<stem>); when the preprint DOI is not a Copernicus DOI (an arXiv preprint), the
         stem is the prefix of the manuscript-version files g15 stored. The discussion page is reached through
         https://doi.org/<preprint DOI> (Copernicus redirects it to <article>-discussion.html), else through the article
         DOI plus -discussion.html. When the discussion page links no preprint PDF and the preprint DOI is an arXiv
         DOI, the preprint is version 1 of that arXiv record (https://arxiv.org/pdf/<id>v1). Pause 1.5 s before
         every request. The page is saved verbatim under
         raw/copernicus/<key>-discussion.html, the PDF as review/<key>/<stem>.pdf, and every fetch (URL, date, bytes,
         sha256, status) in derived/translation/preprint_fetch.json.
analyze  Compares, per paper, the earliest manuscript with the published text.
         Versions  submitted = the discussion preprint (review/<key>/<stem>.pdf) if on disk, else the lowest
                   manuscript-version PDF g15 stored (a revised manuscript, so the change is under-counted; flagged).
                   published = the publisher XML text pdfs/gold/<key>.xml.txt (sections marked "§n Title", paragraphs
                   "[§n ¶k]", figure and table captions on their own lines); else the final PDF.
                   Control  = the final PDF (pdfs/gold/<key>.pdf) parsed exactly like a submitted PDF and compared with
                   the XML text: same words, different extraction. Its change share is the noise floor of the method.
         Text      pdftotext without -layout. Dropped: running heads and preprint banners, standalone numbers (margin
                   line numbers, page numbers, table cells), text blocks that start with "Figure n" or "Table n"
                   (captions), sentences with fewer than 4 word tokens or under half alphabetic tokens (equations,
                   tables). Normalization for matching on both sides: NFKC, lower case, author-year citations removed
                   (the publisher XML text has them removed; bare "Author et al., 2020" too), figure, table,
                   equation and section references removed, line-break hyphenation joined, other hyphens split
                   (copy editing drops hyphens: "dynamically-limited" / "dynamically limited"), British spellings
                   mapped to American (-our, -ise, -yse, -tre; copy editing changes them), tokens [a-z]+ and
                   numbers.
         Sections  PDF: a heading is a short title-like line (1 to 14 words, starts upper case, no final period, at
                   least 70% alphabetic tokens) whose section number, on the same line or on a standalone number line
                   just before it (pdftotext separates them), is a valid successor of the current number (next at
                   some level, or first child). The successor rule is what discards margin line numbers (5, 10, 15 ...)
                   that pdftotext interleaves. "Abstract" opens the abstract; "Appendix X" opens an appendix; Data/Code
                   availability, Author contributions, Competing interests, Acknowledgements, References and similar
                   run-in headings open back matter. XML: the "§" lines. Top-level titles are mapped to a canonical
                   section (CANON below: abstract, introduction, data_methods, results, results_discussion,
                   discussion, conclusions); subsections inherit. A title matching no rule is "unmatched" and kept
                   out of the main comparison; a positional rule (after the introduction and before the first
                   results-type section: data_methods; between results and discussion: results) is a sensitivity
                   analysis. Every unmatched title is listed in the output.
         Alignment Sentences split at . ! ? before an upper-case letter or parenthesis, abbreviations protected.
                   For each published sentence, the 8 submitted sentences sharing the most distinct content tokens
                   (anywhere in the submitted body) are candidates. Similarity s (primary) = coverage: the share of
                   the published sentence's tokens matched, in order, by difflib matching blocks of at least 2 tokens
                   within the window of three submitted sentences centred on a candidate; the best window counts.
                   Coverage was chosen over the sentence-to-sentence difflib ratio on the control alone (below):
                   its noise floor is lower (2% of sentences against 5% on the 61 control papers, mean over
                   papers), because table text and equations break PDF sentences and the ratio penalizes the break.
                   (The ratio had been tried on two papers' submitted-to-published comparisons while the parser was
                   built; no group comparison had been run.) The ratio (2M/T, also tried against the joins of a candidate with
                   its neighbors) is kept as a sensitivity analysis. A published sentence is kept when s >= 0.8,
                   substantially changed when 0.4 <= s < 0.8, new when s < 0.4. "Changed share" of a section = share
                   of its published sentences with s < 0.8 (new or substantially changed). Thresholds 0.7 and 0.9
                   are reported as sensitivity. "Dropped share" = the same in the other direction (submitted
                   sentences with coverage < 0.8 in the published text).
         Per section length ratio = published tokens / submitted tokens (kept sentences only, after the filters);
                   restructured = any of: section absent in the submitted version; a published subsection title
                   added or renamed (not present as a phrase anywhere in the submitted text, and no submitted
                   heading within difflib ratio 0.8; checking the text, not only parsed headings, keeps parser misses
                   out; removed subsections are not counted here, the dropped share covers them);
                   >= 20% of the kept sentences come from another canonical section (moved in); kept sentences
                   reordered (Spearman correlation of submitted and published positions < 0.9, at least 5 kept).
         Tests     Paired across papers, numpy only. Framing = abstract + introduction, workflow = data_methods +
                   results (results_discussion counted in workflow; a sensitivity drops it). Per paper the pooled
                   changed share of each group (sentences pooled within the group); papers with both groups enter.
                   Two-sided sign-flip permutation test of the mean paired difference (20000 flips,
                   np.random.default_rng(2026)); effect sizes: mean and median difference, and dz (mean / SD of the
                   differences), with 95% percentile bootstrap intervals over papers (5000 resamples, same generator).
                   The same test on the log2 length ratio, on the restructured flag, on the floor-corrected share
                   (share minus the control share of the same paper and group), and for each section pair.
         Gap       The paper's gap statement is the entry evidence quote of its calc1 coding
                   (private/analysis/codings/api/calc1/<key>.json, entry.evidence; read only). Coverage of the
                   quote's tokens by matching blocks of 2 or more tokens (difflib) against the best window of three
                   consecutive sentences. Located in the published text when coverage >= 0.9. In the submitted text:
                   same >= 0.9, changed 0.5 to 0.9, absent < 0.5 (appears only in the published version). The canonical
                   section of the best window is recorded in both versions.

Inputs   derived/review/open_review_index.json (g15); review/<key>/*.pdf; pdfs/gold/<key>.xml.txt and .pdf;
         private/analysis/codings/api/calc1/<key>.json (entry.evidence only)
Outputs  derived/translation/preprint_fetch.json (fetch); derived/translation/sections.json and SECTIONS.md
         (analyze); one MANIFEST.md line per run
Run:     python tools/roadmap/g26_translation.py fetch
         python tools/roadmap/g26_translation.py fetch --index private/data/roadmap/derived/review/open_review_index_r2.json \
                --record preprint_fetch_r2.json      (another g15 index; the fetch record gets its own name)
         python tools/roadmap/g26_translation.py analyze
"""
from __future__ import annotations
import difflib
import hashlib
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from common import DATA, DERIVED, PRIVATE, TODAY, log, read_json, rel, write_json

UA = {'User-Agent': 'Mozilla/5.0 (metascience seminar, University of Washington)'}
PAUSE = 1.5
REVIEW = DATA / 'review'
GOLD = DATA / 'pdfs' / 'gold'
RAWC = DATA / 'raw' / 'copernicus'
OUT = DERIVED / 'translation'
CALC1 = PRIVATE / 'analysis' / 'codings' / 'api' / 'calc1'
INDEX = DERIVED / 'review' / 'open_review_index.json'

KEEP, NEW = 0.8, 0.4          # sentence similarity thresholds (kept >= KEEP; new < NEW)
SENS = (0.7, 0.9)             # sensitivity thresholds for the changed share
NCAND = 8                     # candidate submitted sentences per published sentence
MOVED_MIN, ORDER_MIN = 0.2, 0.9
WINDOW, SKIP = 6, 3         # heading parser: number lines within 6 lines before a title; a skipped top-level number costs 3
UNNUMBERED = 1.5           # a canonical title found without a number line in reach weighs 1.5 less
MINGAP, GAPCOST = 8, 3      # a sibling or higher-level heading fewer than 8 lines after the previous one (table rows) costs 3
GAP_SAME, GAP_CHANGED = 0.9, 0.5
NPERM, NBOOT, SEED = 20000, 5000, 2026
FRAMING = ('abstract', 'introduction')
WORKFLOW = ('data_methods', 'results', 'results_discussion')
ORDER = ('abstract', 'introduction', 'data_methods', 'results', 'results_discussion', 'discussion', 'conclusions')


# ---------------------------------------------------------------- fetch

def get(url, binary=False):
    time.sleep(PAUSE)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
        return (data if binary else data.decode('utf-8', 'replace')), r.geturl()


def papers(index=None):
    return [r for r in read_json(index or INDEX) if 'comments' in r]


def preprint_stem(r) -> str:
    pre = r.get('preprint_doi') or ''
    if pre.lower().startswith('10.5194/'):
        return pre.split('/', 1)[1]
    mv = [f for f in r.get('files', []) if '-manuscript-version' in f]
    return mv[0].split('-manuscript-version')[0] if mv else ''


def fetch(index=None, record='preprint_fetch.json'):
    RAWC.mkdir(parents=True, exist_ok=True)
    recs = []
    old = {r['key']: r for r in read_json(OUT / record)} if (OUT / record).is_file() else {}
    for r in papers(index):
        key, stem = r['key'], preprint_stem(r)
        target = REVIEW / key / f'{stem}.pdf'
        rec = {'key': key, 'doi': r['doi'], 'preprint_doi': r.get('preprint_doi'), 'stem': stem,
               'file': rel(target)}
        if target.is_file():
            sha = hashlib.sha256(target.read_bytes()).hexdigest()
            if old.get(key, {}).get('sha256') == sha and old[key].get('url'):
                recs.append(old[key]); print(key, 'on disk, record kept'); continue
            rec.update(bytes=target.stat().st_size, sha256=sha)
            page = RAWC / f'{key}-discussion.html'
            m = re.search(r'(https://[^"\s#]+/preprints/(?:\d{4}/)?' + re.escape(stem) + '/' + re.escape(stem) + r'\.pdf)',
                          page.read_text()) if page.is_file() else None
            if m:
                # an earlier run of this script fetched it: rebuild the record from the saved page and the file date
                rec.update(status='fetched', url=m.group(1), page_file=rel(page),
                           fetched=time.strftime('%Y-%m-%d', time.localtime(target.stat().st_mtime)),
                           note='record rebuilt from the saved discussion page')
            else:
                rec['status'] = 'on disk'
            recs.append(rec); print(key, rec['status']); continue
        try:
            if (r.get('preprint_doi') or '').lower().startswith('10.5194/'):
                page, url = get('https://doi.org/' + r['preprint_doi'])
            else:
                _, land = get('https://doi.org/' + r['doi'])
                url = land.rstrip('/') + '/' + r['doi'].split('/', 1)[1] + '-discussion.html'
                page, url = get(url)
            (RAWC / f'{key}-discussion.html').write_text(page)
            rec['page_url'] = url
            rec['page_file'] = rel(RAWC / f'{key}-discussion.html')
            m = re.search(r'(https://[^"\s#]+/preprints/(?:\d{4}/)?' + re.escape(stem) + '/' + re.escape(stem) + r'\.pdf)', page)
            arx = re.match(r'10\.48550/arxiv\.(.+)$', (r.get('preprint_doi') or '').lower())
            if m:
                rec['url'] = m.group(1)
            elif arx:
                # the discussion preprint is an arXiv record (the discussion page links no PDF): its first version
                rec['url'] = f'https://arxiv.org/pdf/{arx.group(1)}v1'
                rec['note'] = 'no preprint PDF on the discussion page; arXiv preprint DOI, version 1'
            else:
                rec['status'] = 'no preprint link on the discussion page'
                recs.append(rec); print(key, rec['status']); continue
            data, _ = get(rec['url'], binary=True)
            if data[:4] != b'%PDF':
                rec['status'] = 'not a PDF'
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                rec.update(status='fetched', fetched=TODAY, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        except Exception as e:  # noqa: BLE001
            rec['status'] = f'error: {type(e).__name__}: {e}'
        recs.append(rec)
        print(key, rec['status'])
    write_json(OUT / record, recs, [rel(index or INDEX), 'Copernicus discussion pages (doi.org redirect)'],
               {'pause_s': PAUSE, 'user_agent': UA['User-Agent']})
    st = Counter(r['status'] if not r['status'].startswith('error') else 'error' for r in recs)
    log('g26_translation.py fetch', f'discussion preprints of the open-review papers (Copernicus, {rel(index or INDEX)})', len(recs),
        dict(st).__repr__())


# ---------------------------------------------------------------- text extraction and sections

DROP_LINE = [re.compile(p) for p in (
    r'^https?://doi\.org/10\.5194/\S+$',
    r'^Preprint\. Discussion started',
    r'^Discussion started:',
    r'^(c|©|\(c\))\s*Author\(s\) \d{4}',
    r'CC BY 4\.0 License\.?$',
    r'^the Creative Commons Attribution 4\.0 License',
    r'^Published by Copernicus Publications',
    r'^[A-Z][A-Za-z.\-’\' ]{0,40} et al\.: ',                 # running head of the typeset article
    r'^[A-Z][A-Za-z .&:\-]+, \d+, \d+[–-]\d+, \d{4}$',       # journal, volume, pages, year
    r'^Received: \d', r'^Revised: \d', r'^Correspondence: ', r'^Open Access\b',    # Copernicus logo text
)]
CAPTION = re.compile(r'^(Figure|Fig\.|Table)\s*[A-Z]?\d+[a-z]?\s*[.:|]')
NUMLINE = re.compile(r'\d{1,2}(\.\d{1,2}){0,3}\.?')
INLINE_HEAD = re.compile(r'^(\d{1,2}(?:\.\d{1,2}){0,3})\.?\s+(\S.*)$')
BACK = re.compile(r'^(Code availability|Data availability|Code and data availability|Data and code availability|'
                  r'Software availability|Sample availability|Video supplement|Supplement|Author contributions|'
                  r'Competing interests|Disclaimer|Special issue statement|Acknowledgements|Acknowledgments|'
                  r'Acknowledgement|Financial support|Review statement|References|Bibliography)(\.|$)\s*')
APPENDIX = re.compile(r'^Appendix\s+([A-Z])\b[:.]?\s*(.*)$')


def heading_like(s: str) -> bool:
    """A short title-like line. Single-word titles count only when they name a canonical section (figure labels
    such as "Date" or "HV" sit on their own lines in pdftotext output); all-caps short lines are figure text."""
    w = s.split()
    if not 1 <= len(w) <= 14 or len(s) > 120 or not s[0].isupper() or s[-1] in '.,;':
        return False
    if re.search(r'\(\D*\d{4}', s) or re.search(r'[=\[_*@#\\]', s) or s.startswith('The supplement'):
        return False
    if sum(bool(re.match(r'[A-Za-z]', t)) for t in w) / len(w) < 0.7:
        return False
    if len(w) == 1 and canon(s) in ('unmatched', 'back'):
        return False
    if len(w) <= 3 and s.isupper():
        return False
    return True


def continuation(s: str) -> bool:
    """The second line of a wrapped heading: starts lower case, short, no final period."""
    w = s.split()
    return bool(w) and len(w) <= 10 and s[0].islower() and s[-1] not in '.,;' and '=' not in s


def numeric_line(s: str) -> bool:
    """Table cells and equation debris: at least 60% of the whitespace tokens carry no letter."""
    w = s.split()
    return len(w) >= 1 and sum(not re.search(r'[A-Za-z]', t) for t in w) / len(w) >= 0.6


def valid_next(cur: tuple, num: tuple) -> bool:
    if not cur:
        return num == (1,)
    if num == cur + (1,):
        return True
    return any(num == cur[:i] + (cur[i] + 1,) for i in range(len(cur)))


def pdf_lines(path: Path) -> list[str]:
    txt = subprocess.run(['pdftotext', str(path), '-'], capture_output=True, text=True).stdout
    txt = unicodedata.normalize('NFKC', txt)
    out = []
    for page in txt.split('\f'):
        for block in re.split(r'\n\s*\n', page):
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            lines = [l for l in lines if not any(p.search(l) for p in DROP_LINE)]
            first = next((l for l in lines if not NUMLINE.fullmatch(l)), '')
            if lines and not CAPTION.match(first):
                out.extend(l for l in lines if NUMLINE.fullmatch(l) or not numeric_line(l))
    return out


def _sec(kind, num, title):
    return {'kind': kind, 'num': num, 'title': title, 'lines': []}


def _num(x: str) -> tuple:
    return tuple(int(v) for v in x.rstrip('.').split('.'))


def _weight(num: tuple, title: str, nxt: str) -> float:
    """Preference of a candidate heading in the chain. Canonical top-level titles weigh 5, data_methods titles 2
    (their keywords, such as "data" or "model", also occur in table rows), other top-level titles 0.5 (table rows and
    figure labels with a small number in front are the usual false candidates); subsections 1.
    Penalties: a digit in the title, two words or fewer when unmatched, and a long line whose next line goes on in
    lower case (a wrapped sentence)."""
    c = canon(title)
    if len(num) == 1:
        w = 5.0 if c not in ('unmatched', 'back', 'data_methods') else (2.0 if c == 'data_methods' else 0.5)
    else:
        w = 1.0
    if c == 'unmatched' and len(title.split()) <= 2:
        w -= 0.5
    if re.search(r'\d', title):
        w -= 0.5
    if len(title) >= 35 and nxt[:1].islower():
        w -= 1.5
    return w


def _is_back(s):
    b = BACK.match(s)
    return bool(b and (len(s.split()) <= 4 or b.group(2) == '.'))


def _is_app(s):
    a = APPENDIX.match(s)
    return bool(a and (not a.group(2) or heading_like(a.group(2))))


def parse_pdf(path: Path, need_abstract=True) -> list[dict]:
    """Sections of a PDF; kind is front, abstract, body (numbered), appendix or back.

    The numbered headings are the highest-weight chain of candidates in which every number is a valid successor of
    the one before (dynamic programming over candidates in reading order). A candidate is a heading-like line with a
    number on the same line, or with any standalone number line since the last body line. The chain starts at 1
    (or, penalized, at 1.1 or 2 when the first heading was missed); a missed top-level heading (n to n + 2) is
    allowed at a cost of SKIP; a heading that is not the first child of the previous one, fewer than MINGAP lines
    after it, costs GAPCOST (consecutive numbered table rows). A canonical title (Results, Discussion, ...) with no
    number line in reach is a candidate for every top-level number at a cost of UNNUMBERED. Candidates stop at the
    first appendix heading or the reference list."""
    lines = pdf_lines(path)
    a0 = next((i for i, s in enumerate(lines) if re.match(r'^Abstract\b[.:]?', s)), None) if need_abstract else None
    if need_abstract and a0 is None:
        return parse_pdf(path, need_abstract=False)
    start = a0 if a0 is not None else -1
    # numbered headings are looked for up to the reference list; in two-column typeset PDFs the back matter
    # (Data availability, ...) can come before the last numbered section in reading order
    end = next((i for i in range(start + 1, len(lines)) if re.fullmatch(r'(References|Bibliography)', lines[i]) or _is_app(lines[i])), len(lines))
    cands = []
    for i in range(start + 1, end):
        s = lines[i]
        if NUMLINE.fullmatch(s):
            continue
        m = INLINE_HEAD.match(s)
        nxt = lines[i + 1] if i + 1 < len(lines) else ''
        if m and heading_like(m.group(2)):
            n = _num(m.group(1))
            cands.append((i, n, m.group(2), _weight(n, m.group(2), nxt)))
        if heading_like(s):
            near = [_num(lines[k]) for k in range(max(start + 1, i - WINDOW), i) if NUMLINE.fullmatch(lines[k])]
            cands.extend((i, n, s, _weight(n, s, nxt)) for n in dict.fromkeys(near))
            # a canonical title with no number in reach (two-column layouts move the number): any top-level number
            if not near and canon(s) not in ('unmatched', 'back') and len(s.split()) <= 6 and nxt[:1].isupper():
                cands.extend((i, (k,), s, _weight((k,), s, nxt) - UNNUMBERED) for k in range(1, 16))
    n = len(cands)
    best, prev = [float('-inf')] * n, [None] * n
    for j, (lj, nj, tj, wj) in enumerate(cands):
        if nj == (1,):
            best[j] = wj
        elif nj in ((1, 1), (2,)):
            best[j] = wj - 2
        for i in range(j):
            li, ni = cands[i][:2]
            if li >= lj or best[i] == float('-inf'):
                continue
            step = 0 if valid_next(ni, nj) else (SKIP if nj == (ni[0] + 2,) else None)
            if step is not None and lj - li < MINGAP and nj != ni + (1,):
                step += GAPCOST
            if step is not None and best[i] + wj - step > best[j]:
                best[j], prev[j] = best[i] + wj - step, i
    chain = []
    if n and max(best) > float('-inf'):
        j = int(np.argmax(best))
        while j is not None:
            chain.append(cands[j]); j = prev[j]
        chain.reverse()
    # after a conclusions heading only appendices and back matter follow (a numbered Data availability in ESSD, a
    # rare Discussion): other numbered headings there are table or figure text
    conc = next((k for k, c in enumerate(chain) if len(c[1]) == 1 and canon(c[2]) == 'conclusions'), None)
    if conc is not None:
        top = None
        kept = chain[:conc + 1]
        for c in chain[conc + 1:]:
            if len(c[1]) == 1:
                top = canon(c[2])
            if top in ('back', 'discussion'):
                kept.append(c)
        chain = kept
    heads = {}
    for li, num, title, _ in chain:
        k = li
        while k + 1 < end and continuation(lines[k + 1]) and len(title.split()) >= 2:
            k += 1
            title += ' ' + lines[k]
        heads[li] = (num, title, k)
    secs = [_sec('front', (), 'front')]
    i = -1
    while i + 1 < len(lines):
        i += 1
        s = lines[i]
        if i == start:
            secs.append(_sec('abstract', (0,), 'Abstract'))
            rest = re.sub(r'^Abstract\b[.:]?\s*', '', s)
            if rest:
                secs[-1]['lines'].append(rest)
            continue
        if i in heads:
            num, title, k = heads[i]
            secs.append(_sec('body', num, title))
            i = k
            continue
        if i > start:
            if _is_back(s):
                b = BACK.match(s)
                secs.append(_sec('back', ('back',), b.group(1)))
                if s[b.end():]:
                    secs[-1]['lines'].append(s[b.end():])
                continue
            if _is_app(s):
                a = APPENDIX.match(s)
                secs.append(_sec('appendix', (a.group(1),), a.group(2) or 'Appendix ' + a.group(1)))
                continue
        if NUMLINE.fullmatch(s):
            continue
        secs[-1]['lines'].append(s)
    for x in secs:
        x['text'] = re.sub(r'(\w)- (\w)', r'\1\2', ' '.join(x.pop('lines')))
    return secs


def parse_xml(path: Path) -> list[dict]:
    secs = [_sec('front', (), 'front')]
    for line in path.read_text().splitlines():
        m = re.match(r'^§(\S+)\s*(.*)$', line)
        if m:
            num, title = m.group(1), m.group(2).strip()
            if num == '0' or title.lower() == 'abstract':
                secs.append(_sec('abstract', (0,), 'Abstract'))
            elif re.match(r'^\d+(\.\d+)*$', num):
                secs.append(_sec('body', tuple(int(x) for x in num.split('.')), title))
            else:
                secs.append(_sec('appendix', (num,), title))
            continue
        m = re.match(r'^\[§[^\]]*¶\d+\]\s*(.*)$', line)
        if m:
            secs[-1]['lines'].append(m.group(1))
    for x in secs:
        x['text'] = unicodedata.normalize('NFKC', ' '.join(x.pop('lines')))
    return secs


def norm_title(t: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z ]', ' ', unicodedata.normalize('NFKC', t).lower())).strip()


METHODS = re.compile(r'\b(methods?|methodology|methodologies|materials?|data|datasets?|data sets?|study (area|areas|site|sites|region|regions)|'
                     r'field (site|sites|area|setting)|settings?|observations?|measurements?|experiments?|experimental|'
                     r'models?|modell?ing|simulations?|sampling|samples|instrumentation|approach|theory|theoretical|'
                     r'framework|processing|inversion|set ?up|design)\b')


def canon(title: str) -> str:
    """Canonical section of a top-level title (rules in order; first hit wins)."""
    t = norm_title(title)
    if t.startswith('abstract'):
        return 'abstract'
    if re.search(r'\b(code|data|software|sample)( and (code|data))? availability\b', t) or t in (
            'acknowledgements', 'acknowledgments', 'references', 'author contributions', 'competing interests'):
        return 'back'
    if 'introduction' in t or t in ('background', 'motivation', 'background and motivation'):
        return 'introduction'
    if re.search(r'\bresults?\b.*\bdiscussions?\b|\bdiscussions?\b.*\bresults?\b', t):
        return 'results_discussion'
    if re.match(r'(summary|conclusions?|concluding remarks|outlook|final remarks)\b', t):
        return 'conclusions'
    if re.search(r'\bdiscussions?\b', t):
        return 'discussion'
    if re.search(r'\bresults?\b', t):
        return 'results'
    if METHODS.search(t):
        return 'data_methods'
    return 'unmatched'


def label(secs: list[dict]) -> list[dict]:
    """Canonical section of every section (subsections inherit the top level before them), and the positional
    variant for unmatched top-level sections (sensitivity only): after the introduction, data_methods; after
    data_methods, data_methods when a data_methods or results section follows, else results; after results, results."""
    tops = [i for i, x in enumerate(secs) if x['kind'] == 'body' and len(x['num']) == 1]
    can = {i: canon(secs[i]['title']) for i in tops}
    pos = dict(can)
    for k, i in enumerate(tops):
        if can[i] != 'unmatched':
            continue
        before = [can[j] for j in tops[:k] if can[j] != 'unmatched']
        after = [can[j] for j in tops[k + 1:] if can[j] != 'unmatched']
        last = before[-1] if before else None
        if last == 'introduction':
            pos[i] = 'data_methods'
        elif last == 'data_methods':
            pos[i] = 'data_methods' if any(a in after for a in ('data_methods', 'results', 'results_discussion')) else 'results'
        elif last in ('results', 'results_discussion'):
            pos[i] = 'results'
    c, cp = 'unmatched', 'unmatched'
    for i, x in enumerate(secs):
        if x['kind'] == 'body':
            if i in can:
                c, cp = can[i], pos[i]
            x['canon'], x['canon_pos'] = c, cp
        else:
            x['canon'] = x['canon_pos'] = x['kind']
            c = cp = 'unmatched'
    return secs


# ---------------------------------------------------------------- sentences and tokens

ABBR = ('et al.', 'e.g.', 'i.e.', 'Fig.', 'Figs.', 'Eq.', 'Eqs.', 'Sect.', 'Sects.', 'approx.', 'cf.', 'vs.', 'resp.',
        'ca.', 'No.', 'no.', 'Ref.', 'Refs.', 'Tab.', 'Tabs.', 'Ch.', 'Vol.', 'St.', 'Mt.', 'Dr.', 'Prof.', 'Jr.', 'U.S.')
CIT_PAREN = re.compile(r'\((?=[^()]*?(?:et al\.|[A-Z][\w\'’\-]+,? (?:19|20)\d{2}))[^()]*\)')
CIT_NARR = re.compile(r'\b[A-Z][\w\'’\-]+(?: et al\.| and [A-Z][\w\'’\-]+| & [A-Z][\w\'’\-]+)? \((?:19|20)\d{2}[a-z]?'
                      r'(?:[,;] ?(?:(?:19|20)\d{2}[a-z]?|[a-z]))*\)')
CIT_BARE = re.compile(r'\b[A-Z][\w\'’\-]+(?: et al\.| and [A-Z][\w\'’\-]+)?,? (?:19|20)\d{2}[a-z]?\b')
REFS = re.compile(r'\b(?:Figs?|Figures?|Tables?|Tabs?|Eqs?|Equations?|Sects?|Sections?|Appendix|Appendices)\.?\s*'
                  r'(?:\(?[A-Z]?\d+[a-z]?\)?(?:\s*(?:,|and|–|-|to)\s*\(?[A-Z]?\d+[a-z]?\)?)*)?')
STOP = set('the of and in to a an is are was were be been by for with on at as from that this these those which it its '
           'we our or not than also can may into between both all their there has have had more most such using used '
           'based over each other two one when where while within during after before both however thus'.split())


def sentences(text: str) -> list[str]:
    t = text
    for a in ABBR:
        t = t.replace(a, a.replace('.', '\x00'))
    t = re.sub(r'\b([A-Z])\.(?=\s?[A-Z]\.)', '\\1\x00', t)
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z(\[])', t)
    return [p.replace('\x00', '.').strip() for p in parts if p.strip()]


def tokens(s: str) -> list[str]:
    s = unicodedata.normalize('NFKC', s)
    for _ in range(3):
        s2 = CIT_PAREN.sub(' ', s)
        if s2 == s:
            break
        s = s2
    s = CIT_NARR.sub(' ', s)
    s = CIT_BARE.sub(' ', s)
    s = REFS.sub(' ', s)
    s = s.lower().replace('\u00ad', '').replace('-', ' ').replace('\u2010', ' ')
    return [spell(t) for t in re.findall(r'[a-z]+|\d+(?:\.\d+)?', s) if len(t) > 1 or t.isdigit()]


def spell(t: str) -> str:
    """British to American spelling, applied to both versions (copy editing changes it): -our, -ise/-yse, -tre.
    Over-applying (otherwise to otherwize) is harmless because both sides get the same mapping."""
    if len(t) >= 5:
        t = re.sub(r'our$', 'or', t)
        t = re.sub(r'(?<=[a-z]{3})([iy])s(e|ed|es|ing|ation|ations)$', r'\1z\2', t)
        t = re.sub(r'(?<=[a-z]{2})tre(s?)$', r'ter\1', t)
    return t


def keep_sentence(tok: list[str]) -> bool:
    return len(tok) >= 4 and sum(t.isalpha() for t in tok) / len(tok) >= 0.5


def sentence_table(secs: list[dict], key='canon') -> list[dict]:
    """Filtered sentences of every section except front matter, in reading order."""
    rows = []
    for i, x in enumerate(secs):
        if x['kind'] == 'front':
            continue
        for s in sentences(x['text']):
            tok = tokens(s)
            if keep_sentence(tok):
                rows.append({'sec': i, 'canon': x['canon'], 'canon_pos': x['canon_pos'], 'tok': tok,
                             'content': {t for t in tok if t not in STOP and len(t) > 2}})
    return rows


# ---------------------------------------------------------------- alignment

def coverage(p: list[str], q: list[str]) -> float:
    """Share of the tokens of p matched, in order, by runs of at least 2 tokens in q (difflib matching blocks)."""
    sm = difflib.SequenceMatcher(None, p, q, autojunk=False)
    return sum(b.size for b in sm.get_matching_blocks() if b.size >= 2) / len(p)


def align(pub: list[dict], sub: list[dict]) -> None:
    """For every sentence of pub: its best coverage by a window of three consecutive sentences of sub (s, primary),
    the best sentence-to-sentence difflib ratio (ratio, also tried against the joins with a neighbor), and the index
    of the best-matching sub sentence (origin)."""
    inv = defaultdict(list)
    for j, r in enumerate(sub):
        for t in r['content']:
            inv[t].append(j)
    for p in pub:
        cnt = Counter()
        for t in p['content']:
            for j in inv.get(t, ()):
                cnt[j] += 1
        best, bj, bratio = 0.0, None, 0.0
        for j, _ in cnt.most_common(NCAND):
            win = sum((sub[k]['tok'] for k in range(max(0, j - 1), min(len(sub), j + 2))), [])
            c = coverage(p['tok'], win)
            if c > best:
                best, bj = c, j
            seqs = [sub[j]['tok']]
            if j > 0:
                seqs.append(sub[j - 1]['tok'] + sub[j]['tok'])
            if j + 1 < len(sub):
                seqs.append(sub[j]['tok'] + sub[j + 1]['tok'])
            for q in seqs:
                sm = difflib.SequenceMatcher(None, p['tok'], q, autojunk=False)
                if sm.real_quick_ratio() <= bratio or sm.quick_ratio() <= bratio:
                    continue
                bratio = max(bratio, sm.ratio())
        p['s'] = round(best, 4)
        p['ratio'] = round(bratio, 4)
        p['origin'] = bj


def spearman(a, b) -> float:
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    if ra.std() == 0 or rb.std() == 0:
        return float('nan')
    return float(np.corrcoef(ra, rb)[0, 1])


def subtitles(secs, c, key):
    return [norm_title(x['title']) for x in secs if x['kind'] == 'body' and x.get(key) == c and len(x['num']) > 1]


def _nt(t: str) -> str:
    return ' '.join(spell(w) for w in norm_title(t).split())


def titles_not_found(titles: list[str], secs: list[dict]) -> int:
    """Published subsection titles with no counterpart in the submitted version: neither present as a phrase
    anywhere in the submitted text (headings the parser missed are still text) nor within difflib ratio 0.8 of a
    submitted heading."""
    doc = ' ' + _nt(' '.join(x['title'] + ' ' + x['text'] for x in secs)) + ' '
    heads_ = [_nt(x['title']) for x in secs if x['kind'] == 'body']
    n = 0
    for t in titles:
        t = _nt(t)
        if not t or f' {t} ' in doc or any(difflib.SequenceMatcher(None, t, u).ratio() >= 0.8 for u in heads_):
            continue
        n += 1
    return n


def section_metrics(pub_rows, sub_rows, pub_secs, sub_secs, key='canon') -> dict:
    out = {}
    cats = [c for c in dict.fromkeys(r[key] for r in pub_rows) if c not in ('front', 'back')]
    for c in cats:
        P = [r for r in pub_rows if r[key] == c]
        S = [r for r in sub_rows if r[key] == c]
        s = np.array([r['s'] for r in P])
        kept = [(i, r) for i, r in enumerate(P) if r['s'] >= KEEP]
        orig = [sub_rows[r['origin']][key] for _, r in kept]
        moved = sum(o != c for o in orig) / len(kept) if kept else None
        same = [(i, r['origin']) for (i, r), o in zip(kept, orig) if o == c]
        rho = spearman([a for a, _ in same], [b for _, b in same]) if len(same) >= 5 else None
        pst, sst = subtitles(pub_secs, c, key), subtitles(sub_secs, c, key)
        new_titles = titles_not_found(pst, sub_secs)
        sub_changed = new_titles > 0
        flags = {'absent_in_submitted': not S, 'subsections_changed': bool(sub_changed),
                 'moved_in': bool(moved is not None and moved >= MOVED_MIN),
                 'reordered': bool(rho is not None and rho == rho and rho < ORDER_MIN)}
        pt, st = sum(len(r['tok']) for r in P), sum(len(r['tok']) for r in S)
        out[c] = {'n_pub': len(P), 'n_sub': len(S), 'n_kept': int((s >= KEEP).sum()),
                  'n_modified': int(((s >= NEW) & (s < KEEP)).sum()), 'n_new': int((s < NEW).sum()),
                  'changed_share': round(float((s < KEEP).mean()), 4),
                  'changed_share_07': round(float((s < SENS[0]).mean()), 4),
                  'changed_share_09': round(float((s < SENS[1]).mean()), 4),
                  'new_share': round(float((s < NEW).mean()), 4),
                  'tokens_pub': pt, 'tokens_sub': st, 'length_ratio': round(pt / st, 4) if st else None,
                  'moved_in_share': round(moved, 4) if moved is not None else None,
                  'order_spearman': round(rho, 4) if rho is not None and rho == rho else None,
                  'subsections_pub': len(pst), 'subsections_sub': len(sst), 'subsection_titles_new': new_titles,
                  'flags': flags, 'restructured': any(flags.values())}
    return out


def group_share(rows, cats, key='canon', thr=KEEP, field='s'):
    s = [r[field] for r in rows if r[key] in cats]
    return (float(np.mean(np.array(s) < thr)), len(s)) if s else (None, 0)


# ---------------------------------------------------------------- gap statement

def locate(quote: str, rows: list[dict]) -> tuple[float, str | None]:
    q = tokens(quote)
    if not q:
        return 0.0, None
    qc = {t for t in q if t not in STOP and len(t) > 2}
    cnt = Counter()
    for j, r in enumerate(rows):
        n = len(qc & r['content'])
        if n:
            cnt[j] = n
    best, bc = 0.0, None
    for j, _ in cnt.most_common(10):
        win = sum((rows[k]['tok'] for k in range(max(0, j - 1), min(len(rows), j + 2))), [])
        sm = difflib.SequenceMatcher(None, q, win, autojunk=False)
        cov = sum(b.size for b in sm.get_matching_blocks() if b.size >= 2) / len(q)
        if cov > best:
            best, bc = cov, rows[j]['canon']
    return round(best, 4), bc


def all_rows(secs):
    """Every filtered sentence including the front matter (for locating quotes)."""
    rows = []
    for x in secs:
        for s in sentences(x['text']):
            tok = tokens(s)
            if tok:
                rows.append({'canon': x['canon'], 'tok': tok, 'content': {t for t in tok if t not in STOP and len(t) > 2}})
    return rows


# ---------------------------------------------------------------- statistics (numpy only)

def paired(d, rng) -> dict:
    d = np.asarray([x for x in d if x is not None and x == x], dtype=float)
    n = len(d)
    if n < 3:
        return {'n': n}
    obs = d.mean()
    signs = rng.choice(np.array([-1.0, 1.0]), size=(NPERM, n))
    null = (signs * d).mean(1)
    p = (np.sum(np.abs(null) >= abs(obs) - 1e-12) + 1) / (NPERM + 1)
    idx = rng.integers(0, n, (NBOOT, n))
    bd = d[idx]
    sd = d.std(ddof=1)
    bsd = bd.std(axis=1, ddof=1)
    bdz = np.where(bsd > 0, bd.mean(1) / np.where(bsd > 0, bsd, 1), np.nan)

    def ci(v):
        v = v[np.isfinite(v)]
        return [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]
    return {'n': n, 'mean_diff': round(float(obs), 4), 'mean_ci': ci(bd.mean(1)),
            'median_diff': round(float(np.median(d)), 4), 'median_ci': ci(np.median(bd, axis=1)),
            'dz': round(float(obs / sd), 4) if sd > 0 else None, 'dz_ci': ci(bdz) if sd > 0 else None,
            'p_perm': round(float(p), 5), 'n_positive': int((d > 0).sum()), 'n_negative': int((d < 0).sum())}


def mean_ci(v, rng) -> dict:
    v = np.asarray([x for x in v if x is not None and x == x], dtype=float)
    if len(v) == 0:
        return {'n': 0}
    idx = rng.integers(0, len(v), (NBOOT, len(v)))
    b = v[idx].mean(1)
    return {'n': len(v), 'mean': round(float(v.mean()), 4), 'median': round(float(np.median(v)), 4),
            'ci': [round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)]}


# ---------------------------------------------------------------- per paper

def versions(r) -> tuple[dict, dict]:
    key, d = r['key'], REVIEW / r['key']
    stem = preprint_stem(r)
    pre = d / f'{stem}.pdf'
    if pre.is_file():
        sub = {'kind': 'discussion preprint', 'file': rel(pre)}
    else:
        mv = sorted(d.glob('*-manuscript-version*.pdf'), key=lambda f: int(re.search(r'version(\d+)', f.name).group(1)))
        mv = [f for f in mv if 'typeset' not in f.name]
        sub = {'kind': 'lowest manuscript-version (revised)', 'file': rel(mv[0])} if mv else {'kind': None}
    xml = GOLD / f'{key}.xml.txt'
    pdf = GOLD / f'{key}.pdf'
    pub = {'kind': 'publisher XML text', 'file': rel(xml)} if xml.is_file() else (
        {'kind': 'final PDF', 'file': rel(pdf)} if pdf.is_file() else {'kind': None})
    return sub, pub


def heads(secs):
    return [['.'.join(map(str, x['num'])), x['title'], x['canon'], x['canon_pos']] for x in secs
            if x['kind'] in ('body', 'abstract', 'appendix', 'back') and (x['kind'] != 'body' or len(x['num']) == 1)]


def from_private(p: str) -> Path:
    return PRIVATE.joinpath(*Path(p).parts[1:])


def paper(r) -> dict:
    sub_v, pub_v = versions(r)
    rec = {'key': r['key'], 'doi': r['doi'], 'preprint_doi': r.get('preprint_doi'), 'submitted': sub_v, 'published': pub_v}
    if not sub_v['kind'] or not pub_v['kind']:
        rec['skipped'] = 'version missing'
        return rec
    pf = from_private(pub_v['file'])
    pub_secs = label(parse_xml(pf) if pf.suffix == '.txt' else parse_pdf(pf))
    sub_secs = label(parse_pdf(from_private(sub_v['file'])))
    ctl_secs = label(parse_pdf(GOLD / f"{r['key']}.pdf")) if pf.suffix == '.txt' and (GOLD / f"{r['key']}.pdf").is_file() else None
    pub_rows, sub_rows = sentence_table(pub_secs), sentence_table(sub_secs)
    align(pub_rows, sub_rows)
    rec['headings'] = {'submitted': heads(sub_secs), 'published': heads(pub_secs)}
    rec['sections'] = section_metrics(pub_rows, sub_rows, pub_secs, sub_secs, 'canon')
    rec['sections_positional'] = section_metrics(pub_rows, sub_rows, pub_secs, sub_secs, 'canon_pos')
    rec['sims'] = [[r_['canon'], r_['s'], sub_rows[r_['origin']]['canon'] if r_['origin'] is not None else None] for r_ in pub_rows]
    g = {}
    for name, cats in (('framing', FRAMING), ('workflow', WORKFLOW), ('workflow_no_rd', ('data_methods', 'results'))):
        for k_, thr in (('', KEEP), ('_07', SENS[0]), ('_09', SENS[1])):
            g[name + k_] = group_share(pub_rows, cats, 'canon', thr)[0]
        g[name + '_pos'] = group_share(pub_rows, cats, 'canon_pos')[0]
        g[name + '_ratio'] = group_share(pub_rows, cats, 'canon', KEEP, 'ratio')[0]
        g['n_' + name] = group_share(pub_rows, cats)[1]
        pt = sum(len(x['tok']) for x in pub_rows if x['canon'] in cats)
        st = sum(len(x['tok']) for x in sub_rows if x['canon'] in cats)
        g[name + '_log2_length'] = round(float(np.log2(pt / st)), 4) if pt and st else None
        rs = [rec['sections'][c]['restructured'] for c in cats if c in rec['sections']]
        g[name + '_restructured'] = (sum(rs) / len(rs)) if rs else None
    rec['groups'] = g
    if ctl_secs:
        ctl_rows = sentence_table(ctl_secs)
        pub2 = [dict(x) for x in pub_rows]
        align(pub2, ctl_rows)
        cm = section_metrics(pub2, ctl_rows, pub_secs, ctl_secs)
        kept = [x for x in pub2 if x['s'] >= KEEP and x['origin'] is not None]
        rec['control'] = {'headings': heads(ctl_secs),
                          'sections': {c: v['changed_share'] for c, v in cm.items()},
                          'restructured': {c: v['restructured'] for c, v in cm.items()},
                          'framing': group_share(pub2, FRAMING)[0], 'workflow': group_share(pub2, WORKFLOW)[0],
                          # share of kept sentences whose PDF-parsed section equals the XML section: parser accuracy
                          'label_agreement': round(sum(ctl_rows[x['origin']]['canon'] == x['canon'] for x in kept) / len(kept), 4) if kept else None}
    # the reverse direction: submitted sentences not carried into the published text (deleted or rewritten)
    subc = [dict(x) for x in sub_rows]
    align(subc, pub_rows)
    dele = {}
    for c in dict.fromkeys(x['canon'] for x in subc):
        if c in ('front', 'back'):
            continue
        v = [x['s'] for x in subc if x['canon'] == c]
        dele[c] = {'n_sub': len(v), 'dropped_share': round(float(np.mean(np.array(v) < KEEP)), 4)}
    rec['submitted_dropped'] = dele
    for name, cats in (('framing', FRAMING), ('workflow', WORKFLOW)):
        v = [x['s'] for x in subc if x['canon'] in cats]
        g[name + '_dropped'] = float(np.mean(np.array(v) < KEEP)) if v else None
    # gap statement
    cf = CALC1 / f"{r['key']}.json"
    if cf.is_file():
        ent = json.loads(cf.read_text()).get('entry') or {}
        ev = ent.get('evidence') or ''
        cov_pub, sec_pub = locate(ev, all_rows(pub_secs))
        cov_sub, sec_sub = locate(ev, all_rows(sub_secs))
        status = 'same' if cov_sub >= GAP_SAME else ('changed' if cov_sub >= GAP_CHANGED else 'absent')
        rec['gap'] = {'entry_state': ent.get('state'), 'locator': ent.get('page'), 'quote_tokens': len(tokens(ev)),
                      'coverage_published': cov_pub, 'section_published': sec_pub, 'located_in_published': cov_pub >= GAP_SAME,
                      'coverage_submitted': cov_sub, 'section_submitted': sec_sub, 'submitted_status': status}
    return rec


# ---------------------------------------------------------------- summary and report

def summarize(recs) -> dict:
    rng = np.random.default_rng(SEED)
    ok = [r for r in recs if 'groups' in r]
    out = {'n_papers': len(recs), 'n_analyzed': len(ok),
           'submitted_kind': dict(Counter(r['submitted']['kind'] for r in recs)),
           'published_kind': dict(Counter(r['published']['kind'] for r in recs))}
    # coverage of canonical sections
    cov = {}
    for c in ORDER + ('unmatched',):
        cov[c] = {'published': sum(c in r['sections'] for r in ok),
                  'submitted_present': sum(any(h[2] == c for h in r['headings']['submitted']) for r in ok)}
    out['section_coverage'] = cov
    um = Counter()
    for r in ok:
        for v in ('submitted', 'published'):
            for h in r['headings'][v]:
                if h[2] == 'unmatched':
                    um[(v, h[1])] += 1
    out['unmatched_titles'] = [{'version': v, 'title': t, 'n': n} for (v, t), n in sorted(um.items())]
    # top-level heading agreement: published canonical sequence vs the submitted / control parse
    def seq(hs):
        return [h[2] for h in hs if h[2] in ORDER]
    out['heading_agreement'] = {
        'submitted_same_canonical_sequence': sum(seq(r['headings']['submitted']) == seq(r['headings']['published']) for r in ok),
        'control_same_canonical_sequence': sum(seq(r['control']['headings']) == seq(r['headings']['published']) for r in ok if 'control' in r),
        'n_control': sum('control' in r for r in ok),
        'control_label_agreement': mean_ci([r['control']['label_agreement'] for r in ok if 'control' in r], np.random.default_rng(SEED + 1))}
    # per section descriptives
    sec = {}
    for c in ORDER + ('unmatched',):
        vals = [r['sections'][c] for r in ok if c in r['sections']]
        if not vals:
            continue
        sec[c] = {'changed_share': mean_ci([v['changed_share'] for v in vals], rng),
                  'new_share': mean_ci([v['new_share'] for v in vals], rng),
                  'changed_share_07': mean_ci([v['changed_share_07'] for v in vals], rng),
                  'changed_share_09': mean_ci([v['changed_share_09'] for v in vals], rng),
                  'log2_length_ratio': mean_ci([float(np.log2(v['length_ratio'])) for v in vals if v['length_ratio']], rng),
                  'restructured': mean_ci([float(v['restructured']) for v in vals], rng),
                  'flags': {f: sum(v['flags'][f] for v in vals) for f in vals[0]['flags']},
                  'control_changed_share': mean_ci([r['control']['sections'].get(c) for r in ok if 'control' in r and c in r['control']['sections']], rng),
                  'control_restructured': mean_ci([float(r['control']['restructured'][c]) for r in ok if 'control' in r and c in r['control']['restructured']], rng),
                  'sentences_published': sum(v['n_pub'] for v in vals),
                  'dropped_share': mean_ci([r['submitted_dropped'][c]['dropped_share'] for r in ok if c in r['submitted_dropped']], rng)}
    out['sections'] = sec
    # tests: framing vs workflow
    def diff(a, b):
        return [r['groups'][a] - r['groups'][b] if r['groups'][a] is not None and r['groups'][b] is not None else None for r in ok]
    t = {}
    t['changed_share'] = paired(diff('framing', 'workflow'), rng)
    t['changed_share_07'] = paired(diff('framing_07', 'workflow_07'), rng)
    t['changed_share_09'] = paired(diff('framing_09', 'workflow_09'), rng)
    t['changed_share_positional'] = paired(diff('framing_pos', 'workflow_pos'), rng)
    t['changed_share_sentence_ratio'] = paired(diff('framing_ratio', 'workflow_ratio'), rng)
    t['changed_share_without_results_discussion'] = paired(diff('framing', 'workflow_no_rd'), rng)
    t['changed_share_preprint_only'] = paired([d for d, r in zip(diff('framing', 'workflow'), ok) if r['submitted']['kind'] == 'discussion preprint'], rng)
    t['dropped_share'] = paired(diff('framing_dropped', 'workflow_dropped'), rng)
    t['log2_length'] = paired(diff('framing_log2_length', 'workflow_log2_length'), rng)
    t['restructured'] = paired(diff('framing_restructured', 'workflow_restructured'), rng)
    fc = []
    for r in ok:
        g, c = r['groups'], r.get('control')
        if c and None not in (g['framing'], g['workflow'], c['framing'], c['workflow']):
            fc.append((g['framing'] - c['framing']) - (g['workflow'] - c['workflow']))
        else:
            fc.append(None)
    t['changed_share_floor_corrected'] = paired(fc, rng)
    t['control_floor_difference'] = paired([r['control']['framing'] - r['control']['workflow'] if r.get('control') and None not in (r['control']['framing'], r['control']['workflow']) else None for r in ok], rng)
    pairs = {}
    for a in FRAMING:
        for b in ('data_methods', 'results'):
            pairs[f'{a} - {b}'] = paired([r['sections'][a]['changed_share'] - r['sections'][b]['changed_share']
                                          if a in r['sections'] and b in r['sections'] else None for r in ok], rng)
    t['section_pairs'] = pairs
    out['tests'] = t
    out['groups'] = {k: mean_ci([r['groups'][k] for r in ok], rng) for k in (
        'framing', 'workflow', 'framing_dropped', 'workflow_dropped', 'framing_log2_length', 'workflow_log2_length',
        'framing_restructured', 'workflow_restructured')}
    # gap statement
    gp = [r['gap'] for r in ok if 'gap' in r]
    loc = [g for g in gp if g['located_in_published']]
    out['gap'] = {'n_codings': len(gp), 'located_in_published': len(loc),
                  'submitted_status': dict(Counter(g['submitted_status'] for g in loc)),
                  'submitted_status_preprint_only': dict(Counter(g['submitted_status'] for g, r in zip(gp, ok) if g['located_in_published'] and r['submitted']['kind'] == 'discussion preprint')),
                  'section_published': dict(Counter(g['section_published'] for g in loc)),
                  'section_moved': sum(1 for g in loc if g['submitted_status'] != 'absent' and g['section_submitted'] != g['section_published']),
                  'entry_state': dict(Counter(g['entry_state'] for g in loc)),
                  'coverage_submitted': mean_ci([g['coverage_submitted'] for g in loc], rng)}
    return out


def pct(x):
    return '' if x is None else f'{100 * x:.0f}%'


def ci_txt(m, scale=100, unit='%', nd=0):
    if not m or m.get('n', 0) == 0:
        return 'n/a'
    f = f'{{:.{nd}f}}'
    return f"{f.format(scale * m['mean'])}{unit} [{f.format(scale * m['ci'][0])}, {f.format(scale * m['ci'][1])}]"


def test_txt(t, scale=100, unit=' points'):
    if t.get('n', 0) < 3:
        return f"n = {t.get('n', 0)}"
    return (f"mean difference {scale * t['mean_diff']:+.1f}{unit} [{scale * t['mean_ci'][0]:+.1f}, {scale * t['mean_ci'][1]:+.1f}], "
            f"median {scale * t['median_diff']:+.1f}, dz {t['dz']} [{t['dz_ci'][0]}, {t['dz_ci'][1]}], "
            f"p = {t['p_perm']} (sign-flip, {NPERM} flips), {t['n_positive']} of {t['n']} papers positive")


def report(recs, S, prov) -> str:
    T, G = S['tests'], S['gap']
    sec = S['sections']
    L = ['# Translation: what changes between submission and publication, section by section', '',
         f"Script `tools/roadmap/g26_translation.py analyze`; data `private/data/roadmap/derived/translation/sections.json`. "
         f"Provenance: commit {prov['commit']}, run {prov['date']}, inputs {', '.join(prov['inputs'])}. "
         'All numbers below were computed by this run; definitions are in the script docstring and repeated in section 6.', '',
         '**Question.** Colleagues told the PI that framing (abstract, introduction) is often written last and to a recipe. '
         'If the framing is the part of a paper most shaped by writing conventions, it should also be the part that moves most '
         'when a paper is rewritten after open review. Copernicus (EGU) journals publish the submitted manuscript (the '
         'discussion preprint) next to the final paper, so this one step of the translation from research to paper can be '
         'measured. The step from finished workflow to first draft is not observable here.', '']
    L += ['## Headline', '']
    t = T['changed_share']
    L.append(f"- {S['n_analyzed']} of {S['n_papers']} Copernicus papers analyzed. Submitted version: "
             + ', '.join(f'{k} {v}' for k, v in S['submitted_kind'].items()) + '. Published version: '
             + ', '.join(f'{k} {v}' for k, v in S['published_kind'].items()) + '.')
    L.append(f"- Share of published sentences that are new or substantially changed (similarity < {KEEP}), mean over papers: "
             f"framing (abstract + introduction) {ci_txt(S['groups']['framing'])}, workflow (data/methods + results) {ci_txt(S['groups']['workflow'])}.")
    L.append(f"- Framing minus workflow, paired by paper: {test_txt(t)}.")
    L.append(f"- Noise floor (final PDF against the publisher XML of the same paper): framing minus workflow {test_txt(T['control_floor_difference'])}. "
             f"Floor-corrected difference: {test_txt(T['changed_share_floor_corrected'])}.")
    L.append(f"- Submitted sentences not carried into the published text (coverage < {KEEP}): framing {ci_txt(S['groups']['framing_dropped'])}, "
             f"workflow {ci_txt(S['groups']['workflow_dropped'])}; framing minus workflow {test_txt(T['dropped_share'])}.")
    L.append(f"- Length (log2 of published over submitted tokens), framing minus workflow: {test_txt(T['log2_length'], 1, '')}.")
    L.append(f"- Restructured share of sections, framing minus workflow: {test_txt(T['restructured'])}.")
    st = G['submitted_status']
    L.append(f"- Gap statement (calc1 entry evidence quote): located in the published text for {G['located_in_published']} of {G['n_codings']} papers. "
             f"In the submitted version it is the same in {st.get('same', 0)}, changed in {st.get('changed', 0)} and absent in {st.get('absent', 0)} "
             f"(absent = appears only in the published paper).")
    L += ['', '## 1. Versions on disk', '',
          '| Version | Source | Papers |', '|:--|:--|--:|']
    for k, v in S['submitted_kind'].items():
        L.append(f'| submitted | {k} | {v} |')
    for k, v in S['published_kind'].items():
        L.append(f'| published | {k} | {v} |')
    L += ['', f"Control parse (final PDF, same words as the XML): {S['heading_agreement']['n_control']} papers. "
          f"Canonical top-level sequence identical to the XML in {S['heading_agreement']['control_same_canonical_sequence']} of them "
          f"(a check on the PDF heading parser); in the submitted version, identical in {S['heading_agreement']['submitted_same_canonical_sequence']} of {S['n_analyzed']}. "
          f"Sentence-level parser accuracy on the control (share of kept sentences whose PDF section equals their XML section, mean over papers): "
          f"{ci_txt(S['heading_agreement']['control_label_agreement'])}.", '',
          '## 2. Section matching', '',
          '| Canonical section | Papers with it (published) | Papers with it (submitted) |', '|:--|--:|--:|']
    for c, v in S['section_coverage'].items():
        L.append(f"| {c} | {v['published']} | {v['submitted_present']} |")
    L += ['', 'Unmatched top-level titles (excluded from the main comparison; assigned by position in the sensitivity analysis):', '']
    for u in S['unmatched_titles']:
        L.append(f"- {u['version']}: {u['title']} ({u['n']})")
    L += ['', '## 3. Change by section', '',
          'Mean over papers with the section, 95% bootstrap interval. Changed = new or substantially changed (s < 0.8); '
          'floor = the same measure for the final PDF against the XML of the same paper.', '',
          '![Changed share by section](fig_sections.png)', '',
          '| Section | Papers | Sentences | Changed | New (s < 0.4) | Changed at 0.7 / 0.9 | Floor | Submitted dropped | log2 length ratio | Restructured | Floor restructured |',
          '|:--|--:|--:|:--|:--|:--|:--|:--|:--|:--|:--|']
    for c, v in sec.items():
        L.append(f"| {c} | {v['changed_share']['n']} | {v['sentences_published']} | {ci_txt(v['changed_share'])} | {ci_txt(v['new_share'])} | "
                 f"{pct(v['changed_share_07']['mean'])} / {pct(v['changed_share_09']['mean'])} | {ci_txt(v['control_changed_share'])} | {ci_txt(v['dropped_share'])} | "
                 f"{ci_txt(v['log2_length_ratio'], 1, '', 2)} | {ci_txt(v['restructured'])} | {ci_txt(v['control_restructured'])} |")
    L += ['', 'Restructuring flags (papers):', '', '| Section | absent in submitted | subsections changed | moved in | reordered |', '|:--|--:|--:|--:|--:|']
    for c, v in sec.items():
        f = v['flags']
        L.append(f"| {c} | {f['absent_in_submitted']} | {f['subsections_changed']} | {f['moved_in']} | {f['reordered']} |")
    L += ['', '## 4. Framing against workflow (paired tests)', '',
          '| Comparison | Papers | Mean difference [95% CI] | dz [95% CI] | p (sign-flip) |', '|:--|--:|:--|:--|--:|']
    rows = [('changed share (primary)', T['changed_share'], 100), ('changed share, threshold 0.7', T['changed_share_07'], 100),
            ('changed share, threshold 0.9', T['changed_share_09'], 100), ('changed share, positional section rule', T['changed_share_positional'], 100),
            ('changed share, sentence-to-sentence ratio instead of coverage', T['changed_share_sentence_ratio'], 100),
            ('changed share, results-and-discussion dropped', T['changed_share_without_results_discussion'], 100),
            *([('changed share, discussion preprints only', T['changed_share_preprint_only'], 100)]
              if S['submitted_kind'].get('discussion preprint', 0) < S['n_analyzed'] else []),
            ('changed share minus noise floor', T['changed_share_floor_corrected'], 100),
            ('noise floor alone (final PDF vs XML)', T['control_floor_difference'], 100),
            ('submitted sentences dropped', T['dropped_share'], 100),
            ('log2 length ratio', T['log2_length'], 1), ('restructured share', T['restructured'], 100)]
    rows += [(f'section pair {k}', v, 100) for k, v in T['section_pairs'].items()]
    for name, v, sc in rows:
        if v.get('n', 0) < 3:
            L.append(f"| {name} | {v.get('n', 0)} | n/a | n/a | n/a |"); continue
        u = ' pts' if sc == 100 else ''
        L.append(f"| {name} | {v['n']} | {sc * v['mean_diff']:+.1f}{u} [{sc * v['mean_ci'][0]:+.1f}, {sc * v['mean_ci'][1]:+.1f}] | "
                 f"{v['dz']} [{v['dz_ci'][0]}, {v['dz_ci'][1]}] | {v['p_perm']} |")
    L += ['', 'Primary test, named in the task before the 61-paper run: framing minus workflow on the changed share at 0.8. Other rows are sensitivity '
          'or secondary and are not corrected for multiplicity.', '',
          '## 5. The gap statement', '',
          f"The quote the calc1 coder gave as evidence of the entry state (entry states: {', '.join(f'{k} {v}' for k, v in G['entry_state'].items())}) was located in the published text "
          f"(coverage >= {GAP_SAME}) for {G['located_in_published']} of {G['n_codings']} papers. Where it sits in the published paper: "
          + ', '.join(f'{k} {v}' for k, v in G['section_published'].items()) + '.', '',
          '| In the submitted version | Papers | Discussion preprints only |', '|:--|--:|--:|']
    for k in ('same', 'changed', 'absent'):
        L.append(f"| {k} | {G['submitted_status'].get(k, 0)} | {G['submitted_status_preprint_only'].get(k, 0)} |")
    L += ['', f"Present in both versions but in a different canonical section: {G['section_moved']}. Mean coverage in the submitted version: {ci_txt(G['coverage_submitted'])}.", '',
          '## 6. Definitions (for geoscientists and NLP researchers)', '',
          '- **Submitted version**: the discussion preprint, the manuscript as posted for open review in Copernicus journals (after the editor\'s access check, before referee comments). When it could not be obtained, the lowest-numbered revised manuscript the journal posts; that version already contains the response to review, so it under-counts change.',
          '- **Published version**: the publisher XML full text (JATS converted to text by g10); citations, figure numbers and equation numbers are stripped in that text, so the same strings are stripped from the PDF text before matching.',
          f'- **Sentence similarity s** (coverage): the share of a published sentence\'s word tokens (normalized) that are matched, in order, by runs of at least 2 tokens (difflib matching blocks) in a window of three consecutive submitted sentences; best over the windows centred on the {NCAND} submitted sentences sharing the most content words. Coverage does not depend on where the PDF text breaks sentences, which matters because table text and equations break PDF sentences. **Kept** s >= {KEEP}; **substantially changed** {NEW} <= s < {KEEP}; **new** s < {NEW}. **Changed share** = share of a section\'s published sentences with s < {KEEP}. Sensitivity: difflib ratio 2M/T between whole sentences (and joins with a neighbor), which has a higher noise floor.',
          f'- **Dropped share**: the same measure in the other direction, share of a section\'s submitted sentences with coverage < {KEEP} in the published text (deleted or rewritten).',
          '- **Framing** = abstract + introduction; **workflow** = data/methods + results (+ results-and-discussion). Shares pooled over the sentences of the group within a paper, then compared paper by paper.',
          '- **Noise floor**: the same measure for the final PDF against the XML of the same final paper. Nothing changed between them, so whatever it reports is extraction and matching error.',
          '- **Restructured** section: absent in the submitted version, or a published subsection title added or renamed (absent from the whole submitted text), or at least 20% of its kept sentences came from another section, or its kept sentences reordered (Spearman < 0.9).',
          f'- **Tests**: paired sign-flip permutation test of the mean difference across papers ({NPERM} flips); 95% percentile bootstrap intervals over papers ({NBOOT} resamples); dz = mean difference / SD of differences. numpy only, seed {SEED}.',
          '- **Gap statement**: the calc1 coding\'s entry evidence quote (codebook 1.5.0; for most papers the "problem" sentence in the introduction). Coverage = share of its tokens matched in runs of 2 or more tokens within the best three-sentence window.',
          '', '## 7. Caveats', '']
    L += caveats(recs, S)
    return '\n'.join(L) + '\n'


def caveats(recs, S) -> list[str]:
    ok = [r for r in recs if 'groups' in r]
    mv = [r['key'] for r in ok if r['submitted']['kind'] != 'discussion preprint']
    nofr = [r['key'] for r in ok if r['groups']['framing'] is None]
    nowf = [r['key'] for r in ok if r['groups']['workflow'] is None]
    out = [f"- Submitted version is a revised manuscript, not the preprint, for {len(mv)} papers" + (f" ({', '.join(mv)})" if mv else '') + '.',
           f"- No published sentence labeled framing (abstract or introduction found by the parser): {len(nofr)} papers; none labeled workflow (data/methods or results): {len(nowf)} papers"
           + (f" ({', '.join(sorted(set(nofr + nowf)))})" if nofr or nowf else '') + '. They drop out of the paired tests.',
           '- One step only: submission to publication, through open review and copy editing. Framing written last, before submission, leaves no trace in these files.',
           f"- Copernicus journals only, papers coded in calc1 that had an open discussion; journals: {', '.join(f'{k} {v}' for k, v in Counter(r['doi'].split('/')[1].split('-')[0] for r in ok).most_common())}. Not a sample of geoscience, and open review may itself change how much is rewritten.",
           '- The measured change includes copy editing by the publisher (house style, wording fixes), which the noise floor does not remove; spelling and hyphen variants are normalized, other edits are not.',
           '- Similarity on bags of normalized tokens in order; rewording that keeps the words scores as kept, a moved clause can score as changed. The noise floor bounds extraction error, not semantic change.',
           '- The restructured comparison is partly mechanical: abstracts have no subsections and introductions rarely do, so only absence, moved-in and reordered sentences can flag them. Read it as description, not as a test of the hypothesis.',
           '- Section headings in PDFs come from a rule-based parser (no font information); misses are visible in the control parse agreement and in the unmatched titles.',
           '- The gap statement is one quote chosen by a model coder; it is located in the published text only when the coder quoted it closely.']
    return out


def figure(S, path: Path, prov) -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sec = S['sections']
    cats = [c for c in ORDER if c in sec]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    y = np.arange(len(cats))
    for off, k, col, lab in ((-0.17, 'changed_share', '#0f4c5c', 'submitted to published'),
                             (0.17, 'control_changed_share', '#9aa5ab', 'noise floor (final PDF vs XML)')):
        m = np.array([sec[c][k]['mean'] if sec[c][k].get('n') else np.nan for c in cats]) * 100
        lo = np.array([sec[c][k]['ci'][0] if sec[c][k].get('n') else np.nan for c in cats]) * 100
        hi = np.array([sec[c][k]['ci'][1] if sec[c][k].get('n') else np.nan for c in cats]) * 100
        ax.errorbar(m, y + off, xerr=[m - lo, hi - m], fmt='o', color=col, label=lab, capsize=3)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{c.replace('_', ' ')} (n={sec[c]['changed_share']['n']})" for c in cats])
    ax.invert_yaxis()
    ax.set_xlabel('published sentences new or substantially changed (%)\nmean over papers, 95% bootstrap interval', fontsize=9)
    ax.set_xlim(0, 60)
    ax.legend(loc='lower right', frameon=False, fontsize=8)
    ax.spines[['top', 'right']].set_visible(False)
    fig.text(0.01, 0.01, f"Source: g26_translation.py ({prov['commit']}, {prov['date']}); {S['n_analyzed']} Copernicus papers, open review records (g15).",
             fontsize=7, color='#555')
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def analyze(only=None):
    recs = []
    for r in papers():
        if only and r['key'] not in only:
            continue
        rec = paper(r)
        recs.append(rec)
        g = rec.get('groups', {})
        print(rec['key'], rec['submitted']['kind'], 'framing', g.get('framing'), 'workflow', g.get('workflow'),
              'gap', rec.get('gap', {}).get('submitted_status'))
    S = summarize(recs)
    params = {'keep': KEEP, 'new': NEW, 'sensitivity': SENS, 'candidates': NCAND, 'moved_min': MOVED_MIN, 'order_min': ORDER_MIN,
              'gap_same': GAP_SAME, 'gap_changed': GAP_CHANGED, 'permutations': NPERM, 'bootstrap': NBOOT, 'seed': SEED,
              'framing': FRAMING, 'workflow': WORKFLOW, 'pdftotext': 'no -layout'}
    inputs = [rel(INDEX), 'private/data/roadmap/review/<key>/*.pdf', 'private/data/roadmap/pdfs/gold/<key>.xml.txt and .pdf',
              'private/analysis/codings/api/calc1/<key>.json (entry.evidence)']
    if only:
        print(json.dumps(S['tests']['changed_share'], indent=1))
        return
    write_json(OUT / 'sections.json', {'summary': S, 'papers': recs}, inputs, params)
    prov = json.loads((OUT / 'sections.json').read_text())['_provenance']
    figure(S, OUT / 'fig_sections.png', prov)
    md = report(recs, S, prov)
    (OUT / 'SECTIONS.md').write_text(md)
    t = S['tests']['changed_share']
    log('g26_translation.py analyze', 'section-level change from submission to publication (open review papers)', S['n_analyzed'],
        f"framing minus workflow changed share {t.get('mean_diff')} {t.get('mean_ci')}, p {t.get('p_perm')}; "
        f"gap statement {S['gap']['submitted_status']}")


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'analyze'
    if cmd == 'fetch':
        arg = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
        fetch(Path(arg('--index')).resolve() if arg('--index') else None, arg('--record') or 'preprint_fetch.json')
    elif cmd == 'analyze':
        analyze(set(sys.argv[2:]) or None)
    else:
        sys.exit(__doc__)
