"""Scientific advance, the primary outcome on rubrics.qmd, from the blind model coder: pilot report, preregistered plan, test.

Decided by the PI on October 27, 2026: measure advance ("a meaningful warranted improvement in knowledge, understanding,
or research capability") for every coded paper (round 1, tag calc1, 374 valid inquiry codings; round 2, tag r2, 198)
with claude-opus-5-5 under agents/advance/RUBRIC.md, blind to venue, authors and citations; budget $400 in total, of
which $221.59 was spent before the advance pilot. Paid calls run through tools/code_papers.py --task advance, never
from this script. What the coder measures is reported warrant (RUBRIC.md header); until the validation gate below
passes, results are reported as the model's judgment of reported warrant, not as advance.

pick    Helper, before the pilot. 20 papers with a valid inquiry coding, none of the 100 gold-set papers, 4 per
        archetype: hazard or forecast (title vocabulary), methods (claim status capability_characterized),
        reconstruction (composition trace_series), observational (composition natures_repetition or claim status
        regularity_in_range), model or mechanism (claim status best_explanation); within an archetype, alternately
        XML and PDF text routes. Each slot takes, among the papers of its archetype and route, the one whose
        OpenAlex subfield and then round are furthest below their share of the pool (proportional allocation over
        the 20 slots), ties broken by a permutation from default_rng(2029). A paper goes to the first archetype it
        fits in that order. Writes derived/advance/pilot_keys.json and prints the --keys list. Papers with a known
        later correction or failed replication cannot be found from the data here; swap 2 or 3 in by hand if known.
pilot   Reads the two pilot tags (pilot-a-advance, pilot-b-advance: the same papers coded twice under the same rubric,
        submitted as --tag pilot-a / pilot-b --task advance) and reports
          test-retest   verdict: Krippendorff alpha (nominal), raw agreement, prevalence; advance_score: alpha
                        (ordinal), quadratic-weighted kappa, exact and within-1 agreement (pairs with both scores);
                        criteria M1-W4 of G1: alpha (nominal) and agreement; roles: mean Jaccard and per-role alpha;
                        novelty judgment_with_coder_knowledge: alpha (nominal); novelty_score: alpha (ordinal) and
                        weighted kappa; impact_forecast: alpha (ordinal, no_forecast excluded); 95% bootstrap
                        intervals (1000 resamples of papers) for the verdict and score alphas. n = 20 gives intervals of
                        roughly +/- 0.2 to 0.3.
          distributions verdict, unassessable condition, score, novelty score, criterion met rates, magnitude_form,
                        evidence_access, rival_test, verdict_basis origin; a distribution is flagged degenerate when one
                        class holds at least 70% of codings (revise anchors before freezing); use of scores 1 and 5
          strata        verdict by text route (xml, pdftotext); not-quantifiable rate, U2 rate, low-confidence rate and
                        median score by OpenAlex subfield; score by basis gain type
          leakage       residual leakage after blinding (tools/blind_text.py leakage_after, information fields excluded)
                        for the pilot papers; blind_leak_noticed and post_2022_knowledge_flag rates (self-report)
          validator     unmatched quotes, locator mismatches, evidence or verdict quotes from restating parts
                        (tools/check_advance.py); invalid codings in <tag>/_invalid
          cost          recorded spend per tag over every returned result (state.json 'spent'), per valid coding;
                        output tokens median, 90th and 99th percentile, recommended max_tokens (99th percentile plus
                        10%, rounded up to 1,000); projected full-run cost for 572 papers against the remaining budget
          verbosity     Spearman rho of advance_score with paper words and with the coder's output tokens
        Writes derived/advance/pilot.json.
freeze  Refuses when any full-run advance coding exists (a folder <tag>-advance under private/analysis/codings/api/
        whose tag does not start with 'pilot' holding a coding, valid or invalid). Writes the public plan
        preregistration/advance-plan.{json,md}: rubric version and sha256 (with schema, validator, blinding and this
        script), pilot.json sha256 and the pilot keys, the full-run tag, model, effort and max_tokens, outcome
        definitions, the hypotheses H1-H9 below with predicted directions, the test rule, exclusions, covariates,
        the shared-method statement, the expected achieved rate (pilot rate with a Wilson 95% interval), and the
        validation gate. Run by the parent after the pilot, then commit and push before the full run.
        Outcomes
          primary     achieved (1) versus not (0): not_demonstrated and unassessable U1, U2, U3, U5 count as 0 and stay
                      in the denominator; U4 (screen failure) is excluded and reported
          primary-W3  achieved with W3 ignored (some gain meets M1, M2, W1, W2, W4): the outcome for predictors built
                      from validation checks, so a V-check feature is never tested against W3, which measures the same
                      construct in the same text
          secondary   advance_score 1-5 (ordinal; papers with a score, i.e. achieved or not_demonstrated);
                      novelty_score 1-5; roles (presence of each role among assessable papers)
        Hypotheses (feature from the round's inquiry coding, tools/roadmap/g17_outcomes.py features(); predicted sign)
          H1  triangulation (checks of two or more of replication, method, generalization performed here) -> primary-W3, +
          H2  number of kinds of V check performed here -> primary-W3, +
          H3  claim gate yes (the claim faced a test it could fail) -> primary, +
          H4  claim gate yes -> advance_score, +
          H5  action gate yes or partly (a stated hypothesis directed the key data acquisition) -> primary, +
          H6  outcome contradicted -> role corrective, +
          H7  composition capability_first -> role enabling, +
          H8  number of fields imported from -> role integrative, +
          H9  any return after failure -> advance_score, +
        Calibration checks (reported, outside the family): C1 impact_forecast (1-4, no_forecast excluded) against the
        OpenAlex citation percentile cnp, +; C2 advance_score against cnp, + (advance and impact are distinct, so a
        weak positive association is expected and a strong one would suggest the coder reads impact).
        Rule  one family of 9 tests. Spearman rho within strata (round x OpenAlex subfield; subfields with fewer than
              10 papers in the test population pooled within round), two-sided permutation p with the outcome shuffled
              within strata (tools/roadmap/g20_topics_journals.py stratified(): 5000 permutations, 2000 bootstrap
              resamples, generator named 'advance|<id>'); Benjamini-Hochberg q over the 9 p values. Supported when
              q < 0.1 and the sign is the predicted one; reversed when q < 0.1 and the sign is opposite; otherwise not
              supported. A binary feature present in fewer than 10 or more than n - 10 papers of the test population
              is not testable (p = 1, kept in the family).
        Exclusions  the pilot papers; papers without a valid advance coding under the full-run tag, a valid inquiry
              coding (calc1 or r2) or round metrics; U4 papers (reported). Unassessable U1-U3, U5 are kept as 0 in the
              primary outcomes and reported.
        Sensitivity (reported, not part of the rule): plain Spearman; partial Spearman controlling for log paper
              words, text route and the number of reported checks; primary with out-of-taxonomy awards removed; every
              hypothesis against primary-W3.
        Validation gate (40 human-rated gold papers, two raters each, tools/roadmap/g11_human_agreement.py layout):
              (1) human-human alpha (ordinal) on advance score >= 0.667, and alpha (nominal) on the verdict once the
              human instrument records one (ratings v1.1.0); (2) model-human alpha, with the model swapped in for each
              human in turn, at least the human-human alpha minus 0.10; (3) mean model-minus-human score within +/- 0.5
              (Wilcoxon signed-rank, sign-flip permutation); (4) with human verdicts, the model's sensitivity and
              specificity for achieved and a Rogan-Gladen corrected success fraction. Until (1)-(3) pass, results are
              labelled model judgment of reported warrant.
test    Runs the frozen plan on the full-run tag (refuses if RUBRIC.md, the schema or the validator changed since the
        freeze) and writes derived/advance/{results.json, ADVANCE.md}: success fraction with all three verdict counts
        (overall, by round, by subfield, by text route; with and without out-of-taxonomy awards), U4 count, the 9
        tests with q and verdicts, sensitivities, calibration checks, and the validation gate status.

Inputs   private/analysis/codings/api/{pilot-a-advance, pilot-b-advance, <full>-advance, calc1, r2}/, state.json;
         private/data/roadmap/blind/<key>.json; derived/{gold,r2}/metrics.json; derived/gold/human/ (gate)
Outputs  derived/advance/{pilot_keys.json, pilot.json, results.json, ADVANCE.md}; preregistration/advance-plan.{json,md}
Run:     python tools/roadmap/g24_advance.py pick
         python tools/roadmap/g24_advance.py pilot [--tags pilot-a-advance,pilot-b-advance]
         python tools/roadmap/g24_advance.py freeze [--full-tag full-advance]     (parent, after the pilot)
         python tools/roadmap/g24_advance.py test
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from common import ROOT, PRIVATE, DERIVED, TODAY, write_json, read_json, log, rel
import rounds
import g17_outcomes as g17
import g20_topics_journals as g20
from g11_human_agreement import alpha_nominal, alpha_ordinal
import blind_text
import check_advance as ca

API = PRIVATE / 'analysis' / 'codings' / 'api'
OUT = DERIVED / 'advance'
PLAN = ROOT / 'preregistration' / 'advance-plan.json'
PILOT_TAGS = ('pilot-a-advance', 'pilot-b-advance')
BUDGET, SPENT_BEFORE = 400.0, 221.59      # PI decision and parent's record, October 27, 2026
N_FULL = 572                              # valid inquiry codings: calc1 374 + r2 198
DEGENERATE, Q, SEED, MIN_N = 0.70, 0.1, 2029, 10
FROZEN_FILES = ['agents/advance/RUBRIC.md', 'agents/advance/advance.schema.json', 'tools/check_advance.py',
                'tools/blind_text.py', 'tools/code_papers.py', 'tools/roadmap/g24_advance.py']
ROLES = ['corrective', 'enabling', 'integrative', 'cumulative', 'transformative']
IMPACT = {'below_median': 1, 'around_median': 2, 'top_quartile': 3, 'top_decile': 4}
HYPOTHESES = [
    {'id': 'H1', 'feature': 'bin:triangulation', 'outcome': 'achieved_noW3', 'sign': 1,
     'basis': 'rubrics.qmd W3 and the seminar claim that independent checks of more than one kind raise warrant'},
    {'id': 'H2', 'feature': 'num:V check kinds', 'outcome': 'achieved_noW3', 'sign': 1,
     'basis': 'NASEM (2019) V: more kinds of check performed, more warrant'},
    {'id': 'H3', 'feature': 'bin:claim gate yes', 'outcome': 'achieved', 'sign': 1,
     'basis': 'codebook claim gate: a claim that faced a test it could fail is better warranted'},
    {'id': 'H4', 'feature': 'bin:claim gate yes', 'outcome': 'score', 'sign': 1,
     'basis': 'as H3, on the size of the warranted gain'},
    {'id': 'H5', 'feature': 'bin:action gate yes or partly', 'outcome': 'achieved', 'sign': 1,
     'basis': 'seminar: hypothesis-directed acquisition (the hypothesis-testing planner) yields warranted gains'},
    {'id': 'H6', 'feature': 'bin:outcome contradicted', 'outcome': 'role:corrective', 'sign': 1,
     'basis': 'rubrics.qmd: a correction can be a major gain; a contradicted outcome is the inquiry record of one'},
    {'id': 'H7', 'feature': 'bin:composition capability_first', 'outcome': 'role:enabling', 'sign': 1,
     'basis': 'a capability-first workflow builds the method, data or instrument that the enabling role names'},
    {'id': 'H8', 'feature': 'num:import fields', 'outcome': 'role:integrative', 'sign': 1,
     'basis': 'rubrics.qmd interdisciplinary transfer profile: integration across fields'},
    {'id': 'H9', 'feature': 'bin:any return after failure', 'outcome': 'score', 'sign': 1,
     'basis': 'seminar: returning after a failed step is iteration under test, which should enlarge the warranted gain'},
]
HAZARD = re.compile(r'hazard|forecast|projection|scenario|tsunami|probabilistic seismic|risk assessment|early warning', re.I)


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------ data
def advance_codings(tag: str) -> tuple[dict, list[str]]:
    """({key: valid coding}, [keys with an invalid coding]) for an advance tag folder."""
    d, out, bad = API / tag, {}, []
    for f in sorted(d.glob('g22_*.json')) if d.is_dir() else []:
        try:
            c = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            bad.append(f.stem); continue
        (bad.append(f.stem) if ca.validate(c) else out.__setitem__(c['key'], c))
    bad += [f.stem for f in sorted((d / '_invalid').glob('g22_*.json'))] if (d / '_invalid').is_dir() else []
    return out, sorted(set(bad) - set(out))


def inquiry() -> dict:
    """{key: {'round', 'coding', 'metrics'}} for papers with a valid inquiry coding and round metrics."""
    out = {}
    for name, tag, mset, _ in rounds.ROUNDS:
        met = rounds.metrics(mset)
        for k, c in rounds.valid(tag).items():
            if k in met:
                out[k] = {'round': name, 'coding': c, 'metrics': met[k]}
    return out


def blind_meta(k: str) -> dict:
    f = blind_text.CACHE / f'{k}.json'
    return json.loads(f.read_text()) if f.is_file() else {}


def gold_keys() -> set:
    out = set()
    for f in (DERIVED / 'calc1' / 'manifest.jsonl', DERIVED / 'r2calc' / 'manifest.jsonl', DERIVED / 'gold' / 'gold_manifest.jsonl'):
        for l in (f.read_text().splitlines() if f.is_file() else []):
            if l.strip() and json.loads(l).get('in_gold', f.name == 'gold_manifest.jsonl'):
                out.add(json.loads(l)['key'])
    return out


def state() -> dict:
    f = API / 'state.json'
    return json.loads(f.read_text()) if f.is_file() else {'done': {}, 'spent': {}, 'failed': {}}


def derived(c: dict) -> dict:
    """Outcome variables of one advance coding."""
    v, cond = c['verdict'], c['unassessable_condition']
    ok = lambda g, skip=(): all(g['criteria'][x] == 'met' or (x == 'W3' and g['criteria'][x] == 'not_applicable') for x in ca.CRIT if x not in skip)
    bg = ca.basis_gain(c)
    return {'verdict': v, 'condition': cond, 'screen_fail': cond == 'U4',
            'achieved': int(v == 'achieved'),
            'achieved_noW3': int(v != 'unassessable' and any(ok(g, ('W3',)) for g in c['candidate_gains'])),
            'achieved_in_taxonomy': int(v == 'achieved' and bg['origin'] != 'out_of_taxonomy'),
            'score': c['advance_score'], 'novelty_score': c['novelty_score'],
            'roles': set(c['roles']), 'assessable': v != 'unassessable',
            'basis_origin': bg['origin'] if c['verdict_basis'] != 'none' else 'none', 'basis_type': bg['gain_type'],
            'n_checks': sum(len(g['checks']) for g in c['candidate_gains']),
            'impact': IMPACT.get(c['impact_forecast'])}


# ------------------------------------------------------------------------------------------------ statistics
def wkappa(a: list[int], b: list[int], k: int = 5) -> float | None:
    """Quadratic-weighted kappa for paired scores 1..k."""
    if len(a) < 2:
        return None
    o = np.zeros((k, k))
    for x, y in zip(a, b):
        o[x - 1, y - 1] += 1
    w = np.array([[(i - j) ** 2 for j in range(k)] for i in range(k)]) / (k - 1) ** 2
    e = np.outer(o.sum(1), o.sum(0)) / o.sum()
    den = (w * e).sum()
    return None if den == 0 else round(float(1 - (w * o).sum() / den), 3)


def boot_alpha(units: list[list], fn, n: int = 1000) -> list | None:
    rng = np.random.default_rng(SEED)
    vals = []
    for _ in range(n):
        s = [units[i] for i in rng.integers(0, len(units), len(units))]
        a = fn(s)
        if a is not None:
            vals.append(a)
    return [round(float(np.percentile(vals, 2.5)), 3), round(float(np.percentile(vals, 97.5)), 3)] if len(vals) > 50 else None


def wilson(k: int, n: int) -> list | None:
    if n == 0:
        return None
    p, z = k / n, 1.96
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(c - h, 3), round(c + h, 3)]


def shares(vals) -> dict:
    c = Counter(vals)
    n = sum(c.values())
    top = c.most_common(1)[0] if c else (None, 0)
    return {'counts': dict(c), 'n': n, 'modal': top[0], 'modal_share': round(top[1] / n, 3) if n else None,
            'degenerate': bool(n and top[1] / n >= DEGENERATE)}


def partial_spearman(f, o, covs) -> float | None:
    f, o = g17.rank(f), g17.rank(o)
    X = np.column_stack([np.ones(len(f))] + [g17.rank(c) for c in covs])
    rf = f - X @ np.linalg.lstsq(X, f, rcond=None)[0]
    ro = o - X @ np.linalg.lstsq(X, o, rcond=None)[0]
    if rf.std() == 0 or ro.std() == 0:
        return None
    return round(float(np.corrcoef(rf, ro)[0, 1]), 3)


def signflip_wilcoxon(d: list[float], n: int = 10000) -> float | None:
    d = np.asarray([x for x in d if x != 0], float)
    if len(d) < 3:
        return None
    r = g17.rank(np.abs(d)) + 1
    obs = abs((np.sign(d) * r).sum())
    rng = np.random.default_rng(SEED)
    perm = np.abs((rng.choice([-1, 1], (n, len(d))) * r).sum(1))
    return round(float((1 + (perm >= obs - 1e-9).sum()) / (n + 1)), 4)


# ------------------------------------------------------------------------------------------------ pick
def pick(args) -> None:
    inq, gold = inquiry(), gold_keys()
    pool = sorted(k for k in inq if k not in gold and (blind_text.CACHE / f'{k}.txt').is_file())
    rng = np.random.default_rng(SEED)

    def arche(k):
        c, m = inq[k]['coding'], inq[k]['metrics']
        cs, comp = c['end']['claim_status'], c['composition']
        if HAZARD.search(m.get('title') or ''):
            return 'hazard_or_forecast'
        if cs == 'capability_characterized':
            return 'methods'
        if comp == 'trace_series':
            return 'reconstruction'
        if comp == 'natures_repetition' or cs == 'regularity_in_range':
            return 'observational'
        if cs == 'best_explanation':
            return 'model_or_mechanism'
        return 'other'
    groups = {}
    for k in pool:
        groups.setdefault(arche(k), []).append(k)
    chosen, picked = {}, []
    sub = lambda k: inq[k]['metrics'].get('subfield') or 'unknown'
    rnd = lambda k: inq[k]['round']
    share_sub = {x: n / len(pool) for x, n in Counter(map(sub, pool)).items()}
    share_rnd = {x: n / len(pool) for x, n in Counter(map(rnd, pool)).items()}
    for a in ('hazard_or_forecast', 'methods', 'reconstruction', 'observational', 'model_or_mechanism'):
        ks = [str(k) for k in rng.permutation(groups.get(a, []))]
        sel = []
        for slot in range(4):
            route = ('xml', 'pdftotext')[slot % 2]
            cand = [k for k in ks if k not in sel and blind_meta(k).get('source') == route] or [k for k in ks if k not in sel]
            if not cand:
                break
            n = len(picked) + 1
            cs, cr = Counter(map(sub, picked)), Counter(map(rnd, picked))
            k = min(cand, key=lambda k: (cs[sub(k)] - share_sub[sub(k)] * n, cr[rnd(k)] - share_rnd[rnd(k)] * n, ks.index(k)))
            sel.append(k); picked.append(k)
        chosen[a] = sel
    keys = [k for a in chosen for k in chosen[a]]
    rec = {'keys': keys, 'by_archetype': chosen, 'pool': len(pool), 'pool_by_archetype': {a: len(v) for a, v in groups.items()},
           'rounds': dict(Counter(inq[k]['round'] for k in keys)), 'sources': dict(Counter(blind_meta(k).get('source') for k in keys)),
           'subfields': dict(Counter(sub(k) for k in keys)), 'pool_subfields': dict(Counter(map(sub, pool))),
           'rule': __doc__.split('pick    ')[1].split('pilot   ')[0].strip(), 'seed': SEED}
    write_json(OUT / 'pilot_keys.json', rec, ['private/analysis/codings/api/calc1', 'private/analysis/codings/api/r2',
                                              'derived/gold/metrics.json', 'derived/r2/metrics.json', 'private/data/roadmap/blind'])
    print(json.dumps({a: len(v) for a, v in chosen.items()}), rec['rounds'], rec['sources'])
    print('--keys ' + ','.join(keys))


# ------------------------------------------------------------------------------------------------ pilot
def pilot(args) -> None:
    ta, tb = (args.tags.split(',') if args.tags else PILOT_TAGS)
    A, badA = advance_codings(ta)
    B, badB = advance_codings(tb)
    if not A and not B:
        sys.exit(f'no valid codings under {ta} or {tb}')
    inq = inquiry()
    both = sorted(set(A) & set(B))
    DA, DB = {k: derived(c) for k, c in A.items()}, {k: derived(c) for k, c in B.items()}
    retest = {'papers_in_both': len(both)}
    if both:
        u = [[DA[k]['verdict'], DB[k]['verdict']] for k in both]
        retest['verdict'] = {'alpha_nominal': alpha_nominal(u), 'ci': boot_alpha(u, alpha_nominal),
                             'agreement': round(sum(a == b for a, b in u) / len(u), 3),
                             'prevalence_achieved': round(sum(x == 'achieved' for p in u for x in p) / (2 * len(u)), 3)}
        su = [[DA[k]['score'], DB[k]['score']] for k in both]
        pairs = [(a, b) for a, b in su if a is not None and b is not None]
        retest['advance_score'] = {'alpha_ordinal': alpha_ordinal(su), 'ci': boot_alpha(su, alpha_ordinal),
                                   'weighted_kappa': wkappa([a for a, _ in pairs], [b for _, b in pairs]),
                                   'exact': round(np.mean([a == b for a, b in pairs]), 3) if pairs else None,
                                   'within_1': round(np.mean([abs(a - b) <= 1 for a, b in pairs]), 3) if pairs else None,
                                   'pairs_with_both': len(pairs)}
        retest['criteria_G1'] = {}
        for x in ca.CRIT:
            cu = [[A[k]['candidate_gains'][0]['criteria'][x], B[k]['candidate_gains'][0]['criteria'][x]] for k in both]
            retest['criteria_G1'][x] = {'alpha_nominal': alpha_nominal(cu), 'agreement': round(np.mean([a == b for a, b in cu]), 3),
                                        'met_rate': round(np.mean([v == 'met' for p in cu for v in p]), 3)}
        retest['roles'] = {'mean_jaccard': round(float(np.mean([len(DA[k]['roles'] & DB[k]['roles']) / max(1, len(DA[k]['roles'] | DB[k]['roles']))
                                                                for k in both])), 3),
                           'per_role_alpha': {r: alpha_nominal([[r in DA[k]['roles'], r in DB[k]['roles']] for k in both]) for r in ROLES}}
        nj = [[A[k]['precedent_search']['judgment_with_coder_knowledge'], B[k]['precedent_search']['judgment_with_coder_knowledge']] for k in both]
        ns = [[DA[k]['novelty_score'], DB[k]['novelty_score']] for k in both]
        retest['novelty'] = {'judgment_alpha_nominal': alpha_nominal(nj), 'score_alpha_ordinal': alpha_ordinal(ns),
                             'score_weighted_kappa': wkappa([a for a, _ in ns], [b for _, b in ns])}
        retest['impact_forecast_alpha_ordinal'] = alpha_ordinal([[DA[k]['impact'], DB[k]['impact']] for k in both])
    allc = [(k, c, DA[k] if t == 'A' else DB[k]) for t, M in (('A', A), ('B', B)) for k, c in M.items()]
    dist = {'verdict': shares(d['verdict'] for _, _, d in allc),
            'unassessable_condition': shares(d['condition'] for _, _, d in allc),
            'advance_score': shares(d['score'] for _, _, d in allc),
            'novelty_score': shares(d['novelty_score'] for _, _, d in allc),
            'basis_origin': shares(d['basis_origin'] for _, _, d in allc),
            'magnitude_form': shares(g['magnitude_form'] for _, c, _ in allc for g in c['candidate_gains']),
            'evidence_access': shares(g['evidence_access'] for _, c, _ in allc for g in c['candidate_gains']),
            'rival_test': shares(g['rival_test'] for _, c, _ in allc for g in c['candidate_gains'] if g['gain_type'] == 'understanding'),
            'criteria_met_G1': {x: round(np.mean([c['candidate_gains'][0]['criteria'][x] == 'met' for _, c, _ in allc]), 3) for x in ca.CRIT},
            'scores_1_and_5_used': {'1': any(d['score'] == 1 for _, _, d in allc), '5': any(d['score'] == 5 for _, _, d in allc)}}
    dist['degenerate'] = [f for f in ('verdict', 'advance_score', 'novelty_score') if dist[f]['degenerate']]
    sub = lambda k: (inq.get(k, {}).get('metrics') or {}).get('subfield') or 'unknown'
    strata = {'verdict_by_route': {}, 'by_subfield': {}, 'score_by_basis_type': {}}
    for k, c, d in allc:
        strata['verdict_by_route'].setdefault(blind_meta(k).get('source', 'unknown'), Counter())[d['verdict']] += 1
        s = strata['by_subfield'].setdefault(sub(k), {'codings': 0, 'not_quantifiable': 0, 'gains': 0, 'U2': 0, 'low_confidence': 0, 'scores': []})
        s['codings'] += 1; s['U2'] += d['condition'] == 'U2'; s['low_confidence'] += c['verdict_confidence'] == 'low'
        s['gains'] += len(c['candidate_gains']); s['not_quantifiable'] += sum(g['magnitude_form'].startswith('not_quant') for g in c['candidate_gains'])
        if d['score'] is not None:
            s['scores'].append(d['score'])
        if d['score'] is not None:
            strata['score_by_basis_type'].setdefault(d['basis_type'], []).append(d['score'])
    for s in strata['by_subfield'].values():
        s['median_score'] = float(np.median(s['scores'])) if s['scores'] else None
        s['not_quantifiable_rate'] = round(s['not_quantifiable'] / max(1, s['gains']), 3)
        del s['scores']
    strata['score_by_basis_type'] = {t: {'n': len(v), 'median': float(np.median(v)), 'mean': round(float(np.mean(v)), 2)} for t, v in strata['score_by_basis_type'].items()}
    strata['verdict_by_route'] = {r: dict(v) for r, v in strata['verdict_by_route'].items()}
    keys = sorted(set(A) | set(B))
    leak = Counter(); leak_papers = Counter()
    for k in keys:
        la = blind_meta(k).get('leakage_after', {})
        for part, fields in la.items():
            for f, v in fields.items():
                if f'{part}.{f}' not in blind_text.INFO_FIELDS and not f.endswith('first_6000'):
                    leak[f'{part}.{f}'] += v; leak_papers[f'{part}.{f}'] += v > 0
    leakage = {'residual': {f: [leak[f], leak_papers[f]] for f in sorted(leak) if leak[f]},
               'blind_leak_noticed_rate': round(np.mean([c['blind_leak_noticed'].strip().lower() not in ('none', 'none.', '') for _, c, _ in allc]), 3),
               'post_2022_knowledge_flag_rate': round(np.mean([c['post_2022_knowledge_flag'].strip().lower() not in ('none', 'none.', '') for _, c, _ in allc]), 3),
               'blind_leak_noticed': {k: c['blind_leak_noticed'] for k, c, _ in allc if c['blind_leak_noticed'].strip().lower() not in ('none', 'none.', '')}}
    val = Counter()
    for k, c, _ in allc:
        info = {}
        ca.check(c, info=info)
        val.update(info)
    st = state()
    cost = {}
    outs, failures = [], Counter()
    for t in (ta, tb):
        att = {k.split(':', 1)[1]: v for k, v in st.get('spent', {}).items() if k.startswith(t + ':')}
        usd = sum(x.get('usd') or 0 for v in att.values() for x in v)
        ok = len(A if t == ta else B)
        cost[t] = {'usd': round(usd, 2), 'attempts': sum(len(v) for v in att.values()), 'valid': ok,
                   'usd_per_valid': round(usd / ok, 3) if ok else None, 'invalid': len(badA if t == ta else badB)}
        for k, v in att.items():
            for x in v:
                if x.get('outcome') == 'ok' and x.get('usage'):
                    outs.append(x['usage']['output'])
                elif x.get('outcome') != 'ok':
                    failures[(blind_meta(k).get('source', 'unknown'), x.get('outcome', '')[:40])] += 1
    per = np.mean([cost[t]['usd_per_valid'] for t in cost if cost[t]['usd_per_valid']]) if any(cost[t]['usd_per_valid'] for t in cost) else None
    spent_pilot = sum(cost[t]['usd'] for t in cost)
    cost['output_tokens'] = ({'median': int(np.median(outs)), 'p90': int(np.percentile(outs, 90)), 'p99': int(np.percentile(outs, 99)),
                              'max': int(max(outs)), 'n': len(outs),
                              'recommended_max_tokens': int(math.ceil(np.percentile(outs, 99) * 1.1 / 1000) * 1000)} if outs else None)
    cost['failures_by_route'] = {f'{s} | {o}': n for (s, o), n in failures.items()}
    cost['projection'] = {'per_paper_usd': round(float(per), 3) if per else None,
                          'full_run_usd': round(float(per) * N_FULL, 2) if per else None,
                          'remaining_budget_usd': round(BUDGET - SPENT_BEFORE - spent_pilot, 2),
                          'note': f'budget ${BUDGET:.0f} total, ${SPENT_BEFORE} spent before the pilot (parent record), pilot spend from state.json'}
    sc = [(d['score'], blind_meta(k).get('words')) for k, _, d in allc if d['score'] is not None and blind_meta(k).get('words')]
    verb = {'rho_score_paper_words': round(g17.spearman([a for a, _ in sc], [b for _, b in sc]), 3) if len(sc) > 4 else None}
    out_by = {}
    for t in (ta, tb):
        for k, v in st.get('spent', {}).items():
            if k.startswith(t + ':'):
                okx = [x for x in v if x.get('outcome') == 'ok' and x.get('usage')]
                if okx:
                    out_by[(t, k.split(':', 1)[1])] = okx[-1]['usage']['output']
    so = [((A if t == ta else B)[k]['advance_score'], o) for (t, k), o in out_by.items() if k in (A if t == ta else B) and (A if t == ta else B)[k]['advance_score'] is not None]
    verb['rho_score_output_tokens'] = round(g17.spearman([a for a, _ in so], [b for _, b in so]), 3) if len(so) > 4 else None
    res = {'tags': [ta, tb], 'valid': {ta: len(A), tb: len(B)}, 'invalid': {ta: badA, tb: badB}, 'keys': keys,
           'retest': retest, 'distributions': dist, 'strata': strata, 'leakage': leakage, 'validator': dict(val), 'cost': cost,
           'verbosity': verb, 'rubric_version': ca.rubric_version(), 'rubric_sha256': sha(ROOT / 'agents/advance/RUBRIC.md'),
           'blind_version': blind_text.BLIND_VERSION}
    write_json(OUT / 'pilot.json', json.loads(json.dumps(res, default=lambda o: sorted(o) if isinstance(o, set) else str(o))),
               [f'private/analysis/codings/api/{ta}', f'private/analysis/codings/api/{tb}', 'private/analysis/codings/api/state.json',
                'private/data/roadmap/blind'])
    log('g24_advance.py pilot', 'advance pilot report', len(keys), f'{len(both)} papers coded twice')
    print(json.dumps({'retest': retest, 'degenerate': dist['degenerate'], 'verdict': dist['verdict']['counts'],
                      'score': dist['advance_score']['counts'], 'cost': cost['projection'], 'output_tokens': cost['output_tokens'],
                      'leak_noticed_rate': leakage['blind_leak_noticed_rate'], 'validator': dict(val)}, indent=1, default=str))


# ------------------------------------------------------------------------------------------------ freeze
def full_run_folders() -> list[Path]:
    return [d for d in API.glob('*-advance') if d.is_dir() and not d.name.startswith('pilot')
            and (any(d.glob('g22_*.json')) or any((d / '_invalid').glob('g22_*')))]


def freeze(args) -> None:
    if full_run_folders():
        sys.exit('refusing to freeze: full-run advance codings exist in ' + ', '.join(str(d) for d in full_run_folders()))
    pj = OUT / 'pilot.json'
    if not pj.is_file():
        sys.exit('refusing to freeze: run `pilot` first (derived/advance/pilot.json)')
    p = read_json(pj)
    if p['rubric_sha256'] != sha(ROOT / 'agents/advance/RUBRIC.md'):
        print('note: RUBRIC.md changed after the pilot; the plan freezes the current version and records both sha256 values')
    ach = [p['distributions']['verdict']['counts'].get('achieved', 0), p['distributions']['verdict']['n']]
    plan = {'frozen': TODAY, 'decided_by': 'Marine Denolle (PI), October 27, 2026',
            'construct': 'reported warrant (RUBRIC.md header); results are the model judgment of reported warrant until the validation gate passes',
            'rubric_version': ca.rubric_version(), 'files_sha256': {f: sha(ROOT / f) for f in FROZEN_FILES},
            'rubric_sha256_at_pilot': p['rubric_sha256'], 'blind_version': blind_text.BLIND_VERSION,
            'pilot_sha256': sha(pj), 'pilot_keys': p['keys'], 'full_run_tag': args.full_tag,
            'model': 'claude-opus-5-5', 'effort': 'high',
            'max_tokens': (p['cost'].get('output_tokens') or {}).get('recommended_max_tokens') or 32000,
            'success_fraction': 'achieved / (achieved + not_demonstrated + unassessable U1, U2, U3, U5); U4 reported separately; all three verdict counts reported',
            'expected_achieved_rate': {'pilot': f'{ach[0]} of {ach[1]} codings', 'wilson_95': wilson(*ach)},
            'pilot_degenerate_distributions': p['distributions']['degenerate'],
            'hypotheses': HYPOTHESES, 'family_size': len(HYPOTHESES), 'q_threshold': Q, 'min_feature_papers': MIN_N,
            'calibration_checks': [{'id': 'C1', 'x': 'impact_forecast (1-4)', 'y': 'cnp', 'sign': 1},
                                   {'id': 'C2', 'x': 'advance_score', 'y': 'cnp', 'sign': 1}],
            'rule': __doc__.split('freeze  ')[1].split('test    ')[0].strip(),
            'shared_method_variance': ('The inquiry coding (codebook 1.5.0) and the advance coding are made by the same model from the '
                                       'same paper text. An association between a workflow feature and advance is a same-model, '
                                       'same-text estimate that includes method variance: both codings respond to how richly the '
                                       'paper reports its checks. V-check features are tested only against the primary outcome with '
                                       'W3 removed; covariates (log paper words, text route, number of reported checks) are reported '
                                       'as a sensitivity; the same associations are reported on the 40 human-rated papers when the '
                                       'gate data exist. An optional second-coder replication with a different model on a random '
                                       '60-paper subsample (about $8) would show how much the associations shrink.'),
            'validation_gate': {'human_human_alpha_ordinal_score_min': 0.667, 'human_human_alpha_nominal_verdict_min': 0.667,
                                'model_swap_alpha_min': 'human-human alpha minus 0.10', 'mean_offset_max': 0.5,
                                'verdict_validation': 'needs ratings v1.1.0 (verdict, verdict_criteria, unassessable_condition); '
                                                      'until then the verdict has no human comparator and only the score is validated, '
                                                      'on papers both sides rate above 1',
                                'human_raters_saw_venue': True,
                                'note': 'n = 40 gives roughly +/- 0.15 to 0.25 on alpha'}}
    PLAN.parent.mkdir(parents=True, exist_ok=True)
    PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + '\n')
    md = ['# Scientific advance: preregistered plan', '',
          f'Frozen {TODAY}, after the pilot and before any full-run advance coding existed; decided by the PI on October 27, 2026. '
          f'Machine-readable plan: `advance-plan.json`; code: `tools/roadmap/g24_advance.py` (`test`).', '',
          f'- Instrument: agents/advance/RUBRIC.md v{plan["rubric_version"]} (sha256 `{plan["files_sha256"]["agents/advance/RUBRIC.md"][:12]}`), '
          f'claude-opus-5-5, blinded text v{plan["blind_version"]}. Construct: reported warrant.',
          f'- Primary outcome: achieved versus not. {plan["success_fraction"]}.',
          f'- Expected achieved rate (pilot): {plan["expected_achieved_rate"]["pilot"]}, Wilson 95% {plan["expected_achieved_rate"]["wilson_95"]}.',
          f'- One family of {len(HYPOTHESES)} tests: Spearman within round x subfield, stratified permutation p, Benjamini-Hochberg q < {Q} with the predicted sign.',
          '- Pilot papers are excluded from the tests. Unassessable papers (U1-U3, U5) stay in the denominator as not achieved; U4 papers are reported and excluded.',
          '- Validation gate on the 40 human-rated gold papers before the results are read as advance rather than model judgment (json `validation_gate`).', '',
          '| id | feature (inquiry coding) | outcome | predicted |', '|:--|:--|:--|:--|']
    md += [f"| {h['id']} | {h['feature']} | {h['outcome']} | {'positive' if h['sign'] > 0 else 'negative'} |" for h in HYPOTHESES]
    md += ['', 'Calibration checks, outside the family: C1 impact forecast against cnp, C2 advance score against cnp (both positive).', '',
           'Shared-method variance: ' + plan['shared_method_variance']]
    PLAN.with_suffix('.md').write_text('\n'.join(md) + '\n')
    log('g24_advance.py freeze', 'advance plan frozen', len(HYPOTHESES), f'{len(HYPOTHESES)} hypotheses')
    print(f'{rel(PLAN)}: {len(HYPOTHESES)} hypotheses frozen; commit and push it before the full run')


# ------------------------------------------------------------------------------------------------ test
def gate(model: dict) -> dict:
    """Validation gate status from the human ratings (derived/gold/human/<ID>/<key>.<ID>.ratings.json)."""
    hum = {}
    for f in (DERIVED / 'gold' / 'human').glob('*/*.ratings.json'):
        try:
            r = json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            continue
        hum.setdefault(r['key'], {})[f.parent.name] = r
    two = {k: v for k, v in hum.items() if len(v) >= 2}
    if not two:
        return {'status': 'no human ratings yet', 'passed': False}
    hs = lambda r: r['advance']['score']
    hh = alpha_ordinal([[hs(r) for r in v.values()][:2] for v in two.values()])
    swaps = []
    for i in range(2):
        units = [[hs(list(v.values())[1 - i]), model[k]['advance_score']] for k, v in two.items() if k in model]
        swaps.append(alpha_ordinal(units))
    both = [k for k in two if k in model and model[k]['advance_score'] is not None]
    diffs = [model[k]['advance_score'] - np.mean([hs(r) for r in two[k].values()]) for k in both]
    has_verdict = any('verdict' in r for v in two.values() for r in v.values())
    res = {'papers_two_raters': len(two), 'papers_with_model': len(both), 'human_human_alpha_score': hh,
           'model_swap_alpha_score': swaps, 'mean_offset': round(float(np.mean(diffs)), 3) if diffs else None,
           'offset_p_signflip': signflip_wilcoxon(diffs), 'human_verdict_available': has_verdict}
    sw = [x for x in swaps if x is not None]
    res['passed'] = bool(hh is not None and hh >= 0.667 and sw and min(sw) >= hh - 0.10 and diffs and abs(np.mean(diffs)) <= 0.5)
    if has_verdict:
        hv = [[r.get('verdict') for r in v.values()][:2] for v in two.values()]
        res['human_human_alpha_verdict'] = alpha_nominal(hv)
        res['passed'] = res['passed'] and (res['human_human_alpha_verdict'] or 0) >= 0.667
    res['status'] = 'passed' if res['passed'] else 'not passed: results are the model judgment of reported warrant'
    return res


def test(args) -> None:
    if not PLAN.is_file():
        sys.exit(f'refusing to test: no frozen plan at {PLAN.relative_to(ROOT)} (run `pilot`, then `freeze`, commit and push, then the full run)')
    plan = json.loads(PLAN.read_text())
    changed = [f for f in ('agents/advance/RUBRIC.md', 'agents/advance/advance.schema.json', 'tools/check_advance.py')
               if sha(ROOT / f) != plan['files_sha256'][f]]
    if changed:
        sys.exit(f'refusing to test: changed since the freeze: {changed}')
    full, bad = advance_codings(plan['full_run_tag'])
    inq = inquiry()
    pilot_keys = set(plan['pilot_keys'])
    keys = sorted(k for k in full if k in inq and k not in pilot_keys)
    if not keys:
        sys.exit('no valid full-run codings with inquiry codings')
    D = {k: derived(full[k]) for k in keys}
    u4 = [k for k in keys if D[k]['screen_fail']]
    keys = [k for k in keys if not D[k]['screen_fail']]
    F = {k: g17.features(inq[k]['coding']) for k in keys}

    def frac(ks, field='achieved'):
        v = Counter(D[k]['verdict'] for k in ks)
        return {'n': len(ks), 'achieved': v['achieved'], 'not_demonstrated': v['not_demonstrated'], 'unassessable': v['unassessable'],
                'fraction': round(sum(D[k][field] for k in ks) / len(ks), 3) if ks else None, 'wilson_95': wilson(sum(D[k][field] for k in ks), len(ks))}
    desc = {'overall': frac(keys), 'without_out_of_taxonomy_awards': frac(keys, 'achieved_in_taxonomy'), 'U4_screen_failures': len(u4),
            'unassessable_conditions': dict(Counter(D[k]['condition'] for k in keys if D[k]['verdict'] == 'unassessable')),
            'by_round': {r: frac([k for k in keys if inq[k]['round'] == r]) for r in ('round1', 'round2')},
            'by_route': {s: frac([k for k in keys if blind_meta(k).get('source') == s]) for s in ('xml', 'pdftotext')},
            'by_subfield': {s: frac([k for k in keys if (inq[k]['metrics'].get('subfield') or 'unknown') == s])
                            for s in sorted({inq[k]['metrics'].get('subfield') or 'unknown' for k in keys})},
            'score_distribution': dict(Counter(D[k]['score'] for k in keys))}

    def outcome(k, o):
        if o.startswith('role:'):
            return float(o.split(':', 1)[1] in D[k]['roles']) if D[k]['assessable'] else None
        if o == 'score':
            return D[k]['score']
        return float(D[k][o])
    rows = []
    for h in HYPOTHESES:
        ks = [k for k in keys if outcome(k, h['outcome']) is not None]
        f = [float(F[k].get(h['feature'], 0 if h['feature'].startswith('num:') else False)) for k in ks]
        o = [outcome(k, h['outcome']) for k in ks]
        subs = Counter(inq[k]['metrics'].get('subfield') or 'unknown' for k in ks)
        strata = [f"{inq[k]['round']}|{(inq[k]['metrics'].get('subfield') or 'unknown') if subs[inq[k]['metrics'].get('subfield') or 'unknown'] >= MIN_N else g20.POOLED}" for k in ks]
        r = {'id': h['id'], 'feature': h['feature'], 'outcome': h['outcome'], 'predicted_sign': h['sign'], 'n': len(ks)}
        npos = sum(x > 0 for x in f)
        testable = len(set(o)) > 1 and (h['feature'].startswith('num:') and len(set(f)) > 1 or MIN_N <= npos <= len(ks) - MIN_N)
        res = g20.stratified(f, o, strata, f'advance|{h["id"]}') if testable else None
        r.update(res or {'rho_within': None, 'p': 1.0})
        r['testable'] = bool(testable and res)
        r['feature_present'] = npos
        r['direction_ok'] = bool(res and np.sign(res['rho_within']) == h['sign'])
        r['plain_rho'] = round(g17.spearman(f, o), 3) if testable else None
        covs = [np.log1p([blind_meta(k).get('words', 0) for k in ks]), [float(blind_meta(k).get('source') == 'xml') for k in ks],
                [D[k]['n_checks'] for k in ks]]
        r['partial_rho_covariates'] = partial_spearman(f, o, covs) if testable else None
        if h['outcome'] == 'achieved':
            r['rho_against_noW3'] = round(g17.spearman(f, [D[k]['achieved_noW3'] for k in ks]), 3) if testable else None
        rows.append(r)
    for r, q in zip(rows, g17.bh([r['p'] for r in rows])):
        r['q'] = round(float(q), 4)
        r['verdict'] = ('supported' if r['q'] < plan['q_threshold'] and r['direction_ok'] else
                        'reversed' if r['q'] < plan['q_threshold'] else 'not supported')
    cal = []
    for c, xs in (('C1', lambda k: D[k]['impact']), ('C2', lambda k: D[k]['score'])):
        ks = [k for k in keys if xs(k) is not None and inq[k]['metrics'].get('cnp') is not None]
        cal.append({'id': c, 'n': len(ks), **(g17.test([xs(k) for k in ks], [inq[k]['metrics']['cnp'] for k in ks]) or {})})
    res = {'plan_sha256': sha(PLAN), 'full_run_tag': plan['full_run_tag'], 'papers': len(keys), 'invalid_codings': len(bad),
           'excluded_pilot': len(pilot_keys & set(full)), 'descriptive': desc, 'family': rows,
           'verdicts': dict(Counter(r['verdict'] for r in rows)), 'calibration': cal, 'validation_gate': gate(full)}
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / 'results.json', res, ['preregistration/advance-plan.json', f'private/analysis/codings/api/{plan["full_run_tag"]}',
                                           'private/analysis/codings/api/calc1', 'private/analysis/codings/api/r2',
                                           'derived/gold/metrics.json', 'derived/r2/metrics.json'])
    o = desc['overall']
    md = ['# Scientific advance (model judgment of reported warrant)', '',
          f"Validation gate: {res['validation_gate']['status']}.", '',
          f"{len(keys)} papers; achieved {o['achieved']}, not demonstrated {o['not_demonstrated']}, unassessable {o['unassessable']}; "
          f"success fraction {o['fraction']} (Wilson 95% {o['wilson_95']}); U4 screen failures {len(u4)}.", '',
          '| id | feature | outcome | n | rho within | q | verdict |', '|:--|:--|:--|--:|--:|--:|:--|']
    md += [f"| {r['id']} | {r['feature']} | {r['outcome']} | {r['n']} | {r['rho_within']} | {r['q']} | {r['verdict']} |" for r in rows]
    (OUT / 'ADVANCE.md').write_text('\n'.join(md) + '\n')
    log('g24_advance.py test', 'advance plan run', len(keys), str(res['verdicts']))
    print(res['verdicts'], desc['overall'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['pick', 'pilot', 'freeze', 'test'])
    ap.add_argument('--tags', help='pilot: two advance tags, comma-separated (default pilot-a-advance,pilot-b-advance)')
    ap.add_argument('--full-tag', default='full-advance', help='freeze: the full-run tag folder (with the -advance suffix)')
    a = ap.parse_args()
    {'pick': pick, 'pilot': pilot, 'freeze': freeze, 'test': test}[a.cmd](a)
