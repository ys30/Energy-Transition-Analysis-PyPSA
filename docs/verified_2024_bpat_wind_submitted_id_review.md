# Verified BPAT 2024 wind EIA-930A submitted-ID and Schedule 4 review

Evidence: successful [GitHub Actions #41092329146](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41092329146), artifact `bpat-wind-submitted-id-2024`; official [EIA-930A 2024 workbook](https://www.eia.gov/electricity/930-content/EIA_930A_2024_with%20layout.xlsx).

Across nine 2024 EIA-860 WND operating generators absent from BPAT EIA-930A Schedule 2, this review searched official EIA plant/generator IDs and EIA-930A **submitted** plant/generator IDs across Schedules 2, 3 and 4. Exact two-key identity only; a shared plant or nearby generator name is not treated as a match.

| Outcome | Wind generators |
|---|---:|
| Exact EIA ID in another BA | 1 |
| Additional exact submitted-ID pair match | **0** |
| Unresolved | **8** |

One confirmed Schedule 2 other-BA listing is EIA plant **56702**, generator **WPT1**, BA **AVRN**. This is a reporting-inventory identification, not demonstrated hourly generation transfer.

Eight unresolved generators (EIA plant ID / wind generator ID): `55560/V-47`, `55989/V-47`, `56360/1`, `56666/1`, `57890/1`, `62745/WIND`, `64051/OCHW2`, and `64052/OCHW3`. All eight lack exact self-submitted IDs in the inspected workbook fields. For `62745/WIND` (Wheatridge Hybrid), a **different generator** appears under that plant in BPAT SCH 2, so the plant-level record cannot be counted as reporting coverage of the wind generator.

The script also enumerated same-plant Schedule 4 relationship text, but did not establish an exact Schedule 4 record for the nine target generators. The absence of a row does not prove there was no dynamic schedule or pseudo-tie in operation. EIA-930A is a generator inventory rather than hourly plant-to-BA power metering: it does not justify assigning the reported **~1.981 TWh** EIA-923/EIA-930 BPAT wind discrepancy to any of these sources.

## Status / next gating requirements

The official-ID and self-reported-ID exact-match checks did not resolve the remaining eight generator keys. Further reconciliation requires source methodological descriptions or actual hourly asset-level metering/accounting reports, not guessed aliases or energy reallocation. Do not alter EIA-930 wind inputs, interchange, storage operating savings or generator availability in PyPSA based solely on this inventory audit.
