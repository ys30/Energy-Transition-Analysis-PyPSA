# Seven-state EFS full-year supply sensitivity: local-hour ordinal planning screen

## Scientific scope and purpose

This adds a **complete 8,760-hour, three-planning-year** screening model using independently verified [seven-state EFS state-to-zone-to-NetCDF load provenance](efs_source_to_zonal_laf_hourly_reconstruction.md). Demand is sourced; illustrative supply assumptions are **not** observed plants, historical renewable output, seasonal supply, or an independently calibrated Western interconnection.

Instead of labeling the 2040 naive `pd.date_range` index as verified synchronized UTC, the experiment preserves and computes directly on the original `LocalHourID=1…8760` ordinal.

The experiment is *not* a PyPSA OPF solve: it is a transparent **closed-form, independent-zone, least-marginal-cost merit-order screening** exercise without storage or interzonal transmission. This design intentionally avoids implying actual grid connectivity while the [EIA generator-bus evidence gate](eia860_archived_synthetic_candidate_structural_validation.md) still reports zero independently verified electrical POI mappings.

## Assumptions, applied independently to each source ReEDS zone

For each year, zone and LocalHourID:

- `peak` = maximum real EFS modeled zonal hourly demand (MW) over its 8,760 ordinals.
- Hypothetical renewable nameplate `p_nom` = 30%, 60%, or 90% of that zone's own source demand peak.
- Hypothetical renewable available output = `p_nom × 0.5` **at every ordinal hour** (constant 50% capacity factor; no wind or irradiance observation).
- Hypothetical firm dispatchable nameplate = 120% of that zone's peak, ensuring full demand is always feasible under this toy construction.
- Assumed variable costs: $5/MWh renewable, $90/MWh firm; dispatch renewables first due to lower assumed cost. Illustrative objective is *not* historical operating expenditure or investment cost.
- Dispatch: `renewable = min(demand, available_renewable)`, `firm = demand - renewable`, `curtailed = available_renewable - renewable`.

The implementation enforces exactly 8,760 unique source ordinal hours for every zone and year; rejects negative or missing MW/keys; verifies supply-demand and renewable-availability accounting. It emits an auditable CSV with nine scenario-year records plus a JSON metadata document explicitly setting `physical_western_opf_admitted=false` and `utc_weather_alignment_verified=false`.

## Reproduction

- Source: `src/energy_transition/efs_ordinal_full_year_supply_sensitivity.py`.
- Tests: `tests/test_efs_ordinal_full_year_supply_sensitivity.py`, including corrupted/missing source hours and renewable curtailment accounting.
- Workflow: [EFS full-year ordinal-only supply sensitivity](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-ordinal-full-year-sensitivity.yml).
- Input artifact: `efs-real-laf-zonal-pilot.csv.gz`, original workflow run `41281576025`, artifact `real-western-base-network-attempt`.
- Output artifact: `efs-seven-state-8760h-illustrative-ordinal-supply-screen`, with `efs_ordinal_supply_full_year_scenarios.csv` and `efs_ordinal_supply_full_year_metadata.json`.

**Verification status:** workflow submitted; report numerical outputs as verified only after this real archived-source workflow succeeds. The assumptions are deliberately static, so ordinal sensitivity does **not** support annual wind variability, evening peak, extreme event, curtailment on the real grid, 2030–2050 emissions reductions or actual Western price predictions.

## Higher-value follow-on analyses

1. Resolve EFS source `LocalHourID` timezone, DST and calendar mapping before external renewable profile or weather time joins.
2. Develop empirically supported zone-specific renewable resource profiles and explicit generators, keeping provenance and capacity scenario assumptions separate.
3. Incorporate traceable geographic transfer capacities and storage to study constrained dispatch rather than a disconnected-zone screen.
4. Conduct uncertainty/sensitivity analysis across source load growth, capacity, costs, profile assumptions and transmission, and clearly differentiate assumption-driven outcomes.
