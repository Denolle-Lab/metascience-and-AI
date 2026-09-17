# Node rules, with sources

Reference for the `unit-of-inquiry` skill. Human-edited, versioned with the unit graph (`unit.qmd`, graph v0.2). The agent's SKILL.md carries the operative one-line rules; this file carries the full rule, its rationale, and the reading that fixed it. Edit here first, then shorten into SKILL.md.

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

