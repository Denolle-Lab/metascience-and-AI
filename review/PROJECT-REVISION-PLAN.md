# Proposed project revision after the two audits

September 10, 2026. Proposal for curriculum v0.4; not an adopted curriculum or a record of group discussion.

This plan compares [Fable's revised audit](MODES-AND-AGENTS-AUDIT-v2.md) with [my revised audit](SCIENCE-OF-SCIENCE-AUDIT-2.md) and the current project. Fable's v2 responds to my **first** report, so several disagreements it identifies were already addressed in my second. The recommendations below supersede the implementation suggestions in my earlier reports. This document proposes changes; it does not apply them to the book.

**There is substantial convergence on the direction, with consequential differences in implementation.** I recommend keeping the thirteen meetings, correcting the documented errors, reorganizing the vocabulary, changing meeting 11's central readings, and making every meeting contribute to a question about scientific advance. The optional research program should begin with documented inquiry episodes and a small controlled agent comparison. Neither a larger bibliography nor a more elaborate agent roster is the immediate priority.

Agreement between the reports helps identify a workable agenda. It is not independent empirical validation: the revisions explicitly draw on one another, and the proposed methods have not yet been tested.

## 1. Where we converge, and what I would decide

| Issue | Convergence | My proposed decision |
|:--|:--|:--|
| Purpose | The project has drifted toward checking claims and hypothesis gates, underweighting generation, representation, question choice, and advance. | Put these generative activities and the breadth hypothesis in the opening statement and every meeting's exercise. |
| Ten modes | Useful starting vocabulary; mixed levels; statistical practice and estimation need explicit treatment. | Retain ten **teaching entry points**, revised below. Use linked descriptions of epistemic work, actions, and context for analysis and agent design. Do not force one decisive category per paper. |
| Historical precedents | Crombie/Hacking and other schemes belong in the framing. | Add a short comparison that explains differences in purpose and granularity. Correspondence with a historical scheme supplies intellectual context, not validation. |
| Evidence | Different claims owe different evidence; exploration cannot universally require a prior hypothesis. | Separate permission to act, commitments made before evaluation, and evidence supporting a claim. Record uncertainty and amendments. |
| Bibliography | Specific citation and wording errors need repair; several additions would improve the science-of-science center. | Correct those first. Add a small, tiered reading set with explicit roles and verified reading boundaries. |
| Breadth | Integration and specialization deserve direct study; prompting several roles does not create independent expertise. | Separate project integration, individual/team competence, and diversity across a portfolio. Keep the breadth hypothesis open. |
| Meeting load | One anchor plus a companion is suitable for an informal club. | Everyone reads the anchor's selected sections; a rotating reader presents the companion. Additional literature remains optional. |
| Research sequence | Small process records before large paper classification. | Start a twelve-episode feasibility sample. Develop a few procedures and their evaluators together, then compare policies. |

Four differences still matter:

- **No compulsory decisive flag.** An episode can contain several consequential moves, and the available record may not identify a dominant one. Permit multiple labels and “cannot determine.” Code an identifiable turning point when useful, with its source; do not make one mandatory for a whole paper.
- **No universal breadth recipe.** Fable retains an overly definite prescription about distant content, conventional context, and exploration/exploitation. The cited studies measure different populations, timescales, and outcomes. Shi and Evans study surprising combinations of both contents and contexts; that does not establish a single optimal interdisciplinary strategy. [Shi & Evans, 2023](https://www.nature.com/articles/s41467-023-36741-4).
- **No verifier-only account of discovery.** External checks make particular gains assessable. They do not resolve question generation, representation change, or all forms of scientific value. Build an initial evaluator alongside a small procedure; revise both when the case exposes a missing construct. Keep subsequent evaluation cases held out.
- **Different reading replacements.** I favor Nersessian–Shi/Evans for meeting 11 and retain the field/infrastructure and implementation/evaluation purposes of meetings 7 and 13. Jones–Kitcher is valuable for specialization; KEKADA–Co-Scientist is valuable for architectural comparison. Neither is a controlled test of the project's central agent hypothesis.

Fable's new distinction concerning registration is useful, with a correction: record commitments relative to **access to relevant evidence**, not simply whether registration preceded data collection. Existing data can support prospective plans under stated access conditions. Blind assessment, a frozen prediction, and a registered analysis plan are related but distinct arrangements. [Center for Open Science, preregistration guidance](https://www.cos.io/initiatives/prereg).

## 2. Reframe the project around three research questions

Replace the opening “Why” bullets in `index.qmd` with a concise version of this purpose:

> Understand how different forms of scientific inquiry produce warranted gains in knowledge, understanding, and capability. Examine when integrating knowledge across fields helps, and when it fails. Use that evidence to design and evaluate scientific agents that improve inquiry and expand the worthwhile questions researchers can pursue.

Make three standing questions explicit:

1. **Advance:** What changed in what researchers could know, explain, measure, or do, and which action made that change possible?
2. **Breadth:** Did integrating another field's methods, concepts, or observations contribute to that gain? What competence and assumptions made the integration work?
3. **Agents:** Which part could an agent perform, and what comparison would establish a benefit at a stated cost?

The claim that agents might make individual polymathy practical remains one hypothesis under question 2. It should not substitute for the broader hypothesis about interdisciplinary advances, which can arise through teams, instruments, institutions, or transfers between communities.

Keep the public book concise, the existing meeting order and URLs, and the drafted/discussed/adopted distinctions. Update the proposed version only when changes are implemented. Do not mark revised readings as adopted before the convenor adopts them, or any page as discussed before a meeting occurs.

**Files:** `index.qmd`, `README.md`, `_quarto.yml`, introductory text in `glossary.qmd` and `agent-design.qmd`.

**Done when:** the purpose, standing questions, and outputs all name advance and integration; participation in the club does not require joining the optional research study.

## 3. Reorganize the modes without pretending the number is settled

### Teaching vocabulary

Use the following ten entry points in `glossary.qmd`. Their purpose is to help participants recognize different work, not partition all physical science into natural kinds.

| Entry point | Change from the current glossary | An evidence question |
|:--|:--|:--|
| Observation, description, and estimation | Add explicit sublabels for direct records and inferred quantities. Remove routine parameter estimation from its default home under simulation. | What makes the record or estimate informative about the target, given coverage, measurement response, and inverse assumptions? |
| Exploratory inquiry | Replace “no hypothesis stated” with investigation that develops phenomena, representations, questions, or candidate explanations. Background theory and provisional hypotheses can be present. | Is the observed feature credible enough for the proposed follow-up, and how provisional is it? |
| Hypothesis assessment | Keep discriminating tests; explicitly link to the separate action of generating rivals. | Which observations distinguish the specified alternatives, and which alternatives remain unresolved? |
| Theory and mechanistic modeling | Separate concept formation, derivation, and empirical application. Remove the requirement that derivation precede observation. | Is the derivation sound under its assumptions? What additional evidence supports applying it to the world? |
| Simulation and prediction | Distinguish forward calculation, scenario exploration, and scored forecasts. | Is the computation adequate for its stated purpose? For a predictive claim, what independent assessment supports its skill? |
| Instruments and observing systems | Retain as a teaching theme and an inquiry activity; also record instrument contribution separately. | Which new observable is available, with what response, calibration, and limitations? |
| Methods and computation | Retain, separating a new method from an established method producing a new estimate. | What can now be recovered or computed, and on which cases does the method fail? |
| Synthesis and reconstruction | Remove “no new intervention”; reconstructions can include newly collected evidence and laboratory work. | How do different traces constrain the account, and which dependencies do those traces share? |
| Replication and robustness assessment | Clarify that validation is purpose-dependent; retain informative failures and corrections. | What survives repetition, perturbation, transfer, or an independent line of assessment? |
| Statistical modeling and empirical regularities | Replace the use-inspired/co-produced row with an explicit statistical family. | What supports the estimated relation or distribution, its uncertainty, and its claimed domain of applicability? |

Use orientation and co-production become separate context attributes, with their current discussion and references retained. They remain important scientific practices. The move prevents the question's social origin from being treated as the same kind of label as an inference or a computation.

Statistical models can encode stochastic mechanisms as well as empirical relationships. ETAS, hazard estimation, and ground-motion modeling can receive multiple labels. Out-of-sample assessment is appropriate to generalization claims; it is not the sole evidence standard for every descriptive estimate. Breiman's two modeling cultures must not be equated with Shmueli's explanation/prediction distinction.

### Analytical representation

Stop declaring that the teaching rows are automatically the corpus codebook and agent controller. Link three descriptions instead:

- **Epistemic work:** characterize, estimate, establish a regularity, construct a model/concept, discriminate, forecast, reconstruct/integrate, assess robustness.
- **Actions:** inspect, explore, calibrate, build, derive, simulate, generate rivals, test, change representation, frame/reframe, transfer, seek missing evidence, defer.
- **Context and contribution:** new estimate/data/method/instrument/concept; understanding/use aims; co-production; infrastructure; question origin; disciplinary resources and constraints.

A tomography episode may estimate a structure, using inversion and sensitivity analysis, and contribute a new regional estimate. A later episode may use that estimate to assess tectonic explanations. This example should appear in the glossary beside a theory case and a statistical case.

Add short historical framing with clearly limited correspondences to Crombie/Hacking. Explicitly distinguish this usage of “mode” from science-policy Mode 1/Mode 2. Pilot the labels against a simpler vocabulary; evaluate coverage, agreement, missingness, and whether the distinctions help identify useful next actions. The most easily coded vocabulary is not automatically the most useful.

**Files:** `glossary.qmd`, `rubrics.qmd`, `notes.qmd`, `corpus-study.qmd`, `agent-design.qmd`; references in session exercises.

**Done when:** estimation and statistical practice have explicit homes; question reframing and rival generation are observable actions; theory, unique events, and reconstruction no longer fail arbitrary recognition rules; unknown chronology is allowed throughout.

## 4. Revise the meetings with a bounded reading load

Every meeting has one anchor and one companion. Everyone reads the selected anchor sections and the companion abstract or equivalent overview. The rotating reader presents the companion in depth. Existing extra discussant papers become optional resources unless a facilitator deliberately substitutes one. No new meeting is needed.

Use a flexible hour: about 5 minutes to frame the question, 10 for the companion, 25 for discussion, 15 for the exercise, and 5 for the shared note. The only routine output is one episode entry and three sentences: **what changed, what evidence supports that account, and what agent action or evaluation follows**. Longer worksheets are reusable resources, not thirteen compulsory deliverables.

| Meeting | Proposed anchor / companion | Specific revision and small output |
|:--|:--|:--|
| 1. Scientific methods | Platt / Cleland | Keep. Facilitator introduces the historical schemes. Compare two cases in which different actions were reasonable; identify a vocabulary rule that fails. |
| 2. Exploratory experiments | Steinle / Karaca, with its erratum attached to the reading | Keep. Distinguish a hypothesis existing, investigators knowing it, and its guiding their actions. Record a representation or question change with source confidence. |
| 3. Historical traces | Atwater / Nelson | Keep. Compare rival histories and the next trace worth seeking. Separate unique-event evidence from repeatability of analysis. |
| 4. Tectonic synthesis | Wilson / Sykes | Keep. Reconstruct concept generation separately from later discrimination. Identify what became thinkable or testable. |
| 5. Measurement | Lindsey 2019 / Lindsey 2020 | Keep. Trace one measurement chain and one inferred quantity; use a facilitator's brief Chang example. State what new scientific question the capability enables. |
| 6. Exploration and confirmation | Tukey / Nosek | Keep. Replace the Ioannidis framing. Separate exploration, planned evaluation, and warranted claims. Use a short empirical-law example; Breiman is optional background. |
| 7. Field and marine research | Powell / Becker | Keep the field/infrastructure purpose. Compare two possible observations under a real resource constraint, including who set the question. Bond remains an optional interpretation case. |
| 8. Serendipity | Moore / Yaqub | Keep. Propose the cheapest informative anomaly follow-up and a defensible stopping condition. A unique event need not recur before any investigation. |
| 9. Models and inference | Oreskes / Beven–Freer | Keep. Distinguish parameter estimation, prediction, and explanation using one example. Shmueli is optional; facilitator summarizes the relevant distinction. |
| 10. Novelty | Uzzi / Fontana | Keep. Find the closest precedent and distinguish bibliographic surprise from a novel contribution. Produce one bounded novelty judgment. |
| 11. Interdisciplinary integration | **Nersessian 2022, selected case / Shi–Evans 2023** | Replace Burke–Kitcher as the central pair. Connect a documented integration process with a large empirical study and its limits. Produce a transfer record and a possible failure test. |
| 12. Scientific advance | Wu / Petersen | Keep the indicator/reanalysis pair. Use the before/after advance profile before showing citations. A short Azoulay discussion introduces research conditions; Dellsén remains conceptual framing. |
| 13. Agent design and evaluation | Boiko / Chen | Keep. Facilitator supplies a brief KEKADA–modern-agent comparison. Specify one procedure, a credible baseline, two failure cases, and the evidence needed to claim improvement. |

For meeting 11, the proposed anchor is **Nersessian chapter 2, “Building Hybrid Simulation Devices: Distributed Model-Based Reasoning,” narrowed to one case after checking the chapter text**. Do not assign the whole book or finalize page boundaries from a publisher description. Its bioengineering setting supplies an intentional cross-field comparison; ask which mechanisms carry over to geoscience. The official publisher confirms an open-access edition and the table of contents confirms the chapter. This resolves Fable's access uncertainty, while leaving the excerpt selection as implementation work. [MIT Press book page](https://mitpress.mit.edu/9780262544665/interdisciplinarity-in-the-making/); [official contents](https://direct.mit.edu/books/oa-monograph/5498/Interdisciplinarity-in-the-MakingModels-and).

Retain Burke, Kitcher, Jones, Leahey, and Teodoridis as alternatives/background for meeting 11. Use Kitcher's division-of-labor argument in the facilitator's framing so that integration is compared with a serious specialization alternative. Rename the displayed session title to **“Interdisciplinary integration: breadth, competence, and scientific advance”**, while retaining `sessions/11-polymathy.qmd` and its slug for stable links.

This is a deliberate compromise with Fable: one substantial central-pair replacement, more science of science throughout, and no larger required reading burden.

### Bibliography changes in three tiers

| Tier | Proposed additions | Use |
|:--|:--|:--|
| Corrections | Separate Si execution-study record; Karaca erratum | Repair the existing citation and accompany the corrected historical case. |
| New central readings | Nersessian 2022; Shi & Evans 2023 | Meeting 11 anchor/companion. |
| Facilitator or optional background | Hacking 1992; Chang 2004; Breiman 2001; Shmueli 2010; Azoulay, Graff Zivin & Manso 2011; Fortunato et al. 2018 | Historical framing, measurement, statistical practice, conditions of discovery, and an orientation to science of science. |

This is a ten-record initial addition proposal, subject to duplicate/version checks. Cite Crombie through an appropriately verified bibliographic record if the page directly discusses his scheme; add that record as an explicit dependency rather than claiming the list remains exactly ten. Other recommendations in both audits remain a candidate pool. Promote existing readings such as Sourati–Evans and KEKADA where useful before expanding that pool further.

For every changed assignment: verify the identity/version, check the relevant text, specify sections and workload, record access, and state what the source supports. Registry metadata establishes identity, not that our interpretation is correct. Azoulay should be described as a funding-program comparison with identifying assumptions, not an isolated causal experiment on tolerance of failure. [Authors' account of the design](https://www.nber.org/reporter/2012number3/production-scientific-ideas).

## 5. Repair factual claims before restructuring

Make these changes as the first small, reviewable editing bundle:

| File or location | Required repair |
|:--|:--|
| `agent-design.qmd`, Si discussion | Separate the ideation and execution papers; cite the execution study for execution findings. Replace “proposes hypotheses badly” with the particular comparison and its limits. |
| `agent-design.qmd`, Oreskes discussion | Distinguish complete verification/validation from partial confirmation; avoid saying open-system models cannot be confirmed. |
| `agent-design.qmd`, anomaly policy | Allow initial investigation to establish reliability. Require evidence appropriate to the subsequent claim. |
| `sessions/02-exploratory-experiments.qmd` | Attach and discuss the Karaca erratum. Do not infer that a hypothesis controlled the experiment merely because it already existed. |
| `sessions/06-exploration-confirmation.qmd` and `glossary.qmd` | Remove Ioannidis as a universal hypothesis-action-gate defender. Describe the paper's false-positive argument and its assumptions. |
| `README.md` | Remove the stale hard-coded 123-reference count, or generate it. The audit found 139 current records; new additions will change that again. |
| `prior-art.qmd`, `agent-design.qmd`, `corpus-study.qmd` | Replace unsupported “first,” “only,” “not measured,” and universal benchmark/architecture claims with scoped statements tied to documented searches. |

Also narrow the glossary's generalizations about interdisciplinarity and AI: distinguish the measured populations and outcomes, and separate individual productivity, collective topic coverage, and scientific advance. Define depth through demonstrated competence and understanding; do not define it simply as the opposite of breadth or infer it from reference concentration.

Use the existing [metadata evidence](audit-evidence/reading-metadata-2026-09-10.json) for the checks it actually documents. Add a concise claim-check record for changed interpretations, including citation key, source location, verification date, evidence basis, and remaining uncertainty. No fresh claim of having read all 139 sources is needed.

## 6. Make the shared record useful without making meetings bureaucratic

Replace the ledger's emphasis on “a gate would have helped/hurt” with **what action was justified next, and why**. A counterfactual gate assessment can remain an optional discussion question; it is a judgment about a counterfactual, not an observed treatment effect.

Use one compact row per episode:

| Field | Record |
|:--|:--|
| Episode and source | Case identifier, source location, record type, contributor/date. |
| Question before → after | Include “unchanged” or “unknown”; keep question origin distinct from later reframing. |
| Action → result | What was done and what changed; attach the relevant artifact where available. |
| Epistemic work | Multiple labels allowed; unknown or insufficient record allowed. |
| Evidence and claim status | What the available evidence supports; provisional, assessed, unresolved, or contradicted, with scope. |
| Next action or agent lesson | One justified action, alternative, or testable capability. |

For the optional process study, expand a record only where needed: information available at the decision time, hypotheses and alternatives, raw inputs/outputs, measurement assumptions, resources, commitments, amendments, disciplinary transfer, and unrecorded steps. Keep contemporaneous statements and retrospective explanations separate. A model's generated explanation is not a faithful process record by default.

For planned evaluation, record **what was fixed, when, which evidence was already accessible, and what changed**. Use explicit unknown/not-applicable states. A mathematical derivation can be assessed for validity without waiting for a future observation; claims of empirical adequacy owe additional evidence.

**Files:** `rubrics.qmd` defines the record; `notes.qmd` holds the public table; session output text links to it. Confidential project artifacts remain in the existing private workflow.

**Done when:** one case can be recorded in the final five minutes; the expanded form supports chronology without inventing it; generation and gain are as visible as checks and failures.

## 7. Turn selected activities into testable agent procedures

The first implementation target should be a small set of procedures that a planner can choose, not one agent personality per mode. The public design document should distinguish **proposed**, **implemented**, and **evaluated**, with evidence links for the latter two. A role roster does not establish performance or independence.

| Procedure | Required input and output | Failure case to include |
|:--|:--|:--|
| Estimate with measurement checks | Target quantity, observations, forward/inverse assumptions → estimate, uncertainty, sensitivity, limits. | Regularization or an instrument change creates an apparent physical feature. |
| Follow an anomaly | Unexpected observation and its provenance → competing artifact/physical possibilities and an informative next check. | Dismisses a unique event automatically, or promotes an unexamined artifact to discovery. |
| Generate and assess rivals | Evidence and present explanation → substantively distinct rivals; separately, observations with different consequences under those rivals. | Produces verbal variants, or proposes a test all rivals pass. |
| Reframe a question | Current question, constraints, unresolved uncertainty → a revised tractable question and why its answer would matter. | Selects an easy task unrelated to the scientific uncertainty. |
| Transfer across fields | Source method/concept and target problem → explicit mapping, assumptions, mismatch, adaptation, and a validating check. | Borrows vocabulary or code while violating the source method's conditions. |

A transfer record should state source and target variables, units/scales, assumptions, mechanism or mathematical correspondence, required expertise, failure conditions, and a check on the target problem. One successful transfer is evidence about that transfer; it does not establish general polymathy.

Start with estimation/anomaly follow-up in a seismic-velocity case, then add transfer as a second experiment. Include physical change, a processing artifact, rival mechanisms, and insufficient-evidence cases. Develop records and evaluation locally before promising a complete autonomous research system or changes to a separate GAIA implementation.

### Controlled comparison

Compare three policies on the same tasks:

1. A competent generic planner, supplied with the same substantive guidance and checks.
2. A hypothesis-testing planner that can still inspect data, calibrate, and obtain missing information.
3. A planner that explicitly selects among the inquiry procedures.

Hold model version, tools, evidence access, action budget, and human assistance comparable. Give each fresh task state; log all interventions and unsuccessful runs. Treat an intentionally rigid hypothesis-before-every-action rule as a separate ablation, not the only hypothesis-testing baseline. A human reference solution can help assess the tasks without becoming an expensive fourth treatment arm.

For a feasible first comparison, prepare six development task packets and six distinct held-out packets, balanced across the failure types above. Run each held-out packet five times under each policy: **90 evaluation runs**, after the development phase. This is a proposed feasibility budget, not a powered study of general superiority. Cases, rather than repeated runs on one case, determine the breadth of the evidence. Expand the independent cases after observing variability and cost; do not treat 90 runs as 90 independent scientific problems.

Freeze the held-out task packets, criteria, budgets, and policy versions before evaluation. Score executable and empirical outcomes where available; use blinded domain assessment for judgment-dependent claims, with disagreement retained. Human assessors should not see the policy label. Synthetic perturbations test the constructed situations; include later prospective or independently documented cases before claiming real discovery benefits.

Report warranted gain relative to the task's starting information, unsupported-claim frequency, inference/prediction performance where applicable, usefulness of next observations, novelty relative to a bounded search, transfer validity, and cost. Assess diversity of worthwhile questions across runs and projects. Keep these outcomes visible separately; explicit utilities may guide action selection if their assumptions and sensitivity are reported.

The transfer experiment should compare access to the same cross-field material with and without the mapping/check procedure. That tests integration practice rather than simply more retrieval. Include cases where transfer is useful and where a specialist method is sufficient or the transfer fails. Improvements in calibrated restraint without any useful new work should not be presented as improvements in discovery.

**Files:** revise `agent-design.qmd`, the evaluation section of `rubrics.qmd`, and meeting 13. Add executable benchmarks only as a subsequent, explicitly scoped implementation task.

## 8. Keep two distinct research tracks

### Inquiry episodes: how work proceeds

Begin with twelve purposively selected episodes: six with existing dated records and six from ongoing work when available. This is a target sample, not a claim that the records already exist. Include ordinary successful work, corrections, failed paths, estimation, theory, statistical regularity, and both useful and unsuccessful transfer. Include at least a second physical-science setting to probe portability; a bioengineering teaching case alone does not establish physical-science coverage.

Two readers independently annotate an initial subset before reconciling it. Record missing evidence and disagreements; revise the vocabulary, then assess additional episodes without silently recoding away the difficulties. Do not estimate population frequencies or causal benefits from this selected sample.

The output is an evidence-linked set of actions, transitions, and failure conditions that can inform the agent procedures. A twelve-episode feasibility study and the twelve benchmark packets above are different objects: benchmark packets may be constructed from suitable episodes, with provenance and limitations stated.

### Published contributions: what the literature reports

Retain the corpus study as a separate optional project. It can study presented contributions and associations with later uptake. It cannot reconstruct unreported trajectories from article structure alone.

Before scaling:

- Specify the target scientific population and screen subject matter within broad journals.
- Pilot multi-label annotation, explicit estimation/statistical labels, and unknown/uncodable cases. Separate abstracts-only from full-text evidence.
- Preserve a probability-based component for population estimates; add targeted rare-mode cases for evaluation and report that enrichment separately.
- Report per-label agreement and performance, label prevalence, access-related missingness, and uncertainty. A fixed 300-paper holdout is not a guarantee of adequate rare-label coverage.
- Treat disciplinary reference diversity as one proxy. Measure substantive integration on a coded subset; assess competence separately from reference concentration.
- Separate novelty, knowledge/capability gain, and citation uptake. Specify comparable follow-up windows and account for incomplete follow-up.
- State a causal question and identifying assumptions before presenting an association as a breadth effect. Field and year adjustment alone does not establish causality; distinguish potential confounders from mediators.

**Files:** `corpus-study.qmd`, `prior-art.qmd`, shared definitions in `glossary.qmd` and `rubrics.qmd`.

The potentially valuable contribution to AI and science is evidence about **which inquiry procedures improve which tasks under which conditions**, plus a usable method for observing and assessing those procedures. Logs and mode labels are supporting instruments. Their existence alone is not the research result, and priority claims require a scoped prior-art search.

## 9. Implementation bundles and consistency checks

| Order | Editing bundle | Files and dependencies | Acceptance condition |
|:--|:--|:--|:--|
| 1 | Correctness | `agent-design.qmd`, sessions 2/6, `glossary.qmd`, `README.md`; corresponding `references.bib` and `curriculum.json` records | Each corrected claim has the right source and scope; the erratum is visible to readers. |
| 2 | Purpose and vocabulary | `index.qmd`, `glossary.qmd`, `rubrics.qmd`, `notes.qmd`, `corpus-study.qmd` | The three descriptions agree across pages; no compulsory single mode or invented chronology. |
| 3 | Readings and meeting format | All thirteen session pages; meeting 11 title/pair; `curriculum.json`, `references.bib`, `READING-AUDIT.md`, `index.qmd`, `notes.qmd` | One anchor and companion per meeting, bounded excerpts, optional tiers, explicit assignment status. |
| 4 | Agent and study specifications | `agent-design.qmd`, `prior-art.qmd`, `corpus-study.qmd`, evaluation rubric, meeting 13 | Procedures, comparable baselines, feasible pilot, separate outcome constructs, no unsupported implementation/priority claims. |
| 5 | Generated content and release documentation | `tools/build_bibliography.py`, `tools/validate.py`, generated `bibliography.qmd`, `README.md`, `VALIDATION.md`, `_quarto.yml` | Metadata, visible reading roles, counts, links, citations, and rendered pages agree. |

Keep the existing `pair` array in `curriculum.json`: define its first element as the anchor and second as the companion, and document that ordering. The current schema already requires exactly two entries. Update the bibliography generator to print those roles separately, and align each session's reading instructions. Move former extra discussant assignments into `optional` where appropriate, preserving their references and useful context. This avoids a new parallel assignment schema.

Use the existing validation tools rather than adding a second framework. Extend checks only for new invariants, such as consistency of reading-role labels if they become machine-readable. Regenerate the bibliography, run `.venv/bin/python tools/validate.py`, check changed external links with `.venv/bin/python tools/check_links.py`, and run `quarto render`. Inspect the revised glossary, meeting 11, bibliography, and ledger in the rendered book for overflow and usable navigation. Update `VALIDATION.md` with what was actually checked; link success does not establish interpretive correctness.

The repository's contribution instructions call for an issue before changing assigned readings. Handle that coordination when implementing the reading-change bundle; this proposal neither creates an issue nor commits an assignment change. Preserve the existing audits as dated advice. Do not alter private notes, mark group consensus, or publish the site as part of preparing this plan.

## 10. Recommended sequence of commitments

**First, revise the book.** Complete the correctness, purpose, vocabulary, reading, and specification bundles. These changes have value even if no research experiment follows.

**Then, use a few meetings to test the instruments.** Start with three contrasting episodes and the compact ledger. Revise the form if it consumes the discussion or fails to capture the action that mattered. Finish the twelve-episode feasibility sample only if the records prove informative.

**Then, test one architectural claim.** Begin with whether explicit selection between estimation, anomaly follow-up, and hypothesis assessment improves warranted task outcomes under a fixed budget. Test cross-field transfer separately once its task cases and checks are credible.

**Scale after those results justify it.** A larger corpus can characterize reported scientific contributions; a broader agent evaluation can test generalization; prospective studies can examine whether the interventions actually change research choices and gains. None should be a prerequisite for an enjoyable and intellectually useful reading club.
