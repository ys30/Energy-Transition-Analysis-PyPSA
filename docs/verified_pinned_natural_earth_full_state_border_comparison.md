# Upstream-matched Natural Earth 10m verification of two EFS LAF border buses

**Successful pinned-method reconstruction:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41765906929  
**Independent Census 2023 TIGER confirmation:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41765291701

## Why the two state tags can differ

The pinned PyPSA-USA `338af9912addbaf038c6098fe27e1e6ef099d8aa` `build_base_network.py` first maps original buses to the full North America `na_shape` field `full_state` and separately maps their eventual `state` using `state_shapes`. The `full_state` field determines `LAF_state = Pd / sum(Pd by full_state)`, and is then dropped. The `state_shapes` come from an interconnection-filtered, NERC-trimmed state boundary pipeline. `reeds_state` is also subsequently adjusted by county-mode regional membership rules. These are different geographic processing steps, even though they share the Natural Earth shape family.

The pinned `build_shapes.py` `load_na_shapes()` uses Cartopy's **Natural Earth 10m cultural `admin_1_states_provinces_lakes`** polygons. We fetched that same dataset family directly at:
`https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_1_states_provinces_lakes.zip`

The downloaded ZIP has SHA256 `7c41f8aa2827c6cfbd458faff584119bb3a628047f0c4b45cff5fa071cc8a11b` and is now digest-pinned in CI.

## Real bus comparison

| Bus ID | Exported state / ReEDS | Inferred source denominator | Current Natural Earth 10m polygon | Independent Census 2023 polygon |
| --- | --- | --- | --- | --- |
| `2030005` | Nevada / p12 | California, 67028.96 | **California** | **California** |
| `2013019` | Washington / p2 | Oregon, 9281.36 | **Oregon** | **Oregon** |

All **two** Natural Earth polygon matches agree with the source-denominator hypothesis and independently collected Census state polygons. The Census border distances are ~198 m for `2030005` (California side) and ~4,417 m for `2013019` (Oregon side). These are evidence of a processing-stage attribution mismatch, **not** an arbitrary 0.0522% or 0.1884% normalization failure.

## Distinguish evidence levels

**Validated:**
- Pinned source algorithm explicitly uses `full_state` as the `Pd/LAF` denominator key.
- Current Natural Earth 10m polygons, matching the pinned algorithm's *named source GIS dataset family*, place both points in the expected source states.
- Independent official 2023 Census TIGER/Line polygons also place both points in those source states.
- Reassigned-source numerical hypothesis reconciles four CA/NV/OR/WA candidate LAF sums to 1.0; all 157 missing LAFs trace to generated offshore auxiliary buses with zero `Pd`.
- No network geometry, source LAF or EFS records were changed.

**Not yet independently validated:**
- Exact Natural Earth Cartopy shapefile **bytes and vintage** used by the archived pinned build (current source family is matching, not an immutable build-time geospatial archive).
- Original dropped `full_state` labels from the actual pre-normalization bus GIS file, plus the NERC-trimmed `state` and county-mode ReEDS assignment process at the point of generation.
- Official source-approved rules for EFS state-demand redistribution to ReEDS receiving zones, fully simultaneous UTC/DST time alignment and generation/renewables/branch topology constraints.

Therefore this is **strong external source-geography corroboration of the four-state candidate** but does not by itself admit the full 11-state EFS zonal series as calibrated Western dispatch demand.

## Reproduce

Module: `src/energy_transition/efs_cross_bus_pinned_natural_earth.py`.  
Tests: `tests/test_efs_cross_bus_pinned_natural_earth.py`.  
Action: `.github/workflows/efs-cross-bus-natural-earth.yml`.  
Artifact: `pinned-natural-earth-source-geometry-comparison/efs-two-border-buses-natural-earth10m.json`.

The GIS workflow requires the exact immutable upstream function signature and pins the newly downloaded Natural Earth ZIP's SHA, then tests each real bus' polygon membership. It never silently promotes this comparison to certified historic source geography.

**Next decisive input task:** reconstruct the pinned build's NERC-trimmed `state` shape and its overlap with `na_shape` for these two buses (including county/ReEDS membership) to derive the *mechanism* behind the later exported state labels. Then review the EFS source vintage and UTC conventions before attempting a validated network model.
