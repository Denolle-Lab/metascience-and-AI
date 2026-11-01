"""Check g11's Krippendorff alpha against the reliability run (private/analysis/reliability: node-presence alpha 0.63).
Run: python tools/roadmap/test_g11_alpha.py"""
import glob
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g11_human_agreement import alpha_nominal, alpha_ordinal, NODES  # noqa: E402

base = os.path.join(os.environ.get('METASCIENCE_PRIVATE') or os.path.join(os.path.dirname(__file__), '..', '..', 'private'),
                    'analysis', 'reliability', 'codings', 'papers')
A = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(base + '/opus-b/*.json')}
B = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(base + '/sonnet-c/*.json')}
fp = lambda c: next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps']
units = [[n in {s['node'] for s in fp(c)} for c in (A[k], B[k])] for k in A if k in B for n in NODES]
a = alpha_nominal(units)
assert a is not None and abs(a - 0.634) < 0.002, a
assert alpha_nominal([[1, 1], [2, 2], [3, 3]]) == 1.0
assert alpha_ordinal([[1, 1], [5, 5], [3, 3]]) == 1.0
print('ok: node-presence alpha', a, '(reliability run: 0.63)')
