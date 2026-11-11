# Paper T WP2 — 2018 AZPS × Phoenix irradiance, validated controlled timing shifts

**CI passed:** [Actions #43061405750](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43061405750); artifact `paper-t-wp2-real-2018-azps-phoenix-nasa-power-15cases`.

## Source and time semantics
- AZPS measured-derived hourly BA demand from Ruggles October 2020 cleaned EIA-930 archive, pinned original repository Git commit `b80145df5f92aba56c52ed45281831b93543fb3b`, `date_time` UTC hour ending.
- NASA POWER `ALLSKY_SFC_SW_DWN` for 2018, Phoenix 33.4484°N, −112.074°E, API `time-standard=UTC`, interpreted as UTC hour beginning.
- Map demand interval-ending `t` to irradiance interval-starting `t-1`. This yields 8,760 complete common 2018 UTC hours. Evaluation holds target indices 3..8756 (8,754 hours), with no circular wrap, interpolation, or silent missing fills.
- Output model is **illustrative**, with proxy solar = assumed 500/1,000/2,000 MW × min(GHI/1000 W m^-2,1). This is not calibrated PV production or actual AZPS renewable capacity/dispatch.
- The source 8,760-hour load and irradiance data remain unmodified. Nonwrapping demand-index shifts change comparison-window demand energy slightly (−0.00645% to +0.00826%), while target-window irradiance energy is fixed.

## CI-verified results: relative change in maximum proxy net demand
| Proxy size MW | −3h | −2h | +2h | +3h |
|---:|---:|---:|---:|---:|
| 500 | −3.2909% | −2.3049% | +2.2840% | +2.3571% |
| 1000 | −7.3564% | −5.3500% | +3.9873% | +4.1359% |
| 2000 | −13.3482% | −7.7031% | +5.9912% | +6.2947% |

A separate source-derived correlation diagnostic is unaffected by positive capacity multipliers: at demand shift −3h, −2h, 0h, +2h, +3h the load/solar-proxy Pearson correlations are 0.47112, 0.38880, 0.20424, 0.03951 and −0.03180. The respective irradiance-weighted-load differences against baseline are +363.50, +251.36, 0, −224.34 and −321.49 MW.

**Important null metric:** solar overlap defined as `sum(min(demand,solar))/sum(solar)` is exactly 1 in all 15 cases because assumed solar never exceeds demand, making this metric noninformative. It is retained only as an explicit validity diagnostic; correlation and solar-weighted demand are the useful coincidence statistics.

## Evidentiary limits
This experiment does **not** validate EFS2020 `LocalHourID` or the physical-hour crosswalk from EFS2020 to ReEDS2022. That release pair remains `BLOCK_PHYSICAL_JOIN`. The experiment does not estimate an observed electricity-system error, actual photovoltaic output, geographic BA-wide weather, storage dispatch, curtailment or costs. Publisher-source UTC labels are documented and data indices are independently reconciled, but independent review is still required for any operational physical-hour join.

Implementation: `src/energy_transition/paper_t_wp2_real_resource.py`; workflow: `.github/workflows/paper-t-wp2-real-resource.yml`. See private v20.5 manuscript Fig. S8 and Section 4.5 for interpretation.
