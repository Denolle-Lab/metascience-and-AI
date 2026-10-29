"""Paper topics and journal names in the roadmap corpus: who is in it at each stage, whether coding coverage depends on
field or venue, whether workflows and outcomes differ by field and venue, and whether the g17 workflow-outcome
associations survive once field or venue is held fixed.

Inputs
  private/data/roadmap/derived/gold/pool.json                 2022 candidate pool, the frame both rounds are drawn from
  private/data/roadmap/derived/gold/{preselect,metrics,eligibility}.json   round 1 (600 preselected)
  private/data/roadmap/derived/r2/{preselect,metrics,eligibility}.json     round 2 (drawn), if present
  private/data/roadmap/derived/calc1/manifest.jsonl           round 1 eligible corpus
  private/data/roadmap/derived/r2calc/manifest.jsonl          round 2 eligible corpus, if present
  private/download-queue.json                                 full-text status per key, read as it is at run time
  private/analysis/codings/api/{calc1,r2}/*.json              codings (read only)
  private/data/roadmap/derived/outcomes/outcomes.json         g17 tests; rows with q < 0.1 are rechecked in question 5
  OpenAlex /topics (through common.openalex, cached)          field and domain of each leading topic

Stages (per round; the pool is shared by both rounds)
  pool        every paper in gold/pool.json
  drawn       round 1 preselected (600) or round 2 drawn (preselect.json of the round)
  eligible    key in the round's manifest (derived/<calc>/manifest.jsonl)
  full text   eligible and status "have" in private/download-queue.json (a PDF on disk; same rule as fig01)
  coded       eligible with a coding <tag>/<key>.json that passes tools/check_coding.py validate(); tag calc1 for
              round 1, r2 for round 2 (same rule as fig01, fig09). n is whatever exists at run time.

Paper attributes (OpenAlex, from the round's metrics.json or the pool)
  subfield    subfield of the paper's leading (primary) topic; field and domain come from the /topics endpoint
  topic       leading topic (topic_id, topic)
  journal     source display name, control characters removed; source_id for counting distinct journals
  publisher   OpenAlex host organisation name as stored by g02_pool.py
  family      journal family, first matching rule of FAMILY_RULES below: DOI prefix, then publisher, then journal name.
              AGU journals carry DOI prefix 10.1029 whether OpenAlex lists Wiley or AGU as publisher. Nature portfolio
              is DOI prefix 10.1038 (Nature, Nature Geoscience, Nature Communications, Scientific Reports, Communications
              Earth & Environment, npj journals). Springer Nature non-portfolio covers Springer imprints and the
              Pleiades and Allerton translation journals (10.1007, 10.1186, 10.1134, 10.3103 and others with a Springer
              publisher). Wiley non-AGU covers 10.1002, 10.1111, Hindawi (10.1155) and other Wiley prefixes. SSA is
              10.1785 (BSSA, SRL, TSR). Oxford is 10.1093 (GJI). AAAS is 10.1126 (Science, Science Advances).
              MDPI (10.3390) and Frontiers (10.3389) are kept as rules although the pool's host list excludes them.

Questions and statistics (numpy only)
  1 composition   counts and shares of field, subfield, leading topic, journal family, publisher per stage and round.
                  Journals: distinct journals, papers per journal, Herfindahl index HHI = sum of squared journal shares
                  (1/HHI = effective number of journals), top-5 journal share, most frequent journals.
  2 coverage      among eligible papers, is reaching full text and being coded associated with subfield, field,
                  family, publisher? Categories with fewer than MIN_GROUP eligible papers are pooled into POOLED.
                  Effect: Cramer's V (0 = independent, 1 = category determines coverage), plain and bias-corrected
                  (Bergsma 2013), each with a 95% percentile bootstrap interval, and per category the coverage rate
                  minus the rate in all other categories, with interval.
                  Test: permutation of the coverage label (NPERM), statistic Pearson chi-square. Sets: each round
                  alone and, once both rounds have codings, 'pooled' = both rounds with round as a stratum
                  (assoc_strat(), as in question 3). BH q within each set.
  Rounds in questions 3 and 4 (design decided by the PI, October 27, 2026: round 1 exploratory, round 2 confirmatory
                  for the associations frozen in preregistration/round2-confirmatory.json, both rounds also pooled
                  for description with round as a stratum). Each test is run on three blocks, BH q within each block:
                    round1             round 1 alone; also the top-level 'rows' of 'workflows' and 'outcomes_by_group'
                                       (same keys and generator names as earlier runs, so figures keep reading them)
                    by_round.<round>   each round alone (by_round.round1 is the top-level block)
                    pooled_stratified  both rounds, round as a stratum: the response is permuted within round; binary
                                       and categorical features use the sum of within-round Pearson chi-squares, with the
                                       pooled-table Cramer's V and a Mantel-Haenszel rate difference (weighted mean of the
                                       within-round group-minus-rest differences, weight n_group n_rest / n_round);
                                       counts and outcomes use Kruskal-Wallis H on ranks taken within round (aligned
                                       ranks); bootstrap resamples are drawn within round.
                  The confirmatory test itself (g23_confirmatory.py test) is not rerun here; it calls assoc(),
                  numeric_by_group(), stratified() and pool_small(), which this script leaves unchanged.
  3 workflows     among coded papers (per block above), node use, entry state, decisive mode, composition, loop
                  features and counts from g17 features(), against subfield and family. Groups with fewer than
                  MIN_GROUP coded papers are pooled into POOLED. Binary features: chi-square permutation test,
                  Cramer's V and per-group rate difference from the rest. Whole categorical variables (entry state,
                  decisive mode, composition; levels under MIN_GROUP pooled): chi-square permutation test, Cramer's V.
                  Counts: Kruskal-Wallis H (rank analysis of variance) permutation test, effect epsilon^2 = H / (n - 1).
  4 outcomes      medians of cnp, fwci, novelty_pair, breadth_refs by subfield and family, among coded and among
                  eligible papers, with bootstrap intervals; Kruskal-Wallis permutation test and epsilon^2. cnp and fwci
                  are normalized by OpenAlex within subfield, year and type (OpenAlex help, work object, read
                  2026-10-27); novelty_pair and breadth_refs are not.
  5 confounding   for each g17 test with q < 0.1: the Spearman rho recomputed on the codings present now, then the
                  within-stratum rank correlation (ranks centred within each stratum, so only within-stratum
                  co-variation counts) with a stratified bootstrap interval and a stratified permutation p (outcomes
                  shuffled within strata). Strata: subfield, family, subfield x family. A stratum of one paper
                  contributes nothing. Survives = same sign as the g17 rho and BH q < 0.1 over all question-5 tests;
                  also recorded: whether the bootstrap interval excludes 0, and attenuation = within rho / rho now.
  6 subfields      what each OpenAlex subfield holds: its three most common leading topics and its ring (core: the
                  convenor's 8 topics; broad: 8 Earth-science subfields) in the pool, the round-1 preselection and the
                  coded set; and how many coded papers per subfield use machine-learning vocabulary (ML_TERMS) anywhere in
                  the coding or in an N (new capability) step. subfield_display() turns this into figure labels.
  Cramer's V intervals are percentile intervals of the resampled bias-corrected V; V is biased upward under resampling,
  so an interval can sit above its own point estimate. Read them as the spread of V, not as bias-corrected intervals.
  Benjamini-Hochberg q is computed separately within questions 2, 3, 4 and 5. Bootstrap NBOOT resamples over papers;
  permutations NPERM. Each test has its own generator seeded by [SEED, crc32 of the test name]. Descriptive and
  exploratory: one model coder, small cells, citations at about four years.

Outputs  private/data/roadmap/derived/topics/{topics_journals.json, TOPICS.md}
Run:     python tools/roadmap/g20_topics_journals.py
"""
import json
import re
import zlib
from collections import Counter
import numpy as np
from common import ROOT, PRIVATE, DERIVED, write_json, log, openalex
from check_coding import validate
from g17_outcomes import features, bh, OUTCOMES as G17_OUTCOMES

CODINGS = PRIVATE / 'analysis' / 'codings' / 'api'
QUEUE = PRIVATE / 'download-queue.json'
OUT = DERIVED / 'topics'
ROUNDS = [  # name, set folder, calc folder, coding tag, first-stage label
    ('round1', 'gold', 'calc1', 'calc1', 'preselected'),
    ('round2', 'r2', 'r2calc', 'r2', 'drawn'),
]
STAGES = ['drawn', 'eligible', 'full_text', 'coded']
OUTS = ['cnp', 'fwci', 'novelty_pair', 'breadth_refs']
NORMALIZED = {'cnp': True, 'fwci': True, 'novelty_pair': False, 'breadth_refs': False}
MIN_GROUP, MIN_FEATURE = 10, 10        # papers per category; binary feature present in 10 .. n - 10 papers (g17)
NBOOT, NPERM, SEED, TOP = 2000, 5000, 2026, 15
POOLED = 'pooled small groups'
# machine-learning vocabulary, for checking what the OpenAlex subfield 'Artificial Intelligence' holds (question 6)
ML_TERMS = re.compile(r'machine.learning|deep.learning|neural.net|convolutional|random.forest|transformer|support.vector|'
                      r'gradient.boost|xgboost|\blstm\b|u-net|autoencoder|self-supervised|supervised learning|\bcnn\b|'
                      r'artificial intelligence', re.I)
# display names for journal families in figures and pages; the json keeps the rule names
FAMILY_DISPLAY = {'EGU/Copernicus': 'Copernicus (mostly EGU)'}
# short topic names for subfield labels (subfield_display)
TOPIC_SHORT = {'Seismology and Earthquake Studies': 'seismology', 'Cryospheric studies and observations': 'cryosphere',
               'Geophysics and Sensor Technology': 'seismic sensors', 'Archaeological Research and Protection': 'archaeology'}   # categories under MIN_GROUP papers; distinct from the family 'other'
FAMILY_RULES = [  # (kind, pattern, family); first match wins
    ('doi', '10.1029', 'AGU'), ('doi', '10.5194', 'EGU/Copernicus'), ('doi', '10.1038', 'Nature portfolio'),
    ('doi', '10.1785', 'SSA'), ('doi', '10.1093', 'Oxford'), ('doi', '10.1126', 'AAAS'), ('doi', '10.3390', 'MDPI'),
    ('doi', '10.3389', 'Frontiers'), ('doi', '10.1016', 'Elsevier'),
    ('doi', '10.1007', 'Springer Nature (non-portfolio)'), ('doi', '10.1186', 'Springer Nature (non-portfolio)'),
    ('doi', '10.1134', 'Springer Nature (non-portfolio)'), ('doi', '10.3103', 'Springer Nature (non-portfolio)'),
    ('doi', '10.1002', 'Wiley non-AGU'), ('doi', '10.1111', 'Wiley non-AGU'), ('doi', '10.1155', 'Wiley non-AGU'),
    ('publisher', 'AGU', 'AGU'), ('publisher', 'Copernicus', 'EGU/Copernicus'),
    ('publisher', 'Nature Portfolio', 'Nature portfolio'), ('publisher', 'Springer Nature', 'Springer Nature (non-portfolio)'),
    ('publisher', 'Springer', 'Springer Nature (non-portfolio)'), ('publisher', 'Wiley', 'Wiley non-AGU'),
    ('journal', 'Bulletin of the Seismological Society of America', 'SSA'), ('journal', 'Seismological Research Letters', 'SSA'),
    ('journal', 'The Seismic Record', 'SSA'), ('journal', 'Geophysical Journal International', 'Oxford'),
    ('journal', 'Science Advances', 'AAAS'), ('journal', 'Science', 'AAAS'),
]


def family(r):
    pre = (r.get('doi') or '').split('/')[0]
    for kind, pat, fam in FAMILY_RULES:
        if (kind == 'doi' and pre == pat) or (kind == 'publisher' and r.get('publisher') == pat) or \
                (kind == 'journal' and clean(r.get('journal')) == pat):
            return fam
    return 'other'


def clean(name):
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', name or '').strip() or 'unknown'


def load(path):
    x = json.loads(path.read_text())
    return x['data'] if isinstance(x, dict) and 'data' in x else x


def subfield_display(sub, res, short=None, stage='coded', min_share=0.6):
    """Label for an OpenAlex subfield that names its dominant leading topic when one topic holds at least min_share of the
    subfield's papers at the stage (from res['subfield_topics']); e.g. 'Artificial intelligence (100% seismology)'."""
    name = (short or {}).get(sub, sub)
    t = (res.get('subfield_topics', {}).get(stage, {}).get(sub) or {}).get('top_topics') or []
    if t and t[0]['share'] >= min_share and t[0]['topic'] in TOPIC_SHORT:
        return f"{name} ({round(100 * t[0]['share'])}% {TOPIC_SHORT[t[0]['topic']]})"
    return name


def gen(name):
    return np.random.default_rng([SEED, zlib.crc32(name.encode())])


def topic_fields(tids):
    """{topic id: (field, domain)} from OpenAlex /topics, 50 ids per call (cached by common.openalex)."""
    out, tids = {}, sorted(t for t in tids if t)
    for i in range(0, len(tids), 50):
        r = openalex('topics', {'filter': 'id:' + '|'.join(tids[i:i + 50]), 'per-page': 50,
                                'select': 'id,display_name,field,domain'})
        for t in r.get('results', []):
            out[t['id'].rsplit('/', 1)[-1]] = ((t.get('field') or {}).get('display_name'), (t.get('domain') or {}).get('display_name'))
    return out


# ---------- statistics ----------
def rank(x):
    """Average ranks (0-based, as g17), via unique counts."""
    _, inv, cnt = np.unique(np.asarray(x, float), return_inverse=True, return_counts=True)
    return (np.cumsum(cnt) - (cnt - 1) / 2 - 1)[inv]


def codes(labels):
    lv = sorted(set(labels))
    return np.array([lv.index(v) for v in labels]), lv


def chi2(a, b, ka, kb):
    t = np.bincount(a * kb + b, minlength=ka * kb).reshape(ka, kb).astype(float)
    t = t[t.sum(1) > 0][:, t.sum(0) > 0]
    if min(t.shape) < 2:
        return 0.0, 0.0
    e = np.outer(t.sum(1), t.sum(0)) / t.sum()
    x2 = float(((t - e) ** 2 / e).sum())
    return x2, float(np.sqrt(x2 / (t.sum() * (min(t.shape) - 1))))


def v_bc(a, b, ka, kb):
    """Bias-corrected Cramer's V (Bergsma 2013, J. Korean Stat. Soc. 42:323): phi^2 and table size shrunk by their
    expectation under independence, so small tables with many cells are not inflated."""
    t = np.bincount(a * kb + b, minlength=ka * kb).reshape(ka, kb)
    t = t[t.sum(1) > 0][:, t.sum(0) > 0]
    n, (r, k) = t.sum(), t.shape
    if min(r, k) < 2 or n < 2:
        return 0.0
    phi2 = max(0.0, chi2(a, b, ka, kb)[0] / n - (k - 1) * (r - 1) / (n - 1))
    rc, kc = r - (r - 1) ** 2 / (n - 1), k - (k - 1) ** 2 / (n - 1)
    d = min(kc - 1, rc - 1)
    return float(np.sqrt(phi2 / d)) if d > 0 else 0.0


def assoc(g, y, name):
    """Categorical g against categorical y: chi-square permutation p, Cramer's V with bootstrap interval; for a 0/1 y also
    per-group rate and rate minus the rest, with intervals from the same resamples."""
    rng = gen(name)
    a, la = codes(g); b, lb = codes(y)
    n, ka, kb = len(a), len(la), len(lb)
    x2, v = chi2(a, b, ka, kb)
    perm = np.array([chi2(a, rng.permutation(b), ka, kb)[0] for _ in range(NPERM)])
    p = (1 + (perm >= x2 - 1e-9).sum()) / (NPERM + 1)
    binary = set(lb) <= {False, True, 0, 1}
    yb = np.asarray(y, float) if binary else None
    vs, vbs, diffs = [], [], []
    for _ in range(NBOOT):
        i = rng.integers(0, n, n)
        vs.append(chi2(a[i], b[i], ka, kb)[1])
        vbs.append(v_bc(a[i], b[i], ka, kb))
        if binary:
            row = []
            for j in range(ka):
                m = a[i] == j
                row.append(yb[i][m].mean() - yb[i][~m].mean() if 0 < m.sum() < n else np.nan)
            diffs.append(row)
    r = {'n': n, 'chi2': round(x2, 2), 'cramers_v': round(v, 3), 'v_ci': ci(vs), 'cramers_v_bc': round(v_bc(a, b, ka, kb), 3),
         'v_bc_ci': ci(vbs), 'p': round(float(p), 4)}
    if binary:
        diffs = np.array(diffs)
        r['groups'] = {lv: {'n': int((a == j).sum()), 'rate': round(float(yb[a == j].mean()), 3),
                            'diff_vs_rest': round(float(yb[a == j].mean() - yb[a != j].mean()), 3) if 0 < (a == j).sum() < n else None,
                            'diff_ci': ci(diffs[:, j])} for j, lv in enumerate(la)}
    else:
        r['groups'] = {lv: {'n': int((a == j).sum())} for j, lv in enumerate(la)}
    return r


def kw(a, ka, x):
    """Kruskal-Wallis H with tie correction (x already ranked, 1-based) and epsilon^2 = H / (n - 1)."""
    n = len(x)
    s, c = np.bincount(a, x, ka), np.bincount(a, minlength=ka)
    m = c > 0
    h = 12 / (n * (n + 1)) * ((s[m] - c[m] * (n + 1) / 2) ** 2 / c[m]).sum()
    _, t = np.unique(x, return_counts=True)
    corr = 1 - (t ** 3 - t).sum() / (n ** 3 - n)
    h = h / corr if corr > 0 else 0.0
    return float(h), float(h / (n - 1))


def numeric_by_group(g, x, name):
    """Numeric x across groups g: Kruskal-Wallis permutation p, epsilon^2 with interval, per-group median with interval."""
    rng = gen(name)
    a, la = codes(g); x = np.asarray(x, float)
    n, ka = len(a), len(la)
    rx = rank(x) + 1
    h, e2 = kw(a, ka, rx)
    perm = np.array([kw(rng.permutation(a), ka, rx)[0] for _ in range(NPERM)])
    p = (1 + (perm >= h - 1e-9).sum()) / (NPERM + 1)
    es, meds = [], []
    for _ in range(NBOOT):
        i = rng.integers(0, n, n)
        es.append(kw(a[i], ka, rank(x[i]) + 1)[1])
        meds.append([np.median(x[i][a[i] == j]) if (a[i] == j).any() else np.nan for j in range(ka)])
    meds = np.array(meds)
    return {'n': n, 'H': round(h, 2), 'epsilon2': round(e2, 3), 'epsilon2_ci': ci(es), 'p': round(float(p), 4),
            'groups': {lv: {'n': int((a == j).sum()), 'median': round(float(np.median(x[a == j])), 3), 'median_ci': ci(meds[:, j])}
                       for j, lv in enumerate(la)}}


def ci(v):
    v = np.asarray(v, float); v = v[~np.isnan(v)]
    return [round(float(np.percentile(v, 2.5)), 3), round(float(np.percentile(v, 97.5)), 3)] if len(v) else None


def within_rho(rf, ro, s):
    """Rank correlation after centring both rank vectors within strata s."""
    _, s = np.unique(s, return_inverse=True)
    c = np.bincount(s)
    a = rf - (np.bincount(s, rf) / c)[s]
    b = ro - (np.bincount(s, ro) / c)[s]
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return (float((a * b).sum() / d) if d > 0 else np.nan), a, b, d


def stratified(f, o, strata, name):
    """Within-stratum Spearman: estimate, stratified bootstrap interval, stratified permutation p (two-sided)."""
    rng = gen(name)
    f, o = np.asarray(f, float), np.asarray(o, float)
    _, s = np.unique(strata, return_inverse=True)
    rho, a, b, d = within_rho(rank(f), rank(o), s)
    if np.isnan(rho):
        return None
    base = np.argsort(s, kind='stable')
    perm = []
    for _ in range(NPERM):
        idx = np.empty(len(s), int)
        idx[base] = np.lexsort((rng.random(len(s)), s))   # shuffle positions within each stratum
        perm.append(abs((a * b[idx]).sum() / d))
    p = (1 + (np.array(perm) >= abs(rho) - 1e-12).sum()) / (NPERM + 1)
    groups = [np.flatnonzero(s == k) for k in range(s.max() + 1)]
    bs = []
    for _ in range(NBOOT):
        i = np.concatenate([gi[rng.integers(0, len(gi), len(gi))] for gi in groups])
        bs.append(within_rho(rank(f[i]), rank(o[i]), s[i])[0])
    eff = int(sum(len(gi) for gi in groups if len(gi) > 1))
    return {'rho_within': round(rho, 3), 'ci': ci(bs), 'p': round(float(p), 4), 'strata': len(groups),
            'strata_of_2_or_more': sum(len(gi) > 1 for gi in groups), 'papers_in_those_strata': eff}


def spearman(f, o):
    a, b = rank(f), rank(o)
    return float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else np.nan


def pool_small(labels, k=MIN_GROUP):
    c = Counter(labels)
    small = sorted(v for v, m in c.items() if m < k)
    return [(POOLED if v in small else v) for v in labels], {v: c[v] for v in small}


# ---------- round-stratified versions (pooled description with round as a stratum) ----------
# assoc(), numeric_by_group() and stratified() above are also called by g23_confirmatory.py and stay unchanged.
def within_perm(rng, s, base):
    """Index array that shuffles positions within each stratum (s integer codes, base = argsort(s, stable))."""
    idx = np.empty(len(s), int)
    idx[base] = np.lexsort((rng.random(len(s)), s))
    return idx


def within_boot(rng, groups):
    """Bootstrap index: resample papers within each stratum, keeping stratum sizes."""
    return np.concatenate([gi[rng.integers(0, len(gi), len(gi))] for gi in groups])


def assoc_strat(g, y, s, name):
    """assoc() with round as a stratum. Statistic: sum over strata of the within-stratum Pearson chi-square of g against
    y; p from permuting y within strata (NPERM). Effects: bias-corrected Cramer's V of the pooled table (description),
    and cramers_v_strat = sqrt(statistic / (n (min(k) - 1))), each with an interval from bootstrap resamples drawn within
    strata (NBOOT). For a 0/1 y, per group: pooled rate, rate per stratum, and the rate minus the rest as the
    Mantel-Haenszel weighted mean of the within-stratum differences (weight n_group n_rest / n_stratum), with interval."""
    rng = gen(name)
    a, la = codes(g); b, lb = codes(y)
    _, st = np.unique(s, return_inverse=True)
    sl = sorted(set(s))
    n, ka, kb, R = len(a), len(la), len(lb), st.max() + 1
    base = np.argsort(st, kind='stable')
    groups = [np.flatnonzero(st == r) for r in range(R)]

    def stat(a, b, st):
        return sum(chi2(a[st == r], b[st == r], ka, kb)[0] for r in range(R))
    x2 = stat(a, b, st)
    perm = np.array([stat(a, b[within_perm(rng, st, base)], st) for _ in range(NPERM)])
    p = (1 + (perm >= x2 - 1e-9).sum()) / (NPERM + 1)
    binary = set(lb) <= {False, True, 0, 1}
    yb = np.asarray(y, float) if binary else None
    dk = max(1, min(ka, kb) - 1)

    def mh(a, yb, st, j):
        num = den = 0.0
        for r in range(R):
            m1, m0 = (a == j) & (st == r), (a != j) & (st == r)
            n1, n0 = m1.sum(), m0.sum()
            if n1 and n0:
                w = n1 * n0 / (n1 + n0)
                num += w * (yb[m1].mean() - yb[m0].mean()); den += w
        return num / den if den else np.nan
    vs, vss, vbs, diffs = [], [], [], []
    for _ in range(NBOOT):
        i = within_boot(rng, groups)
        vs.append(chi2(a[i], b[i], ka, kb)[1])
        vbs.append(v_bc(a[i], b[i], ka, kb))
        vss.append(np.sqrt(stat(a[i], b[i], st[i]) / (n * dk)))
        if binary:
            diffs.append([mh(a[i], yb[i], st[i], j) for j in range(ka)])
    r = {'n': n, 'n_by_stratum': {sl[k]: len(gk) for k, gk in enumerate(groups)}, 'stratified_by': 'round',
         'chi2': round(x2, 2), 'statistic': 'sum over rounds of the within-round Pearson chi-square',
         'chi2_pooled_table': round(chi2(a, b, ka, kb)[0], 2), 'cramers_v': round(chi2(a, b, ka, kb)[1], 3), 'v_ci': ci(vs),
         'cramers_v_bc': round(v_bc(a, b, ka, kb), 3), 'v_bc_ci': ci(vbs),
         'cramers_v_strat': round(float(np.sqrt(x2 / (n * dk))), 3), 'v_strat_ci': ci(vss), 'p': round(float(p), 4)}
    if binary:
        diffs = np.array(diffs)
        r['groups'] = {}
        for j, lv in enumerate(la):
            d = mh(a, yb, st, j)
            r['groups'][lv] = {'n': int((a == j).sum()), 'rate': round(float(yb[a == j].mean()), 3),
                               'n_by_stratum': {sl[k]: int((a[gk] == j).sum()) for k, gk in enumerate(groups)},
                               'rate_by_stratum': {sl[k]: round(float(yb[gk][a[gk] == j].mean()), 3) if (a[gk] == j).any() else None
                                                   for k, gk in enumerate(groups)},
                               'diff_vs_rest': None if np.isnan(d) else round(float(d), 3),
                               'diff_vs_rest_unadjusted': round(float(yb[a == j].mean() - yb[a != j].mean()), 3) if 0 < (a == j).sum() < n else None,
                               'diff_ci': ci(diffs[:, j])}
    else:
        r['groups'] = {lv: {'n': int((a == j).sum()), 'n_by_stratum': {sl[k]: int((a[gk] == j).sum()) for k, gk in enumerate(groups)}}
                       for j, lv in enumerate(la)}
    return r


def aligned_ranks(x, st):
    """Each value's mid-rank within its stratum scaled to (0, 1) by (n_stratum + 1), then ranked over all papers (1-based)."""
    sc = np.empty(len(x))
    for r in np.unique(st):
        m = st == r
        sc[m] = (rank(x[m]) + 1) / (m.sum() + 1)
    return rank(sc) + 1


def numeric_by_group_strat(g, x, s, name):
    """numeric_by_group() with round as a stratum. Values are ranked within round (aligned ranks, so a round that
    scores higher overall does not count as a group effect); Kruskal-Wallis H and epsilon^2 = H / (n - 1) on those
    ranks; p from permuting values within round; bootstrap resamples drawn within round. Group medians are of the raw
    values, pooled and per round."""
    rng = gen(name)
    a, la = codes(g); x = np.asarray(x, float)
    _, st = np.unique(s, return_inverse=True)
    sl = sorted(set(s))
    n, ka, R = len(a), len(la), st.max() + 1
    base = np.argsort(st, kind='stable')
    groups = [np.flatnonzero(st == r) for r in range(R)]
    rx = aligned_ranks(x, st)
    h, e2 = kw(a, ka, rx)
    perm = np.array([kw(a, ka, rx[within_perm(rng, st, base)])[0] for _ in range(NPERM)])
    p = (1 + (perm >= h - 1e-9).sum()) / (NPERM + 1)
    es, meds = [], []
    for _ in range(NBOOT):
        i = within_boot(rng, groups)
        es.append(kw(a[i], ka, aligned_ranks(x[i], st[i]))[1])
        meds.append([np.median(x[i][a[i] == j]) if (a[i] == j).any() else np.nan for j in range(ka)])
    meds = np.array(meds)
    return {'n': n, 'n_by_stratum': {sl[k]: len(gk) for k, gk in enumerate(groups)}, 'stratified_by': 'round',
            'statistic': 'Kruskal-Wallis H on ranks taken within round', 'H': round(h, 2), 'epsilon2': round(e2, 3),
            'epsilon2_ci': ci(es), 'p': round(float(p), 4),
            'groups': {lv: {'n': int((a == j).sum()), 'median': round(float(np.median(x[a == j])), 3), 'median_ci': ci(meds[:, j]),
                            'median_by_stratum': {sl[k]: round(float(np.median(x[gk][a[gk] == j])), 3) if (a[gk] == j).any() else None
                                                  for k, gk in enumerate(groups)}}
                       for j, lv in enumerate(la)}}


# ---------- composition ----------
def share_table(vals, top=None):
    c = Counter(vals); n = sum(c.values())
    items = c.most_common(top)
    return {'n_distinct': len(c), 'counts': {k: {'n': m, 'share': round(m / n, 3)} for k, m in items}}


def journals(recs):
    c = Counter(r.get('source_id') or clean(r.get('journal')) for r in recs)
    name = {}
    for r in recs:
        name.setdefault(r.get('source_id') or clean(r.get('journal')), clean(r.get('journal')))
    n = sum(c.values()); sh = np.array(list(c.values())) / n if n else np.array([])
    per = np.array(list(c.values()))
    hhi = float((sh ** 2).sum()) if n else None
    return {'papers': n, 'distinct_journals': len(c),
            'papers_per_journal': {'mean': round(float(per.mean()), 2), 'median': float(np.median(per)), 'max': int(per.max()),
                                   'single_paper_journals': int((per == 1).sum())} if n else None,
            'hhi': round(hhi, 4) if hhi is not None else None, 'effective_journals': round(1 / hhi, 1) if hhi else None,
            'top5_share': round(float(np.sort(sh)[::-1][:5].sum()), 3) if n else None,
            'top': [{'journal': name[k], 'n': m, 'share': round(m / n, 3)} for k, m in c.most_common(TOP)]}


def composition(recs):
    if not recs:
        return {'n': 0}
    return {'n': len(recs), 'domain': share_table([r['domain'] for r in recs]), 'field': share_table([r['field'] for r in recs]),
            'subfield': share_table([r['subfield'] for r in recs]),
            'topic': {**share_table([r['topic'] for r in recs], TOP),
                      'hhi': round(float(((np.array(list(Counter(r['topic'] for r in recs).values())) / len(recs)) ** 2).sum()), 4)},
            'family': share_table([r['family'] for r in recs]), 'publisher': share_table([r['publisher'] for r in recs]),
            'ring': share_table([r['ring'] for r in recs]), 'journals': journals(recs)}


def coded_keys(tag, keys):
    folder = CODINGS / tag
    good = {}
    if not folder.is_dir():
        return good
    for k in keys:
        f = folder / f'{k}.json'
        if f.is_file():
            try:
                c = json.loads(f.read_text())
            except Exception:  # noqa: BLE001
                continue
            if not validate(c):
                good[k] = c
    return good


def main():
    pool = load(DERIVED / 'gold' / 'pool.json')
    queue = json.loads(QUEUE.read_text())
    rounds, meta = {}, {}
    for name, sset, calc, tag, first in ROUNDS:
        if not (DERIVED / sset / 'metrics.json').is_file() or not (DERIVED / calc / 'manifest.jsonl').is_file():
            continue
        m = {'g22_' + r['id']: r for r in load(DERIVED / sset / 'metrics.json')}
        drawn = ['g22_' + r['id'] for r in load(DERIVED / sset / 'preselect.json')]
        elig = [json.loads(x)['key'] for x in (DERIVED / calc / 'manifest.jsonl').read_text().splitlines() if x.strip()]
        ok = {e['key'] for e in load(DERIVED / sset / 'eligibility.json') if e.get('eligible')}
        cod = coded_keys(tag, elig)
        rounds[name] = {'first_stage': first, 'tag': tag, 'drawn': drawn, 'eligible': elig,
                        'full_text': [k for k in elig if queue.get(k, {}).get('status') == 'have'], 'coded': sorted(cod),
                        'codings': cod, 'manifest_not_in_eligibility': len(set(elig) - ok)}
        meta.update(m)
    tf = topic_fields({r['topic_id'] for r in pool} | {r['topic_id'] for r in meta.values()})

    def attrs(r):
        f, d = tf.get(r.get('topic_id'), (None, None))
        return {'subfield': r.get('subfield') or 'unknown', 'field': f or 'unknown', 'domain': d or 'unknown',
                'topic': r.get('topic') or 'unknown', 'family': family(r), 'publisher': r.get('publisher') or 'unknown',
                'journal': r.get('journal'), 'source_id': r.get('source_id'), 'ring': r.get('ring') or 'unknown',
                **{o: r.get(o) for o in OUTS}}
    A = {k: attrs(r) for k, r in meta.items()}
    pool_attrs = [attrs(r) for r in pool]
    fam_check = Counter((family(r), (r.get('doi') or '').split('/')[0], r.get('publisher')) for r in pool)

    # ---- 1 composition ----
    comp = {'pool': composition(pool_attrs)}
    for name, R in rounds.items():
        comp[name] = {st: composition([A[k] for k in R[st]]) for st in STAGES}
    if len(rounds) > 1:
        comp['pooled'] = {st: composition([A[k] for R in rounds.values() for k in R[st]]) for st in STAGES}

    # ---- 2 coverage among eligible ----
    rnd = {k: name for name, R in rounds.items() for k in R['eligible']}    # round of each eligible paper (the stratum)
    cov = []
    sets = list(rounds.items())
    if len(rounds) > 1 and all(R['coded'] for R in rounds.values()):
        sets.append(('pooled', {st: [k for R in rounds.values() for k in R[st]] for st in ['eligible', 'full_text', 'coded']}))
    for name, R in sets:
        elig, ft, cd = R['eligible'], set(R['full_text']), set(R['coded'])
        for resp, base, y in [('full_text_among_eligible', elig, lambda k: k in ft), ('coded_among_eligible', elig, lambda k: k in cd),
                              ('coded_among_full_text', [k for k in elig if k in ft], lambda k: k in cd)]:
            ys = [y(k) for k in base]
            if not base or len(set(ys)) < 2:
                cov.append({'set': name, 'response': resp, 'skipped': 'response constant (no codings or all coded)', 'n': len(base)})
                continue
            for var in ['subfield', 'field', 'family', 'publisher']:
                g, pooled = pool_small([A[k][var] for k in base])
                r = (assoc_strat(g, ys, [rnd[k] for k in base], f'cov|{name}|{resp}|{var}') if name == 'pooled'
                     else assoc(g, ys, f'cov|{name}|{resp}|{var}'))
                cov.append({'set': name, 'response': resp, 'variable': var, 'overall_rate': round(float(np.mean(ys)), 3),
                            'pooled_into_other': pooled, **r})
    for name, _ in sets:     # BH within each set (round 1, round 2, pooled with round stratum)
        tested = [r for r in cov if 'p' in r and r['set'] == name]
        for r, q in zip(tested, bh([r['p'] for r in tested])):
            r['q'] = round(float(q), 4)

    # ---- 3 workflows by subfield and family: round 1, round 2, both rounds with round as a stratum ----
    allc = {k: c for R in rounds.values() for k, c in R['codings'].items()}
    keys = sorted(allc)
    F = {k: features(allc[k]) for k in keys}

    def wf_block(ks, prefix, strat):
        """Question-3 tests on papers ks; BH within the block. prefix '' keeps the round-1 generator names of earlier runs."""
        names = sorted({n for k in ks for n in F[k]})
        s = [rnd[k] for k in ks]
        A2 = (lambda g, y, nm: assoc_strat(g, y, s, nm)) if strat else assoc
        N2 = (lambda g, x, nm: numeric_by_group_strat(g, x, s, nm)) if strat else numeric_by_group
        wf, groupings = [], {}
        for var in ['subfield', 'family']:
            g, pooled = pool_small([A[k][var] for k in ks])
            groupings[var] = {'groups': dict(Counter(g)), 'pooled_into_other': pooled}
            for nm in names:
                vals = [F[k].get(nm, False) for k in ks]
                if nm.startswith('bin:'):
                    if not (MIN_FEATURE <= sum(vals) <= len(vals) - MIN_FEATURE):
                        continue
                    r = A2(g, [bool(v) for v in vals], f'wf|{prefix}{var}|{nm}')
                    wf.append({'grouping': var, 'feature': nm[4:], 'kind': 'binary', 'prevalence': round(float(np.mean(vals)), 3), **r})
                else:
                    r = N2(g, [float(v) for v in vals], f'wf|{prefix}{var}|{nm}')
                    wf.append({'grouping': var, 'feature': nm[4:], 'kind': 'count', **r})
            for whole in ['entry', 'decisive', 'composition']:
                lv = [next((n.split(' ', 1)[1] for n in F[k] if n.startswith(f'bin:{whole} ')), 'none') for k in ks]
                lv, lp = pool_small(lv)
                r = A2(g, lv, f'wf|{prefix}{var}|whole {whole}')
                wf.append({'grouping': var, 'feature': f'{whole} (whole variable)', 'kind': 'categorical', 'levels_pooled': lp, **r})
        for r, q in zip(wf, bh([r['p'] for r in wf])):
            r['q'] = round(float(q), 4)
        return {'papers': 'round 1' if prefix == '' else prefix.rstrip('|').replace('_', ' '),
                'stratified_by_round': strat, 'n_papers': len(ks),
                'n_by_round': dict(Counter(rnd[k] for k in ks)), 'groupings': groupings, 'tests': len(wf),
                'q_below_0.1': sum(r['q'] < 0.1 for r in wf), 'rows': wf}

    def oc_block(pops, prefix, strat):
        oc = []
        for pop, ks in pops:
            for var in ['subfield', 'family']:
                for o in OUTS:
                    kk = [k for k in ks if A[k][o] is not None]
                    g, pooled = pool_small([A[k][var] for k in kk])
                    x = [A[k][o] for k in kk]
                    nm = f'oc|{prefix}{pop}|{var}|{o}'
                    r = numeric_by_group_strat(g, x, [rnd[k] for k in kk], nm) if strat else numeric_by_group(g, x, nm)
                    oc.append({'population': pop, 'grouping': var, 'outcome': o, 'field_normalized': NORMALIZED[o],
                               'overall_median': round(float(np.median(x)), 3), 'pooled_into_other': pooled, **r})
        for r, q in zip(oc, bh([r['p'] for r in oc])):
            r['q'] = round(float(q), 4)
        return {'papers': 'round 1' if prefix == '' else prefix.rstrip('|').replace('_', ' '),
                'stratified_by_round': strat, 'tests': len(oc), 'q_below_0.1': sum(r['q'] < 0.1 for r in oc), 'rows': oc}

    blocks = [(name, '' if name == 'round1' else f'{name}|', False, R['coded'], R['eligible'])
              for name, R in rounds.items() if R['coded']]
    if len(blocks) > 1:
        blocks.append(('pooled_stratified', 'pooled_stratified|', True, keys, [k for R in rounds.values() for k in R['eligible']]))
    WF = {b: wf_block(ks, pre, strat) for b, pre, strat, ks, _ in blocks}
    OC = {b: oc_block([('coded', ks), ('eligible', el)], pre, strat) for b, pre, strat, ks, el in blocks}
    wf1, oc1 = WF['round1'], OC['round1']
    wf, groupings = wf1['rows'], wf1['groupings']
    oc = oc1['rows']

    # ---- 5 confounding check of g17 associations (round 1, the g17 paper set) ----
    g17 = load(DERIVED / 'outcomes' / 'outcomes.json')
    sig = [r for r in g17['rows'] if r['q'] < 0.1]
    c1 = rounds['round1']['codings']
    met1 = {k: r for k, r in meta.items() if k in {'g22_' + x['id'] for x in load(DERIVED / 'gold' / 'metrics.json')}}
    k1 = sorted(k for k in c1 if k in met1)      # g17 takes every valid calc1 coding with metrics; these are all in the manifest
    F1 = {k: F[k] for k in k1}
    conf = []
    for r in sig:
        o, nm = r['outcome'], ('bin:' if r['type'] == 'bin' else 'num:') + r['feature']
        kk = [k for k in k1 if met1[k].get(o) is not None and (o != 'breadth_citers' or (met1[k].get('n_citers_noself') or 0) >= 10)]
        f = [float(F1[k].get(nm, False)) for k in kk]
        y = [met1[k][o] for k in kk]
        row = {'feature': r['feature'], 'type': r['type'], 'outcome': o, 'field_normalized': NORMALIZED.get(o, False),
               'g17_rho': r['rho'], 'g17_ci': r['ci'], 'g17_q': r['q'], 'g17_n': r['n'], 'n_now': len(kk),
               'rho_now': round(spearman(f, y), 3), 'strata': {}}
        for sname, sf in [('subfield', lambda k: A[k]['subfield']), ('family', lambda k: A[k]['family']),
                          ('subfield x family', lambda k: A[k]['subfield'] + ' | ' + A[k]['family'])]:
            row['strata'][sname] = stratified(f, y, [sf(k) for k in kk], f'conf|{nm}|{o}|{sname}')
        conf.append(row)
    flat = [(row, s) for row in conf for s, v in row['strata'].items() if v]
    for (row, s), q in zip(flat, bh([row['strata'][s]['p'] for row, s in flat])):
        v = row['strata'][s]
        v['q'] = round(float(q), 4)
        v['attenuation'] = round(v['rho_within'] / row['rho_now'], 2) if row['rho_now'] else None
        v['survives'] = bool(np.sign(v['rho_within']) == np.sign(row['g17_rho']) and v['q'] < 0.1)
        v['ci_excludes_zero'] = bool(v['ci'] and (v['ci'][0] > 0 or v['ci'][1] < 0))
    surv = {s: sum(row['strata'][s]['survives'] for row in conf if row['strata'][s]) for s in ['subfield', 'family', 'subfield x family']}
    surv_ci = {s: sum(row['strata'][s]['survives'] and row['strata'][s]['ci_excludes_zero'] for row in conf if row['strata'][s])
               for s in ['subfield', 'family', 'subfield x family']}

    # ---- 6 what the OpenAlex subfields hold: leading topics and ring per subfield; ML vocabulary in the codings ----
    sub_topics = {}
    for stage, ks in [('pool', None), ('round1_drawn', rounds['round1']['drawn']), ('coded', keys)]:
        recs = pool_attrs if ks is None else [A[k] for k in ks]
        by = {}
        for r in recs:
            by.setdefault(r['subfield'], []).append(r)
        sub_topics[stage] = {sf: {'n': len(rr), 'top_topics': [{'topic': t, 'n': m, 'share': round(m / len(rr), 3)}
                                                               for t, m in Counter(r['topic'] for r in rr).most_common(3)],
                                  'ring': dict(Counter(r['ring'] for r in rr))}
                             for sf, rr in sorted(by.items(), key=lambda x: -len(x[1]))}
    ml = {}
    for k in keys:
        c = allc[k]
        steps = next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps']
        txt = ' '.join([f"{i.get('item', '')} {i.get('field', '')}" for i in c.get('imports', [])] + [s.get('action', '') for s in steps]
                       + [c['decisive_move'].get('sentence', '')])
        ntxt = ' '.join(s.get('action', '') for s in steps if s['node'] == 'N')
        g = A[k]['subfield']
        d = ml.setdefault(g, Counter())
        d['papers'] += 1
        d['ml_terms_anywhere'] += bool(ML_TERMS.search(txt))
        d['ml_terms_in_an_N_step'] += bool(ML_TERMS.search(ntxt))
        d['decisive_methods'] += c['decisive_move']['mode'] == 'methods'
    ml = {g: dict(v) for g, v in sorted(ml.items(), key=lambda x: -x[1]['papers'])}

    n = {name: {st: len(R[st]) for st in STAGES} | {'coding_tag': R['tag'], 'first_stage_label': R['first_stage'],
                                                    'manifest_not_in_eligibility': R['manifest_not_in_eligibility']}
         for name, R in rounds.items()}
    n['pool'] = len(pool)
    n['round2_codings_present'] = (CODINGS / 'r2').is_dir()
    n['coded_pooled'] = len(keys)
    n['g17_set_now'] = len(k1)
    res = {'n': n, 'composition': comp,
           'family_rule': {'rules': [list(x) for x in FAMILY_RULES], 'fallback': 'other',
                           'pool_check': [{'family': f, 'doi_prefix': p, 'publisher': pb, 'n': m} for (f, p, pb), m in fam_check.most_common()]},
           'topics_mapped': {'leading_topics': len(tf), 'unmapped_in_corpus': sorted({r['topic_id'] for r in meta.values()} - set(tf))},
           'coverage': cov,
           # top-level rows, groupings, n_papers, tests, q_below_0.1: round 1 alone (as before); by_round and
           # pooled_stratified hold the same structure for each round alone and for both rounds with round as a stratum
           'workflows': {**wf1, 'by_round': {b: WF[b] for b in WF if b != 'pooled_stratified'},
                         'pooled_stratified': WF.get('pooled_stratified')},
           'outcomes_by_group': {**oc1, 'by_round': {b: OC[b] for b in OC if b != 'pooled_stratified'},
                                 'pooled_stratified': OC.get('pooled_stratified')},
           'subfield_topics': sub_topics,
           'ml_terms_check': {'pattern': ML_TERMS.pattern, 'by_subfield': ml,
                              'note': 'coded papers (rounds pooled): codings whose imports, final-paper step actions or decisive '
                                      'sentence match the pattern, and those with an N (new capability) step whose action matches'},
           'confounding': {'g17_rows_rechecked': len(conf), 'survivors': surv, 'survivors_ci_excludes_zero': surv_ci, 'rows': conf},
           'params': {'MIN_GROUP': MIN_GROUP, 'MIN_FEATURE': MIN_FEATURE, 'NBOOT': NBOOT, 'NPERM': NPERM, 'SEED': SEED},
           'note': 'exploratory; BH q within each question; effect sizes with 95% percentile bootstrap intervals; aggregates only'}
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / 'topics_journals.json', res,
               ['derived/gold/{pool,preselect,metrics,eligibility}.json', 'derived/r2/{preselect,metrics,eligibility}.json',
                'derived/calc1/manifest.jsonl', 'derived/r2calc/manifest.jsonl', 'private/download-queue.json',
                'private/analysis/codings/api/{calc1,r2}', 'derived/outcomes/outcomes.json', 'OpenAlex /topics'], res['params'])
    md = report(res, rounds)
    (OUT / 'TOPICS.md').write_text(md)
    log('g20_topics_journals.py', 'topics, fields and journals by stage; coverage bias; workflows and outcomes by field and venue; g17 confounding',
        len(keys), f"r1 coded {n['round1']['coded']}, r2 coded {n.get('round2', {}).get('coded', 0)}; workflow tests q<0.1 "
                   + ', '.join(f"{b} {W['q_below_0.1']}/{W['tests']}" for b, W in WF.items()) + f"; g17 survivors {surv}")
    print(md)


def fmt_ci(c):
    return f'[{c[0]}, {c[1]}]' if c else '[n/a]'


def report(res, rounds):
    n, comp = res['n'], res['composition']
    r1, r2 = n.get('round1', {}), n.get('round2', {})
    md = ['# Paper topics and journals in the roadmap corpus', '',
          f"Run on {len(rounds)} round(s). Coded papers at run time: round 1 {r1.get('coded', 0)} (tag calc1), round 2 "
          f"{r2.get('coded', 0)} (tag r2{'' if n['round2_codings_present'] else ', folder absent'}). Pool frame {n['pool']} papers. "
          'Script tools/roadmap/g20_topics_journals.py; all numbers in topics_journals.json beside this file.', '',
          '## How to read this', '',
          '- **OpenAlex topic, subfield, field, domain.** OpenAlex assigns each paper a leading topic by a classifier over title, '
          'abstract, venue and citations; topics nest in subfields, fields and domains (for example Seismic Imaging and Inversion '
          'Techniques < Geophysics < Earth and Planetary Sciences < Physical Sciences). These are machine labels, not author keywords.',
          '- **Journal family.** Publisher group from DOI prefix, then publisher, then journal name (rule in the script docstring). '
          'AGU journals form their own family even though Wiley publishes them.',
          '- **Herfindahl index (HHI).** Sum of squared journal shares; 1/HHI is the number of equally sized journals that would give '
          'the same concentration.',
          "- **Cramer's V.** Strength of association between two categorical variables, 0 (independent) to 1 (one determines the "
          'other). Plain V is biased upward when cells are small; the tables report the bias-corrected V (Bergsma 2013), which '
          'subtracts the value expected under independence, with a 95% bootstrap interval. The json has both.',
          '- **Rate difference.** Share of papers with a property in one category minus the share in all other categories.',
          '- **Kruskal-Wallis epsilon squared.** Share of rank variance in a count or outcome explained by the grouping, 0 to 1.',
          '- **Permutation p.** Share of label shuffles giving an association at least as strong as observed. '
          '**BH q** (Benjamini-Hochberg) adjusts p for the number of tests within a question; q < 0.1 means at most about 10% of '
          'such findings are expected to be false positives.',
          '- **Outcome metrics.** cnp: OpenAlex citation-normalized percentile, the paper\'s citation count as a percentile among '
          'works of the same OpenAlex subfield, year and type (0-1). fwci: field-weighted citation impact, citations divided by the mean for '
          'works of the same subfield, year and type (1 = world average; citations are skewed, so the median paper sits below 1). novelty_pair: -log10(1 + number of 2017-2021 works sharing the paper\'s leading pair of '
          'OpenAlex topics); higher means a rarer combination. breadth_refs: share of the paper\'s classified references outside '
          'geoscience. cnp and fwci are already subfield-normalized by OpenAlex; novelty_pair and breadth_refs are not, so differences '
          'between subfields in those two are expected from field structure alone.',
          '- **Within-stratum rank correlation.** Spearman correlation computed after centring both ranks within each subfield (or '
          'family); only co-variation inside a stratum counts. Its p comes from shuffling outcomes within strata only.', '']

    md += ['## 1. Composition by stage', '', '| Set | Stage | Papers | Distinct journals | HHI | Effective journals | Top-5 share | Distinct topics |',
           '|:--|:--|--:|--:|--:|--:|--:|--:|']
    rows = [('pool', 'pool', comp['pool'])] + [(s, st, comp[s][st]) for s in comp if s != 'pool' for st in STAGES]
    for s, st, c in rows:
        if c.get('n'):
            j = c['journals']
            md.append(f"| {s} | {st} | {c['n']} | {j['distinct_journals']} | {j['hhi']} | {j['effective_journals']} | {j['top5_share']} | {c['topic']['n_distinct']} |")
    for var in ['field', 'subfield', 'family']:
        md += ['', f'### {var.capitalize()} by stage', '']
        st1 = comp.get('round1', {})
        lv = list(comp['pool'][var]['counts'])
        for st in STAGES:
            for k in st1.get(st, {}).get(var, {}).get('counts', {}):
                if k not in lv:
                    lv.append(k)
        for st in STAGES:
            for k in comp.get('round2', {}).get(st, {}).get(var, {}).get('counts', {}):
                if k not in lv:
                    lv.append(k)
        md += ['| ' + var + ' | pool share | ' + ' | '.join('round 1 ' + st for st in STAGES) + ' | '
               + ' | '.join('round 2 ' + st for st in STAGES) + ' |',
               '|:--|' + '--:|' * (2 * len(STAGES) + 1)]
        for k in lv:
            cells = [comp['pool'][var]['counts'].get(k, {}).get('share', 0)]
            cells += [st1.get(st, {}).get(var, {}).get('counts', {}).get(k, {}).get('n', 0) for st in STAGES]
            cells += [comp.get('round2', {}).get(st, {}).get(var, {}).get('counts', {}).get(k, {}).get('n', 0) for st in STAGES]
            md.append(f'| {k} | {cells[0]:.3f} | ' + ' | '.join(str(x) for x in cells[1:]) + ' |')
    md += ['', 'Pool column is a share; other columns are counts.', '', '### Most frequent journals (coded, all rounds)', '']
    cj = (comp.get('pooled') or comp['round1'])['coded']['journals']
    md += ['| Journal | Papers | Share |', '|:--|--:|--:|'] + [f"| {t['journal']} | {t['n']} | {t['share']} |" for t in cj['top']]
    md += ['', '### Most frequent leading topics (coded, all rounds) and their share at earlier stages', '',
           '| Topic | Coded papers | Coded share | Pool share | Round 1 preselected share | Round 1 eligible share | Round 1 full-text share |',
           '|:--|--:|--:|--:|--:|--:|--:|']
    sh = lambda c, k: c['topic']['counts'].get(k, {}).get('share', '<top 15')
    for k, v in (comp.get('pooled') or comp['round1'])['coded']['topic']['counts'].items():
        md.append(f"| {k} | {v['n']} | {v['share']} | {sh(comp['pool'], k)} | {sh(comp['round1']['drawn'], k)} | "
                  f"{sh(comp['round1']['eligible'], k)} | {sh(comp['round1']['full_text'], k)} |")

    md += ['', '## 2. Coverage bias', '', 'Among eligible papers, is reaching full text, or being coded, associated with field or venue? '
           f'Categories with fewer than {MIN_GROUP} eligible papers are pooled into "{POOLED}". Set "pooled" is both rounds '
           'with round as a stratum: the statistic sums the within-round chi-squares, coverage labels are shuffled within '
           'round, and the rate difference is the Mantel-Haenszel weighted mean of the within-round differences. BH q is '
           'computed within each set.', '',
           "| Set | Response | Variable | n | Overall rate | Cramer's V, bias-corrected [95% CI] | p | q | Largest rate difference (category) |",
           '|:--|:--|:--|--:|--:|:--|--:|--:|:--|']
    for r in res['coverage']:
        if 'p' not in r:
            md.append(f"| {r['set']} | {r['response']} | (skipped: {r['skipped']}) | {r['n']} | | | | | |")
            continue
        big = max(((g, v) for g, v in r['groups'].items() if v.get('diff_vs_rest') is not None), key=lambda x: abs(x[1]['diff_vs_rest']), default=None)
        bs = f"{big[1]['diff_vs_rest']:+.2f} {fmt_ci(big[1]['diff_ci'])} ({big[0]}, n={big[1]['n']})" if big else ''
        md.append(f"| {r['set']} | {r['response']} | {r['variable']} | {r['n']} | {r['overall_rate']} | {r['cramers_v_bc']} {fmt_ci(r['v_bc_ci'])} | {r['p']} | {r['q']} | {bs} |")

    w = res['workflows']
    blocks = [('round1', 'Round 1 alone (exploratory)', w)] + \
             [(b, 'Round 2 alone', W) for b, W in w['by_round'].items() if b != 'round1'] + \
             ([('pooled_stratified', 'Both rounds, round as a stratum', w['pooled_stratified'])] if w.get('pooled_stratified') else [])
    md += ['', '## 3. Workflows by field and venue', '',
           'Each test is run three ways: round 1 alone, round 2 alone, and both rounds with round as a stratum. In the '
           'stratified version the feature is shuffled within round only, so a difference between the rounds in field mix '
           'or in coding cannot pass for a field or venue effect. Binary and categorical features: statistic = sum of the '
           'within-round chi-squares; effect = bias-corrected Cramer\'s V of the pooled table; rate difference = '
           'Mantel-Haenszel weighted mean of the within-round differences (weight n_group n_rest / n_round). Counts: '
           'Kruskal-Wallis H on ranks taken within round (aligned ranks), epsilon squared = H / (n - 1); group medians are '
           'of the raw values. Bootstrap resamples are drawn within round. BH q is computed within each block. The round-2 '
           'confirmatory test of the round-1 associations is a separate analysis (tools/roadmap/g23_confirmatory.py, '
           'derived/confirmatory/CONFIRMATORY.md) and is not repeated here.', '']
    eff = lambda r: r.get('cramers_v_bc', r.get('epsilon2'))
    for b, title, W in blocks:
        md += [f'### 3.{blocks.index((b, title, W)) + 1} {title}', '',
               f"{W['n_papers']} coded papers ({', '.join(f'{k} {v}' for k, v in W['n_by_round'].items())}). "
               f"{W['tests']} tests, {W['q_below_0.1']} with q < 0.1.", '']
        for var, gi in W['groupings'].items():
            md.append(f"- {var}: groups " + ', '.join(f'{k} ({v})' for k, v in sorted(gi['groups'].items(), key=lambda x: -x[1]))
                      + (f'; pooled into "{POOLED}": ' + ', '.join(f'{k} ({v})' for k, v in gi['pooled_into_other'].items()) if gi['pooled_into_other'] else ''))
        md += ['', "Tests with q < 0.1. Effect: bias-corrected Cramer's V for binary and categorical features, epsilon squared for counts.", '',
               '| Grouping | Feature | Kind | Effect [95% CI] | p | q | Largest rate difference or group medians |', '|:--|:--|:--|:--|--:|--:|:--|']
        for r in sorted([r for r in W['rows'] if r['q'] < 0.1], key=lambda r: (r['kind'] == 'count', -eff(r))):
            e = f"V {r['cramers_v_bc']} {fmt_ci(r['v_bc_ci'])}" if 'cramers_v_bc' in r else f"eps2 {r['epsilon2']} {fmt_ci(r['epsilon2_ci'])}"
            big = ''
            if r['kind'] == 'binary':
                g, v = max(((g, v) for g, v in r['groups'].items() if v.get('diff_vs_rest') is not None), key=lambda x: abs(x[1]['diff_vs_rest']))
                big = f"{v['diff_vs_rest']:+.2f} {fmt_ci(v['diff_ci'])} ({g}, rate {v['rate']}, n={v['n']})"
            elif r['kind'] == 'count':
                big = ', '.join(f"{g} {v['median']:g}" for g, v in sorted(r['groups'].items(), key=lambda x: -x[1]['median']))
            md.append(f"| {r['grouping']} | {r['feature']} | {r['kind']} | {e} | {r['p']} | {r['q']} | {big} |")
        md.append('')
    if len(blocks) > 1:
        idx = {b: {(r['grouping'], r['feature']): r for r in W['rows']} for b, _, W in blocks}
        hit = sorted({k for b in idx for k, r in idx[b].items() if r['q'] < 0.1})
        md += ['### 3.4 The three blocks side by side', '',
               'Every test with q < 0.1 in at least one block. Cell: effect, q; "n.t." = not tested in that block (binary '
               f'feature present in fewer than {MIN_FEATURE} or more than n - {MIN_FEATURE} papers).', '',
               '| Grouping | Feature | ' + ' | '.join(t for _, t, _ in blocks) + ' |', '|:--|:--|' + ':--|' * len(blocks)]
        for k in hit:
            md.append(f'| {k[0]} | {k[1]} | ' + ' | '.join(
                (f"{eff(idx[b][k])}, q {idx[b][k]['q']}" + (' *' if idx[b][k]['q'] < 0.1 else '')) if k in idx[b] else 'n.t.'
                for b, _, _ in blocks) + ' |')
        md += ['', '\\* q < 0.1.', '']

    md += ['', '## 4. Outcomes by field and venue', '', 'Round 1 alone (the top-level rows of outcomes_by_group). Median per group '
           '[95% bootstrap CI]. Last row: Kruskal-Wallis epsilon squared '
           '[95% CI] and BH q. cnp and fwci are subfield-normalized by OpenAlex; novelty_pair and breadth_refs are not. '
           'Section 4.5 compares round 1, round 2 and both rounds with round as a stratum.']
    rows4 = res['outcomes_by_group']['rows']
    for pop in ['coded', 'eligible']:
        for var in ['subfield', 'family']:
            rr = {r['outcome']: r for r in rows4 if r['population'] == pop and r['grouping'] == var}
            if not rr:
                continue
            md += ['', f'### {pop.capitalize()} papers by {var}', '', f'| {var} | n | ' + ' | '.join(OUTS) + ' |', '|:--|--:|' + ':--|' * len(OUTS)]
            groups = sorted(rr[OUTS[0]]['groups'], key=lambda g: -rr[OUTS[0]]['groups'][g]['n'])
            for g in groups:
                md.append(f"| {g} | {rr[OUTS[0]]['groups'][g]['n']} | " + ' | '.join(
                    f"{rr[o]['groups'][g]['median']} {fmt_ci(rr[o]['groups'][g]['median_ci'])}" if g in rr[o]['groups'] else '' for o in OUTS) + ' |')
            md.append('| all | ' + str(rr[OUTS[0]]['n']) + ' | ' + ' | '.join(f"{rr[o]['overall_median']}" for o in OUTS) + ' |')
            md.append('| eps2, q | | ' + ' | '.join(f"{rr[o]['epsilon2']} {fmt_ci(rr[o]['epsilon2_ci'])}, q {rr[o]['q']}" for o in OUTS) + ' |')
    ob = res['outcomes_by_group']
    oblocks = [('round1', 'Round 1', ob)] + [(b, 'Round 2', O) for b, O in ob['by_round'].items() if b != 'round1'] + \
              ([('pooled_stratified', 'Both rounds, round stratum', ob['pooled_stratified'])] if ob.get('pooled_stratified') else [])
    if len(oblocks) > 1:
        oi = {b: {(r['population'], r['grouping'], r['outcome']): r for r in O['rows']} for b, _, O in oblocks}
        md += ['', '### 4.5 Round 1, round 2 and both rounds with round as a stratum', '',
               'Cell: n, Kruskal-Wallis epsilon squared [95% CI], BH q within the block. Stratified block: values ranked '
               'within round, shuffled within round, resampled within round.', '',
               '| Population | Grouping | Outcome | ' + ' | '.join(t for _, t, _ in oblocks) + ' |', '|:--|:--|:--|' + ':--|' * len(oblocks)]
        for k in oi['round1']:
            md.append(f'| {k[0]} | {k[1]} | {k[2]} | ' + ' | '.join(
                (f"n {oi[b][k]['n']}, {oi[b][k]['epsilon2']} {fmt_ci(oi[b][k]['epsilon2_ci'])}, q {oi[b][k]['q']}"
                 + (' *' if oi[b][k]['q'] < 0.1 else '')) if k in oi[b] else '' for b, _, _ in oblocks) + ' |')
        md += ['', '\\* q < 0.1.']

    c = res['confounding']
    md += ['', '## 5. Are the g17 workflow-outcome associations explained by field or venue?', '',
           f"{c['g17_rows_rechecked']} g17 tests with q < 0.1 (round 1, tools/roadmap/g17_outcomes.py output) rechecked on the "
           f"{n['g17_set_now']} round-1 papers coded now. Survivors (same sign, q < 0.1 over the {sum(len([v for v in r['strata'].values() if v]) for r in c['rows'])} "
           f"stratified tests): " + ', '.join(f'{k} {v}/{c["g17_rows_rechecked"]}' for k, v in c['survivors'].items())
           + '; of these, with a bootstrap interval that excludes 0: ' + ', '.join(f'{k} {v}' for k, v in c['survivors_ci_excludes_zero'].items()) + '.', '',
           '| Feature | Outcome | g17 rho | rho now | within subfield [CI], q | within family [CI], q | within subfield x family [CI], q |',
           '|:--|:--|--:|--:|:--|:--|:--|']
    for r in c['rows']:
        cell = lambda v: (f"{v['rho_within']} {fmt_ci(v['ci'])}, {v['q']}" + (' survives' if v['survives'] and v['ci_excludes_zero'] else
                          ' survives, CI spans 0' if v['survives'] else ' does not survive') if v else 'n/a')
        md.append(f"| {r['feature']} | {r['outcome']}{'' if r['field_normalized'] else ' (not normalized)'} | {r['g17_rho']} | {r['rho_now']} | "
                  f"{cell(r['strata']['subfield'])} | {cell(r['strata']['family'])} | {cell(r['strata']['subfield x family'])} |")
    md += ['', '"Survives" means the association keeps its sign and has q < 0.1 within strata. "CI spans 0" marks a survivor whose '
           'stratified bootstrap interval includes 0: weakened, not removed.', '']
    md += ['## 6. What the OpenAlex subfields hold', '',
           'Leading topics and ring per subfield. Core ring: the convenor\'s 8 OpenAlex topics; broad ring: 8 Earth-science subfields '
           '(DECISIONS.md, g02). A subfield named for another discipline can hold geoscience topics: OpenAlex files the topic, not the paper.', '',
           '| Subfield | Pool n | Round 1 preselected n (ring) | Top topics, round 1 preselected | Coded n | Top topic, coded |', '|:--|--:|:--|:--|--:|:--|']
    stp = res['subfield_topics']
    for sf, v in stp['round1_drawn'].items():
        pl = stp['pool'].get(sf, {}).get('n', 0)
        cd = stp['coded'].get(sf, {})
        tt = '; '.join(f"{t['topic']} {t['n']}" for t in v['top_topics'])
        ct = (cd.get('top_topics') or [{}])[0]
        md.append(f"| {sf} | {pl} | {v['n']} ({', '.join(f'{k} {m}' for k, m in v['ring'].items())}) | {tt} | {cd.get('n', 0)} | "
                  + (f"{ct['topic']} {ct['n']} ({round(100 * ct['share'])}%)" if ct else '') + ' |')
    mlc = res['ml_terms_check']['by_subfield']
    md += ['', 'Machine-learning vocabulary in the codings (coded papers): ' + '; '.join(
        f"{g} {v['ml_terms_anywhere']} of {v['papers']} anywhere, {v['ml_terms_in_an_N_step']} in an N step" for g, v in mlc.items()) + '.', '']
    return '\n'.join(md) + '\n'


if __name__ == '__main__':
    main()
