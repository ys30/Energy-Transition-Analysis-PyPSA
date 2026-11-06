# Paper T v5: editorial/causal-claim audit and source-evidence freeze

**Date:** 2026-11-06. **Status:** verified engineering evidence, private collaborator-review manuscript v5; **not** journal submission-ready. Complete private manuscript, comments, and reference bibliography are NOT stored in this public repository.

## Manuscript corrections after v4 review

1. Clarified the numerical lag sign: original 2020 source hour index `h` is compared against independent ReEDS 2022 HDF5 hour index `h-k`, for candidate integer shifts `k=-12..12`; only `8760-abs(k)` genuine overlapping hours contribute, and missing year-boundary values are never circularly synthesized.
2. Distinguished the initial strict numerical threshold of `0.01 MW` from the descriptive `1 MW` near-match screen; neither is a confidence interval or a physical time-label uncertainty bound.
3. Clarified all 289,080 source-hour value pairs come from **two related modeled-product lineages**, so they are **not 289,080 independent random observations**. State-year observations share scenarios and upstream processing; avoid arbitrary significance tests or claims of statistically independent replications.
4. Consolidated redundant conclusions and corrected the prose for Figure T1: the original EFS2020 `LocalHourID` **physical** clock, weather-year interpretation and geographical allocation remain **not authoritatively certified**.
5. Listed the original 2018 EFS report's full ten authors according to the official research record, and removed editorial comments from formatted references.
6. Clarified frozen-candidate testing uses **4,379 source-index hours in the first window and 4,377 in the second** after excluding nonoverlapping boundaries, and that fitting a source lag does not establish a physical Idaho timezone.
7. Figure T3 is based on **separate source-reference month and clock-hour marginal residuals**, not unavailable joint 12×24 month-by-hour cells.

## Publisher and peer-reviewed source records checked

| Record | Verified source metadata | Role/limitation |
|---|---|---|
| [NLR EFS load profile catalog](https://data.nlr.gov/submissions/126) | submitted Jan 14, 2020; DOI `10.7799/1593122` | Original 2020 data provenance; does **not** itself certify physical UTC `LocalHourID` |
| [ReEDS electricity demand profiles 2022](https://zenodo.org/records/18461543) | published Feb 4, 2026; DOI `10.5281/zenodo.18461543`; year-2012 CST UTC−6 hour-ending; 2012 Dec 31 omitted | Product vintage named 2022, **not** an original EFS2020 clock declaration |
| [EFS scenarios report](https://doi.org/10.2172/1459351) | 2018, NREL/TP-6A20-71500, 10 original authors | Context and scenario lineage; not an hour-by-hour cross-release synchronization certificate |
| [Ruggles et al. (2020)](https://doi.org/10.1038/s41597-020-0483-x) | *Scientific Data* 7:155 | Background on hourly load data quality, not this original EFS/ReEDS comparison |
| [Shaffer (2019)](https://doi.org/10.1111/caje.12407) | *Canadian Journal of Economics* 52(4), 1374–1400 | Geographic heterogeneity of DST impacts, not a proven Idaho cause |
| [Lozano Medina et al. (2026)](https://doi.org/10.1016/j.ecmx.2026.101803) | *Energy Conversion and Management: X* 30:101803 | Legal/solar clock distinctions, not justification for treating two source vintages as synchronized |
| [Merrick et al. (2024)](https://doi.org/10.1016/j.eneco.2024.107675) | *Energy Economics* 136:107675 | Storage temporal representation background (especially relevant to separate Paper S) |

## Source figure chain

- Figure T1 exact fail-closed clock admission diagram: [CI #42177083314](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42177083314).
- Source-derived Figures T2/T4 (nonwrapping lag and frozen Idaho candidate): [CI #42145896229](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42145896229).
- Figure T3 real source marginal profiles: [CI #42162565936](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42162565936).

## Before submission

- Obtain *source-specific* publisher explanation for EFS2020 `LocalHourID` calendar/year/time-zone/DST/hour-ending semantics, **or leave the clock admission explicitly blocked**.
- Deposit versioned source-derived 33-state-year lag table, 14 Idaho Sector×Subsector annual profiles, methods and figure assets; link stable hashes/DOI instead of relying only on expiring Actions artifacts.
- Select a target journal and complete journal-specific author information, reference style, metadata and literature-gap discussion.
- Consider an external dataset for generalization. The current pair consists of two **related**, not necessarily independent scenario products, and the Idaho perturbation is numerical/diagnostic, not causal.

The associated v5 manuscript and collaborator review package are **private**; this note is a public technical evidence boundary only.
