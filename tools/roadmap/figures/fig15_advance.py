"""Figure 15: the preregistered test of workflow features against the model's judgment of reported warrant (roadmap g24
analysis, paper figure).

What the outcome is. The advance coder (claude-opus-5-5 under agents/advance/RUBRIC.md v1.1.0, reading a blinded text)
judges reported warrant: whether the paper, as its text documents it, makes a meaningful and warranted gain. The
validation gate (40 human-rated papers) has not been run, so every outcome here is the model's judgment of reported
warrant, not scientific advance.

Panels (every number read from the frozen plan, the g24 results file, the g25 leak probes and the pilot report, except
the Wilson interval of the pooled small families in panel b, differences for the caption, and the like-for-like
calibration of panel d, which reads the full-run advance codings and round metrics through g24's own loaders
(advance_codings, inquiry, derived) and the leak-probe rows, and recomputes Spearman rho with g17.test)
  a  H1-H9, one row per preregistered hypothesis (feature of the inquiry coding -> advance outcome): within-strata
     Spearman rho with its 95% stratified bootstrap interval (blue circle; filled = supported, open = not supported),
     the partial Spearman rho with covariates (orange diamond) and the within-journal-family rho (green triangle).
     Grey band: H6 and H7, where feature and outcome code nearly the same construct, so they check coder
     consistency more than they test a workflow claim. Margin: papers with the feature, BH q, verdict.
  b  success fraction with Wilson 95% intervals: overall, by journal family (families with fewer than 10 papers pooled
     into 'Other'), by text route and by round as reference rows, and the pilot-2 rate the plan expected. Vertical
     line and band: overall fraction and its interval. Margin: achieved of n.
  c  advance score distribution (rubric anchors 1-5); score 1 is the not-demonstrated verdict by rule.
  d  calibration checks C1 and C2 (outside the family): Spearman rho with cnp, the OpenAlex citation percentile,
     with a like-for-like reference line computed here: on the leak-probe papers that are among the analysed papers,
     Spearman rho of the citation bucket the model guessed from title and abstract (g25 recognition probe) with cnp,
     and, for the caption, the full-text C1 forecast against cnp on the same papers.

Definitions
  success fraction    achieved / (achieved + not_demonstrated + unassessable U1, U2, U3, U5); U4 screen failures
                      excluded (advance-plan.json success_fraction). Achieved = at least one candidate gain meets
                      every criterion M1, M2 (meaningful) and W1-W4 (warranted) of the rubric.
  success, W3 ignored the same verdict with W3 (the principal threat is checked) removed; the outcome for features
                      built from validation checks (H1, H2), so a check count is never tested against W3.
  advance score       1-5 rubric anchor of the verdict-basis gain; achieved takes 2-5, not demonstrated takes 1.
  role                presence of a contribution role (corrective, enabling, integrative) among assessable papers.
  within-strata rho   Spearman rho after centring both rank vectors within strata round x OpenAlex subfield
                      (subfields under 10 papers pooled within round); g20 stratified(), 5000 within-stratum
                      permutations for p, 2000 stratified bootstrap resamples for the interval.
  partial rho         Spearman rho of feature and outcome after regressing both rank vectors on the ranks of log paper
                      words, text route (XML or pdftotext) and the number of reported checks in the advance coding;
                      pooled, not stratified, so its unadjusted reference is the plain rho (in the json).
  within-family rho   as within-strata rho, strata round x journal family (families under 10 papers pooled in round).
  BH q                Benjamini-Hochberg adjusted p over the 9 permutation p values (one family).
  rule                supported when q < 0.1 and the sign is the predicted (+); reversed when q < 0.1 and the sign is
                      opposite; otherwise not supported (advance-plan.json q_threshold).
  Wilson interval     score interval for a binomial proportion, z = 1.96 (g24 wilson()).
  Cramer's V          association of verdict with journal family from the chi-square of the family-by-verdict table
                      (g20 assoc_strat()): cramers_v_bc is bias-corrected on the table pooled over rounds;
                      cramers_v_strat uses the sum of within-round chi-squares and is not bias-corrected. The plan
                      names a bias-corrected V within round, which g24 does not compute.

Inputs
  preregistration/advance-plan.json                     frozen plan (public commit f7ca019): hypotheses, rule,
                                                         pilot expected rate, leak-probe summary
  private/data/roadmap/derived/advance/results.json     g24 test (tools/roadmap/g24_advance.py test, tag full-advance)
  private/data/roadmap/derived/advance/leak_probes.json g25 leak probes (tools/roadmap/g25_leak_probes.py)
  private/data/roadmap/derived/advance/pilot.json       pilot 2 test-retest (caption only)
  private/analysis/codings/api/full-advance/            full-run advance codings (panel d like-for-like check, read
                                                         through g24_advance.advance_codings; nothing written there)

Outputs  private/data/roadmap/figures/paper/fig15_advance.{pdf,png,json}
Run:     python tools/roadmap/figures/fig15_advance.py
"""
import json
import math
import re
import sys
from pathlib import Path

from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paperstyle as ps  # noqa: E402
import g17_outcomes as g17  # noqa: E402
import g24_advance as g24  # noqa: E402

PLAN = ps.ROOT / 'preregistration' / 'advance-plan.json'
RES = ps.DERIVED / 'advance' / 'results.json'
LEAK = ps.DERIVED / 'advance' / 'leak_probes.json'
PILOT = ps.DERIVED / 'advance' / 'pilot.json'
FROZEN_COMMIT = 'f7ca019'
SAME_CONSTRUCT = ('H6', 'H7')     # feature and outcome code nearly the same construct (see docstring)
MIN_FAMILY = 10                   # families below this pooled into 'Other' in panel b (as the plan's family strata)
EST, PART, FAM = ps.BLUE, ps.ORANGE, ps.GREEN
BAND = '#f0efec'                  # ps.DIV_MID, the neutral light grey

FEATURE = {'bin:triangulation': 'Triangulation (2+ check kinds)', 'num:V check kinds': 'Kinds of V check (count)',
           'bin:claim gate yes': 'Claim gate yes', 'bin:action gate yes or partly': 'Action gate yes or partly',
           'bin:outcome contradicted': 'Outcome contradicted', 'bin:composition capability_first': 'Capability-first composition',
           'num:import fields': 'Fields borrowed from (count)', 'bin:any return after failure': 'Any return after failure'}
OUTCOME = {'achieved_noW3': 'success, W3 ignored', 'achieved': 'success', 'score': 'advance score',
           'role:corrective': 'role corrective', 'role:enabling': 'role enabling', 'role:integrative': 'role integrative'}
FAMILY_LABEL = {'AGU': 'AGU', 'EGU/Copernicus': 'Copernicus (EGU)', 'Elsevier': 'Elsevier',
                'Nature portfolio': 'Nature portfolio', 'Springer Nature (non-portfolio)': 'Springer Nature, other',
                'Wiley non-AGU': 'Wiley, non-AGU'}
ANCHOR = {1: 'No warranted gain', 2: 'Small, local gain', 3: 'Clear gain, one subfield', 4: 'Substantial gain',
          5: 'Resolves a problem'}
ANCHOR_FULL = {1: 'no warranted gain beyond what was known', 2: 'a small, local gain', 3: 'a clear gain for one subfield',
               4: 'a substantial gain others will build on', 5: 'resolves a recognized problem or opens a new line of work'}
LEAK_BUCKETS = ['0-4', '5-14', '15-49', '50-149', '150+']   # g25_leak_probes.BUCKETS, ordered


def like_for_like(plan: dict, leak_rows: list) -> dict:
    """Panel d reference on the same papers: the leak-probe recognition rows whose key is among the analysed papers
    (g24 test's selection: valid full-run coding, inquiry coding with round metrics, not a pilot paper, not U4) with a
    cnp and a C1 forecast. Returns n, Spearman rho (g17.test: bootstrap interval, permutation p) of the
    title-and-abstract bucket with cnp and of the full-text C1 forecast with cnp, and the forecast classes used."""
    full, _ = g24.advance_codings(plan['full_run_tag'])
    inq = g24.inquiry()
    keys = sorted(k for k in full if k in inq and k not in set(plan['pilot_keys']))
    D = {k: g24.derived(full[k]) for k in keys}
    keys = {k for k in keys if not D[k]['screen_fail']}
    rows = [r for r in leak_rows if r['key'] in keys and inq[r['key']]['metrics'].get('cnp') is not None
            and D[r['key']]['impact'] is not None]
    cnp = [inq[r['key']]['metrics']['cnp'] for r in rows]
    forecast_all = {}
    for c in full.values():
        forecast_all[c['impact_forecast']] = forecast_all.get(c['impact_forecast'], 0) + 1
    forecast_used = {}
    for k in keys:
        forecast_used[full[k]['impact_forecast']] = forecast_used.get(full[k]['impact_forecast'], 0) + 1
    return {'n': len(rows), 'papers_analysed': len(keys),
            'title_abstract_guess_vs_cnp': g17.test([LEAK_BUCKETS.index(r['citations_bucket']) for r in rows], cnp),
            'full_text_C1_vs_cnp': g17.test([D[r['key']]['impact'] for r in rows], cnp),
            'impact_forecast_valid_full_run': forecast_all, 'impact_forecast_analysed': forecast_used}


def wilson(k, n):
    """Wilson 95% interval, the formula of tools/roadmap/g24_advance.py wilson()."""
    p, z = k / n, 1.96
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(c - h, 3), round(c + h, 3)]


def main():
    plan = json.loads(PLAN.read_text())
    d = ps.read_json(RES)
    leak = ps.read_json(LEAK)
    pilot = ps.read_json(PILOT)
    rows = d['family']
    hyp = {h['id']: h for h in plan['hypotheses']}
    assert [r['id'] for r in rows] == [h['id'] for h in plan['hypotheses']] and len(rows) == plan['family_size']
    assert all(r['feature'] == hyp[r['id']]['feature'] and r['outcome'] == hyp[r['id']]['outcome'] for r in rows)
    desc = d['descriptive']
    ov = desc['overall']
    qthr = plan['q_threshold']
    verd = d['verdicts']
    numbers = {'papers': d['papers'], 'invalid_codings': d['invalid_codings'], 'excluded_pilot': d['excluded_pilot'],
               'full_run_tag': d['full_run_tag'], 'plan_frozen': plan['frozen'], 'plan_commit_public': FROZEN_COMMIT,
               'plan_sha256_in_results': d['plan_sha256'], 'rubric_version': plan['rubric_version'],
               'blind_versions_read': desc['blind_versions_read'], 'verdicts': verd, 'q_threshold': qthr,
               'validation_gate': d['validation_gate'], 'overall': ov,
               'results_provenance': json.loads(RES.read_text()).get('_provenance')}

    W = ps.DOUBLE
    PA = 0.20                          # inches per row, panel a
    PB = 0.135                         # inches per row, panel b
    title_h, leg_h = 0.20, 0.36
    ha = len(rows) * PA + 0.05
    b_rows = []                        # (kind, label, stats) for panel b, top to bottom
    fam = desc['by_family']
    big = sorted((f for f in fam if fam[f]['n'] >= MIN_FAMILY), key=lambda f: -fam[f]['fraction'])
    small = sorted(f for f in fam if fam[f]['n'] < MIN_FAMILY)
    k_s, n_s = sum(fam[f]['achieved'] for f in small), sum(fam[f]['n'] for f in small)
    pooled = {'n': n_s, 'achieved': k_s, 'fraction': round(k_s / n_s, 3), 'wilson_95': wilson(k_s, n_s),
              'families': {f: fam[f]['n'] for f in small}}
    m = re.match(r'(\d+) of (\d+)', plan['expected_achieved_rate']['pilot'])
    pk, pn = int(m.group(1)), int(m.group(2))
    pil = {'n': pn, 'achieved': pk, 'fraction': round(pk / pn, 3), 'wilson_95': plan['expected_achieved_rate']['wilson_95']}
    b_rows.append(('head', 'All papers', None))
    b_rows.append(('row', f"Full run, {ov['n']} papers", ov))
    b_rows.append(('row', f'Pilot 2, {pn} codings (expected)', pil))
    b_rows.append(('head', 'Journal family', None))
    for f in big:
        b_rows.append(('row', FAMILY_LABEL.get(f, f), fam[f]))
    b_rows.append(('row', 'Other (pooled, each < 10)', pooled))
    b_rows.append(('head', 'Text route', None))
    b_rows.append(('row', 'Publisher XML', desc['by_route']['xml']))
    b_rows.append(('row', 'PDF text (pdftotext)', desc['by_route']['pdftotext']))
    b_rows.append(('head', 'Round', None))
    b_rows.append(('row', 'Round 1', desc['by_round']['round1']))
    b_rows.append(('row', 'Round 2', desc['by_round']['round2']))
    hb = sum(1.25 if k == 'head' else 1 for k, _, _ in b_rows) * PB + 0.05
    gap_ab = 0.62
    H = title_h + leg_h + 0.12 + ha + gap_ab + hb + 0.36
    fig, _ = ps.figure(W, H)
    fig.axes[0].remove()

    def box(x0, y0, w, h):
        return [x0 / W, y0 / H, w / W, h / H]

    fig.text(0.05 / W, (H - 0.03) / H,
             f"Model judgment of reported warrant, {d['papers']} papers: {verd.get('supported', 0)} of {len(rows)} "
             f"preregistered associations supported, {sum(r['verdict'] == 'supported' for r in rows if r['id'] in SAME_CONSTRUCT)} "
             f"of them coder-consistency checks; human validation gate not yet run",
             ha='left', va='top', fontsize=ps.FONT, fontweight='bold', color=ps.INK)

    # ---------------------------------------------------------------------------------------------- panel a
    ax0, aw = 2.32, 2.25
    ya = H - title_h - leg_h - 0.12
    axa = fig.add_axes(box(ax0, ya - ha, aw, ha))
    leg = [Line2D([], [], color=EST, marker='o', markersize=3.6, markeredgecolor=EST, linewidth=0.9,
                  label=r'Within-strata $\rho$, 95% bootstrap interval (filled = supported, open = not)'),
           Line2D([], [], color=PART, marker='D', markersize=3.0, linestyle='none', markeredgecolor=PART,
                  label=r'Partial $\rho$, covariates: log words, text route, reported checks'),
           Line2D([], [], color=FAM, marker='^', markersize=3.6, linestyle='none', markeredgecolor=FAM,
                  label=r'Within-journal-family $\rho$'),
           Patch(facecolor=BAND, edgecolor='none',
                 label='Feature and outcome code nearly the same construct: a coder-consistency check')]
    fig.legend(handles=leg, loc='upper left', bbox_to_anchor=(0.05 / W, (H - title_h - 0.02) / H), ncol=2,
               handlelength=1.8, fontsize=ps.SMALL, borderaxespad=0, labelspacing=0.35, columnspacing=1.4)
    drawn = []
    xmin, xmax = -0.2, 0.55
    for i, r in enumerate(rows):
        y = i + 0.5
        sup = r['verdict'] == 'supported'
        if r['id'] in SAME_CONSTRUCT:
            axa.add_patch(Rectangle((-2.3 / aw, i + 0.04), (2.3 + aw + 2.4) / aw, 0.92, facecolor=BAND,
                                    edgecolor='none', zorder=0, transform=axa.get_yaxis_transform(), clip_on=False))
        axa.plot(r['ci'], [y, y], color=EST, linewidth=1.0, solid_capstyle='butt', zorder=2)
        axa.plot([r['rho_within']], [y], 'o', markersize=4.0, zorder=4, markeredgewidth=0.9, markeredgecolor=EST,
                 markerfacecolor=EST if sup else 'white')
        axa.plot([r['partial_rho_covariates']], [y - 0.27], 'D', markersize=2.8, color=PART, zorder=3,
                 markeredgecolor='white', markeredgewidth=0.3)
        axa.plot([r['within_family']['rho_within']], [y + 0.27], '^', markersize=3.4, color=FAM, zorder=3,
                 markeredgecolor='white', markeredgewidth=0.3)
        drawn.append({'id': r['id'], 'feature': r['feature'], 'outcome': r['outcome'], 'n': r['n'],
                      'rho_within': r['rho_within'], 'ci': r['ci'], 'p': r['p'], 'q': r['q'],
                      'plain_rho': r['plain_rho'], 'partial_rho_covariates': r['partial_rho_covariates'],
                      'within_family': r['within_family'], 'feature_present': r['feature_present'],
                      'verdict': r['verdict'], 'same_construct': r['id'] in SAME_CONSTRUCT})
    axa.axvline(0, color=ps.MUTED, linewidth=0.6, zorder=1)
    axa.set_xlim(xmin, xmax)
    axa.set_ylim(len(rows), 0)
    axa.set_yticks([i + 0.5 for i in range(len(rows))])
    axa.set_yticklabels([f"{r['id']}  {FEATURE[r['feature']]} $\\rightarrow$ {OUTCOME[r['outcome']]}" for r in rows],
                        fontsize=ps.SMALL)
    for t, r in zip(axa.get_yticklabels(), rows):
        t.set_color(ps.INK if r['verdict'] == 'supported' else ps.INK2)
    axa.tick_params(axis='y', length=0, pad=3)
    axa.spines['left'].set_visible(False)
    axa.set_xlabel(r"Spearman $\rho$ with the model's warrant outcome", labelpad=2)
    ps.grid(axa, 'x')
    ps.panel(axa, 'a', x=-2.27 / aw, y=1.0 + 0.04 / ha)
    tr = axa.get_yaxis_transform()
    cols = {'feat': (aw + 0.52) / aw, 'q': (aw + 0.98) / aw, 'verdict': (aw + 1.08) / aw}
    for k, lab, ha_ in (('feat', 'Papers with feature', 'right'), ('q', 'BH q', 'right'), ('verdict', 'Verdict', 'left')):
        axa.text(cols[k], -0.15, lab, transform=tr, ha=ha_, va='bottom', fontsize=ps.SMALL, color=ps.INK2)
    for i, r in enumerate(rows):
        y = i + 0.5
        fp = f"{r['feature_present']}" + (' > 0' if r['feature'].startswith('num:') else '')
        axa.text(cols['feat'], y, fp, transform=tr, ha='right', va='center', fontsize=ps.SMALL, color=ps.INK2)
        q = r['q']
        axa.text(cols['q'], y, f'{q:.4f}' if q < 0.001 else f'{q:.3f}', transform=tr, ha='right', va='center',
                 fontsize=ps.SMALL, color=ps.INK if q < qthr else ps.INK2)
        vtxt = r['verdict'] + (' (same construct)' if r['id'] in SAME_CONSTRUCT else '')
        axa.text(cols['verdict'], y, vtxt, transform=tr, ha='left', va='center', fontsize=ps.SMALL,
                 color=ps.INK if r['verdict'] == 'supported' else ps.INK2,
                 fontweight='bold' if r['verdict'] == 'supported' and r['id'] not in SAME_CONSTRUCT else 'normal')
    numbers['panel_a'] = drawn

    # ---------------------------------------------------------------------------------------------- panel b
    bx0, bw = 1.42, 1.72
    yb = ya - ha - gap_ab
    axb = fig.add_axes(box(bx0, yb - hb, bw, hb))
    y, ticks, labels, drawn_b = 0.0, [], [], []
    lo, hi = ov['wilson_95']
    for kind, lab, s in b_rows:
        if kind == 'head':
            axb.text(-0.04, y + 1.25 * 0.62, lab, transform=axb.get_yaxis_transform(), ha='right', va='center',
                     fontsize=ps.SMALL, fontweight='bold', color=ps.INK)
            y += 1.25
            continue
        yc = y + 0.5
        is_pilot = lab.startswith('Pilot')
        col = ps.MUTED if is_pilot else EST
        axb.plot(s['wilson_95'], [yc, yc], color=col, linewidth=1.0, solid_capstyle='butt', zorder=2)
        axb.plot([s['fraction']], [yc], 'o', markersize=3.6, color=col, markeredgecolor='white', markeredgewidth=0.4,
                 zorder=3)
        axb.text(1.02, yc, f"{s['achieved']} of {s['n']}", transform=axb.get_yaxis_transform(), ha='left', va='center',
                 fontsize=ps.SMALL, color=ps.INK2)
        ticks.append(yc)
        labels.append(lab)
        drawn_b.append({'label': lab, 'n': s['n'], 'achieved': s['achieved'], 'fraction': s['fraction'],
                        'wilson_95': s['wilson_95']})
        y += 1
    axb.axvspan(lo, hi, color=BAND, zorder=0, linewidth=0)
    axb.axvline(ov['fraction'], color=ps.MUTED, linewidth=0.6, zorder=1)
    axb.set_xlim(0.3, 1.0)
    axb.set_ylim(y + 0.05, 0)
    axb.set_yticks(ticks)
    axb.set_yticklabels(labels, fontsize=ps.SMALL)
    axb.tick_params(axis='y', length=0, pad=3)
    axb.spines['left'].set_visible(False)
    axb.set_xlabel('Success fraction, Wilson 95% interval', labelpad=2)
    ps.grid(axb, 'x')
    ps.panel(axb, 'b', x=-1.37 / bw, y=1.0 + 0.06 / hb)
    vc = desc['venue_check']
    fy = next(i for i, (k, lab, _) in enumerate(b_rows) if lab == 'Journal family')
    yfam = sum(1.25 if k == 'head' else 1 for k, _, _ in b_rows[:fy]) + 1.25 * 0.62
    axb.text(0.02, yfam, f"Cramer's V {vc['cramers_v_bc']:.2f} pooled, bias-corrected; {vc['cramers_v_strat']:.2f} "
                         f"within round; p {vc['p']:.4f}", transform=axb.get_yaxis_transform(), ha='left', va='center',
             fontsize=ps.SMALL, color=ps.INK2, zorder=5,
             bbox=dict(facecolor='white', edgecolor='none', boxstyle='square,pad=0.08'))
    numbers['panel_b'] = drawn_b
    numbers['pooled_other'] = pooled
    numbers['venue_check'] = {k: vc[k] for k in ('cramers_v_bc', 'v_bc_ci', 'cramers_v_strat', 'v_strat_ci', 'cramers_v',
                                                  'v_ci', 'chi2', 'p', 'stratified_by')}

    # ---------------------------------------------------------------------------------------------- panel c
    cx0, cw = 5.42, 1.48
    hc = 1.05
    axc = fig.add_axes(box(cx0, yb - hc, cw, hc))
    sd = {int(k): v for k, v in desc['score_distribution'].items()}
    scores = [1, 2, 3, 4, 5]
    cnt = [sd.get(s, 0) for s in scores]
    axc.barh(scores, cnt, height=0.62, color=[ps.NEUTRAL] + [EST] * 4, zorder=2)
    for s, c in zip(scores, cnt):
        axc.text(c + max(cnt) * 0.02, s, f'{c}', ha='left', va='center', fontsize=ps.SMALL, color=ps.INK2)
    axc.set_yticks(scores)
    axc.set_yticklabels([f'{s}  {ANCHOR[s]}' for s in scores], fontsize=ps.SMALL)
    axc.set_ylim(5.6, 0.4)
    axc.set_xlim(0, max(cnt) * 1.18)
    axc.tick_params(axis='y', length=0, pad=3)
    axc.spines['left'].set_visible(False)
    axc.set_xlabel('Papers', labelpad=2)
    ps.grid(axc, 'x')
    axc.text(0, 1.04, 'Grey: not demonstrated; blue: achieved', transform=axc.transAxes,
             ha='left', va='bottom', fontsize=ps.SMALL, color=ps.INK2)
    ps.panel(axc, 'c', x=-1.3 / cw, y=1.0 + 0.06 / hc)
    numbers['score_distribution'] = {s: c for s, c in zip(scores, cnt)}

    # ---------------------------------------------------------------------------------------------- panel d
    hd = 0.78
    yd = yb - hc - 0.62
    axd = fig.add_axes(box(cx0, yd - hd, cw, hd))
    cal = {c['id']: c for c in d['calibration']}
    rec = leak['recognition']['all80']
    lfl = like_for_like(plan, leak['rows']['recognition'])
    assert lfl['papers_analysed'] == d['papers'], (lfl['papers_analysed'], d['papers'])
    assert not lfl['impact_forecast_valid_full_run'].get('top_decile'), 'caption says no coding used top decile'
    ta = lfl['title_abstract_guess_vs_cnp']
    lab_d = {'C1': 'C1  Impact forecast', 'C2': 'C2  Advance score'}
    for i, cid in enumerate(('C1', 'C2')):
        c = cal[cid]
        axd.plot(c['ci'], [i, i], color=EST, linewidth=1.0, solid_capstyle='butt', zorder=2)
        axd.plot([c['rho']], [i], 'o', markersize=3.6, color=EST, markeredgecolor='white', markeredgewidth=0.4, zorder=3)
    axd.axvline(ta['rho'], color=ps.ORANGE, linewidth=0.9, linestyle=(0, (3, 2)), zorder=1)
    axd.text(ta['rho'] - 0.015, 2.05, f"Title-and-abstract guess vs cnp,\nsame {lfl['n']} papers (\u03c1 {ta['rho']:.2f})",
             ha='right', va='center',
             fontsize=ps.SMALL, color=ps.INK2)
    axd.set_yticks([0, 1])
    axd.set_yticklabels([lab_d['C1'], lab_d['C2']], fontsize=ps.SMALL)
    axd.set_ylim(2.75, -0.5)
    axd.set_xlim(0, 0.7)
    axd.tick_params(axis='y', length=0, pad=3)
    axd.spines['left'].set_visible(False)
    axd.set_xlabel(r'Spearman $\rho$ with citation percentile (cnp)', labelpad=2)
    ps.grid(axd, 'x')
    ps.panel(axd, 'd', x=-1.3 / cw, y=1.0 + 0.06 / hd)
    numbers['panel_d'] = {'calibration': d['calibration'], 'leak_citations_rho_all80': rec['citations_rho'],
                          'leak_citations_rho_venue60': leak['recognition']['venue60']['citations_rho'],
                          'leak_citations_rho_gold20': leak['recognition']['gold20']['citations_rho'],
                          'like_for_like': lfl}

    # ---------------------------------------------------------------------------------------------- caption
    ven = leak['venue']
    rt = pilot['retest']
    fam_lo = min(big, key=lambda f: fam[f]['fraction'])
    fam_hi = max(big, key=lambda f: fam[f]['fraction'])
    shrink = {r['id']: {'within': r['rho_within'], 'plain': r['plain_rho'], 'partial': r['partial_rho_covariates'],
                        'within_family': r['within_family']['rho_within']} for r in rows}
    numbers['shrink'] = shrink
    mid = [i for i in shrink if i not in ('H1', 'H2', 'H8', 'H9')]
    mid_change = max(abs(shrink[i]['plain'] - shrink[i]['partial']) for i in mid)
    fam_gap = max(abs(shrink[i]['within'] - shrink[i]['within_family']) for i in shrink)
    numbers['max_abs_plain_minus_partial_' + '_'.join(mid)] = round(mid_change, 3)
    numbers['max_abs_within_minus_within_family'] = round(fam_gap, 3)
    ref_overlap = all(max(a['wilson_95'][0], b['wilson_95'][0]) < min(a['wilson_95'][1], b['wilson_95'][1])
                      for a, b in ((desc['by_route']['xml'], desc['by_route']['pdftotext']),
                                   (desc['by_round']['round1'], desc['by_round']['round2'])))
    numbers['leak'] = {'journal_top1_blinded': ven['journal_top1'], 'family_blinded': ven['family'],
                       'journal_title_abstract': rec['journal'], 'citations_rho_all80': rec['citations_rho'],
                       'recognized': rec['recognized']}
    numbers['pilot_retest'] = {'papers_in_both': rt['papers_in_both'], 'verdict': rt['verdict'],
                               'advance_score': rt['advance_score']}
    rs = {r['id']: r for r in rows}
    not_sup = [r['id'] for r in rows if r['verdict'] != 'supported']
    sdist = numbers['score_distribution']
    caption = (
        f"Preregistered test of {len(rows)} associations between workflow features and the advance coder's verdict, "
        f"frozen in preregistration/advance-plan.json (public commit {FROZEN_COMMIT}, {plan['frozen']}; errata in "
        f"preregistration/ERRATA.md) before any full-run advance coding existed. Outcome: the judgment of "
        f"claude-opus-5-5 under agents/advance/RUBRIC.md v{plan['rubric_version']}, reading text blinded to journal, "
        f"publisher, authors, affiliations, funding and DOI (blinding v{plan['blind_version']}), of reported warrant: "
        f"whether the paper's text documents a meaningful and warranted gain in knowledge, understanding or research "
        f"capability. The validation gate (40 papers rated by two humans each) has not been run "
        f"('{d['validation_gate']['status']}'), so every value here is the model's judgment of reported warrant, not "
        f"scientific advance. Papers: {d['papers']} with a valid advance coding under tag {d['full_run_tag']}, a valid "
        f"inquiry coding (round 1 or round 2) and round metrics; {d['invalid_codings']} invalid codings and the "
        f"{d['excluded_pilot']} pilot papers with a full-run coding are excluded; U4 screen failures "
        f"{desc['U4_screen_failures']}, unassessable {ov['unassessable']}. Test by tools/roadmap/g24_advance.py test. "
        f"In pilot 2, {rt['papers_in_both']} papers coded twice agreed on the verdict in "
        f"{rt['verdict']['agreement']:.0%} and on the score in {rt['advance_score']['exact']:.0%} (Krippendorff alpha "
        f"{rt['verdict']['alpha_nominal']:.2f} nominal and {rt['advance_score']['alpha_ordinal']:.2f} ordinal), which bounds run-to-run noise, not validity. "
        f"(a) Each row is feature -> outcome. Features come from the inquiry coding (codebook 1.5.0, a separate call of "
        f"the same model on the same text): triangulation, checks of two or more of replication, method and "
        f"generalization performed in the paper; kinds of V check, the number of kinds of validation check; claim gate "
        f"yes, the claim faced a test it could fail; action gate yes or partly, a stated hypothesis directed the key "
        f"data acquisition; outcome contradicted, the walk ends by showing an earlier published claim wrong (codebook outcome contradicted); capability-first "
        f"composition, the method or instrument is built before the question is posed; fields borrowed from, the "
        f"distinct source fields of borrowed concepts, methods or data; any return after failure, a step that goes back "
        f"to an earlier attempt the paper says failed, mismatched or was revised. Outcomes: success, the verdict achieved (at least one candidate gain meets every "
        f"meaningfulness criterion M1, M2 and warrant criterion W1-W4) against not demonstrated; success, W3 ignored, "
        f"the same with W3 (the principal threat is checked) removed, used for H1 and H2 so a count of checks is not "
        f"tested against a criterion about checks; advance score, the 1-5 rubric anchor; role, whether the coder "
        f"assigns that contribution role. Within-strata rho: Spearman rank correlation after centring ranks within "
        f"round x OpenAlex subfield (17 strata), with a 95% stratified bootstrap interval (2000 resamples) and a "
        f"permutation p (5000 within-stratum shuffles); q is the Benjamini-Hochberg adjusted p over the {len(rows)} "
        f"tests; supported when q < {qthr:g} with the predicted positive sign. p {min(r['p'] for r in rows):.4f} is the "
        f"smallest value 5,000 permutations can give, and q {min(r['q'] for r in rows):.4f} is the BH value at that "
        f"floor. {verd.get('supported', 0)} supported, "
        f"{verd.get('not supported', 0)} not supported ({', '.join(not_sup)}: rho {rs['H8']['rho_within']:.3f}), none "
        f"reversed. The inquiry and advance codings share model and text, so part of each association is method "
        f"variance: both respond to how fully a paper reports its checks. The partial rho (orange) removes the ranks "
        f"of log paper words, text route and the number of checks the advance coder lists; it is pooled, so compare "
        f"it with the plain rho: H1 {shrink['H1']['plain']:.2f} to {shrink['H1']['partial']:.2f}, H2 "
        f"{shrink['H2']['plain']:.2f} to {shrink['H2']['partial']:.2f}, H9 {shrink['H9']['plain']:.2f} to "
        f"{shrink['H9']['partial']:.2f}, while {mid[0]} to {mid[-1]} change by at most {mid_change:.3f}. The check count is read from the "
        f"advance coding itself and counts nearly what the H1 and H2 features count, so this adjustment may remove part "
        f"of the feature (H1, H2) or of W3 (H3 to H9); method variance the covariates do not capture may remain, so "
        f"neither the plain nor the partial value bounds the share of a link that is about papers. The within-journal-family "
        f"rho (green; strata round x family) differs from the within-strata rho by at most {fam_gap:.3f}. H9 (q "
        f"{rs['H9']['q']:.3f}, interval reaching {rs['H9']['ci'][0]:.3f}) passes the rule but drops to "
        f"{shrink['H9']['partial']:.2f} after adjustment. H6 and H7 (grey band) pair a feature and an outcome that code "
        f"nearly the same construct (a contradicted outcome and a corrective role; a capability-first walk and an "
        f"enabling role); H6 rests on {rs['H6']['feature_present']} papers with the feature. They show the two "
        f"codings agree, not that a workflow raises warrant. "
        f"(b) Success fraction, achieved over all papers (unassessable U1, U2, U3, U5 counted as not achieved; "
        f"U4 excluded), with Wilson 95% intervals; vertical line and band: the full-run value {ov['fraction']:.2f} "
        f"[{ov['wilson_95'][0]:.3f}, {ov['wilson_95'][1]:.3f}]. Grey row: the pilot-2 rate the plan recorded as "
        f"expected ({pk} of {pn} codings of 20 papers). Journal family from DOI prefix and publisher (g20 family()); "
        f"families with fewer than {MIN_FAMILY} papers pooled ("
        + ', '.join(f'{f} {c}' for f, c in pooled['families'].items()) +
        f"). Among the {len(big)} families with {MIN_FAMILY} or more papers, fractions range from "
        f"{fam[fam_lo]['fraction']:.2f} ({FAMILY_LABEL.get(fam_lo, fam_lo)}) to {fam[fam_hi]['fraction']:.2f} "
        f"({FAMILY_LABEL.get(fam_hi, fam_hi)}); pooled Other {k_s} of {n_s}. Cramer's V of verdict by family: "
        f"{vc['cramers_v_bc']:.3f} [{vc['v_bc_ci'][0]:.2f}, {vc['v_bc_ci'][1]:.2f}] bias-corrected on the table pooled "
        f"over rounds; {vc['cramers_v_strat']:.3f} [{vc['v_strat_ci'][0]:.2f}, {vc['v_strat_ci'][1]:.2f}] from the "
        f"within-round chi-square, not bias-corrected; within-round permutation p {vc['p']}, the floor of 5,000 "
        f"permutations. The plan names a bias-corrected V within round, which g24 does not compute. Blinding does not hide venue: "
        f"from the blinded text the same model named the journal in {ven['journal_top1']['k']} of "
        f"{ven['journal_top1']['n']} papers ({ven['journal_top1']['rate']:.0%}, against a base rate of "
        f"{ven['journal_top1']['base_rate']:.0%}) and the family in {ven['family']['k']} of {ven['family']['n']}, and "
        f"from title and abstract alone the journal in {rec['journal']['k']} of {rec['journal']['n']} "
        f"(tools/roadmap/g25_leak_probes.py). A family difference therefore mixes real differences in reported warrant "
        f"with a possible venue halo. "
        + ("The two text routes, and the two rounds, have overlapping intervals. " if ref_overlap else "") +
        f"(c) Advance score, rubric anchors (the panel labels shorten them): "
        + '; '.join(f'{s} {ANCHOR_FULL[s]}' for s in sorted(ANCHOR_FULL)) +
        f". 1 is given to every not-demonstrated paper by rule, 2 to 5 to achieved papers; "
        f"{sdist[1]} scored 1, {sdist[2]} scored 2, {sdist[3]} scored 3, {sdist[4]} scored 4 and {sdist[5]} scored 5, "
        f"so beyond the verdict the score mostly separates 2 from 3 among achieved papers (H4 and H9 use it). "
        f"(d) Calibration checks outside the family: C1, the coder's blind citation forecast (below median, around "
        f"median, top quartile, top decile, as 1-4) against cnp, the OpenAlex citation normalized percentile among "
        f"works of the same subfield, year and type; C2, advance score against cnp; Spearman rho with 95% bootstrap "
        f"intervals, n = {cal['C1']['n']}. None of the {sum(lfl['impact_forecast_valid_full_run'].values())} valid "
        f"full-run codings used top decile (analysed papers: "
        + ', '.join(f"{k.replace('_', ' ')} {v}" for k, v in sorted(lfl['impact_forecast_analysed'].items(), key=lambda x: g24.IMPACT[x[0]])) +
        f"), so C1 is in effect on a 1-3 scale. Dashed line, computed for this figure: on the {lfl['n']} leak-probe "
        f"papers that are among the {d['papers']}, Spearman rho {ta['rho']:.2f} [{ta['ci'][0]:.2f}, {ta['ci'][1]:.2f}] "
        f"between the citation bucket the model guessed from title and abstract (tools/roadmap/g25_leak_probes.py "
        f"recognition probe) and cnp; on the same papers the full-text C1 forecast reaches "
        f"{lfl['full_text_C1_vs_cnp']['rho']:.2f} [{lfl['full_text_C1_vs_cnp']['ci'][0]:.2f}, "
        f"{lfl['full_text_C1_vs_cnp']['ci'][1]:.2f}]. On all {rec['n']} probed papers the guess correlates with the raw "
        f"OpenAlex citation count at {rec['citations_rho']:.2f}, and the model claimed to recognize "
        f"{rec['recognized']['yes']}. Because the model can place a paper's venue and citation level from its content, "
        f"C1 and C2 cannot separate judgment of the paper from recall or topic priors and are not evidence of "
        f"validity. One model coder; no causal reading.")
    bb = fig.get_tightbbox(fig.canvas.get_renderer())
    numbers['figure_inches_tight'] = [round(bb.width, 2), round(bb.height, 2)]
    ps.save(fig, 'fig15_advance', inputs=[PLAN, RES, LEAK, PILOT], numbers=numbers, caption=caption)
    print(json.dumps({k: v for k, v in numbers.items() if not k.startswith('panel_')}, indent=1, default=str))
    print(caption)


if __name__ == '__main__':
    main()
