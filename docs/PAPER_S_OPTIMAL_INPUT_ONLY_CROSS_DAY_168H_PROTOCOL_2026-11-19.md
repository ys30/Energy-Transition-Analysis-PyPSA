# Paper S — optimal input-only 168h cross-day transfer: pre-registered admission gate (2026-11-19)

## Why this study
Original 24h order-blind surrogate correlated strongly with paired annual LP value, but the 24h greedy, SOC-constrained policy largely falsified the explanatory magnitude (CO R2 r=.388, ID R1.5 r=.144, WY R1.5 r=.827, AZ R1.5 r=.019). This study asks whether the attenuation stems from **greedy charging** and **artificial daily SOC resets**, rather than the broader absence of physically available transfer.

## Experimental design and exact boundaries
- Freeze the already authenticated 15 ReEDS weather-source years, state 2030 EFS reference load (mapped to 2012 reference support), AC-normalized wind/PV, two county weights, and the original marginal 4→8h cost-LP results. No new economic LP or project modification.
- Four predeclared state/penetration cases: AZ 1.5 (negative control), CO 2.0 (valley), ID 1.5 and WY 1.5; wind share fixed at 50%.
- **Two unselected 168-hour calendar windows**: source hour indices 0–167 and 4320–4487, for a total of 240 state×year×weight×window cases (120 each window). A two-week sampling study is NOT an annual maximum-transfer mechanism, nor representative of all weather conditions.
- Every case solves four **maximum delivered MWh** models: 4h or 8h × 7 independent 24h zero-terminal SOC days versus one contiguous 168h zero-terminal SOC week. The initial SOC is always zero. The weekly feasible set contains the daily-zero schedule at each battery duration.
- Hourly charging is bounded by `max(renewable available−load,0)` and rated charging MW. Hourly discharge is bounded by `max(load−renewable available,0)` and rated discharging MW; SOC recursion and SOC MWh ceiling are explicit, round-trip efficiency fixed at 0.90, charging and discharging impossible together because net-surplus and net-deficit hours are mutually exclusive.
- The objective is `maximize(sum(discharge-to-deficit MWh))` without $/MWh, avoided firm-unit-cost weights, ATB assumptions, or annual LP output. The weekly horizon may transfer energy across midnight. For each duration separately, weekly delivered MWh must be at least daily delivered MWh.

## Crucial interpretation
The *incremental 8h-minus-4h gain* under the weekly horizon is **not necessarily larger** than the corresponding gain under daily resets: even though total delivered MWh for each duration weakly increases as constraints relax, differences of two increases can be negative. No test may incorrectly assert weekly minus daily incremental gain is nonnegative.

The new input-only mechanism is an optimal MWh *within the prespecified surplus-only/deficit-only and boundary constraints*, not a physical maximum over all grid operations and not a direct explanatory bound for the original *economic objective* LP (which may charge from renewable output that could otherwise directly serve load or shift over other periods). The full-year cost-optimal LP and 168h energy-optimal LP are deliberately distinct. Cross-correlation with annual LP value across 15 years is descriptive and mismatched-horizon, not a causal or full-year validation.

## Outputs per window
- `W1_120_source_week_cases.csv`: delivered 4h/8h energy, 24h/168h horizons, actual LP annual value and residuals.
- `W2_120_paired_horizon_rows.csv`: EIA-minus-potential annual-source-year pairs for both horizons, aligned with immutable annual LP spatial effect.
- `W3_four_state_horizon_summary.csv`: four state-specific sign agreements, correlations and median contrasts.
- `W0_manifest.json`: input scope, initial/terminal SOC, calendar window and non-causal disclaimers.

## Admission decisions
1. CI must pass all source-independent cross-midnight and SOC negative tests.
2. The complete 120 unique source cases per window must be present; verify two designs per year/state, equality residual <1e-5 MWh, both nested 4h/8h and weekly/day total MWh inequalities.
3. Inspect each window for sign and value agreement **including failures**. Never select the favorable window. Any seasonal reversal must be reported.
4. Decide after the two-window pilot whether a **whole-8760h input-only LP with cyclic terminal SOC** is feasible and scientifically necessary. Avoid drawing annual inferences from two weeks.
5. Preserve original 1,440/360/2,880/720/2,160 LP work, 213/1080 cheapest ATB crossings, C-2, and the original native 2023 IPCO source-shape audit.

**Status: code/tests/workflow submitted; no new numerical results admitted before successful Actions artifact QA.**
