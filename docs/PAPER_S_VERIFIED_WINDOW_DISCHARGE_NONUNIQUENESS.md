# Paper S — verified source-ordinal window discharge redistribution under the same original near-optimal cost cap

**Accepted original-source experiment:** [window-bound full-year LP workflow #42780417107](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42780417107), **success**. Arizona p28 and Wyoming p24 2030 source-demand sequences, same synthetic ordinal Wave A availability, peak-power ratio 0.25 and energy capacity one peak-MW-hour. The original 8,760-hour projected EFS/LAF demands and original annual LP variable objective were restored and matched to previously accepted archival summaries. Each source zone used the **same explicit original cost cap** `C_original(x) <= C* + max(USD 0.05, 10^-9 * C*)` as the previously accepted annual SOC envelope [#42716052153](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42716052153) and annual discharge envelope [#42747095388](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42747095388).

## New research question and locked time windows

An annual sum of energy delivered from the battery can be uniquely or nearly uniquely determined even when **which source hours receive that delivery** is highly nonunique. To check this, we defined two **non-overlapping, source-ordinal 168-hour windows before looking at any dispatch outcomes**:

- `early_1_168`: original `LocalHourID` 1–168.
- `middle_4001_4168`: original `LocalHourID` 4001–4168.

For each window, first obtain the original unperturbed optimum, then separately **minimize and maximize discharge delivered within that 168-hour window**, while enforcing unchanged hourly renewable supply, load, SOC conservation, all power/energy capacity bounds, zero terminal SOC and the **same original cost cap**. All eight secondary LPs plus original baselines were re-scored under the unperturbed variable objective. This is a cost-capped *window-total* range, **not a pointwise/hour-by-hour band**. These source ordinal windows **are not authenticated UTC/calendar weeks**.

## Original precise interval results

| Original source demand | Fixed ordinal window | Original window discharge (MWh) | Min (MWh) | Max (MWh) | Span (MWh) | Span / baseline |
|---|---|---:|---:|---:|---:|---:|
| Arizona p28 | 1–168 | 102,721.738 | 102,721.717 | 102,724.985 | 3.268 | 0.00318% |
| Arizona p28 | 4001–4168 | 108,166.156 | 88,047.183 | 117,399.519 | **29,352.336** | **27.14%** |
| Wyoming p24 | 1–168 | 4.0765 | 0 | 4.1168 | 4.1168 | 100.99% |
| Wyoming p24 | 4001–4168 | 260.530 | 0 | 1,616.753 | **1,616.753** | **620.56%** |

Full unrounded values are in Actions artifact `paper-s-four-cost-capped-window-discharge-intervals`: `paper_s_four_preregistered_window_discharge_intervals.csv` plus all 12 source-scored candidate summaries.

The Arizona second-window span is approximately **29.35 GWh**, whereas the previous [annual discharge interval](PAPER_S_VERIFIED_ANNUAL_DISCHARGE_COST_CAP_ENVELOPES.md) for the exact same Arizona Wave A, P=25%, E=1 configuration was only **3.268 MWh**. The Wyoming second-window span of about 1,616.75 MWh likewise vastly exceeds its prior annual interval of 0.045 MWh. **Those extrema come from separately optimized feasible schedules**; no single min/max pair should be read as simultaneous maximum transfer between exactly those two windows. The annual objective constraints are the same, not a causal claim or hourly stress test.

**Main conclusion:** The previously documented stability of *annual battery-delivered energy* does **not** imply stability in its **allocation to particular source-hour intervals**. The original HiGHS output is just one valid minimum-cost schedule; it is not sufficient evidence that delivery reliably occurs in the same modeled time window across all nearly cost-equivalent schedules.

Wyoming's very high relative percentages must be read with care: its first-window original discharge is just ~4 MWh, so a small absolute difference gives >100%. The second-window increase remains material in absolute MWh relative to that zone's original annual discharge (~76.87 GWh), though this is a synthetic model, not a reliability estimate.

## Admission-gated manuscript paragraph

> We tested whether nearly invariant annual battery discharge implies temporally stable delivery by independently minimizing and maximizing discharge within two prespecified, nonoverlapping 168-source-hour windows. The experiment retained the original hourly linear constraints and bounded additional unperturbed variable cost by `max(USD 0.05, 10^-9 × C*)`. In Arizona p28 under synthetic wave A at a power rating of 25% of local peak load and energy rating of one peak-load hour, the second window's attainable discharge varied from 88.05 to 117.40 GWh, despite an annual delivered-discharge envelope only about 3.27 MWh wide. Consequently, aggregate annual operational outcomes can be robust to near-optimal schedule selection even when the timing of delivered storage service is not. These windows use unvalidated physical time ordinals and must not be interpreted as a calibrated reliability or ramping-service assessment.

## Figure S18 and reproducibility

- [Source-backed min/max selected-hour LP solver](../src/energy_transition/paper_s_window_discharge_envelope.py), [original cyclic LP with optional hour selection](../src/energy_transition/efs_cyclic_storage_lp.py), [tests](../tests/test_paper_s_window_discharge_envelope.py), [source-archived Action](../.github/workflows/paper-s-window-discharge-envelope.yml).
- [Figure S18 rendering/validation](../src/energy_transition/paper_s_window_discharge_figures.py), [tests](../tests/test_paper_s_window_discharge_figures.py), [plot workflow](../.github/workflows/paper-s-window-discharge-figures.yml). **Do not label the figure as accepted until its specific GitHub workflow succeeds**.
- Plot panels use **separate absolute-MWh x-axis ranges**, with black markers showing the original solution and horizontal ranges showing the two separately optimized time-window discharge extrema. They are **not** statistical confidence intervals.
- The intervals are for **one assumed 2030 resource profile and two selected source-demand shapes**, not all seven shapes, future years or observed operation.

## Evidence boundaries

Original source `LocalHourID` is a per-year ordinal, not independently certified UTC; synthetic supply is mathematical and not measured wind/solar. The objective is an illustrative operational LP without transmission, generator commitment, weather-correlated renewables, storage capital/financing/degradation, reliability/reserve criteria, interzonal exchanges or real Western Interconnection OPF. These near-optimal bounds are defined on a tiny **cost-sublevel set**, not an exact certified LP optimal face. Window delivery variability is **not** evidence of reliability failure or economic benefit, only of schedule nonuniqueness under the stated model.

Next diagnostic: compare minimum/maximum battery service within grid-relevant *independently verified* critical demand windows, and repeat at **different cost tolerances** to check whether tiny objective perturbation and solution degeneracy cause the apparent temporal flexibility. The public repository preserves only methodology/aggregates; the full manuscript stays private.
