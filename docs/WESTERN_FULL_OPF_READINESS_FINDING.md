# Western full OPF readiness gate — observed source network

Evidence: [read-only real Western network audit #41548690972](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41548690972), [CI #41548690914](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41548690914).

The actual base PyPSA-USA Western network artifact has **10,157 buses, 9,726 lines, 2,080 transformers**, **zero generators**, **zero loads**, and **one snapshot named `now`**. It has zero generator and load time-series columns. Source line and transformer endpoint checks pass.

**Decision: the topology artifact is NOT a historical-dispatch-ready full network.** A successful topology export, a Colstrip 500-kV synthetic transformer, or a local two-bus transfer linear program cannot establish whole-Western OPF results.

The `western_full_opf_readiness_audit.py` emits an explicit `full_opf_ready` boolean and `missing_required_inputs` list. Its checks are a conservative baseline prerequisite; even after these inputs exist, one must inspect unit status, chronology, marginal cost/fuel assumptions, load shapes, network islanding, solver settings and convergence. Do not claim OPF-ready merely based on this preliminary gate.

## Required research-data integration

1. Obtain source-version-compatible PyPSA-USA workflows to attach EIA generators and time-aligned loads to source-network buses.
2. Verify provenance, year and time-zone consistency for generation and loads; preserve EIA pre-operational missing values.
3. Keep Clearwater `66183` and `66811` off empirical power-flow injections until their actual POI to the modeled physical bus and transformer are verified. Colstrip `sub_id 39703` is geographically corroborated but has no represented 500-kV interface.
4. Only then try an explicitly bounded, solved full-network OPF, compare solver feasibility and controls, and distinguish sourced/verified from hypothetical inputs.

No historical Western OPF or calibrated Clearwater injection has been executed.
