# Paper S alternative input branch — ReEDS 2022 independently timestamped demand (10 November 2026)

**SOURCE SWITCH COMPLETED AND CI ACCEPTED — DEMAND INPUT ONLY.** This is a new state-level projected demand analysis, **not** a silent replacement of prior EFS2020 p-zone results. The source HDF5's publisher identity and exact calendar have been directly verified; the wind/PV matching and new LP model runs remain separate pending gates.

## Original publisher source and verified execution

- [ReEDS: Electricity demand profiles 2022](https://zenodo.org/records/18461543), DOI **10.5281/zenodo.18461543**.
- Original file **`demand_EFS_REFERENCE.h5`**, publisher MD5 `7b2055d43200744a16a8c4fed68b1a17`.
- Publisher documents **gross end-use MWh/hour, hour-ending, 2012 reference weather/calendar, CST (UTC−06:00)** and dropping the last day of the leap year (so 8,760 hours).
- Actual HDF5 fetched and MD5 checked by [dedicated workflow #42958394795](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42958394795), **SUCCESS**; strict clock/index tests also passed. **Four states × three model years**, preserving the 2012 reference calendar.

| Model year | Arizona annual MWh | Colorado annual MWh | Idaho annual MWh | Wyoming annual MWh |
|---|---:|---:|---:|---:|
| 2030 | 89,415,913 | 64,966,091 | 27,988,736 | 21,009,163 |
| 2040 | 99,976,213 | 72,638,899 | 31,294,341 | 23,490,406 |
| 2050 | 114,477,979 | 83,175,174 | 35,833,633 | 26,897,696 |

All twelve source state/year series contain 8760 nonnegative values, no zero hours. Original publisher-file verified time labels span **2012-01-01 00:00:00-06:00 through 2012-12-30 23:00:00-06:00**, with February 29 and no December 31, across all three model years.

Code:
- [input parser and publisher-source verification](../src/energy_transition/reeds_2022_clocked_demand_branch.py)
- [strict time-index tests](../tests/test_reeds_2022_clocked_demand_branch.py)
- [CI workflow](../.github/workflows/paper-s-reeds2022-clocked-demand.yml)
- Artifact `paper-s-reeds2022-independent-source-state-year-clock-validation`: twelve-row annual/peak summary and clock/identity metadata, **not the original third-party HDF5 bytes**.

## Matched-version renewable candidates

Prefer ReEDS publisher's **v1** weather profiles with the same explicitly documented constant **CST** and 2012 weather year. Do **not** combine 2022 CST demand with the new ReEDS wind/PV v2 UTC sources without an exact timezone transform.

- [Land-based wind v1](https://zenodo.org/records/18422200), DOI **10.5281/zenodo.18422200**: `cf_wind-ons_reference_ba.h5`, original publisher MD5 `8fd010e1d38f9a8591ba58c9eff1a368`; `sc_wind-ons_reference_ba.csv` and `county2zone.csv` provide candidate capacity and geography audit inputs.
- [Utility-scale PV v1](https://zenodo.org/records/18407660), DOI **10.5281/zenodo.18407660**: `cf_upv_reference_ba.h5`, original publisher MD5 `398165a0a7ec5c21d3e891a28162a217`; publisher data report PV CF in MW_AC_grid/MW_DC_array and inverter loading ratio **1.34**; `sc_upv_reference_ba.csv` and `county2zone.csv` required for capacity and geography validation.

These weather profile files represent **instantaneous values on the hour**, whereas demand is **hour-ending MWh/h**. The publisher's time zone is known for each, but matching date strings is **not** proof of equal physical hourly energy support. A documented averaging/boundary contract or author clarification is still needed. The wind/PV site resource classes use **ReEDS BA p-zone identifiers** while demand is **state-level**; it is not valid to treat old EFS2020 p-zone values as a state/BA mapping. Official county→BA and capacity weighting must be audited.

## Two separate scientific outputs

1. **Frozen historical synthetic study** — original EFS2020 `LocalHourID`, 20 projected zones (seven distinct positive source shapes), Wave A/B resource profiles, original five figures and sensitivity work. Those numbers do not change and their original source hour clock is still uncertified.
2. **New real-resource-ready ReEDS2022 branch** — 12 authenticated state/model-year demand traces with explicit source clock; true ReEDS wind/PV site/BA data and actual physically supported hour/zone join are **not yet authenticated**, and **zero** new real-wind/solar LP results have been claimed.

**Data release permissions:** Publisher ReEDS 2022, wind and PV Zenodo records display no readable positive named license in the record's Rights section checked here; public access is not automatic redistribution permission. CI artifacts export original analysis summaries and clock metadata only, not original source bytes.

## Exact publication acceptance gate

Authenticate on-disk publisher wind/PV HDF5 checksums, retrieve 2012 profiles, verify their native offset/instantaneous semantics and AC/DC units, reconstruct **state-weighted** renewable CF from the published county→ReEDS-BA source mapping and ReEDS capacity supply tables, then certify physical hourly interval compatibility (not row-count alignment). Only after those checks may the original SciPy/HiGHS storage LP be rerun using **new ReEDS2022 model input**, with Results and figures labeled as a new independent source-backed experiment rather than an EFS2020 rerun.
