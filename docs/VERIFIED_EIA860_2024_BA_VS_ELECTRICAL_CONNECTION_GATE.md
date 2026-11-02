# Verified 2024 EIA-860 mapping status and unresolved electrical interconnection gate

Evidence: [successful EIA-860 official plant BA mapping workflow 41398661331](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41398661331), run with commit `0b18695896bd8ab98dc4afeb1a4924ae6b982aa8`. Job `inventory-and-mapping (2024)` passed. Associated regression CI [41398685623](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41398685623) also passed.

## Verified log-derived 2024 figures

| Measure | Value | Meaning |
|---|---:|---|
| Operating EIA-860 nameplate | 268692 MW | EIA-860 inventory scope screened by workflow |
| Operating nameplate mapped to BA | 268692 MW | BA label completeness, not electrical grid connection |
| Capacity-weighted BA mapping fraction | 1.0 | Does not establish connected PyPSA Generator components |
| Geographic plant-to-bus candidate pairs | 4043 | Same-state nearest bus candidates only |
| Median candidate distance | 3.286 km | Great-circle distance; not power-line route length |
| Candidate pairs farther than 50 km | 82 | Explicit manual/source review priority |
| Verified electrical plant-bus connections | **0** | No generator-to-network electrical tie has been independently verified |

The source-model network represents another reporting universe and different spatial infrastructure. A high BA coverage percentage is not proof that generator fuel, connection bus, chronological availability, or marginal cost can be used for realistic OPF.

## Research admission and next steps

1. Keep geographic candidate buses in separate **evidence-only** tables, never create physical generator components from nearest-bus proximity alone.
2. Prioritize official interconnection evidence for the 82 pairs over 50 km and materially different main-grid alternatives; preserve plant IDs, generator IDs, BA, state, coordinates, candidate bus, original data row and independent connection source.
3. Evaluate alternative physical network matching evidence: official EIA plant/geographic coordinates only establish location, not bus-level electric connectivity; known GIS substation location is also insufficient unless tie evidence is documented.
4. Until validated, future optimization scenarios must label their generators as illustrative and exclude any claims of calibrated real EIA-860 dispatch or emissions.
5. Preserve year scope (2023 versus 2024) in comparisons and do not equate EIA-860 end-of-year nameplate with dependable hourly dispatch.

**Gate outcome:** EIA-860 inventory and BA source-mapping pipeline is verified; real generator-to-bus connections are **not admitted**, and calibrated generation dispatch remains blocked.
