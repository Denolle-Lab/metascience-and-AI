# Methods as compositions of the unit, and the step 0 decision

Reference for the `unit-of-inquiry` skill. Human-edited, versioned with the unit graph (`unit.qmd`, graph v0.2). The agent's SKILL.md carries the operative one-line rules; this file carries the full rule, its rationale, and the reading that fixed it. Edit here first, then shorten into SKILL.md.

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


| Method | How it runs the graph | Its guard |
|:--|:--|:--|
| `strong-inference` | G with n ≥ 2; one S shared by all rivals; C set; O and M once per pass; V run, which Platt's step 3 assumes; every outcome excludes; R then G | If S cannot make the E_i differ, stop and say so; do not run a test all rivals pass (Platt 1964, p. 347) |
| `trace-series` | G with rivals for a past event; C found; O repeated over independent traces, each with its own chain, in place of V; K by best explanation within the stated set; a rival need not be excluded to be beaten | Abstain when no trace discriminates; name the trace that would (Cleland 2002, pp. 484, 487–494) |
| `natures-repetition` | C found but repeated by nature; O over the repetitions; a regularity fitted at K with out-of-sample checks in place of V; no power to set or remove C, so no causal claim from the fit alone | Report the fit as a regularity, not a mechanism; two rivals can predict the same regularity (Cleland 2002, p. 485; Platt 1964, pp. 351–352) |
| `exploration-first` | The before-G node run as a loop until a phenomenon repeats; then re-run step 0 | Never emit a claim record from this method; its output is a phenomenon and a reframed question (Cleland 2002, p. 486) |

