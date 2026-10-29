# Workflow features against outcome metrics

Round 1: 374 papers coded under codebook 1.5.0 (233 in the first analysis, 141 top-up). 274 feature-outcome tests; 38 with Benjamini-Hochberg q < 0.1. Exploratory: one model coder, open-access-leaning sample, citations at about four years. Advance is not measured yet. The confirmatory test of the 15 associations found at 233 papers is round 2 (g23_confirmatory.py); the pooled run below is descriptive.

## Outcomes, round 1

| Outcome | Papers | Median |
|:--|--:|--:|
| impact: citation percentile | 374 | 0.563 |
| impact: field-weighted citations | 374 | 0.57 |
| novelty: rare topic pair | 374 | -3.847 |
| breadth: references outside geoscience | 374 | 0.028 |
| breadth: citers outside geoscience (>=10 citers) | 97 | 0.0 |

Rank correlations among outcomes: cnp~fwci 0.991; cnp~novelty_pair 0.055; cnp~breadth_refs -0.077; cnp~breadth_citers 0.006; fwci~novelty_pair 0.033; fwci~breadth_refs -0.092; fwci~breadth_citers -0.021; novelty_pair~breadth_refs 0.203; novelty_pair~breadth_citers 0.095; breadth_refs~breadth_citers 0.313

## Associations with q < 0.1, round 1

| Feature | Outcome | rho [95% CI] | n | q | Share of papers |
|:--|:--|:--|--:|--:|--:|
| composition capability_first | breadth: references outside geoscience | 0.203 [0.097, 0.302] | 374 | 0.009 | 0.11 |
| composition trace_series | breadth: references outside geoscience | -0.203 [-0.293, -0.111] | 374 | 0.009 | 0.29 |
| decisive methods | breadth: references outside geoscience | 0.26 [0.157, 0.36] | 374 | 0.009 | 0.24 |
| import fields | breadth: references outside geoscience | 0.505 [0.422, 0.584] | 374 | 0.009 | numeric |
| imports | breadth: references outside geoscience | 0.547 [0.466, 0.616] | 374 | 0.009 | numeric |
| steps | impact: field-weighted citations | 0.178 [0.074, 0.276] | 374 | 0.009 | numeric |
| mode synthesis | breadth: references outside geoscience | -0.173 [-0.275, -0.07] | 374 | 0.014 | 0.72 |
| steps | impact: citation percentile | 0.174 [0.071, 0.276] | 374 | 0.014 | numeric |
| mode reconstruction | breadth: references outside geoscience | -0.174 [-0.264, -0.078] | 374 | 0.018 | 0.28 |
| node I infer | breadth: references outside geoscience | -0.177 [-0.28, -0.065] | 374 | 0.02 | 0.84 |
| revisits | impact: field-weighted citations | 0.171 [0.07, 0.274] | 374 | 0.02 | numeric |
| revisits | impact: citation percentile | 0.168 [0.07, 0.269] | 374 | 0.023 | numeric |
| novelty claims | impact: citation percentile | 0.163 [0.058, 0.263] | 374 | 0.025 | numeric |
| distinct modes | breadth: references outside geoscience | -0.159 [-0.262, -0.058] | 374 | 0.029 | numeric |
| imports | novelty: rare topic pair | 0.152 [0.05, 0.249] | 374 | 0.029 | numeric |
| decisive simulation | impact: field-weighted citations | 0.157 [0.065, 0.243] | 374 | 0.041 | 0.11 |
| mode reconstruction | breadth: citers outside geoscience (>=10 citers) | -0.303 [-0.464, -0.114] | 97 | 0.042 | 0.26 |
| node N new capability | breadth: references outside geoscience | 0.15 [0.054, 0.243] | 374 | 0.046 | 0.54 |
| V check kinds | breadth: references outside geoscience | 0.156 [0.051, 0.251] | 374 | 0.052 | numeric |
| decisive reconstruction | breadth: references outside geoscience | -0.145 [-0.226, -0.06] | 374 | 0.058 | 0.11 |
| distinct modes | impact: field-weighted citations | 0.143 [0.038, 0.246] | 374 | 0.06 | numeric |
| decisive simulation | impact: citation percentile | 0.149 [0.054, 0.235] | 374 | 0.062 | 0.11 |
| node H hypothesize | breadth: references outside geoscience | -0.139 [-0.24, -0.037] | 374 | 0.062 | 0.84 |
| novelty claims | impact: field-weighted citations | 0.147 [0.037, 0.247] | 374 | 0.064 | numeric |
| mode observation | novelty: rare topic pair | 0.145 [0.038, 0.248] | 374 | 0.068 | 0.8 |
| mode methods | breadth: citers outside geoscience (>=10 citers) | 0.278 [0.11, 0.423] | 97 | 0.071 | 0.79 |
| revisits | breadth: citers outside geoscience (>=10 citers) | -0.272 [-0.459, -0.071] | 97 | 0.071 | numeric |
| claim gate yes | breadth: citers outside geoscience (>=10 citers) | 0.263 [0.057, 0.431] | 97 | 0.072 | 0.12 |
| decisive methods | breadth: citers outside geoscience (>=10 citers) | 0.258 [0.046, 0.451] | 97 | 0.079 | 0.21 |
| import fields | novelty: rare topic pair | 0.132 [0.032, 0.233] | 374 | 0.083 | numeric |
| steps | breadth: citers outside geoscience (>=10 citers) | -0.263 [-0.451, -0.054] | 97 | 0.083 | numeric |
| mode reconstruction | novelty: rare topic pair | -0.135 [-0.232, -0.037] | 374 | 0.086 | 0.28 |
| mode methods | breadth: references outside geoscience | 0.133 [0.039, 0.231] | 374 | 0.087 | 0.74 |
| steps | breadth: references outside geoscience | -0.137 [-0.234, -0.033] | 374 | 0.087 | numeric |
| composition trace_series | novelty: rare topic pair | -0.135 [-0.234, -0.035] | 374 | 0.088 | 0.29 |
| distinct modes | impact: citation percentile | 0.13 [0.028, 0.237] | 374 | 0.088 | numeric |
| decisive estimation | breadth: references outside geoscience | -0.128 [-0.226, -0.032] | 374 | 0.092 | 0.23 |
| entry capability | breadth: references outside geoscience | 0.123 [0.017, 0.226] | 374 | 0.098 | 0.09 |

## Strongest association per outcome (any q), round 1

| Outcome | Feature | rho [95% CI] | q |
|:--|:--|:--|--:|
| impact: citation percentile | steps | 0.174 [0.071, 0.276] | 0.014 |
| impact: citation percentile | revisits | 0.168 [0.07, 0.269] | 0.023 |
| impact: citation percentile | novelty claims | 0.163 [0.058, 0.263] | 0.025 |
| impact: citation percentile | decisive simulation | 0.149 [0.054, 0.235] | 0.062 |
| impact: citation percentile | distinct modes | 0.13 [0.028, 0.237] | 0.088 |
| impact: field-weighted citations | steps | 0.178 [0.074, 0.276] | 0.009 |
| impact: field-weighted citations | revisits | 0.171 [0.07, 0.274] | 0.02 |
| impact: field-weighted citations | decisive simulation | 0.157 [0.065, 0.243] | 0.041 |
| impact: field-weighted citations | novelty claims | 0.147 [0.037, 0.247] | 0.064 |
| impact: field-weighted citations | distinct modes | 0.143 [0.038, 0.246] | 0.06 |
| novelty: rare topic pair | imports | 0.152 [0.05, 0.249] | 0.029 |
| novelty: rare topic pair | mode observation | 0.145 [0.038, 0.248] | 0.068 |
| novelty: rare topic pair | composition trace_series | -0.135 [-0.234, -0.035] | 0.088 |
| novelty: rare topic pair | mode reconstruction | -0.135 [-0.232, -0.037] | 0.086 |
| novelty: rare topic pair | import fields | 0.132 [0.032, 0.233] | 0.083 |
| breadth: references outside geoscience | imports | 0.547 [0.466, 0.616] | 0.009 |
| breadth: references outside geoscience | import fields | 0.505 [0.422, 0.584] | 0.009 |
| breadth: references outside geoscience | decisive methods | 0.26 [0.157, 0.36] | 0.009 |
| breadth: references outside geoscience | composition capability_first | 0.203 [0.097, 0.302] | 0.009 |
| breadth: references outside geoscience | composition trace_series | -0.203 [-0.293, -0.111] | 0.009 |
| breadth: citers outside geoscience (>=10 citers) | mode reconstruction | -0.303 [-0.464, -0.114] | 0.042 |
| breadth: citers outside geoscience (>=10 citers) | mode methods | 0.278 [0.11, 0.423] | 0.071 |
| breadth: citers outside geoscience (>=10 citers) | revisits | -0.272 [-0.459, -0.071] | 0.071 |
| breadth: citers outside geoscience (>=10 citers) | claim gate yes | 0.263 [0.057, 0.431] | 0.072 |
| breadth: citers outside geoscience (>=10 citers) | steps | -0.263 [-0.451, -0.054] | 0.083 |

## The 15 frozen round-1 associations at each stage

rho [95% bootstrap CI]. First analysis: 233 papers (the plan). Round 1 now: 374 papers (233 + 141 top-up; not independent of the first analysis). Top-up alone: 141 papers, new to the analysis. Round 2: the confirmatory test (g23, read, not rerun). Pooled: within-round ranks, round as a stratum, BH q over the pooled family.

| id | Feature | Outcome | First analysis | Round 1 now (q) | Top-up alone (p) | Round 2 (verdict) | Pooled within round (q) |
|:--|:--|:--|:--|:--|:--|:--|:--|
| H01 | import fields | breadth_refs | 0.512 [0.406, 0.611] | 0.505 [0.422, 0.584] (0.009) | 0.468 [0.317, 0.601] (0.0002) | 0.478 [0.359, 0.58] (confirmed) | 0.501 [0.427, 0.568] (0.01) |
| H02 | imports | breadth_refs | 0.566 [0.463, 0.658] | 0.547 [0.466, 0.616] (0.009) | 0.48 [0.335, 0.614] (0.0002) | 0.515 [0.397, 0.619] (confirmed) | 0.542 [0.472, 0.605] (0.01) |
| H03 | composition capability_first | breadth_refs | 0.217 [0.083, 0.347] | 0.203 [0.097, 0.302] (0.009) | 0.172 [0.006, 0.33] (0.0426) | 0.176 [0.04, 0.314] (confirmed) | 0.199 [0.105, 0.284] (0.01) |
| H04 | decisive methods | breadth_refs | 0.223 [0.088, 0.356] | 0.26 [0.157, 0.36] (0.009) | 0.314 [0.141, 0.456] (0.0004) | 0.111 [-0.034, 0.249] (not confirmed) | 0.242 [0.148, 0.331] (0.01) |
| H05 | decisive simulation | fwci | 0.211 [0.078, 0.33] | 0.157 [0.065, 0.243] (0.041) | 0.065 [-0.064, 0.192] (0.4421) | -0.03 [-0.182, 0.126] (not confirmed) | 0.129 [0.046, 0.209] (0.052) |
| H06 | distinct modes | breadth_refs | -0.224 [-0.342, -0.104] | -0.159 [-0.262, -0.058] (0.029) | -0.011 [-0.187, 0.16] (0.8944) | 0.022 [-0.115, 0.164] (not confirmed) | -0.136 [-0.222, -0.044] (0.046) |
| H07 | revisits | cnp | 0.211 [0.086, 0.335] | 0.168 [0.07, 0.269] (0.023) | 0.09 [-0.074, 0.258] (0.2897) | 0.009 [-0.134, 0.156] (not confirmed) | 0.147 [0.059, 0.233] (0.031) |
| H08 | revisits | fwci | 0.217 [0.078, 0.336] | 0.171 [0.07, 0.274] (0.02) | 0.088 [-0.073, 0.25] (0.2981) | 0.011 [-0.133, 0.158] (not confirmed) | 0.151 [0.06, 0.237] (0.031) |
| H09 | steps | fwci | 0.23 [0.107, 0.349] | 0.178 [0.074, 0.276] (0.009) | 0.087 [-0.081, 0.248] (0.3063) | 0.026 [-0.111, 0.169] (not confirmed) | 0.159 [0.067, 0.247] (0.014) |
| H10 | steps | cnp | 0.227 [0.085, 0.351] | 0.174 [0.071, 0.276] (0.014) | 0.082 [-0.079, 0.245] (0.3243) | 0.022 [-0.121, 0.161] (not confirmed) | 0.154 [0.067, 0.24] (0.031) |
| H11 | mode synthesis | breadth_refs | -0.222 [-0.349, -0.091] | -0.173 [-0.275, -0.07] (0.014) | -0.083 [-0.256, 0.094] (0.3185) | -0.175 [-0.31, -0.03] (confirmed) | -0.173 [-0.267, -0.081] (0.014) |
| H12 | decisive simulation | cnp | 0.202 [0.074, 0.32] | 0.149 [0.054, 0.235] (0.062) | 0.058 [-0.083, 0.192] (0.5107) | -0.031 [-0.176, 0.136] (not confirmed) | 0.122 [0.036, 0.199] (0.069) |
| H13 | mode observation | novelty_pair | 0.207 [0.076, 0.334] | 0.145 [0.038, 0.248] (0.068) | 0.044 [-0.124, 0.216] (0.5983) | 0.005 [-0.13, 0.134] (not confirmed) | 0.127 [0.032, 0.221] (0.056) |
| H14 | V check kinds | breadth_refs | 0.201 [0.076, 0.328] | 0.156 [0.051, 0.251] (0.052) | 0.092 [-0.074, 0.255] (0.2791) | 0.116 [-0.016, 0.257] (not confirmed) | 0.151 [0.053, 0.238] (0.035) |
| H15 | node I infer | breadth_refs | -0.181 [-0.306, -0.049] | -0.177 [-0.28, -0.065] (0.02) | -0.149 [-0.318, 0.029] (0.085) | -0.017 [-0.172, 0.132] (not confirmed) | -0.155 [-0.247, -0.06] (0.023) |

Round 1 now: 15 of 15 at q < 0.1, 15 with the round-1 sign. Top-up alone: 15 with the same sign, 4 also at p < 0.05. Pooled: 15 at q < 0.1 with the same sign. Round 2: {'confirmed': 4, 'not confirmed': 11}.

## Pooled, round as a stratum (descriptive)

572 papers (round 1 374, round 2 198); 310 tests; 42 with BH q < 0.1. rho_within = Spearman on ranks computed inside each round, centred within round and pooled; interval from 2000 bootstrap resamples within round; p from 5000 permutations of the outcome within round.

| Outcome | Round 1 median | Round 2 median |
|:--|--:|--:|
| impact: citation percentile | 0.563 | 0.554 |
| impact: field-weighted citations | 0.57 | 0.58 |
| novelty: rare topic pair | -3.847 | -3.846 |
| breadth: references outside geoscience | 0.028 | 0.038 |
| breadth: citers outside geoscience (>=10 citers) | 0.0 | 0.025 |

| Feature | Outcome | rho_within [95% CI] | rho round 1 | rho round 2 | n | q |
|:--|:--|:--|--:|--:|--:|--:|
| composition capability_first | breadth: references outside geoscience | 0.199 [0.105, 0.284] | 0.203 | 0.176 | 572 | 0.01 |
| composition trace_series | breadth: references outside geoscience | -0.207 [-0.292, -0.125] | -0.203 | -0.232 | 572 | 0.01 |
| decisive methods | breadth: references outside geoscience | 0.242 [0.148, 0.331] | 0.26 | 0.111 | 572 | 0.01 |
| mode reconstruction | breadth: references outside geoscience | -0.17 [-0.251, -0.089] | -0.174 | -0.146 | 572 | 0.01 |
| import fields | breadth: references outside geoscience | 0.501 [0.427, 0.568] | 0.505 | 0.478 | 572 | 0.01 |
| imports | breadth: references outside geoscience | 0.542 [0.472, 0.605] | 0.547 | 0.515 | 572 | 0.01 |
| mode synthesis | breadth: references outside geoscience | -0.173 [-0.267, -0.081] | -0.173 | -0.175 | 572 | 0.014 |
| node N new capability | breadth: references outside geoscience | 0.157 [0.065, 0.241] | 0.15 | 0.199 | 572 | 0.014 |
| steps | impact: field-weighted citations | 0.159 [0.067, 0.247] | 0.178 | 0.026 | 572 | 0.014 |
| node I infer | breadth: references outside geoscience | -0.155 [-0.247, -0.06] | -0.177 | -0.017 | 572 | 0.023 |
| novelty claims | impact: citation percentile | 0.15 [0.061, 0.238] | 0.163 | 0.063 | 572 | 0.023 |
| revisits | impact: citation percentile | 0.147 [0.059, 0.233] | 0.168 | 0.009 | 572 | 0.031 |
| revisits | impact: field-weighted citations | 0.151 [0.06, 0.237] | 0.171 | 0.011 | 572 | 0.031 |
| steps | impact: citation percentile | 0.154 [0.067, 0.24] | 0.174 | 0.022 | 572 | 0.031 |
| decisive reconstruction | breadth: references outside geoscience | -0.139 [-0.216, -0.063] | -0.145 | -0.093 | 572 | 0.035 |
| V check kinds | breadth: references outside geoscience | 0.151 [0.053, 0.238] | 0.156 | 0.116 | 572 | 0.035 |
| decisive instruments | breadth: references outside geoscience | 0.136 [0.072, 0.193] | 0.127 | 0.189 | 572 | 0.036 |
| distinct modes | impact: field-weighted citations | 0.138 [0.046, 0.226] | 0.143 | 0.107 | 572 | 0.046 |
| distinct modes | breadth: references outside geoscience | -0.136 [-0.222, -0.044] | -0.159 | 0.022 | 572 | 0.046 |
| novelty claims | impact: field-weighted citations | 0.138 [0.043, 0.227] | 0.147 | 0.075 | 572 | 0.046 |
| imports | novelty: rare topic pair | 0.144 [0.06, 0.232] | 0.152 | 0.091 | 572 | 0.047 |
| mode reconstruction | breadth: citers outside geoscience (>=10 citers) | -0.256 [-0.403, -0.103] | -0.303 | 0.015 | 152 | 0.048 |
| claim gate yes | breadth: citers outside geoscience (>=10 citers) | 0.248 [0.07, 0.401] | 0.263 | 0.167 | 152 | 0.049 |
| decisive methods | breadth: citers outside geoscience (>=10 citers) | 0.25 [0.06, 0.419] | 0.258 | 0.206 | 152 | 0.052 |
| decisive simulation | impact: field-weighted citations | 0.129 [0.046, 0.209] | 0.157 | -0.03 | 572 | 0.052 |
| composition trace_series | novelty: rare topic pair | -0.138 [-0.225, -0.047] | -0.135 | -0.157 | 572 | 0.053 |
| mode methods | breadth: references outside geoscience | 0.133 [0.046, 0.218] | 0.133 | 0.129 | 572 | 0.053 |
| distinct modes | impact: citation percentile | 0.128 [0.038, 0.214] | 0.13 | 0.108 | 572 | 0.053 |
| claim gate yes | breadth: references outside geoscience | 0.127 [0.032, 0.221] | 0.125 | 0.14 | 572 | 0.056 |
| mode observation | novelty: rare topic pair | 0.127 [0.032, 0.221] | 0.145 | 0.005 | 572 | 0.056 |
| node H hypothesize | breadth: references outside geoscience | -0.13 [-0.22, -0.03] | -0.139 | -0.068 | 572 | 0.056 |
| import fields | novelty: rare topic pair | 0.128 [0.038, 0.214] | 0.132 | 0.099 | 572 | 0.056 |
| composition capability_first | novelty: rare topic pair | 0.121 [0.022, 0.217] | 0.122 | 0.117 | 572 | 0.066 |
| mode reconstruction | novelty: rare topic pair | -0.125 [-0.21, -0.035] | -0.135 | -0.052 | 572 | 0.066 |
| steps | breadth: references outside geoscience | -0.126 [-0.212, -0.033] | -0.137 | -0.047 | 572 | 0.066 |
| decisive simulation | impact: citation percentile | 0.122 [0.036, 0.199] | 0.149 | -0.031 | 572 | 0.069 |
| decisive instruments | novelty: rare topic pair | 0.114 [0.018, 0.19] | 0.116 | 0.103 | 572 | 0.083 |
| mode estimation | impact: field-weighted citations | 0.119 [0.024, 0.208] | 0.106 | 0.213 | 572 | 0.083 |
| mode exploration | impact: field-weighted citations | 0.117 [0.029, 0.198] | 0.118 | 0.11 | 572 | 0.083 |
| node E explore | impact: citation percentile | 0.116 [0.025, 0.208] | 0.114 | 0.128 | 572 | 0.085 |
| node E explore | impact: field-weighted citations | 0.12 [0.026, 0.216] | 0.119 | 0.127 | 572 | 0.085 |
| mode exploration | impact: citation percentile | 0.117 [0.031, 0.198] | 0.119 | 0.103 | 572 | 0.093 |
