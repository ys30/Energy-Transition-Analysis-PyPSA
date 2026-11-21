# Paper S — forensic audit of suspect R=2.0, wind AC share=50% grid cell (2026-11-18)

**Status:** actual frozen-result integrity checked; new continuity LPs are running, **not yet verified**. Preserve the original Paper S 3×3 result and do NOT claim mechanism yet.

## Source and hypothesis

Original successful, verified [3×3 run 44209543001](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44209543001), artifact **14388326204**. The suspect R=2.0, wind=.50 state-year effects are from `paper_s_design_grid_540_paired_siting_effects.csv`, generated from original 0/4/8h LP objectives. Reopened the full 2880 new LP, 1080 duration-value, 540 paired-siting, 36 summary CSVs, and the original **source code** `src/energy_transition/paper_s_siting_design_grid_3x3_2880lp.py`.

## Confirmed numerical and indexing gates

1. **Not the frozen center reused.** Frozen reuse is explicitly gated only at **R=1.5 / wind=.50**. R=2.0 / wind=.50 has **360 original new optimal LP rows** = 4 states ×15 weather years ×2 siting schemes ×3 battery durations. No R=1.5 / .50 rows are present in the 2880-new-LP file. All 360 suspect rows have 8760 source hourly points, unique complete source index keys, and max equality residual under 1e-5 MWh; original actual max 7.28e-12 MWh.
2. Original generation source code constructs `w` and `p` **once per (source year, county scheme, state)** and then forms each design case as `wind_share*w+(1-wind_share)*p` with the same source-hour clock, fixed state 2030 demand, and identical county weights inside that loop. For R=2.0 / .50, there is no special old-center branch, no extra demand branch or separate hour conversion.
3. The 120 source R=2.0 /.50 4→8h marginal storage values were independently recomputed from the 360 original LP objective and storage-energy size rows, giving max absolute discrepancy **7.21e-10 model USD/(added kWh-year)** versus the original source duration-value table. This rules out a simple erroneous 4/8h indexing or aggregation in the published CSV, **but not every possible upstream source-data defect**.
4. Source LP annual **demand MWh** is constant across county-weight and source-year cases within each state. This is an annual total check **not a byte-for-byte load-array or clock hash confirmation**; the new runner will explicitly hash source input arrays.

## The original suspect pattern is reproducible at yearly level

CO R=2.0 paired **EIA-operating minus resource-potential** effect:
- wind 25%: median **−0.163546**, positive 5/15 weather years;
- wind 50%: median **−2.177855**, **negative in every one of the 15 years**, range approximately **−2.967 to −1.316**;
- wind 75%: median **+2.615353**, **positive in every one of the 15 years**.

Other states at R=2.0: AZ medians −0.469/−0.169/+0.358 (25/50/75%); ID +0.717/+0.688/+1.209; WY +1.241/+1.011/+0.983. Note AZ is monotonic upward across these three ratio=2 points, while WY decreases slightly; **the specific CO 50% local dip is not a shared four-state local minimum**. The earlier cross-ratio decline from R=1.5 to 2.0 at 50% occurs in all states but is not in itself evidence of an indexing bug.

## Preliminary operational explanations, not yet proved

CO R=2.0, marginal 4→8h value **medians** by each siting scheme:
- wind 25%, EIA 22.568; potential 22.710
- wind 50%, EIA 13.241; potential 15.419
- wind 75%, EIA 7.321; potential 4.676

Both scheme-specific marginal values decline with increasing wind share; the distinct rates of decline create a crossing in their paired difference. Source four-to-eight-hour changes in curtailment and firm generation also vary substantially across the design points. However, medians of scheme-specific values are not exactly the median of within-year differences, and aggregate curtailment alone cannot identify charging saturation or causal mechanisms. Do NOT claim a physical phase transition until adjacent 40/60% shares and temporal SOC/curtailment indicators are independently evaluated.

## Independent targeted continuity experiment

New branch code: `src/energy_transition/paper_s_R2_wind40_60_continuity_720lp.py`.

New workflow: [#44449229739](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44449229739), `.github/workflows/paper-s-r2-wind40-60-continuity-720lp.yml`. **Planned 720 genuinely new LP solutions** = 4 states ×15 weather years ×2 county-weight schemes ×2 new shares (40%,60%) ×3 battery durations, plus 240 source input hash records, 120 within-year paired siting effects and 8 state/share medians. Identical original source 2012-CST dataset versions, fixed 2030 demand, source weather years, R=2.0, storage parameters, illustrative costs, and the same solver library. New 40/60 source input arrays are SHA-256 pinned across shares. Original 25/50/75 results stay frozen and can be compared after the new workflow succeeds.

**As of this audit:** #44449229739 is running source acquisition; **no 40/60 numerical values are claimed or prefilled**. Do not interpret the mere creation of the workflow as completed new scientific results.

Conversation-local audited source-result bundle `Paper_S_2p0_50pct_Forensic_Audit_2026-11-18.zip` contains recomputed 120 original suspect duration values, 180 original R2 source-year effects, state/scheme operational-value and curtailment proxies, SHA-256 input CSV digests, and the explicit outstanding gate.

**Frozen:** 1440 core LP, previous 360 2×2 new LP, 2880 3×3 LP, 2160 ATB, all original data, Paper C-2. No manuscript result updated until new evidence is verified.
