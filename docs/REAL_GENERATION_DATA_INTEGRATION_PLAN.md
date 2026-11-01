# Transition from synthetic generators to real PyPSA-USA electricity assets

## Decision

Stop presenting the real-line/synthetic-generator 6-bus pilot as an empirical Western generation-cost model. Use the pinned PyPSA-USA build pipeline to obtain source-attributed real generator data before interpreting dispatch cost, generation technology mix, or emissions.

## Official upstream paths

PyPSA-USA documentation: https://pypsa-usa.readthedocs.io/en/stable/data-generators.html and https://pypsa-usa.readthedocs.io/en/stable/model-workflow.html

Required rules in documented order:
- `build_base_network` (already verified here)
- `aggregate_to_substations`, `build_bus_regions`
- `build_powerplants` (unit fleet from PUDL EIA-860/EIA-923, supplemented as documented)
- `build_fuel_prices` and `build_cost_data`
- `add_electricity` and `data_model` only after upstream evidence is present.

Data requirements:
- EIA-860 nameplate capacity, operating status, technology and plant geography;
- EIA-923 generation, fuel costs / heat rates with provenance;
- WECC ADS and ATB where documented; PUDL normalizations;
- link generator to its original bus and check date/future retirement treatment.

## Research gates

1. Produce generated `powerplants.csv` using the **pinned** upstream PyPSA-USA workflow, not manually invented capacity rows.
2. Report actual record count, states, capacities, missing source fields and carrier distribution.
3. Verify scenario-year assumptions and cost-year currency before comparing 2030/2040/2050.
4. Refuse empirical cost/emissions claims while EFS LocalHourID remains unaligned across geography.
5. Exclude current illustrative generator outputs from all final manuscript quantitative claims.

## Current status

Base network, real zonal EFS load and 6-bus physical-line solver verified. Generator fleet and associated costs NOT built or verified; timezone provenance remains BLOCKED. This file is an implementation plan, not proof of the generator pipeline.
