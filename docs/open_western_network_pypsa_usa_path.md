# Project B: open western-US network implementation pathway (2026-10-31)

## Decision: prioritize an open planning-network solve

Rather than continuing to add ADS ZIP preflight utilities without the actual WECC ADS archive, test a reproducible **PyPSA-USA western-interconnection planning network** first. This is a distinct, source-labelled planning-network case, not a 2024 physical operating snapshot and not a replacement for the EIA-930 interchange accounting audits.

### Upstream, independently maintained sources

- [PyPSA-USA model and code](https://github.com/PyPSA/pypsa-usa) (MIT licensed), with configurable U.S./western-interconnection build and solve pipeline.
- [Transmission documentation](https://pypsa-usa.readthedocs.io/en/latest/data-transmission.html), which distinguishes ReEDS/NARIS-derived zonal transfer limits from Texas A&M synthetic nodal networks. Zonal interface capacities **are not AC line impedances**.
- [Model component documentation](https://pypsa-usa.readthedocs.io/en/latest/model-components.html) distinguishes raw nodal and clustered resolutions; keep aggregation metadata.
- [Public bundled data collection](https://zenodo.org/records/14611937) provides `pypsa_usa_data.zip` (~567 MB) and other supporting data. Download and content verification not yet performed here.
- [Default configuration](https://github.com/PyPSA/pypsa-usa/blob/master/workflow/repo_data/config/config.default.yaml) shows `scenario.interconnect: [western]`, `model_topology.transmission_network: 'reeds'`, planning horizons 2030/2040/2050, and 2019 historical weather snapshot defaults. **Those example years should not be represented as our 2024 observed input.**

### Implementation milestones

1. Obtain versioned public PyPSA-USA source and data files; preserve their actual published license, hashes, source dates and upstream revision.
2. Run a minimal **western** regional configuration and export an independently inspectable network `.nc`/bus/line/link data with generation/load mapping. Use upstream setup documentation and actual on-disk schema, not guesses.
3. Validate hourly snapshot chronology and network accounting independently of existing CISO/BPAT EIA-930 pilots; verify regional mappings and whether transmission constraints are zonal `Link` interfaces versus actual AC `Line` objects.
4. Solve and publish a reproducible planning-network baseline and sensitivity. Explain that topology and ratings are from an upstream planning dataset, and report congestion, unserved load, energy balance and solver outputs.
5. Only after credible historical topology and operational BA mapping are available, attempt 2024 observed physical calibration. Do not backdate NARIS-derived interface capacities or claim EIA-930 TI is a rated line.

### Parallel original WECC path

WECC 2034/2036 ADS remains a candidate planning dataset. The [WECC ADS selection record](wecc_ads_2026_source_selection_and_ingestion.md) documents the access and case-year barriers. There is no authorized local WECC ADS physical bus/branch archive in this repository.

### Current validation state

**Source path identified; public data package and actual western solver case have not been downloaded, executed, or validated in this project.** This decision document is an implementation handoff, not a solver achievement.

## Verified archive contents (GitHub Actions 41225182337)

The published `pypsa_usa_data.zip` was downloaded (567,382,729 bytes), publisher MD5 verified, and inventoried successfully. The archive contains **22 files**, primarily land cover, terrain, county/EEZ boundaries and pumped-storage siting inputs. **It does not contain a ready-to-solve bus/branch network** (`candidate_model_files=[]`). A 1.92 GB uncompressed Copernicus GeoTIFF explains why the original 1 GB-per-member preflight limit failed. Receipt and inventory are retained as workflow artifact `13051518237`.

**Next input required:** obtain the versioned PyPSA-USA transmission build inputs (ReEDS/NARIS zonal interfaces or Texas A&M synthetic nodal source) or an independently reproducible exported `.nc` network; validate buses, branches/links, capacities, chronology and license before solving. Do not present this geospatial support-data archive as a physical transmission case.
