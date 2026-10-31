# PyPSA-USA LAF source acquisition — Project B

## Verified source pathway (not an empirical result)

PyPSA-USA documents `LAF_state` as the bus load fraction within its state,
with `reeds_zone` and `reeds_state` denoting REeDS geography:
https://pypsa-usa.readthedocs.io/en/latest/model-network-schema.html

Upstream default settings distinguish `demand.profile: efs` (state-level
future demand) and `demand.bus_allocation` (`population` or
`breakthrough`):
https://pypsa-usa.readthedocs.io/en/stable/config-configuration.html

**Do not confuse an input dataset zip with a built PyPSA network.**
The upstream dataset record at
https://zenodo.org/records/14611937
provides raw bundles, not proof that this project's required built bus
inventory or `LAF_state` columns exist. In particular, the documented schema
notes that offshore buses may have null LAF and that grouping/aggregation
pipelines need care. A pinned model run and its build configuration are needed.

## Reproducible admission procedure

1. Pin PyPSA-USA git revision or released version, model settings, grid vintage,
   demand allocation policy, and raw bundle record/checksums.
2. Reproduce its **built** Western network upstream, retaining bus columns
   `reeds_state,reeds_zone,LAF_state` before any aggregation that might
   overwrite LAF. Confirm the chosen LAF was constructed for the intended
   model vintage and allocation policy.
3. Compare REeDS official Western membership with the built network; disclose
   missing/offshore buses and do not infer zeros or invent transmission links.
4. Run `python -m energy_transition.pypsa_usa_laf_weights
   --network <pinned-built-network.nc> --mapping <membership-audit.json>
   --out <weights.csv>`. This step accepts only complete finite,
   nonnegative, state-conserving zonal shares.
5. Independently review the source revision, underlying geographic derivation
   and build chain, and then provide an evidence manifest for
   `efs_geographic_provenance_gate`. Its metadata/checksum checks alone do
   **not** validate geographic methodology.

Until steps 1–5 are verified on real files, do not label extracted weights
as empirical, calibrated or accepted for publication.

## Current status (2026-10-31)

- Upstream `LAF_state` field definition: **verified from public documentation**.
- Upstream versioned archive record: **identified**, not downloaded/built here.
- Actual Western network `LAF_state` extraction: **not yet performed**.
- Source-backed yearly/multiyear Western dispatch: **not yet completed**.
