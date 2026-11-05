# Cross-release source hourly audit: EFS 2020 vs independent ReEDS 2022 EFS_REFERENCE

## Research question

Original NLR 2020 `EFSLoadProfile_Reference_Moderate.csv` grouped to 11 Western states × 2030, 2040, 2050 has independently verified annual loads 774.400/855.707/980.023 TWh. The later publisher ReEDS 2022 `demand_EFS_REFERENCE.h5` yields near-identical annual values. **Are the underlying 289,080 source-hour MW observations also numerically equivalent?** Do they have any consistent fixed ±12-hour displacement?

Annual totals matching is not a valid proof of subdaily alignment. This new branch performs a side-by-side original archived-data comparison, not a new hypothetical load or wind experiment.

## Authenticated sources

1. **Original 2020 NLR EFS Reference/Moderate source**: the immutable `efs-core-west-2030-2040-2050-hourly.csv.gz` produced by original source-acquisition workflow [#41262154939](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41262154939), artifact `pypsa-usa-efs-source-evidence`. Fields: `year,state,local_hour_id,load_mw`, all 8,760 ordinals.
2. **Separate official ReEDS 2022 reference release**: [Zenodo record 18461543](https://zenodo.org/records/18461543), file `demand_EFS_REFERENCE.h5`, **publisher MD5 `7b2055d43200744a16a8c4fed68b1a17`**. Native HDF5 8,760-hour 2012 CST `-06:00` clock, Feb 29 retained and Dec 31 omitted, verified in [#42117983010](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42117983010).

## Source-hour acceptance checks

- All **11 states × 3 model years × 8,760 hours = 289,080 source-hour pairs**, identical state-year naming but independent source files.
- Strict source key coverage and duplicate/missing/infinite/negative input rejection, and complete 2012 CST ReEDS native source clock.
- Independent state-year annual energy, per-hour mean absolute error, maximum error, number of matching hourly observations under **0.01 MW** absolute tolerance, and **fixed-offset searches from -12 to +12 hours** on the native 8,760-hour array.
- Preserve actual result even when mismatched: **no silent hourly relabeling or automatic 2020 EFS→UTC conversion**.
- Unit tests include *identical yearly energy but wrong hourly ordering*, shifted profiles, one-hour corruption and incomplete source coverage.

New [hourly cross-release verification workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs2020-reeds2022-hourly-crosscheck.yml), code `src/energy_transition/efs2020_reeds2022_hourly_crosscheck.py`, regression `tests/test_efs2020_reeds2022_hourly_crosscheck.py`, output `efs2020_vs_reeds2022_hourly_33_state_year_comparison.csv` and provenance JSON in the artifact `original-efs2020-vs-reeds2022-33-state-year-hourly-equivalence`.

## Interpretation guardrail

- A match in all 289,080 source-hour numeric values would justify a conclusion of **empirical sequence correspondence between these specific published files and source scenarios at the reported precision**. It would be an important independent clock-identity *lead*, more informative than agreeing annual totals.
- **Even a perfect numerical match does not by itself prove that the original EFS 2020 author meant its `LocalHourID` as physically UTC, CST, a particular year, or hour-ending**; that convention still needs a source-specific authoritative document or direct publisher evidence.
- Neither matching source values nor matching 2022 HDF5 timestamps admits EFS zoning to generator buses, weather-derived wind/solar potential, geographical transfers, or real Western network OPF. The existing 2020 EFS→LAF 20-zone pipeline and 540 mathematical storage LP results remain unmodified.

**Status:** source workflow submitted; numerical conclusions require the actual CI output.
