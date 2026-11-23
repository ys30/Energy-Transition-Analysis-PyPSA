# Paper S — Supplementary Information v2 (source-audited editorial draft, 2026-11-22)

**Companion main text:** `PAPER_S_INTEGRATED_ENGLISH_MANUSCRIPT_V2_2026-11-22.md`.

**Scope:** technical audit and robustness tables for the 15-weather-year hypothetical four-state copperplate LP, not independently validated grid dispatch or financial returns. This SI should not be labeled journal-submission ready until figures, references, source hashes and manuscript Word render are reviewed.

## S1. Frozen experimental populations and non-interchangeability

| Cohort | Main comparison | Source-backed scope | Data identity |
|---|---|---|---|
| Original 2010–2013 | county-weight source and hour conversion sensitivity | 96 LPs plus separate 192 LP hour-method comparison | historical four-year subexperiment |
| Full weather-year source | 15 original weather years 2007–2013 and 2016–2023 | source-authenticated 720-LP fixed-demand and separate 720-LP weather-matched-load cohorts | distinct fixed vs historical demand normalization |
| Frozen 3×3 grid | R=1.0, 1.5, 2.0 × AC wind 25%, 50%, 75% | 2,880 freshly optimized LPs, plus source-based reuse; 1,080 4h-to-8h incremental value cases | 4 states, 15 weather years, 2 county weighting schemes |
| CO wind continuity | R=2.0 and 40%, 60% wind AC | 720 new LPs | original 50% retained independently |
| CO hourly dispatch | R=2.0 and wind 40%, 50%, 60% | 180 independently solved optimal LPs; hourly 2012/2023 traces | descriptive SOC/bound and dispatch accounting |
| Annual source-only SOC | state-prescribed R (CO=2.0, others=1.5), wind 50% | 120 8,760-hour source cases, 720 energy-delivery LPs | 24h, 168h, 8760h SOC horizons |
| Common-R SOC sensitivity | R=1.5 in all four states at wind 50% | CO: 180 new LPs; other states: 540 reused LPs | 120 source cases, 60 siting-year pairs |
| ATB screen | 2030 battery extension costs against frozen 3×3 | 19,440 comparisons of same 1,080 duration values to 18 source-labeled hurdles | 12 unique numerical cost thresholds |

The four-year 96/192 subexperiments must not be added as additional years of a 15-year source cohort. A positive or negative median difference is not a claim about an empirically installed 2030 fleet.

## S2. County/fleet/source-clock definitions

ReEDS 2022 original wind/utility PV county-class data and county supply curves use authenticated publisher files with MD5 pins in source-backed CI. Resource shapes are historical, and source hourly labels have a native fixed-CST convention requiring careful point-to-hour treatment. Demand is from an authenticated EFS reference HDF5. County potential is based on original resource supply curves; EIA-860 operating-generator county weights refer to the 2025 fleet. Applying them as spatial aggregation alternatives does not reproduce the actual 2023 balancing-authority fleet.

## S3. Colorado R=2 wind-mix local sensitivity

Median within-source-year paired EIA-minus-potential geography contrasts, 15 years; units are illustrative model USD/(additional kWh-year).

| AC wind share | 25% | 40% | 50% | 60% | 75% |
|---|---:|---:|---:|---:|---:|
| CO paired median at R=2.0 | -0.164 | -1.819 | -2.178 | -0.301 | +2.615 |

At 50% wind, the paired effect is lower than both 40% and 60% in 12/15 source weather years; all 15 weather years have negative sampled midpoint curvature. This is not an estimate of a smooth optimum or proof of a unique SOC saturation threshold. The 40/60 cases are actual new source-authenticated LP solves, not accounting-based approximations.

## S4. Colorado hourly descriptive diagnostics

Across Colorado source-year optima, median number of 8h LP hours with charging at rated power and SOC at its energy limit:

| Wind share | EIA charging-bound h | ReEDS charging-bound h | EIA SOC maximum h | ReEDS SOC maximum h |
|---|---:|---:|---:|---:|
| 40% | 1733 | 1872 | 196 | 237 |
| 50% | 1154 | 1333 | 139 | 168 |
| 60% | 624 | 638 | 104 | 90 |

Matched 15-year median EIA-minus-ReEDS *incremental* firm displacement differences (MWh) are -246,794.80, -295,403.17 and -40,894.41 at 40%, 50%, 60%. These are internal LP accounting indicators with solution nonuniqueness caveats, not an exogenous causal mechanism.

## S5. Four-state common-R=1.5 analysis

| State | R | Median EIA minus ReEDS modeled value | Daily r | Weekly r | Annual r | Daily sign | Weekly sign | Annual sign |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| AZ | 1.5 | -0.340861 | 0.019414 | 0.958747 | 1.0 | 9/15 | 13/15 | 15/15 |
| CO | 1.5 | +0.410384 | 0.368747 | 0.919659 | 1.0 | 12/15 | 15/15 | 15/15 |
| ID | 1.5 | +2.337690 | 0.143886 | 0.963586 | 1.0 | 15/15 | 15/15 | 15/15 |
| WY | 1.5 | +2.636534 | 0.826549 | 0.952937 | 1.0 | 15/15 | 15/15 | 15/15 |

Original CO R=2.0 at 50% wind: -2.177855 median modeled siting contrast versus CO R=1.5 +0.410384. These medians' sign difference is a conditional scenario observation. Do not report it as a weather-year paired R difference, a p-value, or a real-world fleet siting effect.

## S6. Exact cost screening population and currency limitations

At the lowest 2030 ATB source-pinned hurdle (Advanced, 4% rate), crossings in the 1,080 duration case grid are 213 total: AZ=89, CO=60, ID=34, WY=30. By penetration/wind design: R2.0/wind25% 120/120; R1.5/wind25% 61/120; R2.0/wind50% 32/120; every R1.0, 75%-wind and other unlisted design 0. Moderate 7% hurdle 27.869 has 0 crossings. The 18 labeled hurdles include repeated values; raw 954 crossed rows across 19,440 comparisons are not independent observations. The model firm-generator $90/MWh value is illustrative and not reconciled to ATB 2023 USD.

**Prior SI S7 correction:** In the separate frozen 2,160-row ATB screen the AZ/2020 source-potential Advanced/4% value is **15.122061** model USD/(additional kWh-year), its source-pinned cost threshold is **16.049194** in 2023 USD/(additional kWh-year), and the ratio H/V is **1.06131001**. The superseded incorrectly printed value 3.732231 must not appear in a final submission or Zenodo package. This example belongs to a distinct original baseline population.

## S7. Source-only SOC horizon scope and limits

In the original 120 annual cases, correlations of the input-only siting effect and economic LP paired value effect at daily/weekly/annual SOC horizons were AZ 0.0194/0.9587/1, CO 0.3884/0.9546/1, ID 0.1439/0.9636/1, WY 0.8265/0.9529/1. All four original cohorts combined agreed on signs in 53/60, 58/60, 60/60 years across daily, weekly, annual horizons. Perfect annual correlation follows near-structural objective equivalence, not external causal identification. Fixed-duration deliverable energy must satisfy annual >= weekly >= daily; incremental 8h−4h delivered energy need not.

## S8. EIA-930 diagnostic is only a different-geography source shape comparison

IPCO 2023 BA observed shape, 8,743 valid zero-shift UTC-hour observations: wind Pearson 0.7344 (ReEDS potential weights) versus 0.7335 (EIA 2025 county weights); solar 0.9539 versus 0.9694. A +1-hour solar placebo can increase the correlation and must not be selected as verified clock without source-label confirmation. Idaho state resources and IPCO BA reported generation are not coterminous. These statistics do not validate installed capacity, generation by class or a 2030 electricity market forecast.

## S9. Audit references and source artifact identities

- Full 3×3 source: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44209543001
- Wind 40/60 source: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44449229739
- Colorado hourly: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44453880808
- Cost screen: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44463644688
- Annual source-only recovered: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44861775851 (artifact 14692567952)
- Common-R physical comparison: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44919128370 (artifact 14714718140)
- 720×720 fixed/matched comparison: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44919128403 (artifact 14712877100)
- Original SI S7 2020 AZ correction: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43678422986
- Original published input data reference hashes and licensing: see `PAPER_S_ORIGINAL_REEDS_DATASET_BIBLIOGRAPHY_74_REFERENCES_QA_2026-11-18.md` in this branch.

**Unresolved gates:** journal-specific reference list and author declaration, matching final figure IDs/numbering, exact internal DOCX and PDF visual QA, third-party license scoping, source/release checksum, and durable deposited DOI. Freeze original solved LP cases and all other projects.
