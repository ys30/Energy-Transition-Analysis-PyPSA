# Paper S — 2023 IPCO deseasonalized residual-shape verification (2026-11-23)

## Provenance

Original authenticated source-hour artifact: GitHub Actions run [44463644188](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44463644188), ID **14506529618**, file `ipco/I6_IPCO_original2023_matched_pairs.csv.gz`. Actual downloaded file contains **17,486** rows: 8,743 for 2023 solar and 8,743 wind, each aligned to IPCO BA adjusted generation by identical UTC hour-end. Excluded negative or missing adjusted-MW values and held model shift at UTC=0.

## Descriptive residual method

Normalize each fuel's observed adjusted-MW and both independent county-weighted source-CF series by their same-cohort means. Convert source UTC to fixed CST (UTC−06:00), compute each series' original-year month × local-hour mean, and subtract it from that normalized series. Correlate observed and modeled within-bin residuals using exactly the same hour population. This is **one year's deseasonalized within-2023 diagnostic**, not cross-year out-of-sample model testing.

| Fuel | N | Original ReEDS potential raw r | EIA2025 county-weight raw r | Potential residual r | EIA residual r | Residual Δr = EIA−potential | Bootstrap descriptive 95% interval |
|---|---:|---:|---:|---:|---:|---:|---|
| Solar | 8743 | 0.953877 | 0.969391 | 0.819215 | 0.906099 | +0.086884 | [+0.069617, +0.107404] |
| Wind | 8743 | 0.734364 | 0.733499 | 0.699004 | 0.697541 | −0.001463 | [−0.022566, +0.020352] |

Uncertainty: 1000 monthly stratified calendar-day-block bootstrap replicates, original residualization climatologies held fixed; seed 20261123. This preserves some within-day dependence but **does not** protect against multi-day serial correlation or independent weather year uncertainty. The intervals must not be described as general out-of-sample performance significance.

Scientific limits: IPCO BA != entire Idaho state; EIA 2025 state-county fleet weights != original 2023 IPCO installed fleet; point CF native source vs hour-ending observed generation still needs physically equivalent confirmation. Solar residual advantage is useful for **descriptive source-shape sensitivity** only.

## Editorial implications

Include in Main Results §3.7 and Discussion, with full derivation and limitations in SI §S10. Do not use this to claim external deployment, physical class-level 2023 fleet, real-world market revenue, or generator-by-generator validation.

Fig. 3 correction: the 2026-11-22 Main Fig 3 is ATB **count exceedances** and is *not* a mean-value bar chart. A separate 15-year **median paired geography-effect** bar figure was rebuilt from frozen `paper_s_design_grid_540_paired_siting_effects.csv`; it should be labeled supplemental or consistently renumbered if made main text, not silently replace the original count figure.
