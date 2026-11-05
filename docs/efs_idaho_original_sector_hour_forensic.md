# Idaho original EFS Sector/Subsector source-level audit — independent checkpoint

## Scientific question

The EFS2020 `Reference_Moderate` and later ReEDS2022 `EFS_REFERENCE` state-hour records have nearly identical state annual demand, but Idaho shows substantial persistent residual error after the best nonwrapping −2-hour source-index shift (approximately 17.3/19.3/22.1 MW MAE in 2030/2040/2050). The remaining hourly discrepancies are systematically distributed through months and hours, unlike AZ and CA controls.

Do differences originate from **one or more identifiable original EFS source sector profiles**? Can an elementary sector-specific source-index perturbation predict the held-out discrepancy? This is a *mechanism falsification exercise*, not a timezone-assignment model.

## New empirical work

- Re-download the actual original NLR `EFSLoadProfile_Reference_Moderate.zip` and extract its original CSV with all `Sector` and `Subsector` source columns.
- Stream `Year,State,LocalHourID,Sector,Subsector,LoadMW` and strictly select original `Reference` electrification, `Moderate` technology and Idaho, years 2030, 2040, 2050.
- Reconstruct each original EFS `Sector × Year × LocalHourID` profile and require **every one of the 8760 original hours for every source sector and year**; fail if source coverage is incomplete.
- Independently reconcile the full sum of source sectors at every hour with the original previously verified state-hour CSV in run `41262154939`. A missing sector or inconsistent numbers must trigger hard failure, not an approximate substitution.
- Compare against official MD5-verified ReEDS2022 HDF5 Idaho series under the previously independently determined −2-hour shift, excluding cross-year boundary rows.
- Exploratory **predefined** whole-sector ±1-hour source-index shifts (or zero shift): use first approximately half-year to choose the lowest-MAE combination; report actual second-half **held-out** MAE and improvement versus unchanged EFS sectors. This prevents purely in-sample claims while still remaining a descriptive, nonphysical hypothesis.
- Retain original EFS 2020 source sha256, HDF5 publisher MD5, scenario/version distinction, and fail-closed `source_clock_corrected_or_synchronized=false` and `physical_timezone_sector_membership_identified=false`.

## Files and execution

- `src/energy_transition/efs_idaho_raw_sector_source_forensic.py`
- `tests/test_efs_idaho_raw_sector_source_forensic.py`
- [GitHub Actions: Idaho source-sector forensic](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-idaho-raw-sector-forensic.yml)
- Expected outputs: `idaho_raw_sector_shift_holdout.csv`, `idaho_source_sector_provenance.json`.

**Acceptance status:** the CI must pass with actual upstream CSV and source MWh conservation before reporting any sector-specific findings. No substate utility/timezone identifiers or actual 2020 EFS `LocalHourID` meaning has been verified.

## Manuscript implications

If some sector-specific candidate shifts predict held-out discrepancies better, present this as a **structured source transformation hypothesis**. It cannot prove that those sectors are geographically in a particular timezone or that this transformation generated the later ReEDS HDF5. If none improve, that falsifies only the restricted tested class of whole-sector ±1-hour adjustments. Existing 540 annual source-load + synthetic-renewable cyclic LP study is unchanged.

## Actual verified original-source outcomes (2026-11-05)

[Source-backed run #42128806803](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42128806803) passed. The official EFS ZIP uses Deflate64 (system unzip, as in pinned PyPSA-USA), and original Idaho selection yielded **367,920 rows**. Its four sector profiles (Commercial, Industrial, Residential, Transportation) exactly reconstruct the independent original state-hour archive over **3 × 8,760 hours**. Original source SHA-256: `75b6cf99cc04a2b98bd69f7874809a396f256d57ae7f10d36f3e945fb0235eea`.

The 81 predefined {-1,0,+1} whole-sector index-shift configurations **include the unchanged reference**. Selection was trained only on the first approximate half of each source year; the remaining half was held out.

| Year | Idaho original annual source load (TWh) | Baseline training MAE (MW) | Training-selected shifts C/I/R/T | Selected training MAE (MW) | Held-out baseline MAE (MW) | Held-out selected MAE (MW) |
|---|---:|---:|---|---:|---:|---:|
| 2030 | 27.989 | 16.720 | 0/0/0/**+1** | 16.648 | 17.796 | **15.586** |
| 2040 | 31.294 | 18.692 | **0/0/0/0** | 18.692 | 19.903 | 19.903 |
| 2050 | 35.834 | 21.398 | **0/0/0/0** | 21.398 | 22.786 | 22.786 |

The 2030 Transportation-only +1h candidate shows **2.210 MW held-out improvement**, but 2040/2050 **select no shift**. This limited test does not support a stable sector-wide clock shift as the explanation for Idaho. The source does not identify sector-specific physical time zones; the candidate shifts are statistical transformations only. The source-clock and Idaho anomaly remain unresolved. The 540 battery LPs stay synthetic-supply studies, not physical Western-grid dispatch.
