# Verified six-bus zero-flow root cause (2026-11-01)

Source: successful [GitHub Actions 41386813005](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41386813005), commit `26cf2eb4aa31dae49435a16acca91bd52157d6aa`. This documents an **engineering diagnosis**, not a calibrated Western dispatch result.

## Exact selected topology

The six-bus connected graph is a five-edge star centered on bus `2074132`:

| Line ID | Endpoint 1 | Endpoint 2 | Peak absolute flow, MW (2030, 2040, 2050) |
|---|---|---|---:|
| 100242 | 2074132 | 2077126 | 200.09 each |
| 100243 | 2074132 | 2077142 | 0 each |
| 100244 | 2074132 | 2077159 | 0 each |
| 100245 | 2074132 | 2077163 | 0 each |
| 100246 | 2074132 | 2077177 | 0 each |

The model places **all EFS sample load** at hub `2074132`, an illustrative high-cost generator at the hub, and an illustrative low-cost generator at leaf `2077126`. Other four leaves have neither generation nor loads. Because the selected topology is a tree, the four empty leaf branches have zero net injection and zero flow by nodal balance. They are not shown to be physically unused in the full Western network.

From the verified 2030 output, illustrative generator dispatch totals: remote **4,802.16 MWh** and local **13,966.780533598536 MWh** over 24 ordinal local hours. The binding 200.09-MW line permits the remote generator to supply at most 200.09 MW in each hour, with the hub generator filling remaining demand. This is structurally expected given the $10/MWh versus $100/MWh illustrative costs.

## Consequence for research

Do **not** present four zero-flow branches as a grid result. The current experiment is a **one-edge economic transport bottleneck embedded in a star-shaped electrical test case**. It confirms the solver, constraints and input data path, not regional congestion diversity.

The next experiment must not redistribute demand among leaves without sourced bus or zone allocation. It should select an actual connected subgraph with *at least two source-admitted EFS load buses*, establish which external lines are excluded and whether the subgraph boundary affects physical validity, then add clearly labeled generator assumptions. Compare the new model to this intentionally simple benchmark and report bus residuals and line flow distributions. Preserve full Western model and time-zone calibration caveats.
