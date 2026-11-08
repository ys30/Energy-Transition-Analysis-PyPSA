# Paper T scientific peer review v13.3 — novelty and appropriate method scope

**Status:** Private collaborator manuscript revised and full original-source figure bundle checked. **No new numerical experiment, public manuscript, data deposit, license or DOI.**

## Findings grounded in the archived source evidence

- Canonical 33-case lag table T_S1 confirms that in **all 30 non-Idaho year-state series**, after best nonwrapping source-index lag, **every overlapping hourly absolute residual is below 1 MW**. The best-lag MAEs are approximately **0.247–0.255 MW**, and maximum hourly absolute errors are approximately **0.50–0.62 MW**. The Idaho series remain distinct, with best-lag MAE **17.264, 19.304, 22.100 MW** across 2030, 2040 and 2050.
- The original independent-of-EFS NASA POWER known-transform check uses **89 common UTC anchors**, with naive same-label MAE **8.186629°C** and correctly publisher-mapped MAE **0°C**. The earlier 96-label naive MAE **7.787396°C** is a separate descriptive sample and must not be interpreted as the paired effect.
- Original EFS 2020 physical `LocalHourID` clock remains unverified, so **no physical-hour EFS weather/generation join is authorized**.

## Directly relevant prior art

1. [Yan, Zhang & Ma (2026), Energy and Buildings, DOI 10.1016/j.enbuild.2026.117044](https://doi.org/10.1016/j.enbuild.2026.117044) already identifies temporal deviations in measured building electricity data and develops a synchronization/correction method. Therefore **clock deviation detection or numerical re-alignment alone is not a novel methodological claim**.
2. [W3C PROV Data Model Constraints](https://www.w3.org/TR/prov-constraints/) explicitly recognizes time observations from different sources may come from different timelines. [PROV-O](https://www.w3.org/TR/prov-o/) and the [CF conventions](https://cfconventions.org/cf-conventions/cf-conventions.html) already cover important provenance and clock semantics.
3. [Energy Informatics founding editorial](https://doi.org/10.1186/s42162-018-0014-6) defines **Methodology** papers around new methods, tests or procedures. Topic fit does not establish novelty or editorial acceptance.

## Revised scope of the contribution

The defensible contribution is a **reproducible, source-linked forensic case study** and a machine-readable **abstention-oriented evidence screening record** for linking planning-model demand with external weather, renewable-resource or generation profiles. The six gates are **use-case-specific safeguards**, not six new standards, a universal specification for any temporal join, automatic source authentication or an estimator of the physical time difference.

In particular:
- For time-join tasks already anchored to validated absolute UTC observations, a shared **representative weather-year** condition may be irrelevant; do not present it as a universal necessity.
- A data join can validly be many-to-one after an explicit aggregation, so unique keys should refer to the declared **target join granularity**, not all original source rows.
- The code screens caller-provided evidence declarations only. Six self-declared true values return `READY_FOR_INDEPENDENT_SOURCE_REVIEW`, **never `ADMIT_PHYSICAL_JOIN`**.
- The present study has **not benchmarked** false-join rates, cost, detection performance or decision accuracy against an analyst using PROV, CF or Frictionless.

## Reviewer risk assessment

| Priority | Concern | Current disposition |
|---|---|---|
| **Major** | Methodology originality compared with known synchronization and provenance tools | Reframed and direct relevant prior art added; empirical benefit over baseline **still unproven** |
| **Major** | Only one related demand-release lineage and one within-product NASA control | Explicitly bounded; additional independently managed system example not performed |
| **Major** | Physical cause of Idaho differences | Remains unknown; no timezone or DST causal attribution |
| **Medium** | What does the six-gate policy actually verify? | Only schema and declared basis; independent evidentiary truth remains outside code |
| **Medium** | Broad or overrestrictive weather-year/key requirements | Narrowed to planning demand-resource joins; valid aggregation acknowledged |
| **Medium** | Reproducibility rights and persistent archive | Source artifacts and hashes verified; code license and derived-data DOI not resolved |

**Editorial recommendation:** Request coauthor review of whether the contribution is best framed as an *Energy Informatics* methodology, original research/data-quality case study or shorter technical report. It is **not scientifically defensible to claim a proven superior universal clock-validation method** at present. Avoid adding unrelated experiments simply to accumulate version numbers.

The full **private v13.3** manuscript and audited five-figure original-source review bundle are intentionally **not committed** to the public repository.
