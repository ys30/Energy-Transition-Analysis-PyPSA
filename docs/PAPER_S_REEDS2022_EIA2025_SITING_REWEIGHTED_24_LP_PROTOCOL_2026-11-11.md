# Paper S — Source-native ReEDS 2012 × EIA-860 2025 county spatial weighting × 2030 demand: locked 24-LP audit (2026-11-11)

## Study question and admitted scope

Does weighting the same **original ReEDS2012 county-by-resource-class reference-weather CF** by 2025 *observed operating generator county nameplate shares* instead of publisher *developable resource potential county shares* change the modeled 2030 hypothetical state battery's operating-value ceiling? This is the first source-geography experiment based on an independently observed plant fleet distribution rather than an abstract equal-county counterfactual.

**Never label this as a 2025 generation replication or a 2030 deployment prediction.** The controlled original 2012 resource weather, observed 2025 county *siting*, and modeled projected 2030 state demand refer to **three different time frames**. Original weather CF remains source-*instantaneous* and converted to hour-availability with the previously prespecified noncyclic trapezoid and first-hour endpoint fallback. The state copperplate LP is a stylized operating-value sensitivity, not hourly actual energy or grid/financial value.

### Authenticated inputs

1. Original ReEDS v1 2012 county-class HDF5 per technology (uncompressed original 15-year files; never a new synthetic wind/PV series): wind MD5 `0670813d0a18b688d698ca24cf67fb92`, PV MD5 `aba834ea4c592023bca47de2ba79e7ec`. Original publisher supply-curve capacity CSV original MW schema and exact MD5 wind `49ab4e41dc386453b5fd32e5810774d4`, PV `e10b1a64f3a67d163e739b735938eb78`, matched to original 2012 source resource-class/county FIPS column keys.
2. Independently source-verified EIA 2025 operating-generator capacity by Census county FIPS and technology (only OP wind WT/WND and PV PV/SUN, 100% county-mapped capacity per state/tech): [fleet county audit 43124063185](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43124063185), artifact 13901789433.
3. Original publisher 2012 wind/PV four-state potential-weighted county CF, verified [42962740548](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42962740548). Both new county-class HDF5 aggregations **must reproduce** each original 8760-hour potential-weighted state CF within 5e−8 before new EIA county weights are accepted.
4. Original ReEDS2022 projected 2030 demand HDF5 (original MD5 `7b2055d43200744a16a8c4fed68b1a17`), native 2012 fixed CST labels checked against source wind/PV originals, **not publisher-certified within-hour energy**.
5. Frozen 180 common-AC HiGHS original source simulations [43058074434](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43058074434); all 12 corresponding source-potential scenarios (4 states × 0/4/8h, 25% peak power, r=1.5, wind AC=50%) must reproduce original illustrative variable objective within $0.10 before the alternative geography scenario is admitted.

### Spatial assumption and equations

For technology `j`, state `s` and five-digit county `c`:

`w_resource(s,j,c) = Σ_k potentialMW(s,j,c,k) / Σ_{c,k} potentialMW(s,j,c,k)`,

`w_EIA2025(s,j,c) = Σ_operating generator AC nameplateMW(s,j,c) / Σ_c AC nameplateMW(s,j,c)`.

The ReEDS class mix **within county c** remains `p(k|c)=source potentialMW(c,k)/Σ_k source potentialMW(c,k)`. For each 2012 original instantaneous source index t:

`CF_{s,j,geography}(t)=Σ_c w_{s,j,geography,c} Σ_k p_{s,j}(k|c) CF_{source,j,c,k}(t)`.

This does **not** calibrate site-specific vintage, tracker type, microclimate, production losses or resource class. It changes only county siting shares. The source wind CF is per MW_AC; solar original source CF is grid MW_AC / PV array MW_DC. Apply **one-time** ILR=1.34 conversion to the resulting source PV state series for the hypothetical common-AC total nameplate design, with explicit physical maximum/rounding audit.

### Locked 24 LP setup

Four states (AZ, CO, ID, WY) × 2 geographically sourced 2012 weather series (source potential vs EIA2025 operating county) × 3 battery duration controls (0, 4, 8 h) = **24 full 8760-interval LPs**. Fix AC wind+PV nameplate=1.5× state peak demand, wind=50% common AC, battery power=25% peak, RTE=90%, firm variable cost=$90/MWh, renewable=$5/MWh. All input weather and source-demand time labels must match exactly; all LPs must be optimal with hourly equality residual ≤1e−5.

Report the four-state 4h and 8h operating cost savings vs respective 0h controls, plus `(C_4-C_8)/((E_8-E_4)×1000)` in $/kWh-year and differences between weighting methods. Explicitly show whether an illustrative $10/kWh-year *energy-only cost* decision flips. No battery CAPEX or financing is modeled, so the marginal annuity is an operating-value ceiling not a positive net return.

## Strict admission rules

- Do not assert a new source-siting sensitivity result until the [dedicated 24-LP workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/paper-s-reeds2022-eia2025-siting-24-lp.yml) has succeeded and raw CSV/JSON artifacts are archived.
- Fail rather than silently allocate an observed county with positive EIA capacity but no ReEDS resource class. Preserve all original 2012 row indices, per-county class weights, wind/PV source denominator and exact source HDF5 MD5.
- Existing EIA capacity county-weight results alone (TV 0.604–0.862) are **not** CF or battery dispatch differences.
- If PV reweighted CF×ILR is over 1 beyond source rounding tolerance, stop and audit plant/inverter capacity assumptions: do not silently double-normalize or conceal a source technology inconsistency.
- Source original 2012 reference has leap day but excludes 31 December and is not independently publisher-certified as prior-hour interval-integrated wind/PV energy. Source county weighting cannot resolve that limitation.
- Q1 manuscript publication admission requires further physical/weather-year and installed-fleet/vintage validation, not merely 24 more successful LPs. PR remains Draft, previously validated experiments frozen.
