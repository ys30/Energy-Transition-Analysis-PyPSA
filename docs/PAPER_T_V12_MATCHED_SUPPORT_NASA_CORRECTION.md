# Paper T v12 — Paired-support correction of the NASA POWER external clock control

**Status:** confirmed original NASA POWER JSON bytes, exact SHA256, and passing independent recalculation CI [#42419334016](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42419334016). No new API values, physical EFS clock correction or additional simulation.

## Why this correction matters

In v11, the source-reported *naive same-label* MAE covered all **96** original hourly labels, whereas the *publisher-clock-normalized* MAE covered only **89** nonwrapping physical-hour correspondences (7 hours excluded at the calendar boundaries for the documented UTC→LST −7 h transformation). The numbers are individually valid but compare **different supports**.

v12 recalculates *both treatment arms on the identical 89 original UTC-anchor hours* and labels the 96-hour raw result as a separate descriptive benchmark.

| Experimental outcome | Hourly sample support | Actual original-source NASA T2M MAE |
|---|---:|---:|
| **Primary paired comparator: incorrect same-label join** | 89 UTC anchors also retained by converted arm | **8.186629213483148 °C** |
| **Primary paired comparator: NASA publisher UTC→LST conversion** | The identical 89 UTC anchors | **0.000000000000000 °C** |
| Supplementary descriptive same-label join (v11) | All 96 original literal-label pairs | 7.787395833333335 °C |

The published-source coordinate at 35°N, 105°W lies in the NASA LST band with `LST=UTC−7h`. The matched subset is defined by calendar overlap, **not optimization of offset against temperature data**. This is not a confidence interval, an independent observation validation, or 8.1866°C of forecasting improvement.

## Provenance and exact original-source files

The archive in [run #42415066759](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42415066759) contains the source UTC and LST response JSON, with original SHA256:

```text
3d24f1604da17daea9126c7384ec9f4a9132760e224a7cab3d3c833feea81837  nasa_power_hourly_UTC_original.json
1bf50d3c1852e100e4c8dfb4989c56a93fa86cde9beaa097f828355612f4f886  nasa_power_hourly_LST_original.json
```

The subsequent CI **downloads those exact original JSON bytes**, independently checks SHA256, uses them as input, and emits a new source-derived JSON result. Code and tests:
- `src/energy_transition/paper_t_nasa_power_external_clock.py`
- `tests/test_paper_t_nasa_power_external_clock.py`
- `.github/workflows/paper-t-nasa-power-clock.yml`

The **new headline comparator** is 8.1866 vs 0°C on 89 matched anchors. When replicating, ensure `naive_equal_label_on_same_89_utc_anchors_mae_celsius` exists and the `matched_utc_anchors_for_both_comparison_arms` count is 89.

## What is and is not justified by the experiment

NASA POWER is an independent **source family relative to EFS/ReEDS**, but the two time-standard responses are different representations of the **same NASA product**. The exact zero difference after an explicit NASA-published transform is expected. The sample is one longitude and four days. No independent verification of an unrelated organization’s timestamps, model performance comparison, forecast benefits, or broad proof of the six-gate passport has been done.

The original EFS2020 physical `LocalHourID` timestamp is still unknown; no external weather-EFS join is admitted. This is an internal comparison-method correction ahead of coauthor review, not a claim of a new causal finding.

**Publication assessment:** The verified paired support and explicit abstention policy make Paper T more credible as an audit/methods manuscript, but publication still depends on novelty relative to established standards, suitable archive licensing, independently documented EFS time provenance (or a clear unresolved result), coauthor review and editorial fit.
