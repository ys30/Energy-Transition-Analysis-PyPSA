# Paper S — verified original-cost-capped annual storage-discharge envelope

**Source-backed experiment:** [GitHub Actions #42747095388](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42747095388), success. The accepted artifact contains eight complete annual delivered-energy intervals and 24 LP summaries across two preregistered 2030 EFS original source-demand chronologies (Arizona p28 and Wyoming p24), four configurations per zone. All eight primary LPs are checked against the accepted source case history where applicable; 16 are independently solved minimum/maximum annual discharge LPs.

## Exact experimental definition

For each source case, find original LP minimum `C*`; impose `C_original(x) <= C* + max($0.05, 1e-9 × C*)` with all original hourly renewable, demand and SOC balances, installed power MW, installed energy MWh, and terminal zero SOC unchanged. Separately minimize and maximize `SUM_t battery_discharge_to_load(t)`, re-score each under **the unmodified original LP objective**, and verify that the original solution's discharge falls between the extrema.

This creates a range in **annual delivered MWh only**, not a confidence interval, per-hour discharge band, simultaneous bound on SOC occupancy, or proof of exact alternative optimal LP bases. A numerical absolute allowance of at most USD 0.02 for objective-cap checking is additionally enforced.

## Exact-source-derived delivered-energy stability

Values display rounded only; original unrounded results are in the workflow CSV. The max–min interval is in **MWh**, and its ratio is relative to each original solution's **annual discharged MWh**.

| Group | Synthetic supply and battery power | Baseline discharge (GWh) | Max–min discharge (MWh) | Relative interval (%) |
|---|---|---:|---:|---:|
| Arizona p28 | Flat 50%, P=25% peak | 950.877 | 2.35356 | 0.00024751 |
| Arizona p28 | Wave A, P=12.5% peak | 2676.443 | 3.65668 | 0.00013662 |
| Arizona p28 | Wave A, P=25% peak | 5216.555 | 3.26817 | 0.00006265 |
| Arizona p28 | Wave B, P=25% peak | 4014.744 | 2.93413 | 0.00007308 |
| Wyoming p24 | Flat 50%, P=25% peak | 0.136824 | 0.0449423 | 0.03284689 |
| Wyoming p24 | Wave A, P=12.5% peak | 72.14196 | 0.730153 | 0.00101211 |
| Wyoming p24 | Wave A, P=25% peak | 76.86891 | 0.0450266 | 0.00005858 |
| Wyoming p24 | Wave B, P=25% peak | 34.01044 | 0.0449770 | 0.00013224 |

For most probes the relative annual discharge interval is **below 0.001%**; the Wyoming Flat probe has a larger percentage only because its baseline discharge is very small (~137 MWh). This comparison is controlled for each source configuration's toy cost tolerance and is **not** evidence that actual reliability or time-specific discharge is stable.

**Contrast to the independently verified SOC occupancy experiment:** [#42716052153](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42716052153) found annual average SOC feasible ranges spanning tens of *percentage points* in several wave cases. The two distinct secondary LPs show that storage inventory level can be highly nonunique while **annual energy delivered to loads** remains nearly invariant within the same tight original-cost sublevel set. High SOC alone cannot be interpreted as useful operation or annual battery throughput.

## Paper-ready revised Results paragraph

> To distinguish schedule-selection sensitivity in energy inventories from delivered storage services, we solved a second cost-constrained LP in each of eight prespecified source-demand and synthetic-resource configurations, minimizing or maximizing annual battery discharge-to-load subject to a common near-optimal original variable-cost ceiling. Although annual mean SOC occupancies previously exhibited broad intervals within this feasible set, annual delivered discharge was tightly bounded. For example, for Arizona p28 under synthetic wave A and the original 25%-peak power rating, the optimized discharge interval spanned only 3.27 MWh around a baseline of 5.217 TWh, approximately 0.000063%. Consequently, the observed broad SOC-occupancy envelopes do not imply equally broad uncertainty in all aggregated dispatch measures. This result remains conditional on the LP's demand and renewable-resource assumptions, cost coefficients, zero terminal SOC, and explicitly defined near-optimal allowance.

## Technical verification

- Original baseline regression via [solver](../src/energy_transition/efs_cyclic_storage_lp.py) with optional `discharge_extremum` and unchanged old default API;
- [source-backed throughput extrema](../src/energy_transition/paper_s_discharge_optimal_envelope.py) and [unit tests](../tests/test_paper_s_discharge_optimal_envelope.py);
- [fully successful Actions workflow](../.github/workflows/paper-s-discharge-envelope.yml) with two original-source regional branches plus combined 8-interval certificate;
- [Figure S17 plotting module](../src/energy_transition/paper_s_discharge_envelope_figures.py) and [figure workflow](../.github/workflows/paper-s-discharge-envelope-figures.yml) must complete successfully before treating a generated chart as accepted.

## Mandatory limitations

The primary project has **seven distinct peak-normalized demand chronologies** among 19 nonzero zonal series per year; Arizona and Wyoming represent only two of those profiles and not statistically independent regional samples. Renewable profiles are synthetic ordinal waveforms, not observed wind/solar; EFS original `LocalHourID` is not independently certified physical UTC; there is no West-wide OPF, transmission exchange, battery capex, degradation, or investment economics. The 1e-9 cost allowance is predeclared but **not mathematically identical** to the exact primary-optimal face.

The next test should optimize charge throughput and selected-window storage service separately, because a nearly fixed **annual** discharge total could still coexist with material **temporal redistribution** among hours. Similarly, bound-hour counts require a separate mixed-integer or other carefully qualified optimization, not a simple SOC sum proxy.
