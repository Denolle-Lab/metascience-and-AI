"""Phase 2b: how much of the review-process work shows in the published paper.

  prep     one input packet per paper: the numbered changes of the review sequence (calc1-review codings),
           with paths to the published text (publisher XML, located) and the open review record
  analyze  read the visibility labels (two independent labelers per change, adjudicated where they differ),
           check every quote against the published text, and report the shares

Labels, per review change:
  as_revision   the published paper shows the change and says it was revised, added, or prompted by review
  as_planned    the published paper shows the change but presents it as part of the original design
  absent        the published paper does not show the change
  no_change     the review step records no change to the work (a declined request, a reply that only argues)

Run:  python tools/roadmap/g16_visibility.py prep
      (workflow tools/roadmap/workflows/visibility.js writes labels to derived/review/visibility_labels.json)
      python tools/roadmap/g16_visibility.py analyze
"""
import json, re, sys, random
from collections import Counter
from pathlib import Path
from common import ROOT, DATA, DERIVED, write_json, log

CODED = ROOT / 'private' / 'analysis' / 'codings' / 'api' / 'calc1-review'
QUEUE = ROOT / 'private' / 'download-queue.json'
PACK = DERIVED / 'review' / 'visibility_input'
LABELS = DERIVED / 'review' / 'visibility_labels.json'
CATS = ['as_revision', 'as_planned', 'absent', 'no_change']


def norm(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', (s or '').lower())).strip()


def prep():
    q = json.loads(QUEUE.read_text())
    PACK.mkdir(parents=True, exist_ok=True)
    made = 0
    for f in sorted(CODED.glob('*.json')):
        c = json.loads(f.read_text())
        rev = next((s for s in c['sequences'] if s['kind'] == 'review'), None)
        if not rev or not rev['steps']:
            continue
        pdf = Path(q[c['key']]['file'])
        pdf = pdf if pdf.is_absolute() else ROOT / pdf
        final = pdf.with_suffix('.xml.txt')
        steps = [{'i': i, **{k: s.get(k) for k in ['node', 'mode', 'action', 'page', 'quote', 'move', 'trigger']}} for i, s in enumerate(rev['steps'], 1)]
        pack = {'key': c['key'], 'doi': c['doi'], 'final_text': str(final), 'review_record': str(DATA / 'review' / c['key'] / 'discussion.txt'),
                'final_paper_steps': len(next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps']), 'review_steps': steps}
        (PACK / f"{c['key']}.json").write_text(json.dumps(pack, indent=1, ensure_ascii=False))
        made += 1
    log('g16_visibility.py prep', 'visibility input packets', made)
    print(made, 'packets in', PACK)


def analyze():
    lab = json.loads(LABELS.read_text())
    lab = lab.get('data', lab)
    rows, quote_ok, quote_n = [], 0, 0
    texts = {}
    for p in lab:
        pack = json.loads((PACK / f"{p['key']}.json").read_text())
        if p['key'] not in texts:
            texts[p['key']] = norm(Path(pack['final_text']).read_text())
        meta = {r['i']: r for r in pack['review_steps']}
        for s in p['steps']:
            m = meta.get(s['i'], {})
            rows.append({'key': p['key'], 'label': s['label'], 'agreed': s['agreed'],
                         'move': s.get('move') or m.get('move'), 'node': s.get('node') or m.get('node')})
            if s['label'] in ('as_revision', 'as_planned') and s.get('quote'):
                quote_n += 1
                quote_ok += norm(s['quote']) in texts[p['key']]
    n = len(rows)
    ch = [r for r in rows if r['label'] != 'no_change']
    papers = sorted({r['key'] for r in rows})
    per = []
    for k in papers:
        rr = [r for r in ch if r['key'] == k]
        if rr:
            per.append(sum(r['label'] != 'as_revision' for r in rr) / len(rr))
    rng = random.Random(2026)
    bs = sorted(sum(per[rng.randrange(len(per))] for _ in per) / len(per) for _ in range(2000))
    res = {'papers': len(papers), 'review_steps': n, 'changes': len(ch),
           'label_share_of_changes': {c: round(sum(r['label'] == c for r in ch) / max(len(ch), 1), 2) for c in CATS[:3]},
           'no_change_steps': sum(r['label'] == 'no_change' for r in rows),
           'hidden_share_per_paper_mean': [round(sum(per) / len(per), 2), round(bs[50], 2), round(bs[1949], 2)],
           'labeler_agreement': round(sum(r['agreed'] for r in rows) / max(n, 1), 2),
           'quotes_found_in_published_text': [quote_ok, quote_n],
           'by_node_absent_share': {k: round(v[1] / v[0], 2) for k, v in
                                    {nd: (sum(1 for r in ch if r['node'] == nd), sum(1 for r in ch if r['node'] == nd and r['label'] == 'absent'))
                                     for nd in sorted({r['node'] for r in ch if r['node']})}.items() if v[0] >= 5},
           'note': 'hidden = a change shown as planned or absent, i.e. not readable as a revision; interval is a 95% bootstrap over papers'}
    write_json(DERIVED / 'review' / 'visibility_results.json', res, ['derived/review/visibility_labels.json', 'derived/review/visibility_input'])
    log('g16_visibility.py analyze', 'visibility of review-process work in published papers', len(papers), f'{len(ch)} changes')
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    {'prep': prep, 'analyze': analyze}[sys.argv[1]]()
