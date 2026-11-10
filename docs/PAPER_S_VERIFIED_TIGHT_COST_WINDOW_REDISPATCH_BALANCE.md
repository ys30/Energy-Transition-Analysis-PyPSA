# Paper S — Verified tight-cost window reallocation and outside-window balancing

**Numerical evidence is accepted and source-backed.** Original selected-window discharge LP [#42780417107](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42780417107) passed the old 2030 EFS source-hour and HiGHS model consistency checks. Absolute original-cost tolerance ladder [#42848939530](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42848939530) **success**. The accompanying source-derived [Figure S19 run #42849647035](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42849647035) **success**. The independent inside/outside window accounting workflow [#42850121414](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42850121414) **success**, using only the original candidate schedule archives. The last is a mass-balance identity audit of original reported annual and window discharge, not an additional LP solve.

## Tightening original-variable-cost allowances

Original source window = `LocalHourID` **4001–4168**, synthetic ordinal Wave A, battery power 25% of original source-zone demand peak and energy storage capacity one peak-MW-hour. This is **not an authenticated calendar week**.

| Source representative | Permitted USD cost increase above C* | Minimum–maximum delivered discharge within 168 source hours (MWh) | Span (MWh) |
|---|---:|---|---:|
| Arizona p28 | 0.05 | retained in archive | **29,349.159** |
| Arizona p28 | 0.20 | retained in archive | **29,349.430** |
| Arizona p28 | 1.803783 (previous 1e-9 × C*) | 88,047.183–117,399.519 | **29,352.336** |
| Wyoming p24 | 0.05 | retained in archive | **1,616.718** |
| Wyoming p24 | 0.20 | retained in archive | **1,616.733** |
| Wyoming p24 | 0.402599 (previous 1e-9 × C*) | 0–1,616.753 | **1,616.753** |

The USD 0.05 allowance preserves **99.9892%** of the Arizona archived interval and **99.9978%** of the Wyoming archived interval. For the strict-dollar cases, the original objective recomputation verified the candidates' actual additional cost of approximately USD 0.04999–0.05; this was below their cost allowance. The independent checking gate also admitted up to USD 0.02 numerical excess but did not need it to explain the reported run outputs.

Although the allowed *relative* perturbation is extremely small in relation to original C* (~USD 1.8 billion Arizona, USD 0.40 billion Wyoming), this remains a **finite-precision near-optimal LP** experiment. Not an exact-optimal-face proof.

## Explicit inside/outside source-hour discharge reconciliation

Compare separately optimized schedules against the original unmodified HiGHS optimum in the **middle window**. The outside-window change is computed exactly as `change in full-year delivered discharge - change inside predeclared window`.

| Original zone | Candidate LP objective for window | Change inside 168h (MWh) | Change outside 168h (MWh) | Full-year net change (MWh) |
|---|---|---:|---:|---:|
| Arizona p28 | Minimize window discharge | −20,118.974 | +20,118.953 | −0.021 |
| Arizona p28 | Maximize window discharge | +9,233.362 | −9,230.115 | +3.247 |
| Wyoming p24 | Minimize window discharge | −260.530 | +260.525 | −0.0048 |
| Wyoming p24 | Maximize window discharge | +1,356.224 | −1,356.183 | +0.0403 |

All rows originate from the previously accepted source LP candidate archive (`paper_s_6_source_window_discharge_lp.csv` per zone). The derived source-audit output `paper_s_eight_inside_outside_window_discharge_changes.csv` also covers the early 1–168 source-hour window. Because the same candidate determines all three columns and the identity is checked per candidate, this is direct evidence that major changes in delivered energy inside the window are offset by changes in the **aggregate remainder of the year**.

**Do not claim that a specific different hour receives the shifted service.** The original archival candidate summaries preserve annual totals, not full per-hour alternative candidate discharge vectors. The 'outside' value is the complement of the selected window, not a localized event or physically justified service guarantee. Min/max schedules are separately optimized, not one causal transition from one operating schedule to another.

## Revised manuscript Results language

> We evaluated the sensitivity of aggregate storage delivery to solution-selection effects using a 168-source-hour window, first under an explicitly bounded near-optimal original-cost feasible set and then with a progressively tighter absolute cost allowance. In the Arizona Wave-A representative configuration, the feasible range in window-delivered energy was 29.35 GWh under the previously accepted `10^-9 × C*` budget, and remained 29.349 GWh under a USD 0.05 budget. Inspecting the archived window-optimal schedules showed that a decrease of approximately 20.119 GWh within this window was offset by a nearly equal increase outside the window, leaving the full-year delivered-energy total almost unchanged. Thus stability of an aggregate annual throughput metric does not imply stability of discharge allocation among source-hour intervals. This conclusion is conditional on the model's original constraints, synthetic resource profiles, a small nonzero numerical cost allowance and source ordinal hours not verified as physical UTC.

## Interpretation boundaries and next experiment

- Separate original optimal variable **cost** from **dispatch schedule** and from economic investment decisions: no battery CAPEX, cycling degradation, reliability/reserve or network OPF is in this model.
- The seven source-demand patterns have only two geographic representatives in this experimental sequence. Source supply is synthetic, not meteorologically observed or timestamp-verified.
- Neither cost tolerance USD 0.05 nor the reported CI acceptance proves exact alternative optima; the envelope is a cost-sublevel-set result solved in finite precision.
- The next meaningful scientific diagnostic is to archive **full alternative candidate hourly charge, discharge and SOC trajectories** for one predeclared original source-window experiment and verify their within-window and outside-window energy accounting against the annual archived totals. Then one may identify the actual source-hour redistribution without implying physical calendar-day reliability.
- This result is appropriate for a private Paper S manuscript **supplementary sensitivity subsection**. Do not overstate it as observed grid operation.

### Reproduction anchors

- [Original LP and source-window procedure](../src/energy_transition/paper_s_window_discharge_envelope.py)
- [Cost tolerance ladder code](../src/energy_transition/paper_s_window_tolerance_ladder.py)
- [Source-certified Figure S19 code](../src/energy_transition/paper_s_window_tolerance_figures.py)
- [Inside/outside discharge reconciliation](../src/energy_transition/paper_s_window_outside_discharge.py)
