"""Figure 8: workflow features against outcome metrics (roadmap g17 analysis, paper figure).

Panels (all numbers read from the g17 results file; nothing is recomputed here)
  a  Spearman rho for every feature-outcome test, features (rows, grouped) x outcomes (columns: cnp, fwci,
     novelty_pair, breadth_refs, breadth_citers); diverging blue-grey-red colour scale centred at 0 with symmetric
     limits; cells with Benjamini-Hochberg q < 0.1 are outlined in ink. g17 keeps a binary feature when it is present
     in 10 to n - 10 of all its papers, but the breadth_citers column uses a subset (papers with at least 10 non-self
     citers), so some binary features fall outside 10..n - 10 there. Those cells are drawn faded and hatched; their
     count is prevalence x n from g17 (exact to the paper when n < 100, since g17 rounds prevalence to 0.01).
  b  forest plot of the tests with q < 0.1: rho with its 95% bootstrap interval (2000 resamples over papers, from
     g17), grouped by outcome
  c  rank correlations among the five outcomes (g17 outcome_intercorrelation, lower triangle) on their own -1..1
     colour scale with a small colourbar; values written where |rho| >= 0.2; pairs with breadth_citers use its subset

Row labels for entry state, mode, decisive mode and composition come from agents/coder/definitions.json
(terms[<value>]['label']) when the term is defined there, else from the coded value with underscores as spaces.

Rounds: g17 (tools/roadmap/g17_outcomes.py) reads only the round-1 codings (tag calc1) and gold metrics, so panels a-c
are round 1. If a round-2 results file in the same format exists (derived/outcomes_r2/outcomes.json or
derived/r2calc/outcomes.json), panel b adds the round-2 estimate for the same feature-outcome pairs as a second series.
If round-2 codings (private/analysis/codings/api/r2) exist but no such file does, the script prints a warning and records
it in numbers['round2_source'], so the figure cannot go stale silently.

Inputs
  private/data/roadmap/derived/outcomes/outcomes.json      g17: rows {feature, type, outcome, rho, ci, p, q, n,
                                                           prevalence}, outcome_summary, outcome_intercorrelation
  private/data/roadmap/derived/calc1/manifest.jsonl        eligible round-1 papers (count only, for the caption)
  private/analysis/codings/api/calc1/                      round-1 codings (count only, for the caption)
  agents/coder/definitions.json                            term labels
  private/data/roadmap/derived/outcomes_r2/outcomes.json   round 2, when present (same format)

Outputs  private/data/roadmap/figures/paper/fig08_outcomes.{pdf,png,json}
Run:     python tools/roadmap/figures/fig08_outcomes.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgb
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402

SRC = ps.DERIVED / 'outcomes' / 'outcomes.json'
SRC_R2 = [ps.DERIVED / 'outcomes_r2' / 'outcomes.json', ps.DERIVED / 'r2calc' / 'outcomes.json']
MANIFEST = ps.DERIVED / 'calc1' / 'manifest.jsonl'
CODINGS = ps.PRIVATE / 'analysis' / 'codings' / 'api' / 'calc1'
CODINGS_R2 = ps.PRIVATE / 'analysis' / 'codings' / 'api' / 'r2'
DEFS = ps.ROOT / 'agents' / 'coder' / 'definitions.json'
Q_CUT = 0.1
MIN_PAPERS = 10          # g17 prevalence filter: present in MIN_PAPERS to n - MIN_PAPERS papers
LABEL_RHO = 0.2          # panel c writes values where |rho| >= this

OUTCOMES = ['cnp', 'fwci', 'novelty_pair', 'breadth_refs', 'breadth_citers']
OUT_SHORT = {'cnp': 'Citation percentile', 'fwci': 'FWCI', 'novelty_pair': 'Topic-pair rarity',
             'breadth_refs': 'Refs outside geoscience', 'breadth_citers': 'Citers outside geoscience'}
OUT_LONG = {'cnp': 'Impact: citation percentile (cnp)', 'fwci': 'Impact: field-weighted citations (FWCI)',
            'novelty_pair': 'Novelty: rare topic pair', 'breadth_refs': 'Breadth: references outside geoscience',
            'breadth_citers': 'Breadth: citers outside geoscience'}

COUNTS = {'steps': 'Steps', 'distinct nodes': 'Distinct nodes', 'distinct modes': 'Distinct modes of inquiry',
          'revisits': 'Node revisits', 'returns after failure': 'Returns after failure', 'imports': 'Borrowed from other fields',
          'import fields': 'Fields borrowed from', 'novelty claims': 'Novelty claims',
          'V check kinds': 'Kinds of V check'}
CHECKS = {'claim gate yes': 'Claim gate passed', 'action gate yes or partly': 'Action gate passed or partly',
          'V full': 'V check full', 'triangulation': 'Triangulation',
          'any return after failure': 'Any return after failure', 'outcome contradicted': 'Outcome contradicted'}
# (group key, header in panel a, prefix in panel b)
GROUPS = [('count', 'Counts per paper', ''), ('check', 'Gates and checks', ''), ('entry', 'Entry state', 'Entry: '),
          ('node', 'Node used', 'Node used: '), ('mode', 'Mode of inquiry used', 'Mode of inquiry used: '),
          ('decisive', 'Decisive mode of inquiry', 'Decisive mode of inquiry: '), ('composition', 'Composition', 'Composition: '),
          ('other', 'Other', '')]
TERMS = {}               # filled in main() from definitions.json


def term_label(value):
    """Label from definitions.json when the term is defined there, else the coded value with spaces."""
    lab = TERMS.get(value, {}).get('label') or value.replace('_', ' ')
    return lab[:1].upper() + lab[1:]


def classify(feat):
    """Return (group, sort key, short label) for a g17 feature name."""
    if feat in COUNTS:
        return 'count', list(COUNTS).index(feat), COUNTS[feat]
    if feat in CHECKS:
        return 'check', list(CHECKS).index(feat), CHECKS[feat]
    head, _, rest = feat.partition(' ')
    if head == 'node':
        letter = rest.split(' ')[0]
        return 'node', ps.NODES.index(letter), f'{letter} ({ps.NODE_NAMES[letter]})'
    if head in ('mode', 'entry', 'decisive', 'composition'):
        return head, rest, term_label(rest)
    return 'other', feat, feat


def few_papers(r, papers):
    """True when a binary feature is present in fewer than MIN_PAPERS, or more than n - MIN_PAPERS, papers of this test.

    g17 applies the filter over all `papers`, so it holds by construction for tests on the full set; it can fail only
    on a subset (breadth_citers). Count = prevalence x n, exact when n < 100 (prevalence is rounded to 0.01)."""
    if r.get('type') != 'bin' or r.get('prevalence') is None or r['n'] >= papers:
        return False
    k = round(r['prevalence'] * r['n'])
    return k < MIN_PAPERS or k > r['n'] - MIN_PAPERS


def _rel(p):
    return str(p.relative_to(ps.ROOT)) if p.is_relative_to(ps.ROOT) else str(p)


def fade(rgb, w=0.62):
    """Blend a colour toward white (helper kept here: paperstyle has none)."""
    c = np.array(to_rgb(rgb))
    return tuple(c + (1 - c) * w)


def heatmap(ax, rows, papers, numbers):
    """Panel a: grouped features x outcomes; returns the colour norm and map."""
    feats = sorted({r['feature'] for r in rows}, key=lambda f: ([g for g, _, _ in GROUPS].index(classify(f)[0]),
                                                                 str(classify(f)[1]).zfill(4)))
    cell = {(r['feature'], r['outcome']): r for r in rows}
    lim = float(np.ceil(max(abs(r['rho']) for r in rows) * 10) / 10)
    norm = Normalize(-lim, lim)
    cmap = LinearSegmentedColormap.from_list('div', [ps.DIV_NEG, ps.DIV_MID, ps.DIV_POS])
    y, ticks, labels, heads, ymap, faded = 0.0, [], [], [], {}, []
    HEAD = 1.15
    for g, gname, _ in GROUPS:
        fs = [f for f in feats if classify(f)[0] == g]
        if not fs:
            continue
        heads.append((y + HEAD * 0.55, gname))
        y += HEAD
        for f in fs:
            for j, o in enumerate(OUTCOMES):
                r = cell.get((f, o))
                if r is None:
                    ax.add_patch(Rectangle((j, y), 1, 1, facecolor='white', edgecolor=ps.GRID, linewidth=0.4, hatch='////'))
                    continue
                if few_papers(r, papers):
                    ax.add_patch(Rectangle((j, y), 1, 1, facecolor=fade(cmap(norm(r['rho']))), edgecolor='white',
                                           linewidth=0.6))
                    ax.add_patch(Rectangle((j, y), 1, 1, facecolor='none', hatch='//////', hatchcolor=ps.MUTED,
                                           linewidth=0))
                    faded.append({'feature': f, 'outcome': o, 'n': r['n'], 'prevalence': r['prevalence'],
                                  'papers_with_feature': round(r['prevalence'] * r['n']), 'rho': r['rho']})
                    continue
                ax.add_patch(Rectangle((j, y), 1, 1, facecolor=cmap(norm(r['rho'])), edgecolor='white', linewidth=0.6))
            ticks.append(y + 0.5)
            labels.append(classify(f)[2])
            ymap[f] = y
            y += 1
    # q < 0.1 outlines drawn last so they sit above the white gaps
    sig = 0
    for f in feats:
        for j, o in enumerate(OUTCOMES):
            r = cell.get((f, o))
            if r and r['q'] < Q_CUT:
                ax.add_patch(Rectangle((j + 0.06, ymap[f] + 0.06), 0.88, 0.88, facecolor='none', edgecolor=ps.INK, linewidth=0.9))
                sig += 1
    ax.set_xlim(0, len(OUTCOMES))
    ax.set_ylim(y, 0)
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=ps.SMALL)
    ax.tick_params(axis='y', length=0, pad=2)
    for yy, gname in heads:
        ax.text(-0.04, yy, gname, transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=ps.SMALL,
                fontweight='bold', color=ps.INK)
    n_by_o = {o: max((r['n'] for r in rows if r['outcome'] == o), default=0) for o in OUTCOMES}
    ax.xaxis.tick_top()
    ax.set_xticks(np.arange(len(OUTCOMES)) + 0.5)
    full = max(n_by_o.values())
    ax.set_xticklabels([OUT_SHORT[o] for o in OUTCOMES], rotation=50, ha='left',
                       rotation_mode='anchor', fontsize=ps.SMALL)
    ax.tick_params(axis='x', length=0, pad=2)
    # papers per column, written under the heatmap only where it differs from the full sample
    for j, o in enumerate(OUTCOMES):
        if n_by_o[o] != full:
            ax.text(j + 0.5, y + 0.25, f'n = {n_by_o[o]}', ha='center', va='top', fontsize=ps.SMALL, color=ps.INK2)
    for s in ax.spines.values():
        s.set_visible(False)
    nfaded = {o: len({c['feature'] for c in faded if c['outcome'] == o}) for o in OUTCOMES}
    numbers['panel_a_features'] = len(feats)
    numbers['panel_a_tests'] = len(rows)
    numbers['panel_a_cells_outlined_q_below_0.1'] = sig
    numbers['panel_a_colour_limits'] = [-lim, lim]
    numbers['panel_a_n_per_outcome'] = n_by_o
    numbers['panel_a_faded_cells_outside_10_to_n_minus_10'] = faded
    numbers['panel_a_faded_features_per_outcome'] = nfaded
    numbers['panel_a_rho'] = {f: {o: cell[(f, o)]['rho'] for o in OUTCOMES if (f, o) in cell} for f in feats}
    return norm, cmap, n_by_o, nfaded


def forest(ax, sig, r2rows, numbers):
    """Panel b: q < 0.1 tests, grouped by outcome in column order, sorted by rho within each outcome."""
    prefix = {g: p for g, _, p in GROUPS}
    y, ticks, labels, heads, drawn = 0.0, [], [], [], []
    r2 = {(r['feature'], r['outcome']): r for r in r2rows} if r2rows else {}
    off = 0.18 if r2 else 0.0
    for o in OUTCOMES:
        rs = sorted([r for r in sig if r['outcome'] == o], key=lambda r: -r['rho'])
        if not rs:
            continue
        heads.append((y + 0.75, OUT_LONG[o]))
        y += 1.2
        for r in rs:
            g, _, short = classify(r['feature'])
            yc = y + 0.5
            ax.plot(r['ci'], [yc - off] * 2, color=ps.BLUE, linewidth=0.9, solid_capstyle='butt', zorder=2)
            ax.plot([r['rho']], [yc - off], 'o', color=ps.BLUE, markersize=3.2, markeredgecolor='white',
                    markeredgewidth=0.4, zorder=3)
            if r2:
                q2 = r2.get((r['feature'], o))
                if q2:
                    ax.plot(q2['ci'], [yc + off] * 2, color=ps.ORANGE, linewidth=0.9, solid_capstyle='butt', zorder=2)
                    ax.plot([q2['rho']], [yc + off], 's', color=ps.ORANGE, markersize=2.8, markeredgecolor='white',
                            markeredgewidth=0.4, zorder=3)
            ticks.append(yc)
            labels.append(prefix[g] + (short.lower() if g in ('mode', 'decisive', 'composition', 'entry') else short))
            drawn.append({'feature': r['feature'], 'outcome': o, 'rho': r['rho'], 'ci': r['ci'], 'q': r['q'], 'p': r['p'],
                          'n': r['n'], 'prevalence': r['prevalence'],
                          'round2': ({'rho': r2[(r['feature'], o)]['rho'], 'ci': r2[(r['feature'], o)]['ci'],
                                      'q': r2[(r['feature'], o)]['q']} if (r['feature'], o) in r2 else None)})
            y += 1
    ax.axvline(0, color=ps.MUTED, linewidth=0.6, zorder=1)
    ax.set_ylim(y + 0.1, 0)
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=ps.SMALL)
    ax.tick_params(axis='y', length=0, pad=2)
    for yy, h in heads:
        ax.text(-0.02, yy, h, transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=ps.SMALL,
                fontweight='bold', color=ps.INK)
    lo = min(min(d['ci'][0] for d in drawn), 0)
    hi = max(d['ci'][1] for d in drawn)
    ax.set_xlim(np.floor(lo * 10) / 10 - 0.05, np.ceil(hi * 10) / 10 + 0.02)
    ax.set_xlabel(r'Spearman $\rho$ with 95% bootstrap interval')
    ps.grid(ax, 'x')
    ax.spines['left'].set_visible(False)
    numbers['panel_b_tests'] = drawn
    if r2:
        ax.legend(handles=[Line2D([], [], color=ps.BLUE, marker='o', markersize=3.2, linewidth=0.9, label='Round 1'),
                           Line2D([], [], color=ps.ORANGE, marker='s', markersize=2.8, linewidth=0.9, label='Round 2')],
                  loc='lower right', handlelength=1.6)
    return drawn


def intercorr(ax, inter, cmap, n_by_o, numbers):
    """Panel c: lower-triangle matrix of outcome rank correlations on its own -1..1 scale; returns the norm."""
    norm = Normalize(-1, 1)
    k = len(OUTCOMES)
    shown, written = {}, {}
    for i in range(k):
        for j in range(i):
            a, b = OUTCOMES[j], OUTCOMES[i]
            v = inter.get(f'{a}~{b}', inter.get(f'{b}~{a}'))
            if v is None:
                continue
            shown[f'{a}~{b}'] = v
            ax.add_patch(Rectangle((j, i - 1), 1, 1, facecolor=cmap(norm(v)), edgecolor='white', linewidth=0.6))
            if abs(v) >= LABEL_RHO:
                written[f'{a}~{b}'] = round(v, 2)
                ax.text(j + 0.5, i - 0.5, f'{v:.2f}', ha='center', va='center', fontsize=ps.SMALL,
                        color='white' if abs(v) > 0.7 else ps.INK)
    ax.set_xlim(0, k - 1)
    ax.set_ylim(k - 1, 0)
    ax.set_xticks(np.arange(k - 1) + 0.5)
    ax.set_xticklabels([OUT_SHORT[o] for o in OUTCOMES[:-1]], rotation=50, ha='right', rotation_mode='anchor',
                       fontsize=ps.SMALL)
    full = max(n_by_o.values())
    ylabs = [OUT_SHORT[o] + (f' (n = {n_by_o[o]})' if n_by_o[o] != full else '') for o in OUTCOMES[1:]]
    ax.set_yticks(np.arange(k - 1) + 0.5)
    ax.set_yticklabels(ylabs, fontsize=ps.SMALL)
    ax.tick_params(length=0, pad=2)
    for s in ax.spines.values():
        s.set_visible(False)
    numbers['panel_c_outcome_intercorrelation'] = shown
    numbers['panel_c_values_written_abs_rho_ge_0.2'] = written
    numbers['panel_c_colour_limits'] = [-1, 1]
    return norm


def main():
    TERMS.update(json.loads(DEFS.read_text())['terms'])
    d = ps.read_json(SRC)
    rows = [r for r in d['rows'] if r['outcome'] in OUTCOMES]
    papers = d['papers']
    eligible = sum(1 for line in MANIFEST.read_text().splitlines() if line.strip())
    coded = len(list(CODINGS.glob('*.json')))
    inputs = [SRC, MANIFEST, DEFS]
    numbers = {'papers': papers, 'eligible_round1': eligible, 'codings_round1_files': coded, 'tests': d['tests'],
               'q_below_0.1': d['q_below_0.1'], 'q_cut': Q_CUT, 'min_papers_filter': MIN_PAPERS,
               'outcome_summary': d['outcome_summary'], 'note_from_g17': d.get('note')}
    r2path = next((p for p in SRC_R2 if p.is_file()), None)
    r2rows = None
    if r2path:
        d2 = ps.read_json(r2path)
        r2rows = d2['rows']
        inputs.append(r2path)
        numbers['round2_papers'] = d2.get('papers')
        numbers['round2_tests'] = d2.get('tests')
        numbers['round2_q_below_0.1'] = d2.get('q_below_0.1')
        numbers['round2_source'] = str(r2path.relative_to(ps.ROOT))
    elif CODINGS_R2.is_dir():
        n2 = len(list(CODINGS_R2.glob('*.json')))
        numbers['round2_source'] = f'r2 codings present ({n2} files) but not analysed: g17 reads calc1 only'
        print(f'WARNING: {_rel(CODINGS_R2)} holds {n2} codings but no round-2 outcomes file exists '
              f'({", ".join(_rel(p) for p in SRC_R2)}); fig08 shows round 1 only. '
              'Run g17 on the r2 codings to include round 2.', file=sys.stderr)
    else:
        numbers['round2_source'] = 'absent: no r2 codings and no round-2 outcomes file'
    numbers['rounds_drawn'] = ['round 1 (calc1)'] + (['round 2 (r2), panel b only'] if r2rows else [])
    sig = [r for r in rows if r['q'] < Q_CUT]

    W, H = ps.DOUBLE, 6.75
    fig, _ = ps.figure(W, H)
    fig.axes[0].remove()

    def box(x0, y0, w, h):           # inches from bottom-left to figure fraction
        return [x0 / W, y0 / H, w / W, h / H]

    nfeat = len({r['feature'] for r in rows})
    ngroups = len({classify(r['feature'])[0] for r in rows})
    units = nfeat + 1.15 * ngroups
    hm_h = units * 0.092
    hm_top = H - 0.95
    axa = fig.add_axes(box(1.48, hm_top - hm_h, 1.45, hm_h))
    norm, cmap, n_by_o, nfaded = heatmap(axa, rows, papers, numbers)
    ps.panel(axa, 'a', x=-1.48 / 1.45, y=1.0 + 0.82 / hm_h)

    cb_y = hm_top - hm_h - 0.30
    cax = fig.add_axes(box(1.48, cb_y, 1.45, 0.07))
    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation='horizontal')
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=ps.SMALL, length=2, width=0.5)
    cb.set_label(r'Spearman $\rho$ (a)', fontsize=ps.SMALL, labelpad=2)
    lim = norm.vmax
    cb.set_ticks([-lim, -lim / 2, 0, lim / 2, lim])
    # key for panel a, beside its colourbar
    kx = fig.add_axes(box(3.12, cb_y - 0.26, 1.7, 0.42))
    kx.set_axis_off()
    kx.set_xlim(0, 1.7)
    kx.set_ylim(0, 0.42)
    sw = 0.13
    kx.add_patch(Rectangle((0.0, 0.25), sw, 0.11, facecolor=ps.DIV_MID, edgecolor=ps.INK, linewidth=0.9))
    kx.text(sw + 0.06, 0.305, f'Benjamini-Hochberg q < {Q_CUT:g}', va='center', fontsize=ps.SMALL, color=ps.INK)
    kx.add_patch(Rectangle((0.0, 0.03), sw, 0.11, facecolor=fade(ps.DIV_POS), edgecolor='none', linewidth=0))
    kx.add_patch(Rectangle((0.0, 0.03), sw, 0.11, facecolor='none', hatch='//////', hatchcolor=ps.MUTED, linewidth=0))
    kx.text(sw + 0.06, 0.085, f'Fewer than {MIN_PAPERS} papers with,\nor without, the feature', va='center',
            fontsize=ps.SMALL, color=ps.INK, linespacing=1.0)

    nb = len(sig) + 1.2 * len({r['outcome'] for r in sig})
    fb_h = nb * 0.155
    axb = fig.add_axes(box(5.05, H - 0.42 - fb_h, 2.05, fb_h))
    drawn = forest(axb, sig, r2rows, numbers)
    ps.panel(axb, 'b', x=-1.70 / 2.05, y=1.0 + 0.02 / fb_h)

    cs = 1.1
    c_y = H - 0.42 - fb_h - 0.62 - cs
    axc = fig.add_axes(box(5.05, c_y, cs, cs))
    norm_c = intercorr(axc, d['outcome_intercorrelation'], cmap, n_by_o, numbers)
    ps.panel(axc, 'c', x=-1.70 / cs, y=1.04)
    ccax = fig.add_axes(box(5.05 + cs + 0.12, c_y + 0.05, 0.06, cs - 0.1))
    cbc = fig.colorbar(ScalarMappable(norm=norm_c, cmap=cmap), cax=ccax, orientation='vertical')
    cbc.outline.set_visible(False)
    cbc.ax.tick_params(labelsize=ps.SMALL, length=2, width=0.5, pad=1)
    cbc.set_ticks([-1, -0.5, 0, 0.5, 1])
    cbc.set_label(r'Spearman $\rho$ (c)', fontsize=ps.SMALL, labelpad=2)

    ia = d['outcome_intercorrelation']
    n_cit = d['outcome_summary']['breadth_citers']['n']
    nb_n = sorted({r['n'] for r in sig})
    p_floor = round(1 / 5001, 4)
    at_floor = [r for r in sig if r['p'] <= p_floor]
    distinct = len({(r['feature'], 'impact' if r['outcome'] in ('cnp', 'fwci') else r['outcome']) for r in sig})
    minority = [min(c['papers_with_feature'], c['n'] - c['papers_with_feature'])
                for c in numbers['panel_a_faded_cells_outside_10_to_n_minus_10']]
    numbers['panel_a_faded_minority_papers_range'] = [min(minority), max(minority)] if minority else None
    numbers['panel_b_p_floor'] = p_floor
    numbers['panel_b_tests_at_p_floor'] = [f"{r['feature']}~{r['outcome']}" for r in at_floor]
    numbers['panel_b_distinct_associations_cnp_fwci_merged'] = distinct
    caption = (
        f"Workflow features of the coded papers against outcome metrics. Round 1: the {papers} of {eligible} eligible "
        f"earth-science papers published in 2022 that had full text ({coded}) and a coding that passed schema "
        f"validation; full-text availability leans toward open access and so filters the sample. Coded by "
        f"claude-opus-5-5 under codebook 1.5.0 on graph v0.4.2; g17 analysis, tools/roadmap/g17_outcomes.py. "
        f"(a) Spearman rank correlation for each of {d['tests']} feature-outcome tests: {nfeat} features (counts per "
        f"paper from the final-paper sequence; binary features, scored 0/1, kept when present in {MIN_PAPERS} to "
        f"n - {MIN_PAPERS} of all {papers} papers) against five outcomes from OpenAlex (retrieved October 2026, about four years after "
        f"publication): cnp, the citation normalized percentile, the paper's citation count ranked among works of the "
        f"same OpenAlex subfield, year and type, 0 to 1; FWCI, field-weighted citation impact, citations divided by the "
        f"mean for those works, 1 = world average; novelty_pair, the rarity of the paper's two leading OpenAlex topics "
        f"as a pair, -log10(1 + number of 2017-2021 works sharing the pair), higher is rarer; breadth_refs, the share of "
        f"classified references outside geoscience (OpenAlex fields Earth and Planetary Sciences and Environmental "
        f"Science, plus audited geoscience topics filed elsewhere); and breadth_citers, the same share for citing works "
        f"after removing self-citations (only papers with at least 10 such citers, n = {n_cit}). novelty_pair and the "
        f"two breadth measures are not normalized by subfield. A further planned outcome, advance (a blind human rating of "
        f"the contribution), is not yet measured. "
        f"Because that filter is applied over all {papers} papers, {nfaded['breadth_citers']} of "
        f"{nfeat} features fall outside {MIN_PAPERS} to n - {MIN_PAPERS} papers in the n = {n_cit} column; those cells "
        f"are faded and hatched, and their colour rests on {min(minority)} to {max(minority)} papers with, or without, the feature. Outlined cells "
        f"have Benjamini-Hochberg q < {Q_CUT:g} over all {d['tests']} tests (two-sided permutation p, 5000 "
        f"permutations; {len(at_floor)} of the outlined tests sit at the permutation floor p = 1/5001 = {p_floor}, so "
        f"their q is bounded by the number of permutations). V is the Vary or replicate node. "
        f"(b) The {len(sig)} tests with q < {Q_CUT:g}: rho and 95% percentile bootstrap interval (2000 resamples over "
        f"papers), n = {nb_n[0] if len(nb_n) == 1 else ', '.join(map(str, nb_n))} papers each. The cnp and FWCI rows "
        f"repeat the same features, so the panel holds {distinct} distinct associations. Borrowed from other fields is the "
        f"number of concepts, methods, instruments or data from outside Earth science that the coder lists (codebook "
        f"section 6), and fields borrowed from the number of their distinct source fields; their correlation with "
        f"breadth_refs is a convergent validity check of the coder (the same thing measured from the text and from the "
        f"reference list), not a workflow-outcome finding. (c) Rank correlations among "
        f"the outcomes on their own -1 to 1 colour scale; values written where |rho| >= {LABEL_RHO:g}; pairs with "
        f"citers outside geoscience use n = {n_cit}, the rest n = {papers}. cnp and FWCI correlate at "
        f"{ia.get('cnp~fwci'):.2f}, so their columns in (a) repeat one impact signal rather than giving independent "
        f"support. Exploratory and descriptive: one model coder, citations about four years after publication, no "
        f"adjustment for journal or subfield beyond the field normalisation built into cnp and FWCI; no causal reading."
        + (f" Round 2 estimates in (b) from {numbers['round2_source']}." if r2rows else ''))
    ps.save(fig, 'fig08_outcomes', inputs=inputs, numbers=numbers, caption=caption)
    print(json.dumps({k: v for k, v in numbers.items() if k not in ('panel_a_rho', 'panel_b_tests')}, indent=1,
                     default=str)[:3000])
    print(caption)


if __name__ == '__main__':
    main()
