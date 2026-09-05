#!/usr/bin/env python3
"""Validate book sources and run Pandoc citation processing (not a Quarto build)."""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlparse

try:
    import yaml
except ImportError:
    sys.exit('Install PyYAML: python3 -m pip install PyYAML')

ROOT = Path(__file__).resolve().parents[1]
FENCE = re.compile(r'^(`{3,}|~{3,}).*?^\1[^\S\n]*$', re.M | re.S)

def prose(text: str) -> str:
    """Drop fenced code blocks. A worked example is not a citation or a link."""
    return FENCE.sub('', text)

def chapters(items: list) -> list[str]:
    result = []
    for item in items:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict) and 'chapters' in item:
            result.extend(chapters(item['chapters']))
        else:
            raise ValueError(f'Unexpected chapter item: {item!r}')
    return result

def main() -> int:
    errors: list[str] = []
    config = yaml.safe_load((ROOT / '_quarto.yml').read_text())
    order = chapters(config['book']['chapters'])
    data = json.loads((ROOT / 'curriculum.json').read_text())
    refs, sessions = data['references'], data['sessions']
    bib = (ROOT / 'references.bib').read_text()
    bib_keys = re.findall(r'^@\w+\{([^,]+),', bib, flags=re.M)
    if len(bib_keys) != len(set(bib_keys)):
        errors.append('Duplicate BibTeX keys')
    if set(bib_keys) != set(refs):
        errors.append('BibTeX keys and editorial reference metadata differ')
    if len(sessions) != 13:
        errors.append('Expected 13 sessions')
    if len(order) != len(set(order)):
        errors.append('Duplicate chapter paths')
    # The parallel analysis in private/ is deliberately excluded from the public
    # book. Guard both the chapter list and the ignore rule that keeps it unstaged.
    gitignore = ROOT / '.gitignore'
    if not gitignore.is_file() or not re.search(r'^private/\s*$', gitignore.read_text(), flags=re.M):
        errors.append('.gitignore must contain a "private/" rule')
    all_text: list[str] = []
    cited: set[str] = set()
    for name in order:
        if name.startswith('private/'):
            errors.append(f'Private material must not be a published chapter: {name}')
            continue
        path = ROOT / name
        if not path.is_file():
            errors.append(f'Missing chapter: {name}')
            continue
        text = path.read_text()
        all_text.append(text)
        body = prose(text)
        cited.update(re.findall(r'(?<![\w])@([A-Za-z][A-Za-z0-9_-]*)', body))
        for target in re.findall(r'\]\(([^)]+)\)', body):
            # External URLs and local fragments are not filesystem paths.
            if urlparse(target).scheme or target.startswith('#'):
                continue
            target = target.split('#', 1)[0]
            if target and not (path.parent / target).is_file():
                errors.append(f'Broken local link in {name}: {target}')
    unknown = cited - set(bib_keys)
    if unknown:
        errors.append('Unknown citation keys: ' + ', '.join(sorted(unknown)))
    required = set()
    start = dt.date(2026, 9, 8)
    for index, session in enumerate(sessions):
        expected = start + dt.timedelta(weeks=index)
        date = dt.date.fromisoformat(session['date'])
        if session['n'] != index + 1 or date != expected or date.weekday() != 1:
            errors.append(f'Unexpected meeting number/date: {session["n"]}, {date}')
        if len(session['pair']) != 2:
            errors.append(f'Meeting {session["n"]} does not have two required papers')
        # Discussant papers are read in depth by a rotating discussant rather than
        # by every participant. They are cited on the page and linked like the pair.
        discussant = session.get('discussant', [])
        assigned = list(session['pair']) + list(discussant)
        if len(set(assigned)) != len(assigned):
            errors.append(f'Meeting {session["n"]} repeats a paper across pair and discussant')
        required.update(assigned)
        path = ROOT / 'sessions' / f'{session["n"]:02}-{session["slug"]}.qmd'
        if path.is_file():
            text = path.read_text()
            if any('@' + key not in text for key in assigned):
                errors.append(f'Assigned citation missing in {path.name}')
    for key in required:
        if key not in refs or not urlparse(refs[key]['url']).scheme:
            errors.append(f'Missing paper link for {key}')
    command = [shutil.which('pandoc')] if shutil.which('pandoc') else ([shutil.which('quarto'), 'pandoc'] if shutil.which('quarto') else None)
    if not command:
        errors.append('Pandoc not available: install Pandoc or Quarto for citation smoke test')
    elif not errors:
        with tempfile.TemporaryDirectory(prefix='metascience-check-') as tmp:
            inp = Path(tmp) / 'combined.md'
            inp.write_text('\n\n'.join(all_text))
            proc = subprocess.run(command + [str(inp), '--from=markdown', '--to=html', '--citeproc', '--bibliography=' + str(ROOT / 'references.bib')], capture_output=True, text=True, timeout=90)
            if proc.returncode:
                errors.append(proc.stderr.strip() or 'Pandoc failed')
            elif 'not found' in proc.stderr.lower() or 'warning' in proc.stderr.lower():
                errors.append('Pandoc warning: ' + proc.stderr.strip())
            else:
                print('PASS: Pandoc Markdown parsing and citation processing (no warnings)')
    if errors:
        print('\n'.join('FAIL: ' + error for error in errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(order)} chapter files, 13 consecutive Tuesdays, {len(required)} assigned papers, {len(bib_keys)} bibliography records')
    print('PASS: all local source links and citation keys resolve')
    print('PASS: no private material is registered as a published chapter')
    print('NOT TESTED: full Quarto render, browser layout, external full-text access, and deployed website')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
