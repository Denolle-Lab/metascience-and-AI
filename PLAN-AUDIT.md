# Plan audit, September 6, 2026

An audit of the v0.3 curriculum against the convenor's stated aims: reconstruct how inquiry has actually proceeded, record where each mode of inquiry succeeded and where it failed, and then build agents from that record rather than from the hypothesis-testing loop that dominates current AI-for-science work. The audit covers the structure of the thirteen meetings, the thirty-nine references that were in the book, and the private analysis. It ends with the fifty-seven peer-reviewed references added as optional extensions and the reasoning for each group.

Dates are fixed and were not touched. Required pairs were not changed. Where a change to a required pair or to the order of meetings is recommended, it is stated as a recommendation and left for the group.

## Decisions taken, September 6, 2026

The convenor adopted five of the eight recommendations the same day, and they are now in the sources:

1. The inquiry-mode ledger is defined on the rubrics page and kept live on the meeting-notes page; every practice meeting's closing prompt now asks for the episode's row.
2. Ioannidis (2005) is discussant-led in meeting 6 and Geller (1997) in meeting 9.
3. Meetings 11 and 12 are swapped: polymathy on November 17, scientific advance on November 24.
4. Cleland 2001 (Geology) is Paper B of meeting 1, read by everyone; Cleland 2002 is discussant-led.
5. The meeting-1 private analysis was rewritten from the full texts of all three papers, with page references, and the corrections to the earlier memory-based version are marked in it.

On September 8, 2026 the convenor removed all meeting dates: the seminar proceeds one meeting at a time in the numbered order, and the validator checks order only. The calendar remarks in the summary and in section 7 are therefore historical.

Still open: naming a maintainer for a living architecture document, settling the agent-seisbench question before November 3, and retiring the one preprint.

Meeting numbers in sections 1 to 8 below follow the v0.3 order in which the audit was written. After the swap, polymathy is meeting 11 and scientific advance is meeting 12.

## Summary

The plan is well built for a reading group: two papers per meeting with a stated relationship, a case exercise, a named output, and a validation script that keeps the bibliography and the schedule honest. Four things need attention before the quarter starts.

1. The seminar states a disconfirming observation for the polymathy hypothesis in meeting 12 but not for its main thesis, that hypothesis testing is one mode among several and a poor gate for iteration. The reading tilts toward that thesis, and the strongest published cases for a gate were absent. Section 1 says what was added and proposes a ledger that turns "an objective view" into a table the group fills in week by week.
2. The account of prior art started in 2023. Four decades of computational discovery were missing, including one system built exactly the way this seminar proposes to build. Section 4.
3. Meeting 13 is asked to produce an architecture and a benchmark in one hour, with four papers. Section 5 proposes accumulating that artifact across the quarter so meeting 13 reviews rather than invents.
4. Meeting 12, the convenor's own hypothesis, falls on the Tuesday of Thanksgiving week. Section 7.

The bibliography is sound. All thirty-nine DOIs resolve and every field I checked against the Crossref registry agrees. Section 6 lists the small notes.

## 1. Does the seminar test its thesis or assume it?

The purpose statement says the adequacy of a hypothesis loop is a question, not a conclusion. The reading list did not quite keep that promise. Five of the nine practice meetings pair a paper whose role is to limit or qualify hypothesis testing: Cleland in meeting 1, Steinle and Karaca in 2, Tukey in 6, Moore and Yaqub in 8, Oreskes and Beven in 9. Only meeting 4 is a clean positive case for a discriminating test. Platt is the only voice for the loop, and Platt is a manifesto with no evidence beyond selected successes, as the private analysis of meeting 1 already says.

Nothing in the required set makes the strongest published case for a gate, which is the statistical one. When analyses are flexible and prior odds are low, exploration reported as confirmation produces mostly false findings. That is Ioannidis (2005), and it is now in meeting 6. Nothing gave the group's own field's version of the same lesson: decades of exploratory precursor claims in earthquake prediction that failed every prospective test (Geller 1997), the Parkfield experiment, which was a public hypothesis-first prediction that failed on timing and succeeded as an instrument (Bakun and Lindh 1985; Bakun and colleagues 2005), and the community's eventual answer, which was a preregistration infrastructure, CSEP (Schorlemmer and colleagues 2018). These are now in meetings 6 and 9. And nothing gave the best-argued case for a closed loop from the machine side: the Robot Scientist, whose first discovery came from exactly the generate-and-test cycle the convenor distrusts (King and colleagues 2009), now in meeting 13.

Recommendation: promote Ioannidis and Geller to discussant-led status in meeting 6 or 9, as meeting 13 does for Messeri and Crockett. The thesis should meet its best opponent in the room.

Three further additions make the convenor's alternative specifiable rather than intuitive. Klahr and Dunbar (1988) watched people solve a discovery task and found two strategies: searching a space of hypotheses, and searching a space of experiments with no hypothesis, and both worked. Lehman and Stanley (2011) showed in a machine setting that searching for novelty rather than for an objective solves problems that objective search cannot, because the objective is deceptive. Rainforth and colleagues (2024) give the loop its strongest formal form, expected information gain, which needs a space of models rather than a single hypothesis. Schmidhuber (2010) defines interestingness as compression progress. Between them the group has a vocabulary in which "iterate without hypothesis gates" is an architecture with a stated objective and a known failure mode, not a preference.

### The ledger

The stated aim is to see where each mode of inquiry has succeeded and failed. The plan collects nine cases but never tallies them. I recommend one table, kept across meetings 1 to 9, one row per reconstructed episode:

| Episode | Decisive move | Mode | Known at the start | When a hypothesis appeared | A hypothesis gate would have: helped / hurt / not applied | Evidence basis |
|:--|:--|:--|:--|:--|:--|:--|

The last two columns are the point. Filled honestly, the table is the evidence base for meeting 13, and it forces the group to record cases where a gate would have helped. A ledger with no such rows would itself be a finding, about the selection of cases rather than about science. The evidence-basis column keeps the distinction the index already insists on: notebook, archive, primary paper, or retrospective recollection.

If the group wants it, this belongs in `rubrics.qmd` beside the trajectory worksheet. I did not add it, because it changes what participants are asked to do each week.

## 2. Coverage of the modes of inquiry

| Mode (glossary row) | Meeting | Success case in the reading | Failure case in the reading | Added |
|:--|:--|:--|:--|:--|
| Observation and description | 3, 7 | Atwater; Powell; Becker | Powell, in part | Kuklick and Kohler 1996 |
| Exploratory discovery | 2, 6, 8 | Steinle's cases; Tukey; Moore | Yaqub's caution | Franklin 2005; Ioannidis 2005, the failure; Bergen 2019; Leonelli 2014; Rzhetsky 2015; Kuhn 1962; Fugelsang 2004, the base rate; Copeland 2019; Rouet-Leduc 2017 |
| Hypothesis testing | 1, 4, 9 | Sykes | Cleland's limits | Chamberlin 1965; Cleland 2001; Parkfield; Geller 1997; Schorlemmer 2018 |
| Theory and mechanistic modeling | 4 | Wilson | none | Vine and Matthews 1963, a second test; Oreskes 1988, the same community rejecting drift for forty years |
| Simulation and prediction | 9 | Beven and Freer | Oreskes 1994 | Tarantola 2006; Kirchner 2006; Rainforth 2024 |
| Instruments and observing systems | 5 | DAS | Lindsey 2020, the calibration | Kuhn 1961; Tal 2013 |
| Methods and computation | 5, 6, 13 | Coscientist | none | Shapiro 2004 and 2005; Langley 1981; Kulkarni and Simon 1988; King 2009; Schmidt and Lipson 2009; Kapoor 2023; A-Lab and its reanalysis, a loop that failed |
| Synthesis and reconstruction | 3, 10 | Atwater | Nelson's ambiguity | Satake 1996 and Yamaguchi 1997: independent traces converging; Swanson 1986 |
| Replication and validation | 5, 6, 13 | Lindsey 2020 | none | Nosek 2018 (assigned); Kapoor 2023; Schorlemmer 2018 |
| Use-inspired and co-produced research | none | none | none | Stokes 1997; Cash 2003; Jordan 2011, added with the glossary |

The rows are the ten modes of the [glossary](glossary.qmd), the convenor's nine with instruments and methods split on September 6; the audit was first written against a twelve-mode list derived from the readings, which now survives only as the glossary's sub-modes.

Before the additions, six of the nine practice meetings had a success case and no failure case for their mode. That is the selection problem the plan warns about in Burke and Moore, reproduced in the syllabus. Each of those meetings now has at least one failure or scrutiny case.

One mode has no meeting: use-inspired and co-produced research. Two sub-modes have no case of their own: theory-led prediction, for which Vine and Matthews is the closest and is now in meeting 4, and literature-based discovery, the mode an agent is best placed to perform, for which Swanson is now in meeting 10. None needs a new meeting. All need rows in the ledger.

## 3. Meeting-by-meeting notes

Each session page now carries the added readings with a sentence or two on why. What follows is only what the pages do not say.

**Meeting 1.** Chamberlin (1890, reprinted 1965) was missing, which is odd for a geoscience group, since Platt's method is Chamberlin's with a loop drawn around it. Cleland's 2001 Geology paper makes the 2002 argument in four pages for geologists; consider assigning it to everyone and the 2002 paper to the discussant. Simon (1973) is the philosophical root of every discovery program in meeting 13 and the direct answer to the question in the title. Holmes (1987) is the source for standing question 5.

**Meeting 2.** Franklin (2005) and Colaço (2018) are the two papers that carried Steinle's idea forward. Franklin is about high-throughput biology and is the closest philosophy has come to describing what data-driven AI-for-science work does.

**Meeting 3.** The 1700 earthquake was dated by Japanese written records and tsunami modelling (Satake) and by tree rings (Yamaguchi), neither of which is Cascadia geology. Together with Atwater they are the best local example of Cleland's argument, and of borrowed competence for meeting 12.

**Meeting 4.** Oreskes (1988) is the failure case: the American community's methodological standards, not its data, kept drift out. It should be read as the cost of a strict rule about how inquiry must proceed.

**Meeting 5.** Kuhn (1961) argues that measurement rarely tests theory and mostly needs it. The pairing is fine as it stands.

**Meeting 6.** The most changed meeting. Ioannidis and CSEP are the case for the gate; Rzhetsky and colleagues (2015) is an exploration policy tested against the biomedical record and the most directly reusable paper for the agent design; Bergen and colleagues (2019) is the field's own account of machine learning as an exploratory instrument.

**Meeting 7.** No failure case for field work exists in the required pair; Powell supplies some. Kuklick and Kohler frame what makes field sciences different. The pair is fine.

**Meeting 8.** Fugelsang and colleagues (2004) gives the base rate the meeting needs: in live laboratory meetings, scientists first call an anomaly an error and pursue it only after it replicates. Rouet-Leduc and colleagues (2017) is a recent exploration-first discovery in this group's own field, and should be read with the same suspicion the page applies to Moore, since the success is what got published.

**Meeting 9.** Tarantola (2006) is three pages by a geophysicist on Popper and inverse problems. The Parkfield pair and Geller are the field's own history of hypothesis-first prediction, both its failure and what it built.

**Meeting 10.** Si, Yang, and Hashimoto (2025) is the cleanest measurement to date of machine novelty: rated more novel, less feasible, by blinded experts. Tshitoyan and colleagues (2019) is the one prospective test in the literature, done by training on papers before a cutoff and checking against later papers. Swanson (1986) is literature-based discovery, the mode an agent can most plausibly perform.

**Meeting 11.** Park, Leahey, and Funk (2023) is the claim Petersen's critique answers; the meeting was reading the critique without the target. Chu and Evans (2021) and Bloom and colleagues (2020) state the problem the agents are supposed to help with.

**Meeting 12.** See section 5.

**Meeting 13.** See sections 4 and 5.

## 4. Prior art started forty years late

The prior-art chapter began with Coscientist in 2023. The record of automated discovery is older, and its early entries are more relevant to this seminar than the recent ones.

Kulkarni and Simon (1988) built KEKADA, a program that reproduces Hans Krebs's path to the urea cycle. They built it from Frederic Holmes's reconstruction of Krebs's laboratory notebooks. Surprise is one of its control signals; it has an exploratory phase before any hypothesis exists. That is the method this seminar proposes: read how a scientist actually worked, and build the machine from that. It has been done once, and the group should know what it produced and what it did not. BACON (Langley 1981) recovered Kepler's third law from tables of numbers with no hypothesis in the loop. The Robot Scientist Adam (King and colleagues 2009) is the closed loop in its purest form and the best case for it. Eureqa (Schmidt and Lipson 2009) shows what "law discovery" means once the variables are chosen. Swanson (1986) is literature-based discovery. The chapter now opens with these five, each with a "what it does not establish" column like the rest.

Five entries cited as arXiv preprints now have peer-reviewed versions, and the chapter was updated: Co-Scientist in Nature (Gottweis and colleagues 2026), Gravity-Bench and LLM-SRBench in ICML 2025, MLE-bench and DiscoveryBench in ICLR 2025. DiscoveryBench and the Si human study were added as rows. A-Lab (Szymanski and colleagues 2023) and its reanalysis (Leeman and colleagues 2024) were added to the systems table: a closed loop reported 36 of 57 targets synthesized and the reanalysis found most of the claimed successes were misidentified or already known. It is the clearest published case of a loop scoring itself, and the best case exercise available for meeting 13.

A seventh gap was added to the chapter's list: no benchmark scores a system on what it does to the questions a field asks. Hao and colleagues (2026) measured that effect across 41 million papers.

The private prior-art file lists a lab benchmark, `agent-seisbench`, and asks whether the seminar is designing something new or writing the evaluation layer for it. That should be settled before meeting 9 on November 3, because meeting 9's output is the routing policy and it cannot be written without knowing what it routes into.

## 5. Meetings 12 and 13

### Meeting 12

Burke and Kitcher set the terms well, and the page's statement of the hypothesis and its disconfirmers is the best-designed part of the book. But neither paper measures anything, and the measured literature on breadth is large and directly on point. Jones (2009) is the mechanism behind Burke's decline: as knowledge accumulates, reaching a frontier takes longer, so people specialize and teams grow. If agents lower the cost of reaching a frontier, the polymathy hypothesis is a prediction of Jones's model, and the model says what else should change. Wuchty, Jones, and Uzzi (2007) measure what replaced the polymath. Teodoridis (2018) is the closest existing natural experiment: when the Kinect made motion sensing cheap, researchers collaborated less with the specialists whose skill it replaced. Teodoridis, Bikard, and Vakili (2019) predict where breadth pays: fast-moving fields, not slow ones. Leahey, Beckman, and Stanko (2017) measure what breadth costs today.

The disconfirming observation the page names has now been measured. Hao, Xu, Li, and Evans (2026) found, across 41 million papers, that scientists who use AI tools publish more and are cited more, and that the fields they work in narrow. Doshi and Hauser (2024) found the same shape in a controlled experiment on writing. Both concern tools rather than agents, but the session's prediction is about the direction of the effect, and the direction so far is the wrong one for the hypothesis.

Two cautions. First, the convenor's framing dates deep specialization to the 1900s. Stichweh (1992) dates disciplinary specialization to around 1800, and Whewell coined "scientist" in 1833. The nineteenth-century formation of disciplines and the twentieth-century growth of teams are different stories, and Burke's decline mostly belongs to the first. Second, the AI-and-science literature has already produced one withdrawn result: the Toner-Rodgers materials-lab study of 2024 was disavowed by MIT in May 2025 for data it could not verify. Single-firm and single-lab results in this area deserve the scrutiny the seminar applies to Moore.

Wright and colleagues (2025) is the only preprint in the book. It now has peer-reviewed company making the same point, and could be retired.

### Meeting 13

Meeting 13 carries two required papers, two discussant-led papers, a state-machine drawing, a benchmark specification, and the integration of six worksheets, in sixty minutes. It will not happen as written. Three changes would make it work.

First, keep a living architecture document from meeting 1 onward, with a named maintainer, updated in each meeting's 45-to-55-minute block. Meeting 13 then reviews a draft that already exists. Second, bring the state machine drawn; do not draw it in the hour. Third, use A-Lab and its reanalysis as the case exercise. It is a discovery-and-scrutiny pair for an autonomous system, and the group will have practised that reading since meeting 3.

## 6. Reference audit

All thirty-nine DOIs are registered, as the validation log already records. I checked volume, issue, pages, and year for each required and optional paper against the Crossref record; all agree.

- Cleland 2002 is twenty-three pages. Cleland 2001 in Geology is the same argument in four, written for this audience. Recommendation above.
- Chamberlin 1890 was missing. Platt cites it. Added.
- Burke is a book, Moore is an autobiographical prefatory chapter, and Becker is a program retrospective. Each is labelled as such on its page, which is right. Since the brief was peer-reviewed work: meeting 12's Paper A is the only required text that is not a peer-reviewed article. Jones (2009) could stand in for it if the group prefers a measured argument to a narrated one.
- The prior-art chapter's arXiv-only entries have been updated where a peer-reviewed version now exists. The AI Scientist, TinyScientist, FML-bench, and the two surveys remain preprints.
- The Geology DOI for Cleland 2001 contains angle brackets, which the link checker's URL scanner stopped at. The URL is percent-encoded in the sources and the checker now decodes before querying the registry.

## 7. Private analysis and mechanics

Eleven of thirteen private analyses are template stubs, and the two that are written rest on prior knowledge rather than on the texts. Meeting 1 is on September 8. Platt is seven pages and Cleland is available through the library; the meeting 1 analysis should be upgraded to a full-text basis before Tuesday, or the prediction-scoring exercise will compare the group with a recollection.

November 24 is the Tuesday of Thanksgiving week, two days before the holiday. Meeting 12 is the convenor's own hypothesis and the meeting most likely to lose attendance. If the order of meetings can move while the dates stay fixed, swap meetings 11 and 12: polymathy on November 17, and the bibliometrics meeting, which depends least on who is in the room, on November 24. This is a recommendation; the files were not reordered.

The hour has five blocks and a case exercise. Where a discussant presents, in meetings 11 and 13, the 10-to-25-minute comparison block should be the discussant's time rather than a separate block.

The validator checked that required and discussant papers are cited on their pages but not that optional keys are. It now checks both, so the fifty-seven additions cannot drift out of step with the pages.

## 8. What was added

Fifty-seven peer-reviewed papers, every one verified against the Crossref registry, with bibliographic fields taken from the registry record. The required pairs are unchanged. By meeting:

| Meeting | Added |
|:--|:--|
| 1 | Chamberlin 1965; Cleland 2001; Simon 1973; Klahr and Dunbar 1988; Holmes 1987 |
| 2 | Franklin 2005; Colaço 2018 |
| 3 | Satake et al. 1996; Yamaguchi et al. 1997 |
| 4 | Vine and Matthews 1963; Oreskes 1988 |
| 5 | Kuhn 1961; Tal 2013 |
| 6 | Ioannidis 2005; Schorlemmer et al. 2018; Rzhetsky et al. 2015; Leonelli 2014; Bergen et al. 2019 |
| 7 | Kuklick and Kohler 1996 |
| 8 | Kuhn 1962; Fugelsang et al. 2004; Copeland 2019; Rouet-Leduc et al. 2017; Schmidhuber 2010 |
| 9 | Tarantola 2006; Kirchner 2006; Bakun and Lindh 1985; Bakun et al. 2005; Geller 1997 |
| 10 | Si, Yang, and Hashimoto 2025; Sourati and Evans 2023; Tshitoyan et al. 2019; Foster, Rzhetsky, and Evans 2015; Swanson 1986 |
| 11 | Park, Leahey, and Funk 2023; Chu and Evans 2021; Bloom et al. 2020 |
| 12 | Jones 2009; Wuchty, Jones, and Uzzi 2007; Stichweh 1992; Teodoridis 2018; Teodoridis, Bikard, and Vakili 2019; Leahey, Beckman, and Stanko 2017; Hao et al. 2026; Doshi and Hauser 2024 |
| 13 | Langley 1981; Kulkarni and Simon 1988; King et al. 2009; Schmidt and Lipson 2009; Wang et al. 2023; Kitano 2021; Gottweis et al. 2026; Szymanski et al. 2023; Leeman et al. 2024; Kapoor and Narayanan 2023; Rainforth et al. 2024; Lehman and Stanley 2011 |

Considered and not added, with the reason: Simmons, Nelson, and Simonsohn (2011), because Nosek covers the mechanics; Gelman and Loken (2014), because American Scientist is not peer reviewed; King and colleagues (2004), because the 2009 paper supersedes it; Krenn and colleagues (2022) and Coley, Eyke, and Jensen (2020), because Messeri and Wang cover the same ground for this purpose; Harman (1965) and Klahr and Simon (1999), because Simon 1973 and Klahr and Dunbar 1988 are the sharper versions; Noy and Zhang (2023), because it concerns writing tasks; Jordan and colleagues (2011), because CSEP covers it.

Files changed: `references.bib`, `curriculum.json`, the thirteen session pages (two of them renamed by the swap), `reading-library.qmd`, `prior-art.qmd`, `rubrics.qmd`, `notes.qmd`, `index.qmd`, `_quarto.yml`, `README.md`, `READING-AUDIT.md`, `VALIDATION.md`, `tools/validate.py`, `tools/check_links.py`, and this file. Under `private/`, the meeting-1 analysis was rewritten, the two swapped analysis stubs were renamed and redated, and one line in the proposal backlog was renumbered.
