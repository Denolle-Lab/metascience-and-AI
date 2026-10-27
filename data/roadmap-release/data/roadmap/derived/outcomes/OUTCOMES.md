# Workflow features against outcome metrics

233 papers coded under codebook 1.5.0 (first calculation). 245 feature-outcome tests; 15 with Benjamini-Hochberg q < 0.1. Exploratory: one model coder, open-access-leaning sample, citations at about four years. Advance is not measured yet.

## Outcomes

| Outcome | Papers | Median |
|:--|--:|--:|
| impact: citation percentile | 233 | 0.546 |
| impact: field-weighted citations | 233 | 0.482 |
| novelty: rare topic pair | 233 | -3.821 |
| breadth: references outside geoscience | 233 | 0.033 |
| breadth: citers outside geoscience (>=10 citers) | 53 | 0.0 |

Rank correlations among outcomes: cnp~fwci 0.988; cnp~novelty_pair 0.075; cnp~breadth_refs -0.067; cnp~breadth_citers -0.066; fwci~novelty_pair 0.046; fwci~breadth_refs -0.081; fwci~breadth_citers -0.116; novelty_pair~breadth_refs 0.103; novelty_pair~breadth_citers 0.089; breadth_refs~breadth_citers 0.304

## Associations with q < 0.1

| Feature | Outcome | rho [95% CI] | n | q | Share of papers |
|:--|:--|:--|--:|--:|--:|
| import fields | breadth: references outside geoscience | 0.512 [0.406, 0.611] | 233 | 0.025 | numeric |
| imports | breadth: references outside geoscience | 0.566 [0.463, 0.658] | 233 | 0.025 | numeric |
| composition capability_first | breadth: references outside geoscience | 0.217 [0.083, 0.347] | 233 | 0.027 | 0.13 |
| decisive methods | breadth: references outside geoscience | 0.223 [0.088, 0.356] | 233 | 0.027 | 0.29 |
| decisive simulation | impact: field-weighted citations | 0.211 [0.078, 0.33] | 233 | 0.027 | 0.11 |
| distinct modes | breadth: references outside geoscience | -0.224 [-0.342, -0.104] | 233 | 0.027 | numeric |
| revisits | impact: citation percentile | 0.211 [0.086, 0.335] | 233 | 0.027 | numeric |
| revisits | impact: field-weighted citations | 0.217 [0.078, 0.336] | 233 | 0.027 | numeric |
| steps | impact: field-weighted citations | 0.23 [0.107, 0.349] | 233 | 0.027 | numeric |
| steps | impact: citation percentile | 0.227 [0.085, 0.351] | 233 | 0.034 | numeric |
| mode synthesis | breadth: references outside geoscience | -0.222 [-0.349, -0.091] | 233 | 0.04 | 0.7 |
| decisive simulation | impact: citation percentile | 0.202 [0.074, 0.32] | 233 | 0.041 | 0.11 |
| mode observation | novelty: rare topic pair | 0.207 [0.076, 0.334] | 233 | 0.045 | 0.78 |
| V check kinds | breadth: references outside geoscience | 0.201 [0.076, 0.328] | 233 | 0.045 | numeric |
| node I infer | breadth: references outside geoscience | -0.181 [-0.306, -0.049] | 233 | 0.085 | 0.82 |

## Strongest association per outcome (any q)

| Outcome | Feature | rho [95% CI] | q |
|:--|:--|:--|--:|
| impact: citation percentile | steps | 0.227 [0.085, 0.351] | 0.034 |
| impact: citation percentile | revisits | 0.211 [0.086, 0.335] | 0.027 |
| impact: citation percentile | decisive simulation | 0.202 [0.074, 0.32] | 0.041 |
| impact: citation percentile | novelty claims | 0.147 [0.003, 0.282] | 0.248 |
| impact: citation percentile | mode instruments | 0.132 [0.01, 0.261] | 0.295 |
| impact: field-weighted citations | steps | 0.23 [0.107, 0.349] | 0.027 |
| impact: field-weighted citations | revisits | 0.217 [0.078, 0.336] | 0.027 |
| impact: field-weighted citations | decisive simulation | 0.211 [0.078, 0.33] | 0.027 |
| impact: field-weighted citations | distinct modes | 0.143 [0.011, 0.268] | 0.248 |
| impact: field-weighted citations | mode instruments | 0.138 [0.013, 0.268] | 0.249 |
| novelty: rare topic pair | mode observation | 0.207 [0.076, 0.334] | 0.045 |
| novelty: rare topic pair | mode simulation | -0.131 [-0.259, 0.0] | 0.295 |
| novelty: rare topic pair | composition capability_first | 0.129 [-0.017, 0.268] | 0.295 |
| novelty: rare topic pair | imports | 0.114 [-0.012, 0.241] | 0.385 |
| novelty: rare topic pair | returns after failure | 0.095 [-0.031, 0.215] | 0.46 |
| breadth: references outside geoscience | imports | 0.566 [0.463, 0.658] | 0.025 |
| breadth: references outside geoscience | import fields | 0.512 [0.406, 0.611] | 0.025 |
| breadth: references outside geoscience | distinct modes | -0.224 [-0.342, -0.104] | 0.027 |
| breadth: references outside geoscience | decisive methods | 0.223 [0.088, 0.356] | 0.027 |
| breadth: references outside geoscience | mode synthesis | -0.222 [-0.349, -0.091] | 0.04 |
| breadth: citers outside geoscience (>=10 citers) | claim gate yes | 0.37 [0.105, 0.592] | 0.107 |
| breadth: citers outside geoscience (>=10 citers) | decisive estimation | -0.338 [-0.53, -0.128] | 0.183 |
| breadth: citers outside geoscience (>=10 citers) | mode reconstruction | -0.329 [-0.539, -0.076] | 0.187 |
| breadth: citers outside geoscience (>=10 citers) | node X exclude | -0.324 [-0.575, -0.036] | 0.194 |
| breadth: citers outside geoscience (>=10 citers) | steps | -0.317 [-0.562, -0.024] | 0.225 |
