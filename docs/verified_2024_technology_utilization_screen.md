# Verified 2024 EIA-860 × EIA-923 qualified technology utilization screen

Evidence: successful [GitHub Actions #41083088921](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41083088921), `eia2024-technology-utilization-screen` artifact, CSV `eia2024_qualified_generation_nameplate_ratios.csv`. Reuses audited source artifact from [2024 EIA end-to-end pilot #40964541770](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/40964541770).

**Crucial boundary:** these data combine **CISO + BPAT**. The qualified EIA-923 generation observations in this artifact are **not BA-by-technology observations**, and cannot be separated by BA without additional validated source records. Denominator is EIA-860 supported nameplate by corresponding fuel, summed across both BAs, ×8,784 hours in leap year 2024. Qualified Page 1 EIA-923 source rows may be missing, so these are *coverage-constrained descriptive ratios*, **not calibrated actual capacity factors**, hourly availability or capacity credits.

| Technology | Nameplate MW | Qualified EIA-923 net generation MWh | Qualified generation / (nameplate × 8784 h) |
|---|---:|---:|---:|
| Coal | 784.9 | 3,092,147 | 44.85% |
| Natural gas | 34,055.0 | 80,983,755 | 27.07% |
| Geothermal | 2,052.9 | 7,900,613 | 43.81% |
| Hydro | 26,523.2 | 82,215,907 | 35.29% |
| Nuclear | 3,523.0 | 28,345,974 | 91.60% |
| Oil | 158.4 | 100,464 | 7.22% |
| Solar | 23,309.6 | 47,540,199 | 23.22% |
| Wind | 9,951.8 | 24,160,884 | 27.64% |

The previous storage model uses assumed constant 55 GW firm and 20 GW peaker capacity, i.e. **75 GW total illustrative dispatchable resources**. EIA-860 supported thermal/nuclear/hydro/geothermal nameplate summed to 67.10 GW, before any derating, unmodeled technologies, storage, reserves or geographical delivery restrictions. This is not proof of adequate hourly capacity; the assumed 75 GW is **not historically calibrated**.

Next: obtain independently audited **BA/plant-specific** qualified EIA-923 totals, map generator dispatchability and hourly source constraints, avoid duplicate wind/solar injections and audit partial BA coverage. Do not infer future investment profitability or historical shortage levels from the current 55/20 GW model.
