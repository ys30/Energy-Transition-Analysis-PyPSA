# Paper S — author declarations, licensing and durable archive readiness
Version: 2026-11-13. **Editorial template, NOT author-approved publication declarations.**

## Article identity (verified study wording)

**Working title:** Weather-Dependent Storage Duration Value under Renewable Resource Potential versus Observed County Siting: A Source-Audited Four-State U.S. Dispatch Study

**Article type:** A controlled, source-audited, scenario-based method/sensitivity study; not an observed 2030 electricity-system valuation, projected climate-change experiment, PyPSA network optimization, or a battery investment NPV study.

**Model:** Custom SciPy HiGHS state copperplate linear program; no nodal transmission or adequacy model. Empty initial and terminal storage SOC.

**Source-year basis:** 2010–2013 weather references, 2025 EIA observed operating renewable county capacity fractions, fixed modeled 2030 load. The four years are not four forecasts of 2030 weather.

**Numerical sensitivity:** 96 scenario LPs × 2 distinct point-CF-to-hour approximations = 192 LP solves, not independent observations. Observed instantaneous reference source points are NOT certified hourly-integrated renewable energy. AZ 2012 USD 10/kWh-year binary cost-screen change is limited to trapezoid treatment; it does not persist under endpoint hold.

## Author-supplied submission fields — explicitly unresolved

| Submission item | Required author-provided information | Current disposition |
|---|---|---|
| Full author list and ordering | Exact legal/published names, approvals by every author | NOT PROVIDED — do not guess |
| Affiliations | Institution names at study time, addresses, corresponding author email | NOT PROVIDED |
| Contribution statement | CRediT roles per named contributor and approvals | NOT PROVIDED |
| Funding | Award/funding sources and exact grants, or an author-approved no-external-funding declaration | NOT PROVIDED |
| Conflicts of interest | Each author's disclosure, or confirmed none | NOT PROVIDED |
| Acknowledgments | Permissions from anyone named | NOT PROVIDED |
| Ethical approval and consent | Journal-applicable determination for use of published energy datasets, confirmed by authors | NOT CERTIFIED |
| AI-tool usage statement | Applicable journal-policy-compliant factual description approved by authors | NOT PROVIDED |
| Target journal | Exact journal and current author instructions, article type, template, limits, data policy | NOT SELECTED |
| Corresponding author | Name/email and explicit approval | NOT PROVIDED |
| Source license & redistribution | Check each ReEDS Zenodo record, EIA release, Census source and derivative rights separately | NOT CLEARED |
| Code license | Check repository license and rights of all original/third-party code | NOT CLEARED |
| Long-term source release | Tagged source commit, pinned datasets, derived CSV/JSON, methods, hash manifest, license scope | NOT CREATED |

**Never auto-fill any item as “None”, “Not applicable”, or “No conflict” simply because the research is public or code is accessible.**

## Reproducibility and permission ledger

| Item | Source | Evidence to pin | Permission caution |
|---|---|---|---|
| ReEDS onshore wind profiles | https://doi.org/10.5281/zenodo.18422200 | Publisher-version file, MD5/source manifest and native calendar audit | Publisher file license must be separately verified |
| ReEDS utility PV profiles | https://doi.org/10.5281/zenodo.18407660 | PV HDF5 MD5, ILR=1.34 AC basis and source class/county joins | Do not assume AC and DC MW are interchangeable |
| ReEDS electricity demand 2022 | https://doi.org/10.5281/zenodo.18461543 | Product version, MD5, fixed CST reference and hour-ending semantics | Matching labels do not certify hourly production integration |
| EIA-860 annual 2025 | https://www.eia.gov/electricity/data/eia860/ | Operable OP status selection, technology filtering, plant-county crosswalk | Observed 2025 geography is not forecast 2030 fleet |
| Census county FIPS 2020 | https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt | Exact FIPS join QC | Respect source notices and attribution |
| Research computations | [24 LP](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43159121663), [96 LP](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182390), [192 LP](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43317414772) | Original archive files, checksum per internal file and source commit | Do not interpret a temporary Actions artifact as permanent preservation |
| Figure evidence | [source-validated figures](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43288856607) | Exact figure script, original input table and figure files | Label trapezoid-mode uncertainty |
| Manuscript DOCX | [Word run 43553837321](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43553837321) | Extract specific DOCX, SHA-256, actual visual inspection | No inference about final publisher typesetting from CI alone |

## Final journal submission decision gates

1. **Physical input gate:** choose to obtain independent physically hour-integrated renewable generation or limit the paper consistently to numeric source point-to-hour approximation. Cite the limitation in Abstract, Methods, Results, Discussion and captions.
2. **Reproduction gate:** every paper number is traceable to the original 24/96/192 LP archived CSV/JSON and corresponding pinned code, with checksums; never silently recompute or substitute values.
3. **Editorial gate:** inspect final exact DOCX/PDF pages, accessibility/figure legibility, bibliography completeness, and native-editable-equation requirements.
4. **License gate:** document separately verified permissions for redistributed original input data, derived outputs, original code, charts and third-party assets. Do not declare the whole mixed ZIP CC BY without file-scope review.
5. **Author gate:** explicit author signoff on title, affiliations, funding, conflicts, contributions, source limitations and target journal.
6. **Release gate:** freeze one tagged commit and long-lived archive with complete hash manifest and DOI; verify it is public or embargoed according to the selected journal policy and authors' decisions.
7. **Status gate:** keep current PR Draft until all relevant scientific and editorial conditions are met. Green CI and a generated Word file alone cannot close the physical integration uncertainty.

## Concise submission-safe study description

> We report a reproducible, source-audited sensitivity analysis of modeled marginal operating-cost savings from extending storage duration under alternative county-level renewable capacity-factor weighting schemes and four historical ReEDS weather references. The study uses fixed hypothetical AC renewable and storage capacities and a custom copperplate dispatch LP. Results are conditional on point-sampled renewable source profiles and explicitly tested numerical approximations for conversion to hourly availability. They do not measure installed fleet performance, climate-change effects, financial storage returns, or network-constrained adequacy.

**Maintained rule:** Do not change the frozen LP data or introduce additional experiments just to inflate the study. This document is a pre-submission control list, not a statement that journal-submission requirements have been met.
