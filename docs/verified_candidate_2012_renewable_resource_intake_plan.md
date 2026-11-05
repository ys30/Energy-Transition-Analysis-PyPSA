# Project B: 2012 source-year wind/solar resource intake — evidence and restrictions

## Why 2012 is a candidate, not an approved future EFS clock

The original [2020 Electrification Futures Study (EFS) Load Profiles release](https://data.nlr.gov/submissions/126) contains published Reference/Moderate 2018–2050 model-year demand. Its public catalog explains EnergyPATHWAYS-derived and ReEDS-calibrated projected load, but **does not independently define `LocalHourID` as UTC, CST, physical local time or a 2012 weather-year timestamp**.

The related but later [ReEDS electricity demand profiles 2022](https://zenodo.org/records/18461543) explicitly describe **2012 weather/calendar, U.S. CST UTC-06:00, hour-ending profiles, and December 31 dropped for 8,760h**. Those metadata describe the newer ReEDS release and **cannot automatically be transferred** to the project's older original EFS 2020 CSV. The NLR EFS scenario methodology used 2012 weather-related input shapes, but that **alone does not establish a precise source `LocalHourID` → UTC equivalence** in the distributed original 2020 zip.

## High-priority weather/resource candidates from authoritative source documentation

| Candidate | Resource coverage | 2012 available? | Relevant source controls | Unresolved conversion |
| --- | --- | --- | --- | --- |
| [NLR WIND Toolkit V2](https://developer.nlr.gov/docs/wind/wind-toolkit/wtk-download/) | U.S. modelled wind meteorology, 2007–2014 | Yes | `names=2012`, `interval=60`, `utc=true`, `leap_day=false` and geographic WKT | Site/height wind speed requires turbine-specific power curve, hub-height validation and source geographic aggregation |
| [NLR NSRDB resource data](https://developer.nlr.gov/docs/solar/nsrdb/) | GHI/DNI/DHI and meteorological solar resource | Check exact product/year coverage before request | Use product-supported `names=2012`, 60-minute data, explicit `utc=true` and `leap_day=false`; [download guide](https://developer.nlr.gov/docs/solar/nsrdb/guide/) | Irradiance requires independently specified PV module, orientation, derating, inverter and capacity definition; not a solar capacity factor |
| [EIA-930 2024 realized solar/wind net generation](verified_eia930_hourly_renewables_2024.md) | Observed BA-level signed actual output | 2024, not 2012 for this archived analysis | Explicit observed UTC rows with missing/negative values retained | Cannot be treated as unconstrained renewable available potential or independently forecast 2030–2050 capacity |

A current developer API often requires a key, location, requester contact details and/or server-side archive preparation. **No user identity, email, API credentials or geographic sample site has been invented or submitted in this phase**, and no WTK or NSRDB CSV has yet been imported.

## Intake contract implemented

The new source-validator `src/energy_transition/renewable_2012_resource_intake.py` accepts **only a provided site-specific source CSV and explicit companion metadata**. For an initially scoped 2012 candidate it verifies:

- Explicit provider family (`wind_toolkit` or `nsrdb`) and HTTPS source, product/year, request flags (`UTC=true`, `leap_day=false`, `interval=60 minutes`), source/header UTC offset and declared interval time semantics.
- Exactly **8,760 complete 2012 UTC-hour keys with 2012-02-29 omitted**, matching a declared uniform source minute timestamp (including a possible 30-minute midpoint convention).
- Finite nonnegative wind-speed or solar irradiance values, conservative extreme-value screening, source geographic coordinates and original request provenance.
- SHA-256 of submitted source CSV and metadata when actual provider files are available.
- The output always records `generator_capacity_factor_computed=false`, `original_EFS_LocalHourID_utc_mapping_verified=false`, `EFS_load_resource_join_admitted=false` and `physical_Western_OPF_admitted=false`.

**CI verified:** [resource intake validation #42117188587](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42117188587) passed all **six synthetic-fixture regression tests**, including the 2012 nonleap source UTC sequence, resource values and rejection of missing, duplicate, shifted and unsupported source time metadata. **Synthetic tests alone do not constitute empirical resource data retrieval:** no actual WIND Toolkit or NSRDB site CSV was downloaded or used in the original EFS demand model.

## Production admission checklist and scientific critical path

1. Obtain original 2020 EFS `LocalHourID` source-clock documentation or publisher clarification: **time zone, start/end convention, calendar year, DST policy, leap-day rule and any wrap or fixed offset introduced by upstream ReEDS processing**.
2. Verify a **named 2012 solar and wind product's genuine data-availability window** and explicit API request parameters; choose well-documented geographically grounded candidate sites or a transparent spatial sample covering the admitted ReEDS zones.
3. Retrieve and hash source CSVs, enforce exact timestamp/units and missingness/negative/QC gates, then construct site-specific weather-to-power conversions with turbine/PV specifications and explicit model capacity.
4. Independently validate the source zone/BA geographic mapping and weather-year coincidence of EFS projections. **Never join by `LocalHourID` alone** or silently substitute the later ReEDS HDF5 clock.
5. Only then run a physically interpretable renewable-supply sensitivity, while still withholding genuine Western network OPF claims until electrical plant/POI and transmission constraints are admitted.

## Journal manuscript interpretation

The 540 annual LP scenarios remain valid **conditional mathematical illustrations** with projected source EFS demand, not weather-driven forecasts. The standalone EIA-930 2024 weekly analysis remains real observed signed generation, not renewable energy available. The future weather-year route is technically feasible but **not yet empirically run or certified**.
