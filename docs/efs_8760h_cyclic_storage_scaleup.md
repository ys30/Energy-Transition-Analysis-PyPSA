# EFS 8,760-source-ordinal cyclic-storage LP: scale-up gate

## Scope

This is the next engineering scale-up after the [successful 168-hour, 54-case cyclic HiGHS feasibility pilot](efs_cyclic_soc_highs_lp_pilot.md). It reuses the exact solver and source-consistency checks but extends the time horizon to **all 8,760 original LocalHourID ordinals** in 2030, 2040 and 2050.

**Stage 1 — PASSED:** [original-source 8760-hour CI #42106918676](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42106918676) optimized the highest full-year-demand zone **p28** in each year, nine scenarios/year (three explicitly synthetic renewable-availability profiles × assumed 0-, 4-, 8-hour battery durations). Each yearly batch completed in approximately **3–6 seconds** elapsed with roughly **260 MB peak RSS** on GitHub's runner. The independent 168-hour source ranking was not reused. **Do not extrapolate stage-1 results to the 20-zone population.**

**Stage 2 — PASSED in [CI #42107237659](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659):** [all-20-zone workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-cyclic-storage-all-zones.yml) partitions each year's 20 source zones into **four deterministic non-overlapping batches of five**. Each zone runs three synthetic supply shapes and three battery durations; total expected **20 × 3 × 3 × 3 = 540 LP solves**. An independent aggregation job checks unique year/state/zone/shape/duration keys, 8,760h source input, primal equality residual, cyclic terminal SOC and 27 annual aggregated cases. The zero-battery outputs must match the **previously verified** full-year 20-zone source-backed 27-case sensitivity archive numerically. All **12 zone-batch jobs and independent aggregation succeeded**, covering exactly 20 unique source zones/year with 8,760 original hourly ordinals, **540 optimal cyclic LP solutions**. The aggregation independently matched all nine annual no-storage year/shape metrics to the previously passed original 27-scenario source-demand archive. Each LP has near-zero equality residual and zero terminal SOC.

## Exact optimization and boundary conditions

The optimization uses the equations already described in [the cyclic HiGHS model](efs_cyclic_soc_highs_lp_pilot.md). Initial and final battery SOC are strictly 0 MWh; the output records HiGHS optimal status, exact source-demand and hypothetical-renewable mass balance, max constraint residual, battery charge/discharge totals and direct-load delivery.

The workflow prints the runner memory and elapsed time from /usr/bin/time -v for the scaling assessment. It explicitly rejects mismatched zone/hour count, nonoptimal LP status, nonzero final SOC and unsupported real-OPF/UTC claims.

## Reproducibility and admission limits

- [8760h workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-cyclic-storage-8760h.yml)
- Source: original 7-state, 20-zone archived EFS-LAF hourly CSV from Actions run 41281576025.
- Result artifacts per year: efs-cyclic-8760h-source-zonal-{2030,2040,2050}.
- **The model uses genuine source EFS load, but synthetic renewable availability, battery hardware and marginal costs; no network constraints, real POI, actual generator hourly profiles or physically certified UTC.** A full-year LP optimizes the mathematical assumptions, not authentic Western storage value.

**Status:** stages 1 and 2 both verified on original EFS source load. Neither stage establishes physical renewable/weather or electric network credibility.


## Stage 2: verified 20-zone full-year results

Each number below comes from the **independent final aggregation job** in [successful workflow #42107237659](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659), based on all 20 admitted zones in all 8,760 original source ordinal hours. The figures are **hypothetical renewable supply and battery dispatch**, not measured renewable curtailment or Western market economics.

| Year | Hypothetical supply shape | Storage duration | Model unused availability (TWh) | Assumed firm generation (TWh) | Battery delivered to load (TWh) | Toy variable cost ($B) |
|---|---|---:|---:|---:|---:|---:|
| 2030 | Wave A | 0 h | 25.893 | 97.871 | 0 | 9.693 |
| 2030 | Wave A | 4 h | 9.466 | 83.086 | 14.785 | 8.444 |
| 2030 | Wave A | 8 h | 2.626 | 76.930 | 20.940 | 7.924 |
| 2040 | Wave A | 0 h | 28.934 | 109.313 | 0 | 10.826 |
| 2040 | Wave A | 4 h | 10.582 | 92.796 | 16.517 | 9.431 |
| 2040 | Wave A | 8 h | 2.937 | 85.916 | 23.397 | 8.850 |
| 2050 | Wave A | 0 h | 33.104 | 124.992 | 0 | 12.379 |
| 2050 | Wave A | 4 h | 12.114 | 106.102 | 18.891 | 10.783 |
| 2050 | Wave A | 8 h | 3.364 | 98.227 | 26.766 | 10.118 |

**Boundary/identification finding:** at 2030, the 8-hour wave-A *greedy* model previously reported **2.605 TWh** unused energy but ended with **19.983 GWh** stored. The *cyclic* HiGHS LP reports **2.626 TWh** unused energy and **zero** terminal SOC. The near **0.021 TWh** difference in unused energy is not a pure optimization improvement: the boundary conditions are different. The full-year LP reports the same delivered battery energy (20.940 TWh, rounding) but ends with no inventory. All physically real plant/network or weather synchronization flags remain false.

The 20-zone optimization costs omit battery capital, replacement/degradation, grid congestion, realistic variable renewable output and real market prices. They are **model objective values only**. The more defensible conclusion is that source-identical yearly demand and source-identical annual renewable availability can generate quite different assumption-dependent storage outcomes, and that the terminal SOC gate prevents misleading direct comparisons.
