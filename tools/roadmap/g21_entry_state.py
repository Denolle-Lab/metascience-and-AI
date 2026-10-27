"""Entry state under audit: is `problem` (78% of round-1 codings) a catch-all that records the introduction's gap statement
rather than what started the work?

The concern. CODEBOOK.md section 2 asks the coder for one entry state and the sentence that establishes it. Most
research articles carry a gap statement in the introduction (Swales 1990, "create a research space": establish the
territory, name a gap, occupy it). If the coder takes that sentence as the entry, every paper looks like it started
from a problem, whatever actually started it (data in hand, a new instrument, an event, a mandate, a prior result).
This script collects the evidence that can be read off the codings themselves and draws a blind audit sample for a
human reader to check against the full text.

Definitions
  entry state     entry.state, one of anomaly, problem, challenged_result, hypothesis, data_without_theory, capability,
                  external_goal (CODEBOOK.md sections 2 and 8; agents/coder/definitions.json).
  entry node      entry.node, the graph v0.4.2 letter where the paper enters (Q question, N new capability, O observe ...).
  valid coding    passes tools/check_coding.py validate().
  round tag       calc1 = round 1 (first calculation plus its top-up), r2 = round 2. gold-r2 = second, independent coding
                  of the round-1 gold papers, used only for test-retest.
  walk            the steps of the final_paper sequence, in document order.
  revisit         a later step at the entry node, counted on the run-collapsed node sequence (consecutive steps at the
                  same node merged, as check_coding.seq does), so a return needs at least one other node in between.
                  The raw count (any later step at that node, including immediate repeats) is also reported.
  reframe after failure   a step with move return_after_failure whose node is Q, or a return_after_failure step whose
                  next step is at Q.
  agreement       share of papers with the same value in both codings.
  same / overlapping evidence   same = the two entry.evidence quotes are identical after lowercasing and stripping
                  punctuation and extra whitespace; overlapping = one normalized quote contains the other, or their word
                  sets have Jaccard >= 0.5 (two runs often trim the same sentence differently).
  Krippendorff alpha (nominal)   1 - D_o / D_e, from g11_human_agreement.alpha_nominal. D_e uses the pooled marginals of
                  both codings: expected agreement A_e = 1 - D_e = (sum_k n_k (n_k - 1)) / (n (n - 1)), n = 2 x papers.
                  With A_o the observed agreement, alpha = (A_o - A_e) / (1 - A_e). When one category holds most papers,
                  A_e is high and the same A_o gives a lower alpha. Cohen's kappa (chance from each coding's own
                  marginals) is given beside it. Bootstrap interval: 2000 resamples of papers.
  per-state stability   for state X: P(other = X | calc1 = X), P(calc1 = X | other = X), and specific agreement
                  2 n_XX / (n_X,calc1 + n_X,other) (positive agreement for that category).
  location of the evidence   entry.page holds an XML locator (section and paragraph, e.g. "§1 ¶4") or a page number
                  (CODEBOOK section 1). Section: when the paper has located XML text (<key>.xml.txt beside the PDF),
                  the evidence quote is searched in it (case and whitespace normalized) and the section heading of the
                  paragraph that contains it is read; otherwise the locator's section number is mapped to the heading.
                  Headings are classed abstract (§0), introduction (heading matches INTRO_RE), or later. Page: for a
                  page-number locator, page within article = entry page - smallest page number cited anywhere in the
                  coding + 1 (an approximation of the article's first page).
  marker families  regular expressions over entry.evidence, case-insensitive, listed in MARKERS below. gap = rhetoric
                  that names a gap or difficulty (Swales move 2); aim = statement of the paper's own aim (move 3);
                  origin = words that point to a concrete starting object (an event, a dataset, an instrument, a
                  mission, a prior result). A quote can match several families.

Inputs
  private/analysis/codings/api/{calc1,r2,gold-r2}/*.json   codings, read only (whatever is valid at run time)
  private/data/roadmap/derived/{gold,r2}/metrics.json      title, DOI, subfield, journal, publisher per paper
  private/data/roadmap/derived/topics/topics_journals.json and tools/roadmap/g20_topics_journals.py   journal family rule
  private/download-queue.json                             full-text location per key (as tools/code_papers.py reads it)

Outputs
  private/data/roadmap/derived/entry/entry_state.json     all numbers, with provenance
  private/data/roadmap/derived/entry/ENTRY.md             the same, readable
  private/data/roadmap/derived/entry/audit_sample.json    60 sampled codings with coded state, node, evidence, text paths
  private/data/roadmap/derived/entry/audit_packets/<key>.json   blind packets: key, DOI, title, text paths (no coding)

Step 9, blind audit (`audit` subcommand; also run at the end of a full run when blind_audit.json exists)
  Input   private/data/roadmap/derived/entry/blind_audit.json: two blind re-codings (A, B) of the entry of the 60 audit
          papers, saved verbatim with provenance (workflow entry-state-evaluation, 2026-10-27). A and B are Claude agents
          of the same model family as the batch coder, so their agreement with it is not independent evidence. Per paper:
          state, node, evidence, evidence_location, rhetorical_gap (the coder's own quote is a gap statement, Swales
          move 2), operational_start (one of OPERATIONAL: what started the work), operational_evidence, problem_subtype
          (free text), confidence. The batch coding is read from the current valid codings (calc1, r2); a change against
          audit_sample.json is reported.
  consensus       the value A and B both gave; 'split' when they differ.
  confirms        a blind coder gives the same state as the batch coding.
  weighted        the sample is stratified (problem 36 of 181, four of each other state), so shares over the whole sample
                  are also weighted back to the population: weight = papers with that batch state / sampled papers with it.
                  Intervals for weighted shares: stratified bootstrap (resample within batch state), 2000 draws.
  Wilson interval 95% interval for a single proportion k/n, used for per-state confirmation shares.
  START_GROUP     four groups of operational start: concrete object (data in hand, event, instrument or deployment,
                  method or model, mandate, surprising observation), prior result, stated hypothesis, literature gap only.
  SUBTYPE_GROUPS  the free-text problem subtypes grouped by their leading words (rules below, first match wins).
  Outputs: entry_state.json key 'blind_audit' (other keys untouched by the audit subcommand) and ENTRY.md section 8.

Run:  python tools/roadmap/g21_entry_state.py          (steps 1-8, and 9 when blind_audit.json exists)
      python tools/roadmap/g21_entry_state.py audit    (step 9 only; does not redraw the sample or rewrite the packets)
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path
import numpy as np
from common import ROOT, DERIVED, write_json, log
from check_coding import validate, runs
from g11_human_agreement import alpha_nominal

try:
    from g20_topics_journals import family, POOLED, MIN_GROUP, assoc
except Exception:  # noqa: BLE001
    family = None

CODINGS = ROOT / 'private' / 'analysis' / 'codings' / 'api'
QUEUE = ROOT / 'private' / 'download-queue.json'
OUT = DERIVED / 'entry'
STATES = ['problem', 'capability', 'anomaly', 'challenged_result', 'hypothesis', 'data_without_theory', 'external_goal']
NODES = list('NEOIQHSDFCVXKPR')
ROUNDS = [('calc1', 'round 1'), ('r2', 'round 2')]
EXPECTED_NODE = {'problem': {'Q'}, 'capability': {'N'}, 'anomaly': {'O', 'E'}, 'hypothesis': {'H'},
                 'challenged_result': {'C', 'V', 'H', 'Q'}, 'data_without_theory': {'O', 'E'}, 'external_goal': {'Q', 'N', 'D'}}
INTRO_RE = re.compile(r'introduc|background|motivation|^\s*(\d+\s*)?overview', re.I)
MARKERS = {
    'gap': {
        'little or less is known': r'\b(little|less|not much)\b[^.]{0,20}\bknown\b',
        'remains unclear or unknown': r'\bremains?\b[^.]{0,30}\b(unclear|unknown|uncertain|elusive|unresolved|debated|controversial|open|poorly|enigmatic|a matter)',
        'poorly understood or constrained': r'\bpoorly\s+(understood|constrained|known|resolved|characteri[sz]ed|quantified|studied|documented)',
        'not well understood or constrained': r'\bnot\s+(yet\s+)?(well|fully|completely)\s+(understood|constrained|known|resolved|characteri[sz]ed|quantified|established|studied)',
        'unknown or unclear': r'\b(unknown|unclear|uncertain|unresolved|ambiguous|enigmatic)\b',
        'debated or controversial': r'\b(debated?|controvers\w*)\b',
        'open question': r'\bopen (question|problem|issue)s?\b',
        'however': r'\bhowever\b',
        'gap': r'\bgaps?\b',
        'lack': r'\black(s|ing|ed)?\b',
        'few or limited studies': r'\b(few|limited|scarce|sparse|rare(ly)?)\b[^.]{0,25}\b(stud(y|ies)|work|research|attention|data|observations?|measurements?|knowledge|understanding)\b',
        'challenge': r'\bchalleng\w*',
        'need': r'\b(need(s|ed)?|necessary|required)\b',
    },
    'aim': {
        'here we / this study': r'\b(here,? we|in this (study|paper|work|article|contribution)|this (study|paper|work|article))\b',
        'aim or objective': r'\b(aims?|objectives?|purpose|goal)\b',
        'we + research verb': r'\bwe\s+(present|propose|develop|investigate|examine|explore|use|apply|test|assess|evaluate|study|analy[sz]e|report|introduce|quantify|determine|address|show|compare)\b',
    },
    'origin': {
        'event': r'\b(earthquake|eruption|tsunami|landslide|flood|storm|hurricane|typhoon|cyclone|drought|heatwave|heat wave|wildfire|fire|outburst|surge|sequence|swarm|event)\b',
        'data in hand': r'\b(data ?set|dataset|database|catalog(ue)?|archive|records?|survey|campaign|observations? from|recorded|collected|samples?|cores?|drill\w*|deployment|network|array)\b',
        'instrument or method': r'\b(instrument|sensor|seismometer|DAS|fiber|fibre|satellite|mission|spectromet\w*|LiDAR|InSAR|GNSS|GPS|technique|method|algorithm|model(l?ing)?|machine learning|neural network|deep learning|tool|framework|approach)\b',
        'prior result': r'\b(previous(ly)?|prior|earlier|recent(ly)?)\b[^.]{0,30}\b(stud(y|ies)|work|results?|findings?|reported|suggested|proposed|showed|shown)\b',
        'mandate or benchmark': r'\b(benchmark|mandate|requirement|policy|stakeholder|hazard assessment|regulat\w*|project|programme|program)\b',
    },
}
COMPILED = {fam: {k: re.compile(v, re.I) for k, v in d.items()} for fam, d in MARKERS.items()}
N_SAMPLE, N_PROBLEM, SEED, NBOOT = 60, 36, 2026, 2000

# ---- blind audit (step 9) ----
BLIND = OUT / 'blind_audit.json'
OPERATIONAL = ['data_in_hand', 'event_occurred', 'new_instrument_or_deployment', 'new_method_or_model', 'mandate_or_project_goal',
               'surprising_observation', 'prior_result_to_test', 'stated_hypothesis', 'literature_gap_only']
# Four groups of operational start. 'concrete object' = something in hand or happening that the work could not have done
# without (data, an event, an instrument or deployment, a method or model, a mandate, a surprising observation).
START_GROUP = {'data_in_hand': 'concrete object', 'event_occurred': 'concrete object', 'new_instrument_or_deployment': 'concrete object',
               'new_method_or_model': 'concrete object', 'mandate_or_project_goal': 'concrete object', 'surprising_observation': 'concrete object',
               'prior_result_to_test': 'prior result', 'stated_hypothesis': 'stated hypothesis', 'literature_gap_only': 'literature gap only'}
# The codebook 1.5.0 entry state each operational start would point to (event_occurred has no state of its own).
START_TO_STATE = {'data_in_hand': 'data_without_theory', 'event_occurred': None, 'new_instrument_or_deployment': 'capability',
                  'new_method_or_model': 'capability', 'mandate_or_project_goal': 'external_goal', 'surprising_observation': 'anomaly',
                  'prior_result_to_test': 'challenged_result', 'stated_hypothesis': 'hypothesis', 'literature_gap_only': 'problem'}
# Grouping of the coders' free-text problem_subtype, by the leading words of the label (lowercased); first match wins.
# Written after reading the 60 + 60 labels of the 2026-10-27 audit; a label that matches no rule is 'ungrouped'.
SUBTYPE_GROUPS = [
    ('process or mechanism unknown', r'(process unknown|mechanism unknown|drivers of|composition and formation)'),
    ('trend attribution', r'attribution of an observed trend'),
    ('debated history or timing', r'(debated history|process timing)'),
    ('quantity or effect unconstrained', r'(quantity unconstrained|future impact unquantified|effect unquantified)'),
    ('method or instrument limitation', r'(method limitation|method performance|instrument limitation)'),
    ('theory incomplete', r'theory ill-posed'),
    ('data gap', r'data gap'),
    ('applied need (hazard, management)', r'hazard need'),
]


# ---------- loading ----------
def load(tag):
    out, bad = {}, 0
    folder = CODINGS / tag
    if not folder.is_dir():
        return out, bad
    for f in sorted(folder.glob('*.json')):
        try:
            c = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            bad += 1
            continue
        if validate(c):
            bad += 1
        else:
            out[c['key']] = c
    return out, bad


def meta_table():
    m = {}
    for s in ['gold', 'r2']:
        p = DERIVED / s / 'metrics.json'
        if p.is_file():
            for r in json.loads(p.read_text())['data']:
                m.setdefault('g22_' + r['id'], r)
    return m


def text_paths(key, queue):
    """PDF and located XML text exactly as tools/code_papers.py finds them: queue entry with status 'have' and a 'file'
    that exists (paths in the queue are relative to the repository root); XML text = the PDF path with suffix .xml.txt."""
    q = queue.get(key) or {}
    f = q.get('file')
    pdf = (ROOT / f) if f and not Path(f).is_absolute() else (Path(f) if f else None)
    ok = q.get('status') == 'have' and pdf is not None and pdf.exists()
    xml = pdf.with_suffix('.xml.txt') if pdf is not None else None
    rel = lambda p: str(p.relative_to(ROOT)) if p is not None and str(p).startswith(str(ROOT)) else (str(p) if p else None)
    return {'pdf': rel(pdf) if ok else None, 'xml_text': rel(xml) if (ok and xml.is_file()) else None,
            'queue_status': q.get('status'), 'code_papers_candidate': ok}


def steps_of(c):
    return next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps']


# ---------- statistics ----------
def share(counter, n):
    return {k: [v, round(v / n, 3) if n else None] for k, v in counter.most_common()}


def chance(a, b, cats):
    """Expected agreement: Krippendorff (pooled marginals, n-1 correction) and Cohen (each coding's own marginals)."""
    n = len(a)
    pooled = Counter(a) + Counter(b)
    N = 2 * n
    ae_k = sum(v * (v - 1) for v in pooled.values()) / (N * (N - 1))
    ca, cb = Counter(a), Counter(b)
    ae_c = sum(ca[k] * cb[k] for k in cats) / n ** 2
    ao = sum(x == y for x, y in zip(a, b)) / n
    kappa = (ao - ae_c) / (1 - ae_c) if ae_c < 1 else None
    return {'observed_agreement': round(ao, 3), 'expected_agreement_krippendorff': round(ae_k, 3),
            'alpha_from_formula': round((ao - ae_k) / (1 - ae_k), 3) if ae_k < 1 else None,
            'expected_agreement_cohen': round(ae_c, 3), 'cohen_kappa': round(kappa, 3) if kappa is not None else None}


def reliability(a, b, name):
    cats = [c for c in (STATES if name == 'state' else NODES) if c in set(a) | set(b)]
    idx = {c: i for i, c in enumerate(cats)}
    M = np.zeros((len(cats), len(cats)), int)
    for x, y in zip(a, b):
        M[idx[x], idx[y]] += 1
    al = alpha_nominal([[x, y] for x, y in zip(a, b)])
    rng = np.random.default_rng([SEED, len(name)])
    n, bs = len(a), []
    for _ in range(NBOOT):
        i = rng.integers(0, n, n)
        v = alpha_nominal([[a[j], b[j]] for j in i])
        if v is not None:
            bs.append(v)
    stab = {}
    for k in cats:
        n1, n2, nkk = int(M[idx[k]].sum()), int(M[:, idx[k]].sum()), int(M[idx[k], idx[k]])
        stab[k] = {'n_calc1': n1, 'n_retest': n2, 'both': nkk,
                   'p_retest_same_given_calc1': round(nkk / n1, 3) if n1 else None,
                   'p_calc1_same_given_retest': round(nkk / n2, 3) if n2 else None,
                   'specific_agreement': round(2 * nkk / (n1 + n2), 3) if n1 + n2 else None}
    dis = Counter(f'{x} -> {y}' for x, y in zip(a, b) if x != y)
    return {'papers': n, 'categories': cats, 'confusion_rows_calc1_cols_retest': M.tolist(), 'alpha': al,
            'alpha_ci95': [round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)] if bs else None,
            **chance(a, b, cats), 'per_category': stab, 'disagreements': dict(dis.most_common())}


# ---------- location of the evidence ----------
def norm(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', (s or '').lower())).strip()


def overlap(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    ta, tb = set(a.split()), set(b.split())
    return a in b or b in a or len(ta & tb) / len(ta | tb) >= 0.5


def xml_index(path):
    """[(locator, top-level section heading, normalized paragraph text)] from a jats_text file."""
    heads, paras, cur = {}, [], None
    for line in Path(path).read_text(errors='replace').splitlines():
        m = re.match(r'^§(\w+)(?:\.[\w.]+)?\s+(.*)$', line)
        if m and not line.startswith('[§'):
            if '.' not in line.split()[0]:
                heads[m.group(1)] = m.group(2).strip()
            continue
        m = re.match(r'^\[(§(\w+)[^\]]*)\]\s*(.*)$', line)
        if m:
            paras.append((m.group(1), m.group(2), norm(m.group(3))))
    return heads, paras


def section_class(top, heading):
    if top == '0' or re.search(r'abstract', heading or '', re.I):
        return 'abstract'
    if heading and INTRO_RE.search(heading):
        return 'introduction'
    if heading is None and top == '1':
        return 'section 1 (heading unknown)'
    return 'later section'


def pnum(loc):
    """Page number in a locator: '1419', 'p. 5', 'Figure 3 (p. 1618)'; None for XML locators and supplement pages."""
    t = str(loc or '').strip()
    if t.startswith(('§', 'S')):
        return None
    m = re.search(r'p\.\s*(\d+)', t) or re.match(r'^(\d+)', t)
    return int(m.group(1)) if m else None


def where(c, paths):
    page = str(c['entry'].get('page') or '')
    out = {'locator': page, 'section_class': None, 'heading': None, 'xml_locator': None, 'page_in_article': None, 'quote_found_in_xml': None}
    heads, top = {}, None
    m = re.match(r'^§(\w+)', page)
    if m:
        top, out['xml_locator'] = m.group(1), page
    if paths.get('xml_text'):
        heads, paras = xml_index(ROOT / paths['xml_text'])
        q = norm(c['entry'].get('evidence'))
        hit = next((p for p in paras if q and q in p[2]), None)
        if hit is None and q:   # a quote may span a paragraph break or be lightly edited: try its first 8 words
            q8 = ' '.join(q.split()[:8])
            hit = next((p for p in paras if q8 and q8 in p[2]), None)
        out['quote_found_in_xml'] = hit is not None
        if hit:
            top, out['xml_locator'] = hit[1], hit[0]
    if top is not None:
        out['heading'] = heads.get(top)
        out['section_class'] = section_class(top, heads.get(top))
    e = pnum(page)
    if e is not None:
        allp = [x for x in (pnum(s.get('page')) for s in steps_of(c)) if x is not None and x > 0] + [e]
        out['page_in_article'] = e - min(allp) + 1
    return out


def markers(text):
    t = text or ''
    return {fam: sorted(k for k, rx in d.items() if rx.search(t)) for fam, d in COMPILED.items()}


# ---------- main ----------
def main():
    queue = json.loads(QUEUE.read_text())
    meta = meta_table()
    R, bad = {}, {}
    for tag, _ in ROUNDS:
        R[tag], bad[tag] = load(tag)
    retest, bad['gold-r2'] = load('gold-r2')
    pooled = {(tag, k): c for tag in R for k, c in R[tag].items()}
    n_by = {tag: len(R[tag]) for tag in R}

    # ---- 1 distributions ----
    dist = {}
    for name, sel in [(t, [c for (tg, _), c in pooled.items() if tg == t]) for t in R] + [('pooled', list(pooled.values()))]:
        n = len(sel)
        if n:
            dist[name] = {'n': n, 'state': share(Counter(c['entry']['state'] for c in sel), n),
                          'node': share(Counter(c['entry']['node'] for c in sel), n)}

    # ---- 2 reliability (calc1 vs gold-r2) ----
    pair = sorted(k for k in retest if k in R['calc1'])
    rel = {'pairs': len(pair), 'retest_tag': 'gold-r2', 'invalid_retest_files': bad['gold-r2']}
    if pair:
        rel['state'] = reliability([R['calc1'][k]['entry']['state'] for k in pair], [retest[k]['entry']['state'] for k in pair], 'state')
        rel['node'] = reliability([R['calc1'][k]['entry']['node'] for k in pair], [retest[k]['entry']['node'] for k in pair], 'node')
        rel['state_and_node_both_agree'] = round(sum(R['calc1'][k]['entry']['state'] == retest[k]['entry']['state'] and
                                                     R['calc1'][k]['entry']['node'] == retest[k]['entry']['node'] for k in pair) / len(pair), 3)
        rel['same_evidence_quote'] = round(sum(norm(R['calc1'][k]['entry']['evidence']) == norm(retest[k]['entry']['evidence']) for k in pair) / len(pair), 3)
        # exact identity undercounts: two runs often trim the same sentence differently. Overlap = one normalized quote
        # contains the other, or token Jaccard >= 0.5.
        rel['same_evidence_overlap'] = round(sum(overlap(R['calc1'][k]['entry']['evidence'], retest[k]['entry']['evidence']) for k in pair) / len(pair), 3)
        rel['same_locator'] = round(sum(str(R['calc1'][k]['entry']['page']) == str(retest[k]['entry']['page']) for k in pair) / len(pair), 3)
        rel['changed_pairs'] = [{'key': k, 'calc1': [R['calc1'][k]['entry']['state'], R['calc1'][k]['entry']['node'], R['calc1'][k]['entry']['evidence']],
                                 'retest': [retest[k]['entry']['state'], retest[k]['entry']['node'], retest[k]['entry']['evidence']]}
                                for k in pair if R['calc1'][k]['entry']['state'] != retest[k]['entry']['state']]

    # ---- 3 internal consistency and 4 revisits ----
    C = list(pooled.values())
    cons = Counter(); cross = Counter(); exp_ok = Counter(); by_state_n = Counter(c['entry']['state'] for c in C)
    rev = {s: Counter() for s in STATES}
    raf_at, raf_next = Counter(), Counter()
    for c in C:
        st, nd = c['entry']['state'], c['entry']['node']
        steps = steps_of(c)
        nodes = [s['node'] for s in steps]
        coll = runs(nodes)
        cross[(st, nd)] += 1
        cons['entry_node_is_first_step'] += nodes[0] == nd if nodes else 0
        cons['entry_node_in_walk'] += nd in nodes
        exp_ok[st] += nd in EXPECTED_NODE.get(st, set())
        r = rev[st]
        r['n'] += 1
        if nd in coll:
            first = coll.index(nd)
            r['entry_node_in_walk'] += 1
            r['revisited'] += nd in coll[first + 1:]
            r['revisit_steps'] += coll[first + 1:].count(nd)
            raw_first = nodes.index(nd)
            r['later_step_raw'] += nd in nodes[raw_first + 1:]
        r['any_Q_after_first_step'] += 'Q' in nodes[1:]
        r['Q_steps_ge2'] += nodes.count('Q') >= 2
        r['Q_revisited_collapsed'] += coll.count('Q') >= 2
        raf = [i for i, s in enumerate(steps) if s.get('move') == 'return_after_failure']
        raf_at.update(steps[i]['node'] for i in raf)
        raf_next.update(steps[i + 1]['node'] if i + 1 < len(steps) else 'end' for i in raf)
        r['any_return_after_failure'] += bool(raf)
        r['reframe_after_failure'] += any(steps[i]['node'] == 'Q' or (i + 1 < len(steps) and steps[i + 1]['node'] == 'Q') for i in raf)
        r['return_after_failure_at_Q'] += any(steps[i]['node'] == 'Q' for i in raf)
        r['q_steps_new'] += sum(s['node'] == 'Q' and s.get('move') == 'new' for s in steps[1:])
    n = len(C)
    consistency = {'n': n, 'entry_node_is_first_step': [cons['entry_node_is_first_step'], round(cons['entry_node_is_first_step'] / n, 3)],
                   'entry_node_appears_in_walk': [cons['entry_node_in_walk'], round(cons['entry_node_in_walk'] / n, 3)],
                   'state_by_node': {s: {nd: cross[(s, nd)] for nd in NODES if cross[(s, nd)]} for s in STATES if by_state_n[s]},
                   'expected_node': {s: sorted(v) for s, v in EXPECTED_NODE.items()},
                   'state_enters_at_expected_node': {s: [exp_ok[s], by_state_n[s], round(exp_ok[s] / by_state_n[s], 3)] for s in STATES if by_state_n[s]},
                   'first_step_node_by_state': {s: dict(Counter(steps_of(c)[0]['node'] for c in C if c['entry']['state'] == s).most_common()) for s in STATES if by_state_n[s]},
                   'first_step_node_move_when_not_entry_node': {s: dict(Counter(f"{steps_of(c)[0]['node']} {steps_of(c)[0].get('move')}" for c in C
                                                                                 if c['entry']['state'] == s and steps_of(c)[0]['node'] != c['entry']['node']).most_common())
                                                                for s in STATES if by_state_n[s]}}
    # problem papers whose walk does not open at Q, with the first step's node and move (one set, so the count of
    # cited or inherited openings shares its denominator with the count of papers)
    pnq = [c for c in C if c['entry']['state'] == 'problem' and steps_of(c)[0]['node'] != 'Q']
    consistency['problem_first_step_not_Q'] = {
        'n': len(pnq), 'of_problem': by_state_n['problem'],
        'first_move_cited_or_inherited': sum(steps_of(c)[0].get('move') in ('cited', 'inherited') for c in pnq),
        'first_step_node_move': dict(Counter(f"{steps_of(c)[0]['node']} {steps_of(c)[0].get('move')}" for c in pnq).most_common())}
    tot = Counter()
    for r in rev.values():
        tot.update(r)
    revisits = {}
    for s, r in list(rev.items()) + [('all', tot)]:
        if r['n']:
            revisits[s] = {k: [r[k], round(r[k] / r['n'], 3)] if k not in ('n', 'revisit_steps', 'q_steps_new') else r[k] for k in
                           ['n', 'entry_node_in_walk', 'revisited', 'later_step_raw', 'revisit_steps', 'any_Q_after_first_step', 'Q_steps_ge2',
                            'Q_revisited_collapsed', 'any_return_after_failure', 'return_after_failure_at_Q', 'reframe_after_failure', 'q_steps_new']}
    # by entry node Q (not by state): papers that enter at Q and reach Q again later in the walk
    qe, qmv = [c for c in C if c['entry']['node'] == 'Q'], Counter()
    q_raw = q_coll = 0
    for c in qe:
        st = steps_of(c)
        nodes = [s['node'] for s in st]
        if 'Q' not in nodes:
            continue
        i0 = nodes.index('Q')
        q_raw += 'Q' in nodes[i0 + 1:]
        q_coll += runs(nodes).count('Q') >= 2
        qmv.update(s.get('move') for s in st[i0 + 1:] if s['node'] == 'Q')
    revisits['entry_node_Q'] = {'n': len(qe), 'later_Q_step_raw': [q_raw, round(q_raw / len(qe), 3) if qe else None],
                                'Q_revisited_collapsed': [q_coll, round(q_coll / len(qe), 3) if qe else None],
                                'later_Q_step_moves': dict(qmv.most_common())}
    revisits['return_after_failure_steps'] = {'n': sum(raf_at.values()), 'at_node': dict(raf_at.most_common()), 'next_node': dict(raf_next.most_common())}

    # ---- 5 where the evidence sits, and its wording ----
    W, Mk = {}, {}
    for (tag, k), c in pooled.items():
        W[(tag, k)] = where(c, text_paths(k, queue))
        Mk[(tag, k)] = markers(c['entry'].get('evidence'))
    loc = {}
    for s in STATES + ['all']:
        ks = [x for x in pooled if s == 'all' or pooled[x]['entry']['state'] == s]
        if not ks:
            continue
        secs = Counter(W[x]['section_class'] for x in ks if W[x]['section_class'])
        pages = [W[x]['page_in_article'] for x in ks if W[x]['page_in_article'] is not None]
        loc[s] = {'n': len(ks), 'with_section': sum(secs.values()), 'section_class': share(secs, sum(secs.values())),
                  'with_page': len(pages), 'page_in_article': {'median': float(np.median(pages)) if pages else None,
                                                               'share_page_1': round(sum(p == 1 for p in pages) / len(pages), 3) if pages else None,
                                                               'share_page_le_2': round(sum(p <= 2 for p in pages) / len(pages), 3) if pages else None,
                                                               'counts': dict(sorted(Counter(min(p, 10) for p in pages).items()))}}
    loc['quote_found_in_xml'] = dict(Counter(str(W[x]['quote_found_in_xml']) for x in pooled))
    loc['abstract_or_introduction_share'] = {s: round(sum(W[x]['section_class'] in ('abstract', 'introduction', 'section 1 (heading unknown)')
                                                          for x in pooled if pooled[x]['entry']['state'] == s and W[x]['section_class']) /
                                                      max(1, sum(1 for x in pooled if pooled[x]['entry']['state'] == s and W[x]['section_class'])), 3)
                                             for s in STATES if by_state_n[s]}
    words = {}
    for s in STATES + ['all']:
        ks = [x for x in pooled if s == 'all' or pooled[x]['entry']['state'] == s]
        if not ks:
            continue
        d = {'n': len(ks)}
        for fam in MARKERS:
            d[f'any_{fam}'] = round(sum(bool(Mk[x][fam]) for x in ks) / len(ks), 3)
            d[f'{fam}_markers'] = dict(Counter(m for x in ks for m in Mk[x][fam]).most_common())
        d['gap_without_origin'] = round(sum(bool(Mk[x]['gap']) and not Mk[x]['origin'] for x in ks) / len(ks), 3)
        d['origin_without_gap'] = round(sum(bool(Mk[x]['origin']) and not Mk[x]['gap'] for x in ks) / len(ks), 3)
        words[s] = d

    # ---- 6 by subfield and journal family ----
    groups = {'available': family is not None and (DERIVED / 'topics' / 'topics_journals.json').is_file()}
    if family is not None:
        A = {}
        for x in pooled:
            r = meta.get(x[1]) or {}
            A[x] = {'subfield': r.get('subfield') or 'unknown', 'family': family(r) if r else 'unknown'}
        for var in ['subfield', 'family']:
            lab = [A[x][var] for x in pooled]
            cnt = Counter(lab)
            g = [v if cnt[v] >= MIN_GROUP else POOLED for v in lab]
            st = [pooled[x]['entry']['state'] for x in pooled]
            tab = {}
            for gv in sorted(set(g), key=lambda v: -g.count(v)):
                sel = [s for s, gg in zip(st, g) if gg == gv]
                tab[gv] = {'n': len(sel), 'problem_share': round(sel.count('problem') / len(sel), 3),
                           'states': dict(Counter(sel).most_common())}
            stc = Counter(st)
            st_pooled = [s if stc[s] >= MIN_GROUP else 'other states' for s in st]
            groups[var] = {'table': tab, 'min_group': MIN_GROUP,
                           'test_state': assoc(g, st_pooled, f'g21 entry state by {var}'),
                           'test_problem': assoc(g, [s == 'problem' for s in st], f'g21 problem by {var}')}
            for t in ('test_state', 'test_problem'):
                groups[var][t] = {k: v for k, v in groups[var][t].items() if k in ('n', 'chi2', 'cramers_v', 'v_ci', 'cramers_v_bc', 'v_bc_ci', 'p')}

    # ---- 7 audit sample, 8 blind packets ----
    rng = np.random.default_rng(SEED)
    by_state = {s: sorted(x for x in pooled if pooled[x]['entry']['state'] == s) for s in STATES}
    quota = {s: 0 for s in STATES}
    quota['problem'] = min(N_PROBLEM, len(by_state['problem']))
    others = [s for s in STATES if s != 'problem']
    left = N_SAMPLE - quota['problem']
    while left > 0 and any(quota[s] < len(by_state[s]) for s in others):   # round robin: equal spread, all of a small state
        for s in others:
            if left and quota[s] < len(by_state[s]):
                quota[s] += 1; left -= 1
    sample = []
    for s in STATES:
        pool_s = by_state[s]
        rounds_s = sorted({t for t, _ in pool_s})
        if len(rounds_s) > 1:   # proportional split by round, largest remainder
            sizes = {t: sum(1 for x in pool_s if x[0] == t) for t in rounds_s}
            raw = {t: quota[s] * sizes[t] / len(pool_s) for t in rounds_s}
            take = {t: int(raw[t]) for t in rounds_s}
            for t in sorted(rounds_s, key=lambda t: -(raw[t] - take[t]))[:quota[s] - sum(take.values())]:
                take[t] += 1
            chosen = []
            for t in rounds_s:
                sub = [x for x in pool_s if x[0] == t]
                chosen += [sub[i] for i in sorted(rng.choice(len(sub), take[t], replace=False))]
        else:
            chosen = [pool_s[i] for i in sorted(rng.choice(len(pool_s), quota[s], replace=False))] if quota[s] else []
        sample += chosen
    order = rng.permutation(len(sample))   # audit order is shuffled so states are not read in blocks
    sample = [sample[i] for i in order]
    rows = []
    pk = OUT / 'audit_packets'
    pk.mkdir(parents=True, exist_ok=True)
    for old in pk.glob('*.json'):
        old.unlink()
    for i, (tag, k) in enumerate(sample, 1):
        c = pooled[(tag, k)]
        tp = text_paths(k, queue)
        r = meta.get(k) or {}
        title = r.get('title') or ((queue.get(k) or {}).get('meta') or {}).get('title')
        rows.append({'audit_order': i, 'key': k, 'round_tag': tag, 'state': c['entry']['state'], 'node': c['entry']['node'],
                     'evidence': c['entry']['evidence'], 'page': c['entry']['page'], 'pages_convention': c.get('pages_convention'),
                     'evidence_section': W[(tag, k)]['section_class'], 'evidence_markers': Mk[(tag, k)],
                     'first_steps': [[s['node'], s['mode'], s.get('move'), s.get('page')] for s in steps_of(c)[:3]],
                     'doi': c.get('doi') or r.get('doi'), 'title': title, **{f'text_{a}': b for a, b in tp.items()}})
        (pk / f'{k}.json').write_text(json.dumps({'key': k, 'doi': c.get('doi') or r.get('doi'), 'title': title,
                                                  'pdf': tp['pdf'], 'xml_text': tp['xml_text']}, indent=1, ensure_ascii=False))
    comp = {'n': len(rows), 'by_state': dict(Counter(r['state'] for r in rows)), 'by_round': dict(Counter(r['round_tag'] for r in rows)),
            'quota': quota, 'available': {s: len(v) for s, v in by_state.items()},
            'with_pdf': sum(bool(r['text_pdf']) for r in rows), 'with_xml_text': sum(bool(r['text_xml_text']) for r in rows)}
    write_json(OUT / 'audit_sample.json', {'composition': comp, 'rows': rows},
               ['private/analysis/codings/api/{calc1,r2}', 'private/download-queue.json', 'derived/{gold,r2}/metrics.json'],
               {'seed': SEED, 'n': N_SAMPLE, 'problem_quota': N_PROBLEM, 'rule': 'problem 36; other states round robin, all of a state if fewer; '
                'within a state proportional by round, largest remainder; numpy default_rng(2026); audit order shuffled'})

    res = {'n_valid': n_by, 'n_invalid_files': bad, 'distribution': dist, 'reliability': rel, 'consistency': consistency,
           'revisits': revisits, 'evidence_location': loc, 'evidence_wording': words, 'by_group': groups, 'audit_sample': comp,
           'markers': MARKERS, 'intro_regex': INTRO_RE.pattern,
           'note': 'one model coder (Claude, codebook 1.5.0); test-retest is the same model coding twice; descriptive'}
    inputs = ['private/analysis/codings/api/{calc1,r2,gold-r2}', 'derived/{gold,r2}/metrics.json', 'derived/topics/topics_journals.json',
              'private/download-queue.json']
    if BLIND.is_file():   # a full run keeps the audit section (step 9) when the blind re-codings exist
        res['blind_audit'] = audit(pooled, rows)
        inputs.append('private/data/roadmap/derived/entry/blind_audit.json')
    write_json(OUT / 'entry_state.json', res, inputs, {'codebook': '1.5.0', 'seed': SEED, 'nboot': NBOOT})
    md = report(res)
    (OUT / 'ENTRY.md').write_text(md)
    log('g21_entry_state.py', 'entry state audit: distribution, reliability, consistency, revisits, evidence, blind sample', n,
        f"calc1 {n_by.get('calc1', 0)}, r2 {n_by.get('r2', 0)}; {rel['pairs']} retest pairs; sample {len(rows)}")
    print(md)


# ---------- 9 blind audit ----------
def wilson(k, n, z=1.96):
    """Wilson 95% interval for a proportion k/n."""
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(float(c - h), 3), round(float(c + h), 3)]


def agree(a, b, cats=None, boot=True):
    """Observed agreement, Krippendorff alpha (nominal) with a bootstrap interval, Cohen kappa, for two codings of the same
    units. Units where either value is None are dropped."""
    pr = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if not pr:
        return {'n': 0}
    a, b = [x for x, _ in pr], [y for _, y in pr]
    cats = cats or sorted(set(a) | set(b), key=str)
    out = {'n': len(a), 'alpha': alpha_nominal([[x, y] for x, y in pr]), **chance(a, b, cats)}
    if boot:
        rng = np.random.default_rng([SEED, len(a), len(cats)])
        bs = [v for v in (alpha_nominal([pr[j] for j in rng.integers(0, len(pr), len(pr))]) for _ in range(NBOOT)) if v is not None]
        out['alpha_ci95'] = [round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)] if bs else None
    return out


def subtype_group(text):
    """Map a coder's free-text problem_subtype to a group of SUBTYPE_GROUPS (first rule that matches the start of the label)."""
    t = (text or '').strip().lower()
    if not t:
        return None
    for g, rx in SUBTYPE_GROUPS:
        if re.match(rx, t):
            return g
    return 'ungrouped'


def audit(pooled, sample_rows):
    """Compare the two blind coders (A, B) with each other and with the batch coding of the 60 audit papers.

    pooled: {(round_tag, key): coding} of valid codings; sample_rows: audit_sample.json rows (stratified sample, so every
    share over the whole sample is reported twice: raw over the 60, and weighted back to the population with
    w_state = papers with that batch state / sampled papers with that state)."""
    blind = json.loads(BLIND.read_text())
    A = {r['key']: r for r in blind['data']['A']}
    B = {r['key']: r for r in blind['data']['B']}
    rows = [r for r in sample_rows if r['key'] in A and r['key'] in B]
    keys = [r['key'] for r in rows]
    batch, mismatch = {}, []
    for r in rows:
        c = pooled.get((r['round_tag'], r['key']))
        if c is None:   # coding no longer valid or missing: fall back to the state frozen in audit_sample.json
            batch[r['key']] = {'state': r['state'], 'node': r['node'], 'evidence': r['evidence']}
            mismatch.append([r['key'], 'coding not found; audit_sample.json values used'])
            continue
        e = c['entry']
        batch[r['key']] = {'state': e['state'], 'node': e['node'], 'evidence': e['evidence']}
        if (e['state'], e['node']) != (r['state'], r['node']):
            mismatch.append([r['key'], f"audit_sample {r['state']}/{r['node']}, coding now {e['state']}/{e['node']}"])
    bs = {k: batch[k]['state'] for k in keys}
    n = len(keys)
    strata = Counter(bs.values())
    avail = Counter(c['entry']['state'] for c in pooled.values())
    w = {s: avail[s] / strata[s] for s in strata}
    wk = np.array([w[bs[k]] for k in keys])

    def cons(f):
        return {k: (A[k][f] if A[k][f] == B[k][f] else None) for k in keys}

    cs, cn, cg, co = cons('state'), cons('node'), cons('rhetorical_gap'), cons('operational_start')
    out = {'n': n, 'n_A': len(A), 'n_B': len(B), 'coders': blind['_provenance'].get('coders'),
           'source': str(BLIND.relative_to(ROOT)), 'batch_vs_audit_sample_mismatches': mismatch,
           'strata': {s: {'population': avail[s], 'sampled': strata[s], 'weight': round(w[s], 3)} for s in STATES if strata[s]},
           'consensus_rule': 'consensus = the value A and B both gave; split when they differ'}

    # 9a agreement and alpha
    rel = {}
    for f, cats in [('state', STATES), ('node', NODES)]:
        a, b, c = [A[k][f] for k in keys], [B[k][f] for k in keys], [batch[k][f] for k in keys]
        cc = [x for x in cats if x in set(a) | set(b) | set(c)]
        rel[f] = {'A_vs_B': agree(a, b, cc), 'A_vs_batch': agree(a, c, cc), 'B_vs_batch': agree(b, c, cc),
                  'consensus_vs_batch': agree([(cs if f == 'state' else cn)[k] for k in keys], c, cc),
                  'alpha_three_way': alpha_nominal([[x, y, z] for x, y, z in zip(a, b, c)]),
                  'all_three_agree': sum(x == y == z for x, y, z in zip(a, b, c)),
                  'weighted_agreement': {'A_vs_B': round(float((wk * np.array([x == y for x, y in zip(a, b)])).sum() / wk.sum()), 3),
                                         'A_vs_batch': round(float((wk * np.array([x == z for x, z in zip(a, c)])).sum() / wk.sum()), 3),
                                         'B_vs_batch': round(float((wk * np.array([y == z for y, z in zip(b, c)])).sum() / wk.sum()), 3)}}
    rel['rhetorical_gap_A_vs_B'] = agree([A[k]['rhetorical_gap'] for k in keys], [B[k]['rhetorical_gap'] for k in keys], [True, False])
    rel['operational_start_A_vs_B'] = agree([A[k]['operational_start'] for k in keys], [B[k]['operational_start'] for k in keys], OPERATIONAL)
    rel['operational_start_grouped_A_vs_B'] = agree([START_GROUP[A[k]['operational_start']] for k in keys],
                                                    [START_GROUP[B[k]['operational_start']] for k in keys])
    rel['problem_subtype_group_A_vs_B'] = agree([subtype_group(A[k]['problem_subtype']) for k in keys],
                                                [subtype_group(B[k]['problem_subtype']) for k in keys], boot=False)
    out['reliability'] = rel

    # 9b confusion batch vs consensus, per batch state confirmation
    cols = STATES + ['split']
    M = np.zeros((len(STATES), len(cols)), int)
    for k in keys:
        M[STATES.index(bs[k]), cols.index(cs[k] or 'split')] += 1
    keep = [i for i, s in enumerate(STATES) if M[i].sum() or M[:, i].sum()]
    out['confusion_batch_rows_consensus_cols'] = {'rows': [STATES[i] for i in keep], 'cols': [STATES[i] for i in keep] + ['split'],
                                                  'matrix': [[int(M[i, j]) for j in keep + [len(STATES)]] for i in keep]}
    per = {}
    for s in STATES:
        ks = [k for k in keys if bs[k] == s]
        if not ks:
            continue
        both = sum(A[k]['state'] == s and B[k]['state'] == s for k in ks)
        per[s] = {'n': len(ks), 'A_confirms': sum(A[k]['state'] == s for k in ks), 'B_confirms': sum(B[k]['state'] == s for k in ks),
                  'both_confirm': both, 'share_both_confirm': round(both / len(ks), 3), 'share_both_confirm_ci95': wilson(both, len(ks)),
                  'neither_confirms': sum(A[k]['state'] != s and B[k]['state'] != s for k in ks),
                  'consensus_other_state': dict(Counter(cs[k] for k in ks if cs[k] and cs[k] != s).most_common()),
                  'split': sum(cs[k] is None for k in ks)}
    out['per_batch_state'] = per

    # population estimate: weighted shares, stratified bootstrap
    def wshare(labels, ks=keys):
        ww = np.array([w[bs[k]] for k in ks])
        cats = sorted({l for l in labels}, key=lambda x: (x is None, str(x)))
        return {('split' if c is None else c): float((ww * np.array([l == c for l in labels])).sum() / ww.sum()) for c in cats}

    rng = np.random.default_rng([SEED, 9])
    idx = {s: [i for i, k in enumerate(keys) if bs[k] == s] for s in strata}
    pop = {}
    for name, lab in [('batch', [bs[k] for k in keys]), ('A', [A[k]['state'] for k in keys]), ('B', [B[k]['state'] for k in keys]),
                      ('consensus', [cs[k] for k in keys]),
                      ('start_group_consensus', [START_GROUP[co[k]] if co[k] else None for k in keys]),
                      ('start_group_A', [START_GROUP[A[k]['operational_start']] for k in keys])]:
        point = wshare(lab)
        draws = {c: [] for c in point}
        for _ in range(NBOOT):
            pick = [i for s in strata for i in rng.choice(idx[s], len(idx[s]), replace=True)]
            d = wshare([lab[i] for i in pick], [keys[i] for i in pick])
            for c in draws:
                draws[c].append(d.get(c, 0.0))
        pop[name] = {c: {'share': round(point[c], 3), 'ci95': [round(float(np.percentile(draws[c], 2.5)), 3), round(float(np.percentile(draws[c], 97.5)), 3)]}
                     for c in sorted(point, key=lambda c: -point[c])}
    out['population_estimate'] = pop

    # 9c evidence: do the blind coders quote the batch sentence; is the quote a rhetorical gap sentence
    ev = {}
    for who, D in [('A', A), ('B', B)]:
        ev[who] = {s: [sum(overlap(D[k]['evidence'], batch[k]['evidence']) for k in keys if bs[k] == s), strata[s]] for s in STATES if strata[s]}
        ev[who]['all'] = [sum(overlap(D[k]['evidence'], batch[k]['evidence']) for k in keys), n]
    ev['A_vs_B'] = [sum(overlap(A[k]['evidence'], B[k]['evidence']) for k in keys), n]
    out['evidence_overlap_with_batch'] = ev

    gap = {'definition': 'rhetorical_gap = the coder judged its own entry quote a gap statement (Swales move 2: names what is unknown, '
                         'unclear, debated or lacking). Batch quotes carry no flag; they inherit a coder flag when that coder quoted an '
                         'overlapping sentence (overlap() rule), and the g21 regex gap marker (MARKERS["gap"]) is given beside them.'}
    for who, D in [('A', A), ('B', B)]:
        gap[f'{who}_by_own_state'] = {s: [sum(D[k]['rhetorical_gap'] for k in keys if D[k]['state'] == s), sum(D[k]['state'] == s for k in keys)]
                                      for s in STATES if any(D[k]['state'] == s for k in keys)}
    gap['agreed_by_consensus_state'] = {s: {'both_true': sum(cs[k] == s and A[k]['rhetorical_gap'] and B[k]['rhetorical_gap'] for k in keys),
                                            'both_false': sum(cs[k] == s and not A[k]['rhetorical_gap'] and not B[k]['rhetorical_gap'] for k in keys),
                                            'n': sum(cs[k] == s for k in keys)} for s in STATES if any(cs[k] == s for k in keys)}
    gap['by_batch_state'] = {}
    for s in STATES:
        ks = [k for k in keys if bs[k] == s]
        if not ks:
            continue
        inh = [k for k in ks if overlap(A[k]['evidence'], batch[k]['evidence']) or overlap(B[k]['evidence'], batch[k]['evidence'])]
        inh_gap = sum(any(D[k]['rhetorical_gap'] for D in (A, B) if overlap(D[k]['evidence'], batch[k]['evidence'])) for k in inh)
        gap['by_batch_state'][s] = {'n': len(ks), 'A_flag': sum(A[k]['rhetorical_gap'] for k in ks), 'B_flag': sum(B[k]['rhetorical_gap'] for k in ks),
                                    'both_flag': sum(A[k]['rhetorical_gap'] and B[k]['rhetorical_gap'] for k in ks),
                                    'batch_quote_regex_gap': sum(bool(markers(batch[k]['evidence'])['gap']) for k in ks),
                                    'batch_quote_overlaps_a_coder_quote': len(inh), 'of_those_flagged_gap': inh_gap}
    rx = [(bool(markers(D[k]['evidence'])['gap']), D[k]['rhetorical_gap']) for D in (A, B) for k in keys]
    gap['regex_vs_coder_flag'] = {'units': len(rx), 'both': sum(r and f for r, f in rx), 'regex_only': sum(r and not f for r, f in rx),
                                  'flag_only': sum(f and not r for r, f in rx), 'neither': sum(not r and not f for r, f in rx),
                                  'agreement': round(sum(r == f for r, f in rx) / len(rx), 3)}
    out['rhetorical_gap'] = gap

    # 9d operational start
    osd = {'categories': OPERATIONAL, 'groups': START_GROUP, 'implied_state': START_TO_STATE,
           'A': dict(Counter(A[k]['operational_start'] for k in keys).most_common()),
           'B': dict(Counter(B[k]['operational_start'] for k in keys).most_common()),
           'agreed': dict(Counter(co[k] or 'split' for k in keys).most_common())}
    osd['by_batch_state'] = {s: {'n': strata[s], 'agreed': dict(Counter(co[k] or 'split' for k in keys if bs[k] == s).most_common()),
                                 'A': dict(Counter(A[k]['operational_start'] for k in keys if bs[k] == s).most_common()),
                                 'B': dict(Counter(B[k]['operational_start'] for k in keys if bs[k] == s).most_common())}
                             for s in STATES if strata[s]}
    osd['by_consensus_state'] = {s: dict(Counter(co[k] or 'split' for k in keys if cs[k] == s).most_common())
                                 for s in STATES if any(cs[k] == s for k in keys)}
    pk = [k for k in keys if bs[k] == 'problem']
    if pk:
        g_agreed = Counter(START_GROUP[co[k]] if co[k] else 'split' for k in pk)
        osd['batch_problem'] = {
            'n': len(pk),
            'agreed_group': dict(g_agreed.most_common()),
            'agreed_literature_gap_only': [sum(co[k] == 'literature_gap_only' for k in pk), len(pk)],
            'either_literature_gap_only': [sum('literature_gap_only' in (A[k]['operational_start'], B[k]['operational_start']) for k in pk), len(pk)],
            'agreed_concrete_object': [sum(START_GROUP.get(co[k]) == 'concrete object' for k in pk), len(pk)],
            'both_coders_concrete_object': [sum(START_GROUP[A[k]['operational_start']] == 'concrete object' and
                                                START_GROUP[B[k]['operational_start']] == 'concrete object' for k in pk), len(pk)],
            'agreed_prior_result': [sum(co[k] == 'prior_result_to_test' for k in pk), len(pk)],
            'consensus_problem_and_agreed_literature_gap_only': [sum(cs[k] == 'problem' and co[k] == 'literature_gap_only' for k in pk), len(pk)],
            'consensus_problem_with_a_gap_quote_and_concrete_start': [sum(cs[k] == 'problem' and A[k]['rhetorical_gap'] and B[k]['rhetorical_gap'] and
                                                                          START_GROUP.get(co[k]) == 'concrete object' for k in pk), len(pk)],
            'literature_gap_only_ci95': wilson(sum(co[k] == 'literature_gap_only' for k in pk), len(pk)),
            'concrete_object_ci95': wilson(sum(START_GROUP.get(co[k]) == 'concrete object' for k in pk), len(pk)),
            'agreed_start_by_consensus_state': {(s or 'split'): dict(Counter(co[k] or 'split' for k in pk if cs[k] == s).most_common())
                                                for s in sorted({cs[k] for k in pk}, key=lambda x: (x is None, str(x)))}}
    both_ok = [k for k in keys if cs[k] and co[k]]
    osd['implied_state_matches_consensus_state'] = {
        'n': len(both_ok), 'match': sum(START_TO_STATE[co[k]] == cs[k] for k in both_ok),
        'by_consensus_state': {s: [sum(START_TO_STATE[co[k]] == s for k in both_ok if cs[k] == s), sum(cs[k] == s for k in both_ok)]
                               for s in STATES if any(cs[k] == s for k in both_ok)}}
    out['operational_start'] = osd

    # 9e problem subtypes (free text, grouped)
    st = {'rules': [list(x) for x in SUBTYPE_GROUPS]}
    for who, D in [('A', A), ('B', B)]:
        lab = [(k, D[k]['problem_subtype']) for k in keys if D[k]['state'] == 'problem']
        st[who] = dict(Counter(subtype_group(t) or 'blank' for _, t in lab).most_common())
        st[f'{who}_raw'] = {k: [t, subtype_group(t)] for k, t in lab}
    both = [k for k in keys if A[k]['state'] == 'problem' and B[k]['state'] == 'problem']
    st['agreed'] = dict(Counter(subtype_group(A[k]['problem_subtype']) if subtype_group(A[k]['problem_subtype']) == subtype_group(B[k]['problem_subtype'])
                                else 'split' for k in both).most_common())
    st['both_problem'] = len(both)
    out['problem_subtype'] = st
    out['confidence'] = {who: dict(Counter(D[k]['confidence'] for k in keys)) for who, D in [('A', A), ('B', B)]}
    out['state_disagreements'] = [{'key': k, 'batch': f"{bs[k]}/{batch[k]['node']}", 'A': f"{A[k]['state']}/{A[k]['node']}",
                                   'B': f"{B[k]['state']}/{B[k]['node']}", 'A_start': A[k]['operational_start'], 'B_start': B[k]['operational_start']}
                                  for k in keys if not (A[k]['state'] == B[k]['state'] == bs[k])]
    return out


def run_audit():
    """Audit step only: read blind_audit.json, the current codings and audit_sample.json; add 'blind_audit' to entry_state.json
    (other sections kept as they are) and rewrite ENTRY.md."""
    R = {}
    for tag, _ in ROUNDS:
        R[tag], _ = load(tag)
    pooled = {(tag, k): c for tag in R for k, c in R[tag].items()}
    sample = json.loads((OUT / 'audit_sample.json').read_text())['data']['rows']
    old = json.loads((OUT / 'entry_state.json').read_text())
    res = old['data']
    res['blind_audit'] = audit(pooled, sample)
    prov = old['_provenance']
    inputs = sorted(set(prov.get('inputs', [])) | {'private/data/roadmap/derived/entry/blind_audit.json', 'derived/entry/audit_sample.json'})
    write_json(OUT / 'entry_state.json', res, inputs, {**prov.get('params', {}), 'audit_step': 'g21_entry_state.py audit'})
    md = report(res)
    (OUT / 'ENTRY.md').write_text(md)
    ba = res['blind_audit']
    log('g21_entry_state.py audit', 'entry state blind audit: A vs B vs batch, operational start, gap quotes, problem subtypes', ba['n'],
        f"state alpha A-B {ba['reliability']['state']['A_vs_B']['alpha']}; problem confirmed by both {ba['per_batch_state'].get('problem', {}).get('both_confirm')}")
    print(md[md.find('## 8.'):])


def pct(x):
    return f'{100 * x:.0f}%' if x is not None else 'n/a'


def frac(v):
    """[k, n] -> 'k/n (p%)'."""
    return f'{v[0]}/{v[1]} ({pct(v[0] / v[1])})' if v and v[1] else 'n/a'


def audit_report(ba):
    rel = ba['reliability']
    L = ['## 8. Blind audit (two blind re-codings of the entry, 60 sampled papers)', '',
         f"Source `{ba['source']}`: coders A and B are Claude agents of the same model family as the batch coder, blind to the batch "
         'coding and to each other. They are not independent of the batch coder. Each gave state, node, evidence quote, whether the '
         'quote is a rhetorical gap sentence, the operational start (what started the work) with a quote, and a problem subtype. '
         'The sample is stratified (problem 36, four of each other state), so whole-sample shares are also given weighted back to the '
         'population (weight = papers with that batch state / sampled papers with it).', '']
    if ba['batch_vs_audit_sample_mismatches']:
        L += ['Batch codings changed since the sample was drawn: ' + '; '.join(f'{k}: {v}' for k, v in ba['batch_vs_audit_sample_mismatches']) + '.', '']
    L += ['| Field | Pair | n | Agreement | Chance (pooled) | Krippendorff alpha [95% bootstrap] | Weighted agreement |', '|:--|:--|--:|--:|--:|--:|--:|']
    for f in ['state', 'node']:
        for p in ['A_vs_B', 'A_vs_batch', 'B_vs_batch', 'consensus_vs_batch']:
            r = rel[f][p]
            L += [f"| {f} | {p.replace('_vs_', ' vs ')} | {r['n']} | {r['observed_agreement']} | {r['expected_agreement_krippendorff']} | "
                  f"{r['alpha']} {r.get('alpha_ci95')} | {rel[f]['weighted_agreement'].get(p, '')} |"]
    for f, lab in [('rhetorical_gap_A_vs_B', 'rhetorical gap'), ('operational_start_A_vs_B', 'operational start (9 classes)'),
                   ('operational_start_grouped_A_vs_B', 'operational start (4 groups)'), ('problem_subtype_group_A_vs_B', 'problem subtype group')]:
        r = rel[f]
        L += [f"| {lab} | A vs B | {r['n']} | {r['observed_agreement']} | {r['expected_agreement_krippendorff']} | {r['alpha']} {r.get('alpha_ci95', '')} | |"]
    L += ['', f"Three-way alpha (A, B, batch): state {rel['state']['alpha_three_way']}, node {rel['node']['alpha_three_way']}. All three give the same state "
          f"in {rel['state']['all_three_agree']} of {ba['n']} papers.", '']
    cm = ba['confusion_batch_rows_consensus_cols']
    L += ['Confusion, rows batch state, columns A/B consensus (split = A and B differ):', '', '| | ' + ' | '.join(cm['cols']) + ' |',
          '|:--|' + '--:|' * len(cm['cols'])]
    L += [f'| {r} | ' + ' | '.join(str(v) for v in row) + ' |' for r, row in zip(cm['rows'], cm['matrix'])]
    L += ['', '| Batch state | n | A confirms | B confirms | Both confirm [Wilson 95%] | Neither | Consensus on another state | Split |', '|:--|--:|--:|--:|--:|--:|:--|--:|']
    for s, v in ba['per_batch_state'].items():
        L += [f"| {s} | {v['n']} | {v['A_confirms']} | {v['B_confirms']} | {v['both_confirm']} ({pct(v['share_both_confirm'])}) {v['share_both_confirm_ci95']} | "
              f"{v['neither_confirms']} | " + ', '.join(f'{a} {b}' for a, b in v['consensus_other_state'].items()) + f" | {v['split']} |"]
    pe = ba['population_estimate']
    L += ['', 'Population estimate of the entry-state distribution (weighted, stratified bootstrap 95%):', '',
          '| State | Batch | A | B | Consensus |', '|:--|--:|--:|--:|--:|']
    cats = list(pe['batch']) + [c for c in pe['consensus'] if c not in pe['batch']]
    for c in cats:
        L += [f'| {c} | ' + ' | '.join(f"{pct(pe[w][c]['share'])} {pe[w][c]['ci95']}" if c in pe[w] else '' for w in ['batch', 'A', 'B', 'consensus']) + ' |']
    L += ['', 'Population estimate of the operational-start group: consensus ' + ', '.join(
        f"{c} {pct(v['share'])} {v['ci95']}" for c, v in pe['start_group_consensus'].items()) + '; coder A alone ' + ', '.join(
        f"{c} {pct(v['share'])} {v['ci95']}" for c, v in pe['start_group_A'].items()) + '.']
    ev = ba['evidence_overlap_with_batch']
    L += ['', f"Blind quote overlaps the batch quote: A {frac(ev['A']['all'])}, B {frac(ev['B']['all'])}; for batch `problem` A "
          f"{frac(ev['A'].get('problem'))}, B {frac(ev['B'].get('problem'))}. A and B quote overlapping sentences in {frac(ev['A_vs_B'])}.", '']
    g = ba['rhetorical_gap']
    L += ['Rhetorical gap quotes (Swales move 2), by batch state:', '',
          '| Batch state | n | A flags gap | B flags gap | Both | Batch quote has regex gap marker | Batch quote overlaps a coder quote | of those, flagged gap |',
          '|:--|--:|--:|--:|--:|--:|--:|--:|']
    for s, v in g['by_batch_state'].items():
        L += [f"| {s} | {v['n']} | {v['A_flag']} | {v['B_flag']} | {v['both_flag']} | {v['batch_quote_regex_gap']} | {v['batch_quote_overlaps_a_coder_quote']} | {v['of_those_flagged_gap']} |"]
    L += ['', 'By the coder\'s own state: A ' + ', '.join(f'{s} {frac(v)}' for s, v in g['A_by_own_state'].items())
          + '; B ' + ', '.join(f'{s} {frac(v)}' for s, v in g['B_by_own_state'].items()) + '. Both flag gap, by consensus state: '
          + ', '.join(f"{s} {v['both_true']}/{v['n']}" for s, v in g['agreed_by_consensus_state'].items()) + '.',
          f"g21 regex gap marker against the coders' flag on their own quotes ({g['regex_vs_coder_flag']['units']} quotes): both "
          f"{g['regex_vs_coder_flag']['both']}, regex only {g['regex_vs_coder_flag']['regex_only']}, flag only {g['regex_vs_coder_flag']['flag_only']}, "
          f"neither {g['regex_vs_coder_flag']['neither']} (agreement {g['regex_vs_coder_flag']['agreement']}).", '']
    o = ba['operational_start']
    L += ['Operational start (what started the work), A and B agreed (split = they differ):', '',
          '| Batch state | n | Agreed operational start |', '|:--|--:|:--|']
    L += [f"| {s} | {v['n']} | " + ', '.join(f'{a} {b}' for a, b in v['agreed'].items()) + ' |' for s, v in o['by_batch_state'].items()]
    if 'batch_problem' in o:
        p = o['batch_problem']
        L += ['', f"Batch `problem` ({p['n']} papers): literature gap only, agreed {frac(p['agreed_literature_gap_only'])} "
              f"(Wilson {p['literature_gap_only_ci95']}), named by either coder {frac(p['either_literature_gap_only'])}; a concrete object "
              f"(data in hand, event, instrument or deployment, method or model, mandate, surprising observation) agreed "
              f"{frac(p['agreed_concrete_object'])}, both coders {frac(p['both_coders_concrete_object'])}; prior result to test agreed "
              f"{frac(p['agreed_prior_result'])}. Groups: " + ', '.join(f'{a} {b}' for a, b in p['agreed_group'].items()) + '.',
              f"Consensus `problem`, both quotes gap statements, and an agreed concrete start: {frac(p['consensus_problem_with_a_gap_quote_and_concrete_start'])}.",
              'Agreed operational start by A/B consensus state, within batch `problem`: ' + '; '.join(
                  f'{s}: ' + ', '.join(f'{a} {b}' for a, b in d2.items()) for s, d2 in p['agreed_start_by_consensus_state'].items()) + '.']
    im = o['implied_state_matches_consensus_state']
    L += ['', f"State implied by the agreed operational start (`START_TO_STATE`) equals the consensus state in {im['match']} of {im['n']} papers "
          'where both are agreed: ' + ', '.join(f'{s} {frac(v)}' for s, v in im['by_consensus_state'].items()) + '.']
    st = ba['problem_subtype']
    L += ['', f"Problem subtypes (free text grouped by `SUBTYPE_GROUPS`): A " + ', '.join(f'{a} {b}' for a, b in st['A'].items())
          + '; B ' + ', '.join(f'{a} {b}' for a, b in st['B'].items()) + f"; agreed on the {st['both_problem']} papers both call problem: "
          + ', '.join(f'{a} {b}' for a, b in st['agreed'].items()) + '.', '',
          f"Papers where A, B and batch do not all agree on the state ({len(ba['state_disagreements'])}):", '',
          '| Key | Batch | A | B | A start | B start |', '|:--|:--|:--|:--|:--|:--|']
    L += [f"| {d['key']} | {d['batch']} | {d['A']} | {d['B']} | {d['A_start']} | {d['B_start']} |" for d in ba['state_disagreements']]
    return L + ['']


def headline(res):
    """The numbers that bear on the catch-all question, computed from res."""
    pdist = res['distribution']['pooled']
    cons, rv, loc, wd, rel = res['consistency'], res['revisits'], res['evidence_location'], res['evidence_wording'], res['reliability']
    pr = cons['first_step_node_by_state'].get('problem', {})
    npb = sum(pr.values())
    lit = cons['problem_first_step_not_Q']['first_move_cited_or_inherited']
    L = ['## Headline', '',
         f"- `problem` is {pct(pdist['state']['problem'][1])} of {pdist['n']} valid codings; Q is {pct(pdist['node'].get('Q', [0, 0])[1])} of entry nodes."]
    if rel.get('pairs'):
        s = rel['state']
        L += [f"- Test-retest on {s['papers']} gold papers: agreement {s['observed_agreement']}, chance agreement {s['expected_agreement_krippendorff']} "
              f"(one category holds most papers), so alpha {s['alpha']} [{s['alpha_ci95'][0]}, {s['alpha_ci95'][1]}]. The two runs quote an identical "
              f"evidence string in {pct(rel['same_evidence_quote'])} of papers and overlapping evidence (one quote contains the other, or token "
              f"Jaccard at least 0.5) in {pct(rel['same_evidence_overlap'])}; same locator {pct(rel['same_locator'])}. The label repeats somewhat "
              "more often than the supporting sentence."]
    if npb:
        L += [f"- For {npb - pr.get('Q', 0)} of {npb} `problem` papers ({pct((npb - pr.get('Q', 0)) / npb)}) the coded walk does not start at Q: "
              + ', '.join(f'{k} {v}' for k, v in pr.items() if k != 'Q') + f'. In {lit} of them the first step is a cited or inherited result '
              '(move cited or inherited): the walk opens on prior work and the question follows. That prior result is a candidate for the '
              'real start (challenged_result or anomaly) and is one thing the audit should check.']
    if 'problem' in rv:
        L += [f"- After entry, Q comes back in {pct(rv['problem']['revisited'][1])} of `problem` papers; no paper reframes its question after a "
              f"failure ({rv['all']['reframe_after_failure'][0]} of {rv['all']['n']}): the {rv['return_after_failure_steps']['n']} returns after failure land on "
              "P, R, V, I and other nodes, never on Q."]
    if 'problem' in loc and 'problem' in wd:
        p = loc['problem']
        sc = {k: x[1] for k, x in p['section_class'].items()}
        L += [f"- `problem` evidence sits in the abstract or introduction in {pct(sc.get('abstract', 0) + sc.get('introduction', 0))} of the "
              f"{p['with_section']} papers with a section, and on the first article page in {pct(p['page_in_article']['share_page_1'])} of the "
              f"{p['with_page']} with a page number. {pct(wd['problem']['any_gap'])} of its quotes carry a gap marker and "
              f"{pct(wd['problem']['gap_without_origin'])} carry a gap marker with no origin marker; for `capability` the figures are "
              f"{pct(wd.get('capability', {}).get('any_gap'))} and {pct(wd.get('capability', {}).get('gap_without_origin'))}."]
    L += ['- What the codings cannot show: whether a data set, event, instrument or mandate started a `problem` paper. That is the job of '
          'the blind audit sample (section 7).', '']
    return L


def report(res):
    d, rel, cons, rv = res['distribution'], res['reliability'], res['consistency'], res['revisits']
    loc, wd = res['evidence_location'], res['evidence_wording']
    rounds = ', '.join(f'{t} {v}' for t, v in res['n_valid'].items())
    L = ['# Entry state: catch-all check', '',
         'Script `tools/roadmap/g21_entry_state.py`; data `private/data/roadmap/derived/entry/entry_state.json`. '
         f'Valid codings read at run time: {rounds} (tools/check_coding.py validate()). Invalid files skipped: '
         + ', '.join(f'{t} {v}' for t, v in res['n_invalid_files'].items()) + '. One model coder (Claude, codebook 1.5.0). '
         'Definitions of every measure are in the script docstring.', '',
         '**Question.** Does `problem` record what started the work, or the gap statement every introduction carries '
         '(Swales 1990, "create a research space")? The codings alone cannot settle it; they can show whether the label behaves '
         'like a default. The blind audit sample at the end is for the direct check.', '']
    L += headline(res)
    L += ['## 1. Distribution', '']
    for name, x in d.items():
        L += [f'**{name}** (n = {x["n"]})', '', '| Entry state | Papers | Share |', '|:--|--:|--:|']
        L += [f'| {k} | {v[0]} | {pct(v[1])} |' for k, v in x['state'].items()]
        L += ['', '| Entry node | Papers | Share |', '|:--|--:|--:|'] + [f'| {k} | {v[0]} | {pct(v[1])} |' for k, v in x['node'].items()] + ['']
    L += ['## 2. Test-retest (calc1 against gold-r2, same model, independent runs)', '']
    if rel['pairs']:
        for f in ['state', 'node']:
            r = rel[f]
            L += [f'**Entry {f}**, {r["papers"]} papers. Observed agreement {r["observed_agreement"]}; agreement expected by chance from '
                  f'the pooled marginals {r["expected_agreement_krippendorff"]}; Krippendorff alpha {r["alpha"]} '
                  f'(95% bootstrap {r["alpha_ci95"]}); Cohen kappa {r["cohen_kappa"]} (chance {r["expected_agreement_cohen"]}). '
                  f'alpha = (A_o - A_e) / (1 - A_e) = ({r["observed_agreement"]} - {r["expected_agreement_krippendorff"]}) / '
                  f'(1 - {r["expected_agreement_krippendorff"]}) = {r["alpha_from_formula"]}.', '',
                  'Confusion matrix (rows calc1, columns gold-r2):', '',
                  '| | ' + ' | '.join(r['categories']) + ' |', '|:--|' + '--:|' * len(r['categories'])]
            L += [f'| {c} | ' + ' | '.join(str(v) for v in row) + ' |' for c, row in zip(r['categories'], r['confusion_rows_calc1_cols_retest'])]
            L += ['', '| Category | calc1 | gold-r2 | both | P(same in gold-r2 given calc1) | P(same in calc1 given gold-r2) | specific agreement |',
                  '|:--|--:|--:|--:|--:|--:|--:|']
            L += [f"| {k} | {v['n_calc1']} | {v['n_retest']} | {v['both']} | {v['p_retest_same_given_calc1']} | {v['p_calc1_same_given_retest']} | {v['specific_agreement']} |"
                  for k, v in r['per_category'].items()]
            L += ['', 'Disagreements: ' + ('; '.join(f'{k} ({v})' for k, v in r['disagreements'].items()) or 'none'), '']
        L += [f"State and node both the same: {pct(rel['state_and_node_both_agree'])}. Same evidence quote (identical after case, "
              f"punctuation and whitespace normalization): {pct(rel['same_evidence_quote'])}; overlapping quote (one contains the other, or "
              f"token Jaccard at least 0.5): {pct(rel['same_evidence_overlap'])}; same locator: {pct(rel['same_locator'])}.", '']
    else:
        L += ['No paper has valid codings in both calc1 and gold-r2.', '']
    L += ['## 3. Internal consistency', '',
          f"Entry node equals the node of the first step of the walk in {cons['entry_node_is_first_step'][0]} of {cons['n']} papers "
          f"({pct(cons['entry_node_is_first_step'][1])}); the entry node appears somewhere in the walk in {pct(cons['entry_node_appears_in_walk'][1])}.", '',
          '| Entry state | Expected node | At expected node | Entry nodes | First-step nodes |', '|:--|:--|--:|:--|:--|']
    for s, v in cons['state_enters_at_expected_node'].items():
        L += [f"| {s} | {','.join(cons['expected_node'][s])} | {v[0]}/{v[1]} ({pct(v[2])}) | "
              + ', '.join(f'{k} {n}' for k, n in cons['state_by_node'][s].items()) + ' | '
              + ', '.join(f'{k} {n}' for k, n in cons['first_step_node_by_state'][s].items()) + ' |']
    L += ['', 'First step (node and move) when it is not the entry node: ' + '; '.join(
        f"{s}: " + ', '.join(f'{k} {v}' for k, v in d2.items()) for s, d2 in cons['first_step_node_move_when_not_entry_node'].items() if d2) + '.']
    L += ['', '## 4. Revisits of the entry node', '',
          'Revisited = the entry node comes back after at least one other node (run-collapsed walk). Reframe after failure = a '
          '`return_after_failure` step at Q, or one followed directly by Q.', '',
          '| Entry state | n | Entry node in walk | Revisited | Any later step there (raw) | Q twice or more (collapsed) | Any return after failure | Reframe after failure |',
          '|:--|--:|--:|--:|--:|--:|--:|--:|']
    for s, v in rv.items():
        if s in ('return_after_failure_steps', 'entry_node_Q'):
            continue
        L += [f"| {s} | {v['n']} | {pct(v['entry_node_in_walk'][1])} | {pct(v['revisited'][1])} | {pct(v['later_step_raw'][1])} | "
              f"{pct(v['Q_revisited_collapsed'][1])} | {pct(v['any_return_after_failure'][1])} | {pct(v['reframe_after_failure'][1])} |"]
    qe = rv['entry_node_Q']
    L += ['', f"By entry node rather than state: of the {qe['n']} papers that enter at Q, {qe['later_Q_step_raw'][0]} "
          f"({pct(qe['later_Q_step_raw'][1])}) have a later Q step and {qe['Q_revisited_collapsed'][0]} ({pct(qe['Q_revisited_collapsed'][1])}) "
          'return to Q after another node. Moves of those later Q steps: ' + ', '.join(f'{k} {v}' for k, v in qe['later_Q_step_moves'].items()) + '.']
    rf = rv['return_after_failure_steps']
    L += ['', f"The {rf['n']} `return_after_failure` steps sit at " + ', '.join(f'{k} {v}' for k, v in rf['at_node'].items())
          + '; the step after them is at ' + ', '.join(f'{k} {v}' for k, v in rf['next_node'].items()) + '.']
    L += ['', '## 5. Where the entry evidence sits and how it is worded', '',
          f"Quote located in the XML text: {loc['quote_found_in_xml']} (True = found, False = XML present but quote not found, None = no XML text).", '',
          '| Entry state | n | With section | Abstract | Introduction | Section 1, heading unknown | Later section | With page | Median page in article | Page 1 | Pages 1-2 |',
          '|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|']
    for s, v in loc.items():
        if not isinstance(v, dict) or 'n' not in v:
            continue
        sc = {k: x[1] for k, x in v['section_class'].items()}
        p = v['page_in_article']
        L += [f"| {s} | {v['n']} | {v['with_section']} | {pct(sc.get('abstract', 0))} | {pct(sc.get('introduction', 0))} | "
              f"{pct(sc.get('section 1 (heading unknown)', 0))} | {pct(sc.get('later section', 0))} | {v['with_page']} | {p['median']} | {pct(p['share_page_1'])} | {pct(p['share_page_le_2'])} |"]
    L += ['', 'Marker families (regular expressions in the script, `MARKERS`): gap = names a gap or difficulty; aim = states the paper\'s own aim; '
          'origin = points to a concrete starting object (event, dataset, instrument, mission, prior result).', '',
          '| Entry state | n | Any gap marker | Any aim marker | Any origin marker | Gap without origin | Origin without gap |', '|:--|--:|--:|--:|--:|--:|--:|']
    for s, v in wd.items():
        L += [f"| {s} | {v['n']} | {pct(v['any_gap'])} | {pct(v['any_aim'])} | {pct(v['any_origin'])} | {pct(v['gap_without_origin'])} | {pct(v['origin_without_gap'])} |"]
    if 'problem' in wd:
        L += ['', 'Gap markers in `problem` evidence: ' + ', '.join(f'{k} {v}' for k, v in wd['problem']['gap_markers'].items()) + '.']
    g = res['by_group']
    L += ['', '## 6. By OpenAlex subfield and journal family', '']
    if 'subfield' in g:
        for var in ['subfield', 'family']:
            t = g[var]
            L += [f"**{var}** (groups under {t['min_group']} papers pooled). Entry state (states under {t['min_group']} pooled) by {var}: "
                  f"Cramer's V {t['test_state']['cramers_v']} (bias-corrected {t['test_state']['cramers_v_bc']}), permutation p {t['test_state']['p']}. "
                  f"Problem vs other: V {t['test_problem']['cramers_v']}, p {t['test_problem']['p']}.", '',
                  f'| {var} | n | problem | states |', '|:--|--:|--:|:--|']
            L += [f"| {k} | {v['n']} | {pct(v['problem_share'])} | " + ', '.join(f'{a} {b}' for a, b in v['states'].items()) + ' |' for k, v in t['table'].items()]
            L += ['']
    else:
        L += ['Skipped: g20 family rule or topics_journals.json not available.', '']
    a = res['audit_sample']
    L += ['## 7. Blind audit sample', '',
          f"{a['n']} codings, `derived/entry/audit_sample.json` (with coded state) and `derived/entry/audit_packets/<key>.json` (key, DOI, title, "
          f"text paths only). By state: " + ', '.join(f'{k} {v}' for k, v in a['by_state'].items()) + '. By round: '
          + ', '.join(f'{k} {v}' for k, v in a['by_round'].items()) + f". With PDF {a['with_pdf']}, with XML text {a['with_xml_text']}. "
          'Sampled with numpy default_rng(2026): problem 36, the other states spread round robin (all of a state when it has fewer), audit order shuffled.', '']
    if 'blind_audit' in res:
        L += audit_report(res['blind_audit'])
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'audit':
        run_audit()
    else:
        main()
