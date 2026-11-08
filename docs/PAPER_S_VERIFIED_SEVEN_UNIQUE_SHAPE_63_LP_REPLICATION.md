# Paper S — seven unique EFS source-demand shapes: archived-source full-year mechanism replication

**Evidence status: Verified.** [Seven source-shape representative workflow #42511072562](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42511072562), completed success, including seven independent matrix jobs, original 540-case annual-aggregate equality checks, hourly energy/SOC checks and a successful 63-case/21-comparison synthesis. Previous first attempt #42511003051 failed due to a one-year vs three-year source-selection scope mismatch; commit `9217be267a417f872aa2960cd2d3e0a0d17c0c2e` fixed the input filtering, and the entire seven-group run was repeated successfully. Full project CI for the latest code should be separately verified.

**Selection rule (precommitted before examining the results):** Each of the seven distinct positive peak-normalized 2030 EFS/LAF hourly demand-shape groups identified by the previously accepted original source audit [#42464270811](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42464270811) contributes its highest annual-MWh demand zone, stable state/zone tie breaker. Each selected zone has three assumed resource profiles × battery 0/4/8 hours, cyclic source ordinal 8,760-hour HiGHS LP. No profiles were selected according to their storage outcomes.

## Seven source-shape representatives, 4→8 hour additional storage discharge

From the accepted 21-comparison synthesis, delivered energy difference `discharged(8h) - discharged(4h)`, **GWh** (display values rounded to three decimals):

| Original demand-shape group | Selected state-zone | Flat 50% | Synthetic Wave A | Synthetic Wave B |
|---|---|---:|---:|---:|
| Arizona | Arizona p28 | 64.512 | 3,733.614 | 2,793.766 |
| Colorado | Colorado p33 | 0.000 | 262.664 | 36.605 |
| Idaho | Idaho p15 | 0.000 | 294.480 | 52.340 |
| Montana | Montana p17 | 0.000 | 23.944 | 0.114 |
| New Mexico | New Mexico p31 | 0.000 | 407.326 | 46.874 |
| Utah | Utah p25 | 0.000 | 99.547 | 0.180 |
| Wyoming | Wyoming p24 | 0.000 | 0.000 | 0.000 |

**Descriptive outcome:** For the 4→8h increment, Flat shows positive additional discharge in **1/7** distinct source-demand shape groups; synthetic Wave A and Wave B each show positive additional discharge in **6/7** groups. Wyoming is a counterexample for the second duration increment in all three tested synthetic supply profiles. Montana and Utah under Wave B have only small strictly positive increments, so neither energy-value nor economic significance can be inferred without further checks.

This contrasts with the earlier three-**zone** prespecified check (Arizona p28, Wyoming p21, Arizona p29), where p28 and p29 proved to be the same normalized demand shape; the seven-group audit corrects that pseudoreplication problem. The **seven different profiles should not be called seven statistically independent sampled systems**: they originate from the same staged EFS/LAF source architecture, share synthetic supply-generation rules, parameter assumptions and potentially upstream statistical dependencies.

## Mechanism diagnostic — source-ordinal surplus and deficit runs

Illustrative Wave A average pre-dispatch run durations and SOC occupancies (selected 4h/8h cases):

| Original source group | Mean Wave A surplus run (ordinal h) | Mean Wave A deficit run (ordinal h) | Mean SOC 4h | Mean SOC 8h |
|---|---:|---:|---:|---:|
| Arizona | 10.186 | 13.786 | 0.3919 | 0.3928 |
| Colorado | 7.156 | 16.825 | 0.3369 | 0.1935 |
| Idaho | 8.210 | 15.767 | 0.3719 | 0.2738 |
| Montana | 6.657 | 17.658 | 0.2867 | 0.1624 |
| New Mexico | 8.057 | 15.921 | 0.4027 | 0.2850 |
| Utah | 6.951 | 17.030 | 0.3214 | 0.1748 |
| Wyoming | 4.452 | 35.386 | 0.0566 | 0.0283 |

Pre-dispatch run duration is computed from `max(assumed_supply - source_load, 0)` or its deficit counterpart in **source-ordinal hours**, without wrapping December to January. The Wyoming Wave A mean deficit run (~35.4 source hours) and low mean battery SOC (~5.7% of 4h nominal energy capacity) are **consistent with** fewer viable charge-to-discharge cycling opportunities; however, those summary statistics do **not independently establish causality**. LP degeneracy and other constraints can change hourly dispatch patterns.

## Proposed Paper S Results paragraph (limited to actual evidence)

> To avoid treating zonal scale variants of the same demand chronology as independent evidence, we identified seven distinct nonzero peak-normalized hourly source-demand shapes among 19 positive-load zones per projection year. We selected one high-demand representative of each shape before inspecting optimization outputs and reran all nine synthetic supply-by-duration combinations for 2030, preserving the original cyclic LP objective, constraints and full 8,760 source-hour horizon. All 63 optimization results reconciled with the previously accepted 540-case archived solutions. Across seven distinct source shapes, increasing battery duration from four to eight hours increased modeled discharged energy in only one group under a flat supply profile, compared with six groups under either synthetic wave profile. The Wyoming representative had no additional discharge in any of the three synthetic profiles. These conditional comparisons indicate material dependence on assumed supply-demand alignment and source-demand chronology, but do not quantify observed renewable curtailment, real Western Interconnection storage value, or economically optimal storage duration.

## Mandatory limitations and next admission gate

- This is seven distinct *hourly sequence shapes*, **not** a probabilistic sample of seven independently observed grids. The source dataset covers seven admitted Western states, not full WECC.
- All synthetic supply profiles are ordinal mathematical shapes, not independently timestamped wind/solar records. EFS `LocalHourID` is not certified physical UTC, and the 2040 calendar labeling issue remains.
- Storage charge/discharge time series are one valid HiGHS optimum; occupancy-hour measures can change under degenerate solutions without changing the objective.
- The LP excludes battery capital costs, degradation, financing, reserve reliability and transmission; no net storage economics or grid OPF.
- At present the **strongest scientific claim** is about **model-conditional response to temporal structure and the nonindependence of zonal load profiles**.
- Next meaningful improvement is a controlled resource-shape perturbation, power/efficiency sensitivity, and independent timestamped weather/resource data admission; only after those checks consider real-world transition-policy claims.

## Reproducibility links

- [original normalized source-shape classification](../src/energy_transition/efs_source_normalized_shapes.py)
- [optional unchanged HiGHS primal trace](../src/energy_transition/efs_cyclic_storage_lp.py)
- [source group representative and LP archive reconciliation](../src/energy_transition/paper_s_hourly_mechanism.py)
- [run-length and SOC diagnostic](../src/energy_transition/paper_s_trace_mechanism.py)
- [seven-group matrix/merge GitHub Actions workflow](../.github/workflows/paper-s-seven-shape-mechanism.yml)

Source workflow artifacts: seven per-representative compressed full-hour traces, plus `paper-s-2030-seven-independent-source-shape-synthesis` with 63-case mechanism CSV and 21-comparison CSV. The artifact name includes the word “independent” in its historical name; **the seven shapes are distinct but not necessarily statistically independent**. Keep private manuscripts outside the public repository.
