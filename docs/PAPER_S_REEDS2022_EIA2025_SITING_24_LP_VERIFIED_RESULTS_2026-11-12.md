# Paper S — VERIFIED 24 source-native EIA2025 county-siting 2012 weather × 2030 demand common-AC storage LP results (2026-11-12)

## Admission and source chain

**Successful verified run:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43159121663

**Archive artifact:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43159121663/artifacts/13917174380 (`paper-s-reeds2022-eia2025-county-siting-24-LP-comparison`), 5 files:
- `paper_s_2030_EIA2025_county_weight_vs_source_potential_24_LP.csv`: all 24 original 8760-hour HiGHS LPs, optimal/balanced.
- `paper_s_2030_EIA2025_vs_potential_8_battery_pairs.csv`: two siting schemes × four state 0/4/8h controls.
- `paper_s_2030_EIA2025_vs_potential_4_state_storage_value_effects.csv`: four exact potential/EIA siting comparisons including $10 energy-only threshold change.
- `paper_s_2012_4state_EIA2025_vs_resource_weighted_original_instantaneous_CF.csv`: original 8760 source-instantaneous wind/PV county-class state-aggregated profiles for both methods.
- `paper_s_EIA2025_siting_2012_weather_2030_demand_24_LP_manifest.json`: source and accuracy checks, scenario counts, explicit limitations.

Original ReEDS2022 2012 wind and PV county-class HDF5 MD5s independently verified: wind `0670813d0a18b688d698ca24cf67fb92`, PV `aba834ea4c592023bca47de2ba79e7ec`. Source county supply curves exact class × FIPS joined. The frozen potential-weighted CF were reproduced with maximum **absolute errors ~3–7×10⁻¹⁶** across four states and each technology. The original 12 common-AC source LP objectives matched the archived baseline to within the prespecified $0.10 absolute acceptance threshold. **All 24 LPs solved optimally and met hourly energy-balance guards.** Latest full repository CI [43159255382](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43159255382) completed successfully.

The EIA 2025 observed county shares were independently established from *operating* EIA-860 units, Census 2020 five-digit county FIPS, and matched state/technology (prior verified [43124063185](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43124063185)). The **within-county ReEDS source resource-class distribution remains potential-weighted**, because EIA generator inventory does not identify the matching source ReEDS meteorological class or plant-specific capacity-factor shape. Both geographic approaches hold state-wide hypothetical wind and PV AC installed nameplate at 1.5× peak load and 50% wind share: **the EIA 2025 observed *spatial shares*, not actual 2025 MW magnitudes, are transferred into 2030 nameplate scenarios**.

## Verified four-state operating results

All economic values below are annual reference-year *illustrative dispatch variable-objective savings* at firm variable cost $90/MWh, renewable $5/MWh, RTE 90%, battery power 25% peak; durations 0,4,8h. Demand is projected 2030; source meteorology is original 2012 fixed-CST reference instants and trapezoid-first-endpoint approximate hourly availability.

| State | 4h operating savings potential ($M) | 4h savings EIA county ($M) | 8h operating savings potential ($M) | 8h savings EIA county ($M) | 4→8h incremental operating savings potential ($M) | 4→8h incremental operating savings EIA county ($M) |
|---|---:|---:|---:|---:|---:|---:|
| AZ | 387.8498 | 383.9444 | 600.4394 | 575.4383 | 212.5895 | 191.4939 |
| CO | 162.2519 | 172.4154 | 233.5035 | 240.4895 | 71.2516 | 68.0742 |
| ID | 55.4871 | 67.9012 | 77.0048 | 98.0318 | 21.5177 | 30.1306 |
| WY | 27.5882 | 39.8830 | 38.4542 | 58.2282 | 10.8660 | 18.3451 |

The marginal 4→8h storage-energy-only annual annuity threshold, `H_E=(C_4-C_8)/(E_8-E_4)`, with kWh added energy denominator, is:

| State | Potential-weighted ($/kWh-year) | EIA2025 county-weighted ($/kWh-year) | EIA minus potential | Hypothetical $10 screen flipped |
|---|---:|---:|---:|---|
| AZ | 10.955400 | **9.868276** | **−1.087124** | **Yes** |
| CO | 6.220671 | 5.943267 | −0.277404 | No |
| ID | 4.134846 | 5.789886 | +1.655040 | No |
| WY | 3.540569 | 5.977560 | +2.436991 | No |

**Main verified finding: with the same demand/weather/total common-AC nameplate/variable costs/storage power and source technology class conditional weights, county geographic reweighting alone changes Arizona's *illustrative $10/kWh-year energy-cost-only* screening answer from positive to negative.** ID and WY's 4→8h marginal operating values rise strongly, but they remain below $10/kWh-year. Total variation of 2025 observed county siting vs ReEDS developable potential shares was 0.604–0.862 across the eight state × technology cells, verified in [43124063185](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43124063185). These TV metrics quantify **capacity distribution**, not directly the modeled CF energy or avoided operating cost.

## Proposed manuscript Methods statement

We independently reaggregated the original ReEDS2022 reference-year county × resource-class wind and PV capacity-factor matrices, assigning county fractions either by publisher developable resource potential or by EIA-860 2025 operating generator capacity (validated to exact U.S. Census 2020 county FIPS). Within each county, resource classes were retained in the relative proportions of the original ReEDS class-specific available supply-curve capacity rather than being interpreted as measured EIA turbine/vintage or site technology. The original potential-weighted hourly source-instantaneous curves were reproduced within machine precision against frozen independent source archives before calculating any counterfactual. Both scenarios used one-time PV DC-to-AC ILR conversion (1.34), exactly matching native source timestamps, original 2012 reference-weather profiles and projected 2030 hourly state demand. For the controlled dispatch comparison, all assumed renewable total AC nameplate (1.5× demand peak), AC wind share (50%), firm and renewable variable cost, 90% battery efficiency and 25% peak battery charging/discharging power were identical, varying only county siting fractions and the 0/4/8h storage duration.

## Proposed manuscript Results statement

An independently observed existing-fleet geographic perturbation materially affected modeled battery storage value. Using identical original 2012 source-resource weather and projected 2030 demand, changing resource-potential-weighted county wind/PV profiles to EIA 2025 operating-generator-county-weighted profiles lowered Arizona's marginal value of extending a 4h battery to 8h from $10.955 to $9.868 per additional kWh-year. The difference changed the binary conclusion for a deliberately illustrative $10/kWh-year incremental *energy-only* annualized cost screen. In contrast, the equivalent threshold was $6.221 versus $5.943 for Colorado, $4.135 versus $5.790 for Idaho, and $3.541 versus $5.978 for Wyoming (source potential vs EIA county siting, respectively). Although the geographic reweighting increased marginal duration value substantially in Idaho and Wyoming, none of those alternative cases met the hypothetical $10 energy-only ceiling. All 24 LPs solved optimally and the original source-potential weather profiles, as well as the corresponding LP objectives, independently matched archived frozen baselines. Thus the storage operating-value conclusions are not invariant to how plausible renewable site capacity is spatially assigned, even when the nominal state AC technology mix and installed nameplate are held fixed.

## Discussion and publication limits

This is **not** an observed time series of actual 2025 power generation, and not a validated 2030 installed fleet layout. EIA 2025 only determines county capacity *fractions*, with resource classes conditional on ReEDS potential; 2012 source HDF5 meteorology is not contemporaneous with the 2025 generator fleet; 2030 electricity demand is scenario-based. The original 2012 source hourly instants are **not independently certified as hour-integrated renewable MWh** and the 8760-label native reference includes leap day but excludes December 31. State copperplate dispatch omits transmission constraints, plant commitment, firm-capacity scarcity and reserve/adequacy, actual installed wind/PV class, losses, degradation and future weather repetitions. Battery CAPEX, O&M and capital financing are **not** included; the threshold is a maximum illustrative additional energy-cost annuity derived from avoided variable operating expenses, not bankable project profitability or net return.

A 24-LP controlled perturbation with 0/4/8h duration is not a statistical confidence interval and should not justify probability statements. ReEDS original source 2012 available-potential geometry is not equivalent to commercial capacity-siting forecasts. Source weather-year replication, independently hour-integrated generation data and multi-year demand/weather coupling remain scientific validity gates.

## Editorial implication

The original Paper S assertion that the AZ 4→8h marginal annuity is robust to source-geography choice cannot be made. The correct claim is that it is *conditional* not only on efficiency, avoided firm marginal cost and instantaneous-hour approximation, but also on geographic siting weights. This should be a main-text sensitivity result, not suppressed in supplementary material. Recommended candidate table: the four-row marginal $/kWh-year comparison and threshold flips above. Retain source potential baseline as the primary methodological scenario; EIA county weights are an external observational-siting spatial perturbation, not a definitive actual future result. Keep manuscript and PR Draft pending physical source-interval and weather-years validation.
