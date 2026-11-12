# Paper S — VERIFIED external 2025 operating fleet county capacity against 2012 ReEDS county resource potential (11 Nov 2026)

## Independent authoritative source and verification

Successful workflow [43124063185](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43124063185); exact published artifact [13901789433](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43124063185/artifacts/13901789433). Files:
- `paper_s_eia860_2025_vs_reeds_county_spatial_weight_8_summary.csv`
- `paper_s_eia860_2025_vs_reeds_county_spatial_weights.csv`
- `paper_s_eia860_2025_unmatched_county_geographies.csv`
- `paper_s_eia860_2025_vs_reeds_spatial_manifest.json`

Official 2025 EIA-860 annual file, independently downloaded and observed SHA-256 recorded by run: https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip. Verified source workbooks `2___Plant_Y2025.xlsx` `Plant` sheet, and `3_1_Generator_Y2025.xlsx` `Operable` sheet, exact field positions scanned past EIA title rows. Wind strictly `Prime Mover=WT`, `Energy Source 1=WND`, `Status=OP`; PV `Prime Mover=PV`, `Energy Source 1=SUN`, `Status=OP`. Only form-reported operating equipment is counted, not retired, canceled, proposed, standby or out-of-service generators. Unique `Plant Code` joins plant county/state; all observed county labels were mapped with the original Census 2020 national FIPS `STATE|STATEFP|COUNTYFP|...|COUNTYNAME` file at https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt, with exact state constraint and explicit punctuation/county-suffix removal, not fuzzy assignment. Original ReEDS county-class supply-curve MD5 checks on each technology retained.

EIA annual Form 860 reports nameplate generator MW in AC units (official form instruction https://www.reginfo.gov/public/do/DownloadDocument?objectID=126696201). ReEDS available potential wind MW_AC and PV MW_DC differ; **capacity shares normalized *within technology*** allow comparison without adding nominal MW of incompatible bases. These are distinct source-population definitions and calendar years, not the same physical installed portfolio.

## Verified four-state by two-technology comparison

| State | Tech | EIA 2025 OP generator records | EIA 2025 AC nameplate MW | Counties with operating capacity | EIA effective county count | ReEDS source positive-potential counties | ReEDS potential effective county count | County weight total variation |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| AZ | wind | 9 | 1234.5 | 4 | 2.308591 | 15 | 10.756988 | 0.603624 |
| AZ | PV | 154 | 6588.5 | 12 | 3.677099 | 15 | 8.697798 | 0.705602 |
| CO | wind | 41 | 5349.1 | 12 | 7.369633 | 61 | 36.354903 | 0.733759 |
| CO | PV | 186 | 3263.4 | 34 | 4.257585 | 63 | 27.296667 | 0.671097 |
| ID | wind | 33 | 1132.3 | 7 | 4.817033 | 44 | 27.815955 | 0.780738 |
| ID | PV | 14 | 701.6 | 5 | 3.411089 | 44 | 23.984722 | 0.813891 |
| WY | wind | 33 | 4707.4 | 6 | 3.613135 | 23 | 17.735842 | 0.693337 |
| WY | PV | 2 | 242.0 | 2 | 1.891358 | 23 | 16.681175 | 0.862001 |

**Mapping QA:** each of these eight groups has `county_mapping_capacity_coverage=1.0` (100% of its EIA-selected OP nameplate), `eia_fleet_capacity_in_zero_reeds_potential_counties_fraction=0`. No assumption about external generators with nonconforming prime mover/fuel or excluded status is made. Total variation `TV=.5 Σ_county |w_2025_installed - w_ReEDS_developable|` is measured over the **union** of county geographies. Effective number of counties is inverse weight HHI `1/Σ w_c²`.

## New empirical finding and scientific admission

The county geographic distribution of *observed 2025 reported operating wind and utility-scale PV generator nameplate* is substantially more concentrated than publisher ReEDS developable potential weights; all eight TV distances are approximately 0.604–0.862. E.g., WY PV's 2025 operating nameplate occurs in just **two counties**, whereas source available-PV potential covers **23 counties**. Arizona solar source potential effective county count 8.70 contrasts with EIA effective county count 3.68. The source potential state CF is **not an observed operating-fleet CF**.

**A spatial difference in MW weights does not itself estimate a CF time-series discrepancy or battery operating-value discrepancy.** This external observation strengthens the need to reaggregate original class/county 2012 instantaneous CF under observed 2025 EIA county weights (while retaining source potential proportions *within* each county and explicitly not attributing observed class/vintage), and rerun a bounded 2030 common-AC 0h/4h/8h LP to test the extent of this source/installed spatial mismatch. The resulting comparison would be an *illustrative 2025-siting-weighted 2012 resource-weather counterfactual*, not actual 2030 generation forecast or future investment value.

## Proposed manuscript paragraph

We independently evaluated whether publisher ReEDS developable-potential weighting approximated existing generator geography. EIA's 2025 annual in-operation wind and photovoltaic generators were matched by Plant Code to plant counties, assigned official Census county FIPS without fuzzy matching, and aggregated within each technology by nameplate MW. The 2025 capacity-to-county matching coverage was complete across AZ, CO, ID and WY. Nevertheless, the county weight vectors differed markedly from ReEDS available resource potential (total variation 0.604–0.862 across eight state-technology groups). EIA 2025 generator capacity was more concentrated among operating plant counties than the possible source resource geography: for example, 2025 Wyoming photovoltaic capacity was reported in two counties whereas ReEDS potential spanned 23 counties. These observational capacity-siting differences establish a structural limit to using resource-potential-weighted capacity-factor curves as an empirical proxy for the existing or future fleet. They do not by themselves establish any change in storage dispatch or marginal operating costs.

## Restriction and further work

- EIA Form 860 operating status OP is a deliberately strict subset. Source is a 2025 snapshot, not a confirmed 2030 installed forecast or physical 2012 weather record.
- County-level siting alone does not resolve wind/PV technology class, turbine vintage, solar tracking, site location inside county, meteorological plant production or losses.
- Source original 2012 8,760 time instants are fixed-CST with leap day but no December 31; instantaneous CF cannot be equated with hour-ending interval energy absent independent verification.
- Previous 180 common AC LP, 108 cost-efficiency LP and 216 hour-mode LP experiments remain frozen and valid *as resource-potential-weighted hypothetical operating-cost sensitivities*.
- Without the proposed county-reweighted LP replication and separate weather-year validation, do not assert actual installed-fleet energy economics, Q1 manuscript final readiness or empirical project NPV.
