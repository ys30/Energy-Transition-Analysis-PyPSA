# Verified 2030–2050 six-bus constrained EFS pilot results

Evidence: [successful real-six-bus workflow 41386248779](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41386248779), head commit `1bc0560d384f1ac98088f4d87bddc9fc4cd46e13`; job `six-bus` successfully downloaded source network, solved all three years, executed cross-year verification and uploaded artifact `real-six-bus-efs-constrained-solve` (ID 13115004259).

| Planning year | 24h actual EFS load (MWh) | Dispatched MWh | Illustrative objective ($) | Illustrative objective / MWh ($/MWh) | Binding line | Solver |
|---|---:|---:|---:|---:|---|---|
| 2030 | 18768.940533598536 | 18768.940533598536 | 1444699.6533598537 | 76.972 | 100242 | optimal |
| 2040 | 20956.685646460086 | 20956.685646460082 | 1663474.1646460083 | 79.377 | 100242 | optimal |
| 2050 | 23958.635516490845 | 23958.635516490845 | 1963669.1516490837 | 81.961 | 100242 | optimal |

The 24h selected-load series increases with year and annual-demand scenario. Each run has six buses, five original line parameter records, 24 **ordinal local-hour** snapshots, and explicitly **illustrative** generators and marginal costs ($10/MWh remote and $100/MWh local in source code). Reported model load matches total dispatch up to floating point precision. Original-line thermal limit for line 100242 binds (100% utilization); all other selected lines 100243–100246 report maximum utilization 0%. This strongly suggests that the topology/placement and potentially a single bottleneck dominate the experiment; investigate connectivity and branch flow patterns before claiming spatial transmission findings. It does not prove that unused lines are universally irrelevant.

## Critical interpretation constraints

- This is a small engineering constrained-dispatch demonstration, **not** a full Western power system, calibrated historical dispatch, future cost projection, or investment optimization.
- Source network from a previous run was written using PyPSA v0.30.2 and imported under v0.31.2; import generated a version mismatch warning but optimization completed.
- Logs also report unspecified bus/line carriers, not a physical validation verdict; review carrier data on expansion.
- Time zone/DST synchronization is explicitly `timezone_aligned=false`.
- No actual generator bus matching, renewable availability, fuel/cost or technology portfolios is established by this trial.
- Reported dollar values are objective function values conditional on deliberately illustrative marginal costs and *must not* be used as electricity system expenditures or savings.

## Next engineering milestones

1. Audit six-bus topology, load location and remote/local generator siting; explain why four branch flow maxima are zero.
2. Confirm thermal limits and bus/line component provenance and model-unit conventions.
3. Expand to a **connected, multi-load, multi-generation** source-admitted regional subsystem; add nodal/branch residual checks.
4. Complete EIA-860 generator-to-bus and EIA-923 reconciliation evidence; do not substitute annual energy totals for hourly generation availability.
5. Establish UTC/DST semantics and solve longer chronological scenarios before reporting annual or climate-impact conclusions.
