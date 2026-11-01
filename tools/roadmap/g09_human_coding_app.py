#!/usr/bin/env python3
"""Gold set, step 9: the human coding subset, its assignment to coders, and the offline coding app.

Input : derived/gold/gold_set.json (g05); derived/gold/fetch_status.json (g08) when present;
        agents/coder/coding.schema.json, agents/coder/ratings.schema.json (ratings v1.1.0), agents/coder/CODEBOOK.md (version),
        agents/coder/definitions.json (terms, hard cases, rating notes),
        agents/mode-instructions.json (mode purposes), agents/controller/decision-tree.json (questions);
        tools/roadmap/app/gold_coder.html (template, no data)
Output: derived/gold/human_assignment.json   the 40 papers, each assigned to two of the four coders, and each coder's order;
                                             written once and then frozen (rerun with --reassign only before coding starts)
        private/data/roadmap/app/packets/<ID>/     one packet per coder: gold-coder.html locked to that coder, only their papers,
                                             pdfs/ and text/ (located XML text), an empty my_codings/, README.txt. No metrics,
                                             no pairings, no comparison view, and no journal name: the coder payload carries no
                                             journal and the app shows neither journal nor DOI (the DOI stays in the payload only
                                             because both output schemas require it). The PDFs still show the venue; the README
                                             and the app say so and ask coders not to look papers up. Share each packet with its
                                             coder only.
        private/data/roadmap/app/gold-coordinator.html  the comparison view, for the convenor
Rule  : 40 of the 100 gold papers, 20 per ring, spread over impact tiers within a ring; papers whose PDF is in hand first;
        each paper to one of the six coder pairs in rotation, so every coder codes 20 papers and every pair shares 6 or 7;
        each coder's order shuffled. Metrics (impact, novelty, breadth tiers) are not embedded, so coders rate blind.
Run   : python tools/roadmap/g09_human_coding_app.py [--n 40] [--seed 2026]
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
import re
from collections import defaultdict
import hashlib
import shutil
from common import DATA, DERIVED, ROOT, TODAY, commit, decision, log, read_json, write_json

RATINGS_VERSION = '1.1.0'  # agents/coder/ratings.schema.json; adds the advance verdict, its criteria and the unassessable condition

CODERS = [('MD', 'Marine Denolle'), ('SH', 'Sangwoo Han'), ('MK', 'Maleen Kidiwela'), ('MH', 'Michael Hemmett')]
NODES = [
    ('N', 'New capability', 'Build or characterize an instrument or method', 'build'),
    ('E', 'Explore', 'Establish the phenomenon: does it repeat; is it the chain or the world', 'build'),
    ('O', 'Observe', 'Make or gather the observations', 'build'),
    ('I', 'Infer', 'Estimate a latent quantity through a forward model (inversion, fitting)', 'build'),
    ('Q', 'Question', 'Pose the question or name the anomaly', 'test'),
    ('H', 'Hypothesize', 'Generate rival explanations, keeping "artifact" as one', 'test'),
    ('S', 'Simulate', 'Simulate or derive what each rival predicts', 'test'),
    ('D', 'Design', 'Design the test: the observable where the expectations differ', 'test'),
    ('F', 'Find', 'Find or set the conditions (trace, live event, or experiment)', 'test'),
    ('C', 'Compare', 'Compare observation with expectation', 'test'),
    ('V', 'Vary', 'Vary and replicate: controls, independent data, robustness, premise checks', 'test'),
    ('X', 'eXclude', 'Exclude a rival', 'decide'),
    ('K', 'Keep', 'Keep the claim, with a status', 'decide'),
    ('P', 'Protect', 'Protect: revise an auxiliary instead of the hypothesis', 'decide'),
    ('R', 'Refine', 'Refine the surviving claim into subhypotheses', 'decide'),
]


README = """Gold-set coding packet for {name} ({id})

1. Open gold-coder.html in Chrome or Edge (double-click; it runs offline and sends nothing anywhere).
2. Your {n} papers are listed in the order to code them. Each has its PDF in pdfs/ and, when the publisher
   provides XML, a located text in text/ whose paragraphs carry locators such as [§3.2 ¶4] you can cite.
3. When you first save, choose this packet's my_codings folder. Each paper is saved as two files:
   <key>.{id}.coding.json and <key>.{id}.ratings.json. Unfinished saves are named .draft.
4. The app hides each paper's journal and DOI, but the PDFs show them. Judge the work, not the venue: prestige
   is not evidence. Rate novelty and advance without looking the paper up online (publisher page, Google Scholar,
   the authors' pages): those pages show the venue's standing and citation counts.
   Do not discuss a paper with anyone until you have saved it.
5. Ratings v{rv} add the advance verdict (achieved, not demonstrated, unassessable) with six criteria (M1, M2,
   W1 to W4) and the unassessable conditions (U1 to U5), as the model coder uses them. Definitions are under each
   control and in the Codebook drawer.
6. Back up your drafts from the My papers page now and then, and send the my_codings folder to Marine when you
   finish a batch. The PDFs are for this study only; do not redistribute them.

Codebook v{cb}; ratings v{rv}; built {built} from commit {commit}.
"""


def load_vocab(a, cb_version):
    modes = [{'id': m['id'], 'title': m['title'], 'purpose': m['sections'].get('Epistemic purpose', '').lstrip('- ').strip()}
             for m in json.loads((ROOT / 'agents/mode-instructions.json').read_text())['modes']]
    tree = json.loads((ROOT / 'agents/controller/decision-tree.json').read_text())
    questions = [{'n': q['n'], 'q': q['q'], 'sub': q.get('sub', '')} for q in tree['questions']]
    if not any(q['n'] == '6b' for q in questions):
        questions.insert(next(i for i, q in enumerate(questions) if q['n'] == '7'), {'n': '6b', 'q': 'Does nature repeat?', 'sub': 'Conditions found, not set: are there repeated natural instances?'})
    defs = json.loads((ROOT / 'agents/coder/definitions.json').read_text())
    rs = json.loads((ROOT / 'agents/coder/ratings.schema.json').read_text())
    assert RATINGS_VERSION in rs['properties']['ratings_version']['enum'], 'ratings.schema.json does not know ratings v' + RATINGS_VERSION
    return {'meta': {'built': TODAY, 'commit': commit(), 'codebook_version': cb_version, 'ratings_version': RATINGS_VERSION,
                     'graph': 'v0.4.2', 'tree': tree.get('version'), 'assignment_seed': a.seed},
            'coders': [{'id': c, 'name': n} for c, n in CODERS],
            'nodes': [{'id': i, 'verb': v, 'desc': d, 'group': g} for i, v, d, g in NODES],
            'modes': modes, 'questions': questions, 'definitions': defs['terms'], 'hard_cases': defs['hard_cases'],
            'rating_notes': defs.get('rating_notes', []),
            'schema': json.loads((ROOT / 'agents/coder/coding.schema.json').read_text()),
            'ratings_schema': rs}


def assign(a, rng):
    gold = read_json(DERIVED / 'gold' / 'gold_set.json')
    fs_path = DERIVED / 'gold' / 'fetch_status.json'
    fetched = {r['key'] for r in read_json(fs_path) if r['fetched']} if fs_path.is_file() else set()
    picked = []
    for ring in ('core', 'broad'):
        per_ring = a.n // 2
        by_tier = defaultdict(list)
        for g in sorted((g for g in gold if g['ring'] == ring), key=lambda g: g['key']):
            by_tier[g['impact_tier']].append(g)
        for t in by_tier.values():
            rng.shuffle(t)
            t.sort(key=lambda g: g['key'] not in fetched)  # stable: fetched first, random within
        tiers = sorted(by_tier)
        while sum(1 for p in picked if p['ring'] == ring) < per_ring and any(by_tier.values()):
            for t in tiers:
                if by_tier[t] and sum(1 for p in picked if p['ring'] == ring) < per_ring:
                    picked.append(by_tier[t].pop(0))
    pairs = list(itertools.combinations([c for c, _ in CODERS], 2))
    rng.shuffle(pairs)
    # 40 papers over 6 pairs = four pairs of 7 and two of 6; the two short pairs must share no coder, so every coder gets 20
    extra = len(picked) % len(pairs)
    if extra and len(pairs) - extra == 2:
        for a_, b_ in itertools.combinations(range(len(pairs)), 2):
            if not set(pairs[a_]) & set(pairs[b_]):
                short = [pairs[a_], pairs[b_]]
                pairs = [p for p in pairs if p not in short] + short
                break
    rng.shuffle(picked)
    papers = [{'key': g['key'], 'doi': g['doi'], 'title': g['title'], 'journal': g['journal'], 'ring': g['ring'],
               'assigned': list(pairs[i % len(pairs)])} for i, g in enumerate(picked)]
    order = {}
    for c, _ in CODERS:
        mine = [p['key'] for p in papers if c in p['assigned']]
        rng.shuffle(mine)
        order[c] = mine
    write_json(DERIVED / 'gold' / 'human_assignment.json', {'coders': CODERS, 'papers': papers, 'order': order},
               ['derived/gold/gold_set.json', 'derived/gold/fetch_status.json' if fs_path.is_file() else 'no fetch status yet'],
               {'n': a.n, 'seed': a.seed})
    decision(f'Human gold set assignment written (frozen from now on): {len(papers)} of the 100 gold papers ({a.n // 2} per ring, spread '
             f'over impact tiers, papers with a PDF in hand first), each coded independently by two of {", ".join(n for _, n in CODERS)} '
             f'(six pairs; 20 papers per coder); seed {a.seed}. Rebuilding the app no longer changes it; --reassign is for use only before coding starts.')
    return papers, order


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--reassign', action='store_true', help='redraw the assignment (only before any coder has started)')
    a = ap.parse_args()
    rng = random.Random(a.seed)
    ha = DERIVED / 'gold' / 'human_assignment.json'
    if ha.is_file() and not a.reassign:
        d = read_json(ha)
        papers, order = d['papers'], d['order']
    else:
        papers, order = assign(a, rng)
    cb_version = re.search(r'^version:\s*(\S+)', (ROOT / 'agents/coder/CODEBOOK.md').read_text(), re.M).group(1)
    base = load_vocab(a, cb_version)
    src = DATA / 'pdfs' / 'gold'
    tag = hashlib.sha1(json.dumps(order, sort_keys=True).encode()).hexdigest()[:8]
    tpl = (ROOT / 'tools/roadmap/app/gold_coder.html').read_text()
    put = lambda payload: tpl.replace('/*__DATA__*/null', json.dumps(payload, ensure_ascii=False).replace('</', '<\\/'))
    app_dir = DATA / 'app'
    old = app_dir / 'gold-coder.html'
    if old.is_file():
        old.unlink()  # the single shared build is replaced by per-coder packets
    counts = {}
    for cid, name in CODERS:
        pk = app_dir / 'packets' / cid
        for sub in ('pdfs', 'text', 'my_codings'):
            (pk / sub).mkdir(parents=True, exist_ok=True)
        mine = []
        for k in order[cid]:
            p = next(x for x in papers if x['key'] == k)
            has_pdf, has_txt = (src / f'{k}.pdf').is_file(), (src / f'{k}.xml.txt').is_file()
            if has_pdf:
                shutil.copy2(src / f'{k}.pdf', pk / 'pdfs' / f'{k}.pdf')
            if has_txt:
                shutil.copy2(src / f'{k}.xml.txt', pk / 'text' / f'{k}.xml.txt')
            mine.append({'key': k, 'doi': p['doi'], 'title': p['title'],  # no journal: coders rate without the venue in the app
                         'pdf': f'pdfs/{k}.pdf' if has_pdf else None, 'xml_txt': f'text/{k}.xml.txt' if has_txt else None})
        payload = dict(base, mode='coder', coder=cid, papers=mine, order=order[cid])
        payload['meta'] = dict(base['meta'], packet=f'{cid}-{tag}')
        (pk / 'gold-coder.html').write_text(put(payload))
        (pk / 'README.txt').write_text(README.format(name=name, id=cid, n=len(mine), cb=cb_version, rv=RATINGS_VERSION, built=TODAY, commit=base['meta']['commit']))
        counts[cid] = (len(mine), sum(1 for m in mine if m['pdf']), sum(1 for m in mine if m['xml_txt']))
    coord = dict(base, mode='coordinator', coder=None, order=[], papers=[{'key': p['key'], 'title': p['title'], 'doi': p['doi'], 'journal': p['journal']} for p in papers])
    coord['meta'] = dict(base['meta'], packet=f'coord-{tag}')
    (app_dir / 'gold-coordinator.html').write_text(put(coord))
    log('g09_human_coding_app.py', 'coder packets and coordinator build', len(papers),
        '; '.join(f'{c}: {n} papers, {p} PDFs, {t} located texts' for c, (n, p, t) in counts.items()))
    print(len(papers), 'papers;', counts, '-> packets in', app_dir / 'packets')


if __name__ == '__main__':
    main()
