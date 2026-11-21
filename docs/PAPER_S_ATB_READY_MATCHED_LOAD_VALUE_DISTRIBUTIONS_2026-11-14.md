# Paper S — Original-source matched-weather battery 4-to-8h modeled operating-value distributions (ATB-ready)

**Frozen source:** successful 720 LP GitHub Actions run [43665299980](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43665299980), verified artifact 14143076211, file `paper_s_same_weather_240_duration_triplets.csv`. Filter `load_mode == actual_historical_level` only. The 2030-annual-energy-rescaled historical curves are mathematically redundant for unit-normalized values due to linear LP peak-ratio scaling.

**Design:** 15 historical source years (2007–2013, 2016–2023) × four states × potential/EIA county weighting = 120 distinct duration triplets under trapezoid-approximated ReEDS instantaneous CFs. Values are avoided operating costs per 4-to-8h added kWh-year. They are NOT observed energy arbitrage profit, cash flow or investment outcomes.

| State | ReEDS county potential median | EIA2025 county operating weighting median | EIA-weight min–max | EIA-weight weather years at or above illustrative $10/kWh-year |
| --- | ---: | ---: | ---: | ---: |
| AZ | 11.963341 | 11.840970 | 9.807053–14.293300 | 13/15 |
| CO | 6.150555 | 5.889200 | 3.857198–7.839259 | 0/15 |
| ID | 4.263589 | 6.076802 | 4.622725–8.821456 | 0/15 |
| WY | 4.245828 | 7.073825 | 5.520423–8.927342 | 0/15 |

**Interpretation restrictions:**
- A uniform $10/kWh-year hurdle is *hypothetical*, not a NLR ATB 2025 v2 cost. It must NOT be presented as evidence of economic viability.
- The positive EIA-minus-potential effect in every Idaho/Wyoming weather reference is a *difference between siting assumptions* and can coexist with low absolute operating value.
- Full NLR ATB 2025 v2 updated November 11 2026 must be source-audited before inserting 2030 Advanced/Moderate/Conservative 4h/8h incremental installed CAPEX and FOM. Annual hurdle = [CRF*(CAPEX8-CAPEX4)+(FOM8-FOM4)]/[4 kWh per common kW].
- Official ATB scenario values have not yet been confirmed; EIA930 independent observation validation has not been performed.
- SciPy/HiGHS copperplate, not a PyPSA transmission-network OPF.
- Do not merge or delete frozen 24/96/192 and 720 LP original results.

**Pending validation:** official ATB v2 source workflow and BA geography/time semantics EIA930 gate are in GitHub Actions queue at the time of this update.
