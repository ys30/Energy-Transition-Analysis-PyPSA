# Real Western network build and Colstrip identity audit — verified results

**Build:** [GitHub Actions run 41531397166](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41531397166) at commit `f7c2ab15`. The actual upstream Western base network build **succeeded**, and the explicit Colstrip bus audit step **succeeded**. Workflow output artifact `real-western-base-network-attempt` (ID 13183711461, archive size 16,829,493 bytes) includes `colstrip-original-bus-identity.json` and other base-network provenance metadata.

**Audit finding:** `explicit_colstrip_name_candidates=[]`, `candidate_count=0`, `coordinate_nearest_bus_inferred=false`, `independently_verified_eia_generator_bus_ties=0`. Name-based screening was performed on the original network bus index and relevant label columns; no exact Colstrip name match was found. Do not interpret a zero named match as proof that the physical Colstrip substation is absent. Model nodes may be numerically identified or spatially aggregated.

**Physical project-level POI:** Clearwater phases have regulator-documentary evidence of connection via the generation tie to Colstrip 500-kV Substation; see [Clearwater POI source notes](CLEARWATER_COLSTRIP_OFFICIAL_POI_EVIDENCE.md). This is not an exact PyPSA bus mapping.

### Required next gate
Inspect original network bus `sub_id`, `substation_off`, voltage, grid graph and underlying substation source lineage; check whether an authoritative Colstrip station identifier from underlying transmission data can be connected to a source bus. Nearby coordinates alone are insufficient. Until a verified source record maps Colstrip to an exact model bus, do not insert Clearwater generators as real-bus injections.

**Conclusion: original Western base network built, but Clearwater-to-PyPSA electrical crosswalk remains unverified.**
