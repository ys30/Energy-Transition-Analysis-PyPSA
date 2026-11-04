# Actual PyPSA Load.bus attachment settles 53-bus hypothetical EFS exposure question

**Verified real-NetCDF workflow:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41872002039

This is a source-backed negative control against overinterpreting prior hypothetical annual EFS×LAF exposure. It reads the real Western 10,157-bus topology archive and **three already constructed 2030/2040/2050 PyPSA load-bearing NetCDF networks**, not hypothetical generated objects. The source code in `efs_real_load_attachment_pilot.py` chooses the **first extant bus for each state × ReEDS zone**, attaches one zonal `Load`, and does **not** create an independent Load on every bus with positive source `Pd`.

## Verified actual source-network results

| Attribute | 2030 | 2040 | 2050 |
|---|---:|---:|---:|
| Total original Load components | 20 | 20 | 20 |
| Dynamic 8,760-hour Load components | 19 | 19 | 19 |
| Static-only Load components | 1 | 1 | 1 |
| Distinct Load.bus IDs | 20 | 20 | 20 |
| Load components attached to any of 55 original positive-`Pd` zero-degree buses | **0** | **0** | **0** |
| Load components attached to 53 eleven-state-in-scope positive-`Pd` zero-degree buses | **0** | **0** | **0** |
| Loads on any Line+Transformer zero-degree bus | **0** | **0** | **0** |
| Loads outside largest Line+Transformer connected component | **0** | **0** | **0** |
| Actual archived annual EFS pilot demand | 274.706987 TWh | 306.839207 TWh | 350.871475 TWh |
| Annual demand actually attached to 53 positive-`Pd` zero-degree source buses | **0 MWh** | **0 MWh** | **0 MWh** |

The three years use the **same set of 20 original bus IDs**. The archive's source cohort includes 55 positive-`Pd` Line+Transformer-degree-zero source buses, of which 53 are in the chosen 11 EFS state labels and 2 are Texas; 877 Line+Transformer zero-degree source buses in total. No `Load.bus` in any of the three networks overlaps with that 55-bus set, even including the two Texas buses. Every attached Load occurs within the largest Line+Transformer graph component. This is not a physical feasibility, branch rating or full AC/DC power flow result.

### What this validates and what it corrects

A separate [state×LAF sensitivity screen](verified_efs_53_positive_pd_source_exposure_and_state_concentration.md) reported **8.965, 9.946, 11.388 TWh** of hypothetical 53-bus exposure in 2030/2040/2050. That screen deliberately multiplied full 11-state EFS annual source demand by the original bus LAF using **exported** state labels. **Those numbers are not actually attached to the 53 source buses in the archived seven-state zonal pilot**, and must not be labeled lost demand, stranded power, actual network imbalance, or actual EFS pilot bus allocation.

The current load-only pilot instead attaches 20 zone-level Loads and picks existing bus targets according to first-bus ordering. This guarantees no outage or physically accurate load location by itself: it has *not* independently authenticated demand point-of-delivery or the historical `full_state` source denominators. The full 11-state four-state candidate extension and actual UTC alignment are still not independently validated.

The first end-to-end CI attempt failed by treating all 20 Load components as hourly dynamic series. The original archived network stores **19 dynamic profiles plus one static-zero Load component**. CI was repaired to account for both types and to require all static-only missing hourly values to be represented by finite source `p_set`; negative control tests then passed. A second failed unit-test fixture had omitted static `p_set` and was repaired before the successful real-NetCDF run. These changes did **not** modify any archived NetCDF or upstream EFS source input.

## Reproducibility

- Program: `src/energy_transition/efs_archived_actual_load_bus_overlap.py`
- Tests: `tests/test_efs_archived_actual_load_bus_overlap.py`
- Workflow: `.github/workflows/efs-archived-load-bus-overlap.yml`
- Archived source: [run 41281576025](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41281576025), artifact `real-western-base-network-attempt`, includes actual `efs-real-2030/2040/2050-local-hour-load-only.nc` files
- New evidence artifact: `efs-archived-2030-2050-actual-Load-bus-source-overlap`, [run 41872002039](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41872002039)

## Next justified experiment

**Do not redesign the network or modify the source 53 nodes on the basis of the hypothetical 8.97–11.39 TWh.** Instead, check whether 20 first-bus zone Load targets are stable under source topology reorder and are suitable physically and geographically; if they are not, propose an independently documented target-bus crosswalk or explicit source-Pd-weighted allocation with source-provenance gates. Validate the eleven-state spatial extension separately. None of this establishes the historical EIA-860 generator POI fleet or a 2030–2050 calibrated Western OPF.
