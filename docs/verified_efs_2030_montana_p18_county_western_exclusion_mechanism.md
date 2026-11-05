# Verified ReEDS Western exclusion mechanism and Montana p18 source-label discrepancy

**Pinned upstream source:** PyPSA-USA commit `338af9912addbaf038c6098fe27e1e6ef099d8aa`, `workflow/scripts/build_shapes.py` and `workflow/scripts/build_base_network.py`.

**Main exact-original ReEDS raw-polygon overlay CI:** [41960027199](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41960027199).

**Two-node exact polygon boundary forensic CI:** [41960343309](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41960343309).

**Actual archived-source county composition CI:** [41960831161](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41960831161).

**Original upstream Western exclusion parsing + real county consistency gate:** [41961146759](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41961146759).

## What we actually established

The 20 original **seven-state, 2030 EFS** Load targets are attached at the first archived bus for each exported `state × reeds_zone` and preserve 274.706987 TWh annual source demand. Exact raw original ReEDS Shapefile overlay reveals two original first-bus locations outside their namesake original `rb` polygon; all 20 hypothetical connected maximum-original-positive-`Pd` candidates are covered by their raw labelled polygon.

| Source Load | Original representative bus | Original ReEDS polygon relation | Source county `county` | Annual modeled zone EFS demand |
| --- | --- | --- | --- | ---: |
| Arizona `p28` | `2040000` | 0.578 km outside original raw `p28`; nearest zone `p28` | `p04027` | 71.277838 TWh |
| Montana `p18` | `2077004` | Within **original raw `p19`**, 38.973 km from raw `p18` | `p30071` | 5.720456 TWh |

Raw geometry and **actual archived** source county compositional audit:

| Source county | Source buses | Original single-cover raw ReEDS membership | Final archived source county-level `reeds_zone` |
| --- | ---: | --- | --- |
| Arizona `p04027` | 35 | 34 `p28`, one raw unmatched | 35 `p28` |
| Montana `p30071` | 10 | **8 `p35`**, **1 `p19`**, **1 `p18`** | 10 `p18` |

The pinned `build_shapes.py` **explicitly excludes `p35` and `p19` from the Western interconnection** while retaining `p18`. Its later shape-filter code does this before zonal mapping. Applying that **source-defined exclusion as a diagnostic** to the observed raw county membership leaves **one `p18`-covered bus among the original raw membership bins**. The pinned `build_base_network.py` also explicitly performs a county-wide `reeds_zone` mode reassignment after zonal GIS processing. Therefore **the actual saved 10/10 `p18` county labels are consistent with the pinned upstream processing sequence**. The earlier discrepancy is not, by itself, evidence of a mislabeled utility load territory.

### Crucial provenance distinction

This comparison does **not** establish the exact historical pre-county intermediate `reeds_zone` labels. The source build applies interconnection-region shape filtering and nearest/neighborhood fill behavior before county-wide mode, and the archived base NetCDF does not retain the full original intermediate labels. Thus, a demonstration that **8 raw `p35` + 1 raw `p19` are excluded in Western, leaving 1 raw `p18`** is mechanism consistency, not byte-for-byte replay of all intermediate spatial operations.

The Arizona case remains a *near-boundary* sensitivity: 34/35 county buses are covered by raw `p28`, and the remaining source first-bus is 578 m outside raw `p28`. The independently downloaded Natural Earth Arizona **state** polygon distance was approximately 264 m, which reflects a different boundary geometry.

**No 76.998 TWh of load has been proven erroneous, moved, unserved, or dispatched.** It is the sum of originally modeled EFS 2030 zonal annual demands whose selected first-bus source coordinates were flagged by a raw polygon provenance check. No actual original 2030/2040/2050 network or Load was edited.

## Reproducibility

- `src/energy_transition/efs_2030_pinned_reeds_polygon_overlay.py` / `.github/workflows/efs-pinned-reeds-polygon-overlay.yml`
- `src/energy_transition/efs_two_raw_reeds_boundary_forensic.py` / `.github/workflows/efs-two-raw-reeds-boundary-forensic.yml`
- `src/energy_transition/efs_reeds_county_majority_source_audit.py` / `.github/workflows/efs-reeds-county-majority-source-audit.yml`
- `src/energy_transition/efs_montana_p18_western_reeds_exclusion_gate.py` / `.github/workflows/efs-montana-p18-westerngis-exclusion.yml`
- All source inputs restored by GitHub Actions from immutable source archive artifacts and exact original upstream commit `338af991...`.

## Paper interpretation and next model gate

The evidence now supports reporting a **source-dependent ReEDS spatial-label ambiguity with a specific plausible upstream rule-based explanation**, rather than a proven 5.72 or 71.28 TWh physical load mismatch. A paper should distinguish raw original ReEDS geometry, postinterconnect geographic filters, final county-modified `reeds_zone`, and utility-certified load delivery polygons.

Further geographic diagnostic work has diminishing returns without independently anchored utility load-center estimates and the original postinterconnect processing archive. For a defensible 2030–2050 Western system result, the next main engineering milestone should shift to **EFS hourly demand and generator supply on a common UTC snapshot contract, independently verified electrical generator POIs and branch ratings**, followed by a jointly calibrated constrained OPF. Until then, the already solved pilot dispatch models are engineering demonstrations, not empirical Western transition forecasts.
