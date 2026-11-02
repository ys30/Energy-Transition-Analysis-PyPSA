# Verified matched priority EIA-860 generator capacity, 2023–2024

Source: [successful matching workflow 41483089717](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41483089717) and [main CI 41483089438](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41483089438).

| Comparison | Value |
|---|---:|
| Common prioritized plant IDs | 71 |
| Plant-generator IDs present in both original-year audit files | 133 |
| OP-only 2023 MW within common prioritized plants | 5,590.5 |
| OP-only 2024 MW within common prioritized plants | 5,843.1 |
| OP capacity change among common priority plants | **+252.6 MW** |
| Identical generator IDs that are OP in both years, 2023 nameplate MW | 5,514.3 |
| Identical generator IDs that are OP in both years, 2024 nameplate MW | 5,534.3 |
| Same continuously OP generator capacity difference | **+20.0 MW** |
| Independently verified source-network electrical ties | 0 |

The two differences answer **different questions**. The +252.6 MW includes changes in which generators are OP within the common *plant* sample. The +20 MW applies only to matched generator IDs with OP status in both years. Do not label either as western-system growth, annual generation change, or empirical PyPSA dispatch.

Data quality: matching is by `plant_id + generator_id`, from official EIA-860 yearly source inventories, and the OP supply gate requires source sheet `Operable` and status `OP`. The output CSV and JSON are downloadable under GitHub Actions artifact `eia860-matched-generator-capacity`. Network-bus connection remains unverified; dispatch admission stays false.

Next: Decompose the +252.6 MW into continuing OP unit uprates, entries to OP, departures from OP, and units observed in only one year's audited inventory. Keep capacity baselines and network connectivity evidence separate.
