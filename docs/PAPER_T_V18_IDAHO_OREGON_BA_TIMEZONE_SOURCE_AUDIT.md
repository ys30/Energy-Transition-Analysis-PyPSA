# Paper T — independent source-code check of Idaho/Oregon BA timezone hypothesis (2026-11-10)

**Status: partial support, Oregon negative control falsified; the 0.17 BA load share remains unverified.** This is a source-code audit, **not** proof that the published ReEDS2022 `demand_EFS_REFERENCE.h5` used this specific pipeline or legacy mapping.

## Independently fetched source files

Official archived repository: `NatLabRockies/ReEDS-2.0`. GitHub blob IDs and reproducible links:

| file | Git blob SHA |
|---|---|
| `hourlize/inputs/load/legacy_ba_timezone.csv` | `203a617eb0f87845f0783127debc7806926ab5b7` |
| `hourlize/inputs/load/legacy_ba_state_map.csv` | `fa2fba14b8ffaba9c114db6fbac3249cf31009af` |
| `inputs/county2zone.csv` | `b0d62f1685691560b8c413a479ab24885ae8aaf7` |
| `inputs/temporal/reeds_region_tz_map.csv` | `b03ed683233c306e4ff12f0db3678538b3dcd422` |
| `hourlize/load.py` | `0bc278021dc43f6b5378a47c61bbbf049ef3ec39` |

The two legacy tables have 134 data records each, matching 134 legacy BAs.

## Joined BA results

| State | Legacy BA | timezone UTC hours | Historical counties in `inputs/county2zone.csv` |
|---|---|---:|---:|
| Idaho | p14 | -8 (Pacific) | 7 |
| Idaho | p15 | -7 (Mountain) | 22 |
| Idaho | p16 | -7 (Mountain) | 15 |
| Oregon | p5 | -8 (Pacific) | 26 |
| Oregon | p6 | -8 (Pacific) | 6 |
| Oregon | p7 | -7 (Mountain) | 4 |

Idaho p14 counties: Benewah, Bonner, Boundary, Kootenai, Latah, Lewis, Nez Perce. Oregon p7 counties: Baker, Harney, Lake, Malheur.

**Hypothesis test:**
1. Idaho has a Pacific-designated BA: **PASS** (p14).
2. Oregon has no Mountain-designated BA: **FAIL** (p7).
3. Idaho p14's **load-weighted share** close to 1 - 0.834425 = 0.165575 (16.5575%): **NOT TESTABLE from these mappings alone**. 7/44 = 15.91% is an unweighted **county-count ratio**, emphatically **not load allocation** and not validation of the fitted coefficient. BA count 1/3 is equally unsuitable. A version-matched BA demand allocation or historical county load participation factor is required.

## Code path vs evidence of actual execution

`hourlize/load.py` defines `aggregate_legacy_bas_to_states` (lines 116–134) and a conditional branch (lines 182–213) where `sector_settings['timezone']=='local'` and `sector_settings['regional_scope']=='legacy_ba'` obtains BA timezones, applies `np.roll`, then aggregates to states. **This establishes a possible software mechanism, not that this exact code path generated the archived ReEDS2022 dataset.** The retrieved source even refers to `df.columns` within a loop where nearby code stores the concatenated replacement array in `df_load_replace`; implementation details and runtime version must be examined before treating it as an executed source transformation.

A separate county-based time-zone mapping `inputs/temporal/reeds_region_tz_map.csv` labels *all four Oregon p7 historical counties* Pacific, despite the legacy BA p7 Mountain label. Therefore a BA timezone cannot be assumed to describe each county's civil timezone or imply a large allocation share.

## Current manuscript interpretation

The uploaded private v18 manuscript (§5.3) predicts *“a Pacific-time zone in Idaho, none in Oregon, and an allocation share close to [the fitted ~0.17]”*. The first is supported by an official legacy mapping; the second is directly contradicted; the third is unresolved. The Idaho two-lag model remains a numerical fit, not an independently established geographic allocation.

Suggested replacement for §5.3:

> An independent audit of the public ReEDS legacy balancing-area maps identifies one Pacific-designated BA (p14) and two Mountain-designated BAs (p15–p16) in Idaho, confirming that BA-specific time-zone metadata capable of representing a mixed-zone state existed in the model's open input ecosystem. However, Oregon also includes a Mountain-designated legacy BA (p7), despite its rounding-level single-lag correspondence. Thus BA time-zone heterogeneity alone is not sufficient to explain the cross-release Idaho anomaly. The public source contains a conditional pathway for time-zone shifting of legacy BA profiles before state aggregation, but we have not authenticated that this pathway or these exact legacy inputs generated the published ReEDS2022 EFS_REFERENCE release. The Pacific share of Idaho's allocated BA load remains unknown, and the fitted 0.166–0.168 coefficient must not be interpreted as a measured geographic fraction.

**Screening G5 remains blocked.** This check does not authenticate the 2020 EFS physical hour, the 2022 release-generation lineage, or an hourly join.

## Follow-up that would actually test the mechanism

Retrieve version-matched `EFS_REFERENCE` generation code/configuration and Idaho/Oregon BA hourly input (or explicit county allocation weights). For each release-relevant BA, measure annual load share and inspect whether the BA-local clock shift precedes state aggregation. Compare 2030/2040/2050 shares with the *orientation-matched* frozen mixture coefficients; require documented generation lineage and a residual reduction to rounding-level when reconstructing with actual BA series. Otherwise report a plausible but unconfirmed source-processing mechanism.
