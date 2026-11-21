# Paper S — verified 3×3 wind-share × renewable-penetration sensitivity (2026-11-17)

## Source, validation and frozen-results policy

**Successful** GitHub Actions run [44209543001](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44209543001), artifact **14388326204**, recorded **2880/2880 optimal new LPs** (max absolute equality residual ~7.28e-12 MWh); 360 identical original **frozen** baseline LP cells reused, hence 3240 LP design cells, 1080 4→8h duration values, 540 paired state–weather-year–design siting effects, and 36 15-year state×design-point summaries.

- Fixed original ReEDS projection-year **2030 demand**, 2012 reference-clock support; source years 2007–2013 and 2016–2023, **15 years**, states **AZ, CO, ID, WY**.
- Renewable AC nameplate / demand peak = **1.0, 1.5, 2.0**. Wind share of combined wind+PV AC = **0.25, 0.50, 0.75**. Each design point uses the same two county weights (original developer-available ReEDS potential versus county EIA-860 2025 operating-fleet weights), same fixed storage power 0.25 × load peak, 0h/4h/8h, RTE 90%, trapezoid source-hour approximation, nominal 5 USD/MWh renewable and 90 USD/MWh firm unit variable costs.
- Marginal 4→8h value V = (objective_4h−objective_8h)/added battery kWh. Spatial effect is **V_EIA − V_potential**, in model USD/(added kWh-year).
- Input hashes authenticated in CI. No changes to frozen 1440 LP, 2160 ATB, Paper C-2, or the actual 2×2 wind/PV experimental outputs.

## Main result: full 3×3 grid

Each cell shows `median paired spatial effect / count positive out of 15 years`.

| State | R 1.0, wind 25% | R 1.0, wind 50% | R 1.0, wind 75% | R 1.5, wind 25% | R 1.5, wind 50% | R 1.5, wind 75% | R 2.0, wind 25% | R 2.0, wind 50% | R 2.0, wind 75% |
|---|---|---|---|---|---|---|---|---|---|
| AZ | +0.972 /15 | +1.134 /15 | +0.939 /15 | +1.109 /15 | −0.341 /6 | +0.813 /15 | −0.469 /0 | −0.169 /7 | +0.358 /15 |
| CO | +0.379 /15 | +0.387 /14 | +0.784 /15 | +0.183 /11 | +0.410 /11 | +2.120 /15 | −0.164 /5 | −2.178 /0 | +2.615 /15 |
| ID | +1.007 /15 | +0.342 /15 | +0.546 /15 | +1.475 /15 | +2.338 /15 | +1.628 /15 | +0.717 /15 | +0.688 /11 | +1.209 /15 |
| WY | +0.312 /15 | +0.226 /15 | +0.249 /15 | +1.208 /15 | +2.637 /15 | +2.269 /15 | +1.241 /15 | +1.011 /14 | +0.983 /15 |

Values are medians of **within-year** paired differences. The original frozen design point is R=1.5, wind=50% (center of the table).

Across the 9 designs, **ID and WY have positive 15-year median siting effects in all 9/9 cells**, with positive value in all weather years for **8/9 cells**; the only 15-year sign inconsistency is R=2.0 and wind=50% (ID **11/15**, WY **14/15**). Thus the direction is **robust at the nine sampled design-point medians**, but not universally positive for every year, and cannot be extrapolated beyond the sampled R/wind-share rectangle. Arizona's effect is design-dependent with 3 negative-median cells; Colorado has 2 negative-median cells, notably R=2.0 wind=50%, **−2.177855 USD/(added kWh-year), 0/15 positive**, in contrast to R=2.0 wind=75%, **+2.615353, 15/15 positive**.

## Main/SI figure assignment and reporting

- Main Figure D1: color-diverging 4-state 3×3 heatmaps of **median siting effect**; 0 line implied by diverging color; black outline marks frozen reference R=1.5, wind=50%.
- Main Figure D2 or SI: corresponding **positive weather-year count** 0 to 15, making seasonal and year-wise sign limits visible. Each grid entry derives from 15 year-level pairs, not 15 independently randomized samples.
- Supplement: all 540 paired source rows, 1080 duration rows, 2880 new LP cases, 36 aggregate values, data manifest, SHA-256 and source-pinning details.

## Manuscript-safe conclusions

The operating-county vs resource-potential siting weights produce consistently positive **median** incremental 4→8h storage operational value for Idaho and Wyoming at all nine sampled renewable capacity/design points, whereas Arizona and Colorado have changes in effect sign in several sampled configurations. This is a design-point robustness **sensitivity** analysis, not causal proof of the true operating fleet's accuracy, market revenue, observational calibration, or transmission-aware dispatch. The model's existing 2012-weather-support fixed 2030 demand and source instantaneous CF integration limitations remain.

Source CSVs: `paper_s_design_grid_2880_NEW_lp.csv`, `paper_s_design_grid_1080_duration_values.csv`, `paper_s_design_grid_540_paired_siting_effects.csv`, `paper_s_design_grid_36_state_grid_summary.csv`, and `paper_s_design_grid_manifest.json`. A rendered 4-page English addendum and publication-grade figures D1–D2 were produced as downloadable conversation artifacts, not falsely represented as GitHub binary uploads.

## Next priorities

(1) Integrate these source-verified results into the existing Paper S Results/Discussion, with separate Main and SI references. (2) Pursue EIA-930 matched-boundary full-year validation, especially IPCO/ID and PSCO/CO, with BA/state geographic limitations. (3) Only then evaluate whether the 11-state expansion or further design refinement is warranted.
