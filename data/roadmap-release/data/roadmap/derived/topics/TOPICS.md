# Paper topics and journals in the roadmap corpus

Run on 2 round(s). Coded papers at run time: round 1 233 (tag calc1), round 2 0 (tag r2, folder absent). Pool frame 14223 papers. Script tools/roadmap/g20_topics_journals.py; all numbers in topics_journals.json beside this file.

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
| round1 | coded | 233 | 94 | 0.0365 | 27.4 | 0.326 | 38 |
| round2 | drawn | 277 | 157 | 0.009 | 111.0 | 0.072 | 47 |
| round2 | eligible | 222 | 123 | 0.0113 | 88.3 | 0.09 | 32 |
| round2 | full_text | 202 | 114 | 0.0122 | 82.3 | 0.099 | 30 |
| pooled | drawn | 877 | 253 | 0.013 | 77.2 | 0.185 | 63 |
| pooled | eligible | 747 | 195 | 0.0157 | 63.8 | 0.21 | 46 |
| pooled | full_text | 581 | 178 | 0.0159 | 62.8 | 0.208 | 45 |
| pooled | coded | 233 | 94 | 0.0365 | 27.4 | 0.326 | 38 |

### Field by stage

| field | pool share | round 1 drawn | round 1 eligible | round 1 full_text | round 1 coded | round 2 drawn | round 2 eligible |
|:--|--:|--:|--:|--:|--:|--:|--:|
| Earth and Planetary Sciences | 0.860 | 473 | 429 | 329 | 198 | 245 | 211 |
| Environmental Science | 0.130 | 44 | 19 | 17 | 14 | 30 | 9 |
| Computer Science | 0.008 | 64 | 61 | 27 | 17 | 2 | 2 |
| Engineering | 0.001 | 19 | 16 | 6 | 4 | 0 | 0 |

### Subfield by stage

| subfield | pool share | round 1 drawn | round 1 eligible | round 1 full_text | round 1 coded | round 2 drawn | round 2 eligible |
|:--|--:|--:|--:|--:|--:|--:|--:|
| Atmospheric Science | 0.293 | 125 | 119 | 109 | 74 | 75 | 68 |
| Geophysics | 0.269 | 180 | 173 | 112 | 64 | 118 | 108 |
| Oceanography | 0.155 | 45 | 31 | 23 | 10 | 34 | 22 |
| Water Science and Technology | 0.130 | 44 | 19 | 17 | 14 | 30 | 9 |
| Earth-Surface Processes | 0.065 | 43 | 42 | 37 | 26 | 6 | 3 |
| Geochemistry and Petrology | 0.041 | 44 | 37 | 29 | 15 | 10 | 8 |
| Geology | 0.037 | 32 | 27 | 19 | 9 | 2 | 2 |
| Artificial Intelligence | 0.008 | 64 | 61 | 27 | 17 | 2 | 2 |
| Ocean Engineering | 0.001 | 19 | 16 | 6 | 4 | 0 | 0 |
| Space and Planetary Science | 0.000 | 4 | 0 | 0 | 0 | 0 | 0 |

### Family by stage

| family | pool share | round 1 drawn | round 1 eligible | round 1 full_text | round 1 coded | round 2 drawn | round 2 eligible |
|:--|--:|--:|--:|--:|--:|--:|--:|
| AGU | 0.235 | 99 | 98 | 98 | 16 | 32 | 30 |
| Elsevier | 0.225 | 94 | 74 | 72 | 9 | 42 | 30 |
| Wiley non-AGU | 0.144 | 92 | 79 | 77 | 76 | 30 | 24 |
| EGU/Copernicus | 0.132 | 64 | 64 | 64 | 64 | 42 | 40 |
| Springer Nature (non-portfolio) | 0.120 | 139 | 110 | 44 | 44 | 79 | 57 |
| Nature portfolio | 0.082 | 21 | 14 | 14 | 14 | 31 | 22 |
| Oxford | 0.030 | 34 | 34 | 6 | 6 | 4 | 4 |
| SSA | 0.022 | 50 | 46 | 2 | 2 | 8 | 6 |
| other | 0.005 | 5 | 5 | 1 | 1 | 5 | 5 |
| AAAS | 0.005 | 2 | 1 | 1 | 1 | 4 | 4 |

Pool column is a share; other columns are counts.

### Most frequent journals (coded, all rounds)

| Journal | Papers | Share |
|:--|--:|--:|
| The cryosphere | 33 | 0.142 |
| Earth Planets and Space | 13 | 0.056 |
| Geophysical Prospecting | 13 | 0.056 |
| Geological Journal | 9 | 0.039 |
| Scientific Reports | 8 | 0.034 |
| Geophysical Journal International | 6 | 0.026 |
| Geoscientific model development | 5 | 0.021 |
| Basin Research | 5 | 0.021 |
| Hydrological Processes | 5 | 0.021 |
| Earth Surface Processes and Landforms | 4 | 0.017 |
| Natural hazards and earth system sciences | 4 | 0.017 |
| Hydrology and earth system sciences | 4 | 0.017 |
| Biogeosciences | 4 | 0.017 |
| Communications Earth & Environment | 4 | 0.017 |
| Terra Nova | 4 | 0.017 |

### Most frequent leading topics (coded, all rounds) and their share at earlier stages

| Topic | Coded papers | Coded share | Pool share | Round 1 preselected share | Round 1 eligible share | Round 1 full-text share |
|:--|--:|--:|--:|--:|--:|--:|
| Cryospheric studies and observations | 53 | 0.227 | 0.039 | 0.135 | 0.149 | 0.19 |
| Seismology and Earthquake Studies | 17 | 0.073 | <top 15 | 0.107 | 0.116 | 0.071 |
| Seismic Imaging and Inversion Techniques | 17 | 0.073 | 0.02 | 0.042 | 0.046 | 0.055 |
| earthquake and tectonic studies | 14 | 0.06 | 0.07 | 0.103 | 0.116 | 0.095 |
| Geological and Geochemical Analysis | 12 | 0.052 | 0.101 | 0.06 | 0.065 | 0.058 |
| Seismic Waves and Analysis | 12 | 0.052 | 0.029 | 0.052 | 0.057 | 0.053 |
| Geological formations and processes | 12 | 0.052 | 0.025 | 0.032 | 0.036 | 0.045 |
| Hydrology and Watershed Management Studies | 11 | 0.047 | 0.044 | 0.023 | 0.027 | 0.034 |
| Geological and Geophysical Studies | 7 | 0.03 | 0.026 | 0.037 | 0.038 | 0.04 |
| Geochemistry and Elemental Analysis | 7 | 0.03 | <top 15 | 0.027 | 0.027 | 0.024 |
| Marine and coastal ecosystems | 6 | 0.026 | 0.051 | 0.025 | 0.023 | 0.026 |
| Aeolian processes and effects | 5 | 0.021 | <top 15 | <top 15 | <top 15 | <top 15 |
| Meteorological Phenomena and Simulations | 5 | 0.021 | 0.055 | <top 15 | <top 15 | 0.026 |
| Coastal and Marine Dynamics | 5 | 0.021 | 0.02 | <top 15 | <top 15 | 0.024 |
| Geology and Paleoclimatology Research | 5 | 0.021 | 0.05 | <top 15 | <top 15 | 0.026 |

## 2. Coverage bias

Among eligible papers, is reaching full text, or being coded, associated with field or venue? Categories with fewer than 10 eligible papers are pooled into "pooled small groups".

| Set | Response | Variable | n | Overall rate | Cramer's V, bias-corrected [95% CI] | p | q | Largest rate difference (category) |
|:--|:--|:--|--:|--:|:--|--:|--:|:--|
| round1 | full_text_among_eligible | subfield | 525 | 0.722 | 0.342 [0.28, 0.438] | 0.0002 | 0.0003 | -0.36 [-0.606, -0.094] (Ocean Engineering, n=16) |
| round1 | full_text_among_eligible | field | 525 | 0.722 | 0.267 [0.179, 0.367] | 0.0002 | 0.0003 | -0.36 [-0.606, -0.103] (Engineering, n=16) |
| round1 | full_text_among_eligible | family | 525 | 0.722 | 0.788 [0.745, 0.835] | 0.0002 | 0.0003 | -0.74 [-0.806, -0.665] (SSA, n=46) |
| round1 | full_text_among_eligible | publisher | 525 | 0.722 | 0.803 [0.758, 0.854] | 0.0002 | 0.0003 | -0.72 [-0.791, -0.638] (Seismological Research Letters, n=28) |
| round1 | coded_among_eligible | subfield | 525 | 0.444 | 0.26 [0.193, 0.364] | 0.0002 | 0.0003 | +0.30 [0.08, 0.488] (Water Science and Technology, n=19) |
| round1 | coded_among_eligible | field | 525 | 0.444 | 0.159 [0.081, 0.249] | 0.0008 | 0.0011 | +0.30 [0.092, 0.506] (Environmental Science, n=19) |
| round1 | coded_among_eligible | family | 525 | 0.444 | 0.73 [0.688, 0.781] | 0.0002 | 0.0003 | +0.63 [0.59, 0.677] (EGU/Copernicus, n=64) |
| round1 | coded_among_eligible | publisher | 525 | 0.444 | 0.66 [0.612, 0.721] | 0.0002 | 0.0003 | +0.63 [0.585, 0.676] (Copernicus, n=62) |
| round1 | coded_among_full_text | subfield | 379 | 0.615 | 0.116 [0.0, 0.281] | 0.106 | 0.1305 | +0.22 [-0.005, 0.39] (Water Science and Technology, n=17) |
| round1 | coded_among_full_text | field | 379 | 0.615 | 0.034 [0.0, 0.17] | 0.3365 | 0.3846 | +0.22 [0.006, 0.399] (Environmental Science, n=17) |
| round1 | coded_among_full_text | family | 379 | 0.615 | 0.859 [0.812, 0.906] | 0.0002 | 0.0003 | -0.61 [-0.694, -0.516] (AGU, n=98) |
| round1 | coded_among_full_text | publisher | 379 | 0.615 | 0.717 [0.661, 0.771] | 0.0002 | 0.0003 | -0.61 [-0.692, -0.51] (AGU, n=41) |
| round2 | full_text_among_eligible | subfield | 222 | 0.91 | 0.0 [0.0, 0.183] | 0.7151 | 0.7628 | +0.05 [-0.062, 0.128] (Oceanography, n=22) |
| round2 | full_text_among_eligible | field | 222 | 0.91 | 0.0 [0.0, 0.147] | 1.0 | 1.0 | +0.00 [-0.122, 0.209] (Earth and Planetary Sciences, n=211) |
| round2 | full_text_among_eligible | family | 222 | 0.91 | 0.531 [0.354, 0.712] | 0.0002 | 0.0003 | -0.54 [-0.761, -0.298] (pooled small groups, n=19) |
| round2 | full_text_among_eligible | publisher | 222 | 0.91 | 0.487 [0.313, 0.674] | 0.0002 | 0.0003 | -0.51 [-0.742, -0.282] (pooled small groups, n=18) |
| round2 | coded_among_eligible | (skipped: response constant (no codings or all coded)) | 222 | | | | | |
| round2 | coded_among_full_text | (skipped: response constant (no codings or all coded)) | 202 | | | | | |

## 3. Workflows by field and venue

233 coded papers, rounds pooled. 104 tests, 28 with q < 0.1.

- subfield: groups Atmospheric Science (74), Geophysics (64), Earth-Surface Processes (26), Artificial Intelligence (17), Geochemistry and Petrology (15), Water Science and Technology (14), pooled small groups (13), Oceanography (10); pooled into "pooled small groups": Geology (9), Ocean Engineering (4)
- family: groups Wiley non-AGU (76), EGU/Copernicus (64), Springer Nature (non-portfolio) (44), pooled small groups (19), AGU (16), Nature portfolio (14); pooled into "pooled small groups": AAAS (1), Elsevier (9), Oxford (6), SSA (2), other (1)

Tests with q < 0.1. Effect: bias-corrected Cramer's V for binary and categorical features, epsilon squared for counts.

| Grouping | Feature | Kind | Effect [95% CI] | p | q | Largest rate difference or group medians |
|:--|:--|:--|:--|--:|--:|:--|
| subfield | decisive reconstruction | binary | V 0.355 [0.206, 0.538] | 0.0002 | 0.0035 | +0.35 [0.177, 0.566] (Earth-Surface Processes, rate 0.423, n=26) |
| subfield | mode reconstruction | binary | V 0.332 [0.242, 0.477] | 0.0002 | 0.0035 | +0.37 [0.173, 0.578] (Earth-Surface Processes, rate 0.615, n=26) |
| subfield | mode methods | binary | V 0.323 [0.212, 0.489] | 0.0004 | 0.0052 | -0.37 [-0.566, -0.164] (Earth-Surface Processes, rate 0.423, n=26) |
| subfield | composition trace_series | binary | V 0.309 [0.217, 0.465] | 0.0002 | 0.0035 | +0.34 [0.145, 0.536] (Earth-Surface Processes, rate 0.538, n=26) |
| subfield | decisive methods | binary | V 0.294 [0.191, 0.449] | 0.0002 | 0.0035 | +0.51 [0.284, 0.704] (Artificial Intelligence, rate 0.765, n=17) |
| family | mode simulation | binary | V 0.287 [0.181, 0.429] | 0.0004 | 0.0052 | -0.33 [-0.47, -0.182] (Springer Nature (non-portfolio), rate 0.227, n=44) |
| subfield | node I infer | binary | V 0.283 [0.155, 0.448] | 0.001 | 0.008 | -0.46 [-0.715, -0.152] (pooled small groups, rate 0.385, n=13) |
| subfield | node N new capability | binary | V 0.278 [0.188, 0.427] | 0.0008 | 0.0069 | +0.33 [0.148, 0.479] (Artificial Intelligence, rate 0.882, n=17) |
| subfield | mode estimation | binary | V 0.241 [0.124, 0.411] | 0.0054 | 0.0324 | -0.47 [-0.732, -0.181] (pooled small groups, rate 0.308, n=13) |
| family | node N new capability | binary | V 0.24 [0.135, 0.384] | 0.002 | 0.013 | +0.32 [0.116, 0.477] (AGU, rate 0.875, n=16) |
| family | node P protect | binary | V 0.238 [0.115, 0.395] | 0.0014 | 0.0104 | +0.24 [0.098, 0.378] (EGU/Copernicus, rate 0.516, n=64) |
| family | mode methods | binary | V 0.221 [0.118, 0.371] | 0.0072 | 0.0374 | +0.27 [0.21, 0.327] (AGU, rate 1.0, n=16) |
| subfield | mode simulation | binary | V 0.213 [0.118, 0.386] | 0.0118 | 0.0534 | -0.24 [-0.47, 0.002] (Geochemistry and Petrology, rate 0.267, n=15) |
| subfield | node D design | binary | V 0.213 [0.108, 0.399] | 0.0158 | 0.0647 | -0.39 [-0.636, -0.132] (Geochemistry and Petrology, rate 0.333, n=15) |
| family | composition trace_series | binary | V 0.203 [0.107, 0.361] | 0.0154 | 0.0647 | -0.25 [-0.312, -0.196] (AGU, rate 0.0, n=16) |
| family | decisive reconstruction | binary | V 0.199 [0.121, 0.336] | 0.0162 | 0.0647 | +0.13 [0.041, 0.234] (Wiley non-AGU, rate 0.197, n=76) |
| family | composition capability_first | binary | V 0.198 [0.032, 0.4] | 0.0168 | 0.0647 | +0.26 [0.013, 0.508] (AGU, rate 0.375, n=16) |
| subfield | node P protect | binary | V 0.194 [0.104, 0.371] | 0.0246 | 0.0914 | -0.28 [-0.405, -0.109] (Water Science and Technology, rate 0.071, n=14) |
| subfield | decisive (whole variable) | categorical | V 0.17 [0.17, 0.297] | 0.0008 | 0.0069 |  |
| subfield | composition (whole variable) | categorical | V 0.153 [0.146, 0.309] | 0.0098 | 0.0463 |  |
| family | steps | count | eps2 0.149 [0.082, 0.257] | 0.0002 | 0.0035 | AGU 24.5, EGU/Copernicus 24, Nature portfolio 22.5, Springer Nature (non-portfolio) 22, pooled small groups 21, Wiley non-AGU 19.5 |
| family | revisits | count | eps2 0.114 [0.059, 0.221] | 0.0002 | 0.0035 | AGU 14, EGU/Copernicus 13, Nature portfolio 12, Springer Nature (non-portfolio) 12, pooled small groups 11, Wiley non-AGU 10 |
| subfield | V check kinds | count | eps2 0.113 [0.067, 0.22] | 0.0006 | 0.0069 | Artificial Intelligence 4, Atmospheric Science 3, Geophysics 3, Oceanography 3, Water Science and Technology 2.5, Earth-Surface Processes 2, Geochemistry and Petrology 2, pooled small groups 2 |
| family | V check kinds | count | eps2 0.093 [0.049, 0.194] | 0.0008 | 0.0069 | AGU 3, EGU/Copernicus 3, Nature portfolio 3, Springer Nature (non-portfolio) 3, pooled small groups 3, Wiley non-AGU 2 |
| family | distinct nodes | count | eps2 0.081 [0.041, 0.182] | 0.0016 | 0.0111 | AGU 11, EGU/Copernicus 11, pooled small groups 11, Nature portfolio 10, Springer Nature (non-portfolio) 10, Wiley non-AGU 10 |
| family | imports | count | eps2 0.071 [0.034, 0.172] | 0.0056 | 0.0324 | Nature portfolio 4.5, EGU/Copernicus 4, Springer Nature (non-portfolio) 4, pooled small groups 4, AGU 3, Wiley non-AGU 3 |
| family | distinct modes | count | eps2 0.068 [0.031, 0.156] | 0.006 | 0.0328 | AGU 8.5, Nature portfolio 8.5, EGU/Copernicus 7, Springer Nature (non-portfolio) 7, Wiley non-AGU 7, pooled small groups 6 |
| family | import fields | count | eps2 0.064 [0.028, 0.153] | 0.0094 | 0.0463 | Springer Nature (non-portfolio) 4, pooled small groups 4, Nature portfolio 3.5, AGU 3, EGU/Copernicus 3, Wiley non-AGU 3 |

## 4. Outcomes by field and venue

Median per group [95% bootstrap CI]. Last row: Kruskal-Wallis epsilon squared [95% CI] and BH q. cnp and fwci are subfield-normalized by OpenAlex; novelty_pair and breadth_refs are not.

### Coded papers by subfield

| subfield | n | cnp | fwci | novelty_pair | breadth_refs |
|:--|--:|:--|:--|:--|:--|
| Atmospheric Science | 74 | 0.587 [0.525, 0.675] | 0.664 [0.475, 0.949] | -3.827 [-4.155, -3.497] | 0.019 [0.012, 0.033] |
| Geophysics | 64 | 0.399 [0.33, 0.516] | 0.289 [0.144, 0.578] | -4.099 [-4.118, -3.868] | 0.038 [0.028, 0.065] |
| Earth-Surface Processes | 26 | 0.578 [0.461, 0.789] | 0.664 [0.331, 1.49] | -3.509 [-3.704, -3.362] | 0.036 [0.01, 0.066] |
| Artificial Intelligence | 17 | 0.687 [0.548, 0.817] | 0.643 [0.322, 1.366] | -3.711 [-3.711, -3.161] | 0.265 [0.195, 0.356] |
| Geochemistry and Petrology | 15 | 0.397 [0.374, 0.609] | 0.148 [0.148, 0.592] | -3.776 [-4.157, -3.366] | 0.023 [0.0, 0.116] |
| Water Science and Technology | 14 | 0.555 [0.325, 0.777] | 0.486 [0.069, 1.385] | -3.792 [-4.172, -3.513] | 0.03 [0.017, 0.077] |
| pooled small groups | 13 | 0.557 [0.131, 0.662] | 0.418 [0.0, 0.748] | -3.821 [-4.31, -3.079] | 0.064 [0.0, 0.148] |
| Oceanography | 10 | 0.566 [0.068, 0.755] | 0.603 [0.0, 1.51] | -4.302 [-4.312, -3.77] | 0.048 [0.013, 0.087] |
| all | 233 | 0.546 | 0.482 | -3.821 | 0.033 |
| eps2, q | | 0.084 [0.047, 0.196], q 0.0087 | 0.077 [0.043, 0.182], q 0.014 | 0.107 [0.069, 0.208], q 0.001 | 0.117 [0.068, 0.23], q 0.0004 |

### Coded papers by family

| family | n | cnp | fwci | novelty_pair | breadth_refs |
|:--|--:|:--|:--|:--|:--|
| Wiley non-AGU | 76 | 0.433 [0.37, 0.525] | 0.292 [0.148, 0.475] | -3.846 [-4.118, -3.666] | 0.027 [0.017, 0.047] |
| EGU/Copernicus | 64 | 0.646 [0.567, 0.728] | 0.782 [0.592, 1.159] | -3.847 [-4.172, -3.607] | 0.03 [0.018, 0.046] |
| Springer Nature (non-portfolio) | 44 | 0.479 [0.332, 0.595] | 0.399 [0.145, 0.58] | -3.768 [-3.886, -3.366] | 0.064 [0.028, 0.087] |
| pooled small groups | 19 | 0.571 [0.353, 0.797] | 0.402 [0.148, 1.49] | -3.711 [-4.238, -3.081] | 0.04 [0.026, 0.233] |
| AGU | 16 | 0.802 [0.606, 0.923] | 1.431 [0.418, 2.898] | -3.924 [-4.118, -3.411] | 0.026 [0.014, 0.093] |
| Nature portfolio | 14 | 0.604 [0.548, 0.798] | 0.741 [0.323, 1.516] | -3.803 [-4.238, -3.543] | 0.036 [0.0, 0.155] |
| all | 233 | 0.546 | 0.482 | -3.821 | 0.033 |
| eps2, q | | 0.129 [0.072, 0.237], q 0.0004 | 0.134 [0.075, 0.242], q 0.0004 | 0.014 [0.006, 0.08], q 0.6549 | 0.028 [0.012, 0.104], q 0.313 |

### Eligible papers by subfield

| subfield | n | cnp | fwci | novelty_pair | breadth_refs |
|:--|--:|:--|:--|:--|:--|
| Geophysics | 281 | 0.407 [0.39, 0.497] | 0.29 [0.289, 0.435] | -3.934 [-4.082, -3.887] | 0.033 [0.028, 0.041] |
| Atmospheric Science | 187 | 0.565 [0.49, 0.634] | 0.663 [0.474, 0.806] | -3.847 [-3.992, -3.781] | 0.02 [0.016, 0.029] |
| Artificial Intelligence | 63 | 0.688 [0.58, 0.763] | 0.647 [0.402, 0.965] | -3.711 [-3.711, -3.711] | 0.211 [0.116, 0.259] |
| Oceanography | 53 | 0.525 [0.333, 0.607] | 0.483 [0.121, 0.723] | -3.971 [-4.269, -3.77] | 0.026 [0.016, 0.042] |
| Earth-Surface Processes | 45 | 0.494 [0.383, 0.639] | 0.332 [0.166, 0.829] | -3.748 [-3.989, -3.509] | 0.014 [0.0, 0.047] |
| Geochemistry and Petrology | 45 | 0.536 [0.388, 0.648] | 0.443 [0.148, 0.74] | -3.554 [-3.788, -3.342] | 0.045 [0.022, 0.072] |
| Geology | 29 | 0.606 [0.526, 0.783] | 0.419 [0.21, 1.463] | -4.296 [-4.31, -4.137] | 0.01 [0.0, 0.029] |
| Water Science and Technology | 28 | 0.51 [0.326, 0.588] | 0.381 [0.069, 0.623] | -3.797 [-4.126, -3.606] | 0.045 [0.024, 0.08] |
| Ocean Engineering | 16 | 0.473 [0.352, 0.634] | 0.299 [0.12, 0.718] | -3.186 [-3.552, -2.972] | 0.167 [0.057, 0.227] |
| all | 747 | 0.525 | 0.435 | -3.847 | 0.033 |
| eps2, q | | 0.045 [0.029, 0.087], q 0.0004 | 0.028 [0.017, 0.065], q 0.0099 | 0.096 [0.069, 0.143], q 0.0004 | 0.105 [0.07, 0.162], q 0.0004 |

### Eligible papers by family

| family | n | cnp | fwci | novelty_pair | breadth_refs |
|:--|--:|:--|:--|:--|:--|
| Springer Nature (non-portfolio) | 167 | 0.38 [0.333, 0.446] | 0.166 [0.145, 0.289] | -3.886 [-3.916, -3.781] | 0.033 [0.02, 0.047] |
| AGU | 128 | 0.635 [0.546, 0.73] | 0.759 [0.566, 1.159] | -3.844 [-4.021, -3.711] | 0.021 [0.017, 0.03] |
| EGU/Copernicus | 104 | 0.589 [0.547, 0.703] | 0.664 [0.555, 1.028] | -3.847 [-4.082, -3.77] | 0.035 [0.025, 0.049] |
| Elsevier | 104 | 0.546 [0.451, 0.68] | 0.578 [0.289, 0.804] | -3.911 [-4.07, -3.788] | 0.028 [0.018, 0.04] |
| Wiley non-AGU | 103 | 0.431 [0.374, 0.519] | 0.289 [0.148, 0.474] | -3.806 [-4.073, -3.686] | 0.031 [0.022, 0.049] |
| SSA | 52 | 0.541 [0.475, 0.606] | 0.434 [0.322, 0.722] | -3.711 [-3.723, -3.711] | 0.089 [0.055, 0.211] |
| Oxford | 38 | 0.401 [0.092, 0.591] | 0.289 [0.0, 0.683] | -3.82 [-3.886, -3.487] | 0.129 [0.088, 0.185] |
| Nature portfolio | 36 | 0.713 [0.58, 0.791] | 1.147 [0.722, 1.516] | -3.886 [-4.108, -3.711] | 0.03 [0.016, 0.048] |
| other | 10 | 0.517 [0.087, 0.698] | 0.438 [0.0, 1.011] | -3.936 [-4.371, -3.552] | 0.044 [0.028, 0.107] |
| pooled small groups | 5 | 0.884 [0.571, 0.978] | 2.311 [0.722, 5.126] | -3.847 [-4.544, -3.375] | 0.029 [0.0, 0.108] |
| all | 747 | 0.525 | 0.435 | -3.847 | 0.033 |
| eps2, q | | 0.104 [0.075, 0.16], q 0.0004 | 0.113 [0.082, 0.169], q 0.0004 | 0.013 [0.009, 0.044], q 0.4221 | 0.048 [0.029, 0.095], q 0.0004 |

## 5. Are the g17 workflow-outcome associations explained by field or venue?

15 g17 tests with q < 0.1 (round 1, tools/roadmap/g17_outcomes.py output) rechecked on the 233 round-1 papers coded now. Survivors (same sign, q < 0.1 over the 45 stratified tests): subfield 15/15, family 15/15, subfield x family 12/15; of these, with a bootstrap interval that excludes 0: subfield 14, family 12, subfield x family 8.

| Feature | Outcome | g17 rho | rho now | within subfield [CI], q | within family [CI], q | within subfield x family [CI], q |
|:--|:--|--:|--:|:--|:--|:--|
| composition capability_first | breadth_refs (not normalized) | 0.217 | 0.217 | 0.137 [-0.004, 0.272], 0.0475 survives, CI spans 0 | 0.193 [0.056, 0.326], 0.0067 survives | 0.134 [-0.04, 0.279], 0.077 survives, CI spans 0 |
| decisive methods | breadth_refs (not normalized) | 0.223 | 0.223 | 0.157 [0.008, 0.289], 0.0244 survives | 0.2 [0.059, 0.322], 0.0084 survives | 0.18 [0.022, 0.321], 0.0233 survives |
| decisive simulation | cnp | 0.202 | 0.202 | 0.186 [0.053, 0.306], 0.0129 survives | 0.174 [0.052, 0.293], 0.0139 survives | 0.141 [0.003, 0.285], 0.0659 survives |
| decisive simulation | fwci | 0.211 | 0.211 | 0.182 [0.059, 0.299], 0.0129 survives | 0.179 [0.048, 0.293], 0.0139 survives | 0.132 [-0.019, 0.271], 0.0764 survives, CI spans 0 |
| mode observation | novelty_pair (not normalized) | 0.207 | 0.207 | 0.157 [0.026, 0.282], 0.0244 survives | 0.191 [0.062, 0.311], 0.0129 survives | 0.126 [-0.037, 0.267], 0.077 survives, CI spans 0 |
| mode synthesis | breadth_refs (not normalized) | -0.222 | -0.222 | -0.188 [-0.306, -0.044], 0.0129 survives | -0.209 [-0.333, -0.081], 0.0084 survives | -0.21 [-0.335, -0.061], 0.0129 survives |
| node I infer | breadth_refs (not normalized) | -0.181 | -0.181 | -0.164 [-0.292, -0.03], 0.0212 survives | -0.2 [-0.327, -0.063], 0.0069 survives | -0.211 [-0.333, -0.037], 0.0131 survives |
| V check kinds | breadth_refs (not normalized) | 0.201 | 0.201 | 0.164 [0.023, 0.301], 0.0212 survives | 0.172 [0.04, 0.295], 0.0166 survives | 0.162 [0.028, 0.306], 0.047 survives |
| distinct modes | breadth_refs (not normalized) | -0.224 | -0.224 | -0.174 [-0.295, -0.049], 0.0204 survives | -0.235 [-0.354, -0.106], 0.005 survives | -0.21 [-0.325, -0.039], 0.0129 survives |
| import fields | breadth_refs (not normalized) | 0.512 | 0.512 | 0.484 [0.375, 0.587], 0.0015 survives | 0.519 [0.416, 0.618], 0.0015 survives | 0.522 [0.416, 0.626], 0.0015 survives |
| imports | breadth_refs (not normalized) | 0.566 | 0.566 | 0.523 [0.406, 0.628], 0.0015 survives | 0.573 [0.471, 0.669], 0.0015 survives | 0.563 [0.452, 0.663], 0.0015 survives |
| revisits | cnp | 0.211 | 0.211 | 0.224 [0.104, 0.346], 0.005 survives | 0.121 [-0.002, 0.248], 0.0783 survives, CI spans 0 | 0.127 [-0.018, 0.265], 0.0932 survives, CI spans 0 |
| revisits | fwci | 0.217 | 0.217 | 0.218 [0.095, 0.344], 0.0063 survives | 0.124 [0.001, 0.25], 0.077 survives | 0.12 [-0.028, 0.264], 0.1038 does not survive |
| steps | cnp | 0.227 | 0.227 | 0.225 [0.097, 0.352], 0.005 survives | 0.12 [-0.0, 0.251], 0.0852 survives, CI spans 0 | 0.107 [-0.031, 0.258], 0.1424 does not survive |
| steps | fwci | 0.23 | 0.23 | 0.218 [0.094, 0.336], 0.0065 survives | 0.121 [-0.011, 0.243], 0.0783 survives, CI spans 0 | 0.102 [-0.037, 0.244], 0.151 does not survive |

"Survives" means the association keeps its sign and has q < 0.1 within strata. "CI spans 0" marks a survivor whose stratified bootstrap interval includes 0: weakened, not removed.

## 6. What the OpenAlex subfields hold

Leading topics and ring per subfield. Core ring: the convenor's 8 OpenAlex topics; broad ring: 8 Earth-science subfields (DECISIONS.md, g02). A subfield named for another discipline can hold geoscience topics: OpenAlex files the topic, not the paper.

| Subfield | Pool n | Round 1 preselected n (ring) | Top topics, round 1 preselected | Coded n | Top topic, coded |
|:--|--:|:--|:--|--:|:--|
| Geophysics | 3822 | 180 (core 136, broad 44) | earthquake and tectonic studies 62; Geological and Geochemical Analysis 36; Seismic Waves and Analysis 31 | 64 | Seismic Imaging and Inversion Techniques 17 (27%) |
| Atmospheric Science | 4170 | 125 (core 81, broad 44) | Cryospheric studies and observations 81; Meteorological Phenomena and Simulations 11; Geology and Paleoclimatology Research 11 | 74 | Cryospheric studies and observations 53 (72%) |
| Artificial Intelligence | 114 | 64 (core 64) | Seismology and Earthquake Studies 64 | 17 | Seismology and Earthquake Studies 17 (100%) |
| Oceanography | 2209 | 45 (broad 45) | Marine and coastal ecosystems 15; Oceanographic and Atmospheric Processes 14; Marine Biology and Ecology Research 6 | 10 | Marine and coastal ecosystems 6 (60%) |
| Geochemistry and Petrology | 580 | 44 (broad 44) | Groundwater and Isotope Geochemistry 20; Geochemistry and Elemental Analysis 16; Geological Modeling and Analysis 4 | 15 | Geochemistry and Elemental Analysis 7 (47%) |
| Water Science and Technology | 1856 | 44 (broad 44) | Hydrology and Watershed Management Studies 14; Advanced oxidation water treatment 4; Adsorption and biosorption for pollutant removal 4 | 14 | Hydrology and Watershed Management Studies 11 (79%) |
| Earth-Surface Processes | 922 | 43 (broad 43) | Geological formations and processes 19; Coastal and Marine Dynamics 12; Karst Systems and Hydrogeology 5 | 26 | Geological formations and processes 12 (46%) |
| Geology | 526 | 32 (broad 32) | Geological and Geophysical Studies 22; Geological Studies and Exploration 4; Geotourism and Geoheritage Conservation 4 | 9 | Geological and Geophysical Studies 7 (78%) |
| Ocean Engineering | 20 | 19 (core 19) | Geophysics and Sensor Technology 19 | 4 | Geophysics and Sensor Technology 4 (100%) |
| Space and Planetary Science | 4 | 4 (broad 4) | Archaeological Research and Protection 4 | 0 |  |

Machine-learning vocabulary in the codings (coded papers): Atmospheric Science 5 of 74 anywhere, 2 in an N step; Geophysics 9 of 64 anywhere, 2 in an N step; Earth-Surface Processes 1 of 26 anywhere, 0 in an N step; Artificial Intelligence 13 of 17 anywhere, 6 in an N step; Geochemistry and Petrology 1 of 15 anywhere, 0 in an N step; Water Science and Technology 1 of 14 anywhere, 0 in an N step; Oceanography 1 of 10 anywhere, 0 in an N step; Geology 0 of 9 anywhere, 0 in an N step; Ocean Engineering 0 of 4 anywhere, 0 in an N step.

