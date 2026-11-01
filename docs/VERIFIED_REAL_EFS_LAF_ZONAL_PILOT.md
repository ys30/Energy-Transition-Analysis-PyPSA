# Verified first EFS-to-real-Western-network LAF zonal pilot

**Verified GitHub Actions run:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41276635829

## Actual result

The pinned upstream PyPSA-USA Western base network was rebuilt successfully. The EFS source artifact from run 41265678862 was joined with the actual built-network `LAF_state` field and real bus `state`/`reeds_zone` labels.

- **525,600** zonal state/year/local-hour output rows, written to `efs-real-laf-zonal-pilot.csv.gz`.
- Three EFS target years: **2030, 2040, 2050**.
- **Seven admitted states by numerical LAF gate:** Arizona, Colorado, Idaho, Montana, New Mexico, Utah and Wyoming.
- **Four excluded pilot states:** California (nonfinite bus LAF), Nevada (sum exceeds numerical threshold), Oregon (nonfinite bus LAF), Washington (nonfinite bus LAF and invalid state sum).
- Per-state/year EFS-to-zonal allocated-energy checks passed in the pipeline. For split-interconnection states (MT/NM), sums below one preserve the partial-Western demand fraction rather than secretly renormalizing to full-state total.
- Result is a reproducible real-input **spatial demand projection**, not a solved PyPSA optimization.

## Reproduction and provenance

`src/energy_transition/efs_real_laf_zonal_pilot.py` runs within `.github/workflows/pypsa-usa-real-western-base-network.yml`. The Action stores `efs-real-laf-zonal-pilot.csv.gz` and `efs-real-laf-zonal-pilot.json` alongside the actual NetCDF and original LAF audit. Source EFS scenario: NLR Reference/Moderate.

## Critical remaining limits

1. LAF weights were extracted from the pinned upstream-built network but their demographic/geographic derivation has **not** been independently certified.
2. `LocalHourID` has not been reconciled to UTC, daylight saving time or PyPSA network snapshots.
3. California, Nevada, Oregon and Washington cannot yet be safely admitted without further LAF investigation; Texas is not in the core-11 EFS pilot; no cross-border demand assumptions have been validated.
4. The **525,600** rows do not represent 525,600 hours, nor do they mean the entire Western grid demand is covered. No emissions, investment or operational cost findings are supported by this pilot.

**Next actual modeling milestone:** perform state-hour to zone energy-conservation validation with independent summary statistics, then align validated regional time series to snapshots and construct a load-bearing network for optimization.
