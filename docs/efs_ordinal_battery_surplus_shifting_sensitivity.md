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

**Verified numerical execution:** [Actions run #42100384015](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42100384015) **PASSED**, including source-hour validation, mass/SOC energy balance, all 27 scenario-year runs and artifact upload. These are verified *illustrative calculations*, not validated real-world generation/storage values.

## Verified example outcomes: synthetic supply wave A at 90% zone-peak renewable nameplate

| Planning year | Hypothetical storage | Model unused renewable, TWh | Hypothetical firm generation, TWh | Battery discharge to load, TWh | Terminal stored energy, GWh |
|---|---|---:|---:|---:|---:|
| 2030 | None | 25.893 | 97.871 | 0 | 0 |
| 2030 | 4 h | 9.445 | 83.086 | 14.785 | 19.983 |
| 2030 | 8 h | 2.605 | 76.930 | 20.940 | 19.983 |
| 2040 | None | 28.934 | 109.313 | 0 | 0 |
| 2040 | 4 h | 10.559 | 92.796 | 16.517 | 22.322 |
| 2040 | 8 h | 2.914 | 85.916 | 23.397 | 22.322 |
| 2050 | None | 33.104 | 124.992 | 0 | 0 |
| 2050 | 4 h | 12.088 | 106.102 | 18.891 | 25.529 |
| 2050 | 8 h | 3.338 | 98.227 | 26.766 | 25.529 |

For the 2030 wave A assumptions, 8-hour battery duration cuts modeled unused hypothetical supply by **23.288 TWh** compared with no battery, while reducing illustrative firm generation by **20.940 TWh**. Their difference is explained by modeled storage conversion losses and positive terminal energy: **a reduction in unused energy is not equivalent to delivered renewable supply**.

**Boundary effect:** the 2030 wave A storage cases terminate with approximately **19.983 GWh** of combined stored energy (2040: 22.322 GWh; 2050: 25.529 GWh). This is **not counted as supply to load or discarded** and means that a stationary cyclic-storage interpretation would require a separate terminal SOC constraint or additional adjustment. The greedy dispatch is not a cost-optimized battery policy.


## Interpretation and future admission

Any positive modeled benefit is **conditional on arbitrary supply shapes, zero initial SOC, absence of network exchange, battery sizes/costs and greedy dispatch**. It cannot be claimed as actual storage energy saved, grid reliability improved, verified CO2 reduction or financially justified storage investment. The next scientific step is to validate source EFS time semantics and ingest independently sourced renewable profiles, then consider a genuine source-constrained storage/network optimization instead of ordinal-only screening.
