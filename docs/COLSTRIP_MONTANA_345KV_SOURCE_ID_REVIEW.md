# Montana 345 kV bus IDs — priority upstream substation check

**Evidence:** [verified fast audit #41542400547](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41542400547), network artifact from successful build #41531397166.

The actual source Western network has 10,157 buses, including 295 in Montana. Among these, 24 have nominal voltage 345 kV and **none** has 500 kV. The 24 buses yield multiple shared source-substation IDs; see JSON artifact `colstrip-substation-source-candidates.json`.

The two source-network bus records **2077254** and **2077262** both have `sub_id=39703.0`, nominal `v_nom=345.0` kV, coordinates `x=-106.614, y=45.8831`, `state=Montana`, and two incident network lines each. This is a valuable **source-network station grouping candidate** in southeastern Montana. It is **not a documented Colstrip 500-kV source bus**.

**Next evidence needed:** determine what upstream GIS/grid-source record `sub_id 39703` represents; check station identity and any 345/500-kV transformer and 500-kV bus omission, topology and source vintage. Do not equate geographic proximity or shared source ID with confirmed identity. Do not connect EIA Clearwater plants 66183 or 66811 to either 345-kV node without source-to-model electrical crosswalk and appropriate transformer representation.

**Physical POI documentation:** see [Clearwater regulator-filing evidence](CLEARWATER_COLSTRIP_OFFICIAL_POI_EVIDENCE.md). **Independently verified generator-to-original-PyPSA-bus connections remain zero.**
