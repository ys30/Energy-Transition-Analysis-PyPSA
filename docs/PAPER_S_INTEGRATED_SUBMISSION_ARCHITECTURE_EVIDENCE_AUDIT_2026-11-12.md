# Paper S — integrated Q1-journal submission architecture and editorial evidence audit (2026-11-12)

**Artifact type:** submission integration blueprint, not a falsely labeled completed journal article. The 36,804-character [rolling Results/Discussion addendum](./PAPER_S_COMMON_AC_MANUSCRIPT_RESULTS_DISCUSSION_DRAFT_2026-11-11.md) contains repeated preliminary methods and headings (3.5–3.8, 4.3–4.6) and should **not be submitted unchanged**. This document specifies a single coherent paper structure, exact authenticated primary evidence, figure/table allocation, exclusions and outstanding science needed for a defensible review.

## Working English title

**Weather-Dependent Storage Duration Value under Renewable Resource Potential versus Observed County Siting: A Source-Audited Four-State U.S. Dispatch Study**

Do not call this a historical causal impact analysis, a projected 2030 realistic fleet valuation, a physically verified hour-integrated wind/PV reconstruction, or future climate prediction.

## One-sentence central claim

Under a controlled state copperplate linear dispatch model with original source-based renewable resource reference weather and projected 2030 demand, **renewable county siting weights affect the modeled 4-to-8-hour storage operating-value ceiling; the signed county effect is consistent across two hourly point-to-interval approximations in 15/16 historical weather-year/state comparisons, whereas an illustrative $10/kWh-year Arizona 2012 screening reversal **fails** the method-robustness check**.

## Proposed complete submission architecture

1. **Abstract** (190–230 words): motivation → source audit → four-state model + 2025 observed county counterfactual → 2010–2013 weather panels → central continuous effect + AZ example → caveat.
2. **Introduction** (850–1,050 words): storage 4-to-8-hour economics, geographic aggregation bias, source-weather/calendar validity; research questions RQ1 physical input authenticity, RQ2 county siting sensitivity, RQ3 cross-year weather interaction. Do not imply county share is a validated 2030 capacity forecast.
3. **Data and Methods** (1,400–1,800 words): 2022 ReEDS county-class wind/PV authentic supply curves and HDF5, original 15 weather-year native index, 2025 EIA-860 OP generator/plant-Census county join, source CF AC and PV DC→AC ILR=1.34 once, nonleap month/day/hour remap, 2012 fixed-CST reference, projected 2030 demand, constrained 0/4/8h LP, formula for illustrative marginal energy-only operating-cost annuity and assumptions. Directly describe any 24 synthetic Feb29 points.
4. **Results** (1,100–1,400 words): §3.1 exact source + county mapping QA; §3.2 observed-capacity-vs-potential county spatial discrepancy; §3.3 controlled original 2012 24 LP; §3.4 2010–2013 matched 96 LP weather-by-siting. Treat $10 screen as a sensitivity illustration rather than the main dependent variable.
5. **Discussion** (900–1,150 words): why potential-weighted resource curves differ from existing fleet shares, asymmetric AZ/ID/WY value response, weather×county-siting interaction, inability to generalize 2012 crossing, implications for scenario-based planning, distinction from climate-change attribution and net battery profitability.
6. **Limitations** (350–500 words): point CF vs hourly integrated generation, missing Dec31 in native leap years, 24 interpolated Feb29 hours in each nonleap comparator, noncontemporaneous 2012 meteorology/2025 siting/2030 demand, within-county source class unobserved in EIA, no network, ramp, reserves/adequacy, SOC/terminal details, 2025 facilities not projected 2030 installed fleet, no battery CAPEX/financing, four-year deterministic panel not probability sample.
7. **Conclusions** (150–220 words), **Data and Code Availability**, **Author contributions**, **Declaration of interests**, References. Preserve native publisher/Zenodo original links and original digest values. Do not fabricate journal publication approval.

## Main-text figure allocation (four evidence-based panels)

| Candidate | Role | Source artifact | Admission |
|---|---|---|---|
| Figure 1 | Schematic flow from county-class publisher CF + county available MW to four states; EIA original OP plant/county to independent Census FIPS, then LP designs | Original verified source audit 42962740548; observed 2025 fleet county audit 43124063185 | Diagram only; state assumptions in caption; no fabricated graphic provenance |
| Figure 2 | Eight AZ/CO/ID/WY wind/PV counties spatial-weight TV / effective county weights | Verified external geographic comparison 43124063185 | QA supported, main-text or supplement depending journal space |
| Figure 3 | Secondary controlled 2012 source potential vs EIA county weight annual 4→8h annuity | Verified 24 LP 43159121663; figure artifact 13962299804 | **Supplementary recommended:** $10 AZ screen disappears with alternate hourly treatment (192 LP verification 43317414772); do not present its crossing as robust |
| Figure 4 (recommended lead) | 2010–2013 four-state panels for ReEDS potential and EIA county siting, $10 illustrative screen plus a state×year EIA-minus-potential heatmap | Verified **96 LP 43281182390** and weather calendar audit 43281182402. Publication figure workflow **43288856607 succeeded** (source archive artifact 13976367223). Add hour-method 192 LP audit 43317414772, artifact 13989123990. | **Main** continuous sensitivity; Figure 4a–b show trapezoid convention, disclose 15/16 direction agreement and unstable AZ $10 screen in caption |

## Main-text table allocation (three tables; rest supplement)

- **Table 1 — Model and input authenticity:** demand 2030, original 2012 reference and four 2010–2013 weather years, EIA 2025 operating county fractions, wind AC and PV DC→AC conversion, fixed 1.5× renewables-to-peak, 0.5 wind share, 0.25 storage power-to-peak, 90% RTE, source variable firm $90/MWh, renewable $5/MWh. Distinguish model assumptions from publisher facts.
- **Table 2 — External actual siting vs developer resource potential:** 8 state×tech rows, observed 2025 OP MW_AC, 100% census-mapped among included EIA units, observed/potential effective county N, source TV 0.604–0.862. Note EIA source coverage and conditional within-county class assumption.
- **Table 3 — Cross-weather 4-to-8h duration operating-value ceilings:** source-authenticated 4×4 state/weather grid: pairs ReEDS potential and EIA operating county $/kWh-year. The sole illustrative $10 binary flip is **AZ 2012**, one of 16 deterministic matched state-weather comparisons, **not** a 1/16 predictive probability.

## Verified result controls

- Publisher ReEDS original wind HDF5 MD5 `0670813d0a18b688d698ca24cf67fb92`, solar original HDF5 `aba834ea4c592023bca47de2ba79e7ec`. ReEDS potential CSV wind `49ab4e41dc386453b5fd32e5810774d4`, solar `e10b1a64f3a67d163e739b735938eb78`; projected demand original `7b2055d43200744a16a8c4fed68b1a17`.
- EIA 2025 observed in-operation solar/wind source plant-generator + Census county FIPS: eight state×tech source county population support with 100% mapped nameplate coverage among selected units. These are 2025 snapshots, not future 2030 generator placements. Original site potential vs observed capacity TV 0.604–0.862.
- Verified four-year 96 LP workflow [43281182390](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182390), [artifact 13976060428](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182390/artifacts/13976060428), all optimal, 2012 frozen 24 LP objective max absolute difference **$0.004863** (pre-specified threshold $0.10).
- Wind and PV weather-source HDF5 15-year clock audit [43281182402](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182402), [artifact 13976245398](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182402/artifacts/13976245398). Actual source weather years: 2007–2013, 2016–2023; 2014/2015 absent. Original leap-weather years truncate Dec31, retain Feb29.
- For AZ 2010–2013 source-potential vs EIA siting annuity ceilings: `11.067844/10.726983`, `12.016612/11.421001`, `10.955400/9.868276`, `12.821096/12.842341` $/kWh-year. Thus only 2012 changes the illustrative $10 energy-only cost judgment. Other states CO/ID/WY remain below $10 in all four years.
- The previously published **216-LP source-hour approximation sensitivity** held source conditions and showed 0/36 illustrative decisions flip; it cannot establish authentic hour-integrated wind/PV energy and should be retained as Supplement S rather than a competing core central claim.
- Do not revive the discontinued 2020 EFS ordinal-hour or synthetic Wave A/B conclusions as authentic source ReEDS source 2012/2030 results; cite only when explaining the archive history.

## Minimum remaining submission-quality gates

1. **Statistical and scientific framing:** four deliberately chosen authenticated historical weather years are a scenario sample, not representative climate uncertainty. Avoid 95% CI, weather frequencies or significance tests without justified sampling.
2. **Source hour-energy semantics:** neither instantaneous point-CF nor the numerical approximation alone certifies physical hourly generation. A publisher-documented conversion or measured hour-integrated output remains needed for physical calendar validation.
3. **Observational meaning:** EIA 2025 county share alone does not match ReEDS resource class/vintage, installed capacity forecast, or climate-change effects; mark every caption and results paragraph.
4. **Calendar sensitivity:** track and discuss synthetic Feb29 and excluded Dec31; compare an alternative nonleap control if the editorial claim depends on fine cost screen differences.
5. **LP physical scope:** one copperplate per state, no network/reserve/commitment/financial investment valuation. Publish explicit cyclic-terminal SOC assumption consistent between Methods and Discussion, never contradictory zero terminal SOC text.
6. **Journal format:** integrate genuine Introduction, systematic academic references, full consolidated Methods, an abstract and reproducible captions into a single complete manuscript rather than submitting rolling addenda. Obtain target journal's current format and author instructions prior to final DOCX build.

## Editorial conclusion

**The highest-value result is the year-varying *continuous* operating-value response to observed county siting fractions.** The AZ 2012 illustrative $10/kWh-year reversal appears only with trapezoid-mode source CF, **not** endpoint hold; it must not be elevated to a weather-robust **or** hour-discretization-robust economic finding. Verified 192 LP source run 43317414772 found 15/16 state–weather geographical-effect signs agree between methods; AZ 2013 alone has small opposite signs (−0.081 versus +0.021 $/additional kWh-year). A full external publication check is still needed; this document makes scope and the remaining tasks explicit rather than artificially certifying submission readiness.


## Editorial revision — verified 192-LP hour-conversion boundary (2026-11-13)

This addendum **supersedes** any earlier description that the AZ 2012 $10/kWh-year crossing is a repeatable result under source-hour treatments. The original wind/PV reference files are *instantaneous* CF samples; projected load is hour-ending. `end_instant_hold` and `trapezoid_with_first_endpoint` are both author-defined approximations, not publisher-certified hourly energy. The [original-source 192-LP matched 2×96 study](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43317414772) succeeded with [eight audited files](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43317414772/artifacts/13989123990). In AZ 2012, endpoint hold gives 11.900281 (resource-potential) versus 10.875999 (EIA county), both above the illustrative $10 screen. Trapezoid gives 10.955400 versus 9.868276 and crosses. **Main text should foreground the continuous 15/16 signed agreement** with the nonrobust threshold as an explicitly labeled example.

**Figure admissions:** The source-validated four-state×four-year [Figure 4a/4b graphics pipeline](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43288856607) succeeded, but the files plot **trapezoid values only**. Captions and editorial panel must always report sensitivity to source-hour approximation, including AZ 2012 crossing nonrobustness. A new 192-LP chart is optional only if it improves narrative clarity; the paired tabular values and main text already document the important result.

**Submission status:** Complete project CI and editorial checks passed at [43323774425](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43323774425). Remaining: figure/caption final layout, exact citations and reproducibility release, independent integrated-hour physical validation or explicit limitation accepted by target journal, and author/journal metadata. No further parameter sweep required by default.
