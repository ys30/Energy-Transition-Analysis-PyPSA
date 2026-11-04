# Verified topology audit for three high-risk EIA-860 geographic candidate buses

**Real archived Western network + 63 named EIA plants:** [CI run 41779717439](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41779717439). This compares the **real archived 10,157-bus, 9,726-line, 2,080-transformer** PyPSA-USA topology-only NetCDF with the already verified [2024 EIA-860 official 63-plant review archive](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41774793024).

## What the actual archived topology contains

| Synthetic candidate bus | Current `v_nom` | EIA plants / operating generators geographically assigned | Source 2024 nameplate, MW | Candidate distance maximum | Incident Lines | Incident Transformers | Distinct graph neighbors |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `2053003` (NM, ReEDS p31) | 115 kV | 21 / 33 | 2,847.6 | 225.8 km | **2** | **0** | 2 |
| `2053000` (NM, ReEDS p31) | 115 kV | 12 / 14 | 976.0 | 197.1 km | **2** | **0** | 2 |
| `2077001` (MT, ReEDS p20) | 138 kV | 7 / 8 | 913.2 | 185.4 km | **4** | **0** | 3 |

The **top three candidate synthetic bus IDs** account for **4,736.8 MW of 2024 historical EIA nameplate**. This is geographic *candidate* inventory, not admitted injections or power transfer demand.

The real archived node `2053003` is located at **(-105.246, 33.706)**, nominal **115 kV**, and has lines to archived node IDs `2053019` and `2053021`. `2053000` is **(-104.898, 35.5753)**, nominal **115 kV**, with two direct lines; `2077001` is **(-106.596, 46.3057)**, nominal **138 kV**, with four lines reaching three unique neighboring bus IDs. These are archived *synthetic-topology-derived* nodes, not utility-certified station identifiers.

## Important graph interpretation

The current archived NetCDF additionally contains **6 Link components**, excluded from this connectivity metric. The audit deliberately constructs a NetworkX graph using **Line + Transformer** `bus0/bus1` edges only. This graph has **879 connected components**, of which **877 nodes have degree 0**; the three candidate nodes all belong to a larger line-transformer graph component of **9,275 buses**. This is **not a complete PyPSA electrical graph**: the imported NetCDF also contains `Link` components, which the calculation excludes. Consequently, neither 879 components nor the 877 degree-zero buses are evidence of real Western-grid islanding, service outages, or absence of connections through other device types. Further classification of Links and island endpoints is needed before any full electrical-contingency claims.

## Why the outcome matters

- The 21 plant / 33 unit entries grouped at `2053003` are far away from a 115-kV, only-two-line **synthetic candidate**. Their combined 2,847.6 MW historic nameplate is **not** authenticated electrical injection into this bus. Its current nominal bus voltage is not evidence that 345-kV **Sagamore Crossroads** substation, the separate **Hobbs 230-kV receipt point**, or Cunningham unit voltages map into this location. Treating them as such would create a fictional high-capacity input.
- The same issue appears in `2053000` and `2077001`, with several actual BA labels among their geographically coalesced source plants.
- Simple graph degree is not verified branch transfer capacity. Electrical thermal ratings, transformers, changes to source topology and actual utility connection evidence must all be verified before dispatch is interpreted physically.

## Reproduce

Source: `src/energy_transition/eia860_top3_candidate_network_topology.py`. Unit tests: `tests/test_eia860_top3_candidate_network_topology.py`. GitHub Action: `.github/workflows/eia860-top3-candidate-topology.yml`. JSON artifact: `eia860-top-three-synthetic-bus-topology-actual-network`.

The CI requires exactly 63 unique archived source plants, 15 distinct assigned candidate buses, historical MW conservation, exact source network sizes, matching candidate-node coordinates from both original archives and zero falsely admitted POI connections.

**Next action:** inventory archived `Link` edges, ratings and actual branch electrical parameters; independently recover a utility-certified generator-to-station crosswalk or rebuild source-compatible generation network before accepting 2030–2050 EFS dispatch or investment results.
