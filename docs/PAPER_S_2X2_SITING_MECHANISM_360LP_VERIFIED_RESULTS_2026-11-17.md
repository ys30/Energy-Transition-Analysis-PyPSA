# Paper S — 2×2 wind/PV county siting attribution: 360 new LP verified (2026-11-17)

**ADMITTED new results:** GitHub Actions [run 44037447284](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44037447284) **completed successfully**, artifact **14309243501** (`paper-s-wind-pv-independent-siting-weight-360lp-shapley-interaction-results`). All 360 new wind-only/PV-only LPs were optimal; maximum balance residual **7.276e-12 MWh**. The 360 original potential–potential and joint EIA–EIA LP rows were read from the frozen fixed-2030-demand panel, not re-solved or modified. Four-arm factorial comprises 15 weather years × 4 states × 4 wind/PV weight combinations × 3 durations = 720 arm-duration cells; 60 complete state-year factorial quartets yield 4→8-hour marginal storage value at each arm. Source-hour model approximation: **trapezoid only**; fixed 2030 demand has the 2012 calendar.

## Paired 15-year attribution results

Each entry is the median **within-year** contrast in model USD per added kWh-year (each column's median need not add to another column's median). Wind and PV attribution use a symmetric 2-factor Shapley division; the interaction column is the unallocated 2×2 factorial interaction in the standard corner-based representation.

| State | Median total joint EIA − baseline | Wind Shapley | PV Shapley | Wind×PV interaction | Years wind Shapley >0 | Years PV Shapley >0 |
|---|---:|---:|---:|---:|---:|---:|
| AZ | -0.340861 | -0.5116 | +0.2586 | +0.0397 | 1/15 | 12/15 |
| CO | +0.410384 | +0.2267 | +0.2088 | -0.0377 | 10/15 | 15/15 |
| ID | +2.337690 | +1.2045 | +1.1217 | -0.1639 | **15/15** | **15/15** |
| WY | +2.636534 | +1.8799 | +0.7145 | +0.1372 | **15/15** | **15/15** |

Across all 60 quartet rows, numerical Shapley conservation max absolute error ~**1e-11** USD per added kWh-year (after exported decimal rounding). Thus, Idaho's large positive siting effect is supported by **both wind and PV county weighting**, while Wyoming's is **more wind-driven**. These are **model-conditional ablation effects**, not a proof that EIA weighting is more accurate or a real market return.

## Descriptive mechanism changes under joint EIA vs potential baseline

The table reports statewise median matched-year **joint-minus-baseline** values, using the four-arm `paper_s_siting_factorial_240_hourly_curve_descriptives.csv`:

| State | Δ combined wind/PV CF variance | Δ mean daily net-load range, MW | Δ net-load 24 h lag correlation | Years daily range Δ >0 |
|---|---:|---:|---:|---:|
| AZ | +0.00776 | +717.6 | -0.048 | 15/15 |
| CO | +0.00138 | +343.8 | -0.158 | 15/15 |
| ID | +0.00667 | +362.2 | -0.087 | 15/15 |
| WY | +0.00884 | +240.1 | -0.068 | 15/15 |

The fact that AZ also has increased variance/range **despite negative median value effect** shows why a single variability statistic is not a sufficient or causal explanation. The mechanism is sensitive to timing, surplus coincidence and optimal dispatch constraints, which must be discussed as conditional co-responses rather than independently identified statistical mediation.

## Manuscript admission / next results

**Main paper:** Results should distinguish the measured LP intervention effects from the separate descriptive time-series metrics; Discussion §4.1 may now state that wind/PV siting contributions are different across ID/WY, but must NOT claim physical verification of operating-fleet weight accuracy or climate attribution. Publish a 4-state Shapley chart and 15-year trajectory chart; detailed paired CSVs remain SI.

**Next gates:** nine-design-point peak renewable ratio × wind share sensitivity (2,880 new LP if 360 original model runs can be reused); independently BA-reconciled EIA-930 observational shape checks. Do not modify Paper C-2 or frozen 1440 LP/2160 ATB analyses.

**Actual outputs:** artifact ZIP contains `paper_s_siting_factorial_360_NEW_lp.csv`, `paper_s_siting_factorial_240_four_arm_duration_values.csv`, `paper_s_siting_factorial_60_shapley_interaction.csv`, `paper_s_siting_factorial_240_hourly_curve_descriptives.csv`, and manifest JSON. A separate conversation-level Word results supplement contains figures M1–M3 with publication-ready draft text; it is NOT committed as a GitHub binary release.
