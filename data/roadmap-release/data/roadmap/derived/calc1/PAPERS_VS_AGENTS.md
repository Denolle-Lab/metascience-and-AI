# Papers against agent loops (374 papers, 31 agent systems)

Each cell is [estimate, 2.5%, 97.5%] from 2000 bootstrap resamples of papers or of agent systems. Agent shares average the two blind coders.

| Node | Papers | Agents |
|:--|:--|:--|
| N new capability | [0.54, 0.49, 0.59] | [0.06, 0.0, 0.16] |
| E explore | [0.18, 0.14, 0.21] | [0.05, 0.0, 0.13] |
| O observe | [0.93, 0.9, 0.95] | [0.69, 0.53, 0.84] |
| I infer a latent quantity | [0.84, 0.8, 0.88] | [0.05, 0.0, 0.13] |
| Q question | [0.98, 0.97, 0.99] | [0.1, 0.02, 0.21] |
| H hypothesize rivals | [0.84, 0.8, 0.87] | [0.06, 0.0, 0.16] |
| S simulate or derive | [0.66, 0.61, 0.71] | [0.1, 0.02, 0.21] |
| D design the test | [0.65, 0.6, 0.7] | [0.4, 0.24, 0.56] |
| F find or set conditions | [0.41, 0.36, 0.46] | [0.21, 0.1, 0.32] |
| C compare | [0.99, 0.99, 1.0] | [0.6, 0.44, 0.74] |
| V vary and replicate | [0.98, 0.96, 0.99] | [0.1, 0.0, 0.23] |
| X exclude a rival | [0.51, 0.46, 0.56] | [0.05, 0.0, 0.13] |
| K keep the claim | [1.0, 1.0, 1.0] | [0.32, 0.18, 0.47] |
| P protect | [0.32, 0.28, 0.37] | [0.0, 0.0, 0.0] |
| R refine | [0.55, 0.49, 0.6] | [0.68, 0.53, 0.81] |

| V | Papers full | Agents full |
|:--|:--|:--|
| controls_count_full | [0.98, 0.96, 0.99] | [0.1, 0.0, 0.23] |
| controls_count_partial | [0.94, 0.91, 0.96] | [0.05, 0.0, 0.13] |
| triangulation | [0.37, 0.32, 0.42] | [0.0, 0.0, 0.0] |

Distinct nodes per unit, median: papers [10, 10, 11], agents [3.5, 2.0, 4.5].

Researcher transitions in at least 10% of papers: 55; run by any agent: {'opus-b': 31, 'sonnet-c': 23}.

Most common researcher transitions no agent loop runs: VC (0.48), IV (0.48), VI (0.37), OV (0.35), CI (0.32), VO (0.3), QN (0.21), KC (0.18), NV (0.17), IO (0.17)
