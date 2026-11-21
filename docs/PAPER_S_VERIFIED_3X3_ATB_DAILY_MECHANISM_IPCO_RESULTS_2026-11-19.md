# Paper S — SOURCE-VERIFIED 3×3 ATB threshold crossings, input-only mechanism and 2023 IPCO shape (2026-11-19)

## Authentication and status

All numbers below were independently read from the **successful** GitHub Actions runs and their actual ZIP CSV artifacts (not inferred from the narrative):
- Complete 3×3 economic screening: run [44463644688](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44463644688), artifact **14507169113**; direct frozen 1,080-values upstream run [44209543001](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44209543001), artifact **14388326204**.
- Daily input-only transfer proxy and authentic-2023 Idaho/IPCO shape diagnostic: run [44463644188](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44463644188), artifact **14506529618**.
- CI: run **44463644825**, success.

These results do not involve new LP reoptimization: 2,880 earlier new design-grid LPs and 360 reused LPs generate 1,080 duration cases, cross-joined with 18 ATB source-driver/cost-case/discount-rate assumptions.

## 1. ATB economic screening: actual crossing counts

**Actual output manifest:** 1,080 unique 4→8-hour storage value cases, 19,440 comparisons, **954** total crossed rows (the latter includes duplicated numerical hurdles), **213 of 1,080 unique LP cases** cross at least one hurdle, **12 distinct numerical hurdle levels** under 18 labeled source assumptions. The fixed-2030-demand R=1.5/wind=50% baseline produced **0 of 2,160** threshold-crossing comparisons. IMPORTANT: the earlier historical-demand 0/120 is a separate population; neither may substitute for the other.

All rates/scenarios below correspond to the same **1,080** fixed-2030-demand LP values; counts are comparisons, not independent replications.

| 2030 ATB variant / scenario | 4% (hurdle; crossed) | 7% (hurdle; crossed) | 10% (hurdle; crossed) |
|---|---|---|---|
| Expand/R&D Advanced (identical cells) | 16.049; **213/1080** | 18.501; **133/1080** | 21.179; **93/1080** |
| Expand/R&D Moderate (identical cells) | 24.175; **38/1080** | 27.869; **0/1080** | 31.902; **0/1080** |
| Expand Conservative | 32.699; **0/1080** | 37.695; **0/1080** | 43.151; **0/1080** |
| R&D Conservative | 29.715; **0/1080** | 34.255; **0/1080** | 39.213; **0/1080** |

At Advanced/4%, 213 cases split **AZ 89, CO 60, ID 34, WY 30** (each state has 270 cases). By R and installed AC wind share:
- R1.0, all 25/50/75% wind: 0.
- R1.5: wind 25% **61/120**, wind 50% **0/120**, wind 75% **0/120**.
- R2.0: wind 25% **120/120**, wind 50% **32/120**, wind 75% **0/120**.

State-specific counts at Advanced/4% (all points have 30 year×weight cases per state):
| State | R1.5 wind25% | R2.0 wind25% | R2.0 wind50% |
|---|---:|---:|---:|
| AZ | 30 | 30 | 29 |
| CO | 27 | 30 | 3 |
| ID | 4 | 30 | 0 |
| WY | 0 | 30 | 0 |

Maximum modeled value over the 3×3 cells by state, illustrative model USD/(added kWh-year): **AZ 27.7685, CO 23.6170, ID 21.2727, WY 20.3346**.

The immediate economic result is **conditional threshold exceedance**, not demonstrated investment profitability, NPV, IRR, merchant arbitrage income, empirically calibrated real-dollar benefit-cost or economic optimality. The model's illustrative `$90/MWh` firm-unit-cost input is not independently reconciled to ATB's 2023 real dollars. Solar/wind siting and demand simplifications, fixed storage power, degradation, replacement, transmission, energy prices and omitted costs all limit generalization.

## 2. CO nonlinear value landscape

In the R2.0 3×3 design, direct actual LP source median values (not dispatch-accounting approximations):
| Wind AC share | EIA 2025 weighted median | ReEDS potential median | Median within-year paired EIA minus potential (from full grid) |
|---|---:|---:|---:|
| 25% | 22.5682 | 22.7101 | −0.164 (paired median) |
| 50% | 13.2410 | 15.4189 | −2.1779 |
| 75% | 7.3213 | 4.6761 | +2.6154 |

Medians of individual schemes cannot be subtracted to reconstruct the paired median; only the last column uses within-weather-year differences. Existing independently resimulated 40/50/60% CO run 44453880808 provides additional within-valley sign diagnostic, but earlier approx −1.8/−0.3 values were inferred via accounting and must not be represented as direct objective-derived medians until source-row verified.

**Editorial:** a smooth negative interval versus wind mix is compatible with original anomalous center; the minimum's precise position cannot be claimed from sparse sampling.

## 3. Independent input-only daily surplus-deficit proxy: actual results

Verified daily experiment: 240 source cases (15 weather years × 4 states × 2 weightings × R1.5/2.0) at wind 50%, 87,600 daily rows and 120 within-year spatial pairs. Source arrays and original frozen LP outputs are independently joined. The proxy requires both surplus and deficit and is calculated without the LP; it is not an achievable shift because it excludes within-day ordering, charge/discharge power and carryover SOC.

For each state and ratio, 15 weather-year matched spatial differences (EIA minus ReEDS potential) show:

| State | R | Corr(input-only proxy difference, actual LP value difference) | Same sign / 15 |
|---|---:|---:|---:|
| AZ | 1.5 | 0.926 | 12 |
| AZ | 2.0 | 0.764 | 10 |
| CO | 1.5 | 0.643 | 13 |
| CO | 2.0 | 0.836 | 15 |
| ID | 1.5 | 0.886 | 15 |
| ID | 2.0 | 0.898 | 13 |
| WY | 1.5 | 0.974 | 15 |
| WY | 2.0 | 0.948 | 14 |

These correlations are descriptive over 15 physical source-year scenarios, not independent probabilistic trials; same demand scenario and mathematical structure remain. Proxy is a stronger *non-circular explanatory input metric* than objective-derived firm displacement, but not a causal or dispatch-feasible identification claim. Further order-aware feasibility diagnostics may be valuable.

## 4. Native 2023 IPCO observed shape comparison

EIA-930 IPCO BA generation is **not** all Idaho state wind/solar production; EIA-860 2025 operating-county state weights **are not** verified 2023 IPCO fleet weights. The original 2023 ReEDS weather indices were localized from fixed-CST source labels to UTC and aligned with authentic EIA930 UTC-hour-end observations.

For **adjusted MW, nonnegative actual source rows, UTC zero offset**, N=8,743 matched hours per fuel/scheme:

| Fuel | Source potential Pearson / normalized MAE | EIA 2025 weight Pearson / normalized MAE |
|---|---|---|
| Wind | 0.7344 / 0.4101 | 0.7335 / 0.4309 |
| Solar | 0.9539 / 0.2224 | 0.9694 / 0.1788 |

For solar, the EIA-weighted comparison is visibly closer in this proxy diagnostic; wind is marginally worse by both measures. Solar at +1-hour placebo-offset diagnostic has Pearson 0.9736 for EIA-weighted (higher than zero-lag 0.9694); this does not authorize choosing a favorable offset as actual alignment. Solar at −6h collapses to approximately zero correlation, helping detect time-label sensitivity. These are *shape* comparisons normalized by each valid-hour sample mean, not capacity calibration, 2023 physical fleet verification, or generalizable predictive skill.

## Reporting gate

Results are verified from successful GitHub artifacts, but are still **illustrative model-based**. Update Abstract, §1.6, §4.3, Results, Discussion, Conclusion as conditional economic findings, plus an explicit non-circular daily proxy and source-scope-limited IPCO diagnostic. Preserve 1,440/360/2,880/720/2,160 earlier LP work and Paper C-2. Do not merge PR#2 before manuscript consistency and source/artifact provenance audit.
