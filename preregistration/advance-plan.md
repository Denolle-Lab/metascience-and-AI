# Scientific advance: preregistered plan

Frozen 2026-10-28, after the pilot and before any full-run advance coding existed; decided by the PI on October 27, 2026. Machine-readable plan: `advance-plan.json`; code: `tools/roadmap/g24_advance.py` (`test`).

- Instrument: agents/advance/RUBRIC.md v1.1.0 (sha256 `9b303003d11d`), claude-opus-5-5, blinded text v1.2.1. Construct: reported warrant.
- Primary outcome: achieved versus not. achieved / (achieved + not_demonstrated + unassessable U1, U2, U3, U5); U4 reported separately; all three verdict counts reported.
- Expected achieved rate (pilot): 24 of 39 codings, Wilson 95% [0.459, 0.751].
- One family of 9 tests: Spearman within round x subfield, stratified permutation p, Benjamini-Hochberg q < 0.1 with the predicted sign.
- Pilot papers are excluded from the tests. Unassessable papers (U1-U3, U5) stay in the denominator as not achieved; U4 papers are reported and excluded.
- Validation gate on the 40 human-rated gold papers before the results are read as advance rather than model judgment (json `validation_gate`).

| id | feature (inquiry coding) | outcome | predicted |
|:--|:--|:--|:--|
| H1 | bin:triangulation | achieved_noW3 | positive |
| H2 | num:V check kinds | achieved_noW3 | positive |
| H3 | bin:claim gate yes | achieved | positive |
| H4 | bin:claim gate yes | score | positive |
| H5 | bin:action gate yes or partly | achieved | positive |
| H6 | bin:outcome contradicted | role:corrective | positive |
| H7 | bin:composition capability_first | role:enabling | positive |
| H8 | num:import fields | role:integrative | positive |
| H9 | bin:any return after failure | score | positive |

Calibration checks, outside the family: C1 impact forecast against cnp, C2 advance score against cnp (both positive).

Shared-method variance: The inquiry coding (codebook 1.5.0) and the advance coding are made by the same model from the same paper text. An association between a workflow feature and advance is a same-model, same-text estimate that includes method variance: both codings respond to how richly the paper reports its checks. V-check features are tested only against the primary outcome with W3 removed; covariates (log paper words, text route, number of reported checks) are reported as a sensitivity; the same associations are reported on the 40 human-rated papers when the gate data exist. An optional second-coder replication with a different model on a random 60-paper subsample (about $8) would show how much the associations shrink.
