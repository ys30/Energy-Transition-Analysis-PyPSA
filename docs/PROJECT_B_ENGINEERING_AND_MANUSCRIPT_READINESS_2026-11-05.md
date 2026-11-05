# Project B: engineering and manuscript readiness reassessment — 2026-11-05

## Actual verified checkpoint

**Read-only verified Actions status on 5 Nov 2026:** [EFS numeric chain and source hash #42071987010](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42071987010), [archived EIA candidate-bus topology #42079066900](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42079066900), [27 equal-energy synthetic renewable-shape cases #42099467157](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42099467157), [27 ordinal-only greedy battery cases #42100384015](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42100384015), and [README/main CI #42100561608](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42100561608) all **completed successfully**. CI success validates the stated calculation, not unverified physical assumptions.

### Engineering workstreams

| Workstream | Verified now | Essential remaining gate |
|---|---|---|
| NLR EFS ingestion and 2030/2040/2050 state-hour aggregation | Original source derived, coverage checked | Exact clock / publisher source metadata |
| Original LAF state-to-zone to load-only NetCDF | Seven admitted states, 20 load zones, full 8,760h numerical reconciliation | Independent representativeness of LAF and additional geography |
| Source NetCDF chronology | 2040 synthetic leap-label offset exposed and tested | Physical UTC/DST, leap-hour and hour-ending evidence |
| EIA-860 source inventory, BA and facility evidence | Sourced historical names, MW, nearest-bus candidate priority and original synthetic bus topology | Independently verified actual generator POI and real network identity |
| Network optimization | Synthetic/test system and independently scoped preliminary BA/HiGHS demonstrations | Actual matched fleet, topology, branch parameters and calibrated Western OPF |
| Assumption sensitivity | 9 flat, 27 equal-energy supply shape and 27 greedy battery case-year screens with CI | Real renewable profiles, physically defensible dispatch optimization, cyclic storage SOC and economics |
| Presentation | Public README and research-method notes reflect evidence tiers | Publication-quality figures with direct sources, limitations, and versioned reproducible plotted results |

### Manuscript workstreams

**Old 2026-10-31 estimates should not be treated as current objective progress measurements.** It is more accurate to separate two paper scopes:

**A. Transparent-data / assumption-sensitivity methodological paper.** Evidence for source lineage and arithmetic reconciliation is strong. There are material preliminary Results (27 source-load/synthetic-supply scenarios and 27 storage variants). An argument about sensitivity to available-renewable hourly shape at equal annual energy is supported **inside the illustrative assumptions**. A complete literature comparison, credible economic framing, realistic profiles, storage cyclic boundary/optimality experiment and finished visual exhibits are still missing. **Current milestone: results-generating research prototype, not submission-ready manuscript.**

**B. Empirical Western power-system decarbonization / transmission / investment paper.** No authenticated real-generator to original synthetic network electrical crosswalk, no independently validated synchronous EFS+wind+solar hour clock, no actual network-constrained multi-year system solve, and no physical calibration. **Current milestone: empirical foundational data engineering, not validated policy/energy-transition results.**

### Defensible quantitative findings for a methodological framing

- Seven admitted Western states, 20 zones: modeled EFS zonal demand **274.707/306.839/350.871 TWh** (2030/2040/2050) across original 8,760-hour local ordinal series. **These are projections, not observed system consumption and not all Western interconnection demand.**
- 2040 archived naive 8,760-hour calendar labels contain Feb 29 but omit Dec 31, with 7,344 ordinal-aligned date-label differences versus pinned 2018 nonleap template. **Not evidence of lost source MWh.**
- At identical assumed 2030 per-zone renewable nameplate (90% of zonal demand peak) and equal hypothetical yearly renewable availability, the flat profile yields **73.0%** modeled renewable share while ordinal-wave A yields **64.4%**, a difference of **8.63 percentage points**, purely due to invented hour shapes.
- Under the ordinal-wave A and the assumed 2030 90%-renewable scenario, modeled unused renewable availability is **25.893 TWh** (no battery), **9.445 TWh** (4 h) and **2.605 TWh** (8 h), with 90% assumed round-trip efficiency and 25%-of-peak battery power. **This is not real grid curtailment.**
- The 2030 wave A 8-hour battery ends with **19.983 GWh** stored: annual cost/supply comparisons must address terminal SOC and battery dispatch optimality before being presented as cyclic-year engineering estimates.

### Scientific and publication next actions (priority order)

1. **Stop presenting simulated supply and storage as empirically measured/forecast.** Keep file/figure provenance labels on every display.
2. Test cyclic `SOC(8760)=SOC(0)` using an actual dispatch optimizer and compare against the existing greedy cases. Report losses, charging, curtailment, costs and optimizer primal feasibility. Use scoped toy zones before any bigger rollout.
3. Establish authoritative source EFS LocalHourID time semantics; then obtain verified hourly wind/solar profile source and documented point-by-point join. Do not silently reassign 2040 indices.
4. Choose research article target: *evidence-gated reproducible screening/assumption sensitivity* versus *empirical network-optimization* and align novelty plus figure set to that scope.
5. Pursue certified WECC electrical topology / POI mapping only as a separate critical path to eventual empirical OPF.

## Manuscript privacy

**Keep the working manuscript private/local.** The public repository contains reproducibility code, assumption screens and engineering technical notes; it must not be presented as a finished paper. Figures and results used in public readmes must remain accurately labeled source-demand-plus-synthetic-supply.

**This is a milestone assessment, not a percentage-complete claim.** No artificial project or manuscript completion percentage is asserted.
