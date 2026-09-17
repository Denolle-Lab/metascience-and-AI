# Worked example: an observation triggers the run

Reference for the `unit-of-inquiry` skill. Human-edited, versioned with the unit graph (`unit.qmd`, graph v0.2). The agent's SKILL.md carries the operative one-line rules; this file carries the full rule, its rationale, and the reading that fixed it. Edit here first, then shorten into SKILL.md.

Trigger: an observation. Three years of ambient-noise cross-correlations on a dense array; most station pairs show a small annual velocity change; one pair shows an unexpected jump in year two. `situation`: C found (nature sets the seasons), repeated by nature for the annual cycle, unique for the jump. `method: auto`.

| Step | What the agent does | Artifact |
|:--|:--|:--|
| 0 | Two triggers, treated separately. The annual cycle: found, repeated, stable → `natures-repetition`. The jump: found, unique, not yet a phenomenon → `exploration-first` | composition declaration, two entries |
| before G (jump) | Checks the measurement chain first: instrument swap, clock, processing window, source-direction change; re-observes on neighbouring pairs; asks whether the jump repeats on any other pair or year | phenomenon: "jump on one pair, absent on neighbours, coincident with a logged sensor replacement" → artifact verdict; the jump run ends here |
| Q (cycle) | Question: does the seasonal velocity change track groundwater? Origin: observation. Consequence: if yes, the array is a hydrological instrument | question |
| G | Rivals: groundwater storage; thermoelastic strain; precipitation loading; seasonal change in noise-source direction. Marked incompatible except that loading and storage may co-occur; the pair is flagged | rivals |
| D | Each rival gives E_i as a phase lag against a driver and a depth sensitivity: groundwater lags rainfall by weeks and is deep; thermoelastic tracks temperature with days of lag and is shallow; loading is in phase with rainfall; a source change shows in the correlation asymmetry, not in velocity. A listed for each: the depth sensitivity kernel, the noise-source model, the well-record calibration | expectations, auxiliaries |
| S | The observable on which the E_i differ: phase lag against temperature versus against water level, by frequency band (depth). Platt's Question answered per outcome | design |
| C | Found: water-level records from wells outside the array, temperature, rainfall. Not available: a well inside the array | conditions: found, with the gap logged |
| O, M | Phase lags measured per band; matched against the four expectations | match table |
| V substitute | No conditions can be set. Independent traces: the second and third years; two frequency bands; the correlation asymmetry as a separate check on the source rival | traces |
| X, K | Source change excluded by the asymmetry check; thermoelastic excluded at depth by the lag; groundwater and loading not separable with the wells available | verdicts |
| Abstain | "Not decidable between groundwater storage and precipitation loading with these observations; a well inside the array, or a fourth year with a dry winter, would decide it" | abstention with the deciding observation |

The run produces no "groundwater causes the change." It produces two exclusions, one artifact verdict, and a named next observation. Under the textbook method the agent would have reported the fit; under this skill it reports what the evidence owed and what it lacked.

