# First source-pinned ReEDS polygon overlay for 20 EFS seven-state Load buses

**Original raw ReEDS Shapefile provenance:** [PyPSA-USA pinned source 338af9912addbaf038c6098fe27e1e6ef099d8aa](https://github.com/PyPSA/pypsa-usa/tree/338af9912addbaf038c6098fe27e1e6ef099d8aa/workflow/repo_data/geospatial/Reeds_Shapes), specifically the full five-part `rb_and_ba_areas.{shp,shx,dbf,prj,cpg}` GIS dataset. Its original `rb` field is the source ReEDS region ID, and pinned upstream `workflow/scripts/build_shapes.py` renames `rb` to `name` before **later** interconnection trimming.

**First full source polygon CI success:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41960027199

**Second independent source raw-polygon boundary-distance forensic success:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41960343309

The fixed-commit original raw ReEDS GIS has **134 distinct original `rb` polygon IDs**. We evaluated both original first-indexed and one hypothetical connected maximum-positive-source-`Pd` candidate bus for each of **20 original seven-state 2030 EFS pilot Load zones**. The original EFS load-only pilot preserves exactly **274,706,987.114 MWh** of 2030 annual demand, with no NetCDF edits or real OPF dispatch.

## Main raw ReEDS polygon result

| Archived source load placement rule | 2030 EFS zone Load records | Bus candidates outside same-named original `rb` polygon | Original annual zonal EFS demand associated with flagged candidate |
| --- | ---: | ---: | ---: |
| First indexed existing source bus per `state × reeds_zone` (actual archived seven-state pilot rule) | 20 | **2** | **76,998,293.697 MWh = 76.998 TWh** |
| Single connected source bus with largest original positive `Pd` (hypothetical alternative) | 20 | **0** | **0** |

The **two original source polygon mismatches** are:

| Original source Load zone | Source first-bus ID | Raw source polygon matches | Source label raw polygon distance (EPSG:5070 projection) | Candidate max-`Pd` bus | Original annual zone EFS demand |
| --- | --- | --- | ---: | --- | ---: |
| Arizona `p28` | `2040000` | No raw polygon; nearest raw `p28` | **0.5780 km** | `2040003`, inside raw `p28` | **71.277838 TWh** |
| Montana `p18` | `2077004` | **`p19`** | **38.9735 km** from raw `p18` | `2077101`, inside raw `p18` | **5.720456 TWh** |

Coordinates were retrieved directly from pinned original archived Western base network: Arizona `2040000` at (32.4567°N, 114.689°W), candidate `2040003` at (32.6839°N, 114.616°W); Montana `2077004` at (48.0622°N, 106.889°W), candidate `2077101` at (46.6663°N, 111.831°W).

**Montana is the stronger source-zone discrepancy signal:** the original chosen Load bus is *inside a different raw ReEDS region* (`p19`) rather than merely falling outside all source polygons near a mapped border. Independent raw GIS indicates `p18` is about 39 km from this archived first-bus location. The pinned PyPSA-USA pipeline subsequently performs **county-majority reassignment** of ReEDS membership and interconnection clipping, so this raw-polygon mismatch is not sufficient to declare the final `reeds_zone` invalid, or justify moving all 5.720 TWh to the candidate `2077101` location.

**Arizona is a near-border source-shape sensitivity:** its original first-bus coordinate is only 578 m from the pinned raw ReEDS `p28` polygon, and the previous independent Natural Earth state polygon study found a different ~264 m separation from Arizona's state boundary. These are different administrative and ReEDS geographic masks. Neither establishes real 2030 load delivery or an electricity supply failure.

## What was verified versus what remains

Verified: original same-commit raw polygon files, source bus point coordinates, source `reeds_zone` tags, 20 original EFS zone Load IDs, original annual zonal demand, independent Shapely polygon covers and EPSG:5070 raw-boundary distance; successful unit tests + real GitHub Actions artifacts.

**NOT verified**: original post-trim network ReEDS shapes as used at final runtime, original county-majority reassignment recomputation for `p18`, real utility load delivery sites, actual physically meaningful electrical assignments, full eleven-state state×ReEDS EFS mapping, historical generator POI and calibrated 2030–2050 Western OPF.

Do not confuse **76.998 TWh of zonal energy associated with two flagged *representative bus coordinates*** with 76.998 TWh of misplaced, stranded, unserved, or physically relocated electricity. These are not estimates of grid failure or model dispatch errors.

## Reproduction

- Main: `src/energy_transition/efs_2030_pinned_reeds_polygon_overlay.py`, `tests/test_efs_2030_pinned_reeds_polygon_overlay.py`, `.github/workflows/efs-pinned-reeds-polygon-overlay.yml`; artifact `efs-2030-20-source-load-buses-pinned-reeds-original-polygon-evidence`
- Forensic: `src/energy_transition/efs_two_raw_reeds_boundary_forensic.py`, `tests/test_efs_two_raw_reeds_boundary_forensic.py`, `.github/workflows/efs-two-raw-reeds-boundary-forensic.yml`; artifact `efs-original-two-reeds-raw-boundary-forensics`

## Next highest-value validation

Trace exact original `county` and `reeds_zone` of Montana `2077004`, then rerun the **pinned PyPSA-USA county-majority rule** against source archived bus labels. If the reassignment explains the `p19`-polygon to `p18`-network label, retain and document it as a model choice; otherwise flag as unresolved GIS source crosswalk. The final load-delivery and OPF admission still depend on utility-backed load centres, credible demand profiles, branch ratings, and generator POIs.
