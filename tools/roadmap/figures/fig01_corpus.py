"""Figure 1: how the corpus was built, round by round, and why papers left it at screening.

Panel a  stage counts per round as horizontal bars. Round 1: preselected 600 -> eligible -> full text -> submitted for
         coding -> coded. Round 2: drawn -> eligible -> full text -> submitted -> coded. Both rounds come from the same
         2022 OpenAlex candidate pool (given as a number above the bars, since it is about 25 times the largest bar) and
         do not overlap. The label at each bar end is the count and its share of the stage above, except on the
         submitted bar: full text keeps growing after a batch is sent, so that share would mix timing with failure.
Panel b  papers excluded at the double-blind eligibility screen, by category, as a share of the papers screened in
         each round; the count sits at each bar end, with the round named on the first group.

Definitions
  full text  the paper's key is in private/download-queue.json with status "have" (a PDF is on disk; XML, where
             present, comes on top of a PDF for every eligible paper, so it is not counted separately). The queue is
             read once; its read time, mtime and full sha256 go into the numbers and the caption, because a re-fetch
             (tools/fetch_pdfs.py) may still be writing it.
  submitted  a manifest key sent to the Batch API under the round's tag: union of the keys of
             private/analysis/codings/api/state.json batches[tag] and of the done and failed entries for that tag.
  coded      a coding file private/analysis/codings/api/<tag>/<key>.json for a key in the round's manifest that
             passes tools/check_coding.py validate() (schema plus codebook rules); tag calc1 for round 1, r2 for
             round 2. Round 2 is drawn when derived/r2 exists; its coded bar appears once the r2 folder holds codings.
  failed     state.json failed entries for the tag. An entry also listed in done was resubmitted and passed; it is
             counted as resolved, not as failing. Files that fail validate() are counted from the files themselves.

Inputs
  private/data/roadmap/derived/gold/pool.json           2022 candidate pool (g02_pool.py)
  private/data/roadmap/derived/gold/preselect.json      round 1 preselection, 600 (g03_preselect.py, seed 2026)
  private/data/roadmap/derived/gold/eligibility.json    round 1 screen (g07_eligibility.py)
  private/data/roadmap/derived/calc1/manifest.jsonl     round 1 eligible corpus (g12_calc1_manifest.py)
  private/data/roadmap/derived/r2/preselect.json        round 2 draw (g18_round2_draw.py, seed 2027 by default; the
                                                        file's provenance params are empty), if present
  private/data/roadmap/derived/r2/eligibility.json      round 2 screen, if present
  private/data/roadmap/derived/r2calc/manifest.jsonl    round 2 eligible corpus, if present
  private/download-queue.json                           full-text status per key (read as it is at run time)
  private/analysis/codings/api/state.json               batches, done and failed per tag
  private/analysis/codings/api/{calc1,r2}/*.json        codings

Outputs  private/data/roadmap/figures/paper/fig01_corpus.{pdf,png,json}
Run:     python tools/roadmap/figures/fig01_corpus.py
"""
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperstyle as ps  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402
from matplotlib.ticker import MultipleLocator  # noqa: E402
from check_coding import validate  # noqa: E402  (tools/ is on sys.path via common)

D = ps.DERIVED
QUEUE = ps.PRIVATE / 'download-queue.json'
CODINGS = ps.PRIVATE / 'analysis' / 'codings' / 'api'
STATE = CODINGS / 'state.json'
ROUNDS = [  # name, short, set folder, calc folder, coding tag, first-stage label, colour
    ('Round 1', 'R1', 'gold', 'calc1', 'calc1', 'Preselected', ps.BLUE),
    ('Round 2', 'R2', 'r2', 'r2calc', 'r2', 'Drawn', ps.ORANGE),
]
CATEGORY = {'off_topic': 'Off topic', 'review_or_overview': 'Review or overview',
            'comment_reply_or_editorial': 'Comment, reply\nor editorial', 'other_non_research': 'Other\nnon-research'}


def manifest(path):
    return [json.loads(line)['key'] for line in path.read_text().splitlines() if line.strip()]


def coded(tag, keys):
    """Keys of the manifest with a coding that passes validate(); also the keys whose file fails it."""
    folder = CODINGS / tag
    good, bad = [], []
    if not folder.is_dir():
        return good, bad, False
    keyset = set(keys)
    for f in sorted(folder.glob('*.json')):
        if f.stem not in keyset:
            continue
        try:
            ok = not validate(json.loads(f.read_text()))
        except Exception:  # noqa: BLE001
            ok = False
        (good if ok else bad).append(f.stem)
    return good, bad, True


def submitted(state, tag, keys):
    """Manifest keys sent for coding under tag, and the state.json failures split into still failing and resolved."""
    pre = f'{tag}:'
    sent = {k for b in state.get('batches', []) if b.get('tag') == tag for k in b.get('keys', [])}
    done = {k[len(pre):] for k in state.get('done', {}) if k.startswith(pre)}
    failed = {k[len(pre):] for k in state.get('failed', {}) if k.startswith(pre)}
    keyset = set(keys)
    sent = (sent | done | failed) & keyset
    pending = any(b.get('tag') == tag and not b.get('collected') for b in state.get('batches', []))
    return sorted(sent), sorted(failed - done), sorted(failed & done), pending


def screen_category_split(screen):
    """Excluded papers where both screeners excluded but named different categories (screener A's is kept)."""
    n = 0
    for r in screen:
        a, b = r.get('screenA') or {}, r.get('screenB') or {}
        if (not r['eligible'] and not r.get('adjudicated') and a.get('eligible') is False and b.get('eligible') is False
                and a.get('category') != b.get('category')):
            n += 1
    return n


def round_counts(spec, queue, state, inputs):
    name, short, setdir, calcdir, tag, first, colour = spec
    pre, elig, man = D / setdir / 'preselect.json', D / setdir / 'eligibility.json', D / calcdir / 'manifest.jsonl'
    if not (pre.is_file() and elig.is_file() and man.is_file()):
        return None
    inputs += [pre, elig, man]
    drawn = len(ps.read_json(pre))
    screen = ps.read_json(elig)
    keys = manifest(man)
    have = [k for k in keys if queue.get(k, {}).get('status') == 'have']
    sent, failing_state, resolved, pending = submitted(state, tag, keys)
    good, bad, present = coded(tag, keys)
    if present:
        inputs.append(CODINGS / tag)
    excluded = {}
    for r in screen:
        if not r['eligible']:
            excluded[r['category']] = excluded.get(r['category'], 0) + 1
    stages = [(first, drawn), ('Eligible', len(keys)), ('Full text', len(have)),
              ('Submitted for coding', len(sent) or None), ('Coded', len(good) if good else None)]
    return {'name': name, 'short': short, 'tag': tag, 'colour': colour, 'screened': len(screen),
            'adjudicated': sum(bool(r.get('adjudicated')) for r in screen), 'stages': stages, 'excluded': excluded,
            'coded_invalid': bad, 'failed_state': failing_state, 'failed_resolved': resolved,
            'have_not_submitted': sorted(set(have) - set(sent)), 'submitted_without_full_text': sorted(set(sent) - set(have)),
            'batch_pending': pending,
            'in_pending_batch': sorted({k for b in state.get('batches', []) if b.get('tag') == tag and not b.get('collected')
                                        for k in b.get('keys', [])} & set(keys)), 'codings_folder': present, 'category_split': screen_category_split(screen),
            'eligible_equals_manifest': {r['key'] for r in screen if r['eligible']} == set(keys)}


def main():
    raw = QUEUE.read_bytes()                       # read once: the re-fetch may rewrite the file during the run
    read_at = dt.datetime.now().astimezone()
    queue = json.loads(raw)
    queue_sha = hashlib.sha256(raw).hexdigest()
    queue_mtime = dt.datetime.fromtimestamp(QUEUE.stat().st_mtime).astimezone()
    state = json.loads(STATE.read_text())
    inputs = [D / 'gold' / 'pool.json', QUEUE, STATE]
    pool = len(ps.read_json(D / 'gold' / 'pool.json'))
    rounds = [r for r in (round_counts(spec, queue, state, inputs) for spec in ROUNDS) if r]

    fig, _ = ps.figure(ps.DOUBLE, 3.0)
    fig.clf()
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.2, 1], wspace=0.62)
    ax, bx = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])

    # ---- (a) stage counts ----
    y, ticks, labels, heads = 0.0, [], [], []
    for r in rounds:
        heads.append((y, r))
        y += 0.85
        prev = None
        for stage, n in r['stages']:
            ticks.append(y)
            labels.append(stage)
            if n is None:
                if stage == 'Coded' and r['batch_pending']:
                    msg = 'batch not yet returned'
                elif stage == 'Coded':
                    msg = 'no valid codings yet'
                else:
                    msg = 'not yet submitted'
                ax.text(6, y, msg, va='center', ha='left', color=ps.MUTED, fontsize=ps.SMALL, style='italic')
            else:
                ax.barh(y, n, height=0.68, color=r['colour'], edgecolor='white', linewidth=0.6)
                share = f' ({100 * n / prev:.0f}%)' if prev and stage != 'Submitted for coding' else ''
                ax.text(n + 8, y, f'{n}{share}', va='center', ha='left', color=ps.INK, fontsize=ps.SMALL)
                prev = n
            y += 1
        y += 0.35
    for yh, r in heads:
        ax.text(-0.02, yh, r['name'], transform=ax.get_yaxis_transform(), ha='right', va='center',
                fontsize=ps.FONT, fontweight='bold', color=ps.INK)
    ax.set_yticks(ticks, labels)
    ax.tick_params(axis='y', length=0)
    ax.set_ylim(y - 0.35 - 0.5, -0.6)
    xmax = max(n for r in rounds for _, n in r['stages'] if n)
    ax.set_xlim(0, 50 * round(xmax * 1.08 / 50 + 0.5))
    ax.xaxis.set_major_locator(MultipleLocator(200))
    ax.set_xlabel('Papers')
    ps.grid(ax, 'x')
    ax.spines['left'].set_visible(False)
    ax.text(1.0, 1.03, f'2022 candidate pool: {pool:,} OpenAlex articles', transform=ax.transAxes, ha='right',
            va='bottom', fontsize=ps.SMALL, color=ps.INK2)
    ps.panel(ax, 'a', x=-0.36, y=1.03)

    # ---- (b) exclusions at screening ----
    cats = sorted({c for r in rounds for c in r['excluded']},
                  key=lambda c: (-sum(r['excluded'].get(c, 0) for r in rounds), c))
    h = 0.8 / len(rounds)
    for i, r in enumerate(rounds):
        for j, c in enumerate(cats):
            n = r['excluded'].get(c, 0)
            yy = j - 0.4 + h * (i + 0.5)
            share = 100 * n / r['screened']
            bx.barh(yy, share, height=h, color=r['colour'], edgecolor='white', linewidth=0.6,
                    label=f"{r['name']} ({r['short']}): {sum(r['excluded'].values())} of {r['screened']} excluded"
                    if j == 0 else None)
            txt = f"{r['short']}  {n}" if j == 0 else str(n)   # identity named in text on the first group
            bx.text(share + 0.15, yy, txt, va='center', ha='left', color=ps.INK, fontsize=ps.SMALL)
    bx.set_yticks(range(len(cats)), [CATEGORY.get(c, c.replace('_', ' ').capitalize()) for c in cats])
    bx.tick_params(axis='y', length=0)
    bx.set_ylim(len(cats) - 0.5, -0.5)
    smax = max(100 * n / r['screened'] for r in rounds for n in r['excluded'].values())
    bx.set_xlim(0, smax * 1.22)
    bx.xaxis.set_major_locator(MultipleLocator(5 if smax > 8 else 1))
    bx.set_xlabel('Share of screened papers (%)')
    ps.grid(bx, 'x')
    bx.spines['left'].set_visible(False)
    bx.legend(loc='lower right', handlelength=1.0, handleheight=0.8, borderaxespad=0.2)
    ps.panel(bx, 'b', x=-0.42, y=1.03)

    # ---- numbers ----
    numbers = {'rounds_drawn': [r['name'] for r in rounds], 'pool_2022': pool,
               'queue_read_at': read_at.isoformat(timespec='seconds'),
               'queue_mtime': queue_mtime.isoformat(timespec='seconds'), 'queue_sha256': queue_sha,
               'queue_entries': len(queue),
               'round2_seed_note': 'seed 2027 is the g18_round2_draw.py default (DECISIONS.md); '
                                   'derived/r2/preselect.json provenance params are {}, so the file does not record it'}
    for r in rounds:
        k = r['name'].lower().replace(' ', '')
        st = dict(r['stages'])
        numbers[f'{k}_stages'] = st
        numbers[f'{k}_stage_share_pct'] = {
            'eligible_of_first': round(100 * st['Eligible'] / r['stages'][0][1], 1),
            'full_text_of_eligible': round(100 * st['Full text'] / st['Eligible'], 1),
            'coded_of_submitted': round(100 * st['Coded'] / st['Submitted for coding'], 1)
            if st['Coded'] and st['Submitted for coding'] else None}
        numbers[f'{k}_screened'] = r['screened']
        numbers[f'{k}_adjudicated'] = r['adjudicated']
        numbers[f'{k}_eligible_equals_manifest'] = r['eligible_equals_manifest']
        numbers[f'{k}_excluded'] = r['excluded']
        numbers[f'{k}_excluded_share_pct'] = {c: round(100 * n / r['screened'], 1) for c, n in r['excluded'].items()}
        numbers[f'{k}_excluded_both_screeners_category_differs'] = r['category_split']
        numbers[f'{k}_coding_tag'] = r['tag']
        numbers[f'{k}_coding_folder_present'] = r['codings_folder']
        numbers[f'{k}_batch_pending'] = r['batch_pending']
        numbers[f'{k}_codings_failing_validation'] = len(r['coded_invalid'])
        numbers[f'{k}_codings_failing_validation_keys'] = r['coded_invalid']
        numbers[f'{k}_state_failed_unresolved'] = r['failed_state']
        numbers[f'{k}_state_failed_resolved_on_resubmission'] = r['failed_resolved']
        numbers[f'{k}_full_text_not_yet_submitted'] = len(r['have_not_submitted'])
        numbers[f'{k}_submitted_without_full_text_now'] = len(r['submitted_without_full_text'])

    # ---- caption (the script's caption is the caption: no hand-edited copy) ----
    r1 = rounds[0]
    s1 = dict(r1['stages'])
    cap = (f"Corpus construction. (a) Papers at each stage, per round, with the share of the stage above in "
           f"parentheses (none on the submitted bar). Both rounds come from one pool of {pool:,} articles published in 2022 "
           "and indexed by OpenAlex (an open bibliographic index): research articles with an abstract and at least 15 "
           "references, in 16 Earth-science topics and subfields chosen around the study's principal investigator (the "
           "convenor), from publishers with a full-text route (Elsevier, Wiley and AGU, Springer Nature, Copernicus, "
           "Science Advances, Seismica, Geophysical Journal International, and the Seismological Society of America "
           "journals; MDPI, Frontiers, Taylor & Francis and others are not in the pool). The 16 form two rings: the core "
           "ring is the convenor's own 8 OpenAlex topics (seismology, seismic waves and imaging, earthquakes and tectonics, "
           "seismic sensors, cryosphere, high-pressure geophysics), the broad ring 8 Earth-science subfields. Papers with a "
           "convenor co-author are excluded, and the two rounds do not overlap. "
           f"Round 1 is a random preselection of {s1['Preselected']} papers, half per ring, with equal numbers per impact "
           "quintile and subfields taken in turn")
    if len(rounds) > 1:
        s2 = dict(rounds[1]['stages'])
        cap += (f"; round 2 is a draw of {s2['Drawn']} open-access papers from the papers not preselected in round 1, "
                "balanced by ring and impact quintile, taken in turn over publishers, at most four per journal")
    adj = '; '.join(f"{r['name'].lower()}: {r['adjudicated']} of {r['screened']}" for r in rounds)
    cap += (". Eligible: kept by an abstract screen in which two language-model calls judged each abstract without seeing "
            "each other's answer, and a third call settled the cases where they disagreed or either was unsure "
            f"({adj} settled this way); the screener model id was not recorded, and no person has audited the screen. "
            "Full text: a PDF on disk.")
    if len(rounds) > 1:
        cap += (" Round 2 was drawn from open-access papers only, so its higher full-text share reflects the draw, not "
                "better retrieval.")
    cap += (" Submitted: sent for coding as an asynchronous batch request, billed at half price (Anthropic Message Batches "
            "API). Coded: a coding by Claude Opus 5.5 (codebook 1.5.0, graph v0.4.2) that passes the format check of "
            "tools/check_coding.py: required fields and allowed values, steps numbered in order, quotes of 25 words or "
            "fewer. The check says nothing about whether a coding is right; accuracy against human coders is pending.")
    for r in rounds:
        st = dict(r['stages'])
        nm = r['name']
        if st['Coded']:
            fails = len(r['coded_invalid'])
            back = st['Full text'] - st['Coded']
            cap += (f" {nm}: {st['Coded']} papers coded; {back} papers with full text have no valid coding yet: "
                    f"{back - fails} fetched after the first coding batch and {fails} whose coding failed the format check")
            if r['in_pending_batch']:
                cap += (f"; {len(r['in_pending_batch'])} "
                        "of them were sent in a further batch that had not returned when the figure was made")
            if r['have_not_submitted']:
                cap += f"; {len(r['have_not_submitted'])} not yet submitted"
            if r['failed_resolved']:
                cap += f"; {len(r['failed_resolved'])} paper that failed first passed on resubmission"
            cap += f"; a separate {st['Eligible'] - st['Full text']} eligible papers have no PDF."
        elif st['Submitted for coding']:
            cap += (f" {nm}: {st['Submitted for coding']} papers submitted; the coding batch had not returned when the "
                    "figure was made.")
    cap += (" (b) Papers excluded at screening, by category, as a share of papers screened in each round; numbers at bar "
            "ends are counts. The category is the first screener's when both screeners excluded the paper and the "
            "third call's otherwise (the two screeners named different categories for "
            + ' and '.join(f"{r['category_split']} {r['name'].lower()} paper{'s' if r['category_split'] != 1 else ''}"
                           for r in rounds)
            + "). These are counts, not estimates, so no uncertainty is shown. Queue read time and hash, seeds and "
            "script names are in this file's provenance fields.")
    ps.save(fig, 'fig01_corpus', inputs=inputs, numbers=numbers, caption=cap)
    print(cap)


if __name__ == '__main__':
    main()
