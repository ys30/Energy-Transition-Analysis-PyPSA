# Verified 2024 annual battery robustness: generation adequacy, VOLL and terminal SOC

Evidence: successful [GitHub Actions #41080855535](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41080855535), artifact `annual-battery-robustness-2024`, CSV `annual_robustness_comparison.csv`; corresponding CI [#41080855469](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41080855469) passed.

All cases solve the same 8,784-hour 2024 EIA-930 demand, signed wind/solar net generation with 55 **explicitly imputed** missing BA/fuel/hour records, and a 1-GW/4-GWh assumed battery. Assumed marginal costs are $50/MWh firm, $250/MWh peaker and $0.10/MWh battery discharge. Each battery solve is compared with a no-storage solve sharing the same supply limits, VOLL and renewable injection.

| Case | Assumed firm / peaker GW | VOLL ($/MWh) | Cyclic SOC | Avoided unmet load (MWh) | Shortage-penalty avoidance ($M) | Other dispatch savings ($M) | Total modeled operating savings ($M) | Battery discharge (MWh) |
|---|---|---:|---|---:|---:|---:|---:|---:|
| Reference | 55 / 20 | 10,000 | No | 22,352 | 223.520 | 92.473 | 315.993 | 504,175.5 |
| Lower VOLL | 55 / 20 | 1,000 | No | 22,352 | 22.352 | 92.473 | 114.825 | 504,175.5 |
| More supply | 65 / 30 | 10,000 | No | 1,000 | 10.000 | 38.237 | 48.237 | 197,879.0 |
| Cyclic SOC | 55 / 20 | 10,000 | Yes | 22,352 | 223.520 | 92.473 | 315.993 | 504,175.5 |

With more assumed supply, unmet demand with storage falls to 343 MWh and the no-storage comparison to 1,343 MWh, versus 51,021 and 73,373 MWh in the reference. Modeled total operating savings fall ~84.7% ($315.99M to $48.24M). Under lower VOLL, modeled battery dispatch is unchanged at the tested values, but the monetary value of shortage avoidance changes sharply. All four cases end at approximately 0 MWh battery SOC and storage conservation residual <5e-13 MWh.

## Interpretation

The $315.99M reference is *not* independently robust to plausible differences in **assumed** electricity supply and shortage valuation. Neither higher supply nor the four VOLL values is a measured historical reliability calibration; these are counterfactual model choices. The reported sensitivity uses **linear interpolation** of the missing 55 wind/solar BA/fuel/hour records, not a fully observed renewable year. These modeled savings are not energy-market profits, battery NPV or net economic benefits. Battery capex, augmentation/degradation and transmission limits remain unmodeled. EIA-860/EIA-923 resource-to-BA reconciliation and verified source data are necessary before making investment claims.

The unchanged cyclic SOC result tests one boundary alternative only and does not prove longer-run robustness to reservoir/storage initialization or degradation.
