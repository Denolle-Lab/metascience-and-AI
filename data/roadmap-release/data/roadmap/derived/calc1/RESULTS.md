# First calculation: results

Codings: 233 of 525 eligible papers (first coding); 50 gold papers coded twice. Codebook 1.5.0, model coder.

## Test-retest (two independent model codings)

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

## Corpus

```
{
 "papers_coded": 233,
 "eligible": 525,
 "coverage": 0.44,
 "entry_state": {
  "problem": [
   181,
   0.78
  ],
  "capability": [
   25,
   0.11
  ],
  "challenged_result": [
   6,
   0.03
  ],
  "hypothesis": [
   6,
   0.03
  ],
  "data_without_theory": [
   5,
   0.02
  ],
  "anomaly": [
   5,
   0.02
  ],
  "external_goal": [
   5,
   0.02
  ]
 },
 "entry_node": {
  "Q": [
   189,
   0.81
  ],
  "N": [
   27,
   0.12
  ],
  "O": [
   9,
   0.04
  ],
  "H": [
   7,
   0.03
  ],
  "F": [
   1,
   0.0
  ]
 },
 "outcome": {
  "kept": [
   226,
   0.97
  ],
  "contradicted": [
   7,
   0.03
  ]
 },
 "claim_status": {
  "capability_characterized": [
   78,
   0.33
  ],
  "best_explanation": [
   72,
   0.31
  ],
  "estimate_with_resolution": [
   48,
   0.21
  ],
  "regularity_in_range": [
   27,
   0.12
  ],
  "confirmed": [
   8,
   0.03
  ]
 },
 "composition": {
  "none_fits": [
   118,
   0.51
  ],
  "trace_series": [
   55,
   0.24
  ],
  "capability_first": [
   30,
   0.13
  ],
  "natures_repetition": [
   22,
   0.09
  ],
  "independent_replication": [
   4,
   0.02
  ],
  "strong_inference": [
   3,
   0.01
  ],
  "exploration_first": [
   1,
   0.0
  ]
 },
 "decisive_mode": {
  "methods": [
   68,
   0.29
  ],
  "estimation": [
   52,
   0.22
  ],
  "simulation": [
   26,
   0.11
  ],
  "reconstruction": [
   25,
   0.11
  ],
  "observation": [
   18,
   0.08
  ],
  "hypothesis": [
   14,
   0.06
  ],
  "regularities": [
   10,
   0.04
  ],
  "theory": [
   7,
   0.03
  ],
  "instruments": [
   6,
   0.03
  ],
  "exploration": [
   4,
   0.02
  ],
  "synthesis": [
   2,
   0.01
  ],
  "robustness": [
   1,
   0.0
  ]
 },
 "mode_used_share": {
  "estimation": 0.75,
  "exploration": 0.12,
  "hypothesis": 0.67,
  "instruments": 0.33,
  "methods": 0.75,
  "observation": 0.78,
  "question": 0.98,
  "reconstruction": 0.28,
  "regularities": 0.29,
  "robustness": 0.41,
  "simulation": 0.49,
  "synthesis": 0.7,
  "theory": 0.41
 },
 "node_used_share": {
  "N": 0.58,
  "E": 0.15,
  "O": 0.92,
  "I": 0.82,
  "Q": 0.98,
  "H": 0.81,
  "S": 0.64,
  "D": 0.7,
  "F": 0.45,
  "C": 0.99,
  "V": 0.97,
  "X": 0.48,
  "K": 1.0,
  "P": 0.34,
  "R": 0.56
 },
 "steps_median": 20,
 "mode_returns_median": 9,
 "papers_with_return_after_failure": 0.31,
 "textbook_route_in_order": 0.0,
 "papers_with_D_design": 0.7,
 "v": {
  "full": [
   225,
   0.97
  ],
  "none": [
   8,
   0.03
  ]
 },
 "triangulation": 0.33,
 "v_kinds_performed": {
  "control": [
   203,
   0.87
  ],
  "robustness": [
   148,
   0.64
  ],
  "replication": [
   119,
   0.51
  ],
  "method": [
   116,
   0.5
  ],
  "generalization": [
   51,
   0.22
  ],
  "reproduction": [
   21,
   0.09
  ]
 },
 "gates_claim_yes": 0.17,
 "gates_action_yes": 0.03
}
```

## Access bias

```
{
 "coded": {
  "n": 233,
  "impact_cnp_median": 0.546,
  "novelty_median": -3.821,
  "breadth_refs_median": 0.033,
  "open_access_share": 0.83
 },
 "not_coded": {
  "n": 292,
  "impact_cnp_median": 0.475,
  "novelty_median": -3.886,
  "breadth_refs_median": 0.03,
  "open_access_share": 0.46
 }
}
```

## By impact quintile

```
{
 "1": {
  "n": 39,
  "capability_entry": 0.15,
  "v_full": 0.9,
  "steps_median": 18,
  "modes_median": 6
 },
 "2": {
  "n": 43,
  "capability_entry": 0.12,
  "v_full": 1.0,
  "steps_median": 21,
  "modes_median": 7
 },
 "3": {
  "n": 58,
  "capability_entry": 0.1,
  "v_full": 0.97,
  "steps_median": 20.0,
  "modes_median": 7.0
 },
 "4": {
  "n": 50,
  "capability_entry": 0.08,
  "v_full": 0.96,
  "steps_median": 20.5,
  "modes_median": 7.0
 },
 "5": {
  "n": 43,
  "capability_entry": 0.09,
  "v_full": 1.0,
  "steps_median": 23,
  "modes_median": 8
 }
}
```
