# Idaho/source-time forensics — nonwrapping lag robustness audit

## Objective

A previously successful independent original-source comparison established 33 core-West state/year pairs of NLR 2020 EFS Reference/Moderate against the separately published 2022 ReEDS EFS_REFERENCE HDF5. Annual MWh was close, but hourly EFS `LocalHourID` differed from native HDF5 hour positions. Fixed shifts −2/−3 hours brought 30 of the 33 state/year sequences to within 1 MW hourly; Idaho retained much larger differences.

**Methodological risk in the original test:** `np.roll` wraps December to January at the edges. A year-round real-weather join must not silently assume those boundary hours represent the same calendar. The new nonwrapping audit explicitly discards the `abs(offset)` edge hours and measures *only physically overlapping source-series positions*. This makes each lag rank interpretable without inventing values across the annual boundary, though it still does not certify the sources' clock.

## New source checks

- Original EFS2020 verified state/year/ordinal demand archive, GH Actions `41262154939`.
- Publisher-MD5-verified separate ReEDS2022 `EFS_REFERENCE` HDF5, published UTC−06 native 2012 source index.
- All 33 state-year profiles, each with 8,760 source rows.
- Candidate integer offsets −12…+12 hours. For offset k, compare EFS ordinal index i against ReEDS index i−k **only where both indices exist**. Do not wrap; report excluded edge hours, MAE, RMSE, p99/max error, number of residual hours greater than 1 MW, second-ranked lag and best-minus-runner-up MAE difference.
- Independently test exact-clock, intentionally shifted but annual-total-identical, boundary corruption and mixed-curve fixtures.
- No actual UTC conversion or synchronized renewable-hour join. All output labels remain source-index diagnostics.

[Workflow: ReEDS/EFS source nonwrapping lag verification](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs2020-reeds2022-nonwrap-lag.yml). The new output `efs_2020_2022_nonwrap_33_pairs.csv` and JSON metadata will be available in the CI artifact if the original-source workflow passes.

## Source geographic limits to interpreting Idaho

The [original 2020 EFS publisher description](https://data.nlr.gov/submissions/126) states profiles are **aggregated to state, sector and select subsector level**, not authored as a census tract/timezone-county-by-hour feed. Thus the existing raw EFS dataset cannot by itself establish Idaho's cross-timezone **population split** or which utilities contribute which hourly loads. ReEDS/PyPSA geography information and external timezone boundaries do not independently resolve this exact input provenance.

The previous unconstrained **two-shift linear mixture** produced Idaho −2-shift weights ~0.8344 consistently across three years but still thousands of hourly errors above 1 MW. That mixture should be presented as an **unidentified statistical fit only**, not a physical Mountain/Pacific attribution. The present nonwrapping lag audit separately tests whether edge wrapping caused a material part of the residual or shift preference.

## Admission decision

**No 2020 EFS hour-to-UTC admission.** Even a stable nonwrapping ±2/3 shift can at most support numerical cross-release source-index correspondence. Reliable physical clock mapping requires the original EFS author/processing implementation (including state/zone/substate aggregation convention, hour ending, weather-year basis, DST, leap-year rule), and weather/resource profiles with appropriate source year and geography. Treat the already successful 540 annual HiGHS storage LPs as EFS-demand-backed synthetic supply sensitivity, not a time-synchronized Western grid forecast.


## Verified original-source results: nonwrapping test passed

[GitHub Actions #42122065064](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42122065064) **passed** on the original archived 2020 EFS state-hour evidence and the separate 2022 ReEDS official HDF5; all 33 state-year candidates were processed and 5 regression tests passed.

**All 33** best offset selections were unchanged from the earlier circular-shift audit. Each candidate comparison excludes exactly two or three edge hours for a −2/−3-hour lag, so it does **not** manufacture annual boundary continuity. For the 30 non-Idaho state/year pairs, every compared hour has an absolute residual below 1 MW after its best shift. The best-lag margin over the second-best lag is substantial, not a near-tie.

| 2030 state | Best nonwrap shift | Best MAE (MW) | Runner-up shift | Runner-up MAE (MW) | Number of remaining hours over 1 MW |
|---|---:|---:|---:|---:|---:|
| AZ | −2 | 0.248619 | −3 | 376.922469 | 0 |
| CA | −3 | 0.247857 | −4 | 1140.803874 | 0 |
| CO | −2 | 0.254004 | −3 | 177.628817 | 0 |
| ID | −2 | 17.264135 | −3 | 80.197738 | **8,367** |
| MT | −2 | 0.249616 | −3 | 48.289625 | 0 |
| NM | −2 | 0.249274 | −3 | 96.295090 | 0 |
| NV | −3 | 0.252613 | −4 | 149.849590 | 0 |
| OR | −3 | 0.248501 | −4 | 206.646516 | 0 |
| UT | −2 | 0.248250 | −3 | 111.837301 | 0 |
| WA | −3 | 0.248293 | −4 | 397.070324 | 0 |
| WY | −2 | 0.249299 | −3 | 37.147228 | 0 |

**Idaho remains unexplained in all three years:** its −2 h nonwrapping MAE is **17.264 MW (2030), 19.304 MW (2040), 22.100 MW (2050)**, leaving **8,367, 8,408, 8,441** source-overlap hours above 1 MW, respectively. Eliminating two wrapped boundary hours therefore does **not** explain Idaho's discrepancy.

### Causal interpretation and data limits

- The source-level stability of the best offset is strongly supported **numerically**, but shifts are from a computational source-index search, not independently authenticated timezone conversion rules.
- The published original EFS source has **state/sector/subsector** granularity, not a confirmed within-Idaho load-by-timezone time series. It cannot by itself certify that Idaho's exceptional pattern derives from its geographic timezone split.
- The year-end omitted comparison hours are **unresolved boundary hours**, not validated values that can be silently rescaled or appended to wind/solar input.
- As before, nothing in this audit constitutes a time-aligned wind/solar resource experiment, physical source-specific generator attachment or calibrated Western network OPF.

**Manuscript status:** suitable for a provenance and identifiability *Results* subsection documenting shift robustness and the Idaho counterexample; not a sufficient basis for a real grid operation or storage benefit assertion.
