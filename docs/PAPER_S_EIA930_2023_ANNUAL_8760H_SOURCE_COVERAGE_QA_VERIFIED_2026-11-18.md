# Paper S — authenticated 2023 annual EIA-930 BA coverage and raw/adjusted anomaly audit

Date: **2026-11-18**. **Verified successful** original GitHub Actions source archives and exact 2023 BA–fuel hourly CSV:

- January–December workflow [#44246001519](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44246001519), artifact **14406998900**.
- July–December cross-check [#44245742205](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44245742205), artifact **14402563266**.
- 2023 first-half MD5 `1b4acef4e1ec596cf92e7658f9be64c7`, second-half MD5 `1de4e47693426671123bb08ec0d33995`, independently checked in CI against the publisher-mirrored original archives.

## Actual 2023 8,760-hour source coverage

Four EIA balancing authorities (PNM, PSCO, IPCO, WACM), separate observed **wind and solar net MW**. 8 × 8,760 = **70,080 possible BA–fuel–UTC hour records**; **69,952 actual source timestamps**, **128 absent UTC timestamp positions**, **241 present source timestamps with null reported MW**, hence **69,711 valid reported MW records**, **6,375 negative reported MW values** retained as reported. The 128 absent timestamps are **ALL on original 2023-01-01 and 2023-07-01 archive boundary dates**. These are archive/start-of-local-day conventions until independently reconciled, **not measured operating-outage claims**.

| BA | wind valid reported MW | solar valid reported MW | wind/solar coverage jointly |
|---|---:|---:|---:|
| PNM | 8744/8760 | 8743/8760 | 99.81% |
| PSCO | 8721/8760 | 8721/8760 | 99.55% |
| IPCO | 8743/8760 | 8743/8760 | 99.81% |
| WACM | 8648/8760 | 8648/8760 | 98.72% |

**Do not misclassify absent timestamp slots as null reported MW, or replace either with zeros.** The H2 independently archived cohort expected 4,416 UTC positions; observed source counts were 4,408 for most BA/fuel cells (PSCO 4,409), and the complete H2 null-reported total was **193**.

## Actual raw vs adjusted/source-spike findings

Source **reported MW** and source **adjusted MW** disagree in **125 observed records**: 95 PSCO solar and 30 PSCO wind. Other six BA–fuel cohorts have **zero non-null unequal reported/adjusted MW pairs**, though some have null reported data and/or adjusted/imputed values.

Two time-localized extreme raw source records:
1. **PSCO solar** at **2023-06-02 21:00 UTC**: raw reported **15,914 MW**, adjusted **1,327 MW** and imputed **1,327 MW**. Six neighboring reported-hour median **1,255 MW** (about 12.68× smaller). A raw/adjusted disagreement and a clear source QC exception. The value is not silently replaced; corrected/adjusted variants may be considered with explicit labeling.
2. **WACM wind** at **2023-06-21 22:00 UTC**: raw reported and adjusted **7,194 MW**; six neighboring raw-hour median **823 MW** (about 8.74× smaller). This is a **source spike candidate** but NOT proved erroneous solely by local neighbors, and its adjusted field does not resolve the issue. Flag and retain source; do not clip or invent replacement.

The source-reported annual maximum PSCO solar 15,914 MW is therefore **not a valid unqualified summary** of a trustworthy physical BA observed maximum. The source adjusted maximum is 2,428 MW and cannot establish the true BA population or fleet capacity. WACM wind adjusted retains the 7,194 MW outlier.

## New independently regenerated QA outputs

Conversation-local **`Paper_S_2023_EIA930_Annual_Source_QA_2026-11-18.zip`** has:
- `Table_QA1_annual_8_BA_fuel_raw_adjusted_coverage.csv`: 8-BA-fuel aggregate QA.
- `Table_QA2_all_raw_adjusted_disagreements.csv`: all 125 raw-versus-adjusted source disagreements.
- `Table_QA3_all_missing_timestamp_boundary_groups.csv`: exact boundary-date absence patterns.
- `Table_QA4_two_extreme_source_hours_and_neighbors.csv`: two flagged source records and 6-neighbor comparisons.
- `Figure_QA1_monthly_reported_MW_coverage.png`, `Figure_QA2_reported_adjusted_spikes_13h.png`, `paper_s_2023_annual_QA_manifest.json`, `README.md`, `SHA256SUMS.txt`.
The ZIP is in the conversation download area, **not uploaded to GitHub**.

## Research gate and restrictions

Full-year observed **BA** source-year data acquisition/coverage is now done. However external ReEDS forecast skill has **not** been established because BA boundary and state source-footprint differ, 2023 EIA-930A candidate generator roster has documented 2023 July solar reported MW capacity exceedances, source instantaneous CF samples vs observed reported MW hour integration have different timing semantics, and the 2023 BA roster/mapping of cross-BA transfers remains incomplete. The earlier **160-hour same-weather BA/state proxy Pearson correlations** were exploratory; they cannot be relabeled annual externally verified skill.

Next steps: (1) flag/censor and separately report raw-versus-adjusted-QC exceptions using prespecified rules rather than model performance optimization, (2) independently reconcile archive boundary hour-ending semantics and missing records, (3) reconcile 2023 BA fleet accounting before geography-aligned model comparison, (4) consider full-year descriptive BA-based seasonality with explicit unresolved geography, **not** an observed 2023 state CF calibration.

The original fixed/historical 1,440 LPs, 2×2 360 new LPs, 3×3 2,880 new LPs, 2,160 ATB scenarios, and Paper C-2 were not modified.
