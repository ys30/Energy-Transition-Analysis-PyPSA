# Verified 2024 EIA-860 distant-plant nearest-bus concentration

**Actual source audit passed:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41774150894

This extension uses the archived and independently CI-checked **2024 EIA-860 5,665-generator** staging table, rolled up to **3,223 actual source plant IDs**, then restricts to the **63 plants / 88 generators** whose nearest geographic candidate synthetic-topology network bus is more than 50 km away. Only grouped geographic candidate IDs are analyzed; none is independently utility-certified.

## Numerically verified concentration

| Measured source subset | Result |
| --- | ---: |
| Long-distance plants | 63 |
| Long-distance plant historical nameplate | 5,831.9 MW |
| Distinct synthetic candidate buses containing those plants | **15** |
| Candidate buses serving two or more geographically far source plants | **10** |
| Distinct source plants falling in repeated candidate-bus groups | **58** |
| Associated historical nameplate in repeated groups | **5,118.3 MW** |
| Top 10 candidate-bus clusters, combined nameplate | 5,787.8 MW |
| Independently verified POIs | **0** |

This means 5,118.3/5,831.9 = **87.76%** of the far-distance screened historical capacity falls into clusters that share synthetic candidate bus IDs with at least one additional far-away plant. That concentration is a potential issue in the **candidate geographic crosswalk**, not an estimate of operational network congestion, power capacity aggregation, or actual plant electrical connectivity.

### Largest source clusters

| Candidate bus ID (not a real POI identity) | Plant count | Generator rows | Historical nameplate MW | Maximum plant–candidate distance | Reported BA labels |
| --- | ---: | ---: | ---: | ---: | --- |
| `2053003` | 21 | 33 | 2,847.6 | 225.78 km | SWPP, TEPC |
| `2053000` | 12 | 14 | 976.0 | 197.07 km | GRIS, PNM, SWPP |
| `2077001` | 7 | 8 | 913.2 | 185.38 km | AVA, MISO, NWMT, PSEI |
| `2053271` | 1 | 1 | 350.0 | 54.00 km | PNM |
| `2053009` | 1 | 2 | 235.0 | 75.67 km | PNM |

The top **three** candidate bus clusters account for **4,736.8 MW**, or approximately **81.22%** of the far-distance subset. Multiple reported BA labels at the same synthetic candidate ID further reinforce why geographic-nearest mappings cannot be treated as an actual plant–grid POI crosswalk.

## Reproducibility

- Source: `src/energy_transition/eia860_plant_bus_collision_risk.py`
- Regression tests: `tests/test_eia860_plant_bus_collision_risk.py`
- GitHub Actions: `.github/workflows/eia860-plant-bus-collision-risk.yml`
- Source artifact: `eia860-2024-generator-plant-poi-review-triage` from run 41773439738
- Output artifact: `eia860-2024-distant-plant-bus-collision-risk` from run 41774150894; CSV `long_distance_plant_candidate_bus_collision_groups.csv` and JSON `long_distance_plant_candidate_bus_collision_summary.json`

## Source admission and next research decision

The 10,157-bus Western topology originates from a synthetic test-system family; source bus IDs are not equivalent to utility-certified substation/POI IDs. Prioritize collecting official utility maps, interconnection documents, transmission owner nameplates and source-coupled geographic electrical identities for the clusters `2053003`, `2053000` and `2077001`. This likely provides more scientific leverage than re-running 63 independent nearest-neighbor searches.

**Do not** attach 2,847.6 MW or any other grouped EIA generator capacity to a candidate bus for empirical OPF without source-approved electrical connectivity. EIA-860 2024 nameplate is not verified future dispatchable MW or an EFS 2030–2050 capacity assumption. The original model remains **not admitted** for calibrated Western OPF.
