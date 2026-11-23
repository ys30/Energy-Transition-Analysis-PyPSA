# Paper S — 2023 USD / LP illustrative cost numeraire gate and exact 2,160-case uniform-scale sensitivity (2026-11-18)

## Actual source-level audit

Directly reopened latest corrected 22-page main manuscript and 8-page SI, and independently re-read the actual **2,160 frozen LP–ATB comparison rows** in `Paper_S_ATB2025_v2_2030_Cost_Validation/2160_lp_value_vs_ATB_v2_hurdle_cases.csv` (conversation study archive).

Original LP assumptions are `cR=5`, `cF=90` in illustrative **model USD/MWh**, whose historic base year was **not established**. Official ATB revised 2025 v2 cost hurdles are stated in **2023 USD per added kWh-year**. Thus the published comparison of a nominal LP objective difference and 2023-dollar ATB hurdle is scientifically a **conditional common-numeraire accounting comparison**, not an independently deflated 2023 market-profit estimate.

## Frozen algebraic scale audit (no LP reruns)

Positive uniform multiplication of **both** LP variable-cost coefficients by dimensionless `s` leaves its optimal dispatch and all spatial-reweighting relative signs unchanged; the illustrative avoidable variable-cost value scales exactly `V_s=sV`. Given an ATB hurdle `H` the pairwise first crossing is `s*=H/V` for positive archived `V`.

- 2,160 actual original matched-demand LP-value–ATB-hurdle rows verified.
- **Minimum pairwise `s*=1.0613100090`**, in 2020 Arizona, `source_potential_2012`, Expand / Advanced / 4% condition, `V=15.1220606367` model USD/(added kWh-year), `H=16.0491943107` 2023 USD/(added kWh-year).
- At `s=1.00`: **0/2160** meet hurdle; `s=1.05`: **0**; `s=1.07`: **2**; `s=1.10`: **4**; `s=1.50`: **76**; `s=2.00`: **213**.
- This multiplier is a **counterfactual scenario sensitivity, not an independently verified CPI conversion, FX rate, inflation adjustment, or 2023 energy price**.
- Previous manuscript language asserting that the exact break-even calculation “removes dollar-basis dependence” is too strong: it only produces conditional values when `cR` and the hurdle share a defined numeraire. It does not reconcile an unknown LP price year to ATB 2023 USD.

## Manuscript correction (conversation files; no fake binary GitHub claim)

Delivered revised main `Paper_S_Main_Currency_Consistency_Corrected_2026-11-18.docx` and SI `Paper_S_SI_With_Currency_Sensitivity_S7_Table_S4_2026-11-18.docx`. Changes:
- Explicitly label LP coefficients 5/90 as assumed **model** unit costs, the ATB 2023 dollar assumption and fixed-dispatch conditional break-even firm-price.
- Main abstract, methods §2.4–2.5, Results §3.7, Discussion §4.3–4.5 and conclusion qualify the zero-crossing claim by the common-numeraire assumption and reference the independently computed first crossing 1.06131.
- New **Supplementary Note S7**, **Table S4** (11 prespecified uniform scaling points), 2,160 casewise `H/V` thresholds, sensitivity grid, one-row earliest crossing and audit manifest.
- Word documents were successfully rendered for layout QA (main 22 pages, SI 9 pages). No figure renumbering or removal of any source experiment.
- The conversation-only `Paper_S_Currency_Consistency_Sensitivity_Package_2026-11-18.zip` contains both revised Word files, three CSV tables and manifests; it is **not** a GitHub release or Zenodo upload.

## Unchanged and remaining limits

Frozen 1,440 baseline LP, 360 new 2×2 LP, 2,880 new 3×3 LP, 2,160 ATB hurdle inputs, EIA-930/EIA-860M scope audits and Paper C-2 unchanged. Before submission, either (a) explicitly define the illustrative dispatch price coefficients as **hypothetical 2023-USD parameter values**, and keep all conditional sensitivity statements, or (b) introduce independently source-justified, vintage-dated price scenarios and analyze those without calling the present values historically calibrated. Document the archive DOI, author declarations and actual external BA-to-state evidence limits separately.
