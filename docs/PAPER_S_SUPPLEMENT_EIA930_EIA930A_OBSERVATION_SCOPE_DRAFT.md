# Paper S — Supplementary Methods and Results: EIA-930 observational footprint audit
**Status: manuscript-ready draft of source/quality audit, not a validated model-skill result.** Figures, tables and substantive claims must be checked against the journal's final style and the frozen manuscripts before submission.

## S1. Observed generator output and time indexing

We extracted hourly *net generation in MW* from the July 2023 part of the public EIA-930 historical balancing-authority (BA) archive, using source-reported wind and solar columns separately from imputed and adjusted columns. We retained the source's explicitly labeled UTC hour-ending timestamps and did not alter negative net generation. Source provenance is the 2023 second-half EIA-930 raw archive, mirrored by Catalyst Cooperative / PUDL on Zenodo record 22856870 (archive MD5 `1de4e47693426671123bb08ec0d33995`). GitHub Actions run `43682969646`, artifact `14150700990`, records the source extraction; GitHub Actions run `43755967483` independently checks the common-window diagnostic.

The resulting panel contains **1,282** original BA–fuel–hour rows for PNM, PSCO, IPCO, and WACM and two generation categories. The common observation window, **July 1 08:00 through July 7 23:00 UTC (hour-ending)**, contains **160 timestamps** per BA–fuel series (1,280 rows). This common window is used for all descriptive calculations. Earlier start-of-period absences in the downloaded archive are **not** labeled verified physical measurement outages, because local-date source file partition conventions require a separate boundary audit.

## S2. Negative net output and descriptive sensitivity

Out of the 1,280 common-window observations, **87 report negative MW**: four PNM wind hours, 41 PNM solar hours, and 42 PSCO solar hours. Remaining series report no negative values in this window. Zero-clipping would increase the series mean by **0.1063 MW (PNM wind)**, **0.2688 MW (PNM solar)** and **1.7250 MW (PSCO solar)**. We retained original reported net MW in the primary descriptive audit; zero-clipping is shown as a nonphysical-suppression sensitivity diagnostic rather than an undocumented correction. The **160-hour Spearman correlation between PSCO and WACM wind is approximately 0.882**; this is a **between-BA observed-output correlation**, not the accuracy of a ReEDS-derived simulated profile. Solar BA-to-BA correlations are likewise strongly influenced by shared diurnal timing.

## S3. Official EIA-930A 2023 generator reporting roster

To examine whether hourly BA output could be normalized using a compatible source footprint, we audited the official 2023 EIA-930A workbook at `https://www.eia.gov/electricity/930-content/EIA_930A_2023_with%20layout.xlsx` (SHA-256 `ed8008bf4f5cbb0799d5a99b4dbc806e892eb150a9b357a709b582a93e28676f`). The original workbook provides BA identifiers, generator/plant identifiers, fuel technology, physical state/county, nameplate capacity, reported operation dates and schedule-specific reporting context. The source-audited extraction and cross-BA duplicate checks passed GitHub Actions `43797969795`, artifact `14196240937`.

In the scoped four-BA extraction, **322 selected wind/solar source rows** were retained across Schedules 2 and 4; **12 BA–fuel–state candidate nameplate-capacity cells** were aggregated from Schedule 2 for units with recorded commissioning dates on or before July 2023. Schedule 4 was analyzed as distinct dynamic-scheduling/pseudo-tie evidence and **was never added to the Schedule 2 capacity denominator**. The scoped generator-ID audit found **zero records with unresolvable generator identifiers** and **one duplicated generator appearing in two BA reporting scopes**: EIA plant `59975`, generator `CW1`, 150 MW wind in Colorado, listed in PSCO (`SCH 2!18142`) and WACM (`SCH 2!21874`). Summing the four BAs' Schedule 2 wind rows yields a **candidate row-total of 8,907.6 MW**; the union of distinct physical generator identities is **8,757.6 MW**, differing by exactly **150 MW**. These are **static source-scope arithmetic comparisons**, not inferred 2023 hourly available capacities or confidence bounds.

Importantly, IPCO's scoped wind and solar generator rosters span **Idaho and Oregon**, while WACM's scoped wind capacity spans **Colorado, Nebraska and Wyoming**. Consequently, a BA-level net-generation series cannot be interpreted as production exclusively from the identically named or nominal target state. PSCO and WACM likewise cannot simultaneously be assigned the full 150 MW CW1 capacity when deriving a non-overlapping physical union, nor can the 150 MW simply be allocated arbitrarily to one BA.

## S4. Model-validation admission rule

No quantitative ReEDS-to-EIA-930 hourly MAE, RMSE, or observed capacity factor is reported from these data alone. A defensible comparison would require generator-level July 2023 reporting/operating status, BA dispatch/scheduling participation including CW1 and Schedule 4 accounting, observed and modeled wind/solar technology compatibility, a **true 2023 co-temporal model output** on an identical hourly convention, and a verified capacity basis compatible with the EIA-930 reported *net MW*. A **2012 ReEDS weather capacity-factor series** cannot be paired with **2023 observed generation** and called an external same-year validation. We treat the above audit as a reproducible empirical examination of spatial coverage and observational data quality, separate from the paper's frozen LP and conditional ATB cost-screening results.

### Reproducibility anchors

- Actual observed BA source: run `43682969646`, artifact `14150700990`.
- Observed 160-hour descriptive diagnostics: run `43755967483`, artifact `14178595828`.
- Official roster source schema audit: run `43755968031`, artifact `14178298786`.
- Full scoped generator overlap audit: run `43797969795`, artifact `14196240937`.
- Original LP 720+720 and 2,160-case ATB cost screen: remain independently frozen.
