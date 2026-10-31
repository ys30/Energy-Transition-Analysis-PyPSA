# Western US Energy Transition Modeling | PyPSA + EIA

[![CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/ci.yml/badge.svg)](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/ci.yml)
[![BPAT empirical data](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/bpat-wind-empirical.yml/badge.svg)](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/bpat-wind-empirical.yml)

**Portfolio project | Python · PyPSA · HiGHS · pandas · U.S. EIA data · reproducible GitHub Actions**

A reproducible modeling and data-validation pipeline for western U.S. electricity-transition research. The strongest delivered components are **hourly balancing-authority dispatch prototypes, official EIA data ingestion and reconciliation, automated data-quality audits, and PyPSA network optimization tests**. Each finding is linked to a verified run or documented limitation.

> **Scientific status:** The 2024 CISO and BPAT pilots are **independent, gas-only engineering screening models**, not calibrated historical simulations or a coupled WECC network. Synthetic scenario figures and transmission test fixtures must not be interpreted as empirical energy-transition forecasts.

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

**Not yet verified:** authenticated **historical 2024 WECC branch topology, impedance and thermal ratings**; multi-area, physically calibrated network dispatch; CISO/BPAT interchange reconciliation; investment/renewables/storage system-wide benefit claims. The [transmission evidence audit](docs/wecc_hifld_transmission_source_audit.md) explains why a future WECC planning archive or HIFLD geometry cannot simply be renamed a historical 2024 electrical network.

**Next milestones:** (1) resolve plant/generator reporting-boundary attribution for the BPAT wind discrepancy; (2) inspect authorized WECC planning or historical network input files and their physical parameters; (3) build and validate a clearly labeled interconnected PyPSA case; (4) rerun storage/renewables scenarios and quantify uncertainty once the model's historical and source requirements pass.

## Documentation and code navigation

- [2024 CISO/BPAT numerical acceptance](docs/verified_2024_two_ba_hourly_numerical_acceptance.md)
- [Official BA interchange diagnostics and exact missing windows](docs/eia930_2024_interchange_diagnostic_findings.md)
- [BPAT wind 2024 cross-source study](docs/verified_bpat_wind_end_to_end_official_2024.md)
- [2024 EIA-930A BPAT reporting population study](docs/verified_bpat_wind_eia930a_population_2024.md)
- [PyPSA synthetic line dispatch verification](docs/verified_synthetic_ac_line_sweep.md)
- [Source code](src/energy_transition/) · [Tests](tests/) · [GitHub Actions](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions)
