# Paper S — Source-verified near-optimal SOC schedule selection sensitivity

**Accepted evidence:** [32-case archival-source deterministic SOC tie-break run #42704492819](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42704492819) passed. Four predeclared MW–MWh/synthetic-supply configurations in each of two unique source-demand time-shape groups (Arizona p28, Wyoming p24) were solved under four objective modes: original baseline, a +1e−5 USD/(SOC MWh-hour) uniform SOC holding penalty, a negative holding reward of the same absolute size, and a deterministic sinusoidal ordinal-hour SOC coefficient. The perturbations were applied only to the LP selection objective; **every candidate solution was re-scored against the original, unperturbed USD 5/MWh renewable-use + USD 90/MWh firm-supply objective**.

**Important distinction:** This is a near-optimal solution-sensitivity screen, **not an exact multiple-optimal-bases mathematical certificate**. The eight source configurations and 32 dispatch solutions all passed feasibility, cyclic SOC and a within-one-part-per-million original-cost gate; the observed differences in the original LP objective are much smaller than that gate, below one millionth of one dollar in absolute USD. Deterministic weights do not constitute a probability sample of all feasible optimal schedules, and neither binding-hour counts nor solver-selected primal trajectories are independent physical observations.

## Measured maximum impacts on primal dispatch

| Original source group (2030) | Maximum absolute unperturbed objective gap over all tested configurations | Maximum changed hourly SOC relative to the unperturbed solution | Largest observed increase in hours at SOC energy bound |
|---|---:|---:|---:|
| Arizona p28 | USD 0.000000477 | 15,468.317 MWh | +5,166 hours |
| Wyoming p24 | USD 0.000000119 | 1,429.543 MWh | +5,715 hours |

The maxima across columns are **not necessarily at the same factor cell**. The original 32-row CSV and separate figure are the authoritative exact numbers; values above are rounded for interpretation.

For example, at Arizona p28 with **Flat 50%, P=0.25×peak MW, E=1×peak-MW-hour**, a negative tiny SOC holding coefficient yields **5,166 more hours at the energy-capacity bound**, while unperturbed annual cost changes only by floating-point-roundoff magnitude. At Wyoming p24 under **Wave B, P=0.25, E=1**, the SOC reward yields **5,715 more binding hours** than the original solver-selected schedule, while original objective cost is numerically unchanged. Thus an assertion such as “this scenario rarely binds the energy-capacity constraint” is **not robust to selection of near-identical-cost dispatch paths**.

### Consequences for paper interpretation

- **Reliable model-level effects:** independently solved annual optimal objective, source conservation, feasible set/installed MW–MWh bounds, source-derived 2×2 objective interaction and the local optimal objective’s HiGHS dual envelope derivative *when verified against a perturbation*.
- **Solution-specific descriptive quantities:** a single solver-selected SOC trajectory, its mean SOC, counting SOC-at-capacity hours, count of charge/discharge limit hours, and number of nonzero charge/discharge hours. These **are not uniquely identified by the primary linear objective** in general.
- **A zero dual and a binding primal upper bound can coexist** in degenerate solutions; do not imply a positive capacity value merely because the SOC bound is touched, or the reverse.
- **High-quality reviewer response:** present only uniquely interpretable results as primary evidence and explicitly label all trace metrics as one choice among near-cost-equivalent schedules. Optional stronger mathematical confirmation would fix a precise original-optimal-objective level (allowing a carefully justified numerical tolerance) and solve secondary extremum programs to construct minimum/maximum SOC binding exposure. Counting exact binding hours is discontinuous and requires additional formulations if it becomes a primary inferential target.
- A $1e−5 per hour-MWh SOC tie-break is synthetic and is **not intended to represent actual battery depreciation or holding cost**; its only purpose is to test primal-schedule identification.

## Reproducible provenance

- [Original primal and dual HiGHS solver](../src/energy_transition/efs_cyclic_storage_lp.py): optional deterministic `soc_tiebreak_usd_per_mwh` vector, with strict shape, finite-value and maximum magnitude checks. The default absent-perturbation solver retains its original objective.
- [Source-recognized 32-case sensitivity method](../src/energy_transition/paper_s_soc_tiebreak.py), [unit tests](../tests/test_paper_s_soc_tiebreak.py), [successful workflow #42704492819](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42704492819).
- [Figure S15 source-derived renderer](../src/energy_transition/paper_s_soc_tiebreak_figures.py), [Figure S15 tests](../tests/test_paper_s_soc_tiebreak_figures.py), [plot workflow](../.github/workflows/paper-s-soc-tiebreak-figures.yml). Verify that the plot workflow itself passes before calling its output finalized.

**Source limitations:** EFS original LocalHourID is an ordinal-hour sequence and is not independently timestamp-certified UTC; profiles of renewable availability are hypothetical; the underlying model excludes installed storage capital and network power flow; source-demand time shapes may repeat by scalar factor across physical zone records. Full private article manuscript must not be placed in the public repo.

## Manuscript-ready Results phrasing

> To evaluate identification of hourly storage schedules under the linear dispatch objective, we introduced three deterministic SOC-coefficient perturbations of magnitude at most USD 10−5 per MWh-hour into eight predeclared source-backed LP configurations across two different demand chronologies. Re-optimizing and re-evaluating all 32 solutions with the unperturbed objective showed cost differences below USD 10−6, while the selected SOC trajectory and bound-active-hour counts changed substantially. For example, the bound-active-hour count increased by more than 5,000 in selected Arizona and Wyoming cases without a meaningful change in primary objective value. Hence an isolated LP primal trajectory cannot uniquely establish the frequency of physically binding storage-energy constraints. We rely on certified objective differences and independently checked dual sensitivity estimates for operational-cost interpretation, and treat binding-hour statistics as solver-dependent exploratory diagnostics.
