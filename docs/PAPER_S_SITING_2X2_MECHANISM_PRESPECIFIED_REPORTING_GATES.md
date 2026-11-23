# Paper S — Prespecified 2×2 wind/PV siting-mechanism reporting protocol

## Experimental identity and separation from C-2

This is an intervention on **county aggregation weights**, not weather or climate forcing. It is distinct from Project C-2 heat × wind meteorological-stress attribution. Hold fixed: four states, all 15 ReEDS source weather years, fixed 2030 load shaped by the publisher's 2012 reference, AC capacity, wind fraction 0.5, renewable peak ratio 1.5, storage power 0.25 × peak demand, 90% roundtrip efficiency, 0/4/8h storage, source-hour **trapezoid** approximation, nominal firm and renewable variable costs. Single-zone SciPy HiGHS LP, not PyPSA network OPF.

Four arms are `potential_potential` (PP), `eia_wind_only` (EP), `eia_pv_only` (PE), and `eia_wind_eia_pv` (EE). PP and EE values are **unchanged** frozen original records; only EP and PE require solving new LPs: 15 × 4 × 2 × 3 = 360 new cases. Full factorial: 15 × 4 × 4 × 3 = 720 duration-specific cases. Primary outcome V = (C4−C8)/(1000×(E8−E4)) in modelled USD/(added kWh-year). Neither dispatch dollar value nor EIA siting weight defines actual project revenue.

For each state-year:
- Wind-only effect: `V_EP−V_PP`.
- PV-only effect: `V_PE−V_PP`.
- Non-additive interaction: `V_EE−V_EP−V_PE+V_PP`.
- Symmetric wind Shapley share: `0.5×[(V_EP−V_PP)+(V_EE−V_PE)]`.
- Symmetric PV Shapley share: `0.5×[(V_PE−V_PP)+(V_EE−V_EP)]`.
- **Numerical gates:** wind-only + PV-only + interaction = total EE−PP; wind Shapley + PV Shapley = total EE−PP, absolute tolerance <= 1e-8 USD/(added kWh-year).

## Separate mechanism descriptors; avoid claiming causally identified mediation

Compute on the **same 8,760 aligned hours**, for each of four arms and weather year:
- Mean wind and PV source CF; combined wind/PV CF variance, lag-24 autocorrelation.
- Mean within-day net-load peak-to-trough, annual net-load standard deviation and maximum, lag-24 autocorrelation.
- Pre-dispatch positive surplus and deficit integrals in MWh. Note these are **not** actual model dispatch curtailment.
- 4h and 8h actual LP `unused_renewable_mwh` and their difference. This is solved dispatch curtailment and may vary with optimization, not merely CF shape.
- Report paired within-state-year **change from PP** for all three other arms, with the 15 source years shown individually and a median across weather years. Inter-year samples are weather scenarios, not independent IID draws.
- Optionally show Spearman association between 60 paired **change in mechanism indicator** and total storage-value effect, strictly **descriptive**. Shared intervention and endogenous dispatch preclude calling this mediated causal attribution.

## Figure and table gates

Main Results: one four-state weather-year-resolved wind-Shapley/PV-Shapley/total figure; one two-factor (wind-only × PV-only) figure with interaction label; one table of each state's 15-year median **paired** total, wind-only, PV-only, interaction and Shapley effects plus positive-year counts. Supplement: all 60 raw decomposition rows, all 240 arm×year mechanism descriptors, 4-to-8 curtailment changes, source SHA and solver residual checks. Never divide a median contribution by a median total effect without caveat: ratios can be unstable or exceed 100% when opposing contributions cancel; prefer absolute USD/(added kWh-year) quantities.

## Publication acceptance criteria

1. GitHub Actions **completed successfully** and emitted all four CSVs; do not infer results from pending job status.
2. All 360 new cases optimal, small energy-balance residual; all 360 reused PP/EE duration rows exactly match frozen original case identities.
3. Main source-year and hour clock equivalence verified; 15×4×4×3 cells; exactly 60 complete 2×2 quartets.
4. New 15-year result claims cite **actual artifact**, not inferred data. Update abstract/discussion only after checking ID/WY signs under wind-only and PV-only interventions.
5. Keep the existing 1,440 LP/2,160 ATB evidence, Paper C-2 and PR #2 Draft unchanged.
