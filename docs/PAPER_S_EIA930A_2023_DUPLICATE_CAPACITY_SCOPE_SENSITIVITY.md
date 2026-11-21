# Paper S — official EIA-930A 2023 BA generator accounting sensitivity

## Evidence, source and scope

Source: official **2023 EIA-930A**, workbook SHA256 `ed8008bf4f5cbb0799d5a99b4dbc806e892eb150a9b357a709b582a93e28676f`. Generator-row extraction: [GitHub Actions #43795452473](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43795452473), artifact `14194398635`. These are **candidate 2023-July-by-recorded-operation-date nameplate MW**, not confirmed hourly installed/available MW, not EIA-930 observed capacity factors, and not ReEDS model validation.

Source `SCH 2`: 283 selected reporting rows with operation year/month recorded no later than July 2023, corresponding to 282 distinct plant/generator IDs across the four selected BAs.

| BA | Fuel | All SCH 2 rows, candidate MW | Excluding any shared generator, candidate MW | Shared-ID ambiguity MW |
|---|---|---:|---:|---:|
| IPCO | wind | 714.7 | 714.7 | 0 |
| IPCO | solar | 473.5 | 473.5 | 0 |
| PNM | wind | 2,569.0 | 2,569.0 | 0 |
| PNM | solar | 544.0 | 544.0 | 0 |
| PSCO | wind | 4,492.3 | 4,342.3 | 150.0 |
| PSCO | solar | 1,666.9 | 1,666.9 | 0 |
| WACM | wind | 1,131.6 | 981.6 | 150.0 |
| WACM | solar | 161.9 | 161.9 | 0 |

**PSCO/WACM common generator**: EIA plant `59975`, generator `CW1`, **150 MW** wind in Colorado, from `SCH 2!18142` and `SCH 2!21874` (2015-11 commissioning date reported). Candidate wind records across BAs sum to **8,907.6 MW**, while deduplicating identical generator IDs gives **8,757.6 MW** (150 MW excess). The all-record and exclusive-only numbers above form a **generator-assignment sensitivity**, **not independently verified confidence intervals** nor defensible hourly fleet lower/upper bounds. Do not simply subtract 150 MW from both BAs simultaneously and call that a valid BA allocation.

**Separate Schedule 4 evidence** (excluded from Schedule 2 denominator): `PNM`: AZPS 190.0 MW / 2 wind rows, CISO 1,220.5 MW / 5 wind rows, LDWP 350.0 MW / 1 wind row (**1,760.5 MW total, eight rows**). `IPCO`: NWMT 9.0 MW / one wind row. Their interpretation and any pseudo-tie or dynamic BA allocation requires upstream documentation and must not be added to observed BA nameplate MW without proof.

Important caveat: `SCH 2` source matching is based on annual 2023 EIA-930A generator information (the underlying EIA-860 linkage may be later); the historical state, BA, technology, active commissioning date, temporal fleet status, net-vs-nameplate compatibility and reporting coverage all require separate verification. **No MAE/RMSE and no revenue or profitability result is claimed**. The original 1,440 LP and 2,160 ATB comparisons remain frozen.

Next required evidence gate: generator-level 2023 July status, report/reassignment conventions for `59975/CW1`, Schedule 4 accounting, matched observed 2023 generation footprint and authentic co-temporal ReEDS profile.
