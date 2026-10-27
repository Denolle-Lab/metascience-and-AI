"""Figure 12: workflows and outcomes by field and venue, and whether the g17 workflow-outcome associations survive once
field or venue is held fixed (roadmap g20 analysis, paper figure).

Panels
  a  heat map of workflow use by subfield. Columns: all coded papers, then each OpenAlex subfield with at least
     MIN_GROUP (g20, 10) coded papers, n in the label; subfields under that size (g20 pools them) are in "All" only.
     Upper block, one row per graph node in paperstyle NODES order: share of papers whose final-paper sequence uses
     the node at least once. Lower block: share of papers whose decisive move is in each mode (g17 features(), the
     coded decisive_move.mode); modes outside the tested levels are summed into "other", so each column of this block
     sums to 100%. Sequential blue scale, 0 to 100%, the share written in each cell. Right margin: the g20 BH q of the
     subfield test for that row (chi-square permutation test of the feature against subfield, BH within g20
     question 3), "n.t." when g20 did not test the row (binary feature present in fewer than 10 or more than n - 10
     papers). A cell is outlined in ink when its row has q < 0.1 and the 95% bootstrap interval of that subfield's
     rate minus the rate in all other papers (g20 diff_ci) excludes 0.
  b  workflow length and citation by journal family, the venue path behind the attenuation in (c). Rows: g20 journal
     families with at least 10 coded papers, plus g20's pooled small families, sorted by median cnp. Four small panels:
     median steps (nodes in the final-paper sequence), median revisits (steps that return to a node already used),
     median cnp and median fwci (log axis, a ratio; dashed line at 1 = world average), each with its g20 95% bootstrap
     interval. Each
     title carries the Kruskal-Wallis epsilon^2 (share of rank variance explained by family) and BH q.
  c  the g17 associations with q < 0.1, one row per feature-outcome pair, grouped by outcome. Ink: the g17 Spearman rho
     with its 95% bootstrap interval, all papers together. Blue, orange, aqua: the within-stratum rank correlation
     (ranks centred within each subfield, each journal family, or each subfield x family cell) with its stratified
     bootstrap interval (g20 question 5). Filled marker = survives (same sign as g17 and BH q < 0.1 over all g20
     question-5 tests); open marker = does not. Right margin: how many of the three stratifications it survives
     (bold when fewer than three). The legend carries the g17 n (round 1 only, unlike panels a and b).

Definitions
  coded       a coding private/analysis/codings/api/<tag>/<key>.json for a key in the round's manifest that passes
              tools/check_coding.py validate(); tag calc1 (round 1) and r2 (round 2), rounds pooled as in g20. n is
              whatever exists at run time. g17, and so panel c, uses round 1 only.
  subfield    OpenAlex subfield of the paper's leading topic (machine label from title, abstract, venue, citations).
  family      journal family, g20 FAMILY_RULES (DOI prefix, then publisher, then journal name). AGU is its own family.
  cnp         OpenAlex citation normalized percentile, 0 to 1, citations ranked among works of the same field, year
              and type. fwci: field-weighted citation impact, citations over the mean of comparable works.
  novelty_pair  -log10(1 + number of 2017-2021 works sharing the paper's leading OpenAlex topic pair); higher = rarer.
  breadth_refs  share of the paper's classified references outside geoscience.

Numbers: rates for rows g20 tested come from topics_journals.json; the four nodes it did not test (and the "All"
column and "other" decisive share) are counted here from the codings with the same rule and grouping, and the
script checks that its own counts reproduce every g20 rate it draws (mismatches go to numbers['data_issues']).
Panels b and c draw g20 numbers only.

Inputs
  private/data/roadmap/derived/topics/topics_journals.json   g20 results (tools/roadmap/g20_topics_journals.py)
  private/data/roadmap/derived/{gold,r2}/metrics.json        subfield per paper (OpenAlex)
  private/data/roadmap/derived/{calc1,r2calc}/manifest.jsonl eligible papers per round
  private/analysis/codings/api/{calc1,r2}/*.json             codings (read only)

Outputs  private/data/roadmap/figures/paper/fig12_field_workflows.{pdf,png,json}
Run:     python tools/roadmap/figures/fig12_field_workflows.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.ticker import NullLocator as plt_null  # noqa: E402
import g20_topics_journals as g20  # noqa: E402
from g17_outcomes import features, NODES as G17_NODES  # noqa: E402

D = ps.DERIVED
TJ = D / 'topics' / 'topics_journals.json'
CMAP = LinearSegmentedColormap.from_list('seq', ['#ffffff'] + ps.SEQ)
STRATA = [('subfield', 'within subfield', ps.BLUE), ('family', 'within journal family', ps.ORANGE),
          ('subfield x family', 'within subfield \u00d7 family', ps.AQUA)]
OUT_LABEL = {'cnp': 'cnp (citation percentile)', 'fwci': 'fwci (field-weighted citations)',
             'novelty_pair': 'novelty_pair (rare topic pair)', 'breadth_refs': 'breadth_refs (references outside geoscience)'}
SHORT_SUB = {'Artificial Intelligence': 'Artificial intelligence', 'Atmospheric Science': 'Atmospheric science',
             'Earth-Surface Processes': 'Earth-surface processes', 'Geochemistry and Petrology': 'Geochemistry, petrology',
             'Geophysics': 'Geophysics', 'Oceanography': 'Oceanography', 'Water Science and Technology': 'Water science'}
SHORT_FAM = {'Springer Nature (non-portfolio)': 'Springer Nature, other', 'Wiley non-AGU': 'Wiley, non-AGU',
             'EGU/Copernicus': 'Copernicus (EGU)',
             g20.POOLED: 'Other families'}


def feature_label(f, kind):
    w = f.split(' ', 1)
    if w[0] == 'node':
        return f'Uses node {w[1][0]} ({w[1][2:]})'
    if w[0] == 'mode':
        return f'Uses {w[1]} mode'
    if w[0] == 'decisive':
        return f'Decisive mode: {w[1]}'
    if w[0] == 'composition':
        return f"Composition: {w[1].replace('_', ' ')}"
    lab = {'V check kinds': 'Kinds of V checks', 'distinct modes': 'Distinct modes', 'import fields': 'Fields borrowed from',
           'imports': 'Borrowed from other fields', 'revisits': 'Revisits', 'steps': 'Steps'}.get(f, f)
    return lab + (' (count)' if kind == 'num' else '')


def load_codings(issues):
    """{key: (coding, subfield)} for every valid coding in either round, same rule as g20 coded_keys()."""
    out = []
    for name, sset, calc, tag, _ in g20.ROUNDS:
        man, met = D / calc / 'manifest.jsonl', D / sset / 'metrics.json'
        if not man.is_file() or not met.is_file():
            continue
        elig = [json.loads(x)['key'] for x in man.read_text().splitlines() if x.strip()]
        m = {'g22_' + r['id']: r for r in g20.load(met)}
        for k, c in g20.coded_keys(tag, elig).items():
            if k not in m:
                issues.append(f'{name}: coded key {k} has no metrics row')
                continue
            out.append((k, c, m[k].get('subfield') or 'unknown'))
    return out


def main():
    tj = ps.read_json(TJ)
    T = tj['data'] if 'data' in tj else tj
    issues = []
    wf = {(r['grouping'], r['feature']): r for r in T['workflows']['rows']}
    groupings = T['workflows']['groupings']

    # ---------- (a) data: node and decisive rates by subfield ----------
    papers = load_codings(issues)
    n_all = len(papers)
    if n_all != T['workflows']['n_papers']:
        issues.append(f"codings now {n_all}, g20 ran on {T['workflows']['n_papers']}: rerun g20_topics_journals.py")
    subs = sorted((g for g in groupings['subfield']['groups'] if g != g20.POOLED),
                  key=lambda g: -groupings['subfield']['groups'][g])
    pooled_subs = groupings['subfield']['pooled_into_other']
    cols = ['All'] + subs
    sub_of = {k: s for k, _, s in papers}
    F = {k: features(c) for k, c, _ in papers}
    dec = {k: c['decisive_move']['mode'] for k, c, _ in papers}
    members = {'All': list(F)} | {s: [k for k in F if sub_of[k] == s] for s in subs}
    ncol = {s: len(members[s]) for s in cols}
    for s in subs:
        if ncol[s] != groupings['subfield']['groups'][s]:
            issues.append(f"{s}: {ncol[s]} coded papers now, g20 had {groupings['subfield']['groups'][s]}")

    rows = []      # (label, feature key in g20 or None, rates per column, block)
    for n in ps.NODES:
        fname = f'node {n} {G17_NODES[n]}'
        rates = [float(np.mean([F[k].get('bin:' + fname, False) for k in members[c]])) if members[c] else np.nan
                 for c in cols]
        rows.append((f'{n}  {ps.NODE_NAMES[n]}', fname, rates, 'node'))
    dec_levels = sorted({f.split(' ', 1)[1] for (g, f), r in wf.items()
                         if g == 'subfield' and f.startswith('decisive ') and r['kind'] == 'binary'},
                        key=lambda m: -sum(dec[k] == m for k in F))
    for m in dec_levels:
        rates = [float(np.mean([dec[k] == m for k in members[c]])) if members[c] else np.nan for c in cols]
        rows.append((m, f'decisive {m}', rates, 'decisive'))
    other_modes = Counter(dec[k] for k in F if dec[k] not in dec_levels)
    rows.append(('other', None, [float(np.mean([dec[k] not in dec_levels for k in members[c]])) for c in cols], 'decisive'))

    # check own counts against every g20 rate drawn; collect q and outlined cells
    cell_marks, row_q, a_numbers = [], [], {}
    for i, (lab, fname, rates, block) in enumerate(rows):
        r = wf.get(('subfield', fname)) if fname else None
        if r:
            if abs(r['prevalence'] - rates[0]) > 0.0015:
                issues.append(f'{fname}: overall rate {rates[0]:.3f} here, g20 {r["prevalence"]}')
            for j, s in enumerate(subs, 1):
                if abs(r['groups'][s]['rate'] - rates[j]) > 0.0015:
                    issues.append(f'{fname} in {s}: rate {rates[j]:.3f} here, g20 {r["groups"][s]["rate"]}')
                ci = r['groups'][s]['diff_ci']
                if r['q'] < 0.1 and ci and (ci[0] > 0 or ci[1] < 0):
                    cell_marks.append((i, j))
        row_q.append(r['q'] if r else None)
        a_numbers[lab] = {'rate_by_column': {c: round(v, 3) for c, v in zip(cols, rates)},
                          'g20_q_subfield': r['q'] if r else 'not tested',
                          'g20_cramers_v_bc': [r['cramers_v_bc'], r['v_bc_ci']] if r else None,
                          'outlined': [cols[j] for (ii, j) in cell_marks if ii == i]}
    dec_whole = wf[('subfield', 'decisive (whole variable)')]

    # ---------- layout (inches, explicit so the label columns of a and c line up) ----------
    W, H = ps.DOUBLE, 8.8
    fig = ps.figure(W, H)[0]
    fig.clf()
    box = lambda x, y, w, h: fig.add_axes([x / W, y / H, w / W, h / H])  # noqa: E731
    ax = box(1.12, 4.45, 2.6, 3.5)
    bax = [box(5.2, 6.6, 0.92, 1.1), box(6.22, 6.6, 0.92, 1.1), box(5.2, 4.75, 0.92, 1.1), box(6.22, 4.75, 0.92, 1.1)]
    cax = box(2.62, 0.45, 4.1, 3.4)
    plabel = lambda x, y, k: fig.text(x / W, y / H, f'({k})', fontsize=ps.LABEL, fontweight='bold', va='bottom', ha='left')  # noqa: E731

    # ---------- (a) heat map ----------
    gap = 1.25
    ys, y = [], 0.0
    for i, (_, _, _, block) in enumerate(rows):
        if i and block != rows[i - 1][3]:
            y += gap
        ys.append(y)
        y += 1
    xs = np.arange(len(cols)) + np.array([0] + [0.25] * len(subs))        # small gap after "All"
    for i, (lab, fname, rates, block) in enumerate(rows):
        for j, v in enumerate(rates):
            ax.add_patch(Rectangle((xs[j] - 0.5, ys[i] - 0.5), 1, 1, facecolor=CMAP(v), edgecolor='white', linewidth=0.6))
            ax.text(xs[j], ys[i], f'{100 * v:.0f}', ha='center', va='center', fontsize=5.5,
                    color='white' if v >= 0.55 else ps.INK)
    for i, j in cell_marks:
        ax.add_patch(Rectangle((xs[j] - 0.46, ys[i] - 0.46), 0.92, 0.92, fill=False, edgecolor=ps.INK, linewidth=0.9,
                               zorder=4))
    ax.set_xlim(xs[0] - 0.5, xs[-1] + 0.5)
    ax.set_ylim(ys[-1] + 0.5, -2.1)
    ax.set_yticks(ys, [r[0] for r in rows])
    ax.tick_params(axis='y', length=0, labelsize=ps.SMALL, pad=2)
    ax.set_xticks(xs, [f'All coded ({ncol["All"]})'] + [f'{g20.subfield_display(s, T, SHORT_SUB)} ({ncol[s]})' for s in subs])
    ax.xaxis.tick_top()
    ax.tick_params(axis='x', length=0, labelsize=ps.SMALL, pad=1)
    plt_labels = ax.get_xticklabels()
    for t in plt_labels:
        t.set_rotation(38)
        t.set_ha('left')
        t.set_rotation_mode('anchor')
    for sp in ax.spines.values():
        sp.set_visible(False)
    # block headers
    first_dec = next(i for i, r in enumerate(rows) if r[3] == 'decisive')
    ax.text(xs[0] - 0.5, ys[0] - 0.75, 'Nodes used (% of papers)', ha='left', va='bottom', fontsize=ps.SMALL,
            fontweight='bold', color=ps.INK)
    ax.text(xs[0] - 0.5, ys[first_dec] - 0.75, f"Decisive mode (% of papers; whole variable: Cram\u00e9r's V = {dec_whole['cramers_v_bc']}, "
            f"q = {dec_whole['q']:.3f})", ha='left', va='bottom', fontsize=ps.SMALL, fontweight='bold', color=ps.INK)
    # q column
    qx = xs[-1] + 0.62
    ax.text(qx, ys[0] - 0.75, 'q', ha='left', va='bottom', fontsize=ps.SMALL, fontweight='bold', color=ps.INK,
            clip_on=False)
    for i, q in enumerate(row_q):
        if rows[i][1] is None:
            continue
        s = 'n.t.' if q is None else (f'{q:.3f}' if q < 0.1 else f'{q:.2f}')
        ax.text(qx, ys[i], s, ha='left', va='center', fontsize=5.5, clip_on=False,
                color=ps.INK if (q is not None and q < 0.1) else ps.MUTED,
                fontweight='bold' if (q is not None and q < 0.1) else 'normal')
    plabel(0.02, 8.55, 'a')

    # ---------- (b) family: steps, revisits, cnp ----------
    fam = groupings['family']['groups']
    ocf = {r['outcome']: r for r in T['outcomes_by_group']['rows'] if r['population'] == 'coded' and r['grouping'] == 'family'}
    cnp_f = ocf['cnp']
    fams = sorted(fam, key=lambda f: (f == g20.POOLED, -cnp_f['groups'][f]['median']))
    b_specs = [('steps', wf[('family', 'steps')], 'Steps'), ('revisits', wf[('family', 'revisits')], 'Revisits'),
               ('cnp', cnp_f, 'cnp'), ('fwci', ocf['fwci'], 'fwci')]
    b_numbers = {}
    for j, (key, r, title) in enumerate(b_specs):
        a = bax[j]
        for i, f in enumerate(fams):
            g = r['groups'][f]
            m, (lo, hi) = g['median'], g['median_ci']
            col = ps.MUTED if f == g20.POOLED else ps.INK
            a.plot([lo, hi], [i, i], color=col, linewidth=0.9, solid_capstyle='butt', zorder=2)
            a.plot(m, i, 'o', color=col, ms=3.4, mec='white', mew=0.5, zorder=3)
        a.set_ylim(len(fams) - 0.4, -0.6)
        a.set_yticks(range(len(fams)), [f'{SHORT_FAM.get(f, f)} ({fam[f]})' for f in fams] if j % 2 == 0 else [])
        a.tick_params(axis='y', length=0)
        a.spines['left'].set_visible(False)
        eps, q = r['epsilon2'], r['q']
        a.set_title(f'{title}\n$\\epsilon^2$ = {eps:.2f}, q = {q:.4f}', fontsize=ps.SMALL, pad=3, loc='center')
        ps.grid(a, 'x')
        b_numbers[key] = {'epsilon2': eps, 'epsilon2_ci': r['epsilon2_ci'], 'p': r['p'], 'q': q,
                          'median_ci_by_family': {f: [r['groups'][f]['median'], *r['groups'][f]['median_ci']] for f in fams}}
    bax[2].set_xlim(0, 1)
    bax[2].set_xticks([0, 0.5, 1], ['0', '0.5', '1'])
    lo_f = min(v[1] for v in b_numbers['fwci']['median_ci_by_family'].values())
    hi_f = max(v[2] for v in b_numbers['fwci']['median_ci_by_family'].values())
    if lo_f > 0:   # fwci is a ratio: log axis so 0.3 and 1.4 sit symmetric about the world average
        bax[3].set_xscale('log')
        bax[3].set_xlim(lo_f / 1.25, hi_f * 1.25)
        tk = [t for t in (0.25, 0.5, 1, 2, 4, 8) if lo_f / 1.25 <= t <= hi_f * 1.25]
        bax[3].set_xticks(tk, [f'{t:g}' for t in tk])
        bax[3].xaxis.set_minor_locator(plt_null())
    else:
        bax[3].set_xlim(left=0)
    bax[3].axvline(1, color=ps.MUTED, linewidth=0.6, linestyle=(0, (3, 2)), zorder=1)
    fig.text(6.18 / W, 4.42 / H, 'Median by journal family, 95% bootstrap interval', ha='center', va='center',
             fontsize=ps.SMALL, color=ps.INK2)
    plabel(4.05, 8.08, 'b')

    # ---------- (c) confounding ----------
    conf = T['confounding']['rows']
    order = ['cnp', 'fwci', 'novelty_pair', 'breadth_refs']
    conf = sorted(conf, key=lambda r: (order.index(r['outcome']) if r['outcome'] in order else 9, -r['g17_rho']))
    cy, y, heads, labels = [], 0.0, [], []
    last = None
    for r in conf:
        if r['outcome'] != last:
            heads.append((y, r['outcome']))
            y += 0.85
            last = r['outcome']
        cy.append(y)
        labels.append(feature_label(r['feature'], r['type']))
        y += 1
    off = [-0.33, -0.11, 0.11, 0.33]
    c_numbers = []
    for r, yy in zip(conf, cy):
        if r['n_now'] != r['g17_n']:
            issues.append(f"{r['feature']} ~ {r['outcome']}: g17 n {r['g17_n']}, g20 recheck n {r['n_now']}")
        cax.plot(r['g17_ci'], [yy + off[0]] * 2, color=ps.INK, linewidth=0.9, solid_capstyle='butt', zorder=2)
        cax.plot(r['g17_rho'], yy + off[0], 'o', color=ps.INK, ms=2.8, mec='white', mew=0.4, zorder=3)
        surv = 0
        rec = {'feature': r['feature'], 'outcome': r['outcome'], 'g17': [r['g17_rho'], *r['g17_ci']], 'g17_q': r['g17_q']}
        for k, (s, _, col) in enumerate(STRATA, 1):
            v = r['strata'].get(s)
            if not v:
                continue
            cax.plot(v['ci'], [yy + off[k]] * 2, color=col, linewidth=0.9, solid_capstyle='butt', zorder=2)
            cax.plot(v['rho_within'], yy + off[k], 'o', ms=2.8, zorder=3, mew=0.9,
                     mfc=col if v['survives'] else 'white', mec=col)
            surv += v['survives']
            rec[s] = [v['rho_within'], *v['ci'], v['q'], v['survives']]
        cax.text(1.005, yy, f'{surv} of 3', transform=cax.get_yaxis_transform(), ha='left', va='center',
                 fontsize=ps.SMALL, color=ps.INK2 if surv == 3 else ps.INK, clip_on=False,
                 fontweight='bold' if surv < 3 else 'normal')
        rec['survives_of_3'] = surv
        c_numbers.append(rec)
    cax.axvline(0, color=ps.MUTED, linewidth=0.7, zorder=1)
    cax.set_yticks(cy, labels)
    cax.tick_params(axis='y', length=0, labelsize=ps.SMALL)
    cax.spines['left'].set_visible(False)
    for yh, o in heads:
        cax.text(-0.005, yh + 0.05, OUT_LABEL.get(o, o), transform=cax.get_yaxis_transform(), ha='right', va='center',
                 fontsize=ps.SMALL, fontweight='bold', color=ps.INK, clip_on=False)
    cax.text(1.005, -0.6, 'survives', transform=cax.get_yaxis_transform(), ha='left', va='center', fontsize=ps.SMALL,
             fontweight='bold', color=ps.INK, clip_on=False)
    cax.set_ylim(y - 0.4, -1.0)
    lo = min(min(r['g17_ci'][0], *[v['ci'][0] for v in r['strata'].values() if v]) for r in conf)
    hi = max(max(r['g17_ci'][1], *[v['ci'][1] for v in r['strata'].values() if v]) for r in conf)
    cax.set_xlim(np.floor(lo * 10) / 10 - 0.02, np.ceil(hi * 10) / 10 + 0.02)
    cax.set_xlabel('Spearman rank correlation of workflow feature with outcome (95% bootstrap interval)')
    ps.grid(cax, 'x')
    handles = [Line2D([], [], color=ps.INK, marker='o', ms=3.4, mec='white', linewidth=0.9, label=f"all papers (n = {conf[0]['g17_n']})")]
    handles += [Line2D([], [], color=col, marker='o', ms=3.4, mfc=col, mec=col, linewidth=0.9, label=lab)
                for _, lab, col in STRATA]
    handles += [Line2D([], [], color=ps.INK2, marker='o', ms=3.4, mfc='white', mec=ps.INK2, linestyle='none',
                       label='open = does not survive')]
    cax.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.42, 1.0), ncol=5, handlelength=1.3,
               columnspacing=0.9, handletextpad=0.4, fontsize=ps.SMALL, borderaxespad=0.3)
    plabel(0.02, 3.95, 'c')

    # ---------- numbers and caption ----------
    surv = T['confounding']['survivors']
    surv_ci = T['confounding']['survivors_ci_excludes_zero']
    nconf = T['confounding']['g17_rows_rechecked']
    numbers = {'n_coded_pooled': n_all, 'n_coded_g20': T['workflows']['n_papers'], 'n_by_round': {
        k: v.get('coded') for k, v in T['n'].items() if isinstance(v, dict)},
        'subfield_columns': {c: ncol[c] for c in cols}, 'subfields_pooled_not_shown': pooled_subs,
        'a_rates': a_numbers, 'a_outlined_cells': [[rows[i][0], cols[j]] for i, j in cell_marks],
        'a_decisive_whole_variable': {'cramers_v_bc': dec_whole['cramers_v_bc'], 'ci': dec_whole['v_bc_ci'],
                                      'p': dec_whole['p'], 'q': dec_whole['q']},
        'a_decisive_other_modes': dict(other_modes),
        'b_family_groups': fam, 'b_family_pooled': groupings['family']['pooled_into_other'], 'b': b_numbers,
        'c_rows': c_numbers, 'c_survivors': surv, 'c_survivors_ci_excludes_zero': surv_ci,
        'g20_workflow_tests': T['workflows']['tests'], 'g20_workflow_q_below_0.1': T['workflows']['q_below_0.1'],
        'data_issues': issues}

    nodes_untested = [r[0].split()[0] for r, q in zip(rows, row_q) if r[3] == 'node' and q is None]
    nodes_sig = [r[0].split()[0] for r, q in zip(rows, row_q) if r[3] == 'node' and q is not None and q < 0.1]
    st = {(r['feature'], r['outcome']): r for r in conf}
    lost = [f"{feature_label(r['feature'], r['type']).lower()} with {r['outcome']}" for r in conf
            if not all(v and v['survives'] for v in r['strata'].values())]
    fam_steps = b_numbers['steps']['median_ci_by_family']
    fam_cnp = b_numbers['cnp']['median_ci_by_family']
    top_f, low_f = fams[0], [f for f in fams if f != g20.POOLED][-1]
    cap = (f"Workflows and outcomes by field and venue, and the confounding check. Panels a and b: {n_all} research "
           "articles published in 2022 and coded by a language model (Claude Opus 5.5, codebook 1.5.0); panel c: the "
           f"round-1 papers used by the workflow-outcome analysis (n = {conf[0]['g17_n']}). Each paper is coded as a sequence "
           "of steps; each step carries a node, the kind of move in the modes-of-inquiry graph (N new capability, "
           "E explore, O observe, I infer a latent quantity, Q question, H hypothesize rivals, S simulate or derive "
           "expectations, D design the test, F find or set conditions, C compare, V vary or replicate, X exclude a rival, "
           "K keep the claim, P protect the claim by revising an auxiliary assumption, R refine), and a mode, the style of "
           "inquiry the step belongs to (methods: new inference or computational capability; estimation: a latent "
           "quantity with uncertainty; simulation: model forecasts or consequences; reconstruction: a past event from its "
           "traces; observation: describing a phenomenon; hypothesis: testing among rivals; regularities: an empirical "
           "relation with its range; theory: consequences derived from first principles; instruments: building or "
           "characterizing an apparatus or sensor; exploration: establishing that a phenomenon is real; synthesis: "
           "combining results across studies; robustness: varying conditions to see whether a result holds; question: "
           "posing or sharpening the question). A node is one of 15 kinds of move; a mode is one of 13 styles of inquiry "
           "the move serves. The decisive move is the single step, with its mode, without which the "
           "paper's main claim would not exist. Field is the subfield of the paper's leading topic in OpenAlex (an open "
           "bibliographic database), a machine label from title, abstract, venue and citations. OpenAlex files topics, not papers, under subfields, so "
           "a subfield label names its dominant leading topic where one topic holds at least 60% of the subfield's coded "
           "papers: the subfield Artificial Intelligence holds only the seismology topic (OpenAlex files Seismology and "
           "Earthquake Studies under Computer Science), and Atmospheric Science is mostly the cryosphere topic (glaciology, "
           "mainly The Cryosphere). Venue is the journal family, grouped by DOI prefix and publisher (AGU apart from Wiley; "
           "Copernicus, mostly European Geosciences Union journals). "
           f"(a) Share of papers in each subfield that use each node at least once (upper block) and whose decisive move "
           f"is in each mode (lower block; modes with fewer than 10 papers summed as other, so columns sum to 100%). "
           f"Subfields with fewer than 10 coded papers ({', '.join(f'{k} {v}' for k, v in pooled_subs.items())}) appear "
           "in All only. The q column is the Benjamini-Hochberg adjusted p (BH q; rows with q < 0.1 are expected to "
           "include at most about 10% false discoveries) of a permutation chi-square test of that row against subfield, "
           f"adjusted over all {T['workflows']['tests']} workflow tests (every binary, count and categorical feature, tested "
           "once against subfield and once against journal family); n.t. marks rows not tested because fewer "
           f"than 10 or more than n - 10 papers have the feature (nodes {', '.join(nodes_untested)}). Cram\u00e9r's V for the "
           "decisive mode as a whole is bias-corrected, 0 when mode is independent of subfield and 1 when subfield "
           "determines it. An outlined cell has row q < 0.1 and a 95% bootstrap interval of its rate minus the rate in "
           "all other papers that excludes zero, above or below (a 0 can be outlined). "
           f"Nodes with q < 0.1: {', '.join(nodes_sig)}. "
           f"(b) Median workflow length (steps in the coded sequence, consecutive steps on the same node counted "
           "separately), revisits (steps whose node already occurred earlier in that sequence, so a consecutive repeat "
           "counts), cnp (OpenAlex citation normalized percentile, 0 to 1: a paper's citation count ranked among works of "
           "the same OpenAlex subfield, year and type) and fwci (field-weighted citation impact: citations divided by the "
           "mean for works of the same subfield, year and type; log axis, dashed line at 1 = world average; citations are "
           "skewed, so the median paper sits below 1) by journal family, with 95% bootstrap intervals (2000 "
           "resamples of papers). Epsilon squared is the share of rank variance explained by family (Kruskal-Wallis "
           "rank analysis of variance), with BH q. Families sorted by median cnp: "
           f"{SHORT_FAM.get(top_f, top_f)} {fam_steps[top_f][0]:g} steps and cnp {fam_cnp[top_f][0]:.2f}, "
           f"{SHORT_FAM.get(low_f, low_f)} {fam_steps[low_f][0]:g} steps and cnp {fam_cnp[low_f][0]:.2f}. Family is "
           "associated with both workflow length and citation, consistent with the weaker length-citation "
           "associations within family in (c). "
           f"(c) The {nconf} associations between a workflow feature and an outcome with q < 0.1 over the "
           f"{ps.read_json(D / 'outcomes' / 'outcomes.json')['tests']} workflow-outcome tests (cnp and fwci correlate at "
           "0.99, so the impact rows repeat one signal). Features: "
           "steps and revisits as in (b); decisive mode as in (a); uses a mode, at least one step in it; distinct modes, "
           "number of different modes in the sequence; borrowed from other fields, number of concepts, methods, instruments "
           "or data from outside Earth science that the coder lists (codebook section 6); fields borrowed from, number of "
           "distinct source fields (these two against breadth_refs are a convergent validity check of the coder, the same "
           "thing measured from the text and from the reference list, not workflow-outcome findings); composition capability "
           "first, the paper builds a new capability before posing its question; kinds of V checks, number of distinct "
           "kinds of check the paper performs itself (replication on new data, a second method, varied parameters, a "
           "control or reference, a new context, a rerun). Outcomes: cnp and fwci as in (b); novelty_pair, -log10(1 + "
           "number of 2017-2021 works sharing the paper's leading pair of OpenAlex topics), higher is rarer; "
           "breadth_refs, share of classified references outside geoscience. cnp and fwci are normalized within subfield by "
           "OpenAlex; novelty_pair and breadth_refs are not. Effect is Spearman rank correlation, ink for all papers "
           "together; coloured points recompute it within strata (ranks centred inside each subfield, journal family, or "
           "subfield-by-family cell, so only variation inside a stratum counts), with stratified bootstrap intervals "
           "(2000) and permutation p from shuffling outcomes within strata (5000). Filled: same sign and BH q < 0.1 over "
           f"the {sum(1 for r in conf for v in r['strata'].values() if v)} stratified tests; open: not. Survivors: "
           f"{surv['subfield']} of {nconf} within subfield, {surv['family']} within family, {surv['subfield x family']} "
           f"within subfield by family ({surv_ci['subfield']}, {surv_ci['family']} and {surv_ci['subfield x family']} with "
           f"an interval excluding zero). Not surviving all three: {'; '.join(lost) if lost else 'none'}. "
           "Exploratory: one model coder, small cells, citations at about four years. OpenAlex retrieved October 2026; "
           "figure date " + ps.TODAY + '.')

    inputs = [TJ, D / 'gold' / 'metrics.json', D / 'calc1' / 'manifest.jsonl', g20.CODINGS / 'calc1']
    for p in (D / 'r2' / 'metrics.json', D / 'r2calc' / 'manifest.jsonl', g20.CODINGS / 'r2'):
        if p.exists():
            inputs.append(p)
    ps.save(fig, 'fig12_field_workflows', inputs=inputs, numbers=numbers, caption=cap)
    print(json.dumps({k: numbers[k] for k in ('n_coded_pooled', 'subfield_columns', 'a_outlined_cells', 'c_survivors',
                                               'data_issues')}, indent=1))
    print(cap)


if __name__ == '__main__':
    main()
