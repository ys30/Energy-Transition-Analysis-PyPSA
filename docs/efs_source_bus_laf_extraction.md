# Candidate EFS load-allocation factors from PyPSA-USA source buses

The first real-data bottleneck for the Western NARIS model is geographic
state-to-ReEDS-zone allocation. [PyPSA-USA network schema](https://pypsa-usa.readthedocs.io/en/latest/model-network-schema.html)
documents `LAF_state` as the share of **full-state demand** carried by a
bus (`Pd / full-state Pd`) and `reeds_state`, `reeds_zone` as mapping
attributes. These may be available on a properly built, version-pinned
PyPSA-USA network; the standalone NARIS interface-only topology **does not
contain source bus-level LAFs**.

## Candidate extraction

Run on a **source bus network retaining all required columns**:

```bash
python -m energy_transition.efs_source_bus_laf_extraction \
  --network path/to/source-bus-network.nc \
  --weights outputs/candidate_efs_state_zone_weights.csv \
  --report outputs/candidate_efs_state_zone_laf_audit.json \\
  --membership-report outputs/naris2024_efs_state_mapping_audit.json
```

The script groups original `LAF_state` values by original
`reeds_state`/`reeds_zone` without ever renormalizing the Western
subset. It rejects duplicated bus identities, invalid/negative/non-finite
shares, conflicting state assignments and every state whose **raw
full-state** share fails to sum to one. A state only partially within
Western membership should therefore be **blocked**, not given a
fabricated redistribution of its external demand.

## Evidence tiers

1. A passing unit test proves only deterministic aggregation and
   rejection behavior using a synthetic test table.
2. A passing extraction on a **real** network establishes that its *reported
   source bus coefficients* are internally normalized; it does not establish
   source authority, geometry vintage, demographic representativeness or
   reliability of the state-to-zone demand model.
3. Empirical acceptance additionally requires provenance of the
   network/revision, original LAF inputs, actual full-state coverage,
   licensed source and independent reproduction/review, then a complete
   EFS time-axis and MWh reconciliation.
4. No invented links to `p19`. If upstream LAFs cover p19, its demand
   must remain accounted for and its generation/network-interface
   readiness handled separately.

**Status as of 2026-11-03:** extraction logic implemented; **no source
network with independently validated LAFs has yet been admitted**. This
does not change the empirically unready status of the 35-zone synthetic
OPF workflow.

## Western membership exact-match gate

The optional `--membership-report` parameter consumes the NARIS Western membership audit's `state_to_all_membership_zones` inventory (including `p19`). It fails if any source-network LAF zone is absent, extraneous, duplicated, or assigned to the wrong state. It does not invent missing weights or silently rescale partial state demand. Passing this check proves only candidate inventory compatibility, **not** independent LAF provenance, empirical calibration, or permission to publish energy-transition effect estimates.
