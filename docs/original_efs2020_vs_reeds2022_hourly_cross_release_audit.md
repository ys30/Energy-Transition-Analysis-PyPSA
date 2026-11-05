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

**Status: REAL-SOURCE HOURLY COMPARISON PASSED.** [Original full-hour Actions run #42119225537](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42119225537) compared all 289,080 pairs. [Follow-up numerical residual run #42119633401](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42119633401) added half-MW proximity, max residual and source-shift diagnostics. The **CI jobs succeeded**, but this does **not** mean the two releases have identical unshifted hourly chronology.

## Verified numerical source-hour findings

Both official source files deliver the **same rounded annual totals** (11 Western states: 774.400/855.707/980.023 TWh in 2030/2040/2050). However, **0 of 33** complete state-year hourly series match directly with 0.01 MW precision at the same unshifted native source ordinal.

A 25-shift numerical screen (integer shifts −12…+12 hours, applied to the **published ReEDS HDF5 hourly vector**) finds:

| Original 2020 EFS state | Best source-index shift (2022 ReEDS sequence) | After-shift mean absolute error (MW) | Above 1 MW residual hours |
|---|---:|---:|---:|
| AZ, CO, MT, NM, UT, WY | −2 h in all three years | approximately 0.25 | **0 per state-year** |
| CA, NV, OR, WA | −3 h in all three years | approximately 0.25 | **0 per state-year** |
| ID | −2 h in all three years | **17.266 / 19.306 / 22.102** in 2030 / 2040 / 2050 | **8,369 / 8,410 / 8,443** |

**Thus 30/33 complete state-year sequences are within 1 MW at every one of their 8,760 source hour keys after applying the individually best candidate shift.** No state-year has all 8,760 values within **0.01 MW**, and even non-Idaho states have a few values slightly over 0.5 MW (largest displayed 2050 CA error approximately 0.618 MW). Therefore this finding must be described as **sub-MW near-equivalence after shift**, not strict bitwise identity or proven pure rounding. Differences in published integer precision and/or upstream aggregation are possible explanations, not demonstrated causes.

**Idaho requires separate scrutiny:** its residuals after −2 h shifting are systematic (most hours exceed 1 MW), with extreme hourly deviations up to roughly **299 MW** by 2050, despite matching rounded annual demand totals. Its geographic split across physical time zones makes mixed-source chronology a *plausible hypothesis*, not a verified attribution. The [independently rerun 33-state-year source comparison #42120010571](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42120010571) additionally tested an **exploratory convex combination** of the same HDF5 state demand shifted by −2 h and −3 h. For Idaho, the fitted weight on the −2-hour shifted series was **0.83440, 0.83441 and 0.83441** (2030/2040/2050), and the fitted MAE fell from **17.266 → 6.445 MW**, **19.306 → 7.206 MW**, and **22.102 → 8.249 MW** respectively. **This did not resolve the discrepancy:** even the fitted mixtures retain **7,781, 7,884 and 7,998** hours with residual error >1 MW. The fitted weights must **never** be reported as actual Idaho timezone membership or demand allocation; they only show that source-series variation is consistent with, but cannot identify, mixed time-offset effects. Independent original regional/county-hour data and publisher metadata are needed to establish any physical cause.

**Clock admission remains blocked.** These observed differences strongly suggest that the candidate `LocalHourID`→ReEDS2022 datetime relationship is not identity by default, and candidate −2/−3 transformations require independent metadata checks. In particular, the HDF5's 2012 CST timestamps do **not** automatically certify that the original 2020 `LocalHourID` convention is physical UTC/CST, nor authenticate a weather-year synchronous wind/solar future-year dispatch. No replacement of EFS load, resampling, actual wind/solar resource join or network OPF has been performed.

