# Papers against agent loops (233 papers, 31 agent systems)

Each cell is [estimate, 2.5%, 97.5%] from 2000 bootstrap resamples of papers or of agent systems. Agent shares average the two blind coders.

| Node | Papers | Agents |
|:--|:--|:--|
| N new capability | [0.58, 0.51, 0.64] | [0.06, 0.0, 0.16] |
| E explore | [0.15, 0.11, 0.2] | [0.05, 0.0, 0.13] |
| O observe | [0.92, 0.89, 0.95] | [0.69, 0.53, 0.84] |
| I infer a latent quantity | [0.82, 0.76, 0.86] | [0.05, 0.0, 0.13] |
| Q question | [0.98, 0.97, 1.0] | [0.1, 0.02, 0.19] |
| H hypothesize rivals | [0.81, 0.76, 0.86] | [0.06, 0.0, 0.16] |
| S simulate or derive | [0.64, 0.58, 0.7] | [0.1, 0.02, 0.21] |
| D design the test | [0.7, 0.64, 0.76] | [0.4, 0.24, 0.58] |
| F find or set conditions | [0.45, 0.38, 0.51] | [0.21, 0.1, 0.34] |
| C compare | [0.99, 0.98, 1.0] | [0.6, 0.44, 0.74] |
| V vary and replicate | [0.97, 0.94, 0.99] | [0.1, 0.0, 0.19] |
| X exclude a rival | [0.48, 0.42, 0.55] | [0.05, 0.0, 0.13] |
| K keep the claim | [1.0, 1.0, 1.0] | [0.32, 0.16, 0.48] |
| P protect | [0.34, 0.28, 0.4] | [0.0, 0.0, 0.0] |
| R refine | [0.56, 0.5, 0.63] | [0.68, 0.55, 0.81] |

| V | Papers full | Agents full |
|:--|:--|:--|
| controls_count_full | [0.97, 0.94, 0.99] | [0.1, 0.0, 0.19] |
| controls_count_partial | [0.94, 0.9, 0.97] | [0.05, 0.0, 0.13] |
| triangulation | [0.33, 0.27, 0.39] | [0.0, 0.0, 0.0] |

Distinct nodes per unit, median: papers [10, 10, 11], agents [3.5, 2.0, 4.5].

Researcher transitions in at least 10% of papers: 59; run by any agent: {'opus-b': 33, 'sonnet-c': 24}.

Most common researcher transitions no agent loop runs: VC (0.46), IV (0.46), VI (0.37), OV (0.33), CI (0.32), QN (0.26), VO (0.25), KC (0.19), NV (0.18), IO (0.17)
