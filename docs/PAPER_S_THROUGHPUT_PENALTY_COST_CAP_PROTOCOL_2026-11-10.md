# Paper S — discharge-throughput cost sensitivity protocol (10 November 2026)

## Research question

The previous source-archived model demonstrated near-invariant annual delivered battery MWh but a large range in discharged MWh in predeclared original source-hours 4001–4168. A physically exclusive feasible witness ruled out the few concurrent charge/discharge observations as a sufficient sole explanation. This new sensitivity asks whether **assigning an explicit linear cost to discharged battery energy** materially narrows the near-optimal *within-window discharge* range.

## Design — a new proxy objective, not an observed degradation model

For each hourly solution x with original source objective C0(x)=5 Σ(r+c)+90 Σf, define

```text
Cp(x) = C0(x) + p * sum_t d_t
p ∈ {0, 1, 10} illustrative USD per MWh delivered from battery
```

The penalty is an **assumed linear per-discharged-MWh throughput charge**, not calibrated battery degradation, replacement economics, warranted lifetime, calendar aging, end-of-life salvage or a cycle-depth-sensitive stress function. It may encourage lower cycling, but does not enforce charge/discharge mutual exclusion.

At each p, solve an independent full-year original-demand Wave-A LP for each representative 2030 source-zone: original Arizona p28 and Wyoming p24; P=25% of source peak MW and E=one source peak-MW-hour; cyclic zero initial/final SOC; no network. The historical p=0 primary LP must equal its archived original result and historical p=0 window secondary extrema must reproduce accepted 168-source-hour values within explicitly checked numerical tolerances.

Define Cp*(p) as the **independent optimum of the penalized objective**, and `delta(p)=max(USD 0.05, 10^-9 Cp*(p))`. Independently minimize and maximize `Σ_(t=4001..4168) d_t` within the same original LP hourly constraints plus `Cp(x) <= Cp*(p) + delta(p)`. The cost ceiling is now placed on the **penalized** objective, not the old primary objective. If the ceiling were left on C0 for p>0, the study would not answer the stated question.

Output 18 original-source LP schedules = 2 source groups × 3 penalties × 3 schedules. Compare six source-group/penalty interval widths, optimized penalized objectives, annual discharged MWh, and concurrent charge/discharge diagnostic hours. Source-hour IDs are ordinal, **not certified calendar UTC hours**.

## Important scientific and code-safety boundaries

- The default parameter p=0 must preserve the behavior of original 540 LP, 189 independent MW–MWh and all prior secondary LP tests.
- The solver retains both `objective_illustrative_variable_usd` (unpenalized C0) and `objective_with_throughput_penalty_usd` (Cp) plus explicit penalty component, so no source archival objective is silently relabeled.
- Existing `original_cost_ceiling_usd` argument is kept for backward compatibility, but at p>0 its inequality uses Cp, explicitly identified as an **augmented objective cap** in results.
- A nonzero cost tolerance and floating-point solver precision means these are near-optimal sublevel-set results, not exact-MGA optimal faces.
- The penalty alone does **not** solve the physical mutual-exclusion problem, and its $1 and $10 values are deliberately sensitivity values, not market prices or measured degradation charges.
- No empirical wind/PV availability, real Western Interconnection power flows, transmission, CAPEX, unit-commitment or real reliability inference.

## Reproduction

- [LP extended with explicit opt-in penalty and original cost dual reporting](../src/energy_transition/efs_cyclic_storage_lp.py)
- [Penalized-window experiment](../src/energy_transition/paper_s_throughput_penalty_sensitivity.py)
- [Backward-compatibility and ceiling-unit tests](../tests/test_paper_s_throughput_penalty_sensitivity.py)
- [Source-restoring GitHub Actions](../.github/workflows/paper-s-throughput-penalty.yml)

**Numerical-results gate:** Do not claim penalty robustness until the two source-group LP jobs and six-row cross-group synthesis have completed successfully and their archived CSVs are inspected.
