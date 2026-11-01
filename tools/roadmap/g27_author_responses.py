"""Phase 2c: author responses as a window on the unreported workflow (the translation from research to paper).

Question. In the open review of a Copernicus (EGU) paper, authors answer referees in their own voice. Those answers
sometimes say what the paper itself does not: what was tried and dropped, in which order the work was done, what limited
it, why a choice was made. How often do author responses disclose such workflow information, of which kinds, and how
often does the disclosure reach the final paper?

Status. Exploratory, single labeler: one Claude Code agent (Claude Opus 5.5) read the author text and assigned every
label and every final-paper check. No second labeler, no adjudication, no agreement statistic. No paid API call.

Scheme (fixed before labeling; one disclosure = one author statement of one kind; a paragraph may hold several)
  tried_dropped     a method, dataset, parameter, model setting or analysis that the authors say they tried, tested or
                    ran and did not report, or reported only as "results not shown" / "similar results" (includes
                    sensitivity tests run before or during review whose outcome is given only in the response)
  order_of_work     what was done first or later: the sequence of the work, an earlier design, what existed before
                    the study started, what was done after submission, what is planned in follow-up work
  constraint        a limit on the work: data access or availability, time, funding or project scope, instrument or
                    sensor limits, computing cost, field logistics, permissions, staff
  unstated_reason   the reason for a methodological or data choice, given in the response because a referee asked
                    about a choice the discussion manuscript states without its reason
  added_for_review  a new analysis, computation, experiment, dataset or quantitative test carried out for the review
                    (text edits, reference additions, figure styling and rewording are not counted)
  claim_narrowed    the authors weaken, qualify or remove a claim or interpretation (scope, generality, causal
                    language, certainty)
  writing_process   how the paper itself was composed, as distinct from the research: a figure, section or framing
                    drafted and cut, debated among the authors, shaped by length or format; added after the first five
                    papers had been labelled (the PI's question about the translation from workflow to paper), and
                    those five were re-read for it
  none              an author paragraph with none of the above (assigned by this script to every unit without a label)

Final-paper check (one per disclosure; searched in the published text from the publisher XML, located [§n ¶m])
  present   the final paper states the specific content of the disclosure (the method tried, the order, the limit,
            the reason, the added analysis, the narrowed wording)
  partly    the final paper touches the topic but not the specific content (e.g. names the alternative method but not
            that it was tried; mentions a limit in general terms only)
  absent    the specific content is not found in the final paper
For a claim or analysis the authors say they removed, 'present' means the final paper no longer carries it; such a
disclosure has "removed": true and no final_quote. For writing_process, 'present' means the paper itself says something
about the composition step (it rarely does).
The search covers the main text, figure captions and appendices as the publisher XML gives them; the final paper's
supplement and data-availability statements are not searched, so 'absent' is an upper bound for some kinds.

Units of reading (built by 'extract')
  AC  every author-comment paragraph of discussion.txt: [ACn ¶k] (inline), [ACn p.k] (comment posted as PDF),
      [ACn-S p.k] (comment supplement). Copernicus page furniture is stripped; a unit under 12 words is dropped; a unit
      whose 8-word shingles are at least 90% contained in earlier AC units of the paper (the same reply posted twice) is dropped.
      Pages whose font maps to shifted code points (pdftotext gives 'WKH' for 'the') are decoded (decode_shift).
  AR  every page of the author-response PDFs (<stem>-AR<n>.pdf, the responses filed with each revision, including
      replies to the second-round referee reports that the open discussion does not carry), kept only where the page
      text is not already in the AC text of that paper: share of its 8-word shingles found in the AC text < 0.5.
Reading protocol (what the labeler saw). Each unit is split into sentences, and each sentence is classed
  quoted_referee  >= 50% of its 8-word shingles occur in the referee, community or editor text of the same paper
                  (RC/CC/EC paragraphs of discussion.txt and the second-round referee reports <stem>-RR<n>.pdf)
  quoted_paper    else >= 50% of its shingles occur in the final paper (the authors quoting their revised text)
  own             the rest: the authors' own words
A cue lexicon (CUES, broad, per kind) marks own sentences with '>>' as an attention aid. reading/<key>.txt shows
every own sentence of every unit (quoted sentences are dropped and counted in the unit header); the labeler read all
of it, paper by paper. A cue-only protocol (flagged sentences plus one neighbour) was tried first and kept 71% of the
own words (267k of 378k), too little saving to justify its recall loss, so it was dropped.
read_units in a label file is the unit count of reading/<key>.txt when that paper was labelled. 'extract' was rerun
after 11 papers had been labelled (duplicate-reply removal), so for those read_units exceeds the current count; merge
checks that every labelled unit still exists (unit_found), and all do.

Inputs   private/data/roadmap/review/<key>/discussion.txt and <stem>-AR<n>.pdf (g15_open_review.py);
         final text private/data/roadmap/pdfs/gold/<key>.xml.txt via private/download-queue.json;
         derived/translation/labels/<key>.json (the labeler's file, one per paper; see LABEL FORMAT)
Outputs  derived/translation/author_units.jsonl (extract; each unit with its sentence classes),
         derived/translation/reading/<key>.txt (extract),
         derived/translation/author_responses.json (merge: units with labels, per-paper and per-kind counts,
         quote checks), derived/translation/AUTHOR_RESPONSES.md (merge: summary),
         derived/translation/fig_author_responses.png (merge: disclosures per kind by final-paper status, and the
         number of papers with at least one disclosure of the kind)
Label format, derived/translation/labels/<key>.json:
         {"key": ..., "read_units": n, "disclosures": [{"unit": "AC1 ¶3", "kind": "tried_dropped",
          "quote": "<= 25 words verbatim from the unit", "content": "<= 25 words, what exactly was disclosed",
          "final": "present|partly|absent", "final_loc": "§3 ¶2" or null, "final_quote": "<= 25 words verbatim" or null}]}
Run:     python tools/roadmap/g27_author_responses.py extract
         (label: write derived/translation/labels/<key>.json for every paper)
         python tools/roadmap/g27_author_responses.py merge
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from common import PRIVATE, DATA, DERIVED, TODAY, commit, write_json, log, private_path, rel

REVIEW = DATA / 'review'
QUEUE = PRIVATE / 'download-queue.json'
OUT = DERIVED / 'translation'
UNITS = OUT / 'author_units.jsonl'
READ = OUT / 'reading'
LABELS = OUT / 'labels'
KINDS = ['tried_dropped', 'order_of_work', 'constraint', 'unstated_reason', 'added_for_review', 'claim_narrowed',
         'writing_process']
WORKFLOW = ['tried_dropped', 'order_of_work', 'constraint', 'unstated_reason']   # disclosures about the unreported work
FINAL = ['present', 'partly', 'absent']
MIN_WORDS, SHINGLE, COVER, QUOTED, DUP = 12, 8, 0.5, 0.5, 0.9
CUES = {
    'tried_dropped': r'\b(tried|tested|test(ed)? (with|whether)|attempt\w*|experiment\w* with|initially|originally|at first|'
                     r'preliminary|not shown|similar results|did not (improve|change|affect|alter)|no significant (difference|change)|'
                     r'discarded|abandon\w*|decided not|sensitivity (test|analys|experiment)\w*|we (also )?(checked|verified|ran)|'
                     r'earlier version|previous version|alternative\w*|instead|rather than|did not (use|include|consider|show)|we did|'
                     r'we have (done|tried|tested|checked|run)|in fact|indeed|robust\w*)\b',
    'order_of_work': r'\b(first|afterwards|later|subsequently|at the time|when we (started|began)|before (the|we)|'
                     r'after (the|we) |in the meantime|meanwhile|since (the )?submission|ongoing|follow[- ]up|future (work|stud)\w*|'
                     r'next step|companion paper|in preparation|was designed|were designed|started|earlier|previous\w*|'
                     r'when (we|the)|already|yet|at that time|years? ago|then)\b',
    'constraint':    r'\b(not available|unavailable|no data|lack of|limited|limitation\w*|computational\w*|cost\w*|expensive|'
                     r'funding|funded|budget|project|instrument\w*|sensor\w*|malfunction\w*|outage|gaps?|access|permission\w*|'
                     r'restricted|proprietary|confidential|field (season|campaign|work)|covid|pandemic|logistic\w*|'
                     r'beyond the scope|out of (the )?scope|not feasible|infeasible|impossible|could not|cannot|unable|time[- ]consuming|'
                     r'due to|only (one|two|a few|available)|not possible|difficult|resources?|money|staff)\b',
    'unstated_reason': r'\b(because|the reason|reasons?|chose|choose|chosen|decided|decision|selected|opted|prefer\w*|'
                       r'motivat\w*|rationale|justif\w*|why we|since|as the|we used|we use|in order to|aim\w*|purpose)\b',
    'added_for_review': r'\b(we (have )?(now )?(added|performed|carried out|computed|calculated|ran|conducted|included|extended|repeated)|'
                        r'new (figure|analysis|simulation|experiment|test)\w*|additional (analys|simulation|experiment|test|figure)\w*)\b',
    'claim_narrowed': r'\b(rephras\w*|reword\w*|tone[d]? down|soften\w*|overstat\w*|too strong|more (careful|cautious)|'
                      r'caution\w*|qualif\w*|speculati\w*|removed (the|this) (statement|claim|sentence)|we agree)\b',
}
FURNITURE = [r'^.*?CC BY 4\.0 Licen[sc]e\.\s*', r'Interactive comment on “[^”]*” by [^.]*?et al\.\s*', r'Interactive comment',
             r'Printer-friendly version', r'Interactive discussion', r'Discussion paper', r'Full Screen / Esc',
             r'\bC\d{1,3}\b\s*$', r'Received and published: \d+ \w+ \d{4}',
             r'Please provide a reason why you see this comment as being abusive\.\s*(You might include your name and email but you can also stay anonymous\.)?',
             r'id="comment-body-\d+"[^>]*>', r'Citation ?: https://doi\.org/ ?\S+']


def norm(s: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', (s or '').lower().replace('-\n', ''))).strip()


def decode_shift(text: str) -> str:
    """Undo the fixed +29 code-point shift that some PDF fonts produce in pdftotext output ('WKH' for 'the');
    applied only when a page reads as shifted (at least three ' WKH ' tokens). A second, non-linear font encoding seen
    in one paper (quoted manuscript passages) is left as it is."""
    if text.count(' WKH ') < 3:
        return text
    return ''.join(chr(ord(c) + 29) if 33 <= ord(c) <= 93 else c for c in text)


def contains(hay: str, needle: str) -> bool:
    """Quote check: normalised substring, or the same ignoring spaces (PDF text breaks words at soft hyphens)."""
    a, b = norm(hay), norm(needle)
    return b in a or b.replace(' ', '') in a.replace(' ', '')


def clean(text: str) -> str:
    text = decode_shift(text)
    for pat in FURNITURE:
        text = re.sub(pat, ' ', text, flags=re.I)
    return re.sub(r'\s+', ' ', text).strip()


def shingles(words: list[str]) -> set[str]:
    return {' '.join(words[i:i + SHINGLE]) for i in range(max(0, len(words) - SHINGLE + 1))}


def ac_units(key: str, review: Path = REVIEW) -> list[dict]:
    """Author-comment paragraphs of discussion.txt, in order, with their locators."""
    units, seen = [], set()
    for line in (review / key / 'discussion.txt').read_text().splitlines():
        m = re.match(r'\[((AC\d+)(-S)? (?:¶|p\.)\d+)\] (.*)', line)
        if not m:
            continue
        text = clean(m.group(4))
        if len(text.split()) < MIN_WORDS:
            continue
        sh = shingles(norm(text).split())
        if sh and len(sh & seen) / len(sh) >= DUP:
            continue   # the same reply posted again under another AC number (or as its own supplement)
        seen |= sh
        units.append({'key': key, 'unit': m.group(1), 'source': 'AC', 'text': text})
    return units


def ar_units(key: str, ac_text: str, review: Path = REVIEW) -> tuple[list[dict], dict]:
    """Pages of the AR PDFs not already carried by the AC text (shingle coverage < COVER)."""
    have = shingles(norm(ac_text).split())
    units, stats = [], {'ar_pages': 0, 'ar_pages_kept': 0}
    for f in sorted((review / key).glob('*-AR*.pdf'), key=lambda p: int(re.search(r'-AR(\d+)', p.name).group(1))):
        tag = re.search(r'-(AR\d+)\.pdf', f.name).group(1)
        pages = subprocess.run(['pdftotext', '-layout', str(f), '-'], capture_output=True, text=True).stdout.split('\f')
        for n, pg in enumerate(pages, 1):
            text = clean(re.sub(r'\s+', ' ', pg))
            if len(text.split()) < MIN_WORDS:
                continue
            stats['ar_pages'] += 1
            sh = shingles(norm(text).split())
            cover = len(sh & have) / len(sh) if sh else 1.0
            if cover < COVER:
                stats['ar_pages_kept'] += 1
                units.append({'key': key, 'unit': f'{tag} p.{n}', 'source': 'AR', 'text': text, 'ac_cover': round(cover, 2)})
                have |= sh   # a later AR repeating this page is not read twice
    return units, stats


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z“"(\[])', text) if s.strip()]


def cue_kinds(sent: str) -> list[str]:
    s = sent.lower()
    return [k for k, pat in CUES.items() if re.search(pat, s)]


def referee_text(key: str, review: Path = REVIEW) -> str:
    lines = (review / key / 'discussion.txt').read_text().splitlines()
    txt = ' '.join(re.sub(r'^\[[^\]]+\] ', '', l) for l in lines if re.match(r'\[(RC|CC|EC)\d+', l))
    for f in (review / key).glob('*-RR*.pdf'):
        txt += ' ' + subprocess.run(['pdftotext', str(f), '-'], capture_output=True, text=True).stdout
    return txt


def classify(units: list[dict], ref: set, paper: set) -> None:
    for u in units:
        u['sents'] = []
        for s in sentences(u['text']):
            sh = shingles(norm(s).split())
            if sh and len(sh & ref) / len(sh) >= QUOTED:
                c = 'quoted_referee'
            elif sh and len(sh & paper) / len(sh) >= QUOTED:
                c = 'quoted_paper'
            else:
                c = 'own'
            u['sents'].append({'s': s, 'class': c, 'cues': cue_kinds(s) if c == 'own' else []})


def render(units: list[dict], full: bool) -> list[str]:
    lines = []
    for u in units:
        own = [x for x in u['sents'] if x['class'] == 'own']
        if not own:
            continue
        q = sum(len(x['s'].split()) for x in u['sents'] if x['class'] != 'own')
        lines.append(f'\n[{u["unit"]}] ({u["source"]}, {u["words"]} w; quoted dropped {q} w)')
        keep = [full or bool(x['cues']) for x in own]
        hidden = 0
        for x, k in zip(own, keep):
            if k:
                if hidden:
                    lines.append(f'   [... {hidden} w]')
                    hidden = 0
                lines.append(('>> ' if x['cues'] else '   ') + x['s'])
            else:
                hidden += len(x['s'].split())
        if hidden:
            lines.append(f'   [... {hidden} w]')
    return lines


def extract() -> None:
    keys = sorted(p.name for p in REVIEW.iterdir() if (p / 'discussion.txt').is_file())
    q = json.loads(QUEUE.read_text())
    for d in (READ, LABELS):
        d.mkdir(parents=True, exist_ok=True)
    allu, tot = [], Counter()
    for key in keys:
        ac = ac_units(key)
        ar, st = ar_units(key, ' '.join(u['text'] for u in ac))
        units = ac + ar
        paper, _ = final_text(key, q)
        classify(units, shingles(norm(referee_text(key)).split()), shingles(norm(paper).split()))
        for u in units:
            u['words'] = len(u['text'].split())
            for x in u['sents']:
                tot[x['class']] += len(x['s'].split())
                tot['own_cue'] += len(x['s'].split()) if x['cues'] else 0
        head = f'# {key}  units={len(units)} (AC {len(ac)}, AR {len(ar)} of {st["ar_pages"]} AR pages)'
        (READ / f'{key}.txt').write_text('\n'.join([head] + render(units, True)) + '\n')
        allu += units
    UNITS.write_text(''.join(json.dumps(u, ensure_ascii=False) + '\n' for u in allu))
    log('g27_author_responses.py extract', 'author-response units (AC paragraphs + uncovered AR pages)', len(allu),
        f'{len(keys)} papers; words by class {dict(tot)}')
    print(len(keys), 'papers', len(allu), 'units', dict(tot))


def final_text(key: str, q: dict) -> tuple[str, dict]:
    f = private_path(q[key]['file']).with_suffix('.xml.txt')
    txt = f.read_text()
    paras = {'TITLE': next((l[7:] for l in txt.splitlines() if l.startswith('TITLE: ')), '')}
    for line in txt.splitlines():
        m = re.match(r'\[(§[\d.]+ ¶\d+)\] (.*)', line)
        if m:
            paras[m.group(1)] = m.group(2)
    return txt, paras


def figure(summary: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    kf, n = summary['kind_final'], summary['papers']
    cols = {'present': '#0f4c5c', 'partly': '#7fa7b0', 'absent': '#d9a441'}
    fig, ax = plt.subplots(figsize=(8, 4.4))
    left = [0] * len(KINDS)
    for fl in FINAL:
        vals = [kf[k][fl] for k in KINDS]
        ax.barh(range(len(KINDS)), vals, left=left, color=cols[fl], label=f'{fl} in final paper')
        left = [a + b for a, b in zip(left, vals)]
    for i, k in enumerate(KINDS):
        ax.text(left[i] + 1.5, i, f"{summary['papers_with_kind'][k]} of {n} papers", va='center', fontsize=8, color='#153742')
    ax.set_yticks(range(len(KINDS)))
    ax.set_yticklabels([k.replace('_', ' ') + (' *' if k in WORKFLOW else '') for k in KINDS])
    ax.invert_yaxis()
    ax.set_xlabel('disclosures in author responses (count)', fontsize=9)
    ax.set_xlim(0, max(left) * 1.3)
    ax.legend(loc='lower right', frameon=False, fontsize=8)
    ax.spines[['top', 'right']].set_visible(False)
    fig.text(0.01, 0.01, f"Source: g27_author_responses.py merge ({commit()}, {TODAY}); {n} Copernicus papers, open review (g15);\n"
             "single labeler (one Claude Code agent), exploratory. * workflow kinds.", fontsize=7, color='#555')
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def merge() -> None:
    q = json.loads(QUEUE.read_text())
    units = [json.loads(l) for l in UNITS.read_text().splitlines()]
    by_key = defaultdict(dict)
    for u in units:
        by_key[u['key']][u['unit']] = u
    problems, rows, per_paper = [], [], {}
    for key in sorted(by_key):
        f = LABELS / f'{key}.json'
        if not f.is_file():
            problems.append(f'{key}: no label file')
            continue
        lab = json.loads(f.read_text())
        txt, paras = final_text(key, q)
        for i, d in enumerate(lab['disclosures'], 1):
            u = by_key[key].get(d['unit'])
            chk = {'unit_found': u is not None, 'quote_words': len(d['quote'].split()),
                   'quote_in_unit': bool(u) and contains(u['text'], d['quote'])}
            if d['kind'] not in KINDS:
                problems.append(f'{key} #{i}: kind {d["kind"]}')
            if d['final'] not in FINAL:
                problems.append(f'{key} #{i}: final {d["final"]}')
            if d.get('final_quote'):
                chk['final_quote_in_paper'] = contains(txt, d['final_quote'])
                chk['final_quote_at_loc'] = contains(paras.get(d.get('final_loc') or '', ''), d['final_quote'])
                chk['final_quote_words'] = len(d['final_quote'].split())
            elif d['final'] in ('present', 'partly') and not d.get('removed'):
                problems.append(f'{key} #{i}: {d["final"]} without final_quote')
            for k, ok in chk.items():
                if ok is False:
                    problems.append(f'{key} #{i} ({d["unit"]}): {k} failed')
            if chk['quote_words'] > 25 or chk.get('final_quote_words', 0) > 25:
                problems.append(f'{key} #{i}: quote over 25 words')
            rows.append({'key': key, 'n': i, **d, 'check': chk})
        kinds = Counter(d['kind'] for d in lab['disclosures'])
        labelled = {d['unit'] for d in lab['disclosures']}
        per_paper[key] = {
            'units': len(by_key[key]), 'units_read': lab.get('read_units'),
            'units_none': sum(1 for u in by_key[key] if u not in labelled),
            'words': sum(u['words'] for u in by_key[key].values()),
            'disclosures': len(lab['disclosures']),
            'by_kind': {k: kinds.get(k, 0) for k in KINDS},
            'by_kind_final': {k: dict(Counter(d['final'] for d in lab['disclosures'] if d['kind'] == k)) for k in KINDS if kinds.get(k)},
            'absent_any': sum(1 for d in lab['disclosures'] if d['final'] == 'absent'),
            'absent_workflow': sum(1 for d in lab['disclosures'] if d['final'] == 'absent' and d['kind'] in WORKFLOW),
        }
    n = len(per_paper)
    kind_final = {k: {fl: sum(1 for r in rows if r['kind'] == k and r['final'] == fl) for fl in FINAL} for k in KINDS}
    summary = {
        'papers': n, 'units': sum(p['units'] for p in per_paper.values()),
        'words': sum(p['words'] for p in per_paper.values()),
        'disclosures': len(rows), 'kind_final': kind_final,
        'papers_with_kind': {k: sum(1 for p in per_paper.values() if p['by_kind'][k]) for k in KINDS},
        'papers_with_absent_any': sum(1 for p in per_paper.values() if p['absent_any']),
        'papers_with_absent_workflow': sum(1 for p in per_paper.values() if p['absent_workflow']),
        'papers_with_workflow_disclosure': sum(1 for p in per_paper.values() if any(p['by_kind'][k] for k in WORKFLOW)),
        'quote_checks_failed': [p for p in problems if 'failed' in p or 'over 25' in p],
        'problems': problems,
        'labeler': 'one Claude Code agent (Claude Opus 5.5); single labeler, exploratory; no agreement statistic',
    }
    write_json(OUT / 'author_responses.json', {'summary': summary, 'per_paper': per_paper, 'disclosures': rows},
               inputs=[rel(UNITS), rel(LABELS) + '/*.json', 'private/data/roadmap/pdfs/gold/<key>.xml.txt'],
               params={'kinds': KINDS, 'workflow_kinds': WORKFLOW, 'final': FINAL, 'min_words': MIN_WORDS,
                       'shingle': SHINGLE, 'ar_cover_threshold': COVER})
    md = [f'# Author responses: disclosures and the final paper ({TODAY})', '',
          'Exploratory, single labeler (one Claude Code agent). Source: tools/roadmap/g27_author_responses.py.', '',
          f'Papers {n}; author-text units {summary["units"]}; words {summary["words"]}; disclosures {len(rows)}.', '',
          '| Kind | Papers with ≥1 | Disclosures | Present | Partly | Absent |', '|:--|--:|--:|--:|--:|--:|']
    for k in KINDS:
        kf = kind_final[k]
        md.append(f'| {k} | {summary["papers_with_kind"][k]} | {sum(kf.values())} | {kf["present"]} | {kf["partly"]} | {kf["absent"]} |')
    md += ['', f'Papers with at least one absent disclosure (any kind): {summary["papers_with_absent_any"]} of {n}.',
           f'Papers with at least one absent workflow disclosure ({", ".join(WORKFLOW)}): {summary["papers_with_absent_workflow"]} of {n}.',
           f'Papers with at least one workflow disclosure: {summary["papers_with_workflow_disclosure"]} of {n}.', '',
           f'Checks failed: {len(summary["quote_checks_failed"])}; other problems: {len(problems) - len(summary["quote_checks_failed"])}.']
    md += [f'- {p}' for p in problems[:60]]
    (OUT / 'AUTHOR_RESPONSES.md').write_text('\n'.join(md) + '\n')
    figure(summary, OUT / 'fig_author_responses.png')
    log('g27_author_responses.py merge', 'labelled disclosures', len(rows), f'{n} papers; {len(problems)} problems')
    print('\n'.join(md))


if __name__ == '__main__':
    {'extract': extract, 'merge': merge}[sys.argv[1]]()
