# Paper S — common-AC ReEDS2022 2030 cost–efficiency robustness RESULTS (verified 2026-11-11)

## Independently archived and accepted output

**Successful workflow:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43060677031

**Canonical artifact:** `paper-s-reeds2022-2030-ac-108-cost-eta-lp-and-36-storage-hurdles`, containing
- `paper_s_reeds2022_2030_common_ac_108_efficiency_firm_cost_lp.csv` (108 HiGHS LP records)
- `paper_s_reeds2022_2030_common_ac_36_efficiency_firm_cost_4_to_8h.csv` (36 directly matched 0/4/8h triples and 4→8h marginal cost thresholds)
- `paper_s_reeds2022_2030_common_ac_108_cost_eta_manifest.json` (scope and source checks)

All 108 solutions reached optimum, checked hourly equality balance residuals; 36 triplets match a unique set of source load/weather and model parameters. Zero-storage LP objective is independent of irrelevant battery efficiency. Previously archived Arizona anchor at η=0.90, firm $90/MWh reproduces incremental energy-only cost ceiling $10.955400/kWh-year.

## Study definition

- Original ReEDS2022 county wind and utility-PV 2012 fixed-CST 8760-hour *instantaneous* CF, original HDF5 MD5 audited: [source archive 42962740548](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42962740548).
- 2030 source-demand scenario file MD5 `7b2055d43200744a16a8c4fed68b1a17`.
- Four states AZ, CO, ID, WY; hypothetical combined renewable AC nameplate 1.5× demand peak, 50% wind AC and 50% PV inverter AC, PV array DC capacity = 1.34× PV inverter AC. The original publisher PV CF was grid AC / array DC, hence multiply once by 1.34 to change denominator, limited to ≤1 with decimal-rounding-only tolerance.
- Battery power = 0.25× peak demand; compare 0h, 4h, 8h at same power. RTE 80/90/95%, firm marginal generation $60/90/120 per MWh, renewable $5/MWh. Source weather and load held fixed in all comparisons.
- Price and efficiency are **illustrative scenario levers**, not estimated real regional generator costs, future storage efficiencies, or current project price forecasts.

## Main 4→8-hour marginal upper-bound results

The operating-value-only threshold in $/kWh-year is `[optimal operating objective(4h)-optimal operating objective(8h)] / [incremental storage energy in kWh]`. The denominator is added installed energy capacity, with **constant battery power**. No new charge/discharge power equipment cost is attributed to this extension.

| State | RTE | Firm $60/MWh | Firm $90/MWh | Firm $120/MWh |
|---|---:|---:|---:|---:|
| AZ | 80% | 6.198183 | 9.657633 | 13.117084 |
| AZ | 90% | 7.063350 | 10.955400 | 14.847451 |
| AZ | 95% | 7.465665 | 11.557424 | 15.649183 |
| CO | 80% | 3.416227 | 5.322958 | 7.229689 |
| CO | 90% | 4.010696 | 6.220671 | 8.430646 |
| CO | 95% | 4.292891 | 6.645726 | 8.998560 |
| ID | 80% | 2.268680 | 3.534920 | 4.801159 |
| ID | 90% | 2.665888 | 4.134846 | 5.603804 |
| ID | 95% | 2.853044 | 4.416732 | 5.980419 |
| WY | 80% | 1.943365 | 3.028034 | 4.112703 |
| WY | 90% | 2.282735 | 3.540569 | 4.798403 |
| WY | 95% | 2.446058 | 3.786686 | 5.127313 |

### Conditional $10/kWh-year energy expansion cost screening

Of these nine efficiency × firm-cost choices, AZ meets or exceeds the illustrative incremental energy-annuity requirement in **5/9** conditions (all three $120/MWh cases and $90/MWh with η≥0.90). Colorado, Idaho and Wyoming have **0/9** cases meeting that condition, even at η=0.95 and $120/MWh firm generation cost. These are deterministic scenario counts, NOT frequencies/probabilities or evidence that one state has a 5/9 likelihood of economic viability.

A *conditional annualized energy-cost-only screen* passing does **not** imply bankable profitability. Excluded battery capital installation beyond energy modules, O&M, finance, degradation, future resource conditions, market participation, capacity/reliability values and transmission constraints.

## Paper S manuscript correction

In the source-calibrated **hypothetical common-AC** model:
1. The earlier claim “4→8h extension is uneconomic in all states at $10/kWh-year” is wrong after source denominator normalization. AZ passes under the reference η=.90, firm $90/MWh choice, at margin ≈$0.9554/kWh-year above the illustrative energy-only annuity, but it fails with η=.80 at $90/MWh or at any RTE with $60/MWh firm cost.
2. CO, ID, WY do **not** meet the illustrative $10/kWh-year energy-only benchmark in any of 9 cost × efficiency combinations.
3. The central causal/optimization mechanism is conditional value of surplus-renewable shifting and avoided firm variable energy, not empirical estimation of investment feasibility.
4. This source-data model does not certify instantaneous CF as past-hour integrated energy. End-instant/trapezoid conversion remains a numerical sensitivity; full true-hour energy join and physical time convention remain unresolved.
5. Wind/PV weights are developer-resource-potential classes and hypothetical installed nameplates, not a verified actual 2030 buildout; LP omits transmission, ancillary services, scarcity and reliability.
6. Preserve 180 common-AC and 144 source-matched incremental analyses as predecessor sources. Freeze legacy EFS2020 study unchanged. Keep PR Draft until full CI and publication-level source, reproducibility and validity gates pass.

**Acceptance status:** source-backed storage operating-value *scenario sensitivity* is reproducible; real-world operating forecast, project investment advice and Q1 journal final manuscript readiness are **not** established.
