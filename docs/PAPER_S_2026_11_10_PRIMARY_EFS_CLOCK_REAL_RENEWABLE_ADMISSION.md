# Paper S — Original EFS physical-clock authority and authentic renewable-capacity-factor admission audit (2026-11-10)

**Decision: BLOCK_PHYSICAL_WEATHER_JOIN.** Source-author-grade evidence for original 2020 `LocalHourID` → physical UTC **was not obtained**. Authentic matched 2012 solar and wind source bytes were **not ingested**. Accordingly **no physical-weather-joined Paper S LP rerun took place**; all prior Paper S values remain those of the synthetic Wave A/B model.

## Primary EFS source-author and upstream-method findings

- Original [Electrification Futures Study (EFS) Load Profiles, DOI 10.7799/1593122](https://data.nlr.gov/submissions/126) is a **2020** source release. Its catalog does not declare enough original `LocalHourID` detail to build a certified source-to-UTC one-to-one clock.
- [Sun et al. (2020), EFS Methodological Approaches, Appendix A pp.59–60](https://www.energy.gov/sites/default/files/2020/07/f77/EFS%20Methodology%20Report%202020.pdf) establishes that the Reference case uses the **ReEDS default load shape** and hourly EnergyPATHWAYS source material to disaggregate/adjust it by subsector and hour. This is concrete **load lineage** evidence; it **does not supply timezone, DST policy, start/end hour nor leap-year clock** for the published 2020 CSV.
- Later [ReEDS electricity demand profiles 2022, DOI 10.5281/zenodo.18461543](https://zenodo.org/records/18461543) expressly state the related **different release** uses a 2012 weather/calendar reference, **hour-ending CST UTC−06:00**, with 8760 hours after omitting December 31. Neither these publisher fields nor Paper T's fitted −2/−3 source-index offsets may be retrospectively assigned as the 2020 source clock.
- The current [Paper T strict six-evidence admission policy](PAPER_T_V9_FAIL_CLOSED_TIME_JOIN_METHOD.md) remains `BLOCK_PHYSICAL_JOIN`; the Idaho fitted timezone mixing does not create source-publisher authentication. Do **not** use adjacent release source-index matches to silently join real physical weather.
- The source-author question is prepared to the [verified ReEDS official contact](https://www.nlr.gov/analysis/reeds/), **ReEDS.Inquiries@nlr.gov**, but **not sent**. Ask for 2020 vintage specific LocalHourID convention, mapping code/version, leap/DST treatment, source date anchor and any signed one-to-one original-to-2012 source clock mapping.

## Authenticated 2012 physical-resource candidates identified, not downloaded

| Source | Exact version | Publisher clock | Data interpretation | Remaining obstacle |
|---|---|---|---|---|
| [ReEDS land-based wind v2](https://zenodo.org/records/18827074) | Zenodo 18827074 | **UTC instantaneous on hour**, 2012 included, drop Dec 31 for leap years | HDF5 hourly wind CF int data scaled by `cf_profile_2012` `scale` (typically 1e−4); site-scale | ~9 GB reference siting file and site-to-original-EFS-zone weights needed |
| [ReEDS utility PV v2](https://zenodo.org/records/18826700) | Zenodo 18826700 | **UTC instantaneous on hour**, 2012 included, drop Dec 31 | `MW_AC,grid/MW_DC,array`; inverter loading ratio **1.34** needed for normalized AC/nameplate CF; site-scale | spatial weighting and real publisher file checksums |
| [NASA POWER hourly API](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/) | Explicit 2012 request | `time-standard=UTC`, **hour-beginning** | Real modeled solar radiation and wind-speed meteorological inputs, **not already wind/PV CF** | site/weather-to-power assumptions and timestamp boundary crosswalk |

**Version drift warning:** [ReEDS wind v1](https://zenodo.org/records/18422200) instead describes **CST**, whereas **v2 uses UTC**. Original [ReEDS utility PV v1](https://zenodo.org/records/18407660) lists **CST** and BA/county resource classes while v2 has site-level UTC. Never combine different versions by row index or assume similar zone labels/units represent identical physics. Original EFS project P-zones are not automatically equivalent to a newer ReEDS county or site ID.

The [NLR WIND Toolkit API](https://developer.nlr.gov/docs/wind/wind-toolkit/wtk-download/) also supports 2012 UTC at 60-min resolution with `leap_day=false`, but requires authentic site selection, request credentials/contact, conversion to turbine CF and the same source clock admission. If hourly NASA POWER is used, its **hour-beginning** convention must not silently match a **hour-ending** demand or an instantaneous capacity factor.

## Source compliance

The [official original 2020 EFS dataset license](https://data.nlr.gov/node/126/license) allows no-fee use and copying subject to preservation of the complete license notice on dataset copies and DOE/NREL/Alliance publication credit. These rights do not determine third-party ReEDS source-derivative redistribution or code ownership.

## Locally tested fail-closed implementation

A private-source-research downloadable package contains:
- `source_weather_join_gate.py`, refusing unverified original-source clock passports and missing independent row-level source-to-UTC crosswalks, authentic 2012 weather capacity-factor input and publisher provenance, missing spatial source-zone allocation, duplicate/mismatched UTC keys, or 0–1 violations.
- Nine targeted unit tests **PASS** on synthetic control fixtures, including DST and hour-beginning/hour-ending mismatch rejection and correct support for either clock convention with an actual authority-backed crosswalk.
- `current_gate_decision.json` explicitly **BLOCK_PHYSICAL_WEATHER_JOIN**; no authentic source-weather numeric inputs were fabricated.
- `clock_weather_evidence_status.json`, a prepared but **unsent** author inquiry, README and SHA256 file manifest.

**Crucial distinction:** a software claim of an `independently_verified` Boolean is **not evidence** that the purported source author really verified it; manual source authority audit is a separate condition. The sample positive passport is **test-only**.

## What must happen before changing manuscript numeric results

1. Get source-specific author/publisher confirmation for **original EFS 2020**, not its ReEDS 2022 descendant, identifying the exact physical hour and calendar convention.
2. Pin actual source wind + solar publication **versions, file hashes**, source sites/zone crosswalk, AC vs DC units, averaging/instant convention, complete 2012 year, and rights.
3. Build and independently inspect actual one-to-one source-hour → physical timestamp and renewable data-hour keys for all 8,760 hours, including geographic/timezone and DST/leap boundaries.
4. Only then rerun **original** frozen Paper S core LP scenarios and original-cost window envelope sensitivity on physically matched wind/solar; rewrite Results/Figures and caveats based on actual changed numbers. **Do not call the old Wave A/B figures weather-driven.**

**Scientific gate remains closed.** This is a provenance and intake validation step, not a claim to have solved either unverified scientific hurdle. Full private manuscript and publisher source numeric bytes are not uploaded to the public repository.
