# Time alignment evidence and pending source-specific verification

## Verified repository evidence

Actions run [41325500944](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41325500944) completed successfully, and all three scenarios 2030/2040/2050 contain exactly 8760 LocalHourID ordinals. The generated gate records `utc_time_aligned=false` and `time_alignment_gate=BLOCKED`.

## Verified external source metadata

1. The primary [NLR EFS Load Profiles dataset](https://data.nlr.gov/submissions/126), DOI [10.7799/1593122](https://doi.org/10.7799/1593122), confirms state/sector hourly scenario data for 2018, 2020, 2024, 2030, 2040 and 2050, but its public catalog description does **not** establish that `LocalHourID` is UTC, local standard time, or daylight-saving-aware.
2. The independent [ReEDS Electricity demand profiles 2022 dataset](https://zenodo.org/records/18461543) describes its own profiles as using the **2012 weather year**, **Central Standard Time (UTC−06:00)** and a leap-day/calendar treatment giving 8760 hours. This is potentially useful provenance context, but it is **not evidence that the EFS LoadProfile_Reference_Moderate CSV uses the same clock convention**.
3. [NLR SAM electric-load documentation](https://samrepo.nlr.gov/help/electric_load.html) describes 8760 values without leap or DST, but this documents SAM rather than EFS and must not be transferred to the EFS format as a fact.

## Technical requirements before enabling combined Western hourly OPF

- Obtain authoritative documentation of EFS `LocalHourID` clock reference (date anchor, timezone, DST, leap year, whether all states have synchronized hourly indices), ideally source file documentation or written confirmation from the data authors.
- Inspect available source metadata and compare native EFS state sector rows to documented ReEDS input conventions; do not infer from the 8760 count alone.
- If a uniform source clock is established, build a source-clock-to-UTC mapping with explicit representative weather/calendar year. If state-specific clocks are established, require a geolocated crosswalk for split-timezone states; do not assign zones to timezones by state abbreviation.
- Assert total energy preservation, unique UTC snapshots, and representative-hour reproducibility. Keep annual profiles 8760 hours even for 2040 planning horizon until the source calendar convention is verified; do not silently attach a leap-year Gregorian index.
- Continue labeling currently available 2030/2040/2050 six-bus results as ordinal-hour exploratory optimization, not geographically synchronous Western dispatch.

**Current status:** temporal provenance remains unverified. No verified UTC-aligned EFS dataset has yet been produced.
