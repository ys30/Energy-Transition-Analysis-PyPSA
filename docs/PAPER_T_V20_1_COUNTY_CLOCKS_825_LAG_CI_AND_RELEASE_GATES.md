# Paper T v20.1 — Idaho county clocks, ReEDS2022 lineage, and verified v4 / 825-point CI (2026-11-11)

## Verified county-level geography
Official `NatLabRockies/ReEDS-2.0` main-branch `inputs/temporal/reeds_region_tz_map.csv` assigns PT to all seven historical p14 northern Idaho counties: Benewah (16009), Bonner (16017), Boundary (16021), Kootenai (16055), Latah (16057), Lewis (16061), and Nez Perce (16069). The other 37 Idaho counties map MT. The four Oregon counties in legacy p7—Baker, Harney, Lake and Malheur—are assigned PT in the newer county map, although legacy BA p7 is labeled UTC−7 / Mountain in `legacy_ba_timezone.csv`. **BA labels cannot be substituted for actual county physical time without version-appropriate provenance.**

## Release-generation lineage — UNVERIFIED
Current ReEDS `hourlize/inputs/configs/config_base.json` selects a **2025 EER** source (`20250512_eer_download`); `hourlize/inputs/load/sector_config.json` contains a **conditional local-time legacy-BA** setting for the Transportation replacement sector. These are **not** the authenticated configuration that built the publisher's `demand_EFS_REFERENCE.h5`. No release-matched p14/p15/p16 hourly demand or county allocation weights have been recovered. Hence p14's real load fraction is unknown and **cannot** be compared legitimately with the fitted 0.165575 coefficient. Count ratio 7/44 = 15.91% is not a load share.

## CI results
- **v4 synthetic-only source code**: [successful GitHub Actions run #43052039916](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43052039916), 300 cases and 75 PV-scale groups, 29/75 groups with scale-sensitive absolute peak, 37/75 groups with scale-sensitive peak shift. 10 regression tests pass. No EFS/ReEDS physical-hour join.
- **Complete 25-lag original source**: [successful GitHub Actions run #43052221098](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43052221098), 825 exact -12..12 source-derived MAEs across 33 state-years. Data from EFS source run #41262154939 and publisher MD5-verified `demand_EFS_REFERENCE.h5`. **33/33** best, runner-up and zero-lag results match frozen T_S1. Not a physical-hour crosswalk.
- New Fig. S6 is generated locally from this actual 825-point CSV (plot and source data provided privately to author).

## Release and manuscript statements
- Publisher dataset DOI **already exists**: EFS2020 `10.7799/1593122`, ReEDS2022 `10.5281/zenodo.18461543`. Neither is the author's code DOI.
- The upstream ReEDS source code is BSD-3-Clause (official `LICENSE`). The author's own repository has no verified top-level `LICENSE` and no issued analysis-specific DOI. Do not invent one or apply an external project license.
- Source-CI used Python 3.11, and bounded `numpy>=1.24,<3`, `pandas>=2,<3`, `h5py>=3.10` and `pytest>=8`; v4 CI pins NumPy 1.26.4. These are the **CI installation constraints**, not a comprehensive dependency lock.
- Funding and conflicts require factual author signoff. AI assistance with code/source review/drafting can be disclosed honestly. Paper remains private, unreleased, and under author review.
- Physical-hour screening remains **BLOCK_PHYSICAL_JOIN**; G5 remains blocked.

## Paths
- `hourlize/inputs/load/legacy_ba_timezone.csv`
- `hourlize/inputs/load/legacy_ba_state_map.csv`
- `inputs/county2zone.csv`
- `inputs/temporal/reeds_region_tz_map.csv`
- `hourlize/inputs/load/sector_config.json`
- `hourlize/inputs/configs/config_base.json`

Current main-branch source files are documentary mechanism clues, not authenticated 2022 dataset generation instructions. A publisher-released manifest/config and historical per-BA demand must be obtained before asserting a measured Idaho Pacific share or releasing G5.
