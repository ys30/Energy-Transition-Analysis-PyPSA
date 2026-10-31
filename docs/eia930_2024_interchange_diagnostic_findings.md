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

## Verified UTC field-level missingness (2024)

In [successful official-data run #41166545686](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41166545686), the new `triple_missingness_by_month.csv` quantified missing D/NG/TI observations directly from aligned hourly data:

| BA | Missing D hours | Missing NG hours | Missing TI hours | Complete D/NG/TI triples |
|---|---:|---:|---:|---:|
| BPAT | 0 | 0 | 1 | 8,783 |
| CISO | 0 | 24 | 312 | 8,472 |

CISO's **312 missing TI hours** comprise January 72, March 96, May 72, June 24 and November 48. In November, 24 hours have both NG and TI missing and 24 hours have only TI missing. Accordingly, the 24 absent NG timestamps are a *subset* of the total 312 TI-missing timestamps, not an additional 24 hours to add to the incomplete-triple count. BPAT has one TI-only missing hour in March.

**Implication:** Diagnosing only the November 24-hour NG gap cannot restore CISO triple coverage: there remain 288 additional TI-only missing hours. Do not interpolate/zero-fill or infer line transfer capacities from these gaps. API field availability and reporting definitions remain under investigation.

## Verified contiguous UTC missing-data intervals

In [successful EIA-930 observed-data run #41168894844](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41168894844), the `missing_field_utc_windows.csv` artifact identified these intervals. End timestamps are **exclusive**; all are in UTC.

| BA | Missing field | UTC start | UTC end (exclusive) | Hours |
|---|---|---|---|---:|
| BPAT | TI | 2024-03-10 10:00 | 2024-03-10 11:00 | 1 |
| CISO | NG | 2024-11-02 08:00 | 2024-11-03 08:00 | 24 |
| CISO | TI | 2024-01-18 09:00 | 2024-01-21 09:00 | 72 |
| CISO | TI | 2024-03-11 08:00 | 2024-03-12 08:00 | 24 |
| CISO | TI | 2024-03-14 08:00 | 2024-03-17 08:00 | 72 |
| CISO | TI | 2024-05-17 08:00 | 2024-05-19 08:00 | 48 |
| CISO | TI | 2024-05-21 08:00 | 2024-05-22 08:00 | 24 |
| CISO | TI | 2024-06-03 08:00 | 2024-06-04 08:00 | 24 |
| CISO | TI | 2024-11-01 08:00 | 2024-11-03 08:00 | 48 |

CISO's **seven** TI outages sum to **312 hours**. Its 24 missing NG hours overlap the final TI interval, explaining **312 unique incomplete D/NG/TI hours**, not 336. BPAT has one TI-only incomplete hour. These are observed absence windows, not evidence of a DST cause or a zero-MW dispatch state. Independent historical BA operating records are needed before any replacement or calibration.

## Validated gap-window reconciliation (official 2024 data)

The [EIA-930 official workflow #41170615744](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41170615744) successfully executed the new hourly gap-window validator. It emitted `missing_window_validation.json` with `verified=true` and the following exact missing-field totals:

| BA | Demand D | Net generation NG | Total interchange TI |
|---|---:|---:|---:|
| BPAT | 0 | 0 | 1 |
| CISO | 0 | 24 | 312 |

This independently reconciles each generated contiguous missing interval back to the already aligned EIA-930 hourly observation table. It does **not** restore observations, certify EIA-930 source reporting correctness, or override the existing historical calibration failures. The code's unit tests passed [CI #41170622115](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41170622115).
