# Verified actual EFS seven-state Load attachment and source representative-bus selection audit

## Two real-NetCDF validations passed

1. [Actual 2030/2040/2050 Load.bus × 53 isolated source-node overlap](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41872002039): re-imported all three **previously archived** load-only PyPSA NetCDF files from run 41281576025. Each year contains 20 Load components (19 dynamic time-series and 1 static-only zero), 8,760 local-hour ordinal snapshots and 20 distinct selected Load.bus identities. **No** Load in any year attaches to the 55 original source-positive-Pd, Line+Transformer graph-isolated buses; all 20 Load targets lie in the largest undirected Line+Transformer connected component. The actual archived seven-state demand totals are 274.706987, 306.839207 and 350.871475 TWh respectively. This proves that the **hypothetical** 8.965/9.946/11.388 TWh eleven-state exported-state×LAF exposure is **not attached demand or lost load in these seven-state pilot networks**.
2. [Actual 2030 representative-bus selection QA](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41872759268): the original loader `efs_real_load_attachment_pilot.py` chooses the **first bus by existing index order** for each `state × reeds_zone`, not a source-Pd, voltage, utility delivery, substation or geography-based placement. The actual 2030 archive contains **20** Load targets; all 20 exactly match this first-bus selection rule, while **10 of the 20 selected buses have source `Pd=0`**, despite 19 of the 20 zones having at least one different source-connected positive-Pd candidate. None of the 20 representative targets is offshore-flagged, of graph degree zero, or outside the largest graph component.

## Actual 2030 zone placement diagnostic

| Metric | Observed |
|---|---:|
| Archived base network buses | 10,157 |
| Original 2030 seven-state EFS Load components | 20 |
| Load targets matching first-indexed bus in the exported state × ReEDS zone | **20** |
| Selected Load targets with original `Pd=0` | **10** |
| Selected Load targets on graph degree-zero buses | **0** |
| Selected Load targets outside largest Line+Transformer connected component | **0** |
| Selected Load targets with offshore source flag | **0** |
| EFS zones containing a connected, positive-`Pd` alternative source bus | **19** |
| Utility-authenticated source load delivery points | **0 verified** |

Example: `EFS_2030_p31_New Mexico` is placed at saved model bus `2040690`, where original `Pd=0`; the same exported state-zone group has **138** source buses with positive `Pd` and membership in the main Line+Transformer graph component. This demonstrates *non-uniqueness of candidate load placement*, not that the first-index bus is necessarily a physically wrong utility delivery point. Note that `Pd` is an upstream demand-disaggregation attribute, not measured 2030 EFS bus demand.

A special case is Arizona `p13`: its current first-bus target has `Pd=0` and **zero** other connected source buses with positive `Pd` in the source zone, so a simple blanket rule “switch to largest Pd” would fail. Blindly replacing every first-bus selection with the largest-Pd bus would thus not be an admissible source-backed solution.

## Scientific implications

- The already built *seven-state* EFS pilot does **not** contain the hypothesized positive-Pd low-voltage zero-degree bus demand; it does contain **order-dependent representative-bus placement** across one Load per selected state×zone. It is appropriate as a numerical load attachment and NetCDF roundtrip proof, not verified spatial delivery of demand.
- A physically meaningful future model needs independently validated demand delivery-point geography or a transparent zone-to-bus disaggregation with audited weights and topology constraints. Consider a **separate candidate placement sensitivity**, preserving original 2030/2040/2050 EFS hourly zonal sums exactly, before replacing any official source artifacts.
- The full **11-state** candidate geography is not yet admitted, and actual DST/UTC alignment, utility generator POI assignment, future generation fleet and reliable dispatch/cost models remain unresolved.
- Do not publish the prior hypothetical 8.965–11.388 TWh as confirmed stranded energy; it is a discarded-as-real-demand *screening sensitivity* only.

## Reproduction

- Actual archived Load.bus QA: `src/energy_transition/efs_archived_actual_load_bus_overlap.py` with `tests/test_efs_archived_actual_load_bus_overlap.py` and `.github/workflows/efs-archived-load-bus-overlap.yml`. CI output artifact `efs-archived-2030-2050-actual-Load-bus-source-overlap`.
- Actual source representative-bus selection QA: `src/energy_transition/efs_actual_representative_load_bus_audit.py`, `tests/test_efs_actual_representative_load_bus_audit.py`, `.github/workflows/efs-representative-load-bus-audit.yml`. CI output artifact `efs-2030-actual-representative-load-bus-qa`, including 20 bus-level rows with original `Pd`, `LAF`, voltage, graph degree and number of alternative connected positive-`Pd` buses.

No original EFS source, base NetCDF, archived load-only network, or existing published optimization result was altered.
