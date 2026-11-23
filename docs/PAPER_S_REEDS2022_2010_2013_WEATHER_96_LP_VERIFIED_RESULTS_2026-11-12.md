# Paper S — VERIFIED 15 original weather-year clocks and 96 source-native LP interannual geographic sensitivity (2026-11-12)

## Outcome: both original-source quality gates passed

- **15 source-year authentic native clocks:** [successful workflow 43281182402](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182402), [original calendar audit artifact 13976245398](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182402/artifacts/13976245398).
- **96 source-backed weather-year LPs:** [successful workflow 43281182390](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182390), [five research output files in artifact 13976060428](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182390/artifacts/13976060428).
- **Full repository CI:** [success 43281182545](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182545).

The source original HDF5 wind MD5 `0670813d0a18b688d698ca24cf67fb92` and utility PV MD5 `aba834ea4c592023bca47de2ba79e7ec` were independently reauthenticated. The 15, exactly 8760-hour original publisher weather years are **2007, 2008, 2009, 2010, 2011, 2012, 2013, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023**. Wind and PV native time indices agree, with no nonhourly within-year gaps. The years **2014 and 2015 are not in these two original resources**; do not imply contiguous 2007–2021 coverage. All leap years 2008/2012/2016/2020 contain 29 February and omit December 31 (24 hours); nonleap years contain all ordinary 8760 hours.

## Four-weather-year LP design and exact numerical admission

Selected 2010, 2011, 2012 and 2013 (four historical source weather references) × four states (AZ, CO, ID, WY) × two geographic schemes (original ReEDS available-developable wind/PV resource potential county capacities; independent 2025 EIA-860 in-operation generator county AC-nameplate shares) × battery duration (0/4/8h), **96 LPs total**. Each year was reaggregated from original county × source resource class HDF5, retaining ReEDS source class proportions within each county. Native source time samples are instantaneous wind/PV CF, *not observed past-hour MWh*. The fixed projected 2030 ReEDS state demand is on the original 2012 8760-hour reference support. The site-weighted case transfers only 2025 EIA observed county shares to the hypothetical 2030 common-AC nameplate design (total AC renewable capacity 1.5× state peak, wind share 50%, battery power 25% peak and η=0.90).

**Explicit calendar mapping:** each native year is assigned by month/day/hour to the 2012 demand-reference support. For nonleap 2010, 2011, and 2013, source did not observe leap-day February 29, so **24 hypothetical leap-day hourly CF points** are assigned as the average of actual February 28 and March 1 at the corresponding clock hour; source December 31 (24 real original hours) is **excluded** so target remains 8760 hours. Leap 2012 source exactly matches 2012 reference support and needs no imputation. Reproducibility records 64 technology × geographic scenario × state × year calendar adjustment records, native/aligned CF-hour sums and the exact inserted-Feb29 minus dropped-Dec31 difference. **These imputed values are not observations; calendar processing can affect economic values.**

All 96 LPs solved `optimal` with preserved hourly equality constraints and 32 complete 0h/4h/8h scenario triplets, giving 16 weather-year × state exact county-siting comparisons. Every one of the **24 frozen 2012 original EIA/resource county-siting LP cases** was reproduced; maximal objective deviation was only **$0.0048633**, versus an advance-set acceptance bound of $0.10.

## Verified central results — marginal 4→8h operating-value-only storage energy annuity

Dollar values represent **hypothetical annual avoided variable dispatch operating costs per incremental kWh** of storage energy capacity; not investment NPV, realized market earnings, or battery CAPEX. Both values in a cell use the same 2030 load and 2010–2013 weather year; order is **ReEDS potential weights → 2025 EIA operating county shares**.

| Native weather year | Arizona $/kWh-year | Colorado $/kWh-year | Idaho $/kWh-year | Wyoming $/kWh-year |
|---|---|---|---|---|
| **2010** | 11.067844 → 10.726983 | 5.562371 → 5.948076 | 2.992730 → 5.645376 | 3.168761 → 5.438663 |
| **2011** | 12.016612 → 11.421001 | 6.177731 → 5.831785 | 3.145816 → 6.207938 | 3.864010 → 6.650881 |
| **2012** | **10.955400 → 9.868276** | 6.220671 → 5.943267 | 4.134846 → 5.789886 | 3.540569 → 5.977560 |
| **2013** | 12.821096 → 12.842341 | 5.618886 → 5.826154 | 3.467274 → 5.274190 | 2.671878 → 5.043572 |

The matched hypothetical `$10/kWh-year` *added battery energy-only* cost screening comparison flips for **one of sixteen** year/state geographic comparisons (Arizona in **2012 only**). For Arizona, in the other three years both spatial schemes exceed $10. Colorado, Idaho and Wyoming remain below $10 in every one of these four years and both geographic schemes. Spatial weights affect the magnitude and sometimes sign of the value differential, not just an arbitrary decision threshold. Arizona spatial value changes are approximately −0.341 (2010), −0.596 (2011), −1.087 (2012), +0.021 (2013) $/kWh-year, while Idaho and Wyoming value remains higher under EIA county shares across these four modeled weather-year cases.

**Interpretation:** The striking 2012 Arizona $10 binary threshold reversal is a **weather-year-specific occurrence, not demonstrated robust across the four historical years**. The broader result that geographic distribution influences storage operating value is supported across the four source weather references. The four-year sample is not a probabilistic draw, and the one-in-four 2012 crossing is **not a probability of future economic success, confidence level or return frequency**.

## Admitted manuscript result paragraph

We expanded the county-geographic storage experiment across four independent authenticated ReEDS weather references (2010–2013), holding the hypothetical projected 2030 demand, technology mix, battery design and EIA 2025 operating-generator county placement fractions fixed. Original county-class wind and photovoltaic HDF5 were spatially reaggregated separately for each year. All 96 LPs solved optimally, and the original 2012 24-LP results were reproduced to within $0.005 of the frozen operating-objective values. With a deliberately illustrative additional-storage-energy cost of $10/kWh-year, an Arizona binary economic screening reversal under EIA county weights was present in the 2012 weather realization (10.955 vs 9.868 $/kWh-year) but did not recur in 2010, 2011 or 2013, when both geographic schemes were above $10/kWh-year. Spatial reweighting affected marginal value in all four meteorological realizations, with Arizona's EIA-minus-resource-potential difference changing from negative in 2010–2012 to marginally positive in 2013. This indicates a county-siting × weather-reference interaction: a screening outcome found in one weather year cannot be generalized to all years.

## Unresolved scientific validity gates

1. Original source wind/PV samples are instantaneous at source hour, while the modeled demand uses hour-ending values; the hourly trapezoid approximation is an assumed numerical treatment, not publisher-authenticated integrated energy. The original 216 LP hold/trapezoid sensitivity does not certify hourly physical integration.
2. Nonleap weather reference February 29 is **synthetically interpolated** and December 31 excluded; it is not a true full-year contemporaneous source-weather/load series. The annual marginal value responds to both seasonal weather and the fixed 2012 reference load placement.
3. EIA 2025 reports plant county capacities but does not identify the exact matched original ReEDS within-county renewable technology classes/vintage or the 2030 installed facility siting; it is a **counterfactual with observed county shares**, not a 2030 buildout forecast.
4. This four-weather-year perturbation is historical interannual meteorological variability, **not an SSP/RCP future climate projection**.
5. State copperplate variable-cost optimization omits transmission, reliability, operational constraints and battery capital/financing; thresholds are hypothetical avoided operating-cost ceilings only.

**Paper S disposition:** The new cross-year results are admitted as a bounded main-text sensitivity, while physical source-hour, actual spatial plant vintage and forecast-weather validity remain open. The original 2012 spatial effect is not removed, but any broad claim that its $10 screening flip persists across years must be explicitly rejected. PR #2 remains Draft.
