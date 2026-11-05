# EFS 8,760-source-ordinal cyclic-storage LP: scale-up gate

## Scope

This is the next engineering scale-up after the [successful 168-hour, 54-case cyclic HiGHS feasibility pilot](efs_cyclic_soc_highs_lp_pilot.md). It reuses the exact solver and source-consistency checks but extends the time horizon to **all 8,760 original LocalHourID ordinals** in 2030, 2040 and 2050.

**Stage 1 — PASSED:** [original-source 8760-hour CI #42106918676](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42106918676) optimized the highest full-year-demand zone **p28** in each year, nine scenarios/year (three explicitly synthetic renewable-availability profiles × assumed 0-, 4-, 8-hour battery durations). Each yearly batch completed in approximately **3–6 seconds** elapsed with roughly **260 MB peak RSS** on GitHub's runner. The independent 168-hour source ranking was not reused. **Do not extrapolate stage-1 results to the 20-zone population.**

**Stage 2 — SUBMITTED:** [all-20-zone workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-cyclic-storage-all-zones.yml) partitions each year's 20 source zones into **four deterministic non-overlapping batches of five**. Each zone runs three synthetic supply shapes and three battery durations; total expected **20 × 3 × 3 × 3 = 540 LP solves**. An independent aggregation job checks unique year/state/zone/shape/duration keys, 8,760h source input, primal equality residual, cyclic terminal SOC and 27 annual aggregated cases. The zero-battery outputs must match the **previously verified** full-year 20-zone source-backed 27-case sensitivity archive numerically. **Do not claim stage 2 succeeds until all batch jobs AND aggregation succeed.**

## Exact optimization and boundary conditions

The optimization uses the equations already described in [the cyclic HiGHS model](efs_cyclic_soc_highs_lp_pilot.md). Initial and final battery SOC are strictly 0 MWh; the output records HiGHS optimal status, exact source-demand and hypothetical-renewable mass balance, max constraint residual, battery charge/discharge totals and direct-load delivery.

The workflow prints the runner memory and elapsed time from /usr/bin/time -v for the scaling assessment. It explicitly rejects mismatched zone/hour count, nonoptimal LP status, nonzero final SOC and unsupported real-OPF/UTC claims.

## Reproducibility and admission limits

- [8760h workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-cyclic-storage-8760h.yml)
- Source: original 7-state, 20-zone archived EFS-LAF hourly CSV from Actions run 41281576025.
- Result artifacts per year: efs-cyclic-8760h-source-zonal-{2030,2040,2050}.
- **The model uses genuine source EFS load, but synthetic renewable availability, battery hardware and marginal costs; no network constraints, real POI, actual generator hourly profiles or physically certified UTC.** A full-year LP optimizes the mathematical assumptions, not authentic Western storage value.

**Status:** stage 1 verified on the original 8,760-hour source; stage 2 all-zone acceptance is pending its workflow completion. Neither stage establishes physical weather or electric network credibility.
