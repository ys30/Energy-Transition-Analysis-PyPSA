# Papers T/S — Collaborator review evidence and bibliography check (2026-11-05)

This public memo contains **only** source provenance, evidence state and reference checks. The complete edited English paper drafts are private and are not committed.

## Paper T: three original-source figures ready for coauthor inspection

- [Paper T Figures T2 and T4, CI #42145896229](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42145896229): source-value lag/error comparison and 2030-frozen Transportation +1 source-index-hour train/holdout differences. Source archives: nonwrapping 33 state-year original-data run #42122065064 and Idaho transfer #42131969905.
- [Figure T3, CI #42162565936](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42162565936) **passed**: `figure_T3_idaho_month_hour_marginals.svg/png` in artifact `paper-t-idaho-reference-month-hour-marginal-figure`. It uses the originally verified grouped source data from #42125517759, 324 rows for 3 years × 3 states × (12 months + 24 clock hours). The data contain **monthly and hourly margins separately, not 12×24 month–hour joint cells**. Therefore **no joint heatmap is claimed, shown, or fabricated**. Idaho, Arizona and California control curves are shown by published **ReEDS 2022 2012 CST reference labels**, never certified EFS2020 physical time.

**Final figure lineup:** T1 provenance/admission flowchart (still to author); T2 source lag and error (passed); T3 monthly/hour marginal residual (passed); T4 frozen source-index shift window comparison (passed). Large 33-pair source table should be supplementary; main text should stay about the broader temporal admission problem, with Idaho as a falsification test.

## Verified official dataset citation and semantics

1. **2020 EFS Reference/Moderate source**: National Laboratory of the Rockies catalog, *Electrification Futures Study Load Profiles*, DOI [10.7799/1593122](https://doi.org/10.7799/1593122). Catalog lists original `EFSLoadProfile_Reference_Moderate.zip` release date January 14, **2020** and 2026 catalog update. Original published aggregation dimensions are state, sector and select subsector. Its public catalog **does not certify** the original `LocalHourID` physical UTC or weather-year.
2. **ReEDS demand 2022 product**: Murphy, Mai, Jadun, Ho, McMillan and Mayernik, [*ReEDS: Electricity demand profiles 2022*](https://doi.org/10.5281/zenodo.18461543), deposited to Zenodo **February 4, 2026**, version 1. The dataset **title** includes 2022 but publication date is 2026. Publisher declares modeled state gross end-use load (MWh/h), hour-ending values, full 2012 representative weather/calendar fixed **Central Standard Time UTC−06**, and December 31 dropped to give 8760 hours. These metadata **cannot be asserted for the distinct original 2020 EFS source**. Exact official HDF5 original MD5: `7b2055d43200744a16a8c4fed68b1a17`. CI independently authenticated it.

## Literature additions to private drafts — source-checked, not overstated

- Ruggles, Farnham, Tong and Caldeira (2020), [*Developing reliable hourly electricity demand data through screening and imputation*](https://doi.org/10.1038/s41597-020-0483-x), *Scientific Data*. Relevant to data quality, **not** an existing cross-release EFS clock-correction demonstration.
- Shaffer (2019), [*Location matters: Daylight saving time and electricity demand*](https://doi.org/10.1111/caje.12407), *Canadian Journal of Economics*. Relevant evidence that load response to clock policy can depend on geography, **not** proof of Idaho's cross-release cause.
- Lozano Medina et al. (2026), [*Solar-time reconstruction of electricity demand*](https://doi.org/10.1016/j.ecmx.2026.101803), *Energy Conversion and Management: X*. Conceptual distinction between legal, solar and DST time coordinates; it does **not** authorize using solar-time corrections to rectify the original EFS source.
- Frew and Jacobson (2016), [*Temporal and spatial tradeoffs in power system modeling with assumptions about storage*](https://doi.org/10.1016/j.energy.2016.10.074), *Energy*. Source-checked DOI; relevant to storage chronology effects.
- Merrick, Bistline and Blanford (2024), [*On representation of energy storage in electricity planning models*](https://doi.org/10.1016/j.eneco.2024.107675), *Energy Economics*. Relevant to Paper S storage chronology and temporal planning representation.
- Shirizadeh and Quirion (2022), [*Do multi-sector energy system optimization models need hourly temporal resolution?*](https://doi.org/10.1016/j.apenergy.2021.117951), *Applied Energy*. Relevant to Paper S's temporal simplification literature.

## Paper S: no new empirical generator results

The [independent source-backed 540-case audit #42146086492](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42146086492) remains successful. The **exact** implemented linear objective is `5*(renewable_direct_mwh + storage_charge_input_mwh) + 90*firm_generation_mwh` for **each LP case**. The battery charge and discharge efficiency are each `sqrt(0.90)`, so with zero initial and terminal state the annual discharge MWh equals 90% of charged input MWh, up to solver numerical tolerance. Each of the 20 EFS zones is optimized independently; renewable hourly availability, battery and firm prices, capacity and shape are illustrative assumptions, and no physical Western OPF is established.

**External submission readiness:** Paper T is ready for initial **collaborator review**, not journal submission; Paper S needs more substantive empirical validation for an applied energy claim. Neither private manuscript is published through this repo. A permanent archival dataset/figure DOI and source lineage check remain to complete.
