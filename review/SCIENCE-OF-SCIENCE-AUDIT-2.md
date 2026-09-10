# Second audit: critique of Fable and revised recommendations

September 10, 2026. This report follows [my first audit](SCIENCE-OF-SCIENCE-AUDIT.md) and evaluates [Fable's report](MODES-AND-AGENTS-AUDIT.md). It revises my assessment; it does not change the curriculum or either earlier report.

**My revised assessment**

Fable strengthens the analysis by identifying the weak treatment of statistical inference and imaging, supplying historical precedents for scientific pluralism, and bringing funding institutions into the account of discovery. I accept those improvements. Its strongest practical proposal is to collect prospective records of research decisions alongside the reading club.

Its main weakness is that it repeatedly turns suggestive evidence into general rules: career-level topic concentration becomes hypothesis testing; a funding comparison becomes an experiment on gates; examples of successful evaluation become a necessary condition for scientific progress; and a proposed laboratory record becomes a first-of-its-kind dataset. Those steps are not established by the cited evidence.

My own first report also needs revision. I was too willing to preserve ten headings, did not give estimation a sufficiently clear home, and underweighted the institutions and material arrangements that make inquiry possible. The stronger project is to study **how scientific activities, representations, resources, and collective organization interact to produce warranted advances**, then test selected implications for agents. It should remain an informal reading club with an optional empirical project.

**Scope and independence of this comparison**

I read both reports and checked consequential new claims against primary papers, author-hosted sources, and publisher records. The checks below include Breiman/Shmueli, Chang, Shi–Evans, Yegros-Yegros and colleagues, Liu and colleagues, Azoulay and colleagues, Sinatra and colleagues, GNoME and its critique, AlphaFold, and Dunbar's study of laboratory practice. Some checks use abstracts or relevant sections rather than full texts. Hacking's publication identity and the later accessible discussion of styles were checked; I did not read all of Crombie's volumes, Strevens's book, or Fable's entire proposed library.

Fable explicitly read my report while preparing its own. Our agreement is therefore not independent corroboration. Its registry-verification log is described as outside the repository; I cannot audit that log here. I retain my first report's completed metadata check without repeating it. Neither report establishes the performance of the private GAIA implementation, and this comparison does not inspect that implementation.

**What Fable improves, and what I change**

| Issue | Fable's useful contribution | Revision to my first report |
|:--|:--|:--|
| Statistical science | Empirical regularities and statistical models are poorly distinguished in the ten rows. | Make statistical model construction and assessment explicit. Distinguish a distributional claim, a prediction, an estimate, and a causal explanation. |
| Imaging and estimation | A standard inversion producing a new image is not primarily a methods contribution. | Separate inferential estimation from forward simulation. Require uncertainty, resolution, identifiability, and sensitivity to assumptions. |
| Historical precedents | Crombie and Hacking belong in the genealogy of the taxonomy. | Add a short comparison of precedents before proposing a codebook. The operational usefulness of our vocabulary still requires testing. |
| Institutions | Funding horizons and constraints shape what research can be pursued. | Include question allocation, resources, collaboration, incentives, and infrastructure among explanatory variables. |
| Process evidence | Prospective observation is more informative about decisions than abstracts. | Start a small prospective record alongside retrospective reconstruction, without claiming that either is a complete trace of cognition. |
| Question framing | Paper classification and question selection need not occupy the same axis. | Withdraw my preference for making question framing the tenth paper mode. Keep it an explicit agent activity and a process-coding category. |

**Where Fable needs correction**

**1. Statistical inference is a real omission, but Breiman does not put it all in his second culture.** Fable groups empirical laws, ETAS, hazard curves, and b-value maps under Breiman's algorithmic culture. Breiman distinguishes assumed stochastic data models from algorithmic models; a statistical point-process model is not algorithmic modeling simply because it predicts. Shmueli's distinction between explanatory and predictive objectives is related but different. Add both readings as competing analytical lenses, not interchangeable taxonomies. [Breiman, original article](https://file.biolab.si/files/ml1/2001-breiman-two-cultures.pdf); [Shmueli, author preprint](https://arxiv.org/abs/1101.0891).

Fable is right that imaging lacks a clear home, but its proposed label “inferred observation” should preserve the distinction between measurement and model-dependent estimate. Standard software does not make the estimate directly observed. Its claim that imaging and estimation are the largest class of seismology papers is an unmeasured prevalence claim, not an audit finding.

**2. The historical taxonomies are precedents, not a validation of this particular list.** Scientific styles, epistemic cultures, and Gray's computational paradigms answer different questions and operate at different scales. They can inform a vocabulary of inquiry actions without being nested versions of one classification. Nor does conceptual similarity establish that this project's glossary was derived from Hacking. Cite the relationship as an intellectual precedent. Fable's assertion that our operational columns are better than anything in the precedents is unsupported: ease of coding does not establish historical or philosophical adequacy. [Hacking, publication record](https://www.sciencedirect.com/science/article/abs/pii/003936819290024Z); [Gray's fourth-paradigm framing](https://www.microsoft.com/en-us/research/wp-content/uploads/2009/10/Fourth_Paradigm.pdf).

**3. The breadth evidence does not establish one universal recipe.** Fable combines different studies into a prescription involving moderate distance, conventional foundations, fast-moving fields, and outsiders. Those conditions were not tested jointly in a common population with a common outcome. They concern reference diversity, citation surprise, specialization, researcher background, and recognition—related but distinct constructs.

Yegros-Yegros and colleagues do report nonlinear relationships between reference diversity and citations in four fields. Their evidence supports taking distance and measurement choices seriously, not a general ban on distant combinations. Wang and colleagues report different long-term patterns, which makes the comparison especially useful. [Yegros-Yegros et al.](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0135095); [Wang et al.](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0127298).

Shi and Evans are a valuable addition, but Fable's phrase “distant content on a conventional context” is too narrow. The paper analyzes surprising combinations of both contents and contexts and reports particularly consequential context surprises. It offers evidence relevant to the breadth hypothesis, not a causal test that interdisciplinary work produces greater epistemic advances. [Shi and Evans](https://www.nature.com/articles/s41467-023-36741-4).

**4. Career exploitation is not experimental confirmation.** Fable calls Liu and colleagues a measured explore-then-test pattern. The study operationalizes exploration and exploitation through the diversity and concentration of creative outputs; for scientists, these are publication topics. It does not code exploratory experiments followed by discriminating tests. The association with hot streaks is interesting, but the timescale and construct differ from next-action routing. Use it to motivate a candidate portfolio policy, then test that policy. [Liu et al., measures and results](https://www.nature.com/articles/s41467-021-25477-8).

**5. Azoulay is not a clean natural experiment on hypothesis gates.** The authors use weighting/matching and difference-in-differences to compare HHMI and NIH-funded investigators. Their own account explicitly notes the absence of a plausible source of exogenous variation in HHMI appointment. The funding programs differ along several dimensions, including flexibility, feedback, and horizons. This is informative observational evidence about funding arrangements, with identifying assumptions; it neither isolates tolerance of failure nor manipulates an agent's action gate. Keep the paper and label the inference correctly. [Authors' paper](https://web.mit.edu/manso/www/hhmi.pdf); [authors' methodological account](https://www.nber.org/reporter/2012number3/production-scientific-ideas).

**6. CASP demonstrates credible evaluation, not the causal sufficiency of gates.** AlphaFold's CASP14 performance is a strong example of independent blind assessment on undisclosed structures. It does not isolate the contribution of CASP from data, architecture, compute, and accumulated domain knowledge. CASP also supplies empirical reference structures rather than an exact verifier for every scientific claim about a protein. FunSearch's executable checks address a different kind of task. Keep these examples, but replace “where AI actually advanced a field” with “two cases in which external evaluation made particular advances demonstrable.” [Jumper et al.](https://www.nature.com/articles/s41586-021-03819-2).

Fable's claim that seismology lacks comparable evaluation infrastructure for entire other areas also needs a scoped search. We can propose a missing evaluation capability for a specific task without asserting that no relevant community benchmark or validation practice exists.

**7. GNoME should not be treated as a second established self-scoring failure.** The original work combines learned predictions with DFT calculations, comparison to competing phases, and experimental structure matching. It reports 736 experimental matches, including 184 discoveries since the project's start. Those numbers do not validate every candidate or make all candidates experimentally novel. Cheetham and Seshadri challenge the novelty, credibility, and utility of the proposed compounds. That is a useful scientific disagreement, but not evidence that GNoME is simply the same verification failure as A-Lab. Distinguish computational stability, experimental realization, novelty, and utility. [Merchant et al.](https://www.nature.com/articles/s41586-023-06735-9); [Cheetham and Seshadri](https://escholarship.org/uc/item/9qx9t3kz).

My first report also made the A-Lab verifier lesson sound more settled than necessary. It is better to attribute the reanalysis's conclusions and inspect the particular claims than adopt a criticism as a complete verdict on an entire system.

**8. Random position in a publication sequence is not uncontrollable scientific advance.** Sinatra and colleagues study citation impact and the position of influential publications within an author's sequence of papers. This is not uniform randomness over calendar time and does not show that investment or strategy cannot change expected outcomes. Fable uses the result too strongly to argue that advance cannot be optimized. We should instead distinguish uncertain, delayed outcomes from the measurable decision objectives available now. [Sinatra et al., author-hosted paper](https://www.barabasi.com/media/pub_imports/files/825.pdf).

**9. A prospective laboratory record would be useful; its claimed priority is unsupported.** Fable says only notebooks give trajectories and calls the proposed dataset the first of its kind. Dunbar's research already recorded scientists working and interacting through audio, video, and interviews. Nersessian's ethnographic work also studies research as it proceeds. Neither source establishes that our exact proposed dataset already exists, but both make an unqualified priority claim untenable. A narrower contribution might be synchronized human–agent action records linked to independently coded epistemic decisions and outcomes. That still requires a prior-art search. [Dunbar's research methods](https://education.umd.edu/research-college/labs/laboratory-thinking-reasoning-creativity-educational-neuroscience/research); [Nersessian's study](https://mitpress.mit.edu/9780262544665/interdisciplinarity-in-the-making/).

Notebook entries are selective records too. A generated account of why an action happened is not automatically a faithful account of its cause. Preserve raw artifacts, contemporaneous statements, and retrospective interpretation separately. Fable's statement that the group's notebook already produces mode-tagged live trajectories is not demonstrated by the report; it should be checked against actual logs.

**10. The history of discovery systems and the claim that generation is solved are overstated.** Fable attributes the limitations of several different historical systems to each modeling one episode. That conflicts even with this project's BACON description, which lists multiple rediscovered laws, and treats Klahr–Dunbar's human experiments as though they were another implemented system. Restricted representations and domains are defensible limitations; a single common failure cause is not established.

Modern models make candidate text inexpensive, but good experiments, representations, concepts, and tractable questions remain difficult to generate. “The control policy is what a study of practice yields” also jumps from description to prescription: the recorded policy may reflect convention, unavailable resources, or bias. This is precisely why a comparative experiment is needed.

**11. The proposed agent rules are still design hypotheses.** A universal hard evidence obligation can become an action gate if it prevents generating a conjecture before corroboration exists. An empirical regularity can first be reported provisionally; independent evidence changes the strength of the claim. Chang's epistemic iteration concerns progressive revision of measurement systems, not simply agreement between two chains. Independent-looking chains can share assumptions and errors. [Chang, chapter on measurement and iteration](https://academic.oup.com/book/5530/chapter-abstract/148476793).

Expected information gain is useful when the model space and observation process are sufficiently specified. Merely allowing the action “expand the model set” does not supply a probability model or a comparable value for discovering a new representation. Likewise, “never a scalar” is too absolute. Report the scientific outcomes separately; a decision rule may still use explicit costs, thresholds, or utilities, with sensitivity analysis. My earlier preference for separate outcomes should be read this way too.

**12. Verification and reading load need tighter presentation.** Fable responsibly discloses that it did not read the papers that day, but its conclusions often sound like full-text assessments. Its summary says 24 new readings while the reference section contains 45 entries, including books and a preprint; the selection tiers should be explicit. “All Crossref-verified” should be narrowed to the records actually checked there, with publisher checks for the others. These are reporting problems, not evidence that the references are fabricated. The confirmed Oreskes, Si, Ioannidis-framing, Karaca, anomaly-rule, and README issues from the first audit remain valid and should be addressed first.

**A revised answer on the modes**

There is no reason that the reading club's themes, the corpus codebook, and the agent controller must share one flat taxonomy. That was the main unresolved problem in both reports.

Use three linked descriptions:

| Description | What it records | Why it is needed |
|:--|:--|:--|
| Epistemic work | Characterize a phenomenon; estimate an unobserved quantity; establish a regularity; construct a concept/model; discriminate explanations; forecast; reconstruct/integrate; assess robustness. | Makes the evidence owed by a claim explicit. These are provisional families, not a fixed exhaustive count. |
| Inquiry actions | Inspect, explore, calibrate, build an apparatus or method, change representation, frame/reframe a question, derive, simulate, seek evidence, transfer a method, challenge, defer. | Gives an agent things to do and lets a process study record changes in direction. |
| Context and contribution | New data/method/instrument/estimate/concept; applied aims; co-production; infrastructure; disciplinary resources; who set the problem; constraints. | Prevents contribution type and research organization from being mistaken for an inference rule. |

A tomography episode might estimate a structure using an established inversion, with calibration and sensitivity analysis as actions, and a new regional estimate as its contribution. A later episode might use that structure to discriminate tectonic explanations. Both labels are informative; neither requires inventing a single decisive mode for the whole paper.

Question framing belongs explicitly in process coding and agent action selection. It need not be an exclusive paper category. Its quality can be assessed through clarity, tractability, relevance to an uncertainty, and consequences of possible answers; its eventual importance remains uncertain. My first proposal to make it the tenth paper mode was premature. Fable's proposal to record only who chose the question is insufficient because origin and reframing are different variables.

For teaching, the existing ten headings can remain familiar entry points while their status is clarified. For the pilot, make statistical modeling and inferential estimation explicit labels; separate use orientation and co-production. Compare this representation with a simpler codebook. Judge it by coverage, agreement, explanatory usefulness, and whether it changes worthwhile next actions. A confusion matrix alone can select an easy-to-code but scientifically unhelpful vocabulary.

**A revised answer on the breadth hypothesis**

Keep the original ambition open. The evidence justifies asking when integrating distant knowledge produces advances, but does not justify replacing the hypothesis with a supposedly settled moderate-distance recipe. Distinguish three hypotheses:

1. **Project hypothesis:** verified transfer of a method, mechanism, or representation improves a project's knowledge or capability gain relative to an appropriate comparison.
2. **Capability hypothesis:** assistance expands what an individual or team can competently do, including recognizing when specialist input is required.
3. **Portfolio hypothesis:** assistance expands the range of substantively different worthwhile questions pursued, rather than repeatedly directing projects toward the same accessible methods and data.

Assess breadth and depth separately. Measure practical integration, not only reference variety. Examine distant transfers that fail, nearby transfers that succeed, and specialized projects that produce major advances. Use comparable time windows for citation uptake and avoid interpreting low recognition as absence of knowledge gain. Reduced productivity or funding success can coexist with valuable advances; these are costs or selection mechanisms, not automatic disconfirmers of the epistemic hypothesis.

Hao, Doshi–Hauser, and Messeri–Crockett provide different kinds of motivation for monitoring collective narrowing: a scientific-publication study, a writing experiment, and a conceptual analysis. They should not be pooled as three direct demonstrations that scientific agents narrow inquiry. The qualification in my first report stands.

**A revised reading-club plan**

The goal should be a better conversation and a few sharper experiments, not a much longer compulsory library.

| Part of the club | Recommendation after comparing both audits |
|:--|:--|
| Opening framing | Add a facilitator's short comparison with Crombie/Hacking. Keep Platt–Cleland. Strevens can supply a contrasting argument about public evidence, presented as a philosophical position. |
| Measurement, meeting 5 | Keep the DAS pair; use a short Chang case or Bogen–Woodward excerpt as the companion discussion. Include one new estimate produced with an established method. |
| Statistical practice, meetings 6 or 9 | Promote Breiman or Shmueli into the conversation. Prefer Shmueli when the aim is to distinguish prediction from explanation; Breiman when comparing modeling practices. Replace an optional assignment rather than adding another required paper. |
| Field practice, meeting 7 | Keep the field/infrastructure purpose. Bond is useful for interpretation, but substituting it automatically for Becker changes the question. Add a field decision record or choose the replacement only if that shift is intended. |
| Breadth, meeting 11 | Use one Nersessian case plus one empirical paper, such as Shi–Evans or Leahey. Jones–Kitcher is a reasonable alternative for the narrower question of specialization and division of labor, not the strongest direct pairing on successful integration. |
| Advance, meeting 12 | Keep the Wu–Petersen measurement debate available. Azoulay is an excellent alternative companion when the question is what conditions enable advances; retain Dellsén's distinction between progress and attention. |
| Agent design, meeting 13 | Keep one implemented system and one evaluation paper as anchors. Bring KEKADA and Sourati–Evans in a brief comparison prepared beforehand. Boiko–Chen addresses implementation and evaluation; calling it off-topic is too strong. KEKADA–Co-Scientist cannot itself isolate the effect of mode routing because the systems differ in domain, era, tools, and tasks. |

The strongest additions from Fable for immediate use are **Shmueli/Breiman, Chang, Azoulay, and Shi–Evans**, plus a short historical-taxonomy framing. I retain **Nersessian** as my first addition for understanding interdisciplinary integration. CASP–AlphaFold is a useful positive evaluation case; the materials controversy is useful when attribution and disagreement remain explicit. The larger reading pool should stay optional.

**A revised research and agent plan**

Build a small shared record before implementing a comprehensive controller. Record actions and their actual inputs/outputs, the question in force at that moment, measurement and modeling assumptions, constraints, alternatives considered, and the basis for each next decision. Preserve uncertainty about unrecorded steps. Apply independent human coding to a sample; do not make the agent's own mode labels the ground truth.

Study some existing records while observing a few ongoing projects. Retrospective cases supply breadth and completed outcomes; prospective observation supplies chronology and failed branches. Starting both on a small scale is more useful than declaring one categorically superior. The corpus study can later examine published contribution patterns, which is a different useful question.

Then implement a few selectable procedures: inferential estimation with assumption checks, anomaly follow-up, competing-explanation assessment, question reframing, and cross-field transfer. Give each a purpose, permissible actions, an output format, and criteria for advancing the claim. Allow conjectures, provisional results, and inconclusive outcomes. Develop the evaluator and the procedures together so that existing scores do not silently restrict what counts as science.

Compare a competent generic planner, a hypothesis-testing planner, and an inquiry-routing planner on matched tasks. Keep model, tools, evidence access, budgets, and human intervention comparable. Do not handicap the hypothesis-testing baseline by forbidding ordinary inspection or calibration; distinguish that useful baseline from an intentionally strict action-gate ablation. Give the generic planner the same substantive checks in unstructured form where possible, so that the experiment tests routing rather than simply extra instructions.

For the seismic-velocity example, include a credible physical change, a processing artifact, confounded rival mechanisms, and a case where useful information can be borrowed from hydrology only after checking assumptions. Include answerable and insufficient-evidence cases. Independent observations and controlled perturbations can test particular decisions; synthetic perturbations establish performance on those constructed cases, not universal real-world discovery skill.

Report warranted gain, predictive or inferential performance where relevant, novelty relative to prior work, quality of next observations, transfer validity, and cost. Evaluate question diversity across runs/projects as well as within a report. A small local pilot can reveal failures and feasibility; diverse held-out cases and prospective outcomes are needed before claiming general benefits.

The defensible research contribution is **evidence about which inquiry procedures and transitions improve which scientific tasks, under which constraints**, together with a validated process record and evaluation method. Merely attaching mode names to an agent, collecting logs, or showing that it narrates the scientific method more fluently would not establish that contribution.

**What should happen next**

First, make the already-confirmed citation and wording corrections. Second, clarify the distinction between themes, epistemic work, and agent actions; add statistical inference and estimation to the pilot. Third, choose a small number of readings that expose mechanisms of advance and integration. Finally, collect a few research episodes and test one specific routing or transfer change. Preserve the club's freedom to discover that its initial categories, preferred policies, or breadth hypothesis need revision.

This second report adds no curriculum changes and makes no new claim of a comprehensive bibliography check. Its linked sources document the targeted checks behind the revisions; uncertain priority and implementation claims remain explicitly unresolved.
