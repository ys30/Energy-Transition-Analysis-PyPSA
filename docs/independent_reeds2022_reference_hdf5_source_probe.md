# Project B: separately sourced ReEDS 2022 reference HDF5 chronology and load provenance

## Exact published source

[NLR/ReEDS: Electricity demand profiles 2022, Zenodo record 18461543](https://zenodo.org/records/18461543), published 2026-02-04, DOI `10.5281/zenodo.18461543`. The original official download `demand_EFS_REFERENCE.h5` has the publisher's MD5 **7b2055d43200744a16a8c4fed68b1a17**.

The publisher states the demand product is **gross end-use load in MWh/h, hour-ending**, using a **2012 weather/calendar year** and **US Central Standard Time UTC-06:00**. The year contains exactly 8,760 hours by **dropping 2012-12-31**. Unlike the 2020 zipped EFS `Reference_Moderate` series, this *later 2022 ReEDS release* includes a native HDF5 datetime index.

**Crucial separation:** No one has certified that the original 2020 EFS `LocalHourID` is numerically identical to the 2022 ReEDS HDF5 datetime index or exactly the same published demand vintage. The source scenario labels `EFS_REFERENCE` versus `Reference_Moderate` do not establish data equality. Use this HDF5 as an *independent, explicit-clock comparison branch*, not an unreviewed replacement for Project B's already accepted 2020 EFS-LAF data.

## Newly implemented source-verification workflow

- [Workflow: independent official ReEDS 2022 EFS reference HDF5 source inspection](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/reeds2022-reference-hdf5-source.yml).
- `src/energy_transition/reeds2022_reference_hdf5_provenance.py`: actual downloaded HDF5 MD5 check (publisher exact value); HDF5 datetime datasets; native 8,760 unique index checks; original 11 Western-state profiles for the three model years 2030, 2040 and 2050, 33 state-year demand sums and peak values.
- Artifacts: `reeds2022_reference_2030_2040_2050_state_summary.csv`, `reeds2022_reference_source_time_metadata.json`. The HDF5 datetime first/last records are saved for independent chronology scrutiny.
- No synthetic data are substituted for the publisher's HDF5. The workflow fails on missing source file, wrong checksum, missing years/Western-state series or invalid numeric units.

**Actual publisher-file source validation passed:** [CI #42117508479](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42117508479) downloaded and MD5-verified the **official 43.2-MB HDF5**, read all 33 state-year profiles and native datetime arrays. For 2030, 2040 and 2050 the HDF5's datetime strings start **2012-01-01 00:00:00-06:00**, end **2012-12-30 23:00:00-06:00**, and contain **8,760 unique time keys** per model year. The source HDF5 is separate from EFS2020. A subsequent stricter follow-up CI also tests **the exact 2012 CST sequence, Feb 29 inclusion and Dec 31 exclusion**, rather than accepting merely 8,760 unique rows. Even with source validation, original EFS2020 weather-hour alignment, generator-to-bus POIs, future wind/solar resource capacity factors and Western OPF remain *blocked*.

## Independent native HDF5 evidence (actual official 2022 source)

| Example state/model year | Signed/source annual state demand | Native hourly source peak |
|---|---:|---:|
| California, 2030 | 284.614329 TWh | 56,878 MW |
| Arizona, 2030 | 89.415913 TWh | 19,405 MW |
| Colorado, 2030 | 64.966091 TWh | 11,454 MW |

These numbers are *independent 2022 ReEDS release model results* and **must not be merged with or advertised as numerically equivalent to the 2020 EFS Reference/Moderate dataset**. The native time index carries a real fixed `-06:00` offset; the authoritative publisher's hour-ending claim is metadata, not a license to introduce an undocumented one-hour relabeling of the original source.

## Next empirical research step

After this source audit, a legitimate *new input branch* could use the explicitly clocked ReEDS2022 published load profile to study independent wind/solar 2012 resource time alignment. First verify the HDF5 actual hour-ending stamp vs resource API interval stamp, the December 31 omission, and hour-by-hour geographical/CST↔UTC conversion, then quantify annual energy differences from the original EFS2020 source rather than presuming equality. Such a new branch must remain distinguishable in all results and manuscript tables.
