# Paper S — full July 2023 BA generator-footprint candidate capacity check (2026-11-18)

## Provenance and status

An independent, reproducible **entire July** observation-vs-generator-roster screen has been computed using already source-verified data:
- Official 2023 EIA-930 original observed **BA wind/solar reported and adjusted MW**, run [44246001519](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44246001519), artifact **14406998900**, full-year 2023 source series (MD5-authenticated H1/H2 archive).
- Original 2023 EIA-930A source-extracted `SCH 2` rows with commissioning year/month **no later than July 2023**; archive SHA256 `cf16b685460596c40de0ae11a96f541ffc128cddf4b411fe9d27f4dd61b7cd29`. These are **candidate, non-exhaustive installed nameplate** figures, not complete dynamic BA-hour power denominators.
- Annual source CSV local SHA256 `46ea3e5f9703b8a62189a9df3428f378c8a8d9e35665101952192b16f5b54c10`.

## Strict same-month July check

| BA | Fuel | eligible known-by-July SCH2 candidate nameplate MW | July reported BA peak MW | July reported hours above candidate MW |
|---|---|---:|---:|---:|
| IPCO | solar | 473.5 | 459 | 0 |
| IPCO | wind | 714.7 | 565 | 0 |
| PNM | solar | 544.0 | **580** | **12** |
| PNM | wind | 2569.0 | 1558 | 0 |
| PSCO | solar | 1666.9 | **1806** | **37** |
| PSCO | wind | 4492.3 | 3327 | 0 |
| WACM | solar | 161.9 | **286** | **275** |
| WACM | wind | 1131.6 | 913 | 0 |

**324 July BA–solar/hour candidate exceedance records total**. At those hours, the source `adjusted_mw` and `reported_mw` show the same candidate-exceedance counts; this is a reproducible **population/measurement-scope discrepancy** diagnostic, not proof of physically impossible per-generator output.

**First-week anchor reproduced exactly**: filtering the annual 2023 observation series to **2023-07-01 08:00Z through 2023-07-07 23:00Z** reproduces the original frozen first-week findings **PSCO solar 14** and **WACM solar 50**, **64** total; no change to the original 160-hour pilot. The additional **PNM 12** July exceedances occur outside the pilot and broaden the observation-coverage issue.

## Annual output: purposefully not an annual denominator

The 96 BA×fuel×month diagnostic rows retain each month's observed peak, valid raw/adjusted hours and observed values above a **fixed July roster**. Only the July rows are even **same-month candidate comparisons**. All eleven other months are separately and explicitly labeled **EXPLORATORY_FIXED_JULY_ROSTER_OUT_OF_MONTH**: the generator fleet changes during the year and no complete month-specific historic roster has been verified. Those out-of-month exceedances cannot be interpreted as capacity-factor violations, 2023 BA installed capacity or ReEDS simulation error.

## Limitations and reporting rule

A source-authenticated Operating July EIA-860M match validated 91 PSCO and 22 WACM identifiable solar generators (run 44242291685), but cannot cover the unidentified/undated WACM rows, competing generator BA schedules, uncounted solar projects, spatially overlapping regions, or BA dynamic net MW reporting. The EIA-930A candidate `SCH2` subset cannot be assumed the complete source accounting of every BA's wind/solar production. Solar thermal sources cannot be relabeled solar PV; negative source MW and missing values are not silently clipped or zero-filled. **BA ≠ state**, and these are not authenticated external state CFs.

## Reproduction deliverables

Conversation-local `Paper_S_2023_BA_July_Roster_Annual_Observation_Scope_QA_2026-11-18.zip` contains source-driven deterministic `audit.py`, `figures.py`, 96 monthly cohort table, 8 BA/fuel annual static-July-roster sensitivity table, all 6258 row-level two-variant candidate exceedance cases (July and exploratory non-July annotated), 8 July source candidate capacities, Figure V1 July/day solar exceedance tally, source SHA256 manifest and README. This is an actual local verified package **not a binary in GitHub**.

## Next science gate

Before any claim of observed 2023 BA capacity factor or ReEDS skill, establish complete contemporaneous 2023 *each-month* generator/BA participation, reconcile 2023 EIA-930A reporting and Schedule-4/dynamic dispatch scope, and align ReEDS county resource profiles to the observed generator footprint. The original Paper S 1440 LPs, 360 2×2 new LPs, 2880 3×3 new LPs, 2160 ATB cases and Paper C-2 stay frozen.
