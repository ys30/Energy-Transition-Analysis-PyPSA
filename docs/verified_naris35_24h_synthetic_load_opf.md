# Verified NARIS Western membership 24-hour OPF (synthetic load and generation)

**Evidence:** [GitHub Actions run 41716290974](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41716290974) completed successfully at commit `7890688bdc82dcb2e241fa6f20da76115c84ced7`. Independent main-CI syntax and regression checks subsequently passed in [run 41716345808](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41716345808), commit `9e32f1a5fe40a187e9801a882e43cbec2bf69ad0`.

## What was solved

The 24-snapshot linearized PyPSA optimization used **35 Western membership zone buses** and **131 source-backed NARIS directed zonal transfer Links**. The original 34-zone connected topology was augmented with the missing, **isolated p19 zone**. This adds no invented transmission interface. The test's time labels, zonal hourly demand profiles, low-cost central generation, local backup capacities, and unit costs were **hypothetical**. These are neither actual 2024 operating observations nor a historical NARIS/WECC calibration.

## Confirmed numerical evidence

| Verified output | Value |
| --- | ---: |
| Snapshot count | 24 |
| Western membership buses | 35 |
| Directional NARIS transfer Links | 131 |
| Isolated buses | p19 only |
| Central hypothetical supply bus | p1 |
| Total scenario load | 42,840 MWh |
| Optimized scenario generation | 42,840 MWh |
| Total hypothetical local backup generation | 816 MWh |
| p19 hypothetical load | 816 MWh |
| p19 hypothetical local generation | 816 MWh |
| Maximum absolute nodal power-balance residual | 1.8189894035458565 × 10^-12 MW |
| Solver status / termination | ok / optimal |
| Optimization objective | 123,624 synthetic cost units |

All **816 MWh** of local backup is needed at isolated p19 in this
synthetic fixture; this is **not** historical Western electricity shortage,
unserved load, or transmission-congestion cost. The model equips p19 with an
invented local dispatchable generator; it does not demonstrate that an
authentic p19 generating facility exists. The central generator is located on
connected bus p1. The objective uses arbitrary modeled unit costs (1 for
central and 100 for backup), and **must not be expressed as USD**.

The isolated zone accounts for approximately **1.90%** of scenario load
(816 / 42,840). This fraction is specific to the invented profile, not an
empirical regional allocation.

## Interpretation boundaries and remaining data gates

1. NARIS capacities are published planning **directional zonal Links**, not validated historical electrical AC Line parameters, and 131 directed Links are not 131 physical transmission lines.
2. The isolated p19 zone has no confirmed NARIS interface in this source inventory. Do not silently connect it, exclude its load, or interpret its local backup as congestion relief.
3. The successful solver and conservative conservation checks establish an **engineering integration milestone only**. They do not authenticate hourly demand, state-to-ReEDS-zone weights, generator interconnections, historical demand balance, marginal costs, or 2024 physical grid behavior.
4. Before any empirical claim, independently validate source vintages/hashes and zone membership, obtain authoritative demand-allocation factors, reconcile annual and hourly source demand, admit generator capacity/fuel/cost mapping, and audit boundary interchange and zonal energy conservation.
5. Only after those gates should the paper compare real-data-backed transition, storage, and transmission scenarios with transparent uncertainty and model limitations.

**Reproduction entry points:** `.github/workflows/naris2024-34zone-loaded-opf.yml`,
`src/energy_transition/naris2024_synthetic_24h_load_fixture.py`, and
`src/energy_transition/naris2024_loaded_dispatch_integration.py`.
