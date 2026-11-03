# Three-bus, three-snapshot synthetic-source OPF verification

This experiment extends the successful two-bus source-topology solver benchmark to **three source-network bus records, two source-model AC Line records, and three synthetic hourly snapshots**. It is an engineering verification exercise, not real Palo Verde dispatch, nor the full Western OPF.

**Implementation:** `src/energy_transition/source_topology_three_bus_multihour_opf.py`

**Workflow:** [source-topology-three-bus-multihour-opf.yml](../.github/workflows/source-topology-three-bus-multihour-opf.yml)

The procedure selects two **distinct** same-voltage, positive-reactance neighbors of original model Bus `2040841`. The original source Line IDs, bus endpoints, resistance and reactance are retained. Source Line capacity values are not assumed accurate: the optimization substitutes clearly **hypothetical** ratings of 25, 50, and 125 MW. It also creates purely hypothetical low-cost supply at the anchor (cost 1), expensive backup supply at each leaf (cost 100), and hourly load profiles [60, 90, 120] MW and [40, 75, 100] MW at the leaf buses.

The DC linearized PyPSA OPF is checked against a simple radial-network analytical optimum: each branch imports `min(demand, branch_capacity)` of low-cost supply and local backup serves any residual. All three hourly snapshots are verified for nodal aggregate generation/consumption balance and line-capacity feasibility. Total numerical objective is in **synthetic cost units**, not USD.

Expected analytical objective values (specification, **not** proof of CI result):

| Hypothetical per-branch rating | Three-hour low-cost supply | Three-hour backup supply | Expected objective |
|---:|---:|---:|---:|
| 25 MW | 150 MWh | 335 MWh | 33,650 |
| 50 MW | 290 MWh | 195 MWh | 19,790 |
| 125 MW | 485 MWh | 0 MWh | 485 |

**Source and scientific limits:** The [underlying Western grid model is synthetic](WESTERN_SYNTHETIC_NETWORK_PROVENANCE.md). No actual generator-to-bus mapping, validated thermal ratings, real dispatch observations, generator availability or measured costs have been supplied. Three synthetic time steps do not represent EFS hourly operation. No physical Palo Verde POI identification, empirical calibration or full-Western solution may be asserted from these results.

The workflow stores a JSON artifact with the selected source Line IDs, source resistance/reactance, and every hourly solved flow and dispatch. Report success only after the workflow reaches a successful conclusion and numerical checks pass.
