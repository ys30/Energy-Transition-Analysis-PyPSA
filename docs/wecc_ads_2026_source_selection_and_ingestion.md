# WECC ADS source selection and next physical-case ingestion gate (2026-10-31)

## Source discovery: verified official destinations

- [WECC Anchor Data Set (ADS) official page](https://www.wecc.org/program-areas/reliability-planning-performance-analysis/reliability-modeling/anchor-data-set-ads) — primary source. Its public listings include **2036 ADS PCM** and **2034 ADS PCM V3.1/V3.2** deliverables. ADS represents a **planning horizon** and can contain production cost and power flow variants. A listed download is not evidence that an independently readable archive, physical line ratings, bus topology, or historical 2024 power-flow case was obtained.
- [WestTEC resources](https://www.westernpowerpool.org/pages/westtec-resources/) — separately states that WECC 2034 ADS *base-case model* access can require contacting WECC support, specifying base-case permissions, and completing forms.
- [WECC 2025 Data Preparation Manual](https://www.wecc.org/sites/default/files/documents/meeting/2025/2025%20Data%20Preparation%20Manual-1.pdf) — bus numbering and ADS owners are described; these are **not** CISO/BPAT bus-to-BA topology mappings.

## Scientific decision

**Do not represent the public 2034/2036 ADS planning data as observed 2024 western US grid infrastructure.** The EIA-930 D/NG/TI series measures balancing-authority aggregates, not rated physical AC branches. A public GIS route or a calculated net interchange is not a substitute for electrical impedance or line ratings.

Two explicit pathways:

1. **Planning-case scenario (feasible after access):** obtain authorized public ADS archive and record its actual file format, SHA-256, vintage, license and assumptions. Inspect inventory with:
   `python -m energy_transition.wecc_ads_archive_inventory --archive /path/to/authorized-ads.zip --output outputs/wecc_ads_inventory.json`
   The tool lists member file types and hashes only; it deliberately **does not** claim physical parse success. Inspect actual schema (e.g., PCM/GridView database versus power-flow text) before implementing any parser.
2. **Historical calibration (blocked):** independently obtain a credible historical 2024 network case with electrical bus/branch topology, impedance, voltage, rated line flows/capacity, status and a contemporaneous geographic/BA assignment. Reconcile model generation/load accounting separately with EIA-930 and EIA-860/EIA-923. No validated 2024 physical case is in this repository.

## Electrical data contract when an eligible archive is available

Minimum fields at source-native **physical bus/branch** resolution: branch/circuit identifier, end bus IDs, terminal bus nominal voltage (kV), r and x (ohms or on a **documented** power/voltage base), continuous ratings with documented MVA versus MW semantics, statuses, case vintage, authoritative source reference and model license. Preserve parallel circuits and transformers (tap/phase shift) as distinct objects. Avoid deduplicating purely on BA pair; multiple real AC branches can connect the same areas. Aggregation to an illustrative two-BA equivalent requires a separately validated electrical reduction, not a simple sum of corridor ratings.

The existing `transmission_branch_case_audit` and `pypsa_line_evidence_adapter` screen only a toy **BA-level** line schema. They are **not** production converters for an ADS bus/branch archive. The enforced `base_mva` conversion check is necessary but cannot authenticate sources or prove a valid reduction.

## Current checkpoint and blocking input

- Verified synthetic two-bus AC Line congestion test: [numerical record](verified_synthetic_ac_line_sweep.md).
- Verified upstream line adapter tests: [GitHub CI #41222291957](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41222291957).
- **Not obtained:** an authorized WECC ADS bus/branch data file in a known importable format.
- **Not achieved:** physical multi-area network conversion or historical calibration.

The next non-synthetic implementation step is **real archive inspection**, then parser design against the observed file schema. No more generic branch-field claims should be interpreted as genuine data integration.
