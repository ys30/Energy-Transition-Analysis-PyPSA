# Paper S — prespecified 2023 12-month EIA-860M operating generator BA-code population audit

**Date:** 2026-11-18. **Status:** protocol/code committed, awaiting source-backed GitHub Actions completion. Do not claim 12-month capacity results before 12 original official workbooks pass download and validation.

## Key correction to earlier full-year diagnostics

Prior 2023 BA EIA-930 net-generation data now cover 8 BA×technology series throughout 8,760 UTC hours (source audit run 44246001519, artifact 14406998900). Historical monthly 2023 BA *generator* capacity must be sourced from its **own corresponding month**, not extrapolated from July EIA-930A or the later 2025 EIA-860 survey. The previously computed **324 July candidate-capacity breach hours** remain a reproducible July SCH2-subset screening result, not an estimate of 2023 annual breaches.

The new workflow [#44391834613](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44391834613) independently downloads every original 2023 EIA-860M monthly XLSX using the official archive's `{lowercase_month}_generator2023.xlsx` naming pattern. It records every SHA-256, validates month-specific source schema and the already verified July SHA-256 `9a7b3f4051f1edb55f4d6508a1b963d2b344d687de6ea464ac538f2929122510`, and fails closed if any source is absent. EIA-860M is **preliminary** and a census of generators, not of BA hourly physical measurement membership.

## Scientific prespecification

- Population: original `Operating` (main US; not `Operating_PR`) sheet each month, source **Plant ID + Generator ID**, source **Balancing Authority Code**, original **Plant State**, and `Nameplate Capacity (MW)`. Distinguish `(OP) Operating` from standby or other statuses.
- Technologies: `Solar Photovoltaic` treated as solar PV; `Onshore Wind Turbine` and `Offshore Wind Turbine` treated as wind; **Solar Thermal with Energy Storage is not silently conflated with PV**.
- Cohorts: PNM, PSCO, IPCO, WACM, wind/solar, January–December 2023: **96 month×BA×fuel generator census rows** and **192 observed reported/adjusted paired diagnostic rows**.
- Preserve original reported EIA-930 BA net MW and separately source-adjusted MW; no zero filling, denominator clipping, spurious smoothing, BA-to-state conversion, or p-value tuning.
- Report number of hours when the **source BA net MW aggregate** exceeds the *candidate EIA-860M operating generator subset* nameplate MW for that specific source month. This is a **necessary-coverage challenge**, not proof of a physically impossible machine, verified observed CF or true BA reporting footprint.
- Explicitly report cross-state `Plant State` breakdown for each BA, and original source-operating status and commissioning date; if duplicate generator IDs appear within the month, fail rather than count twice.
- Source-pin actual full-year observed EIA-930 GitHub artifact 14406998900. Do not modify prior 1440 original Paper S LPs, 360 new 2×2, 2880 new 3×3, 2160 ATB, or Paper C-2.

## Required before manuscript admission

1. Source run must succeed, yielding authentic 12 original source SHA-256s, 96 monthly BA×fuel fleet records, geographic breakdown and 192 BA peak/exception metrics.
2. Validate July 2023 PSCO/WACM source-nameplate anchors against the independently verified EIA-860M July source (91 PSCO PV generators 1666.9 MW, 22 WACM PV generators 161.9 MW), with a documented difference if monthly scope differs.
3. Explain whether PNM July solar 580 MW EIA-930 reported peak versus 544 MW older `SCH2` subset is resolved by contemporaneous EIA-860M BA census, **without presuming that BA-code generator inventory equals EIA-930 net-generation contributors**.
4. Confirm PSCO/WACM July solar original BA capacity gap sensitivity and seasonal trend under reported vs adjusted variant.
5. Only after evidence is assessed decide whether any empirical validation can be admitted to main manuscript; otherwise retain this as a source/measurement caveat in SI.

**No numerical outcome beyond existing verified July source and EIA-930 archive facts is asserted in this protocol.**
