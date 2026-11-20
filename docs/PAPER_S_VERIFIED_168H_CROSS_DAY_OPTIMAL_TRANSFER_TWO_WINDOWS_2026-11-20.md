# Paper S — source-verified input-only 168-hour optimal transfer, two windows (2026-11-20)

## Status and audit
**SUCCESS** GitHub Actions [44678383884](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44678383884), source-pinned artifacts **14606114704** (hours 0–167) and **14606811197** (hours 4320–4487). Both window artifacts were downloaded and directly inspected; each has W0–W3 CSV/JSON outputs, 120 cases and 120 paired horizon records, four state summaries, exactly 15 weather years per state. Across two windows, 240 source case×window rows and 960 LP solves (4 per case). Maximum equality residual < 7.3×10⁻¹² MWh. All 4h vs 8h nested feasible sets, and 24h zero terminal SOC vs 168h zero terminal SOC energy domination gates passed. No economic objective coefficients appear in these source-only transport optimizations.

## Descriptive correlation with frozen full-year LP siting value differences
Values are Pearson r across 15 within-year EIA-minus-potential paired county-weight spatial contrasts. They represent *two 168h windows*, while the benchmark marginal LP values cover the full year; the horizons are mismatched. Neither weather years nor windows are randomized replicates.

| State, R | Window A daily reset r | Window A weekly SOC r | Window B daily reset r | Window B weekly SOC r |
|---|---:|---:|---:|---:|
| AZ 1.5 | −0.1400 | +0.1423 | −0.2225 | −0.1368 |
| CO 2.0 | −0.3486 | −0.0558 | −0.0543 | +0.4484 |
| ID 1.5 | −0.0488 | −0.3454 | +0.2923 | +0.3120 |
| WY 1.5 | +0.2961 | +0.2853 | +0.3582 | +0.2136 |

Same-sign years (week LP spatial effect compared with frozen annual LP):
- AZ R1.5: window A 5/15; B 6/15.
- CO R2.0: window A 2/15; B 12/15.
- ID R1.5: window A 5/15; B 10/15.
- WY R1.5: window A 11/15; B 5/15.

## Physical effect of allowing cross-day SOC
Both durations separately weakly increase optimal shifted MWh with weekly versus daily horizon. However the **incremental 8h minus 4h response need not increase**.
- Window A: 56 cases increased incremental gain, 56 unchanged, **8 decreased**; week-delivered total improved in 31/120 4h and 55/120 8h cases. 49/120 have effectively zero 8h-minus-4h increment even in the weekly horizon.
- Window B: 90 increased, 30 unchanged, none decreased; weekly total improved in 66/120 4h and 90/120 8h cases. 31/120 have zero weekly 8h-minus-4h increment.
- Median weekly-minus-daily incremental gain in MWh, window A: AZ +19,058.19, CO +3,600.63, ID 0, WY 0. Window B: AZ +21,759.15, CO +31,050.44, ID +2,248.79, WY 0.

These source outputs are valid only for prespecified days and zero-initial/terminal SOC. A simple inference that 'cross-day SOC solves CO/ID/WY' is **not supported**. Cross-day availability changes the amount of transfer, but short sampled horizons, fixed calendar support and differing objective functions prevent claiming this mechanism determines the original annual economic value. Time-window sensitivity itself is a relevant negative/falsification result.

## Manuscript decision
- Put the short-window negative/falsification and sensitivity results in supplementary material, not as demonstrated annual mechanism.
- Main text: spatial siting effect depends on wind share and penetration, cost threshold screening is conditional (previous authenticated 213/1080 cases exceed lowest ATB hurdle), while input-only short-horizon energy transfer is insufficient for a stable explanation of annual economic variation.
- The next decisive **predeclared** experiment, if needed for main mechanism, must compare a full 8,760-hour input-only maximum renewable-only shifted energy to a full-year day-reset or 7-day boundary approach on the same 8,760-hour input and same 15 source-year calendar. A two-window regression must not be called an annual result.
- Existing 3×3/ATB artifacts, Paper T and C-2 are untouched.

Original artifact links: [first week](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44678383884) and the two run artifacts numbered above.
