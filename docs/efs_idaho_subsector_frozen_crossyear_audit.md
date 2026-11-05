# Idaho original EFS Subsector provenance and frozen 2030 lag transfer

## Research question

The archived original EFS2020 state demand for Idaho was exactly reconstructed from four EFS sector categories, but a 2030-only Transportation +1 source-index candidate that modestly reduced held-out source-release hourly discrepancy was **not** selected when 2040 and 2050 were independently searched. To prevent re-selection from hiding cross-year failures, the present source-backed study **freezes that exact 2030 candidate** and evaluates it without any parameter search on both later planning years.

In parallel, the original raw NLR EFS ZIP does retain `Sector` and `Subsector` information. We now calculate original source annual MWh by both categories, cross-check against the previously accepted original Idaho state-hour archive and preserve the exact original source SHA-256. The subsector names and MWh shares identify source aggregation structure, **not geographical area or physical time zone**.

## Experimental protocol

1. Reacquire the authentic NLR original `EFSLoadProfile_Reference_Moderate.zip` using an official NLR URL and upstream-compatible system `unzip` for Deflate64. Verify the previously checked original source CSV SHA-256 `75b6cf99cc04a2b98bd69f7874809a396f256d57ae7f10d36f3e945fb0235eea`.
2. Filter `Electrification=Reference`, `TechnologyAdvancement=Moderate`, `State=ID`, planning years 2030/2040/2050, retaining every original `Sector/Subsector` label. Source rows with missing labels or nonfinite load are rejected.
3. Aggregate annual MWh for each original `Year × Sector × Subsector`. Require annual total energy equality against the independently archived 2020 EFS state-hour series in each year. Separately reconstruct complete 8760-hour `Year × Sector` traces to verify every original state-hour value.
4. Compare the archive with independent publisher-MD5-verified ReEDS2022 EFS_REFERENCE, excluding shifted cross-year boundaries. With the previously audited source index reference −2 h, fix **only** Transportation's +1-hour shift. Measure the last approximate half-year MAE against the unchanged four-sector baseline, without retuning the candidate in 2040 or 2050. Report signed MAE change, including negative values if the candidate worsens fit.
5. Explicitly reject the claims that a subsector's geography, original EFS source clock, physical Idaho time zones or future wind/solar resource joins have been established.

## Code and evidence

- `src/energy_transition/efs_idaho_subsector_crossyear.py`
- `tests/test_efs_idaho_subsector_crossyear.py`
- [GitHub Actions — Idaho EFS original subsector and frozen cross-year clock hypothesis](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-idaho-subsector-crossyear.yml)
- Artifact `idaho-efs-original-subsector-frozen-crossyear-evidence` containing:
  - `idaho_source_subsector_annual_energy.csv`
  - `idaho_frozen_2030_transport_shift_crossyear.csv`
  - `idaho_subsector_source_provenance.json`

**Scientific interpretation:** even a positive source-index fit on later years would only show a transferable mathematical rule on these two releases. It would not prove actual physical time-zone boundaries, causality of upstream data processing, or forecast-calibrated grid operation. A worsening later-year result would strengthen the evidence against a stable Transportation +1-hour explanation.

**Status:** CI source audit must pass before recording the numeric subsector population and cross-year transfer outcomes.
