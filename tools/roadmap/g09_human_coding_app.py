#!/usr/bin/env python3
"""Gold set, step 9: the human coding subset, its assignment to coders, and the offline coding app.

Input : derived/gold/gold_set.json (g05); derived/gold/fetch_status.json (g08) when present;
        agents/coder/coding.schema.json, agents/coder/ratings.schema.json, agents/coder/CODEBOOK.md (version),
        agents/mode-instructions.json (mode purposes), agents/controller/decision-tree.json (questions);
        tools/roadmap/app/gold_coder.html (template, no data)
Output: derived/gold/human_assignment.json   the 40 papers, each assigned to two of the four coders, and each coder's order
        private/data/roadmap/app/gold-coder.html   the app with that data embedded (opens from disk; works offline)
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
from common import DATA, DERIVED, ROOT, TODAY, commit, decision, log, read_json, write_json

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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--seed', type=int, default=2026)
    a = ap.parse_args()
    rng = random.Random(a.seed)
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
    if extra:
        for a_, b_ in itertools.combinations(range(len(pairs)), 2):
            if not set(pairs[a_]) & set(pairs[b_]) and len(pairs) - extra == 2:
                short = [pairs[a_], pairs[b_]]
                pairs = [p for p in pairs if p not in short] + short
                break
    rng.shuffle(picked)
    papers = []
    for i, g in enumerate(picked):
        papers.append({'key': g['key'], 'doi': g['doi'], 'title': g['title'], 'journal': g['journal'], 'year': 2022,
                       'ring': g['ring'], 'pdf': f"../pdfs/gold/{g['key']}.pdf", 'pdf_in_hand': g['key'] in fetched,
                       'xml_txt': f"../pdfs/gold/{g['key']}.xml.txt" if (DATA / 'pdfs' / 'gold' / f"{g['key']}.xml.txt").is_file() else None,
                       'assigned': list(pairs[i % len(pairs)])})
    order = {}
    for c, _ in CODERS:
        mine = [p['key'] for p in papers if c in p['assigned']]
        rng.shuffle(mine)
        order[c] = mine
    write_json(DERIVED / 'gold' / 'human_assignment.json', {'coders': CODERS, 'papers': papers, 'order': order},
               ['derived/gold/gold_set.json', 'derived/gold/fetch_status.json' if fs_path.is_file() else 'no fetch status yet'],
               {'n': a.n, 'seed': a.seed})

    cb_version = re.search(r'^version:\s*(\S+)', (ROOT / 'agents/coder/CODEBOOK.md').read_text(), re.M).group(1)
    modes = [{'id': m['id'], 'title': m['title'], 'purpose': m['sections'].get('Epistemic purpose', '').lstrip('- ').strip()}
             for m in json.loads((ROOT / 'agents/mode-instructions.json').read_text())['modes']]
    tree = json.loads((ROOT / 'agents/controller/decision-tree.json').read_text())
    questions = [{'n': q['n'], 'q': q['q'], 'sub': q.get('sub', '')} for q in tree['questions']]
    if not any(q['n'] == '6b' for q in questions):
        questions.insert(next(i for i, q in enumerate(questions) if q['n'] == '7'), {'n': '6b', 'q': 'Does nature repeat?', 'sub': 'Conditions found, not set: are there repeated natural instances?'})
    payload = {
        'meta': {'built': TODAY, 'commit': commit(), 'codebook_version': cb_version, 'ratings_version': '1.0.0',
                 'graph': 'v0.4.2', 'tree': tree.get('version'), 'assignment_seed': a.seed},
        'coders': [{'id': c, 'name': n} for c, n in CODERS], 'papers': papers, 'order': order,
        'nodes': [{'id': i, 'verb': v, 'desc': d, 'group': g} for i, v, d, g in NODES],
        'modes': modes, 'questions': questions,
        'schema': json.loads((ROOT / 'agents/coder/coding.schema.json').read_text()),
        'ratings_schema': json.loads((ROOT / 'agents/coder/ratings.schema.json').read_text()),
    }
    tpl = (ROOT / 'tools/roadmap/app/gold_coder.html').read_text()
    blob = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')
    out = DATA / 'app' / 'gold-coder.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl.replace('/*__DATA__*/null', blob))
    log('g09_human_coding_app.py', 'human coding subset, assignment, offline app', len(papers),
        f"{sum(p['pdf_in_hand'] for p in papers)} with PDF in hand; app {out.relative_to(ROOT)}")
    decision(f'Human gold set: {len(papers)} of the 100 gold papers ({a.n // 2} per ring, spread over impact tiers, PDFs in hand first), '
             f'each coded independently by two of {", ".join(n for _, n in CODERS)} (six pairs in rotation; 20 papers per coder); '
             f'seed {a.seed}. Coders see no metrics; they code with codebook v{cb_version} and rate novelty and advance blind '
             '(ratings v1.0.0, Novelty Dossier v1 and Scientific Advance Profile v1).')
    print(len(papers), 'papers;', {c: len(v) for c, v in order.items()}, 'per coder;', out)


if __name__ == '__main__':
    main()
