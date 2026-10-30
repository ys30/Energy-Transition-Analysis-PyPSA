# Verified EIA-930 hourly solar and wind generation (2024)

Evidence: successful [GitHub Actions #41003777337](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41003777337), artifact `eia930-hourly-solar-wind-2024`. Source: [EIA RTO fuel-type-data hourly API](https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/), `fueltype=SUN` or `WND`. The source reports MWh per hourly period.

## Source coverage and signed reported net generation

| Balancing authority | Fuel | Reported hours | Missing hours | Negative hourly values | Signed net generation on reported hours (TWh) |
|---|---|---:|---:|---:|---:|
| CAISO (CISO) | Solar (SUN) | 8,760 | 24 | 2,761 | 44.729341 |
| CAISO (CISO) | Wind (WND) | 8,760 | 24 | 0 | 20.044281 |
| BPA (BPAT) | Solar (SUN) | 8,777 | 7 | 1,500 | 0.270656 |
| BPA (BPAT) | Wind (WND) | 8,784 | 0 | 115 | 6.839734 |

**Negative net generation is part of the reported data and is not filled with zero.** In particular, CAISO solar has -100,208 MWh of negative-valued hours and its nonnegative-only sum would overstate signed net energy. BPAT's negative signed solar hours total -1,863 MWh. This audit does not determine whether negative records are due to station service, measurement adjustments or another reporting convention. Missing hours are never imputed.

## Verified representative seasonal windows

The four 168-hour windows previously used for the chronological storage pilot (starting January 8, April 8, July 8 and October 7, 2024 UTC) are complete for **both BAs and both fuel types**: 168 × 2 × 2 = 672 distinct BA/fuel-hour observations per week, 2,688 in total.

Observed signed solar and wind energy summed over two BAs per window:

| Season | Solar (MWh) | Wind (MWh) |
|---|---:|---:|
| Winter | 544,074 | 578,131 |
| Spring | 909,293 | 435,803 |
| Summer | 1,069,541 | 488,776 |
| Autumn | 869,261 | 327,955 |

Output files: `renewable_hourly_observed.csv`, `renewable_hourly_coverage.csv`, `seasonal_observed_renewables.csv` and `provenance.json`.

## Modeling policy

1. These are **realized historical net generation** observations, not a meteorological resource assessment, uncurtailed availability profile, or wind/solar capacity factors.
2. A future dispatch experiment may use the signed generation as exogenous net injections with a consistent balancing adjustment; do not replace generator `p_max_pu` with raw MWh or apply assumed clipping without preserving an audit.
3. BA-level fuel generation and 11-state EIA-860 plant nameplate do not necessarily share a perfectly matched plant universe, so a naïve generator CF division is not scientifically validated.
4. This improves traceability of four-week studies but **does not yet validate** transmission constraints, reservoir/storage behavior, or 2025–2040 renewable expansion.
