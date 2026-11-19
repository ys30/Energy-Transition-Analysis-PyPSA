# Paper S — hour-order constrained 4→8h input-only storage policy (2026-11-19)

## Objective and status
This experiment strengthens the earlier order-blind daily surplus–deficit proxy, **without rerunning or modifying the main LP**. The 240 original source cases are 15 independent source-weather years × AZ/CO/ID/WY × 2 county weight schemes × renewable peak ratios 1.5/2.0, wind AC share 0.5 and the same authenticated fixed-2030 demand. The previously audited 3×3 economic screening (19,440 comparisons, 213 unique source cases above the cheapest ATB threshold) remains frozen.

**Status: method and CI code committed; not an empirical finding until the new GitHub Actions artifact succeeds and is audited.**

## Dispatch rule and physical scope
For each 24-hour block on the fixed 2012 reference calendar and with zero starting SOC, form hourly exogenous net renewable surplus `max(available - load,0)` or exogenous deficit `max(load - available,0)`. Under common battery power `P=0.25 × peak(load)`, energy capacity `E=P×4` or `P×8`, and charging/discharging efficiency `sqrt(0.9)`:

1. In positive-surplus hours, charge using **only exogenous excess renewable energy** up to the hourly charging power limit and remaining SOC headroom: `charge=min(surplus,P,(E-SOC)/eta_charge)`. No simultaneous discharging.
2. In deficit hours, discharge up to demand deficit, inverter power and stored SOC: `delivered=min(deficit,P,SOC×eta_discharge)`. No simultaneous charging.
3. Update `SOC+=charge×eta_charge−delivered/eta_discharge`; explicitly check `0≤SOC≤E` and the per-hour SOC conservation error.
4. End-of-day unused SOC is accounted as discarded stored energy, and the next day starts empty. The same delivered service can be implemented by not charging surplus that would remain unused; hence this is an admissible conservative **daily-restricted** schedule, not a full-year maximum. An optional interday carryover strategy can transfer more energy and is not tested here.

Each run computes **two separate feasible policies** (4h and 8h), then takes the difference in served deficit MWh. Because the dispatch is greedy rather than globally cost minimizing, the difference is a *policy-dependent witness*, **not** the maximum feasible 4→8h incremental discharge and **not** an upper bound for the optimized annual LP value. Battery assets cannot import firm generation for charging in this test. This is intentionally independent of the LP objective function.

## Decisive falsification
- Surplus-only and deficit-only days deliver no energy.
- **Deficit before surplus**: earlier order-blind daily proxy can be positive; the hour-ordered policy must deliver zero for both battery durations.
- **Surplus before deficit**: capacity expansion can yield positive additional delivered deficit, subject to power/SOC conservation.
- Compare 15-year *matched siting differences* of chronological policy energy with original frozen LP value differences. For 4 states × 2 penetration ratios, preserve `r`, signed agreement count /15 and median paired spatial effects, including failures/negative results. Do not infer cause from correlations.
- Report 240 source cases, 87,600 day records, 120 matched siting pairs, and 8 state×penetration summaries; all directly joined to the frozen 1,080 LP duration table.

## Reproducibility
Code: `src/energy_transition/paper_s_daily_transfer_proxy_and_ipco_shape.py` (`chronological_daily_policy`, `chronological_comparison`, expanded `--mode daily`).
Tests: `tests/test_paper_s_daily_proxy_and_ipco_shape.py`.
CI: `.github/workflows/paper-s-daily-mechanism-ipco-shape-2023.yml`.

New source-artifact files:
- `daily/C1_chronological_policy_240_cases.csv`
- `daily/C2_chronological_policy_87600_days.csv.gz`
- `daily/C3_chronological_policy_vs_LP.csv`
- `daily/C4_chronological_policy_120_paired_differences.csv`
- `daily/C5_chronological_mechanism_8_group_summary.csv`

Outputs are not EIA930 observed generation; original 2023 IPCO BA shape diagnostics run separately and do not resolve BA/state mismatch.

## Manuscript interpretation
The chronological witness is a physically constrained, objective-independent mechanism *diagnostic*, not a proof of unique causality. Any broad claim of feasible 8h-only daily shift must be qualified by the policy and no-carryover boundary. Keep LP accounting identities and SOC active-set/dual statistics in separate model-internal evidence or SI. A mechanism supported by three layers (input-only annual proxy, hour-ordered feasibility, fixed original LP values) is stronger than a tautology; no field calibration or causal estimate follows.
