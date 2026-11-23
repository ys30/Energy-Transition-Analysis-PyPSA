# Paper S — Official EIA-930A 2023 BA/state wind and solar generator evidence

**Evidence source:** Original EIA-930A 2023 workbook,
https://www.eia.gov/electricity/930-content/EIA_930A_2023_with%20layout.xlsx .
Workbook SHA-256:
`ed8008bf4f5cbb0799d5a99b4dbc806e892eb150a9b357a709b582a93e28676f`.

**Verified extraction:** GitHub Actions [run 43795452473](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43795452473), source-artifact ID `14194398635`, completed successfully. Data files:
`eia930a_2023_four_BA_wind_solar_generator_evidence.csv`,
`eia930a_2023_four_BA_SCH2_renewable_state_capacity_candidates.csv`,
`eia930a_2023_four_BA_schedule4_pseudotie_audit_counts.csv`.

## Original source, candidate capacities only

Include `SCH 2` wind or solar generators with source EIA-860 operation year/month **at or before July 2023**. The 2023 EIA-930A generator list was matched to an EIA-860 snapshot dated February 2025 in the publisher's workbook layout notes, so retrospective availability is **not confirmed for every historical hour**. Source entries without eligible dates or source capacity are not silently assigned values.

| BA | Technology | Generator state | Candidate nameplate MW | Share of BA-technology candidate capacity |
|---|---|---|---:|---:|
| IPCO | Solar | ID | 400.0 | 84.5% |
| IPCO | Solar | OR | 73.5 | 15.5% |
| IPCO | Wind | ID | 561.0 | 78.5% |
| IPCO | Wind | OR | 153.7 | 21.5% |
| PNM | Solar | NM | 544.0 | 100.0% |
| PNM | Wind | NM | 2,569.0 | 100.0% |
| PSCO | Solar | CO | 1,666.9 | 100.0% |
| PSCO | Wind | CO | 4,492.3 | 100.0% |
| WACM | Solar | CO | 161.9 | 100.0% |
| WACM | Wind | CO | 751.7 | 66.4% |
| WACM | Wind | NE | 30.0 | 2.7% |
| WACM | Wind | WY | 349.9 | 30.9% |

Aggregated by BA: PNM wind 2,569.0 MW, solar 544.0 MW;
PSCO wind 4,492.3 MW, solar 1,666.9 MW;
IPCO wind 714.7 MW, solar 473.5 MW;
WACM wind 1,131.6 MW, solar 161.9 MW.

**Cross-BA duplication requiring resolution:** SCH 2 includes the same source EIA Plant ID **59975**, Generator ID **CW1**, nominal wind **150.0 MW**, in **PSCO worksheet row 18142** and **WACM worksheet row 21874**, both with state CO, recorded operation November 2015. Do not count those two source assignments as distinct physical generators when summing capacities across BAs; verify reporting and pseudo-tie treatment first.

`SCH 4` renewable relationship counts included PNM wind 8 and IPCO wind 1; these **were not added** to capacity totals. Source extraction contains 322 target BA wind/solar evidence records including SCH 2 and SCH 4, with 30 source SCH 2 records not meeting the known pre-July operation-date screen.

## Scientific admission gates

1. No comparison between **state-level ReEDS CF** and **BA-level reported MW** may be labeled direct validation without verified geographical alignment and capacity contributions.
2. Annual BA-reported candidate generator populations are **not** necessarily July 2023 hourly active, net-output-capacity-equivalent populations; retirement and pseudo-tie details require review.
3. `SCH 4` relationships, unresolved IDs and cross-BA duplicate source assignments are separate auditable exception categories.
4. Real source data in EIA-930 balance are **MW**; generator nameplate denominators are **MW**. Dividing net MW by nameplate MW would be a *candidate diagnostic ratio*, not automatically a source-authenticated capacity factor.
5. Correlation of the observed BA series, a state capacity share or the current 1,440 LP scenario results are not an observed-versus-ReEDS source-matched RMSE.
6. Do not alter pinned weather/load 720+720 LP results or ATB 2025 v2 2,160 cost screening. Paper S PR remains Draft until causal and physical-coverage limitations are resolved.
