# Verified origin of 157 missing Western network LAF factors

**Evidence:** [GitHub Actions run 41762974412](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41762974412) and [cross-bus geography run 41763059308](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41763059308).

## Root cause is source construction order, not missing future demand files

The immutable PyPSA-USA `338af9912addbaf038c6098fe27e1e6ef099d8aa` source performs, in order:

1. Compute `group_sums = gdf_bus.groupby("full_state")["Pd"].transform("sum")`
2. Compute `LAF_state = Pd / group_sums` and remove `full_state` from export
3. Build the base buses and transmission branches
4. Call `add_offshore_buses(n, offshore_buses)`, which sets `Pd=0` and `substation_off=True`, but **does not set `LAF_state`** and copies geographical attributes from onshore POI buses
5. Apply subsequent ReEDS assignment and regional filtering

All **157** null-LAF buses in the saved 10,157-bus Western NetCDF satisfy *simultaneously*:
- `substation_off=True`;
- IDs in the source-generated offshore range starting at `3008161`;
- finite `Pd=0`.

The geographical distribution is California **111**, Oregon **26**, Washington **20**. The pinned upstream source-order explanation and all 157 matching node signatures are reproducible in `src/energy_transition/efs_null_laf_offshore_origin_audit.py`. The audit does not assume their future system role, impute their LAF, or modify source data.

The **practical inference** is that a future bus-level allocation eligibility mask could explicitly exclude these post-LAF offshore auxiliaries, *if the mask is kept source-specific and separately audited*. It is **not** a license to replace all arbitrary null values with zero. Shore-to-offshore generation connections and full geography validation remain a separate task.

## Exact cross-denominator buses, exported geography

| ID | Present `state` | ReEDS zone / BA | County code | Lon / Lat | Pd | Source-denominator inference |
| --- | --- | --- | --- | --- | ---: | ---: |
| `2030005` | Nevada | p12 / NEVP | p32031 | -120.003 / 39.7699 | 34.99 | 67,028.96 (California group) |
| `2013019` | Washington | p2 / BPAT | p53049 | -123.962 / 46.2056 | 17.49 | 9,281.36 (Oregon group) |

These are **exported current labels**, not the dropped original `full_state` field. The buses retain `LAF_state` factors tied numerically to California and Oregon original denominators, respectively. The mismatches account precisely for **Nevada's 0.00052201317** and **Washington's 0.00188442211** extra LAF mass relative to their current state groups, and corresponding California/Oregon shortfalls. No bus is reclassified yet; the geographic source and demand-key policy need validation.

## Engineering gate to advance safely

1. Add a **source-revision-specific offshore auxiliary mask**, requiring **all** identifying attributes and confirming exactly 157 on this frozen artifact. Treat excluded offshore nodes as outside the *eligible demand allocation set* without writing synthetic coefficients into the original network.
2. Review the two borderline bus locations against original `full_state` source polygon/county overlay and applicable EFS state demand keys. Do not auto-reassign based solely on a matching denominator.
3. Recompute four-state **candidate** state→ReEDS-zone allocation with mass-conservation and geospatial provenance reports, retaining original `Pd/LAF` for traceability.
4. Only after source-approved geography and demand conservation, independently reconcile +7/+8 fixed clock shifts, then perform combined 11-state temporal and source-data checks; a 35-zone calibrated OPF remains a later stage.

**Current result:** the missing-factor origin is explained and two interstate-denominator discrepancies are localized. Full four-state EFS demand admission and empirical Western OPF remain blocked, and no reported EFS loads were changed.
