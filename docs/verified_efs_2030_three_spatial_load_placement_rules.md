# Verified 2030 EFS three-method spatial load-placement sensitivity

**Real archived source-data CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41874208815

**Three-method source-bounded comparison CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41874891129

## Exactly what is compared

The initial seven-state source EFS model has **20 zone-level Load components** with original 2030 local-ordinal 8,760-hour time series and **274,706,987.114 MWh annual load**. Its original load-attachment algorithm picks the **first existing network bus by index ordering** in each source state × ReEDS zone.

We compare:
1. **First-bus baseline:** original source demand at exactly its archived first-indexed bus, unchanged.
2. **Single largest original positive-Pd main-graph bus:** keep each region's *entire existing hourly* demand at one main Line+Transformer connected source bus with the largest original `Pd`, choosing the original first-bus target only if no eligible positive-`Pd` alternative exists.
3. **Multiple original positive-Pd main-graph buses:** distribute each region's *same hourly* demand among all eligible connected source buses proportionally to their original `Pd`, with the same explicit fallback.

Both alternatives are modeling assumptions for source-defined *candidate* load sites, not utility-authenticated points of delivery; no network or generator component was modified and no OPF was run.

## Numerically verified sensitivity

| Original 2030 source metric | First bus | Single max-Pd bus | All connected positive-Pd buses |
| --- | ---: | ---: | ---: |
| Existing zone-level Loads | 20 | 20 source zones | 20 source zones |
| Regions with potential changed load location | — | 19 | 19 |
| Zones with no eligible source bus and explicit fallback | — | 1 | 1 |
| Original archived annual demand | 274.706987 TWh | **274.706987 TWh, unchanged** | **274.706987 TWh, unchanged** |
| Archived annual demand assigned to a different *candidate bus ID* from first-bus baseline | — | **274.706987 TWh** | **273.648153 TWh** |
| Share of annual modeled load placed at different source bus IDs from baseline | 0% | **100.000%** | **99.6146%** |
| Each source-zone hourly EFS total preserved | yes | yes | yes |
| Historical source bus/branch network changed | no | no | no |
| Calibrated physical OPF solved | no | no | no |

The one fallback is original Arizona `p13`, which has **zero original annual EFS pilot demand**, no connected positive-source-`Pd` candidates and remains at its original bus under both alternatives. Thus 19 of 20 zones change possible placement and 100% of nonzero annual demand could change bus ID in the single-max-Pd scenario.

The ~99.6% multi-bus relocation fraction is not an error, but follows from the contrast of the old single-bus allocation with a distributed allocation. The 100% single-max-Pd result is particularly clarifying: even **without** distributing a zone's load over multiple nodes, changing the arbitrary first-bus selection changes the possible source-bus coordinates for all nonzero EFS pilot demand. This is a **high spatial representation sensitivity**, not power-flow impacts or literal load being moved in a grid.

## Audit methods and artifacts

The earlier real-NetCDF [first-bus vs multi-bus CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41874208815) produced complete source bus IDs, source-`Pd` shares and original annual zonal loads, while enforcing exact hourly source demand conservation. The new `src/energy_transition/efs_single_max_pd_vs_multibus.py` compares the baseline with both alternatives using that **immutable CI-produced CSV**. It validates the 20 source-zone identities, nonnegative finite share sums, unchanged original zonal annual demand, candidate bus identity and explicit no-positive-source-bus fallback.

- Code: `src/energy_transition/efs_single_max_pd_vs_multibus.py`
- Tests: `tests/test_efs_single_max_pd_vs_multibus.py`
- Workflow: `.github/workflows/efs-three-bus-placement-rules.yml`
- Source artifact: `efs-2030-pd-weighted-vs-firstbus-source-placement`, run 41874208815.
- New artifact: `efs-2030-three-source-bus-placement-rules`, run 41874891129, including 20-row `efs_2030_three_bus_placement_rules.csv` and numeric summary JSON.

## Interpretation limits

This comparison does not validate whether any proposed alternative node is a real physical load point. Original source `Pd` is a demand-disaggregation coefficient and not actual 2030 demand at that bus; neither source `Pd` nor topological membership proves physically accurate electricity delivery. The source topology is a synthetic system and the original load pilot is **seven-state, ordinal-local-hour-only**, not the full independently admitted eleven-state EFS forecast. Original EFS `full_state` normalization details, UTC/DST, future generation, EIA-860 generator POI, real network ratings and full OPF remain unresolved.

A high relocation fraction alone cannot establish line-flow changes, congestion or a better physical model. The next meaningful steps are to validate zone-to-bus delivery-point provenance, document the raw original bus/branch and `Pd` classification, and only then compare physically admissible power flow results under independent generation assumptions.
