# Paper S — July 2023 EIA-930 capacity-denominator falsification gate

Date 2026-11-17. New *necessary-condition* test of previously publisher-verified 2023 EIA-930A Schedule 2 candidate generator-nameplate MW versus actual 160 UTC hour-ending July 2023 EIA-930 reported BA-level net MW. **Not** a validated capacity factor and not an externally audited BA↔state generator crosswalk.

## Critical result

In the full 160 shared-hour source panel (2023-07-01 08:00Z to 2023-07-07 23:00Z), the following generator-roster candidate capacities are breached by observed BA net generation:

| BA | fuel | candidate Schedule 2 nameplate MW | observed max net MW | hours above candidate (of 160) | observed peak / candidate |
|---|---|---:|---:|---:|---:|
| PSCO | solar | 1666.9 | 1806 | **14** | 1.0834 |
| WACM | solar | 161.9 | 277 | **50** | 1.7109 |

Other observed BA/fuel groups (IPCO wind/solar, PNM wind/solar, PSCO wind, WACM wind) did not exceed their candidate nameplate totals in this window. **Passing this necessary bound is not sufficient for a validated 2023 hourly denominator.** Each exceeded candidate is incompatible with using the 2023 roster subset as an assumed *complete, simultaneously applicable* set of net MW capacity at every hour, absent reconciliation of BA scheduling, roster coverage, reporting definitions, and generator vintage. It does not imply individual physical generators exceed their rated power.

## Geographical and duplicate cautions

- IPCO wind candidate: **561 MW in Idaho / 714.7 MW overall = 78.5%**; remainder 153.7 MW is physically Oregon. IPCO solar: 400 MW Idaho / 473.5 overall = 84.5%. **Nameplate shares are not hourly generation allocation shares**.
- WACM wind candidate: Wyoming 349.9 MW / 1131.6 MW overall = **30.9%**; Colorado 751.7 MW, Nebraska 30 MW. The selected WACM solar 161.9 MW is in Colorado, **0 MW in Wyoming**, rendering a WACM↔WY state solar proxy particularly unsafe.
- Shared physical generator EIA plant 59975/CW1: 150 MW wind appears in both PSCO and WACM Schedule 2; no arbitrary BA assignment or double addition allowed. Schedule 4 pseudo-ties remain distinct and are not simply added to Schedule 2 totals.

## Data audit provenance and status

Official EIA-930A 2023 workbook SHA256 `ed8008bf4f5cbb0799d5a99b4dbc806e892eb150a9b357a709b582a93e28676f`, source extraction artifact 14194398635; existing authentic EIA-930 July BA 160h extraction source SHA256 `0e72513a99c920391c0fc51a1691e84780ca5da81ba0c34b2fe218ed3fbc2f5a`. Exact source subset and generator evidence were re-opened from the existing local archived file `Paper_S_EIA930A_2023_BA_State_Candidate_Capacity_Audit.zip`; hour observations re-opened from `Paper_S_EIA930_2023_July_BA_Observed_Audit`. New reproducibility output is provided as conversation bundle `Paper_S_EIA930_Capacity_Denominator_Falsification_2026-11-17.zip` (audit.py, eight BA-fuel rows, every 64 exceedance timestamp, cross-BA overlap, figure, sha256 manifest).

The previously observed 2023 common-weather **160 h** state–BA *curve shape* test remains a diagnostic only; do not use candidate nameplate to convert reported MW to trusted observed CF, nor describe BA curves as directly observed state power.

**Next evidence gates**: (a) audit complete 2023 monthly EIA-860 generator activity and 930A scope, including PV behind-the-meter and dynamic BA transfers; (b) reconcile CW1 Schedule 2 assignments and Schedule 4 transfers, (c) source verified 2023 full-year BA reported data and time labels, then (d) co-weather shape comparisons on appropriately matched BA source geographic shares. Frozen 1440 LP, 2160 ATB comparisons, 2×2 and 3×3 studies remain unmodified.
