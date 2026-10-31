## Verified BPAT wind end-to-end official data reconciliation (2026-10-30)

[GitHub Actions 41162114345](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41162114345) completed official 2024 EIA-923, EIA-860 and EIA-930 BPAT WND retrieval and reconciliation; [CI 41162114409](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41162114409) passed. EIA-923 BPAT-attributed wind = **8,820,435.41 MWh** across 28 plants; EIA-930 BPAT WND = **6,839,734.00 MWh** with 8,784/8,784 hourly observations; signed difference = **1,980,701.41 MWh**. See [verified numerical record](verified_bpat_wind_end_to_end_official_2024.md).

**Scope:** This validates a reproducible cross-source discrepancy, **not its cause**. The 993 unmatched wind plants and other-BA totals are broad national/unmatched diagnostics, **not BPAT-specific missing generation**. The wind gap cannot be reinterpreted as curtailment, interchange or transmission loss without further evidence. Official annual wind reconciliation execution is verified; physical-network calibration remains unverified.

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

## Verified BPAT wind plant-ID hypothesis test (2026-10-30)

[Official-source-derived plant-ID audit run 41161308306](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41161308306) examined 1,988 plant qualification rows and 1,650 unique IDs; it found **zero decimal-suffixed IDs and zero normalization collisions**. [Regression CI 41161308283](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41161308283) passed. Thus plant-ID decimal serialization **does not explain** the observed 1,980,701.41 MWh BPAT wind discrepancy in that archived source-qualified population. See [source audit](verified_2024_eia_plant_id_serialization.md).

This is **one eliminated hypothesis**, not an end-to-end EIA-923/EIA-930 wind reconciliation. The 1,988 rows are not 1,988 BPAT wind plants; the separately analyzed BPAT wind subset contains 28 matched plant records. Full wind-hour source coverage, BA reassignment, accounting boundaries and cross-source aggregation still require numerical acceptance.

## Verified CISO source-coverage resolution (2026-10-30)

The narrow CISO observed-NG gap is now **source-confirmed, not source-repaired**. [Official EIA-930 recheck run 41157405658](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41157405658) independently re-queried the 2024 EIA-930 CISO NG series and found **zero returned timestamps** in the 24-hour UTC interval 2024-11-02 08:00 through 2024-11-03 08:00 (end exclusive). [Enhanced recheck 41157449057](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41157449057) and [regression CI 41157458443](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41157458443) passed. This rules out an exclusively downstream join omission for that independently queried API series, **not** all upstream publication or timezone explanations. No imputation is authorized.

**Acceptance boundary:** close the question *whether these timestamps are returned by the current official EIA-930 NG API*; keep root cause, alternative EIA publication channels, and any historical-generation calibration unresolved. Do not claim that the 24 hours were recovered.

## Gates before calling Project B empirically validated

1. Record a passing GitHub Actions run URL and commit SHA for `.github/workflows/eia923-validate.yml`, plus retained input SHA256 manifests and version metadata.
2. Confirm the EIA-923 normalized coverage report and selected-BA plant mapping; national plant-ID matching alone is **not** proof of selected-BA completeness.
3. Confirm annual model metadata states `288_weighted_month_hour_snapshots_not_chronological_hourly` with the correct year, 288 snapshots and 8,784 represented hours for 2024.
4. Report observed-versus-modeled annual dispatch deviations as **diagnostics**, not calibrated historical predictions.
5. Treat the 31 missing renewable hours with disclosed scenario assumptions, and keep the chronological storage study distinct from the representative-hour annual dispatch comparison.
6. Report the BPAT discrepancy as unresolved until a quantitative source-by-source reconciliation supports a narrower conclusion.

**Progress interpretation:** approximately 90% is an informal *implementation* estimate, not a validation pass rate or publication-readiness score.

## Reproduce and inspect the official annual workflow

1. Open [EIA-923 annual validation Actions](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/eia923-validate.yml), select **Run workflow**, choose **2024**, and use the main branch. The EIA-930 demand downloader requires the repository secret `EIA_API_KEY`; absence of this secret is a configuration blocker, not an empirical result.
2. Confirm **all three jobs** succeed: `validate-code`, `official-download`, and `observed-versus-model`. A green unit-test job alone is insufficient.
3. Download both retained artifacts: `eia923-official-2024` (source/normalization audit) and `eia923-vs-pypsa-2024` (crosswalk, model output, comparison, environment and provenance). Artifacts currently have a 30-day retention policy; archive them for manuscript reproducibility.
4. Verify `outputs/eia923_validation/input_provenance_2024.json`, `environment.json`, `eia923_validation_manifest_2024.json`, and `eia923_vs_pypsa_2024.csv`; inspect the EIA-923 source audit for excluded numeric records and unknown fuels.
5. Report the Actions **run URL, run ID, commit SHA, completion date, job outcomes**, and a concise carrier-level comparison before changing the status of this study to empirical-validation-complete.

No successful run ID or artifact-level confirmation has been independently established in this status document.


## Chronological hourly pilot: separate validation track

The repository now contains an independent **full-year hourly demand/dispatch pilot** and an hourly BA generation export. This is a different temporal experiment from the 288 weighted month-hour annual model. A full-year hourly timestamp index does **not** by itself establish historical calibration: the pilot still has explicit supply and availability assumptions.

For an empirical hourly comparison, require a solved PyPSA NetCDF with genuine UTC hourly snapshots, matching BA identities and a separately audited EIA-930 generation series. Compare only aligned observed hours, report missing-hour coverage and the distribution of hourly residuals (not just annual totals), and inspect interchange/balancing residuals before interpreting discrepancies as model error. Do not infer hourly generation validation from the annual EIA-923 comparison.

**Acceptance status, updated 2026-10-30:** The assumption-driven 2024 CISO chronological pilot has **verified successful GitHub Actions execution**, including observed EIA-930 NG comparison, hourly gas-plus-unserved demand identity, artifact SHA-256 verification, and provenance output:
- [full-hour pilot run 41121054415](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41121054415), commit `2db5d78a`, success;
- [full-hour pilot run 41123841820](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41123841820), commit `bc59cc1c`, success;
- [CI run 41123841738](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41123841738), success.

Artifacts are published through successful workflow runs for a limited retention window (the current CISO/BPAT pilot workflows retain artifacts for 90 days; earlier runs may have shorter retention). The run writes `execution_manifest.json`, which records source/output SHA-256 hashes, versions and commit identity; its contents are re-checked by the workflow. **Numerical MAE/RMSE and paired-hour coverage are now documented in the verified two-BA acceptance report linked below.** The NG comparison is *descriptive only*, because independent BA gas-only supply with assumed capacity and costs omits the observed mix, interchange, storage and other system components. The separate 288 representative-hour model and its assumptions are unchanged.

### Engineering delivery criteria still outstanding

1. Preserve a durable snapshot of successful workflow artifacts beyond GitHub's 30-day retention period for long-term reproducibility.
2. **Completed for paired coverage and error metrics:** see the verified two-BA numerical acceptance report. Negative observed-hour statistics and source-vintage audit remain follow-up items.
3. Demonstrate repeatable CI for any subsequently added BA, year or realistic capacity/availability inputs before claiming general coverage.
4. Resolve or explicitly scope out the BPAT accounting discrepancy, source-alignment caveats, and all research-calibration assertions.

**Verified numerical evidence (2026-10-30):** [Two-BA acceptance run 41145034758](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41145034758) passed using common source commit `c9dbc8216fe4b7a7293a0be6dbd7bd84f0db19e0`. The full evidence table is in [verified_2024_two_ba_hourly_numerical_acceptance.md](verified_2024_two_ba_hourly_numerical_acceptance.md). CISO has 8,760/8,784 observed paired hours (24 missing), MAE 4,190.52 MW, RMSE 4,807.98 MW; BPAT has 8,784/8,784 paired hours, MAE 2,463.95 MW, RMSE 2,783.56 MW. Both report zero maximum simplified hourly accounting residual. These are *descriptive gas-only baseline errors*, not validated historical generation forecasts. The previously stated lack of transcribed numerical evidence is superseded by this linked report; the separate EIA-923 annual validation remains unverified.

**Engineering progress is an informal estimate rather than a binary 100% certification.** The CISO/BPAT independent hourly gas-only *pilot track* has verified same-revision numerical acceptance and a scoped engineering handoff, but a calibrated regional electric-grid model is not yet delivered. See [engineering handoff](project_b_hourly_pilot_engineering_handoff.md).
