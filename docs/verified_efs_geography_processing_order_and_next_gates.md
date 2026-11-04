# Project B — geographic keys and remaining validation gates

**Verified source-order action:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41771311393

The pinned PyPSA-USA source commit `338af9912addbaf038c6098fe27e1e6ef099d8aa` uses **three distinct geographical keys** in a specific, tested order:

1. Initial `full_state`: untrimmed North America Natural Earth 10m administrative polygons; it is the source `Pd` normalization key.
2. Exported `state`: Natural Earth state shapes clipped/filtered by the chosen interconnection (plus missing-attribute nearest-neighbor fills). This is not guaranteed to match the earlier `full_state`.
3. `reeds_state`: derived from ReEDS-zone membership and then reassigned by the mode within `county` to correct disjoint county/zone polygon membership. This is not guaranteed to match exported `state`.

The pinned method performs the original `full_state` and `state` overlays before computing `LAF_state = Pd / sum(Pd by full_state)`. It then drops `full_state`, adds offshore auxiliaries *after* the LAF computation, and later applies county-majority ReEDS membership. A source revision that changes any of these anchor steps now breaks the source-order audit. Source digests are captured in the CI output JSON.

**Independent geographic observations**, not just code semantics: two denominator-crossing buses `2030005` and `2013019` were localized to California and Oregon respectively by both official 2023 Census state boundaries and the named upstream Natural Earth 10m polygon family. Their currently exported states are Nevada and Washington, respectively. Exact original build-time polygons and original full_state labels remain unavailable.

## Result and remaining gates

- The 11-state 2030/2040/2050 EFS zonal time sensitivity is a **candidate engineering analysis**, not a calibrated Western electricity system prediction. Verified annual allocated candidate totals are 768.2468, 848.8846 and 972.2979 TWh, and the +7/+8 pinned fixed-offset peak sensitivity is +23.537, +31.845, +35.970 MW.
- Four-state candidate `Pd/LAF` source-group mass conservation, 157 offshore auxiliaries and two cross-denominator buses are documented. Source GIS evidence is compelling but does **not** establish model approval of the source-to-ReEDS demand key.
- The 2023 Census and newly downloaded Natural Earth shapes do not establish the exact historical shapefile byte identities.
- EFS `LocalHourID` is confirmed complete over 1..8760, and its pinned upstream conversion algorithm has been reproduced, but DST/calendar semantics and alignment with real wind, solar and generation availability remain externally unverified.
- Full Western OPF is **blocked by non-admitted simultaneous supply and demand profiles, network branch/zone compatibility, and empirical calibration**, not a missing synthetic solver smoke test.
- Paper-ready status: provenance and engineering-methods evidence are available; defensible physically constrained 2030–2050 transition results and quantitative discussion have not been established.

**Next milestone:** build a source-verified hourly generator/renewables availability input and its common snapshot contract, then a model configuration admission gate tying temporal, source-geographic, and network-vintage manifests together. A numerical solved dispatch without these checks must still be labeled a synthetic or engineering demonstration.
