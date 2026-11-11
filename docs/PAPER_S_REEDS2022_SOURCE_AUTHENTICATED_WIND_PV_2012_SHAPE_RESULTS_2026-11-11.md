# Paper S — verified 2012 county wind/PV joint source-CF results (11 Nov 2026 UTC)

## Source lineage and execution

- Original ReEDS2022 county wind and PV original HDF5 MD5-authenticated and 2012 weather extracted: [workflow 42962740548](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42962740548), BOTH wind/PV SUCCESS. Derived artifacts contain 8760 hourly wind and PV CF values for AZ/CO/ID/WY, plus source audit metadata. Original vendor HDF5 is not redistributed.
- Same-hour, independently checked reference-weather *instantaneous* wind/PV joint-source assessment: [workflow 42964322745](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42964322745), SUCCESS. Artifacts: `reeds2022_2012_wind_pv_instantaneous_state_shape_diagnostic.json` and `reeds2022_2012_wind_pv_state_hour_of_day.csv`.
- ReEDS model years 2030/2040/2050 refer to projected demands conditioned on 2012 reference meteorology. This is NOT realized future generation.

## Reproducible native-reference results

All correlations below are Pearson correlations of the source-aligned *instantaneous* 2012 wind and PV state profiles (n=8760). Neither hourly energy nor demand/wind co-optimization has been asserted.

| State | Wind mean CF | PV mean CF | Wind/PV instantaneous r | Hours both CF<0.1 | Hours both CF>0.3 |
|---|---:|---:|---:|---:|---:|
| AZ | 0.201192 | 0.251183 | -0.145807 | 1305 | 585 |
| CO | 0.282574 | 0.229560 | -0.269305 | 423 | 830 |
| ID | 0.245264 | 0.191740 | -0.204199 | 972 | 546 |
| WY | 0.348053 | 0.206051 | -0.227259 | 379 | 1094 |

These figures are source-derived observations conditional on ReEDS publisher weather and available-resource class/county capacity weighting, NOT observed operational wind/PV or projected built fleet. The r values suggest anticorrelation at the state level for all four states but cannot by themselves establish storage benefit, adequacy, hours of shortage or quantified grid savings.

## Remaining admission constraints

1. Official ReEDS CF labels are instantaneous at hour, whereas source demand is hour-ending MWh/h. Identical timestamp strings establish comparable clock labels, not integrated energy over the preceding hour. Explicit convention and sensitivity remain required for LP.
2. County supply-curve available resource MW is not installed MW. Choose and document installed scenario caps, matched PV DC denominators and wind AC denominator.
3. The stored 2012 values have noncyclic year boundaries. A trapezoidal approximation for the first hour requires a genuine previous-hour sample; no last-hour wrap.
4. The new ReEDS2022 resource-backed LP and demand results have NOT been run. Keep original EFS2020 synthetic LP frozen and do not merge claims.
5. The unrelated overall CI at 42962740529 failed on `research/paper_t_hypothetical_downstream/paper_t_directional_v3.py` due to `KeyError: net_peak_clock_hour`; source original HDF5/CF jobs completed independently and are not the cause.

This note is safe to publish as source-verified **resource-shape diagnostics**, not an empirically joined generation/dispatch model.
