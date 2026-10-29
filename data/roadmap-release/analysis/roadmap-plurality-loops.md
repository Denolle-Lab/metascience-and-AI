# Roadmap: from plurality and unreported work to a human-guided agent loop

Drafted October 24, 2026, for Marine Denolle. Prose. Status: proposed, nothing adopted.

## The argument in four steps

1. **Plurality (dilemma 1).** Experts given the same task make different workflow choices and reach different results. Quantify how large that spread is in the geosciences, and how much of it is analyst choice rather than data or region.
2. **Unreported work (dilemma 2).** Papers record the route that worked. Failed, null, and unfinished work stays in theses, abstracts, review files, notebooks, or nowhere. Quantify the funnel from started to published, and how much of the workflow a paper drops.
3. **A reference model of human workflow, corrected for (1) and (2).** Observed paper walks are a censored sample. Use paired documents (thesis and paper, review file and paper, abstract and paper) to estimate what reporting removes, and correct the graph's transition rates.
4. **Agent loops measured against that model, then a hybrid loop tuned for success.** Compare agent loops with the corrected human model, build the controller from it, and run controlled trials of where the human sits, scored on novelty, advance, breadth and impact.

Steps 1 and 2 run in parallel and come first because they set the denominators for everything after. Each phase ends in a paper.

## What already exists (October 24, 2026)

| Piece | Where | State |
|:--|:--|:--|
| Vocabulary: graph v0.4.2, 13 modes, controller v0.5.1 | `unit.qmd`, `modes/`, `agents/controller/decision-tree.json` | Adopted |
| Codebook and schema | `agents/coder/CODEBOOK.md` v1.3.0, `coding.schema.json` | 15 codings validate; no human coder yet |
| Corpus, fetch, code, aggregate | `tools/corpus.py`, `select_dois.py`, `fetch_pdfs.py`, `download_wiley.py`, `download_nature.py`, `code_papers.py`, `aggregate_codings.py` | Tested on small runs; the API coder has not made a real call |
| Plurality pilot | dv/v-groundwater table, 19 studies, 14 distinct workflows; 28 pickers on one arrival | `private/talks/aiuw-2026/` |
| Unreported-work pilot | 9 papers with process documents: 126 loops, 4 visible in the published text | `private/analysis/success-set/loops/` |
| Funnel probe | NSF Geophysics 2015: 69 of 217 awards list no publication (upper bound) | `private/analysis/modes-literature/` (strand 08) |
| Agent-loop and human-workflow reviews | 31 agent systems; human process studies | `private/analysis/agent-loops/09-*.md`, `10-*.md` |

Missing before scale: a human-coded gold set, a licence decision for sending subscription full text to a model API, and task-specific extraction schemas.

## Phase 0. Measurement you can trust (November to December 2026)

- **Human gold set.** Two people (you and one student, or two students) code 40 papers independently with codebook v1.3: 10 success, 10 controls, 10 stratum C, 10 stratum D. Report Krippendorff's alpha per field (Hayes & Krippendorff, 2007): entry state, outcome, node set, mode set. Target alpha of at least 0.67 on the categorical fields before trusting model coding; 0.8 for anything used as an outcome.
- **Model against human.** Run `code_papers.py` on the same 40 twice (test–retest) and score against the human consensus. Gate from the runbook: node-set overlap of at least 0.7 and entry and outcome agreement of at least 80%.
- **Licence.** Ask UW Libraries which Wiley, Elsevier, Springer Nature and AGU terms allow sending text to a commercial model service. Until answered, code only CC BY full text through the API, and code subscription papers locally with the Claude Code subagent on your machine, or extract structured fields locally and send only those.
- **Deliverable:** codebook v1.4 with measured reliability, and a one-page methods note.

## Phase 1. Quantify plurality (January to June 2027)

Three complementary designs, because each alone confounds analyst choice with something else.

### 1a. Meta-review of many-analyst and intercomparison studies (all fields, geoscience flagged)

- **Corpus.** OpenAlex and Crossref queries: "many analysts", "crowdsourced analysis", "same data", "blind test", "model intercomparison", "benchmark exercise", "inversion validation", "interpretation uncertainty". Expect 150 to 400 candidates; screen by title and abstract.
- **Known geoscience anchors:**
  - Bond et al. (2007): 412 interpretations of one synthetic seismic section.
  - The earthquake source inversion validation project (Mai et al., 2016): finite-fault models of the same event that disagree.
  - Dynamic rupture code verification (Harris et al., 2018): codes that agree on a benchmark, a control case where plurality is small.
  - Hydrology many-modeler exercises: ten groups predicting discharge from one artificial catchment (Holländer et al., 2009), and collaborative virtual laboratories (Ceola et al., 2015).

  The findings attributed here to Mai, Harris, Holländer and Ceola come from prior knowledge; the DOIs were checked, the texts not yet read.
- **Coding per study:** task, number of teams, whether teams saw the same data, the outcome, and a dispersion measure on a common scale (share of teams disagreeing with the majority conclusion; coefficient of variation or interquartile range of the estimate relative to its stated uncertainty).
- **Output:** distribution of plurality by field and task type, and whether disagreement shrinks when the task is better specified (verification exercises against open analyses). Breznau et al. (2022), Silberzahn et al. (2018), Botvinik-Nezer et al. (2020) and Gould et al. (2025) set the non-geoscience reference.

### 1b. Same task, many published workflows (geoscience, 5 to 8 tasks)

- **Tasks** (chosen where your lab can judge the choices and where open data exist):
  1. dv/v from ambient noise (the 19-study table is the seed);
  2. ambient-noise surface-wave tomography;
  3. receiver functions;
  4. finite-fault source inversion;
  5. phase picking and catalog building;
  6. InSAR time series;
  7. rainfall–runoff calibration;
  8. glacier or ice-sheet mass balance.
- **Corpus.** 100 to 300 papers per task through `select_dois.py` (keyword plus subfield, citation-stratified). About 1,500 papers total.
- **Extraction.** A task-specific "decision vector" schema per task, extending the coding schema: for dv/v, wave type, lapse window, stack length, band, reference, stretching or wavelet method, and environmental correction. Each field has `reported: true/false`, so reporting completeness comes out of the same pass.
- **Measures:**
  - distinct workflows per task;
  - Shannon entropy of each decision;
  - share of decisions unreported;
  - where results are comparable (velocity sensitivity to groundwater, tomographic speeds in overlapping regions), how much of the variance in results the decisions explain, against region and data.

### 1c. Multiverse on fixed data (computational many-analysts)

- Take one open dataset per task (for dv/v, a station pair with groundwater wells) and run the full space of published choices from 1b with NoisePy and the matching code. This is a multiverse or specification-curve analysis (Steegen et al., 2016; Simonsohn et al., 2020).
- **Key output:** the spread of results caused by choices alone on identical data, set against the spread across published papers. If the multiverse spread is comparable, much of the published disagreement is analyst choice, not geology.
- **Agent analysts.** Run N independent agent instances on the same data and task with the same prompt. Does their spread cover the human workflow space, or collapse onto one modal workflow? This is the first direct link to dilemma 1 in agents.
- **Optional human round:** a small crowd analysis (10 to 30 seismologists; one dataset, one question) through a workshop or an SSA or AGU session.
- **Deliverable for Phase 1:** paper 1, "How much do geoscience results depend on the analyst?", combining 1a, 1b and 1c.

## Phase 2. Quantify unreported work (January to September 2027)

### 2a. The funnel: how much work reaches a paper

| Source | Denominator | Numerator | Access | Matching |
|:--|:--|:--|:--|:--|
| NSF awards (EAR, OCE, AGS, OPP), 2010–2020 | Funded projects | Awards listing publications; outcome reports that state a conclusion | NSF award API, public | Award ID in acknowledgements; PI and title |
| Theses (OpenAlex type dissertation; ProQuest; UW ResearchWorks) | Thesis chapters | Chapters later published as papers | OpenAlex public; ProQuest through UW | Author name plus title and abstract similarity, verified by hand on a sample |
| AGU Fall Meeting and EGU abstracts | Abstracts | Abstracts followed by a paper within 5 years | EGU abstracts are in Crossref; AGU through the ESS Open Archive or Confex (access unchecked) | First author plus abstract similarity |
| Preprints (ESSOAr, EarthArXiv) | Preprints | Preprints later published | Public | Crossref relations plus title match |

- **Measures:** conversion rate per source, time to publication, and what predicts non-publication: student first author, null or negative wording in the abstract, the mode of the work (methods, observation, hypothesis test), and the subfield.
- **References for the method and the non-geoscience baseline:**
  - Scherer et al. (2018): 37.3% of biomedical abstracts reach full publication.
  - Evans et al. (2018): publication outcomes of psychology dissertations.
  - Franco et al. (2014): null results are not written up.
  - Decullier et al. (2005): fate of research protocols.
  - The "dark data" framing: Heidorn (2008).
  - A geoscience call to publish failures: Andréassian et al. (2010).

### 2b. What reporting removes: paired documents

- **Pairs where the fuller record exists:**
  - thesis chapter and its paper;
  - review file or open discussion and the paper (Nature transparent peer review, EGU journals);
  - preprint versions;
  - GitHub history or notebooks and the paper (your lab's repositories first).
- **Code both members of each pair** with the same codebook (the `review` and `final_paper` sequences already exist in the schema). Target 200 pairs: 100 thesis–paper, 60 review–paper, 40 repository–paper.
- **Measures:**
  - compression: steps in the fuller record against steps in the paper;
  - reporting probability per node and per transition, P(reported | happened);
  - which kinds are dropped: failed attempts, rivals argued away, narrowed claims, protective moves.

  The 9-paper pilot predicts that loops and protective moves are dropped most.

### 2c. A prospective ground truth

- Instrument a small number of real projects, in your lab and with willing collaborators, so the whole workflow is logged as it happens: a structured research diary keyed to the graph, plus git and notebook history. Three to six projects over a year give the only sample with a true denominator.
- The same logging runs on every agent run in Phase 4, which gives the agent side a full record for free.
- Check with the UW Human Subjects Division whether this needs review; logging your own lab's work may still count as research on people.
- **Deliverable for Phase 2:** paper 2, "The geoscience file drawer: what never reaches the paper, and how much of the workflow papers drop".

## Phase 3. A corrected model of human research workflow (graph v0.6) (July to December 2027)

- **Input:** codings from the success, control and C/D strata scaled to about 1,000 papers (`corpus.py` draw, `code_papers.py`), plus the paired documents of 2b and the funnel rates of 2a.
- **Model:** treat each project as a walk on the graph that is only partly observed. A step is reported with probability r(step type, context), estimated from the pairs in 2b. Fit a hidden Markov or selection model to recover the latent transition matrix and loop rates. Weight projects by the funnel probabilities of 2a so that unfinished and failed work enters the estimate rather than being invisible.
- **Outputs:**
  - corrected transition probabilities and loop rates by stratum (success, control, failure, unfinished);
  - which routes and modes are associated with success after correction;
  - graph v0.6 edges drawn where the corrected rate passes a threshold the group sets in advance.
- **Validation:** hold out the prospective projects of 2c and check that the corrected model predicts their logged walks better than the raw paper walks do.
- **Deliverable:** paper 3, the corrected workflow model, and controller v0.6 derived from it.

## Phase 4. Agent loops against the corrected human model (October 2027 to March 2028)

- **Descriptive:** extend the 31-system comparison to measured behaviour by running five representative loops (ReAct-style, plan-and-execute, Reflexion-style, tree search, a multi-agent science system) on the same tasks with full logging. Compare against the corrected human model: modes used, loops, replication, protection, stopping, entry from an anomaly.
- **Benchmarks drawn from Phases 1 to 3:**
  1. re-derive a known result from frozen data (dv/v, picks, historical decision reconstruction);
  2. detect the planted and real flaws already found in the success papers;
  3. span the plurality: does an agent ensemble reproduce the human workflow spread of 1b and 1c, or collapse onto one?
  4. recover from a failed pass: give the agent a setup known to fail and score whether it diagnoses the failure, reframes the question (tree question 8), or overclaims.
- **Test:** controller v0.6 against a ReAct-style baseline on benchmarks 1 to 4, with the evaluator blind and holding the rubric out of the actor's context.
- **Deliverable:** paper 4, a benchmark and an evaluation of agent loops against human workflow.

## Phase 5. Optimize the hybrid loop (2028)

- **Success metrics, operationally:**

| Dimension | Measure | Usable for new work? |
|:--|:--|:--|
| Novelty | Blinded expert rating on the Novelty Dossier; embedding distance to prior work as a secondary measure | Yes |
| Advance | Blinded expert rating on the advance profile; claim survives replication or independent data | Yes, slowly |
| Breadth | Breadth v1 (citers and references outside geoscience); for new work, the fields of the imported auxiliaries | Partly |
| Impact | Citation percentile at 3 to 5 years; for new work, expert forecasts scored later | Only as a forecast |

  The macro score stays the geometric mean, reported with its uncertainty. Citations are an outcome to check, never a training target, because optimizing a proxy of success invites gaming it.
- **Design space:** where the human acts (at tree questions 1, 5, 8 and 9, at every node, or only at the end), how the mode budget is set, the number of rival hypotheses, and whether a replication pass is mandatory.
- **Trial:** randomized comparison of 3 to 4 configurations across 20 to 40 project-sized tasks: agent-only, human at the gates, human throughout. The tasks are open problems with frozen data, or reconstructions of the historical decisions behind known results. Outcomes are blinded ratings on the four dimensions, plus cost and time. Pre-register the configurations and the analysis.
- **Then tune within the best configuration** by Bayesian optimization over the continuous knobs (mode budget, rival count, stopping thresholds) against the blinded ratings. Keep a held-out task set to detect overfitting.
- **Deliverable:** paper 5, the hybrid loop and its trial.

## Scale and cost

| Phase | Papers or documents | Model coding cost (estimate) | Human time |
|:--|:--|:--|:--|
| 0 | 40 papers, coded twice by humans and twice by the model | under $20 | about 40 hours per human coder |
| 1 | about 1,500 task papers plus about 300 meta-review studies | $300–400 | screening 1a; spot checks of 5% |
| 2 | about 2,000 abstracts, theses and awards to match; 200 pairs (400 documents) to code | $100–200 | matching checks; pair spot checks |
| 3 | about 1,000 papers in strata | $150–200 | spot checks |
| 4–5 | agent runs, not papers | API cost scales with runs; budget per task | expert raters for blinded scoring |

The coding cost assumes $0.15–0.20 per paper at batch prices, from assumed token counts. The 20-paper pilot in Phase 0 replaces the estimate with measured cost.

## Decisions and risks

| Decision or risk | When | Mitigation |
|:--|:--|:--|
| Licence for model coding of subscription text | Before Phase 1 | Ask UW Libraries; fall back to local coding or extracted fields |
| Model coders agree with each other but not with humans | Phase 0 | Gold set and alpha gates; report human-only estimates where the gates fail |
| Availability bias: open papers differ from paywalled ones | Every phase | Record the fetch route; compare coverage per stratum; top up by hand |
| Matching errors in the funnel (abstract to paper) | Phase 2 | Hand-verify a stratified sample; report precision and recall |
| Region and data confound analyst choice in 1b | Phase 1 | 1c holds the data fixed |
| Selection on success makes the route look causal | Phase 3 | Controls, failures and unfinished work in the model; the prospective holdout |
| Human-subjects review for 2c and the trial | Before 2c | Ask the UW Human Subjects Division early |

## The next four weeks

1. Decide the four Phase 1b tasks and write their decision-vector schemas, starting with dv/v from the 19-study table.
2. Send the licence question to UW Libraries.
3. Pick the 40 gold-set papers and the second human coder; schedule the coding.
4. Run `select_dois.py` for dv/v and ambient-noise tomography (about 300 papers each) and freeze the manifests in the private repo.
5. Pull the NSF EAR, OCE, AGS and OPP awards for 2010 to 2020 and compute the first funnel table.

## References

- Andréassian, V., Perrin, C., Parent, E., & Bárdossy, A. (2010). The Court of Miracles of Hydrology: Can failure stories contribute to hydrological science? *Hydrological Sciences Journal, 55*(6), 849–856. https://doi.org/10.1080/02626667.2010.506050 (not read; DOI checked)
- Bond, C. E., Gibbs, A. D., Shipton, Z. K., & Jones, S. (2007). What do you think this is? "Conceptual uncertainty" in geoscience interpretation. *GSA Today, 17*(11), 4–10. https://doi.org/10.1130/GSAT01711A.1
- Botvinik-Nezer, R., et al. (2020). Variability in the analysis of a single neuroimaging dataset by many teams. *Nature, 582*, 84–88. https://doi.org/10.1038/s41586-020-2314-9
- Breznau, N., et al. (2022). Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty. *Proceedings of the National Academy of Sciences, 119*(44), e2203150119. https://doi.org/10.1073/pnas.2203150119
- Ceola, S., Arheimer, B., Baratti, E., Blöschl, G., Capell, R., et al. (2015). Virtual laboratories: New opportunities for collaborative water science. *Hydrology and Earth System Sciences, 19*, 2101–2117. https://doi.org/10.5194/hess-19-2101-2015 (not read; DOI checked)
- Decullier, E., Lhéritier, V., & Chapuis, F. (2005). Fate of biomedical research protocols and publication bias in France: Retrospective cohort study. *BMJ, 331*(7507), 19. https://doi.org/10.1136/bmj.38488.385995.8F
- Evans, S. C., Amaro, C. M., Herbert, R., Blossom, J. B., & Roberts, M. C. (2018). "Are you gonna publish that?" Peer-reviewed publication outcomes of doctoral dissertations in psychology. *PLOS ONE, 13*(2), e0192219. https://doi.org/10.1371/journal.pone.0192219 (not read; DOI checked; fifth author from prior knowledge, to verify)
- Franco, A., Malhotra, N., & Simonovits, G. (2014). Publication bias in the social sciences: Unlocking the file drawer. *Science, 345*(6203), 1502–1505. https://doi.org/10.1126/science.1255484
- Gould, E., et al. (2025). Same data, different analysts: Variation in effect sizes due to analytical decisions in ecology and evolutionary biology. *BMC Biology, 23*, 35. https://doi.org/10.1186/s12915-024-02101-x
- Harris, R. A., Barall, M., Aagaard, B., Ma, S., et al. (2018). A suite of exercises for verifying dynamic earthquake rupture codes. *Seismological Research Letters, 89*(3), 1146–1162. https://doi.org/10.1785/0220170222 (not read; DOI checked)
- Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard reliability measure for coding data. *Communication Methods and Measures, 1*(1), 77–89. https://doi.org/10.1080/19312450709336664
- Heidorn, P. B. (2008). Shedding light on the dark data in the long tail of science. *Library Trends, 57*(2), 280–299. https://doi.org/10.1353/lib.0.0036 (not read; DOI checked)
- Holländer, H. M., Blume, T., Bormann, H., Buytaert, W., Chirico, G. B., et al. (2009). Comparative predictions of discharge from an artificial catchment (Chicken Creek) using sparse data. *Hydrology and Earth System Sciences, 13*, 2069–2094. https://doi.org/10.5194/hess-13-2069-2009 (not read; DOI checked)
- Mai, P. M., Schorlemmer, D., Page, M., Ampuero, J.-P., et al. (2016). The earthquake-source inversion validation (SIV) project. *Seismological Research Letters, 87*(3), 690–708. https://doi.org/10.1785/0220150231 (not read; DOI checked)
- Scherer, R. W., Meerpohl, J. J., Pfeifer, N., Schmucker, C., Schwarzer, G., & von Elm, E. (2018). Full publication of results initially presented in abstracts. *Cochrane Database of Systematic Reviews, 2018*(11), MR000005. https://doi.org/10.1002/14651858.MR000005.pub4
- Silberzahn, R., et al. (2018). Many analysts, one data set: Making transparent how variations in analytic choices affect results. *Advances in Methods and Practices in Psychological Science, 1*(3), 337–356. https://doi.org/10.1177/2515245917747646
- Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis. *Nature Human Behaviour, 4*(11), 1208–1214. https://doi.org/10.1038/s41562-020-0912-z
- Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing transparency through a multiverse analysis. *Perspectives on Psychological Science, 11*(5), 702–712. https://doi.org/10.1177/1745691616658637
