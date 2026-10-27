"""Figure 9: who is in the sample. Outcome metrics at each stage of each round, to show what eligibility screening
and coding coverage do to the composition of the corpus.

Rows     one per stage, grouped by round. Round 1: preselected (600) -> eligible -> coded. Round 2: drawn (277) ->
         eligible -> coded. Stage colours are the same in panels a-d (slot 1 first stage, slot 2 eligible, slot 3
         coded). Round 2 is drawn when derived/r2 and derived/r2calc exist; its coded row fills in once tag r2 codings
         exist, and until then carries a "batch not yet returned" note.
Panel a  impact: cnp (OpenAlex citation normalized percentile, 0-1), one point per paper (jittered strip) with a box
         (quartiles, median, whiskers at 1.5 times the interquartile range). Both draws take equal numbers per fixed cnp
         bin min(4, int(5 cnp)) (g03_preselect.py, g18_round2_draw.py), so the sample is near-uniform in cnp by design
         and the pool median is not a like-for-like reference; it is not drawn (it is in the json and the caption).
Panel b  novelty: novelty_pair = -log10(1 + number of 2017-2021 works sharing the paper's leading OpenAlex topic pair)
         (g04_metrics.py); higher is rarer. Same marks.
Panel c  reference breadth: breadth_refs = share of classified references outside geoscience (the field g17 uses).
         Same marks, square-root x axis (most values lie below 0.15; 28% of round 1 papers are exactly 0).
Panel d  open-access share (is_oa) per stage with 95% Wilson intervals, axis from 40%. Dashed grey line: share in the
         pool frame. Round 2 is open access by construction (g18_round2_draw.py keeps OA papers only).
Panel e  coverage effect per round: coded against eligible not (yet) coded, on one standardized scale, Cliff's delta
         = P(coded > not coded) - P(coded < not coded) over all cross-group pairs (ties count zero). For a 0/1 variable
         (is_oa) it equals the difference in shares. 95% percentile bootstrap interval.

Definitions
  eligible   key in the round's manifest (derived/<calc>/manifest.jsonl); checked against eligibility.json
  coded      a coding file private/analysis/codings/api/<tag>/<key>.json for a manifest key that passes
             tools/check_coding.py validate(); tag calc1 for round 1, r2 for round 2 (same rule as fig01 and g17).
             In round 1, coding was attempted on the eligible papers with retrieved full text (EXPERIMENTS.md E1);
             "attempted" here = manifest keys with any coding file, valid or not.
  coverage effect  for each metric, Cliff's delta (drawn) and the median difference, coded minus eligible not coded
             (for is_oa, the share difference), each with a 95% percentile bootstrap interval: 2000 resamples within
             each group. Every (round, metric) pair has its own generator np.random.default_rng([2026, round index,
             metric index]) so the intervals can be reproduced independently of the plotting jitter (which uses
             np.random.default_rng(2026)). The median difference and delta come from the same resamples.

Inputs
  private/data/roadmap/derived/gold/pool.json           2022 candidate pool (g02_pool.py)
  private/data/roadmap/derived/gold/preselect.json      round 1 preselection (g03_preselect.py, seed 2026)
  private/data/roadmap/derived/gold/eligibility.json    round 1 screen (g07_eligibility.py)
  private/data/roadmap/derived/gold/metrics.json        round 1 metrics (g04_metrics.py)
  private/data/roadmap/derived/calc1/manifest.jsonl     round 1 eligible corpus (g12_calc1_manifest.py)
  private/data/roadmap/derived/r2/{preselect,eligibility,metrics}.json   round 2, if present
  private/data/roadmap/derived/r2calc/manifest.jsonl    round 2 eligible corpus, if present
  private/analysis/codings/api/{calc1,r2}/*.json        codings

Outputs  private/data/roadmap/figures/paper/fig09_sample.{pdf,png,json}
Run:     python tools/roadmap/figures/fig09_sample.py
"""
import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402
from check_coding import validate  # noqa: E402  (tools/ is on sys.path via common)

D = ps.DERIVED
CODINGS = ps.PRIVATE / 'analysis' / 'codings' / 'api'
ROUNDS = [  # name, set folder, calc folder, coding tag, first-stage label, draw seed
    ('Round 1', 'gold', 'calc1', 'calc1', 'Preselected', 2026),
    ('Round 2', 'r2', 'r2calc', 'r2', 'Drawn', 2027),
]
STAGE_COLOUR = [ps.BLUE, ps.ORANGE, ps.AQUA]          # first stage, eligible, coded (fixed slots 1-3)
STAGE_ALPHA = [0.55, 0.55, 0.7]                        # AQUA is light on white; a little more ink
SQRT = (lambda x: np.sign(x) * np.sqrt(np.abs(x)), lambda y: np.sign(y) * y * y)
METRICS = [  # field, axis label, x limits, scale, ticks
    ('cnp', 'Citation percentile (cnp)', (-0.03, 1.03), None, None),
    ('novelty_pair', 'Topic-pair rarity,\n$-\\log_{10}$(1 + prior works)', None, None, None),
    ('breadth_refs', 'Share of references outside\ngeoscience (square-root axis)', (-0.0015, 1.03), SQRT,
     [0, 0.05, 0.2, 0.5, 1]),
]
EFFECTS = [('cnp', 'Citation'), ('novelty_pair', 'Rarity'), ('breadth_refs', 'Breadth'), ('is_oa', 'Open access')]
SEED = 2026
NBOOT = 2000


def manifest(path):
    return [json.loads(line)['key'] for line in path.read_text().splitlines() if line.strip()]


def coded(tag, keys):
    """Manifest keys with a coding that passes validate(); keys whose coding fails; whether the tag folder exists."""
    folder = CODINGS / tag
    if not folder.is_dir():
        return [], [], False
    keyset, good, bad = set(keys), [], []
    for f in sorted(folder.glob('*.json')):
        if f.stem not in keyset:
            continue
        try:
            ok = not validate(json.loads(f.read_text()))
        except Exception:  # noqa: BLE001
            ok = False
        (good if ok else bad).append(f.stem)
    return good, bad, True


def wilson(k, n, z=1.959964):
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def cliffs_delta(a, b):
    """P(a > b) - P(a < b) over all pairs, ties count zero; O((n + m) log m) via a sorted b."""
    bs = np.sort(b)
    below = np.searchsorted(bs, a, 'left').sum()            # pairs with b < a
    above = (len(bs) - np.searchsorted(bs, a, 'right')).sum()  # pairs with b > a
    return float(below - above) / (len(a) * len(b))


def coverage(a, b, binary, gen):
    """Coded (a) against not coded (b): Cliff's delta and the median (or share) difference, each as
    [estimate, 2.5%, 97.5%] from one set of NBOOT within-group resamples drawn by `gen`."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    loc = np.mean if binary else np.median
    dl, df = np.empty(NBOOT), np.empty(NBOOT)
    for i in range(NBOOT):
        ra, rb = a[gen.integers(0, len(a), len(a))], b[gen.integers(0, len(b), len(b))]
        dl[i], df[i] = cliffs_delta(ra, rb), loc(ra) - loc(rb)
    out = lambda o, bs: [round(float(o), 4), round(float(np.percentile(bs, 2.5)), 4),  # noqa: E731
                         round(float(np.percentile(bs, 97.5)), 4)]
    return out(cliffs_delta(a, b), dl), out(loc(a) - loc(b), df)


def load_round(name, setdir, calcdir, tag, first, seed, inputs, issues):
    pre, elig, met, man = (D / setdir / 'preselect.json', D / setdir / 'eligibility.json', D / setdir / 'metrics.json',
                           D / calcdir / 'manifest.jsonl')
    if not all(p.is_file() for p in (pre, elig, met, man)):
        return None
    inputs += [pre, elig, met, man]
    metrics = {'g22_' + r['id']: r for r in ps.read_json(met)}
    drawn = ['g22_' + r['id'] for r in ps.read_json(pre)]
    keys = manifest(man)
    flagged = {r['key'] for r in ps.read_json(elig) if r['eligible']}
    if flagged != set(keys):
        issues.append(f'{name}: manifest ({len(keys)}) and eligibility.json eligible ({len(flagged)}) differ')
    missing = [k for k in drawn if k not in metrics]
    if missing:
        issues.append(f'{name}: {len(missing)} drawn papers have no metrics row')
    good, bad, present = coded(tag, keys)
    if bad:
        issues.append(f'{name}: {len(bad)} codings fail check_coding.validate() and are left out of Coded: {", ".join(bad)}')
    if present:
        inputs.append(CODINGS / tag)
    quint = Counter(min(4, int(metrics[k]['cnp'] * 5)) for k in drawn
                    if metrics.get(k, {}).get('cnp') is not None)
    stages = [(first, drawn), ('Eligible', keys), ('Coded', good if good else None)]
    return {'name': name, 'tag': tag, 'seed': seed, 'metrics': metrics, 'stages': stages, 'folder': present,
            'eligible': keys, 'coded': good, 'failed': bad, 'quintiles': [quint.get(q, 0) for q in range(5)]}


def values(rnd, ks, field):
    return np.array([rnd['metrics'][k][field] for k in ks if rnd['metrics'].get(k, {}).get(field) is not None], float)


def main():
    rng = np.random.default_rng(SEED)                      # plotting jitter only
    inputs, issues = [D / 'gold' / 'pool.json'], []
    frame = [p for p in ps.read_json(D / 'gold' / 'pool.json') if not p.get('convenor_coauthor')]
    pool_cnp = np.array([p['cnp'] for p in frame if p.get('cnp') is not None], float)
    pool_oa_k, pool_n = sum(bool(p.get('is_oa')) for p in frame), len(frame)
    rounds = [r for r in (load_round(*spec, inputs, issues) for spec in ROUNDS) if r]

    # row layout: a bold round header row, then one row per stage
    rows, y = [], 0.0          # (y, round, stage index, label, keys or None)
    heads = []
    for r in rounds:
        heads.append((y, r['name']))
        y += 0.9
        r['ys'] = []
        for i, (stage, ks) in enumerate(r['stages']):
            lab = f'{stage}, n = {len(ks)}' if ks is not None else stage
            rows.append((y, r, i, lab, ks))
            r['ys'].append(y)
            y += 1
        y += 0.3
    ybot = y - 0.3 - 0.45
    ytop = -0.75

    fig = ps.figure(ps.DOUBLE, 0.42 + 0.235 * (ybot + 0.6))[0]
    fig.clf()
    gs = GridSpec(1, 6, figure=fig, width_ratios=[1, 1, 1, 0.62, 0.36, 0.78], wspace=0.13,
                  left=0.128, right=0.995, bottom=0.2, top=0.93)
    axes = [fig.add_subplot(gs[0])]
    axes += [fig.add_subplot(gs[j], sharey=axes[0]) for j in range(1, 4)]
    ex = fig.add_subplot(gs[5])
    numbers = {'rounds_drawn': [r['name'] for r in rounds],
               'stage_counts': {r['name']: {s: (len(ks) if ks is not None else None) for s, ks in r['stages']}
                                for r in rounds},
               'coding_tags': {r['name']: r['tag'] for r in rounds},
               'coding_folder_present': {r['name']: r['folder'] for r in rounds},
               'coding_attempted': {r['name']: len(r['coded']) + len(r['failed']) for r in rounds},
               'coding_failed_validation': {r['name']: r['failed'] for r in rounds},
               'first_stage_per_cnp_bin': {r['name']: r['quintiles'] for r in rounds},
               'pool_frame_n': pool_n, 'pool_cnp_median_not_drawn': round(float(np.median(pool_cnp)), 4),
               'pool_oa_share': round(pool_oa_k / pool_n, 4), 'pool_oa_wilson95': [round(v, 4) for v in wilson(pool_oa_k, pool_n)]}

    # ---- (a)-(c) distributions ----
    for j, (field, xlabel, xlim, scale, ticks) in enumerate(METRICS):
        ax = axes[j]
        if scale:
            ax.set_xscale('function', functions=scale)
        summ = {}
        for yy, r, i, lab, ks in rows:
            if ks is None:
                continue
            v = values(r, ks, field)
            jit = rng.uniform(-0.28, 0.28, len(v))
            ax.scatter(v, yy + jit, s=2.4, color=STAGE_COLOUR[i], alpha=STAGE_ALPHA[i], linewidths=0, zorder=2,
                       rasterized=True)
            ax.boxplot(v, positions=[yy], orientation='horizontal', widths=0.62, whis=1.5, showfliers=False,
                       manage_ticks=False, patch_artist=False, zorder=3,
                       boxprops={'color': ps.INK, 'linewidth': 0.6}, whiskerprops={'color': ps.INK, 'linewidth': 0.6},
                       capprops={'color': ps.INK, 'linewidth': 0.6}, medianprops={'color': ps.INK, 'linewidth': 1.3})
            q1, med, q3 = np.percentile(v, [25, 50, 75])
            summ[f"{r['name']} {r['stages'][i][0]}"] = {'n': int(len(v)), 'median': round(float(med), 4),
                                                         'q25': round(float(q1), 4), 'q75': round(float(q3), 4),
                                                         'n_zero': int((v == 0).sum())}
            if len(v) != len(ks):
                issues.append(f"{r['name']} {r['stages'][i][0]}: {len(ks) - len(v)} papers without {field}")
        numbers[f'{field}_by_stage'] = summ
        if xlim:
            ax.set_xlim(*xlim)
        if ticks:
            ax.set_xticks(ticks, [f'{t:g}' for t in ticks])
            ax.minorticks_off()
        ax.set_xlabel(xlabel)
        ps.grid(ax, 'x')
        ps.panel(ax, 'abc'[j], x=-0.02)

    # ---- (d) open-access share with Wilson intervals ----
    dx = axes[3]
    oa = {}
    for yy, r, i, lab, ks in rows:
        if ks is None:
            continue
        k = sum(bool(r['metrics'][key].get('is_oa')) for key in ks if key in r['metrics'])
        n = sum(key in r['metrics'] for key in ks)
        lo, hi = wilson(k, n)
        p = k / n
        dx.errorbar(p, yy, xerr=[[max(0.0, p - lo)], [max(0.0, hi - p)]], fmt='o', color=STAGE_COLOUR[i], ms=3.6,
                    mec='white', mew=0.5, elinewidth=0.8, capsize=0, zorder=3)
        dx.text(min(lo, p - 0.012) - 0.025, yy, f'{100 * p:.0f}%', va='center', ha='right', fontsize=ps.SMALL,
                color=ps.INK, zorder=4, bbox={'boxstyle': 'square,pad=0.08', 'fc': 'white', 'ec': 'none'})
        oa[f"{r['name']} {r['stages'][i][0]}"] = {'k': k, 'n': n, 'share': round(p, 4),
                                                  'wilson95': [round(lo, 4), round(hi, 4)]}
    numbers['is_oa_by_stage'] = oa
    dx.axvline(pool_oa_k / pool_n, color=ps.MUTED, linewidth=0.7, linestyle=(0, (3, 2)), zorder=1)
    dx.set_xlim(0.4, 1.04)            # dot plot of shares: the axis need not start at zero
    dx.set_xticks([0.4, 0.6, 0.8, 1.0], ['40', '60', '80', '100'])
    dx.set_xlabel('Open access\n(% of papers)')
    ps.grid(dx, 'x')
    ps.panel(dx, 'd', x=-0.02)
    # pool label above the axes, clear of the dashed line
    dx.text(pool_oa_k / pool_n, 1.0, 'pool', transform=dx.get_xaxis_transform(), ha='center', va='bottom',
            fontsize=ps.SMALL, color=ps.INK2, clip_on=False)

    # shared y axis: stage rows labelled on (a), round headers in bold
    axes[0].set_yticks([r[0] for r in rows], [r[3] for r in rows])
    for yh, nm in heads:
        axes[0].text(-0.03, yh, nm, transform=axes[0].get_yaxis_transform(), ha='right', va='center',
                     fontsize=ps.FONT, fontweight='bold', color=ps.INK)
    for ax in axes:
        ax.tick_params(axis='y', length=0)
        ax.spines['left'].set_visible(False)
        ax.set_ylim(ybot, ytop)
    for ax in axes[1:]:
        ax.tick_params(axis='y', labelleft=False)
    for yy, r, i, lab, ks in rows:
        if ks is None:
            axes[0].text(0.0, yy, 'batch not yet returned', va='center', ha='left', color=ps.MUTED,
                         fontsize=ps.SMALL, style='italic')

    # ---- (e) coverage effect: coded vs eligible not coded ----
    cov, eticks = {}, []
    for ri, r in enumerate(rounds):
        y0, y1 = r['ys'][0], r['ys'][-1]
        ey = np.linspace(y0 - 0.15, y1 + 0.15, len(EFFECTS))
        if not r['coded']:
            ex.text(0.5, (y0 + y1) / 2, 'batch not yet\nreturned', transform=ex.get_yaxis_transform(), ha='center',
                    va='center', color=ps.MUTED, fontsize=ps.SMALL, style='italic')
            continue
        cset = set(r['coded'])
        rest = [k for k in r['eligible'] if k not in cset]
        e = {'n_coded': len(r['coded']), 'n_not_coded': len(rest)}
        for mi, (field, lab) in enumerate(EFFECTS):
            gen = np.random.default_rng([SEED, ri, mi])
            if field == 'is_oa':
                a = [float(bool(r['metrics'][k].get('is_oa'))) for k in r['coded']]
                b = [float(bool(r['metrics'][k].get('is_oa'))) for k in rest]
                e['is_oa_share_coded'] = round(float(np.mean(a)), 4)
                e['is_oa_share_not_coded'] = round(float(np.mean(b)), 4)
                e['is_oa_k_not_coded'] = int(sum(b))
                e['is_oa_cliffs_delta'], e['is_oa_share_diff'] = coverage(a, b, True, gen)
            else:
                e[f'{field}_cliffs_delta'], e[f'{field}_median_diff'] = coverage(
                    values(r, r['coded'], field), values(r, rest, field), False, gen)
            est, lo, hi = e[f'{field}_cliffs_delta']
            ex.errorbar(est, ey[mi], xerr=[[est - lo], [hi - est]], fmt='o', color=ps.INK, ms=3.0, mec='white',
                        mew=0.5, elinewidth=0.8, capsize=0, zorder=3)
            eticks.append((ey[mi], lab))
        cov[r['name']] = e
    ex.axvline(0, color=ps.MUTED, linewidth=0.7, zorder=1)
    ex.set_ylim(ybot, ytop)
    if eticks:
        ex.set_yticks([t[0] for t in eticks], [t[1] for t in eticks])
    else:
        ex.set_yticks([])
    ex.tick_params(axis='y', length=0, labelsize=ps.SMALL)
    ex.spines['left'].set_visible(False)
    lim = max([0.3] + [abs(v) for e in cov.values() for f, _ in EFFECTS for v in e[f'{f}_cliffs_delta']])
    ex.set_xlim(-0.2, math.ceil((lim + 0.05) * 10) / 10)
    ex.set_xticks([-0.2, 0, 0.2, 0.4][: 2 + int(lim >= 0.2) + int(lim >= 0.4)])
    ex.set_xlabel("Coded vs not coded,\nCliff's delta")
    ps.grid(ex, 'x')
    ps.panel(ex, 'e', x=-0.02)

    numbers['coverage_effect_coded_minus_not_coded'] = cov
    numbers['coverage_effect_note'] = ("[estimate, 2.5%, 97.5%]; Cliff's delta drawn in (e); median difference for cnp, "
                                       'novelty_pair, breadth_refs and share difference for is_oa in the caption; '
                                       f'percentile bootstrap, {NBOOT} resamples per group, generator '
                                       f'np.random.default_rng([{SEED}, round index, metric index]), metrics in the '
                                       'order cnp, novelty_pair, breadth_refs, is_oa')
    numbers['data_issues'] = issues

    # ---- caption: one version, written here and stored in the json ----
    r1 = rounds[0]
    s1 = {s: len(ks) for s, ks in r1['stages'] if ks is not None}
    b0 = numbers['breadth_refs_by_stage']['Round 1 Preselected']['n_zero']
    nov_floor = min(values(r, ks, 'novelty_pair').min() for _, r, _, _, ks in rows if ks is not None)

    def equal_note(r):
        q = r['quintiles']
        if len(set(q)) == 1:
            return f'equal numbers per cnp quintile ({q[0]} each)', ''
        short = [f'{"lowest second third fourth highest".split()[i]} quintile {q[i]}' for i in range(5) if q[i] < max(q)]
        return 'equal numbers per cnp quintile where the pool allowed', f'{max(q)} per quintile, {", ".join(short)}; '

    numbers['novelty_pair_min'] = round(float(nov_floor), 4)
    numbers['novelty_pair_min_prior_works'] = int(round(10 ** -nov_floor - 1))
    cap = (f"Who is in the sample. Each row is one stage of one round. Rings: the core ring is the OpenAlex topics of the "
           "study's principal investigator (the convenor), the broad ring 8 neighbouring Earth-science subfields. "
           f"Round 1: {s1['Preselected']} papers from 2022 "
           f"preselected, half per ring, with {equal_note(r1)[0]} on fixed bins of the OpenAlex citation normalized percentile "
           f"(cnp, a paper's citation rank among works of the same OpenAlex subfield, year and type; {equal_note(r1)[1]}seed "
           f"{r1['seed']}), so the sample cnp distribution is near-uniform by design: the sample is stratified on this outcome; {s1['Eligible']} passed "
           f"the eligibility screen. Coding ran on the {len(r1['coded']) + len(r1['failed'])} eligible papers with "
           f"retrieved full text")
    if r1['failed']:
        cap += (f"; {len(r1['failed'])} codings failed the format check (fields, allowed values, step order, quote "
                f"length) and are excluded, leaving {len(r1['coded'])} coded papers")
    cap += ' (Claude Opus 5.5, codebook 1.5.0).'
    if len(rounds) > 1:
        r2 = rounds[1]
        s2 = {s: len(ks) for s, ks in r2['stages'] if ks is not None}
        cap += (f" Round 2: {s2['Drawn']} open-access papers drawn from the rest of the pool, per ring, with "
                f"{equal_note(r2)[0]} ({equal_note(r2)[1]}seed {r2['seed']}); {s2['Eligible']} eligible; ")
        cap += (f"{s2['Coded']} coded." if 'Coded' in s2 else 'coding batch not yet returned.')
    cap += (f" (a) Citation normalized percentile. The median of the 2022 candidate pool "
            f"({np.median(pool_cnp):.2f}) is not drawn: the stratified draws are not a like-for-like comparison with it. "
            "(b) Rarity of the leading topic pair, -log10(1 + works published 2017 to 2021 that share it). Papers with "
            f"the same pair share a value; the left end ({nov_floor:.2f}, about {round(10 ** -nov_floor, -3):,.0f} prior works) is "
            f"the most common pair, and a value of -3.8 means about {round(10 ** 3.8, -2):,.0f} prior works. (c) Share of classified references outside geoscience, square-root axis; "
            f"{b0} of {s1['Preselected']} round 1 papers ({100 * b0 / s1['Preselected']:.0f}%) have none. Points are "
            "papers (jittered vertically); boxes give quartiles and median, whiskers 1.5 times the interquartile range. "
            "(d) Open-access share with 95% Wilson intervals (axis starts at 40%). The dashed line is the 2022 "
            f"candidate pool without convenor co-authored papers (n = {pool_n:,}; {100 * pool_oa_k / pool_n:.0f}% open "
            "access).")
    if len(rounds) > 1:
        cap += (' Round 2 is open access by construction (open-access-only draw), so its rows in (d) carry no '
                'information about the screen.')
    cap += (" (e) Coverage effect: coded papers against eligible papers not coded, as Cliff's delta, P(coded > not "
            "coded) minus P(coded < not coded) over all pairs; for open access this equals the difference in shares. "
            f"Bars are 95% percentile bootstrap intervals ({NBOOT} resamples within each group).")
    if 'Round 1' in cov:
        c = cov['Round 1']
        f = lambda t, s=1, d=2: f'{s * t[0]:+.{d}f} [{s * t[1]:+.{d}f}, {s * t[2]:+.{d}f}]'  # noqa: E731
        oa_all = oa['Round 1 Eligible']
        cap += (f" In round 1, {100 * c['is_oa_share_coded']:.0f}% of the {c['n_coded']} coded papers are open "
                f"access, against {100 * c['is_oa_share_not_coded']:.0f}% of the {c['n_not_coded']} eligible papers not "
                f"coded ({100 * oa_all['share']:.0f}% of all {oa_all['n']} eligible), a difference of "
                f"{f(c['is_oa_share_diff'], 100, 0)} percentage points. Median differences, coded minus not coded: "
                f"cnp {f(c['cnp_median_diff'])}, rarity {f(c['novelty_pair_median_diff'])}, breadth "
                f"{f(c['breadth_refs_median_diff'], d=3)}.")
    cap += (' Source: derived/{gold,r2}/metrics.json (OpenAlex, retrieved October 2026), round manifests and model '
            'codings; figure date ' + ps.TODAY + '.')

    ps.save(fig, 'fig09_sample', inputs=inputs, numbers=numbers, caption=cap)
    print(json.dumps({k: numbers[k] for k in ('stage_counts', 'is_oa_by_stage', 'first_stage_per_cnp_bin',
                                               'coverage_effect_coded_minus_not_coded', 'data_issues')}, indent=1))
    print(cap)


if __name__ == '__main__':
    main()
