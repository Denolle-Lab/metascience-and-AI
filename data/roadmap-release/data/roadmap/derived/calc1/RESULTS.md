# First calculation: results

Codings: round 1 374 of 525 eligible papers (first coding; 233 in the first analysis, 141 top-up); round 2 198 of 222 eligible; 50 round-1 gold papers coded twice. Codebook 1.5.0, model coder. Valid = passes tools/check_coding.py validate().

## Test-retest (two independent model codings, round 1 gold papers)

| Measure | Value |
|:--|:--|
| papers | 50 |
| entry_state_agree | 0.92 |
| entry_node_agree | 0.9 |
| outcome_agree | 1.0 |
| decisive_mode_agree | 0.86 |
| node_set_jaccard_mean | 0.86 |
| mode_set_jaccard_mean | 0.81 |
| node_seq_similarity_mean | 0.69 |
| mode_seq_similarity_mean | 0.64 |
| alpha entry_state | 0.768 |
| alpha outcome | 1.0 |
| alpha claim_status | 0.755 |
| alpha decisive_mode | 0.83 |
| alpha composition | 0.596 |
| alpha v_status | 1.0 |
| alpha node_presence | 0.743 |
| gate node_set_jaccard>=0.7 | True |
| gate entry_and_outcome>=0.8 | True |

## Corpus descriptives by round (shares of valid codings)

| entry_state | round 1 first analysis (233) | round 1 all (374) | round 2 (198) | pooled (572) |
|:--|--:|--:|--:|--:|
| problem | 0.78 | 0.79 | 0.7 | 0.76 |
| capability | 0.11 | 0.09 | 0.11 | 0.09 |
| challenged_result | 0.03 | 0.02 | 0.04 | 0.03 |
| hypothesis | 0.03 | 0.03 | 0.06 | 0.04 |
| data_without_theory | 0.02 | 0.03 | 0.02 | 0.02 |
| anomaly | 0.02 | 0.03 | 0.08 | 0.05 |
| external_goal | 0.02 | 0.02 | 0.01 | 0.01 |

| entry_node | round 1 first analysis (233) | round 1 all (374) | round 2 (198) | pooled (572) |
|:--|--:|--:|--:|--:|
| Q | 0.81 | 0.82 | 0.71 | 0.78 |
| N | 0.12 | 0.1 | 0.12 | 0.11 |
| O | 0.04 | 0.05 | 0.08 | 0.06 |
| H | 0.03 | 0.03 | 0.08 | 0.05 |
| F | 0.0 | 0.01 | 0.01 | 0.01 |
| S | 0 | 0 | 0.01 | 0.0 |
| E | 0 | 0 | 0.01 | 0.0 |

| outcome | round 1 first analysis (233) | round 1 all (374) | round 2 (198) | pooled (572) |
|:--|--:|--:|--:|--:|
| kept | 0.97 | 0.97 | 0.99 | 0.98 |
| contradicted | 0.03 | 0.02 | 0.01 | 0.02 |
| excluded | 0 | 0.01 | 0 | 0.0 |

| claim_status | round 1 first analysis (233) | round 1 all (374) | round 2 (198) | pooled (572) |
|:--|--:|--:|--:|--:|
| capability_characterized | 0.33 | 0.3 | 0.27 | 0.29 |
| best_explanation | 0.31 | 0.37 | 0.41 | 0.38 |
| estimate_with_resolution | 0.21 | 0.19 | 0.19 | 0.19 |
| regularity_in_range | 0.12 | 0.12 | 0.11 | 0.12 |
| confirmed | 0.03 | 0.03 | 0.03 | 0.03 |

| composition | round 1 first analysis (233) | round 1 all (374) | round 2 (198) | pooled (572) |
|:--|--:|--:|--:|--:|
| none_fits | 0.51 | 0.47 | 0.41 | 0.45 |
| trace_series | 0.24 | 0.29 | 0.28 | 0.28 |
| capability_first | 0.13 | 0.11 | 0.14 | 0.12 |
| natures_repetition | 0.09 | 0.11 | 0.11 | 0.11 |
| independent_replication | 0.02 | 0.01 | 0.03 | 0.02 |
| strong_inference | 0.01 | 0.01 | 0.02 | 0.02 |
| exploration_first | 0.0 | 0.0 | 0.01 | 0.0 |

| decisive_mode | round 1 first analysis (233) | round 1 all (374) | round 2 (198) | pooled (572) |
|:--|--:|--:|--:|--:|
| methods | 0.29 | 0.24 | 0.17 | 0.22 |
| estimation | 0.22 | 0.23 | 0.29 | 0.25 |
| simulation | 0.11 | 0.11 | 0.17 | 0.13 |
| reconstruction | 0.11 | 0.11 | 0.07 | 0.09 |
| observation | 0.08 | 0.09 | 0.1 | 0.09 |
| hypothesis | 0.06 | 0.07 | 0.07 | 0.07 |
| regularities | 0.04 | 0.05 | 0.03 | 0.04 |
| theory | 0.03 | 0.03 | 0.03 | 0.03 |
| instruments | 0.03 | 0.02 | 0.04 | 0.03 |
| exploration | 0.02 | 0.03 | 0.02 | 0.02 |
| synthesis | 0.01 | 0.02 | 0.03 | 0.02 |
| robustness | 0.0 | 0.01 | 0.01 | 0.01 |

| mode of inquiry used (share of papers) | round 1 first analysis (233) | round 1 all (374) | round 2 (198) | pooled (572) |
|:--|--:|--:|--:|--:|
| estimation | 0.75 | 0.77 | 0.78 | 0.78 |
| exploration | 0.12 | 0.14 | 0.19 | 0.15 |
| hypothesis | 0.67 | 0.72 | 0.81 | 0.75 |
| instruments | 0.33 | 0.31 | 0.32 | 0.31 |
| methods | 0.75 | 0.74 | 0.75 | 0.74 |
| observation | 0.78 | 0.8 | 0.8 | 0.8 |
| question | 0.98 | 0.97 | 0.97 | 0.97 |
| reconstruction | 0.28 | 0.28 | 0.24 | 0.27 |
| regularities | 0.29 | 0.32 | 0.34 | 0.33 |
| robustness | 0.41 | 0.39 | 0.36 | 0.38 |
| simulation | 0.49 | 0.49 | 0.51 | 0.49 |
| synthesis | 0.7 | 0.72 | 0.7 | 0.71 |
| theory | 0.41 | 0.48 | 0.48 | 0.48 |

| Count | round 1 first analysis (233) | round 1 all (374) | round 2 (198) | pooled (572) |
|:--|--:|--:|--:|--:|
| steps_median | 20 | 20.0 | 20.0 | 20.0 |
| mode_returns_median | 9 | 9.0 | 9.0 | 9.0 |
| papers_with_return_after_failure | 0.31 | 0.3 | 0.3 | 0.3 |
| textbook_route_in_order | 0.0 | 0.01 | 0.02 | 0.01 |
| papers_with_D_design | 0.7 | 0.65 | 0.71 | 0.67 |
| triangulation | 0.33 | 0.37 | 0.39 | 0.37 |
| gates_claim_yes | 0.17 | 0.15 | 0.15 | 0.15 |
| gates_action_yes | 0.03 | 0.03 | 0.02 | 0.03 |

## Round 1 against round 2 (descriptive)

| Variable | n | Cramer V (bias-corrected) or epsilon^2 [95% CI] | permutation p | BH q |
|:--|--:|:--|--:|--:|
| entry_state | 572 | V 0.124 [0.051, 0.241] | 0.0186 | 0.065 |
| entry_node | 572 | V 0.117 [0.0, 0.231] | 0.0154 | 0.065 |
| outcome | 572 | V 0.027 [0.0, 0.101] | 0.3155 | 0.552 |
| claim_status | 572 | V 0.0 [0.0, 0.13] | 0.8766 | 0.877 |
| composition | 572 | V 0.0 [0.0, 0.169] | 0.4431 | 0.62 |
| decisive_mode | 572 | V 0.062 [0.0, 0.233] | 0.2875 | 0.552 |
| steps | 572 | eps2 0.0 [0.0, 0.011] | 0.7944 | 0.877 |

## Round 1 corpus (json)

```
{
 "papers_coded": 374,
 "eligible": 525,
 "coverage": 0.71,
 "entry_state": {
  "problem": [
   296,
   0.79
  ],
  "capability": [
   33,
   0.09
  ],
  "anomaly": [
   11,
   0.03
  ],
  "hypothesis": [
   10,
   0.03
  ],
  "data_without_theory": [
   10,
   0.03
  ],
  "challenged_result": [
   8,
   0.02
  ],
  "external_goal": [
   6,
   0.02
  ]
 },
 "entry_node": {
  "Q": [
   305,
   0.82
  ],
  "N": [
   38,
   0.1
  ],
  "O": [
   17,
   0.05
  ],
  "H": [
   12,
   0.03
  ],
  "F": [
   2,
   0.01
  ]
 },
 "outcome": {
  "kept": [
   363,
   0.97
  ],
  "contradicted": [
   9,
   0.02
  ],
  "excluded": [
   2,
   0.01
  ]
 },
 "claim_status": {
  "best_explanation": [
   137,
   0.37
  ],
  "capability_characterized": [
   111,
   0.3
  ],
  "estimate_with_resolution": [
   70,
   0.19
  ],
  "regularity_in_range": [
   45,
   0.12
  ],
  "confirmed": [
   11,
   0.03
  ]
 },
 "composition": {
  "none_fits": [
   174,
   0.47
  ],
  "trace_series": [
   107,
   0.29
  ],
  "capability_first": [
   42,
   0.11
  ],
  "natures_repetition": [
   41,
   0.11
  ],
  "strong_inference": [
   5,
   0.01
  ],
  "independent_replication": [
   4,
   0.01
  ],
  "exploration_first": [
   1,
   0.0
  ]
 },
 "decisive_mode": {
  "methods": [
   89,
   0.24
  ],
  "estimation": [
   87,
   0.23
  ],
  "simulation": [
   42,
   0.11
  ],
  "reconstruction": [
   40,
   0.11
  ],
  "observation": [
   33,
   0.09
  ],
  "hypothesis": [
   28,
   0.07
  ],
  "regularities": [
   17,
   0.05
  ],
  "theory": [
   11,
   0.03
  ],
  "exploration": [
   10,
   0.03
  ],
  "instruments": [
   8,
   0.02
  ],
  "synthesis": [
   6,
   0.02
  ],
  "robustness": [
   3,
   0.01
  ]
 },
 "mode_used_share": {
  "estimation": 0.77,
  "exploration": 0.14,
  "hypothesis": 0.72,
  "instruments": 0.31,
  "methods": 0.74,
  "observation": 0.8,
  "question": 0.97,
  "reconstruction": 0.28,
  "regularities": 0.32,
  "robustness": 0.39,
  "simulation": 0.49,
  "synthesis": 0.72,
  "theory": 0.48
 },
 "node_used_share": {
  "N": 0.54,
  "E": 0.18,
  "O": 0.93,
  "I": 0.84,
  "Q": 0.98,
  "H": 0.84,
  "S": 0.66,
  "D": 0.65,
  "F": 0.41,
  "C": 0.99,
  "V": 0.98,
  "X": 0.51,
  "K": 1.0,
  "P": 0.32,
  "R": 0.55
 },
 "steps_median": 20.0,
 "mode_returns_median": 9.0,
 "papers_with_return_after_failure": 0.3,
 "textbook_route_in_order": 0.01,
 "papers_with_D_design": 0.65,
 "v": {
  "full": [
   365,
   0.98
  ],
  "none": [
   9,
   0.02
  ]
 },
 "triangulation": 0.37,
 "v_kinds_performed": {
  "control": [
   324,
   0.87
  ],
  "robustness": [
   238,
   0.64
  ],
  "replication": [
   205,
   0.55
  ],
  "method": [
   193,
   0.52
  ],
  "generalization": [
   74,
   0.2
  ],
  "reproduction": [
   35,
   0.09
  ]
 },
 "gates_claim_yes": 0.15,
 "gates_action_yes": 0.03
}
```

## Access bias, round 1

```
{
 "coded": {
  "n": 374,
  "impact_cnp_median": 0.563,
  "novelty_median": -3.847,
  "breadth_refs_median": 0.028,
  "open_access_share": 0.82
 },
 "not_coded": {
  "n": 151,
  "impact_cnp_median": 0.366,
  "novelty_median": -3.886,
  "breadth_refs_median": 0.048,
  "open_access_share": 0.15
 }
}
```

## By impact quintile, round 1

```
{
 "1": {
  "n": 57,
  "capability_entry": 0.11,
  "v_full": 0.93,
  "steps_median": 18,
  "modes_median": 7
 },
 "2": {
  "n": 72,
  "capability_entry": 0.11,
  "v_full": 0.99,
  "steps_median": 21.0,
  "modes_median": 7.0
 },
 "3": {
  "n": 81,
  "capability_entry": 0.07,
  "v_full": 0.98,
  "steps_median": 20,
  "modes_median": 7
 },
 "4": {
  "n": 82,
  "capability_entry": 0.1,
  "v_full": 0.98,
  "steps_median": 21.0,
  "modes_median": 7.0
 },
 "5": {
  "n": 82,
  "capability_entry": 0.06,
  "v_full": 1.0,
  "steps_median": 21.0,
  "modes_median": 8.0
 }
}
```

## Access bias, round 2

```
{
 "coded": {
  "n": 198,
  "impact_cnp_median": 0.554,
  "novelty_median": -3.846,
  "breadth_refs_median": 0.038,
  "open_access_share": 1.0
 },
 "not_coded": {
  "n": 24,
  "impact_cnp_median": 0.512,
  "novelty_median": -3.745,
  "breadth_refs_median": 0.015,
  "open_access_share": 1.0
 }
}
```

## By impact quintile, round 2

```
{
 "1": {
  "n": 29,
  "capability_entry": 0.1,
  "v_full": 0.97,
  "steps_median": 19,
  "modes_median": 7
 },
 "2": {
  "n": 43,
  "capability_entry": 0.16,
  "v_full": 0.95,
  "steps_median": 21,
  "modes_median": 7
 },
 "3": {
  "n": 42,
  "capability_entry": 0.07,
  "v_full": 0.95,
  "steps_median": 20.5,
  "modes_median": 7.0
 },
 "4": {
  "n": 40,
  "capability_entry": 0.12,
  "v_full": 0.97,
  "steps_median": 21.0,
  "modes_median": 7.5
 },
 "5": {
  "n": 44,
  "capability_entry": 0.07,
  "v_full": 0.98,
  "steps_median": 19.0,
  "modes_median": 7.0
 }
}
```
