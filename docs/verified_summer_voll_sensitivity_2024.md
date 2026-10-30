# Verified summer 2024 storage sensitivity to value of lost load (VOLL)

Source: successful [GitHub Actions run 41003214458](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41003214458), artifact `summer-voll-storage-sensitivity-2024`, file `summer_voll_sensitivity.csv`.

A 1-GW/4-GWh battery is independently reoptimized at $1,000, $5,000, $10,000 and $20,000 per MWh assumed unmet-load penalty. Each run uses the **same VOLL in the battery and no-battery counterfactual**; this corrects an earlier invalid comparison. The demand is the same 168-hour EIA-930 CAISO/BPAT summer sample, and generator capacities/costs are illustrative.

| VOLL ($/MWh) | Unserved with battery (MWh) | Avoided unserved (MWh) | Penalty avoidance ($M) | Other dispatch savings ($M) | Total objective savings ($M) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1,000 | 315,022 | 22,179 | 22.179 | -3.207 | 18.972 |
| 5,000 | 315,022 | 22,179 | 110.895 | -3.207 | 107.688 |
| 10,000 | 315,022 | 22,179 | 221.790 | -3.207 | 218.583 |
| 20,000 | 315,022 | 22,179 | 443.580 | -3.207 | 440.373 |

For all four scenarios, modeled battery discharge is 25,979 MWh and SOC energy conservation error is below 3e-13 MWh. The shortage-volume response is identical over these four tested penalties; the monetary value changes nearly linearly because it is calculated using a chosen penalty. This does not prove robustness outside these four values or under realistic network/renewable constraints.

**Policy:** These are assumed scenario-objective differences, **not** measured market prices, observed blackout losses, electricity arbitrage revenue, verified capacity value, annualized benefits, or battery investment returns. The model still leaves 315,022 MWh unserved in the summer battery case.
