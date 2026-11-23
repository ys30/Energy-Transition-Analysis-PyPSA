# Paper S — Official July 2023 EIA-860M exact generator and capacity cross-check (2026-11-17)

## Source and execution evidence

The official July 2023 [EIA-860M monthly generator workbook](https://www.eia.gov/electricity/data/eia860m/archive/xls/july_generator2023.xlsx) was downloaded and source-audited with SHA256 `9a7b3f4051f1edb55f4d6508a1b963d2b344d687de6ea464ac538f2929122510`. GitHub Actions [#44242291685](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44242291685) succeeded with result artifact **14399717341**. The prior successful schema-only [#44228858746](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44228858746) had flagged two similarly named sheets; the fixed preflight selects **Operating** (not **Operating_PR**, the separate Puerto Rico worksheet).

**Source of candidate IDs:** previously verified EIA-930A official 2023 generator rows, excluding identifiers absent in both EIA and EIA-930A source columns. Generator ID matching uses exact `Plant ID` plus `Generator ID`; the monthly inventory is filtered to its actual July 2023 `Operating` source sheet.

## Verified match facts

| Source group | Rows with full generator IDs | Matched to official July 2023 Operating records | Unmatched | Matched official nameplate MW | Source list nameplate MW | Official source status |
|---|---:|---:|---:|---:|---:|---|
| PSCO solar | 99 | **91** | **8** | **1,666.9** | **1,666.9** | All 91 (OP) Operating |
| WACM solar | 22 | **22** | **0** | **161.9** | **161.9** | All 22 (OP) Operating |
| **Total** | **121** | **113** | **8** | **1,828.8** | **1,828.8** | All 113 (OP) Operating |

For **all 113 exact matches**, EIA-860M reports Solar Photovoltaic technology, source BA codes agree with EIA-930A, and source physical state is Colorado. Original nameplate MW agree **per generator**, not just in aggregate (maximum floating point difference approximately `9e-16` MW). The eight PSCO source rows not in July Operating are exactly the eight with known Aug–Dec 2023 commissioning dates, totaling 274.5 MW. Do not backdate these units.

**Critical unresolved limitations:** 15 other WACM undated solar records (~376.3 MW nominal) are excluded from the 121 identifiable rows because **both** candidate original/alternate plant+generator ID pairs are unavailable. This audit does not identify those units, and does not establish whether or when they were operating. A source-reported EIA-930 BA peak of **1,806 MW** for PSCO solar still exceeds the July Operating matched roster's **1,666.9 MW** by 139.1 MW, and the WACM solar BA peak of **277 MW** exceeds the **161.9 MW** identifiable roster by 115.1 MW. Thus validating generator identities and monthly inventory capacities does NOT authenticate the BA reported net generation denominator or its dynamic reporting footprint.

## Scientific acceptance boundaries

1. This audit confirms exact generator identities, contemporaneous *monthly* Operating-list membership and nameplate agreement for the **113 identifiable rows**; it cannot assert all actual BA-hour eligible generators were captured, or that static nameplate equals BA instantaneous/net generation reporting capacity.
2. EIA-930A's BA schedule and EIA-860M BA code agree for these 113, but observed source BA net MW may encompass dynamic transfers, additional reporting groups or other generators. **No valid observed capacity factor, model-skill RMSE or external validation claim** follows.
3. WACM's other 15 source rows remain explicitly blocked from key-based joins; later-month PSCO rows are not interpolated into July.
4. The 160h same-weather 2023 BA↔state proxy comparison remains exploratory. The fixed original 1440 LP, 360 2×2 new LP, 2880 3×3 new LP, 2160 ATB comparisons, and Paper C-2 remain frozen/unchanged.

## Reproducibility

- Code: `src/energy_transition/paper_s_eia860m_2023_07_source_identity_preflight.py`.
- GitHub Action artifact 14399717341: `eia860m_2023_07_PSCO_WACM_source_ID_join_candidates.csv` (121 candidates), `eia860m_2023_07_PSCO_WACM_exact_id_coverage.csv`, original schema header inspection, source SHA256 and manifest.
- Separately generated local audit bundle `Paper_S_2023_July_EIA860M_113_Exact_Generator_Matches_2026-11-17.zip` includes source-extracted 121 generator records, independent per-generator capacity assertions, table E13, eight unmatched PSCO rows E14, QA script, provenance manifest and hashes. It is delivered as a conversation artifact and is NOT claimed to be a GitHub binary release.

## Next gate

Trace BA net generation's reporting population and Schedule 4/BA dynamic transfers using official contemporaneous source records; inspect any 2023 monthly changes and whether 15 unknown WACM records represent row aggregations, without guessing physical IDs. Once scope is reconciled, attempt source-matched full-year EIA-930 assessment. Publish this audit in SI, not as a verified empirical capacity-factor fit.
