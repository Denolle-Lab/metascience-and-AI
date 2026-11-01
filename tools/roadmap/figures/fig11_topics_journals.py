"""Figure 11: field and venue of the papers at each stage of the corpus, and whether coding coverage depends on venue.

Rows     panels a and b share one row per stage: the 2022 candidate pool, then round 1 (preselected -> eligible -> full
         text -> coded) and round 2 (drawn -> eligible -> full text -> coded). The round 2 coded row fills in once tag r2
         codings exist and g20 has been rerun; until then it carries a "batch not yet returned" note.
Panel a  OpenAlex subfield share per stage, stacked horizontal bars. The six subfields with the largest share at any
         stage get the six palette slots in pool order; the rest are one grey segment. Shares of 7% or more are written
         in the segment. The key above the bars runs in stack order.
Panel b  journal family share per stage, same form. Right of each bar: effective number of journals (1/HHI) and the
         number of distinct journals at that stage.
Panel c  the journals with the most coded papers (rounds with codings, pooled), one row each, with the coded count in
         the label. Three shares per journal on a log axis: in the 2022 pool, among eligible papers of the rounds that
         have codings, and among coded papers. A journal far right of its pool dot is over-represented in the coded set.
Panel d  coverage by journal family, round 1 eligible papers (each round with codings gets its own series): rate in the
         family minus the rate in all other families, for two steps, full text retrieved (hollow) and coded (filled),
         with 95% percentile bootstrap intervals. Right column: coded share and eligible count of the family.

Definitions
  OpenAlex subfield  subfield of the paper's leading topic, a machine label OpenAlex assigns from title, abstract, venue
             and citations (topic < subfield < field < domain); not an author keyword.
  journal family     publisher group from DOI prefix, then publisher, then journal name (FAMILY_RULES in
             tools/roadmap/g20_topics_journals.py); AGU is its own family although Wiley publishes it.
  share      papers of a category at a stage / papers at that stage.
  HHI        Herfindahl index, sum of squared journal shares; 1/HHI = effective number of journals, the number of
             equally sized journals that would give the same concentration.
  eligible   key in the round's manifest (derived/<calc>/manifest.jsonl); full text = eligible and status "have" in
             private/download-queue.json; coded = eligible with a coding <tag>/<key>.json that passes
             tools/check_coding.py validate() (tag calc1 round 1, r2 round 2; same rule as g17, g20, fig01, fig09).
  rate minus rest    for a family f and a step (full text among eligible, coded among eligible): rate in f minus the
             rate in all other families; 0 = no venue dependence. Families with fewer than 10 eligible papers are pooled
             (g20 MIN_GROUP). Intervals: g20, 2000 bootstrap resamples over papers.
  Cramer's V  association of two categorical variables, bias-corrected (Bergsma 2013), 0 = coverage independent of the grouping, 1 = grouping decides coverage;
             from g20, quoted in the caption.

Numbers  panels a, b, d and every summary number come from g20's topics_journals.json and are not recomputed. Panel c
         needs the share of every journal at three stages; the json keeps only the top 15 per stage, so the script
         recounts journals from the raw records with g20's own helpers (clean, coded_keys) and checks the recount
         against the json (coded n, top-journal counts); a mismatch is printed and stored in numbers['data_issues'].

Inputs
  private/data/roadmap/derived/topics/topics_journals.json   g20 results (composition, coverage, n)
  private/data/roadmap/derived/gold/pool.json                2022 candidate pool (journal per paper, panel c)
  private/data/roadmap/derived/{gold,r2}/metrics.json        journal per drawn paper (panel c)
  private/data/roadmap/derived/{calc1,r2calc}/manifest.jsonl eligible keys (panel c)
  private/analysis/codings/api/{calc1,r2}/*.json             codings, read only (panel c)

Outputs  private/data/roadmap/figures/paper/fig11_topics_journals.{pdf,png,json}
Run:     python tools/roadmap/g20_topics_journals.py && python tools/roadmap/figures/fig11_topics_journals.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from g20_topics_journals import clean, coded_keys, CODINGS, subfield_display  # noqa: E402  (tools/roadmap on sys.path via paperstyle)

D = ps.DERIVED
SRC = D / 'topics' / 'topics_journals.json'
ROUNDS = [  # json name, label, set folder, calc folder, coding tag
    ('round1', 'Round 1', 'gold', 'calc1', 'calc1'),
    ('round2', 'Round 2', 'r2', 'r2calc', 'r2'),
]
STAGES = [('drawn', None), ('eligible', 'Eligible'), ('full_text', 'Full text'), ('coded', 'Coded')]
NCOL = 6                    # coloured categories per stacked panel; the rest are grey
MIN_LABEL = 0.07            # write the share inside a segment at or above this
TOPJ = 12                   # journals in panel c
DARK = {ps.BLUE, ps.ORANGE, ps.GREEN}          # white text inside these, ink inside the light slots
SHORT_SUB = {'Water Science and Technology': 'Water science and technology', 'Earth-Surface Processes': 'Earth-surface processes',
             'Geochemistry and Petrology': 'Geochemistry and petrology', 'Artificial Intelligence': 'Artificial intelligence',
             'Atmospheric Science': 'Atmospheric science', 'Space and Planetary Science': 'Space and planetary science',
             'Ocean Engineering': 'Ocean engineering'}
SHORT_FAM = {'Springer Nature (non-portfolio)': 'Springer Nature (other)', 'Wiley non-AGU': 'Wiley (non-AGU)',
             'EGU/Copernicus': 'Copernicus (mostly EGU)',
             'pooled small groups': 'Small families pooled'}
SMALL_WORDS = {'and', 'of', 'the', 'for', 'in', 'on', 'at', 'to', '&'}


def title(name):
    """OpenAlex stores some journal names in sentence case ('The cryosphere'); title-case them for display only."""
    w = name.split()
    return ' '.join(x if (x.lower() in SMALL_WORDS and i) or x.isupper() else x[:1].upper() + x[1:] for i, x in enumerate(w))


def load(path):
    x = json.loads(Path(path).read_text())
    return x['data'] if isinstance(x, dict) and 'data' in x else x


def stage_rows(res):
    """[(label, json path tuple or None, round label or None)] in drawing order; headers carry path None."""
    n = res['n']
    rows = [(f"Pool, n = {n['pool']:,}", ('pool',), None)]
    for name, lab, *_ in ROUNDS:
        if name not in n:
            continue
        rows.append((lab, None, lab))
        for st, stlab in STAGES:
            stlab = stlab or n[name]['first_stage_label'].capitalize()
            k = n[name][st]
            rows.append((f'{stlab}, n = {k}' if k else stlab, (name, st) if k else ('missing', name, st), lab))
    return rows


def comp_at(res, path):
    c = res['composition']
    for p in path:
        c = c.get(p, {}) if isinstance(c, dict) else {}
    return c if c.get('n') else None


def stacked(ax, res, rows, ys, var, short, key_ncol, key_x=-0.01):
    """Stacked share bars for composition variable var; returns the categories coloured and the shares drawn."""
    shares = {}
    for (lab, path, _), y in zip(rows, ys):
        c = comp_at(res, path) if path and path[0] != 'missing' else None
        if c:
            shares[lab] = {k: v['share'] for k, v in c[var]['counts'].items()}
    pool = shares[rows[0][0]]
    peak = Counter()
    for s in shares.values():
        for k, v in s.items():
            peak[k] = max(peak[k], v)
    coloured = [k for k, _ in peak.most_common(NCOL)]
    coloured.sort(key=lambda k: -pool.get(k, 0))
    rest = [k for k in peak if k not in coloured]
    cols = dict(zip(coloured, ps.SERIES))
    drawn = {}
    for (lab, path, _), y in zip(rows, ys):
        if path is None:
            continue
        if lab not in shares:
            ax.text(0.01, y, 'batch not yet returned', va='center', ha='left', color=ps.MUTED, fontsize=ps.SMALL,
                    style='italic')
            continue
        s, x0, row = shares[lab], 0.0, {}
        for k in coloured + ['_rest']:
            v = s.get(k, 0.0) if k != '_rest' else sum(s.get(r, 0.0) for r in rest)
            row[k if k != '_rest' else 'other (grey)'] = round(v, 3)
            col = cols.get(k, ps.NEUTRAL)
            ax.barh(y, v, left=x0, height=0.72, color=col, edgecolor='white', linewidth=0.4, zorder=2)
            if round(100 * v) >= round(100 * MIN_LABEL):   # same rule as the printed number
                ax.text(x0 + v / 2, y, f'{100 * v:.0f}', ha='center', va='center', fontsize=ps.SMALL - 0.5,
                        color='white' if col in DARK else ps.INK, zorder=3)
            x0 += v
        drawn[lab] = row
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ['0', '25', '50', '75', '100'])
    handles = [Patch(facecolor=cols[k], label=short.get(k, k)) for k in coloured]
    handles.append(Patch(facecolor=ps.NEUTRAL, label=f'{len(rest)} others' if rest else 'others'))
    ax.legend(handles=handles, ncol=key_ncol, loc='lower left', bbox_to_anchor=(key_x, 1.0), handlelength=0.9,
              handleheight=0.9, handletextpad=0.35, columnspacing=0.9, borderaxespad=0.2, fontsize=ps.SMALL)
    return coloured, rest, drawn


def sub_note(res):
    """What the misleadingly named subfields hold, from g20 subfield_topics and ml_terms_check."""
    out = []
    st = res.get('subfield_topics', {})
    for sf, v in st.get('round1_drawn', {}).items():
        t = v['top_topics'][0] if v['top_topics'] else None
        if t and t['share'] >= 0.6 and sf in ('Artificial Intelligence', 'Atmospheric Science', 'Ocean Engineering', 'Space and Planetary Science'):
            out.append(f"{sf}: {t['n']} of {v['n']} round-1 preselected papers have the leading topic {t['topic']}")
    ml = res.get('ml_terms_check', {}).get('by_subfield', {}).get('Artificial Intelligence')
    txt = '; '.join(out) + '.' if out else ''
    if ml:
        txt += (f" Of the {ml['papers']} coded papers in the subfield Artificial Intelligence, {ml['ml_terms_anywhere']} use "
                f"machine-learning terms somewhere in their coding and {ml['ml_terms_in_an_N_step']} build a new capability "
                "described in such terms; they are seismology papers, many of them machine-learning seismology.")
    return txt


def raw_journals(res, issues):
    """Journal counts for panel c: pool, eligible and coded of the rounds that have valid codings."""
    pool = load(D / 'gold' / 'pool.json')
    key = lambda r: r.get('source_id') or clean(r.get('journal'))  # noqa: E731  (g20 journals() rule)
    names, cpool = {}, Counter()
    for r in pool:
        names.setdefault(key(r), clean(r.get('journal')))
        cpool[key(r)] += 1
    celig, ccoded, used, inputs = Counter(), Counter(), [], [D / 'gold' / 'pool.json']
    for name, lab, sset, calc, tag in ROUNDS:
        met, man = D / sset / 'metrics.json', D / calc / 'manifest.jsonl'
        if not (met.is_file() and man.is_file()):
            continue
        meta = {'g22_' + r['id']: r for r in load(met)}
        elig = [json.loads(x)['key'] for x in man.read_text().splitlines() if x.strip()]
        cod = coded_keys(tag, elig)
        nj = res['n'].get(name, {}).get('coded')
        if nj is not None and nj != len(cod):
            issues.append(f'{lab}: {len(cod)} valid codings now, {nj} in topics_journals.json; rerun g20 first')
        if not cod:
            continue
        used.append(lab)
        inputs += [met, man, CODINGS / tag]
        for k in elig:
            r = meta[k]
            names.setdefault(key(r), clean(r.get('journal')))
            celig[key(r)] += 1
            if k in cod:
                ccoded[key(r)] += 1
    # cross-check against the json's top coded journals (pooled when two rounds have codings)
    comp = res['composition']
    jc = (comp.get('pooled', {}).get('coded') if len(used) > 1 else comp.get('round1', {}).get('coded')) or {}
    for t in (jc.get('journals') or {}).get('top', []):
        mine = sum(m for k, m in ccoded.items() if names[k] == t['journal'])
        if mine != t['n']:
            issues.append(f"panel c recount: {t['journal']} {mine} coded, json {t['n']}")
    return cpool, celig, ccoded, names, used, inputs


def main():
    res = load(SRC)
    issues = []
    rows = stage_rows(res)
    numbers = {'n': res['n'], 'params_g20': res['params']}

    nrow = len(rows)
    fig = ps.figure(ps.DOUBLE, 6.3)[0]
    fig.clf()
    top_b, top_t = 0.505, 0.835
    ax_a = fig.add_axes([0.135, top_b, 0.345, top_t - top_b])
    ax_b = fig.add_axes([0.525, top_b, 0.345, top_t - top_b], sharey=ax_a)
    ax_c = fig.add_axes([0.205, 0.065, 0.30, 0.335])
    ax_d = fig.add_axes([0.665, 0.065, 0.215, 0.335])

    # ---- y layout shared by a and b: header rows tighter than stage rows ----
    ys, y = [], 0.0
    for lab, path, rnd in rows:
        if path is None:
            y += 0.25
        ys.append(y)
        y += 0.8 if path is None else 1.0
    for ax in (ax_a, ax_b):
        ax.set_ylim(ys[-1] + 0.6, -0.6)
        ax.tick_params(axis='y', length=0)
        ax.spines['left'].set_visible(False)
        ps.grid(ax, 'x')
    stage_ticks = [(y, lab) for (lab, path, _), y in zip(rows, ys) if path is not None]
    ax_a.set_yticks([t[0] for t in stage_ticks], [t[1] for t in stage_ticks])
    for (lab, path, _), y in zip(rows, ys):
        if path is None:
            ax_a.text(-0.03, y, lab, transform=ax_a.get_yaxis_transform(), ha='right', va='center',
                      fontsize=ps.FONT, fontweight='bold')
    ax_b.tick_params(axis='y', labelleft=False)

    # ---- (a) subfield, (b) journal family ----
    sub_short = {k: subfield_display(k, res, SHORT_SUB) for k in res['subfield_topics']['round1_drawn']}
    sub_short.update({k: subfield_display(k, res, SHORT_SUB) for k in res['subfield_topics']['pool'] if k not in sub_short})
    numbers['subfield_labels'] = sub_short
    sub_key = {k: (v.replace(' (', '\n(') if len(v) > 34 else v) for k, v in sub_short.items()}   # long keys wrap
    sub_col, sub_rest, sub_drawn = stacked(ax_a, res, rows, ys, 'subfield', sub_key, 2)
    ax_a.set_xlabel('Share of papers by OpenAlex subfield (%)')
    ps.panel(ax_a, 'a', x=-0.33, y=1.0 + 0.2)
    fam_col, fam_rest, fam_drawn = stacked(ax_b, res, rows, ys, 'family', SHORT_FAM, 2, key_x=0.06)
    ax_b.set_xlabel('Share of papers by journal family (%)')
    ps.panel(ax_b, 'b', x=-0.04, y=1.0 + 0.2)
    numbers['subfield_share_by_stage'] = {'coloured': sub_col, 'grey': sub_rest, 'shares': sub_drawn}
    numbers['family_share_by_stage'] = {'coloured': fam_col, 'grey': fam_rest, 'shares': fam_drawn}

    # effective / distinct journals right of (b)
    eff = {}
    ax_b.text(1.03, -0.55, 'Journals:\neffective / distinct', transform=ax_b.get_yaxis_transform(), ha='left',
              va='bottom', fontsize=ps.SMALL, color=ps.INK2, clip_on=False)
    for (lab, path, _), y in zip(rows, ys):
        c = comp_at(res, path) if path and path[0] != 'missing' else None
        if not c:
            continue
        j = c['journals']
        eff[lab] = {'effective': j['effective_journals'], 'distinct': j['distinct_journals'], 'hhi': j['hhi'],
                    'top5_share': j['top5_share']}
        ax_b.text(1.03, y, f"{j['effective_journals']:.0f} / {j['distinct_journals']}", transform=ax_b.get_yaxis_transform(),
                  ha='left', va='center', fontsize=ps.SMALL, color=ps.INK, clip_on=False)
    numbers['journal_concentration_by_stage'] = eff

    # ---- (c) top journals among coded papers ----
    cpool, celig, ccoded, names, used, raw_inputs = raw_journals(res, issues)
    tj = {}
    if ccoded:
        npool, nel, ncd = sum(cpool.values()), sum(celig.values()), sum(ccoded.values())
        top = sorted(ccoded, key=lambda k: (-ccoded[k], names[k]))[:TOPJ]
        yc = np.arange(len(top))
        series = [('pool', cpool, npool, ps.NEUTRAL, ps.INK2, 'o'), ('eligible', celig, nel, ps.ORANGE, ps.ORANGE, 'o'),
                  ('coded', ccoded, ncd, ps.AQUA, ps.INK, 'o')]
        for i, k in enumerate(top):
            v = [cnt[k] / nn for _, cnt, nn, *_ in series]
            ax_c.plot([min(v), max(v)], [i, i], color=ps.GRID, linewidth=1.0, zorder=1)
            for (lab, cnt, nn, fc, ec, mk), x in zip(series, v):
                ax_c.plot(x, i, mk, ms=4.2, mfc=fc, mec=ec if lab != 'coded' else ps.INK, mew=0.5, zorder=3)
            tj[names[k]] = {'coded_n': ccoded[k], 'eligible_n': celig[k], 'pool_n': cpool[k],
                            'coded_share': round(v[2], 4), 'eligible_share': round(v[1], 4), 'pool_share': round(v[0], 4),
                            'coded_over_pool': round(v[2] / v[0], 1)}
        ax_c.set_yticks(yc, [f'{title(names[k])} ({ccoded[k]})' for k in top])
        ax_c.set_ylim(len(top) - 0.4, -1.6)
        ax_c.set_xscale('log')
        lo_x = min(min(t['pool_share'], t['eligible_share'], t['coded_share']) for t in tj.values()) / 1.6
        hi_x = max(max(t['pool_share'], t['eligible_share'], t['coded_share']) for t in tj.values()) * 1.6
        ax_c.set_xlim(lo_x, hi_x)
        ticks = [t for t in [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2] if lo_x <= t <= hi_x]
        ax_c.set_xticks(ticks, [f'{100 * t:g}' for t in ticks])
        ax_c.minorticks_off()
        # direct labels above the first row
        v0 = [cnt[top[0]] / nn for _, cnt, nn, *_ in series]
        for j, ((lab, *_), x) in enumerate(zip(series, v0)):   # staggered so close markers keep separate labels
            ax_c.text(x, -0.6 - 0.5 * (j % 2), lab, ha='center', va='bottom', fontsize=ps.SMALL, color=ps.INK2)
        numbers['top_journals_coded'] = {'rounds': used, 'n_pool': npool, 'n_eligible': nel, 'n_coded': ncd,
                                         'distinct_journals_coded': len(ccoded), 'journals': tj}
    else:
        ax_c.text(0.5, 0.5, 'no codings yet', transform=ax_c.transAxes, ha='center', va='center', color=ps.MUTED)
    ax_c.tick_params(axis='y', length=0)
    ax_c.spines['left'].set_visible(False)
    ax_c.set_xlabel('Share of papers in the journal (%, log axis)\n' +
                    (f'n = {npool:,} pool, {nel} eligible, {ncd} coded' if ccoded else ''))
    ps.grid(ax_c, 'x')
    ps.panel(ax_c, 'c', x=-0.95, y=1.0)

    # ---- (d) coverage by journal family ----
    cov = {(r['set'], r['response']): r for r in res['coverage'] if r.get('variable') == 'family'}
    sets = [(name, lab) for name, lab, *_ in ROUNDS if (name, 'coded_among_eligible') in cov]
    dd = {}
    if sets:
        base = cov[(sets[0][0], 'coded_among_eligible')]['groups']
        fams = sorted(base, key=lambda f: (f == 'pooled small groups', -base[f]['diff_vs_rest']))
        off = {0: [0.0], 1: [-0.18, 0.18]}[len(sets) - 1] if len(sets) <= 2 else np.linspace(-0.25, 0.25, len(sets))
        rcol = [ps.BLUE, ps.ORANGE]
        for si, (name, lab) in enumerate(sets):
            dd[lab] = {}
            for resp, filled, dy in [('full_text_among_eligible', False, -0.13), ('coded_among_eligible', True, 0.13)]:
                g = cov.get((name, resp), {}).get('groups', {})
                for i, f in enumerate(fams):
                    if f not in g or g[f]['diff_vs_rest'] is None:
                        continue
                    e, (lo, hi) = g[f]['diff_vs_rest'], g[f]['diff_ci']
                    y = i + off[si] + dy * (len(sets) == 1)
                    ax_d.errorbar(e, y, xerr=[[e - lo], [hi - e]], fmt='o', ms=3.6, mfc=rcol[si] if filled else 'white',
                                  mec=rcol[si], mew=0.8, color=rcol[si], elinewidth=0.8, capsize=0, zorder=3)
                    dd[lab].setdefault(f, {})[resp] = {'n': g[f]['n'], 'rate': g[f]['rate'], 'diff_vs_rest': e,
                                                       'diff_ci': [lo, hi]}
            r = cov[(name, 'coded_among_eligible')]
            dd[lab]['_cramers_v_bc'] = {resp: {'v_bc': cov[(name, resp)]['cramers_v_bc'], 'ci': cov[(name, resp)]['v_bc_ci'],
                                               'p': cov[(name, resp)]['p'], 'q': cov[(name, resp)].get('q'),
                                               'overall_rate': cov[(name, resp)]['overall_rate']}
                                        for resp in ('full_text_among_eligible', 'coded_among_eligible', 'coded_among_full_text')
                                        if (name, resp) in cov}
        ax_d.set_yticks(range(len(fams)), [SHORT_FAM.get(f, f) for f in fams])
        ax_d.set_ylim(len(fams) - 0.5, -1.7)
        g0 = cov[(sets[0][0], 'coded_among_eligible')]['groups']
        ax_d.text(1.04, -0.75, 'coded / eligible', transform=ax_d.get_yaxis_transform(), ha='left', va='bottom',
                  fontsize=ps.SMALL, color=ps.INK2, clip_on=False)
        for i, f in enumerate(fams):
            ax_d.text(1.04, i, f"{100 * g0[f]['rate']:.0f}% of {g0[f]['n']}", transform=ax_d.get_yaxis_transform(),
                      ha='left', va='center', fontsize=ps.SMALL, color=ps.INK, clip_on=False)
        # direct labels for the two markers, on the top row
        g_ft = cov.get((sets[0][0], 'full_text_among_eligible'), {}).get('groups', {})
        if fams[0] in g_ft:
            ax_d.text(g_ft[fams[0]]['diff_vs_rest'], -1.05, 'full text', ha='center', va='bottom', fontsize=ps.SMALL,
                      color=ps.INK2, bbox={'boxstyle': 'square,pad=0.05', 'fc': 'white', 'ec': 'none'}, zorder=4)
        ax_d.text(g0[fams[0]]['diff_vs_rest'], -0.55, 'coded', ha='center', va='bottom', fontsize=ps.SMALL, color=ps.INK2)
    ax_d.axvline(0, color=ps.MUTED, linewidth=0.7, zorder=1)
    ax_d.set_xlim(-0.9, 0.9)
    ax_d.set_xticks([-0.8, -0.4, 0, 0.4, 0.8], ['-80', '-40', '0', '40', '80'])
    ax_d.set_xlabel('Rate in family minus rate in all\nother families (percentage points), round 1')
    ax_d.tick_params(axis='y', length=0)
    ax_d.spines['left'].set_visible(False)
    ps.grid(ax_d, 'x')
    ps.panel(ax_d, 'd', x=-0.85, y=1.0)
    numbers['coverage_by_family'] = dd
    numbers['coverage_note'] = ('rate minus rest and 95% percentile bootstrap intervals from g20 (2000 resamples over '
                                'papers); families with fewer than 10 eligible papers pooled')
    numbers['data_issues'] = issues
    for s in issues:
        print('WARNING', s)

    # ---- caption ----
    n = res['n']
    r1 = n['round1']
    c1 = {k[1]: v for k, v in cov.items() if k[0] == 'round1'}
    sub_cov = {(r['set'], r['response']): r for r in res['coverage'] if r.get('variable') == 'subfield'}

    def v(r):
        return f"{r['cramers_v_bc']:.2f} [{r['v_bc_ci'][0]:.2f}, {r['v_bc_ci'][1]:.2f}]"

    pool_n = n['pool']
    cap = ("Field and venue of the papers at each stage of the corpus. OpenAlex is an open index of scholarly works that "
           "supplies each paper's journal, publisher, citation counts and topic labels. The pool is every 2022 candidate "
           f"article from OpenAlex (n = {pool_n:,}): research articles with an abstract and at least 15 references, from "
           "publishers with a full-text route, in two rings: the core ring is the 8 OpenAlex topics of the study's principal "
           "investigator (the convenor: seismology, seismic waves and imaging, earthquakes, seismic sensors, cryosphere, "
           "high-pressure geophysics), the broad ring 8 Earth-science subfields. "
           f"Round 1 preselected {r1['drawn']}: half per ring, equal numbers from each quintile of "
           "cnp (OpenAlex citation normalized percentile, a paper's citation rank among works of the same OpenAlex subfield, "
           "year and type, 0 to 1) and, within a quintile, subfields taken in turn. The core ring is "
           f"{100 * res['composition']['pool']['ring']['counts']['core']['share']:.0f}% of the pool and half "
           "of round 1, so the convenor's topics are over-represented by design. Eligible papers passed an abstract screen by two independent language-model screeners "
           "(a third settled disagreements) that drops off-topic papers, reviews and comments or replies; full text means a "
           "PDF was retrieved; coded means a Claude model (claude-opus-5-5, codebook 1.5.0) read the full text and returned a "
           "coding, the paper's research workflow written as a graph of modes of inquiry defined in the codebook, that "
           "passes the schema check of tools/check_coding.py (schema fields and values, steps numbered in order, each step with a page and a quote of at most 25 words) "
           f"(round 1: {r1['eligible']} eligible, {r1['full_text']} full text, {r1['coded']} coded, so "
           f"{r1['full_text'] - r1['coded']} papers with full text have no valid coding yet; the check says nothing about "
           "whether a coding is right).")
    if 'round2' in n:
        r2 = n['round2']
        cap += (f" Round 2 drew {r2['drawn']} open-access papers from the rest of the pool, at most 4 per journal "
                f"({r2['eligible']} eligible, {r2['full_text']} full text, " +
                (f"{r2['coded']} coded)." if r2['coded'] else 'coding batch not yet returned).'))
    cap += (" (a) Share of papers by OpenAlex subfield, the subfield of the paper's leading topic as assigned by OpenAlex's "
            f"classifier (a machine label, not an author keyword); the {NCOL} subfields with the largest share at any stage "
            "are coloured, the rest grey; numbers in segments are percentages. OpenAlex files topics, not papers, under "
            "subfields, so a subfield name can mislead: where one leading topic holds at least 60% of a subfield's coded "
            "papers, the label gives it. " + sub_note(res) + " (b) Share by journal family, the publisher "
            "group read from the DOI prefix, then the publisher name: AGU, American Geophysical Union journals (published "
            "by Wiley, counted apart from other Wiley journals); Copernicus (mostly EGU), journals published by Copernicus (DOI "
            "prefix 10.5194), nearly all of the European Geosciences Union, plus European Journal of Mineralogy and "
            "Scientific Drilling; Nature portfolio, Nature-branded journals, Scientific Reports and Communications "
            "Earth & Environment; Springer Nature (other), the rest of Springer Nature; SSA, Seismological Society of "
            "America; Oxford, Oxford University Press (Geophysical Journal International). Right: effective number of "
            "journals, 1/HHI where the Herfindahl index HHI is the sum of squared journal shares (the number of equally "
            "sized journals giving the same concentration), and distinct journals.")
    if tj:
        t0 = next(iter(tj.items()))
        nc = numbers['top_journals_coded']
        cap += (f" (c) The {len(tj)} journals with the most coded papers ({', '.join(used).lower()}; coded count in "
                f"brackets): share of papers in the pool (grey, n = {nc['n_pool']:,}), among eligible papers (orange, "
                f"n = {nc['n_eligible']}) and among coded papers (green, n = {nc['n_coded']}), log axis. "
                f"{title(t0[0])} holds {100 * t0[1]['pool_share']:.1f}% of the pool, "
                f"{100 * t0[1]['eligible_share']:.1f}% of eligible and {100 * t0[1]['coded_share']:.1f}% of coded papers.")
    if 'coded_among_eligible' in c1:
        fe, ce, cf = c1.get('full_text_among_eligible'), c1['coded_among_eligible'], c1.get('coded_among_full_text')
        cap += (" (d) Coverage by journal family among round 1 eligible papers: the rate of a step in the family minus the "
                "rate in all other families, in percentage points, for full text retrieved (hollow) and coded (filled), with "
                "95% percentile bootstrap intervals (2000 resamples over papers); 0 means the family reaches the step as "
                "often as the rest; families with fewer than 10 eligible papers are pooled. Right: share of the family's "
                "eligible papers that are coded, and their number. How strongly a grouping decides coverage is given by "
                "Cramér's V, the association between two categorical variables (here the grouping and whether a paper "
                "reached the step), bias-corrected (Bergsma 2013) so that small samples with many categories are not "
                "inflated; 0 = independent, 1 = the grouping decides coverage; it measures association, not cause. The "
                "intervals are percentile intervals of the resampled V, which is biased upward under resampling, so read "
                "them as spread, not as bias-corrected intervals: "
                "family against full text " + (v(fe) if fe else 'n/a') + ", against coded " + v(ce) +
                (", against coded among papers with full text " + v(cf) if cf else '') + "; subfield against full text " +
                v(sub_cov[('round1', 'full_text_among_eligible')]) + ", against coded " +
                v(sub_cov[('round1', 'coded_among_eligible')]) +
                (", against coded among papers with full text " + v(sub_cov[('round1', 'coded_among_full_text')])
                 if ('round1', 'coded_among_full_text') in sub_cov else '') + ".")
    cap += (" Statistics from tools/roadmap/g20_topics_journals.py (descriptive; permutation tests and Benjamini-Hochberg "
            "q, the false-discovery-rate adjusted p value, in topics_journals.json); journal shares in (c) recounted from "
            "the same records. Source: OpenAlex (retrieved October 2026), round manifests, download queue and model "
            f"codings; figure date {ps.TODAY}.")

    ps.save(fig, 'fig11_topics_journals', inputs=[SRC] + raw_inputs, numbers=numbers, caption=cap)
    print(json.dumps({k: numbers[k] for k in ('journal_concentration_by_stage', 'data_issues')}, indent=1))
    print(cap)


if __name__ == '__main__':
    main()
