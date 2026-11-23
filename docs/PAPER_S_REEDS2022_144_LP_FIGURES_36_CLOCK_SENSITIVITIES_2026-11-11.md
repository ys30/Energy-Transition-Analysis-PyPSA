# Paper S — 144-case scale-and-hour-convention plot audit (11 November 2026 UTC)

Source artifacts:
- Original authenticated 2012 county wind/PV aggregate CF: [42962740548](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42962740548)
- 144 optimal LP scenarios, 72 exact storage pairs, regression against frozen 0.9× 48-LP baseline: [42966023512](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42966023512)
- **12 reproducible figures plus 36 timestamp-assumption sensitivity records**: [42967335330](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42967335330), success, artifact `paper-s-reeds2022-county-144-lp-source-figures-and-time-convention`.

Figures: three separate panels per state, each with 2030, 2040 and 2050 source-demand years:
- `paper_s_{AZ,CO,ID,WY}_storage_objective_savings_2012_weather.{png,pdf}`
- `paper_s_{AZ,CO,ID,WY}_no_storage_curtailment_2012_weather.{png,pdf}`
- `paper_s_{AZ,CO,ID,WY}_firm_energy_displacement_2012_weather.{png,pdf}`

The time-convention sensitivity artifact has 36 comparisons (4 states × 3 demand years × 3 modeled renewable nameplate ratios). Maximum absolute difference of percent savings between end-instant and trapezoidal hour-average approximations is **0.3613869911 percentage points** over these 36 comparisons; this is a numeric model sensitivity, not uncertainty interval or original publisher validation.

Interpretation: higher hypothetical renewable nameplate shares produce more no-storage curtailment and higher modeled four-hour battery objective savings in the four target states. This is a mechanism hypothesis supported by controlled model scenarios, not observed causal treatment effects or financially net-positive investment estimates.

**Not calibrated:** actual 2030–2050 wind/PV installed or dispatched fleet, battery capital/fixed/degradation costs, network and capacity adequacy, or physical hour-average generation observations. The solar+wind model uses 2012 source weather, 50/50 MW mix and illustrative energy prices. The first trapezoidal time interval uses an explicitly artificial endpoint fallback, no cyclic wrap. Avoid claims of publisher-certified demand/weather energy alignment.

Repository full CI remains red due to a separate synthetic Paper T helper API mismatch, `paper_t_directional_v3.py` expecting `net_peak_clock_hour` and `solar_overlap_fraction` while the underlying `paper_t_robustness.calculate()` returns `net_peak_hour` and `overlap_pct`. That file is on main but not in the present PR branch tree, so avoid merging an ad hoc duplicate into this Paper S branch. Follow up on the Paper T branch independently.

Figure outputs are the new source-specific Paper S supplement candidates, not replacements for frozen earlier EFS2020 p-zone figures.
