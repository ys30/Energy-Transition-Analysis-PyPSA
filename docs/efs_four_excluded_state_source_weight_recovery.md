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

## Follow-up: all 157 null-LAF buses have zero legacy Pd (verified)

[Western four-state Pd audit #41756661215](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41756661215) passed against the archived actual NetCDF. Every null-LAF bus has a **finite zero** `Pd`: California 111/111, Oregon 26/26, Washington 20/20, Nevada 0 missing. No null-LAF bus has positive, negative, or nonfinite `Pd`. This improves the description of the **archived nominal base-network demand** on those buses, **not** their potential future EFS demand or source-derived `load_weight`.

The original pinned PyPSA-USA LAF generation can use county-population-based `load_weight` rather than legacy `Pd`, depending on the upstream `electricity.demand.bus_allocation` setting. The exported Western NetCDF does **not** carry `load_weight`. Therefore **do not promote any of these 157 missing LAFs to zero** based only on zero `Pd`; the actual upstream allocation config, `full_state` denominator and national bus preprocessing must be recovered. Nevada's 1.000522 excess and Washington's 1.001884 excess are separate numerical issues.

**Next decisive source check:** recover the exact pinned input configuration for run 41531397166; if it specifies population, reconstruct county-population `load_weight` and source `full_state` before any missing-weight resolution. If breakthrough, independently reproduce the original pre-filter `Pd` normalization before considering any zero-LAF classification. Neither branch is yet certified.
