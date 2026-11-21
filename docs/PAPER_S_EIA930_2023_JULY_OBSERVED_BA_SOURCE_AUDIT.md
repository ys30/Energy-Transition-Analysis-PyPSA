# Paper S — Real EIA-930 July 2023 BA-level generation source audit

Source: successful GitHub Actions run [#43682969646](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43682969646), artifact ID `14150700990`. Upstream archive: Catalyst/PUDL-preserved EIA-930 `eia930-2023half2.zip` at Zenodo record 22856870; archive MD5 `1de4e47693426671123bb08ec0d33995`.

The script downloaded and checksum-verified the historical archive, parsed `eia930-2023half2-balance.csv`, and retained BA-level **reported MW**, imputed MW, adjusted MW, and **UTC hour-ending** tokens for PNM, PSCO, IPCO, WACM and wind/solar.

## Independently confirmed empirical results

| BA | Wind rows | Solar rows | Negative wind MW rows | Negative solar MW rows |
| --- | ---: | ---: | ---: | ---: |
| PNM | 160 | 160 | 4 | 41 |
| PSCO | 161 | 161 | 0 | 42 |
| IPCO | 160 | 160 | 0 | 0 |
| WACM | 160 | 160 | 0 | 0 |

Total: **1,282 BA-fuel-hour records**, **87 negative-MW records** retained and unmodified. All selected reported-MW fields are nonmissing. The imputed-MW field has zero nonmissing entries, and reported and adjusted MW match in these selected rows. These properties do not prove fully independent metering or establish physical meaning of negative net generation.

The original queried UTC window (July 1 00:00 to July 7 23:00 UTC) comprises 168 hourly end labels per group, or 1,344 expected slots; 62 are absent: PNM/IPCO/WACM lack July 1 00:00–07:00 UTC (8 each per fuel), while PSCO lacks July 1 00:00–06:00 UTC (7 each per fuel). **All eight series are continuous over the common 160-hour window, July 1 08:00 to July 7 23:00 UTC, for exactly 1,280 comparable BA-fuel-hour records.** The absent beginning hours appear consistent with local-date archive partition boundaries; do not call them missing observations of a full 168-hour UTC collection without verifying upstream archive boundaries.

## Hard limits

1. The values are in **MW**, not source-authenticated hourly MWh.
2. A BA is not a state. No BA-to-state or county capacity allocation has been authenticated.
3. Net MW may be negative; preserve and investigate meaning rather than clipping to zero.
4. No historical installed-capacity denominator or matching ReEDS weather/clock profile has yet been jointly validated.
5. This is an actual observation **source/quality audit**, **not** an observed-vs-simulated RMSE validation nor profitability evidence.
6. Original 720+720 LP study and pinned ATB 2025 v2 2,160 cost comparisons must remain unchanged.
