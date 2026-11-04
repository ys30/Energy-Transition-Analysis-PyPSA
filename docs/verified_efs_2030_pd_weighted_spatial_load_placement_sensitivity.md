# Verified 2030 EFS spatial load-placement sensitivity: first-bus vs original positive-Pd distribution

**Successful original-NetCDF calculation:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41874208815

This experiment starts with **previously verified actual 2030 seven-state EFS load-only NetCDF** from archived PyPSA-USA Western network build [run 41281576025](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41281576025). It is a *source-data spatial-placement counterfactual* and a rigorous energy-conservation test. It does **not** rebuild or overwrite the original network and does **not** solve OPF or validate utility load points.

## Experiment designs

**Baseline — original actual PyPSA attachment:** for each exported `state × ReEDS zone`, the historical pilot attaches the entire zone's 8,760-hour EFS source-derived zonal Load to the first existing original source bus. There are **20 Load components** (19 dynamic hourly and one static-only zero).

**Candidate — Pd-weighted connected multi-bus distribution:** keep the exact original hourly zonal demand, but calculate bus shares `w_b = Pd_b / Σ_(c in connected, Pd>0, same source zone) Pd_c` among strictly positive, finite upstream `Pd` buses that belong to the **largest Line+Transformer graph component** of the archived 10,157-bus network. For zones with no such candidates, explicitly retain the original first-bus target as a 100% fallback. This is a read-only matrix/distribution comparison, not a NetCDF mutation or a dispatched model.

The program checks each zone's sum of candidate bus weights equals 1, reconstructs its original hourly demand using those weights, then checks all 8,760 hours of total demand equal the baseline. Candidate bus IDs and full-precision shares are saved per source zone; no true physical load location is asserted.

## Actual 2030 archived results

| Real-source audit metric | Verified |
| --- | ---: |
| Original Western network buses | **10,157** |
| Original pilot zonal Load components | **20** |
| Baseline Load targets with original `Pd=0` | **10** |
| Zones with connected, positive upstream `Pd` candidates | **19** |
| Explicit fallback zones with no such candidate | **1** |
| Zones with some load shifted from original first-bus representative | **19** |
| Annual baseline demand | **274,706,987.114 MWh** |
| Annual multi-bus candidate demand | **274,706,987.114 MWh** |
| Identical *each-hour* zone and total demand | **yes** |
| Cumulative source-load amount allocated to a different model bus than the baseline | **273,648,153.496 MWh** |
| Fraction of original load reallocated to other source bus IDs in this counterfactual | **99.6146%** |

The large **99.61%** spatial-reallocation fraction is a consequence of contrasting an *entire-zone-on-one-bus model* against a multi-bus distribution, not evidence of physical load relocation, operational instability or infrastructure inadequacy. The counterfactual may still be geographically or electrically inappropriate because positive original `Pd` and graph connectivity alone **do not verify utility delivery-point locations**. Original `Pd` is an upstream demand-disaggregation attribute and is not the 2030 EFS target demand.

For example, `EFS_2030_p13_Arizona` has **zero original zonal annual MWh**, and zero connected positive-Pd candidates. It is retained at the original node; a blanket rule to replace every first-bus load with a positive-Pd bus would fail for this genuine zero-demand pilot zone.

The entire 20-zone alternative-share table including original bus IDs, original source `Pd`, candidate bus IDs and their source-Pd normalized weights is uploaded in the Actions artifact `efs-2030-pd-weighted-vs-firstbus-source-placement`.

## Interpretation relative to prior low-voltage audits

The source-backed [actual Load.bus audit](verified_actual_efs_load_bus_overlap_53_zero_degree_nodes.md) separately established that **none** of the 53 original positive-`Pd`, degree-zero, low-voltage source buses had a Load attached in the original 2030/2040/2050 seven-state EFS NetCDF. The present counterfactual **excludes** graph-isolated nodes and thus does not move any load onto those 53 buses. It tests a *different* issue: whether concentrating each EFS zone's load at a single arbitrary first-indexed bus is a robust placement assumption.

The full eleven-state extension and candidate CA/NV/OR/WA geography are **not admitted**; this experiment covers only the original seven numerically accepted source-weighted states. It does not correct DST/UTC or historical `full_state` normalization, does not link real EIA-860 generators to approved electrical POIs, and does not measure transmission congestion, dispatch cost, emissions or reliability.

## Reproduction

- Code: `src/energy_transition/efs_pd_weighted_bus_placement_sensitivity.py`
- Tests: `tests/test_efs_pd_weighted_bus_placement_sensitivity.py`
- Workflow: `.github/workflows/efs-pd-weighted-placement-sensitivity.yml`
- Successful run: [41874208815](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41874208815)
- Data artifact: `efs-2030-pd-weighted-vs-firstbus-source-placement`, containing `efs_2030_zone_firstbus_vs_source_pd_candidates.csv` and `efs_2030_zone_firstbus_vs_source_pd_summary.json`.

## Next decisive test

To assess potential *electric network consequences*, implement an **appropriately calibrated generator scenario and branch rating provenance** before comparing actual power flows or production cost. Prior to that, a useful non-OPF engineering follow-up would compare a limited candidate rule (single connected positive-Pd bus per zone) against the full Pd-weighted distribution; that would separate *single-bus selection* effects from *spatial distribution* effects without mistaking either for a utility-approved load crosswalk.
