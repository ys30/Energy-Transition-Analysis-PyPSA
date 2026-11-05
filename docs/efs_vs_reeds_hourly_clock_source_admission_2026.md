# Source distinction: original EFS 2020 versus newer ReEDS hourly demand releases

## Why this matters for Project B

The project currently reconstructs **NLR Electrification Futures Study (EFS) Load Profiles**, published in 2020, for the Reference electrification / Moderate technology advancement scenario. Its original CSV uses a source `LocalHourID` of 1…8760 and the project has independently proven the EFS state-hour → archived LAF zone-hour → PyPSA NetCDF numeric chain. That is **not** the same thing as independently verifying its timezone, DST rule or physical weather chronology.

The [NLR original EFS load-profiles release](https://data.nlr.gov/submissions/126) describes the scenarios, source versions and projection years but does **not**, in its displayed catalog page, explicitly certify how `LocalHourID` maps to UTC.

There are newer **ReEDS electricity demand profile** releases, which are *different source families*:

- [ReEDS electricity demand profiles 2022](https://zenodo.org/records/18461543): its description explicitly states **U.S. Central Standard Time, UTC–06:00**, a 2012 weather year as its weather/calendar template, and a 8760-hour final-day omission convention. This is a description of the *2022 ReEDS* file, **not a valid metadata assertion for the original 2020 EFS ZIP**.
- [ReEDS electricity demand profiles 2025](https://zenodo.org/records/18435264): its publisher description similarly states **UTC−06:00**, multiple weather years 2007–2013 and 2016–2023, and a specific leap-year last-day treatment. This is a distinct input family and cannot be silently substituted for the original 2020 EFS data.

## Admission decision (unchanged)

| Field | Original EFS 2020 | ReEDS 2022 | ReEDS 2025 |
|---|---|---|---|
| Source release | Original EFS Load Profiles ZIP | ReEDS demand 2022 | ReEDS demand 2025 |
| Weather/calendar source | Requires original source-specific evidence | Publisher states 2012 weather year | Publisher describes 15 weather years |
| Time basis directly established by release | **Not independently certified from catalog evidence** | Publisher states Central Standard Time UTC−06:00 | Publisher states Central Standard Time UTC−06:00 |
| Can its timezone be applied to original EFS? | No inference permitted | **No** | **No** |
| Current Project B numeric source-backed EFS 540-case model | Yes, source demand only | Not used | Not used |
| Can be joined to real wind/solar simply by identical ordinal | **No** | No, not without compatible weather-year join and validation | No, not without compatible weather-year join and validation |

**No production data replacement or actual UTC conversion has been performed.** Original EFS source modeling is still an ordinal-only representative 8760-hour load screening. The nearest next physical input gate is to inspect the actual original EFS source documentation/headers and/or publisher response for hour semantics and weather-year identity, plus a model-year-to-weather-year join contract and explicit energy conservation verification.

## Reason for this distinction

Treating a newer ReEDS data release's explicit CST convention as authoritative metadata for a different vintage could create artificially synchronous demand and generation series. This would directly affect the manuscript's claims about renewable supply-demand coincidence, storage value and curtailment. Until source-specific evidence exists, all supply-shape and storage results remain **explicitly hypothetical**.

Last checked: November 5, 2026.
