# Paper S — SI S7 frozen 2,160-row original LP value correction (2026-11-20)

The November 20 Supplementary Note S7 mistakenly printed `V=3.732231` beside the **correct** minimum threshold multiplier `s*=1.06131001`. Direct reinspection of the authentic GitHub Actions artifact [14147890135 from run 43678422986](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43678422986), CSV `paper_s_official_atb2025_v2_2160_lp_cost_comparisons.csv` (2,160 rows), shows:

| Frozen source key | Official value |
|---|---|
| State / weather year | AZ / 2020 |
| County weight | `source_potential_2012` |
| ATB pathway / scenario / real discount | Expand / Advanced / 4% |
| Original modeled marginal 4→8h operating value | **15.122061 nominal model USD/(added kWh-year)** |
| Original ATB v2 duration hurdle | **16.049194 2023 USD/(added kWh-year)** |
| Minimum common cost-coefficient scaling H/V | **1.06131001** |

The corrected SI DOCX and corrected prepublication deposit candidate replace the erroneous V number and retain its valid result. The initial 0/2160 baseline-screen crossings, minimal 6.131% illustrative scaling to first crossing, and separate 3×3 213/1080 Advanced/4% crossings remain unchanged. This repair does not establish a real 2023 dollar numeraire. No optimization was rerun.

**Publication release gate:** never publish the superseded `Paper_S_Zenodo_Deposit_Candidate_2026-11-20.zip` or `Paper_S_SI_Revised_2026-11-20.docx` with the incorrect number; use the verified corrected successor files.
