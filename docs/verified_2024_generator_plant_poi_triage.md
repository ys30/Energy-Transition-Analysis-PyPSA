# Verified 2024 EIA-860 generator-to-plant POI evidence triage

**Actual source data workflow passed:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41773439738

The 5,665 generator rows and 268,692.0 MW operating nameplate from the previously verified 2024 EIA-860 generator-bus staging archive (run 41772568847) were aggregated **once by original EIA plant ID**, preserving official generator identities and preventing duplicate plant capacity. The original source network is synthetic-topology-derived, and **none of these geographically nearest bus candidates has an independently verified electrical POI**.

| Measured inventory | Value |
| --- | ---: |
| EIA-860 2024 screened operating generator units | 5,665 |
| Distinct operating plants | 3,223 |
| Screened total historical nameplate | 268,692.0 MW |
| Geographic candidate generator rows with distance >50 km | 88 |
| Distinct plants represented by those generator rows | **63** |
| Total nameplate at >50 km candidate plants | **5,831.9 MW** |
| Nameplate of 20 highest-priority >50 km plants | **4,922.7 MW** |
| Total BA×state inventory groups | 70 |
| Independently confirmed electrical POI ties | **0** |

Top 20 far-distance priority plants cover approximately **84.4%** of far-distance nameplate. This is a **review concentration**, not a capacity availability or system-feasibility measurement.

## Highest-priority plant examples

| EIA plant ID | Reported state / BA | Nearest candidate network bus | Candidate distance km | Historic nameplate MW | Generator units |
| --- | --- | --- | ---: | ---: | ---: |
| 56458 | NM / SWPP | 2053003 | 210.403 | 681.5 | 4 |
| 63578 | NM / SWPP | 2053003 | 192.168 | 522.0 | 1 |
| 2454 | NM / SWPP | 2053003 | 207.829 | 444.2 | 3 |
| 65577 | MT / PSEI | 2077001 | 59.304 | 365.5 | 1 |
| 63981 | NM / PNM | 2053271 | 54.000 | 350.0 | 1 |

Several large NM plants share nearest network candidate `2053003` despite separations over 160 km; the observation strongly prioritizes source topology and electrical connection review, **but does not itself identify the true POI** or establish that those plants are within a validated Western interconnection.

## Deliverable evidence inventory

The run artifact `eia860-2024-generator-plant-poi-review-triage` contains:

- `all_operating_plant_poi_triage.csv`: one row per original EIA operating plant.
- `over50km_plant_poi_triage.csv`: all 63 high-distance plants, including source IDs, BA/state and unit/capacity counts.
- `top20_over50km_poi_document_queue.csv`: finite focused documentation review queue covering 4,922.7 MW.
- `poi_triage_by_ba_state.csv`: all 70 BA×state group summaries, reconciled with source inventory.
- `generator_plant_poi_triage_summary.json`: audit metrics and explicit non-admission flags.

Source: `src/energy_transition/eia860_generator_poi_triage.py`. Tests: `tests/test_eia860_generator_poi_triage.py`. CI: `.github/workflows/eia860-generator-poi-triage.yml`.

## Next decisive verification

Obtain official facility interconnection agreements, transmission-owner substations, utility system studies or mapped network crosswalks for highest-priority plant IDs, and reconcile whether an actual utility-verified bus exists in the pinned synthetic-topology network. If no such bus exists, the scientifically defensible options are to build a new sourced powerplant network or explicitly use a different topology and label its scope, **not** assign real generation to an invented original electrical POI.

The results do not imply plant-to-bus electrical approval, authenticated voltage-level connection, future 2030–2050 capacity, hourly generator availability, marginal cost calibration, or successful full-Western OPF.
