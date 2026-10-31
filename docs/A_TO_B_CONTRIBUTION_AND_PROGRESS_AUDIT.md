# Project A → B integration audit and revised status (2026-10-31)

## Repositories and evidence

- **A:** [ys30/lut-to-pypsa](https://github.com/ys30/lut-to-pypsa): standalone LUT-DEMAND-to-PyPSA demonstration. Most recent checked commit `1ec9b789`; both Tests and PyPSA integration workflows succeeded.
- **B:** [ys30/Energy-Transition-Analysis-PyPSA](https://github.com/ys30/Energy-Transition-Analysis-PyPSA): Western U.S. EIA/EFS/ReEDS/NARIS modeling; most recent checked commit `ae3fb992`; main CI and upstream pinned-code preflight succeeded.
- **No direct A-to-B data feed, Python-package dependency or migrated empirical model output is verified.** Treat any shared concepts as methodological reuse, not an automatically merged result.

## Audited contribution and limits

| A artifact / method | What is actually available in A | Useful for B | **What it cannot provide** |
|---|---|---|---|
| `real_lut.py`, source-cell-traced LUT-DEMAND v1.1 fixture | 35 annual values across five continents, 2020–2050; cached Excel output | Source lineage and workbook-to-table QA pattern | U.S. state or Western ReEDS-zone demand; direct EFS calibration |
| `hourly.py` | Full 8,784-hour 2020 flat *assumed* disaggregation and conservation checks | Calendar/unit/annual-energy QA pattern | Observed hourly electricity demand shape |
| `comparison.py`, `scenarios.py` | Annual LUT year comparison and researcher-selected 0.9×/1.1× demand sensitivity | Scenario labelling and energy conservation audit patterns | EFS scenario validation or projected Western demand |
| `benchmark.py`, `fixed_capacity.py` | Isolated-bus HiGHS dispatch with illustrative generator capacity, costs and shortage penalty | Feasibility/slack and dispatch regression patterns | Physical transmission constraints or calibrated adequacy |
| `observed_network.py` | Audited **unsolved** observed-capacity import, strict geography completeness gate | Source inventory and region-coverage preflight | A full USA/Western plant fleet, real network solve or REeDS allocation |
| A GitHub Actions | Passing tests and PyPSA smoke workflow | Independent engineering evidence | Verification of B's empirical WECC scenarios |

**Boundary:** LUT-DEMAND is annual electricity *energy-service* demand for a continent, not a measured end-use load for Western BA/state cells. Dividing its Americas total among Western zones would be an invented geographic assignment. Keep A as an independent global-demand/methodology case, not B's empirical demand input.

## Revised Project B progress interpretation

Percentages below are **nonformal workstream estimates**, not statistically measured completion rates. Report independently rather than averaging into an overstated overall score.

| Workstream | Planning estimate | Verified state |
|---|---:|---|
| Data engineering, CI, audit machinery | ~95% of current engineering milestone | Tests green; comprehensive inputs not yet acquired |
| 2024 EIA BA source ingestion and diagnostics | ~85% of defined QA tasks | Historical CISO/BPAT comparisons, missingness and wind-accounting mismatch documented |
| PyPSA model API, NetCDF, synthetic solver integration | ~90% of current smoke/integration milestone | Real PyPSA and HiGHS calls succeed for illustrative cases |
| Western topology/membership acceptance | ~65% of source-aware zonal engineering milestone | NARIS interfaces, 35-zone membership, connectivity limitation, isolated zone disclosure; **no calibrated AC network** |
| Empirical EFS → ReEDS LAF weights | ~20% of intended real-data milestone | Extractor and provenance gates implemented, **no actual source-network LAF extracted** |
| Multiyear Western scenario solve & calibration | ~15% of intended research milestone | Annual-year gates exist; no verified full Western 2030/2040/2050 optimization |

**A's incremental B benefit:** stronger methodological precedent and separate evidence for provenance/energy conservation, but **0 newly admitted Western hourly observations, 0 real ReEDS LAF weights, and 0 additional empirical B solves** from this audit. Do not sum A's completion into B's percentage or claim project merger.

## Remaining B critical path (priority)

1. Obtain a **built, versioned** upstream PyPSA-USA network retaining `reeds_state`, `reeds_zone`, `LAF_state` and its exact configuration and geographic build lineage.
2. Audit and aggregate real Western LAF against official membership; keep state-conservation, all-zone coverage, and evidence review mandatory.
3. Load independently sourced EFS state-hour profiles per 2030/2040/2050 and reconcile time standards and annual energy against appropriate source totals.
4. Couple modelled supply, renewable time series, network limits and investment costs; run full-network solves and physical/economic acceptance and sensitivities.
5. Present recruiter results as source-derived diagnostics vs illustrative models separately; do not label prototype storage benefits as observed savings.

A is deliberately retained as a distinct `lut-to-pypsa` showcase; B remains the Western research integration repository.
