# Four excluded Western EFS states: source-weight recovery diagnosis

> **Pinned-version correction (2026-11-03):** This project's built Western network uses PyPSA-USA commit `338af9912addbaf038c6098fe27e1e6ef099d8aa`, where `workflow/scripts/build_base_network.py` computes `LAF_state = Pd / groupby(full_state).sum(Pd)`. Later upstream `master` implementations with selectable `load_weight`/population policy are **not** the algorithm used for this archived network. `Pd` is the pinned numerator; `full_state` was dropped from the exported bus inventory. All 157 missing-LAF buses have zero observed `Pd`, but this alone does not independently validate zero future demand or source geography. See pinned denominator audit workflow for further diagnostics.


**Verified initial run:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41756476054

Source: archived 10,157-bus Western PyPSA-USA base network from workflow run 41531397166. This is a **read-only** source inventory, not an independently certified geographic allocation.

| Native state | Buses | Null `LAF_state` | Observed raw LAF sum | Numerical admission |
| --- | ---: | ---: | ---: | --- |
| California | 4,248 | 111 | 0.9994779868 | blocked |
| Nevada | 464 | 0 | 1.0005220132 | blocked (excess) |
| Oregon | 716 | 26 | 0.9981155779 | blocked |
| Washington | 1,114 | 20 | 1.0018844221 | blocked (nulls and excess) |

**Critical data finding:** the archived bus table has `Pd` but **does not contain `load_weight`**. Even though some existing bus `LAF_state` coefficients are numerically valid, the raw `full_state` source denominator cannot be reconstructed from this file. The current audit now also examines the available `Pd` values at null-LAF buses, but `Pd` is legacy nominal base-network demand and **must not be identified as a verified 2030–2050 EFS allocation factor**.

The 70 native-state-to-ReEDS-state mismatches are separate from these missing values. In the four excluded native states, 42 Oregon buses map to Idaho or Washington and eight Washington buses map to Oregon. Comparing LAF totals by native `state` and by `reeds_state` has different semantics.

## Source resolution

1. Recover the **version-pinned, upstream pre-normalization national bus dataset** with `full_state`, `load_weight`, matching bus IDs and the corresponding population or legacy `Pd` input policy.
2. Explain 157 absent bus factors, distinguishing offshore/auxiliary buses and upstream GIS additions by original source IDs; assess `Pd` diagnostics but do not set null LAF to zero merely because `Pd` is zero.
3. Reconcile the full national denominator with the Western subset and the native→ReEDS geographic crosswalk; do not automatically force split-state Western totals to 1.
4. Only admit the four states after independent weight provenance, complete hourly EFS source scope, and conservation against expected geographically covered demand are validated.
5. For newly admitted Pacific-offset states, recompute the real EFS coincident peak sensitivity across +7/+8 hour shifts; the previously successful seven-state pilot has only +7 shifts and cannot show this effect.

No partial-Western load shares have been fabricated or calibrated OPF results claimed.

## Follow-up: all 157 null-LAF buses have zero legacy Pd (verified)

[Western four-state Pd audit #41756661215](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41756661215) passed against the archived actual NetCDF. Every null-LAF bus has a **finite zero** `Pd`: California 111/111, Oregon 26/26, Washington 20/20, Nevada 0 missing. No null-LAF bus has positive, negative, or nonfinite `Pd`. This improves the description of the **archived nominal base-network demand** on those buses, **not** their potential future EFS demand or source-derived `load_weight`.

A newer PyPSA-USA release can use county-population-based `load_weight`, but **this project's pinned source uses `Pd` directly as its numerator**. The exported Western NetCDF does **not** carry `load_weight`. Therefore **do not promote any of these 157 missing LAFs to zero** based only on zero `Pd`; the actual upstream allocation config, `full_state` denominator and national bus preprocessing must be recovered. Nevada's 1.000522 excess and Washington's 1.001884 excess are separate numerical issues.

**Next decisive source check:** independently reproduce the pre-filter national `Pd` and `full_state` denominators for the exact pinned revision, including handling of zero-denominator source groups and subsequent topology additions. No automatic filling is admitted.
