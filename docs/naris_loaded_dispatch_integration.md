# NARIS zonal loads → constrained OPF integration

The `naris2024_loaded_dispatch_integration` module connects an exported
load-bearing PyPSA zonal network to the HiGHS solver while **holding the
generation fleet explicitly hypothetical**.

## Inputs and gates

1. A NetCDF network created by `naris2024_audited_load_ingest`, containing
   directional NARIS `Link` interfaces and hourly `Load` profiles.
2. The JSON report from the corresponding load-ingestion operation. In
   non-fixture mode, provenance-required, official Western membership and
   NetCDF round-trip evidence flags must all be true. Those flags are
   **not external provenance authentication**; the upstream evidence and
   source files must still be independently audited.
3. Link assumptions are strict: efficiency 1, forward-only capacity,
   no preexisting generation/storage; this demonstration rejects rather
   than silently relaxes other data.

Run an admitted case:

```bash
python -m energy_transition.naris2024_loaded_dispatch_integration \
  --network outputs/admitted_zonal_load_network.nc \
  --load-report outputs/admitted_zonal_load_report.json \
  --report outputs/loaded_zonal_dispatch_smoke.json
```

For *unit tests only*, `--synthetic-fixture` permits a small artificial
load case without production source-admission flags. **Never use this
flag to label results empirical.**

## What the report establishes

- Every admitted snapshot participates in a linear optimization.
- Input MWh matches the load-ingestion report, and optimized generation
  conserves aggregate MWh, subject to stated numerical tolerances.
- Every bus satisfies the directional-link nodal balance equations.
- Transfer flows obey the retained source Link capacities.
- A hypothetical cheap central supply competes with hypothetical local
  backup generation.

## What the report does not establish

No EIA-860 plant-to-bus mapping, authentic generating fleet, published
marginal operating cost, historical dispatch, WECC physical branch
reactance or validated nodal price is inferred. The optimization cost
is **arbitrary model units**, not USD, and the result is not a historical
energy-transition impact estimate.

Next research gates: independently validate the empirical load weight
crosswalk and calendar; admit a documented actual generator fleet;
assess interchange and regional energy balances; then evaluate
network-wide multi-period scenarios with explicitly separated empirical
and assumed inputs.
