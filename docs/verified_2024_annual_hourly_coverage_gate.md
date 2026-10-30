# Verified 2024 annual chronological input coverage gate

Evidence: successful [GitHub Actions run 41075859368](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41075859368), artifact `annual-hourly-storage-input-coverage-2024`, file `annual_hourly_coverage_gate.json`.

Data: hourly EIA-930 2024 reported demand in CAISO/CISO and BPAT and signed EIA-930 wind (WND) / solar (SUN) fuel-type net generation, 8,784 expected UTC hourly timestamps in a leap year.

| Metric | Verified result |
|---|---:|
| Expected hours | 8,784 |
| Complete positive BA demand hours | 8,784 |
| Hours complete across both BAs and both wind/solar fuel types | 8,753 |
| Missing at least one wind/solar BA-fuel observation | 31 |
| Fully aligned hours | 8,753 |
| Longest consecutive fully aligned interval | 4,950 hours |
| Longest interval UTC start | 2024-01-01T00:00:00+00:00 |
| Longest interval UTC end | 2024-07-25T05:00:00+00:00 |
| Number of aligned complete runs | 4 |
| Full 8,784-hour optimization permitted by strict source gate | **No** |

The input data are not silently interpolated or zero-filled. Solar/wind negative net-energy records are retained as reported, not clipped. The strict annual full-year investment screening gate therefore blocks a 2024 annual result. A partial contiguous 4,950-hour study would be an illustrative subannual period and **must not be annualized**.

Next: inspect the 31 missing renewable hours, ascertain source/BA-fuel-specific causes, evaluate whether an independently justified correction is possible, and only then run a clearly documented continuous full-year scenario. Future modeled cashflow must also explicitly address 55 GW assumed residual supply and the modeled unmet-load valuation; neither has been calibrated to historical EIA-923/EIA-860 and observed electricity markets.
