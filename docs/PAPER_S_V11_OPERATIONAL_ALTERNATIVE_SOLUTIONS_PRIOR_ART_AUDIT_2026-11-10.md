# Paper S v11 — operational alternative-solution prior-art challenge (10 November 2026)

**Status:** targeted (not systematic) literature review, private manuscript v11 revision, no new LP or user EFS data published. The private working manuscript expands the Introduction, Related Work, Discussion and reference list, with Appendix G's study-by-study novelty comparison. All 7 previously certified embedded figures remain unchanged. Word rendering was inspected over 28 pages.

## Newly located direct predecessor — critical novelty constraint

**Viens, M. P., Skolfield, J. K., Hart, W. E., & Ferris, M. C. (2026).** *An Optimal Solution is Not Enough: Alternative Solutions and Optimal Power Systems.* 2026 IEEE Texas Power and Energy Conference, DOI [10.1109/TPEC67884.2026.11513200](https://doi.org/10.1109/TPEC67884.2026.11513200); accessible full preprint at [arXiv:2511.08805](https://arxiv.org/abs/2511.08805).

That paper already characterizes exact/near-optimal alternative solutions via feasible sublevel sets/projection and demonstrates them in **optimal power flow**. Therefore Paper S **cannot claim to be the first work applying near-optimal alternative-solution theory to electrical operations**, nor may it present cost-capped secondary objectives or temporal solution nonuniqueness as novel optimization methods.

**Bistline et al. (2020).** *Energy storage in long-term system models: a review of considerations, best practices, and research needs.* Progress in Energy 2, 032001, DOI [10.1088/2516-1083/ab9894](https://doi.org/10.1088/2516-1083/ab9894). This establishes the need for separate storage power/energy representation, chrono-SOC, temporal representation and perfect-foresight caution. It directly prevents a novelty claim based solely on independently sizing MW vs MWh.

Additional related work:
- [Neumann and Brown (2021)](https://doi.org/10.1016/j.epsr.2020.106690) and [Pedersen et al. (2021)](https://doi.org/10.1016/j.energy.2021.121294): near-optimal energy system alternatives already established.
- [Intersecting near-optimal spaces across weather variability (2022)](https://doi.org/10.1016/j.eneco.2022.106496): weather/year robustness and near-optimal solution-space intersections are also pre-existing.
- [EPRI model-selection guidance](https://msites.epri.com/resource-adequacy/methodologies-and-data/model-selection-guidelines) notes annual perfect-foresight over-optimization and storage horizon boundary effects.

## What can still be tested as a narrower scientific contribution?

The private v11 text proposes an **auditable diagnostic case study**: under one original-source matched cost cap, compare the *annual delivered battery MWh* feasible interval to the *same delivered-MWh metric in a prespecified 168-source-hour window*, then certify source-demand redundancy, avoid fictitious independent samples, and evaluate physically exclusive charging feasible witnesses plus illustrative throughput cost perturbations.

It is possible this quantitative *metric pairing* and source-provenance workflow is useful. **No verified claim of first publication or unique novelty** results from this selective search. The paper uses direct **SciPy/HiGHS**, ordinal projected EFS demand and hypothetical supply. It neither solves the richer Viens et al. OPF nor establishes actual Western dispatch/service availability.

## Matched-literature comparison

| Antecedent | Known overlap | Narrow possible difference | Prohibited overclaim |
|---|---|---|---|
| DeCarolis (2011/2016) | MGA and cost-bounded secondary alternatives | Predeclared battery-window metric | Invented MGA |
| Neumann & Brown (2021); Pedersen et al. (2021) | Near-optimal energy feasible spaces | Temporal deliverability contrasted with annual totals | First near-optimal energy analysis |
| **Viens et al. (2026)** | Alternative exact/near-optimal solutions **in OPF** | Explicit battery annual/window MWh comparison on a transparent toy LP | **First alternative-solution operating-model study** |
| Bistline et al. (2020) | MW/MWh distinctions, SOC and chronology | Audited source-specific orthogonal factorial | Invented independent storage sizing |
| EPRI | Annual foresight optimism and terminal conditions | Source-ordinal tolerance-bounded envelope | Real operational reliability |
| Schade and Egging-Bratseth (2024) | Battery degradation depends on real cycling physics | Simple linear 0/1/10 USD per discharged MWh sensitivity | Validated degradation physics |

## Remaining mandatory gates

1. Search explicitly for **temporal optimal-dispatch metric projection**, cost-constrained storage-operation degeneracy, annual-versus-window energy intervals and marginal service availability. Record search queries, databases and exclusion criteria before claiming literature coverage.
2. Vary predeclared source-window choice and timing to rule out window-selection artifacts; keep clear that local source hour IDs have no certified UTC.
3. Confirm source EFS LocalHourID chronology, unlicensed mixed data reuse, manuscript/coauthor authorization and source-figure publication quality before submission.
4. Keep original cost allowance and solver feasibility limits visible. Separate the previously constructed exclusivity **feasible witness** from a global mixed-integer optimum.
5. Check target-journal formatting after selecting outlet; current manuscript v11 is **private working draft**, not journal acceptance or final submission.

**Public source code and archived LP results were not changed by this editorial research update.**
