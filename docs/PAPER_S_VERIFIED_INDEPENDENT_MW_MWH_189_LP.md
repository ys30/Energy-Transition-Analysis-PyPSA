# Paper S — verified independent MW and MWh factorial mechanism (2030)

**Audit status: SUCCESS.** [Archived-source seven-shape factorial run #42674534963](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42674534963) passed tests, all original 4h/8h baseline checks, all 189 cyclic 8,760-hour LPs, all 252 fixed-axis contrasts, and artifact upload. Input seven distinct source-demand shapes are the preselected representatives in [source-verified 63-LP audit #42511072562](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42511072562).

## Factorial design

The HiGHS `solve_zone` function has a backward-compatible optional `storage_energy_peak_hours` parameter. When unspecified the original baseline remains **capacity MWh = MW × specified duration**; when explicitly supplied, the MWh rating is `peak_load_MW × storage_energy_peak_hours`, independent of `battery_power_peak_ratio`. The original objective and primal constraints are unchanged.

- Storage MW ratings: 0.125, 0.25, 0.50 × original demand peak MW
- Storage MWh ratings: 0.5, 1.0, 2.0 × original peak MW × one hour
- Three **synthetic** resource shapes: flat 50%, ordinal wave A, ordinal wave B
- Seven **distinct source-demand chronologies** represented once each, for 2030, with fixed 90% roundtrip efficiency and USD 5 renewable / USD 90 firm coefficients
- **189 = 7 × 3 × 3 × 3** full-year optimizations
- **252** controlled adjacent increments: 126 adding MWh with MW fixed and 126 adding MW with MWh fixed
- Original 0.25-peak-MW / 1.0-peak-MWh and 0.25-peak-MW / 2.0-peak-MWh cells reproduce the original 4h/8h archive for all seven demand profiles and all three resource shapes

The positive-increment classification is `additional discharged MWh > 1e-3`. Counts below are **numbers of seven distinct source patterns**, not p-values and not seven independent field systems.

## Main source-derived counts

### Add MWh at fixed 25%-of-peak MW

| Synthetic supply | Energy 0.5→1 peak-hour, positive groups | Energy 1→2 peak-hours, positive groups |
|---|---:|---:|
| Flat | 1/7 | 1/7 |
| Wave A | 7/7 | 6/7 |
| Wave B | 7/7 | 6/7 |

The same 0.5→1 increase has positive delivered-energy response across all seven source shapes in the wave assumptions, including Wyoming. When capacity increases from 1→2 peak-hour equivalents at the **same** 0.25 peak MW rating, Wyoming no longer gains delivered discharge.

### Add MW at fixed 1 peak-hour of MWh

| Synthetic supply | MW 12.5%→25% peak, positive groups | MW 25%→50% peak, positive groups |
|---|---:|---:|
| Flat | 6/7 | 0/7 |
| Wave A | 7/7 | 1/7 |
| Wave B | 7/7 | 0/7 |

At fixed MWh, increasing power first unlocks more modeled battery throughput in many of the original demand chronologies; raising power beyond the 25%-of-peak level usually gives little or no further discharged energy with this capacity rating. The behavior is **conditional on the investigated grid and price assumptions**, not an engineering rating recommendation.

### Wyoming p24 as a controlled mechanism counterexample

- Under *fixed MW=25% of source peak*, adding energy 0.5→1.0 source-peak-hour increases annual delivered discharge by approximately **4,559 MWh (Wave A)** and **816 MWh (Wave B)**, whereas further energy 1→2 source-peak-hours adds **0 MWh** for both.
- Under *fixed MWh=1 peak-hour*, raising MW 12.5%→25% increases delivered discharge by approximately **1,720 MWh (Wave A)** and **143 MWh (Wave B)**, whereas MW 25%→50% adds approximately **220 MWh (Wave A)** and **0 MWh (Wave B)**.
- This sharp change in the energy- and power-axis marginal response explains why the earlier *duration-with-power-coupled* experiment can show zero 4h→8h additional discharge in Wyoming: it tests a region of the LP design surface where energy capacity no longer yields new dispatch. It does **not** prove a real physical storage optimum or exclude other grid reliability services.

## Critical interpretation limits

1. The unit of the MWh setting is `peak_MW × 1 hour`, *not* a normalized percentage of annual consumption. The implied nominal duration is `energy_peak_hours / power_peak_ratio`; no fixed duration is maintained across the factorial.
2. More feasible MW/MWh cannot increase minimum LP objective, but delivered battery MWh may in general behave nonmonotonically under alternative cost functions or alternative optimal bases. Report the actual discharged-MWh and toy objective separately, and keep tolerance rules visible.
3. All seven load shapes are from the staged EFS/LAF demand dataset, not statistically independent sampled regions. Source `LocalHourID` is **not certified UTC**; 2040 calendar-label anomaly has not been resolved.
4. Resource profiles are explicitly synthetic 24-ordinal shapes, not observed solar/wind weather.
5. This LP excludes storage CAPEX and degradation, interzone transmission, unit commitment, reserves and network OPF. Its variable-cost responses cannot identify an economically optimal MW or MWh rating, real Western grid savings or observed curtailment.

## Reproducibility

- [Backward-compatible independently parameterized LP](../src/energy_transition/efs_cyclic_storage_lp.py)
- [Original 189-LP factorial and exact baseline reconciliations](../src/energy_transition/paper_s_orthogonal_power_energy.py)
- [Tests](../tests/test_paper_s_orthogonal_power_energy.py)
- [GitHub Actions full seven-shape experiment](../.github/workflows/paper-s-orthogonal-mw-mwh.yml)
- Passed run artifact: `paper-s-orthogonal-189-lp-252-contrasts`, containing full LP CSV, all one-axis contrast CSV and positive counts CSV.

**Paper S placement:** The findings support a *model-conditional, constraint-specific* mechanism subsection and paired Figure S11 (MWh increment at fixed MW) and Figure S12 (MW increment at fixed MWh). Keep full manuscript drafts private.
