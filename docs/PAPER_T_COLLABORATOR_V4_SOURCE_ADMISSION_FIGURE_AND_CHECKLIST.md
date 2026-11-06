# Paper T collaborator-review v4: Figure T1 source admission and submission checklist

**Internal manuscript:** complete private collaborator-review v4 (not stored in this public repository). The public repository holds a reproducible **Figure T1** and source-backed figures T2/T3/T4, plus transparent evidence limits.

## Newly completed Figure T1

[CI run #42177083314](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42177083314) **passed**, producing `figure_T1_source_admission.svg` and `figure_T1_source_admission.png` in the `paper-t-figure-t1-source-admission` artifact.

- Original EFS2020 `Reference/Moderate` raw state-hour sequence enters its own structural completeness and Idaho sector-reconciliation gate.
- Independently published ReEDS2022 `EFS_REFERENCE` HDF5 enters publisher MD5, native 2012 representative CST clock and per-state hourly checks.
- The independent numerical comparison of 11 states × 3 planning years × 8760 source hours (289,080 value pairs), nonwrapping lag ranking and unresolved Idaho residuals is a **numerical data-comparability result only**.
- **Physical-hour join remains BLOCKED**: original EFS2020 `LocalHourID` source-publisher clock, compatible weather-year mapping, and source geography are not independently authenticated. In particular, ReEDS2022's fixed CST clock cannot automatically be transferred to EFS2020.

The figure is a reproducible source-admission **conceptual flowchart**, not an observed data plot. Script: `src/energy_transition/paper_t_source_admission_flowchart.py`. It uses no invented numeric observations. Avoid misleading readers by plotting a plausible but uncited clock conversion.

## Current full figure ledger

| Figure | Data type | Success / original artifact |
|---|---|---|
| T1 source-admission flowchart | Documented source-gate logic | [CI #42177083314](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42177083314) |
| T2 state shifts and residual MAE | Original EFS2020/ReEDS2022 33 state-year comparisons | [CI #42145896229](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42145896229) |
| T3 separate monthly and clock-hour marginal profiles | Original source residual audit grouped 324 month/hour margins | [CI #42162565936](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42162565936) |
| T4 Idaho frozen Transportation +1 index-hour by evaluation half | Original EFS sector source against independently published ReEDS source | [CI #42145896229](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42145896229) |

**Important T3 limitation:** The archived data are separate monthly and hourly margins, not full joint month × hour cells. A joint residual heatmap cannot be inferred and was not fabricated. The displayed HDF5 clock references are for ReEDS2022 2012 CST, not EFS2020 certified physical UTC.

## Core reviewer/author checks before submission

1. Check that the central result is framed as **cross-release source numerical correspondence and admission constraints**, not physical time-zone correction.
2. Keep the original 2020 EFS and 2022-vintage/2026-deposited ReEDS data publication identities distinct.
3. Preserve the **Idaho unresolved mechanism**, including that the original sector source reconstruction and simple lag perturbations do not prove geographical timezone membership.
4. State the related EFS/ReEDS source lineage, so the comparison of two files is not generalized as independent sampling of all demand databases.
5. Request original publisher/source implementation clarification for EFS2020 `LocalHourID`, hour-end, timezone, leap and weather year. If unavailable, report physical clock admission as unresolved.
6. Confirm actual DOIs, publishers and bibliographic details of each related-work citation and identify journal fit.
7. Archive code/figures and original source hashes in a stable release/DOI, rather than relying on GitHub Actions artifacts that can expire.

**Status:** Figure T1–T4 available through passing CI; Paper T is ready for *collaborator methodological review*, **not** yet an externally submitted article. Paper S remains a separate 540-scenario synthetic renewable-storage LP methods/sensitivity paper; no real wind/solar resource join or Western transmission-constrained OPF is claimed.
