# Project B — evidence and validation status (2026-10-30)

This checklist separates implementation, reported research observations, and empirical validation. **A committed test or workflow is not evidence that the workflow passed.**

| Research component | Evidence status | Remaining acceptance criterion |
|---|---|---|
| Illustrative 2025–2040 portfolio figures | Synthetic, documented | Never describe as measured or optimized transition outcomes |
| EIA-930 2024 hourly BA demand | Data ingestion and completeness checks implemented | Retain source, timestamp, BA coverage and QC artifacts |
| EIA-860 operating nameplate by BA/technology | Mapping and qualification checks implemented | Verify source vintage, unmatched/unsupported technology shares |
| PyPSA annual generation comparison | 288 month-hour snapshots weighted to 8,784 calendar hours in leap year 2024 | Successful end-to-end official-data workflow with preserved metrics, logs and provenance |
| Full-year battery scenarios | Separate chronological 2024 scenario runs reported | Preserve 31-hour renewable gap-fill sensitivity labels and cost assumptions |
| EIA-923 observed vs modeled dispatch | Comparison and evidence-qualified deviation metrics implemented | Inspect successful official download, normalized coverage, BA matching, and model dispatch artifacts |
| BPAT wind accounting | EIA-923 vs EIA-930 difference approximately 1.981 TWh remains unresolved | Quantify plant-level unmatched generation, BA reassignment and accounting-boundary explanations without forced reconciliation |
| Manuscript-ready validation | Not established | Reproducible annual figures, verified CI, explicit limitations, independent checks |

## Gates before calling Project B empirically validated

1. Record a passing GitHub Actions run URL and commit SHA for `.github/workflows/eia923-validate.yml`, plus retained input SHA256 manifests and version metadata.
2. Confirm the EIA-923 normalized coverage report and selected-BA plant mapping; national plant-ID matching alone is **not** proof of selected-BA completeness.
3. Confirm annual model metadata states `288_weighted_month_hour_snapshots_not_chronological_hourly` with the correct year, 288 snapshots and 8,784 represented hours for 2024.
4. Report observed-versus-modeled annual dispatch deviations as **diagnostics**, not calibrated historical predictions.
5. Treat the 31 missing renewable hours with disclosed scenario assumptions, and keep the chronological storage study distinct from the representative-hour annual dispatch comparison.
6. Report the BPAT discrepancy as unresolved until a quantitative source-by-source reconciliation supports a narrower conclusion.

**Progress interpretation:** approximately 90% is an informal *implementation* estimate, not a validation pass rate or publication-readiness score.
