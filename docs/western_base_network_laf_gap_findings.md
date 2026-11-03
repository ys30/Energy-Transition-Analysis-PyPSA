# Western network LAF gaps: observed evidence and source-resolution queue

**Verified run**: [41733203918](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41733203918) (state and zone counts), [41734329207](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41734329207) (network-component role diagnostics). These refer to the archived **10,157-bus PyPSA-USA Western base network** downloaded from run 41531397166, not an empirically calibrated EFS demand model.

## Missing bus-level factors

Of 10,157 network buses, **10,000 have the three fields populated and 157 have null `LAF_state`**. The required `reeds_state` and `reeds_zone` fields have no null records.

| State | ReEDS zone(s) | Missing LAF buses |
| --- | --- | ---: |
| CA | p9 (79), p10 (23), p11 (9) | 111 |
| OR | p5 (14), p6 (12) | 26 |
| WA | p2 (20) | 20 |
| **Total** | 6 zones | **157** |

The 157 buses have **no attached Load, Generator, StorageUnit, or line/link endpoint in this archived base network** according to run 41734329207. That does not establish they would carry zero demand under an EFS profile: this is a network-building artifact and its component inventory is not evidence for the future geographic allocation. No null `LAF_state` has been filled, zeroed or renormalized.

## Observed raw state LAF sums

These are sums of **only valid observed source-bus values**, not approved Western shares:

| State | Raw LAF sum | Null buses | One-sum check |
| --- | ---: | ---: | --- |
| AZ | 1.000000 | 0 | pass |
| CA | 0.999478 | 111 | fail |
| CO | 1.000000 | 0 | pass |
| ID | 1.000681 | 0 | fail |
| MT | 0.883993 | 0 | fail |
| NM | 0.840724 | 0 | fail |
| NV | 1.000522 | 0 | fail |
| OR | 0.981373 | 26 | fail |
| TX | 0.022867 | 0 | fail |
| UT | 1.000000 | 0 | pass |
| WA | 1.017946 | 20 | fail |
| WY | 0.998845 | 0 | fail |

Some states have no nulls yet deviate substantially from unity, particularly **MT, NM and TX**, showing that the problem cannot be reduced to filling 157 missing values. Potential explanations include partial state geographic coverage or a different normalization/reference population, but neither is demonstrated here. In particular, a Western subnetwork capturing part of Texas must not be scaled to all Texas demand without source evidence.

## Evidence-gated next actions

1. Freeze the upstream source network revision and inspect the original `LAF_state` derivation and construction phases, not merely NetCDF field names.
2. Compare full nationwide or full-state bus inventories and `LAF_state` totals to the Western subset, including excluded state footprints.
3. Identify whether null buses represent auxiliary/synthetic topology elements, before any proposal to exclude them from the allocation denominator. **Do not infer that from absent Load components.**
4. Obtain a defensible definition of region-targeted EFS demand (full state vs Western state fraction). Validate source-vintage compatibility, missing-hour treatment and per-source energy conservation.
5. Only after independent provenance and all membership/crosswalk gates pass may any candidate allocation feed the 35-zone model. The current 35-zone optimal case remains **synthetic**, and the absence of NARIS `p19` interface evidence remains unresolved.

**Status:** upstream LAF geography and empirical EFS admission remain blocked; evidence extraction and diagnosis succeed. No historical Western economic/reliability result is claimed.
