# Paper T WP1 — real observed-demand release validation (11 Nov 2026)

## Target: new outcome, not another -2/-3 h example

Ruggles et al. archive two *published editions* of the same hourly EIA-930 BA-demand records:
- 2019 October cleaned release (`data/release_2019_Oct/balancing_authorities`), common overlap 2015-07-02 00:00 through 2019-07-01 23:00 UTC;
- 2020 October cleaned release (`data/release_2020_Oct/balancing_authorities`), whose first 35,064 hourly labels match the older edition.
Both files are under the independently specified upstream Git commit `b80145df5f92aba56c52ed45281831b93543fb3b`.

A second, subordinate control compares the archived original EIA CSVs with the 2019 cleaned data at the same hour labels; this identifies missing and anomalous-data effects. The edition-to-edition release comparison is the stronger transferability experiment.

## Reproduced numerical findings (direct file read; before CI)

| BA | Overlap UTC hours | Changed cleaned-hour values | Best nonwrap lag | MAE at best | Runner-up lag | Runner-up MAE |
|---|---:|---:|---:|---:|---:|---:|
| IPCO | 35,064 | 4,061 (11.58%) | 0 h | 34.9836 MW | +1 h | 92.4493 MW |
| AZPS | 35,064 | 152 (0.43%) | 0 h | 0.47174 MW | -1 h | 152.7190 MW |
| BPAT | 35,064 | 53 (0.15%) | 0 h | 0.05938 MW | +1 h | 190.4081 MW |

Observations: a 0-h optimum does **not** mean the published values are numerically identical. IPCO has unusually extensive revisions; 2019 original-to-cleaned comparison has almost all hours unchanged, yet a large raw-data MAE due to anomalous observations. The version-pair result remains a same-lineage check rather than independent validation of forecast correctness or a physical weather-hour join.

The method must report 2019/2020 numeric changes separately from relative lag. Version-data timestamps have documented UTC labels in the upstream repository, but the paper's screening contract still requires independent evidence review before any physical-hour join.

## Code and CI

- `src/energy_transition/paper_t_ruggles_release_pair.py`
- `.github/workflows/paper-t-ruggles-release-pair-ci.yml`
- `src/energy_transition/paper_t_ruggles_external_case.py`
- `.github/workflows/paper-t-ruggles-external-25lag.yml`

CI generates 75 nonwrapping lag results across 3 BAs, a summary with changed-hour fractions, upstream source content hashes and category changes. The 2019 raw-to-cleaned control requires treating both `MISSING` and `EMPTY` as missing-value tokens. The original EFS 2020 / ReEDS 2022 source join remains **BLOCK_PHYSICAL_JOIN**.

## Manuscript next stage (after CI evidence checks)

Add a compact Results subsection `External release-pair validation` and an expanded Table 7 row for documented same-hour numerical revisions (0 h best but nonzero residual). Preserve `O1–O4` conceptual distinction and the program's independent review gate. Avoid calling this a new publisher-independent forecasting product; it is a separate, real observed-demand processing and versioning family.

## Sources
- Ruggles repository: https://github.com/truggles/EIA_Cleaned_Hourly_Electricity_Demand_Data
- 2020 release Zenodo: https://doi.org/10.5281/zenodo.4116342
- Earlier release archive: https://doi.org/10.5281/zenodo.3517197
- Methodology: https://doi.org/10.1038/s41597-020-0483-x
