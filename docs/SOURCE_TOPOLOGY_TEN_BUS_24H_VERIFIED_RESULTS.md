# Verified 10-bus 24-hour synthetic network sensitivity results

**Evidence:** [Successful GitHub Actions HiGHS/PyPSA solver run #41694426795](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41694426795), based on commit `2a47c5dd`. The workflow loaded the pinned Breakthrough Energy synthetic Western source network and selected a source-model 10-bus/9-Line radial subgraph. The reported results are **numerically solved** and passed all six 24-hour scenarios' source-topology nodal and system balance, Line rating, renewable availability, and objective reconstruction checks.

**All** generator fleets, loads, solar profiles, ratings and costs are explicitly hypothetical; the source model itself is a **synthetic** network. Thus none of the results are an observed Western electrical, energy-policy, or Palo Verde finding.

## Actual solved values

| Uniform hypothetical Line rating (MW) | Hypothetical solar nameplate (MW) | Synthetic 24-hour cost (arbitrary units) | Backup energy (MWh) | Solar energy (MWh) | Binding Line-hours (count) |
|---:|---:|---:|---:|---:|---:|
| 45 | 75 | 390,790.745 | 2,958.346 | 569.682 | 70 |
| 75 | 75 | 325,520.318 | 2,142.466 | 569.682 | 31 |
| 120 | 75 | 241,765.364 | 1,095.529 | 569.682 | 21 |
| 45 | 200 | 315,700.131 | 2,257.081 | 1,519.151 | 64 |
| 75 | 200 | 266,191.871 | 1,638.228 | 1,519.151 | 23 |
| 120 | 200 | 209,185.516 | 925.648 | 1,519.151 | 15 |

- The assumed daily load is the same for all scenarios (8,275.834 MWh).
- Computed solar curtailment is effectively zero (numerical roundoff below 1e-12 MWh).
- Maximum absolute nodal balance residual across scenarios is about 5.68e-14 MW, demonstrating numerical conservation for the solved **synthetic** test.
- More permitted branch capacity reduced model cost and expensive local backup, while a higher solar nameplate reduced modeled cost at each branch capacity. These comparisons are **mechanical scenario outcomes**, not estimates of real expansion benefits.

## Outputs and interpretation constraints

The workflow artifact includes the 24-hour solver JSON for all six scenarios. A following reporting workflow revision may add CSV tables and labeled graphics; do not call those artifacts verified before that later run succeeds.

When writing a paper or recruiter-facing portfolio, label this clearly **synthetic topology OPF sensitivity / method validation** and avoid phrases such as `validated Western grid operations`, `Palo Verde observed congestion`, or `real-world cost savings`.

See [underlying synthetic network provenance](WESTERN_SYNTHETIC_NETWORK_PROVENANCE.md) and [experiment methods](SOURCE_TOPOLOGY_TEN_BUS_24H_SENSITIVITY.md).
