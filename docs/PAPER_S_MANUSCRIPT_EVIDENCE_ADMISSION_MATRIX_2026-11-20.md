# Paper S — manuscript evidence admission matrix and source-verified claims (2026-11-20)

## Why this gate exists
The workflow queue is congested; **queued is not success** and source-independent unit tests are not the same as source-backed annual results. No 8760h physical mechanism numerical claim is admitted until the actual GitHub artifact, 15 original weather years, conservation checks, and frozen-LP joins are independently reviewed.

## Main-text findings already source-verified

### 3×3 design and economic threshold *screening*
Authenticated 15-weather-year, four-state, two-county-weight study across renewable peak ratios R = 1.0/1.5/2.0 and AC wind shares 25/50/75%, yielding **1,080 original four-to-eight-hour value cases**. ReEDS original-county-potential versus EIA2025 operating-fleet-county weights are contrasts in modeled spatial aggregation, not observed contemporaneous 2023 fleet counterfactuals. Costs were compared with 18 labeled source-pinned ATB 2030 storage capex/FOM/discount-rate assumptions, **19,440 rows**, whose numerical hurdle values contain duplicates.

- Under the lowest ATB hurdle (Advanced, 4% real rate), **213 / 1,080** modeled source cases exceed **16.049 illustrative USD/(added kWh-year)**. The count is **not** a claim of profitability, ROI, net present value, or actual project viability.
- Breakdown under that hurdle: AZ 89, CO 60, ID 34, WY 30; **R=2.0, 25% wind 120/120**; R=1.5, 25% wind 61/120; R=2.0, 50% wind 32/120; all R=1.0 designs and 75% wind designs 0.
- The model firm generator marginal cost is illustrative ($90/MWh); ATB is an authenticated cost-input source expressed in 2023 real dollars. Their units/year base have **not** been independently reconciled. Phrase the comparison as **conditional cost-threshold screening** only, not a calibrated investment cost-benefit analysis.
- Fixed 2030 EFS-demand R=1.5 and 50% wind central design: 0/2,160 cost comparisons crossed. Historical demand experiments are **different populations** and must not be collapsed into the same baseline.

Provenance: [19440 screening artifact run 44463644688](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44463644688), result details in `docs/PAPER_S_VERIFIED_3X3_ATB_DAILY_MECHANISM_IPCO_RESULTS_2026-11-19.md`.

### Input-only daily surplus-deficit mechanism proxy
The original order-blind daily energy proxy correlated strongly with EIA-minus-potential LP spatial value effects for selected ratios (AZ 0.926/0.764, CO 0.643/0.836, ID 0.886/0.898, WY 0.974/0.948). **These are not physically ordered battery shifts**, and may reflect shared weather/source structure rather than independently identifying the mechanism.

### Physically chronological greedy daily policy
Imposing hourly ordering, rated power, SOC bounds, daily empty initial SOC and end-of-day discharge reduced annual paired-effect correlations for eight groups:
AZ (R1.5/R2) 0.019/0.003; CO 0.369/0.388; ID 0.144/0.498; WY 0.827/0.359. Corresponding sign agreement across the **120** source-weather-year within-state siting pairs decreased from **107/120 to 98/120**. The policy is feasible but greedy, day-restricted and not maximizing annual deliveries. This finding falsifies an overly broad inference from the order-blind proxy, **not** the entire class of chronological renewable-shift explanations.
Provenance: [chronological 240-case run 44570259601](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44570259601).

### Two optimal 168-hour window pilot experiments
Optimal renewable surplus-to-deficit energy-shift LPs under 24h and 168h zero-terminal SOC, for the same two predetermined source-week windows, produced 240 source case×window records (960 optimization solves). Allowing weekly SOC improved deliverable energy for 4h and 8h individually, but does **not** necessarily improve their 8h-minus-4h difference. Cross-year correlations with the annual LP value effect varied strongly by window (CO R2 weekly: -0.056 in window A vs +0.448 in window B). **Do not** present two time windows as an annual validation. Put the full eight-window comparison in the Supplement.
Provenance: [168h run 44678383884](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44678383884), `docs/PAPER_S_VERIFIED_168H_CROSS_DAY_OPTIMAL_TRANSFER_TWO_WINDOWS_2026-11-20.md`.

### IPCO original 2023 shape diagnostic
EIA-930 Idaho Power BA actual wind and solar is a different geography from Idaho statewide renewable supply. EIA 2025 operating-counties are not an authenticated native 2023 IPCO fleet inventory. Zero-shift adjusted solar Pearson r approximately 0.954 (ReEDS potential) versus 0.969 (EIA-weighted); wind r approximately 0.734 for both. This is a model/input **shape diagnostic**, not independent capacity calibration, out-of-sample predictive proof or observed causal siting validation.
Provenance: `docs/PAPER_S_VERIFIED_3X3_ATB_DAILY_MECHANISM_IPCO_RESULTS_2026-11-19.md`.

## Yet-to-be-admitted annual 8760h physical mechanism
An annual (8760h) input-only MWh maximization model has been coded with three nested storage SOC feasible sets: 365 daily intervals, 52 seven-day intervals plus a final one-day tail, and one 8760-hour zero-to-zero continuous interval. Each separately maximizes renewable-only surplus delivery to later deficit without using firm-generation prices. 4h/8h energy capacities and charging power, and initial/terminal SOC, remain comparable.

**Execution status as checked on 2026-11-20:** [four-state source-backed annual pilot](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44770251096) queued; the all-15-weather-year workflow is prepared but **not started**. It is wrong to declare the annual mechanism passed, or report Pearson r over just two pilot weather years.

### Required review before annual mechanistic manuscript conclusion
1. Pilot must upload authentic per-state 2012/2023 source results and pass all hourly/sparse equality, nested-feasible-set, complete-window, frozen EFS demand and ReEDS CF source checks.
2. All 15 original source-weather-year partition jobs must finish successfully (4 states × three five-year groups): **120 full-year source cases, 720 distinct physical energy LP solves**.
3. Aggregated cases must contain exactly 60 EIA-minus-potential annual siting pairs, four complete 15-year state groups and **no duplicates or missing** original LP values; independent 1:1 match to frozen wind share 50% LP grid.
4. Inspect three horizons' 4h-to-8h **incremental** value; do not impose false annual >= weekly >= daily *incremental* monotonicity. The nesting property applies only to the total delivered MWh **at fixed battery duration**.
5. Report all four state-by-ratio spatial effects, correlations and negative findings including seasonal/window disagreements, rather than focusing only on WY or CO.
6. Do not promote input-only energy correlation to causal identification. The original economic LP can respond to temporal prices/firm constraints, whereas this maximum MWh formulation uses only renewable surplus/deficit envelopes. Both originate from common weather and demand inputs.
7. Render and visually review the audited annual heatmap and 4-state paired-weather-year scatter. Figure code rejects incomplete 15-year populations.

## Manuscript edits to make after the 15-year gate
- **Abstract:** distinguish *conditional cost-screening* and model sensitivity from calibrated profitability; note heterogeneity and unresolved mechanism if annual physical evidence is weak.
- **Methods:** define time support and county weights, wind/PV AC normalization, battery power-duration basis, efficiency, 2030 EFS fixed demand, 15 source weather years and ATB source year. Delineate model-derived outputs versus exogenous mechanism inputs.
- **Results:** 36 design cells and 213/1080 cheapest-hurdle crosses; CO nonlinear negative siting interval at R2.0 with support and appropriately qualified interpolation; separate full-year physical mechanism results only upon admission.
- **Discussion:** acknowledge no empirical 2023 fleet truth, transmission and network omissions, uncalibrated 2023 USD consistency, unobserved merchant prices, 15-year weather rather than independent random replication, and BA/state scope mismatch.
- **Supplement:** daily un-ordered, greedy chronological, 168h optimal pilot, year-by-year diagrams, full threshold matrix and provenance checks.
- **Conclusion:** avoid universal '8h batteries never pass costs', avoid a universal physical siting mechanism, and avoid claims of observed realized profitability.

## Source immutability
Do not modify previously audited 2,880 new LPs, 360 reused 3×3 baseline LPs, existing ATB screens, Paper T, Project C-1 or Project C-2. This file is a **reporting gate**, not permission to merge or submit.
