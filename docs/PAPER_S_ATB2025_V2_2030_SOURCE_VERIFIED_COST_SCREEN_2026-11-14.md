# Paper S — Official ATB 2025 v2 2030 4→8-hour BESS expansion cost screening

**Source status:** Numerical entries transcribed with exact cell references from the successful official 2025 ATB **v2 (2026-11-11)** workbook source-cell inventory, GitHub Actions [43673367026](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43673367026), artifact 14146671653. Official workbook:
https://data.openei.org/files/8759/2025_v2_Workbook_11-11-2026.xlsx

**SHA256** `c3cece683ecbc943ac7170cbe668e4efdc5367731fe0bce83ee34bb359970b56`. Unit: **2023 USD**. Exact original values committed to `data/paper_s_atb2025_v2_2030_bess_4h_8h_source_cells.csv`.

ATB source sheets and cells: `'Utility-Scale Battery - Expand'` and `'Utility-Scale Battery - R&D'` with **2030 in column O**; overnight capital costs ($/kW) on rows **107–109 (4h), 113–115 (8h)**, and FOM ($/kW-year) on rows **124–126 (4h), 130–132 (8h)**. Rows within each duration are Advanced, Moderate, Conservative. The 2030 year markers are O103 for OCC and O120 for FOM. Do NOT substitute total CAPEX source rows 73–81 (includes other capital components): that would double count financing components against the direct overnight CAPEX basis.

**Power rating fixed** for 4h and 8h: each additional 1 kW × (8−4) h = 4 additional kWh. Incremental hurdle **$/(new kWh-year)**:

```
H = [(OCC_8 − OCC_4) * CRF(r,15) + (FOM_8 − FOM_4)] / 4
```

Assumed **15-year economic lifetime**, real discount rates **4, 7 and 10%** are *author scenario inputs*, not externally verified economics. No merchant-market revenues are inferred.

## Annualized cost per additional kWh (2023 USD/year)

| ATB source driver | Cost case | 4% | 7% | 10% |
| --- | --- | ---: | ---: | ---: |
| Expand | Advanced | 16.049 | 18.501 | 21.179 |
| Expand | Moderate | 24.175 | 27.869 | 31.902 |
| Expand | Conservative | 32.699 | 37.695 | 43.151 |
| R&D | Advanced | 16.049 | 18.501 | 21.179 |
| R&D | Moderate | 24.175 | 27.869 | 31.902 |
| R&D | Conservative | 29.715 | 34.255 | 39.213 |

## Cross-check to verified LP operating-value scenario distribution

The previously validated matched-historical 720-LP simulation includes 240 duration triplets (120 unique state-weather-weight cases per history-load treatment), GitHub Actions [43665299980](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43665299980). The annual-energy-rescaled historical mode is algebraically redundant in value per added kWh, so the cost comparison uses **only 120 unscaled-historical-load triplets**.

Maximum among 120 modeled 4→8h operating-cost savings: **15.1221 $/(added kWh-year)**. It is lower than the smallest of the 18 source-variant × cost-case × discount-rate annualized cost hurdles (**16.0492**). Therefore **0/120** modeled cases clear the annualized extension hurdle in each assumption, **conditional on the stated model and financial assumptions**. Do not interpret 18 × 120 = 2160 parameter comparisons as 2160 independent simulations.

**Very important caveat:** Cost inputs are explicitly in 2023 real dollars; the source LP's $90/MWh illustrative firm generation cost is *not independently calibrated to 2023 real prices*. Treat this as **illustrative screening, not a validated real-dollar investment cost-benefit model**. Additional unmodeled costs, BESS replacement and degradation, geography-independent copperplate constraints and weather-conditioned 2030 demand all remain limitations. No claim about profitability or comparative empirical realism of county weights. EIA930 external BA-measured hourly generation validation is still incomplete.

## Reproduction
- ATB original v2 source-cell CSV: `data/paper_s_atb2025_v2_2030_bess_4h_8h_source_cells.csv`
- Official cost screening script: `src/energy_transition/paper_s_atb2025_v2_verified_results.py`
- Workflow `.github/workflows/paper-s-atb2025-v2-verified-cost-screening.yml` pins the successful original 720-LP run and expects 18 annualized cost assumptions and 2160 scenario comparisons.
- **Admission condition:** Workflow completion and artifact audit. Results above independently calculated from verified original source-cell inventory and LP artifact; the new GitHub workflow may still be queued.

**Manuscript wording:**

> Under an illustrative 15-year battery life and real discount rates of 4–10%, official ATB 2025 v2 battery overnight-cost and FOM assumptions imply 2030 marginal 4-to-8-hour expansion hurdles of 16.05–43.15 2023 USD per added kWh-year across two cost-driver variants and three cost cases. The highest modeled increment in avoided variable operating cost across 120 weather-matched state–year–county-weight combinations is 15.12 per added kWh-year. No modeled case exceeds the corresponding cost hurdle under this screening exercise. This is not an empirical profitability finding because the model's avoided-cost price basis has not been independently calibrated to 2023-dollar economic data.

