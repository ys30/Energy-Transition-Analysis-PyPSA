# Paper S — certified exclusive-operation feasible-window witness (10 November 2026)

**Validation:** archival-source reproducibility workflow [#42887951004](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42887951004) **SUCCESS**, using the original accepted 52,560 source-hour records from [#42851448558](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42851448558). No additional annual LP or exclusive-operation MILP was solved. This is an algebraically certified **feasible witness** and a rigorous *lower bound* on the mutually exclusive cost-capped temporal discharge interval width, not an exact MILP optimum.

## Analytical construction for the archived LP

Let `r,c,d,f,u,s` denote hourly renewable direct-to-load, battery renewable charging, battery discharge-to-load, firm supply, unused hypothetical renewable, and end-hour SOC. Let `η_rt=0.9` and `t=min(c,d/η_rt)`. Define an adjusted schedule:

```text
r' = r + η_rt t
c' = c − t
d' = d − η_rt t
f' = f
u' = u + (1 − η_rt)t
s' = s
```

**Why this works under the precise source implementation:** The original hourly balance is `r+c+u=A` and `r+d+f=L`. Each remains exactly unchanged. SOC recursion is `Δs=√η_rt·c − d/√η_rt`; the adjusted difference changes by `−√η_rt t+η_rt t/√η_rt=0`. Nonnegativity of `c'` and `d'` is ensured by the minimum; at least one becomes zero. The additional direct renewable `η_rt t` is no greater than **either** the original c or d, so `r'≤A`, `r'≤L` and `r'≤min(A,L)`. The original `c,d` power limits and `s` energy limit still hold. Original firm generation `f` and original SOC `s` remain unchanged. The original toy cost `5(r+c)+90f` decreases by exactly `5(1−η_rt)t` per hour, so an originally feasible near-optimal schedule with `C(x)≤C*+epsilon` remains feasible under **the same original cost cap**.

The algebra assumes a no-firm-charging model, a renewable direct-use and renewable-charge input coefficient of USD 5/MWh, nonnegative modeled unused renewable potential and η_rt<1. **It must not be transferred without proof to another storage formulation** (e.g., energy-price-based arbitrage or firm-charged batteries).

## Source-archive results and logically valid bound

| Original source zone | Relaxed min–max window discharge span (MWh) | Exclusive-operation feasible span **at least** (MWh) | At least % of relaxed span | Cost reduction from repairing archived maximum (USD) |
|---|---:|---:|---:|---:|
| Arizona p28 | 29,352.336139 | **29,349.089339** | **99.988939%** | 1.803777 |
| Wyoming p24 | 1,616.753223 | **1,616.712964** | **99.997510%** | 0.022366 |

The original archived `min` schedules are already exclusively charging-or-discharging in every source hour and therefore retain the relaxed minimum as the exclusive minimum. The archived relaxed maximum is an upper bound on the exclusive maximum; repairing it yields an **explicit feasible exclusive solution** and therefore a lower bound on that maximum. Consequently, the true exclusive feasible interval width lies between the values reported above and the original relaxed interval widths, subject to original LP numerical acceptance. These source windows are `LocalHourID` 4001–4168, not authenticated UTC/calendar weeks.

The only archived simultaneous charging/discharging cases were:

- Arizona source hour 4035 (maximum-window schedule): originally 3712.692349 MWh renewable charge and 3.246799 MWh discharge; repair eliminates this overlap, retains original SOC and firm supply, and decreases the original cost.
- Wyoming source hour 4137 (maximum-window schedule): 0.044732 MWh charge and 0.040259 MWh discharge; same complete repair.
- All four original and minimum-window schedules already had no same-hour charging and discharging.

All six corrected schedules pass the source hourly accounting transformation, unchanged capacity limits by construction, no-overlap postcondition and exact original-objective nonincrease. The new CI reports min/base/max source cases and bounds in machine-readable CSV.

## Manuscript inference gate

**Admissible statement:** Within this source-ordinal synthetic dispatch LP, wide selected-window storage delivery ranges **persist** even among mutually exclusive charging/discharging feasible schedules under the same near-optimal original objective ceiling. The relaxed LP's nonexclusive model structure is not a sufficient explanation for the observed large window interval.

**Not yet admissible:** the exact mixed-integer exclusive global maximum, measured renewable curtailment, actual power-grid reliability, economic value or a mathematically certified exact optimal face. No claims of model robustness to degradation-cost assumptions, self-discharge, reserve requirements, interzonal transmission, chronology calibration or year-specific real weather input.

Reproducibility: [construction program](../src/energy_transition/paper_s_exclusive_feasibility_witness.py), [unit tests](../tests/test_paper_s_exclusive_feasibility_witness.py), [CI workflow](../.github/workflows/paper-s-exclusivity-witness.yml). Accepted archive artifact `paper-s-certified-exclusive-feasible-window-witness` includes `paper_s_exclusive_window_interval_feasible_bounds.csv`, `paper_s_six_algebraic_exclusive_repair_certificates.csv` and source-scoped manifest.

The private Paper S manuscript v4 contains a corresponding Results subsection, Discussion revision and reviewer response; its full contents remain private and have **not** been committed to the public repository.
