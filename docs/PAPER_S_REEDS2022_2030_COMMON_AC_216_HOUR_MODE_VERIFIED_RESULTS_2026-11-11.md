# Paper S — common AC same-source 216-hour-approximation robustness results (2026-11-11)

## Verified run

Successful source-verified 216-original-LP experiment and 36 paired time-approximation comparisons:
https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43080107709

Artifact: `paper-s-reeds2022-2030-common-ac-216-hour-mode-lps-and-36-comparisons`.

Contents:
- `paper_s_reeds2022_2030_common_ac_216_hour_assumption_LPs.csv` — original HiGHS LP outcomes for four states × 3 common-AC renewable nameplate ratios × 3 AC wind fractions × 2 hour approximation modes × 0h/4h/8h storage
- `paper_s_reeds2022_2030_common_ac_72_hour_storage_pairs.csv` — matched 0/4/8h savings and 4→8h energy-only annual annuity hurdles under each mode
- `paper_s_reeds2022_2030_common_ac_36_hour_assumption_comparisons.csv` — matched end-instant-hold vs trapezoid comparisons; includes a boolean flag for the conditional $10/kWh-year *energy-only* annuity decision
- `paper_s_reeds2022_2030_common_ac_216_hour_assumption_manifest.json` — count, objective regression and scientific scope gates

All 216 LPs optimal, checked hourly balance residual ≤1e-5, 72 duration triplets complete, 36 matched source-hour choices complete. The trapezoid model's **108 corresponding scenarios** matched the earlier frozen source-AC LP experiment [43058074434](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43058074434) within **max $0.0049758** absolute difference in original illustrative annual operating objective.

## Central 2030 common AC reference scenario

Hypothetical installed wind+PV AC = 1.5× peak demand, wind = 50% common AC nameplate, PV array DC = 1.34× its inverter AC nameplate, battery charging/discharging power 25% of peak demand; 90% battery round-trip efficiency, illustrative firm marginal cost $90/MWh, renewable $5/MWh. Same publisher 2012 8,760 source instants (with leap-day and omitting Dec 31) and projected 2030 demand.

Incremental 4→8h energy-annuity ceilings, $/kWh-year:

| State | End-instant hold | Prior-instant+end-instant trapezoid, first endpoint fallback | Trapezoid minus hold |
|---|---:|---:|---:|
| AZ | 11.900281 | 10.955400 | −0.944881 |
| CO | 6.853588 | 6.220671 | −0.632917 |
| ID | 4.483479 | 4.134846 | −0.348633 |
| WY | 3.754351 | 3.540569 | −0.213782 |

Across all **36 time assumption comparisons**, the largest absolute 4h→8h marginal energy-only annuity difference was **$1.0504948/kWh-year**. Under the chosen *hypothetical* $10/kWh-year added energy-capacity annuity threshold, exactly **zero of the 36 scenarios** had a decision flip between the two numerical interpretations. This binary classification stability cannot be misread as evidence the numerical hourly-generation energy is publisher-certified or observed.

## Proposed manuscript insertion

### Results — sensitivity of hypothetical storage value to within-hour representation

An additional prespecified 216-LP same-source sensitivity compared (i) holding the publisher's instantaneous wind and PV CF at each end-hour label and (ii) a trapezoidal average with the prior source instant, using an explicit first-hour endpoint approximation and no unobserved last-to-first wrap. Resource AC nameplate, demand, storage power, cost and energy-duration assumptions were held identical, with 108 trapezoid solutions numerically reproducing previously archived common-AC benchmark objectives within $0.005. The two numerical assumptions produced nonidentical marginal 4→8h storage-value ceilings; for the illustrative 1.5× AC penetration, 50% wind case, Arizona's energy-only threshold shifted from $11.90/kWh-year under end-instant hold to $10.96/kWh-year under trapezoid. Colorado, Idaho and Wyoming showed corresponding reductions of approximately $0.63, $0.35 and $0.21/kWh-year. Among 36 matched state/resource portfolio configurations, the largest absolute difference was $1.05/kWh-year, but none changed the binary conclusion of whether the model's energy-only savings exceeded an arbitrarily posited $10/kWh-year annualized cost. These results demonstrate limited *binary decision* sensitivity in this specified model grid, not physical validation of hourly renewable energy integration.

### Discussion — what this test does and does not establish

All weather-resource curves originate from independently audited ReEDS2022 county-source 2012 data and original projected demand timestamps, but **source CF is a point observation while demand is hour-ending**. Neither the prior/end source-average approximation nor the hold approximation has been established against independent interval-integrated output (NSRDB or other independently timestamped source). Thus comparisons of marginal dollar value are conditional on an unvalidated numerical hour-energy interpretation. Passing the 36-case binary threshold test is not a physical-hour mapping certification, and extrapolating it to other cost/efficiency/renewable penetration combinations, weather years, or actual fleet sites is not supported.

## Data-integrity and pre-submission gates

This is a synthetic *capacity deployment* and variable cost scenario on real publisher-source resource shapes. State resource development supply curves are *available potential*, not installed fleet. Model uses within-state copperplate, one weather reference year, 2030 projected load, no transmission/commitment/reserves/capacity adequacy, zero battery CAPEX or O&M in LP objective. Margin above hypothetical energy-only annuity is not bankable net NPV/IRR or observed avoided utility bills. Full original EFS2020↔ReEDS2022 cross-release time audit gate from Paper T remains blocked; do not use same-release fixed-CST source timestamps to certify different EFS releases. The separate legacy full-repository CI failure is unrelated to the successful dedicated experiment but still blocks declaring a fully green PR.

A substantive follow-up needs independent publisher-certified or measured UTC/hour-integrated generation under the same 2012 source period, *or* explicitly retain the time approximation as limiting uncertainty. A future more defensible physical calibration should also replace resource-potential-weighted state CF with actual or credible 2030-installed-fleet spatial weights and model local grid network constraints.
