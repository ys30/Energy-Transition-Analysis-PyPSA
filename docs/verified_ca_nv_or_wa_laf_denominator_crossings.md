# Source-denominator evidence: California–Nevada and Oregon–Washington reconciliation

**Actual Western NetCDF evidence:** [pinned Pd/LAF denominator cluster audit #41757260369](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41757260369).

Pinned PyPSA-USA commit `338af9912addbaf038c6098fe27e1e6ef099d8aa` defines `LAF_state = Pd / sum(Pd grouped by full_state)` before dropping `full_state` and applying the final filtered network geography. This is **not** the later `load_weight`/population implementation.

## Two concrete source-denominator crossings

| Current native state | Bus ID | Pd (legacy nominal units) | Inferred denominator | Observed LAF | Matching source denominator |
| --- | --- | ---: | ---: | ---: | --- |
| Nevada | `2030005` | 34.99 | 67,028.96 | 0.000522013171620 | California |
| Washington | `2013019` | 17.49 | 9,281.36 | 0.001884422110553 | Oregon |

All **174** other Nevada positive-Pd/positive-LAF buses use a common inferred denominator **8,033.08**, with their LAF sum **1.0**. The extra Nevada bus contributes exactly **0.000522013171620**, so Nevada's current label-based total is **1.000522013171620**. California's 1,713 positive-Pd/positive-LAF buses use denominator 67,028.96, with total **0.999477986828380**. These two deviations cancel to numerical precision.

All **451** Washington positive-Pd/positive-LAF buses in its main denominator cluster use **16,058.07**, summing to **1.0**. Its additional bus `2013019` with denominator 9,281.36 contributes **0.001884422110553**, producing Washington's observed total **1.001884422110553**. Oregon's positive-Pd/LAF buses use the same 9,281.36 denominator, summing to **0.998115577889447**. Again the two deviations cancel to numerical precision.

The source-denominator matches establish strong **internal numerical evidence** that two buses retained their original denominator even though their exported current state label differs from that denominator's dominant native state. **It does not independently recover the original dropped `full_state` labels or prove the correct final policy for EFS geographic allocations.** Do not recode these buses for empirical state-to-zone demand without independent GIS/official crosswalk evidence.

## Other missing LAF values

All **157** missing-LAF buses in CA (111), OR (26) and WA (20) have finite zero `Pd` in the archived network. There is no positive `Pd` with zero valid LAF in the audited denominator group evidence. The missing LAFs must remain missing until each bus's original role, source denominator and initial graph-augmentation history are independently confirmed. They were not zero-imputed in this work.

## Why this materially narrows the blocker

The Nevada and Washington **overfull** sums can now be explained using two specific source bus IDs and exact denominator-matched LAF mass, rather than a generic numeric tolerance or arbitrary renormalization. The remaining tasks are source geography validation and missing-bus origin tracing, then re-running the source-admission rules against an explicit approved native-source-to-ReEDS mapping. The existing seven-state EFS pilot and 2030/2040/2050 numbers are unchanged; no full Western calibrated OPF is claimed.
