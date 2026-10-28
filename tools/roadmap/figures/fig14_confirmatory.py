"""Figure 14: the round-2 confirmatory test of the 43 preregistered associations (roadmap g23 analysis, paper figure).

Panels (every number read from the frozen plan and the g23 results file; nothing is recomputed here)
  strip  one square per hypothesis, by kind (citations, novelty, breadth, subfield, journal family): filled =
         confirmed, open = not confirmed, red outline = reversed; counts per kind and over the family of 43.
  a      H01-H15, workflow feature against outcome (g17 tests): round-1 Spearman rho with its 95% bootstrap interval
         (blue circle, the estimate frozen in the plan) and round-2 rho with its interval (orange square) on one row
         per hypothesis, grouped by outcome; zero line. Round-2 marker filled = confirmed, open = not confirmed; the
         row label is bold when confirmed. Right margin: round-2 BH q and whether the predicted sign held.
  b      H16-H43 with a count feature (g20 Kruskal-Wallis tests): round-1 against round-2 epsilon squared, each with
         its 95% bootstrap interval, grouped by subfield and journal family. Margin: round-2 q and whether the round-2
         group medians rank the shared named groups in the round-1 order.
  c      H16-H43 with a binary or categorical feature (g20 chi-square tests): round-1 against round-2 bias-corrected
         Cramer's V with intervals, grouped by subfield and journal family. The label names the round-1 leading group
         and the predicted direction of its rate against the rest; margin: round-2 q and whether that direction held.
  Panels b and c together are the 28 field and venue hypotheses; they are split only because the two effect sizes
  are on different scales.

Definitions
  rho              Spearman rank correlation between a workflow feature (count per paper, or 0/1) and an outcome.
  Cramer's V       association between a feature and a grouping (subfield or journal family) from the chi-square
                   of their contingency table, 0 = independent, 1 = the group determines the feature; bias-corrected
                   after Bergsma (2013), as g20 reports it.
  epsilon squared  Kruskal-Wallis H / (n - 1): the share of rank variance of a count explained by the grouping.
  BH q             Benjamini-Hochberg adjusted p over the 43 round-2 permutation p values (one family).
  rule             (preregistration/round2-confirmatory.json) confirmed when q < 0.1 and the predicted direction holds;
                   reversed when q < 0.1 and the direction is opposite; otherwise not confirmed.
  direction        H01-H15: sign of rho. Binary g20 rows: sign of the round-1 leading group's rate minus the rate in
                   all other papers. Count g20 rows: Spearman correlation of round-1 and round-2 group medians over the
                   shared named groups > 0 ('undefined' when it cannot be computed, which g23 scores as not held).
                   Categorical g20 rows: no direction predicted.

Inputs
  preregistration/round2-confirmatory.json                 frozen plan (public commit b4369fe): hypotheses, round-1
                                                           estimates, predicted directions
  private/data/roadmap/derived/confirmatory/results.json   g23 test (tools/roadmap/g23_confirmatory.py test): round-2
                                                           estimates, q, direction, verdict
  private/data/roadmap/derived/calc1/manifest.jsonl        eligible round-1 papers (count only, for the caption)
  private/data/roadmap/derived/r2calc/manifest.jsonl       eligible round-2 papers (count only, for the caption)
  agents/coder/definitions.json                            composition labels

Outputs  private/data/roadmap/figures/paper/fig14_confirmatory.{pdf,png,json}
Run:     python tools/roadmap/figures/fig14_confirmatory.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402

PLAN = ps.ROOT / 'preregistration' / 'round2-confirmatory.json'
RES = ps.DERIVED / 'confirmatory' / 'results.json'
MAN1 = ps.DERIVED / 'calc1' / 'manifest.jsonl'
MAN2 = ps.DERIVED / 'r2calc' / 'manifest.jsonl'
DEFS = ps.ROOT / 'agents' / 'coder' / 'definitions.json'
TJ = ps.DERIVED / 'topics' / 'topics_journals.json'
FROZEN_COMMIT, FIX_COMMIT = 'b4369fe', 'cb6dcfd'
R1, R2 = ps.BLUE, ps.ORANGE
PITCH = 0.122            # inches per row
HEAD = 1.25              # rows taken by a group header

OUTCOME_ORDER = ['cnp', 'fwci', 'novelty_pair', 'breadth_refs']
OUTCOME_HEAD = {'cnp': 'Citations: citation percentile (cnp)', 'fwci': 'Citations: field-weighted impact (FWCI)',
                'novelty_pair': 'Novelty: rare topic pair', 'breadth_refs': 'Breadth: references outside geoscience'}
COUNTS = {'imports': 'Borrowed from other fields (count)', 'import fields': 'Fields borrowed from (count)',
          'distinct modes': 'Distinct modes of inquiry (count)', 'distinct nodes': 'Distinct nodes (count)',
          'revisits': 'Node revisits (count)', 'steps': 'Steps (count)', 'V check kinds': 'Kinds of V check (count)'}
SHORT_GROUP = {'Artificial Intelligence': 'Seismology (OpenAlex: Artificial Intelligence)',
               'Atmospheric Science': 'Atmospheric Science', 'Earth-Surface Processes': 'Earth-Surface Processes',
               'Geochemistry and Petrology': 'Geochemistry and Petrology', 'Geophysics': 'Geophysics',
               'Oceanography': 'Oceanography', 'Water Science and Technology': 'Water Science and Technology',
               'Springer Nature (non-portfolio)': 'Springer Nature, other', 'Wiley non-AGU': 'Wiley, non-AGU',
               'EGU/Copernicus': 'Copernicus (EGU)', 'AGU': 'AGU', 'Nature portfolio': 'Nature portfolio'}
# Freeze timeline, local time (UTC-6) on 2026-10-27. Sources: round-2 batch submission times from
# private/analysis/codings/api/state.json (report_numbers.json r2.batch); plan commit b4369fe pushed 16:45:17 (local
# reflog of origin/framework-v0.5); first round-2 coding file written 20:55:49 (file times in codings/api/r2/).
FREEZE_TIMELINE = {'r2_batches_submitted': ['01:37', '08:40'], 'plan_pushed': '16:45',
                   'first_r2_coding_downloaded': '20:55'}
# Families among the 233 first-analysis papers the plan was built from (tools/roadmap/rounds.py round1_split, DOI
# prefixes 10.1029 and 10.1016 in derived/calc1/manifest.jsonl; read 2026-10-27). Elsevier is not a named plan family.
FIRST_ANALYSIS_FAMILY = {'AGU': 16, 'Elsevier': 9}
GROUPING_HEAD = {'subfield': 'Subfield (OpenAlex)', 'family': 'Journal family'}
KINDS = [('cit', 'Citations'), ('nov', 'Novelty'), ('brd', 'Breadth'), ('subfield', 'Subfield'), ('family', 'Journal family')]
TERMS = {}


def feat_label(f):
    """Plain-words label for a g17 or g20 feature name."""
    f = f.split(':', 1)[1] if f[:4] in ('num:', 'bin:') else f
    if f in COUNTS:
        return COUNTS[f]
    head, _, rest = f.partition(' ')
    if rest == '(whole variable)':
        return {'decisive': 'Decisive mode of inquiry', 'composition': 'Composition'}[head] + ' (whole variable)'
    if head == 'mode':
        return f'Uses {rest} (mode of inquiry)'
    if head == 'decisive':
        return f'Decisive mode of inquiry: {rest}'
    if head == 'composition':
        return 'Composition: ' + (TERMS.get(rest, {}).get('label') or rest.replace('_', ' '))
    if head == 'node':
        letter = rest.split(' ')[0]
        return f'Uses node {letter} ({ps.NODE_NAMES[letter]})'
    return f


def clopper_pearson(k, n, a=0.05):
    """Exact binomial 95% interval for k of n (bisection on the binomial tail; no scipy in this environment)."""
    from math import comb

    def tail_ge(p):   # P(X >= k)
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))

    def tail_le(p):   # P(X <= k)
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))

    def solve(f, target, increasing):
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if (f(mid) < target) == increasing:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(tail_ge, a / 2, True)
    upper = 1.0 if k == n else solve(tail_le, a / 2, False)
    return round(lower, 2), round(upper, 2)


def kind_of(h):
    if h['source'] == 'g17':
        return 'cit' if h['outcome'] in ('cnp', 'fwci') else ('nov' if h['outcome'] == 'novelty_pair' else 'brd')
    return h['grouping']


def direction_word(h, r):
    if h['source'] == 'g20' and h['kind'] == 'categorical':
        return 'none set'
    if h['source'] == 'g20' and h['kind'] == 'count' and r.get('median_order_rho') is None:
        return 'undefined'
    return 'held' if r['direction_ok'] else 'opposite'


def r1_effect(h):
    a = h['round1']
    if h['source'] == 'g17':
        return a['rho'], a['ci']
    if 'epsilon2' in a:
        return a['epsilon2'], a['epsilon2_ci']
    return a['cramers_v_bc'], a['v_bc_ci']


def r2_effect(h, r):
    if h['source'] == 'g17':
        return r['rho'], r['ci']
    if 'epsilon2' in r:
        return r['epsilon2'], r['epsilon2_ci']
    return r['cramers_v_bc'], r['v_bc_ci']


def forest(ax, groups, xlabel, margin_x, numbers, key, zero=True):
    """Rows of (round 1, round 2) estimates with intervals; groups = [(header, [(label, h, r)])]."""
    y, ticks, labels, heads, bold = 0.0, [], [], [], []
    off = 0.2
    drawn = []
    for head, rows in groups:
        heads.append((y + HEAD * 0.55, head))
        y += HEAD
        for lab, h, r in rows:
            yc = y + 0.5
            e1, c1 = r1_effect(h)
            e2, c2 = r2_effect(h, r)
            conf = r['verdict'] == 'confirmed'
            ax.plot(c1, [yc - off] * 2, color=R1, linewidth=0.9, solid_capstyle='butt', zorder=2)
            ax.plot([e1], [yc - off], 'o', color=R1, markersize=3.0, markeredgecolor='white', markeredgewidth=0.4, zorder=3)
            ax.plot(c2, [yc + off] * 2, color=R2, linewidth=0.9, solid_capstyle='butt', zorder=2)
            ax.plot([e2], [yc + off], 's', markersize=3.0, zorder=4, markeredgewidth=0.8,
                    markerfacecolor=R2 if conf else 'white',
                    markeredgecolor=ps.DIV_POS if r['verdict'] == 'reversed' else R2)
            ticks.append(yc)
            labels.append(lab)
            bold.append(conf)
            dw = direction_word(h, r)
            ax.text(margin_x[0], yc, f"{r['q']:.3f}" if r['q'] >= 0.001 else f"{r['q']:.4f}", transform=ax.get_yaxis_transform(),
                    ha='right', va='center', fontsize=ps.SMALL, color=ps.INK if r['q'] < 0.1 else ps.INK2,
                    fontweight='bold' if conf else 'normal')
            ax.text(margin_x[1], yc, dw, transform=ax.get_yaxis_transform(), ha='left', va='center', fontsize=ps.SMALL,
                    color=ps.INK if dw == 'held' else ps.INK2)
            drawn.append({'id': h['id'], 'label': lab, 'round1': {'effect': e1, 'ci': c1, 'q': h['round1']['q'],
                                                                   'n': h['round1']['n']},
                          'round2': {'effect': e2, 'ci': c2, 'q': r['q'], 'p': r['p'], 'n': r['n']},
                          'direction': dw, 'verdict': r['verdict']})
            y += 1
    if zero:
        ax.axvline(0, color=ps.MUTED, linewidth=0.6, zorder=1)
    ax.set_ylim(y + 0.15, 0)
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=ps.SMALL)
    for t, b in zip(ax.get_yticklabels(), bold):
        if b:
            t.set_fontweight('bold')
            t.set_color(ps.INK)
    ax.tick_params(axis='y', length=0, pad=2)
    for yy, hd in heads:
        ax.text(-0.012, yy, hd, transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=ps.SMALL,
                fontweight='bold', color=ps.INK)
    ax.text(margin_x[0], -0.25, 'q, round 2', transform=ax.get_yaxis_transform(), ha='right', va='bottom',
            fontsize=ps.SMALL, color=ps.INK2)
    ax.text(margin_x[1], -0.25, 'Direction', transform=ax.get_yaxis_transform(), ha='left', va='bottom',
            fontsize=ps.SMALL, color=ps.INK2)
    lo = min(min(d['round1']['ci'][0], d['round2']['ci'][0]) for d in drawn)
    hi = max(max(d['round1']['ci'][1], d['round2']['ci'][1]) for d in drawn)
    lo = min(lo, 0)
    pad = 0.03 if lo < 0 else 0.012 * (np.ceil(hi * 10) / 10)     # room for a marker sitting at 0
    ax.set_xlim(np.floor(lo * 10) / 10 - pad, np.ceil(hi * 10) / 10 + 0.01)
    ax.set_xlabel(xlabel, labelpad=2)
    ps.grid(ax, 'x')
    ax.spines['left'].set_visible(False)
    numbers[key] = drawn
    return y + 0.15


def strip(ax, hyps, res, numbers):
    """Summary: one square per hypothesis by kind; filled = confirmed."""
    ax.set_axis_off()
    x = 0.0
    per = {}
    sq, gap = 1.0, 0.25
    for k, name in KINDS:
        hs = [h for h in hyps if kind_of(h) == k]
        nc = sum(res[h['id']]['verdict'] == 'confirmed' for h in hs)
        nr = sum(res[h['id']]['verdict'] == 'reversed' for h in hs)
        per[name] = {'hypotheses': [h['id'] for h in hs], 'confirmed': nc, 'reversed': nr, 'tested': len(hs)}
        lab = f'{name}: {nc} of {len(hs)}'
        ax.text(x, 1.55, lab, ha='left', va='bottom', fontsize=ps.SMALL, color=ps.INK)
        order = sorted(hs, key=lambda h: (res[h['id']]['verdict'] != 'confirmed', h['id']))
        for i, h in enumerate(order):
            v = res[h['id']]['verdict']
            ax.add_patch(Rectangle((x + i * (sq + gap), 0), sq, sq, facecolor=R2 if v == 'confirmed' else 'white',
                                   edgecolor=ps.DIV_POS if v == 'reversed' else R2, linewidth=0.7))
        x += max(len(hs) * (sq + gap), len(lab) * 0.62) + 2.6
    ax.set_xlim(0, x - 2.6)
    ax.set_ylim(-0.2, 2.9)
    ax.set_aspect('equal', anchor='W')
    numbers['strip_per_kind'] = per


def main():
    TERMS.update(json.loads(DEFS.read_text())['terms'])
    plan = json.loads(PLAN.read_text())
    d = ps.read_json(RES)
    hyps = plan['hypotheses']
    res = {r['id']: r for r in d['rows']}
    assert len(hyps) == plan['family_size'] == d['family_size'] == len(res), 'plan and results disagree on the family'
    verd = d['verdicts']
    eligible1 = sum(1 for line in MAN1.read_text().splitlines() if line.strip())
    eligible2 = sum(1 for line in MAN2.read_text().splitlines() if line.strip())
    n1 = sorted({h['round1']['n'] for h in hyps})
    n2 = d['papers']
    numbers = {'family_size': len(hyps), 'verdicts': verd, 'q_threshold': plan['q_threshold'],
               'round1_papers_in_plan': n1, 'round2_papers': n2, 'eligible_round1': eligible1,
               'eligible_round2': eligible2, 'plan_frozen': plan['frozen'], 'plan_commit_public': FROZEN_COMMIT,
               'post_freeze_fix_commit_public': FIX_COMMIT, 'results_provenance': json.loads(RES.read_text()).get('_provenance'),
               'plan_sha256_in_results': d.get('plan_sha256')}

    # panel a groups
    ga = []
    for o in OUTCOME_ORDER:
        rows = [(feat_label(h['feature']), h, res[h['id']]) for h in hyps if h['source'] == 'g17' and h['outcome'] == o]
        if rows:
            ga.append((OUTCOME_HEAD[o], rows))
    # panels b (counts) and c (binary, categorical)
    gb, gc = [], []
    for g in ('subfield', 'family'):
        hb = [h for h in hyps if h['source'] == 'g20' and h['grouping'] == g and h['kind'] == 'count']
        if hb:
            gb.append((GROUPING_HEAD[g], [(feat_label(h['feature']), h, res[h['id']]) for h in hb]))
        hc = [h for h in hyps if h['source'] == 'g20' and h['grouping'] == g and h['kind'] != 'count']
        rows = []
        for h in hc:
            lab = feat_label(h['feature'])
            if h['kind'] == 'binary':
                p = h['predicted']
                lab += f"; {'higher' if p['sign_of_rate_minus_rest'] > 0 else 'lower'} in {SHORT_GROUP.get(p['leading_group'], p['leading_group'])}"
            rows.append((lab, h, res[h['id']]))
        if rows:
            gc.append((GROUPING_HEAD[g], rows))

    na = sum(len(r) for _, r in ga) + HEAD * len(ga) + 0.15
    nb = sum(len(r) for _, r in gb) + HEAD * len(gb) + 0.15
    nc = sum(len(r) for _, r in gc) + HEAD * len(gc) + 0.15
    ha, hb_, hc = na * PITCH, nb * PITCH, nc * PITCH
    W = ps.DOUBLE
    top = 0.62                       # strip and legend band
    H = top + 0.22 + ha + 0.42 + 0.30 + hc + 0.32
    fig, _ = ps.figure(W, H)
    fig.axes[0].remove()

    def box(x0, y0, w, h):
        return [x0 / W, y0 / H, w / W, h / H]

    # strip
    axs = fig.add_axes(box(0.05, H - 0.42, 4.9, 0.20))
    strip(axs, hyps, res, numbers)
    fig.text(0.05 / W, (H - 0.09) / H,
             f"Round 2 test of the {len(hyps)} preregistered associations: {verd.get('confirmed', 0)} confirmed, "
             f"{verd.get('reversed', 0)} reversed, {verd.get('not confirmed', 0)} not confirmed "
             f"(rule: BH q < {plan['q_threshold']:g} and the predicted direction)",
             ha='left', va='top', fontsize=ps.FONT, fontweight='bold', color=ps.INK)
    leg = [Line2D([], [], color=R1, marker='o', markersize=3.0, markeredgecolor='white', markeredgewidth=0.4,
                  linewidth=0.9, label=f'Round 1, n = {n1[0]} (exploratory, frozen in the plan)'),
           Line2D([], [], color=R2, marker='s', markersize=3.0, markerfacecolor=R2, markeredgecolor=R2, linewidth=0.9,
                  label=f'Round 2, n = {n2}: confirmed'),
           Line2D([], [], color=R2, marker='s', markersize=3.0, markerfacecolor='white', markeredgecolor=R2,
                  markeredgewidth=0.8, linewidth=0.9, label=f'Round 2, n = {n2}: not confirmed')]
    fig.legend(handles=leg, loc='upper right', bbox_to_anchor=((W - 0.02) / W, (H - 0.17) / H), handlelength=1.8,
               fontsize=ps.SMALL, borderaxespad=0, labelspacing=0.3)

    # panel a: top left
    y_top = H - top - 0.22
    axa = fig.add_axes(box(1.62, y_top - ha, 1.25, ha))
    forest(axa, ga, r'Spearman $\rho$, 95% interval', (1.39, 1.45), numbers, 'panel_a')
    ps.panel(axa, 'a', x=-1.58 / 1.25, y=1.0 + 0.14 / ha)

    # panel b: top right, counts
    axb = fig.add_axes(box(5.25, y_top - hb_, 1.0, hb_))
    forest(axb, gb, r'Epsilon squared, 95% interval', (1.47, 1.53), numbers, 'panel_b', zero=False)
    ps.panel(axb, 'b', x=-1.62 / 1.0, y=1.0 + 0.14 / hb_)
    key = ("Nodes of graph v0.4.2: N New capability, I Infer, D Design,\n"
           "P Protect, V Vary or replicate.\n"
           "Direction: held = the predicted sign or group order holds in\n"
           "round 2; opposite = it does not; undefined = group medians\n"
           "cannot be ranked; none set = whole variable, no direction.\n"
           f"Bold label and filled square: confirmed (q < {plan['q_threshold']:g} and\n"
           "direction held). Round-1 estimates are the frozen ones.")
    fig.text(3.98 / W, (y_top - hb_ - 0.55) / H, key, ha='left', va='top', fontsize=ps.SMALL, color=ps.INK2,
             linespacing=1.35)

    # panel c: bottom, full width, binary and categorical
    yc_top = y_top - ha - 0.42 - 0.30
    axc = fig.add_axes(box(3.05, yc_top - hc, 2.95, hc))
    forest(axc, gc, "Cramer's V, bias-corrected, 95% interval", (1.165, 1.18), numbers, 'panel_c', zero=False)
    ps.panel(axc, 'c', x=-3.0 / 2.95, y=1.0 + 0.14 / hc)

    # numbers for the caption
    g17 = [h for h in hyps if h['source'] == 'g17']
    cit = [h for h in g17 if h['outcome'] in ('cnp', 'fwci')]
    numbers['citation_hypotheses_round2_rho_range'] = [min(res[h['id']]['rho'] for h in cit),
                                                      max(res[h['id']]['rho'] for h in cit)]
    numbers['confirmed_ids'] = [h['id'] for h in hyps if res[h['id']]['verdict'] == 'confirmed']
    numbers['q_below_threshold_direction_not_held'] = [h['id'] for h in hyps
                                                       if res[h['id']]['q'] < plan['q_threshold'] and not res[h['id']]['direction_ok']]
    numbers['direction_held_q_not_below'] = [h['id'] for h in hyps
                                             if res[h['id']]['q'] >= plan['q_threshold'] and res[h['id']]['direction_ok']]
    lead = {h['id']: {'group': h['predicted']['leading_group'], **res[h['id']]['leading_group_round2']}
            for h in hyps if h['source'] == 'g20' and h['kind'] == 'binary' and res[h['id']].get('leading_group_round2')}
    numbers['round2_leading_group'] = lead
    small = {i: v for i, v in lead.items() if res[i]['verdict'] == 'confirmed' and v['n'] < 10}
    numbers['confirmed_binary_with_round2_leading_group_under_10'] = small
    exact = {i: {'k': round(v['rate'] * v['n']), 'n': v['n'],
                 'rate_ci95_clopper_pearson': clopper_pearson(round(v['rate'] * v['n']), v['n'])}
             for i, v in lead.items() if v['n'] < 10}
    numbers['round2_leading_group_under_10_exact_rate_ci'] = exact
    per = numbers['strip_per_kind']

    # what the confirmed rows are (a reading aid; the verdicts are the frozen ones)
    conf_ids = numbers['confirmed_ids']
    hmap = {h['id']: h for h in hyps}
    validity = [i for i in conf_ids if hmap[i]['source'] == 'g17' and hmap[i]['feature'] in ('num:imports', 'num:import fields')]
    whole = [i for i in conf_ids if hmap[i].get('kind') == 'categorical']
    sign_only = [i for i in small if small[i]['diff_ci'][0] < 0 < small[i]['diff_ci'][1]]
    few = [i for i in small if i not in sign_only]
    directional = [i for i in conf_ids if i not in validity + whole + few + sign_only]
    numbers['confirmed_breakdown'] = {'convergent_validity': validity, 'whole_variable_no_direction': whole,
                                      'leading_group_under_10': few, 'sign_only': sign_only,
                                      'directional_full_sample_or_group_of_20_plus': directional}
    few_groups = sorted({(small[i]['group'], small[i]['n']) for i in few})
    opposite = [h['id'] for h in hyps if res[h['id']]['verdict'] == 'not confirmed'
                and direction_word(h, res[h['id']]) == 'opposite']
    undefined = [h['id'] for h in hyps if direction_word(h, res[h['id']]) == 'undefined']
    single = [i for i, v in lead.items() if v['n'] == 1 and res[i]['verdict'] == 'not confirmed']
    numbers['not_confirmed_breakdown'] = {'opposite_sign': opposite, 'direction_undefined': undefined,
                                          'leading_group_of_1': single}

    # population difference between the rounds (derived/topics/topics_journals.json, coded papers)
    T = ps.read_json(TJ)['composition']
    sub1, sub2 = T['round1']['coded']['subfield']['counts'], T['round2']['coded']['subfield']['counts']
    fam2 = T['round2']['coded']['family']['counts']
    n1now = T['round1']['coded']['subfield'].get('n') or sum(v['n'] for v in sub1.values())
    j2 = T['round2']['coded']['journals']['distinct_journals']
    pop = {'round2_journals': j2, 'esp': [sub1['Earth-Surface Processes']['n'], sub2['Earth-Surface Processes']['n']],
           'seismology_group': [sub1['Artificial Intelligence']['n'], sub2['Artificial Intelligence']['n']],
           'round1_papers_now': n1now, 'first_analysis_family': FIRST_ANALYSIS_FAMILY,
           'elsevier_round2': fam2.get('Elsevier', {}).get('n'), 'freeze_timeline_local': FREEZE_TIMELINE}
    numbers['population'] = pop
    ft = FREEZE_TIMELINE
    ex_txt = '; '.join(f"{i} {SHORT_GROUP.get(lead[i]['group'], lead[i]['group'])}, {e['k']} of {e['n']}, "
                       f"[{e['rate_ci95_clopper_pearson'][0]:.2f}, {e['rate_ci95_clopper_pearson'][1]:.2f}]"
                       for i, e in sorted(exact.items()))
    caption = (
        f"Round-2 confirmatory test of the {len(hyps)} associations frozen in preregistration/round2-confirmatory.json "
        f"(public commit {FROZEN_COMMIT}, {plan['frozen']}), written when no round-2 coding had been collected or read: "
        f"the two main round-2 batches were submitted at {ft['r2_batches_submitted'][0]} and "
        f"{ft['r2_batches_submitted'][1]} local time, the plan was pushed at {ft['plan_pushed']}, and the first "
        f"round-2 coding was downloaded at {ft['first_r2_coding_downloaded']}; the freeze refuses to run if any "
        f"round-2 coding file exists, and found {plan['round2_codings_at_freeze']}. Round 1 is exploratory: "
        f"the {n1[0]} papers valid at the first analysis (tag calc1, of {eligible1} eligible), whose estimates the plan "
        f"froze; later round-1 codings do not enter this test. Round 2 is confirmatory: {n2} of {eligible2} eligible "
        f"papers (tag r2) with a coding that passes tools/check_coding.py validate(); no other exclusion. Round 2 is a "
        f"different population: open access only, at most 4 papers per journal, {j2} journals, drawn by publisher "
        f"rotation rather than by the subfield rotation of round 1, so it holds {pop['esp'][1]} Earth-Surface Processes "
        f"papers against {pop['esp'][0]} of the {n1now} round-1 papers, and {pop['seismology_group'][1]} seismology "
        f"paper against {pop['seismology_group'][0]}. The plan's groups come from the {n1[0]} first-analysis papers, "
        f"which held only {FIRST_ANALYSIS_FAMILY['AGU']} AGU and {FIRST_ANALYSIS_FAMILY['Elsevier']} Elsevier papers; "
        f"Elsevier is therefore not a named family, and its {pop['elsevier_round2']} round-2 papers go to the pooled "
        f"small groups. Coded by claude-opus-5-5 under codebook 1.5.0; test by tools/roadmap/g23_confirmatory.py test, "
        f"which wrote its output once. The only code change after the freeze (public commit {FIX_COMMIT}) converts numpy "
        f"booleans to Python booleans for the JSON output; it changes no data, statistic or rule. "
        f"Top: one square per hypothesis, filled when confirmed; {verd.get('confirmed', 0)} confirmed, "
        f"{verd.get('reversed', 0)} reversed, {verd.get('not confirmed', 0)} not confirmed "
        f"(citations {per['Citations']['confirmed']} of {per['Citations']['tested']}, novelty "
        f"{per['Novelty']['confirmed']} of {per['Novelty']['tested']}, breadth {per['Breadth']['confirmed']} of "
        f"{per['Breadth']['tested']}, subfield {per['Subfield']['confirmed']} of {per['Subfield']['tested']}, journal "
        f"family {per['Journal family']['confirmed']} of {per['Journal family']['tested']}). "
        f"The {len(conf_ids)} confirmed rows are of four kinds: {len(validity)} are the convergent validity check of the "
        f"coder ({', '.join(validity)}); {len(whole)} are whole-variable associations with no direction "
        f"({', '.join(whole)}); {len(few)} rest on round-2 leading groups of fewer than 10 papers "
        f"({', '.join(few)}; " + '; '.join(f"{SHORT_GROUP.get(g, g)}, {n} papers, the same papers in each row"
                                           for g, n in few_groups) + f"); "
        f"{len(sign_only)} holds by sign only ({', '.join(sign_only)}); and {len(directional)} are directional "
        f"confirmations on the full sample or on a leading group of at least 20 papers ({', '.join(directional)}). "
        f"Among the {verd.get('not confirmed', 0)} not confirmed, {len(opposite)} changed sign without reaching "
        f"q < {plan['q_threshold']:g} ({', '.join(opposite)}), {len(undefined)} count rows have an undefined direction "
        f"({', '.join(undefined)}), and {len(single)} rest on a single round-2 paper ({', '.join(single)}). "
        f"Rule: one family of {len(hyps)} tests; q is the Benjamini-Hochberg adjusted p value over the {len(hyps)} "
        f"round-2 permutation p values (5000 permutations, floor 1/5001 = 0.0002), the smallest false-discovery rate at "
        f"which that test would be called significant; q < {plan['q_threshold']:g} means the test belongs to a set in "
        f"which at most about 10% of findings are expected to be false. A hypothesis is confirmed when "
        f"q < {plan['q_threshold']:g} and the predicted direction holds, reversed when q < {plan['q_threshold']:g} and "
        f"the direction is opposite, and not confirmed otherwise. Intervals are 95% percentile bootstrap intervals "
        f"(2000 resamples over papers). "
        f"(a) The {len(g17)} feature-outcome hypotheses: Spearman rho, the rank correlation between a workflow feature "
        f"of the coded paper (a count, or 0/1 for present or absent) and an OpenAlex outcome: cnp, the citation "
        f"normalized percentile among works of the same subfield, year and type, 0 to 1; FWCI, citations over the mean "
        f"of those works; novelty_pair, the rarity of the paper's two leading topics as a pair; breadth_refs, the share "
        f"of classified references outside geoscience. cnp and FWCI correlate at 0.99, so the six citation rows are "
        f"three associations. The prediction is the round-1 sign. All six citation "
        f"hypotheses have round-2 rho between {numbers['citation_hypotheses_round2_rho_range'][0]:.3f} and "
        f"{numbers['citation_hypotheses_round2_rho_range'][1]:.3f}. Borrowed from other fields counts the concepts, "
        f"methods, instruments or data from outside Earth science that the coder lists, and fields borrowed from counts "
        f"their distinct source fields; their correlation with breadth_refs is a convergent validity check of the coder "
        f"(the same property read from the text and from the reference list), not a workflow-outcome finding. "
        f"(b, c) The 28 field and venue hypotheses: a workflow feature against OpenAlex subfield or journal family "
        f"(groups of at least 10 round-1 papers; other papers pooled). (b) Count features: epsilon squared, "
        f"Kruskal-Wallis H / (n - 1), the share of the count's rank variance explained by the grouping; the direction "
        f"holds when round-2 group medians rank the shared named groups in the round-1 order (Spearman correlation of "
        f"the medians > 0; 'undefined' in the Direction column when tied medians leave it uncomputable, scored as not "
        f"held). (c) Binary and categorical "
        f"features: Cramer's V, bias-corrected (Bergsma 2013), from the chi-square of the feature-by-group table, 0 = "
        f"independent, 1 = the group determines the feature. The label names the round-1 leading group (largest "
        f"absolute rate minus the rate in all other papers) and whether its rate was higher or lower; the direction "
        f"holds when the round-2 difference has the same sign, while q comes from the test over all groups. "
        f"Whole-variable rows (all levels of composition or of "
        f"the decisive mode of inquiry) carry no direction. Bias-corrected V and epsilon squared cannot fall below 0, "
        f"so read their intervals as spread, not as tests; the V intervals are percentiles of the resampled "
        f"bias-corrected V, which is biased upward under resampling, so an interval can sit above its own estimate, "
        f"and with a 3-paper group the resamples that omit it give V near 0 (H32: interval reaching 0.0 beside "
        f"q {res['H32']['q']:.3f}). For round-2 leading groups of fewer than 10 papers the bootstrap interval of the "
        f"rate difference is degenerate when every paper of the group agrees (each resample of 3 of 3 is 3 of 3), so "
        f"exact Clopper-Pearson 95% intervals of the leading-group rate are given instead: {ex_txt}. "
        f"Bold labels: confirmed. A mode of inquiry is one of 13 kinds of epistemic work a step serves (observation, "
        f"simulation, synthesis across studies, reconstruction from traces, and others); the decisive mode of inquiry "
        f"is that of the single step without which the paper's main claim would not exist; composition is the coded "
        f"overall pattern of the walk (trace series: conditions found in nature rather than set, with observations "
        f"repeated over independent natural records such as sediment cores, deposits or landforms, ending in the best "
        f"explanation among stated rivals, where a trace is a natural record, not a seismic trace; capability first: "
        f"the method or instrument is built before the question is posed); nodes are the 15 kinds of move of graph "
        f"v0.4.2, one per step (N New capability, I Infer, D Design, P Protect, V Vary or replicate). Subfield names "
        f"are OpenAlex's; the subfield Artificial Intelligence holds only the topic Seismology and Earthquake Studies. "
        f"One model coder; no causal reading.")
    ps.save(fig, 'fig14_confirmatory', inputs=[PLAN, RES, MAN1, MAN2, DEFS, TJ], numbers=numbers, caption=caption)
    print(json.dumps({k: v for k, v in numbers.items() if not k.startswith('panel_')}, indent=1, default=str))
    print(caption)


if __name__ == '__main__':
    main()
