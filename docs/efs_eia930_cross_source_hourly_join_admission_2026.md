# Cross-source temporal admission: original 2030–2050 EFS load vs 2024 EIA-930 signed generation

## Purpose

Project B has two legitimately independent, auditable source families:

1. **EFS future load:** original published state hourly projected loads, then checked source-LAF-zone and NetCDF load-only pathways, on `LocalHourID=1...8760` per 2030/2040/2050 for seven admitted states and twenty source ReEDS zones. **The original EFS physical UTC/DST, hour-ending and weather-year meaning is not independently certified**; stored naive 2040 calendar labels are known to be inconsistent with the source 8760-hour nonleap convention.
2. **EIA-930 observed net generation:** reported **2024** solar/wind net MWh for CAISO (CISO) and BPAT, with four complete 168-hour observed periods and 16 BA×fuel×season subsets. These are measured *reported net output*, may be negative, and are **not available generation potential or 2030–2050 hourly wind/solar forecasts**.

This audit reopens the same original archived source files as independent previous CI checks and explicitly verifies source-year identities, temporal keys, missing/duplicate records, and original SHA256. The resulting decision is deliberately **fail closed**: **zero future EFS–historical EIA-930 hourly rows are joined**.

## Source acceptance checks

- Exact EFS projection years `2030,2040,2050`, 20 source zones, 8,760 distinct original local-hour IDs per `year/state/zone`, no duplicates.
- Exact observed EIA-930 year `2024`, four seasons, two original BAs, two fuels, 16 panels × 168 consecutive UTC-marked hourly records, no duplicates.
- Original compressed EFS input and original EIA-930 seasonal CSV SHA-256 included in JSON evidence.
- Explicitly **not admitted**: `LocalHourID`→physical UTC; 2040 leap-calendar semantics; EFS scenario-to-EIA weather-year identity; ReEDS zones-to-BA population mapping; historical net generation-as-uncurtailed-availability; future matched generator nameplate.

No pseudo-UTC timestamp is constructed from an EFS ordinal. No weather-year matching, capacity-factor normalization, physical Western network simulation or 2030–2050 projection is fabricated.

## Reproduction

- `src/energy_transition/efs_eia930_cross_source_join_gate.py`
- `tests/test_efs_eia930_cross_source_join_gate.py`
- [GitHub Actions source-join audit](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-eia930-source-join-gate.yml)
- Original EFS zonal hourly source: run `41281576025`, artifact `real-western-base-network-attempt`, file `efs-real-laf-zonal-pilot.csv.gz`.
- Original EIA observed source: run `41003777337`, artifact `eia930-hourly-solar-wind-2024`, file `seasonal_observed_renewables.csv`.
- Audit evidence artifact: `efs-eia930-original-source-join-admission-evidence`, report `efs_eia930_cross_source_join_refusal.json`.

## Scientific interpretation and next admission work

A passing CI here demonstrates successful reproducibility of the **refusal decision and actual source coverage**; it does not establish that all requested evidence is available. A claimed 2030–2050 weather-driven capacity-factor experiment requires an independently time-stamped EFS source convention, weather-year selection policy, a source-supported capacity-normalized and geographically mapped wind/solar resource series, and explicit handling of the 2040 representative-year date labels. Even after a successful source join, physical Western network dispatch additionally needs authenticated generator-to-bus electrical mapping and real line/network parameters.

Until then, the paper may discuss historical EIA-930 observed generation-shape descriptive results and the separate EFS future-year **synthetic** supply sensitivity, but must not present either as a validated synchronous joint EFS-plus-weather experiment.
