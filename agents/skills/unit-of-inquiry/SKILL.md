---
name: unit-of-inquiry
description: Runs a research agent along the unit graph of scientific inquiry (unit.qmd, graph v0.2), from a trigger event to a warranted claim or a principled abstention, following a human-made method chosen from the situation. Load whenever an agent is asked to investigate, explain, test, or decide something about the physical world. Not a paper classifier.
version: 0.2.1
rubric: unit.qmd graph v0.2; modes/*.qmd for the evidence each claim owes
references: references/nodes.md (rules with sources), references/methods.md, references/example.md, references/evaluation.md, CHANGELOG.md
status: drafted, not evaluated
---

# Unit of inquiry: the procedure

You do research by moving through the nodes of the unit graph. At each node produce the artifact it owes, move on only when its exit condition holds, and refuse the moves marked "do not." Log every step with its node letter. The rubric you are held to is the graph and the mode pages, not this file.

## Inputs

`trigger` (one of: observation, problem, prediction, capability, supplied goal, with its content) · `situation` (can conditions be set or only found; is the event unique or repeated by nature; is the phenomenon stable) · `method` (`auto` or `strong-inference` | `trace-series` | `natures-repetition` | `exploration-first`) · `evidence_access` (what you already hold, dated) · `budget` · `tools`.

## Step 0: enter, then choose the method

| Trigger | Enter at | First move |
|:--|:--|:--|
| Observation or anomaly | before G | Establish it is a phenomenon: does it repeat; is it in the chain or the world |
| Problem or question | Q, G | Enumerate rivals before deriving anything |
| Prediction | D | Name A and C, write the expectation, then design |
| New capability | before G via O | Record the chain; treat the first structure seen as an anomaly |
| Supplied goal | Q | Record who supplied it; reframe as a question with a consequence |

| Set C? | Unique or repeated | Stable? | Method |
|:--|:--|:--|:--|
| any | any | no | `exploration-first`, then re-decide |
| set | any | yes | `strong-inference` |
| found | unique | yes | `trace-series` |
| found | repeated | yes | `natures-repetition` |

A named method overrides the table; log the override and the table's choice.

## The loop

| Node | Do | Produce | Move on when | Do not |
|:--|:--|:--|:--|:--|
| before G | Vary conditions and representations; check the measurement chain before the world; record what repeats | `phenomenon` | It repeats, or an independent record corroborates it, or the chain explains it (stop: artifact) | Invent a hypothesis to make exploration look like a test |
| Q | Write the question, its origin, every reframing with a date | `question` | It names a consequence that differs between answers | Proceed on a goal with no consequence |
| G | Enumerate ≥ 2 incompatible rivals, by analogy and by known causes; keep "artifact" as a rival until before-G excluded it | `rivals` | n ≥ 2 marked incompatible, or n = 1 with a logged reason | List verbal variants as rivals; treat an auxiliary as a rival |
| D | For each rival, derive E_i from H_i + A + C with A and C named | `expectations`, `auxiliaries` | Every E_i has its A and C listed | Use at X an expectation whose A is unlisted |
| S | Choose the observable and conditions where the E_i differ; map each outcome to the rival it disproves | design | Every outcome excludes ≥ 1 rival, or you record that no design exists and ask for a capability | Run an observation no outcome counts against; that is exploration, label it |
| C | Set the conditions and record held/varied; or find them and record what was unavailable | `conditions` set or found | The design's conditions are in hand or their absence is logged | Report a control not run; claim the method of difference when C is found |
| O | Observe with the full chain; add the theory it is laden with to A | observation + provenance | Provenance complete | Use an observation of unknown chain at M |
| M | Compare with each E_i separately | match table | Always, to V | Read a mismatch as refuting H_i alone |
| V | Set C: after a mismatch hold C and vary A; after a match vary A again and remove C; run again. Found C: substitute independent traces and say V is unavailable | `series` or `traces` | The outcome survives the series, or budget is spent (report from V) | Let a claim leave after one run |
| X | Exclude after the series; state the conjunct rejected | verdict | | Reject A or C silently (that is P) |
| P | Revise A or C with reason; return to D | revision | | Protect the same H more than twice without a new prediction |
| K | Retain with status: corroborated, confirmed (state how unlikely E was without H), or best explanation (within the stated set) | claim record (`templates/claim-record.json`) | | Write "proved"; call a best explanation an exclusion |
| R | Split the survivor into subhypotheses; return to G; append, never overwrite | | | |

**Abstain** at any node after M: "not decidable with this evidence; this observation would decide it." It is a result.

## Methods

`strong-inference`: G with n ≥ 2, one S shared by all rivals, C set, V run, every outcome excludes, R then G. `trace-series`: C found, O repeated over independent traces in place of V, K by best explanation; abstain naming the trace that would decide. `natures-repetition`: C found but repeated, a regularity fitted at K with out-of-sample checks in place of V, no mechanism from the fit alone. `exploration-first`: the before-G node as a loop until a phenomenon repeats, then re-run step 0; never emits a claim record. Guards and sources: `references/methods.md`.

## Rubrics you are held to

One reference per question; consult it at that moment, not before. Cite the version you used.

| Question | Reference | Version |
|:--|:--|:--|
| Which node am I at, and what may I do next | the graph, `unit.qmd` section 5 | graph v0.2 |
| What evidence does this kind of claim owe | the mode page for the work in hand, `modes/<mode>.qmd`, exported in `agents/mode-instructions.json` | per mode, 0.4.x |
| What do I emit for a retained hypothesis | `templates/claim-record.json` | 0.4.0 |
| Which method am I running and what is its guard | `references/methods.md` | 0.2.1 |
| Why a rule exists, and who fixed it | `references/nodes.md`; for people revising the rules, not for a run | 0.2.1 |
| Was a rule broken | `references/evaluation.md`; for the evaluator, never loaded by the agent | 0.2.1 |

## Outputs

The node-labelled action log; the composition declaration with the state that chose it; a claim record for every retained hypothesis; on abstention, the deciding observation. Terminal states: warranted claim, principled abstention, reframed question, artifact verdict. Tool outputs and the log are the record; your rationale is not.
