# Official EIA-930 2024 renewable missing-hour refetch result

Verified successful [GitHub Actions #41078514888](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41078514888), artifact `official-eia-renewable-gap-refetch-2024`, file `official_gap_refetch_matches.csv` (55 rows) and `official_gap_refetch_provenance.json`.

Four narrow source requests were made against the [official hourly EIA RTO fuel-type endpoint](https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/), one per affected BA/fuel/date window.

| BA and fuel | UTC missing window | Missing source rows | Refetched valid numeric rows |
|---|---|---:|---:|
| BPAT SUN | July 25 06:00–07:00 | 2 | 0 |
| CISO SUN | November 2 08:00–November 3 07:00 | 24 | 0 |
| CISO WND | November 2 08:00–November 3 07:00 | 24 | 0 |
| BPAT SUN | November 8 02:00–06:00 | 5 | 0 |
| **Total** | 31 distinct UTC hours | **55** | **0** |

Official API responses in the four enclosing query windows contained, respectively, 22, 48, 48, and 19 rows, but none of those rows filled the missing BA/fuel/timestamps.

**Consequence:** no EIA-sourced correction is currently available via this route. Full-year optimization of complete empirical demand + signed renewable net generation remains blocked by the strict 8,784-hour coverage gate. Future sensitivity scenarios may fill missing observations only in an explicitly separate, flagged data product and must show the impact on results; they must not be labeled as fully observed historical wind/solar dispatch. Additional official alternative data releases can be audited separately.
