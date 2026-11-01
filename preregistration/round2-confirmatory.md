# Round 2: confirmatory test of the round-1 associations

Frozen 2026-10-27, before any round-2 coding existed; decided by the PI on October 27, 2026. Machine-readable plan: `round2-confirmatory.json`; code: `tools/roadmap/g23_confirmatory.py` (`test`).

- Round 1 (233 coded papers) is exploratory. Round 2 tests the associations below as one family of 43 tests, Benjamini-Hochberg q < 0.1, with the predicted direction.
- Both rounds are also reported pooled for description, with round as a stratum. That analysis is not part of this test.
- Data, groups, features, statistics and seed are fixed in the json `rule` field.

| id | source | association | round 1 | predicted |
|:--|:--|:--|:--|:--|
| H01 | g17 | num:import fields vs breadth_refs | rho 0.512, q 0.025 | positive |
| H02 | g17 | num:imports vs breadth_refs | rho 0.566, q 0.025 | positive |
| H03 | g17 | bin:composition capability_first vs breadth_refs | rho 0.217, q 0.027 | positive |
| H04 | g17 | bin:decisive methods vs breadth_refs | rho 0.223, q 0.027 | positive |
| H05 | g17 | bin:decisive simulation vs fwci | rho 0.211, q 0.027 | positive |
| H06 | g17 | num:distinct modes vs breadth_refs | rho -0.224, q 0.027 | negative |
| H07 | g17 | num:revisits vs cnp | rho 0.211, q 0.027 | positive |
| H08 | g17 | num:revisits vs fwci | rho 0.217, q 0.027 | positive |
| H09 | g17 | num:steps vs fwci | rho 0.23, q 0.027 | positive |
| H10 | g17 | num:steps vs cnp | rho 0.227, q 0.034 | positive |
| H11 | g17 | bin:mode synthesis vs breadth_refs | rho -0.222, q 0.04 | negative |
| H12 | g17 | bin:decisive simulation vs cnp | rho 0.202, q 0.041 | positive |
| H13 | g17 | bin:mode observation vs novelty_pair | rho 0.207, q 0.045 | positive |
| H14 | g17 | num:V check kinds vs breadth_refs | rho 0.201, q 0.045 | positive |
| H15 | g17 | bin:node I infer vs breadth_refs | rho -0.181, q 0.085 | negative |
| H16 | g20 | composition capability_first by family (binary) | effect 0.198, q 0.0647 | AGU above the rest |
| H17 | g20 | composition trace_series by family (binary) | effect 0.203, q 0.0647 | AGU below the rest |
| H18 | g20 | decisive reconstruction by family (binary) | effect 0.199, q 0.0647 | Wiley non-AGU above the rest |
| H19 | g20 | mode methods by family (binary) | effect 0.221, q 0.0374 | AGU above the rest |
| H20 | g20 | mode simulation by family (binary) | effect 0.287, q 0.0052 | Springer Nature (non-portfolio) below the rest |
| H21 | g20 | node N new capability by family (binary) | effect 0.24, q 0.013 | AGU above the rest |
| H22 | g20 | node P protect by family (binary) | effect 0.238, q 0.0104 | EGU/Copernicus above the rest |
| H23 | g20 | V check kinds by family (count) | effect 0.093, q 0.0069 | same order of group medians |
| H24 | g20 | distinct modes by family (count) | effect 0.068, q 0.0328 | same order of group medians |
| H25 | g20 | distinct nodes by family (count) | effect 0.081, q 0.0111 | same order of group medians |
| H26 | g20 | import fields by family (count) | effect 0.064, q 0.0463 | same order of group medians |
| H27 | g20 | imports by family (count) | effect 0.071, q 0.0324 | same order of group medians |
| H28 | g20 | revisits by family (count) | effect 0.114, q 0.0035 | same order of group medians |
| H29 | g20 | steps by family (count) | effect 0.149, q 0.0035 | same order of group medians |
| H30 | g20 | composition trace_series by subfield (binary) | effect 0.309, q 0.0035 | Earth-Surface Processes above the rest |
| H31 | g20 | decisive methods by subfield (binary) | effect 0.294, q 0.0035 | Artificial Intelligence above the rest |
| H32 | g20 | decisive reconstruction by subfield (binary) | effect 0.355, q 0.0035 | Earth-Surface Processes above the rest |
| H33 | g20 | mode estimation by subfield (binary) | effect 0.241, q 0.0324 | Oceanography above the rest |
| H34 | g20 | mode methods by subfield (binary) | effect 0.323, q 0.0052 | Earth-Surface Processes below the rest |
| H35 | g20 | mode reconstruction by subfield (binary) | effect 0.332, q 0.0035 | Earth-Surface Processes above the rest |
| H36 | g20 | mode simulation by subfield (binary) | effect 0.213, q 0.0534 | Geochemistry and Petrology below the rest |
| H37 | g20 | node D design by subfield (binary) | effect 0.213, q 0.0647 | Geochemistry and Petrology below the rest |
| H38 | g20 | node I infer by subfield (binary) | effect 0.283, q 0.008 | Oceanography above the rest |
| H39 | g20 | node N new capability by subfield (binary) | effect 0.278, q 0.0069 | Artificial Intelligence above the rest |
| H40 | g20 | node P protect by subfield (binary) | effect 0.194, q 0.0914 | Water Science and Technology below the rest |
| H41 | g20 | composition (whole variable) by subfield (categorical) | effect 0.153, q 0.0463 | association only |
| H42 | g20 | decisive (whole variable) by subfield (categorical) | effect 0.17, q 0.0069 | association only |
| H43 | g20 | V check kinds by subfield (count) | effect 0.113, q 0.0069 | same order of group medians |
