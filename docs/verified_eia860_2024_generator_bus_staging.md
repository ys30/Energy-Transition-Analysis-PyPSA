# Verified EIA-860 2024 generator-level Western bus-candidate staging

**Successful actual-data CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41772568847

The repository has now generated a **generator-level** staging CSV from independently downloaded official 2024 EIA-860 generator/BA inventory (archived run 41349585538), official plant coordinate extraction, and the actual saved 10,157-bus Western PyPSA-USA base topology (archived run 41531397166). This reuses existing pipelines rather than inventing plant capacities or synthetic source identifiers.

## Actual source result

| Metric | Verified |
|---|---:|
| Screened `status=OP`, BA matched, positive-MW individual generator rows | 5,665 |
| Distinct matched generating plants | 3,223 |
| Total 2024 source nameplate capacity | 268,692 MW |
| Generator rows with some same-state nearest geographic bus candidate | 5,665 |
| Generator rows lacking a candidate | 0 |
| Candidate rows more than 50 km from their facility coordinates | 88 |
| Nameplate of those >50 km rows | 5,831.9 MW |
| Independent electrical plant-to-bus connections verified | **0** |
| Real PyPSA `Generator` components created | **0** |

The exported per-generator CSV retains original `plant_id`, `generator_id`, `fuel`, `ba_code`, historic `capacity_mw`, nearest geographic `candidate_bus`, distance, source state and explicit false electrical-connection and network-injection flags. The 88 far-away **generator rows** must not be confused with the older 82 far-away **plant candidate pairs**; these counts have different units. All source capacity reconciles exactly to mapped plus unmapped MW.

**Critical scope:** This is an EIA-screened source set overlapping the original Western bus state coverage. The national/Western electrical-interconnection eligibility of each operating power plant has **not** been independently validated. The original Western bus network is synthetic-topology-derived, not a utility-certified real POI registry. A generator at the nearest bus need not actually feed that bus.

## Reproduction

- Generator-level join: `src/energy_transition/eia860_generator_bus_staging.py`
- Regression tests: `tests/test_eia860_generator_bus_staging.py`
- CI workflow: `.github/workflows/eia860-generator-bus-staging.yml`
- Verified artifact: `eia860-2024-generator-level-bus-candidate-staging` in Actions run 41772568847; contains `official_2024_generator_to_candidate_bus.csv`, the numerical summary JSON and official plant/geographic candidate source reports.

The workflow fails on duplicate EIA unit identities, conflicting plant-state labels, already-approved geographic source claims, invalid distances or failed generator nameplate conservation. It does not add any generator to a PyPSA network.

## Next decisive step toward a defensible model

1. Use the generated 5,665-row staging table to prioritize **plant-level interconnection evidence by MW and uncertain grid match**, rather than attempting to validate all generating units manually at once.
2. Obtain original source-compatible `build_powerplants` output and audit source electrical connection method, capacity and status; distinguish nearest mapped bus from independent substation/POI proof.
3. Link future scenario assumptions to generator IDs/technologies and plan/retirement years, not merely reuse the 2024 installed capacity as future assured generation.
4. Reconcile generator availability, official/meteorological resource profiles and the pinned EFS 11-state candidate demand on one independently justified UTC axis, including the 2040 calendar issue.
5. Validate branch operational limits, generator-to-bus connectivity, islanding and numerical feasibility before interpreting an OPF as empirical.

**This evidence is engineering preparation only.** No full Western source-backed 2030–2050 dispatch, curtailment, reliability or emissions result has yet been produced.
