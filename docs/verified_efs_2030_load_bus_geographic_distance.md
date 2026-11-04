# Verified geodesic sensitivity of 2030 seven-state EFS load bus placements

**Source-backed end-to-end CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41875462614

## Experimental source and exact scope

The archived 10,157-bus PyPSA-USA Western network provides original `x` and `y` source bus coordinates. Previously [CI-verified 2030 EFS three-method allocation](verified_efs_2030_three_spatial_load_placement_rules.md) compares the first-indexed zonal bus with a *single* largest original positive-`Pd` main-graph bus (among other counterfactuals). This new analysis joins the two actual archived original bus IDs per 20 zone-level EFS Load records back to the original source-network coordinates and computes **Haversine straight-line distance**. It does not perform routing along transmission lines or alter the original network.

## Verified geographic differences

| Measurement | Real original source-network result |
| --- | ---: |
| Original seven-state EFS planning year | 2030 |
| Original zone-level Load records | 20 |
| Zones with a different single max-source-`Pd` bus ID | 19 |
| Zones with positive annual EFS load | 19 |
| Median distance over all 20 zone records | **153.8318 km** |
| Load-weighted mean distance | **233.0393 km** |
| 90th percentile among 19 positive-load zones | **405.7760 km** |
| Maximum straight-line geographic distance | **505.6548 km** |
| Original verified annual load, unchanged | **274,706,987.114 MWh** |
| Independently certified utility delivery points | **0** |
| Real OPF solved or generator POI approved | **no** |

### Four examples

| Source zone Load | Original first source bus | Candidate max-Pd bus | Straight-line separation |
| --- | --- | --- | ---: |
| `EFS_2030_p31_New Mexico` | `2040690` | `2080000` | **505.65 km** |
| `EFS_2030_p25_Utah` | `2040602` | `2050099` | **416.14 km** |
| `EFS_2030_p18_Montana` | `2077004` | `2077101` | **403.18 km** |
| `EFS_2030_p34_Colorado` | `2060000` | `2060508` | **384.45 km** |

**Important anomaly for follow-up:** The candidate `2080000` in the New Mexico `p31` exported source zone lies at approximately **31.8555°N, -106.703°W**, while the first-bus location is approximately 35.9839°N, -109.002°W. This merits a separate state and zone geographic polygon check; the current screen does **not** independently certify that either location belongs to the correct real-world load-serving region. Do not claim a verified state mismatch based on ID alone.

## Scientific interpretation

The already verified first-bus versus max-source-`Pd` scenario relocates **100% of nonzero zonal modeled source load to other candidate source bus IDs**; this analysis measures the geographic magnitude under the candidate rule. The high distance numbers do **not** show that electricity actually moves hundreds of kilometres, that transmission lines have those lengths, that one variant is better, or that any physical branch-flow or reliability outcome changes.

Original `Pd`, `state` and `reeds_zone` are imported source attributes, not individually verified utility demand-delivery sites. The pinned network's synthetic-topology-derived origin and the already documented state/LAF boundary anomalies mean assigning EFS demand by simple source-`Pd` maxima can be as geographically arbitrary as selecting the first index. **The supported result is placement-model uncertainty, not source-qualified alternative load mapping.**

## Reproducibility

- Source: `src/energy_transition/efs_2030_load_bus_geographic_distance.py`
- Regression: `tests/test_efs_2030_load_bus_geographic_distance.py`
- Workflow: `.github/workflows/efs-load-bus-geographic-distance.yml`
- Successful run: [41875462614](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41875462614)
- Data artifact: `efs-2030-source-firstbus-maxpd-geodesic-sensitivity` with 20-row `efs_2030_single_max_pd_geographic_bus_distance.csv` and summary JSON.

## Next source-based decision

**Do not replace the original first-bus Load assignment with max-`Pd` simply because it passes graph-connectivity and numerical-conservation gates.** First add a state polygon and receiving-zone consistency test for the 20 candidate pairs, especially New Mexico `p31`; investigate source metadata and the actual source `full_state` denominator. Only after that could one justify a geographic load-delivery-site rule and physically grounded 2030–2050 OPF.
