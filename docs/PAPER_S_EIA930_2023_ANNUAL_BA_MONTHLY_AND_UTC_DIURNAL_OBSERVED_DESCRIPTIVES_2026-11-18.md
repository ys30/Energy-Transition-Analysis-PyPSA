# Paper S — 2023 annual observed EIA-930 BA seasonality (2026-11-18)

## Source and scope
Actual source run https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44246001519, artifact **14406998900**, 69,952 original BA-fuel-hour records. This is BA-only descriptive data and NOT state-level ReEDS model validation, physical observed fleet CF, or hour-integrated MWh. The original H1/H2 archive MD5s were verified in the successful run.

## Newly calculated independent annual descriptions
- 192 monthly rows: 4 BAs × 2 fuels × 12 months × 2 source variants (reported vs adjusted); source count, valid count, median, mean, p95, max, negative counts.
- 384 UTC hour-ending diurnal rows: 4 BAs × 2 fuels × 24 UTC hours × 2 variants; median, quartiles, valid counts. UTC is not presumed to be BA local clock.
- All 125 raw-versus-adjusted source disagreements retained: PSCO solar 95, PSCO wind 30, zero in other six BA/fuel groups.

| BA | Fuel | source reported annual max MW | source adjusted max MW | reported median MW | adjusted median MW |
|---|---|---:|---:|---:|---:|
| IPCO | solar | 462 | 462 | 5 | 5 |
| IPCO | wind | 671 | 671 | 160 | 160 |
| PNM | solar | 636 | 636 | 8 | 8 |
| PNM | wind | 1795 | 1795 | 732.5 | 732.5 |
| PSCO | solar | 15914 | 2428 | 93 | 94 |
| PSCO | wind | 4440 | 4440 | 1558 | 1562 |
| WACM | solar | 334 | 334 | 4 | 4 |
| WACM | wind | 7194 | 7194 | 450 | 452 |

PSCO solar 15,914 MW extreme has source adjusted 1,327 MW at the specific anomalous hour; WACM wind 7,194 MW extreme remains unchanged in adjusted source and is not silently discarded. Existing annual audit identified 128 absent hourly slots and 241 source-present null reported MW; absent slots fall at archive boundary dates and cannot be asserted as true physical outages.

## Provenance and preservation
Conversation deliverable Paper_S_2023_EIA930_Annual_BA_Seasonality_2026-11-18.zip holds 4 analytical tables, four new plotted BA observation-only graphs, deterministic Python scripts and manifest. The full original hourly series is in verified Actions artifact 14406998900 and is not claimed to be newly uploaded to GitHub. A true BA generator membership and 2023 hourly boundary crosswalk is still required for external model-skill validation. Original LP, ATB, 2×2, 3×3 and Paper C-2 results remain unchanged.
