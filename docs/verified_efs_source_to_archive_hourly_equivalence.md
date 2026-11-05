# Source-to-archive EFS zonal hourly equivalence: full 8,760-hour gate

## Motivation

The original 2030/2040/2050 seven-state EFS Load-only NetCDFs were created by the repository's own `efs_real_load_attachment_pilot.py`. Its actual mechanism is:

1. Load staged `efs-real-laf-zonal-pilot.csv.gz`, using source fields `year,state,reeds_zone,local_hour_id,allocated_mw`.
2. Select each `state × reeds_zone`, reindex `local_hour_id` to **1...8760**.
3. Attach one PyPSA `Load` per zone, with power values in that **local-hour ordinal** order.
4. Assign a naive synthetic 8,760-hour `pd.date_range(f"{year}-01-01", periods=8760, freq="h")`; these are not certified UTC timestamps.

The last step creates the 2040 stored leap-year label problem; it does **not** add the pinned upstream +7/+8-hour shift on load attachment. The pinned upstream shift audit and these separate staged local-hour source files must never be conflated.

## New full source-value comparison

The `efs_zonal_archive_hourly_equivalence.py` validator downloads the **same original archived workflow artifact** (run `41281576025`) containing both staged zonal CSV and three load-bearing NetCDF networks. For each year, zone and ordinal hour, it tests:

- 8,760 unique source-hour IDs per zone, with no duplicate `year/state/zone/hour` keys.
- Presence of precisely matching `EFS_<year>_<zone>_<state>` network Load IDs, with no unexpected extra Loads.
- Numerical equality of **each archived Load MW value** and its staged zonal source value, including static-only Load components, at tolerance `atol=1e-6 MW, rtol=1e-10`.
- Fail-closed behavior on source-value perturbations, missing components, invalid/negative values or inconsistent hours.
- Audit JSON for each model year with compared values, mismatch counts and max absolute MW error.

Source-run comparison CI: [latest EFS archival clock and equivalence workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-actual-snapshot-semantics.yml). **Do not claim the numerical comparison succeeded until the Actions run reports success.**

## Scientific boundary

If successful, this proves **staged EFS zonal hourly allocation → archived NetCDF Load** numeric equality and establishes archived row index (i) corresponds to staged `local_hour_id=i+1`. It does **not** independently certify that earlier original NLR EFS CSV hours use physical local standard time, DST or UTC, nor align demand to weather/generation, verify electrical branch ratings or justify 2030–2050 calibrated OPF results.

Remaining next step: verify **original state EFS demand → staged LAF zonal load** hourly with independent original source data, including source CSV hashes and state-year weighting, then separately certify the EFS time convention before synchronizing supply profiles.
