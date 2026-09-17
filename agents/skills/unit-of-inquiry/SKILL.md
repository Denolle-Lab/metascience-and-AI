---
name: unit-of-inquiry
description: Runs a research agent along the unit graph of scientific inquiry, from a trigger event (an observation, a problem, a prediction, a new capability, or a supplied goal) to a warranted claim or a principled abstention, following a human-made scientific method chosen from the trigger and the epistemic situation (strong inference, trace series, nature's repetition, exploration first). Load whenever an agent is asked to investigate, explain, test, or decide something about the physical world. Derived from unit.qmd graph v0.2 and the meeting 1 readings. Not a paper classifier.
version: 0.2.0
source: unit.qmd (graph v0.2, compositions in section 6), sessions/01-scientific-method.qmd
status: drafted, not evaluated; built progressively, one meeting at a time
---

# The unit of inquiry as an operating procedure

This skill makes an agent do research the way the graph in `unit.qmd` says research is done. It does not describe or classify a finished paper; that is the job of the claim record and the corpus codebook. Here the agent starts from a trigger, chooses a method that people have used and defended, and moves through the nodes, producing at each one the artifact the node owes and moving on only when the node's exit condition is met.

The graph is the scientific method in its unit form: H + A + C ⇒ E, tested, controlled, and revised. A method is a way of composing units. The skill encodes four methods so far, with the reading that defined each. Later meetings add procedures for the nodes they study and new compositions, logged at the end of this file.

## 1. Inputs

| Input | Content | Default |
|:--|:--|:--|
| `trigger` | The event that starts inquiry, one of five kinds (section 3), with its content: the observation, the problem statement, the prediction and its source, the new capability, or the goal and who supplied it | required |
| `situation` | What the agent can do to the system: can it set conditions (experiment, simulation) or only find them (field, archive, catalog)? Is the phenomenon unique or repeated by nature? Is it stable enough to derive from? | inferred from the trigger; the agent must state its inference |
| `method` | `auto`, or one of `strong-inference`, `trace-series`, `natures-repetition`, `exploration-first` | `auto` |
| `evidence_access` | Which data the agent already has, dated, so that commitments can be recorded relative to access (the registration gate) | required |
| `budget` | Runs, observations, tool calls, or time the agent may spend before it must report | required |
| `tools` | What it can call: data access, forward models, inversion codes, literature search, laboratory or field requests to a human | required |

## 2. State the agent carries

Every field is written to the action log with the node letter of the step that changed it.

| Field | Content | Node |
|:--|:--|:--|
| `question` | The question in force, its origin, and every reframing with its date | Q |
| `phenomenon` | What has been seen, whether it repeats, and on what | before G |
| `rivals` | H_1 … H_n, each marked incompatible with the others or not | G |
| `auxiliaries` | The assumptions A each derivation depends on: instrument model, background laws, processing choices, dating method | D |
| `conditions` | C, and whether it is set or found | C |
| `expectations` | E_i per rival, with the observable on which they differ | S |
| `series` | Every run: what was held, varied, removed; the outcome | V |
| `traces` | Independent lines of evidence, for the found-C methods | V substitute |
| `verdicts` | Per rival: excluded, retained (with status), protected (with the conjunct revised and why), or not decidable (with the deciding observation) | X, K, P |
| `claim_record` | The card for anything asserted; template `templates/claim-record.json` | K |
| `composition` | The method in use and the state that selected it | step 0 |

## 3. Step 0: read the trigger, choose the method

**Classify the trigger.** Five kinds, from the unit page's entry-state table. The kind determines where on the graph the agent enters.

| Trigger | Enter at | First move |
|:--|:--|:--|
| A surprising observation or anomaly | before G | Establish whether it is a phenomenon: does it repeat, is it in the measurement chain or in the world? (Cleland 2002, p. 486; Fugelsang et al. 2004 for the base rate that anomalies are first errors) |
| An unsolved problem or question | Q then G | Enumerate rivals before deriving anything (Chamberlin 1890; Gilbert 1896 by analogy and enumeration) |
| A hypothesis or a theory's prediction | D | Name A and C, then design; do not observe until the expectation is written down (Cleland 2001, p. 987) |
| A new capability | before G, via O | Observe what the capability can see, record the measurement chain, and treat the first structure seen as an anomaly to be established (meeting 5) |
| A goal supplied by someone else | Q | Record who supplied it and reframe it as a question with a consequence; a goal is not a hypothesis (Platt 1964, p. 352) |

**Choose the method.** With `method: auto`, three state variables decide. The choice is logged and may be contested by the human.

| Can C be set? | Unique or repeated? | Phenomenon stable? | Method |
|:--|:--|:--|:--|
| any | any | no | `exploration-first`, then re-decide |
| set | any | yes | `strong-inference` (Platt 1964, p. 347) |
| found | unique | yes | `trace-series` (Cleland 2002, pp. 484, 487–491) |
| found | repeated by nature | yes | `natures-repetition` (Cleland 2002, p. 485) |

A named `method` overrides the table, and the agent records the override and what the table would have chosen.

## 4. The procedure, node by node

Each node states what to do, what to produce, when to move on, and what not to do. The source is the reading that fixed the rule. A move that violates a "do not" is refused and logged, not silently corrected.

**Before G: establish the phenomenon** (only when the trigger is an anomaly or a capability, or `exploration-first` is chosen).
- Do: vary conditions and representations; re-observe; check the measurement chain (instrument, processing, sampling) before the world; record what repeats and under what.
- Produce: `phenomenon`, with a repeatability statement and the checks that separated instrument from world.
- Move on when: the phenomenon repeats, or an independent record corroborates a unique event, or a measurement-chain check attributes it to the chain (then stop: it was an artifact).
- Do not: invent a hypothesis to make exploration look like a test; report the anomaly as a discovery before this node is complete. (Cleland 2002, p. 486; the meeting 2 and 8 procedures will extend this node.)

**Q: fix the question.**
- Do: write the question and its origin; if a goal was supplied, reframe it as a question whose answer would change something; record every later reframing with the date.
- Produce: `question`.
- Move on when: the question names a consequence that would differ between answers.
- Do not: proceed on a goal with no consequence stated.

**G: generate rivals.**
- Do: enumerate at least two hypotheses incompatible with one another; generate by analogy, by enumeration of known causes, and by asking what else produces this evidence; include the null of "nothing physical, an artifact" until the before-G node has excluded it.
- Produce: `rivals`, each with a one-line mechanism.
- Move on when: n ≥ 2 and the rivals are marked incompatible, or n = 1 with a logged reason no rival could be formulated.
- Do not: list verbal variants as rivals; treat an auxiliary as a rival, since an auxiliary can be dropped to save H and a rival cannot. (Chamberlin 1890; Platt 1964, p. 350; Cleland 2002, pp. 483–484.)

**D: derive expectations.**
- Do: for each rival, write E_i as a consequence of H_i together with named A and named C; list the auxiliaries explicitly, including processing choices and instrument response.
- Produce: `expectations`, `auxiliaries`.
- Move on when: every E_i has its A and C listed.
- Do not: use an expectation at X whose auxiliaries were never listed. (Cleland 2001, pp. 987–988.)

**S: design the discriminating observation.**
- Do: choose the observable and the conditions under which the E_i differ most; answer Platt's Question for the design: which rival would each outcome disprove?; prefer a test the rival would probably fail if false.
- Produce: the design, with the outcome-to-rival map.
- Move on when: every outcome excludes at least one rival, or the agent records that no such design exists with current tools and asks a human for a capability.
- Do not: run an observation that no outcome would count against any rival; that is exploration, so label it and go before G. (Platt 1964, p. 352; Bacon's instances of the fingerpost; Mayo 1996.)

**C: set or find the conditions.**
- Do: if set, set them and record what was held and what varied; if found, search the record or the field for the conditions the design needs, and record what was found and what was not available.
- Produce: `conditions`, marked set or found.
- Move on when: the conditions of the design are in hand, or the agent records which are missing.
- Do not: report a control that was never run; when C is found, do not claim the method of difference. (Cleland 2002, p. 484; 2001, p. 988.)

**O: observe.**
- Do: make or retrieve the observation with its full measurement chain; state the theory the observation is laden with and add it to A.
- Produce: the observation and its provenance.
- Move on when: provenance is complete.
- Do not: accept an observation whose chain is unknown as evidence at M. (Hanson 1958; meeting 5 will extend this node.)

**M: match.**
- Do: compare the observation with each E_i separately; record match, mismatch, or not separable.
- Produce: the match table.
- Move on: always to V.
- Do not: read a mismatch as refuting H_i alone; it refutes H_i + A + C. (Duhem; Cleland 2001, p. 988.)

**V: control the series.**
- Do, when C is set: after a mismatch, hold C and vary A, against false negatives; after a match, vary A again and remove C, against false positives; run again; controls fixed before any data may be revised after data with the reason logged.
- Do, when C is found: substitute independent traces, each with its own chain, and record that V proper is unavailable.
- Produce: `series` or `traces`.
- Move on when: the outcome survives the series, or the budget is spent (then report from V, not from K).
- Do not: let any experimental claim leave this node after one run. (Cleland 2002, pp. 477–480, 491; the Viking rule.)

**X: exclude.**
- Do: exclude a rival only after the series; state which conjunct was rejected.
- Produce: a verdict per excluded rival.
- Do not: reject A or C silently; that move is P and must be logged as P. (Popper; Cleland 2001, p. 988.)

**P: protect, logged.**
- Do: revise an auxiliary or a condition instead of the hypothesis when the series supports it; return to D with the revised A or C.
- Produce: the revision and its reason.
- Do not: protect the same hypothesis more than twice without a new prediction; flag it as degenerating. (Lakatos 1970.)

**K: retain, with a status.**
- Do: retain with one of three statuses: corroborated (survived a severe test), confirmed (E observed, with how unlikely E was without H stated), or best explanation (best within the stated rival set; may be deposed); write the claim record.
- Produce: `claim_record` with `status` and the evidence supplied against the evidence owed.
- Do not: write "proved"; call a best explanation an exclusion; retain without saying whether the rivals were excluded. (Hempel 1945; Popper; Harman 1965; Cleland 2002, pp. 481–483.)

**R: refine and return.**
- Do: split the survivor into subhypotheses; return to G with the record intact and appended, never overwritten.

**Abstain**, at any node after M: "not decidable with this evidence, and here is the observation that would decide it." This is a result. It is scored as correct where the evidence was insufficient and penalized where an answer was available. (Cleland 2002, pp. 492–494, ALH84001.)

## 5. The methods, as compositions of the unit

| Method | How it runs the graph | Its guard |
|:--|:--|:--|
| `strong-inference` | G with n ≥ 2; one S shared by all rivals; C set; O and M once per pass; V run, which Platt's step 3 assumes; every outcome excludes; R then G | If S cannot make the E_i differ, stop and say so; do not run a test all rivals pass (Platt 1964, p. 347) |
| `trace-series` | G with rivals for a past event; C found; O repeated over independent traces, each with its own chain, in place of V; K by best explanation within the stated set; a rival need not be excluded to be beaten | Abstain when no trace discriminates; name the trace that would (Cleland 2002, pp. 484, 487–494) |
| `natures-repetition` | C found but repeated by nature; O over the repetitions; a regularity fitted at K with out-of-sample checks in place of V; no power to set or remove C, so no causal claim from the fit alone | Report the fit as a regularity, not a mechanism; two rivals can predict the same regularity (Cleland 2002, p. 485; Platt 1964, pp. 351–352) |
| `exploration-first` | The before-G node run as a loop until a phenomenon repeats; then re-run step 0 | Never emit a claim record from this method; its output is a phenomenon and a reframed question (Cleland 2002, p. 486) |

## 6. Terminal states and outputs

- A **warranted claim**: a claim record with status corroborated, confirmed, or best explanation, and the composition used.
- A **principled abstention**: the deciding observation, and what capability or budget it needs.
- A **reframed question**: from exploration, with the phenomenon established.
- An **artifact verdict**: the trigger was in the measurement chain; the chain check is the result.

Every run emits the node-labelled action log, the composition declaration with the state that chose it, and, for any retained hypothesis, the claim record. Generated rationales are not the record; the log and the tool outputs are.

## 7. Worked example: an observation triggers the run

Trigger: an observation. Three years of ambient-noise cross-correlations on a dense array; most station pairs show a small annual velocity change; one pair shows an unexpected jump in year two. `situation`: C found (nature sets the seasons), repeated by nature for the annual cycle, unique for the jump. `method: auto`.

| Step | What the agent does | Artifact |
|:--|:--|:--|
| 0 | Two triggers, treated separately. The annual cycle: found, repeated, stable → `natures-repetition`. The jump: found, unique, not yet a phenomenon → `exploration-first` | composition declaration, two entries |
| before G (jump) | Checks the measurement chain first: instrument swap, clock, processing window, source-direction change; re-observes on neighbouring pairs; asks whether the jump repeats on any other pair or year | phenomenon: "jump on one pair, absent on neighbours, coincident with a logged sensor replacement" → artifact verdict; the jump run ends here |
| Q (cycle) | Question: does the seasonal velocity change track groundwater? Origin: observation. Consequence: if yes, the array is a hydrological instrument | question |
| G | Rivals: groundwater storage; thermoelastic strain; precipitation loading; seasonal change in noise-source direction. Marked incompatible except that loading and storage may co-occur; the pair is flagged | rivals |
| D | Each rival gives E_i as a phase lag against a driver and a depth sensitivity: groundwater lags rainfall by weeks and is deep; thermoelastic tracks temperature with days of lag and is shallow; loading is in phase with rainfall; a source change shows in the correlation asymmetry, not in velocity. A listed for each: the depth sensitivity kernel, the noise-source model, the well-record calibration | expectations, auxiliaries |
| S | The observable on which the E_i differ: phase lag against temperature versus against water level, by frequency band (depth). Platt's Question answered per outcome | design |
| C | Found: water-level records from wells outside the array, temperature, rainfall. Not available: a well inside the array | conditions: found, with the gap logged |
| O, M | Phase lags measured per band; matched against the four expectations | match table |
| V substitute | No conditions can be set. Independent traces: the second and third years; two frequency bands; the correlation asymmetry as a separate check on the source rival | traces |
| X, K | Source change excluded by the asymmetry check; thermoelastic excluded at depth by the lag; groundwater and loading not separable with the wells available | verdicts |
| Abstain | "Not decidable between groundwater storage and precipitation loading with these observations; a well inside the array, or a fourth year with a dry winter, would decide it" | abstention with the deciding observation |

The run produces no "groundwater causes the change." It produces two exclusions, one artifact verdict, and a named next observation. Under the textbook method the agent would have reported the fit; under this skill it reports what the evidence owed and what it lacked.

## 8. Guardrails and evaluation hooks

Planted-flaw items that test whether the procedure holds:
- a forced single hypothesis at G;
- a test all rivals pass at S;
- a claim leaving V after one run;
- an exclusion that silently rejected A;
- a smoking gun reported as an exclusion;
- abstention on an answerable case, and a confident answer on an unanswerable one;
- an artifact reported as a phenomenon.

Historical items score the process at the date, not the known outcome (`historical-evaluation.qmd`).

## 9. Progressive build

| Version | Meeting | What it adds |
|:--|:--|:--|
| 0.2.0 | 1 | This procedure: triggers, method choice, the eleven nodes, four compositions, one worked example |
| 0.3 | 2 | The before-G node as a full exploration procedure: systematic variation, representation change, when to stop exploring (Steinle; Karaca) |
| 0.4 | 3 | The trace-series method in detail: trace provenance, rival histories, the discriminating trace (Atwater; Nelson) |
| 0.5 | 4 | Concept formation at G and the discriminating prediction at S (Wilson; Sykes) |
| 0.6 | 5 | The O node: measurement chain, response, calibration, independent sensor (Lindsey and Lindsey) |
| 0.7 | 6 | The registration gate as a state field: commitments recorded relative to evidence access (Nosek; CSEP) |
| 0.8 | 8, 9 | Anomaly triage with its base rate; model equifinality at K (Moore; Yaqub; Oreskes; Beven) |
| 1.0 | 13 | Evaluated on the planted flaws and one historical case |

## 10. Changes

| Version | Date | Change |
|:--|:--|:--|
| 0.1.0 | September 17, 2026 | First draft: state, one rule per node, three compositions |
| 0.2.0 | September 17, 2026 | Rewritten as an operating procedure from a trigger; step 0 method choice; do / produce / move on / do not per node; exploration-first added as a fourth method; worked example; progressive-build plan |
