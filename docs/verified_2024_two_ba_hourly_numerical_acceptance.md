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

The CISO 24 missing observed hours have **not** been imputed. The acceptance workflow now exports the missing UTC timestamps into its JSON artifact, but the specific timestamps and causes have not yet been independently reviewed in this document. A calendar-year leap-year model still has 8,784 hours. Missing observed generation hours are distinct from model hours. The zero model balance residual follows from the simplified gas-plus-synthetic-unserved accounting identity; it is **not** proof of physical system fidelity.

The artifact checks covered checksum-verified modeled generation, observed generation, hourly balance and error summary for each BA. Upstream source revision, plant/technology supply completeness, BA interchange accounting, 2024 observed-vs-modeled discrepancies and BPAT renewable reconciliation remain separate empirical research concerns.

**Engineering closure boundary:** The narrow *independent gas-only hourly pilot* has successful computational and artifact-verification evidence. Project B as a physically calibrated, interconnected regional power-system research model has **not** reached full completion.
