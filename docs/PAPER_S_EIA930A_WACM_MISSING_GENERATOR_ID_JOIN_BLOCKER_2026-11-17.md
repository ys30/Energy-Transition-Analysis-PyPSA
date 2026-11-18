# Paper S — 2023 EIA-930A generator-identity admission gate (2026-11-17)

**Status: SOURCE-ID COMPLETENESS AUDIT ONLY.** This document corrects the potential overinterpretation of the preceding 376.3 MW WACM undated-solar sensitivity. It does NOT validate BA–state generation allocation, 2023 observed nameplate capacity factors, or a July 2023 operating roster.

## New finding from the retained source-derived 2023 EIA-930A Schedule 2 generator-row CSV

The previously verified official EIA-930A workbook (SHA-256 `ed8008bf4f5cbb0799d5a99b4dbc806e892eb150a9b357a709b582a93e28676f`) was source-extracted in archived `Paper_S_EIA930A_2023_BA_State_Candidate_Capacity_Audit.zip` (zip SHA-256 `cf16b685460596c40de0ae11a96f541ffc128cddf4b411fe9d27f4dd61b7cd29`). The new audit operates directly on the 136 PSCO/WACM solar rows from this **existing verified extraction**:

| BA | Original operation-month category | Rows | Candidate MW | Exact plant/generator ID join gate |
|---|---|---:|---:|---|
| PSCO | Known by 2023-07 | 91 | 1666.9 | 91/91 have complete identity |
| PSCO | Known after 2023-07 | 8 | 274.5 | 8/8 have complete identity; **exclude from July 2023** |
| WACM | Known by 2023-07 | 22 | 161.9 | 22/22 have complete identity |
| **WACM** | **Unknown / incomplete operation month and year** | **15** | **376.3** | **0/15 contain either complete EIA plant/generator ID pair or EIA930A alternate pair** |

The WACM 15 rows include **150 MW of candidate solar capacity listed in Wyoming**, but with neither EIA plant ID nor EIA-930A plant ID and neither generator ID. No keyed merge with monthly EIA-860M is possible for these 15 rows without **additional original identifying fields**. Joining on state+MW or guessed names would be an unaudited many-to-many linkage, not a verified generator crosswalk.

**Correction to prior status:** The 376.3 MW was not a verified list of July 2023 active units. It is an *undated, unidentifiable source-roster sensitivity*; adding it to the 161.9 MW candidate denominator until the 50 WACM solar output exceedances disappear would be circular and methodologically invalid. PSCO's 8 late-2023 units cannot be backdated to July. The PSCO 139.1 MW solar peak candidate shortfall (14 exceedance hours) still requires independent BA-scope/reported-generation reconciliation.

## Official monthly 2023 source identified — use within scope

[EIA Preliminary Monthly Electric Generator Inventory](https://www.eia.gov/electricity/data/eia860m/) supplies an official **July 2023** XLSX link (`https://www.eia.gov/electricity/data/eia860m/archive/xls/july_generator2023.xlsx`). It contains a *preliminary monthly operating-generator inventory*, not BA-hour net-generation reporting. The date-specific generator-list status can be read directly by plant and generator ID for the **113 PSCO/WACM solar rows with identifiers and plausible relevant operation dates** (91 PSCO plus 22 WACM), subject to verified worksheet schema and status. It cannot directly identify the 15 undated WACM records missing both key pairs. This original monthly XLSX has **not yet been downloaded and independently audited** by this work; do not claim a joined roster result.

## Reproducibility output

Conversation-local bundle `Paper_S_EIA930A_Generator_Identity_Gate_2026-11-17.zip` includes deterministic `audit.py`, source-record-level `Table_E10_SCH2_solar_identity_gate_rows.csv`, 4-row `Table_E11_join_eligibility_by_BA_date.csv`, and `Table_E12_15_WACM_undated_unidentified_generator_rows.csv`, manifest and SHA-256 file digests. The bundle is not a GitHub release. The earlier source file and LP, 2×2, 3×3, ATB, Paper C-2 work are untouched.

## Remaining requirements, priority order

1. Source-fetch official **July 2023 EIA-860M** and verify schema/date status for the identifiable 113 pre-July PSCO/WACM solar Schedule 2 rows. Never silently fill missing-generator identities.
2. Source-verify WACM's original 15 ID-less rows; investigate whether they represent distributed reporting, scheduled imports, a generator grouping or incomplete roster fields; require authoritative original identifiers before joining; no assignment by capacity/state guesses.
3. Inspect PSCO discrepancy between 1666.9 MW candidate nameplate and July observation peak 1806 MW, including source reporting/BA membership and scheduling rather than backdating future units.
4. Trace 2023 CW1 wind (plant 59975, 150 MW) dual PSCO/WACM Schedule 2 reporting before any full-year capacity normalization.
5. Only when an actual auditable BA-fleet crosswalk and hourly capacity denominator exist, assess external 2019–2023 model fit. The 160-hour proxy correlation remains explicitly exploratory.

**Manuscript-safe wording:** “Contemporaneous source screening revealed non-identifiable and temporally ambiguous WACM solar roster records, as well as PSCO solar output exceeding the eligible candidate nameplate. Consequently we report observed BA–state curve-shape comparisons as descriptive sensitivity tests only and do not claim authenticated BA-level capacity factors.”
