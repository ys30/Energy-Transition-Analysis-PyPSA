# Verified EIA-860 retired/canceled status reconciliation, 2023–2024

## CI provenance
- [Official EIA860 priority source-status workflow 41410682545](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41410682545): success, source original annual EIA-860 2023 and 2024 archives.
- [Main CI 41410682610](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41410682610): success.
- These figures describe **generator rows** in the `Retired and Canceled` sheet for priority plants missing from the Operable and Proposed sheets; they are not counts of distinct plants.

| Status code | 2023 generator rows | 2024 generator rows | EIA meaning |
|---|---:|---:|---|
| RE | 14 | 9 | Retired, no longer in service |
| CN | 5 | 5 | Planned generator canceled |
| IP | 1 | 2 | Planned generator indefinitely postponed or removed from resource plan |
| **Total** | **20** | **16** | Exclude from year-end OP supply |

References for code interpretation: [EPA eGRID generator code lookup](https://www.epa.gov/egrid/code-lookup), [PUDL EIA operational status metadata](https://docs.catalyst.coop/pudl/en/v2025.7.0/data_dictionaries/codes_and_labels.html), and the [2023 EIA-860 form instructions](https://catalystcoop-pudl.readthedocs.io/en/v2025.2.0/_downloads/b2b6a6507bb154840c8d8c443e259199/eia860_instructions_2023-05-31.pdf).

## Source-sheet completeness
Each priority review year contains **84 unique plant IDs**. The 2023 original workbook covers 65 plants on Operable, 8 on Proposed, and 11 on Retired and Canceled; the 2024 workbook covers 66, 9, and 9 respectively. No outstanding plant IDs after auditing all parseable generator sheets ([run 41409659722](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41409659722)). These are **plant-level sheet-presence** figures; a plant may own several generator records, and any eligible capacity must be determined on **generator-year status**, not merely the presence of a plant on the Operable sheet.

## Historical dispatch gate
1. Do not count `RE`, `CN`, `IP`, or `P` generators as year-end operating capacity.
2. Even for `OP` generator-year records, real source-network dispatch requires an independently verified electrical bus crosswalk; source-sheet status and owner metadata do not establish it.
3. Distinguish end-of-year operating inventory from generation during a calendar year. A unit retired during the year might have produced earlier that year: exclusion from year-end OP capacity does **not** prove annual generation was zero.
4. The original downloadable EIA-860 ZIP and year are recorded in workflow logs; for stronger reproducibility, pin upstream ZIP hashes or immutable releases in a subsequent data-provenance step.

**Electrical connections verified: zero. This audit does not authorize dispatch in the empirical PyPSA network.**
