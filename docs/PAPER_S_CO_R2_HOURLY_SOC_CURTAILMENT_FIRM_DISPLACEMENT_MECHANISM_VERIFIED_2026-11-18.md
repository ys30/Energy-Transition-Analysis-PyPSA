# Paper S — VERIFIED CO R=2.0 hourly dispatch mechanism (2026-11-18)

## Actual successful source-backed work

Actions [run 44453880808](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44453880808) **success**, artifact **14499285164**. Independently re-solved **180 full-hour optimal Colorado LPs** across 15 weather years × two county siting schemes × wind 40/50/60% × batteries 4/8 h. The 180 model objectives match the originally frozen 3×3 and newly validated 40/60 runs to **max absolute $0.00492263** on total annual illustrative objective; battery capacities exactly identical, maximum LP primal equality residual **3.637978807091713e-12 MWh**. The 90 source-array records verify within each source weather year/scheme, the demand, wind and solar base-array SHA-256 are identical across 40/50/60 share; the wind–PV mixture necessarily changes with share. For 2012 and 2023, the original artifact includes **24 full 8,760-hour gzip CSV traces** with storage SOC, charging/discharging, unused renewable, generation, active upper bounds and HiGHS dual marginals. All 24 traces independently passed per-hour renewable balance and per-hour demand balance (max 7.276e-12 MWh).

## Original CO 8h LP active-bound hours: medians over 15 weather years

| Wind share | EIA operating-weight hours charging at rated power | ReEDS potential-weight hours charging at rated power | EIA hours SOC at energy maximum | Potential hours SOC at energy maximum |
|---|---:|---:|---:|---:|
| 40% | 1733 | 1872 | 196 | 237 |
| 50% | 1154 | 1333 | 139 | 168 |
| 60% | 624 | 638 | 104 | 90 |

Note that the observed decline is **not a singular peak at 50%**. A local valley is in the **paired siting contrast of incremental 4→8h value**, not necessarily in the underlying active-set counts.

## Important source-year paired mechanism comparison (NOT difference of medians)

For each source weather year and weight, subtract 8h firm-generation MWh from 4h firm-generation MWh, then compute EIA-minus-potential *same-year* difference. 15-year median of this paired extra firm displacement difference:

- wind **40%:** **−246,794.80 MWh**
- wind **50%:** **−295,403.17 MWh**
- wind **60%:** **−40,894.41 MWh**

Similarly, same-year paired additional curtailment absorption from extending 4→8h, EIA-minus-potential difference (15-year medians):

- wind **40%:** **−274,216.45 MWh**
- wind **50%:** **−328,225.74 MWh**
- wind **60%:** **−45,438.23 MWh**

Thus the 50%-share local value minimum coincides with a stronger relative shortfall in EIA-weighted *incremental* dispatchable firm substitution and renewable-surplus absorption than 40% or 60%. This is an empirically checked **internal LP dispatch-accounting mechanism**, not proof of a unique battery SOC saturation threshold. Under the source LP cost coefficients and unchanged marginal storage size, accounting identities mechanically connect firm displacement, curtailed energy and the storage operating value. Caution: while total optimal objective is stable, hourly SOC, individual active-set hours and some dual marginals may differ across alternative optimal bases.

## Reproducible new interpretive package

The actual conversation-local `Paper_S_CO_R2_Hourly_Mechanism_QA_Verified_2026-11-18.zip` contains:
- Table M1: 12 scheme×share×duration median active-set/energy diagnostics;
- Table M2: 90 year×weight×share matched 4h/8h operating changes;
- Table M3: 45 same-year matched geography differences for incremental curtailed energy and displaced firm energy;
- Table M4: source-hour QA across 24 retained traces;
- 3 original descriptive figures (8h charging power bound, SOC upper bound, sum of SOC-capacity upper duals);
- README and SHA256SUMS.
The **full 24 original hourly traces** are instead in the authentic GitHub run artifact 14499285164, not silently truncated/rewritten.

## Admission rule for Paper S

Keep existing 3×3 design values and R2 40/60 continuity results unchanged; add a focused **mechanism-supported nonlinear geography–mix interaction**, backed by 15 source-weather-year paired displacement and curtailment contrasts. No claim that physical plant-level production exceeds capacity, that actual 2023 CO dispatch is verified, or that one hourly charge/SOC active bound **causally** or uniquely determines the valley. The spatial scheme uses 2025 EIA operating-fleet weights vs original ReEDS potential weights in an illustrative state copperplate LP, not physical network OPF.

Frozen Paper S original 1,440 LP, 360 2×2, 2,880 3×3, 720 40/60, 2,160 ATB, and Paper C-2 all preserved.
