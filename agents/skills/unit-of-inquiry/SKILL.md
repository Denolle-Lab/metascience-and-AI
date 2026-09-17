---
name: unit-of-inquiry
description: Controls how a scientific agent moves through one unit of hypothesis testing, H + A + C => E, and how it composes units into a mode of inquiry. Load for any task that proposes, tests, retains, or excludes an explanation. Derived from unit.qmd v0.2; every rule cites the reading that forced it.
version: 0.1.0
source: unit.qmd (graph v0.2), sessions/01-scientific-method.qmd
status: drafted, not evaluated
---

# The unit of inquiry as an agent skill

This skill does not tell the agent what to think. It tells it which node of the unit graph it is at, what that node owes, and when it may move. The graph is `unit.qmd`, section 5; letters below are its node letters. The rules are design hypotheses from the meeting 1 readings, not evaluated capabilities.

## State the agent must carry

| Field | Content | Node |
|:--|:--|:--|
| `question` | The question in force, its origin (anomaly, problem, prediction, capability, supplied goal), and every reframing with its date | Q |
| `rivals` | The hypotheses H_1 … H_n, each marked incompatible with the others or not | G |
| `auxiliaries` | The assumptions A each derivation depends on: instrument model, background laws, dating method | D |
| `conditions` | C, and whether it was set (experiment) or found (trace) | C |
| `expectations` | E_i per rival, with the observable on which they differ | S |
| `series` | Every run: what was held, what was varied, what was removed, and the outcome | V |
| `verdicts` | Per rival: excluded, retained, protected (with the conjunct revised and why), or not decidable (with the observation that would decide) | X, K, P |
| `claim_record` | The claim card for anything asserted; template `templates/claim-record.json` | K |

## Rules by node

**Q.** Record the origin of the question before doing anything else. A goal supplied from outside is an origin, not a hypothesis. (Platt 1964, p. 352, on funders; every system in the prior-art chapter.)

**G.** Do not proceed with n = 1 unless the log says why no rival could be formulated. Rivals must be incompatible with one another; verbal variants are not rivals. Do not confuse a rival with an auxiliary: an auxiliary can be dropped to save H, a rival cannot. (Chamberlin 1890; Platt 1964, p. 350; Cleland 2002, pp. 483–484.)

**D.** Every expectation E_i is derived from H_i together with named A and C. Name them. An expectation whose auxiliaries are unlisted cannot be used at X. (Cleland 2001, pp. 987–988.)

**S.** Prefer the observable on which the E_i differ. Before any experiment, answer Platt's Question: which hypothesis would this outcome disprove? If the answer is none, the experiment is exploration, not a test; label it so and go to the exploration rule below. (Platt 1964, p. 352; Bacon's instances of the fingerpost.)

**C.** Record set or found. If found, the method of difference is unavailable: do not report a control that was never run. (Cleland 2002, p. 484; 2001, p. 988.)

**O.** Record the observation with its measurement chain. An observation is theory-laden; the theory it is laden with is an auxiliary and goes in A. (Hanson 1958; meeting 5.)

**M.** Match each E_i separately. A mismatch is a mismatch with H_i + A + C, never with H_i alone. (Duhem 1954; Cleland 2001, p. 988.)

**V.** No experimental claim leaves this node after one run. After a mismatch, hold C and vary A, against false negatives. After a match, vary A again and remove C, against false positives. Log every run. Controls fixed before any data may be revised after data, with the reason logged. (Cleland 2002, pp. 477–480, the Viking case.) When C is found, V is unavailable: substitute independent traces, and say so. (Cleland 2002, p. 491.)

**X.** Exclude only after the series. State which conjunct is rejected. If A or C is rejected instead of H, that is node P, not X, and the reason is logged. (Popper; Duhem; Cleland 2001, p. 988, Neptune.)

**K.** Retain with a status: corroborated (survived a severe test), confirmed (E observed, strength stated as how unlikely E was without H), or best explanation (best within the stated rival set; may be deposed). Never "proved." A best explanation need not have excluded the rivals; say whether it did. (Hempel 1945; Popper; Harman 1965; Cleland 2002, pp. 481–483.)

**P.** Allowed, logged, and bounded: a hypothesis protected more than twice without a new prediction is flagged as degenerating. (Lakatos 1970.)

**R.** Refine survivors into subhypotheses and return to G with the record intact. Never overwrite an earlier verdict; append.

**Abstention.** "Not decidable with this evidence, and here is the observation that would decide it" is a legal terminal state at any node after M. It is scored as correct where the evidence was insufficient and penalized where an answer was available. (Cleland 2002, pp. 492–494, ALH84001.)

**Exploration.** Before G, when no phenomenon is stable: vary conditions and representations, record what repeats, and enter G only when a phenomenon repeats. Do not invent a hypothesis to make exploration look like a test. (Cleland 2002, p. 486; meeting 2.)

## Composing units into a mode

A mode of inquiry is a way of composing units. Three compositions are defined so far; later meetings add more.

| Composition | Structure | Where it comes from |
|:--|:--|:--|
| Parallel, shared test (Platt) | n units share one S, C, O, M; each outcome excludes at least one rival; survivors go to R and back to G | Platt 1964, p. 347 |
| Trace series (Cleland) | C found; O repeated over independent traces instead of V over varied A; K by best explanation within the rival set | Cleland 2002, pp. 484, 487–491 |
| Nature's repetition | C found but repeated by nature; a regularity fitted across the repetitions; no power to set or remove C | Cleland 2002, p. 485; the regularities mode |

The skill selects a composition from `conditions` and `rivals`: set and n > 1 permits the Platt composition; found and unique permits the trace series; found and repeated permits nature's repetition. The selection is logged and can be contested.

## What the skill must emit

- A node-labelled action log: every step names its node and its inputs.
- A claim record for every retained hypothesis, with `status` and the evidence supplied against the evidence owed (the mode page's evidence column).
- The composition used and the reason.
- On abstention, the deciding observation.

## Evaluation hooks

- Planted-flaw items: a forced single hypothesis at G; a test all rivals pass at S; a claim leaving V after one run; an exclusion that silently rejected A; a smoking gun reported as an exclusion; abstention on an answerable case.
- Historical items: the meeting 1 cases, scored on process at the date, not on the known outcome (see `historical-evaluation.qmd`).

## Changes

| Version | Date | Change |
|:--|:--|:--|
| 0.1.0 | September 17, 2026 | First draft from unit graph v0.2 and the meeting 1 readings read in full |
