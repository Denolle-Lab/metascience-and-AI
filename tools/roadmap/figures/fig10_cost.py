"""Figure 10: cost of every paid model run of the roadmap (claude-opus-5-5, Message Batches API), per coding and cumulative.

Panels (every number read from the coder's state file; nothing is re-priced here)
  a  cost per valid coding by run, one point per paper (deterministic jitter, seed 2026), with the median as an ink
     tick. Rows in time order of first submission, labelled with the experiment of EXPERIMENTS.md: E0 format test
     (fmt-P1, fmt-P2, fmt-PX1, fmt-PX2), E1 first calculation, E2 test-retest (gold-r2), E3 open-review coding
     (calc1-review), E7 round 2 (r2, top-up and retries included), E1b round-1 top-up, E11 advance pilot 1
     (pilot-a/b-advance), pilot 2 (pilot2-a/b-advance) and full run (full-advance), E16 review v2 (calc1-review-v2,
     r2-review-v2). A calc1 coding belongs to E1 or E1b by the batch in which its paper was first submitted under
     calc1. The leak probes (g25) are not codings and are not drawn here. The x axis stops just past the largest batch
     cost; the one coding run outside the batch API (`code_papers.py one`, full price) is drawn as a hollow edge marker.
  b  cumulative spend in time order of first submission (waterfall: each bar starts where the previous ends), one row
     per experiment or step: E0, E1, E2, E3, E7 round 2, E7 round-2 top-up (msgbatch_01HTgc7EkMN55Gd8gzUtQPjm),
     E1b round-1 top-up (msgbatch_01EsvmQCFDiY2ido76NMGZK3), the October 27 retries (msgbatch_013ZG3gufNPdiUFbVWpDQRwG,
     msgbatch_01EmbCm5vt45XfPoVVWJgBPP), E11 advance pilot 1, pilot 2, leak probes (g25, tags leak-venue and
     leak-recognition), full advance run, E16 review v2 pilot (msgbatch_01QhNfQMBJWQPgWb3ua81dFE and its redraw
     msgbatch_011KaWJ7a7t8UWd4UCVWSF24) and E16 review v2 of rounds 1 and 2 (the rest). Solid: cost of valid codings;
     light: billed attempts that did not end as the kept valid coding (output-limit stops, invalid answers, redraws),
     known only for runs recorded in state.json 'spent' (from October 27 23:50, advance pilot 1 on). Rows before
     that count valid codings only and their increment is printed with a >= sign. The cap in force is drawn as a step
     line (CAPS below): $250 from the start, then each raise from the time its DECISIONS.md entry was committed in the
     private repo. Requests still in an uncollected batch are drawn hatched: their count times the mean first-attempt
     cost of the same task already measured, with a 95% interval from 5000 bootstrap sums (seed 2026) of those costs;
     a hollow diamond marks the projection that also counts redraws at the measured rate (billed per paper over all
     attempts). The interval covers sampling of the measured costs only.
  c  cost against prompt tokens (input + cache read + cache write) per valid coding, inquiry and open-review codings
     of E0 to E7 and E1b (tags of C_TAGS), as before the advance runs
  d  cost against output tokens, same papers; the share of their recorded spend due to each token type is written
     in the panel. Pearson r describes how tokens and cost covary across papers; cost is a linear function of the
     token counts, so r is partly mechanical and is not a causal attribution.

What "cost" is: state.json 'spent' ("<tag>:<key>": every returned attempt with usage and usd, from October 27 23:50 on)
and done["<tag>:<key>"].usd for runs before 'spent' existed, both computed by tools/code_papers.py (and g25 for the leak
probes) at collection time as token usage times its PRICE table (USD per million tokens: input 4, output 20, cache read
0.20, cache write 5, the last an assumption in the code) and halved for batch requests. The total is the same sum as
code_papers.spent_usd(), which the --max-usd cap of every submit uses, less batch attempts that repeat an earlier
attempt's tag:key, batch and usage (one result recorded twice by two collectors of one batch; their number and dollars
are in numbers['duplicate_records_dropped'] and the caption). Not recorded anywhere, so not counted: the
first E0 submission (overwritten by its rerun), failed and overwritten requests before 'spent' existed, and the
full-price cache pre-warm request sent before each batch from the round-2 top-up on (printed at submission only).

Inputs
  private/analysis/codings/api/state.json   spent (attempts), done (valid codings: usage, usd, batch id), batches (id,
                                            tag, keys, submitted, collected); read only, while collectors may write it,
                                            so the sha256 of the bytes read is recorded in numbers['state_sha256_16']
  CAPS below                                cap history from private/data/roadmap/DECISIONS.md and the private commits
                                            that recorded each entry (git -C private log -- data/roadmap/DECISIONS.md)

Outputs  private/data/roadmap/figures/paper/fig10_cost.{pdf,png,json}
Run:     python tools/roadmap/figures/fig10_cost.py   (or make_all.py fig10)
"""
import hashlib
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

STATE = ps.PRIVATE / 'analysis' / 'codings' / 'api' / 'state.json'
SEED = 2026
N_BOOT = 5000
LEDGER_FROM = '2026-10-27 23:50'   # first attempt recorded in state.json 'spent' (advance pilot 1)
# Cap history (private/data/roadmap/DECISIONS.md). 'from' is the local time (UTC-6) of the private commit that recorded
# the decision; a cap applies to rows first submitted at or after it. $250 had no earlier cap and is drawn from the
# start (E1 was submitted with --max-usd 250 at 12:04 on October 25, before commit 9c7785a recorded the line).
CAPS = [{'usd': 250.0, 'date': 'Oct 25', 'from': '', 'commit': '9c7785a', 'spend_at_decision': None},
        {'usd': 400.0, 'date': 'Oct 27', 'from': '2026-10-27 22:19', 'commit': 'e19677b', 'spend_at_decision': 221.59},
        {'usd': 500.0, 'date': 'Oct 28', 'from': '2026-10-28 07:00', 'commit': 'dd3bb0d', 'spend_at_decision': 229.64},
        {'usd': 600.0, 'date': 'Oct 28', 'from': '2026-10-28 11:58', 'commit': '70412da', 'spend_at_decision': None}]

# rows of panel b: id, label, experiment. Shown when they carry spend or requests in flight, ordered by first submission
ROWS = [('E0', 'E0 format test'), ('E1', 'E1 first calculation'), ('E2', 'E2 test-retest'), ('E3', 'E3 open review'),
        ('E7', 'E7 round 2'), ('E7t', 'E7 round-2 top-up'), ('E1b', 'E1b round-1 top-up'),
        ('retry', 'Retries, rounds 1 and 2'), ('A1', 'E11 advance pilot 1'), ('A2', 'E11 advance pilot 2'),
        ('LP', 'E11 leak probes (g25)'), ('AF', 'E11 full advance run'), ('RVp', 'E16 review v2 pilot'),
        ('RV', 'E16 review v2, rounds 1-2'), ('R12', 'Rounds 1-2 completion'), ('C22', '2022 draw (cop22)'),
        ('other', 'Other tags')]
ROW_LABEL = dict(ROWS)
BATCH_ROW = {'msgbatch_01HTgc7EkMN55Gd8gzUtQPjm': 'E7t', 'msgbatch_01EsvmQCFDiY2ido76NMGZK3': 'E1b',
             'msgbatch_013ZG3gufNPdiUFbVWpDQRwG': 'retry', 'msgbatch_01EmbCm5vt45XfPoVVWJgBPP': 'retry',
             'msgbatch_01QhNfQMBJWQPgWb3ua81dFE': 'RVp', 'msgbatch_011KaWJ7a7t8UWd4UCVWSF24': 'RVp'}
KNOWN_UNTIL = '2026-10-28 11:57'   # last batch this mapping was written against; later calc1/r2 batches go to R12
# panel a rows: tag-level rows for E0, then groups; the group of a coding is the panel-b row of the batch in which its
# paper was first submitted under its tag, merged as below
A_FMT = [('fmt-P1', 'E0 PDF, run 1'), ('fmt-P2', 'E0 PDF, run 2'), ('fmt-PX1', 'E0 PDF + XML, run 1'),
         ('fmt-PX2', 'E0 PDF + XML, run 2')]
A_MERGE = {'E7t': 'E7', 'retry': None, 'RVp': 'RV', 'LP': None}   # None: not a group of its own (retry: never a first batch)
A_LABEL = {'E1': 'E1 first calculation', 'E2': 'E2 test-retest', 'E3': 'E3 open review', 'E7': 'E7 round 2',
           'E1b': 'E1b round-1 top-up', 'A1': 'E11 advance pilot 1', 'A2': 'E11 advance pilot 2',
           'AF': 'E11 full advance', 'RV': 'E16 review v2', 'R12': 'Rounds 1-2 completion', 'C22': '2022 draw (cop22)'}
C_TAGS = {'fmt-P1', 'fmt-P2', 'fmt-PX1', 'fmt-PX2', 'calc1', 'gold-r2', 'calc1-review', 'r2'}   # panels c, d
# projection basis for requests in flight: first attempts of the same task already returned
FAMILY = {'RV': 'review-v2', 'RVp': 'review-v2', 'AF': 'advance', 'A1': 'advance', 'A2': 'advance', 'R12': 'inquiry'}


def tag_row(tag: str, batch: dict | None) -> str:
    bid = batch['id'] if batch else None
    if bid in BATCH_ROW:
        return BATCH_ROW[bid]
    late = bool(batch) and batch.get('submitted', '') > KNOWN_UNTIL
    if tag.startswith('cop22'):
        return 'C22'
    if tag.startswith('fmt-'):
        return 'E0'
    if tag in ('calc1', 'r2', 'gold-r2') and late:
        return 'R12'
    if tag.endswith('-review-v2'):
        return 'RV'
    if tag.startswith('leak-'):
        return 'LP'
    return {'calc1': 'E1', 'gold-r2': 'E2', 'calc1-review': 'E3', 'r2': 'E7', 'pilot-a-advance': 'A1',
            'pilot-b-advance': 'A1', 'pilot2-a-advance': 'A2', 'pilot2-b-advance': 'A2',
            'full-advance': 'AF'}.get(tag, 'other')


def family_of(tag: str) -> str:
    if tag.endswith('-review-v2'):
        return 'review-v2'
    if tag.endswith('-advance'):
        return 'advance'
    if tag.startswith('leak-'):
        return 'probe'
    return 'inquiry'


def load():
    raw = STATE.read_bytes()   # plain JSON, not a {_provenance, data} file
    st = json.loads(raw)
    sha = hashlib.sha256(raw).hexdigest()[:16]
    batches = {b['id']: b for b in st['batches']}
    sp, done = st.get('spent', {}), st['done']
    # one item per billed result: every ledger attempt, plus done records of keys with no ledger entry (older runs)
    # A batch result recorded twice (two collectors for one batch; save_state drops a repeat only when the whole record,
    # 'at' minute included, matches) is one billed result: drop batch attempts that repeat tag:key, batch and usage.
    items, dup = [], {'n': 0, 'usd': 0.0, 'by_batch': defaultdict(lambda: {'n': 0, 'usd': 0.0, 'ok': 0, 'failed': 0})}
    for k, attempts in sp.items():
        tag, key = k.split(':', 1)
        seen, n = set(), 0
        for a in attempts:
            sig = (a.get('batch'), json.dumps(a.get('usage'), sort_keys=True))
            if a.get('batch') is not None and sig in seen:
                d = dup['by_batch'][a['batch']]
                d['n'] += 1; d['usd'] += float(a.get('usd') or 0)
                d['ok' if str(a.get('outcome', '')).startswith('ok') else 'failed'] += 1
                dup['n'] += 1; dup['usd'] += float(a.get('usd') or 0)
                continue
            seen.add(sig)
            items.append({'tag': tag, 'key': key, 'batch': a.get('batch'), 'usd': float(a.get('usd') or 0),
                          'at': a.get('at'), 'attempt': n, 'ledger': True, 'outcome': a.get('outcome', '')})
            n += 1
    for k, v in done.items():
        if k not in sp:
            tag, key = k.split(':', 1)
            items.append({'tag': tag, 'key': key, 'batch': v.get('batch'), 'usd': float(v['usd']), 'at': None,
                          'attempt': 0, 'ledger': False, 'outcome': 'ok'})
    for it in items:
        it['row'] = tag_row(it['tag'], batches.get(it['batch']))
    # valid codings
    first_batch = {}   # (tag, key) -> earliest batch submitting it
    for b in sorted(st['batches'], key=lambda b: b.get('submitted', '')):
        for k in b['keys']:
            first_batch.setdefault((b['tag'], k), b)
    valid = []
    for k, v in done.items():
        tag, key = k.split(':', 1)
        u = v['usage']
        b = batches.get(v.get('batch'))
        first = first_batch.get((tag, key))
        valid.append({'tag': tag, 'key': key, 'usd': float(v['usd']), 'batch': v.get('batch') is not None,
                      'row': tag_row(tag, b), 'group': tag_row(tag, first) if first else tag_row(tag, b),
                      'prompt': u['input'] + u['cache_read'] + u['cache_write'], 'output': u['output'],
                      'usd_out': u['output'] * 20.0 / 1e6 * (0.5 if v.get('batch') is not None else 1.0)})
    # requests, papers, requests in flight, collected batches nothing references, first submission per row
    referenced = {it['batch'] for it in items}
    rows = defaultdict(lambda: {'requests': 0, 'papers': 0, 'pending': 0, 'orphan': [], 'first': None,
                                'batches': [], 'tags': set()})
    papers = defaultdict(set)
    attempted = {(it['batch'], it['tag'], it['key']) for it in items if it['ledger']}
    for b in st['batches']:
        r = tag_row(b['tag'], b)
        R = rows[r]
        R['requests'] += len(b['keys'])
        R['batches'].append(b['id'])
        R['tags'].add(b['tag'])
        papers[(r, b['tag'])] |= set(b['keys'])
        R['first'] = min(filter(None, [R['first'], b.get('submitted')]))
        if not b.get('collected'):
            R['pending'] += sum(1 for k in b['keys'] if (b['id'], b['tag'], k) not in attempted
                                and not (f"{b['tag']}:{k}" in done and done[f"{b['tag']}:{k}"].get('batch') == b['id']))
        elif b['id'] not in referenced:
            R['orphan'].append({'id': b['id'], 'submitted': b.get('submitted'), 'n': len(b['keys'])})
    for (r, _), s in papers.items():
        rows[r]['papers'] += len(s)
    return st, sha, items, valid, rows, dup


def bootstrap(costs, n, rng):
    costs = np.asarray(costs, float)
    proj = n * float(costs.mean())
    if len(costs) < 2:
        return proj, None, None
    boot = rng.choice(costs, size=(N_BOOT, n), replace=True).sum(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return proj, float(lo), float(hi)


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
            y = ax.get_position().y1 + 0.008
            fig.text(x0, y, f'({letter})', fontsize=ps.LABEL, fontweight='bold', va='bottom', ha='left')


def short_date(ts: str) -> str:
    m = {'10': 'Oct', '11': 'Nov', '12': 'Dec'}
    return f"{m.get(ts[5:7], ts[5:7])} {int(ts[8:10])}" if ts else ''


def main():
    st, sha, items, valid, rows, dup = load()
    rng = np.random.default_rng(SEED)
    order = {r: i for i, (r, _) in enumerate(ROWS)}
    b_rows = sorted((r for r in rows if r in order and (any(it['row'] == r for it in items) or rows[r]['pending'])),
                    key=lambda r: (rows[r]['first'] or '9999', order[r]))
    unknown = sorted({it['tag'] for it in items if it['row'] == 'other'})
    if unknown:
        print(f'note: tags not mapped to a row, drawn as "Other tags": {unknown}')

    fig = ps.figure(ps.DOUBLE, 7.6)[0]
    fig.clf()
    top = GridSpec(1, 2, figure=fig, width_ratios=[1, 1.2], wspace=0.72, left=0.135, right=0.985, top=0.975,
                   bottom=0.385)
    bot = GridSpec(1, 2, figure=fig, wspace=0.22, left=0.075, right=0.985, top=0.285, bottom=0.055)
    numbers = {'state_sha256_16': sha, 'price_per_mtok_usd': {'input': 4.0, 'output': 20.0, 'cache_read': 0.2,
               'cache_write': 5.0, 'batch_discount': 0.5}, 'ledger_from': LEDGER_FROM,
               'cap_history': CAPS}

    # (a) cost per valid coding ------------------------------------------------------------------------------------
    ax_a = ax = fig.add_subplot(top[0, 0])
    groups = []   # (id, label, codings)
    for tag, lab in A_FMT:
        cs = [v for v in valid if v['tag'] == tag]
        if cs:
            groups.append((tag, lab, cs))
    gmap = defaultdict(list)
    for v in valid:
        if v['tag'].startswith('fmt-'):
            continue
        g = A_MERGE.get(v['group'], v['group'])
        if g:
            gmap[g].append(v)
    for g in sorted(gmap, key=lambda g: (rows[g]['first'] or '9999', order.get(g, 99))):
        if g in A_LABEL:
            groups.append((g, A_LABEL[g], gmap[g]))
    xmax = max(v['usd'] for _, _, cs in groups for v in cs if v['batch']) * 1.08
    ylab, a_nums, edge = [], {}, []
    for i, (gid, lab, cs) in enumerate(groups):
        y = len(groups) - 1 - i
        c = np.array([v['usd'] for v in cs])
        jit = rng.uniform(-0.22, 0.22, len(c))
        bat = np.array([v['batch'] for v in cs])
        ax.scatter(c[bat], y + jit[bat], s=5, color=ps.BLUE, alpha=0.5, linewidths=0, zorder=2)
        for cv in c[~bat]:
            edge.append((gid, float(cv)))
            ax.scatter([min(cv, xmax * 0.985)], [y], s=16, marker='>' if cv > xmax else 'o', facecolors='white',
                       edgecolors=ps.INK, linewidths=0.6, zorder=3, clip_on=False)
            ax.annotate(f'\\${cv:.2f}, full price', (min(cv, xmax * 0.985), y), xytext=(-2, -7),
                        textcoords='offset points', fontsize=ps.SMALL, color=ps.INK2, va='top', ha='right',
                        arrowprops=dict(arrowstyle='-', color=ps.INK2, lw=0.5, shrinkA=0, shrinkB=2.5))
        med = float(np.median(c))
        ax.plot([med, med], [y - 0.34, y + 0.34], color=ps.INK, lw=1.2, zorder=4, solid_capstyle='butt')
        ylab.append(f'{lab}  (n = {len(c)})')
        a_nums[gid] = {'label': lab, 'tags': sorted({v['tag'] for v in cs}), 'n_valid': int(len(c)),
                       'median_usd': round(med, 4), 'mean_usd': round(float(c.mean()), 4),
                       'min_usd': round(float(c.min()), 4), 'max_usd': round(float(c.max()), 4),
                       'sum_usd': round(float(c.sum()), 2)}
    ax.set_yticks(range(len(groups))[::-1], ylab)
    ax.set_ylim(-0.6, len(groups) - 0.4)
    ax.set_xlim(0, xmax)
    ax.set_xlabel('Cost per valid coding (USD)')
    ax.tick_params(axis='y', length=0)
    ps.grid(ax, 'x')
    ax.legend(handles=[Line2D([], [], ls='none', marker='o', ms=3, color=ps.BLUE, alpha=0.7, label='One paper'),
                       Line2D([], [], color=ps.INK, lw=1.2, label='Median')],
              loc='upper right', handlelength=1.2, borderaxespad=0.2)
    numbers['a_cost_per_valid_coding'] = a_nums
    numbers['a_x_axis_max_usd'] = round(xmax, 4)
    numbers['a_full_price_codings'] = [{'group': g, 'usd': round(v, 4), 'drawn_at_edge': v > xmax} for g, v in edge]

    # (b) cumulative spend against the cap in force ----------------------------------------------------------------
    ax_b = ax = fig.add_subplot(top[0, 1])
    n = len(b_rows)
    cum, b_nums, ylab, caps_drawn, proj_rows = 0.0, {}, [], [], []
    xmax_b = max(c['usd'] for c in CAPS) * 1.1
    for i, r in enumerate(b_rows):
        y = n - 1 - i
        its = [it for it in items if it['row'] == r]
        billed = sum(it['usd'] for it in its)
        vs = [v for v in valid if v['row'] == r]
        val = sum(v['usd'] for v in vs)
        other = billed - val
        ledger = any(it['ledger'] for it in its)
        R = rows[r]
        if billed > 0:
            ax.barh(y, val, left=cum, height=0.62, color=ps.BLUE, edgecolor='white', linewidth=0.5, zorder=2)
            if other > 0.005:
                ax.barh(y, other, left=cum + val, height=0.62, color=ps.SEQ[1], edgecolor='white', linewidth=0.5,
                        zorder=2)
        start = cum
        cum += billed
        cap = [c for c in CAPS if c['from'] <= (R['first'] or '')][-1]
        caps_drawn.append(cap['usd'])
        rec = {'label': ROW_LABEL[r], 'first_submitted': R['first'], 'batches': R['batches'], 'tags': sorted(R['tags']),
               'billed_usd': round(billed, 2), 'valid_usd': round(val, 2), 'other_billed_usd': round(other, 2),
               'ledger': ledger, 'n_valid': len(vs), 'n_submitted': R['papers'], 'n_requests': R['requests'],
               'n_attempts': sum(1 for it in its if it['ledger']), 'n_in_flight': R['pending'],
               'cumulative_start_usd': round(start, 2), 'cumulative_usd': round(cum, 2), 'cap_in_force_usd': cap['usd'],
               'unreferenced_batches': R['orphan']}
        if billed > 0:
            ge = '' if ledger else '\u2265'
            ax.text(cum + 5, y, f'{ge}\\${billed:,.2f}' + (f'\ntotal \\${cum:,.0f}' if i else ''), va='center',
                    ha='left', fontsize=ps.SMALL, color=ps.INK, zorder=5, linespacing=1.05,
                    bbox=dict(boxstyle='square,pad=0.05', facecolor='white', edgecolor='none', alpha=0.85))
        if R['pending']:
            fam = FAMILY.get(r)
            firsts, per_paper = [], defaultdict(float)
            for it in items:
                if it['ledger'] and family_of(it['tag']) == fam:
                    per_paper[(it['tag'], it['key'])] += it['usd']
                    if it['attempt'] == 0:
                        firsts.append(it['usd'])
            if firsts:
                proj, lo, hi = bootstrap(firsts, R['pending'], rng)
                redraw = R['pending'] * float(np.mean(list(per_paper.values())))
                ax.barh(y, proj, left=cum, height=0.62, facecolor='white', edgecolor=ps.BLUE, linewidth=0.8,
                        hatch='//////', zorder=2)
                if lo is not None:
                    ax.errorbar(cum + proj, y, xerr=[[proj - lo], [hi - proj]], fmt='none', ecolor=ps.INK,
                                elinewidth=0.6, capsize=1.8, capthick=0.6, zorder=3)
                ax.plot([cum + redraw], [y], marker='D', ms=3.2, mfc='white', mec=ps.INK, mew=0.6, ls='none', zorder=4)
                ci = f' (95% CI {cum + lo:,.0f} to {cum + hi:,.0f})' if lo is not None else ''
                ax.text(cum - 5, y, f'{R["pending"]} requests in flight: ~\\${proj:,.0f}\n'
                        f'total ~\\${cum + proj:,.0f}{ci}\nwith redraws ~\\${cum + redraw:,.0f} (diamond)',
                        va='center', ha='right', fontsize=ps.SMALL, color=ps.INK, linespacing=1.15)
                rec.update({'projection_family': fam, 'projection_basis_n': len(firsts),
                            'projection_basis_mean_first_attempt_usd': round(float(np.mean(firsts)), 4),
                            'projected_usd': round(proj, 2),
                            'projected_ci95_usd': [round(lo, 2), round(hi, 2)] if lo is not None else None,
                            'projected_cumulative_usd': round(cum + proj, 2),
                            'projected_cumulative_ci95_usd': [round(cum + lo, 2), round(cum + hi, 2)]
                            if lo is not None else None,
                            'projection_basis_papers': len(per_paper),
                            'projection_basis_billed_per_paper_usd': round(float(np.mean(list(per_paper.values()))), 4),
                            'projected_with_redraws_usd': round(redraw, 2),
                            'projected_cumulative_with_redraws_usd': round(cum + redraw, 2)})
                proj_rows.append((r, rec))
        nv = f'{len(vs)} of {R["papers"]} valid' if billed > 0 else f'{R["papers"]} in flight'
        orph = sum(b['n'] for b in R['orphan'])
        ylab.append(f'{ROW_LABEL[r]}, {short_date(R["first"])}\n{nv}, {R["requests"]} requests'
                    + (f' ({orph} unrecorded)' if orph else ''))
        b_nums[r] = rec
    # cap step line: one vertical segment per row, horizontal at row boundaries; a stub below the last row for a cap
    # raised after the last submission
    xs, ys, starts = [], [], []
    for i, c in enumerate(caps_drawn):
        y = n - 1 - i
        if i == 0 or c != caps_drawn[i - 1]:
            starts.append((c, y + 0.5))
        xs += [c, c]
        ys += [y + 0.5, y - 0.5]
    now = CAPS[-1]['usd']
    stub = now != caps_drawn[-1]
    if stub:
        xs += [now, now]
        ys += [-0.5, -1.15]
        starts.append((now, -0.5))
    ax.plot(xs, ys, color=ps.INK, lw=0.8, ls=(0, (3, 2)), zorder=1)
    for c, ytop in starts:
        cp = next(x for x in CAPS if x['usd'] == c)
        when = cp['date'] + (f', {cp["from"][-5:]}' if cp['from'] else '')
        below = stub and c == now
        ax.text(c + (-6 if below else 6), ytop - 0.12, f'cap \\${c:,.0f}\n{when}', ha='right' if below else 'left',
                va='top', fontsize=ps.SMALL, color=ps.INK, linespacing=1.1)
    ax.set_yticks(range(n)[::-1], ylab)
    ax.set_ylim(-1.2 if stub else -0.6, n - 0.4)
    ax.set_xlim(0, xmax_b)
    ax.set_xlabel('Cumulative spend (USD)')
    ax.tick_params(axis='y', length=0, labelsize=ps.SMALL)
    for t in ax.get_yticklabels():
        t.set_linespacing(1.05)
    ps.grid(ax, 'x')
    handles = [Patch(facecolor=ps.BLUE, label='Valid codings'),
               Patch(facecolor=ps.SEQ[1], label='Other billed attempts\n(recorded from Oct 27 23:50)')]
    if proj_rows:
        handles += [Patch(facecolor='white', edgecolor=ps.BLUE, hatch='//////', linewidth=0.8,
                          label='In flight, projected (95% CI)')]
    handles.append(Line2D([], [], color=ps.INK, lw=0.8, ls=(0, (3, 2)), label='Cap in force'))
    ax.legend(handles=handles, loc='upper right', bbox_to_anchor=(1.0, 0.875), handlelength=1.4, borderaxespad=0.3,
              labelspacing=0.5)
    total = sum(it['usd'] for it in items)
    total_valid = sum(v['usd'] for v in valid)
    numbers['b_rows'] = b_nums
    numbers['b_total_recorded_usd'] = round(total, 2)
    numbers['b_total_valid_codings_usd'] = round(total_valid, 2)
    numbers['b_total_other_billed_usd'] = round(total - total_valid, 2)
    numbers['b_cap_now_usd'] = now
    numbers['b_headroom_to_cap_usd'] = round(now - total, 2)
    checks = {}
    for c in CAPS:
        if c['spend_at_decision'] is not None:
            before = [b_nums[r]['cumulative_start_usd'] for r in b_rows if b_nums[r]['cap_in_force_usd'] == c['usd']]
            checks[f"cap_{c['usd']:.0f}"] = {'spend_at_decision_recorded': c['spend_at_decision'],
                                              'cumulative_before_first_row_under_it': before[0] if before else None}
    numbers['b_cap_placement_check'] = checks
    if proj_rows:
        numbers['b_projected_total_usd'] = round(total + sum(p['projected_usd'] for _, p in proj_rows), 2)
        numbers['b_projected_total_with_redraws_usd'] = round(
            total + sum(p['projected_with_redraws_usd'] for _, p in proj_rows), 2)

    # (c, d) cost against tokens, inquiry and open-review codings of E0 to E7 and E1b --------------------------------
    pts = [v for v in valid if v['tag'] in C_TAGS]
    bat = np.array([v['batch'] for v in pts])
    usd = np.array([v['usd'] for v in pts])
    usd_out = np.array([v['usd_out'] for v in pts])
    share_out = usd_out.sum() / usd.sum()
    cd, axcd = {}, []
    for j, (field, xl, letter, share, word) in enumerate([
            ('prompt', 'Prompt tokens per coding (thousands)', 'c', 1 - share_out, 'prompt'),
            ('output', 'Output tokens per coding (thousands)', 'd', share_out, 'output')]):
        ax = fig.add_subplot(bot[0, j])
        axcd.append(ax)
        x = np.array([v[field] for v in pts]) / 1e3
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
        cd[letter] = {'x': field, 'tags': sorted(C_TAGS), 'n': int(len(x)), 'n_batch': int(bat.sum()),
                      'pearson_r_batch': round(r, 3), 'share_of_spend': round(float(share), 3),
                      'median_tokens': int(np.median(x * 1e3)), 'min_tokens': int(x.min() * 1e3),
                      'max_tokens': int(x.max() * 1e3), 'x_axis_from_thousands': float(x0)}
    axcd[1].sharey(axcd[0])
    axcd[0].set_ylim(0, usd.max() * 1.25)
    numbers['cd_drivers'] = cd
    numbers['duplicate_records_dropped'] = {'n': dup['n'], 'usd': round(dup['usd'], 2), 'by_batch': {
        b: {**d, 'usd': round(d['usd'], 2)} for b, d in dup['by_batch'].items()}}
    column_letters(fig, [[(ax_a, 'a'), (axcd[0], 'c')], [(ax_b, 'b'), (axcd[1], 'd')]])

    # caption ------------------------------------------------------------------------------------------------------
    e0 = b_nums.get('E0', {})
    e0_orph = e0.get('unreferenced_batches', [])
    e0_first = sorted({b['submitted'] for b in e0_orph})
    e0_ids = {b['id'] for b in e0_orph}
    e0_later = sorted({b['submitted'][-5:] for b in st['batches']
                       if tag_row(b['tag'], b) == 'E0' and b['id'] not in e0_ids})
    pre = [r for r in b_rows if not b_nums[r]['ledger'] and b_nums[r]['billed_usd'] > 0]
    pre_sum = b_nums[pre[-1]]['cumulative_usd'] if pre else 0.0   # pre rows come first in time order
    led = [r for r in b_rows if b_nums[r]['ledger']]
    led_other = sum(b_nums[r]['other_billed_usd'] for r in led)
    led_sum = sum(b_nums[r]['billed_usd'] for r in led)
    af = b_nums.get('AF')
    an = a_nums
    med = lambda g: f'${an[g]["median_usd"]:.2f}' if g in an else 'n/a'   # noqa: E731
    cap_txt = '; '.join(f'${c["usd"]:,.0f} ' + (f'from {c["date"]} {c["from"][-5:]} (private commit {c["commit"]}'
                        + (f', spend at decision ${c["spend_at_decision"]:.2f}' if c['spend_at_decision'] else '')
                        + ')' if c['from'] else 'from the start')
                        for c in CAPS)
    proj_txt = ''
    for r, p in proj_rows:
        ci = (f', 95% interval {p["projected_ci95_usd"][0]:.0f} to {p["projected_ci95_usd"][1]:.0f}'
              if p['projected_ci95_usd'] else '')
        proj_txt += (f'Hatched: {p["n_in_flight"]} requests of {ROW_LABEL[r]} still in flight (submitted '
                     f'{p["first_submitted"]}), projected at the mean first-attempt cost of the {p["projection_family"]} '
                     f'requests already returned (${p["projection_basis_mean_first_attempt_usd"]:.4f}, '
                     f'n = {p["projection_basis_n"]}): ~${p["projected_usd"]:.0f}{ci} from {N_BOOT} bootstrap sums, '
                     f'total ~${p["projected_cumulative_usd"]:.0f}. With redraws at the measured rate '
                     f'(${p["projection_basis_billed_per_paper_usd"]:.2f} billed per paper over all attempts, '
                     f'{p["projection_basis_papers"]} papers), the projection is ~${p["projected_with_redraws_usd"]:.0f} '
                     f'(total ~${p["projected_cumulative_with_redraws_usd"]:.0f}, diamond). The interval reflects '
                     'sampling of the few measured costs only, not differences between the measured papers and those '
                     'in flight. ')
    caption = (
        'Cost of every paid model run of the roadmap with Claude Opus 5.5 (claude-opus-5-5). Tokens are the word-piece '
        'units a language model reads and writes; cost is billed per token. Cached input is instruction text reused '
        'across requests at a reduced price. Batch requests run asynchronously at half price (Anthropic Message '
        'Batches API). A valid coding passes the format check of its task (tools/check_coding.py for inquiry and '
        'review codings, tools/check_advance.py for advance codings). '
        '(a) Cost per valid coding, one point per paper, ink tick at the median, rows in time order: E0 format test '
        '(four runs of 6 papers, codebook 1.4.0), E1 first calculation, E2 test-retest on gold papers, E3 coding with '
        'the open review discussion, E7 round 2, E1b round-1 top-up (inquiry codings, codebook 1.5.0); E11 blind '
        'advance coding (pilot 1, pilot 2, full run); E16 review coding with author-response disclosures (review '
        f'v2). Medians: E1 {med("E1")}, E1b {med("E1b")}, E7 {med("E7")}, E3 {med("E3")}, E11 full advance '
        f'{med("AF")}, E16 review v2 {med("RV")} (n = {an.get("RV", {}).get("n_valid", 0)}). The leak probes are not '
        'codings and are not drawn in (a). '
        + (f'The axis stops at ${xmax:.2f}; the one coding run at full price outside the batch API '
           f'(${edge[0][1]:.2f}) is drawn at the edge. ' if any(v > xmax for _, v in edge) else '')
        + f'(b) Cumulative spend in time order of first submission, total ${total:,.2f} recorded. Each bar is '
        'labelled with its increment and the running total; row labels give valid codings of the paper-runs submitted '
        '(papers times tags) and requests (resubmissions and retries included). Solid: valid codings; light: other billed attempts (output-'
        f'limit stops, invalid answers, redraws, canceled requests at $0), recorded only from {LEDGER_FROM} on: '
        f'${led_other:,.2f} of ${led_sum:,.2f} in those rows'
        + (f', of which ${af["other_billed_usd"]:.2f} in the full advance run' if af else '')
        + f'. The {len(pre)} earlier rows (${pre_sum:,.2f}) count valid codings only, so their increments are lower '
        'bounds (marked \u2265). '
        + (f'E0 was submitted twice ({", ".join(e0_first)}, then {", ".join(e0_later)} under the same tags and '
           f'papers); the first submission ({sum(b["n"] for b in e0_orph)} requests) has no cost record. '
           if e0_orph else '')
        + f'Dashed step line: the cap in force when each row was first submitted, {cap_txt}. '
        + (f'The ${now:,.0f} entry was committed at {CAPS[-1]["from"][-5:]}, after the last batch of the figure '
           f'(submitted {max(rows[r]["first"] for r in b_rows)[-5:]}), so it is drawn as a stub below the last row. '
           if stub else '')
        + proj_txt
        + f'(c, d) Cost per coding against prompt tokens (input plus cache) and output tokens for the {len(pts)} valid '
        f'inquiry and open-review codings of E0 to E7 and E1b ({int(bat.sum())} batch, {int((~bat).sum())} at full '
        f'price, drawn hollow); advance and review v2 codings are not drawn. Output tokens account for '
        f'{share_out:.0%} of their recorded spend. Cost is a linear function of the token counts, so Pearson r '
        'describes how tokens and cost covary across papers, not a causal driver. '
        + (f'{dup["n"]} ledger records that repeat an earlier record of the same paper, tag, batch and token usage '
           f'(${dup["usd"]:.2f}; one batch result recorded twice by two collectors, batch '
           f'{", ".join(sorted(dup["by_batch"]))}) are counted once. ' if dup['n'] else '')
        + 'Cost is token usage times the price table in tools/code_papers.py, halved for batch requests. Not counted: '
        'the full-price cache pre-warm request sent before each batch from the round-2 top-up on, which is printed '
        'at submission and not stored. '
        f'Cost record read {ps.TODAY} (state.json sha256 {sha}); file paths in the provenance fields of this file.')
    ps.save(fig, 'fig10_cost', inputs=[STATE], numbers=numbers, caption=caption)


if __name__ == '__main__':
    main()
