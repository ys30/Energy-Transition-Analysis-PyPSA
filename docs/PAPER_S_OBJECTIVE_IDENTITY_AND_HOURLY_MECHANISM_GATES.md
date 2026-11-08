# Paper S: operational-objective mechanism and what is not identifiable yet

## Status and lineage

This note documents an **exact algebraic interpretation** of the original 540 annual optimal cyclic LP solutions, not an additional physical validation. The [source-archived objective decomposition](../src/energy_transition/paper_s_objective_decomposition.py) runs from the accepted [540 original LP output CSV](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659). The relevant workflow is [paper-s-marginal-duration.yml](../.github/workflows/paper-s-marginal-duration.yml). **Do not call the new decomposition certified before its run passes.**

## Exact accounting identity

The implemented illustrative objective at each annual LP is:

`C = 5 USD/MWh * (direct renewable MWh + renewable-to-storage charge input MWh) + 90 USD/MWh * firm MWh`.

For an unchanged synthetic supply profile and load, supply conservation implies:

`direct renewable + storage charge = available hypothetical renewables - unused hypothetical renewables`.

Consequently at each 0→4 h and 4→8 h battery-duration increment, defining *avoided* energy as the value at the lower duration minus the value at the higher duration:

`reduction in C = 90 USD/MWh * avoided firm generation - 5 USD/MWh * avoided unused renewable availability`.

This is a **model identity**, not a fitted causal relationship, statistical estimate, or new economic benefit. The second term is negative when storage reduces unused renewable availability because the specified objective charges a positive USD 5/MWh for additional renewable utilization/charging. Neither term accounts for battery CAPEX or transmission. Exact reconciliation on the original unrounded 540-case table is covered by the CI.

## Mechanism inference boundaries

- Figures S4/S5 already show the **nine combinations** of three years × three artificial supply shapes yield a smaller objective reduction for hours 4–8 than 0–4. Strong differences in second/first ratio are model-specific observations.
- The above identity shows *what the annual cost difference consists of*, but does **not** establish *why* the optimal dispatch shifts differently by synthetic shape.
- Identifying a temporal mechanism needs **hourly** candidate surplus `max(available(t)-load(t), 0)`, candidate deficit, charge/discharge and SOC time series, binding power/energy constraints and empirical-style temporal concentration metrics. The original zone-year LP archive stores annual aggregates, peak SOC and installed capacity, **not** full 8,760-hour primal decision vectors.
- Because the synthetic shape functions are explicit, calculating unmatched-surplus/deficit opportunities over the original EFS hourly demand (without a new LP) is feasible, but must be called a *pre-dispatch opportunity diagnostic*, not proof of causality.
- A production-quality mechanism test should extract hourly vectors at a deliberately small set of representative zones/years, export audit-friendly CSV/Parquet, check all hour-wise balances and SOC recursion, and compare whether observed binding constraints explain the aggregate marginal differences. Additional synthetic duration points without this diagnostic will add limited scientific value.
- EFS `LocalHourID` is an **ordinal source sequence**, not verified physical UTC. Do not call the synthetic 24-ordinal cycle a real solar/wind diurnal clock or assume it is aligned with actual sunlight.

## Next admission-gated experiment

1. Freeze the source dataset, zone selection and three supply-shape functions.
2. Add a **small-scope** hourly primal-vector export option to the existing HiGHS LP solver, without altering its objective or constraints; regression-test compatibility with the currently accepted annual outputs.
3. Report charging hours, discharging hours, SOC-at-capacity hours, charge/discharge power-binding hours, and the duration-length distribution of hypothetical surplus/deficit runs on the source ordinal sequence.
4. Reconcile each hourly exported trace exactly to the original published per-zone aggregate and year/shape/duration IDs.
5. Interpret a shape-dependent finding as **conditional on synthetic supply functions and source-ordinal EFS loads** until independent source clocks and weather/resource profiles are admitted.

No journal claim about real Western grid storage optimality, capex-adjusted savings or observed curtailment is authorized by this note. Manuscripts stay private.
