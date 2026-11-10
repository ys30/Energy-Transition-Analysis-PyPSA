# Paper S proposed main Figures 2–4 — accepted original archival evidence and editorial review

**Status: three figure-candidate PNG/SVG assets rendered, source cross-certified, and visually reviewed.** The final [GitHub workflow #42877258094](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42877258094) passed. It restored two *separate* historical artifacts: the original 540 full-year LP output and nine-year/shape marginal duration comparisons, and checked all 27 annual aggregate source-case values against the corresponding marginal archive records, including original unused resource, firm generation, toy objective and 0→4/4→8 differences. No additional LP experiment or empirical resource series was added in this stage.

## Figure 2 — 2030 synthetic resource timing and modeled unused availability

**Caption candidate.** Modeled unused synthetic renewable availability as a percentage of modeled available renewable potential for the year 2030, comparing three assumed hourly resource shapes (flat 50%, ordinal Wave A and ordinal Wave B) at zero, four or eight hours of illustrative battery storage duration. Battery power was held at 25% of each source zone's demand peak, with capacity proportional to duration. Results aggregate the 20 original EFS projected load zones, not 20 independent temporal replicates. The supply profiles are hypothetical mathematical constructs, not observed solar/PV output; unused availability is not verified real-world curtailment.

- Original source: [540-case full-year LP acceptance #42107237659](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659), file `all_20zone_cyclic_8760h_summary.csv`.
- Source-derived values from the accepted archive (0h → 4h → 8h): Flat **1.085% → 0.418% → 0.374%**, Wave A **12.772% → 4.669% → 1.295%**, Wave B **7.775% → 2.635% → 0.607%**.
- Distinct from Figure 4, Figure 2 reports the fraction of *unutilized hypothetical resource supply*, not modeled dollar objective differences.

## Figure 3 — planning-year demand scale versus normalized objective response

**Caption candidate.** (A) EFS projected annual aggregate demand for source planning years 2030, 2040 and 2050. (B) Illustrative firm generation divided by the corresponding planning year's projected annual demand for assumed storage durations zero, four and eight hours under an identical synthetic ordinal Wave A availability profile. The normalized curves nearly coincide: planning years are scenario projections rather than independent observed weather-year experiments. This figure highlights how absolute system-level changes may largely reflect a scaled projected demand input rather than independent chronological/weather information.

| Planning year | Original aggregate demand (TWh) | 0h firm / demand | 4h firm / demand | 8h firm / demand |
|---|---:|---:|---:|---:|
| 2030 | 274.70699 | 35.627266% | 30.245290% | 28.004426% |
| 2040 | 306.83921 | 35.625517% | 30.242672% | 28.000276% |
| 2050 | 350.87147 | 35.623409% | 30.239481% | 27.995061% |

**Editorial concern:** At the baseline/4h/8h points, the 2030–2050 normalized differences are only about **0.003857, 0.005809, and 0.009365 percentage points**, respectively. This is an interesting *negative* cross-year invariance/scale check but potentially too repetitive for a six-figure main text. For a higher-tier methods journal, **recommend moving Figure 3 to supplement** unless a coherent original demand-shape/uncertainty question gives it independent interpretative value. Retaining the six-slot layout is an editorial option, not a scientific requirement. If removed, a five-figure main text with a clearer single message may be stronger.

## Figure 4 — marginal 0→4 versus 4→8h model operating objective

**Caption candidate.** Additional reduction in the illustrative model variable operating objective for the first four-hour storage increment (0→4h) and the second four-hour increment (4→8h), conditional on each of three synthetic hourly supply profiles and each EFS projected demand planning year. Values sum the original 20-zone source LP results, expressed in billions of hypothetical USD. The second increment is smaller in every displayed pair of conditions; no battery investment expenditure, degradation/replacement, operational reliability, real-world savings or optimal battery sizing is implied.

| Year | Supply profile | 0→4h objective reduction (USD B) | 4→8h (USD B) |
|---|---|---:|---:|
| 2030 | Flat | 0.102813 | 0.006834 |
| 2030 | Wave A | 1.248483 | 0.519824 |
| 2030 | Wave B | 0.791973 | 0.312397 |
| 2040 | Flat | 0.114957 | 0.007641 |
| 2040 | Wave A | 1.394742 | 0.581024 |
| 2040 | Wave B | 0.884763 | 0.349292 |
| 2050 | Flat | 0.131635 | 0.008749 |
| 2050 | Wave A | 1.595212 | 0.665003 |
| 2050 | Wave B | 1.011931 | 0.399960 |

Original source: [nine conditional marginal contrasts #42455745341](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42455745341), file `paper_s_marginal_duration_all_shapes.csv`, independently reconciled against [accepted 540 LP original aggregation](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659).

## Production and claims gates

- Publication candidate [Figures 2/3/4 generator](../src/energy_transition/paper_s_main_figures_234.py), [cross-archive negative-path tests](../tests/test_paper_s_main_figures_234.py), [CI](../.github/workflows/paper-s-main-figures-234.yml).
- Do not infer statistically independent replicates from 20 zonal datasets: **seven unique within-year peak-normalized positive-demand shapes**, with even fewer independent input-creation processes across years.
- Real solar/wind, physical UTC, interzonal power transport, battery capital costs, degradation, reserve and firm generation realism are **not validated**.
- None of the percentage or toy-objective changes is a confidence interval or population generalization.
- Figures 1, 5 and 6 already have independently accepted submission-candidate assets; **all six candidates now exist**, but figure-numbering, literature context and the complete private manuscript are not final, and Figure 3 should undergo an editorial inclusion decision.
