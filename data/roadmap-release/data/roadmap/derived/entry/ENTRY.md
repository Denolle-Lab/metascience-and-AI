# Entry state: catch-all check

Script `tools/roadmap/g21_entry_state.py`; data `private/data/roadmap/derived/entry/entry_state.json`. Valid codings read at run time: calc1 233, r2 0 (tools/check_coding.py validate()). Invalid files skipped: calc1 2, r2 0, gold-r2 1. One model coder (Claude, codebook 1.5.0). Definitions of every measure are in the script docstring.

**Question.** Does `problem` record what started the work, or the gap statement every introduction carries (Swales 1990, "create a research space")? The codings alone cannot settle it; they can show whether the label behaves like a default. The blind audit sample at the end is for the direct check.

## Headline

- `problem` is 78% of 233 valid codings; Q is 81% of entry nodes.
- Test-retest on 50 gold papers: agreement 0.92, chance agreement 0.655 (one category holds most papers), so alpha 0.768 [0.504, 0.945]. The two runs quote an identical evidence string in 52% of papers and overlapping evidence (one quote contains the other, or token Jaccard at least 0.5) in 74%; same locator 88%. The label repeats somewhat more often than the supporting sentence.
- For 50 of 181 `problem` papers (28%) the coded walk does not start at Q: O 23, H 14, N 4, S 4, I 2, E 2, C 1. In 49 of them the first step is a cited or inherited result (move cited or inherited): the walk opens on prior work and the question follows. That prior result is a candidate for the real start (challenged_result or anomaly) and is one thing the audit should check.
- After entry, Q comes back in 23% of `problem` papers; no paper reframes its question after a failure (0 of 233): the 101 returns after failure land on P, R, V, I and other nodes, never on Q.
- `problem` evidence sits in the abstract or introduction in 94% of the 87 papers with a section, and on the first article page in 91% of the 97 with a page number. 49% of its quotes carry a gap marker and 40% carry a gap marker with no origin marker; for `capability` the figures are 4% and 4%.
- What the codings cannot show: whether a data set, event, instrument or mandate started a `problem` paper. That is the job of the blind audit sample (section 7).

## 1. Distribution

**calc1** (n = 233)

| Entry state | Papers | Share |
|:--|--:|--:|
| problem | 181 | 78% |
| capability | 25 | 11% |
| challenged_result | 6 | 3% |
| hypothesis | 6 | 3% |
| data_without_theory | 5 | 2% |
| anomaly | 5 | 2% |
| external_goal | 5 | 2% |

| Entry node | Papers | Share |
|:--|--:|--:|
| Q | 189 | 81% |
| N | 27 | 12% |
| O | 9 | 4% |
| H | 7 | 3% |
| F | 1 | 0% |

**pooled** (n = 233)

| Entry state | Papers | Share |
|:--|--:|--:|
| problem | 181 | 78% |
| capability | 25 | 11% |
| challenged_result | 6 | 3% |
| hypothesis | 6 | 3% |
| data_without_theory | 5 | 2% |
| anomaly | 5 | 2% |
| external_goal | 5 | 2% |

| Entry node | Papers | Share |
|:--|--:|--:|
| Q | 189 | 81% |
| N | 27 | 12% |
| O | 9 | 4% |
| H | 7 | 3% |
| F | 1 | 0% |

## 2. Test-retest (calc1 against gold-r2, same model, independent runs)

**Entry state**, 50 papers. Observed agreement 0.92; agreement expected by chance from the pooled marginals 0.655; Krippendorff alpha 0.768 (95% bootstrap [0.504, 0.945]); Cohen kappa 0.766 (chance 0.658). alpha = (A_o - A_e) / (1 - A_e) = (0.92 - 0.655) / (1 - 0.655) = 0.768.

Confusion matrix (rows calc1, columns gold-r2):

| | problem | capability | hypothesis | data_without_theory | external_goal |
|:--|--:|--:|--:|--:|--:|
| problem | 38 | 2 | 0 | 1 | 0 |
| capability | 1 | 5 | 0 | 0 | 0 |
| hypothesis | 0 | 0 | 1 | 0 | 0 |
| data_without_theory | 0 | 0 | 0 | 1 | 0 |
| external_goal | 0 | 0 | 0 | 0 | 1 |

| Category | calc1 | gold-r2 | both | P(same in gold-r2 given calc1) | P(same in calc1 given gold-r2) | specific agreement |
|:--|--:|--:|--:|--:|--:|--:|
| problem | 41 | 39 | 38 | 0.927 | 0.974 | 0.95 |
| capability | 6 | 7 | 5 | 0.833 | 0.714 | 0.769 |
| hypothesis | 1 | 1 | 1 | 1.0 | 1.0 | 1.0 |
| data_without_theory | 1 | 2 | 1 | 1.0 | 0.5 | 0.667 |
| external_goal | 1 | 1 | 1 | 1.0 | 1.0 | 1.0 |

Disagreements: problem -> capability (2); capability -> problem (1); problem -> data_without_theory (1)

**Entry node**, 50 papers. Observed agreement 0.9; agreement expected by chance from the pooled marginals 0.642; Krippendorff alpha 0.721 (95% bootstrap [0.483, 0.909]); Cohen kappa 0.719 (chance 0.644). alpha = (A_o - A_e) / (1 - A_e) = (0.9 - 0.642) / (1 - 0.642) = 0.721.

Confusion matrix (rows calc1, columns gold-r2):

| | N | O | Q | H | S | F |
|:--|--:|--:|--:|--:|--:|--:|
| N | 6 | 0 | 0 | 0 | 0 | 0 |
| O | 0 | 1 | 0 | 0 | 0 | 1 |
| Q | 2 | 1 | 38 | 0 | 0 | 0 |
| H | 0 | 0 | 0 | 0 | 1 | 0 |
| S | 0 | 0 | 0 | 0 | 0 | 0 |
| F | 0 | 0 | 0 | 0 | 0 | 0 |

| Category | calc1 | gold-r2 | both | P(same in gold-r2 given calc1) | P(same in calc1 given gold-r2) | specific agreement |
|:--|--:|--:|--:|--:|--:|--:|
| N | 6 | 8 | 6 | 1.0 | 0.75 | 0.857 |
| O | 2 | 2 | 1 | 0.5 | 0.5 | 0.5 |
| Q | 41 | 38 | 38 | 0.927 | 1.0 | 0.962 |
| H | 1 | 0 | 0 | 0.0 | None | 0.0 |
| S | 0 | 1 | 0 | None | 0.0 | 0.0 |
| F | 0 | 1 | 0 | None | 0.0 | 0.0 |

Disagreements: Q -> N (2); H -> S (1); Q -> O (1); O -> F (1)

State and node both the same: 88%. Same evidence quote (identical after case, punctuation and whitespace normalization): 52%; overlapping quote (one contains the other, or token Jaccard at least 0.5): 74%; same locator: 88%.

## 3. Internal consistency

Entry node equals the node of the first step of the walk in 153 of 233 papers (66%); the entry node appears somewhere in the walk in 100%.

| Entry state | Expected node | At expected node | Entry nodes | First-step nodes |
|:--|:--|--:|:--|:--|
| problem | Q | 179/181 (99%) | N 2, Q 179 | Q 131, O 23, H 14, N 4, S 4, I 2, E 2, C 1 |
| capability | N | 24/25 (96%) | N 24, O 1 | N 10, Q 10, O 4, H 1 |
| anomaly | E,O | 4/5 (80%) | O 4, Q 1 | O 4, H 1 |
| challenged_result | C,H,Q,V | 6/6 (100%) | Q 5, H 1 | Q 4, H 2 |
| hypothesis | H | 6/6 (100%) | H 6 | Q 3, O 2, H 1 |
| data_without_theory | E,O | 4/5 (80%) | O 4, F 1 | Q 2, F 1, S 1, O 1 |
| external_goal | D,N,Q | 5/5 (100%) | N 1, Q 4 | Q 3, H 1, N 1 |

First step (node and move) when it is not the entry node: problem: O cited 20, H cited 12, S cited 4, N inherited 3, O inherited 3, I cited 2, E cited 2, H inherited 1, C cited 1, Q new 1, H new 1; capability: Q new 10, O cited 3, H cited 1, O inherited 1; anomaly: H cited 1, O cited 1; challenged_result: Q cited 1, H inherited 1, H cited 1; hypothesis: Q new 3, O cited 2; data_without_theory: Q new 2, F new 1, S cited 1; external_goal: H cited 1.

## 4. Revisits of the entry node

Revisited = the entry node comes back after at least one other node (run-collapsed walk). Reframe after failure = a `return_after_failure` step at Q, or one followed directly by Q.

| Entry state | n | Entry node in walk | Revisited | Any later step there (raw) | Q twice or more (collapsed) | Any return after failure | Reframe after failure |
|:--|--:|--:|--:|--:|--:|--:|--:|
| problem | 181 | 100% | 23% | 24% | 22% | 29% | 0% |
| capability | 25 | 100% | 84% | 92% | 8% | 44% | 0% |
| anomaly | 5 | 100% | 80% | 80% | 40% | 0% | 0% |
| challenged_result | 6 | 100% | 17% | 17% | 17% | 33% | 0% |
| hypothesis | 6 | 100% | 67% | 67% | 0% | 50% | 0% |
| data_without_theory | 5 | 100% | 80% | 80% | 0% | 0% | 0% |
| external_goal | 5 | 100% | 20% | 40% | 0% | 60% | 0% |
| all | 233 | 100% | 33% | 35% | 19% | 31% | 0% |

By entry node rather than state: of the 189 papers that enter at Q, 43 (23%) have a later Q step and 40 (21%) return to Q after another node. Moves of those later Q steps: new 44, cited 2, repeat 1.

The 101 `return_after_failure` steps sit at P 36, R 34, V 9, I 8, N 5, H 2, O 2, S 2, D 1, C 1, F 1; the step after them is at C 27, V 15, K 12, I 12, H 7, X 7, S 5, O 4, N 3, R 3, D 2, P 2, F 1, E 1.

## 5. Where the entry evidence sits and how it is worded

Quote located in the XML text: {'None': 108, 'True': 119, 'False': 6} (True = found, False = XML present but quote not found, None = no XML text).

| Entry state | n | With section | Abstract | Introduction | Section 1, heading unknown | Later section | With page | Median page in article | Page 1 | Pages 1-2 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| problem | 181 | 87 | 30% | 64% | 0% | 6% | 97 | 1.0 | 91% | 100% |
| capability | 25 | 14 | 36% | 57% | 0% | 7% | 12 | 1.0 | 67% | 92% |
| anomaly | 5 | 5 | 40% | 60% | 0% | 0% | 0 | None | n/a | n/a |
| challenged_result | 6 | 3 | 0% | 67% | 0% | 33% | 3 | 1.0 | 100% | 100% |
| hypothesis | 6 | 2 | 0% | 50% | 0% | 50% | 4 | 1.5 | 50% | 75% |
| data_without_theory | 5 | 4 | 0% | 75% | 0% | 25% | 1 | 1.0 | 100% | 100% |
| external_goal | 5 | 5 | 20% | 80% | 0% | 0% | 0 | None | n/a | n/a |
| all | 233 | 120 | 28% | 64% | 0% | 8% | 117 | 1.0 | 87% | 98% |

Marker families (regular expressions in the script, `MARKERS`): gap = names a gap or difficulty; aim = states the paper's own aim; origin = points to a concrete starting object (event, dataset, instrument, mission, prior result).

| Entry state | n | Any gap marker | Any aim marker | Any origin marker | Gap without origin | Origin without gap |
|:--|--:|--:|--:|--:|--:|--:|
| problem | 181 | 49% | 9% | 18% | 40% | 9% |
| capability | 25 | 4% | 60% | 52% | 4% | 52% |
| anomaly | 5 | 40% | 0% | 40% | 20% | 20% |
| challenged_result | 6 | 33% | 50% | 67% | 33% | 67% |
| hypothesis | 6 | 0% | 33% | 0% | 0% | 0% |
| data_without_theory | 5 | 0% | 20% | 80% | 0% | 80% |
| external_goal | 5 | 40% | 20% | 40% | 0% | 0% |
| all | 233 | 41% | 17% | 25% | 33% | 16% |

Gap markers in `problem` evidence: however 36, unknown or unclear 19, need 13, remains unclear or unknown 12, challenge 8, lack 8, poorly understood or constrained 7, debated or controversial 5, not well understood or constrained 4, few or limited studies 3, little or less is known 1, gap 1, open question 1.

## 6. By OpenAlex subfield and journal family

**subfield** (groups under 10 papers pooled). Entry state (states under 10 pooled) by subfield: Cramer's V 0.128 (bias-corrected 0.0), permutation p 0.919. Problem vs other: V 0.119, p 0.8616.

| subfield | n | problem | states |
|:--|--:|--:|:--|
| Atmospheric Science | 74 | 80% | problem 59, capability 8, external_goal 3, challenged_result 2, anomaly 2 |
| Geophysics | 64 | 75% | problem 48, capability 7, hypothesis 3, challenged_result 2, anomaly 2, data_without_theory 1, external_goal 1 |
| Earth-Surface Processes | 26 | 85% | problem 22, capability 2, anomaly 1, hypothesis 1 |
| Artificial Intelligence | 17 | 76% | problem 13, capability 2, challenged_result 1, data_without_theory 1 |
| Geochemistry and Petrology | 15 | 67% | problem 10, data_without_theory 2, hypothesis 2, capability 1 |
| Water Science and Technology | 14 | 86% | problem 12, capability 1, challenged_result 1 |
| pooled small groups | 13 | 69% | problem 9, capability 3, external_goal 1 |
| Oceanography | 10 | 80% | problem 8, data_without_theory 1, capability 1 |

**family** (groups under 10 papers pooled). Entry state (states under 10 pooled) by family: Cramer's V 0.182 (bias-corrected 0.108), permutation p 0.1136. Problem vs other: V 0.227, p 0.0308.

| family | n | problem | states |
|:--|--:|--:|:--|
| Wiley non-AGU | 76 | 88% | problem 67, capability 4, hypothesis 2, challenged_result 2, data_without_theory 1 |
| EGU/Copernicus | 64 | 70% | problem 45, capability 8, external_goal 4, anomaly 3, challenged_result 2, data_without_theory 1, hypothesis 1 |
| Springer Nature (non-portfolio) | 44 | 68% | problem 30, capability 7, data_without_theory 3, challenged_result 1, external_goal 1, anomaly 1, hypothesis 1 |
| pooled small groups | 19 | 68% | problem 13, capability 3, hypothesis 2, challenged_result 1 |
| AGU | 16 | 81% | problem 13, capability 3 |
| Nature portfolio | 14 | 93% | problem 13, anomaly 1 |

## 7. Blind audit sample

60 codings, `derived/entry/audit_sample.json` (with coded state) and `derived/entry/audit_packets/<key>.json` (key, DOI, title, text paths only). By state: problem 36, external_goal 4, anomaly 4, hypothesis 4, data_without_theory 4, challenged_result 4, capability 4. By round: calc1 60. With PDF 60, with XML text 32. Sampled with numpy default_rng(2026): problem 36, the other states spread round robin (all of a state when it has fewer), audit order shuffled.

## 8. Blind audit (two blind re-codings of the entry, 60 sampled papers)

Source `private/data/roadmap/derived/entry/blind_audit.json`: coders A and B are Claude agents of the same model family as the batch coder, blind to the batch coding and to each other. They are not independent of the batch coder. Each gave state, node, evidence quote, whether the quote is a rhetorical gap sentence, the operational start (what started the work) with a quote, and a problem subtype. The sample is stratified (problem 36, four of each other state), so whole-sample shares are also given weighted back to the population (weight = papers with that batch state / sampled papers with it).

| Field | Pair | n | Agreement | Chance (pooled) | Krippendorff alpha [95% bootstrap] | Weighted agreement |
|:--|:--|--:|--:|--:|--:|--:|
| state | A vs B | 60 | 0.85 | 0.226 | 0.806 [0.675, 0.915] | 0.836 |
| state | A vs batch | 60 | 0.767 | 0.295 | 0.669 [0.5, 0.819] | 0.73 |
| state | B vs batch | 60 | 0.717 | 0.288 | 0.602 [0.427, 0.76] | 0.696 |
| state | consensus vs batch | 51 | 0.784 | 0.281 | 0.7 [0.521, 0.844] |  |
| node | A vs B | 60 | 0.833 | 0.261 | 0.775 [0.636, 0.889] | 0.862 |
| node | A vs batch | 60 | 0.683 | 0.358 | 0.507 [0.291, 0.68] | 0.654 |
| node | B vs batch | 60 | 0.617 | 0.366 | 0.395 [0.189, 0.571] | 0.613 |
| node | consensus vs batch | 50 | 0.68 | 0.365 | 0.496 [0.276, 0.686] |  |
| rhetorical gap | A vs B | 60 | 0.9 | 0.541 | 0.782 [0.596, 0.929] | |
| operational start (9 classes) | A vs B | 60 | 0.833 | 0.128 | 0.809 [0.692, 0.905] | |
| operational start (4 groups) | A vs B | 60 | 0.9 | 0.534 | 0.785 [0.619, 0.931] | |
| problem subtype group | A vs B | 21 | 0.857 | 0.195 | 0.823  | |

Three-way alpha (A, B, batch): state 0.696, node 0.573. All three give the same state in 40 of 60 papers.

Confusion, rows batch state, columns A/B consensus (split = A and B differ):

| | problem | capability | anomaly | challenged_result | hypothesis | data_without_theory | external_goal | split |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| problem | 20 | 5 | 1 | 0 | 0 | 3 | 0 | 7 |
| capability | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| anomaly | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| challenged_result | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| hypothesis | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 2 |
| data_without_theory | 0 | 0 | 1 | 0 | 0 | 3 | 0 | 0 |
| external_goal | 1 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |

| Batch state | n | A confirms | B confirms | Both confirm [Wilson 95%] | Neither | Consensus on another state | Split |
|:--|--:|--:|--:|--:|--:|:--|--:|
| problem | 36 | 24 | 23 | 20 (56%) [0.396, 0.705] | 9 | capability 5, data_without_theory 3, anomaly 1 | 7 |
| capability | 4 | 4 | 4 | 4 (100%) [0.51, 1.0] | 0 |  | 0 |
| anomaly | 4 | 4 | 4 | 4 (100%) [0.51, 1.0] | 0 |  | 0 |
| challenged_result | 4 | 4 | 4 | 4 (100%) [0.51, 1.0] | 0 |  | 0 |
| hypothesis | 4 | 4 | 2 | 2 (50%) [0.15, 0.85] | 0 |  | 2 |
| data_without_theory | 4 | 3 | 3 | 3 (75%) [0.301, 0.954] | 1 | anomaly 1 | 0 |
| external_goal | 4 | 3 | 3 | 3 (75%) [0.301, 0.954] | 1 | problem 1 | 0 |

Population estimate of the entry-state distribution (weighted, stratified bootstrap 95%):

| State | Batch | A | B | Consensus |
|:--|--:|--:|--:|--:|
| problem | 78% [0.777, 0.777] | 52% [0.399, 0.637] | 50% [0.367, 0.626] | 44% [0.307, 0.566] |
| capability | 11% [0.107, 0.107] | 24% [0.15, 0.345] | 24% [0.15, 0.345] | 22% [0.129, 0.302] |
| challenged_result | 3% [0.026, 0.026] | 3% [0.026, 0.026] | 3% [0.026, 0.045] | 3% [0.026, 0.026] |
| hypothesis | 3% [0.026, 0.026] | 5% [0.026, 0.09] | 6% [0.006, 0.121] | 1% [0.0, 0.026] |
| anomaly | 2% [0.021, 0.021] | 7% [0.021, 0.135] | 5% [0.021, 0.097] | 5% [0.021, 0.097] |
| data_without_theory | 2% [0.021, 0.021] | 8% [0.016, 0.162] | 10% [0.032, 0.194] | 8% [0.016, 0.162] |
| external_goal | 2% [0.021, 0.021] | 2% [0.005, 0.021] | 2% [0.011, 0.035] | 2% [0.005, 0.021] |
| split |  |  |  | 16% [0.071, 0.265] |

Population estimate of the operational-start group: consensus concrete object 62% [0.486, 0.749], split 19% [0.082, 0.307], prior result 10% [0.032, 0.177], literature gap only 6% [0.0, 0.151], stated hypothesis 3% [0.0, 0.078]; coder A alone concrete object 72% [0.595, 0.838], literature gap only 15% [0.065, 0.259], prior result 10% [0.032, 0.175], stated hypothesis 3% [0.0, 0.078].

Blind quote overlaps the batch quote: A 35/60 (58%), B 31/60 (52%); for batch `problem` A 20/36 (56%), B 15/36 (42%). A and B quote overlapping sentences in 37/60 (62%).

Rhetorical gap quotes (Swales move 2), by batch state:

| Batch state | n | A flags gap | B flags gap | Both | Batch quote has regex gap marker | Batch quote overlaps a coder quote | of those, flagged gap |
|:--|--:|--:|--:|--:|--:|--:|--:|
| problem | 36 | 21 | 21 | 18 | 24 | 22 | 18 |
| capability | 4 | 0 | 0 | 0 | 0 | 4 | 0 |
| anomaly | 4 | 0 | 0 | 0 | 1 | 4 | 0 |
| challenged_result | 4 | 0 | 0 | 0 | 2 | 2 | 0 |
| hypothesis | 4 | 0 | 0 | 0 | 0 | 4 | 0 |
| data_without_theory | 4 | 0 | 0 | 0 | 0 | 2 | 0 |
| external_goal | 4 | 0 | 0 | 0 | 1 | 3 | 0 |

By the coder's own state: A problem 21/25 (84%), capability 0/10 (0%), anomaly 0/7 (0%), challenged_result 0/4 (0%), hypothesis 0/5 (0%), data_without_theory 0/6 (0%), external_goal 0/3 (0%); B problem 21/24 (88%), capability 0/10 (0%), anomaly 0/6 (0%), challenged_result 0/5 (0%), hypothesis 0/4 (0%), data_without_theory 0/7 (0%), external_goal 0/4 (0%). Both flag gap, by consensus state: problem 18/21, capability 0/9, anomaly 0/6, challenged_result 0/4, hypothesis 0/2, data_without_theory 0/6, external_goal 0/3.
g21 regex gap marker against the coders' flag on their own quotes (120 quotes): both 32, regex only 7, flag only 10, neither 71 (agreement 0.858).

Operational start (what started the work), A and B agreed (split = they differ):

| Batch state | n | Agreed operational start |
|:--|--:|:--|
| problem | 36 | data_in_hand 8, split 7, new_method_or_model 7, new_instrument_or_deployment 3, prior_result_to_test 3, literature_gap_only 3, mandate_or_project_goal 2, stated_hypothesis 1, surprising_observation 1, event_occurred 1 |
| capability | 4 | new_method_or_model 2, split 1, event_occurred 1 |
| anomaly | 4 | surprising_observation 4 |
| challenged_result | 4 | prior_result_to_test 4 |
| hypothesis | 4 | mandate_or_project_goal 1, prior_result_to_test 1, split 1, stated_hypothesis 1 |
| data_without_theory | 4 | data_in_hand 2, surprising_observation 1, split 1 |
| external_goal | 4 | mandate_or_project_goal 2, event_occurred 1, new_method_or_model 1 |

Batch `problem` (36 papers): literature gap only, agreed 3/36 (8%) (Wilson [0.029, 0.218]), named by either coder 7/36 (19%); a concrete object (data in hand, event, instrument or deployment, method or model, mandate, surprising observation) agreed 22/36 (61%), both coders 23/36 (64%); prior result to test agreed 3/36 (8%). Groups: concrete object 22, split 7, prior result 3, literature gap only 3, stated hypothesis 1.
Consensus `problem`, both quotes gap statements, and an agreed concrete start: 8/36 (22%).
Agreed operational start by A/B consensus state, within batch `problem`: anomaly: data_in_hand 1; capability: new_method_or_model 3, split 1, new_instrument_or_deployment 1; data_without_theory: data_in_hand 3; problem: split 5, new_method_or_model 3, data_in_hand 3, literature_gap_only 3, prior_result_to_test 2, mandate_or_project_goal 2, new_instrument_or_deployment 1, event_occurred 1; split: split 1, stated_hypothesis 1, new_method_or_model 1, surprising_observation 1, data_in_hand 1, prior_result_to_test 1, new_instrument_or_deployment 1.

State implied by the agreed operational start (`START_TO_STATE`) equals the consensus state in 26 of 42 papers where both are agreed: problem 3/16 (19%), capability 6/7 (86%), anomaly 5/6 (83%), challenged_result 4/4 (100%), hypothesis 1/1 (100%), data_without_theory 5/5 (100%), external_goal 2/3 (67%).

Problem subtypes (free text grouped by `SUBTYPE_GROUPS`): A process or mechanism unknown 10, quantity or effect unconstrained 5, method or instrument limitation 4, applied need (hazard, management) 2, theory incomplete 1, debated history or timing 1, trend attribution 1, data gap 1; B process or mechanism unknown 10, method or instrument limitation 5, quantity or effect unconstrained 3, data gap 2, theory incomplete 1, applied need (hazard, management) 1, debated history or timing 1, trend attribution 1; agreed on the 21 papers both call problem: process or mechanism unknown 7, quantity or effect unconstrained 3, split 3, method or instrument limitation 3, theory incomplete 1, applied need (hazard, management) 1, debated history or timing 1, trend attribution 1, data gap 1.

Papers where A, B and batch do not all agree on the state (20):

| Key | Batch | A | B | A start | B start |
|:--|:--|:--|:--|:--|:--|

