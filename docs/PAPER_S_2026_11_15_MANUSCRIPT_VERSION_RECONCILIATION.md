# Paper S — integrated Word draft versus newer validated evidence: revision reconciliation

**Audit basis:** GitHub Actions `43682950922`, successful artifact `14150216413`: `Paper_S_Integrated_Review_Manuscript_2026-11-13.docx` (84 paragraphs, 1 Word table, 2 archived source figures). Inspected source paragraphs, not just workflow status. Newer record: independent frozen 720 fixed-2030-load and 720 historical-demand LP studies, ATB2025-v2 2,160 screens, EIA930 160-hour observed BA audits, EIA930A 2023 fleet geographic audit. **Do not overwrite the published prior-version manuscript or its figures.**

## Critical issue: prior document cannot be labeled the latest complete Paper S

| Issue | Exact content in existing 2026-11-13 Word | Required final revision | Priority |
|---|---|---|---|
| Abstract | Paragraph 4 says **96 original LPs; 192 paired hourly-conversion LPs**, 2010–13 four-year study; no 720+720 expansion | Decide and explicitly present main 15-weather-year scope without claiming four-year and 15-year results are interchangeable; retain 96/192 results as separately labeled robustness substudies | BLOCKER |
| Meteorological calendar | §§2.1 and 3.1 correctly identify native ReEDS `2007–2013, 2016–2023`, but main study uses only 2010–13 | Add provenance, per-weather-year scope and results for 15-year study; do not confuse source-record availability with experiments actually included | BLOCKER |
| Model identity | §2.3 correctly identifies **custom SciPy HiGHS copperplate LP, not PyPSA network OPF**; SOC empty-to-empty, 90% RTE, $5/$90 per MWh | Preserve this precise model description in final title/abstract/methods; do not relabel as a calibrated PyPSA dispatch study | LOCK |
| Hourly CF semantics | §§2.1, 2.3, 3.5, 4.4 correctly state point-to-hour conversion is numerical approximation; 2012 is the calendar reference | Retain source weather-vs-demand timestamp caveat and 2012 leap-year interpolation audit. Clarify differences between fixed-year and historical-matched demands | LOCK |
| Siting design | Main 2026-11-13 study reweights EIA **2025** operating county shares versus ReEDS potential | Explicitly describe an anachronistic controlled comparison using **2025 siting, 2030 projected demand, historical weather**; EIA930A **2023 BA** generator population is a different measurement and must not be merged into the 2025 county comparison | BLOCKER |
| Illustrative $10 threshold | Abstract/§3.5/§4.3 correctly note AZ 2012 screening crossing is **not** robust to endpoint-hold versus trapezoid | Stop foregrounding hypothetical $10 binary threshold as an empirical investment claim; substitute official ATB 2025 v2 **conditional** screens in primary economics, with 2023 USD/LP cost-unit alignment warning | BLOCKER |
| ATB 2025 v2 | Absent from old main abstract, results and economic discussion | Add factual 2030 Advanced/Moderate/Conservative x 4h→8h capex/O&M 15y annuity, 4/7/10% discount sensitivity; display 2,160/2,160 conditional negative screens with exact valuation limits; cite frozen successful run `43678422986` and source workbook digest | BLOCKER |
| Updated 15-year results | Not in the 2026-11-13 review text | Obtain frozen original 720+720 artifacts and compute final manuscript tables using **original CSV values** (not recollection or rounded earlier prose); contrast fixed-2030 vs historical-demand designs | BLOCKER |
| EIA-930 / EIA930A | Absent from earlier main manuscript | Add new observational source/scope audit **only as supplement** until 2023 co-temporal model output, BA dispatch assignment and verified 2023 hourly fleet permit direct metrics; see `PAPER_S_SUPPLEMENT_EIA930_EIA930A_OBSERVATION_SCOPE_DRAFT.md` | SUPPLEMENT |
| Figure package | Old package includes two 96-LP/weather-siting PNGs | Preserve these with accurate subexperiment captions; produce new 15-year/weather-demand and ATB screening main plots from frozen outputs, with source run/artifact/provenance metadata | BLOCKER |
| Submission evidence | §Data and code availability says PR #2 Draft, and lists older specific workflows | Replace with pinned release snapshot and final input/result manifests; Draft PR #2 is not a stable source release and currently contains many experimental files | BLOCKER |

## Proposed final Results spine (new document version, not retroactive rewriting)

3.1 Source calendars, power units, spatial potential vs operating-county weights.
3.2 Fifteen-weather-year 720-case fixed 2030 load design: original paired duration values and weather dependence.
3.3 Fifteen-weather-year 720-case matched historical demand design: same paired contrasts, differences from fixed load, per-state distributions and uncertainty interpreted as **scenario spread**, not inferential CI.
3.4 Siting weight comparison (2025 EIA860 vs ReEDS original potential), with cross-weather-year robustness; separately label 2010–13 96-LP and hour-method 192-LP tests.
3.5 Official 2025 ATB v2 **2030** 4h→8h annualized incremental cost screen, 2,160 conditional pairings; display units and discount/lifetime assumptions and caution against true investment inference.
3.6 Optional concise note on 2023 EIA930 external BA-source representativeness; full EIA930/930A audit in supplement, **no ReEDS RMSE**.
4. Discussion: source clock/calendar; geography and endogenous siting; model simplifications and cross-year mixes; cost-year and sensitivity; prospective observational validation.
5. Conclusions: avoid system-wide renewable adequacy, forecast skill, actual battery profit, future climate impact claims.

## Immediate reproducibility gate for the new Word build

1. Use **actual frozen** 720+720 and 2,160 outputs to generate tables and figure annotations, including run IDs, SHA256 and currency units.
2. Validate the exact numerator and denominator of the marginal 4→8h value, state/fuel, spatial weight and weather-year pairs. Avoid conflating the LP's incremental variable-cost savings with an observed revenue stream.
3. Make manuscript build fail if the output title/abstract claims a full 15-year/ATB result but tables or provenance still derive only from 96/192-LP artifacts.
4. Retain old Word version as a reproducible historical snapshot; save the revised manuscript under a new submission-review filename after a full Word render/visual check.
5. Continue keeping PR #2 Draft until a compact release snapshot has completed independent checks.

**Submission decision:** Core-paper route A remains the correct default; the EIA930 source audit is novel supplementary evidence, not a gate for fabricated same-hour model validation. This document is a version-reconciliation audit, not a claim that the complete new manuscript has already been built.
