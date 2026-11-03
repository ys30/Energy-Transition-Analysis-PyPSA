# Official facility leads for EIA-860 top-capacity plants (not POI approvals)

> **Important source correction (2026-11-03):** The pinned PyPSA-USA Western base topology is derived from the **Breakthrough Energy synthetic US test system**, not a verified utility-level grid facility database. `sub_id` and bus IDs are **model identifiers**. See [Western synthetic network provenance](WESTERN_SYNTHETIC_NETWORK_PROVENANCE.md). Even a 500-kV bus with matching coordinates cannot establish an actual Palo Verde or Grand Coulee point of interconnection.

The first concrete documentary research leads are in [eia860_official_facility_document_leads_2024.csv](eia860_official_facility_document_leads_2024.csv). These source records link to government/utility documents, **not** verified original PyPSA-USA network-bus mappings:

- EIA plant **6163 Grand Coulee**: [BPA's 21 October 2024 announcement](https://www.bpa.gov/about/newsroom/news-articles/20241021-bpa-takes-ownership-of-switchyards-at-the-grand-coulee-dam) identifies switchyards at **115, 230 and 500 kV**. This confirms switchyard existence, not which specific model bus represents the injection interface.
- EIA plant **6008 Palo Verde**: [DOE EIS-0301](https://www.energy.gov/nepa/eis-0301-nrg-energy-services-inc-arizona-baja-california-500-kv-transmission-line) describes a **proposed** 500-kV transmission line originating at Palo Verde's switchyard. It does **not** establish that the proposed line was built, nor validate any specific model bus.

**Evidence boundary:** These are facility-level documents only. The lead CSV must never be used as input to `eia860_plant_bus_evidence_gate` or `electrical_interconnection_evidence_gate` as reviewed/approved connection records. Every row deliberately has an empty `network_bus_id`, `independent_electrical_bus_match_verified=false`, and an unresolved status. There is no claim of electrical connection to a particular PyPSA-USA bus or availability of full-Western OPF.

**Next verification steps:** trace the source document to a facility's electrical one-line/substation GIS ID and voltage; verify an independently reviewed, version-matched original network-bus ID; then check generator identities, injection voltage, connected components, and operating constraints. For Palo Verde, distinguish proposed from built transmission assets.

Source EIA-860 candidate screening: [successful real-data CI #41667615119](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41667615119).
