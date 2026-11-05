# Idaho original EFS Subsector provenance and frozen 2030 lag transfer

## Research question

The archived original EFS2020 state demand for Idaho was exactly reconstructed from four EFS sector categories, but a 2030-only Transportation +1 source-index candidate that modestly reduced held-out source-release hourly discrepancy was **not** selected when 2040 and 2050 were independently searched. To prevent re-selection from hiding cross-year failures, the present source-backed study **freezes that exact 2030 candidate** and evaluates it without any parameter search on both later planning years.

In parallel, the original raw NLR EFS ZIP does retain `Sector` and `Subsector` information. We now calculate original source annual MWh by both categories, cross-check against the previously accepted original Idaho state-hour archive and preserve the exact original source SHA-256. The subsector names and MWh shares identify source aggregation structure, **not geographical area or physical time zone**.

## Experimental protocol

1. Reacquire the authentic NLR original `EFSLoadProfile_Reference_Moderate.zip` using an official NLR URL and upstream-compatible system `unzip` for Deflate64. Verify the previously checked original source CSV SHA-256 `75b6cf99cc04a2b98bd69f7874809a396f256d57ae7f10d36f3e945fb0235eea`.
2. Filter `Electrification=Reference`, `TechnologyAdvancement=Moderate`, `State=ID`, planning years 2030/2040/2050, retaining every original `Sector/Subsector` label. Source rows with missing labels or nonfinite load are rejected.
3. Aggregate annual MWh for each original `Year × Sector × Subsector`. Require annual total energy equality against the independently archived 2020 EFS state-hour series in each year. Separately reconstruct complete 8760-hour `Year × Sector` traces to verify every original state-hour value.
4. Compare the archive with independent publisher-MD5-verified ReEDS2022 EFS_REFERENCE, excluding shifted cross-year boundaries. With the previously audited source index reference −2 h, fix **only** Transportation's +1-hour shift. Measure the last approximate half-year MAE against the unchanged four-sector baseline, without retuning the candidate in 2040 or 2050. Report signed MAE change, including negative values if the candidate worsens fit.
5. Explicitly reject the claims that a subsector's geography, original EFS source clock, physical Idaho time zones or future wind/solar resource joins have been established.

## Code and evidence

- `src/energy_transition/efs_idaho_subsector_crossyear.py`
- `tests/test_efs_idaho_subsector_crossyear.py`
- [GitHub Actions — Idaho EFS original subsector and frozen cross-year clock hypothesis](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-idaho-subsector-crossyear.yml)
- Artifact `idaho-efs-original-subsector-frozen-crossyear-evidence` containing:
  - `idaho_source_subsector_annual_energy.csv`
  - `idaho_frozen_2030_transport_shift_crossyear.csv`
  - `idaho_subsector_source_provenance.json`

**Scientific interpretation:** even a positive source-index fit on later years would only show a transferable mathematical rule on these two releases. It would not prove actual physical time-zone boundaries, causality of upstream data processing, or forecast-calibrated grid operation. A worsening later-year result would strengthen the evidence against a stable Transportation +1-hour explanation.

**Validated source results:** [original publisher-source CI #42131511821](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42131511821) succeeded: 14 distinct Sector×Subsector source combinations across the same 367,920 Idaho source records, original file and archive checksums passed, all annual energy totals reconciled.

### 2030 source subsector energy shares (selected)

| Sector / original Subsector | Idaho original 2030 MWh (approx) | Fraction of Idaho 2030 EFS original total |
|---|---:|---:|
| Commercial / other | 8,812,122 | 31.48% |
| Industrial / other | 7,520,245 | 26.87% |
| Residential / other | 6,189,303 | 22.11% |
| Residential / space heating and cooling | 1,461,317 | 5.22% |
| Industrial / machine drives | 1,468,272 | 5.25% |
| Transportation / light-duty vehicles | 380,937 | 1.36% |

The original source includes other smaller and some zero-MWh subsectors; the full 42-row source-year table is preserved in the CI artifact. `Subsector` describes end-use classification, **not Idaho geography, balancing-area membership or physical clock**.

### Frozen original 2030 Transportation +1 index shift: strictly later-half evaluations

| Year | Held-out original baseline MAE (MW) | Held-out fixed Transportation +1 MAE (MW) | Numeric improvement (MW) |
|---|---:|---:|---:|
| 2030 | 17.795943 | 15.585717 | 2.210226 |
| 2040 | 19.902631 | 17.889956 | 2.012675 |
| 2050 | 22.785865 | 20.558538 | 2.227327 |

The **same previously selected** 2030 source-index perturbation shows lower mismatch on the *later halves* of all three years, without tuning a new parameter in 2040 or 2050. This contrasts with the previous experiment's **per-year first-half selection**, which preferred the all-unshifted reference in 2040 and 2050. That implies the candidate's relative usefulness varies by evaluation window. It **does not** prove a stable EFS physical time zone rule, because both source releases' data processing and the original EFS2020 publisher clock are still not independently linked. Substantial residual remains even after the perturbation, and the original subsector labels are not an electrical or geographical mapping.

### First-half versus later-half sign reversal (verified)

[Independent rerun #42131969905](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42131969905) and [full main CI #42131969928](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42131969928) **both passed** after an unrelated pandas test fixture was corrected from a read-only NumPy view. The same previously selected Transportation +1 hour rule is now scored on **all 4,379 first-half and 4,377 held-out interior reference hours** per year:

| Year | First-half original MAE (MW) | First-half fixed-rule MAE (MW) | First-half improvement (MW) | Held-out original MAE (MW) | Held-out fixed-rule MAE (MW) | Held-out improvement (MW) |
|---|---:|---:|---:|---:|---:|---:|
| 2030 | 16.720487 | 16.647585 | +0.072903 | 17.795943 | 15.585717 | +2.210226 |
| 2040 | 18.692429 | 19.449288 | **−0.756859** | 19.902631 | 17.889956 | **+2.012675** |
| 2050 | 21.398003 | 22.386465 | **−0.988462** | 22.785865 | 20.558538 | **+2.227327** |

Thus **2040 and 2050 show a sign reversal**: the frozen 2030 candidate worsens the first-half numerical fit but improves the later-half fit. This explains why a same-year training-based selection in 2040/2050 preferred the unchanged baseline, even though a locked candidate evaluated on their latter halves outperformed that baseline. **Do not infer a specific DST, physical time zone, generator coincidence, or forecasting mechanism from this pattern.** It is a robust result for these cross-release source-hour index comparisons; more geographically resolved and authoritative original processing metadata are needed for causal explanation.
