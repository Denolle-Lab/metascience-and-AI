"""Figure 16: what the open review record adds to the paper's account of its own workflow (reconstruction, descriptive).

Papers give the paper's account of the work, not its chronology, and leave out loops (PI direction, October 28, 2026).
For Copernicus papers with an open discussion, part of what is left out is on the record: referee comments, author
responses and the discussion preprint. tools/roadmap/g34_reconstruction.py `features` stacks four layers on each paper
(reported, review-induced, disclosed, revised; preregistration/reconstruction.md) and counts loops per layer. This
figure draws those features for the three sets of the frozen plan. No outcome is read: no advance coding and no
citation metric (the plan's `test` reads them, after the PI decides the cop22 prefix is final).

Panels
  a  papers per set at each layer condition of the plan (candidates, C0 open discussion, C1 valid inquiry coding,
     C2 valid review coding with a referee-triggered step, C3 review inputs unchanged on disk, C4 preprint and published
     text found with >= 80% of reported steps located; complete = C0 to C4). Advance pilot papers are excluded upstream.
  b  per complete paper, counts per layer: loops the paper reports (paper_returns: returns to an earlier node in the
     final-paper walk), review loops (review steps by a referee, editor or commenter, not declined), disclosed
     tried-and-dropped attempts, outside-only loops (tried-and-dropped or added-for-review items absent from the final
     paper, counted as distinct events), claims narrowed at review. Points jittered, bar = median, set by colour.
  c  share of complete papers with at least one of: a reported loop, an outside-only loop, a disclosed tried-and-dropped
     attempt, an added-for-review item absent from the final paper; Wilson 95% intervals, by set.

Definitions are the plan's (preregistration/reconstruction.md, Features). The disclosure statuses (present, partly,
absent in the final paper) are the review coder's judgments (claude-opus-5-5, review addendum 1.0.0), not checked by a
person; quotes are checked against the texts (rule `item`).

Inputs   private/data/roadmap/derived/reconstruction/features.json (g34 features)
         private/analysis/codings/api/{calc1,r2,cop22}-review-v2/<key>.json (disclosure kinds and statuses, panel c)
Outputs  private/data/roadmap/figures/paper/fig16_reconstruction.{pdf,png,json}
Run:     python tools/roadmap/g34_reconstruction.py features && python tools/roadmap/figures/fig16_reconstruction.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402

API = ps.PRIVATE / 'analysis' / 'codings' / 'api'
FEATURES = ps.DERIVED / 'reconstruction' / 'features.json'
SETS = [('round1', 'Round 1', 'calc1-review-v2', ps.BLUE), ('round2', 'Round 2', 'r2-review-v2', ps.ORANGE),
        ('cop22', '2022 draw', 'cop22-review-v2', ps.AQUA)]
STAGES = [('candidates', 'All'), ('C0_open_discussion', 'C0'), ('C1_reported', 'C1'), ('C2_review', 'C2'),
          ('C3_disclosed', 'C3'), ('C4_revised', 'C4'), ('complete_C0_C4', 'Done')]
COUNTS = [('paper_returns', 'Reported\nloops'), ('review_loops', 'Review\nloops'), ('tried_dropped', 'Tried and\ndropped'),
          ('outside_only_loops', 'Outside-\nonly loops'), ('claim_narrowed', 'Claims\nnarrowed')]
Z = 1.959964


def wilson(k, n):
    if n == 0:
        return float('nan'), float('nan'), float('nan')
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return p, c - h, c + h


def main():
    F = json.loads(FEATURES.read_text())
    summ, papers = F['data']['summary']['by_set'], F['data']['papers']
    numbers = {'features_provenance': F.get('_provenance', {}).get('commit'), 'funnel': {}, 'counts': {}, 'shares': {}}

    W, H = ps.DOUBLE, 2.75
    fig, ax0 = ps.figure(W, H)
    ax0.remove()
    bot, top = 0.42 / H, 1 - 0.42 / H      # room for tick labels below and the legend row above
    axa = fig.add_axes([0.45 / W, bot, 1.45 / W, top - bot])
    axb = fig.add_axes([2.45 / W, bot, 2.35 / W, top - bot])
    axc = fig.add_axes([6.0 / W, bot, 1.15 / W, top - bot])

    # (a) layer funnel
    xs = np.arange(len(STAGES))
    for name, label, _, col in SETS:
        ys = [summ[name][k] for k, _ in STAGES]
        numbers['funnel'][name] = dict(zip([k for k, _ in STAGES], ys))
        axa.plot(xs, ys, color=col, marker='o', markersize=3, linewidth=1.0, zorder=3)
        axa.text(xs[-1] + 0.3, ys[-1], str(ys[-1]), color=ps.INK, fontsize=ps.SMALL, va='center')
    axa.set_xticks(xs, [s for _, s in STAGES], fontsize=ps.SMALL)
    axa.set_xlabel('Layer condition met')
    axa.set_ylabel('Papers')
    axa.set_ylim(0, 70)
    axa.set_xlim(-0.4, len(STAGES) - 0.1)
    ps.grid(axa, 'y')
    ps.panel(axa, 'a', x=-0.3)

    # (b) per-paper counts per layer, complete papers
    rng = np.random.default_rng(0)
    off = {'round1': -0.24, 'round2': 0.0, 'cop22': 0.24}
    for name, label, _, col in SETS:
        rows = [p['features'] for p in papers.values() if p['set'] == name and p['complete_C0_C4'] and not p['excluded_pilot']]
        numbers['counts'][name] = {'n': len(rows)}
        for i, (k, _) in enumerate(COUNTS):
            v = np.array([r[k] for r in rows], dtype=float)
            x = i + off[name]
            axb.scatter(x + rng.uniform(-0.09, 0.09, len(v)), v, s=2.2, color=col, alpha=0.5, linewidths=0, zorder=2)
            med = float(np.median(v))
            axb.plot([x - 0.11, x + 0.11], [med, med], color=ps.INK, linewidth=1.4, zorder=4, solid_capstyle='butt')
            numbers['counts'][name][k] = {'median': med, 'mean': round(float(v.mean()), 3), 'max': float(v.max()),
                                          'q1': float(np.percentile(v, 25)), 'q3': float(np.percentile(v, 75))}
    axb.set_xticks(range(len(COUNTS)), [s for _, s in COUNTS], fontsize=ps.SMALL)
    axb.set_ylabel('Count per paper (complete papers)')
    axb.set_ylim(-0.6, None)
    axb.yaxis.set_major_locator(MultipleLocator(5))
    ps.grid(axb, 'y')
    ps.panel(axb, 'b', x=-0.12)
    fig.legend(handles=[Line2D([], [], color=c, marker='o', linestyle='none', markersize=3.2,
                               label=f'{l} (complete n = {numbers["counts"][n]["n"]})') for n, l, _, c in SETS]
               + [Line2D([], [], color=ps.INK, linewidth=1.4, label='Median, panel b')],
               loc='upper left', bbox_to_anchor=(0.45 / W, 1 - 0.02 / H), ncol=4, fontsize=ps.SMALL, handletextpad=0.3,
               columnspacing=1.6, borderaxespad=0)

    # (c) share of papers with at least one event
    cats = [('reported', 'Reported loop'), ('outside_only', 'Outside-only loop'), ('tried_dropped', 'Tried and dropped'),
            ('afr_absent', 'Added for review,\nabsent from paper')]
    yoff = {'round1': 0.22, 'round2': 0.0, 'cop22': -0.22}
    for name, label, tag, col in SETS:
        keys = [k for k, p in papers.items() if p['set'] == name and p['complete_C0_C4'] and not p['excluded_pilot']]
        hit = {c: 0 for c, _ in cats}
        for k in keys:
            f = papers[k]['features']
            d = json.loads((API / tag / f'{k}.json').read_text())
            hit['reported'] += f['paper_returns'] > 0
            hit['outside_only'] += f['outside_only_loops'] > 0
            hit['tried_dropped'] += f['tried_dropped'] > 0
            hit['afr_absent'] += any(x.get('kind') == 'added_for_review' and x.get('final_paper_status') == 'absent'
                                     for x in d.get('disclosures', []))
        numbers['shares'][name] = {}
        for j, (c, _) in enumerate(cats):
            p, lo, hi = wilson(hit[c], len(keys))
            y = len(cats) - 1 - j + yoff[name]
            axc.plot([lo, hi], [y, y], color=col, linewidth=1.0, zorder=2)
            axc.plot(p, y, 'o', color=col, markersize=3.2, zorder=3)
            numbers['shares'][name][c] = {'k': hit[c], 'n': len(keys), 'share': round(p, 3), 'lo': round(lo, 3), 'hi': round(hi, 3)}
    axc.set_yticks(range(len(cats)), [s for _, s in cats][::-1], fontsize=ps.SMALL)
    axc.set_xlim(0, 1)
    axc.set_xticks([0, 0.25, 0.5, 0.75, 1], ['0', '25', '50', '75', '100'])
    axc.set_xlabel('Papers with at least one (%)')
    axc.set_ylim(-0.5, len(cats) - 0.5)
    ps.grid(axc, 'x')
    ps.panel(axc, 'c', x=-0.95)

    fig.text(0.45 / W, 0.01 / H, 'Source: g34_reconstruction.py features (private/data/roadmap/derived/reconstruction/features.json) and the '
             'review codings (claude-opus-5-5, review addendum 1.0.0); no outcome read. Script: tools/roadmap/figures/fig16_reconstruction.py.',
             fontsize=ps.SMALL - 1, color=ps.INK2, ha='left', va='bottom', transform=fig.transFigure)

    n = {s: numbers['counts'][s]['n'] for s, *_ in SETS}
    sh = numbers['shares']
    caption = (
        "What the open review record adds to the paper's account of its workflow, Copernicus papers with an open discussion. "
        "(a) Papers per set at each layer condition of the frozen reconstruction plan (All: candidates; C0 open discussion; "
        "C1 valid inquiry coding; C2 valid review coding with a referee-triggered step; C3 review inputs unchanged on disk; "
        "C4 preprint and published text found, >= 80% of reported steps located; Done: C0 to C4). "
        f"Complete papers: {n['round1']} (round 1), "
        f"{n['round2']} (round 2), {n['cop22']} (2022 draw, the first 53 of the frozen draw order). "
        "(b) Per complete paper: returns to an earlier node in the walk the paper reports; review loops (steps a referee, editor "
        "or commenter triggered, not declined); attempts the authors disclose as tried and dropped; outside-only loops "
        "(tried-and-dropped or added-for-review items absent from the final paper, distinct events); claims narrowed at review. "
        "Bars: medians. (c) Share of complete papers with at least one event of each kind, Wilson 95% intervals. "
        f"Round 2 has no added-for-review item marked absent ({sh['round2']['afr_absent']['k']} of {sh['round2']['afr_absent']['n']} papers), "
        f"against {sh['round1']['afr_absent']['k']} of {sh['round1']['afr_absent']['n']} and {sh['cop22']['afr_absent']['k']} of "
        f"{sh['cop22']['afr_absent']['n']} in the other sets; journal mix explains part of the gap, not all of it, and the statuses are "
        "model judgments not yet checked by a person. No outcome is read here.")
    ps.save(fig, 'fig16_reconstruction', inputs=[FEATURES, *[API / t for _, _, t, _ in SETS]], numbers=numbers, caption=caption)


if __name__ == '__main__':
    main()
