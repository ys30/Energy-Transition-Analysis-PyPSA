# Verified 2024 BPAT unlisted wind generator cross-schedule audit

Evidence: successful [GitHub Actions #41090860630](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41090860630), artifact `bpat-wind-cross-schedule-2024`, including exact matched generator IDs and `provenance.json`. Original source: official [2024 EIA-930A workbook](https://www.eia.gov/electricity/930-content/EIA_930A_2024_with%20layout.xlsx).

The 2024 EIA-860 WND-only generator comparison previously identified nine operating wind generator IDs at BPAT-attributed EIA-923 wind plants that were absent from **BPAT EIA-930A Schedule 2**. Matching each exact `EIA Plant ID + EIA Generator ID` across EIA-930A Schedule 2, 3, and 4 gives:

| Match check | Count of nine previously unlisted WND generators |
|---|---:|
| Listed in another BA Schedule 2 | **1** |
| Listed in BPAT Schedule 3 | 0 |
| Listed in BPAT Schedule 4 | 0 |
| Listed in another BA Schedule 4 | 0 |
| None of these categories with exact ID match | **8** |

**One cross-BA Schedule 2 identification:** EIA plant **56702**, wind generator **WPT1** (2024 EIA-860 operating wind nameplate **136.3 MW**) appears under EIA-930A BA code **AVRN**, not BPAT, in Schedule 2. All other eight unmatched wind generator keys have no exact entries in the searched schedule/BA classes. This does not rule out EIA-930A self-reported, unmatched, or alternative generator identifiers. It also does not prove the energy was measured by AVRN instead of BPAT for all hours.

No evidence of Schedule 4 pseudo-tie or dynamic relationship is established for these exact generator keys; **absence of a matching Schedule 4 row is not evidence that no such operating relationship existed**.

The overall 2024 EIA-923 versus EIA-930 BPAT wind difference remains about **1.981 TWh** and is **not allocated** to individual generators, BA transfers, curtailment, losses or unmetered generation. The 2024 EIA-923 Page 1 wind energy is reported at plant/fuel/prime-mover level and cannot be decomposed across generator IDs without independent generation records. The next defensible test is EIA-930A's unmatched/self-reported plant-generator identifiers and Schedule 4 relationship fields, plus any published hourly meter reporting population documentation.
