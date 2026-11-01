# Paper topics and journals in the roadmap corpus

Run on 2 round(s). Coded papers at run time: round 1 374 (tag calc1), round 2 198 (tag r2). Pool frame 14223 papers. Script tools/roadmap/g20_topics_journals.py; all numbers in topics_journals.json beside this file.

## How to read this

- **OpenAlex topic, subfield, field, domain.** OpenAlex assigns each paper a leading topic by a classifier over title, abstract, venue and citations; topics nest in subfields, fields and domains (for example Seismic Imaging and Inversion Techniques < Geophysics < Earth and Planetary Sciences < Physical Sciences). These are machine labels, not author keywords.
- **Journal family.** Publisher group from DOI prefix, then publisher, then journal name (rule in the script docstring). AGU journals form their own family even though Wiley publishes them.
- **Herfindahl index (HHI).** Sum of squared journal shares; 1/HHI is the number of equally sized journals that would give the same concentration.
- **Cramer's V.** Strength of association between two categorical variables, 0 (independent) to 1 (one determines the other). Plain V is biased upward when cells are small; the tables report the bias-corrected V (Bergsma 2013), which subtracts the value expected under independence, with a 95% bootstrap interval. The json has both.
- **Rate difference.** Share of papers with a property in one category minus the share in all other categories.
- **Kruskal-Wallis epsilon squared.** Share of rank variance in a count or outcome explained by the grouping, 0 to 1.
- **Permutation p.** Share of label shuffles giving an association at least as strong as observed. **BH q** (Benjamini-Hochberg) adjusts p for the number of tests within a question; q < 0.1 means at most about 10% of such findings are expected to be false positives.
- **Outcome metrics.** cnp: OpenAlex citation-normalized percentile, the paper's citation count as a percentile among works of the same OpenAlex subfield, year and type (0-1). fwci: field-weighted citation impact, citations divided by the mean for works of the same subfield, year and type (1 = world average; citations are skewed, so the median paper sits below 1). novelty_pair: -log10(1 + number of 2017-2021 works sharing the paper's leading pair of OpenAlex topics); higher means a rarer combination. breadth_refs: share of the paper's classified references outside geoscience. cnp and fwci are already subfield-normalized by OpenAlex; novelty_pair and breadth_refs are not, so differences between subfields in those two are expected from field structure alone.
- **Within-stratum rank correlation.** Spearman correlation computed after centring both ranks within each subfield (or family); only co-variation inside a stratum counts. Its p comes from shuffling outcomes within strata only.

## 1. Composition by stage

| Set | Stage | Papers | Distinct journals | HHI | Effective journals | Top-5 share | Distinct topics |
|:--|:--|--:|--:|--:|--:|--:|--:|
| pool | pool | 14223 | 475 | 0.0148 | 67.7 | 0.198 | 72 |
| round1 | drawn | 600 | 185 | 0.0195 | 51.2 | 0.242 | 61 |
| round1 | eligible | 525 | 150 | 0.023 | 43.5 | 0.27 | 45 |
| round1 | full_text | 379 | 133 | 0.0251 | 39.8 | 0.282 | 43 |
| round1 | coded | 374 | 133 | 0.0252 | 39.7 | 0.283 | 42 |
| round2 | drawn | 277 | 157 | 0.009 | 111.0 | 0.072 | 47 |
| round2 | eligible | 222 | 123 | 0.0113 | 88.3 | 0.09 | 32 |
| round2 | full_text | 202 | 114 | 0.0122 | 82.3 | 0.099 | 30 |
| round2 | coded | 198 | 114 | 0.0121 | 82.7 | 0.101 | 30 |
| pooled | drawn | 877 | 253 | 0.013 | 77.2 | 0.185 | 63 |
| pooled | eligible | 747 | 195 | 0.0157 | 63.8 | 0.21 | 46 |
| pooled | full_text | 581 | 178 | 0.0159 | 62.8 | 0.208 | 45 |
| pooled | coded | 572 | 178 | 0.0159 | 63.0 | 0.208 | 44 |

### Field by stage

| field | pool share | round 1 drawn | round 1 eligible | round 1 full_text | round 1 coded | round 2 drawn | round 2 eligible | round 2 full_text | round 2 coded |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Earth and Planetary Sciences | 0.860 | 473 | 429 | 329 | 327 | 245 | 211 | 192 | 188 |
| Environmental Science | 0.130 | 44 | 19 | 17 | 17 | 30 | 9 | 9 | 9 |
| Computer Science | 0.008 | 64 | 61 | 27 | 24 | 2 | 2 | 1 | 1 |
| Engineering | 0.001 | 19 | 16 | 6 | 6 | 0 | 0 | 0 | 0 |

### Subfield by stage

| subfield | pool share | round 1 drawn | round 1 eligible | round 1 full_text | round 1 coded | round 2 drawn | round 2 eligible | round 2 full_text | round 2 coded |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Atmospheric Science | 0.293 | 125 | 119 | 109 | 109 | 75 | 68 | 63 | 62 |
| Geophysics | 0.269 | 180 | 173 | 112 | 112 | 118 | 108 | 96 | 94 |
| Oceanography | 0.155 | 45 | 31 | 23 | 22 | 34 | 22 | 21 | 20 |
| Water Science and Technology | 0.130 | 44 | 19 | 17 | 17 | 30 | 9 | 9 | 9 |
| Earth-Surface Processes | 0.065 | 43 | 42 | 37 | 37 | 6 | 3 | 3 | 3 |
| Geochemistry and Petrology | 0.041 | 44 | 37 | 29 | 29 | 10 | 8 | 8 | 8 |
| Geology | 0.037 | 32 | 27 | 19 | 18 | 2 | 2 | 1 | 1 |
| Artificial Intelligence | 0.008 | 64 | 61 | 27 | 24 | 2 | 2 | 1 | 1 |
| Ocean Engineering | 0.001 | 19 | 16 | 6 | 6 | 0 | 0 | 0 | 0 |
| Space and Planetary Science | 0.000 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Family by stage

| family | pool share | round 1 drawn | round 1 eligible | round 1 full_text | round 1 coded | round 2 drawn | round 2 eligible | round 2 full_text | round 2 coded |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| AGU | 0.235 | 99 | 98 | 98 | 95 | 32 | 30 | 30 | 29 |
| Elsevier | 0.225 | 94 | 74 | 72 | 70 | 42 | 30 | 30 | 29 |
| Wiley non-AGU | 0.144 | 92 | 79 | 77 | 77 | 30 | 24 | 22 | 22 |
| EGU/Copernicus | 0.132 | 64 | 64 | 64 | 64 | 42 | 40 | 40 | 38 |
| Springer Nature (non-portfolio) | 0.120 | 139 | 110 | 44 | 44 | 79 | 57 | 50 | 50 |
| Nature portfolio | 0.082 | 21 | 14 | 14 | 14 | 31 | 22 | 22 | 22 |
| Oxford | 0.030 | 34 | 34 | 6 | 6 | 4 | 4 | 3 | 3 |
| SSA | 0.022 | 50 | 46 | 2 | 2 | 8 | 6 | 1 | 1 |
| other | 0.005 | 5 | 5 | 1 | 1 | 5 | 5 | 4 | 4 |
| AAAS | 0.005 | 2 | 1 | 1 | 1 | 4 | 4 | 0 | 0 |

Pool column is a share; other columns are counts.

### Most frequent journals (coded, all rounds)

| Journal | Papers | Share |
|:--|--:|--:|
| The cryosphere | 35 | 0.061 |
| Geophysical Research Letters | 28 | 0.049 |
| Journal of Geophysical Research Solid Earth | 24 | 0.042 |
| Earth Planets and Space | 17 | 0.03 |
| Geophysical Prospecting | 15 | 0.026 |
| Earth and Space Science | 11 | 0.019 |
| Journal of Geophysical Research Atmospheres | 10 | 0.017 |
| Ore Geology Reviews | 10 | 0.017 |
| Journal of Geophysical Research Earth Surface | 10 | 0.017 |
| Scientific Reports | 10 | 0.017 |
| Geophysical Journal International | 9 | 0.016 |
| Journal of Geophysical Research Oceans | 9 | 0.016 |
| Geological Journal | 9 | 0.016 |
| Natural hazards and earth system sciences | 8 | 0.014 |
| Geoscientific model development | 8 | 0.014 |

### Most frequent leading topics (coded, all rounds) and their share at earlier stages

| Topic | Coded papers | Coded share | Pool share | Round 1 preselected share | Round 1 eligible share | Round 1 full-text share |
|:--|--:|--:|--:|--:|--:|--:|
| Cryospheric studies and observations | 98 | 0.171 | 0.039 | 0.135 | 0.149 | 0.19 |
| earthquake and tectonic studies | 71 | 0.124 | 0.07 | 0.103 | 0.116 | 0.095 |
| Geological and Geochemical Analysis | 38 | 0.066 | 0.101 | 0.06 | 0.065 | 0.058 |
| Seismic Waves and Analysis | 34 | 0.059 | 0.029 | 0.052 | 0.057 | 0.053 |
| Seismic Imaging and Inversion Techniques | 29 | 0.051 | 0.02 | 0.042 | 0.046 | 0.055 |
| Seismology and Earthquake Studies | 25 | 0.044 | <top 15 | 0.107 | 0.116 | 0.071 |
| High-pressure geophysics and materials | 21 | 0.037 | <top 15 | 0.023 | 0.023 | <top 15 |
| Hydrology and Watershed Management Studies | 20 | 0.035 | 0.044 | 0.023 | 0.027 | 0.034 |
| Meteorological Phenomena and Simulations | 19 | 0.033 | 0.055 | <top 15 | <top 15 | 0.026 |
| Geology and Paleoclimatology Research | 19 | 0.033 | 0.05 | <top 15 | <top 15 | 0.026 |
| Geological formations and processes | 18 | 0.031 | 0.025 | 0.032 | 0.036 | 0.045 |
| Groundwater and Isotope Geochemistry | 18 | 0.031 | <top 15 | 0.033 | 0.032 | 0.037 |
| Atmospheric chemistry and aerosols | 17 | 0.03 | 0.067 | <top 15 | <top 15 | <top 15 |
| Oceanographic and Atmospheric Processes | 17 | 0.03 | 0.048 | 0.023 | 0.027 | <top 15 |
| Geological and Geophysical Studies | 16 | 0.028 | 0.026 | 0.037 | 0.038 | 0.04 |

## 2. Coverage bias

Among eligible papers, is reaching full text, or being coded, associated with field or venue? Categories with fewer than 10 eligible papers are pooled into "pooled small groups". Set "pooled" is both rounds with round as a stratum: the statistic sums the within-round chi-squares, coverage labels are shuffled within round, and the rate difference is the Mantel-Haenszel weighted mean of the within-round differences. BH q is computed within each set.

| Set | Response | Variable | n | Overall rate | Cramer's V, bias-corrected [95% CI] | p | q | Largest rate difference (category) |
|:--|:--|:--|--:|--:|:--|--:|--:|:--|
| round1 | full_text_among_eligible | subfield | 525 | 0.722 | 0.342 [0.28, 0.438] | 0.0002 | 0.0003 | -0.36 [-0.606, -0.094] (Ocean Engineering, n=16) |
| round1 | full_text_among_eligible | field | 525 | 0.722 | 0.267 [0.179, 0.367] | 0.0002 | 0.0003 | -0.36 [-0.606, -0.103] (Engineering, n=16) |
| round1 | full_text_among_eligible | family | 525 | 0.722 | 0.788 [0.745, 0.835] | 0.0002 | 0.0003 | -0.74 [-0.806, -0.665] (SSA, n=46) |
| round1 | full_text_among_eligible | publisher | 525 | 0.722 | 0.803 [0.758, 0.854] | 0.0002 | 0.0003 | -0.72 [-0.791, -0.638] (Seismological Research Letters, n=28) |
| round1 | coded_among_eligible | subfield | 525 | 0.712 | 0.363 [0.293, 0.452] | 0.0002 | 0.0003 | -0.36 [-0.492, -0.235] (Artificial Intelligence, n=61) |
| round1 | coded_among_eligible | field | 525 | 0.712 | 0.291 [0.208, 0.389] | 0.0002 | 0.0003 | -0.36 [-0.489, -0.236] (Computer Science, n=61) |
| round1 | coded_among_eligible | family | 525 | 0.712 | 0.764 [0.72, 0.816] | 0.0002 | 0.0003 | -0.73 [-0.797, -0.656] (SSA, n=46) |
| round1 | coded_among_eligible | publisher | 525 | 0.712 | 0.781 [0.732, 0.834] | 0.0002 | 0.0003 | -0.71 [-0.776, -0.622] (Seismological Research Letters, n=28) |
| round1 | coded_among_full_text | subfield | 379 | 0.987 | 0.229 [0.118, 0.426] | 0.0074 | 0.0096 | -0.10 [-0.244, 0.006] (Artificial Intelligence, n=27) |
| round1 | coded_among_full_text | field | 379 | 0.987 | 0.221 [0.0, 0.433] | 0.008 | 0.0096 | -0.10 [-0.244, 0.006] (Computer Science, n=27) |
| round1 | coded_among_full_text | family | 379 | 0.987 | 0.025 [0.0, 0.173] | 0.3969 | 0.433 | -0.02 [-0.063, 0.008] (AGU, n=98) |
| round1 | coded_among_full_text | publisher | 379 | 0.987 | 0.0 [0.0, 0.173] | 0.8072 | 0.8072 | -0.02 [-0.063, 0.016] (Elsevier, n=74) |
| round2 | full_text_among_eligible | subfield | 222 | 0.91 | 0.0 [0.0, 0.183] | 0.7151 | 1.0 | +0.05 [-0.062, 0.128] (Oceanography, n=22) |
| round2 | full_text_among_eligible | field | 222 | 0.91 | 0.0 [0.0, 0.147] | 1.0 | 1.0 | +0.00 [-0.122, 0.209] (Earth and Planetary Sciences, n=211) |
| round2 | full_text_among_eligible | family | 222 | 0.91 | 0.531 [0.354, 0.712] | 0.0002 | 0.0006 | -0.54 [-0.761, -0.298] (pooled small groups, n=19) |
| round2 | full_text_among_eligible | publisher | 222 | 0.91 | 0.487 [0.313, 0.674] | 0.0002 | 0.0006 | -0.51 [-0.742, -0.282] (pooled small groups, n=18) |
| round2 | coded_among_eligible | subfield | 222 | 0.892 | 0.0 [0.0, 0.181] | 0.8444 | 1.0 | -0.04 [-0.124, 0.034] (Geophysics, n=108) |
| round2 | coded_among_eligible | field | 222 | 0.892 | 0.0 [0.0, 0.124] | 1.0 | 1.0 | -0.02 [-0.14, 0.218] (Earth and Planetary Sciences, n=211) |
| round2 | coded_among_eligible | family | 222 | 0.892 | 0.454 [0.272, 0.641] | 0.0002 | 0.0006 | -0.52 [-0.736, -0.285] (pooled small groups, n=19) |
| round2 | coded_among_eligible | publisher | 222 | 0.892 | 0.414 [0.241, 0.623] | 0.0002 | 0.0006 | -0.49 [-0.733, -0.249] (pooled small groups, n=18) |
| round2 | coded_among_full_text | subfield | 202 | 0.98 | 0.0 [0.0, 0.259] | 0.9078 | 1.0 | -0.03 [-0.139, 0.033] (Oceanography, n=21) |
| round2 | coded_among_full_text | field | 202 | 0.98 | 0.0 [0.0, 0.0] | 1.0 | 1.0 | -0.02 [-0.042, -0.005] (Earth and Planetary Sciences, n=192) |
| round2 | coded_among_full_text | family | 202 | 0.98 | 0.0 [0.0, 0.246] | 0.5735 | 1.0 | -0.04 [-0.113, 0.023] (EGU/Copernicus, n=40) |
| round2 | coded_among_full_text | publisher | 202 | 0.98 | 0.0 [0.0, 0.294] | 0.5111 | 1.0 | -0.05 [-0.184, 0.031] (AGU, n=16) |
| pooled | full_text_among_eligible | subfield | 747 | 0.778 | 0.33 [0.267, 0.417] | 0.0002 | 0.0003 | -0.36 [-0.597, -0.097] (Ocean Engineering, n=16) |
| pooled | full_text_among_eligible | field | 747 | 0.778 | 0.286 [0.202, 0.374] | 0.0002 | 0.0003 | -0.36 [-0.613, -0.101] (Engineering, n=16) |
| pooled | full_text_among_eligible | family | 747 | 0.778 | 0.724 [0.684, 0.769] | 0.0002 | 0.0003 | -0.75 [-0.812, -0.669] (SSA, n=52) |
| pooled | full_text_among_eligible | publisher | 747 | 0.778 | 0.727 [0.684, 0.777] | 0.0002 | 0.0003 | -0.73 [-0.81, -0.617] (Bulletin of the Seismological Society of America, n=22) |
| pooled | coded_among_eligible | subfield | 747 | 0.766 | 0.346 [0.285, 0.427] | 0.0002 | 0.0003 | -0.36 [-0.491, -0.231] (Artificial Intelligence, n=63) |
| pooled | coded_among_eligible | field | 747 | 0.766 | 0.302 [0.218, 0.39] | 0.0002 | 0.0003 | -0.36 [-0.489, -0.233] (Computer Science, n=63) |
| pooled | coded_among_eligible | family | 747 | 0.766 | 0.691 [0.646, 0.74] | 0.0002 | 0.0003 | -0.73 [-0.798, -0.654] (SSA, n=52) |
| pooled | coded_among_eligible | publisher | 747 | 0.766 | 0.695 [0.649, 0.75] | 0.0002 | 0.0003 | -0.72 [-0.803, -0.608] (Bulletin of the Seismological Society of America, n=22) |
| pooled | coded_among_full_text | subfield | 581 | 0.985 | 0.16 [0.0, 0.36] | 0.0742 | 0.089 | -0.10 [-0.233, 0.005] (Artificial Intelligence, n=28) |
| pooled | coded_among_full_text | field | 581 | 0.985 | 0.152 [0.0, 0.357] | 0.0318 | 0.0424 | -0.10 [-0.233, 0.006] (Computer Science, n=28) |
| pooled | coded_among_full_text | family | 581 | 0.985 | 0.048 [0.0, 0.159] | 0.5313 | 0.5796 | -0.02 [-0.055, 0.007] (AGU, n=128) |
| pooled | coded_among_full_text | publisher | 581 | 0.985 | 0.0 [0.0, 0.162] | 0.7978 | 0.7978 | -0.02 [-0.075, 0.018] (AGU, n=57) |

## 3. Workflows by field and venue

Each test is run three ways: round 1 alone, round 2 alone, and both rounds with round as a stratum. In the stratified version the feature is shuffled within round only, so a difference between the rounds in field mix or in coding cannot pass for a field or venue effect. Binary and categorical features: statistic = sum of the within-round chi-squares; effect = bias-corrected Cramer's V of the pooled table; rate difference = Mantel-Haenszel weighted mean of the within-round differences (weight n_group n_rest / n_round). Counts: Kruskal-Wallis H on ranks taken within round (aligned ranks), epsilon squared = H / (n - 1); group medians are of the raw values. Bootstrap resamples are drawn within round. BH q is computed within each block. The round-2 confirmatory test of the round-1 associations is a separate analysis (tools/roadmap/g23_confirmatory.py, derived/confirmatory/CONFIRMATORY.md) and is not repeated here.

### 3.1 Round 1 alone (exploratory)

374 coded papers (round1 374). 116 tests, 56 with q < 0.1.

- subfield: groups Geophysics (112), Atmospheric Science (109), Earth-Surface Processes (37), Geochemistry and Petrology (29), Artificial Intelligence (24), Oceanography (22), Geology (18), Water Science and Technology (17), pooled small groups (6); pooled into "pooled small groups": Ocean Engineering (6)
- family: groups AGU (95), Wiley non-AGU (77), Elsevier (70), EGU/Copernicus (64), Springer Nature (non-portfolio) (44), Nature portfolio (14), pooled small groups (10); pooled into "pooled small groups": AAAS (1), Oxford (6), SSA (2), other (1)

Tests with q < 0.1. Effect: bias-corrected Cramer's V for binary and categorical features, epsilon squared for counts.

| Grouping | Feature | Kind | Effect [95% CI] | p | q | Largest rate difference or group medians |
|:--|:--|:--|:--|--:|--:|:--|
| subfield | composition capability_first | binary | V 0.358 [0.233, 0.51] | 0.0002 | 0.0018 | +0.73 [0.381, 0.924] (pooled small groups, rate 0.833, n=6) |
| subfield | mode reconstruction | binary | V 0.357 [0.273, 0.476] | 0.0002 | 0.0018 | +0.40 [0.161, 0.628] (Geology, rate 0.667, n=18) |
| subfield | composition trace_series | binary | V 0.346 [0.271, 0.448] | 0.0002 | 0.0018 | +0.34 [0.171, 0.507] (Earth-Surface Processes, rate 0.595, n=37) |
| subfield | entry capability | binary | V 0.315 [0.117, 0.494] | 0.0002 | 0.0018 | +0.76 [0.393, 0.943] (pooled small groups, rate 0.833, n=6) |
| subfield | decisive reconstruction | binary | V 0.305 [0.188, 0.456] | 0.0006 | 0.0039 | +0.30 [0.141, 0.471] (Earth-Surface Processes, rate 0.378, n=37) |
| subfield | decisive methods | binary | V 0.299 [0.21, 0.422] | 0.0002 | 0.0018 | +0.46 [0.261, 0.639] (Artificial Intelligence, rate 0.667, n=24) |
| subfield | mode methods | binary | V 0.255 [0.182, 0.389] | 0.0002 | 0.0018 | -0.31 [-0.479, -0.137] (Earth-Surface Processes, rate 0.459, n=37) |
| subfield | node N new capability | binary | V 0.253 [0.192, 0.364] | 0.0002 | 0.0018 | +0.47 [0.417, 0.519] (pooled small groups, rate 1.0, n=6) |
| family | composition trace_series | binary | V 0.247 [0.163, 0.376] | 0.0006 | 0.0039 | +0.28 [0.157, 0.408] (Elsevier, rate 0.514, n=70) |
| subfield | composition (whole variable) | categorical | V 0.236 [0.209, 0.334] | 0.0002 | 0.0018 |  |
| family | mode reconstruction | binary | V 0.234 [0.152, 0.356] | 0.0006 | 0.0039 | +0.20 [0.067, 0.328] (Elsevier, rate 0.443, n=70) |
| subfield | decisive (whole variable) | categorical | V 0.225 [0.203, 0.321] | 0.0002 | 0.0018 |  |
| family | mode simulation | binary | V 0.223 [0.145, 0.347] | 0.001 | 0.0055 | -0.29 [-0.417, -0.154] (Springer Nature (non-portfolio), rate 0.227, n=44) |
| subfield | mode simulation | binary | V 0.22 [0.149, 0.353] | 0.0008 | 0.0049 | -0.30 [-0.452, -0.128] (Geochemistry and Petrology, rate 0.207, n=29) |
| subfield | node I infer | binary | V 0.201 [0.12, 0.354] | 0.0036 | 0.0149 | -0.51 [-0.865, -0.074] (pooled small groups, rate 0.333, n=6) |
| family | node P protect | binary | V 0.197 [0.111, 0.33] | 0.0018 | 0.0087 | +0.23 [0.098, 0.369] (EGU/Copernicus, rate 0.516, n=64) |
| subfield | mode instruments | binary | V 0.196 [0.135, 0.31] | 0.004 | 0.0155 | +0.70 [0.655, 0.748] (pooled small groups, rate 1.0, n=6) |
| family | mode hypothesis | binary | V 0.195 [0.119, 0.317] | 0.002 | 0.0089 | -0.23 [-0.56, 0.104] (pooled small groups, rate 0.5, n=10) |
| family | claim gate yes | binary | V 0.192 [0.073, 0.349] | 0.004 | 0.0155 | +0.36 [0.027, 0.681] (pooled small groups, rate 0.5, n=10) |
| family | decisive reconstruction | binary | V 0.188 [0.113, 0.309] | 0.0056 | 0.0197 | +0.11 [0.019, 0.211] (Wiley non-AGU, rate 0.195, n=77) |
| subfield | any return after failure | binary | V 0.187 [0.105, 0.329] | 0.0062 | 0.0205 | +0.20 [-0.291, 0.709] (pooled small groups, rate 0.5, n=6) |
| subfield | node P protect | binary | V 0.181 [0.112, 0.32] | 0.009 | 0.029 | -0.28 [-0.368, -0.134] (Water Science and Technology, rate 0.059, n=17) |
| family | node S simulate or derive | binary | V 0.165 [0.079, 0.301] | 0.0116 | 0.0345 | -0.24 [-0.39, -0.073] (Springer Nature (non-portfolio), rate 0.455, n=44) |
| subfield | mode synthesis | binary | V 0.164 [0.086, 0.315] | 0.0192 | 0.0518 | -0.23 [-0.446, -0.028] (Artificial Intelligence, rate 0.5, n=24) |
| subfield | node E explore | binary | V 0.163 [0.075, 0.324] | 0.021 | 0.0541 | +0.22 [-0.001, 0.462] (Geology, rate 0.389, n=18) |
| subfield | decisive simulation | binary | V 0.159 [0.089, 0.289] | 0.0252 | 0.0606 | +0.13 [0.044, 0.209] (Atmospheric Science, rate 0.202, n=109) |
| subfield | node X exclude | binary | V 0.159 [0.073, 0.299] | 0.024 | 0.0605 | -0.29 [-0.485, -0.056] (Water Science and Technology, rate 0.235, n=17) |
| family | node O observe | binary | V 0.159 [0.097, 0.301] | 0.0202 | 0.0533 | -0.13 [-0.426, 0.085] (pooled small groups, rate 0.8, n=10) |
| family | node N new capability | binary | V 0.158 [0.069, 0.292] | 0.0166 | 0.0481 | +0.37 [0.124, 0.507] (pooled small groups, rate 0.9, n=10) |
| family | mode theory | binary | V 0.155 [0.063, 0.301] | 0.0192 | 0.0518 | -0.18 [-0.299, -0.048] (EGU/Copernicus, rate 0.328, n=64) |
| subfield | entry problem | binary | V 0.152 [0.0, 0.307] | 0.0324 | 0.0709 | -0.64 [-0.832, -0.278] (pooled small groups, rate 0.167, n=6) |
| subfield | mode robustness | binary | V 0.152 [0.079, 0.289] | 0.0316 | 0.0705 | -0.39 [-0.443, -0.344] (pooled small groups, rate 0.0, n=6) |
| family | mode methods | binary | V 0.148 [0.071, 0.283] | 0.0256 | 0.0606 | +0.27 [0.224, 0.314] (pooled small groups, rate 1.0, n=10) |
| family | decisive methods | binary | V 0.147 [0.045, 0.304] | 0.0282 | 0.0641 | +0.37 [0.028, 0.694] (pooled small groups, rate 0.6, n=10) |
| family | mode estimation | binary | V 0.146 [0.027, 0.293] | 0.0264 | 0.0612 | -0.19 [-0.301, -0.075] (Wiley non-AGU, rate 0.623, n=77) |
| subfield | entry (whole variable) | categorical | V 0.142 [0.112, 0.262] | 0.003 | 0.0129 |  |
| family | composition capability_first | binary | V 0.142 [0.042, 0.304] | 0.034 | 0.073 | +0.19 [-0.103, 0.519] (pooled small groups, rate 0.3, n=10) |
| family | mode observation | binary | V 0.14 [0.0, 0.297] | 0.0396 | 0.0835 | -0.31 [-0.656, 0.003] (pooled small groups, rate 0.5, n=10) |
| family | entry problem | binary | V 0.135 [0.016, 0.285] | 0.0426 | 0.0882 | +0.14 [-0.033, 0.246] (Nature portfolio, rate 0.929, n=14) |
| family | composition (whole variable) | categorical | V 0.13 [0.11, 0.231] | 0.002 | 0.0089 |  |
| family | decisive (whole variable) | categorical | V 0.111 [0.13, 0.24] | 0.011 | 0.0345 |  |
| family | steps | count | eps2 0.089 [0.049, 0.168] | 0.0002 | 0.0018 | EGU/Copernicus 24, AGU 23, Nature portfolio 22.5, Elsevier 22, Springer Nature (non-portfolio) 22, pooled small groups 21, Wiley non-AGU 19 |
| subfield | imports | count | eps2 0.082 [0.051, 0.158] | 0.0002 | 0.0018 | Artificial Intelligence 5, pooled small groups 5, Earth-Surface Processes 4, Geochemistry and Petrology 4, Water Science and Technology 4, Oceanography 3.5, Atmospheric Science 3, Geophysics 3, Geology 2 |
| family | V check kinds | count | eps2 0.082 [0.047, 0.158] | 0.0002 | 0.0018 | pooled small groups 4, AGU 3, EGU/Copernicus 3, Elsevier 3, Nature portfolio 3, Springer Nature (non-portfolio) 3, Wiley non-AGU 2 |
| family | revisits | count | eps2 0.071 [0.039, 0.144] | 0.0002 | 0.0018 | EGU/Copernicus 13, AGU 12, Elsevier 12, Nature portfolio 12, Springer Nature (non-portfolio) 12, pooled small groups 10.5, Wiley non-AGU 10 |
| family | imports | count | eps2 0.07 [0.038, 0.14] | 0.0006 | 0.0039 | Nature portfolio 4.5, pooled small groups 4.5, EGU/Copernicus 4, Elsevier 4, Springer Nature (non-portfolio) 4, AGU 3, Wiley non-AGU 3 |
| subfield | V check kinds | count | eps2 0.067 [0.04, 0.146] | 0.001 | 0.0055 | Artificial Intelligence 4, Atmospheric Science 3, Earth-Surface Processes 3, Geochemistry and Petrology 3, Geology 3, Geophysics 3, Oceanography 3, Water Science and Technology 3, pooled small groups 2.5 |
| subfield | steps | count | eps2 0.066 [0.042, 0.137] | 0.0014 | 0.0074 | pooled small groups 25, Oceanography 24.5, Atmospheric Science 23, Earth-Surface Processes 23, Geochemistry and Petrology 22, Geology 22, Artificial Intelligence 21, Geophysics 21, Water Science and Technology 20 |
| subfield | import fields | count | eps2 0.064 [0.039, 0.134] | 0.0018 | 0.0087 | pooled small groups 5, Artificial Intelligence 4, Geochemistry and Petrology 4, Atmospheric Science 3, Earth-Surface Processes 3, Geophysics 3, Oceanography 3, Water Science and Technology 3, Geology 2 |
| family | import fields | count | eps2 0.063 [0.034, 0.135] | 0.0004 | 0.0033 | Springer Nature (non-portfolio) 4, pooled small groups 4, Nature portfolio 3.5, AGU 3, EGU/Copernicus 3, Elsevier 3, Wiley non-AGU 3 |
| subfield | returns after failure | count | eps2 0.06 [0.034, 0.131] | 0.0042 | 0.0157 | pooled small groups 0.5, Artificial Intelligence 0, Atmospheric Science 0, Earth-Surface Processes 0, Geochemistry and Petrology 0, Geology 0, Geophysics 0, Oceanography 0, Water Science and Technology 0 |
| subfield | revisits | count | eps2 0.056 [0.035, 0.123] | 0.0058 | 0.0198 | pooled small groups 15, Oceanography 13.5, Atmospheric Science 12, Earth-Surface Processes 12, Geochemistry and Petrology 12, Geology 11, Geophysics 11, Water Science and Technology 11, Artificial Intelligence 9.5 |
| subfield | distinct modes | count | eps2 0.052 [0.033, 0.114] | 0.0116 | 0.0345 | Oceanography 8, Atmospheric Science 7, Earth-Surface Processes 7, Geochemistry and Petrology 7, Geology 7, Geophysics 7, Water Science and Technology 7, Artificial Intelligence 6, pooled small groups 6 |
| family | distinct modes | count | eps2 0.049 [0.026, 0.116] | 0.0044 | 0.016 | Nature portfolio 8.5, AGU 8, EGU/Copernicus 7, Elsevier 7, Springer Nature (non-portfolio) 7, Wiley non-AGU 7, pooled small groups 6.5 |
| subfield | distinct nodes | count | eps2 0.046 [0.025, 0.114] | 0.0246 | 0.0606 | Atmospheric Science 11, Earth-Surface Processes 11, Geology 11, Oceanography 11, pooled small groups 11, Artificial Intelligence 10, Geochemistry and Petrology 10, Geophysics 10, Water Science and Technology 10 |
| family | distinct nodes | count | eps2 0.04 [0.021, 0.107] | 0.0178 | 0.0504 | EGU/Copernicus 11, pooled small groups 10.5, AGU 10, Elsevier 10, Nature portfolio 10, Springer Nature (non-portfolio) 10, Wiley non-AGU 10 |

### 3.2 Round 2 alone

198 coded papers (round2 198). 106 tests, 4 with q < 0.1.

- subfield: groups Geophysics (94), Atmospheric Science (62), pooled small groups (22), Oceanography (20); pooled into "pooled small groups": Artificial Intelligence (1), Earth-Surface Processes (3), Geochemistry and Petrology (8), Geology (1), Water Science and Technology (9)
- family: groups Springer Nature (non-portfolio) (50), EGU/Copernicus (38), Elsevier (29), AGU (29), Wiley non-AGU (22), Nature portfolio (22), pooled small groups (8); pooled into "pooled small groups": Oxford (3), SSA (1), other (4)

Tests with q < 0.1. Effect: bias-corrected Cramer's V for binary and categorical features, epsilon squared for counts.

| Grouping | Feature | Kind | Effect [95% CI] | p | q | Largest rate difference or group medians |
|:--|:--|:--|:--|--:|--:|:--|
| family | mode simulation | binary | V 0.293 [0.181, 0.465] | 0.0008 | 0.0283 | -0.31 [-0.481, -0.138] (Elsevier, rate 0.241, n=29) |
| subfield | composition natures_repetition | binary | V 0.257 [0.103, 0.405] | 0.0008 | 0.0283 | +0.19 [0.081, 0.305] (Atmospheric Science, rate 0.242, n=62) |
| subfield | mode regularities | binary | V 0.241 [0.099, 0.4] | 0.0022 | 0.0583 | -0.25 [-0.372, -0.119] (Geophysics, rate 0.213, n=94) |
| subfield | composition (whole variable) | categorical | V 0.201 [0.14, 0.344] | 0.0006 | 0.0283 |  |

### 3.3 Both rounds, round as a stratum

572 coded papers (round2 198, round1 374). 130 tests, 45 with q < 0.1.

- subfield: groups Geophysics (206), Atmospheric Science (171), Oceanography (42), Earth-Surface Processes (40), Geochemistry and Petrology (37), Water Science and Technology (26), Artificial Intelligence (25), Geology (19), pooled small groups (6); pooled into "pooled small groups": Ocean Engineering (6)
- family: groups AGU (124), EGU/Copernicus (102), Wiley non-AGU (99), Elsevier (99), Springer Nature (non-portfolio) (94), Nature portfolio (36), pooled small groups (18); pooled into "pooled small groups": AAAS (1), Oxford (9), SSA (3), other (5)

Tests with q < 0.1. Effect: bias-corrected Cramer's V for binary and categorical features, epsilon squared for counts.

| Grouping | Feature | Kind | Effect [95% CI] | p | q | Largest rate difference or group medians |
|:--|:--|:--|:--|--:|--:|:--|
| subfield | decisive instruments | binary | V 0.517 [0.255, 0.736] | 0.0002 | 0.0015 | +0.82 [0.488, 0.997] (pooled small groups, rate 0.833, n=6) |
| subfield | mode reconstruction | binary | V 0.334 [0.267, 0.424] | 0.0002 | 0.0015 | +0.42 [0.194, 0.627] (Geology, rate 0.684, n=19) |
| subfield | decisive reconstruction | binary | V 0.326 [0.216, 0.452] | 0.0002 | 0.0015 | +0.35 [0.198, 0.503] (Earth-Surface Processes, rate 0.425, n=40) |
| subfield | composition trace_series | binary | V 0.319 [0.256, 0.402] | 0.0002 | 0.0015 | +0.37 [0.218, 0.524] (Earth-Surface Processes, rate 0.625, n=40) |
| subfield | composition capability_first | binary | V 0.275 [0.173, 0.402] | 0.0002 | 0.0015 | +0.73 [0.378, 0.922] (pooled small groups, rate 0.833, n=6) |
| subfield | decisive methods | binary | V 0.26 [0.179, 0.364] | 0.0002 | 0.0015 | +0.47 [0.278, 0.658] (Artificial Intelligence, rate 0.68, n=25) |
| subfield | entry capability | binary | V 0.253 [0.118, 0.389] | 0.0004 | 0.0026 | +0.76 [0.412, 0.945] (pooled small groups, rate 0.833, n=6) |
| family | composition trace_series | binary | V 0.243 [0.169, 0.341] | 0.0002 | 0.0015 | +0.28 [0.178, 0.381] (Elsevier, rate 0.515, n=99) |
| subfield | decisive (whole variable) | categorical | V 0.24 [0.211, 0.333] | 0.0002 | 0.0015 |  |
| family | mode simulation | binary | V 0.238 [0.172, 0.333] | 0.0002 | 0.0015 | -0.23 [-0.332, -0.125] (Springer Nature (non-portfolio), rate 0.309, n=94) |
| subfield | composition (whole variable) | categorical | V 0.222 [0.198, 0.295] | 0.0002 | 0.0015 |  |
| subfield | mode methods | binary | V 0.219 [0.158, 0.329] | 0.0002 | 0.0015 | -0.35 [-0.5, -0.192] (Earth-Surface Processes, rate 0.425, n=40) |
| subfield | mode simulation | binary | V 0.208 [0.148, 0.314] | 0.0004 | 0.0026 | -0.24 [-0.384, -0.085] (Geochemistry and Petrology, rate 0.27, n=37) |
| subfield | node N new capability | binary | V 0.204 [0.149, 0.299] | 0.0002 | 0.0015 | +0.47 [0.418, 0.518] (pooled small groups, rate 1.0, n=6) |
| family | claim gate yes | binary | V 0.203 [0.117, 0.317] | 0.002 | 0.0096 | +0.36 [0.113, 0.598] (pooled small groups, rate 0.5, n=18) |
| family | mode reconstruction | binary | V 0.2 [0.138, 0.296] | 0.0012 | 0.0071 | -0.21 [-0.298, -0.085] (pooled small groups, rate 0.056, n=18) |
| subfield | mode regularities | binary | V 0.194 [0.133, 0.3] | 0.002 | 0.0096 | -0.32 [-0.372, -0.278] (pooled small groups, rate 0.0, n=6) |
| subfield | composition natures_repetition | binary | V 0.186 [0.121, 0.289] | 0.0106 | 0.0394 | +0.13 [-0.023, 0.311] (Water Science and Technology, rate 0.231, n=26) |
| family | node N new capability | binary | V 0.186 [0.118, 0.285] | 0.0004 | 0.0026 | +0.24 [0.033, 0.435] (pooled small groups, rate 0.778, n=18) |
| family | mode hypothesis | binary | V 0.174 [0.103, 0.28] | 0.005 | 0.0203 | -0.21 [-0.448, 0.015] (pooled small groups, rate 0.556, n=18) |
| family | decisive reconstruction | binary | V 0.173 [0.111, 0.27] | 0.0112 | 0.0394 | +0.10 [0.025, 0.186] (Wiley non-AGU, rate 0.182, n=99) |
| subfield | node X exclude | binary | V 0.171 [0.115, 0.278] | 0.0014 | 0.0073 | -0.28 [-0.43, -0.093] (Water Science and Technology, rate 0.231, n=26) |
| family | composition capability_first | binary | V 0.164 [0.1, 0.277] | 0.0112 | 0.0394 | +0.21 [0.001, 0.452] (pooled small groups, rate 0.333, n=18) |
| subfield | node I infer | binary | V 0.162 [0.097, 0.285] | 0.0024 | 0.0108 | -0.51 [-0.866, -0.036] (pooled small groups, rate 0.333, n=6) |
| subfield | mode instruments | binary | V 0.158 [0.111, 0.256] | 0.026 | 0.0786 | +0.70 [0.653, 0.745] (pooled small groups, rate 1.0, n=6) |
| family | V full | binary | V 0.155 [0.07, 0.261] | 0.0212 | 0.0656 | -0.07 [-0.128, -0.011] (Springer Nature (non-portfolio), rate 0.915, n=94) |
| subfield | mode robustness | binary | V 0.147 [0.089, 0.26] | 0.0188 | 0.0611 | -0.39 [-0.446, -0.343] (pooled small groups, rate 0.0, n=6) |
| subfield | node E explore | binary | V 0.147 [0.077, 0.272] | 0.008 | 0.0306 | +0.20 [-0.023, 0.426] (Geology, rate 0.368, n=19) |
| family | node V vary and replicate | binary | V 0.143 [0.067, 0.253] | 0.0196 | 0.0621 | -0.07 [-0.128, -0.011] (Springer Nature (non-portfolio), rate 0.915, n=94) |
| family | composition (whole variable) | categorical | V 0.14 [0.125, 0.214] | 0.0006 | 0.0037 |  |
| family | mode theory | binary | V 0.104 [0.0, 0.221] | 0.0284 | 0.0839 | +0.25 [0.023, 0.46] (pooled small groups, rate 0.722, n=18) |
| subfield | mode estimation | binary | V 0.099 [0.0, 0.252] | 0.0334 | 0.0965 | -0.45 [-0.8, 0.012] (pooled small groups, rate 0.333, n=6) |
| subfield | imports | count | eps2 0.067 [0.042, 0.12] | 0.0002 | 0.0015 | Artificial Intelligence 5, pooled small groups 5, Earth-Surface Processes 4, Geochemistry and Petrology 4, Geophysics 4, Water Science and Technology 4, Atmospheric Science 3, Oceanography 3, Geology 2 |
| family | steps | count | eps2 0.058 [0.031, 0.11] | 0.0002 | 0.0015 | EGU/Copernicus 24, Nature portfolio 23, AGU 22, Elsevier 22, Springer Nature (non-portfolio) 22, pooled small groups 21, Wiley non-AGU 20 |
| family | distinct modes | count | eps2 0.053 [0.029, 0.1] | 0.0002 | 0.0015 | Nature portfolio 8, AGU 7, EGU/Copernicus 7, Elsevier 7, Springer Nature (non-portfolio) 7, Wiley non-AGU 7, pooled small groups 7 |
| subfield | V check kinds | count | eps2 0.048 [0.03, 0.107] | 0.0014 | 0.0073 | Artificial Intelligence 4, Atmospheric Science 3, Geochemistry and Petrology 3, Geology 3, Geophysics 3, Oceanography 3, Earth-Surface Processes 2.5, pooled small groups 2.5, Water Science and Technology 2 |
| family | V check kinds | count | eps2 0.048 [0.025, 0.098] | 0.0002 | 0.0015 | pooled small groups 3.5, AGU 3, EGU/Copernicus 3, Elsevier 3, Nature portfolio 3, Springer Nature (non-portfolio) 3, Wiley non-AGU 2 |
| subfield | import fields | count | eps2 0.046 [0.031, 0.101] | 0.0014 | 0.0073 | pooled small groups 5, Artificial Intelligence 4, Geochemistry and Petrology 4, Water Science and Technology 4, Atmospheric Science 3, Earth-Surface Processes 3, Geophysics 3, Oceanography 3, Geology 2 |
| family | revisits | count | eps2 0.044 [0.023, 0.09] | 0.0002 | 0.0015 | EGU/Copernicus 13, AGU 12, Elsevier 12, Nature portfolio 12, Springer Nature (non-portfolio) 12, Wiley non-AGU 10, pooled small groups 10 |
| subfield | steps | count | eps2 0.042 [0.024, 0.084] | 0.0022 | 0.0102 | pooled small groups 25, Oceanography 24, Earth-Surface Processes 23, Atmospheric Science 22, Geochemistry and Petrology 22, Geology 22, Artificial Intelligence 21, Geophysics 21, Water Science and Technology 20 |
| subfield | distinct modes | count | eps2 0.039 [0.024, 0.084] | 0.0032 | 0.0139 | Geochemistry and Petrology 8, Oceanography 8, Atmospheric Science 7, Earth-Surface Processes 7, Geology 7, Geophysics 7, Water Science and Technology 7, Artificial Intelligence 6, pooled small groups 6 |
| subfield | revisits | count | eps2 0.039 [0.024, 0.084] | 0.004 | 0.0168 | pooled small groups 15, Earth-Surface Processes 13, Oceanography 13, Atmospheric Science 12, Geochemistry and Petrology 12, Geology 11, Geophysics 11, Water Science and Technology 11, Artificial Intelligence 9 |
| family | imports | count | eps2 0.031 [0.015, 0.076] | 0.0058 | 0.0228 | EGU/Copernicus 4, Elsevier 4, Nature portfolio 4, Springer Nature (non-portfolio) 4, pooled small groups 4, AGU 3, Wiley non-AGU 3 |
| family | import fields | count | eps2 0.029 [0.011, 0.064] | 0.0178 | 0.0593 | Springer Nature (non-portfolio) 4, pooled small groups 4, AGU 3, EGU/Copernicus 3, Elsevier 3, Nature portfolio 3, Wiley non-AGU 3 |
| family | distinct nodes | count | eps2 0.026 [0.013, 0.073] | 0.0178 | 0.0593 | EGU/Copernicus 11, Nature portfolio 11, Springer Nature (non-portfolio) 11, pooled small groups 11, AGU 10.5, Elsevier 10, Wiley non-AGU 10 |

### 3.4 The three blocks side by side

Every test with q < 0.1 in at least one block. Cell: effect, q; "n.t." = not tested in that block (binary feature present in fewer than 10 or more than n - 10 papers).

| Grouping | Feature | Round 1 alone (exploratory) | Round 2 alone | Both rounds, round as a stratum |
|:--|:--|:--|:--|:--|
| family | V check kinds | 0.082, q 0.0018 * | 0.028, q 0.77 | 0.048, q 0.0015 * |
| family | V full | n.t. | n.t. | 0.155, q 0.0656 * |
| family | claim gate yes | 0.192, q 0.0155 * | 0.174, q 0.31 | 0.203, q 0.0096 * |
| family | composition (whole variable) | 0.13, q 0.0089 * | 0.143, q 0.2502 | 0.14, q 0.0037 * |
| family | composition capability_first | 0.142, q 0.073 * | 0.182, q 0.31 | 0.164, q 0.0394 * |
| family | composition trace_series | 0.247, q 0.0039 * | 0.223, q 0.2367 | 0.243, q 0.0015 * |
| family | decisive (whole variable) | 0.111, q 0.0345 * | 0.028, q 0.747 | 0.089, q 0.2443 |
| family | decisive methods | 0.147, q 0.0641 * | 0.0, q 0.9148 | 0.11, q 0.2443 |
| family | decisive reconstruction | 0.188, q 0.0197 * | 0.062, q 0.6762 | 0.173, q 0.0394 * |
| family | distinct modes | 0.049, q 0.016 * | 0.064, q 0.31 | 0.053, q 0.0015 * |
| family | distinct nodes | 0.04, q 0.0504 * | 0.027, q 0.7723 | 0.026, q 0.0593 * |
| family | entry problem | 0.135, q 0.0882 * | 0.0, q 0.7807 | 0.107, q 0.2314 |
| family | import fields | 0.063, q 0.0033 * | 0.014, q 0.941 | 0.029, q 0.0593 * |
| family | imports | 0.07, q 0.0039 * | 0.009, q 0.9821 | 0.031, q 0.0228 * |
| family | mode estimation | 0.146, q 0.0612 * | 0.048, q 0.7057 | 0.134, q 0.1508 |
| family | mode hypothesis | 0.195, q 0.0089 * | 0.098, q 0.6395 | 0.174, q 0.0203 * |
| family | mode methods | 0.148, q 0.0606 * | 0.074, q 0.6578 | 0.142, q 0.12 |
| family | mode observation | 0.14, q 0.0835 * | 0.0, q 0.9054 | 0.094, q 0.2567 |
| family | mode reconstruction | 0.234, q 0.0039 * | 0.071, q 0.6578 | 0.2, q 0.0071 * |
| family | mode simulation | 0.223, q 0.0055 * | 0.293, q 0.0283 * | 0.238, q 0.0015 * |
| family | mode theory | 0.155, q 0.0518 * | 0.099, q 0.6395 | 0.104, q 0.0839 * |
| family | node N new capability | 0.158, q 0.0481 * | 0.25, q 0.1102 | 0.186, q 0.0026 * |
| family | node O observe | 0.159, q 0.0533 * | 0.0, q 0.9069 | 0.139, q 0.1907 |
| family | node P protect | 0.197, q 0.0087 * | 0.0, q 1.0 | 0.107, q 0.122 |
| family | node S simulate or derive | 0.165, q 0.0345 * | 0.0, q 0.7807 | 0.131, q 0.1269 |
| family | node V vary and replicate | n.t. | n.t. | 0.143, q 0.0621 * |
| family | revisits | 0.071, q 0.0018 * | 0.038, q 0.6395 | 0.044, q 0.0015 * |
| family | steps | 0.089, q 0.0018 * | 0.044, q 0.6321 | 0.058, q 0.0015 * |
| subfield | V check kinds | 0.067, q 0.0055 * | 0.046, q 0.2698 | 0.048, q 0.0073 * |
| subfield | any return after failure | 0.187, q 0.0205 * | 0.0, q 0.9054 | 0.105, q 0.1203 |
| subfield | composition (whole variable) | 0.236, q 0.0018 * | 0.201, q 0.0283 * | 0.222, q 0.0015 * |
| subfield | composition capability_first | 0.358, q 0.0018 * | 0.0, q 0.77 | 0.275, q 0.0015 * |
| subfield | composition natures_repetition | 0.13, q 0.1495 | 0.257, q 0.0283 * | 0.186, q 0.0394 * |
| subfield | composition trace_series | 0.346, q 0.0018 * | 0.07, q 0.6395 | 0.319, q 0.0015 * |
| subfield | decisive (whole variable) | 0.225, q 0.0018 * | 0.101, q 0.5406 | 0.24, q 0.0015 * |
| subfield | decisive instruments | n.t. | n.t. | 0.517, q 0.0015 * |
| subfield | decisive methods | 0.299, q 0.0018 * | 0.036, q 0.6854 | 0.26, q 0.0015 * |
| subfield | decisive reconstruction | 0.305, q 0.0039 * | 0.031, q 0.6854 | 0.326, q 0.0015 * |
| subfield | decisive simulation | 0.159, q 0.0606 * | 0.136, q 0.3884 | 0.165, q 0.1401 |
| subfield | distinct modes | 0.052, q 0.0345 * | 0.01, q 0.781 | 0.039, q 0.0139 * |
| subfield | distinct nodes | 0.046, q 0.0606 * | 0.003, q 0.9758 | 0.021, q 0.285 |
| subfield | entry (whole variable) | 0.142, q 0.0129 * | 0.0, q 0.8701 | 0.101, q 0.2465 |
| subfield | entry capability | 0.315, q 0.0018 * | 0.0, q 0.77 | 0.253, q 0.0026 * |
| subfield | entry problem | 0.152, q 0.0709 * | 0.0, q 0.747 | 0.133, q 0.1667 |
| subfield | import fields | 0.064, q 0.0087 * | 0.041, q 0.31 | 0.046, q 0.0073 * |
| subfield | imports | 0.082, q 0.0018 * | 0.037, q 0.31 | 0.067, q 0.0015 * |
| subfield | mode estimation | 0.112, q 0.1975 | 0.157, q 0.31 | 0.099, q 0.0965 * |
| subfield | mode instruments | 0.196, q 0.0155 * | 0.0, q 0.9054 | 0.158, q 0.0786 * |
| subfield | mode methods | 0.255, q 0.0018 * | 0.0, q 0.9109 | 0.219, q 0.0015 * |
| subfield | mode reconstruction | 0.357, q 0.0018 * | 0.077, q 0.6395 | 0.334, q 0.0015 * |
| subfield | mode regularities | 0.116, q 0.1944 | 0.241, q 0.0583 * | 0.194, q 0.0096 * |
| subfield | mode robustness | 0.152, q 0.0705 * | 0.0, q 0.9477 | 0.147, q 0.0611 * |
| subfield | mode simulation | 0.22, q 0.0049 * | 0.189, q 0.2438 | 0.208, q 0.0026 * |
| subfield | mode synthesis | 0.164, q 0.0518 * | 0.0, q 0.8701 | 0.15, q 0.1583 |
| subfield | node E explore | 0.163, q 0.0541 * | 0.146, q 0.31 | 0.147, q 0.0306 * |
| subfield | node I infer | 0.201, q 0.0149 * | 0.195, q 0.2438 | 0.162, q 0.0108 * |
| subfield | node N new capability | 0.253, q 0.0018 * | 0.0, q 0.9758 | 0.204, q 0.0015 * |
| subfield | node P protect | 0.181, q 0.029 * | 0.0, q 0.9821 | 0.106, q 0.1227 |
| subfield | node X exclude | 0.159, q 0.0605 * | 0.122, q 0.4578 | 0.171, q 0.0073 * |
| subfield | returns after failure | 0.06, q 0.0157 * | 0.005, q 0.9148 | 0.017, q 0.7788 |
| subfield | revisits | 0.056, q 0.0198 * | 0.011, q 0.7807 | 0.039, q 0.0168 * |
| subfield | steps | 0.066, q 0.0074 * | 0.012, q 0.77 | 0.042, q 0.0102 * |

\* q < 0.1.


## 4. Outcomes by field and venue

Round 1 alone (the top-level rows of outcomes_by_group). Median per group [95% bootstrap CI]. Last row: Kruskal-Wallis epsilon squared [95% CI] and BH q. cnp and fwci are subfield-normalized by OpenAlex; novelty_pair and breadth_refs are not. Section 4.5 compares round 1, round 2 and both rounds with round as a stratum.

### Coded papers by subfield

| subfield | n | cnp | fwci | novelty_pair | breadth_refs |
|:--|--:|:--|:--|:--|:--|
| Geophysics | 112 | 0.484 [0.394, 0.576] | 0.434 [0.289, 0.722] | -4.066 [-4.118, -3.887] | 0.033 [0.024, 0.047] |
| Atmospheric Science | 109 | 0.581 [0.5, 0.639] | 0.663 [0.474, 0.854] | -3.827 [-4.238, -3.653] | 0.018 [0.012, 0.028] |
| Earth-Surface Processes | 37 | 0.558 [0.391, 0.681] | 0.498 [0.166, 0.997] | -3.666 [-3.989, -3.506] | 0.02 [0.004, 0.056] |
| Geochemistry and Petrology | 29 | 0.464 [0.382, 0.675] | 0.296 [0.148, 0.74] | -3.776 [-3.836, -3.342] | 0.023 [0.013, 0.045] |
| Artificial Intelligence | 24 | 0.703 [0.559, 0.817] | 0.725 [0.323, 1.366] | -3.711 [-3.711, -3.426] | 0.236 [0.175, 0.289] |
| Oceanography | 22 | 0.594 [0.524, 0.755] | 0.663 [0.482, 1.329] | -4.269 [-4.302, -3.971] | 0.022 [0.0, 0.042] |
| Geology | 18 | 0.6 [0.33, 0.789] | 0.419 [0.105, 1.463] | -4.303 [-4.31, -3.79] | 0.011 [0.0, 0.034] |
| Water Science and Technology | 17 | 0.451 [0.31, 0.738] | 0.277 [0.069, 1.18] | -3.777 [-4.172, -3.513] | 0.033 [0.017, 0.077] |
| pooled small groups | 6 | 0.596 [0.13, 0.778] | 0.599 [0.0, 1.435] | -3.186 [-3.552, -2.885] | 0.167 [0.059, 0.222] |
| all | 374 | 0.563 | 0.57 | -3.847 | 0.028 |
| eps2, q | | 0.029 [0.018, 0.09], q 0.24 | 0.021 [0.014, 0.081], q 0.4607 | 0.103 [0.069, 0.172], q 0.0003 | 0.137 [0.09, 0.225], q 0.0003 |

### Coded papers by family

| family | n | cnp | fwci | novelty_pair | breadth_refs |
|:--|--:|:--|:--|:--|:--|
| AGU | 95 | 0.653 [0.581, 0.763] | 0.867 [0.578, 1.335] | -3.971 [-4.099, -3.711] | 0.02 [0.014, 0.025] |
| Wiley non-AGU | 77 | 0.404 [0.352, 0.512] | 0.289 [0.148, 0.475] | -3.856 [-4.118, -3.678] | 0.028 [0.018, 0.042] |
| Elsevier | 70 | 0.558 [0.434, 0.709] | 0.59 [0.283, 0.988] | -3.886 [-4.041, -3.782] | 0.028 [0.013, 0.044] |
| EGU/Copernicus | 64 | 0.646 [0.577, 0.728] | 0.782 [0.592, 1.169] | -3.847 [-4.172, -3.607] | 0.03 [0.018, 0.046] |
| Springer Nature (non-portfolio) | 44 | 0.479 [0.332, 0.595] | 0.399 [0.145, 0.58] | -3.768 [-3.886, -3.366] | 0.064 [0.028, 0.084] |
| Nature portfolio | 14 | 0.604 [0.548, 0.798] | 0.741 [0.323, 1.516] | -3.803 [-4.238, -3.543] | 0.036 [0.0, 0.155] |
| pooled small groups | 10 | 0.489 [0.247, 0.779] | 0.345 [0.08, 1.285] | -3.711 [-4.371, -2.471] | 0.214 [0.08, 0.265] |
| all | 374 | 0.563 | 0.57 | -3.847 | 0.028 |
| eps2, q | | 0.087 [0.053, 0.162], q 0.0003 | 0.096 [0.058, 0.172], q 0.0003 | 0.013 [0.007, 0.063], q 0.5751 | 0.045 [0.022, 0.106], q 0.0101 |

### Eligible papers by subfield

| subfield | n | cnp | fwci | novelty_pair | breadth_refs |
|:--|--:|:--|:--|:--|:--|
| Geophysics | 173 | 0.383 [0.33, 0.47] | 0.289 [0.145, 0.433] | -4.005 [-4.099, -3.887] | 0.033 [0.027, 0.042] |
| Atmospheric Science | 119 | 0.546 [0.468, 0.62] | 0.57 [0.38, 0.759] | -3.847 [-4.238, -3.678] | 0.018 [0.013, 0.029] |
| Artificial Intelligence | 61 | 0.688 [0.569, 0.763] | 0.647 [0.402, 0.964] | -3.711 [-3.711, -3.711] | 0.211 [0.121, 0.262] |
| Earth-Surface Processes | 42 | 0.523 [0.383, 0.674] | 0.414 [0.166, 0.993] | -3.753 [-3.989, -3.579] | 0.014 [0.0, 0.043] |
| Geochemistry and Petrology | 37 | 0.464 [0.377, 0.616] | 0.296 [0.148, 0.592] | -3.776 [-3.836, -3.366] | 0.029 [0.018, 0.052] |
| Oceanography | 31 | 0.525 [0.35, 0.666] | 0.483 [0.121, 1.025] | -4.269 [-4.291, -3.971] | 0.022 [0.0, 0.042] |
| Geology | 27 | 0.595 [0.522, 0.764] | 0.419 [0.209, 1.463] | -4.296 [-4.31, -4.296] | 0.01 [0.0, 0.049] |
| Water Science and Technology | 19 | 0.374 [0.31, 0.593] | 0.139 [0.069, 0.623] | -3.777 [-4.133, -3.513] | 0.033 [0.017, 0.067] |
| Ocean Engineering | 16 | 0.473 [0.352, 0.634] | 0.299 [0.12, 0.718] | -3.186 [-3.552, -2.972] | 0.167 [0.057, 0.22] |
| all | 525 | 0.518 | 0.419 | -3.847 | 0.032 |
| eps2, q | | 0.063 [0.038, 0.121], q 0.0003 | 0.042 [0.025, 0.096], q 0.007 | 0.134 [0.098, 0.196], q 0.0003 | 0.148 [0.102, 0.225], q 0.0003 |

### Eligible papers by family

| family | n | cnp | fwci | novelty_pair | breadth_refs |
|:--|--:|:--|:--|:--|:--|
| Springer Nature (non-portfolio) | 110 | 0.332 [0.319, 0.374] | 0.145 [0.095, 0.157] | -3.886 [-3.925, -3.776] | 0.033 [0.018, 0.053] |
| AGU | 98 | 0.66 [0.603, 0.778] | 0.909 [0.603, 1.435] | -3.971 [-4.1, -3.711] | 0.02 [0.014, 0.026] |
| Wiley non-AGU | 79 | 0.404 [0.366, 0.525] | 0.289 [0.148, 0.474] | -3.856 [-4.126, -3.666] | 0.028 [0.016, 0.047] |
| Elsevier | 74 | 0.558 [0.431, 0.704] | 0.59 [0.289, 0.964] | -3.886 [-4.037, -3.776] | 0.028 [0.013, 0.045] |
| EGU/Copernicus | 64 | 0.646 [0.577, 0.728] | 0.782 [0.58, 1.16] | -3.847 [-4.172, -3.607] | 0.03 [0.018, 0.046] |
| SSA | 46 | 0.551 [0.46, 0.634] | 0.402 [0.201, 0.722] | -3.711 [-3.711, -3.711] | 0.089 [0.057, 0.222] |
| Oxford | 34 | 0.426 [0.092, 0.676] | 0.289 [0.0, 0.722] | -3.732 [-3.886, -3.379] | 0.132 [0.078, 0.191] |
| Nature portfolio | 14 | 0.604 [0.548, 0.798] | 0.741 [0.323, 1.516] | -3.803 [-4.238, -3.543] | 0.036 [0.0, 0.155] |
| pooled small groups | 6 | 0.311 [0.03, 0.665] | 0.222 [0.0, 1.011] | -4.34 [-4.544, -3.747] | 0.039 [0.007, 0.107] |
| all | 525 | 0.518 | 0.419 | -3.847 | 0.032 |
| eps2, q | | 0.147 [0.106, 0.217], q 0.0003 | 0.164 [0.117, 0.238], q 0.0003 | 0.026 [0.016, 0.068], q 0.1113 | 0.065 [0.038, 0.128], q 0.0003 |

### 4.5 Round 1, round 2 and both rounds with round as a stratum

Cell: n, Kruskal-Wallis epsilon squared [95% CI], BH q within the block. Stratified block: values ranked within round, shuffled within round, resampled within round.

| Population | Grouping | Outcome | Round 1 | Round 2 | Both rounds, round stratum |
|:--|:--|:--|:--|:--|:--|
| coded | subfield | cnp | n 374, 0.029 [0.018, 0.09], q 0.24 | n 198, 0.029 [0.006, 0.116], q 0.2205 | n 572, 0.026 [0.016, 0.068], q 0.0672 * |
| coded | subfield | fwci | n 374, 0.021 [0.014, 0.081], q 0.4607 | n 198, 0.018 [0.004, 0.096], q 0.3824 | n 572, 0.016 [0.011, 0.061], q 0.3489 |
| coded | subfield | novelty_pair | n 374, 0.103 [0.069, 0.172], q 0.0003 * | n 198, 0.057 [0.019, 0.142], q 0.0784 * | n 572, 0.072 [0.047, 0.122], q 0.0003 * |
| coded | subfield | breadth_refs | n 374, 0.137 [0.09, 0.225], q 0.0003 * | n 198, 0.049 [0.013, 0.132], q 0.1152 | n 572, 0.097 [0.065, 0.149], q 0.0003 * |
| coded | family | cnp | n 374, 0.087 [0.053, 0.162], q 0.0003 * | n 198, 0.061 [0.032, 0.162], q 0.1646 | n 572, 0.062 [0.038, 0.113], q 0.0003 * |
| coded | family | fwci | n 374, 0.096 [0.058, 0.172], q 0.0003 * | n 198, 0.058 [0.031, 0.155], q 0.1646 | n 572, 0.063 [0.039, 0.116], q 0.0003 * |
| coded | family | novelty_pair | n 374, 0.013 [0.007, 0.063], q 0.5751 | n 198, 0.024 [0.013, 0.121], q 0.6271 | n 572, 0.008 [0.004, 0.04], q 0.6235 |
| coded | family | breadth_refs | n 374, 0.045 [0.022, 0.106], q 0.0101 * | n 198, 0.044 [0.024, 0.135], q 0.272 | n 572, 0.036 [0.019, 0.08], q 0.004 * |
| eligible | subfield | cnp | n 525, 0.063 [0.038, 0.121], q 0.0003 * | n 222, 0.028 [0.007, 0.103], q 0.1692 | n 747, 0.05 [0.032, 0.091], q 0.0003 * |
| eligible | subfield | fwci | n 525, 0.042 [0.025, 0.096], q 0.007 * | n 222, 0.017 [0.004, 0.084], q 0.3824 | n 747, 0.031 [0.018, 0.07], q 0.0038 * |
| eligible | subfield | novelty_pair | n 525, 0.134 [0.098, 0.196], q 0.0003 * | n 222, 0.054 [0.017, 0.133], q 0.0784 * | n 747, 0.095 [0.069, 0.138], q 0.0003 * |
| eligible | subfield | breadth_refs | n 525, 0.148 [0.102, 0.225], q 0.0003 * | n 222, 0.029 [0.006, 0.097], q 0.1692 | n 747, 0.104 [0.07, 0.153], q 0.0003 * |
| eligible | family | cnp | n 525, 0.147 [0.106, 0.217], q 0.0003 * | n 222, 0.055 [0.027, 0.152], q 0.1646 | n 747, 0.101 [0.074, 0.154], q 0.0003 * |
| eligible | family | fwci | n 525, 0.164 [0.117, 0.238], q 0.0003 * | n 222, 0.054 [0.031, 0.148], q 0.1646 | n 747, 0.106 [0.077, 0.158], q 0.0003 * |
| eligible | family | novelty_pair | n 525, 0.026 [0.016, 0.068], q 0.1113 | n 222, 0.019 [0.01, 0.104], q 0.6423 | n 747, 0.013 [0.009, 0.042], q 0.4138 |
| eligible | family | breadth_refs | n 525, 0.065 [0.038, 0.128], q 0.0003 * | n 222, 0.025 [0.013, 0.103], q 0.5496 | n 747, 0.049 [0.031, 0.093], q 0.0003 * |

\* q < 0.1.

## 5. Are the g17 workflow-outcome associations explained by field or venue?

38 g17 tests with q < 0.1 (round 1, tools/roadmap/g17_outcomes.py output) rechecked on the 374 round-1 papers coded now. Survivors (same sign, q < 0.1 over the 114 stratified tests): subfield 31/38, family 36/38, subfield x family 24/38; of these, with a bootstrap interval that excludes 0: subfield 25, family 35, subfield x family 21.

| Feature | Outcome | g17 rho | rho now | within subfield [CI], q | within family [CI], q | within subfield x family [CI], q |
|:--|:--|--:|--:|:--|:--|:--|
| claim gate yes | breadth_citers (not normalized) | 0.263 | 0.263 | 0.178 [-0.013, 0.388], 0.1232 does not survive | 0.275 [0.065, 0.475], 0.0218 survives | 0.218 [0.017, 0.467], 0.1105 does not survive |
| composition capability_first | breadth_refs (not normalized) | 0.203 | 0.203 | 0.101 [-0.009, 0.2], 0.0586 survives, CI spans 0 | 0.196 [0.094, 0.298], 0.0023 survives | 0.11 [0.001, 0.227], 0.0587 survives |
| composition trace_series | novelty_pair (not normalized) | -0.135 | -0.135 | -0.151 [-0.251, -0.05], 0.0177 survives | -0.118 [-0.224, -0.017], 0.0453 survives | -0.099 [-0.209, 0.009], 0.0972 survives, CI spans 0 |
| composition trace_series | breadth_refs (not normalized) | -0.203 | -0.203 | -0.159 [-0.253, -0.06], 0.0177 survives | -0.203 [-0.289, -0.106], 0.0023 survives | -0.169 [-0.266, -0.072], 0.0177 survives |
| decisive estimation | breadth_refs (not normalized) | -0.128 | -0.128 | -0.095 [-0.196, 0.003], 0.0897 survives, CI spans 0 | -0.12 [-0.213, -0.022], 0.0382 survives | -0.097 [-0.202, 0.002], 0.1058 does not survive |
| decisive methods | breadth_refs (not normalized) | 0.26 | 0.26 | 0.192 [0.088, 0.292], 0.0023 survives | 0.24 [0.13, 0.34], 0.0023 survives | 0.191 [0.083, 0.311], 0.007 survives |
| decisive methods | breadth_citers (not normalized) | 0.258 | 0.258 | 0.165 [-0.036, 0.335], 0.1501 does not survive | 0.198 [-0.017, 0.411], 0.0839 survives, CI spans 0 | 0.166 [-0.034, 0.365], 0.1816 does not survive |
| decisive reconstruction | breadth_refs (not normalized) | -0.145 | -0.145 | -0.114 [-0.208, -0.017], 0.0529 survives | -0.149 [-0.236, -0.061], 0.0182 survives | -0.144 [-0.237, -0.033], 0.031 survives |
| decisive simulation | cnp | 0.149 | 0.149 | 0.139 [0.05, 0.227], 0.0205 survives | 0.121 [0.025, 0.211], 0.0363 survives | 0.125 [0.021, 0.216], 0.041 survives |
| decisive simulation | fwci | 0.157 | 0.157 | 0.14 [0.052, 0.227], 0.02 survives | 0.128 [0.036, 0.214], 0.0284 survives | 0.126 [0.025, 0.221], 0.0377 survives |
| entry capability | breadth_refs (not normalized) | 0.123 | 0.123 | 0.084 [-0.021, 0.19], 0.1192 does not survive | 0.124 [0.017, 0.234], 0.0358 survives | 0.096 [-0.024, 0.211], 0.1058 does not survive |
| mode methods | breadth_refs (not normalized) | 0.133 | 0.133 | 0.099 [-0.003, 0.201], 0.0839 survives, CI spans 0 | 0.117 [0.012, 0.21], 0.0378 survives | 0.102 [0.004, 0.219], 0.0839 survives |
| mode methods | breadth_citers (not normalized) | 0.278 | 0.278 | 0.291 [0.096, 0.452], 0.0218 survives | 0.264 [0.087, 0.429], 0.027 survives | 0.334 [0.111, 0.523], 0.0201 survives |
| mode observation | novelty_pair (not normalized) | 0.145 | 0.145 | 0.111 [0.009, 0.212], 0.0537 survives | 0.134 [0.025, 0.231], 0.0223 survives | 0.1 [-0.026, 0.205], 0.0839 survives, CI spans 0 |
| mode reconstruction | novelty_pair (not normalized) | -0.135 | -0.135 | -0.144 [-0.248, -0.038], 0.0177 survives | -0.121 [-0.22, -0.023], 0.0375 survives | -0.088 [-0.192, 0.021], 0.1238 does not survive |
| mode reconstruction | breadth_refs (not normalized) | -0.174 | -0.174 | -0.129 [-0.225, -0.035], 0.0284 survives | -0.176 [-0.27, -0.07], 0.0057 survives | -0.161 [-0.265, -0.058], 0.0192 survives |
| mode reconstruction | breadth_citers (not normalized) | -0.303 | -0.303 | -0.247 [-0.424, -0.036], 0.0282 survives | -0.354 [-0.492, -0.192], 0.0071 survives | -0.22 [-0.392, -0.073], 0.0597 survives |
| mode synthesis | breadth_refs (not normalized) | -0.173 | -0.173 | -0.116 [-0.216, -0.008], 0.043 survives | -0.159 [-0.259, -0.05], 0.0171 survives | -0.114 [-0.203, 0.008], 0.0681 survives, CI spans 0 |
| node H hypothesize | breadth_refs (not normalized) | -0.139 | -0.139 | -0.105 [-0.201, -0.005], 0.0586 survives | -0.131 [-0.238, -0.031], 0.0263 survives | -0.091 [-0.196, 0.024], 0.1231 does not survive |
| node I infer | breadth_refs (not normalized) | -0.177 | -0.177 | -0.15 [-0.247, -0.043], 0.0179 survives | -0.184 [-0.285, -0.079], 0.0057 survives | -0.151 [-0.248, -0.033], 0.0205 survives |
| node N new capability | breadth_refs (not normalized) | 0.15 | 0.15 | 0.088 [-0.014, 0.188], 0.1138 does not survive | 0.141 [0.048, 0.233], 0.0218 survives | 0.095 [0.001, 0.202], 0.107 does not survive |
| V check kinds | breadth_refs (not normalized) | 0.156 | 0.156 | 0.122 [0.012, 0.231], 0.0349 survives | 0.151 [0.051, 0.248], 0.0177 survives | 0.144 [0.032, 0.255], 0.0218 survives |
| distinct modes | cnp | 0.13 | 0.13 | 0.137 [0.035, 0.244], 0.0233 survives | 0.077 [-0.027, 0.182], 0.1614 does not survive | 0.091 [-0.024, 0.199], 0.1196 does not survive |
| distinct modes | fwci | 0.143 | 0.143 | 0.138 [0.035, 0.243], 0.0218 survives | 0.087 [-0.021, 0.195], 0.1105 does not survive | 0.091 [-0.017, 0.199], 0.117 does not survive |
| distinct modes | breadth_refs (not normalized) | -0.159 | -0.159 | -0.101 [-0.205, 0.003], 0.0836 survives, CI spans 0 | -0.143 [-0.235, -0.035], 0.0205 survives | -0.087 [-0.187, 0.037], 0.1252 does not survive |
| import fields | novelty_pair (not normalized) | 0.132 | 0.132 | 0.078 [-0.021, 0.187], 0.1527 does not survive | 0.125 [0.022, 0.23], 0.0308 survives | 0.068 [-0.048, 0.174], 0.2284 does not survive |
| import fields | breadth_refs (not normalized) | 0.505 | 0.505 | 0.483 [0.392, 0.566], 0.0023 survives | 0.497 [0.409, 0.576], 0.0023 survives | 0.482 [0.39, 0.567], 0.0023 survives |
| imports | novelty_pair (not normalized) | 0.152 | 0.152 | 0.091 [-0.015, 0.193], 0.1046 does not survive | 0.143 [0.039, 0.245], 0.0182 survives | 0.08 [-0.033, 0.186], 0.1536 does not survive |
| imports | breadth_refs (not normalized) | 0.547 | 0.547 | 0.512 [0.426, 0.595], 0.0023 survives | 0.538 [0.454, 0.614], 0.0023 survives | 0.507 [0.411, 0.588], 0.0023 survives |
| novelty claims | cnp | 0.163 | 0.163 | 0.161 [0.061, 0.262], 0.0084 survives | 0.149 [0.041, 0.249], 0.0192 survives | 0.152 [0.045, 0.263], 0.0177 survives |
| novelty claims | fwci | 0.147 | 0.147 | 0.151 [0.047, 0.259], 0.0177 survives | 0.135 [0.024, 0.238], 0.0233 survives | 0.142 [0.035, 0.258], 0.0228 survives |
| revisits | cnp | 0.168 | 0.168 | 0.172 [0.07, 0.273], 0.0084 survives | 0.111 [0.015, 0.211], 0.0558 survives | 0.153 [0.045, 0.264], 0.0205 survives |
| revisits | fwci | 0.171 | 0.171 | 0.168 [0.067, 0.268], 0.008 survives | 0.111 [0.017, 0.211], 0.0559 survives | 0.148 [0.04, 0.261], 0.0228 survives |
| revisits | breadth_citers (not normalized) | -0.272 | -0.272 | -0.19 [-0.386, 0.027], 0.0915 survives, CI spans 0 | -0.277 [-0.477, -0.07], 0.0218 survives | -0.197 [-0.429, 0.06], 0.1188 does not survive |
| steps | cnp | 0.174 | 0.174 | 0.175 [0.074, 0.279], 0.0071 survives | 0.109 [0.007, 0.212], 0.0583 survives | 0.139 [0.036, 0.248], 0.0263 survives |
| steps | fwci | 0.178 | 0.178 | 0.171 [0.068, 0.276], 0.0071 survives | 0.11 [0.013, 0.214], 0.057 survives | 0.135 [0.024, 0.248], 0.0308 survives |
| steps | breadth_refs (not normalized) | -0.137 | -0.137 | -0.109 [-0.218, 0.003], 0.0609 survives, CI spans 0 | -0.141 [-0.241, -0.031], 0.0202 survives | -0.139 [-0.246, -0.032], 0.027 survives |
| steps | breadth_citers (not normalized) | -0.263 | -0.263 | -0.158 [-0.373, 0.073], 0.1501 does not survive | -0.262 [-0.456, -0.046], 0.0308 survives | -0.168 [-0.424, 0.085], 0.1614 does not survive |

"Survives" means the association keeps its sign and has q < 0.1 within strata. "CI spans 0" marks a survivor whose stratified bootstrap interval includes 0: weakened, not removed.

## 6. What the OpenAlex subfields hold

Leading topics and ring per subfield. Core ring: the convenor's 8 OpenAlex topics; broad ring: 8 Earth-science subfields (DECISIONS.md, g02). A subfield named for another discipline can hold geoscience topics: OpenAlex files the topic, not the paper.

| Subfield | Pool n | Round 1 preselected n (ring) | Top topics, round 1 preselected | Coded n | Top topic, coded |
|:--|--:|:--|:--|--:|:--|
| Geophysics | 3822 | 180 (core 136, broad 44) | earthquake and tectonic studies 62; Geological and Geochemical Analysis 36; Seismic Waves and Analysis 31 | 206 | earthquake and tectonic studies 71 (34%) |
| Atmospheric Science | 4170 | 125 (core 81, broad 44) | Cryospheric studies and observations 81; Meteorological Phenomena and Simulations 11; Geology and Paleoclimatology Research 11 | 171 | Cryospheric studies and observations 98 (57%) |
| Artificial Intelligence | 114 | 64 (core 64) | Seismology and Earthquake Studies 64 | 25 | Seismology and Earthquake Studies 25 (100%) |
| Oceanography | 2209 | 45 (broad 45) | Marine and coastal ecosystems 15; Oceanographic and Atmospheric Processes 14; Marine Biology and Ecology Research 6 | 42 | Oceanographic and Atmospheric Processes 17 (40%) |
| Geochemistry and Petrology | 580 | 44 (broad 44) | Groundwater and Isotope Geochemistry 20; Geochemistry and Elemental Analysis 16; Geological Modeling and Analysis 4 | 37 | Groundwater and Isotope Geochemistry 18 (49%) |
| Water Science and Technology | 1856 | 44 (broad 44) | Hydrology and Watershed Management Studies 14; Advanced oxidation water treatment 4; Adsorption and biosorption for pollutant removal 4 | 26 | Hydrology and Watershed Management Studies 20 (77%) |
| Earth-Surface Processes | 922 | 43 (broad 43) | Geological formations and processes 19; Coastal and Marine Dynamics 12; Karst Systems and Hydrogeology 5 | 40 | Geological formations and processes 18 (45%) |
| Geology | 526 | 32 (broad 32) | Geological and Geophysical Studies 22; Geological Studies and Exploration 4; Geotourism and Geoheritage Conservation 4 | 19 | Geological and Geophysical Studies 16 (84%) |
| Ocean Engineering | 20 | 19 (core 19) | Geophysics and Sensor Technology 19 | 6 | Geophysics and Sensor Technology 6 (100%) |
| Space and Planetary Science | 4 | 4 (broad 4) | Archaeological Research and Protection 4 | 0 |  |

Machine-learning vocabulary in the codings (coded papers): Geophysics 20 of 206 anywhere, 8 in an N step; Atmospheric Science 16 of 171 anywhere, 9 in an N step; Oceanography 4 of 42 anywhere, 1 in an N step; Earth-Surface Processes 1 of 40 anywhere, 0 in an N step; Geochemistry and Petrology 3 of 37 anywhere, 0 in an N step; Water Science and Technology 3 of 26 anywhere, 1 in an N step; Artificial Intelligence 20 of 25 anywhere, 11 in an N step; Geology 0 of 19 anywhere, 0 in an N step; Ocean Engineering 0 of 6 anywhere, 0 in an N step.

