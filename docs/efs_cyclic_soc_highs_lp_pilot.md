# Project B: cyclic HiGHS storage LP pilot (168 ordinal hours)

## Purpose and evidence boundary

The previous 27 full-year storage sensitivity scenarios used sourced EFS demand but deliberately synthetic renewable supply and greedy battery scheduling. Several had a positive terminal SOC, preventing equal-boundary comparisons.

The new experiment optimizes the original first **168 hourly ordinals** for the **two largest-demand zones per year**, in planning years 2030, 2040 and 2050. It crosses 3 synthetic supply profiles with 0/4/8 hour battery durations, for **54 expected optimizations** across three year jobs.

The optimization is a real linear program solved by HiGHS, but the supply, costs, battery and independent-zone topology remain hypothetical; it is **not** a real Western grid dispatch model.

## LP equations and assumed parameters

For each zone and ordinal t, minimize total assumed variable cost:

    min sum_t [5*(renewable_direct_t + battery_charge_t) + 90*firm_t]

Subject to:

    renewable_direct_t + battery_charge_t + unused_t = assumed_renewable_available_t
    renewable_direct_t + battery_discharge_t + firm_t = source_EFS_load_t
    SOC_t - SOC_(t-1) - sqrt(0.9)*battery_charge_t + battery_discharge_t/sqrt(0.9) = 0
    SOC_initial = SOC_terminal = 0
    0 <= battery_charge_t, battery_discharge_t <= 0.25*zone_peak
    0 <= SOC_t <= battery_duration_hours*(0.25*zone_peak)
    0 <= firm_t <= 1.2*zone_peak
    0 <= renewable_direct_t <= min(assumed_available_t,source_EFS_load_t)

Renewable nameplate remains 0.9 times each zone's own demand peak. Hypothetical capacity-factor shapes remain constant 0.5 or the two opposite purely mathematical ordinal-24 waveforms, never asserted as physical day-night wind/solar observations.

## Comparability and verification

The solver reports optimality, energy mass and primal equality residual, and terminal SOC. Original greedy storage is replayed on the same demand/profile, but its cost is **directly comparable only when the greedy terminal SOC is also zero**. The new output flag cyclic_lp_vs_greedy_cost_directly_comparable enforces this boundary.

The scoped workflow is [EFS cyclic HiGHS storage LP](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-cyclic-storage-lp.yml). Original archived EFS/LAF demand comes from Actions run 41281576025. Output artifacts contain per-year CSV and JSON. **Check the latest run before claiming empirical execution success.**

The exercise does not admit weather synchronization, real plant-to-bus POIs, interzonal transmission, battery capex, or calibrated Western OPF. The next engineering step is a full-8,760-hour cyclic optimization after the scoped solve and reference-boundary checks pass.


## Verified original-archive CI results — 2026-11-05

All three year-matrix jobs completed **successfully** in [run #42103133043](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42103133043). Each year selected original source-load zones **p28** and **p33** for the first 168 ordinals; 2 zones × 3 supply shapes × 3 durations = 18 LP solves/year, **54 solved cases** total. All reported zero terminal SOC and optimal HiGHS solver status.

For hypothetical wave A, **across only the two selected zones and 168 hours**:

| Year | No-battery unused renewable (MWh) | 4h battery unused renewable (MWh) | 8h battery unused renewable (MWh) | Assumed firm generation reduction, no battery → 4h (MWh) |
|---|---:|---:|---:|---:|
| 2030 | 1,013.318 | 0 | 0 | 911.986 |
| 2040 | 1,132.939 | 0 | 0 | 1,019.645 |
| 2050 | 1,297.342 | 0 | 0 | 1,167.608 |

The difference between unused-energy reduction and firm-energy reduction is compatible with the assumed 90% battery round-trip efficiency. Under this **specific week and these two zones**, 4h storage is enough to capture all hypothetical supply surplus in wave A; 8h has no incremental effect. It would be **incorrect** to extrapolate this outcome to the prior 20-zone, full-8,760-hour, *greedy* sensitivity results. Those use a different horizon, potentially positive terminal SOC, and different demand set. No storage economics/optimal investment inference follows.

**Remaining critical gate:** scale to a complete 8,760-hour cyclic LP and test end effects on every admitted zone before writing generalized annual storage conclusions. Supply shapes and costs still require empirical source support.
