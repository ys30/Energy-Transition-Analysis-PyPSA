# Four excluded Western EFS states: source-weight recovery diagnosis

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
