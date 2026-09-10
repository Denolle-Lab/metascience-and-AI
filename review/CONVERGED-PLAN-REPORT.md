# Scientific advance as the objective: convergence report and revised plan

September 10, 2026. Initially prepared against the user's clarified objectives, [PROJECT-REVISION-PLAN.md](PROJECT-REVISION-PLAN.md), and Fable's [REVISION-PLAN.md](REVISION-PLAN.md). Updated to incorporate [Fable's CONVERGED-PLAN.md](CONVERGED-PLAN.md): section 8 records the additions and qualifications, and the implementation details below incorporate them. This is a proposed consolidation, not an implemented curriculum or an adopted group decision.

**Both plans can lead toward the project you describe, but neither is sufficient as written.** Both support plural inquiry, evidence from human scientific practice, and comparative agent evaluation. Both still leave too much room for the result to become a well-audited scientific assistant whose contribution to scientific advance is unclear. Your clarification establishes the missing hierarchy: **scientific advance is the main outcome; novelty, correctness, and impact help characterize and assess it; human-defined epistemic modes organize how agents pursue it; past scientific work supplies both design evidence and evaluation cases.**

The main required change is therefore architectural and evaluative, not another expansion of the reading list.

## 1. Initial assessment of the two revision plans against your requirements

| Requirement | My original revision plan | Fable's REVISION-PLAN.md | Change needed for convergence |
|:--|:--|:--|:--|
| Scientific advance is the primary outcome | Prominent in the purpose, but presented alongside breadth and agent performance; evaluation lists many outcomes without a primary endpoint. | Includes warranted gain among evaluation outcomes; gives more implementation detail to labels, gates, and audit fields. | Put advance above the supporting measurements and define the primary outcome before choosing agent components. |
| Novelty, correctness, and impact are measured | Separates the constructs and proposes bounded novelty searches; lacks a fully operational measurement protocol. | Makes similar distinctions and retracts several overclaims about impact studies. | Specify what is measured, the reference frame, timing, uncertainty, and how the measurement bears on advance. |
| Agents are organized around human-defined epistemic modes | Selectable procedures are explicit; human authority over the definitions and their translation into procedures is underspecified. | Three layers and changes to the agent roster are explicit; modes can still become labels attached to generic behavior. | Make a versioned, human-defined mode specification the contract between the literature, agent, and evaluator. |
| Modes fit geosciences and borrow appropriately | Geoscience cases and cross-field transfer are central. | Similar, with useful additions concerning existing seismological evaluation infrastructure. | Cover multiple geoscience practices; justify borrowing through a documented correspondence of problems, assumptions, and evidence. |
| Science of process/impact, philosophy, and history inform design | All are represented, often as framing or optional reading. | Richer reading pool and links to prospective records, but no systematic source-to-design chain. | Require a traceable account of which source informs a definition, procedure, evidence standard, or prediction of benefit. |
| Evaluate agents against past scientific work | Past episodes inform design; the initial benchmark emphasizes local task packets and synthetic failures. | Retrospective records inform design; the main comparison also uses the velocity-change project. | Build explicit suites for historical decision reconstruction, reproduction of past results, and extension beyond a supplied starting point. |
| Demonstrate that modes improve science | Fair planner baselines are proposed. | Substantially the same baselines, with a more concrete roster mapping. | Compare scientific gains and show that mode structure contributes beyond additional instructions, checks, or computation. |

Fable's `REVISION-PLAN.md` accepted the corrections concerning a universal breadth recipe, causal interpretations of funding comparisons, historical discovery systems, and verification examples. Those are **resolved differences** for this consolidation. My earlier plan's statement that Fable retained the breadth recipe describes its earlier audit and should not be carried forward as a criticism of `REVISION-PLAN.md`.

That document's statement that all structural questions were resolved was nevertheless too strong. Your clarification exposed choices about the primary outcome, the authority and function of modes, and the role of historical evaluation. Both subsequent convergence reports address those choices; section 8 compares the remaining implementation differences.

## 2. Establish the objective and measurement hierarchy

Use this as the project's working charter:

> We study how scientists produce advances in knowledge, understanding, and research capability through different epistemic modes of inquiry. We define these modes from geoscientific practice, informed by the science of scientific process and impact, philosophy of science, and history of science. We design agents around those human-defined modes and evaluate their ability to produce warranted scientific gains against documented past work and, subsequently, new research. We measure novelty, correctness, and impact to understand the character, support, and consequences of those gains. We test when interdisciplinary integration helps produce them.

This makes advance the organizing objective of this project without claiming that philosophy has settled a universal definition. For example, Dellsén argues for an understanding-based account rather than identifying progress with accumulated knowledge. That disagreement should inform the club's working definition. [Dellsén, 2016](https://doi.org/10.1016/j.shpsa.2016.01.003).

### What is an advance in this project?

A **demonstrated advance** is an evidenced improvement, relative to an explicit starting state, in what can be known, explained, predicted, measured, or investigated. Record the particular gain and why it matters scientifically. An enabling capability counts when its performance and scientific relevance are demonstrated; a promise that a tool might someday help is prospective value.

Assess contributions at the scale on which they occur. A calibration, a well-supported correction, or a result that excludes a plausible mechanism can advance a project without being a new theory. A routine activity can support a later advance without constituting one by itself. The same distinction applies to scientists and agents.

Three reference frames must remain visible:

- **Task or project advance:** improvement beyond the information and capabilities supplied at the start.
- **Historical advance:** what a contribution added relative to knowledge available at its historical date.
- **Contemporary field advance:** what an output adds beyond currently available scientific knowledge.

An agent reproducing a known discovery can demonstrate task competence. That does not constitute a new contemporary discovery.

### How novelty, correctness, and impact enter

| Assessment | Operational measurement | Role in evaluating advance |
|:--|:--|:--|
| **Novelty** | Identify the exact contribution, dated reference corpus, closest precedents, and the component that differs. Record precedent-search coverage and uncertainty. Bibliographic or semantic distance can supplement this assessment. | Describes what changed relative to prior work. High novelty alone provides no warrant or scientific importance. Replication may add independent evidential support without a novel substantive claim. |
| **Correctness and evidential warrant** | Use claim-appropriate checks: mathematical validity, empirical error, uncertainty coverage, measurement response, sensitivity, independent observations, or robustness to alternatives. Record contradicted, unresolved, and supported components separately. | Determines whether the claimed gain is justified and within what scope. In many geoscience cases we can assess evidential support and adequacy rather than directly measure final truth. |
| **Impact** | Record observed downstream use in later explanations, experiments, datasets, instruments, methods, or decisions. Add field/time-qualified citation measures where relevant. State the observation window and distinguish realized impact from predicted impact. | Shows consequences and reach over time. Missing or delayed uptake does not by itself refute a demonstrated gain; popularity cannot validate an incorrect claim. |
| **Scientific advance, the primary outcome** | State the before/after change, measure it in terms appropriate to the case, and assess its scientific significance using the evidence above. | Answers whether meaningful scientific progress occurred within the stated reference frame. |

Do not define advance as `novelty × correctness × impact` or a default weighted sum. Such a formula would, for example, assign no value to an important correction with little immediate uptake. Conversely, reporting three separate scores without judging the actual gain would leave your main objective unmeasured.

### A practical primary endpoint

For each evaluation case, humans should specify **before running agents**:

1. The starting knowledge/capability and unresolved scientific question.
2. A meaningful gain that could be demonstrated, plus how an unanticipated valid gain will be assessed.
3. Observable evidence sufficient to support that gain at its claimed scope.
4. The independent measurements or expert judgments used to assess it.

Where possible, quantify the gain in scientific units: improved resolution at comparable uncertainty coverage, better forecast skill against a defined baseline, a validated new measurement range, or a reduced set of explanations supported by discriminating evidence. For less directly commensurable gains, use blinded comparative expert judgments with written evidence and retained disagreement.

The initial cross-case summary can be the **fraction of cases achieving a prespecified meaningful, warranted gain**, reported by mode and case family, alongside the magnitude and nature of each gain. This is a pragmatic benchmark endpoint, not a universal scale of scientific progress. Unsupported gains do not count; incomplete cases stay in the denominator. Successful identification of a genuine limit can count where it resolves a substantive uncertainty, while generic abstention does not.

Report novelty, warrant, later impact, cost, and failure patterns alongside that endpoint. Assess sensitivity to human thresholds and case selection. At action-selection time, an agent can estimate the expected contribution of an action to advance under a budget; that estimate is a design hypothesis, distinct from the subsequently observed outcome.

Preserve a dated assessment at the original decision point and append later evidence rather than rewriting the original judgment. Separate the claim's empirical or mathematical adequacy from whether the investigator was justified in asserting it with the information then available. Record subsequent corroboration, contradiction, revision, or absence of an informative check. Continued use or the absence of a reported contradiction does not establish correctness. Section 8 specifies the shared claim record and follow-up fields.

## 3. Make human-defined modes the design foundation

Your requirement is stronger than “the agent may choose several tools” or “the agent labels its work afterward.” A mode must change how it frames a task, selects actions, handles evidence, and judges what it has achieved.

Keep the useful three-part distinction from both plans, with one clear relationship:

> **Humans define an epistemic mode by its purpose and standards of evidence. Its agent implementation supplies relevant actions and transitions. Context records where and under what constraints those actions are appropriate.**

These are linked views of an explicit mode specification, not three competing taxonomies. Human definitions can be revised when cases expose omissions or ambiguity. Agents may propose revisions and recognize unfamiliar work; they should not silently redefine a mode or its success conditions during evaluation. Human authorship does not require approval of every routine action.

### The mode specification

Each mode should have one short, versioned specification containing:

| Element | Required content |
|:--|:--|
| Epistemic purpose | What kind of knowledge, understanding, or capability gain it can produce. |
| Applicability | Situations, available evidence, and constraints in which it is useful; limits of that applicability. |
| Representations and actions | What the agent must be able to represent and do; how it generates possibilities as well as assesses them. |
| Evidence standards | What warrants its different claims, including provisional findings and unresolved outcomes. |
| Transitions | When to continue, change representation, enter another mode, acquire evidence, or stop. These are conditional policies, not a fixed universal sequence. |
| Failure conditions | Scientific errors, misleading proxies, and circumstances where the procedure adds no useful gain. |
| Human evidence base | Specific source passages or artifacts, their record types, what they establish, and the inference from them to the proposed design. |
| Evaluation cases | Past successes, failures, and boundary cases; expected scientific gains; independent assessment method. |

Adopt Fable's proposal for one authoritative public specification per mode in `modes/*.qmd`, with an index linking them from the glossary. Derive agent instructions and evaluation references from those specifications, recording the source version; avoid separately maintained definitions in the book, agent skill, and benchmark. Translating a specification into executable behavior still requires implementation and testing. Detailed confidential case records can remain private. Missing evidence from a scholarly tradition should be explicit rather than filled with an irrelevant citation.

Use the existing mode definitions as the starting material. Make **inferential estimation** and **statistical modeling/empirical regularities** explicit specifications. Preserve exploratory inquiry, theory, historical reconstruction, instruments, methods, and robustness. Move use orientation/co-production to context while retaining their consequences for question choice and evaluation.

I would now relax my earlier recommendation to preserve exactly ten teaching entries. Starting from the existing ten, moving one orientation to context and adding two explicit profiles yields eleven initial profiles if the other definitions are retained. That is a transparent provisional result, not a claim that there are eleven natural kinds of science. Merge or split them for a documented scientific reason, not to recover a preferred count. Shared actions and overlapping episodes are expected.

### Evidence from three scholarly traditions

| Tradition | What it contributes to a mode specification | What it does not establish by itself |
|:--|:--|:--|
| Philosophy of science | Epistemic aims, distinctions among evidence and claims, accounts of explanation, measurement, and progress. | How often scientists follow a practice, or that its agent implementation improves outcomes. |
| History of science | Situated sequences, conceptual and instrument changes, alternatives, constraints, and retrospective consequences. | A unique optimal path or a complete record of everything investigators considered. |
| Science of scientific process and impact | Observed behavior, organizational conditions, patterns of combination, uptake, and outcomes; comparative evidence where available. | A universal causal recipe transferable unchanged to an individual agent. |

For each proposed agent rule, distinguish **documented practice**, **normative argument**, **empirical association**, and **our implementation hypothesis**. A rule can be worth testing without every tradition endorsing it. The required property is traceability and an honest statement of the inferential step.

For example: a documented reconstruction may show scientists seeking a trace that separates rival histories. A philosophical argument explains why that trace is probative under specified assumptions. The agent design then proposes an action for identifying discriminating observations. Whether that implementation improves an agent's scientific gains remains an experimental question.

## 4. Make evaluation against past work a central deliverable

Both plans use past work mainly to inform design. Your objective requires it also to organize the evaluation. Create a **historical case bank**, with three complementary uses.

| Suite | What the agent receives and does | What a successful result establishes |
|:--|:--|:--|
| **Decision reconstruction** | Receives evidence available at a documented decision point; proposes questions, representations, actions, and evidence requirements before later artifacts are revealed. | Whether its proposed inquiry is defensible from the supplied information, including useful alternatives to the path scientists actually took. |
| **Reproduction and reassessment** | Receives a past claim, data, and available methodological record; reproduces, qualifies, or challenges the result using inspectable outputs. | Reliability of execution and claim assessment; identification of real limitations or corrections. |
| **Extension and transfer** | Receives an established result or method and a held-out region, time period, observable, or related scientific problem. | Whether it produces a warranted gain beyond the supplied result and transfers competence under appropriate assumptions. |

A paper can support reproduction without supporting a reliable reconstruction of its discovery. Assign cases to suites according to their actual records; do not invent chronology to fill a template.

### Contents of a case

Each case needs a scientific question, explicit starting information, data/artifact links, dated evidence boundaries, documented human actions where known, later findings kept separate, known limitations or reanalyses, mode specifications it probes, outcome criteria, and contamination status. Record what the historical work gained and what later work established about its correctness and impact. Keep those later assessments hidden from the agent when the task requires an earlier information state.

Use the existing club cases first to develop the definitions and examples: coastal earthquake reconstruction, tectonic concept formation and testing, exploratory experimentation, sensing/measurement, and model uncertainty. For executable evaluation, first inventory the group's completed projects and prioritize those with usable dated artifacts. Four to six projects are a reasonable candidate pool, subject to availability, permissions, and mode coverage; their existence and suitability have not been established here. Reserve whole projects or closely related case families for evaluation so that a development episode does not reveal a held-out episode from the same project. Add external cases for coverage beyond the group's habits. Include inversion/estimation, an empirical-law or forecast case, and a documented transfer, as well as ordinary contributions, unsuccessful approaches, and corrections.

Reuse existing infrastructure where appropriate. The SIV project provides forward-modeling and earthquake-source inversion benchmarks; SeisBench provides infrastructure for seismological ML datasets and models. These are useful components of capability evaluation, not complete measures of scientific advance. [Mai et al., 2016](https://www.usgs.gov/publications/earthquake-source-inversion-validation-siv-project); [Woollam et al., 2022, author preprint](https://arxiv.org/abs/2111.00786).

ScienceAgentBench supplies a relevant model for extracting executable tasks from published research: its tasks are validated by experts and evaluated through programs, results, and costs. Our proposed extension is to specify epistemic modes and scientific gains beyond task completion. That is a proposed contribution, not an assertion of priority. [Chen et al., 2025](https://arxiv.org/abs/2410.05080).

### Historical work is evidence, not an answer key for behavior

Score the scientific adequacy of an agent's path, not its similarity to a famous scientist's sequence. Humans may have followed a resource-constrained or suboptimal route. A different defensible route can succeed; a familiar narrative without the necessary calculation or evidence should fail.

Distinguish two comparisons:

- **Relative to past science:** What result or capability did the historical work establish, and can the agent reproduce, reassess, or extend it?
- **Relative to another agent policy:** With comparable information, tools, and budgets today, does the human-defined mode structure improve scientific gains?

Historical human effort often cannot be measured comparably. Do not claim that an agent outperformed the original scientists because it uses modern tools and later knowledge to obtain an old result quickly.

Famous historical answers may be present in model training. Removing a paper from retrieval does not remove that knowledge. Historical reconstruction is therefore a pedagogical and diagnostic test with explicit contamination limits. Use independently held-out artifacts, altered cases that preserve the scientific issue, unfamiliar regional applications, and later prospective work for stronger generalization evidence. Such variants need scientific checking and are not themselves historical records.

## 5. Test whether mode-based design contributes to advance

Retain the shared three-policy comparison: a competent generic planner, a hypothesis-testing planner, and a planner implementing the human-defined modes. Supply equivalent substantive guidance, evidence access, tools, and budgets. The hypothesis-testing planner can inspect and calibrate. Keep an artificially strict hypothesis-before-every-action rule as an optional ablation.

Make the main hypothesis explicit:

> On held-out scientific cases, organizing an agent around human-defined epistemic modes increases the frequency or magnitude of warranted scientific gains under comparable resource constraints.

Evaluate both **mode competence** and **mode selection**. First supply a mode to test whether its procedure works. Then let the agent select and transition among modes. This distinguishes an ineffective implementation from poor routing.

Add a small ablation that preserves the instructions but removes explicit mode organization. That helps distinguish benefits from more guidance from benefits of the mode structure itself. Use observable actions and artifacts to establish that a purported mode change affected behavior; fluent labels are not evidence.

Independent humans define and review the case rubrics, and assess judgment-dependent outcomes without policy labels where practical. Executable checks and independent scientific evidence supply the parts of evaluation they can support. Human judgments also need agreement checks and explicit uncertainty.

The breadth hypothesis is subsidiary and important: **does appropriate interdisciplinary integration increase the scientific gain?** Compare the same access to external material with and without a procedure for mapping concepts, variables, scales, assumptions, and validation conditions. Include beneficial, irrelevant, and invalid transfers. Measure project gains, competence, and portfolio diversity separately; a more diverse bibliography alone is not successful integration.

My earlier ninety-run proposal remains a possible engineering budget, not a scientific sample-size justification. Choose the case families and primary outcomes first; use development runs to estimate feasibility and variability, then set the held-out evaluation budget. Repeated runs on the same historical case do not supply independent examples of scientific practice.

## 6. The consolidated project changes

The following packages replace the competing implementation priorities in the two plans. They preserve the thirteen-meeting format and separate attendance from the optional implementation/research workload.

| Order | Change and files | Concrete completion condition |
|:--|:--|:--|
| 1 | **Correct the documented errors** in `agent-design.qmd`, sessions 2/6, `glossary.qmd`, reference records, and README. | Sources and claim scope agree; Karaca's correction accompanies the reading. Avoid replacing “strongest action-gate case” with the still unsupported “strongest claim-gate case.” |
| 2 | **Adopt the outcome hierarchy in the draft materials:** `index.qmd`, `rubrics.qmd`, `glossary.qmd`, `agent-design.qmd`. | Advance is named as the primary outcome. Novelty, correctness/warrant, and impact have distinct measurements and explicit reference frames. |
| 3 | **Write human-defined mode specifications:** one authoritative `modes/*.qmd` file per profile, indexed from `glossary.qmd` and `_quarto.yml`. | Each initial mode links purpose, actions, evidence, transitions, past cases, and its predicted contribution to advance. Agent instructions identify the source version. Unverified source interpretations are marked pending. |
| 4 | **Create the historical evaluation specification:** proposed `historical-evaluation.md`, linked from `rubrics.qmd`, `prior-art.qmd`, and session 13. | The three suites, evidence boundaries, human reference work, outcome measures, and contamination limits are explicit. At least three contrasting cases are fully specified before a large case bank is promised. |
| 5 | **Align meetings and reading roles:** session pages, `curriculum.json`, `references.bib`, generated bibliography, index, and reading audit. | Each meeting connects a documented scientific gain to a mode specification and an evaluation case; required reading remains bounded. |
| 6 | **Specify the agent implementation and comparison:** `agent-design.qmd`, the claim-record template in `rubrics.qmd`, and the existing agent/vault mapping once its state is inspected. | Mode definitions affect executable behavior. Claims link to evidence, dated assessments, and case outcomes. Proposed, implemented, and evaluated capabilities are distinguished. Primary outcome and fair comparisons precede runs. |
| 7 | **Specify measurement at two scales:** `corpus-study.qmd`, episode-record guidance, and prior-art search record. | The agent evaluation includes a bounded reference sample and claim-level assessment. A larger corpus study supplies population estimates if undertaken; it is not required for the first agent comparison. |

No audit relocation or major new software framework is needed to start. Retain the existing bibliography/validation workflow. Public pages remain concise; detailed specifications can initially be repository documents. These are proposed files, not files created by this report.

### How the meetings change under this objective

Introduce the working definition of advance in **meeting 1**, rather than waiting until meeting 12. Use a short, selected Dellsén passage as facilitator framing with Platt–Cleland; do not add a third full assignment.

For **meetings 2–9**, add the same four questions to the case exercise: what was gained, what evidence warrants it, which mode/actions enabled it, and what an agent would need to demonstrate on a comparable case. Each discussion contributes one brief case-to-mode record, not a complete benchmark.

Keep **meeting 10** focused on quantifying novelty and its limits. Choose **integration** as the central question for **meeting 11**, using the Nersessian case and Shi–Evans pairing; specialization remains a serious comparison. Your clarification resolves that choice without requiring another menu of alternatives.

Rename the displayed focus of **meeting 12** to **“Assessing scientific advance: novelty, correctness, and impact.”** Retain Wu–Petersen as the citation-indicator case, but organize the exercise around before/after gains and the primary-outcome rubric. This prevents a debate about one impact indicator from standing in for the whole outcome.

Make **meeting 13** review one complete chain from human scientific evidence to a mode specification, an implemented or proposed procedure, a claim record, and a historical evaluation case. Boiko–Chen remains a useful implementation/evaluation pair; the historical discovery-system comparison explains the precedent for learning agent design from human inquiry.

Use the source-to-design record to expose disagreements that matter: whether a practice occurred, whether it was epistemically justified, and whether formalizing it would help an agent are three different questions.

## 7. What this consolidation commits the project to testing

The project should produce three connected deliverables:

1. **A human-defined account of plural epistemic modes**, grounded primarily in geosciences and explicitly informed by relevant work from other disciplines and the three scholarly traditions.
2. **Agents whose behavior implements those definitions**, including generation, representation change, measurement, inference, synthesis, and appropriate assessment.
3. **Evidence of scientific gains against documented past work**, with novelty, correctness/warrant, and impact measured in their appropriate roles, followed by prospective evaluation when feasible.

This changes my earlier plan in four material ways: advance becomes the explicit primary endpoint; human mode specifications become the design contract; historical evaluation becomes a central deliverable; and a small anomaly/estimation pilot is recognized as one initial test rather than adequate coverage of plural science.

Fable's operational mapping and my curriculum/evaluation structure are compatible once those changes are made. The resulting research question is concrete: **does organizing scientific agents around human-defined epistemic modes help them produce greater warranted scientific advances, and on which kinds of problems?** The plan must allow the answer to be mixed, and use those differences to improve both the modes and the agents.

## 8. Additions from Fable's CONVERGED-PLAN.md

Fable's consolidated report strengthens the implementation of the shared scope. I would adopt five additions, with the adjustments below. These extend the agreed emphasis on advance; they do not reopen the choice between advance and breadth as co-equal objectives. Breadth remains a candidate contributor to advance, consistent with the user's original hypothesis.

### 8.1 One shared claim record, linked to the scientific gain

Adopt the claim card as a common interface between mode execution, the notebook, and assessment. Use it for substantive findings, conjectures, or capability claims rather than requiring a full novelty search after every tool call. Exploratory actions that have not produced a claim should still record observations and changes of direction.

| Field | Required content |
|:--|:--|
| Identity and context | Claim ID, case/project, date, claim text and scope, mode IDs and specification versions. |
| Contribution to advance | What changes relative to the starting state, why it matters, and which case-level gain it supports. |
| Novelty | Reference date, bounded search, closest precedent, new component, uncertainty. |
| Warrant and adequacy | Evidence required and supplied; assumptions; checks and their results; unresolved or contradicted components. |
| Status and history | Conjectural, provisional, supported within scope, contradicted, or unresolved; dated revisions with the original assessment preserved. |
| Impact | Observed uptake with sources and dates; separately, any forecast with target, horizon, and a way to check it later. |
| Provenance and dependencies | Data/code/source artifacts, dependencies on other claims, and assessor judgments with reasons. |

Link related claim records so the assessment can distinguish a new result from an assumption inherited from another claim. Score the **case-level scientific gain** as the primary outcome. Counting cards or rewarding each separately would encourage claim proliferation and double-count the same advance. Fable's proposal that a card is the scored unit is useful for diagnosis, but insufficient as the primary endpoint.

Use the mode's evidence requirements as the warrant rubric for the relevant claim, without identifying correctness entirely with checklist completion. A procedure can be followed correctly and its conclusion later overturned; a lucky correct answer can lack warrant. This distinction is especially important when assessing historical decisions.

### 8.2 Separate immediate assessment from later scientific history

Adopt Fable's insistence on time-indexed novelty, later checks, and dated impact predictions. Add a follow-up record with states such as corroborated, challenged, narrowed, overturned, and no informative follow-up located, each supported by a source and search date. This can track what science learns about a claim without treating “survival” as truth.

Citations, correction notices, and reports of failed replication can help locate later evidence. They should initially be treated as **signals of reception or reassessment**, not validated correctness proxies. A notice may concern a peripheral error; a contradiction may concern different conditions; an unchallenged result may never have been seriously tested. Validation requires claim-level expert review, including cases with little attention, and cannot establish inaccessible ground truth merely by agreement among coders.

When replaying past work, the original paper's impact is part of the historical reference record. An agent's alternative proposal does not inherit that impact automatically. If its output recovers the historical contribution, record that relationship; if it proposes a different contribution, its impact is unobserved unless separate evidence exists. Assess decision quality using the evidence available at that point, and eventual adequacy using later evidence. A later answer does not make an earlier warranted abstention wrong.

Add Bird (2007) alongside Dellsén as optional framing for meeting 12. Bird explicitly defends scientific progress as accumulation of knowledge; this gives the understanding-based account a direct comparison. It does not establish Fable's proposed equation of advance with newness, correctness, and uptake. [Bird, 2007, author institutional record](https://kclpure.kcl.ac.uk/portal/en/publications/what-is-scientific-progress/).

### 8.3 Combine task suites with source categories

Keep the three task suites in section 4: decision reconstruction, reproduction/reassessment, and extension/transfer. Add Fable's three source categories as a second axis: the group's completed projects, external historical cases, and prospective or otherwise newly held-out cases. They answer different questions: **what capability is tested**, and **where its evidence comes from**.

Prioritize well-documented local projects for the first executable cases, with external cases checking whether the modes travel beyond local practice. Authors can reconstruct records and explain ambiguities; include another qualified assessor where feasible rather than relying exclusively on the people who conducted the project. Private details may reduce exposure, but neither privacy nor a publication date establishes that a model could not know the answer through another route.

Adopt a contamination assessment, but change Fable's “known/partly known/unknown” labels to **evidence of prior knowledge detected / no evidence detected by these probes / exposure unresolved**. Record the exact frozen model version, publicly documented training bounds if available, retrieval and tool access, probe design, and artifact history. Run probes separately from evaluation contexts so they do not supply answers to the evaluated agent.

A failed recall probe cannot certify no training exposure, and process scores can also benefit from knowing the eventual answer. A post-cutoff publication may have an earlier preprint, and a deployed system may receive later information. Report sensitivity across exposure categories rather than granting “no leakage” status after a negative probe. Research has demonstrated contamination that escapes tested detectors; that supports caution about negative findings, not an allegation about the models used here. [Dekoninck et al., 2024](https://arxiv.org/abs/2402.02823).

### 8.4 Add empirical reference distributions in stages

Fable is right that quantitative comparisons become more informative when a contribution is placed among comparable past contributions. Add a **bounded reference sample** to the initial evaluation design: explicit selection criteria, dated novelty assessments, claim-level warrant assessment, comparable follow-up windows, and uncertainty. This supports comparison with the selected cases without claiming population base rates.

A larger probability-based corpus can later estimate mode prevalence and distributions of measured novelty and impact, conditional on field, period, and coverage. Put those profiles in the mode specifications with their population and limitations. Use them as descriptive context, not as universal ceilings, correctness measures, or a prescription to pursue only historically popular modes. Otherwise the reference distribution could penalize precisely the unusual advances the project seeks.

I would not adopt “the corpus study is the only source of quantification” or make the full study a prerequisite. Direct scientific performance measures, claim-level comparisons, and existing published datasets already permit quantification. A bounded prior-art search can establish the closest known precedent without estimating a whole field's novelty distribution. **The full corpus is necessary for claims about population patterns, not for every quantitative agent evaluation.** The initial reference sample belongs in the evaluation; scaling the corpus remains a separate research commitment.

### 8.5 Calibrate the advance judgment without turning contribution types into ranks

Adopt Fable's proposal to test assessors' judgments on the seminar cases before scoring agents. Use independent ratings, retain disagreements, revise ambiguous criteria on development examples, and freeze the final protocol before held-out evaluation. Agreement demonstrates consistency, not by itself validity.

Do not use `none → incremental → enabling → field-shaping` as an ordinal scale. Enabling is a contribution role; field-shaping describes downstream reach. An enabling contribution can be incremental or transformative. Record contribution type separately from the magnitude of the evidenced gain and its later reach. Keep the primary case-success endpoint and case-specific quantitative measures from section 2; add comparative judgments of significance where necessary.

Use two assessment passes where feasible: first judge the evidenced gain with venue, citation counts, and policy identity hidden; then reveal documented uptake for an assessment of realized impact and reach. This preserves scientific advance as the main outcome while making the influence of prestige and retrospective popularity visible.

### Resulting implementation priorities

The immediate additions are now concrete: **authoritative mode files, a shared claim-record template, dated follow-up assessments, an inventory of completed projects for evaluation, a contamination assessment, and an assessor-calibration exercise**. Start by completing one chain from a mode file through an executable case to an assessed scientific gain. Expand to contrasting modes and independent cases before reporting general benefits. Add the bounded comparison sample alongside that evaluation; scale the corpus only for the population questions it is designed to answer.

**Evidence scope:** this report compares the revision and convergence plan texts with current project pages. Targeted primary-source checks support the distinctions concerning scientific progress, evaluation resources, and contamination detection. It does not claim a new comprehensive reading audit, an inspection of private agent implementations or available project archives, or completed experiments. The consolidated design and measurement choices are recommendations for human review and testing.
