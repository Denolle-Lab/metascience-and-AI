"""Round bookkeeping shared by g13, g17, g19 and g21: which codings belong to which round, and which round-1 codings
were in the first analysis.

Rounds (the 2022 candidate pool is shared; derived/gold/pool.json)
  round 1   coding tag calc1, metrics derived/gold/metrics.json (600 preselected, stratified to equal cnp quintiles),
            eligible papers derived/calc1/manifest.jsonl (525). Exploratory.
  round 2   coding tag r2, metrics derived/r2/metrics.json (open access only, at most 4 papers per journal, equal cnp
            quintiles per ring; g18_round2_draw.py), eligible papers derived/r2calc/manifest.jsonl (222). Confirmatory for
            the 43 associations frozen in preregistration/round2-confirmatory.json (public commit b4369fe).
  pooled    both rounds together, with round kept as a stratum.
Valid coding: passes tools/check_coding.py validate(). g17 also requires a row in the round's metrics.json.

Round-1 split
  first analysis  the 233 valid calc1 codings the round-1 exploratory analysis and the freeze used (E1 batches submitted
                  on October 25, 2026, plus one synchronous run).
  top-up          valid calc1 codings whose state.json record 'calc1:<key>' names a calc1 batch submitted on or after
                  TOPUP_FROM (the top-up batch of October 27 and its retries); 141 papers on October 27.
  The split is read from private/analysis/codings/api/state.json; it matches the valid calc1 codings at private commit
  abf4cf7 (233, unchanged since).
"""
from __future__ import annotations
import json
from common import PRIVATE, DERIVED, read_json
from check_coding import validate

API = PRIVATE / 'analysis' / 'codings' / 'api'
ROUNDS = [  # name, coding tag, metrics set, manifest folder
    ('round1', 'calc1', 'gold', 'calc1'),
    ('round2', 'r2', 'r2', 'r2calc'),
]
TOPUP_FROM = '2026-10-26'


def metrics(set_name: str) -> dict:
    return {'g22_' + m['id']: m for m in read_json(DERIVED / set_name / 'metrics.json')}


def manifest(folder: str) -> list[dict]:
    p = DERIVED / folder / 'manifest.jsonl'
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.is_file() else []


def valid(tag: str, keep=None) -> dict:
    """{key: coding} for codings of a tag that pass validate(); keep = optional set of keys to restrict to."""
    out = {}
    folder = API / tag
    for f in sorted(folder.glob('*.json')) if folder.is_dir() else []:
        try:
            c = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            continue
        if not validate(c) and (keep is None or c['key'] in keep):
            out[c['key']] = c
    return out


def round1_split(keys) -> tuple[set, set]:
    """(first-analysis keys, top-up keys) among the given valid calc1 keys."""
    state = json.loads((API / 'state.json').read_text())
    late = {b['id'] for b in state['batches'] if b['tag'] == 'calc1' and b['submitted'] >= TOPUP_FROM}
    top = {k for k in keys if (state['done'].get(f'calc1:{k}') or {}).get('batch') in late}
    return set(keys) - top, top


def quintile(cnp):
    """Impact quintile as g03/g18 assign it: min(4, int(cnp * 5)) + 1; None when cnp is missing."""
    return None if cnp is None else min(4, int(cnp * 5)) + 1
