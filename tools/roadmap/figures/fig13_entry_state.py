"""Figure 13: the entry state under audit. Does the coded entry state record what started the work, or how the paper
frames its start (the introduction's gap statement)?

Terms (CODEBOOK.md 1.5.0, sections 2 and 8; tools/roadmap/g21_entry_state.py docstring)
  entry state      entry.state, one label per paper for how the research began: problem, capability, anomaly,
                   challenged_result, hypothesis, data_without_theory, external_goal.
  entry node       entry.node, the graph v0.4.2 letter where the paper enters (Q question, N new capability, O observe ...).
  walk             the steps of the final_paper sequence, in document order.
  batch coder      the model coder of record (claude-opus-5-5, Batch API), tags calc1 (round 1) and r2 (round 2).
  blind coders     A and B, two Claude agents of the same model family that re-coded the entry of 60 sampled round-1
                   papers from the full text without seeing the batch label or each other (blind_audit.json).
  consensus        the value A and B both gave; 'split' when they differ.
  operational start  what the study could not have begun without (one of 9 classes, g21 OPERATIONAL), recorded by A and B.
  gap statement    the coder judged its own entry quote a gap sentence (Swales 1990 move 2: names what is unknown,
                   unclear, debated or lacking).
  revisit          the entry node appears again later in the run-collapsed walk, after at least one other node (g21 step 4).

Panels
  (a) entry-state shares: batch coder over every valid coding of each round (calc1, and r2 when present), and the
      blind consensus weighted back to all of round 1 (stratified sample, weight = papers with that batch state /
      sampled papers with it), with the stratified bootstrap 95% interval from g21 (2000 draws).
  (b) agreement on entry state and entry node for four pairs of codings: observed agreement against the agreement
      expected by chance (Krippendorff), and Krippendorff's alpha (nominal) with its 95% bootstrap interval over papers.
  (c) audit sample, one part-to-whole bar per batch state: the operational start both blind coders agreed on.
  (d) share of each blind coder's entry quotes that the coder flagged as a gap statement, by the state that coder gave,
      with Wilson 95% intervals.
  (e) batch codings of round 1 (and round 2 when present), by entry state: share whose walk opens at the entry node,
      and share whose walk returns to the entry node after another node, with Wilson 95% intervals. Recomputed here
      from the codings (read only) with g21's own rules and checked against entry_state.json.

Colour groups in (c) are this figure's choice (OP_GROUPS below); g21's START_GROUP folds the first three into one
'concrete object' group.

Inputs
  private/data/roadmap/derived/entry/entry_state.json   g21_entry_state.py output (steps 1-9), the numbers of record
  private/analysis/codings/api/calc1/*.json, r2/*.json  valid codings, read only, for panel (e)
Outputs  private/data/roadmap/figures/paper/fig13_entry_state.{pdf,png,json}
Run:     python tools/roadmap/g21_entry_state.py   (first, so the codings and the json agree)
         python tools/roadmap/figures/fig13_entry_state.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402
from paperstyle import DERIVED, ROOT  # noqa: E402
import g21_entry_state as g21  # noqa: E402
from check_coding import runs  # noqa: E402

SRC = DERIVED / 'entry' / 'entry_state.json'
API = ROOT / 'private' / 'analysis' / 'codings' / 'api'
STATES = g21.STATES
SNAME = {'problem': 'Problem', 'capability': 'Capability', 'anomaly': 'Anomaly', 'challenged_result': 'Challenged result',
         'hypothesis': 'Hypothesis', 'data_without_theory': 'Data without theory', 'external_goal': 'External goal'}
ROUND_NAME = {'calc1': 'round 1', 'r2': 'round 2'}
ROUND_COLOR = {'calc1': ps.BLUE, 'r2': ps.AQUA}
# operational start, drawn in six colour groups plus 'coders split' (left to right in the bars)
OP_GROUPS = [
    ('Literature gap only', ['literature_gap_only'], ps.ORANGE),
    ('Prior result to test', ['prior_result_to_test'], ps.YELLOW),
    ('Stated hypothesis', ['stated_hypothesis'], ps.MAGENTA),
    ('Data in hand', ['data_in_hand'], ps.BLUE),
    ('New method, model or instrument', ['new_method_or_model', 'new_instrument_or_deployment'], ps.AQUA),
    ('Event, surprise or mandate', ['event_occurred', 'surprising_observation', 'mandate_or_project_goal'], ps.GREEN),
    ('Coders split', ['split'], ps.NEUTRAL),
]


def P(v) -> int:
    """Percent, rounded half up (0.705 -> 71), as the text of the report rounds."""
    return int(float(v) * 100 + 0.5 + 1e-9)


def wilson(k: int, n: int) -> tuple[float, float]:
    lo, hi = g21.wilson(k, n)
    return lo, hi


def walks():
    """Per batch state: papers, first step at the entry node, revisit of the entry node (g21 step 4 rules)."""
    pooled, bad = {}, {}
    for tag, _ in g21.ROUNDS:
        ok, nbad = g21.load(tag)
        bad[tag] = nbad
        pooled.update({(tag, k): c for k, c in ok.items()})
    out = {s: Counter() for s in STATES + ['all']}
    for c in pooled.values():
        st, nd = c['entry']['state'], c['entry']['node']
        nodes = [s['node'] for s in g21.steps_of(c)]
        coll = runs(nodes)
        rev = nd in coll and nd in coll[coll.index(nd) + 1:]
        for key in (st, 'all'):
            out[key]['n'] += 1
            out[key]['first'] += bool(nodes) and nodes[0] == nd
            out[key]['revisited'] += rev
    return out, pooled, bad


def dot(ax, x, y, lo, hi, color, open_=False, size=4.0, z=4):
    ax.plot([lo, hi], [y, y], color=color, lw=0.8, zorder=z - 1, solid_capstyle='butt', clip_on=False)
    if open_:
        ax.plot(x, y, 'o', ms=size - 0.5, mfc='white', mec=color, mew=1.0, zorder=z, clip_on=False)
    else:
        ax.plot(x, y, 'o', ms=size, color=color, mec='white', mew=0.5, zorder=z, clip_on=False)


def rows_axis(ax, n, xlabel, ticks=(0, 0.25, 0.5, 0.75, 1.0), labels=('0', '25', '50', '75', '100'), lim=(0, 1.0)):
    ax.set_xlim(*lim)
    ax.set_ylim(n - 0.5, -0.6)
    ax.set_xticks(list(ticks))
    ax.set_xticklabels(list(labels))
    ax.set_xlabel(xlabel)
    ax.tick_params(axis='y', length=0)
    ax.spines['left'].set_visible(False)
    ps.grid(ax, 'x')


def main():
    J = json.loads(SRC.read_text())
    d = J['data']
    ba = d['blind_audit']
    W, pooled, bad = walks()
    # the json must describe the codings as they are now
    assert W['all']['n'] == d['consistency']['n'], (
        f"{W['all']['n']} valid codings now, entry_state.json has {d['consistency']['n']}: rerun g21_entry_state.py first")
    assert W['all']['first'] == d['consistency']['entry_node_is_first_step'][0]
    for s in STATES + ['all']:
        if W[s]['n']:
            assert W[s]['revisited'] == d['revisits'][s]['revisited'][0], (s, W[s]['revisited'], d['revisits'][s]['revisited'])
    rounds = [t for t, _ in g21.ROUNDS if d['n_valid'].get(t)]

    ps.setup()
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    fig = ps.plt.figure(figsize=(ps.DOUBLE, 6.3))
    t1, b1 = 0.945, 0.625                          # row 1 axes
    t2, b2 = 0.405, 0.062                          # row 2 axes
    y_t1, y_t2 = 0.958, 0.497                      # panel titles (figure fraction)
    ax_a = fig.add_axes([0.13, b1, 0.25, t1 - b1])
    ax_b1 = fig.add_axes([0.575, b1, 0.19, t1 - b1])
    ax_b2 = fig.add_axes([0.80, b1, 0.185, t1 - b1])
    ax_c = fig.add_axes([0.155, b2, 0.265, t2 - b2])
    ax_d = fig.add_axes([0.445, b2, 0.17, t2 - b2], sharey=ax_c)
    ax_e = fig.add_axes([0.735, b2, 0.20, t2 - b2], sharey=ax_c)

    def ftitle(letter, text, x, yy):
        fig.text(x, yy, f'({letter})', fontsize=ps.LABEL, fontweight='bold', va='bottom', ha='left')
        fig.text(x + 0.032, yy, text, fontsize=ps.FONT, color=ps.INK, va='bottom', ha='left')

    # (a) entry-state shares: batch per round, blind consensus reweighted to round 1
    pe = ba['population_estimate']['consensus']
    cats = STATES + ['split']
    y = np.arange(len(cats), dtype=float)
    off = 0.16
    for i, s in enumerate(cats):
        for r in rounds:
            st = d['distribution'][r]['state']
            if s in st:
                ax_a.plot(st[s][1], y[i] - off, 'o', ms=4.0, color=ROUND_COLOR[r], mec='white', mew=0.5, zorder=4)
        if s in pe:
            dot(ax_a, pe[s]['share'], y[i] + off, *pe[s]['ci95'], ps.ORANGE, open_=True)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels([SNAME.get(s, 'Coders split') for s in cats])
    rows_axis(ax_a, len(cats), 'Share of papers (%)')
    ax_a.set_ylim(len(cats) - 0.5, -1.0)
    pb = d['distribution']['calc1']['state']['problem'][1]
    ax_a.text(pb + 0.03, -off, f"{P(pb)}%", fontsize=ps.SMALL, color=ps.BLUE, ha='left', va='center')
    ax_a.text(pb, -0.72, f"batch coder, round 1 ({d['n_valid']['calc1']})", fontsize=ps.SMALL, color=ps.BLUE,
              ha='center', va='center')
    pc = pe['problem']
    ax_a.text(pc['ci95'][0] - 0.02, off, f"{P(pc['share'])}%", fontsize=ps.SMALL, color=ps.ORANGE,
              ha='right', va='center')
    ax_a.text(0.36, y[1] + off + 0.05, 'blind consensus, weighted\nto round 1 (95% interval)', fontsize=ps.SMALL,
              color=ps.ORANGE, ha='left', va='center')
    if 'r2' in rounds:
        ax_a.text(0.36, y[3], f"batch coder, round 2 ({d['n_valid']['r2']})", fontsize=ps.SMALL, color=ps.AQUA, va='center')
    ftitle('a', 'Entry-state shares', 0.005, y_t1)

    # (b) agreement: observed vs chance, and alpha
    rs, rel = d['reliability'], ba['reliability']
    pairs = [('Batch run 1 vs run 2', rs['state'], rs['node'], rs['pairs']),
             ('Blind A vs blind B', rel['state']['A_vs_B'], rel['node']['A_vs_B'], rel['state']['A_vs_B']['n']),
             ('Blind A vs batch', rel['state']['A_vs_batch'], rel['node']['A_vs_batch'], rel['state']['A_vs_batch']['n']),
             ('Blind B vs batch', rel['state']['B_vs_batch'], rel['node']['B_vs_batch'], rel['state']['B_vs_batch']['n'])]
    yb, lab = [], []
    for gi, (gname, idx) in enumerate([('Entry state', 1), ('Entry node', 2)]):
        for j, p in enumerate(pairs):
            yy = gi * (len(pairs) + 1.0) + j
            yb.append(yy)
            lab.append(f'{p[0]} ({p[3]})')
            m = p[idx]
            exp, obs = m['expected_agreement_krippendorff'], m['observed_agreement']
            ax_b1.plot([exp, obs], [yy, yy], color=ps.NEUTRAL, lw=1.4, zorder=2, solid_capstyle='butt')
            ax_b1.plot(exp, yy, 'o', ms=3.4, mfc='white', mec=ps.INK2, mew=0.8, zorder=3)
            ax_b1.plot(obs, yy, 'o', ms=4.0, color=ps.BLUE, mec='white', mew=0.5, zorder=4)
            ci = m.get('alpha_ci95') or [m['alpha'], m['alpha']]
            dot(ax_b2, m['alpha'], yy, *ci, ps.BLUE)
        hdr = gi * (len(pairs) + 1.0) - 0.8
        ax_b1.text(-0.04, hdr, gname, fontsize=ps.FONT, color=ps.INK, fontweight='bold', va='center', ha='right',
                   transform=ax_b1.get_yaxis_transform())
    nb = yb[-1] + 1
    ax_b1.set_yticks(yb)
    ax_b1.set_yticklabels(lab)
    rows_axis(ax_b1, nb, 'Agreement (%)')
    ax_b1.set_ylim(nb - 0.5, -1.3)
    m0 = pairs[0][1]
    ax_b1.text(m0['expected_agreement_krippendorff'] - 0.04, yb[0], 'chance', fontsize=ps.SMALL, color=ps.INK2,
               ha='right', va='center')
    ax_b1.text(m0['observed_agreement'], yb[0] - 0.62, 'observed', fontsize=ps.SMALL, color=ps.BLUE, ha='center', va='center')
    for ref, txt, ha, dx in [(0.667, '0.667', 'right', -0.02), (0.8, '0.8', 'left', 0.02)]:
        ax_b2.axvline(ref, color=ps.INK2, lw=0.6, ls=(0, (3, 2)), zorder=1)
        ax_b2.text(ref + dx, -0.9, txt, fontsize=ps.SMALL, color=ps.INK2, ha=ha, va='center')
    rows_axis(ax_b2, nb, "Krippendorff's alpha", ticks=(0, 0.2, 0.4, 0.6, 0.8, 1.0),
              labels=('0', '0.2', '0.4', '0.6', '0.8', '1'))
    ax_b2.set_ylim(nb - 0.5, -1.3)
    ax_b2.set_yticks(yb)
    ax_b2.tick_params(axis='y', labelleft=False)
    ftitle('b', 'Agreement between two codings of the same papers (number of papers)', 0.42, y_t1)

    # rows shared by (c), (d), (e): the seven states, then all papers
    rows = STATES + ['all']
    yr = np.arange(len(rows), dtype=float)
    yr[-1] += 0.45
    ylim = (yr[-1] + 0.5, -0.55)

    # (c) operational start by batch state, audit sample
    bbs = ba['operational_start']['by_batch_state']
    allag = ba['operational_start']['agreed']
    cnt = {}
    for i, s in enumerate(rows):
        if s == 'all':
            ag, n = allag, ba['n']
        elif s in bbs:
            ag, n = bbs[s]['agreed'], bbs[s]['n']
        else:
            continue
        left = 0.0
        for gname, members, col in OP_GROUPS:
            k = sum(ag.get(m, 0) for m in members)
            cnt[(s, gname)] = k
            if not k:
                continue
            wdt = k / n
            ax_c.barh(yr[i], wdt, left=left, height=0.66, color=col, edgecolor='white', linewidth=0.6, zorder=3)
            txtcol = 'white' if col in (ps.BLUE, ps.GREEN, ps.ORANGE) else ps.INK
            ax_c.text(left + wdt / 2, yr[i], str(k), fontsize=ps.SMALL, color=txtcol, ha='center', va='center', zorder=4)
            left += wdt
    ax_c.set_yticks(yr)
    ax_c.set_yticklabels([SNAME.get(s, 'All papers') for s in rows])
    ax_c.set_xlim(0, 1)
    ax_c.set_ylim(*ylim)
    ax_c.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_c.set_xticklabels(['0', '25', '50', '75', '100'])
    ax_c.set_xlabel('Share of audited papers (%)')
    ax_c.tick_params(axis='y', length=0)
    ax_c.spines['left'].set_visible(False)
    hd = [Patch(facecolor=c, edgecolor='none', label=g) for g, _, c in OP_GROUPS]
    ax_c.legend(handles=hd, loc='lower left', bbox_to_anchor=(-0.55, 1.015), ncol=2, handlelength=0.9, handleheight=0.9,
                handletextpad=0.35, columnspacing=0.9, labelspacing=0.25, borderaxespad=0.0, fontsize=ps.SMALL)
    ftitle('c', 'What started the work, by batch entry state (blind coders agree)', 0.005, y_t2)

    # (d) gap statement share by coder's own state
    rg = ba['rhetorical_gap']
    dvals = {}
    for i, s in enumerate(rows):
        for who, col, op, dy in [('A', ps.BLUE, False, -0.15), ('B', ps.ORANGE, True, 0.15)]:
            tab = rg[f'{who}_by_own_state']
            k, n = (sum(v[0] for v in tab.values()), sum(v[1] for v in tab.values())) if s == 'all' else tab.get(s, [0, 0])
            if not n:
                continue
            lo, hi = wilson(k, n)
            dvals[(who, s)] = (k, n, lo, hi)
            dot(ax_d, k / n, yr[i] + dy, lo, hi, col, open_=op, size=3.6)
        if ('A', s) in dvals and ('B', s) in dvals:
            ax_d.text(1.04, yr[i], f"{dvals[('A', s)][0]}/{dvals[('A', s)][1]}, {dvals[('B', s)][0]}/{dvals[('B', s)][1]}",
                      fontsize=ps.SMALL, color=ps.INK2, va='center', ha='left', transform=ax_d.get_yaxis_transform())
    rows_axis(ax_d, 1, 'Quotes that are a gap statement (%)')
    ax_d.set_ylim(*ylim)
    ax_d.tick_params(axis='y', labelleft=False)
    ax_d.text(1.04, -0.75, 'A, B', fontsize=ps.SMALL, color=ps.INK2, va='center', ha='left', transform=ax_d.get_yaxis_transform())
    hd = [Line2D([], [], marker='o', ls='-', lw=0.8, color=ps.BLUE, mec='white', mew=0.5, ms=3.6, label='coder A'),
          Line2D([], [], marker='o', ls='-', lw=0.8, color=ps.ORANGE, mfc='white', mec=ps.ORANGE, mew=1.0, ms=3.1, label='coder B')]
    ax_d.legend(handles=hd, loc='lower left', bbox_to_anchor=(0.0, 1.06), ncol=1, handlelength=1.4, handletextpad=0.4,
                labelspacing=0.25, borderaxespad=0.0, fontsize=ps.SMALL, title="by the coder's own state",
                title_fontsize=ps.SMALL, alignment='left')
    ftitle('d', 'Entry quote is a gap statement', 0.445, y_t2)

    # (e) the walk: opens at the entry node, returns to it
    evals = {}
    for i, s in enumerate(rows):
        n = W[s]['n']
        if not n:
            continue
        for key, col, op, dy in [('first', ps.BLUE, False, -0.15), ('revisited', ps.ORANGE, True, 0.15)]:
            k = W[s][key]
            lo, hi = wilson(k, n)
            evals[(key, s)] = (k, n, lo, hi)
            dot(ax_e, k / n, yr[i] + dy, lo, hi, col, open_=op, size=3.6)
        ax_e.text(1.04, yr[i], str(n), fontsize=ps.SMALL, color=ps.INK2, va='center', ha='left',
                  transform=ax_e.get_yaxis_transform())
    ax_e.text(1.04, -0.75, 'papers', fontsize=ps.SMALL, color=ps.INK2, va='center', ha='left',
              transform=ax_e.get_yaxis_transform())
    rows_axis(ax_e, 1, 'Share of batch-coded papers (%)')
    ax_e.set_ylim(*ylim)
    ax_e.tick_params(axis='y', labelleft=False)
    hd = [Line2D([], [], marker='o', ls='-', lw=0.8, color=ps.BLUE, mec='white', mew=0.5, ms=3.6, label='walk opens at the entry node'),
          Line2D([], [], marker='o', ls='-', lw=0.8, color=ps.ORANGE, mfc='white', mec=ps.ORANGE, mew=1.0, ms=3.1,
                 label='walk returns to it after another node')]
    ax_e.legend(handles=hd, loc='lower left', bbox_to_anchor=(0.0, 1.06), ncol=1, handlelength=1.4, handletextpad=0.4,
                labelspacing=0.25, borderaxespad=0.0, fontsize=ps.SMALL, title='by batch entry state',
                title_fontsize=ps.SMALL, alignment='left')
    ftitle('e', 'Entry node in the walk', 0.735, y_t2)
    sts = [s for s in rows if s == 'all' or s in bbs]

    # ---- numbers and caption ----
    r3 = lambda v: round(float(v), 3)
    per = ba['per_batch_state']
    bp = ba['operational_start']['batch_problem']
    rv = d['revisits']
    raf = rv['return_after_failure_steps']
    qmv = rv['entry_node_Q']['later_Q_step_moves']
    numbers = {
        'source': str(SRC.relative_to(ROOT)), 'source_provenance': J.get('_provenance'),
        'valid_codings_now': {t: d['n_valid'].get(t, 0) for t, _ in g21.ROUNDS}, 'invalid_files': bad,
        'a_shares': {'batch': {r: {s: v for s, v in d['distribution'][r]['state'].items()} for r in rounds},
                     'blind_consensus_weighted': pe, 'blind_A_weighted': ba['population_estimate']['A'],
                     'blind_B_weighted': ba['population_estimate']['B'], 'strata': ba['strata']},
        'b_agreement': {p[0]: {f: {k: p[1 if f == 'state' else 2].get(k) for k in
                                   ('n', 'papers', 'observed_agreement', 'expected_agreement_krippendorff', 'alpha', 'alpha_ci95')}
                               for f in ('state', 'node')} for p in pairs},
        'b_retest_state_confusion': {'categories': rs['state']['categories'],
                                     'rows_calc1_cols_gold_r2': rs['state']['confusion_rows_calc1_cols_retest']},
        'c_operational_start_by_batch_state': {s: {g: cnt[(s, g)] for g, _, _ in OP_GROUPS} for s in sts},
        'c_groups': {g: m for g, m, _ in OP_GROUPS},
        'c_batch_problem': bp,
        'd_gap_flag': {f'{w}_{s}': {'k': v[0], 'n': v[1], 'wilson95': [v[2], v[3]]} for (w, s), v in dvals.items()},
        'd_regex_vs_coder_flag': rg['regex_vs_coder_flag'],
        'e_walk': {f'{key}_{s}': {'k': v[0], 'n': v[1], 'wilson95': [v[2], v[3]]} for (key, s), v in evals.items()},
        'e_entry_node_Q': rv['entry_node_Q'], 'e_return_after_failure_steps': raf,
        'e_reframe_after_failure_all': rv['all']['reframe_after_failure'],
        'per_batch_state_confirmation': per,
    }
    pr = per['problem']
    others = [s for s in STATES if s != 'problem' and s in per]
    oth_k, oth_n = sum(per[s]['both_confirm'] for s in others), sum(per[s]['n'] for s in others)
    cons_other = ', '.join(f'{v} to {SNAME[s].lower()}' for s, v in pr['consensus_other_state'].items())
    rt = rs['state']
    f2 = lambda v: f"{int(float(v) * 100 + 0.5 + 1e-9) / 100:.2f}"   # two decimals, half up (0.945 -> 0.95), as the report
    al = lambda m: f"{f2(m['alpha'])} [{f2(m['alpha_ci95'][0])}, {f2(m['alpha_ci95'][1])}]"
    rounds_txt = ' and '.join(f"{ROUND_NAME[r]} ({r}, {d['n_valid'][r]} valid codings)" for r in rounds)
    strata = ba['strata']
    small_txt = ' or '.join(str(v) for v in sorted({v['sampled'] for s, v in strata.items() if s != 'problem'}))
    wa = rel['state']['weighted_agreement']
    pag = ba['operational_start']['by_batch_state']['problem']['agreed']
    made = pag.get('new_method_or_model', 0) + pag.get('new_instrument_or_deployment', 0)
    qe = rv['entry_node_Q']
    band = ('below the 0.667 floor' if rt['alpha'] < 0.667 else 'in the tentative band, 0.667 to 0.8' if rt['alpha'] < 0.8
            else 'above 0.8')
    caption = (
        f"The batch coder repeats its own entry state ({P(rt['observed_agreement'])}% agreement between two runs, alpha "
        f"{f2(rt['alpha'])}, {band}), but its most common state, problem, mostly records the introduction's gap statement "
        f"rather than what started the work; the other six states ({small_txt} audited papers each) mostly match what "
        'started it. Entry state: one label per coded paper for how the research began, chosen from seven states defined in codebook '
        '1.5.0 (problem: an unsolved question the literature names; capability: a new instrument, method or archive; anomaly: '
        'a surprising observation; challenged result: a published finding the paper checks; hypothesis: stated in advance; data '
        'without theory: data collected without a guiding question; external goal: a mandate, benchmark or mission), with a '
        'supporting quote. Batch coder: claude-opus-5-5 through the Batch API, ' + rounds_txt + '. Blind coders A and B: two '
        f"Claude agents of the same model family that re-coded the entry of {ba['n']} round-1 papers from the full text, blind "
        f"to the batch label and to each other; the sample is stratified, {strata['problem']['sampled']} of the "
        f"{strata['problem']['population']} problem papers and {small_txt} of each other state. "
        'Consensus: the value A and B both gave. '
        f"(a) Share of papers in each entry state. Filled: batch coder. Open with bar: blind consensus weighted back to all "
        f"{d['n_valid']['calc1']} round-1 papers (weight = papers with that batch state / sampled papers with it), with a "
        f"stratified bootstrap 95% interval (2000 draws); 'coders split' is the weighted share where A and B disagree. "
        f"Problem falls from {P(d['distribution']['calc1']['state']['problem'][1])}% to {P(pe['problem']['share'])}% "
        f"[{P(pe['problem']['ci95'][0])}, {P(pe['problem']['ci95'][1])}]; single blind coders give "
        f"{P(ba['population_estimate']['A']['problem']['share'])}% (A) and {P(ba['population_estimate']['B']['problem']['share'])}% (B). "
        f"(b) Agreement on entry state (top) and entry node (bottom: the node of the project's research-workflow graph, "
        f"v0.4.2, where the paper enters, e.g. Q question, N new capability) for four pairs of codings, number of papers in "
        f"brackets. Batch run 1 vs run 2: the same coder twice on {rs['pairs']} gold-set papers (the frozen set held for "
        f"human coding; tags calc1 and gold-r2). Left: observed agreement (filled) against the agreement "
        f"expected by chance from how often each label is used (open). Right: Krippendorff's alpha (nominal) = (observed - "
        f"chance) / (1 - chance); 1 is perfect agreement, 0 is chance; dashed lines at 0.667 (floor for tentative conclusions) "
        f"and 0.8 (reliable); bars are 95% bootstrap intervals over papers (2000 resamples). State alpha: run 1 vs run 2 "
        f"{al(rt)}, A vs B {al(rel['state']['A_vs_B'])}, A vs batch {al(rel['state']['A_vs_batch'])}, B vs batch "
        f"{al(rel['state']['B_vs_batch'])}. With one label holding most papers, chance agreement is high and a "
        f"{P(rt['observed_agreement'])}% match gives alpha {f2(rt['alpha'])}. Blind pairs are unweighted over the stratified "
        f"sample, which holds fewer problem papers than round 1; weighted to round 1, state agreement is "
        f"{P(wa['A_vs_B'])}% (A vs B), {P(wa['A_vs_batch'])}% (A vs batch) and {P(wa['B_vs_batch'])}% (B vs batch). "
        f"(c) Audit sample, one bar per batch entry state, numbers in the bars are papers (bottom bar: all {ba['n']} audited "
        f"papers, unweighted): what started the work, as both blind coders "
        f"named it (operational start: what the study could not have begun without, one of nine classes, drawn in six colour "
        f"groups); grey where they named different classes. Of the {bp['n']} batch problem papers, both coders said "
        f"'literature gap only' for {bp['agreed_literature_gap_only'][0]} and named a concrete object (data in hand, an event, "
        f"an instrument or deployment, a method or model, a mandate, a surprising observation) for {bp['agreed_concrete_object'][0]}; "
        f"{made} of these are a new method, model or instrument, which can be the paper's product as much as its start. "
        f"Both kept the problem label for {pr['both_confirm']} of {pr['n']} ({P(pr['share_both_confirm'])}%, Wilson 95% "
        f"interval for a proportion {P(pr['share_both_confirm_ci95'][0])} to {P(pr['share_both_confirm_ci95'][1])}%); consensus moved "
        f"{cons_other}, and {pr['split']} were split. The other states were confirmed by both for {oth_k} of {oth_n}. "
        f"(d) Share of each blind coder's entry quotes that the coder itself flagged as a gap statement (a sentence naming what "
        f"is unknown, unclear, debated or lacking: the second move of the introduction in Swales 1990), by the state that coder "
        f"gave (bottom row: all {ba['n']} quotes of each coder); flagged/total at right (A, B); bars are Wilson 95% intervals. A word-pattern detector (g21 gap "
        f"markers) agrees with the coders' flag on {P(rg['regex_vs_coder_flag']['agreement'])}% of "
        f"{rg['regex_vs_coder_flag']['units']} quotes. "
        f"(e) Batch codings ({W['all']['n']} papers), by entry state: share whose walk (the coded sequence of steps in document "
        f"order) opens at the entry node (filled) and share that returns to the entry node after at least one other node "
        f"(open), Wilson 95% intervals; papers per state at right. The entry state itself is one label per paper and cannot recur; only its node can. Of "
        f"the {qe['n']} papers entering at Q, {qe['later_Q_step_raw'][0]} have a later Q step ({qe['Q_revisited_collapsed'][0]} "
        f"after another node); of those {sum(qmv.values())} later Q steps, {qmv.get('new', 0)} are coded as new, "
        f"{qmv.get('cited', 0)} as cited and {qmv.get('repeat', 0)} as a repeat (new: a step forward in the work), so "
        f"the coder records them as further questions, not as the entry question asked again. None of the {raf['n']} steps coded as a return after failure sits at Q or is "
        f"followed by Q: no paper reframes its question after a failed test. "
        'All coders are Claude models, so agreement among them is an upper bound. '
        'Source: private/data/roadmap/derived/entry/entry_state.json (tools/roadmap/g21_entry_state.py, steps 1-4 and 9), '
        'blind codings in private/data/roadmap/derived/entry/blind_audit.json; (e) recomputed from '
        'private/analysis/codings/api and checked against the json.')
    ps.save(fig, 'fig13_entry_state',
            inputs=[SRC, DERIVED / 'entry' / 'blind_audit.json', *[API / t for t, _ in g21.ROUNDS if (API / t).is_dir()]],
            numbers=numbers, caption=caption)


if __name__ == '__main__':
    main()
