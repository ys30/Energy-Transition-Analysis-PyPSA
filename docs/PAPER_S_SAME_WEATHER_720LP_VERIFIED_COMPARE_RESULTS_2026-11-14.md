# Paper S — Independent same-weather historical demand 720 LP versus frozen fixed-2030 demand 720 LP

**Results admitted from genuine authenticated-source successful GitHub Actions runs, 2026-11-14 (Mountain):**
- Fixed projected-2030 demand, weather reference 2012, 720 LP, run [43651682920](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43651682920), artifact 14137831093, `paper_s_all15_120_siting_comparisons.csv`.
- Same-year historic demand at original level and separately normalized to projected 2030 *annual energy*, 720 LP, run [43665299980](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43665299980), artifact 14143076211, `paper_s_same_weather_120_spatial_comparisons.csv`.
- Both archived sets passed 720/720 HiGHS optimal and have maximum hourly balance residual ~7.3e-12 MWh, including 15 source years 2007-2013 and 2016-2023, AZ CO ID WY.
- Contrast uses **trapezoid_with_first_endpoint only** for clean hour-mode pairing, not the other source hour approximation.

## A. Main result: effect of county-share reweighting on marginal 4-to-8 h storage operational value

EIA2025 county MW-share weights **minus** ReEDS source resource-potential county weights, USD/kWh-year. These are conditional avoided variable operational costs (not profits) under a copperplate SciPy/HiGHS LP. Each state contains exactly 15 paired weather-year references.

| State | Fixed-2030 median | Matched historic median | Median within-year change | Fixed-2030 positive | Matched historic positive | Same sign vs fixed |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| AZ | -0.340861 | -0.326367 | -0.099590 | 6/15 | 3/15 | 10/15 |
| CO | +0.410384 | -0.024635 | -0.230813 | 11/15 | 7/15 | 11/15 |
| ID | +2.337690 | +1.948399 | -0.273221 | 15/15 | 15/15 | 15/15 |
| WY | +2.636534 | +2.630832 | +0.042512 | 15/15 | 15/15 | 15/15 |

Overall sign agreement fixed versus historical is **51/60** year-state comparisons. Idaho and Wyoming stay positive in all 15; Colorado changes from 11/15 positive to 7/15 and median crosses zero; Arizona from 6/15 to 3/15. These are descriptive deterministic modeled years, not statistical confidence, real fleet calibration, or evidence that county EIA weight is 'true'.

## B. Why the two historical load modes have identical unit-normalized contrasts

The LP sizes wind/PV AC MW and battery power and energy proportionally to each demand series peak, and all objective costs are linear. Multiplying a full 8760-hour historical demand vector by one positive scalar therefore scales both objective cost savings and added energy capacity by the same scalar, so USD/(added kWh-year) is invariant, up to solver tolerance. Across the 60 year-state spatial effects, maximum absolute difference of the two historical treatments is ~1e-12 USD/kWh-year; the historical_raw and historical_scaled positive-year counts are **not independent robustness observations**. The `historical_weather_shape_scaled_to_2030_annual_energy` branch changes total load, peak load and installed hypothetical power simultaneously; it does not isolate demand *shape* alone. This is a mathematical interpretation restriction, not a second external validation.

## C. Limitations and admission rules
- The original ReEDS 2030 demand in the fixed panel is tied to 2012 weather reference; historical panel uses source-matched weather years but actual historical load levels / normalized historical shapes are NOT independently published future-2030 weather-specific projections.
- The two county weighting alternatives retain original **within-county resource classes**; no proof of actual site-class distributions.
- EIA2025 observed county fleet cannot be equated to historical-year operating fleet or a 2030 installed fleet.
- ReEDS wind/PV CF are publisher **instantaneous** samples; the trapezoid is a model approximation, NOT validated integrated hourly MWh.
- Annual cost hurdle USD10/kWh-year is illustrative; ATB cost / EIA930 observational comparison are **not yet admitted**.
- Source LP is SciPy HiGHS copperplate, not a modeled PyPSA transmission network.
- New manuscript Results text should treat **matched historical** panel as the main load-weather robustness check, and 2030 annual-energy-scaled historical modes as a mathematical rescaling diagnostic rather than independent replicated evidence.

## Recommended publication wording

> Under the matched historical load–renewable weather design, the positive incremental 4-to-8-hour operational-value effect of alternative installed-county wind/PV allocation persists in Idaho and Wyoming for each of the 15 historical weather years. However, Colorado's positive-year count falls from 11 to 7 and its median spatial effect shifts from +0.410 to −0.025 USD/kWh-year relative to a fixed 2012-weather-based 2030 demand profile. Across all 60 state–weather pairs, 51 preserve the spatial-effect sign. This suggests that the demand–renewable weather co-variation materially conditions conclusions in some jurisdictions, without establishing observational superiority of either county-weight assumption.

**Next gates:** reuse the new `reeds2022_load_weather_coupling_comparison.py` with authentic 720 CSVs, validate its objective/duration/geographic matching in CI, then perform EIA930 measured BA wind/PV validation and NREL ATB expansion annualization before final manuscript admission.
