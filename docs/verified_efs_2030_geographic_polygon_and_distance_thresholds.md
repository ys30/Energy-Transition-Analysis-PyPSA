# Verified 2030 EFS placement: Natural Earth state polygon checks and source-distance thresholds

## Completed, passing official-source CI

- **GIS polygon overlay:** [run 41876120938](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41876120938), 20 original first-bus Load placements versus 20 single max-original-positive-Pd candidates; each checked with independent Natural Earth 10m US state polygons. Source geometries are current downloaded archive bytes, not verified original cartopy cache from the upstream build.
- **Distance threshold census:** [run 41878146215](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41878146215), preserves exact original seven-state **2030 274,706,987.114 MWh** and original 20 zone Load IDs. Distances are Haversine between candidate synthetic bus point coordinates, **not** path lengths or load movements.
- Latest Portfolio Pages build [41878450440](https://github.com/ys30/ys30.github.io/actions/runs/41878450440) passed.

## Independent state polygon audit

| Source load-placement rule | Zone records | Candidate buses not covered by matching *exported-state* polygon |
| --- | ---: | ---: |
| Original **first-indexed** zonal bus | 20 | **1** |
| Alternative connected, single largest positive-source-Pd bus | 20 | **0** |

**Only original mismatch in this polygon overlay:** `EFS_2030_p28_Arizona`, original first-indexed bus `2040000`; Natural Earth returned **no match among the seven study states** for its point. The alternative max-positive-Pd bus `2040003` is included in the Natural Earth Arizona polygon. This zone's original 2030 annual Load is **71,277,837.594 MWh**, representing approximately **25.95%** of the 274,706,987.114 MWh seven-state pilot annual demand. This is the *size of source load whose representative point is flagged*, **not** misallocated, unserved or lost electricity.

The `p31` New Mexico candidate IDs `2040690` and `2080000`, despite **505.655 km** point separation, are **both** within the independent Natural Earth New Mexico state polygon. Thus distance alone did not establish a cross-state mismatch in this case.

The independent GIS process has **not** recovered the original cached `full_state` labels or a utility-certified ReEDS load-delivery geographic mask; it cannot prove that an original source bus lies in the wrong physical service territory. Detailed border-distance and all-US-state overlay for `2040000` remain priorities.

## Threshold-based candidate placement uncertainty

| Candidate first-bus versus max-Pd separation | Number of zones with separation above threshold | Original annual EFS demand in those zones | Share of 274.707 TWh |
| --- | ---: | ---: | ---: |
| >25 km | 19 | 274.707 TWh | 100.00% |
| >50 km | 15 | 199.656 TWh | 72.68% |
| >100 km | 13 | 194.592 TWh | 70.84% |
| >200 km | 7 | 141.780 TWh | 51.61% |
| >300 km | 5 | 125.619 TWh | 45.73% |
| >400 km | 3 | 60.653 TWh | 22.08% |
| >500 km | 1 | 22.047 TWh | 8.03% |

The median candidate distance remains **153.832 km**, the original-load-weighted mean **233.039 km**, and maximum **505.655 km**. These numbers quantify geographic *sensitivity to representative source bus selection*, **not** generator/electric transmission performance or physical electricity movements.

## Next experiment and admissibility gates

1. For the Arizona `p28` pair, resolve the **actual** archived bus coordinates, independent Natural Earth classification among **all US states** and nearest Arizona-border distance using a suitable projected CRS; record whether the original node lies near a border, in a neighboring state, or outside available US polygons.
2. Independently validate exported `state` and `reeds_zone` against original network source history and, if available, a pinned ReEDS planning region polygon. Passing the state polygon alone does **not** prove correct ReEDS-zone membership.
3. Preserve the seven-state original 2030–2050 Load-only NetCDF artifacts untouched. The max-Pd alternative remains a hypothetical source comparison, not an approved replacement.
4. Before a calibrated Western 2030–2050 OPF, still resolve dynamic generation, authenticated electrical POIs, electrical equipment ratings, cost inputs and UTC source alignment.

**Scientific bottom line:** both arbitrary first-bus selection and max-source-Pd selection exhibit pronounced spatial modeling uncertainty; independent state polygons identify one concrete original candidate requiring investigation, not a proven grid outage or solved system failure.
