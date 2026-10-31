# Pinned PyPSA-USA Western build source — empirical admission checkpoint

This document **pins a reproducible upstream code release**, not a completed
Western empirical model or extracted geographic weights.

## Upstream inputs (verified 2026-10-31)

- Upstream repository: https://github.com/PyPSA/pypsa-usa
- Tag: `v0.8.0`
- Tag commit SHA: `338af9912addbaf038c6098fe27e1e6ef099d8aa`
- Official example configuration:
  https://github.com/PyPSA/pypsa-usa/blob/338af9912addbaf038c6098fe27e1e6ef099d8aa/workflow/repo_data/config/config.default.yaml
- Published data record, v17:
  https://zenodo.org/records/14611937
  (raw data archives, **not** a verified built network file)
- For reproducibility, record the exact checksum of each downloaded data file
  and the resulting network NetCDF; record the actual config and code revisions.

## Practical reproducible build route

```bash
git clone https://github.com/PyPSA/pypsa-usa.git
cd pypsa-usa
git checkout 338af9912addbaf038c6098fe27e1e6ef099d8aa
bash init_pypsa_usa.sh
cd workflow
uv run snakemake -j1 --configfile config/config.default.yaml
```

The upstream default config describes `interconnect: [western]`,
`transmission_network: 'reeds'`, `topological_boundaries: 'reeds_zone'`,
and planning horizons 2030/2040/2050 on the repository master branch.
**Verify** all these values against the pinned v0.8.0 config before running;
do not silently substitute master's settings. The full default workflow may
require much more compute, disk, external weather inputs, credentials and
runtime than this repository's GitHub CI affords. Avoid adding it to CI.

After a real upstream network is built, inspect `network.buses.columns`
and the data values, especially `reeds_state`, `reeds_zone`, `LAF_state`.
Their availability is a tested requirement, not a presumption. Pin its
build configuration including geography and load allocation choices.

Use the existing extraction command:

```bash
python -m energy_transition.pypsa_usa_laf_weights \
  --network /path/to/actual-built-network.nc \
  --mapping /path/to/official-western-membership-audit.json \
  --out /path/to/weights.csv
```

The input must be a genuine **built PyPSA-USA network** retaining geographic
load fractions. A successful extraction only verifies numerical conservation
and schema. Independently review the geographic provenance manifest before
enabling publication-grade demand allocation.

## Empirical readiness

- Upstream code tag SHA: **pinned**.
- Upstream data archive: **located, not downloaded or checksum-confirmed**.
- Actual upstream Western network: **not yet produced in Project B**.
- Derived actual `LAF_state` weights: **not yet produced**.
- Multi-year Western network dispatch: **not yet computed**.
