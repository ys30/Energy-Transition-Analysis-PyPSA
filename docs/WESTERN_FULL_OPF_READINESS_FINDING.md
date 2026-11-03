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

## Important scope clarification — already verified load-bearing networks

The **zero loads, zero generators, one snapshot** finding above applies ONLY to the `real-western-base-network.nc` topology artifact. It must not be generalized to every network artifact in this repository.

Previously successful [EFS load-bearing network workflow #41281576025](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41281576025) created source-topology-based Western load networks with **8,760 ordinal local-hour snapshots, 20 EFS-derived zonal Load components, and independently verified NetCDF roundtrips** for each of 2030, 2040, and 2050. Their documented (incomplete-Western) EFS allocation totals are ~274.707, ~306.839, and ~350.871 TWh, respectively. See [VERIFIED_EFS_LOAD_BEARING_NETWORKS_2030_2040_2050.md](VERIFIED_EFS_LOAD_BEARING_NETWORKS_2030_2040_2050.md). These are **future scenario** loads, not historical observations; spatial coverage is partial and clocks remain ordinal rather than timezone-aligned.

There is also an already successful [four-bus/two-EFS-load, real-line, illustrative-generation 24h/168h optimization workflow](VERIFIED_TWO_LOAD_AC_PATH_2030_2050_RESULTS.md), which **does not** establish genuine generator provenance or full-Western OPF readiness.

**Current priority is verified generator fleet + operating constraints + costs, and regional/time alignment of load, not re-creation of the already available EFS load networks.**

The expanded readiness workflow [western-full-opf-readiness.yml](../.github/workflows/western-full-opf-readiness.yml) now audits BOTH the original topology artifact and all three verified EFS load-bearing NetCDF files to enumerate the precise remaining inputs. Until its new run passes, the three audits should be treated as pending validation, not new results.
