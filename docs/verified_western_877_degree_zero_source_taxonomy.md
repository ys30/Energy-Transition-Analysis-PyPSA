# Verified source decomposition of 877 degree-zero Western network buses

**Successful actual archived network CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41780731794

The pinned original Western 10,157-bus PyPSA-USA base topology was loaded from archived run 41531397166. A Line+Transformer-only undirected graph identifies **877** degree-zero nodes. After independently confirming that all **six** archived DC Link components contribute zero new connections to those zero-degree nodes ([actual source Link CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41780445705)), we classify the source attributes of all 877 records.

## Source-verified partition

| Source attribute category | Archived zero-degree buses |
| --- | ---: |
| `substation_off=true` with null original `LAF_state` | **157** |
| Non-offshore, non-null original `LAF_state` | **720** |
| Offshore with non-null LAF | 0 |
| Non-offshore with null LAF | 0 |
| **Total** | **877** |

**The 157 offshore/NULL-LAF auxiliary nodes exactly match the previously traced post-LAF offshore bus generator stage.** However, offshore nodes are **only 17.9%** of the Line+Transformer degree-zero cohort, not an explanation for all 877 records.

The 877-node original Pd partition is: **822 nodes with `Pd=0`**, **55 nodes with `Pd>0`**; the latter total **1,714.97 MW** of archived `Pd`. This is a source coefficient field, not verified stranded or unserved load. The archived base network itself has **zero PyPSA Generator components and zero Load components**, so assigning real dispatch or service-status meaning to these isolated source nodes would be unjustified. No degree-zero node is an endpoint of the six archived Links.

### Source nominal voltage mix

| Archived source bus `v_nom`, kV | Zero-degree nodes |
| --- | ---: |
| 1.0 | 300 |
| 13.8 | 251 |
| 230.0 | 157 |
| 18.0 | 95 |
| 22.0 | 27 |
| 24.0 | 19 |
| 20.0 | 17 |
| 13.2 | 11 |
| **Total** | **877** |

The 157 source-voltage 230-kV nodes are numerically equal to the offshore cohort, but **this univariate coincidence does not prove an intersection** without a bus-level joint cross-tab. The high count of low-voltage zero-degree records motivates a focused audit of source generator-terminal and stub formation rules.

The source-state distribution includes California 458, Washington 81, Oregon 76, Colorado 59, Arizona 53, Nevada 38, Idaho 31, Utah 27, Montana 18, New Mexico 16, Wyoming 12, Texas 8. These are exported network-state labels, not approved load-serving region definitions.

## Engineering interpretation

- Source graph degree-zero `!=` actual real-world disconnected substation, loss of supply, or failed physical Western grid.
- Non-offshore zero-degree nodes **must not be dropped automatically** from real EFS demand maps or network representation: 55 have positive source `Pd` and all 720 have existing source `LAF_state` entries.
- The topology test says nothing about real utility plant interconnection POIs, generator availability, or future capacity. The 5,665 unit EIA-860 2024 historical fleet remains an *external source identity* dataset, and independently verified synthetic-node generator connections remain zero.
- This result helps refine the scientific audit: test exact original bus creation order, bus types and **joint** node categories before model pruning or source-to-PyPSA injection.

## Reproducibility

Code: `src/energy_transition/western_degree_zero_origin_audit.py`; tests: `tests/test_western_degree_zero_origin_audit.py`; GitHub Actions: `.github/workflows/western-degree-zero-origin.yml`. The JSON artifact is `western-real-network-zero-degree-source-taxonomy` in the successful real-network run.

**Next research milestone:** recover source-specific bus types (particularly low-voltage generator terminals), create a bus-level cross-tab with `Pd`, state, voltage, and offshore origin, and validate whether the 55 positive-`Pd` nodes should be held out of empirical EFS mapping. Do not treat the 1,714.97 MW as actual unmet demand.
