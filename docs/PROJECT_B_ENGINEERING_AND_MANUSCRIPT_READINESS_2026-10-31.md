# Project B research milestone and manuscript readiness — 2026-10-31

## Verified engineering evidence

- [NLR EFS reference/moderate annual demand](NLR_EFS_CORE_WEST_QUANTITATIVE_RESULTS.md): core-11 states 774.400, 855.707, 980.023 TWh for 2030, 2040, 2050. These are **demand projections** from official source records, not solved network demand or observed consumption.
- [Genuine PyPSA-USA network dependency DAG](REAL_WESTERN_NETWORK_ARTIFACT_CHECKPOINT.md): pinned v0.8.0, 29 jobs, output path identified, **full network not yet built**.
- Real pinned ReEDS membership: 42 Western-labeled balancing-area zones including AB, BC and MEX; U.S. states MT, NM, SD and TX straddle electrical interconnection assignments. The core 11-state EFS scope is not the entire interconnection.
- Verified [SD/TX extraction run](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41265678862): full-state demand only, **not Western shares**.

| Year | SD full-state (TWh) | TX full-state (TWh) |
| --- | ---: | ---: |
| 2030 | 12.630215 | 447.369397 |
| 2040 | 13.541068 | 492.537338 |
| 2050 | 14.745876 | 543.526733 |

## Explicit manuscript status

**Suggested working title:** *Reproducible Western U.S. Electricity Demand Scenarios and the Data-Alignment Challenges of Multi-Year Capacity Expansion Modeling*.

**Current research readiness estimate ~25%**, separate from engineering infrastructure (~90%) and full empirical simulation (~40%). These are subjective stage estimates, not measured progress indicators.

| Manuscript component | Evidence and readiness |
| --- | --- |
| Research motivation | Broad question identified; more precise, falsifiable hypotheses needed |
| Sources and methodology | EFS and official membership provenance reproducible; UTC/DST and LAF methods incomplete |
| Descriptive results | Verified 2030/2040/2050 state-level annual demand and source QA |
| Network optimization | No solved full Western model with admitted real topology and constraints |
| Uncertainty and sensitivity | Synthetic screens available, not sufficient for empirical paper claims |
| Discussion | Can identify boundary conditions; quantitative policy claims premature |
| Figures | EFS scenario trend suitable as descriptive figure; no validated dispatch/emissions/cost plots |
| Reproducibility | CI and source-derived artifacts strong; full solve reproducibility pending |

## Critical path, in order

1. Obtain actual built PyPSA-USA Western NetCDF; record version, config, input source hashes, snapshot index, and solver provenance.
2. Validate effective model zone and geographic domain; reconcile U.S. versus Canadian/Mexican zones, split-state shares and border import assumptions.
3. Obtain and verify actual LAF_state zonal shares; do **not** spread full SD/TX/MT/NM source demand to Western without empirical allocation weights.
4. Resolve LocalHourID-to-network snapshot and leap/DST/time-zone alignment; verify annual MWh conservation before and after hourly spatial allocation.
5. Run baseline 2030/2040/2050 scenarios and technology/storage sensitivities with full optimality diagnostics; distinguish model scenarios from observed data.
6. Write quantitative Results, sensitivity tables, credible uncertainty discussion and technical supplement around validated solves.

A stand-alone **descriptive data engineering/benchmark paper** could be pursued earlier, but would require explicit methodological novelty and comparison to other openly reproducible pipelines. An *energy transition optimization* manuscript cannot be described as results-complete now.
