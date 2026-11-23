# Paper S — ReEDS 2022 demand / real wind–PV admission contract (2026-11-10)

**Scope:** New independent ReEDS 2022 four-state × three-model-year scenario. Do not alter the frozen EFS2020 / LocalHourID synthetic study.

## Verified publisher source conventions
- Demand: `demand_EFS_REFERENCE.h5`, Zenodo 18461543, publisher MD5 `7b2055d43200744a16a8c4fed68b1a17`; 2012 fixed CST UTC-06:00, 8760 hours inclusive of Feb 29 and exclusive of Dec 31; **hour-ending energy** (MWh/h).
- Land wind v1: `cf_wind-ons_reference_ba.h5`, Zenodo 18422200, publisher MD5 `8fd010e1d38f9a8591ba58c9eff1a368`.
- Utility PV v1: `cf_upv_reference_ba.h5`, Zenodo 18407660, publisher MD5 `398165a0a7ec5c21d3e891a28162a217`.
- Wind/PV v1: 2012 fixed CST weather; source **instantaneous capacity factor at exact hour**. Same hour labels do not certify interval-integrated generation.
- Published PV CF uses MW(AC grid) / MW(DC array); multiply by ILR 1.34 to obtain MW(AC grid) / MW(AC nameplate), then validate bounds and source capacity unit before weighting.

## Required independent physical hourly contract
Let `t_k` be the source demand hour-ending timestamp, with fixed UTC-06:00 timezone. Demand `D[k]` is energy over `(t_k-1h,t_k]`. Weather `c(t_k)` is an instantaneous value at `t_k`.

**PROHIBITED:** `renewable_energy[k] = capacity * c(t_k)` claimed as a publisher-proven hourly energy profile without an explicit integrating convention.

For a sensitivity-only candidate, a transparent trapezoid `E[k] = capacity * (c(t_{k-1}) + c(t_k))/2 * 1h` needs the preceding-hour source sample, including the year boundary for `k=0`. Such an approximation is **not** source-certified physical hourly energy, and it is not a pass of the admission gate. Do not silently cyclic-wrap 2012-12-30 to 2012-01-01. Investigate publisher/ReEDS source modeling semantics and handle boundary hours explicitly before a new empirical headline result.

## Spatial / technology contract
- ReEDS renewable columns are `{class}|p{BA zone}`, **not** state codes. Capacity supply curves `sc_*_reference_ba.csv` and `county2zone.csv` provide resource class/BA and county/BA data, but do not by themselves define fractional interstate BA-zone ownership.
- Crosswalk each ReEDS BA resource-zone polygon to a **documented state allocation** using county FIPS and audited geographical rules; identify BAs crossing state borders. Never assign whole BA profiles to states using only a string match or majority state without quantifying error.
- State energy CF weighting must be capacity-consistent, `CF_state(t)=sum_j K_j CF_j(t)/sum_j K_j`, with documented `K_j`, units, exclusions, and no double counting.
- Verify technology-dependent capacity denominator: especially PV DC-to-AC correction and supply-curve MW normalization.
- Explicitly declare that 2030/2040/2050 **demand projections** are combined with 2012 reference weather, not contemporaneous 2030–2050 meteorological forecasts.

## Fail-closed executable gates for the next workflow
1. Both official 2012 publisher HDF5 files, capacity tables and county2zone table pass exact publisher MD5.
2. Demand and renewable 2012 source calendars each pass independently: contiguous 8760, Feb 29 present, Dec 31 absent, fixed UTC-06:00 interpretation; preserve native timezone/offset metadata.
3. Verify raw CF scaling from actual source dtype/attributes and full matrix (no sample-only validation); report native and normalized ranges plus abnormal rows.
4. Verify 134-zone geographical schema and county-to-state fractions, cross-state BAs, unallocated or duplicated records; reject silent fallback.
5. Verify resource-class capacity weighting and PV AC conversion with independent sum-of-capacities and unit assertions.
6. Obtain or define and prominently label the wind/PV instantaneous-to-hour-ending interval transformation. **No empirical hourly co-optimization admission until defensible.**
7. Once all gates pass, solve the exact source-backed LP and compare cost, curtailment, discharge, peak shifting and sensitivity; preserve separate IDs, figures and provenance from legacy EFS2020.

## Current certification status
- ReEDS2022 independent *demand* source: PASS; official archived workflow #42958394795.
- Wind/PV intake workflow `.github/workflows/paper-s-reeds2022-wind-pv-source-intake.yml` exists; workflow execution status must be checked separately. Authenticated bytes alone do not establish spatial aggregation or energy-interval compatibility.
- State-weighted wind/PV physical join: **BLOCKED**.
- New real-renewable LP runs and Paper S empirical results: **NOT YET EXECUTED/CERTIFIED**.

Source pages:
- https://zenodo.org/records/18461543
- https://zenodo.org/records/18422200
- https://zenodo.org/records/18407660
