# Paper S — 8760-hour annual input-only two-source-year pilot VERIFIED (2026-11-20)

## Verification and scope
Run [44787084995](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44787084995) completed **SUCCESS**, all four independent state jobs succeeded. Four state artifacts (IDs AZ 14671282364, CO 14672055725, ID 14670229532, WY 14672170489) were **downloaded and read**, not inferred from CI status alone.

All four states cover both publisher-backed 2012 and 2023 weather years and both potential vs EIA2025 operating-county spatial weights, 16 cases, 96 storage-transfer HiGHS LP solves. Each case uses source-aligned fixed 2030 annual 8,760h reference demand, native ReEDS wind/PV, AC normalization and 50% wind share; input-only objective maximizes surplus-renewable electricity dispatched into later deficit hours. SOC boundaries zero at each 24h, each 168h plus terminal 24h, or at 8760h; 4h and 8h capacities considered separately. **Largest 8760-hour equality residual observed across all artifacts: 7.276e-12 MWh.**

## Spatial EIA-minus-potential differences (same weather year)

| State, ratio | Weather year | Daily 4→8h siting effect (MWh) | Weekly effect (MWh) | Annual effect (MWh) | Original full-year LP siting effect (USD/added kWh-year) |
|---|---|---:|---:|---:|---:|
| AZ,1.5 | 2012 | -78,464.0 | -227,714.8 | -249,816.9 | -1.087 |
| AZ,1.5 | 2023 | -22,902.7 | -76,273.4 | -81,099.3 | -0.353 |
| CO,2.0 | 2012 | -3,749.6 | -280,725.0 | -317,150.0 | -2.338 |
| CO,2.0 | 2023 | -7,863.4 | -245,614.1 | -287,960.9 | -2.123 |
| ID,1.5 | 2012 | +7,307.9 | +81,004.2 | +101,994.0 | +1.655 |
| ID,1.5 | 2023 | +5,697.4 | +86,813.2 | +100,534.0 | +1.631 |
| WY,1.5 | 2012 | +27,004.1 | +81,094.1 | +88,568.6 | +2.437 |
| WY,1.5 | 2023 | +40,803.4 | +116,275.4 | +121,602.9 | +3.346 |

**Pilot interpretation:** source-only transfer effects have the same *sign* as the frozen model-economic spatial effects in all 8 state×year pairs, under daily, weekly and annual SOC boundaries. The **magnitudes are in different units**; this is not causal identification or observed dispatch. The model maximizes physical transferred MWh, not avoided generation cost. Correlation from only two weather years is **inadmissible** and must not be reported.

## Important limitations
The differences between 4h and 8h energy can respond strongly to SOC boundary choice even for the same fixed 8760h source. The study uses synthetic modeling assumptions for firm generation in the *comparison* LP, rather than observed prices; the mechanistic LP itself uses no electricity price. Neither the pilot nor earlier two-week falsification results authorize declaring a stable 15-year annual mechanism. Weather years are source-year samples and are not independent randomized trials. EIA2025 county operational spatial weights are not observed 2012 or 2023 fleet truth.

## Admission decision
The source-verified pilot satisfies numerical and schema validation and supports **launching the predeclared full 15-weather-year analysis**, not manuscript-wide causal mechanism conclusions. The final 120 annual cases, 60 year-paired siting effects and all four 15-year grouped correlations must be audited before main-text annual mechanism results are admitted. Preserve 213/1080 conditional economic hurdle crossings unchanged.
