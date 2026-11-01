# Real Western network acquisition checkpoint

The pinned PyPSA-USA v0.8.0 preflight workflow succeeds, but **it does not
produce a built network NetCDF**. The next dependency is a genuine built
network from an actual upstream run, not another synthetic PyPSA fixture.

## Concrete upstream Snakemake build target (verified in pinned source)

The pinned PyPSA-USA `workflow/Snakefile` defines `rule data_model`
whose input is `resources/{run-name}/{interconnect}/elec_s{simpl}_c{clusters}_ec_l{ll}_{opts}_{sector}.nc`
(with the exact prefix and wildcards resolved by the effective configuration).
By contrast, `rule all` enumerates downstream plots. For a network artifact,
target **`data_model`**, not a broad default `all`.

From the checked-out upstream `workflow/` directory after
`init_pypsa_usa.sh`:

```bash
# Preview the exact DAG without downloading source data.
uv run snakemake -n -j1 --configfile config/config.default.yaml data_model

# Execute only after reviewing required inputs and compute/disk demand.
uv run snakemake -j1 --configfile config/config.default.yaml data_model
```

In this pinned version, the default scenario specifies `western`,
`reeds`, 2030/2040/2050 EFS reference/moderate years. The rule's
`elec_*.nc` output is **a model network candidate**. Inspect its buses
and the `LAF_state` column before treating it as a valid real-data
source. The network file need not be published in Git (large upstream data
and license conditions apply).

**This target has been identified from the official pinned Snakefile,
not executed to completion in Project B.** No built network files or derived
real weights are claimed.

## Required evidence for first empirical import

- Exact upstream Git revision `338af9912addbaf038c6098fe27e1e6ef099d8aa`
- Effective merged upstream configuration and SHA-256 checksums
- Full Snakemake command and actual completed rule/target, with logs
- The resulting network NetCDF file, its SHA-256, bus metadata and time snapshots
- Documentation of `LAF_state` construction methodology and geographic scope
- Official Western ReEDS membership and auditable source of EFS hourly data

## Execute once the actual network is available

```bash
python -m energy_transition.pypsa_usa_built_network_intake \
  --network /path/to/built-network.nc \
  --membership /path/to/official-membership.csv \
  --report outputs/western_network_intake.json

python -m energy_transition.pypsa_usa_real_laf_intake \
  --network /path/to/built-network.nc \
  --membership /path/to/official-membership.csv \
  --mapping /path/to/reconciled-state-zone-mapping.json \
  --out outputs/real_laf_candidate
```

Do **not** submit unverified LAF shares into a historical or future dispatch
calibration pipeline. These CLI reports are candidate admission evidence only.

## Honest project status

| Milestone | Status |
|---|---|
| Upstream pinned-revision/config/CI preflight | PASS |
| Upstream built Western network artifact | NOT YET ACQUIRED |
| Actual Western state-to-zone LAF extraction | NOT YET RUN |
| Verified EFS hourly future demand across 2030/2040/2050 | NOT YET IMPORTED |
| Empirical future dispatch and sensitivity solves | NOT YET RUN |

Project A's authentic LUT workbook extracts global annual electricity
energy-service demand; no dataset from A substitutes for these empirical
Western EFS inputs.
