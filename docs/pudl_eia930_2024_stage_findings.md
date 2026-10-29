# PUDL cross-check of EIA-930 BPAT/CISO accounting stages (2024)

Source: successful [GitHub Actions run 40945002335](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/40945002335), artifact `pudl-eia930-stage-comparison-2024`. Underlying table: Catalyst Cooperative PUDL public nightly `core_eia930__hourly_operations` Parquet. Figures below are calculated only on complete source-specific stage triplets using `D - NG + TI` (MWh per hourly period).

| BA | Stage | Complete hours | Residual (MWh) | Median hourly residual (MW) |
| --- | --- | ---: | ---: | ---: |
| BPAT | reported | 8,783 | 36,044,891 | 4,122 |
| BPAT | adjusted | 8,783 | 36,044,891 | 4,122 |
| BPAT | imputed_eia | 0 | unavailable | unavailable |
| CISO | reported | 6,552 | 650,647 | 179 |
| CISO | adjusted | 6,552 | 628,064 | 178 |
| CISO | imputed_eia | 0 | unavailable | unavailable |

## Interpretation

BPAT's +36.04 TWh accounting discrepancy is present in the **reported** PUDL dataset, and remains identical in the **adjusted** dataset. Thus it is not primarily introduced by this PUDL adjustment stage. This evidence **does not establish** which underlying physical or reporting process caused the discrepancy.

The CISO PUDL reported/adjusted triplet counts (6,552) are smaller than the separate EIA API pipeline's 8,472 complete-hour triplets. Those totals should **not** be compared without same-hour intersection, time convention checks, and field-definition reconciliation.

No complete imputed-EIA three-series hourly observations were present in this extracted subset. A zero from a sum over zero observations is **undefined, not an exact balance**. The code now outputs a missing value and a `no_complete_triplets` status.

## Research implications

1. Keep BPAT out of transmission-capacity calibration until source definitions and true exchange accounting are resolved.
2. Do not infer transfer capacity or net imports from `D - NG + TI` residual.
3. Prioritize stage-aligned, same-hour validation and independent Bonneville operational documentation before modifying the PyPSA network.
4. Retain all extracted and excluded observations and source provenance.
