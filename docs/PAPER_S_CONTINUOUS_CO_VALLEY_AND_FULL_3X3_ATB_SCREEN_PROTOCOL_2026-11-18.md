# Paper S — Continuous CO valley, non-circular mechanism, and complete 3×3 ATB economic gate (2026-11-18)

## What is established
The authenticated full 3×3 run 44209543001 (artifact 14388326204) contains 1,080 weather-year × state × siting × design-point 4→8h values from 2,880 new LPs and 360 reused original baseline LPs. ReEDS 2030 reference demand, 15 source-weather years and two geographically distinct county weighting schemes are held under the original assumptions.

For Colorado at renewable peak ratio R=2.0, direct 3×3 paired median EIA-minus-potential value is −0.164 (25% wind), −2.178 (50% wind), +2.615 (75% wind). An independently completed CO hourly mechanism run 44453880808 verified 40/50/60% wind sensitivities and matched 180 optimal LP outcomes. Approximate −1.8 (40%) and −0.3 (60%) values obtained by scaling dispatch totals against the 50% anchor are **not** independent LP-derived median value estimates, and must be replaced by direct 40/60% objective-based paired medians from authenticated run outputs before they appear in a main result table. Sign counts 40% 0/15, 50% 0/15, 60% 1/15 and 75% 15/15 require source-row verification. Taken together these show a candidate broad negative interval, not an isolated 50% grid error; interpolation of the exact minimum is not identified.

## Mechanism hierarchy
- Level 1 (model accounting): 4→8h reduction in firm generation and curtailment and changes in the LP objective are internally consistent. These quantities are algebraically linked by the objective, so correlation is **not independent causal physical explanation**.
- Level 2 (input-only): daily renewable surplus and deficit derived without solving optimization are tested as explanatory proxies; code: `paper_s_daily_transfer_proxy_and_ipco_shape.py`. This is NOT physically feasible shifted MWh, an LP upper bound, or proof of mechanism: it ignores within-day timing, battery power, carryover SOC and alternative optimal schedules.
- Level 3 (physical timing): future causal explanation requires order-aware charging/discharging availability under identical inputs and power/SOC rules, and agreement across geography–weather scenarios without selecting favorable years. Hourly SOC and active-constraint counts are descriptive SI because optimal solutions can be nonunique.

## Reopened economics conclusion
Earlier authentic ATB screening compared 18 annualized hurdles against only the original 120 reference/design-point duration values (2,160 comparisons), establishing 0/120 threshold crossings **per hurdle under its specific original design**. It cannot support a universal 'never economic' claim. The official source-cell-pinned ATB 2025 v2 cost hurdle formula, under fixed common MW, a 15-year life and discount rates 4%, 7%, 10%, is
`H = [(OCC8-OCC4)*CRF + (FOM8-FOM4)]/4` in 2023 USD/(added kWh-year).
The 18 cost scenarios include duplicate numerical hurdle values; do not treat them as independent experimental observations.

## Executable full economic gate
New code `src/energy_transition/paper_s_atb_full_3x3_screen.py`, unit tests, and workflow `.github/workflows/paper-s-atb-full-3x3-screen.yml` use the unchanged 1,080-value artifact from run 44209543001 and the pinned ATB source cell CSV to calculate all **19,440** comparisons. Expected output:
- 18 verified source hurdles
- 19,440 comparison rows, one per duration value × cost assumption
- 1,296 state × design × siting × ATB summary rows (15 weather years per cell)
- 18 cost-assumption overall rows
- explicit manifest documenting full counts, numeric cost duplicates, and independent fixed-2030 baseline comparisons. The earlier historical-load 0/120 is a different LP population and is **not** a regression gate for the fixed-2030 baseline.

**Result status: PENDING successful CI/artifact audit.** The suggested CO R=2.0, wind 40% potential/equipment-weight median values of approximately 19.7/17.9 USD/kWh-year may clear the cheapest ATB 16.05 threshold, but they are not substituted for original LP values. Do not report aggregate threshold crossing counts until a completed source-backed artifact is read.

## Required figure and manuscript changes
- Plot a 4 × 3 × 3 economic crossing-count matrix (weather-year count 0–15), separately by siting assumption and selected ATB cost scenario, plus distribution and paired differences. Always show the value scale and cost threshold in 2023 USD only as illustrative, not verified currency-matched profitability.
- Present conditional threshold exceedance, not positive investment NPV, real-world investment viability, or 'economic in this state'. The model's illustrative 90 USD/MWh firm generation price has not been independently deflated or calibrated to the ATB 2023 USD basis. Other battery costs, cycling degradation and transmission constraints remain excluded.
- Restrict Abstract, §1.6, §4.3 and Conclusion's original historical-load non-crossing claim to the **historical-load baseline scenario** (do not conflate it with the fixed-2030-demand R=1.5, wind share 50% baseline) and clearly label the expanded 3×3 findings separately after numeric verification.
- Keep the scientific mechanisms and economic screening results separate: neither LP accounting identities nor repeated cost inputs provide independent physical causal evidence.
- Preserve existing 1,440/360/2,880/720/2,160 LP source artifacts, Paper T and Paper C-2.
