"""Figure 7: how much of the open-review work shows in the published paper (roadmap E3 and E4, paper figure).

Experiment E3 coded the open discussion of the Copernicus papers in round 1 as a review sequence (tag calc1-review,
claude-opus-5-5, codebook 1.5.0, graph v0.4.2). In E4 two independent Claude agents running in Claude Code (workflow
tools/roadmap/workflows/visibility.js), with a third agent adjudicating where they differed, read each review step
against the published text and gave it one label:
  as_revision   the published paper shows the change and says it was revised, added, or prompted by review
  as_planned    the published paper shows the change but presents it as part of the original design
  absent        the published paper does not show the change
  no_change     the review step records no change to the work
A "change" is any step not labelled no_change; a change is "hidden" when it is not readable as a revision
(as_planned or absent), as in tools/roadmap/g16_visibility.py analyze. All counts are recomputed here from the labels;
only the quote check (quotes found in the published text) is read from the g16 summary.

Panels
  a  part-to-whole flow on one count axis: review steps -> changes vs no change -> shown as planned, absent, marked
     as revision (zero, drawn as a hollow ink marker); 95% interval on the absent share by bootstrap over papers
     (5000 draws, seed 0), the g16 method, because changes cluster in papers; the Wilson interval, which treats steps
     as independent, is kept in the numbers for comparison
  b  share of changes absent from the published paper, by graph node of the review step (node joined from the
     calc1-review coding, review sequence, step i), nodes with at least 5 changes as in g16, sorted, Wilson 95%
     intervals (steps treated as independent, not adjusted for the 14 comparisons), n per node at right; dashed
     line = pooled share
  c  one column per paper (58), height = changes recorded in its review, split into absent and shown as planned;
     marked as revision is 0 in every paper; one-sided 95% upper bound on the share of papers marking any change
     by the rule of three (3/n)

Labeler agreement (raw, and Cohen's kappa from label_a and label_b over the four labels) goes to the caption.
Selection: the round-1 manifest's Copernicus papers (DOI prefix 10.5194), those with a fetched open discussion
(private/data/roadmap/review/<key>/), and those with a valid review coding; failures are read from state.json.
Journal mix joins the labelled papers to derived/gold/metrics.json.

Rounds: only round 1 has open-review codings and visibility labels. The script draws every round listed in ROUNDS whose
label file exists; round 2 has none today, so numbers['rounds_drawn'] records ['round 1'].

Inputs
  private/data/roadmap/derived/review/visibility_labels.json     E4 labels per paper and step (label, agreed, label_a/b)
  private/analysis/codings/api/calc1-review/<key>.json            E3 review sequences (node of each step)
  private/data/roadmap/derived/review/visibility_results.json    g16 summary: quote check, and differences reported
  private/data/roadmap/derived/calc1/manifest.jsonl               round-1 papers (Copernicus count by DOI prefix)
  private/data/roadmap/derived/gold/metrics.json                  journal of each paper
  private/analysis/codings/api/state.json                         failed calc1-review codings

Outputs  private/data/roadmap/figures/paper/fig07_review.{pdf,png,json}
Run:     python tools/roadmap/figures/fig07_review.py
"""
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402

API = ps.ROOT / 'private' / 'analysis' / 'codings' / 'api'
ROUNDS = [('round 1', 'calc1-review', ps.DERIVED / 'review' / 'visibility_labels.json')]
G16 = ps.DERIVED / 'review' / 'visibility_results.json'
MANIFEST = ps.DERIVED / 'calc1' / 'manifest.jsonl'
METRICS = ps.DERIVED / 'gold' / 'metrics.json'
STATE = API / 'state.json'
REVIEW_DIR = ps.DATA / 'review'
MIN_N = 5            # nodes with fewer changes are left out of panel b (g16 rule)
Z = 1.959964
B, SEED = 5000, 0    # bootstrap over papers, panel a

PLANNED, ABSENT = ps.BLUE, ps.ORANGE
CHANGE, NOCHANGE = ps.INK2, ps.NEUTRAL      # INK2 under white text: about 8:1


def wilson(k, n, z=Z):
    if n == 0:
        return (float('nan'),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def v_test_txt():
    """Paper-level test of V against the other nodes, from g19 (report_numbers.json vis.node_vs_rest_paper_level)."""
    try:
        t = ps.read_json(ps.DERIVED / 'report_numbers.json')['vis.node_vs_rest_paper_level']['value']
        v = t['V']
        others = [k for k, x in t.items() if k not in ('nodes_tested', 'V') and x['q'] < 0.1]
    except Exception:  # noqa: BLE001
        return ''
    return (f' With papers as units (absent labels shuffled among the changes within each paper, 5000 permutations; '
            f'Benjamini-Hochberg over the {t["nodes_tested"]} nodes), V\'s absent share exceeds that of the other nodes by '
            f'{100 * v["diff"]:.1f} percentage points (95% interval over papers {100 * v["ci"][0]:.1f} to {100 * v["ci"][1]:.1f}, '
            f'q = {v["q"]:.3f}); other nodes with q < 0.1: {", ".join(others) or "none"}. Exploratory.')


def paper_bootstrap(num, den, b=B, seed=SEED):
    """95% percentile interval of sum(num)/sum(den) resampling papers with replacement."""
    num, den = np.asarray(num, float), np.asarray(den, float)
    idx = np.random.default_rng(seed).integers(0, len(num), (b, len(num)))
    s = num[idx].sum(1) / den[idx].sum(1)
    return float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[c] * cb[c] for c in set(a) | set(b)) / (n * n)
    return po, (po - pe) / (1 - pe)


def pct(x, nd=0):
    return f'{100 * x:.{nd}f}%'


def clean(s):
    """Journal names in metrics.json can carry C1 control characters and lower case (e.g. '\\x98The \\x9ccryosphere')."""
    s = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s or '').strip()
    small = {'and', 'of', 'for', 'in', 'the', 'on'}
    return ' '.join(w if (i and w.lower() in small) else w[:1].upper() + w[1:] for i, w in enumerate(s.split()))


def load(tag, labels_path):
    """Rows (key, i, label, agreed, label_a, label_b, node) for every labelled review step, plus the files read."""
    lab = ps.read_json(labels_path)
    rows, files = [], [labels_path]
    for p in lab:
        f = API / tag / f"{p['key']}.json"
        files.append(f)
        c = json.loads(f.read_text())
        rev = next(s for s in c['sequences'] if s['kind'] == 'review')['steps']
        for s in p['steps']:
            node = rev[s['i'] - 1].get('node') if 1 <= s['i'] <= len(rev) else None
            rows.append({'key': p['key'], 'i': s['i'], 'label': s['label'], 'agreed': bool(s['agreed']),
                         'a': s.get('label_a'), 'b': s.get('label_b'), 'node': node})
    return rows, files


def per_paper(rows):
    keys = sorted({r['key'] for r in rows})
    ch = {k: 0 for k in keys}
    ab = {k: 0 for k in keys}
    for r in rows:
        if r['label'] != 'no_change':
            ch[r['key']] += 1
            ab[r['key']] += r['label'] == 'absent'
    return keys, ch, ab


def panel_a(ax, rows, numbers):
    n = len(rows)
    lab = Counter(r['label'] for r in rows)
    ch = n - lab['no_change']
    planned, absent, rev = lab['as_planned'], lab['absent'], lab['as_revision']
    keys, chp, abp = per_paper(rows)
    p = absent / ch
    lo, hi = paper_bootstrap([abp[k] for k in keys], [chp[k] for k in keys])
    numbers.update({'review_steps': n, 'changes': ch, 'no_change': lab['no_change'], 'as_planned': planned,
                    'absent': absent, 'as_revision': rev,
                    'absent_share_of_changes_paper_bootstrap95': [round(p, 4), round(lo, 4), round(hi, 4)],
                    'absent_share_bootstrap': f'{B} resamples of papers, seed {SEED}, percentile interval',
                    'absent_share_of_changes_wilson95_steps_independent': [round(v, 4) for v in wilson(absent, ch)],
                    'as_planned_share_of_changes': round(planned / ch, 4),
                    'as_revision_upper95_changes_rule_of_three': round(3 / ch, 4)})
    h, y1, y2 = 0.42, 0.66, 0.0
    seg = dict(height=h, edgecolor='white', linewidth=0.6)
    ax.barh(y1, ch, left=0, color=CHANGE, **seg)
    ax.barh(y1, lab['no_change'], left=ch, color=NOCHANGE, **seg)
    ax.barh(y2, planned, left=0, color=PLANNED, **seg)
    ax.barh(y2, absent, left=planned, color=ABSENT, **seg)
    # connector band: the changes of row 1 are the whole of row 2
    ax.fill_between([0, ch], [y2 + h / 2] * 2, [y1 - h / 2] * 2, color=ps.GRID, alpha=0.45, linewidth=0, zorder=0)
    ax.text(ch / 2, y1, f'Change to the work  {ch}', ha='center', va='center', color='white', fontsize=ps.FONT)
    ax.text(ch + lab['no_change'] / 2, y1, f'No change  {lab["no_change"]}', ha='center', va='center', color=ps.INK,
            fontsize=ps.FONT)
    ax.text(planned / 2, y2, f'Shown as planned  {planned} ({pct(planned / ch)})', ha='center', va='center',
            color='white', fontsize=ps.FONT)
    ax.annotate(f'Absent  {absent} ({pct(p, 1)}; 95% CI {pct(lo, 1)} to {pct(hi, 1)})',
                xy=(planned + absent / 2, y2 - h / 2), xytext=(planned - 12, y2 - h / 2 - 0.2),
                ha='right', va='top', fontsize=ps.FONT, color=ps.INK,
                arrowprops=dict(arrowstyle='-', color=ps.INK2, lw=0.5, shrinkA=0, shrinkB=0))
    # the zero: a hollow ink marker past the bar end, so it cannot read as a thin segment
    x0 = planned + absent + 9
    ax.plot([x0], [y2], 'o', ms=4, mfc='white', mec=ps.INK, mew=0.7, clip_on=False, zorder=3)
    ax.text(x0 + 8, y2, f'Marked as revision  {rev}', ha='left', va='center', fontsize=ps.FONT, color=ps.INK,
            fontweight='bold')
    ax.set_yticks([y1, y2], [f'Review steps\n(n = {n})', f'Changes\n(n = {ch})'], fontsize=ps.FONT, color=ps.INK)
    ax.tick_params(axis='y', length=0)
    ax.set_xlim(0, n * 1.005)
    ax.set_ylim(-0.6, y1 + h / 2 + 0.03)
    ax.xaxis.set_major_locator(MultipleLocator(100))
    ax.set_xlabel('Number of review steps')
    ax.spines['left'].set_visible(False)
    ps.grid(ax, 'x')


def panel_b(ax, rows, numbers):
    ch = [r for r in rows if r['label'] != 'no_change']
    tot = Counter(r['node'] for r in ch)
    ab = Counter(r['node'] for r in ch if r['label'] == 'absent')
    keep = [k for k in ps.NODES if tot[k] >= MIN_N]
    dropped = {k: tot[k] for k in ps.NODES if 0 < tot[k] < MIN_N}
    stats = {k: wilson(ab[k], tot[k]) for k in keep}
    order = sorted(keep, key=lambda k: (-stats[k][0], -tot[k], ps.NODES.index(k)))
    pooled = sum(ab.values()) / len(ch)
    numbers['by_node_changes'] = {k: tot[k] for k in ps.NODES if tot[k]}
    numbers['by_node_absent'] = {k: ab[k] for k in ps.NODES if tot[k]}
    numbers['by_node_absent_share_wilson95'] = {k: [round(v, 4) for v in stats[k]] for k in order}
    numbers['by_node_interval_excludes_pooled'] = [k for k in order if stats[k][1] > pooled or stats[k][2] < pooled]
    numbers['by_node_comparisons_unadjusted'] = len(order)
    numbers['by_node_dropped_below_min_n'] = dropped
    numbers['changes_with_no_node'] = sum(1 for r in ch if not r['node'])
    for k in numbers['by_node_interval_excludes_pooled']:
        numbers[f'by_node_{k}_papers_with_absent'] = len({r['key'] for r in ch if r['node'] == k and r['label'] == 'absent'})
    ys = list(range(len(order)))[::-1]
    for y, k in zip(ys, order):
        p, lo, hi = stats[k]
        ax.plot([lo, hi], [y, y], color=ps.BLUE, lw=0.8, solid_capstyle='butt')
        ax.plot([p], [y], 'o', color=ps.BLUE, ms=3.2, mec='white', mew=0.4, zorder=3, clip_on=False)
        ax.text(1.02, y, f'{ab[k]}/{tot[k]}', transform=ax.get_yaxis_transform(), ha='left', va='center',
                fontsize=ps.SMALL, color=ps.INK2)
    ax.text(1.02, len(order) - 0.35, 'absent/\nchanges', transform=ax.get_yaxis_transform(), ha='left', va='bottom',
            fontsize=ps.SMALL, color=ps.INK2, linespacing=0.95)
    ax.axvline(pooled, color=ps.INK2, lw=0.6, ls=(0, (3, 2)), zorder=1)
    ax.text(pooled + 0.006, -1.05, f'all changes {pct(pooled, 1)}', ha='left', va='center', fontsize=ps.SMALL,
            color=ps.INK2)
    ax.set_yticks(ys, [f'{k}  {ps.NODE_NAMES[k]}' for k in order], fontsize=ps.SMALL)
    ax.tick_params(axis='y', length=0)
    ax.set_ylim(-1.5, len(order) - 0.4)
    ax.set_xlim(0, 0.4)
    ax.xaxis.set_major_locator(MultipleLocator(0.1))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{100 * v:.0f}%'))
    ax.set_xlabel('Share of changes absent from the published paper')
    ax.spines['left'].set_visible(False)
    ps.grid(ax, 'x')
    return dropped


def panel_c(ax, rows, numbers):
    keys, ch, ab = per_paper(rows)
    rev = Counter(r['key'] for r in rows if r['label'] == 'as_revision')
    keys = [k for k in keys if ch[k] > 0]
    m = len(keys)
    order = sorted(keys, key=lambda k: (-ch[k], -ab[k], k))
    x = np.arange(m)
    a = np.array([ab[k] for k in order])
    c = np.array([ch[k] for k in order])
    seg = dict(width=1.0, edgecolor='white', linewidth=0.6)
    ax.bar(x, a, color=ABSENT, **seg)
    ax.bar(x, c - a, bottom=a, color=PLANNED, **seg)
    any_rev = sum(rev[k] > 0 for k in keys)
    r3 = 3 / m
    with_abs = int((a > 0).sum())
    numbers.update({'papers': len({r['key'] for r in rows}), 'papers_with_changes': m,
                    'changes_per_paper': {'median': float(np.median(c)), 'min': int(c.min()), 'max': int(c.max())},
                    'papers_with_any_absent': with_abs, 'absent_per_paper_max': int(a.max()),
                    'papers_marking_any_revision': any_rev,
                    'papers_marking_any_revision_upper95_rule_of_three': round(r3, 4),
                    'papers_marking_any_revision_upper95_exact_one_sided': round(1 - 0.05 ** (1 / m), 4),
                    'panel_c_order': 'papers sorted by changes, then absent, descending'})
    top = int(c.max())
    ax.text(0.0, 0.995,
            f'No paper marks any change as a revision: {any_rev} of {m}\n'
            f'(one-sided 95% upper bound {pct(r3, 1)}, rule of three 3/{m})\n'
            f'{with_abs} of {m} papers have at least one absent change',
            transform=ax.transAxes, ha='left', va='top', fontsize=ps.SMALL, color=ps.INK, linespacing=1.35)
    ax.legend(handles=[Patch(color=PLANNED, label='Shown as planned'), Patch(color=ABSENT, label='Absent')],
              loc='lower right', bbox_to_anchor=(1.0, (top + 0.4) / (top + 6)), ncol=2, fontsize=ps.SMALL,
              handlelength=1.0, handleheight=0.8, borderaxespad=0.0, columnspacing=1.0)
    ax.set_xlim(-0.8, m - 0.2)
    ax.set_xticks([])
    ax.set_ylim(0, top + 6)
    ax.set_yticks([v for v in range(0, top + 1, 5)])
    ax.spines['left'].set_bounds(0, top)
    ax.set_ylabel('Changes per paper')
    ax.set_xlabel(f'Papers, sorted by number of changes (n = {m})')
    ax.spines['bottom'].set_color(ps.AXIS)
    ps.grid(ax, 'y')


def selection(keys, numbers, inputs):
    """Copernicus papers in round 1 -> open discussion fetched -> valid review coding; journal mix of the labelled set."""
    man = [json.loads(line) for line in MANIFEST.read_text().splitlines() if line.strip()]
    cop = [m['key'] for m in man if str(m.get('doi', '')).startswith('10.5194/')]
    fetched = [k for k in cop if (REVIEW_DIR / k).is_dir()]
    failed = []
    if STATE.is_file():
        st = json.loads(STATE.read_text())
        failed = sorted(k.split(':', 1)[1] for k in (st.get('failed') or {}) if k.startswith('calc1-review:'))
        inputs.append(STATE)
    met = {r['id']: r for r in ps.read_json(METRICS)}
    jour = Counter(clean(met.get(k.removeprefix('g22_'), {}).get('journal')) for k in keys)
    inputs += [MANIFEST, METRICS]
    numbers.update({'round1_copernicus_papers_doi_10.5194': len(cop), 'open_discussion_fetched': len(fetched),
                    'review_codings_failed': failed, 'papers_labelled': len(keys),
                    'journals_of_labelled_papers': dict(jour.most_common())})
    return len(cop), len(fetched), failed, jour


def main():
    numbers, inputs, drawn, rows = {}, [], [], None
    for name, tag, path in ROUNDS:
        if path.is_file() and (API / tag).is_dir():
            r, files = load(tag, path)
            if rows is None:
                rows = r
            inputs += files
            drawn.append(name)
    numbers['rounds_drawn'] = drawn
    numbers['round_2_note'] = 'no open-review coding or visibility labels exist for round 2'

    ps.setup()
    fig = ps.plt.figure(figsize=(ps.DOUBLE, 4.6))
    gs = GridSpec(2, 2, figure=fig, height_ratios=[0.75, 2.3], width_ratios=[1.1, 1.0], hspace=0.45, wspace=0.42)
    axa = fig.add_subplot(gs[0, :])
    axb = fig.add_subplot(gs[1, 0])
    axc = fig.add_subplot(gs[1, 1])
    panel_a(axa, rows, numbers)
    dropped = panel_b(axb, rows, numbers)
    panel_c(axc, rows, numbers)
    ps.panel(axa, 'a', x=-0.085, y=1.04)
    ps.panel(axb, 'b', x=-0.42)
    ps.panel(axc, 'c', x=-0.13)

    agree = sum(r['agreed'] for r in rows)
    po, kap = kappa([r['a'] for r in rows], [r['b'] for r in rows])
    numbers['labeler_agreement'] = [agree, len(rows), round(agree / len(rows), 4)]
    numbers['labeler_agreement_from_label_a_b'] = round(po, 4)
    numbers['labeler_cohen_kappa_4_labels'] = round(kap, 3)
    numbers['label_a_counts'] = dict(Counter(r['a'] for r in rows))
    numbers['label_b_counts'] = dict(Counter(r['b'] for r in rows))

    keys = sorted({r['key'] for r in rows})
    n_cop, n_fetch, failed, jour = selection(keys, numbers, inputs)

    # differences from the g16 summary file
    if G16.is_file():
        g = ps.read_json(G16)
        inputs.append(G16)
        diff = {}
        for k_g, k_n in [('review_steps', 'review_steps'), ('changes', 'changes'), ('no_change_steps', 'no_change'),
                         ('papers', 'papers')]:
            if g.get(k_g) != numbers.get(k_n):
                diff[k_g] = [g.get(k_g), numbers.get(k_n)]
        la = g.get('labeler_agreement')
        if la is not None and abs(la - numbers['labeler_agreement'][2]) > 0.005:
            diff['labeler_agreement'] = [la, numbers['labeler_agreement'][2]]
        for k, v in (g.get('by_node_absent_share') or {}).items():
            mine = numbers['by_node_absent_share_wilson95'].get(k)
            if mine is None or abs(mine[0] - v) > 0.005:
                diff[f'by_node_absent_share.{k}'] = [v, mine[0] if mine else None]
        numbers['g16_differences'] = diff
        numbers['g16_quotes_found_in_published_text'] = g.get('quotes_found_in_published_text')

    m = numbers['papers_with_changes']
    ab = numbers['absent_share_of_changes_paper_bootstrap95']
    drop_txt = ', '.join(f'{k} ({ps.NODE_NAMES[k]}, {v})' for k, v in dropped.items()) or 'none'
    q = numbers.get('g16_quotes_found_in_published_text') or ['?', '?']
    top_j, top_n = jour.most_common(1)[0]
    excl = numbers['by_node_interval_excludes_pooled']
    excl_txt = (', '.join(f'{k} ({ps.NODE_NAMES[k]}, {numbers["by_node_absent"][k]} of {numbers["by_node_changes"][k]}, '
                          f'absences in {numbers[f"by_node_{k}_papers_with_absent"]} papers)' for k in excl)
                if excl else 'none')
    caption = (
        f'Visibility of open-review work in the published paper, round 1. Papers: {m} of the {n_cop} Copernicus papers '
        f'in round 1 (2022); the open discussion was fetched for {n_fetch}, and {n_fetch - m} review codings failed '
        f'validation. {top_n} of the {m} are in {top_j}, so the result mostly describes one journal. The open '
        f'discussion (referee, author, community and editor comments, posted beside a citable discussion preprint) was '
        f'coded as a sequence of review steps by Claude Opus 5.5 (codebook 1.5.0, graph v0.4.2), which also read the '
        f'published paper. Each of the {numbers["review_steps"]} review steps was then labelled against the published '
        f'text (publisher XML) by two model labelers, separate runs of a Claude model inside the Claude Code tool (model '
        f'id not recorded), each without seeing the other\'s labels; a third run settled disagreements. The labelers agreed on {numbers["labeler_agreement"][0]} of {numbers["labeler_agreement"][1]} '
        f'steps ({pct(numbers["labeler_agreement"][2], 1)}; Cohen\'s kappa {numbers["labeler_cohen_kappa_4_labels"]:.2f} '
        f'over the four labels: agreement corrected for the agreement expected by chance from each labeler\'s label '
        f'frequencies, 1 perfect, 0 chance) before adjudication. '
        f'(a) Of {numbers["review_steps"]} review steps, {numbers["changes"]} record a change to the work; '
        f'{numbers["as_planned"]} of these appear in the paper as if planned, {numbers["absent"]} do not appear, and '
        f'{numbers["as_revision"]} are marked as a revision. The interval on the absent share is a 95% percentile '
        f'interval from {B} bootstrap resamples of papers ({pct(ab[1], 1)} to {pct(ab[2], 1)}), because changes cluster '
        f'within papers. Every quote offered as evidence of a shown change exists verbatim in the published text '
        f'({q[0]} of {q[1]}); this checks that the quote exists, not that it shows the change. (b) Share of changes absent from the paper by graph node of the review step, nodes '
        f'with at least {MIN_N} changes (left out: {drop_txt}); points are proportions, bars Wilson 95% intervals that '
        f'treat steps as independent and are not adjusted for the {len(numbers["by_node_absent_share_wilson95"])} '
        f'comparisons; counts at right; the dashed line is the pooled share. Interval excluding the pooled share: '
        f'{excl_txt}.' + v_test_txt() + f' (c) One column per paper, height = changes recorded in its review, split into absent and shown as '
        f'planned; no paper marks any change as a revision ({numbers["papers_marking_any_revision"]} of {m}; one-sided '
        f'95% upper bound by the rule of three, 3/{m} = {pct(3 / m, 1)}). '
        f'Changes per paper: median {numbers["changes_per_paper"]["median"]:.0f}, range '
        f'{numbers["changes_per_paper"]["min"]} to {numbers["changes_per_paper"]["max"]}; '
        f'{numbers["papers_with_any_absent"]} papers have at least one absent change, at most '
        f'{numbers["absent_per_paper_max"]} in one paper. Columns are anonymous and unordered by journal.')
    ps.save(fig, 'fig07_review', inputs=inputs + [ps.DERIVED / 'report_numbers.json'], numbers=numbers, caption=caption)
    print(json.dumps(numbers, indent=1, default=str))
    print(caption)


if __name__ == '__main__':
    main()
