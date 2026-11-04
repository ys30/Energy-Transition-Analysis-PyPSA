# Verified archived Western six-Link DC network topology sensitivity

**Real-NetCDF end-to-end CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41780445705

The pinned archived Western PyPSA-USA NetCDF was loaded directly (10,157 buses; 9,726 Lines; 2,080 Transformers; **6 Links**). The independent module `src/energy_transition/western_link_topology_scope_audit.py` inventories each Link endpoint and static recorded nominal transfer and conversion-efficiency parameters, and tests the change when including Links as undirected edges in an otherwise Line+Transformer graph.

## Archived Link components

| Forward / reverse component pair | Forward endpoints (source bus IDs) | Each-direction nominal p_nom | Each-direction efficiency | Carrier |
| --- | --- | ---: | ---: | --- |
| `9_fwd` / `9_rev` | `2050383` to `2028847` | 2,300 MW | 0.95402833 | DC |
| `10_fwd` / `10_rev` | `2013620` to `2025332` | 3,000 MW | 0.93210701 | DC |
| `15_fwd` / `15_rev` | `2021181` to `2021641` | 375 MW | 0.97798177 | DC |

All six Link components have `p_min_pu=0`, `p_max_pu=1`, and individually oriented `bus0`/`bus1` endpoints. There are **six distinct endpoint bus IDs** and **three reciprocal source-bus pairs**. These model ratings are source component parameters, not validated actual operating limits. Do not add both nominal directional capacities as if they were simultaneous transfer capability.

## Actual graph sensitivity

| Diagnostic | Line + Transformer only | Line + Transformer + Link undirected edges |
| --- | ---: | ---: |
| Connected components in the **descriptive undirected graph** | **879** | **879** |
| Nodes with undirected degree zero | **877** | **877** |
| High-risk candidate node `2053003`, degree | **2** | **2** |
| High-risk candidate node `2053000`, degree | **2** | **2** |
| High-risk candidate node `2077001`, degree | **3** | **3** |

**All six Link components connect nodes that already belong to preexisting connected components of the Line + Transformer graph.** Therefore the undirected graph component count and isolate count do not change. The three high-risk EIA-860 geographic candidate buses are not incident to any Link, and their earlier Line+Transformer results stand unchanged. These are facts about the archived modeled topology **not** proof of real electrical islanding, dispatch feasibility, generator POI, or transmission limits.

### What this resolves and what it does not

This resolves the concern that the earlier 879 graph components and 877 degree-zero nodes might be purely a consequence of excluding the 6 archived DC Links: including the Link endpoints as additional undirected edges leaves both counts unchanged.

It does **not** mean that all 877 undirected isolates are real unserved Western electrical buses. Some source network buses may be offshore auxiliary nodes, or may serve other metadata purposes; we have not yet classified each of the 877 by source formation date and bus types. Nor does static topology confirm AC/DC power-flow feasibility, link efficiencies under full dispatch, or generator-to-bus physical correspondence.

The unrelated 2024 EIA-860 generator nearest-bus crosswalk remains unapproved. The 11-state 2030–2050 EFS demand remains a candidate spatial/time mapping. The authentic historical generator fleet is not yet attached to utility-verified electrical POIs.

## Reproduce

- Real data CI: [run 41780445705](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41780445705).
- Output artifact: `western-real-network-six-link-topology-sensitivity`, file `western_link_topology_scope.json`.
- Code: `src/energy_transition/western_link_topology_scope_audit.py`.
- Tests: `tests/test_western_link_topology_scope_audit.py`.
- Workflow: `.github/workflows/western-link-topology-scope.yml`.

**Next experiment:** classify each of the **877** zero-degree buses by offshore flag, source Pd/LAF, source voltage and generator/load attachment, including a unit-test-guarded count reconciliation. The graph degrees should be evaluated separately from empirical generator and load availability.
