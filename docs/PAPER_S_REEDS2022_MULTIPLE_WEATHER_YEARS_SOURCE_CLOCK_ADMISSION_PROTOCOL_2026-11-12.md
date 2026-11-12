# Paper S — Admission protocol for cross-weather-year original ReEDS resource source experiment (2026-11-12)

## Reason for the gate

The latest source-native EIA 2025 county-siting 24-LP comparison [43159121663](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43159121663) establishes that the illustrative Arizona $10/kWh-year added-storage-energy operating-cost screen changes when only county geography changes: from $10.955400 (potential-weighted) to $9.868276 (EIA 2025 operating county-capacity weights), with 2012 source weather and projected 2030 demand held fixed.

However, that is a *single weather-reference-year* controlled perturbation. Before interpreting cross-year differences as weather sensitivity, we must validate and explicitly document the original source calendar.

The original ReEDS county CF HDF5 products contain 15 weather references (nominal 2007–2021), recorded on the publisher fixed CST source-instant clock. Their 2012 reference segment has 8760 timestamps **including February 29 but omitting December 31**, whereas a conventional nonleap year has 8760 timestamps with no February 29 and includes December 31. Consequently, **pairing years solely by integer hour ordinal would misalign calendar days** and should be disallowed without explicit controlled reindexing.

## Stage W0 — exact source calendar audit (running)

Dedicated source-independent original HDF5 audit [GitHub workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/paper-s-reeds2022-original-15-weather-year-clock.yml). Both original untouched publisher county-class wind/PV HDF5 are authenticated with exact source MD5; each native index_0 is parsed without inferred time-zone localization; year 2007–2021 is inventoried with source rows, native first/last, conventional calendar coverage, presence of leap-day/Dec31 samples and gaps. Wind/PV raw indices must agree exactly. A 30-row year × technology CSV and a machine-readable manifest specify admissible calendars.

This **is not** a multi-weather-year LP. No statistical conclusion is allowed before a later physical and numerical resource extraction and LP pass.

## Stage W1 — proposed calendar-preserving source CF reaggregation, subject to W0

For each independently authenticated weather year, reaggregate original county × resource-class HDF5 CF using (A) ReEDS developable resource county weights and (B) independently observed EIA-860 2025 operating county AC-nameplate shares, with source ReEDS capacity proportions *within county* unchanged. Authenticate all original column identities, supply-curve MD5, exact geography and technology capacity denominator (wind AC, solar raw grid AC / DC array); normalize solar AC **once** via publisher ILR=1.34. Explicit numerical checks must reproduce 2012 frozen potential profiles and 24-LP results.

**Do not silently align raw 8760-element arrays by index.** A defensible illustrative cross-year mapping to the ReEDS 2012 demand reference calendar may map by explicit month-day-hour local fixed CST labels. For nonleap weather years, the absent February 29 should be clearly flagged and treated either as missing/out-of-scope (e.g., skip a leap-day sensitivity) or imputed with a prespecified interpolation from February 28 and March 1 same clock time; December 31 should be removed to match the unusual 2012 8760 reference-day support. If interpolation is chosen, calculate and report its annual energy effect. No source-unobserved leap-day values are observed data, and arbitrary 2012 calendar replacement is not equivalent to a validated contemporaneous 2030 weather/demand match. For leap weather years verify their native 8760 hour records before deciding whether direct month-day-hour matching is available.

## Stage W2 — balanced weather-year LP and interpretation

Only after W0 and W1, compare at least 2011/2012/2013/2014 weather references in a *fixed* common AC nameplate and 2030 source-demand scenario for four states, source potential vs EIA2025 observed county siting, and 0h/4h/8h battery options. This is 4 weather × 4 states × 2 geographies × 3 storage durations = 96 original 8760-interval HiGHS LPs for one fixed engineering/economic scenario, if all source calendars are admitted.

Outputs must include time-calendar completeness and imputation diagnostics, LP feasibility/conservation, 2012 exact frozen anchor, 4h and 8h operating savings, 4→8h incremental energy-only annual annuity threshold and the number of illustrative $10/kWh-year screening flips by weather and county geography. A central/year-spread should be reported as **sample scenario dispersion**, not a predictive confidence interval or future climate probability. Historic source weather years (2007–2021) are not anthropogenic climate projections; the experiment can assess interannual meteorological variability but **cannot by itself quantify climate-change impacts**.

## Separate unresolved physical hour-energy gate

Publisher source weather CF is an **instantaneous point sample**, while modeled demand is hour-ending. The previous 216-LP hold-vs-trapezoid sensitivity is a comparison of numerical approximations, not independent certification that either represents integrated past-hour generation. Full physical-hour validation would require publisher-source semantics or independent hour-integrated renewable energy output. Original ReEDS fixed-CST same-release labels do not authenticate separate EFS2020/ReEDS2022 cross-release time mappings.

## Publication status

Engineering reproducibility with verified original source HDF5 and 2025 EIA siting has been established for the 2012 weather reference. Stage W0 is running; W1/W2 are proposed and not claimed complete. Main text should retain the Arizona spatial-screen reversal as a **conditional structural sensitivity** and leave cross-weather generality and real 2030 installed fleet predictions unproven. PR #2 remains Draft until physical and manuscript admission criteria have been independently reviewed.
