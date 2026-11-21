# Paper S — R=2 wind-share 40/50/60 continuity test VERIFIED (2026-11-18)

## Successful independent numerical experiment

- Original fully verified 3×3 [GitHub Actions run 44209543001](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44209543001), artifact **14388326204** (25/50/75% shares; originally frozen).
- New [GitHub Actions run 44449229739](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44449229739), artifact **14496385838**, job **success**, **720 freshly solved optimal LPs** for R=2, 40% and 60% wind AC: 4 states × 15 source weather years × 2 county siting weights × 2 shares × 3 battery-duration alternatives. This is not an interpolation, refit, or reuse of the 50% cell.
- Verified 240 original-source input-array checksum records, consistent within every (state, weather year, siting scheme) for 40% and 60%: **demand, original wind series and original PV series hashes are exactly identical across the two shares**; only the wind/PV weighted mixture changes. Original 50% share code uses the same underlying input calculation pathway, but this particular new output **does not store the original 50% hour-array hashes**, so do not claim a cryptographic equality check at 50%.
- All new LP cases have max equality residual **7.275957614183426e-12 MWh**. Original frozen 3×3 result is not modified.
- Independently joined the real original and new paired weather-year artifacts by **state, weather year, ratio, wind AC share** with **300 unique R=2 paired source-weather-year values** (4 states×15 years×5 shares), no duplicated keys.

## Main verified 15-weather-year paired state-mean geography effect (MEDIAN across within-year pairs)

All values in illustrative model USD/(added storage kWh-year), county EIA 2025 fleet weight **minus** original ReEDS 2012 source resource potential.

| State | 25% | **40% NEW** | 50% original | **60% NEW** | 75% | 40% positive years | 60% positive years |
|---|---:|---:|---:|---:|---:|---:|---:|
| AZ | -0.469 | **-0.713** | -0.169 | **-0.112** | +0.358 | 0/15 | 6/15 |
| CO | -0.164 | **-1.819** | **-2.178** | **-0.301** | +2.615 | **0/15** | **1/15** |
| ID | +0.717 | **+0.355** | +0.688 | **+1.230** | +1.209 | 13/15 | 14/15 |
| WY | +1.241 | **+1.444** | +1.011 | **+1.327** | +0.983 | 15/15 | 14/15 |

**CO year-level rather than median-only evidence:** 50% effect below both 40% and 60% in **12/15 weather years**; 50% below 60% in **15/15**. Each CO weather year has negative midpoint curvature: `effect(50%)-[effect(40%)+effect(60%)]/2 < 0`, median **-1.139462 model USD/(added kWh-year)**. This local valley is present across years and survives two genuinely new design-point solves, making a single 3×3 grid 50% output-assignment error much less plausible. It is NOT proof of a universal continuous response or of any individual charging saturation event.

## Mechanism indicators — source-cohort descriptive, not causality

Colorado source-year **medians** of model's marginal 4→8h value by weights, along with the **4→8h decrease in firm generation**:

| Wind share | EIA weight median marginal V | ReEDS potential median marginal V | EIA median firm reduction MWh | Potential median firm reduction MWh |
|---|---:|---:|---:|---:|
| 25% | 22.568 | 22.710 | 3,061,138 | 3,080,389 |
| 40% | 17.898 | 19.740 | 2,427,652 | 2,677,556 |
| 50% | 13.241 | 15.419 | 1,796,005 | 2,091,408 |
| 60% | 8.595 | 8.890 | 1,165,867 | 1,205,838 |
| 75% | 7.321 | 4.676 | 993,058 | 634,258 |

In both county-weight schemes marginal 4→8h savings decline as wind share rises; **the two schemes decline at different rates**, and their weather-year-paired difference dips and reverses. The same-shares decrease in unused renewable generation between 4h and 8h is also different between schemes. These are compatible with a nonlinear **dispatch value crossover**, but aggregate 4h/8h energy and 15-year medians alone cannot diagnose an SOC-saturation threshold or hour-specific curtailment-absorption cause. **Median(EIA V)−median(potential V) need not equal median(EIA−potential)**, so do not use the table's scheme medians as an arithmetic reconstruction of paired effects.

## Reproducibility material

Conversation-local `Paper_S_R2_40_60_Continuity_Verified_2026-11-18.zip` includes a combined unique 300 weather-year pair table, 20 state×share medians and sign counts, 60 year-level 40/50/60 curvature tests, 150 Colorado siting/year operational indicators, 10 Colorado design×weight operational medians, an original figure with state median trajectories and all 15 Colorado year trajectories, README, provenance and SHA-256. It is not represented as a GitHub binary/release.

## Scientific decision

- **Case diagnosed:** suspect R=2, 50% is a replicable local nonlinearity; not a simple old-center result reuse, weather-year misalignment or missing source cases.
- **Still required for causal mechanism**: hourly storage SOC, curtailment, charging and shadow prices/constraint active sets at 40/50/60%, using identical source weather years, and checking branch-crossover behavior under changed battery/storage penalty assumptions. Do not claim nonlinear mechanism proven.
- **Manuscript:** keep original 3×3 numerical findings, add this targeted robustness check in SI as an evidence-backed qualification, not a post hoc replacement.
- **Frozen:** original 1440 baseline LPs, 360 2×2 LPs, 2880 3×3 LPs, 2160 ATB sensitivity, all Paper C-2 untouched.
