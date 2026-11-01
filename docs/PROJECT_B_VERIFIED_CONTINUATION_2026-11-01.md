# Project B — verified continuation checkpoint (2026-11-01)

This checkpoint reconciles new verified engineering artifacts with older milestone descriptions. It does **not** assert that a calibrated Western power-system optimization has been completed.

## CI evidence at audited head

- Audited main head: `181e5291f5b2c28b9f3608caf00f6f70c7e29df5`.
- Main CI run [41357877875](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41357877875): success.
- Actual EIA-923 BA-fuel workflow [41357877888](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41357877888): success; its `generation` job completed successfully and published an unexpired `eia923-ba-fuel-generation-2024` artifact at inspection.
- Engineering monitor [41360420342](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41360420342): success. A monitor pass is not evidence of calibration.
- The latest workflow commits separate monthly-reconciled EIA-923 records from *official annual-only* evidence; incomplete monthly records must never be silently imputed from annual values.

## Corrected network milestone definition

Prior documentation that describes *all* actual Western PyPSA network files as not yet built is out of date in this narrow sense: [successful network load-bearing run 41281576025](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41281576025) verifies three **load-bearing** PyPSA-USA-based NetCDF files for 2030, 2040 and 2050, with 20 zonal Load components and 8,760 ordinal local-hour snapshots. Reimported annual energy is 274.707, 306.839 and 350.871 TWh, respectively, for seven numerically admitted states (AZ, CO, ID, MT, NM, UT, WY), *not* all of WECC. Source: [verified load-bearing networks](VERIFIED_EFS_LOAD_BEARING_NETWORKS_2030_2040_2050.md).

These roundtrip-verified **load-only** outputs do **not** demonstrate:
- a complete, authenticated 2024 historical Western transmission network;
- fully admitted CA/NV/OR/WA, SD/TX, cross-border or split-state quantities;
- UTC, daylight-saving and local-hour temporal reconciliation;
- empirically justified generation capacities, fuel costs, renewable availability, storage or emissions factors;
- a successful multi-year, physically interpretable dispatch or investment optimization.

## Research acceptance gates for next development

| Gate | Existing evidence | Required before claim |
|---|---|---|
| G1 2024 EIA-923 data integrity | Successful 2024 generation workflow, monthly/annual evidence tiers | Download and summarize latest artifact per BA/fuel: eligible monthly data, annual-only data, withheld/excluded records, source population |
| G2 Temporal/spatial alignment | Three 2030/2040/2050 load-only networks with roundtrip conservation | Admit missing Western zones; document LAF and hourly mapping, UTC/DST handling and split-state weighting |
| G3 Network/plant inputs | Pinned PyPSA-USA-derived zonal topology pathway | Validate generators, renewable profiles, marginal costs, links, N-1/thermal assumption and source vintage; never equate ReEDS links with measured 2024 AC branches |
| G4 Baseline optimization | Historical CISO/BPAT gas-only pilots and synthetic Line sweep | Solve a source-qualified, interconnected reference year with solver status, annual/hourly energy balance, curtailment, load shedding, interchange and comparison metrics |
| G5 Transition analysis | Source-derived EFS demand projections | Solve comparable 2030/2040/2050 scenarios with explicit generation and investment decisions, emissions/cost accounting and sensitivity sweeps |
| G6 Manuscript | Descriptive demand and QA evidence | Only add quantified optimization Results after G1–G5 pass; keep illustrative plots labeled synthetic |

## Outstanding empirical mismatches

- 2024 gas-only CISO/BPAT dispatch versus full observed BA net generation MAE: **4,190.52 / 2,463.95 MW**; descriptive mismatch, **not historical calibration**.
- BPAT 2024 wind: qualified EIA-923 **8,820,435.41 MWh** versus EIA-930 BPAT WND **6,839,734 MWh**, signed difference **1,980,701.41 MWh**; reporting boundary unresolved, not inferred loss or curtailment.
- 2024 CISO EIA-930 total-interchange missing 312 hours, including 24 hours also missing NG; BPAT TI missing one hour; not legitimate to fill silently.

## Project isolation and research posture

Project A (`ys30/lut-to-pypsa`) supplies methodological and manifest-contract lessons only. Its continent-level load-only network is **not** admissible as B's Western state-hour electricity source. Project C is a separate resilience analysis, and neither C's screens nor B's synthetic scenarios can substitute for B's validated multi-year optimizer.

**Next executable step:** inspect the latest `eia923-ba-fuel-generation-2024` artifact for per-BA/per-fuel source qualification and update the source-to-generator admission contract. Then complete hourly/geographic load alignment and connect validated generation/transmission inputs before a Western baseline solve. Do not promote engineering CI success to manuscript-ready historical validation.
