# Paper S — source-backed 2030 storage sizing incremental economic frontiers (11 Nov 2026 UTC)

## Verified provenance and results

- Original authenticated four-state 2012 county wind/PV instantaneous CF: GitHub Actions run [42962740548](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42962740548).
- Successful [180 original HiGHS LP solutions](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43051615043), 2030 projected demand, 2012 weather reference, 3 hypothetical renewable ratios × 3 wind-PV source-nameplate mixes × baseline and 4 storage designs.
- Successful source-archive post-processing [144 incremental sizing design pairs](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43055466036), **72 fixed-storage-power 4→8h comparisons** and **72 fixed-storage-duration 10→25% of peak demand power comparisons**, each matched on state, 2030 source demand, renewable nameplate ratio, wind MW share and 2012 weather approximation.
- Artifacts: `paper_s_reeds2022_72_incremental_4h_to_8h_fixed_power.csv`, `paper_s_reeds2022_72_incremental_10_to_25pct_fixed_duration.csv`, and `paper_s_reeds2022_144_incremental_storage_design_manifest.json`.

## Prespecified representative case (2030, ratio 1.5× peak, wind source-MW share 50%)

| State | 4→8h incremental variable-cost saving USD/year | Incremental energy kWh | Conditional energy-only break-even $/kWh-year | 10→25% peak MW incremental saving USD/year | Conditional power-only break-even $/kW-year |
|---|---:|---:|---:|---:|---:|
| AZ | 76,756,534.780 | 19,405,000 | 3.955503 | ~105,282,700 | 36.170289 |
| CO | 20,810,090.470 | 11,454,000 | 1.816840 | ~29,134,310 | 16.957285 |
| ID | 6,727,986.280 | 5,204,000 | 1.292849 | ~9,492,355 | 12.160332 |
| WY | 4,315,881.974 | 3,069,000 | 1.406283 | ~5,487,196 | 11.919617 |

The duration comparison adds energy capacity without altering charge/discharge power, so the energy-only threshold is `ΔS/ΔE`. The power comparison holds **duration fixed at 4h** and thus adds both power and energy (`ΔE=4h×ΔP`). Its power-only threshold is conditional on **zero** marginal energy cost; the more realistic two-part investment frontier is `A_power + 4 × A_energy ≤ ΔS/ΔP`, with `A_power` in $/kW-year and `A_energy` in $/kWh-year.

For the entirely illustrative additional energy-capacity cost $10/kWh-year, extending 4→8h fails the conditional hurdle in all four central state cases. This only tests a simplified variable operational objective, not actual installed cost, battery finance, capacity credit, market value, emissions, or reliability. A longer duration could still have unmodeled value.

## Model scope and publication restrictions

- All renewable resource CF values are source-derived from 2012 fixed-CST ReEDS county capacity-weighted profiles, not real installed fleet generation or projected future weather. Hour-averaged renewable output relies on a **trapezoidal numerical assumption** with first-hour endpoint fallback, never manufacturer/publisher-verified hourly integrated energy.
- Hypothetical wind + PV nameplate denominator mixes wind and solar source-MW conventions (wind generally AC, solar MW_DC). The 50% wind share is **not** a common AC MW ratio. A consistent AC basis must be modeled and audited before quantitative mix-optimality claims.
- The original 180 LPs assume 90% battery round-trip efficiency, no grid network/flows, no resilience/capacity adequacy/ancillary service values, illustrative generator costs and no storage CAPEX, depreciation or fixed O&M in the solver objective.
- The value in the incremental CSV is the modeled **maximum annualized cost that can be supported solely by avoided variable operating cost**. It is not NPV, payback, IRR, real utility procurement recommendation, or an investment-cost forecast.
- Full repository CI remains separately impacted by the Paper T synthetic test's helper API mismatch; the specific storage-sizing Actions workflow passed.

## Manuscript candidate claim

**The economic interpretation changes substantially when incremental rather than total storage operating value is considered.** Adding 4 hours of duration yields positive operational savings under the selected scenarios, but a low per-kWh-year incremental investment hurdle, challenging extrapolation of 4h storage value to 8h installations. A broader 2030 resource mix and penetration sweep with explicitly declared source-capacity bases underlies the data.

Next: add plots of marginal energy-cost hurdle by wind share, penetration and storage power; check a common AC-normalized PV basis; run cost and efficiency sensitivity for investment-grade conclusions. Do not silently merge new 2012 weather-based analysis with frozen older EFS2020 synthetic experiments.
