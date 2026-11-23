# Paper S — Authenticated common-R=1.5 four-state annual storage comparison and manuscript insertion (2026-11-22)

## Primary reproducible evidence

- Successful official GitHub Actions source run **44919128370**: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44919128370
- Final aggregated artifact **14714718140**: `paper-s-CO-R15-180LP-common-design-15-year-4state-comparator`, official zip size 35,969 bytes.
- Three Colorado 5-year partitions **all succeeded**; aggregation **succeeded**, printed `PAPER_S_CO_R15_180LP_COMMON_DESIGN_COMPARATOR_PASS`.
- 180 **new** physical transfer optimization LP solves for CO (15 years × 2 county schemes × 2 durations × 3 SOC horizons); 540 **reused**, source-verified physical optimization LP results for AZ, ID, WY.
- 30 new CO year×county-weight source cases, 120 common-R1.5 four-state source cases, 60 within-year siting effect pairs (15 per state), **all 8,760 source hours** per year, daily/weekly/annual fixed-duration feasible nesting and balance residual <1e-5 MWh. The frozen 3×3 economic objective grid remains unchanged.
- Source ReEDS wind/PV/demand HDF5 and supply curves pinned by MD5 in the workflow, with immutable official frozen and comparison artifacts.

## Matched source-year results at R=1.5 and 50% AC wind share

Median 15-weather-year within-year model siting effect (EIA2025 county-weighted minus original ReEDS2012 source-potential weighted), illustrative model USD/(additional storage kWh-year), **not real-world storage profitability**:

| State | R | Paired median modeled effect | Daily proxy Pearson r | Weekly physically optimal Pearson r | Annual physically optimal Pearson r | Daily same sign years | Weekly same sign years | Annual same sign years |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| AZ | 1.5 | -0.340861 | 0.019414 | 0.958747 | 1.000000 | 9/15 | 13/15 | 15/15 |
| CO | 1.5 | +0.410384 | 0.368747 | 0.919659 | 1.000000 | 12/15 | 15/15 | 15/15 |
| ID | 1.5 | +2.337690 | 0.143886 | 0.963586 | 1.000000 | 15/15 | 15/15 | 15/15 |
| WY | 1.5 | +2.636534 | 0.826549 | 0.952937 | 1.000000 | 15/15 | 15/15 | 15/15 |

These are year-paired modeled **geography effects**. Pearson correlations quantify internal covariation within shared source/weather/LP structure, not external model validation or causal physical proof. Annual perfect correlations follow from the shared objective/accounting structure of these models; cannot be cited as independently identifying mechanism.

## Previously verified controlled contrast at CO R=2.0, 50% wind

- The original frozen 3×3 economic grid, at CO R=2.0 and 50% wind, yields median paired EIA-minus-ReEDS geography effect **-2.177855** model USD/(additional kWh-year).
- The newly confirmed common R=1.5 CO matched effect is **+0.410384** model USD/(additional kWh-year).
- **Interpretation:** the sign of Colorado's *median modeled geographic-weighting effect* differs across the two renewable peak-ratio settings under 50%-wind scenario controls; a state-invariant effect claim is therefore unsupported. Do **not** claim that a difference between these two group medians is itself a median of weather-year-paired R-contrast differences; that would require directly joining both raw 15-year paired outputs.
- Nor does this alone prove a statistical significance test, SOC causality, real-grid congestion, observed 2023 dispatch, or real-investment economics.

## Draft manuscript insertion (Results)

> In a common penetration-ratio sensitivity (R=1.5, AC wind share 50%), the 15-weather-year median within-year difference in modeled marginal 4-to-8-hour storage value between EIA-2025 fleet-county and original ReEDS-2012 resource-potential county weights was -0.341, +0.410, +2.338, and +2.637 illustrative model USD per additional kWh-year for Arizona, Colorado, Idaho, and Wyoming, respectively. In contrast, Colorado's otherwise corresponding R=2.0, 50%-wind experiment yielded a paired median of -2.178. This sign reversal in the scenario-conditional Colorado median indicates that the modeled siting contrast depends on renewable penetration and should not be interpreted as a fixed state-level property. These comparisons concern hypothetical county weighting and copperplate dispatch under authenticated historical resource shapes; they do not establish actual investment returns or isolate a causal operational mechanism.

## Draft manuscript insertion (Discussion / limitations)

> The annual source-only transfer experiment provides a consistency check under common hourly inputs and feasible SOC conventions, rather than independent causal identification. Strong correlations with the economic LP can arise from structural equivalence under shared constraints and prices; distinguishing operational drivers would require comparisons with independently varied price structures, congestion, storage constraints, or observed load and supply series with matched geographic fleet definitions. We therefore report state- and scenario-conditional directional effects instead of extrapolating a universal 50% wind share threshold.

## Publication release decision

ACCEPT the audited R=1.5 four-state table and CO median reversal as **within-model scenario sensitivities**. Do not publish unsourced per-year crossover counts, significance statements, or imply that the hypothetical 2025 EIA fleet-weight spatial reaggregation is authenticated 2023 operations. The PR is deliberately kept unmerged; manuscript/SI version and Zenodo package must be reconciled before a deposit.
