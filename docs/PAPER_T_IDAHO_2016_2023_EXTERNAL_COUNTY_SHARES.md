# Paper T — Idaho seven-versus-nine-county external demand-share audit

**Source:** Obika, Cole & Rivers, OEDI hourly county demand 2016–2023, https://doi.org/10.25984/3366592; corrected HDF5 dated 2026-02-09. Research article: https://doi.org/10.1038/s41597-026-07693-3.
**Raw source:** https://data.openei.org/files/8562/historic_load_hourly_2016_2023_county.h5
**SHA-256:** `565b6182432c60c6e6fa9f68b1db5f490cec3fe2f11e41fad41d47d3c301e403`.
**CI:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43120784885 (success; artifact `paper-t-idaho-2016-2023-county-share-evidence`).

## Audited percentages of all Idaho annual modeled county-hour demand

| Year | 7 northern proxy counties | 9 fully Pacific-time counties | Nine + all Idaho County (upper proxy) | Seven minus fitted 16.5575% (pp) |
|---|---:|---:|---:|---:|
| 2016 | 15.976 | 20.303 | 21.242 | -0.581 |
| 2017 | 16.055 | 20.064 | 20.992 | -0.503 |
| 2018 | 16.076 | 20.070 | 20.987 | -0.481 |
| 2019 | 16.091 | 20.189 | 21.095 | -0.467 |
| 2020 | 16.015 | 20.089 | 20.961 | -0.542 |
| 2021 | 16.214 | 20.140 | 21.010 | -0.344 |
| 2022 | 16.385 | 20.225 | 21.110 | -0.172 |
| 2023 | 16.374 | 20.177 | 21.060 | -0.183 |

7 county FIPS: 16009 Benewah, 16017 Bonner, 16021 Boundary, 16035 Clearwater, 16055 Kootenai, 16057 Latah, 16079 Shoshone. All nine full Pacific-time counties also include 16061 Lewis and 16069 Nez Perce. The federal boundary (49 CFR §71.9) traverses 16049 Idaho County, which cannot be wholly allocated. The full Pacific territory share is therefore between the nine-county and nine-plus-Idaho-County values, **if** county-level modeled demand is allocated within Idaho County consistently.

2020 population (Idaho official 2020 census table): seven = 301,478 / 1,839,106 = **16.393%**; nine = 347,101 / 1,839,106 = **18.873%**. The fitted numerical −2/−3 shift weight is **16.5575%** for its smaller component.

## Interpretation and non-claims

1. The seven-county *proxy* shares (15.98–16.39%) are descriptively close to 16.5575%. This is **not** evidence that the seven counties are the time-zone processing region.
2. The **nine fully Pacific counties** have annual modeled demand shares around **20.1%**, noticeably different from 16.5575%. Reporting only the seven would risk cherry-picking a convenient geographical support.
3. Annual county-level demand is estimated, not direct measurement. OEDI uses population-based allocation for retail energy as one model component, so census and county-demand shares are not independent proofs.
4. This is a 2025/2026 county-data model and **not the actual EER → ReEDS 2022 production pipeline**. Source clock and county assignment for 2022 remain unauthenticated; numerical two-shift coefficient is not a known geographic share.
5. A held-out signed-hour p14/BA shape reconstruction is still required; no evidence supports removing `BLOCK_PHYSICAL_JOIN`. No publisher inquiry is claimed to have been sent.

**Reproducible code:** `src/energy_transition/paper_t_idaho_county_share_audit.py` and `.github/workflows/paper-t-idaho-county-external-share.yml`.

**Manuscript private v20.7** includes Methods §3.7c, revised §5.3, and supplementary Table S1. 