# Paper S — submission evidence gate and final manuscript boundaries

Last evidence review: 2026-11-15. This checklist is deliberately conservative. No new LP scenarios are authorized by this note.

## Frozen outputs

- Original single-zone copperplate **SciPy HiGHS LP** results: two independent series of 720 optimal cases (fixed synthetic 2030 demand and historical-weather-matched observed demand). The solver is **not** PyPSA network OPF.
- Storage marginal operating-cost savings are conditional on source/model assumptions and do **not** represent plant revenue, market profit or bankable savings.
- Source-pinned 2025 ATB v2 cost screen, 2,160 combinations, is conditional; its LP savings and ATB cost inputs are not independently calibrated to one cost-year basis.
- Preserve pinned inputs, run identifiers and hashes in the existing archives. Do not overwrite frozen output artifacts.

## Empirical evidence and claim tier

| Source | Observed property | Permitted manuscript claim | Forbidden until independently proven |
| --- | --- | --- | --- |
| EIA-930 2023H2 actual raw archive, original 2023 July source observation artifact #14150700990 | BA-level wind/solar reported net MW, UTC hour-ending | External source quality; 160-hour shared BA timeline; negative-value sensitivity; BA-to-BA *descriptive* correlations | State observed capacity factors; wind-solar weather-model skill; BA-to-state equality |
| EIA-930A 2023 generator roster and SCH 2 | Reporting BA, generator ID, technology, state, candidate MW, reported operating date | Candidate BA-state nominal capacity scope and cross-state composition | Actual available capacity for July 1–7 2023 at each hour; claim of 100% BA reporting coverage |
| EIA-930A SCH 4 | Separate pseudo-tie/dynamic dispatch relationships | Footprint ambiguity requiring accounting sensitivity | Addition of SCH 4 MW to SCH 2 denominator; inference of energy transfer quantities |
| EIA 930A plant 59975 / unit CW1 | Same 150 MW wind unit appears in PSCO and WACM SCH 2 | Cross-BA duplicate assignment: 8907.6 MW row-sum vs 8757.6 MW unique-generator union (four-BA wind) | Assign all CW1 output to PSCO or WACM without an independent dispatch/settlement crosswalk |
| ReEDS physical/weather records | Existing source-proven ReEDS profiles | Source-specific modeled resource analysis after clock and unit validation | Same-hour MAE or RMSE versus EIA 930 without geography, capacity, year and quantity crosswalk |

**Critical temporal limitation:** The EIA-930 public archive has local-date/UTC boundary complications. 2023-07-01 08:00–2023-07-07 23:00 UTC is the conservative 160-hour common **UTC hour-ending** comparison window. Do not label the preceding 7–8 absent hours per BA/fuel as verified EIA measurement outages.

## Two independent submissions paths

**Route A — core paper without direct EIA-930 quantitative benchmark (default unless every gate below passes):**
Main claims rely on existing ReEDS source audit, source-proven weather scenario comparisons, 1440 frozen LP cases and conditional 2025 ATB cost screening. Include EIA-930/A as independent observation-source and representativeness audit in supplementary material. The 160-hour BA correlation is descriptive and cannot establish validated ReEDS forecast performance.

**Route B — direct EIA-to-model validation (conditional):**
Publish MAE, RMSE or hourly capacity factors **only after all**:
1. July 2023 actual-generator operation, generator capacities and reporting fleet verified from temporal sources.
2. Auditable BA-dispatch participation, explicit non-overlap accounting of plant 59975/CW1, SCH 4 treatment, and geographic support.
3. Genuine **2023** same-period ReEDS/weather model output for the same **wind or solar generation quantity**, identical UTC hour-end convention, technology definitions, and capacity basis. Do not substitute 2012 ReEDS wind/PV CF for July 2023 observations.
4. Explicit checks for negative net generation, source imputation and the source unit MW; define any net-MW-to-hourly-MWh conversion and stationarity assumptions.
5. Hold-out validation with fully documented mask, paired N, MAE, RMSE, bias, and uncertainty/representativeness discussion.

If any gate fails, stay on Route A; do **not** fabricate a metric.

## Final manuscript pre-submission blockers

- [ ] Reconcile manuscript claims against original frozen LP and source-pinned ATB summaries, including currency year and operating-cost-vs-capital-cost units.
- [ ] Finish two-sided account of evidence limitations, especially BA/state boundaries, duplicated EIA930A generator and source clock.
- [ ] Separate main results from exploratory EIA-930 descriptive source auditing; place source-cell provenance, id overlap and clipping diagnostics in supplementary material.
- [ ] Freeze a minimal submission snapshot/release (source, input manifest, result manifests, scripts and computational environment). Reduce PR #2 scope, not by rewriting prior work but by selecting the final reproducible subset.
- [ ] Audit references, figure IDs/captions, methods timing conventions, results/abstract consistency, journal style and author-only metadata.

## Immediate latest CI dependency

- The enhanced EIA930A cross-BA generator audit previously failed **only** because synthetic fixture lacked `original_excel_row`; correction committed at `e3953285`. Require an actual green run plus an artifact review before marking its extended duplicate-gate validated.
- Existing source extraction (#43795452473), 160-hour observed BA diagnostics (#43755967483) and EIA930A schema (#43755968031) passed previously.
- PR #2 remains Draft. **Do not merge before final release validation.**
