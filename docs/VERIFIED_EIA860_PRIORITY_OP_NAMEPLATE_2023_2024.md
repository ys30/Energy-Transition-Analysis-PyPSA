# Verified OP-only nameplate capacity in prioritized EIA-860 plants

Verified workflow: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41481510731 (success). Main CI: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41481510723 (success).

| Metric | 2023 | 2024 |
|---|---:|---:|
| Priority plants reviewed (distinct IDs) | 84 | 84 |
| Generator records with status OP in the source Operable sheet | 114 | 112 |
| OP-only nameplate capacity (MW) | 5,593.7 | 5,843.1 |
| Real electrical bus crosswalk verified | 0 | 0 |

The difference of +249.4 MW (+4.46% relative to the 2023 subset) is a **comparison of distinct year-specific prioritized review subsets**, not a matched-plant annual capacity growth estimate, not all Western-region generation, and not realized dispatch.

The source is the official EIA-860 2023 and 2024 annual generator workbook. The program now checks nameplate MW for null/zero/negative values among OP records, and emits OP-only generator CSV. Planned (P), retired (RE), canceled (CN), and indefinitely postponed (IP) records must not enter the historical operating inventory. An OP record alone does not establish a physical tie to any PyPSA network bus. No empirical dispatch is authorized from this evidence.
