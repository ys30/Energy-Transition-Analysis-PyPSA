# Paper S — integrated English manuscript draft v1 (2026-11-12)

**Working title:** Weather-Dependent Storage Duration Value under Renewable Resource Potential versus Observed County Siting: A Source-Audited Four-State U.S. Dispatch Study

**Manuscript status:** integrated narrative draft, not a submitted article or certified physical-grid forecast. All numerical claims below are traceable to completed GitHub Actions in Data and Code Availability. Academic literature references, manuscript-quality final layout, graphical QA, and independent physical-hour generation semantics remain for submission.

## Abstract

The value assigned to longer-duration battery storage depends on renewable generation timing, which can vary with both geographic capacity placement and weather realization. Yet spatially aggregated capacity-factor profiles are frequently weighted by available development potential rather than the geography of operating generators. We examine this distinction in a source-audited linear dispatch experiment for Arizona, Colorado, Idaho and Wyoming. Authentic ReEDS2022 county-by-resource-class wind and utility-scale photovoltaic source profiles were aggregated using two alternative county weights: original developable supply-curve potential and independently mapped 2025 EIA-860 operating-generator nameplate. Source wind/PV time samples and 2030 state demand use an explicitly documented original 2012 reference support. Four historical ReEDS weather references (2010–2013) were compared in 96 matched state × weather × siting × battery-duration (0/4/8 h) linear programs under fixed hypothetical common-AC renewable capacities. Geographic shares differed markedly between observed 2025 operating generators and resource potential (county total variation 0.604–0.862 over eight state–technology comparisons). In Arizona, changing county weights reduced the marginal 4-to-8-hour storage operating-value ceiling from $10.955 to $9.868 per added kWh-year using 2012 weather, reversing a hypothetical $10/kWh-year energy-only cost screen. However, this screen did not reverse with 2010, 2011 or 2013 weather. Thus geographic aggregation affects modeled storage value, while individual threshold crossings depend on weather reference and economic assumptions. The experiment is a conditional operating-cost sensitivity, not a 2030 installed-fleet or climate-change forecast; original point-sampled capacity factors are not independently certified as hour-integrated generation.

**Keywords:** battery duration; renewable siting; county aggregation; ReEDS; EIA-860; historical weather variability; electricity dispatch; source provenance.

## 1. Introduction

Additional battery storage duration can reduce fuel-intensive electricity dispatch by shifting renewable generation to hours of higher residual demand [R1, R2]. An operating-cost benefit, however, does not alone establish a bankable project investment: the incremental energy capacity must be compared with appropriate annualized capital, financing, replacement and other costs. Estimates based on stylized generation profiles can be especially sensitive to the hourly correlation of wind, solar and demand.

A separate modeling issue is where aggregated wind and photovoltaic capacity factors come from. The ReEDS framework has an established published model history [R5], although that background does not certify the particular hourly semantics of the 2022 data products used here. Regional developer-resource datasets provide high-resolution resource-class and geographical availability, but their county potential weights describe feasible resource opportunity, not necessarily the county distribution of existing or subsequently planned generators. These populations differ for economically meaningful reasons such as site development, transmission access and local permitting. Consequently, even when a regional model holds total nominal renewable capacity constant, a potential-weighted regional time series may differ from one based on the geography of observed operating facilities.

Weather-year choice is a further potential confounder. A threshold crossing observed with one year's meteorological reference may disappear with another year's renewable timing. In contrast, a weather-dependent response in the continuous operating-value difference can be scientifically informative without implying any particular long-term crossing frequency or climate-change projection.

We examine three bounded questions. First, how different are authentic developer-potential county weights from operating generator county capacity shares in four Western U.S. states? Second, how do these weights alter a controlled storage-duration dispatch comparison with fixed total renewable AC nameplate? Third, how does the resulting sensitivity change across four source-authenticated historical weather references? We emphasize numerical provenance, source-year calendars and independently replicated baseline solutions while maintaining explicit separation between a scenario's operating-cost ceiling and real-world investment returns.

## 2. Materials and methods

### 2.1. Geographic and temporal source inputs

We selected Arizona (AZ), Colorado (CO), Idaho (ID) and Wyoming (WY). ReEDS2022 original county-class wind and utility-PV capacity factor HDF5 files and original county resource supply-curve tables [D1] were authenticated against archived publisher MD5 digests and exact resource-class × five-digit county FIPS keys. Weather-source HDF5 files contained 15 native reference years with 8,760 source observations each: 2007–2013 and 2016–2023. The source wind and PV time indexes matched exactly. Source leap years 2008, 2012, 2016 and 2020 include February 29 but exclude December 31. Observations are source *instantaneous capacity factors*, not independently verified electricity-energy integrals over their preceding hours.

A separate official ReEDS2022 2030 reference demand product was used as the fixed 8,760-interval state load. Its native source time labels were audited against the original 2012 reference support in fixed CST (UTC−06:00), with no assumption that matching labels alone certifies real-hour generation integration. We used 2010, 2011, 2012 and 2013 renewable weather references for the controlled interannual sensitivity and maintained the same projected 2030 demand for each.

For nonleap 2010, 2011 and 2013 weather references, source capacity factors were mapped to the unusual publisher 2012 demand-reference support by exact month–day–hour matching. The missing February 29 was **synthetically interpolated** by taking the same-hour mean of February 28 and March 1; original December 31 source data were excluded to retain 8,760 target intervals. For the native 2012 weather reference, no imputation was needed. Both the synthetic-February and excluded-December CF-hour sums and their difference were recorded; these changes introduce a bounded numerical mapping assumption and do not reconstruct actual observed February 29 weather.

### 2.2. Operating generator geographic shares and county potential

EIA's official 2025 annual EIA-860 `Operable` generator records [D2] were filtered to operating status `OP` and technology-consistent onshore wind (`WT/WND`) or utility-scale photovoltaic (`PV/SUN`). Exact plant codes were used to join the official Plant county and state fields. County names were independently matched by state to published 2020 Census county FIPS, without fuzzy state-crossing assignment. Capacity mapping coverage was 100% among the operating generator records selected for all eight state–technology cells, but this does not establish completeness for excluded facilities or smaller distributed solar.

For state `s`, technology `j`, and county `c`, the two alternative weights were
\[
w_{c,j,s}^{pot}=\frac{\sum_k M_{c,k,j,s}^{pot}}{\sum_{c,k} M_{c,k,j,s}^{pot}},\qquad
w_{c,j,s}^{EIA}=\frac{M_{c,j,s}^{OP,2025}}{\sum_c M_{c,j,s}^{OP,2025}},
\]
where `k` indexes source meteorological resource classes. Wind source development potential is in MW AC; original solar development potential is in MW DC, whereas EIA generator nameplate is reported on its AC basis. We compare only normalized **within-technology county shares**, not sums of AC and DC physical capacities.

For each county, the source class profile remained weighted by the original ReEDS potential `M^{pot}_{c,k,j,s}`. The aggregated native technology CF was `CF_{j,s,t}=Σ_c w_{c,j,s} Σ_k p(k|c,j,s) CF_{c,k,j,s,t}`, with `p(k|c,j,s)=M^{pot}_{c,k,j,s}/Σ_k M^{pot}_{c,k,j,s}`. Thus the EIA scenario changes county placement fractions alone; it does not identify observed generator vintage, tracker specification, turbine class or actual production at an EIA site.

### 2.3. Controlled common-AC dispatch experiment

To compare renewable technologies with a shared nameplate denominator, original PV output-to-DC-array-capacity CF was converted **once** using the publisher inverter loading ratio, ILR 1.34, to an illustrative PV AC-nameplate CF. A small source-decimal-rounding excess above unity was guarded and clipped only within the documented tolerance. Source instantaneous wind and PV CF were approximated as interval generation availability using a prespecified noncyclic trapezoid between adjacent source instants; the first interval used the first source endpoint because a prior measurement is absent. This is an explicit assumption, not publisher-certified past-hour integration.

In each state the hypothetical total renewable AC nameplate was set to 1.5 times the projected peak demand, with 50% allocated to wind AC and 50% to PV AC. A battery's charge/discharge power limit equaled 25% of projected peak demand, and its energy capacity was compared at 0, 4 and 8 hours of that power rating. Round-trip efficiency was fixed at 90% (symmetric charge/discharge efficiencies of `sqrt(0.9)`). Renewable and firm variable costs were $5/MWh and $90/MWh, respectively. **The implemented firm generation power bound is 1.2 times projected peak state demand in every interval**, an assumed availability ceiling and not a calibrated real power-plant capability. The state was represented as an uncongested copperplate with no inter-state transfer or transmission constraint.

For each time interval, the LP minimized variable renewable and firm dispatch costs subject to renewable allocation, demand balance, battery power and energy capacity, and storage intertemporal SOC balances. **The implemented initial SOC is zero, and terminal SOC is also constrained to zero**; this is a fixed empty-to-empty annual boundary, sometimes loosely called a cyclic SOC condition, but not a free cyclic inventory state. There are no minimum-generation, ramping or unit-commitment constraints. Model costs do not include a nonzero battery discharge throughput penalty in the reported scenarios. The no-storage case uses zero battery power/energy. Optimizations were solved with the **custom SciPy `optimize.linprog(method='highs')` formulation** [R3], as implemented in `src/energy_transition/efs_cyclic_storage_lp.py`; the 96 reported LP cases were **not solved as PyPSA networks**. PyPSA [R4] is relevant project/framework background only. Only optimal solutions passing the specified primal energy-balance residual checks were accepted.

Define the annual illustrative objective `C_h` for a battery of duration `h`. The incremental *energy-only* operating-value ceiling of extending 4 h to 8 h is
\[
V_{4\to8}=\frac{C_4-C_8}{1000(E_8-E_4)}
\quad\mathrm{USD/(additional\ kWh\,year)},
\]
where `C` is measured in USD per modeled reference year and `E` in MWh. It estimates the annual additional energy-capacity cost that the **modeled avoided variable operating cost alone** could cover. It excludes capital expenditures, charging market revenue, financing and net project valuation. A $10/kWh-year incremental energy-capacity-only hypothetical screen was used solely as an interpretable threshold example.

### 2.4. Source audits and replication gates

The archived 2012 original county potential-weighted state CF curves were independently reconstructed from the same raw HDF5 at numerical precision, before EIA county weight changes were admitted. All source wind and PV HDF5 digests, supply curves, annual indexes and 2025 EIA county mapping were checked. A separate 2012 24-LP spatial comparison passed, followed by 96 full 8,760-interval LPs across four weather years. All 24 exact 2012 LP objective anchors in the later 96-LP experiment were required to reproduce the prior archived run within $0.10; the observed maximum deviation was $0.004863. Fail-closed guards prevent inventing missing source weather years or silently assigning unmatched EIA sites.

## 3. Results

### 3.1. Original-source weather calendars and observed operating-generator county coverage

The native source weather index was not a simple consecutive sequence of 15 civil years. The exact set was 2007–2013 plus 2016–2023, each containing 8,760 observations with matched wind/PV indexes and no within-year nonhourly gaps. The previously attempted use of 2014 was correctly rejected because those source records did not exist. Original source leap-reference segments retained February 29 but omitted December 31. The independent EIA Plant/Generator-to-Census county mapping covered the entire included 2025 operating wind/PV nameplate in each of the eight state–technology groups.

### 3.2. Observed operating generator siting differs from available development potential

ReEDS resource potential and the EIA 2025 operating capacity shares differed materially among counties. County total variation between the normalized weight vectors was 0.604 (AZ wind), 0.706 (AZ PV), 0.734 (CO wind), 0.671 (CO PV), 0.781 (ID wind), 0.814 (ID PV), 0.693 (WY wind) and 0.862 (WY PV). The 2025 Wyoming PV inventory represented 242 MW AC in two operating-generator counties, whereas the ReEDS potential source identified positive photovoltaic development potential in 23 counties. This finding identifies structural differences in source weight populations; it does not itself quantify weather resource profile or storage value differences.

### 3.3. Single-year controlled storage sensitivity: 2012

Holding projected demand, assumed total wind/PV AC nameplate, 50% wind share, battery power/efficiency, source weather and variable operating costs fixed, the source-potential versus EIA-2025-county-weighted marginal 4→8 h energy-only operating value was **$10.955 versus $9.868/kWh-year for AZ**; **$6.221 versus $5.943 for CO**, **$4.135 versus $5.790 for ID**, and **$3.541 versus $5.978 for WY**. Therefore the illustrative $10 additional energy-cost screen reversed under the siting perturbation for AZ in 2012 alone. These are avoided reference-year operating-cost values from an uncongested LP, not investment returns.

### 3.4. Cross-weather-year interaction in 96 source-native LPs

The 2010–2013 four-year comparison consisted of 96 independently optimal LPs, with 32 matched 0/4/8 h duration triplets and 16 matched year×state geographic comparisons. Their source-index and solver validations succeeded. Arizona's potential-weighted versus observed-operating-county-weighted incremental duration operating-value ceilings ($/kWh-year) were **11.068 vs 10.727 (2010), 12.017 vs 11.421 (2011), 10.955 vs 9.868 (2012), and 12.821 vs 12.842 (2013)**. In the first three weather years, EIA reweighting lowered Arizona's value; in 2013 the estimated difference was slightly positive. **Only 2012** crossed the deliberately illustrative $10 screen under a change in geographic weights.

For Colorado, the comparable paired values were 5.562/5.948, 6.178/5.832, 6.221/5.943, and 5.619/5.826 over 2010–2013. Idaho was 2.993/5.645, 3.146/6.208, 4.135/5.790 and 3.467/5.274. Wyoming was 3.169/5.439, 3.864/6.651, 3.541/5.978 and 2.672/5.044. None of these latter three state cases crossed $10 under either spatial weighting in the selected four-year weather panel.

Thus the only screen reversal occurred in **one of 16 deterministic year–state pairs**, which cannot be interpreted as a probability. The broader comparison supports geographic siting as a determinant of the modeled continuous operating-value sensitivity under the fixed scenarios, with interactions that depend on historical weather reference. Figures should prioritize the full four-state four-year response rather than only the 2012 AZ threshold example.

## 4. Discussion

### 4.1. Why source spatial weighting matters

Available resource potential represents a much broader geographic opportunity set than the realized operating generator inventory, which is affected by economic development constraints. The eight county total variation distances, together with effective county concentration from the source audit, show that potential-weighted regional CF need not represent the installed 2025 wind or PV fleet. Keeping the total hypothetical AC MW and nominal state technology mix constant isolates a scenario-level county-siting component of the difference in aggregated source renewable timing. However, an observed county siting fraction is not actual wind/PV resource-class identification within county; the counterfactual does not reconstruct generation data of reported EIA units.

### 4.2. Weather realization conditions economic screening conclusions

The 2012 Arizona crossing demonstrates that an economic interpretation tied to one cost threshold may differ across plausible geographic weighting schemes. The four-year experiment materially refines that result: the geographic change influences the continuous annual value in each weather year, but the binary cost screen reverses only in 2012. Hence it would be misleading to declare that observed siting systematically removes 8h storage attractiveness. For AZ in 2010, 2011 and 2013, both geographic treatments remained above the illustrative cost screen. In Idaho and Wyoming, EIA county weights increased the modeled storage energy-value ceiling in all four reference years, though none reached the illustrative $10 cost. These changes represent model outcomes conditional on static 2030 demand and the source-year mapping, not future annual dispatch forecasts.

### 4.3. Economic and physical limitations

The LP's avoided variable cost per additional kWh-year is not storage revenue, an optimal system buildout decision or bankable NPV. It includes neither battery CAPEX nor annualized cost components associated with financing and lifecycle. Network-level deliverability, resource adequacy, reserve provision, thermal ramping, scarcity effects and multi-area exchanges are excluded. The 2012 resource weather, 2025 EIA geographic shares and 2030 projected load are noncontemporaneous, so these inputs construct a controlled numerical experiment rather than observed physical operations.

The largest unresolved source-validity issue is the original publisher's *instantaneous* renewable CF versus the hour-ending demand interval: our noncyclic trapezoid is a prespecified approximation, not an independently authenticated hour-integrated production series. Alternative point-hold versus trapezoid checks previously bounded a particular numerical sensitivity but cannot substitute for publisher documentation or observed integrated-hour energy. Nonleap 2010/2011/2013 leap-day interpolation similarly inserts 24 synthetic samples while discarding December 31 source observations. These assumptions are explicit, recorded in 64 calendar diagnostics, and limit precision near an arbitrary screening threshold. A larger fully calendar-matched dataset and independent actual renewable generation are necessary before claims about real-system annual effects.

## 5. Conclusions

The way renewable capacity is spatially allocated can materially change modeled marginal operating benefits of extending battery storage from four to eight hours, even with constant hypothetical state renewable capacity, wind/PV AC composition and battery design. Authentic developer-resource potential and 2025 operating-generator county fractions differ strongly in all eight state–technology cases. Across four original historical weather references and 96 optimized scenarios, geographic reweighting altered modeled operating-value ceilings, but a $10/kWh-year illustrative screening reversal in Arizona was confined to the 2012 source weather reference. This weather-conditioned result cautions against treating resource-potential-weighted state renewable CF or any single reference year as a robust prediction of actual storage profitability. The available evidence supports a reproducible structural scenario analysis, not an installed-2030 fleet forecast, climate-change attribution, or physically certified hour-integrated energy calculation.

## Data and code availability

All public input links and authenticated digests are specified in the repository evidence audit and output manifests. Original county-class ReEDS wind resource file: https://zenodo.org/records/18422200 ; PV: https://zenodo.org/records/18407660 ; reference demand: https://zenodo.org/records/18461543 ; official EIA-860 annual release: https://www.eia.gov/electricity/data/eia860/ ; official Census county codes: https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt .

Source code and prespecified data/LP validations are in [GitHub Draft PR #2](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/pull/2). Independently successful original [15-year source calendar workflow 43281182402](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182402), [EIA-860 county geographic validation 43124063185](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43124063185), [24 2012 geographic LP 43159121663](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43159121663) and [96 four-weather LP 43281182390](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182390) provide immutable run identities and downloadable original CSV/JSON archives. Their GitHub workflow results and source files take precedence over any rounded article table. The 96-LP new main-text figure and heatmap have a separate dedicated source-validating workflow; insert only after success.

## References and original data sources

[R1] Zerrahn, A., Schill, W.-P., & Kemfert, C. (2018). On the economics of electrical storage for variable renewable energy sources. *European Economic Review*, 108, 259–279. https://doi.org/10.1016/j.euroecorev.2018.07.004

[R2] Sepulveda, N. A., Jenkins, J. D., de Sisternes, F. J., & Lester, R. K. (2018). The role of firm low-carbon electricity resources in deep decarbonization of power generation. *Joule*, 2(11), 2403–2420. https://doi.org/10.1016/j.joule.2018.08.006

[R3] Virtanen, P., Gommers, R., Oliphant, T. E., et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. *Nature Methods*, 17, 261–272. https://doi.org/10.1038/s41592-019-0686-2

[R4] Brown, T., Hörsch, J., & Schlachtberger, D. (2018). PyPSA: Python for Power System Analysis. *Journal of Open Research Software*, 6(1), article 4. https://doi.org/10.5334/jors.188 (framework/software context only; not this study's LP solver).

[R5] Ho, J., Becker, J., Brown, M., et al. (2021). *Regional Energy Deployment System (ReEDS) Model Documentation: Version 2020*. NREL/TP-6A20-78195. https://www.nrel.gov/docs/fy21osti/78195.pdf (general ReEDS framework context; not validation of this study's 2022 data-release interval semantics).

[D1] ReEDS original county-class onshore wind and utility-PV resource HDF5 and county source-capacity files, plus EFS reference demand dataset: https://zenodo.org/records/18422200 ; https://zenodo.org/records/18407660 ; https://zenodo.org/records/18461543 . Full publisher release-author metadata and licenses require source-level final formatting review.

[D2] U.S. Energy Information Administration. Form EIA-860 annual detailed generator data, 2025. https://www.eia.gov/electricity/data/eia860/

[D3] U.S. Census Bureau. 2020 national county FIPS code text file. https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt

**Reference provenance:** [verified source/library and method attribution register](./PAPER_S_VERIFIED_REFERENCE_LIBRARY_AND_METHOD_ATTRIBUTION_2026-11-12.md). Source experiment run IDs are cited in the Results and Data and Code Availability sections; literature references do not substitute for those audits.

## Manuscript completion items (not scientific findings)

The reference list must be assembled from verified publisher and peer-reviewed studies; target journal author instructions, final numbering, affiliations, acknowledgments, disclosure and repository release/DOI metadata remain to be finalized. The manuscript must not be described as submitted or accepted. Review sections on physical hour-energy semantics, 2012 calendar support and 2025 siting-vintage mismatch before any final editorial claim of external grid validity.


## Verified candidate main-text figure captions (accepted external artifact)

**Figure 4a — County siting–weather interactions in marginal storage duration operating value.** Four state panels display the 4→8 h battery energy-only operating-value ceiling (USD per added kWh-year) for ReEDS original development-potential-weighted renewable counties and 2025 EIA-860 observed operating-generator county-capacity shares, paired within each of four historical original ReEDS source-weather references (2010–2013). The dashed $10/kWh-year line is a deliberately illustrative *incremental storage-energy-only* annual cost screen; the weights straddle this threshold only in Arizona 2012 (source-potential 10.955 vs EIA 9.868). Each combination uses projected 2030 load, original county-class source resource fractions conditional on county, fixed nominal total common-AC wind+PV 1.5× peak, wind 50%, battery power 25% peak, η=0.9, $5/MWh renewable and $90/MWh firm variable costs, with empty initial and empty terminal SOC. The four years are historical reference weather, not future climate projections or independent observations of 2030 generation. Nonleap source years use *synthetic* 24-hour February 29 interpolation and exclude original December 31 to align with the publisher 2012 reference support. Input profiles are point-sampled CF with a numerical approximation to hourly availability, not physically certified integrated hourly generation. Source: verified [original 96-LP run](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182390). Reproducible accepted figure: [workflow 43288856607](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43288856607), [PNG and PDF artifact 13976367223](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43288856607/artifacts/13976367223).

**Figure 4b — EIA observed operating county share minus developer potential weighted storage operating-value ceiling.** Signed values (USD per added kWh-year) derive from the same 16 state × original weather-year pairs and 96 LPs. Positive values mean the EIA-2025-county fraction *increases* the modeled 4→8 h incremental annualized operating-cost avoidance relative to source developer-potential geography, not actual profit. Colors express numerical paired differences; no confidence interval, probability or future climate model is implied. Both spatial source schemes hold hypothetical 2030 total wind+PV AC capacity and storage technology parameters constant. Original reference-year calendar alignment, resource-class conditional weights, point-source CF and 2025→2030 observed-siting limitations match Figure 4a. [Accepted original figure and heatmap artifact 13976367223](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43288856607/artifacts/13976367223).
