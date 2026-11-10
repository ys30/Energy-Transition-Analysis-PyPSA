# Paper S v6 — primary EFS license verified; physical source clock remains blocked (10 Nov 2026)

**Status: primary-source license recheck and manuscript editorial correction.** This report is suitable for public repository use. The privately revised Paper S v6 Word manuscript is not committed here.

## What is now positively verified

The original 2020 *Electrification Futures Study Load Profiles* catalog page is https://data.nlr.gov/submissions/126, dataset DOI [10.7799/1593122](https://doi.org/10.7799/1593122), for the original `EFSLoadProfile_Reference_Moderate.zip` (not the later ReEDS 2022/2025 releases). The dataset's **View License** page is https://data.nlr.gov/node/126/license.

The directly published license text expressly grants a **no-fee right to use or copy the dataset**, subject to including the **entire notice in all copies of the Data** and crediting **DOE/NREL/Alliance in publications resulting from its use**. It also includes nonendorsement and disclaimer terms. This is an explicit official dataset license, not an assumed Creative Commons license.

Publication-specific consequences:
- Cite the original EFS dataset with DOI 10.7799/1593122 and credit the identified organizations as required.
- If making any **copies of the dataset** available, ensure the complete original publisher notice accompanies the copies. Do not misdescribe this license as generic CC-BY or public domain.
- Validate the treatment of any derived redistributed numerical files against the scope of the actual source terms and any separate contributions before creating an open deposit.
- The official source license is not permission to publish privately held coauthor manuscripts, independently copyrighted repository code, or separately licensed ReEDS datasets.

## What remains **unverified**

The catalog documents state/sector hourly source series for 2018, 2020, 2024, 2030, 2040 and 2050, but **does not certify the exact physical clock transformation of `LocalHourID`**: UTC versus local time, leap-day/DST treatment, hour-ending versus hour-beginning and synchronized hour meaning across states. Previous pinned project mappings show a mathematical fixed-offset ordinal reindexing, but **not** physical clock authentication. Weather-year provenance statements or a different ReEDS release's CST convention cannot fill this metadata gap.

The planning-year 2040 source and archived model label mismatch is separately documented: stored 8,760 naive Gregorian 2040 index positions can include February 29 and omit December 31. Do not treat this output-label pathology as proof that the EFS source inputs are physically synchronized.

**Current admission decisions:**
- Original EFS source-data use under posted license — **verified subject to its full stated conditions**.
- Release of a dataset copy without the complete notice — **not admitted**.
- Redistribution rights for distinct ReEDS 2022 files and independently licensed inputs — **not established by EFS license**.
- Physical EFS `LocalHourID` → UTC transformation — **BLOCKED** pending source-author evidence.
- Any cross-state real-weather-hour joining, source-derived reliability conclusions and empirically calibrated Western network OPF — **BLOCKED**.

## Proposed Data Availability wording (public-safe draft)

> The source demand profiles are from the Electrification Futures Study (EFS) Load Profiles dataset (Mai et al., 2020; DOI: 10.7799/1593122). The dataset's published terms allow use and copying without fee subject to retention of the full original notice on copies and publication credit to DOE, NREL and Alliance for Sustainable Energy. Source time is retained as an ordinal `LocalHourID`; its physical timezone, hour-ending and daylight-saving interpretation has not been independently certified in this study. The synthetic renewable profiles and hourly optimization results presented here do not represent an empirically synchronized weather–grid time series. Any dataset redistribution must retain the applicable source notice, and other data/code licensing terms must be checked independently.

## Verified reference points

- [Official EFS catalog and citation](https://data.nlr.gov/submissions/126)
- [Official EFS license text](https://data.nlr.gov/node/126/license)
- [Historical EFS temporal provenance gate](EFS_TEMPORAL_PROVENANCE_EVIDENCE.md)
- [Distinct ReEDS source-release warning](efs_vs_reeds_hourly_clock_source_admission_2026.md)
- [Pinned ordinal vs physical calendar distinction](efs_pinned_ordinal_bijection_and_calendar_admission.md)
- [Previous EFS/ReEDS licensing inquiry, still unsent](PAPER_T_REEDS_SOURCE_PERMISSION_AND_CLOCK_INQUIRY.md)

**Private manuscript editorial step:** v6 adds source-license and clock limitations within Methods, Discussion and Data Availability and includes a public-safe source-specific release decision log. This does **not** certify publication-ready source rights for other inputs or resolve the physical chronology question.