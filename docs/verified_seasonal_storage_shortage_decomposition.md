# Verified four-season storage benefit decomposition (2024 pilot)

Source: successful [GitHub Actions run 40995850141](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/40995850141), artifact `seasonal-storage-sensitivity-2024`, `seasonal_storage_sensitivity.csv`. All 16 cases use four distinct observed 168-hour EIA-930 load windows, a 1-GW assumed battery, 2/4/6/8-hour duration, illustrative generation and a $10,000/MWh unserved energy penalty.

## Summer week: modeled benefits dominated by avoided shortage penalty

| Battery duration (h) | Total modeled operating savings ($M) | Avoided unserved energy (MWh) | Avoided shortage penalty ($M) | Remaining non-shortage dispatch cost change ($M savings) | Unserved with storage (MWh) |
|---:|---:|---:|---:|---:|---:|
| 2 | 112.834 | 11,400 | 114.000 | -1.166 | 325,801 |
| 4 | 218.583 | 22,179 | 221.790 | -3.207 | 315,022 |
| 6 | 311.096 | 31,679 | 316.790 | -5.694 | 305,522 |
| 8 | 403.463 | 41,179 | 411.790 | -8.327 | 296,022 |

The no-storage summer run had **337,201 MWh** of unserved demand. In the 4-hour case, $221.79M of modeled shortage-penalty avoidance is offset by approximately $3.21M more other dispatch expense. These values are *scenario-objective accounting*, not electricity prices, energy-market revenue, measured avoided outage costs, or lifecycle investment returns.

## Other weeks

Winter 2/4/6/8h operating savings: $4.143M/$7.314M/$9.537M/$10.225M; spring: zero in all configurations; autumn: $2.217M/$4.265M/$6.113M/$7.960M. None of these three selected weeks had unserved energy in either the no-storage baseline or battery scenario.

## Interpretation gate

- Do not annualize four selected weeks, add them as an annual benefit, or treat summer savings as normal energy arbitrage.
- The summer case is **shortage-affected** and its result should always be labeled `includes_high_assumed_unserved_energy_penalty`.
- Spring zero dispatch is a valid solution, not a failed experiment.
- A future robust adequacy study needs realistic chronological dispatch, actual hourly renewable output, geographic transmission bounds, storage costs and credible shortage valuations.
