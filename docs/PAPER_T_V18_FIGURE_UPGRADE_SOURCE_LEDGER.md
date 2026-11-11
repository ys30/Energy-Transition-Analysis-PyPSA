# Paper T v18 — source-derived figure upgrades (10 Nov 2026)

Three figures were generated locally from previously passing GitHub Actions source artifacts, not from synthetic residuals.

- **Fig. 2b:** `T_S1_nonwrapping_33_state_year_lags.csv` from Actions run 42332230767 (artifact 13557423465), plots 33 state-year best / runner-up / zero-shift MAEs on log scale. Round-level ten-state best fit versus runner-up at tens to thousands MW; Idaho remains exceptional.
- **Fig. 2c:** `control_residual_histogram_bins.csv` from Actions run 42927236434 (artifact 13814063958). Bin counts for OR/AZ/CA (2030–2050 pooled) normalized by **their unequal bin widths** and compared against density 1 on [-0.5,0.5]. Counts outside ±0.5 MW are OR 99/26271 (0.38%), AZ 154/26274 (0.59%), CA 362/26271 (1.38%); residuals are *approximately* uniform but **not solely exact nearest-integer rounding**.
- **Fig. S4:** `T_S2_idaho_original_subsector_annual_energy.csv` (same source supplement) gives sector annual demand fractions for 2030–2050. `provenance.json` from Actions 42927236434 supplies 2030-first-half inverse fitted coefficients frozen for later evaluation: Commercial 0.7674493, Industrial 0.8957408, Residential 0.8460022, Transportation 0.8046173; matched frozen whole-state coefficient 0.8278387. These coefficients are **constant by construction**, not verified regional allocation fractions.

Idaho 2030/2040/2050 sector annual demand fraction (%) [C, I, R, T]:
- 2030: 33.342, 32.115, 32.956, 1.587
- 2040: 34.534, 31.941, 31.481, 2.045
- 2050: 37.243, 32.699, 27.921, 2.136

**Optional 25-point lag curve remains NOT RUN.** Archived original T_S1 has best, runner-up and zero-shift MAE, not the 25 values. It requires source-authenticated 8,760-length EFS/ReEDS arrays; do not interpolate or invent unobserved lag MAEs.

Supporting plots and source CSVs are provided to the author in the locally generated `Paper_T_v18_Figure_Upgrade_and_BA_Audit_Data.zip` package. Private Word manuscript has not yet been changed.

Idaho/Oregon BA source audit: [PAPER_T_V18_IDAHO_OREGON_BA_TIMEZONE_SOURCE_AUDIT.md](PAPER_T_V18_IDAHO_OREGON_BA_TIMEZONE_SOURCE_AUDIT.md).
