# Independent U.S. Census border-bus evidence for four-state EFS candidate

**Verified GitHub Actions:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41765291701

This audit independently overlays exact coordinates from the archived pinned PyPSA-USA Western network with the **U.S. Census Bureau's official 2023 TIGER/Line state polygon file**, not a model-derived region map. The archived 2023 state ZIP has SHA256 `8ded0ef036e205e246ae4b03a66873f7e1eed50285b993702ce5aca674283a2e`; the workflow now asserts that digest and observed state assignments to fail closed if underlying source bytes or analytical results drift.

| Source bus ID | Archived current state | Inferred LAF denominator source state | Official 2023 Census polygon containing the bus | Approximate 2023 border distance |
| --- | --- | --- | --- | ---: |
| `2030005` | Nevada (county code `p32031`; p12/NEVP) | California (Pd denominator 67028.96) | **California** | **198 m** |
| `2013019` | Washington (county code `p53049`; p2/BPAT) | Oregon (Pd denominator 9281.36) | **Oregon** | **4,417 m** |

The Census polygon matches **both** independently inferred LAF denominator source states; both *disagree* with the archived network's later `state` labels. The Washington-labeled source bus is about 4.4 km inside Oregon, substantially beyond a 1 km border ambiguity threshold. The Nevada-labeled source bus is only ~198 m into California, making the exact polygon vintage and coordinate representation especially consequential. Distances were computed after projecting to EPSG:5070 in meters. No coordinates, state labels or original LAF values were modified.

## Strength of evidence and limits

- **Independently verified**: 2023 official state polygon membership of the **exported** bus coordinates. This is external spatial corroboration of the earlier `Pd/LAF` denominator hypothesis.
- **Not independently verified**: original dropped PyPSA-USA `full_state` attribute, exact vintage/geometry used by the pinned upstream network builder, source year, and the downstream EFS state-to-ReEDS allocation policy. Modern Census polygons may differ from the project's source GIS. These are separate variables.
- **Not authorized**: swapping bus geography in the published NetCDF or admitting the CA/NV/OR/WA candidate weights as an empirical, geographically certified EFS mapping.
- **Still required for operating results**: audited simultaneous source-hour UTC semantics; wind/solar/generator profiles; physical line/branch transfer and zone-vintage compatibility; network calibration.

The existing **11-state** EFS candidate conservation and mixed-offset peak sensitivity stays a **source-backed engineering comparison**, not a fully verified Western energy-transition outcome.

## Reproduce

Module `src/energy_transition/efs_cross_bus_official_polygon_audit.py`; tests `tests/test_efs_cross_bus_official_polygon_audit.py`; workflow `.github/workflows/efs-cross-bus-census-geography.yml`. Authoritative download: `https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip`; derived JSON: `outputs/efs-cross-bus-census-2023-evidence.json` in Actions artifact `efs-cross-bus-independent-census-geography`.

**Next scientific gate:** inspect the pinned network's original `na_shape`/state-shape geometries and GIS assignment order to explain why the final `state` labels disagree with the original normalization keys, then independently audit ReEDS zone eligibility. A numerical source-state sum equal to 1 does not establish that an 11-state scenario is fit for empirical PyPSA dispatch.
