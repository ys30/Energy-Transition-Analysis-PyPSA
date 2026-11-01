# Verified multi-year real EFS load-bearing Western PyPSA networks

Verified workflow: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41281576025 (success). Main CI 41281575958 (success).

Three actual built-network NetCDF files were created with the pinned PyPSA-USA Western topology, 8,760 ordinal local-hour snapshots, 20 zonal Load components, and observed upstream `LAF_state` weights for seven numerically admitted states.

| Planning year | Reimported allocated annual demand (MWh) | TWh | Absolute NetCDF roundtrip error (MWh) |
|---|---:|---:|---:|
| 2030 | 274706987.11412096 | 274.707 | 5.96e-8 |
| 2040 | 306839206.74116015 | 306.839 | 1.19e-7 |
| 2050 | 350871474.8471029 | 350.871 | 5.96e-8 |

All three `verified_netCDF_roundtrip` flags true. Source is NLR EFS Reference/Moderate, not observed future demand. Inputs cover AZ, CO, ID, MT, NM, UT, WY only; MT/NM have partial-Western LAF sums. This is not total Western electricity consumption.

Corresponding artifacts: `efs-real-2030-local-hour-load-only.nc`, `efs-real-2040-local-hour-load-only.nc`, `efs-real-2050-local-hour-load-only.nc`, plus audit JSON per year.

**Not yet established:** time-zone/DST synchronization, full-Western spatial admission (CA/NV/OR/WA, Texas and cross-border nodes), independently certified demographic provenance of LAF, generator/fuel/carbon system, real dispatch/investment optimization. Do not interpret these as optimized generation or grid-resilience outcomes.
