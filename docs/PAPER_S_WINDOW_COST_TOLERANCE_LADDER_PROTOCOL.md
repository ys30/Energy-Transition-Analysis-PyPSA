# Paper S — preregistered fixed-window discharge cost-tolerance ladder

## Purpose and input controls

The verified [Figure S18 fixed-window source-hour experiment](PAPER_S_VERIFIED_WINDOW_DISCHARGE_NONUNIQUENESS.md) found an approximately 29.35-GWh range in Arizona p28 discharge in source hours 4001–4168 under a cost allowance of `max(USD 0.05, 1e-9 * C*)`, despite a roughly 3.27-MWh range in the annual total. The present experiment checks **how sensitive that interval is to the near-optimal cost allowance**, rather than assuming this range certifies a mathematically exact alternate-optimum face.

The two input groups are the historically archived original 2030 Arizona p28 and Wyoming p24 source-demand time series. Use original `LocalHourID` 1–8760, synthetic ordinal wave A, installed battery charge/discharge power = 0.25 × source peak MW, energy capacity = 1.0 × peak MW-hour, and the **predeclared window 4001–4168**. No physical UTC interpretation is admitted.

Re-solve the unchanged original LP to get `C*` and reconcile against its accepted historical 4h source case. For each fixed cost allowance below, add `C_original(x) <= C* + allowance` and separately minimize and maximize the sum of delivered battery MWh in the selected source-hour window:

| Cost allowance name | Absolute allowed increase (USD) |
|---|---|
| strict absolute | 0.05 |
| moderate absolute | 0.20 |
| previously accepted near-optimal | `max(0.05, 1e-9 * C*)` |

The original LP primal feasibility and cyclic SOC bounds are unchanged. Candidate schedules must be independently re-scored using unperturbed original objective coefficients. A separate USD 0.02 numerical checking allowance is documented and cannot be confused with the optimization cost cap.

Acceptance requires all six original-source interval results (two groups × three tolerances), each with a min and max constrained LP solution plus original source optimum, and an input archive validity gate. Numeric envelope spans should be nondecreasing as allowances are enlarged, up to explicitly allowed solver noise.

## Critical interpretation

- This is a small **near-optimal sublevel-set sensitivity analysis**, not mathematical proof that the exact LP optimal face contains multiple schedules.
- Even USD 0.05 above a hundred-million-dollar objective is a nonzero allowance, and primal feasibility, dual feasibility and original-cost recomputation are all finite precision.
- The interval bounds **one selected 168-hour sum**. It does not bound independent hours, battery availability at stress events, or grid reliability.
- Temporal “weeks” are original source ordinal 168-hour stretches, not independently verified UTC/calendar timestamps.
- Synthetic assumed renewable supply, no full Western OPF, no interzone transmission, no battery investment/degradation/financing cost.

## Reproducibility

- [Cost-tolerance implementation](../src/energy_transition/paper_s_window_tolerance_ladder.py)
- [Locked tolerance tests](../tests/test_paper_s_window_tolerance_ladder.py)
- [GitHub Actions source restoration and run](../.github/workflows/paper-s-window-tolerance-ladder.yml)

**No numerical conclusion should be inserted here before a successful completed Actions run and available derived artifact.** The full Paper S manuscript remains private; only evidence methods and derived summaries belong in the public repository.
