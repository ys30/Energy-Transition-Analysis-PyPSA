# EFS 8,760-source-ordinal cyclic-storage LP: scale-up gate

## Scope

This is the next engineering scale-up after the [successful 168-hour, 54-case cyclic HiGHS feasibility pilot](efs_cyclic_soc_highs_lp_pilot.md). It reuses the exact solver and source-consistency checks but extends the time horizon to **all 8,760 original LocalHourID ordinals** in 2030, 2040 and 2050.

**Stage 1:** optimize the single highest-total-demand ReEDS zone in each year, nine scenarios/year (three explicitly synthetic renewable-availability profiles × assumed 0-, 4-, 8-hour battery durations). Year-specific zone selection uses *full-year EFS source demand*, not the previous first-168-hour ranking. The year runs are independent. **Do not extrapolate stage-1 results to the 20-zone source population.**

**Planned Stage 2:** after all 27 year/zone/scenario solves pass, distribute the independently constrained LP to all twenty admitted zones using appropriate runner batching and source-derived output recombination. Every zone must pass 8,760 unique-hour checks.

## Exact optimization and boundary conditions

The optimization uses the equations already described in [the cyclic HiGHS model](efs_cyclic_soc_highs_lp_pilot.md). Initial and final battery SOC are strictly 0 MWh; the output records HiGHS optimal status, exact source-demand and hypothetical-renewable mass balance, max constraint residual, battery charge/discharge totals and direct-load delivery.

The workflow prints the runner memory and elapsed time from /usr/bin/time -v for the scaling assessment. It explicitly rejects mismatched zone/hour count, nonoptimal LP status, nonzero final SOC and unsupported real-OPF/UTC claims.

## Reproducibility and admission limits

- [8760h workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-cyclic-storage-8760h.yml)
- Source: original 7-state, 20-zone archived EFS-LAF hourly CSV from Actions run 41281576025.
- Result artifacts per year: efs-cyclic-8760h-source-zonal-{2030,2040,2050}.
- **The model uses genuine source EFS load, but synthetic renewable availability, battery hardware and marginal costs; no network constraints, real POI, actual generator hourly profiles or physically certified UTC.** A full-year LP optimizes the mathematical assumptions, not authentic Western storage value.

**Status:** submitted for initial real-source CI; only label the full-year pilot successful after the three jobs complete successfully.
