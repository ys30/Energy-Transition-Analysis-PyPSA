# Verified 2024 EIA-923 plant-to-EIA-860 BA match

Evidence: [successful GitHub Actions #41085325552](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41085325552), artifact `eia2024-plant-ba-qualification-match`; `plant_match_provenance.json`, `plant_qualification_match_audit.csv`, and `ba_fuel_plant_match_summary.csv`.

The source is previously reconciled/qualified EIA-923 Page 1 annual plant/fuel/prime-mover records and a freshly reconstructed **2024** EIA-860 reported plant-BA crosswalk. Matching uses plant identifiers and compares **reported BA** on both sources; it does not allocate plant net generation across individual generator capacities. Negative source generation values are preserved; the coverage ratio deliberately uses absolute MWh to avoid misleading cancellation.

| Metric | Verified result |
|---|---:|
| Selected 2024 EIA-923 source records | 1,988 |
| Matched source records | 1,944 |
| Unmatched or ambiguous source records | 44 |
| Qualified matched records | 1,887 |
| Qualified unmatched records | 31 |
| BA disagreement records among matched plants | **0** |
| Total qualified absolute generation | 281,935,046.982 MWh |
| Matched qualified absolute generation | 281,233,356.978 MWh |
| Unmatched qualified absolute generation | 701,690.004 MWh |
| Matched qualified absolute generation fraction | **99.7511%** |

The largest unmatched qualified **absolute** generation category is CISO SUN at 444,370 MWh, followed by CISO WDS at 178,460.260 MWh. Unmatched plants must remain visible rather than disappearing from plant-level summaries.

### BPAT wind: unresolved boundary discrepancy

All **28** BPAT WND EIA-923 source rows qualified and matched reported EIA-860 plant BA; their combined qualified EIA-923 annual generation is **8,820,435.410 MWh**. Earlier EIA-930 BPAT hourly WND net-generation reported over observed 2024 timestamps summed approximately **6,839,734 MWh**. The descriptive difference is ~**1.981 TWh**, but the EIA-930 coverage and reporting definitions differ from EIA-923 plant-level Page 1 reporting. It is **not** yet a reconciled energy-balance mismatch, transmission figure, or proof of lost/curtailed energy.

**Interpretation limits:** 99.75% is the matched share of the available **qualified annual EIA-923 generation absolute values**, not a census-level generation completeness percentage, not validated hourly generation, and not proven BA deliverability. The match provides a necessary source-integrity gate for deeper per-plant and per-technology generation audit, not authorization to calibrate the current illustrative 55-GW firm + 20-GW peaker PyPSA supply model.

Next: independently examine BPAT wind plant-level membership and the EIA-930 monthly wind generation series and reporting boundaries; assess source row qualification coverage and generator capacities plant by plant before physical modeling.
