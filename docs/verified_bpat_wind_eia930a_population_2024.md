# Verified BPAT 2024 wind source-population check against EIA-930A

Evidence: [successful EIA-930A crosswalk GitHub Actions #41089242221](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41089242221), artifact `bpat-eia930a-reported-population-2024` containing `bpat_wind_eia930a_population_audit.csv` and `provenance.json`. Official [2024 EIA-930A workbook](https://www.eia.gov/electricity/930-content/EIA_930A_2024_with%20layout.xlsx) linked from [EIA-930 About](https://www.eia.gov/electricity/930-content/about.html).

EIA explicitly states hourly BA net generation covers a **subset** of all utility-scale generators and introduced **EIA-930A** to identify EIA-860 plant/generator IDs reported in the hourly system. The official data also explain physical BA reporting boundaries and possible pseudo-tie/dynamic-schedule exceptions. The EIA-930 hourly series is reported as submitted without its aggregation-level imputation.

## 2024 BPAT wind findings

| Measure | Verified value |
|---|---:|
| EIA-923 qualified and 2024 EIA-860 BA-matched BPAT wind plants | 28 |
| Plant IDs present in official 2024 EIA-930A BPAT Schedule 2 | 20 |
| Plant IDs absent from BPAT Schedule 2 | **8** |
| Qualified EIA-923 generation at these eight plant IDs | **1,802,779 MWh** |
| Qualified EIA-923 generation at BPAT Schedule-2-listed plant IDs | 7,017,656.410 MWh |
| Plant IDs appearing anywhere in EIA-930A under another BA (not necessarily exclusive) | 2 |
| EIA-923 qualified wind generation total | 8,820,435.410 MWh |
| EIA-930 2024 BPAT WND observed hourly signed sum | 6,839,734 MWh |
| Unreconciled reported-generation difference | 1,980,701.410 MWh |

This is **direct source-population evidence** supporting a possible explanation for part of the difference: eight EIA-923 BPAT-attributed plant identifiers are not in the 2024 BPAT EIA-930A Schedule 2 reporting population. **Do not subtract** 1,802,779 MWh from the difference as if it were a verified component. EIA-930A is a *generator-level* annual inventory, while this pilot screens at *plant-ID* granularity; a plant appearing in Schedule 2 does not establish that every generator or every MWh from the plant contributed to hourly BPAT WND. Some plants may have a listing under other BAs or other schedules, which also does not imply ownership or physical-meter allocation. A rigorous follow-up is plant + generator matched population against EIA-860 generator IDs and the Page 1/4 EIA-923 accounting boundary, then separate missing-asset and meter-methodology assessments.

**Do not** modify the original EIA-930 wind hourly injection, claim loss/curtailment, reallocate interchanges, or infer a residual loss of 177,922.41 MWh by subtracting unmatched plant output. All current battery results remain illustrative.
