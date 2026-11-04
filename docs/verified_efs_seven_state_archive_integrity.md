# Independent archive integrity validation — seven-state EFS pilot

**Successful CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41752091853

On 2026-11-03, the archived original EFS source from run **41265678862** and the existing real-network-derived pilot from run **41276635829** were independently audited, without rebuilding network geography or accepting unverified LAFs.

## Evidence

| Metric | Verified |
|---|---|
| Planning years | 2030, 2040, 2050 |
| Original EFS state scope | 11 states |
| Archived pilot allocation scope | 7 states |
| Source state-local-hour rows admitted for the pilot | 183,960 |
| Zonal output rows across the seven states and three years | 525,600 |
| State-year groups tested | 21 |
| Source/zonal local-hour keys | exactly matched |
| Duplicate source or state-hour-zone keys | rejected |
| Complete hour-by-zone coverage | checked |
| Constant state-year source-to-allocated arithmetic factor | checked |
| States in original EFS not admitted by pilot | CA, NV, OR, WA |
| UTC/DST/local-hour semantic reconciliation | **not verified** |
| Independent geographic source LAF acceptance | **not verified** |
| Complete Western EFS demand / actual OPF result | **not verified** |

The first workflow attempt #41751999680 failed because it incorrectly required the original 11-state source file to contain only seven states. The check was repaired to require *at least* the admitted seven original states while explicitly recording the four excluded states. Corrected run #41752091853 passed. No records or source LAF coefficients were fabricated or re-normalized.

## Remaining critical stages

1. Independently verify original LAF source geography and the full-state-versus-ReEDS demand-key transformations; null LAFs and partial-Western state footprints remain unresolved.
2. Reconcile the EFS `local_hour_id` calendar, daylight saving conventions and UTC snapshots before actual hourly network operations. The 183,960 state-hour records do not prove a validated chronological UTC sequence.
3. Apply validated generator availability, placement and costs to a defensible Western topology; the archived seven-state load-only network does not qualify as historical dispatch.
4. Resolve the four excluded states and any missing national-to-Western demand mass before generalizing projected Western-region energy outcomes.

**Scope:** this is reproducible source-to-output numerical integrity, not an empirically calibrated 35-zone Western energy-transition finding.

## LocalHourID strict ordinal gate (additional verification)

The independent EFS pilot audit now requires each of the **21** admitted state-year source series, and each individual state-year-zone output series, to contain exactly the integer ordinals `1..8760` without gaps, duplicates or offset IDs. It also checks that a state-year's zone inventory is stable. This is stronger than verifying only that the union of all source hours has 8760 entries; a single zone's missing hour must fail.

**This check is not a timezone conversion.** The [NLR EFS dataset catalog](https://data.nlr.gov/submissions/126) documents the Reference/Moderate scenario and years, but its overview alone does not establish the specific downloaded CSV's hour-begin/end convention, time-zone offset, weather-year reference calendar or DST treatment. A [related, distinct ReEDS demand-profile release](https://zenodo.org/records/18461543) describes 2012 weather-year chronology and fixed CST (UTC-06:00) for *that* ReEDS data product. The related release's time convention must not silently be transplanted to this archived EFS CSV without direct source/version verification.

Until verified from the *specific EFS input* and reconciled with generation/weather profiles and model snapshot semantics, `local_hour_id` remains an ordinal axis only. Strictly passing all 8760 integers does not establish simultaneous Western-grid UTC operation.
