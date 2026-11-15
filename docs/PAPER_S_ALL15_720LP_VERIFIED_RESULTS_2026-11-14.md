# Paper S — Verified 15-source-weather-year 720 LP results (2026-11-14)

**Execution status:** successful GitHub Actions [run 43651682920](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43651682920), artifact `paper-s-all15-720lp-fixed2030demand-source-validated` ID **14137831093**. Full CI, original 96/192 comparison workflows also succeeded at original analysis commit `dd258ea0552d5e139535d2e2ca32f1fcf10fcb25`.

## Exact validity gates

- 15 authentic years: 2007–2013 and 2016–2023; no 2014/2015.
- **720/720 HiGHS LPs optimal**, maximum equality balance residual 7.27595761418e−12 MWh.
- **240** duration triplets, **120** siting contrasts (60 per hour mode), and **60** matched hour-method year-state comparisons.
- Frozen original 192 LP objectives all reproduced; max absolute mismatch **USD 0.0048999786377**, accepted tolerance USD 0.10.
- Spatial effect sign agreement **59 of 60**, one disagreement AZ 2013 (endpoint hold −0.080980 vs trapezoid +0.021245 USD/kWh-year).

## Spatial weighting effect on annualized 4→8h operating-value upper bound

Difference: EIA-860 2025 installed **county** fractions minus ReEDS developable potential **county** fractions; within-county resource-class potential distributions were *not calibrated to observed locations*. Units: USD/kWh-year of added stored energy.

| State | Trapezoid median across 15 source weather years | Min | Max | Positive years | Hold median | Hold positive years |
|---|---:|---:|---:|---:|---:|---:|
| AZ | −0.340861 | −1.087124 | +0.374850 | 6/15 | −0.214192 | 5/15 |
| CO | +0.410384 | −0.345945 | +0.722707 | 11/15 | +0.277415 | 11/15 |
| ID | +2.337690 | +1.631348 | +3.062122 | 15/15 | +2.361725 | 15/15 |
| WY | +2.636534 | +1.758072 | +3.707935 | 15/15 | +2.702031 | 15/15 |

Across 60 year×state comparisons, **47/60** are positive under trapezoid; **46/60** positive under hold. 2012 is one of 15 source-year references, not a random sample of possible future climate.

## Precise scientific interpretation

The **Idaho and Wyoming** positive geographic sensitivity remains directionally stable for all 15 source weather years under *both* numerical hour conventions; Arizona often moves in the opposite direction and Colorado has some negative years. This is direct evidence that the *assumed county share of nominal renewable potential* changes the conditional modeled value of energy storage duration; it is **not external evidence that 2025 EIA shares are the better forecast of hourly power generation**.

All results still use **fixed 2030 projected demand with 2012 reference weather**, even when source wind/PV use another weather year; true matched-weather demand remains untested. Source wind/PV CFs are **instantaneous samples**, not independently certified hourly MWh integrals; neither hold nor trapezoid validates the physical integration. The optimization is an **illustrative state-level copperplate SciPy HiGHS LP**, not an observed 2030 fleet, transmission simulation, market-revenue computation, or investment NPV.

## Manuscript implications

1. Update `15 of 16` to a clearly identified **four-year pilot only**, and add an authenticated all-year result: 59/60 hour-mode effect sign agreement; 15/15 positive for ID and WY under both hour conventions.
2. Avoid arbitrary `$10/kWh-year` pass/fail as headline: continuous signed effect and weather-by-state distribution are more robust and do not require a projected battery cost.
3. Cite source files and full run before accepting any revised figure: `paper_s_all15_720_lp.csv`, `paper_s_all15_240_duration_triplets.csv`, `paper_s_all15_120_siting_comparisons.csv`, `paper_s_all15_60_hour_method_pairs.csv`, `paper_s_all15_calendar_audit.csv`, `paper_s_all15_manifest.json`.
4. Until EIA-930 and same-weather load validations are done, do NOT claim the main physical limitations have been resolved.

**Data archive status:** GitHub Actions artifact exists but is not a durable DOI repository. Do not mark publication ready. PR #2 remains Draft.
