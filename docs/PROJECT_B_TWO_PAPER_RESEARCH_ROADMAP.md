# Project B research publication split — temporal provenance vs cyclic storage sensitivity

**Status: two distinct private manuscript drafts; engineering datasets, results and runnable validation remain public.**

Project B has two valuable but **scientifically distinct** contributions. The prior combined 2026-11-05 private working manuscript v10 is retained as a historical evidence ledger, **not** used as a submission manuscript. Two separate private, complete English drafts are maintained outside this public repository:

- **Paper T (temporal provenance and identifiability)** — *Annual Agreement, Hourly Disagreement: A Source-Forensic Audit of Published U.S. Electricity Demand Profiles*.
- **Paper S (source-bounded cyclic-storage sensitivity)** — *Why Hourly Supply Assumptions and Battery Boundary Conditions Matter: Reproducible Storage Sensitivity on Projected Western U.S. Demand*.

Do not confuse these paper letters with engineering **Project A** (multi-year PyPSA data pipeline), **Project B** (energy transition) and **Project C** (climate/grid resilience).

## Evidence and claims by publication track

| Research question | Paper T | Paper S |
|---|---|---|
| Original EFS2020 and separate ReEDS2022 numerical comparability | Primary: 11 states × 3 years × 8,760 hours = **289,080** source-value pairs | Short provenance warning only |
| Nonwrapping best source-index offsets | Primary: −2 h for AZ/CO/MT/NM/UT/WY, −3 h for CA/NV/OR/WA | Not a direct result |
| Idaho unresolved source anomaly | Primary: 17–22 MW MAE under best fixed shift; original sector/subsector recovery; evaluation-window sign reversal | Cite only as a reason to avoid uncertified source-clock joins |
| EFS-to-LAF 20-zone original projected demand | Supporting provenance | Primary: 7 states, 20 source zones, 3 projection years |
| Mathematical equal-annual-energy supply-shape experiment | Not used | Primary |
| Strict annual battery SOC and solved HiGHS LP | Not used | Primary: **540 full-year** LPs, all with zero terminal inventory |
| Real wind/solar availability, generator POIs, Western OPF | **Not claimed** | **Not claimed** |
| Manuscript content | Private | Private |

## Paper T: source-clock provenance / Idaho falsification

**Scientific finding:** published demand releases that agree in annual MWh can disagree in their raw hourly indices. Original full-hour comparison and nonwrapping robustness show source-index correspondence for 30/33 state-year series after shifts, but **do not establish physical UTC**. Idaho remains a persistent numerical exception. The pinned downstream PyPSA-USA assigns Idaho one `US/Mountain` timezone, with explicit multi-timezone limitation, but this does not prove the mismatch's cause.

Original Idaho source material was reconstructed from **367,920 rows**, yielding **14 Sector×Subsector** categories and four complete sector hourly traces. A previously selected Transportation +1 source-index-hour candidate gives the following changes in source-release discrepancy MAE, with positive numbers meaning lower error:

| Year | First-half difference (MW) | Later-half difference (MW) |
|---|---:|---:|
| 2030 | +0.073 | +2.210 |
| 2040 | **−0.757** | +2.013 |
| 2050 | **−0.988** | +2.227 |

The **evaluation-window sign reversals** in 2040 and 2050 show that a small numerical gain is **not a consistent clock correction**. No sector/subsector physical geographies were identified.

**Public evidence:**
- [289,080 pair source crosscheck](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42120010571)
- [Nonwrapping lag test](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42122065064)
- [Pinned upstream timezone source audit](pinned_upstream_efs_clock_idaho_source_forensics.md)
- [Original source Idaho residuals](efs_idaho_source_residual_seasonality_audit.md)
- [Idaho original subsector and frozen cross-year test](efs_idaho_subsector_frozen_crossyear_audit.md), [passing source experiment](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42131969905)

**Must finish before submission:** independently establish author/publisher source-time documentation and release relationship, source-specific Idaho upstream geography if available; produce final source-derived error heat map and state-lag panels; complete related-work comparisons and uncertainty assessment. If attribution remains unresolved, frame it as source identity/uncertainty rather than causal timezone correction.

## Paper S: demand-backed, synthetic resource and cyclic storage

**Scientific finding:** identical annual assumed renewable supply and EFS-projected demand can produce strongly different *model-generated* unused availability and backup requirements when **mathematical supply timing** changes. A full-year 20-zone 3-year × 3 shape × 3 duration grid yields **540** optimal HiGHS LPs. Every solve enforces zero initial and terminal battery SOC.

For *2030, synthetic wave A* across the 20 independent zones, the 0/4/8-hour cases have modeled unused availability of **25.893/9.466/2.626 TWh** and illustrative firm generation of **97.871/83.086/76.930 TWh**. Neither the supply shape nor the network/cost assumptions are empirical representations of the actual Western system.

**Public evidence:**
- [Full-year 540-case source-backed acceptance](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659)
- [Model and all-year results](efs_8760h_cyclic_storage_scaleup.md)
- [Verified publication figure assets](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42108416559)
- [Source chronology metadata and explicit refusal of unverified EFS/EIA-930 join](efs_eia930_cross_source_hourly_join_admission_2026.md)

**Must finish before a real-system energy-transition paper:** source-authenticated hourly renewable-availability data with weather-year/clock/spatial alignment, physically defensible wind/PV-to-generation conversion, verified generator-to-bus and transmission constraints, realistic battery economics, and uncertainty/scenario checks. These limitations currently prevent interpreting the 540 cases as a real decarbonization, curtailment or storage value forecast. As a **methods/sensitivity** article, narrower claims are possible but require journal-specific framing and literature.

## Engineering next steps — prioritized, not additional scenario proliferation

1. **Freeze accepted CI artifacts and parameter provenance** for both tracks. Publish machine-readable source hash, run ID, data scope and evidence/admission labels in technical docs.
2. Produce **only essential final figures:** source lag/error comparison and Idaho held-out-sign panels for Paper T; annual supply-shape and cyclic battery results for Paper S. Derive them from accepted artifact CSVs; annotate all physical-data caveats.
3. Resolve the original EFS 2020 timestamp meaning **at the publisher/source-code level**, or explicitly state unresolved. Do not use inferred −2/−3 shifts as a production weather join.
4. Acquire actual site/zone 2012 WTK/NSRDB resource data only after source product, timestamps, weather-year, geography and API terms are verifiable; a unit-tested parser is **not** a downloaded resource dataset.
5. Keep project engineering README recruiter-readable: main confirmed outcomes up front; deep-source investigations and both paper scopes in linked documentation rather than repetitive top-level sections.

## Admission boundary / data ethics

No full private manuscript draft is stored here. Public code/docs may discuss verified experiments and reproducibility, but must distinguish:
- **published projected demand data** vs **historical observed generation**;
- **mathematical synthetic available renewable profiles** vs **measured wind/PV resource**;
- **source-index numerical displacement** vs **certified physical time conversion**;
- **independent-zone optimization** vs **real Western Interconnection transmission-constrained OPF**.

This document is a research organization and evidence-status report, **not a claim that either manuscript is ready for submission**.
