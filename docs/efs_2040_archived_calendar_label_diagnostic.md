# EFS 2040 calendar-label mismatch: archive sequence versus nonleap template

This is an **audit-only diagnostic**, not a revised EFS source time-series, UTC conversion, or physically synchronized OPF.

## Exact comparison

The original archived seven-state EFS Load-only NetCDFs contain 8,760 contiguous naive stored hours for each of 2030, 2040 and 2050. In 2040 they begin on Jan 1 and end Dec 30, including Feb 29. The pinned PyPSA-USA upstream clock algorithm instead uses a **nonleap 2018 template** to convert ordinal source hours into month/day/hour labels (see [pinned clock audit](verified_pinned_efs_clock_compatibility.md)).

A newly added validator compares each stored calendar label with a nonleap 2018 ordinal-template month/day/hour key, without relabeling or changing demand:

| Archived year | Compared hours | Differing month/day/hour labels |
|---|---:|---:|
| 2030 | 8,760 | 0 |
| 2040 | 8,760 | **7,344** |
| 2050 | 8,760 | 0 |

These counts follow from the audited 8,760-hour date ranges and the explicitly tested ordinal comparison. For 2040, the first divergent ordinal is **1,417**, where the archived naive timestamp is **2040-02-29 00:00** but the 2018 nonleap template ordinal corresponds to **03-01 00**. All remaining 7,344 stored hour *labels* differ in month/day even though the original demand values are untouched.

**Interpretation and limits:** The disagreement is a representational calendar mismatch, **not** 7,344 missing source hours, megawatt-hours of lost load, or evidence of a real generator/load phase lag. The archive-sequence ordinal has **not** been independently verified to equal the original EFS LocalHourID, and no independent source-convention check proves UTC/DST semantics. The comparison does not authorize a direct timestamp replacement. Weather and generator hourly profiles remain unadmitted.

## Reproduction

- `src/energy_transition/efs_archive_sequence_manifest.py`
- `src/energy_transition/efs_archive_calendar_diagnostic.py`
- `tests/test_efs_archive_calendar_diagnostic.py`
- `.github/workflows/efs-actual-snapshot-semantics.yml`

CI: [latest dedicated archived-source workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-actual-snapshot-semantics.yml); check the run status before citing the 7,344-hour diagnostic as source-CI verified.

## Next admission requirements

1. Independently validate how source EFS LocalHourID relates to archived sequence ordinal and pinned state-offset transformations.
2. Document authoritative source timezone, DST policy, and hour-ending convention.
3. Select and validate an explicit source-supported 2040 nonleap representative-year policy, preserving source ordinal and original hourly demand.
4. Only then construct a shared UTC chronology and test load/wind/solar/generator exact-hour joins.
5. Keep physical Western OPF and seasonal claims blocked until generator POI, transmission impedances/ratings and empirical accounting also pass.
