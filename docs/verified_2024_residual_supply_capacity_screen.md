# Verified EIA-860 2024 capacity screen for illustrative residual supply

Source: successful [GitHub Actions run 41082411566](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41082411566), artifact `residual-supply-capacity-screen-2024`, audited `eia860_model_subset/ba_operating_nameplate_by_fuel_2024.csv` from historical end-to-end artifact [run 40964541770](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/40964541770).

| 2024 CISO + BPAT category | EIA-860 supported BA nameplate (MW) |
|---|---:|
| Thermal/nuclear fuel categories | 38,521.3 |
| Hydro and geothermal | 28,576.1 |
| Thermal/nuclear/hydro/geothermal subtotal | **67,097.4** |
| Wind and solar nameplate | 33,261.4 |
| Existing assumed residual firm supply | 55,000.0 |
| Existing assumed residual peaker supply | 20,000.0 |
| Assumed residual total | **75,000.0** |
| Assumed minus supported thermal/nuclear capacity | +36,478.7 |
| Assumed minus supported thermal/nuclear/hydro/geothermal capacity | **+7,902.6** |

The 75-GW assumed residual supply is **not calibrated** to these EIA-860 BA data. Neither 38.5 GW (thermal/nuclear) nor 67.1 GW (with hydro/geothermal) represents **dependable hourly** output: fuel classes and EIA nameplate do not classify resource commitment, seasonal hydro availability, plant outages, reserves or price/merit order. Existing separately observed EIA-930 signed wind/solar injections must not be double-counted. Supported fuel subsets exclude some resources and storage; do not claim these are total physical BA nameplate capacities.

**Actionable calibration gate:** preserve the 75-GW assumptions as illustrative and do not label the previously computed $315.99M annual modeled operating objective difference as an observed, BA-calibrated reliability or investment result. Next, allocate exact generator/technology classes and hourly availability using matched 2024 EIA-860/EIA-923 data and independently justify cross-BA deliverability before optimizing a revised capacity mix. EIA-923 monthly net generation is an energy benchmark, not proof of 24/7 availability.
