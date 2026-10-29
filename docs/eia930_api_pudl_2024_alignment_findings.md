# EIA API versus PUDL same-hour validation (2024)

Verified source: [GitHub Actions run 40945843861](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/40945843861), artifact `eia930-api-pudl-hour-alignment-2024`, file `api_pudl_same_hour_comparison.csv`.

## Selected reported-stage comparisons (zero UTC hour shift)

| BA | Field | Matched observations | Mean absolute difference (MW) |
|---|---|---:|---:|
| BPAT | Demand | 8,784 | 0.016735 |
| BPAT | Net generation | 8,784 | 0.006034 |
| BPAT | Total interchange | 8,783 | 0.005579 |
| CISO | Demand | 8,736 | 0 |
| CISO | Net generation | 8,736 | 0 |
| CISO | Total interchange | 6,552 | 0 |

At ±1-hour shifts, the observed MAEs increase to hundreds of MW or more, confirming zero-hour offset for these fields. BPAT demand and generation each had a maximum individual discrepancy of 32 MW even at zero shift, so **do not assert exact equality for every observation**.

This strongly supports that BPAT's previous ~36.04 TWh imbalance is present in the underlying EIA-reported series, rather than caused by a cross-source time-zone error. It does **not** explain the cause of the underlying inconsistent reported figures.

CISO reported total interchange is available on only 6,552 paired hours, compared with 8,736 for reported demand and generation; stage-specific missingness is material. EIA adjusted values cover some additional hours for CISO demand/generation and must not be mixed with reported values for account balances.

## Sources and important cautions

- [EIA-930 data definitions](https://www.eia.gov/electricity/930-content/about.html): normally D = NG - TI; EIA warns that pseudo-ties, dynamic scheduling and metering/reporting differences may cause inconsistency.
- [PUDL EIA-930 data dictionary](https://data.catalyst.coop/preview/pudl/core_eia930__hourly_operations): reported vs adjusted vs imputed hourly data are distinct.
- [BPA EIA reports index](https://transmission.bpa.gov/business/operations/Misc/eia/): primary BPA operational submissions, available for future independent review.

## Modeling gate

BPAT and CISO remain **not validated for transmission calibration**. This alignment is a timestamp/source validation, not an inferred physical transfer capacity or net import estimate.
