# Source-generation admission: Western EFS 2030–2050

**Successful source-gate CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41771905008

This is a read-only evidence check against the **real saved Western topology** and its three **real-input EFS load-bearing** archived NetCDF files. It is deliberately not an OPF calculation.

| Archived network | Buses | Loads | Generators | Source-based 2030–2050 generation admission |
| --- | ---: | ---: | ---: | --- |
| Real base Western topology | 10,157 | 0 | 0 | **blocked** |
| EFS 2030 load-only | 10,157 | 20 | 0 | **blocked** |
| EFS 2040 load-only | 10,157 | 20 | 0 | **blocked** |
| EFS 2050 load-only | 10,157 | 20 | 0 | **blocked** |

The source inputs have 9,726 lines and 2,080 transformers. The generator and hourly generator-availability columns are empty in all four files. The EFS load-only files have 8,760 ordinal local-hour snapshots, but not independently certified physical UTC-aligned demand. Previous load-component audits verified 19 time-varying load components and one legitimate static-zero load.

The new `src/energy_transition/western_supply_admission_gate.py` requires explicit source and revision fields for the generator fleet, original generator-to-bus mapping, plant capacity/fuel, wind/solar hourly availability, dispatchable operating constraints, marginal and fuel costs, geography and temporal evidence. It also checks generator capacities, buses, carriers and valid 0..1 dynamic availability **if** generator components exist. Even a numerically plausible toy generator does not clear independent source provenance.

## Existing authentic generation evidence that can be reused

- Official **EIA-860** historical nameplate and operating-status analysis is already implemented in `eia860_generation_readiness.py` and `eia860_matched_generator_capacity.py`. This is valuable for assembling source-authenticated historical powerplants, but an EIA operating nameplate MW is **not** an approved 2030/2040/2050 plant capacity, hourly dispatch availability, or verified electrical bus/transformer.
- Official **EIA-923** generator generation/fuel-accounting and **EIA-930** balancing-authority hourly generation/wind/solar data exist in existing project modules. The 2024 BA boundaries and missing observations are not equivalent to modern 11-state ReEDS zones; those sources require plant ID, BA and timeline reconciliation before admission.
- `wind_availability.py` and `solar_availability.py` implement documented **illustrative** profiles for scenario engineering; they must not be silently substituted for measured or independently modeled Western 2030–2050 meteorological availability.
- The pinned PyPSA-USA upstream generator workflow should be the primary path for real source-unit construction: `build_powerplants`, `build_fuel_prices`, `build_cost_data`, and `add_electricity`, with supported historical PUDL/EIA sources, documented scenario assumptions and explicit network-attachment provenance. See `docs/REAL_GENERATION_DATA_INTEGRATION_PLAN.md`.

## Next scientific work in dependency order

1. Recover and validate a frozen source-version-compatible Western generator fleet from the upstream `build_powerplants` data flow. Quantify number of active units, locations, EIA IDs, type, MW, statuses, missing mappings and unmapped capacity.
2. Match units to actual network electrical buses using the pinned mapping method; distinguish geographic nearest-bus methods from verified physical POIs.
3. Document independently sourced 2030/2040/2050 retirement/addition and technology/cost assumptions. Historical 2024 EIA-860 inventory alone cannot define future units.
4. Produce time-indexed wind/solar availability and dispatchable constraints on the **same independently approved UTC snapshot calendar** as the final EFS load and weather input.
5. Reassess true topology/zone operating ratings and electrical feasibility before **any** physically constrained, genuinely sourced full-Western OPF.
6. Only then develop paper conclusions on cost, reliability, curtailment and emissions. The validated 11-state mixed-clock peak results remain an **engineering sensitivity**, not calibrated transition results.

**Status:** Source load and geographic sensitivity engineering is reproducible; full Western future power-plant portfolio and common supply-demand time series are absent. Therefore empirical OPF is correctly blocked.
