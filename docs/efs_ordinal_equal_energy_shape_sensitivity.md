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

Outputs: `efs_supply_shape_equal_energy_27_scenarios.csv`, `efs_supply_shape_assumption_summary.csv`, and `efs_supply_shape_assumptions.json` (including input SHA256). **Treat empirical numerical values as preliminary until the GitHub workflow has passed and logged all cases.**

## Interpretation and next research

If the synthetic shapes differ in model curtailment and firm dispatch while holding available MWh constant, this shows a **sensitivity/identifiability issue in simplified planning models**, not measured renewable curtailment, economic savings, or reliability outcomes. Physical interpretation requires independently sourced time-aligned renewable profiles and the unresolved EFS timezone/DST/2040-leap-year convention. Model credibility then requires sourced zone-to-zone transmission capacity and plant/interconnection evidence.

These experiments can support a methodology-oriented paper section on assumption dependence and data admission gates; they cannot substantiate operational Western-grid decarbonization or annual wind/solar benefit claims.
