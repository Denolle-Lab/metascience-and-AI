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
from common import ROOT, DATA, DERIVED, log, read_json, write_json
from check_coding import validate
import code_papers_open as cpo  # tools/ (on the path via common); imports code_papers
import g17_outcomes as g17

API = ROOT / 'private' / 'analysis' / 'codings' / 'api'
STATE = API / 'state.json'
QUEUE_NOW = ROOT / 'private' / 'download-queue.json'
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
        put(f'calc1.open_access.{name}', {'n': len(v), 'oa': sum(v), 'share': round(sum(v) / len(v), 3)},
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
        for when, q, qpath in [('oct27', q27, str(QUEUE_OCT27.relative_to(ROOT))), ('now', qnow, 'private/download-queue.json')]:
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
            'usd = (pages x 2300 x $4 + papers x 10000 x $20) / 1e6 x 0.5.', ['private/analysis/codings/api/state.json', str(QUEUE_OCT27.relative_to(ROOT))])
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
    write_json(OUT, VALUES, ['private/analysis/codings/api/state.json', 'private/analysis/codings/api/{calc1,calc1-review,r2}',
                             'derived/{gold,calc1,r2,r2calc,review,outcomes}', str(QUEUE_OCT27.relative_to(ROOT)), 'private/download-queue.json'],
               {'publisher_rule': 'DOI registrant prefix (PREFIX in g19_report_numbers.py); 10.1029 = AGU', 'cap_usd': CAP_USD,
                'chars_per_token': CHARS_PER_TOKEN, 'max_chars': MAX_CHARS})
    log('g19_report_numbers.py', 'reported numbers recomputed from data (counts, costs, tokens, fetch)', len(VALUES),
        f"r2 codings {'present' if 'r2.coded_valid' in VALUES else 'absent'}")
    for k, v in VALUES.items():
        print(k, '=', json.dumps(v['value'], ensure_ascii=False))


if __name__ == '__main__':
    main()
