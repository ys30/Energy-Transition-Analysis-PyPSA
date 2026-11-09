# Paper S — verified HiGHS bound marginals vs capacity finite differences (eight archived-source 2030 probe configurations)

**Verified production run:** [MW/MWh bound-dual diagnostic workflow #42688265863](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42688265863) (**success**), both source-demand groups passed individually and consolidated 8-case comparison passed. Upstream accepted EFS demand and 8,760 source-hour original LP solutions from [seven-shape archive #42511072562](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42511072562).

## New method and exact interpretation

[Source solver](../src/energy_transition/efs_cyclic_storage_lp.py) now has a **strictly optional** `return_duals=True` argument. With unchanged constraints, objective, and default API, it exposes the *HiGHS minimization objective derivatives with respect to each original hour's variable upper bound*: charge-MW, discharge-MW, and SOC-MWh. For the same installed upper bound imposed on every hour, sum the corresponding upper-bound marginals:

- `∂C/∂P = sum_t[marginal(charge_t <= P) + marginal(discharge_t <= P)]` (USD per additional MW).
- `∂C/∂E = sum_t[marginal(SOC_t <= E)]` (USD per additional MWh).

The sign is nonpositive in this cost-minimization LP: a negative value means locally allowing more capacity reduces the **toy variable operating-cost objective**, not the storage lifecycle cost. Nonzero marginals are checked against active upper bounds. Additional runs perturb **only MW** or **only MWh** by `peak_MW × 1e-4` and reoptimize. One-sided directional derivatives can disagree at piecewise-linear kinks / basis degeneracy; disagreements are reported, not silently interpreted as solver failures.

**Evidence scope:** selected Arizona p28 and Wyoming p24, 2030 projected demand source ordinal 8,760 hours, flat or synthetic 24-ordinal wave resource profiles. Four preselected resource/design points per region. 8 base solves with explicit bound marginals + 16 one-variable perturbation solves. All 8 pairs of finite-difference derivatives match respective dual estimates within the pre-specified 1% classification tolerance; observed maximum absolute disagreement among the 16 derivative comparisons was **9.56×10⁻⁶ USD per unit**.

## Source-backed results

Annual sum of upper-bound marginal shadow prices (negative = extra capacity reduces modeled variable cost):

| Zone | Resource profile | Power / source peak MW | Energy / peak-MW-hour | `∂C/∂P` USD/MW | `∂C/∂E` USD/MWh |
|---|---|---:|---:|---:|---:|
| Arizona p28 | Flat | 0.250 | 1.0 | 0 | −640.888 |
| Arizona p28 | Wave A | 0.125 | 0.5 | 0 | −29,080.305 |
| Arizona p28 | Wave A | 0.250 | 1.0 | 0 | −25,715.642 |
| Arizona p28 | Wave B | 0.250 | 1.0 | 0 | −18,505.649 |
| Wyoming p24 | Flat | 0.250 | 1.0 | 0 | 0 |
| Wyoming p24 | Wave A | 0.125 | 0.5 | −152.000 | −2,243.109 |
| Wyoming p24 | Wave A | 0.250 | 1.0 | −76.000 | 0 |
| Wyoming p24 | Wave B | 0.250 | 1.0 | 0 | 0 |

The Wyoming Wave A small-capacity configuration demonstrates **simultaneously nonzero MW and MWh marginal cost value**. At 0.25 power ratio and 1.0 peak-hour capacity, the MWh derivative is zero but MW is still negative, so declaring all incremental storage capacity economically useless would be wrong even under this hypothetical objective.

**Crucial binding-hour counterexample:** in Arizona Wave A at power ratio 0.25, energy 1.0, the solver reports **615 charge-MW bound hours, 764 discharge-MW bound hours and 669 SOC-MWh bound hours**. Nevertheless the sum of *nonzero power-bound duals is zero*, while 321 SOC hours have nonzero negative energy marginals. A primal variable being exactly at an upper bound is **not evidence that relaxing this constraint would lower the optimum**. Bound-frequency counts cannot replace duals or controlled perturbations.

## Recommended results wording

> An eight-configuration diagnostic on two representative source-demand chronologies extracted the HiGHS upper-bound marginals for charge power, discharge power and stored energy and independently verified capacity derivatives by one-sided LP reoptimization. The two derivative estimates reconciled to within 9.6×10⁻⁶ USD per unit in these probes. Wyoming's wave-A small-capacity design had nonzero local value for both MW and MWh, but its larger-capacity design exhibited zero marginal energy value while retaining a negative MW cost derivative. Conversely, Arizona wave-A solutions had numerous hours with binding charge/discharge power limits but no nonzero power-bound marginals. Thus constraint activity alone does not establish economic shadow value; capacity responses must be interpreted from dual-certified LP sensitivity and the assumed synthetic supply-demand chronology.

## Limitations

- A bound marginal is a **local, solver-basis-dependent sensitivity**, not a globally valid cost saving for arbitrary large investment in a fixed MW/MWh design, especially at a kink or with alternative optimal primal/dual solutions.
- Only two *distinct* source load shapes and eight preselected configurations have been dual-audited so far; no across-seven-shape universality or formal statistical uncertainty claim.
- All source-hour labels are original EFS ordinal `LocalHourID`, **not certified physical UTC**; synthetic resource shapes are not observed meteorology.
- No battery CAPEX, degradation, discounting, reliability market, transmission-constrained Western grid dispatch or real source-certified renewable production data. The modeled variable objective must not be called investment ROI or net system benefits.

## Files / provenance

- [Code: source LP optional bound duals](../src/energy_transition/efs_cyclic_storage_lp.py)
- [Code: source-archived dual/FD checks](../src/energy_transition/paper_s_bound_dual_diagnostics.py)
- [Tests](../tests/test_paper_s_bound_dual_diagnostics.py)
- [GH Actions workflow](../.github/workflows/paper-s-bound-dual-diagnostics.yml)
- GitHub artifact: `paper-s-dual-finite-difference-representative-comparison` contains `paper_s_8_source_dual_vs_fd_comparisons.csv`. The per-group artifacts include 8,760-hour upper-bound dual CSV files.
- Figure S14, created from the accepted consolidated 8-row CSV, illustrates positive reductions in the toy cost for 1 additional MW or 1 additional MWh. Both quantities have **different physical units** and should not be interpreted as directly comparable investment opportunities.

**Next test (not yet completed):** For a few degeneracy-prone cases, perturb objective tie-breaking or use alternative primal selection and verify whether bound activity counts change while objective and directional derivatives remain consistent. Also examine alternative optimal dual marginal allocation before making claims on individual-hour binding patterns.
