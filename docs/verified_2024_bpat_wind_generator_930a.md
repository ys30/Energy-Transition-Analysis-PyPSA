# Verified 2024 BPAT wind generator-level EIA-930A Schedule 2 coverage

Evidence: successful [GitHub Actions #41090215668](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41090215668), artifact `bpat-wind-generator-930a-2024`; source tables: 2024 EIA-860 operating generator inventory and official 2024 EIA-930A Schedule 2.

**Important correction to prior plant-ID-only check:** Only **WND** fuel generators from EIA-860 count as wind facilities. An EIA-930A Schedule 2 plant entry for another technology must **not** count that plant's wind capacity as reported.

| Verified measure | Value |
|---|---:|
| BPAT-attributed EIA-923 qualified wind plants examined | 28 |
| 2024 EIA-860 operating WND generators at these plants | 30 |
| Operating WND generators matched to BPAT EIA-930A Schedule 2 by plant + generator ID | **21** |
| Wind plants with all operating WND generator IDs matched | **19** |
| Wind plants with no operating WND generator IDs matched | **9** |
| Annual qualified EIA-923 WND generation at those 9 plants | **2,419,650 MWh** |
| Annual qualified EIA-923 WND generation at 19 matched plants | 6,400,785.410 MWh |
| Operating wind nameplate at those 28 plants | 3,611.1 MW |
| Operating wind nameplate matched to BPAT SCH 2 | 2,683.7 MW |
| Operating wind nameplate not matched to BPAT SCH 2 | 927.4 MW |

**Hybrid example, plant 62745 (Wheatridge Hybrid):** 2024 EIA-860 has WND `WIND` 200 MW, SUN `SOLAR` 50 MW, and storage `BTRY` 30 MW. The 50-MW solar generator is in BPAT EIA-930A Schedule 2; the 200-MW WND generator is **not**. This plant was incorrectly classified as included by the preliminary plant-ID-only view. Generator-level wind matching corrects it.

The ~2.420 TWh of qualified EIA-923 WND generation at nine plants whose **operating wind generators are absent from BPAT EIA-930A SCH2** is **not an attributable numerical component** of the EIA-923 versus EIA-930 ~1.981-TWh difference. It is larger than the difference and highlights that different accounting boundaries, assets, reporting schedules or methodology may offset one another. Do **not** subtract, rescale or otherwise assign this amount to hourly EIA-930 wind data, historical curtailment or transmission flows.

Pending: examine whether the unmatched WND generator IDs appear in Schedule 2 under *another BA*, Schedule 4 pseudo-ties, or under unmatched/self-reported EIA-930A IDs; review publication coverage definition and EIA reporting hierarchy. No physical revenue or storage simulation calibration claim follows.
