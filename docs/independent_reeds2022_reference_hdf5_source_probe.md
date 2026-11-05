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

**Admission status:** source validation pending a successful actual workflow run. Even if the separate HDF5 source is verified, the existing original EFS2020 weather-hour alignment, generator-to-bus POIs, future wind/solar resource capacity factors and Western OPF remain *blocked*.

## Next empirical research step

After this source audit, a legitimate *new input branch* could use the explicitly clocked ReEDS2022 published load profile to study independent wind/solar 2012 resource time alignment. First verify the HDF5 actual hour-ending stamp vs resource API interval stamp, the December 31 omission, and hour-by-hour geographical/CST↔UTC conversion, then quantify annual energy differences from the original EFS2020 source rather than presuming equality. Such a new branch must remain distinguishable in all results and manuscript tables.
