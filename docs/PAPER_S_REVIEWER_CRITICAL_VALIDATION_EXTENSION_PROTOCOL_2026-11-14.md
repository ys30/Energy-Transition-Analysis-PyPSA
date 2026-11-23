# Paper S — reviewer-critical external validation and 15-weather-year extension
Date: 2026-11-14. **Prespecified design ONLY; no new LPs or external empirical validation are claimed.** Preserve the frozen 2012 24-LP, 2010–2013 96-LP, and paired 192-LP archives verbatim. PR remains Draft.

## What is already supported
- ReEDS wind/PV original source calendars: 15 x 8760 rows, source years 2007–2013, 2016–2023; 2014/2015 absent. Original source instantaneous fixed-CST samples, not validated hour-integrated MWh.
- Four historical weather years 2010–2013, four states (AZ CO ID WY), two county-weight scenarios (ReEDS potential and EIA2025 operating county MW shares), three durations (0h/4h/8h), two hour approximations (endpoint hold and noncyclic trapezoid): 192 previously verified LPs total.
- Current operating-value objective is a **custom SciPy HiGHS state copperplate LP**, not a PyPSA network solve. USD 10/kWh/year screening flip in AZ2012 is NOT robust to hour approximation.
- Existing 180-design LP sweep includes storage power, duration, wind mix; 108 common-AC LPs include firm variable cost USD 60/90/120 per MWh and battery RTE 0.80/0.90/0.95. Do not describe these as untested dimensions, but don't claim they cover the full weather x siting factorial.

## A. Fully specified 15-weather-year scenario extension: 720 LP
15 authentic weather years x 4 states x 2 county schemes x 3 durations x 2 hour conventions = **720 LP solutions** (including frozen 192 subset, not 720 additional LPs; additional unique full-factorial scenarios = 528). Each source weather year requires exact wind+PV native timestamp coverage; 2014/2015 must never be inserted.
- Year input: original ReEDS wind/PV county-class HDF5, county supply-curve class potential, authenticated original MD5s, verified EIA2025 county share input.
- Freeze controls: fixed ReEDS projected-2030 reference state load based on 2012 weather; same common AC capacity scenario, firm capacity ceiling, no network constraints, storage empty-to-empty; preserve original 2012 LP anchors.
- Year-specific calendar alignment: explicit source-year to ReEDS 2012 model reference with Feb29 interpolation for non-leap years and Dec31 source omission. Record all imputed/omitted hours; no implied physical hour-energy validation.
- Fail-closed: 192 original anchor LP objectives within $0.10; 15 years valid source, each scenario conservation and optimality; 720 distinct combinations, 240 0/4/8h triplets, 120 year-state geographic comparisons per hour mode? **Exactly 15x4x2x2=240 triplets and 15x4x2=120 geographic contrasts**. Do not count year-state/mode pairs as independent statistical observations.
- Analysis: show paired continuous EIA-minus-potential V4to8 distribution over 15 weather references, state-specific min/median/max/IQR, all years separately, hour-method sign agreement n/60 year-state cases, not a fabricated p-value. Flag 2012 anchor and omit arbitrary USD 10 classification from abstract.

## B. Same-weather demand validation (distinct experiment, NOT a 2030 forecast)
The publisher's "ReEDS: Electricity demand profiles 2022" DOI 10.5281/zenodo.18461543 uses **2012 weather for all projected model years** and therefore does NOT supply matching future-2030 demand weather realizations.
An independently published **historical** demand source DOI 10.5281/zenodo.18462671 contains 15 original weather years in `demand_historic.h5` (MD5 `06ca6b65088a870afafc25191dcfd6f3`), state gross end-use hour-ending MWh/h in CST, covering 2007–2013, 2016–2023.
- Gate B0: inspect actual HDF5 keys/index and the state/year aggregation before inventing joins or dimensions; confirm downloaded MD5 and native 15-year count.
- Gate B1: **2012 matched-weather original load** baseline vs historical 2012 load, disclose level differences and peak MWh/h.
- Gate B2: 15-year **same-year historical load with same-year wind/PV**. Run raw historical load and, as a separate counterfactual, a declared peak/energy scaling to the 2030 projected demand (this scaling preserves weather shape but is NOT a published 2030 weather-conditioned demand forecast). Keep both scenarios distinguishable.
- Gate B3: check net-load timing and wind/solar/load correlation for each year-state under each geography method. Historical demand and model generation remain noncontemporaneous with EIA2025 installed geography.

## C. External EIA-930 observational curve tests: do not directly equate BA with state
Official EIA-930 metered BA wind/solar **hour-integrated hour-ending** net generation by fuel becomes available from **2018-07-01**; hourly data are not complete for 2007–2017. BA footprints cross state lines, and reported assets are a subset of all utility-scale units; BA local reporting zones can be non-obvious (e.g., Idaho Power reports Pacific Time). Official source: https://www.eia.gov/electricity/930-content/about.html
- C0: identify which original source weather years overlap observed EIA-930 (2018-07 onward; full comparison years 2019–2023, subject to actual completeness).
- C1: source-aligned EIA-860 generator->plant->county and BA ownership/asset affiliation crosswalk at the **same observation year**, with audit of unmapped and cross-state plants; if no credible BA asset mapping, restrict to defensible BA subsets or admit no external curve validation.
- C2: compare matched BA-hour **measured generation** against county/class ReEDS curves under three schemes: original ReEDS potential, historical EIA installed county shares, and feasible observed technology/class proxies. Never equate 2025 EIA installed capacities with a 2019 operating fleet without vintage filtering.
- C3: report normalized CF, capacity normalization basis, correlation, MAE/RMSE, lag cross-correlation, diurnal/seasonal curves, held-out year, hour-to-energy timing and daylight saving QC. Do not claim a fitter model is 'true' county placement solely because of source-level BA mismatch.
- C4: if resource-class data for actual individual sites are unavailable, add a sensitivity bounding within-county class mixes; never relabel that as an observed fleet calibration.
This gate is **substantial data integration, not inherently cheaper than 720 LP**.

## D. Battery costs: use 2025 ATB power/energy separation
The official [2025 ATB utility-scale BESS page](https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage) reports separate battery-pack USD/kWh and BOS USD/kW, with Advanced/Moderate/Conservative 2030 trajectories. It is a modeled technology-cost source, not measured market or project revenues.
- Obtain **2030 source numerical cells** from official ATB Data workbook with named sheet/columns/units and provenance. Do NOT substitute total 4h USD/kWh for incremental 4->8h energy-only capital cost.
- At fixed battery power, `DeltaCAPEX = CAPEX_8h - CAPEX_4h`, `DeltaE = P*(8-4)` hours. Define `k_incremental = DeltaCAPEX / DeltaE_kWh` for projected energy-increment USD/kWh, retaining any duration-specific non-canceling BOS/power terms.
- For stated discount rate r and economic life n, `CRF = r(1+r)^n / ((1+r)^n - 1)`, annualized incremental USD/(kWh-year) `H = k_incremental*CRF + DeltaFixedOM/DeltaE_kWh` plus replacement/degradation assumptions where applicable. ATB source does not itself supply a study-specific financing rate; label discount rate sensitivity as author's assumption.
- Overlay H_low/H_mid/H_high horizontal ranges against continuous `V4to8` across weather years and numerical hour modes. A threshold crossing is conditional operating avoided-cost adequacy, NOT investability, because dispatch/network/market revenues and other costs remain omitted.

## E. Other reviewer concerns and admission
- Existing 180-LP wind-mix/power/duration and 108-LP firm USD 60/90/120, efficiency variations need integration as existing supplementary source-backed evidence, NOT counted twice. New study: 2012 factorial renewable-to-peak penetration x wind-share with *both county schemes*, while frozen central anchors remain unchanged.
- Add fossil generation MWh displaced (4h vs 8h), wind/PV curtailed MWh, renewable supply/load/net-load correlation, peak and seasonal net-load shapes; no assumed fuel price necessary for these outputs, but they are also conditional LP outcomes.
- Add start-point hold as a **third numerical approximation only after verifying proper source boundary mapping**, and solar noon geolocation/clock physical check; these alone do not certify physically integrated hourly CF.
- Examine observed EIA860 PV array AC/DC and tracking configuration and source 1.34 ILR; calculate clear technology-matched bounds, not single undocumented replacement.
- Durable source release with checksummed original CSV/JSON and source code, review each third-party redistribution license, assign Zenodo DOI after author sign-off. Do not treat GitHub Actions retention as permanent preservation.

## Reporting and gate conditions
Main abstract/results must NOT retain '15 of 16 direction agreement' as the final cross-weather headline after all-year run unless explicitly referring to the frozen 4-year pilot; update to authenticated n/60 after new completion. With added third hour convention, denominator becomes 60 year-state effects for each method pair, but avoid implying independent samples or statistical confidence. Publication wording must distinguish fixed projected 2030 demand panel, 15-year historical demand panel, and EIA-930 observational validation.
No new result/claim is admitted until original source digest, exact calendar/units, LP objective replication and full CI pass and outputs are archived.
