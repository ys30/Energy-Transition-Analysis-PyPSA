# Paper S — ReEDS2022 common-AC cost and battery efficiency robustness protocol (2026-11-11)

## Required original source and source-unit controls

- Original publisher 2012 resource data and four-state county-weighted CF audited at [run #42962740548](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42962740548).
- Source 2030 demand HDF5 must satisfy exact MD5 `7b2055d43200744a16a8c4fed68b1a17`, with fixed CST original 2012 reference-year time labels.
- Main comparison must use common AC renewable nameplate: publisher ReEDS utility PV original CF = MW_gridAC / MW_arrayDC; AC-normalized CF uses ILR 1.34 exactly once, clipped only for documented four-decimal source rounding ≤1e−4 above 1. This does not imply measured actual AC installed fleet or validated future PV inverter ratios.
- Native resource CF is **instantaneous at timestamp**, not hour-ending MWh; model uses trapezoidal approximation and first-hour endpoint fallback; this is not publisher-certified hour-integrated generation.

## Locked 108-case cost-efficiency experiment

- Demand projection: 2030, four states Arizona, Colorado, Idaho, Wyoming; source meteorology 2012.
- Hypothetical AC total wind+PV nameplate = 1.5× demand peak; 50% wind / 50% PV **common AC**, no calibrated installed fleet.
- Battery discharge/charge power = 25% of demand peak; durations 0h, 4h and 8h.
- Battery round-trip efficiency = 0.80, 0.90, 0.95.
- Variable dispatch costs: renewable $5/MWh; firm generation $60, $90, $120/MWh. These are **illustrative assumptions**, not current published LCOE, retail tariff or contracted fuel prices.
- Each combination solves a full 8760-hour one-state copperplate HiGHS LP with terminal SOC zero and strict energy-balance checks: 4×3×3×3 = **108 original LP solves** and **36 exact 0/4/8h triplets**.
- Original accepted Arizona benchmark must be reproduced for 90% storage round-trip efficiency and $90/MWh firm cost: **4→8h incremental energy-only annualized cost limit $10.9554/kWh-year** at this one scenario, tolerance ±$0.001/kWh-year.
- Zero-storage LP objective must be independent of an irrelevant battery efficiency input at the same state and firm generation cost (≤$0.05 variation).

## Correct marginal financial interpretation

Compare 8h to 4h with identical storage power, AC renewable portfolio, weather year, demand year, variable costs and efficiency. The incremental cost threshold is

`A_E,max = [Objective(4h) - Objective(8h)] / [E(8h) - E(4h)]`

in USD/kWh-year. A value above a **hypothetical** $10/kWh-year annualized energy hardware cost means the simulated additional operating value covers only that assumed energy annuity, not all real project costs. No degradation, investment financing, installed capital costs, O&M, transmission, reserves, scarcity, capacity value, reliability, or battery replacements are included. The threshold is reference-weather-simulation-specific, not predicted actual annual net profit.

**Admission rule:** do not claim efficiency/cost robustness until original 108-LP workflow is green and the full 36-pair result CSV and manifest have been archived. Original EFS2020 Paper S and earlier heterogeneous-source-MW ReEDS scenarios remain separately frozen. Full repo CI continues to have a separate Paper T legacy helper test failure until repaired independently.
