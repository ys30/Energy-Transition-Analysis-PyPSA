# Why Western source `LAF_state` does not sum to one by `reeds_state`

> **Pinned-version correction (2026-11-03):** This project's built Western network uses PyPSA-USA commit `338af9912addbaf038c6098fe27e1e6ef099d8aa`, where `workflow/scripts/build_base_network.py` computes `LAF_state = Pd / groupby(full_state).sum(Pd)`. Later upstream `master` implementations with selectable `load_weight`/population policy are **not** the algorithm used for this archived network. `Pd` is the pinned numerator; `full_state` was dropped from the exported bus inventory. All 157 missing-LAF buses have zero observed `Pd`, but this alone does not independently validate zero future demand or source geography. See pinned denominator audit workflow for further diagnostics.


## Upstream code finding (2026-11-03)

In PyPSA-USA [`workflow/scripts/build_base_network.py`](https://github.com/PyPSA/pypsa-usa/blob/master/workflow/scripts/build_base_network.py), `load_weight` is chosen from census population or legacy nominal demand `Pd`; the original `LAF_state` is calculated as `load_weight / sum(load_weight by full_state)` **before** `full_state` is dropped. The network may subsequently be filtered to Western buses, and `reeds_state` is assigned from ReEDS zone membership and county fixes. Neither `reeds_state` nor native `state` in the output necessarily equals the original `full_state` grouping.

In upstream [`workflow/scripts/build_demand.py`](https://github.com/PyPSA/pypsa-usa/blob/master/workflow/scripts/build_demand.py), the demand writer documents a separate per-demand-key LAF normalization. It may also replace missing per-bus factors by zero inside its own disaggregation route; this is **not** a defensible shortcut for this project's empirical 35-zone allocation, absent source coverage and resulting demand-conservation checks.

Therefore, raw `reeds_state` sums far from one in the archived Western network (e.g., MT 0.883993, NM 0.840724, TX 0.022867, WA 1.017946) **cannot by themselves quantify missing future state demand or demonstrate a corrupt LAF computation**. They can reflect a national `full_state` denominator, Western subsetting, reassignment to `reeds_state`, and/or genuine unassigned factors. The original scope must be independently established.

## New source-network diagnostic

`python -m energy_transition.efs_laf_normalization_key_audit` is used from the [Western LAF audit workflow](../.github/workflows/western-source-laf-audit.yml). It compares the two **visible** labels `state` and `reeds_state`, counts disagreements, preserves missing values, and exports the raw observed sums per ReEDS state. It **does not** assert that native `state` equals the dropped upstream `full_state`; nor does it infer, redistribute, zero-fill, or legitimize LAF values.

The separate [Western base-network LAF findings](western_base_network_laf_gap_findings.md) document 157 null factors in CA, OR, WA. All 157 buses lacked attached components in the base-network audit, but this is **not** proof of zero future EFS allocation.

## Required next source-backed step

Recover the complete upstream national bus set **with original `full_state` and `load_weight` before geographic filtering and later assignment** (or independently reproduce its transformation from version-pinned raw inputs). Reconcile the full-state normalization denominator, native-state/ReEDS crosswalk, 157 nulls, actual Western footprint, and 35 NARIS zone membership. Then verify hourly regional load mass conservation against original EFS state demand. No real-demand admission or real transition outcome may be claimed from the currently successful synthetic OPF.

## Verified actual source-to-ReEDS crossing mass (2026-11-03)

From [real Western network CI #41743955102](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41743955102), **70 buses** have distinct normalized native state and ReEDS state. The four groups carry the following original observed `LAF_state` coefficients (not Western-wide demand shares):

| Native state → ReEDS state | Buses | Observed LAF mass |
| --- | ---: | ---: |
| AZ → NV | 20 | 0.000000000 |
| OR → ID | 7 | 0.000680935 |
| OR → WA | 35 | 0.016061224 |
| WA → OR | 8 | 0.000000000 |

None of these crossing records has missing LAF, but the base network still has **157 null LAF buses** elsewhere. A zero factor in a source record is not proof of zero future EFS demand. The LAFs are normalized against upstream `full_state`, and the original national scope remains unverified. The sum of crossing observed LAF is **0.016742158**, not 1.6742% of Western demand.

The new `target_reeds_state_laf_decomposition` audit separates source-native and inbound cross-state factors for each receiving ReEDS state and retains null counts. It is deliberately **not** a historical or future EFS MW transfer estimate. Native-state source demand, original full-state denominators and Western footprint must first be reconstructed.
