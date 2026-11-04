# Three high-capacity EIA-860 source plants: graded SPP evidence, no synthetic POI admission

**Verified evidence-ledger CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41775561325

This ledger extends the official 2024 EIA-860 name/coordinate audit of 63 high-risk geographically distant plants (run 41774793024) with publicly accessible SPP documents. It compares original plant name and historical nameplate **without** claiming that the synthetic-topology PyPSA bus `2053003` represents a utility-owned or approved real substation.

| EIA plant ID | Official 2024 plant name | Screened historical nameplate | Candidate synthetic bus | Public SPP evidence | Evidence category |
| --- | --- | ---: | --- | --- | --- |
| `63578` | Sagamore Wind | 522.0 MW | `2053003` | GEN-2016-123-124-125 Sagamore Wind Farm 522 MW, SPS Crossroads 345-kV substation | Project and named substation; exact EIA ID to queue request unresolved |
| `56458` | Hobbs Generating Station | 681.5 MW | `2053003` | SPS network service **receipt point** listed with Hobbs Generating Station, 230 kV | Named service-point and voltage; not a verified generator electrical POI |
| `2454` | Cunningham | 444.2 MW | `2053003` | SPS receipt-point rows list Cunningham units 1,3,4 at 13.8 kV; unit 2 at 20 kV | Named unit-side receipt voltages; **not** the high-voltage generator step-up or station connection |

The three source EIA records sum to **1,647.7 MW of 2024 nameplate capacity**, which **must not** be interpreted as future dispatchable MW or as physically installed capacity on the PyPSA synthetic node.

## Public original documents

- [SPP 2025 Shared Network Upgrade Facilities Construction Agreement (ER26-290)](https://spp.org/Documents/75146/20251029_3978R1_Tip%20Top%20%26%20SPS%20%26%20PSCoOK%20Shared%20Network%20Upgrade%20FCA_ER26-290.pdf), Appendix A, Sagamore Wind nameplate and Crossroads 345-kV named substation. The shared network-upgrade agreement is a facility-level project record, not the EIA plant ID ↔ PyPSA bus crosswalk.
- [SPP/SPS Network Integration Transmission Service Agreement, transmission service receipt-point appendix](https://www.spp.org/documents/74457/20270731_1910r28%20sps%20nitsa%20noa_er25-3059.pdf), dated **July 31, 2025 in the filing content** (the hosted PDF URL filename contains a different date-like prefix). Lists the Hobbs and Cunningham receipt-point voltages in an appendix. It is **not** a physical electrical one-line diagram. The public PDF text is indexed by search, but a separate original-PDF visual rendering could not be completed in the external web interface, so exact table placement should be double-checked before publication-grade citation.
- [SPP active interconnection request listing](https://opsportal.spp.org/Studies/GIActive) provides separate prospective projects and request statuses. Similarly named substations appearing on newer applications are **not** confirmation of the operating EIA generators' own POIs.

## Evidence-level contract

New JSON ledger: `data/eia860_top3_official_transmission_evidence.json`. Audit: `src/energy_transition/eia860_spptop3_poi_evidence_gate.py`. Tests: `tests/test_eia860_spptop3_poi_evidence_gate.py`. CI: `.github/workflows/eia860-spp-top3-evidence.yml`.

The CI enforces:
- All three EIA 2024 IDs, official facility names, original historical nameplate values and synthetic *candidate* bus IDs are exactly as previously audited.
- Sagamore: source names a 345-kV substation, **but original EIA plant-ID ↔ SPP GEN request linkage is not marked verified**.
- Hobbs: 230-kV service receipt point evidence only, not an authenticated unit-to-station electrical connection.
- Cunningham: 13.8/20-kV receipt/unit voltage data only; no fabricated high-voltage POI.
- `synthetic_bus_electrical_connection_verified=false` for all plants, and future 2030–2050 generator capacity admission stays false.

## Next step with highest research value

Resolve the original **SPP interconnection queue request → actual EIA plant identifier** correspondence, then obtain utility-backed line/substation topology or an approved GIS crosswalk tied to the exact PyPSA-USA network vintage. Prioritize the 21 plants sharing candidate bus `2053003` and the other two top collision groups. **Do not** force 1,647.7 MW of generation into a single synthetic PyPSA bus; this would create a spurious physically constrained dispatch and undermine the manuscript.

**Current verified state:** three names with graded external evidence; zero independently approved synthetic-model generator connections; no authenticated 2030–2050 Western generation OPF.
