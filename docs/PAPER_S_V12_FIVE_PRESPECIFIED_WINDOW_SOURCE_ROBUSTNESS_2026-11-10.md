# Paper S — five-window original-source sensitivity (10 November 2026)

**Evidence:** [dedicated original-source five-window CI #42919689808](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42919689808) **SUCCESS**: two original representative 2030 EFS projected-load source groups, five **predeclared mutually disjoint** 168-ordinal-hour windows per group, one unmodified primary solution plus minimum and maximum battery discharge window objectives per window. The original 4001–4168 case was cross-checked against historical accepted discharge-window archives. This is a **source-clock-ordinal synthetic-resource linear program**, not calendar-weeks or actual Western-grid OPF.

## Predeclared five-window selection

The source windows were fixed in code **before the new LPs**: `[1,168]`, `[2001,2168]`, `[4001,4168]`, `[6001,6168]`, `[8001,8168]`. All are 168 source ordinals, do not overlap, and retain original source hour order. The 4001–4168 reference was already selected in a previous experiment, not independently randomly selected. These five windows cannot establish population-level frequency across the full year.

Identical source and model assumptions: Wave A mathematical availability profile at 90% of source-zone peak, 2030 EFS source-load year, battery P=.25 source peak MW, E=1 source peak MW-hour, sqrt(0.9) charge/discharge efficiency, fixed original LP objective `C=5 Σ(r+c)+90 Σ(f)`, and identical near-optimal cap `C(x) <= C* + max(0.05 USD, 10^-9 C*)`. The original baseline LP is reused across all windows within a source group; ten group-window interval pairs correspond to **22 unique LP solves**, recorded as 30 window/schedule rows. Do not report the 30 source rows as independent experiments.

## Original-source verified discharge span, MWh

| Source zone | 1–168 | 2001–2168 | 4001–4168 original | 6001–6168 | 8001–8168 |
|---|---:|---:|---:|---:|---:|
| Arizona p28 | **3.268168** | **1,286.517487** | **29,352.336139** | **251.728977** | **2,485.499552** |
| Wyoming p24 | **4.116797** | **2,712.411825** | **1,616.753223** | **2,135.073029** | **2,319.566221** |

All ten sample-window spans exceed 1 MWh, **but are extremely heterogeneous in magnitude**. Arizona's original 4001–4168 window is the largest of the five and is **not representative** of its selected year. Wyoming has larger spreads at 2001–2168, 6001–6168 and 8001–8168 than in the originally selected window. The zero-based minimum in three Wyoming windows is a feasibility result for the toy LP sublevel set, not observed outages.

Normalized by primary solution **annual** discharge, Arizona spans vary from ~0.000063% to 0.562677%, while Wyoming spans vary from ~0.005356% to 3.528620%. The occasionally >100% ratios based on a small **window** baseline reflect a denominator artifact and must not be called probability or availability.

## Interpretation and important limitations

The original conclusion that annual totals alone do not identify selected-window discharge is qualitatively supported across several separated source windows in both original source groups. **It does not show every window has an equally severe problem**; in fact, the strong variation across windows is a material refinement of the scientific result. Any claim that the 27.136% original Arizona relative spread is typical or generalizable must be removed.

The near-optimal allowance is strictly positive and solver tolerances remain finite; this is **not proof of multiple exact equal-cost optimal schedules**. The source demand chronology is an ordinal, its physical UTC year and hour alignment remain uncertified, and the renewable availability is hypothetical. Original 20 zones represent only seven unique within-year positive demand shapes, not IID observations.

## Source-preserving program and artifacts

- [Five-window source LP program](../src/energy_transition/paper_s_five_window_robustness.py)
- [Selection, overlap and admission tests](../tests/test_paper_s_five_window_robustness.py)
- [Independent original-source GitHub Actions](../.github/workflows/paper-s-five-window-robustness.yml)
- [Accepted CI #42919689808](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42919689808) archives two zone-level fifteen-row schedule files and consolidated ten-interval + thirty-window/schedule records.

The private v12 manuscript includes Results 3.8, Discussion 4.8 and Supplementary Figure S3 (two-panel absolute MWh intervals and baseline optimal schedules) and a source acceptance appendix. **That private manuscript and its figure bytes are not uploaded to this public repo.**

**Next scientific question:** Can an independently specified predictor (e.g., physical surplus, hourly tightness or primal dual shadow price) distinguish windows with wide versus narrow attainable discharge intervals? Answer using non-circular holdout methodology and do not fit/evaluate solely on these five nonrandom, ordinal windows.
