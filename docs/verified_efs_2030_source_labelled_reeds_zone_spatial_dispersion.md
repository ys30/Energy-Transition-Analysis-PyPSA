# Verified original-source ReEDS-labelled EFS zone bus dispersion

**End-to-end, real archived Western network CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41926602723

This experiment directly loads the original **10,157-bus synthetic-derived Western NetCDF** from the previously accepted PyPSA-USA base network and the verified 20-Load, first-bus versus single-max-positive-source-Pd 2030 EFS zone comparison. It computes the coordinate distribution of **all original source buses** in each exported `state × reeds_zone` label group, not only the two candidates.

Each source group is summarized by the **median latitude/longitude**, and Haversine distances of all buses and candidate placements from that descriptive coordinate-median point. This center is **not a geometrical polygon centroid, a utility load centroid, or an externally validated ReEDS-region geometry**.

## Verified real-network results

| Source spatial diagnostic | Result |
| --- | ---: |
| Original seven-state pilot 2030 EFS Load zones | **20** |
| Total unchanged archived zonal annual EFS demand | **274,706,987.114 MWh** |
| Source first and alternative bus share same exported `state × reeds_zone` labels | **20/20** |
| First-index bus farther than max-Pd from source bus coordinate median | **12/20** |
| Max-Pd bus farther than first-index from source bus coordinate median | **7/20** |
| First and max-Pd same source bus ID | **1/20** |
| Median across 20 zone-level *90th percentile source-bus coordinate radius* | **209.505 km** |
| Haversine separation between first and max-Pd, median | **153.832 km** |
| Haversine separation between first and max-Pd, maximum | **505.655 km** |

The single unchanged case is Arizona `p13` (zero annual EFS load); its 20 archived zone-label source buses share essentially the same coordinate and its source coordinate radius p90 is zero. The **12 vs 7** split is descriptive geometry, not an optimization criterion: the source `Pd` maximum and the bus median location may each be unrelated to actual load-serving locations.

### Selected original source zones

| Source EFS zone | Archived source buses | Source-bus 90%-radius | Original first-bus distance to label-group median | Max-source-Pd distance to label-group median | Between-candidate distance |
| --- | ---: | ---: | ---: | ---: | ---: |
| New Mexico `p31` | 308 | **322.29 km** | 229.69 km | 356.59 km | 505.65 km |
| Arizona `p28` | 792 | 257.75 km | 275.40 km | 259.73 km | 26.17 km |
| Colorado `p33` | 610 | 206.28 km | 331.70 km | 22.51 km | 326.70 km |
| Colorado `p34` | 287 | 295.87 km | 379.95 km | 38.68 km | 384.45 km |
| Utah `p25` | 412 | 355.41 km | 393.21 km | 24.06 km | 416.14 km |

These values reveal wide **source-label-defined** regional geographic spreads. The source label and state are inherited from the pinned upstream mapping pipeline; **this study does not independently overlay a ReEDS region polygon nor prove the label is geographically correct**.

The separate [independent Natural Earth 10m Arizona p28 review](verified_efs_2030_arizona_p28_precise_border_distance.md) found the original Arizona `p28` first-bus `2040000` only **0.264 km** outside the downloaded state polygon, so it is a *near-border external-GIS sensitivity* rather than proven misallocation of that zone's 71.278 TWh annual EFS load.

## What the result changes

- Source-zone membership equality is **necessary but not sufficient** for a defensible physical electricity delivery-point crosswalk.
- Large distances between first and max-Pd source buses are not automatically cross-zone misassignment; the source group itself can span hundreds of kilometres.
- Centrality in source bus points does not prove electric load geography, because bus placement density and generator-terminal representation may bias the coordinate median.
- Do **not** change archived 2030/2040/2050 seven-state Load-only NetCDF or publish calibrated dispatch until the ReEDS zone polygon source and external load delivery evidence are available.
- The full eleven-state 2030–2050 candidate and future generator fleet still lack independently authenticated spatial, UTC, electrical POI, supply and branch-rating compatibility.

## Reproduction

- Code: `src/energy_transition/efs_source_zone_bus_spatial_dispersion.py`
- Tests: `tests/test_efs_source_zone_bus_spatial_dispersion.py`
- GitHub Actions: `.github/workflows/efs-source-zone-spatial-dispersion.yml`
- Source-data verified CI: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41926602723
- Output artifact: `efs-2030-source-labelled-zone-bus-spatial-dispersion`, with full 20-row CSV and summary JSON.

**Research next step:** obtain pinned original ReEDS region polygon geography, establish source state-zone metadata concordance including county/zone assignment history, and build a real load-center/demand disaggregation reference. Only then compare actual network dispatch under identical generation assumptions.
