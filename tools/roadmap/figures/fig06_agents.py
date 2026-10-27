"""Figure 6: researchers' papers against AI agent systems on graph v0.4.2 (roadmap g14, paper figure).

Panels
  a  for each node, in graph order N..R, the share of papers whose final_paper sequence uses it against the share of
     agent systems whose loops run it (node marked "full" under loop codebook 0.1.2, averaged over the two blind
     coders), paired dots with 95% percentile bootstrap intervals (2000 resamples of papers or of agent systems,
     Python random seed 2026, as in g14)
  b  distinct nodes per workflow: median and 95% bootstrap interval, papers against agent systems
  c  edge coverage: of the researcher transitions (consecutive distinct nodes, runs merged) that occur in at least
     10% of papers, how many are run in any loop of the 31 agent systems, one bar per agent coder; agent transitions
     are read from the coded loop step sequences whatever the node mark. The three most common researcher transitions
     that no loop runs are written under the bars

Round 1 numbers are computed here, in memory, with the functions and the random-number order of
tools/roadmap/g14_papers_vs_agents.py (validate() and seq() from tools/check_coding.py, edges(), v_rule(), ci() with
random.Random(2026)), from every valid coding in private/analysis/codings/api/calc1. The stored g14 output
(derived/calc1/papers_vs_agents.json) is read only as a check: when its n_papers differs from the count of valid calc1
codings, or any cell differs from the in-memory result, the script prints a warning and records the mismatch in the
figure JSON. Rerunning g14 removes the warning; the figure does not change. Nothing under derived/ is written.

Round 2 (tag r2, papers in derived/r2calc/manifest.jsonl) is added as a second paper series when that coding folder
holds at least one valid coding, with the same rules (numpy bootstrap, seed 2026) against the same agent codings.

Inputs
  private/analysis/codings/api/calc1/*.json                               round-1 model codings (codebook 1.5.0)
  private/data/roadmap/derived/calc1/manifest.jsonl                       the 525 eligible round-1 papers
  private/analysis/reliability/codings/agents/{opus-b,sonnet-c}/*.json    agent loop codings (loop codebook 0.1.2)
  private/data/roadmap/derived/calc1/papers_vs_agents.json                stored g14 output, staleness check only
  private/analysis/codings/api/r2/*.json, derived/r2calc/manifest.jsonl   round 2, when present

Outputs  private/data/roadmap/figures/paper/fig06_agents.{pdf,png,json}
Run:     python tools/roadmap/figures/fig06_agents.py
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from matplotlib.gridspec import GridSpecFromSubplotSpec
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402

sys.path.insert(0, str(ps.ROOT / 'tools'))
from check_coding import seq, validate  # noqa: E402
import g14_papers_vs_agents as g14  # noqa: E402  (tools/roadmap is on sys.path through paperstyle)

G14 = ps.DERIVED / 'calc1' / 'papers_vs_agents.json'
API = ps.ROOT / 'private' / 'analysis' / 'codings' / 'api'
AGENTS = ps.ROOT / 'private' / 'analysis' / 'reliability' / 'codings' / 'agents'
R1_MANIFEST = ps.DERIVED / 'calc1' / 'manifest.jsonl'
R2_MANIFEST = ps.DERIVED / 'r2calc' / 'manifest.jsonl'
B, SEED = 2000, 2026
NAME = 'fig06_agents'


# ---------------------------------------------------------------- round 1, the g14 computation in memory
def load_agents():
    """Per coder, per agent system: nodes marked full, loop transitions (any mark), V kinds, codebook version (g14)."""
    coders = {}
    for d in sorted(p for p in AGENTS.iterdir() if p.is_dir()):
        sysm = {}
        for f in sorted(d.glob('*.json')):
            a = json.loads(f.read_text())
            full = {n for n in g14.NODES if a['nodes'][n]['mark'] == 'full'}
            e = set()
            for lp in a.get('loops', []):
                e |= g14.edges(lp['steps'])
            kinds = {v['kind'] for v in a.get('v_checks', []) if v.get('in_loop')}
            sysm[a['key']] = {'set': full, 'edges': e, 'kinds': kinds, 'version': a.get('codebook_version')}
        coders[d.name] = sysm
    return coders


def g14_round1(exclude=()):
    """Return what g14 main() would write today, without writing it. Same call order, so the same random draws."""
    g14.rng = random.Random(2026)
    papers, n_files = [], 0
    for f in sorted((API / 'calc1').glob('*.json')):
        n_files += 1
        c = json.loads(f.read_text())
        if validate(c) or f.stem in exclude:
            continue
        ns = seq(c, 'node')
        kinds = {v['kind'] for v in c.get('v_checks', []) if v.get('performed_here') is True}
        papers.append({'set': set(ns), 'edges': g14.edges(ns), 'kinds': kinds})
    coders = load_agents()
    keys = sorted(set.intersection(*(set(v) for v in coders.values())))
    versions = sorted({coders[c][k]['version'] for c in coders for k in keys})
    node = {}
    for n in g14.NODES:
        hum = g14.ci([int(n in p['set']) for p in papers])
        ag = [sum(int(n in coders[c][k]['set']) for c in coders) / len(coders) for k in keys]
        node[n] = {'papers': hum, 'agents': g14.ci(ag)}
    hum_edges = Counter(e for p in papers for e in p['edges'])
    ag_edges = {c: set().union(*(coders[c][k]['edges'] for k in keys)) for c in coders}
    common_h = {e for e, m in hum_edges.items() if m / len(papers) >= .10}
    edge = {'researcher_edges_in_10pct_of_papers': len(common_h),
            'of_those_run_by_any_agent': {c: len(common_h & ag_edges[c]) for c in coders},
            'agent_edges_never_in_papers': {c: sorted(''.join(e) for e in ag_edges[c] - set(hum_edges)) for c in coders},
            'top_researcher_edges_no_agent_runs': [[''.join(e), round(m / len(papers), 2)] for e, m in hum_edges.most_common()
                                                   if all(e not in ag_edges[c] for c in coders)][:10]}
    # the V-rule intervals are not drawn, but g14 draws them before the size intervals: keep the random order
    for cf in (True, False):
        hv = [g14.v_rule(p['kinds'], cf) for p in papers]
        av = {c: [g14.v_rule(coders[c][k]['kinds'], cf) for k in keys] for c in coders}
        g14.ci([int(x == 'full') for x in hv])
        g14.ci([int(x == 'partial') for x in hv])
        g14.ci([sum(av[c][i] == 'full' for c in coders) / len(coders) for i in range(len(keys))])
    g14.ci([int(len(p['kinds'] & g14.TRI) >= 2) for p in papers])
    g14.ci([sum(len(coders[c][k]['kinds'] & g14.TRI) >= 2 for c in coders) / len(coders) for k in keys])
    med = lambda xs: sorted(xs)[len(xs) // 2]  # noqa: E731
    sizes = {'papers': g14.ci([len(p['set']) for p in papers], stat=med),
             'agents': g14.ci([sum(len(coders[c][k]['set']) for c in coders) / len(coders) for k in keys], stat=med)}
    # loop steps on nodes the same coder did not mark full (they enter panel c, not panel a)
    steps = {}
    for c in coders:
        tot = nf = 0
        for f in sorted((AGENTS / c).glob('*.json')):
            a = json.loads(f.read_text())
            if a['key'] not in keys:
                continue
            for lp in a.get('loops', []):
                for s in lp['steps']:
                    tot += 1
                    nf += a['nodes'][s]['mark'] != 'full'
        steps[c] = {'steps': tot, 'not_full': nf}
    return {'n_papers': len(papers), 'n_files': n_files, 'n_agents': len(keys), 'agent_coders': list(coders),
            'loop_codebook_versions': versions, 'distinct_nodes_median': sizes, 'node_use': node, 'edges': edge,
            'loop_steps': steps}, ag_edges


def stale_check(live):
    """Compare the stored g14 output with the in-memory result; return a list of mismatches (empty when current)."""
    if not G14.is_file():
        return ['stored g14 output missing']
    g = ps.read_json(G14)
    out = []
    if g['n_papers'] != live['n_papers']:
        out.append(f"n_papers: stored {g['n_papers']}, valid calc1 codings now {live['n_papers']}")
    for n in ps.NODES:
        for side in ('papers', 'agents'):
            if g['node_use'][n][side] != live['node_use'][n][side]:
                out.append(f"node {n} {side}: stored {g['node_use'][n][side]}, now {live['node_use'][n][side]}")
    for k in ('papers', 'agents'):
        if g['distinct_nodes_median'][k] != live['distinct_nodes_median'][k]:
            out.append(f"distinct nodes {k}: stored {g['distinct_nodes_median'][k]}, now {live['distinct_nodes_median'][k]}")
    if g['edges'] != live['edges']:
        out.append('edges block differs')
    return out


# ---------------------------------------------------------------- round 2, computed with the g14 rules
def ci(vals, rng, stat=np.mean):
    """Point estimate and 95% percentile bootstrap interval over units (g14 convention, rounded to 0.01)."""
    v = np.asarray(vals, float)
    idx = rng.integers(0, len(v), size=(B, len(v)))
    bs = np.sort([stat(v[i]) for i in idx])
    return [round(float(stat(v)), 2), round(float(bs[int(.025 * B)]), 2), round(float(bs[int(.975 * B) - 1]), 2)]


def upper_median(xs):
    """g14's median: the element at index n // 2 of the sorted values."""
    return float(np.sort(xs)[len(xs) // 2])


def load_round2():
    """Valid round-2 codings in the r2calc manifest; returns (papers, files read) or (None, []) when absent."""
    d = API / 'r2'
    if not d.is_dir() or not R2_MANIFEST.is_file():
        return None, []
    keys = {json.loads(l)['key'] for l in R2_MANIFEST.read_text().splitlines() if l.strip()}
    papers = []
    for f in sorted(d.glob('*.json')):
        try:
            c = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            continue
        if validate(c) or c.get('key') not in keys:
            continue
        ns = seq(c, 'node')
        papers.append({'set': set(ns), 'edges': g14.edges(ns)})
    return (papers or None), [d, R2_MANIFEST]


def round2_side(papers, ag_edges):
    rng = np.random.default_rng(SEED)
    node = {n: ci([int(n in p['set']) for p in papers], rng) for n in ps.NODES}
    size = ci([len(p['set']) for p in papers], rng, stat=upper_median)
    hum = Counter(e for p in papers for e in p['edges'])
    common = {e for e, m in hum.items() if m / len(papers) >= .10}
    cover = {c: len(common & ag_edges[c]) for c in ag_edges}
    top = [[''.join(e), round(m / len(papers), 2)] for e, m in hum.most_common()
           if all(e not in ag_edges[c] for c in ag_edges)][:3]
    return {'n': len(papers), 'node': node, 'size': size, 'common': len(common), 'cover': cover, 'top': top}


# ---------------------------------------------------------------- drawing
def errdot(ax, x, y, lo, hi, color, marker='o', filled=True, size=3.6):
    ax.errorbar([x], [y], xerr=[[x - lo], [hi - x]], fmt=marker, color=color, ms=size, mew=0.8, elinewidth=0.8,
                capsize=0, zorder=3, mfc=color if filled else 'white', mec=color)


def arrow(e):
    return e[0] + r'$\rightarrow$' + e[1]   # mathtext arrow: Helvetica has no U+2192 glyph


def slug(lab):
    return lab.lower().replace(', ', '_').replace(' ', '_')


def main():
    g, ag_e = g14_round1()
    n1, na = g['n_papers'], g['n_agents']
    n_elig = sum(1 for l in R1_MANIFEST.read_text().splitlines() if l.strip())
    coders = list(g['agent_coders'])
    stale = stale_check(g)
    if stale:
        print('WARNING: stored g14 output is stale; the figure uses the in-memory g14 computation. '
              'Rerun tools/roadmap/g14_papers_vs_agents.py to refresh it.\n  ' + '\n  '.join(stale), file=sys.stderr)
    inputs = [API / 'calc1', R1_MANIFEST] + [AGENTS / c for c in coders] + ([G14] if G14.is_file() else [])
    numbers = {'n_papers_round1': n1, 'n_calc1_coding_files': g['n_files'], 'n_eligible_round1': n_elig,
               'n_agent_systems': na, 'agent_coders': coders, 'loop_codebook_versions': g['loop_codebook_versions'],
               'agent_node_mark_panel_a': 'full, averaged over coders',
               'agent_loop_steps_panel_c': g['loop_steps'],
               'round1_source': 'in-memory g14 computation (tools/roadmap/g14_papers_vs_agents.py functions, seed 2026)',
               'stored_g14_check': stale or 'stored papers_vs_agents.json matches'}

    r2papers, r2files = load_round2()
    r2 = None
    if r2papers:
        r2 = round2_side(r2papers, ag_e)
        inputs += r2files
    numbers['rounds_drawn'] = ['round 1'] + (['round 2'] if r2 else [])

    # paper series: (label, colour, filled, node cells, size cell, n)
    series = [('Papers' + (', round 1' if r2 else ''), ps.BLUE, True,
               {n: g['node_use'][n]['papers'] for n in ps.NODES}, g['distinct_nodes_median']['papers'], n1)]
    if r2:
        series.append(('Papers, round 2', ps.BLUE, False, r2['node'], r2['size'], r2['n']))
    agent = ('Agent systems', ps.ORANGE, True, {n: g['node_use'][n]['agents'] for n in ps.NODES},
             g['distinct_nodes_median']['agents'], na)
    allser = series + [agent]

    ps.setup()
    fig = ps.plt.figure(figsize=(ps.DOUBLE, 3.25))
    outer = fig.add_gridspec(1, 2, width_ratios=[1.2, 1], wspace=0.42, left=0.14, right=0.985, top=0.9, bottom=0.17)
    axa = fig.add_subplot(outer[0])
    right = GridSpecFromSubplotSpec(2, 1, subplot_spec=outer[1], height_ratios=[0.55 + 0.25 * len(series), 1.0 + 0.5 * len(series)],
                                    hspace=0.95)
    axb = fig.add_subplot(right[0])
    axc = fig.add_subplot(right[1])

    # ---- (a) node use, graph order top to bottom
    k = len(allser)
    offs = np.linspace(-0.2, 0.2, k) if k > 2 else np.array([-0.16, 0.16])
    for i, n in enumerate(ps.NODES):
        for (lab, col, fill, cells, _, _), dy in zip(allser, offs):
            e, lo, hi = (100 * v for v in cells[n])
            errdot(axa, e, i + dy, lo, hi, col, filled=fill)
    axa.set_yticks(range(len(ps.NODES)))
    axa.set_yticklabels([f'{n}  {ps.NODE_NAMES[n]}' for n in ps.NODES])
    axa.set_ylim(len(ps.NODES) - 0.45, -0.55)
    axa.set_xlim(-2, 102)
    axa.set_xticks([0, 25, 50, 75, 100])
    axa.set_xlabel('Share of papers or agent systems using the node (%)')
    ps.grid(axa, 'x')
    axa.tick_params(axis='y', length=0)
    handles = [Line2D([], [], marker='o', ls='', color=col, mfc=col if fill else 'white', mec=col, ms=3.6, mew=0.8,
                      label=f'{lab} (n = {nn})') for lab, col, fill, _, _, nn in allser]
    axa.legend(handles=handles, loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2 if k > 2 else k, handletextpad=0.3,
               columnspacing=1.2, borderaxespad=0.2)
    for lab, _, _, cells, _, _ in allser:
        numbers[f'node_share_{slug(lab)}'] = {n: cells[n] for n in ps.NODES}
    numbers['node_share_gap_papers_minus_agents_r1'] = {
        n: round(g['node_use'][n]['papers'][0] - g['node_use'][n]['agents'][0], 2) for n in ps.NODES}

    # ---- (b) distinct nodes per workflow
    for j, (lab, col, fill, _, size, nn) in enumerate(allser):
        e, lo, hi = size
        errdot(axb, e, j, lo, hi, col, filled=fill, size=4.2)
        axb.text(hi + 0.4, j, f'{e:g} [{lo:g}–{hi:g}]', va='center', ha='left', fontsize=ps.SMALL, color=ps.INK)
        numbers[f'distinct_nodes_median_{slug(lab)}'] = size
    axb.set_yticks(range(len(allser)))
    axb.set_yticklabels([lab for lab, *_ in allser])
    axb.set_ylim(len(allser) - 0.4, -0.6)
    axb.set_xlim(0, 15)
    axb.set_xticks([0, 3, 6, 9, 12, 15])
    axb.set_xlabel('Distinct nodes per workflow (of 15), median')
    axb.tick_params(axis='y', length=0)
    ps.grid(axb, 'x')

    # ---- (c) edge coverage: researcher transitions in >= 10% of papers run in any agent loop, per coder
    rows = [('round 1', g['edges']['researcher_edges_in_10pct_of_papers'], g['edges']['of_those_run_by_any_agent'])]
    if r2:
        rows.append(('round 2', r2['common'], r2['cover']))
    bars = []
    for rname, tot, cov in rows:
        for c in coders:
            bars.append((f'Coder {c}' + (f', {rname}' if r2 else ''), tot, cov[c]))
    for j, (lab, tot, cv) in enumerate(bars):
        axc.barh(j, cv, height=0.62, color=ps.ORANGE, edgecolor='white', linewidth=0.6, zorder=2)
        axc.barh(j, tot - cv, left=cv, height=0.62, color=ps.NEUTRAL, edgecolor='white', linewidth=0.6, zorder=2)
        axc.text(tot + 1.8, j, f'{cv} of {tot} ({100 * cv / tot:.0f}%)', va='center', ha='left', fontsize=ps.SMALL, color=ps.INK)
    axc.set_yticks(range(len(bars)))
    axc.set_yticklabels([b[0] for b in bars])
    axc.set_ylim(len(bars) - 0.4, -0.6)
    xmax = max(t for _, t, _ in bars)
    xtop = int(np.ceil(xmax / 10) * 10)
    axc.set_xlim(0, xmax * 1.45)
    axc.set_xticks(range(0, xtop + 1, 10))
    axc.spines['bottom'].set_bounds(0, xtop)     # the axis ends at the last tick; the space to its right holds the labels
    axc.set_xlabel('Researcher transitions in ≥ 10% of papers', x=xtop / (xmax * 1.45) / 2)
    axc.tick_params(axis='y', length=0)
    ps.grid(axc, 'x')
    leg = [ps.plt.Rectangle((0, 0), 1, 1, color=ps.ORANGE, label='run in any agent loop'),
           ps.plt.Rectangle((0, 0), 1, 1, color=ps.NEUTRAL, label='run in none')]
    axc.legend(handles=leg, loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, handlelength=1.0,
               handletextpad=0.4, columnspacing=1.0, borderaxespad=0.2)
    top = g['edges']['top_researcher_edges_no_agent_runs'][:3]
    note = ('Most common transitions no loop runs' + (' (round 1)' if r2 else '') + ':\n'
            + ', '.join(f'{arrow(e)} ({100 * s:.0f}%{" of papers" if i == 0 else ""})' for i, (e, s) in enumerate(top)))
    axc.annotate(note, xy=(0, 0), xycoords='axes fraction', xytext=(0, -27), textcoords='offset points',
                 fontsize=ps.SMALL, color=ps.INK2, va='top', ha='left', linespacing=1.4)
    numbers['edges_round1'] = {'researcher_edges_in_10pct_of_papers': rows[0][1], 'run_by_any_agent': rows[0][2],
                               'top3_no_agent_runs': top,
                               'agent_edges_never_in_papers': g['edges']['agent_edges_never_in_papers']}
    if r2:
        numbers['edges_round2'] = {'researcher_edges_in_10pct_of_papers': r2['common'], 'run_by_any_agent': r2['cover'],
                                   'top3_no_agent_runs': r2['top']}
        numbers['n_papers_round2'] = r2['n']

    # ---- panel labels in figure coordinates: (a) at the left edge of the canvas, (b) and (c) in the gutter
    def label(ax, letter, x, dy=0.012):
        fig.text(x, ax.get_position().y1 + dy, f'({letter})', fontsize=ps.LABEL, fontweight='bold', va='bottom', ha='left')
    label(axa, 'a', 0.004, dy=0.0)
    xb = axb.get_position().x0 - 0.155
    label(axb, 'b', xb)
    label(axc, 'c', xb)

    # ---- caption
    nu = g['node_use']
    gap = {n: nu[n]['papers'][0] - nu[n]['agents'][0] for n in ps.NODES}
    big = sorted(ps.NODES, key=lambda n: -gap[n])[:4]
    gaps = ', '.join(f"{n} {ps.NODE_NAMES[n].lower()} ({100 * nu[n]['papers'][0]:.0f}% of papers against "
                     f"{100 * nu[n]['agents'][0]:.0f}% of agent systems)" for n in big)
    hi_ag = [n for n in ps.NODES if nu[n]['agents'][0] > nu[n]['papers'][0]]
    more = ('only ' if len(hi_ag) == 1 else 'nodes ') if hi_ag else 'no node is used more often by agent systems'
    if hi_ag:
        more += ', '.join(f"{n} ({100 * nu[n]['agents'][0]:.0f}% of agent systems against {100 * nu[n]['papers'][0]:.0f}% "
                          f"of papers)" for n in hi_ag) + (' has' if len(hi_ag) == 1 else ' have') + \
            ' the higher estimate among agent systems'
        if any(nu[n]['agents'][1] <= nu[n]['papers'][2] for n in hi_ag):
            more += ', with overlapping intervals'
    zero = [f"{n} among {'papers' if side == 'papers' else 'agent systems'} ({100 * c[0]:.0f}%, [{100 * c[1]:.0f}, {100 * c[2]:.0f}])"
            for n in ps.NODES for side in ('papers', 'agents') for c in [nu[n][side]] if c[1] == c[2]]
    sp, sa = g['distinct_nodes_median']['papers'], g['distinct_nodes_median']['agents']
    st = g['loop_steps']
    cov = rows[0][2]
    cap = (f"Researchers' papers against AI agent systems on the inquiry graph (graph v0.4.2). "
           f"Papers are the {n1} of {n_elig} eligible round-1 papers (2022) with full text and a valid coding "
           f"({g['n_files']} were coded; the sample is set by full-text access, not drawn at random), coded by "
           f"claude-opus-5-5 under codebook 1.5.0. Agent systems are {na} systems coded blind by two model coders "
           f"({', '.join(coders)}) under loop codebook {', '.join(g['loop_codebook_versions'])}. "
           f"(a) Share of papers whose coded final-paper workflow uses each node at least once (blue) and share of agent "
           f"systems whose loops run it (orange; a node counts when marked full, and the share is the mean of the two "
           f"coders). Nodes in graph order. Horizontal lines in (a) and (b) are 95% percentile bootstrap intervals "
           f"(2000 resamples of papers or of agent systems, seed 2026)"
           + (f"; the intervals for {' and '.join(zero)} have zero width and are not visible" if zero else '') + ". "
           f"The four largest gaps, papers minus agent systems, are at {gaps}; {more}. "
           f"(b) Distinct nodes per workflow, median [95% interval]: papers {sp[0]:g} [{sp[1]:g}, {sp[2]:g}], agent systems "
           f"{sa[0]:g} [{sa[1]:g}, {sa[2]:g}] (coder mean per system, hence half values). "
           f"(c) Of the {rows[0][1]} researcher transitions (consecutive distinct nodes) found in at least 10% of papers, "
           f"the number run in any loop of the {na} agent systems, per coder ({', '.join(f'{c}: {cov[c]}' for c in coders)}); "
           f"the three most common transitions no loop runs are listed. Agent transitions are read from the coded loop "
           f"step sequences, including steps on nodes not marked full ("
           + ', '.join(f"{st[c]['not_full']} of {st[c]['steps']} loop steps for {c}" for c in coders)
           + "), so (c) counts more agent nodes than (a). "
           f"Source: private/analysis/codings/api/calc1 and the agent codings, aggregated with the functions of "
           f"tools/roadmap/g14_papers_vs_agents.py (stored output private/data/roadmap/derived/calc1/papers_vs_agents.json).")
    if r2:
        cap += (f" Round 2 papers (open blue circles, n = {r2['n']}) were computed here from the r2 codings with the "
                f"g14 rules against the same agent codings.")
    else:
        cap += " Round 2 codings were not available at the figure date."
    ps.save(fig, NAME, inputs=inputs, numbers=numbers, caption=cap)


if __name__ == '__main__':
    main()
