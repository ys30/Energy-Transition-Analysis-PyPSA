# Verified 53 source-positive-Pd low-voltage zero-degree bus EFS exposure screen

**Actual-data primary source screen passed:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41866601224

**State/year concentration follow-up passed:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41869023373

## Source interpretation and scope

The original archived 10,157-bus Western source topology contains 877 zero-degree bus records in its Line+Transformer graph. Exactly 55 of these have positive archived `Pd` totaling **1,714.97 MW**, all at nominal voltage <=25 kV. Of the 55, **53** are assigned exported state labels within the eleven EFS source states and **2** belong to **Texas**, which is outside the official study source coverage; Texas excluded source `Pd` is **106.42 MW**. In-scope original source `Pd` totals **1,608.55 MW**.

The candidate computation takes each 2030/2040/2050 official NLR EFS **state's** 8,760 local ordinal-hour `load_mw` records, sums over the year, and multiplies each bus's original `LAF_state` by the annual demand in its **exported** state. This is a deliberately hypothetical numerical screening result, not verified physical time-aligned bus demand, served energy, lost load, or a solved OPF. Original `full_state` normalization and exact ReEDS receiving zones were not fully recovered. Texas remains explicitly excluded rather than treated as zero demand.

| Planning year | In-scope 53-bus candidate exposure | Largest contribution state | CA component | CA share of screened candidate exposure | Top-three state share |
| --- | ---: | --- | ---: | ---: | ---: |
| 2030 | **8.965409 TWh** | CA | 2.179841 TWh | 24.31% | 53.44% |
| 2040 | **9.945565 TWh** | CA | 2.362358 TWh | 23.75% | 53.11% |
| 2050 | **11.388189 TWh** | CA | 2.710816 TWh | 23.80% | 53.16% |

In 2030 the next highest contributing exported states are **AZ** (7 buses, 1.428701 TWh) and **WA** (8 buses, 1.182609 TWh). CA has 13 source buses in this hypothetical screen. Top-three composition and underlying bus identities are available in the archived state-year CSV.

## Scientific interpretation

These quantities mean **potential sensitivity of a simplistic source-state×LAF mapping to the 53 selected low-voltage, graph-zero-degree buses**; they are **NOT** evidence that any network node actually receives EFS demand in the final zone-based PyPSA build, nor evidence of unserved energy, utility grid islands, physical power flows or a future-generation shortfall.

The original source `Pd` value is a demand disaggregation attribute used upstream; on-screen `Pd` totals are an independent historical/source-network description and must not be added to the candidate annual EFS exposure as though they were comparable energy quantities. The state-level LAF screening does not reprove the missing original `full_state` denominator.

## Implementation

- `src/energy_transition/western_zero_degree_joint_source_audit.py` and [CI 41862652028](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41862652028) locate the 55 original bus identities and show their source-voltage categories.
- `src/energy_transition/efs_55_positive_pd_candidate_exposure.py` and [CI 41866601224](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41866601224) screen real official 11-state EFS original year-hour source demand and explicitly partition 53 in-scope vs 2 out-of-scope Texas buses.
- `src/energy_transition/efs_55_positive_pd_state_concentration.py` and [CI 41869023373](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41869023373) aggregate the source-consistent three-year bus records by original exported state and test consistent bus source identities, constant LAF, positivity and exact source-to-bus arithmetic.

CI outputs: `efs-55-isolated-source-pd-buses-candidate-demand-screen` with 159 bus-year screen rows; and `efs-53-positive-pd-source-bus-state-concentration` with the state-year concentration table. Neither artifact is an empirical generator dispatch dataset.

## Research priority

**Next genuinely decisive validation:** trace the underlying bus construction `baseKV`, `sub_id`, original generator-terminal/transformer records and EFS demand-attachment workflow for the 53 in-scope low-voltage nodes. In particular, verify whether source-level demand distribution ever targets these nodes in the *actual accepted* zone-to-bus demand attachment. If it does, quantify the difference between retaining/reconnecting nodes and an admissible network topology; if it does not, the hypothetical EFS screening remains only an uncertainty bound. **Do not interpret 8.97–11.39 TWh as actual stranded load.**
