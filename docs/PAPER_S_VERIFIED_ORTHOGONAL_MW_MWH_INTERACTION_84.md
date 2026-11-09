# Paper S — Verified orthogonal MW × MWh interaction audit (84 adjacent rectangles)

**Evidence:** Original 189 annual HiGHS LP optimal solutions from [accepted orthogonal MW/MWh workflow #42674534963](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42674534963). All 84 adjacent 2×2 rectangles were algebraically revalidated and saved by [source-derived interaction workflow #42675999423](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42675999423) (**success**). Source-demand-group selection and old original source-hour 4h/8h baseline comparison were certified in upstream runs; no new physical or cost data introduced.

## Definition, unit and interpretation

At fixed original zone-year and hypothetical resource-availability shape, let `C(P,E)` denote the **illustrative variable LP objective** at independent storage power `P` and energy capacity `E`.

For adjacent `P_low < P_high`, `E_low < E_high`, define:

`I(P_low,P_high,E_low,E_high) = [C(P_high,E_low)-C(P_high,E_high)] - [C(P_low,E_low)-C(P_low,E_high)]`.

- **Positive:** increasing installed MWh at high MW reduces the LP variable objective *more* than adding that same MWh at low MW (cost-side complementarity).
- **Negative:** less benefit from additional MWh at higher MW (substitutability on these particular source scenarios).
- **Near zero:** no meaningful numerical difference on this model grid. A USD 1 absolute interaction magnitude is used as an explicit **numerical classification threshold**, not a statistical test.

Each source group has three synthetic resource availability shapes and four adjacent rectangles from the 3×3 independent-factor grid: `7×3×2×2=84`. Exact conservation identity verified for each rectangle:

`I = 90 * [additional avoided firm output from energy step when power is high vs low] - 5 * [additional avoided unused renewable when power is high vs low]`.

Each interaction was also normalized by the **same shape-zone original reference LP objective at (0.25×peak MW, 1.0×peak MW-hour)** for readability. The normalized statistic is a percentage of the baseline toy **variable cost**, not an IRR, actual dollar-saving estimate, percentage of battery capital cost, or economic storage value.

## Verified source-computed results

| Synthetic supply | Positive interactions (> USD 1) | Near-zero (absolute <= USD 1) | Negative interactions (< −USD 1) | Median (percent of reference LP cost) | Maximum (percent) |
|---|---:|---:|---:|---:|---:|
| Flat 50% | 1/28 | 27/28 | 0/28 | 0.000 | 0.000374 |
| Ordinal wave A | 20/28 | 8/28 | 0/28 | 0.637 | 14.565 |
| Ordinal wave B | 15/28 | 13/28 | 0/28 | 0.00218 | 11.691 |

**Interpretation:** On this precise source-ordinal, capacity-factor-profile and cost grid, storage MW and MWh show positive cost-side complementarity in many wave-profile cells; Flat is almost always numerically additive/flat. None of the 84 rectangles had a negative interaction exceeding the USD 1 threshold. This observation is **not a proof of theoretical nonnegative MW–MWh cross effects**, nor a claim that complementarity must hold across different years, true weather profiles, generator assumptions, capex functions or real grid operating constraints.

### Wyoming p24: falsifiable within-model exception

For the 2030 Wyoming p24 unique source-demand shape, under synthetic wave A, increasing MWh from 0.5 to 1.0 peak-hour at low power (0.125×peak MW) reduces toy variable cost by about **USD 253,931**. The same energy step at 0.25×peak MW reduces it by about **USD 384,998**; the complementarity interaction is **USD 131,067** (0.0326% of the reference LP cost). However, the 1→2 MWh factor increment yields **zero** interaction at both tested adjacent MW steps. Thus a higher power can make the *lower* energy-capacity increment more useful, while large capacity increments still saturate. This is a more precise interpretation than asserting a general statewide lack of storage value.

## Figure and source provenance

**Figure S13:** Heatmap of `I / C_baseline × 100` for each of seven unique EFS peak-normalized 2030 source-demand sequences, three synthetic supply profiles and four adjacent MW–MWh factor steps. Source: original unrounded archived 189-LP output → independent 84-rectangle numerical certificate → [reproducible Figure S13 plotter](../src/energy_transition/paper_s_orthogonal_interaction_figures.py), [tests](../tests/test_paper_s_orthogonal_interaction_figures.py) and [automated plot workflow](../.github/workflows/paper-s-orthogonal-interaction-figures.yml). Plot must pass its own latest workflow before manuscript use.

## Why this increases scientific rigor

- The previous 294-case power sensitivity implicitly changed installed energy because `E = P × nominal duration`. The new analysis uses **independently specified MW and MWh**, and its 2×2 differences quantify cross-dependence.
- Factor effects have been checked against conservation identities and previously accepted original LP case results rather than manually reinterpreted from rounded plots.
- All seven shape groups were defined from original source load chronologies, preventing pseudoreplication of proportional zone-scale variants (19 nonzero zones with only seven distinct normalized shapes each projection year).

## Important restrictions

The *numerical results are not from observed solar/wind profiles*. Supply is hypothetical, hour labels are unverified physical UTC ordinal EFS `LocalHourID`, and the 2040 calendar-label anomaly remains. Objective excludes storage CAPEX, reliability, reserve, degradation, financing, lifetime, unit commitment, and zonal transmission. The historical dataset covers seven staged Western states, not a calibrated Western Interconnection. These seven source shapes are distinct but **not assumed to be probabilistically independent grid systems**.

**Next admission-gated step:** For representative and falsifying designs, export the *hourly primal vector* and identify charge/discharge power bounds and SOC energy-capacity binding hours by exact normalized factor cell, while testing LP optimal-solution non-uniqueness. Avoid treating simple binding counts alone as sensitivity/dual derivatives; if claiming shadow prices, extract and reconcile HiGHS dual marginals and perturb RHS bounds.
