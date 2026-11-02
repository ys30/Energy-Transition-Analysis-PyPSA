# Plant 59047 — persistent PUDL T&D owner gap; planned-project status needs vintage reconciliation

## CI-verified finding
- [PUDL 2023/2024 extraction run 41405753838](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41405753838): plant ID **59047** is the sole reviewed plant without both T&D owner ID and name in 2023 and 2024, within each year’s 84-plant review subset.
- [Cross-year missingness audit 41405975842](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41405975842): persistent ID 59047; no exclusively 2023 or 2024 missing-owner IDs.
- PUDL join and geospatial proximity are evidence only: **zero** independently verified plant-to-source-PyPSA-bus links.

## External cross-check and caveats
- EIA plant code 59047 is **Gallegos Wind Farm, Phase 1**, Union County, New Mexico, operator Gallegos Wind Farm LLC. The October 2026-released EIA Electric Power Monthly table 6.5 identifies it as a **planned** wind unit, generator `GEN 1`, 190 MW nameplate, with 2028 planned installation. Source: https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_6_05 (published 2026-10-23; source may roll forward).
- Secondary EIA-860M-derived source: https://www.interconnection.fyi/eia/plant/59047 describes the same plant as planned and not operational, with proposed completion November 2028. A prospective completion date is **not** proof of future commissioning.
- **Important temporal distinction:** current 2026 planned status does **not** retroactively establish the EIA-860 2023/2024 generator reporting status, nor explain the missing T&D owner causally. Check original 2023/2024 EIA-860 generator inventory and status codes before analyzing this ID’s eligibility in historic supply.
- Neither source verifies a substation, point of interconnection, voltage, source PyPSA bus ID, or physical connection. Do not promote this plant from geographic candidate to a generator component.

## Follow-up evidence required
1. Read original EIA-860 2023 and 2024 plant and generator reporting status for plant 59047; preserve release year and exact status code.
2. Look for a dated utility/ISO interconnection agreement or officially reported point of interconnection, with facility name and voltage.
3. If a POI is independently verified, establish and document its linkage to a **specific** original-network bus; absent this retain `electrical_connection_verified=false`.
4. Ensure planned units are never automatically interpreted as operating supply in 2023–2024 or in 2030/2040/2050 scenarios.

## Evidence tier

G0 geographic candidate, G1 owner incomplete (for both reviewed historical years); G2 POI **not found**; G3 source-network bus **not verified**. Generator dispatch admission: **blocked**.
