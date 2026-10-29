#!/usr/bin/env python3
"""Open-review 2022 draw (set cop22): a third set of 2022 papers, each with a public review record: the Copernicus (EGU)
discussion journals (referee and author comments, author response AR, tracked-changes manuscript ATC, discussion
preprint) and, by PI decision of October 28, 2026, Nature Communications (NC) and Communications Earth & Environment (CEE)
Earth articles with a peer review file (referee reports and author responses, no discussion preprint, so no
submitted-version layer unless a preprint is linked). Purpose: reconstruct the review-induced, disclosed and revised
layers of each workflow (experiment E3, g26, g27) on a sample large enough to test, with the outcome measures of rounds
1 and 2. Every journal has equal weight in the draw (PI decision, October 28).

Steps (subcommands; run in this order)
frame    The frame: 2022 Copernicus final papers in the research area, with a public discussion.
         Journals  the 24 Copernicus journals in which at least half of the 2022 final papers had a discussion
                   preprint (derived/review/inventory_parts/copernicus.json, g28: Crossref with_discussion /
                   crossref_final for 2022). OpenAlex source ids from g28's COPERNICUS table. Journals that OpenAlex
                   files under another host (WCD, GChron, GC) are treated as Copernicus venues here; g02 missed them.
         Works     OpenAlex, primary_location.source.id = one of the journals, with g02's base filter
                   (publication_year 2022, type article, has an abstract, at least 15 references) and g02's select.
         Rules     applied in this order, each count kept: DOI with prefix 10.5194; Earth-science venue (g02: more
                   than half of the journal's top-25 OpenAlex topics geoscience under the breadth v1 map); no review,
                   overview or perspective title (g02 regex); research area = g02's rings (core: primary topic is one
                   of the convenor's topics from derived/gold/author_profile.json; broad: primary topic in one of g02's
                   neighbouring Earth-science subfields); no convenor author or co-author (g02, g03, g18); not in the
                   round-1 preselection (derived/gold/preselect.json, 600) nor the round-2 preselection
                   (derived/r2/preselect.json, 277); public discussion = Crossref asserts has-preprint and at least one
                   has-review DOI (referee or author comment registered as a DOI).
         Crossref  the relation records come from g28's cached Crossref pages (issn, prefix 10.5194, relation.type
                   has-review, by publication year 2021-2023, 1000 rows per page); a DOI found in none of them is asked
                   for alone (works/<doi>). Requests go through g28.crossref() (cache raw/inventory/crossref/, fetch log
                   raw/inventory/fetch_log.jsonl, 1 s pause).
         Nature    NC (S64187185) and CEE (S4210221880), same base filter, primary topic field 19 (Earth and Planetary
                   Sciences, the g28 definition), then the same rules (DOI 10.1038, paper topic geoscience as g02 keeps
                   multidisciplinary journals, title, area, convenor, rounds 1 and 2); in the frame when the article page
                   links a peer review file (g28.page() with g28.nature_evidence: evidence and page hash kept, not the
                   page, since it carries the paper text; 2 s pause).
         The g02 pool (derived/gold/pool.json) is the frame of rounds 1 and 2, not a drawn set: frame papers that are
         also pool papers are kept and flagged in_pool. Output derived/cop22/frame.json (every work, with the first
         rule it failed).
check    Does a 2022 discussion carry the AR and the ATC? Three sources, each reported apart:
         (a) the g28 era check (2018 and 2023 samples; no 2022 sample exists), (b) the 61 round-1 Copernicus papers
         whose review records g15 fetched (derived/review/open_review_index.json, file names -AR<n>.pdf, -ATC<n>.pdf),
         (c) one frame paper per journal (random.Random(SEED), frame sorted by id), its <stem>-discussion.html page
         read through g28.page() (kept verbatim in raw/inventory/pages/, 1.5 s pause) and parsed with
         g28.parse_discussion(). Output derived/cop22/availability.json.
draw     Equal quota per journal (PI decision, October 28): q = the smallest quota with sum over journals of
         min(q, frame papers) >= N; a journal with fewer frame papers than q gives all of them (its shortfall is
         recorded, not redistributed). Within a journal, the quota is spread over impact quintiles (OpenAlex
         citation_normalized_percentile, quintile = min(4, int(cnp * 5)), as g03 and g18) as equally as the frame
         allows (water filling: a quintile with too few papers gives all it has, the rest goes to the others; the
         quintiles limited this way are recorded per journal); within a journal x quintile cell, round robin over the
         rings (core, broad; order shuffled), random within a ring. random.Random(SEED), frame sorted by OpenAlex id.
         No Copernicus frame paper has cnp below 0.2, so quintile 1 is empty there. draw_order interleaves the
         journals proportionally (paper i of a journal's n gets (i + 0.5) / n), so the first k papers of draw_order are
         an approximately equal-weight sub-draw if the coding budget forces a smaller set.
         Output derived/cop22/preselect.json (g02 record format plus journal_abbr, impact_quintile, draw_order, so
         g04, g06, g10 and g12 run unchanged with ROADMAP_SET=cop22 ROADMAP_CALC=cop22calc) and
         derived/cop22/draw_manifest.jsonl (key, doi, stratum, openalex, in_gold), the input to g10 --manifest and
         g15 --manifest before the eligibility screen.
prf      For the drawn NC and CEE papers: the peer review file PDFs linked on the article page, saved as
         review/<key>/<file>.pdf (open download, no key, 2 s pause, each request in raw/inventory/fetch_log.jsonl),
         a located text review/<key>/peer_review.txt ("[PRF1 p.3] ..."), and the index
         derived/review/open_review_index_nature22.json (files with sha256, words, author response detected by phrase,
         Crossref has-preprint, layers present).
batches  The eligibility screen input in batches of 10, derived/cop22/screen_batches/batch_NNN.json, from
         derived/cop22/screen_input.json (g06), records unchanged and in order (as the round-2 batches); the screen
         itself is the workflow tools/roadmap/workflows/gold-eligibility-screen.js with
         args {"dir": ".../derived/cop22/screen_batches", "n_batches": <n>}, then g07.
report   Counts at each step, journal mix and shortfalls, AR/ATC availability among the drawn papers (g15 index for
         cop22, prf index) and the round-2 Copernicus papers, into derived/cop22/DRAW.md and derived/cop22/draw_report.json.

Run   : python tools/roadmap/g32_copernicus_draw.py frame|check|draw|prf|batches|report [--n 160] [--seed 2028]
Then  : ROADMAP_SET=cop22 ROADMAP_CALC=cop22calc python tools/roadmap/g06_abstracts.py, g04_metrics.py,
        g32 batches; g15_open_review.py --manifest derived/cop22/draw_manifest.jsonl --index ...; g10_fetch_xml.py
        --manifest derived/cop22/draw_manifest.jsonl; g26_translation.py fetch --index ... --record ...
"""
from __future__ import annotations
import argparse
import csv
import json
import random
import re
import urllib.parse
from collections import Counter, defaultdict

from common import DERIVED, TODAY, decision, log, openalex, paged, read_json, rel, sid, write_json
import g02_pool as g02
import g28_review_inventory as g28

SET = DERIVED / 'cop22'
INV_PART = DERIVED / 'review' / 'inventory_parts' / 'copernicus.json'
R1_INDEX = DERIVED / 'review' / 'open_review_index.json'
COP_INDEX = DERIVED / 'review' / 'open_review_index_cop22.json'
R2_INDEX = DERIVED / 'review' / 'open_review_index_r2.json'
YEAR = 2022
SEED, N = 2028, 160
NATURE = {'NC': 'S64187185', 'CEE': 'S4210221880'}   # Nature Communications, Communications Earth & Environment
NAT_INDEX = DERIVED / 'review' / 'open_review_index_nature22.json'


def quintile(x):
    return 0 if x is None else min(4, int(x * 5))


def journals() -> dict:
    """{abbr: (source id, issn, final 2022, with discussion 2022)} for journals with a discussion for >= half of 2022 papers."""
    inv = read_json(INV_PART)
    out = {}
    for ab, j in inv.items():
        fin, dis = (j.get('crossref_final') or {}).get(str(YEAR), 0), (j.get('with_discussion') or {}).get(str(YEAR), 0)
        if fin and dis / fin >= 0.5:
            out[ab] = (j['openalex_source'], j['issn_crossref'], fin, dis)
    return out


def crossref_relations(issn: str) -> dict:
    """{doi lower: relation} for the journal's papers with has-review, from g28's cached year pages (2021-2023)."""
    out = {}
    for y in (YEAR - 1, YEAR, YEAR + 1):
        offset = 0
        while True:
            m = g28.crossref('works', {'filter': f'issn:{issn},prefix:10.5194,relation.type:has-review,'
                                                 f'from-pub-date:{y}-01-01,until-pub-date:{y}-12-31',
                                       'select': 'DOI,relation', 'rows': 1000, 'offset': offset})
            items = m.get('items', [])
            for it in items:
                out[it['DOI'].lower()] = it.get('relation', {})
            offset += 1000
            if len(items) < 1000 or offset >= m.get('total-results', 0):
                break
    return out


def asserted(relation: dict, kind: str) -> list[str]:
    return sorted({x['id'] for x in relation.get(kind, []) if x.get('asserted-by') == 'subject'})


# ---------------------------------------------------------------------------------------------------- frame
def frame() -> None:
    J = journals()
    by_src = {v[0]: k for k, v in J.items()}
    g02.SOURCES.update({s: ('Copernicus', 'open') for s in by_src})   # WCD, GChron, GC are filed under another host
    ov = {r['topic_id']: {'geoscience': 'geo', 'adjacent': 'near', 'outside': 'far'}[r['verdict'].strip()]
          for r in csv.DictReader(open(g02.AUDIT)) if r.get('verdict', '').strip() in ('geoscience', 'adjacent', 'outside')}
    prof = read_json(DERIVED / 'gold' / 'author_profile.json')
    mine, coauth = set(prof['author_ids']), set(prof['coauthor_ids'])
    core = {t['topic_id'] for t in g02.core_topics(prof)}
    r1 = {p['id'] for p in read_json(DERIVED / 'gold' / 'preselect.json')}
    r2 = {p['id'] for p in read_json(DERIVED / 'r2' / 'preselect.json')}
    pool = {p['id'] for p in read_json(DERIVED / 'gold' / 'pool.json')}
    works = paged('works', {'filter': f"{g02.BASE},primary_location.source.id:{'|'.join(sorted(by_src))}", 'select': g02.SEL})
    rels = {}
    for ab in sorted(J):
        rels.update(crossref_relations(J[ab][1]))
    rows, single = [], 0
    for w in sorted(works, key=lambda w: w['id']):
        src = sid(((w.get('primary_location') or {}).get('source') or {}).get('id'))
        doi = (w.get('doi') or '').replace('https://doi.org/', '')
        pt = w.get('primary_topic') or {}
        ring = 'core' if sid(pt.get('id')) in core else 'broad' if sid((pt.get('subfield') or {}).get('id')) in g02.BROAD_SUBFIELDS else None
        aus = {sid((a.get('author') or {}).get('id')) for a in w.get('authorships', [])}
        rec = g02.slim(w, ring or 'outside', mine, coauth) if doi.lower().startswith('10.5194/') else {'id': sid(w['id']), 'doi': doi}
        rec.update(journal_abbr=by_src.get(src), in_pool=sid(w['id']) in pool)
        if not doi.lower().startswith('10.5194/'):
            rec['excluded'] = 'DOI not 10.5194'
        elif not g02.earth_venue(src, ov):
            rec['excluded'] = 'not an Earth-science venue (g02 rule)'
        elif g02.REVIEW.search(w.get('title') or ''):
            rec['excluded'] = 'review, overview or perspective (title)'
        elif ring is None:
            rec['excluded'] = 'outside the research area (no core topic, no broad subfield)'
        elif aus & mine or aus & coauth:
            rec['excluded'] = 'convenor author or co-author'
        elif rec['id'] in r1:
            rec['excluded'] = 'in the round-1 preselection'
        elif rec['id'] in r2:
            rec['excluded'] = 'in the round-2 preselection'
        else:
            r = rels.get(doi.lower())
            if r is None:
                single += 1
                r = g28.crossref('works/' + urllib.parse.quote(doi, safe='/')).get('relation', {})
            rec['preprint_doi'] = (asserted(r, 'has-preprint') or [None])[0]
            rec['n_review_dois'] = len(asserted(r, 'has-review'))
            if not rec['preprint_doi'] or not rec['n_review_dois']:
                rec['excluded'] = 'no public discussion (Crossref has-preprint and has-review)'
        rows.append(rec)
    steps = Counter(r.get('excluded', 'in frame') for r in rows)
    order = ['DOI not 10.5194', 'not an Earth-science venue (g02 rule)', 'review, overview or perspective (title)',
             'outside the research area (no core topic, no broad subfield)', 'convenor author or co-author',
             'in the round-1 preselection', 'in the round-2 preselection',
             'no public discussion (Crossref has-preprint and has-review)']
    left, flow = len(rows), [(f'OpenAlex works, {len(J)} Copernicus journals, g02 base filter', len(rows))]
    for o in order:
        left -= steps.get(o, 0)
        flow.append((o, left))
    nrows, nflow = nature_rows(ov, core, mine, coauth, r1, r2, pool)
    rows += nrows
    venue = {ab: round(g02._SRC.get(J[ab][0], 0.0), 3) for ab in sorted(J)}
    params = {'year': YEAR, 'journals': {k: list(v) for k, v in J.items()}, 'nature_journals': NATURE, 'base_filter': g02.BASE,
              'core_topics': sorted(core), 'broad_subfields': g02.BROAD_SUBFIELDS, 'review_regex': g02.REVIEW.pattern,
              'venue_geo_share': venue, 'flow': flow, 'flow_nature': nflow, 'crossref_single_lookups': single}
    write_json(SET / 'frame.json', rows, ['OpenAlex works API', rel(INV_PART), 'derived/gold/author_profile.json',
                                         'derived/gold/preselect.json', 'derived/r2/preselect.json', 'derived/gold/pool.json',
                                         rel(g02.AUDIT), 'Crossref REST API (g28 cache)',
                                         'nature.com article pages (evidence only, g28 cache)'], params)
    fr = [r for r in rows if 'excluded' not in r]
    log('g32_copernicus_draw.py frame', f'{YEAR} frame: Copernicus discussion journals with a public discussion, Nature '
        'Communications and Communications Earth & Environment with a peer review file; research area', len(fr),
        'Copernicus: ' + '; '.join(f'{a}: {b}' for a, b in flow) + ' | Nature: ' + '; '.join(f'{a}: {b}' for a, b in nflow)
        + f"; {sum(r['in_pool'] for r in fr)} also in the g02 pool; {single} single Crossref lookups; web {dict(g28._n)}")
    for a, b in flow + nflow:
        print(f'{b:6d}  {a}')
    print('in frame by journal', Counter(r['journal_abbr'] for r in fr).most_common())
    print('by ring x quintile', sorted(Counter((r['ring'], quintile(r['cnp']) + 1) for r in fr).items()))
    print('venue geo share', venue)


def nature_rows(ov, core, mine, coauth, r1, r2, pool) -> tuple[list, list]:
    """Nature Communications and Communications Earth & Environment, 2022, Earth articles (OpenAlex primary topic field
    19), same base filter, area and exclusion rules as the Copernicus part; in the frame when the article page links a
    peer review file (g28.nature_evidence; the page itself is not kept, only the evidence and the page hash)."""
    by_src = {v: k for k, v in NATURE.items()}
    works = paged('works', {'filter': f"{g02.BASE},primary_location.source.id:{'|'.join(sorted(by_src))},"
                                      f"primary_topic.field.id:{g28.FIELD_EARTH}", 'select': g02.SEL})
    rows = []
    for w in sorted(works, key=lambda w: w['id']):
        src = sid(((w.get('primary_location') or {}).get('source') or {}).get('id'))
        doi = (w.get('doi') or '').replace('https://doi.org/', '')
        pt = w.get('primary_topic') or {}
        ring = 'core' if sid(pt.get('id')) in core else 'broad' if sid((pt.get('subfield') or {}).get('id')) in g02.BROAD_SUBFIELDS else None
        aus = {sid((a.get('author') or {}).get('id')) for a in w.get('authorships', [])}
        rec = g02.slim(w, ring or 'outside', mine, coauth) if doi.lower().startswith('10.1038/') else {'id': sid(w['id']), 'doi': doi}
        rec.update(journal_abbr=by_src.get(src), in_pool=sid(w['id']) in pool)
        if not doi.lower().startswith('10.1038/'):
            rec['excluded'] = 'DOI not 10.1038'
        elif not g02.topic_geo(sid(pt.get('id')), sid((pt.get('field') or {}).get('id')), ov):
            rec['excluded'] = 'paper topic not geoscience (g02 multidisciplinary rule)'
        elif g02.REVIEW.search(w.get('title') or ''):
            rec['excluded'] = 'review, overview or perspective (title)'
        elif ring is None:
            rec['excluded'] = 'outside the research area (no core topic, no broad subfield)'
        elif aus & mine or aus & coauth:
            rec['excluded'] = 'convenor author or co-author'
        elif rec['id'] in r1:
            rec['excluded'] = 'in the round-1 preselection'
        elif rec['id'] in r2:
            rec['excluded'] = 'in the round-2 preselection'
        else:
            ev = g28.page('https://www.nature.com/articles/' + doi.split('/', 1)[1], keep=False, extract=g28.nature_evidence)
            e = ev.get('evidence') or {}
            rec.update(page_status=ev.get('status'), prf_links=e.get('prf_links') or [],
                       peer_review_information=e.get('peer_review_information'))
            if ev.get('status') != 200:
                rec['excluded'] = f"article page not read (HTTP {ev.get('status')})"
            elif not e.get('has_peer_review_file') or not e.get('prf_links'):
                rec['excluded'] = 'no peer review file linked on the article page'
        rows.append(rec)
    steps = Counter(r.get('excluded', 'in frame') for r in rows)
    order = ['DOI not 10.1038', 'paper topic not geoscience (g02 multidisciplinary rule)', 'review, overview or perspective (title)',
             'outside the research area (no core topic, no broad subfield)', 'convenor author or co-author',
             'in the round-1 preselection', 'in the round-2 preselection']
    order += sorted(k for k in steps if k.startswith('article page not read')) + ['no peer review file linked on the article page']
    left, flow = len(rows), [('OpenAlex works, NC and CEE, field 19, g02 base filter', len(rows))]
    for o in order:
        left -= steps.get(o, 0)
        flow.append((o, left))
    return rows, flow


# ---------------------------------------------------------------------------------------------------- check
def check() -> None:
    inv = read_json(INV_PART)
    era = defaultdict(lambda: Counter())
    for j in inv.values():
        for y, recs in (j.get('era_check') or {}).items():
            for r in recs:
                if r.get('has_discussion_page'):
                    era[y]['pages'] += 1
                    era[y]['AR'] += bool(r.get('AR'))
                    era[y]['ATC'] += bool(r.get('ATC'))
    r1 = [r for r in read_json(R1_INDEX) if 'comments' in r]
    r1c = {'pages': len(r1), 'AR': sum(any(re.search(r'-AR\d*\.pdf$', f) for f in r['files']) for r in r1),
           'ATC': sum(any(re.search(r'-ATC\d*\.pdf$', f) for f in r['files']) for r in r1),
           'no_open_discussion': sum(1 for r in read_json(R1_INDEX) if r.get('no_open_discussion'))}
    fr = sorted([r for r in read_json(SET / 'frame.json') if 'excluded' not in r and r['journal_abbr'] not in NATURE],
                key=lambda r: r['id'])
    rng = random.Random(SEED)
    by_j = defaultdict(list)
    for r in fr:
        by_j[r['journal_abbr']].append(r)
    live = []
    for ab in sorted(by_j):
        r = by_j[ab][rng.randrange(len(by_j[ab]))]
        cr = g28.crossref('works/' + urllib.parse.quote(r['doi'], safe='/'))
        land = cr.get('resource', {}).get('primary', {}).get('URL', '').rstrip('/') + '/'
        stem = r['doi'].split('/', 1)[1]
        pg = g28.page(land + stem + '-discussion.html', keep=True)
        rec = {'journal': ab, 'key': 'g22_' + r['id'], 'doi': r['doi'], 'status': pg['status']}
        if pg['status'] == 200:
            rec.update(g28.parse_discussion(pg['text']))
        live.append(rec)
        print(ab, rec['doi'], rec['status'], rec.get('comments'), 'AR', rec.get('AR'), 'ATC', rec.get('ATC'), flush=True)
    ok = [r for r in live if r['status'] == 200]
    out = {'era_check': {y: dict(c) for y, c in sorted(era.items())}, 'round1_records': r1c,
           'frame_sample': {'pages': len(ok), 'AR': sum(bool(r.get('AR')) for r in ok), 'ATC': sum(bool(r.get('ATC')) for r in ok),
                            'papers': live}}
    write_json(SET / 'availability.json', out, [rel(INV_PART), rel(R1_INDEX), rel(SET / 'frame.json'),
                                                'Copernicus discussion pages (g28 page cache)'], {'seed': SEED})
    log('g32_copernicus_draw.py check', f'AR and ATC on {YEAR} Copernicus discussion pages', len(ok),
        f"frame sample AR {out['frame_sample']['AR']}/{len(ok)}, ATC {out['frame_sample']['ATC']}/{len(ok)}; "
        f"round-1 records AR {r1c['AR']}/{r1c['pages']}, ATC {r1c['ATC']}/{r1c['pages']}; web {dict(g28._n)}")
    print(json.dumps({k: v for k, v in out.items() if k != 'frame_sample'}, indent=1))
    print('frame sample', {k: v for k, v in out['frame_sample'].items() if k != 'papers'})


# ---------------------------------------------------------------------------------------------------- draw
def fill(room: dict, total: int) -> tuple[dict, int]:
    """Spread total over the cells as evenly as their room allows (water filling); returns the allocation and what is left."""
    q = {c: 0 for c in room}
    while total > 0:
        open_ = [c for c in room if q[c] < room[c]]
        if not open_:
            break
        share = max(1, total // len(open_))
        for c in open_:
            add = min(share, room[c] - q[c], total)
            q[c] += add
            total -= add
            if total == 0:
                break
    return q, total


def journal_quota(avail: Counter, n: int) -> int:
    """The smallest equal per-journal quota q with sum over journals of min(q, frame papers) >= n."""
    q = 1
    while sum(min(q, v) for v in avail.values()) < n and q < max(avail.values()):
        q += 1
    return q


def draw(n: int, seed: int) -> None:
    fr = sorted([r for r in read_json(SET / 'frame.json') if 'excluded' not in r], key=lambda r: r['id'])
    avail = Counter(r['journal_abbr'] for r in fr)
    q = journal_quota(avail, n)
    rng = random.Random(seed)
    out, strat = [], {}
    for j in sorted(avail):
        mine = [r for r in fr if r['journal_abbr'] == j]
        cells = defaultdict(lambda: defaultdict(list))
        for r in mine:
            cells[quintile(r.get('cnp'))][r['ring']].append(r)
        room = {k: sum(len(v) for v in cells[k].values()) for k in range(5)}
        alloc, _ = fill(room, min(q, len(mine)))
        got = []
        for k in range(5):
            rings = sorted(cells[k])
            for ring in rings:
                rng.shuffle(cells[k][ring])
            rng.shuffle(rings)
            picked = []
            while len(picked) < alloc[k]:      # round robin over rings within a journal x quintile cell
                for ring in rings:
                    if cells[k][ring] and len(picked) < alloc[k]:
                        picked.append({**cells[k][ring].pop(), 'impact_quintile': k + 1})
            got += picked
        present = [k for k in range(5) if room[k]]
        strat[j] = {'frame': len(mine), 'drawn': len(got), 'shortfall': max(0, q - len(mine)),
                    'frame_by_quintile': {k + 1: room[k] for k in range(5)}, 'drawn_by_quintile': {k + 1: alloc[k] for k in range(5)},
                    # quintiles that got fewer papers than the largest quintile share because the frame ran out there
                    'limited_quintiles': [k + 1 for k in range(5) if alloc[k] == room[k] and alloc[k] < max(alloc.values())]}
        for i, r in enumerate(got):
            out.append({**r, '_f': ((i + 0.5) / len(got), rng.random())})
    out.sort(key=lambda r: r.pop('_f'))
    for k, r in enumerate(out, 1):
        r['draw_order'] = k
    short = {j: v['shortfall'] for j, v in strat.items() if v['shortfall']}
    params = {'n_target': n, 'journal_quota': q, 'seed': seed, 'frame': len(fr), 'journals': len(avail),
              'shortfall': short, 'strata': strat}
    write_json(SET / 'preselect.json', out, [rel(SET / 'frame.json')], params)
    (SET / 'draw_manifest.jsonl').write_text(''.join(json.dumps(
        {'key': 'g22_' + r['id'], 'doi': r['doi'], 'stratum': f"cop22 {r['journal_abbr']} {r['ring']}", 'openalex': r['id'],
         'in_gold': False}) + '\n' for r in sorted(out, key=lambda r: r['id'])))
    uneq = {j: [k for k in v['limited_quintiles'] if k != 1] for j, v in strat.items() if [k for k in v['limited_quintiles'] if k != 1]}
    log('g32_copernicus_draw.py draw', f'{YEAR} draw cop22 (equal quota per journal, cnp quintiles within journal)', len(out),
        f'frame {len(fr)}; {len(avail)} journals, quota {q}, seed {seed}; shortfall {short}; '
        f'quintiles limited by the frame (beyond q1): {uneq or "none"}')
    decision(f'Copernicus {YEAR} draw (set cop22), PI decision October 28: every journal has equal weight. Quota {q} papers per '
             f'journal (the smallest equal quota reaching {n}), all frame papers where a journal has fewer; within a journal, '
             f'equal numbers per impact quintile (cnp) as far as the frame allows (water filling), rings alternated within a '
             f'quintile; seed {seed}. {len(out)} papers from {len(avail)} journals (18 Copernicus with a public discussion, Nature '
             f'Communications and Communications Earth & Environment Earth articles with a peer review file). Short of the quota: '
             f'{short or "none"}. Replaces the same-day draw with a 12-per-journal cap and half per ring, which weighted '
             f'journals by size. No frame paper has cnp below 0.2 in the Copernicus journals, so quintile 1 is empty there.')
    print(len(out), 'drawn;', len(avail), 'journals; quota', q, '; shortfall', short)
    for j, v in strat.items():
        print(f"{j:7s} frame {v['frame']:4d} drawn {v['drawn']:3d} by quintile {v['drawn_by_quintile']} "
              f"(frame {v['frame_by_quintile']}) limited {v['limited_quintiles']}")
    print('rings', Counter(r['ring'] for r in out), 'quintiles', sorted(Counter(r['impact_quintile'] for r in out).items()))


# ---------------------------------------------------------------------------------------------------- prf
AUTHOR_RESPONSE = re.compile(r'(?i)response to (?:the )?reviewers?|point[- ]by[- ]point|we thank the reviewers?|'
                             r"authors?['’]? (?:response|reply)|rebuttal|our response")


def prf() -> None:
    """Peer review files of the drawn Nature Communications and CEE papers, into review/<key>/, with a located text."""
    import hashlib
    import subprocess
    from common import DATA
    pre = [r for r in read_json(SET / 'preselect.json') if r['journal_abbr'] in NATURE]
    index = []
    for r in sorted(pre, key=lambda r: r['id']):
        key = 'g22_' + r['id']
        d = DATA / 'review' / key
        cr = g28.crossref('works/' + urllib.parse.quote(r['doi'], safe='/'))
        pre_ids = sorted({x['id'] for x in cr.get('relation', {}).get('has-preprint', [])})
        rec = {'key': key, 'doi': r['doi'], 'journal': r['journal_abbr'], 'preprint_doi': pre_ids[0] if pre_ids else None,
               'peer_review_information': r.get('peer_review_information'), 'files': []}
        lines = [f'# Peer review file of {r["doi"]} ({r["journal"]})', '# Locator: [PRF<n> p.k] = page k of peer review file n.', '']
        for i, link in enumerate(r.get('prf_links') or [], 1):
            url = link['href']
            f = d / urllib.parse.unquote(url.rsplit('/', 1)[1])
            if not f.is_file():
                status, final, body = g28._request(url)
                g28._logfetch({'url': url, 'final_url': final, 'date': TODAY, 'status': status, 'bytes': len(body),
                               'sha256': hashlib.sha256(body).hexdigest(), 'file': rel(f) if body[:4] == b'%PDF' else None})
                if status != 200 or body[:4] != b'%PDF':
                    rec['files'].append({'url': url, 'status': status, 'error': 'not a PDF' if status == 200 else f'HTTP {status}'})
                    continue
                d.mkdir(parents=True, exist_ok=True)
                f.write_bytes(body)
            pages = subprocess.run(['pdftotext', '-layout', str(f), '-'], capture_output=True, text=True).stdout.split('\f')
            lines += [f'[PRF{i} p.{n}] ' + re.sub(r'\s+', ' ', pg).strip() for n, pg in enumerate(pages, 1) if pg.strip()]
            rec['files'].append({'url': url, 'file': rel(f), 'bytes': f.stat().st_size,
                                 'sha256': hashlib.sha256(f.read_bytes()).hexdigest(), 'pages': sum(1 for pg in pages if pg.strip())})
        ok = [x for x in rec['files'] if 'file' in x]
        if ok:
            (d / 'peer_review.txt').write_text('\n'.join(lines) + '\n')
            txt = '\n'.join(lines)
            rec.update(words=len(txt.split()), has_author_response=bool(AUTHOR_RESPONSE.search(txt)),
                       reviewer_mentions=len(set(re.findall(r'(?i)reviewer\s*#?\s*(\d)', txt))))
        rec['layers'] = {'review': bool(ok), 'author_response': rec.get('has_author_response', False),
                         'submitted_version': bool(rec['preprint_doi'])}
        rec['note'] = ('peer review file: referee reports and author responses; no discussion preprint, so no '
                       'submitted-version layer' + (' (a preprint is linked in Crossref)' if rec['preprint_doi'] else ''))
        index.append(rec)
        print(key, r['journal_abbr'], len(ok), 'files', rec.get('words'), 'words; AR', rec.get('has_author_response'),
              'preprint', rec['preprint_doi'], flush=True)
    write_json(NAT_INDEX, index, [rel(SET / 'preselect.json'), 'nature.com peer review files (static-content.springer.com)',
                                  'Crossref relation has-preprint'], {'pause_s': 2.0})
    got = [x for x in index if x['layers']['review']]
    log('g32_copernicus_draw.py prf', 'peer review files of the drawn Nature Communications and CEE papers', len(got),
        f"{len(index)} drawn; {sum(x['layers']['author_response'] for x in index)} with author responses detected; "
        f"{sum(bool(x['preprint_doi']) for x in index)} with a preprint in Crossref; web {dict(g28._n)}")


# ---------------------------------------------------------------------------------------------------- batches
def batches() -> None:
    recs = read_json(SET / 'screen_input.json')
    d = SET / 'screen_batches'
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob('batch_*.json'):
        old.unlink()
    for i in range(0, len(recs), 10):
        (d / f'batch_{i // 10:03d}.json').write_text(json.dumps(recs[i:i + 10], indent=1, ensure_ascii=False))
    nb = (len(recs) + 9) // 10
    log('g32_copernicus_draw.py batches', 'eligibility screen batches of 10 (cop22)', len(recs), f'{nb} batches')
    print(len(recs), 'records in', nb, 'batches;', rel(d))


# ---------------------------------------------------------------------------------------------------- report
PILOT = {'g22_W4205292752', 'g22_W4223595027'}   # advance pilot papers: their advance codings have been seen


def review_summary(path) -> dict:
    if not path.is_file():
        return {'index': rel(path), 'missing': True}
    idx = read_json(path)
    ok = [r for r in idx if 'comments' in r]
    has = lambda r, k: any(re.search(rf'-{k}\d*\.pdf$', f) for f in r.get('files', []))
    return {'index': rel(path), 'papers': len(idx), 'with_page': len(ok),
            'no_open_discussion': sum(1 for r in idx if r.get('no_open_discussion')),
            'errors': {r['key']: r['error'] for r in idx if 'error' in r},
            'AR': sum(has(r, 'AR') for r in ok), 'ATC': sum(has(r, 'ATC') for r in ok),
            'RC': sum(r['comments'].get('RC', 0) for r in ok), 'AC': sum(r['comments'].get('AC', 0) for r in ok),
            'manuscript_versions': sum(bool(r.get('manuscript_versions')) for r in ok),
            'pilot_papers': sorted(PILOT & {r['key'] for r in idx})}


def report() -> None:
    fr_all = read_json(SET / 'frame.json')
    fp = json.loads((SET / 'frame.json').read_text())['_provenance']['params']
    fr = [r for r in fr_all if 'excluded' not in r]
    pre = read_json(SET / 'preselect.json')
    dp = json.loads((SET / 'preselect.json').read_text())['_provenance']['params']
    av = read_json(SET / 'availability.json')
    opt = lambda f: read_json(f) if f.is_file() else None
    si, met = opt(SET / 'screen_input.json'), opt(SET / 'metrics.json')
    xml = opt(DERIVED / 'cop22calc' / 'xml_status.json')
    nat = opt(NAT_INDEX)
    pf = {k: opt(DERIVED / 'translation' / f) for k, f in (('cop22', 'preprint_fetch_cop22.json'), ('r2', 'preprint_fetch_r2.json'))}
    rv = {'cop22': review_summary(COP_INDEX), 'r2': review_summary(R2_INDEX)}
    S = {'flow_copernicus': fp['flow'], 'flow_nature': fp['flow_nature'], 'frame': len(fr),
         'frame_in_pool': sum(r['in_pool'] for r in fr), 'drawn': len(pre), 'journal_quota': dp['journal_quota'],
         'shortfall': dp['shortfall'], 'strata': dp['strata'],
         'drawn_rings': dict(Counter(r['ring'] for r in pre)),
         'drawn_quintiles': {k: v for k, v in sorted(Counter(r['impact_quintile'] for r in pre).items())},
         'availability': {k: v for k, v in av.items() if k != 'frame_sample'} | {'frame_sample': {k: v for k, v in av['frame_sample'].items() if k != 'papers'}},
         'screen_input': None if si is None else {'records': len(si), 'no_abstract': sum(1 for r in si if not r['abstract'])},
         'metrics': None if met is None else {'rows': len(met), 'novelty_missing': sum(m['novelty_pair'] is None for m in met),
                                              'breadth_citers_missing': sum(m['breadth_citers'] is None for m in met)},
         'xml': None if xml is None else {'papers': len(xml), 'with_xml': sum(r['xml'] for r in xml),
                                          'by_route': dict(Counter(r['route'] for r in xml if r['xml'])),
                                          'failed': {r['key']: r['tried'] for r in xml if not r['xml']}},
         'review': rv,
         'peer_review_files': None if nat is None else {
             'papers': len(nat), 'with_file': sum(x['layers']['review'] for x in nat),
             'author_response_detected': sum(x['layers']['author_response'] for x in nat),
             'preprint_in_crossref': sum(bool(x['preprint_doi']) for x in nat),
             'failed': {x['key']: x['files'] for x in nat if not x['layers']['review']}},
         'preprints': {k: None if v is None else dict(Counter(r['status'] if not r['status'].startswith('error') else 'error' for r in v))
                       for k, v in pf.items()}}
    write_json(SET / 'draw_report.json', S, [rel(SET / f) for f in ('frame.json', 'preselect.json', 'availability.json',
               'screen_input.json', 'metrics.json')] + [rel(COP_INDEX), rel(R2_INDEX), rel(NAT_INDEX),
               'derived/cop22calc/xml_status.json', 'derived/translation/preprint_fetch_{cop22,r2}.json'])
    md = [f'# Open-review {YEAR} draw (set cop22)', '',
          f'Built by `tools/roadmap/g32_copernicus_draw.py report` on {TODAY}. Rules in the script docstring; numbers from '
          'the files named in derived/cop22/draw_report.json.', '', '## Frame', '', '| Step | Papers left |', '|:--|--:|']
    md += [f'| {a} | {b} |' for a, b in S['flow_copernicus'] + S['flow_nature']]
    md += ['', f"{S['frame_in_pool']} of the {S['frame']} frame papers are also in the g02 pool.", '', '## Draw', '',
           f"{S['drawn']} papers, seed {dp['seed']}, equal quota {S['journal_quota']} per journal ({dp['journals']} journals). "
           f"Short of the quota: {S['shortfall'] or 'none'}. Rings {S['drawn_rings']}; impact quintiles {S['drawn_quintiles']}.", '',
           '| Journal | Frame | Drawn | Short | Frame by quintile 1-5 | Drawn by quintile 1-5 | Quintiles limited by the frame |',
           '|:--|--:|--:|--:|:--|:--|:--|']
    for j, v in S['strata'].items():
        fq = ' '.join(str(v['frame_by_quintile'][str(k)] if str(k) in v['frame_by_quintile'] else v['frame_by_quintile'][k]) for k in range(1, 6))
        dq = ' '.join(str(v['drawn_by_quintile'][str(k)] if str(k) in v['drawn_by_quintile'] else v['drawn_by_quintile'][k]) for k in range(1, 6))
        md.append(f"| {j} | {v['frame']} | {v['drawn']} | {v['shortfall']} | {fq} | {dq} | {v['limited_quintiles']} |")
    a = S['availability']
    md += ['', '## Author response (AR) and tracked changes (ATC)', '', '| Source | Discussion pages | With AR | With ATC |', '|:--|--:|--:|--:|']
    md += [f"| g28 era check {y} | {v['pages']} | {v['AR']} | {v['ATC']} |" for y, v in a['era_check'].items()]
    md += [f"| Round-1 records (g15, 2022) | {a['round1_records']['pages']} | {a['round1_records']['AR']} | {a['round1_records']['ATC']} |",
           f"| Frame sample, one per Copernicus journal | {a['frame_sample']['pages']} | {a['frame_sample']['AR']} | {a['frame_sample']['ATC']} |"]
    for k, v in rv.items():
        if not v.get('missing'):
            md.append(f"| {k} Copernicus records (g15) | {v['with_page']} | {v['AR']} | {v['ATC']} |")
    if S['peer_review_files']:
        p = S['peer_review_files']
        md.append(f"| NC and CEE peer review files (prf) | {p['with_file']} of {p['papers']} | {p['author_response_detected']} | n/a |")
    md += ['', '## Downstream inputs', '']
    md += [f'- screen input: {S["screen_input"]}', f'- metrics: {S["metrics"]}',
           f'- XML: {None if xml is None else {k: v for k, v in S["xml"].items() if k != "failed"}}; failed {list((S["xml"] or {}).get("failed", {}))}',
           '- review records: ' + '; '.join(f"{k}: {v.get('with_page')} of {v.get('papers')} with a discussion page, "
                                            f"{len(v.get('errors', {}))} errors, pilot papers {v.get('pilot_papers')}" for k, v in rv.items()),
           f'- peer review files: {S["peer_review_files"]}',
           f'- discussion preprints: {S["preprints"]}']
    (SET / 'DRAW.md').write_text('\n'.join(md) + '\n')
    log('g32_copernicus_draw.py report', 'open-review 2022 draw report (counts per step, journals, AR/ATC)', len(pre),
        f"frame {S['frame']}; quota {S['journal_quota']}; review pages cop22 {rv['cop22'].get('with_page')}, r2 {rv['r2'].get('with_page')}")
    print('\n'.join(md))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['frame', 'check', 'draw', 'prf', 'batches', 'report'])
    ap.add_argument('--n', type=int, default=N)
    ap.add_argument('--seed', type=int, default=SEED)
    a = ap.parse_args()
    if a.cmd == 'frame':
        frame()
    elif a.cmd == 'check':
        check()
    elif a.cmd == 'draw':
        draw(a.n, a.seed)
    elif a.cmd == 'prf':
        prf()
    elif a.cmd == 'batches':
        batches()
    else:
        report()


if __name__ == '__main__':
    main()
