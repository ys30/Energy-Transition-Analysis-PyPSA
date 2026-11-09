# Paper S — verified cost-capped annual SOC occupancy envelope (24 source-backed LP solutions)

**Validation:** [source-backed min/max SOC workflow #42716052153](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42716052153) **success**: Arizona p28 and Wyoming p24 each solved four predefined supply-and-capacity cases, with original 8,760 EFS source-hour demand, retained cyclic-SOC constraints and original LP objective. The eight baseline LPs plus 16 constrained secondary LPs reconcile in the accepted artifact `paper-s-eight-explicit-cost-cap-soc-envelope-comparisons`. The independently source-derived [Figure S16 workflow #42716686617](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42716686617) **success**, exporting PNG/SVG, an eight-interval CSV and a manifest. This is a model-based **near-optimal annual SOC occupancy envelope**, not a new empirical wind/solar or economic-value experiment.

## Exact admission rule and what was optimized

For each zone/supply/power/energy configuration, solve the original LP once to obtain C*. Set `epsilon = max(USD 0.05, 1e-9 × C*)`. Without changing any original balance or storage MW/MWh bounds, impose a new constraint `C_original(x) <= C* + epsilon`. Independently minimize and maximize `SUM_t SOC_end(t)` over that same constrained feasible region.

Rescore all candidates using **the unperturbed original toy LP objective**. Every new solution was checked for full source-hour conservation, cyclic SOC = 0 at the terminal hour, original objective cap with at most USD 0.02 numerical allowance, and inclusion of the original optimal schedule's annual SOC occupancy between the extrema. The maximum observed candidate cost increase above C* was approximately **USD 2.018**, under the largest explicit allowed budget of approximately USD 2.0183. The (predefined) cost budget varies with each source case's original C*; the value is intentionally extremely small relative to hundred-million- to billion-dollar illustrative objective totals. It is still **not the strict exact-optimal face**, and does not mathematically establish multiple perfectly equal optimal simplex bases.

## Actual source-derived means

Annual mean SOC as a **percentage of installed MWh energy capacity** (rounded to two decimal points). Each min and max is the globally optimized annual **SUM SOC** under the cost cap; these are not separately optimized limits of every hour or of the count of hours at capacity.

| Source group | Synthetic supply, power | Lowest SOC mean | Original solver SOC mean | Highest SOC mean | Interval (percentage points) |
|---|---|---:|---:|---:|---:|
| Arizona p28 | Flat, P=25% peak | 12.32% | 13.60% | 88.29% | 75.98 |
| Arizona p28 | Wave A, P=12.5% peak | 21.89% | 36.84% | 77.24% | 55.34 |
| Arizona p28 | Wave A, P=25% peak | 26.34% | 39.19% | 72.10% | 45.76 |
| Arizona p28 | Wave B, P=25% peak | 21.07% | 29.78% | 76.67% | 55.60 |
| Wyoming p24 | Flat, P=25% peak | 0.0012% | 0.0058% | 1.52% | 1.52 |
| Wyoming p24 | Wave A, P=12.5% peak | 5.84% | 11.63% | 76.33% | 70.49 |
| Wyoming p24 | Wave A, P=25% peak | 3.11% | 5.66% | 78.11% | 75.00 |
| Wyoming p24 | Wave B, P=25% peak | 1.28% | 2.42% | 75.12% | 73.85 |

**Important:** Wyoming's original HiGHS optimal mean SOC may be very low, yet the cost-capped schedule can keep the battery much fuller through much of the year. Therefore a reported mean SOC or count of SOC-bound hours from a single LP optimum cannot be treated as a unique consequence of resource chronology or as a physical indicator of active, beneficial storage cycling. A high SOC in the max-occupancy schedule need not imply useful discharge, additional load served, or economic value: it can reflect nearly cost-free energy *holding* under the model assumptions. Likewise, the min-SOC schedule is optimized to empty storage when possible, not to maximize reliability. Neither extreme is a claim about actual dispatch.

## Figure S16

[Figure S16 plotting code](../src/energy_transition/paper_s_soc_envelope_figures.py), [verification tests](../tests/test_paper_s_soc_envelope_figures.py), [workflow](../.github/workflows/paper-s-soc-envelope-figures.yml). The **line** is the near-optimal annual mean SOC interval, and the **black dot** is the original unperturbed HiGHS optimum. It is intentionally not a statistical confidence interval, a pointwise uncertainty band or an estimate of investment outcomes. All eight precise values are in the GitHub Actions archive CSV.

### Revised Paper S Results / Discussion language

> To quantify solution-selection sensitivity in storage occupancy, we added a secondary LP over an explicitly constrained near-optimal feasible set defined by no more than `max(USD 0.05, 10^-9 × original optimum)` of additional toy variable cost. For two prespecified 2030 source-demand chronology groups and four synthetic resource/power–energy configurations each, we obtained lower and upper bounds on annual summed storage SOC without changing the underlying cyclic dispatch constraints. The original HiGHS schedules frequently occupied a small fraction of that feasible range; for example, the Wyoming wave-A, 25%-power configuration had an original mean SOC of 5.66%, while cost-capped alternative schedules covered 3.11%–78.11% of nominal energy capacity. These findings demonstrate that occupancy and simple capacity-bound-hour counts are highly solution-selection-sensitive, whereas the primary optimal objective and independently perturbed cost derivatives have a more direct model-defined interpretation. They do not establish physical storage efficiency, system reliability or net investment returns.

## Remaining methodological limits and next study

- The cost-cap envelope identifies **bounds on annual total/mean SOC only**, not rigorous envelopes on individual hour-by-hour SOC, capacity-bound-hour counts or total battery throughput. Those need distinct secondary objectives or min/max per hour and should not be inferred from the present two extrema.
- One feasible near-optimal optimum can store energy without discharging it. Annual SOC and binding-hour quantities are less directly physically meaningful than throughput, firm-energy displacement and a model objective with explicit storage opportunity costs and degradation.
- The synthetic resource shapes and original EFS `LocalHourID` are not validated physical wind/solar or UTC time. The model excludes transmission, generator unit commitment, storage capex and financing.
- The two source groups are chosen for falsification and contrast, not as independent statistically sampled regional systems.
- If a paper requires a formal **exact** alternate-optimum proof, fix `C=C*` to an independently certified tolerance and carry out a feasibility/secondary-objective witness or dual-based facial analysis. The present narrow near-optimal cost-sublevel set is a stronger practical sensitivity test but not that proof.

Keep full private Paper S manuscript outside the public repository.
