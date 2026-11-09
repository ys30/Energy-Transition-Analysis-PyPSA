# Paper S — 294 LP one-factor parameter sensitivity, seven unique source-demand shapes (verified)

**Source audit status:** **PASS** in [single-job seven-group baseline-verified full-year workflow #42672106407](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42672106407). The original 2030 EFS hourly load chronologies were recovered from [seven distinct source-shape full-year archives #42511072562](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42511072562). A single deterministic representative per normalized EFS source-load shape was selected before investigating storage outcomes. The 294 solved LPs all reached `optimal`, retained 8,760 source-hour ordinals and cyclic terminal SOC. Default cases (3 synthetic supply shapes × 2 battery durations × 7 source-demand shapes) reproduced their accepted archived hourly aggregate discharge, charge, firm, unused availability and original objective. Archived artifact name: `paper-s-all-seven-shapes-294-lp-parameter-sensitivity`.

**The first multi-job batch [#42671580855](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42671580855) reported failure**, though individual groups yielded verified results. Do not cite it as complete. The repaired original-hour audit and successful **serial consolidated run #42672106407** are the authoritative numerical record.

## Design

Seven one-factor-at-a-time scenarios, with EFS source demand and synthetic resource profiles fixed in each zone:

| Scenario | Battery power, fraction of zonal peak load | Round-trip efficiency | Firm price (USD/MWh) |
|---|---:|---:|---:|
| Baseline | 0.250 | 0.90 | 90 |
| Half power | 0.125 | 0.90 | 90 |
| Double power | 0.500 | 0.90 | 90 |
| Lower efficiency | 0.250 | 0.80 | 90 |
| Higher efficiency | 0.250 | 0.95 | 90 |
| Lower firm price | 0.250 | 0.90 | 60 |
| Higher firm price | 0.250 | 0.90 | 150 |

Renewable direct delivery or charging inputs retain the toy coefficient **USD 5/MWh**. For each scenario, three artificial resource shapes and **4h/8h** battery design points were solved: 7 distinct source-demand shapes × 7 parameter scenarios × 3 artificial resource profiles × 2 durations = **294 successful full-year LPs**. The 147 paired effects are `E_discharge(8h) - E_discharge(4h)` within fixed source-shape/parameter/resource-shape groups. All 147 differences were nonnegative at report precision; no modeled cost objective increased under the longer duration. Neither confirms net investment value because **battery CAPEX is absent**.

**Important confounding by model design:** `battery_energy_MWh = storage_power_MW × duration_h`. Consequently the half/double-*power* scenarios modify **both power rating and nominal energy capacity**, not power only. They are alternative battery sizing designs rather than an isolated causal test of power bottlenecks. Do not call these a power-only perturbation experiment.

## Source-derived main outcome: counts of distinct demand shapes with positive 4h→8h additional battery discharge

Numerical threshold: `additional_discharge_mwh > 0.001`, out of seven deterministic source-hour demand shapes; the counts are **not inferential proportions from seven statistically independent grid systems**.

| Parameter scenario | Flat artificial resource | Synthetic Wave A | Synthetic Wave B |
|---|---:|---:|---:|
| Baseline | 1/7 | 6/7 | 6/7 |
| Half power | 1/7 | **7/7** | **7/7** |
| Double power | 1/7 | **2/7** | **1/7** |
| 80% round-trip efficiency | 1/7 | 6/7 | 5/7 |
| 95% round-trip efficiency | 1/7 | 6/7 | 6/7 |
| Firm cost USD 60/MWh | 1/7 | 6/7 | 6/7 |
| Firm cost USD 150/MWh | 1/7 | 6/7 | 6/7 |

**Result:** The originally reported 1/7 Flat versus 6/7 Wave A and B contrast is sensitive to how the battery power-and-energy dimensions are sized, especially doubling or halving power relative to zonal peak. It is relatively insensitive to the tested positive firm marginal-cost coefficients in terms of the **optimized discharged energy**: relative to baseline, all 21 shape-by-zone marginal discharge comparisons for each of the USD 60 and 150 cases differed only by numerical rounding (maximum absolute difference under `1e-8 MWh` in the archived source). **Toy cost savings still change with firm cost**, so do not say economic values were unchanged.

### Wyoming p24 counterexample and reversal

Under the default 0.25 peak power ratio, **Wyoming p24** had `E_discharge(8h)-E_discharge(4h)=0` in all three synthetic resource shapes. It stayed at zero under doubling power, changing efficiency to 80%/95%, and pricing firm energy at USD 60 or 150/MWh. But **halving power and therefore battery energy sizing** to 0.125 peak ratio made incremental discharge positive under both waves:

- Wave A: **3,007.078 MWh** more battery energy delivered for 8h relative to 4h; toy variable objective falls by **USD 253,931.05**.
- Wave B: **673.883 MWh** more delivered; toy objective falls by **USD 56,905.70**.
- Flat remained zero in the same half-power variant.

This **invalidates** the strong claim that source chronology alone makes >4h duration irrelevant in Wyoming. It supports a conditional interaction of assumed temporal resource structure with battery sizing; an isolated power-versus-energy factorial investigation is the correct next mechanism experiment.

## Scientific limits

1. Repeated temporal shapes originate from the staged EFS/LAF zones, not seven independently sampled real-world load data generators.
2. Each source year contains 8,760 `LocalHourID` source ordinals. Physical UTC is not independently validated. The 2040 leap-label issue remains.
3. Artificial renewable shapes are not empirical wind/PV profiles; this study cannot make claims about actual solar diurnal alignment.
4. No Western transmission-constrained OPF, generator-to-bus site validation, storage investment costs, reliability adequacy, or depreciation/degradation.
5. This sensitivity experiment varies **one parameter setting at a time**, but changing battery power changes energy capacity by construction. Varying firm price within the tested range does not change optimized energy dispatch, but other price regions and investment economics are untested.
6. The seven-source-shape sample was chosen deterministically for **mechanism diversity**, not to generate hypothesis-test p-values, significance tests, population frequencies, or generalized national policy statements.

## Recommended Paper S Results wording

> In an archived-baseline-validated 294-case one-factor sensitivity experiment spanning seven distinct EFS-derived source-demand chronologies, three synthetic renewable supply profiles, two battery durations and seven illustrative parameter settings, the presence of additional discharge from increasing nominal storage duration from four to eight hours depended strongly on the battery sizing ratio. At baseline power of 25% of zonal peak, six of seven distinct demand chronologies exhibited positive additional discharge under each synthetic wave profile; at half that power ratio, all seven did, whereas at double power only two under wave A and one under wave B did. Within the model's construction, changing battery power scales its stored-energy capacity at fixed duration, so these are **coupled power-and-energy sizing** effects rather than isolated power sensitivity. A Wyoming representative with no additional baseline discharge gained additional discharge under the half-power design. This result indicates conditional nonrobustness of a chronology-only explanation and motivates a controlled independent power and energy capacity factorial test.

## Verified source files and code

- Baseline parameterized unchanged LP: [efs_cyclic_storage_lp.py](../src/energy_transition/efs_cyclic_storage_lp.py)
- Recompute stress cases and audit original archives: [paper_s_parameter_sensitivity.py](../src/energy_transition/paper_s_parameter_sensitivity.py)
- Successful consolidated seven-shape serial CI: [paper-s-parameter-robustness-serial.yml](../.github/workflows/paper-s-parameter-robustness-serial.yml)
- Figure S10 generator and source consistency checks: [paper_s_parameter_robustness_figures.py](../src/energy_transition/paper_s_parameter_robustness_figures.py), [Figure S10 workflow](../.github/workflows/paper-s-parameter-figure-S10.yml).

**Artifact:** `paper-s-all-seven-shapes-294-lp-parameter-sensitivity`: full 294 optimized LP rows, 147 marginal comparison rows, cross-parameter positive-shape count table. Source case and Figure S10 code should be used rather than numbers manually typed in this audit.

Paper S manuscript remains private; this public document is a provenance-checked summary and method disclosure.
