# EFS source-hour transform: mathematical bijection versus provenance admission

The verified pinned PyPSA-USA source revision `338af9912addbaf038c6098fe27e1e6ef099d8aa` applies fixed state offsets to ordinal `LocalHourID` values, wrapping at 8,760. The implementation is documented in [pinned source-clock audit](verified_pinned_efs_clock_compatibility.md).

This follow-up introduces deterministic tests of the **mathematical** 11-state mapping. It does **not** prove that the NLR EFS CSV uses UTC, a particular DST scheme or an hour-beginning/hour-ending definition.

```text
pinned_ordinal = ((LocalHourID + fixed_offset - 1) mod 8760) + 1
inverse_ordinal = ((pinned_ordinal - fixed_offset - 1) mod 8760) + 1
```

Seven states use +7 hours (AZ, CO, ID, MT, NM, UT, WY); four use +8 hours (CA, NV, OR, WA). Both transforms are tested across every ordinal 1…8760 for each fixed offset and the manifest reports every state's wrap boundary. Pinned output ordinals are **not certified physical UTC timestamps**.

The archived 2030/2040/2050 network index may have a distinct provenance from the **source** `LocalHourID`. The archive-sequence ordinal (row position in the NetCDF) is not automatically identical to original source-hour ordinal, especially after fixed-offset transformation and timezone-dependent sorting. No relationship is assumed without comparing actual source hourly demand to the resulting per-zone archived hourly load values and provenance transformations.

## Required source-to-archive equivalence test before UTC admission

1. Retrieve the exact archived hourly EFS input CSV and checksums from the network-building run, including original `LocalHourID`, state and scenario year.
2. Apply the **pinned** source transformation by state, retaining source ID and pinned ordinal as separate fields; audit duplicates, completeness, fixed year-end wrap and numerical load conservation.
3. Reproduce the staged zone load through the source-weight and bus placement stages with the exact pinned inputs; compare values and identify the archived row position corresponding to each pinned ordinal.
4. Separately establish timezone, DST, hour-ending and leap-day policy from **authoritative source documentation**. Validate the same UTC key in demand, generator and weather series.
5. Only then create a replacement model chronology with traceable source keys and rerun power-flow and optimization. Never relabel existing NetCDF silently.

## Current verified and unverified status

- **Verified:** 2040 archived 8,760 consecutive naive hours include Feb 29 but omit Dec 31, and 7,344 stored 2040 month/day/hour labels differ from the nonleap 2018 template by archive ordinal. Source-backed checks: [CI run 41965231298](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41965231298).
- **New code under CI:** `efs_pinned_ordinal_bijection.py`, `test_efs_pinned_ordinal_bijection.py`, and duplicate-ordinal regression tests. [Workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-actual-snapshot-semantics.yml).
- **Not verified:** equivalence of source `LocalHourID` to archived NetCDF row positions, cross-state physical simultaneity, and actual chronological Western OPF.

These boundaries keep exploratory temporal QA distinct from empirical energy-transition or reliability estimates.
