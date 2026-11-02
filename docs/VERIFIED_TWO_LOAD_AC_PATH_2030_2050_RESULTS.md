# Verified two-EFS-load, four-bus AC-path constrained pilot (2030–2050)

Evidence: [successful GitHub Actions run 41392315969](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41392315969), commit `9fd60ec590e2df84981afafe3d88175cca781e42`. [Main CI 41392315948](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41392315948) passed. The workflow imported previously verified EFS NetCDF networks, solved three years using HiGHS, and uploaded JSON artifacts.

## Configuration

Original source network buses: `2040602 → 2040610 → 2040614 → 2040645`. Original AC lines: `97145`, `97156`, `97159`. Actual EFS demand is attached to *both* terminal buses `2040602` and `2040645`. Two supply components, located at those terminal buses, are **illustrative**, with marginal costs $10/MWh and $100/MWh, not observed generator data. The run uses 24 ordinal local-hour snapshots for each planning year, not an annual chronological simulation.

| Planning year | Demand at bus 2040602 (MWh) | Demand at bus 2040645 (MWh) | Total demand / dispatch (MWh) | Illustrative objective ($) | Max nodal residual (MW) |
|---|---:|---:|---:|---:|---:|
| 2030 | 85502.04745957165 | 2236.80514887149 | 87738.85260844314 | 8324496.797445879 | 8.526512829121202e-14 |
| 2040 | 95600.1996213096 | 2500.9806100707465 | 98101.18023138035 | 9336953.768231664 | 3.694822225952521e-13 |
| 2050 | 109467.12135446192 | 2863.7512215714787 | 112330.8725760334 | 10727273.647661906 | 3.694822225952521e-13 |

All three model runs report `solver_status=ok` and `solver_condition=optimal`, matched total load to dispatch within floating-point tolerance, and respected original line capacities.

## Branch-level results

| Source AC line | Peak absolute flow (MW), each year | Maximum utilization, each year |
|---|---:|---:|
| 97145 | 114.85 | 79.0760% |
| 97156 | 114.85 | 100.0000% (binding) |
| 97159 | 114.85 | 72.3693% |

The path is a tree. All three edges carry identical absolute flow because there are no injections at intermediate buses; the lowest-capacity edge 97156 sets the maximum affordable remote-to-local transfer. Consequently identical peak line utilizations across planning years are a **model-structure effect** rather than evidence of fixed actual Western grid congestion.

## Important research limitations

- These are genuine original source-line parameters and attached EFS load profiles, but **not an observed, calibrated, generation-admitted Western grid**.
- The optimization excludes all branches and boundary injections outside the chosen four-bus path. This can materially change the dispatch feasibility and congestion patterns compared with the full network.
- The illustrative $10/$100 per MWh generator costs are deliberately imposed. Objectives and changes are not empirical electricity system costs, benefits or savings.
- Calendar and DST conversion are not verified (`timezone_aligned=false`). A 24-hour pilot is not a full-year simulation; no 2030–2050 annual cost trajectory may be inferred.
- The supplied line thermal ratings are the source network's nominal settings; not independently field-calibrated physical limits.
- Future analyses should use verified EIA-860 generator bus/technology matches and EIA-923 generation reconciliations before citing dispatch/emissions, and expand to multiple zones, tie-lines and chronological snapshots.

## Next executable tasks

1. Add independent tests validating per-bus nodal balance and failure on missing expected source-line IDs.
2. Compare congestion/dispatch against a strictly labeled unconstrained sensitivity case to quantify the **illustrative** shadow effect, never actual grid savings.
3. Select a multi-load source-admitted connected larger network, retain adjacent branches and model boundary injections explicitly.
