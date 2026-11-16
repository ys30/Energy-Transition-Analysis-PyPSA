# Paper S: New 15-year Word reconstruction and frozen-data table register (2026-11-15)

**Status:** New integrated **review draft generated locally and visually rendered**, not committed as binary to GitHub, not a final journal submission, and not a new solver execution. The generated editable DOCX and review ZIP were supplied as conversation artifacts. **Do not claim they already exist in this GitHub repository.**

## Review draft

- File: `Paper_S_Integrated_15Year_Submission_Review_2026-11-15.docx`
- Local reproducible build: `build_paper_s_integrated.py` (conversation artifact working script; not yet pinned here as a repository build)
- DOCX SHA256: `eba9892d576c79e2e55d53a99f69fc795fca1a77315a95e7a20f390026128820`
- Word rendered and visually inspected as eight pages using the DOCX skill renderer.
- Three regenerated figures for frozen fixed-load and matched-load 15-year medians and ATB scenario hurdle range.
- Includes new Abstract, Introduction, Methods, Results, Discussion, Conclusions, provisional provenance register, editorial blockers.

## Frozen numerical evidence driving the document

| Evidence | Input source | Audited values |
| --- | --- | --- |
| Fixed 2030 demand | `Paper_S_15Year_720LP_Verified_Results.zip` / `paper_s_all15_720_lp.csv`, `paper_s_all15_240_duration_triplets.csv` | 720/720 LP optimal, 15 weather years, 4 states, 2 weights, 2 hour modes, durations 0/4/8 |
| Matched historical demand | `Paper_S_Nov14_Load_Weather_Comparison/full_720_lp_pairwise_crosswalk.csv` | 720/720 LP optimal; independent historical demand load treatment |
| Cross-load siting | `Paper_S_Nov14_Load_Weather_Comparison/60_weather_state_spatial_effects.csv` | 60 paired state-year siting contrasts |
| 2030 ATB v2 | GitHub Actions `43678422986` / artifact `14147890135` | 18 annualized cost hurdle definitions, 120 independent historical-load operating values, **2,160 comparisons, zero above annualized cost hurdle**, best operating value 15.122061 USD/added-kWh-year; 2023 USD ATB costs not independently currency-year-calibrated to illustrative LP savings |
| External observed source audit | EIA-930 run `43682969646`; EIA-930A run `43797969795` | BA observed net generation, 160-hour window, one 150 MW cross-BA generator CW1; **no** claimed ReEDS same-period accuracy metric |

Fixed-demand (trapezoid source-hour approximation) 15-weather-year **median marginal annual illustrative operating values**, source-potential versus EIA 2025 operating-fleet county weighting:

| State | Source potential | EIA 2025 |
| --- | ---: | ---: |
| AZ | 11.109 | 11.421 |
| CO | 5.778 | 6.113 |
| ID | 3.467 | 5.790 |
| WY | 3.505 | 6.186 |

All values USD/(added kWh-year), frozen model assumptions, not observed market revenue. Read exact machine decimals from CSV, not rounded summary.

## Known remaining submission blockers

1. **Not a finished journal manuscript:** complete reference list, full equation and parameter cross-check against pinned code, article-specific citation style and final journal format need author review.
2. Confirm all numeric figure and table entries against immutable final SHA-256 input list and final frozen release—not just a local file name.
3. Do not refer to the SciPy single-zone LP as PyPSA OPF.
4. Distinguish source weather years, 2030 projected load in fixed-load experiments, historical matched-load cases, and the 2025 EIA observed county siting counterfactual.
5. Official ATB cost data are in 2023 USD. Without independent calibration of illustrative LP $ units, the 2160 non-exceedance results are **conditional** only; the result is not profit or feasibility proof.
6. EIA-930/930A remains supplementary spatial/observational auditing; no source-mismatched 2012-vs-2023 MAE/RMSE.
7. Final reproducibility ZIP/Zenodo release and binary manuscript need to be published explicitly in a future separate action if authorized. Keep PR #2 Draft.

The previous `Paper_S_Integrated_Review_Manuscript_2026-11-13.docx` is a **historical narrower 96/192-case version**, retained as-is; this new draft is a separate reconstruction and did not overwrite it.
