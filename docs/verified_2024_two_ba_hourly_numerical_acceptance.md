# Verified 2024 CISO/BPAT chronological hourly engineering acceptance

Verified GitHub Actions acceptance: [run 41145034758](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41145034758), succeeded on 2026-10-30. Matched source revision: `c9dbc8216fe4b7a7293a0be6dbd7bd84f0db19e0`.

This record reports **descriptive model mismatch**, not calibrated historical accuracy. The engineering baseline uses independent BA gas-only dispatch and assumed capacity and cost; the observed EIA-930 `NG` is total balancing-authority net generation.

| Indicator | CISO | BPAT |
|---|---:|---:|
| Underlying full-year run | [41135401304](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41135401304) | [41135401291](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41135401291) |
| Expected/model hours | 8,784 | 8,784 |
| Observed and paired hours | 8,760 | 8,784 |
| Missing observed hours | 24 | 0 |
| Paired fraction | 0.9972677595628415 | 1.0 |
| Mean absolute error (MW) | 4190.51906392694 | 2463.9454690346083 |
| Root mean squared error (MW) | 4807.976871171643 | 2783.560288777914 |
| Maximum hourly model energy-balance residual (MW) | 0.0 | 0.0 |
| Validated historical generation calibration | No | No |

The CISO 24 missing observed hours have **not** been imputed. Their exact UTC timestamps were subsequently verified in the investigation below; their underlying data-source cause remains unresolved. A calendar-year leap-year model still has 8,784 hours. Missing observed generation hours are distinct from model hours. The zero model balance residual follows from the simplified gas-plus-synthetic-unserved accounting identity; it is **not** proof of physical system fidelity.

The artifact checks covered checksum-verified modeled generation, observed generation, hourly balance and error summary for each BA. Upstream source revision, plant/technology supply completeness, BA interchange accounting, 2024 observed-vs-modeled discrepancies and BPAT renewable reconciliation remain separate empirical research concerns.

**Engineering closure boundary:** The narrow *independent gas-only hourly pilot* has successful computational and artifact-verification evidence. Project B as a physically calibrated, interconnected regional power-system research model has **not** reached full completion.


## Observed CISO NG missing-hour investigation (verified)

[Two-BA acceptance run 41145410855](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41145410855) independently reconstructed the exact missing UTC hours from the retained EIA-930 NG source artifact. All **24 missing CISO observations form a single continuous block**, from **2024-11-02 08:00 UTC through 2024-11-03 07:00 UTC inclusive** (end-exclusive boundary 2024-11-03 08:00 UTC). **BPAT has no missing NG hours** in this paired run. No missing records were interpolated or treated as zeros. This block overlaps the US daylight-saving transition weekend, but the cause is **not established** from the time correlation alone; data-source auditing is required before attributing it to timezone or EIA publication issues.

The observed NG comparison therefore covers **8,760 / 8,784 hours (99.7268%)** for CISO and **8,784 / 8,784 (100%)** for BPAT. Chronological model demand dispatch remains full-year in both BA baselines. The reported gas-only MAE/RMSE exclude unmatched CISO hours and are not calibrated-grid skill scores.
