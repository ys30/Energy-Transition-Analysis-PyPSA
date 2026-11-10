# Paper T — Idaho bidirectional reconstruction, residual structure and Oregon control (2026-11-10)

## Original-source run and status

- [Verified source-backed run #42923402459](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42923402459); code `src/energy_transition/paper_t_idaho_bidirectional_residual.py`, workflow `.github/workflows/paper-t-idaho-bidirectional-residual.yml`.
- EFS 2020 archival state-hour source is retrieved from verified run #41262154939. ReEDS 2022 independent HDF5 publisher MD5 `7b2055d43200744a16a8c4fed68b1a17` is verified.
- Each 2-shift comparison is **nonwrapping, 8757 hours**; the expanded four-shift comparison uses **8756 matched hours**. All current weights are **within-year diagnostics**, not the separately validated 2030-first-half-frozen weights (0.827385) from run #42921835974.
- Original EFS physical clock and geographic weights **remain unidentified**.

| Year | EFS <- ReEDS (-2/-3) w | EFS <- ReEDS MAE MW | ReEDS <- EFS (+2/+3) w | ReEDS <- EFS MAE MW | Oregon (-3) MAE MW | Oregon >1 MW hours |
|---|---:|---:|---:|---:|---:|---:|
| 2030 | 0.83442493 | 6.443099 | 0.83218092 | 6.818321 | 0.248501 | 0 |
| 2040 | 0.83443471 | 7.203540 | 0.83219326 | 7.621906 | 0.251139 | 0 |
| 2050 | 0.83444100 | 8.246547 | 0.83218615 | 8.721460 | 0.250801 | 0 |

## Residual geometry

- The signed EFS-minus-mixture residual is **not** unstructured rounding noise. Its correlation with the source-sequence first difference is approximately +0.180 in all three years. Source-ordinal hour 7 has signed means **+12.671 / +14.141 / +16.181 MW** and hour 23 has **−9.373 / −10.464 / −12.022 MW** for 2030/2040/2050.
- Labels are **source-ordinal hour modulo 24, not independently certified physical local clock hours**. The earlier T_S4 published HDF5 reference clock labeling uses a separate definition; do not equate two hour labels without accounting for the shift.
- In an expanded nonnegative convex `-1/-2/-3/-4` lag model, the weights on -1 and -4 are practically zero. Same-support MAE gain relative to the original two components is at floating point tolerance approximately 0 MW (three numerical differences about -1e-7 MW). This finding does **not** falsify heterogeneous end-use-specific transforms; sector-specific weights were not tested in the new run.

## Interpretation

- Full-year nonwrapping Idaho forward -2h coefficients span only **1.61e-5**, which is compatible with a fixed processing coefficient across planning years. It is not evidence that a measured Panhandle geographic share is invariant.
- Oregon is also geographically split between Pacific and Mountain civil time (Mountain for much of Malheur County), but is already within 1 MW at all original overlapping hours under a **single** -3h shift in all three planning years. Thus a geographically mixed civil-time state need not show Idaho's source-index mixture.
- The best inverse-index reconstruction changes the sign of source-index offsets and yields comparable but higher MAE. **Reconstruction orientation and upstream causality cannot be identified** from fitting alone.
- Numeric source-index correspondences do not authorize external physical weather joins. The Paper T six-gate screen remains fail-closed.

Data artifact: `paper-t-idaho-bidirectional-signed-residual-oregon`, including `idaho_bidirectional_residual_metrics.csv`, `idaho_signed_residual_by_source_hour.csv`, `idaho_bidirectional_provenance.json`.

**Private manuscript:** Paper T v14.1 updated separately; this public note is code/evidence documentation only and does not publish the private article.
