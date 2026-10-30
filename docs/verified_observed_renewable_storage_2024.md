# Verified observed wind/solar net injection × chronological storage pilot (2024)

Source: successful [GitHub Actions #41073323883](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41073323883), artifact `observed-renewable-storage-comparison-2024`, file `observed_renewable_storage_comparison.csv`. This is an eight-run, four-season 168-hour, 1-GW/4-GWh battery experiment.

**Scenario meaning:** both variants use the same 55-GW low-cost and 20-GW expensive illustrative generators, and the battery/no-battery comparisons are each matched. The second variant additionally offsets net electricity demand by the **signed observed** EIA-930 CISO+BPAT wind and solar generation for the same hour. That illustrative firm source must be interpreted as *non-wind/non-solar residual supply*; its identity and true nameplate allocation have not been independently verified. Do not assume the experiment reconstructs historical generator dispatch, transmission, or actual reliability. Negative renewable net generation is preserved as additional net demand, not clipped.

| Week | Observed signed wind+solar (TWh) | Unserved with storage, supply-only (MWh) | Unserved with storage, + observed wind/solar (MWh) | Battery savings, supply-only ($M) | Battery savings, + observed wind/solar ($M) |
|---|---:|---:|---:|---:|---:|
| Winter | 1.122 | 0 | 0 | 7.314 | 3.558 |
| Spring | 1.345 | 0 | 0 | 0 | 0 |
| Summer | 1.558 | 315,022 | 10,652 | 218.583 | 73.142 |
| Autumn | 1.197 | 0 | 0 | 4.265 | 3.377 |

For summer *without the battery*, modeled unmet demand changes from 337,201 MWh to 17,707 MWh when observed wind/solar injections are added. With the battery, unmet demand changes from 315,022 to 10,652 MWh. Consequently, the battery's own avoided unmet demand is **7,055 MWh** in the observed-wind/solar variant, versus **22,179 MWh** in the supply-only variant. Do not attribute the entire improvement in unmet demand to the battery.

All eight solves passed their PyPSA optimization and storage conservation checks (max residual below `5e-13 MWh`). The four selected weeks are not a statistically representative year and cost savings omit battery capex and degradation. $10,000/MWh modeled value of lost load dominates shortage-related monetary results. A BA-level realized net generation observation is neither a weather-derived potential nor a suitable forecast of new renewable installed capacity.

## Required next scientific steps
- Reconcile historical assumed residual generation with verified EIA-923/EIA-860 technology totals before inferring resource adequacy or capacity credit.
- Source meteorological hourly wind/solar availability for future expansion.
- Incorporate actual geographically grounded transmission constraints, storage energy-capacity data, and investment costs.
- Keep BPAT interchange withheld from transfer-capacity calibration until its failed accounting audit is resolved.
