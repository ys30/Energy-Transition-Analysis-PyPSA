# Equal-energy, different-shape renewable supply sensitivity on verified EFS ordinal demand

## Research question

At a fixed renewable **nameplate-to-local-zonal-peak** ratio and the same *annual available renewable MWh*, how much can merely changing the assumed hourly shape of renewable supply affect **modeled** unused available renewable energy, dispatched energy, firm generation, and toy variable costs?

This extends the [successful constant-50%-availability 8,760-hour EFS pilot](efs_ordinal_full_year_illustrative_supply_screen.md), which already established source-backed demand for **seven states and 20 zones** across 2030/2040/2050. It remains an **uncalibrated assumption sensitivity**, not a measured solar/wind or WECC electricity-network result.

## Inputs and experimental controls

- **Real input:** Original verified seven-state hourly EFS/LAF zonal CSV from run `41281576025`, keeping *source* `LocalHourID=1...8760`, with its SHA-256 recorded by the new script.
- **Years:** 2030, 2040, 2050.
- **Renewable nameplate scenarios:** 0.3, 0.6 or 0.9 times each zone's annual peak MW (nine year × capacity cells).
- **Three synthetic availability-shape treatments**, applied only to ordinal `h`:
  - `flat_50pct`: `cf(h)=0.50`
  - `ordinal24_wave_A`: `cf(h)=0.50+0.35 cos(2π(h−1)/24)`
  - `ordinal24_wave_B`: `cf(h)=0.50−0.35 cos(2π(h−1)/24)`
- Across 8,760 ordinals, each synthetic profile has **exactly 0.5 mean** and therefore **identical renewable available MWh at the same zonal nameplate**, even though supply-demand ordinal coincidence differs.
- **Backup and pricing assumptions:** independent firm capacity 120% of zone peak, variable cost $5/MWh renewable vs $90/MWh firm. No storage, interzonal trade, capex or investment.
- **Calculation:** cheap assumed renewable supply is dispatched up to local demand; excess assumed available energy is classified as *model unused renewable energy*, with remainder supplied by illustrative firm backup. Explicit MW-to-MWh arithmetic uses unit 1-hour ordinal steps.

**Critical semantics:** 24-ordinal periodicity is a reproducible mathematical intervention only. `LocalHourID` is not verified physical UTC, daylight-saving policy or hour-ending time. `ordinal24_wave_A/B` **must never be called actual solar, wind, day/night, daily irradiance or observed peak timing**. There are no independently sourced renewable time-series in the experiment.

## Test and CI acceptance

The [27-case workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-ordinal-supply-shapes.yml) checks input keys and all 8,760 hours; zero missing/nonfinite/negative demand; strict supply-demand and renewable-availability balance; invariant annual available renewable MWh across all three shape treatments within each year/capacity cell; and absence of any real-OPF/UTC admission. Regression tests additionally inject a missing, duplicated, and negative source record.

Outputs: `efs_supply_shape_equal_energy_27_scenarios.csv`, `efs_supply_shape_assumption_summary.csv`, and `efs_supply_shape_assumptions.json` (including input SHA256). **Source-run result:** [Actions run #42099467157](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42099467157) **PASSED** with 27 scenario records and all conservation/equal-annual-energy assertions. This is a verified calculation using source-backed demand and explicitly synthetic supply, *not* a validated renewable-production outcome.

## Validated numerical findings (90% hypothetical renewable nameplate / zone peak)

| Year | Assumed hourly shape | Modeled renewable share | Unused hypothetical renewable energy | Toy variable cost |
|---|---|---:|---:|---:|
| 2030 | flat 50% | 72.998% | 2.200 TWh | $7.679 billion |
| 2030 | ordinal24_wave_A | 64.373% | 25.893 TWh | $9.693 billion |
| 2030 | ordinal24_wave_B | 68.061% | 15.763 TWh | $8.831 billion |
| 2040 | flat 50% | 73.003% | 2.460 TWh | $8.575 billion |
| 2040 | ordinal24_wave_A | 64.374% | 28.934 TWh | $10.826 billion |
| 2040 | ordinal24_wave_B | 68.064% | 17.614 TWh | $9.864 billion |
| 2050 | flat 50% | 73.009% | 2.817 TWh | $9.804 billion |
| 2050 | ordinal24_wave_A | 64.377% | 33.104 TWh | $12.379 billion |
| 2050 | ordinal24_wave_B | 68.067% | 20.154 TWh | $11.278 billion |

For **2030** at identical hypothetical zone-level nameplate and **identical annual renewable available energy**, switching flat availability to `ordinal24_wave_A` decreases modeled renewable energy share by about **8.63 percentage points** and increases the hypothetical unused amount by **23.693 TWh**, under this deliberately disconnected-zone design. This is a sensitivity of the **assumptions**, not a prediction of actual system curtailment or costs.



## Interpretation and next research

If the synthetic shapes differ in model curtailment and firm dispatch while holding available MWh constant, this shows a **sensitivity/identifiability issue in simplified planning models**, not measured renewable curtailment, economic savings, or reliability outcomes. Physical interpretation requires independently sourced time-aligned renewable profiles and the unresolved EFS timezone/DST/2040-leap-year convention. Model credibility then requires sourced zone-to-zone transmission capacity and plant/interconnection evidence.

These experiments can support a methodology-oriented paper section on assumption dependence and data admission gates; they cannot substantiate operational Western-grid decarbonization or annual wind/solar benefit claims.
