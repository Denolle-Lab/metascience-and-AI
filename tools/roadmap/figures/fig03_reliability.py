"""Figure 3: reliability of the model coder (test-retest on gold papers, input-format test, Krippendorff's alpha).

Panels
  (a) test-retest: two independent codings of the same gold paper by the model coder (claude-opus-5-5 via the Batch API,
      codebook 1.5.0, graph v0.4.2), first coding from tag calc1, second from tag gold-r2. Only papers whose two codings
      both pass tools/check_coding.py validate() are kept (50 of the 51 gold papers coded twice; the gold-r2 coding of
      g22_W4297373829 fails with '$.tree[2]: unexpected aim'). Four match shares (entry state, entry node, outcome,
      decisive mode) and four similarity means (node-set and mode-set Jaccard, node-sequence and mode-sequence
      similarity = 1 - normalized edit distance), each with a 95% bootstrap interval over papers. Per-paper values of the
      four similarity measures (rounded to 2 decimals by agree()) are drawn as a vertically jittered grey strip.
  (b) format test (experiment E0, codebook 1.4.0, which also used graph v0.4.2: CODEBOOK.md header at commit 32b807e):
      agreement between two codings of the same paper in the same input format (repeat run, the noise floor) against
      agreement between codings made from different formats. Arms X (located XML text) and T (pdftotext text) were
      coded by a Claude Code paper-coder subagent (workflows/format-test-coding.js, no model id recorded); arms P (PDF)
      and PX (PDF plus XML text) by claude-opus-5-5 through the Batch API, so P-T, P-X, PX-T and PX-X pairs also cross
      the coding pipeline. Means over 6 papers, 95% bootstrap interval over papers. Format-test codings are not filtered
      by validate(), as in f01_format_test.py (the numbers of record).
  (c) the paired difference behind (b): per paper, between-format mean minus within-format mean, with the mean over the
      6 papers and its paired 95% bootstrap interval (papers resampled, both terms together). The two papers whose PDF was
      the discussion preprint (arms T and P coded another text version than arms X and PX) are drawn as open triangles;
      the 4-paper (same version) within and between means are recorded in the numbers and the caption.
  (d) Krippendorff's alpha (nominal) for the test-retest pairs of panel (a), with the 0.667 and 0.8 reference values,
      95% bootstrap interval over papers (node presence: all 15 node units of a paper resampled together). Fields whose
      alpha rests on a single paper outside the modal class are drawn as open circles without an interval.
Round 2 (tag r2) adds test-retest pairs only for papers coded both in round 2 and in round 1 or gold-r2. Round 2 is a
fresh 277-paper draw, so this is expected to stay at 0 pairs; the script records the count (numbers.round2_retest_pairs)
and picks such pairs up if they ever exist.

Agreement logic is the one of record: tools/check_coding.py agree() (as in g13_calc1_results.py and f01_format_test.py)
and g11_human_agreement.alpha_nominal(). The plotted point estimates are recomputed here from the codings and checked
against derived/calc1/results.json and derived/format_test/results.json; the script stops if they differ.

Inputs
  private/analysis/codings/api/calc1/*.json, gold-r2/*.json, r2/*.json (if present)   model codings
  private/analysis/codings/api/fmt-{P,PX}{1,2}/*.json                                 format test, Batch API arms
  private/data/roadmap/derived/format_test/codings/<key>.{X,T}{1,2}.json              format test, subagent arms
  private/data/roadmap/derived/format_test/design.json                               the 6 format-test papers
  private/data/roadmap/derived/calc1/results.json                                    g13 test-retest (check)
  private/data/roadmap/derived/format_test/results.json                              f01 agreement (check)
Outputs  private/data/roadmap/figures/paper/fig03_reliability.{pdf,png,json}
Run:     python tools/roadmap/figures/fig03_reliability.py
"""
from __future__ import annotations

import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402
from paperstyle import DERIVED, ROOT, read_json  # noqa: E402
from check_coding import agree, seq, v_status, validate  # noqa: E402
from g11_human_agreement import alpha_nominal  # noqa: E402

API = ROOT / 'private' / 'analysis' / 'codings' / 'api'
FT = DERIVED / 'format_test'
B = 2000
SEED = 2026
# papers whose PDF was the discussion preprint (format_test/report.md, second table): arms T and P coded another version
PREPRINT = ['g22_W4285387965', 'g22_W4283688628']
GRAPH_FOR_CODEBOOK = {'1.4.0': 'v0.4.2', '1.5.0': 'v0.4.2'}   # agents/coder/CODEBOOK.md header at 32b807e and at HEAD

BOOL = ['entry_state', 'entry_node', 'outcome', 'decisive_mode']
NUM = ['node_set_jaccard', 'mode_set_jaccard', 'node_seq_similarity', 'mode_seq_similarity']
MEASURES = BOOL + NUM
LABEL = {'entry_state': 'Entry state', 'entry_node': 'Entry node', 'outcome': 'Outcome', 'decisive_mode': 'Decisive mode',
         'node_set_jaccard': 'Node set (Jaccard)', 'mode_set_jaccard': 'Mode set (Jaccard)',
         'node_seq_similarity': 'Node sequence', 'mode_seq_similarity': 'Mode sequence'}
ALPHA = ['entry_state', 'outcome', 'claim_status', 'decisive_mode', 'composition', 'v_status', 'node_presence']
ALPHA_LABEL = {'entry_state': 'Entry state', 'outcome': 'Outcome', 'claim_status': 'Claim status',
               'decisive_mode': 'Decisive mode', 'composition': 'Composition', 'v_status': 'V status',
               'node_presence': 'Node presence'}


def load(tag: str) -> tuple[dict, dict]:
    """Valid codings of a tag by key, and the invalid ones (key -> first validation error)."""
    ok, bad = {}, {}
    for f in sorted((API / tag).glob('*.json')):
        try:
            c = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            bad[f.stem] = 'unreadable JSON'
            continue
        err = validate(c)
        if err:
            bad[c.get('key', f.stem)] = err[0]
        else:
            ok[c['key']] = c
    return ok, bad


def boot_mean(x: np.ndarray, rng) -> tuple[float, float]:
    idx = rng.integers(0, len(x), size=(B, len(x)))
    m = x[idx].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def alpha_units(field: str, a: dict, b: dict) -> list[list]:
    """Alpha units contributed by one paper coded twice (as in g13_calc1_results.py)."""
    if field == 'entry_state':
        return [[a['entry']['state'], b['entry']['state']]]
    if field == 'outcome':
        return [[a['end']['outcome'], b['end']['outcome']]]
    if field == 'claim_status':
        return [[a['end']['claim_status'], b['end']['claim_status']]]
    if field == 'decisive_mode':
        return [[a['decisive_move']['mode'], b['decisive_move']['mode']]]
    if field == 'composition':
        return [[a['composition'], b['composition']]]
    if field == 'v_status':
        return [[v_status(a)['v'], v_status(b)['v']]]
    sa, sb = seq(a, 'node'), seq(b, 'node')
    return [[n in sa, n in sb] for n in ps.NODES]


def test_retest():
    (r1, bad1), (r2, bad2) = load('calc1'), load('gold-r2')
    coded_twice = sorted(k for k in set(r2) | set(bad2) if k in r1 or k in bad1)
    dropped = {k: (bad1.get(k), bad2.get(k)) for k in coded_twice if k in bad1 or k in bad2}
    pair = sorted(k for k in r2 if k in r1)
    rows = [agree(r1[k], r2[k]) for k in pair]
    vals = {f: np.array([float(r[f]) for r in rows]) for f in MEASURES}
    rounds = ['round 1 (calc1 vs gold-r2)']
    r2_pairs = 0
    if (API / 'r2').is_dir():                       # round 2: retest pairs only where a paper was coded twice
        rr, _ = load('r2')
        other = {**r1, **r2}
        extra = sorted(k for k in rr if k in other and k not in pair)
        r2_pairs = len(extra)
        if extra:
            rows2 = [agree(other[k], rr[k]) for k in extra]
            for f in MEASURES:
                vals[f] = np.concatenate([vals[f], [float(r[f]) for r in rows2]])
            pair = pair + extra
            r1 = {**r1, **{k: other[k] for k in extra}}
            r2 = {**r2, **{k: rr[k] for k in extra}}
            rounds.append(f'round 2 (r2 vs earlier coding, {len(extra)} papers)')
    rng = np.random.default_rng(SEED)
    est = {f: (float(vals[f].mean()), *boot_mean(vals[f], rng)) for f in MEASURES}
    # alpha with a bootstrap over papers (all units of a paper resampled together)
    units = {fld: [alpha_units(fld, r1[k], r2[k]) for k in pair] for fld in ALPHA}
    alpha = {}
    rng = np.random.default_rng(SEED + 1)
    for fld in ALPHA:
        point = alpha_nominal([u for us in units[fld] for u in us])
        draws = []
        for _ in range(B):
            idx = rng.integers(0, len(pair), len(pair))
            a = alpha_nominal([u for i in idx for u in units[fld][i]])
            if a is not None:
                draws.append(a)
        # papers outside the modal class (either coding): when this is tiny, alpha rests on those few papers
        flat = [v for us in units[fld] for u in us for v in u]
        mode = max(set(flat), key=flat.count)
        outside = [k for k, us in zip(pair, units[fld]) if any(v != mode for u in us for v in u)]
        alpha[fld] = {'est': (point, float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))),
                      'undefined': B - len(draws), 'outside': outside, 'modal': str(mode),
                      'outside_values': {k: [str(v) for u in units[fld][pair.index(k)] for v in u] for k in outside[:3]}}
    cb = Counter(c.get('codebook_version') for t in (r1, r2) for k, c in t.items() if k in pair)
    return pair, vals, est, alpha, rounds, r2_pairs, coded_twice, dropped, cb


def format_test():
    keys = [p['key'] for p in read_json(FT / 'design.json')['papers']]
    within, between = defaultdict(list), defaultdict(list)          # per paper: list of agree() rows
    label_rows = defaultdict(lambda: defaultdict(list))             # label -> paper -> rows (for the check)
    meta = {'codebook': Counter(), 'coder': defaultdict(set), 'invalid': {}}
    for k in keys:
        cod = {}
        for arm in ['X', 'T', 'P', 'PX']:
            for rep in (1, 2):
                f = (FT / 'codings' / f'{k}.{arm}{rep}.json') if arm in ('X', 'T') else (API / f'fmt-{arm}{rep}' / f'{k}.json')
                if f.is_file():
                    c = json.loads(f.read_text())
                    cod[f'{arm}{rep}'] = c
                    meta['codebook'][c.get('codebook_version')] += 1
                    meta['coder'][arm].add(re.sub(r' replicate \d+$', '', str(c.get('coder'))))
                    err = validate(c)
                    if err:
                        meta['invalid'][f'{k}.{arm}{rep}'] = err[0]
        for a, b in itertools.combinations(sorted(cod), 2):
            ga, gb = re.sub(r'\d', '', a), re.sub(r'\d', '', b)
            m = agree(cod[a], cod[b])
            label = f'{ga} within' if ga == gb else '-'.join(sorted([ga, gb]))
            label_rows[label][k].append(m)
            (within if ga == gb else between)[k].append(m)
    # per paper: mean over within-format pairs and over between-format pairs (each label equally weighted:
    # every label has the same number of pairs per paper, 1 within and 4 between)
    pw = {f: np.array([np.mean([float(m[f]) for m in within[k]]) for k in keys]) for f in MEASURES}
    pb = {f: np.array([np.mean([float(m[f]) for m in between[k]]) for k in keys]) for f in MEASURES}
    rng = np.random.default_rng(SEED + 2)
    ew = {f: (float(pw[f].mean()), *boot_mean(pw[f], rng)) for f in MEASURES}
    eb = {f: (float(pb[f].mean()), *boot_mean(pb[f], rng)) for f in MEASURES}
    # paired difference: resample papers, both terms of a paper together
    rng = np.random.default_rng(SEED + 4)
    diff = {f: pb[f] - pw[f] for f in MEASURES}
    ed = {f: (float(diff[f].mean()), *boot_mean(diff[f], rng)) for f in MEASURES}
    same = np.array([k not in PREPRINT for k in keys])
    sub4 = {f: {'within': float(pw[f][same].mean()), 'between': float(pb[f][same].mean()),
                'between_minus_within': float(diff[f][same].mean())} for f in MEASURES}
    labels = {lab: {f: float(np.mean([np.mean([float(m[f]) for m in ms]) for ms in per.values()])) for f in MEASURES}
              for lab, per in label_rows.items()}
    npairs = {'within': sum(len(v) for v in within.values()), 'between': sum(len(v) for v in between.values())}
    meta['coder'] = {a: sorted(v) for a, v in meta['coder'].items()}
    return keys, ew, eb, ed, diff, sub4, labels, npairs, meta


def check(est, alpha, labels, n_pairs):
    tr = read_json(DERIVED / 'calc1' / 'results.json')['test_retest']
    if n_pairs == tr['papers']:      # only comparable when no round-2 pairs were added
        for f in BOOL:
            assert abs(round(est[f][0], 2) - tr[f + '_agree']) < 1e-9, (f, est[f][0], tr[f + '_agree'])
        for f in NUM:
            assert abs(round(est[f][0], 2) - tr[f + '_mean']) < 1e-9, (f, est[f][0], tr[f + '_mean'])
        for f in ALPHA:
            assert alpha[f]['est'][0] == tr['alpha'][f], (f, alpha[f]['est'][0], tr['alpha'][f])
    ftr = read_json(FT / 'results.json')['agreement']
    for lab, v in labels.items():
        for f in MEASURES:
            assert abs(round(v[f], 3) - ftr[lab][f]) < 1e-9, (lab, f, v[f], ftr[lab][f])


def dot(ax, y, e, color, size=4.2, z=4, open_=False, bar=True):
    if bar:
        ax.errorbar(e[0], y, xerr=[[e[0] - e[1]], [e[2] - e[0]]], fmt='none', ecolor=color, elinewidth=0.8, capsize=0,
                    zorder=z - 1)
    if open_:
        ax.plot(e[0], y, 'o', ms=size - 0.6, mfc='white', mec=color, mew=1.0, zorder=z, clip_on=False)
    else:
        ax.plot(e[0], y, 'o', ms=size, color=color, mec='white', mew=0.6, zorder=z, clip_on=False)


def style_axis(ax, n, xlabel, lim=(0, 1.04), ticks=(0, 0.2, 0.4, 0.6, 0.8, 1.0), ticklabels=('0', '0.2', '0.4', '0.6', '0.8', '1')):
    ax.set_xlim(*lim)
    ax.set_ylim(n - 0.5, -1.1)
    ax.set_xticks(list(ticks))
    ax.set_xticklabels(list(ticklabels))
    ax.set_xlabel(xlabel)
    ax.tick_params(axis='y', length=0)
    ax.spines['left'].set_visible(False)
    ps.grid(ax, 'x')


def head(ax, letter: str, title: str, x: float) -> None:
    """Panel label through ps.panel, then the panel's subset name just right of it, on the same baseline."""
    ps.panel(ax, letter, x=x)
    ax.annotate(title, xy=(x, 1.04), xycoords='axes fraction', xytext=(15, 0), textcoords='offset points',
                fontsize=ps.FONT, color=ps.INK, va='bottom', ha='left')


def group_headers(ax, ys, color):
    ax.text(0.02, ys[0] - 0.75, 'Share of papers that match', fontsize=ps.SMALL, color=color, va='center',
            transform=ax.get_yaxis_transform())
    ax.text(0.02, ys[len(BOOL)] - 0.75, 'Mean similarity', fontsize=ps.SMALL, color=color, va='center',
            transform=ax.get_yaxis_transform())


def main():
    pair, vals, est, alpha, rounds, r2_pairs, coded_twice, dropped, cb_tr = test_retest()
    fkeys, ew, eb, ed, fdiff, sub4, flabels, fpairs, fmeta = format_test()
    check(est, alpha, flabels, len(pair))
    cb_ft = sorted(v for v in fmeta['codebook'] if v)
    cb_a = sorted(v for v in cb_tr if v)

    ps.setup()
    fig = ps.plt.figure(figsize=(ps.DOUBLE, 2.85))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 0.8], wspace=0.17, left=0.118, right=0.70, bottom=0.165, top=0.87)
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1], sharey=ax_a)
    ax_c = fig.add_subplot(gs[2], sharey=ax_a)
    ax_d = fig.add_axes([0.848, 0.165, 0.985 - 0.848, 0.87 - 0.165])
    ys = np.arange(len(MEASURES), dtype=float)
    ys[len(BOOL):] += 0.5                           # gap between match shares and similarity means
    n = ys[-1] + 1

    # (a) test-retest
    jit = np.random.default_rng(SEED + 3)
    for f, y in zip(MEASURES, ys):
        if f in NUM:
            v = vals[f]
            ax_a.scatter(v, y + jit.uniform(-0.28, 0.28, len(v)), s=3, color=ps.NEUTRAL, linewidths=0, zorder=2, clip_on=False)
        dot(ax_a, y, est[f], ps.BLUE)
    ax_a.set_yticks(ys)
    ax_a.set_yticklabels([LABEL[f] for f in MEASURES])
    style_axis(ax_a, n, 'Agreement between two codings')
    group_headers(ax_a, ys, ps.INK2)
    ax_a.text(0.02, ys[len(BOOL)] - 0.42, '(grey: single papers)', fontsize=ps.SMALL, color=ps.MUTED, va='center')
    ps.panel(ax_a, 'a', x=-0.56)
    ax_a.set_title(f'Same model, two runs, {len(pair)} papers', fontsize=ps.FONT, loc='left', color=ps.INK)

    # (b) format test: within (filled, upper) and between (open, lower)
    off = 0.17
    for f, y in zip(MEASURES, ys):
        dot(ax_b, y - off, ew[f], ps.BLUE, size=3.8)
        dot(ax_b, y + off, eb[f], ps.ORANGE, size=3.8, open_=True)
    style_axis(ax_b, n, 'Agreement between two codings')
    ax_b.tick_params(axis='y', labelleft=False)
    group_headers(ax_b, ys, ps.MUTED)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker='o', ls='', color=ps.BLUE, mec='white', mew=0.6, ms=4, label='Same format (upper)'),
         Line2D([], [], marker='o', ls='', mfc='white', mec=ps.ORANGE, mew=1.0, ms=3.4, label='Different formats (lower)')]
    ax_b.legend(handles=h, loc='upper left', bbox_to_anchor=(0.0, 0.90), handletextpad=0.1, borderaxespad=0.2,
                labelcolor=ps.INK, labelspacing=0.3)
    head(ax_b, 'b', f'Format test, {len(fkeys)} papers', x=-0.04)

    # (c) paired difference, between minus within, per paper
    ax_c.axvline(0, color=ps.INK2, lw=0.6, zorder=1)
    offs = np.linspace(-0.27, 0.27, len(fkeys))
    for f, y in zip(MEASURES, ys):
        for i, k in enumerate(fkeys):
            x = fdiff[f][i]
            if k in PREPRINT:
                ax_c.plot(x, y + offs[i], '^', ms=3.0, mfc='white', mec=ps.INK2, mew=0.7, zorder=3, clip_on=False)
            else:
                ax_c.plot(x, y + offs[i], 'o', ms=2.4, color=ps.NEUTRAL, mew=0, zorder=2, clip_on=False)
        dot(ax_c, y, ed[f], ps.BLUE, size=3.8, z=5)
    style_axis(ax_c, n, 'Between minus within', lim=(-0.4, 0.15), ticks=(-0.3, -0.2, -0.1, 0, 0.1),
               ticklabels=('\u22120.3', '', '\u22120.1', '0', '0.1'))
    ax_c.tick_params(axis='y', labelleft=False)
    yk = ys[MEASURES.index('node_seq_similarity')]
    i_pp = max(PREPRINT, key=lambda k: -fdiff['node_seq_similarity'][fkeys.index(k)])
    xi = fdiff['node_seq_similarity'][fkeys.index(i_pp)]
    ax_c.annotate('preprint PDF', xy=(xi, yk + offs[fkeys.index(i_pp)]), xytext=(xi - 0.02, yk - 0.62), fontsize=ps.SMALL,
                  color=ps.INK2, ha='center', va='center',
                  arrowprops=dict(arrowstyle='-', color=ps.INK2, lw=0.5, shrinkA=1, shrinkB=2))
    box = dict(boxstyle='square,pad=0.05', fc='white', ec='none')
    ax_c.text(-0.39, ys[0] - 0.75, 'Blue: mean, paired CI', fontsize=ps.SMALL, color=ps.INK2, va='center', zorder=6, bbox=box)
    ax_c.text(-0.39, ys[len(BOOL)] - 0.75, 'Grey: single papers', fontsize=ps.SMALL, color=ps.INK2, va='center', zorder=6,
              bbox=box)
    head(ax_c, 'c', 'Paired difference', x=-0.06)

    # (d) Krippendorff's alpha
    ya = np.arange(len(ALPHA), dtype=float)
    for ref, txt, ha, dx in [(0.667, '0.667', 'right', -0.015), (0.8, '0.8', 'left', 0.015)]:
        ax_d.axvline(ref, color=ps.INK2, lw=0.6, ls=(0, (3, 2)), zorder=1)
        ax_d.text(ref + dx, -0.8, txt, fontsize=ps.SMALL, color=ps.INK2, ha=ha, va='center')
    single = {}
    for fld, y in zip(ALPHA, ya):
        a = alpha[fld]
        single[fld] = len(a['outside']) == 1 and a['undefined'] > 0.1 * B
        dot(ax_d, y, a['est'], ps.BLUE, open_=single[fld], bar=not single[fld])
        if single[fld]:                          # interval undefined in many resamples: say what alpha rests on
            ax_d.text(a['est'][0] - 0.05, y, f'rests on 1 of {len(pair)} papers', fontsize=ps.SMALL,
                      color=ps.INK2, ha='right', va='center', zorder=5,
                      bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'))
    ax_d.set_yticks(ya)
    ax_d.set_yticklabels([ALPHA_LABEL[f] for f in ALPHA])
    style_axis(ax_d, len(ALPHA), "Krippendorff's alpha (nominal)")
    ax_d.set_ylim(len(ALPHA) - 0.5, -1.1)
    ps.panel(ax_d, 'd', x=-0.62)
    ax_d.set_title('Two runs, chance-corrected', fontsize=ps.FONT, loc='left', color=ps.INK)

    r3 = lambda t: [round(x, 3) for x in t]
    sing = [f for f in ALPHA if single[f]]
    sing_txt = ' and '.join(ALPHA_LABEL[f].split(' (')[0].replace('V status', 'V status') for f in sing)
    sing_papers = ', '.join(f'{alpha[f]["outside"][0]} for {ALPHA_LABEL[f].split(" (")[0].lower().replace("v status", "V status")}'
                            for f in sing)
    sing_modal = ', respectively '.join(f'"{alpha[f]["modal"]}"' for f in sing)
    numbers = {
        'rounds_drawn': rounds, 'round2_retest_pairs': r2_pairs,
        'bootstrap': {'resamples': B, 'seed_a': SEED, 'seed_alpha': SEED + 1, 'seed_b': SEED + 2, 'seed_c_paired': SEED + 4,
                      'unit': 'paper', 'interval': 'percentile 2.5-97.5'},
        'a_test_retest': {'gold_papers_coded_twice': len(coded_twice), 'dropped_invalid': dropped, 'papers': len(pair),
                          'codebook_versions': dict(cb_tr),
                          **{f: {'estimate_lo_hi': r3(est[f])} for f in MEASURES},
                          'per_paper': {f: [float(x) for x in vals[f]] for f in NUM},
                          'per_paper_share_of_1.0': {f: round(float((vals[f] == 1.0).mean()), 3) for f in NUM}},
        'b_format_test': {'papers': len(fkeys), 'keys': fkeys, 'pairs': fpairs, 'codebook_versions': dict(fmeta['codebook']),
                          'graph_version': {v: GRAPH_FOR_CODEBOOK.get(v) for v in cb_ft}, 'coder_by_arm': fmeta['coder'],
                          'invalid_codings_not_filtered': fmeta['invalid'],
                          'within_format': {f: r3(ew[f]) for f in MEASURES},
                          'between_format': {f: r3(eb[f]) for f in MEASURES},
                          'between_minus_within': {f: round(eb[f][0] - ew[f][0], 3) for f in MEASURES},
                          'by_pair_label': {lab: {f: round(v[f], 3) for f in MEASURES} for lab, v in sorted(flabels.items())},
                          'same_version_4_papers': {f: {k2: round(v2, 3) for k2, v2 in sub4[f].items()} for f in MEASURES},
                          'preprint_papers': PREPRINT},
        'c_paired_difference': {'estimate_lo_hi': {f: r3(ed[f]) for f in MEASURES},
                                'per_paper': {f: {k: round(float(fdiff[f][i]), 3) for i, k in enumerate(fkeys)} for f in MEASURES}},
        'd_alpha': {f: {'estimate_lo_hi': r3(alpha[f]['est']), 'resamples_undefined': alpha[f]['undefined'],
                        'modal_class': alpha[f]['modal'], 'papers_outside_modal_class': len(alpha[f]['outside']),
                        'outside_keys': alpha[f]['outside'] if len(alpha[f]['outside']) <= 3 else None,
                        'outside_values': alpha[f]['outside_values'] if len(alpha[f]['outside']) <= 3 else None,
                        'drawn_open_without_interval': single[f]} for f in ALPHA},
        'reference_lines_alpha': [0.667, 0.8],
    }
    fmt0 = lambda x: '0' if abs(x) < 5e-4 else f'{x:+.3f}'
    s4 = lambda f, k: f'{sub4[f][k]:.3f}'
    dd = lambda f: f'{ed[f][0]:+.3f} [{ed[f][1]:+.3f}, {ed[f][2]:+.3f}]'
    caption = (
        f'Run-to-run consistency of the model coder. The same model (Claude Opus 5.5) coded the same paper twice, '
        'independently; agreement between the two runs measures how stable the output is, not whether it is right. It does '
        'not cap or estimate agreement with human coders, whose coding has not started, and errors the model repeats on '
        'every run do not show. '
        f'Codebook {", ".join(cb_a)} and graph {GRAPH_FOR_CODEBOOK.get(cb_a[0])} in (a) and (d); '
        f'the format test in (b) and (c) used the earlier codebook {", ".join(cb_ft)} (also graph {GRAPH_FOR_CODEBOOK.get(cb_ft[0])}) '
        'and two coding pipelines, so it is not comparable with (a). '
        f'(a) First and second coding of {len(coded_twice)} gold-set papers (the papers of the 100-paper gold sample that had full '
        f'text at the first coding); {len(pair)} pairs pass the format check in both runs. Both runs were sent as asynchronous '
        'batch requests with the same instructions, effort setting high and no temperature set. '
        'Top four rows: share of papers whose two codings match on entry state, entry node, outcome and decisive mode; '
        f'the outcome row has no visible interval because all {len(pair)} pairs agree. '
        'Bottom four rows: mean similarity of the node set and mode set (Jaccard: shared items over items in either) and of '
        'the node and mode sequences (1 minus the normalized edit distance, after merging repeated consecutive steps). Grey '
        'points are single papers, jittered vertically; per-paper similarities are rounded to 2 decimals, so several papers '
        'share a value. '
        f'(b) Input format test, n = {len(fkeys)} papers, four input formats, two codings per format and paper: '
        f'agreement between the two codings made from the same format (filled blue, upper, {fpairs["within"]} pairs) and between '
        f'codings made from different formats (open orange, lower, {fpairs["between"]} pairs), averaged within paper, then over '
        'papers. The two text-only formats (publisher XML text, and text extracted from the PDF) were coded by a Claude model '
        'run inside the Claude Code tool, model version not recorded; the PDF and PDF-plus-XML formats by Claude Opus 5.5 in '
        'batch mode, so four of the six between-format pair types also cross the coding pipeline. Format-test codings are not '
        f'filtered by the format check ({len(fmeta["invalid"])} of {sum(fmeta["codebook"].values())} fail it, '
        f'{"each on one quote over 25 words" if all("quote over 25" in e for e in fmeta["invalid"].values()) else "see the numbers file"}). '
        f'(c) Per paper, between-format minus within-format agreement (grey circles), and the mean over the {len(fkeys)} papers '
        'with a paired 95% bootstrap interval (blue). The difference excludes zero for the node sequence '
        f'({dd("node_seq_similarity")}) and the mode sequence ({dd("mode_seq_similarity")}); for entry state, decisive mode, '
        f'node set and outcome it lies between {fmt0(min(ed[f][0] for f in ("entry_state", "decisive_mode", "node_set_jaccard", "outcome")))} '
        f'and {fmt0(max(ed[f][0] for f in ("entry_state", "decisive_mode", "node_set_jaccard", "outcome")))}. '
        f'Open triangles: the {len(PREPRINT)} papers whose PDF was the discussion preprint, so two formats coded '
        'another text version and their between-format pairs compare different texts; they carry the largest sequence drops. '
        f'On the 4 same-version papers, node-sequence similarity is {s4("node_seq_similarity", "within")} within and '
        f'{s4("node_seq_similarity", "between")} between formats, mode sequence {s4("mode_seq_similarity", "within")} and '
        f'{s4("mode_seq_similarity", "between")}. '
        "(d) Krippendorff's alpha (nominal) for the pairs of (a): agreement corrected for the agreement expected by chance, "
        '1 perfect, 0 chance; node presence uses one unit per paper and node (15 nodes). V status is full when the paper '
        'performs at least one check of its result other than a plain rerun (new data, a second method, varied parameters, '
        'a control or reference, a new context), partial when its only checks are reruns, and none otherwise; it counts '
        'internal checks, not only replication by others (terms of NASEM, the US National Academies, 2019, for '
        'reproduction, replication and generalization). Dashed lines: 0.667 and 0.8, the usual thresholds for tentative '
        f'and firm conclusions. Alpha for {sing_txt.lower().replace("v status", "V status")} equals 1 but each rests on a single, '
        f'different paper outside the modal class ({len(pair) - 1} of {len(pair)} papers are {sing_modal} in both codings); '
        'such an alpha says little, and its bootstrap interval is undefined in about '
        f'a third of resamples ({", ".join(str(alpha[f]["undefined"]) for f in sing)} of {B}), so it is drawn as an open circle '
        'without interval. '
        f'Bars: 95% percentile bootstrap intervals ({B} resamples) over papers; in (d) all 15 node units of a paper are resampled '
        f'together. With n = {len(fkeys)} in (b) and (c) the intervals are coarse and reach the ceiling of 1 for several match shares. '
        'Paper identifiers, run tags and validation messages are in the numbers and provenance fields of this file.')
    ps.save(fig, 'fig03_reliability',
            inputs=[API / 'calc1', API / 'gold-r2', *([API / 'r2'] if (API / 'r2').is_dir() else []),
                    *[API / f'fmt-{a}{r}' for a in ('P', 'PX') for r in (1, 2)], FT / 'codings', FT / 'design.json',
                    DERIVED / 'calc1' / 'results.json', FT / 'results.json'],
            numbers=numbers, caption=caption)


if __name__ == '__main__':
    main()
