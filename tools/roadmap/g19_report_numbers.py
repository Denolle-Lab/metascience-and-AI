"""Every reported number that no other committed script writes to a file, recomputed from the data in one place.

The reports (review-visibility.qmd, workflow-outcomes.qmd, private/text/report-review-visibility.md,
private/text/olmo-meeting-brief.md, agents/coder/HANDOFF.md, private/data/roadmap/EXPERIMENTS.md) quote counts,
costs, token statistics and fetch tallies that were computed by hand. This script recomputes each of them, so every
number in a report traces to a script, a commit and an input file. Numbers that an existing script already writes
(g13 results.json, g14 papers_vs_agents.json, g16 visibility_results.json, g17 outcomes.json) are not repeated here,
except where a report needs a count that file holds only as a rounded share.

Inputs (paths from the repo root; read only)
  private/analysis/codings/api/state.json                  per-paper cost and token usage, failures, batches
  private/analysis/codings/api/{calc1,calc1-review,r2}/    model codings (r2 is optional: included when present)
  private/data/roadmap/derived/calc1/manifest.jsonl        525 eligible round-1 papers
  private/data/roadmap/derived/calc1/xml_status.json       publisher XML for round 1
  private/data/roadmap/derived/calc1/papers_vs_agents.json node use by agent loops (g14)
  private/data/roadmap/derived/gold/metrics.json           journal, publisher, is_oa, impact, n_refs (600)
  private/data/roadmap/derived/outcomes/outcomes.json      g17 tests
  private/data/roadmap/derived/review/open_review_index.json, visibility_labels.json, visibility_input/<key>.json
  private/data/roadmap/derived/r2/{preselect,eligibility}.json, derived/r2calc/{manifest.jsonl,xml_status.json}
  private/data/roadmap/download-queue.before-refetch-2026-10-27.json   fetch state on October 27, before the retry
  private/download-queue.json                                          fetch state now (the retry may still be running)
  PDFs and <key>.xml.txt files named in the queue; pdftotext for round-1 papers without XML (text-route statistics)
  private/analysis/codings/api/gold-r2/, derived/gold/{gold_set,human_assignment,pool}.json   gold set, test-retest
  private/data/roadmap/review/<key>/                         open-review files (what the review coder was given)
  private/analysis/success-set/loops/REPORT.md               October 21 loop pilot totals

Added after the October 27 report review: the round-1 backlog split (calc1.full_text_without_valid_coding*), gold-set
counts, the coder's annotation setup, steps and revisits merged and unmerged, V status by kind, run-to-run consistency
of the features behind the g17 associations, the rho interval half-width, review steps by trigger, what the review coder
read, a string scan of the published texts for revision phrases, a paper-level test of absences by node, and the
round-2 dry-run total. Added after the second review (audit_extra): a between-paper baseline for the test-retest
similarities, quote existence in the source text, the textbook order as an ordered subsequence, coded against uncoded
AGU papers, the within-family re-ranked estimate, the E4 labelers' Cohen kappa, the E1 text route and resubmissions.

Output
  private/data/roadmap/derived/report_numbers.json   {id: {value, definition, inputs}}, with provenance
  one row appended to private/data/roadmap/MANIFEST.md

Publisher rule (fixed): the DOI registrant prefix, mapped by PREFIX below. AGU journals are 10.1029 and count as AGU
even though Wiley publishes them; 10.1002 and 10.1111 count as Wiley. The OpenAlex 'publisher' field (first host in
the lineage that matched g02 HOSTS) labels some AGU journals as Wiley, so it is reported only as a secondary
'.openalex_field' tally, to trace the numbers already in EXPERIMENTS.md E7 and workflow-outcomes.qmd.

Percentiles: 'p90_nearest' is the nearest-rank value sorted(x)[ceil(0.9 n) - 1]; 'p90_linear' is numpy's default.

Run:  ROADMAP_SET=gold python tools/roadmap/g19_report_numbers.py
"""
from __future__ import annotations
import argparse
import json
import math
import os
import re
import statistics as st
from collections import Counter
from pathlib import Path

import numpy as np
from common import ROOT, PRIVATE, DATA, DERIVED, log, read_json, rel, write_json
from check_coding import validate
import code_papers_open as cpo  # tools/ (on the path via common); imports code_papers
import g17_outcomes as g17

API = PRIVATE / 'analysis' / 'codings' / 'api'
STATE = API / 'state.json'
QUEUE_NOW = PRIVATE / 'download-queue.json'
QUEUE_OCT27 = DATA / 'download-queue.before-refetch-2026-10-27.json'
PDFS = DATA / 'pdfs' / 'gold'
OUT = DERIVED / 'report_numbers.json'
CAP_USD = 250.0          # spending cap passed to code_papers.py --max-usd for every coding run
CHARS_PER_TOKEN = 4      # assumed, not measured: used only for the open-model context estimate
MAX_CHARS = 200_000      # code_papers_open.py --max-chars default

# DOI registrant prefix -> publisher, for every prefix in derived/gold/metrics.json and derived/r2/preselect.json
# (checked against their journal names on 2026-10-27). A prefix not listed reports as 'other (<prefix>)'.
# Russian-language journals translated by Pleiades (10.1134) and Allerton Press (10.3103) are distributed by
# Springer but keep their own registrant; GJI (10.1093) counts as OUP; BSSA and SRL (10.1785) as SSA.
PREFIX = {
    '10.1029': 'AGU', '10.1002': 'Wiley', '10.1111': 'Wiley', '10.1016': 'Elsevier',
    '10.1007': 'Springer Nature', '10.1038': 'Springer Nature', '10.1186': 'Springer Nature',
    '10.1134': 'Pleiades (via Springer)', '10.3103': 'Allerton Press (via Springer)', '10.1785': 'SSA',
    '10.1126': 'AAAS', '10.1093': 'OUP', '10.2113': 'GeoScienceWorld', '10.18261': 'Scandinavian University Press',
    '10.5194': 'Copernicus', '10.1155': 'Hindawi', '10.26443': 'Seismica', '10.26464': 'Science Press (Earth and Planetary Physics)',
    '10.4311': 'National Speleological Society', '10.5572': 'Korean Society for Atmospheric Environment',
}
VALUES: dict = {}


def put(key: str, value, definition: str, inputs: list[str]) -> None:
    VALUES[key] = {'value': value, 'definition': definition, 'inputs': inputs}


def publisher(doi: str) -> str:
    p = doi.split('/')[0]
    return PREFIX.get(p, f'other ({p})')


def clean(s: str | None) -> str:
    """Drop C0/C1 control characters (metrics.json journal names carry some) and normalize spaces."""
    return re.sub(r'\s+', ' ', re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s or '')).strip()


def p90_nearest(xs):
    xs = sorted(xs)
    return xs[math.ceil(0.9 * len(xs)) - 1]


def p90_linear(xs):
    return round(float(np.percentile(xs, 90)), 1)


def counter(c: Counter) -> dict:
    return dict(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def manifest(name: str) -> list[dict]:
    return [json.loads(l) for l in (DERIVED / name / 'manifest.jsonl').read_text().splitlines() if l.strip()]


def load_valid(tag: str) -> tuple[dict, dict]:
    """Codings of a tag: (valid key -> coding, invalid key -> validation errors)."""
    ok, bad = {}, {}
    for f in sorted((API / tag).glob('*.json')) if (API / tag).is_dir() else []:
        try:
            c = json.loads(f.read_text())
        except Exception as e:  # noqa: BLE001
            bad[f.stem] = [f'invalid_json: {e}']
            continue
        errs = validate(c)
        (bad if errs else ok)[c.get('key', f.stem)] = errs or c
    return ok, bad


def reason(errs: list[str]) -> str:
    if all('quote over 25 words' in e for e in errs):
        return 'quote over 25 words'
    return 'schema: ' + '; '.join(e for e in errs if 'quote over 25 words' not in e)


# ---------------------------------------------------------------- costs and tokens (state.json)
def costs(state: dict) -> None:
    I = ['private/analysis/codings/api/state.json']
    done, batches = state['done'], state['batches']
    tags = sorted({k.split(':')[0] for k in done} | {b['tag'] for b in batches})
    exp = {'fmt': 'E0', 'calc1': 'E1', 'gold-r2': 'E2', 'calc1-review': 'E3', 'r2': 'E7'}
    group = lambda t: 'fmt' if t.startswith('fmt-') else t
    for g in sorted({group(t) for t in tags}):
        d = [v for k, v in done.items() if group(k.split(':')[0]) == g]
        usd = [v['usd'] for v in d]
        e = exp.get(g, g)
        put(f'cost.{e}.usd', round(sum(usd), 4), f'Sum of recorded per-paper cost (state.json done[*].usd) over valid codings of tag group {g}.', I)
        put(f'cost.{e}.valid_codings', len(d), f'Valid codings with a recorded cost, tag group {g} (0 while its batch is uncollected).', I)
        if d:
            put(f'cost.{e}.usd_per_paper_mean', round(sum(usd) / len(usd), 4), f'Mean recorded cost per valid coding, tag group {g}.', I)
            put(f'cost.{e}.usd_per_paper_median', round(st.median(usd), 4), f'Median recorded cost per valid coding, tag group {g}.', I)
        if g == 'fmt':
            put('cost.E0.usd_by_tag', {t: round(sum(v['usd'] for k, v in done.items() if k.startswith(t + ':')), 4)
                                       for t in tags if t.startswith('fmt-')}, 'Recorded cost per format-test arm replicate.', I)
    allusd = [v['usd'] for v in done.values()]
    put('cost.all.usd', round(sum(allusd), 4), 'Sum of recorded cost over every valid coding of every tag in state.json (the spend '
        'code_papers.py counts against --max-usd). Outputs that failed validation, were refused or hit max_tokens are billed '
        'but carry no cost here, so true spend is higher.', I)
    put('cost.all.valid_codings', len(allusd), 'Valid codings with a recorded cost, all tags.', I)
    put('cost.all.usd_per_paper_mean', round(sum(allusd) / len(allusd), 4), 'Mean recorded cost per valid coding over all tags '
        '(mixes format-test, review-attached and plain codings; not the round-1 per-paper rate).', I)
    put('cost.cap_usd', CAP_USD, 'Spending cap passed as --max-usd to code_papers.py.', ['EXPERIMENTS.md E1, E3, E7 commands'])
    put('cost.cap_remaining_usd', round(CAP_USD - sum(allusd), 2), 'Cap minus recorded cost over all tags (an upper bound on what remains).', I)
    coll = [b for b in batches if b.get('collected')]
    put('cost.batch_requests_collected', {'total': sum(len(b['keys']) for b in coll),
                                          **counter(Counter(group(b['tag']) for b in coll for _ in b['keys']))},
        'Requests in collected batches (each billed), by tag group.', I)
    ids = {b['id'] for b in coll}
    costed = sum(1 for v in done.values() if v.get('batch') in ids)
    put('cost.batch_requests_without_cost', sum(len(b['keys']) for b in coll) - costed,
        'Billed batch requests with no recorded cost: requests in collected batches minus done entries whose batch is one of '
        'them (synchronous `one` runs are not batch requests and are excluded from both sides).', I)
    put('cost.sync_one_runs', [k for k, v in done.items() if v.get('batch') is None],
        'Done entries written by the synchronous `code_papers.py one` command (full price, no batch discount).', I)
    pending = [b for b in batches if not b.get('collected')]
    put('cost.pending_batches', [{'id': b['id'], 'tag': b['tag'], 'requests': len(b['keys']), 'submitted': b['submitted']} for b in pending],
        'Submitted batches not yet collected (their cost is unknown until collect).', I)
    if 'calc1' in tags and any(k.startswith('calc1-review:') for k in done):
        lo = sum(v['usd'] for k, v in done.items() if k.startswith('calc1:')) / sum(k.startswith('calc1:') for k in done)
        hi = sum(v['usd'] for k, v in done.items() if k.startswith('calc1-review:')) / sum(k.startswith('calc1-review:') for k in done)
        put('cost.projection_10000_papers_usd', [round(10000 * lo), round(10000 * hi)],
            '10,000 papers times the mean recorded cost per paper of calc1 (PDF + XML) and of calc1-review (with review record), batch price.', I)
    # tokens per paper
    for t in ('calc1', 'calc1-review', 'r2'):
        d = [v['usage'] for k, v in done.items() if k.startswith(t + ':')]
        if not d:
            continue
        inp = [u['input'] + u['cache_read'] + u['cache_write'] for u in d]
        out = [u['output'] for u in d]
        put(f'tokens.{t}.input', {'n': len(inp), 'median': round(st.median(inp)), 'p90_nearest': p90_nearest(inp), 'p90_linear': p90_linear(inp), 'max': max(inp)},
            f'Input tokens per valid coding (input + cache_read + cache_write; PDF pages as images and text, plus XML), tag {t}.', I)
        put(f'tokens.{t}.output', {'n': len(out), 'median': round(st.median(out)), 'p90_nearest': p90_nearest(out), 'max': max(out)},
            f'Output tokens per valid coding including reasoning, tag {t}.', I)


# ---------------------------------------------------------------- round 1 coded set
def round1(state: dict, met: dict) -> tuple[set, set]:
    man = manifest('calc1')
    keys = [m['key'] for m in man]
    ok, bad = load_valid('calc1')
    I = ['private/analysis/codings/api/calc1', 'derived/calc1/manifest.jsonl']
    sub = set().union(*[set(b['keys']) for b in state['batches'] if b['tag'] == 'calc1'])
    files = {f.stem for f in (API / 'calc1').glob('*.json')}
    put('calc1.eligible', len(keys), 'Eligible round-1 papers (derived/calc1/manifest.jsonl).', I)
    put('calc1.submitted_with_full_text', len(sub), 'Papers with full text sent to the coder in E1: union of keys of state.json batches tagged calc1.', ['private/analysis/codings/api/state.json'])
    put('calc1.coding_files', len(files), 'Coding files in private/analysis/codings/api/calc1/.', I)
    put('calc1.valid', len(ok), 'calc1 codings that pass tools/check_coding.py validate.', I)
    put('calc1.invalid', {k: reason(v) for k, v in sorted(bad.items())}, 'calc1 codings that fail validation, with the reason.', I)
    put('calc1.without_full_text_e1', len(keys) - len(sub), 'Eligible round-1 papers not sent to the coder in E1 (no full text then).', I)
    put('calc1.without_valid_coding', sum(k not in ok for k in keys), 'Eligible round-1 papers without a valid calc1 coding.', I)
    Im = I + ['derived/gold/metrics.json']
    oa = lambda ks: [bool(met[k]['is_oa']) for k in ks if k in met]
    for name, ks in [('eligible', keys), ('coded', [k for k in keys if k in ok]), ('not_coded', [k for k in keys if k not in ok])]:
        v = oa(ks)
        put(f'calc1.open_access.{name}', {'n': len(v), 'oa': sum(v), 'share': round(sum(v) / len(v), 4)},
            f'Open-access papers (metrics.json is_oa) among the {name.replace("_", " ")} round-1 papers.', Im)
    jc = Counter(clean(met[k]['journal']) for k in ok if k in met)
    put('calc1.coded_by_journal_top5', counter(Counter(dict(jc.most_common(5)))),
        'Journals with the most valid calc1 codings (metrics.json journal, control characters removed).', Im)
    top = jc.most_common(1)[0][0]
    put('calc1.top_journal_eligible_all_coded', [sum(clean(met[k]['journal']) == top for k in keys if k in ok),
                                                 sum(clean(met[k]['journal']) == top for k in keys if k in met)],
        f'[coded, eligible] papers of the top journal ({top}).', Im)
    # publisher XML among E1 papers
    xs = {r['key']: r for r in read_json(DERIVED / 'calc1' / 'xml_status.json')}
    put('calc1.xml_among_submitted', sum(bool(xs.get(k, {}).get('xml')) for k in sub),
        'E1 papers (submitted with full text) that have publisher XML in derived/calc1/xml_status.json.', ['derived/calc1/xml_status.json', 'private/analysis/codings/api/state.json'])
    return sub, set(ok)


# ---------------------------------------------------------------- text route for an open model (E1 set)
def text_route(sub: set) -> None:
    rows, _ = cpo.inputs(argparse.Namespace(manifest=str(DERIVED / 'calc1' / 'manifest.jsonl'), keys=None, pdf_text=True, max_chars=10 ** 9))
    rows = [r for r in rows if r['key'] in sub]
    I = ['derived/calc1/manifest.jsonl', 'private/download-queue.json (files)', '<key>.xml.txt', 'pdftotext', 'tools/code_papers_open.py']
    put('text.calc1.source', counter(Counter(r['source'] for r in rows)),
        'Text route the open-model runner (code_papers_open.py --pdf-text) uses for each E1 paper: publisher XML, else pdftotext.', I)
    put('text.calc1.over_cap', sum(len(r['xml']) > MAX_CHARS for r in rows), f'E1 papers whose text is longer than {MAX_CHARS:,} characters (skipped by default).', I)
    U = [len(cpo.user_text(r['key'], r['doi'], r['xml'], r['review'], '<model>', r['source'])) for r in rows if len(r['xml']) <= MAX_CHARS]
    sysc = len(cpo.system_text())
    put('text.calc1.user_chars', {'n': len(U), 'median': st.median(U), 'p90_linear': p90_linear(U), 'max': max(U)},
        f'Characters of user text per E1 paper within the {MAX_CHARS:,} cap (code_papers_open.user_text).', I)
    put('text.system_chars', sysc, 'Characters of the system prompt (codebook + schema), code_papers_open.system_text().', ['agents/coder/CODEBOOK.md', 'agents/coder/coding.schema.json'])
    put('text.calc1.input_tokens_est', {'median': round((st.median(U) + sysc) / CHARS_PER_TOKEN), 'p90': round((p90_linear(U) + sysc) / CHARS_PER_TOKEN),
                                        'cap': round((MAX_CHARS + sysc) / CHARS_PER_TOKEN)},
        f'Estimated input tokens for a text-only model: (user + system characters) / {CHARS_PER_TOKEN}; the ratio is assumed, not measured.', I)


# ---------------------------------------------------------------- fetch counts
def fetch(met: dict) -> None:
    q27, qnow = json.loads(QUEUE_OCT27.read_text()), json.loads(QUEUE_NOW.read_text())
    pre2 = {('g22_' + p['id']): p for p in read_json(DERIVED / 'r2' / 'preselect.json')}
    for rnd, name, mfield in [('calc1', 'calc1', met), ('r2', 'r2calc', pre2)]:
        man = {m['key']: m for m in manifest(name)}
        xml = {r['key'] for r in read_json(DERIVED / name / 'xml_status.json') if r['xml']}
        for when, q, qpath in [('oct27', q27, rel(QUEUE_OCT27)), ('now', qnow, 'private/download-queue.json')]:
            I = [qpath, f'derived/{name}/manifest.jsonl', f'derived/{name}/xml_status.json']
            p = f'fetch.{rnd}.{when}'
            have = {k for k in man if q.get(k, {}).get('status') == 'have'}
            pdf = {k for k in have if str(q[k].get('file', '')).endswith('.pdf') and (ROOT / q[k]['file']).exists()}
            put(f'{p}.papers', len(man), f'Papers in derived/{name}/manifest.jsonl.', I)
            put(f'{p}.have', len(have), 'Papers with queue status "have" (the rule code_papers.py candidates() uses).', I)
            put(f'{p}.pdf', len(pdf), 'Papers with status "have" whose queue file is an existing .pdf.', I)
            put(f'{p}.pdf_in_pdfs_gold', sum((PDFS / f'{k}.pdf').exists() for k in man) if when == 'now' else
                sum(k in pdf and Path(q[k]['file']).name == f'{k}.pdf' for k in man),
                'Papers whose PDF is private/data/roadmap/pdfs/gold/<key>.pdf (now: on disk; oct27: queue file of that name).', I)
            put(f'{p}.xml', len(xml), f'Papers with publisher XML (derived/{name}/xml_status.json; not dated, read as it is).', I)
            put(f'{p}.text_any', len(have | xml), 'Papers with a queue PDF or publisher XML.', I)
            miss = sorted(k for k in man if k not in have)
            put(f'{p}.not_fetched', len(miss), 'Papers without queue status "have".', I)
            put(f'{p}.not_fetched_by_publisher', counter(Counter(publisher(man[k]['doi']) for k in miss)),
                'Papers without status "have", by publisher (DOI registrant prefix rule, module docstring).', I)
            put(f'{p}.not_fetched_by_doi_prefix', counter(Counter(man[k]['doi'].split('/')[0] for k in miss)), 'The same papers by DOI prefix.', I)
            put(f'{p}.not_fetched_by_publisher.openalex_field', counter(Counter(mfield[k]['publisher'] for k in miss if k in mfield)),
                'The same papers by the OpenAlex publisher field (metrics/preselect "publisher"; labels some AGU journals as Wiley). '
                'Secondary: kept to trace numbers already reported.', I + ['derived/gold/metrics.json' if rnd == 'calc1' else 'derived/r2/preselect.json'])
            jr = Counter(clean(mfield[k]['journal']) for k in miss if k in mfield)
            put(f'{p}.not_fetched_by_journal_top', counter(Counter(dict(jr.most_common(10)))), 'The same papers, ten most common journals.', I)
            if rnd == 'r2':
                put(f'{p}.not_fetched_open_access', sum(bool(pre2[k]['is_oa']) for k in miss if k in pre2),
                    'Of the papers not fetched, those marked is_oa in derived/r2/preselect.json.', I + ['derived/r2/preselect.json'])
        if rnd == 'r2':
            xr = Counter(r['route'] for r in read_json(DERIVED / name / 'xml_status.json') if r['xml'])
            put('fetch.r2.xml_by_route', counter(xr), 'Round-2 papers with publisher XML, by route.', [f'derived/{name}/xml_status.json'])


# ---------------------------------------------------------------- round 2 draw, screen and dry-run estimate
def round2(state: dict) -> None:
    pre = read_json(DERIVED / 'r2' / 'preselect.json')
    el = read_json(DERIVED / 'r2' / 'eligibility.json')
    I = ['derived/r2/preselect.json']
    pj = Counter(p['journal'] for p in pre)
    put('r2.drawn', len(pre), 'Papers in the round-2 preselection (g18_round2_draw.py).', I)
    put('r2.journals', len(pj), 'Distinct journals in the round-2 preselection.', I)
    put('r2.max_per_journal', max(pj.values()), 'Largest number of papers from one journal in the round-2 preselection.', I)
    put('r2.publishers.openalex_field', len({p['publisher'] for p in pre}), 'Distinct values of the OpenAlex publisher field in the round-2 preselection.', I)
    put('r2.publishers.doi_rule', counter(Counter(publisher(p['doi']) for p in pre)), 'Round-2 preselection by publisher (DOI registrant prefix rule).', I)
    put('r2.open_access', sum(bool(p['is_oa']) for p in pre), 'Round-2 preselected papers marked is_oa.', I)
    I = ['derived/r2/eligibility.json']
    both = [x for x in el if x['screenA'] and x['screenB']]
    put('r2.eligible', sum(bool(x['eligible']) for x in el), 'Round-2 papers judged eligible after screening and adjudication.', I)
    put('r2.screen_agree', [sum(x['screenA']['eligible'] == x['screenB']['eligible'] for x in both), len(both)],
        '[papers where the two screeners agreed on eligibility, papers with both screens].', I)
    put('r2.excluded_by_category', counter(Counter(x['category'] for x in el if not x['eligible'])), 'Excluded round-2 papers by category.', I)
    q27 = json.loads(QUEUE_OCT27.read_text())
    qnow = json.loads(QUEUE_NOW.read_text())
    pdf_of = lambda k: (q27.get(k) or {}).get('file') or qnow[k]['file']   # top-up batches hold papers fetched after Oct 27
    for b in [b for b in state['batches'] if b['tag'] == 'r2']:
        pages = sum(max(4, (ROOT / pdf_of(k)).stat().st_size // 60_000) for k in b['keys'])
        est = (pages * 2300 * 4.00 + len(b['keys']) * 10_000 * 20.00) / 1e6 * 0.5
        put(f'r2.batch.{b["id"]}', {'requests': len(b['keys']), 'submitted': b['submitted'], 'est_pages': pages, 'dry_run_estimate_usd': round(est, 2)},
            'Round-2 batch and the code_papers.py submit estimate: pages = sum(max(4, pdf_bytes // 60000)); '
            'usd = (pages x 2300 x $4 + papers x 10000 x $20) / 1e6 x 0.5.', ['private/analysis/codings/api/state.json', rel(QUEUE_OCT27)])
    ok, bad = load_valid('r2')
    if ok or bad:
        put('r2.coded_valid', len(ok), 'Valid round-2 codings (tools/check_coding.py validate).', ['private/analysis/codings/api/r2'])
        put('r2.coded_invalid', {k: reason(v) for k, v in sorted(bad.items())}, 'Invalid round-2 codings with reason.', ['private/analysis/codings/api/r2'])


# ---------------------------------------------------------------- review visibility (E3, E4)
def visibility(state: dict, met: dict) -> None:
    labels = read_json(DERIVED / 'review' / 'visibility_labels.json')
    idx = read_json(DERIVED / 'review' / 'open_review_index.json')
    qnow = json.loads(QUEUE_NOW.read_text())
    IL = ['derived/review/visibility_labels.json', 'derived/review/visibility_input']
    rows = []
    for p in labels:
        meta = {r['i']: r for r in json.loads((DERIVED / 'review' / 'visibility_input' / f"{p['key']}.json").read_text())['review_steps']}
        for s in p['steps']:
            m = meta.get(s['i'], {})
            rows.append({**s, 'key': p['key'], 'node': s.get('node') or m.get('node'), 'move': s.get('move') or m.get('move')})
    ch = [r for r in rows if r['label'] != 'no_change']
    lab = Counter(r['label'] for r in rows)
    put('vis.papers', len(labels), 'Papers with visibility labels.', IL)
    put('vis.steps', len(rows), 'Review steps labelled.', IL)
    put('vis.changes', len(ch), 'Review steps that changed the work (label not no_change).', IL)
    for c in ('as_planned', 'absent', 'as_revision', 'no_change'):
        put(f'vis.label.{c}', lab[c], f'Review steps labelled {c}.', IL)
        if c != 'no_change':
            put(f'vis.label.{c}.share_of_changes_pct', round(100 * lab[c] / len(ch), 2), f'{c} as a percentage of changes.', IL)
    papers_marking = len({r['key'] for r in ch if r['label'] == 'as_revision'})
    put('vis.papers_marking_any_change', papers_marking, 'Papers with at least one change labelled as_revision.', IL)
    n = len(labels)
    put('vis.papers_marking_upper95_pct', {'rule_of_three': round(100 * 3 / n, 2), 'exact_one_sided': round(100 * (1 - 0.05 ** (1 / n)), 2)} if papers_marking == 0
        else None, f'95% upper bound on the share of papers that would mark a review change, given 0 of {n}: 3/n and 1 - 0.05^(1/n).', IL)
    put('vis.agreement', [sum(bool(r['agreed']) for r in rows), len(rows)], '[steps where the two labelers agreed, steps].', IL)
    put('vis.adjudicated', sum(not r['agreed'] for r in rows), 'Steps where the labelers differed (adjudicated).', IL)
    per = [len(p['steps']) for p in labels]
    put('vis.steps_per_paper', {'median': st.median(per), 'min': min(per), 'max': max(per)}, 'Review steps per labelled paper.', IL)
    put('vis.quotes_over_25_words', sum(len(str(r.get('quote') or '').split()) > 25 for r in rows if r['label'] in ('as_planned', 'as_revision')),
        'Labeler quotes (as_planned or as_revision) longer than 25 whitespace-separated words.', IL)
    nodes = sorted({r['node'] for r in ch if r['node']}, key=lambda x: (-sum(r['node'] == x for r in ch), x))
    put('vis.by_node', {x: [sum(r['node'] == x for r in ch), sum(r['node'] == x and r['label'] == 'absent' for r in ch)] for x in nodes},
        'Per node of the coded review step: [changes, changes labelled absent].', IL)
    v = [r for r in ch if r['node'] == 'V']; o = [r for r in ch if r['node'] != 'V']
    put('vis.V_absent', [sum(r['label'] == 'absent' for r in v), len(v)], '[V changes absent, V changes].', IL)
    put('vis.other_absent', [sum(r['label'] == 'absent' for r in o), len(o)], '[absent, changes] for every node other than V.', IL)
    put('vis.most_common_node_all_steps', list(Counter(r['node'] for r in rows).most_common(1)[0]), 'Most common node over all labelled steps, with count.', IL)
    for mv in ('declined', 'review_forced'):
        put(f'vis.move.{mv}', counter(Counter(r['label'] for r in rows if r['move'] == mv)) | {'total': sum(r['move'] == mv for r in rows)},
            f'Labels of the steps the coder marked move = {mv}.', IL)
    ok_rev, bad_rev = load_valid('calc1-review')
    IR = ['private/analysis/codings/api/calc1-review']
    put('vis.journals', counter(Counter(ok_rev[p['key']]['doi'].split('/')[1].split('-')[0] for p in labels)),
        'Labelled papers by Copernicus journal (DOI suffix prefix, e.g. tc = The Cryosphere).', IR + IL)
    I = ['derived/review/open_review_index.json']
    wc = [r for r in idx if 'comments' in r]
    put('review.copernicus_coded', len(idx), 'E1-coded papers in Copernicus journals (rows of open_review_index.json).', I)
    put('review.with_open_discussion', len(wc), 'Of these, papers with an open discussion and its comments.', I)
    put('review.without_open_discussion', counter(Counter(r['doi'].split('/')[1].split('-')[0] for r in idx if r.get('no_open_discussion'))),
        'Papers without an open discussion, by journal (DOI suffix prefix).', I)
    put('review.comments', {t: sum(r['comments'].get(t, 0) for r in wc) for t in ('RC', 'AC', 'CC', 'EC')},
        'Comments in the open discussions: RC referee, AC author, CC community, EC editor.', I)
    put('review.final_xml', [sum((ROOT / qnow[r['key']]['file']).with_suffix('.xml.txt').exists() for r in wc if r['key'] in qnow), len(wc)],
        '[papers with <file>.xml.txt beside the queue file, papers with an open discussion].', I + ['private/download-queue.json'])
    mdoi = {m['doi'].lower(): m for m in met.values()}
    put('review.open_access', [sum(bool(mdoi[r['doi'].lower()]['is_oa']) for r in idx if r['doi'].lower() in mdoi), len(idx)],
        '[open access per metrics.json is_oa, Copernicus papers].', I + ['derived/gold/metrics.json'])
    put('review.coded_valid', len(ok_rev), 'Valid calc1-review codings.', IR)
    put('review.coded_invalid', {k: reason(v) for k, v in sorted(bad_rev.items())}, 'calc1-review codings dropped, with the validation reason.', IR)
    rb = [b for b in state['batches'] if b['tag'] == 'calc1-review']
    put('review.batches', [{'id': b['id'], 'requests': len(b['keys']), 'max_tokens': b.get('max_tokens')} for b in rb],
        'calc1-review batches in order: the first pass, then the resubmissions (their sum is the first-pass failure count).', ['private/analysis/codings/api/state.json'])
    put('review.first_pass_failures', sum(len(b['keys']) for b in rb[1:]), 'Requests resubmitted after the first calc1-review pass.', ['private/analysis/codings/api/state.json'])


# ---------------------------------------------------------------- agents vs papers (g14), ranking only
def agents() -> None:
    nu = read_json(DERIVED / 'calc1' / 'papers_vs_agents.json')['node_use']
    put('agents.node_share_rank', {k: v['agents'][0] for k, v in sorted(nu.items(), key=lambda kv: kv[1]['agents'][0])},
        'Share of agent loops running each node (g14 papers_vs_agents.json node_use[*].agents estimate), lowest first. '
        'Agent estimates do not depend on the paper set.', ['derived/calc1/papers_vs_agents.json'])


# ---------------------------------------------------------------- outcomes (g17): counts, bound, partial correlations
def outcomes(met: dict) -> None:
    o = read_json(DERIVED / 'outcomes' / 'outcomes.json')
    I = ['derived/outcomes/outcomes.json']
    sig = [r for r in o['rows'] if r['q'] < 0.1]
    put('outcomes.tests', len(o['rows']), 'Feature-outcome tests (rows of outcomes.json).', I)
    put('outcomes.tests_by_type', counter(Counter(r['type'] for r in o['rows'])), 'Tests by feature type.', I)
    put('outcomes.q_below_0.1', len(sig), 'Tests with Benjamini-Hochberg q < 0.1.', I)
    put('outcomes.bh_expected_false_upper', round(0.1 * len(sig), 2), 'Upper bound on expected false discoveries among them under BH at 0.1 (0.1 x count).', I)
    put('outcomes.q_sum_significant', round(sum(r['q'] for r in sig), 3), 'Sum of q over the tests with q < 0.1.', I)
    put('outcomes.abs_rho_range_significant', [min(abs(r['rho']) for r in sig), max(abs(r['rho']) for r in sig)], 'Range of |rho| among tests with q < 0.1.', I)
    # partial Spearman controlling for reference count, same paper filter as g17
    codes = {}
    for f in sorted(g17.API.glob('*.json')):
        try:
            c = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            continue
        if not validate(c) and c['key'] in met:
            codes[c['key']] = c
    F = {k: g17.features(c) for k, c in codes.items()}
    feats = {'steps': 'num:steps', 'revisits': 'num:revisits', 'decisive simulation': 'bin:decisive simulation'}

    def partial(x, y, z):
        rx, ry, rz = g17.rank(x), g17.rank(y), g17.rank(z)
        A = np.column_stack([np.ones(len(rz)), rz])
        ex = rx - A @ np.linalg.lstsq(A, rx, rcond=None)[0]
        ey = ry - A @ np.linalg.lstsq(A, ry, rcond=None)[0]
        return round(float(np.corrcoef(ex, ey)[0, 1]), 3)
    Ip = ['private/analysis/codings/api/calc1', 'derived/gold/metrics.json']
    for oc in ('cnp', 'fwci'):
        ks = sorted(k for k in codes if met[k].get(oc) is not None and met[k].get('n_refs') is not None)
        y, z = [met[k][oc] for k in ks], [met[k]['n_refs'] for k in ks]
        put(f'outcomes.partial_nrefs.{oc}', {'n': len(ks), **{name: partial([float(F[k].get(f, False)) for k in ks], y, z) for name, f in feats.items()}},
            f'Partial Spearman of a feature with {oc}, controlling for reference count (n_refs): ranks with average ties, '
            'feature and outcome ranks regressed on [1, rank(n_refs)], Pearson correlation of residuals.', Ip)
        put(f'outcomes.rho_nrefs.{oc}', round(g17.spearman(z, y), 3), f'Spearman of n_refs with {oc}.', Ip)
    ks = sorted(k for k in codes if met[k].get('n_refs') is not None)
    put('outcomes.rho_steps_nrefs', round(g17.spearman([F[k]['num:steps'] for k in ks], [met[k]['n_refs'] for k in ks]), 3), 'Spearman of steps with n_refs.', Ip)


# ---------------------------------------------------------------- numbers added after the October 27 report review
def _merged(xs):
    out = []
    for x in xs:
        if not out or out[-1] != x:
            out.append(x)
    return out


def _revisits(nodes):
    seen, r = set(), 0
    for x in nodes:
        r += x in seen
        seen.add(x)
    return r


def qnow_file(key: str) -> str:
    return json.loads(QUEUE_NOW.read_text())[key]['file']


def backlog(state: dict) -> None:
    """Round-1 papers with full text and no valid coding, split by why (numbers auditor, October 27)."""
    keys = [m['key'] for m in manifest('calc1')]
    qnow = json.loads(QUEUE_NOW.read_text())
    ok, bad = load_valid('calc1')
    have = {k for k in keys if qnow.get(k, {}).get('status') == 'have'}
    e1 = set().union(*[set(b['keys']) for b in state['batches'] if b['tag'] == 'calc1' and b.get('collected')])
    pend = set().union(*[set(b['keys']) for b in state['batches'] if b['tag'] == 'calc1' and not b.get('collected')] or [set()])
    wait = sorted(k for k in have if k not in ok)
    I = ['private/download-queue.json', 'derived/calc1/manifest.jsonl', 'private/analysis/codings/api/calc1', 'private/analysis/codings/api/state.json']
    put('calc1.full_text_now', len(have), 'Eligible round-1 papers with queue status "have" now.', I)
    put('calc1.full_text_without_valid_coding', len(wait), 'Eligible round-1 papers with full text now and no valid calc1 coding.', I)
    put('calc1.full_text_without_valid_coding.split', {
        'never_in_a_collected_batch': sum(k not in e1 for k in wait),
        'failed_validation': sum(k in bad for k in wait),
        'in_an_uncollected_calc1_batch': sum(k in pend for k in wait)},
        'The same papers: not in any collected calc1 batch (fetched after E1); coded but failing validation; and how many of '
        'all of them sit in a calc1 batch submitted but not yet collected.', I)
    man = {m['key']: m for m in manifest('calc1')}
    met = {('g22_' + m['id']): m for m in read_json(DERIVED / 'gold' / 'metrics.json')}
    put('calc1.full_text_without_valid_coding.by_publisher', counter(Counter(publisher(man[k]['doi']) for k in wait)),
        'The backlog by publisher (DOI registrant prefix rule).', I)
    put('calc1.open_access_by_publisher', {pb: {'eligible': [sum(met[k]['is_oa'] for k in ks), len(ks)],
                                                'coded': [sum(met[k]['is_oa'] for k in ks if k in ok), sum(k in ok for k in ks)]}
                                           for pb in ('AGU', 'Elsevier') for ks in [[k for k in keys if publisher(man[k]['doi']) == pb]]},
        '[open access, papers] among eligible and among coded round-1 papers of AGU and Elsevier (metrics.json is_oa).',
        I + ['derived/gold/metrics.json'])
    put('calc1.no_pdf_now', len(keys) - len(have), 'Eligible round-1 papers still without queue status "have" (no PDF); a separate set from the backlog above.', I)


def gold() -> None:
    g = read_json(DERIVED / 'gold' / 'gold_set.json')
    ha = read_json(DERIVED / 'gold' / 'human_assignment.json')
    gk = {('g22_' + x['id']) if not str(x.get('id', '')).startswith('g22_') else x['id'] for x in g}
    ok1, _ = load_valid('calc1')
    ok2, bad2 = load_valid('gold-r2')
    files2 = {f.stem for f in (API / 'gold-r2').glob('*.json')}
    hdir = DERIVED / 'gold' / 'human'
    I = ['derived/gold/gold_set.json', 'derived/gold/human_assignment.json', 'private/analysis/codings/api/{calc1,gold-r2}']
    put('gold.n', len(gk), 'Papers in the frozen gold set (a stratified sample of 100 eligible round-1 papers; not human-labelled yet).', I)
    put('gold.retest', {'gold_papers_coded_twice': len(files2 & gk), 'pairs_valid_both': len(set(ok1) & set(ok2) & gk)},
        'Gold papers with a second coding (tag gold-r2; the gold papers that had full text at E1) and pairs where both codings pass validation.', I)
    put('gold.human_assigned', {'papers': len(ha['papers']), 'coders': len(ha['coders']),
                                'per_paper': len(ha['papers'][0]['assigned']) if ha['papers'] else 0,
                                'codings_returned': len(list(hdir.glob('*/*.json'))) if hdir.is_dir() else 0},
        'Human coding of the gold subset: papers, coders, coders per paper, coding files returned to derived/gold/human/.', I)


def setup() -> None:
    import hashlib
    import code_papers as cp
    txt = cp.system_blocks()[0]['text']
    put('setup.coder', {'model': cp.MODEL, 'effort': 'high (code_papers.py default, recorded per batch in state.json)',
                        'max_tokens': '32000; retries after max_tokens at 64000', 'temperature': 'not set (API default)',
                        'thinking': 'no thinking parameter set; output tokens include reasoning',
                        'system_prompt_sha256': hashlib.sha256(txt.encode()).hexdigest(), 'system_prompt_chars': len(txt),
                        'codebook': 'agents/coder/CODEBOOK.md 1.5.0, last changed at public commit 01b7f78'},
        'Annotation setup of the batch coder: tools/code_papers.py params() and system_blocks() at the current commit.',
        ['tools/code_papers.py', 'agents/coder/CODEBOOK.md', 'agents/coder/coding.schema.json'])


def coded_features(met: dict) -> None:
    """Steps (merged and unmerged), revisits with and without consecutive repeats, V check kinds, and run-to-run
    consistency of the features behind the 15 g17 associations (calc1 against gold-r2)."""
    from g11_human_agreement import alpha_nominal
    from check_coding import v_status
    ok1, _ = load_valid('calc1')
    ok2, _ = load_valid('gold-r2')
    I = ['private/analysis/codings/api/calc1', 'private/analysis/codings/api/gold-r2', 'derived/gold/metrics.json']
    codes = {k: c for k, c in ok1.items() if k in met}
    fp = lambda c: [s['node'] for s in next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps']]
    un = [len(fp(c)) for c in codes.values()]
    mg = [len(_merged(fp(c))) for c in codes.values()]
    put('features.steps_median', {'unmerged': st.median(un), 'merged': st.median(mg), 'n': len(un)},
        'Median steps per final-paper sequence: unmerged (as coded; the g17 "steps" feature) and with consecutive repeats of '
        'a node merged (g13 steps_median).', I)
    rv = [g17.features(c)['num:revisits'] for c in codes.values()]
    rvm = [_revisits(_merged(fp(c))) for c in codes.values()]
    put('features.revisits_median', {'g17_unmerged': st.median(rv), 'merged': st.median(rvm),
                                     'consecutive_repeats_share': round(1 - sum(rvm) / sum(rv), 4) if sum(rv) else None},
        'Median revisits per paper. g17 counts a step whose node already occurred earlier in the unmerged sequence, so a '
        'consecutive repeat counts; "merged" counts returns to an earlier node after merging consecutive repeats. '
        'consecutive_repeats_share = share of g17 revisits that are consecutive repeats.', I)
    for oc in ('cnp', 'fwci'):
        ks = sorted(k for k in codes if met[k].get(oc) is not None)
        put(f'features.revisits_merged_rho.{oc}', {'rho_g17_revisits': round(g17.spearman([g17.features(codes[k])['num:revisits'] for k in ks], [met[k][oc] for k in ks]), 3),
                                                   'rho_merged_revisits': round(g17.spearman([_revisits(_merged(fp(codes[k]))) for k in ks], [met[k][oc] for k in ks]), 3),
                                                   'rho_merged_steps': round(g17.spearman([len(_merged(fp(codes[k]))) for k in ks], [met[k][oc] for k in ks]), 3),
                                                   'n': len(ks)},
            f'Sensitivity check, outside the g17 BH family: Spearman of {oc} with g17 revisits, with revisits on the merged '
            'sequence, and with merged steps.', I)
    kinds = Counter(k for c in codes.values() for k in v_status(c)['kinds'])
    put('features.v_status', {'n': len(codes), 'status': counter(Counter(v_status(c)['v'] for c in codes.values())),
                              'papers_with_kind': counter(kinds)},
        'V status per paper (check_coding.v_status: full = a check performed here that is not a reproduction) and the number '
        'of papers with each kind of check performed here (reproduction, replication, method, robustness, control, generalization).', I)
    # run-to-run consistency on the gold pairs
    pairs = sorted(set(ok1) & set(ok2))
    A, B = [g17.features(ok1[k]) for k in pairs], [g17.features(ok2[k]) for k in pairs]
    out = {}
    for name in ['num:steps', 'num:revisits', 'num:distinct modes', 'num:imports', 'num:import fields', 'num:V check kinds']:
        a, b = [x.get(name, 0) for x in A], [x.get(name, 0) for x in B]
        out[name[4:]] = {'kind': 'count', 'spearman_run1_run2': round(g17.spearman(a, b), 3)}
    for name in ['bin:decisive simulation', 'bin:decisive methods', 'bin:composition capability_first', 'bin:mode observation',
                 'bin:mode synthesis', 'bin:node I infer']:
        a, b = [bool(x.get(name, False)) for x in A], [bool(x.get(name, False)) for x in B]
        out[name[4:]] = {'kind': 'binary', 'agreement': round(sum(x == y for x, y in zip(a, b)) / len(a), 3),
                         'alpha_nominal': alpha_nominal([[x, y] for x, y in zip(a, b)]),
                         'prevalence_run1': round(sum(a) / len(a), 3)}
    put('features.retest_consistency', {'pairs': len(pairs), **out},
        'Run-to-run consistency of the coded features behind the 15 g17 associations, on gold papers coded twice (calc1 and '
        'gold-r2, both valid): Spearman between runs for counts; agreement and Krippendorff alpha (nominal, '
        'g11_human_agreement.alpha_nominal) for binary features. Both runs are the same model; this is stability, not accuracy.', I)


def outcomes_extra() -> None:
    o = read_json(DERIVED / 'outcomes' / 'outcomes.json')
    hw = [(r['ci'][1] - r['ci'][0]) / 2 for r in o['rows'] if r['n'] == o['papers']]
    put('outcomes.rho_ci_halfwidth', {'rows': len(hw), 'median': round(float(np.median(hw)), 3), 'min': round(min(hw), 3), 'max': round(max(hw), 3)},
        'Half-width of the 95% bootstrap interval on rho, over g17 rows that use all coded papers.', ['derived/outcomes/outcomes.json'])
    p = np.array([r['p'] for r in o['rows']])
    cm = float(np.sum(1 / np.arange(1, len(p) + 1)))
    by = np.minimum(1, g17.bh(p) * cm)
    put('outcomes.benjamini_yekutieli', {'tests': len(p), 'c_m': round(cm, 3), 'q_below_0.1': int((by < 0.1).sum()),
                                         'min_q': round(float(by.min()), 3), 'min_p': float(p.min()),
                                         'p_floor': round(1 / 5001, 4)},
        'Sensitivity check: Benjamini-Yekutieli q (BH q times c(m) = sum 1/i, valid under any dependence) over the g17 tests. '
        'With 5000 permutations the smallest attainable p is 1/5001.', ['derived/outcomes/outcomes.json'])
    pool = read_json(DERIVED / 'gold' / 'pool.json')
    c = [p['cnp'] for p in pool if p.get('cnp') is not None and not p.get('convenor_coauthor')]
    put('outcomes.pool_cnp_median', {'n': len(c), 'median': round(float(np.median(c)), 3)},
        'Median cnp in the 2022 candidate pool without convenor co-authored papers (the round-1 sample is stratified to equal cnp quintiles).',
        ['derived/gold/pool.json'])


def review_extra(state: dict) -> None:
    """Review steps by trigger, coder input, a string scan of the published texts, and a paper-level test of V absences."""
    labels = read_json(DERIVED / 'review' / 'visibility_labels.json')
    IL = ['derived/review/visibility_labels.json', 'derived/review/visibility_input']
    rows = []
    for p in labels:
        pack = json.loads((DERIVED / 'review' / 'visibility_input' / f"{p['key']}.json").read_text())
        meta = {r['i']: r for r in pack['review_steps']}
        for s in p['steps']:
            m = meta.get(s['i'], {})
            rows.append({'key': p['key'], 'label': s['label'], 'node': s.get('node') or m.get('node'), 'trigger': m.get('trigger')})
    put('vis.by_trigger', {t: counter(Counter(r['label'] for r in rows if r['trigger'] == t)) | {'total': sum(r['trigger'] == t for r in rows)}
                           for t in sorted({r['trigger'] for r in rows}, key=str)},
        'Review steps by coded trigger (referee, editor, commenter, author, unknown), with their labels.', IL)
    rdir = DATA / 'review'
    atc = sum(any('ATC' in f.name for f in (rdir / p['key']).glob('*.pdf')) for p in labels if (rdir / p['key']).is_dir())
    supp = sum('-S p.' in (rdir / p['key'] / 'discussion.txt').read_text() for p in labels if (rdir / p['key'] / 'discussion.txt').is_file())
    put('review.coder_input', {'papers': len(labels), 'tracked_changes_pdf_downloaded': atc, 'comment_supplements_in_discussion_txt': supp,
                               'given_to_coder': 'published PDF, publisher XML text, discussion.txt (RC, AC, CC, EC comments and comment supplements)',
                               'not_given_to_coder': 'tracked-changes manuscripts (ATC), author-response PDFs (AR), manuscript versions, the article supplement'},
        'What the review coder read (tools/code_papers.py review_text_for: <review-dir>/<key>/discussion.txt only), and how many '
        'labelled papers have a tracked-changes PDF on disk that was not sent.', IL + ['private/data/roadmap/review/<key>/'])
    # string scan of the published texts for revision markers
    pat_any = re.compile(r'\b(reviewers?|referees?)\b', re.I)
    pat_mark = re.compile(r'as suggested by (an?|the|two|both)? ?(anonymous )?(reviewer|referee)|(reviewer|referee)s? (suggested|asked|pointed out|requested)|'
                          r'in response to (an?|the)? ?(reviewer|referee)|during (the )?(review|revision)|in (the )?revised (manuscript|version)', re.I)
    pat_thanks = re.compile(r'thank|grateful|reviewed by|edited by|acknowledg|comments|appreciat|review statement', re.I)
    import subprocess
    scan = {'xml': Counter(), 'pdf': Counter()}
    for p in labels:
        pack = json.loads((DERIVED / 'review' / 'visibility_input' / f"{p['key']}.json").read_text())
        t = Path(pack['final_text'])
        texts = {'xml': t.read_text() if t.is_file() else '',
                 'pdf': subprocess.run(['pdftotext', str(ROOT / qnow_file(p['key'])), '-'], capture_output=True, text=True).stdout}
        for src, s in texts.items():
            s = re.sub(r'\s+', ' ', s)
            hits = list(pat_any.finditer(s))
            scan[src]['papers'] += 1
            scan[src]['acknowledgement_section'] += bool(re.search(r'acknowledg', s, re.I))
            scan[src]['any_reviewer_or_referee'] += bool(hits)
            scan[src]['mention_outside_thanks_or_review_statement'] += any(
                not pat_thanks.search(s[max(0, h.start() - 160):h.end() + 60]) for h in hits)
            scan[src]['revision_phrase'] += bool(pat_mark.search(s))
    put('vis.string_scan', {**{k: dict(v) for k, v in scan.items()}, 'pattern_any': pat_any.pattern, 'pattern_revision': pat_mark.pattern,
                            'pattern_thanks_context': pat_thanks.pattern},
        'Script check, independent of the labelers, on the published text of each labelled paper in two forms: the publisher XML '
        'text the labelers read (xml; the converter keeps body and captions, and most back matter, including acknowledgements, '
        'is missing) and pdftotext of the published PDF (pdf). Counts papers with an acknowledgements heading, with the word '
        'reviewer or referee, with such a word outside a thank-you or the Copernicus review statement (160 characters before, '
        '60 after), and with a phrase tying content to review (pattern_revision).', IL + ['published PDFs (private/download-queue.json)'])
    # V against the other nodes, papers as units
    ch = [r for r in rows if r['label'] != 'no_change' and r['node']]
    keys = sorted({r['key'] for r in ch})
    by = {k: [r for r in ch if r['key'] == k] for k in keys}
    rng = np.random.default_rng(2026)
    nodes = sorted({r['node'] for r in ch}, key=lambda x: -sum(r['node'] == x for r in ch))
    tests = {}
    for nd in [x for x in nodes if sum(r['node'] == x for r in ch) >= 5]:
        def diff(groups):
            a = sum(r['label'] == 'absent' for g in groups for r in g if r['node'] == nd)
            na = sum(r['node'] == nd for g in groups for r in g)
            b = sum(r['label'] == 'absent' for g in groups for r in g if r['node'] != nd)
            nb = sum(r['node'] != nd for g in groups for r in g)
            return (a / na if na else np.nan) - (b / nb if nb else np.nan)
        obs = diff(by.values())
        # permutation: shuffle absent labels among the changes of each paper (keeps each paper's absences)
        lab = {k: np.array([r['label'] == 'absent' for r in by[k]]) for k in keys}
        nod = {k: np.array([r['node'] == nd for r in by[k]]) for k in keys}
        perm = []
        for _ in range(5000):
            a = na = b = nb = 0
            for k in keys:
                l = rng.permutation(lab[k])
                a += (l & nod[k]).sum(); na += nod[k].sum(); b += (l & ~nod[k]).sum(); nb += (~nod[k]).sum()
            perm.append(a / na - b / nb)
        p = (1 + (np.abs(perm) >= abs(obs) - 1e-12).sum()) / 5001
        bs = []
        for _ in range(2000):
            g = [by[keys[i]] for i in rng.integers(0, len(keys), len(keys))]
            bs.append(diff(g))
        bs = np.array(bs); bs = bs[~np.isnan(bs)]
        tests[nd] = {'diff': round(obs, 4), 'ci': [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)], 'p': round(float(p), 4)}
    q = g17.bh([t['p'] for t in tests.values()])
    for t, qq in zip(tests.values(), q):
        t['q'] = round(float(qq), 4)
    put('vis.node_vs_rest_paper_level', {'nodes_tested': len(tests), **tests},
        'Absent share of a node minus the absent share of all other nodes (changes only, nodes with at least 5 changes). '
        'p: two-sided permutation test that shuffles the absent labels among the changes within each paper (5000), so '
        'papers keep their own number of absences; interval: 2000 bootstrap resamples of papers; q: Benjamini-Hochberg over the nodes tested. Exploratory.', IL)


def loop_pilot() -> None:
    """The October 21 loop pilot (9 papers with review files), read from its report's totals row; distinct from the
    10-paper labelling pilot of E4 (derived/review/visibility_labels_pilot.json)."""
    src = PRIVATE / 'analysis' / 'success-set' / 'loops' / 'REPORT.md'
    row = next((l for l in src.read_text().splitlines() if l.startswith('| All |')), None)
    if not row:
        return
    c = [x.strip() for x in row.strip('|').split('|')]
    put('review.loop_pilot', {'papers': int(c[1]), 'loops': int(c[2]), 'readable_as_loops': int(c[6]), 'as_planned': int(c[7]), 'absent': int(c[8])},
        'October 21 loop pilot: loops recorded in the process documents (Nature peer-review files, EGU discussions, one preprint '
        'revision) of 9 papers, and how they appear in the published paper; totals row of the pilot report, coded by hand-run '
        'model sessions, not by a committed script.', ['private/analysis/success-set/loops/REPORT.md'])


def cost_extra(state: dict) -> None:
    est = [v['value']['dry_run_estimate_usd'] for k, v in VALUES.items() if k.startswith('r2.batch.')]
    pend = [b for b in state['batches'] if not b.get('collected')]
    put('cost.r2_dry_run_total_usd', round(sum(est), 2), 'Sum of the code_papers.py submit estimates of the round-2 batches (an upper-bound style estimate).',
        ['private/analysis/codings/api/state.json'])
    put('cost.pending_requests', {'total': sum(len(b['keys']) for b in pend), **counter(Counter(b['tag'] for b in pend for _ in b['keys']))},
        'Requests in batches submitted and not yet collected, by tag.', ['private/analysis/codings/api/state.json'])
    put('cost.pending_projection_usd', round(sum(len(b['keys']) for b in pend) * VALUES['cost.E1.usd_per_paper_mean']['value'], 2),
        'Pending requests times the E1 mean recorded cost per valid coding (a lower-bound style projection; retries and invalid outputs are billed but not counted).',
        ['private/analysis/codings/api/state.json'])


def _norm(s: str) -> str:
    """NFKC (ligatures split), lower case, line-break hyphens joined, every run of non-alphanumerics one space (quote search)."""
    import unicodedata
    s = re.sub(r'-\s*\n\s*', '', unicodedata.normalize('NFKC', s or ''))
    return ' '.join(re.sub(r'[\W_]+', ' ', s.lower()).split())


def _quote_found(q: str, text: str) -> bool:
    parts = [_norm(p) for p in re.split(r'\.\.\.|…|\[\.\.\.\]', q or '')]
    parts = [p for p in parts if p]
    return bool(parts) and all(p in text for p in parts)


def audit_extra(state: dict, met: dict) -> None:
    """Numbers added after the second review of private/text/report-roadmap.md (October 27): a between-paper baseline
    for the test-retest similarities, quote existence in the source text, the textbook order as an ordered subsequence,
    coded against uncoded AGU papers, the within-family re-ranked estimate, the E4 labelers' Cohen kappa, the E1 text
    route as the coder reported it, and resubmissions."""
    import subprocess
    from check_coding import seq, edit, jacc
    import g20_topics_journals as g20
    ok1, _ = load_valid('calc1')
    ok2, _ = load_valid('gold-r2')
    I = ['private/analysis/codings/api/calc1', 'private/analysis/codings/api/gold-r2']
    sim = lambda x, y: 1 - edit(x, y) / max(len(x), len(y), 1)

    # 1. test-retest against a between-paper baseline (unrounded per pair; consecutive repeats merged, as check_coding.agree)
    def measures(a, b):
        na, nb, ma, mb = seq(a, 'node'), seq(b, 'node'), seq(a, 'mode'), seq(b, 'mode')
        return {'node_set_jaccard': jacc(na, nb), 'mode_set_jaccard': jacc(ma, mb), 'node_seq_similarity': sim(na, nb),
                'mode_seq_similarity': sim(ma, mb), 'entry_state': a['entry']['state'] == b['entry']['state'],
                'decisive_mode': a['decisive_move']['mode'] == b['decisive_move']['mode']}
    pairs = sorted(set(ok1) & set(ok2))
    rt = [measures(ok1[k], ok2[k]) for k in pairs]
    ks = sorted(ok1)
    bp = [measures(ok1[a], ok1[b]) for i, a in enumerate(ks) for b in ks[i + 1:]]
    out = {}
    for m in rt[0]:
        r, b = float(np.mean([x[m] for x in rt])), float(np.mean([x[m] for x in bp]))
        out[m] = {'retest': round(r, 3), 'between_papers': round(b, 3), 'chance_corrected': round((r - b) / (1 - b), 3)}
    put('retest.between_paper_baseline', {'retest_pairs': len(rt), 'between_paper_pairs': len(bp), **out},
        'Test-retest mean (calc1 against gold-r2, same paper) next to the mean over every pair of two different papers\' calc1 '
        'codings (all unordered pairs of valid calc1 codings); chance_corrected = (retest - baseline) / (1 - baseline). '
        'Sets and sequences after merging consecutive repeats (check_coding.seq); categorical fields as share of pairs that match.', I)

    # 2. quote existence in the text the coder was given
    q = json.loads(QUEUE_NOW.read_text())
    e1 = set().union(*[set(b['keys']) for b in state['batches'] if b['tag'] == 'calc1' and b.get('collected')])
    xs = {r['key']: r for r in read_json(DERIVED / 'calc1' / 'xml_status.json')}
    route_counts = Counter()
    stats = {r: Counter() for r in ('xml', 'pdf')}
    below90, stub_rows = [], []
    for k in sorted(ok1):
        c = ok1[k]
        pdf = ROOT / q[k]['file']
        said_xml = any('xml' in d.lower() for d in c.get('documents', [])) or 'xml' in str(c.get('pages_convention', '')).lower()
        xml_file = pdf.with_suffix('.xml.txt')
        xml_text = xml_file.read_text() if xml_file.is_file() else ''
        if xs.get(k, {}).get('xml') and len(xml_text) < 15000:
            stub_rows.append({'key': k, 'chars': len(xml_text), 'route': xs[k].get('route'), 'coder_reports_xml': said_xml})
        r = 'xml' if said_xml else 'pdf'
        route_counts[r] += 1
        # pdftotext in reading order and in raw content-stream order (-raw); two-column pages interleave lines in the first
        txt_pdf = ' | '.join(_norm(subprocess.run(['pdftotext', *mode, str(pdf), '-'], capture_output=True, text=True).stdout)
                             for mode in ([], ['-raw']))
        txt_xml = _norm(xml_text) if said_xml else ''
        qs = [s.get('quote', '') for s in next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps'] if (s.get('quote') or '').strip()]
        f_x = [_quote_found(x, txt_xml) for x in qs] if said_xml else []
        f_p = [_quote_found(x, txt_pdf) for x in qs]
        f_any = [a or b for a, b in zip(f_x or [False] * len(qs), f_p)]
        st_ = stats[r]
        st_['papers'] += 1; st_['quotes'] += len(qs); st_['found_any'] += sum(f_any); st_['found_pdftotext'] += sum(f_p)
        if said_xml:
            st_['found_xml'] += sum(f_x)
        if qs and sum(f_any) / len(qs) < 0.9:
            below90.append({'key': k, 'route': r, 'quotes': len(qs), 'found': sum(f_any)})
    res = {}
    for r, s in stats.items():
        res[r] = dict(s) | {'share_found_any': round(s['found_any'] / s['quotes'], 4) if s['quotes'] else None,
                            'share_found_pdftotext': round(s['found_pdftotext'] / s['quotes'], 4) if s['quotes'] else None}
        if r == 'xml':
            res[r]['share_found_xml'] = round(s['found_xml'] / s['quotes'], 4) if s['quotes'] else None
    put('quotes.calc1_existence', {'papers': len(ok1), **res, 'papers_below_90pct': below90},
        'Do the final-paper quotes of the valid calc1 codings exist in the source text? Route = what the coder reports in '
        '`documents` or `pages_convention` (xml: PDF plus located publisher XML text; pdf: PDF only). A quote counts as found when '
        'every fragment between ellipses occurs in the text after lower-casing, joining line-break hyphens and collapsing '
        'punctuation and spaces to single spaces (NFKC first, so ligatures split). Texts: <key>.xml.txt (xml route) and pdftotext '
        'of the PDF in default and -raw order (both routes). '
        'Existence only: whether the quote supports the step is not checked.', I + ['PDFs and <key>.xml.txt (private/download-queue.json)', 'pdftotext'])
    put('text.calc1.e1_route', {'e1_papers': len(e1), 'xml_status_true_now': sum(bool(xs.get(k, {}).get('xml')) for k in e1),
                                'xml_fetched_after_e1_elsevier': sum(xs.get(k, {}).get('route') == 'elsevier' for k in e1 if xs.get(k, {}).get('xml')),
                                'valid_codings_by_reported_route': counter(route_counts), 'xml_files_under_15000_chars': stub_rows},
        'E1 text route. xml_status_true_now counts E1 papers with publisher XML in derived/calc1/xml_status.json today; the Elsevier '
        'XML files were fetched on October 27, after E1 was submitted (October 25), so the coder did not see them. '
        'valid_codings_by_reported_route uses the coder\'s own `documents` field. Short XML files (under 15,000 characters) are listed.',
        ['derived/calc1/xml_status.json', 'private/analysis/codings/api/state.json', 'private/analysis/codings/api/calc1'])

    # 3. textbook order as an ordered subsequence (gaps allowed) and as a contiguous run, merged node sequences (as g13)
    def subseq(xs_, pat):
        it = iter(xs_)
        return all(p in it for p in pat)
    nodes = {k: seq(c, 'node') for k, c in ok1.items()}
    tb = list('QHSDFOC')
    put('workflow.textbook_order', {'papers': len(nodes),
                                    'QHSDFOC_ordered_with_gaps': sum(subseq(v, tb) for v in nodes.values()),
                                    'QHSDFOC_contiguous': sum(''.join(tb) in ''.join(v) for v in nodes.values()),
                                    'QHC_ordered_with_gaps': sum(subseq(v, 'QHC') for v in nodes.values()),
                                    'QHDOC_ordered_with_gaps': sum(subseq(v, 'QHDOC') for v in nodes.values()),
                                    'papers_with_D': sum('D' in v for v in nodes.values())},
        'Papers whose merged final-paper node sequence contains the textbook order question, hypothesize, simulate, design, find '
        'conditions, observe, compare (QHSDFOC) as an ordered subsequence with other steps allowed between (the g13 rule), as a '
        'contiguous run, and shorter orders.', I)

    # 4. coded against uncoded eligible AGU papers (selection at E1)
    man = manifest('calc1')
    agu = [m['key'] for m in man if m['doi'].startswith('10.1029/')]
    def jgroup(j):
        j = clean(j)
        return 'Geophysical Research Letters' if j.startswith('Geophysical Research Letters') else \
            ('Journal of Geophysical Research (all sections)' if j.startswith('Journal of Geophysical Research') else 'other AGU journals')
    def summ(ks_):
        ms = [met[k] for k in ks_ if k in met]
        cn = [m['cnp'] for m in ms if m.get('cnp') is not None]
        return {'n': len(ms), 'open_access': sum(bool(m['is_oa']) for m in ms), 'cnp_median': round(float(np.median(cn)), 3) if cn else None,
                'journals': counter(Counter(jgroup(m['journal']) for m in ms))}
    put('calc1.agu_selection', {'coded': summ([k for k in agu if k in ok1]), 'not_coded': summ([k for k in agu if k not in ok1])},
        'Eligible round-1 AGU papers (DOI prefix 10.1029), coded at E1 against not coded: open access, median cnp, and journal '
        'group (GRL, the letters journal; JGR, the full-length journals; other).', ['derived/calc1/manifest.jsonl', 'derived/gold/metrics.json'] + I)

    # 5. within-family estimator choice for the steps and revisits associations (g20 confounding uses pooled ranks centred)
    kk = sorted(k for k in ok1 if k in met)
    fam = np.array([g20.family(met[k]) for k in kk])
    F = {k: g17.features(ok1[k]) for k in kk}
    rng = np.random.default_rng(2026)
    def rerank_rho(f, y, s):
        a, b = np.empty(len(f)), np.empty(len(f))
        for g in np.unique(s):
            i = np.flatnonzero(s == g)
            a[i], b[i] = g20.rank(f[i]), g20.rank(y[i])
        return g20.within_rho(a, b, s)[0]
    est = {}
    for feat in ('steps', 'revisits'):
        for oc in ('cnp', 'fwci'):
            idx = [i for i, k in enumerate(kk) if met[k].get(oc) is not None]
            f = np.array([F[kk[i]]['num:' + feat] for i in idx], float)
            y = np.array([met[kk[i]][oc] for i in idx], float)
            s = fam[idx]
            pooled = g20.within_rho(g20.rank(f), g20.rank(y), np.unique(s, return_inverse=True)[1])[0]
            rr = rerank_rho(f, y, s)
            groups = [np.flatnonzero(s == g) for g in np.unique(s)]
            bs = []
            for _ in range(2000):
                i = np.concatenate([gi[rng.integers(0, len(gi), len(gi))] for gi in groups])
                bs.append(rerank_rho(f[i], y[i], s[i]))
            est[f'{feat}~{oc}'] = {'pooled_ranks_centred': round(pooled, 3), 'ranks_within_family': round(rr, 3),
                                   'ranks_within_family_ci': g20.ci(bs), 'n': len(idx)}
    put('confounding.family_estimators', est,
        'Within-journal-family Spearman of steps and revisits with cnp and fwci under two estimators: pooled ranks centred '
        'within family (the g20 confounding estimator) and ranks recomputed inside each family, then centred. Interval: 2000 '
        'stratified bootstrap resamples (seed 2026). Families by g20_topics_journals.family, not pooled.', I + ['derived/gold/metrics.json'])

    # 6. E4 labelers: Cohen kappa between labeler a and labeler b
    labels = read_json(DERIVED / 'review' / 'visibility_labels.json')
    ab = [(s['label_a'], s['label_b']) for p in labels for s in p['steps'] if s.get('label_a') and s.get('label_b')]
    n = len(ab)
    po = sum(a == b for a, b in ab) / n
    ca, cb = Counter(a for a, _ in ab), Counter(b for _, b in ab)
    pe = sum(ca[c] * cb[c] for c in set(ca) | set(cb)) / n / n
    put('vis.labeler_kappa', {'steps': n, 'agreed': sum(a == b for a, b in ab), 'observed': round(po, 4), 'chance': round(pe, 4),
                              'cohen_kappa': round((po - pe) / (1 - pe), 3), 'labeler_marginals_a': counter(ca), 'labeler_marginals_b': counter(cb)},
        'Agreement of the two E4 labelers (label_a, label_b) before adjudication: Cohen kappa = (observed - chance) / (1 - chance), '
        'chance from each labeler\'s own label frequencies.', ['derived/review/visibility_labels.json'])

    # 7. resubmissions within E1, E2 and E3
    res_ = {}
    for tag in ('calc1', 'gold-r2', 'calc1-review'):
        bs_ = [b for b in state['batches'] if b['tag'] == tag and b.get('collected')]
        cnt = Counter(k for b in bs_ for k in b['keys'])
        again = sorted(k for k, v in cnt.items() if v > 1)
        okt = ok1 if tag == 'calc1' else (ok2 if tag == 'gold-r2' else load_valid(tag)[0])
        stp = lambda ks_: [len(next(s for s in okt[k]['sequences'] if s['kind'] == 'final_paper')['steps']) for k in ks_ if k in okt]
        res_[tag] = {'papers': len(cnt), 'requests': sum(cnt.values()), 'papers_resubmitted': len(again),
                     'requests_at_64000_max_tokens': sum(len(b['keys']) for b in bs_ if b.get('max_tokens') == 64000),
                     'steps_median_resubmitted': st.median(stp(again)) if stp(again) else None,
                     'steps_median_first_pass': st.median(stp([k for k in cnt if k not in again])) if stp([k for k in cnt if k not in again]) else None}
    put('coding.resubmissions', res_,
        'Collected batches per tag: papers, requests, papers sent more than once (a failed or invalid first answer), requests sent '
        'with max_tokens 64000, and median unmerged final-paper steps of valid codings for resubmitted and first-pass papers.',
        ['private/analysis/codings/api/state.json'] + I)


def audit_extra2(met: dict) -> None:
    """Second batch for the October 27 review: the retest sample against the coded set, and agent node shares for
    research systems and general patterns separately."""
    import g20_topics_journals as g20
    ok1, _ = load_valid('calc1')
    ok2, _ = load_valid('gold-r2')
    I = ['private/analysis/codings/api/calc1', 'private/analysis/codings/api/gold-r2']
    # retest sample against the coded set
    pairs = sorted(set(ok1) & set(ok2))
    mix = lambda ks: {'n': len(ks), 'family': counter(Counter(g20.family(met[k]) for k in ks if k in met)),
                      'entry_state': counter(Counter(ok1[k]['entry']['state'] for k in ks)),
                      'ring': counter(Counter(met[k].get('ring') for k in ks if k in met))}
    put('retest.sample_mix', {'retest_pairs': mix(pairs), 'coded': mix(sorted(ok1))},
        'Journal family (g20 rule), entry state (first coding) and ring of the 50 retest papers (gold papers with full text at E1 '
        'and both codings valid) against all 233 coded papers.', I + ['derived/gold/metrics.json'])
    # agent node shares by system family (research systems against general patterns), two coders averaged
    man = {x['key']: x for x in json.loads((PRIVATE / 'analysis' / 'reliability' / 'agents_manifest.json').read_text())}
    AG = PRIVATE / 'analysis' / 'reliability' / 'codings' / 'agents'
    coders = sorted(p.name for p in AG.iterdir() if p.is_dir())
    marks = {cd: {json.loads(f.read_text())['key']: json.loads(f.read_text()) for f in sorted((AG / cd).glob('*.json'))} for cd in coders}
    out = {}
    for grp, keep in [('research systems (manifest family science)', lambda f: f == 'science'),
                      ('general patterns and tools (other families)', lambda f: f != 'science')]:
        ks = sorted(k for k in man if keep(man[k]['family']))
        out[grp] = {'systems': len(ks), 'names': [man[k]['system'] for k in ks],
                    'node_share_full': {n: round(float(np.mean([np.mean([marks[cd][k]['nodes'][n]['mark'] == 'full' for cd in coders]) for k in ks])), 3)
                                        for n in 'NEOIQHSDFCVXKPR'}}
    agree_ = [marks[coders[0]][k]['nodes'][n]['mark'] == marks[coders[1]][k]['nodes'][n]['mark'] for k in man for n in 'NEOIQHSDFCVXKPR'] if len(coders) == 2 else []
    put('agents.node_share_by_group', {'coders': coders, **out, 'mark_agreement_two_coders': round(float(np.mean(agree_)), 3) if agree_ else None},
        'Share of agent systems whose loop runs each node in full (loop codebook 0.1.2), averaged over the two blind coders, for '
        'research systems (agents_manifest.json family "science") and for general patterns, coding, multi-agent and deep-research '
        'systems; and raw agreement of the two coders on the mark (full, partial, none) over 31 systems x 15 nodes.',
        ['private/analysis/reliability/agents_manifest.json', 'private/analysis/reliability/codings/agents/{opus-b,sonnet-c}'])


def main() -> None:
    os.chdir(ROOT)  # code_papers.candidates() resolves queue file paths against the working directory
    state = json.loads(STATE.read_text())
    met = {('g22_' + m['id']): m for m in read_json(DERIVED / 'gold' / 'metrics.json')}
    costs(state)
    sub, _ = round1(state, met)
    text_route(sub)
    fetch(met)
    round2(state)
    visibility(state, met)
    agents()
    outcomes(met)
    backlog(state)
    gold()
    setup()
    coded_features(met)
    outcomes_extra()
    review_extra(state)
    cost_extra(state)
    loop_pilot()
    audit_extra(state, met)
    audit_extra2(met)
    write_json(OUT, VALUES, ['private/analysis/codings/api/state.json', 'private/analysis/codings/api/{calc1,calc1-review,r2}',
                             'derived/{gold,calc1,r2,r2calc,review,outcomes}', rel(QUEUE_OCT27), 'private/download-queue.json'],
               {'publisher_rule': 'DOI registrant prefix (PREFIX in g19_report_numbers.py); 10.1029 = AGU', 'cap_usd': CAP_USD,
                'chars_per_token': CHARS_PER_TOKEN, 'max_chars': MAX_CHARS})
    log('g19_report_numbers.py', 'reported numbers recomputed from data (counts, costs, tokens, fetch)', len(VALUES),
        f"r2 codings {'present' if 'r2.coded_valid' in VALUES else 'absent'}")
    for k, v in VALUES.items():
        print(k, '=', json.dumps(v['value'], ensure_ascii=False))


if __name__ == '__main__':
    main()
