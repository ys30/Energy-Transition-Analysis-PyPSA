# Verified 2030–2050 archived EFS Load-network snapshot semantics and 2040 leap-year defect

**Source-backed PyPSA NetCDF CI:** [run 41961836356](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41961836356).

The CI re-imported the **actual archived seven-state EFS load-only** PyPSA-USA networks from original Actions archive 41281576025, rather than extrapolating from code or synthetic snapshots.

## Exact verified stored timestamps

| Original source network year | Source stored first snapshot | Source stored last snapshot | Saved snapshots | Timezone aware? | Dynamic / static Load components | Verified archived annual Load |
| --- | --- | --- | ---: | --- | ---: | ---: |
| 2030 | `2030-01-01 00:00` | `2030-12-31 23:00` | 8,760 | **No** | 19 / 1 | 274.706987 TWh |
| **2040 (leap year)** | **`2040-01-01 00:00`** | **`2040-12-30 23:00`** | **8,760** | **No** | 19 / 1 | 306.839207 TWh |
| 2050 | `2050-01-01 00:00` | `2050-12-31 23:00` | 8,760 | **No** | 19 / 1 | 350.871475 TWh |

All three raw saved model indexes are naive, contiguous, increasing 8,760-hour pandas calendars and pass uniqueness and numerical source-load validation. **However, the 2040 index covers February 29 and omits December 31**, as a direct consequence of assigning 8,760 continuous hours from January 1 of a true leap year. Its month/day/hour order is therefore **not** the same as the original 2030/2050 nonleap model calendars. The actual 2040 monthly/seasonal snapshot labels are not immediately compatible with the official source's original 8,760 local ordinal-hour distribution.

**This is a confirmed archived model-calendar representation defect**, but its effect on an eventual 2040 chronological physical dispatch is not quantified because no simultaneous generator and weather profiles have been admitted. The 306.839 TWh total remains the actual sum of original model Load values, **not** corrected climate seasonality or source chronology.

## Prior pinned upstream timing context

[Verified pinned upstream time transformation](verified_pinned_efs_clock_compatibility.md) documents a fixed state clock offset (+7 AZ/CO/ID/MT/NM/UT/WY, +8 CA/NV/OR/WA) from original `LocalHourID` and a nonleap calendar template (2018), with later replacement of planning year. It **does not** independently certify NLR EFS source timezone, DST, leap-day policy, hour-ending convention, or simultaneous alignment with wind/solar/generator profiles.

The current saved model timestamps themselves are **naive** and have not passed a source-provenanced UTC time synchronization gate. Replacing the 2040 pandas index alone, or using `tz_localize('UTC')`, is **not a scientifically valid correction** without checking ordinal-hour meanings, source DST/calendar assumptions and correct hourly load-value order.

## Scope of model impact and safe remediation

1. Preserve original archived NetCDF as immutable historical artifacts.
2. Define a reviewed **nonleap representative-year snapshot contract** (e.g., explicit `source_hour_ordinal=1..8760` with independent nonleap reference-year month/day/hour keys) and source-specific UTC offset convention **only after authoritative source evidence**. Never silently reinterpret naive timestamps.
3. Build an **hour-identity mapping manifest** for source ordinal, planning-year label, leap-day treatment, DST, original source state and eventual UTC time. Gate any joined EFS + wind/solar/thermal hourly profile input on the same exact manifest identifiers and hours.
4. For 2040, retain `source_hour_ordinal` as a separate source key until the method specifies a leap-year strategy. A corrected nonleap representative calendar cannot be assumed from the current labels, which include February 29 and omit December 31.
5. Do not promote actual 2030–2050 Western OPF, seasonal peaks, emissions or reliability claims from archived load-only NetCDF until source data and electrical supply/POI provenance are independently validated.

## Reproduce

- `src/energy_transition/efs_actual_archived_snapshot_semantics.py`
- `tests/test_efs_actual_archived_snapshot_semantics.py`
- `.github/workflows/efs-actual-snapshot-semantics.yml`
- Real network CI and artifact: [41961836356](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41961836356), `efs-2030-2050-original-load-network-clock-semantics`.

**Scientific status:** source timestamp indices audited; **2040 leap-year representation flaw verified**; source EFS UTC/DST interpretation and synchronized generation profile alignment **not verified**. No original data was altered or false physical load shed was inferred.
