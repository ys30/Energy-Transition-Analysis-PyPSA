# Paper S — 15-year fixed-load geographic sensitivity: per-hour-mode results admitted for manuscript revision (2026-11-14)

**Source:** successful GitHub Actions run [43651682920](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43651682920), artifact `paper-s-all15-720lp-fixed2030demand-source-validated` (id 14137831093), input `paper_s_all15_120_siting_comparisons.csv`, `paper_s_all15_60_hour_method_pairs.csv`. This note is an editorial interpretation of **previously verified** source results, NOT a new LP solve or manuscript submission release.

**Design:** 15 original ReEDS source years 2007–2013 and 2016–2023; four states AZ CO ID WY; two county weighting scenarios; three storage durations; two hourly sample-to-energy approximations = 720 LPs, 240 triplets and 120 spatial comparisons (60 year-state pairs per method). Fixed ReEDS2022 2030 load adopts weather-reference 2012; non-2012 demand/wind/PV are **not contemporaneous**. County potential resource classes are still used within each county for both weighting schemes; EIA2025 weights are NOT an empirically validated site-level reconstruction.

## Trapezoidal endpoint approximation
EIA2025 county-share minus ReEDS county-resource-potential marginal 4->8h storage operating value, USD/kWh-year, each state 15 source weather years. Quantiles use pandas default linear interpolation; n=15 for each state, **not independently sampled population years**.

| State | Q1 | Median | Q3 | Min | Max | Positive years |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AZ | -0.576321 | -0.340861 | 0.119384 | -1.087124 | 0.374850 | 6/15 |
| CO | 0.019233 | 0.410384 | 0.580985 | -0.345945 | 0.722707 | 11/15 |
| ID | 1.951894 | 2.337690 | 2.656540 | 1.631348 | 3.062122 | 15/15 |
| WY | 2.420234 | 2.636534 | 2.843490 | 1.758072 | 3.707935 | 15/15 |

## Endpoint-hold approximation

| State | Q1 | Median | Q3 | Min | Max | Positive years |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AZ | -0.556277 | -0.214192 | 0.081836 | -1.024282 | 0.289643 | 5/15 |
| CO | -0.060782 | 0.277415 | 0.475746 | -0.440989 | 0.673309 | 11/15 |
| ID | 1.956962 | 2.361725 | 2.724477 | 1.719399 | 2.994550 | 15/15 |
| WY | 2.497304 | 2.702031 | 2.890450 | 1.832968 | 3.745791 | 15/15 |

**Hour approximation sign agreement:** 59/60 year-state geographic differences have the same direction in the two original-source approximations. One discordance, Arizona 2013: hold -0.080980 and trapezoid +0.021245 USD/kWh-year. This near-zero cross-over matters for qualitative thresholds; neither approximation authenticates physical integrated hourly generation.

## Permitted manuscript wording

> Across 15 original ReEDS historical weather references, under a fixed 2012-weather-based 2030 demand profile and the trapezoidal source-CF hour approximation, the EIA2025 county weighting yields a positive 4-to-8-hour marginal storage operating-value difference relative to county resource-potential weights in all 15 weather references for Idaho and Wyoming. Arizona and Colorado are not uniformly positive, and 59 of 60 state-by-weather sign contrasts agree between two numerical hour conventions. The analysis establishes sensitivity to the assumed county allocation, not the observational superiority of EIA2025 weighting or actual 2030 profitability.

**Admission gates remaining:** historical same-weather load LP underway in separate workflow; must not overwrite this fixed-demand result. No EIA930 external profile calibration or observed resource-class reconstruction yet. BAT cost annualization / EIA930 validation pending. Do NOT summarize historical same-year LPs as passed prior to artifact check, and do not say the model is a solved PyPSA transmission-network model (it is SciPy/HiGHS copperplate).
