"""Figure 4: what the coded workflows look like (roadmap Phase 0 descriptives, paper figure).

Panels (final_paper sequence of each coding, codebook 1.5.0, graph v0.4.2)
  a  share of papers that use each node at least once, nodes in graph order N..R, with 95% percentile bootstrap
     intervals (2000 resamples over papers, seed 2026); a Wilson 95% interval is recorded for every node as well,
     because the percentile interval has zero width when a node is in every paper (K)
  b  coded steps per paper (len of the final_paper steps, no run collapsing; the g17 'num:steps' feature), histogram
     with the median marked; the run-collapsed median (tools/check_coding.seq, the g13 'steps_median') is recorded
  c  entry state composition (entry.state), one part-to-whole bar per round; legend labels carry the counts
  d  claim status at the end of the paper (end.claim_status), one bar per round; the number and share whose outcome
     is 'contradicted' (end.outcome) are written beside each bar
In (c) and (d) a category with zero papers in every round drawn is left out of the bar, the legend and the caption.

Rounds: round 1 is always drawn (tag calc1, first coding; papers in derived/calc1/manifest.jsonl). Round 2 (tag r2,
papers in derived/r2calc/manifest.jsonl) is added as a second series when that coding folder holds at least one valid
coding. The test-retest second run of the gold papers (tag gold-r2) is not used; its size is recorded for the caption.
Codings that fail tools/check_coding.py validate() are left out, as in g13 and g17, and named in the provenance.

Inputs
  private/analysis/codings/api/calc1/*.json            round-1 model codings (claude-opus-5-5, Batch API)
  private/analysis/codings/api/r2/*.json               round-2 model codings, when present
  private/analysis/codings/api/gold-r2/*.json          counted only (second codings excluded from the figure)
  private/data/roadmap/derived/calc1/manifest.jsonl    the 525 eligible round-1 papers
  private/data/roadmap/derived/r2calc/manifest.jsonl   the 222 eligible round-2 papers
  private/data/roadmap/derived/calc1/results.json      g13 corpus values, read only to record differences

Outputs  private/data/roadmap/figures/paper/fig04_workflows.{pdf,png,json}
Run:     python tools/roadmap/figures/fig04_workflows.py
"""
import json
import math
import statistics as st
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator, MultipleLocator
from matplotlib.transforms import ScaledTranslation

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402

sys.path.insert(0, str(ps.ROOT / 'tools'))
from check_coding import seq, validate  # noqa: E402

API = ps.PRIVATE / 'analysis' / 'codings' / 'api'
ROUNDS = [('Round 1', 'calc1', ps.DERIVED / 'calc1' / 'manifest.jsonl'),
          ('Round 2', 'r2', ps.DERIVED / 'r2calc' / 'manifest.jsonl')]
RETEST_TAG = 'gold-r2'
RCOL = [ps.BLUE, ps.ORANGE]
B, SEED = 2000, 2026
WIDTH, HEIGHT = ps.DOUBLE, 4.6

# part-to-whole categories: up to five named hues in schema order, the rest pooled as "other" in neutral grey.
# Each category keeps its colour slot even when another category is dropped for having no papers.
ENTRY = [('problem', 'Problem'), ('capability', 'Capability'), ('hypothesis', 'Hypothesis'),
         ('anomaly', 'Anomaly'), ('challenged_result', 'Challenged result')]
ENTRY_OTHER = ('data_without_theory', 'external_goal')
CLAIM = [('confirmed', 'Confirmed'), ('best_explanation', 'Best explanation'),
         ('regularity_in_range', 'Regularity in range'), ('estimate_with_resolution', 'Estimate with resolution'),
         ('capability_characterized', 'Capability characterized')]
CLAIM_OTHER = ('forecast_skill', 'none')
CAT_COL = [ps.BLUE, ps.ORANGE, ps.AQUA, ps.YELLOW, ps.MAGENTA, ps.NEUTRAL]


def load(tag, manifest):
    """Valid codings of the papers in the manifest; returns (codings, files read, invalid file stems with reasons)."""
    d = API / tag
    if not d.is_dir() or not manifest.is_file():
        return [], [], {}
    keys = {json.loads(l)['key'] for l in manifest.read_text().splitlines() if l.strip()}
    out, files, bad = [], sorted(d.glob('*.json')), {}
    for f in files:
        try:
            c = json.loads(f.read_text())
        except Exception as e:  # noqa: BLE001
            bad[f.stem] = [f'unreadable: {e}']
            continue
        errs = validate(c)
        if errs:
            bad[f.stem] = errs
            continue
        if c.get('key') in keys:
            out.append(c)
    return out, files, bad


def final_steps(c):
    return next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps']


def boot_shares(M, rng):
    """M: papers x nodes 0/1. Point share and 95% percentile bootstrap interval per column."""
    n = M.shape[0]
    idx = rng.integers(0, n, size=(B, n))
    bs = M[idx].mean(axis=1)                      # B x nodes
    lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
    return M.mean(axis=0), lo, hi


def wilson(x, n, z=1.959964):
    p = x / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def composition(values, cats, other):
    """Counts per named category plus the pooled 'Other'; returns (counts list, n, raw counts, unexpected values)."""
    cnt = Counter(values)
    counts = [cnt.get(k, 0) for k, _ in cats] + [sum(cnt.get(k, 0) for k in other)]
    unknown = sorted(set(cnt) - {k for k, _ in cats} - set(other))
    return counts, len(values), dict(cnt), unknown


def stacked(ax, rows, labels, colours, ncol=3):
    """Horizontal part-to-whole bars. rows = [(row label, counts, n)], counts aligned with labels and colours.
    Categories with zero papers in every row are dropped. Percent written in segments >= 7%; every legend label
    carries the count(s), so thin segments can be read without matching colours."""
    keep = [j for j in range(len(labels)) if any(cnt[j] > 0 for _, cnt, _ in rows)]
    for i, (_, cnt, n) in enumerate(rows):
        left = 0.0
        for j in keep:
            w = cnt[j] / n
            if w > 0:
                ax.barh(i, w, left=left, height=0.62, color=colours[j], edgecolor='white', linewidth=0.6)
                if w >= 0.07:
                    ax.text(left + w / 2, i, f'{100 * w:.0f}%', ha='center', va='center', fontsize=ps.SMALL,
                            color=ps.INK)
            left += w
    ax.set_yticks(range(len(rows)), [f'{lab}\n(n = {n})' for lab, _, n in rows])
    ax.set_ylim(len(rows) - 0.45, -0.55)
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ['0', '0.25', '0.5', '0.75', '1'])
    ax.tick_params(axis='y', length=0)
    ax.spines['left'].set_visible(False)
    handles = [Patch(facecolor=colours[j], edgecolor='white', linewidth=0.6,
                     label=f'{labels[j]} ({"; ".join(str(cnt[j]) for _, cnt, _ in rows)})') for j in keep]
    # legend a fixed distance (0.33 in) below the axes, clear of tick labels and axis label at any axes height
    off = ax.transAxes + ScaledTranslation(0, -0.33, ax.figure.dpi_scale_trans)
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(-0.01, 0), bbox_transform=off, ncol=ncol,
              handlelength=1.0, handleheight=0.8, columnspacing=0.8, handletextpad=0.35, borderaxespad=0,
              labelspacing=0.3)
    return [labels[j] for j in range(len(labels)) if j not in keep]


def main():
    rng = np.random.default_rng(SEED)
    data, inputs, numbers = [], [], {}
    for name, tag, man in ROUNDS:
        cs, files, bad = load(tag, man)
        if not cs:
            continue
        data.append((name, tag, cs))
        inputs += [man, *files]
        numbers[f'{tag}_coding_files'] = len(files)
        numbers[f'{tag}_codings_failing_validation'] = len(bad)
        numbers[f'{tag}_invalid_files'] = bad
        numbers[f'{tag}_papers'] = len(cs)
        numbers[f'{tag}_eligible_in_manifest'] = sum(1 for l in man.read_text().splitlines() if l.strip())
    numbers['rounds_drawn'] = [t for _, t, _ in data]

    # second codings of round-1 papers (test-retest), counted for the caption, not drawn
    keys1 = {c['key'] for c in data[0][2]}
    rt_files = sorted((API / RETEST_TAG).glob('*.json')) if (API / RETEST_TAG).is_dir() else []
    rt = []
    for f in rt_files:
        try:
            c = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            continue
        if isinstance(c, dict) and not validate(c) and c.get('key') in keys1:
            rt.append(c['key'])
    inputs += rt_files
    numbers[f'{RETEST_TAG}_second_codings_of_drawn_round1_papers_excluded'] = len(rt)

    k = len(data)
    fig = ps.figure(WIDTH, HEIGHT + (0.4 if k > 1 else 0.0))[0]
    fig.clf()
    # right column: (b), then (c) and (d) whose height grows with the number of rounds; the short rows hold legends
    hcd = 0.2 + 0.2 * k
    ncol = 3 if k == 1 else 2          # two rounds lengthen every legend label by '; n'
    leg = 0.38 if k == 1 else 0.55
    gs = GridSpec(6, 2, figure=fig, width_ratios=[1.0, 1.42], height_ratios=[1.5, 0.3, hcd, leg + 0.12, hcd, leg],
                  wspace=0.3, hspace=0.62, left=0.155, right=0.885, top=0.95 if k == 1 else 0.93, bottom=0.085)
    axa = fig.add_subplot(gs[:, 0])
    axb, axc, axd = fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[2, 1]), fig.add_subplot(gs[4, 1])

    # ---- (a) node use with bootstrap intervals ----
    h = 0.8 / k
    y = np.arange(len(ps.NODES))
    for r, (name, tag, cs) in enumerate(data):
        M = np.array([[x in {s['node'] for s in final_steps(c)} for x in ps.NODES] for c in cs], float)
        p, lo, hi = boot_shares(M, rng)
        yy = y - 0.4 + h * (r + 0.5)
        axa.barh(yy, p, height=h * 0.92, color=RCOL[r], label=f'{name} (n = {len(cs)})')
        axa.errorbar(p, yy, xerr=[p - lo, hi - p], fmt='none', ecolor=ps.INK2, elinewidth=0.6, capsize=0)
        numbers[f'{tag}_node_share'] = {x: [round(float(a), 3), round(float(b), 3), round(float(c), 3)]
                                        for x, a, b, c in zip(ps.NODES, p, lo, hi)}
        numbers[f'{tag}_node_count'] = {x: int(v) for x, v in zip(ps.NODES, M.sum(axis=0))}
        numbers[f'{tag}_node_share_wilson95'] = {x: [round(v, 3) for v in wilson(int(v), len(cs))]
                                                 for x, v in zip(ps.NODES, M.sum(axis=0))}
        numbers[f'{tag}_nodes_in_every_paper'] = [x for x, v in zip(ps.NODES, M.sum(axis=0)) if v == len(cs)]
    axa.set_yticks(y, [f'{x}  {ps.NODE_NAMES[x]}' for x in ps.NODES])
    axa.set_ylim(len(ps.NODES) - 0.5, -0.5)
    axa.set_xlim(0, 1.0)
    axa.set_xticks([0, 0.25, 0.5, 0.75, 1], ['0', '0.25', '0.5', '0.75', '1'])
    axa.set_xlabel('share of papers using the node\n(95% bootstrap interval)')
    axa.tick_params(axis='y', length=0)
    axa.spines['left'].set_visible(False)
    ps.grid(axa, 'x')
    if k > 1:
        axa.legend(loc='lower left', bbox_to_anchor=(0, 1.0), ncol=k, handlelength=1.0, borderaxespad=0.2)
    # panel letter at the left edge of the longest node label (about 0.95 in left of the axes)
    lab_a = ScaledTranslation(-0.98, 0, fig.dpi_scale_trans)
    axa.text(0, 1.0 + (0.04 if k > 1 else 0.012), '(a)', transform=axa.transAxes + lab_a, fontsize=ps.LABEL,
             fontweight='bold', va='bottom', ha='left')

    # ---- (b) steps per paper ----
    allsteps = [len(final_steps(c)) for _, _, cs in data for c in cs]
    edges = np.arange(min(allsteps) - 0.5, max(allsteps) + 1.5, 1.0)
    ymax = 0
    for r, (name, tag, cs) in enumerate(data):
        L = [len(final_steps(c)) for c in cs]
        w = np.ones(len(L)) / len(L)
        if r == 0:
            hv, _, _ = axb.hist(L, bins=edges, weights=w, color=RCOL[r], edgecolor='white', linewidth=0.6,
                                label=f'{name} (n = {len(cs)})')
        else:
            hv, _, _ = axb.hist(L, bins=edges, weights=w, histtype='step', color=RCOL[r], linewidth=1.0,
                                label=f'{name} (n = {len(cs)})')
        ymax = max(ymax, hv.max())
        m = st.median(L)
        numbers[f'{tag}_steps'] = {'median': m, 'min': min(L), 'max': max(L),
                                   'q1': float(np.percentile(L, 25)), 'q3': float(np.percentile(L, 75)),
                                   'hist_counts': {int(e + 0.5): int(round(v * len(L))) for e, v in zip(edges[:-1], hv)}}
        numbers[f'{tag}_steps_run_collapsed_median'] = st.median(len(seq(c, 'node')) for c in cs)
    top = ymax * (1.32 if k == 1 else 1.55)
    meds = [numbers[f'{tag}_steps']['median'] for _, tag, _ in data]
    for r, (name, tag, cs) in enumerate(data):
        m = meds[r]
        yl = top * (0.95 - 0.13 * r)
        # the largest median is labelled to the right of its line, the others to the left, so labels never cross
        right = m == max(meds) and (r == 0 or meds.count(m) == 1)
        axb.plot([m, m], [0, yl], color=ps.INK if r == 0 else ps.INK2, linewidth=0.8,
                 linestyle='-' if r == 0 else (0, (3, 1.5)))
        axb.text(m + (0.4 if right else -0.4), yl, f'median {m:g}' + (f' ({name.lower()})' if k > 1 else ''),
                 fontsize=ps.SMALL, color=ps.INK, va='top', ha='left' if right else 'right')
    axb.set_ylim(0, top)
    axb.set_xlim(edges[0], edges[-1])
    axb.xaxis.set_major_locator(MultipleLocator(5))
    axb.yaxis.set_major_locator(MaxNLocator(nbins=4, steps=[1, 2, 5, 10]))
    axb.set_xlabel('coded steps per paper (final-paper sequence)')
    axb.set_ylabel('share of papers')
    ps.grid(axb, 'y')
    if k > 1:
        axb.legend(loc='lower right', bbox_to_anchor=(1.0, 1.0), ncol=k, handlelength=1.0, borderaxespad=0.2)
    else:
        axb.text(0.99, 0.95, f'n = {len(data[0][2])}', transform=axb.transAxes, fontsize=ps.SMALL, color=ps.INK2,
                 va='top', ha='right')
    ps.panel(axb, 'b', x=-0.135, y=1.02 if k == 1 else 1.07)

    # ---- (c) entry state, (d) claim status ----
    rows_c, rows_d = [], []
    for name, tag, cs in data:
        cnt, n, raw, unk = composition([c['entry']['state'] for c in cs], ENTRY, ENTRY_OTHER)
        rows_c.append((name, cnt, n))
        numbers[f'{tag}_entry_state_counts'] = raw
        if unk:
            numbers[f'{tag}_entry_state_unexpected'] = unk
        cnt, n, raw, unk = composition([c['end']['claim_status'] for c in cs], CLAIM, CLAIM_OTHER)
        rows_d.append((name, cnt, n))
        numbers[f'{tag}_claim_status_counts'] = raw
        if unk:
            numbers[f'{tag}_claim_status_unexpected'] = unk
        numbers[f'{tag}_outcome_counts'] = dict(Counter(c['end']['outcome'] for c in cs))
    drop_c = stacked(axc, rows_c, [l for _, l in ENTRY] + ['Other'], CAT_COL, ncol)
    drop_d = stacked(axd, rows_d, [l for _, l in CLAIM] + ['Other'], CAT_COL, ncol)
    numbers['entry_categories_dropped_zero_papers'] = drop_c
    numbers['claim_categories_dropped_zero_papers'] = drop_d
    for i, (name, tag, cs) in enumerate(data):
        nc = numbers[f'{tag}_outcome_counts'].get('contradicted', 0)
        numbers[f'{tag}_contradicted'] = {'count': nc, 'percent': round(100 * nc / len(cs), 1)}
        axd.text(1.02, i, f'{nc} contradicted\n({100 * nc / len(cs):.0f}%)', fontsize=ps.SMALL, color=ps.INK2,
                 va='center', ha='left', transform=axd.get_yaxis_transform())
    axc.set_xlabel('share of papers, by entry state')
    axd.set_xlabel('share of papers, by claim status at the end')
    ps.panel(axc, 'c', x=-0.135, y=1.08)
    ps.panel(axd, 'd', x=-0.135, y=1.08)

    # ---- cross-check against g13 results.json (round 1), recorded, not drawn ----
    res_p = ps.DERIVED / 'calc1' / 'results.json'
    if res_p.is_file():
        corp = ps.read_json(res_p)['corpus']
        inputs.append(res_p)
        numbers['g13_results_papers_coded'] = corp.get('papers_coded')
        numbers['g13_results_steps_median_run_collapsed_nodes'] = corp.get('steps_median')

    # ---- caption ----
    def other_txt(cats_other, rows, label):
        tot = [cnt[-1] for _, cnt, _ in rows]
        if not any(tot):
            return ''
        per = ' and '.join(f'{k_.replace("_", " ")} ('
                           + '; '.join(str(numbers[f"{t}_{label}_counts"].get(k_, 0)) for _, t, _ in data) + ')'
                           for k_ in cats_other)
        return f' Other pools {per}.'

    def dropped_txt(dropped, cats, cats_other):
        names = [l.lower() for l in dropped if l != 'Other']
        if 'Other' in dropped:
            names += [k_.replace('_', ' ') for k_ in cats_other]
        return f' No paper was coded {" or ".join(names)}; these categories are not shown.' if names else ''

    r1 = data[0]
    inv1 = numbers['calc1_invalid_files']
    why = sorted({e.split(': ', 1)[-1] for v in inv1.values() for e in v})
    rounds_txt = (f'round 1 (n = {numbers["calc1_papers"]} of {numbers["calc1_eligible_in_manifest"]} eligible papers '
                  'with a valid coding; first coding)')
    if k > 1:
        rounds_txt += (f' and round 2 (n = {numbers["r2_papers"]} of {numbers["r2_eligible_in_manifest"]} eligible '
                       'papers with a valid coding; tag r2)')
    excl = (f'{numbers["calc1_codings_failing_validation"]} of {numbers["calc1_coding_files"]} round-1 coding files '
            f'fail the format check of tools/check_coding.py ({"; ".join(sorted(set(why)))}) and are excluded'
            if inv1 else 'no round-1 coding file fails the format check')
    if k > 1:
        excl += (f', as are {numbers["r2_codings_failing_validation"]} of {numbers["r2_coding_files"]} round-2 files')
    every = numbers['calc1_nodes_in_every_paper']
    n1 = numbers['calc1_papers']
    zero_w = ''
    if every:
        wl = numbers['calc1_node_share_wilson95'][every[0]][0]
        zero_w = (f' {", ".join(every)} ({", ".join(ps.NODE_NAMES[x] for x in every)}) is coded in all {n1} round-1 '
                  f'papers, so its percentile interval has zero width; a Wilson 95% interval for {n1} of {n1} is '
                  f'{wl:.3f} to 1.')
    med_txt = ', '.join(f'{numbers[f"{t}_steps"]["median"]:g}' for _, t, _ in data)
    rc_txt = ', '.join(f'{numbers[f"{t}_steps_run_collapsed_median"]:g}' for _, t, _ in data)
    contra = '; '.join(f'{numbers[f"{t}_contradicted"]["count"]}, {numbers[f"{t}_contradicted"]["percent"]:.0f}%'
                       for _, t, _ in data)
    cnt_txt = 'the number of papers in each category' if k == 1 else 'the number of papers in each category (round 1; round 2)'
    caption = (
        f'Coded research workflows of earth-science papers published in 2022, {rounds_txt}. Each paper\'s full text '
        'was coded once by a language model (Claude Opus 5.5, sent as asynchronous batch requests) onto graph v0.4.2 of '
        'the modes of inquiry with codebook 1.5.0. A valid coding passes a format check (fields, allowed values, step '
        'order, quotes of 25 words or fewer), which says nothing about accuracy. The second coding of '
        f'{numbers[f"{RETEST_TAG}_second_codings_of_drawn_round1_papers_excluded"]} gold-set papers (run-to-run test) is '
        f'not used. {excl[0].upper() + excl[1:]}. All measures use the '
        'final-paper sequence. (a) Share of papers that use each node at least once, nodes in graph order; error bars '
        f'are 95% percentile bootstrap intervals over papers (2000 resamples, seed 2026).{zero_w} (b) Number of coded '
        'steps per paper, steps as coded with consecutive repeats of a node not merged; the vertical line marks the '
        f'median ({med_txt}). Merging consecutive repeats of a node gives a median of {rc_txt}.'
        f' (c) Entry state of the paper. (d) Claim status at the end of the paper; '
        'the text at right gives the number and share of papers whose outcome was coded as contradicted '
        f'({contra}). In (c) and (d), legend labels give {cnt_txt} and percentages are written in '
        'segments of 7% or more.'
        + other_txt(ENTRY_OTHER, rows_c, 'entry_state').replace('Other pools', 'In (c), Other pools')
        + other_txt(CLAIM_OTHER, rows_d, 'claim_status').replace('Other pools', 'In (d), Other pools')
        + dropped_txt(drop_d, CLAIM, CLAIM_OTHER) + dropped_txt(drop_c, ENTRY, ENTRY_OTHER)
        + ' Paper identifiers and file paths are in the provenance fields of this file.')
    ps.save(fig, 'fig04_workflows', inputs=inputs, numbers=numbers, caption=caption)
    print(caption)
    return r1


if __name__ == '__main__':
    main()
