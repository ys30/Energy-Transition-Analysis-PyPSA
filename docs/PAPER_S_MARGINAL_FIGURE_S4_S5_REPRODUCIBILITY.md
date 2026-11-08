# Paper S: archived-source marginal-duration figures S4 and S5

**Status:** plotting and tests committed; verify run success before treating the figure binary as a completed evidence asset.

## Source and procedure

The figure workflow [paper-s-marginal-duration.yml](../.github/workflows/paper-s-marginal-duration.yml) downloads the **unchanged original 540-case LP CSV** from the accepted [source run #42107237659](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659). It then:

1. Runs the original objective, energy-conservation and terminal-SOC certificate using [paper_s_lp_objective_certification.py](../src/energy_transition/paper_s_lp_objective_certification.py).
2. Validates that the original 540-case table has 20 zones × 3 years × 3 synthetic supply shapes × 3 storage durations and 8,760 original ordinal hours per zone/year.
3. Reaggregates **unrounded** source-case objective and energy columns into the nine year/shape × two incremental-duration pairs with [paper_s_marginal_duration.py](../src/energy_transition/paper_s_marginal_duration.py).
4. Independently verifies that all duration differences reconcile back to the 0-, 4- and 8-hour reported levels before drawing, with [paper_s_marginal_duration_figures.py](../src/energy_transition/paper_s_marginal_duration_figures.py).
5. Exports publication-size SVG and PNG versions of `figure_S4_unused_potential` and `figure_S5_toy_variable_objective`, a nine-row numerical CSV and a machine-readable manifest.

The figures compare **0–4 h** and **4–8 h** marginal increments across the three **synthetic** resource shapes and three EFS demand projection years. Unlike single-shape Wave A results, this exposes whether diminishing incremental improvement is shape-dependent. **Do not generalize the result until the source-derived cross-shape outputs are examined.**

## Correct captions and journal interpretation

**Figure S4.** Reduction in *unused hypothetical renewable availability* after each four-hour increase in assumed battery duration, grouped by planning year and synthetic renewable-availability profile. Twenty independent EFS-load zones; annual cyclic 8,760-source-ordinal-hour HiGHS LP. Not observed renewable curtailment.

**Figure S5.** Reduction in the *illustrative LP variable operating-cost objective* after each four-hour increase in assumed storage duration under the same three synthetic profiles and demand projections. Assumed direct renewable/charging coefficient USD 5/MWh and firm supply coefficient USD 90/MWh; excludes battery capital, O&M, degradation and transmission. Not actual investment savings.

A negative bar, if encountered, is preserved and should be independently investigated rather than silently clipped.

## Disclosures that must accompany reuse

- Demand: original NLR EFS-derived load data; seven Western states, 20 admitted zones, not complete Western Interconnection load.
- Renewable availability, battery sizing/efficiency and cost parameters: **synthetic assumptions**.
- Time axis: 8,760 original source-hour ordinal values, **not independently source-certified UTC**, with a specific 2040 calendar-label problem.
- Network: **20 independent-zone LPs**, no real Western transmission-constrained OPF.
- Objective: LP marginal variable-cost changes **exclude storage investment costs**. The figures cannot identify economically optimal storage duration.
- Do not redistribute any source bytes for which data rights are uncertain; GitHub Actions derived figure and aggregation artifacts are not permanent DOI-backed repositories.

## Evidence tier

The software/figure workflow does not create new independent real-system evidence. This is a visualization and integrity upgrade on the already accepted hypothetical-case archive. The public repository preserves methods and provenance; full paper drafts remain private.
