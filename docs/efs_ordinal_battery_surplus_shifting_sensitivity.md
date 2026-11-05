# Full-year EFS ordinal-only synthetic battery shifting sensitivity

## Research question

Given the already verified 7-state EFS zonal demand and the three explicitly hypothetical, equal-annual-energy supply shapes in [the previous study](efs_ordinal_equal_energy_shape_sensitivity.md), how much does an assumed short-duration battery change **model-defined unused renewable availability** and **illustrative firm backup generation**?

The experiment is not a true PyPSA OPF, operational storage study, historical solar/wind analysis, or calibrated WECC simulation. It deliberately operates on original EFS `LocalHourID=1…8760`, without interpreting its unverified timezone and DST semantics.

## Controls and assumptions

- 2030, 2040 and 2050; 20 independent ReEDS zones in the seven admitted states.
- **Real inputs:** original staged EFS/LAF zonal hourly demand artifact from run `41281576025`; source file SHA-256 included in the output metadata.
- **Hypothetical renewables:** nameplate 90% of each zone's own annual demand peak, with identical 50%-mean annual available energy per zone. Three synthetic profiles: constant 50%, and opposite ordinal-24 waves `0.5 ± 0.35cos(2π(h−1)/24)`. They are mathematical perturbations, **not actual daily wind or solar patterns**.
- **Hypothetical battery:** duration 0, 4 or 8 hours, power equal to 25% of the zone's demand peak at positive durations; 90% round-trip efficiency split equally as `sqrt(.9)` charge/discharge efficiencies.
- **Rule:** greedily charge from renewable availability *excess to concurrent load*, discharge later only when concurrent availability is below load, otherwise use assumed firm supply; no grid exchange, arbitrage, forecast, or curtailment markets.
- **State of charge:** starts exactly at 0 MWh, never exceeds power×duration, and is tracked to the terminal hour. Terminal SOC is reported, **not counted as power delivered or falsely set to zero**.
- **Illustrative energy-related cost:** renewable direct and battery-charged MWh assessed at an assumed $5/MWh, firm generation $90/MWh. No capex, battery depreciation, asset lifetime, electricity prices, carbon prices, grid constraints, or operational costs are certified.

## Conservation tests

Each scenario/year verifies:

```text
renewable_direct_to_load + battery_discharge_to_load + firm_generation = EFS_zonal_demand

renewable_direct_to_load + battery_charge_input + unused_renewable = hypothetical_renewable_available

battery_charge_input * sqrt(.9) - battery_discharge_to_load / sqrt(.9) = terminal_SOC
```

Across the three durations for a given year and supply shape, real EFS demand and hypothetical renewable availability are **held strictly identical**; only the notional storage power/energy constraint changes. Source duplicate/missing/nonfinite/negative hours and battery bound violations are rejected.

## Reproducibility

- Python: `src/energy_transition/efs_ordinal_storage_sensitivity.py`
- Regression tests: `tests/test_efs_ordinal_storage_sensitivity.py`
- GitHub Action: [EFS ordinal synthetic renewable and battery duration sensitivity](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-ordinal-storage-sensitivity.yml)
- Artifacts: `efs_storage_27_synthetic_scenarios.csv` and `efs_storage_27_synthetic_scenarios_metadata.json`

**Status:** Code committed and source-backed CI triggered; do not treat numerical storage outputs as confirmed until its specific run passes and output logs are reviewed.

## Interpretation and future admission

Any positive modeled benefit is **conditional on arbitrary supply shapes, zero initial SOC, absence of network exchange, battery sizes/costs and greedy dispatch**. It cannot be claimed as actual storage energy saved, grid reliability improved, verified CO2 reduction or financially justified storage investment. The next scientific step is to validate source EFS time semantics and ingest independently sourced renewable profiles, then consider a genuine source-constrained storage/network optimization instead of ordinal-only screening.
