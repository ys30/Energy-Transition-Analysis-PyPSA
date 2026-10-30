# Verified 2024 full-year chronological battery gap-fill sensitivity

Source: successful [GitHub Actions #41080248923](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41080248923), artifact `annual-storage-gap-sensitivity-2024`, `annual_2024_storage_fill_sensitivity.csv`.

Three independently optimized 8,784-hour 2024 cases use complete observed EIA-930 demand for CISO/BPAT, signed EIA-930 wind and solar generation with 55 *explicitly imputed* missing BA/fuel/hour values across 31 unique hours, 55 GW assumed firm ($50/MWh), 20 GW assumed peaker ($250/MWh), and a 1-GW/4-GWh battery. Each battery case has an identical no-battery counterfactual with the same renewable input and $10,000/MWh assumed shortage penalty.

| Metric | Linear interpolation | ±7 day same UTC hour | Missing-record zero bound |
|---|---:|---:|---:|
| Imputed BA/fuel/hour observations | 55 | 55 | 55 |
| Annual signed wind/solar observed+imputed (MWh) | 71,958,157 | 72,006,862.5 | 71,884,012 |
| Battery charging (MWh) | 558,643.221607 | 558,643.221607 | 558,643.221607 |
| Battery discharging (MWh) | 504,175.5075 | 504,175.5075 | 504,175.5075 |
| Unserved with storage (MWh) | 51,021 | 51,021 | 51,021 |
| Unserved without storage (MWh) | 73,373 | 73,373 | 73,373 |
| Avoided unmet load (MWh) | 22,352 | 22,352 | 22,352 |
| Assumed shortage-penalty savings ($M) | 223.520 | 223.520 | 223.520 |
| Other modeled dispatch savings ($M) | 92.4733 | 92.4733 | 92.4733 |
| Total modeled operating savings ($M) | 315.9933 | 315.9933 | 315.9933 |
| Peaker displacement (MWh) | 481,823.5075 | 481,823.5075 | 481,823.5075 |
| SOC conservation max absolute residual (MWh) | 4.55e-13 | 4.55e-13 | 4.55e-13 |

**Scope and interpretation**: The three missing-value assumptions change the annual renewable energy sum but not the reported battery metrics in this scenario. This is *conditional robustness* to the tested gap fills for the model as parameterized, **not** evidence of a validated annual investment benefit, historical grid reconstruction, or robustness to assumed generation capacity, value of lost load, transmission or weather. The $315.9933M objective difference contains $223.52M of *assumed* shortage-penalty avoidance. It is not electricity-market revenue, and does not subtract battery capital expenditure, augmentation or degradation. The official observed-only annual completeness gate remains **blocked** because 31 distinct 2024 UTC hours are missing; the annual results are **scenario-imputed** only.

Remaining validation: stress-test supply adequacy and shortage penalties, test terminal SOC boundary assumptions, and reconcile the assumed residual generation with EIA-860/EIA-923 before claiming investment feasibility.
