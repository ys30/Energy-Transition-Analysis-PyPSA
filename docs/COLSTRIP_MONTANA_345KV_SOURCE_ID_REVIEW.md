# Montana 345 kV bus IDs — priority upstream substation check

**Evidence:** [verified fast audit #41542400547](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41542400547), network artifact from successful build #41531397166.

The actual source Western network has 10,157 buses, including 295 in Montana. Among these, 24 have nominal voltage 345 kV and **none** has 500 kV. The 24 buses yield multiple shared source-substation IDs; see JSON artifact `colstrip-substation-source-candidates.json`.

The two source-network bus records **2077254** and **2077262** both have `sub_id=39703.0`, nominal `v_nom=345.0` kV, coordinates `x=-106.614, y=45.8831`, `state=Montana`, and two incident network lines each. This is a valuable **source-network station grouping candidate** in southeastern Montana. It is **not a documented Colstrip 500-kV source bus**.

**Next evidence needed:** determine what upstream GIS/grid-source record `sub_id 39703` represents; check station identity and any 345/500-kV transformer and 500-kV bus omission, topology and source vintage. Do not equate geographic proximity or shared source ID with confirmed identity. Do not connect EIA Clearwater plants 66183 or 66811 to either 345-kV node without source-to-model electrical crosswalk and appropriate transformer representation.

**Physical POI documentation:** see [Clearwater regulator-filing evidence](CLEARWATER_COLSTRIP_OFFICIAL_POI_EVIDENCE.md). **Independently verified generator-to-original-PyPSA-bus connections remain zero.**

## Source lineage and coordinate corroboration (2026-11-02)

PyPSA-USA network schema identifies `sub_id` as a **Breakthrough Energy source-substation ID** constructed by `build_base_network.py`. See https://pypsa-usa.readthedocs.io/en/stable/model-network-schema.html . This is not an EIA plant ID and not, by itself, the substation's human-readable name.

The source buses `2077254` and `2077262` have **identical coordinates (45.8831, -106.614) to the publicly reported EIA plant 6076 Colstrip plant location**, reproduced at https://www.gridinfo.com/plant/colstrip/6076 . This provides strong *location corroboration*, but it is not an independently established electrical transformer or source-bus interconnection. The coordinates may represent common source geocoding rather than distinct surveyed substation location.

Model: 345-kV at these two buses; no 500-kV bus in Montana within the currently audited source network. Physical Clearwater POI: Colstrip 500-kV substation. Therefore the **500/345-kV interface or network-model representation is unresolved**. Never assert direct injection of Clearwater CWE/CW3 into buses 2077254 or 2077262 based on coordinate coincidence. The source-network build pipeline may aggregate or omit equipment; upstream Breakthrough Energy bus/substation metadata and transformer tables require inspection.

Next evidence: inspect `n.transformers` and any links at buses 2077254/2077262 and the upstream source substation table for `sub_id=39703`; check exact structural lineage, 345/500-kV relationship and whether the Colstrip project POI is represented in the network at all.

**Verification status:** geographic substation cluster candidate strongly corroborated; exact electrical Clearwater-to-PyPSA link **not verified**.
