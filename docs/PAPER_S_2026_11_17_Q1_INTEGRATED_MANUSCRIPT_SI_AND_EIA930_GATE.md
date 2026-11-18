# Paper S — integrated Q1-style manuscript and SI review build (2026-11-17)

**Scope:** review package prepared for the user; this record pins factual content and source identities, not a GitHub upload of the binary DOCX or PDF. PR #2 remains Draft. Neither the original fixed/matched 1440 LP set nor the 2160 conditional ATB comparisons nor Paper C-2 has been modified.

## Manuscript changes

The conversation deliverables are:
- `Paper_S_Main_Manuscript_Integrated_Mechanism_3x3_2026-11-17.docx` (22-page rendered review draft, eight original-and-new numbered figures, 229-word abstract)
- `Paper_S_Supplementary_Integrated_Mechanism_3x3_2026-11-17.docx` (7-page rendered review supplement, source audit figures S1–S5, 4-state Shapley summary and full 36-cell design table)
- `Paper_S_Q1_Integrated_Manuscript_SI_Data_2026-11-17.zip` (main/SI Word and PDF, Figures 5–8, 2×2/3×3 model-generated results, exact ATB break-even table, 60 hour-method results, SHA256 manifest). **This ZIP resides in the conversation's download sandbox, not this GitHub repository; do not link to a fictional GitHub release.**

Amendments already incorporated:
1. Historical demand source `demand_historic.h5`, DOI 10.5281/zenodo.18462671, MD5 06ca6b65088a870afafc25191dcfd6f3, native fixed-CST 8760-hour calendar and Feb29/Dec31 original-support mapping.
2. Correct distinction between fixed-demand 720 LP (2 hour conventions) and weather-matched historical demand 720 LP (2 demand-level scales, trapezoid only); no fake crossed hour-mode replication.
3. Complete 15-year hour-method sign agreement **59/60**; max individual value difference **1.128274** USD/(added kWh-year).
4. Exact fixed-dispatch F/Q Table 4 cost numbers from the archived 2160 ATB hurdle cases (conditional dollar basis, not reoptimized real market return).
5. New §3.5 controlled 2×2 wind-only/PV-only siting intervention: 360 **new** optimal LP, 360 **frozen** reused; 60 state-year Shapley quartets (run 44037447284, artifact 14309243501).
6. New §3.6 renewable ratio × wind-share 3×3 sensitivity: 2880 **new** optimal LP, 360 **frozen** reused; 540 paired contrasts and 36 state-grid cells (run 44209543001, artifact 14388326204). Idaho and Wyoming positive at **9/9 sampled design-point medians**, but not for all years in every cell. Arizona and Colorado reverse direction in some designs.
7. Discussion/Conclusion and SI updated to avoid claims of causal mediation, real 2023 fleet accuracy or external model validation. No Paper S-specific Zenodo DOI exists yet.

## External observation gate newly launched

Experimental code `src/energy_transition/paper_s_eia930_2023_samework_weather_shape_proxy.py`, tests and `.github/workflows/paper-s-eia930-2023-sameweather-proxy.yml` establish an exploratory **2023 same-weather year, July 160 common UTC hours** comparison between modelled state 2023 wind/PV source profile **as a proxy** and EIA-930 BA wind/PV measured MW, for IPCO↔ID and PSCO↔CO; two county-weight alternatives and prescribed source-clock offsets −1/0/+1h, for 24 descriptive metric rows. Workflows must pass and archived CSVs be examined before numbers are reported; this is not a comparison of genuine 2023 operating-generator spatial weights, and BA boundaries are not equivalent to target states. The earlier 160h observed-source audit of 87 negative MW and CW1/150MW reporting overlap continues to apply.

**Outstanding before submission:** successful external observational comparison audit, full-year BA/asset mapping if stronger claims are wanted, code/reproducibility Zenodo DOI minted by user, bibliography verification, and journal-specific Q1 editorial/ethical formatting.
