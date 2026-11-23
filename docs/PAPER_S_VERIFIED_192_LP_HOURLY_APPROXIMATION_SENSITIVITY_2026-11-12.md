# Paper S — VERIFIED original-source 192 LP hourly-approximation sensitivity (2026-11-12)

## Verification and traceability

Original 2010–2013 wind and PV county/class HDF5, source capacities, 2025 EIA operating county shares, 2030 fixed reference demand and frozen 96-LP original results were authenticated in [dedicated successful 192-LP workflow 43317414772](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43317414772).

**Eight archived result files** are downloadable from [GitHub artifact 13989123990](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43317414772/artifacts/13989123990). Original **complete CI 43317414168** succeeded. The 192 program solves are the **same 96 scenarios each evaluated under two approximate point-CF-to-hour conventions**, not independent draws or 192 separate meteorological years.

Methods:

- `end_instant_hold`: use the source hour instant CF for the modeled interval.
- `trapezoid_with_first_endpoint`: average adjacent source instants for subsequent hours, with first-hour source endpoint fallback.

Both are author-chosen numerical approximations. Neither is publisher-certified physically hour-integrated generation. Wind/PV points are instantaneous while demand is hour-ending; neither run resolves that fundamental observational mismatch.

## Authenticated primary numerical checks

- **192 / 192 LP optimal**, with all required conservation guards.
- **96/96 frozen original trapezoid LP objectives reproduced** within the original $0.10 acceptance tolerance.
- **64** complete 0h/4h/8h scenario triplets, **32** hour-method paired 4→8h energy annuity contrasts, **16** hour-method paired state–weather county-siting contrasts.
- Maximum absolute 4→8h incremental annual operating-value difference due to approximation mode among 32 county/state/year cases: **$1.08983665 per added kWh-year**.
- Across 32 year/state/geographic cases, **one** binary decision under the illustrative $10 energy-only cost screen changes between hour methods.
- Across the 16 year/state pairs, the EIA-minus-ReEDS-potential county-siting *signed continuous* effect agrees in **15/16** and disagrees in **1/16**, **AZ 2013** (near zero under both hour approximations).
- The **illustrative AZ 2012 EIA spatial screen flip** occurs under the trapezoid approximation only, **not** under the instant-hold approximation. Thus it is **not numerically robust** to the two stated hour-integration approaches.

## Critical Arizona 2012 exact comparisons

| Hour treatment | ReEDS source potential ($/kWh-year) | EIA2025 operating county fractions ($/kWh-year) | EIA minus potential | Does $10 county-siting screening flip? |
|---|---:|---:|---:|---|
| Instantaneous end-point hold | **11.900281** | **10.875999** | **−1.024282** | **No** — both above $10 |
| Noncyclic trapezoid | **10.955400** | **9.868276** | **−1.087124** | **Yes** — potential above, EIA below $10 |

The *direction* of AZ 2012 county-siting effect is robustly **negative** under both conventions; the binary screening interpretation is not.

## Sixteen state×weather differences: EIA minus developer potential

All in $ per additional kWh-year of 4→8h energy capacity, instant-point hold then trapezoid:

| Weather year | AZ | CO | ID | WY |
|---|---|---|---|---|
| 2010 | −0.214192 / −0.340861 | +0.133865 / +0.385705 | +2.744076 / +2.652646 | +2.281249 / +2.269902 |
| 2011 | −0.436790 / −0.595612 | −0.437795 / −0.345945 | +2.994550 / +3.062122 | +2.903595 / +2.786870 |
| 2012 | **−1.024282 / −1.087124** | −0.363516 / −0.277404 | +1.750607 / +1.655040 | +2.468808 / +2.436991 |
| 2013 | **−0.080980 / +0.021245** | +0.173898 / +0.207267 | +1.866010 / +1.806916 | +2.472791 / +2.371694 |

AZ 2013 is the sole sign disagreement, and both estimated changes are small compared with the other state-year comparisons. A sign check alone must not be described as complete value robustness or statistical significance. With only four deliberately selected historical weather years, counts such as 15/16 do not measure weather or future-climate probabilities.

## Updated scientific hierarchy for journal publication

**Supported main result:** The estimated sensitivity of marginal *variable operating cost savings* to available-resource-potential versus observed 2025 operating county renewable shares depends on location and historical meteorological reference. The effect's sign is consistent between the two hour approximations in 15 of 16 state–weather comparisons, and materially positive for ID and WY throughout this modeled panel.

**Conditional illustrative example:** The Arizona 2012 $10/kWh-year *battery energy-only* screening crossing exists with one hourly numerical treatment but not the other; report this as fragility of threshold-based inference, not demonstrated investment attractiveness.

**Still unproven:** Hour-ending integrated generation, real 2030 generator-location forecasts, true project costs/financing and market revenues, network/adequacy behavior, future SSP climate-change attribution. Nonleap reference weather years have 24 interpolated Feb29 CF points and omit native Dec31; source weather, 2025 EIA installed county shares and 2030 projected demand are noncontemporaneous. Independent published integrated-hour renewable power output or validated observation remains a separate scientific admission gate.

## Proposed concise manuscript text

*A source-native paired hour-discretization sensitivity was conducted across all 96 original county-siting and historical-weather combinations, applying both an instantaneous-endpoint hold and a noncyclic trapezoidal approximation to wind and PV source points. All 192 LPs were optimal, and the original 96 trapezoidal objectives were replicated within their prespecified $0.10 tolerance. The sign of the continuous EIA-minus-developer-potential county-siting effect agreed in 15 of 16 state–weather comparisons; Arizona in 2013 alone changed from −0.081 to +0.021 dollars per additional kWh-year, both near zero. In contrast, the illustrative Arizona 2012 $10/kWh-year additional battery energy-cost screening reversal obtained with the trapezoidal approximation was absent with end-point hold (11.900 vs 10.876 dollars per kWh-year for potential versus operating county shares); the trapezoidal case gave 10.955 versus 9.868. The binary threshold result is therefore sensitive to the hourly conversion method, even though the local spatial value difference remained negative. These are numerical sensitivity results for instantaneous point-sampled renewable CF and do not independently establish physically integrated hour-ending renewable generation.* 

## Citation links

- [192 verified original-source LP and all 8 source outputs](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43317414772/artifacts/13989123990)
- [Original 96 LP](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182390/artifacts/13976060428)
- [Original source-year weather calendar audit](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182402/artifacts/13976245398)

**Study status:** The hour-approximation sensitivity is verified, not a proof of authentic integrated hourly wind/PV output. All earlier original 96 and 24 LP files remain unchanged.
