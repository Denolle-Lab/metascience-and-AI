"""Load credentials from ~/.config/metascience/keys.env (or $METASCIENCE_KEYS) into the environment.

The file holds one KEY=value per line; '#' starts a comment. Variables already set in the shell win.
Keep the file outside every repository and readable only by you (chmod 600).
"""
from __future__ import annotations
import os
from pathlib import Path

KEYS = Path(os.environ.get('METASCIENCE_KEYS', Path.home() / '.config' / 'metascience' / 'keys.env'))


def load() -> None:
    if not KEYS.is_file():
        return
    if KEYS.stat().st_mode & 0o077:
        print(f'warning: {KEYS} is readable by others; run: chmod 600 {KEYS}')
    for line in KEYS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        v = v.strip().strip('"').strip("'")
        if v:
            os.environ.setdefault(k.strip(), v)
