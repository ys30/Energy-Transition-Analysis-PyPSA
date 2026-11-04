# Western US Energy Transition Modeling | PyPSA + EIA

[![CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/ci.yml/badge.svg)](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/ci.yml)
[![BPAT empirical data](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/bpat-wind-empirical.yml/badge.svg)](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/bpat-wind-empirical.yml)

**Portfolio project | Python · PyPSA · HiGHS · pandas · U.S. EIA data · reproducible GitHub Actions**

A reproducible modeling and data-validation pipeline for western U.S. electricity-transition research. The strongest delivered components are **hourly balancing-authority dispatch prototypes, official EIA data ingestion and reconciliation, automated data-quality audits, and PyPSA network optimization tests**. Each finding is linked to a verified run or documented limitation.

> **Scientific status:** The 2024 CISO and BPAT pilots are **independent, gas-only engineering screening models**, not calibrated historical simulations or a coupled WECC network. Synthetic scenario figures and transmission test fixtures must not be interpreted as empirical energy-transition forecasts.

## Project A → B integration status (audited)

[**A contribution, repository boundaries, and revised B milestone progress**](docs/A_TO_B_CONTRIBUTION_AND_PROGRESS_AUDIT.md)

Project A (`ys30/lut-to-pypsa`) remains an **independent global annual
LUT-DEMAND methodology demonstration**. Its authentic data is continent-level
electricity energy-service demand; **no direct state-hour Western EFS input,
actual ReEDS LAF weights, or empirical Western solve has been admitted into B
from A**. B reuses methodological lessons, not A's regional quantities.
Engineering CI success must not be conflated with research calibration.

**A handoff contract (not a Western-US input):** Project A now emits a
`handoff_contract` in `lut_pypsa_input_manifest.json` with an artifact
SHA-256, snapshot count, hourly resolution, MW units, source quantity, and
`requires_explicit_geographic_mapping=true`. The associated
`lut_load_only.nc` is a five-continent, flat-profile, load-only network.
**B must reject it as an empirical Western-US load input** unless an
independently documented geographic crosswalk and energy-service-demand to
electricity-load transformation are supplied and validated. A matching hash
establishes artifact identity, not regional compatibility. B's EIA/EFS
pipelines remain the regional source of record; no A demand is silently
substituted for them.

## Recruiter quick view

[**Quantitative evidence, four charts and A/B/C project differentiation**](docs/recruiter_evidence_brief.md)

![2024 hourly dispatch model mismatch (not calibrated)](figures/portfolio_dispatch_mae_2024.svg)

## Results at a glance — verified evidence and modeled scenarios

The figures below are versioned in this repository and distinguish official source measurements from assumption-dependent optimization.

![2024 BPAT official cross-source wind totals](figures/portfolio_bpat_wind_totals.svg)

The totals come from different reporting populations. See the [EIA-930A population investigation](docs/verified_bpat_wind_eia930a_population_2024.md) and [wind reconciliation](docs/verified_bpat_wind_end_to_end_official_2024.md). The 1.981 TWh gap is **not** a measured loss or curtailment.

![2024 EIA-930 missingness by source field](figures/portfolio_eia930_missingness.svg)

The [hourly audit](docs/eia930_2024_interchange_diagnostic_findings.md) identifies 312 CISO TI hours, 24 overlapping CISO NG hours, and one BPAT TI hour. Interchange observations are **not** independently calibrated physical branch flows.

![2024 storage scenario change in unmet load](figures/portfolio_storage_sensitivity.svg)

The [8,784-hour storage gap-fill sensitivity](docs/verified_annual_storage_gap_sensitivity_2024.md) reports 73,373 MWh without storage versus 51,021 MWh with a hypothetical 1-GW/4-GWh battery: 22,352 MWh less model-defined unmet load (30.5%). This is a **scenario-conditioned dispatch comparison**, based on assumed generator capacity, costs, 55 imputed renewable source observations and a $10,000/MWh shortage penalty; not a historical battery investment return. The modeled $315.9933 million objective improvement includes $223.52 million in assumed shortage-penalty reductions and excludes battery capex/degradation. Three gap-fill treatments yield the same battery dispatch metrics under these assumptions, not generalized robustness.

**Most recent verified integration:** [NARIS Western 35-zone/24-hour synthetic OPF](docs/verified_naris35_24h_synthetic_load_opf.md) · [full-network CI success](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41718188340) · [main test CI success](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41718188226). The experiment uses source-published *directional planning Link capacities*; demand, supply and cost are hypothetical. **Not a calibrated WECC or historical Western dispatch estimate.**

## 11-state EFS candidate load-synchronization experiment (source-backed, not calibrated)

The [verified 2030–2050 mixed-clock sensitivity study](docs/verified_eleven_state_efs_candidate_mixed_clock.md) combines **actual archived NLR EFS demand** for 11 Western states with the **unchanged seven-state LAF pilot** and **numerically audited candidate weights** for CA/NV/OR/WA. The pinned +7/+8 hour shift changes candidate coincident peak by **+23.54 MW (2030), +31.84 MW (2040), +35.97 MW (2050)** relative to an unshifted LocalHourID comparison, while conserving total annual allocated load (**768.25, 848.88, 972.30 TWh**, respectively). [Verified workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41764316720).

**Independent geographic corroboration:** Both [official Census TIGER 2023 state polygons](docs/verified_census_border_bus_independent_overlay.md) and the [Natural Earth 10m source shape family used by pinned upstream PyPSA-USA](docs/verified_pinned_natural_earth_full_state_border_comparison.md) place network node `2030005` in **California** and node `2013019` in **Oregon**, matching their independently inferred original LAF denominators despite later exported labels of Nevada and Washington. The Census estimated border distances are **198 m** and **4.42 km**, respectively. The exact historical Natural Earth Cartopy archive and dropped `full_state` bus labels remain unavailable, so the four-state mapping is **still a candidate**.

**Scope guard:** The exact original `full_state` GIS for the two crossing source-denominator buses, actual EFS UTC/DST interpretation and Western generator/weather snapshot compatibility have **not** been independently certified. This is a reproducible **candidate temporal sensitivity**, **not** a verified Western hourly demand profile, empirical OPF, emissions forecast, or electricity-transition outcome.

**Western generation admission gate:** The [four-network real source audit](docs/verified_western_efs_generation_source_admission.md) confirms that the original **10,157-bus Western topology** and all three load-bearing EFS 2030/2040/2050 NetCDF scenarios have **zero Generator components**, despite the EFS networks' 20 Load components each. [Source-admission CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41771905008). Existing EIA-860/EIA-923/EIA-930 pipelines provide historical generation evidence, **not** source-verified future unit-to-bus mapping, hourly availability or 2030–2050 costs. Full Western empirical dispatch remains blocked until authentic generation and time-alignment inputs are integrated.

**Official generator-level source staging now available:** The [verified 2024 EIA-860 generator-to-Western-bus candidate run](docs/verified_eia860_2024_generator_bus_staging.md) produces a **5,665-generator / 3,223-plant** source inventory representing **268,692 MW of operating nameplate**, preserving each unit ID, fuel, state, BA and nearest geographic candidate bus. **88 generator rows (5,831.9 MW)** are more than 50 km from their candidate bus and require priority connection review. [Successful actual-data CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41772568847). **Zero electrical plant-to-bus connections are independently approved**, and this historical nameplate screen is not a validated 2030–2050 future fleet. No unsourced generators were inserted into PyPSA.

**Priority electrical-interconnection evidence queue:** A [verified generator-to-plant risk triage](docs/verified_2024_generator_plant_poi_triage.md) now identifies **63 distinct plants / 88 EIA-860 operating generator rows** whose nearest geographic source-topology buses are over **50 km** away, totaling **5,831.9 MW** of 2024 nameplate. The top 20 source plants cover **4,922.7 MW** (~84.4%) of those candidate-risk MW. [Source CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41773439738). This is an audit prioritization rather than independently confirmed electrical connectivity, generator admission or 2030–2050 dispatch modeling.

**New network-crosswalk concentration finding:** [Verified cluster audit](docs/verified_2024_distant_plant_bus_collision_risk.md) shows that the **63** distant EIA source plants (5,831.9 MW historical nameplate) collapse into only **15** nearest synthetic candidate buses; **58** plants (5,118.3 MW) share a candidate bus with at least one other distant plant. The three largest candidate IDs (`2053003`, `2053000`, `2077001`) account for **4,736.8 MW** of that screened subset. [Successful CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41774150894). This is an **uncertainty finding in the GIS-to-synthetic-topology crosswalk**, not physical grid congestion or approved plant connections.

![Official EIA-860 2024 historical nameplate concentrated into unverified synthetic candidate buses](figures/portfolio_eia860_distant_bus_clusters.svg)

**Official plant identities and transmission-document evidence:** The [verified named-plant review](docs/verified_2024_named_plant_poi_and_sagamore_external_evidence.md) reconciles **all 63** geographically distant 2024 EIA-860 plants to their official facility names and original source coordinates. A published SPP agreement identifies **522-MW Sagamore Wind** as connecting to **Crossroads 345-kV substation**, while the model's nearby geographic candidate bus remains **unverified**. [Successful EIA identity CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41774793024). No synthetic network bus has been promoted to an independently approved POI.

**Source-to-grid evidence hierarchy (three priority EIA plants):** A [new CI-verified SPP evidence ledger](docs/verified_top3_spp_eia_poi_evidence_hierarchy.md) distinguishes **Sagamore Wind** (522 MW; named **Crossroads 345-kV substation**), **Hobbs Generating Station** (681.5 MW; SPS **230-kV service receipt point**) and **Cunningham** (444.2 MW; 13.8/20-kV **unit-side receipt voltage records**). These claims are from different SPP document types and **do not establish any connection** to their shared geographic candidate synthetic bus `2053003`. [Evidence gate CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41775561325). All three EIA source identifiers and historical nameplates are preserved; zero generator-to-synthetic-bus POIs are certified.

## Four recruiter-ready work samples

| Work sample | What was implemented | Verified evidence | Status |
|---|---|---|---|
| **1. Reproducible Python research engineering** | Installable package, automated tests, provenance-aware source handling, CI workflows, audit artifacts and plotting | [CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/ci.yml) · [reproducibility guide](docs/reproduce_2024_two_ba_hourly_baseline.md) | **Working** |
| **2. 2024 hourly PyPSA modeling** | Separate CISO/BPAT, 8,784-hour gas-only dispatch pilots; benchmark against observed BA net generation with no gap imputation | [numerical acceptance](docs/verified_2024_two_ba_hourly_numerical_acceptance.md) | **Engineering baseline verified; not calibrated** |
| **3. Official EIA-930 quality and BA accounting audits** | Demand (D), generation (NG), total interchange (TI), hourly coverage, gap-window validation, and conservative calibration eligibility gates | [2024 BA diagnostic evidence](docs/eia930_2024_interchange_diagnostic_findings.md) · [audit workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/eia930-balance-audit.yml) | **Observed-data audit verified; calibration gates fail** |
| **4. BPAT wind cross-source reconciliation** | Official EIA-923 generation × EIA-860 plant mapping × EIA-930 hourly WND; EIA-930A reporting-population cross-check and 28-plant review queue | [official 2024 cross-source reconciliation](docs/verified_bpat_wind_end_to_end_official_2024.md) · [EIA-930A population check](docs/verified_bpat_wind_eia930a_population_2024.md) | **Pipeline verified; accounting gap unresolved** |

### Selected measured results

- **Chronological modeling:** 8,784 hourly snapshots per 2024 pilot; observed NG comparison pairs **8,760 hours for CISO** and **8,784 for BPAT**. Model-versus-observed NG MAE: **4,190.52 MW (CISO)** and **2,463.95 MW (BPAT)**. These errors reflect simplified gas-only dispatch versus *total observed* BA generation; they are **not acceptable calibrated error claims**. [Verified acceptance](docs/verified_2024_two_ba_hourly_numerical_acceptance.md).
- **Data QA:** For the EIA-930 D/NG/TI triple audit, CISO has **312 missing interchange hours**, including **24 hours also missing NG**; BPAT has **one missing TI hour**. Exact contiguous UTC windows and independent window-consistency checks were verified in the [interchange audit](docs/eia930_2024_interchange_diagnostic_findings.md). **Neither BA passes the historical interchange calibration screening gate.**
- **Wind reconciliation:** Qualified BPAT-attributed EIA-923 wind totals **8,820,435.41 MWh** versus EIA-930 BPAT WND **6,839,734 MWh** (signed difference **1,980,701.41 MWh**); full-year EIA-930 WND has 8,784 recorded hours. No excluded EIA-923 wind source records intersect the matched BPAT plant population in the verified audit. [Evidence](docs/verified_bpat_wind_end_to_end_official_2024.md).
- **Independent source-population discriminator:** Of **28** EIA-923/EIA-860 BPAT-associated wind plant IDs, **20** occur on BPAT's official EIA-930A Schedule 2 reporting inventory and **8 do not**. The eight plants account for **1,802,779 MWh** of qualified EIA-923 generation. **This is evidence of a population-boundary issue, not a verified allocation of the 1.981 TWh difference**; EIA-930A includes generator-level reporting and plant IDs alone cannot reconcile all differences. [EIA-930A audit](docs/verified_bpat_wind_eia930a_population_2024.md).

## Western NARIS zonal integration — verified synthetic case

[**35-zone, 24-hour NARIS Link OPF numerical verification**](docs/verified_naris35_24h_synthetic_load_opf.md) documents a successful HiGHS solve using 131 directional planning interfaces. Total **hypothetical** demand and generation are both 42,840 MWh; the isolated member zone `p19` has 816 MWh of **invented** demand served entirely by **invented** local backup. This is an engineering integration and energy-balance result, **not** a historical Western-US dispatch simulation, calibrated grid, unmet demand estimate, or quantified transition benefit.

## A separate solver-verified PyPSA `Line` example

A deliberately **synthetic** two-bus PyPSA + HiGHS linear-optimization sensitivity test demonstrates congestion-driven dispatch. A line rated at **25 / 50 / 125 MW** carries **25 / 50 / 100 MW**, respectively, and local backup dispatch falls **75 / 50 / 0 MW** for 100 MW load. This confirms solver integration, **not** real CISO–BPAT transmission capability or historical savings. [Verified line sweep](docs/verified_synthetic_ac_line_sweep.md).

## Run locally

```bash
git clone https://github.com/ys30/Energy-Transition-Analysis-PyPSA.git
cd Energy-Transition-Analysis-PyPSA
python -m pip install -e '.[dev]'
python -m pytest -q
python -m energy_transition --output outputs
```

The last command generates **illustrative**, hardcoded 2025–2040 scenario plots (`outputs/generation_mix.png`, `outputs/renewable_share.png`, `outputs/emissions.png`) that **are not outputs from solved historical PyPSA energy-transition scenarios**. For reproducible empirical workflows, including API-key requirements and different temporal models, follow the [Western US EIA-930 study guide](docs/western_us_eia930.md) and [hourly pilot instructions](docs/reproduce_2024_two_ba_hourly_baseline.md). Official data workflows run in GitHub Actions and retain versioned audit artifacts.

## Research boundaries and roadmap

**Verified:** source-aware hourly ingestion and audits, two independent simplified 2024 BA pilots, BPAT wind plant crosswalk/reconciliation, EIA-930A population audit, and a synthetic PyPSA `Line` optimizer example.

**Not yet verified:** authenticated **historical 2024 WECC branch topology, impedance and thermal ratings**; multi-area physically calibrated dispatch; CISO/BPAT interchange reconciliation; source-backed state-to-ReEDS load allocations and real generator-to-bus availability/cost mapping; investment/renewables/storage system-wide benefit claims. The [transmission evidence audit](docs/wecc_hifld_transmission_source_audit.md) explains why a future WECC planning archive or HIFLD geometry cannot simply be renamed a historical 2024 electrical network.

**Implemented and solver-verified planning interface pathway:** [PyPSA-USA Western network integration](docs/open_western_network_pypsa_usa_path.md) and the [35-zone NARIS 24-hour synthetic OPF evidence](docs/verified_naris35_24h_synthetic_load_opf.md) document a working **35-bus Western membership, 131-directional-Link** PyPSA/HiGHS experiment, including isolated `p19`, **42,840 MWh synthetic load**, 816 MWh local backup and an optimal conservation-checked solution. [The current CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41718188340) also archives an **empirical-readiness audit that intentionally blocks historical claims**. These planning interfaces are not authenticated 2024 WECC AC branches; empirical loads and generators remain unadmitted.

**Next milestones:** (1) independently authenticate EFS/EIA temporal and geographic allocation factors and validate hourly load conservation; (2) admit EIA-860 generator capacity with verified bus/zone placement, hourly availability and operational costs; (3) resolve `p19` interface evidence without inventing links; (4) reconcile EIA BA observations and BPAT wind reporting boundaries; (5) run sensitivity and energy-transition comparisons only after empirical readiness gates pass.

## Documentation and code navigation

- [2024 CISO/BPAT numerical acceptance](docs/verified_2024_two_ba_hourly_numerical_acceptance.md)
- [Official BA interchange diagnostics and exact missing windows](docs/eia930_2024_interchange_diagnostic_findings.md)
- [BPAT wind 2024 cross-source study](docs/verified_bpat_wind_end_to_end_official_2024.md)
- [2024 EIA-930A BPAT reporting population study](docs/verified_bpat_wind_eia930a_population_2024.md)
- [PyPSA synthetic line dispatch verification](docs/verified_synthetic_ac_line_sweep.md)
- [Source code](src/energy_transition/) · [Tests](tests/) · [GitHub Actions](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions)
