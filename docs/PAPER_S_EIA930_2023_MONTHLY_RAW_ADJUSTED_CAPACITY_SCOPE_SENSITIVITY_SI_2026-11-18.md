# Paper S — 2023 same-month EIA-860M candidate capacity scope: raw vs adjusted EIA-930 source sensitivity (2026-11-18)

**Status:** observed BA source-population diagnostic, **NOT** ReEDS external model validation, physical generator overproduction or measured BA capacity factor.

## Actual checked inputs

- Successful original 12-month EIA-860M × full-year EIA-930 scope reconciliation [run 44391834613](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44391834613), artifact **14472021718**: 96 BA×fuel×month candidate contemporaneous monthly OP nameplate cohorts, 192 source-reported/source-adjusted comparisons.
- Successful authenticated full-year 2023 EIA-930 BA observations [run 44246001519](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44246001519), artifact **14406998900**.

## Main new finding

Across all 96 month×BA×fuel cells, counting hours with source EIA-930 net reported or adjusted MW strictly **above the matching-month EIA-860M Operating-list candidate nameplate**, we obtained:

| BA / fuel | Reported exceeded-hours | Adjusted exceeded-hours | Difference |
|---|---:|---:|---:|
| IPCO solar | 14 | 14 | 0 |
| IPCO wind | 0 | 0 | 0 |
| PNM solar | 85 | 85 | 0 |
| PNM wind | 0 | 0 | 0 |
| PSCO solar | **696** | **695** | **1** |
| PSCO wind | 0 | 0 | 0 |
| WACM solar | 523 | 523 | 0 |
| WACM wind | 2 | 2 | 0 |
| **Total** | **1,320** | **1,319** | **1** |

All counts are **BA–fuel–hour flags** with each source month using its own official month’s candidate inventory; these are not 1,319 unique physical plants or proof of false telemetry.

**Exactly one hourly threshold classification changes:** 2023-06-02 21:00 UTC, PSCO solar **raw reported = 15,914 MW**, **source adjusted = 1,327 MW** (and source imputed = 1,327 MW), against June 2023 PSCO EIA-860M source candidate Operating nameplate **1,666.9 MW**. PSCO June source counts drop from 69 to 68 on using adjusted MW. All other month/BA/fuel threshold counts are unchanged. Thus eliminating the known large raw source exception cannot explain the persistent candidate population-accounting mismatch. WACM wind June 21 7,194 MW remains in adjusted source and is an unresolved separately flagged anomalous source value.

## Delivered reproducibility material

Conversation-local package `Paper_S_2023_Monthly_Raw_Adjusted_SI_Addendum_2026-11-18.zip` contains an English **one-page Word Supplementary Information addendum**, 96-row `Table_SI_R6`, 8-row `Table_SI_R7`, one-row `Table_SI_R8`, original data SHA-256 manifest, and deterministic `reproduce.py`. Local bundle is **not claimed to be a GitHub release**.

**Scientific admission boundary:** EIA-860M preliminary monthly Operating-listed BA-code generator subset is not independently established as complete EIA-930 BA-level hourly metered net-generation contributors; BA geographic boundary not a modeled state boundary. These flags are therefore a source-reporting/coverage *necessary-condition diagnostic*; they do not substantiate external ReEDS CF skill, economic value, or physical generator exceedance. Keep as supplementary data QA.

**Preservation:** Frozen 1,440 original LP, 360 new 2×2 LP, 2,880 new 3×3 LP, 2,160 ATB scenarios, prior 160-hour EIA proxy comparisons, and Paper C-2 unchanged.
