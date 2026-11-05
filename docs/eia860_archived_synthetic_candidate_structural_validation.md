# Original archived Western synthetic-bus structure and 2024 EIA-860 POI evidence

## Purpose

Previous evidence-ledger analyses connected three EIA 2024 source plant **names** to a *geographically selected synthetic* network candidate, bus `2053003`. Earlier source-network diagnostics reported the candidate as 115 kV with two incident Lines. The new gate checks that assertion against the **original archived PyPSA NetCDF**, rather than treating a hard-coded 115-kV value as current source evidence.

## Original evidence and method

- Network source: original `real-western-base-network.nc` from validated Actions run `41531397166`, artifact `real-western-base-network-attempt`.
- Source family and identity restrictions: [Western network provenance](western_source_network_provenance.json), which explicitly identifies the Breakthrough Energy USATestSystem network as *synthetic*.
- Facility evidence: [three-plant official evidence ledger](../data/eia860_top3_official_transmission_evidence.json) and [previous voltage grading](eia860_source_voltage_vs_synthetic_bus_2024.md).
- Audit module: `src/energy_transition/eia860_archived_candidate_structural_gate.py`; workflow: `.github/workflows/eia860-archived-candidate-structural-gate.yml`.

For the original archived node `2053003`, the gate reads `buses.v_nom` and all incident `Line`, `Transformer` and `Link` `bus0/bus1` edges. It verifies the previously archived **115 kV** source voltage, **two** Line edges to `2053019` and `2053021`, and **zero** incident Transformer edges. It records incident Links separately so no Line-only connectivity observation is presented as a complete electrical graph.

A changed source network, voltage or branch-neighbor identity fails the gate; no EIA-860 Generator components are inserted.

## Official facility evidence compared

| EIA plant | 2024 source nameplate | External source context | Archived candidate `2053003` |
|---|---:|---|---|
| Sagamore Wind (63578) | 522.0 MW | SPP: Crossroads substation 345 kV | synthetic bus nominal 115 kV |
| Hobbs Generating Station (56458) | 681.5 MW | SPP/SPS: named 230-kV receipt point | synthetic bus nominal 115 kV |
| Cunningham (2454) | 444.2 MW | 13.8/20-kV unit-side receipt voltages; **not HV POI** | synthetic bus nominal 115 kV |

Total historical capacity reviewed: **1,647.7 MW**. Current approved electrical generator injections into the source network: **0 MW**.

**Interpretation:** A voltage mismatch at candidate synthetic bus `2053003` does not prove the actual utility station lacks transformer connections or has no alternative POI. A matching voltage also would not prove equivalence. This audit certifies **archived synthetic topology attributes**, not electric generator-to-station identity, calibrated branch ratings, future fleet or operational availability.

## Acceptance and next source acquisition

The [source topology workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/eia860-archived-candidate-structural-gate.yml) must **succeed** before calling the archived-NetCDF comparison source-verified. A successful run authorizes only the synthetic structural findings, not real plant POI approval.

The decisive missing item is a source-compatible **real electrical network** or independently sourced facility-to-network bus/substation crosswalk with utility evidence, exact network vintage, line/transformer details, and per-generator capacity/availability. If unavailable, a defensible fallback is a deliberately coarse zonal *planning* model with clearly labeled assumptions, not an invented real Western AC power-flow model.
