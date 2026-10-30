# Verified BPAT 2024 wind EIA-923 plant concentration

Evidence: successful [GitHub Actions #41086750022](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41086750022), artifact `bpat-wind-plant-concentration-2024`, CSV `bpat_wind_qualified_plant_concentration.csv`, and `provenance.json`. Input: independently audited EIA-923 qualified source rows already linked to EIA-860 2024 plant BA codes.

## Results

- 28 EIA-923 wind source records, each belonging to a separate BPAT-attributed plant (28 distinct plant identifiers).
- All 28 source records are qualified and EIA-860 BA-matched.
- Qualified 2024 EIA-923 wind generation: **8,820,435.410 MWh**.
- Top five plants contribute **38.4574%** of those 28 plants' qualified net generation.

| EIA plant ID | Annual qualified net generation (MWh) | Share of 28-plant generation |
|---|---:|---:|
| 57195 | 864,875.00 | 9.8054% |
| 57159 | 671,560.00 | 7.6137% |
| 57549 | 619,466.82 | 7.0231% |
| 57526 | 619,333.48 | 7.0216% |
| 62745 | 616,871.00 | 6.9937% |

## Limits

EIA-930 reports BPAT hourly WND net generation at balancing-area level, not matching plant-level generation from this EIA-923 dataset. The previously verified EIA-930 BPAT WND annual signed sum is 6,839,734 MWh and EIA-923 plant sum is 8,820,435.410 MWh, a **1,980,701.410 MWh descriptive gap**. Plant concentration is NOT a decomposition of that cross-source gap. It does not demonstrate any plant's contribution to discrepancy, curtailment, losses or outside-BA trading. Even full plant-ID agreement does not prove that the two EIA datasets cover identical generation populations or accounting boundaries.

Next investigation: obtain plant names, operator/BA reporting definitions and location for these 28 plants from original EIA-860/EIA-923 source tables; compare with formal EIA-930 accounting documentation. Do not alter the currently observed EIA-930 time series or assign plant-specific missing volumes without independent evidence.
