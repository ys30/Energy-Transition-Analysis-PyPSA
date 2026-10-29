# Verified 2024 EIA-923 → EIA-860 → PyPSA end-to-end pilot

**Verified GitHub Actions:** [run 40964541770](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/40964541770) (all three jobs succeeded: regression tests, official download/normalization, observed-versus-model). The results below are transcribed from its uploaded `eia923-vs-pypsa-2024` artifact, not forecasts or calibration coefficients.

## Study boundaries
Two balancing authorities, CISO (CAISO) and BPAT (Bonneville), calendar 2024. Generation is **aggregate across both BAs**, rather than per-BA estimates. EIA-923 plant-month net generation is mapped by same-year EIA-860 plant ID and primary fuel category to the supported carriers. PyPSA dispatch uses EIA-930 demand (representative hours) with assumed costs and availability.

## Real model scope

| EIA-860 nameplate, selected two BAs | MW |
| --- | ---: |
| Total originally mapped BA nameplate | 113,205.5 |
| Supported carrier nameplate modeled | 100,358.8 |
| Excluded non-modeled nameplate | 12,846.7 |
| Supported fraction | 88.65% |
| Of excluded, `MWH` battery/storage | 11,689.1 |

Exclusions are **not** zero physical capacity. Storage is not modeled with energy-state and efficiency constraints in this historical generator-only pilot. The separate model-scope audit retains every excluded fuel code and capacity. The 95% EIA-860 plant-to-BA mapping gate applies to **reported plant BA match**, not to technology-support coverage.

## Actual observed versus modeled aggregate annual generation

| Carrier | EIA-923 mapped observed (TWh) | PyPSA modeled (TWh) | Model minus observed (%) |
| --- | ---: | ---: | ---: |
| Coal | 3.092 | 5.468 | +76.8% |
| Natural gas | 80.984 | 45.034 | −44.4% |
| Geothermal | 7.901 | 16.068 | +103.4% |
| Hydro | 82.216 | 104.841 | +27.5% |
| Nuclear | 28.346 | 27.851 | −1.7% |
| Oil | 0.100 | 0 | −100% |
| Solar | 47.540 | 53.235 | +12.0% |
| Wind | 24.161 | 30.596 | +26.6% |

These are **descriptive differences, not model validation scores**: incomplete EIA-923 records and unmapped facilities remain, the BA boundary/reporting may differ, EIA-930 demand is not the same thing as EIA-923 net generation, and this dispatch model does not represent imports, storage operations or hourly chronological constraints.

The provenance reports national EIA-923-to-Western-EIA-860 plant-ID matched **absolute generation fraction of 17.83%**; this is **not a CAISO/BPAT coverage percentage**. A large national unmatched pool is expected with an 11-state EIA-860 source, and the BA completeness remains **unverified**.

Among mapped selected-BA observations, separate non-modeled fuels include biomass (+5.607 TWh), other (+0.029 TWh), storage (−1.152 TWh), and waste (+0.040 TWh); these are **excluded from comparable model carrier rows**, not assumed to be zero generation.

## What passed; what remains

- **Passed:** code regression tests, source download + SHA256 provenance, audited incomplete fuel/month exclusions, same-year plant BA crosswalk extraction, limited-carrier historical PyPSA solve, machine-readable observed/model carrier comparison and preserved audit artifacts.
- **Not yet verified:** all-fuel EIA-923 completeness of selected BAs, storage and net interchange modeling, chronological dispatch/adequacy, meteorological wind/solar inputs, true inter-year investment linkage, and external predictive validity.
- **Data-quality gating:** BPAT EIA-930 net interchange still fails the hourly energy-balance screening; do not use its published TI to fit a transmission line or invent imports.

This document is a reproducible **phase-1 pipeline milestone**, not a research-grade Western US decarbonization forecast.
