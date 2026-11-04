# Project B — source-level audit of the 720 non-offshore degree-zero Western nodes

## Existing verified facts (before the new joint audit)

The original PyPSA-USA topology has **10,157 buses**, **9,726 Lines**, **2,080 Transformers** and **6 DC Link components**. The Line+Transformer graph has **877 degree-zero nodes**; adding the six Links as undirected edges does not change this number. Of the 877 source nodes, **157** are post-LAF offshore auxiliaries with missing `LAF_state`, while **720** are non-offshore nodes with non-null LAF. These cohorts and their exact counts passed [CI 41780731794](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41780731794) and [CI 41780445705](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41780445705).

The archived degree-zero population includes **822 `Pd=0`** rows and **55 `Pd>0`** rows with **1,714.97 MW** in the original source `Pd` column. This column was imported by the pinned upstream code as a demand *allocation coefficient*; it is not a solved dispatch, measured served load or unmet demand.

## Important pinned upstream semantics

Pinned PyPSA-USA `workflow/scripts/build_base_network.py` at `338af9912addbaf038c6098fe27e1e6ef099d8aa` directly maps a source bus `baseKV` into `v_nom`, and source `Pd` into the bus field `Pd` with an explicit comment that it is `used to decompose zone demand to bus demand`. A low source `baseKV` is *compatible with* unit-terminal or network auxiliary voltage, but **low voltage alone is not a recovered bus-equipment type**. The source `sub_id` and the separate later offshore-bus creation rule should therefore remain available in audit output.

The pinned code marks `substation_off` from `sub_id >= 41012` for part of the original source pipeline and separately appends offshore buses after original state LAF normalization. Thus the label `substation_off` is meaningful as a source-process flag, but it is **not** sufficient by itself to certify a bus as physically an offshore wind generator terminal. No graph nodes are deleted or repaired based on this categorization.

## New reproducible experiment

- Source: `src/energy_transition/western_zero_degree_joint_source_audit.py`
- Tests: `tests/test_western_zero_degree_joint_source_audit.py`
- CI: `.github/workflows/western-zero-degree-joint-source.yml`
- Real-network CI run: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41862652028

The new job emits three artifacts from the pinned original network: `western_degree_zero_voltage_pd_origin_cross_tab.csv` with a joint `offshore × v_nom × Pd positive/zero × LAF missing/present` cross-tab; `western_55_positive_pd_zero_degree_bus_review.csv` identifying original buses for source-examination; and `western_degree_zero_voltage_pd_source_summary.json` with audited source cohort totals, plus a boolean indicator for source `sub_id >= 41012`.

**Completion gate:** real 10,157-bus source archive; exactly 877 Line+Transformer degree-zero nodes; exactly 157 offshore and 720 non-offshore; exactly 55 positive-`Pd` nodes totaling 1,714.97 source MW; no unsafe claim that the nodes are generator terminals, outages, or certified physical buses to delete.

## Next data-admission decisions

1. Recover detailed source bus equipment and transformer/branch terminal records corresponding to the **55** positive-Pd nodes; document whether their absence from the branch graph is an intended intermediate-system representation, an excluded voltage level, or a mapping error.
2. Distinguish offshore auxiliaries and onshore low-voltage buses with a joint `v_nom`/offshore/Pd table; avoid concluding that all 230-kV zero-degree nodes are offshore merely because both totals equal 157.
3. Check whether active allocated EFS zone load ever maps to the 55 zero-degree buses, and if so quantify **scenario demand at those source nodes** separately by 2030/2040/2050; do not treat original `Pd` as the EFS load itself.
4. Any pruning or reconnection of these 720 onshore source nodes requires validated original bus and branch semantics; in particular, **do not drop 55 positive-Pd rows or silently normalize them away**.
5. Full 11-state scenario OPF remains blocked on source-qualified generator electrical POI, supply profiles, UTC alignment and real branch constraints. This is a topology data-engineering validation, not a simulated energy-transition result.

**Status:** existing 877-node results empirically verified; new joint cross-tab and 55-row review list are submitted to CI and should be treated as pending until the job succeeds.
