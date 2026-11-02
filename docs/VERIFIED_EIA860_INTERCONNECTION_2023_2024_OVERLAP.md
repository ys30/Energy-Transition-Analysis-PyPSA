# Verified 2023–2024 EIA-860 interconnection review overlap

Source: [successful deduplication workflow 41400588920](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41400588920); [successful main CI 41400588929](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41400588929).

## Results

| Metric | Verified count |
|---|---:|
| 2023 priority-review records | 84 |
| 2024 priority-review records | 84 |
| **Distinct plant IDs across both years** | **89** |
| Both years | 79 |
| 2023 only | 5 |
| 2024 only | 5 |
| Independently verified generator-to-bus electrical connections | **0** |
| Real generator dispatch approved | **No** |

The 79 persistent cases are the natural first group to investigate, followed by the year-specific differences. These are *review queue entries*, not a validated Western-generator connectivity sample. A 2023/2024 year difference can arise from coverage, nearest-neighbor changes or source data updates; no causal explanation is inferred from these counts alone.

The Actions run publishes `eia860_interconnection_cross_year.csv` and `eia860_interconnection_cross_year.json` under artifact `eia860-cross-year-unique-review-plants`. The CSV retains plant IDs, year-specific candidate buses and distances, and review reasons. Any future manual connection evidence must include a traceable primary source, plant/generator identity, confirmed point of interconnection and effective date. Do not convert geographic candidates into real generators without that evidence.
