# Paper S — ReEDS2022 county-native 144-LP nameplate sensitivity (2026-11-11 UTC)

## Verified runs and exact source

- Authenticated official 2012 county-level wind/PV to AZ/CO/ID/WY state hourly source-CF artifacts: [Actions #42962740548](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42962740548).
- Original 0.9× state-peak-load 48-case LP baseline: [Actions #42965036275](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42965036275), success.
- New 0.9, 1.5, 2.0× nameplate × four states × three demand-model years (2030/2040/2050) × two hour interpolation assumptions × 0h/4h battery: **144/144 optimal**, with 72 fully matched 0h/4h pairs. [Actions #42966023512](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42966023512), success. Exact 48 original baseline costs matched within $0.05, and solver equality-residual checks passed.
- Canonical files in `paper-s-reeds2022-county-144-ratio-sweep-original-source-2012` artifact: `paper_s_reeds2022_county_native_144_ratio_LP.csv`, `paper_s_reeds2022_county_native_72_ratio_paired.csv`, `paper_s_reeds2022_county_native_ratio_sweep_manifest.json`.

## Matched source-based 2030 results (trapezoidal with first-hour endpoint fallback)

Each saving is the difference in **illustrative variable operational LP objective**, 0h minus 4h, using identical weather source and assumed renewable nameplate. It is **not** net benefit of storage investment.

| State | Ratio | Variable-cost avoided, USD | % of 0h objective | Curtailment as % of no-storage renewable availability |
|---|---:|---:|---:|---:|
| AZ | 0.9 | 25,125,374.79 | 0.488769 | 1.173426 |
| AZ | 1.5 | 218,243,845.64 | 5.975283 | 10.349234 |
| AZ | 2.0 | 373,762,197.39 | 12.914189 | 21.161677 |
| CO | 0.9 | 2,350,999.07 | 0.060531 | 0.133772 |
| CO | 1.5 | 64,082,810.27 | 2.375974 | 3.850787 |
| CO | 2.0 | 175,027,412.78 | 8.715741 | 12.115542 |
| ID | 0.9 | 371,613.08 | 0.021146 | 0.054542 |
| ID | 1.5 | 21,144,468.29 | 1.645984 | 2.807337 |
| ID | 2.0 | 67,012,689.51 | 6.703574 | 10.277962 |
| WY | 0.9 | 13,036.44 | 0.000987 | 0.002559 |
| WY | 1.5 | 11,610,383.93 | 1.206923 | 2.196197 |
| WY | 2.0 | 36,461,995.85 | 5.020007 | 8.037454 |

## Mechanistic interpretation and causal limitations

1. The low 0.9× result in WY/ID is **not stable across nameplate assumptions**: simulated four-hour storage savings rise substantially in the 1.5× and 2.0× scenarios.
2. Increased nameplate coincides with much higher no-storage curtailment. Storage can charge using otherwise curtailed energy, helping explain the strong rising operational value, although correlation of curtailment and benefit does not separately identify causality.
3. The four-state rank by absolute savings is AZ > CO > ID > WY across these 2030 cases. But ranking is contingent on modeled demand and potential-weighted resource mix; must not be generalized to actual capacity plans.
4. Prespecified wind/PV nameplate mix 50/50, storage discharge/charge power 0.25× state peak, 4h energy, roundtrip 90%, modeled marginal generation costs ($5 renewable, $90 firm per MWh), **zero storage capital or fixed costs**. State copperplate, no buses, interconnectors, reserves, capacity adequacy, degradation or ancillary services. These assumptions may dominate monetary results.
5. Resource profiles derive from original county-level *available developable potential* weighted by class/county supply curve, not installed fleet siting. ReEDS reference weather is 2012, paired to 2030–2050 demand projections, not measured future wind/PV generation.
6. Original native CF is **instantaneous**, while source demand is **hour-ending**. End-instant hold and interpolating consecutive instants (with non-cyclic first-hour endpoint fallback) are numerical approximations, not original-publisher certified interval energy. Both must be shown in sensitivity tables/figures.
7. The original EFS2020 p-zone Paper S numerical claims remain frozen and untouched; this new source study must be identified by its own scope.

## Next experimental gates

- Publish 4-state across-ratio plots of savings, curtailment and temporal-convention sensitivity for all demand years.
- Quantify 0h to 4h firm-energy displacement (MWh) and charging from surplus; avoid inferring capacity adequacy.
- Acknowledge model's inability to distinguish real build-out potential, transmission bottlenecks, and battery investment viability.
- Follow with prespecified 2D storage power/energy and wind/PV share controls, then cost and battery CAPEX sensitivity before considering strong Q1 journal claims.

**Other CI:** Full repository CI #42966023525 failed during a separate Paper T downstream test on `KeyError: net_peak_clock_hour`. This does not overturn the successful 144-case LP and matching artifact workflows, but PR #2 still cannot be treated as all-green.
