#!/usr/bin/env python3
"""Export authoritative mode pages as versioned agent-readable instructions.

Run after changing modes/*.qmd. --check verifies the checked-in export; it does
not execute an agent or establish that a proposed procedure works.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'agents' / 'mode-instructions.json'
SECTIONS = ('Epistemic purpose', 'When this mode helps',
            'Agent actions and representations', 'Evidence and claim scope',
            'Transitions and stopping', 'Characteristic failure',
            'Human evidence and borrowing', 'Evaluation against past work')


def collect() -> dict:
    modes = []
    ids = set()
    for path in sorted((ROOT / 'modes').glob('*.qmd')):
        raw = path.read_text()
        match = re.match(r'\A---\n(.*?)\n---\n(.*)\Z', raw, re.S)
        if not match:
            raise ValueError(f'{path.name}: missing mode metadata')
        meta = yaml.safe_load(match[1])
        mid = meta.get('mode_id')
        if mid != path.stem or mid in ids:
            raise ValueError(f'{path.name}: duplicate or mismatched mode ID')
        if not isinstance(meta.get('mode_version'), str) or not re.fullmatch(r'\d+\.\d+\.\d+', meta['mode_version']):
            raise ValueError(f'{path.name}: expected semantic mode_version string')
        if meta.get('mode_status') not in ('drafted', 'discussed', 'adopted'):
            raise ValueError(f'{path.name}: invalid mode status')
        ids.add(mid)
        title = re.search(r'^# (.*?) \{\.unnumbered\}$', match[2], re.M)
        if not title:
            raise ValueError(f'{path.name}: missing title')
        chunks = re.split(r'^## (.+)\n', match[2], flags=re.M)
        sections = dict(zip(chunks[1::2], (v.strip() for v in chunks[2::2])))
        if any(not sections.get(section) for section in SECTIONS):
            raise ValueError(f'{path.name}: missing a required specification section')
        modes.append({'id': mid, 'version': meta['mode_version'], 'status': meta['mode_status'],
                      'title': title[1], 'source': path.relative_to(ROOT).as_posix(),
                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'sections': sections})
    if not modes:
        raise ValueError('No mode specifications found')
    return {'schema_version': '1.0',
            'purpose': 'Human-editable epistemic modes for pursuing warranted scientific advance. Procedures are design hypotheses, not evaluated capabilities.',
            'source_policy': 'Edit modes/*.qmd and regenerate. Links are relative to each source; citation keys resolve in references.bib. Preserve version and hash with every agent run.',
            'modes': modes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        rendered = json.dumps(collect(), indent=2, ensure_ascii=False) + '\n'
    except (ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != rendered:
            print('FAIL: mode export is stale; run tools/export_modes.py', file=sys.stderr)
            return 1
        print('PASS: agent instructions match versioned mode sources')
    else:
        OUTPUT.parent.mkdir(exist_ok=True)
        OUTPUT.write_text(rendered)
        print('agents/mode-instructions.json updated')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
