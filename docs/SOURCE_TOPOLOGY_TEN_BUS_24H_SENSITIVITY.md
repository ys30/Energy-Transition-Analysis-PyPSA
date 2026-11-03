# Synthetic 10-bus 24-hour capacity × solar sensitivity study

## Scientific status

**Hypothetical scenario study only.** The 10-bus tree topology, original line IDs, source nominal voltage, and line r/x are selected from a pinned PyPSA-USA Breakthrough Energy **synthetic** Western source. Loads, time profiles, solar installed MW, generator costs and all branch ratings are explicitly assumed. No physical Palo Verde facility connection, historical Western dispatch, 2030/2040/2050 projection or full-Western OPF has been calibrated or run.

## Reproduction

Run:
```bash
python -m energy_transition.source_topology_ten_bus_24h_sensitivity \
  --network /path/to/western-base-network.nc \
  --anchor 2040841 \
  --out outputs/ten_bus_24h_sensitivity.json
```

Workflow: [source-topology-ten-bus-24h-sensitivity.yml](../.github/workflows/source-topology-ten-bus-24h-sensitivity.yml).

Experiment: 10 nodes, nine original source-model line records, 24 one-hour *synthetic* hourly snapshots, three common hypothetical branch ratings (45, 75 and 120 MW), two hypothetical solar nameplates (75 and 200 MW) and 6 solves. Each leaf has a profile-scaled assumed load; a 20-unit/MWh generator is placed at the anchor, 0-cost solar at one leaf and 100-unit/MWh backups at receiving buses.

The solver audits all 24 × 6 hourly states for (1) aggregate power balance; (2) each node's signed incident Line `p0/p1` balance; (3) flow capacity; (4) solar availability; and (5) summed variable-cost objective. It checks optimal cost does not increase as synthetic network capacity or solar availability increase.

Reported outcome fields include total synthetic objective (non-currency), local backup MWh, renewable production MWh, solar curtailment MWh, line–hour congestion counts, and maximum nodal power residual. These should be read from the **successful CI artifact**, not inferred from scenario parameters.

## Interpretation

This is an optimization, numerical integrity and reproducibility exercise using **synthetic source topology and operational assumptions**. Optimization sensitivity can support a bounded engineering demonstration but does **not** demonstrate real-world grid economics, resilience or public-policy impacts.

See [synthetic network provenance](WESTERN_SYNTHETIC_NETWORK_PROVENANCE.md).
