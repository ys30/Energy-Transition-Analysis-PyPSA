# Paper S — preliminary frozen-LP curtailment and storage-value mechanism diagnostic (2026-11-17)

**Source:** unchanged `paper_s_all15_720_lp.csv` from authenticated 720-LP fixed-2030-demand run; select trapezoid mode, 15 weather years × AZ/CO/ID/WY × two siting weight schemes × 0/4/8h = 360 previously frozen rows. Aggregated as 120 site-year duration triplets and 60 matched (EIA fleet minus ReEDS potential) siting contrasts. **No new LPs were solved for these results.**

For each weather/state/weight arm, define storage value as (objective_4h−objective_8h)/(1000×(energy_capacity_8h−energy_capacity_4h)), USD/(added kWh-year). Curtailment is solver-reported `unused_renewable_mwh`, not measured generation nor raw potential surplus. All median siting effects below are **medians of paired differences**, not differences between separately reported medians.

| State | Median siting effect on marginal 4→8h value, USD/(added kWh-year) | Median siting effect on 4h optimized curtailment, million MWh | Median siting effect on 8h optimized curtailment, million MWh |
|---|---:|---:|---:|
| AZ | -0.340861 | +2.820 | +3.054 |
| CO | +0.410384 | +0.922 | +0.833 |
| ID | +2.337690 | +0.582 | +0.400 |
| WY | +2.636534 | +0.318 | +0.218 |

In ID and WY, more 4h curtailment can coexist with higher marginal incremental duration value in the EIA spatial weighting. This is a **descriptive pattern**, not identification that curtailment *causes* the storage-value gain. Net-load deficit timing, chargeability and actual battery constraints require further inspection in the 2×2 factor study. The LP's objective is a linear combination of system flows, so correlations between objective differences and changes in firm generation are partly **algebraically induced** and should **not** be advanced as independent mechanism validation. Any almost-perfect correlation of such components with value is not a discovery.

**Source CSVs available as conversation output:** `120_arm_year_lp_curtailment_and_firm_descriptives.csv`, `60_paired_siting_mechanism_contrasts.csv`, `4_state_mechanism_descriptive_summary.csv`, plus figure. The new 360-case wind-only/PV-only factorial workflow [run 44037447284](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44037447284) had not passed or uploaded artifact at time of audit. These summaries cannot distinguish wind versus PV or support a completed attribution claim. No modifications to frozen CSVs or Paper C-2.
