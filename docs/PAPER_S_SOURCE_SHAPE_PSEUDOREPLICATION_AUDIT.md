# Paper S — source-demand temporal pseudoreplication audit (2030/2040/2050)

**Status: VERIFIED on actual archived source dataset**, not inferred from a figure. Full 20-zone × 8,760 source-hour × 3-year run: [EFS source-shape uniqueness run #42464270811](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42464270811), success. The three-rank 27-case independent LP/source archive replication [#42463963411](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42463963411) and independent pairwise normalized demand check [#42464137879](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42464137879) both passed.

## Main audit result

For **each** planning year 2030, 2040 and 2050:

- 20 enumerated zone IDs, 19 with positive EFS-LAF projected demand, **one static-zero Arizona p13**.
- Among 19 positive-demand zones, only **seven distinct peak-normalized source-demand hourly sequences**, by maximum pairwise absolute difference <= 1e-10 on the original 8,760 `LocalHourID` ordinals within each year.
- Six positive shape groups have more than one zone, collectively representing **18** of the 19 positive-demand zones. Only New Mexico p31 contributes a singleton.
- Group *membership* is identical across the three years; **cross-year identity of normalized hourly shapes was not tested** by this within-year algorithm. Do not claim there are only seven across all years without a separate cross-year alignment test.

| Group by source-ordinal normalized shape | Original zones | Count |
|---|---|---:|
| Arizona | p27, p28, p29, p30 | 4 |
| Colorado | p33, p34 | 2 |
| Idaho | p14, p15, p16 | 3 |
| Montana | p17, p18, p20 | 3 |
| New Mexico | p31 | 1 |
| Utah | p25, p26 | 2 |
| Wyoming | p21, p22, p23, p24 | 4 |
| Separate zero-demand record | Arizona p13 | 1 |

Source code: [efs_source_normalized_shapes.py](../src/energy_transition/efs_source_normalized_shapes.py) and [unit tests](../tests/test_efs_source_normalized_shapes.py); result artifact `source-efs-20zone-three-year-normalized-shape-groups`. Groups are determined directly from the **original archived EFS-LAF hourly load**, without inspecting the model's storage outcomes.

## Three-zone precommitted replication and counterexample

The original-zone yearly-demand ranks 1, 10, 19 (zero-based 0,9,18) selected **Arizona p28, Wyoming p21, Arizona p29** in 2030. In the three source profiles, the rank-1 and rank-19 normalized demand sequences had max absolute difference **4.44e-16**, peak-scaling factor p29/p28 **~0.013758**, normalized hourly Pearson correlation **1.0**. Relative normalized difference p28 versus Wyoming p21 was **~0.502596** and correlation **~0.459086**. Thus the experiment contains **two**, not three, distinct source-demand temporal shapes.

The archive-reconciled 4h-to-8h battery *additional discharged energy* (GWh) was:

| Original demand zone | Flat | Synthetic wave A | Synthetic wave B |
|---|---:|---:|---:|
| Arizona p28 | 64.512 | 3733.614 | 2793.766 |
| Wyoming p21 | 0.000 | 0.000 | 0.000 |
| Arizona p29 | 0.888 | 51.368 | 38.437 |

These are **only** one-year, three-source-zone illustrative dispatch comparisons: not evidence for real observed renewable curtailment or universal storage performance. The Wyoming zero-increment finding is genuine within its modeled demand/availability/LP assumptions, but whether it is caused by energy-capacity nonbinding versus other objective/feasibility conditions requires an explicit binding/dual audit. Do not overstate it.

## Mandatory manuscript correction

Existing summaries of “20 independent zones”, “20 regional replications”, “540 independent experiments”, or cross-zone robustness from just Arizona p28/p29 must be rewritten:

> The modeling dataset contained 20 EFS-derived zonal demand records per projection year, of which 19 had nonzero load. Peak-normalized hourly sequence auditing identified seven distinct nonzero demand temporal shapes per year. Several zones within a state were exact scaling variants of the same source-hour demand sequence, which limits the effective diversity of demand chronologies and prevents treating zonal dispatch responses as independent temporal replications. We therefore distinguish computational LP case count from unique source-demand shapes and restrict mechanistic inference to the shape-level evidence.

This result is **not** a claim that different physical locations have identical real load, that source data are erroneous, or that scaling zones is inherently inappropriate. It is a methodological feature of the staged project input that must be disclosed in any scientific conclusions.

## Next useful test

A pre-specified seven-group experiment should choose **one** zone representative from each unique nonzero source-demand shape (e.g. highest original annual MWh in that group, deterministically), before evaluating any dispatch outcomes; verify each original archived 540-case LP summary, collect nine hourly cases per representative, and summarize effects by **seven source shapes**, not nominal number of zones. To generalize to real regional grid operation, admit genuine zonal hourly electricity time series plus independently timed resource-weather data, actual generator/bus topology, and storage capital costs.

**Other limitations:** `LocalHourID` is a source ordinal, not physical UTC; 2040 calendar label issue is unresolved. All modeled renewable profiles are mathematical constructions. No network-constrained Western OPF, no empirically validated power capacity nor storage CAPEX.
