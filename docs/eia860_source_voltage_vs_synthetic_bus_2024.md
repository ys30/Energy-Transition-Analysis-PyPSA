# EIA-860 2024: external facility voltages versus geographically assigned synthetic bus

## Evidence status

The EIA-860 review archive and independent source-documents ledger identify three historical source plants sharing geographically nearest synthetic source-model bus `2053003`. Earlier [real archived bus audit](verified_eia860_top3_actual_archived_bus_topology.md) independently recorded this source-model bus as **115 kV**, two incident Line components and no incident Transformer. This does **not** define a real utility POI.

| EIA 2024 plant ID | Plant | EIA 2024 nameplate MW | Source transmission document | Sourced voltage context | Archived synthetic candidate |
|---|---|---:|---|---|---|
| 63578 | Sagamore Wind | 522.0 | SPP named Crossroads interconnection substation | 345 kV | `2053003`, 115 kV |
| 56458 | Hobbs Generating Station | 681.5 | SPP/SPS named network-service receipt point | 230 kV | `2053003`, 115 kV |
| 2454 | Cunningham | 444.2 | SPP/SPS unit-side receipt voltages | 13.8 / 20 kV (not HV POI) | `2053003`, 115 kV |

The names, values and sources are preserved in [source ledger](../data/eia860_top3_official_transmission_evidence.json) and [verified source hierarchy](verified_top3_spp_eia_poi_evidence_hierarchy.md). **Two externally documented high-voltage contexts differ from the synthetic candidate's nominal 115 kV.** Cunningham unit-side voltages are **not comparable** to a high-voltage substation voltage. Voltage differences flag a lack of direct identity evidence; they **do not rule out** a real stepped transformer or alternate connection. No utility-certified model-bus crosswalk is available.

## New automated checks

`src/energy_transition/eia860_synthetic_candidate_voltage_discriminator.py` consumes the source ledger and [source-model provenance](western_source_network_provenance.json), tests that the three plants still refer to the same originally audited synthetic candidate and that no POI acceptance flags were promoted. It emits machine-readable classifications and keeps admitted injection at **0 MW**, despite **1,647.7 MW** of historical EIA source nameplate in the three records. The CI is [EIA top-three SPP plant evidence hierarchy](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/eia860-spp-top3-evidence.yml). Source data come from prior verified archived studies; this is a **cross-evidence grading step**, not newly acquired substation engineering data.

## Actionable next research

1. Resolve the SPP request identifier for Sagamore against an independently established EIA plant/generator ID crosswalk.
2. Obtain actual plant-to-POI line diagrams and station voltage-level ties for Sagamore, Hobbs, and Cunningham; do not mistake source receipt points for physical generator junctions.
3. Recover a defensible real electrical-network case and map source facility IDs into that source vintage; avoid creating fabricated links to synthetic `2053003`.
4. Only after network, capacity, 8760-hour supply, source time semantics, and BA accounting gates pass should future physically constrained OPF be attempted.

**Research claim allowed:** the archived geographic candidates are insufficient to establish electrical injections. **Research claim prohibited:** EIA-860 generation is connected to the model's 115-kV node, or that plant voltage disagreement proves disconnection of the actual plant.
