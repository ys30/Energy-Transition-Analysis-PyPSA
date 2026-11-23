# Paper S — successful official 15-year 8760h source-only mechanism aggregate: QA and manuscript freeze

**Official verified recovery:** [run 44861775851](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44861775851), conclusion **success**; single `aggregate-recovery` job succeeded including original-artifact retrieval, frozen original LP source retrieval, 15-year fail-closed counts, test suite, two figure renderings and final upload.

**Official final artifact:** `paper-s-annual-full-15year-120-source-mechanism`, ID **14692567952**, 526,224 compressed bytes; eight verified contents:
- `Y0_verified_full_year_manifest.json`
- `Y1_all15_annual_mechanism_cases.csv` (120 rows × 37 columns)
- `Y2_all15_paired_mechanism.csv` (60 rows × 7 columns)
- `Y3_all15_four_state_mechanism.csv` (4 rows × 13 columns)
- `paper_s_annual_input_only_mechanism_heatmap.{png,pdf}`
- `paper_s_annual_input_only_vs_lp_scatter.{png,pdf}`

This official zip was downloaded independently and contents re-read after success, including the manifest; the verified flags include `ALL15_SOURCE_ANNUAL_MECHANISM_ARTIFACT_CHECK_PASS`, 120 cases, 60 matched year pairs, 15 source years, 8760 source hours, daily-weekly-annual fixed-duration feasibility nesting, and no observed-profit claim.

## Source-population gate
15 original ReEDS weather years (2007–2013, 2016–2023) × 4 states × 2 county weights = **120** complete year-length input-only cases, covering three SOC boundary conditions (24h, 168h with final 24h, 8760h zero terminal), and two battery energy durations each: **720 optimized linear programs**. Each state's prescribed renewable ratio was held fixed (AZ 1.5, CO 2.0, ID 1.5, WY 1.5) and installed wind share at 50%; not the complete 3×3 renewable design. Equality residual maximum = **7.275957614×10⁻¹² MWh**.

## Final matched yearly differences (original frozen LP vs physical transfer)

| State | Daily SOC Pearson r | Weekly SOC Pearson r | Annual SOC Pearson r | Daily sign | Weekly sign | Annual sign | Median LP weight contrast (USD/added kWh-year) |
|---|---:|---:|---:|---:|---:|---:|---:|
| AZ (R1.5) | +0.019414 | +0.958747 | +1.000000 | 9/15 | 13/15 | 15/15 | -0.340861 |
| CO (R2) | +0.388377 | +0.954618 | +1.000000 | 14/15 | 15/15 | 15/15 | -2.177855 |
| ID (R1.5) | +0.143886 | +0.963586 | +1.000000 | 15/15 | 15/15 | 15/15 | +2.337690 |
| WY (R1.5) | +0.826549 | +0.952937 | +1.000000 | 15/15 | 15/15 | 15/15 | +2.636534 |

Annual sign 60/60; weekly sign 58/60; daily sign 53/60. This is a paired *modeled siting-effect* comparison, not state-by-state real profits.

## Numerically audited affine proportionality

| State | coefficient USD/added kWh-year per input-only delivered MWh | near-zero intercept | max absolute 15-year residual USD/added kWh-year |
|---|---:|---:|---:|
| AZ | 4.351684845975e-6 | -1.427e-11 | 6.076e-10 |
| CO | 7.372485109489e-6 | -1.410e-11 | 6.453e-11 |
| ID | 1.622683406681e-5 | -1.214e-9 | 1.200e-9 |
| WY | 2.751529633314e-5 | -1.058e-10 | 4.238e-10 |

The exact near-linearity arises from **structural objective equivalence** between the input-only energy-delivery optimum and original fixed-marginal-cost economic LP under these shared modeled constraints. It is NOT independent evidence, external validation, observational causality, weather-prediction skill or actual operating profit. Different SOC cycle constraints lead to nontrivial within-model timing sensitivity; no universal price-independent economic conclusion is warranted.

## Manuscript release decision
- **ACCEPT** annual source case and fixed-duration SOC comparisons as numerical model-method consistency/sensitivity results.
- **REJECT** wording implying 60/60, r=1, or the annual input-only model independently validates the economic LP mechanism.
- **ACCEPT** previously verified 1,080 economic dispatch 4-to-8h comparisons and 19,440 conditional ATB screen rows, 213/1080 lowest-cost threshold exceedances. Do not mix those with the narrower 120 annual source-only cases.
- **PENDING** integrated English main-text and SI document version reconciliation, journal-specific references/format, and independent empirical validation.
- **NO RERUN** of 720 physical LPs: reuse the official artifact for tables and figures. The original first all-15 run 44849783992 failed *only after all 12 calculation partitions passed*, due to duplicate pre-joined frozen LP column; the separate recovery fixed that postprocessing issue.

**Source and figure authority:** GitHub Actions official artifact ID 14692567952 from successful recovery run 44861775851; not a local approximate replot. Source discussion insertions: `docs/PAPER_S_MANUSCRIPT_ANNUAL_SOC_MECHANISM_INSERTION_2026-11-20.md`.
