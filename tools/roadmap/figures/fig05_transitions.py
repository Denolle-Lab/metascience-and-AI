"""Figure 5: node-to-node transitions in the coded final-paper sequences (graph v0.4.2, codebook 1.5.0).

Panels
  a  15 x 15 heatmap, row = node a step leaves, column = node the next step enters, nodes in graph order N..R. Each cell
     is the share of round-1 papers whose final_paper sequence contains that directed transition at least once.
     Sequences are run-collapsed first (tools/check_coding.py seq(), as in g13, g14 and g17), so a node followed by itself
     is not a transition and the diagonal is drawn empty and hatched. Cells never seen are left white with a hairline
     grey outline, so zero reads as data. All values are in percent of papers; cell text is written only for the 12
     transitions ranked in panel b.
  b  the 12 most common transitions, ranked by share of round-1 papers, with 95% percentile bootstrap intervals
     (2000 resamples over papers, seed 2026). Fill says whether any of the 31 coded AI agent systems runs that
     transition inside one of its loops, as read by the two blind loop coders opus-b and sonnet-c (loop codebook
     version read from the files): filled = both coders find it in at least one system, hatched = one coder only,
     hollow = no agent loop runs it. The column at right gives how many of the 31 systems run it, per coder.
     Agent edges are built exactly as in tools/roadmap/g14_papers_vs_agents.py (consecutive loop steps, a != b).

Rounds: round 1 is always drawn (tag calc1). Round 2 (tag r2, papers in derived/r2calc/manifest.jsonl) is added to
panel b as a second series (diamond with interval) when that coding folder holds at least one valid coding; the
heatmap stays round 1. Codings that fail tools/check_coding.py validate() are left out, as in g13, g14 and g17.

Inputs
  private/analysis/codings/api/calc1/*.json                      round-1 model codings (claude-opus-5-5, Batch API)
  private/analysis/codings/api/r2/*.json                         round-2 model codings, when present
  private/data/roadmap/derived/calc1/manifest.jsonl              the 525 eligible round-1 papers
  private/data/roadmap/derived/r2calc/manifest.jsonl             the 222 eligible round-2 papers
  private/analysis/reliability/codings/agents/{opus-b,sonnet-c}  the 31 agent systems, loop codings
  private/data/roadmap/derived/calc1/papers_vs_agents.json       g14, read only to cross-check the no-agent edges

Outputs  private/data/roadmap/figures/paper/fig05_transitions.{pdf,png,json}
Run:     python tools/roadmap/figures/fig05_transitions.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402

sys.path.insert(0, str(ps.ROOT / 'tools'))
from check_coding import seq, validate  # noqa: E402

API = ps.PRIVATE / 'analysis' / 'codings' / 'api'
AG = ps.PRIVATE / 'analysis' / 'reliability' / 'codings' / 'agents'
G14 = ps.DERIVED / 'calc1' / 'papers_vs_agents.json'
ROUNDS = [('Round 1', 'calc1', ps.DERIVED / 'calc1' / 'manifest.jsonl'),
          ('Round 2', 'r2', ps.DERIVED / 'r2calc' / 'manifest.jsonl')]
NODES = ps.NODES
IDX = {n: i for i, n in enumerate(NODES)}
TOP = 12
B, SEED = 2000, 2026
ARROW = r'$\rightarrow$'           # mathtext arrow; Helvetica has no U+2192
DIAG_FACE = '#f0efec'
INSET = 0.06                       # outline of never-observed cells sits this far inside the white gap (data units)
# panel b fill by how many of the two loop coders find the edge in at least one agent system
BAR_STYLE = {2: dict(facecolor=ps.BLUE, edgecolor=ps.BLUE, linewidth=0.7),
             1: dict(facecolor='white', edgecolor=ps.BLUE, linewidth=0.7, hatch='//////'),
             0: dict(facecolor='white', edgecolor=ps.BLUE, linewidth=0.7)}


def load_round(tag, manifest):
    """Run-collapsed final_paper edge sets of the valid codings in api/<tag> that belong to the round's manifest."""
    folder = API / tag
    if not folder.is_dir():
        return None
    keys = {json.loads(l)['key'] for l in manifest.read_text().splitlines() if l.strip()} if manifest.is_file() else None
    papers, invalid, outside, raw_self, merged = [], [], [], Counter(), 0
    files = sorted(folder.glob('*.json'))
    for f in files:
        c = json.loads(f.read_text())
        if validate(c):
            invalid.append(f.stem)
            continue
        if keys is not None and f.stem not in keys:
            outside.append(f.stem)
            continue
        ns = seq(c, 'node')
        papers.append({(a, b) for a, b in zip(ns, ns[1:])})
        steps = [st['node'] for st in next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps']]
        rep = {a for a, b in zip(steps, steps[1:]) if a == b}
        raw_self.update(rep)
        merged += bool(rep)
    if not papers:
        return None
    return {'papers': papers, 'invalid': invalid, 'outside_manifest': outside, 'raw_self': raw_self, 'merged': merged,
            'files': folder, 'n_files': len(files), 'n_eligible': len(keys) if keys is not None else None}


def agent_edges():
    """Per coder: Counter of directed edges over the 31 systems (a system counts once per edge)."""
    out = {}
    for d in sorted(p for p in AG.iterdir() if p.is_dir()):
        cnt, n, ver = Counter(), 0, set()
        for f in sorted(d.glob('*.json')):
            a = json.loads(f.read_text())
            e = set()
            for lp in a.get('loops', []):
                e |= {(x, y) for x, y in zip(lp['steps'], lp['steps'][1:]) if x != y}
            cnt.update(e)
            n += 1
            ver.add(a.get('codebook_version'))
        out[d.name] = {'edges': cnt, 'n_systems': n, 'versions': ver}
    return out


def boot(ind, rng):
    """ind: papers x edges 0/1 matrix -> (share, lo, hi) per edge, percentile bootstrap over papers."""
    n = ind.shape[0]
    idx = rng.integers(0, n, size=(B, n))
    bs = ind[idx].mean(axis=1)
    return ind.mean(axis=0), np.percentile(bs, 2.5, axis=0), np.percentile(bs, 97.5, axis=0)


def main():
    rng = np.random.default_rng(SEED)
    rounds = {}
    for label, tag, man in ROUNDS:
        r = load_round(tag, man)
        if r is not None:
            rounds[label] = r | {'tag': tag, 'manifest': man}
    r1 = rounds['Round 1']
    n1 = len(r1['papers'])
    cnt = Counter(e for p in r1['papers'] for e in p)
    M = np.zeros((len(NODES), len(NODES)))
    for (a, b), m in cnt.items():
        M[IDX[a], IDX[b]] = m / n1
    ranked = [e for e, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], IDX[kv[0][0]], IDX[kv[0][1]]))]
    top = ranked[:TOP]

    ag = agent_edges()
    coders = list(ag)
    n_sys = {c: ag[c]['n_systems'] for c in coders}
    lv = sorted({str(v) for c in coders for v in ag[c]['versions']})
    runs = {e: {c: ag[c]['edges'][e] for c in coders} for e in top}
    any_agent = {e: any(v > 0 for v in runs[e].values()) for e in top}
    n_coders = {e: sum(v > 0 for v in runs[e].values()) for e in top}      # 0 none, 1 one coder, 2 both

    # bootstrap intervals for the ranked edges, per round
    stats = {}
    for label, r in rounds.items():
        ind = np.array([[int(e in p) for e in top] for p in r['papers']], dtype=float)
        stats[label] = boot(ind, rng)

    # ---------------------------------------------------------------- figure
    W, H = ps.DOUBLE, 3.72
    fig = ps.plt.figure(figsize=(W, H))
    ps.setup()

    def axes_in(x, y, w, h):
        """Axes placed in inches from the lower left corner of the figure."""
        return fig.add_axes([x / W, y / H, w / W, h / H])

    side, base = 2.62, 0.74
    ax = axes_in(0.98, base, side, side)
    cax = axes_in(0.98, 0.50, 1.45, 0.07)
    bx = axes_in(4.90, base, 1.50, side)

    # (a) heatmap
    cmap = LinearSegmentedColormap.from_list('seq', ps.SEQ)
    P = 100 * M                                           # percent of papers, the unit of the whole figure
    vmax = 60
    shown = np.ma.masked_where(P == 0, P)
    im = ax.imshow(shown, cmap=cmap, vmin=0, vmax=vmax, aspect='equal', interpolation='nearest')
    ax.set_facecolor('white')
    diag = dict(facecolor=DIAG_FACE, edgecolor=ps.NEUTRAL, hatch='//////', linewidth=0)
    for i in range(len(NODES)):
        ax.add_patch(Rectangle((i - .5, i - .5), 1, 1, zorder=2, **diag))
    for i in range(len(NODES)):                          # never observed: hairline grey outline inside the white gaps
        for j in range(len(NODES)):
            if i != j and P[i, j] == 0:
                ax.add_patch(Rectangle((j - .5 + INSET, i - .5 + INSET), 1 - 2 * INSET, 1 - 2 * INSET, facecolor='white',
                                       edgecolor=ps.NEUTRAL, linewidth=0.3, zorder=3.5))
    for k in range(len(NODES) + 1):                      # white gaps between cells
        ax.axhline(k - .5, color='white', lw=0.6, zorder=3)
        ax.axvline(k - .5, color='white', lw=0.6, zorder=3)
    ax.set_xticks(range(len(NODES)), NODES)
    ax.set_yticks(range(len(NODES)), [f'{ps.NODE_NAMES[n]}  {n}' for n in NODES])
    ax.tick_params(length=0, pad=2)
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('To node (next step)', labelpad=3)
    ax.set_ylabel('From node', labelpad=3)
    for sp in ax.spines.values():
        sp.set_visible(False)
    for e in top:
        i, j = IDX[e[0]], IDX[e[1]]
        v = P[i, j]
        ax.text(j, i, f'{v:.0f}', ha='center', va='center', fontsize=ps.SMALL,
                color='white' if v / vmax > 0.55 else ps.INK, zorder=4)
    ps.panel(ax, 'a', x=-0.36, y=1.07)

    cb = fig.colorbar(im, cax=cax, orientation='horizontal')
    cb.set_label('Share of papers (%)', labelpad=2)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=2, width=0.5, pad=1.5)
    cb.set_ticks(range(0, vmax + 1, 10))
    key = [Patch(label='Same node (merged)', **diag),
           Patch(facecolor='white', edgecolor=ps.NEUTRAL, linewidth=0.3, label='Never observed (0)')]
    fig.legend(handles=key, loc='upper left', bbox_to_anchor=(2.62 / W, 0.62 / H), handlelength=1.2,
               handleheight=1.0, borderaxespad=0, labelspacing=0.35, handletextpad=0.4)

    # (b) ranked bars
    y = np.arange(TOP)
    s, lo, hi = (100 * v for v in stats['Round 1'])
    two = len(rounds) > 1
    for k, e in enumerate(top):
        bx.barh(y[k], s[k], height=0.62, zorder=2, **BAR_STYLE[n_coders[e]])
    bx.errorbar(s, y, xerr=[s - lo, hi - s], fmt='none', ecolor=ps.INK, elinewidth=0.6, capsize=0, zorder=3)
    if two:
        s2, lo2, hi2 = (100 * v for v in stats['Round 2'])
        bx.errorbar(s2, y, xerr=[s2 - lo2, hi2 - s2], fmt='D', ms=2.6, mfc=ps.ORANGE, mec='white', mew=0.4,
                    ecolor=ps.ORANGE, elinewidth=0.6, capsize=0, zorder=4)
    bx.set_yticks(y, [f'{ps.NODE_NAMES[e[0]]} ({e[0]}) {ARROW}\n{ps.NODE_NAMES[e[1]]} ({e[1]})' for e in top])
    bx.set_ylim(TOP - 0.5, -0.5)
    bx.tick_params(axis='y', length=0, pad=2)
    for t in bx.get_yticklabels():
        t.set_linespacing(1.0)
    bx.set_xlim(0, 70)
    bx.set_xticks(range(0, 71, 10))
    bx.set_xlabel('Share of papers with the transition (%)')
    bx.spines['left'].set_visible(False)
    ps.grid(bx, 'x')
    tr = bx.get_yaxis_transform()
    cx = 1.0 + 0.27 / 1.50                                # centre of the count column, 0.27 in right of the axes
    bx.text(cx, -0.55, f'Agents (of {n_sys[coders[0]]})\n' + ' / '.join(coders),
            transform=tr, ha='center', va='bottom', fontsize=ps.SMALL, color=ps.INK2, linespacing=1.05)
    for k, e in enumerate(top):
        bx.text(cx, y[k], ' / '.join(str(runs[e][c]) for c in coders), transform=tr, ha='center', va='center',
                fontsize=ps.SMALL, color=ps.INK)
    handles = [Patch(**BAR_STYLE[2], label='Agent loop, both coders'),
               Patch(**BAR_STYLE[1], label='Agent loop, one coder only'),
               Patch(**BAR_STYLE[0], label='No agent loop'),
               Line2D([], [], color=ps.INK, lw=0.6, label='95% interval')]
    if two:
        handles.append(Line2D([], [], marker='D', ls='none', ms=2.6, mfc=ps.ORANGE, mec='white', mew=0.4,
                              label=f'Round 2 (n = {len(rounds["Round 2"]["papers"])})'))
    bx.legend(handles=handles, loc='upper left', bbox_to_anchor=(-0.75, -0.115), ncol=2, handlelength=1.2,
              handleheight=0.8, borderaxespad=0, columnspacing=1.0, labelspacing=0.3,
              title=f'Round 1 papers, n = {n1}', title_fontsize=ps.SMALL, alignment='left')
    ps.panel(bx, 'b', x=-0.78, y=1.07)

    # ---------------------------------------------------------------- numbers, cross-check, save
    g14 = ps.read_json(G14)
    g14_no_agent = {e: v for e, v in g14['edges']['top_researcher_edges_no_agent_runs']}
    pct = lambda v: round(100 * float(v), 2)                                    # noqa: E731
    one_coder = [e for e in top if n_coders[e] == 1]
    n_white = int(sum(P[i, j] == 0 for i in range(len(NODES)) for j in range(len(NODES)) if i != j))
    numbers = {
        'unit': 'percent of papers (heatmap cells, colour bar, panel b bars and intervals)',
        'rounds_drawn': list(rounds),
        'n_papers': {k: len(r['papers']) for k, r in rounds.items()},
        'n_eligible_in_manifest': {k: r['n_eligible'] for k, r in rounds.items()},
        'n_coding_files': {k: r['n_files'] for k, r in rounds.items()},
        'invalid_codings_left_out': {k: r['invalid'] for k, r in rounds.items()},
        'codings_outside_manifest_left_out': {k: r['outside_manifest'] for k, r in rounds.items()},
        'n_agent_systems': n_sys, 'agent_coders': coders,
        'n_distinct_transitions_round1': len(cnt),
        'n_never_observed_offdiagonal_round1': n_white,
        'n_transitions_in_10pct_of_papers_round1': sum(m / n1 >= .10 for m in cnt.values()),
        'heatmap_vmax_pct': vmax,
        'heatmap_round1_pct': {f'{a}{b}': round(P[IDX[a], IDX[b]], 2) for a in NODES for b in NODES if P[IDX[a], IDX[b]] > 0},
        'top_transitions': [{'edge': f'{e[0]}{e[1]}', 'papers_round1': cnt[e],
                             **{f'pct_{k.replace(" ", "").lower()}_est_lo_hi': [pct(stats[k][0][i]), pct(stats[k][1][i]),
                                                                                 pct(stats[k][2][i])] for k in rounds},
                             'agent_systems_running_it': runs[e], 'coders_finding_it': n_coders[e],
                             'g14_no_agent_share': g14_no_agent.get(f'{e[0]}{e[1]}')} for i, e in enumerate(top)],
        'edges_one_coder_only': [f'{e[0]}{e[1]}' for e in one_coder],
        'papers_with_merged_repeats_round1': r1['merged'],
        'papers_with_merged_repeats_round1_pct': pct(r1['merged'] / n1),
        'loop_codebook_versions': lv,
        'raw_self_repeat_papers_round1': {n: r1['raw_self'][n] for n in NODES if r1['raw_self'][n]},
        'bootstrap': {'resamples': B, 'seed': SEED, 'interval': '2.5 and 97.5 percentiles'},
        'g14_n_papers': g14['n_papers'],
        'g14_note': (f'g14 (papers_vs_agents.json) shares are on n = {g14["n_papers"]}, this figure on n = {n1}; '
                     'the no-agent edge set is checked, the shares differ slightly. Rerun g14 before citing both.'),
    }
    no_ag = [f'{e[0]} to {e[1]}' for e in top if n_coders[e] == 0]
    one_txt = '; '.join(f'{e[0]} to {e[1]}, ' + ', '.join(f'{c} {runs[e][c]}' for c in coders) for e in one_coder)
    out_txt = (f'; {len(r1["outside_manifest"])} codings outside the manifest left out' if r1['outside_manifest'] else '')
    caption = (f'Node-to-node transitions in the coded final-paper sequences of {n1} round-1 papers with valid codings '
               f'({r1["n_files"] - len(r1["outside_manifest"])} of the {r1["n_eligible"]} eligible papers coded so far; '
               f'{len(r1["invalid"])} codings failing the format check left out{out_txt}). Papers are from 2022 Earth '
               'science, coded by Claude Opus 5.5 with codebook 1.5.0 on graph v0.4.2. Consecutive steps on the same node '
               f'are merged first, which affects {r1["merged"]} of {n1} papers ({100 * r1["merged"] / n1:.0f}%). All values '
               'are percent of papers. (a) Share of papers whose sequence contains each directed transition at least '
               'once, row node to column node in graph order. The hatched diagonal is empty by construction (repeats on '
               'one node are merged); white cells are transitions that never occur '
               f'({len(cnt)} of 210 possible transitions occur at least once, {n_white} never). Numbered cells are the '
               f'{TOP} transitions ranked in (b). (b) The {TOP} most common transitions with 95% percentile bootstrap '
               f'intervals ({B} resamples over papers). Fill gives whether any of {n_sys[coders[0]]} coded AI agent '
               f'systems runs the transition inside a loop (the cycle of steps the system repeats), as read by two model coders '
               f'that did not see each other\'s work, a Claude Opus run (opus-b) and a Claude Sonnet run (sonnet-c), '
               f'under loop codebook {", ".join(lv)}: filled, both coders; hatched, one coder only'
               + (f' (the coders disagree on {one_txt})' if one_coder else '')
               + f'; hollow, no agent loop ({", ".join(no_ag)}). Right column: number of agent systems running the '
               f'transition, {coders[0]} / {coders[1]}.'
               + (f' Diamonds: round 2 ({len(rounds["Round 2"]["papers"])} papers).' if two else ''))
    inputs = [r['files'] for r in rounds.values()] + [r['manifest'] for r in rounds.values()] + \
             [AG / c for c in coders] + [G14]
    ps.save(fig, 'fig05_transitions', inputs=inputs, numbers=numbers, caption=caption)
    print('top:', [(f'{e[0]}{e[1]}', cnt[e], round(cnt[e] / n1, 3), runs[e]) for e in top])


if __name__ == '__main__':
    main()
