# Verified 2023–2024 matched priority-generator OP capacity decomposition

**Evidence:** [GitHub Actions matched-capacity run 41487686930](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41487686930), success at commit `5c7eaffea8af53ba994035a9135932addb31f0f7`. [Main CI run 41487686978](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41487686978), success.

| Generator transition class | Year-union generator rows | OP MW (2023) | OP MW (2024) | Delta MW |
|---|---:|---:|---:|---:|
| Continuing OP | 108 | 5,514.3 | 5,534.3 | +20.0 |
| Entered OP | 4 | 0 | 308.8 | +308.8 |
| Exited OP | 4 | 76.2 | 0 | -76.2 |
| Neither year OP | 18 | 0 | 0 | 0 |
| **Total** | **134** | **5,590.5** | **5,843.1** | **+252.6** |

Population: 71 common prioritized plant IDs. **133 generator keys occur in both year files**, while the outer join contains 134 unique generator keys in the union: one generator key is recorded in only one year's audit. Rows are plant-generator identities, not entire power plants.

Strict interpretation: capacity is original EIA-860 year-end nameplate for generator-year entries with source-sheet Operable and reported status OP; in-year generation may differ. The net change is for this **nonrepresentative, jointly prioritized subpopulation** only; it is not a regional fleet trend, causal analysis, dispatch result, verified interconnection, or annual electricity generation.

The machine-readable decomposition and matched individual generator rows are in the workflow artifact `eia860-matched-generator-capacity`. The decomposed changes reconcile exactly to the CI-verified +252.6 MW total. **Zero** original network generator-to-bus electrical ties independently verified. Do not admit these OP units to empirical PyPSA dispatch without external POI and bus evidence.

Future analyses: separate the 4 entering OP IDs by previously proposed vs absent-year record, the 4 exiting IDs by retirement vs absent-year record, examine status codes and the one one-sided row. Retrieve official EIA forms and status codes at original source vintage to ensure defensible labels.
