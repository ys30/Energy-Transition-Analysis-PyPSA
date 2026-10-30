# Project B: 2024 chronological hourly pilot engineering handoff

## Acceptance scope

This handoff closes the **2024 CISO/BPAT independent gas-only hourly engineering baseline**, not the overall Energy Transition Analysis research project. Each BA is modeled with 8,784 chronological demand hours, assumed gas dispatch and synthetic unserved-load accounting. No physical Line/Link interchange or empirically calibrated generator mix is claimed.

## Verified source and execution evidence

| Evidence | URL | Verified |
|---|---|---|
| CISO full-year solve | https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41135401304 | Passed |
| BPAT full-year solve | https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41135401291 | Passed |
| Shared-source numerical acceptance | https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41145410855 | Passed |
| README CI | https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41145661693 | Passed |
| Reproduction-guide CI | https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41145651571 | Passed |

The paired CISO/BPAT pilots ran using the **same tested source commit** `c9dbc8216fe4b7a7293a0be6dbd7bd84f0db19e0`. Later documentation commits have their own CI results, but the underlying 8,784-hour numerical solve was **not rerun at every documentation revision**.

## Quantitative acceptance

| Metric | CISO | BPAT |
|---|---:|---:|
| Modeled hours | 8,784 | 8,784 |
| Observed NG paired hours | 8,760 | 8,784 |
| MAE (MW) | 4190.5191 | 2463.9455 |
| RMSE (MW) | 4807.9769 | 2783.5603 |
| Maximum simplified demand-balance residual (MW) | 0 | 0 |

The observed CISO NG gap is the continuous UTC interval 2024-11-02 08:00 through 2024-11-03 07:00 inclusive. Its cause has **not** been established. This data was neither filled nor silently discarded from coverage reporting.

See [verified numeric report](verified_2024_two_ba_hourly_numerical_acceptance.md) and [local reproduction guide](reproduce_2024_two_ba_hourly_baseline.md).

## Acceptance declaration and exclusions

**Engineering acceptance: PASS for the narrow independent gas-only hourly pilot, as evidenced by the linked runs.** This means the computational workflow, full-year modeled coverage, source-limited observed comparison, hourly conservation check, artifact integrity, and handoff documentation are in place.

**Not delivered by this acceptance:** calibrated CISO/BPAT historical production, actual BA transmission/interchange constraints, EIA-923 generator-fuel matching reconciliation, BPAT wind accounting resolution, empirical storage cost savings, capacity expansion, or 2025–2040 investment/transition projections. These remain project-wide research and model-engineering work, not silently considered complete.

## Research continuation priorities

1. **Observed CISO NG gap:** Compare EIA-930 source API timestamps and timezone semantics around 2024-11-02 08:00 through 2024-11-03 08:00 UTC; retain source payload and request metadata before assigning a daylight-saving explanation. Keep the 24 missing hours excluded from observed-error statistics.
2. **BPAT generation reconciliation:** Trace EIA-923 plant-level annual wind generation against EIA-930 BA-hour totals, with plant-to-BA mapping and reporting-boundary differences explicitly audited. Do not treat unmatched plants as proof of the discrepancy's cause.
3. **Annual empirical gates:** Execute and preserve the EIA-860/EIA-923 annual validation with run ID, input vintage, BA coverage, artifact hashes and reproducible error tables. The successful hourly gas-only pilots do not satisfy this separate validation.
4. **Physical model extension:** Replace synthetic gas-only supply with defensible technology-specific capacities and availability, then introduce physical interconnection (PyPSA Line/Link as appropriate), storage chronology and calibrated constraints. Re-evaluate costs, shortages and emissions only after these steps.

**Next milestone:** A separately documented, source-audited annual validation and an evidence-backed reconciliation of the CISO missing block and BPAT wind difference. No claim of historical calibration or completed transition projections is authorized by the current engineering acceptance.

GitHub artifact retention is time-limited; no indefinite external archive is evidenced here.
