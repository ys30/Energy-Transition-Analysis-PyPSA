# Verified quantitative results — NLR EFS Reference / Moderate (core 11 Western states)

**Source:** official NLR EFSLoadProfile_Reference_Moderate.csv via pinned PyPSA-USA v0.8.0. **CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41262154939

## Measured demand-series aggregates (not solved power-system results)

| Target year | Core-11 annual load (TWh) | Mean load (GW) | California annual load (TWh) | Washington annual load (TWh) |
|---|---:|---:|---:|---:|
| 2030 | 774.400 | 88.402 | 284.614 | 110.958 |
| 2040 | 855.707 | 97.683 | 308.445 | 124.062 |
| 2050 | 980.023 | 111.875 | 353.942 | 142.058 |

All annual totals computed by summing 8,760 one-hour LoadMW observations for each of 11 states; mean load equals total MWh / 8,760 hours.

### Verified state annual demand (TWh)

| State | 2030 | 2040 | 2050 |
|---|---:|---:|---:|
| AZ | 89.416 | 99.976 | 114.478 |
| CA | 284.614 | 308.445 | 353.942 |
| CO | 64.966 | 72.639 | 83.175 |
| ID | 27.989 | 31.294 | 35.834 |
| MT | 16.827 | 18.779 | 21.458 |
| NM | 26.224 | 28.987 | 32.675 |
| NV | 41.462 | 46.359 | 53.084 |
| OR | 56.505 | 63.179 | 72.343 |
| UT | 34.429 | 38.495 | 44.079 |
| WA | 110.958 | 124.062 | 142.058 |
| WY | 21.009 | 23.490 | 26.898 |

California independent state peak: 56.878 GW (2030), 61.640 GW (2040), 70.733 GW (2050). Independent state peaks cannot simply be summed to obtain synchronized regional peak.

**Coverage:** 289,080 unique state/year/local-hour rows = 11 states × 3 years × 8,760 hourly identifiers; 4,047,120 source sector/subsector rows. Nonnegative finite MW, no missing state-year-hour pairs within the core-11 scope.

**Limitations:** local source hour IDs not UTC/time-zone/DST synchronized, 11-state pilot is not the complete Western ReEDS membership, no verified LAF-state weights, not an empirical PyPSA network solution, and no claims about optimum costs, CO₂ outcomes or grid adequacy. These figures are source-based load *projections*, not observed future energy consumption.

**Reproduce:** CI artifact `efs-core-west-annual-mwh-state-peaks.json` and `efs-core-west-2030-2040-2050-hourly.csv.gz`, produced by `src/energy_transition/nlr_efs_annual_metrics.py`.
