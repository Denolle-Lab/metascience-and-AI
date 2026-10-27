# Entry state: valid variable, or a record of the gap statement?

Written October 27, 2026 by the workflow `entry-state-evaluation` (branch `framework-v0.5`, commit 2798f89 with uncommitted g21 changes). Not committed.

- **Script:** `tools/roadmap/g21_entry_state.py`, new step 9 (`python tools/roadmap/g21_entry_state.py audit`; also runs at the end of a full run). Rerun today, both ways; the 60-paper audit sample came out with the same keys, order and coded states.
- **Data:** `private/data/roadmap/derived/entry/entry_state.json` (key `blind_audit`), readable copy in `ENTRY.md` section 8. Blind re-codings saved verbatim in `private/data/roadmap/derived/entry/blind_audit.json`.
- **Codings read:** round 1 (tag calc1) 233 valid of 235 files; test-retest (tag gold-r2) 50 valid of 51; round 2 (tag r2) 0, the folder does not exist yet. All valid codings are codebook 1.5.0, coder claude-opus-5-5. Valid = `tools/check_coding.py validate()` passes.
- **Terms.** *Batch coding*: the round-1 coding by Claude Opus 5.5 through the API. *Blind coders A and B*: two Claude agents run in Claude Code, same model family, who saw only the paper (key, DOI, title, PDF and XML text) and not the batch coding or each other. *Consensus*: the value A and B both gave; *split* when they differ. *Operational start*: what the work could not have begun without (data in hand, an event, an instrument, a method, a mandate, a surprising observation, a prior result, a hypothesis, or only a literature gap). *Rhetorical gap statement*: the introduction sentence that names what is unknown, unclear, debated or lacking, move 2 of Swales's (1990) "create a research space" model.

## Verdict

1. **As coded under codebook 1.5.0, entry state is a valid variable for how a paper frames its start, not for what started the work.** Blind coders who were asked separately for the operational start found a concrete object behind most `problem` papers.
2. **`problem` is a catch-all.** Both blind coders confirm it in 20 of 36 sampled `problem` papers (56%). Weighted back to round 1, `problem` falls from 78% of papers to about 44% (95% interval 31 to 57%), with another 16% where A and B split. In the same 36 papers the agreed operational start is a literature gap alone in 3 (8%) and a concrete object in 22 (61%). The other six states hold up: 20 of 24 confirmed by both coders.
3. **Agreement is above chance but short of Krippendorff's 0.8, even for one coder run twice.** Krippendorff alpha for entry state is 0.77 between two batch runs (inside the 0.667 to 0.8 band Krippendorff (2019) allows for tentative conclusions), 0.81 between the two blind coders, and 0.67 and 0.60 between each blind coder and the batch coding. All intervals exclude zero; the blind-to-batch values sit at or below the 0.667 floor. Entry node is weaker (alpha 0.51 and 0.40 against the batch coding). All coders are one model family, so these are upper bounds on what two people would reach.

The one action needed from you: decide whether to adopt the 1.6.0 draft below (a separate operational-start field), and whether the human gold coding of the entry should use the 60 audit packets already built.

## Evidence

### 1. Agreement and alpha (60 papers)

Alpha is Krippendorff's nominal alpha, (A_o - A_e) / (1 - A_e), with chance agreement A_e from the pooled category counts; intervals are 2000 bootstrap resamples of papers (Hayes & Krippendorff, 2007). Weighted agreement reweights the stratified sample to round 1 (see section 4).

| Field | Pair | Agreement | Chance | Alpha [95%] | Weighted agreement |
|:--|:--|--:|--:|--:|--:|
| state | A vs B | 0.85 | 0.23 | 0.81 [0.68, 0.92] | 0.84 |
| state | A vs batch | 0.77 | 0.30 | 0.67 [0.50, 0.82] | 0.73 |
| state | B vs batch | 0.72 | 0.29 | 0.60 [0.43, 0.76] | 0.70 |
| node | A vs B | 0.83 | 0.26 | 0.78 [0.64, 0.89] | 0.86 |
| node | A vs batch | 0.68 | 0.36 | 0.51 [0.29, 0.68] | 0.65 |
| node | B vs batch | 0.62 | 0.37 | 0.40 [0.19, 0.57] | 0.61 |
| rhetorical gap flag | A vs B | 0.90 | 0.54 | 0.78 [0.60, 0.93] | |
| operational start, 9 classes | A vs B | 0.83 | 0.13 | 0.81 [0.69, 0.91] | |
| operational start, 4 groups | A vs B | 0.90 | 0.53 | 0.79 [0.62, 0.93] | |

For comparison, the batch test-retest on 50 gold papers (calc1 against gold-r2, same model, same instructions) gives state agreement 0.92, alpha 0.77 [0.50, 0.95]. All three coders give the same state in 40 of 60 papers; three-way alpha 0.70.

The blind coders agree with each other more than with the batch coder. Their output form asked for an operational start and a gap flag, which likely pulled them away from `problem`. So the gap between 0.81 and 0.60 to 0.67 measures sensitivity to the instruction as much as coder error. That sensitivity is itself the finding: the label moves when the coder is asked to think about what started the work.

### 2. Which batch states the blind coders confirm

Rows are the batch state; "both confirm" = A and B give the same state as the batch. Interval: Wilson (1927) 95% score interval.

| Batch state | n | A confirms | B confirms | Both confirm [95%] | Consensus on another state | Split |
|:--|--:|--:|--:|--:|:--|--:|
| problem | 36 | 24 | 23 | 20 (56%) [40, 71%] | capability 5, data_without_theory 3, anomaly 1 | 7 |
| capability | 4 | 4 | 4 | 4 | | 0 |
| anomaly | 4 | 4 | 4 | 4 | | 0 |
| challenged_result | 4 | 4 | 4 | 4 | | 0 |
| hypothesis | 4 | 4 | 2 | 2 | | 2 |
| data_without_theory | 4 | 3 | 3 | 3 | anomaly 1 | 0 |
| external_goal | 4 | 3 | 3 | 3 | problem 1 | 0 |

The traffic runs one way. [Withheld until the human coding ends: names or describes a paper in the blind coding set.]

### 3. The quote: what `problem` is recording

| Measure | Value |
|:--|:--|
| Blind coders' own `problem` quotes flagged as gap statements | A 21/25 (84%), B 21/24 (88%) |
| Blind coders' quotes for any other state flagged as gap statements | A 0/35, B 0/36 |
| Batch `problem` quotes overlapping a blind coder's quote | 22/36; of these, 18 flagged gap |
| Batch `problem` quotes with a g21 regex gap marker | 24/36 |
| g21 regex gap marker against the coders' flag, 120 quotes | agreement 0.86 (both 32, regex only 7, flag only 10, neither 71) |

Under 1.5.0, `problem` is close to "the paper has a gap statement and the coder quoted it". No other state is ever supported by a gap sentence. The regex gap marker agrees with the coders' flag on 86% of quotes, so the step-5 figure for all 181 round-1 `problem` codings (49% carry a gap marker, 94% of located quotes sit in the abstract or introduction) is a usable proxy.

### 4. Population estimate

The sample is stratified (36 of 181 `problem`, four of each other state), so whole-sample shares are reweighted by papers with that batch state divided by sampled papers with it. Intervals: stratified bootstrap, 2000 draws.

| State | Batch | Consensus [95%] |
|:--|--:|--:|
| problem | 78% | 44% [31, 57%] |
| capability | 11% | 22% [13, 30%] |
| data_without_theory | 2% | 8% [2, 16%] |
| anomaly | 2% | 5% [2, 10%] |
| challenged_result, hypothesis, external_goal | 3%, 3%, 2% | 3%, 1%, 2% |
| split (A and B differ) | | 16% [7, 27%] |

### 5. Operational start behind `problem`

Agreed operational start for the 36 batch `problem` papers: data in hand 8, new method or model 7, new instrument or deployment 3, mandate or project goal 2, event 1, surprising observation 1 (concrete object together: 22, 61%, Wilson 45 to 75%); prior result to test 3; stated hypothesis 1; literature gap only 3 (8%, Wilson 3 to 22%); split 7. Either coder names literature gap only in 7 of 36.

Even the 20 papers that stay `problem` under consensus mostly have a concrete start: literature gap only 3, new method 3, data in hand 3, mandate 2, instrument 1, event 1, prior result 2, split 5. Eight of the 36 are "consensus `problem`, both quotes gap statements, agreed concrete start": the framing and the start disagree, and both coders still kept the framing.

The state implied by the agreed operational start (data in hand to `data_without_theory`, instrument or method to `capability`, and so on; `START_TO_STATE` in the script) matches the consensus state in 26 of 42 papers where both are agreed: 3 of 16 for `problem`, 23 of 26 for the other states. The other six states already describe a start; `problem` describes a framing.

Over round 1 (weighted), the agreed operational start is a concrete object for about 62% [49, 75%] of papers, a prior result for 10%, a literature gap alone for 6.5% [0, 15%], with 19% split.

[Withheld until the human coding ends: names or describes a paper in the blind coding set.] Rule 3 of the draft below targets the first kind.

### 6. Problem subtypes

The coders wrote free-text subtypes for their `problem` papers. Grouped by `SUBTYPE_GROUPS` in the script (leading words of the label, first rule wins, no label left ungrouped):

| Group | A | B | Agreed (21 papers both call `problem`) |
|:--|--:|--:|--:|
| process or mechanism unknown | 10 | 10 | 7 |
| quantity or effect unconstrained | 5 | 3 | 3 |
| method or instrument limitation | 4 | 5 | 3 |
| data gap | 1 | 2 | 1 |
| applied need (hazard, management) | 2 | 1 | 1 |
| theory incomplete; debated history or timing; trend attribution | 1 each | 1 each | 1 each |
| split | | | 3 |

A and B agree on the group in 18 of 21 (alpha 0.82). The subtype describes what kind of question is posed, not what started the work, so it does not fix the catch-all.

### 7. The walk (steps 3 and 4 of g21, round 1, 233 codings)

- In 50 of 181 `problem` codings the walk does not open at Q; in 49 of these the first step is a cited or inherited result (O cited 20, H cited 12, S cited 4, N inherited 4, O inherited 3, others 6). The coder's own walk often starts from prior work or data and reaches the question second.
- Revisits answer the narrow question below.

## Is the entry state revisited in the walk?

No, and it cannot be in the current schema. Entry state is one paper-level label; the walk has nodes, modes and moves, and no state. What can recur is the entry node. From g21 step 4 (rerun today, 233 round-1 codings; revisit = the node returns after at least one other node):

| Measure | Value |
|:--|:--|
| Entry node revisited, all papers | 77/233 (33%) |
| `problem` papers: entry node (Q for 179 of 181) revisited | 42/181 (23%); any later step there 44/181 (24%) |
| Papers entering at Q: later Q step | 43/189 (23%); after another node 40/189 (21%) |
| Moves of those later Q steps | new 44, cited 2, repeat 1 |
| `capability` papers: entry node (N for 24 of 25) revisited | 21/25 (84%) |
| Question reframed after a failure | 0/233 (0 of 101 `return_after_failure` steps sit at Q or are followed by Q) |

So in roughly one paper in five the question comes back, almost always as a new author question further on, never as a reframing after something failed. Whether that reflects practice or the coder reading the question from one introduction paragraph cannot be told from the codings; the blind audit points to the second for the entry itself.

## Proposal for codebook 1.6.0 (draft, not adopted)

Three options were weighed against this evidence.

- **A. Keep the stated entry, add a separate operational-start field.** Keeps the 233 round-1 codings and the 50 test-retest pairs comparable; measures the thing the audit shows `problem` misses. Recommended.
- **B. Split `problem` into subtypes.** Subtypes are codable (alpha 0.82 on 21 papers) but describe the kind of question, not the start. Not recommended as the fix; could be added later as an optional `question_kind`.
- **C. Require the entry quote to describe what started the work.** Changes the meaning of an existing field and breaks comparison with round 1. Its rule is kept, but applied only to the new field.

Draft wording for `agents/coder/CODEBOOK.md` section 2 (replaces the current section 2; nothing is edited in the codebook until you adopt it):

> ## 2. Entry
> Code the entry twice: how the paper frames its start, and what started the work. The two may differ; record both as the paper gives them.
>
> **2a. Stated entry (`entry.state`, `entry.node`, `entry.evidence`, `entry.page`).** Pick one entry state and quote the sentence that establishes it: `anomaly` (a surprising observation) · `problem` (an unsolved question) · `challenged_result` (a published result the paper sets out to check or replicate) · `hypothesis` (a hypothesis or a theory's prediction) · `data_without_theory` · `capability` (a new instrument, method, archive, or computer) · `external_goal` (a goal set by someone else, such as a benchmark or a mission). A gap statement ("X remains unclear", "few studies have considered Y") supports `problem` here. Give the node where the paper enters the graph.
>
> **2b. Operational start (`entry.start.kind`, `entry.start.evidence`, `entry.start.page`).** Pick what the work could not have begun without, and quote the sentence that names it:
> `data_in_hand` (a data set, catalogue, archive, sample collection or core that existed before this study's question) · `event_occurred` (an earthquake, eruption, flood, new exposure, drilling or other event that made the study possible or necessary) · `new_instrument_or_deployment` (an instrument built, or a deployment, network or field campaign) · `new_method_or_model` (a method, model, code or algorithm the authors built or adapted, including their own earlier one) · `mandate_or_project_goal` (a funded project, agency, regulation, benchmark or intercomparison that set the goal) · `surprising_observation` (an observation that contradicted an expectation) · `prior_result_to_test` (a named published result that the paper checks, tests or replicates) · `stated_hypothesis` (a hypothesis stated before the work) · `literature_gap_only` (none of the above is named anywhere in the paper).
> 1. The 2b quote must name the object or the act: the data set, the event, the instrument, the method, the mandate, the observation, the result, the hypothesis. A sentence whose only content is that something is unknown, unclear, debated, lacking or understudied is not evidence for 2b.
> 2. Read the abstract, introduction, data and methods sections, and the acknowledgements and funding statement before choosing `literature_gap_only`.
> 3. `prior_result_to_test` needs a named result that this paper checks. A cited result that only motivates the question is background; code the object that let the authors take the question up.
> 4. If more than one applies, pick the one without which the study could not have been done; if the paper says which came first, follow the paper.
> 5. 2a and 2b may point to different states. That is not an error; do not change 2a to match 2b.

Schema and definitions: `entry` gains a required `start` object `{kind, evidence, page}` with `kind` in the nine values above and `evidence` at most 25 words; `agents/coder/definitions.json` gains the nine definitions (wording as above) and the codebook version becomes 1.6.0.

**Expected effect on reliability.** The stated entry is unchanged, so its test-retest alpha (0.77) should hold. For the new field the two blind coders already reach alpha 0.81 on nine classes and 0.79 on four groups without these rules; four of their ten disagreements are literature gap against prior result, which rule 3 addresses. A batch-to-blind alpha for 2b is unknown until a 1.6.0 run is compared with the 60 blind codings. Expect it below 0.81 for the same reason the state fell to 0.60 to 0.67, since the batch coder's prompt and the blind coders' differ.

**Expected effect on the outcome analysis (g17).** `tools/roadmap/g17_outcomes.py` tests `bin:entry <state>` only for states present in at least 10 and at most n - 10 papers. Round 1 has two: `entry problem` (prevalence 0.78) and `entry capability` (0.11). Neither is associated with any outcome after correction: |rho| at most 0.16, all q above 0.18; the largest is `entry capability` with reference breadth, rho 0.16 [0.03, 0.29], q 0.19. With 2b, the weighted estimates give a concrete-object start near 60%, a prior result near 10% and a literature gap near 6 to 15% of papers. That is two or three binary features with usable prevalence, plus one derived feature, "framing and start differ" (stated `problem` with a concrete start). Each added feature adds five tests to the Benjamini-Hochberg family (245 tests now). Until then, the current null for `entry problem` should be reported as a null for framing, not for how work starts.

**What it costs.** One more quote per paper. Recoding round 1 under 1.6.0 needs an API run, which this workflow did not do. The cheaper path is to code 2b on round 2 as it arrives and on the 60 audit papers for a batch-to-blind check.

## Limitations

- Blind coders A and B and the batch coder are one model family (Claude). Their agreement shows the label is stable for this model, not that it is right. Human gold coding of the entry is pending.
- 60 papers, stratified: 36 `problem` and four of each other state. Per-state confirmation for the six small states rests on four papers each (Wilson intervals 30 to 100%).
- The blind coders' output form asked for an operational start and a gap flag, which may have primed them against `problem`.
- Operational starts were judged from the paper alone. Whether data in hand truly came before the question is the authors' account, or an inference from it.
- Round 2 has no codings yet (tag r2 folder absent); every number here is round 1.

## References

- Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard reliability measure for coding data. *Communication Methods and Measures, 1*(1), 77–89. https://doi.org/10.1080/19312450709336664
- Krippendorff, K. (2019). *Content analysis: An introduction to its methodology* (4th ed.). SAGE Publications. https://doi.org/10.4135/9781071878781
- Swales, J. M. (1990). *Genre analysis: English in academic and research settings*. Cambridge University Press.
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association, 22*(158), 209–212. https://doi.org/10.1080/01621459.1927.10502953

All four are paywalled; entries and status are in `private/bibliography.md`, section "Entry-state evaluation".
