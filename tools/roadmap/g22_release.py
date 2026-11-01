"""Public data release of the roadmap work: build data/roadmap-release/ from the private tree.

What. Copies the roadmap's derived data, model codings, paper figures (PNG and provenance JSON), logs and reports from
private/ into data/roadmap-release/, laid out as a mirror of private/ so that every roadmap script reruns from it:
  METASCIENCE_PRIVATE=data/roadmap-release python tools/roadmap/g13_calc1_results.py
Rule set by the PI on October 27, 2026: quoting individual papers is fine, republishing papers is not; everything else
in the roadmap work can be public. The folder is wiped and rebuilt on every run (rerun after new codings arrive).

Rules, applied in this order
  1 allowlist     only paths matching ALLOW (relative to the private root) are considered.
  2 denylist      DENY drops, with its reason: paper full texts in any form (*.pdf, *.xml, *.xml.txt, pdftotext output,
                  derived/format_test/inputs/), abstracts (screen_input.json, screen_batches/), open-review discussion
                  text and the paper text given to the visibility coder (derived/review/visibility_input/), who codes
                  what (derived/gold/human_assignment.json), transcripts of agent review runs on material that stays
                  private (*_wf_*.json: talk slides, human-coder app), run logs (*.log). Never in the allowlist at all:
                  raw/ (API cache), pdfs/, review/ (open-review files), app/ (coder app and packets), keys.
  3 embargo       the papers in derived/gold/human_assignment.json (four human coders) and derived/entry/audit_sample.json
                  (entry-state audit) stay blind until the human coding is done. Identified by key (g22_W...), OpenAlex
                  id (W...) and DOI; in Markdown also by the first 50 characters of the title. Removed:
                    files named after an embargoed key (codings, packets);
                    in JSON/JSONL: list items that are records of an embargoed paper (a top-level string field equal to,
                    or a path containing, one of its identifiers), dict entries keyed by an identifier, bare identifier
                    strings in lists; any other string has the identifier replaced by "[withheld]";
                    in Markdown: table rows naming an embargoed paper; in prose, the sentence (or the '; ' clause) that
                    names it, replaced by a marker; in the run logs (INLINE_MD), only the identifier is replaced.
                  A paper described in prose without an identifier is caught by EMBARGO_DESCRIPTORS (regexes, treated
                  like an identifier in Markdown). While the embargo holds, per-paper entries of state.json (cost,
                  tokens, validation failures) are kept under a pseudonym per run tag ('withheld-007'), so total spend
                  reproduces, and the per-paper test-retest similarities in fig03_reliability.json are sorted (the strip
                  plot needs no paper order). Counts per file go to RELEASE.json (no keys are listed).
  4 quotes        a field that holds a quote from a paper (QUOTE_KEYS) is cut to its first 25 words plus " [...]"; a
                  disagreements[].target (the name of a cited work or position) to its first 20 words plus " [...]"
                  (codebook limit). The marker is a 26th token, so check_coding.validate() still rejects a step or V-check
                  quote that was over the limit, and reruns keep the same valid set.
  5 chained       separate strings of one file can add up to a longer verbatim passage (a V-check quote that continues a
                  step quote, a cut quote whose tail reappears in another field). Every string of a released JSON file
                  is placed in its paper's texts (6-word shingles; publisher XML text, pdftotext, open-review files) and
                  in any source the 12-word check below finds; spans of one file in one source document that overlap
                  or lie within 2 words of each other form one passage. When adding a string would make a passage
                  longer than 25 words and longer than the longest single string in it, the string keeps the longest
                  piece (from its start or from its end) that does not, and the rest becomes " [...] ". A string
                  repeated word for word never lengthens a passage and is left alone.
  6 wording       "Private; not for circulation" status lines in the released reports are removed (PRIVATE_PHRASES).
  7 fetch state   download-queue.json (private root) and data/roadmap/download-queue.before-refetch-2026-10-27.json are
                  released filtered: roadmap keys (g22_*) only, embargo applied, fields doi, status, group, route, meta,
                  updated and file (as 'private/...' or a bare file name, never a local home path). g19, g20, g21, fig01
                  and fig02 read them.
Checks that fail the build (nothing is replaced; the previous release stays)
  - a JSON string over 60 words outside LONG_OK (prose written by the model coder or by the scripts);
  - in LONG_OK fields and Markdown: a passage over 25 words inside quotation marks;
  - a key named abstract_inverted_index, or a string over 25 words under a key containing "abstract";
  - verbatim text: every string of every released JSON, JSONL and Markdown file (Markdown by paragraph) is compared,
    by 12-word shingles, with every paper text (publisher XML text and pdftotext of every PDF), format-test input,
    open-review file and abstract (screen input and every abstract_inverted_index in the raw OpenAlex cache). The build
    fails on a verbatim passage over 25 words, and on strings of one file that chain into one (rule 5). Exempt:
    bibliographic fields (EXEMPT_KEYS: titles, journal names, citation strings) and runs that are mostly numbers (a
    table row of zeros). The word-count cut of rule 4 is only the first pass;
  - any email address, sk-ant-, "Bearer ", apiKey=, api_key=, or any value of ~/.config/metascience/keys.env (read
    here, never printed) anywhere in a released file (keys.env values and key patterns: text or binary; email
    addresses: JSON, JSONL and Markdown);
  - a quote (8 words or more) from an embargoed paper's coding found anywhere in the release, unless the same quote also
    appears in a released paper's coding (shared boilerplate);
  - an identifier or descriptor of an embargoed paper left in any released file;
  - a .pdf in the release, or any file over 20 MB.
After the checks, g13_calc1_results.py and g17_outcomes.py are run on a scratch copy of the new release; their headline
numbers are written to the README and RELEASE.json as the values a colleague's rerun should give.

Inputs   private/ (or $METASCIENCE_PRIVATE): data/roadmap/{EXPERIMENTS,DECISIONS,MANIFEST}.md, data/roadmap/derived/,
         data/roadmap/figures/paper/, analysis/codings/api/<tag>/ and state.json, the reports in DOCS,
         download-queue.json and data/roadmap/download-queue.before-refetch-2026-10-27.json; for the verbatim check only
         data/roadmap/pdfs/, data/roadmap/review/, derived/format_test/inputs/, derived/{gold,r2}/screen_input.json and
         screen_batches/, data/roadmap/raw/; ~/.config/metascience/keys.env (or $METASCIENCE_KEYS) for the key check only
Outputs  data/roadmap-release/ (mirror of private/), data/roadmap-release/README.md, data/roadmap-release/RELEASE.json
         (date, both commits, file list with sha256 and size, dropped files and records per reason, embargo counts,
         quoted share of the papers, expected rerun values); pdftotext cache in private/data/roadmap/pdfs/.pdftotext/
         (git-ignored, never released); one row appended to private/data/roadmap/MANIFEST.md
Run:     python tools/roadmap/g22_release.py
         python tools/roadmap/g22_release.py --lift-embargo   (only once the four coders have finished, PI's decision)
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import random
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from common import PRIVATE, ROOT, log

OUT = ROOT / 'data' / 'roadmap-release'
TMP = ROOT / 'data' / '.roadmap-release.building'
KEYS_ENV = Path(os.environ.get('METASCIENCE_KEYS', Path.home() / '.config' / 'metascience' / 'keys.env'))
MAX_BYTES = 20 * 1024 * 1024

DOCS = ['text/report-roadmap.md', 'text/report-section-entry-state.md', 'text/report-review-visibility.md',
        'analysis/entry-state-evaluation.md', 'analysis/roadmap-plurality-loops.md', 'analysis/roadmap-inquirygraph.md']
ALLOW = ['data/roadmap/EXPERIMENTS.md', 'data/roadmap/DECISIONS.md', 'data/roadmap/MANIFEST.md',
         'data/roadmap/derived/**/*', 'data/roadmap/figures/paper/*.png', 'data/roadmap/figures/paper/*.json',
         'analysis/codings/api/state.json', 'analysis/codings/api/*/*.json'] + DOCS
DENY = [(r'\.pdf$', 'full text (PDF)'),
        (r'\.xml$|\.xml\.txt$|\.pdf\.txt$', 'full text (XML or extracted text)'),
        (r'^data/roadmap/derived/format_test/inputs/', 'full text (format-test inputs)'),
        (r'(^|/)screen_input\.json$|/screen_batches/', 'abstracts (eligibility screen input)'),
        (r'^data/roadmap/derived/review/visibility_input/', 'open-review discussion and paper text'),
        (r'^data/roadmap/(raw|pdfs|review|app)/', 'raw cache, full texts, open-review files or coder app'),
        (r'^data/roadmap/derived/gold/human_assignment\.json$', 'who codes what (human assignment)'),
        (r'_wf_[^/]*\.json$', 'agent review transcripts of private material (slides, coder app)'),
        (r'\.log$', 'run log')]
# Strings allowed over 60 words: prose written by the model coder or by the scripts, never a paper's text.
LONG_OK = {'limits', 'action', 'claim', 'pages_convention', 'reason', 'definition', 'caption', 'note', 'rationale', 'rule'}
LONG_OK_PATHS = {('gates', 'evidence')}
# Fields that hold a quote from a paper (25-word codebook limit).
QUOTE_KEYS = {'quote', 'operational_evidence'}
NAME_MAX = 20   # disagreements[].target names the cited work or position (CODEBOOK section 7)
# Run logs: an embargoed paper is named there for fetch or exclusion reasons, not for its coding; the identifier alone
# is replaced.
INLINE_MD = {'data/roadmap/DECISIONS.md', 'data/roadmap/MANIFEST.md', 'data/roadmap/EXPERIMENTS.md',
             'data/roadmap/derived/format_test/report.md'}
PRIVATE_PHRASES = [(r' ?Private; not for circulation outside the lab\.( The public book carries aggregate results only\.)?', ''),
                   (r' ?Not for circulation outside the lab\.', ''),
                   (r'Private; prose\.', 'Prose.')]
KEYLIKE = [r'sk-ant-', r'Bearer\s', r'apiKey=', r'api_key=']
EMAIL = re.compile(rb'[\w.+-]+@[\w-]+\.[\w.]+')
# Prose that identifies an embargoed paper without naming it (a topic or data set specific to one paper of the blind
# set). Treated like an identifier in Markdown (the sentence is withheld) and checked over the whole release.
EMBARGO_DESCRIPTORS = [r'seafloor fib(?:re|er)[- ]optic', r'telecom cable as a dense line', r'seafloor DAS interferometry',
                       r'25 years of (?:Ethiopian )?agency', r'agency rainfall and streamflow',
                       r'Ethiopian agency hydrometeorological', r'Gilgel Gibe', r'off Sanriku',
                       r'Mat[ée]rn random-field sampler', r'national air-quality network',
                       r'geodetic and seismic strain-stress discrepanc', r'induced-seismicity screening ahead of a geothermal',
                       r'Earth, Planets and Space paper on travel-time tomography']
MARKER = '[withheld]'
SENT_MARK = '[Withheld until the human coding ends: names or describes a paper in the blind coding set.]'


# ---------------------------------------------------------------------------------------------------------- embargo
class Embargo:
    def __init__(self, src: Path, lifted: bool):
        D = src / 'data' / 'roadmap' / 'derived'
        ha = json.loads((D / 'gold' / 'human_assignment.json').read_text())['data']['papers']
        au = json.loads((D / 'entry' / 'audit_sample.json').read_text())['data']['rows']
        self.human = {p['key'] for p in ha}
        self.audit = {r['key'] for r in au}
        self.keys = set() if lifted else self.human | self.audit
        meta = {}
        for f in [D / 'gold' / 'metrics.json', D / 'r2' / 'metrics.json']:
            if f.is_file():
                for r in json.loads(f.read_text())['data']:
                    meta['g22_' + r['id'].rsplit('/', 1)[-1]] = r
        dois = {p['key']: p.get('doi') for p in ha} | {r['key']: r.get('doi') for r in au}
        self.wids = {k[4:] for k in self.keys}
        self.dois = {norm_doi(dois.get(k) or meta.get(k, {}).get('doi')) for k in self.keys} - {None, ''}
        self.titles = {(meta.get(k, {}).get('title') or '').lower()[:50] for k in self.keys}
        self.titles = {t for t in self.titles if len(t) >= 30}
        self._wre = re.compile(r'(?<![0-9A-Za-z])(?:g22_)?(W\d{6,})(?!\d)')
        self._dre = re.compile('|'.join(f'(?:{d})' for d in EMBARGO_DESCRIPTORS), re.I) if self.keys else None

    def descriptor_in(self, s: str) -> bool:
        return bool(self._dre and self._dre.search(s))

    def hits(self, text: str) -> list[str]:
        """Where an embargoed paper is named or described in text: 'line N: <kind>' entries, no identifier printed.
        Used by build_report_page.py before it writes the public book page."""
        out = []
        for i, line in enumerate(text.split('\n'), 1):
            if not self.keys:
                break
            if any(m in self.wids for m in self._wre.findall(line)):
                out.append(f'line {i}: embargoed W id or key')
            low = line.lower()
            if '10.' in line and any(d in low for d in self.dois):
                out.append(f'line {i}: embargoed DOI')
            if any(t in low for t in self.titles):
                out.append(f'line {i}: embargoed title')
            if self.descriptor_in(line):
                out.append(f'line {i}: embargo descriptor')
        return out

    def ids_in(self, s: str) -> bool:
        if not self.keys:
            return False
        if any(m in self.wids for m in self._wre.findall(s)):
            return True
        if '10.' in s:
            low = s.lower()
            return any(d in low for d in self.dois)
        return False

    def is_id(self, s: str) -> bool:
        s2 = s.rsplit('/', 1)[-1] if s.startswith('https://openalex.org/') else s
        return s2 in self.keys or s2 in self.wids or norm_doi(s) in self.dois

    def in_text(self, s: str) -> bool:
        if self.ids_in(s):
            return True
        low = s.lower()
        return any(t in low for t in self.titles) or self.descriptor_in(s)

    def redact(self, s: str) -> tuple[str, int]:
        n = 0

        def w(m):
            nonlocal n
            if m.group(1) in self.wids:
                n += 1
                return MARKER
            return m.group(0)
        s = self._wre.sub(w, s)
        if '10.' in s:
            for d in self.dois:
                for m in list(re.finditer(re.escape(d), s, flags=re.I)):
                    n += 1
                s = re.sub(re.escape(d), MARKER, s, flags=re.I)
        return s, n


def norm_doi(d):
    if not d:
        return None
    return re.sub(r'^https?://(dx\.)?doi\.org/', '', str(d).strip().lower())


def file_key(rel: str) -> str:
    return Path(rel).name.split('.')[0]


# -------------------------------------------------------------------------------------------------- JSON processing
class JsonFilter:
    def __init__(self, emb: Embargo):
        self.emb = emb
        self.c = Counter()

    def run(self, x):
        return self._walk(x, ())

    def _record_is_embargoed(self, d: dict) -> bool:
        for v in d.values():
            if isinstance(v, str) and (self.emb.is_id(v) or self.emb.ids_in(v)):
                return True
        return False

    def _walk(self, x, path):
        e = self.emb
        if isinstance(x, dict):
            out = {}
            for k, v in x.items():
                if e.keys and isinstance(k, str) and (e.is_id(k) or e.ids_in(k)):
                    self.c['embargoed dict entries'] += 1
                    continue
                out[k] = self._walk(v, path + (k,))
            return out
        if isinstance(x, list):
            out = []
            for v in x:
                if e.keys and isinstance(v, dict) and self._record_is_embargoed(v):
                    self.c['embargoed records'] += 1
                    continue
                if e.keys and isinstance(v, str) and (e.is_id(v) or e.ids_in(v)):
                    self.c['embargoed identifiers in lists'] += 1
                    continue
                out.append(self._walk(v, path + ('[]',)))
            return out
        if isinstance(x, str):
            if e.keys:
                x, n = e.redact(x)
                if n:
                    self.c['identifiers redacted in text'] += n
            key = next((p for p in reversed(path) if p != '[]'), None)
            parent = next((p for p in reversed(path[:-1]) if p != '[]'), None) if path else None
            is_quote = key in QUOTE_KEYS or (key == 'evidence' and parent != 'gates')
            if is_quote and len(x.split()) > 25:
                x = ' '.join(x.split()[:25]) + ' [...]'
                self.c['quotes cut to 25 words'] += 1
            if key == 'target' and parent == 'disagreements' and len(x.split()) > NAME_MAX:
                x = ' '.join(x.split()[:NAME_MAX]) + ' [...]'   # a target names a work or position; long ones copy a sentence
                self.c['disagreement targets cut to 20 words'] += 1
            return x
        return x


def strings(x, path=()):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from strings(v, path + (k,))
    elif isinstance(x, list):
        for v in x:
            yield from strings(v, path + ('[]',))
    elif isinstance(x, str):
        yield path, x


def keys_of(x, path=()):
    if isinstance(x, dict):
        for k, v in x.items():
            yield path, k, v
            yield from keys_of(v, path + (k,))
    elif isinstance(x, list):
        for v in x:
            yield from keys_of(v, path + ('[]',))


def records(x):
    """Every dict with a string 'key' field (a per-paper record), at any depth."""
    if isinstance(x, dict):
        if isinstance(x.get('key'), str):
            yield x
            return
        for v in x.values():
            yield from records(v)
    elif isinstance(x, list):
        for v in x:
            yield from records(v)


QUOTED = [re.compile(r'“([^”]+)”'), re.compile(r'"([^"]+)"'), re.compile(r'‘([^’]+)’'),
          re.compile(r"(?<![A-Za-z0-9])'([^']+?)'(?![A-Za-z0-9])")]


def long_quotes(text: str) -> list[str]:
    return [m for q in QUOTED for m in q.findall(text) if len(m.split()) > 25]


# ---------------------------------------------------------------------------------------------- Markdown processing
SENT = re.compile(r'(?<=[.!?])\s+(?=[A-Z`*(\[])')


def md_filter(text: str, emb: Embargo, c: Counter, inline: bool = False) -> str:
    """Remove private-status phrases; then table rows naming an embargoed paper, and in prose the sentence (or the
    '; '-separated clause) that names it, with a marker in its place. inline=True (run logs): replace the identifier only."""
    for pat, rep in PRIVATE_PHRASES:
        text, n = re.subn(pat, rep, text)
        if n:
            c['private-status phrases removed'] += n
    if not emb.keys:
        return text
    out, fence = [], False
    for line in text.split('\n'):
        if line.lstrip().startswith('```'):
            fence = not fence
        if not emb.in_text(line):
            out.append(line)
            continue
        if inline and not emb.in_text(emb.redact(line)[0]):
            line, n = emb.redact(line)
            c['identifiers redacted in text'] += n
            out.append(line)
            continue
        if line.lstrip().startswith('|') or fence:
            c['embargoed table rows or code lines'] += 1
            continue
        m = re.match(r'^(\s*(?:[-*+]|\d+\.)\s+|\s*#+\s+|\s*>\s*)?(.*)$', line)
        lead, body = m.group(1) or '', m.group(2)
        pieces = []
        for sent in SENT.split(body):
            if not emb.in_text(sent):
                pieces.append(sent)
                continue
            clauses = sent.split('; ')
            if len(clauses) > 1 and not all(emb.in_text(x) for x in clauses):
                kept = [x for x in clauses if not emb.in_text(x)]
                c['embargoed clauses'] += len(clauses) - len(kept)
                pieces.append('; '.join(kept).rstrip('.;') + '; ' + SENT_MARK)
                continue
            c['embargoed sentences'] += 1
            if not pieces or pieces[-1] != SENT_MARK:
                pieces.append(SENT_MARK)
        out.append(lead + ' '.join(pieces).strip())
    return '\n'.join(out)


# ---------------------------------------------------------------------------------------------------------- helpers
def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def git_commit(repo: Path, paths: list[str]) -> str:
    try:
        sha = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(['git', '-C', str(repo), 'status', '--porcelain', *paths], capture_output=True, text=True).stdout.strip()
        return (sha or 'unknown') + ('+uncommitted' if dirty else '')
    except Exception:  # noqa: BLE001
        return 'unknown'


def secret_values() -> list[tuple[str, str]]:
    out = []
    if KEYS_ENV.is_file():
        for line in KEYS_ENV.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip().strip('"').strip("'")
            if len(v) >= 6:
                out.append((k.strip(), v))
    return out


def norm_words(s: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', s.lower())).strip()


def coding_quotes(x) -> list[str]:
    return [s for path, s in strings(x)
            if path and (path[-1] in QUOTE_KEYS or (path[-1] == 'evidence' and 'gates' not in path))
            and len(s.split()) >= 8]


# ------------------------------------------------------------------------------- verbatim text: sources and passages
K_CHECK = 12      # shingle length of the verbatim check (the method of the release audit of October 27, 2026)
K_FINE = 6        # shorter shingles, to place short quotes in their paper when cutting chained strings
LIMIT = 25        # codebook limit on a quote, in words
GAP = 2           # spans of one file in one source closer than this (in words) form one passage
EXEMPT_KEYS = {'title', 'journal', 'documents', 'venue', 'display_name'}   # bibliographic strings, not paper text
WORD = re.compile(r'[a-z0-9]+')


def norm_tokens(text: str):
    """Word tokens ([a-z0-9]+ after NFKC and lowercase) of a release string, with their character offsets in it."""
    chars, off = [], []
    for i, ch in enumerate(text):
        for d in unicodedata.normalize('NFKC', ch).lower():
            chars.append(d)
            off.append(i)
    t = ''.join(chars)
    off.append(len(text))
    toks, st, en = [], [], []
    for m in WORD.finditer(t):
        toks.append(m.group())
        st.append(off[m.start()])
        en.append(off[m.end() - 1] + 1)
    return toks, st, en


def src_tokens(text: str) -> list[str]:
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)          # PDF line-break hyphenation
    return WORD.findall(unicodedata.normalize('NFKC', text).lower())


def _h(tokens, i, k=K_CHECK) -> int:
    return int.from_bytes(hashlib.blake2b(' '.join(tokens[i:i + k]).encode(), digest_size=8).digest(), 'little', signed=True)


def mostly_numbers(tokens) -> bool:
    return 2 * sum(t.isdigit() for t in tokens) >= len(tokens)


def exempt(path) -> bool:
    return any(p in EXEMPT_KEYS for p in path if isinstance(p, str))


class Sources:
    """Every text the release must not reproduce, tokenized: paper texts (publisher XML text and pdftotext of every PDF
    under data/roadmap/pdfs/), format-test inputs, open-review files (text files and pdftotext of the PDFs under
    data/roadmap/review/<key>/) and abstracts (derived/{gold,r2} screen input and batches, and every
    abstract_inverted_index in data/roadmap/raw/). pdftotext output is cached in data/roadmap/pdfs/.pdftotext/."""

    def __init__(self, src: Path):
        D = src / 'data' / 'roadmap'
        cache = D / 'pdfs' / '.pdftotext'
        self.docs = []                    # (kind, name, key, tokens)
        self.by_key = defaultdict(list)   # paper key -> doc indices (paper, format-test input, review)
        if not shutil.which('pdftotext'):
            sys.exit('pdftotext not found: the verbatim check needs it (poppler)')
        jobs = []
        for p in sorted((D / 'pdfs').rglob('*.pdf')):
            jobs.append(('paper', p, cache / 'papers' / (str(p.relative_to(D / 'pdfs')) + '.txt'), file_key(p.name)))
        for p in sorted((D / 'review').rglob('*.pdf')):
            k = p.relative_to(D / 'review').parts[0]
            jobs.append(('review', p, cache / 'review' / (str(p.relative_to(D / 'review')) + '.txt'), k))

        def run(job):
            _, pdf, dst, _ = job
            if not dst.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(['pdftotext', '-q', '-enc', 'UTF-8', str(pdf), str(dst)], capture_output=True, timeout=180)
            return dst.is_file()
        with ThreadPoolExecutor(8) as ex:
            ok = list(ex.map(run, jobs))
        self.pdf_failed = sum(not x for x in ok)
        for p in sorted((D / 'pdfs').rglob('*.xml.txt')):
            if cache not in p.parents:
                self._add('paper', p.name, file_key(p.name), p.read_text(errors='ignore'))
        for (kind, pdf, dst, k), good in zip(jobs, ok):
            if good:
                self._add(kind, pdf.name, k, dst.read_text(errors='ignore'))
        for p in sorted((D / 'derived' / 'format_test' / 'inputs').glob('*.txt')):
            self._add('ftin', p.name, file_key(p.name), p.read_text(errors='ignore'))
        for p in sorted((D / 'review').rglob('*.txt')):
            self._add('review', p.name, p.relative_to(D / 'review').parts[0], p.read_text(errors='ignore'))
        for sub in ('gold', 'r2'):
            for p in [D / 'derived' / sub / 'screen_input.json', *sorted((D / 'derived' / sub / 'screen_batches').glob('*.json'))]:
                if p.is_file():
                    self._abstracts(json.loads(p.read_text()))
        for p in sorted((D / 'raw').rglob('*.json')):
            try:
                self._abstracts(json.loads(p.read_text()))
            except (ValueError, UnicodeDecodeError):
                pass
        H, Dd, P = [], [], []
        for di, (_, _, _, toks) in enumerate(self.docs):
            if len(toks) >= K_CHECK:
                H.append(np.array([_h(toks, i) for i in range(len(toks) - K_CHECK + 1)], dtype=np.int64))
                Dd.append(np.full(len(H[-1]), di, np.int32))
                P.append(np.arange(len(H[-1]), dtype=np.int32))
        H, Dd, P = np.concatenate(H), np.concatenate(Dd), np.concatenate(P)
        o = np.argsort(H, kind='stable')
        self.H, self.D, self.P = H[o], Dd[o], P[o]
        self._fine = {}
        self.counts = dict(Counter(k for k, _, _, _ in self.docs))

    def _add(self, kind, name, key, text):
        toks = src_tokens(text)
        if toks:
            self.docs.append((kind, name, key, toks))
            if kind != 'abstract':
                self.by_key[key].append(len(self.docs) - 1)

    def _abstracts(self, o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == 'abstract' and isinstance(v, str) and v.strip():
                    self._add('abstract', str(o.get('key') or o.get('id')), None, v)
                elif k == 'abstract_inverted_index' and isinstance(v, dict) and v:
                    pos = sorted((i, w) for w, ii in v.items() for i in ii)
                    self._add('abstract', str(o.get('id')), None, ' '.join(w for _, w in pos))
                else:
                    self._abstracts(v)
        elif isinstance(o, list):
            for v in o:
                self._abstracts(v)

    def runs(self, toks) -> list[tuple]:
        """Verbatim runs of 12 words or more: (doc, src_start, src_end, i0, i1), tokens [i0, i1) of the string."""
        if len(toks) < K_CHECK:
            return []
        s = np.array([_h(toks, i) for i in range(len(toks) - K_CHECK + 1)], dtype=np.int64)
        pos = np.searchsorted(self.H, s)
        pos[pos >= len(self.H)] = len(self.H) - 1
        hit = self.H[pos] == s
        out, i = [], 0
        while i < len(s):
            if not hit[i]:
                i += 1
                continue
            j = i
            while j + 1 < len(s) and hit[j + 1]:
                j += 1
            p0 = int(self.P[pos[i]])
            out.append((int(self.D[pos[i]]), p0, p0 + j - i + K_CHECK, i, j + K_CHECK))
            i = j + 1
        return out

    def fine_runs(self, toks, di) -> list[tuple]:
        """Runs of 6 words or more (the whole string when it is shorter than 8 words) of a string in document di:
        (i0, i1, src_start), one per diagonal; the same words found at two places in the source give two runs."""
        if len(toks) < K_FINE:
            return []
        if di not in self._fine:
            dt_ = self.docs[di][3]
            idx = defaultdict(list)
            for p in range(len(dt_) - K_FINE + 1):
                idx[' '.join(dt_[p:p + K_FINE])].append(p)
            self._fine[di] = idx
        idx = self._fine[di]
        diag = defaultdict(list)
        for i in range(len(toks) - K_FINE + 1):
            for p in idx.get(' '.join(toks[i:i + K_FINE]), ()):
                diag[p - i].append(i)
        out = []
        for d, ii in diag.items():
            a = prev = ii[0]
            for i in ii[1:] + [None]:
                if i is not None and i == prev + 1:
                    prev = i
                    continue
                i0, i1 = a, prev + K_FINE
                if i1 - i0 >= min(8, len(toks)):
                    out.append((i0, i1, i0 + d))
                if i is not None:
                    a = prev = i
        return out


def passage_over(spans: list[tuple], new: tuple | None = None) -> list[tuple]:
    """spans: (src_start, src_end, slot) of one file in one source document. Merge spans that overlap or lie within GAP
    words; return the passages (start, end, slots) that hold two or more strings and are longer than LIMIT words and
    than the longest single span in them (a string repeated word for word never lengthens a passage). With new=(a, b,
    slot), only the passage that contains it is considered."""
    allsp = sorted(spans + ([new] if new else []))
    out, cur = [], None
    for a, b, sl in allsp:
        if cur and a <= cur[1] + GAP:
            cur[1] = max(cur[1], b)
            cur[2].add(sl)
            cur[3] = max(cur[3], b - a)
            cur[4] = cur[4] or (new is not None and (a, b, sl) == new)
        else:
            if cur:
                out.append(cur)
            cur = [a, b, {sl}, b - a, new is not None and (a, b, sl) == new]
    if cur:
        out.append(cur)
    return [(a, b, sl) for a, b, sl, longest, has_new in out
            if len(sl) > 1 and b - a > LIMIT and b - a > longest and (new is None or has_new)]


def slots(x, path=(), rkey=None):
    """(container, index, path, record key) for every string, in document order; record key = 'key' of the nearest
    enclosing dict that has one."""
    if isinstance(x, dict):
        rk = x['key'] if isinstance(x.get('key'), str) and x['key'].startswith('g22_') else rkey
        for k, v in x.items():
            if isinstance(v, str):
                yield x, k, path + (k,), rk
            else:
                yield from slots(v, path + (k,), rk)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            if isinstance(v, str):
                yield x, i, path + ('[]',), rkey
            else:
                yield from slots(v, path + ('[]',), rkey)


def cut_chains(rel: str, data, srcs: Sources) -> int:
    """Rule 5, in place on the filtered JSON of one file; returns the number of strings shortened."""
    cov = defaultdict(list)                  # doc -> [(src_start, src_end, slot)]
    fk, n_cut = file_key(rel), 0
    for sid, (cont, k, path, rkey) in enumerate(list(slots(data))):
        s = cont[k]
        if exempt(path):
            continue
        toks, st, en = norm_tokens(s)
        if len(toks) < K_FINE:
            continue
        docs = set(srcs.by_key.get(rkey or fk, ())) | {r[0] for r in srcs.runs(toks)}
        runs = sorted((i0, i1, d, p0) for d in docs for i0, i1, p0 in srcs.fine_runs(toks, d))
        drop = set()
        for i0, i1, d, p0 in runs:
            if not passage_over(cov[d], (p0, p0 + i1 - i0, sid)):
                continue
            best = None
            for m in range(i1 - i0 - 1, 0, -1):          # longest piece kept from the start, else from the end
                for a in (i0, i1 - m):
                    pa = p0 + a - i0
                    if not passage_over(cov[d], (pa, pa + m, sid)):
                        best = (a, a + m)
                        break
                if best:
                    break
            keep = set(range(*best)) if best else set()
            drop |= set(range(i0, i1)) - keep
        if drop:
            pieces, i = [], 0
            last = 0
            while i < len(toks):
                if i in drop:
                    j = i
                    while j + 1 < len(toks) and j + 1 in drop:
                        j += 1
                    pieces.append(s[last:st[i]])
                    pieces.append(' [...] ')
                    last = en[j]
                    i = j + 1
                else:
                    i += 1
            pieces.append(s[last:])
            new = re.sub(r'\s+', ' ', ''.join(pieces)).strip()
            new = re.sub(r'(\[\.\.\.\]\W*){2,}', '[...] ', new).strip()
            cont[k] = new
            n_cut += 1
            toks = norm_tokens(new)[0]
        for d in docs:
            for i0, i1, p0 in srcs.fine_runs(toks, d):
                cov[d].append((p0, p0 + i1 - i0, sid))
    return n_cut


def text_units(rel: str, text: str):
    """(location, path, string) of a released text file: JSON strings, JSONL strings per line, Markdown paragraphs."""
    if rel.endswith('.json'):
        for path, s in strings(json.loads(text)):
            yield '.'.join(map(str, path)), path, s
    elif rel.endswith('.jsonl'):
        for ln, line in enumerate(text.splitlines(), 1):
            if line.strip():
                for path, s in strings(json.loads(line)):
                    yield f'L{ln}.' + '.'.join(map(str, path)), path, s
    elif rel.endswith('.md'):
        ln = 1
        for para in re.split(r'(\n\s*\n)', text):
            if para.strip():
                yield f'L{ln}', (), para
            ln += para.count('\n')


def verbatim_check(released: list[str], base: Path, srcs: Sources) -> tuple[list[str], dict]:
    """12-word shingle check of every released text file against every source; returns failures and the share of each
    paper text that appears verbatim somewhere in the release."""
    fails, cover = [], defaultdict(set)
    for rel in released:
        if not rel.endswith(('.json', '.jsonl', '.md')):
            continue
        spans = defaultdict(list)
        for sid, (loc, path, s) in enumerate(text_units(rel, (base / rel).read_text())):
            if exempt(path):
                continue
            toks, st, en = norm_tokens(s)
            for d, a, b, i0, i1 in srcs.runs(toks):
                if mostly_numbers(toks[i0:i1]):
                    continue
                spans[d].append((a, b, sid))
                if srcs.docs[d][0] in ('paper', 'ftin'):
                    cover[d].update(range(a, b))
                nws = len(s[st[i0]:en[i1 - 1]].split())
                if nws > LIMIT:
                    fails.append(f'verbatim passage of {nws} words from a {srcs.docs[d][0]} text: {rel} :: {loc}')
        for d, sp in spans.items():
            for a, b, sl in passage_over(sp):
                fails.append(f'{len(sl)} strings chain into a verbatim passage of {b - a} words from a '
                             f'{srcs.docs[d][0]} text: {rel}')
    pct = [100 * len(c) / len(srcs.docs[d][3]) for d, c in cover.items()]
    share = {'source_texts_with_a_match': len(pct),
             'median_pct': round(float(np.median(pct)), 1) if pct else 0.0,
             'max_pct': round(max(pct), 1) if pct else 0.0,
             'method': 'share of the words of each paper text (publisher XML text or pdftotext, counted separately) '
                       'covered by verbatim runs of 12 words or more found anywhere in the release; an upper bound, '
                       'since paraphrased fields that share 12 words with the paper count too'}
    return fails, share


# ------------------------------------------------------------------------------------------------------------ build
def select(src: Path) -> tuple[list[str], Counter, Counter]:
    """Return released relative paths, files dropped per deny reason, files dropped by the embargo."""
    cand = set()
    for pat in ALLOW:
        for p in src.glob(pat):
            if p.is_file():
                cand.add(p.relative_to(src).as_posix())
    deny, keep = Counter(), []
    for rel in sorted(cand):
        r = next((why for pat, why in DENY if re.search(pat, rel)), None)
        if r:
            deny[r] += 1
        else:
            keep.append(rel)
    return keep, deny, Counter()


STATE_REL = 'analysis/codings/api/state.json'
FIG03_REL = 'data/roadmap/figures/paper/fig03_reliability.json'
QUEUES = ['download-queue.json', 'data/roadmap/download-queue.before-refetch-2026-10-27.json']
QUEUE_FIELDS = ('doi', 'status', 'group', 'route', 'meta', 'updated', 'file')


def pseudonymize_state(st: dict, emb: Embargo) -> tuple[dict, int]:
    """Embargoed papers in state.json keep their cost, tokens, batch and validation message under a pseudonym per run
    tag ('withheld-007'), listed after the named papers; their Files API entries (file id, sha256 of the upload) are
    dropped by the JSON filter. The pseudonym order comes from a hash salted with the keys.env values, so it cannot be
    rebuilt from the public key list."""
    if not emb.keys:
        return st, 0
    salt = hashlib.sha256(''.join(v for _, v in secret_values()).encode() or os.urandom(16)).hexdigest()
    tagkeys = defaultdict(set)
    for k in list(st.get('done', {})) + list(st.get('failed', {})):
        tag, key = k.split(':', 1)
        if key in emb.keys:
            tagkeys[tag].add(key)
    for b in st.get('batches', []):
        tagkeys[b.get('tag')] |= {k for k in b.get('keys', []) if k in emb.keys}
    alias = {}
    for tag, ks in tagkeys.items():
        for i, key in enumerate(sorted(ks, key=lambda x: hashlib.sha256(f'{salt}|{tag}|{x}'.encode()).hexdigest()), 1):
            alias[(tag, key)] = f'withheld-{i:03d}'

    def remap(d):
        named, hidden = {}, {}
        for k, v in d.items():
            tag, key = k.split(':', 1)
            if (tag, key) in alias:
                hidden[f'{tag}:{alias[(tag, key)]}'] = v
            else:
                named[k] = v
        return named | dict(sorted(hidden.items()))
    out = dict(st)
    for f in ('done', 'failed'):
        if isinstance(st.get(f), dict):
            out[f] = remap(st[f])
    out['batches'] = [{**b, 'keys': [k for k in b.get('keys', []) if (b.get('tag'), k) not in alias]
                       + sorted(alias[(b.get('tag'), k)] for k in b.get('keys', []) if (b.get('tag'), k) in alias)}
                      for b in st.get('batches', [])]
    return out, len(alias)


def queue_copy(q: dict) -> dict:
    """Fetch state for reruns: roadmap keys only, a few fields, file paths without the local home directory."""
    out = {}
    for k, v in q.items():
        if not k.startswith('g22_'):
            continue
        r = {f: v[f] for f in QUEUE_FIELDS if f in v}
        if r.get('file'):
            i = r['file'].find('private/')
            r['file'] = r['file'][i:] if i >= 0 else Path(r['file']).name
        out[k] = r
    return out


def build(src: Path, emb: Embargo, srcs: Sources) -> dict:
    rels, deny, _ = select(src)
    embargo_files = Counter()
    per_file = {}
    long_fail, quote_fail, abstract_fail = [], [], []
    released = []
    if TMP.exists():
        shutil.rmtree(TMP)
    for rel in rels + [q for q in QUEUES if (src / q).is_file()]:
        p = src / rel
        if emb.keys and file_key(rel) in emb.keys:
            embargo_files[str(Path(rel).parent)] += 1
            continue
        dest = TMP / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith('.json') or rel.endswith('.jsonl'):
            jf = JsonFilter(emb)
            if rel.endswith('.jsonl'):
                rows = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
                new = jf.run(rows)
                data = new
                if n := cut_chains(rel, data, srcs):
                    jf.c['strings cut where they chained into a passage over 25 words'] += n
                if new != rows:
                    dest.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in new))
                else:
                    shutil.copy2(p, dest)
            else:
                orig = json.loads(p.read_text())
                if emb.keys and isinstance(orig, dict) and isinstance(orig.get('key'), str) and emb.is_id(orig['key']):
                    embargo_files[str(Path(rel).parent)] += 1
                    continue
                pre = orig
                if rel in QUEUES:
                    pre = queue_copy(orig)
                    jf.c['queue entries kept (roadmap keys)'] = len(pre)
                if rel == STATE_REL:
                    pre, n = pseudonymize_state(orig, emb)
                    if n:
                        jf.c['state entries kept under a pseudonym (embargo)'] += n
                data = jf.run(pre)
                if rel == FIG03_REL and emb.keys:
                    pp = data.get('numbers', {}).get('a_test_retest', {}).get('per_paper')
                    if isinstance(pp, dict):
                        for f in pp:
                            pp[f] = sorted(pp[f])
                        jf.c['per-paper similarity lists sorted (embargo)'] += len(pp)
                if n := cut_chains(rel, data, srcs):
                    jf.c['strings cut where they chained into a passage over 25 words'] += n
                if data != orig:
                    dest.write_text(json.dumps(data, indent=1, ensure_ascii=False))
                else:
                    shutil.copy2(p, dest)
            if jf.c:
                per_file[rel] = dict(jf.c)
            for path, s in strings(data):
                n = len(s.split())
                named = [q for q in path if q != '[]']
                k = named[-1] if named else None
                pair = tuple(named[-2:]) if len(named) >= 2 else ()
                prose = k in LONG_OK or pair in LONG_OK_PATHS
                if n > 60 and not prose:
                    long_fail.append(f'{rel} :: {".".join(map(str, path))} ({n} words)')
                if prose and (lq := long_quotes(s)):
                    quote_fail += [f'{rel} :: {".".join(map(str, path))} quoted passage of {len(q.split())} words' for q in lq]
                if k and 'abstract' in str(k).lower() and n > 25:
                    abstract_fail.append(f'{rel} :: {".".join(map(str, path))}')
            for path, k, v in keys_of(data):
                if str(k) == 'abstract_inverted_index':
                    abstract_fail.append(f'{rel} :: {".".join(map(str, path))}.abstract_inverted_index')
        elif rel.endswith('.md'):
            c = Counter()
            text = md_filter(p.read_text(), emb, c, inline=rel in INLINE_MD)
            dest.write_text(text)
            if c:
                per_file[rel] = dict(c)
            quote_fail += [f'{rel} :: quoted passage of {len(q.split())} words' for q in long_quotes(text)]
        else:
            shutil.copy2(p, dest)
        released.append(rel)
    return {'released': released, 'deny': deny, 'embargo_files': embargo_files, 'per_file': per_file,
            'long_fail': long_fail, 'quote_fail': quote_fail, 'abstract_fail': abstract_fail}


def checks(src: Path, emb: Embargo, res: dict, srcs: Sources) -> list[str]:
    fails = []
    vfails, res['quoted_share'] = verbatim_check(res['released'], TMP, srcs)
    fails += vfails
    fails += [f'string over 60 words: {x}' for x in res['long_fail']]
    fails += [f'quoted passage over 25 words: {x}' for x in res['quote_fail']]
    fails += [f'abstract field: {x}' for x in res['abstract_fail']]
    secrets = secret_values()
    # quotes of embargoed papers (from every coding tag and the entry audit)
    emb_q, shared = set(), set()
    if emb.keys:
        for p in (src / 'analysis' / 'codings' / 'api').glob('*/*.json'):
            qs = {norm_words(q) for q in coding_quotes(json.loads(p.read_text()))}
            (emb_q if p.stem.split('.')[0] in emb.keys else shared).update(qs)
        D = src / 'data' / 'roadmap' / 'derived'
        for f in [D / 'entry' / 'audit_sample.json', D / 'entry' / 'blind_audit.json', D / 'review' / 'visibility_labels.json']:
            if f.is_file():
                for rec in records(json.loads(f.read_text())['data']):
                    (emb_q if rec.get('key') in emb.keys else shared).update(norm_words(q) for q in coding_quotes(rec))
        for p in (D / 'format_test' / 'codings').glob('*.json'):
            qs = {norm_words(q) for q in coding_quotes(json.loads(p.read_text()))}
            (emb_q if file_key(p.name) in emb.keys else shared).update(qs)
        emb_q = {q for q in emb_q if len(q.split()) >= 8 and q not in shared}
    by_head = defaultdict(list)
    for q in emb_q:
        by_head[' '.join(q.split()[:6])].append(q)
    for rel in res['released']:
        p = TMP / rel
        size = p.stat().st_size
        if size > MAX_BYTES:
            fails.append(f'file over 20 MB: {rel} ({size / 1e6:.1f} MB)')
        if rel.lower().endswith('.pdf'):
            fails.append(f'PDF in release: {rel}')
        raw = p.read_bytes()
        if rel.endswith(('.json', '.jsonl', '.md')) and EMAIL.search(raw):
            fails.append(f'email address in {rel}')
        for pat in KEYLIKE:
            if re.search(pat.encode(), raw):
                fails.append(f'key-like string {pat!r} in {rel}')
        for name, val in secrets:
            if val.encode() in raw:
                fails.append(f'value of {name} from keys.env in {rel}')
        if rel.endswith(('.json', '.jsonl', '.md')):
            text = raw.decode('utf-8')
            if emb.keys and (rel.endswith('.md') and emb.in_text(text) or emb.ids_in(text)):
                fails.append(f'embargoed identifier left in {rel}')
            if emb.descriptor_in(text):
                fails.append(f'embargo descriptor (prose naming a blind-set paper) left in {rel}')
            if emb_q:
                if rel.endswith('.md'):
                    blob = norm_words(text)
                else:
                    blob = ' | '.join(norm_words(s) for _, s in strings(
                        [json.loads(line) for line in text.splitlines() if line.strip()] if rel.endswith('.jsonl') else json.loads(text)))
                w = blob.split()
                heads = {' '.join(w[i:i + 6]) for i in range(max(0, len(w) - 5))}
                for h in heads & by_head.keys():
                    for q in by_head[h]:
                        if q in blob:
                            fails.append(f'quote from an embargoed paper in {rel}')
    return fails


# ----------------------------------------------------------------------------------------------------------- README
README = """# Roadmap data release

Data, model codings, figures and reports of the roadmap study in this repository (how Earth-science papers move
through the inquiry graph v0.4.2, coded by a language model under codebook 1.5.0). Built on {date} by
`tools/roadmap/g22_release.py` from the private working tree (public commit {cp}, private commit {cq}).
{n_files} files, {mb:.1f} MB. `RELEASE.json` lists every file with its sha256 and size.

The folder mirrors the layout of the private tree (`private/` in the scripts' docstrings and provenance blocks is this
folder), so every path written as `private/...` in a report or provenance block is found here without the `private/`
prefix.

## What is here

| Path | Content |
|:--|:--|
| `data/roadmap/derived/` | every derived table: the 2022 pool and preselection (OpenAlex metadata, no abstracts), eligibility screen decisions, gold set, metrics, round-1 and round-2 manifests, first-calculation results (g13), outcomes (g17), topics and journals (g20), entry-state evaluation (g21), open-review index and visibility labels (g16), report numbers (g19), format test (f01) |
| `data/roadmap/figures/paper/` | paper figures fig01-fig13 as PNG, each with its provenance JSON (inputs with sha256, numbers drawn, draft caption) |
| `data/roadmap/{{EXPERIMENTS,DECISIONS,MANIFEST}}.md` | experiment log, every selection rule and exclusion, one row per script run |
| `analysis/codings/api/<tag>/` | the model codings, one JSON per paper: `calc1` round 1, `gold-r2` second coding of the gold papers (test-retest), `calc1-review` papers with open review, `fmt-*` format test |
| `analysis/codings/api/state.json` | batch log of the coding runs: batches, per-paper cost and tokens, Files API ids |
| `download-queue.json`, `data/roadmap/download-queue.before-refetch-2026-10-27.json` | full-text fetch state of the roadmap papers (DOI, status, route, file name, title, year, venue), now and on October 27, 2026; the scripts read them to know which papers had full text |
| `text/`, `analysis/` | the reports: {docs} |

## What is not here, and why

| Withheld | Why |
|:--|:--|
| Paper full texts (PDF, publisher XML, extracted text) | publishers' terms: we quote papers, we do not republish them |
| Abstracts (eligibility screen input) | same reason |
| Open-review discussion texts and the excerpts given to the visibility coder | same reason |
| The raw OpenAlex cache | size; every query can be refetched from OpenAlex |
| The human-coder app and its packets, who codes what | part of the blind human coding |
| Per-paper records of the {n_emb} papers under embargo (below) | blinding |
| Figure PDFs | the repository does not carry PDFs; PNG and provenance JSON are here |

Quotes. A field that quotes a paper (`quote`, `entry.evidence`) is cut to 25 words, the codebook limit, with " [...]"
appended; {n_cut} quotes were longer. The marker keeps such a coding invalid under `tools/check_coding.py`, as it was,
so reruns use the same papers. Separate strings of one coding that continue each other in the paper (a V-check quote
that picks up where a step quote stops) are cut where together they would pass 25 words; {n_chain} strings were
shortened this way, with " [...] " where words were removed. Every string in the release was then compared with every
paper text, open-review file and abstract we hold: no verbatim passage, single or chained, is longer than 25 words,
except bibliographic titles and citation strings. Taken together, the quotes and coded fields of this release reproduce
a median of {q_med}% of the words of a coded paper's text and at most {q_max}% ({q_n} paper texts with any 12-word
match; an upper bound, since paraphrased fields that share 12 words with the paper count too).

## Embargo

{n_human} papers will be coded by four people (derived/gold/human_assignment.json, not released) and {n_audit} papers
were drawn for the entry-state audit, which may also go to them ({n_overlap} papers are in both: {n_emb} in all). Until
their coding is done, no per-paper record of these papers is released: their coding files, their rows in the derived
tables (the pool and preselection files included: `pool.json` holds {pool_n} rows), the audit rows and blind
re-codings, and the sentences in the reports that name or describe them. In `state.json` their cost, token and
validation entries are kept under pseudonyms (`withheld-001`, ...) so that total spend reproduces.

Aggregates computed over many papers (results.json, outcomes.json, entry_state.json, topics_journals.json and the
figures) are released as computed on the full set; they include these papers. One consequence: a table cell of such an
aggregate minus the released per-paper records of the same cell gives the embargoed papers' distribution in that cell.
For the model's entry state, where 78% of round-1 papers are `problem`, a few small cells (a subfield or publisher
family with 4 or 5 embargoed papers) contain only `problem` papers, so the model's label of those papers can be inferred.
The embargo hides the model's per-paper coding from the human coders; it does not hide aggregates. The embargo lifts
when the four coders have finished; the release is then rebuilt with `python tools/roadmap/g22_release.py
--lift-embargo` and the withheld records appear.

## Rerunning the analyses

Copy the folder first: reruns overwrite outputs and append to MANIFEST.md, and the released outputs are the full-set
record, which a rerun from this folder cannot reproduce while the embargo holds. From the repository root, with the
conda environment of the repository:

```sh
cp -r data/roadmap-release /tmp/roadmap-rerun
METASCIENCE_PRIVATE=/tmp/roadmap-rerun python tools/roadmap/g13_calc1_results.py
METASCIENCE_PRIVATE=/tmp/roadmap-rerun python tools/roadmap/g17_outcomes.py
```

`METASCIENCE_PRIVATE` points the scripts at a private tree (default `private/`); a relative path is read from the
current directory. While the embargo holds, reruns use the papers released here, so their numbers differ from the
reports, which used all coded papers. g22 ran g13 and g17 on a copy of this release when it built it; a correct rerun
gives:

| Number | Released (all coded papers) | Rerun from this release |
|:--|:--|:--|
{expected}

Scripts that fetch or read full texts (f00, f01, g08, g10, g15, the coding runs) need the withheld files and do not run
from the release.

Checked on October 27, 2026 against a copy of the release (embargo on):

| Runs | Does not run, and what it needs |
|:--|:--|
| g13_calc1_results, g17_outcomes, g21_entry_state (without its blind-audit section, withheld); fig01, fig02 (fig02 counts PDFs on disk, of which the release has none), fig04, fig07, fig08, fig09, fig10; fig11 and fig12, which draw the released full-set topics_journals.json against the released codings and report that as a data issue (`make_all.py` prints "ok (stale input)") | g19_report_numbers: stops at the open-model text route, which needs the PDFs and XML texts; later steps also read the reliability study (`analysis/reliability/`) and `analysis/success-set/loops/REPORT.md`, which are not part of the release |
| | g20_topics_journals: OpenAlex topic names come from the raw cache, which is not released; with network access it refetches them from OpenAlex |
| | fig03: the format-test papers are all under embargo; fig13: the blind audit is under embargo |
| | g14_papers_vs_agents, fig05, fig06: the agent codings of the reliability study (`analysis/reliability/`, not released) |

`tools/roadmap/figures/make_all.py` refreshes the book's `assets/roadmap/` figures only when it runs on the private tree;
with `METASCIENCE_PRIVATE` set it leaves them alone.

## Licence and citation

Data and text in this folder: CC BY 4.0 (see `LICENSE`, section 1). Code in `tools/`: MIT. Rights in the papers quoted
remain with their holders; a quotation here does not license reuse of the source.

Cite as: Denolle, M. ({year}). *Roadmap data release: model codings of Earth-science papers on the inquiry graph*
(release of {date}, commit {cp}). Denolle Lab, University of Washington.
https://github.com/Denolle-Lab/metascience-and-AI/tree/main/data/roadmap-release
"""

PI_RULE = 'quoting individual papers is fine, we can just not republish papers. everything else can go public'


def headline(base: Path) -> dict:
    D = base / 'data' / 'roadmap' / 'derived'
    r = json.loads((D / 'calc1' / 'results.json').read_text())['data']
    o = json.loads((D / 'outcomes' / 'outcomes.json').read_text())['data']
    es = r['corpus']['entry_state'].get('problem') or [None, None]
    return {'g13 papers coded (round 1, valid)': r['corpus']['papers_coded'], 'g13 eligible papers': r['corpus']['eligible'],
            'g13 coverage': r['corpus']['coverage'], 'g13 test-retest pairs': r['test_retest']['papers'],
            'g13 entry state problem (papers, share)': es, 'g17 papers': o['papers'], 'g17 tests': o['tests'],
            'g17 tests with q < 0.1': o['q_below_0.1']}


def expected_rerun(tmp: Path) -> dict:
    """Run g13 and g17 on a scratch copy of the new release; return their headline numbers (or the error)."""
    with tempfile.TemporaryDirectory(prefix='roadmap-rerun-') as d:
        cp = Path(d) / 'release'
        shutil.copytree(tmp, cp)
        env = {**os.environ, 'METASCIENCE_PRIVATE': str(cp)}
        for s in ['g13_calc1_results.py', 'g17_outcomes.py']:
            r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'roadmap' / s)], cwd=ROOT, env=env,
                               capture_output=True, text=True)
            if r.returncode:
                return {'error': f'{s} failed on the release copy: {r.stderr.strip().splitlines()[-1:]}'}
        return headline(cp)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--lift-embargo', action='store_true', help='release the embargoed papers (after the human coding)')
    a = ap.parse_args()
    src = PRIVATE
    if src.resolve() == OUT.resolve():
        sys.exit('METASCIENCE_PRIVATE points at the release itself; run g22 from the private tree')
    emb = Embargo(src, a.lift_embargo)
    srcs = Sources(src)
    print(f'verbatim check sources: {srcs.counts}; {srcs.pdf_failed} PDFs without text')
    res = build(src, emb, srcs)
    fails = checks(src, emb, res, srcs)
    if fails:
        shutil.rmtree(TMP, ignore_errors=True)
        print(f'release NOT built: {len(fails)} check(s) failed; the previous release is unchanged')
        for f in fails[:200]:
            print('  ', f)
        return 1
    today = dt.date.today().isoformat()
    cp = git_commit(ROOT, ['tools/roadmap'])
    cq = git_commit(src, ['data/roadmap', 'analysis/codings/api', 'text', 'analysis'])
    tot = Counter()
    for c in res['per_file'].values():
        tot.update(c)
    full = headline(src)
    rerun = expected_rerun(TMP)
    if 'error' in rerun:
        expected = f'| rerun failed | | {rerun["error"]} |'
    else:
        expected = '\n'.join(f'| {k} | {full[k]} | {rerun[k]} |' for k in full)
    pool = TMP / 'data' / 'roadmap' / 'derived' / 'gold' / 'pool.json'
    pool_n = len(json.loads(pool.read_text())['data']) if pool.is_file() else 0
    pool_full = len(json.loads((src / 'data' / 'roadmap' / 'derived' / 'gold' / 'pool.json').read_text())['data'])
    qs = res['quoted_share']
    files = []
    for rel in res['released']:
        p = TMP / rel
        files.append({'path': rel, 'bytes': p.stat().st_size, 'sha256': sha256(p)})
    n_bytes = sum(f['bytes'] for f in files)
    docs = ', '.join(f'`{d}`' for d in DOCS)
    readme = README.format(date=today, cp=cp, cq=cq, n_files=len(files) + 2, mb=n_bytes / 1e6, docs=docs,
                           n_emb=len(emb.keys), n_human=len(emb.human), n_audit=len(emb.audit),
                           n_overlap=len(emb.human & emb.audit), n_cut=tot['quotes cut to 25 words'],
                           n_chain=tot['strings cut where they chained into a passage over 25 words'],
                           q_med=qs['median_pct'], q_max=qs['max_pct'], q_n=qs['source_texts_with_a_match'],
                           pool_n=f'{pool_n:,} of {pool_full:,}', expected=expected, year=today[:4])
    if not emb.keys:
        readme = re.sub(r'## Embargo\n.*?\n## ', '## Embargo\n\nLifted: every coded paper is released.\n\n## ', readme, flags=re.S)
    (TMP / 'README.md').write_text(readme)
    files.append({'path': 'README.md', 'bytes': (TMP / 'README.md').stat().st_size, 'sha256': sha256(TMP / 'README.md')})
    rel_info = {
        'date': today, 'script': 'tools/roadmap/g22_release.py', 'commit_public': cp, 'commit_private': cq,
        'rule': {'by': 'Marine Denolle (PI)', 'date': '2026-10-27', 'words': PI_RULE},
        'embargo': {'active': bool(emb.keys), 'papers': len(emb.keys), 'human_coding_set': len(emb.human),
                    'entry_audit_sample': len(emb.audit), 'in_both': len(emb.human & emb.audit),
                    'scope': 'no per-paper record (coding files, rows of derived tables, audit rows, report sentences '
                             'naming or describing a paper) of a paper in the human-coding set or the entry-audit '
                             'sample until the human coding ends; aggregates over many papers are released',
                    'set_by': 'proposed by the roadmap workflow to keep the human coders blind to the model codings; '
                              'confirmed by the PI on 2026-10-27 (keep until the human coding ends); quote volume '
                              'accepted as is; data released under CC BY 4.0 (LICENSE section 1)'},
        'quoted_share': qs,
        'expected_rerun': {'released': full, 'rerun_from_release': rerun},
        'n_files': len(files) + 1, 'bytes': sum(f['bytes'] for f in files),
        'dropped_files_by_rule': dict(res['deny']),
        'dropped_files_by_embargo': dict(sorted(res['embargo_files'].items())),
        'changes_per_file': dict(sorted(res['per_file'].items())),
        'changes_total': dict(tot),
        'files': files,
    }
    (TMP / 'RELEASE.json').write_text(json.dumps(rel_info, indent=1, ensure_ascii=False))
    if OUT.exists():
        shutil.rmtree(OUT)
    TMP.rename(OUT)
    log('g22_release.py', 'public data release data/roadmap-release', len(files) + 1,
        f'embargo {len(emb.keys)} papers; {sum(res["embargo_files"].values())} files withheld; {dict(tot)}')
    print(f'wrote {OUT.relative_to(ROOT)}: {len(files) + 1} files, {rel_info["bytes"] / 1e6:.1f} MB')
    print('dropped by rule:', dict(res['deny']))
    print('dropped by embargo:', dict(res['embargo_files']))
    print('changes:', dict(tot))
    print('quoted share:', qs)
    print('expected rerun:', rerun)
    return 0


if __name__ == '__main__':
    sys.exit(main())
