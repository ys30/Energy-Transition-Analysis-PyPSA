# Paper S — VERIFIED 2025-independent spatial representativeness concern in original ReEDS2022 county potential weights

## Source-authenticated successful audit (11 November 2026)

Successful [Actions run 43120911728](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43120911728), artifact `paper-s-reeds2022-original-county-resource-potential-spatial-weight-audit` ([direct artifact](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43120911728/artifacts/13900916856)). Two original publisher capacity CSV files were downloaded from ReEDS Zenodo records and independently checked against known original MD5 values. Keys were validated as class × five-digit county FIPS, county resource MW aggregated by state and technology, and fractions tested to sum to one. This audit uses **original potential data only**, not installed generating equipment or HDF5 CF replay.

| State | Technology | Positive-resource counties | Effective counties (inverse county HHI) | Top 5 resource-potential share | Total variation distance versus equally weighted counties |
|---|---|---:|---:|---:|---:|
| AZ | wind (AC MW) | 15 | 10.756988 | 57.6207% | 0.243874 |
| CO | wind (AC MW) | 61 | 36.354903 | 24.0791% | 0.321455 |
| ID | wind (AC MW) | 44 | 27.815955 | 29.4320% | 0.232476 |
| WY | wind (AC MW) | 23 | 17.735842 | 40.5823% | 0.228970 |
| AZ | utility PV (DC MW) | 15 | 8.697798 | 66.3326% | 0.329992 |
| CO | utility PV (DC MW) | 63 | 27.296667 | 29.8174% | 0.441219 |
| ID | utility PV (DC MW) | 44 | 23.984722 | 33.9925% | 0.321942 |
| WY | utility PV (DC MW) | 23 | 16.681175 | 41.2666% | 0.257246 |

A state's potential-weighted source CF is `CF_state(t) = Σ_c w_c Σ_class [MW_class,c / MW_c] CF_class,c(t)`, with `w_c = MW_c / Σ MW_c`. The county-weight effective number is `N_eff = 1 / Σ w_c²`. One can evaluate how this differs from the **counterfactual equal-positive-county weighting** `w_c = 1/K`, but neither scenario represents observed generator siting. PV potential source capacity is MW_DC and wind is MW_AC; never add the two in mixed units.

## Main implications

- Arizona's hypothetical source-PV reference CF gives **66.3%** of its county potential mass to only five counties, and Colorado PV's potential-weighted geography effectively reflects **27.3 counties** despite **63 counties** with positive source potential. These are direct indications that the CF shape is **not uniform across counties**.
- The largest potential-vs-equal-country [county] total variation metric among these eight is Colorado PV **0.4412**. This demonstrates weight-vector distance, **not** an observed effect on CF or dispatch results. Actual source-class hourly resource values need to be replayed under the alternate weights before making any claims about resulting storage savings.
- All EIA resource-fleet comparisons must be matched on **county FIPS, technology, operational status, date, AC/DC MW denominator** and coverage. Source county availability is not equivalent to existing wind turbine or solar plant count.

## External independently published installation-source opportunity

EIA has published the **2025** annual detailed EIA-860 generator inventory: https://www.eia.gov/electricity/data/eia860/ (official confirmed 2025 ZIP `https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip`). The publisher documents plant location, including state and county, and generator fuel/technology, status and nameplate MW. See EIA's primary source https://www.eia.gov/tools/faqs/faq.php?id=567&t=3. A future independent 2025 *observed fleet distribution* spatial benchmark can merge EIA Plant2025 county and Generator2025 operable wind/utility PV generator MW by plant ID, map to Census validated five-digit county FIPS, exclude proposed, retired, non-operable and small-scale distributed systems as appropriate, then compare observed county *capacity shares* with ReEDS supply-potential shares. Solar EIA AC/DC reporting standards must be verified from source field definitions, and plant site county may not equal the location of distributed solar arrays or multi-county projects.

The 2025 actual fleet is a snapshot, not an actual 2030 deployed fleet, so it can serve only as **out-of-sample current-fleet benchmark**; no extrapolation to 2030 without an explicit projection/deployment scenario. Source hourly weather is 2012 instantaneous CF, not validated 2025 generation output, and direct capacity weighting does not imply exact 2025 generator CF given technology vintage, plant siting within counties or operational losses.

## Required next admission work

1. Independently probe 2025 official EIA-860 ZIP worksheet names/headers, plant ID linkage, county and generator-operating filters. Refuse to guess EIA column names; retain SHA256 and release provenance, then build a validated EIA county fleet weighted comparison.
2. If original ReEDS 2012 county HDF5 is fetched again, compute a *source-consistent county weight-swapped 8760-hour CF*, preserving county-specific within-class proportions, and rerun a limited common-AC 2030 LP on the equal-county counterfactual. Do not substitute equal counties for actual EIA observed generators.
3. Add a detailed source spatial validity limitation to manuscript: publisher developable potential weights are neither plant inventories nor calibrated future installed resource layouts.
4. Keep the 2012 instantaneous-CF/hour-ending energy and missing 31 Dec ambiguity open; the previous 216-LP hour numerical mode sensitivity (0/36 decision flips) is not actual interval validation.

Engineering CI 975 passed under [43109407850](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43109407850). This spatial study is an independent successfully tested diagnostic and does not alter frozen previously accepted LP outcomes.
