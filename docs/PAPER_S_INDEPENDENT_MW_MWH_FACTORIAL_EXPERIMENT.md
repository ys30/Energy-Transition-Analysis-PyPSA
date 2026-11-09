# Paper S: independent power and energy sizing experiment (MW × MWh)

## Design admission and fixed analysis plan

This experiment responds to the accepted one-factor parameter screen ([294 LPs, successful archive-backed run #42672106407](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42672106407)). That screen changed peak-rated battery power while also changing installed MWh at any fixed nominal duration, so it could **not** isolate the contribution of MW from MWh. This experiment parameterizes the original HiGHS LP's two battery design bounds independently without altering conservation constraints or the illustrative unit-cost function.

**Input chronology:** The seven unique positive 2030 peak-normalized source-demand shape groups identified by the accepted [20-zone source shape audit](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42464270811), represented by the *highest-annual-load* zone in each source group. All seven original 8,760-hour load sequences and their baseline 4h/8h 0.25-peak-MW results were archived in the previously successful [63 LP source-verified run #42511072562](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42511072562).

| Controlled axis | Values | Interpretation |
|---|---|---|
| Storage discharge/charge power rating | 0.125, 0.25, 0.50 × original local zone peak MW | MW is held constant when MWh increases |
| Storage energy capacity | 0.5, 1.0, 2.0 × original local zone peak MW × one hour | MWh is held constant when MW increases |
| Renewable availability | Flat 50%, ordinal wave A, ordinal wave B | Synthetic, not observed resource data |
| Battery round-trip efficiency | 90% | Constant |
| Cost coefficients | USD 5/MWh renewable utilization, USD 90/MWh firm | Constant, no storage CAPEX |

The 3×3 MW–MWh grid yields nine LPs per synthetic renewable profile per representative EFS demand chronology, i.e. **189 planned full-year optimal LPs** across seven source-demand patterns. It yields **252 planned adjacent one-axis comparisons**, exactly 126 with MW fixed and capacity increasing plus 126 with MWh fixed and power increasing. The derived quantity `battery_energy_peak_hours / battery_power_peak_ratio` is an *implied* rated energy duration, not an independently manipulated experimental parameter.

The initial 0.25-peak-power/1.0-peak-energy and 0.25-peak-power/2.0-peak-energy cells **must exactly reproduce** each source group's archived 4h and 8h LP annual source data; six archived checks per group are required (three renewable shapes times two baseline storage points). No cross-group result is admitted otherwise. Hourly primal/summary conservation and initial/terminal-zero SOC remain enforced.

**Planned output:** [new LP module](../src/energy_transition/paper_s_orthogonal_power_energy.py) and [new archive-backed workflow](../.github/workflows/paper-s-orthogonal-mw-mwh.yml) produce LP results, fixed-MW and fixed-MWh contrasts, the count of demand shapes with positive additional battery discharge for each factor step, and cost decomposition `90*avoided firm - 5*avoided unused`. The workflow is considered validated only after an actual successful GitHub run and artifact availability.

## Interpretation gates

- Compare **change in MWh capacity at fixed MW** separately from **change in MW power at fixed MWh**.
- Do not interpret extra annual discharged MWh as *cost-effective investment* or a causal effect of real solar/wind climatology.
- Because the objective includes no battery CAPEX, variable-cost decreases cannot establish an optimal MW–MWh design.
- Because EFS `LocalHourID` is not certified physical UTC, no real hourly sunlight attribution follows.
- The seven EFS source-demand normalized patterns are distinct, but not necessarily statistically independent sampled regional systems.
- A zero additional delivered-MWh increment is not proof of zero system value under reliability, reserves, losses, constraints, or different costs.
- Do not claim seven-group outcomes from any partial job or a failed workflow. The methods are accepted only after full tests, 189 LP outputs, and 252 reconciled contrasts.

**Source / dataset limits:** Seven Western-state EFS-derived projected demand; synthetic resources; no actual network dispatch, interzonal power transfer, storage degradation or investment costs. Full private manuscript remains outside this public repository.
