# Project B / Paper S — derived marginal-duration analysis (2026-11-07)

## Scientific scope and provenance

This is a **secondary arithmetic interpretation** of the already published rounded annual **Wave A** results from [the source-backed 540-case cyclic-storage audit](efs_8760h_cyclic_storage_scaleup.md), based on [successful original all-zone run #42107237659](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659) and [independent objective/conservation certification #42146086492](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42146086492).

**No new LP run, actual renewable-resource acquisition, Western transmission-constrained OPF, or battery investment model was performed for this note.** All reported differences are calculated from already rounded three-decimal-place TWh / USD-billion figures; they are not exact unrounded archive-derived marginal values.

For a fixed synthetic availability shape and year, let (U_d) denote unused assumed renewable availability in TWh and (C_d) the model's *illustrative annual variable objective* in USD billion at storage duration (d \in \{0,4,8\}\) hours, as tabulated in the source note. Define the 0-to-4 increment (U_0-U_4), (C_0-C_4), and the 4-to-8 increment (U_4-U_8), (C_4-C_8).

| Projection year | Unused availability reduction, 0→4 h (TWh) | Unused availability reduction, 4→8 h (TWh) | Model variable-cost reduction, 0→4 h ($B) | Model variable-cost reduction, 4→8 h ($B) | 4→8 h variable-cost increment as % of 0→4 h |
|---|---:|---:|---:|---:|---:|
| 2030 | 16.427 | 6.840 | 1.249 | 0.520 | 41.6% |
| 2040 | 18.352 | 7.645 | 1.395 | 0.581 | 41.6% |
| 2050 | 20.990 | 8.750 | 1.596 | 0.665 | 41.7% |

The same 2030 source rounded values imply 0→4 h reduces the assumed toy objective by about 12.9% of the 0-hour objective; the additional 4→8 h reduction is about 5.4% of the *0-hour* objective. These are not uncertainty bounds or predictions. The cross-year similarity may reflect construction/scaling of the synthetic assumptions, so the three years should **not** be described as independent empirical confirmations.

## Interpretation and claim limits

For these fixed assumed renewable-availability shapes, zonal demand series and stylized hardware/cost settings, adding the first four hours of storage produces a larger reduction in unused assumed renewable availability and toy variable cost than adding hours 5–8. The comparison has a **diminishing modeled marginal benefit** within this restricted experiment, but no inference about the optimal economic duration is licensed.

- The LP is performed over **20 independent zones** rather than a connected Western grid; electricity transfers, congestion, network reliability and real plant/POI placement are not modeled.
- The assumed wind/solar availability shapes, 90% round-trip efficiency, power rating and operating-cost coefficients are not observed 2030–2050 energy-system inputs.
- The objective prices renewable directly serving demand or charging at **$5/MWh**, and firm supply at **$90/MWh**. There is **no CAPEX, fixed O&M, replacement, degradation, financing, electricity-market value or capacity credit**. A lower variable objective cannot be called net system savings or investment return.
- Durations 0, 4 and 8 hours are only three assumed design points. Comparisons at constant battery power do not identify the full storage-duration response curve.
- The source's 8,760 hourly series is **LocalHourID ordinal**, not an independently certified physical UTC chronology. In particular, 2040 archived calendar labels have leap-year interpretation hazards.
- The source numeric input population comprises **seven states and 20 zones**, not comprehensive Western Interconnection demand.

## The next experiment that would change scientific inference

Rather than running more variants of the same synthetic shapes, identify one **source-authenticated hourly wind/PV resource** with documented weather year, publication rights, measurement/model basis, zone mapping and physical timestamp semantics. Only join it to EFS when the source-clock admission checks independently pass. Add explicit storage power/capacity economics and a credible network or explicitly bounded independent-zone use case. Compare variable-cost reductions with annualized cost of incremental capacity and report the difference. Do not silently convert these dollar figures to an annual net benefit.

For any future figure, name the result **"Illustrative Wave-A cyclic-storage LP: marginal avoided unused availability / variable objective"**, not "Western storage savings" or "optimal battery duration."

## Source table and reproducibility

Source: [efs_8760h_cyclic_storage_scaleup.md](efs_8760h_cyclic_storage_scaleup.md), section "Stage 2: verified 20-zone full-year results"; objective: [PAPERS_T_S_VERIFIED_FIGURES_AND_OBJECTIVE_CERTIFICATE.md](PAPERS_T_S_VERIFIED_FIGURES_AND_OBJECTIVE_CERTIFICATE.md).

For a publication-quality final table, recalculate all differences from original 540-case CSV before quoting additional decimal places. This note preserves the derived calculations at the available display precision and does not claim an additional artifact or verification CI.
