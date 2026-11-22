# Paper S — integrated English manuscript v2 (source-audited review, 2026-11-22)

**Proposed title:** Weather-Year and Renewable-Penetration Dependence of Marginal Battery Duration Value under Alternative County-Level Renewable Resource Weights

**Status:** consolidated author-review manuscript text. The study concerns a hypothetical state copperplate optimization, **not an operationally verified PyPSA network model, calibrated 2030 fleet prediction, or battery investment appraisal**. All source-based numerical claims below refer to completed and successful workflows listed in Data and Code Availability. Journal formatting, source-specific bibliographic verification, visual DOCX/PDF QA, and release licensing remain open.

## Abstract

The estimated operating value of extending battery duration depends on the geographical aggregation of wind and photovoltaic resource profiles, renewable penetration, weather-year conditions, and temporal storage assumptions. We evaluated four western U.S. states (Arizona, Colorado, Idaho and Wyoming) using authenticated ReEDS-2022 county-level renewable-resource time series, a fixed 2030 reference-demand scenario, and two alternative county aggregation weights: original 2012 resource potential and observed 2025 EIA operating-generator county shares. The alternatives are hypothetical model weighting schemes, not equivalent contemporaneous installed fleets. A source-verified 3×3 design varied renewable AC nameplate relative to peak demand (1.0, 1.5 and 2.0) and wind share (25%, 50%, 75%) over 15 historical resource-weather years, yielding 1,080 matched incremental four-to-eight-hour battery-duration value cases from authenticated optimal linear programs. Under an illustrative 2030 ATB Advanced/4% storage-extension cost threshold of 16.049 in 2023 USD per additional kWh-year, 213 of 1,080 modeled value cases exceeded the threshold; this is conditional screening, not a demonstrated benefit-cost result because model and ATB dollar bases are not calibrated. Spatial-weight contrasts were not state-invariant: for Colorado at 50% wind, the 15-year median EIA-minus-resource-potential siting effect was +0.410 at penetration ratio 1.5, versus -2.178 at ratio 2.0 (illustrative model USD per additional kWh-year). Independent 40/60% wind design-point reoptimizations and hourly dispatch diagnostics supported a local nonlinearity but did not uniquely identify its physical cause. Chronological daily, weekly and annual energy-transfer optimizations showed substantial SOC-horizon sensitivity; near-perfect agreement between continuous-year source-only transfer and the economic LP followed from their shared objective structure and does not constitute external validation. We conclude that marginal storage-duration value from county-aggregated renewable shapes is strongly conditional on design and timing assumptions and should not be extrapolated to observed dispatch or investment profitability without additional geographic, network and price validation.

## 1. Introduction

Long-duration storage is commonly assessed by comparing energy capacities at fixed power, but the resulting incremental value is partly determined by the chronological alignment of renewable generation and demand. Even with identical statewide renewable nameplate, county aggregation weights can change the timing of modeled availability. Resource-potential weights and operating-generator capacity weights answer distinct questions: one describes a developable resource representation; the other describes a fleet geography for a particular observed year. Neither is a calibrated 2030 generator buildout.

This study asks three related questions. First, how much do source-verified weather-year and county-weight choices change the incremental annual operating-cost avoidance from extending a hypothetical battery from four to eight hours? Second, do penetration and wind/PV mix modify the direction and scale of the modeled county-weight contrast? Third, which aspects of the modeled duration effect reflect source-hour conventions or imposed storage state-of-charge (SOC) horizons rather than independent physical evidence? We deliberately separate these sensitivity questions from real-world economic appraisal.

The contribution is a source-authenticated, paired scenario experiment with explicit time, spatial-weight and numerical-convention gates, combined with a falsification-oriented SOC-horizon comparison. Results do not claim novelty from first proposing spatial validation, energy-only storage mechanisms, or multi-year optimization; a final journal-specific prior-art and bibliography review remains necessary.

## 2. Materials and methods

### 2.1. Source data, geography and temporal scope

Renewable inputs use the original ReEDS-2022 county-level wind and utility-scale PV available-resource series and source supply-curve weights. Historical source-weather years are **2007–2013 and 2016–2023** (15 years, not 2010–2024). The county resource profiles are conditioned on original ReEDS 2012 weather/technology resource definitions. The fixed 2030 reference demand and source-hour clock are separately pinned to authenticated publisher HDF5 inputs. Source checks cover MD5, native fixed-CST labeling, dimensions and joins. County-based alternative EIA operating-generator weight fractions refer to **2025** generator metadata and must not be called an authenticated 2023 fleet or actual 2030 siting.

The four modeled state aggregates are Arizona (AZ), Colorado (CO), Idaho (ID) and Wyoming (WY). A state-level copperplate boundary omits intra-state network transfer, congestion and reserve constraints. EIA-930 balancing-authority dispatch is an imperfect external source-shape diagnostic because balancing-authority boundaries and operating-fleet scope do not coincide with statewide model aggregates; it is not admitted as plant-level model validation.

### 2.2. Renewable-capacity and duration factorial

AC-normalized aggregate renewable capacity is expressed as a ratio R of renewable installed AC nameplate to state reference peak load. The 3×3 screen uses R in {1.0, 1.5, 2.0} and AC wind share in {0.25, 0.50, 0.75}; utility-scale PV supplies the complement. Storage compares equal installed power with 4h and 8h energy capacities, plus a no-storage alternative when applicable. PV DC-to-AC conversion retains the source-normalized ILR assumptions. The model uses a constant illustrative firm-unit variable generation cost of 90 model USD/MWh and renewable cost of 5 model USD/MWh, with battery round-trip efficiency of 90%. These are controlled hypothetical operating assumptions, not observed price or market revenue.

The custom optimization is a **SciPy/HiGHS linear-programming state copperplate dispatch model**, not a spatial PyPSA AC/DC power-flow optimization. Hourly balance, dispatch, charging/discharging limits and SOC constraints are enforced. The value V is the annual illustrative variable-generation-cost reduction associated with extending storage energy from 4P to 8P at fixed power P, normalized per *additional* 4P of battery energy capacity and year. V is not gross revenue, discounted NPV, or total system benefit.

### 2.3. Pairing, weather-year design and interpretation

For each state, weather year, R, wind share and source-hour convention, both county weighting schemes are evaluated with matched total capacities and identical source-year identity. Spatial effects are EIA-county-weighted V minus original ReEDS-potential-weighted V **within weather year**. A reported median of these paired differences is not reconstructible by subtracting the separate schemes' medians. Historical resource years are scenario references, not IID climate draws. Main 3×3 values use the frozen 1,080 incremental duration comparisons; 40/60% Colorado follow-up and the common-R=1.5 SOC experiment are separately source-verified extensions, not replacements.

### 2.4. Hour approximation, load-weather comparison and external scope

Original source CF are instantaneous fixed-CST samples; endpoint-hold and trapezoidal point-to-hour approximations were tested separately. The historical-load paired 720-LP population and fixed-2030-load 720-LP population are retained as distinct cohorts. The authenticated 720×720 cross-panel control produced 720 objective matches, 240 duration triplets and 120 geographic comparisons; altering historical-load annual energy also alters peak-based installed power. This is **not a shape-only causal test**.

The 2023 EIA-930 Idaho Power (IPCO) source-shape comparison is restricted to a balancing authority with different spatial scope than Idaho statewide generation and to valid-hour/UTC reporting conditions; observed correlation is diagnostic, not generator fleet, energy-price or calibrated 2030 validation.

### 2.5. Battery extension cost-threshold screen

We compared the 1,080 model duration-value cases with 18 labeled ATB-2025-v2 2030 battery extension assumptions, across selected scenarios and discount rates. The threshold is the annualized difference in 8h versus 4h storage overnight capital costs plus fixed operation/maintenance difference, divided by 4 added kWh per fixed kW of rated power: H=[(OCC8-OCC4)×CRF+(FOM8-FOM4)]/4. Its units are ATB 2023 USD/(additional kWh-year). Twelve unique numerical threshold levels occur among the 18 labeled cases. Since model cost input currency has not been deflated and reconciled to 2023 USD, comparisons are **conditional illustrative threshold exceedances** only, not true investment viability.

### 2.6. Chronological input-only SOC horizon sensitivity

A separate optimization maximizes renewable-surplus energy delivered into subsequent deficit periods, using identical source series and charge/discharge power limits, but no firm-generation price objective. The same 8,760-hour source year is tested with 365 daily reset intervals, 52 weekly reset intervals plus a final 24-hour tail, and one continuous 8,760-hour zero-initial/terminal-SOC interval. For each fixed duration, daily-deliverable MWh cannot exceed weekly, which cannot exceed annually deliverable MWh. These inequalities do not imply that *incremental 8h-minus-4h* delivered energy is monotonic across horizons. Because the economic LP uses constant firm/renewable cost differences and shared chronological feasibility, annual source-only delivery can be almost affine-equivalent to cost-LP value; this is a model consistency result, not an independent causal mechanism.

## 3. Results

### 3.1. Fifteen-year source-audited duration and geographic heterogeneity

The source-audited 3×3 grid contains **1,080** state×weather-year×siting×design-point incremental 4→8h operating-value cases, from the preserved optimized design-grid source. Contrasts depend on wind/PV mix, renewable nameplate ratio and county weighting. As a robustness study, the authenticated source-hour numerical convention comparison retained direction for 59 of 60 full 15-year paired spatial effects under its specific matched design; it does not identify actual integrated source-hour generation.

### 3.2. Colorado nonlinear wind-mix contrast

At **CO, R=2.0**, 15-weather-year median within-year EIA-minus-potential modeled value contrasts for wind shares 25%, 40%, 50%, 60%, and 75% are respectively **-0.164, -1.819, -2.178, -0.301, +2.615** in illustrative model USD per added kWh-year. Values at 40% and 60% were obtained from 720 additional authentic optimal LP solves, not interpolation. The 50% design lies lower than both its 40% and 60% neighbors in 12/15 weather years, and the weather-year paired local curvature at 50% is negative in all 15. These findings support a reproducible *local, scenario-conditional* nonlinearity, not a universal analytic optimum.

Within original Colorado hourly re-solves, the 15-year median difference between siting schemes in extra firm-generation displacement from extending 4h to 8h was -246,795, -295,403, and -40,894 MWh at 40%, 50%, 60% wind, respectively. These operations-accounting contrasts are compatible with the local valley but mechanically relate to the economic LP objective; they do not uniquely prove an SOC-saturation cause.

### 3.3. Common renewable penetration control

A new, successful **180-LP Colorado R=1.5** physical source-only analysis joined 540 previously verified AZ/ID/WY LPs into a common-R=1.5, 50%-wind four-state horizon analysis. The median original economic LP siting effect across 15 weather-year pairs was **AZ -0.340861, CO +0.410384, ID +2.337690, WY +2.636534** model USD per additional kWh-year. The original Colorado R=2.0, 50%-wind paired median was **-2.177855**; thus the *median scenario effect* for Colorado switches sign between R=1.5 and R=2.0. Neither subtracting these medians nor comparing their magnitude establishes the median of a direct weather-year-paired interaction contrast. This sensitivity means the modeled geography effect is not a state-invariant constant.

### Table 1. Common-R=1.5 state contrasts at AC wind share 50%

The table reports the median *within-weather-year* paired value contrast, EIA-2025 county weights minus original ReEDS-2012 potential weights; SOC-only correlations are descriptive, not external predictions. Each state's comparison includes 15 source-weather years.

| State | R | Median siting contrast (model USD/added kWh-year) | Daily SOC r | Weekly SOC r | Annual SOC r | Daily sign matches | Weekly sign matches | Annual sign matches |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Arizona | 1.5 | -0.340861 | 0.019414 | 0.958747 | 1.000000 | 9/15 | 13/15 | 15/15 |
| Colorado | 1.5 | +0.410384 | 0.368747 | 0.919659 | 1.000000 | 12/15 | 15/15 | 15/15 |
| Idaho | 1.5 | +2.337690 | 0.143886 | 0.963586 | 1.000000 | 15/15 | 15/15 | 15/15 |
| Wyoming | 1.5 | +2.636534 | 0.826549 | 0.952937 | 1.000000 | 15/15 | 15/15 | 15/15 |

Primary provenance: GitHub Actions run 44919128370, official artifact 14714718140. The Colorado ratio-1.5 versus ratio-2.0 difference is between separately computed medians, not a direct paired ratio-interaction median.

### 3.4. Conditional storage-extension cost thresholds

Under the lowest selected ATB hurdle (Advanced case, 4% real rate; **16.049** ATB 2023 USD per additional kWh-year), **213/1,080** modeled incremental operating-value cases exceed that hurdle: 89 AZ, 60 CO, 34 ID, and 30 WY. By design cell: R=2.0, wind 25% has 120/120 exceedances; R=1.5, wind 25% has 61/120; R=2.0, wind 50% has 32/120; all R=1.0 designs and 75%-wind designs have zero. Advanced/7%, Advanced/10%, Moderate/4%, Moderate/7% yield 133, 93, 38 and **0** of 1,080, respectively, under their own thresholds. Aggregate 19,440 ATB comparison rows contain 954 exceedances, but duplicated numerical hurdles mean that total is not a count of independent experiments. Under the distinct fixed-2030 reference baseline at R=1.5, 50%-wind, **0/2,160** ATB comparisons exceed their corresponding hurdle; it cannot substitute for the entire 3×3 grid nor for the separate historical-demand cohort.

### Table 2. ATB2025-v2 conditional screening assumptions

Crossings count modeled 4-to-8-hour savings exceeding the given source-pinned cost extension hurdle among the **same** 1,080 model duration-value cases. Units for hurdle are ATB 2023 USD/(added kWh-year), while modeled value's currency year remains unreconciled.

| ATB 2030 assumption | Discount rate | Hurdle | Exceedances / 1,080 cases |
|---|---:|---:|---:|
| Advanced | 4% | 16.049 | 213 |
| Advanced | 7% | 18.501 | 133 |
| Advanced | 10% | 21.179 | 93 |
| Moderate | 4% | 24.175 | 38 |
| Moderate | 7% | 27.869 | 0 |
| Moderate | 10% | 31.902 | 0 |
| Conservative (Expand) | 4% | 32.699 | 0 |
| Conservative (R&D) | 4% | 29.715 | 0 |

The 18 source-labeled scenarios contain 12 distinct numerical hurdles; these are not 18 independent cost-data observations. Results reflect conditional threshold exceedance and do not demonstrate a project profit or investment NPV. Source: GitHub Actions 44463644688, artifact 14507169113.

### 3.5. Horizon and mechanism falsification checks

For the original predeclared state-specific R values (CO 2.0; other states 1.5), 15 years×four states×two siting schemes produced 120 full-year source-only cases and 720 independently optimized energy-transfer LPs. At fixed duration, feasible-energy nesting held, and maximum LP equality-balance residual was approximately 7.276×10^-12 MWh. Comparing weather-year paired input-only siting contrasts with frozen economic LP contrasts, the correlations at daily/weekly/continuous-year SOC horizons were AZ 0.019/0.959/1.000; CO 0.388/0.955/1.000; ID 0.144/0.964/1.000; WY 0.827/0.953/1.000. Across all four cohorts, matching effect signs occurred in 53/60, 58/60 and 60/60 weather-year pairs for daily, weekly and annual horizons, respectively. The continuous-year correlation of 1 is explained by near-exact objective proportionality, not independently validated physical causality.

In the new CO R=1.5 source-only cohort, daily/weekly/annual correlations were **0.368747/0.919659/1.000000**, with effect-sign matches **12/15, 15/15 and 15/15**. Results support caution about daily-reset approximations and the influence of feasible SOC horizons; high annual agreement is structurally expected for the present cost and energy constraints.

### 3.6. Limited observed BA shape diagnostic

A native 2023 EIA-930 Idaho Power BA shape comparison retained 8,743 valid matched UTC hours per fuel/scheme. Under zero-shift adjusted MW and normalized shapes, solar Pearson r was 0.9539 for source-potential weights and 0.9694 for 2025 EIA-county weights, whereas wind r was 0.7344 versus 0.7335. These are not like-for-like state fleet generation predictions; positive shifts can yield alternative descriptive correlations, and no offset was selected opportunistically as a new verified clock.

## 4. Discussion

The central model result is a design-dependent geography–mix interaction: county weighting influences the incremental storage-duration value differently as renewable wind mix and capacity penetration change, and the effect can change sign within one state under alternative penetration scenarios. This refines an overly strong claim that resource-potential versus operating-county weighting uniformly raises or lowers duration value. The Colorado 40/50/60% supplementary LPs and common-R=1.5 experiment address two distinct confounders—missing neighboring design cells and conflation of state and penetration ratio—but they do not establish general statistical inference for future climatic regimes.

Three levels of interpretation must remain separate. The frozen optimization objective and firm-displacement/curtailment accounting describe an internally consistent cost-minimization problem. Input-only surplus and deficit metrics capture weather-source timing with fewer optimization assumptions but can fail when power/SOC chronology is enforced. Optimized annual source-only energy transfer shares enough mathematical structure with the economic dispatch LP to yield nearly perfect agreement by construction. Consequently none of these alone supplies exogenous evidence of causation, congestion effects, realized market prices, or site-specific installed-generator dispatch.

The ATB comparison helps identify model designs where illustrative variable-cost avoidance approaches cost-extension thresholds, but fails to provide credible positive project NPV without common price-year currency, finance assumptions, full storage lifecycle costs, and an actual network and fleet. Case counts are finite scenario screens; 15 weather years and two geographic weights are paired model inputs, not randomized trials.

Additional constraints include use of historical ReEDS 2012 county resource shapes, fixed hypothetical 2030 demand, EIA 2025 operating-fleet county shares applied non-contemporaneously, source-point-to-hour convention sensitivity, fixed prices and simplified generation, and omission of network congestion and long-run adequacy. A high-quality real-grid validation would require a contemporaneous state/BA/plant fleet crosswalk, synchronized demand and generation, interval semantics, actual storage performance and location-specific network prices.

## 5. Conclusions

The apparent marginal modeled value of extending battery duration from 4h to 8h is conditional on renewable penetration, wind/PV mix, county resource weighting, weather year and storage time horizon. Under an illustrative 3×3 sensitivity grid, a subset of optimized scenarios crosses the lowest ATB extension hurdle, but those exceedances are not demonstrated financial viability. The Colorado county-weight median changes sign between two penetration settings at 50% wind, and neighboring wind mixes reproduce a local nonlinear contrast. Continuous-year source-only transfer agrees closely with economic LP value because the models are structurally related; shorter SOC horizons can materially alter the result. The appropriate generalization is therefore a reproducible modeled sensitivity, not a claim about observed 2030 Western U.S. grid dispatch or investment economics.

## Data and code availability and primary numerical provenance

Code and protected source-provenance records: [ys30/Energy-Transition-Analysis-PyPSA](https://github.com/ys30/Energy-Transition-Analysis-PyPSA), research branch `paper-s-reeds2022-hourly-join-gates` (unmerged draft). The external publisher's HDF5 and supply curves retain their original licenses and checksums; no blanket license is asserted over third-party files.

- Frozen 3×3 2,880 newly optimized LPs and 1,080 marginal duration cases: [run 44209543001](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44209543001).
- Exact 40/60% wind additional sensitivity: [run 44449229739](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44449229739).
- Colorado hourly mechanism and objective checks: [run 44453880808](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44453880808).
- Source-verified 19,440 ATB screen rows: [run 44463644688](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44463644688).
- Original 15-year full-annual 720-LP physical input-only comparison, recovered final artifact 14692567952: [run 44861775851](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44861775851).
- New common-R1.5 Colorado 180 LPs and 4-state artifact 14714718140: [run 44919128370](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44919128370).
- Fixed vs matched 720×720 comparison, artifact 14712877100: [run 44919128403](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44919128403).
- Observed-BA source-scope and shape gate: [verified screening record](PAPER_S_VERIFIED_3X3_ATB_DAILY_MECHANISM_IPCO_RESULTS_2026-11-19.md).
- Original source documentation and references: [publisher dataset bibliography QA](PAPER_S_ORIGINAL_REEDS_DATASET_BIBLIOGRAPHY_74_REFERENCES_QA_2026-11-18.md). The article's final scholarly bibliography must be rebuilt and independently verified before journal submission.

## Author and editorial release fields (to complete)

Affiliation and corresponding-author contact: author-approved final text required. Author contribution, funding statement, competing interests, dataset redistribution permissions, code license, deposited research DOI and journal-specific citations: pending author/editorial completion. No Zenodo DOI has been invented or represented as minted.

**Integrity rule:** This v2 manuscript source supersedes the November 12 four-year narrative for editorial review but does not overwrite it, the frozen optimal LP artifacts, or any Paper T / Project C-2 result.
