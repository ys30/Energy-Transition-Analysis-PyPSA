# Verified Arizona p28 EFS original-bus polygon near-boundary sensitivity

**Real 20-zone Natural Earth audit:** [successful run 41876120938](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41876120938).

**Independent Arizona p28 projected boundary-distance audit:** [successful run 41887672429](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41887672429), artifact `efs-2030-arizona-p28-original-bus-border-distance-review`.

The first independent seven-state Natural Earth 10m polygon overlay returned **one source exported-state mismatch among 20 original first-bus Load representatives**, `EFS_2030_p28_Arizona` on source network bus `2040000`. The alternative `2040003` was within Arizona. A separate follow-up has now retrieved the archived source coordinates and independently tested **all-US-state** matching and projected point-to-polygon distance using EPSG:5070.

| Verified source attribute | Original first bus | Alternative single max-positive-Pd candidate |
| --- | --- | --- |
| Archived source bus ID | `2040000` | `2040003` |
| Source latitude | 32.4567°N | 32.6839°N |
| Source longitude | 114.6890°W | 114.6160°W |
| Contained within downloaded Natural Earth Arizona polygon | **No** | **Yes** |
| Other Natural Earth US state matches | None | Arizona |
| Minimum projected point-to-Arizona-polygon distance | **0.263784 km (264 metres)** | **0.0 km** |
| Original zone 2030 EFS annual source demand | 71,277,837.594 MWh | The **same** original zone source demand; only hypothetical location differs |

**Interpretation update:** The original point lies **just 264 metres from the independent Arizona polygon boundary**, not hundreds of kilometres away in a different US state. This is a *near-boundary GIS classification sensitivity*, not evidence that 71.278 TWh is incorrectly located or lost. The precise boundary source and geographic mask used in the historical `full_state` upstream PyPSA-USA build remain unrecovered. The 71.278 TWh is the *entire modeled zone's annual energy*, not an inferred fraction on the wrong side of the actual service border.

### Engineering next steps

1. Treat `2040000` as an **independent-polygon near-boundary review**, not an automatically invalid source node. Compare a reasonable 0.5–1 km border tolerance only as **sensitivity**, not as a license to reclassify into the Arizona electricity grid.
2. Compare original upstream `full_state` and ReEDS source-zone geometry; check data vintage, shapefile projection and source bus coordinate accuracy.
3. Keep the already verified 2030/2040/2050 source NetCDF files and EFS demand untouched. Neither this test nor a candidate within the Arizona polygon certifies utility point-of-delivery.
4. For materially larger zone placement uncertainty, the [real distance analysis](verified_efs_2030_geographic_polygon_and_distance_thresholds.md) documents 7/20 zone candidate pairs >200 km, covering 51.61% of original pilot annual EFS demand. This remains a *source-model sensitivity* without actual path-flow validation.

### Reproduction

- Source: `src/energy_transition/efs_arizona_p28_border_distance_review.py`
- Tests: `tests/test_efs_arizona_p28_border_distance_review.py`
- Workflow: `.github/workflows/efs-arizona-p28-border-distance.yml`
- Original 20-pair coordinate artifact: [41875462614](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41875462614), `efs-2030-source-firstbus-maxpd-geodesic-sensitivity`.

**Model admission gates:** independent US-state polygon result != original upstream `full_state`; independent state coverage != ReEDS zone/load-delivery certification; hypothetical max-Pd load representative != physical grid optimum; no historical EIA-860 generator POI or full 2030–2050 OPF was solved.
