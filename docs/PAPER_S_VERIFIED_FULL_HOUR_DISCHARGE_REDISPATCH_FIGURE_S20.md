# Paper S — Verified full-hour window redispatch, source-hour offset localization and Figure S20

**Status:** The original archive-verified six full-year LP dispatch traces and 52,560 hourly rows were reproduced successfully in [GitHub Actions #42851448558](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42851448558). Independent source-derived Figure S20 and gross-vs-net offset audit were validated successfully by [GitHub Actions #42852393262](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42852393262). This study extends accepted Figure S18 and source-hour window discharge bounds.

## Original-source setup

One 2030 EFS source-demand representative from each of the two predeclared original normalized demand groups: Arizona p28 and Wyoming p24. The full original 8,760 EFS `LocalHourID`s were used, with assumed synthetic ordinal Wave A renewable availability, battery power at 25% of local source peak MW and energy capacity equal to one peak-MW-hour. The predetermined discharge window is original **source hour 4001–4168 inclusive**.

For each source zone, reconstruct three independent LP schedules: (1) unmodified original HiGHS optimum, (2) minimize discharge to load in the predetermined source window under `C_original <= C* + max(USD 0.05, 10^-9*C*)`, (3) maximize discharge in the same window under the same cap. Each new candidate must match the previously **accepted actual LP archival** window MWh, full-year MWh and unperturbed variable cost (accepted archive absolute energy tolerance 0.1 MWh), while passing hourly renewable/load/SOC equations and zero terminal SOC. The workflow persisted all hourly charge, discharge, SOC, firm and unused renewable variables.

## New full-hour evidence, difference relative to the original HiGHS schedule

| Source group | Window direction | Change inside 168 source hours (MWh) | Net outside (MWh) | Annual net (MWh) | Gross absolute outside differences (MWh) | Outside hours with |Δdischarge| > 1 MWh |
|---|---|---:|---:|---:|---:|---:|
| Arizona p28 | minimum | −20,118.974 | +20,118.953 | −0.021 | **5,903,051** | 2,278 |
| Arizona p28 | maximum | +9,233.362 | −9,230.115 | +3.247 | **5,886,431** | 2,273 |
| Wyoming p24 | minimum | −260.530 | +260.525 | −0.0048 | **117,751** | 777 |
| Wyoming p24 | maximum | +1,356.224 | −1,356.183 | +0.0403 | **116,075** | 756 |

Here **gross** means `sum(abs(hourly candidate discharge - original hourly discharge))` across all 8,592 original source hours *outside* the selected interval. It is **not** additional storage energy or modeled energy available, and is not the same as the net offset. Positive and negative redispatch within that remainder can nearly cancel. Do not infer transfer from any one particular source hour to another. The annual total remains nearly unchanged even though hour-by-hour solutions can be substantially different.

### Where does net compensation occur?

An additional partition into source-hour ranges reveals a more nuanced result:

- Arizona minimum-window candidate: of the net +20,118.953 MWh outside the window, **+5,161.400 MWh** occurs in original hours **3801–4000** and **+14,597.253 MWh** in **4169–4368**; outside those adjacent 200-hour source ranges, the **net** is ~+360.300 MWh. This near-boundary net pattern coexists with large gross cancellation elsewhere.
- Arizona maximum-window candidate: original hours 3801–4000 contribute ~−9,513.134 MWh and 4169–4368 contribute ~−77.281 MWh; distant outside net ~+360.300 MWh. The total balances approximately −9,230.115 MWh outside the selected window.
- Wyoming minimum-window candidate: adjacent source hours 3801–4000 net ~−184.499 MWh and 4169–4368 +260.525 MWh, with distant outside net +184.499 MWh.
- Wyoming maximum-window candidate: adjacent 3801–4000 net ~−1,231.892 MWh and 4169–4368 approximately zero; distant outside net approximately −124.291 MWh.

These partitions are purely original `LocalHourID` intervals, not physical days, UTC weeks, seasonal diagnostics or geographic transmission flows. The largest net compensating 24h blocks and the complete compressed LP traces are retained in run artifacts; daily blocks overlapping the 168h window are split into inside/outside portions.

## Figure S20 and repeatability

Figure S20 renders net differences against the original schedule in source 24-hour blocks around the fixed study interval (source hours 3601–4560). Four panels show Arizona/Wyoming × minimum/maximum window discharge, shaded around original source hours 4001–4168. The plot is intentionally a **local-window view**, not the whole-year difference, and visualizes signed, not gross, changes. Caption must state that other times also vary.

[Hourly reconstruction and archived LP reconciliation](../src/energy_transition/paper_s_window_hourly_redistribution.py), [CI workflow](../.github/workflows/paper-s-window-hourly-redistribution.yml), [Figure S20 source and gross-net audit](../src/energy_transition/paper_s_hourly_offset_figures.py), [Figure workflow](../.github/workflows/paper-s-hourly-offset-figures.yml).

## Revised Paper S Results paragraph (model-conditional)

> To identify whether apparently stable annual delivered energy masks hourly solution-selection differences, we reconstructed full 8,760-source-hour dispatches at the extrema of a prespecified 168-hour discharge window under a fixed near-optimal original-cost cap. Relative to the original Arizona p28 Wave-A schedule, minimizing window discharge reduced discharge in that interval by 20.119 GWh, nearly balanced by a 20.119-GWh net increase in the other 8,592 source hours. However, the gross absolute difference of discharge across those other hours reached 5,903 GWh, demonstrating substantial, bidirectional, offsetting reallocation across alternative nearly cost-equivalent LP schedules. The large gross difference does not represent net additional generation or grid benefit. Analogous patterns were detected in the Wyoming source-demand representative. These outcomes establish pronounced schedule-selection sensitivity in the **synthetic, source-ordinal LP**, despite stability of annual aggregated dispatch metrics.

## Critical limitations

The original `LocalHourID` index is an ordinal (not certified UTC) and the supply traces are mathematically constructed, not real wind/solar observations. The model is a zonal toy LP without actual interzonal transmission, reserve and reliability constraints, storage investment or degradation costs. The cost tolerance is nonzero, so the experiment is not proof of alternative **exactly optimal** LP faces. This workflow checks three selected schedules per source group: it does **not** compute rigorous pointwise hourly min/max intervals. The seven source-demand shapes are not independent random grid samples.

This newly uncovered gross hourly dispatch degeneracy argues strongly **against** treating single-optimum SOC trajectories, charging events, and selected-hour dispatch as identified outcomes. For a full paper, focus on robust optimal objective and rigorously qualified aggregate metrics; cite this analysis as a supplementary mechanism and nonidentification check. The full paper remains private.
