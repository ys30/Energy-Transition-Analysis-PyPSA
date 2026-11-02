# Real Western network build and Colstrip identity audit — verified results

**Build:** [GitHub Actions run 41531397166](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41531397166) at commit `f7c2ab15`. The actual upstream Western base network build **succeeded**, and the explicit Colstrip bus audit step **succeeded**. Workflow output artifact `real-western-base-network-attempt` (ID 13183711461, archive size 16,829,493 bytes) includes `colstrip-original-bus-identity.json` and other base-network provenance metadata.

**Audit finding:** `explicit_colstrip_name_candidates=[]`, `candidate_count=0`, `coordinate_nearest_bus_inferred=false`, `independently_verified_eia_generator_bus_ties=0`. Name-based screening was performed on the original network bus index and relevant label columns; no exact Colstrip name match was found. Do not interpret a zero named match as proof that the physical Colstrip substation is absent. Model nodes may be numerically identified or spatially aggregated.

**Physical project-level POI:** Clearwater phases have regulator-documentary evidence of connection via the generation tie to Colstrip 500-kV Substation; see [Clearwater POI source notes](CLEARWATER_COLSTRIP_OFFICIAL_POI_EVIDENCE.md). This is not an exact PyPSA bus mapping.

### Required next gate
Inspect original network bus `sub_id`, `substation_off`, voltage, grid graph and underlying substation source lineage; check whether an authoritative Colstrip station identifier from underlying transmission data can be connected to a source bus. Nearby coordinates alone are insufficient. Until a verified source record maps Colstrip to an exact model bus, do not insert Clearwater generators as real-bus injections.

**Conclusion: original Western base network built, but Clearwater-to-PyPSA electrical crosswalk remains unverified.**

## Follow-up: corrected Montana state filter and actual voltage spectrum

[Successful fast artifact audit 41541846957](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41541846957) uses full state name `Montana` rather than only `MT` and inspects the previously successful source Western network (10,157 buses). **Montana has 295 buses, with zero at 500 kV**. Source Montana voltages: 138 kV (212), 13.8 kV (34), 345 kV (24), 18 kV (11), 1 kV (8), 13.2 kV (3), and one each at 24, 20 and 22 kV. The full network contains 174 500-kV buses elsewhere. This is a *model representation gap*, not evidence that Colstrip 500-kV physical POI is nonexistent.

**Implication:** Stop looking for a literal Montana 500-kV bus in this network vintage. Evaluate the upstream network topology and voltage transformation/aggregation source: Colstrip may be absent, modeled at another voltage, or disconnected from identifiable substation metadata. No legal promotion of a nearby 345-kV node to the 500-kV physical POI without an authoritative source crosswalk.
