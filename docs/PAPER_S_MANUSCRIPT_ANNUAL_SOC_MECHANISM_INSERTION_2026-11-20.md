# Paper S — manuscript-ready annual mechanism insertion (2026-11-20)

**Status:** author review draft to insert into the current integrated manuscript and supplementary information (SI). Uses only the source-audited 15 original weather years: four states, 120 state×weather-year×county-weight records and 60 paired within-year spatial contrasts. The original optimization results and economic threshold screening are unchanged. The independent local artifact audit has passed; official aggregation-recovery GitHub Actions status must be verified separately before labeling its output successful.

## Suggested revised title
**Weather-dependent battery duration value across renewable resource potential and operating-county spatial weights: a 15-weather-year, four-state optimization study**

## Manuscript insertion — Section 2: Methods

### 2.X. Chronological input-only transfer and SOC-horizon sensitivity

To determine how assumed battery terminal conditions affect the representation of storage-duration value, we implemented a separate set of chronological linear programs using the same authenticated source years, 2030 reference-demand hourly support, AC-normalized county-weighted wind and utility-scale photovoltaic profiles, renewable capacity ratios and fixed battery power assumptions as the original dispatch study. This experiment was confined to four prespecified state–renewable-penetration combinations: Arizona (R=1.5), Colorado (R=2.0), Idaho (R=1.5) and Wyoming (R=1.5), each at 50% installed AC wind share. Every combination was evaluated over 15 original ReEDS weather-source years (2007–2013 and 2016–2023), two alternative county weight definitions and 8,760 hourly observations per reference year.

For each hour `t`, the battery could charge from nonnegative *exogenous* renewable surplus `max(G_t−L_t,0)` and discharge only against net load deficit `max(L_t−G_t,0)`. Charging and discharging were each limited by installed battery power `P`; the energy limit was `4P` or `8P`. The state-of-charge recursion used equal one-way efficiencies `sqrt(0.90)`, with no simultaneous charging/discharging feasible because the exogenous hourly surplus and deficit sets are disjoint. Each LP maximized total renewable surplus delivered into deficit hours (MWh) independently of a price or firm-generation cost objective.

We solved each duration under three distinct terminal-SOC conventions on the **same complete 8,760-hour** input: (i) 365 daily intervals with zero terminal SOC every 24 h; (ii) 52 seven-day intervals with zero SOC every 168 h plus one terminal 24 h interval; and (iii) a single 8,760-hour cycle with zero initial and terminal SOC. At a fixed battery duration, the longer-boundary feasible set weakly contains the shorter-boundary feasible set, but the incremental 8 h minus 4 h delivery difference need not increase monotonically across horizons. We then computed the within-year county-weight contrast in the **incremental 4→8 h MWh** metric and compared it descriptively with the frozen annual dispatch model's **incremental 4→8 h operating-value** contrast. Neither the 15 weather references nor the two county-weight constructions were treated as randomized causal experiments.

### 2.X+1. Structural equivalence and interpretation gate

The reference economic LP uses a constant illustrative firm-generation marginal variable cost of $90/MWh and a constant renewable variable cost of $5/MWh. In settings where the same chronological storage and load constraints allow each additional unit of renewable-delivered energy to replace a constant-cost firm-generation unit, maximizing the delivered input-only MWh may be mathematically equivalent—up to scaling and source feasibility conventions—to minimizing variable generation cost. Consequently, high correlations between independently coded energy-maximizing and cost-minimizing LP outputs would not, by themselves, identify an exogenous physical mechanism, validate actual dispatch or predict market profitability. As a predeclared postprocessing check, we therefore examined the residuals from a within-state affine mapping between the source-only annual transfer spatial contrast and the frozen cost-LP spatial contrast. The analysis is characterized as an **internal objective-consistency and horizon-sensitivity diagnostic**, not independent causal validation.

## Manuscript insertion — Section 3: Results

### 3.X. Complete-year SOC boundaries and storage-duration siting contrasts

All 12 state×five-year source partitions completed successfully, yielding 120 annual source cases and 720 energy-only LP solves (three SOC conventions, two durations). The final numerical aggregation was independently reconstructed from the 12 source artifacts after identifying and correcting a duplicated-column merge error in the official summary workflow. The maximum observed equality-balance residual across the source LPs was 7.276×10⁻¹² MWh. Nested deliverable-energy inequalities (annual ≥ weekly ≥ daily) held separately for both duration capacities.

Across 15 paired weather years per state, Pearson correlations between the source-only marginal 4→8 h *siting* contrast and the original full-year cost-LP marginal-value siting contrast were as follows:

| State (R) | Daily-reset r | Weekly-reset r | Continuous-year r | Daily sign matches | Weekly sign matches | Continuous-year sign matches |
|---|---:|---:|---:|---:|---:|---:|
| Arizona (1.5) | 0.0194 | 0.9587 | 1.0000 | 9/15 | 13/15 | 15/15 |
| Colorado (2.0) | 0.3884 | 0.9546 | 1.0000 | 14/15 | 15/15 | 15/15 |
| Idaho (1.5) | 0.1439 | 0.9636 | 1.0000 | 15/15 | 15/15 | 15/15 |
| Wyoming (1.5) | 0.8265 | 0.9529 | 1.0000 | 15/15 | 15/15 | 15/15 |

The annual-cycle model matched all **60/60** year-specific siting-effect signs, whereas the weekly and daily reset models matched **58/60** and **53/60**, respectively. These findings demonstrate that terminal-SOC convention materially changes how much of the original cost-LP variation can be reproduced by an energy-only chronological surrogate. They should **not** be interpreted as externally validated explanatory accuracy.

### 3.X+1. Annual objective-proportionality diagnostic

The perfect correlations under the annual SOC convention were not independent evidence of a previously unidentified mechanism. An explicit linear proportionality audit demonstrated a near-exact mapping between annual energy-maximizing siting effects and the frozen economic LP siting effects in every state. The estimated state-specific scaling coefficient (in model USD per added kWh-year per transferred MWh) and maximum absolute residual were:

| State | Proportionality coefficient | Maximum absolute residual (model USD/added kWh-year) |
|---|---:|---:|
| AZ | 4.351684846×10⁻⁶ | 6.08×10⁻¹⁰ |
| CO | 7.372485109×10⁻⁶ | 6.45×10⁻¹¹ |
| ID | 1.622683407×10⁻⁵ | 1.20×10⁻⁹ |
| WY | 2.751529633×10⁻⁵ | 4.24×10⁻¹⁰ |

The intercepts were effectively zero (absolute magnitudes below 1.3×10⁻⁹ model USD/added kWh-year). Thus, the complete-year test is best interpreted as a verification of internal objective equivalence and storage-horizon assumptions. It does not provide independent evidence that real-world avoided costs or asset-level generation follow the model.

## Manuscript insertion — Section 4: Discussion

### 4.X. Why source-only storage transfer does not constitute independent economic validation

A central methodological lesson of these experiments is that a predictor derived from the same constraints and source series as a cost-minimizing LP is not automatically an independent mechanism or external check. The earlier order-blind same-day surplus–deficit proxy showed apparent strong associations with modeled value, but the physically ordered 24 h greedy policy markedly weakened several correlations. The subsequently optimized two-window, 168 h analysis exhibited pronounced window sensitivity and did not consistently reproduce annual economic contrasts. On a complete 8,760-hour horizon, allowing SOC to carry over between days and weeks raised the correspondence with the original full-year LP. Crucially, the continuous annual variant achieved an almost perfect **algebraic correspondence**, revealing that the energy-only and fixed-cost economic objectives encode largely the same marginal substitution under the modeled assumptions.

This result supports treating cross-day energy availability and terminal-SOC constraints as **important modeling sensitivities**, rather than claiming identification of a universal physical causal mediator. The stronger weekly relative to daily correlations do not imply that the real-world system will achieve the simulated savings, nor do they identify the separate contributions of energy scarcity, power rating, regional transmission limits or actual hourly electricity prices. A future genuinely discriminating test should hold the same renewable and load inputs fixed while introducing *independent* time-varying prices or scarcity costs with documented source provenance, or should evaluate against actual asset-level production/dispatch and balancing-authority geography that match the model scope. The present EIA-930 Idaho Power BA shape comparison has important BA-versus-state and 2025-versus-2023 fleet identity limitations and cannot serve as such an unqualified external validation.

### 4.X+1. Economic screening limits remain separate

The 3×3 resource ratio/wind mix design generated 1,080 duration-value cases across four states, 15 weather years and two county weighting schemes. Under the lowest authenticated 2030 ATB annualized storage energy-extension hurdle (16.049 model USD per added kWh-year, Advanced/4%), 213 cases exceeded the illustrative modeled operating-value ceiling. The repeated threshold grid contains 19,440 labeled comparisons, not 19,440 independently solved economic dispatch scenarios. These conditional exceedances are sensitive to an assumed $90/MWh firm-generation marginal cost and are **not** evidence of realized investment profitability, net present value, ratepayer savings, or a calibrated model of observed market electricity prices. The objective proportionality result must not be used to promote the ATB screen into bankable economics.

## Suggested abstract replacement paragraph (insert in current integrated abstract, not a separate abstract)

We evaluated 15 authenticated weather years across four Western U.S. states, two renewable county-weighting constructions, three renewable capacity ratios and three wind-share levels. From 1,080 modeled 4-to-8-hour storage comparisons, 213 exceeded the lowest of the tested 2030 ATB-based annualized incremental energy-capacity cost thresholds; this conditional screening does not establish project profitability. A separate full-year chronological source-only storage-transfer study comprised 120 state–year–weight cases and three state-of-charge boundary conventions, showing substantial sensitivity to daily, weekly or annual SOC resets. Although the annual continuous-SOC energy metric matched the economic LP siting-effect directions in all 60 weather-year pairs, a proportionality audit demonstrated that this near-perfect association reflects objective-structure equivalence under fixed marginal generation costs rather than independent causal or observational validation. These results emphasize the joint influence of resource aggregation, wind–solar mix and temporal storage constraints on stylized modeled duration value.

## Supplementary information insertion (SI §S.X)

### S.X. Model and source-reconciliation controls

Retain raw year-by-year `Y1_all15_annual_mechanism_cases.csv`, within-weather-year paired `Y2_all15_paired_mechanism.csv`, four-group `Y3_all15_four_state_mechanism.csv`, and `Y4_exact_proportionality_audit.csv` as supplementary tabular provenance, together with the original 12 source-partition artifacts and hashing/checking manifests. Include both the annual time-horizon correlation heatmap and four-state year-labeled scatter plot. Every figure is a **descriptive model-to-model consistency** comparison; no observed-profit, validated-forecast or causal language is permissible.

The source-backed original workflow [44849783992](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44849783992) completed 12/12 compute jobs; its aggregate step failed due to duplicate frozen LP value column names. Local reconstruction of all 12 compute artifacts was independently audited and the join logic repaired. Cite a separately passing official recovery workflow if and only if that workflow ultimately succeeds. The original 3×3 ATB economic screening and historical-demand study are unchanged.

## Editorial and reproducibility decisions

- Do not merge this addendum blindly into the 2026-11-12 English draft: it originally describes a four-weather-year design and needs the integrated 15-year/3×3 Methods/Results numerical population reconciled across the entire document.
- The new source-only study spans four **prespecified** state–ratio combinations, **not** the full nine-point design matrix; do not write that all 1,080 cases underwent the mechanism experiment.
- Describe the per-state Pearson r over n=15 weather references as descriptive model sensitivity, not independently replicated predictive validation.
- Do not infer state-to-state differences in economic units from raw shifted MWh because installed battery sizes and denominators differ across states.
- Keep the supplementary two × 168 h window findings (CO R2: weekly r = −0.056 versus +0.448) as evidence of sampling/horizon sensitivity, not an annual physical counterexample once complete-year results exist.
- Preserve Original Paper C-1/C-2/Paper T results and the source-pinned 3×3 cost threshold CSV.
