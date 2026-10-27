"""Shared style and provenance for the roadmap's paper figures.

Every figure script imports this module, draws with its constants, and saves through `save()`, which writes
  private/data/roadmap/figures/paper/<name>.pdf   vector, fonts embedded (Type 42)
  private/data/roadmap/figures/paper/<name>.png   300 dpi, for review and slides
  private/data/roadmap/figures/paper/<name>.json  provenance: script, commit, date, every input file with sha256,
                                                  the numbers drawn, and a draft caption
so each number in a figure traces to a file and a commit (tools/roadmap/README.md, traceability rules 1-6).

Sizes follow AGU and most Earth-science journals: one column 3.5 in (89 mm), two columns 7.2 in (183 mm), text 7 pt,
panel labels 8 pt bold. Colours are the dataviz reference palette in light mode; slots 1-6 were checked with the
dataviz validator on a white surface (adjacent colour-blind separation >= 9.1, normal vision >= 19.6). Slots 3, 4 and 5
are below 3:1 contrast on white, so marks in those colours carry a direct label or sit beside one.
"""
from __future__ import annotations

import hashlib
import json
import logging
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

logging.getLogger('fontTools').setLevel(logging.ERROR)   # Helvetica .ttc subsetting notices
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from common import DATA, DERIVED, ROOT, TODAY, read_json  # noqa: E402,F401

OUT = DATA / 'figures' / 'paper'

SINGLE, DOUBLE = 3.5, 7.2          # inches
FONT, SMALL, LABEL = 7, 6, 8      # pt

# categorical slots, fixed order (never cycled)
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300'
SERIES = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN]
# ink and chrome
INK, INK2, MUTED = '#0b0b0b', '#52514e', '#898781'
GRID, AXIS = '#e1e0d9', '#c3c2b7'
NEUTRAL = '#c3c2b7'               # "other", "not available", de-emphasised marks
# sequential (blue, light to dark) and diverging (blue to red through grey)
SEQ = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']
DIV_NEG, DIV_MID, DIV_POS = '#2a78d6', '#f0efec', '#e34948'

# graph v0.4.2 nodes in the order of the graph (codebook 1.5.0)
NODES = list('NEOIQHSDFCVXKPR')
NODE_NAMES = {'N': 'New capability', 'E': 'Explore', 'O': 'Observe', 'I': 'Infer', 'Q': 'Question',
              'H': 'Hypothesize', 'S': 'Simulate or derive', 'D': 'Design', 'F': 'Find conditions',
              'C': 'Compare', 'V': 'Vary or replicate', 'X': 'Exclude', 'K': 'Keep', 'P': 'Protect', 'R': 'Refine'}


def setup() -> None:
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
        'font.size': FONT, 'axes.titlesize': FONT, 'axes.labelsize': FONT, 'xtick.labelsize': SMALL,
        'ytick.labelsize': SMALL, 'legend.fontsize': SMALL, 'legend.frameon': False,
        'axes.edgecolor': AXIS, 'axes.linewidth': 0.6, 'axes.labelcolor': INK, 'text.color': INK,
        'xtick.color': INK2, 'ytick.color': INK2, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
        'xtick.major.size': 2.5, 'ytick.major.size': 2.5, 'axes.spines.top': False, 'axes.spines.right': False,
        'axes.grid': False, 'grid.color': GRID, 'grid.linewidth': 0.5, 'grid.linestyle': '-',
        'lines.linewidth': 1.2, 'lines.markersize': 4, 'patch.linewidth': 0,
        'axes.prop_cycle': matplotlib.cycler(color=SERIES),
        'figure.dpi': 150, 'savefig.dpi': 300, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.02,
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none'})


def figure(width: float = DOUBLE, height: float = 3.0, **kw):
    setup()
    return plt.subplots(figsize=(width, height), **kw)


def panel(ax, letter: str, x: float = -0.12, y: float = 1.04) -> None:
    ax.text(x, y, f'({letter})', transform=ax.transAxes, fontsize=LABEL, fontweight='bold', va='bottom', ha='left')


def grid(ax, axis: str = 'x') -> None:
    """Hairline grid behind the marks, on the value axis only."""
    ax.grid(True, axis=axis, color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def _commit(repo: Path, paths: list[str]) -> str:
    try:
        sha = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(['git', '-C', str(repo), 'status', '--porcelain', *paths], capture_output=True, text=True).stdout.strip()
        return sha + ('+uncommitted' if dirty else '')
    except Exception:  # noqa: BLE001
        return 'unknown'


def save(fig, name: str, inputs: list, numbers: dict, caption: str) -> Path:
    """Write <name>.pdf, .png and .json (provenance, numbers drawn, draft caption); return the PDF path."""
    OUT.mkdir(parents=True, exist_ok=True)
    script = Path(sys.argv[0]).resolve()
    fig.savefig(OUT / f'{name}.pdf', metadata={'Title': name, 'Creator': script.name})
    fig.savefig(OUT / f'{name}.png')
    plt.close(fig)
    ins = []
    for p in inputs:
        p = Path(p)
        p = p if p.is_absolute() else ROOT / p
        ins.append({'file': str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
                    'sha256_16': _sha(p) if p.is_file() else None,
                    'provenance': _provenance(p)})
    prov = {'figure': name, 'script': str(script.relative_to(ROOT)) if script.is_relative_to(ROOT) else str(script), 'date': TODAY,
            'commit_public': _commit(ROOT, ['tools/roadmap']),
            'commit_private': _commit(ROOT / 'private', ['data/roadmap/derived', 'analysis/codings']),
            'inputs': ins, 'numbers': numbers, 'caption': caption}
    (OUT / f'{name}.json').write_text(json.dumps(prov, indent=1, ensure_ascii=False, default=str))
    print(f'wrote {OUT.relative_to(ROOT)}/{name}.pdf|.png|.json')
    return OUT / f'{name}.pdf'


def _provenance(p: Path):
    if p.suffix == '.json' and p.is_file():
        try:
            return json.loads(p.read_text()).get('_provenance')
        except Exception:  # noqa: BLE001
            return None
    return None
