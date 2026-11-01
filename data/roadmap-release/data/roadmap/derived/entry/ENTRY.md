# Entry state: catch-all check

Script `tools/roadmap/g21_entry_state.py`; data `private/data/roadmap/derived/entry/entry_state.json`. Valid codings read at run time: calc1 374, r2 198 (tools/check_coding.py validate()). Invalid files skipped: calc1 5, r2 4, gold-r2 1. One model coder (Claude, codebook 1.5.0). Definitions of every measure are in the script docstring.

**Question.** Does `problem` record what started the work, or the gap statement every introduction carries (Swales 1990, "create a research space")? The codings alone cannot settle it; they can show whether the label behaves like a default. The blind audit sample at the end is for the direct check.

## Headline

- `problem` is 76% of 572 valid codings; Q is 78% of entry nodes.
- Test-retest on 50 gold papers: agreement 0.92, chance agreement 0.655 (one category holds most papers), so alpha 0.768 [0.504, 0.945]. The two runs quote an identical evidence string in 52% of papers and overlapping evidence (one quote contains the other, or token Jaccard at least 0.5) in 74%; same locator 88%. The label repeats somewhat more often than the supporting sentence.
- For 114 of 435 `problem` papers (26%) the coded walk does not start at Q: O 50, H 29, S 9, N 8, E 7, I 6, C 3, F 2. In 108 of them the first step is a cited or inherited result (move cited or inherited): the walk opens on prior work and the question follows. That prior result is a candidate for the real start (challenged_result or anomaly) and is one thing the audit should check.
- After entry, Q comes back in 20% of `problem` papers; no paper reframes its question after a failure (0 of 572): the 235 returns after failure land on P, R, V, I and other nodes, never on Q.
- `problem` evidence sits in the abstract or introduction in 95% of the 184 papers with a section, and on the first article page in 88% of the 255 with a page number. 50% of its quotes carry a gap marker and 39% carry a gap marker with no origin marker; for `capability` the figures are 6% and 4%.
- What the codings cannot show: whether a data set, event, instrument or mandate started a `problem` paper. That is the job of the blind audit sample (section 7).

## 1. Distribution

**calc1** (n = 374)

| Entry state | Papers | Share |
|:--|--:|--:|
| problem | 296 | 79% |
| capability | 33 | 9% |
| anomaly | 11 | 3% |
| hypothesis | 10 | 3% |
| data_without_theory | 10 | 3% |
| challenged_result | 8 | 2% |
| external_goal | 6 | 2% |

| Entry node | Papers | Share |
|:--|--:|--:|
| Q | 305 | 82% |
| N | 38 | 10% |
| O | 17 | 4% |
| H | 12 | 3% |
| F | 2 | 0% |

**r2** (n = 198)

| Entry state | Papers | Share |
|:--|--:|--:|
| problem | 139 | 70% |
| capability | 21 | 11% |
| anomaly | 15 | 8% |
| hypothesis | 12 | 6% |
| challenged_result | 7 | 4% |
| data_without_theory | 3 | 2% |
| external_goal | 1 | 0% |

| Entry node | Papers | Share |
|:--|--:|--:|
| Q | 140 | 71% |
| N | 24 | 12% |
| O | 16 | 8% |
| H | 15 | 8% |
| S | 1 | 0% |
| E | 1 | 0% |
| F | 1 | 0% |

**pooled** (n = 572)

| Entry state | Papers | Share |
|:--|--:|--:|
| problem | 435 | 76% |
| capability | 54 | 9% |
| anomaly | 26 | 4% |
| hypothesis | 22 | 4% |
| challenged_result | 15 | 3% |
| data_without_theory | 13 | 2% |
| external_goal | 7 | 1% |

| Entry node | Papers | Share |
|:--|--:|--:|
| Q | 445 | 78% |
| N | 62 | 11% |
| O | 33 | 6% |
| H | 27 | 5% |
| F | 3 | 0% |
| S | 1 | 0% |
| E | 1 | 0% |

Round 1 (calc1) against round 2 (r2), entry state (states under 10 papers merged): bias-corrected Cramer's V 0.124 [0.026, 0.243], permutation p 0.021. Problem against the rest: V 0.091, p 0.0168; problem share calc1 79%, r2 70%. The rounds were drawn differently (round 2 open access only, at most 4 papers per journal), so a difference mixes sampling and coding.

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

Entry node equals the node of the first step of the walk in 372 of 572 papers (65%); the entry node appears somewhere in the walk in 100%.

| Entry state | Expected node | At expected node | Entry nodes | First-step nodes |
|:--|:--|--:|:--|:--|
| problem | Q | 426/435 (98%) | N 7, E 1, O 1, Q 426 | Q 321, O 50, H 29, S 9, N 8, E 7, I 6, C 3, F 2 |
| capability | N | 52/54 (96%) | N 52, O 1, S 1 | N 23, Q 20, O 8, S 2, H 1 |
| anomaly | E,O | 20/26 (77%) | O 20, Q 5, F 1 | O 13, Q 5, S 3, H 1, I 1, E 1, N 1, F 1 |
| challenged_result | C,H,Q,V | 15/15 (100%) | Q 10, H 5 | Q 8, H 6, K 1 |
| hypothesis | H | 22/22 (100%) | H 22 | Q 11, O 5, H 4, K 1, I 1 |
| data_without_theory | E,O | 11/13 (85%) | O 11, F 2 | O 5, H 3, Q 3, F 1, S 1 |
| external_goal | D,N,Q | 7/7 (100%) | N 3, Q 4 | Q 3, N 2, H 2 |

First step (node and move) when it is not the entry node: problem: O cited 41, H cited 27, S cited 8, O inherited 7, Q new 6, E cited 6, I cited 4, N inherited 3, C cited 3, N cited 2, I inherited 2, O new 2, F new 2, S inherited 1, H inherited 1, H new 1, E inherited 1, N new 1; capability: Q new 20, O cited 7, S cited 2, H cited 1, O inherited 1; anomaly: Q new 4, O cited 3, S cited 3, H cited 1, O inherited 1, I new 1, E cited 1, N inherited 1; challenged_result: H cited 2, Q new 2, Q cited 1, H inherited 1, K cited 1, H new 1; hypothesis: Q new 11, O cited 3, O inherited 1, K cited 1, O new 1, I cited 1; data_without_theory: H cited 3, Q new 3, F new 1, S cited 1; external_goal: H cited 1, H new 1.

## 4. Revisits of the entry node

Revisited = the entry node comes back after at least one other node (run-collapsed walk). Reframe after failure = a `return_after_failure` step at Q, or one followed directly by Q.

| Entry state | n | Entry node in walk | Revisited | Any later step there (raw) | Q twice or more (collapsed) | Any return after failure | Reframe after failure |
|:--|--:|--:|--:|--:|--:|--:|--:|
| problem | 435 | 100% | 20% | 22% | 20% | 30% | 0% |
| capability | 54 | 98% | 70% | 78% | 11% | 37% | 0% |
| anomaly | 26 | 100% | 69% | 69% | 15% | 15% | 0% |
| challenged_result | 15 | 100% | 40% | 40% | 40% | 27% | 0% |
| hypothesis | 22 | 100% | 64% | 68% | 14% | 32% | 0% |
| data_without_theory | 13 | 100% | 85% | 85% | 0% | 15% | 0% |
| external_goal | 7 | 100% | 43% | 57% | 0% | 57% | 0% |
| all | 572 | 100% | 31% | 33% | 18% | 30% | 0% |

The same per round (the table above is both rounds pooled):

| Round | Entry state | n | Entry node first step | Revisited | Any later step there (raw) | Q twice or more (collapsed) | Any return after failure | Reframe after failure |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| calc1 | all | 374 | 70% | 32% | 34% | 20% | 30% | 0% |
| calc1 | problem | 296 |  | 23% | 24% | 22% | 29% | 0% |
| calc1 | capability | 33 |  | 76% | 85% | 6% | 46% | 0% |
| r2 | all | 198 | 56% | 30% | 32% | 16% | 30% | 0% |
| r2 | problem | 139 |  | 15% | 16% | 14% | 32% | 0% |
| r2 | capability | 21 |  | 62% | 67% | 19% | 24% | 0% |

By entry node rather than state: of the 445 papers that enter at Q, 91 (20%) have a later Q step and 87 (20%) return to Q after another node. Moves of those later Q steps: new 94, cited 3, repeat 2.

The 235 `return_after_failure` steps sit at P 86, R 78, I 22, N 16, V 13, H 6, C 3, D 3, S 3, O 2, F 2, X 1; the step after them is at C 56, V 41, I 35, K 25, O 14, H 13, S 11, X 10, R 8, P 5, N 5, D 5, F 3, E 3, end 1.

## 5. Where the entry evidence sits and how it is worded

Quote located in the XML text: {'None': 256, 'True': 256, 'False': 60} (True = found, False = XML present but quote not found, None = no XML text).

| Entry state | n | With section | Abstract | Introduction | Section 1, heading unknown | Later section | With page | Median page in article | Page 1 | Pages 1-2 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| problem | 435 | 184 | 36% | 58% | 0% | 5% | 255 | 1.0 | 88% | 98% |
| capability | 54 | 27 | 48% | 48% | 0% | 4% | 28 | 1.0 | 79% | 93% |
| anomaly | 26 | 16 | 25% | 50% | 0% | 25% | 11 | 2.0 | 46% | 82% |
| challenged_result | 15 | 4 | 0% | 75% | 0% | 25% | 11 | 1.0 | 82% | 100% |
| hypothesis | 22 | 13 | 23% | 54% | 0% | 23% | 9 | 2.0 | 44% | 78% |
| data_without_theory | 13 | 9 | 22% | 67% | 0% | 11% | 4 | 1.0 | 75% | 100% |
| external_goal | 7 | 5 | 20% | 80% | 0% | 0% | 2 | 1.0 | 100% | 100% |
| all | 572 | 258 | 35% | 57% | 0% | 8% | 320 | 1.0 | 84% | 96% |

Marker families (regular expressions in the script, `MARKERS`): gap = names a gap or difficulty; aim = states the paper's own aim; origin = points to a concrete starting object (event, dataset, instrument, mission, prior result).

| Entry state | n | Any gap marker | Any aim marker | Any origin marker | Gap without origin | Origin without gap |
|:--|--:|--:|--:|--:|--:|--:|
| problem | 435 | 50% | 6% | 20% | 39% | 9% |
| capability | 54 | 6% | 56% | 52% | 4% | 50% |
| anomaly | 26 | 19% | 4% | 35% | 15% | 31% |
| challenged_result | 15 | 20% | 20% | 40% | 20% | 40% |
| hypothesis | 22 | 4% | 32% | 14% | 0% | 9% |
| data_without_theory | 13 | 0% | 8% | 54% | 0% | 54% |
| external_goal | 7 | 43% | 14% | 29% | 14% | 0% |
| all | 572 | 40% | 12% | 25% | 31% | 16% |

Gap markers in `problem` evidence: however 73, unknown or unclear 51, remains unclear or unknown 35, need 25, challenge 20, lack 19, debated or controversial 19, poorly understood or constrained 15, few or limited studies 12, little or less is known 9, not well understood or constrained 6, gap 4, open question 3.

## 6. By OpenAlex subfield and journal family

**subfield** (groups under 10 papers pooled). Entry state (states under 10 pooled) by subfield: Cramer's V 0.155 (bias-corrected 0.101), permutation p 0.0068. Problem vs other: V 0.178, p 0.0178.

| subfield | n | problem | states |
|:--|--:|--:|:--|
| Geophysics | 206 | 75% | problem 154, capability 20, anomaly 13, hypothesis 9, data_without_theory 5, challenged_result 4, external_goal 1 |
| Atmospheric Science | 171 | 77% | problem 131, capability 15, anomaly 8, challenged_result 7, hypothesis 5, external_goal 4, data_without_theory 1 |
| Oceanography | 42 | 67% | problem 28, capability 6, data_without_theory 3, hypothesis 2, anomaly 2, external_goal 1 |
| Earth-Surface Processes | 40 | 82% | problem 33, anomaly 3, capability 2, hypothesis 2 |
| Geochemistry and Petrology | 37 | 84% | problem 31, data_without_theory 2, hypothesis 2, capability 1, challenged_result 1 |
| Water Science and Technology | 26 | 77% | problem 20, capability 3, challenged_result 2, hypothesis 1 |
| Artificial Intelligence | 25 | 80% | problem 20, capability 2, data_without_theory 2, challenged_result 1 |
| Geology | 19 | 90% | problem 17, hypothesis 1, external_goal 1 |
| pooled small groups | 6 | 17% | capability 5, problem 1 |

**family** (groups under 10 papers pooled). Entry state (states under 10 pooled) by family: Cramer's V 0.132 (bias-corrected 0.083), permutation p 0.0122. Problem vs other: V 0.148, p 0.0522.

| family | n | problem | states |
|:--|--:|--:|:--|
| AGU | 124 | 81% | problem 100, capability 12, anomaly 5, hypothesis 3, challenged_result 2, external_goal 1, data_without_theory 1 |
| EGU/Copernicus | 102 | 70% | problem 71, capability 16, external_goal 4, hypothesis 3, challenged_result 3, anomaly 3, data_without_theory 2 |
| Elsevier | 99 | 78% | problem 77, anomaly 6, hypothesis 5, capability 4, data_without_theory 4, challenged_result 2, external_goal 1 |
| Wiley non-AGU | 99 | 85% | problem 84, capability 7, challenged_result 5, hypothesis 2, data_without_theory 1 |
| Springer Nature (non-portfolio) | 94 | 67% | problem 63, capability 13, data_without_theory 5, anomaly 5, hypothesis 5, challenged_result 2, external_goal 1 |
| Nature portfolio | 36 | 75% | problem 27, anomaly 6, hypothesis 3 |
| pooled small groups | 18 | 72% | problem 13, capability 2, challenged_result 1, hypothesis 1, anomaly 1 |

## 7. Blind audit sample

60 codings, `derived/entry/audit_sample.json` (with coded state) and `derived/entry/audit_packets/<key>.json` (key, DOI, title, text paths only). By state: problem 36, external_goal 4, anomaly 4, hypothesis 4, data_without_theory 4, challenged_result 4, capability 4. By round: calc1 60. With PDF 60, with XML text 32. Sampled with numpy default_rng(2026): problem 36, the other states spread round robin (all of a state when it has fewer), audit order shuffled. Drawn from the valid codings at the time (problem 181, capability 25, anomaly 5, challenged_result 6, hypothesis 6, data_without_theory 5, external_goal 5); kept as drawn: the blind re-codings exist, so later codings do not redraw it, and the population weights of section 8 use these counts.

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

