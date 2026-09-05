#!/usr/bin/env python3
"""Stage a rendered Quarto book into one subdirectory; never commit or publish."""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import shutil
import sys

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site_checkout', type=Path, help='Existing local Jekyll website checkout')
    parser.add_argument('--destination', default='metascience', help='Single subdirectory name, not a path')
    parser.add_argument('--replace', action='store_true', help='Explicitly permit replacing that subdirectory only')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.destination):
        parser.error('--destination must be a single non-hidden directory name')
    source = Path(__file__).resolve().parents[1] / '_book'
    site = args.site_checkout.expanduser().resolve()
    if not (source / 'index.html').is_file():
        parser.error('Rendered _book/index.html is missing. Run quarto render first.')
    if not site.is_dir() or not (site / '_config.yml').is_file():
        parser.error('The target must be an existing website directory with _config.yml')
    target = site / args.destination
    if target.is_symlink():
        parser.error('Refusing a symbolic-link destination')
    if source.resolve() == target.resolve() or source.resolve() in target.resolve().parents or target.resolve() in source.resolve().parents:
        parser.error('Source and target may not contain one another')
    if target.exists() and not args.replace:
        parser.error(f'{target} exists; review it and use --replace for an intentional update')
    if target.exists():
        if not target.is_dir():
            parser.error('Destination exists and is not a directory')
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('.nojekyll'))
    print(f'Staged rendered book in {target}')
    print('No other website path was changed; no commit, push, or publication performed.')
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except OSError as exc:
        sys.exit(f'Filesystem error: {exc}')
