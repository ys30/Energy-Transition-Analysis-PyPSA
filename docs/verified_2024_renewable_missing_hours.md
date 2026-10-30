# Verified 2024 EIA-930 missing renewable BA/fuel hours

Source: 2024 official EIA-930 archived hourly renewable data, GitHub Actions [missing-hour inventory #41077396834](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41077396834), and independently checked original `renewable_hourly_observed.csv` artifact from [#41003777337](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41003777337).

2024 leap-year full UTC index has **8,784** hours. CISO and BPAT hourly demand is complete, but wind and solar combined coverage is 8,753/8,784 hours (31 distinct missing UTC hours). There are **55 missing BA×fuel/hour records**:

| Missing UTC period, inclusive | BA | Fuel | Missing hours | Missing BA×fuel rows |
|---|---|---|---:|---:|
| 2024-07-25 06:00–07:00 | BPAT | SUN | 2 | 2 |
| 2024-11-02 08:00–2024-11-03 07:00 | CISO | SUN and WND | 24 | 48 |
| 2024-11-08 02:00–06:00 | BPAT | SUN | 5 | 5 |

Rows by source: BPAT SUN 7, CISO SUN 24, CISO WND 24, BPAT WND 0. Concurrent 24-hour CISO solar and wind outage suggests a shared reporting gap but is **not proof** of any root cause. The November gap overlaps daylight-saving time change in the USA; that coincidence does **not** establish a DST problem or authorize timestamp correction.

**Data policy:** Missing values are NOT zero generation. Never silently fill, resample or concatenate disjoint complete segments into one continuous storage optimization. Keep the full-year investment gate blocked pending verified source correction or an explicitly sensitivity-tested imputation strategy. Preserve valid signed renewable net values including negative records.

Files published by the inventory workflow: `missing_renewables_by_ba_fuel_hour.csv`, `missing_renewables_by_ba_fuel_summary.csv`, `missing_renewables_hour_overlap.csv`.
