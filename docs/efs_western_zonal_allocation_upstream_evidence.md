# EFS state-demand to Western ReEDS zonal allocation: upstream evidence

Verified 2026-10-31. Upstream: https://github.com/PyPSA/pypsa-usa/blob/master/workflow/scripts/build_demand.py

## What is proven

- NARIS2024 Western ReEDS membership has 35 regions. Current published positive-capacity AC interface network has 34; the additional p19 bus is retained only as an isolated membership placeholder.
- NARIS2024 published BA AC and non-AC interface input tables contain no p19 endpoint. Absence in these model tables does **not** show real-world Montana is physically isolated.
- Upstream PyPSA-USA `build_demand.py` documents EFS demand as state-based and includes demand allocation with geographic census/population inputs, not equal distribution by zone.
- `membership.csv` provides region-to-state categorical membership, **not** empirical allocation factors. The new `efs_zonal_weight_admission.py` intentionally refuses guessed weights.
- Upstream EFS state profiles require timezone/daylight/calendar checks; documented upstream EFS load files are not leap-year complete.

## Required actual implementation

1. Reproduce or reuse upstream bus/county allocation factors (LAF), including census population source, geometry intersections and source revisions, rather than assigning 1 / number of zones.
2. Aggregate normalized location factors to ReEDS state-to-zone weights. Store reproducible input hashes and per-state weight sums. For a state spanning partially outside Western Interconnection, explicitly account for excluded footprints.
3. Use validated state-by-zone weights to allocate EFS 2030, 2040, 2050 state demand, verifying per-state and per-hour demand mass conservation.
4. Keep p19 in the allocation accounting and **do not silently drop demand** or invent a connection; an isolated positive-load zone requires local supply or an explicitly documented external source.
5. Freeze planning-year network / load scenario semantics separately from historical EIA-930 observations.

## Gate

**Not yet data-ready:** no verified state-to-zone numerical weights or empirical hourly regional loads have been admitted. Existing full-Western dispatch results are synthetic stress tests. This note is a source and scope audit, not a claim of actual EFS integration.


## Provenance gate implementation (2026-10-31)

The source metadata check is implemented in `energy_transition.efs_geographic_provenance_gate`.
It verifies externally supplied weights against a SHA-256 digest and requires:
`weights_sha256`, `source_url`, `source_revision`, `geographic_method`,
`geography_vintage`, `population_vintage`, `processing_script_sha256`, and
`coverage_note`.

Example CLI after obtaining **actual** externally computed and reviewed files:

```bash
python -m energy_transition.efs_geographic_provenance_gate \\
  --mapping input/reeds_state_membership.json \\
  --weights input/efs_state_reeds_weights.csv \\
  --manifest input/efs_weights_provenance.json \\
  --report outputs/efs_geographic_evidence_gate.json
```

The validator does not download or calculate weights; an arbitrary URL or fabricated
metadata can still pass format checks. A green unit test **does not** establish
empirical validity, accurate state boundaries, independent reproduction, a correct
crosswalk, or a calibrated PyPSA Western network. Independent review of the
upstream geographic calculation and archived raw source assets remains mandatory.
