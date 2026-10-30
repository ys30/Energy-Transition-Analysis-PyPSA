# Verified synthetic PyPSA AC Line capacity sweep

**Status: PASS** for a deliberately synthetic two-bus PyPSA + HiGHS dispatch test at [GitHub Actions run 41146602328](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41146602328), source commit `ac0ae745`. The general test-suite CI for that commit also [passed](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41146602365). Subsequent boundary-test fixture fixes passed [CI 41146778543](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41146778543).

## Solver-produced numerical results

| Synthetic line rating MW | Solved flow MW | Local backup dispatch MW | Optimized one-hour cost (arbitrary units) |
|---:|---:|---:|---:|
| 25 | 25 | 75 | 7,525 |
| 50 | 50 | 50 | 5,050 |
| 125 | 100 | 0 | 100 |

The demand at bus B is 100 MW, low-cost supply at bus A has marginal cost 1, and local backup supply has marginal cost 100. The one-hour optimized dispatch therefore saturates the line at 25/50 MW and no longer saturates the line when its 125 MW rating exceeds the 100 MW demand. These **solver-produced values** were transcribed from the action log and are independently available in the `project-b-synthetic-ac-line-smoke` workflow artifact.

## Scientific interpretation and next gate

This demonstration proves that **PyPSA `Line` objects and their rated capacities participate in this simple linear optimization** and that the resulting synthetic redispatch cost has the expected direction. It does **not** verify CISO–BPAT real topology, BA interchange measurements, branch reactance/impedance, voltage, thermal rating, AC nonlinear power flow, N-1 security, or investment savings. No synthetic line parameter is represented as a real-world engineering measurement.

The `transmission_evidence_gate.py` and `pypsa_line_evidence_adapter.py` modules reject missing/unsourced physical inputs. A future real-grid experiment requires independently verified topology, `s_nom` and ohmic `r/x`, correct bus voltage/base definitions, and provenance suitable for audit. Without these inputs, do not claim a calibrated inter-BA grid.
