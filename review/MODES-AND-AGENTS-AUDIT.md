# Modes-and-agents audit, September 10, 2026

> **Superseded.** A second report, `MODES-AND-AGENTS-AUDIT-v2.md`, revises this one after a critique of Astra's `SCIENCE-OF-SCIENCE-AUDIT.md`. Read that one; this file is kept for the record.

**The question asked.** Is a ten-mode taxonomy the right description of how the physical sciences work; are the assigned papers the right ones; what is missing; how do the modes become agents; and is there a research programme in studying how science is done before building agents for it. The club's stated aim is to optimize for novelty and advance, with the convenor's own hypothesis that greater advances come from interdisciplinary work.

**Basis.** Every public page, the two earlier audits, the private analyses (meeting 1 rests on full texts; meeting 11 on prior knowledge; the rest are stubs), the GAIA assessment, `references.bib`, and `curriculum.json`. Judgments about the assigned papers rest on those pages and on my prior knowledge of the papers, which should be checked against the texts. Every new reading proposed below was verified on Crossref and OpenAlex today; the verification log is in the scratchpad, not the repository. I did not read the new papers today; I cite them for what they are known for.

**A parallel audit.** An untracked file, `SCIENCE-OF-SCIENCE-AUDIT.md`, with an `audit-evidence/` folder, is dated today and was modified while this one was being written. It appears to be a second session's answer to the same question. I read it. We agree on most points; where we differ I say so. Its Crossref pass covers the 139 existing records and I did not repeat it; mine covers the new candidates.

## Short answers

1. **The ten modes are a workable first codebook, not a description of the physical sciences.** Seven rows are activities, two are contribution types, one is an orientation. The list has no row for statistical inference and empirical law, which is the mode machine learning automates and where most of statistical seismology lives. Imaging and estimation papers, the largest kind of paper in seismology, have no clear home. Question choice is coded nowhere in the public ledger. The number should be settled by the pilot's confusion matrix, not by argument.
2. **The bibliography is bibliographically sound. Three claims in the public pages misstate their sources**, one line conflates two papers by the same first author, and three pairs (meetings 7, 11, and 13) fit the club's purpose poorly.
3. **Twenty-four new readings are proposed**, all registry-verified. The most important are the taxonomic precedents the glossary does not cite, Breiman's two cultures, Chang's epistemic iteration, Strevens's iron rule, Azoulay's natural experiment on tolerance of failure, and the interdisciplinarity measurements that sharpen the breadth hypothesis.
4. **A mode enters an agent as a triple**: a recognition rule, an evidence obligation, and a transition condition. It is a property of a task, not a persona. The design notes already say this. What is missing is the objective and the experiment that would show routing by mode beats a generic planner.
5. **Yes, there is a place for studying practice before building.** The timing is better than in 1988, because the generative step is now cheap and the control policy is not. The most original thing this group can do is not the corpus study. It is to instrument its own projects so that trajectories, not narratives, become data.

## 1. Are ten modes the right description of the physical sciences?

### 1.1 The taxonomy has precedents the glossary does not cite

The idea that science has several styles, each with its own objects and its own standard of evidence, is Crombie's (1994) and Hacking's (1992). Crombie names six: postulation in the mathematical sciences, experimental exploration and measurement, hypothetical modelling, ordering by comparison and taxonomy, statistical analysis of regularities in populations, and historical derivation of genetic development. Hacking's addition is the point the glossary makes on its own: each style introduces the kind of evidence that counts within it. The glossary's "epistemic function plus the evidence it produces" is that idea, and it should say so. Gray's four paradigms (Hey et al., 2009) are the coarser version the computing world uses: empirical, theoretical, computational, data-intensive. The ten modes are a finer cut of the same space. Stokes (1997) is cited in the glossary, but as a mode; it is a two-axis attribute (aimed at understanding, aimed at use).

One term collision matters. "Mode 1" and "Mode 2" (Gibbons et al., 1994) are established science-policy terms for disciplinary versus transdisciplinary, problem-driven research. A metascience audience will hear "mode" that way. One sentence on the glossary page prevents that.

| Crombie and Hacking style | Ten-mode row | Note |
|:--|:--|:--|
| Postulation, mathematical derivation | Theory and mechanistic modeling | The glossary merges concept formation (Wilson) with derivation (Vine and Matthews) under one row; its sub-modes already separate them |
| Experimental | Hypothesis testing; exploratory discovery | Two rows for one style; Steinle's split is the finer one and is right |
| Hypothetical modelling | Simulation and prediction | Good match |
| Taxonomic, ordering by comparison | Observation and description | Good match |
| Statistical | none | Missing; see 1.3 |
| Historical, genetic | Synthesis and reconstruction | Good match |
| no style | Instruments; methods; replication; use-inspired | Two contribution types, one quality-control activity, one orientation |

### 1.2 The rows sit at different levels

The parallel audit says this and I agree. Instruments and methods are contribution roles; the glossary admits it ("they are also contribution roles") and then keeps them as modes because "each has its own epistemic function." That is true of the activity of calibrating a sensor or validating an inversion, and those activities already have a row: replication and validation. Use-inspired and co-produced research is an orientation and a way of choosing questions, not a kind of evidence. The cleaner scheme is rows for activities and attributes for everything else. Most of the attributes are already in the corpus coding scheme, so this is a reshuffle, not new work:

- intervention on the system: yes or no (Cleland)
- hypothesis stated before the result, as presented: yes, no, cannot tell
- contribution role: new data, new estimate, new method, new instrument, new concept, replication, synthesis
- aim: understanding, use, both (Stokes)
- who chose the question, and from what: an anomaly, a capability, a funding call, a user, a review
- shared infrastructure: yes or no
- data: collected, reused, none

### 1.3 What is missing for the physical sciences

**Statistical inference and empirical law.** Gutenberg-Richter, Omori, ETAS, ground-motion prediction equations, magnitude scaling relations, hazard curves, b-value maps. The decisive move is a distribution or functional form that compresses a population of observations and generalizes, with or without a mechanism. The evidence it owes is out-of-sample fit, stability across catalogs, and survival of completeness and declustering corrections. Its failure is the law fitted where it does not hold, the catalog artifact read as physics, and the scaling relation extrapolated past its range. This is Crombie's statistical style, Breiman's (2001) second culture, and the mode BACON automated (Langley, 1981, already in the bibliography). Under the current rules an ETAS forecast codes as simulation, a b-value map as observation, and a ground-motion model as methods, and the corpus study will report that seismology has no statistical mode. It has a subfield of it. Add the row, or add it as a named sub-mode of observation and description with its own recognition rule; either way, decide before the pilot.

**Imaging and estimation.** Tomography, source inversions, moment-tensor catalogs, receiver functions, and the seasonal velocity-change series of the worked project. The contribution is the estimate. Today a coder must choose between methods (if the inversion is new), observation (if the image is the point), and simulation (where parameter estimation is listed). Recommend a sub-mode under observation and description, "inferred observation," with the rule: standard method plus new estimate codes as observation; new method codes as methods; a forward model of what has not been observed codes as simulation. Bogen and Woodward (1988) supply the philosophical basis, the distinction between data and the phenomena inferred through them, and it is the distinction an agent needs in order not to mistake a processing output for a physical result.

**Question choice.** The parallel audit proposes it as the tenth mode, in place of use-inspired research. I would keep it as an attribute and a ledger column rather than a row, because a mode needs an evidence obligation of its own and question framing is what every mode begins with. But it must be coded. Today "who chose the question" appears only in the design-notes table, not in the public ledger. Promote it.

**Theory.** The recognition rule "the derivation precedes the observation" excludes theory that reorganizes known facts, which is what Wilson (1965) did. Loosen it. The sub-modes already separate conceptual synthesis from theory-led prediction; the rule should match.

### 1.4 Exhaustive and exclusive?

Neither, and a codebook does not need to be, provided four things hold. Papers get several labels and one decisive flag. There is an "uncodable" outcome. Agreement is reported per row, and the confusion matrix is treated as a finding. And the vocabulary is tested on a second physical science before it is called general. Karaca supplies high-energy physics; Knorr Cetina (1999) is the comparative anchor, since her two cultures, high-energy physics and molecular biology, are the comparison the corpus study proposes, done ethnographically. My prediction for the pilot: confusion will concentrate in three pairs, observation versus exploration, methods versus inferred observation, and simulation versus hypothesis testing. If the pilot shows that, the fix is rules, not rows.

### 1.5 Verdict on the number

Ten is fine as a start. I would go to eleven by adding statistical inference and empirical law, or stay at ten by moving use-inspired research to an attribute and adding the statistical row. Decide in meeting 1 and let the pilot revise it. The number is the least important thing about the glossary; the recognition, evidence, and failure columns are the most important, and they are better than anything in the precedents above because they are operational.

## 2. Are the proposed papers correct?

### 2.1 Bibliographic and factual checks

- **Registry.** The parallel audit found all 133 DOI records registered. I did not repeat that pass.
- **Karaca has an erratum** (Karaca, 2013b), open at the publisher, which no page mentions. I did not read it. The parallel audit says it touches the chronology of Bjorken scaling relative to the deep-inelastic-scattering experiments, which bears on meeting 2's central question. Check it before the meeting.
- **`agent-design.qmd`, line 38** cites `si2025` for arXiv:2506.20803. These are two papers. `si2025` is the ICLR ideation study, in which blinded reviewers rated the model's ideas more novel and less feasible than researchers' ideas. arXiv:2506.20803 is the execution study (Si, Hashimoto, & Yang, 2025), in which the novelty advantage shrank after the ideas were executed. Neither supports "a language model proposes hypotheses badly." Fix the citation and the claim.
- **`agent-design.qmd`, line 51** says open-system models cannot be confirmed. Oreskes, Shrader-Frechette, and Belitz (1994) say verification and validation are impossible for open systems and that confirmation is possible but always partial. The meeting 9 page has it right.
- **`sessions/06`, line 35** calls Ioannidis (2005) the strongest published case for a hypothesis gate. Under the glossary's own definition a hypothesis gate is a gate on the action. Ioannidis's argument is about prior odds, bias, and analytic flexibility, which is a gate on the claim. Reword it, or the seminar's central distinction collapses on its own page.
- **`agent-design.qmd`, line 46**, "pursue an anomaly only after it reproduces," excludes unique events: one large earthquake, one transient. Reword to "after independent corroboration or a measurement-chain check." The parallel audit says the same.
- **`README.md`, line 26** says 123 records. There are 139.

### 2.2 Fit of the pairs to the club's purpose

| Meeting | Pair | Fit | Recommendation |
|:--|:--|:--|:--|
| 1 | Platt / Cleland 2001 | Good | Keep. Add Strevens (2020) as optional: his "iron rule" is the claim gate argued at book length, with the explicit point that it constrains the argument and leaves the thinking free |
| 2 | Steinle / Karaca | Good | Keep; note the erratum. Gooding (1990) optional: Faraday's notebooks are Steinle's own evidence |
| 3 | Atwater / Nelson | Good | Keep |
| 4 | Wilson / Sykes | Good | Keep |
| 5 | Lindsey / Lindsey | Good | Keep. Chang (2004) and Bogen and Woodward (1988) optional |
| 6 | Tukey / Nosek; Ioannidis | Good | Keep; reword the Ioannidis line. Add Breiman (2001), and Moult et al. (1995) with Jumper et al. (2021) as the prospective gate that worked, beside CSEP |
| 7 | Powell / Becker | Weak for reasoning | Becker et al. (2019) is a program retrospective with little on how anyone reasoned. Replace it with Bond et al. (2007), already optional, the one measured study of geoscientists interpreting the same data. This settles the fourteenth-meeting question without a fourteenth meeting. Oreskes (2021) optional, on who chose ocean science's questions |
| 8 | Moore / Yaqub | Good | Keep. Dunbar (1997) optional; Fugelsang et al. (2004) is its follow-up |
| 9 | Oreskes / Beven and Freer; Geller | Good | Keep. Parker (2020) and Shmueli (2010) optional |
| 10 | Uzzi / Fontana | Good | Keep. Shi and Evans (2023) optional: the direct measurement of the breadth hypothesis |
| 11 | Burke / Kitcher | Weak for the hypothesis | Burke is a book, selected on success; Kitcher is about a community, not a person; the private analysis already says both. Make Jones (2009) Paper A, since it is the mechanism agents would change, keep Kitcher as the objection, move Burke to optional. Add Yegros-Yegros et al. (2015) and Bromham et al. (2016) |
| 12 | Wu / Petersen | Narrow | Keep. Add Azoulay et al. (2011) as the natural experiment on gates, and Sinatra et al. (2016) optional |
| 13 | Boiko / Chen | Off the question | Boiko et al. (2023) is a tool-use demonstration and says nothing about modes. The pair that tests the seminar's own premise is Kulkarni and Simon (1988), an agent built from a reconstructed trajectory, against Gottweis et al. (2026), an agent built as a hypothesis tournament. Make Boiko discussant-led; keep Chen for the benchmark half. Add Merchant et al. (2023) with Cheetham and Seshadri (2024) as the second loop-scores-itself pair |

### 2.3 Is the reading balanced against the convenor's thesis?

Better than before the September 6 audit, and still tilted: five of the nine practice meetings pair a paper whose job is to qualify hypothesis testing. That is acceptable as long as the ledger records rows where a gate would have helped. The strongest pro-gate evidence is not in the reading, and it is not a philosophical argument. It is CASP. Since 1994, protein-structure prediction has been scored by a blind prospective test (Moult et al., 1995), and that is where AI for science had its clearest success (Jumper et al., 2021). The lesson is specific: a gate built as infrastructure, on the claim, with a verifier, worked. Seismology has one such gate, CSEP, for forecasting, and none for imaging, source studies, or velocity change. That fact belongs in meeting 6 next to Schorlemmer et al. (2018), and it constrains the agent design in section 4.

## 3. New readings, ranked by the gap they fill

All Crossref-verified today. Open-access status is from OpenAlex; a book without a DOI is marked as such. Full references are at the end; works already in the seminar bibliography are cited by their existing key.

| Reading | What it adds | Where |
|:--|:--|:--|
| Hacking (1992); Crombie (1994) | The taxonomic precedent for plural modes, each with its own evidence | Glossary |
| Hey, Tansley, and Tolle (2009) | The four-paradigm scheme the computing world uses; free PDF | Glossary |
| Gibbons et al. (1994) | The "Mode 2" term collision; one sentence needed | Glossary |
| Breiman (2001) | Prediction versus explanation as two cultures of modelling; the statistical mode's own manifesto | Meeting 6 or 9 |
| Shmueli (2010) | The explain-or-predict distinction made operational | Meeting 9 |
| Strevens (2020) | The iron rule: gate the argument, not the thinking; the claim-gate thesis at book length | Meeting 1 |
| Chang (2004) | Epistemic iteration: measurement progressed by iterating without a fixed standard; the philosophical version of "iteration without hypothesis gates" | Meeting 5 |
| Bogen and Woodward (1988) | Data versus phenomena; the basis for the inferred-observation sub-mode | Meeting 5 |
| Knorr Cetina (1999) | Two epistemic cultures compared ethnographically; the anchor for testing the vocabulary beyond geoscience | Glossary |
| Kuhn (1977, original 1959) | The essential tension between convergent and divergent thinking; the frame Foster et al. (2015) measure | Meeting 8 |
| Dunbar (1997) | The in-vivo laboratory studies; Fugelsang et al. (2004) is the follow-up | Meeting 8 |
| Gooding (1990) | Faraday's notebooks read as a trajectory; Steinle's evidence base | Meeting 2 |
| Azoulay, Graff Zivin, and Manso (2011) | Investigators funded with tolerance for early failure produced more high-impact and more novel work than matched investigators on short renewable grants; the funding-level version of the action gate, measured | Meeting 12 |
| Shi and Evans (2023) | Surprising combinations of content and context predict impact and come disproportionately from outsiders to a field; the direct measurement of the breadth hypothesis | Meetings 10 and 11 |
| Yegros-Yegros, Rafols, and D'Este (2015) | Proximal interdisciplinarity raises citation impact; distal lowers it; an inverted U, so "more breadth" is not monotone | Meeting 11 |
| Bromham, Dinnage, and Hua (2016) | Interdisciplinary proposals are funded less; the cost side of breadth | Meeting 11 |
| Liu et al. (2021) | Hot streaks begin when exploration is followed by exploitation; a measured explore-then-test pattern across careers | Meetings 11 and 12 |
| Fortunato et al. (2018) | The review of the science of science; the index for meetings 10 to 12 | Index |
| Sinatra et al. (2016) | The random-impact rule: a scientist's biggest hit falls at a random point in the career; bears on what "optimize for advance" can mean | Meeting 12 |
| Moult et al. (1995); Jumper et al. (2021) | CASP and AlphaFold: a blind prospective gate as infrastructure, and the success it enabled | Meetings 6 and 13 |
| Merchant et al. (2023); Cheetham and Seshadri (2024) | GNoME's millions of predicted crystals and the chemists' scrutiny; a second loop-scores-itself pair beside A-Lab | Meeting 13 |
| Krenn et al. (2022) | What AI can do for scientific understanding, in Dellsén's sense: computational microscope, source of inspiration, agent of understanding | Meetings 12 and 13 |
| Reichstein et al. (2019); Mousavi and Beroza (2022) | The Earth-system and seismology reviews of machine learning; companions to Bergen et al. (2019) | Meeting 6 |
| Ratti (2015); Kitchin (2014) | Data-driven inquiry as eliminative inference and exploration; the reply to "the end of theory" | Meeting 6 |
| Oreskes (2021) | How military funding chose what ocean science asked and did not ask; "who chose the question" at the scale of a field | Meeting 7 |
| Parker (2020); Wang, Thijs, and Glänzel (2015); Devezer et al. (2019); Nersessian (2022) | Proposed by the parallel audit; I agree; verified today except Nersessian, whose DOI did not resolve and which MIT Press publishes open access | Meetings 9, 11, 13 |

Lower priority, listed so the references are complete: Anderson (1972) on emergence as a physics counterweight to reductive theory; Weitzman (1998) and Fleming (2001) on recombination as the source of novelty; Evans and Foster (2011) and Lin, Evans, and Wu (2022) on metaknowledge and where new directions come from; Larivière and Gingras (2010), an earlier inverted-U result; Cohen, McClure, and Yu (2007) on the explore-exploit trade-off as a formal frame for the routing policy; Hofstra et al. (2020) on novelty that goes unrecognized; Norton (2021) on induction licensed by local facts rather than universal schemas, the philosophical statement that there is no single method.

## 4. From modes to agents

### 4.1 A mode is a triple, not a persona

For an agent, a mode is a recognition rule (what am I doing), an evidence obligation (what must exist before I claim), and a transition condition (when do I switch). Its characteristic failure becomes a negative-control item. The design notes and the GAIA assessment already say this, and both are right not to add a fourteenth agent. The mode is carried by the orchestrator and written by the notebook.

### 4.2 State and policy

The shared state carries the question and who chose it, the observations with their measurement chain, the live rival explanations, the evidence labelled by kind, the uncertainties, and the remaining budget. Each action logs its mode, its purpose, its expected evidential consequence, and why the next action changed. The transition rules the readings give are already listed in the design notes. Three amendments follow from this audit:

- Chang's rule for the instrument and estimation modes: iterate the standard and the measurement together; the claim gate is agreement between independent chains, not a fixed prior standard.
- The anomaly rule loosened, as in section 2.1: escalate after independent corroboration or a measurement-chain check, not only after reproduction.
- A statistical-mode rule: an empirical law owes out-of-sample fit and stability under catalog corrections before it is reported as a regularity.

### 4.3 The objective

The convenor wants to optimize for novelty and advance, with breadth. None of the three can be optimized directly. Novelty without a conventional core is penalized (Uzzi et al., 2013) and rewarded late (Wang, Veugelers, & Stephan, 2017); the timing of a career's largest advance is random (Sinatra et al., 2016); breadth pays at moderate distance and costs at large distance (Yegros-Yegros et al., 2015). What can be built is a three-layer objective:

1. **Hard constraints per mode.** The evidence obligation is not traded against anything.
2. **A next-action rule.** Expected information gain over a model set (Rainforth et al., 2024), with one change that makes "no action gate" precise: the model set is expandable, and "grow the set" is a legal action. That is Cleland's exploration phase and Klahr and Dunbar's experiment-space search written into the rule. Expected information gain within a fixed set cannot recognize an explanation outside it; the parallel audit makes the same point.
3. **A portfolio constraint.** Diversity of questions and methods across the group's projects, not within one (Kitcher, 1990), with a reserved share of budget for directions that do not promise an immediate result (Azoulay et al., 2011; Liu et al., 2021).

Report novelty, warrant, and breadth as three scores. Never a scalar.

### 4.4 Breadth as an explicit operation

The group already has the instrument: the translator (`gaia-translate-QA`), with cards that say where an analogy breaks and an evaluation taxonomy of failure modes. A cross-field transfer should be logged as: source mechanism or method, target problem, the mapping of quantities and assumptions, where the mapping fails, and one cheap discriminating check. Shi and Evans (2023) give the measurable target, distant content on a conventional context, and the polymathy meeting's disconfirmer gives the measurement: a specialist's blind score against the user's own stated check.

### 4.5 The experiment

Three arms, fixed model, tools, data, and budget: a competent generic planner, a hypothesis-first planner, and a mode-routing planner. Ablate the mode labels and the transfer operation. Task families from the worked project: a measurement-chain anomaly, rival mechanisms with similar fits and one separating observable, a cross-field method transfer with a borrowed assumption to check, and cases where the honest answer is "not decidable with these data, and this is what would decide it." Score abstention as correct only where warranted, and penalize it where an answer was available. Repeat across seeds; report failures.

### 4.6 Build order

The design notes' order is reader, rival enumerator, trajectory reconstructor, abstention. I would move the trajectory reconstructor to first, because it is the instrument that produces the evidence the whole seminar says is missing (section 5). Build the verifier before the generator: the two published loop failures, A-Lab and GNoME, were verifier failures, and the successes, CASP and FunSearch, had verifiers before they had agents.

## 5. Is there a place for advancing AI and science by first studying how science is done?

Yes, and the record says why and where.

**It has been tried, and the results are instructive.** BACON found laws in tables with no hypothesis in the loop (Langley, 1981). KEKADA was built from Holmes's reconstruction of Krebs's notebooks and used surprise as a control signal (Kulkarni & Simon, 1988). Klahr and Dunbar (1988) found people searching an experiment space with no hypothesis at all. Each produced a real insight and no transferable system, because each modelled one episode and the generative step was hand-coded.

**What changed.** The generative step is now cheap. A language model will propose hypotheses, experiments, and analogies without limit. What it will not do on its own is decide which mode it is in, what evidence that mode owes, and when to stop. That control policy is what a study of practice yields, and in 1988 nobody could use it because nothing could fill in the generation. The timing is better now.

**Where it will pay first, in order of tractability:**

1. **The verifier.** The two published loop failures scored themselves with positive-only tests. Historical and observational science's answer has been in print since Chamberlin: enumerate the rivals before claiming. A rival enumerator is a design change that came from studying practice, and the A-Lab reanalysis (Leeman et al., 2024) is a ready-made test for it.
2. **Abstention as an outcome.** No benchmark in the prior-art registry scores "not decidable, and here is what would decide it." Cleland's Martian meteorite case is the canonical example. This is cheap to add to the evaluation vault.
3. **Anomaly triage with a base rate.** Dunbar's laboratories called anomalies error first and pursued them after replication. An agent can carry that rule and its exception for unique events.
4. **Question choice away from crowded directions.** Rzhetsky et al. (2015) showed that the community's actual strategy is far from efficient, and Sourati and Evans (2023) built a model that finds hypotheses people are unlikely to reach. This is the one place where the science of science already has a design result, and it bears directly on breadth.

**Where AI for science actually advanced a field.** Where a prospective or exact verifier existed first: CASP for structure, an executable check for FunSearch (Romera-Paredes et al., 2024). That is a science-of-science finding, and it says that for one seismology mode the larger contribution may be the gate itself, a prospective test for velocity-change or imaging claims that does not yet exist, rather than any agent.

**The group's most original opportunity.** The literature gives narratives; only notebooks give trajectories; the seminar's own analyses say this on every page. The group's lab-notebook agent produces dated, mode-tagged trajectories on live projects. An instrumented lab, logging every inquiry decision prospectively on real projects, would be the first dataset of its kind, and it answers the corpus study's fourth question, which the literature cannot. Start that before the corpus study. A dozen documented episodes and one three-arm comparison will say whether the taxonomy carries information; ten thousand coded abstracts will not.

**The risk that must be measured.** Hao et al. (2026), Doshi and Hauser (2024), and Messeri and Crockett (2024) all point the same way: tools that widen what one person can do narrow what a field asks. Any agent that optimizes for novelty and breadth must be evaluated at the portfolio level, and the group is the portfolio.

**The breadth hypothesis, sharpened.** "Greater advances come from interdisciplinary work" is not what the evidence supports as stated. What it supports is narrower and testable: atypical content on a conventional core, at the paper level, at moderate rather than maximal distance, in fast-moving subfields, often brought by an outsider (Uzzi et al., 2013; Yegros-Yegros et al., 2015; Teodoridis, Bikard, & Vakili, 2019; Shi & Evans, 2023). The disconfirmers are equally specific: distal-only breadth, the career-level productivity and funding penalty (Leahey, Beckman, & Stanko, 2017; Bromham et al., 2016), and collective narrowing (Hao et al., 2026). State the hypothesis in that form on the meeting 11 page and the corpus study can test it in seismology.

## 6. Mechanical corrections

- `agent-design.qmd:38`: separate `si2025` from arXiv:2506.20803 and add a record for the execution study.
- `agent-design.qmd:46`: reword the anomaly rule.
- `agent-design.qmd:51`: reword the Oreskes summary.
- `sessions/06-exploration-confirmation.qmd:35`: "the strongest published case for a claim gate."
- `sessions/02-exploratory-experiments.qmd`: add the Karaca erratum.
- `README.md:26`: 139 records.
- `glossary.qmd`: cite Crombie and Hacking, Hey et al., and the Gibbons term collision; add the statistical row or sub-mode; add the inferred-observation sub-mode; add "who chose the question" to the ledger columns in `rubrics.qmd` and `notes.qmd`.
- Two audit files now carry today's date; decide which is kept or merge them before either is committed.

None of these were applied; the request was an assessment.

## 7. What this audit did not do

It did not read the assigned papers or the new ones today. It did not run the site, the validator, or the link checker. It did not inspect the private agent prompts beyond the GAIA assessment. It did not re-verify the 139 existing records.

## References

Works already in the seminar bibliography are cited above by author and year and are listed in `bibliography.qmd`; they are not repeated here. Every work below was checked against Crossref on September 10, 2026. Open-access notes are from OpenAlex on the same day.

- Anderson, P. W. (1972). More is different: Broken symmetry and the nature of the hierarchical structure of science. *Science*, *177*(4047), 393–396. https://doi.org/10.1126/science.177.4047.393 *Paywalled.*
- Azoulay, P., Graff Zivin, J. S., & Manso, G. (2011). Incentives and creativity: Evidence from the academic life sciences. *The RAND Journal of Economics*, *42*(3), 527–554. https://doi.org/10.1111/j.1756-2171.2011.00140.x *Open copy: MIT DSpace, http://hdl.handle.net/1721.1/64640*
- Bogen, J., & Woodward, J. (1988). Saving the phenomena. *The Philosophical Review*, *97*(3), 303–352. https://doi.org/10.2307/2185445 *Paywalled at JSTOR.*
- Breiman, L. (2001). Statistical modeling: The two cultures (with comments and a rejoinder by the author). *Statistical Science*, *16*(3), 199–231. https://doi.org/10.1214/ss/1009213726 *OpenAlex lists it closed; Project Euclid usually serves Statistical Science free; check.*
- Bromham, L., Dinnage, R., & Hua, X. (2016). Interdisciplinary research has consistently lower funding success. *Nature*, *534*(7609), 684–687. https://doi.org/10.1038/nature18315 *Paywalled.*
- Chang, H. (2004). *Inventing temperature: Measurement and scientific progress*. Oxford University Press. https://doi.org/10.1093/0195171276.001.0001 *Book; not open access.*
- Cheetham, A. K., & Seshadri, R. (2024). Artificial intelligence driving materials discovery? Perspective on the article: Scaling deep learning for materials discovery. *Chemistry of Materials*, *36*(8), 3490–3495. https://doi.org/10.1021/acs.chemmater.4c00643 *Open access at the publisher.*
- Cohen, J. D., McClure, S. M., & Yu, A. J. (2007). Should I stay or should I go? How the human brain manages the trade-off between exploitation and exploration. *Philosophical Transactions of the Royal Society B*, *362*(1481), 933–942. https://doi.org/10.1098/rstb.2007.2098 *Open copy: PubMed Central 2430007.*
- Crombie, A. C. (1994). *Styles of scientific thinking in the European tradition: The history of argument and explanation especially in the mathematical and biomedical sciences and arts* (3 vols.). Duckworth. *Book; no DOI; not open access.*
- Devezer, B., Nardin, L. G., Baumgaertner, B., & Buzbas, E. O. (2019). Scientific discovery in a model-centric framework: Reproducibility, innovation, and epistemic diversity. *PLOS ONE*, *14*(5), e0216125. https://doi.org/10.1371/journal.pone.0216125 *Open access.*
- Dunbar, K. (1997). How scientists think: On-line creativity and conceptual change in science. In T. B. Ward, S. M. Smith, & J. Vaid (Eds.), *Creative thought: An investigation of conceptual structures and processes* (pp. 461–493). American Psychological Association. https://doi.org/10.1037/10227-017 *Book chapter; not open access.*
- Evans, J. A., & Foster, J. G. (2011). Metaknowledge. *Science*, *331*(6018), 721–725. https://doi.org/10.1126/science.1201765 *Paywalled.*
- Fleming, L. (2001). Recombinant uncertainty in technological search. *Management Science*, *47*(1), 117–132. https://doi.org/10.1287/mnsc.47.1.117.10671 *Paywalled.*
- Fortunato, S., Bergstrom, C. T., Börner, K., Evans, J. A., Helbing, D., Milojević, S., Petersen, A. M., Radicchi, F., Sinatra, R., Uzzi, B., Vespignani, A., Waltman, L., Wang, D., & Barabási, A.-L. (2018). Science of science. *Science*, *359*(6379), eaao0185. https://doi.org/10.1126/science.aao0185 *Open copy: eScholarship, https://escholarship.org/content/qt51s2h05k/qt51s2h05k.pdf*
- Gibbons, M., Limoges, C., Nowotny, H., Schwartzman, S., Scott, P., & Trow, M. (1994). *The new production of knowledge: The dynamics of science and research in contemporary societies*. Sage. *Book; no DOI; not open access.*
- Gooding, D. (1990). *Experiment and the making of meaning: Human agency in scientific observation and experiment*. Kluwer. https://doi.org/10.1007/978-94-009-0707-2 *Book; not open access.*
- Hacking, I. (1992). 'Style' for historians and philosophers. *Studies in History and Philosophy of Science Part A*, *23*(1), 1–20. https://doi.org/10.1016/0039-3681(92)90024-Z *Paywalled.*
- Hey, T., Tansley, S., & Tolle, K. (Eds.). (2009). *The fourth paradigm: Data-intensive scientific discovery*. Microsoft Research. *Book; no DOI; the publisher distributes the PDF free.*
- Hofstra, B., Kulkarni, V. V., Munoz-Najar Galvez, S., He, B., Jurafsky, D., & McFarland, D. A. (2020). The diversity–innovation paradox in science. *Proceedings of the National Academy of Sciences*, *117*(17), 9284–9291. https://doi.org/10.1073/pnas.1915378117 *Free to read at the publisher.*
- Jumper, J., Evans, R., Pritzel, A., Green, T., Figurnov, M., Ronneberger, O., Tunyasuvunakool, K., Bates, R., Žídek, A., Potapenko, A., Bridgland, A., Meyer, C., Kohl, S. A. A., Ballard, A. J., Cowie, A., Romera-Paredes, B., Nikolov, S., Jain, R., Adler, J., . . . Hassabis, D. (2021). Highly accurate protein structure prediction with AlphaFold. *Nature*, *596*(7873), 583–589. https://doi.org/10.1038/s41586-021-03819-2 *Open access.*
- Karaca, K. (2013b). The strong and weak senses of theory-ladenness of experimentation: Theory-driven versus exploratory experiments in the history of high-energy particle physics – Erratum. *Science in Context*, *26*(4), 665–666. https://doi.org/10.1017/S0269889713000215 *Free at the publisher.*
- Kitchin, R. (2014). Big Data, new epistemologies and paradigm shifts. *Big Data & Society*, *1*(1). https://doi.org/10.1177/2053951714528481 *Open access.*
- Knorr Cetina, K. (1999). *Epistemic cultures: How the sciences make knowledge*. Harvard University Press. https://doi.org/10.4159/9780674039681 *Book; not open access.*
- Krenn, M., Pollice, R., Guo, S. Y., Aldeghi, M., Cervera-Lierta, A., Friederich, P., dos Passos Gomes, G., Häse, F., Jinich, A., Nigam, A., Yao, Z., & Aspuru-Guzik, A. (2022). On scientific understanding with artificial intelligence. *Nature Reviews Physics*, *4*(12), 761–769. https://doi.org/10.1038/s42254-022-00518-3 *Open copy: Max Planck repository, https://pure.mpg.de/rest/items/item_3450670/component/file_3450671/content*
- Kuhn, T. S. (1977). The essential tension: Tradition and innovation in scientific research. In *The essential tension: Selected studies in scientific tradition and change* (pp. 225–239). University of Chicago Press. https://doi.org/10.7208/chicago/9780226217239.001.0001 (Original work published 1959) *Book; not open access.*
- Larivière, V., & Gingras, Y. (2010). On the relationship between interdisciplinarity and scientific impact. *Journal of the American Society for Information Science and Technology*, *61*(1), 126–131. https://doi.org/10.1002/asi.21226 *Paywalled.*
- Lin, Y., Evans, J. A., & Wu, L. (2022). New directions in science emerge from disconnection and discord. *Journal of Informetrics*, *16*(1), 101234. https://doi.org/10.1016/j.joi.2021.101234 *Paywalled.*
- Liu, L., Dehmamy, N., Chown, J., Giles, C. L., & Wang, D. (2021). Understanding the onset of hot streaks across artistic, cultural, and scientific careers. *Nature Communications*, *12*, 5392. https://doi.org/10.1038/s41467-021-25477-8 *Open access.*
- Merchant, A., Batzner, S., Schoenholz, S. S., Aykol, M., Cheon, G., & Cubuk, E. D. (2023). Scaling deep learning for materials discovery. *Nature*, *624*(7990), 80–85. https://doi.org/10.1038/s41586-023-06735-9 *Open access.*
- Moult, J., Pedersen, J. T., Judson, R., & Fidelis, K. (1995). A large-scale experiment to assess protein structure prediction methods. *Proteins: Structure, Function, and Bioinformatics*, *23*(3). https://doi.org/10.1002/prot.340230303 *Open copy: Zenodo record 1229334.*
- Mousavi, S. M., & Beroza, G. C. (2022). Deep-learning seismology. *Science*, *377*(6607), eabm4470. https://doi.org/10.1126/science.abm4470 *Paywalled.*
- Nersessian, N. J. (2022). *Interdisciplinarity in the making: Models and methods in frontier science*. MIT Press. *Book; open access at the publisher; no DOI resolved on Crossref today.*
- Norton, J. D. (2021). *The material theory of induction*. University of Calgary Press. https://doi.org/10.2307/j.ctv25wxcb5 *Book; the press publishes it in an open series; OpenAlex lists it closed; check.*
- Oreskes, N. (2021). *Science on a mission: How military funding shaped what we do and don't know about the ocean*. University of Chicago Press. https://doi.org/10.7208/chicago/9780226732411.001.0001 *Book; not open access.*
- Parker, W. S. (2020). Model evaluation: An adequacy-for-purpose view. *Philosophy of Science*, *87*(3), 457–477. https://doi.org/10.1086/708691 *Open access at the publisher.*
- Ratti, E. (2015). Big Data biology: Between eliminative inferences and exploratory experiments. *Philosophy of Science*, *82*(2), 198–218. https://doi.org/10.1086/680332 *Paywalled.*
- Reichstein, M., Camps-Valls, G., Stevens, B., Jung, M., Denzler, J., Carvalhais, N., & Prabhat. (2019). Deep learning and process understanding for data-driven Earth system science. *Nature*, *566*(7743), 195–204. https://doi.org/10.1038/s41586-019-0912-1 *Open copy: Max Planck repository, http://hdl.handle.net/21.11116/0000-0003-0B7B-8*
- Shi, F., & Evans, J. (2023). Surprising combinations of research contents and contexts are related to impact and emerge with scientific outsiders from distant disciplines. *Nature Communications*, *14*, 1641. https://doi.org/10.1038/s41467-023-36741-4 *Open access.*
- Shmueli, G. (2010). To explain or to predict? *Statistical Science*, *25*(3), 289–310. https://doi.org/10.1214/10-STS330 *Free at Project Euclid.*
- Si, C., Hashimoto, T., & Yang, D. (2025). *The ideation–execution gap: Execution outcomes of LLM-generated versus human research ideas* [Preprint]. arXiv:2506.20803. *Open preprint; not peer reviewed; the title should be checked against the arXiv record before it is entered in the bibliography.*
- Sinatra, R., Wang, D., Deville, P., Song, C., & Barabási, A.-L. (2016). Quantifying the evolution of individual scientific impact. *Science*, *354*(6312), aaf5239. https://doi.org/10.1126/science.aaf5239 *Open copy: University of Copenhagen research portal.*
- Strevens, M. (2020). *The knowledge machine: How irrationality created modern science*. Liveright. *Book; no DOI; not open access.*
- Wang, J., Thijs, B., & Glänzel, W. (2015). Interdisciplinarity and impact: Distinct effects of variety, balance, and disparity. *PLOS ONE*, *10*(5), e0127298. https://doi.org/10.1371/journal.pone.0127298 *Open access.*
- Weitzman, M. L. (1998). Recombinant growth. *The Quarterly Journal of Economics*, *113*(2), 331–360. https://doi.org/10.1162/003355398555595 *Open copy: Harvard DASH, http://nrs.harvard.edu/urn-3:HUL.InstRepos:3708468*
- Yegros-Yegros, A., Rafols, I., & D'Este, P. (2015). Does interdisciplinary research lead to higher citation impact? The different effect of proximal and distal interdisciplinarity. *PLOS ONE*, *10*(8), e0135095. https://doi.org/10.1371/journal.pone.0135095 *Open access.*
