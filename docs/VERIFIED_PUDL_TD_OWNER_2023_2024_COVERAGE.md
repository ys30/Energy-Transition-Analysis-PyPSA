# Verified PUDL transmission/distribution owner enrichment (2023 and 2024)

Source: [successful PUDL owner workflow run 41402271820](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41402271820) at commit `5d302a1152291463a9b9a8321507f50af3d85bb7`; main [CI 41402271910](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41402271910) also succeeded.

| Verified workflow output | 2023 | 2024 |
|---|---:|---:|
| Reviewed priority plants | 84 | 84 |
| Matched PUDL yearly plant records | 84 | 84 |
| Plant records with non-null owner ID and owner name | 83 | 83 |
| Owner identity coverage within reviewed records | 98.81% | 98.81% |
| Independently verified plant-to-source-network electrical connections | 0 | 0 |
| Real-generator dispatch admitted | **No** | **No** |

The PUDL source is the current nightly Parquet asset and is **not yet pinned to an immutable release**. The successful run downloaded from the dotted S3 bucket using path-style TLS-safe addressing; do not disable certificate checking. Outputs under artifacts `pudl-td-owner-evidence-2023` and `pudl-td-owner-evidence-2024` retain plant ID, T&D owner and `G1_owner_only` / `G0_geographic_only` tiers.

A PUDL owner identity identifies a research direction (utility/owner and region) but not the point of interconnection, voltage-specific substation, or an original source-network bus. Do **not** inject generators into calibrated dispatch from owner matching alone.

Next: pin the PUDL publication snapshot, identify the single missing-owner case in each year from archived output, and search official interconnection sources to progress individual plants from G1 to POI-level G2 and source-network-bus-level G3 only when independently corroborated.
