"""Figure 10: cost of model coding (claude-opus-5-5, Message Batches API), per paper and cumulative.

Panels (every number read from the coder's state file; nothing is re-priced here)
  a  cost per valid coding by run tag, one point per paper (deterministic jitter, seed 2026), with the median as an
     ink tick; rows grouped by experiment as registered in EXPERIMENTS.md: E0 format test (fmt-P1, fmt-P2, fmt-PX1,
     fmt-PX2), E1 first calculation (calc1), E2 test-retest (gold-r2), E3 open-review coding (calc1-review),
     E7 round 2 (r2, only once its codings are collected). The x axis stops just past the largest batch cost; the one
     coding run outside the batch API (`code_papers.py one`, full price) is drawn as a hollow edge marker with its value.
  b  cumulative spend by experiment in chronological order (waterfall: each bar starts where the previous ends)
     against the $250 cap that `code_papers.py submit --max-usd 250` enforces. Each bar carries its increment and the
     running total. Row labels give valid codings, distinct papers submitted, and requests (resubmissions and retries
     included), plus the requests in collected batches that no cost record references (E0: the first submission of
     each fmt-* tag at 07:56 on 2026-10-25, overwritten by the 08:13 rerun under the same tag:key). Requests still in an
     uncollected batch (round 2 today) are drawn hatched: their count times the mean cost of an E1 batch coding, with a
     95% interval from 5000 bootstrap sums (seed 2026) of E1 batch per-paper costs. That interval covers sampling of E1
     costs only. A second basis, the mean of all batch codings, is recorded in numbers and the caption.
  c  cost against prompt tokens (input + cache read + cache write) per valid coding, one colour
  d  cost against output tokens, same papers; the share of total recorded spend due to each token type is written
     in the panel. Pearson r describes how tokens and cost covary across papers; cost is a linear function of the
     token counts, so r is partly mechanical and is not a causal attribution.

What "cost" is: state.json done["<tag>:<key>"].usd, computed by tools/code_papers.py at collection time as token
usage times its PRICE table (USD per million tokens: input 4, output 20, cache read 0.20, cache write 5, the last an
assumption in the code) and halved for batch requests. It is recorded only for codings that passed validation, and a
rerun under the same tag:key overwrites the earlier record; requests that hit the output limit, failed validation, or
were overwritten were billed but have no usd entry, so recorded spend is a lower bound on billed spend.

Rounds: round 1 (E0-E3) is always drawn. Round 2 (tag r2, E7) is added automatically: as measured points and spend
once state.json holds r2 entries, and as a projection for any r2 requests still in flight. numbers['rounds_drawn']
records which.

Inputs
  private/analysis/codings/api/state.json   done (per-paper usage, usd, batch id), failed, batches (id, tag, keys,
                                            submitted, collected)

Outputs  private/data/roadmap/figures/paper/fig10_cost.{pdf,png,json}
Run:     python tools/roadmap/figures/fig10_cost.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402

STATE = ps.ROOT / 'private' / 'analysis' / 'codings' / 'api' / 'state.json'
CAP = 250.0
SEED = 2026
N_BOOT = 5000
# tag -> (experiment, row label); order is chronological and is the order of the rows
TAGS = [('fmt-P1', 'E0', 'PDF, run 1'), ('fmt-P2', 'E0', 'PDF, run 2'),
        ('fmt-PX1', 'E0', 'PDF + XML, run 1'), ('fmt-PX2', 'E0', 'PDF + XML, run 2'),
        ('calc1', 'E1', 'first calculation'), ('gold-r2', 'E2', 'test-retest'),
        ('calc1-review', 'E3', 'open review'), ('r2', 'E7', 'round 2')]
EXPS = [('E0', 'E0 format test'), ('E1', 'E1 first calculation'), ('E2', 'E2 test-retest'),
        ('E3', 'E3 open review'), ('E7', 'E7 round 2')]
EXP_OF = {t: e for t, e, _ in TAGS}


def load():
    st = json.loads(STATE.read_text())   # plain JSON, not a {_provenance, data} file
    rows = []
    for k, v in st['done'].items():
        tag, key = k.split(':', 1)
        u = v['usage']
        rows.append({'tag': tag, 'key': key, 'usd': float(v['usd']), 'batch': v.get('batch') is not None,
                     'prompt': u['input'] + u['cache_read'] + u['cache_write'], 'output': u['output'],
                     'usd_out': u['output'] * 20.0 / 1e6 * (0.5 if v.get('batch') is not None else 1.0)})
    referenced = {v.get('batch') for v in st['done'].values()}
    requests, papers = defaultdict(int), defaultdict(set)
    pending = defaultdict(set)
    orphan = defaultdict(list)          # collected batches that no done entry references
    for b in st['batches']:
        requests[b['tag']] += len(b['keys'])
        papers[b['tag']] |= set(b['keys'])
        if not b.get('collected'):
            pending[b['tag']] |= {k for k in b['keys'] if f"{b['tag']}:{k}" not in st['done']}
        elif b['id'] not in referenced:
            orphan[b['tag']].append({'id': b['id'], 'submitted': b.get('submitted'), 'n': len(b['keys'])})
    unknown = sorted({r['tag'] for r in rows} - set(EXP_OF))
    if unknown:
        print(f'note: tags not mapped to an experiment, left out: {unknown}')
    return (st, rows, requests, {t: len(s) for t, s in papers.items()},
            {t: len(s) for t, s in pending.items() if s}, orphan)


def column_letters(fig, cols):
    """Panel letters in one figure-coordinate column per grid column: x at the leftmost extent (tick labels
    included) of the axes in that column, y just above each axes. paperstyle.panel() places letters in axes
    coordinates, which cannot align axes of different widths, so this helper lives here."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    inv = fig.transFigure.inverted()
    for col in cols:
        x0 = min(inv.transform(ax.get_tightbbox(r).p0)[0] for ax, _ in col)
        for ax, letter in col:
            y = ax.get_position().y1 + 0.012
            fig.text(x0, y, f'({letter})', fontsize=ps.LABEL, fontweight='bold', va='bottom', ha='left')


def main():
    st, rows, requests, n_papers, pending, orphan = load()
    rng = np.random.default_rng(SEED)
    by_tag = defaultdict(list)
    for r in rows:
        if r['tag'] in EXP_OF:
            by_tag[r['tag']].append(r)
    tags = [t for t in TAGS if by_tag.get(t[0])]
    rounds = ['round 1'] + (['round 2 (measured)'] if by_tag.get('r2') else []) + \
             (['round 2 (projected, in flight)'] if pending.get('r2') else [])

    fig = ps.figure(ps.DOUBLE, 5.0)[0]
    fig.clf()
    top = GridSpec(1, 2, figure=fig, wspace=0.66, left=0.155, right=0.985, top=0.965, bottom=0.53)
    bot = GridSpec(1, 2, figure=fig, wspace=0.22, left=0.075, right=0.985, top=0.40, bottom=0.075)
    numbers = {'rounds_drawn': rounds, 'cap_usd': CAP, 'price_per_mtok_usd': {'input': 4.0, 'output': 20.0,
               'cache_read': 0.2, 'cache_write': 5.0, 'batch_discount': 0.5}}

    # (a) cost per paper by tag -------------------------------------------------------------------------------------
    ax_a = ax = fig.add_subplot(top[0, 0])
    xmax = max(r['usd'] for t, _, _ in tags for r in by_tag[t] if r['batch']) * 1.08
    ylab, a_nums, edge = [], {}, []
    for i, (tag, exp, lab) in enumerate(tags):
        y = len(tags) - 1 - i
        rs = by_tag[tag]
        c = np.array([r['usd'] for r in rs])
        jit = rng.uniform(-0.22, 0.22, len(c))
        bat = np.array([r['batch'] for r in rs])
        ax.scatter(c[bat], y + jit[bat], s=6, color=ps.BLUE, alpha=0.55, linewidths=0, zorder=2)
        for cv in c[~bat]:
            edge.append((tag, float(cv)))
            ax.scatter([min(cv, xmax * 0.985)], [y], s=16, marker='>' if cv > xmax else 'o', facecolors='white',
                       edgecolors=ps.INK, linewidths=0.6, zorder=3, clip_on=False)
            ax.annotate(f'\\${cv:.2f}, full price, not batch', (min(cv, xmax * 0.985), y), xytext=(-2, -9),
                        textcoords='offset points', fontsize=ps.SMALL, color=ps.INK2, va='top', ha='right',
                        arrowprops=dict(arrowstyle='-', color=ps.INK2, lw=0.5, shrinkA=0, shrinkB=2.5))
        med = float(np.median(c))
        ax.plot([med, med], [y - 0.34, y + 0.34], color=ps.INK, lw=1.2, zorder=4, solid_capstyle='butt')
        ylab.append(f'{exp} {lab}  (n = {len(c)})')
        a_nums[tag] = {'experiment': exp, 'n_valid': int(len(c)), 'median_usd': round(med, 4),
                       'mean_usd': round(float(c.mean()), 4), 'min_usd': round(float(c.min()), 4),
                       'max_usd': round(float(c.max()), 4), 'sum_usd': round(float(c.sum()), 2)}
    ax.set_yticks(range(len(tags))[::-1], ylab)
    ax.set_ylim(-0.6, len(tags) - 0.4)
    ax.set_xlim(0, xmax)
    ax.set_xlabel('Cost per valid coding (USD)')
    ax.tick_params(axis='y', length=0)
    ps.grid(ax, 'x')
    ax.legend(handles=[Line2D([], [], ls='none', marker='o', ms=3, color=ps.BLUE, alpha=0.7, label='One paper'),
                       Line2D([], [], color=ps.INK, lw=1.2, label='Median')],
              loc='upper right', handlelength=1.2, borderaxespad=0.2)
    numbers['a_cost_per_paper_by_tag'] = a_nums
    numbers['a_x_axis_max_usd'] = round(xmax, 4)
    numbers['a_full_price_codings'] = [{'tag': t, 'usd': round(v, 4), 'drawn_at_edge': v > xmax} for t, v in edge]

    # (b) cumulative spend by experiment against the cap ------------------------------------------------------------
    ax_b = ax = fig.add_subplot(top[0, 1])
    e1_all = np.array([r['usd'] for r in by_tag.get('calc1', [])])
    e1 = np.array([r['usd'] for r in by_tag.get('calc1', []) if r['batch']])     # round 2 is billed at batch rates
    allb = np.array([r['usd'] for t, _, _ in tags for r in by_tag[t] if r['batch']])
    exps = [e for e in EXPS if any(EXP_OF[t] == e[0] for t in by_tag) or any(EXP_OF.get(t) == e[0] for t in pending)]
    cum, b_nums, ylab = 0.0, {}, []
    proj_note = None
    for i, (e, lab) in enumerate(exps):
        y = len(exps) - 1 - i
        etags = [t for t, ee, _ in TAGS if ee == e]
        spent = sum(r['usd'] for t in etags for r in by_tag.get(t, []))
        nval = sum(len(by_tag.get(t, [])) for t in etags)
        nval_batch = sum(r['batch'] for t in etags for r in by_tag.get(t, []))   # 'one' runs are not requests
        nreq = sum(requests.get(t, 0) for t in etags)
        npap = sum(n_papers.get(t, 0) for t in etags)
        npend = sum(pending.get(t, 0) for t in etags)
        norph = sum(b['n'] for t in etags for b in orphan.get(t, []))
        rec = {'recorded_usd': round(spent, 2), 'n_valid': nval, 'n_papers': npap, 'n_requests': nreq,
               'n_requests_without_cost_record': nreq - nval_batch - npend,
               'n_requests_in_unreferenced_batches': norph,
               'unreferenced_batches': [b for t in etags for b in orphan.get(t, [])]}
        if spent > 0:
            ax.barh(y, spent, left=cum, height=0.6, color=ps.BLUE, edgecolor='white', linewidth=0.6, zorder=2)
        cum += spent
        rec['cumulative_usd'] = round(cum, 2)
        if spent > 0:
            label = f'\\${spent:,.2f}' + (f' (total \\${cum:,.2f})' if i > 0 else '')
            ax.text(cum + 4, y, label, va='center', ha='left', fontsize=ps.SMALL, color=ps.INK)
        if npend and len(e1):
            proj = npend * float(e1.mean())
            boot = rng.choice(e1, size=(N_BOOT, npend), replace=True).sum(axis=1)
            lo, hi = np.percentile(boot, [2.5, 97.5])
            ax.barh(y, proj, left=cum, height=0.6, facecolor='white', edgecolor=ps.BLUE, linewidth=0.8,
                    hatch='//////', zorder=2)
            ax.errorbar(cum + proj, y, xerr=[[proj - lo], [hi - proj]], fmt='none', ecolor=ps.INK, elinewidth=0.6,
                        capsize=1.8, capthick=0.6, zorder=3)
            ax.text(cum - 4, y, f'~\\${proj:,.0f} in flight\n(95% CI {lo:,.0f} to {hi:,.0f})\n'
                    f'total ~\\${cum + proj:,.0f} ({cum + lo:,.0f} to {cum + hi:,.0f})',
                    va='center', ha='right', fontsize=ps.SMALL, color=ps.INK, linespacing=1.15)
            alt = npend * float(allb.mean())
            proj_note = {'n': npend, 'proj': proj, 'lo': lo, 'hi': hi, 'cum': cum, 'alt': alt}
            rec.update({'n_in_flight': npend, 'projected_usd': round(proj, 2),
                        'projected_ci95_usd': [round(lo, 2), round(hi, 2)],
                        'projected_cumulative_usd': round(cum + proj, 2),
                        'projected_cumulative_ci95_usd': [round(cum + lo, 2), round(cum + hi, 2)],
                        'projection_basis': f'n in flight x mean E1 batch cost per valid coding (${e1.mean():.4f}, '
                                            f'n = {len(e1)}); CI from {N_BOOT} bootstrap sums of E1 batch costs, '
                                            'sampling of E1 costs only; projects recorded (valid-coding) spend',
                        'alt_basis_all_batch_mean_usd': round(float(allb.mean()), 4),
                        'alt_basis_n': int(len(allb)),
                        'alt_projected_usd': round(alt, 2),
                        'alt_projected_cumulative_usd': round(cum + alt, 2),
                        'e1_mean_incl_full_price_usd': round(float(e1_all.mean()), 4)})
        ylines = [lab, f'{nval} valid of {npap} papers' if nval else f'{npap} papers',
                  f'{nreq} requests' + (f' ({norph} unrecorded)' if norph else '')]
        ylab.append('\n'.join(ylines))
        b_nums[e] = rec
    ax.axvline(CAP, color=ps.INK, lw=0.8, ls=(0, (3, 2)), zorder=1)
    ax.text(CAP + 3, (len(exps) - 1) / 2 + 0.5, f'cap \\${CAP:,.0f}', ha='left', va='center', rotation=90,
            fontsize=ps.SMALL, color=ps.INK)
    ax.set_yticks(range(len(exps))[::-1], ylab)
    ax.set_ylim(-0.6, len(exps) + 0.05)
    ax.set_xlim(0, CAP * 1.06)
    ax.set_xlabel('Cumulative spend (USD)')
    ax.tick_params(axis='y', length=0)
    ps.grid(ax, 'x')
    handles = [Patch(facecolor=ps.BLUE, label='Recorded (valid codings)')]
    if pending:
        handles.append(Patch(facecolor='white', edgecolor=ps.BLUE, hatch='//////', linewidth=0.8,
                             label='In flight, projected (95% CI)'))
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.30, 1.0), handlelength=1.4, borderaxespad=0.2)
    total = sum(r['usd'] for r in rows if r['tag'] in EXP_OF)
    numbers['b_cumulative_by_experiment'] = b_nums
    numbers['b_total_recorded_usd'] = round(total, 2)
    numbers['b_headroom_to_cap_usd'] = round(CAP - total, 2)

    # (c, d) cost against tokens -----------------------------------------------------------------------------------
    pts = [r for t, _, _ in tags for r in by_tag[t]]
    bat = np.array([r['batch'] for r in pts])
    usd = np.array([r['usd'] for r in pts])
    usd_out = np.array([r['usd_out'] for r in pts])
    share_out = usd_out.sum() / usd.sum()
    cd, axcd = {}, []
    for j, (field, xl, letter, share, word) in enumerate([
            ('prompt', 'Prompt tokens per coding (thousands)', 'c', 1 - share_out, 'prompt'),
            ('output', 'Output tokens per coding (thousands)', 'd', share_out, 'output')]):
        ax = fig.add_subplot(bot[0, j])
        axcd.append(ax)
        x = np.array([r[field] for r in pts]) / 1e3
        ax.scatter(x[bat], usd[bat], s=6, color=ps.BLUE, alpha=0.55, linewidths=0, zorder=2)
        if (~bat).any():
            ax.scatter(x[~bat], usd[~bat], s=12, facecolors='white', edgecolors=ps.INK, linewidths=0.6, zorder=3)
            ax.annotate('full price', (x[~bat][0], usd[~bat][0]), xytext=(5, 0), textcoords='offset points',
                        fontsize=ps.SMALL, color=ps.INK2, va='center', ha='left')
        r = float(np.corrcoef(x[bat], usd[bat])[0, 1])
        ax.text(0.03 if letter == 'd' else 0.97, 0.97,
                f'{word.capitalize()} tokens: {share:.0%} of recorded spend\n'
                f'Pearson r = {r:.2f} (batch codings, n = {bat.sum()})',
                transform=ax.transAxes, ha='left' if letter == 'd' else 'right', va='top', fontsize=ps.SMALL,
                color=ps.INK)
        span = x.max() - x.min()
        x0 = max(0.0, np.floor((x.min() - 0.05 * span) / 5) * 5)
        ax.set_xlim(x0, x.max() + 0.05 * span)
        ax.set_ylim(0, None)
        ax.set_xlabel(xl)
        if j == 0:
            ax.set_ylabel('Cost per valid coding (USD)')
        ps.grid(ax, 'y')
        cd[letter] = {'x': field, 'n': int(len(x)), 'n_batch': int(bat.sum()), 'pearson_r_batch': round(r, 3),
                      'share_of_spend': round(float(share), 3), 'median_tokens': int(np.median(x * 1e3)),
                      'min_tokens': int(x.min() * 1e3), 'max_tokens': int(x.max() * 1e3),
                      'x_axis_from_thousands': float(x0)}
    axcd[1].sharey(axcd[0])
    axcd[0].set_ylim(0, usd.max() * 1.25)
    numbers['cd_drivers'] = cd
    column_letters(fig, [[(ax_a, 'a'), (axcd[0], 'c')], [(ax_b, 'b'), (axcd[1], 'd')]])

    # caption ------------------------------------------------------------------------------------------------------
    e0 = b_nums.get('E0', {})
    e0_orph = e0.get('unreferenced_batches', [])
    e0_first = sorted({b['submitted'] for b in e0_orph})
    e0_ids = {b['id'] for b in e0_orph}
    e0_later = sorted({b['submitted'][-5:] for b in st['batches']
                       if EXP_OF.get(b['tag']) == 'E0' and b['id'] not in e0_ids})
    req_eg = '; '.join(f'{e}: {b_nums[e]["n_requests"]} requests for {b_nums[e]["n_papers"]} papers'
                       for e in ('E1', 'E2', 'E3') if e in b_nums)
    caption = (
        'Cost of coding papers with claude-opus-5-5 through the Message Batches API. '
        '(a) Cost per valid coding by run, one point per paper, ink tick at the median; rows grouped by experiment '
        '(EXPERIMENTS.md): E0 format test (four runs of 6 papers, 4 to 6 valid codings each, codebook 1.4.0), E1 '
        'first calculation, E2 test-retest on gold papers, E3 coding with the open review discussion (codebook 1.5.0 '
        f'for E1 to E3). E1 cost per coding: median ${a_nums["calc1"]["median_usd"]:.2f}, mean '
        f'${a_nums["calc1"]["mean_usd"]:.2f} (n = {a_nums["calc1"]["n_valid"]}). '
        + (f'The axis stops at ${xmax:.2f}; the one coding run at full price outside the batch API '
           f'(${edge[0][1]:.2f}) is drawn at the edge. ' if any(v > xmax for _, v in edge) else '')
        + '(b) Cumulative spend by experiment in order against the $250 cap enforced at submission; each bar is '
        f'labelled with its increment and the running total (recorded total ${total:,.2f}). Row labels give valid '
        'codings, distinct papers submitted and requests; requests include resubmissions and retries, so they exceed '
        f'the number of papers ({req_eg}). '
        + (f'E0 was submitted twice ({", ".join(e0_first)}, then {", ".join(e0_later)} under the same tags and '
           f'papers); the first submission ({sum(b["n"] for b in e0_orph)} requests) has no cost record in '
           'state.json because the rerun overwrote it, so E0 spend covers the second submission only. '
           if e0_orph else '')
        + (f'Hatched: {proj_note["n"]} round-2 requests still in flight, projected at the mean cost of an E1 batch '
           f'coding (${e1.mean():.4f}, n = {len(e1)}): ~${proj_note["proj"]:.0f}, 95% interval '
           f'{proj_note["lo"]:.0f} to {proj_note["hi"]:.0f} from {N_BOOT} bootstrap sums of E1 batch costs, '
           f'giving a total of ~${proj_note["cum"] + proj_note["proj"]:.0f}. The interval reflects sampling of E1 '
           'per-paper costs only, not differences between the round-1 and round-2 corpora (round 2 is open access '
           'only, spread over 157 journals, with XML for 105 papers, EXPERIMENTS.md E7) or retries, and it projects recorded '
           '(valid-coding) spend, not billed spend. At the mean of all batch codings '
           f'(${allb.mean():.2f}, n = {len(allb)}; the basis of the ~$52 estimate in EXPERIMENTS.md E7) the '
           f'projection is ${proj_note["alt"]:.0f} (total ${proj_note["cum"] + proj_note["alt"]:.0f}), above the '
           'interval. ' if proj_note else '')
        + f'(c, d) Cost per coding against prompt tokens (input plus cache) and output tokens for all '
        f'{len(pts)} valid codings ({int(bat.sum())} batch, {int((~bat).sum())} at full price, drawn hollow). '
        f'Output tokens account for {share_out:.0%} of recorded spend. Cost is a linear function of the token '
        'counts, so Pearson r describes how tokens and cost covary across papers, not a causal driver. '
        'Cost is token usage times the price table in tools/code_papers.py, halved for batch requests, and is '
        'recorded only for codings that passed validation: requests that hit the output limit, failed validation, '
        'or were overwritten by a rerun were billed but are not counted, so spend is a lower bound. '
        f'Source: private/analysis/codings/api/state.json, read {ps.TODAY}.')
    ps.save(fig, 'fig10_cost', inputs=[STATE], numbers=numbers, caption=caption)


if __name__ == '__main__':
    main()
