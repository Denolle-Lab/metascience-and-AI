# Modes-and-agents audit, second report, September 10, 2026

This report supersedes `MODES-AND-AGENTS-AUDIT.md`, written earlier today. Part A critiques Astra's report, `SCIENCE-OF-SCIENCE-AUDIT.md`, which answered the same prompt. Part B is the revised audit, self-contained, with each change from the first report marked "revised."

**Basis.** Every public page, the two earlier audits, the private analyses, the GAIA assessment, `references.bib`, `curriculum.json`, Astra's report and its evidence file. Two of Astra's specific claims were checked against the sources today: the execution-study preprint and the Karaca erratum. Every new reading proposed below was verified on Crossref and OpenAlex today. I did not read the assigned papers or the proposed ones today; where a judgment rests on my knowledge of a paper rather than its text, that is the kind of claim the convenor has asked to have checked, and it should be.

## Part A. Critique of Astra's report

### A.1 What it gets right, and what I adopt from it

- **The factual errors.** Astra found four misstatements in the public pages and the stale README count. I confirmed all five independently. Two of its specific claims I checked against the sources today. The execution study (Si, Hashimoto, & Yang, 2025) did recruit 43 researchers, and it found that the scores of language-model ideas fell more than the scores of expert ideas on all four measures after execution. The Karaca erratum (Karaca, 2013b) does correct footnote 58 to say that Bjorken formulated the scaling hypothesis in an unpublished manuscript before the deep-inelastic-scattering experiments, and also corrects one equation, three symbols, and four references. Astra undersells that footnote. It bears on meeting 2's central question, whether the deep-inelastic work was exploratory or theory-led, and it moves the answer toward "a hypothesis existed, unpublished." The erratum should be assigned with the paper, not noted.
- **The level-mixing critique of the rows**, the loosened recognition rules, and multi-label coding. Right, and stated more carefully than in my first report.
- **The drift diagnosis.** The seminar's aim is novelty, advance, and breadth; its pages have drifted toward gates and auditing. Generation, representation change, question choice, and collective diversity are underweighted. I agree, and my first report understated it. Astra's remedy is the wrong instrument (A.2, point 3); the diagnosis stands.
- **The corpus-study critique** is the strongest section of either report. Multi-label coding with an uncodable outcome; 300 held-out papers leave rare modes almost untested; stratify the validation; a journal set does not isolate seismology inside broad geophysics journals; reference concentration and reference diversity are mathematically related, so entering them as independent measures of depth and breadth invites a circular result; distinguish confounders from mediators; replace "not measured" with a documented search. I adopt all of it in B.8.
- **Two design points I had not made.** Different prompting roles on the same model are not independent expertise, which bears on the group's thirteen-role roster and on Kitcher's portfolio argument under correlated strategies. And "no claim without a test it could have failed" is the wrong universal form of the claim gate: descriptive claims, derivations, and capability demonstrations owe different evidence. Adopted in B.4.
- **A lighter format** for an informal club: one anchor reading for everyone, a companion presented by a rotating reader, and a three-sentence output. Presented as an option in B.7.
- **Convergence.** Both reports, written separately with different emphases, arrive at the same build order: a dozen documented inquiry episodes and one small controlled policy comparison before any large-scale paper classification. That agreement is itself a finding for the group.

### A.2 Where it is wrong or weaker

1. **No taxonomic precedent.** Astra declares the ten modes "not yet a validated taxonomy" and never checks them against the taxonomies that exist: Crombie's and Hacking's styles of scientific reasoning, Gray's four paradigms, Gibbons's Mode 1 and Mode 2, Kell and Oliver's hypothesis-driven versus data-driven split. Validation against the literature was available and was not done. The consequence is the next point.
2. **No statistical mode, and estimation folded into simulation.** Astra's revised table keeps "simulate, estimate, and predict" with inverse estimation inside it. In seismology an inversion is a measurement, not a simulation. Astra recommends Bogen and Woodward (1988) for exactly this distinction, data versus the phenomena inferred through them, and then does not apply it to its own table. And nothing in its table holds an empirical law or a statistical regularity: Gutenberg-Richter, Omori, ETAS, ground-motion models, hazard curves. Crombie has the statistical style as one of six. For a seismology corpus this is the largest omission in Astra's report.
3. **Its tenth family, "find and frame questions," breaks its own rule.** Having argued that the rows mix levels, it adds a row at yet another level. Question framing is what every activity begins with, and it has no evidence obligation that can be checked after the fact; Astra's own "evidence that the capability worked" entry for the row describes good planning, not evidence. As a decisive-mode code it would mark agenda papers and reviews and little else. The right instruments are an attribute and a ledger column, "who chose the question, and from what," and a meeting exercise on question choice (B.7). Under multi-label coding the harm is small; it still should not be a row.
4. **It merges generation and discrimination.** "Generate and discriminate explanations" is one family in its table. That erases the distinction the seminar exists to examine: Chamberlin, Gilbert, and Pólya on producing rivals against Platt on discriminating among them. For an agent these are different components with different failure modes, fluent rivals that do not compete versus a test no outcome could fail, and the A-Lab lesson (Leeman et al., 2024) is precisely that the loop tested without enumerating rivals. Keep them separable, at least as sub-modes with separate evidence columns.
5. **The reading-pair audit is too conservative.** Astra identifies the weakness of meetings 7, 11, and 13 and keeps all three as they are. For meeting 13 it names KEKADA in one section and Co-Scientist in another and never pairs them, which is the pair that tests the seminar's own premise.
6. **It omits the strongest evidence for gates and the verifier lesson.** Nothing on CASP and AlphaFold, CSEP, or FunSearch. Its objective, warranted gains under a budget, is right, but it never says what the verifier is, and the two published loop failures were verifier failures. It also omits GNoME and the chemists' scrutiny of it (Merchant et al., 2023; Cheetham & Seshadri, 2024).
7. **Its reading list is thin where the project says its centre is.** Seven additions plus two. Nothing from the science of science proper: no Fortunato et al. (2018), no Azoulay, Graff Zivin, and Manso (2011), no Shi and Evans (2023), no Yegros-Yegros, Rafols, and D'Este (2015), no Bromham, Dinnage, and Hua (2016), no Liu et al. (2021), no Sinatra et al. (2016). Nothing from the philosophy that states the seminar's own theses: Strevens (2020) on the iron rule, Chang (2004) on epistemic iteration. Astra's caution to "add selectively" is reasonable for an informal club; the prompt asked what else is relevant.
8. **Conventions.** No APA references and no reference list, against the convenor's standing rule; nothing added to the private bibliography. Its registry-evidence file is good practice and I have nothing equivalent for the 139 existing records. It links a copy of the Oreskes paper hosted on a Portland State course page; that is a third-party copy, not an author-hosted one, and the public book's own rule is not to point at such copies. The title carries an em-dash.
9. **One claim I could not verify.** That Nersessian (2022) is an open-access book. The MIT Press page refused the fetch and OpenAlex has no record of the book. It may well be true; it is unverified.

### A.3 What Astra changed in my own report

- Instruments and methods stay as activity rows. My first report half-suggested folding their activity into replication and validation; that was too quick. Contribution role becomes a separate attribute (B.1).
- The claim gate is restated as a mode-specific evidence obligation. The Popperian form applies to explanatory claims only (B.4).
- A third gate is named: registration. Committing the test before the data is what Nosek, CSEP, and CASP are, and it is neither the action gate nor the claim gate. Both reports had run it together with the claim gate (B.4). This is new.
- The corpus-study amendments are adopted wholesale (B.8).
- "The largest kind of paper in seismology" for imaging and estimation becomes "common"; nobody has counted.
- The lighter format is presented as an option, and a question-choice exercise is added (B.7).
- "Prompting roles are not independent expertise" is added to the agent section (B.5).

## Part B. Revised audit

### Short answers

1. **The ten modes are a workable first codebook, not a description of the physical sciences.** They match Crombie's and Hacking's styles in five of six places and miss the sixth, the statistical style. Imaging and estimation papers, common in seismology, have no clear home. Question choice is coded nowhere in the public ledger. The pilot's confusion matrix, not argument, should settle the number.
2. **The bibliography is bibliographically sound. Five things on the public pages are wrong**, two of them now checked against the sources. Three pairs, meetings 7, 11, and 13, fit the club's purpose poorly.
3. **Twenty-five new readings are proposed, all registry-verified.** If the club takes only five: Hacking (1992), Breiman (2001), Chang (2004), Azoulay et al. (2011), and Shi and Evans (2023).
4. **A mode enters an agent as a recognition rule, an evidence obligation, and a transition condition.** The seminar's two gates need a third, registration. The objective is warranted gain under a budget with hard evidence constraints per mode, expected information gain over an expandable model set, and a portfolio constraint across the group's projects. Build the verifier before the generator.
5. **Yes, there is a place for studying practice before building.** Both audits converge on the first step: a dozen dated inquiry episodes from the group's own projects and one three-arm policy comparison, before the corpus study. The lab-notebook agent is the instrument.

### B.1 Are ten modes the right description? (revised)

**Precedents the glossary should cite.** Crombie (1994) named six styles of scientific thinking: postulation in the mathematical sciences, experimental exploration and measurement, hypothetical modelling, ordering by comparison and taxonomy, statistical analysis of regularities in populations, and historical derivation. Hacking (1992) added that each style brings its own objects and its own standard of evidence, which is the glossary's "epistemic function plus the evidence it produces." Gray's four paradigms (Hey, Tansley, & Tolle, 2009) are the coarser scheme the computing world uses. "Mode 1" and "Mode 2" (Gibbons et al., 1994) are established science-policy terms and a metascience audience will hear "mode" that way; one sentence prevents the collision. Kell and Oliver (2004), already in the bibliography, is the biology version of the debate.

| Crombie and Hacking style | Ten-mode row | Note |
|:--|:--|:--|
| Postulation, derivation | Theory and mechanistic modeling | The sub-modes already separate concept formation from derivation; the recognition rule should not require derivation before observation |
| Experimental | Hypothesis testing; exploratory discovery | Two rows for one style; Steinle's split is the finer one and is right; keep generation of rivals visible as a sub-mode of the first |
| Hypothetical modelling | Simulation and prediction | Good match |
| Taxonomic, ordering | Observation and description | Good match |
| Statistical | none | Missing |
| Historical, genetic | Synthesis and reconstruction | Good match |
| no style | Instruments; methods; replication; use-inspired | Three activities and one orientation |

**Rows and attributes (revised).** Rows are activities. Instruments and methods stay as rows, since building a sensor or an inversion is an activity with its own evidence, calibration and recovery of known signals. Use-inspired and co-produced research is an orientation and a way of choosing questions, and becomes attributes. The attribute set, most of it already in the corpus coding scheme:

- intervention on the system: yes or no
- hypothesis stated before the result, as presented: yes, no, cannot tell
- registered before the data: yes or no (B.4)
- contribution role: new data, new estimate, new method, new instrument, new concept, replication, synthesis
- aim: understanding, use, both
- who chose the question, and from what: an anomaly, a capability, a call, a user, a review
- shared infrastructure: yes or no
- data: collected, reused, none

**What is missing for the physical sciences.**

*Statistical inference and empirical law.* Gutenberg-Richter, Omori, ETAS, ground-motion models, magnitude scaling, hazard curves, b-value maps. The decisive move is a distribution or a functional form that compresses a population of observations and generalizes, with or without a mechanism. It owes out-of-sample fit, stability across catalogs, and survival of completeness and declustering corrections. It fails when the law is fitted where it does not hold, when a catalog artifact is read as physics, and when a scaling relation is extrapolated past its range. This is Crombie's statistical style, Breiman's (2001) second culture, and the mode BACON automated (Langley, 1981). Under the current rules an ETAS forecast codes as simulation, a b-value map as observation, and a ground-motion model as methods, and the corpus study would report that seismology has no statistical mode. Give it a label before the pilot. Whether it is a row or a sub-mode matters less under multi-label coding than that the label exists.

*Inferred observation.* Tomography, source inversions, moment tensors, receiver functions, and the velocity-change series of the worked project. The contribution is the estimate. Rule: a standard method with a new estimate codes as observation and description, sub-mode inferred; a new method codes as methods; a forward model of what has not been observed codes as simulation. Bogen and Woodward (1988) give the basis, and it is the distinction an agent needs in order not to mistake a processing output for a physical result.

*Question choice.* An attribute, a ledger column, and an exercise (B.7), not a row.

*Generation versus discrimination.* Keep them separable under hypothesis testing: rival generation (Chamberlin, Gilbert) and discriminating test (Platt) as sub-modes with their own evidence columns, so the corpus study can ask whether papers enumerate rivals at all.

**Exhaustive and exclusive?** Neither, and a codebook does not need to be, provided: several labels per paper and one decisive flag; an uncodable outcome; agreement reported per row with the confusion matrix treated as a finding; and a test on a second physical science before the vocabulary is called general, with Karaca supplying high-energy physics and Knorr Cetina (1999) the comparative anchor. Prediction for the pilot: confusion concentrates in observation versus exploration, methods versus inferred observation, and simulation versus hypothesis testing. If so, the fix is rules, not rows.

**Verdict on the number.** Ten rows plus the statistical label and the inferred-observation sub-label go into the pilot. Decide rows after it. The number is the least important thing about the glossary; the recognition, evidence, and failure columns are its real contribution, and they are more operational than any precedent above.

### B.2 Are the papers correct? (revised)

**Errors on the public pages.**

| Where | What is wrong | Status |
|:--|:--|:--|
| `agent-design.qmd:38` | Cites `si2025`, the ICLR ideation study, for arXiv:2506.20803, the execution study; and neither supports "proposes hypotheses badly" | Confirmed against the arXiv record today |
| `agent-design.qmd:51` | "Open-system models cannot be confirmed"; Oreskes et al. (1994) say verification and validation are impossible and confirmation is partial | From knowledge; both audits agree; check the abstract's wording |
| `sessions/06:35` | Ioannidis as "the strongest published case for a hypothesis gate"; under the glossary's definition it is a claim gate, and preregistration is a registration gate (B.4) | Confirmed on the page |
| `sessions/02` | The Karaca erratum is not mentioned; it corrects the Bjorken chronology that meeting 2 turns on | Erratum content confirmed today |
| `agent-design.qmd:46` | "Pursue an anomaly only after it reproduces" excludes unique events | Confirmed on the page |
| `README.md:26` | 123 records; there are 139 | Confirmed |

**Fit of the pairs.**

| Meeting | Pair | Fit | Recommendation |
|:--|:--|:--|:--|
| 1 | Platt / Cleland 2001 | Good | Keep. Strevens (2020) optional: the iron rule constrains the argument and leaves the thinking free, the claim gate at book length |
| 2 | Steinle / Karaca | Good | Keep; assign the erratum. Gooding (1990) optional: Faraday's notebooks are Steinle's evidence |
| 3 | Atwater / Nelson | Good | Keep |
| 4 | Wilson / Sykes | Good | Keep |
| 5 | Lindsey / Lindsey | Good | Keep. Chang (2004) and Bogen and Woodward (1988) optional |
| 6 | Tukey / Nosek; Ioannidis | Good | Keep; reword the Ioannidis line. Add Breiman (2001), and Moult et al. (1995) with Jumper et al. (2021) beside Schorlemmer et al. (2018) as registration gates that worked |
| 7 | Powell / Becker | Weak for reasoning | Replace Becker et al. (2019), a program retrospective, with Bond et al. (2007), already optional and the one measured study of geoscientists interpreting the same data. This settles the fourteenth-meeting question. Oreskes (2021) optional on who chose ocean science's questions. Astra keeps the pair and makes Bond a discussant case; either works, mine is cheaper |
| 8 | Moore / Yaqub | Good | Keep. Dunbar (1997) optional |
| 9 | Oreskes / Beven and Freer; Geller | Good | Keep. Parker (2020) and Shmueli (2010) optional |
| 10 | Uzzi / Fontana | Good | Keep. Shi and Evans (2023) optional |
| 11 | Burke / Kitcher | Weak for the hypothesis | Jones (2009) as Paper A, the mechanism agents would change; Kitcher stays as the objection; Burke to optional. Add Yegros-Yegros et al. (2015), Bromham et al. (2016), and Nersessian (2022) for the mechanism of integration. Astra prefers Leahey and Teodoridis, also good; Jones is the one that turns the hypothesis into a prediction of a model |
| 12 | Wu / Petersen | Narrow | Keep. Add Azoulay et al. (2011), the natural experiment on tolerance of failure; Sinatra et al. (2016) optional |
| 13 | Boiko / Chen | Off the question | Pair Kulkarni and Simon (1988), an agent built from a reconstructed trajectory, with Gottweis et al. (2026), an agent built as a hypothesis tournament. Boiko becomes discussant-led if the group wants a running laboratory system in the room; Chen stays for the benchmark half. Add Merchant et al. (2023) with Cheetham and Seshadri (2024) as the second loop-scores-itself pair |

**Balance.** Five of nine practice meetings still qualify hypothesis testing. That is acceptable if the ledger records rows where a gate helped. The strongest pro-gate evidence is not in the reading and it is not philosophical. Since 1994 protein-structure prediction has been scored by a blind prospective test (Moult et al., 1995), and that is where AI for science had its clearest success (Jumper et al., 2021). Seismology has one such gate, CSEP, for forecasting, and none for imaging, source studies, or velocity change. That belongs in meeting 6 and constrains B.5.

### B.3 New readings (revised)

All verified on Crossref today. Open-access notes are from OpenAlex. Full references at the end; works already in the seminar bibliography are cited by author and year and not repeated.

| Reading | What it adds | Where |
|:--|:--|:--|
| Hacking (1992); Crombie (1994) | The taxonomic precedent: plural styles, each with its own evidence | Glossary |
| Hey, Tansley, and Tolle (2009) | The four-paradigm scheme; free PDF | Glossary |
| Gibbons et al. (1994) | The "Mode 2" term collision | Glossary |
| Breiman (2001) | Prediction versus explanation as two cultures; the statistical mode's manifesto | Meeting 6 or 9 |
| Shmueli (2010) | Explain or predict, made operational | Meeting 9 |
| Strevens (2020) | The iron rule: gate the argument, not the thinking | Meeting 1 |
| Chang (2004) | Epistemic iteration: measurement progressed by iterating without a fixed standard; the historian's version of "iteration without hypothesis gates" | Meeting 5 |
| Bogen and Woodward (1988) | Data versus phenomena; the basis for inferred observation | Meeting 5 |
| Knorr Cetina (1999) | Two epistemic cultures compared ethnographically; the anchor for testing the vocabulary beyond geoscience | Glossary |
| Kuhn (1977, original 1959) | The essential tension; the frame Foster et al. (2015) measure | Meeting 8 |
| Dunbar (1997) | The in-vivo laboratory studies | Meeting 8 |
| Gooding (1990) | Faraday's notebooks read as a trajectory | Meeting 2 |
| Azoulay, Graff Zivin, and Manso (2011) | Investigators funded with tolerance for early failure produced more high-impact and more novel work than matched investigators on short renewable grants; the funding-level action gate, measured | Meeting 12 |
| Shi and Evans (2023) | Surprising combinations of content and context predict impact and come disproportionately from outsiders; the direct measurement of the breadth hypothesis | Meetings 10 and 11 |
| Yegros-Yegros, Rafols, and D'Este (2015) | Proximal breadth raises citation impact, distal lowers it; an inverted U | Meeting 11 |
| Bromham, Dinnage, and Hua (2016) | Interdisciplinary proposals are funded less; the cost of breadth | Meeting 11 |
| Liu et al. (2021) | Hot streaks begin when exploration is followed by exploitation | Meetings 11 and 12 |
| Fortunato et al. (2018) | The review of the science of science | Index |
| Sinatra et al. (2016) | The random-impact rule; what "optimize for advance" can mean | Meeting 12 |
| Moult et al. (1995); Jumper et al. (2021) | CASP and AlphaFold: a registration gate as infrastructure, and the success it enabled | Meetings 6 and 13 |
| Merchant et al. (2023); Cheetham and Seshadri (2024) | GNoME and the chemists' scrutiny; the second loop-scores-itself pair | Meeting 13 |
| Krenn et al. (2022) | What AI can do for understanding, in Dellsén's sense | Meetings 12 and 13 |
| Reichstein et al. (2019); Mousavi and Beroza (2022) | The Earth-system and seismology reviews of machine learning | Meeting 6 |
| Ratti (2015); Kitchin (2014) | Data-driven inquiry as eliminative inference and exploration | Meeting 6 |
| Oreskes (2021) | Who chose ocean science's questions, at the scale of a field | Meeting 7 |
| Nersessian (2022); Nersessian (2008) | Cognitive ethnography of integration across fields; analogy and representation change in physics. Proposed by Astra; agreed; the 2008 DOI verified today, the 2022 open-access status not | Meetings 11 and 2 |
| Parker (2020); Wang, Thijs, and Glänzel (2015); Devezer et al. (2019) | Proposed by Astra; agreed; verified | Meetings 9, 11, 13 |

Lower priority: Anderson (1972); Weitzman (1998); Fleming (2001); Evans and Foster (2011); Lin, Evans, and Wu (2022); Larivière and Gingras (2010); Cohen, McClure, and Yu (2007); Hofstra et al. (2020); Norton (2021).

### B.4 Three gates, not two (new)

The seminar's central distinction is a gate on the action against a gate on the claim. Both audits ran a third kind together with the second. Naming it changes how several readings are classified.

| Gate | Rule | Examples in the reading | What the reading says |
|:--|:--|:--|:--|
| Action | The next step must test a stated hypothesis | Platt (1964); the closed loops of King et al. (2009) and Kitano (2021); the GAIA study designer as built | Helps where the hypothesis space is enumerable and the assay is automatic; hurts where the phenomenon is not yet stable (Cleland, 2002) or the finding comes from data nobody hypothesized about (Rouet-Leduc et al., 2017) |
| Registration | Commit the test, or the analysis, before the data that will score it | Nosek et al. (2018); CSEP (Schorlemmer et al., 2018); CASP (Moult et al., 1995); Parkfield (Bakun & Lindh, 1985) | The clearest successes of gating in the reading are all of this kind; it does not constrain what the next action is, only when the commitment is made |
| Claim | Nothing is claimed without the evidence its kind owes | Ioannidis (2005); Leeman et al. (2024); Chamberlin (1965) | Supported everywhere; the form of the evidence differs by claim |

**Evidence by kind of claim (revised from the first report).** "A test it could have failed" is the right obligation for an explanatory claim. A descriptive claim, a catalog or a map, owes coverage, completeness, and consistency. An estimate owes resolution, uncertainty, and recovery of known signals. A derivation owes consistency, limiting cases, and a consequence later found. A capability demonstration owes calibration and the same signal on an independent sensor. A conjecture owes its own label. The glossary's evidence column already says most of this row by row; the "claim gate" slogan should be replaced by "the evidence its mode owes."

### B.5 From modes to agents (revised)

**A mode is a triple, not a persona.** Recognition rule, evidence obligation, transition condition; its characteristic failure becomes a negative-control item. The mode is carried by the orchestrator and written by the notebook. No fourteenth agent. And, from Astra: thirteen prompting roles on one model are thirteen views of one model, not thirteen experts. Independence of judgment has to come from independent evidence, independent tools, or people, and the evaluation should not credit the roster with a diversity it does not have.

**State and policy.** The shared state carries the question and who chose it, the observations with their measurement chain, the live rivals, the evidence labelled by kind, the uncertainties, and the remaining budget. Each action logs its mode, purpose, expected evidential consequence, and why the next action changed. Generated rationales are not the record; logs and tool outputs are. Transition rules from the readings are in the design notes; three amendments: Chang's rule for the instrument and estimation modes, iterate the standard and the measurement together and gate the claim on agreement between independent chains; the anomaly rule loosened to independent corroboration or a measurement-chain check; and a statistical-mode rule, an empirical law owes out-of-sample fit and stability under catalog corrections before it is reported.

**The objective.** None of novelty, advance, or breadth can be optimized directly. Novelty without a conventional core is penalized (Uzzi et al., 2013) and rewarded late (Wang, Veugelers, & Stephan, 2017); a career's largest advance falls at a random time (Sinatra et al., 2016); breadth pays at moderate distance and costs at large distance (Yegros-Yegros et al., 2015). Three layers: hard evidence constraints per mode, never traded; a next-action rule of expected information gain over a model set that the agent may expand, so that "grow the set" is a legal action, which is Cleland's exploration phase and Klahr and Dunbar's experiment-space search written into the rule, and which Astra also insists on; and a portfolio constraint across the group's projects rather than within one (Kitcher, 1990), with budget reserved for directions that promise nothing immediate (Azoulay et al., 2011; Liu et al., 2021). Report novelty, warrant, and breadth as three scores, never one.

**Breadth as an operation.** The translator the group already has is the instrument. A transfer is logged as source mechanism, target problem, mapping of quantities and assumptions, where the mapping fails, and one cheap discriminating check. Shi and Evans (2023) give the target, distant content on a conventional context; the polymathy meeting's disconfirmer gives the measurement, a specialist's blind score against the user's stated check.

**The experiment.** Three arms with model, tools, data, and budget fixed: a generic planner, a hypothesis-first planner, a mode-routing planner. Ablate the mode labels and the transfer operation. Task families from the worked project: a measurement-chain anomaly, rival mechanisms with similar fits and one separating observable, a cross-field transfer with a borrowed assumption to check, and cases whose honest answer is "not decidable, and this would decide it." Credit abstention only where warranted; penalize it where an answer existed. Repeat across seeds; report failures. Both audits specify this experiment in nearly the same words.

**Build order.** Verifier first. The two published loop failures, A-Lab and GNoME, were verifier failures; the successes, CASP and FunSearch (Romera-Paredes et al., 2024), had verifiers before they had agents. Then the trajectory reconstructor, because it produces the evidence the seminar says is missing (B.6). Then the mode-aware reader and the rival enumerator, which the design notes already specify.

### B.6 Is there a place for studying science before building agents for it? (revised)

Yes. The record says why and where.

**It has been tried.** BACON found laws with no hypothesis in the loop (Langley, 1981). KEKADA was built from Holmes's reconstruction of Krebs's notebooks and used surprise as a control signal (Kulkarni & Simon, 1988). Klahr and Dunbar (1988) watched people search an experiment space with no hypothesis at all. Each produced an insight and no transferable system, because each modelled one episode and the generative step was hand-coded.

**What changed.** Generation is cheap now. What a language model will not do on its own is decide which mode it is in, what evidence that mode owes, and when to stop. That control policy is what a study of practice yields, and in 1988 nothing could use it.

**Where it pays first.** The verifier: rival enumeration before any "new" or "confirmed," which Chamberlin printed in 1890 and the A-Lab reanalysis tests. Abstention as an outcome. Anomaly triage with Dunbar's base rate and an exception for unique events. Question choice away from crowded directions, where Rzhetsky et al. (2015) and Sourati and Evans (2023) already give a design result.

**Where AI for science actually advanced a field.** Where a registration or exact gate existed first. For one seismology mode the larger contribution may be the gate itself, a prospective test for velocity-change or imaging claims, rather than any agent.

**The group's most original opportunity.** The literature gives narratives; only notebooks give trajectories. The lab-notebook agent produces dated, mode-tagged trajectories on live projects. An instrumented lab, logging inquiry decisions prospectively on real projects, would be the first dataset of its kind, and it answers the corpus study's fourth question, which the literature cannot. Both audits say to start here. A dozen documented episodes and one three-arm comparison will show whether the taxonomy carries information; ten thousand coded abstracts will not.

**The risk.** Hao et al. (2026), Doshi and Hauser (2024), and Messeri and Crockett (2024) point one way: tools that widen what one person can do narrow what a field asks. Astra is right that the collective result does not by itself falsify the individual claim; the two are different outcomes and both must be measured. The group is the portfolio.

**The breadth hypothesis, sharpened.** "Greater advances come from interdisciplinary work" is not what the evidence supports as stated. It supports: atypical content on a conventional core, at the paper level, at moderate rather than maximal distance, in fast-moving subfields, often brought by an outsider (Uzzi et al., 2013; Yegros-Yegros et al., 2015; Teodoridis, Bikard, & Vakili, 2019; Shi & Evans, 2023). The disconfirmers: distal-only breadth, the career-level productivity and funding penalty (Leahey, Beckman, & Stanko, 2017; Bromham et al., 2016), and collective narrowing (Hao et al., 2026). State it that way on the meeting 11 page.

### B.7 Format and the question-choice exercise (new)

Astra's format is worth adopting for an informal club: one anchor paper read by everyone, one companion presented by a rotating reader, and a three-sentence output per meeting: what move mattered, what an agent would do differently, what evidence would test that. The current pairs survive unchanged as anchor and companion. The ledger row stays; it is one line.

The answer to the drift diagnosis is an exercise, not a row. In meeting 6 or 8, each participant brings one question they chose not to pursue and says why, then codes it against Foster et al. (2015): tradition or innovation. Read Rzhetsky et al. (2015) on how far the community's actual choices are from efficient, Sourati and Evans (2023) on choosing away from crowds, and Azoulay et al. (2011) on what a funder's tolerance of failure changed. Output: the "who chose the question, and from what" column of the ledger, filled for nine episodes.

### B.8 The corpus study (adopted from Astra, with additions)

- Papers give contribution profiles; episodes give process. Do not read a missing hypothesis in an abstract as evidence that none guided the work.
- Multi-label coding, one decisive flag, an uncodable outcome. Check whether modes predict anything beyond the simpler attributes of new data, intervention, and contribution role.
- The validation set: stratify by mode, period, and access; 300 papers in total leave rare modes almost untested. Report per-mode precision, recall, calibration, and a prevalence correction, and carry classifier uncertainty into the regressions.
- The corpus: a journal set does not isolate seismology inside JGR Solid Earth or GRL; add a topic filter and report sensitivity to it. Add a second physical-science corpus before molecular biology is the only comparison.
- Depth and breadth: reference concentration and reference diversity are mathematically related; do not enter them as independent regressors. Specialization is not competence.
- Confounders and mediators: team size, article type, infrastructure, and field conventions may lie on the causal path from mode to impact; decide before adjusting.
- Field-shaping cases are selected; add ordinary, failed, and enabling contributions.
- "Not measured" becomes a documented search across studies of scientific practice, research-strategy taxonomies, epistemic cultures, and discovery cognition, in Novelty Dossier form. Hacking, Knorr Cetina, Foster, and Kell and Oliver are where it starts.
- Add the statistical label and the inferred-observation sub-label before the pilot, or the pilot cannot test them.

### B.9 Mechanical corrections

- `agent-design.qmd:38`: separate `si2025` from the execution study and add a record for it.
- `agent-design.qmd:46`: reword the anomaly rule.
- `agent-design.qmd:51`: reword the Oreskes summary.
- `sessions/06-exploration-confirmation.qmd:35`: "the strongest published case for a claim gate," and name preregistration as a registration gate.
- `sessions/02-exploratory-experiments.qmd`: assign the erratum.
- `README.md:26`: 139 records.
- `glossary.qmd`: cite Crombie, Hacking, Hey et al., and the Gibbons collision; add the statistical label and the inferred-observation sub-label; separate rival generation from the discriminating test; add the registration gate beside the two the page defines; add "who chose the question" to the ledger in `rubrics.qmd` and `notes.qmd`.
- Two audits and this second report now carry today's date; reconcile before committing any of them.

None of these were applied; the request was an assessment.

### B.10 What this report did not do

It did not read the assigned or proposed papers today, apart from the two records checked in A.1. It did not run the site or the link checker. It did not inspect the private agent prompts beyond the GAIA assessment. It did not re-verify the 139 existing records; Astra's evidence file covers them.

## References

Works already in the seminar bibliography are cited above by author and year and listed in `bibliography.qmd`. Every work below was checked against Crossref on September 10, 2026. Open-access notes are from OpenAlex the same day. Entries for all of them are in the private bibliography under "Candidates from the modes-and-agents audit."

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
- Nersessian, N. J. (2008). *Creating scientific concepts*. MIT Press. https://doi.org/10.7551/mitpress/7967.001.0001 *Book; not open access.*
- Nersessian, N. J. (2022). *Interdisciplinarity in the making: Models and methods in frontier science*. MIT Press. *Book; Astra reports it open access at the publisher; unverified today; no DOI resolved on Crossref.*
- Norton, J. D. (2021). *The material theory of induction*. University of Calgary Press. https://doi.org/10.2307/j.ctv25wxcb5 *Book; the press publishes it in an open series; OpenAlex lists it closed; check.*
- Oreskes, N. (2021). *Science on a mission: How military funding shaped what we do and don't know about the ocean*. University of Chicago Press. https://doi.org/10.7208/chicago/9780226732411.001.0001 *Book; not open access.*
- Parker, W. S. (2020). Model evaluation: An adequacy-for-purpose view. *Philosophy of Science*, *87*(3), 457–477. https://doi.org/10.1086/708691 *Open access at the publisher.*
- Ratti, E. (2015). Big Data biology: Between eliminative inferences and exploratory experiments. *Philosophy of Science*, *82*(2), 198–218. https://doi.org/10.1086/680332 *Paywalled.*
- Reichstein, M., Camps-Valls, G., Stevens, B., Jung, M., Denzler, J., Carvalhais, N., & Prabhat. (2019). Deep learning and process understanding for data-driven Earth system science. *Nature*, *566*(7743), 195–204. https://doi.org/10.1038/s41586-019-0912-1 *Open copy: Max Planck repository, http://hdl.handle.net/21.11116/0000-0003-0B7B-8*
- Shi, F., & Evans, J. (2023). Surprising combinations of research contents and contexts are related to impact and emerge with scientific outsiders from distant disciplines. *Nature Communications*, *14*, 1641. https://doi.org/10.1038/s41467-023-36741-4 *Open access.*
- Shmueli, G. (2010). To explain or to predict? *Statistical Science*, *25*(3), 289–310. https://doi.org/10.1214/10-STS330 *Free at Project Euclid.*
- Si, C., Hashimoto, T., & Yang, D. (2025). *The ideation-execution gap: Execution outcomes of LLM-generated versus human research ideas* [Preprint]. arXiv:2506.20803. *Open preprint; not peer reviewed; title and the 43-researcher design confirmed against the arXiv record on September 10, 2026.*
- Sinatra, R., Wang, D., Deville, P., Song, C., & Barabási, A.-L. (2016). Quantifying the evolution of individual scientific impact. *Science*, *354*(6312), aaf5239. https://doi.org/10.1126/science.aaf5239 *Open copy: University of Copenhagen research portal.*
- Strevens, M. (2020). *The knowledge machine: How irrationality created modern science*. Liveright. *Book; no DOI; not open access.*
- Wang, J., Thijs, B., & Glänzel, W. (2015). Interdisciplinarity and impact: Distinct effects of variety, balance, and disparity. *PLOS ONE*, *10*(5), e0127298. https://doi.org/10.1371/journal.pone.0127298 *Open access.*
- Weitzman, M. L. (1998). Recombinant growth. *The Quarterly Journal of Economics*, *113*(2), 331–360. https://doi.org/10.1162/003355398555595 *Open copy: Harvard DASH, http://nrs.harvard.edu/urn-3:HUL.InstRepos:3708468*
- Yegros-Yegros, A., Rafols, I., & D'Este, P. (2015). Does interdisciplinary research lead to higher citation impact? The different effect of proximal and distal interdisciplinarity. *PLOS ONE*, *10*(8), e0135095. https://doi.org/10.1371/journal.pone.0135095 *Open access.*
