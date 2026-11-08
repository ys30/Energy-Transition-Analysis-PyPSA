# Paper S hourly mechanism pilot: original EFS source, archived-LP matched, 2030 Arizona p28

**Accepted workflow:** [Paper S representative zone hourly LP mechanism #42460995051](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42460995051), completed successfully. Archive `paper-s-representative-zone-hourly-mechanism-2030` (3 files: gzipped 78,840-record hourly trace, 9-row metric CSV, JSON certificate).

**Scope:** deterministically highest annual-demand 2030 EFS-LAF original source zone, Arizona `p28`, 8,760 source `LocalHourID` ordinals × 3 mathematically synthetic supply profiles × 0/4/8 h battery duration. The experimental algorithm was the existing HiGHS LP; only an optional `return_trace` path was added, without modifying objective, bounds or constraints. Full-year objective and energy outputs were compared, for **all nine** individual cases, against the original accepted 540-case archive (source [#42107237659](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659)) and matched.

## Original source-derived mechanism metrics

| Shape | Battery h | Pre-dispatch surplus hours | Pre-dispatch deficit hours | Charging hours | Discharging hours | Hours SOC at capacity | Charge power-bound hours | Discharge power-bound hours | Toy objective USD billion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Flat | 0 | 2,903 | 5,857 | 0 | 0 | 0 | 0 | 0 | 1.379249 |
| Flat | 4 | 2,903 | 5,857 | 2,142 | 1,694 | 8 | 0 | 1 | 1.298952 |
| Flat | 8 | 2,903 | 5,857 | 2,249 | 1,772 | 2 | 0 | 1 | 1.293505 |
| Wave A | 0 | 3,728 | 5,032 | 0 | 0 | 0 | 0 | 0 | 2.244293 |
| Wave A | 4 | 3,728 | 5,032 | 2,277 | 1,896 | 669 | 615 | 764 | 1.803783 |
| Wave A | 8 | 3,728 | 5,032 | 3,595 | 3,179 | 148 | 1,410 | 1,389 | 1.488500 |
| Wave B | 0 | 3,276 | 5,484 | 0 | 0 | 0 | 0 | 0 | 1.958454 |
| Wave B | 4 | 3,276 | 5,484 | 2,152 | 1,640 | 437 | 390 | 384 | 1.619432 |
| Wave B | 8 | 3,276 | 5,484 | 3,153 | 2,664 | 69 | 913 | 666 | 1.383514 |

These are rounded display values, not exact numerical certificates. Read exact unrounded case-level metrics from `representative_zone_mechanism_metrics.csv` in the accepted artifact.

## Scientific interpretation

- The fixed pre-dispatch hypothetical surplus and deficit hours *within each shape* remain unchanged across durations (by construction: battery design cannot alter source demand or synthetic resource availability).
- Flat has just 8 SOC capacity-bound hours in 4h and 2 in 8h versus 669/148 for wave A and 437/69 for wave B. This is consistent with the relative scarcity of additional duration-dependent reshaping opportunities for a flat artificial supply profile.
- Wave A 4h→8h expands charging hours from 2,277 to 3,595 and discharging hours from 1,896 to 3,179; wave B expands 2,152→3,153 and 1,640→2,664. This provides a specific **model-based mechanism diagnostic** to accompany annual Figure S4/S5.
- Increased charge/discharge *hours* alone do not identify additional MWh or physical value. A linear program may have nonunique optimal primal schedules; individual active-hour counts should be treated as solver-specific diagnostics. Both zero and near-limit tolerances are operational definitions, not physical hardware performance.
- 8h may have more *power-bound hours* than 4h because additional capacity permits different use of the unchanged power rating. Avoid treating those counts in isolation as evidence of higher system stress.
- Only one zone and year have the hourly traces so far. Do not describe these differences as verified across all 20 zones, all three years, or real WECC generation.

## Reproducibility / strict validation

- Code: [solver optional trace](../src/energy_transition/efs_cyclic_storage_lp.py), [hourly export and archived match](../src/energy_transition/paper_s_hourly_mechanism.py), [new tests](../tests/test_paper_s_hourly_mechanism.py).
- [Workflow](../.github/workflows/paper-s-hourly-mechanism.yml) restores the original EFS source CSV from Actions #41281576025 and the accepted 540-case original summaries from Actions #42107237659.
- Validates hourly renewable balance, load balance, SOC recursion, terminal-zero SOC and reconstruction of all original annual energy totals, with exact source zone identity.
- Exports 78,840 hourly records, 9 annual case rows and one JSON manifest.
- Reported `LocalHourID` values are source ordinals, **not certified physical UTC**, especially given unresolved physical clock provenance and the 2040 year labeling bug.
- Synthetic resource shapes, battery assumptions and marginal-cost coefficients cannot be interpreted as measured wind/PV conditions or net storage investment returns. No network transfer or Western grid OPF.

## Research next step

Investigate surplus/deficit **run length distributions**, charged/discharged MWh, binding periods and SOC trajectories for this scoped zone using the already exported 78,840 records. Figures should display only source-ordinal hour and clearly identify synthetic supply assumptions. Then expand in a pre-specified manner to contrasting zones rather than cherry-picking after seeing results. Preserve all full-year original-source validation checks.
