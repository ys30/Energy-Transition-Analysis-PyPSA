# Official 2024 EIA plant name and 2025 SPP interconnection-evidence review

## Reproducible name and coordinate expansion

**Successful CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41774793024

Inputs are the original 2024 official EIA-860 facility coordinate and name extract plus the 63-plant risk queue generated from the archived 5,665-row 2024 generator inventory. The new `src/energy_transition/eia860_named_poi_review.py` joins by exact EIA plant ID and verifies the original source state, nearest synthetic candidate bus ID, reported geographical distance and valid coordinate ranges.

| Metric | Real source audit |
| --- | ---: |
| Distant source plants matched by official EIA plant ID | **63 / 63** |
| Official facility names available / missing | **63 / 0** |
| Distinct synthetic candidate bus IDs | 15 |
| Historical 2024 nameplate covered | 5,831.9 MW |
| Plants assigned nearest bus `2053003` | 21 |
| Historic nameplate in that candidate grouping | 2,847.6 MW |
| Independently certified connections to **synthetic** network bus IDs | **0** |

The workflow uploads `official_named_63plant_poi_review_queue.csv`, `official_named_top20plant_poi_review_queue.csv`, and `named_candidate_bus_collision_clusters.csv`. Each contains official facility names and/or audited source plant coordinates, and is a far more actionable document-search input than plant ID alone.

## Top official EIA-860 plants in the high-risk candidate queue

| EIA plant ID | Official 2024 plant name | State/BA | Nearest *synthetic candidate* bus | Distance km | Historical nameplate MW |
| --- | --- | --- | --- | ---: | ---: |
| 56458 | Hobbs Generating Station | NM / SWPP | 2053003 | 210.403 | 681.5 |
| 63578 | Sagamore Wind | NM / SWPP | 2053003 | 192.168 | 522.0 |
| 2454 | Cunningham | NM / SWPP | 2053003 | 207.829 | 444.2 |
| 65577 | Clearwater Wind I | MT / PSEI | 2077001 | 59.304 | 365.5 |
| 63981 | Red Cloud Wind LLC | NM / PNM | 2053271 | 54.000 | 350.0 |

## First external transmission-owner evidence: Sagamore Wind

**Official SPP 29 October 2025 FERC-linked Shared Network Upgrade Facilities Construction Agreement:**
https://spp.org/Documents/75146/20251029_3978R1_Tip%20Top%20%26%20SPS%20%26%20PSCoOK%20Shared%20Network%20Upgrade%20FCA_ER26-290.pdf

In the document's Appendix A section 1.1, `GEN-2016-123-124-125` is explicitly identified as **Sagamore Wind Farm**, nameplate **522 MW**, in **Roosevelt County, New Mexico**, interconnected to **Southwestern Public Service Company's Crossroads 345-kV substation**, and commissioned in late 2020.

This is **positive project-specific evidence for a named interconnection substation**, not evidence that the model's nearest geographic bus `2053003` corresponds to that substation. The project match is supported by the exact EIA name/capacity (Sagamore Wind 522 MW), but independent EIA plant-ID linkage to the specific SPP interconnection request should also be verified prior to treating it as an electrical source crosswalk. The SPP document is a shared-network-upgrades construction agreement rather than a complete utility electrical node map. No PyPSA generator is inserted or approved.

The [SPP public queue](https://opsportal.spp.org/Studies/GIActive) also contains names such as `Cunningham 115kV` and `Hobbs 230kV` in **2026 proposed generator** requests, but those are NOT independent proof of the actual operating Cunningham or Hobbs Generating Station's historical point of interconnection. Do not conflate a named substation in another project's queue entry with the plant's own POI.

## Key scientific implication

The analysis can now distinguish **official EIA facility identity**, **third-party transmission agreement named substation**, **unverified exact EIA plant↔interconnection project linkage**, and **unverified synthetic-model bus**. This evidence hierarchy prevents silently attaching 2024 generation capacity to an arbitrary nearest bus or claiming that it establishes the 2030–2050 Western generator fleet.

**Current status:** 63 named plants in a reproducible review queue; one corroborating named-substation document (Sagamore, Crossroads 345 kV) found; **zero approved synthetic bus attachments**. Source-valid generator-to-real-system interconnection mapping is still an open research stage, and full Western calibrated OPF remains blocked.
