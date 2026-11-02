# EIA-860 plant-to-grid connection review: 2023–2024 accepted queue results

Reproducibility evidence: [EIA-860 mapping and prioritization Actions run 41399889385](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41399889385) was successful in **both** 2023 and 2024 matrix jobs. [Regression CI 41399915353](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41399915353) was also successful.

| Measure | 2023 | 2024 |
|---|---:|---:|
| Geographic plant-to-bus candidate plants | 3810 | 4043 |
| Geographic nearest-bus distance greater than 50 km | 83 | 82 |
| Material (>1 km) shift under main-grid candidate restriction | 1 | 2 |
| Unique plants in the union of either priority category | 84 | 84 |
| Plants satisfying both priority categories | 0 | 0 |
| Electrical plant-bus connections independently verified | 0 | 0 |
| Real dispatch approved | **No** | **No** |

Outputs uploaded to artifacts `eia860-plant-ba-2023` and `eia860-plant-ba-2024`: `eia860_interconnection_priority_2023.csv` and `eia860_interconnection_priority_2024.csv`, accompanied by JSON reports. Each record has plant ID, original candidate bus, distance, evidence priority reason and flags blocking real dispatch.

**Interpretation:** The 84 + 84 are *year-specific review records*, not a verified 168 unique real-world plants. Do not sum them without a plant-ID year-over-year deduplication. A low geographic distance, same BA, or ReEDS membership cannot establish a physical interconnection. The 2024 material changes previously identified are EIA plant IDs `6704` and `67982`; they are *not* certified grid connections.

## Outstanding research gate

An auditable electrical interconnection crosswalk should contain plant/generator ID, verified connection bus or substation ID, voltage, documentary source, source year, and quality/ambiguity flag. Until actual verified links exist, any constrained OPF with these matched nodes remains inadmissible as calibrated Western generation. Prioritize review using official interconnection records, utility connection maps and plant operational documents, then validate against the source network's electrical graph. Maintain separate evidence tables from provisional geospatial nearest-neighbor outputs.
