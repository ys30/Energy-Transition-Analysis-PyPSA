# 10-bus, six-hour synthetic Western source-topology OPF

This experiment uses a reproducible **10-bus radial subtree of the pinned Breakthrough Energy synthetic Western model**. It is a numerical engineering test, **not** observed Palo Verde operation, true Western OPF, or an EIA-860 plant-to-bus crosswalk.

Code: `src/energy_transition/source_topology_ten_bus_six_hour_opf.py`

Workflow: [source-topology-ten-bus-six-hour-opf.yml](../.github/workflows/source-topology-ten-bus-six-hour-opf.yml).

## Model and assumptions

- Starting from source-model Bus `2040841`, the script selects a 10-bus acyclic tree with nine existing, positive-reactance, same-voltage source lines. Actual model Line IDs, endpoints and `r`/`x` are preserved for reproducibility.
- **Invented scenario assumptions:** all nine Line ratings are set to 60 or 120 MW, six representative *synthetic* one-hour loads vary across nodes and time, and solar availability ranges from 0 to 90% of an assumed 125 MW generator. A low-cost central generator and high-cost backups at every receiving bus guarantee feasible dispatch.
- **Costs are synthetic units, not dollars.** Solar marginal cost is 0, central marginal cost 20, and local backups 100; source network ratings and actual generator behavior are not treated as verified.
- The Linopy/HiGHS-based PyPSA linearized OPF runs once for each assumed common line rating. Every hourly generator/load sum is checked, and every Line active power transfer is checked against its assumed limit. Solar dispatch is checked against hourly assumed availability. The reconstructed marginal-cost objective is compared with PyPSA's result, and cost should be non-increasing when all line ratings are relaxed.

The artifact `ten_bus_six_hour_synthetic_opf.json` records the selected source IDs and source electrical parameters, plus synthetic hourly demand, solar, backup, maximum branch flow, count of binding constraints, power-balance residual and scenario objective.

## Interpretation boundary

The source is the geographically referenced **synthetic** US transmission test network, not a utility-certified facility database. Synthetic topology is the only provenance-preserving element: the historical/future load shapes, thermal limits, generators, costs and solar capacity are artificial. No 2030/2040/2050 energy-transition scenario results, 8760-hour reliability metrics, real carbon emissions or empirically verified POI mappings are provided by this experiment.

This is a next-step solver and audit demonstration. Check the GitHub workflow's final status before claiming execution success.

See [network provenance](WESTERN_SYNTHETIC_NETWORK_PROVENANCE.md).
