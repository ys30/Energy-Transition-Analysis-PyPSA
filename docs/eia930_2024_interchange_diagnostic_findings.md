# EIA-930 2024 BA interchange diagnostics — verified findings

Source: GitHub Actions [run 40943712858](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/40943712858), artifact `eia930-ba-interchange-balance-2024`, files `interchange_ba_diagnostics.csv`, `interchange_monthly_diagnostics.csv`, `interchange_calibration_gate.json`.

## Method
All values are from common hourly records with valid EIA-930 demand (`D`), net generation (`NG`) and total interchange (`TI`). Official diagnostic residual: `D - NG + TI`, expressed in MW at each hourly observation and summed in MWh for energy. Positive `TI` means net exports; negative means net imports. Do not equate annual unaligned source sums with common-hour balance.

## Verified 2024 results

| Metric | BPAT | CISO |
| --- | ---: | ---: |
| Complete hourly triples | 8,783 | 8,472 |
| Positive-residual share | 100.00% | 59.57% |
| Median residual (MW) | +4,122 | +214 |
| Sum of common-hour residual (MWh) | +36,044,878 | +1,165,067 |
| 95th percentile of absolute residual (MW) | 5,463 | 2,158 |
| Correlation of TI with NG minus D | 0.8808 | 0.9342 |

All 12 BPAT months have strictly positive hourly residuals on all complete hours. Monthly BPAT median residuals range from +2,832.5 MW (May) to +4,642.5 MW (July); monthly residual-energy fraction of load ranges from +47.4% to +72.3%. This persistent one-sided discrepancy is a **reporting-definition or data-quality investigation target, not an inferred missing interconnection or a justified adjustment to physical capacity**.

## Decision
Both BAs fail the conservative interchange-calibration screening gate: BPAT fails persistent energy balance; CISO fails common-hour coverage in several months. **Do not estimate annual net imports or transfer capability from these series** for planning scenarios. Retain raw observations, full-hour missingness and error terms.

## Next verification
Investigate BA reporting boundaries, alternate EIA-930 interchange series and generation definitions with primary EIA documentation; compare BPAT reporting to independently published Bonneville data before any correction. The diagnosis alone does not establish a cause.

## Revalidated calibration gate (2026-10-30)

Fresh [successful observed BA interchange audit #41163962193](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41163962193), after mixed-year and physically bounded quality guards:

| Gate metric | BPAT | CISO |
|---|---:|---:|
| Annual complete triple share | 99.9886% | 96.4481% |
| Official balance MAE / load | 61.0318% | 3.2742% |
| Months below 99% coverage | 0 | 5 |
| Months above 10% residual threshold | 12 | 0 |
| Interchange calibration eligibility | **FAIL** | **FAIL** |

These are empirical screening decisions on observed official EIA-930 data, **not CI failures**. BPAT fails balance residual quality despite excellent temporal coverage; CISO fails temporal coverage despite a relatively low mean residual. Neither data stream qualifies to calibrate real line ratings or historical net imports. A successful audit workflow means the gate executed correctly, not that the underlying observations passed it.

## Verified machine-readable calibration blocker artifact

The [observed-data workflow #41166102963](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41166102963) successfully produced `interchange_calibration_blockers.json` alongside its original 2024 EIA-930 audit files. Its generated records independently confirm these **screening failures**:

- **BPAT:** `screening_passed=false`, `physical_calibration_verified=false`, blocker `official_balance_residual`. Compare the definitions of reported demand, generation and signed total interchange against independent BA operational publications.
- **CISO:** `screening_passed=false`, `physical_calibration_verified=false`, blocker `temporal_coverage`. Trace absent or nonmatching UTC D/NG/TI triple observations by field; do not zero-fill missing data.

The corresponding regression tests passed [CI #41166110708](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41166110708). A completed GitHub Actions run means the diagnostic was generated successfully; it is not a pass for real-grid calibration.
