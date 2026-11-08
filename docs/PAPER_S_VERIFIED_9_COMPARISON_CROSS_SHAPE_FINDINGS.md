# Paper S v11: Source-derived marginal duration findings across all three synthetic supply shapes

**Verified source:** [original 540 optimal full-year cyclic LP cases](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659) → [derived 9-row numerical audit and S4/S5 plots, passing run #42455745341](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42455745341). This report was prepared by inspecting the run's actual seven-file ZIP, not manually reconstructing figure values.

**Figure/data artifact:** `paper-s-source-derived-marginal-duration`, seven files: Figures S4 and S5 each as SVG and PNG, the unrounded input-aggregated comparison CSV, certificate JSON and figure manifest JSON. SHA256 of ZIP as recorded by Actions: `09f253219e48d244245622ed7befca4dd2c25e8419f40c2c2b25a0d06ed73fc3`.

## Results from original LP CSV, not rounded Markdown data

Cost values below are illustrative LP objective reductions in **USD billion** (rounded here to six decimal places). `ratio` is benefit of adding storage hours 4–8 divided by benefit of adding hours 0–4, within each year and synthetic shape.

| Year | Synthetic supply | Reduction 0→4 h ($B) | Reduction 4→8 h ($B) | Incremental ratio (%) |
|---|---|---:|---:|---:|
| 2030 | Flat 50% | 0.102813 | 0.006834 | 6.647 |
| 2030 | Wave A | 1.248483 | 0.519824 | 41.637 |
| 2030 | Wave B | 0.791973 | 0.312397 | 39.445 |
| 2040 | Flat 50% | 0.114957 | 0.007641 | 6.647 |
| 2040 | Wave A | 1.394742 | 0.581024 | 41.658 |
| 2040 | Wave B | 0.884763 | 0.349292 | 39.479 |
| 2050 | Flat 50% | 0.131635 | 0.008749 | 6.647 |
| 2050 | Wave A | 1.595212 | 0.665003 | 41.687 |
| 2050 | Wave B | 1.011931 | 0.399960 | 39.524 |

**Core finding:** In all **nine** synthetic-shape × EFS-projection-year comparisons, both duration increments reduce the toy variable objective, and **4→8 h** produces a smaller incremental reduction than **0→4 h**. The relative remaining marginal benefit is about **6.65% for Flat**, **39.4–39.5% for Wave B**, and **41.6–41.7% for Wave A**. Do not treat repeated near-identical across-year percentages as independent replication: scenario generation and load scaling share a fixed construction. The shape-dependence supports a more precise *model-conditional* claim than Wave A alone, but is **not a general theorem for storage duration**.

### Model-unused hypothetical renewable potential

The corresponding absolute reduction in unused hypothetical supply is also larger for 0→4 h than 4→8 h in all nine cases (TWh):

| Year | Shape | 0→4 h (TWh) | 4→8 h (TWh) |
|---|---|---:|---:|
| 2030 | Flat 50% | 1.352802 | 0.089921 |
| 2030 | Wave A | 16.427410 | 6.839789 |
| 2030 | Wave B | 10.420700 | 4.110490 |
| 2040 | Flat 50% | 1.512594 | 0.100541 |
| 2040 | Wave A | 18.351860 | 7.645057 |
| 2040 | Wave B | 11.641620 | 4.595954 |
| 2050 | Flat 50% | 1.732035 | 0.115124 |
| 2050 | Wave A | 20.989630 | 8.750035 |
| 2050 | Wave B | 13.314880 | 5.262632 |

**Note:** the TWh values above are rounded for reporting; exact machine data are in the artifact CSV. Because the hypothetical cost functional has 5 USD/MWh for renewables delivered directly or used to charge and 90 USD/MWh for firm supply, the relative variable-cost improvements track the dispatch/unused-energy structure under this particular LP. This is not a universal economic relationship.

## Recommended wording for Paper S Results

> Across the 20 independent EFS-load zones, each of the nine combinations of three planning-year projections and three synthetic renewable availability shapes exhibited a smaller reduction in the illustrative LP variable objective when battery duration increased from four to eight hours than when it increased from zero to four hours. The ratio of the second four-hour increment to the first depended strongly on assumed supply timing: approximately 6.65% for the flat profile versus 39.4–41.7% for the two ordinal-wave profiles. These results demonstrate sensitivity to assumed resource chronology, not a physically calibrated Western Interconnection storage-value or optimal-duration estimate.

## Limitations essential for manuscript

- The source EFS load is projected demand for seven admitted Western states and 20 zones; it is **not complete Western Interconnection demand**.
- All three resource-availability shapes and storage hardware assumptions are mathematical scenarios, not observed 2012 resource/weather profiles or future forecast actuals.
- All 540 LPs enforce annual initial/terminal SOC zero with 90% assumed roundtrip efficiency; the 20 zones **do not exchange power**.
- The objective is `5 * (direct_renewable_MWh + battery_charge_input_MWh) + 90 * firm_generation_MWh`, **without any battery capacity investment, degradation, replacement, financing, O&M, market value, or transmission**. Cost reductions cannot be interpreted as *net economic savings* or an optimal duration.
- Original 8,760 EFS `LocalHourID` hour sequence is a **source ordinal**, not independently certified physical UTC; the 2040 leap-label issue persists.
- With only 0/4/8 h sample points, "diminishing marginal returns" applies only to these two **four-hour increments** and this modeled objective, not all storage capacities or physical systems.

## Figure placement

**Figure S4:** Marginal reduction in unused hypothetical renewable availability across synthetic shapes by year (0–4 h versus 4–8 h).  
**Figure S5:** Marginal reduction in the illustrative LP variable objective, same structure.  
S5 is useful for discussing model-cost sensitivity but should not be titled economic "savings". Include source and caveats in captions.

Keep the full manuscript private; this public file is a source-linked results audit only.
