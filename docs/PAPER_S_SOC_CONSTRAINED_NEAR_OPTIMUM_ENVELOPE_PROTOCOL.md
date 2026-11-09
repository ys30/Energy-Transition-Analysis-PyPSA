# Paper S — explicit original-cost-cap SOC occupancy envelope (predefined protocol)

## Research question

The accepted [32 near-optimal SOC objective-perturbation experiment](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42704492819) showed that different schedules can have almost identical unperturbed toy LP costs but radically different binding-hour statistics. The new protocol asks a sharper **constrained optimization** question: among schedules that satisfy all original hourly balance equations, bounds and cyclic SOC condition and whose **original** toy variable objective is no more than a pre-declared small allowance above the optimum, what are the **minimum and maximum annual sums of end-of-hour SOC**?

The earlier 32-case evidence is a deterministic objective-perturbation sensitivity, not a mathematical strict alternate-optimum certificate. This follow-up optimizes the explicitly constrained objective sublevel set; it does **not** prove multiple exactly equal optimal LP bases or bound each individual hour's SOC independently.

## Locked protocol

1. Restore unchanged EFS 2030 original 8,760 ordinal-hour demand for the preregistered Arizona p28 (shape group 1) and Wyoming p24 (shape group 7).
2. For each of the same four preregistered supply/power/energy probes ([paper_s_soc_tiebreak.py](../src/energy_transition/paper_s_soc_tiebreak.py)), solve the **unmodified original HiGHS LP** to determine its optimal objective C*.
3. Confirm the three applicable cases with power = 0.25 × peak demand and energy = 1 × peak-demand-hour independently match the accepted source-archive 4h original variable costs.
4. Set **epsilon = max(USD 0.05, 10⁻⁹ × C*)**, in dollars. Add exactly one new linear inequality **C_original(x) ≤ C* + epsilon** to the original balance and bound system. This is an explicit *near-optimal cost set*, not an unmodified optimal face.
5. Optimize **min Σ SOC_end(t)** and **max Σ SOC_end(t)** as distinct secondary LPs, with the original energy balance, capacity ratings and cost coefficients unchanged.
6. Rescore each candidate under **C_original**, verify C_original ≤ C* + epsilon + USD 0.02 numerical allowance, cyclic SOC, all hourly balances, and the presence of the original primary-optimal SOC occupancy between the two computed extremes.
7. Produce baseline/min/max SOC hourly vectors and summarise average SOC, capacity-bound hours, charge/discharge-bound hours, throughput, cost gaps, and **the interval in total annual SOC occupancy**.

The interval is **not** an independent bound on individual-hour SOC or on the counts of binding hours. Those are descriptive outcomes for the two extremal-total-SOC schedules; they can vary across other solutions within the same objective sublevel set. The original source `LocalHourID` is an ordinal, not source-certified UTC.

## Execution and acceptance

Code: [cost-cap extension of original LP](../src/energy_transition/efs_cyclic_storage_lp.py), [source-backed envelope solver](../src/energy_transition/paper_s_soc_optimal_envelope.py), [small-LP unit tests](../tests/test_paper_s_soc_optimal_envelope.py) and [GitHub Actions workflow](../.github/workflows/paper-s-soc-optimal-envelope.yml).

Full planned scale: **8 source scenario configurations × three solutions (original optimum, min SOC, max SOC) = 24 annual LP solutions** with **210,240 source-hour rows** (24×8760). The two secondary min/max solves are **16 new constrained optimizations**, distinct from the eight original baseline LPs. There will be eight annual total-SOC intervals, not one universal bound. Completed counts and validated numerical outcomes may be reported **only** after a successful workflow and unrounded derived artifact.

## Paper S interpretation gate

The paper should report which proposed mechanism metrics are robust to constrained near-optimal primal schedules, and distinguish that from locally validated MW/MWh shadow-price sensitivity. Direct objective derivatives and normalized source-shape pseudoreplication limitations remain necessary.

**Limitations:** Seven Western-state source-projected EFS load, two selected source chronologies for this test, synthetic availability, no real solar/wind observation, noncertified physical time axis, no actual network-constrained Western OPF, no capital cost and no proven economic design optimality. Private full manuscripts are not committed to public GitHub.
