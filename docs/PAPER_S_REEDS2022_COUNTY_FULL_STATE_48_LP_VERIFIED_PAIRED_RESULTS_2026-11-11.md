# Paper S — county-native full-state ReEDS2022 real-source 48-LP first results (11 Nov 2026 UTC)

## Accepted calculations and exact provenance

- [Archived authenticated county wind and PV 2012 state CF](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42962740548): complete 8760 source instants for Arizona, Colorado, Idaho, Wyoming.
- [48 original-source demand and real-weather-derived CF LPs](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42965036275): SUCCESS, 4 states × demand model years 2030/2040/2050 × two hour-energy approximations × battery 0h/4h.
- [24 exact no-battery/4h pairs and 12 sensitivity pairs](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42965356842): SUCCESS and reconciled from the source 48-case CSV; manifest, exact paired CSV and cross-mode CSV in artifact `paper-s-reeds2022-county-native-exact-24-paired-storage-results`.
- Original demand is publisher `demand_EFS_REFERENCE.h5`, MD5 `7b2055d43200744a16a8c4fed68b1a17`, state model projections with **2012 fixed-CST reference weather**.
- This is county-native four-state resource aggregation, NOT the pure-state-BA subset in the distinct earlier source LP nor old EFS2020 p-zone model.

## Frozen illustrative model assumptions

- Renewable nameplate **0.9 × each demand state's peak load**, 50% wind/50% PV, no capacity expansion; NOT the enormous available-resource capacity from ReEDS supply curves. 4-hour storage dispatch at 0.25 × peak load power; round-trip efficiency 90%.
- LP illustrative renewable cost $5/MWh, firm cost $90/MWh, no storage capital, wear, reliability/network or transmission constraints. Cost savings here do not imply positive economic net benefit of a real storage investment.
- Native weather CF is *instantaneous*, whereas demand is hour-ending. The two model approximations are (a) end-instant hold, (b) trapezoidal between source instants, with an explicitly non-validated first-hour end-instant boundary replacement. Both are numerical assumptions, not source-certified interval generation.

## Exact 2030 primary reference sensitivity

| State | 0h-to-4h savings with end-instant hold (USD) | 0h-to-4h savings with trapezoid (USD) | Trapezoid savings / 0h original objective | End-instant savings / 0h original objective |
|---|---:|---:|---:|---:|
| AZ | 26,377,752.11 | 25,125,374.79 | 0.488769% | 0.512901% |
| CO | 2,620,614.61 | 2,350,999.06 | 0.060531% | 0.067466% |
| ID | 372,304.94 | 371,613.08 | 0.021146% | 0.021185% |
| WY | 16,290.44 | 13,036.44 | 0.000987% | 0.001233% |

Under these fixed assumptions, the storage benefit is much larger for Arizona and very small for Wyoming. The phrase 'benefit' refers solely to the **illustrative variable operating objective**; no storage investment viability or regional policy inference is licensed.

## Temporal-method sensitivity (trapezoid minus end-instant, 2030 savings USD)

- AZ −1,252,377.32; CO −269,615.55; ID −691.86; WY −3,254.00.
- For 2040 and 2050, the exact source-artifact CSV (not text-rounded displays) remains the canonical numerical authority.

## Interpretation and next scientific acceptance

1. This is a real-source *resource-shape* + independently timestamped projected-load LP that uses hypothetical deployed MW and simplified economics. It is stronger than Wave A/B synthetic availability but NOT an observed or physically validated hourly-generation dispatch case.
2. Inspect actual source low-availability hours and **renewable surplus under the 0.9×peak illustrative deployment**, since a low overall wind/solar nameplate assumption may explain storage's almost zero benefit in some states. Perform prespecified deployment-sensitivity sweep, rather than generalizing from this one scenario.
3. Compare with previously published pure-state BA subset LP only as a sensitivity with harmonized capacities and weather approximation; their coverage differs.
4. Add battery power/energy/capex and plausible costs before claiming an investment case.
5. Preserve original EFS2020 p-zone results unchanged; Paper S manuscript needs a new source-specific model/results section and citations to exact artifacts.

No policy claim of 'Western grid cost savings' or capacity-factor-to-hourly-energy publisher certification is made here.
